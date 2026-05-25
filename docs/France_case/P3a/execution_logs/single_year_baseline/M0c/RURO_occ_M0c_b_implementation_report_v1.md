# RURO `ruro_occ_M0c_b` — Implementation Report v1

Date: 2026-05-14
Status: **IMPLEMENTATION COMPLETE — not yet estimated**

---

## 1. Motivation and design rationale

The M0b2 multi-start experiment ([Results/P3a/single_year_baseline/M0b/RURO_occ_M0b2_multistart_report_v1.md](../Results/P3a/single_year_baseline/M0b/RURO_occ_M0b2_multistart_report_v1.md)) established three findings that directly motivate M0c_b:

1. **`theta_c` = 0.0 is the unique attractor.** Every successful start from three diverse initial points (theta_c spanning −2.0 to −1.0) converged to theta_c = 0.0 at the upper bound. The boundary is not a local trap or an initialisation artefact.
2. **`beta_ll` = 2.0 is a genuinely binding upper bound.** Every successful start moved beta_ll from 0.0–1.648 toward 2.0. The data strongly prefer large positive leisure-leisure interaction; the current bound prevents identification of the true magnitude.
3. **The negative Hessian eigenvalue is structural.** It appears identically across all runs and reflects the corner geometry (two simultaneous bound hits) rather than a numerical accident.

M0c_b addresses both problems simultaneously:
- Fix `theta_c = 0.0` structurally (log-utility for couples consumption, not estimated). This removes one boundary degree of freedom and should eliminate the negative Hessian eigenvalue.
- Widen `beta_ll` to `[0.0, 10.0]`. This allows the leisure-leisure interaction to be identified in the interior of a much larger feasible region.

---

## 2. Specification changes relative to M0b2

| Field | M0b2 | M0c_b |
|---|---|---|
| `specification.name` | `ruro_occ_M0b2` | `ruro_occ_M0c_b` |
| `utility.consumption.couples_fixed_box_cox_exponent` | _(absent)_ | `0.0` |
| `theta_c` in estimated params | yes | **no** (fixed) |
| `theta_c` in `initial_values` | `−1.0` | _(absent)_ |
| `theta_c` in `optimization.bounds` | `[−8.0, 0.0]` | _(absent)_ |
| `beta_ll` bound | `[−2.0, 2.0]` | `[0.0, 10.0]` |
| `beta_ll` initial value | `0.0` | `2.0` |
| Parameter count | 48 | **47** |

All other blocks (hours opportunity, wage opportunity, market opportunity, occupation opportunity, expression constraints, gradient verification) are byte-identical to M0b2.

---

## 3. New YAML key: `utility.consumption.couples_fixed_box_cox_exponent`

The implementation uses a new generic spec key rather than a M0c_b-specific hard-code. The key lives under `utility.consumption`:

```yaml
utility:
  consumption:
    coefficient: "beta_c"
    box_cox_exponent: "theta_c"                   # still used for singles routing
    singles_box_cox_exponent: "theta_c_singles"   # singles shared (M0a-clean)
    couples_fixed_box_cox_exponent: 0.0           # M0c_b: theta_c FIXED, not estimated
```

**Semantics:** when `couples_fixed_box_cox_exponent` is present, `theta_c` is treated as a compile-time constant for all couples-group computations. It is excluded from `all_param_names`, from `initial_values`, and from `optimization.bounds`. The `box_cox_exponent: "theta_c"` key is retained to preserve the singles-routing logic (singles still use `theta_c_singles` via `singles_box_cox_exponent`).

**Mutual exclusivity:** `couples_fixed_box_cox_exponent` and `pool_across_groups` are mutually exclusive; the parser raises `ValueError` if both are set.

---

## 4. Parser changes (`estimation_spec_parser.py`)

### 4a. `EstimationSpec` dataclass — new field (line ~98)

```python
# Fixed (non-estimated) couples consumption Box-Cox exponent (M0c-b).
# When set to a float, this value is used as a compile-time constant for
# the couples BC-C transform; theta_c is NOT added to all_param_names.
# Singles are unaffected (they still use utility_consumption_theta_singles_shared).
# YAML key: utility.consumption.couples_fixed_box_cox_exponent
utility_consumption_theta_couples_fixed: Optional[float] = None
```

### 4b. `parse_specification` — parse logic (after `singles_box_cox_exponent` block)

Reads `couples_fixed_box_cox_exponent` from YAML, casts to `float`, raises on bad values, enforces mutual exclusivity with `pool_across_groups`, logs the fixed value.

### 4c. `_build_parameter_list` — guard at the `theta_c` append site (line ~1373)

```python
# Skip theta_c when couples_fixed_theta is set — it's a compile-time constant.
if utility_form == "box_cox" and utility_consumption_theta and couples_fixed_theta is None:
    params.append(utility_consumption_theta)  # theta_c
```

New `couples_fixed_theta: Optional[float] = None` parameter added to the function signature.

### 4d. `EstimationSpec(...)` constructor call — new kwarg

```python
utility_consumption_theta_couples_fixed=utility_consumption_theta_couples_fixed,
```

### 4e. `_build_parameter_list(...)` call site — new kwarg

