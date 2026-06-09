---
name: baseline-applicability
description: Determines which security baseline items apply to a Java microservice using ServiceContext and baseline-catalog.yaml. Use for baseline-applicability subagent.
---

# Baseline Applicability

## Inputs

- `.claude/runs/{runId}/01-context/{service}.json`
- `compliance/taxonomy/baseline-catalog.yaml`
- `compliance/taxonomy/risk-taxonomy.yaml` (coverageScope defaults)

## Output

`.claude/runs/{runId}/02-applicability/{service}.json` — schema `applicability`

## Rules

| Baseline domain | Applicable when |
|-----------------|-----------------|
| SQLI | `dataStores` non-empty or SQL/ORM detected |
| CMDI | command execution patterns likely in service scope |
| FILE | file upload/download/unzip in entry points or code hints |
| AUTH | HTTP `entryPoints` exist |
| SECRETS / DEPENDENCY | usually applicable; mark `productOnly` scope |

For **non-applicable** baselines, add to `excludedBaselines` with clear `reason`. Do **not** create risk points for excluded domains later.

## Hints from catalog

Use `applicabilityHints` in baseline-catalog.yaml (`requiresDataStore`, `requiresCommandExecution`, `requiresFileIO`, `requiresHttpEntry`, `alwaysApplicable`).
