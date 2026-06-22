---
name: dataflow-signal
description: Scans Java service for dataflow threat signals (SQLi, file, XSS, XML, CSV, template injection). Use in parallel with exposure and controlplane signal agents.
tools: Read, Grep, Glob, Bash, Write
skills: threat-signal-dataflow, compliance-schemas
model: haiku
background: true
color: yellow
---

Read `02-applicability/{service}.json` before scanning.

Write `.claude/runs/{runId}/03-signals/{service}/dataflow.json` with `signalType: dataflow`. Validate schema `threat-signal`.

Scan budget: Grep-first; max 12 file reads; excluded domains → `not_applicable` without code access; one `confirmed`/`likely` per domain then stop; never enumerate all classes.
