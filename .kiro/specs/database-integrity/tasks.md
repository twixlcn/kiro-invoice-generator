# Implementation Plan

- [ ] 1. Investigate persistence (Requirement 1)
  - [ ] 1.1 Write a two-session repro script: create an invoice,
        update it in a second session, then read it back in a third
        session
    - _Requirements: 1.1, 1.3_
  - [ ] 1.2 Inspect `invoice_repository.update()` for a missing or
        skipped commit
    - _Requirements: 1.2_
  - [ ] 1.3 Fix and re-verify with the same multi-session repro
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Investigate duplicate prevention (Requirement 2)
  - [ ] 2.1 Send an identical create-invoice payload twice and record
        how many rows result
    - _Requirements: 2.1_
  - [ ] 2.2 Inspect the invoices table's actual constraints via psql
        and compare against `db/models.py`
    - _Requirements: 2.2, 2.3_
  - [ ] 2.3 Inspect `invoice_service.create_invoice()` for a
        pre-insert existence check
    - _Requirements: 2.2, 2.3_
  - [ ] 2.4 Restore both the database-level constraint and the
        application-level check; confirm a second identical POST now
        returns 409
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3. Investigate item scoping (Requirement 3)
  - [ ] 3.1 Create one business/customer and 3 invoices that all
        reference it, each with distinctly named line items
    - _Requirements: 3.3_
  - [ ] 3.2 Fetch each invoice and confirm which items it actually
        returns
    - _Requirements: 3.1_
  - [ ] 3.3 Inspect `invoice_repository._base_query()`'s join
        condition for `invoice_items`
    - _Requirements: 3.2_
  - [ ] 3.4 Fix the join condition and re-run the 3-invoice repro to
        confirm each invoice now shows only its own items
    - _Requirements: 3.1, 3.2, 3.3_
