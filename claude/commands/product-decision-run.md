---
description: Aggregate per-service compliance decisions into product-level weighted conclusion (standalone)
argument-hint: [--product-run-id ID] [--service-runs runId:service,...] [--manifest PATH]
---

# Product Decision Run

Standalone product-level 送检即合规 evaluation. **Not** part of `/compliance-run`.

Run as **product-decision** agent, following the `product-gate-decision` skill.

## Parse arguments from: $ARGUMENTS

- `--product-run-id` → auto-generated timestamp if omitted
- `--service-runs` → comma-separated `runId:service` pairs (required unless `--manifest` given)
- `--manifest` → path to existing `product-manifest.json`
- `--product-id` → default `demo-product`

## Steps

1. Load skill `product-gate-decision`.
2. If no manifest, initialize:

   ```bash
   python3 compliance/scripts/init_product_eval.py \
     --product-id <product-id> \
     --product-run-id <productRunId> \
     --service-runs <service-runs> \
     --project-root .
   ```

3. Validate manifest:

   ```bash
   python3 compliance/scripts/validate_artifact.py \
     --schema product-manifest \
     --file .claude/runs/<productRunId>/product-manifest.json
   ```

4. Aggregate:

   ```bash
   python3 compliance/scripts/aggregate_product_decision.py \
     --manifest .claude/runs/<productRunId>/product-manifest.json \
     --project-root .
   ```

5. Validate output:

   ```bash
   python3 compliance/scripts/validate_artifact.py \
     --schema product-decision \
     --file .claude/runs/<productRunId>/product-decision.json
   ```

6. Report `decision`, `readyForSubmission`, and file path.

Each `runId:service` must already have `.claude/runs/{runId}/08-decisions/{service}.json` from a completed compliance run.

Do not spawn compliance-coordinator or re-run the threat analysis pipeline.
