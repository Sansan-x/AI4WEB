#!/usr/bin/env python3
"""Merge exposure, dataflow, controlplane signal files for one service."""
import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict:
    if not path.exists():
        return {"service": "", "signalType": "", "signals": []}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--exposure", required=True)
    parser.add_argument("--dataflow", required=True)
    parser.add_argument("--controlplane", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    merged = {
        "service": args.service,
        "signals": {
            "exposure": load(Path(args.exposure)),
            "dataflow": load(Path(args.dataflow)),
            "controlplane": load(Path(args.controlplane)),
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "count": sum(len(v.get("signals", [])) for v in merged["signals"].values())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
