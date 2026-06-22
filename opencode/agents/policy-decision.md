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

**Not used in `/compliance-run` pipeline.** The coordinator runs `compute_service_decision.py` directly. Invoke this agent only for manual debugging or non-weighted (`lenient`/`strict`) policy modes.

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, middleware cases, applicability, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

**Preferred:** run `compute_service_decision.py`:

```bash
python3 compliance/scripts/compute_service_decision.py --run-id {runId} --project-root .
```

Validate `08-decisions/{service}.json` (schema `service-decision`) and `08-decision.json` (schema `decision`).

Default **policyMode: weighted** (v1.3): P0 + key-baseline P1 mandatory; other P1/P2/P3 by coverage ratio.
