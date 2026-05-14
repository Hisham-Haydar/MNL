# RURO `ruro_occ_M0c` — Design Memo v1

Date: 2026-05-14

Scope: define the next-step identification repair on top of `ruro_occ_M0b2`.
Two candidate specifications (`M0c_b` and `M0c_pool`) are defined; one is
recommended as the first estimation to run; the other is sequenced as a
contingency. This memo does not commit to a YAML change; it is the design
the implementation prompt will follow.

Inputs to this memo:
- `docs/RURO_occ_M0a_clean_verdict_v1.md`
- `docs/RURO_occ_M0b_design_memo_v1.md`
- `docs/RURO_occ_M0b_implementation_report_v1.md`
- `Results/RURO_occ_M0b2_estimation_report_v1.md`
- `Results/RURO_occ_M0b2_multistart_report_v1.md`
- `Results/_M0b2_multistart_summary.json`
- `Results/RURO_occ_M0b1_wage_pathology_diagnostic_v1.md`
- `reports/fr_2016_ruro_occ_gamspy_M0b2_llm_summary_20260514_125410.md`
- `scripts/enhanced/estimation_spec_ruro_occ_M0b2.yaml`

---

## 1. Purpose of M0c

Convert the M0b2 boundary solution into an interior, fully-identified
specification by acting on the two binding constraints (`θ_c = 0` and
`β_ll = 2`) that the M0b2 multi-start confirmed as unique attractors. The
target is to clear v4 contract §22 Gate B (positive-semidefinite Hessian,
all SEs finite, 0 parameters at strict bounds, κ < 10⁷) while preserving
the M0b2 substantive fit gains (couples participation within 2 pp of
observed, couples L1 hours-bin distance below 0.5, predicted couples wages
within 5 EUR/h of observed mean).

M0c is identification repair on the couples consumption curvature and the
leisure-leisure interaction strength. It is not a robustness extension.
M1 (region opportunity dummies) remains the next robustness step after
M0c clears its gates.

---

## 2. Why M0a-clean → M0b2 isn't enough

M0b2 is a substantive triumph and an identification failure. The
multi-start report establishes both:

(a) **Substantive triumph (Gate F PASS).** From M0a-clean to M0b2, couples
predicted participation moved from 1.0000 to 0.982/0.988 (observed
0.972/0.965), couples mean hours moved from ~60 to 42.6/38.8 (observed
41.6/35.6), L1 hours-bin distance dropped from ~1.7 to 0.33/0.49, predicted
couples wage mean moved from ~140 EUR/h to 17.1/15.9 EUR/h (observed
17.7/15.2), and `p_chosen_median` moved from 8.3×10⁻⁵⁰ to 0.272. All Gate F
criteria are satisfied at M0b2.

(b) **Identification failure (Gate B FAIL).** Hessian has 1 negative
eigenvalue (min −18.86), κ = 8.52×10⁹, 5 NA SEs, 2 parameters at strict
bounds. Three of the NA SEs are in the singles consumption block (carrying
forward from M0a-clean); two are at the bound (`θ_c = 0`, `β_ll = 2`).

(c) **The boundary is the unique attractor.** Three diverse starting points
(`θ_c` initial values of −2.0, −1.8, −1.0; `β_ll` initial values of 0.0,
1.6, 0.5) all converged to `θ_c = 0.000` and `β_ll = 2.000` to machine
precision. The multi-start summary shows LL = −6511.4731 across all
successful starts. The fourth start (S2) failed for unrelated reasons
(GAMS arithmetic overflow at an extreme initial vector). This rules out
local-optimum traps within the M0b2 feasible region.

The interpretation of (c) is direct: the data wants `θ_c > 0` and
`β_ll > 2`. M0b2's constraints prevent the model from running away with
this preference (which would re-introduce the wage pathology), but the
constraints also prevent identification. Both bounds need to be addressed.

---

## 3. What M0c should fix

In order of priority:

(i) **No parameter at a strict bound.** `θ_c` and `β_ll` must each either
settle in their interior or be removed from the estimable vector via
structural fixing.

