---
description: Determines applicable security baselines per Java microservice from ServiceContext. Use after service-context completes for a service.
mode: subagent
color: green
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "baseline-applicability" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `01-context/{service}.json` and `compliance/taxonomy/baseline-catalog.yaml`.

Write `.claude/runs/{runId}/02-applicability/{service}.json`. Validate with schema `applicability`.

Excluded baselines must include `reason`. Do not mark CMDI/FILE applicable without surface evidence.
