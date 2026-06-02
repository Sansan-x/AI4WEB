---
description: Assembles audit evidence package with agentRunTrace for compliance submission. Use after policy-decision completes.
mode: subagent
color: cyan
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "evidence-pack-generate" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Collect all artifacts under `.claude/runs/{runId}/` and middleware cases.

Write `.claude/runs/{runId}/09-evidence/index.json`. Validate schema `evidence-package`.

Include SHA256 hashes in `agentRunTrace` for each major artifact.
