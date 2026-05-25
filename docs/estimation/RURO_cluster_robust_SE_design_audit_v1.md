# RURO Cluster-Robust Standard Error Infrastructure Design Audit v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Audit verdict

**GA17 status: PENDING.**

The existing standard-error infrastructure is Hessian-only. There is no
cluster-robust sandwich estimator in any script. All four SE-relevant files
(`compute_standard_errors.py`, `estimation_engine.py`,
`enh_RURO_estimate_FR.py`, `gamspy_estimation_vectorized.py`) were grepped
for `cluster`, `sandwich`, `robust`, `vcov`, and `covariance` — zero matches
in all four.

GA17 can be cleared before pooled estimation by implementing a callable
smoke-test function that computes the sandwich covariance on a dummy-theta
vector. Completing the full implementation requires access to estimated
parameters but the scaffolding — score extractor, meat assembler,
sandwich combiner — can be written and unit-tested independently.

---

## 2. Files inspected

| File | Lines inspected | Purpose |
|------|-----------------|---------|
| `scripts/enhanced/compute_standard_errors.py` | All (380 lines) | Standalone SE script |
| `scripts/enhanced/estimation_engine.py` | 1–1100 (likelihood + gradient functions) | Core likelihood and analytical gradient |
| `scripts/enhanced/estimation_utils.py` | 1–750 (data structures + precompute) | PrecomputedDataSingles, PrecomputedDataCouples |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | 1–294 | Main estimation script, in-script SE function |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | 1–250 | GAMSPy solver wrapper |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | All | Target pooled YAML (55 params) |
| `Results/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md` | All | Gate-A record |

---

## 3. Current standard-error infrastructure

Two SE implementations exist. Both are Hessian-only. Neither accepts a
cluster argument.

**`compute_standard_errors.py` (standalone script):**

```
compute_standard_errors(theta, grad_func, eps=1e-4, use_pinv=True, rcond=1e-10)
```

Computes the numerical Hessian of the negative log-likelihood via central
differences, then inverts to obtain the variance-covariance matrix.

**`enh_RURO_estimate_FR.py` (in-script function, lines 166–294):**

Same algorithm with additional logic:
- Free-parameter mask: parameters at their bounds are excluded from the
  variance-covariance computation.
- Bound-tolerance guard: a parameter is "at bound" if it is within 1 × 10⁻⁶
  of the lower or upper bound.
- Pseudoinverse fallback: if the Hessian is not invertible, `np.linalg.pinv`
  is used.
- SE is reported as zero for parameters at bounds.

Neither implementation computes scores, a meat matrix, or a sandwich estimator.

---

## 4. How the current Hessian / variance-covariance is computed

The central-difference Hessian formula used in both implementations:

```
H[:, i] = (grad_func(θ + ε·eᵢ) - grad_func(θ - ε·eᵢ)) / 2ε
```

where `grad_func` returns the gradient of the **negative** log-likelihood
(∇_θ(−ℓ)) and `eᵢ` is the i-th unit vector.

After symmetrization (`H = (H + H.T) / 2`):

```
VarCov = inv(H)   or   pinv(H)
SE[k]  = sqrt(abs(VarCov[k, k]))
```

The resulting SEs are valid under i.i.d. draws from the choice-set proposal
distribution. They are not valid under clustered sampling, where households
contribute multiple draws and appear in multiple survey years.

---

## 5. Whether per-observation log-likelihood contributions are available

Yes, with minor modification.

`compute_likelihood_singles` accepts `return_components=True` and returns a
dict containing `V` (n_obs,), `lse` (n_groups,), and `V_obs` (n_groups,).

The per-choice-set log-likelihood contribution is:

```
ll_g = V_obs[g] - lse[g]      (positive LL for group g)
```

A per-row breakdown is not needed; the natural score unit is the choice set
(one household-year × 100 draws). No structural change is required to
expose per-choice-set contributions. An analogous path exists for
`compute_likelihood_couples`.

---

## 6. Whether per-cluster log-likelihood contributions are available

Not yet directly accessible, but straightforwardly derivable.

The gradient computation in `compute_gradient_singles` already loops over
choice sets (groups) and computes the per-group score vector:

```python
for g in range(data.n_groups):
    start, end = data.group_starts[g], data.group_ends[g]
    P_group = np.exp(V_group - lse[g])
    dV_obs   = dV_dtheta[start, :]
    dV_exp   = P_group @ dV_dtheta[start:end, :]
    grad    += dV_obs - dV_exp
```

