## Integration: Dagster → QALITA (Beta)

Goal: integrate Dagster ops/jobs with QALITA for quality checks and run reporting.

High-level flow:

1. Ops/materializations execute transformations.
2. After-ops hooks or resources call QALITA to register assets and push check results.
3. QALITA persists, scores, and surfaces issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` ingestion endpoints for runs, checks, metrics.
- `app-backend/src/backend/database/model/` for Jobs and Results.

Implementation options:

- A Dagster `ResourceDefinition` wrapping QALITA CLI/REST
- An `@success_hook` that sends asset metrics and statuses

Docs references:

- Dagster integration concepts: https://docs.dagster.io
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Provide `ResourceDefinition` example
- Define asset identity mapping to QALITA datasets
- Add CI example for dagster-cloud


