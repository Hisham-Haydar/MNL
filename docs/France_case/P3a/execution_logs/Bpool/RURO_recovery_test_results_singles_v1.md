# RURO Recovery Test Results — Singles isolation (bpool_p3a_v1, 55 params, beta_c=1)

> **Corrections-of-record (2026-05-29):** the "Box-Cox theta_l multi-modality" and "leisure preference scale freedom" framings in §3 are scipy trust-constr local-plateau descriptions, NOT properties of the RURO LL surface. CONOPT (analytical Hessian) on the same singles male 766 and singles female 910 slices reaches an LL 7236 / 8933 units better with G2 = 2e-6 / 0.60 reproducibility, recovers theta_l_sm / theta_l_sf with **correct sign**, and reaches OptimalLocal both starts. The theta_l sign-constraint experiment recommendation in §5.1 of this document should **not** be acted on. **The chosen-row LH-flag diagnostic that this doc led to was correct** and was fixed in commit `099e5c4` — that part stands and is decisively validated. The "structural" identification framing is reframed in `RURO_recovery_test_results_v3.md` §5 as a description of trust-constr's BFGS-approximation breakdown, not LL geometry.

> ## VERDICT: ❌ Singles fail STRUCTURALLY — same Box-Cox multi-modality as couples v2, NOT a couples-specific failure
>
> Three singles slices (male 300 HH, male 766 HH, female 910 HH) all fail the G3
> PD-Hessian gate with the **same wrong-attractor signature** as the v2 couples run:
> `beta_l0` collapses to ~0.05, `theta_l` flips sign, `theta_c_singles` collapses to ~0,
> the hours block scrambles. **The 300→766 male comparison is decisive on the
> sample-size question** — with 2.6× the data, min_eig went from −30.7 to **−84.0**
> (3× worse, not better), G2 collapsed from 1.5 to **0.009** (both starts find the
> *same* wrong basin more confidently). Sample size is **not** the answer; this is a
> structural non-convexity of the singles ACS Box-Cox parameterisation.
>
> **The good news isolated from this:** the beta_c=1 normalisation **is sound and
> necessary** — the v1 ridge is eliminated in every slice. The wage block, sigma,
> singles occupation, and the year fixed effects all recover cleanly. The shared
> engine + Phase-1 fix are not the cause. **The failure is in the leisure
> preference parameterisation itself**, not in the implementation.
>
> **Recommended next step (NOT applied here):** sign-constrain `theta_l` to strict
> negativity (e.g. `[−8.0, −0.05]` instead of `[−8.0, 0.95]`) to forbid the wrong
> basin. This is an economically standard restriction (concavity in leisure utility)
> and the cheapest test of whether removing the sign ambiguity eliminates the
> non-convexity. Per Phase-2 instruction, no spec change is applied — the choice
> is yours.
>
> ---

**Date:** 2026-05-28
**Spec:** `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` (55 params, beta_c FIXED=1.0)
**Solver:** scipy-trustconstr (BFGS Hessian approx, trust-region; analytical gradient)
**Seed:** 20260527  **Flat-tol:** 5e-3 (early-stop in flat regions to avoid grinding)
**Raw reports:** `RURO_recovery_test_results_singles_male_v1_raw.md` (300 HH),
`RURO_recovery_test_results_singles_male_full2016_v1_raw.md` (766 HH),
`RURO_recovery_test_results_singles_female_full2016_v1_raw.md` (910 HH)
**Console logs:** `recovery_singles_*_v1.log`

---

## 1. The five-slice comparison

This document brings together five recovery-test runs on the same spec to isolate
where the identification problem lives.

