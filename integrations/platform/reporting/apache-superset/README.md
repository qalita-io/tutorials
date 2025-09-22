## Integration: Apache Superset ← QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-superset.png"/>
</p>

Goal: explore and dashboard QALITA metrics and issues via Superset.

### What you'll set up
- A local Apache Superset + Postgres stack seeded with example QALITA reporting tables
- A Superset database connection to query those tables
- Example datasets you can use to build charts and dashboards

### Architecture
1) QALITA exports metrics/issues to a SQL store (here: Postgres).
2) Superset connects to that store and models datasets over tables/views.
3) Users build charts/dashboards; links can drill through to QALITA entities.

### Prerequisites
- Docker and Docker Compose
- Ports available: 5432 (Postgres) and 8088 (Superset)

### Quickstart
1. Change directory:
   - `cd platform/tutorials/integrations/platform/reporting/apache-superset/resources`
2. (Optional) Configure environment overrides:
   - Copy `env.example` to `.env` and adjust values (defaults work out of the box).
3. Start services:
   - `docker compose up -d`
4. Wait for initialization:
   - Postgres seeds the reporting schema and CSV demo data.
   - Superset database is migrated and an admin user is created.
5. Open Superset:
   - `http://localhost:8088` (user: `admin`, pass: `admin` unless changed)
6. Add the reporting database in Superset:
   - Menu → Settings → Database Connections → + Database → Postgres
   - SQLAlchemy URI:
     - `postgresql+psycopg2://reporter:reporter@postgres:5432/qalita_reporting`
     - If running Superset separately, use `localhost` instead of `postgres`.
   - Test connection and save.
7. Create datasets:
   - Menu → Data → Datasets → + Dataset → pick the new database and select table `reporting.metrics_daily`
   - Repeat for `reporting.issues`

You're ready to explore and build charts.

### Example queries
- Daily completeness trend:
  - `SELECT metric_date, metric_value FROM reporting.metrics_daily WHERE metric_name = 'completeness_score' ORDER BY metric_date`
- Open issues by severity:
  - `SELECT severity, COUNT(*) FROM reporting.issues WHERE status = 'open' GROUP BY severity`

### Drill-through to QALITA
- Add a column or calculated field that constructs a URL to QALITA entity pages, e.g. `https://app.qalita.io/projects/{{ project }}` and use Superset's table chart with clickable links.

### Schema provided (reporting)
- `metrics_daily(metric_date, project, domain, metric_name, metric_value, tags JSONB)`
- `issues(issue_id, project, domain, severity, status, created_at, resolved_at)`

Indexes are included for common filters (date/project/metric).

### Security and RBAC (recommended)
- Use a read-only database user for Superset (the default `reporter` user has full rights in this demo; restrict in production).
- Limit exposed tables/views to necessary reporting surfaces only.

### Files in this tutorial
- `resources/docker-compose.yml`: launches Postgres (seeded) and Superset
- `resources/env.example`: optional env overrides; copy to `.env`
- `resources/postgres/init/01_schema.sql`: reporting schema and tables
- `resources/postgres/init/02_seed.sql`: CSV imports for demo data
- `resources/postgres/seeds/*.csv`: sample data
- `resources/superset/init.sh`: Superset initialization script

### Cleanup
- `docker compose down -v` from the `resources` directory

### Docs references
- Reporting: https://doc.qalita.io/docs/platform/user-guides/reporting

