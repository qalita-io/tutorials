## Integration: Apache Airflow → QALITA (Beta)

Goal: embed data quality steps into DAGs and report run metadata and check results to QALITA.

High-level flow:

1. DAG tasks run transformations and validations.
2. Custom operators or simple Python callouts invoke QALITA CLI/REST to:
   - Register sources/datasets impacted by the DAG
   - Push check results and metrics
   - Report DAG run context (dag_id, run_id, task_id, try_number)
3. QALITA aggregates and surfaces issues and scores.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` for ingestion of runs, checks, metrics.
- `app-backend/src/backend/database/model/` for run and job lineage.

Implementation options:

- Lightweight `PythonOperator` calling `qalita` CLI
- Custom `QalitaOperator` for cleaner ergonomics and retries

Docs references:

- Orchestration guide: https://doc.qalita.io/docs/platform/user-guides/data-engineering/pipelines
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Provide sample DAG with `QalitaOperator`
- Standardize env variables for auth and endpoint URL
- Correlate Airflow run with QALITA Job id


### Quickstart

1) Install dependencies with Airflow constraints (recommended):

```bash
export AIRFLOW_VERSION=2.9.3
export PYTHON_VERSION="$(python -c 'import sys; print("".join(map(str, sys.version_info[:2])))')"
pip install -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
```

2) Configure environment variables (copy and edit). If your environment ignores `.env.example`, use `.env.sample` instead:

```bash
cp .env.sample .env || cp .env.example .env
```

Key variables (env or Airflow Variables):

- `QALITA_AGENT_ENDPOINT` — API base URL (e.g., `http://localhost:3080`)
- `QALITA_AGENT_TOKEN` — API token
- `QALITA_AGENT_NAME` — Optional name for this agent (default: airflow-agent)
- `QALITA_AGENT_MODE` — `job` or `worker` (DAG uses `job`)

3) Place the example DAG in your Airflow `dags/` folder:

- Copy the `dags/` directory from this tutorial into your Airflow `dags/` location, e.g. `~/airflow/dags/` or your deployment’s DAGs volume.

4) Start/refresh Airflow and trigger the DAG `qalita_example_dag`.

The DAG uses the `qalita` Python package from PyPI (Click-based CLI) via `QalitaOperator`:

- `version`: shows CLI version
- `agent login`: registers the agent context
- `source list`, `pack list`: helper discovery
- `agent run -s <source_id> -p <pack_id>`: runs a job for a given source/pack

Optional: set an Airflow Variable used by the DAG for IDs

```json
{
  "source_id": "<your_source_id>",
  "pack_id": "<your_pack_id>"
}
```

Save it under the key `qalita_params` in the Airflow UI (Admin → Variables) or via `airflow variables set`.

The DAG includes four tasks: extract, transform, a CLI smoke test, a checks run, and a run report. Commands are templated to include Airflow context. Adjust the CLI subcommands/flags to match your installed QALITA CLI.

### Files

- `dags/_lib/qalita_operator.py` — Custom operator to invoke the `qalita` Python package
- `dags/example_qalita_dag.py` — Example DAG wiring tasks and QALITA calls
- `requirements.txt` — Minimal Python deps
- `.env.example` — Environment variables used by the operator/CLI

### Notes

- The example uses the CLI pathway for simplicity. If you prefer direct REST calls, point the CLI at `QALITA_API_URL` or adapt the operator to use `requests` with your auth token.
- Airflow installations should use version-pinned constraints (see quickstart commands) to avoid dependency conflicts.