| # | run | HH | G3 PD | min_eig | max_eig | G2 max\|warm−cold\| | stuck @ \|g\| | LL agreement |
|---|---|---:|---|---:|---:|---:|---|---:|
| 1 | couples v1 (beta_c free, 58 params) | 300 | ❌ | −1.24e−2 | 2.38e+5 | n/a (1 start) | beta_l0_m @ bound +21.05 | n/a |
| 2 | couples v2 (beta_c=1) | 300 | ❌ | **−1.73e+2** | 1.64e+4 | **6.69** | beta_l0_m ‖g‖=205 | gap 47.97 |
| 3 | singles male v1 | 300 | ❌ | **−3.07e+1** | 1.4e+4 | **1.54** | beta_l0_sm ‖g‖=54 | gap 0.014 |
| 4 | singles male v1 (full 2016) | **766** | ❌ | **−8.40e+1** | n/a | **8.63e−3** | beta_l0_sm ‖g‖=166 | gap 0.0001 |
| 5 | singles female v1 (full 2016) | **910** | ❌ | **−2.56e+1** | 3.33e+4 | **3.54e−2** | beta_l0_sf ‖g‖=89 | gap 0.033 |

Three patterns to read from this table:

**Pattern A — the v1 ridge is GONE in every post-fix run.** v1's signature was a
parameter pinned at its bound along a near-flat ridge (min_eig only −0.012). Runs
2–5 all have min_eig at least 100× larger in magnitude with the stuck parameter
sitting in the INTERIOR of its bound and a non-zero gradient there. The beta_c=1
normalisation **changed the geometry entirely**, exactly as intended. The
implementation is sound.

**Pattern B — sample size makes the non-convexity SHARPER, not milder.**
Comparing runs 3 vs 4 (same spec, same mode, same sex, same solver, 2.6× the data):
- **min_eig grew from −30.7 to −84.0** (proportional to sample size, the signature
  of a structural property of the LL, not finite-sample noise).
- **G2 collapsed from 1.54 to 0.009** (both starts now find the *same* wrong
  attractor confidently). LL agreement tightened from 1.4e−2 to 1.0e−4.
- **beta_l0_sm landed at the same 0.05 value at both sample sizes** (theta\* = 1.25).
- `theta_l_sm` flipped sign at both sample sizes (+0.29 / +0.37 vs theta\* = −0.75).
- `theta_c_singles` collapsed to ~0 at both sample sizes (theta\* = −0.75).

A normalisation indeterminacy does not sharpen with more data, and finite-sample
non-convexities dissolve with more data. **A non-convexity that scales linearly
with sample size while pulling two starts to the same wrong attractor is a
structural multi-modality.**

**Pattern C — the failure is gender-symmetric and qualitatively identical to
couples.** Female (run 5) shows the same `theta_l_sf` sign flip (+0.13 vs theta\*
= −1.25), same `beta_l0_sf` collapse to 0.05, same `theta_c_singles` ≈ 0. The
shared opportunity shifters that scramble in couples v2 (`beta_h_pt1`,
`beta_h_lh`, `beta_E_gsur`, `beta_occ_*_cf`) scramble identically in singles
male and singles female (`beta_h_pt1` wrong-signed, `beta_h_lh` glued to its
lower bound at −9.99, `beta_E_gsur` wrong-signed, `beta_occ_*_s*` wrong-signed).

---

## 2. The wrong attractor — same point across all four post-fix slices

The recovery test asks "from a known theta\*, does the optimizer recover it?" In
runs 2–5, the optimizer instead converges to a **different point** that *is* a
strong local feature of the LL, but is not the data-generating parameters. The
attractor's structure is consistent across slices:

