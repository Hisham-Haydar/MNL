# Joint Pooled RURO Estimation - Design Memo

**Project:** Unequal Job Opportunities and Well-Being Inequality (JMP)  
**Status:** design settled in prose, pre-spec, pre-code  
**Object:** ONE joint maximum-likelihood run over singles AND couples, pooled 2015-2017, with shared opportunity parameters and group-specific preference parameters.  
**Relation to prior work:** supersedes the three separate 2016 slice runs (`RURO_realdata_2016_estimation_v1.md`) as the *estimation object*. The slices were a diagnostic device, not the model.

---

## 0. Framing: the joint run *is* the RURO model; the slices were a decomposition of it

This is the central conceptual point and it should be stated as such in the paper. In the RURO / Aaberge-Colombino tradition (Dagsvik; AC-Strom 1999; AC-Wennemo 2009; AC 2018), the choice probability factors as

> P(job) proportional to exp( v_type(job) ) * g(job)

where **v_type** is type-specific systematic *utility* (preferences) and **g** is an *opportunity density* - a measure of how many jobs of each kind the market makes available. The defining discipline of the tradition is that **g is a market primitive**: one offer environment faces everyone, indexed only by admissible circumstances (region, urbanisation, gender-segmentation of occupations), while **v varies by household type**. Different household types do not face different labour markets; they *value the same offered jobs differently*.

The three slice runs estimated a *separate copy* of g for each slice. That was a validity check - it told us each block is basin-stable and that the wage technology is shared in fact (`beta_w0`, `educH`, `sigma` agree to two decimals across slices). But estimating three private copies of "the offer distribution" is not the RURO model; it is a saturated relaxation of it. **The joint run imposes the model's actual restriction - one g, shared - and that restriction is part of the paper's contribution, not a convenience.** The "log prior/proposal correction" in your choice-index formula is the importance-sampling correction for the B-pool draws that realise g (D1 focal modes + W1 wages + empirical `loc4`); `center_weights: proposal` is that correction. The architecture is internally consistent with a single shared g.

Everything below operationalises that single restriction.

---

## 1. The shared / group-specific partition (exact list + identification)

Recommended baseline: **49 free parameters** = 29 shared opportunity + 20 group-specific preference. The only change from the 55-param slice spec is that **occupation opportunity collapses from four blocks (`sm`/`sf`/`cm`/`cf`) to two (`m`/`f`)** - see §1c. In the joint run there are **no inert parameters**: the pool exercises both genders, both marital statuses, and all three years, so every block is active and the Hessian should be positive definite at the solution (this is itself a test - §6).

### 1a. SHARED - opportunity (market primitives), one value across all groups and years

