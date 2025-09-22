## Integration: DataHub ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-datahub.png"/>
</p>

**Goal:** publish QALITA quality assertions, metrics, and links into DataHub so governance users can see quality in context and navigate back to QALITA.

**Overview:**

1. QALITA computes assertions, dataset/field metrics, and issue signals.
2. An integration job uses DataHub APIs (REST/GraphQL) or the Python Emitter to upsert metadata aspects.
3. From DataHub entities, users can open the corresponding dataset or alert views in QALITA via deep links.

This integration is in beta.

**References:**

* Admin integrations: [https://doc.qalita.io/docs/platform/user-guides/admin/integrations](https://doc.qalita.io/docs/platform/user-guides/admin/integrations)
* DataHub docs: [https://datahubproject.io](https://datahubproject.io)

---

### Prerequisites

* A QALITA Platform administrator account.
* Access to your DataHub instance (UI + APIs) and a service principal/token with permission to write metadata aspects (dataset, assertion/ML model where applicable, glossary if used).
* Outbound network egress from QALITA (or your integration worker) to your DataHub GMS endpoint (HTTPS).
* Agreement on the identity mapping between QALITA datasets and DataHub entities (e.g., by platform + name, or by URN mapping).

---

### What data we sync

Core aspects (recommended minimal set):

* Dataset-level quality score (as a Tag/Glossary Term, or in `DatasetProperties.description` prefix) — optional if using Assertions only.
* Assertions as DataHub `Assertion` entities, referencing target dataset/field URNs.
* Run results for assertions (success/failure, last evaluated time, links to QALITA for run details).
* QALITA Link (URL) on the dataset as a `Link` aspect or in `DatasetProperties.externalUrl` when available.

Optional signals:

* Dimension scores (Completeness, Accuracy, Freshness, Consistency, Timeliness) as Tags or a custom aspect.
* Open issues count as a `Tag` or property in a custom aspect.

Identifiers used for mapping:

* QALITA `sourceId` / `datasetId` and, for field-level assertions, `fieldName`.
* DataHub URNs for datasets/fields (e.g., `urn:li:dataset:(urn:li:dataPlatform:snowflake,RETAIL.SALES.DAILY,PROD)`).

---

### Implementation options

* Method A — Scheduled export + DataHub Python Emitter (simple, robust)
* Method B — Push-based updates from a QALITA worker calling DataHub REST/GraphQL (near real-time)

---

### Method A — Scheduled export + DataHub Python Emitter

1. **Define identity mapping (QALITA ↔ DataHub)**

   Provide a mapping so the job can resolve which DataHub URN to update for each QALITA dataset and (optionally) fields.

```yaml
# Example mapping file (YAML)
qalita:
  baseUrl: https://<your-qalita-domain>
  token: <qalita-api-token>

datahub:
  gms: https://<your-datahub-host>/api/gms
  token: <datahub-personal-access-token>

mappings:
  - qalitaDatasetId: retail.sales.daily
    datahub:
      datasetUrn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,RETAIL.SALES.DAILY,PROD)"
      fields:
        - qalitaField: amount
          urn: "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,RETAIL.SALES.DAILY,PROD),amount)"
  - qalitaDatasetId: retail.customers
    datahub:
      lookup:
        platform: snowflake
        name: RETAIL.CUSTOMERS
        env: PROD
```

2. **Configure the export in QALITA**

   * In QALITA: `Settings` > `Integration` > `Catalogs` tab > `DataHub` card.
   * Fill in `GMS endpoint`, token, and upload the mapping file (or configure lookups).
   * Choose a schedule (e.g., hourly) and the set of metrics/assertions to push.

3. **Test connectivity**

```bash
# Check GMS health (requires token if your instance is secured)
curl -H "Authorization: Bearer <datahub-token>" \
  https://<your-datahub-host>/api/health | jq .
```

4. **Emitter example (Python)**

Install dependencies locally for testing:

```bash
pip install acryl-datahub requests pydantic
```

Example script to upsert a dataset link, a tag with score, and an assertion with last run:

```python
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    GlobalTagsClass,
    TagAssociationClass,
)
from datahub.metadata.schema_classes import AssertionInfoClass, AssertionRunEventClass
import requests

GMS = "https://<your-datahub-host>/api/gms"
TOKEN = "<datahub-token>"
QALITA_TOKEN = "<qalita-token>"
QALITA_BASE = "https://<your-qalita-domain>"

emitter = DatahubRestEmitter(GMS, extra_headers={"Authorization": f"Bearer {TOKEN}"})

# Resolve URN
dataset_urn = make_dataset_urn(platform="snowflake", name="RETAIL.SALES.DAILY", env="PROD")

# 1) Upsert dataset properties with external link to QALITA
props = DatasetPropertiesClass(
    name=None,
    description="Quality monitored by QALITA",
    customProperties={
        "qalita.link": f"{QALITA_BASE}/sources/retail.sales.daily",
    },
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(entityUrn=dataset_urn, aspect=props)
)

# 2) Add a tag carrying the overall score (simplest representation)
score_tag = GlobalTagsClass(tags=[TagAssociationClass(tag="urn:li:tag:qalita_score_92")])

emitter.emit_mcp(
    MetadataChangeProposalWrapper(entityUrn=dataset_urn, aspect=score_tag)
)

# 3) Create an assertion and publish a run event
assertion_urn = "urn:li:assertion:(retail.sales.daily,row_count_gt_zero)"
assertion_info = AssertionInfoClass(
    type="ROW_COUNT",
    description="Row count must be greater than zero",
    dataset=dataset_urn,
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(entityUrn=assertion_urn, aspect=assertion_info)
)

run = AssertionRunEventClass(
    assertion=assertion_urn,
    timestampMillis=1737600000000,
    runId="qalita-2025-09-22",
    status="SUCCESS",
    reportUrl=f"{QALITA_BASE}/sources/retail.sales.daily/assertions/row_count_gt_zero",
)

emitter.emit_assertion_run_event(run)

emitter.flush()
print("Emitted sample metadata to DataHub.")
```

Notes:

* In production, generate tags dynamically or prefer a custom aspect to store numeric scores.
* For field assertions, use `schemaField` URNs for targets.

---

### Method B — Real-time push from a QALITA worker

Use this when you need near real-time updates in DataHub after each QALITA measurement or issue change.

1. **Provision API token** for DataHub; capture GMS URL and token.
2. **Configure a QALITA webhook**: `Settings` > `Integration` > `Webhooks` > subscribe to events like `assertion.result`, `quality_score_changed`, `issue.created`.
3. **Implement the worker**:
   * Receive event, resolve mapping, and call DataHub REST/GraphQL to upsert aspects.
   * Optionally emit `AssertionRunEvent` for every evaluation to populate the Assertions UI.

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
* Go to `Settings` > `Integration` > `Catalogs` tab > `DataHub` card.

2. **Fields to fill**

* `GMS endpoint` (e.g., `https://datahub.example.com/api/gms`).
* `Token` (personal access token or bearer token configured for DataHub).
* Optional: TLS verification toggle, HTTP proxy, custom headers.
* `Mapping` (upload YAML/JSON or configure lookups by platform+name+env).
* Schedule (for Method A) or Webhook (for Method B).

3. **Save and test**

* Save the configuration.
* Trigger a one-off sync to validate permissions and aspect availability.

---

### Troubleshooting

* **401/403 Unauthorized/Forbidden:**
  * Verify token validity and that the principal has write permissions for target entities.
  * If using proxies, pass headers end-to-end to GMS.
* **404/400 on aspects:**
  * Ensure target URNs are correct; for field-level updates, use `schemaField` URNs.
  * Ensure aspect classes are supported by your DataHub version; for custom aspects, register schemas.
* **Rate limits or timeouts:**
  * Implement exponential backoff and retries with jitter; batch updates where possible.
* **Stale values:**
  * Confirm the schedule is active and job succeeded; verify last run timestamp in logs.
* **Conflicting writers:**
  * If other pipelines write to the same aspects, coordinate ownership or use deduped upserts.

---

### Security and best practices

* Use a dedicated, least-privileged token for API access.
* Store secrets securely and rotate regularly.
* Prefer idempotent upserts and stable URN mapping.
* Keep an audit log of updates (dataset, values, timestamp, status).

---

### Backend touchpoints

* `app-backend`: export jobs, mapping resolution, and DataHub API/emitter client.


