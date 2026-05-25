# RURO `ruro_occ_M0b` — Implementation Audit v1

Date: 2026-05-14
Scope: pre-implementation audit for M0b1 and M0b2, based on inspection of
four source files: `estimation_spec_ruro_occ_M0a_clean.yaml`,
`estimation_spec_parser.py`, `gamspy_estimation_vectorized.py`, and
`RURO_post_estimation_styled.py`. No code changes in this document.

---

## 1. M0a-clean YAML state

`scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` has 47 estimable
parameters. The `couples` block at line 166 reads `couples: {}` — empty, no
`leisure_interaction` sub-key. The parser therefore sets
`spec.couples_interaction_coef = None` for M0a-clean.

Bounds: `theta_c: [-8.0, 0.95]` at line 251. `theta_c_singles: [-8.0, 0.95]`
at line 250.

Initial values: `beta_c: 1.0`, `theta_c: -1.0`, `theta_c_singles: -1.0`.
No `beta_ll` key.

The `expression_constraints` block retains two soft constraints
(`mul_cou_m_positive`, `mul_cou_f_positive`). These are carried forward
unchanged to M0b1 and M0b2 (design memo §11).

---

## 2. Parser current state

`scripts/enhanced/estimation_spec_parser.py`:

- `EstimationSpec` dataclass (line 72): field
  `couples_interaction_coef: Optional[str]` is **already declared**.
- Parse logic (lines 479-484): reads `couples.leisure_interaction.coefficient`
  from YAML; if absent leaves `couples_interaction_coef = None`. If the
  `couples` block is non-empty and contains `leisure_interaction.coefficient`,
  the value is stored verbatim (defaulting to `"beta_interact"` if the key
  exists but no value is given).
- `_build_parameter_list` (line 1416-1417): appends
  `couples_interaction_coef` at the end of the ordered parameter list when
  non-None.
- The parser is constructed in two places (lines 694 and 755); both pass
  `couples_interaction_coef=couples_interaction_coef`.

**Verdict: no parser changes required for M0b.** The field, parse logic, and
parameter-list entry all exist today. Adding
`couples: {leisure_interaction: {coefficient: "beta_ll"}}` to the YAML is
sufficient for the parser to expose `spec.couples_interaction_coef = "beta_ll"`
and include `beta_ll` in `spec.all_param_names`.

---

## 3. Vectorized engine current state

`scripts/enhanced/gamspy_estimation_vectorized.py`:

The couples log-likelihood builder `_build_couples_ll_vectorized` computes
(lines 803-808):

```python
# Interaction term (if specified)
u_interact = 0.0
if spec.couples_interaction_coef and spec.couples_interaction_coef in param_vars:
    u_interact = param_vars[spec.couples_interaction_coef] * bc_l_m * bc_l_f

utility = u_consumption + u_leisure_m + u_leisure_f + u_consumption_leisure + u_interact
```

`bc_l_m` and `bc_l_f` are already computed with partner-specific `theta_l_m`
and `theta_l_f` respectively. The expression matches the design memo §5
exactly: `beta_ll * BC(L_m, theta_l_m) * BC(L_f, theta_l_f)`.

The GAMSPy symbolic engine builds the expression graph automatically; the
gradient with respect to `beta_ll` is `BC(L_m) * BC(L_f)`, which CONOPT
differentiates without manual extension.

**Verdict: no vectorized engine changes required for M0b.** The interaction
term is already live; it evaluates to zero when `spec.couples_interaction_coef`
is None (the M0a-clean case), and activates immediately once the YAML is
updated.

---

## 4. Post-estimation reporter current state

`scripts/enhanced/RURO_post_estimation_styled.py`:

The patched `_add_predicted_probabilities` (around line 2881) builds couples V
as (lines 2919-2934):

```python
V += beta_l_m * l_bc_m
V += beta_l_f * l_bc_f
# consumption-leisure cross terms
V += beta_cl_m * c_bc * l_bc_m
V += beta_cl_f * c_bc * l_bc_f
# then opportunity layer...
```

**The `beta_ll * l_bc_m * l_bc_f` term is absent.** For M0a-clean this is
harmless (there is no `beta_ll`), but for M0b1/M0b2 the reporter will
underestimate V on working alternatives (specifically on alternatives where
both partners work, where both `l_bc_m` and `l_bc_f` are non-zero). The
magnitude of the omission is `beta_ll * BC(L_m) * BC(L_f)`; at typical working
alternatives with `theta_l approx -0.7`, `BC(L) approx -1.2`, so the
interaction contributes approximately `1.44 * beta_ll` per working alternative.
For `beta_ll = -1`, this is -1.44 nats, which shifts predicted probabilities
non-trivially.

`compute_marginal_utilities_at_chosen` (line 5062) does not accept `spec` and
calls `compute_beta_l_full(df_g, params, suffix='')` without spec (line 5151).
The docstring shows it is aware of the `beta_cl` consumption-leisure
interaction but has no provision for the `beta_ll` leisure-leisure interaction.
For couples, the correct MUL expressions under M0b are:

```
MUL_m = (beta_l_m(Z_m) + beta_ll * BC(L_f, theta_l_f)) * L_m^(theta_l_m - 1)
MUL_f = (beta_l_f(Z_f) + beta_ll * BC(L_m, theta_l_m)) * L_f^(theta_l_f - 1)
```

These are not currently implemented. The marginal-utility panel in the M0b LLM
summary will report stale MUL values for couples.

---

## 5. Required YAML changes

Two new files in `scripts/enhanced/`:

### `estimation_spec_ruro_occ_M0b1.yaml`

Copy `estimation_spec_ruro_occ_M0a_clean.yaml` and apply four targeted changes:

1. `specification.name: "ruro_occ_M0b1"`.
2. `specification.description`: update to mention the leisure-leisure
   interaction addition.
3. Replace `couples: {}` with:
   ```yaml
   couples:
     leisure_interaction:
       coefficient: "beta_ll"
   ```
4. In `initial_values`, add: `beta_ll: 0.0`.
5. In `optimization.bounds`, add: `beta_ll: [-2.0, 2.0]`.

All other sections are byte-identical to M0a-clean (opportunity blocks,
proposal-density correction, expression constraints, gradient settings).

### `estimation_spec_ruro_occ_M0b2.yaml`

Same as M0b1 with two further changes:

1. `specification.name: "ruro_occ_M0b2"`.
2. In `optimization.bounds`, change `theta_c: [-8.0, 0.95]` to
   `theta_c: [-8.0, 0.0]`.

---

## 6. Required parser changes

None. See §2.

---

## 7. Required vectorized engine changes

None. See §3.

---

## 8. Required post-estimation reporter changes

One targeted addition to `_add_predicted_probabilities` in
`scripts/enhanced/RURO_post_estimation_styled.py`.

In the `if is_couples:` branch, after `V += beta_cl_f * c_bc * l_bc_f` (line
2934) and before the opportunity-layer block, insert:

```python
# Leisure-leisure interaction (M0b+: zero when spec has no couples_interaction_coef)
if spec is not None and hasattr(spec, 'couples_interaction_coef') \
        and spec.couples_interaction_coef \
        and spec.couples_interaction_coef in params:
    beta_ll = params[spec.couples_interaction_coef]
    V += beta_ll * l_bc_m * l_bc_f
```

`l_bc_m` and `l_bc_f` are already computed at that point (lines 2922-2923);
no new variables are needed.

This change is backward-compatible: for M0a-clean `spec.couples_interaction_coef`
is None, so the block is skipped.

`compute_marginal_utilities_at_chosen` gains no corresponding update in this
patch. The omission must be flagged in the M0b patch report (matching the
precedent set by patch report v1 §7.2). MUL values for couples in the M0b LLM
summary will therefore omit the `beta_ll * BC(L_f)` / `beta_ll * BC(L_m)`
contributions to the leisure derivatives.

---

## 9. Required structural diagnostic changes

The structural participation diagnostic
`Results/_participation_diag_ruro_occ_M0a_clean.py` must be saved as a new
file `Results/_participation_diag_ruro_occ_M0b1.py` with one addition: after
the couples V is built, add the `beta_ll * BC(L_m) * BC(L_f)` term. This
preserves the reference diagnostic used for the 1e-14 cross-check
(`Results/_M0a_clean_post_est_fit_check.py` cross-check). The analogous M0b1
fit-check script should be `Results/_M0b1_post_est_fit_check.py`.

The cross-check must continue to hold within 1e-14 after the M0b post-est
patch is applied (§8 above) and the M0b1 diagnostic is updated.

---

## 10. Sign-convention note for beta_ll

Design memo §5 establishes this explicitly. With `theta_l < 0` (M0a-clean
estimates: `theta_l_m approx -0.71`, `theta_l_f approx -0.75`), `BC(L, theta_l)` is
negative when the partner works (`L < 1`) and zero at non-work (`L = 1`).
Therefore:

| state | BC(L_m) | BC(L_f) | product |
|---|---|---|---|
| both work | < 0 | < 0 | > 0 |
| one works | < 0 or 0 | 0 or < 0 | = 0 |
| both non-work | 0 | 0 | = 0 |

A **negative** `beta_ll` makes joint-working less attractive (the interaction
term is negative on both-working alternatives, zero elsewhere). This is the
sign needed to reduce the +91-nat couples U gap. A positive `beta_ll` would
make joint-working more attractive (leisure complements in the Capéau et al.
sense). The estimator is unconstrained over `[-2, 2]`; the sign must not be
imposed.

