## Integration: Collibra ↔ QALITA (Beta)

Goal: enrich Collibra with QALITA data quality metrics and link back to datasets.

High-level flow:

1. QALITA exports dataset quality scores and issues.
2. Collibra import/API updates asset attributes and relations.
3. Users navigate from catalog assets to QALITA details.

Backend touchpoints:

- `app-backend` export jobs and mapping of datasets to catalog IDs.

Implementation options:

- Scheduled export + Collibra Import API
- Real-time update via webhook worker

Docs references:

- Integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Define attribute schema in Collibra for scores and SLAs
- Provide mapping config file
- Document error handling and retries


