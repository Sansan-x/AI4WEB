#!/usr/bin/env python3
"""Create a compliance run directory and manifest."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize compliance run directory")
    parser.add_argument("--project-root", default=".", help="AI4Mic-Threat project root")
    parser.add_argument("--run-id", help="Run ID (auto-generated if omitted)")
    parser.add_argument("--repo-path", required=True, help="Path to Java repo under analysis")
    parser.add_argument("--services", required=True, help="Comma-separated service names")
    parser.add_argument("--middleware", help="Path to middleware cases JSON")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_base = root / ".claude" / "runs" / run_id

    subdirs = [
        "01-context",
        "02-applicability",
        "03-signals",
        "04-profiles",
        "09-evidence",
    ]
    for d in subdirs:
        (runs_base / d).mkdir(parents=True, exist_ok=True)

    services = [s.strip() for s in args.services.split(",") if s.strip()]
    manifest = {
        "runId": run_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "repoPath": args.repo_path,
        "services": services,
        "middlewareCasesPath": args.middleware,
        "status": "initialized",
        "taxonomyVersion": "1.0.0",
        "policyVersion": "1.0.0",
    }
    manifest_path = runs_base / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    slices = {
        "runId": run_id,
        "repoPath": args.repo_path,
        "services": [
            {"serviceName": s, "sourcePaths": ["src/main/java"]}
            for s in services
        ],
    }
    slices_path = runs_base / "00-service-slices.json"
    slices_path.write_text(json.dumps(slices, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"runId": run_id, "runsDir": str(runs_base), "manifest": str(manifest_path)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