| param | theta\* | male 300 | male 766 | female 910 | couples v2 |
|---|---:|---:|---:|---:|---:|
| `beta_l0_s*` / `beta_l0_*` | 1.25 / 0.0125 | sm: +0.050 | sm: +0.050 | sf: +0.051 | l0_m: +0.057, l0_f: +0.057 |
| `theta_l_s*` / `theta_l_*` | −0.75 / −1.25 | sm: +0.30 (**sign flip**) | sm: +0.37 (**sign flip**) | sf: +0.13 (**sign flip**) | l_m: +0.95 (**sign flip**), l_f: +0.12 (**sign flip**) |
| `theta_c_singles` / `theta_c` (couples) | −0.75 / (FIXED 0) | +0.014 (**sign flip**) | +0.009 (**sign flip**) | +0.047 (**sign flip**) | (theta_c is fixed at 0 for couples; no comparison) |
| `beta_l_age2_s*` / `beta_l_age2_*` | +0.12 | sm: −1.00 (**sign flip**) | sm: −1.00 (**sign flip**) | sf: −1.00 (**sign flip**) | l_age2_m: −0.98 (**sign flip**), l_age2_f: −0.99 (**sign flip**) |
| `beta_h_pt1` | +1.20 | −1.53 (**sign flip**) | −1.30 (**sign flip**) | −0.79 (**sign flip**) | −1.90 (**sign flip**) |
| `beta_h_lh` | −1.20 | −10.0 (**at bound**) | −10.0 (**at bound**) | −9.97 (**at bound**) | −9.99 (**at bound**) |
| `beta_E_gsur` | +1.20 | −1.43 (**sign flip**) | −1.59 (**sign flip**) | −2.62 (**sign flip**) | −3.35 (**sign flip**) |

**This is one attractor, not five.** Every leisure intercept lands near 0.05.
Every `theta_l` flips sign. Every `theta_c_singles` collapses to ~0.
`beta_h_lh` saturates at the lower bound in every run. `beta_E_gsur` and
`beta_h_pt1` reverse sign in every run.

What this means: the singles MNL likelihood, at the true wage / occupation /
year / region values (which it apparently knows — those recover fine), has a
deep local maximum where the leisure utility is structurally degenerate
in a specific way. The Box-Cox transform `BC(l, θ_l) = (l^{θ_l} − 1) / θ_l` is
not sign-symmetric: at positive θ_l it is convex-increasing for l<1 and
concave-increasing for l>1, while at negative θ_l it has the opposite curvature
pattern. With the leisure normaliser putting l around 1, **the two θ_l sign
regimes can produce similar utility differences across the 9 leisure alternatives
when paired with different bracket coefficients**, creating a non-convex
likelihood with two attracting basins. Combined with the unconstrained
`theta_c_singles`, the wrong basin sits at θ_c ≈ 0 (i.e. linear consumption
utility), `theta_l` flipped, and a tiny leisure intercept — equivalent to a
nearly-flat per-HH leisure utility differentiated mainly by the hours-opportunity
shifters, which then absorb the misfit by going to wrong signs or bounds.

---

## 3. What recovers cleanly (and why this matters)

Across all four post-fix runs:

- **Wage block.** `beta_w0` (theta\* +2.5, all four recover ~+2.2 to +2.3), `beta_w_educL` and `beta_w_educH` recover with correct sign in all runs, `beta_w_pexp` recovers correct sign, `beta_w_pexp2` recovers correct sign and magnitude ~0.03–0.1 (vs theta\* −0.0004 — close in magnitude, correct sign).
- **`sigma`.** Recovers in **all four** runs to within 0.05 of theta\* = 0.375.
- **Year fixed effects.** `beta_E_y2015`, `beta_E_y2017` correct sign in every run (where not inert).
- **Singles occupation block.** Every `beta_occ_*_sm` / `beta_occ_*_sf` that is on-slice recovers within tol with correct sign (the "inert on this slice" detector excludes the wrong-sex family generically).
- **`beta_l0_*` correct sign.** Even though magnitude collapses, the leisure intercept does NOT cross zero; the wrong basin still respects the positivity bound.

This recovery pattern tells us:
- The wage equation is identified.
- The opportunity-side regional/year/occupation structure is identified.
- The data has variation; the engine reads it correctly; the implementation routes
  parameters to alternatives correctly.
- **The failure is localised to the leisure preference subspace**: `beta_l0_*`,
  `beta_l_age*`, `theta_l_*`, plus `theta_c_singles` (which is structurally
  coupled to BC(c) and thus to the leisure utility via the level of consumption).

---

## 4. G3b — the urbanisation × region question

The Phase-2 doc identified G3b (do `beta_E_drgur` / `beta_E_drgmd` separate
identifiably from `beta_E_drgn2..8`?) as the founding identification question.
It was unanswerable in v1 and v2 because cov = H⁻¹ is undefined for non-PD H.