The quantity `(dV_obs - dV_exp)` is the score contribution of choice set `g`
for the positive log-likelihood (note: `compute_gradient_singles` negates the
running sum and returns ∇(-ℓ); scores for ℓ are the negatives).

To obtain per-cluster scores, the score vectors must be saved per group and
then aggregated to the cluster level using `idorighh`. This requires adding a
`return_scores=True` mode to the gradient functions.

---

## 7. Correct cluster definition

The cluster key is `cluster_id = idorighh` (original household identifier).

In the pooled parquet (`fr_p3a_gsurv2_harmonised.parquet`), GA16 confirmed
that `cluster_id == idorighh` for 100% of sampled rows. The dataset contains
9,657 unique clusters.

A household with survey appearances in two years (e.g., FR_2015 and FR_2016)
contributes two sets of choice sets but belongs to one cluster. The robust
meat matrix must sum score vectors over all choice sets belonging to the same
`idorighh`, whether those choice sets come from singles or couples rows, and
whether they come from FR_2015, FR_2016, or FR_2017.

The joint optimization is over a single parameter vector θ (55 parameters).
Singles and couples contribute to the same Hessian and to the same meat
matrix. Cross-group aggregation to the cluster level must be performed after
all four group scores (singles-male, singles-female, couples-male,
couples-female) are collected.

---

## 8. Correct score object for the RURO/MNL likelihood

The per-choice-set score for the positive log-likelihood is:

```
s_g = ∂ℓ_g/∂θ = (dV_obs_g - dV_exp_g)
```

where:
- `dV_obs_g = dV_dtheta[start_g, :]`   (n_params,) — derivative of V at the
  observed alternative (draw = 0, index `group_starts[g]`)
- `dV_exp_g = P_g @ dV_dtheta[start_g:end_g, :]`   (n_params,) —
  softmax-weighted mean derivative over the 100-draw choice set

This is the per-group score already computed inside `compute_gradient_singles`
and `compute_gradient_couples`, minus the negation applied before return.

The cluster score is the sum of all per-group scores belonging to cluster j:

```
s_j = Σ_{g ∈ j} s_g
```

where "g ∈ j" means choice set g belongs to a household with
`idorighh == j`.

The meat matrix is:

```
B = Σ_j s_j s_j'        (n_params × n_params)
```

The sandwich covariance is:

```
V_cluster = H⁻¹ B H⁻¹
```

where H is the Hessian of the negative log-likelihood (i.e., the same H
used in the current Hessian-only SE computation).

**Sign convention:** `grad_func` returns ∇(-ℓ). Scores for the sandwich
formula require ∇(+ℓ) = −∇(−ℓ). The score sign must be flipped relative to
the gradient returned by `compute_gradient_singles` / `compute_gradient_joint`.

---

## 9. Treatment of draw-expanded rows

The pooled parquet has 1,244,500 rows = 12,445 household-years × 100 draws.

The choice set for household-year g spans rows `[group_starts[g], group_ends[g])`,
which is exactly 100 rows (100 draws). Within that choice set, `draw == 0`
is the observed alternative and `draw == 1, …, 99` are the 100 Monte Carlo
draws from the importance sampling proposal.

The score `s_g` is already the result of integrating over all 100 draws
(the softmax probability `P_g` weights each draw). The correct per-choice-set
score is a single (n_params,) vector — there is no per-draw score; drawing
is fully handled inside the MNL likelihood.

The meat matrix assembler must loop over choice sets (groups), not over rows.
The `group_starts` and `group_ends` arrays in `PrecomputedDataSingles` and
`PrecomputedDataCouples` define the group-to-row mapping.

---

## 10. Treatment of household-year observations

Each household-year appears once per survey year. A household present in all
three survey years contributes three sets of choice sets: one from the
FR_2015 subset, one from FR_2016, and one from FR_2017.

In the pooled data, the household is identified by `idorighh`. The
`idhh` column (used in group_starts / group_ends as `group_ids`) is a
stacked identifier that may be constructed as
`idorighh * year_tag_multiplier + year_tag` or similar to ensure uniqueness
across years. The cluster key for robust SE is `idorighh`, not `idhh`.

When computing per-cluster scores, the aggregation must use `idorighh`
as the grouping key, not `idhh`. This means the score extractor must have
access to the `idorighh` column (or equivalently, a mapping from choice-set
index to `idorighh`).

