# JMP NC Pilot — Vectorized-Likelihood Cleanup Authorization v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: cleanup/validation authorization, narrow.** Authorizes only
cleanup and validation of the fixed-theta vectorized-likelihood prototype: fix
the stale start-2 path, add a finite-gradient check at `theta_CONOPT`, and
re-issue the report in the requested structure as a **qualified PASS**. It does
**not** authorize optimization, a new optimum, welfare, SA2, or promotion.
M1-clean 2016 remains active; corrected pooled P3a unaffected.

---

## 1. Purpose

To finalize the LL-equivalence prototype as a clean, correctly-sourced,
gradient-validated **qualified PASS**, fixing two defects found on review: a
stale start-2 result path, and the absence of a finite-gradient check (needed
before any later optimization could be trusted). No modeling change; the LL
formula stands.

---

## 2. Current equivalence status

The fixed-theta prototype reproduced the GAMSPy/CONOPT formula:

- Initial gap **20.9 LL units**, root-caused to the **Box-Cox convention**:
  GAMSPy `box_cox_transform` uses a **4th-order Taylor** expansion of
  `(exp(θ·log x)−1)/θ` around θ=0, not the exact exponential formula.
- After matching: **NumPy LL = −16,527.0670**, **JAX LL = −16,527.0664**,
  oracle **−16,527.1422**; |Δ| vs oracle **≈ 0.075**; NumPy-vs-JAX **≈ 5.63e-4**.
- All conventions verified (prior correction, market centering, gender-specific
  GSUR, region, hours, wage log-normal, loc4, EPS, log-sum-exp).
- No optimization, CONOPT, welfare, SA2, or promotion run.

---

## 3. Why this is a qualified pass

**Qualified PASS for formula equivalence — not exact identity.** The vectorized
NumPy/JAX likelihood implements the *same formula* as GAMSPy (the bisection
isolated the only material discrepancy to the Box-Cox convention, now matched),
and NumPy and JAX agree to 5.63e-4. The residual **0.075 LL gap vs the oracle is
acceptable as formula equivalence but is explicitly not an exact-identity pass**:
it is a precision-boundary artifact of evaluating a CONOPT optimum externally —
the reported theta is CONOPT's converged iterate rounded to 16 digits (internal
tolerance ~1e-8), and float64 accumulation over 2.3M rows differs from GAMS's
symbolic evaluation. Closing it fully would require re-running CONOPT, which is
out of scope. **The qualification must be stated plainly in the report**: same
formula, ~0.075 external-precision gap, not bit-identity.

---

## 4. Required cleanup items

1. **Fix the stale start-2 path (RESULT_S2).** The script currently sets
   `RESULT_S2` to
   `Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_2_yaml_defaults/estimation_result.json`
   — wrong filename. The actual start-2 file is **`estimation_result2.json`** in
   that directory. Correct `RESULT_S2` to point to
   `.../start_2_yaml_defaults/estimation_result2.json`. (The start-2 cross-check
   was reading a non-existent/wrong file; the fix makes the start-2 oracle LL
   −16,527.142183173302 load correctly.)
2. **Confirm start-1 path unaffected** (`.../start_1_warm_P3a/estimation_result.json`
   is correct — leave it).
3. No other logic change to the LL itself.

---

## 5. Required finite-gradient validation

The prototype only evaluated LL; before any future optimization is trusted, the
gradient must be finite at `theta_CONOPT`.

- **If JAX is available:** compute the gradient of the fixed-theta LL w.r.t. the
  full 35-parameter theta vector at `theta_CONOPT` (e.g. `jax.grad`), and verify
  **all 35 entries are finite** (no NaN/inf). Report the gradient norm and any
  non-finite entries.
- **If the full JAX gradient fails** (memory, dtype, or JAX unavailable): **halt
  that check cleanly** (do not force it) and perform **NumPy finite-difference
  spot checks** on these parameters: **`beta_c`, `beta_E`, `beta_E_gsur`,
  `beta_occ_2_cm`, `sigma`**. Report each finite-difference derivative and
  confirm finiteness.
- This is a **gradient-finiteness** check, not an optimization step — no
  parameter is updated, no optimum is sought.

---

## 6. Required start-path correction

After fixing RESULT_S2 (§4), the script must load **both** oracle results
correctly: start-1 LL −16,527.14218317334 and start-2 LL −16,527.142183173302,
and report both. The equivalence comparison uses the start-1 theta as the
primary `theta_CONOPT` (as before); start-2 is the cross-check. The report must
show both oracle LLs sourced from their correct files.

---

## 7. Required report-structure correction

Re-issue the equivalence report as **v2** in the requested structure (preserve
v1 unchanged). The v2 report must:

- preserve the **qualified PASS for formula equivalence** conclusion (§3) —
  explicitly *not* exact identity;
- state that the **0.075 LL gap is acceptable for formula equivalence but not an
  exact-identity pass**;
- carry the corrected start-2 sourcing and the finite-gradient result;
- retain the bisection root-cause (4th-order Taylor Box-Cox) and the convention
  inventory.

A separate cleanup-validation report records the path fix and the gradient
check.

---

## 8. What is authorized

- Fixing `RESULT_S2` to `estimation_result2.json` (§4).
- The finite-gradient check at `theta_CONOPT` (JAX full-vector, or NumPy
  finite-difference spot checks on the five named parameters) (§5).
- Re-issuing the equivalence report as **v2** (§7) and a cleanup-validation
  report.
- Updating `scripts/pilot/_run_ll_equivalence_prototype.py` for the path fix and
  the gradient check only.

---

## 9. What is not authorized

- **Optimization** or any new optimum search (gradient is checked for
  finiteness only, not used to step).
