## Integration: Slack Alerts ← QALITA (Beta)

Goal: send QALITA alerts to Slack channels for rapid awareness and triage.

High-level flow:

1. QALITA triggers alerts on score thresholds or issue lifecycle events.
2. Outbound notifier sends a message via Slack Webhook or Bot token.
3. Messages contain links to issues, sources, and datasets in QALITA.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` notification configuration.
- Worker/service layer for webhook posting and retries.

Implementation options:

- Slack Incoming Webhooks for simple messages
- Slack App with Bot token for threads and interactivity

Docs references:

- Alerts: https://doc.qalita.io/docs/platform/user-guides/alerts
- Admin integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Provide sample message templates
- Support per-project routing and severity-based channels
- Implement retry/backoff strategy