| Block | Parameters | n | What pooled variation identifies it |
|---|---|---:|---|
| Hours opportunity | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh` | 5 | Chosen-mode frequencies across the focal-hours bands, pooled over all groups/years. A pt2 job is a pt2 job regardless of who holds it; the flags are defined identically across the singles (101-alt) and couples (901-alt) choice sets, so the restriction is well-posed. **Tension params: `beta_E` and `beta_h_pt2` (see §3).** |
| Wage technology | `beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` | 6 | One Mincer equation (D3/W1) over the full pooled chosen-wage support. Slice pre-test strongly supports sharing: `beta_w0` 2.165/2.225/2.216, `beta_w_educH` 0.332/0.338/0.354, `sigma` 0.424/0.402/0.414. **Tension param: `beta_w_educL` flips sign on singles-male (+0.148 vs -0.10).** |
| Market opportunity | `beta_E_gsur`; `beta_E_drgn2..8`; `beta_E_drgur`, `beta_E_drgmd` | 11 | Cross-region, urbanisation, and local-demand variation in the offer/employment margin. **This block is the strongest single argument for the joint run**: region and urbanisation were *inert on every singles slice* and only the couples 2016 slice identified them. Pooling singles into the same region structure activates the full region/access block for all groups. |
| Year shifters | `beta_E_y2015`, `beta_E_y2017` | 2 | Cross-year variation in the aggregate offer/employment level (2016 = reference). Inert on any single-year slice by construction; the pool is what makes them estimable. |
| Occupation opportunity | `beta_occ_{2,3,4}_m`, `beta_occ_{2,3,4}_f` | 6 | Gender-segmented offer mass over LOC4 categories (`loc4=1` reference), pooled across marital status. See §1c. |

**Shared total: 29.**

### 1b. GROUP-SPECIFIC - preferences, each identified on its own group's data

| Group | Parameters | n | Identified by |
|---|---|---:|---|
| Singles male leisure | `beta_l0_sm`, `beta_l_age_sm`, `beta_l_age2_sm`, `theta_l_sm` | 4 | singles-male slice (clean, valid SEs in `RURO_realdata_2016_postestimation_v1.md`) |
| Singles female leisure | `beta_l0_sf`, `beta_l_age_sf`, `beta_l_age2_sf`, `beta_l_nkids_sf`, `theta_l_sf` | 5 | singles-female slice (post-bugfix; `beta_l_nkids_sf=+0.634` recovered) |
| Singles consumption curvature | `theta_c_singles` | 1 | singles only (couples `theta_c` fixed at 0) |
| Couples male leisure | `beta_l0_m`, `beta_l_age_m`, `beta_l_age2_m`, `theta_l_m` | 4 | couples slice |
| Couples female leisure | `beta_l0_f`, `beta_l_age_f`, `beta_l_age2_f`, `beta_l_nkids_f`, `theta_l_f` | 5 | couples slice |
| Couples leisure interaction | `beta_ll` | 1 | see §5 |

**Group-specific total: 20.** (`beta_c` = 1 numeraire and couples `theta_c` = 0 remain fixed, as in the slice spec.)

Each of these blocks was cleanly identified with valid Hessian SEs on its own slice. The joint run does not change *which* data identifies them - it changes only that they are now estimated **conditional on a single shared g** rather than a private copy. That conditioning is the contamination channel (§3).

### 1c. The occupation decision (decided: collapse to gender)

The slice spec carries four occupation blocks (`_sm`/`_sf`/`_cm`/`_cf`). Your stated intent is that occupation opportunity is *shared*. The clean resolution, consistent with RURO discipline and the access-purity rule (D2/D10), is:

**Occupation offer mass is gender-specific and pooled across marital status.** Gender is the canonical admissible circumstance - occupational segregation means men and women genuinely face different offer distributions, which is an offer-side fact, not a taste. Marital status, by contrast, is a *preference* conditioner (it acts through `beta_ll` and the leisure blocks), and the market does not condition occupation offers on whether a man is partnered. So `_sm` and `_cm` collapse to `_m`; `_sf` and `_cf` collapse to `_f`.

The slice estimates **pre-test this restriction and support it**: male blocks (sm -1.498/-2.087/0.064 vs cm -1.579/-2.403/0.326) and female blocks (sf -0.021/-0.498/0.831 vs cf 0.094/-0.355/0.807) are close and same-signed within gender, while sm differs from sf and cm differs from cf sharply - exactly the pattern that justifies "gender-specific, marital-status-pooled."

Note this is genuinely "shared opportunity" in your sense: a single offer environment with admissible observable segmentation, not a taste term. The fallback (keep all four blocks -> 55 params) is available if the pooling test (§3b) rejects the marital-status collapse, but the pre-test says it should not.

---

## 2. Pooling over 2015-2017: the identifying assumption, stated

The pool is not free; it buys identification (`beta_ll`, year shifters, the activated region block) at the price of assumptions that must be written into the paper.

**Held FIXED across years:**

- **Preferences.** No year subscript on any leisure block, `theta_l`, `theta_c_singles`, or `beta_ll`. Assumption: over three adjacent years, tastes are stable. This is the assumption that licenses pooling preference blocks across years for identification.
- **Wage technology.** `beta_w*` and `sigma` carry no year subscript. Assumption: the real Mincer return structure is constant 2015-2017.
- **Opportunity structure.** The *mapping* from region/urbanisation/occupation/hours-band to offers is constant across years.

**Allowed to VARY across years:**

- **The aggregate offer level only**, through `beta_E_y2015` and `beta_E_y2017` (2016 reference). This absorbs business-cycle / aggregate labour-demand shifts in the employment margin.

**Wage price-basis resolution:** confirmed by build inspection, the priced wages were nominal while disposable income was 2016-real. Resolved at the build stage (Option 1, `RURO_build_fix_wage_idorighh_v1`): the estimator-facing wage columns are deflated by the same `phi` basis as `ils_dispy_real`, so all objects entering utility share the 2016-real basis. The year shifters therefore absorb real aggregate offer-level shifts, not nominal drift.

**Panel/SE treatment:** P3a shows meaningful 2016-2017 household recurrence under the stable key `idorighh` (about 1,105 singles and 1,600 couples appear twice; zero three-wave recurrence). Point estimates treat the pool as repeated cross-section. Standard errors are reported in two forms - unclustered and `idorighh`-clustered - with the difference reported as a robustness check. Clustering is the correct treatment given the two-wave recurrence, and the clustering key is `idorighh`, never `stacked_hh_uid`.

---

## 3. Contamination: the failure mode the slices structurally could not show

This is the genuinely new risk of the joint design, and it deserves the most careful treatment because it strikes the paper's central object - the decomposition.

### 3a. The mechanism

In the slice runs, each slice estimated its own copy of every "shared" parameter. A misspecification in singles-female preferences could only distort singles-female estimates - it was firewalled. **In the joint run, all groups depend on one g.** If group A's preference block is mildly misspecified, the likelihood will adjust the *shared* opportunity parameters to fit group A, and because those parameters are common, **the misfit propagates to every other group and into the decomposition.** The shared opportunity estimate becomes a compromise that is wrong for everyone, and the only remaining slack - the group-specific leisure blocks - absorbs the residual, so preferences get contaminated by mis-located opportunity. Since the paper's headline number is "opportunity share of welfare inequality," a biased shared g biases the headline directly.

The slice numbers already flag *where* this will bite:

- **`beta_E`** ranges -1.94 / -1.00 / -0.71 across slices - a factor of about 3. Forcing one value means the base employment attractiveness is a pooled compromise; if the cross-group difference is real (genuinely different market/non-market offer ratios by type), the shared value is wrong for the extremes and the difference spills into the leisure intercepts.
- **`beta_h_pt2`** flips sign sm (-2.11) -> sf (+0.15). A *shared* parameter cannot flip by gender. Whatever this term is capturing is, on the slice evidence, gender-specific. If it is offer availability of the pt2 band, that is admissibly gender-specific and belongs gender-indexed; if it is a taste, it does not belong in g at all.
- **`beta_w_educL`** flips sign on singles-male (+0.15 vs -0.10 elsewhere).

### 3b. Guards and detection (do all of these before trusting the joint estimate)

1. **Pre-test from the slices (already in hand).** Where slice values agree (`beta_w0`, `educH`, `sigma`, occupation-within-gender), pooling is safe. Where they diverge (`beta_E`, `beta_h_pt2`, `educL`), pooling is *on probation*.
2. **Formal pooling-restriction test.** Estimate an **unrestricted joint model** (shared params allowed to vary by group - equivalent to stacking the slices into one likelihood) and the **restricted joint model** (params forced equal). Likelihood-ratio test of the restriction, block by block. A rejection on a specific block is a directive: relax *that* block to gender-specific (one increment, written reason, D10-compliant), not the whole vector.
3. **Range check.** Each shared estimate should land at roughly the precision-weighted average of the slice values, i.e. **inside the range spanned by the slice estimates**. A shared parameter landing *outside* the slice range is a contamination signature - something is pulling it beyond any group's own evidence.
4. **Leisure-block displacement check.** Compare each group's joint leisure estimate to its slice leisure estimate. If a leisure block moves materially once g is forced shared, that is the contamination spilling into preferences - the most dangerous symptom, because it directly mis-splits the decomposition.
5. **Leave-one-group-out.** Re-estimate the joint model dropping each group in turn. If a shared opportunity parameter moves materially when one group leaves, that group is driving (possibly contaminating) it.

The pre-flagged outcome: I expect `beta_w0`/`educH`/`sigma`/occupation to pool cleanly, and `beta_E` and/or `beta_h_pt2` to be the ones the LR test may reject. If so, the disciplined response is to make *just those* gender-specific, with a one-line written justification, and re-run - not to abandon sharing.

---

## 4. The 10x10 couples coarsening: DEFER it from this estimate

**Decision: run the first joint estimate on the validated 30x30 (900-alt) couples draws. Defer 10x10 to a separately-gated runtime-robustness variant.**

Reasons, in order of weight:

1. **It contaminates exactly what the joint design exists to share.** The shared `beta_h_*` and `beta_occ_*` are now identified jointly off the singles grid *and* the couples grid. If couples switch to a 10x10 grid that resolves the five focal hours-modes (PT1/PT2/F35/FT/**LH**) differently from the singles grid, the shared hours/occupation parameters are estimated off **heterogeneous supports** - a grid-resolution artifact injected straight into the shared block. You would be paying an identification cost on the model's load-bearing restriction to save runtime.
2. **It is not free; it is its own work item.** Per your own note, 10x10 needs a **new draw build + an LH-band coverage gate** (the men's long-hours cluster from D1 is the band most at risk of under-resolution at coarse grids) **+ its own recovery test**. That is not a parameter you flip; it is a parallel build with its own validation ladder.
3. **The runtime problem may not be a grid problem.** The 4.5h couples solve is single-threaded CONOPT at about 2% CPU (one core of 64); `RURO_spec_redesign_decisions_v2.md` parks estimator/runtime as orthogonal to the economic ladder. Do not pay an *identification* cost to fix what is plausibly an *engineering* cost (solver/parallelism).

**Where 10x10 does belong:** as a **runtime-robustness check at the resampling stage**. If the welfare/decomposition step needs bootstrap or many counterfactual re-solves and 30x30 makes that infeasible, build the 10x10 variant, pass its LH-coverage gate and its own recovery test, re-estimate, and **show the decomposition shares are invariant to grid resolution.** That converts the coarsening from a hidden risk into a published robustness result - which is strictly better for the paper than baking it into the baseline.

---

## 5. `beta_ll`: repeated-cross-section verdict and fallback

Confirmed: the P3a pool should be treated as a repeated cross-section under `idorighh` for point estimation. There is meaningful two-wave recurrence, but no clean three-wave panel structure and no basis for treating the baseline point estimate as a within-couple panel estimator. The strong panel route to identifying `beta_ll` through within-couple multi-year leisure variation is therefore unavailable.

On every single 2016 slice, `beta_ll` is **inert on singles** (no leverage - it is a couples parameter) and **lands at the bound 0.0 on couples**. Landing exactly at a bound is the signature of a likelihood that is flat (or monotone) in the parameter on that sample, i.e. weak-to-no identification, not merely imprecision.

The pooled repeated cross-section can still add statistical power. It can rescue `beta_ll` if the 2016 bound-landing was small-sample flatness, but it cannot rescue it if the flatness is structural (the interaction term has no leverage given the product choice-set geometry). The honest prior is therefore weak: expect to test `beta_ll`, but expect the fallback to be needed unless the pooled likelihood clearly moves it off the bound with stable curvature.

Fallback if `beta_ll` stays at the bound even pooled - and this fallback is cheap, which is the key point: `beta_ll` is a **couples-preference** parameter, fully inside the group-specific block. It touches neither the shared opportunity g nor the opportunity component of the decomposition. So:

- **Baseline:** fix `beta_ll = 0` (additively separable couples leisure) and report the decomposition conditional on that, with a **sensitivity sweep over a calibrated range** of `beta_ll` (anchored to AC couples estimates).
- State explicitly that **the opportunity share of welfare inequality is robust to the `beta_ll` treatment**, because `beta_ll` is a within-couples preference term - fixing or freeing it re-allocates welfare *within* the couples preference block, not between the opportunity and preference components.

Do not let `beta_ll` block the paper. Try pooled identification; if it fails, fix it, sweep it, and move on.

---

## 6. The recovery test the joint object must pass (it does NOT inherit the slice verdict)

The slice recovery verdict (`RURO_recovery_test_results_v3.md`) certified three *private* copies of g. It says nothing about whether **one shared g is recoverable from cross-group pooling**, which is the whole novelty. The D10 guardrail - *no reported decomposition before the recovery test passes* - applies to this configuration specifically. The joint recovery test must show:

1. **One DGP, shared g.** Generate synthetic singles AND couples across all three years from **a single set of shared opportunity parameters + group-specific preference parameters + year shifters**, on the production grids (101-alt singles, 900-alt couples) and the production B-pool draw/proposal structure.

2. **Shared-from-pooled recovery (the new test).** Re-estimate and recover the shared block - `beta_E`, `beta_h_*`, `beta_w_*`, `sigma`, the full market block, occupation - to tolerance **from the pooled likelihood**. This is precisely what the slices could not test: there, each shared parameter was recovered from one group; here it must be recovered as a single value from all groups jointly.

3. **Group-specific recovery.** Each leisure block recovered on its own group; year shifters recovered (tests the cross-year identification); **`beta_ll` recovered or diagnosed**. If synthetic recovery of `beta_ll` fails *even with the true pooled DGP*, the data structure genuinely cannot identify it and §5's fallback is mandatory, not optional.

4. **Two-start basin agreement on ALL parameters.** Unlike the slices, where inert cross-group parameters legitimately differed between warm and cold starts, the joint run has **no inert parameters**, so warm (= theta*) and cold (= spec init) must agree to tolerance on the *entire* vector. Any parameter that does not agree is a genuine flat direction, not slice-inertness.

5. **Positive-definite Hessian at the solution.** Because everything is now identified, the Hessian should be PD - no flat directions. A non-PD Hessian here is a real identification failure (contrast the slices, where non-PD was the *expected* fingerprint of inert blocks). If non-PD, name the flat direction via the patched G3b diagnostic (commit `c90d47a`).

6. **Contamination recovery test (run this - it is itself a contribution).** Generate synthetic data where one group's preference block is *deliberately misspecified relative to the estimation model* (e.g. simulate a genuinely group-specific `beta_E`, then estimate forcing it shared). Measure how much the shared g and the **decomposition shares** move. This quantifies the §3 failure mode, tells you how robust the headline number is to the pooling restriction being slightly wrong, and gives you a defensible robustness paragraph: "under a [X]% misspecification of group preferences, the opportunity share moves by [Y] points."

Tests 1-5 must pass and test 6 must be characterised **before any real-data joint decomposition is reported.**

---

## Summary of decisions

| # | Decision |
|---|---|
| Partition | 29 shared opportunity + 20 group-specific preference = **49 params** |
| Occupation | **Collapse to gender (m/f)**, pooled across marital status; slice pre-test supports it |
| Pooling | Preferences + wage tech + opportunity *structure* fixed across years; only the **offer level** shifts via year dummies. Wages are corrected to 2016-real in the build. |
| SE treatment | Point estimates treat the pool as repeated cross-section; report both unclustered and `idorighh`-clustered SEs. |
| Contamination | Pre-flagged on `beta_E`, `beta_h_pt2`, `educL`; gate the run with an LR pooling test + range/displacement/LOGO checks |
| 10x10 couples | **Defer**; run on validated 30x30; 10x10 becomes a gated resampling-stage robustness variant |
| `beta_ll` | Strong panel route unavailable; try pooled repeated-cross-section identification, but expected fallback is fix at 0, sweep, and document opportunity-share robustness |
| Recovery | A **new** joint recovery test (shared-from-pooled + contamination) is required; the slice verdict does not transfer |

---

## Next step

Prerequisite: the wage-deflation + `idorighh` build fix (`RURO_build_fix_wage_idorighh_v1`) must land and pass its verification gates before the spec-build session, since the joint estimate runs on the corrected parquets. This prerequisite is now satisfied in the current build chain.

With this memo settled, the next action is to *build the joint spec YAML* from `estimation_spec_bpool_p3a_v1.yaml` - collapsing occupation to gender, marking the shared/group-specific blocks, and removing the slice-inert handling - **and** to scaffold the joint recovery-test harness implementing the six checks in §6. Attach to that session: this memo, `estimation_spec_bpool_p3a_v1.yaml`, `RURO_spec_redesign_decisions_v2.md`, and `RURO_build_fix_wage_idorighh_v1.md`.

Save the outputs as `estimation_spec_joint_pooled_v1.yaml` and `RURO_joint_recovery_test_design_v1.md`. Do not authorise a real-data joint run until the recovery harness exists and §6 tests 1-5 pass.

