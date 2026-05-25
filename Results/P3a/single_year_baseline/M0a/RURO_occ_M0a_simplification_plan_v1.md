# RURO `ruro_occ_M0a` — Design Memo v1

Date: 2026-05-13

Scope: define the simplest conservative repair of `ruro_occ_M0` that
addresses the identification failures documented in
`RURO_ruro_occ_M0_triage_memo_v1.md` and
`RURO_ruro_occ_M0_baseline_decision_v1.md`. This memo does not expand the
model. It removes the smallest set of parameters needed to bring Gates B2
and B3 of v4 contract §22 within reach.

Active naming: `ruro_occ_M0a`. The YAML to create is
`estimation_spec_ruro_occ_M0a.yaml`.

---

## 1. Why M0 failed

Three identification failures, with the first two technically blocking
gates B2 and B3.

(a) **The female-singles consumption block is jointly unidentified.**
`β_c_sf` and `θ_c_sf` return NA standard errors. Their reported parameter
correlation is `−1.035`, a magnitude > 1 that is impossible for a valid
covariance matrix. This is the direct mechanical fingerprint of two
negative diagonal entries in the inverse Hessian and is the proximate
cause of κ = 6.76 × 10¹⁰ with two negative eigenvalues.

(b) **The (intercept, education) cell of every leisure block is
near-collinear.** Reported correlations: `corr(β_l0_sf, β_l_educH_sf) =
0.996`, `corr(β_l0_f, β_l_educH_f) = 0.979`, `corr(β_l0_sm,
β_l_educH_sm) = 0.971`, `corr(β_l0_m, β_l_educH_m)` similar by structure.
At correlations 0.97–0.99, the data identify a single linear combination
of `β_l0_g + β_l_educH_g · 1{educH=1}`, not two separate parameters per
group. This did not by itself cause Gate B to fail, but it produces SEs
that are uninterpretable in isolation.

(c) **The hours/employment opportunity block over-predicts participation
and over-predicts hours.** Predicted participation ≈ 1.0000 for all
four groups against observed 0.93–0.97; predicted couples mean hours 58
against observed 36–42. This pathology is **not addressed by M0a YAML
changes** and is treated separately in §6 and §9 below: a participation
diagnostic at the M0 converged θ must be run first to determine whether
the issue is in the structural index, in the proposal correction, or in
the post-estimation reporting code. Until that diagnostic returns, M0a
makes no YAML attempt to "fix" hours/participation fit.

The wage block, occupation block, and prior-correction machinery are
not in the failure list and are not changed at M0a.

---

## 2. M0a objective

Pass Gates B2 and B3 of v4 contract §22 on the existing France 2016
rebuilt MNL files, with the smallest possible change to the M0 spec.

Concretely:

- No negative Hessian eigenvalues at the converged θ̂.
- Hessian condition number `κ < 10⁷`.
- All M0a parameters return finite SEs.
- No bound hits on substantive parameters.

Explicit non-objectives at M0a:

- **Not** to fix predicted participation = 1.0000. That is a separate
  diagnostic step; M0a is a spec-side identification repair and does
  not assume the participation issue is YAML-tractable.
- **Not** to improve the hours-bin L1 distance. Same reason.
- **Not** to add interactions, random coefficients, conditional
  opportunity structures, or any new parameters of any kind.
- **Not** to change the choice index `V = U + O^E + O^H + O^W + O^Occ
  − log q`. The model family is preserved exactly.
- **Not** to change starting values to "warm-start" from M0. The M0
  optimum is on the wrong side of an indefinite Hessian; M0a starts
  from spec defaults or a small random perturbation.

The point of M0a is to make the next estimation tractable and
informative. It is not the JMP baseline. M0a passing Gate B is a
necessary condition for considering it the baseline; the participation
pathology and the §22 items B5 (seed stability), B6 (cross-engine),
and §23 recovery test are separate gates handled after M0a.

---

## 3. Parameters to fix

None hard-fixed at M0a.

Hard-fixing a parameter (e.g. `θ_c_sm` fixed at `[−1.5255, −1.5254]` in
the legacy `M2h_pruned` spec) is a stronger move than pooling and
should be reserved for a contingency `M0b` if M0a still fails Gate B.
At M0a, every estimated parameter is free within its bound.

The v4 contract §19 already states that **no parameter is hard-fixed
at M0**. M0a respects this.

---

## 4. Parameters to remove

Remove four parameters, all in the utility/leisure block.