---

## 11. Treatment of repeated households across years

A household observed in two or three survey years is one cluster. Its
repeated observations are not independent — the same household's preferences
govern labor supply in all years it appears.

The sandwich estimator handles this correctly by construction: all choice sets
belonging to the same `idorighh` are summed into one cluster score `s_j`
before the outer product `s_j s_j'` is formed. This is the clustered variant
of the "sandwich" formula. The standard correction factor J/(J-1) can optionally
be applied (J = 9,657 clusters), but for a dataset of this size its effect is
negligible.

Clustering at `idorighh` is conservative relative to clustering at `idhh`
(household-year): it absorbs both within-year and cross-year dependence.

---

## 12. Treatment of weights

No survey weights are currently used in the likelihood. The current
`compute_likelihood_singles` and `compute_likelihood_couples` do not weight
choice sets by population weights; all household-years enter the likelihood
with equal weight.

If survey weights were added in future, the weighted sandwich estimator
would require `s_j = Σ_{g ∈ j} w_g s_g` where `w_g` is the choice-set
weight. No weight adjustment is needed for the current (unweighted) pooled
estimator.

---

## 13. Treatment of fixed and bounded parameters

The current Hessian-based SE code in `enh_RURO_estimate_FR.py` applies a
free-parameter mask: parameters exactly at a bound (within tolerance 1 × 10⁻⁶)
receive SE = 0.

The sandwich SE implementation must use the same free-parameter mask. The
sub-Hessian H_free and sub-meat B_free should be assembled over the free
parameters only, the sandwich covariance inverted in that subspace, and
full-dimension SE assembled with zeros at bounded positions.

The parameter `theta_c` for couples is fixed at 0.0 and not estimated (it
does not appear in `initial_values` or `optimization.bounds` in the P3a
pooled YAML). It must not appear in the sandwich computation.

---

## 14. Treatment of singles and couples income columns

**GA15 carry-forward.**

In the pooled parquet, `ils_dispy_real` is the CPI-deflated real income column
for **singles only**. It is non-null for all 500,700 singles rows and null for
all 743,800 couples rows.

Couples real income is held in `ils_dispy_male` and `ils_dispy_female`. The
estimation engine uses `consumption_male` and `consumption_female` for couples
(the `PrecomputedDataCouples.consumption` field is the normalized household sum
`(ils_dispy_male + ils_dispy_female) / mean`).

**Implication for the cluster-robust implementation:**

The score extractor for singles reads precomputed arrays from
`PrecomputedDataSingles` (whose `consumption` field derives from
`ils_dispy_real` via `c_norm`). The score extractor for couples reads from
`PrecomputedDataCouples` (whose `consumption` derives from the sum of
`ils_dispy_male` and `ils_dispy_female`). The two paths use different source
columns and must not be confused.

Any implementation prompt or authorization must explicitly state which income
column feeds each group's consumption, so that CPI-deflation correctness
can be confirmed independently for each group.

---

## 15. Feasible implementation strategy

The recommended implementation is a single new function
`compute_cluster_robust_se` in `scripts/enhanced/compute_standard_errors.py`.

**Inputs:**
- `theta`: converged parameter vector (n_params,)
- `grad_func_singles_m`, `grad_func_singles_f`, `grad_func_couples`:
  callables returning per-group score matrices (n_groups × n_params) for
  the positive LL — implemented as `return_scores=True` modes added to the
  existing gradient functions.
- `idorighh_singles_m`, `idorighh_singles_f`, `idorighh_couples`:
  arrays of shape (n_groups,) giving the cluster key for each choice set.
- `hessian`: precomputed Hessian H (n_params × n_params), as returned by
  the existing SE code. The bread is the same whether SE is Hessian-only
  or sandwich.
- Optional `free_mask`: boolean array (n_params,) identifying estimated params.

**Algorithm:**

1. Call each `grad_func_*` with `return_scores=True` to obtain
   per-choice-set score arrays (n_groups_* × n_params) for ∇ℓ.
2. Stack all choice-set scores together with their `idorighh` keys.
3. For each unique cluster j, sum scores over all choice sets with
   `idorighh == j` to get `s_j` (n_params,).
