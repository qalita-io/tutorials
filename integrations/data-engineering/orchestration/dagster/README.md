## Integration: Dagster → QALITA (Beta)

Goal: integrate Dagster ops/jobs with QALITA for quality checks and run reporting.

High-level flow:

1. Ops/materializations execute transformations.
2. After-ops hooks or resources call QALITA to register assets and push check results.
3. QALITA persists, scores, and surfaces issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` ingestion endpoints for runs, checks, metrics.
- `app-backend/src/backend/database/model/` for Jobs and Results.

Implementation options:

- A Dagster resource wrapping QALITA CLI/REST (provided below)
- Optional hooks that send asset metrics and statuses

Docs references:

- Dagster integration concepts: https://docs.dagster.io
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

### Quickstart

1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) Configure environment variables (copy and edit). If your environment ignores `.env.example`, set environment variables directly:

Required variables:

- `QALITA_AGENT_ENDPOINT` — API base URL (e.g., `http://localhost:3080`)
- `QALITA_AGENT_TOKEN` — API token
- `QALITA_AGENT_NAME` — Optional name for this agent (default: dagster-agent)
- `QALITA_AGENT_MODE` — `job` (default)

Option A — export in your shell:

```bash
export QALITA_AGENT_ENDPOINT=http://localhost:3080
export QALITA_AGENT_TOKEN=replace-with-your-token
export QALITA_AGENT_NAME=dagster-agent
export QALITA_AGENT_MODE=job
```

3) Run the example job with Dagster UI:

```bash
dagster dev -f definitions.py
```

Open the UI link printed by the command, find the job `example_qalita_job`, and launch it with the provided run config file:

```bash
run_config: run_config.example.yaml
```

Alternatively, run the job via CLI:

```bash
dagster job execute -f definitions.py -j example_qalita_job -c run_config.example.yaml
```

The job uses the `qalita` Python package (Click-based CLI) via the `QalitaResource`:

- `version`: shows CLI version
- `agent login`: registers the agent context
- `source list`, `pack list`: helper discovery
- `agent run -s <source_id> -p <pack_id>`: runs a checks job for a given source/pack

### Files

- `resources/qalita_resource.py` — Dagster resource to invoke the QALITA Python CLI
- `jobs/example_qalita_job.py` — Example ops and job wired to the resource
- `definitions.py` — Registers jobs and resources for Dagster
- `requirements.txt` — Minimal Python deps
- `run_config.example.yaml` — Example run config to pass source/pack IDs

### Notes

- The example uses the CLI pathway for simplicity. If you prefer direct REST calls, point the CLI at `QALITA_API_URL` or adapt the resource to use `requests` with your auth token.
- To align with Airflow examples, environment variables are shared: `QALITA_AGENT_ENDPOINT`, `QALITA_AGENT_TOKEN`, `QALITA_AGENT_NAME`, `QALITA_AGENT_MODE`.