(ii) **Hessian negative eigenvalue count drops from 1 to 0.** The current
negative eigenvalue is at min = −18.86, which is large in magnitude;
freeing the bound constraints and allowing the parameters to settle should
move this eigenvalue positive.

(iii) **Hessian condition number drops below 10⁷.** Currently κ = 8.52×10⁹.

(iv) **All standard errors finite.** Currently 5 NA SEs. Two of these
(`θ_c`, `β_ll`) are bound-induced and will clear once the bounds are
addressed. Three (`β_c_sm`, `β_c_sf`, `θ_c_singles`) are due to the
singles consumption block's near-singular sub-block (pairwise correlations
of −1.04 to −1.07) and need separate attention — see §15.

(v) **Substantive fit moments must not regress.** Couples participation
within 2 pp of observed, couples L1 hours-bin distance ≤ 0.6, predicted
couples wage mean within 5 EUR/h of observed. Singles fit moments must
also hold at M0b2-equivalent levels.

(vi) **Multi-start verification.** At least three diverse starting points
must converge to the same interior point.

---

## 4. What M0c must not change

Hard constraints — same as M0b. Violating these turns M0c into a much
larger spec change.

(a) **All opportunity blocks remain identical to M0b2** (and thus to
M0a-clean, M0b1). No region dummies, no occupation interactions, no
conditional wage, no conditional hours by occupation. The four opportunity
blocks `O^E + O^H`, `O^Market`, `O^W`, `O^Occ` retain the exact same
specification.

(b) **The proposal-density correction is identical.** No change to the
proposal samplers, the `−log(prior)` subtraction, or the proposal-component
aliases.

(c) **MNL parquet files are not regenerated.** Same data, same draws, same
EUROMOD-computed disposable income.

(d) **Occupation does not enter utility.** Contract §20 exclusion
restriction stands.

(e) **Singles preferences are unchanged at the YAML level.** The
near-singular sub-block (`β_c_sm`, `β_c_sf`, `θ_c_singles`) is a real
identification issue but is reserved for M0c-pool (§6) if M0c-b doesn't
resolve it. M0c-b does not modify the singles block.

(f) **No new leisure shifters on couples preferences.** No child-age-band
dummies, no partner-status interactions on age, no new region or education
terms in utility.

(g) **Couples consumption remains shared at the household level.** No
adult-equivalence scale at this iteration. (M0c-equiv reserved for future
attempts.)

---

## 5. M0c-b: fix couples `θ_c = 0`, widen `β_ll`

The recommended first move. Acts directly on both M0b2 binding constraints.

**Mathematical effect**: with `θ_c = 0` fixed structurally, the couples
consumption Box-Cox becomes:

```
BC(C, 0) := lim_{θ→0} (C^θ − 1) / θ = log(C)
```

So couples utility uses log-consumption:

```
U_couples = β_c · log(C)
          + β_l_m(Z_m) · BC(L_m, θ_l_m)
          + β_l_f(Z_f) · BC(L_f, θ_l_f)
          + β_ll · BC(L_m, θ_l_m) · BC(L_f, θ_l_f)
```

This is a maintained-hypothesis specification: the data preferred a value
just above 0 (which would have given mildly convex consumption utility),
but M0b2 forced θ_c ≤ 0, and the multi-start confirmed the boundary was
unique. Fixing `θ_c = 0` (log utility) is one position back from the
unconstrained data preference and is the canonical economic functional
form for this region.

**Why log utility is defensible economically.** Log utility is the
benchmark functional form for many household consumption applications: it
embeds constant elasticity of marginal utility (= 1), it generates the
standard Cobb-Douglas-equivalent demand system in a static framework, and
it is the limiting case of CRRA at risk-aversion = 1. The literature
allows this value; Capéau et al. (2015/16) estimate `α_c = 0.61` for
couples, which is even more linear than log, so accepting log utility
here is more conservative than the literature's typical estimates.

**`β_ll` bound widening**: from `[−2.0, 2.0]` to **`[−1.0, 10.0]`**.

Rationale for the wider upper end (10.0): M0b2 saturated at 2.0 from three
distinct starts, so the gradient is pulling strongly upward. Setting the
upper end at 10.0 gives generous room for the interior optimum. If the
data wants `β_ll` at 5 or 7, this gets it there.

