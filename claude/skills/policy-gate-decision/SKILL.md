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
- `compliance/taxonomy/risk-taxonomy.yaml` → `ruleTypeToDomain`, `baselineToDomainRules`

## Output

- `.claude/runs/{runId}/08-decisions/{service}.json` — schema `service-decision` (primary, per service)
- `.claude/runs/{runId}/08-decision.json` — schema `decision` (run-level worst-of summary)

## Pipeline integration

**`/compliance-run` does not spawn the `policy-decision` agent.** The coordinator runs the script below directly (Phase 8). Use the `policy-decision` agent only for manual debugging or when `policyMode` is `lenient`/`strict`.

## Preferred execution (weighted v1.3)

Run the deterministic script for each service in manifest:

```bash
python3 compliance/scripts/compute_service_decision.py \
  --run-id {runId} \
  --project-root .
```

Then validate:

```bash
python3 compliance/scripts/validate_artifact.py --schema service-decision \
  --file .claude/runs/{runId}/08-decisions/{service}.json
python3 compliance/scripts/validate_artifact.py --schema decision \
  --file .claude/runs/{runId}/08-decision.json
```

The script updates `04-profiles/{service}.json` → `readyForSubmission` from the per-service decision.

## Submission semantics

- `Pass` and `ConditionalPass` are **submission-compliant** (送检即合规) per `submissionCompliant` in policy-gate.yaml.
- `readyForSubmission` on each service profile comes from **that service's** `08-decisions/{service}.json`.

## domainMatched (all modes)

For each **Open** risk in `05-risk-points.json`:

1. Skip if risk domain is in `02-applicability` `excludedBaselines` (match by `domain`).
2. `domainMatched = false` if `07-gaps` contains `NoCaseMatched` for the risk.
3. Otherwise `domainMatched = true` if `06-mappings` has an entry with `[domain_matched]` in `explanation` (ignore FAIL/ERROR for match purposes).

## Decision logic — `policyMode: weighted` (default v1.3)

Severity tiers from `severityTiers` in policy-gate.yaml:

| Tier | Rule |
|------|------|
| **mandatory** | P0, or P1 where `category` ∈ `keyBaselines` (SQLI, CMDI, FILE) |
| **ratioEligible** | Other P1, P2, P3 |

Algorithm (per service):

1. No applicable Open risks → **Pass** (`no_open_risks`).
2. Any mandatory-tier risk with `domainMatched = false` → **Block** (`mandatory_coverage_gap`).
3. Compute `ratioEligibleCoverageRate` over ratio-eligible Open risks.
4. Rate ≥ `coverageRatio.minConditionalPass` (0.70) → **ConditionalPass** (`optional_coverage_ratio_met`).
5. Rate ≥ `coverageRatio.minBlock` (0.50) → **ConditionalPass** (`optional_coverage_ratio_partial`).
6. Else → **Block** (`insufficient_optional_coverage`).
7. If mandatory met and no ratio-eligible risks → **ConditionalPass** (`mandatory_coverage_met`).

Run-level `08-decision.json` = worst-of all service decisions + `serviceSummaries`.

## Decision logic — `policyMode: lenient` (v1.2)

1. If no Open risks (or all excluded) → **Pass**.
2. **Block** if any applicable Open risk has `domainMatched = false`.
   - Reason: `risk_domain_without_matching_case`
3. **ConditionalPass** if all applicable Open risks have `domainMatched = true`.
   - Reason: `domain_matched_lenient_phase`
4. Do **not** Block based on `CaseFailed` / `CaseNotEffective` (informational only).

## Decision logic — `policyMode: strict` (v1.1)

Apply `strictRules` from policy-gate.yaml in order:

1. Determine `partialKind` for Partial mappings (Hard vs Soft).
2. **Block** on Gap, Hard Partial, or key baseline FAIL/ERROR with related open risk.
3. **ConditionalPass** for Soft partial only or valid waiver.
4. **Pass** otherwise.

## Waivers

- Lenient / weighted phase: waivers optional (`requiredForConditionalPass: false`).
- Strict phase: reject expired waivers when `denyExpired: true`; enforce `maxValidityDays` when set.

Include `policyVersion` and reflect active `policyMode` in output.
