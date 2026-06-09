---
name: risk-point-synthesize
description: Synthesizes ServiceRiskProfile and RiskPoint list from threat signals and applicability. Use for risk-synthesizer subagent.
---

# Risk Point Synthesize

## Inputs

- `02-applicability/{service}.json`
- `03-signals/{service}/exposure.json`, `dataflow.json`, `controlplane.json`
- `compliance/taxonomy/risk-taxonomy.yaml` (default severities)
- Optional: `08-decision.json` when synthesizing after policy gate in same run

## Output

`.claude/runs/{runId}/04-profiles/{service}.json` — schema `service-risk-profile`

## Rules

1. Merge signals with `strength` in `confirmed`, `likely` per domain into **one RiskPoint per domain**.
2. Skip domains in `excludedBaselines` (match by `domain` or `ruleType`) or `not_applicable` signals.
3. Set `severity` from taxonomy defaults (SQLI/CMDI/FILE/AUTH → P1 unless justified).
4. `riskPointIds` must match embedded `riskPoints[].riskId`.
5. `overallExposure`: low | medium | high | critical based on highest open severity.
6. `readyForSubmission`:
   - Prefer `08-decisions/{service}.json`: `true` when `decision` is `Pass` or `ConditionalPass`.
   - Fallback to run-level `08-decision.json` if per-service file absent.
   - If decision not yet available (profile written before policy gate): default `false`.

## RiskPoint shape

```json
{
  "riskId": "R-SQL-001",
  "service": "order-service",
  "category": "SQLI",
  "severity": "P1",
  "status": "Open",
  "codeEvidence": ["OrderDao.java:8"],
  "serviceLevelSummary": "..."
}
```

Max 3 `codeEvidence` entries.