4. Assemble meat: `B = Σ_j s_j @ s_j.T` (n_params × n_params).
5. Apply free-mask to restrict to estimated parameters.
6. Compute sandwich: `VarCov_robust = H_inv @ B_free @ H_inv`.
7. SE_robust = sqrt(abs(diag(VarCov_robust))).
8. Optionally apply finite-sample correction J/(J-1).

---

## 16. Numerical versus analytical score strategy

**Recommendation: use analytical scores.**

The analytical gradient machinery already exists in `estimation_engine.py`.
Each gradient function (`compute_gradient_singles`, `compute_gradient_couples`)
internally builds the per-group score loop (lines 810–824 of estimation_engine.py):

```python
for g in range(data.n_groups):
    dV_obs = dV_dtheta[start, :]
    dV_exp = P_group @ dV_dtheta[start:end, :]
    grad  += dV_obs - dV_exp
```

Adding `return_scores=True` saves `(dV_obs - dV_exp)` for each g into a
preallocated `(n_groups, n_params)` array before accumulating into `grad`.
No additional function evaluations are required.

**Numerical alternative (finite-difference cluster scores):**

If per-group scores were not accessible analytically, the meat could be
estimated numerically: for each cluster j, evaluate
`[ℓ(θ + ε·eₖ; data_j) - ℓ(θ - ε·eₖ; data_j)] / 2ε` to get score k for
cluster j. This requires 2 × n_params × n_clusters = 2 × 55 × 9,657 ≈
1.06 M likelihood evaluations — feasible but approximately 100× slower than
the analytical path. The analytical path is strongly preferred.

---

## 17. Required code modules

The minimum callable infrastructure required to clear GA17:

| Module / location | Required change |
|-------------------|-----------------|
| `scripts/enhanced/estimation_engine.py` | Add `return_scores: bool = False` parameter to `compute_gradient_singles` and `compute_gradient_couples`. When True, return a tuple `(grad, score_matrix)` where `score_matrix` is shape `(n_groups, n_params)` containing per-group `(dV_obs - dV_exp)` for the positive LL (i.e., negated relative to the existing return value). |
| `scripts/enhanced/estimation_engine.py` | Add `compute_gradient_joint_with_scores(theta, ...) -> Tuple[np.ndarray, np.ndarray, np.ndarray]` wrapper that calls `compute_gradient_singles` (×2) and `compute_gradient_couples` with `return_scores=True` and stacks the score matrices with their `idorighh` arrays. |
| `scripts/enhanced/compute_standard_errors.py` | Add `compute_cluster_robust_se(theta, hessian, score_extractor, free_mask, n_clusters) -> Tuple[np.ndarray, np.ndarray]` returning `(se_robust, varcov_robust)`. |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | After estimation converges, call `compute_cluster_robust_se` in addition to (or in place of) the existing Hessian SE function. Log both sets of SEs. |

The `idorighh` arrays must be extracted from the precomputed data objects or
from the underlying DataFrame before estimation starts, and passed alongside
the data objects. The `PrecomputedDataSingles` and `PrecomputedDataCouples`
dataclasses should be extended with a `cluster_ids` field (n_groups,) holding
the `idorighh` value for each choice-set group.

---

## 18. Required validation tests

The following tests must pass before GA17 is cleared:

| Test | Criterion |
|------|-----------|
| **T1. Score consistency** | `sum(score_matrix, axis=0)` equals `-grad_func(theta)` (within 1e-10). Verifies that the per-group scores aggregate to the full gradient. |
| **T2. Meat matrix symmetry** | `max(abs(B - B.T)) < 1e-10`. |
| **T3. Cluster count** | Number of unique `idorighh` values contributing to B equals 9,657. |
| **T4. SE positivity** | All cluster-robust SEs for free parameters are strictly positive when evaluated at a non-degenerate theta. |
| **T5. Hessian sandwich consistency** | At a correctly converged theta, cluster-robust SEs should be ≥ Hessian SEs for most parameters (clustering inflates SEs when there is within-cluster correlation). Flag any parameter where robust SE < Hessian SE for review. |
| **T6. Dummy-theta smoke test** | `compute_cluster_robust_se` runs without error at `theta = initial_values` (the all-zero/default starting vector), returning finite SEs. This is the GA17 clearance test; it does not require completed estimation. |

T6 is the minimum test needed to record GA17 as CONFIRMED before pooled
estimation begins.

---

## 19. Memory and runtime risks

**Memory:**

The per-group score matrix has shape `(n_groups, n_params)`. For the pooled
data:

