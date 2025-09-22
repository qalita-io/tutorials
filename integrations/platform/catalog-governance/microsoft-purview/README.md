## Integration: Microsoft Purview ↔ QALITA (Beta)

<p align="center">
  <img width="800px" height="auto" src="../../../../img/integration/qalita-x-purview.png"/>
</p>

**Goal:** enrich Microsoft Purview with QALITA data quality metrics and deep links so governance users can see quality in context and navigate back to QALITA for details.

This integration is in beta.

**Overview:**

1. QALITA computes dataset/field scores, assertion results, and issue signals.
2. An integration job calls Purview (Apache Atlas compatible) Catalog APIs to upsert Business Metadata and, optionally, Classifications on assets.
3. From Purview assets, users can open the corresponding dataset or alert views in QALITA via deep links.

---

### Prerequisites

* A QALITA Platform administrator account.
* A Microsoft Purview account (Governance) and a service principal (App Registration) with permissions to write to the Catalog.
  - Assign the service principal a Purview role that can edit catalog metadata (e.g., Data Curator) at the appropriate scope.
  - Ensure network egress from QALITA (or your integration worker) to `https://<your-purview-account>.purview.azure.com`.
* Agreement on identity mapping between QALITA datasets and Purview assets (e.g., by qualifiedName or entity GUID).

References:

* Admin integrations: [https://doc.qalita.io/docs/platform/user-guides/admin/integrations](https://doc.qalita.io/docs/platform/user-guides/admin/integrations)
* Purview Catalog (Atlas) API overview: `https://learn.microsoft.com/azure/purview` (search for Catalog/Atlas APIs)

---

### What data we sync

Business Metadata (recommended minimal set):

* Overall Quality Score (Number; 0–100)
* Score Updated At (DateTime)
* Open Issues (Integer)
* SLA Status (Choice: `Good`, `At risk`, `Breached`)
* QALITA Link (URL)

Optional, by dimension:

* Completeness, Accuracy, Freshness, Consistency, Timeliness (Number; 0–100)

Optional classifications:

* `QALITA_AtRisk` classification for highlighting assets with degraded SLA

Identifiers used for mapping:

* QALITA `sourceId` / `datasetId` and, for field-level signals, `fieldName`
* Purview entity `guid` or `qualifiedName` for concrete types (e.g., `azure_sql_table`, `azure_datalake_gen2_path`, `snowflake_table`)

---

### Implementation options

* Method A — Scheduled export + Purview (Atlas) REST API (simple, reliable)
* Method B — Real-time push from a QALITA webhook worker (near real-time)

---

### Method A — Scheduled export + Purview (Atlas) REST API

1) Define the identity mapping (QALITA ↔ Purview)

Provide a mapping so the job can resolve which Purview entity to update for each QALITA dataset.

```yaml
# Example mapping file (YAML)
qalita:
  baseUrl: https://<your-qalita-domain>
  token: <qalita-api-token>

purview:
  account: <your-purview-account> # e.g., mypurview
  tenantId: <tenant-guid>
  clientId: <app-registration-client-id>
  clientSecret: <client-secret>

mappings:
  - qalitaDatasetId: retail.sales.daily
    purview:
      # Option A: reference entity directly by GUID
      guid: 11111111-2222-3333-4444-555555555555
      # Option B: resolve by qualifiedName/type at runtime instead of guid
      resolve:
        typeName: snowflake_table
        qualifiedName: RETAIL.SALES.DAILY@PROD
  - qalitaDatasetId: retail.customers
    purview:
      resolve:
        typeName: azure_sql_table
        qualifiedName: myserver.database.windows.net/mydb/tables/Customers@prod
```

2) Create Business Metadata definition in Purview

In Purview Studio (UI):

* Go to `Management` > `Business metadata` > `+ New` and create a definition named `QALITA` with attributes:
  - `overallScore` (Number)
  - `updatedAt` (Date/Time)
  - `openIssues` (Number)
  - `slaStatus` (Enum: `Good`, `At risk`, `Breached`)
  - `link` (String/URL)
  - Optional: `completeness`, `accuracy`, `freshness`, `consistency`, `timeliness` (Number)

API alternative (if enabled in your tenant):

```bash
PURVIEW=my-purview-account
TOKEN=$(az account get-access-token --resource https://purview.azure.net --query accessToken -o tsv)

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://$PURVIEW.purview.azure.com/api/atlas/v2/types/businessmetadatadef?api-version=2023-09-01 \
  -d '{
    "category": "BUSINESS_METADATA",
    "name": "QALITA",
    "description": "QALITA quality metadata",
    "attributeDefs": [
      {"name": "overallScore", "typeName": "float"},
      {"name": "updatedAt", "typeName": "date"},
      {"name": "openIssues", "typeName": "int"},
      {"name": "slaStatus", "typeName": "string"},
      {"name": "link", "typeName": "string"},
      {"name": "completeness", "typeName": "float"},
      {"name": "accuracy", "typeName": "float"},
      {"name": "freshness", "typeName": "float"},
      {"name": "consistency", "typeName": "float"},
      {"name": "timeliness", "typeName": "float"}
    ]
  }'
```

3) Test connectivity

