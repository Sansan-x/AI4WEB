---
name: baseline-applicability
description: Determines which security baseline items apply to a Java microservice using ServiceContext and baseline-catalog.yaml. Use for baseline-applicability subagent.
---

# Baseline Applicability

## Inputs

- `.claude/runs/{runId}/01-context/{service}.json`
- `manifest.json` → `publicBaselinePath` (default: `compliance/examples/public_baseline.template.json`)
- `compliance/taxonomy/baseline-catalog.yaml` (14 ruleTypes aligned with `categoryCatalog`)
- `compliance/taxonomy/risk-taxonomy.yaml` (coverageScope defaults, `ruleTypeToDomain`)

## Output

`.claude/runs/{runId}/02-applicability/{service}.json` — schema `applicability`

Each item must include `baselineId`, `ruleType`, `ruleTypeEn`, `domain`, and either `applicable: true` (in `applicableBaselines`) or appear in `excludedBaselines` with `reason`.

**Completeness**: `applicableBaselines` + `excludedBaselines` must cover all 14 `categoryCatalog` ruleTypes exactly once.

## Applicability rules (by ruleType)

| ruleType | domain | Applicable when |
|----------|--------|-----------------|
| SQL注入 | SQLI | `dataStores` non-empty or SQL/ORM detected |
| 命令注入 | CMDI | `Runtime.exec`, `ProcessBuilder`, or shell invocation likely |
| 文件上传下载 | FILE | file upload/download/unzip in entry points or code |
| 身份管理 | AUTH | HTTP `entryPoints` exist |
| WEB安全 | WEB | HTTP `entryPoints` exist |
| 敏感信息保护 | SECRETS | almost always; mark `productOnly` |
| 安全配置 | SEC_CONFIG | almost always; mark `productOnly` |
| 密码算法安全 | CRYPTO | crypto/TLS/JWT/password handling in code or config |
| D-DoS | DOS | HTTP `entryPoints` exist |
| XSS注入 | XSS | HTML rendering or template output with user input |
| 模板注入 | TEMPLATE_INJ | Freemarker/Thymeleaf/Velocity with user-controlled expressions |
| XML注入 | XML_INJ | XML parsing (DOM4J, JAXB, etc.) of user input |
| CSV注入 | CSV_INJ | CSV export endpoints |
| SUDO提权 | PRIV_ESC | shell/sudo/container privilege patterns |

For **non-applicable** ruleTypes, add to `excludedBaselines` with clear `reason`. Do **not** create risk points for excluded domains later.

## Hints from catalog

Use `applicabilityHints` in baseline-catalog.yaml:

- `requiresDataStore`, `requiresCommandExecution`, `requiresFileIO`, `requiresHttpEntry`
- `requiresTemplateEngine`, `requiresXmlParsing`, `requiresCsvExport`, `requiresCryptoUsage`, `requiresShellOrSudo`
- `alwaysApplicable`

## Validate

```bash
python3 compliance/scripts/validate_artifact.py --schema applicability \
  --file .claude/runs/{runId}/02-applicability/{service}.json --project-root .
```
