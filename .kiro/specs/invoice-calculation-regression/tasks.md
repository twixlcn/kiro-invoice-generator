# Implementation Plan

- [ ] 1. Reproduce the discrepancy using the README reference example
      (subtotal 17000, discount 1000, tax_rate 0.12) and record the
      actual vs. expected value for each intermediate field
  - _Requirements: 1.2_

- [ ] 2. Trace `calculate_totals()` line by line and identify which
      variable feeds the tax calculation
  - _Requirements: 1.1_

- [ ] 3. Compare against the order of operations in design.md and
      identify the specific line where behavior deviates
  - _Requirements: 1.1_

- [ ] 4. Fix the identified line so tax is computed from the
      post-discount taxable amount
  - _Requirements: 1.1, 1.2_

- [ ] 5. Re-run `backend/tests/test_calculations.py` and confirm
      `test_reference_example` and related tests pass
  - _Requirements: 1.2, 2.2_

- [ ] 6. Verify the discount-exceeds-subtotal and zero-discount edge
      cases still behave correctly after the fix
  - _Requirements: 1.3, 1.4_