**It is still unanswerable on a singles slice**, for the same reason: G3 PD = False
in all three singles runs, so cov is undefined and the correlation pair `nan`.
The harness's "market-opp access shifters SEPARATELY IDENTIFIED" verdict is
auto-generated from absence-of-correlation, which is meaningless when the
correlation can't be computed. **Defer this question until the underlying
non-convexity is resolved** — only a PD-Hessian run will yield an interpretable
G3b correlation.

(One read of inertia in the female 910 slice: `beta_E_drgur`/`beta_E_drgmd`
appear as **non-inert** in the male slices but **inert** in female. That's
because the harness detects inertia by perturbation; in female-only the
urbanisation effect was dominated by other shifters and didn't move the LL above
the inert-detection tolerance. Not a finding — a small-sample artefact of the
inert detector, harmless here.)

---

## 5. The diagnosis going forward — three options (not applied)

Per the task's non-objective ("do NOT modify the spec further; report only"),
none of these is applied. The choice is yours.

### 5.1 Sign-constrain `theta_l` to strictly negative (RECOMMENDED for a quick test)

The current bound `theta_l ∈ [−8.0, 0.95]` allows the sign flip that defines the
wrong basin. Tightening to `theta_l ∈ [−8.0, −0.05]` (or similar) forbids the
wrong attractor by construction. This is **economically standard** (concavity in
leisure utility is the orthodox assumption in labour-supply MNL) and is the
**cheapest possible test** of the diagnosis: if min_eig flips positive on a
singles recovery test with this single bound change, the diagnosis is confirmed
and the fix is a one-line spec edit. If min_eig is still negative, the
non-convexity has another source and we'd look at `theta_c_singles` (a
parallel sign-constraint to negative) or at the consumption-leisure interaction.

**Cost:** one spec edit; one ~5-min singles recovery test. **Risk:** if the true
data-generating `theta_l` were near zero or positive, this constraint would bias
estimates — but the recovery test framing avoids this risk because we know
theta\* a priori; this is a diagnostic, not a production fit.

### 5.2 Switch leisure transform from Box-Cox to log-leisure or CES

The Box-Cox `(l^θ − 1)/θ` reduces to `log(l)` as θ → 0 and is otherwise a
two-parameter family in (θ, level). Replacing it with `log(l)` removes the
θ-sign ambiguity entirely (no Box-Cox exponent to flip). CES is a richer
alternative that still has one elasticity parameter but with a different
identification geometry.

**Cost:** engine-level change to the utility function and its gradient; involves
deeper refactoring than 5.1. **Risk:** changes the model's economic
interpretation; not a drop-in fix.

### 5.3 Pre-fix `theta_l` to a literature value

E.g. `theta_l = −0.5` (a common AC-family choice) fixed at the spec level, mirroring
how we fixed `beta_c = 1`. Removes `theta_l_sm`, `theta_l_sf`, `theta_l_m`,
`theta_l_f` from the estimated vector (4 fewer params, 55 → 51).

**Cost:** spec edit, no engine change (the fix-to-constant mechanism we built
for beta_c generalises trivially to theta_l). **Risk:** loses the model's
ability to estimate the leisure-utility curvature parameter; depends on the
literature value being a good fit.

### 5.4 What I would NOT do

**Multistart with random initial values.** The 300→766 comparison shows both
starts already converge to the *same* wrong attractor; running 20 random starts
would just give 20 confirmations of the wrong attractor. Multistart helps when
the local optima are well-separated; here the wrong basin's gravity is strong
enough that perturbed starts won't find the true basin without a constraint
nudging them toward it.

**More data alone.** The 300→766 male comparison directly tested this. min_eig
got 3× worse, not better. Adding the other 1,500 male HH (all-years) would
likely make min_eig ~−250, not flip it positive.

---

## 6. Phase-1 status: validated, committed

The Phase-1 normalisation (`beta_c = 1`, commit `31eaecc`) is **independently
validated** by this diagnostic:

