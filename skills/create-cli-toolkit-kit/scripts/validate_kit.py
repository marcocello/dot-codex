#!/usr/bin/env python3
"""Statically validate a TWYD CLI Toolkit kit archive."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import stat
import sys
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any

MAX_ARCHIVE = 5 * 1024 * 1024
MAX_EXPANDED = 10 * 1024 * 1024
MAX_MEMBER = 512_000
MAX_MEMBERS = 100
MAX_TOOLS = 50
JSON_MAX_DEPTH = 32
JSON_MAX_NODES = 10_000
IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,119}$")
SCHEMA_KEYS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "const",
    "enum",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
}


class KitInvalid(ValueError):
    pass


def fail(message: str) -> None:
    raise KitInvalid(message)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def strict_json(content: bytes, name: str) -> Any:
    try:
        value = json.loads(content, parse_constant=reject_constant)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError, RecursionError) as error:
        fail(f"{name}: invalid strict JSON ({error})")
    nodes = 0
    stack = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > JSON_MAX_NODES or depth > JSON_MAX_DEPTH:
            fail(f"{name}: JSON exceeds depth/node limits")
        if isinstance(current, dict):
            stack.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
    return value


def schema_accepts(schema: dict[str, Any], value: Any) -> bool:
    if "const" in schema and value != schema["const"]:
        return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    expected = schema.get("type")
    if expected == "object":
        if not isinstance(value, dict):
            return False
        properties = schema.get("properties", {})
        if any(key not in value for key in schema.get("required", [])):
            return False
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            return False
        valid = all(
            key not in value or schema_accepts(child, value[key])
            for key, child in properties.items()
        )
    elif expected == "string":
        valid = isinstance(value, str)
    elif expected == "number":
        valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    elif expected == "integer":
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif expected == "boolean":
        valid = isinstance(value, bool)
    elif expected == "array":
        valid = isinstance(value, list) and all(
            schema_accepts(schema.get("items", {}), item) for item in value
        )
    else:
        valid = expected is None
    if not valid:
        return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            return False
        if "maximum" in schema and value > schema["maximum"]:
            return False
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            return False
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return False
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            return False
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            return False
    return True


def validate_schema(
    schema: Any, *, depth: int = 0, budget: list[int] | None = None
) -> None:
    count = budget if budget is not None else [0]
    count[0] += 1
    if depth > JSON_MAX_DEPTH or count[0] > JSON_MAX_NODES:
        fail("schema exceeds depth/node limits")
    if not isinstance(schema, dict) or set(schema) - SCHEMA_KEYS:
        fail("schema contains unsupported keywords or is not an object")
    expected = schema.get("type")
    if expected not in {None, "object", "string", "number", "integer", "boolean", "array"}:
        fail(f"schema has unsupported type: {expected!r}")
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        fail("schema enum must be a nonempty array")
    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            fail("schema properties must be an object")
        for child in properties.values():
            validate_schema(child, depth=depth + 1, budget=count)
    if expected == "array":
        validate_schema(schema.get("items"), depth=depth + 1, budget=count)
    type_keywords = {
        "object": {"properties", "required", "additionalProperties"},
        "array": {"items", "minItems", "maxItems"},
        "string": {"minLength", "maxLength"},
    }
    for schema_type, keywords in type_keywords.items():
        if set(schema) & keywords and expected != schema_type:
            fail(f"{schema_type} keywords require type={schema_type}")
    if set(schema) & {"minimum", "maximum"} and expected not in {"number", "integer"}:
        fail("numeric bounds require number or integer type")
    required = schema.get("required")
    if required is not None and (
        not isinstance(required, list)
        or not all(isinstance(item, str) for item in required)
        or len(required) != len(set(required))
        or properties is None
        or not set(required).issubset(properties)
    ):
        fail("schema required must be unique property names")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        fail("additionalProperties must be boolean")
    for keyword in ("minimum", "maximum"):
        constraint = schema.get(keyword)
        if constraint is not None and (
            isinstance(constraint, bool)
            or not isinstance(constraint, (int, float))
            or not math.isfinite(constraint)
        ):
            fail(f"{keyword} must be finite numeric")
    for keyword in ("minLength", "maxLength", "minItems", "maxItems"):
        constraint = schema.get(keyword)
        if constraint is not None and (
            isinstance(constraint, bool) or not isinstance(constraint, int) or constraint < 0
        ):
            fail(f"{keyword} must be a nonnegative integer")
    for lower, upper in (
        ("minimum", "maximum"),
        ("minLength", "maxLength"),
        ("minItems", "maxItems"),
    ):
        if lower in schema and upper in schema and schema[lower] > schema[upper]:
            fail(f"{lower} exceeds {upper}")
    shape = {key: value for key, value in schema.items() if key not in {"const", "enum"}}
    if "const" in schema and not schema_accepts(shape, schema["const"]):
        fail("const does not match its schema")
    if "enum" in schema and not all(schema_accepts(shape, item) for item in schema["enum"]):
        fail("enum value does not match its schema")


def validate_tool(tool: Any, entries: dict[str, bytes], names: set[str]) -> None:
    allowed = {
        "name",
        "description",
        "entrypoint",
        "timeout_seconds",
        "input_schema",
        "output_schema",
    }
    if not isinstance(tool, dict) or set(tool) != allowed:
        fail("tool must contain exactly the supported fields")
    name = tool["name"]
    entrypoint = tool["entrypoint"]
    description = tool["description"]
    timeout = tool["timeout_seconds"]
    if not isinstance(name, str) or not IDENTITY.fullmatch(name):
        fail("tool name is invalid")
    if name.startswith(("coworker.", "twyd.")) or name in names:
        fail(f"tool name is reserved or duplicated: {name}")
    if not isinstance(description, str) or not description.strip() or description != description.strip() or len(description) > 2_000:
        fail(f"tool description is invalid: {name}")
    if not isinstance(entrypoint, str):
        fail(f"entrypoint is invalid: {name}")
    path = PurePosixPath(entrypoint)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".py" or entrypoint not in entries:
        fail(f"entrypoint is missing or unsafe: {entrypoint}")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < float(timeout) <= 30:
        fail(f"timeout is invalid: {name}")
    validate_schema(tool["input_schema"])
    validate_schema(tool["output_schema"])
    try:
        ast.parse(entries[entrypoint], filename=entrypoint)
    except (SyntaxError, ValueError) as error:
        fail(f"entrypoint Python is invalid: {error}")
    names.add(name)


def validate_archive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"archive does not exist: {path}")
    if path.stat().st_size > MAX_ARCHIVE:
        fail("archive exceeds 5 MiB")
    try:
        archive = zipfile.ZipFile(path)
        infos = archive.infolist()
    except (OSError, zipfile.BadZipFile) as error:
        fail(f"invalid ZIP: {error}")
    if not infos or len(infos) > MAX_MEMBERS:
        fail("archive is empty or has too many members")
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        fail("archive contains duplicate member names")
    if sum(info.file_size for info in infos) > MAX_EXPANDED:
        fail("archive exceeds expanded-size limit")
    entries: dict[str, bytes] = {}
    normalized_names: set[str] = set()
    for info in infos:
        member = PurePosixPath(info.filename)
        normalized = member.as_posix()
        expected = f"{normalized}/" if info.is_dir() else normalized
        if not member.parts or normalized == "." or info.filename != expected or normalized in normalized_names:
            fail(f"member path is noncanonical or aliased: {info.filename}")
        normalized_names.add(normalized)
        if info.is_dir():
            continue
        mode = (info.external_attr >> 16) & 0o177777
        if (
            info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
            or member.is_absolute()
            or ".." in member.parts
            or any(part.startswith(".") or part == "__pycache__" for part in member.parts)
            or stat.S_IFMT(mode) == stat.S_IFLNK
            or mode & 0o111
            or info.file_size > MAX_MEMBER
            or info.filename in {"setup.py", "conftest.py"}
            or (info.filename != "kit.json" and member.suffix not in {".py", ".json"})
        ):
            fail(f"member is unsafe or unsupported: {info.filename}")
        try:
            entries[info.filename] = archive.read(info)
        except (OSError, EOFError, RuntimeError, ValueError, zipfile.BadZipFile, zlib.error) as error:
            fail(f"member cannot be read safely: {info.filename} ({error})")
        if member.suffix == ".json" and info.filename != "kit.json":
            strict_json(entries[info.filename], info.filename)
    manifest = strict_json(entries.get("kit.json", b""), "kit.json")
    required = {"id", "version", "name", "description", "contract_version", "tools"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        fail("kit.json must contain exactly the supported root fields")
    for key in ("id", "version"):
        if not isinstance(manifest[key], str) or not IDENTITY.fullmatch(manifest[key]):
            fail(f"manifest {key} is invalid")
    for key, limit in (("name", 200), ("description", 2_000)):
        value = manifest[key]
        if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > limit:
            fail(f"manifest {key} is invalid")
    if manifest["contract_version"] != "1":
        fail("contract_version must be '1'")
    tools = manifest["tools"]
    if not isinstance(tools, list) or not tools or len(tools) > MAX_TOOLS:
        fail("tools must be a nonempty array of at most 50 items")
    seen: set[str] = set()
    for tool in tools:
        validate_tool(tool, entries, seen)
    return {
        "archive": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "kit_id": manifest["id"],
        "version": manifest["version"],
        "tools": sorted(seen),
        "members": len(infos),
        "expanded_bytes": sum(info.file_size for info in infos),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        result = validate_archive(args.archive.resolve())
    except KitInvalid as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
