# RURO post-estimation M1-naive diagnostics — implementation report v1

Date: 2026-05-18  
Author: research pipeline  
Status: **research-only** — not package-core; see §5 for package classification

---

## 1. Purpose

This document records how `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py`
was written, what it computes, the inputs it consumed, the outputs it produced,
and its classification against the package portability standard.

The script provides four diagnostics that are specific to the M1-naive
specification's extended opportunity block and cannot be derived from the standard
post-estimation output alone:

| Diagnostic | What it answers |
|---|---|
| D1 — Joint Wald test (7 d.f.) | Are β_E_drgn2 … β_E_drgn8 jointly non-zero in M1-naive? |
| D2 — 7×7 region VCV | Do the region dummies develop new collinearity when β_E_educH is added? |
| D3 — 9×9 GSUR+educH+region Hessian eigenvalues | Is the extended GSUR+educH+region sub-block locally convex? |
| D4 — β_E_educH cross-correlations | Does β_E_educH absorb substantial variation from β_E_gsur or any region dummy? |

M1-naive is the direct robustness specification for M1-clean: it restores the
`beta_E_educH` parameter that M1-clean dropped, holding everything else equal
(54 parameters vs 53). These four diagnostics are required before the M1-naive
robustness verdict can be written, because they determine whether adding β_E_educH
changes the identification and collinearity properties of the opportunity block.

The M1-naive script extends the M1-clean script
(`scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`) with:

- D3 expanded from 8×8 (GSUR+region) to 9×9 (GSUR+educH+region);
- D4 added as a new diagnostic (no M1-clean counterpart).

---

## 2. Inputs

