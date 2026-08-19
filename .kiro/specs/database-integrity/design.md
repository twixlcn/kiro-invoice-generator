# Design Document

## Overview

Covers `backend/app/repositories/invoice_repository.py`,
`backend/app/db/models.py` (ORM relationships),
`backend/app/services/invoice_service.py`'s duplicate-prevention
logic, and the constraints defined in
`backend/alembic/versions/`.

## Architecture

Relevant relationships:

- `Invoice.business` — FK `business_id -> businesses.id`, `ON DELETE RESTRICT`
- `Invoice.customer` — FK `customer_id -> customers.id`, `ON DELETE RESTRICT`
- `Invoice.items` — FK `invoice_items.invoice_id -> invoices.id`, `ON DELETE CASCADE`

Session handling: `app/db/session.py`'s `get_db()` dependency yields
one `Session` per request and closes it afterward. A `Session` that
is never committed rolls back its changes on close.

## Investigation Approach

### Requirement 1 (persistence)

- Check `invoice_repository.update()` (and `create()`/`delete()` for
  comparison) for a `commit()` call after mutating the ORM object.
- Reproduce with two separate `SessionLocal()` instances in a script
  — one to write, one to read afterward — since a single shared
  session can show "correct" data in-memory even when nothing was
  committed.

### Requirement 2 (uniqueness / idempotency)

- Check whether `invoices.invoice_number` has a database-level unique
  constraint (inspect via `psql \d invoices`, or the Alembic migration
  history) and compare against what `backend/app/db/models.py`
  declares.
- Check `invoice_service.create_invoice()` for a pre-insert existence
  check, and consider whether it's sufficient on its own without a
  database-level constraint (a check-then-insert race).
- Reproduce by sending the same create payload twice in quick
  succession and checking whether two rows are created.

### Requirement 3 (item scoping)

- Inspect `invoice_repository._base_query()` — specifically how
  `invoice_items` are joined/loaded — and confirm the join key is the
  invoice's own primary key (`id`), not any other column.
- Reproduce using one business/customer referenced by 3 or more
  invoices (the reusable-entity feature), not a
  one-invoice-per-business setup, since small sequential IDs can
  coincidentally line up and hide this class of bug in a minimal
  repro.

## Testing Strategy

- Prefer verification scripts that open independent `SessionLocal()`
  instances over relying on a single shared session, since
  session-sharing can mask exactly the bugs this spec is about.
- Use `psql` directly against the dev database to confirm what's
  physically stored, independent of what the API reports.
