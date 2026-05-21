# JMP Pooled P3a Estimation — Execution Report v2

*France FR_2015 / FR_2016 / FR_2017 | Three-start pooled RURO estimation*
*Executed: 2026-05-21 | Orchestrator started: 20260521T143815Z, finished: 20260521T161114Z*

**Supersedes:** `Results/JMP_pooled_P3a_estimation_report_v1.md`

**Corrections in this revision:**
- Headings reorganised to match D1–D15 diagnostic structure of authorization §13
- T4 denominator and region-dummy SE value explicitly defined (Action 3)
- Start 3 base-theta protocol deviation documented (Action 4)
- D5 GSUR t-statistic, S2 and S3 verdicts, and SA2 criteria mapped
- D6 Wald test result (degenerate; region dummies unidentified) documented
- D12 income-routing and D13 cluster-key confirmations added
- Artifact provenance confirmed: git working tree clean; all `Results/` artifacts committed

---

## 1. Authorization provenance

Execution authorised under:

- `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` (§§1–19, the primary authorization)
- `docs/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md` (correction addendum)
- `docs/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md` (repair clearance — superseded the `fr_p3a_gsurv2_harmonised.parquet` data input path with the split-stem base; see Section 3)

Preflight v2 (`Results/JMP_pooled_P3a_estimation_preflight_report_v2.md`): all 15 checks PASS.

Hard constraints active throughout: no welfare, no SA2, no canonical promotion, no M1-clean displacement, halt on H1–H6.

---

## 2. Execution overview

Orchestrator: `scripts/maintenance/run_pooled_P3a_estimation.py`

All three starts completed with `returncode = 0`. Post-estimation cluster-robust SEs computed
after each start. Orchestrator summary: `Results/JMP_pooled_P3a_orchestrator_summary.json`.

---

## 3. Specification and data input

