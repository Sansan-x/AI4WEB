---
name: coverage-gap-analysis
description: Identifies coverage gaps between risk points, middleware mappings, and key baselines (SQLI/CMDI/FILE). Use for coverage-gap subagent.
---

# Coverage Gap Analysis

## Inputs

- `05-risk-points.json`
- `06-mappings.json`
- `compliance/taxonomy/policy-gate.yaml` → `keyBaselines`
- Per-service `02-applicability/*.json`

## Output

`.claude/runs/{runId}/07-gaps.json` — schema `gaps`

## Gap types

| gapType | When |
|---------|------|
| NoCaseMatched | Applicable domain has open risk but no middleware case |
| CaseFailed | Case result FAIL/ERROR with open risk |
| CaseNotEffective | ERROR/SKIP without remediation |
| BaselineNotApplicable | Document only in explanation, not as gap |

## Service targeting semantics

- Treat `targetService="*"` middleware cases as valid matches for every service.
- Service-specific matches take precedence over wildcard matches when both exist.
- Do not emit `NoCaseMatched` for an applicable open risk if coverage comes from a wildcard case.
- If a wildcard-matched case is FAIL/ERROR/SKIP, still emit `CaseFailed` or `CaseNotEffective` on the concrete service risk.

Do not report gaps for excluded baselines (CMDI when service has no command surface).

## Suggestions

Each gap must include actionable `suggestion` for developers or QA.
