---
description: Assembles audit evidence package with agentRunTrace for compliance submission. Use after policy-decision completes.
mode: subagent
skills: evidence-pack-generate, compliance-schemas
color: cyan
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

Collect all artifacts under `.claude/runs/{runId}/` and middleware cases.

Write `.claude/runs/{runId}/09-evidence/index.json`. Validate schema `evidence-package`.

Include SHA256 hashes in `agentRunTrace` for each major artifact.