Rationale for the small negative lower end (−1.0 rather than 0.0): the
M0b2 evidence strongly suggests `β_ll > 0`, but `θ_c = 0` is a different
feasible set than M0b2's `θ_c = 0` boundary. Once `θ_c` is fixed
structurally, the couples consumption channel attenuates (no curvature
left to play with), and the leisure-leisure interaction might settle
differently. Allowing slightly negative values prevents a hard binding at
zero if the new equilibrium has `β_ll` near +0.1. Allowing some negative
range costs nothing and protects against another bound artifact.

**Initial value for `β_ll`**: **0.0** (spec-defaults convention), not 2.0
(warm-start from M0b2). The reasoning: the optimizer's path from 0.0 to
the new interior optimum tests whether the new spec is robust
independently of M0b2. If M0c-b can't find a sensible `β_ll` from 0.0,
the result is suspect anyway. Three perturbed starts (per the
multi-start design used for M0b2) provide the robustness check.

**Total parameter count**: 48 − 1 = **47** (one less than M0b2 because
`θ_c` is removed from the estimable vector).

**Expected outcome**: `β_ll` settles in interior, probably in [+2.0,
+5.0] based on the M0b2 gradient direction. Hessian becomes PSD because
the bound constraint that was sitting on the boundary is now absent. The
singles consumption block's three NA SEs (`β_c_sm`, `β_c_sf`,
`θ_c_singles`) may or may not clear automatically — these are not driven
by the couples-side constraint and may need M0c-pool to fix.

---

## 6. M0c-pool: pool `θ_c` globally (fallback)

Activate only if M0c-b passes the couples-bound test but the singles
consumption block still has NA SEs.

**Mathematical effect**: replace `theta_c_singles` and `theta_c` with a
single shared `theta_c`, free in `[−8.0, 0.95]`. Couples consumption
becomes `BC(C, theta_c_shared)`; singles consumption uses the same
exponent.

At M0b2, `θ_c_singles = −0.971` (interior, near `[−8, 0.95]` lower
end), and `θ_c (couples) = 0.000` (at upper bound of [−8, 0]). Pooling
these forces a common value across household types; based on relative
sample sizes (1,676 singles vs 2,577 couples) and current point
estimates, the pooled value would likely settle around `[−0.4, −0.2]`.

**Why pooling might help**: the M0b2 singles consumption block has
`|corr(β_c_sm, β_c_sf)| = 1.07`, `|corr(β_c_sm, θ_c_singles)| = 1.04`,
`|corr(β_c_sf, θ_c_singles)| = 1.05`. The non-PSD signature is concentrated
in this 3-parameter sub-block. Pooling `θ_c_singles` with `θ_c` removes
one parameter from this sub-block and forces a more identifying linear
combination, potentially restoring PSD.

**Why pooling might not help**: the three super-collinear pairs all
involve `β_c_sm` and `β_c_sf`, not `θ_c_singles` only. Pooling `θ_c`
removes one of the three culprits but leaves `β_c_sm × β_c_sf` collinearity
in place. If the latter is the dominant non-PSD direction, pooling
helps only partially.

**Total parameter count**: 47 − 1 = **46** (if pooling alone) or other
depending on whether further restrictions are added.

**Singles fit risk**: pooling forces the singles consumption curvature to
match couples'. Singles fit moments may degrade (current singles L1 hours
distance is 0.72 and 0.41 in M0b2). The pooled `θ_c` value will be closer
to 0 than singles' current −0.97, so singles consumption utility becomes
less concave, which may shift predicted singles hours toward extreme
alternatives. Monitor singles fit moments closely.

---

## 7. Why not M0c-wide (interior margin only)

A natural alternative is to keep `θ_c` estimable but tighten the bound
slightly from `[−8, 0]` to `[−8, −0.05]` (small interior margin),
while widening `β_ll` to `[−1, 10]`. Reject this variant for two reasons:

(a) **The multi-start gradient information is unambiguous.** Three
independent starts (from `θ_c` initial values of −2.0, −1.8, −1.0) all
walked `θ_c` upward to the boundary. The LL gradient w.r.t. `θ_c` is
positive throughout the feasible region: increasing `θ_c` toward 0
improves LL monotonically. There is no interior `θ_c` value where the
gradient sign changes. So M0c-wide would just produce another boundary
solution at the new tighter bound (`θ_c = −0.05`), with the same Gate B
failures.

