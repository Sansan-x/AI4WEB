#!/usr/bin/env python3
"""Aggregate per-service decisions into a product-level compliance conclusion."""
import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from weighted_decision import compute_product_decision, load_policy  # noqa: E402


def resolve_path(root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate service decisions into product decision")
    parser.add_argument("--manifest", help="Path to product-manifest.json")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", help="Output path for product-decision.json")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()

    if args.manifest:
        manifest_path = resolve_path(root, args.manifest)
    else:
        print(json.dumps({"error": "--manifest is required"}), file=sys.stderr)
        return 1

    if not manifest_path.is_file():
        print(json.dumps({"error": f"manifest not found: {manifest_path}"}), file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    product_id = manifest.get("productId", "unknown-product")
    product_run_id = manifest.get("productRunId", manifest_path.parent.name)
    service_runs = manifest.get("serviceRuns", [])

    policy_rel = manifest.get("policyGatePath", "compliance/taxonomy/policy-gate.yaml")
    policy = load_policy(resolve_path(root, policy_rel))

    service_decisions = []
    for entry in service_runs:
        decision_path = resolve_path(root, entry["decisionPath"])
        if not decision_path.is_file():
            print(json.dumps({"error": f"service decision not found: {decision_path}"}), file=sys.stderr)
            return 1
        service_decisions.append(json.loads(decision_path.read_text(encoding="utf-8")))

    product_decision = compute_product_decision(
        product_id=product_id,
        product_run_id=product_run_id,
        service_decisions=service_decisions,
        service_run_entries=service_runs,
        policy=policy,
    )

    if args.output:
        output_path = resolve_path(root, args.output)
    else:
        output_path = manifest_path.parent / "product-decision.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(product_decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"productRunId": product_run_id, "decision": product_decision["decision"], "output": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
