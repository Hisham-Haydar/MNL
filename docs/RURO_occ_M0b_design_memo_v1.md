# RURO `ruro_occ_M0b` — Design Memo v1

Date: 2026-05-14

Scope: define the minimal couples-preference repair on top of
`ruro_occ_M0a_clean`. Two candidate specifications (`M0b1` and
`M0b2`) are defined, one is recommended as the first estimation to
run, and the others are sequenced as contingencies. This memo
does not commit to a YAML change; it is the design that the
implementation prompt will follow.

Inputs to this memo:
- `docs/RURO_occ_M0a_clean_verdict_v1.md`
- `reports/fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260514_102334.md`
- `docs/RURO_occ_M0a_clean_post_estimation_patch_report_v1.md`
- `docs/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md`
- `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml`
- `RURO_METHODS_AND_PIPELINE_MANUAL_v1.md`

---

## 1. Purpose of M0b

Repair the couples preference block of `ruro_occ_M0a_clean` so that
the model predicts a realistic joint household labour-supply
distribution. The target is to clear v4 contract §22 Gate B
(positive-semidefinite Hessian, all SEs finite, κ < 10⁷) and to
bring couples within-sample fit moments into a defensible range
(predicted participation within 2 pp of observed, predicted mean
hours within 5 of observed, L1 hours-bin distance below 1.0). This
is the single empirical task that stands between the project and
the welfare / decomposition stages.

M0b is identification repair on the preference side, parallel to
M0a (which was identification repair on the singles consumption
side). It is not a robustness extension. M1 — region dummies on the
opportunity layer — remains the next robustness step after M0b
clears its gates.

---

## 2. Why M0a-clean fails as a JMP baseline

Three concrete failure modes are now visible after the reporting
patch (they were partly hidden before). All three are concentrated
on couples and on the consumption block.

(a) **Couples predicted participation is 1.0000 against observed
0.972 (cou_m) and 0.965 (cou_f).** The structural V-decomposition
shows `V_work − V_nonwork ≈ +83` nats per partner. This is
mechanically driven by the preference utility `U`: the median
work-minus-nonwork gap in `U` alone is +91 (cou_m) and +97 (cou_f)
nats, with the opportunity layer netting to −17 and the prior
correction adding +8. Couples preferences, not opportunities,
drive the participation lock.

(b) **Couples predicted moments are extreme.** Mean predicted hours
59.7 (cou_m) and 59.6 (cou_f) against observed 41.6 and 35.6.
Mean predicted wages 139.9 and 140.1 EUR/h against observed 17.7
and 15.2. Predicted hours-bin distribution has 43% in 51-60 and
31% in 60+ for both partners, against observed 2-6% combined. L1
hours-bin distance is 1.70 (cou_f) and 1.43 (cou_m) out of a
maximum of 2.0 — near-maximal mismatch.

(c) **Singles consumption block has non-PSD covariance.** Even
after the proper rename to `theta_c_singles`, three preference
parameters return NA standard errors (`β_c_sm`, `β_c_sf`,
`θ_c_singles`) and ten correlation pairs exceed `|corr| = 1`. The
non-PSD signature is now in the consumption-σ block (couples
`β_c`, `θ_c`, and `σ` correlate with the singles consumption
parameters at magnitudes 1.02-1.27). The equality-constraint
fallback in M0a was suppressing rather than fixing this; M0a-clean
exposes that the underlying identification gap survives the rename.

(d) **Hessian remains indefinite**: 1 negative eigenvalue, min
= −4.47, κ = 9.94e9. The θ̂ is not a local maximum. Gate B2 fails.

The root cause of (a) and (b) is that couples `θ_c = +0.319`
makes consumption Box-Cox near-linear over the empirical range,
so a household-income difference between working and non-working
states produces an enormous utility gap. Compared to singles
`θ_c_singles = −0.836` (strongly concave), couples consumption
behaves under the current spec as if the marginal utility of
income is nearly constant — which empirically is implausible.
Without an offsetting mechanism on the leisure side, the model has
no way to predict joint non-work. The cause of (c) is partly
mechanical (the wage σ correlates with the consumption block
because both contribute to predicted disposable income on working
alternatives) and partly the same consumption-block over-fitting.

