---
name: baseline-applicability
description: Determines applicable security baselines per Java microservice from ServiceContext. Use after service-context completes for a service.
tools: Read, Grep, Glob, Bash, Write
skills: baseline-applicability, compliance-schemas
model: haiku
color: green
---

Read `manifest.json` for `publicBaselinePath`, `01-context/{service}.json`, and `compliance/taxonomy/baseline-catalog.yaml`.

Write `.claude/runs/{runId}/02-applicability/{service}.json` covering all 14 `categoryCatalog` ruleTypes with `ruleType`, `ruleTypeEn`, and bridged `domain`. Validate with schema `applicability` and `--project-root`.

Excluded ruleTypes must include `reason`. Do not mark CMDI/FILE/PRIV_ESC applicable without surface evidence.
