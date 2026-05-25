# RURO post-estimation M1 diagnostics — implementation report v1

Date: 2026-05-18  
Author: research pipeline  
Status: **research-only** — not package-core; see §5 for package classification

---

## 1. Purpose

This document records how `scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`
was written, what it computes, the inputs it consumed, the outputs it produced,
and its classification against the package portability standard.

The script provides three diagnostics that are specific to the M1-clean
specification's region-dummy block and cannot be derived from the standard
post-estimation output alone:

| Diagnostic | What it answers |
|---|---|
| D1 — Joint Wald test | Are β_E_drgn2 … β_E_drgn8 jointly non-zero? |
| D2 — 7×7 region VCV | Are the region dummies collinear with one another? |
| D3 — 8×8 GSUR+region Hessian eigenvalues | Is the GSUR+region sub-block locally convex? |

These diagnostics address a question the standard post-estimation cannot: whether
the seven region dummies introduced in M1-clean are *jointly* identified and
contribute genuine variation to the employment-opportunity index, or are
individually noisy while collectively redundant.

---

## 2. Inputs

| Input | Path | Notes |
|---|---|---|
| Parameter estimates | `outputs/post_estimation/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-56-41/params.csv` | From selected M1-clean run; contains estimate, SE, t-stat, p-value per parameter |
| Estimation results JSON | `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json` | Selected run folder; used for provenance metadata only |
| MNL base | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2` | GSURv2 parquets and sidecar JSON; same base used in estimation and post-estimation |
| Spec YAML | `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml` | Parsed to obtain parameter list, bounds, and precompute variable requirements |

The full 53×53 Hessian is **not** stored in `estimation_results.json` — it is
excluded at save time because of size (line 557 of `enh_RURO_estimate_FR.py`:
`# Don't save varcov and hessian matrices (too large for JSON)`). The script
therefore recomputes it via central-difference finite differences on the joint
gradient function.

---

## 3. Method

### 3.1 Hessian recomputation

The joint negative log-likelihood gradient `compute_gradient_joint` from
`estimation_engine.py` is used. Central differences with step `eps = 1e-5`:

```
H[i, j] = (g(θ + ε·eᵢ)[free_idx] − g(θ − ε·eᵢ)[free_idx]) / (2ε)
```

Only the free parameters (those not at bounds) enter the Hessian; the full
53-parameter vector has two fixed parameters (`beta_c_sm`, `beta_c_sf` at
their lower bound `0.05` — consistent with the estimation run) excluded from
the Hessian computation. The free-parameter Hessian is then symmetrised.

The VCV is the Moore-Penrose pseudo-inverse of H (rcond = 1e-10), consistent
with the `compute_standard_errors` function in `enh_RURO_estimate_FR.py` that
uses pseudo-inverse for ill-conditioned Hessians (condition number ≈ 5.1×10¹⁰).

### 3.2 D1 — Joint Wald test

Standard Wald statistic for a linear restriction R·θ = 0 where R is the
7-row selection matrix for {β_E_drgn2, …, β_E_drgn8}:

```
W = θ_R' · V_RR⁻¹ · θ_R  ~  χ²(7)  under H₀
```

V_RR is the 7×7 sub-block of the full VCV. The individual parameter table
uses the original SEs and p-values from `params.csv` (from the GAMSPy solver's
internal Hessian), which are more precise than the finite-difference recomputed
values. The Wald statistic itself uses the recomputed VCV because it requires
the full joint covariance structure, which was not saved from the original run.

### 3.3 D2 — Region covariance block

Direct extraction of the 7×7 sub-block of V and the derived correlation matrix.
Pairs with |corr| > 0.70 are flagged.

### 3.4 D3 — GSUR+region Hessian sub-block eigenvalues

The 8×8 sub-block of H spanning {β_E_gsur, β_E_drgn2, …, β_E_drgn8} is
extracted and its eigenvalues computed via `numpy.linalg.eigvalsh`. All 8
eigenvalues positive implies the objective function is locally convex in the
GSUR+region direction at the solution.

---

## 4. Outputs

All outputs in `Results/`:

| File | Description |
|---|---|
| `RURO_occ_M1_clean_supplementary_diagnostics_v1.md` | Primary report — D1, D2, D3 results and interpretation |
| `RURO_occ_M1_clean_vcv_region_block_20260518_125924.csv` | 7×7 region VCV (raw matrix) |
| `RURO_occ_M1_clean_hessian_region_block_20260518_125924.csv` | 8×8 GSUR+region Hessian sub-block |

### Key numerical results

**D1 (joint Wald test, 7 d.f.):** W = 28.18, p = 0.000204  
The seven region dummies are jointly highly significant.

**D1 (individual significance at 5%):**

