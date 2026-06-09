---
name: compliance-orchestrator
description: Orchestrates Java microservice compliance threat analysis pipeline (送检即合规). Use when running /compliance-run, coordinating subagents, or managing .claude/runs/{runId} artifacts.
---

# Compliance Orchestrator

## Goal

Produce **service-level risk profiles** mappable to security baselines—not line-by-line code audits.

## Initialize run

```bash
python3 compliance/scripts/init_run.py \
  --project-root . \
  --repo-path <REPO_PATH> \
  --services <svc1,svc2> \
  --middleware <MIDDLEWARE_JSON> \
  --public-baseline compliance/examples/public_baseline.template.json
```

Capture `runId` from stdout JSON. All artifacts go under `.claude/runs/{runId}/`.

## Pipeline phases

| Phase | Agent | Output |
|-------|-------|--------|
| 0 | coordinator + init_run.py | `manifest.json`, `00-service-slices.json` |
| 1 | service-context × N | `01-context/{service}.json` |
| 2 | baseline-applicability × N | `02-applicability/{service}.json` |
| 3 | exposure-signal, dataflow-signal, controlplane-signal × N (parallel OK) | `03-signals/{service}/{exposure,dataflow,controlplane}.json` |
| 4 | risk-synthesizer × N | `04-profiles/{service}.json` |
| 5 | coordinator + merge_risk_points.py | `05-risk-points.json` |
| 6 | case-mapping | `06-mappings.json` |
| 7 | coverage-gap | `07-gaps.json` |
| 8 | policy-decision | `08-decisions/{service}.json`, `08-decision.json` (run summary) |
| 9 | evidence-pack | `09-evidence/index.json` |

**Submission gate (policy v1.3, `policyMode: weighted`)**: per-service `08-decisions/{service}.json` — `Pass`/`ConditionalPass` = 送检即合规. P0 + key-baseline P1 mandatory; other P1/P2/P3 by coverage ratio. Run-level `08-decision.json` is worst-of summary.

**Product-level gate (standalone)**: use `/product-decision-run` or `product-decision` agent — not part of this pipeline.

## Validation gate

After each phase, validate artifacts:

```bash
python3 compliance/scripts/validate_artifact.py \
  --schema <schema-key> \
  --file .claude/runs/{runId}/<artifact>.json \
  --schema-dir compliance/schemas \
  --project-root .
```

Schema keys: `service-slices`, `service-context`, `applicability`, `threat-signal`, `service-risk-profile`, `risk-points`, `risk-case-mapping`, `gaps`, `decision`, `service-decision`, `evidence-package`.

On validation failure: write `08-decision.json` with `{"decision":"Block","reasons":["pipelineDegraded"]}` and **stop** delegating to further subagents.

## Delegation (Claude Code vs OpenCode)

**Claude Code** — use the **Agent** tool with worker agent names (`service-context`, `baseline-applicability`, etc.). Parallel signal phases may use `background: true`.

**OpenCode** — use the **task** tool with `subagent_type` set to the worker name (no `@` prefix). Example:

```text
task({ subagent_type: "service-context", prompt: "runId=... serviceName=... output=.claude/runs/.../01-context/....json" })
```

For parallel signals, issue multiple task calls for `exposure-signal`, `dataflow-signal`, and `controlplane-signal`.

## Delegation prompt template

When delegating to a worker, always include:

- `runId`, `serviceName`, `repoPath`, `publicBaselinePath` (from manifest)
- exact **output file path**
- path to upstream inputs (context, applicability, signals)

## Merge commands

```bash
python3 compliance/scripts/merge_risk_points.py \
  --profiles-dir .claude/runs/{runId}/04-profiles \
  --output .claude/runs/{runId}/05-risk-points.json
```

## Granularity rules

- Max 3 `anchors` per ThreatSignal
- Do not map ruleTypes/domains excluded in `02-applicability`
- Never produce CWE dumps or full-file audit reports