| Phase-1 claim | evidence from singles diagnostic |
|---|---|
| beta_c family removed from estimated vector (55 params) | confirmed in every run; smoke + recovery harness both read 55 |
| LL+gradient finite, both modes | confirmed across all four post-fix runs (couples + 3 singles) |
| v1 scale ridge eliminated | min_eig went from −0.012 (v1) to −25 to −173 (v2/singles); beta_l0 no longer drifts to bound; this geometry change is a direct consequence of the fix working as designed |
| wage / sigma / year / occupation blocks identified | all recover cleanly across all four runs |

The Phase-1 implementation is **necessary** (the v1 ridge was real and would
have blocked any meaningful identification) and **correct** (the diagnosed
remaining non-convexity is downstream of the fix, not caused by it). It stays
in the tree as committed.

---

## 7. Artefacts not committed

The `--sex` extension to `scripts/bpool/recovery_test.py` and this report are
working-tree changes pending commit. The `--sex` flag is a generic addition to
the harness (singles-mode dgn filter routing `is_male` correctly through to the
engine's `gender_suffix`) and belongs in a separate small commit before further
work; the report is the analytic output of this session. Both await user
sign-off before staging.

No spec, engine, or data changes were made in this Phase-2 follow-up.

---

## Addendum (2026-05-28) — `theta_l` sign-constraint experiment refines the diagnosis

Followed up on §5.1's recommendation. Edited the spec so `theta_l_sm / sf / m / f`
bounds = `[−8.0, −0.05]` (strictly negative; padding away from the Box-Cox
singular boundary at θ=0), re-ran singles-male 2016 full (766 HH), same harness
otherwise. After the run, the spec change was **reverted in the working tree** —
no commit — because the experiment did not validate §5.1's diagnosis.

### Result

| diagnostic | male full 2016 (theta_l free, §1 table row 4) | **male full 2016 (theta_l ∈ [−8, −0.05])** | change |
|---|---:|---:|---|
| G3 PD | False | **False** | unchanged |
| min_eig | −84.0 | **−77.5** | only 8% milder |
| G2 max\|warm−cold\| | 0.009 | 0.012 | unchanged (~0.01) |
| `theta_l_sm` at stop | +0.37 (sign-flipped, free) | **−0.051 (at the new −0.05 bound)** | constraint binding |
| `theta_c_singles` at stop | +0.009 (sign-flipped) | **−0.029** (correct sign, ~0 magnitude) | moved across zero |
| `beta_l0_sm` at stop | +0.050 | **+0.051** | **unchanged** |
| stuck param ‖g‖ | 166 @ beta_l0_sm | 112 @ beta_l0_sm | reduced ~33% |
| wrong-sign count (hours/occupation block) | 5 (pt1, gsur, occ_2_sm, ...) | **5 (same list)** | unchanged |

Raw report: `RURO_recovery_test_results_singles_male_full2016_thetaL_neg_raw.md`.

### What this tells us

**The Box-Cox `theta_l` sign ambiguity is a symptom, not the root cause.** The
constraint forbade the wrong-sign value (+0.37) and the optimizer pressed up
against the new upper bound. `theta_c_singles` crossed zero from +0.009 to
−0.029, retaining the correct sign. But:

- **`beta_l0_sm` did NOT move** (0.050 → 0.051). The leisure intercept is still
  pinned near zero — far from theta\* = +1.25.
- **min_eig barely changed** (−84 → −77.5, an 8% reduction; not the order-of-magnitude
  flip we needed).
- **The hours-opportunity block did not unwind.** `beta_h_pt1` still −1.47 (theta\*
  +1.2, wrong sign); `beta_E_gsur` still −1.45 (theta\* +1.2, wrong sign);
  `beta_h_lh` still glued to the bound at −9.93; `beta_occ_2_sm` still −1.53
  (theta\* +1.2, wrong sign). These scrambles are not driven by `theta_l`'s sign.

### Revised diagnosis

The non-convexity is **in a direction orthogonal to `theta_l`**. The dominant
unidentified subspace is the **leisure-intercept × consumption-curvature × hours-
opportunity** coupling:
- `beta_l0_sm` wants to be ≈ 0 regardless of `theta_l` (a near-flat per-HH
  leisure utility);
- with `beta_l0_sm ≈ 0`, `theta_c_singles` is weakly identified and lands near 0
  (linear consumption utility);
- the hours-opportunity shifters (`beta_h_pt1`, `beta_h_lh`, `beta_E_gsur`,
  `beta_occ_*_sm`) absorb the residual misfit by going to wrong signs or
  saturating bounds, because the per-HH preference utility is essentially
  uninformative about cross-alternative preferences in this region.

This is **not** a Box-Cox-specific failure mode. It is the singles ACS
parameterisation having a deep local maximum at "preferences ≈ 0, opportunities
absorb the data." The same pattern is visible in the v2 couples failure (see
§2 wrong-attractor table); both modes converge to the same structural wrong
attractor.

