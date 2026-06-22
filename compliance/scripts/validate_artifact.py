#!/usr/bin/env python3
"""Validate a JSON artifact against a compliance schema (minimal validator, no deps)."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCHEMA_MAP = {
    "service-context": "service-context.schema.json",
    "threat-signal": "threat-signal.schema.json",
    "service-risk-profile": "service-risk-profile.schema.json",
    "risk-point-list": "risk-point.schema.json",
    "risk-points": "risk-point.schema.json",
    "applicability": "applicability.schema.json",
    "middleware-case": "middleware-case.schema.json",
    "risk-case-mapping": "risk-case-mapping.schema.json",
    "gaps": "gaps.schema.json",
    "decision": "decision.schema.json",
    "service-decision": "service-decision.schema.json",
    "product-manifest": "product-manifest.schema.json",
    "product-decision": "product-decision.schema.json",
    "service-slices": "service-slices.schema.json",
    "evidence-package": "evidence-package.schema.json",
    "public-baseline": "public-baseline.schema.json",
}


def load_schema(schema_dir: Path, name: str) -> Dict[str, Any]:
    fname = SCHEMA_MAP.get(name, name if name.endswith(".json") else f"{name}.schema.json")
    if not fname.endswith(".json"):
        fname = f"{fname}.schema.json"
    return json.loads((schema_dir / fname).read_text(encoding="utf-8"))


def check_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return True


def resolve_schema(schema: Dict[str, Any], root: Dict[str, Any]) -> Dict[str, Any]:
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/$defs/"):
            name = ref.split("/")[-1]
            defs = root.get("$defs", {})
            if name in defs:
                return resolve_schema(defs[name], root)
    return schema


def validate(value: Any, schema: Dict[str, Any], path: str = "$", root: Optional[Dict[str, Any]] = None) -> List[str]:
    if root is None:
        root = schema
    schema = resolve_schema(schema, root)
    errors: List[str] = []

    if "oneOf" in schema:
        branch_errors: List[List[str]] = []
        for subschema in schema["oneOf"]:
            resolved = resolve_schema(subschema, root)
            branch_errors.append(validate(value, resolved, path, root))
        if any(not errs for errs in branch_errors):
            return []
        return [f"{path}: value does not match any oneOf branch"] + branch_errors[0]

    if "$ref" in schema:
        return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum {schema['enum']}")
        return errors

    if schema.get("type") == "array":
        if not isinstance(value, list):
            errors.append(f"{path}: expected array")
            return errors
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: array exceeds maxItems {schema['maxItems']}")
        item_schema = schema.get("items", {})
        for i, item in enumerate(value):
            errors.extend(validate(item, item_schema, f"{path}[{i}]", root))
        return errors

    if schema.get("type") == "object":
        if not isinstance(value, dict):
            errors.append(f"{path}: expected object")
            return errors
        required: Set[str] = set(schema.get("required", []))
        props = schema.get("properties", {})
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required field '{key}'")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: unexpected field '{key}'")
        for key, subschema in props.items():
            if key in value:
                errors.extend(validate(value[key], subschema, f"{path}.{key}", root))
        return errors

    if "type" in schema and not check_type(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")

    if schema.get("type") == "string":
        if "minLength" in schema and isinstance(value, str) and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength")

    return errors


def load_category_catalog_rule_types(project_root: Path) -> Set[str]:
    template_path = project_root / "compliance" / "examples" / "public_baseline.template.json"
    if not template_path.is_file():
        return set()
    template = json.loads(template_path.read_text(encoding="utf-8"))
    return {item["ruleType"] for item in template.get("categoryCatalog", []) if "ruleType" in item}


def validate_applicability_completeness(data: Any, project_root: Path) -> List[str]:
    errors: List[str] = []
    expected = load_category_catalog_rule_types(project_root)
    if not expected:
        return errors

    seen: Set[str] = set()
    for section, key in (("applicableBaselines", "applicable"), ("excludedBaselines", None)):
        for i, item in enumerate(data.get(section, [])):
            rule_type = item.get("ruleType")
            if not rule_type:
                continue
            if rule_type in seen:
                errors.append(f"$.{section}[{i}]: duplicate ruleType {rule_type!r}")
            seen.add(rule_type)

    missing = expected - seen
    extra = seen - expected
    if missing:
        errors.append(f"$.applicability: missing ruleTypes from categoryCatalog: {sorted(missing)}")
    if extra:
        errors.append(f"$.applicability: unknown ruleTypes not in categoryCatalog: {sorted(extra)}")
    return errors


def validate_risk_point_list(data: Any, schema_dir: Path) -> List[str]:
    rp_schema = load_schema(schema_dir, "risk-point.schema.json")
    if not isinstance(data, list):
        return ["$: expected array of risk points"]
    errors = []
    for i, item in enumerate(data):
        errors.extend(validate(item, rp_schema, f"$[{i}]"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, help="Schema key or filename")
    parser.add_argument("--file", required=True)
    parser.add_argument("--schema-dir", default="compliance/schemas")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root for applicability categoryCatalog completeness checks",
    )
    args = parser.parse_args()

    schema_dir = Path(args.schema_dir)
    project_root = Path(args.project_root).resolve()
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))

    if args.schema in ("risk-point-list", "risk-points"):
        errors = validate_risk_point_list(data, schema_dir)
    else:
        schema = load_schema(schema_dir, args.schema)
        if schema.get("type") == "array" and isinstance(data, list):
            item_schema = schema.get("items", {})
            errors = []
            for i, item in enumerate(data):
                errors.extend(validate(item, item_schema, f"$[{i}]"))
        else:
            errors = validate(data, schema, root=schema)

    if args.schema == "applicability" and not errors:
        errors.extend(validate_applicability_completeness(data, project_root))

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "file": args.file}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