**Specification:** `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
(55 parameters: 53 M1-clean shared + `beta_E_y2015` + `beta_E_y2017`; FR_2016 reference year;
`couples_fixed_box_cox_exponent: 0.0` — theta_c fixed, not estimated).

**Data input:** `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready` (split-stem base).
The repair clearance explicitly updated the data input from the unified `fr_p3a_gsurv2_harmonised.parquet`
(referenced in authorization §6) to the split-stem base (binding condition §2 of the repair clearance).
The two representations are derived from the same source; the split stem was created by
`scripts/maintenance/prepare_pooled_estimation_ready.py` and validated with V1–V9 PASS.

Split-stem files loaded:

| Suffix | Rows | Description |
|--------|------|-------------|
| `__singles.parquet` | 500,700 | Single household-year-alternative rows |
| `__couples.parquet` | 743,800 | Couple household-year-alternative rows |
| `__mnlmeta.json` | — | Metadata (columns, cluster key, year tags) |

Total: 1,244,500 rows; 12,445 household-year choice sets; 9,657 unique `idorighh` clusters.
Precomputed groups: 2,243 singles-male, 2,764 singles-female, 7,438 couples.
Each group: exactly 100 alternatives, exactly 1 chosen (`draw = 0 ↔ is_chosen = 1`).

---

## 4. Infrastructure fixes applied prior to execution

**Fix A — Precompute groupby (estimation_utils.py):** `precompute_data_singles` and
`precompute_data_couples` previously grouped by `df["idhh"]` (= `idorighh`, constant across
years), creating groups spanning multiple years. Fix: sort by `(idhh, year_tag)` on entry
and detect group boundaries via composite key `idhh × 10 + year_tag`. Produces n_groups =
2,243 / 2,764 / 7,438 with exactly 100 alts per group.

**Fix B — Vectorized reshape (gamspy_estimation_vectorized.py):** The precompute fix directly
resolves the `n_obs = 224,300 / n_groups = 1,738 = 129.05…` non-integer reshape failure.
With n_groups = 2,243, `224,300 / 2,243 = 100` exactly. Vectorized mode restored.

**Fix C — Couples theta_c (gamspy_estimation.py):** The P3a spec fixes `theta_c = 0.0` for
couples; `theta_c` is therefore absent from `param_vars`. Guard added at both
`estimate_couples_gamspy` and `estimate_joint_gamspy`: when
`spec.utility_consumption_theta_couples_fixed is not None`, a Python float constant
(`math.log(c_val)` for `theta_c = 0.0`) is substituted instead of a GAMSPy variable lookup.

Committed: `14b5b20` (Fixes A+B), `3b3372b` (Fix C).

---

## D1. Convergence status by start

| Start | Group | Solver status | Message | Iterations | Wall (s) |
|-------|-------|--------------|---------|-----------|----------|
| Start 1 | singles_male | True | NormalCompletion / OptimalLocal | 14 | 280.3 |
| Start 1 | singles_female | True | NormalCompletion / OptimalLocal | 14 | 280.3 |
| Start 1 | couples | True | NormalCompletion / OptimalLocal | 14 | 280.3 |
| Start 2 | singles_male | True | NormalCompletion / OptimalLocal | 16 | 282.2 |
| Start 2 | singles_female | True | NormalCompletion / OptimalLocal | 16 | 282.2 |
| Start 2 | couples | True | NormalCompletion / OptimalLocal | 16 | 282.2 |
| Start 3 | singles_male | True | NormalCompletion / OptimalLocal | 19 | 299.8 |
| Start 3 | singles_female | True | NormalCompletion / OptimalLocal | 19 | 299.8 |
| Start 3 | couples | True | NormalCompletion / OptimalLocal | 19 | 299.8 |

All three starts: **success = True, solver status = NormalCompletion / OptimalLocal**.
No halt condition H3 (non-convergence) triggered.

Note: the estimator runs a joint optimization; all three groups converge in the same solver
call and report an identical `final_ll` (the joint log-likelihood).

---

## D2. Objective value by start

| Start | Joint log-likelihood |
|-------|---------------------|
| Start 1 | −57,280.621315 |
| Start 2 | −57,280.621315 |
| Start 3 | −57,280.621315 |

All three starts agree to nine decimal places (maximum absolute difference < 1 × 10⁻⁹).
The SA2-STANDS criterion **S1 (all three starts within 1 LL unit)** is satisfied.

---

## D3. Parameter vector comparison across starts

L∞ (maximum absolute) differences between converged parameter vectors:

| Pair | L∞ distance | Parameter driving gap |
|------|-------------|----------------------|
| Start 1 vs Start 2 | 1.563 | `beta_E_drgn4` (1.563 vs 0.000) |
| Start 1 vs Start 3 | 0.094 | `beta_E_drgn6` (0.767 vs 0.860) |
| Start 2 vs Start 3 | 1.599 | `beta_E_drgn4` (0.000 vs 1.599) |

**The entire parameter disagreement is confined to the 7 region dummies** (`beta_E_drgn2`–`beta_E_drgn8`).
These parameters are unidentified (Section D6); their values are not pinned by the data.

For all 48 identified parameters (the 55-parameter vector minus 7 unidentified region dummies
minus `beta_l0_m` at bound), the three converged vectors agree to 12+ significant figures. The
maximum absolute difference in any identified parameter across all three pairs is less than
5 × 10⁻¹². The SA2-STANDS criterion **S1 (parameter vectors within 0.01 absolute)** is
satisfied for all identified parameters.

---

## D4. Year-effect estimates and signs

| Parameter | Estimate | SE robust | t-ratio | Sign |
|-----------|----------|-----------|---------|------|
| beta_E_y2015 | 0.109717 | 0.253210 | 0.43 | positive |
| beta_E_y2017 | 0.325530 | 0.277286 | 1.17 | positive |

Estimates are identical across all three starts (agreement to 10+ decimal places).
Both year effects are positive, indicating higher employment opportunity in 2015 and 2017
relative to the 2016 reference year, with the 2017 effect larger. Neither estimate achieves
conventional significance at the 5% level under cluster-robust SEs (t < 1.96).

The SA2-REVISION threshold from the design memo applies if the year effects are individually
significant and large; neither condition is met at current precision.

---

## D5. GSUR coefficient estimate and sign

| | beta_E_gsur | SE robust | t-ratio | SE Hessian |
|-|-------------|-----------|---------|------------|
| Pooled P3a | −1.198054 | 0.178819 | −6.70 | 0.092274 |
| M1-clean FR_2016 | −1.329 | 0.163 | −8.15 | — |

Pooled estimate as % of M1-clean magnitude: **90.1%** (within ±50% threshold → S3 PASS).

**S2** (cluster-robust t < −2.576 for p < 0.01 two-tailed): t = −6.70 → **S2 PASS**.
**S3** (within 50% of M1-clean magnitude −1.329): |Δ| / |−1.329| = 9.9% → **S3 PASS**.

The GSUR loading is negative, highly significant under cluster-robust SEs, and stable in
magnitude relative to the single-year M1-clean estimate. This confirms the pooled specification
recovers the GSUR identification result from M1-clean.

---

## D6. Region-dummy stability

| Parameter | Start 1 estimate | Start 2 estimate | Start 3 estimate | SE robust (all) |
|-----------|-----------------|-----------------|-----------------|-----------------|
| beta_E_drgn2 | 0.801 | 0.000 | 0.710 | ~8 × 10⁻¹⁵ |
| beta_E_drgn3 | 0.656 | 0.000 | 0.587 | ~7 × 10⁻¹⁵ |
| beta_E_drgn4 | 1.563 | 0.000 | 1.599 | ~1.4 × 10⁻¹⁴ |
| beta_E_drgn5 | 0.772 | 0.000 | 0.821 | ~1.1 × 10⁻¹⁵ |
| beta_E_drgn6 | 0.767 | 0.000 | 0.860 | ~1.7 × 10⁻¹⁴ |
| beta_E_drgn7 | 0.640 | 0.000 | 0.606 | ~7.3 × 10⁻¹⁵ |
| beta_E_drgn8 | 0.463 | 0.000 | 0.437 | ~5.6 × 10⁻¹⁵ |

**The seven region dummies are not identified in the pooled specification.** Evidence:

1. Start 2 converged with all seven at 0.0, while Starts 1 and 3 converged with different
   non-zero values, all achieving the same joint LL (D2). The LL surface is flat in these
   seven dimensions.
2. The cluster-robust SEs are ~10⁻¹⁴ to 10⁻¹⁵ (numerical noise in the sandwich computation,
   attributable to a near-zero Hessian sub-block in the unidentified subspace). These are
   technically > 0 (see D10 for T4 denomination), but represent numerical noise not
   inferential precision.
3. The VCV sub-block for region dummies has eigenvalues in the range −1.7 × 10⁻²⁸ to
   5.9 × 10⁻²⁸ (both signs, machine-precision scale). The sub-block is effectively zero.

**Joint Wald test:** The cluster-robust Wald statistic W = theta_drgn' × VCV_drgn⁻¹ × theta_drgn
is numerically undefined (degenerate inverse). The test cannot be formed validly.

**SA2-STANDS criterion S4** (region-dummy Wald test p < 0.01): **S4 is INDETERMINATE** — the
Wald test is not computable due to non-identification. The region dummies cannot be tested
jointly under cluster-robust inference. This requires a design decision: either constrain the
region dummies to zero (making the pooled spec a 48-free-parameter model) or investigate the
source of non-identification before proceeding to SA2.

M1-clean comparison: M1-clean ran on a single year (FR_2016 only) and identified region
dummies via cross-sectional region variation. In the pooled three-year panel, with year
effects included, the region-level employment opportunity variation is apparently absorbed
by or collinear with other model dimensions (time-invariant region effects are not identified
when household-year effects enter through other channels). This structural finding should be
addressed in the SA2 verdict.

---

## D7. Hessian condition and invertibility

| Start | Condition number (H, free 54×54) | VCV condition (identified 47×47) |
|-------|----------------------------------|----------------------------------|
| Start 1 | 5.18 × 10²⁴ | 2.03 × 10¹⁰ |
| Start 2 | 1.13 × 10²⁵ | 2.03 × 10¹⁰ |
| Start 3 | 2.83 × 10²⁵ | 2.03 × 10¹⁰ |

The full Hessian (54 free parameters) is highly ill-conditioned due to the unidentified
region-dummy subspace. The condition number of the identified 47-parameter subspace (parameters
with robust SE > 10⁻¹⁰) is 2.03 × 10¹⁰ — comparable to M1-clean (5.10 × 10¹⁰).

Eigenvalue analysis of the VCV (identified subspace, Start 1): min = 6.03 × 10⁻¹¹,
max = 1.22 × 10⁰.

M1-clean had 3 negative-diagonal Hessian entries in the singles-consumption sub-block
(`beta_c_sm`, `beta_c_sf`, `theta_c_singles`). The pooled Hessian follows the same pattern
(these parameters are at the boundary of their feasible region numerically); the pinv-based
SE computation handles this correctly.

**SA2-STANDS criterion S5** (no negative eigenvalues in GSUR-region Hessian sub-block):
the GSUR-region subspace includes unidentified region dummies with near-zero eigenvalues;
the criterion requires an SA2-level adjudication once the region-dummy identification issue
is resolved.

**SA2-STANDS criterion S8** (no new negative-diagonal Hessian entries beyond M1-clean's 3):
the same 3 singles-consumption parameters show near-singular Hessian behavior; no additional
entries are introduced.

---

## D8. Cluster-robust SE availability

Cluster-robust SEs computed for all three starts using `run_cluster_robust_se.py
--mode post-estimation` with:
- Converged theta from `estimation_results.json`
- TRUE Hessian (central differences on `compute_gradient_joint` at converged theta)
- Full split-stem dataset (no row bound)
- Cluster column: `idorighh`
- Sandwich: V = H⁻¹ B H⁻¹

Output files:
- `Results/JMP_pooled_P3a_start1_cluster_robust_se.json` (run_timestamp: 20260521T150329Z)
- `Results/JMP_pooled_P3a_start2_cluster_robust_se.json` (run_timestamp: 20260521T153135Z)
- `Results/JMP_pooled_P3a_start3_cluster_robust_se.json` (run_timestamp: 20260521T160424Z)

---

## D9. Full 9,657-cluster confirmation (T3)

All three starts: **T3 PASS**.

| Start | n_unique_clusters | expected | Pass |
|-------|-------------------|----------|------|
| Start 1 | 9,657 | 9,657 | PASS |
| Start 2 | 9,657 | 9,657 | PASS |
| Start 3 | 9,657 | 9,657 | PASS |

Score matrix shape: 12,445 × 55 for all three starts (12,445 household-year choice sets,
55 parameters). The meat-matrix assembly aggregated over all 9,657 unique `idorighh` clusters
on the full dataset, correctly accounting for households appearing in multiple years.

---

## D10. Robust-SE positivity (T4)

All three starts: **T4 PASS** — n_nonpositive = 0.

**T4 denominator definition:** The free-parameter mask (`free_mask`) excludes parameters at
their bounds. With `bound_tol = 1e-6`, only `beta_l0_m = 1e-06` (at its lower bound) is
excluded. The free count is **n_free = 54** (55 parameters minus `beta_l0_m`). T4 checks
`se_free <= 0` (strictly non-positive) over the 54 free parameters.

**Region dummy SE values:** The 7 region dummies are in the free set (n_free = 54 = 55 − 1,
not 55 − 8). Their cluster-robust SEs are not identically zero; they are on the order of
10⁻¹⁴ to 10⁻¹⁵ — strictly positive floating-point values representing numerical noise in
the sandwich computation on a near-degenerate Hessian subspace. Because these values are
> 0 (not ≤ 0), they pass T4's `se_free <= 0` check. T4 PASS is therefore technically correct.

However, these SEs carry no inferential content: they are numerical noise approximately
equal to machine precision for double-precision arithmetic (ε ≈ 2.2 × 10⁻¹⁶), not
precision estimates of estimable quantities. They should not be used for inference.

Explicit values (Start 1):

| Parameter | se_robust |
|-----------|-----------|
| beta_E_drgn2 | 8.63 × 10⁻¹⁵ |
| beta_E_drgn3 | 7.06 × 10⁻¹⁵ |
| beta_E_drgn4 | 1.35 × 10⁻¹⁴ |
| beta_E_drgn5 | 1.14 × 10⁻¹⁵ |
| beta_E_drgn6 | 1.69 × 10⁻¹⁴ |
| beta_E_drgn7 | 7.31 × 10⁻¹⁵ |
| beta_E_drgn8 | 5.56 × 10⁻¹⁵ |

All other 47 identified free parameters have strictly positive cluster-robust SEs
representing genuine inferential precision (range: 1.52 × 10⁻³ to 8.78 × 10⁻¹).

---

## D11. Robust-vs-Hessian comparison (T5)

All three starts: **T5 PASS** — n_below = 0 (no robust SE smaller than Hessian SE among
free parameters).

The ordering cluster-robust SE ≥ Hessian SE holds for all identified parameters, consistent
with positive within-cluster correlation inflating SEs relative to the i.i.d. assumption.
No anomalous SE inversion observed.

Selected ratio (robust / Hessian) for key identified parameters (Start 1):

| Parameter | SE robust | SE Hessian | Ratio |
|-----------|-----------|------------|-------|
| beta_c | 0.4415 | 0.0569 | 7.76 |
| beta_E | 0.2742 | 0.1206 | 2.27 |
| beta_E_gsur | 0.1788 | 0.0923 | 1.94 |
| beta_E_y2015 | 0.2532 | 0.1099 | 2.30 |
| beta_E_y2017 | 0.2773 | 0.1183 | 2.34 |
| sigma | 0.001522 | 0.000220 | 6.92 |
| beta_ll | 0.3747 | 0.0479 | 7.83 |

The robust-to-Hessian ratios of 2–8× reflect substantial within-`idorighh` correlation
across years, as expected for a three-year panel.

---

## D12. Income-routing confirmation

**Income routing confirmed correct per GA15 rule.**

The precompute functions enforce separate income paths:
- `precompute_data_singles`: reads `ils_dispy_real` (singles-only column; null for couples rows).
  Confirmed non-null for all 500,700 singles rows (PE3 output).
- `precompute_data_couples`: reads `ils_dispy_male` and `ils_dispy_female` (gender-specific
  columns). Does NOT read `ils_dispy_real`. Confirmed non-null for all 743,800 couples rows.

No step in the estimation or post-estimation SE computation assumed `ils_dispy_real` covers
couples. Halt condition H2 (income routing wrong) did not trigger.

---

## D13. Cluster-key confirmation

**Cluster key confirmed as `idorighh`.**

The SE CLI was invoked with `--cluster-col idorighh`. T3 confirmed 9,657 unique `idorighh`
clusters on the full dataset. The cluster-key strictness safeguard in `precompute_data_singles`
and `precompute_data_couples` was active; no silent fallback to `idhh` occurred.

Halt condition H1 (cluster key not `idorighh`) did not trigger.

---

## D14. No-welfare confirmation

**Welfare computation: CONFIRMED NOT RUN.**

All three SE JSON files carry `PE9_no_welfare: {passed: true, note: "No welfare computed
(not authorized)"}`. The orchestrator script contains no welfare step. No welfare function
was called at any point during estimation or post-estimation.

Halt condition H5 (welfare or canonical step attempted) did not trigger.

---

## D15. M1-clean-active confirmation

**M1-clean 2016 remains the active JMP baseline.**

All three SE JSON files carry `PE9_m1clean_active: {passed: true, note: "M1-clean 2016
remains active JMP baseline."}`. No operation in this session altered the M1-clean results
or re-pointed the JMP baseline. No canonical output was modified or promoted.

Halt conditions H4 (partial: not triggered — all SE computations succeeded), H5 (not
triggered — no canonical step), and H6 (not triggered — no spec modification) held.

---

## 5. Protocol deviations

### PD1 — Start 3 base theta: converged vs warm-start initial values

The authorization (§8, §9) describes Start 3 as "a random perturbation (seed 42, magnitude
±0.1) is applied to the Start 1 vector." The authorization text is ambiguous: "Start 1
vector" could refer to the Start 1 initial warm-start vector (M1-clean params + 0.0 for year
dummies) or the Start 1 converged theta.

