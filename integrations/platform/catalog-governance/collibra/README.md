## Integration: Collibra ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-collibra.png"/>
</p>

**Goal:** enrich Collibra with QALITA data quality metrics and provide deep links back to datasets and alerts in QALITA.

**Overview:**

1. QALITA computes and exposes dataset quality scores and issue signals.
2. An integration job (scheduled or event-driven) calls Collibra APIs to update asset attributes and, optionally, relations.
3. From Collibra, users can open the corresponding dataset, source, or alerts directly in QALITA.

This integration is in beta.

**References:**

* Admin integrations: [https://doc.qalita.io/docs/platform/user-guides/admin/integrations](https://doc.qalita.io/docs/platform/user-guides/admin/integrations)

---

### Prerequisites

* A QALITA Platform administrator account.
* Collibra DGC base URL and API credentials for a least-privileged service account with permission to read/write attributes on the target asset types/domains.
* Outbound network egress from QALITA (or your integration worker) to your Collibra URL (HTTPS).
* Agreement on which Collibra asset type(s) represent data sets (e.g., `Table`, `Dataset`, or a custom type) and which Domain(s) they live in.

---

### What data we sync

Attributes (recommended minimal set):

* Overall Quality Score (Number; 0–100)
* Score Updated At (DateTime)
* Open Issues (Integer)
* SLA Status (Choice: `Good`, `At risk`, `Breached`)
* QALITA Link (URL)

Optional attributes (by dimension):

* Completeness, Accuracy, Freshness, Consistency, Timeliness (Number; 0–100)

Relations (optional):

* Link asset to a “Monitored by QALITA” system or steward group

Identifiers used for mapping:

* QALITA `sourceId`/`datasetId`
* Collibra `assetId` (or name+domain)

---

### Implementation options

* Method A — Scheduled export + Collibra REST API (simple, reliable)
* Method B — Real-time update via webhook worker (near real-time)

---

### Method A — Scheduled export + Collibra REST API

1. **Create attribute types in Collibra**

   In Collibra, as an administrator: `Settings` > `Type System`.

   * Under the target asset type (e.g., `Table`/`Dataset`), add these Attribute Types:
     - `QALITA Quality Score` (Data type: Number)
     - `QALITA Score Updated At` (Data type: Date/Time)
     - `QALITA Open Issues` (Data type: Integer)
     - `QALITA SLA Status` (Data type: Choice with values: Good, At risk, Breached)
     - `QALITA Link` (Data type: Hyperlink/URL)
     - Optional: `QALITA Completeness`, `QALITA Accuracy`, `QALITA Freshness`, `QALITA Consistency`, `QALITA Timeliness` (Number)

   Capture each Attribute Type ID (or keep the names consistent for lookups).

2. **Define dataset mapping (QALITA ↔ Collibra)**

   Provide a mapping so the job can resolve which Collibra asset to update for each QALITA dataset.

```yaml
# Example mapping file (YAML)
collibra:
  baseUrl: https://<your-collibra-host>
  auth:
    username: <service-account>
    password: <secret>
  # Alternative: personal access token or OAuth2 client credentials

assets:
  - qalitaDatasetId: retail.sales.daily
    collibra:
      assetId: 11111111-2222-3333-4444-555555555555
  - qalitaDatasetId: retail.customers
    collibra:
      lookup:
        name: Customers
        domainId: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

3. **Configure the export job in QALITA**

   * In QALITA: `Settings` > `Integration` > `Catalogs` tab > `Collibra` card.
   * Fill in `Base URL`, credentials, and upload the mapping file (or configure lookups).
   * Choose a schedule (e.g., hourly) and the set of metrics to push.

4. **Test connectivity**

```bash
curl -u <user>:<pass> \
  -H 'Accept: application/json' \
  https://<your-collibra-host>/rest/2.0/system | jq .
```

5. **Run a dry run for one dataset**

   From QALITA, trigger `Sync now` for a single dataset and inspect the job log.

6. **Collibra REST examples (attribute upsert)**

Create or update attribute values for a known `assetId` and `attributeTypeId`:

```bash
# Create attribute (if not present)
curl -u <user>:<pass> -H 'Content-Type: application/json' \
  -d '{
    "assetId": "11111111-2222-3333-4444-555555555555",
    "typeId": "<score-attribute-type-id>",
    "value": "92.4"
  }' \
  https://<your-collibra-host>/rest/2.0/attributes

