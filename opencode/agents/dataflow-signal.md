---
description: Scans Java service for dataflow threat signals (SQLi, file path, SSRF). Use in parallel with exposure and controlplane signal agents.
mode: subagent
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "threat-signal-dataflow" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `02-applicability/{service}.json` before scanning.

Write `.claude/runs/{runId}/03-signals/{service}/dataflow.json` with `signalType: dataflow`. Validate schema `threat-signal`.

Max 3 anchors per signal. Service-level summaries only.
