## Integration: Microsoft Purview ↔ QALITA (Beta)

Goal: annotate Purview assets with QALITA data quality scores and issues.

High-level flow:

1. QALITA exports quality metadata per asset/dataset.
2. Purview Atlas API updates custom attributes/classifications.
3. Users traverse from Purview to QALITA for root cause.

Backend touchpoints:

- `app-backend` export service and identity mapping for assets.

Implementation options:

- Scheduled sync job using Azure credentials
- Event-driven updates for critical changes

Docs references:

- Integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Define Purview custom attribute schema
- Provide sample sync script and Azure app registration steps
- Error handling and throttling


