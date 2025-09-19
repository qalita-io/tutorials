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


