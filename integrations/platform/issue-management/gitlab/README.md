## Integration: GitLab Issues ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-gitlab.png"/>
</p>

Synchronize QALITA data quality issues with GitLab for triage and resolution. This guide covers prerequisites, configuration on both sides, field/status mapping, webhooks, and troubleshooting.

### Prerequisites

- A QALITA admin account with access to `Admin → Integrations`.
- GitLab.com or self-managed GitLab with permission to create Personal Access Tokens (PAT) for the target group/project.
- GitLab project(s) where issues will be created/managed.

### Supported capabilities

- Create/update GitLab issues from QALITA issues.
- Two-way sync for status, assignee, title/description, labels (configurable).
- Sync comments/notes between QALITA and GitLab (optional).
- Idempotent linking to avoid duplicates per QALITA issue.

### Architecture and flow

1. QALITA detects/updates an issue from rules/checks/metrics and, if configured, creates or updates a corresponding GitLab issue.
2. GitLab webhooks notify QALITA of changes (status transitions, comments, assignees, labels).
3. QALITA maintains the linkage and state sync between platforms.

Backend touchpoints:

- `app-backend/src/backend/routers/v2/` integration endpoints (e.g., `/integrations/gitlab/*`, `/issues/*`).
- `app-backend/src/backend/database/model/Issue.py` and external reference/link tables.
- Background jobs for retries and rate-limit backoff.

### Permissions and scopes (GitLab PAT)

- Scope: `api` (required to create/update issues and read project metadata).
- Token owner must have at least `Reporter` (read) and typically `Developer` access in target project(s) to create and edit issues.
- For self-managed GitLab, ensure the PAT is valid in Admin Mode if required by your instance policies.

### Step 1 — Configure GitLab in QALITA

1. In QALITA, go to `Admin → Integrations → Issue Management → GitLab`.
2. Set:
   - Base URL: `https://gitlab.com` or your self-managed URL, e.g., `https://gitlab.example.com`.
   - Personal Access Token (PAT) with `api` scope.
   - Default project: the GitLab project ID or path (e.g., `group/subgroup/project`).
   - Webhook Secret: a shared secret QALITA will use to validate GitLab webhook requests.
   - Field mapping: configure how QALITA fields map to GitLab (see below).
3. Save the configuration.

Notes:

- For per-dataset or per-domain routing, define project mapping rules in QALITA (e.g., by domain, tag, or owner) to choose a different GitLab project dynamically.

### Step 2 — Create a GitLab Personal Access Token

1. In GitLab, go to `User → Edit profile → Access Tokens` (or `Group → Settings → Access Tokens` for group-scoped tokens).
2. Create a token with scope `api`. Set an appropriate expiration and name (e.g., `qalita-integration`).
3. Copy the token and paste it into QALITA’s GitLab integration settings.

### Step 3 — Configure GitLab Webhooks

Create a webhook in each target project (or at the group level) pointing to QALITA.

1. In GitLab, go to `Project → Settings → Webhooks`.
2. URL: `https://<your-qalita-host>/api/v2/integrations/gitlab/webhook`
3. Secret Token: use the exact value configured in QALITA.
4. Trigger events:
   - Issues events (required)
   - Note events (enable if syncing comments)
   - Optional: Confidential issues if you plan to use them
5. SSL verification: keep enabled unless using a dev/staging environment with self-signed certs.
6. Add webhook and click “Test” → “Issues events”. Verify QALITA returns `200`.

Headers and security:

- GitLab sends the secret via `X-Gitlab-Token`. QALITA rejects requests if the token mismatch occurs.

### Field and status mapping

Default mapping (can be customized in QALITA Admin):

- Title: `"[QALITA] <dataset>: <rule/metric>"`
- Description: includes dataset, rule, current evidence, run links, owners.
- Labels: derived from severity and categories (e.g., `qalita`, `severity:high`, `domain:<name>`).
- Assignee: maps from QALITA owner if resolvable to a GitLab user; otherwise unassigned.
- Status:
  - QALITA Open/Active → GitLab `opened`
  - QALITA Resolved → GitLab `closed`
  - QALITA Muted/Ignored → label `ignored` (configurable) without closing by default

You can override label names, add components/areas as labels, and define custom close criteria.

### Sync behavior

- Idempotency: QALITA stores the GitLab issue reference per QALITA issue to prevent duplicates. If deleted in GitLab, QALITA can recreate on next sync (configurable).
- Updates: QALITA is source-of-truth for title/description by default; enable “two-way” to let GitLab edits sync back.
- Comments: bidirectional if enabled. QALITA prefixes system comments to avoid loops.
- Assignees: optional one-way from QALITA → GitLab, or two-way if enabled.
- Labels: merged set; QALITA-managed labels use a reserved prefix (e.g., `qalita/*`) to avoid clobbering.

### Rate limits and retries

- QALITA batches updates and applies exponential backoff on HTTP 429/5xx.
- A background worker retries transient failures; permanent errors are surfaced in the Integration Logs.

### Testing the connection

In QALITA `Admin → Integrations → GitLab`:

1. Click “Test Connection” to validate PAT and project access.
2. Use “Send Test Webhook” in GitLab to confirm QALITA receives events.
3. From a QALITA issue, click “Create External Issue” and verify it appears in GitLab with expected fields.

### Troubleshooting

- 401/403 from GitLab: verify PAT is valid, has `api` scope, and the token owner has access to the project.
- 404 project not found: confirm Base URL correctness and project path/ID.
- Webhook 401/403 in QALITA: mismatch `X-Gitlab-Token` or wrong URL path. Recheck secret and endpoint.
- Duplicate issues: ensure idempotent linking is enabled and that the linkage table was not purged.
- Comments not syncing: enable Note events on the webhook and check integration logs for filtering rules.
- Rate limiting: reduce comment/label churn, or increase backoff window in QALITA settings.

### API references

- GitLab Issues API
  - Create: `POST /projects/:id/issues`
  - Update: `PUT /projects/:id/issues/:issue_iid`
  - Notes: `POST /projects/:id/issues/:issue_iid/notes`
- QALITA inbound webhook: `POST /api/v2/integrations/gitlab/webhook`

Example create call (for debugging):

```bash
curl -X POST \
  "https://gitlab.com/api/v4/projects/<PROJECT_ID>/issues" \
  -H "PRIVATE-TOKEN: <PAT>" \
  --data-urlencode "title=[QALITA] Example dataset: freshness breach" \
  --data-urlencode "description=See QALITA for details: https://<qalita-host>/issues/<id>" \
  --data-urlencode "labels=qalita,severity:high,domain:billing"
```

### Security considerations

- Store PATs only in QALITA’s encrypted secrets store.
- Rotate tokens regularly and set expiration.
- Use Webhook Secret and HTTPS. For self-managed instances, ensure valid TLS.

### Uninstall / disable

- In QALITA, disable the GitLab integration or remove PAT to stop outbound sync.
- In GitLab, remove project/group webhooks.
- Existing links remain stored; you can sever links per issue from QALITA if needed.

### Related documentation

- Issues UI and workflow: https://doc.qalita.io/docs/platform/user-guides/issues
- Admin integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

---

If you need help, contact your QALITA administrator or support.
