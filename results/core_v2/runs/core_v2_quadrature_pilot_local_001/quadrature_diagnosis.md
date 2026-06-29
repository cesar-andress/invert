# Quadrature detector diagnosis (`core_v2_quadrature_pilot_local_001`)

Failed trapezoidal artifacts where the detector returned `ambiguous` or the wrong method.
The detector itself was not modified for this report.

## Failure classification counts

- **detector_too_strict**: 0
- **nonstandard_valid_trapezoidal**: 0
- **not_trapezoidal**: 0
- **stripping_broke_detector**: 0
- **ambiguous_legitimate**: 0

## Interpretation guide

### detector_too_strict

Generated code appears to implement trapezoidal quadrature correctly, but rigid signature rules (separate half weights, return * h) missed it.

### nonstandard_valid_trapezoidal

Behaviorally valid trapezoidal implementations using unconventional structure (n+1 sample grid, indexed arrays, late *= h scaling).

### not_trapezoidal

Code is not trapezoidal or failed the behavioral oracle without recoverable trapezoidal signatures.

### stripping_broke_detector

Raw/no_comments detection was stronger; renaming or import stripping changed scope or introduced false Simpson cues.

### ambiguous_legitimate

Ambiguous classification is reasonable given weak or mixed arithmetic signatures.

