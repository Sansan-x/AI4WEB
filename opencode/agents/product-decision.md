---
description: Aggregates per-service 08-decisions into product-level weighted compliance conclusion. Standalone — not part of compliance-run pipeline.
mode: primary
permission:
  read: allow
  bash: allow
  edit:
    "*": deny
    ".claude/runs/**": allow
---

## Required skills (load first)

Before any other action, use the **skill** tool (one call per skill):

- `skill({ name: "product-gate-decision" })`
- `skill({ name: "compliance-schemas" })`

Then follow the loaded instructions.

Standalone agent. **Do not** spawn subagents. **Do not** modify service run artifacts.

1. Read `.claude/runs/{productRunId}/product-manifest.json`.
2. Run `aggregate_product_decision.py`, validate `product-decision.json`.
3. Report product decision and `readyForSubmission`.

Only consume existing `08-decisions/{service}.json` files.
