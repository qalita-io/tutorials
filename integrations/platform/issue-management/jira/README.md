## Integration: Jira ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-jira.png"/>
</p>

Synchronize QALITA data quality issues with Jira for triage and resolution. This guide covers prerequisites, configuration on both sides, field/status mapping, webhooks, and troubleshooting.

### Prerequisites

- A QALITA admin account with access to `Admin → Integrations`.
- Jira Cloud (Atlassian) or self-managed Jira Server/Data Center with admin rights to create API tokens or OAuth apps and webhooks.
- A Jira project where issues will be created/managed and permission to create issues in that project.

### Supported capabilities

- Create/update Jira issues from QALITA issues.
- Two-way sync for status, assignee, title/description, labels (configurable).
- Optional sync of comments between QALITA and Jira.
- Idempotent linking to avoid duplicates per QALITA issue.

### Architecture and flow

1. QALITA detects/updates an issue from rules/checks/metrics and, if configured, creates or updates a corresponding Jira issue.
2. Jira webhooks notify QALITA of changes (status transitions, comments, assignees, fields).
3. QALITA maintains the linkage and state sync between platforms.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` integration endpoints (e.g., `/integrations/jira/*`, `/issues/*`).
- `app-backend/src/backend/database/model/Issue.py` and external reference/link tables.
- Background jobs for retries and rate-limit backoff.

### Permissions and authentication (Jira)

Choose one of the following for outbound API calls from QALITA to Jira:

- API token (Jira Cloud): user email + API token for Basic auth. Permissions inherited from the Jira user who owns the token (must be able to create/update issues in the target project).
- OAuth 2.0 (3LO) app: configure with the required scopes and authorize QALITA. Typical scopes include read/write for issues and metadata. Use this for centralized control and revocation.

For inbound webhooks from Jira to QALITA, use HTTPS and a shared secret/signature if available in your Jira deployment. If secrets are not available, consider restricting by IP allowlist and using a unique webhook URL.

### Step 1 — Configure Jira in QALITA

1. In QALITA, go to `Admin → Integrations → Issue Management → Jira`.
2. Set:
   - Base URL: `https://<your-domain>.atlassian.net` (Jira Cloud) or your self-managed URL.
   - Authentication:
     - For API token: Jira user email and API token.
     - For OAuth: client ID/secret and redirect/callback as required.
   - Default project key: e.g., `DATA`.
   - Issue type: e.g., `Bug` or a custom type you use for data quality.
   - Webhook Secret: a shared secret QALITA will use to validate incoming Jira webhook requests (if supported).
   - Field mapping: configure how QALITA fields map to Jira (see below).
3. Save the configuration.

Notes:

- For per-dataset or per-domain routing, define project mapping rules in QALITA (e.g., by domain, tag, or owner) to choose a different Jira project dynamically.
- If you use custom workflows, ensure status/category mapping is defined (e.g., map QALITA Resolved → a workflow status in the Done category).

### Step 2 — Create a Jira API token (Jira Cloud) or OAuth app

API token (simplest):

1. Visit Atlassian account security: `https://id.atlassian.com/manage-profile/security/api-tokens`.
2. Create a new token (e.g., name it `qalita-integration`).
3. Copy the token and in QALITA set Auth = API token, entering your Jira email and the token.

OAuth 2.0 (optional):

1. Create an OAuth app in Atlassian Developer Console.
2. Add scopes required to create/update issues and read metadata.
3. Set redirect URL to QALITA’s provided callback URL.
4. In QALITA, enter client ID/secret and complete the authorization flow.

### Step 3 — Configure Jira Webhooks

Create a webhook in Jira that points to QALITA.

1. In Jira (Cloud: `Jira settings → System → Webhooks`; Server/DC: `Administration → System → Webhooks`).
2. URL: `https://<your-qalita-host>/api/v2/integrations/jira/webhook`
3. Secret/signature: set the same secret you configured in QALITA (if supported by your Jira version).
4. Events to send:
   - Issue events (created, updated, transitioned, deleted)
   - Comment events (created/updated/deleted) if syncing comments
   - Optional: Assignment/field change events depending on your needs
5. Filters: limit to the target project(s) or JQL such as `project = DATA`.
6. Save webhook. Perform a small change on a test issue to verify QALITA returns `200` and logs the event.

Headers and security:

- QALITA validates the webhook using the configured secret/signature (when available) and rejects mismatches. Always use HTTPS.

### Field and status mapping

Default mapping (customizable in QALITA Admin):

- Title: `"[QALITA] <dataset>: <rule/metric>"`
- Description: includes dataset, rule, current evidence, run links, owners.
- Labels: derived from severity and categories (e.g., `qalita`, `severity:high`, `domain:<name>`).
- Components: optional mapping from QALITA domain/owner to Jira components.
- Assignee: maps from QALITA owner if resolvable to a Jira user; otherwise unassigned.
- Priority: map QALITA severity to Jira priority if desired.
- Status mapping (example):
  - QALITA Open/Active → Jira workflow status in the "To Do" or "In Progress" category
  - QALITA Resolved → Jira workflow status in the "Done" category (e.g., `Done`)
  - QALITA Muted/Ignored → add label `ignored` (configurable) without transitioning

You can override label/component names, map custom fields, and define close criteria per project.

### Sync behavior

- Idempotency: QALITA stores the Jira issue key/reference per QALITA issue to prevent duplicates. If deleted in Jira, QALITA can recreate on next sync (configurable).
- Updates: QALITA is source-of-truth for title/description by default; enable two-way to let Jira edits sync back.
- Comments: bidirectional if enabled. QALITA prefixes system comments to avoid loops.
- Assignees: one-way from QALITA → Jira, or two-way if enabled.
- Labels and components: merged set; QALITA-managed labels may use a reserved prefix to avoid clobbering.

### Rate limits and retries

- QALITA batches updates and applies exponential backoff on HTTP 429/5xx from Jira.
- A background worker retries transient failures; permanent errors are surfaced in Integration Logs.

### Testing the connection

In QALITA `Admin → Integrations → Jira`:

1. Click “Test Connection” to validate credentials and project access.
2. Trigger a change in Jira (e.g., add a comment) to confirm QALITA receives webhook events.
3. From a QALITA issue, click “Create External Issue” and verify it appears in Jira with expected fields.

### Troubleshooting

- 401/403 from Jira: verify API token/email or OAuth token is valid and the user has permissions in the project.
- 404 project/issue type not found: confirm Base URL, project key, and issue type exist and are accessible.
- Webhook unauthorized in QALITA: secret/signature mismatch or wrong URL path. Recheck secret and endpoint.
- Duplicate issues: ensure idempotent linking is enabled and linkage records are intact.
- Comments not syncing: enable comment events in the webhook and check integration logs for filtering rules.
- Rate limiting: reduce update churn (comments/labels), or increase backoff window in QALITA settings.

### API references

- Jira Cloud REST API (Issues)
  - Create: `POST /rest/api/3/issue`
  - Update: `PUT /rest/api/3/issue/{issueIdOrKey}`
  - Comment: `POST /rest/api/3/issue/{issueIdOrKey}/comment`
- QALITA inbound webhook: `POST /api/v2/integrations/jira/webhook`

Example create call (for debugging):

```bash
curl -X POST \
  "https://<your-domain>.atlassian.net/rest/api/3/issue" \
  -H "Authorization: Basic <base64(email:api_token)>" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": { "key": "DATA" },
      "summary": "[QALITA] Example dataset: freshness breach",
      "issuetype": { "name": "Bug" },
      "labels": ["qalita","severity:high","domain:billing"]
    }
  }'
```

### Security considerations

- Store tokens only in QALITA’s encrypted secrets store.
- Rotate tokens regularly and set expiration where supported.
- Use webhook secrets/signatures when available and always use HTTPS.

### Uninstall / disable

- In QALITA, disable the Jira integration or remove credentials to stop outbound sync.
- In Jira, remove the webhook.
- Existing links remain stored; you can sever links per issue from QALITA if needed.

### Related documentation

- Issues UI and workflow: https://doc.qalita.io/docs/platform/user-guides/issues
- Admin integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations



