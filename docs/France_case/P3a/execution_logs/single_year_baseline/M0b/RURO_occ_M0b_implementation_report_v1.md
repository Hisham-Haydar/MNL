# RURO `ruro_occ_M0b` — Implementation Report v1

Date: 2026-05-14
Scope: implementation of M0b1 and M0b2 specification files and the targeted
post-estimation reporter patch. No estimation was run. No parser or likelihood
engine was changed. `ruro_occ_M0a_clean` is untouched.

---

## 1. Files changed

| file | action | purpose |
|---|---|---|
| `scripts/enhanced/estimation_spec_ruro_occ_M0b1.yaml` | **CREATED** | M0b1 spec (M0a-clean + `beta_ll`) |
| `scripts/enhanced/estimation_spec_ruro_occ_M0b2.yaml` | **CREATED** | M0b2 spec (M0b1 + `theta_c` upper bound 0.0) |
| `scripts/enhanced/RURO_post_estimation_styled.py` | **PATCHED** | add `beta_ll * BC(L_m) * BC(L_f)` to couples V in `_add_predicted_probabilities` |

Files confirmed unchanged:

| file | status |
|---|---|
| `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` | untouched |
| `scripts/enhanced/estimation_spec_parser.py` | untouched |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | untouched |
| `scripts/enhanced/estimation_engine.py` | untouched |
| `scripts/enhanced/gamspy_estimation.py` | untouched |

---

## 2. Exact YAML differences for M0b1

All other sections are byte-identical to `estimation_spec_ruro_occ_M0a_clean.yaml`.

### 2.1 `specification.name`

```yaml
# M0a-clean
name: "ruro_occ_M0a_clean"

# M0b1
name: "ruro_occ_M0b1"
```

### 2.2 `specification.description`

```yaml
# M0a-clean
description: "M0a-clean: singles consumption Box-Cox curvature pooled into a
  single theta_c_singles parameter ..."

# M0b1
description: "M0b1: adds beta_ll * BC(L_m, theta_l_m) * BC(L_f, theta_l_f)
  leisure-leisure interaction to couples utility (Capeau et al. 2015/16 eq. 2).
  All other blocks identical to M0a-clean."
```

### 2.3 `couples` block

```yaml
# M0a-clean
couples: {}

# M0b1
couples:
  leisure_interaction:
    coefficient: "beta_ll"
```

### 2.4 `initial_values` — addition

```yaml
# M0b1 adds at the end of the block
beta_ll: 0.0
```

### 2.5 `optimization.bounds` — addition

```yaml
# M0b1 adds at the end of the bounds block
beta_ll: [-2.0, 2.0]
```

---

## 3. Exact YAML differences for M0b2

M0b2 is identical to M0b1 except for the two changes below.

### 3.1 `specification.name`

```yaml
# M0b1
name: "ruro_occ_M0b1"

# M0b2
name: "ruro_occ_M0b2"
```

### 3.2 `optimization.bounds.theta_c`

```yaml
# M0b1
theta_c: [-8.0, 0.95]        # couples shared (unchanged from M0a-clean)

# M0b2
theta_c: [-8.0, 0.0]         # CHANGED: tightened upper bound to 0.0
```

All other bounds, initial values, and blocks are byte-identical between M0b1
and M0b2.

---

## 4. Post-estimation reporter patch

File: `scripts/enhanced/RURO_post_estimation_styled.py`
Function: `_add_predicted_probabilities`
Location: couples branch, after the two consumption-leisure cross terms and
before the opportunity layer.

### Insertion point (context)

```python
        V += beta_cl_m * c_bc * l_bc_m
        V += beta_cl_f * c_bc * l_bc_f

        # [INSERTED BLOCK — see below]

        opp_added = False
        for col in ['log_opp_male', 'log_opp_female', 'log_opp']:
```

### Inserted block

```python
        # Leisure-leisure interaction (M0b+): beta_ll * BC(L_m) * BC(L_f).
        # Zero contribution for M0a-clean (couples_interaction_coef is None).
        if spec is not None and hasattr(spec, 'couples_interaction_coef') \
                and spec.couples_interaction_coef \
                and spec.couples_interaction_coef in params:
            beta_ll = params[spec.couples_interaction_coef]
            V += beta_ll * l_bc_m * l_bc_f
```

`l_bc_m` and `l_bc_f` are already computed at that point (the existing lines
`l_bc_m = boxcox_transform(l_m, theta_l_m)` and `l_bc_f = boxcox_transform(l_f, theta_l_f)`
appear a few lines above). No new variables are required.

**Backward compatibility**: for M0a-clean, `spec.couples_interaction_coef is None`,
so the inserted block is skipped entirely. The M0a-clean post-estimation
output is identical to before this patch.

---

## 5. Parser and likelihood engine — unchanged

**Parser (`estimation_spec_parser.py`)**: not modified. The implementation
audit confirmed that the parser already declares
`couples_interaction_coef: Optional[str]` on `EstimationSpec` (line 72),
already reads `couples.leisure_interaction.coefficient` from the YAML (lines
479-484), and already appends the coefficient name to `_build_parameter_list`
(line 1416). No parser change was needed or made.

