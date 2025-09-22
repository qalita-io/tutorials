## Integration: Soda → QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../img/integration/qalita-x-soda.png"/>
</p>

Goal: forward Soda scan results to QALITA for centralized tracking and issue management.

High-level flow:

1. `soda scan` executes checks from YAML and outputs results (JSON/CLI).
2. A post-scan step calls QALITA CLI/REST to push:
   - Check definitions and outcomes
   - Dataset metrics and thresholds
   - Scan context (environment, dataset identifiers)
3. QALITA stores results, updates scores, and opens/updates issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` for checks, results, issues.
- `app-backend/src/backend/database/model/` for Check, Result, Issue, Dataset.

Implementation options:

- Wrap `soda scan` in a script that outputs JSON and calls `qalita ingest soda --file results.json`.
- Direct REST webhook if using Soda Cloud webhooks.

Docs references:

- Data quality checks: https://doc.qalita.io/docs/platform/user-guides/data-engineering/checks
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

### Quickstart (standalone example)

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Run a Soda scan on the sample dataset and produce artifacts:

```bash
python run_soda.py --data data/retail.csv --checks checks/checks.yaml --artifacts artifacts
```

This writes:
- `artifacts/metrics.json` and `artifacts/recommendations.json` compatible with QALITA Agent upload
- `artifacts/soda_results.json` raw Soda results for troubleshooting

3. (Optional) Push artifacts via the QALITA Agent CLI

If you already have an agent configured and a `Source` published, you can run a pack that uploads `metrics.json` and `recommendations.json`, or adapt your CI to POST these files using `qalita`'s agent upload endpoints used by packs.

---

### Example contents

- `data/retail.csv` — sample dataset
- `checks/checks.yaml` — SodaCL checks
- `run_soda.py` — script: loads CSV, runs Soda, writes artifacts (metrics/recommendations)
- `requirements.txt` — Python dependencies

---

### Notes

- For production, plug the scan into your orchestration (Airflow/Dagster) and call QALITA upload endpoints similarly to agent pack post-run.
- You can also reuse the existing `soda_pack` under `packs/` for a ready-to-run Agent workflow.


