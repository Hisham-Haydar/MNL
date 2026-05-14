# RURO `ruro_occ_M0b` — Smoke Test Report v1

Date: 2026-05-14
Script: `Results/_M0b_smoke_test.py`
Python: `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`
MNL data: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl`
Sample: 200 households per group (seed 42), from 167,600 singles and 257,700 couples rows.
Reference spec: `ruro_occ_M0a_clean` (47 params).

---

## Summary

| check | M0b1 | M0b2 |
|---|---|---|
| 1. YAML parses | PASS | PASS |
| 2. MNL files load | PASS | PASS |
| 3. all parameters initialize | PASS | PASS |
| 4. likelihood finite at initial values | PASS | PASS |
| 5. gradients finite | PASS | PASS |
| 6. no NaN/Inf in any component | PASS | PASS |
| 7. `beta_ll` enters only couples utility | PASS | PASS |
| 8. `beta_ll` does not affect singles | PASS | PASS |
| 9. opportunity blocks unchanged from M0a-clean | PASS | PASS |
| 10. prior/proposal correction unchanged | PASS | PASS |
| **Overall** | **PASS (10/10)** | **PASS (10/10)** |

**Both M0b1 and M0b2 pass all smoke tests. No fixes required.**

---

## Check-by-check detail

### 1. YAML parses

Both YAML files parse without error via `estimation_spec_parser.parse_specification`.

| spec | `spec.name` | `n_params` | `couples_interaction_coef` |
|---|---|---|---|
| M0b1 | `ruro_occ_M0b1` | 48 | `beta_ll` |
| M0b2 | `ruro_occ_M0b2` | 48 | `beta_ll` |

### 2. MNL files load

Singles parquet: 167,600 rows. Couples parquet: 257,700 rows. Both loaded
successfully from `fr_2016_RURO_mnl__singles.parquet` and
`fr_2016_RURO_mnl__couples.parquet`.

### 3. All parameters initialize

All 48 parameters in `spec.all_param_names` are present in `spec.initial_values`
for both M0b1 and M0b2. No missing initial values.

`beta_ll` initial value: 0.0 in both specs (confirmed in Gate A report; re-
confirmed here by the parameter initialization check).

### 4. Likelihood finite at initial values

The softmax log-likelihood was evaluated on the 200-household sample at spec
initial values (`beta_ll = 0.0`, all other parameters at M0a-clean defaults).
At `beta_ll = 0` the M0b interaction term contributes zero, so M0b1 and M0b2
produce the same likelihood as M0a-clean at the starting point.

| group | M0b1 log-lik | M0b2 log-lik |
|---|---|---|
| singles male | -1057.0439 | -1057.0439 |
| singles female | -1035.8585 | -1035.8585 |
| couples | -1058.9077 | -1058.9077 |

All values are finite and negative (correct sign for a log-likelihood). The
equality of M0b1 and M0b2 at initial values is expected: the only difference
between them is the `theta_c` upper bound, which does not affect the initial
`theta_c = -1.0` evaluation point (well inside both bounds).

### 5. Gradients finite

Finite-difference gradients (eps = 1e-5) were computed for `beta_c` on the
singles group and for `beta_ll` on the couples group.

| param | M0b1 | M0b2 |
|---|---|---|
| `beta_c` (singles) | OK | OK |
| `beta_ll` (couples) | OK | OK |

All gradient approximations are finite. The `beta_ll` gradient on the couples
group is `BC(L_m, theta_l_m) * BC(L_f, theta_l_f)` per alternative, which is
finite and well-defined at all observed values.

### 6. No NaN/Inf in any component

All utility, opportunity, prior correction, and choice-index arrays were scanned
for NaN and Inf values across all four groups (sm, sf, cou_m, cou_f equivalent
via cou evaluation).

| component | M0b1 | M0b2 |
|---|---|---|
| `U` (preference utility) | clean | clean |
| `interact_contrib` (`beta_ll * bc_l_m * bc_l_f`) | clean | clean |
| `O` (opportunity layer) | clean | clean |
| `log_prior` (proposal correction) | clean | clean |
| `V` (full choice index) | clean | clean |
| `bc_c`, `bc_l_m`, `bc_l_f` | clean | clean |

"Clean" means zero NaN and zero Inf across the entire sampled dataset.

### 7. `beta_ll` enters only couples utility

Test: set `beta_ll = 0.0` vs `beta_ll = 1.5`. The couples V array must differ;
the singles V arrays must be unchanged.

| group | M0b1 | M0b2 |
|---|---|---|
| couples V changes | True | True |
| singles male V unchanged | True | True |

### 8. `beta_ll` does not affect singles

Test: same as check 7, but explicitly checked on singles female (`sf`) in
addition to singles male.

| group | M0b1 | M0b2 |
|---|---|---|
| singles female V unchanged | True | True |

The `beta_ll` interaction term is guarded by `spec.couples_interaction_coef`
in the post-estimation reporter and uses `param_vars[spec.couples_interaction_coef]`
only inside `_build_couples_ll_vectorized` in the vectorized engine. There is
no path for `beta_ll` to enter singles utility.

### 9. Opportunity blocks unchanged from M0a-clean

The `hours_shifters` and `market_opportunity_shifters` coefficient lists were
compared between M0a-clean and M0b1/M0b2.

**Hours opportunity** (all three specs):
`beta_E`, `beta_h_ft`, `beta_h_pt1`, `beta_h_pt2` — identical.

**Market + occupation opportunity** (parser appends occupation onto
`market_opportunity_shifters` for the evaluation path):
`beta_E_educH`, `beta_E_gsur`, `beta_occ_2_cf`, `beta_occ_2_cm`,
`beta_occ_2_sf`, `beta_occ_2_sm`, `beta_occ_3_cf`, `beta_occ_3_cm`,
`beta_occ_3_sf`, `beta_occ_3_sm`, `beta_occ_4_cf`, `beta_occ_4_cm`,
`beta_occ_4_sf`, `beta_occ_4_sm` — identical across all three specs.

Wage opportunity: `sigma` parameter present in all three specs.

### 10. Prior/proposal correction unchanged from M0a-clean

The `log_prior` column (read directly from the parquet) was compared between
the M0a-clean and M0b1/M0b2 evaluations on the same 200-household sample.

| comparison | result |
|---|---|
| M0a-clean vs M0b1 `log_prior` (singles male) | `np.allclose` = True |
| M0a-clean vs M0b2 `log_prior` (couples) | `np.allclose` = True |

The `log_prior` column is data-side (pre-computed in the parquet); no code in
the M0b implementation touches it. The `expression_constraints` block (soft
constraints `mul_cou_m_positive`, `mul_cou_f_positive`) is identical in all
three specs and was not modified.

---

## Verdict

Both `ruro_occ_M0b1` and `ruro_occ_M0b2` pass all 10 smoke tests. There are
no failures and no fixes required.

**Gate A (parse): PASS** (from parse report v1, 2026-05-14).
**Smoke tests: PASS** (this report, 2026-05-14).

Both specs are ready for Gate B (estimation). Run M0b1 first per design memo
§7. Use `--warm-start none` from at least three start points.

---

## How to reproduce

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\Results\_M0b_smoke_test.py"
```

Runtime: ~5 seconds (200-household sample, no GAMSPy solver invoked).
