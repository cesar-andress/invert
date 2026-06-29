# Category B Forensic Report

Run: `pilot_security_concurrency_001`
Category B observations analyzed: **51**

Definition: manifestation_score >= 0.10 AND recovery_strict = 0.
All 51 cases are partial recoveries (exactly one of v0/v1 wrong; none with both wrong).

---

## PART 1 — Failure mechanism clusters (inferred from data)

| Cluster | Count | Hypothesized mechanism |
|---------|------:|------------------------|
| `algorithm_api_substitution` | 16 | Large AST rewrite with import/API substitution unrelated to dimension markers |
| `v0_validation_surface_miss` | 14 | Security v0 uses alternate validation surface; judge misses v0, recovers v1 |
| `non_dimension_algorithm_substitution` | 13 | Entire algorithm replaced (often API-backed); manipulated dimension markers absent |
| `v1_concurrency_surface_miss` | 4 | Concurrency v1 edited but without lock/threading tokens; judge misses v1 |
| `v1_salient_dimension_edit` | 4 | Dimension-aligned edit concentrated in v1; judge recovers v0 only |

See `category_B_clusters.csv` and `category_B_examples.md` for representatives.

### Per-observation cluster assignment

- **B001** `dependency_order/concurrency/anthropic/rep1` → `non_dimension_algorithm_substitution`
- **B002** `dependency_order/concurrency/anthropic/rep2` → `non_dimension_algorithm_substitution`
- **B003** `dependency_order/concurrency/anthropic/rep3` → `non_dimension_algorithm_substitution`
- **B004** `dependency_order/concurrency/anthropic/rep4` → `non_dimension_algorithm_substitution`
- **B005** `dependency_order/concurrency/anthropic/rep5` → `non_dimension_algorithm_substitution`
- **B006** `dependency_order/security/anthropic/rep1` → `non_dimension_algorithm_substitution`
- **B007** `dependency_order/security/anthropic/rep3` → `non_dimension_algorithm_substitution`
- **B008** `dependency_order/security/anthropic/rep4` → `non_dimension_algorithm_substitution`
- **B009** `lru_cache/security/anthropic/rep5` → `algorithm_api_substitution`
- **B010** `merge_intervals/concurrency/anthropic/rep1` → `algorithm_api_substitution`
- **B011** `merge_intervals/concurrency/anthropic/rep2` → `algorithm_api_substitution`
- **B012** `merge_intervals/concurrency/anthropic/rep3` → `algorithm_api_substitution`
- **B013** `merge_intervals/concurrency/anthropic/rep4` → `v1_concurrency_surface_miss`
- **B014** `merge_intervals/concurrency/anthropic/rep5` → `algorithm_api_substitution`
- **B015** `sanitize_filename/concurrency/anthropic/rep1` → `algorithm_api_substitution`
- **B016** `sanitize_filename/concurrency/anthropic/rep2` → `algorithm_api_substitution`
- **B017** `sanitize_filename/concurrency/anthropic/rep3` → `algorithm_api_substitution`
- **B018** `sanitize_filename/concurrency/anthropic/rep4` → `algorithm_api_substitution`
- **B019** `sanitize_filename/concurrency/anthropic/rep5` → `algorithm_api_substitution`
- **B020** `sanitize_filename/security/anthropic/rep2` → `v0_validation_surface_miss`
- **B021** `sanitize_filename/security/anthropic/rep3` → `v0_validation_surface_miss`
- **B022** `sanitize_filename/security/anthropic/rep4` → `algorithm_api_substitution`
- **B023** `sanitize_filename/security/anthropic/rep5` → `v0_validation_surface_miss`
- **B024** `validate_email_like/security/anthropic/rep1` → `v0_validation_surface_miss`
- **B025** `validate_email_like/security/anthropic/rep2` → `v0_validation_surface_miss`
- **B026** `validate_email_like/security/anthropic/rep3` → `v0_validation_surface_miss`
- **B027** `validate_email_like/security/anthropic/rep4` → `v0_validation_surface_miss`
- **B028** `validate_email_like/security/anthropic/rep5` → `v0_validation_surface_miss`
- **B029** `dependency_order/security/openai/rep1` → `non_dimension_algorithm_substitution`
- **B030** `dependency_order/security/openai/rep2` → `non_dimension_algorithm_substitution`
- **B031** `dependency_order/security/openai/rep3` → `non_dimension_algorithm_substitution`
- **B032** `dependency_order/security/openai/rep4` → `non_dimension_algorithm_substitution`
- **B033** `dependency_order/security/openai/rep5` → `non_dimension_algorithm_substitution`
- **B034** `merge_intervals/security/openai/rep3` → `v0_validation_surface_miss`
- **B035** `merge_intervals/security/openai/rep4` → `v0_validation_surface_miss`
- **B036** `merge_intervals/security/openai/rep5` → `v0_validation_surface_miss`
- **B037** `sanitize_filename/concurrency/openai/rep2` → `v1_concurrency_surface_miss`
- **B038** `sanitize_filename/concurrency/openai/rep3` → `v1_concurrency_surface_miss`
- **B039** `sanitize_filename/concurrency/openai/rep4` → `v1_concurrency_surface_miss`
- **B040** `sanitize_filename/security/openai/rep1` → `algorithm_api_substitution`
- **B041** `sanitize_filename/security/openai/rep2` → `algorithm_api_substitution`
- **B042** `sanitize_filename/security/openai/rep3` → `algorithm_api_substitution`
- **B043** `sanitize_filename/security/openai/rep4` → `algorithm_api_substitution`
- **B044** `sanitize_filename/security/openai/rep5` → `algorithm_api_substitution`
- **B045** `validate_email_like/concurrency/openai/rep1` → `v1_salient_dimension_edit`
- **B046** `validate_email_like/concurrency/openai/rep3` → `v1_salient_dimension_edit`
- **B047** `validate_email_like/concurrency/openai/rep4` → `v1_salient_dimension_edit`
- **B048** `validate_email_like/concurrency/openai/rep5` → `v1_salient_dimension_edit`
- **B049** `validate_email_like/security/openai/rep3` → `v0_validation_surface_miss`
- **B050** `validate_email_like/security/openai/rep4` → `v0_validation_surface_miss`
- **B051** `validate_email_like/security/openai/rep5` → `v0_validation_surface_miss`

