## Integration: Apache Superset ← QALITA (Draft)

Goal: explore and dashboard QALITA metrics and issues via Superset.

High-level flow:

1. Expose QALITA metrics in a SQL-accessible store (or via CSV imports).
2. Add as a dataset in Superset and build charts/dashboards.
3. Provide drill-through links to QALITA.

Backend touchpoints:

- `app-backend` export jobs or materialized views for metrics.

Implementation options:

- Nightly export to Postgres schema used by Superset
- CSV export via CLI and file upload

Docs references:

- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Define metrics tables and recommended indexes
- Provide example Superset dashboard JSON import
- Configure RBAC for read-only access