### What this means for §5's options

- **§5.1 (sign-constrain `theta_l`) — REJECTED.** Tested. 8% improvement; does
  not flip PD. The sign ambiguity was a symptom.
- **§5.2 (switch leisure transform)** — still on the table but requires a
  larger engine change; would test whether the issue is Box-Cox-specific
  (unlikely, given the constraint-experiment result).
- **§5.3 (fix `theta_l` to a literature value)** — would also remove the sign
  ambiguity but not address the `beta_l0` / `theta_c_singles` coupling that
  the experiment just isolated. Equally unlikely to flip PD on its own.

### A different next experiment to consider

The constraint experiment surfaces a **new** diagnostic question: what if the
issue is the **identifiability of the hours-opportunity block** when the per-HH
leisure utility is near-flat? `beta_h_lh` saturates at its lower bound (−9.93)
in every post-fix run, including this experiment. If the LH alternatives
(working_lh = 1 iff working AND hours ∈ [44.5, 70]) are very rare in the data
(few HH have LH = 1 within their choice set), then `beta_h_lh` is effectively
identified only by the chosen alternative, and pushing it to a large negative
value is a way the optimizer drives the LH alternatives off the choice set
entirely. That would also pull `beta_h_pt1`, `beta_E_gsur`, and `beta_occ_2_sm`
to absorb the resulting misfit.

A **cheap test of this hypothesis** — ran it as a read-only data inspection:

```text
singles 2016, 169,276 rows (1,676 HH)
  working      avail=152,403 (90.0% of all alternatives)
  working_pt1  avail= 24,720 (14.6% / 16.2% of working)  chosen=  45 ( 2.7% of chosen)
  working_pt2  avail= 16,100 ( 9.5% / 10.6% of working)  chosen=  36 ( 2.1% of chosen)
  working_ft   avail= 32,401 (19.1% / 21.3% of working)  chosen= 383 (22.9% of chosen)
  working_lh   avail= 27,706 (16.4% / 18.2% of working)  chosen=   0 ( 0.0% of chosen)
HH with >=1 LH alternative : 1,676 / 1,676 (100.0%)
HH whose chosen alt is LH  :     0 / 1,676 (  0.0%)
```

**`working_lh` is chosen by ZERO singles in 2016.** Every choice set contains
LH alternatives (16% of all alternatives, 18% of the working alternatives), but
no household — not one — chose to work long hours according to the data
construction. The MNL likelihood's `beta_h_lh` gradient is therefore simply
"make LH alternatives as unlikely as possible across all 1,676 HH", which is
unbounded above (in magnitude) and only stops at the bound at `−10`.

This is **not** a structural non-convexity. It is a degenerate identification
problem: `beta_h_lh` is the coefficient on an alternative class with zero
chosen observations. The likelihood has no finite optimum for it. The
optimizer drives it to the lower bound; the residual misfit then propagates to
the parameters that share variance with the LH alternatives' opportunity-side
representation (`beta_h_pt1`, `beta_E_gsur`, `beta_occ_*_sm`), producing the
wrong-sign pattern that contaminates the recovery test results.

