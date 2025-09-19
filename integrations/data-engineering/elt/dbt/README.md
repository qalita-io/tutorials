## Integration: dbt → QALITA (Draft)

Goal: export data quality metadata and test results from dbt runs into QALITA.

High-level flow:

1. dbt generates artifacts (manifest.json, run_results.json) and test results.
2. A post-run step invokes QALITA CLI (`tools-cli`) or direct REST calls to `app-backend` to push:
   - Source, dataset, and model metadata
   - Test definitions and outcomes
   - Run context (job id, environment, git sha)
3. QALITA ingests and persists via `app-backend` (`routers/v2`, `database/model`) and triggers scoring/jobs.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` for ingestion endpoints (e.g., sources, datasets, checks, runs, issues).
- `app-backend/src/backend/database/model/` for persisted entities (Job, Source, Check, Result).
- Optional background workers for async processing and scoring.

Implementation options:

- Use QALITA CLI (`/home/aleopold/platform/tools-cli`) in a dbt post-hook or CI step:
  - Collect artifacts: `target/manifest.json`, `target/run_results.json`
  - Run: `qalita ingest dbt --manifest path --results path --project <name> --env <name>`
- Direct REST integration from CI using an API token.

Docs references:

- Platform quick start: https://doc.qalita.io/docs/platform/quick-start
- Packs and sources: https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Map dbt test statuses to QALITA status schema
- Define idempotency keys per run (project, environment, git sha, run id)
- Provide example CI YAML for dbt Cloud and GitHub Actions


