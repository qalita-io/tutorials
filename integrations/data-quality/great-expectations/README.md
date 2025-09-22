## Integration: Great Expectations → QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../img/integration/qalita-x-great-expectations.png"/>
</p>

Goal: forward Great Expectations validation results to QALITA for centralized observability and issue tracking.

High-level flow:

1. GE `Checkpoints` run validations and produce `validation_results` and data docs artifacts.
2. A post-validation action or CI step calls QALITA CLI/REST to push:
   - Expectation suite metadata
   - Validation outcomes and metrics
   - Run context (datasource, suite name, run id, env)
3. QALITA persists results, updates scores, and opens/updates issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` endpoints for checks, results, datasets, issues.
- `app-backend/src/backend/database/model/` entities: Check, Result, Dataset, Issue, Job.

Implementation options:

- Use a GE `Action` in a `Checkpoint` to export JSON and invoke `qalita ingest ge --file <validation.json>`.
- Direct REST POST in CI after running `great_expectations checkpoint run`.

Docs references:

- Checks and results: https://doc.qalita.io/docs/platform/user-guides/data-engineering/checks
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Map GE result schema to QALITA unified model
- Provide example `Checkpoint` YAML and integration script
- Define deterministic dataset identity mapping

### Quickstart (standalone example)

1. Create the environment and install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (copy and edit):

```bash
cp .env.sample .env || cp .env.example .env
```

Key variables:

* `QALITA_AGENT_ENDPOINT` — API URL (e.g. `http://localhost:3080`)
* `QALITA_AGENT_TOKEN` — QALITA API token
* `QALITA_SOURCE_ID` — QALITA Source ID associated with the dataset

3. Run a Great Expectations validation and ingest results into QALITA:

**Option A** — simplified Python runner (recommended for this example):

```bash
python run_ge_and_ingest.py --suite retail_suite --data data/retail.csv
```

**Option B** — via Checkpoint YAML (GE CLI), then ingestion:

```bash
great_expectations checkpoint run retail_checkpoint
python ingest_ge_results.py --file artifacts/last_validation_result.json
```

4. Visualize in QALITA: checks, results, scores, and issues are created/updated.

---

### Example contents

* `data/retail.csv` — sample dataset
* `ge/expectations/retail_suite.json` — expectation suite
* `ge/checkpoints/retail_checkpoint.yml` — ready-to-use checkpoint
* `run_ge_and_ingest.py` — script: loads data, runs GE, sends metrics to QALITA
* `ingest_ge_results.py` — script: ingests an existing GE validation JSON
* `requirements.txt` — Python dependencies
* `.env.example` — environment variables
* `Makefile` — handy commands

---

### Notes

* The example uses the QALITA API via the `qalita` library (tools-cli) to publish metrics as `metrics.json` compatible with the Agent.
* If you already use GE `Checkpoints`, you can plug in a custom `Action` to export the JSON and call:

  ```bash
  python ingest_ge_results.py --file <path>
  ```

  or integrate a `qalita` CLI call directly into your CI.
