"""Verify the PostgreSQL schema matches what the app expects.

Meant to run right after Alembic migrations, before the test suite —
so a schema mismatch fails clearly on its own, instead of surfacing as
a confusing test failure. Checks whatever DATABASE_URL currently points
to (dev locally, the CI Postgres service in the pipeline).

Run from the backend/ directory: python scripts/verify_schema.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect

from app.db.session import engine

EXPECTED_TABLES = {
    "businesses": {"id", "name", "address", "email", "created_at", "updated_at"},
    "customers": {"id", "name", "email", "created_at", "updated_at"},
    "invoices": {
        "id",
        "invoice_number",
        "business_id",
        "customer_id",
        "invoice_date",
        "due_date",
        "discount",
        "tax_rate",
        "subtotal",
        "taxable_amount",
        "tax",
        "total",
        "created_at",
        "updated_at",
    },
    "invoice_items": {
        "id",
        "invoice_id",
        "description",
        "quantity",
        "unit_price",
        "item_total",
        "created_at",
        "updated_at",
    },
}


def verify_schema() -> None:
    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())
    errors = []

    for table, expected_columns in EXPECTED_TABLES.items():
        if table not in actual_tables:
            errors.append(f"Missing table: {table!r}")
            continue
        actual_columns = {col["name"] for col in inspector.get_columns(table)}
        missing = expected_columns - actual_columns
        if missing:
            errors.append(f"Table {table!r} is missing column(s): {sorted(missing)}")

    if errors:
        print("Schema verification FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("Schema verification passed:")
    for table in EXPECTED_TABLES:
        print(f"  - {table}: OK")


if __name__ == "__main__":
    verify_schema()