| Parameter | Reason for removal |
|---|---|
| `β_l_educH_sm` | `corr(β_l0_sm, β_l_educH_sm) = 0.971` at M0; not separately identified from `β_l0_sm` |
| `β_l_educH_sf` | `corr(β_l0_sf, β_l_educH_sf) = 0.996`; not separately identified from `β_l0_sf` |
| `β_l_educH_m` | `corr(β_l0_m, β_l_educH_m) ≈ 0.97`; not separately identified |
| `β_l_educH_f` | `corr(β_l0_f, β_l_educH_f) = 0.979`; not separately identified |

Total: **−4 parameters**.

Education does **not** disappear from the model. It remains in:

- The **hours/employment opportunity** block as `β_E_educH` (the
  market-access shifter on education). This is the structural channel
  through which higher-education individuals receive more market
  offers.
- The **wage opportunity** block as `β_w_educH` (the Mincer education
  premium). This is the structural channel through which
  higher-education individuals receive higher wage offers.

What M0a removes is only the **leisure-utility** education shifter
`β_l_educH_g`, on the grounds that the leisure intercept `β_l0_g` is
already absorbing all the variation that this term was claiming to
explain. Removing it is identification repair, not realism reduction:
the model loses no economic content because `β_l_educH_g` was not
identified separately from `β_l0_g` in M0.

If M0a passes Gate B, `β_l_educH_g` can be reintroduced in a later
robustness pass (`M1`+) once the leisure block is on solid footing.

---

## 5. Parameters to pool

Pool one pair across the singles partition.

| Old (M0) | New (M0a) | Reason |
|---|---|---|
| `θ_c_sm`, `θ_c_sf` | single shared `θ_c_singles` | `(β_c_sf, θ_c_sf)` NA SE; `corr = −1.035`. Pooling `θ_c` across singles releases `β_c_sm` and `β_c_sf` to be jointly identified from twice the data. |

Total from pooling: **−1 parameter**.

What M0a does **not** pool, deliberately:

- `β_c_sm` and `β_c_sf` remain **separate** within singles. The
  failure was in `(β_c_g, θ_c_g)` joint identification per group, not
  in the gendered consumption scale. With one shared `θ_c_singles`,
  the two `β_c_sm`, `β_c_sf` can identify separately. If they still
  fail in M0a, the contingency move is `M0b`: pool `β_c_singles` too.
- Singles `θ_c_singles` and couples `θ_c` remain **separate**. The
  v4 contract treats singles and couples as different consumption
  units (singles consume their own disposable income; couples share
  household disposable income). The reported MUC = 1 at C ≈ 0.83 for
  singles and ≈ 8.30 for couples is a 10× scale gap that probably
  reflects a real difference in C-normalisation between singles and
  couples and should not be forced into a single curvature. Pooling
  `θ_c` globally (across the singles/couples partition) would impose
  a strong restriction without identification evidence demanding it.
- Couples `β_c` and `θ_c` stay shared **within couples** (between cm
  and cf), per v4 contract §17 item 5. M0a does not touch the
  couples consumption block.

Net pooling: only `θ_c_sm = θ_c_sf = θ_c_singles`. One parameter
removed. This is the minimum pool consistent with the identification
evidence.

---

## 6. Opportunity block simplification

**None.** All opportunity blocks remain identical to M0.

This is deliberate. The hours/participation fit pathology is the most
visible failure of M0, and it is tempting to simplify the
`(β_E, β_h_pt1, β_h_pt2, β_h_ft, β_E_gsur, β_E_educH)` block at M0a.
M0a does not do this for three reasons.

(a) The opportunity-block parameters at M0 are all individually
significant with sensible signs. `β_E = −2.61` (t = −8.7), `β_h_ft =
1.46` (t = 29.3), `β_h_pt2 = 0.37` (t = 3.4), `β_h_pt1 = −0.52` (t =
−4.8), `β_E_gsur = −0.77` (t = −3.5). These are not failing in any
identification sense. The fit pathology is something the model is
doing with these parameters, not a problem with the parameters
themselves.

(b) The participation = 1.0000 pattern is uniform across all four
groups. A uniform pathology of that exact form is far more likely to
be a coding issue (sign convention, double-counted prior correction,
or a `1{h > 0}` indicator inverted somewhere) than a parameterisation
issue. Removing or modifying focal-point parameters in the YAML will
not fix a coding issue; it will just confuse the diagnostic.