**Vectorized likelihood engine (`gamspy_estimation_vectorized.py`)**: not
modified. The audit confirmed that `_build_couples_ll_vectorized` already
contains (lines 803-808):

```python
u_interact = 0.0
if spec.couples_interaction_coef and spec.couples_interaction_coef in param_vars:
    u_interact = param_vars[spec.couples_interaction_coef] * bc_l_m * bc_l_f

utility = u_consumption + u_leisure_m + u_leisure_f + u_consumption_leisure + u_interact
```

This is exactly the `beta_ll * BC(L_m, theta_l_m) * BC(L_f, theta_l_f)` term
specified in the design memo §5. No engine change was needed or made.

**Non-vectorized engines (`estimation_engine.py`, `gamspy_estimation.py`)**:
not modified. As documented in the implementation audit §13, these engines are
not used by the `--vectorized` estimation path. They do not include the
`beta_ll` interaction term; this is a known gap for any future non-vectorized
run on M0b results. Flag in the M0b1 post-estimation report when writing.

---

## 6. Opportunity blocks — unchanged

All four opportunity blocks are byte-identical across M0a-clean, M0b1, and M0b2:

| block | YAML section | status |
|---|---|---|
| Employment + hours focal points | `hours_opportunity` | byte-identical |
| Market opportunity residual | `market_opportunity` | byte-identical |
| Wage opportunity (lognormal) | `wage_opportunity` | byte-identical |
| Occupation opportunity (loc4) | `occupation_opportunity` | byte-identical |

The `proposal-density correction` (`expression_constraints`, and all
`-log(prior)` code paths in the engines) is untouched. The two soft constraints
(`mul_cou_m_positive`, `mul_cou_f_positive`) are carried forward unchanged.

---

## 7. Prior/proposal correction — unchanged

The `expression_constraints` block in both M0b1 and M0b2 is byte-identical to
M0a-clean: `enabled: true`, `default_mode: soft`, `default_weight: 1000.0`,
same two `mul_cou_*_positive` constraints, no additions.

The `-log(prior)` subtraction in the likelihood engines was not touched. The
`log_prior` / `prior` column read in `_add_predicted_probabilities` (lines
2981-2985) was not touched.

---

## 8. Parameter count

| spec | params | derivation |
|---|---|---|
| `ruro_occ_M0a_clean` | 47 | baseline |
| `ruro_occ_M0b1` | **48** | 47 + `beta_ll` |
| `ruro_occ_M0b2` | **48** | same as M0b1 (bound tightening adds no params) |

Verified by `len(spec.all_param_names)` from `parse_specification` (Gate A
parse run, 2026-05-14). `beta_ll` is appended last in `all_param_names` for
both M0b specs, consistent with `_build_parameter_list` appending
`couples_interaction_coef` at the end of the ordered list (parser line 1416).

---

## 9. `compute_marginal_utilities_at_chosen` — not yet patched

`compute_marginal_utilities_at_chosen` (line 5062 of
`RURO_post_estimation_styled.py`) does not accept `spec` and calls
`compute_beta_l_full(df_g, params, suffix='')` without the spec argument
(line 5151). It has no provision for the leisure-leisure interaction.

For M0b1/M0b2 the correct couples marginal utilities are:

```
MUL_m = (beta_l_m(Z_m) + beta_ll * BC(L_f, theta_l_f)) * L_m^(theta_l_m - 1)
MUL_f = (beta_l_f(Z_f) + beta_ll * BC(L_m, theta_l_m)) * L_f^(theta_l_f - 1)
```

The current implementation omits the `beta_ll * BC(L_f)` / `beta_ll * BC(L_m)`
cross-terms. The marginal-utility diagnostics panel in the M0b1 LLM summary
will therefore report stale MUL values for couples. This must be flagged
explicitly in the M0b post-estimation report. A future patch should add a
`spec` argument to `compute_marginal_utilities_at_chosen` and extend the
couples MUL calculation accordingly.

---

## 10. How to run smoke tests

### Gate A (parse + static check) — already run, all pass

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\Results\RURO_occ_M0b_gate_A_parse_report_v1.py"
```

See `Results/P3a/single_year_baseline/M0b/RURO_occ_M0b_gate_A_parse_report_v1.md` for full output.

### M0b1 estimation (when ready)

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py" `
    --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
    --group joint `
    --solver gamspy-conopt `
    --vectorized `
    --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0b1.yaml" `
    --warm-start none `
    --auto-timestamp `
    --verbose
```

`--warm-start none` is mandatory (design memo §7). Run from at least three
start points: spec defaults, spec defaults + Gaussian perturbation
(sigma = 0.1 * bound-width), and random uniform within bounds.

### M0b2 estimation (if M0b1 fails couples-fit gates)

Same invocation with `estimation_spec_ruro_occ_M0b2.yaml`.

### Post-estimation fit check (after estimation)

Adapt `Results/_M0a_clean_post_est_fit_check.py` to point at the M0b1 run
directory and spec file. Save as `Results/_M0b1_post_est_fit_check.py`.
The V cross-check against the structural participation diagnostic
(`Results/_participation_diag_ruro_occ_M0b1.py`, to be created) must hold
within 1e-14 on the 100-household sample.