(b) **M0c-wide consumes a cycle without producing information.** The
purpose of M0c-wide would be diagnostic — to confirm that the boundary
is binding rather than incidental. M0b2's multi-start has already done
this. Running another estimation to confirm what we already know is not
a useful step.

---

## 8. Recommended order of estimation

Run **M0c-b first** with three perturbed starts. If M0c-b clears Gate B,
that is the next baseline. If M0c-b clears `β_ll` and the couples-side
identification but the singles consumption block still has NA SEs, run
**M0c-pool**. If both fail Gate B, escalate to a supervisor memo.

**The exact first estimation to run** is M0c-b, with the same multi-start
runner used for M0b2 (`Results/_M0b2_multistart_runner.py` adapted to
point at the M0c_b spec). Use three starts:

1. **S1 — spec defaults**: `β_ll = 0.0`, all other parameters at YAML
   initial values. Most agnostic start.
2. **S2 — perturbation from M0b2 solution**: `β_ll = 2.0` (warm-start
   value), all other interior parameters perturbed with Gaussian noise
   (σ = 0.1, seed = 7). Tests whether M0b2's interior parameters are
   stable under the new specification.
3. **S3 — dispersed interior**: `β_ll = 5.0` (mid-range of new bound),
   all other parameters at spec defaults. Tests whether the optimizer
   can find the interior optimum from a position far from M0b2.

A fourth perturbed start can be added but is not required given the
multi-start work already done for M0b2.

**Wall-time per start**: ~100 seconds (same engine, similar problem
size). Total estimation time across three starts: ~5 minutes plus
diagnostics.

---

## 9. Recommended baseline if M0c-b works

If M0c-b clears Gate B with all three starts converging to the same
interior point: **M0c-b is the next baseline**.

If M0c-b clears the couples-side gates (`β_ll` interior, no neg eigs from
the couples block) but the singles consumption block still shows NA SEs:
**run M0c-pool**.

If M0c-b clears Gate B and Gate F: proceed to M1 (region opportunity).
If M0c-pool also clears Gate B and Gate F: M0c-pool is the baseline.

---

## 10. Parameters to add / remove / restrict / leave unchanged

### M0c-b

| change | parameter | M0b2 status | M0c-b status |
|---|---|---|---|
| **REMOVE** | `theta_c` | estimable in `[−8.0, 0.0]` | structurally fixed at 0.0 (not in estimable vector) |
| **WIDEN BOUND** | `beta_ll` | `[−2.0, 2.0]` | `[−1.0, 10.0]` |
| **CHANGE INITIAL** | `beta_ll` | 0.0 (YAML default) | 0.0 (kept; not 2.0 from warm-start) |
| **UNCHANGED** | everything else | — | — |

### M0c-pool (contingency)

Adds to M0c-b the change:

| change | parameter | M0c-b status | M0c-pool status |
|---|---|---|---|
| **POOL** | `theta_c_singles` | estimable in `[−8.0, 0.95]` | replaced by `theta_c` (shared); estimable in `[−8.0, 0.95]` |

Net parameter count: M0b2 = 48 → M0c-b = 47 → M0c-pool = 46.

---

## 11. Required YAML changes

### M0c-b: new file `estimation_spec_ruro_occ_M0c_b.yaml`

Copy `estimation_spec_ruro_occ_M0b2.yaml` and apply:

1. **Rename**: `specification.name: "ruro_occ_M0c_b"`.

2. **Description**: update to describe the fix-and-widen.