(c) The right ordering is: first run the V_nonwork vs V_work
diagnostic (Step 2 of the prior baseline-decision memo); if the
diagnostic shows that the structural index produces non-zero
non-employment probability but the post-estimation report shows
1.0000, the bug is in the reporting code; if the structural index
itself produces near-zero non-employment, the bug is in the
estimator or proposal correction. Either way, the M0a YAML should
be unchanged in the opportunity block while that diagnostic runs.

If after M0a the participation pathology persists, the next step is
to inspect the engine code, not to further simplify the YAML.

**The wage block is also unchanged.** It is the cleanest piece of
M0 and there is no identification reason to touch it.

**The occupation-opportunity block is unchanged.** Twelve `β_occ_k_g`
parameters, 9 of which were significant at p < 0.05 in M0. The block
inherits some contamination from the participation pathology (§5 of
the baseline-decision memo) but the structural specification is
sound and removing parameters here would weaken the JMP value-add.

---

## 7. Preference block simplification

After §4 and §5, the M0a preference block is:

| Component | Parameter | Count | Per group? |
|---|---|---|---|
| Consumption scale (singles) | `β_c_sm`, `β_c_sf` | 2 | gendered within singles |
| Consumption scale (couples) | `β_c` | 1 | shared cm/cf |
| Consumption curvature (singles) | `θ_c_singles` (new pooled) | 1 | shared sm/sf |
| Consumption curvature (couples) | `θ_c` | 1 | shared cm/cf |
| Leisure intercept | `β_l0_g` | 4 | per group |
| Leisure age | `β_l_age_g` | 4 | per group |
| Leisure age² | `β_l_age2_g` | 4 | per group |
| Leisure children | `β_l_nkids_sf`, `β_l_nkids_f` | 2 | females only |
| Leisure curvature | `θ_l_g` | 4 | per group |

Preference parameter count: **23** (was 28 at M0; −5 net: −4 from §4,
−1 from §5).

No consumption-leisure interaction. No leisure-leisure interaction.
No random coefficients. No occupation in utility. The structural form
of `U` is unchanged from v4 contract §8 except for the two removals
above.

---

## 8. Required YAML changes

Create a new file `scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml`
by copying `estimation_spec_ruro_occ_M0.yaml` and applying the four
changes below.

(a) **In `specification:`**, rename:

```yaml
specification:
  name: "ruro_occ_M0a"
  description: "M0a identification repair: θ_c pooled across singles; β_l_educH removed from utility"
  wage_spec: "vw"
  model_family: "regular"
```

(b) **In `utility.leisure.shifters:`**, remove the `educH` shifter
entry. The block becomes:

```yaml
leisure:
  intercept: "beta_l0"
  box_cox_exponent: "theta_l"
  box_cox_bounds: [-8.0, 0.95]
  shifters:
    - variable: "age_norm"
      coefficient: "beta_l_age"
    - variable: "age_norm2"
      coefficient: "beta_l_age2"
    - variable: "n_children"
      coefficient: "beta_l_nkids"
      gender_specific: true   # female only
    # REMOVED at M0a: educH shifter (corr with β_l0_g > 0.97 in M0)
```

(c) **In `initial_values:`**, remove four entries (`β_l_educH_sm/sf/m/f`)
and consolidate the singles `θ_c` pair into a single
`θ_c_singles`:

```yaml
# REMOVE these four lines:
#   beta_l_educH_sm: 0.0
#   beta_l_educH_sf: 0.0
#   beta_l_educH_m: 0.0
#   beta_l_educH_f: 0.0

# REPLACE these two lines:
#   theta_c_sm: -1.0
#   theta_c_sf: -1.0
# WITH the single shared singles curvature:
theta_c_singles: -1.0
```

(d) **In `optimization.bounds:`**, perform the same four removals and
the same `θ_c` consolidation:

```yaml
# REMOVE these four lines:
#   beta_l_educH_sm: [-8.0, 5.0]
#   beta_l_educH_sf: [-8.0, 5.0]
#   beta_l_educH_m:  [-8.0, 5.0]
#   beta_l_educH_f:  [-8.0, 5.0]

# REPLACE these two lines:
#   theta_c_sm: [-8.0, 0.95]
#   theta_c_sf: [-8.0, 0.95]
# WITH:
theta_c_singles: [-8.0, 0.95]
```

