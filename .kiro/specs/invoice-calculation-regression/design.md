# Design Document

## Overview

This spec covers the tax/discount/total computation pipeline in
`backend/app/services/calculator.py`, and its consumers in
`invoice_service.py` (`create_invoice`, `update_invoice`,
`calculate`).

## Architecture

`calculate_totals()` is a pure function:
`(items, discount, tax_rate) -> {subtotal, discount, taxable_amount, tax, total}`.
It has no I/O and no database dependency, so it is fully testable in
isolation.

Correct order of operations:

1. `item_total = quantity × unit_price` (per item, rounded)
2. `subtotal = sum(item_total)`
3. `discount_amount = min(discount, subtotal)`
4. `taxable_amount = subtotal - discount_amount`
5. `tax = taxable_amount × tax_rate`
6. `total = taxable_amount + tax`

Each step is rounded to 2 decimal places (ROUND_HALF_UP) before being
used in the next step.

## Components and Interfaces

- `calculate_item_total(quantity, unit_price) -> float`
- `calculate_totals(items, discount, tax_rate) -> dict`

## Data Model

`InvoiceTotals`: `{subtotal, discount, taxable_amount, tax, total}` —
all floats, 2 decimal places.

## Investigation Approach

1. Reproduce with the README reference example values.
2. Compare **every** intermediate value (subtotal, taxable_amount,
   tax, total) against the expected values in Requirement 1 — not
   just the final total. A field that looks right in isolation (e.g.
   `taxable_amount`) can still feed into a miscalculated downstream
   value.
3. Trace which variable each arithmetic step actually reads from —
   confirm it matches the order of operations above, not just that a
   plausible-looking variable name appears nearby in the code.

## Error Handling

No exceptions are expected for valid numeric input; Pydantic
validation (`ge=0`, `le=1` for `tax_rate`, etc.) happens upstream in
`InvoiceCreate`.

## Testing Strategy

- Unit test against `calculator.py` directly — no database, no HTTP.
- Cross-check against `backend/tests/test_calculations.py`'s existing
  `test_reference_example` and `test_tax_rounding` cases.
