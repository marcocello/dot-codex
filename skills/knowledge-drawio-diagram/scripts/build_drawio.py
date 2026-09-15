#!/usr/bin/env python3
"""Build an uncompressed, native Draw.io diagram from a constrained JSON spec."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


TOKENS = {
    "paper": "#f5f5f5",
    "paper_2": "#ececec",
    "ink": "#2d3142",
    "muted": "#4f5d75",
    "soft": "#7a8399",
    "rule": "#d9dade",
    "rule_solid": "#bfc0c0",
    "accent": "#eb6c36",
    "accent_tint": "#fcefe9",
    "link": "#2e5aa8",
}

NODE_KINDS = {
    "focal",
    "backend",
    "store",
    "external",
    "input",
    "optional",
    "security",
    "decision",
    "state",
    "plain",
}
EDGE_KINDS = {"default", "accent", "link", "optional", "async", "return", "passive"}
SHAPES = {"rect", "ellipse", "rhombus", "cylinder", "cloud", "hexagon", "triangle", "parallelogram"}


class SpecError(ValueError):
    pass


def parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("spec", type=Path, help="Input JSON specification")
    arg_parser.add_argument("output", type=Path, help="Output .drawio file")
    return arg_parser


def load_spec(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecError(f"cannot read JSON spec: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecError("top-level JSON value must be an object")
    return data


def is_grid(value: Any) -> bool:
    return isinstance(value, int) and value % 4 == 0


def validate_geometry(item: dict[str, Any], label: str, page: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("x", "y", "w", "h"):
        if field not in item or not is_grid(item[field]):
            errors.append(f"{label}.{field} must be an integer divisible by 4")
    if errors:
        return errors
    if item["w"] < 0 or item["h"] < 0:
        errors.append(f"{label} width and height cannot be negative")
    if item["x"] < 0 or item["y"] < 0:
        errors.append(f"{label} cannot start outside the page")
    if item["x"] + item["w"] > page["width"] or item["y"] + item["h"] > page["height"]:
        errors.append(f"{label} exceeds page bounds")
    return errors


def validate_port(port: Any, label: str) -> list[str]:
    if not isinstance(port, dict) or "x" not in port or "y" not in port:
        return [f"{label} must contain normalized x and y"]
    x, y = port["x"], port["y"]
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return [f"{label} x and y must be numeric"]
    if not (0 <= x <= 1 and 0 <= y <= 1):
        return [f"{label} x and y must be between 0 and 1"]
    if x not in (0, 1) and y not in (0, 1):
        return [f"{label} must lie on a node edge"]
    return []


def validate_ids(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for collection in ("zones", "edges", "edge_labels", "nodes", "primitives"):
        for index, item in enumerate(spec.get(collection, [])):
            item_id = item.get("id") if isinstance(item, dict) else None
            if not item_id or not isinstance(item_id, str):
                errors.append(f"{collection}[{index}].id must be a non-empty string")
                continue
            if "::" in item_id:
                errors.append(f"{collection}[{index}].id cannot contain reserved token '::'")
            if item_id in seen:
                errors.append(f"duplicate id: {item_id}")
            seen.add(item_id)
    return errors


def validate_edges(spec: dict[str, Any], node_ids: set[str]) -> list[str]:
    errors: list[str] = []
    attachments: set[tuple[str, float, float]] = set()
    edge_ids: set[str] = set()
    labelled_edges: dict[str, str] = {}
    for index, edge in enumerate(spec.get("edges", [])):
        label = f"edges[{index}]"
        edge_id = edge.get("id")
        edge_ids.add(edge_id)
        if edge.get("kind", "default") not in EDGE_KINDS:
            errors.append(f"{label}.kind is unsupported")
        for endpoint in ("source", "target"):
            node_id = edge.get(endpoint)
            if node_id not in node_ids:
                errors.append(f"{label}.{endpoint} references unknown node {node_id!r}")
            port_name = "source_port" if endpoint == "source" else "target_port"
            port = edge.get(port_name)
            errors.extend(validate_port(port, f"{label}.{port_name}"))
            if isinstance(port, dict) and node_id in node_ids and "x" in port and "y" in port:
                key = (node_id, float(port["x"]), float(port["y"]))
                if key in attachments:
                    errors.append(f"{label} reuses attachment point {key}")
                attachments.add(key)
        for point_index, point in enumerate(edge.get("waypoints", [])):
            if not isinstance(point, dict) or not is_grid(point.get("x")) or not is_grid(point.get("y")):
                errors.append(f"{label}.waypoints[{point_index}] must use 4 px grid coordinates")
        edge_label = edge.get("label", "")
        if edge_label:
            if len(edge_label) > 14:
                errors.append(f"{label}.label must be 14 characters or fewer")
            labelled_edges[edge_id] = edge_label
    label_map: dict[str, str] = {}
    for index, edge_label in enumerate(spec.get("edge_labels", [])):
        edge_id = edge_label.get("edge")
        if edge_id not in edge_ids:
            errors.append(f"edge_labels[{index}].edge references unknown edge {edge_id!r}")
        if edge_id in label_map:
            errors.append(f"edge {edge_id!r} has more than one label cell")
        label_map[edge_id] = edge_label.get("text", "")
    for edge_id, edge_label in labelled_edges.items():
        if label_map.get(edge_id) != edge_label:
            errors.append(f"edge {edge_id!r} needs one matching separate edge_labels entry")
    return errors


def validate_spec(spec: dict[str, Any]) -> None:
    errors: list[str] = []
    for field in ("title", "description"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            errors.append(f"{field} must be a non-empty string")
    page = spec.get("page")
    if not isinstance(page, dict):
        errors.append("page must be an object")
        page = {"width": 0, "height": 0}
    for field in ("width", "height"):
        if not is_grid(page.get(field)) or page.get(field, 0) <= 0:
            errors.append(f"page.{field} must be a positive integer divisible by 4")
    errors.extend(validate_ids(spec))
    geometry_collections = ("zones", "edge_labels", "nodes", "primitives")
    if not errors or page.get("width", 0) > 0:
        for collection in geometry_collections:
            for index, item in enumerate(spec.get(collection, [])):
                if isinstance(item, dict):
                    errors.extend(validate_geometry(item, f"{collection}[{index}]", page))
    nodes = spec.get("nodes", [])
    primitives = spec.get("primitives", [])
    if not nodes and not primitives:
        errors.append("at least one node or primitive is required")
    detail = spec.get("detail", "balanced")
    node_limit = 24 if detail == "faithful" else 9
    if len(nodes) > node_limit:
        errors.append(f"node count {len(nodes)} exceeds {detail} limit {node_limit}")
    if len(spec.get("edges", [])) > 12:
        errors.append("edge count exceeds the standard limit of 12")
    focal_count = sum(1 for node in nodes if node.get("kind") == "focal")
    focal_count += sum(1 for item in primitives if item.get("kind") == "focal")
    if focal_count > 2:
        errors.append("more than two focal elements")
    for index, node in enumerate(nodes):
        if node.get("kind", "backend") not in NODE_KINDS:
            errors.append(f"nodes[{index}].kind is unsupported")
        shape = node.get("shape")
        if shape is not None and shape not in SHAPES:
            errors.append(f"nodes[{index}].shape is unsupported")
    node_ids = {item.get("id") for item in nodes if isinstance(item, dict)}
    errors.extend(validate_edges(spec, node_ids))
    if errors:
        raise SpecError("\n".join(f"- {error}" for error in errors))


def add_geometry(cell: ET.Element, x: int, y: int, w: int, h: int, relative: bool = False) -> ET.Element:
    attrs = {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    return ET.SubElement(cell, "mxGeometry", attrs)


def add_vertex(
    root: ET.Element,
    cell_id: str,
    value: str,
    style: str,
    geometry: dict[str, int],
    extra: dict[str, str] | None = None,
) -> ET.Element:
    attrs = {"id": cell_id, "value": value, "style": style, "vertex": "1", "parent": "1"}
    if extra:
        attrs.update(extra)
    cell = ET.SubElement(root, "mxCell", attrs)
    add_geometry(cell, geometry["x"], geometry["y"], geometry["w"], geometry["h"])
    return cell


def text_style(font: str, size: int, color: str, align: str = "left") -> str:
    return (
        "text;html=1;strokeColor=none;fillColor=none;align="
        f"{align};verticalAlign=middle;whiteSpace=wrap;rounded=0;shadow=0;"
        f"fontFamily={font};fontSize={size};fontColor={color};spacing=0;"
    )


def node_shape(node: dict[str, Any]) -> str:
    shape = node.get("shape")
    if shape:
        return shape
    if node.get("kind") == "store":
        return "cylinder"
    if node.get("kind") == "decision":
        return "rhombus"
    return "rect"


def shape_style(shape: str) -> str:
    mapping = {
        "rect": "rounded=1;arcSize=8;",
        "ellipse": "ellipse;",
        "rhombus": "rhombus;perimeter=rhombusPerimeter;",
        "cylinder": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=12;",
        "cloud": "shape=cloud;",
        "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;",
        "triangle": "shape=triangle;",
        "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;",
    }
    return mapping[shape]


def kind_style(kind: str) -> str:
    styles = {
        "focal": (TOKENS["accent_tint"], TOKENS["accent"], "1", "0"),
        "backend": ("#ffffff", TOKENS["ink"], "1", "0"),
        "store": ("#eaeaec", TOKENS["muted"], "1", "0"),
        "external": ("#efeff0", TOKENS["rule_solid"], "1", "0"),
        "input": ("#e5e7eb", TOKENS["soft"], "1", "0"),
        "optional": ("#f2f2f3", TOKENS["rule_solid"], "1", "1"),
        "security": ("#fcefe9", "#f2b399", "1", "1"),
        "decision": ("#ffffff", TOKENS["ink"], "1", "0"),
        "state": ("#ffffff", TOKENS["muted"], "1", "0"),
        "plain": (TOKENS["paper"], TOKENS["rule"], "1", "0"),
    }
    fill, stroke, stroke_width, dashed = styles[kind]
    return (
        f"fillColor={fill};strokeColor={stroke};strokeWidth={stroke_width};dashed={dashed};"
        "dashPattern=4 3;shadow=0;glass=0;gradientColor=none;"
    )


def node_value(node: dict[str, Any]) -> str:
    tag = html.escape(str(node.get("tag", "")).upper())
    label = html.escape(str(node.get("label", "")))
    sublabel = html.escape(str(node.get("sublabel", "")))
    parts: list[str] = ["<div style=\"text-align:center;line-height:1.25;\">"]
    if tag:
        parts.append(
            f"<span style=\"font-family:Geist Mono,Menlo,monospace;font-size:8px;letter-spacing:1px;color:{TOKENS['soft']};\">{tag}</span><br>"
        )
    parts.append(
        f"<span style=\"font-family:Geist,Arial,sans-serif;font-size:12px;font-weight:600;color:{TOKENS['ink']};\">{label}</span>"
    )
    if sublabel:
        parts.append(
            f"<br><span style=\"font-family:Geist Mono,Menlo,monospace;font-size:8px;color:{TOKENS['soft']};\">{sublabel}</span>"
        )
    parts.append("</div>")
    return "".join(parts)


def edge_style(edge: dict[str, Any]) -> str:
    kind = edge.get("kind", "default")
    color = TOKENS["muted"]
    dashed = "0"
    width = "1"
    if kind == "link":
        color = TOKENS["link"]
    elif kind == "accent":
        color, width = TOKENS["accent"], "1.2"
    elif kind in {"optional", "async", "return", "passive"}:
        dashed = "1"
    source_port, target_port = edge["source_port"], edge["target_port"]
    style = (
        "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;html=1;rounded=1;curved=0;"
        f"strokeColor={color};strokeWidth={width};dashed={dashed};dashPattern=4 3;"
        "endArrow=block;endFill=1;endSize=8;startArrow=none;shadow=0;"
        f"exitX={source_port['x']};exitY={source_port['y']};exitDx=0;exitDy=0;exitPerimeter=1;"
        f"entryX={target_port['x']};entryY={target_port['y']};entryDx=0;entryDy=0;entryPerimeter=1;"
    )
    if edge.get("jump"):
        style += "jumpStyle=arc;jumpSize=8;"
    return style + str(edge.get("style", ""))


def add_header(root: ET.Element, spec: dict[str, Any], page: dict[str, Any]) -> None:
    header = spec.get("header", {})
    eyebrow = str(header.get("eyebrow", spec.get("type", "DIAGRAM"))).upper()
    title = str(header.get("title", spec["title"]))
    subtitle = str(header.get("subtitle", ""))
    width = page["width"] - 96
    add_vertex(root, "header::eyebrow", html.escape(eyebrow), text_style("Geist Mono", 8, TOKENS["soft"]), {"x": 48, "y": 24, "w": width, "h": 16}, {"data-role": "header"})
    add_vertex(root, "header::title", html.escape(title), text_style("Instrument Serif", 28, TOKENS["ink"]), {"x": 48, "y": 44, "w": width, "h": 40}, {"data-role": "header"})
    if subtitle:
        add_vertex(root, "header::subtitle", html.escape(subtitle), text_style("Geist", 12, TOKENS["muted"]), {"x": 48, "y": 88, "w": width, "h": 24}, {"data-role": "header"})


def add_zone(root: ET.Element, zone: dict[str, Any]) -> None:
    zone_style = (
        "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=#f1f1f2;strokeColor=#d9dade;"
        "strokeWidth=1;dashed=1;dashPattern=4 4;shadow=0;glass=0;gradientColor=none;"
    )
    add_vertex(root, zone["id"], "", zone_style, zone, {"data-role": "zone"})
    label_geometry = {"x": zone["x"] + 12, "y": zone["y"] + 8, "w": min(160, zone["w"] - 24), "h": 16}
    label_style = text_style("Geist Mono", 8, TOKENS["soft"])
    label_style += f"fillColor={TOKENS['paper']};"
    add_vertex(root, f"{zone['id']}::label", html.escape(str(zone.get("label", "")).upper()), label_style, label_geometry, {"data-role": "zone-label"})


def add_edge(root: ET.Element, edge: dict[str, Any]) -> None:
    attrs = {
        "id": edge["id"],
        "value": "",
        "style": edge_style(edge),
        "edge": "1",
        "parent": "1",
        "source": edge["source"],
        "target": edge["target"],
        "data-role": "connector",
        "data-kind": edge.get("kind", "default"),
        "data-label": str(edge.get("label", "")),
    }
    cell = ET.SubElement(root, "mxCell", attrs)
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    points = edge.get("waypoints", [])
    if points:
        array = ET.SubElement(geometry, "Array", {"as": "points"})
        for point in points:
            ET.SubElement(array, "mxPoint", {"x": str(point["x"]), "y": str(point["y"])})


def add_edge_label(root: ET.Element, item: dict[str, Any], paper: str) -> None:
    style = (
        "shape=label;rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
        f"fillColor={paper};strokeColor=none;fontFamily=Geist Mono;fontSize=8;fontColor={TOKENS['soft']};"
        "spacing=0;shadow=0;glass=0;gradientColor=none;"
    )
    add_vertex(
        root,
        item["id"],
        html.escape(str(item["text"]).upper()),
        style,
        item,
        {"data-role": "edge-label", "data-edge-id": item["edge"]},
    )


def add_node(root: ET.Element, node: dict[str, Any]) -> None:
    kind = node.get("kind", "backend")
    shape = node_shape(node)
    style = shape_style(shape) + kind_style(kind)
    style += "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacing=8;overflow=hidden;fontFamily=Geist,Arial,sans-serif;"
    style += str(node.get("style", ""))
    add_vertex(root, node["id"], node_value(node), style, node, {"data-role": "node", "data-kind": kind})


def add_primitive(root: ET.Element, item: dict[str, Any]) -> None:
    style = str(item["style"])
    if not style.endswith(";"):
        style += ";"
    if "shadow=" not in style:
        style += "shadow=0;"
    add_vertex(
        root,
        item["id"],
        str(item.get("value", "")),
        style,
        item,
        {"data-role": "primitive", "data-kind": str(item.get("kind", "plain")), "data-layer": str(item.get("layer", "content"))},
    )


def legend_marker_style(kind: str) -> str:
    if kind == "focal":
        return f"rounded=1;arcSize=8;fillColor={TOKENS['accent_tint']};strokeColor={TOKENS['accent']};shadow=0;"
    if kind == "link":
        return f"rounded=0;fillColor={TOKENS['link']};strokeColor={TOKENS['link']};strokeWidth=1;shadow=0;"
    if kind in {"optional", "async", "return", "passive"}:
        return f"rounded=0;fillColor=none;strokeColor={TOKENS['muted']};dashed=1;dashPattern=4 3;shadow=0;"
    return f"rounded=1;arcSize=8;fillColor=#ffffff;strokeColor={TOKENS['ink']};shadow=0;"


def add_legend(root: ET.Element, items: list[dict[str, Any]], page: dict[str, Any]) -> None:
    if not items:
        return
    y = page["height"] - 64
    line = {"x": 32, "y": y - 8, "w": page["width"] - 64, "h": 0}
    add_vertex(root, "legend::rule", "", f"shape=line;strokeColor={TOKENS['rule']};strokeWidth=1;shadow=0;", line, {"data-role": "legend"})
    add_vertex(root, "legend::title", "LEGEND", text_style("Geist Mono", 8, TOKENS["muted"]), {"x": 32, "y": y + 4, "w": 72, "h": 16}, {"data-role": "legend"})
    x = 120
    for index, item in enumerate(items):
        kind = item.get("kind", "default")
        marker_height = 4 if kind == "link" else (8 if kind in {"optional", "async", "return", "passive"} else 12)
        marker_y = y + 12 if marker_height == 4 else y + 8
        marker = {"x": x, "y": marker_y, "w": 24, "h": marker_height}
        add_vertex(root, f"legend::{index}::marker", "", legend_marker_style(kind), marker, {"data-role": "legend"})
        add_vertex(root, f"legend::{index}::label", html.escape(str(item["label"])), text_style("Geist", 8, TOKENS["muted"]), {"x": x + 32, "y": y + 4, "w": 144, "h": 20}, {"data-role": "legend"})
        x += 192


def graph_tree(spec: dict[str, Any]) -> ET.ElementTree:
    page = spec["page"]
    digest = hashlib.sha1(f"{spec['title']}|{page.get('name', 'Page-1')}".encode()).hexdigest()[:12]
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "agent": "drawio-diagram-design",
            "compressed": "false",
            "data-title": spec["title"],
            "data-description": spec["description"],
            "data-type": str(spec.get("type", "diagram")),
            "data-audience": str(spec.get("audience", "mixed")),
            "data-detail": str(spec.get("detail", "balanced")),
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": digest, "name": str(page.get("name", "Page-1"))})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1422",
            "dy": "762",
            "grid": "1",
            "gridSize": "4",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(page["width"]),
            "pageHeight": str(page["height"]),
            "math": "0",
            "shadow": "0",
            "background": str(page.get("background", TOKENS["paper"])),
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    add_header(root, spec, page)
    for zone in spec.get("zones", []):
        add_zone(root, zone)
    for primitive in spec.get("primitives", []):
        if primitive.get("layer", "content") == "background":
            add_primitive(root, primitive)
    for edge in spec.get("edges", []):
        add_edge(root, edge)
    paper = str(page.get("background", TOKENS["paper"]))
    for edge_label in spec.get("edge_labels", []):
        add_edge_label(root, edge_label, paper)
    for node in spec.get("nodes", []):
        add_node(root, node)
    for primitive in spec.get("primitives", []):
        if primitive.get("layer", "content") == "content":
            add_primitive(root, primitive)
    add_legend(root, spec.get("legend", []), page)
    for primitive in spec.get("primitives", []):
        if primitive.get("layer", "content") == "foreground":
            add_primitive(root, primitive)
    ET.indent(mxfile, space="  ")
    return ET.ElementTree(mxfile)


def main() -> int:
    args = parser().parse_args()
    try:
        spec = load_spec(args.spec)
        validate_spec(spec)
        tree = graph_tree(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.output, encoding="utf-8", xml_declaration=True)
    except SpecError as exc:
        print(f"INVALID SPEC\n{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"WRITE ERROR: {exc}", file=sys.stderr)
        return 3
    print(f"WROTE {args.output}")
    print(f"TYPE {spec.get('type', 'diagram')} | NODES {len(spec.get('nodes', []))} | EDGES {len(spec.get('edges', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