- Singles: `n_groups_sm + n_groups_sf ≈ 5,007 households × 100 draws / 100 = 5,007 choice sets`
- Couples: `n_groups_couples ≈ 7,438 households × 100 draws / 100 = 7,438 choice sets`
- Total groups: ≈ 12,445
- n_params: 55

Score matrix size: `12,445 × 55 × 8 bytes ≈ 5.5 MB`. This is negligible.

**Hessian reuse:** The Hessian H is already computed for Hessian-based SEs
(2 × 55 × n_params evaluations of grad_func ≈ 110 gradient evaluations). The
sandwich computation reuses H; no additional Hessian evaluations are needed.

**Meat assembly:** One outer product of shape (55,) per cluster, summed over
9,657 clusters. Cost is 9,657 × 55² ≈ 29 M floating-point operations — under
1 ms on any modern CPU.

**Runtime conclusion:** The entire cluster-robust SE computation after
estimation converges is dominated by the Hessian evaluation, which is already
performed. The incremental cost of the meat matrix and sandwich combination
is negligible.

---

## 20. Whether implementation is feasible now

**Yes.** All prerequisites are present:

- Analytical gradient functions are implemented and tested (`compute_gradient_singles`,
  `compute_gradient_couples`, `compute_gradient_joint`).
- The per-group score loop is already written inside those functions (lines
  810–824 of estimation_engine.py); adding `return_scores=True` requires
  approximately 10 lines of modification per function.
- The cluster key `idorighh` is present in the parquet and confirmed equal to
  `cluster_id` (GA16 PASS).
- The group-to-`idhh` mapping is already in `PrecomputedDataSingles.group_ids`;
  adding an `idorighh`-based `cluster_ids` field is a minor extension.
- The meat matrix and sandwich combination are simple NumPy operations.

The T6 smoke test (GA17 clearance) can be run immediately after the score
extractor is added, before any estimation is run, using `initial_values`
as the dummy theta.

**Blocking dependency:** The implementation does not require completed
pooled estimation results. GA17 can be cleared by implementing the
smoke-test callable and confirming T1–T6 pass.

---

## 21. What not to implement

| Item | Reason |
|------|--------|
| HC3 / leverage-corrected sandwich | Not needed for large-sample MNL; 9,657 clusters is adequate. |
| Bootstrap SE | Computationally intensive (requires re-estimation); no added value given analytical scores are available. |
| Survey-weight adjustments | Weights are not currently used in the likelihood; adding them is a separate design decision. |
| Per-draw (row-level) scores | Draw-level decomposition is not required; the score is defined at the choice-set (household-year) level. |
| Numerical cluster scores | The analytical path is 100× faster; numerical scores are a fallback only if analytical gradients are removed. |
| Separate robust SE scripts for singles / couples | Unnecessary; a single `compute_cluster_robust_se` function accepts the stacked score matrix and a single `idorighh` array. |
| Recoding `group_ids` from `idhh` to `idorighh` | The stacked `idhh` is needed for group_starts / group_ends; `cluster_ids` (n_groups,) is a separate field holding `idorighh`. Both coexist in the dataclass. |
| Welfare computation | Not authorized; separately gated. |
| Pooled estimation before GA17 is cleared | The sandwich infrastructure should be implemented and smoke-tested (T6) before estimation is authorized. |

---

## 22. Exact Claude Code implementation prompt