---

## 11. Analytical gradient

`optimization.analytical_gradient: true` is inherited from M0a-clean. The
GAMSPy symbolic engine constructs the expression graph, so the gradient of
`beta_ll * BC(L_m, theta_l_m) * BC(L_f, theta_l_f)` with respect to all
48 parameters is differentiated automatically:

- wrt `beta_ll`: `BC(L_m) * BC(L_f)`
- wrt `theta_l_m`: `beta_ll * BC(L_f) * d_BC(L_m)/d_theta_l_m`
- wrt `theta_l_f`: `beta_ll * BC(L_m) * d_BC(L_f)/d_theta_l_f`

No manual gradient extension is needed. If CONOPT reports gradient-norm issues
at initial values, the fallback documented in design memo §13(d) is to switch
`analytical_gradient: false` for M0b only; this is a documented allowed
deviation and must be noted in the patch report if triggered.

---

## 12. Parameter count verification

M0a-clean: 47 parameters (verified from YAML `initial_values` block: counts
26 singles/couples preference params + 4 hours + 2 market + 5 wage + 1 sigma
+ 12 occupation = 50... correction below).

Exact M0a-clean parameter count from the YAML `initial_values` block:

| block | params |
|---|---|
| singles male preferences | `beta_l0_sm`, `beta_l_age_sm`, `beta_l_age2_sm`, `beta_c_sm`, `theta_l_sm` = 5 |
| singles female preferences | `beta_l0_sf`, `beta_l_age_sf`, `beta_l_age2_sf`, `beta_l_nkids_sf`, `beta_c_sf`, `theta_l_sf` = 6 |
| singles shared curvature | `theta_c_singles` = 1 |
| couples male preferences | `beta_l0_m`, `beta_l_age_m`, `beta_l_age2_m`, `theta_l_m` = 4 |
| couples female preferences | `beta_l0_f`, `beta_l_age_f`, `beta_l_age2_f`, `beta_l_nkids_f`, `theta_l_f` = 5 |
| couples shared | `beta_c`, `theta_c` = 2 |
| hours opportunity | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft` = 4 |
| market opportunity | `beta_E_gsur`, `beta_E_educH` = 2 |
| wage opportunity | `beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` = 6 |
| occupation opportunity | `beta_occ_{2,3,4}_{sm,sf,cm,cf}` = 12 |
| **total** | **47** |

M0b1 and M0b2 add `beta_ll` = 1 parameter. Total: **48**. Matches design
memo §9.

---

## 13. Non-vectorized engines

`estimation_engine.py` (numpy gradient) and `gamspy_estimation.py` (non-
vectorized GAMSPy) are not inspected in this audit. Design memo §13(c) notes
they should mirror the vectorized change for consistency but are not strictly
required for the M0b1 run since `enh_RURO_estimate_FR.py --vectorized` uses
only `gamspy_estimation_vectorized.py`. The risk is that any future non-
vectorized run on an M0b1/M0b2 JSON would silently omit `beta_ll` from the
utility. Flag this in the M0b patch report as a known gap.

---

## 14. Summary of changes required

| component | change | required for M0b1 run | required for correct post-est |
|---|---|---|---|
| `estimation_spec_ruro_occ_M0b1.yaml` | **CREATE** (copy M0a-clean + 5 targeted edits) | yes | yes |
| `estimation_spec_ruro_occ_M0b2.yaml` | **CREATE** (copy M0b1 + name + theta_c bound) | for M0b2 run | for M0b2 post-est |
| `estimation_spec_parser.py` | **none** | — | — |
| `gamspy_estimation_vectorized.py` | **none** | — | — |
| `RURO_post_estimation_styled.py` | **one insertion** in `_add_predicted_probabilities` (8 lines, couples branch) | no | **yes** |
| `Results/_participation_diag_ruro_occ_M0b1.py` | **CREATE** (copy M0a-clean diagnostic + beta_ll term) | no | for 1e-14 cross-check |
| `Results/_M0b1_post_est_fit_check.py` | **CREATE** (analogue of M0a-clean fit-check script) | no | for validation |
| `estimation_engine.py` | optional consistency update | no | no |
| `gamspy_estimation.py` | optional consistency update | no | no |
| `compute_marginal_utilities_at_chosen` | out of scope for this patch; flag in patch report | no | no (MUL output will be stale for couples) |

The minimal change set for a correct M0b1 estimation and correct post-estimation
reporting is three items: create M0b1 YAML, insert the eight-line interaction
block into `_add_predicted_probabilities`, and create the M0b1 fit-check driver.
Everything else in the source tree is already M0b-ready.
