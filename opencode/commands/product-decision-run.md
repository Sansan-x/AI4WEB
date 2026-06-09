---
description: Aggregate per-service compliance decisions into product-level weighted conclusion (standalone)
argument-hint: [--product-run-id ID] [--service-runs runId:service,...] [--manifest PATH]
---

# Product Decision Run

Standalone product-level 送检即合规 evaluation. **Not** part of `/compliance-run`.

Use the **product-decision** agent (primary mode), following the `product-gate-decision` skill.

## Parse arguments from: $ARGUMENTS

- `--product-run-id` → auto-generated timestamp if omitted
- `--service-runs` → comma-separated `runId:service` pairs (required unless `--manifest` given)
- `--manifest` → path to existing `product-manifest.json`
- `--product-id` → default `demo-product`

## Steps

1. Load skill `product-gate-decision` via `skill({ name: "product-gate-decision" })`.
2. If no manifest, run `init_product_eval.py` with the arguments above.
3. Validate manifest (`product-manifest` schema).
4. Run `aggregate_product_decision.py`.
5. Validate `product-decision.json` (`product-decision` schema).
6. Report `decision`, `readyForSubmission`, and file path.

Each service run must already have `08-decisions/{service}.json` from a completed compliance pipeline.

Do not invoke compliance-coordinator or re-run threat analysis.
