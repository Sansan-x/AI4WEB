---
description: Produces Pass, ConditionalPass, or Block decision from risks, mappings, gaps, and waivers. Use after coverage-gap completes.
mode: subagent
color: red
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "policy-gate-decision" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/08-decision.json`. Validate schema `decision`.

Apply rules in priority order from the skill; prefer Block when in doubt for submission gates.
