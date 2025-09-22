## QALITA → Warehouse export job (example)

Prereqs:

- Python 3.10+
- Postgres (or adapt SQLAlchemy URL and DDL for your warehouse)

Setup:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit values
```

Run:

```bash
python export_qalita_to_warehouse.py
```

Notes:

- Uses offset pagination. It upserts by primary key `id` and stops early when items are older than the local `created_at` watermark.
- Ensure you executed `../warehouse/schema.sql` in your warehouse before the first run.

