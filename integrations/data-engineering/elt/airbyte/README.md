## Integration: Airbyte → QALITA (Draft)

Goal: push Airbyte connection sync metadata and optional validation results into QALITA.

High-level flow:

1. Airbyte sync runs emit connection/job events.
2. A webhook or post-sync task calls `app-backend` to record:
   - Source/stream schemas and changes
   - Row counts and basic freshness metrics
   - Optional validation outcomes (pre/post-load checks)
3. QALITA persists and computes data quality scores and issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` ingestion endpoints (sources, datasets, runs, metrics, issues).
- `app-backend/src/backend/database/model/` for entities such as Source, Dataset, Job, Metric.

Implementation options:

- Airbyte webhook to a QALITA endpoint with a small adapter service.
- Post-sync script using QALITA CLI to push metrics and schema snapshots.

Docs references:

- Platform quick start: https://doc.qalita.io/docs/platform/quick-start
- Sources: https://doc.qalita.io/docs/platform/user-guides/admin/sources
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Define minimal payload schema for connection runs
- Provide example Docker Compose with Airbyte + QALITA adapter
- Map Airbyte stream to QALITA dataset identity


