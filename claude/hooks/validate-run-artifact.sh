#!/usr/bin/env bash
# PostToolUse hook: validate JSON written under .claude/runs/
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || true)

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Only validate run artifacts
if [[ "$FILE_PATH" != *".claude/runs/"* ]] || [[ "$FILE_PATH" != *.json ]]; then
  exit 0
fi

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
VALIDATOR="$PROJECT_ROOT/compliance/scripts/validate_artifact.py"
SCHEMA_DIR="$PROJECT_ROOT/compliance/schemas"

schema_for() {
  local base
  base=$(basename "$FILE_PATH")
  local dir
  dir=$(dirname "$FILE_PATH")

  case "$base" in
    manifest.json) echo "" ;;
    product-manifest.json) echo "product-manifest" ;;
    product-decision.json) echo "product-decision" ;;
    00-service-slices.json) echo "service-slices" ;;
    06-mappings.json) echo "risk-case-mapping" ;;
    05-risk-points.json) echo "risk-points" ;;
    07-gaps.json) echo "gaps" ;;
    08-decision.json) echo "decision" ;;
    index.json) echo "evidence-package" ;;
    exposure.json|dataflow.json|controlplane.json) echo "threat-signal" ;;
    *)
      if [[ "$dir" == *"/01-context" ]]; then echo "service-context"; fi
      if [[ "$dir" == *"/02-applicability" ]]; then echo "applicability"; fi
      if [[ "$dir" == *"/04-profiles" ]]; then echo "service-risk-profile"; fi
      if [[ "$dir" == *"/08-decisions" ]]; then echo "service-decision"; fi
      ;;
  esac
}

SCHEMA=$(schema_for)
if [[ -z "$SCHEMA" ]]; then
  exit 0
fi

if [[ ! -f "$VALIDATOR" ]]; then
  exit 0
fi

python3 "$VALIDATOR" --schema "$SCHEMA" --file "$FILE_PATH" --schema-dir "$SCHEMA_DIR" || {
  echo "Compliance artifact validation failed for $FILE_PATH (schema=$SCHEMA)" >&2
  exit 2
}

exit 0
