---
name: threat-signal-dataflow
description: Detects service-level dataflow threats (SQLi, file path, XSS, XML, CSV, template injection) in Java code. Use for dataflow-signal subagent.
---

# Threat Signal — Dataflow

## Output

`.claude/runs/{runId}/03-signals/{service}/dataflow.json`

Schema: `threat-signal` with `signalType: dataflow`

## Applicable domains (from `02-applicability`)

Only scan domains whose ruleType is in `applicableBaselines`. Map ruleType → domain via `risk-taxonomy.yaml` `ruleTypeToDomain`:

| ruleType | domain |
|----------|--------|
| SQL注入 | SQLI |
| 文件上传下载 | FILE |
| XSS注入 | XSS |
| XML注入 | XML_INJ |
| CSV注入 | CSV_INJ |
| 模板注入 | TEMPLATE_INJ |

For excluded ruleTypes, emit `strength: not_applicable` for the bridged domain.

## Patterns

| Domain | Patterns |
|--------|----------|
| SQLI | SQL string `+`, MyBatis `${}`, raw `Statement` |
| FILE | user input in `Paths.get`, `../`, unsafe zip |
| XSS | unescaped HTML output, `@ResponseBody` returning user input in HTML context |
| XML_INJ | XXE, unsafe `DocumentBuilder`, external entity resolution |
| CSV_INJ | formula injection in CSV export (`=`, `+`, `-`, `@` prefixes) |
| TEMPLATE_INJ | user input in Freemarker/Thymeleaf `${}` or SpEL expressions |

Use `strength: absent` when applicable domain has no concerning patterns.

## Limits

- Service-level summaries only
- Max 3 anchors per signal

## Scan budget

Follow `compliance-orchestrator` § Scan budget (Phase 3). Summary:

- Scope: `sourcePaths` from `00-service-slices.json` + `src/main/resources/application*.yml|properties` only
- Applicability-first: excluded domains → `not_applicable` without opening code
- Grep-before-Read; max **12** file reads; stop each domain after `confirmed`/`likely`
- No hits → `absent` with `anchors: []`
- Never enumerate all classes or produce CWE dumps
