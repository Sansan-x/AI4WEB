#!/usr/bin/env python3
"""Initialize a product-level compliance evaluation run directory and manifest."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_service_runs(spec: str, project_root: Path) -> list:
    """Parse service-runs like run-id:service,run-id2:service2 into manifest entries."""
    entries = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"invalid service-run spec (expected runId:service): {part!r}")
        run_id, service = part.split(":", 1)
        run_id = run_id.strip()
        service = service.strip()
        decision_path = f".claude/runs/{run_id}/08-decisions/{service}.json"
        abs_path = project_root / decision_path
        if not abs_path.is_file():
            raise FileNotFoundError(f"service decision not found: {decision_path}")
        entries.append(
            {
                "service": service,
                "runId": run_id,
                "decisionPath": decision_path,
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize product compliance evaluation")
    parser.add_argument("--product-id", default="demo-product")
    parser.add_argument("--product-run-id", help="Auto-generated if omitted")
    parser.add_argument(
        "--service-runs",
        required=True,
        help="Comma-separated runId:service pairs (e.g. golden-demo-soft:order-service)",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--policy-gate",
        default="compliance/taxonomy/policy-gate.yaml",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    product_run_id = args.product_run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-product")
    product_dir = root / ".claude" / "runs" / product_run_id
    product_dir.mkdir(parents=True, exist_ok=True)

    try:
        service_runs = parse_service_runs(args.service_runs, root)
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    manifest = {
        "productId": args.product_id,
        "productRunId": product_run_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "serviceRuns": service_runs,
        "policyGatePath": args.policy_gate,
    }
    manifest_path = product_dir / "product-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "productRunId": product_run_id,
                "productDir": str(product_dir),
                "manifest": str(manifest_path),
                "serviceRuns": len(service_runs),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
