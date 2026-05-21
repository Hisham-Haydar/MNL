# RURO occ P3a Pooled — Gate-A Parse Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Gate-A verdict

**PASS WITH BLOCKER.**

GA1–GA16: all PASS.

GA17: PENDING. No cluster-robust SE method (sandwich estimator at
`cluster_id = idorighh`) exists in the current estimation engine
codebase. The cluster-robust SE infrastructure must be built and
confirmed callable before the pooled-estimation authorization memo
is issued.

**Pooled estimation execution is NOT authorized by this Gate-A audit.**

Pooled estimation execution requires:
1. Gate-A passing — satisfied by this audit (PASS WITH BLOCKER);
2. GA17 cluster-robust SE infrastructure blocker cleared — NOT YET
   SATISFIED; the sandwich-estimator build is the identified blocker;
3. A separate pooled-estimation authorization memo — NOT YET ISSUED.

**M1-clean 2016 remains the active JMP baseline.**

**Welfare computation is NOT authorized.**

---

## 2. YAML derivation record

**Source:** `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`

**Output:** `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`

**Changes made (exactly five, no others):**

| Field | Change |
|-------|--------|
| `specification.name` | `"ruro_occ_M1_clean"` → `"ruro_occ_P3a_pooled"` |
| `specification.description` | Updated to describe pooled three-year P3a spec (see YAML header) |
| `market_opportunity.shifters` | Added two entries after `beta_E_drgn8`: `beta_E_y2015` (`year_2015_indicator`) and `beta_E_y2017` (`year_2017_indicator`), both `interaction: ["working"]`, both `applies_to: "household"` |
| `initial_values` | Added `beta_E_y2015: 0.0` and `beta_E_y2017: 0.0` |
| `optimization.bounds` | Added `beta_E_y2015: [-5.0, 5.0]` and `beta_E_y2017: [-5.0, 5.0]` |

**Schema note:** The M1-clean YAML uses `coefficient` as the field name
in `market_opportunity.shifters` entries (not `name`). The two new
year-dummy entries follow the same schema: `variable`, `coefficient`,
`interaction`, `applies_to`. No field-name change was introduced.

**Frozen blocks (all confirmed byte-identical to M1-clean):**
- `utility` block (functional form, consumption config, leisure config)
- `hours_opportunity.shifters`
- `wage_opportunity` (mean_shifters, variance)
- `occupation_opportunity` (variable, reference, all 12 shifter entries)
- `couples.leisure_interaction`
- `optimization` settings (method, analytical_gradient, max_iterations,
  tolerance, gradient_tolerance, disp, iprint)
- `optimization.expression_constraints` (both constraints unchanged)
- `gradient_verification`
- All 53 M1-clean entries in `initial_values` (unchanged)
- All 53 M1-clean entries in `optimization.bounds` (unchanged)

---

## 3. Parser output

**Command:** `parse_specification('scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml')`

**Result:** Parsed without error.

**Parser-reported fields:**

| Field | Value |
|-------|-------|
| `name` | `ruro_occ_P3a_pooled` |
| `param_count` | **55** |
| `wage_spec` | `vw` |
| `model_family` | `regular` |
| `expression_constraints_enabled` | `True` |

**Full parameter list (55 parameters in parser order):**

```
 1  beta_l0_sm
 2  beta_l_age_sm
 3  beta_l_age2_sm
 4  beta_c_sm
 5  theta_l_sm
 6  beta_l0_sf
 7  beta_l_age_sf
 8  beta_l_age2_sf
 9  beta_l_nkids_sf
10  beta_c_sf
11  theta_l_sf
12  theta_c_singles
13  beta_l0_m
14  beta_l_age_m
15  beta_l_age2_m
16  theta_l_m
17  beta_l0_f
18  beta_l_age_f
19  beta_l_age2_f
20  beta_l_nkids_f
21  theta_l_f
22  beta_c
23  beta_E
24  beta_h_pt1
25  beta_h_pt2
26  beta_h_ft
27  beta_E_gsur
28  beta_E_drgn2
29  beta_E_drgn3
30  beta_E_drgn4
31  beta_E_drgn5
32  beta_E_drgn6
33  beta_E_drgn7
34  beta_E_drgn8
35  beta_E_y2015      ← NEW
36  beta_E_y2017      ← NEW
37  beta_occ_2_sm
38  beta_occ_3_sm
39  beta_occ_4_sm
40  beta_occ_2_sf
41  beta_occ_3_sf
42  beta_occ_4_sf
43  beta_occ_2_cm
44  beta_occ_3_cm
45  beta_occ_4_cm
46  beta_occ_2_cf
47  beta_occ_3_cf
48  beta_occ_4_cf
49  beta_w0
50  beta_w_educL
51  beta_w_educH
52  beta_w_pexp
53  beta_w_pexp2
54  sigma
55  beta_ll
```

