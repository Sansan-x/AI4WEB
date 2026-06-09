# AI4Mic-Threat — 送检即合规

## Purpose

This project implements **service-level threat risk profiles** for Java microservices, mapped to security baselines and middleware test cases. Output is for **compliance evaluation**, not line-by-line code audit.

## Default workflow

1. Run `/compliance-run` with repo path, services, and middleware results; or
2. `claude --agent compliance-coordinator -p "..."` for automation.

## Rules

- All pipeline artifacts are JSON under `.claude/runs/{runId}/`.
- Follow paths and schemas in the `compliance-orchestrator` skill.
- Baseline checklist: `compliance/taxonomy/baseline-catalog.yaml` — 14 ruleTypes aligned with `public_baseline.template.json` `categoryCatalog` (edit and restart session to reload).
- Only **compliance-coordinator** may spawn subagents via the Agent tool.
- Worker agents write **only** under `.claude/runs/` unless reading the target Java repo.

## Validation

```bash
python3 compliance/scripts/validate_artifact.py --schema <key> --file <path> --project-root .
```

## Golden demo

```bash
python3 compliance/scripts/run_golden_pipeline.py
```

Demo Java service: `compliance/fixtures/demo-service/`
