## Integration: Microsoft Teams Alerts ← QALITA (Beta)

Goal: deliver QALITA alerts to Microsoft Teams channels when scores drop or issues change.

High-level flow:

1. QALITA scoring rules or issue events trigger an alert.
2. A notifier posts a card/message to Teams via Incoming Webhook or Graph API.
3. (Optional) Deep links guide users back to QALITA issue details.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` notifications settings endpoints.
- `app-backend/src/backend/services/` or workers handling outbound webhooks.

Implementation options:

- Configure Teams Incoming Webhook URL per project/team.
- Use Adaptive Cards for richer context and action buttons.

Docs references:

- Alerts: https://doc.qalita.io/docs/platform/user-guides/alerts
- Admin integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Provide Adaptive Card JSON template
- Support message throttling and aggregation windows
- Document environment variable configuration


