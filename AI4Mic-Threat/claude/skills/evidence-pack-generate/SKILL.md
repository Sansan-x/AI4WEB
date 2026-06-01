---
name: evidence-pack-generate
description: Assembles compliance evidence package with agentRunTrace for audit submission. Use for evidence-pack subagent.
---

# Evidence Pack Generate

## Inputs

All artifacts under `.claude/runs/{runId}/`:
manifest, 00–08, middleware cases, optional waivers

## Output

`.claude/runs/{runId}/09-evidence/index.json` — schema `evidence-package`

## agentRunTrace entries

For each pipeline step, include:

```json
{
  "runId": "...",
  "agentType": "service-context",
  "inputHash": "<sha256 of inputs or manifest>",
  "outputHash": "<sha256 of output file>",
  "artifactPath": ".claude/runs/{runId}/01-context/order-service.json",
  "latencyMs": 0,
  "retryCount": 0
}
```

Compute hashes via: `shasum -a 256 <file>` or Python.

## index.json fields

- `version`, `releaseId` (= runId), `generatedAt` (ISO8601 UTC)
- `policyVersion`, `taxonomyVersion` from manifest
- `decision`, `riskPoints`, `middlewareCases`, `mappings`, `gaps`, `agentRunTrace`

Copy or reference artifact paths in `09-evidence/artifacts/` if useful for auditors.
