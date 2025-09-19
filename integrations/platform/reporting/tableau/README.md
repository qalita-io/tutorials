## Integration: Tableau ← QALITA (Draft)

Goal: consume QALITA metrics and issues in Tableau dashboards.

High-level flow:

1. Tableau connects to a QALITA reporting view/API.
2. Scheduled extract refresh pulls metrics (scores, failures, MTTR) and issue tables.
3. Dashboards visualize trends and drill back to QALITA.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` read-only endpoints for metrics and issues.
- Optional pre-aggregated views in reporting schema.

Implementation options:

- REST connector (Web Data Connector) or CSV exports via CLI
- Direct database connection if QALITA exposes analytics DB (TBD)

Docs references:

- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Define stable, paginated endpoints for BI consumption
- Provide example Tableau workbook with schema description
- Authentication via API key in connector