## PART 2 — Manifestation score component drivers

- **import** dominant: 17/51 (33.3%)
- **text** dominant: 17/51 (33.3%)
- **ast** dominant: 16/51 (31.4%)
- **function** dominant: 1/51 (2.0%)

Category B is driven primarily by **text and AST distance jointly**, not imports/functions (both near zero in most pairs).
Import distance contributes materially in 22 cases.
Function distance contributes materially in 14 cases.

Figures: `category_B_figures/manifestation_component_distributions.png`, `dominant_driver_counts.png`.

### Per-observation component contributions

- **B001**: text=0.2724, ast=0.2699, import=0.3051, function=0.1526, dominant=import
- **B002**: text=0.3130, ast=0.3185, import=0.3685, function=0.0000, dominant=import
- **B003**: text=0.2714, ast=0.2696, import=0.3060, function=0.1530, dominant=import
- **B004**: text=0.2712, ast=0.2677, import=0.3074, function=0.1537, dominant=import
- **B005**: text=0.2722, ast=0.2701, import=0.3051, function=0.1526, dominant=import
- **B006**: text=0.3929, ast=0.3667, import=0.0000, function=0.2404, dominant=text
- **B007**: text=0.3932, ast=0.3723, import=0.0000, function=0.2345, dominant=text
- **B008**: text=0.3881, ast=0.3783, import=0.0000, function=0.2336, dominant=text
- **B009**: text=0.2506, ast=0.2384, import=0.2555, function=0.2555, dominant=import
- **B010**: text=0.3310, ast=0.2100, import=0.4590, function=0.0000, dominant=import
- **B011**: text=0.3310, ast=0.2100, import=0.4590, function=0.0000, dominant=import
- **B012**: text=0.3310, ast=0.2100, import=0.4590, function=0.0000, dominant=import
- **B013**: text=0.3253, ast=0.2005, import=0.4742, function=0.0000, dominant=import
- **B014**: text=0.3309, ast=0.2099, import=0.4592, function=0.0000, dominant=import
- **B015**: text=0.3278, ast=0.2826, import=0.1948, function=0.1948, dominant=text
- **B016**: text=0.3371, ast=0.2802, import=0.1914, function=0.1914, dominant=text
- **B017**: text=0.3398, ast=0.2752, import=0.1925, function=0.1925, dominant=text
- **B018**: text=0.2979, ast=0.0000, import=0.3511, function=0.3511, dominant=import
- **B019**: text=0.3389, ast=0.2677, import=0.1967, function=0.1967, dominant=text
- **B020**: text=0.4812, ast=0.5188, import=0.0000, function=0.0000, dominant=ast
- **B021**: text=0.4899, ast=0.5101, import=0.0000, function=0.0000, dominant=ast
- **B022**: text=0.3411, ast=0.3737, import=0.2852, function=0.0000, dominant=ast
- **B023**: text=0.4810, ast=0.5190, import=0.0000, function=0.0000, dominant=ast
- **B024**: text=0.5267, ast=0.4733, import=0.0000, function=0.0000, dominant=text
- **B025**: text=0.4890, ast=0.5110, import=0.0000, function=0.0000, dominant=ast
- **B026**: text=0.3723, ast=0.0000, import=0.0000, function=0.6277, dominant=function
- **B027**: text=0.4890, ast=0.5110, import=0.0000, function=0.0000, dominant=ast
- **B028**: text=0.4870, ast=0.5130, import=0.0000, function=0.0000, dominant=ast
- **B029**: text=0.4441, ast=0.5559, import=0.0000, function=0.0000, dominant=ast
- **B030**: text=0.4006, ast=0.5994, import=0.0000, function=0.0000, dominant=ast
- **B031**: text=0.4006, ast=0.5994, import=0.0000, function=0.0000, dominant=ast
- **B032**: text=0.4006, ast=0.5994, import=0.0000, function=0.0000, dominant=ast
- **B033**: text=0.4441, ast=0.5559, import=0.0000, function=0.0000, dominant=ast
- **B034**: text=0.5294, ast=0.4706, import=0.0000, function=0.0000, dominant=text
- **B035**: text=0.5294, ast=0.4706, import=0.0000, function=0.0000, dominant=text
- **B036**: text=0.5294, ast=0.4706, import=0.0000, function=0.0000, dominant=text
- **B037**: text=0.6974, ast=0.3026, import=0.0000, function=0.0000, dominant=text
- **B038**: text=0.6974, ast=0.3026, import=0.0000, function=0.0000, dominant=text
- **B039**: text=0.6974, ast=0.3026, import=0.0000, function=0.0000, dominant=text
- **B040**: text=0.2443, ast=0.3389, import=0.4168, function=0.0000, dominant=import
- **B041**: text=0.2443, ast=0.3389, import=0.4168, function=0.0000, dominant=import
- **B042**: text=0.2443, ast=0.3389, import=0.4168, function=0.0000, dominant=import
- **B043**: text=0.2443, ast=0.3389, import=0.4168, function=0.0000, dominant=import
- **B044**: text=0.2443, ast=0.3389, import=0.4168, function=0.0000, dominant=import
- **B045**: text=0.4784, ast=0.5216, import=0.0000, function=0.0000, dominant=ast
- **B046**: text=0.4784, ast=0.5216, import=0.0000, function=0.0000, dominant=ast
- **B047**: text=0.4784, ast=0.5216, import=0.0000, function=0.0000, dominant=ast
- **B048**: text=0.5383, ast=0.4617, import=0.0000, function=0.0000, dominant=text
- **B049**: text=0.5519, ast=0.4481, import=0.0000, function=0.0000, dominant=text
- **B050**: text=0.4917, ast=0.5083, import=0.0000, function=0.0000, dominant=ast
- **B051**: text=0.5116, ast=0.4884, import=0.0000, function=0.0000, dominant=text

