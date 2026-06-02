---
description: Maps aggregated RiskPoints to middleware test cases for compliance coverage. Use after 05-risk-points.json exists.
mode: subagent
skills: middleware-case-mapping, compliance-schemas
color: purple
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

Read `05-risk-points.json`, middleware cases from manifest, and `compliance/taxonomy/risk-taxonomy.yaml`.

Write `.claude/runs/{runId}/06-mappings.json`. Validate schema `risk-case-mapping`.

Do not modify source code or middleware input files.
