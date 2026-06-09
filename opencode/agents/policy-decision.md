---
description: Produces Pass, ConditionalPass, or Block decision from risks, mappings, gaps, and waivers. Use after coverage-gap completes.
mode: subagent
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "policy-gate-decision" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, middleware cases, applicability, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

Write `.claude/runs/{runId}/08-decision.json`. Validate schema `decision`.

Apply rules from the skill using `policyMode` in policy-gate.yaml (default **lenient**): domain-matched open risks → **ConditionalPass** (submission-compliant); only unmatched domain → **Block**. In lenient phase, ignore informational gaps (`CaseFailed`, `CaseNotEffective`).
