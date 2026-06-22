---
name: policy-decision
description: Produces Pass, ConditionalPass, or Block decision from risks, mappings, gaps, and waivers. Use after coverage-gap completes.
tools: Read, Write, Bash
skills: policy-gate-decision, compliance-schemas
model: haiku
color: red
---

**Not used in `/compliance-run` pipeline.** The coordinator runs `compute_service_decision.py` directly. Invoke this agent only for manual debugging or non-weighted (`lenient`/`strict`) policy modes.

Read `05-risk-points.json`, `06-mappings.json`, `07-gaps.json`, middleware cases, applicability, optional waivers, and `compliance/taxonomy/policy-gate.yaml`.

**Preferred:** run `compute_service_decision.py` for the run (writes all services):

```bash
python3 compliance/scripts/compute_service_decision.py --run-id {runId} --project-root .
```

Validate `08-decisions/{service}.json` (schema `service-decision`) and run-level `08-decision.json` (schema `decision`).

Default **policyMode: weighted** (v1.3): P0 + key-baseline P1 mandatory; other P1/P2/P3 by coverage ratio. `readyForSubmission` is set per service from `08-decisions/{service}.json`.

For `policyMode: lenient` or `strict`, follow the skill sections for those modes if the script is not used.