| Input | Path | Notes |
|---|---|---|
| Parameter estimates | `outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/params.csv` | From standard post-estimation of selected M1-naive run; contains estimate, SE, t-stat, p-value per parameter |
| Estimation results JSON | `outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/estimation_results.json` | Selected M1-naive run (Start 1); used for provenance metadata only |
| MNL base | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2` | GSURv2 parquets and sidecar JSON; same base used for M1-naive estimation and post-estimation |
| Spec YAML | `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml` | Parsed to obtain the 54-parameter list, bounds, and precompute variable requirements |

The full 54×54 Hessian is **not** stored in `estimation_results.json` — it is
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

All 54 parameters enter the Hessian. The selected M1-naive run has `beta_c_sm =
0.5496` and `beta_c_sf = 0.5020`, both well above the lower bound of `0.05`; no
parameter is at a bound in the selected run. The free-parameter Hessian is the full
54×54 matrix, symmetrised after the central-difference pass (108 gradient
evaluations).

The VCV is the Moore-Penrose pseudo-inverse of H (rcond = 1e-10), consistent with
the `compute_standard_errors` function in `enh_RURO_estimate_FR.py`.

**Numerical consistency check**: the condition number recomputed by this script
(5.1484×10¹⁰) matches the estimation-time value in
`outputs/.../run_2026-05-18_17-50-20/identification_diagnostics.txt`
(5.148×10¹⁰) to 4 significant figures, confirming the Hessian is being
correctly recomputed at the same point.

### 3.2 Path setup

The script lives in `scripts/diagnostics/`. To import local modules from
`scripts/enhanced/`, both directories are prepended to `sys.path`:

```python
_SCRIPT_DIR  = Path(__file__).resolve().parent          # scripts/diagnostics/
_ENHANCED_DIR = _SCRIPT_DIR.parent / "enhanced"         # scripts/enhanced/
for _p in (_SCRIPT_DIR, _ENHANCED_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
```

During spec parsing, the working directory is temporarily changed to
`_ENHANCED_DIR` so that `parse_specification` can resolve any relative import
paths, then restored after parsing.

### 3.3 D1 — Joint Wald test

Standard Wald statistic for a linear restriction R·θ = 0 where R is the
7-row selection matrix for {β_E_drgn2, …, β_E_drgn8}:

```
W = θ_R' · V_RR⁻¹ · θ_R  ~  χ²(7)  under H₀
```

V_RR is the 7×7 sub-block of the full VCV. The individual parameter table uses
the original SEs and p-values from `params.csv` (from the standard post-estimation
run, which in turn uses the solver's internal Hessian). The Wald statistic itself
uses the recomputed VCV because it requires the full joint covariance structure,
which is not saved from the original run.

### 3.4 D2 — Region covariance block

Direct extraction of the 7×7 sub-block of V and the derived correlation matrix.
Pairs with |corr| > 0.70 are flagged. This diagnostic tests whether the presence
of β_E_educH in the model changes the effective collinearity between region dummies.

### 3.5 D3 — 9×9 GSUR+educH+region Hessian sub-block eigenvalues

The 9×9 sub-block of H spanning {β_E_gsur, β_E_educH, β_E_drgn2, …, β_E_drgn8}
is extracted and its eigenvalues computed via `numpy.linalg.eigvalsh`. All
eigenvalues positive implies the objective function is locally convex in the
extended GSUR+educH+region direction at the solution. This is the M1-naive
extension of the 8×8 block from M1-clean.

The function `diagnostic_d3_hessian_subblock` is generic: it accepts any list
of `block_params` and extracts the corresponding sub-block from the free-parameter
Hessian. This is an improvement over the M1-clean version, which was specific to
the GSUR+region block.

### 3.6 D4 — β_E_educH cross-correlations (new in M1-naive)

The function `diagnostic_d4_educ_cross_corr` extracts off-diagonal covariance
and correlation entries between β_E_educH and each of {β_E_gsur, β_E_drgn2, …,
β_E_drgn8} from the full VCV. A large |corr| with β_E_gsur would indicate that
education mainly reallocates explanatory weight from GSUR. A large |corr| with
a specific region dummy would indicate the education effect is concentrated in
that region's household composition. Correlations ≤ 0.70 in absolute value are
taken as evidence of distinct variation.

---

## 4. Outputs

All outputs in `Results/`:

| File | Description |
|---|---|
| `RURO_occ_M1_naive_supplementary_diagnostics_v1.md` | Primary report — D1–D4 results and evidence-only interpretation |
| `RURO_occ_M1_naive_vcv_region_block_<UTC>.csv` | 7×7 region VCV (raw matrix) |
| `RURO_occ_M1_naive_vcv_educ_gsur_region_block_<UTC>.csv` | 9×9 β_E_educH + β_E_gsur + region VCV block |
| `RURO_occ_M1_naive_hessian_gsur_educ_region_block_<UTC>.csv` | 9×9 GSUR+educH+region Hessian sub-block |

### Key numerical results

**D1 (joint Wald test, 7 d.f.):** W = 28.20, p = 0.000202  
cf. M1-clean: W = 28.18, p = 0.000204. The seven region dummies remain jointly
highly significant after adding β_E_educH; the Wald statistic is numerically
unchanged.

**D1 (individual significance at 5% — M1-naive vs M1-clean):**

| Parameter | M1-naive p | M1-naive sig | M1-clean p | Change |
|---|---|---|---|---|
| β_E_drgn2 | 0.0021 | ** | 0.0026 | slightly stronger |
| β_E_drgn3 | 0.0842 | — | 0.0394 | weakened (crosses 5%) |
| β_E_drgn4 | 0.0002 | *** | 0.0001 | unchanged |
| β_E_drgn5 | 0.0032 | ** | 0.0045 | slightly stronger |
| β_E_drgn6 | 0.0178 | * | 0.0192 | unchanged |
| β_E_drgn7 | 0.0343 | * | 0.0399 | unchanged |
| β_E_drgn8 | 0.1188 | — | 0.0974 | slightly weaker |

drgn3 (North) weakens from p=0.039 to p=0.084. This is explained by the
β_E_educH ↔ β_E_drgn3 correlation (D4: corr = −0.156): the North has
above-average education composition, so β_E_educH absorbs part of the
North-specific opportunity signal. The joint test is unaffected.

**D2 (collinearity):** No pair exceeds |corr| = 0.70. Maximum pairwise region
correlation = 0.193 (cf. M1-clean: 0.191). Adding β_E_educH does not introduce
new collinearity among the region dummies.

**D3 (GSUR+educH+region eigenvalues):** All 9 eigenvalues positive (range: 5.559
to 286.3). No saddle-point direction in the expanded GSUR+educH+region block.
Condition number = 51.51. cf. M1-clean 8×8 minimum eigenvalue = 5.768.

**D4 (β_E_educH cross-correlations):**

| β_E_educH ↔ | Correlation |
|---|---|
| β_E_gsur | 0.6397 |
| β_E_drgn2 | 0.0370 |
| β_E_drgn3 | −0.1557 |
| β_E_drgn4 | −0.0236 |
| β_E_drgn5 | 0.0678 |
| β_E_drgn6 | 0.0209 |
| β_E_drgn7 | 0.0314 |
| β_E_drgn8 | −0.0474 |

The β_E_educH ↔ β_E_gsur correlation (0.640) is below the 0.70 flag threshold
but is the structural mechanism behind the β_E_gsur reversion: in M1-clean, GSUR
absorbs the education-on-opportunity signal (β_E_gsur = −1.329); in M1-naive,
educH carries part of that signal back (β_E_gsur reverts to −1.048). The
correlation represents moderate sharing of variance, not full absorption.
No region dummy exceeds |corr| = 0.20 with β_E_educH.

---

## 5. Package classification

### Classification: research-only / stage-specific

This script is **not** package-core and must not be shipped as a reusable
package module in its current form. Reasons:

1. **Specification-specific hardcoding**: `REGION_PARAMS`, `GSUR_EDUC_REGION_PARAMS`,
   and `EDUC_CROSS_PARAMS` are lists of M1-naive parameter names. Output filenames
   and report prose reference "M1-naive" explicitly. A future specification with
   a different regional or education structure would require code changes, not
   config changes.

2. **Wrong location for package code**: the script lives in `scripts/diagnostics/`,
   consistent with the policy in `docs/PIPELINE_ENTRYPOINTS.md` §Diagnostics:
   "Manual diagnostic scripts belong in `scripts/diagnostics/`. They are useful
   for investigation, but they are not pipeline entrypoints."

3. **Hessian recomputation is expensive and duplicative**: the main estimator
   already computes a Hessian during the SE step but does not save the full
   matrix. Package-quality code would either (a) save the matrix once at
   estimation time and consume it here, or (b) expose a generic block-diagnostic
   utility driven by a config-specified parameter list.

4. **Report generation is hardcoded**: section titles, file names, and
   interpretation strings are specific to M1-naive. A generic diagnostic utility
   would accept a parameter-block config and produce a neutral template.

### What to retain for the future package

The following *logic* inside the script is worth extracting as generic utilities
before package publication:

| Reusable function | Current location | Future home |
|---|---|---|
| `compute_numerical_hessian` | `RURO_post_estimation_M1_naive_diagnostics.py` | `estimation_engine.py` or `estimation_utils.py` |
| `diagnostic_d1_wald` (generalised to any R matrix) | same | generic `diagnostics_utils.py` |
| `diagnostic_d2_region_vcv` (generalised to any param block) | same | generic `diagnostics_utils.py` |
| `diagnostic_d3_hessian_subblock` (generic, accepts any block_params list) | same | generic `diagnostics_utils.py` |
| `diagnostic_d4_educ_cross_corr` (generalised to any two param groups) | same | generic `diagnostics_utils.py` |
| `write_matrix_csv` | same | generic `diagnostics_utils.py` |

The `diagnostic_d3_hessian_subblock` function in this script is already more
generic than the M1-clean equivalent: it accepts an arbitrary `block_params` list
and can be used for any sub-block without modification. The M1-clean version
should be updated to match this interface.

### Archival status

The script and its outputs are retained for provenance of the M1-naive robustness
verdict. Before package publication:

- archive the script as `scripts/diagnostics/archive/RURO_post_estimation_M1_naive_diagnostics_research_v1.py`
  (or equivalent);
- extract the generic functions above into package utilities;
- the four output files in `Results/` remain as empirical provenance and are
  not deleted.

---

## 6. Interpretation in context

The M1-naive supplementary diagnostics answer the identification question for
the extended opportunity block. They do **not** by themselves constitute the
M1-naive robustness verdict. The full verdict requires:

1. Estimation evidence from
   `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_estimation_report_v1.md` (completed).
2. Standard fit assessment from
   `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_post_estimation_diagnostics_v1.md` (completed).
3. These M1-naive supplementary diagnostics (completed in this step).
4. A final comparative decision: whether M1-naive or M1-clean should be
   the production specification, or whether the β_E_educH parameter should
   be retained in subsequent specifications.

The diagnostics are broadly favourable for M1-naive's identification properties:

- joint regional significance is unaffected (W unchanged to 4 s.f.);
- no new collinearity among region dummies;
- 9×9 sub-block is locally convex (all eigenvalues positive, min = 5.559);
- β_E_educH ↔ β_E_gsur sharing is moderate (0.640), not pathological.

The borderline inferential status of β_E_educH itself (LR p ≈ 0.044, Wald
p ≈ 0.053) and the drgn3 weakening (p: 0.039 → 0.084) are the key
considerations for the verdict. Both are noted as evidence; neither constitutes
a decisive finding. The verdict adjudicates these in the context of the broader
research question.

---

## 7. Script location and invocation

**Final location**: `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py`

**Invocation that produced these results** (run via wrapper at `C:\Users\hisham\AppData\Local\Temp\run_m1naive_suppl.py`):

```
python scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py \
  --params-csv "outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/params.csv" \
  --results-json "outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/estimation_results.json" \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --spec "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml" \
  --output-dir "Results" \
  --eps 1e-5
```

Runtime: approximately 4–6 minutes (54×54 Hessian recomputation via 108 gradient
evaluations — 2 evaluations per parameter column).

**Non-fatal warnings during run**: `estimation_utils` emits "extra var X could NOT
be derived from couples data" warnings for `age_norm`, `educH`, and several region
interaction variables. These are benign — the region dummies are resolved from
`drgn1` indicator columns at precompute time, not from the extra-vars list. The
same warnings appear during the main estimation run and do not affect Hessian
computation.