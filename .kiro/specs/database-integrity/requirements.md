# Requirements Document

## Introduction

This spec covers the correctness guarantees the database layer
(`backend/app/repositories/`, `backend/app/db/models.py`, Alembic
migrations) is expected to provide: that writes persist, that
invoice numbers uniquely identify one invoice, and that related
records (business, customer, items) are correctly scoped to the
invoice that owns them.

## Requirements

### Requirement 1 — Writes persist

**User Story:** As a user editing an invoice, I want my changes to be
saved permanently, so that refreshing the page or reopening the
invoice later shows my edits, not the old data.

#### Acceptance Criteria

1. WHEN a PUT request to `/api/invoices/{invoice_number}` returns 200
   THEN THE SYSTEM SHALL have durably persisted the change such that
   a subsequent GET, in a new and independent request/session,
   reflects it.
2. WHEN an update is made THEN THE SYSTEM SHALL NOT rely on
   in-memory/session state alone to represent success — the response
   must reflect what is actually committed to PostgreSQL.
3. WHEN verifying this behavior THEN THE SYSTEM SHALL be tested using
   two separate database sessions (simulating two separate HTTP
   requests), not a single shared session, which can mask a missing
   commit.

### Requirement 2 — Invoice numbers uniquely identify one invoice

**User Story:** As a business owner, I want each invoice number to
refer to exactly one invoice, so I never end up with two different
invoices sharing a number, or duplicate records from a single save
action.

#### Acceptance Criteria

1. WHEN a client submits the same create-invoice request twice (e.g.
   due to a network retry) THEN THE SYSTEM SHALL create at most one
   invoice, not two.
2. WHEN a second `POST /api/invoices` is sent with an `invoice_number`
   that already exists THEN THE SYSTEM SHALL reject it with a 409 and
   SHALL NOT create a second row.
3. WHEN protection against duplicates is implemented THEN THE SYSTEM
   SHALL enforce it at the database level (a constraint), not solely
   via an application-level check, since a check-then-insert without
   a database-level backstop is subject to a race condition.

### Requirement 3 — Line items belong to their own invoice only

**User Story:** As a business owner reusing the same business/customer
across multiple invoices, I want each invoice to show only its own
line items, so invoice totals and line items are never mixed up
between records.

#### Acceptance Criteria

1. WHEN an invoice is fetched (GET, list, create response, update
   response) THEN THE SYSTEM SHALL return only `invoice_items` whose
   `invoice_id` matches that invoice's own primary key.
2. WHEN a business or customer is reused across multiple invoices
   THEN THE SYSTEM SHALL still correctly scope each invoice's items
   to itself — item attachment SHALL NOT depend on `business_id`,
   `customer_id`, or any column other than the invoice's own `id`.
3. WHEN this is verified THEN THE SYSTEM SHALL be tested with a
   scenario where one business/customer is shared across 3 or more
   invoices, since a bug scoped to a single invoice-per-business case
   can pass undetected.
