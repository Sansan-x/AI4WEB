# AI4Mic-Threat — 送检即合规

## Purpose

This project implements **service-level threat risk profiles** for Java microservices, mapped to security baselines and middleware test cases. Output is for **compliance evaluation**, not line-by-line code audit.

## Default workflow

### Claude Code

1. Run `/compliance-run` with repo path, services, and middleware results; or
2. `claude --agent compliance-coordinator -p "..."` for automation.

### OpenCode

1. Set models (see `.env.example` or `export OPENCODE_MODEL=provider/model-id`; run `opencode models` to list IDs).
2. Start `opencode` in this repo (default agent: `compliance-coordinator`).
3. Run `/compliance-run` with the same arguments as Claude Code.

## Rules

- All pipeline artifacts are JSON under `.claude/runs/{runId}/`.
- Follow paths and schemas in the `compliance-orchestrator` skill.
- Baseline checklist: `compliance/taxonomy/baseline-catalog.yaml` — 14 ruleTypes aligned with `public_baseline.template.json` `categoryCatalog` (edit and restart session to reload).
- **Claude Code**: only **compliance-coordinator** may spawn subagents via the Agent tool.
- **OpenCode**: only **compliance-coordinator** may invoke workers via the **task** tool (subagent names without `@`).
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

Default policy gate: **v1.3** (`compliance/taxonomy/policy-gate.yaml`, `policyMode: weighted`). P0 + key-baseline P1 mandatory; other P1/P2/P3 by coverage ratio. Pass/ConditionalPass = 送检即合规. Product-level aggregation is standalone via `/product-decision-run` (not embedded in `/compliance-run`). Set `policyMode: lenient` or `strict` for legacy behavior.

## Agent definitions (dual-track)

| Runtime | Agent definitions |
|---------|-------------------|
| Claude Code | `.claude/agents/compliance/*.md` |
| OpenCode | `.opencode/agents/*.md` |

When changing orchestration prompts, update both locations or generate from a single source later.