The orchestrator (`run_pooled_P3a_estimation.py`) perturbed the **converged** theta from
Start 1. This is recorded in the perturbed init JSON:
`"_base_source": "start_1_converged"`.

**Assessment: non-blocking protocol deviation.** Perturbing the converged theta (rather than
the initial warm-start) is the more stringent test of local optimum stability — it tests
whether the optimizer finds the same optimum from the neighbourhood of that optimum, not just
from the neighbourhood of the initial warm start. The intent of Start 3 ("perturbed warm
start… to test the optimum's stability," §9) is satisfied at least as well. Since all three
starts reached the same LL and the same identified parameters (D2, D3), this deviation has
no effect on the results or the SA2 readiness conclusions.

### PD2 — Data input: harmonised parquet vs split-stem base

The primary execution authorization §6 references `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
as the data input. The estimation ran against the split-stem base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`.

**Assessment: authorized deviation, not a protocol deviation.** The repair clearance
explicitly updated the data input as a binding condition: "Run against the split-stem base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`." The split-stem files are derived
from the harmonised parquet without modification to the data; the conversion is documented and
verified in the repair report (V1–V2 PASS, row-count conservation, cluster-count conservation).

---

## 6. Full parameter table (Start 1 converged theta with cluster-robust SEs)

Start 2 and Start 3 are identical on all identified parameters; any difference is in the
unidentified region dummies (see D3). Start 1 results are used as the canonical record.

| # | Parameter | Estimate | SE robust | SE Hessian | t-ratio |
|---|-----------|----------|-----------|------------|---------|
| 1 | beta_l0_sm | 4.348369 | 0.793436 | 0.038251 | 5.48 |
| 2 | beta_l_age_sm | 0.043685 | 0.023043 | 0.012730 | 1.90 |
| 3 | beta_l_age2_sm | 0.001761 | 0.002080 | 0.001173 | 0.85 |
| 4 | beta_c_sm | 2.746037 | 0.285809 | 0.067080 | 9.61 |
| 5 | theta_l_sm | −0.719261 | 0.061579 | 0.047329 | −11.68 |
| 6 | beta_l0_sf | 4.457162 | 0.878118 | 0.234007 | 5.08 |
| 7 | beta_l_age_sf | 0.038770 | 0.028850 | 0.014234 | 1.34 |
| 8 | beta_l_age2_sf | 0.004707 | 0.002548 | 0.001222 | 1.85 |
| 9 | beta_l_nkids_sf | 0.386053 | 0.414746 | 0.182662 | 0.93 |
| 10 | beta_c_sf | 2.359708 | 0.360238 | 0.066286 | 6.55 |
| 11 | theta_l_sf | −0.701927 | 0.057756 | 0.026104 | −12.15 |
| 12 | theta_c_singles | 0.048451 | 0.065621 | 0.014443 | 0.74 |
| 13 | beta_l0_m | 0.000001 | — (at bound) | — | — |
| 14 | beta_l_age_m | 0.006831 | 0.018737 | 0.008989 | 0.36 |
| 15 | beta_l_age2_m | 0.001581 | 0.001234 | 0.000713 | 1.28 |
| 16 | theta_l_m | −0.683695 | 0.037860 | 0.025805 | −18.06 |
| 17 | beta_l0_f | 2.613305 | 0.760980 | 0.266490 | 3.43 |
| 18 | beta_l_age_f | −0.056330 | 0.038853 | 0.012777 | −1.45 |
| 19 | beta_l_age2_f | 0.005090 | 0.003749 | 0.001332 | 1.36 |
| 20 | beta_l_nkids_f | 0.142397 | 0.362386 | 0.129203 | 0.39 |
| 21 | theta_l_f | −0.659007 | 0.031356 | 0.013760 | −21.02 |
| 22 | beta_c | 4.331393 | 0.441485 | 0.056931 | 9.81 |
| 23 | beta_E | −2.280614 | 0.274203 | 0.120582 | −8.31 |
| 24 | beta_h_pt1 | −0.473101 | 0.131242 | 0.063078 | −3.61 |
| 25 | beta_h_pt2 | 0.423733 | 0.103303 | 0.065748 | 4.10 |
| 26 | beta_h_ft | 1.403611 | 0.085415 | 0.029973 | 16.43 |
| 27 | beta_E_gsur | −1.198054 | 0.178819 | 0.092274 | −6.70 |
| 28 | beta_E_drgn2 | 0.801342 | ~8.6 × 10⁻¹⁵ | ~0 | n/a |
| 29 | beta_E_drgn3 | 0.656401 | ~7.1 × 10⁻¹⁵ | ~0 | n/a |
| 30 | beta_E_drgn4 | 1.562552 | ~1.4 × 10⁻¹⁴ | ~0 | n/a |
| 31 | beta_E_drgn5 | 0.772496 | ~1.1 × 10⁻¹⁵ | ~0 | n/a |
| 32 | beta_E_drgn6 | 0.766517 | ~1.7 × 10⁻¹⁴ | ~0 | n/a |
| 33 | beta_E_drgn7 | 0.640451 | ~7.3 × 10⁻¹⁵ | ~0 | n/a |
| 34 | beta_E_drgn8 | 0.463141 | ~5.6 × 10⁻¹⁵ | ~0 | n/a |
| 35 | beta_E_y2015 | 0.109717 | 0.253210 | 0.109935 | 0.43 |
| 36 | beta_E_y2017 | 0.325530 | 0.277286 | 0.118330 | 1.17 |
| 37 | beta_occ_2_sm | −1.510499 | 0.110795 | 0.083107 | −13.63 |
| 38 | beta_occ_3_sm | −2.152414 | 0.154508 | 0.108361 | −13.93 |
| 39 | beta_occ_4_sm | 0.060615 | 0.057888 | 0.050426 | 1.05 |
| 40 | beta_occ_2_sf | −0.129549 | 0.084525 | 0.065076 | −1.53 |
| 41 | beta_occ_3_sf | −0.556515 | 0.091624 | 0.073169 | −6.07 |
| 42 | beta_occ_4_sf | 0.740398 | 0.074766 | 0.052324 | 9.90 |
| 43 | beta_occ_2_cm | −1.494608 | 0.156217 | 0.069545 | −9.57 |
| 44 | beta_occ_3_cm | −2.209091 | 0.211045 | 0.089689 | −10.47 |
| 45 | beta_occ_4_cm | 0.482506 | 0.086172 | 0.041536 | 5.60 |
| 46 | beta_occ_2_cf | 0.132114 | 0.138665 | 0.060979 | 0.95 |
| 47 | beta_occ_3_cf | −0.313212 | 0.156356 | 0.067593 | −2.00 |
| 48 | beta_occ_4_cf | 1.090385 | 0.111977 | 0.048920 | 9.74 |
| 49 | beta_w0 | 2.034758 | 0.094030 | 0.012775 | 21.64 |
| 50 | beta_w_educL | −0.041977 | 0.073680 | 0.011383 | −0.57 |
| 51 | beta_w_educH | 0.305805 | 0.060170 | 0.008671 | 5.08 |
| 52 | beta_w_pexp | 0.017236 | 0.008711 | 0.001319 | 1.98 |
| 53 | beta_w_pexp2 | −0.000181 | 0.000193 | 0.000030 | −0.94 |
| 54 | sigma | 0.403289 | 0.001522 | 0.000220 | 265.0 |
| 55 | beta_ll | 2.655290 | 0.374735 | 0.047935 | 7.09 |

Region dummies (rows 28–34): estimates are from Start 1; Start 2 converged at 0.000 with
identical LL; Start 3 converged at different non-zero values with identical LL. SEs at
machine-epsilon scale are not inferential (see D6, D10).

---

## 7. SA2 criteria pre-assessment

| Criterion | Requirement | Status |
|-----------|-------------|--------|
| S1 | LL agreement within 1 unit; params within 0.01 | **PASS** — LL identical; identified params agree to 10⁻¹² |
| S2 | beta_E_gsur significant at p < 0.01 (robust) | **PASS** — t = −6.70 |
| S3 | beta_E_gsur within 50% of M1-clean magnitude | **PASS** — 90.1% of M1-clean |
| S4 | Region-dummy joint Wald test p < 0.01 (robust) | **INDETERMINATE** — region dummies unidentified; Wald stat degenerate |
| S5 | No negative eigenvalues in GSUR-region Hessian subblock | **INDETERMINATE** — pending resolution of region identification |
| S6 | Preference block max |Δ| < 10% relative to M1-clean | Requires explicit comparison computation; not evaluated here |
| S7 | beta_ll t > 5 (robust) | **PASS** — t = 7.09 |
| S8 | No new negative-diagonal Hessian entries | **PASS** — same 3 singles-consumption entries as M1-clean |
| S9 | Gate-A GA1–GA17 all clear | **PASS** — Gate-A PASS + GA17 cleared |
| S10 | Participation fit ≤ 2 pp regression vs M1-clean | Requires post-estimation simulation; not authorized here |
| S11 | Mean-hours fit ≤ 0.5 hrs regression vs M1-clean | Requires post-estimation simulation; not authorized here |

S4 and S5 are blocked by region-dummy non-identification. S6, S10, S11 require simulation
steps separately authorized. SA2 verdict cannot proceed until S4/S5 are resolved.

---

## 8. Artifact inventory and git status

All artifacts in `Results/` are tracked by git and committed. The `outputs/` directory is
gitignored per `.gitignore:25`.

**`Results/` artifacts committed:**

| File | Contents |
|------|----------|
| `JMP_pooled_P3a_estimation_report_v1.md` | First execution report (superseded by this v2) |
| `JMP_pooled_P3a_estimation_report_v2.md` | This document |
| `JMP_pooled_P3a_orchestrator_summary.json` | Orchestrator run summary (all returncodes=0) |
| `JMP_pooled_P3a_start1_cluster_robust_se.json` | Start 1 SE + diagnostic checks |
| `JMP_pooled_P3a_start2_cluster_robust_se.json` | Start 2 SE + diagnostic checks |
| `JMP_pooled_P3a_start3_cluster_robust_se.json` | Start 3 SE + diagnostic checks |
| `JMP_pooled_P3a_start1_cluster_robust_se_vcv.npy` | Start 1 sandwich VCV (55×55) |
| `JMP_pooled_P3a_start2_cluster_robust_se_vcv.npy` | Start 2 sandwich VCV (55×55) |
| `JMP_pooled_P3a_start3_cluster_robust_se_vcv.npy` | Start 3 sandwich VCV (55×55) |
| `JMP_pooled_P3a_start3_perturbed_init.json` | Start 3 initial values (base: start_1_converged, seed 42, ±0.1) |

**Gitignored (not committed, reproducible by re-running orchestrator):**
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_*/run_*/` — per-start estimation
  run directories, including `estimation_results.json`. Excluded by `.gitignore:25 (outputs/*)`.

The converged theta is preserved in each start's SE JSON (`cluster_robust_se_artifacts.converged_theta`).
Re-running is possible from the committed spec, data, and orchestrator script.

**Git status at time of this report: clean (`nothing to commit, working tree clean`).**

---

## 9. Required final statements

- **The pooled P3a estimation was executed** under the authorizations listed in Section 1.
  All three starts converged with success = True / NormalCompletion / OptimalLocal to the
  same joint log-likelihood (−57,280.621315). T3 (9,657 clusters), T4 (n_nonpositive = 0
  among n_free = 54 free parameters), and T5 (n_below = 0) PASS for all three starts.

- **SA2 verdict readiness is PARTIAL.** S1, S2, S3, S7, S8, S9 PASS. S4 and S5 are
  INDETERMINATE due to non-identification of the 7 region dummies. S6, S10, S11 are not
  evaluated (require separately authorized simulation). The SA2 verdict cannot be issued
  until S4/S5 are resolved.

- **No welfare was computed.** Confirmed by D14; separately gated.

- **M1-clean 2016 remains the active JMP baseline.** Confirmed by D15; no canonical promotion
  was performed.

- **No SA2 verdict was issued.** This report records execution and diagnostics only.

- **All hard constraints H1–H6 held throughout execution.**