| Parameter | p-value | Sig |
|---|---|---|
| β_E_drgn2 | 0.0026 | ** |
| β_E_drgn3 | 0.0394 | * |
| β_E_drgn4 | 0.0001 | *** |
| β_E_drgn5 | 0.0045 | ** |
| β_E_drgn6 | 0.0192 | * |
| β_E_drgn7 | 0.0399 | * |
| β_E_drgn8 | 0.0974 | — |

drgn8 (Méditerranée, drgn1=8) is not individually significant at 5%; joint
significance is preserved. The Wald test is the relevant evidence here; dropping
the whole block because of one marginal dummy would be incorrect.

**D2 (collinearity):** No pair exceeds |corr| = 0.70. Maximum pairwise
correlation is ≈ 0.19, consistent with the mutually exclusive by-construction
structure of a region dummy set (households are in exactly one region, so
drgn_i × drgn_j cross-second-derivatives in the Hessian are zero — confirmed
in the raw CSV).

**D3 (GSUR+region eigenvalues):** All 8 eigenvalues positive (range: 5.77 to
285.5). No saddle-point direction in the GSUR+region block.

---

## 5. Package classification

### Classification: research-only / stage-specific

This script is **not** package-core and must not be shipped as a reusable
package module in its current form. Reasons:

1. **Specification-specific hardcoding**: `REGION_PARAMS` and `GSUR_REGION_PARAMS`
   are lists of M1-clean parameter names. Output filenames and report prose
   reference "M1-clean" explicitly. A future specification with a different
   regional structure would require code changes, not config changes.

2. **Wrong location for package code**: the script lives in
   `scripts/diagnostics/` (moved from `scripts/enhanced/` after creation),
   consistent with the policy in `docs/PIPELINE_ENTRYPOINTS.md` §Diagnostics:
   "Manual diagnostic scripts belong in `scripts/diagnostics/`. They are useful
   for investigation, but they are not pipeline entrypoints."

3. **Hessian recomputation is expensive and duplicative**: the main estimator
   already computes a Hessian during the SE step but does not save the full
   matrix. Package-quality code would either (a) save the matrix once at
   estimation time and consume it here, or (b) expose a generic block-diagnostic
   utility driven by a config-specified parameter list.

4. **Report generation is hardcoded**: section titles, file names, and
   interpretation strings are specific to M1-clean. A generic diagnostic utility
   would accept a parameter-block config and produce a neutral template.

### What to retain for the future package

The following *logic* inside the script is worth extracting as generic utilities
before package publication:

| Reusable function | Current location | Future home |
|---|---|---|
| `compute_numerical_hessian` | `RURO_post_estimation_M1_diagnostics.py` | `estimation_engine.py` or `estimation_utils.py` |
| `diagnostic_d1_wald_test` (generalised to any R matrix) | same | generic `diagnostics_utils.py` |
| `diagnostic_d2_region_vcv` (generalised to any param block) | same | generic `diagnostics_utils.py` |
| `write_matrix_csv` | same | generic `diagnostics_utils.py` |

The `diagnostic_d3_gsur_region_hessian` function is specific to a GSUR+region
design and should be replaced by a generic "Hessian sub-block eigenvalues for
a named parameter group" utility driven by config.

### Archival status

The script and its outputs are retained for provenance of the M1-clean verdict.
Before package publication:

- archive the script as `scripts/diagnostics/archive/RURO_post_estimation_M1_diagnostics_research_v1.py`
  (or equivalent);
- extract the generic functions above into package utilities;
- the three output files in `Results/` remain as empirical provenance and are
  not deleted.

---

## 6. Interpretation in context

The M1-specific diagnostics answer the identification question for the new
regional block. They do **not** by themselves constitute the M1-clean model
verdict. The full verdict still requires:

1. Standard fit assessment from
   `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_standard_post_estimation_diagnostics_v1.md`
   (completed).
2. These M1-specific supplementary diagnostics (completed in this step).
3. A final comparative decision: keep M1-clean as the production specification,
   pool regions, or proceed to M1-naive robustness.

The diagnostics are favorable for keeping M1-clean:
- joint regional significance is strong (p < 0.001);
- no collinearity;
- well-conditioned regional Hessian sub-block.

The one remaining weakness noted in the standard diagnostics (singles-male
hours-bin fit degradation at L1) is an inherited consequence of all-positive
region shifters pushing probability mass into the 21–30h bin, not an
identification failure. Whether that tradeoff is acceptable relative to the
welfare-partition gain is the substance of the M1-clean verdict, which is a
separate step.

---

## 7. Script location and invocation

**Final location**: `scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`

**Invocation that produced these results**:

```
python scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py \
  --params-csv "outputs/post_estimation/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-56-41/params.csv" \
  --results-json "outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json" \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --spec "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml" \
  --output-dir "Results" \
  --eps 1e-5
```

Runtime: approximately 3–5 minutes (53×53 Hessian recomputation via 106
gradient evaluations over the full GSURv2 dataset).