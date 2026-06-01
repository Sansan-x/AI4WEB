---
name: threat-signal-dataflow
description: Detects service-level dataflow threats (SQLi, SSRF, deserialization, file path) in Java code. Use for dataflow-signal subagent.
---

# Threat Signal — Dataflow

## Output

`.claude/runs/{runId}/03-signals/{service}/dataflow.json`

Schema: `threat-signal` with `signalType: dataflow`

## Applicable domains

SQLI, FILE, SSRF — only if applicable in `02-applicability`.

## Patterns

| Domain | Patterns |
|--------|----------|
| SQLI | SQL string `+`, MyBatis `${}`, raw `Statement` |
| FILE | user input in `Paths.get`, `../`, unsafe zip |
| SSRF | user-controlled URL in HTTP clients |

Use `strength: absent` when applicable domain has no concerning patterns.

## Limits

- Service-level summaries only
- Max 3 anchors per signal
