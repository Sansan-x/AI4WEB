---
name: policy-decision
description: Produces Pass, ConditionalPass, or Block decision from risks, mappings, gaps, and waivers. Use after coverage-gap completes.
tools: Read, Write, Bash
skills: policy-gate-decision, compliance-schemas
model: haiku
color: red
---

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/08-decision.json`. Validate schema `decision`.

Apply rules in priority order from the skill; prefer Block when in doubt for submission gates.