Parameters #35–36 are the two new year-dummy entries. Parameters
#1–34 and #37–55 are identical to M1-clean parameters #1–34 and
#35–53 in parser order.

---

## 4. GA1–GA17 check results

| Check | Requirement | Result | Detail |
|-------|------------|--------|--------|
| GA1 | Pooled YAML exists | **PASS** | `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` created and present |
| GA2 | Pooled YAML parses without error | **PASS** | `parse_specification()` returned `EstimationSpec` with no exception |
| GA3 | `specification.name == ruro_occ_P3a_pooled` | **PASS** | Parser reports `name: ruro_occ_P3a_pooled` |
| GA4 | Parameter count = 55 | **PASS** | Parser reports `param_count: 55` (53 M1-clean + 2 year dummies) |
| GA5 | `beta_E_y2015` and `beta_E_y2017` present | **PASS** | Both present in `all_param_names` at positions 35 and 36 |
| GA6 | `beta_E_y2015` and `beta_E_y2017` have initial value 0.0 | **PASS** | `initial_values: beta_E_y2015=0.0, beta_E_y2017=0.0` |
| GA7 | `beta_E_y2015` and `beta_E_y2017` have bounds `[-5.0, 5.0]` | **PASS** | `bounds: beta_E_y2015=(-5.0, 5.0), beta_E_y2017=(-5.0, 5.0)` |
| GA8 | `beta_E_y2015` and `beta_E_y2017` enter `market_opportunity.shifters` | **PASS** | Both present in `spec.market_opportunity_shifters` |
| GA9 | `beta_E_y2015` and `beta_E_y2017` have `applies_to: household` | **PASS** | Both shifter entries have `applies_to: household` |
| GA10 | `beta_E_y2015` and `beta_E_y2017` interact with `["working"]` | **PASS** | Both shifter entries have `interaction: ["working"]` |
| GA11 | All M1-clean frozen blocks unchanged | **PASS** | utility, preferences, wage, hours, occupation, GSUR, region dummies, proposal/prior correction, expression constraints — all byte-identical; 0 M1-clean params missing; 0 extra params beyond M1-clean + year dummies |
| GA12 | `beta_E_gsur` and `beta_E_drgn2–beta_E_drgn8` present and unchanged | **PASS** | `beta_E_gsur` at position 27; `beta_E_drgn2–beta_E_drgn8` at positions 28–34; all present with same bounds `[-10.0, 10.0]` and initial value `0.0` as M1-clean |
| GA13 | Precompute smoke test (see §5) | **PASS** | year_tag==1: 423,500 rows; year_tag==3: 395,700 rows; all four subsets (singles×{1,3}, couples×{1,3}) non-empty |
| GA14 | GSUR completeness | **PASS** | singles rows: 500,700; gsur null for singles: 0. Couples rows: 743,800; gsur_male null: 0; gsur_female null: 0 |
| GA15 | CPI/real-income check | **PASS WITH NOTE** | `ils_dispy_real` null for couples rows (743,800 nulls); non-null for all 500,700 singles rows. For singles non-FR_2016: 332,980 of 333,100 rows have `ils_dispy_real ≠ ils_dispy` (CPI deflation confirmed active). Note: couples use gender-specific income columns (`ils_dispy_male`, `ils_dispy_female`); the scalar `ils_dispy_real` column is singles-only. This is a structural property of the parquet pipeline, not a data error. GA15 passes on the scalar column for singles; couples income handling is deferred to the execution-authorization review. |
| GA16 | Cluster key check (bounded sample) | **PASS** | Row group 0 sample: 1,048,576 rows; `cluster_id == idorighh` for all 1,048,576 sampled rows (100%). This is a bounded Gate-A confirmation on row group 0, not a full-data scan. |
| GA17 | Cluster-robust SE infrastructure status | **PENDING** | See §6 for full detail |

