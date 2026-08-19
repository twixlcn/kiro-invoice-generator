# Requirements Document

## Introduction

Invoice totals must be correct whenever a discount and a tax rate are
both applied. This spec defines the expected calculation behavior of
`backend/app/services/calculator.py` and how to verify it.

## Requirements

### Requirement 1 — Correct order of operations

**User Story:** As a business owner, I want invoice totals to be
calculated correctly when both a discount and a tax rate are applied,
so that I can trust the amounts on the invoices I send to customers.

#### Acceptance Criteria

1. WHEN an invoice has a non-zero discount and a non-zero tax rate
   THEN THE SYSTEM SHALL compute tax on the post-discount taxable
   amount, not the pre-discount subtotal.
2. WHEN the reference example values from README.md are used
   (subtotal 17000, discount 1000, tax_rate 0.12) THEN THE SYSTEM
   SHALL produce taxable_amount=16000, tax=1920, total=17920.
3. WHEN discount is zero THEN THE SYSTEM SHALL produce a total
   mathematically equal to subtotal + (subtotal × tax_rate).
4. WHEN discount exceeds subtotal THEN THE SYSTEM SHALL cap the
   discount at subtotal, producing taxable_amount=0 and tax=0.
5. WHEN totals are computed THEN THE SYSTEM SHALL round every
   intermediate value (item totals, subtotal, discount,
   taxable_amount, tax, total) to 2 decimal places using
   ROUND_HALF_UP, consistent with `calculator.py`'s documented
   behavior.

### Requirement 2 — Verifiable in isolation

**User Story:** As a developer maintaining this app, I want a fast,
deterministic way to verify the calculation logic on its own, so
regressions are caught without needing a running database.

#### Acceptance Criteria

1. WHEN `calculate_totals()` is called with a known set of
   items/discount/tax_rate THEN THE SYSTEM SHALL be verifiable via a
   pure unit test with no I/O.
2. IF `calculate_totals()`'s output diverges from the worked
   reference example in README.md THEN THE SYSTEM SHALL be considered
   to have a calculation regression — regardless of whether an
   individual field such as `taxable_amount` still displays a
   plausible-looking value on its own.
