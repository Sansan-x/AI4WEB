#!/usr/bin/env python3
"""Aggregate risk points from service profiles or jsonl into 05-risk-points.json."""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles-dir", required=True, help="Directory with 04-profiles/*.json")
    parser.add_argument("--jsonl", help="Optional 04-risk-points.jsonl path")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    points: list = []
    profiles_dir = Path(args.profiles_dir)
    if profiles_dir.is_dir():
        for profile_path in sorted(profiles_dir.glob("*.json")):
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            for rp in profile.get("riskPoints", []):
                points.append(rp)

    if args.jsonl:
        jsonl_path = Path(args.jsonl)
        if jsonl_path.exists():
            for line in jsonl_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    points.append(json.loads(line))

    seen = set()
    unique = []
    for rp in points:
        rid = rp.get("riskId")
        if rid and rid not in seen:
            seen.add(rid)
            unique.append(rp)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(unique, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "count": len(unique)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
