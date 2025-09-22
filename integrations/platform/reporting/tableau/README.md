## Integration: Tableau ← QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-tableau.png"/>
</p>

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



### What you'll set up

- A minimal Tableau Web Data Connector (WDC) for QALITA APIs
- Sample CSVs you can import into Tableau for an offline/demo setup
- Guidance on authentication and recommended endpoints

### Prerequisites

- Tableau Desktop (2021.4 or later recommended)
- Access to a running QALITA backend (`http://localhost:8000` by default)
- A QALITA API token with read permissions

### Option A — Connect via Web Data Connector (recommended)

1) Start a simple local web server to host the connector UI:

   - `cd platform/tutorials/integrations/platform/reporting/tableau/resources/wdc`
   - `python3 -m http.server 8089`

2) In Tableau Desktop:

   - Data → New Data Source → To a Server → Web Data Connector
   - URL: `http://localhost:8089/index.html`
   - Fill in the form:
     - Base URL: `http://localhost:8000/api/v1` (adjust if needed)
     - API Token: your QALITA token
     - Select tables: `metrics` and/or `issues`
     - For `metrics`: provide `Report ID`, `Source ID`, `Pack ID`
     - For `issues`: provide `Project ID`
   - Click “Connect to Tableau”, then proceed to load data.

3) Refreshes in Tableau:

   - Use Extracts for scheduled refreshes
   - For large volumes, consider filtering by project or splitting by table

### Option B — Use sample CSVs (quick demo)

If you only want to try the visuals without hitting the API, import the CSVs:

- `resources/csv/metrics_daily.csv`
- `resources/csv/issues.csv`

These match the example reporting schema used in other tutorials and can be replaced with your own exports.

### API endpoints used by the WDC

- Metrics: `/api/v1/reports/{report_id}/metrics?source_id={sid}&pack_id={pid}`
- Issues: `/api/v1/projects/{project_id}/issues`

Required scopes depend on your RBAC configuration. Typical read scopes include: `report:get`, `metric:get`, `issue:get.all`.

### Table schemas exposed to Tableau

- metrics:
  - `id` (int)
  - `created_at` (datetime)
  - `source_id` (int)
  - `source_version_id` (int)
  - `pack_id` (int)
  - `pack_version_id` (int)
  - `key` (string)
  - `value` (string)
  - `scope` (stringified JSON)

- issues:
  - `id` (int)
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `title` (string)
  - `description` (string)
  - `status` (string)
  - `source_id` (int)
  - `assignee` (int)
  - `due_date` (datetime)
  - `url` (string)
  - `chat_url` (string)
  - `closed_at` (datetime)

Notes:

- The WDC stringifies nested objects like `scope` and `source` so they can be used as dimensions or parsed in Tableau Prep if needed.
- Add filters in Tableau to limit data volume by dates, projects, or sources.

### Files in this tutorial

- `resources/wdc/index.html`: Connector UI (form + load button)
- `resources/wdc/qalita-wdc.js`: WDC logic (schema + data fetch)
- `resources/csv/metrics_daily.csv`: Sample metrics
- `resources/csv/issues.csv`: Sample issues

### Security and best practices

- Use a token scoped to read-only for the intended projects/sources
- Rotate API tokens regularly and store them securely
- Use Extract refreshes on a secure server rather than live connections

### Troubleshooting

- Cannot reach API from Tableau:
  - Verify Base URL, and that QALITA is reachable (`curl http://localhost:8000/ping`)
  - If Tableau runs in a sandboxed environment, host the WDC on a reachable address
- 401 Unauthorized:
  - Check token validity and scopes
- Empty tables:
  - Ensure `report_id`, `source_id`, `pack_id`, and `project_id` are correct and data exists
- Corporate proxy/SSL:
  - Host the WDC behind HTTPS if required by your environment
