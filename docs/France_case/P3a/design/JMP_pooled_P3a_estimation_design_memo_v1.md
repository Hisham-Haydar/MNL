# JMP Pooled P3a Estimation — Design Memo v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This memo specifies the pooled MNL estimation design for the JMP's
multi-year P3a extension. It covers the pooled specification (the
mapping from the single-year M1-clean baseline to the pooled setting),
the treatment of year effects, the treatment of GSURv2 opportunity
rates, the draw-expanded stacking structure, the cluster-robust
inference design, the Gate-A validation requirements, and the SA2
verdict criteria.

This memo is a **design document only**. It does not authorise
pooled estimation execution. Execution requires a separate pooled-
estimation authorization memo issued after this design is reviewed
and accepted. This memo does not authorise welfare computation,
welfare implementation, canonical MNL promotion, or displacement of
the M1-clean single-year baseline.

Governing evidence chain:

- `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` — the
  P3a GSURv2 pooled dataset is valid as the final non-provisional
  construction input for pooled-estimation design and Gate-A
  validation (PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC
  CAVEATS).
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` — M1-clean is the active
  JMP structural specification; pooled specification must be grounded
  in M1-clean parameter structure.
- `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`
  and `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_V9_validation_patch_note_v1.md` — minor
  documentation and validation-spec items resolved; no impact on
  construction input validity.

---

## 2. Current empirical status

| Item | Status |
|------|--------|
| Active single-year baseline | `ruro_occ_M1_clean` — SA1-STANDS with documented qualifications; LL = −6487.5522; 53 free parameters |
| Pooled dataset | `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` — `gsurv2_opportunity_year_aligned`; V1–V9 PASS; 1,244,500 rows; 12,445 household-years; 9,657 unique clusters |
| Pooled estimation | NOT YET AUTHORIZED |
| Welfare computation | NOT AUTHORIZED |
| M1-naive robustness | Estimated; verdict pending at time of this memo |
| SA2 verdict | Not yet issued; requires pooled estimation to be run and accepted |

The construction verdict establishes that the dataset is ready; this
memo establishes what the estimation specification should be. The
estimation authorization memo is the gate between this design and
execution.

---

## 3. Why pooled estimation is now design-ready but not execution-ready

**Design-ready:** The GSURv2 P3a pooled construction verdict is PASS.
The harmonised parquet carries the correct provenance label, the correct
cluster key, GSURv2 opportunity rates verified by SHA-256, and V1–V9 all
PASS. There is no pending data or construction item that would require
design decisions to be revisited.

**Not execution-ready:** Three preconditions remain unmet.

(P1) **This design memo is not an authorization.** Pooled estimation
requires a dedicated authorization memo that reviews the specification
defined here, confirms the data input, confirms the inference design,
and explicitly authorises execution. That memo has not been written.

(P2) **No pooled YAML has been written or parsed.** The pooled
specification exists here as a design; the Gate-A static checks
(parameter count, frozen-block preservation, YAML parse) have not yet
been run.

(P3) **Cluster-robust SE infrastructure.** The single-year estimation
engine uses a standard GAMSPy/CONOPT solver. Running cluster-robust
inference on a draw-expanded dataset of 1,244,500 rows with a 53+ parameter
specification requires confirming that the estimator's Hessian
computation handles the clustered structure correctly and that the
reported SEs are valid under the sandwich estimator. This confirmation
is required before execution authorization is issued.

None of these preconditions is a data or specification problem; all
three are procedural steps whose completion will not require revisiting
the decisions in this memo.

---

## 4. Active baseline and candidate pooled baseline

**Active baseline:** `ruro_occ_M1_clean`

- Single-year: FR_2016 only.
- 53 free parameters: 12 singles preference + 10 couples preference +
  1 household leisure interaction + 4 hours opportunity + 1 GSUR
  opportunity (`beta_E_gsur`) + 1 baseline employment shifter
  (`beta_E`) + 7 region dummies (`beta_E_drgn2`–`beta_E_drgn8`) +
  12 occupation opportunity + 6 wage/Mincer.
- LL = −6487.5522 (on FR_2016; 4,253 households; 425,300 draw-expanded
  rows).
- Key finding: `beta_E_gsur` = −1.329 (within-region education-sex
  variation in GSURv2), seven region dummies jointly significant
  (W = 28.18, p = 0.0002), strong leisure complementarity (`beta_ll`
  = 2.617, t = 7.48), preference block stable relative to
  M0c_b2_GSURv2.

**Candidate pooled baseline:** `ruro_occ_P3a_pooled` (to be named in
the YAML). The pooled specification pools FR_2015, FR_2016, FR_2017
under shared structural parameters, with year-specific GSUR opportunity
rates (from the GSURv2 lookup) and optional year-effect controls.

The candidate pooled baseline is not yet estimated. It is not yet
the active JMP baseline and does not displace M1-clean until an SA2
verdict is issued.

---

## 5. Pooled data input

**Input file:**
`Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`

Properties:

| Property | Value |
|----------|-------|
| Rows | 1,244,500 |
| Columns | 146 |
| File size | 185.5 MB |
| Survey years | FR_2015, FR_2016, FR_2017 |
| Opportunity years | y2014 (for FR_2015), y2015 (for FR_2016), y2016 (for FR_2017) |
| Provisioning label | `gsurv2_opportunity_year_aligned` |
| Household-years | 12,445 |
| Unique clusters (`cluster_id = idorighh`) | 9,657 |
| Draws per household-year | 100 |
| Household types | `singles`, `couples` |
| CPI base year | 2016 |
| Deflated income columns | `ils_dispy_real`, `ils_earns_real`, `yem_real` |
| Active GSUR columns | `gsur` (singles), `gsur_female` / `gsur_male` (couples) |

The estimation must use `ils_dispy_real` (not `ils_dispy`) as the
real-income variable throughout. The `gsur`, `gsur_female`, and
`gsur_male` columns carry the GSURv2 opportunity-year-aligned rates
confirmed by V8 to be complete for all active records.

The stacked-raw parquet
(`Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet`) is
the pre-CPI version; it must not be used as the estimation input.

---

## 6. Required pooled MNL base

The pooled specification is derived directly from the M1-clean
single-year specification. The pooling extension changes two things
and nothing else:

1. **Observation scope:** The dataset spans three survey years instead
   of one; the likelihood sums over all household-year draws.
2. **Year-effect controls:** Year fixed effects (year dummies or
   equivalents) are added to the market-opportunity index to absorb
   time-varying aggregate labour-market conditions not captured by the
   GSURv2 rates.

Everything in the M1-clean specification — the utility functional form,
the preference parameters, the household leisure interaction, the
Mincer wage block, the occupation shifters, the hours-opportunity
parameters, the prior-correction block, the expression constraints,
the `beta_E_gsur` GSUR loading, the seven region dummies — is carried
forward without modification in structure or in the parameter count per
block.

The pooled specification does not re-estimate a fundamentally different
model; it re-estimates the M1-clean model on the three-year panel with
year controls. The interpretation of shared structural parameters is
the JMP's central claim about parameter stability.

---

## 7. Baseline specification to pool

The pooled YAML must be derived from
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
(53 free parameters). Derivation steps:

1. Copy the M1-clean YAML as the starting document.
2. Update `specification.name` to `ruro_occ_P3a_pooled` (or the
   agreed name).
3. Update `specification.description` to describe the pooled
   three-year specification.
4. Add the year-effect parameters to the `market_opportunity.shifters`
   block (see §8 below).
5. Update `initial_values` for the new year-effect parameters.
6. Update `optimization.bounds` for the new year-effect parameters.
7. Do not change any other field.

Gate-A parse requirements (must pass before execution authorization):

- Parameter count = 53 (M1-clean) + k year-effect parameters, where
  k is determined by the year-effect design in §8.
- All M1-clean frozen blocks preserved byte-for-byte (utility,
  preference, occupation, wage, hours, prior-correction,
  expression-constraints).
- `beta_E_gsur` entry present and unchanged.
- All seven `beta_E_drgn{2..8}` entries present and unchanged.
- New year-effect parameters present with correct `applies_to` field.

---

## 8. Treatment of year effects

**Decision: add two year dummy shifters in the market-opportunity
index, using FR_2016 as the omitted reference year.**

The three-year panel spans FR_2015, FR_2016, FR_2017. The GSURv2
rates are opportunity-year-aligned and absorb within-region
education-sex variation in unemployment; they do not absorb aggregate
year-to-year macroeconomic movements. Year fixed effects in the
opportunity index control for residual aggregate time trends.

**Specification:**

Add `beta_E_y2015` and `beta_E_y2017` to `market_opportunity.shifters`:

```yaml
- name: beta_E_y2015
  variable: year_2015_indicator
  applies_to: household
  description: "Year 2015 fixed effect in employment opportunity (ref: FR_2016)"