---

## 3. What M0b should fix

In order of priority:

(i) Couples predicted participation moves away from 1.0000 toward
observed 0.96-0.97.

(ii) Couples predicted mean hours moves from ~60 toward observed
36-42.

(iii) Couples L1 hours-bin distance drops from 1.7 to under 1.0.

(iv) Hessian negative-eigenvalue count drops from 1 to 0; κ drops
below 10⁷; Gate B2 passes.

(v) All preference standard errors are finite. Gate B3 passes.

(vi) The non-PSD correlations involving the consumption block
become consistent (all |corr| ≤ 1, ideally ≤ 0.95).

(vii) The wage and occupation opportunity blocks are unaffected.
These blocks were the cleanest part of M0a-clean and should remain
so.

---

## 4. What M0b must not change

Hard constraints on what M0b leaves untouched. Violating these
turns M0b into a much larger spec change and breaks the audit
trail from M0a-clean.

(a) **All opportunity blocks remain identical to M0a-clean.** No
region dummies, no occupation interactions, no conditional wage,
no conditional hours by occupation. The four opportunity blocks
`O^E + O^H`, `O^Market`, `O^W`, `O^Occ` retain the exact same
specification.

(b) **The proposal-density correction is identical.** No change to
how `log_prior` is computed, no change to the `−log(prior)`
subtraction, no change to the proposal-component aliases
(`log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`).

(c) **MNL parquet files are not regenerated.** Same data, same
draws, same EUROMOD-computed disposable income for every
alternative. The variable dictionary
(`docs/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md`) remains
authoritative.

(d) **Occupation does not enter utility.** The contract §20
exclusion restriction stands: `loc4` lives in `O^Occ` only.

(e) **Singles preferences are unchanged.** The repair is
strictly on the couples side. `β_c_sm`, `β_c_sf`,
`θ_c_singles`, `β_l0_sm`, `β_l0_sf`, `θ_l_sm`, `θ_l_sf`, and the
singles leisure shifters (`β_l_age_sm`, `β_l_age2_sm`,
`β_l_age_sf`, `β_l_age2_sf`, `β_l_nkids_sf`) are not touched. If
the singles consumption block's non-PSD covariance is also
resolved by M0b, that is a useful side-effect; M0b does not
target it directly.

(f) **The consumption variable `consumption` is shared at the
household level.** Couples have shared `consumption` and
partner-specific `leisure_male`, `leisure_female`. M0b does not
introduce per-partner consumption, an adult-equivalence scale, or
any household-composition shifter on consumption. (These are
candidate moves for `M0c` if M0b fails.)

