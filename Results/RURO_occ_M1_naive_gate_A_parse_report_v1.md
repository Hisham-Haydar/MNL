# RURO occ M1-naive — Gate-A Parse Report v1

Date: 2026-05-18
Specification: ruro_occ_M1_naive
YAML file: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml`
Status: **PASS — all 18 checks pass**

---

## 1. Static checks

| # | Check | Result | Observed value |
|---|---|---|---|
| 1 | `specification.name` == `"ruro_occ_M1_naive"` | **PASS** | `"ruro_occ_M1_naive"` |
| 2 | `specification.wage_spec` == `"vw"` | **PASS** | `"vw"` |
| 3 | `specification.model_family` == `"regular"` | **PASS** | `"regular"` |
| 4 | `initial_values` entry count == 54 | **PASS** | 54 entries (see §2) |
| 5 | `optimization.bounds` entry count (free params) | **PASS** | 54 entries; 1-to-1 correspondence with `initial_values`; `theta_c` absent in both (explicitly commented out) |
| 6 | Coefficients in `market_opportunity.shifters` count == 9 | **PASS** | 9: beta_E_gsur, beta_E_educH, beta_E_drgn2–beta_E_drgn8 (see §3) |
| 7 | `beta_E_educH` in `market_opportunity.shifters` with `variable: "educH"` and `interaction: ["working"]` | **PASS** | Present: `variable: "educH"`, `coefficient: "beta_E_educH"`, `interaction: ["working"]` |
| 8 | `beta_E_educH` in `initial_values` with value `0.0` | **PASS** | `beta_E_educH:  0.0` |
| 9 | `beta_E_educH` in `optimization.bounds` with `[-10.0, 10.0]` | **PASS** | `beta_E_educH:  [-10.0, 10.0]` |
| 10 | `beta_E_educH` does NOT have `applies_to:` field | **PASS** | No `applies_to` field on the educH shifter entry — consistent with M0c_b2_GSURv2 form; parser default is `"both"` |
| 11 | All seven region dummies present in `market_opportunity.shifters`, each with `applies_to: "household"` | **PASS** | beta_E_drgn2–beta_E_drgn8 all present; all carry `applies_to: "household"` |
| 12 | All seven region dummies in `initial_values` with value `0.0` | **PASS** | beta_E_drgn2 through beta_E_drgn8, all `0.0` |
| 13 | All seven region dummies in `optimization.bounds` with `[-10.0, 10.0]` | **PASS** | beta_E_drgn2 through beta_E_drgn8, all `[-10.0, 10.0]` |
| 14 | `utility` block identical to M1-clean | **PASS** | `functional_form: "box_cox"`; consumption block (beta_c, theta_c, theta_c_singles, couples_fixed=0.0, box_cox_bounds [-8.0, 0.95]); leisure block (beta_l0, theta_l, box_cox_bounds [-8.0, 0.95], three shifters: age_norm, age_norm2, n_children gender_specific:true) — byte-identical to M1-clean |
| 15 | `wage_opportunity` block identical to M1-clean | **PASS** | `specification: "log_normal"`; mean_shifters: intercept/beta_w0, educL/beta_w_educL, educH/beta_w_educH, pexp_years/beta_w_pexp, pexp_years2/beta_w_pexp2; variance: sigma — byte-identical to M1-clean |
| 16 | `occupation_opportunity` block identical to M1-clean (12 shifters) | **PASS** | `variable: "loc4"`, `reference: 1`; 12 shifters (loc4_2/3/4 × sm/sf/cm/cf), all with `interaction: ["working"]` — byte-identical to M1-clean |
| 17 | `hours_opportunity` block identical to M1-clean (4 shifters) | **PASS** | 4 shifters: working/beta_E, working_pt1/beta_h_pt1, working_pt2/beta_h_pt2, working_ft/beta_h_ft — byte-identical to M1-clean |
| 18 | `optimization.expression_constraints` identical to M1-clean | **PASS** | `enabled: true`, `default_mode: soft`, `default_weight: 1000.0`; two constraints: `mul_cou_m_positive` and `mul_cou_f_positive`, both with `expression: mul`, `at: {consumption: 1.0, leisure_male: 1.0, leisure_female: 1.0}`, `lower: 1.0e-6` — byte-identical to M1-clean |

---

## 2. Parameter count detail

**Total: 54 entries in `initial_values`**

| Group | Parameters | Count |
|---|---|---|
| Singles male (utility) | beta_l0_sm, beta_l_age_sm, beta_l_age2_sm, beta_c_sm, theta_l_sm | 5 |
| Singles female (utility) | beta_l0_sf, beta_l_age_sf, beta_l_age2_sf, beta_l_nkids_sf, beta_c_sf, theta_l_sf | 6 |
| Singles shared | theta_c_singles | 1 |
| Couples male (utility) | beta_l0_m, beta_l_age_m, beta_l_age2_m, theta_l_m | 4 |
| Couples female (utility) | beta_l0_f, beta_l_age_f, beta_l_age2_f, beta_l_nkids_f, theta_l_f | 5 |
| Couples household consumption | beta_c | 1 |
| Hours opportunity | beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft | 4 |
| Market opportunity | beta_E_gsur, beta_E_educH, beta_E_drgn2, beta_E_drgn3, beta_E_drgn4, beta_E_drgn5, beta_E_drgn6, beta_E_drgn7, beta_E_drgn8 | 9 |
| Wage opportunity | beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2 | 5 |
| Occupation opportunity | beta_occ_2_sm, beta_occ_3_sm, beta_occ_4_sm, beta_occ_2_sf, beta_occ_3_sf, beta_occ_4_sf, beta_occ_2_cm, beta_occ_3_cm, beta_occ_4_cm, beta_occ_2_cf, beta_occ_3_cf, beta_occ_4_cf | 12 |
| Wage variance | sigma | 1 |
| Couples interaction | beta_ll | 1 |
| **Total** | | **54** |

`theta_c` (couples consumption Box-Cox exponent) is NOT estimated — fixed at 0.0 via `couples_fixed_box_cox_exponent: 0.0`. Explicitly absent from both `initial_values` and `optimization.bounds` (commented out in both sections). The parser's `_build_parameter_list` skips `theta_c` when `couples_fixed_theta is not None`, consistent with M1-clean behaviour.

**Derivation from M1-clean:** M1-clean has 53 free parameters. M1-naive adds `beta_E_educH` = 53 + 1 = **54**.

---

## 3. market_opportunity.shifters

All 9 shifters as read from the M1-naive YAML:

| # | Coefficient | Variable | Interaction | applies_to |
|---|---|---|---|---|
| 1 | `beta_E_gsur` | `gsur` | `["working"]` | (none — parser default: `"both"`) |
| 2 | `beta_E_educH` | `educH` | `["working"]` | (none — parser default: `"both"`) |
| 3 | `beta_E_drgn2` | `reg2` | `["working"]` | `household` |
| 4 | `beta_E_drgn3` | `reg3` | `["working"]` | `household` |
| 5 | `beta_E_drgn4` | `reg4` | `["working"]` | `household` |
| 6 | `beta_E_drgn5` | `reg5` | `["working"]` | `household` |
| 7 | `beta_E_drgn6` | `reg6` | `["working"]` | `household` |
| 8 | `beta_E_drgn7` | `reg7` | `["working"]` | `household` |
| 9 | `beta_E_drgn8` | `reg8` | `["working"]` | `household` |

The `beta_E_educH` and `beta_E_gsur` entries have no explicit `applies_to:` field — this is consistent with M0c_b2_GSURv2, where neither entry carried `applies_to`. The parser applies these to both singles and couples, the same behaviour as in M0c_b2_GSURv2. The region dummies (entries 3–9) carry `applies_to: "household"`, matching M1-clean.

---

## 4. Diff summary vs M1-clean

The YAML header declares five changes relative to M1-clean. All five verified by literal file inspection:

| # | Change | Verified |
|---|---|---|
| 1 | `specification.name`: `"ruro_occ_M1_clean"` → `"ruro_occ_M1_naive"` | **Confirmed** |
| 2 | `specification.description`: updated to robustness/sensitivity purpose | **Confirmed** |
| 3 | `market_opportunity.shifters`: `beta_E_educH` entry added (after `beta_E_gsur`, before `beta_E_drgn2`) | **Confirmed** |
| 4 | `initial_values`: `beta_E_educH: 0.0` added (after `beta_E_gsur`, before `beta_E_drgn2`) | **Confirmed** |
| 5 | `optimization.bounds`: `beta_E_educH: [-10.0, 10.0]` added (after `beta_E_gsur`, before `beta_E_drgn2`) | **Confirmed** |

No other field differs from M1-clean. All frozen blocks (utility, hours_opportunity, wage_opportunity, occupation_opportunity, couples, solver settings, expression_constraints, gradient_verification) are byte-identical to M1-clean.

---

## 5. Overall verdict

**PASS**

All 18 static checks pass. The YAML is internally consistent, the parameter count is correct (54 = M1-clean 53 + 1), and the diff relative to M1-clean is exactly as declared. No unintended structural divergence from M1-clean was detected in any frozen block.

The specification is cleared for estimation (Gate-B).