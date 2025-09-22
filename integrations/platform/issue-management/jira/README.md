## Integration: Jira ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-jira.png"/>
</p>

Goal: synchronize QALITA data quality issues with Jira for backlog tracking and resolution.

High-level flow:

1. QALITA creates/updates Jira issues based on data quality events and rules.
2. Jira webhooks notify QALITA on transitions, comments, and assignments.
3. QALITA keeps statuses aligned and updates links back to root cause and datasets.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` integration endpoints (e.g., `/integrations/jira/*`, `/issues/*`).
- `app-backend/src/backend/database/model/` for Issue and external references.
- Background workers for retry policies and bulk sync.

Implementation options:

- OAuth/API token configuration for Jira Cloud
- Project/issue type mapping and label strategy

Docs references:

- Issues: https://doc.qalita.io/docs/platform/user-guides/issues
- Admin integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Define custom fields mapping (components, priority)
- Provide example Jira webhook setup
- Document permission scopes required


