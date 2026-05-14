# RURO `ruro_occ_M0c_b` — Estimation Report v1

Date: 2026-05-14
Run folder: `run_2026-05-14_18-03-32`
Spec file: `scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml`
Warm-start: `estimation_spec_ruro_occ_M0b2/run_2026-05-14_12-46-04/estimation_results.json`

---

## 1. Command

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py" `
    --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
    --group joint --solver gamspy-conopt --vectorized `
    --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml" `
    --warm-start "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0b2/run_2026-05-14_12-46-04/estimation_results.json" `
    --auto-timestamp --verbose
```

---

## 2. Run folder

`outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0c_b/run_2026-05-14_18-03-32/`

---

## 3. Convergence status

| field | value |
|---|---|
| SolveStatus | NormalCompletion |
| ModelStatus | OptimalLocal |
| iterations | 8 |
| walltime (solver) | 192.0s |
| warm-start from | M0b2 reference run |

8 iterations from the M0b2 warm-start confirms the solution is nearby; the solver needed only minor adjustments from the fixed-theta starting point.

---

## 4. Log-likelihood

| spec | n_params | LL | AIC | notes |
|---|---|---|---|---|
| M0a-clean | 48 | −6521.43 | 13138.9 | singles-shared theta_c; theta_c_singles interior |
| M0b2 | 48 | −6511.47 | 13118.9 | theta_c and beta_ll at upper bounds |
| **M0c_b** | **47** | **−6509.33** | **13112.7** | theta_c fixed at 0.0; beta_ll interior |

**M0c_b improves LL by +2.14 nats vs M0b2** (with one fewer parameter). AIC improves by 6.2 units. Fixing theta_c = 0.0 structurally is supported by the data: the model is better-fitting with one fewer parameter.

---

## 5. `beta_ll` identification

| field | M0b2 | M0c_b |
|---|---|---|
| final value | 2.0000 | **2.5865** |
| bound | [−2.0, 2.0] | [0.0, 10.0] |
| at bound? | **yes** (upper) | **no** — interior |

`beta_ll` is now identified in the interior of [0.0, 10.0] at 2.587. This is the primary success of the M0c_b design: removing the binding `theta_c` constraint frees the model to find the true optimum for leisure-leisure interaction. The value 2.587 means couples have strong complementarity between spouses' leisure.

---

## 6. `theta_c` status

| field | value |
|---|---|
| mode | **structurally fixed** |
| fixed value | 0.0 (log-utility) |
| in estimated params | no |
| in bounds | no |

`theta_c` does not appear in the parameter vector. The couples consumption Box-Cox transform is log(C) for all alternatives. This is consistent with the M0b2 multi-start finding that theta_c = 0.0 is the unique attractor.

---

## 7. New bound hit: `beta_l0_m`

| field | value |
|---|---|
| `beta_l0_m` final | 0.0500 |
| bound | [0.05, 50.0] |
| at bound? | **yes** (lower) |

`beta_l0_m` (couples male leisure intercept) hits its lower bound at 0.05. This is a new binding constraint not present in M0b2. The interpretation is that coupled males have very low base leisure utility — the optimiser pushes the intercept as low as the bound allows. This may reflect:
1. Collinearity between `beta_l0_m` and `beta_ll` (the leisure-leisure interaction term absorbs couples male leisure utility).
2. Genuine model finding: coupled males have near-zero autonomous leisure utility, with all leisure-related utility flowing through the interaction term with their partner's leisure.

---

## 8. Identification diagnostics

| diagnostic | M0b2 | M0c_b | change |
|---|---|---|---|
| n_parameters | 48 | 47 | −1 (theta_c removed) |
| bound hits total | 2 | 1 | −1 (theta_c gone; beta_ll free) |
| bound hits upper | 2 | 0 | −2 |
| bound hits lower | 0 | 1 | +1 (beta_l0_m new) |
| kappa | 8.52×10⁹ | 8.61×10⁹ | ≈ identical |
| negative Hessian eigenvalues | 1 | 1 | **unchanged** |
| near-zero eigenvalues | 0 | 0 | — |
| negative VarCov variances | 3 | 3 | **unchanged** |

**The negative Hessian eigenvalue persists.** Fixing theta_c eliminated the corner at (theta_c, beta_ll) simultaneously at their upper bounds, but `beta_l0_m` has moved to its lower bound, recreating a boundary corner. The structure of the problem is the same: one bound-hit parameter → one negative eigenvalue → Gate B fails.

---

## 9. Parameter stability

