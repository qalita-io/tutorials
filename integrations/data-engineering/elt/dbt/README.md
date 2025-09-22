## Integration: dbt → QALITA (Beta)

Goal: export data quality metadata and test results from dbt runs into QALITA.

High-level flow:

1. dbt generates artifacts (manifest.json, run_results.json) and test results.
2. A post-run step invokes QALITA CLI (`tools-cli`) or direct REST calls to `app-backend` to push:
   - Source, dataset, and model metadata
   - Test definitions and outcomes
   - Run context (job id, environment, git sha)
3. QALITA ingests and persists via `app-backend` (`routers/v2`, `database/model`) and triggers scoring/jobs.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` for ingestion endpoints (e.g., sources, datasets, checks, runs, issues).
- `app-backend/src/backend/database/model/` for persisted entities (Job, Source, Check, Result).
- Optional background workers for async processing and scoring.

Implementation options:

- Use QALITA CLI (`/home/aleopold/platform/tools-cli`) in a dbt post-hook or CI step:
  - Collect artifacts: `target/manifest.json`, `target/run_results.json`
  - Run: `qalita ingest dbt --manifest path --results path --project <name> --env <name>`
- Direct REST integration from CI using an API token.

Docs references:

- Platform quick start: https://doc.qalita.io/docs/platform/quick-start
- Packs and sources: https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Map dbt test statuses to QALITA status schema
- Define idempotency keys per run (project, environment, git sha, run id)
- Provide example CI YAML for dbt Cloud and GitHub Actions


### Exemple prêt-à-l'emploi (Open Data + DuckDB)

Cet exemple montre comment utiliser dbt avec DuckDB à partir d'une seed Open Data (qualité de l'air), puis ingérer les artefacts dbt dans QALITA.

- **Dossier**: `/home/aleopold/platform/tutorials/integrations/data-engineering/elt/dbt/example_dbt`
- **Base**: DuckDB (fichier `opendata.duckdb` local)
- **Seed**: `seeds/opendata_airquality.csv`
- **Modèles**: `models/staging/stg_airquality.sql`, `models/marts/airquality_metrics.sql`

#### Prérequis

- Python 3.10+
- `make`
- Optionnel: CLI QALITA (`qalita`) dans le PATH pour l'ingestion

#### Démarrage rapide

1. Aller dans l'exemple:
```bash
cd /home/aleopold/platform/tutorials/integrations/data-engineering/elt/dbt/example_dbt
```
2. Créer l'environnement, installer dbt-duckdb, charger la seed, construire et tester:
```bash
make all
```
3. (Optionnel) Ingérer les artefacts dbt dans QALITA:
```bash
make ingest
```

Notes:
- Le `Makefile` configure `DBT_PROFILES_DIR` pour utiliser `profiles.yml` local.
- Les artefacts dbt (`target/manifest.json`, `target/run_results.json`) sont générés par `make run/test`.
- L'ingestion appelle `qalita ingest dbt --manifest target/manifest.json --results target/run_results.json --project opendata_dbt --env dev`.

#### Fichiers clés

- `dbt_project.yml` et `profiles.yml`: configuration du projet et profil DuckDB
- `seeds/opendata_airquality.csv`: échantillon Open Data (qualité de l'air)
- `models/staging/stg_airquality.sql`: nettoyage/typage des mesures
- `models/marts/airquality_metrics.sql`: agrégations (min/max/moyenne, volume)
- `models/schema.yml`: tests basiques (not_null, accepted_values)
- `scripts/ingest_qalita.sh`: ingestion vers QALITA (nécessite la CLI)

#### Personnalisation

- Remplacez `seeds/opendata_airquality.csv` par vos données (mêmes colonnes) et relancez `make seed && make run`.
- Adaptez l'agrégation dans `models/marts/airquality_metrics.sql` à vos KPI.
- Modifiez le projet/env d'ingestion via les variables dans `scripts/ingest_qalita.sh`.
