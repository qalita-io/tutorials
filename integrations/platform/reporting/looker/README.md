## Integration: Looker ← QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-looker.png"/>
</p>

This guide explains how to model QALITA Platform data in Looker: land QALITA metrics and issues into your warehouse and expose them through LookML explores and dashboards.

What you will set up:

1. Warehouse tables for `qalita_metrics` and `qalita_issues`.
2. LookML model and views for metrics and issues.
3. A sample incremental export job that pulls from QALITA APIs and upserts into the warehouse.

Backend touchpoints and APIs:

- Read-only v2 endpoints (auth required):
  - Metrics: `/api/v2/metrics`
  - Issues: `/api/v2/issues`
  - Both are partner-scoped and support typical field filters (e.g., `source_id`) and offset-based pagination.

Implementation options:

- Recommended: Scheduled export job → Warehouse tables → LookML explores.
- Optional/advanced: Direct API → external ingestion → transient staging → PDTs. This is possible but not generally recommended for production due to reliability and rate limits.

References:

- Reporting guide: https://doc.qalita.io/docs/platform/user-guides/reporting

Prerequisites

- A running QALITA Platform instance (API URL and an API token with scopes `metric:get` and `issue:get`).
- A SQL warehouse accessible from Looker (e.g., Postgres, Snowflake, BigQuery). The provided SQL DDL is Postgres-compatible; adapt types as needed for your warehouse.
- A Looker connection pointing to the target schema/database where you will create the tables.

1) Create the warehouse schema

- Apply the DDL at `warehouse/schema.sql` in your warehouse (Postgres shown; adapt as needed).
- Resulting tables: `qalita_metrics`, `qalita_issues` with indexes for common filters.

2) Configure the export job (incremental)

- Location: `export_job/`
- Files:
  - `export_qalita_to_warehouse.py`: pulls QALITA metrics/issues and upserts into warehouse tables, maintaining a watermark on `created_at` to export incrementally.
  - `requirements.txt`: minimal dependencies.
  - `.env.example`: environment variables to set (copy to `.env`).

Quick start

```bash
cd tutorials/integrations/platform/reporting/looker/export_job
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # then edit values
python export_qalita_to_warehouse.py
```

Environment variables

- `QALITA_API_URL`: e.g., `https://your-qalita.example.com`
- `QALITA_API_TOKEN`: Bearer token (scopes: `metric:get`, `issue:get`)
- `WAREHOUSE_URL`: SQLAlchemy URL to your warehouse, e.g., `postgresql+psycopg2://user:pass@host:5432/dbname`
- `WAREHOUSE_SCHEMA`: Target schema (optional for Postgres; if using, the script sets `search_path`)
- `BATCH_SIZE`: Optional page size for API reads (default 1000)

Scheduling

- Run the job every 5–15 minutes (cron, Airflow, dbt, etc.). The job reads `created_at` watermarks from the warehouse and only upserts newer records.

3) Add LookML (model + views + explores)

- Location: `looker/`
- Files:
  - `qalita.model.lkml`: sets your Looker connection and includes views.
  - `views/metrics.view.lkml`: dimensions/measures for `qalita_metrics`.
  - `views/issues.view.lkml`: dimensions/measures for `qalita_issues`.

Usage in Looker

1. Copy the `looker/` directory into your LookML project (or copy-paste file contents into your repo). Update the `connection:` value in `qalita.model.lkml` to match your Looker connection name.
2. Adjust `sql_table_name` to include your database/schema if needed (e.g., `mydb.public.qalita_metrics`).
3. Push to production and validate the explores. Start building Looks and dashboards.

Backlinks to QALITA

- The views include URL dimensions that link back to QALITA for a given source/issue.
- You can parameterize the base URL via a LookML parameter or use a hardcoded URL for your environment.

Data model notes

- Metrics are time-series keyed by (`partner_id`, `source_id`, `pack_id`, `key`, `created_at`). The `value` is stored as text; cast to numeric in measures when needed.
- Issues represent data quality work items with assignees and due dates.
- Both entities inherit `partner_id`, `created_at`, `updated_at`. Partner-level scoping happens at export time via API token.

Validation queries (warehouse)

```sql
-- total metrics rows, latest ingestion time
select count(*) as row_count, max(created_at) as latest from qalita_metrics;

-- list of distinct metric keys
select key, count(*) from qalita_metrics group by 1 order by 2 desc limit 50;

-- issues status distribution
select status, count(*) from qalita_issues group by 1 order by 2 desc;
```

Troubleshooting

- Empty explores: check your export job ran and that Looker’s connection points to the correct schema.
- Auth errors: verify `QALITA_API_TOKEN` scopes and API base URL.
- Slow queries: consider clustering/indexing `created_at`, `source_id`, `pack_id`, and `status`.
