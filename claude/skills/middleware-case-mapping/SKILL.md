---
name: middleware-case-mapping
description: Maps RiskPoints to middleware test cases using risk-taxonomy baseline rules. Use for case-mapping subagent.
---

# Middleware Case Mapping

## Inputs

- `.claude/runs/{runId}/05-risk-points.json`
- Middleware cases JSON (from manifest `middlewareCasesPath`)
- `compliance/taxonomy/risk-taxonomy.yaml` → `ruleTypeToDomain`, `baselineToDomainRules`
- `compliance/taxonomy/policy-gate.yaml` → `policyMode`

## Output

`.claude/runs/{runId}/06-mappings.json` — schema `risk-case-mapping`

## Algorithm

1. Map each middleware `baselineType` to domain via `mapToDomain()`:
   - First check exact match in `ruleTypeToDomain` (for ruleType-style baselineType values).
   - Then apply `baselineToDomainRules` substring matching on lowercase `baselineType`.
2. For each RiskPoint, find cases with matching domain using service targeting priority:
   - First match cases where `targetService == <risk.service>`.
   - If no service-specific match exists, fallback to `targetService == "*"`.
   - If `targetService` is omitted, treat as non-targeted and allow as generic fallback after the two rules above.
   - When both service-specific and wildcard cases exist for the same domain, prefer the service-specific case for `caseId` binding.
3. Set `coverageState` (schema enum unchanged):
   - Domain matched + open risk → `Covered` in lenient phase when any same-domain case exists; may use `Partial` for audit notes only.
   - PASS + no risk → `Covered`
   - No matching case → do not invent; coverage-gap agent handles `NoCaseMatched`
4. Set `coverageScope` from taxonomy `defaultCoverageScope` for domain.
5. Add `explanation` with machine-readable markers:
   - `[domain_matched]` when risk.category matches mapped case domain (required for lenient gate).
   - Optional audit markers: `partial:depth_insufficient`, `partial:cross_service_missing`, `partial:case_failed` (do not imply Block in lenient phase).

## Lenient phase (policyMode: lenient)

- If ≥1 middleware case shares domain with the risk, emit mapping with `[domain_matched]`.
- Do **not** downgrade to non-match because case `result` is FAIL/ERROR.
- Service-level FAIL with wildcard PASS still counts as domain matched (bind preferred case, note FAIL in explanation if needed).

## Strict phase (policyMode: strict)

- Use Partial/Covered semantics from v1.1: PASS+open→Partial, FAIL+open→Partial with `partial:case_failed`.

## mappingExplanation

Summarize excluded ruleTypes/domains and unmatched domains in string array.
When wildcard (`targetService="*"`) matches are used, include audit-friendly notes (for example: wildcard case IDs/domains used as fallback coverage).
