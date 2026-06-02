---
description: Reports coverage gaps between risks, mappings, and key baselines SQLI/CMDI/FILE. Use after case-mapping completes.
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

- `skill({ name: "coverage-gap-analysis" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `05-risk-points.json`, `06-mappings.json`, `02-applicability/*.json`, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/07-gaps.json`. Validate schema `gaps`.