3. **Fix `theta_c` structurally**. Two implementation strategies, in
   increasing order of invasiveness — pick the least invasive that works:

   **Strategy A (spec-side fixing, preferred)**: add a new field at the
   top of the consumption block specifying the fixed value:

   ```yaml
   utility:
     consumption:
       coefficient: "beta_c"
       box_cox_exponent: "theta_c"
       fixed_box_cox_exponent_value: 0.0    # NEW
       singles_box_cox_exponent: "theta_c_singles"
       box_cox_bounds: [-8.0, 0.95]
   ```

   The parser interprets `fixed_box_cox_exponent_value: 0.0` as: do not
   add `theta_c` to the estimable parameter vector; substitute 0.0
   everywhere `theta_c` would have been used.

   **Strategy B (engine-side fixing, fallback)**: remove `theta_c` from
   `initial_values` and from `optimization.bounds`. Modify the
   vectorized engine's couples utility evaluator to use a hard-coded
   `0.0` in place of `theta_c` whenever `theta_c` is not in the
   parameter vector. Risk: harder to discover, harder to undo.

   Strategy A is preferred. The implementation prompt should attempt
   Strategy A first; if the parser is incompatible, the prompt falls
   back to Strategy B and documents the fallback.

4. **Remove `theta_c` from `initial_values`** and from
   `optimization.bounds` regardless of strategy.

5. **Widen `beta_ll` bound** in `optimization.bounds`:

   ```yaml
   # M0b2 (was):
   beta_ll: [-2.0, 2.0]

   # M0c-b:
   beta_ll: [-1.0, 10.0]
   ```

6. **Keep `beta_ll` initial value at 0.0** in `initial_values`.

7. **Everything else unchanged** from M0b2.

### M0c-pool: new file `estimation_spec_ruro_occ_M0c_pool.yaml`

All of M0c-b plus: remove `singles_box_cox_exponent: "theta_c_singles"`
from `utility.consumption`. The parser falls back to using the couples
`theta_c_param_name(group)` resolution to route both singles groups
through the same shared `theta_c` (which is now estimable, not fixed).

Equivalently: remove `theta_c_singles` from `initial_values` and from
`optimization.bounds`. Restore `theta_c` to estimable status (it was
fixed in M0c-b; it returns to estimable in M0c-pool) with bounds
`[−8.0, 0.95]`. Initial value for `theta_c` in M0c-pool: −0.5 (between
singles' M0b2 value of −0.97 and the data's couples preference around
0.0).

---

## 12. Required parser / engine changes

The implementation prompt should make minimum-invasive changes:

(a) **`scripts/enhanced/estimation_spec_parser.py`**: add support for
the `fixed_box_cox_exponent_value` field (Strategy A in §11). The parser
should:

- recognise the new field under `utility.consumption`;
- when the field is present, do NOT add `theta_c` to
  `spec.all_param_names`;
- store the fixed value on the spec object as
  `spec.fixed_theta_c_value: float`;
- attribute the fixed value via the existing `theta_c_param_name(group)`
  resolution method (or extend it to return a literal float when the
  parameter is fixed).

This is a backward-compatible additive change. M0a-clean, M0b1, and M0b2
specs continue to parse identically.

(b) **`scripts/enhanced/gamspy_estimation_vectorized.py`**: where the
engine looks up the couples `theta_c` for the consumption Box-Cox
evaluation, the lookup must return the fixed scalar when
`spec.fixed_theta_c_value` is set, and the parameter from `param_vars`
otherwise. Pseudocode:

```python
def get_theta_c(spec, param_vars):
    if hasattr(spec, 'fixed_theta_c_value') and spec.fixed_theta_c_value is not None:
        return spec.fixed_theta_c_value
    return param_vars[spec.theta_c_param_name('couples')]
```

This applies to every site that previously read `theta_c` from the
parameter vector. A grep for `theta_c` in the engine will identify them.

(c) **`scripts/enhanced/estimation_engine.py`** and
**`gamspy_estimation.py`**: mirror the change. If only the vectorized
engine is in use for the `--vectorized` path, the others can be flagged
for follow-up but are not strictly required for the M0c-b run.

(d) **Analytical gradient**: `θ_c` is no longer estimated, so the
gradient of `LL` with respect to `θ_c` is not needed. The gradient
implementation should simply skip the `θ_c` slot when building the
gradient vector. If the gradient is reported by parameter name (likely),
the M0c-b gradient vector will be of length 47 instead of 48; the engine
must handle the shorter vector cleanly.

(e) **Box-Cox numerical handling at `θ = 0`**: when `θ_c = 0` is
substituted, the Box-Cox formula `(C^θ − 1) / θ` is `0/0` and must be
replaced by the analytic limit `log(C)`. The engine must implement:

