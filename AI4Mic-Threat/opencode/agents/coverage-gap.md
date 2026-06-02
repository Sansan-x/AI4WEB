---
description: Reports coverage gaps between risks, mappings, and key baselines SQLI/CMDI/FILE. Use after case-mapping completes.
mode: subagent
skills: coverage-gap-analysis, compliance-schemas
color: purple
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

Read `05-risk-points.json`, `06-mappings.json`, `02-applicability/*.json`, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/07-gaps.json`. Validate schema `gaps`.