```python
couples_fixed_theta=utility_consumption_theta_couples_fixed,
```

---

## 5. Engine changes (`gamspy_estimation_vectorized.py`)

In `_build_couples_ll_vectorized`, the couples BC-C path (around line 714) now has a priority branch for the fixed-theta case:

```python
_couples_fixed_theta = getattr(spec, "utility_consumption_theta_couples_fixed", None)
if _couples_fixed_theta is not None:
    # M0c-b: theta_c is structurally fixed — use compile-time constant, no param lookup.
    bc_c = box_cox_transform(consumption_param, float(_couples_fixed_theta))
elif spec.utility_consumption_theta:
    # existing estimated-theta path (unchanged)
    ...
else:
    bc_c = gp_log(consumption_param + LOG_EPS)
```

The singles path (lines 381–390 in `_build_singles_ll_vectorized`) is **unaffected** — singles still use `theta_c_singles` via the `theta_c_param_name` helper.

---

## 6. Post-estimator changes (`RURO_post_estimation_styled.py`)

In `_add_predicted_probabilities`, the theta_c fallback for couples (around line 2904) is patched to return the fixed constant when applicable:

```python
if theta_c is None:
    _fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None) if spec is not None else None
    if _fixed is not None and group_suffix not in ('_sm', '_sf'):
        theta_c = float(_fixed)
    else:
        theta_c = params.get(f'theta_c{group_suffix}', params.get('theta_c', 0.5))
```

This prevents the fallback from returning `0.5` (the generic default) for couples when `theta_c` is absent from the results because it was never estimated.

---

## 7. Files created / modified

| File | Action | Description |
|---|---|---|
| `scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml` | **Created** | M0c_b specification (47 params) |
| `scripts/enhanced/estimation_spec_parser.py` | **Modified** | New field, parse logic, `_build_parameter_list` guard, constructor/call-site kwargs |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | **Modified** | Couples BC-C priority branch for fixed theta |
| `scripts/enhanced/expression_constraints.py` | **Modified** | MUL/MUC constraint evaluator uses fixed couples theta when `theta_c` is not estimated |
| `scripts/enhanced/estimation_engine.py` | **Modified** | Couples utility and gradient functions use fixed theta constant; theta_c gradient term suppressed |
| `scripts/enhanced/RURO_post_estimation_styled.py` | **Modified** | Couples theta_c fallback uses fixed constant |
| `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b_implementation_report_v1.md` | **Created** | This document |
| `Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b_gate_A_parse_report_v1.md` | **Created** | Gate-A parse verification |

---

## 8. What is NOT changed

- **No changes to the singles path** in the engine or parser. Singles still use `theta_c_singles` (M0a-clean shared exponent).
- **No changes to the numpy gradient estimator** (`estimation_engine.py`). The fixed-theta mechanism is specific to the GAMSPy vectorized engine used for production runs.
- **No changes to opportunity blocks** (hours, wage, market, occupation). All blocks are identical to M0b2.
- **No changes to the YAML expression constraints**. The MUL positivity
  constraints for couples_male and couples_female are retained unchanged.
  The constraint evaluator was patched so those unchanged constraints use the
  fixed couples theta constant instead of looking for an estimated `theta_c`
  parameter.
- **No welfare computation.** This report documents the implementation only; welfare use requires Gate B to pass.

---

## 9. Identification hypothesis

The structural fix removes the binding `theta_c = 0.0` constraint from the optimisation problem. With `theta_c` no longer a free parameter, the log-likelihood surface is now a function of 47 parameters. The expected effects at the M0c_b solution relative to M0b2:

| Diagnostic | M0b2 observed | M0c_b expected |
|---|---|---|
| Bound hits | 2 (`theta_c`, `beta_ll`) | 0 or 1 (`beta_ll` if [0,10] is still too narrow) |
| Negative Hessian eigenvalues | 1 | 0 (hypothesis: structural corner removed) |
| NA standard errors | 5 | ≤ 2 (hypothesis: `theta_c_singles`/`beta_c_sm`/`beta_c_sf` cluster may persist) |
| Negative VarCov variances | 3 | 0 (hypothesis: follows from eigenvalue resolution) |
| `beta_ll` final | 2.0 (bound) | Interior in [0, 10] |

If `beta_ll` still hits 10.0, the bound must be widened further (M0c_b2: [0, 20]) or the negative eigenvalue returns for a different reason.

---

## 10. Gate B criteria

M0c_b must satisfy all five criteria before welfare use is authorised:

| Criterion | Pass condition |
|---|---|
| Condition number | κ < 10⁷ |
| Negative Hessian eigenvalues | 0 |
| NA standard errors | 0 |
| Parameters at strict bounds | 0 |
| Negative VarCov variances | 0 |

---

## 11. Estimation command

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py" `
    --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy" `
    --group joint --solver gamspy-conopt --vectorized `
    --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml" `
    --warm-start "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0b2/run_2026-05-14_12-46-04/estimation_results.json" `
    --auto-timestamp --verbose
```

Use the M0b2 warm start for the first production attempt because M0c_b is a
structural reparameterisation of the M0b2 boundary solution.
