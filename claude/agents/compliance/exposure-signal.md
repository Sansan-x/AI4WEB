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

Max 3 anchors per signal. Service-level summaries only.
