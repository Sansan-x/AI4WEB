#!/usr/bin/env python3
"""Compute weighted per-service and run-level compliance decisions."""
import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from weighted_decision import (  # noqa: E402
    build_run_summary,
    compute_service_decision,
    load_policy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute weighted service compliance decisions")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--service", help="Single service name; omit to process all manifest services")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--policy",
        default="compliance/taxonomy/policy-gate.yaml",
        help="Path to policy-gate.yaml relative to project root",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    runs = root / ".claude" / "runs" / args.run_id
    if not runs.is_dir():
        print(json.dumps({"error": f"run directory not found: {runs}"}), file=sys.stderr)
        return 1

    manifest = json.loads((runs / "manifest.json").read_text(encoding="utf-8"))
    policy_path = root / args.policy
    policy = load_policy(policy_path)

    if policy.get("policyMode") != "weighted":
        print(
            json.dumps({"warning": f"policyMode is {policy.get('policyMode')}, expected weighted"}),
            file=sys.stderr,
        )

    services = [args.service] if args.service else manifest.get("services", [])
    if not services:
        print(json.dumps({"error": "no services to process"}), file=sys.stderr)
        return 1

    risk_points = json.loads((runs / "05-risk-points.json").read_text(encoding="utf-8"))
    gaps_doc = json.loads((runs / "07-gaps.json").read_text(encoding="utf-8"))
    mappings_doc = json.loads((runs / "06-mappings.json").read_text(encoding="utf-8"))
    gaps = gaps_doc.get("gaps", [])
    mappings = mappings_doc.get("mappings", [])

    decisions_dir = runs / "08-decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    service_decisions = []
    for service in services:
        applicability_path = runs / "02-applicability" / f"{service}.json"
        if not applicability_path.is_file():
            print(json.dumps({"error": f"missing applicability: {applicability_path}"}), file=sys.stderr)
            return 1
        applicability = json.loads(applicability_path.read_text(encoding="utf-8"))

        svc_decision = compute_service_decision(
            service=service,
            run_id=args.run_id,
            risks=risk_points,
            gaps=gaps,
            mappings=mappings,
            applicability=applicability,
            policy=policy,
        )
        out_path = decisions_dir / f"{service}.json"
        out_path.write_text(json.dumps(svc_decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        service_decisions.append(svc_decision)

        profile_path = runs / "04-profiles" / f"{service}.json"
        if profile_path.is_file():
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["readyForSubmission"] = svc_decision["readyForSubmission"]
            profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    run_summary = build_run_summary(args.run_id, service_decisions, policy)
    (runs / "08-decision.json").write_text(
        json.dumps(run_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "runId": args.run_id,
                "services": [s["service"] for s in service_decisions],
                "runDecision": run_summary["decision"],
                "serviceDecisions": [
                    {"service": s["service"], "decision": s["decision"], "path": f"08-decisions/{s['service']}.json"}
                    for s in service_decisions
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
