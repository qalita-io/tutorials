## Integration: Power BI ← QALITA (Beta)

Goal: visualize QALITA scores and issues in Power BI reports.

High-level flow:

1. Power BI connects to QALITA API endpoints.
2. Scheduled refresh retrieves metrics and issue dimensions/facts.
3. Reports include deep links back to QALITA entities.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` read-only reporting endpoints.

Implementation options:

- Power BI dataflows using REST connector
- Incremental refresh with updated_since parameters

Docs references:

- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Provide sample Power BI template and query M scripts
- Define authentication strategy (Bearer token)
- Document recommended dataset model


