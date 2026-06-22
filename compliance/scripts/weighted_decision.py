#!/usr/bin/env python3
"""Shared weighted compliance decision logic for service and product levels."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

DEFAULT_WEIGHTS = {"P0": 4, "P1": 3, "P2": 2, "P3": 1}
DECISION_ORDER = {"Block": 3, "ConditionalPass": 2, "Pass": 1}
SUBMISSION_COMPLIANT = {"Pass", "ConditionalPass"}


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Minimal YAML subset parser for policy-gate.yaml (no external deps)."""
    result: Dict[str, Any] = {}
    stack: List[Tuple[int, Any]] = [(-1, result)]
    key_stack: List[Optional[str]] = [None]

    def current_container() -> Any:
        return stack[-1][1]

    def set_value(key: str, value: Any) -> None:
        container = current_container()
        if isinstance(container, dict):
            container[key] = value

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
            key_stack.pop()

        if line.startswith("- "):
            item_text = line[2:].strip()
            container = current_container()
            if not isinstance(container, list):
                raise ValueError(f"expected list context for array item: {line}")
            if ":" in item_text:
                key, val = item_text.split(":", 1)
                key = key.strip()
                val = val.strip()
                item: Dict[str, Any] = {key: _coerce_scalar(val)}
                container.append(item)
                stack.append((indent, item))
                key_stack.append(key)
            else:
                container.append(_coerce_scalar(item_text))
            continue

        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        if val == "":
            parent = current_container()
            if not isinstance(parent, dict):
                raise ValueError(f"expected dict context for key {key}")
            if key in ("rules", "strictRules", "weightedRules", "serviceRuns"):
                new_obj: Any = []
            else:
                new_obj = {}
            parent[key] = new_obj
            stack.append((indent, new_obj))
            key_stack.append(key)
        elif val.startswith("[") and val.endswith("]"):
            items = val[1:-1].strip()
            set_value(key, [] if not items else [_coerce_scalar(x.strip()) for x in items.split(",")])
        else:
            set_value(key, _coerce_scalar(val))

    return result


def _coerce_scalar(val: str) -> Any:
    if val in ("true", "True"):
        return True
    if val in ("false", "False"):
        return False
    if val in ("null", "None", "~"):
        return None
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        pass
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val


def load_policy(policy_path: Path) -> Dict[str, Any]:
    text = policy_path.read_text(encoding="utf-8")
    try:
        import yaml

        return yaml.safe_load(text)
    except ImportError:
        return _parse_simple_yaml(text)


def classify_tier(risk: Dict[str, Any], key_baselines: List[str], policy: Dict[str, Any]) -> str:
    severity = risk.get("severity", "P1")
    category = risk.get("category", "")
    tiers = policy.get("severityTiers", {})
    mandatory = tiers.get("mandatory", {})
    mandatory_severities = set(mandatory.get("severities", ["P0"]))
    p1_domains = set(mandatory.get("p1Domains", key_baselines))

    if severity in mandatory_severities:
        return "mandatory"
    if severity == "P1" and category in p1_domains:
        return "mandatory"
    return "ratioEligible"


def excluded_domains(applicability: Dict[str, Any]) -> Set[str]:
    domains: Set[str] = set()
    for item in applicability.get("excludedBaselines", []):
        domain = item.get("domain")
        if domain:
            domains.add(domain)
    return domains


def is_risk_excluded(risk: Dict[str, Any], applicability: Dict[str, Any]) -> bool:
    category = risk.get("category", "")
    return category in excluded_domains(applicability)


