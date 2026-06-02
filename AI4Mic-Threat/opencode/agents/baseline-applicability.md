---
description: Determines applicable security baselines per Java microservice from ServiceContext. Use after service-context completes for a service.
mode: subagent
skills: baseline-applicability, compliance-schemas
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

Read `01-context/{service}.json` and `compliance/taxonomy/baseline-catalog.yaml`.

Write `.claude/runs/{runId}/02-applicability/{service}.json`. Validate with schema `applicability`.

Excluded baselines must include `reason`. Do not mark CMDI/FILE applicable without surface evidence.
