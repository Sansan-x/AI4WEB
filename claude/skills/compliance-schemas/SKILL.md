---
name: compliance-schemas
description: JSON schema reference for compliance pipeline artifacts. Use when validating or authoring RiskPoint, ThreatSignal, ServiceContext, and evidence outputs.
---

# Compliance Schemas

Canonical schemas live in `compliance/schemas/`. Load the relevant file from `references/` when validating outputs.

## Schema index

| Key | File |
|-----|------|
| service-context | service-context.schema.json |
| threat-signal | threat-signal.schema.json |
| applicability | applicability.schema.json |
| service-risk-profile | service-risk-profile.schema.json |
| risk-points | risk-point.schema.json (array) |
| risk-case-mapping | risk-case-mapping.schema.json |
| gaps | gaps.schema.json |
| decision | decision.schema.json |
| service-decision | service-decision.schema.json |
| product-manifest | product-manifest.schema.json |
| product-decision | product-decision.schema.json |
| service-slices | service-slices.schema.json |
| evidence-package | evidence-package.schema.json |

## Validate

```bash
python3 compliance/scripts/validate_artifact.py --schema <key> --file <path>
```

Always validate before handing off to the next pipeline phase.
