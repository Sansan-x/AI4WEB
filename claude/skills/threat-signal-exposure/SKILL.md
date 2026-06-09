---
name: threat-signal-exposure
description: Detects service-level exposure threats (anonymous APIs, Actuator, CORS, Swagger) for Java microservices. Use for exposure-signal subagent.
---

# Threat Signal — Exposure

## Output

`.claude/runs/{runId}/03-signals/{service}/exposure.json`

Schema: `threat-signal` with `signalType: exposure`

## Only evaluate domains marked applicable in `02-applicability`

For excluded domains, emit one signal with `strength: not_applicable`.

## Patterns (Grep, read-only)

- Missing auth on `@RestController` methods
- `springdoc`, `swagger` public without security
- `management.endpoints.web.exposure.include: '*'` or Actuator without auth
- Permissive CORS `allowedOrigins: "*"`

## Signal fields

- `strength`: confirmed | likely | absent | not_applicable
- `serviceLevelSummary`: one sentence for compliance reviewers
- `anchors`: max 3 `file:line` references
