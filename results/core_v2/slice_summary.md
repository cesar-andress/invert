# INVERT Core v2 — Slice Analysis Summary

Analysis uses handcrafted fixtures only. No LLM APIs.

## 1. Does F3.2 validate the experimental instrument?

**Yes, on fixtures.** Shuffled-label accuracy = 0.500 (n=10), within chance band. A process-signature detector applied to code does not recover permuted metadata labels.

## 2. Does F1.1 survive all implemented stripping levels?

**Yes.** Euler and RK4 fixtures remain correctly classified at raw, no_comments, renamed, no_imports, and format_normalized. F1.1 is not evaluated at `lock_marker_strip` (lock ablation applies only to F2.1).

## 3. Does F2.1 behave as a positive trivial control?

**Yes at raw and no_comments.** Lock vs no-lock fixtures are discriminated correctly.

### Collapse after `lock_marker_strip`

**Yes — collapse observed on fixtures.** After lock-marker ablation, the with-lock fixture is no longer classified as locked (predicted `no_lock`). The no-lock fixture remains no-lock. This matches the preregistered trivial-control expectation: lock recovery depends on obvious lock markers.

Levels `renamed`, `no_imports`, and `format_normalized` do not remove lock primitives; F2.1 accuracy at those levels is reported but **not_tested** as collapse evidence.

## 4. Preregistered conditions satisfied

- F1.1 detection survives all implemented stripping levels (≥0.95 threshold)
- F2.1 detector accuracy ≥0.95 at raw/no_comments
- F2.1 collapse after lock_marker_strip (with-lock no longer detected as locked)
- F3.2 shuffled-label accuracy in chance band (0.30–0.70 on fixtures)

## 5. Not yet testable

- F1.1 manipulation failure rate (requires generated artifacts + behavioral oracle)
- F1.1 detector accuracy ≥0.90 on manipulation-confirmed LLM-generated pairs
- F2.1 false positive rate ≤0.05 on large artifact sample
- F3.2 on LLM-generated artifacts (only fixture-based shuffled copies tested)

## 6. Recommended next implementation steps

1. Add ODE integration task generation with behavioral equivalence tests.
2. Run F1.1 on generated artifacts (still detector-primary, no LLM judge).
3. Expand F3.2 to generated artifact pairs with metadata-only label shuffle.
4. Add Jacobi/Gauss-Seidel and quadrature dimensions when Family 1 expands.

## Matrix status

| family | dimension | strip_level | accuracy | status |
|--------|-----------|-------------|----------|--------|
| F1 | F1.1_integration | raw | 1.0000 | pass |
| F1 | F1.1_integration | no_comments | 1.0000 | pass |
| F1 | F1.1_integration | renamed | 1.0000 | pass |
| F1 | F1.1_integration | no_imports | 1.0000 | pass |
| F1 | F1.1_integration | format_normalized | 1.0000 | pass |
| F2 | F2.1_lock_control | raw | 1.0000 | pass |
| F2 | F2.1_lock_control | no_comments | 1.0000 | pass |
| F2 | F2.1_lock_control | renamed | 1.0000 | not_tested |
| F2 | F2.1_lock_control | no_imports | 1.0000 | not_tested |
| F2 | F2.1_lock_control | format_normalized | 1.0000 | not_tested |
| F2 | F2.1_lock_control | lock_marker_strip | 0.5000 | pass |
| F3 | F3.2_shuffled_label | n/a | 0.5000 | pass |
