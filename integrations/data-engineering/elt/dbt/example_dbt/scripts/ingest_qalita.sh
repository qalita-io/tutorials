#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="opendata_dbt"
ENV_NAME="dev"

MANIFEST="target/manifest.json"
RESULTS="target/run_results.json"

if [[ ! -f "$MANIFEST" || ! -f "$RESULTS" ]]; then
  echo "manifest.json or run_results.json not found. Run 'make all' first." >&2
  exit 1
fi

echo "Ingesting dbt artifacts into QALITA..."
qalita ingest dbt \
  --manifest "$MANIFEST" \
  --results "$RESULTS" \
  --project "$PROJECT_NAME" \
  --env "$ENV_NAME"

echo "Done."