# List attributes on the asset to find existing IDs
curl -u <user>:<pass> \
  "https://<your-collibra-host>/rest/2.0/attributes?assetId=11111111-2222-3333-4444-555555555555"

# Update an existing attribute by ID
curl -u <user>:<pass> -X PUT -H 'Content-Type: application/json' \
  -d '{"value": "93.1"}' \
  https://<your-collibra-host>/rest/2.0/attributes/<attributeId>
```

Example payload the exporter sends for each dataset:

```json
{
  "assetId": "11111111-2222-3333-4444-555555555555",
  "attributes": [
    { "type": "QALITA Quality Score", "value": 92.4 },
    { "type": "QALITA Score Updated At", "value": "2025-09-22T08:15:00Z" },
    { "type": "QALITA Open Issues", "value": 3 },
    { "type": "QALITA SLA Status", "value": "At risk" },
    { "type": "QALITA Link", "value": "https://<your-qalita-domain>/sources/retail.sales.daily" },
    { "type": "QALITA Completeness", "value": 98.7 }
  ]
}
```

---

### Method B — Real-time update via webhook worker

Use this when you need near real-time updates in Collibra after each QALITA measurement or issue change.

1. **Create/confirm attribute types** as in Method A.
2. **Provision API credentials** in Collibra for the worker.
3. **Configure a QALITA webhook**: `Settings` > `Integration` > `Webhooks` > subscribe to events like `quality_score_changed`, `issue.created`, `issue.updated`.
4. **Implement the worker**:
   * Receive event, resolve mapping, and call Collibra REST to upsert attributes.
   * Optionally post a Collibra comment/task if SLA is `Breached`.

Example event payload from QALITA:

```json
{
  "event": "quality_score_changed",
  "sourceId": "retail.sales.daily",
  "scores": { "overall": 92.4, "completeness": 98.7 },
  "issues": { "open": 3 },
  "urls": {
    "dataset": "https://<your-qalita-domain>/sources/retail.sales.daily",
    "alerts": "https://<your-qalita-domain>/home/data-management/alerts"
  },
  "measuredAt": "2025-09-22T08:15:00Z"
}
```

---

### Configuration in QALITA Platform

1. **Access the integration page**

* Log in as administrator.
* Go to `Settings` > `Integration` > `Catalogs` tab > `Collibra` card.

2. **Fields to fill**

* `Base URL` (e.g., `https://collibra.example.com`).
* `Username` and `Password` (or token, depending on your Collibra setup).
* Optional: TLS verification toggle, HTTP proxy, custom headers.
* `Mapping` (upload YAML/JSON or configure lookups by name+domain).
* Schedule (for Method A) or Webhook (for Method B).

3. **Save and test**

* Save the configuration.
* Trigger a one-off sync to validate permissions and attribute availability.

---

### Troubleshooting

* **401/403 Unauthorized/Forbidden:**
  * Verify credentials, user role, and that the service account can write attributes on the target asset type and domain.
  * If using OAuth or PAT, ensure token audience/scope and expiry are correct.
* **404/400 on attributes:**
  * Attribute Type name/ID must exist and be attached to the asset type. Ensure the attribute type is allowed for that asset type.
  * For updates, confirm you target the correct `attributeId`.
* **Asset not found:**
  * Check mapping; if using name+domain lookups, ensure exact match and correct `domainId`.
* **Rate limits or timeouts:**
  * Implement exponential backoff and retries with jitter; batch updates where possible.
* **Stale values:**
  * Confirm the schedule is active and job succeeded; verify the last run timestamp.

---

### Security and best practices

* Use a dedicated, least-privileged service account for API access.
* Store credentials in a secure secret store; rotate regularly.
* Restrict the attribute types to only those needed; avoid overexposing data.
* Keep an audit log of updates (dataset, values, timestamp, status).

---

### Appendix — Useful API calls and examples

Check system and user:

```bash
curl -u <user>:<pass> https://<your-collibra-host>/rest/2.0/system | jq .
curl -u <user>:<pass> https://<your-collibra-host>/rest/2.0/user/me | jq .
```

Find assets by name:

```bash
curl -u <user>:<pass> \
  "https://<your-collibra-host>/rest/2.0/assets?name=Sales%20Daily&domainId=<domainId>" | jq .
```

Find attribute types by name:

```bash
curl -u <user>:<pass> \
  "https://<your-collibra-host>/rest/2.0/attributeTypes?name=QALITA%20Quality%20Score" | jq .
```

---

Backend touchpoints:

* `app-backend`: export jobs, mapping resolution, and Collibra API client.