**GA1–GA16: all PASS (GA15 with a structural note).**

**GA17: PENDING.**

---

## 5. Precompute smoke test

**GA13 — year indicator construction:**

Bounded read of `year_tag` column (full column, 1,244,500 rows as
a single columnar read; parquet metadata confirms 2 row groups):

| `year_tag` value | Row count | Mapping |
|-----------------|-----------|---------|
| 1 (FR_2015) | 423,500 | `year_2015_indicator = (year_tag == 1)` |
| 2 (FR_2016) | 425,300 | reference year (omitted) |
| 3 (FR_2017) | 395,700 | `year_2017_indicator = (year_tag == 3)` |
| **Total** | **1,244,500** | |

Subsets by household type (bounded read of `year_tag` and
`household_type`):

| Household type | year_tag==1 | year_tag==3 | Non-empty? |
|----------------|------------|------------|-----------|
| singles | 166,900 | 166,200 | YES |
| couples | 256,600 | 229,500 | YES |

`year_2015_indicator` can be constructed as `(year_tag == 1)` on
both singles and couples subsets: confirmed.

`year_2017_indicator` can be constructed as `(year_tag == 3)` on
both singles and couples subsets: confirmed.

**GA13: PASS.**

---

## 6. Cluster-robust SE infrastructure status

**GA17 finding: PENDING.**

The following files were inspected for cluster-robust SE
infrastructure:

| File | Cluster-robust SE method? |
|------|--------------------------|
| `scripts/enhanced/estimation_engine.py` | No — grep for `cluster`, `sandwich`, `robust`, `hessian`, `vcov`, `covariance` returns zero matches. The file contains only the objective/gradient computation. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | No — same grep returns zero matches. The GAMSPy solver wrapper calls CONOPT but contains no SE computation. |
| `scripts/enhanced/compute_standard_errors.py` | No — contains `compute_hessian_se()` (numerical Hessian via central differences → matrix inversion → Moore-Penrose fallback). No cluster argument, no score-matrix computation, no sandwich formula. |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | No — contains `compute_standard_errors()` (numerical Hessian, same design as the module above). Lines 179–294 implement Hessian-based SEs only; no cluster-id parameter, no meat-matrix computation. |

**Current SE implementation:** Hessian-based only. The standard-error
pipeline computes numerical second derivatives of the log-likelihood,
inverts the Hessian, and reports diagonal SEs. This is the
conventional MNL sandwich with identity meat — correct for i.i.d.
observations, but does not cluster at `idorighh`.

**What is missing for cluster-robust inference:** A sandwich estimator
of the form V = H⁻¹ · B · H⁻¹ where:
- H is the 55×55 observed Hessian (available from current code).
- B = Σⱼ sⱼ sⱼᵀ is the meat matrix, with sⱼ = Σᵢ∈Cⱼ ∇ᵢ log L the
  summed score vector for cluster j (household idorighh = j), summed
  over all draw-expanded rows belonging to that household.
- The sum is over all J = 9,657 distinct idorighh values.

Neither the score-matrix computation (∇ᵢ log L per row) nor the
meat-matrix assembly (Σᵢ∈Cⱼ per cluster) exist in the current
codebase.

**Implication:** The cluster-robust SE infrastructure build is the
blocker between this Gate-A audit and the pooled-estimation
authorization memo. Under the corrected Gate-A verdict semantics
(design memo correction §6), this produces a **PASS WITH BLOCKER**
outcome: GA1–GA16 pass, GA17 is PENDING, and the blocker must be
cleared before the execution-authorization memo is issued.

---

## 7. What was not run

- No estimation was run.
- No solver was invoked.
- No optimisation was performed.
- No welfare computation was performed.
- No welfare-related code was written or run.
- The pooled parquet was not modified; only schema and selected column
  reads were performed (bounded reads for GA13–GA16).
- The M1-clean YAML was not modified.
- The M1-naive YAML was not modified.
- No pooled-estimation authorization was issued.
- No canonical promotion of any output was performed.

