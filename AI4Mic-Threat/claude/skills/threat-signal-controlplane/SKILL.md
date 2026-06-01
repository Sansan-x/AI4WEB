---
name: threat-signal-controlplane
description: Detects service-level control-plane threats (authz gaps, secrets in config/logs, vulnerable deps) in Java microservices. Use for controlplane-signal subagent.
---

# Threat Signal — Controlplane

## Output

`.claude/runs/{runId}/03-signals/{service}/controlplane.json`

Schema: `threat-signal` with `signalType: controlplane`

## Domains

AUTH, SECRETS, DEPENDENCY, CMDI (when applicable).

## Patterns

| Domain | Patterns |
|--------|----------|
| AUTH | sensitive operations without `@PreAuthorize` / role checks |
| SECRETS | plaintext passwords in yml, tokens in log statements |
| DEPENDENCY | known-vulnerable coords in pom (flag likely, no CVE dump) |
| CMDI | `Runtime.exec`, `ProcessBuilder` with external input |

Mark CMDI `not_applicable` when service has no command surface.
