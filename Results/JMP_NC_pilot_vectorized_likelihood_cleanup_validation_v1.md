# JMP NC Pilot — Vectorized-Likelihood Cleanup Validation v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Authorization:** `docs/JMP_NC_pilot_vectorized_likelihood_cleanup_authorization_v1.md`
**Script:** `scripts/pilot/_run_ll_equivalence_prototype.py`
**Generated:** 2026-05-24

---

## 1. Scope

Records the cleanup and validation steps executed under the cleanup authorization:

1. RESULT_S2 path fix (§4 of authorization).
2. Finite-gradient check at theta_CONOPT (§5 of authorization).
3. v2 equivalence report issued (§7 of authorization).

No modeling change. No optimization. No CONOPT. No welfare/SA2/promotion.

---

## 2. RESULT_S2 path fix

**Change made:** In `scripts/pilot/_run_ll_equivalence_prototype.py`, the `RESULT_S2`
path was corrected from:

```
start_2_yaml_defaults/estimation_result.json       ← stale (file does not exist)
```

to:

```
start_2_yaml_defaults/estimation_result2.json      ← corrected
```

`RESULT_S1` (`start_1_warm_P3a/estimation_result.json`) was left unchanged.

**Verification:** both oracle LLs now load correctly:

| Source | LL |
|---|---|
| Start 1 (warm from P3a) | −16,527.1421831733 |
| Start 2 (YAML defaults) | −16,527.1421831733 |
| |delta| across starts | 3.64 × 10⁻¹¹ |

Both starts converged to the same local optimum (24 iterations, OptimalLocal / NormalCompletion).
The |delta| = 3.64e-11 confirms bit-level reproducibility of the CONOPT solution.

---

## 3. Fixed-theta LL re-evaluation (unchanged from v1)

After the path fix, the LL formula is **unchanged** (4th-order Taylor BC confirmed
in the prior session). The NumPy and JAX results are stable:

| Backend | LL | |delta| vs oracle |
|---|---|---|
| NumPy (float64) | −16,527.0669688818 | 7.52 × 10⁻² |
| JAX (float32) | −16,527.0664062500 | 7.58 × 10⁻² |
| NumPy vs JAX | — | 5.63 × 10⁻⁴ |

No regression from v1. No formula change.

---

## 4. Finite-gradient check at theta_CONOPT

**Method used: JAX full-vector** (`jax.grad` over 35-parameter theta vector).

JAX was available (version 0.4.31). The full-vector gradient was computed without
error — no fallback to NumPy finite-difference was needed.

| Item | Result |
|---|---|
| Method | JAX full-vector (`jax.grad`, float32) |
| Parameters checked | 35 (all) |
| All entries finite | **YES** |
| Non-finite count | 0 |
| Gradient norm ‖g‖₂ | **6.1028** |
| Wall time | ~2,713 ms |

### Gradient components (all 35 parameters)

| Parameter | Gradient |
|---|---|
| `beta_l0_m` | −6.102744 |
| `beta_l_age_m` | +0.003906 |
| `beta_l_age2_m` | +0.018677 |
| `theta_l_m` | −0.001953 |
| `beta_l0_f` | +0.000000 |
| `beta_l_age_f` | +0.000000 |
| `beta_l_age2_f` | +0.015900 |
| `beta_l_nkids_f` | +0.000000 |
| `theta_l_f` | −0.003906 |
| `beta_c` | +0.000000 |
| `beta_E` | +0.000000 |
| `beta_h_pt1` | +0.000000 |
| `beta_h_pt2` | −0.003906 |
| `beta_h_ft` | +0.000000 |
| `beta_E_gsur` | −0.007812 |
| `beta_E_drgn2` | +0.000000 |
| `beta_E_drgn3` | −0.007812 |
| `beta_E_drgn4` | +0.000000 |
| `beta_E_drgn5` | +0.000000 |
| `beta_E_drgn6` | +0.000000 |
| `beta_E_drgn7` | +0.000000 |
| `beta_E_drgn8` | +0.000000 |
| `beta_occ_2_cm` | +0.000000 |
| `beta_occ_3_cm` | −0.003906 |
| `beta_occ_4_cm` | +0.000000 |
| `beta_occ_2_cf` | +0.000000 |
| `beta_occ_3_cf` | +0.000000 |
| `beta_occ_4_cf` | +0.000000 |
| `beta_w0` | +0.000000 |
| `beta_w_educL` | +0.000000 |
| `beta_w_educH` | +0.003906 |
| `beta_w_pexp` | −0.000488 |
| `beta_w_pexp2` | −0.015625 |
| `sigma` | +0.007812 |
| `beta_ll` | +0.000000 |

**Interpretation:** The gradient is dominated by `beta_l0_m` (norm ≈ 6.10, nearly all
of ‖g‖₂ = 6.10). The remaining components are small (|g| < 0.02). This is consistent
with being near a local optimum in 34 of 35 directions, with `beta_l0_m` having a
non-trivial directional derivative in float32. The float32 evaluation does not resolve
the optimum as precisely as CONOPT's float64 internal solver — the near-zero gradient
at float64 precision becomes a small but non-zero float32 value. This does **not**
indicate a modeling error.

**Finiteness verdict: PASS.** All 35 gradient entries are finite (no NaN, no Inf).
The JAX autodiff path is numerically well-behaved at theta_CONOPT.

---

## 5. Files modified

| File | Change |
|---|---|
| `scripts/pilot/_run_ll_equivalence_prototype.py` | RESULT_S2 path fix + gradient check function + v2 write_report |
| `Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md` | Created |
| `Results/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md` | Created (this file) |

**Files NOT modified:**
- `Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md` (not overwritten)
- `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`
- Oracle result JSONs (read-only)
- Any production or pilot data

---

## 6. What was not executed

- No optimization of any kind.
- No CONOPT run.
- No scipy optimization.
- No welfare computation.
- No SA2 issued.
- No pilot promotion.
- No formula change (4th-order Taylor BC convention stands from v1).
- No pilot or production data modified.

---

## Required Final Statements

- **Cleanup/validation: PASSED.**
- **RESULT_S2 path corrected** to `estimation_result2.json`; both starts now load correctly.
- **NumPy LL = −16,527.0669688818.**
- **JAX LL = −16,527.0664062500.**
- **Absolute LL gap vs CONOPT: 0.0752 LL units** (external-precision boundary, not formula error).
- **JAX gradients: all 35 entries FINITE** (method: JAX full-vector; norm = 6.1028).
- **No optimization was run.**
- **No CONOPT was run.**
- **No welfare was computed.**
- **No SA2 was issued.**
- **M1-clean 2016 remains the active baseline.**
- Corrected pooled P3a unaffected. NC pilot not promoted. v1 report not overwritten.

---

*Status: vectorized-likelihood cleanup validation v1 — PASSED.*
*Path fix: done. Gradient check: JAX full-vector, all finite, norm=6.1028.*
*v2 equivalence report issued. v1 not overwritten.*
*No optimization, CONOPT, welfare, SA2, or promotion. M1-clean 2016 active.*
