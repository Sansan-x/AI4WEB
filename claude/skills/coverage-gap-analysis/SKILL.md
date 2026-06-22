---
name: coverage-gap-analysis
description: Identifies coverage gaps between risk points, middleware mappings, and key baselines (SQLI/CMDI/FILE). Use for coverage-gap subagent.
---

# Coverage Gap Analysis

## Inputs

- `05-risk-points.json`
- `06-mappings.json`
- Middleware cases JSON (from manifest)
- `compliance/taxonomy/policy-gate.yaml` → `keyBaselines`, `policyMode`, `informationalGapTypes`
- Per-service `02-applicability/*.json`

## Output

`.claude/runs/{runId}/07-gaps.json` — schema `gaps`

## Gap types

| gapType | When | Policy impact (lenient) |
|---------|------|-------------------------|
| NoCaseMatched | Applicable domain has open risk but no middleware case in same domain | **Block** |
| CaseFailed | Case result FAIL/ERROR with open risk | Informational only |
| CaseNotEffective | ERROR/SKIP without remediation | Informational only |
| BaselineNotApplicable | Document only in explanation, not as gap | None |

## Service targeting semantics

- Treat `targetService="*"` middleware cases as valid domain matches for every service.
- Service-specific matches take precedence over wildcard matches when both exist for binding notes.
- Do not emit `NoCaseMatched` for an applicable open risk if any same-domain case exists (`targetService` service or `*`).
- If a wildcard-matched case is FAIL/ERROR/SKIP, emit `CaseFailed` or `CaseNotEffective` for audit but do not treat as Block trigger in lenient phase.

Do not report gaps for excluded ruleTypes/domains (e.g. CMDI when service has no command surface).

## Lenient vs strict

- **lenient** (`policyMode: lenient`): only `NoCaseMatched` affects policy-decision Block; `CaseFailed`/`CaseNotEffective` are informational (`informationalGapTypes`).
- **strict** (`policyMode: strict`): `CaseFailed`/`CaseNotEffective`/`NoCaseMatched` participate in strict gate rules per policy-gate-decision skill.

## Suggestions

Each gap must include actionable `suggestion` for developers or QA.
