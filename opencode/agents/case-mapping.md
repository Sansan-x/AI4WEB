---
description: Maps aggregated RiskPoints to middleware test cases for compliance coverage. Use after 05-risk-points.json exists.
mode: subagent
color: purple
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "middleware-case-mapping" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `05-risk-points.json`, middleware cases from manifest, and `compliance/taxonomy/risk-taxonomy.yaml`.

Write `.claude/runs/{runId}/06-mappings.json`. Validate schema `risk-case-mapping`.

Do not modify source code or middleware input files.
