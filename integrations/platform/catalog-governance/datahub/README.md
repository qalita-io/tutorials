## Integration: DataHub ↔ QALITA (Beta)

Goal: publish QALITA quality assertions and metrics to DataHub for lineage-aware governance.

High-level flow:

1. QALITA emits assertions/metrics for datasets and fields.
2. DataHub ingestion pipeline (REST/Emitter) upserts metadata aspects.
3. Links provide navigation from DataHub entities to QALITA.

Backend touchpoints:

- `app-backend` export endpoints for assertions and metrics.

Implementation options:

- DataHub Python Emitter job reading from QALITA APIs
- Push-based integration from QALITA worker

Docs references:

- Integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Define DataHub aspects mapping (Assertions, DatasetProperties)
- Provide example emitter script
- Establish idempotent URNs mapping


