#!/usr/bin/env python3
"""Validate structural and editorial invariants in an uncompressed .drawio file."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


MAX_BYTES = 20 * 1024 * 1024
BANNED_STYLE = ("shadow=1", "glass=1", "gradientColor=#", "curved=1")


def parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("diagram", type=Path, help="Uncompressed .drawio file")
    return arg_parser


def parse_file(path: Path) -> tuple[ET.Element, list[str]]:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read file: {exc}") from exc
    if len(raw) > MAX_BYTES:
        raise ValueError(f"file exceeds {MAX_BYTES} byte validation limit")
    upper = raw[:4096].upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("DOCTYPE and ENTITY declarations are not allowed")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"invalid XML: {exc}") from exc
    if root.tag != "mxfile":
        errors.append("root element must be mxfile")
    if root.get("compressed") != "false":
        errors.append("file must use uncompressed Draw.io XML")
    return root, errors


def geometry(cell: ET.Element) -> dict[str, float] | None:
    item = cell.find("mxGeometry")
    if item is None:
        return None
    try:
        return {key: float(item.get(key, "0")) for key in ("x", "y", "width", "height")}
    except ValueError:
        return None


def style_value(style: str, key: str) -> str | None:
    match = re.search(rf"(?:^|;){re.escape(key)}=([^;]+)", style)
    return match.group(1) if match else None


def validate_metadata(root: ET.Element, errors: list[str]) -> None:
    for attr in ("data-title", "data-description", "data-type", "data-audience", "data-detail"):
        if not root.get(attr, "").strip():
            errors.append(f"missing mxfile {attr} metadata")
    diagrams = root.findall("diagram")
    if len(diagrams) != 1:
        errors.append(f"expected exactly one diagram page, found {len(diagrams)}")


def validate_cells(root: ET.Element, errors: list[str], warnings: list[str]) -> list[ET.Element]:
    cells = root.findall(".//mxCell")
    ids = [cell.get("id") for cell in cells]
    duplicates = [cell_id for cell_id, count in Counter(ids).items() if cell_id and count > 1]
    if duplicates:
        errors.append(f"duplicate cell ids: {', '.join(duplicates)}")
    for cell in cells:
        style = cell.get("style", "")
        for banned in BANNED_STYLE:
            if banned in style:
                errors.append(f"cell {cell.get('id')} uses banned style {banned}")
        if cell.get("vertex") == "1":
            box = geometry(cell)
            if box is None:
                errors.append(f"vertex {cell.get('id')} has invalid geometry")
                continue
            for key, value in box.items():
                if value % 4 != 0:
                    errors.append(f"vertex {cell.get('id')} {key}={value:g} is off the 4 px grid")
            if "shape=line" in style and box["width"] and box["height"]:
                errors.append(f"line primitive {cell.get('id')} is diagonal")
    if not any(cell.get("data-role") == "header" for cell in cells):
        warnings.append("no editable header cells found")
    return cells


def validate_budget(root: ET.Element, cells: list[ET.Element], errors: list[str]) -> None:
    nodes = [cell for cell in cells if cell.get("data-role") == "node"]
    edges = [cell for cell in cells if cell.get("data-role") == "connector"]
    focal = [cell for cell in cells if cell.get("data-role") in {"node", "primitive"} and cell.get("data-kind") == "focal"]
    detail = root.get("data-detail", "balanced")
    limit = 24 if detail == "faithful" else 9
    if len(nodes) > limit:
        errors.append(f"node count {len(nodes)} exceeds {detail} limit {limit}")
    if len(edges) > 12:
        errors.append(f"connector count {len(edges)} exceeds limit 12")
    if len(focal) > 2:
        errors.append(f"focal element count {len(focal)} exceeds limit 2")


def validate_connectors(cells: list[ET.Element], errors: list[str]) -> None:
    edges = [cell for cell in cells if cell.get("data-role") == "connector"]
    labels = [cell for cell in cells if cell.get("data-role") == "edge-label"]
    labels_by_edge = Counter(cell.get("data-edge-id") for cell in labels)
    attachments: set[tuple[str, str, str]] = set()
    ids = {cell.get("id") for cell in cells}
    for edge in edges:
        edge_id = edge.get("id", "")
        style = edge.get("style", "")
        if "edgeStyle=orthogonalEdgeStyle" not in style or "rounded=1" not in style:
            errors.append(f"connector {edge_id} is not rounded orthogonal")
        if edge.get("value", "").strip():
            errors.append(f"connector {edge_id} uses a built-in edge label")
        for endpoint, prefix in (("source", "exit"), ("target", "entry")):
            node_id = edge.get(endpoint)
            if node_id not in ids:
                errors.append(f"connector {edge_id} has unknown {endpoint} {node_id!r}")
            x = style_value(style, f"{prefix}X")
            y = style_value(style, f"{prefix}Y")
            if x is None or y is None:
                errors.append(f"connector {edge_id} lacks explicit {prefix} attachment")
                continue
            key = (str(node_id), x, y)
            if key in attachments:
                errors.append(f"connector {edge_id} reuses attachment point {key}")
            attachments.add(key)
        label = edge.get("data-label", "")
        if label and labels_by_edge[edge_id] != 1:
            errors.append(f"connector {edge_id} needs exactly one separate label cell")
    for label in labels:
        style = label.get("style", "")
        if "fillColor=#f5f5f5" not in style:
            errors.append(f"edge label {label.get('id')} lacks the paper mask fill")


def validate_page(root: ET.Element, cells: list[ET.Element], errors: list[str]) -> None:
    model = root.find("./diagram/mxGraphModel")
    if model is None:
        errors.append("missing mxGraphModel")
        return
    try:
        page_width = float(model.get("pageWidth", "0"))
        page_height = float(model.get("pageHeight", "0"))
    except ValueError:
        errors.append("invalid page dimensions")
        return
    if page_width % 4 or page_height % 4:
        errors.append("page dimensions must use the 4 px grid")
    for cell in cells:
        if cell.get("vertex") != "1":
            continue
        box = geometry(cell)
        if box and (box["x"] < 0 or box["y"] < 0 or box["x"] + box["width"] > page_width or box["y"] + box["height"] > page_height):
            errors.append(f"vertex {cell.get('id')} exceeds page bounds")


def main() -> int:
    args = parser().parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        root, parse_errors = parse_file(args.diagram)
        errors.extend(parse_errors)
    except ValueError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    validate_metadata(root, errors)
    cells = validate_cells(root, errors, warnings)
    validate_budget(root, cells, errors)
    validate_connectors(cells, errors)
    validate_page(root, cells, errors)
    if errors:
        print("INVALID DRAWIO", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    print(f"VALID {args.diagram}")
    print(f"CELLS {len(cells)} | NODES {sum(c.get('data-role') == 'node' for c in cells)} | CONNECTORS {sum(c.get('data-role') == 'connector' for c in cells)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print("VISUAL REVIEW REQUIRED: inspect routing, label gaps, crossings, clipping, and hierarchy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