(e) **Parser consideration.** The current
`estimation_spec_parser.py` may auto-create gendered copies of
`θ_c` based on `gender_specific` flags or naming conventions. The
parser must be checked to confirm that `θ_c_singles` is read as a
shared singles-only parameter (one parameter used by both sm and
sf likelihood blocks, not duplicated). If the parser does not
support this naming convention out of the box, the minimum
parser change is to recognise `θ_c_singles` (and refuse to
auto-create `θ_c_sm`, `θ_c_sf` when this name is present). This is
a one-line addition to the parser's gendered-copy logic.

If parser modification is too large a scope at this step, an
equivalent alternative is to keep two names `θ_c_sm` and `θ_c_sf`
but link them via an equality constraint in
`expression_constraints:`:

```yaml
expression_constraints:
  enabled: true
  default_mode: hard
  constraints:
    - name: theta_c_singles_pool
      expression: "theta_c_sm - theta_c_sf"
      lower: 0.0
      upper: 0.0
```

The hard equality constraint yields exactly the same likelihood
landscape as the renamed-shared-parameter approach, but at the cost
of one extra reported parameter that is mechanically pinned to its
sibling. The equality-constraint route is the **fallback** for
parser-side hurdles, not the preferred route.

(f) **Nothing else changes.** The `hours_opportunity`,
`wage_opportunity`, `market_opportunity`, and `occupation_opportunity`
blocks are byte-identical to M0. The `couples:` block stays empty.
The `optimization:` method, max_iterations, tolerance, gradient
tolerance, and expression_constraints (other than (e) fallback)
stay as in M0.

Parameter count change: **52 → 47** at M0a.

---

## 9. Required validation checks

Two pre-estimation checks and four during/after.

**Pre-estimation (run before invoking the estimator):**

P1. **MNL data validation re-check.** Re-run
`Results/_validation_ruro_occ_M0.py` against the rebuilt parquet
files. Expected: all 8 categories PASS (no data has changed since
2026-05-13_10:38; this is a sanity check that the validation script
is reproducible and that no shared-storage file has been altered).

P2. **Participation diagnostic at M0 converged θ.** This is Step 2
from `RURO_ruro_occ_M0_baseline_decision_v1.md` §12. Compute, at the
M0 converged θ, the per-household `V_nonwork`, `max_j V_work,j`, and
the implied `P(non-work)` from the structural index (no
post-estimation reporting). Sample 100 households across all four
groups. Save the per-household table and a summary as
`RURO_ruro_occ_M0_participation_check_v1.md`. **This is a precondition
for interpreting M0a.** If the diagnostic shows non-zero `P(non-work)`
under the structural index, the M0 reported "predicted participation
= 1.0000" was a post-estimation reporting artefact and M0a only needs
to clear Gate B. If the diagnostic shows `P(non-work) ≈ 0` under the
structural index, the spec-side change in M0a will not by itself
fix the participation issue and code-side work is needed in parallel.

**During estimation (`enh_RURO_estimate_FR.py --vectorized --solver
gamspy-conopt --spec-config estimation_spec_ruro_occ_M0a.yaml --group
joint --auto-timestamp --verbose --warm-start none`):**

E1. **Spec parses** with exactly 47 estimable parameters. Print the
parameter count from `spec.all_param_names` before solving.

E2. **No warm-start from M0.** `--warm-start none` is mandatory.
Starting from M0 θ̂ would re-enter the indefinite-Hessian region.
At least three starts in total: spec defaults, spec defaults with
small Gaussian perturbation (σ = 0.1 of each bound width), and a
random uniform draw within bounds. If GAMSPy/CONOPT does not natively
support multistart, run three separate invocations and compare the
converged θ̂ and joint LL.

E3. **Optimizer terminates with `OptimalLocal`** on all three result
blocks (sm, sf, couples) and on all three starts.

**Post-estimation:**

E4. **Run `RURO_post_estimation_styled.py --compute-se`** on each
of the three converged runs. Save the low-token Markdown summary
to `reports/`. Read the resulting `Convergence Health Summary`
panel.

E5. **Cross-engine consistency check** at the M0a converged θ from
the spec-defaults start: evaluate `joint_ll` on both
`gamspy_estimation_vectorized.py` and either `gamspy_estimation.py`
or `estimation_engine.py`. The contract gate is agreement within
`1e−6` per observation. Save as
`RURO_ruro_occ_M0a_cross_engine_check_v1.md`.

---

## 10. Pass/fail criteria for M0a

Three gates, evaluated in order.

**Gate A — Spec parses correctly:**

