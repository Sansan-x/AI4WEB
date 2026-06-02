---
description: Run full Java microservice compliance threat analysis pipeline (送检即合规)
argument-hint: [--repo PATH] [--services a,b] [--middleware PATH] [--waivers PATH]
---

# Compliance Run

Execute the full compliance pipeline as **compliance-coordinator**, following the `compliance-orchestrator` skill.

## Parse arguments from: $ARGUMENTS

Defaults if omitted:

- `--repo` → `compliance/fixtures/demo-service`
- `--services` → `order-service`
- `--middleware` → `compliance/examples/middleware_cases.sample.json`
- `--waivers` → none

## Steps

1. Load skill `compliance-orchestrator` (or use preloaded coordinator context).
2. Run:
   ```bash
   python3 compliance/scripts/init_run.py \
     --project-root . \
     --repo-path <repo> \
     --services <services> \
     --middleware <middleware>
   ```
3. Invoke worker subagents via the **task** tool in pipeline order for each service:
   - `service-context` → `baseline-applicability`
   - `exposure-signal`, `dataflow-signal`, `controlplane-signal` (parallel OK via multiple task calls)
   - `risk-synthesizer`
4. Run `merge_risk_points.py` → task: `case-mapping` → `coverage-gap` → `policy-decision` → `evidence-pack`.
5. Validate artifacts after each phase with `validate_artifact.py`.
6. Report final `08-decision.json` and `09-evidence/index.json` paths.

If you are not already running as coordinator, switch to the `compliance-coordinator` agent and run the flow above.

Do not produce code-audit-style reports; only service-level risk profiles and evidence package.
