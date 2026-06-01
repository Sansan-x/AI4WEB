---
name: middleware-case-mapping
description: Maps RiskPoints to middleware test cases using risk-taxonomy baseline rules. Use for case-mapping subagent.
---

# Middleware Case Mapping

## Inputs

- `.claude/runs/{runId}/05-risk-points.json`
- Middleware cases JSON (from manifest `middlewareCasesPath`)
- `compliance/taxonomy/risk-taxonomy.yaml` → `baselineToDomainRules`

## Output

`.claude/runs/{runId}/06-mappings.json` — schema `risk-case-mapping`

## Algorithm

1. Map each middleware `baselineType` to domain (SQLI, CMDI, FILE, …) via rules.
2. For each RiskPoint, find cases with matching domain using service targeting priority:
   - First match cases where `targetService == <risk.service>`.
   - If no service-specific match exists, fallback to `targetService == "*"`.
   - If `targetService` is omitted, treat as non-targeted and allow as generic fallback after the two rules above.
   - When both service-specific and wildcard cases exist for the same domain, use the service-specific case.
3. Set `coverageState`:
   - PASS + open risk → `Partial`
   - PASS + no risk → `Covered`
   - FAIL + open risk → `Partial`
   - No matching case → do not invent; coverage-gap agent handles
4. Set `coverageScope` from taxonomy `defaultCoverageScope` for domain.
5. Add human-readable `explanation` per mapping.

## mappingExplanation

Summarize excluded baselines and unmatched domains in string array.
When wildcard (`targetService="*"`) matches are used, include audit-friendly notes (for example: wildcard case IDs/domains used as fallback coverage).
