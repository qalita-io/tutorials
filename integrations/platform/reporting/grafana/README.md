## Integration: Grafana ← QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-grafana.png"/>
</p>

Monitor QALITA quality metrics and issues in Grafana. This tutorial ships a ready-to-run stack with Postgres (seeded demo data), Grafana provisioning (datasources + dashboards), and optional access to your running QALITA API via Grafana's JSON API plugin.

### What you'll set up
- A local Postgres database seeded with a minimal reporting schema and demo data
- Grafana with pre-provisioned datasources and a starter "QALITA Quality Overview" dashboard
- Optional JSON API datasource to call QALITA read APIs directly (Bearer token)

### Architecture
1) QALITA metrics can be exported to a SQL store (here: Postgres) or read via HTTP APIs.
2) Grafana connects to these sources and renders time-series and KPIs.
3) Alerts can be configured either in Grafana or within QALITA.

### Prerequisites
- Docker and Docker Compose
- Open ports: 5432 (Postgres), 3000 (Grafana)
- Optional: A running QALITA backend if you want to query live APIs from Grafana

### Quickstart
1. Change directory:
   - `cd platform/tutorials/integrations/platform/reporting/grafana/resources`
2. (Optional) Enable QALITA API access from Grafana:
   - Create a file named `.env` in this folder with:
     - `QALITA_API_TOKEN=<your_bearer_token>`
   - The JSON API datasource points to `http://host.docker.internal:8000/api/v1` by default. On Linux we map `host.docker.internal` to the host gateway.
3. Start services:
   - `docker compose up -d`
4. Open Grafana:
   - `http://localhost:3000` (user: `admin`, pass: `admin`)
5. Verify provisioning:
   - Datasource `QALITA Reporting (Postgres)` should be present and healthy.
   - Folder `QALITA` contains the dashboard `QALITA Quality Overview`.
6. Explore the dashboard:
   - Timeseries panels use demo metrics (`reporting.metrics_daily`).
   - KPIs and charts use `reporting.issues` and can be adapted to your needs.

You're ready to monitor quality trends.

### Files in this tutorial
- `resources/docker-compose.yml`: launches Postgres (seeded) and Grafana (provisioned)
- `resources/grafana/provisioning/datasources/datasource.yml`: Postgres + JSON API datasources
- `resources/grafana/provisioning/dashboards/dashboards.yml`: dashboard provisioning
- `resources/grafana/dashboards/qalita-quality-overview.json`: starter dashboard
- `resources/postgres/init/01_schema.sql`: reporting schema (metrics + issues)
- `resources/postgres/init/02_seed.sql`: loads CSV demo data
- `resources/postgres/seeds/*.csv`: sample data (edit or replace for your PoC)

### Reporting schema provided (Postgres)
- `reporting.metrics_daily(metric_date, project, domain, metric_name, metric_value, tags JSONB)`
- `reporting.issues(issue_id, project, domain, severity, status, created_at, resolved_at)`
Indexes are included for common filters (date/project/metric).

### Optional: Query QALITA live APIs from Grafana (JSON API datasource)
This stack installs the `marcusolsson-json-datasource` plugin and provisions a datasource named `QALITA API (JSON)` pointing to `http://host.docker.internal:8000/api/v1`.

- Authentication:
  - Set `QALITA_API_TOKEN` in `resources/.env` before `docker compose up -d`.
  - The datasource sends `Authorization: Bearer $QALITA_API_TOKEN`.

- Useful endpoints you can query:
  - `/reports/{report_id}/sources/{source_id}/monthly_scores` → returns monthly scores with `datetime` and per-dimension values
  - `/reports/{report_id}/metrics?source_id={sid}&pack_id={pid}` → returns recent metrics for a source/pack
  - `/sources/{source_id}/metrics` (requires appropriate scopes) → metrics for a given source

Notes:
- JSON responses can be transformed in Grafana (Labels to fields, Organize fields, etc.) to plot timeseries.
- If `host.docker.internal` does not resolve on your Linux distro, replace it with your host IP and update `datasource.yml` accordingly.

### Security and RBAC
- The demo `reporter` Postgres user has full rights in this sandbox. In production, restrict to read-only.
- Pass only necessary auth tokens to Grafana and rotate them regularly.
- Limit exposed tables/views and API scopes.

### Cleanup
- From the `resources` directory: `docker compose down -v`

### Troubleshooting
- Grafana cannot reach QALITA API:
  - Ensure `QALITA_API_TOKEN` is set and the backend is reachable from Docker (try `curl http://host.docker.internal:8000/ping`).
  - Update `datasource.yml` to use your host IP if needed and `docker compose restart grafana`.
- Plugin missing:
  - The compose file sets `GF_INSTALL_PLUGINS=marcusolsson-json-datasource`. If not installed, check Grafana logs.
- Postgres not seeding:
  - Ensure the `./postgres/init` and `./postgres/seeds` mounts are present and files are readable.

### Docs references
- Reporting/Monitoring: https://doc.qalita.io/docs/platform/user-guides/reporting