| Check | Required |
|---|---|
| `spec.name = "ruro_occ_M0a"` | yes |
| `n_estimated_params = 47` | yes |
| `β_l_educH_*` absent from `spec.all_param_names` | yes |
| `θ_c_singles` (or equivalent pooled object) present | yes |
| `θ_c_sm`, `θ_c_sf` absent (or hard-linked) | yes |

If any of these fail, the YAML is wrong; fix and re-parse before any
estimation attempt.

**Gate B — Estimation convergence (the headline gates):**

| Check | Threshold | Source |
|---|---|---|
| Optimizer status on all 3 result blocks | `OptimalLocal` / equivalent | v4 §22 B1 |
| Number of negative Hessian eigenvalues | 0 | v4 §22 B2 |
| Hessian condition number κ | < 10⁷ | v4 §22 B2 |
| Smallest \|eigenvalue\| | > 10⁻⁸ | v4 §22 B2 |
| All 47 parameters return finite SEs | yes | v4 §22 B3 |
| Parameters within 10⁻³ of bound (substantive ones) | 0 | v4 §22 B4 |
| Cross-engine `joint_ll` agreement | < 10⁻⁶ per obs | v4 §22 B6 |
| Multistart agreement | max-Δ on key params < 5% across starts | v4 §22 (multistart proxy for B5) |

If Gate B passes on all eight, M0a is provisionally usable as the JMP
baseline at the within-sample level. Seed-stability (B5 proper) and
recovery (Gate C) can then be planned.

**Gate B Soft Diagnostics (informational, not blocking):**

- Predicted participation: ideally moves away from 1.0000 toward
  observed 0.93–0.97. If it does not, the participation pathology
  is confirmed to be spec-orthogonal (i.e. code-side); flag for
  follow-up, but do not block M0a.
- Hours-bin L1 distance: ideally drops from 1.66 (cou_f) and 1.41
  (cou_m). Same logic.
- `corr(β_l0_g, β_l_educH_g)` is now N/A (the latter is removed).
  `corr(β_c_g, θ_c_singles)` should be visibly below 0.95 for both
  singles groups. If it is not, additional pooling is needed.

**Failure responses, in order of escalation:**

If Gate A fails → fix the YAML or parser. Do not estimate.

If Gate B2 fails (still indefinite Hessian) → identify which
parameter pair drives the indefiniteness from the new correlation
panel. The most likely candidates are `(β_c_sm, β_c_sf)` (in which
case `M0b` pools `β_c_singles = β_c_sm = β_c_sf`) or `(β_l0_g,
β_l_nkids_g)` in the female blocks (in which case `M0b` removes
`β_l_nkids` from utility).

If Gate B3 fails on a small number of parameters → identify whether
those parameters share a near-1 correlation with another. If so,
pool or remove the pair following the same logic. Do not add
parameters.

If Gate B6 fails (cross-engine disagreement) → one of the engines
has a coding bug. Do not interpret either set of estimates until the
bug is found. M0a is held at status "diagnostic only" until B6
passes.

If predicted participation is still 1.0000 after M0a clears all Gate
B items → the issue is in the engine code (likely the
`exp(V_nonwork) / Σ exp(V_j)` evaluation, the `1{h>0}` gate on the
opportunity terms, or the prior correction on non-work
alternatives). Open as a parallel work item; do not address it
through further M0a-level YAML changes.

If predicted participation moves toward observed AND Gate B passes
→ M0a becomes the candidate baseline. Plan seed-stability (run M0a
with two alternative draw seeds in the data rebuild; this requires
the rebuild pipeline, which is in good shape) and recovery test
(synthetic data; this requires roughly 12 h compute for R = 50). Only
after both pass should the JMP baseline label be applied and the
welfare layer be invoked.

---

## What M0a deliberately does not do

For audit clarity:

- Does not add `β_E_educL`, region dummies, conditional opportunity
  structures, `β_cl` or `β_ll` interactions, or any extension from
  the M1–M6 ladder.
- Does not change the choice index, the proposal correction, or the
  prior factorisation.
- Does not change the draw script, the EUROMOD scenario, the MNL
  prep, or the rebuilt parquets.
- Does not warm-start from M0 θ̂.
- Does not hard-fix any parameter at a value.
- Does not modify the occupation-opportunity block (which inherits
  some contamination from the participation issue but is structurally
  intact).
- Does not modify the wage block.
- Does not commit to a welfare layer or to recovery testing.

This is identification repair. Nothing more.

---

## Suggested filename

Save this memo as: `RURO_ruro_occ_M0a_design_memo_v1.md`
(category: technical memo / design).
