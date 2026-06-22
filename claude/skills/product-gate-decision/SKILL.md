---
name: product-gate-decision
description: Aggregates per-service 08-decisions into product-level weighted compliance conclusion. Standalone — not part of compliance-run pipeline.
---

# Product Gate Decision

## Purpose

Produce a **product-level** 送检即合规 conclusion by pooling weighted coverage scores from completed microservice runs. Does **not** re-analyze Java code or re-run threat signals.

## Inputs

- `.claude/runs/{productRunId}/product-manifest.json` — schema `product-manifest`
- `compliance/taxonomy/policy-gate.yaml` (path from manifest `policyGatePath`)

Each `serviceRuns[]` entry must point to an existing:

`.claude/runs/{runId}/08-decisions/{service}.json` — schema `service-decision`

## Output

`.claude/runs/{productRunId}/product-decision.json` — schema `product-decision`

## Preferred execution

```bash
python3 compliance/scripts/aggregate_product_decision.py \
  --manifest .claude/runs/{productRunId}/product-manifest.json \
  --project-root .

python3 compliance/scripts/validate_artifact.py \
  --schema product-decision \
  --file .claude/runs/{productRunId}/product-decision.json
```

## Initialize manifest (optional)

```bash
python3 compliance/scripts/init_product_eval.py \
  --product-id demo-product \
  --product-run-id {productRunId} \
  --service-runs golden-demo-soft:order-service,golden-demo-unmatched:order-service \
  --project-root .
```

## Product aggregation rules (v1.3)

From `productAggregation` in policy-gate.yaml (default):

- **Pool** `ratioEligibleMatched` / `ratioEligibleTotal` across all services.
- **Block** if any pooled `mandatoryGaps` exist (`blockOnAnyMandatoryGap: true`).
- **Do not** Block solely because a single service is Block (`blockOnAnyServiceBlock: false`).
- Apply same ratio thresholds as service level (`minConditionalPass: 0.70`, `minBlock: 0.50`).

## Reason codes

| Reason | Meaning |
|--------|---------|
| `product_mandatory_coverage_gap` | P0 or key-baseline P1 uncovered somewhere in product |
| `product_ratio_eligible_met` | Pooled ratio ≥ 70% |
| `product_ratio_eligible_partial` | Pooled ratio 50–70% |
| `product_insufficient_optional_coverage` | Pooled ratio < 50% |
| `product_all_services_pass` | All services Pass, no ratio targets |
| `product_mandatory_coverage_met` | Mandatory met, no ratio-eligible risks |

## Constraints

- Do **not** spawn subagents.
- Do **not** modify service run artifacts.
- Validate manifest and each service-decision before aggregating.
