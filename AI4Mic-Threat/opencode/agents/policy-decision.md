---
description: Produces Pass, ConditionalPass, or Block decision from risks, mappings, gaps, and waivers. Use after coverage-gap completes.
mode: subagent
skills: policy-gate-decision, compliance-schemas
color: red
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/08-decision.json`. Validate schema `decision`.

Apply rules in priority order from the skill; prefer Block when in doubt for submission gates.