```bash
PURVIEW=my-purview-account
TOKEN=$(az account get-access-token --resource https://purview.azure.net --query accessToken -o tsv)
curl -H "Authorization: Bearer $TOKEN" \
  https://$PURVIEW.purview.azure.com/api/atlas/v2/types/typedefs?api-version=2023-09-01 | jq .
```

4) Upsert Business Metadata values for an entity

First, resolve the entity `guid` (if you don't have it already):

```bash
TYPE=snowflake_table
QNAME=RETAIL.SALES.DAILY@PROD
curl -G -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "typeName=$TYPE" \
  --data-urlencode "attrName=qualifiedName" \
  --data-urlencode "attrValue=$QNAME" \
  https://$PURVIEW.purview.azure.com/api/atlas/v2/search/attribute?api-version=2023-09-01 | jq .
```

Then, set the `QALITA` business metadata on the entity GUID:

```bash
GUID=11111111-2222-3333-4444-555555555555
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://$PURVIEW.purview.azure.com/api/atlas/v2/entity/guid/$GUID/businessmetadata?api-version=2023-09-01 \
  -d '{
    "QALITA": {
      "overallScore": 92.4,
      "updatedAt": 1737600000000,
      "openIssues": 3,
      "slaStatus": "At risk",
      "link": "https://<your-qalita-domain>/sources/retail.sales.daily",
      "completeness": 98.7
    }
  }'
```

Optional: add a classification for visibility in Purview UI facets:

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://$PURVIEW.purview.azure.com/api/atlas/v2/entity/guid/$GUID/classifications?api-version=2023-09-01 \
  -d '{ "classification": { "typeName": "QALITA_AtRisk" } }'
```

5) Sample emitter (Python) — client credentials

```python
from azure.identity import ClientSecretCredential
import requests

TENANT_ID = "<tenant-id>"
CLIENT_ID = "<client-id>"
CLIENT_SECRET = "<client-secret>"
PURVIEW_ACCOUNT = "my-purview-account"

credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
token = credential.get_token("https://purview.azure.net/.default").token

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
})

guid = "11111111-2222-3333-4444-555555555555"
payload = {
    "QALITA": {
        "overallScore": 92.4,
        "updatedAt": 1737600000000,
        "openIssues": 3,
        "slaStatus": "At risk",
        "link": "https://<your-qalita-domain>/sources/retail.sales.daily",
    }
}

url = f"https://{PURVIEW_ACCOUNT}.purview.azure.com/api/atlas/v2/entity/guid/{guid}/businessmetadata?api-version=2023-09-01"
resp = session.post(url, json=payload, timeout=30)
resp.raise_for_status()
print("Upserted QALITA business metadata to Purview entity", guid)
```

Notes:

* Use millisecond epoch for date/time attributes when required by your Atlas API version.
* For field-level assertions, target `schema` or `column` entities where applicable and attach the same business metadata subset.
* Prefer idempotent upserts and reconcile on each run.

---

### Method B — Real-time push from a QALITA webhook worker

Use this when you need near real-time updates in Purview after each QALITA measurement or issue change.

1. Provision the Azure AD app (client credentials) with Catalog write permissions and assign a Purview role (e.g., Data Curator).
2. In QALITA, configure a webhook: `Settings` > `Integration` > `Webhooks` > subscribe to events like `quality_score_changed`, `assertion.result`, `issue.created`.
3. Implement the worker to resolve mapping and call the Purview Atlas API to upsert Business Metadata and optional Classifications.

Example QALITA event payload:

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

1. Access the integration page

* Log in as administrator.
* Go to `Settings` > `Integration` > `Catalogs` tab > `Microsoft Purview` card.

2. Fields to fill

* `Purview account` (e.g., `mypurview`).
* `Tenant ID`, `Client ID`, `Client Secret` for the Azure AD app.
* Optional: TLS verification toggle, HTTP proxy, custom headers.
* `Mapping` (upload YAML/JSON or configure lookups by typeName + qualifiedName).
* Schedule (for Method A) or Webhook (for Method B).

3. Save and test

* Save the configuration.
* Trigger a one-off sync to validate permissions and API access.

---

### Troubleshooting

* **401/403 Unauthorized/Forbidden:**
  * Verify AAD app credentials and that the principal has a Purview role permitting writes (e.g., Data Curator) at the correct scope.
  * Ensure token audience/scope is `https://purview.azure.net/.default` or resource `https://purview.azure.net` (for Azure CLI token).
* **404/400 on business metadata:**
  * Confirm the `QALITA` Business Metadata definition exists and is attached to the asset types you target.
  * Check entity type and `guid`/`qualifiedName` are correct; for columns, use the appropriate entity type.
* **Rate limits or timeouts:**
  * Implement exponential backoff with jitter; batch updates where possible.
* **Stale values:**
  * Confirm the schedule is active and jobs succeeded; verify last run timestamp.
* **Conflicting writers:**
  * Coordinate ownership if other pipelines update the same Business Metadata or classifications.

---

### Security and best practices

* Use a dedicated, least-privileged Azure AD app; assign only the necessary Purview role.
* Store secrets in a secure secret store and rotate regularly.
* Prefer Business Metadata over free-text attributes for typed fields.
* Keep an audit log of updates (asset, values, timestamp, status).

---

### Backend touchpoints

* `app-backend`: export jobs, mapping resolution, and Purview (Atlas) API client.

