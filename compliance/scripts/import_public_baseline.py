#!/usr/bin/env python3
"""Merge imported public security baseline test data into a full baseline template."""
import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


COMPLETED_STATUS = "已完成"


def rule_covered(datas: List[Dict[str, Any]]) -> bool:
    return any(d.get("status") == COMPLETED_STATUS for d in datas)


def upsert_datas(existing: List[Dict[str, Any]], incoming: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_service: Dict[str, Dict[str, Any]] = {d["service"]: dict(d) for d in existing}
    for entry in incoming:
        service = entry.get("service", "")
        if not service:
            continue
        by_service[service] = {
            "service": service,
            "status": entry.get("status", ""),
            "selectResult": entry.get("selectResult", ""),
        }
    return list(by_service.values())


def collect_services(rules: List[Dict[str, Any]]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for rule in rules:
        for entry in rule.get("datas", []):
            service = entry.get("service", "")
            if service and service not in seen:
                seen.add(service)
                ordered.append(service)
    return ordered


def compute_summary(rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_rules = len(rules)
    covered_rules = sum(1 for r in rules if r.get("covered"))
    services = collect_services(rules)
    coverage_by_service: Dict[str, Dict[str, int]] = {}
    for service in services:
        covered = sum(
            1
            for r in rules
            if any(
                d.get("service") == service and d.get("status") == COMPLETED_STATUS
                for d in r.get("datas", [])
            )
        )
        coverage_by_service[service] = {"total": total_rules, "covered": covered}
    return {
        "totalRules": total_rules,
        "coveredRules": covered_rules,
        "services": services,
        "coverageByService": coverage_by_service,
    }


def filter_by_service(baseline: Dict[str, Any], service: str) -> Dict[str, Any]:
    filtered_rules = []
    for rule in baseline.get("rules", []):
        matching = [d for d in rule.get("datas", []) if d.get("service") == service]
        filtered_rule = {
            "ruleType": rule["ruleType"],
            "ruleId": rule["ruleId"],
            "ruleName": rule["ruleName"],
            "datas": matching,
            "covered": rule_covered(matching),
        }
        filtered_rules.append(filtered_rule)
    result = copy.deepcopy(baseline)
    result["rules"] = filtered_rules
    result["summary"] = compute_summary(filtered_rules)
    return result


def merge_baseline(
    template: Dict[str, Any],
    import_doc: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    warnings: List[str] = []
    result = copy.deepcopy(template)
    index = {r["ruleId"]: r for r in result.get("rules", [])}

    for import_rule in import_doc.get("rules", []):
        rule_id = import_rule.get("ruleId")
        if not rule_id or rule_id not in index:
            warnings.append(f"unknown ruleId skipped: {rule_id!r}")
            continue
        target = index[rule_id]
        target["datas"] = upsert_datas(target.get("datas", []), import_rule.get("datas", []))
        target["covered"] = rule_covered(target["datas"])

    for rule in result.get("rules", []):
        if "covered" not in rule:
            rule["covered"] = rule_covered(rule.get("datas", []))

    import_meta = {
        "importBatchId": import_doc.get("importBatchId", ""),
        "importedAt": import_doc.get("importedAt", ""),
    }
    result["importMeta"] = import_meta
    result["summary"] = compute_summary(result.get("rules", []))
    return result, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge public baseline import data into template")
    parser.add_argument("--template", required=True, help="Path to public_baseline.template.json")
    parser.add_argument("--import", dest="import_path", required=True, help="Path to import JSON")
    parser.add_argument("--output", required=True, help="Output merged baseline path")
    parser.add_argument(
        "--service",
        help="Optional: filter output to a single service (matches datas.service)",
    )
    args = parser.parse_args()

    template = json.loads(Path(args.template).read_text(encoding="utf-8"))
    import_doc = json.loads(Path(args.import_path).read_text(encoding="utf-8"))

    merged, warnings = merge_baseline(template, import_doc)
    if args.service:
        merged = filter_by_service(merged, args.service)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    payload: Dict[str, Any] = {
        "output": str(out),
        "totalRules": merged.get("summary", {}).get("totalRules"),
        "coveredRules": merged.get("summary", {}).get("coveredRules"),
        "services": merged.get("summary", {}).get("services"),
    }
    if warnings:
        payload["warnings"] = warnings
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
