## Integration: Airbyte → QALITA (Beta)

Goal: push Airbyte connection sync metadata and optional validation results into QALITA.

High-level flow:

1. Airbyte sync runs emit connection/job events.
2. A webhook or post-sync task calls `app-backend` to record:
   - Source/stream schemas and changes
   - Row counts and basic freshness metrics
   - Optional validation outcomes (pre/post-load checks)
3. QALITA persists and computes data quality scores and issues.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` ingestion endpoints (sources, datasets, runs, metrics, issues).
- `app-backend/src/backend/database/model/` for entities such as Source, Dataset, Job, Metric.

Implementation options:

- Airbyte webhook to a QALITA endpoint with a small adapter service.
- Post-sync script using QALITA CLI to push metrics and schema snapshots.

Docs references:

- Platform quick start: https://doc.qalita.io/docs/platform/quick-start
- Sources: https://doc.qalita.io/docs/platform/user-guides/admin/sources
- CLI quick start: https://doc.qalita.io/docs/cli/quick-start

Next steps:

- Define minimal payload schema for connection runs ✅
- Provide example Docker Compose with QALITA adapter ✅
- Map Airbyte stream to QALITA dataset identity ✅ (via adapter config)

Setup:

1) Build and run the adapter

```bash
cd tutorials/integrations/data-engineering/elt/airbyte
docker compose build qalita-airbyte-adapter
docker compose up -d qalita-airbyte-adapter
```

2) Configure Airbyte webhook

- Set the webhook URL to `http://host.docker.internal:8080/airbyte/webhook` (or your adapter host)
- Airbyte will POST job/run events to this endpoint

3) Map Airbyte connection to QALITA identifiers

- Edit `config/config.json` with your `connectionId` and the corresponding QALITA `source_id`, `source_version_id`, `pack_id`, `pack_version_id`.

Adapter responsibilities:

- Receives Airbyte events and extracts:
  - Schemas: one entry per stream.column → stored in `schema.key/value/scope`
  - Metrics: `records_emitted`, `bytes_emitted`, `records_committed`, `duration_seconds`, `status`
  - Job: creates a `job` row with status, start/end timestamps for observability

QALITA API touchpoints used:

- `POST /api/v1/schemas/upload` with multipart file `schemas.json` and `SchemaBase` form fields
- `POST /api/v1/metrics/upload` with multipart file `metrics.json` and `MetricBase` form fields
- `POST /api/v2/jobs` with `JobCreate`

Example Airbyte webhook payload:

```12:999:tutorials/integrations/data-engineering/elt/airbyte/examples/airbyte_webhook_payload.json
{
  "connection": {
    "connectionId": "your-airbyte-connection-id"
  },
  "job": {
    "id": 1234,
    "status": "succeeded",
    "startedAt": 1716480000000,
    "endedAt": 1716480123000,
    "name": "Daily sync: shopify → warehouse"
  },
  ...
}
```

Adapter config example:

```12:999:tutorials/integrations/data-engineering/elt/airbyte/config/config.json
{
  "connection_map": {
    "your-airbyte-connection-id": {
      "source_id": 1,
      "source_version_id": 1,
      "pack_id": 1,
      "pack_version_id": 1
    }
  },
  "default": {
    "source_id": 1,
    "source_version_id": 1,
    "pack_id": 1,
    "pack_version_id": 1
  }
}
```

Authentication:

- The adapter signs in to QALITA using `QALITA_USERNAME`/`QALITA_PASSWORD` via `POST /api/v1/auth/signin` and stores the bearer token for subsequent calls.

Notes:

- Ensure the referenced `source_id`, `pack_id` and their versions exist in QALITA. You can create sources via `POST /api/v1/sources/publish` and manage packs in the UI.
- If your Airbyte payload contains a catalog, the adapter will post schemas; otherwise only metrics and job will be created.