- name: beta_E_y2017
  variable: year_2017_indicator
  applies_to: household
  description: "Year 2017 fixed effect in employment opportunity (ref: FR_2016)"
```

where `year_2015_indicator` and `year_2017_indicator` are binary
indicators derived from `year_tag == 1` and `year_tag == 3`
respectively, available (or constructible at precompute time) from the
`year_tag` column in the parquet.

**Rationale for FR_2016 as reference year:**

FR_2016 is the survey year used for the M1-clean single-year
estimation. Using FR_2016 as the reference ensures that the pooled
`beta_E` and region-dummy estimates are anchored to the same year as
the M1-clean estimates, facilitating direct SA2 comparison. It also
makes the pooled single-year posterior for FR_2016 (with
`year_2015_indicator = year_2017_indicator = 0`) directly comparable
to the M1-clean posterior.

**Parameter count adjustment:**
Pooled parameter count = 53 (M1-clean) + 2 (year dummies) = **55 free
parameters**.

**Alternative treatment (sensitivity):**

A fully year-interacted specification — where year interacts with all
opportunity parameters — is a natural robustness check for the
assumption that structural parameters are constant across years. This
is not the baseline specification design; it is a post-SA2 sensitivity
that would require a separate authorization.

---

## 9. Treatment of GSURv2

**Decision: carry `beta_E_gsur` forward without modification. Use the
`gsur` / `gsur_female` / `gsur_male` columns from the harmonised
parquet as the active GSUR variable.**

The GSURv2 opportunity-year-aligned rates are embedded in the parquet:
`gsur` for singles, `gsur_female` and `gsur_male` for couples. These
are the output of the GSURv2 MNL-parquet rebuild verified by V1–V12 in
`Results/P3a/gsurv2/JMP_GSURv2_MNL_rebuild_report_v2.md`.

The `gsur` / `gsur_female` / `gsur_male` columns in the pooled parquet
carry year-specific opportunity-year-aligned rates: for a FR_2015 row,
`gsur` is the y2014 GSURv2 rate; for a FR_2016 row, `gsur` is the y2015
GSURv2 rate; and so on. The `beta_E_gsur` parameter estimate in the
pooled specification therefore captures the within-region education-sex
variation in GSURv2 rates pooled across three years and three opportunity
years.

**Deflation exclusion:** The GSUR columns are proportions (not monetary
variables) and must not be deflated. The config field
`variables_excluded_from_deflation` in
`config/multi_year/fr_p3a_gsurv2_stage_m1.yaml` already lists `gsur`.
The estimation YAML must not include `gsur`, `gsur_female`, or
`gsur_male` in any CPI-deflation list.

**v1-fallback columns preserved but unused:** The parquet also carries
`gsur_v1_fallback`, `gsur_female_v1_fallback`, and `gsur_male_v1_fallback`
columns from the GSURv2 rebuild. These must not be used as GSUR inputs
to the pooled estimation. They are retained for provenance and for
GSURv2-vs-v1 comparison diagnostics only.

---

## 10. Treatment of region dummies

**Decision: carry all seven region dummies forward from M1-clean
without modification. FR_2016 drgn1=1 (Île-de-France) remains the
reference category.**

The seven region dummies `beta_E_drgn2` through `beta_E_drgn8`
(EUROMOD `drgn1` values 2–8) are structural parameters capturing
regional employment-opportunity differentials. Their inclusion in the
pooled specification is mandated by the M1-clean design.

The pooled dataset's region variable is `drgn1` (carried through from
the upstream EUROMOD parquets into the pooled stacked file). Households
that appear in multiple survey years contribute region-dummy observations
in all years in which they appear; region is assumed time-invariant
within the panel (households do not change region between FR_2016 and
FR_2017 in the MNL sample). The repeated-observation structure does not
introduce any new interpretation of the region-dummy coefficients.

For singles, the parquet also carries pre-computed indicator columns
`reg_nuts1_1` through `reg_nuts1_8` (confirmed present by column
inspection). For couples, the indicators must be constructed at precompute
time via `(drgn1 == k).astype(float)`, as in the M1-clean estimation.

**SA2 comparison:** The primary SA2 stability test for the region block
is whether the seven `beta_E_drgn{k}` estimates in the pooled run
remain directionally consistent with M1-clean and within a
quantitatively plausible range given the expanded sample. A major sign
reversal or dramatic shrinkage to zero in the pooled estimates would
be diagnostically informative and would require explanation.

---

## 11. Treatment of preferences

**Decision: pool all preference parameters across years and household
types under the assumption of time-invariant preferences. Do not add
year-interacted preference terms.**

The preference block — singles utility (`beta_c_sm`, `beta_c_sf`,
`theta_c_singles`, `beta_l_sm`, `beta_l_sf`, `theta_l_sm`, `theta_l_sf`,
and five more singles parameters), couples utility (`beta_c_m`,
`beta_c_f`, `theta_l_m`, `theta_l_f`, and six more couples parameters),
and household leisure interaction (`beta_ll`) — is carried forward
without modification from M1-clean.

**Rationale:** The JMP's identification strategy rests on cross-sectional
within-year variation in wages, hours, occupations, and the GSUR rates.
Year-to-year preference variation is not identified without strong
additional assumptions (preference shifters or instruments for aggregate
taste changes). The assumption of time-invariant preferences is
maintained across the three survey years FR_2015, FR_2016, FR_2017.

**Singles consumption identification limitation:** The three parameters
`beta_c_sm`, `beta_c_sf`, `theta_c_singles` exhibit near-singular joint
identification in M1-clean (negative diagonal Hessian entries; no
valid SEs). This limitation is structurally inherited and will persist
in the pooled run. The expanded sample (three years vs one) may
marginally improve identification, but this is not guaranteed. The
pooled SA2 Hessian diagnostics must report the same sub-block check
as M1-clean (eigenvalues of the three-by-three sub-block; number of
NA SEs).

---

## 12. Treatment of opportunity parameters

**Decision: pool hours-opportunity, wage-opportunity, and occupation-
opportunity parameters across years. Keep `beta_E` and `beta_E_gsur`
pooled. Add year dummies in the market-opportunity index only (§8).**

The opportunity block divides into:

- **Market opportunity (shared):** `beta_E` (baseline employment
  shifter), `beta_E_gsur` (GSUR loading), `beta_E_drgn2`–`beta_E_drgn8`
  (region dummies), `beta_E_y2015` and `beta_E_y2017` (new year
  dummies, §8). Pooled with year controls absorbing aggregate
  time trends.
- **Hours opportunity (shared):** `beta_h_pt1`, `beta_h_pt2`,
  `beta_h_ft` (hours-band shifters), carried forward from M1-clean.
- **Wage opportunity (shared):** `beta_w0`, `beta_w_educL`,
  `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` (Mincer +
  dispersion), carried forward from M1-clean.
- **Occupation opportunity (shared):** twelve occupation shifters
  for couples-male and couples-female, carried forward from M1-clean.

The use of `ils_dispy_real` (CPI-deflated, base 2016) ensures that
the wage utility terms are on a consistent real scale across the three
survey years. The deflation is already applied in the harmonised
parquet via the Stage M1 CPI step.

**Year-interaction sensitivity:** Whether `beta_E_gsur` should vary
by year (i.e., whether the GSUR loading is year-stable) is a natural
robustness question. A year-interacted GSUR parameter
(`beta_E_gsur_y2015`, `beta_E_gsur_y2016`, `beta_E_gsur_y2017`)
is a sensitivity specification, not the baseline. The SA2 verdict
design in §21 specifies how to evaluate the pooled `beta_E_gsur`
stability.

---

## 13. Treatment of singles and couples

**Decision: maintain the M1-clean structure in which singles and
couples are estimated jointly with household-type-specific columns
resolved by the estimator's variable resolver. Do not separate the
pooled dataset into singles-only and couples-only estimation runs.**

The harmonised parquet contains both household types in a single file,
distinguished by the `household_type` column (`"singles"` or
`"couples"`). The schema-union structure means that singles-only
columns (`gsur`, `dag`, etc.) are NaN for couples rows, and couples-
only columns (`gsur_female`, `gsur_male`, `dag_female`, `dag_male`,
etc.) are NaN for singles rows.

The M1-clean estimation handles this via the estimator's variable
resolver, which applies the correct variable per household type. The
pooled estimation must use the same resolver logic.

**Singles consumption identification caveat** (from §11) applies
across all three survey years in the pooled run.

**Household-type counts in the pooled dataset:**

| Year | Singles rows | Singles HH | Couples rows | Couples HH |
|------|-------------|-----------|-------------|-----------|
| FR_2015 | 166,900 | 1,669 | 256,600 | 2,566 |
| FR_2016 | 167,600 | 1,676 | 257,700 | 2,577 |
| FR_2017 | 166,200 | 1,662 | 229,500 | 2,295 |
| **Total** | **500,700** | **5,007** | **743,800** | **7,438** |

---

## 14. Treatment of draw-expanded structure

**Decision: the pooled estimation is run on the draw-expanded 1,244,500-
row dataset. The likelihood is the same draw-expansion averaging used
in the single-year estimation.**

The pooled parquet is draw-expanded: each household-year contributes
100 draws (indexed by the `draw` column, values 0–99). The 1,244,500
rows correspond to 12,445 household-years × 100 draws. The
`(stacked_person_uid, draw)` pair is row-unique (confirmed by V1 of
the construction validation).

The RURO MNL estimator averages the simulated choice probabilities
over the 100 draws per household before summing the log-likelihood
contribution. This draw-averaging structure is unchanged from the
single-year estimation; the pooled run stacks the three survey years
and sums the log-likelihood over all 12,445 household-years.

**Draw identification:** the `draw` column (integer 0–99) is present in
the pooled parquet and can be used by the estimator to group draws
within a household-year before averaging.

**Computational scale:** 1,244,500 rows is approximately 2.93× the
FR_2016 single-year estimation size (425,300 rows). Walltime should
scale sub-linearly with row count if the estimator vectorises across
draws; a rough estimate is 3–6× the single-year walltime per start,
approximately 1,000–2,100 seconds per start with GAMSPy-CONOPT.

---

## 15. Cluster-robust inference requirement

**The pooled estimation must produce cluster-robust standard errors.
Unadjusted Hessian-based SEs are not acceptable as the reported
inference for the pooled specification.**

**Why clustering is required:** The pooled dataset contains two
sources of within-cluster correlation that make OLS/Hessian SEs
invalid:

1. **Household-level correlation across years.** Households that
   appear in both FR_2016 and FR_2017 (the 2,788 repeat-HH records;
   see §17) contribute correlated observations within the cluster
   `idorighh`. Even if the structural model is correctly specified,
   the log-likelihood curvature at the ML estimate does not account
   for this within-household correlation. Hessian-based SEs computed
   from the full-data Hessian will under-state uncertainty for
   parameters identified off between-year variation.

2. **Draw-level correlation within household-years.** The 100 draws
   per household-year are correlated by construction (they are
   alternative simulations of the same household's latent preference).
   The likelihood correctly averages over draws; but the sandwich
   estimator applied at the `idorighh` level simultaneously handles
   the draw correlation and the cross-year household correlation.

**Inference method:** The sandwich (Huber-White) variance-covariance
estimator clustered at `cluster_id = idorighh`. The cluster-robust
VCV is:

```
Σ_cluster = H^{-1} · B · H^{-1}
```

where H is the Hessian of the log-likelihood at the ML estimate and B
is the meat matrix:

```
B = Σ_{c=1}^{9657} ( Σ_{i ∈ cluster c} s_i )( Σ_{i ∈ cluster c} s_i )^T
```

with s_i the gradient contribution (score) of observation i.
Observations here are draw-averaged log-likelihood contributions per
household-year; the cluster sum runs over all household-year
appearances of cluster c across all years.

**Implementation prerequisite (§3 P3):** Confirm that the estimation
engine (`scripts/enhanced/gamspy_estimation_vectorized.py` and/or
`scripts/enhanced/estimation_engine.py`) can compute the score matrix
at the cluster level and compute the sandwich VCV. This must be
confirmed in the execution authorization memo before pooled estimation
is authorised.

---

## 16. Cluster key

**`cluster_id = idorighh`**

The cluster key is the original EU-SILC household identifier
`idorighh`, which persists across survey years for households that
appear in multiple waves. The `cluster_id` column in the harmonised
parquet is a direct copy of `idorighh` (confirmed by V6 of the
construction validation and by `m1_add_cluster_key.py`).

| Property | Value |
|----------|-------|
| Cluster key column | `cluster_id` |
| Source column | `idorighh` |
| Unique cluster count | 9,657 |
| Total household-year observations | 12,445 |
| Average household-year appearances per cluster | 12,445 / 9,657 ≈ 1.29 |
| Clusters appearing in exactly one year | 9,657 − 2,788 = 6,869 |
| Clusters appearing in two or more years | 2,788 |

The cluster count (9,657) is the relevant quantity for asymptotic
cluster-robust inference, not the household-year count (12,445) or
the row count (1,244,500). With 9,657 clusters, asymptotic
approximations for the sandwich estimator are well-supported.

The cluster key must be used consistently: all standard-error
calculations, confidence intervals, hypothesis tests, and Wald
statistics reported in the SA2 verdict and in JMP text must be
based on the cluster-robust VCV. Unadjusted Hessian-based SEs
are acceptable only as a diagnostic comparison and must be labelled
as such.

---

## 17. Repeated-household diagnostic and V6 interpretation

**The 2016×2017 repeat-HH overlap in the RURO MNL sample is 2,788
households (not 8,796). This is the correct number to use for
inference design and for reporting.**

From the construction validation V6:

| Year pair | Observed (RURO MNL) | Nominal (full EU-SILC) | Diff |
|-----------|--------------------|-----------------------|------|
| 2015×2016 | 0 | 0 | 0 |
| 2015×2017 | 0 | 0 | 0 |
| 2016×2017 | **2,788** | ~8,796 | 6,008 |

The V6 construction verdict classified the discrepancy as
**diagnostic/non-blocking**. The 2,788 figure reflects the RURO
sampling restriction: only households in both the FR_2016 and FR_2017
RURO-eligible subsets contribute repeated observations. The V7
identity validation confirmed that the 2,788 repeat-HH records have
clean identity (sex stability 1.0000, age progression 1.0000,
suspicious rate 0.0000, household continuity 0.9985).

**Implications for inference design:**

1. The 2,788 repeat-HH households are the source of within-cluster
   correlation across years. Each of these 2,788 clusters contributes
   two household-year observations (FR_2016 and FR_2017), for a total
   of 5,576 observations from repeat-HH clusters. The remaining
   6,869 clusters contribute exactly one household-year observation
   each.

2. The sandwich estimator correctly handles this structure because
   it clusters at the `idorighh` level and sums score contributions
   across all household-year appearances of each cluster before
   computing the meat matrix.

3. The absence of FR_2015 cross-year repeat households means that
   the FR_2015 data contributes 4,235 independent singleton clusters.
   Any year-effect parameter identified partly off the FR_2015–FR_2016
   variation benefits from this independence.

4. The pooled SA2 verdict must report the 2,788 figure explicitly
   and must not use the nominal 8,796 as the description of the
   repeated-household structure.

---

## 18. Estimation starts and warm-start strategy

**Decision: three independent starts with warm-start from M1-clean
FR_2016 estimates as Start 1.**

**Start 1 — warm from M1-clean:**
Transfer all 53 M1-clean parameter values to the pooled starting
vector. Initialise the two new year-effect parameters
(`beta_E_y2015`, `beta_E_y2017`) at zero. The M1-clean estimates
provide a near-optimal starting point for the shared structural
parameters.

**Start 2 — specification defaults:**
Use YAML-specified initial values for all 55 parameters (the same
defaults used in M1-clean's Start 2). This provides an independent
check against Start 1 convergence.

**Start 3 — perturbed from M1-clean:**
Apply a random perturbation (seed 42, magnitude ±0.1) to the
Start 1 vector. This tests the sensitivity of the optimum to
the warm-start neighborhood.

All three starts must be run with `--solver gamspy-conopt --vectorized`
using the `.venv\Scripts\python.exe` interpreter.

**Convergence criterion:** All three starts must converge to the same
log-likelihood within 1 unit and to parameter vectors within 0.01 in
absolute value across all 55 parameters. If the starts converge to
clearly different log-likelihoods (> 5 units apart), the estimation
is not trusted and the SA2 verdict cannot be issued until the
convergence discrepancy is explained.

**Expected walltime:** approximately 1,000–2,100 seconds per start
(3–6× the M1-clean per-start time). The three-start protocol may
therefore require 3,000–6,300 seconds of compute. The estimation
authorization memo should note this.

---

## 19. Gate-A validation requirements

Gate-A validation must pass before the pooled estimation is authorised
for execution. The Gate-A protocol follows the same structure as the
M1-clean Gate-A (`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_gate_A_parse_report_v1.md`)
extended to the pooled specification.

**Required Gate-A checks:**

| Check | Requirement |
|-------|-------------|
| GA1 | Parameter count = 55 (53 M1-clean + 2 year dummies) |
| GA2 | `beta_E_gsur` present, unchanged structure |
| GA3 | All seven `beta_E_drgn{2..8}` present, unchanged structure |
| GA4 | `beta_E_y2015` and `beta_E_y2017` present, `applies_to: household` |
| GA5 | Utility block byte-identical to M1-clean YAML |
| GA6 | Preference block byte-identical to M1-clean YAML |
| GA7 | Occupation block byte-identical to M1-clean YAML |
| GA8 | Wage/Mincer block byte-identical to M1-clean YAML |
| GA9 | Hours-opportunity block byte-identical to M1-clean YAML |
| GA10 | Prior-correction block byte-identical to M1-clean YAML |
| GA11 | Expression-constraints block byte-identical to M1-clean YAML |
| GA12 | YAML parses without error using `estimation_spec_parser.py` |
| GA13 | Precompute smoke test: `year_2015_indicator` and `year_2017_indicator` successfully resolved on singles and couples subsets of the pooled parquet |
| GA14 | `gsur`, `gsur_female`, `gsur_male` columns present and non-null for their respective household types in the pooled parquet |
| GA15 | `ils_dispy_real` column present and non-null; `ils_dispy` (nominal) present and distinct from `ils_dispy_real` |
| GA16 | `cluster_id` column present; `cluster_id == idorighh` for all rows (re-confirm on execution input) |
| GA17 | Cluster-robust SE implementation confirmed callable on the pooled parquet with 9,657 clusters |

Gate-A must produce a parse report (`Results/P3a/pooled_P3a/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md`) recording all 17 checks. All checks must PASS before the pooled-estimation authorization memo is issued.

---

## 20. Post-estimation diagnostics

The pooled SA2 post-estimation diagnostics mirror the M1-clean
post-estimation protocol (`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md`
and `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`),
extended for the pooled setting.

**Required post-estimation diagnostics:**

(D1) **Parameter comparison table:** Pooled vs M1-clean, parameter by
parameter, for all 53 shared parameters. Maximum absolute shift and
relative shift per block. Required column: |Δ| absolute and relative.

(D2) **Participation fit by year and household type:** For each of the
six (year × household type) cells, predicted-minus-observed
participation rate. Comparison to M1-clean FR_2016 figures.

(D3) **Mean-hours fit by year and household type:** Analogous to D2.

(D4) **Hours-bin distribution L1 distance by year and household type:**
Flagging any group-year combination that regresses by more than the
M1-clean worst-case (singles male, L1 = 0.6945). The mechanism of
the regression must be diagnosed if observed.

(D5) **Hessian condition number and eigenvalue spectrum:** For the
full 55-parameter Hessian. Minimum and maximum eigenvalues; number
of near-zero (<1) and negative eigenvalues; condition number.
Comparison to M1-clean condition number (5.10 × 10¹⁰).

(D6) **Cluster-robust vs Hessian-based SE comparison:** For each of
the 55 parameters, the Hessian-based SE and the cluster-robust SE.
The ratio cluster-robust/Hessian provides a direct measure of the
clustering adjustment.

(D7) **Year-effect parameter significance:** t-statistics and p-values
for `beta_E_y2015` and `beta_E_y2017` under cluster-robust SEs.

(D8) **`beta_E_gsur` pooled vs M1-clean comparison:** Pooled estimate,
cluster-robust SE, t-stat, p-value. Comparison to M1-clean
`beta_E_gsur` = −1.329 (SE 0.163, t = −8.15). Any major shift
(> 30 per cent in magnitude) requires diagnosis.

(D9) **Region-dummy joint Wald test (cluster-robust):** Joint test on
the seven `beta_E_drgn{2..8}` parameters using the cluster-robust VCV
sub-block. Required: W statistic, d.f. = 7, p-value. Comparison to
M1-clean W = 28.18, p = 0.0002.

(D10) **GSUR-region Hessian sub-block:** Eigenvalues of the
8×8 sub-block spanning `beta_E_gsur` and the seven region dummies.
Minimum eigenvalue > 0 required for SA2-STANDS.

(D11) **Log-likelihood and information criteria:** Pooled LL, AIC,
BIC. Comparison to M1-clean (LL = −6487.55, AIC = 13081.1,
BIC = 13662.0); note that the sample is 2.93× larger so the
absolute LL is not directly comparable; compute normalised
pseudo-log-likelihood per observation for comparison.

(D12) **Multistart convergence summary:** LL and parameter-vector L∞
distance across the three starts. Required: all starts converge to
within 1 LL unit and 0.01 parameter units.

---

## 21. SA2 verdict criteria

The SA2 verdict is the pooled counterpart of the SA1 verdict issued
for M1-clean. It is not issued automatically on construction-PASS; it
requires that the pooled estimation is run, that the post-estimation
diagnostics are complete, and that the following criteria are evaluated.

**SA2-STANDS criteria (all must hold for the pooled specification to be
accepted):**

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| S1 | All three starts converge to the same LL within 1 unit | §18 |
| S2 | Pooled `beta_E_gsur` significant at p < 0.01 (cluster-robust) | D8 |
| S3 | Pooled `beta_E_gsur` within 50% of M1-clean magnitude (−1.329) | D8 |
| S4 | Region-dummy joint Wald test: p < 0.01 (cluster-robust) | D9 |
| S5 | GSUR-region Hessian sub-block: no negative eigenvalues | D10 |
| S6 | Preference block: maximum |Δ| < 10% relative to M1-clean | D1 |
| S7 | `beta_ll` remains strongly positive (t > 5, cluster-robust) | D1 |
| S8 | No new negative-diagonal Hessian entries beyond M1-clean's 3 | D5 |
| S9 | Gate-A GA1–GA17: all PASS | §19 |
| S10 | Participation fit: no group-year regresses by more than 2 pp relative to M1-clean FR_2016 | D2 |
| S11 | Mean-hours fit: no group-year mean-hours regression exceeds 0.5 hours relative to M1-clean FR_2016 | D3 |

**SA2-QUALIFIED situations (pooled accepted with documented qualification):**

- Individual region dummy insignificant in pooled but jointly
  significant block (analogous to M1-clean Q1).
- Singles-male hours-bin L1 regression (analogous to M1-clean Q3),
  if traceable to the same region-shifter mechanism.
- Participation-fit regression for a single group-year combination
  that falls between 1 and 2 percentage points, where the mechanism
  is identifiable.

**SA2-REVISION situations (pooled specification requires revision):**

- `beta_E_gsur` changes sign in the pooled run (becomes positive).
- Preference block maximum |Δ| > 20% relative to M1-clean.
- Year-effect parameters `beta_E_y2015` or `beta_E_y2017` are large
  in magnitude (> 2.0 in absolute value) and absorb most of the
  cross-year variation, leaving other parameters poorly identified.
- More than 3 new negative-diagonal Hessian entries beyond M1-clean's
  existing 3.
- Convergence failure: starts converge to different LL values > 5
  units apart.

**SA2-FAIL situations (pooled specification rejected):**

- Any S1–S11 criterion fails without a documented SA2-QUALIFIED path.
- A data-integrity problem in the pooled parquet identified during
  estimation (column missing, wrong GSUR year, deflation error).

---

## 22. What pooled estimation may and may not claim

**A pooled specification that receives SA2-STANDS may claim:**

- That the M1-clean structural parameters are stable across the three
  survey years FR_2015, FR_2016, and FR_2017 (subject to the SA2
  qualification list).
- That the within-region GSURv2 loading `beta_E_gsur` is identified
  off three years of opportunity-year-aligned rates and remains
  significant.
- That the region-opportunity differentials estimated from the pooled
  data are consistent with the single-year M1-clean estimates.
- That the pooled log-likelihood and fit diagnostics support
  parameter stability.

**A pooled specification that receives SA2-STANDS may NOT yet claim:**

- Any welfare decomposition result (welfare computation is separately
  gated).
- Canonical promotion of the pooled specification (separately gated).
- Displacement of M1-clean as the JMP baseline until the SA2 verdict
  is issued and accepted.
- That pooled estimation reveals the causal structure of regional
  labour-market inequality (causal identification requires the full
  ability-versus-opportunity decomposition, which requires welfare
  computation).

---

## 23. What remains blocked

The following are explicitly **NOT authorized** by this design memo,
by the construction verdict, or by any prior document in the evidence
chain:

**Pooled estimation execution.** This memo defines the specification;
execution requires a separate authorization memo.

**Welfare computation.** Welfare scaffolding design is complete per
`docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md`. Welfare computation
requires an accepted SA2 verdict on a pooled specification and a
separate welfare-computation authorization.

**Welfare implementation.** No welfare-related script or computation
is to be written or run.

**Canonical MNL promotion.** The versioned GSURv2 MNL parquets remain
the operative data source. Promotion (the O10 decision) is separately
gated.

**M1-clean displacement.** `ruro_occ_M1_clean` remains the active JMP
baseline. Displacement requires an explicit SA2 verdict.

**P3b or P4 configurations.** P3b (FR_2015+FR_2016+FR_2018) is
hard-blocked pending the ISF comparability gate; P4 is not a priority.
Neither is authorised.

**Year-interacted or other alternative pooled specifications.** This
memo defines one baseline pooled specification (M1-clean + 2 year
dummies). Alternative pooled specifications (year-interacted GSUR,
year-interacted preferences, etc.) are post-SA2 sensitivity exercises
requiring their own design decisions.

---

## 24. Exact Claude Code implementation-audit prompt

The following is the exact prompt to be provided to Claude Code Sonnet
for the Gate-A implementation audit of the pooled YAML. It must be
used verbatim, without abbreviation or paraphrase, to initiate the
pooled YAML implementation and Gate-A parse audit. It should be issued
only after this design memo has been reviewed and accepted, and before
the pooled-estimation authorization memo is drafted.

---

> Work locally in my RURO/MNL codebase.
>
> This is a Gate-A YAML implementation and static parse audit for the
> pooled P3a estimation specification. Do not run estimation. Do not
> modify the pooled parquet. Do not modify M1-clean or M1-naive specs.
>
> Read:
> - `docs/France_case/P3a/design/JMP_pooled_P3a_estimation_design_memo_v1.md` (this memo —
>   the authoritative spec for the pooled YAML)
> - `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
>   (the source YAML to derive from)
> - `scripts/enhanced/estimation_spec_parser.py`
>   (the parser to use for Gate-A static checks)
> - `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
>   (the pooled data input — read column names only, do not load full
>   data)
>
> Task:
>
> 1. Create
>    `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
>    by deriving from the M1-clean YAML with exactly these changes and
>    no others:
>    - `specification.name`: set to `ruro_occ_P3a_pooled`
>    - `specification.description`: update to describe the pooled
>      three-year P3a specification
>    - `market_opportunity.shifters`: add two new entries after the
>      last existing shifter entry:
>      `beta_E_y2015` (variable: `year_2015_indicator`,
>      applies_to: `household`) and
>      `beta_E_y2017` (variable: `year_2017_indicator`,
>      applies_to: `household`)
>    - `initial_values`: add `beta_E_y2015: 0.0` and
>      `beta_E_y2017: 0.0`
>    - `optimization.bounds`: add entries for `beta_E_y2015` and
>      `beta_E_y2017` with bounds `[-5.0, 5.0]`
>    - Do not change any other field. All other blocks must be
>      byte-identical to the M1-clean YAML.
>
> 2. Run `estimation_spec_parser.py` on the new YAML and confirm it
>    parses without error.
>
> 3. Run Gate-A checks GA1–GA17 as specified in
>    `docs/France_case/P3a/design/JMP_pooled_P3a_estimation_design_memo_v1.md` §19.
>    For GA13 (precompute smoke test): confirm that `year_tag == 1`
>    and `year_tag == 3` resolve to non-empty subsets on the pooled
>    parquet, and confirm that `year_2015_indicator` and
>    `year_2017_indicator` can be constructed as `(year_tag == 1)`
>    and `(year_tag == 3)` respectively.
>    For GA14: confirm `gsur` non-null for singles rows, `gsur_female`
>    and `gsur_male` non-null for couples rows.
>    For GA15: confirm `ils_dispy_real` present and non-null; confirm
>    `ils_dispy_real != ils_dispy` for at least one non-FR_2016 row.
>    For GA16: confirm `cluster_id == idorighh` for all rows (sample
>    check, not full scan).
>    For GA17: note whether the estimation engine exposes a
>    `cluster_id` parameter or cluster-robust SE method; record the
>    finding even if the method is not yet implemented.
>
> 4. Create `Results/P3a/pooled_P3a/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md`
>    with exactly these headings:
>    1. Gate-A verdict
>    2. YAML derivation record
>    3. Parser output
>    4. GA1–GA17 check results
>    5. Precompute smoke test
>    6. Cluster-robust SE infrastructure status
>    7. What was not run
>    8. Immediate next step
>
> Required final statements in the report:
> - State whether all GA1–GA17 checks passed.
> - State whether cluster-robust SE infrastructure is confirmed or
>   pending.
> - State that pooled estimation execution is NOT authorized by this
>   Gate-A audit.
> - State that pooled estimation execution requires a separate
>   pooled-estimation authorization memo.
> - State that M1-clean 2016 remains the active JMP baseline.
> - State that pooled estimation is NOT authorized.
> - State that welfare computation is NOT authorized.

---

**Pooled estimation is NOT authorized.**

**Welfare computation is NOT authorized.**

**M1-clean 2016 remains the active JMP baseline.** Displaced only by
a future SA2 verdict explicitly promoting a final pooled specification.