```
Work locally in my RURO/MNL codebase.
This is the GA17 cluster-robust SE implementation task.
Do not run pooled estimation.
Do not modify the pooled parquet.

Read before making changes:
  - docs/RURO_cluster_robust_SE_design_audit_v1.md  (this audit)
  - scripts/enhanced/estimation_engine.py            (full file)
  - scripts/enhanced/estimation_utils.py             (full file)
  - scripts/enhanced/compute_standard_errors.py      (full file)
  - scripts/enhanced/enh_RURO_estimate_FR.py         (lines 160–294)

Task A — Extend estimation_engine.py:

  1. Modify `compute_gradient_singles(theta, data, spec)`:
     - Add parameter `return_scores: bool = False`.
     - When return_scores=True, collect the per-group score for the POSITIVE
       log-likelihood:
           score_g = -(dV_obs_g - dV_exp_g)   [negate the gradient-sign convention]
       into a preallocated array `scores` of shape (data.n_groups, n_params).
     - Return `(grad, scores)` when return_scores=True, else return `grad` as
       before. The existing calling convention must not change.
     - Apply the same change to `compute_gradient_couples`.

  2. Add function `compute_scores_joint(theta, data_sm, data_sf, data_c, spec)`:
     - Returns a tuple: (scores_all, cluster_ids_all) where
       scores_all  has shape (n_groups_total, n_params)
       cluster_ids_all has shape (n_groups_total,)   [idorighh per group]
     - Calls compute_gradient_singles(return_scores=True) for sm and sf,
       compute_gradient_couples(return_scores=True) for couples.
     - Reads cluster_ids from data.cluster_ids (see Task B below).
     - Stack: np.vstack for scores, np.concatenate for cluster_ids.

Task B — Extend PrecomputedDataSingles and PrecomputedDataCouples
         in estimation_utils.py:

  3. Add field `cluster_ids: np.ndarray` to PrecomputedDataSingles (n_groups,).
     This array contains the idorighh value for each choice-set group.
     It is extracted in precompute_data_singles from the first-row of each
     group: `cluster_ids = df["idorighh"].values[data.group_starts]`.
     (group_starts already indexes the first row of each choice set.)

  4. Apply the same extension to PrecomputedDataCouples.

Task C — Add cluster-robust SE function to compute_standard_errors.py:

  5. Add function:

       def compute_cluster_robust_se(
           hessian: np.ndarray,
           scores_all: np.ndarray,
           cluster_ids_all: np.ndarray,
           free_mask: Optional[np.ndarray] = None,
       ) -> Tuple[np.ndarray, np.ndarray]:
           """
           Sandwich covariance: V = H^{-1} B H^{-1}
           where B = sum_j s_j s_j', s_j = sum_{g in j} scores_all[g]

           Returns (se_robust, varcov_robust).
           se_robust[k] = 0 if free_mask is given and free_mask[k] is False.
           """

     The function must:
     a. For each unique cluster j in cluster_ids_all, sum rows of scores_all
        with cluster_ids_all == j to form s_j.
     b. Accumulate B += np.outer(s_j, s_j).
     c. Apply free_mask: restrict H and B to free parameters; compute
        H_free_inv = np.linalg.pinv(H[free_mask][:, free_mask]).
     d. Compute VarCov_free = H_free_inv @ B_free @ H_free_inv.
     e. Assemble full-dimension varcov_robust (n_params × n_params) with zeros
        at masked rows/cols.
     f. se_robust = np.sqrt(np.abs(np.diag(varcov_robust))).

Task D — Wire into enh_RURO_estimate_FR.py:

  6. After estimation converges and Hessian SEs are computed, call:
       scores_all, cluster_ids_all = compute_scores_joint(
           theta_opt, data_sm, data_sf, data_couples, spec
       )
       se_robust, varcov_robust = compute_cluster_robust_se(
           hessian, scores_all, cluster_ids_all, free_mask=free_mask
       )
     Log both se_hessian and se_robust for each parameter.
     Persist varcov_robust to the results JSON alongside varcov_hessian.

Task E — Validation:

  7. Implement and run checks T1–T6 from section 18 of the audit:
     T1: assert np.allclose(scores_all.sum(axis=0), -grad_func(theta), atol=1e-8)
     T2: assert np.max(np.abs(B - B.T)) < 1e-10
     T3: assert len(np.unique(cluster_ids_all)) == 9657
     T4: assert np.all(se_robust[free_mask] > 0)
     T5: log any parameter where se_robust < se_hessian (do not raise)
     T6: run at theta = spec initial_values; confirm finite output

  8. T6 is the GA17 smoke test. Run it at initial_values, not at estimated
     theta. It does not require estimation to be completed.

Commit order:
  a. Commit estimation_utils.py changes (Task B): cluster_ids field.
  b. Commit estimation_engine.py changes (Task A): return_scores mode.
  c. Commit compute_standard_errors.py changes (Task C): sandwich function.
  d. Commit enh_RURO_estimate_FR.py changes (Task D): wire-up.
  e. Run T1–T6; commit a validation log to Results/.

Do NOT run pooled estimation.
Do NOT modify the pooled parquet.
Do NOT authorize pooled estimation in this task.
After T6 passes, record GA17 status as CONFIRMED in a new
  Results/RURO_occ_P3a_pooled_gate_A_ga17_clearance_v1.md
with a single verdict line: "GA17: CONFIRMED. T1-T6 PASS."
```

---

*End of audit document.*