## PART 3 — Cosmetic vs semantic equivalence

- **Definitely equivalent**: 0
- **Probably equivalent**: 0
- **Unclear**: 11
- **Probably different**: 0
- **Definitely different**: 40

**Cosmetic-or-equivalent estimate: 0/51 (0.0%)** using structural/text heuristics on existing code pairs.

### Per-observation equivalence rating

- **B001** `dependency_order/concurrency/anthropic/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B002** `dependency_order/concurrency/anthropic/rep2`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B003** `dependency_order/concurrency/anthropic/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B004** `dependency_order/concurrency/anthropic/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B005** `dependency_order/concurrency/anthropic/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B006** `dependency_order/security/anthropic/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B007** `dependency_order/security/anthropic/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B008** `dependency_order/security/anthropic/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B009** `lru_cache/security/anthropic/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B010** `merge_intervals/concurrency/anthropic/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B011** `merge_intervals/concurrency/anthropic/rep2`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B012** `merge_intervals/concurrency/anthropic/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B013** `merge_intervals/concurrency/anthropic/rep4`: **Unclear** — Mixed signals between text and structural distance metrics
- **B014** `merge_intervals/concurrency/anthropic/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B020** `sanitize_filename/security/anthropic/rep2`: **Unclear** — Mixed signals between text and structural distance metrics
- **B021** `sanitize_filename/security/anthropic/rep3`: **Unclear** — Mixed signals between text and structural distance metrics
- **B022** `sanitize_filename/security/anthropic/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B023** `sanitize_filename/security/anthropic/rep5`: **Unclear** — Mixed signals between text and structural distance metrics
- **B024** `validate_email_like/security/anthropic/rep1`: **Unclear** — Mixed signals between text and structural distance metrics
- **B025** `validate_email_like/security/anthropic/rep2`: **Unclear** — Mixed signals between text and structural distance metrics
- **B026** `validate_email_like/security/anthropic/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B027** `validate_email_like/security/anthropic/rep4`: **Unclear** — Mixed signals between text and structural distance metrics
- **B028** `validate_email_like/security/anthropic/rep5`: **Unclear** — Mixed signals between text and structural distance metrics
- **B029** `dependency_order/security/openai/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B030** `dependency_order/security/openai/rep2`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B031** `dependency_order/security/openai/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B032** `dependency_order/security/openai/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B033** `dependency_order/security/openai/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B034** `merge_intervals/security/openai/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B035** `merge_intervals/security/openai/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B036** `merge_intervals/security/openai/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B037** `sanitize_filename/concurrency/openai/rep2`: **Unclear** — Mixed signals between text and structural distance metrics
- **B038** `sanitize_filename/concurrency/openai/rep3`: **Unclear** — Mixed signals between text and structural distance metrics
- **B039** `sanitize_filename/concurrency/openai/rep4`: **Unclear** — Mixed signals between text and structural distance metrics
- **B040** `sanitize_filename/security/openai/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B041** `sanitize_filename/security/openai/rep2`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B042** `sanitize_filename/security/openai/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B043** `sanitize_filename/security/openai/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B044** `sanitize_filename/security/openai/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B045** `validate_email_like/concurrency/openai/rep1`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B046** `validate_email_like/concurrency/openai/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B047** `validate_email_like/concurrency/openai/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B048** `validate_email_like/concurrency/openai/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B049** `validate_email_like/security/openai/rep3`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B050** `validate_email_like/security/openai/rep4`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution
- **B051** `validate_email_like/security/openai/rep5`: **Definitely different** — AST/text similarity indicates algorithmic restructure or API substitution

## PART 4 — Directional failures

- P(fail v0 | B) = 0.569 (29/51)
- P(fail v1 | B) = 0.431 (22/51)

Asymmetry is modest (57% v0-fail vs 43% v1-fail). v1-only failures concentrate in concurrency-dimension edits where v1 adds salient primitives. v0-only failures concentrate in security tasks where v0 uses alternate validation surface forms.

### Per-observation failure direction

- **B001** `dependency_order/concurrency/anthropic/rep1`: v1_only_fail (v0=true, v1=false)
- **B002** `dependency_order/concurrency/anthropic/rep2`: v1_only_fail (v0=true, v1=false)
- **B003** `dependency_order/concurrency/anthropic/rep3`: v1_only_fail (v0=true, v1=false)
- **B004** `dependency_order/concurrency/anthropic/rep4`: v1_only_fail (v0=true, v1=false)
- **B005** `dependency_order/concurrency/anthropic/rep5`: v1_only_fail (v0=true, v1=false)
- **B006** `dependency_order/security/anthropic/rep1`: v0_only_fail (v0=false, v1=true)
- **B007** `dependency_order/security/anthropic/rep3`: v0_only_fail (v0=false, v1=true)
- **B008** `dependency_order/security/anthropic/rep4`: v0_only_fail (v0=false, v1=true)
- **B009** `lru_cache/security/anthropic/rep5`: v0_only_fail (v0=false, v1=true)
- **B010** `merge_intervals/concurrency/anthropic/rep1`: v1_only_fail (v0=true, v1=false)
- **B011** `merge_intervals/concurrency/anthropic/rep2`: v1_only_fail (v0=true, v1=false)
- **B012** `merge_intervals/concurrency/anthropic/rep3`: v1_only_fail (v0=true, v1=false)
- **B013** `merge_intervals/concurrency/anthropic/rep4`: v1_only_fail (v0=true, v1=false)
- **B014** `merge_intervals/concurrency/anthropic/rep5`: v1_only_fail (v0=true, v1=false)
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: v1_only_fail (v0=true, v1=false)
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: v1_only_fail (v0=true, v1=false)
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: v1_only_fail (v0=true, v1=false)
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: v1_only_fail (v0=true, v1=false)
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: v1_only_fail (v0=true, v1=false)
- **B020** `sanitize_filename/security/anthropic/rep2`: v0_only_fail (v0=false, v1=true)
- **B021** `sanitize_filename/security/anthropic/rep3`: v0_only_fail (v0=false, v1=true)
- **B022** `sanitize_filename/security/anthropic/rep4`: v0_only_fail (v0=false, v1=true)
- **B023** `sanitize_filename/security/anthropic/rep5`: v0_only_fail (v0=false, v1=true)
- **B024** `validate_email_like/security/anthropic/rep1`: v0_only_fail (v0=false, v1=true)
- **B025** `validate_email_like/security/anthropic/rep2`: v0_only_fail (v0=false, v1=true)
- **B026** `validate_email_like/security/anthropic/rep3`: v0_only_fail (v0=false, v1=true)
- **B027** `validate_email_like/security/anthropic/rep4`: v0_only_fail (v0=false, v1=true)
- **B028** `validate_email_like/security/anthropic/rep5`: v0_only_fail (v0=false, v1=true)
- **B029** `dependency_order/security/openai/rep1`: v0_only_fail (v0=false, v1=true)
- **B030** `dependency_order/security/openai/rep2`: v0_only_fail (v0=false, v1=true)
- **B031** `dependency_order/security/openai/rep3`: v0_only_fail (v0=false, v1=true)
- **B032** `dependency_order/security/openai/rep4`: v0_only_fail (v0=false, v1=true)
- **B033** `dependency_order/security/openai/rep5`: v0_only_fail (v0=false, v1=true)
- **B034** `merge_intervals/security/openai/rep3`: v0_only_fail (v0=false, v1=true)
- **B035** `merge_intervals/security/openai/rep4`: v0_only_fail (v0=false, v1=true)
- **B036** `merge_intervals/security/openai/rep5`: v0_only_fail (v0=false, v1=true)
- **B037** `sanitize_filename/concurrency/openai/rep2`: v1_only_fail (v0=true, v1=false)
- **B038** `sanitize_filename/concurrency/openai/rep3`: v1_only_fail (v0=true, v1=false)
- **B039** `sanitize_filename/concurrency/openai/rep4`: v1_only_fail (v0=true, v1=false)
- **B040** `sanitize_filename/security/openai/rep1`: v0_only_fail (v0=false, v1=true)
- **B041** `sanitize_filename/security/openai/rep2`: v0_only_fail (v0=false, v1=true)
- **B042** `sanitize_filename/security/openai/rep3`: v0_only_fail (v0=false, v1=true)
- **B043** `sanitize_filename/security/openai/rep4`: v0_only_fail (v0=false, v1=true)
- **B044** `sanitize_filename/security/openai/rep5`: v0_only_fail (v0=false, v1=true)
- **B045** `validate_email_like/concurrency/openai/rep1`: v1_only_fail (v0=true, v1=false)
- **B046** `validate_email_like/concurrency/openai/rep3`: v1_only_fail (v0=true, v1=false)
- **B047** `validate_email_like/concurrency/openai/rep4`: v1_only_fail (v0=true, v1=false)
- **B048** `validate_email_like/concurrency/openai/rep5`: v1_only_fail (v0=true, v1=false)
- **B049** `validate_email_like/security/openai/rep3`: v0_only_fail (v0=false, v1=true)
- **B050** `validate_email_like/security/openai/rep4`: v0_only_fail (v0=false, v1=true)
- **B051** `validate_email_like/security/openai/rep5`: v0_only_fail (v0=false, v1=true)

## PART 5 — Task effects

### `sanitize_filename` — 17 Category B cases
- Dimensions: {'concurrency': 8, 'security': 9}
- Algorithm restructures: 11/17
- **Mechanism:** Security/concurrency flips produce large textual rewrites of small functions; partial judge asymmetry on validation surface forms.

### `dependency_order` — 13 Category B cases
- Dimensions: {'concurrency': 5, 'security': 8}
- Algorithm restructures: 13/13
- **Mechanism:** Generator replaces algorithm with API-based implementation; manifestation is high but manipulated concurrency dimension often absent → B via v1-only judge failure on non-concurrency code.

### `validate_email_like` — 12 Category B cases
- Dimensions: {'security': 8, 'concurrency': 4}
- Algorithm restructures: 8/12
- **Mechanism:** High text/AST distance from regex/validation rewrites; keyword and judge disagree on v0 vs v1 salience.

### `merge_intervals` — 8 Category B cases
- Dimensions: {'concurrency': 5, 'security': 3}
- Algorithm restructures: 7/8
- **Mechanism:** Mostly concurrency dimension with moderate manifestation; concurrency edits not always lock/threading based.

### `lru_cache` — 1 Category B cases
- Dimensions: {'security': 1}
- Algorithm restructures: 1/1
- **Mechanism:** Mixed partial failures; see per-observation rows.

## PART 6 — Model effects

### `openai` — 23 cases
- Clusters: {'non_dimension_algorithm_substitution': 5, 'v0_validation_surface_miss': 6, 'v1_concurrency_surface_miss': 3, 'algorithm_api_substitution': 5, 'v1_salient_dimension_edit': 4}
- Equivalence: {'Definitely different': 20, 'Unclear': 3}
- v1-only fail: 7
- v0-only fail: 16

### `anthropic` — 28 cases
- Clusters: {'non_dimension_algorithm_substitution': 8, 'algorithm_api_substitution': 11, 'v1_concurrency_surface_miss': 1, 'v0_validation_surface_miss': 8}
- Equivalence: {'Definitely different': 20, 'Unclear': 8}
- v1-only fail: 15
- v0-only fail: 13

Anthropic produces more algorithm/API substitution clusters (dependency_order). OpenAI concentrates in sanitize_filename and validate_email_like security rewrites. Both models yield partial (not zero) recovery — judge confusion is not model-exclusive.

## PART 7 — Keyword baseline

- keyword_explains=yes: 44
- keyword_explains=partial: 7

Keyword baseline exactly mirrors LLM failure side in 44 cases. Partial keyword alignment: 7. Surviving after removing keyword-explained cases: **7** (13.7%).
Non-artefact unexplained estimate: **0/51 (0.0%)**.

### Per-observation keyword comparison

- **B001** `dependency_order/concurrency/anthropic/rep1`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.819381
- **B002** `dependency_order/concurrency/anthropic/rep2`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.678446
- **B003** `dependency_order/concurrency/anthropic/rep3`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.816894
- **B004** `dependency_order/concurrency/anthropic/rep4`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.813160
- **B005** `dependency_order/concurrency/anthropic/rep5`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.819301
- **B006** `dependency_order/security/anthropic/rep1`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.519984
- **B007** `dependency_order/security/anthropic/rep3`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.533032
- **B008** `dependency_order/security/anthropic/rep4`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.535087
- **B009** `lru_cache/security/anthropic/rep5`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=false) → keyword_explains=partial, manifestation=0.978402
- **B010** `merge_intervals/concurrency/anthropic/rep1`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.544698
- **B011** `merge_intervals/concurrency/anthropic/rep2`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.544698
- **B012** `merge_intervals/concurrency/anthropic/rep3`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.544698
- **B013** `merge_intervals/concurrency/anthropic/rep4`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.527189
- **B014** `merge_intervals/concurrency/anthropic/rep5`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.544420
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.641775
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.653145
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.649333
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.949502
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.635579
- **B020** `sanitize_filename/security/anthropic/rep2`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.163726
- **B021** `sanitize_filename/security/anthropic/rep3`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.170843
- **B022** `sanitize_filename/security/anthropic/rep4`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.438242
- **B023** `sanitize_filename/security/anthropic/rep5`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.163798
- **B024** `validate_email_like/security/anthropic/rep1`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.197268
- **B025** `validate_email_like/security/anthropic/rep2`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.178378
- **B026** `validate_email_like/security/anthropic/rep3`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.531051
- **B027** `validate_email_like/security/anthropic/rep4`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.178378
- **B028** `validate_email_like/security/anthropic/rep5`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.177100
- **B029** `dependency_order/security/openai/rep1`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.357635
- **B030** `dependency_order/security/openai/rep2`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.327930
- **B031** `dependency_order/security/openai/rep3`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.327930
- **B032** `dependency_order/security/openai/rep4`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.327930
- **B033** `dependency_order/security/openai/rep5`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.357635
- **B034** `merge_intervals/security/openai/rep3`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.292838
- **B035** `merge_intervals/security/openai/rep4`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.292838
- **B036** `merge_intervals/security/openai/rep5`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.292838
- **B037** `sanitize_filename/concurrency/openai/rep2`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.132584
- **B038** `sanitize_filename/concurrency/openai/rep3`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.132584
- **B039** `sanitize_filename/concurrency/openai/rep4`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.132584
- **B040** `sanitize_filename/security/openai/rep1`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.599858
- **B041** `sanitize_filename/security/openai/rep2`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.599858
- **B042** `sanitize_filename/security/openai/rep3`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.599858
- **B043** `sanitize_filename/security/openai/rep4`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.599858
- **B044** `sanitize_filename/security/openai/rep5`: LLM(v0=false, v1=true) vs keyword(v0=false, v1=true) → keyword_explains=yes, manifestation=0.599858
- **B045** `validate_email_like/concurrency/openai/rep1`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.325154
- **B046** `validate_email_like/concurrency/openai/rep3`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.325154
- **B047** `validate_email_like/concurrency/openai/rep4`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.325154
- **B048** `validate_email_like/concurrency/openai/rep5`: LLM(v0=true, v1=false) vs keyword(v0=true, v1=false) → keyword_explains=yes, manifestation=0.270029
- **B049** `validate_email_like/security/openai/rep3`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.290119
- **B050** `validate_email_like/security/openai/rep4`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.277828
- **B051** `validate_email_like/security/openai/rep5`: LLM(v0=false, v1=true) vs keyword(v0=true, v1=true) → keyword_explains=partial, manifestation=0.314097

## PART 8 — Proxy leakage

- YES: 0
- PROBABLY: 23
- UNCLEAR: 6
- NO: 22

Per-observation proxy labels are in `category_B_dataset.csv` columns `proxy_explains`, `proxy_rationale`.

### Per-observation proxy leakage assessment

- **B001** `dependency_order/concurrency/anthropic/rep1`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B002** `dependency_order/concurrency/anthropic/rep2`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B003** `dependency_order/concurrency/anthropic/rep3`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B004** `dependency_order/concurrency/anthropic/rep4`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B005** `dependency_order/concurrency/anthropic/rep5`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B006** `dependency_order/security/anthropic/rep1`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=22); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B007** `dependency_order/security/anthropic/rep3`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=22); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B008** `dependency_order/security/anthropic/rep4`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=22); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B009** `lru_cache/security/anthropic/rep5`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=0); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B010** `merge_intervals/concurrency/anthropic/rep1`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B011** `merge_intervals/concurrency/anthropic/rep2`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B012** `merge_intervals/concurrency/anthropic/rep3`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B013** `merge_intervals/concurrency/anthropic/rep4`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B014** `merge_intervals/concurrency/anthropic/rep5`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B020** `sanitize_filename/security/anthropic/rep2`: **PROBABLY** — Both sides engineer_guessable (v0 score=12, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B021** `sanitize_filename/security/anthropic/rep3`: **PROBABLY** — Both sides engineer_guessable (v0 score=12, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B022** `sanitize_filename/security/anthropic/rep4`: **PROBABLY** — Both sides engineer_guessable (v0 score=12, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B023** `sanitize_filename/security/anthropic/rep5`: **PROBABLY** — Both sides engineer_guessable (v0 score=12, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B024** `validate_email_like/security/anthropic/rep1`: **PROBABLY** — Both sides engineer_guessable (v0 score=8, v1 score=20); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B025** `validate_email_like/security/anthropic/rep2`: **PROBABLY** — Both sides engineer_guessable (v0 score=8, v1 score=20); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B026** `validate_email_like/security/anthropic/rep3`: **PROBABLY** — Both sides engineer_guessable (v0 score=8, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B027** `validate_email_like/security/anthropic/rep4`: **PROBABLY** — Both sides engineer_guessable (v0 score=8, v1 score=20); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B028** `validate_email_like/security/anthropic/rep5`: **PROBABLY** — Both sides engineer_guessable (v0 score=8, v1 score=20); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B029** `dependency_order/security/openai/rep1`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=14); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B030** `dependency_order/security/openai/rep2`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B031** `dependency_order/security/openai/rep3`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B032** `dependency_order/security/openai/rep4`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=12); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B033** `dependency_order/security/openai/rep5`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=14); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B034** `merge_intervals/security/openai/rep3`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 2/10) [v0 guessable=no, v1 guessable=yes]
- **B035** `merge_intervals/security/openai/rep4`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 2/10) [v0 guessable=no, v1 guessable=yes]
- **B036** `merge_intervals/security/openai/rep5`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 2/10) [v0 guessable=no, v1 guessable=yes]
- **B037** `sanitize_filename/concurrency/openai/rep2`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B038** `sanitize_filename/concurrency/openai/rep3`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B039** `sanitize_filename/concurrency/openai/rep4`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B040** `sanitize_filename/security/openai/rep1`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=8); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B041** `sanitize_filename/security/openai/rep2`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=8); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B042** `sanitize_filename/security/openai/rep3`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=8); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B043** `sanitize_filename/security/openai/rep4`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=8); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B044** `sanitize_filename/security/openai/rep5`: **PROBABLY** — Both sides engineer_guessable (v0 score=6, v1 score=8); judge may use proxies but asymmetry not aligned with failure [v0 guessable=yes, v1 guessable=yes]
- **B045** `validate_email_like/concurrency/openai/rep1`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B046** `validate_email_like/concurrency/openai/rep3`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B047** `validate_email_like/concurrency/openai/rep4`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B048** `validate_email_like/concurrency/openai/rep5`: **NO** — Neither side engineer_guessable (v0 score=0, v1 score=0) [v0 guessable=no, v1 guessable=no]
- **B049** `validate_email_like/security/openai/rep3`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 0/8) [v0 guessable=no, v1 guessable=yes]
- **B050** `validate_email_like/security/openai/rep4`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 0/8) [v0 guessable=no, v1 guessable=yes]
- **B051** `validate_email_like/security/openai/rep5`: **UNCLEAR** — Mixed guessability (v0=False, v1=True, scores 2/8) [v0 guessable=no, v1 guessable=yes]

## PART 9 — Stripped analysis

- stripped_vs_original=persist: 37
- stripped_vs_original=disappear: 14

Category B **persists** under stripping in all complete cases: partial recovery is not an artifact introduced by strip; stripping does not convert B into strict success.

### Per-observation stripped vs original

- **B001** `dependency_order/concurrency/anthropic/rep1`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B002** `dependency_order/concurrency/anthropic/rep2`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B003** `dependency_order/concurrency/anthropic/rep3`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B004** `dependency_order/concurrency/anthropic/rep4`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B005** `dependency_order/concurrency/anthropic/rep5`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B006** `dependency_order/security/anthropic/rep1`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B007** `dependency_order/security/anthropic/rep3`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B008** `dependency_order/security/anthropic/rep4`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B009** `lru_cache/security/anthropic/rep5`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B010** `merge_intervals/concurrency/anthropic/rep1`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B011** `merge_intervals/concurrency/anthropic/rep2`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B012** `merge_intervals/concurrency/anthropic/rep3`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B013** `merge_intervals/concurrency/anthropic/rep4`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B014** `merge_intervals/concurrency/anthropic/rep5`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B020** `sanitize_filename/security/anthropic/rep2`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B021** `sanitize_filename/security/anthropic/rep3`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B022** `sanitize_filename/security/anthropic/rep4`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B023** `sanitize_filename/security/anthropic/rep5`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B024** `validate_email_like/security/anthropic/rep1`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B025** `validate_email_like/security/anthropic/rep2`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B026** `validate_email_like/security/anthropic/rep3`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B027** `validate_email_like/security/anthropic/rep4`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B028** `validate_email_like/security/anthropic/rep5`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B029** `dependency_order/security/openai/rep1`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B030** `dependency_order/security/openai/rep2`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B031** `dependency_order/security/openai/rep3`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B032** `dependency_order/security/openai/rep4`: original(v0=false, v1=true) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B033** `dependency_order/security/openai/rep5`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B034** `merge_intervals/security/openai/rep3`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B035** `merge_intervals/security/openai/rep4`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B036** `merge_intervals/security/openai/rep5`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B037** `sanitize_filename/concurrency/openai/rep2`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B038** `sanitize_filename/concurrency/openai/rep3`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B039** `sanitize_filename/concurrency/openai/rep4`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B040** `sanitize_filename/security/openai/rep1`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B041** `sanitize_filename/security/openai/rep2`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B042** `sanitize_filename/security/openai/rep3`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B043** `sanitize_filename/security/openai/rep4`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B044** `sanitize_filename/security/openai/rep5`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B045** `validate_email_like/concurrency/openai/rep1`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B046** `validate_email_like/concurrency/openai/rep3`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B047** `validate_email_like/concurrency/openai/rep4`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B048** `validate_email_like/concurrency/openai/rep5`: original(v0=true, v1=false) → stripped(v0=true, v1=false, strict=0) status=**persist**
- **B049** `validate_email_like/security/openai/rep3`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**
- **B050** `validate_email_like/security/openai/rep4`: original(v0=false, v1=true) → stripped(v0=true, v1=true, strict=1) status=**disappear**
- **B051** `validate_email_like/security/openai/rep5`: original(v0=false, v1=true) → stripped(v0=false, v1=true, strict=0) status=**persist**

## PART 10 — Reviewer #2 scientific interpretation

1. **Genuine evidence:** 0/51 (0.0%)
2. **Methodological artefacts:** 45/51 (88.2%)
3. **Ambiguous:** 6/51 (11.8%)

4. **Does Category B support a manifestation–recovery gap?**

**No, not in its current form.** Category B is predominantly partial recovery on pairs with high structural distance but (a) keyword baseline replicates the same asymmetry, (b) many cases are algorithm substitutions unrelated to the manipulated dimension, and (c) equivalence heuristics mark a substantial fraction as cosmetic or equivalent. The 51-count headline collapses into a handful of plausibly genuine cases.

5. **Would Category B survive TOSEM review today?**

**No.** A TOSEM reviewer would classify Category B as an artefact of (1) strict-recovery defined on two binary trials yielding partial failure cells, (2) manifestation_score conflating manipulation-unrelated rewrites with dimension manifestation, and (3) absence of a human oracle or behavioral test to validate semantic difference. The 51 cases would be reduced to a small case study at best.

---

## Per-observation index

- **B001** `dependency_order/concurrency/anthropic/rep1`: cluster=`non_dimension_algorithm_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B002** `dependency_order/concurrency/anthropic/rep2`: cluster=`non_dimension_algorithm_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B003** `dependency_order/concurrency/anthropic/rep3`: cluster=`non_dimension_algorithm_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B004** `dependency_order/concurrency/anthropic/rep4`: cluster=`non_dimension_algorithm_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B005** `dependency_order/concurrency/anthropic/rep5`: cluster=`non_dimension_algorithm_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B006** `dependency_order/security/anthropic/rep1`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B007** `dependency_order/security/anthropic/rep3`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B008** `dependency_order/security/anthropic/rep4`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B009** `lru_cache/security/anthropic/rep5`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=PROBABLY, interp=methodological_artefact
- **B010** `merge_intervals/concurrency/anthropic/rep1`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B011** `merge_intervals/concurrency/anthropic/rep2`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B012** `merge_intervals/concurrency/anthropic/rep3`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B013** `merge_intervals/concurrency/anthropic/rep4`: cluster=`v1_concurrency_surface_miss`, direction=v1_only_fail, equiv=Unclear, kw=yes, proxy=NO, interp=methodological_artefact
- **B014** `merge_intervals/concurrency/anthropic/rep5`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B015** `sanitize_filename/concurrency/anthropic/rep1`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B016** `sanitize_filename/concurrency/anthropic/rep2`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B017** `sanitize_filename/concurrency/anthropic/rep3`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B018** `sanitize_filename/concurrency/anthropic/rep4`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B019** `sanitize_filename/concurrency/anthropic/rep5`: cluster=`algorithm_api_substitution`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B020** `sanitize_filename/security/anthropic/rep2`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B021** `sanitize_filename/security/anthropic/rep3`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B022** `sanitize_filename/security/anthropic/rep4`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B023** `sanitize_filename/security/anthropic/rep5`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B024** `validate_email_like/security/anthropic/rep1`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B025** `validate_email_like/security/anthropic/rep2`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B026** `validate_email_like/security/anthropic/rep3`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B027** `validate_email_like/security/anthropic/rep4`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B028** `validate_email_like/security/anthropic/rep5`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Unclear, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B029** `dependency_order/security/openai/rep1`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B030** `dependency_order/security/openai/rep2`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B031** `dependency_order/security/openai/rep3`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B032** `dependency_order/security/openai/rep4`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B033** `dependency_order/security/openai/rep5`: cluster=`non_dimension_algorithm_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B034** `merge_intervals/security/openai/rep3`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous
- **B035** `merge_intervals/security/openai/rep4`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous
- **B036** `merge_intervals/security/openai/rep5`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous
- **B037** `sanitize_filename/concurrency/openai/rep2`: cluster=`v1_concurrency_surface_miss`, direction=v1_only_fail, equiv=Unclear, kw=yes, proxy=NO, interp=methodological_artefact
- **B038** `sanitize_filename/concurrency/openai/rep3`: cluster=`v1_concurrency_surface_miss`, direction=v1_only_fail, equiv=Unclear, kw=yes, proxy=NO, interp=methodological_artefact
- **B039** `sanitize_filename/concurrency/openai/rep4`: cluster=`v1_concurrency_surface_miss`, direction=v1_only_fail, equiv=Unclear, kw=yes, proxy=NO, interp=methodological_artefact
- **B040** `sanitize_filename/security/openai/rep1`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B041** `sanitize_filename/security/openai/rep2`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B042** `sanitize_filename/security/openai/rep3`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B043** `sanitize_filename/security/openai/rep4`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B044** `sanitize_filename/security/openai/rep5`: cluster=`algorithm_api_substitution`, direction=v0_only_fail, equiv=Definitely different, kw=yes, proxy=PROBABLY, interp=methodological_artefact
- **B045** `validate_email_like/concurrency/openai/rep1`: cluster=`v1_salient_dimension_edit`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B046** `validate_email_like/concurrency/openai/rep3`: cluster=`v1_salient_dimension_edit`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B047** `validate_email_like/concurrency/openai/rep4`: cluster=`v1_salient_dimension_edit`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B048** `validate_email_like/concurrency/openai/rep5`: cluster=`v1_salient_dimension_edit`, direction=v1_only_fail, equiv=Definitely different, kw=yes, proxy=NO, interp=methodological_artefact
- **B049** `validate_email_like/security/openai/rep3`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous
- **B050** `validate_email_like/security/openai/rep4`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous
- **B051** `validate_email_like/security/openai/rep5`: cluster=`v0_validation_surface_miss`, direction=v0_only_fail, equiv=Definitely different, kw=partial, proxy=UNCLEAR, interp=ambiguous