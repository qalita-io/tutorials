## Integration: Power BI ← QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-powerbi.png"/>
</p>

Goal: visualize QALITA scores and issues in Power BI reports.

High-level flow:

1. Power BI connects to QALITA API endpoints.
2. Scheduled refresh retrieves metrics and issue dimensions/facts.
3. Reports include deep links back to QALITA entities.

Backend touchpoints:

- QALITA API base URL: your tenant URL, e.g. `https://your-qalita.example.com`
- API versions and resources (secured with Bearer JWT):
  - v1 Authentication and tokens: `/api/v1/auth/signin`, `/api/v1/tokens/create`
  - v2 CRUD resources (read for reporting): `/api/v2/metrics`, `/api/v2/issues`, `/api/v2/sources`, `/api/v2/packs`, `/api/v2/jobs`, `/api/v2/recommendations`, etc.
  - v1 Report-friendly endpoints (optional): `/api/v1/reports/{report_id}/...` for curated joins such as monthly scores

Implementation options:

- Power BI Desktop or Dataflows using Power Query (M) via Web.Contents
- Incremental refresh using date filters (see Monthly Scores example)

Docs references:

- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Provide sample Power BI template and query M scripts
- Define authentication strategy (Bearer token)
- Document recommended dataset model

### Prerequisites

- QALITA Platform URL and a user with API access
- Email/password for `/api/v1/auth/signin` or an existing Bearer/API token
- Power BI Desktop (or Power BI Service for Dataflows)

### Authentication

You can authenticate with either a short-lived Bearer JWT (username/password) or a longer-lived API token created by the user.

1) Obtain a Bearer JWT via signin (recommended for development):
   - Endpoint: `POST {QALITA_URL}/api/v1/auth/signin`
   - Form fields: `username`, `password`
   - Returns JSON with `access_token`

2) Or create an API token (recommended for scheduled refresh):
   - Endpoint: `POST {QALITA_URL}/api/v1/tokens/create`
   - Auth: Bearer JWT from step 1
   - Response contains `access_token` of type `api`

Both tokens are used with header: `Authorization: Bearer {token}`

### Endpoints commonly used for reporting

- v2 resources (paginated up to 10,000 by default):
  - `/api/v2/metrics?source_id={id}&pack_id={id}`
  - `/api/v2/issues`
  - `/api/v2/sources`
  - `/api/v2/packs`
  - `/api/v2/jobs?status=succeeded&status=failed`
  - `/api/v2/recommendations?source_id={id}&pack_id={id}`

- v1 curated report endpoints (include domain logic; useful for timeseries):
  - `/api/v1/reports/{report_id}/sources/{source_id}/monthly_scores`
  - `/api/v1/reports/{report_id}/sources/{source_id}/scores`
  - `/api/v1/reports/{report_id}/jobs?source_id={source_id}`
  - `/api/v1/reports/{report_id}/schemas/{source_id}?source_version_id={version_id}`

Note: v1 report endpoints require a `report_id` created in QALITA and check access via token/user.

### Power Query (M) setup

This tutorial ships with two M resources:

- `QALITA.pq`: reusable functions for Auth and GET requests
- `QALITA-Samples.m`: sample queries you can paste into Power BI Desktop

Files are located next to this README. In Power BI Desktop:

1. Get Data → Blank Query
2. Advanced Editor → paste the contents of `QALITA.pq` first (create a new query named `QALITA` or multiple function queries).
3. Then add new queries using snippets from `QALITA-Samples.m` and replace placeholders.

Recommended privacy level: Organizational. Authentication in Power BI should be set to Anonymous because headers are set in M code.

### Sample: Sign in and store token

Use `QALITA_SignIn` to exchange username/password for a JWT and keep it in a parameter or a table.

Parameters to create in Power BI:

- `QALITA_Url` (Text), e.g. `https://your-qalita.example.com`
- `QALITA_Username` (Text)
- `QALITA_Password` (Text) or `QALITA_ApiToken` (Text) if you prefer API token

### Sample: Metrics for a source/pack

Refer to `QALITA_Sample_Metrics` in `QALITA-Samples.m`. It calls `/api/v2/metrics?source_id=...&pack_id=...` and expands JSON.

### Sample: Monthly scores timeseries

Refer to `QALITA_Sample_MonthlyScores` in `QALITA-Samples.m`. It calls `/api/v1/reports/{report_id}/sources/{source_id}/monthly_scores` and returns a table with month and scores by dimension. You can configure incremental refresh on the month column.

### Deep links back to QALITA

Build columns like:

- Source URL: `{QALITA_URL}/home/data-engineering/sources/{source_id}`
- Pack URL: `{QALITA_URL}/home/data-engineering/packs/{pack_id}`
- Alerts URL: `{QALITA_URL}/home/data-management/alerts`

### Dataset model (recommendation)

- Sources (dimension)
- Packs (dimension)
- Metrics (fact, includes key/value, created_at, source_id, pack_id)
- Issues (fact, includes status, severity, source_id, assignees)
- Jobs (fact for runs)
- Optional: MonthlyScores (fact by month × dimension)

### Security and pagination

- All calls require `Authorization: Bearer {token}`
- v2 list endpoints return up to 10,000 rows by default. For very large volumes, consider partitioning by `source_id`, `pack_id`, or using report endpoints.

### Troubleshooting

- 401 Unauthorized: token expired or missing scopes; reauthenticate or use API token
- 204 No Content: resource not found or user lacks access; verify IDs and permissions
- Refresh errors in Service: ensure the data source privacy is Organizational and M sets headers; avoid using the built-in Web connector auth


