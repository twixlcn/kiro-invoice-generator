# Invoice Generator — Backend

FastAPI + Pydantic v2 + SQLAlchemy 2.x + Alembic + Python standard-library logging.

## Layer Rules (strictly enforced)

| Layer | Allowed | Not allowed |
|---|---|---|
| `api/invoices.py`, `api/businesses.py`, `api/customers.py` | Validate, call service, shape response | Calculate, touch the database directly |
| `services/invoice_service.py`, `business_service.py`, `customer_service.py` | Orchestrate calculator + repositories | Direct database access, HTTP |
| `services/calculator.py` | Pure math | Any I/O |
| `repositories/invoice_repository.py`, `business_repository.py`, `customer_repository.py` | Query/write via a SQLAlchemy `Session` | Calculations, business logic |

## Database

- PostgreSQL, SQLAlchemy 2.x (sync engine), migrations in `alembic/`.
- Schema: `businesses`, `customers`, `invoices` (FKs to business/customer `ON DELETE RESTRICT`), `invoice_items` (FK to invoice `ON DELETE CASCADE`). One consolidated initial migration (`alembic/versions/0001_initial_schema.py`) creates the whole schema — `alembic upgrade head` on a fresh database is a single step.
- Businesses/customers are reusable — invoices reference them by id, never embed a copy. Creating/updating an invoice verifies the referenced `business_id`/`customer_id` exist (`BusinessNotFoundError`/`CustomerNotFoundError` → 404) but never dedupes or mutates them.
- `created_at`/`updated_at` are set by the database (`server_default`/`onupdate=func.now()`), not app code.

Apply migrations:
```bash
alembic upgrade head
```

One-time import of the legacy `backend/data/*.json` invoices (idempotent — reuses a matching business/customer row instead of duplicating it, skips invoice numbers already present):
```bash
python scripts/migrate_json_to_db.py
```

Verify the schema matches what the app expects (handy after a manual migration):
```bash
python scripts/verify_schema.py
```

## Logging

```
logs/application.log   DEBUG+  all messages
logs/error.log         ERROR+  with tracebacks
console                INFO+   readable output
```

Every log line in a request is prefixed `[req <8-char-hex>]`.  
The same ID is returned as `X-Request-ID` response header.

> Customer name and email only appear in DEBUG lines. Never log secrets.

## Running Tests

```bash
pytest -v
```

`tests/test_calculations.py` covers `services/calculator.py` and the `InvoiceCreate` validation rules — pure logic, no database. There's no database-backed test suite; the app itself is the thing to exercise manually against `invoice_generator` for the debugging workshop.
