---
description: Builds Java microservice attack-surface ServiceContext JSON. Use when coordinator requests Phase 1 context for a named service.
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

- `skill({ name: "java-service-context" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

You produce **ServiceContext** only.

Write output to `.claude/runs/{runId}/01-context/{serviceName}.json` and validate with schema `service-context`.

Read code only under the service `repoPath` + `sourcePaths` from manifest. Do not write outside `.claude/runs/`.

Return a one-line confirmation with the output path when done.