| metric | value | interpretation |
|---|---|---|
| matched params | 47/47 | full match |
| delta_L2 | 0.647 | small shift from M0b2 warm-start |
| delta_L2_relative | 0.066 | 6.6% relative shift |
| delta_max_abs | 0.587 | largest single-param move |
| delta_mean_abs | 0.030 | typical move is small |

The solution is stable and close to the M0b2 warm-start. The main moves were in the couples block (beta_ll from 2.0 to 2.587; beta_l0_m to its lower bound).

---

## 10. Parameters with NA standard errors

The same NA cluster pattern as M0b2, with one change:

| parameter | reason |
|---|---|
| `beta_l0_m` | at lower bound (0.05) — **new** |
| `theta_c_singles` | near-singular with `beta_c_sm`, `beta_c_sf` (same as M0b2) |
| `beta_c_sm` | near-singular sub-block |
| `beta_c_sf` | near-singular sub-block |

`theta_c` NA is gone (no longer estimated). `beta_ll` NA is gone (now interior with valid SE). `beta_l0_m` NA is new. Net: 4 NA SEs vs 5 in M0b2 — one improvement, one regression.

---

## 11. Condition number

κ = 8.61×10⁹. Essentially identical to M0b2's 8.52×10⁹. The condition number is dominated by the near-singular `{theta_c_singles, beta_c_sm, beta_c_sf}` sub-block, which is unchanged. Fixing theta_c had no effect on kappa.

---

## 12. Gate B assessment

| criterion | threshold | M0c_b result | pass? |
|---|---|---|---|
| κ | < 10⁷ | 8.61×10⁹ | **FAIL** |
| negative Hessian eigenvalues | 0 | 1 | **FAIL** |
| NA standard errors | 0 | 4 | **FAIL** |
| parameters at strict bounds | 0 | 1 (`beta_l0_m`) | **FAIL** |
| negative VarCov variances | 0 | 3 | **FAIL** |

**Gate B: FAIL on all 5 criteria.** The negative eigenvalue migrated from the (theta_c, beta_ll) corner to the beta_l0_m lower bound. The root identification problem — one bound-hitting parameter creating a non-interior solution — persists.

---

## 13. Verdict

**FLAG — do not use for welfare computation.**

M0c_b achieved its proximate goal: `beta_ll` is now identified in the interior (2.587), and the model is better-fitting than M0b2 (+2.14 nats, AIC −6.2). However, Gate B fails because `beta_l0_m` has moved to its lower bound (0.05), recreating the same structural problem — a boundary solution with one negative Hessian eigenvalue.

The pattern is: fixing one binding constraint reveals a previously masked binding constraint in a different parameter. The data are telling us that the current parameterisation of couples leisure utility is inadequate — the model is trying to push `beta_l0_m` below its lower bound.

**Diagnosis:** `beta_l0_m` at 0.05 (lower bound) while `beta_ll` = 2.587 suggests strong multicollinearity between the male leisure intercept and the leisure-leisure interaction. The interaction term `beta_ll * bc_l_m * bc_l_f` is absorbing all of the couples male leisure utility, leaving the intercept with nothing to contribute. This is a structural identification problem in the couples utility block.

---

## 14. Selected run

**Selected run: `run_2026-05-14_18-03-32`.**

This is the only M0c_b run. Results JSON, CSVs, and identification diagnostics are saved.

---

## 15. Recommendation

**Proceed to M0c_b2: widen or remove the `beta_l0_m` lower bound.**

The immediate fix is to lower `beta_l0_m`'s lower bound from 0.05 to a small positive value (e.g., 0.001 or even 0.0001) or to remove the lower bound entirely (set to 0.0). This will allow the solver to find the true unconstrained optimum for couples male leisure intercept.

**Alternative analysis before M0c_b2:**

The near-zero `beta_l0_m` combined with large `beta_ll` may reflect a genuine structural finding: in the joint estimation, coupled males' autonomous leisure utility is very small, and essentially all their leisure utility is interaction-mediated. This is interpretable but needs Gate B to pass before it can be used.

If `beta_l0_m` moves to 0 after bound removal and still hits the new lower bound, the problem is deeper — the couples utility parameterisation may need rethinking (e.g., separate male and female leisure-leisure interaction terms).

**Recommended M0c_b2 change:**

```yaml
beta_l0_m: [0.001, 50.0]   # was [0.05, 50.0] — lower bound relaxed
```

with initial value `beta_l0_m: 0.05` (warm-start from M0c_b).
