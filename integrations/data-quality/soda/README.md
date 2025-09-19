## Integration: Soda → QALITA (Beta)

Goal: forward Soda scan results to QALITA for centralized tracking and issue management.

High-level flow:

1. `soda scan` executes checks from YAML and outputs results (JSON/CLI).
2. A post-scan step calls QALITA CLI/REST to push:
   - Check definitions and outcomes
   - Dataset metrics and thresholds
   - Scan context (environment, dataset identifiers)
3. QALITA stores results, updates scores, and opens/updates issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` for checks, results, issues.
- `app-backend/src/backend/database/model/` for Check, Result, Issue, Dataset.

Implementation options:

- Wrap `soda scan` in a script that outputs JSON and calls `qalita ingest soda --file results.json`.
- Direct REST webhook if using Soda Cloud webhooks.

Docs references:

- Data quality checks: https://doc.qalita.io/docs/platform/user-guides/data-engineering/checks
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Map Soda check types to QALITA unified schema
- Provide example `soda.yaml` and integration script
- Correlate scans with QALITA Source and Dataset ids