```python
def box_cox(C, theta):
    if abs(theta) < 1e-12:
        return np.log(C)
    return (C**theta - 1.0) / theta
```

The engine likely already has this (Box-Cox at `θ ≈ 0` is a standard
edge case), but the implementation prompt should verify and add the
limit if missing.

---

## 13. Required post-estimation changes

The post-estimation reporter
(`scripts/enhanced/RURO_post_estimation_styled.py`) needs to mirror the
engine change for the V reconstruction in `_add_predicted_probabilities`.
Same lookup pattern as in §12(b). The participation V-decomposition
diagnostic
(`Results/_participation_diag_ruro_occ_M0a_clean.py` —
new variant `_participation_diag_ruro_occ_M0c_b.py`) needs the same
treatment.

The Box-Cox limit at `θ → 0` should be checked in the reporter too. If
the reporter uses a different Box-Cox implementation than the engine, the
1e-14 cross-check that anchored the M0a-clean reporting patch will fail
under M0c-b. Both implementations must use the same numerical limit.

`compute_marginal_utilities_at_chosen` still has the stale-`β_ll` issue
flagged in the M0b implementation report §9. That issue is independent of
M0c-b and remains a follow-up.

---

## 14. Diagnostics required after estimation

After M0c-b (and after M0c-pool if run), the diagnostic battery is:

(a) **Multi-start verification across the three starts.** Confirm all
three converge to the same interior point to 6 significant figures.

(b) **Standard low-token LLM summary**. Compare against M0b2's
`fr_2016_ruro_occ_gamspy_M0b2_llm_summary_20260514_125410.md` line by
line.

(c) **Patched-reporter fit check**. Adapt the M0a-clean fit-check script
to M0c-b. The reporter V vector must match the structural diagnostic V
within 1e-14 on the 100-household sample (same protocol used for the
M0a-clean patch).