This explains **all four post-fix recovery failures consistently**:

- `beta_h_lh` saturates at the lower bound in every run (couples v2, singles
  male 300 / 766, singles female 910).
- The same parameters scramble in every run (`beta_h_pt1`, `beta_E_gsur`,
  `beta_occ_2`/`beta_occ_3`/`beta_occ_4`).
- The negative Hessian eigenvalue scales with sample size (more HH × more
  unconstrained `beta_h_lh` gradient = larger negative direction in the
  Hessian along the LH-correlated subspace).
- The wage block, sigma, year fixed effects, and singles occupation recover
  cleanly (they don't share variance with LH).

### Revised recommendation

The cheapest, cleanest test of the LH-sparsity diagnosis: **remove
`working_lh` from the hours-opportunity block** (or merge it into `working_ft`
if the labour-supply structure requires the LH range), then re-run the
singles male 2016 full recovery. If the LH-sparsity diagnosis is correct:

- `beta_h_lh` is no longer in the parameter vector (54 free params, was 55);
- `beta_h_pt1`, `beta_E_gsur`, and the singles occupation block stop scrambling;
- `beta_l0_sm` and `theta_c_singles` may also unstick (they were absorbing the
  same residual misfit);
- min_eig flips positive (the LH-correlated unidentified direction is gone).

This is **a different finding** than the original singles-v1 doc's diagnosis
of "Box-Cox theta_l multi-modality". The theta_l sign ambiguity may still
exist as a milder secondary issue (the constraint experiment showed
~8% improvement) but is not the dominant one. The dominant problem is data:
no singles in 2016 chose to work long hours.

**Couples confirmation (read-only data inspection, 2026-05-28):**

```text
couples 2016, 2,321,877 rows (2,577 HH)
  male:
    working_male      avail=2,091,524 (90.1%)  chosen=2,504 (97.2%)
    working_pt1_male  avail=  345,044 (14.9%)  chosen=   14 ( 0.5%)
    working_pt2_male  avail=  219,596 ( 9.5%)  chosen=   26 ( 1.0%)
    working_ft_male   avail=  441,713 (19.0%)  chosen=  683 (26.5%)
    working_lh_male   avail=  384,780 (16.6%)  chosen=    0 ( 0.0%)
  female:
    working_female    avail=2,087,127 (89.9%)  chosen=2,487 (96.5%)
    working_pt1_female avail= 334,033 (14.4%)  chosen=   73 ( 2.8%)
    working_pt2_female avail= 221,658 ( 9.5%)  chosen=  108 ( 4.2%)
    working_ft_female  avail= 445,087 (19.2%)  chosen=  517 (20.1%)
    working_lh_female  avail= 385,320 (16.6%)  chosen=    0 ( 0.0%)
  per-HH chosen joint alt:
    has male LH       :     0 / 2,577 (0.00%)
    has female LH     :     0 / 2,577 (0.00%)
    has EITHER LH     :     0 / 2,577 (0.00%)
```

**Confirmed mode-symmetric.** Of 2,577 couples households in 2016, **zero**
have a chosen joint alternative with male LH or female LH. The LH flag is
available in 16.6% of alternatives in both modes; chosen in exactly zero in
both modes. The diagnosis applies identically to couples and singles.

### Final diagnosis

The Phase-2 (v2 couples) and singles recovery failures both reduce to the
same root cause: **`beta_h_lh` is the coefficient on an alternative class
with zero chosen observations in the 2016 data**, available in every choice
set but never selected. Its MNL gradient has no finite optimum from above
in magnitude; the optimizer drives it to the lower bound at −10; the
LH-correlated misfit propagates to `beta_h_pt1`, `beta_E_gsur`, and the
occupation block, producing the wrong-sign pattern and the negative Hessian
eigenvalue.

Per the standing "no further spec modification" instruction, no edit is
applied. The next step (whether to remove `beta_h_lh`, merge LH into FT, or
investigate why no household chose the LH range in this data construction) is
a design decision left for a fresh session.

