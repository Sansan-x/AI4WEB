---
name: threat-signal-controlplane
description: Detects service-level control-plane threats (secrets, security config, crypto, CMDI, privilege escalation) in Java microservices. Use for controlplane-signal subagent.
---

# Threat Signal — Controlplane

## Output

`.claude/runs/{runId}/03-signals/{service}/controlplane.json`

Schema: `threat-signal` with `signalType: controlplane`

## Applicable domains (from `02-applicability`)

Only scan domains whose ruleType is in `applicableBaselines`:

| ruleType | domain |
|----------|--------|
| 敏感信息保护 | SECRETS |
| 安全配置 | SEC_CONFIG |
| 密码算法安全 | CRYPTO |
| 命令注入 | CMDI |
| SUDO提权 | PRIV_ESC |

For excluded ruleTypes, emit `strength: not_applicable` for the bridged domain.

## Patterns

| Domain | Patterns |
|--------|----------|
| SECRETS | plaintext passwords in yml, tokens in log statements |
| SEC_CONFIG | insecure defaults, debug mode enabled, overly permissive CORS in config |
| CRYPTO | weak algorithms (MD5, DES), hardcoded keys, fixed salt |
| CMDI | `Runtime.exec`, `ProcessBuilder` with external input |
| PRIV_ESC | shell invocation, sudo usage, container privilege escalation |

Use `strength: absent` when applicable domain has no concerning patterns.

## Limits

- Service-level summaries only
- Max 3 anchors per signal
