---
name: threat-signal-exposure
description: Detects service-level exposure threats (identity, web security, DoS) for Java microservices. Use for exposure-signal subagent.
---

# Threat Signal — Exposure

## Output

`.claude/runs/{runId}/03-signals/{service}/exposure.json`

Schema: `threat-signal` with `signalType: exposure`

## Applicable domains (from `02-applicability`)

Only scan domains whose ruleType is in `applicableBaselines`:

| ruleType | domain |
|----------|--------|
| 身份管理 | AUTH |
| WEB安全 | WEB |
| D-DoS | DOS |

For excluded ruleTypes, emit `strength: not_applicable` for the bridged domain.

## Patterns (Grep, read-only)

| Domain | Patterns |
|--------|----------|
| AUTH | missing auth on `@RestController` methods, hardcoded credentials |
| WEB | `springdoc`/`swagger` public without security, CSRF disabled, missing security headers |
| DOS | unbounded queries, missing pagination, ReDoS-prone regex, no rate limiting |

Also check:
- `management.endpoints.web.exposure.include: '*'` or Actuator without auth
- Permissive CORS `allowedOrigins: "*"`

## Signal fields

- `strength`: confirmed | likely | absent | not_applicable
- `serviceLevelSummary`: one sentence for compliance reviewers
- `anchors`: max 3 `file:line` references

## Scan budget

Follow `compliance-orchestrator` § Scan budget (Phase 3). Summary:

- Scope: `sourcePaths` from `00-service-slices.json` + `src/main/resources/application*.yml|properties` only
- Applicability-first: excluded domains → `not_applicable` without opening code
- Grep-before-Read; max **12** file reads; stop each domain after `confirmed`/`likely`
- No hits → `absent` with `anchors: []`
- Never enumerate all classes or produce CWE dumps
