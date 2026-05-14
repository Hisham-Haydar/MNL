# RURO `ruro_occ_M0b` — Gate A Parse Report v1

Date: 2026-05-14
Runner: `parse_specification` from `scripts/enhanced/estimation_spec_parser.py`
Python: `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`

All checks performed immediately after implementation (no estimation run).

---

## Summary

| check | M0a_clean | M0b1 | M0b2 |
|---|---|---|---|
| Parses without error | PASS | PASS | PASS |
| `spec.name` correct | PASS | PASS | PASS |
| `beta_ll` in `all_param_names` | n/a | PASS | PASS |
| `beta_ll` initial value = 0.0 | n/a | PASS | PASS |
| `beta_ll` bounds = [-2.0, 2.0] | n/a | PASS | PASS |
| `theta_c` upper bound | 0.95 (expected) | 0.95 (expected) | **0.0 (expected)** |
| `n_params` = 47 / 48 / 48 | PASS (47) | PASS (48) | PASS (48) |
| M0a-clean unchanged | PASS | — | — |
| `hours_opportunity` coefs match M0a-clean | — | PASS | PASS |
| `market_opportunity` coefs match M0a-clean | — | PASS | PASS |
| `wage_opportunity` sigma param = `sigma` | PASS | PASS | PASS |
| `couples_interaction_coef` | None | `beta_ll` | `beta_ll` |

**All Gate A checks pass.**

---

## 1. Parse status

All three YAML files parsed successfully with `parse_specification`.

| spec | path | parse result |
|---|---|---|
| `ruro_occ_M0a_clean` | `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` | OK |
| `ruro_occ_M0b1` | `scripts/enhanced/estimation_spec_ruro_occ_M0b1.yaml` | OK |
| `ruro_occ_M0b2` | `scripts/enhanced/estimation_spec_ruro_occ_M0b2.yaml` | OK |

---

## 2. Specification names

| spec | `spec.name` | expected | result |
|---|---|---|---|
| M0a_clean | `ruro_occ_M0a_clean` | `ruro_occ_M0a_clean` | PASS |
| M0b1 | `ruro_occ_M0b1` | `ruro_occ_M0b1` | PASS |
| M0b2 | `ruro_occ_M0b2` | `ruro_occ_M0b2` | PASS |

---

## 3. `beta_ll` present in both M0b specs

| spec | `beta_ll` in `all_param_names` | result |
|---|---|---|
| M0a_clean | False (not expected) | PASS |
| M0b1 | True | PASS |
| M0b2 | True | PASS |

`beta_ll` is appended last in the ordered parameter list for both M0b specs,
consistent with `_build_parameter_list` appending `couples_interaction_coef`
at the tail of the list.

---

## 4. `beta_ll` initial value

| spec | `initial_values['beta_ll']` | expected | result |
|---|---|---|---|
| M0a_clean | ABSENT | ABSENT | PASS |
| M0b1 | 0.0 | 0.0 | PASS |
| M0b2 | 0.0 | 0.0 | PASS |

---

## 5. `beta_ll` bounds

| spec | `bounds['beta_ll']` | expected | result |
|---|---|---|---|
| M0a_clean | ABSENT | ABSENT | PASS |
| M0b1 | (-2.0, 2.0) | [-2.0, 2.0] | PASS |
| M0b2 | (-2.0, 2.0) | [-2.0, 2.0] | PASS |

---

## 6. `theta_c` upper bound (couples shared)

| spec | `bounds['theta_c']` | expected | result |
|---|---|---|---|
| M0a_clean | (-8.0, 0.95) | (-8.0, 0.95) | PASS |
| M0b1 | (-8.0, 0.95) | (-8.0, 0.95) | PASS |
| M0b2 | (-8.0, 0.0) | (-8.0, 0.0) | **PASS** |

`theta_c_singles` bound is `(-8.0, 0.95)` in all three specs (unchanged from
M0a-clean, as required).

---

## 7. Parameter count

| spec | `len(all_param_names)` | expected | result |
|---|---|---|---|
| M0a_clean | 47 | 47 | PASS |
| M0b1 | 48 | 48 | PASS |
| M0b2 | 48 | 48 | PASS |

Full parameter lists:

**M0a_clean (47)**:
`beta_l0_sm`, `beta_l_age_sm`, `beta_l_age2_sm`, `beta_c_sm`, `theta_l_sm`,
`beta_l0_sf`, `beta_l_age_sf`, `beta_l_age2_sf`, `beta_l_nkids_sf`,
`beta_c_sf`, `theta_l_sf`, `theta_c_singles`, `beta_l0_m`, `beta_l_age_m`,
`beta_l_age2_m`, `theta_l_m`, `beta_l0_f`, `beta_l_age_f`, `beta_l_age2_f`,
`beta_l_nkids_f`, `theta_l_f`, `beta_c`, `theta_c`, `beta_E`, `beta_h_pt1`,
`beta_h_pt2`, `beta_h_ft`, `beta_E_gsur`, `beta_E_educH`, `beta_occ_2_sm`,
`beta_occ_3_sm`, `beta_occ_4_sm`, `beta_occ_2_sf`, `beta_occ_3_sf`,
`beta_occ_4_sf`, `beta_occ_2_cm`, `beta_occ_3_cm`, `beta_occ_4_cm`,
`beta_occ_2_cf`, `beta_occ_3_cf`, `beta_occ_4_cf`, `beta_w0`,
`beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma`

**M0b1 / M0b2 (48)**: same as M0a-clean, plus `beta_ll` appended at position 48.

---

## 8. M0a-clean unchanged

`parse_specification("estimation_spec_ruro_occ_M0a_clean.yaml")` returns
`spec.name = "ruro_occ_M0a_clean"`, `n_params = 47`,
`couples_interaction_coef = None`. File mtime was not modified by this
implementation. PASS.

---

## 9. Opportunity blocks match M0a-clean

Checked via `spec.hours_shifters` coefficients and `spec.market_opportunity_shifters`
coefficients.

### Hours opportunity

| spec | coefs | matches M0a-clean |
|---|---|---|
| M0b1 | `['beta_E', 'beta_h_pt1', 'beta_h_pt2', 'beta_h_ft']` | PASS |
| M0b2 | `['beta_E', 'beta_h_pt1', 'beta_h_pt2', 'beta_h_ft']` | PASS |

### Market opportunity

| spec | coefs | matches M0a-clean |
|---|---|---|
| M0b1 | `['beta_E_educH', 'beta_E_gsur']` | PASS |
| M0b2 | `['beta_E_educH', 'beta_E_gsur']` | PASS |

Occupation opportunity: 12 `beta_occ_{2,3,4}_{sm,sf,cm,cf}` entries present
in all three specs, byte-identical.

---

## 10. Prior/proposal correction matches M0a-clean

`spec.wage_variance_param = 'sigma'` in all three specs. PASS.

`expression_constraints_enabled = True`, `default_mode = 'soft'`,
`default_weight = 1000.0`, two constraints (`mul_cou_m_positive`,
`mul_cou_f_positive`) in all three specs. PASS.

No modification was made to any code path computing `log_prior` or the
`-log(prior)` subtraction.

---

## Gate A verdict

**PASS** — both M0b1 and M0b2 YAML files are well-formed, parse correctly,
expose `beta_ll` with the correct initial value and bounds, have 48 parameters,
differ from each other only on `spec.name` and the `theta_c` upper bound, and
leave M0a-clean and all opportunity/prior blocks identical.

Ready for Gate B (estimation).
