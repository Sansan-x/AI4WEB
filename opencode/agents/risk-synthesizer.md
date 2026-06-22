---
description: Synthesizes ServiceRiskProfile and RiskPoints from threat signals for one Java microservice. Use after all three signal files exist for the service.
mode: subagent
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "risk-point-synthesize" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Inputs: `02-applicability/{service}.json` and all files under `03-signals/{service}/`.

Write `.claude/runs/{runId}/04-profiles/{service}.json`. Validate schema `service-risk-profile`.

Do not read the Java repo. Synthesize only from `02-applicability` + `03-signals` JSON. Merge multiple signals per domain into one RiskPoint. Skip excluded ruleTypes/domains entirely. Set `readyForSubmission: false`.
