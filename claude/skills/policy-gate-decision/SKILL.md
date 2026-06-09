---
name: policy-gate-decision
description: Applies policy-gate.yaml rules to produce Pass, ConditionalPass, or Block compliance decision. Use for policy-decision subagent.
---

# Policy Gate Decision

## Inputs

- `05-risk-points.json`
- `06-mappings.json`
- `07-gaps.json`
- Middleware cases JSON (from manifest `middlewareCasesPath`)
- Per-service `02-applicability/*.json`
- Optional waivers JSON (`riskId`, `owner`, `reason`, `expiresAt`, `mitigationPlan`)
- `compliance/taxonomy/policy-gate.yaml`
- `compliance/taxonomy/risk-taxonomy.yaml` → `baselineToDomainRules`

## Output

`.claude/runs/{runId}/08-decision.json` — schema `decision`

## Submission semantics

- `Pass` and `ConditionalPass` are **submission-compliant** (送检即合规) per `submissionCompliant` in policy-gate.yaml.
- Downstream profiles should set `readyForSubmission: true` when decision is Pass or ConditionalPass.

## domainMatched (lenient phase)

For each **Open** risk in `05-risk-points.json`:

1. Skip if risk domain is in `02-applicability` `excludedBaselines`.
2. Let `domain = risk.category`.
3. Search middleware cases where `mapBaselineToDomain(baselineType) == domain` and `targetService` is `risk.service` or `*`.
4. `domainMatched = true` if at least one case exists (**ignore** `result` PASS/FAIL/SKIP/ERROR).

## Decision logic — `policyMode: lenient` (default v1.2)

1. If no Open risks (or all excluded) → **Pass**.
2. **Block** if any applicable Open risk has `domainMatched = false` (equivalent to `NoCaseMatched` in gaps).
   - Reason: `risk_domain_without_matching_case`
3. **ConditionalPass** if all applicable Open risks have `domainMatched = true`.
   - Reason: `domain_matched_lenient_phase`
4. Do **not** Block based on:
   - `coverageState` Partial/Gap from mappings alone
   - `07-gaps` with `CaseFailed` / `CaseNotEffective` (informational only in lenient phase)
   - Middleware `FAIL` / `ERROR` when domain still has matching cases

## Decision logic — `policyMode: strict` (v1.1)

Apply `strictRules` from policy-gate.yaml in order:

1. Determine `partialKind` for Partial mappings (Hard vs Soft).
2. **Block** on Gap, Hard Partial, or key baseline FAIL/ERROR with related open risk.
3. **ConditionalPass** for Soft partial only or valid waiver.
4. **Pass** otherwise.

## Waivers

- Lenient phase: waivers optional (`requiredForConditionalPass: false`).
- Strict phase: reject expired waivers when `denyExpired: true`; enforce `maxValidityDays` when set.

Include `policyVersion` and reflect active `policyMode` in reasons when useful.
