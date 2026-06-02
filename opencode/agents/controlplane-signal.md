---
description: Scans Java service for control-plane threat signals (authz, secrets, dependencies, CMDI). Use in parallel with exposure and dataflow signal agents.
mode: subagent
color: yellow
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

- `skill({ name: "threat-signal-controlplane" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `02-applicability/{service}.json` before scanning.

Write `.claude/runs/{runId}/03-signals/{service}/controlplane.json` with `signalType: controlplane`. Validate schema `threat-signal`.

Max 3 anchors per signal. Service-level summaries only.
