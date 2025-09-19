## Integration: Grafana ← QALITA (Draft)

Goal: monitor QALITA metrics and alerts in Grafana.

High-level flow:

1. Expose QALITA metrics via a time-series store or HTTP API.
2. Grafana panels query these sources to visualize score trends and issue counts.
3. Alert rules in Grafana or QALITA notify on thresholds.

Backend touchpoints:

- `app-backend` export endpoints or metrics push to TSDB (e.g., Prometheus-compatible)

Implementation options:

- JSON API datasource pointing to QALITA read APIs
- Prometheus exposition if enabled

Docs references:

- Reporting/Monitoring: https://doc.qalita.io/docs/platform/user-guides/reporting

Next steps:

- Provide Grafana dashboard JSON
- Define time-series schema and labels
- Document auth headers for JSON API datasource


