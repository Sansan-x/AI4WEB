---
description: Synthesizes ServiceRiskProfile and RiskPoints from threat signals for one Java microservice. Use after all three signal files exist for the service.
mode: subagent
skills: risk-point-synthesize, compliance-schemas
color: orange
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

Inputs: `02-applicability/{service}.json` and all files under `03-signals/{service}/`.

Write `.claude/runs/{runId}/04-profiles/{service}.json`. Validate schema `service-risk-profile`.

Merge multiple signals per domain into one RiskPoint. Skip excluded domains entirely.