(g) **No new leisure shifters on couples preferences.** No
child-age-band dummies (Capéau et al.'s `ch03`, `ch36`, `ch69`),
no partner-status interactions on age, no new region or education
terms in utility. The leisure shifters remain `β_l_age_m`,
`β_l_age2_m`, `β_l_age_f`, `β_l_age2_f`, `β_l_nkids_f` exactly as
in M0a-clean.

---

## 5. M0b1: leisure-leisure interaction only

The minimal repair. Add one parameter to couples utility.

**Mathematical form**:

```
U_couples = β_c · BC(C, θ_c)
          + β_l_m(Z_m) · BC(L_m, θ_l_m)
          + β_l_f(Z_f) · BC(L_f, θ_l_f)
          + β_ll · BC(L_m, θ_l_m) · BC(L_f, θ_l_f)
```

This follows the Capéau et al. (2015/16) Section 3.3 couples
utility, eq. (2). The term is symmetric in (L_m, L_f) and uses
the partner-specific Box-Cox exponents.

**Important sign-convention note.** With `θ_l < 0` (the M0a-clean
estimated values are around −0.7), `BC(L, θ_l)` is negative when
the partner works (`L < 1`) and zero at non-work (`L = 1`).
Therefore:

- both work: `BC(L_m) · BC(L_f) > 0` → interaction is +
- one works, one non-work: `BC × 0 = 0` → interaction is zero
- both non-work: `0 · 0 = 0` → interaction is zero

So positive `β_ll` makes joint-working **more** attractive than
additivity predicts (which is the opposite of what M0b is trying to
fix), and negative `β_ll` makes joint-working **less** attractive
(which is what we want). Capéau et al. label `β > 0` "leisure
complements" based on the cross-partial sign at an interior point;
this labeling is technically correct but counterintuitive at the
corners that matter for participation prediction. The M0b
implementation must allow `β_ll` to take either sign and not
mechanically expect a positive estimate.

**Initial value**: `β_ll = 0.0` (neutral, agnostic about sign).

**Bounds**: `[−2.0, 2.0]`. Capéau et al.'s estimate is `+0.206`;
allowing the estimator to find `β_ll` in [−2, 2] covers Capéau's
range with substantial room for a negative value if our data
prefers it.

**Total parameter count**: 47 + 1 = **48**.

**Expected outcome**: `β_ll` likely settles negative (the data has
strong joint-non-work events the model needs to explain), but
the magnitude may be small. Given that the M0a-clean U gap is
+91 nats and the interaction term at chosen-working alternatives
contributes only roughly `β_ll · BC(L_m, −0.7) · BC(L_f, −0.7)` ≈
`β_ll · (−1.2) · (−1.2)` ≈ `1.44 β_ll`, a `β_ll` of −1.0 would
contribute only ~−1.4 nats — far short of overcoming the 91-nat
consumption gap. **M0b1 alone is likely insufficient** to bring
couples predicted participation below 0.99. The value of running
M0b1 first is diagnostic: it isolates the contribution of the
interaction term, establishes a sign and magnitude estimate, and
confirms the implementation is correct before piling on the
second intervention.

---

## 6. M0b2: leisure-leisure interaction plus tighter couples θ_c bound

The more substantive repair. Adds the M0b1 parameter and
additionally tightens the upper bound on couples `θ_c`.

**Same `β_ll` term as M0b1**.

**Additional bound change**:

```yaml
# In optimization.bounds:
theta_c: [-8.0, 0.0]    # was [-8.0, 0.95]
```

This forces couples consumption Box-Cox to be at most logarithmic
(at `θ_c = 0` the BC limit is `log(C)`) and prevents the
near-linear curvature that drives the +91-nat consumption gap.
The new upper bound `0.0` is conservative: it does not pool
couples and singles consumption (singles `θ_c_singles` is
unbounded at ≤ 0.95, separately) and it does not force a specific
value — it only forbids the near-linear region.

**Initial value for `θ_c`**: keep at `−1.0` (the M0a-clean default).
At M0a-clean's converged θ̂ the optimizer drifted to `+0.319`; with
the new upper bound, the optimizer should settle somewhere in
`[−1.5, 0.0]`. Roughly speaking, if the couples consumption is
truly identified as logarithmic or more concave, the estimator
will find that interior value.

**Why upper bound 0.0 and not, say, −0.5?** Two reasons:

(i) Capéau et al. estimated `α_c = 0.610` for couples (their
α_c is our θ_c). That's quite linear too, so the literature
sometimes finds near-linear couples consumption. Forcing `θ_c ≤
−0.5` would over-restrict relative to literature norms. Upper
bound `0.0` is the natural natural-log barrier.

(ii) If `θ_c = 0` is the interior solution (i.e. log-utility on
consumption), that's a credible economic specification and we
should let the estimator find it.

**Total parameter count**: 47 + 1 = **48** (same as M0b1; the bound
tightening does not add or remove parameters).

**Expected outcome**: this is the configuration that should
mechanically reduce the U gap from +91 to roughly +20-40 nats,
which combined with the opportunity layer's −17 net contribution
and the prior correction's +8 should make `V_work − V_nonwork`
small enough that the model can produce 3-5% non-employment for
couples. Couples participation should drop from 1.0000 to roughly
0.96-0.98. Couples mean hours should drop from ~60 to ~40-45.

---

## 7. Recommended order of estimation

Run **M0b1 first**, then **M0b2** if M0b1 does not clear the
couples-fit criteria.

The conservative case for this ordering: M0b1 isolates the
contribution of the new parameter, lets us see the sign and
magnitude of `β_ll` cleanly, and provides a control comparison
for evaluating whether the bound change at M0b2 was decisive.
M0b1's likely failure (predicted by §5) is itself a useful result.

The cost of this ordering: one extra estimation cycle (~5 minutes
of compute). The benefit: cleaner attribution of which intervention
fixed which symptom.

**The exact first estimation to run** is M0b1 with the
following invocation:

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

`--warm-start none` is mandatory: M0a-clean's θ̂ is on the wrong side
of an indefinite Hessian and would drag M0b1 to a similar region.
At least three start points: spec defaults, spec defaults +
Gaussian perturbation (σ = 0.1 × bound-width), and a random
uniform draw within bounds.

If M0b1 fails the couples-fit gates (§16), run M0b2 with the same
invocation (path swapped to `estimation_spec_ruro_occ_M0b2.yaml`),
again from spec defaults.

---

## 8. Recommended baseline if both models work

If M0b1 alone fixes couples participation and clears Gate B
(unlikely but possible): **M0b1 is the next baseline**. Lower
parameter count is preferable when both specifications fit
comparably.

If M0b1 fails but M0b2 succeeds: **M0b2 is the next baseline**.

If both work but with materially different point estimates of
`β_c` and `θ_c` for couples: prefer **M0b2**, because (a) it has the
tighter identification, (b) the tighter `θ_c` bound is
literature-defensible, and (c) the larger fit gain on couples
justifies the bound restriction.

In any case, the chosen baseline must pass the gates in §16.
There is no version of "M0b succeeded therefore M1 is next" —
gate-passing is necessary, gate-passing plus fit improvement is
sufficient.

---

## 9. Parameters to add

One parameter, identical across M0b1 and M0b2:

| name | role | initial value | bounds |
|---|---|---|---|
| `beta_ll` | leisure-leisure interaction coefficient in couples utility | `0.0` | `[−2.0, 2.0]` |

The parameter is a scalar; it is not partner-specific, group-
specific, or interaction-specific. It enters only the couples
utility expression (singles utility has no leisure-leisure
interaction because singles have only one labour margin).

---

## 10. Parameters to restrict

M0b1 restricts none.

M0b2 tightens **one bound only**:

| name | old bound | new bound | reason |
|---|---|---|---|
| `theta_c` | `[−8.0, 0.95]` | `[−8.0, 0.0]` | forbid near-linear couples consumption Box-Cox |

No parameter is hard-fixed at a value. No parameter is removed
from the estimable vector.

---

## 11. Parameters to leave unchanged

Everything in M0a-clean except as above. Specifically all 47
M0a-clean parameters keep their M0a-clean YAML configuration:

- `beta_c, beta_c_sm, beta_c_sf` (consumption scales)
- `theta_c_singles` (singles consumption Box-Cox curvature, shared sm/sf)
- `beta_l0_m, beta_l0_f, beta_l0_sm, beta_l0_sf` (leisure intercepts)
- `theta_l_m, theta_l_f, theta_l_sm, theta_l_sf` (leisure Box-Cox curvatures)
- `beta_l_age_*, beta_l_age2_*, beta_l_nkids_*` (leisure shifters)
- `beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft` (employment + hours focal points)
- `beta_E_gsur, beta_E_educH` (market opportunity residual)
- `beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2, sigma` (wage opportunity)
- `beta_occ_2_*, beta_occ_3_*, beta_occ_4_*` (occupation opportunity, 12 params)

No changes to expression_constraints (the two `mul_cou_*_positive`
soft constraints from M0a-clean stay; no new constraint is added).
No changes to `gradient_verification` (still disabled).

---

## 12. Required YAML changes

Two new YAML files in `scripts/enhanced/`:

### `estimation_spec_ruro_occ_M0b1.yaml`

Copy `estimation_spec_ruro_occ_M0a_clean.yaml` and apply:

1. `specification.name: "ruro_occ_M0b1"`.

2. `specification.description`: update to describe the
   leisure-leisure interaction addition.

3. Add a new top-level block:

```yaml
couples:
  leisure_interaction:
    coefficient: "beta_ll"
```

The existing M0a-clean YAML has `couples: {}` (empty). Replace
that with the populated block.

4. In `initial_values`, add: `beta_ll: 0.0`.

5. In `optimization.bounds`, add: `beta_ll: [-2.0, 2.0]`.

No other changes.

### `estimation_spec_ruro_occ_M0b2.yaml`

Same as M0b1 with:

1. `specification.name: "ruro_occ_M0b2"`.

2. In `optimization.bounds`, change the existing line:

```yaml
theta_c: [-8.0, 0.95]
```

to:

```yaml
theta_c: [-8.0, 0.0]
```

---

## 13. Required parser / likelihood changes

The implementation prompt should make minimum-invasive changes to:

(a) **`scripts/enhanced/estimation_spec_parser.py`**: recognize the
`couples.leisure_interaction.coefficient` field. If the field is
present, append `beta_ll` to `spec.all_param_names` and store the
coefficient name on the spec object (e.g. as
`spec.couples_leisure_interaction = "beta_ll"`). If the field is
absent, the spec parses exactly as M0a-clean (no `beta_ll`).
This is a backward-compatible additive change.

(b) **`scripts/enhanced/gamspy_estimation_vectorized.py`**: add the
interaction term to the couples utility evaluation. The change
is at the point where couples `U` is constructed, after the
marginal leisure terms are added. Pseudocode:

```python
# After computing U_cm and U_cf marginal terms:
if spec.couples_leisure_interaction is not None:
    beta_ll = params[spec.couples_leisure_interaction]
    bc_l_m = box_cox(leisure_m, theta_l_m)
    bc_l_f = box_cox(leisure_f, theta_l_f)
    U_couples += beta_ll * bc_l_m * bc_l_f
```

The term is symmetric in m/f and is added once to the
household-level U (not twice, once per partner). The Box-Cox
applied is `(L^θ − 1) / θ` with the partner-specific θ_l, on raw
`leisure_male` / `leisure_female` (matching the variable
dictionary §4).

(c) **`scripts/enhanced/estimation_engine.py`** and
**`scripts/enhanced/gamspy_estimation.py`**: mirror the change
in (b) for any code path that recomputes couples utility outside
the vectorized engine. If only the vectorized engine is used by
`enh_RURO_estimate_FR.py --vectorized`, the other engines can be
updated for consistency but are not strictly required for the
M0b1 run.

(d) **Analytical gradient**: `optimization.analytical_gradient:
true` in the YAML. The gradient of `β_ll · BC(L_m) · BC(L_f)`
with respect to `β_ll` is `BC(L_m) · BC(L_f)`. With respect to
`θ_l_m`: `β_ll · BC(L_f) · ∂BC(L_m)/∂θ_l_m`. The implementation
must propagate this. If the analytical gradient cannot be cleanly
extended, the implementation prompt should switch to
`analytical_gradient: false` for M0b only as a defensive
fallback. (This is a documented allowed deviation, not a silent
change.)

---

## 14. Required post-estimation changes

The patched post-estimation reporter
(`scripts/enhanced/RURO_post_estimation_styled.py`) needs one
additional change: the couples utility reconstruction inside
`_add_predicted_probabilities` and any other V-computation path
must include the `β_ll · BC(L_m) · BC(L_f)` term when
`spec.couples_leisure_interaction` is set.

Specifically:

(a) **`_add_predicted_probabilities`** (around line 2880): the
couples branch currently builds `U_household` from `β_c · BC(C)`
plus the two partner-specific leisure terms. Add the interaction
term using the spec resolution: `if hasattr(spec,
'couples_leisure_interaction') and spec.couples_leisure_interaction
is not None: ...`.

(b) **The structural participation diagnostic
`Results/_participation_diag_ruro_occ_M0a_clean.py`**: this is the
reference V reconstruction used for the 1e-14 cross-check. It
must also gain the `β_ll` term so the cross-check at M0b
continues to validate the reporter. Save the updated diagnostic
as `Results/_participation_diag_ruro_occ_M0b1.py`.

(c) **`compute_marginal_utilities_at_chosen`**: this currently
uses the legacy `compute_beta_l_full` without spec. For M0b, it
must also extend to include the interaction in MUL computation
for couples. (MUL_m gains a `β_ll · BC(L_f) · ∂BC(L_m)/∂L_m`
contribution.) If this is too invasive at this step, the M0b
LLM summary's "marginal utility diagnostics" panel may report
slightly stale numbers — flag this in the patch report rather
than silently ship.

---

## 15. Diagnostics required after estimation

After M0b1 (and after M0b2 if run), the diagnostic battery is:

(a) **Standard low-token LLM summary** via
`RURO_post_estimation_styled.py --compute-se`. Compare line by
line against M0a-clean's
`reports/fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260514_102334.md`.

(b) **Patched-reporter fit check** via
`Results/_M0b1_post_est_fit_check.py` (analogue of the
M0a-clean script). Confirm the cross-check between
patched reporter and structural diagnostic still holds within
1e-14 on the 100-household sample.

(c) **Participation V-decomposition** via the updated
`Results/_participation_diag_ruro_occ_M0b1.py`. Report
component-wise `V_work − V_nonwork` per group, focusing on:
- the couples `U` gap (must drop from +91 toward +20-40 in M0b2)
- the couples `O_W` and `O_market` gaps (unchanged from M0a-clean)
- the new contribution from the `β_ll · BC(L_m) · BC(L_f)` term
  to the work-nonwork V gap

(d) **Cross-spec comparison table** of M0a-clean vs M0b1 (vs
M0b2): joint LL, n_params, n_negative_eigenvalues, κ, n_NA_SE,
predicted participation per group, predicted mean hours per group,
L1 hours-bin distance per group, `β_ll` estimate and SE,
`θ_c` estimate (especially relative to its bound in M0b2),
top-10 |corr| pairs.

(e) **Bound-binding check on `θ_c` for M0b2**: confirm `θ_c`
settles strictly interior, not at the new upper bound of `0.0`.
If `θ_c` hits the bound, it is a sign that the data wants the
near-linear region that M0b2 forbids, and the next move (M0c)
should be re-evaluated.

---

## 16. Pass/fail criteria

Three gates evaluated in order on M0b1 (and on M0b2 if run).

### Gate A — Spec, parse, smoke test

| check | required |
|---|---|
| `spec.name = "ruro_occ_M0b1"` (or `_M0b2`) | yes |
| `n_estimated_params = 48` | yes |
| `'beta_ll' in spec.all_param_names` | yes |
| likelihood is finite at initial values | yes |
| gradient norm at initial values is finite | yes |

### Gate B — Estimation (the hard gates)

Strict thresholds from the v4 contract §22:

| check | threshold |
|---|---|
| solver status | `OptimalLocal` or equivalent |
| n_negative_Hessian_eigenvalues | `0` |
| Hessian condition number `κ` | `< 10⁷` |
| smallest \|eigenvalue\| | `> 10⁻⁸` |
| n_parameters_with_NA_SE | `0` |
| n_parameters_at_strict_bound | `0` |
| cross-engine `joint_ll` agreement | `< 10⁻⁶` per obs |

### Gate F — Fit (couples-specific, which is the whole point)

| check | threshold |
|---|---|
| couples predicted participation (cou_m) | `< 0.99` |
| couples predicted participation (cou_f) | `< 0.99` |
| couples predicted mean hours (cou_m) | `< 50` |
| couples predicted mean hours (cou_f) | `< 50` |
| L1 hours-bin distance (cou_m) | `< 1.0` |
| L1 hours-bin distance (cou_f) | `< 1.0` |
| `p_chosen_min` (whole sample) | `> 10⁻¹⁰` |

The pre-existing singles fit moments should not regress. If
predicted singles participation moves outside `[obs ± 0.03]` or
singles L1 hours-bin distance jumps above 1.0, that is a
**REGRESSION**, not an improvement, and the M0b YAML implementation
must be reviewed.

### Pass/fail decisions

- **M0b1 passes Gate A + B + F**: declare M0b1 as next baseline.
  Proceed to M1.
- **M0b1 passes A + B, fails F**: proceed to M0b2.
- **M0b1 fails B (Hessian still indefinite)**: proceed to M0b2;
  the bound change in M0b2 is what is actually fixing the
  consumption block, and M0b1's bound was insufficient.
- **M0b2 passes A + B + F**: declare M0b2 as next baseline.
  Proceed to M1.
- **M0b2 passes A + B, fails F**: escalate. Most likely M0c is
  needed (global `θ_c` pool: `θ_c_singles = θ_c`, or a separate
  adult-equivalence scale on couples consumption).
- **M0b2 fails B**: escalate. The non-PSD signature is deeper than
  the consumption-block-only repair can fix. Possible next moves:
  (i) drop one of the high-correlation pairs, e.g. fix
  `θ_l_m = θ_l_f`; (ii) pool `β_c` globally across all four
  groups; (iii) write a supervisor memo before further code work.

---

## 17. What remains postponed to M1

The v4 contract roadmap places M1 (region opportunity), M2 (`loc`
fine occupation), M3 (occupation-conditional wage), M4
(occupation-conditional hours), M5 (richer couples preferences),
M6 (further robustness) after the M0 family is stable. M0b is
strictly between M0a-clean and M1. The following items remain
postponed until M0b clears Gate B and Gate F:

- **M1 region dummies on `O^E + O^H`**: location-driven
  opportunity heterogeneity. The whole point of M1 is to test
  whether residential location matters for opportunity even after
  controlling for individual characteristics. Running M1 on a
  spec whose couples preference block is broken would attribute
  the broken-couples-prediction variance to region by accident.

- **M2 fine occupation (`loc` instead of `loc4`)**: 9 ISCO codes
  instead of 4 task-content groups. Higher parameter count, finer
  occupation-opportunity coefficients. Defer until M1 has shown
  whether region matters, since region and occupation interact in
  the French labour market.

- **M3 occupation-conditional wage**: separate Mincer means by
  occupation. Real economic content, but contaminated if the
  preference block is unstable.

- **M4 occupation-conditional hours**: separate focal points by
  occupation. Same argument.

- **Recovery test**: Monte Carlo simulation from a true `θ⁰` to
  verify the estimator can recover it. Expensive (≥ 12 hours
  compute for 50 replications). Wasted compute if the spec is
  about to change again.

- **Seed stability**: re-estimate with two alternative draw
  seeds, check parameter-level max-diff < 5%. The current draws
  are sufficient for M0b purposes.

- **Welfare scaffolding on real data**: defer until M0b passes.
  Develop the welfare code against a synthetic θ⁰ (e.g. from a
  recovery test) so the code is ready to plug in when a credible
  θ̂ becomes available.

- **Capéau-style elasticity tables**: postpone until M0b clears
  Gate F. The tables are only meaningful if the model fits the
  joint distribution of hours and participation.

- **Slides, supervisor figures, abstract numbers touching
  couples**: any externally-facing artifact about couples
  participation, hours, wages, occupation, or decomposition
  remains blocked until M0b passes.

The first M1 task — once M0b passes — will be a small data-side
check: confirm the EUROMOD region variable `drgn1` (NUTS-1) is
present in the singles and couples parquets and has expected
French region values. If it is, M1 is one YAML addition; if it is
not, the MNL prep pipeline needs a small extension first.

---

## Suggested filename

Save this memo as: `docs/RURO_occ_M0b_design_memo_v1.md`
(category: technical memo / design).
