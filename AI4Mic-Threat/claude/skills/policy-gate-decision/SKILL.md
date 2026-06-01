---
name: policy-gate-decision
description: Applies policy-gate.yaml rules to produce Pass, ConditionalPass, or Block compliance decision. Use for policy-decision subagent.
---

# Policy Gate Decision

## Inputs

- `05-risk-points.json`
- `06-mappings.json`
- `07-gaps.json`
- Optional waivers JSON (`riskId`, `owner`, `reason`, `expiresAt`, `mitigationPlan`)
- `compliance/taxonomy/policy-gate.yaml`

## Output

`.claude/runs/{runId}/08-decision.json` — schema `decision`

## Decision logic (priority order)

1. **Block** if any open P0/P1 has mapping `coverageState` in Gap or Partial.
2. **Block** if middleware case for key baseline (SQLI/CMDI/FILE) is FAIL/ERROR and domain is applicable to a service with open risk.
3. **ConditionalPass** if valid waiver covers all blocking risks (not expired).
4. **Pass** otherwise.

Include `policyVersion` from policy-gate.yaml.

## Waivers

Reject expired waivers when `denyExpired: true`.
