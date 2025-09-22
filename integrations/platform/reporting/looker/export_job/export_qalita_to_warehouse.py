import os
import time
import math
import logging
from datetime import datetime, timezone

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("qalita_export")


def get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def make_engine() -> Engine:
    url = get_env("WAREHOUSE_URL", required=True)
    engine = create_engine(url, pool_pre_ping=True, future=True)
    schema = os.getenv("WAREHOUSE_SCHEMA")
    if schema:
        with engine.connect() as conn:
            conn.execute(text(f"set search_path to {schema}"))
    return engine


def get_headers() -> dict:
    token = get_env("QALITA_API_TOKEN", required=True)
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def paginate(endpoint: str, params: dict, batch_size: int):
    page = 0
    while True:
        page_params = params | {"offset": page * batch_size, "limit": batch_size}
        resp = requests.get(endpoint, headers=get_headers(), params=page_params, timeout=60)
        resp.raise_for_status()
        items = resp.json() or []
        if not items:
            break
        yield items
        if len(items) < batch_size:
            break
        page += 1


def upsert_metrics(engine: Engine, rows: list[dict]):
    if not rows:
        return
    sql = text(
        """
        insert into qalita_metrics (id, partner_id, created_at, updated_at, key, value,
                                    source_id, source_version_id, pack_id, pack_version_id, scope)
        values (:id, :partner_id, :created_at, :updated_at, :key, :value,
                :source_id, :source_version_id, :pack_id, :pack_version_id, cast(:scope as jsonb))
        on conflict (id) do update set
          partner_id = excluded.partner_id,
          created_at = excluded.created_at,
          updated_at = excluded.updated_at,
          key = excluded.key,
          value = excluded.value,
          source_id = excluded.source_id,
          source_version_id = excluded.source_version_id,
          pack_id = excluded.pack_id,
          pack_version_id = excluded.pack_version_id,
          scope = excluded.scope
        """
    )
    with engine.begin() as conn:
        conn.execute(sql, rows)


def upsert_issues(engine: Engine, rows: list[dict]):
    if not rows:
        return
    sql = text(
        """
        insert into qalita_issues (id, partner_id, created_at, updated_at, title, description, status,
                                   url, chat_url, source_id, assignee, scope, due_date,
                                   author_id, closed_at, updated_by, closed_by)
        values (:id, :partner_id, :created_at, :updated_at, :title, :description, :status,
                :url, :chat_url, :source_id, :assignee, cast(:scope as jsonb), :due_date,
                :author_id, :closed_at, :updated_by, :closed_by)
        on conflict (id) do update set
          partner_id = excluded.partner_id,
          created_at = excluded.created_at,
          updated_at = excluded.updated_at,
          title = excluded.title,
          description = excluded.description,
          status = excluded.status,
          url = excluded.url,
          chat_url = excluded.chat_url,
          source_id = excluded.source_id,
          assignee = excluded.assignee,
          scope = excluded.scope,
          due_date = excluded.due_date,
          author_id = excluded.author_id,
          closed_at = excluded.closed_at,
          updated_by = excluded.updated_by,
          closed_by = excluded.closed_by
        """
    )
    with engine.begin() as conn:
        conn.execute(sql, rows)


def get_watermark(engine: Engine, table: str) -> datetime | None:
    sql = text(f"select max(created_at) from {table}")
    with engine.connect() as conn:
        result = conn.execute(sql).scalar()
        return result


def _parse_iso8601(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def export_metrics(engine: Engine, api_url: str, batch_size: int):
    wm = get_watermark(engine, "qalita_metrics")
    endpoint = f"{api_url}/api/v2/metrics"
    total = 0
    early_stop = False
    for page in paginate(endpoint, {}, batch_size):
        # Stop early if we hit records at or before watermark (API returns newest first)
        filtered = []
        for m in page:
            created_at = _parse_iso8601(m.get("created_at"))
            if wm and created_at and created_at <= wm:
                early_stop = True
                continue
            filtered.append(
                {
                    "id": m["id"],
                    "partner_id": m.get("partner_id"),
                    "created_at": m.get("created_at"),
                    "updated_at": m.get("updated_at"),
                    "key": m.get("key"),
                    "value": m.get("value"),
                    "source_id": m.get("source_id"),
                    "source_version_id": m.get("source_version_id"),
                    "pack_id": m.get("pack_id"),
                    "pack_version_id": m.get("pack_version_id"),
                    "scope": m.get("scope"),
                }
            )
        if filtered:
            upsert_metrics(engine, filtered)
            total += len(filtered)
            logger.info("Upserted %d metrics (cum=%d)", len(filtered), total)
        if early_stop:
            break


def export_issues(engine: Engine, api_url: str, batch_size: int):
    wm = get_watermark(engine, "qalita_issues")
    endpoint = f"{api_url}/api/v2/issues"
    total = 0
    early_stop = False
    for page in paginate(endpoint, {}, batch_size):
        filtered = []
        for it in page:
            created_at = _parse_iso8601(it.get("created_at"))
            if wm and created_at and created_at <= wm:
                early_stop = True
                continue
            filtered.append(
                {
                    "id": it["id"],
                    "partner_id": it.get("partner_id"),
                    "created_at": it.get("created_at"),
                    "updated_at": it.get("updated_at"),
                    "title": it.get("title"),
                    "description": it.get("description"),
                    "status": it.get("status"),
                    "url": it.get("url"),
                    "chat_url": it.get("chat_url"),
                    "source_id": it.get("source_id"),
                    "assignee": it.get("assignee"),
                    "scope": it.get("scope"),
                    "due_date": it.get("due_date"),
                    "author_id": it.get("author_id"),
                    "closed_at": it.get("closed_at"),
                    "updated_by": it.get("updated_by"),
                    "closed_by": it.get("closed_by"),
                }
            )
        if filtered:
            upsert_issues(engine, filtered)
            total += len(filtered)
            logger.info("Upserted %d issues (cum=%d)", len(filtered), total)
        if early_stop:
            break


def main():
    load_dotenv()
    api_url = get_env("QALITA_API_URL", required=True)
    batch_size = int(get_env("BATCH_SIZE", "1000"))
    engine = make_engine()
    export_metrics(engine, api_url, batch_size)
    export_issues(engine, api_url, batch_size)


if __name__ == "__main__":
    main()


