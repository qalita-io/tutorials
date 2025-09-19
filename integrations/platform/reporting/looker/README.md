## Integration: Looker ← QALITA (Beta)

Goal: model QALITA metrics and issues in LookML and build explores.

High-level flow:

1. ETL or direct API ingestion lands QALITA metrics into a warehouse table/view.
2. LookML models define views and explores.
3. Dashboards surface trends with links back to QALITA.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` read-only APIs or export jobs.

Implementation options:

- Scheduled export to warehouse + LookML
- Direct PDTs using API via external connection

Docs references:

- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Provide warehouse schema for metrics and issues
- Example LookML snippets
- Define incremental export job in `app-backend`