def build_gap_index(gaps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for gap in gaps:
        risk_id = gap.get("riskId")
        if risk_id:
            index.setdefault(risk_id, []).append(gap)
    return index


def build_mapping_index(mappings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {m["riskId"]: m for m in mappings if m.get("riskId")}


def is_domain_matched(
    risk_id: str,
    gap_index: Dict[str, List[Dict[str, Any]]],
    mapping_index: Dict[str, Dict[str, Any]],
) -> bool:
    for gap in gap_index.get(risk_id, []):
        if gap.get("gapType") == "NoCaseMatched":
            return False
    mapping = mapping_index.get(risk_id)
    if mapping is None:
        return False
    explanation = mapping.get("explanation", "")
    if "[domain_matched]" in explanation:
        return True
    return mapping.get("coverageState") == "Covered"


def risk_weight(risk: Dict[str, Any], weights: Dict[str, int]) -> int:
    return weights.get(risk.get("severity", "P1"), 1)


def compute_weighted_score(risks: List[Dict[str, Any]], matched_flags: List[bool], weights: Dict[str, int]) -> float:
    total = 0
    matched = 0
    for risk, is_matched in zip(risks, matched_flags):
        w = risk_weight(risk, weights)
        total += w
        if is_matched:
            matched += w
    if total == 0:
        return 1.0
    return round(matched / total, 4)


def build_mandatory_gap_record(risk: Dict[str, Any], gap_index: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    gaps = gap_index.get(risk["riskId"], [])
    gap_type = "NoCaseMatched"
    for gap in gaps:
        if gap.get("gapType") == "NoCaseMatched":
            gap_type = "NoCaseMatched"
            break
    return {
        "riskId": risk["riskId"],
        "category": risk.get("category", ""),
        "severity": risk.get("severity", "P1"),
        "gapType": gap_type,
    }


def compute_service_decision(
    service: str,
    run_id: str,
    risks: List[Dict[str, Any]],
    gaps: List[Dict[str, Any]],
    mappings: List[Dict[str, Any]],
    applicability: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    key_baselines = policy.get("keyBaselines", ["SQLI", "CMDI", "FILE"])
    weights = policy.get("weights", DEFAULT_WEIGHTS)
    ratio_cfg = policy.get("coverageRatio", {})
    min_conditional = float(ratio_cfg.get("minConditionalPass", 0.70))
    min_block = float(ratio_cfg.get("minBlock", 0.50))
    policy_mode = policy.get("policyMode", "weighted")
    policy_version = policy.get("version", "1.3.0")

    gap_index = build_gap_index(gaps)
    mapping_index = build_mapping_index(mappings)

    open_risks = [
        r
        for r in risks
        if r.get("service") == service
        and r.get("status") == "Open"
        and not is_risk_excluded(r, applicability)
    ]

    if not open_risks:
        return {
            "service": service,
            "runId": run_id,
            "decision": "Pass",
            "reasons": ["no_open_risks"],
            "policyVersion": policy_version,
            "policyMode": policy_mode,
            "coverageScore": {
                "mandatoryTotal": 0,
                "mandatoryMatched": 0,
                "mandatoryGaps": [],
                "ratioEligibleTotal": 0,
                "ratioEligibleMatched": 0,
                "ratioEligibleCoverageRate": 1.0,
                "weightedScore": 1.0,
            },
            "readyForSubmission": True,
        }

    matched_flags = [is_domain_matched(r["riskId"], gap_index, mapping_index) for r in open_risks]
    weighted_score = compute_weighted_score(open_risks, matched_flags, weights)

    mandatory_risks: List[Dict[str, Any]] = []
    ratio_risks: List[Dict[str, Any]] = []
    for risk in open_risks:
        tier = classify_tier(risk, key_baselines, policy)
        if tier == "mandatory":
            mandatory_risks.append(risk)
        else:
            ratio_risks.append(risk)

    mandatory_matched = sum(
        1 for r in mandatory_risks if is_domain_matched(r["riskId"], gap_index, mapping_index)
    )
    mandatory_gaps = [
        build_mandatory_gap_record(r, gap_index)
        for r in mandatory_risks
        if not is_domain_matched(r["riskId"], gap_index, mapping_index)
    ]

    ratio_matched = sum(
        1 for r in ratio_risks if is_domain_matched(r["riskId"], gap_index, mapping_index)
    )
    ratio_total = len(ratio_risks)
    ratio_rate = round(ratio_matched / ratio_total, 4) if ratio_total else 1.0

    coverage_score = {
        "mandatoryTotal": len(mandatory_risks),
        "mandatoryMatched": mandatory_matched,
        "mandatoryGaps": mandatory_gaps,
        "ratioEligibleTotal": ratio_total,
        "ratioEligibleMatched": ratio_matched,
        "ratioEligibleCoverageRate": ratio_rate,
        "weightedScore": weighted_score,
    }

    reasons: List[str] = []
    if mandatory_gaps:
        decision = "Block"
        reasons.append("mandatory_coverage_gap")
    elif ratio_total == 0:
        decision = "ConditionalPass"
        reasons.append("mandatory_coverage_met")
    elif ratio_rate >= min_conditional:
        decision = "ConditionalPass"
        reasons.append("optional_coverage_ratio_met")
    elif ratio_rate >= min_block:
        decision = "ConditionalPass"
        reasons.append("optional_coverage_ratio_partial")
    else:
        decision = "Block"
        reasons.append("insufficient_optional_coverage")

    return {
        "service": service,
        "runId": run_id,
        "decision": decision,
        "reasons": reasons,
        "policyVersion": policy_version,
        "policyMode": policy_mode,
        "coverageScore": coverage_score,
        "readyForSubmission": decision in SUBMISSION_COMPLIANT,
    }


def worst_decision(decisions: List[str]) -> str:
    if not decisions:
        return "Pass"
    return max(decisions, key=lambda d: DECISION_ORDER.get(d, 0))


def compute_product_decision(
    product_id: str,
    product_run_id: str,
    service_decisions: List[Dict[str, Any]],
    service_run_entries: List[Dict[str, Any]],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    ratio_cfg = policy.get("coverageRatio", {})
    min_conditional = float(ratio_cfg.get("minConditionalPass", 0.70))
    min_block = float(ratio_cfg.get("minBlock", 0.50))
    policy_mode = policy.get("policyMode", "weighted")
    policy_version = policy.get("version", "1.3.0")
    product_agg = policy.get("productAggregation", {})

    all_mandatory_gaps: List[Dict[str, Any]] = []
    ratio_total = 0
    ratio_matched = 0
    weighted_sum = 0.0
    weighted_count = 0

    services_pass = 0
    services_conditional = 0
    services_block = 0

    service_summaries: List[Dict[str, Any]] = []
    for entry, svc_decision in zip(service_run_entries, service_decisions):
        score = svc_decision.get("coverageScore", {})
        for gap in score.get("mandatoryGaps", []):
            all_mandatory_gaps.append({**gap, "service": svc_decision.get("service", entry.get("service", ""))})
        ratio_total += score.get("ratioEligibleTotal", 0)
        ratio_matched += score.get("ratioEligibleMatched", 0)
        ws = score.get("weightedScore", 0.0)
        weighted_sum += ws
        weighted_count += 1

        svc_dec = svc_decision.get("decision", "Block")
        if svc_dec == "Pass":
            services_pass += 1
        elif svc_dec == "ConditionalPass":
            services_conditional += 1
        else:
            services_block += 1

        service_summaries.append(
            {
                "service": svc_decision.get("service", entry.get("service", "")),
                "runId": entry.get("runId", svc_decision.get("runId", "")),
                "decision": svc_dec,
                "decisionPath": entry.get("decisionPath", ""),
            }
        )

    ratio_rate = round(ratio_matched / ratio_total, 4) if ratio_total else 1.0
    product_weighted = round(weighted_sum / weighted_count, 4) if weighted_count else 1.0

    coverage_score = {
        "servicesTotal": len(service_decisions),
        "servicesPass": services_pass,
        "servicesConditionalPass": services_conditional,
        "servicesBlock": services_block,
        "mandatoryTotal": sum(s.get("coverageScore", {}).get("mandatoryTotal", 0) for s in service_decisions),
        "mandatoryMatched": sum(s.get("coverageScore", {}).get("mandatoryMatched", 0) for s in service_decisions),
        "mandatoryGaps": all_mandatory_gaps,
        "ratioEligibleTotal": ratio_total,
        "ratioEligibleMatched": ratio_matched,
        "ratioEligibleCoverageRate": ratio_rate,
        "weightedScore": product_weighted,
    }

    reasons: List[str] = []
    block_on_service = product_agg.get("blockOnAnyServiceBlock", False)

    if product_agg.get("blockOnAnyMandatoryGap", True) and all_mandatory_gaps:
        decision = "Block"
        reasons.append("product_mandatory_coverage_gap")
    elif block_on_service and services_block > 0:
        decision = "Block"
        reasons.append("product_service_block_present")
    elif ratio_total == 0 and not all_mandatory_gaps:
        decision = worst_decision([s.get("decision", "Pass") for s in service_decisions])
        if decision == "Pass":
            reasons.append("product_all_services_pass")
        else:
            reasons.append("product_mandatory_coverage_met")
    elif ratio_rate >= min_conditional:
        decision = "ConditionalPass"
        reasons.append("product_ratio_eligible_met")
    elif ratio_rate >= min_block:
        decision = "ConditionalPass"
        reasons.append("product_ratio_eligible_partial")
    else:
        decision = "Block"
        reasons.append("product_insufficient_optional_coverage")

    from datetime import datetime, timezone

    return {
        "productId": product_id,
        "productRunId": product_run_id,
        "decision": decision,
        "readyForSubmission": decision in SUBMISSION_COMPLIANT,
        "reasons": reasons,
        "policyVersion": policy_version,
        "policyMode": policy_mode,
        "coverageScore": coverage_score,
        "serviceDecisions": service_summaries,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


def build_run_summary(
    run_id: str,
    service_decisions: List[Dict[str, Any]],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    decisions = [s["decision"] for s in service_decisions]
    run_decision = worst_decision(decisions)
    reasons: List[str] = []
    if run_decision == "Block":
        reasons.append("service_blockers_present")
    elif run_decision == "ConditionalPass":
        reasons.append("service_conditional_pass")
    else:
        reasons.append("all_services_pass")

    return {
        "decision": run_decision,
        "reasons": reasons,
        "policyVersion": policy.get("version", "1.3.0"),
        "policyMode": policy.get("policyMode", "weighted"),
        "serviceSummaries": [
            {
                "service": s["service"],
                "decision": s["decision"],
                "path": f"08-decisions/{s['service']}.json",
            }
            for s in service_decisions
        ],
    }