**Data read scope (Gate-A bounded-read rule applied):**

| Column(s) read | Purpose | Read scope |
|----------------|---------|------------|
| Schema only | GA1–GA12 (structural checks) | Full schema, dtypes only |
| `year_tag` | GA13 | Full column (columnar read, 1,244,500 values, single pyarrow column array) |
| `year_tag`, `household_type` | GA13 singles/couples split | Full columns |
| `household_type`, `gsur`, `gsur_male`, `gsur_female` | GA14 | Full columns |
| `ils_dispy_real`, `ils_dispy`, `year_tag`, `household_type` | GA15 | Full columns |
| `cluster_id`, `idorighh` | GA16 | Row group 0 only (1,048,576 rows — bounded sample) |

No full 1,244,500-row materialisation into a single in-memory
DataFrame was performed. All reads were columnar via PyArrow.

---

## 8. Immediate next step

**The immediate next step is the cluster-robust SE infrastructure
build (the GA17 blocker).**

Gate-A is PASS WITH BLOCKER. The pooled YAML is valid
(`estimation_spec_ruro_occ_P3a_pooled.yaml`, 55 parameters, parses
correctly, all frozen blocks intact) and the pooled data input is
structurally confirmed (GA13–GA16 all pass). The pipeline is
unblocked at the YAML-and-data level.

The only remaining gate between Gate-A and the execution-
authorization memo is the cluster-robust SE infrastructure (GA17
PENDING). The build task is:

- Implement a sandwich-SE computation that accepts a `cluster_id`
  column, computes the per-row score vectors ∇ᵢ log L, aggregates
  them to the cluster level (sum over draw-expanded rows for each
  `idorighh`), assembles the meat matrix B = Σⱼ sⱼ sⱼᵀ over 9,657
  clusters, and returns V = H⁻¹ · B · H⁻¹.
- Confirm the implementation is callable on the pooled parquet with
  cluster key `cluster_id = idorighh` and 9,657 unique clusters.
- Record the confirmation in the pooled-estimation authorization memo.

**After the GA17 blocker is cleared:**

The pooled-estimation authorization memo may be drafted. That memo
authorises the three-start estimation
(`--solver gamspy-conopt --vectorized`, starts from M1-clean warm,
spec defaults, and perturbed M1-clean) and the SA2 post-estimation
diagnostics. The memo is a separate document; it is not authorised by
this Gate-A audit.

**GA15 structural carry-forward note (required in the authorization
chain).** The `ils_dispy_real` column in the pooled parquet is
singles-only: it is non-null for all 500,700 singles rows and null
for all 743,800 couples rows. Couples real income enters the
estimation engine via the gender-specific columns `ils_dispy_male`
and `ils_dispy_female` (both present in the parquet schema), which
carry the CPI-deflated disposable income for each partner. The scalar
`ils_dispy_real` column is not the couples income variable.

This is a structural property of the pooled parquet pipeline, not a
data error. It does not invalidate Gate-A or the pooled construction.
However, it must be explicitly acknowledged in the pooled-estimation
authorization memo and in any cluster-robust SE implementation that
reads income data, so that no downstream step assumes `ils_dispy_real`
covers couples rows. The authorization memo must confirm that the
estimation engine reads `ils_dispy_male` / `ils_dispy_female` for
couples and `ils_dispy_real` for singles (matching the existing
single-year M1-clean engine behaviour), and that the CPI deflation is
correctly applied to both the scalar and gender-specific columns.

**Required final statements:**

**Gate-A verdict: PASS WITH BLOCKER.**

**GA1–GA16: all PASS.**

**GA17: PENDING.** No cluster-robust SE method (sandwich estimator
clustered at `idorighh`) exists in the current codebase. The
cluster-robust SE infrastructure build is the blocker.

**Pooled estimation execution is NOT authorized by this Gate-A audit.**

**Pooled estimation execution requires:** (1) Gate-A passing — met by
this audit; (2) GA17 cluster-robust SE infrastructure blocker
cleared; (3) a separate pooled-estimation authorization memo.

**M1-clean 2016 remains the active JMP baseline.**

**Welfare computation is NOT authorized.**