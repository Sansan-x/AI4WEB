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

| Phase | Agent / executor | Output |
|-------|------------------|--------|
| 0 | coordinator + init_run.py | `manifest.json`, `00-service-slices.json` |
| 1 | service-context × N | `01-context/{service}.json` |
| 2 | baseline-applicability × N | `02-applicability/{service}.json` |
| 3 | exposure-signal, dataflow-signal, controlplane-signal × N (parallel OK) | `03-signals/{service}/{exposure,dataflow,controlplane}.json` |
| 4 | risk-synthesizer × N | `04-profiles/{service}.json` |
| 5 | coordinator + merge_risk_points.py | `05-risk-points.json` |
| 6 | case-mapping | `06-mappings.json` |
| 7 | coverage-gap | `07-gaps.json` |
| 8 | **coordinator + `compute_service_decision.py`** | `08-decisions/{service}.json`, `08-decision.json` (run summary) |
| 9 | evidence-pack | `09-evidence/index.json` |

**Submission gate (policy v1.3, `policyMode: weighted`)**: per-service `08-decisions/{service}.json` — `Pass`/`ConditionalPass` = 送检即合规. P0 + key-baseline P1 mandatory; other P1/P2/P3 by coverage ratio. Run-level `08-decision.json` is worst-of summary.

**Product-level gate (standalone)**: use `/product-decision-run` or `product-decision` agent — not part of this pipeline.

## Phase 8 — script only (no LLM)

Coordinator runs the deterministic script directly. **Do not** spawn/task `policy-decision` during `/compliance-run`. Use the `policy-decision` agent only for manual debugging or non-weighted (`lenient`/`strict`) policy modes.

```bash
python3 compliance/scripts/compute_service_decision.py \
  --run-id {runId} \
  --project-root .

# Validate each service in manifest.services[]
python3 compliance/scripts/validate_artifact.py \
  --schema service-decision \
  --file .claude/runs/{runId}/08-decisions/{service}.json \
  --project-root .

python3 compliance/scripts/validate_artifact.py \
  --schema decision \
  --file .claude/runs/{runId}/08-decision.json \
  --project-root .
```

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
- `Follow compliance-orchestrator § Scan budget. Service-level only; no code audit.`

**Phase 3 (signal agents)** — also include:

- `sourcePaths`: from `00-service-slices.json` for this service
- `scanBudget`: Grep-first, max 12 reads, applicability-first, stop per domain after hit

**Phase 4 (risk-synthesizer)** — also include:

- `inputsOnly`: `02-applicability` + `03-signals/*.json` — do not scan repo

## Merge commands

```bash
python3 compliance/scripts/merge_risk_points.py \
  --profiles-dir .claude/runs/{runId}/04-profiles \
  --output .claude/runs/{runId}/05-risk-points.json
```

## Scan budget (Phase 3–4)

Authoritative constraints for signal and synthesizer workers.

### Scope

- Read only `sourcePaths` from `00-service-slices.json` for the service (default `src/main/java`) plus `src/main/resources/application*.yml|properties`
- **Do not** scan: `src/test/**`, `**/*Test.java`, `**/*IT.java`, `target/`, `build/`, `generated/`, `.git/`

### Phase 3 — signal agents (exposure, dataflow, controlplane)

| Rule | Requirement |
|------|-------------|
| Applicability-first | Read `02-applicability` first; for `excludedBaselines` domains emit `not_applicable` only — **do not open code** |
| Grep-before-Read | Use skill patterns via `Grep`; `Read` only files with hits |
| File read cap | Max **12** source file reads per signal agent; after cap, mark remaining applicable domains `absent` |
| Stop per domain | After `confirmed` or `likely` for a domain, stop searching that domain |
| No hits | Applicable domain with no Grep hits → single `absent` signal, `anchors: []` |
| Anchors | Max 3 `anchors` per signal; when `Read`ing, use match line ±20 lines context only |
| Forbidden output | CWE lists, per-file reports, full class enumeration, stacking `likely` findings |

### Phase 4 — risk-synthesizer

| Rule | Requirement |
|------|-------------|
| JSON inputs only | Read `02-applicability`, `03-signals/{service}/*.json`, taxonomy default severities |
| No repo rescan | Do not `Grep` or `Read` the target Java repository |
| Synthesis cap | Only `confirmed`/`likely` → one RiskPoint per domain; copy `codeEvidence` from signal `anchors` (max 3) |
| readyForSubmission | Set `false` in Phase 4; Phase 8 script updates from `08-decisions/{service}.json` |

## Granularity rules

- Max 3 `anchors` per ThreatSignal
- Do not map ruleTypes/domains excluded in `02-applicability`
- Never produce CWE dumps or full-file audit reports