- Welfare; SA2; promotion; M1-clean displacement.
- Any change to the LL formula or its conventions (the formula stands as
  validated).
- Modifying pilot data, production data, or the CONOPT oracle results.
- Overwriting `Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md`.
- Full JAX optimization, denser product, pooled/singles, or P3a rebuild.

---

## 10. Required outputs

- Updated `scripts/pilot/_run_ll_equivalence_prototype.py` (RESULT_S2 fix +
  finite-gradient check).
- `Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md` (re-issued
  report, requested structure, qualified PASS; v1 **not** overwritten).
- `Results/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md` (records
  the path fix, the gradient check method actually used — JAX full-vector or
  NumPy spot checks — and the finiteness result).

---

## 11. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Cleanup + gradient-finiteness only; no
optimization; read-only on data and oracle results.

```text
Work locally in my RURO/MNL codebase. VECTORIZED-LIKELIHOOD CLEANUP + GRADIENT
VALIDATION, FR_2016 couples pilot. Authorized by
docs/JMP_NC_pilot_vectorized_likelihood_cleanup_authorization_v1.md.
Fixed-theta only. NO optimization, NO new optimum, NO welfare/SA2/promotion.

HARD CONSTRAINTS (halt and report if any would be violated):
- Read-only on the pkl, all data, and the CONOPT oracle result JSONs. No
  modeling/formula change.
- NO optimization or optimum search. Gradient is checked for FINITENESS ONLY;
  no parameter is updated.
- Do NOT overwrite Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md.
- Do NOT modify pilot data, production data, or the oracle results.

Read (read-only):
- docs/JMP_NC_pilot_vectorized_likelihood_cleanup_authorization_v1.md
- scripts/pilot/_run_ll_equivalence_prototype.py (to edit: RESULT_S2 + gradient)
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_2_yaml_defaults/estimation_result2.json
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl

STEP 1 — Fix RESULT_S2 path:
- In _run_ll_equivalence_prototype.py, change RESULT_S2 from
  ".../start_2_yaml_defaults/estimation_result.json" to
  ".../start_2_yaml_defaults/estimation_result2.json".
- Leave RESULT_S1 (start_1_warm_P3a/estimation_result.json) unchanged.
- Confirm both oracle LLs load: start_1 = -16527.14218317334,
  start_2 = -16527.142183173302.

STEP 2 — Re-run fixed-theta LL (no optimization) to confirm unchanged result:
- NumPy LL ~= -16527.0670, JAX LL ~= -16527.0664 (4th-order Taylor BC).
- |delta| vs oracle ~= 0.075; NumPy-vs-JAX ~= 5.6e-4. Report.

STEP 3 — Finite-gradient check at theta_CONOPT:
- If JAX available: g = jax.grad(LL)(theta_CONOPT) over all 35 params; verify
  ALL entries finite (no NaN/inf); report gradient norm + any non-finite.
- If full JAX gradient FAILS (memory/dtype) or JAX unavailable: HALT that check
  cleanly, then NumPy finite-difference spot checks on: beta_c, beta_E,
  beta_E_gsur, beta_occ_2_cm, sigma. Report each derivative + finiteness.
- Gradient is FINITENESS-ONLY; do NOT step / optimize.

STEP 4 — Write outputs (do NOT overwrite v1):
- Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md  (re-issued
  report; qualified PASS for FORMULA equivalence, explicitly NOT exact identity;
  state the 0.075 gap is acceptable as formula equivalence but not bit-identity;
  corrected start-2 sourcing; bisection root-cause = 4th-order Taylor BC;
  convention inventory; finite-gradient result).
- Results/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md  (records
  the RESULT_S2 fix, the gradient method used (JAX full-vector or NumPy spot),
  and finiteness outcome).
- Update scripts/pilot/_run_ll_equivalence_prototype.py (path fix + gradient).

THEN STOP. No optimization, no welfare, no SA2, no promotion.

End both reports with: qualified PASS (formula equivalence, not exact identity);
0.075 gap = external-precision boundary; gradient finite (method stated); no
optimization; no welfare/SA2/promotion; M1-clean 2016 active; corrected pooled
P3a unaffected; cleanup/validation only.
```

Save the reports as:
`Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md` and
`Results/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md`

---

## Required Final Statements

- **This authorizes only cleanup and validation of the fixed-theta vectorized
  likelihood prototype** — the RESULT_S2 path fix, a finite-gradient check at
  `theta_CONOPT`, and a re-issued report.
- **No optimization, no new optimum search, no welfare, no SA2, no promotion.**
- **RESULT_S2 is corrected** to `.../start_2_yaml_defaults/estimation_result2.json`.
- **Finite-gradient check at `theta_CONOPT`:** JAX full-vector if available;
  else clean halt of that check + NumPy finite-difference spot checks on
  `beta_c`, `beta_E`, `beta_E_gsur`, `beta_occ_2_cm`, `sigma`.
- **Conclusion preserved as a qualified PASS for formula equivalence — not exact
  identity;** the **0.075 LL gap is acceptable for formula equivalence but is
  not an exact-identity pass** (external-precision boundary of evaluating a
  CONOPT optimum).
- **v1 report not overwritten;** v2 + cleanup-validation reports written.
- **Pilot data, production data, and CONOPT oracle results unmodified.**
  M1-clean 2016 active; corrected pooled P3a unaffected.

---

*Status: vectorized-likelihood cleanup authorization v1. Authorizes the
RESULT_S2 fix, the finite-gradient check, and the v2/cleanup reports; no
optimization, welfare, SA2, or promotion. Qualified PASS for formula equivalence
stands. Next (separate gate): authorize JAX optimization from theta_CONOPT only
after the gradient is confirmed finite.*