(d) **Participation V-decomposition**. Component-wise `V_work − V_nonwork`
per group. Compare to M0b2. The couples `U` gap should be smaller in
M0c-b than in M0b2 (because log utility caps the consumption channel
even more than M0b2's `θ_c = 0` boundary).

(e) **Wage-pathology re-check**. The diagnostic that ran on M0b1
(`Results/_wage_pathology_diag_ruro_occ_M0b1.py`) should be re-run on
M0c-b. Predicted couples wage mean must stay below 25 EUR/h.

(f) **Cross-spec comparison table** of M0a-clean vs M0b1 vs M0b2 vs M0c-b
(vs M0c-pool if run). Same fields as the M0b2 estimation report §6.

(g) **Bound-binding check on `β_ll`**: confirm `β_ll` settles strictly
interior to `[−1, 10]`. If `β_ll` hits +10, the bound was still too tight
and M0c-b² should widen further. If `β_ll` hits −1, something is wrong
(this would contradict M0b2's strong upward gradient).

---

## 15. Pass/fail criteria

### Gate A — Spec, parse, smoke test

| check | required |
|---|---|
| `spec.name = "ruro_occ_M0c_b"` (or `_M0c_pool`) | yes |
| `n_estimated_params = 47` (M0c-b) or 46 (M0c-pool) | yes |
| `'theta_c' NOT in spec.all_param_names` (M0c-b) | yes |
| `'beta_ll' in spec.all_param_names` | yes |
| Box-Cox at `θ = 0` evaluates as `log(C)` | yes |
| likelihood is finite at initial values | yes |
| gradient norm at initial values is finite | yes |

### Gate B — Estimation (the hard gates)

Same thresholds as M0b's Gate B (§16 of design memo M0b v1):

| check | threshold |
|---|---|
| solver status | `OptimalLocal` or equivalent |
| n_negative_Hessian_eigenvalues | **0** |
| Hessian condition number κ | **< 10⁷** |
| smallest \|eigenvalue\| | > 10⁻⁸ |
| n_parameters_with_NA_SE | **0** (M0c-b) or **0** (M0c-pool) |
| n_parameters_at_strict_bound | **0** |
| cross-engine `joint_ll` agreement | < 10⁻⁶ per obs |
| multi-start agreement on θ̂ | 6 significant figures |

### Gate F — Fit (must not regress from M0b2)

| check | threshold |
|---|---|
| couples participation (cou_m) | within 0.03 of observed 0.972 |
| couples participation (cou_f) | within 0.03 of observed 0.965 |
| couples mean hours (cou_m) | within 5 of observed 41.6 |
| couples mean hours (cou_f) | within 5 of observed 35.6 |
| L1 hours-bin distance (cou_m) | < 0.6 |
| L1 hours-bin distance (cou_f) | < 0.6 |
| couples predicted mean wage (cou_m) | within 5 EUR/h of observed 17.7 |
| couples predicted mean wage (cou_f) | within 5 EUR/h of observed 15.2 |
| `p_chosen_min` (whole sample) | > 10⁻¹⁰ |
| singles fit moments | no regression vs M0b2 |

### Pass/fail decisions

- **M0c-b passes Gate A + B + F**: declare M0c-b as next baseline.
  Proceed to M1.
- **M0c-b passes A + B (couples block clear), fails B in singles
  consumption block** (3 NA SEs remain in `β_c_sm`, `β_c_sf`,
  `θ_c_singles`): run **M0c-pool**.
- **M0c-b passes A + F, fails B with new bound on `β_ll`**: widen `β_ll`
  upper bound further (e.g., `[−1, 25]`) and re-run as M0c-b² with same
  multi-start protocol.
- **M0c-b fails A**: implementation bug. Inspect parser and engine
  changes. Do not re-estimate until A passes.
- **M0c-b passes A but fails F** (couples fit regresses substantially):
  fixing `θ_c = 0` was too restrictive. Try M0c-pool (which keeps
  `θ_c` estimable but pools singles with couples).
- **M0c-pool fails Gate B too**: the identification problem is deeper
  than M0c can resolve. Escalate to supervisor memo before further code
  work. Candidate next steps include an adult-equivalence scale on
  couples consumption (M0c-equiv), or accepting M0c-b as a working
  specification with documented identification caveats.

---

## 16. What gets unblocked at M0c-b PASS

Three lines of work that have been postponed by the M0a → M0b → M0c
identification ladder become unblocked once Gate B clears at M0c-b (or
M0c-pool):

(a) **Welfare scaffolding on real estimates**. The money-metric
well-being code can be developed and tested against the actual M0c-b
θ̂, not just against a synthetic θ⁰ from a recovery test. Both point
estimates and bootstrap-based confidence bands become possible (the
bootstrap is necessary in any case because asymptotic SEs from MNL with
a complex constraint structure are not directly informative for welfare
nonlinearly derived from θ̂).

(b) **M1 region-opportunity step**. With Gate B passing, adding region
dummies to `O^E + O^H` is a clean incremental step. Confirm `drgn1`
(NUTS-1) is present in the parquets, draft the M1 YAML, run the
estimation.

(c) **Capéau-style elasticity table**. Compute aggregate wage
elasticities (intensive, extensive, total) per group via the simulation
procedure in Capéau et al. §3.5. Compare to their Belgian numbers as a
sanity check.

---

## 17. What remains postponed to M1

The v4 contract roadmap items unchanged from the M0b design memo:

- **M1 region dummies on `O^E + O^H`**: postponed until M0c-b clears
  Gate B + F. Pre-condition: confirm `drgn1` is in the parquets.
- **M2 fine occupation (`loc` instead of `loc4`)**: postponed until M1
  has shown whether region matters.
- **M3 occupation-conditional wage**: postponed.
- **M4 occupation-conditional hours**: postponed.
- **Recovery test (Monte Carlo seed)**: postponed.
- **Seed stability** (alternative draw seeds): postponed.
- **Capéau-style elasticity table on M0c-b**: unblocked at M0c-b
  Gate B pass, see §16(c).
- **Welfare scaffolding on real estimates**: unblocked at M0c-b
  Gate B pass, see §16(a).
- **Slides, supervisor figures, abstract numbers touching couples**:
  unblocked once Gate B + F clears.

---

## Suggested filename

Save this memo as: `docs/RURO_occ_M0c_design_memo_v1.md`
(category: technical memo / design).
