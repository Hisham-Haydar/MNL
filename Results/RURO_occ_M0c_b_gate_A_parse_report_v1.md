# RURO `ruro_occ_M0c_b` — Gate-A Parse Report v1

Date: 2026-05-14
Spec file: `scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml`
Parser: `scripts/enhanced/estimation_spec_parser.py`
Test script: `C:\Users\hisham\AppData\Local\Temp\gate_a_test.py`

---

## Summary

**All 9 Gate-A checks PASS.** The spec parses cleanly, `theta_c` is absent from the
parameter vector, `theta_c_singles` is present, `beta_ll` has the correct widened bound,
and the parameter count is 47 (M0b2 minus one).

---

## 1. Spec name and description

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `spec.name` | `ruro_occ_M0c_b` | `ruro_occ_M0c_b` | **PASS** |
| Description string | contains `theta_c fixed` | present | **PASS** |

---

## 2. Parameter count

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `len(spec.all_param_names)` | 47 (M0b2 − 1) | **47** | **PASS** |

---

## 3. `theta_c` absent from parameter vector

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `'theta_c' in spec.all_param_names` | `False` | `False` | **PASS** |
| `spec.bounds.get('theta_c')` | `None` | `None` | **PASS** |
| `spec.initial_values.get('theta_c')` | absent | `NOT IN INITIAL VALUES` | **PASS** |

---

## 4. `utility_consumption_theta_couples_fixed` set correctly

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `spec.utility_consumption_theta_couples_fixed` | `0.0` (float) | `0.0` | **PASS** |

---

## 5. `theta_c_singles` present (singles routing preserved)

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `'theta_c_singles' in spec.all_param_names` | `True` | `True` | **PASS** |
| `spec.utility_consumption_theta_singles_shared` | `'theta_c_singles'` | `'theta_c_singles'` | **PASS** |

---

## 6. `beta_ll` bound widened

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `spec.bounds.get('beta_ll')` | `(0.0, 10.0)` | `(0.0, 10.0)` | **PASS** |
| `spec.initial_values.get('beta_ll')` | `2.0` | `2.0` | **PASS** |

---

## 7. `beta_ll` in parameter vector

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `'beta_ll' in spec.all_param_names` | `True` | `True` | **PASS** |

---

## 8. Parser log messages

The following INFO messages confirm correct activation of both new mechanisms:

```
INFO Singles theta_c POOLED: singles_male and singles_female share 'theta_c_singles'.
INFO Couples theta_c FIXED: couples consumption BC exponent = 0 (not estimated; theta_c removed from parameter vector).
INFO Total parameters: 47
```

---

## 8b. Fixed-theta expression-constraint smoke check

The unchanged couples MUL positivity constraints were evaluated with
`theta_c` absent from the parameter vector and
`utility_consumption_theta_couples_fixed = 0.0`.

| constraint | group | result |
|---|---|---|
| `mul_cou_m_positive` | `couples_male` | PASS |
| `mul_cou_f_positive` | `couples_female` | PASS |

This confirms that the constraint evaluator now uses the fixed couples theta
constant instead of requiring an estimated `theta_c` symbol.

---

## 9. Full parameter list (47 parameters)

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
28  beta_E_educH
29  beta_occ_2_sm
30  beta_occ_3_sm
31  beta_occ_4_sm
32  beta_occ_2_sf
33  beta_occ_3_sf
34  beta_occ_4_sf
35  beta_occ_2_cm
36  beta_occ_3_cm
37  beta_occ_4_cm
38  beta_occ_2_cf
39  beta_occ_3_cf
40  beta_occ_4_cf
41  beta_w0
42  beta_w_educL
43  beta_w_educH
44  beta_w_pexp
45  beta_w_pexp2
46  sigma
47  beta_ll
```

Notable: `theta_c` (parameter 23 in M0b2's 48-parameter list) is absent. All 47
remaining parameters are present and in the expected order.

---

## Gate-A verdict

**PASS — ready for estimation.**

The implementation is complete. Gate-A confirms:
- Spec parses without errors.
- `theta_c` is absent from the estimated parameter vector (fixed at 0.0).
- `theta_c_singles` routing for singles is preserved.
- `beta_ll` bound is `[0.0, 10.0]` with initial value 2.0 (warm-start from M0b2 boundary).
- Parameter count is 47.

Estimation may proceed once the user authorises it. See
[docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b_implementation_report_v1.md](../docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b_implementation_report_v1.md)
for the estimation command and Gate-B criteria.
