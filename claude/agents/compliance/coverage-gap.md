---
name: coverage-gap
description: Reports coverage gaps between risks, mappings, and key baselines SQLI/CMDI/FILE. Use after case-mapping completes.
tools: Read, Write, Bash
skills: coverage-gap-analysis, compliance-schemas
model: haiku
color: purple
---

Read `05-risk-points.json`, `06-mappings.json`, `02-applicability/*.json`, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/07-gaps.json`. Validate schema `gaps`.
