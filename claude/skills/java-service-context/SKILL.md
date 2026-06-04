---
name: java-service-context
description: Builds Java microservice attack-surface ServiceContext JSON from Spring/MyBatis/Maven layouts. Use for service-context subagent or Phase 1 context extraction.
---

# Java Service Context

## Output

Write **only** to: `.claude/runs/{runId}/01-context/{serviceName}.json`

Schema: `compliance/schemas/service-context.schema.json`

## Steps

1. Resolve service root under `repoPath` (Maven module or monorepo subfolder).
2. Inspect `pom.xml` / `build.gradle`, `*Application.java`, `application.yml|properties`.
3. List REST entry points: `@RestController`, `@RequestMapping`, `@GetMapping`, etc.
4. List data stores: JDBC, JPA, MyBatis, Redis mentions in config.
5. List outbound: `@FeignClient`, `RestTemplate`, `WebClient`, message queues.
6. Note sensitive assets at service level (PII, payment, credentials)—no secret values.

## Example output

See `assets/service-context.example.json`.

## Do not

- Enumerate every file or class
- Output vulnerability findings (that is signal agents)
