"""
Minimal Airbyte → QALITA adapter service

Receives Airbyte webhook events and forwards computed schemas/metrics
and job status to QALITA Platform APIs.

Environment variables:
  - QALITA_BASE_URL: e.g. http://localhost:8000
  - QALITA_USERNAME / QALITA_PASSWORD: service account credentials
  - ADAPTER_CONFIG_PATH: path to JSON config mapping connectionId→QALITA ids (default: /config/config.json)

Run:
  uvicorn app:app --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional, List
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel


class QalitaIds(BaseModel):
    source_id: int
    source_version_id: int
    pack_id: int
    pack_version_id: int


class AdapterConfig(BaseModel):
    # Map Airbyte connectionId to QALITA identifiers
    connection_map: Dict[str, QalitaIds] = {}
    # Optional defaults if no mapping found
    default: Optional[QalitaIds] = None


class QalitaClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._token: Optional[str] = None

    async def _ensure_token(self, client: httpx.AsyncClient) -> None:
        if self._token is not None:
            return
        data = {
            "username": self.username,
            "password": self.password,
        }
        resp = await client.post(
            f"{self.base_url}/api/v1/auth/signin",
            data=data,
            timeout=30.0,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Failed to sign in to QALITA: {resp.text}")
        payload = resp.json()
        self._token = payload.get("access_token")
        if not self._token:
            raise HTTPException(status_code=500, detail="No access_token returned by QALITA")

    def _auth_headers(self) -> Dict[str, str]:
        if not self._token:
            raise RuntimeError("Token not initialized")
        return {"Authorization": f"Bearer {self._token}"}

    async def upload_metrics(
        self,
        client: httpx.AsyncClient,
        ids: QalitaIds,
        metrics: List[Dict[str, Any]],
    ) -> None:
        await self._ensure_token(client)
        files = {
            # Send metrics as a JSON array file
            "file": ("metrics.json", json.dumps(metrics), "application/json"),
        }
        data = {
            "source_id": str(ids.source_id),
            "source_version_id": str(ids.source_version_id),
            "pack_id": str(ids.pack_id),
            "pack_version_id": str(ids.pack_version_id),
        }
        resp = await client.post(
            f"{self.base_url}/api/v1/metrics/upload",
            headers=self._auth_headers(),
            files=files,
            data=data,
            timeout=60.0,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Metric upload failed: {resp.text}")

    async def upload_schemas(
        self,
        client: httpx.AsyncClient,
        ids: QalitaIds,
        schemas: List[Dict[str, Any]],
    ) -> None:
        await self._ensure_token(client)
        files = {
            "file": ("schemas.json", json.dumps(schemas), "application/json"),
        }
        data = {
            "source_id": str(ids.source_id),
            "source_version_id": str(ids.source_version_id),
            "pack_id": str(ids.pack_id),
            "pack_version_id": str(ids.pack_version_id),
        }
        resp = await client.post(
            f"{self.base_url}/api/v1/schemas/upload",
            headers=self._auth_headers(),
            files=files,
            data=data,
            timeout=60.0,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Schema upload failed: {resp.text}")

    async def create_or_update_job(
        self,
        client: httpx.AsyncClient,
        ids: QalitaIds,
        name: Optional[str],
        status: Optional[str],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> None:
        await self._ensure_token(client)
        # Create a Job row for observability purposes
        payload: Dict[str, Any] = {
            "source_id": ids.source_id,
            "pack_id": ids.pack_id,
        }
        if status:
            payload["status"] = status
        if name:
            payload["name"] = name
        if start_dt:
            payload["start_date"] = start_dt.isoformat()
        if end_dt:
            payload["end_date"] = end_dt.isoformat()

        resp = await client.post(
            f"{self.base_url}/api/v2/jobs",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            content=json.dumps(payload),
            timeout=30.0,
        )
        # Accept 200/201
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=resp.status_code, detail=f"Job create failed: {resp.text}")


def load_config() -> AdapterConfig:
    path = os.getenv("ADAPTER_CONFIG_PATH", "/config/config.json")
    if not os.path.exists(path):
        # Allow running without config for quick tests
        return AdapterConfig()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize keys to strings
    conn_map = {str(k): v for k, v in data.get("connection_map", {}).items()}
    default = data.get("default")
    return AdapterConfig(connection_map=conn_map, default=default)


def pick_ids(cfg: AdapterConfig, connection_id: Optional[str]) -> QalitaIds:
    if connection_id and connection_id in cfg.connection_map:
        return QalitaIds(**cfg.connection_map[connection_id])
    if cfg.default is not None:
        return QalitaIds(**cfg.default)
    raise HTTPException(status_code=400, detail="No QALITA id mapping found for connection and no default provided")


def extract_metrics_from_airbyte(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    # Best-effort extraction across Airbyte OSS/Cloud payloads
    job = event.get("job", {})
    attempt = event.get("attempt", {})
    stats = attempt.get("totalStats", {}) or attempt.get("syncStats", {}) or {}

    def add_metric(key: str, value: Any, scope: Optional[Dict[str, Any]] = None) -> None:
        metrics.append({"key": key, "value": str(value), "scope": scope or {}})

    # Row counts
    if "recordsEmitted" in stats:
        add_metric("records_emitted", stats.get("recordsEmitted", 0))
    if "bytesEmitted" in stats:
        add_metric("bytes_emitted", stats.get("bytesEmitted", 0))
    if "recordsCommitted" in stats:
        add_metric("records_committed", stats.get("recordsCommitted", 0))

    # Duration and success
    status = job.get("status") or attempt.get("status")
    if status:
        add_metric("status", status)
    start_ts = attempt.get("startedAt") or job.get("startedAt")
    end_ts = attempt.get("endedAt") or job.get("endedAt")
    if start_ts and end_ts and isinstance(start_ts, (int, float)) and isinstance(end_ts, (int, float)):
        duration_s = max(0, (int(end_ts) - int(start_ts)) / 1000.0)
        add_metric("duration_seconds", duration_s)

    return metrics


def extract_schemas_from_airbyte(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    schemas: List[Dict[str, Any]] = []
    # Attempt to parse catalog/streams if provided
    catalog = event.get("catalog") or event.get("syncedCatalog") or {}
    streams = catalog.get("streams", [])
    for stream in streams:
        stream_name = stream.get("stream", {}).get("name") or stream.get("name")
        json_schema = stream.get("stream", {}).get("jsonSchema") or stream.get("jsonSchema") or {}
        properties = json_schema.get("properties", {})
        for col_name, col_schema in properties.items():
            dtype = col_schema.get("type")
            # Store one line per column
            schemas.append(
                {
                    "key": f"{stream_name}.{col_name}",
                    "value": str(dtype),
                    "scope": {"stream": stream_name, "column": col_name},
                }
            )
    return schemas


def parse_dt(ms: Optional[int]) -> Optional[datetime]:
    if ms is None:
        return None
    try:
        # Airbyte timestamps are often in millis
        return datetime.utcfromtimestamp(int(ms) / 1000.0)
    except Exception:
        return None


app = FastAPI(title="QALITA Airbyte Adapter")


@app.post("/airbyte/webhook")
async def airbyte_webhook(req: Request) -> Dict[str, Any]:
    try:
        body = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    # Identify connection id
    connection_id = (
        body.get("connection", {}).get("connectionId")
        or body.get("connectionId")
        or body.get("connection_id")
    )

    cfg = load_config()
    ids = pick_ids(cfg, str(connection_id) if connection_id is not None else None)

    qalita = QalitaClient(
        base_url=os.getenv("QALITA_BASE_URL", "http://localhost:8000"),
        username=os.getenv("QALITA_USERNAME", "admin"),
        password=os.getenv("QALITA_PASSWORD", "admin"),
    )

    async with httpx.AsyncClient() as client:
        # 1) Upload schemas (if any)
        schemas = extract_schemas_from_airbyte(body)
        if schemas:
            await qalita.upload_schemas(client, ids, schemas)

        # 2) Upload metrics
        metrics = extract_metrics_from_airbyte(body)
        if metrics:
            await qalita.upload_metrics(client, ids, metrics)

        # 3) Create job record for the run
        job = body.get("job", {})
        attempt = body.get("attempt", {})
        status = job.get("status") or attempt.get("status")
        name = job.get("name") or f"Airbyte connection {connection_id}"
        start_dt = parse_dt(attempt.get("startedAt") or job.get("startedAt"))
        end_dt = parse_dt(attempt.get("endedAt") or job.get("endedAt"))
        await qalita.create_or_update_job(
            client,
            ids,
            name=name,
            status=status,
            start_dt=start_dt,
            end_dt=end_dt,
        )

    return {"ok": True}


