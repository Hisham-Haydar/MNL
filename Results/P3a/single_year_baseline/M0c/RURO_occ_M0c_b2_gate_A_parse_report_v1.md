# RURO `ruro_occ_M0c_b2` — Gate-A Parse Report v1

Date: 2026-05-15
Spec file: `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml`
Test script: `C:\Users\hisham\AppData\Local\Temp\gate_a_b2.py`

---

## Summary

**All 7 Gate-A checks PASS.** The spec parses cleanly. `theta_c` remains absent from the parameter vector (inherited from M0c_b). `beta_l0_m` bound is `(1e-6, 50.0)` and initial value is `0.01`. `beta_ll` bound is unchanged at `(0.0, 10.0)`. Parameter count is 47.

---

## Checks

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| `spec.name` | `ruro_occ_M0c_b2` | `ruro_occ_M0c_b2` | **PASS** |
| `len(spec.all_param_names)` | 47 | 47 | **PASS** |
| `'theta_c' not in params` | `False` | `False` | **PASS** |
| `spec.bounds['beta_l0_m']` | `(1e-6, 50.0)` | `(1e-6, 50.0)` | **PASS** |
| `spec.initial_values['beta_l0_m']` | `0.01` | `0.01` | **PASS** |
| `spec.utility_consumption_theta_couples_fixed` | `0.0` | `0.0` | **PASS** |
| `spec.bounds['beta_ll']` | `(0.0, 10.0)` | `(0.0, 10.0)` | **PASS** |

---

## Parser log (key lines)

```
INFO Specification: ruro_occ_M0c_b2
INFO Singles theta_c POOLED: singles_male and singles_female share 'theta_c_singles'.
INFO Couples theta_c FIXED: couples consumption BC exponent = 0 (not estimated; theta_c removed from parameter vector).
INFO Total parameters: 47
```

---

## Gate-A verdict

**PASS — ready for estimation.**
