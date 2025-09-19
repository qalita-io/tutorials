## Integration: Great Expectations → QALITA (Beta)

Goal: forward Great Expectations validation results to QALITA for centralized observability and issue tracking.

High-level flow:

1. GE `Checkpoints` run validations and produce `validation_results` and data docs artifacts.
2. A post-validation action or CI step calls QALITA CLI/REST to push:
   - Expectation suite metadata
   - Validation outcomes and metrics
   - Run context (datasource, suite name, run id, env)
3. QALITA persists results, updates scores, and opens/updates issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` endpoints for checks, results, datasets, issues.
- `app-backend/src/backend/database/model/` entities: Check, Result, Dataset, Issue, Job.

Implementation options:

- Use a GE `Action` in a `Checkpoint` to export JSON and invoke `qalita ingest ge --file <validation.json>`.
- Direct REST POST in CI after running `great_expectations checkpoint run`.

Docs references:

- Checks and results: https://doc.qalita.io/docs/platform/user-guides/data-engineering/checks
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Map GE result schema to QALITA unified model
- Provide example `Checkpoint` YAML and integration script
- Define deterministic dataset identity mapping


