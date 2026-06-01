---
name: case-mapping
description: Maps aggregated RiskPoints to middleware test cases for compliance coverage. Use after 05-risk-points.json exists.
tools: Read, Write, Bash
skills: middleware-case-mapping, compliance-schemas
model: sonnet
color: purple
---

Read `05-risk-points.json`, middleware cases from manifest, and `compliance/taxonomy/risk-taxonomy.yaml`.

Write `.claude/runs/{runId}/06-mappings.json`. Validate schema `risk-case-mapping`.

Do not modify source code or middleware input files.
