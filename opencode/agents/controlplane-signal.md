---
description: Scans Java service for control-plane threat signals (secrets, security config, crypto, CMDI, privilege escalation). Use in parallel with exposure and dataflow signal agents.
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

- `skill({ name: "threat-signal-controlplane" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `02-applicability/{service}.json` before scanning.

Write `.claude/runs/{runId}/03-signals/{service}/controlplane.json` with `signalType: controlplane`. Validate schema `threat-signal`.

Scan budget: Grep-first; max 12 file reads; excluded domains → `not_applicable` without code access; one `confirmed`/`likely` per domain then stop; never enumerate all classes.
