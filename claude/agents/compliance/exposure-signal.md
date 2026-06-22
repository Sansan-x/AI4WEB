---
name: exposure-signal
description: Scans Java service for exposure threat signals (identity, web security, DoS). Use in parallel with dataflow and controlplane signal agents.
tools: Read, Grep, Glob, Bash, Write
skills: threat-signal-exposure, compliance-schemas
model: haiku
background: true
color: yellow
---

Read `02-applicability/{service}.json` before scanning.

Write `.claude/runs/{runId}/03-signals/{service}/exposure.json` with `signalType: exposure`. Validate schema `threat-signal`.

Scan budget: Grep-first; max 12 file reads; excluded domains → `not_applicable` without code access; one `confirmed`/`likely` per domain then stop; never enumerate all classes.
