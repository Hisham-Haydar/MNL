# JMP Next-Cycle Opportunity Respecification Plan v1

*France RURO multi-year extension | v1 | 2026-05-22*

**Document category: next-cycle design memo only.** This memo plans the
next specification-and-rebuild cycle for the RURO opportunity mechanism.
It does **not** authorize implementation, data rebuild, EUROMOD execution,
estimation, welfare computation, or an SA2 verdict. M1-clean 2016 remains
the active JMP baseline throughout. The currently authorized corrected
pooled P3a post-estimation track is unaffected and proceeds independently
(§27).

---

## 1. Purpose

To consolidate two opportunity-mechanism corrections — confirmed by the
read-only opportunity-block diagnostic (`Results/_shared/JMP_opportunity_block_readonly_diagnostic_v1.md`)
— into a single next-cycle respecification plan, because both corrections
are upstream of the same data-preparation pipeline and must be built
together:

1. **Couples choice set:** replace the index-paired diagonal with a product
   sample of the joint (his job, her job) opportunity space.
2. **Wage-offer structure:** replace the unconditional wage draw with an
   occupation-conditional wage draw (W1), arbitrated by the pre-committed
   diagnostic rule that has now fired.

The memo fixes the next-cycle baseline specification, the candidate
alternatives, the pilot design, the open design risks, and the data-prep /
EUROMOD / merge / estimation steps each correction requires. It does not
green-light any of them. The deliverable that follows this memo is a
spec contract + data-build authorization, not code.

---

## 2. Current empirical status

- **Active baseline:** M1-clean 2016 (single-year). Not displaced by
  anything in this memo.
- **Candidate pooled model:** corrected-region pooled P3a
  (`ruro_occ_P3a_pooled`), FR_2015/2016/2017, 55 parameters (54 free;
  `beta_l0_m` at active lower bound). Three starts converged to an identical
  parameter vector at joint LL = −19,084.3313; region-dummy block repaired
  (flat ridge removed) and true-Hessian cluster-robust SEs computed
  (T3 = 9,657 clusters; T4 = 0 non-positive; T5 = 0 below-Hessian). No
  welfare, no SA2 verdict, no canonical promotion.
- **Immediate P3a gate (separate track):** a fresh strict post-estimation
  review / SA2-readiness verdict (S4/S5 region identification; S6
  preference-block comparison). That review is the next event on the P3a
  track and is **not** part of this memo.
- **Frozen spec under that track:** 100-alternative diagonal couples
  construction, unconditional wage draw. Both are exactly what this memo
  proposes to change — in the *next* cycle, not this one.

The two tracks are deliberately separate: the P3a track finishes on its
frozen spec and earns (or fails) its verdict; this memo designs the
specification that comes after.

---

## 3. Why this is a next-cycle redesign, not an immediate modification

Both corrections are set at **data preparation**, upstream of EUROMOD and
the GSURv2 merge. Neither can be applied as an edit to the frozen P3a
estimation:

- The couples product sample changes the **choice set** in the MNL parquet,
  which is fixed at build time. New joint alternatives must be passed
  through EUROMOD to obtain their disposable incomes, re-merged with GSUR,
  re-stacked, and only then estimated.
- The occupation-conditional wage draw changes the **draw construction** in
  `enh_RURO_draws.py`, also upstream of EUROMOD (the simulated wage feeds
  the disposable-income computation for each alternative).

Applying either mid-flight would invalidate the frozen spec and contaminate
the P3a verdict. The disciplined sequence is: P3a finishes on its frozen
spec → this memo's plan is authorized as a *new* specification with its own
spec contract and data-build authorization → rebuild → re-estimate against
P3a as the comparison point. Even the simulation-consistency check (§23) is
not read-only: it requires *building* denser-product samples, so it too
belongs to this next cycle.

---

## 4. Evidence from the read-only diagnostic

From `Results/_shared/JMP_opportunity_block_readonly_diagnostic_v1.md`:

**Wage-occupation separation (Part A).** Occupation-conditional accepted
log-wage distributions are materially separated. One-way ANOVA of log wage
on `loc4`: η² = 0.159 pooled, 0.150 male, 0.176 female, 0.168 couples-male,
0.184 couples-female — all above the pre-committed 0.10–0.15 threshold.
Adding `loc4` dummies to the descriptive Mincer raises R² by 0.066
(F = 127.87, p < 10⁻¹⁶). The pre-committed rule fires: **adopt
occupation-conditional wage draws in the next cycle.**

**The separation is concentrated, not uniform (key qualifier).** The η²
is driven mainly by **loc4 = 4 (Non-Intellectual)** pulling away from the
rest. Pairwise IQR overlaps: RM-vs-NRM 87–97% (statistically the same wage
distribution), RM-vs-Intel 74–78% and NRM-vs-Intel 64–75% (modest),
RM-vs-NonInt 17% and NRM-vs-NonInt 13% (strongly separated). The binding
empirical fact is a **Non-Intellectual premium** (+0.33 vs RM, +0.39 vs
NRM), not four cleanly distinct wage tiers. This is what motivates the
two-group alternative (§7).

**Couples diagonal (Part B).** Confirmed Classification A: index-paired
diagonal. The combine step is an `inner` merge on `["idhh", "draw"]` in
`_reshape_couples_to_wide()` (lines ~1058–1065 of
`enh_RURO_prep_mnl_basic.py`); his draw *i* is always paired with her draw
*i*; off-diagonal combinations are absent by construction. The current
743,800 couples rows = 7,438 × 100 confirm 100 joint alternatives per
couple — the diagonal, i.e. 1% of the 100×100 product space.

**Occupation draw treatment (Part B/§15 of diagnostic).** `occ_spec =
"fixed"`: working simulated draws keep the observed occupation; occupation
is not resampled across the 100 draws. This conditions how the wage
correction should be read (§10–§11).

**Placement (Part C).** `loc4` enters the model **only** through the
`occupation_opportunity` block (12 log-linear shifters: 4 sub-groups ×
3 non-reference categories, reference loc4 = 1). The `wage_opportunity`
block has **no** `loc4` term. This is the "occupation in the opportunity
layer, wage drawn independently of it" case — the case where conditioning
wages on occupation is most directly required for internal consistency.

---

## 5. Couples diagonal-to-product correction

**Status: specification fix, not an accuracy refinement.** The diagonal
mis-represents the couple's joint feasible set in two ways: it drops every
off-diagonal combination (his_i, her_j with i ≠ j), and it silently imposes
maximal partner-draw dependence (perfect rank-matching, no economic
content). The correct object — under the conditional-independence
assumption the model otherwise uses — is the **product** of the marginal
per-partner draws.

**The fix:** keep the marginal per-partner draws (drawing N jobs per
partner is a valid marginal sample); change the **combination rule** in
`_reshape_couples_to_wide()` from index-pairing (diagonal) to a product
sample of (his job, her job). This is a combination-rule change, not a
re-draw of marginals — the diagnostic confirms the marginals themselves are
fine.

**Why it is first-order for the JMP.** Couples are ≈7,438 of 12,445 pooled
household-years (≈60%). A mis-specified couples feasible set means the
opportunity-attributable component of couples' well-being inequality — the
paper's core contribution — is computed against a feasible set that is not
the couple's actual feasible set, for the majority of the sample.

**Partner-dependence assumption (state explicitly).** The next-cycle spec
contract must state the assumption: if partners' opportunity draws are
conditionally independent, the product is the correct joint sample; if
genuine dependence (e.g. assortative opportunity matching) is intended, the
joint draw must encode it and the product-of-independent-marginals is
itself an approximation. The recommended baseline assumption is
conditional independence (product), made explicit — not left implicit as
the diagonal currently does (where it silently imposes maximal dependence).

---

## 6. Occupation-conditioned wage correction

**Status: the first wage-opportunity correction, warranted by the fired
decision rule.** The current `wage_opportunity` block is a five-parameter
log-normal Mincer equation (intercept, educL, educH, pexp, pexp²) with a
single common `sigma`, unconditional on occupation and sex.

**W1 (recommended baseline correction):** add occupation intercept shifts to
the wage mean equation, common slopes, reference loc4 = 1:

```
log w = beta_w0 + beta_w_educL·educL + beta_w_educH·educH
        + beta_w_pexp·pexp + beta_w_pexp2·pexp²
        + delta_occ2·1[loc4=2] + delta_occ3·1[loc4=3] + delta_occ4·1[loc4=4]
        + epsilon
```

Three added mean parameters (delta_occ2, delta_occ3, delta_occ4). This lets
the wage-offer density shift by occupation without exploding the parameter
count or imposing occupation-specific slopes.

**Why W1 and not the status quo.** With `loc4` in the opportunity index but
absent from the wage draw, the model offers wage–occupation combinations at
densities that contradict the data (e.g. a routine-manual job at a
Non-Intellectual wage). For a paper whose contribution is the consistent
treatment of opportunities, that internal inconsistency is a soft spot
exactly in the mechanism being decomposed. W1 removes it at minimal cost.

---

## 7. Two-group wage alternative

**The diagnostic's own evidence says the four-group structure is overkill.**
RM and NRM are near-identical on wages (IQR overlap 87–97%); the separation
is essentially loc4 = 4 vs the rest. A parsimonious alternative captures the
binding fact with one parameter:

```
log w = beta_w0 + beta_w_educL·educL + beta_w_educH·educH
        + beta_w_pexp·pexp + beta_w_pexp2·pexp²
        + delta_NonInt·1[loc4=4]
        + epsilon
```

One added mean parameter (delta_NonInt). If this captures materially the
same wage-offer separation and the same decomposition as W1 (three
parameters), it is the better specification — fewer parameters, a sharper
contribution claim ("one occupation class commands a large wage premium")
than a fuzzier "wages differ across four classes."

**Decision: the 2016 pilot must estimate W1 and the two-group alternative
side by side** and compare their effect on the decomposition. Ship the
parsimonious one if it matches W1. This is cheap to add and directly tests
the concentration finding in §4.

---

## 8. Sex-specific wage equation as later refinement

**W2 (occupation × sex intercepts) is supported but deferred.** The
descriptive evidence supports sex-specific occupation premia (loc4 × sex
interactions F = 13.86, p < 10⁻¹³; adding sex alone raises Mincer R² by
0.011 — smaller than the 0.066 from occupation). But:

- Sex contributes far less than occupation (ΔR² 0.011 vs 0.066); the
  unconditional gender gap is only ≈0.08 log-units.
- W2 adds ≈8 parameters over W1, and some cells are thin (Intel-Male
  n = 104 in singles).

**Decision: W2 is a later refinement, tested only if the W1 pilot runs
cleanly and the decomposition motivates it.** It is not the first
correction. Note that the wage block already supports sub-group structure
elsewhere; whether sex-specific *occupation* premia are needed is a
second-stage question.

---

## 9. Accepted-wage versus offer-wage caveat

**State explicitly in the spec contract: the §4 diagnostic separation is
measured on *accepted* wages (conditional on holding the job), not the pure
*offer* distribution.** The wage-opportunity layer is conceptually an
*offer* distribution. Accepted wages are selected on employment within each
occupation; if selection differs across `loc4` (plausible — entry into
NonInt vs RM is not random), the offer-distribution separation could be
larger or smaller than the measured 0.159.

**Implication for the decision vs the form:**

- For the **keep/condition decision**, this changes nothing: sharp
  separation in accepted wages is strong evidence against an unconditional
  offer draw. The rule fired correctly.
- For the **form of the conditional draw**, it is a live design issue.
  "Fit W1 on accepted wages and sample from it" bakes the selection into the
  offer distribution. Do **not** treat that as automatically final. The spec
  contract should flag occupation-conditional *offer* modelling (with a
  selection correction) as an open question, and at minimum document the
  accepted-wage approximation as a stated limitation if the simple approach
  is used for the pilot.

For the pilot, the pragmatic position is: use the accepted-wage W1 fit as a
first implementation, **explicitly labelled an accepted-wage approximation**,
with offer-selection correction listed as the next refinement if the pilot
motivates it. This is honesty about the object, not a blocker.

---

## 10. Occupation draw treatment

**Pilot decision: retain `occ_spec = "fixed"`.** Working simulated draws
keep the observed occupation; occupation is not resampled across draws. This
is the cleanest choice for the pilot for three reasons:

1. It limits the dimensionality of the rebuild (the product is over
   his hours×wage × her hours×wage at fixed occupations — fewer moving
   parts; §14).
2. It keeps the occupation-opportunity block (`beta_occ_*`) doing the
   cross-occupation work, with the wage draw conditional *within* each
   person's fixed occupation. This is internally coherent: the wage premium
   is attached to the occupation the person actually holds.
3. It isolates the two corrections under test (product + W1 wage) from a
   third change (occupation sampling), which would confound the pilot.

**Consequence to record:** with `occ_spec = "fixed"`, the W1 occupation
wage premium re-weights wages *within* a fixed occupation; it does not
generate cross-occupation wage opportunities through the wage layer. Cross-
occupation opportunity continues to come from the `occupation_opportunity`
block. This is the design that makes §11 (double-counting) manageable.

**Deferred alternative (not pilot):** sampling occupation from empirical
frequencies, or sampling occupation jointly/conditionally with wage, is a
later extension. It changes the meaning of the occupation-opportunity layer
and must not be bundled into this pilot.

---

## 11. Wage-occupation double-counting risk

**This is the identification risk to name in the spec contract.** With W1,
the occupation premium enters the model in two places:

- `delta_occ*` in the **wage mean equation** (new, W1).
- `beta_occ_*` in the **occupation_opportunity block** (existing, 12
  shifters).

Both are functions of `loc4`. Without explicit handling, the occupation
premium can be split arbitrarily between the wage layer and the occupation
layer, and the two coefficient sets are not separately interpretable.

**Why `occ_spec = "fixed"` makes this tractable (not automatic).** Because
occupation is fixed per person across draws, the two layers act on different
margins of the choice index:

- `delta_occ*` shifts the **wage** (and hence consumption/disposable income)
  *within* the person's fixed occupation — it affects the level of the wage
  drawn for each alternative.
- `beta_occ_*` shifts the **opportunity weight** of the occupation in the
  market-opportunity index — it affects how available that occupation type
  is.

These are conceptually distinct channels (wage level vs opportunity weight),
which is what permits separate identification in principle. But it must be
**verified, not assumed.** The spec contract must require:

1. A statement of the exact role of each coefficient set in the choice
   index (which enters consumption via the wage, which enters the
   opportunity weight).
2. A recovery/identification check in the pilot: confirm that `delta_occ*`
   and `beta_occ_*` are separately recoverable (e.g. that their estimates
   are stable and that the information matrix does not show near-collinearity
   between them). If they are not separately identified, the fallback is to
   keep occupation in one layer only (most likely: keep `beta_occ_*` in the
   opportunity block and condition the wage draw on occupation through the
   *offer distribution* without a free wage-equation `delta_occ`, i.e. an
   empirical occupation-conditional offer density rather than an additional
   estimated mean shifter).

This is the single most important technical caution in the memo. The
diagnostic did not surface it; the spec contract must.

---

## 12. Recommended next-cycle baseline specification

The next-cycle baseline ("NC-baseline") is:

| Component | NC-baseline choice |
|---|---|
| Couples choice set | **Product sample** (not diagonal); conditional-independence assumption stated |
| Product size (pilot) | **30 × 30 = 900** alternatives per couple |
| Wage-offer structure | **W1** — occupation intercepts (delta_occ2/3/4), common slopes, reference loc4=1 |
| Wage form caveat | Accepted-wage approximation, explicitly labelled (§9) |
| Occupation draw | **`occ_spec = "fixed"`** retained (§10) |
| Sigma | **Single common sigma** for pilot; occupation-specific sigma tested as alternative (§16) |
| Draw design | **Halton or Sobol** for the product (§17) |
| Pilot scope | **2016 couples only** (§25) |
| Identification guard | Wage–occupation double-counting check required (§11) |

The NC-baseline is the candidate that the rebuild would target. It is
compared against the corrected pooled P3a (the diagonal/unconditional spec)
as the reference point, once P3a has its own verdict.

---

## 13. Candidate alternative specifications

To be evaluated against the NC-baseline in the pilot (cheap variants on the
same rebuild) and the full cycle:

| Label | Variant | Relative to NC-baseline |
|---|---|---|
| **A0** | Reference: diagonal + unconditional wage (current P3a) | Comparison point only |
| **NC-baseline** | Product 900 + W1 + fixed occ + common sigma | Recommended |
| **G2** | Product 900 + **two-group wage** (1[loc4=4]) + fixed occ | Parsimony test (§7) — **run in pilot** |
| **S-occ** | NC-baseline + **occupation-specific sigma** | Variance test (§16) |
| **P16** | NC-baseline at **40 × 40 = 1,600** product | Simulation-consistency (§14, §23) |
| **W2** | NC-baseline + occupation × sex wage intercepts | Later refinement (§8) |
| **OFF** | NC-baseline with occupation-conditional **offer** draw (selection-corrected) | Later refinement (§9) |

Pilot priority: NC-baseline vs G2 (the parsimony decision) and the P16
consistency point. S-occ, W2, OFF are full-cycle or later.

---

## 14. Product-sample size decision

| Combination rule | Alt./couple | Couples rows (2016 pilot, 2,577) | Couples rows (pooled, 7,438) |
|---|---|---|---|
| Diagonal (current) | 100 | 257,700 | 743,800 |
| Product 30 × 30 | 900 | 2,319,300 | 6,694,200 |
| Product 40 × 40 | 1,600 | 4,123,200 | 11,900,800 |
| Product 100 × 100 (ideal) | 10,000 | 25,770,000 | 74,380,000 |

**Decision:** start at **900 (30 × 30)** for the 2016 pilot. **1,600
(40 × 40)** is the simulation-consistency comparison point. **10,000
(100 × 100)** is conceptually clean but computationally infeasible for the
current pipeline (×100 the couples rows; ~74M pooled). The size is **not**
chosen by judgement — it is settled by the simulation-consistency check
(§23): if 900 and 1,600 give materially the same estimates and
decomposition, 900 is sufficient; if still moving, go denser. Halton/Sobol
(§17) reduces the count needed for a given accuracy.

---

## 15. Wage-density decision

**Decision: W1 (occupation intercepts) is the wage-density correction for
the pilot, tested against the two-group alternative G2.** The wage-density
richness and the couples product size compete for one computational budget
(§24): a moderate product (900) with W1/G2 wages may be both more correct
and cheaper than a large product (1,600) with an unconditional wage. Size
them jointly, not as independent knobs. Full occupation-conditional offer
densities with selection correction (OFF, §9) and W2 (§8) are deferred.

---

## 16. Common sigma versus occupation-specific sigma

The diagnostic shows residual SD is heteroskedastic across occupations
(Regression B residuals: NRM largest scatter ≈0.43–0.46 both sexes;
Intel-Female smallest ≈0.28). A single `sigma` misrepresents within-
occupation spread.

**Decision: pilot retains a single common `sigma`** (the cleaner first step,
isolating the mean-shift correction); **occupation-specific sigma is tested
as alternative S-occ.** Adding occupation-specific sigmas is +3 variance
parameters (or +1 for a two-group variance). Whether the decomposition is
sensitive to the variance structure is an empirical question for the pilot;
do not pre-commit to occupation-specific sigma without evidence that the
mean-shift W1 alone leaves material residual heteroskedasticity that affects
the decomposition.

---

## 17. Random, Halton, or Sobol draw design

**Decision: switch the couples product draws to a low-discrepancy sequence
(Halton or Sobol).** Two reasons:

1. **Highest-leverage cost lever.** If current draws are pseudo-random, a
   low-discrepancy sequence cuts the product points needed for a given
   accuracy substantially — a moderate Halton product can match a much
   larger pseudo-random product. It reduces the *count* without changing the
   *correctness* (still a product, better spread).
2. **Randomised product over coarse grid.** The product need not be a fixed
   30 × 30 grid; a randomised/scrambled subsample of the 100×100 product
   (or a Halton/Sobol joint sample) avoids the grid-edge artifacts of a
   coarse deterministic grid and is generally preferable for the same point
   count.

Scrambled Sobol with a fixed seed is the recommended default for
reproducibility plus low discrepancy. The spec contract should record the
sequence, the seed, and the scrambling.

---

## 18. Required data-prep changes

(Plan only — not authorized here.)

1. **`enh_RURO_draws.py`** — wage draw: replace the unconditional draw with
   an occupation-conditional draw consistent with W1 (or G2). Decide the
   draw source per §9/§11 (estimated W1 mean shift vs empirical
   occupation-conditional offer density). Retain `occ_spec = "fixed"`
   (§10). Switch the couples draw generator to Halton/Sobol (§17).
2. **`enh_RURO_prep_mnl_basic.py`, `_reshape_couples_to_wide()`** — replace
   the `inner` merge on `["idhh", "draw"]` (diagonal) with a product /
   randomised-product join producing 900 (pilot) joint alternatives per
   couple. State the conditional-independence assumption in the builder.
3. **`prepare_pooled_estimation_ready.py`** — adjust split-stem prep for the
   new per-couple alternative count; verify singles unchanged (100/individual).
4. **Spec YAML (new file, not an edit to P3a)** — add `delta_occ*` (or
   `delta_NonInt`) to `wage_opportunity`; record sigma decision; record the
   role of `delta_occ*` vs `beta_occ_*` per §11.

---

## 19. Required EUROMOD reruns

The new joint couple-alternatives and the new occupation-conditional wages
both feed disposable income. EUROMOD must be re-run on the rebuilt
alternative set to obtain disposable incomes for every new (his job, her
job) product point and for the re-drawn wages. This is the binding
data-build step (it is why neither correction is read-only). Pilot:
2016 couples only.

---

## 20. Required GSURv2 merge and MNL rebuild

After EUROMOD: re-run the GSURv2 merge on the rebuilt couples alternatives,
then rebuild the MNL parquet (`enh_RURO_prep_mnl_basic.py`) at the product
choice set. Verify row counts (2016 couples ≈ 2,319,300 at 900;
singles unchanged), the one-region-per-household partition is preserved, and
the income routing (GA15) is intact on the new alternatives.

---

## 21. Required pooled stacking

For the pilot, no pooled stacking — the pilot is 2016 couples only. For the
full cycle (after a clean pilot), re-stack FR_2015/2016/2017 at the product
choice set and re-attach year/region shifters, reproducing the pooled
structure of P3a but on the corrected opportunity set.

---

## 22. Required estimation protocol

(Plan only — not authorized here.) When the rebuild is authorized:

- Three-start design (M1-clean/P3a warm; spec defaults; perturbed
  converged), as in P3a, to confirm a reproducible optimum.
- True-Hessian cluster-robust SEs (sandwich V = H⁻¹ B H⁻¹), cluster key
  `idorighh`, with T3/T4/T5 checks as in the P3a report.
- The wage–occupation double-counting / separate-identification check (§11)
  as an explicit estimation diagnostic, not an afterthought.
- No welfare, no SA2, no canonical promotion until the new model has its own
  post-estimation review.

---

## 23. Simulation-consistency checks

The product size is settled by convergence, not feel. Build the pilot
couples block at **400, 900, and 1,600** product points and check whether
the key structural estimates **and** the decomposition quantities stabilise:

- If 900 ≈ 1,600 on estimates and decomposition → 900 is sufficient; 1,600
  buys only cost.
- If still moving at 1,600 → go denser (and lean harder on Halton/Sobol to
  control cost).

This yields the citable justification ("estimates stable beyond N product
points") that couple-model referees expect. Note this check is itself a
data build (it requires constructing the denser samples) — it is next-cycle
work, not part of the read-only diagnostic phase.

---

## 24. Computational-cost plan

The cost lands on three places, in increasing bindingness: parquet
storage/management; the one-time precompute; and — most bindingly — the
per-iteration estimator cost, paid at every gradient and Hessian evaluation,
which scales with total choice-row count.

**Joint budget rule:** the product size (rows) and the wage-density richness
(per-row cost + parameters) are sized **against one budget**, not
independently. Pilot ordering of levers, cheapest-first:
(1) Halton/Sobol to cut the product count; (2) start at 900, not 1,600;
(3) 2016 couples only, not pooled; (4) common sigma, not occupation-specific.
Escalate (denser product, occupation sigma, W2, pooling) only as the
consistency check and the decomposition motivate, and only within the
measured budget from the pilot's precompute and gradient timings.

---

## 25. Pilot design

**Recommended pilot: 2016 couples only, 900-alternative product (30 × 30,
Halton/Sobol), W1 wages, `occ_spec = "fixed"`, common sigma.**

Pilot objectives:

1. Verify the full corrected pipeline end-to-end on a tractable scale:
   draw generation → EUROMOD → GSURv2 merge → MNL build → precompute →
   one estimation.
2. Measure precompute timing and gradient/Hessian evaluation time to set the
   computational budget for the full cycle (§24).
3. **Run NC-baseline vs G2** (two-group wage) and compare the decomposition
   — the parsimony decision (§7).
4. Run the **400/900/1,600 simulation-consistency** points (§23).
5. Run the **wage–occupation separate-identification check** (§11).

The pilot is a feasibility-and-design instrument, not a result. It does not
produce a baseline or a welfare number; it tells you which full-cycle spec
to build and whether the pipeline survives the row-count increase.

---

## 26. What remains blocked

Not authorized by this memo:

- Any data rebuild or draw regeneration.
- Any EUROMOD execution.
- Any GSURv2 merge or MNL rebuild.
- Any pooled re-stacking.
- Any structural estimation (pilot or full).
- Any welfare computation.
- Any SA2 verdict.
- Any canonical promotion or displacement of M1-clean 2016.
- Any modification of the frozen pooled P3a YAML.

The next document is a **spec contract + data-build authorization** for the
pilot (`RURO_model_spec_contract_v3_NC.md` / a pilot authorization), not
code. This memo feeds that contract; it does not replace it.

---

## 27. What should continue in the current corrected pooled P3a track

The P3a track proceeds **independently and unchanged**:

- The immediate P3a gate is the **fresh strict post-estimation review /
  SA2-readiness verdict** (S4/S5 region identification on the repaired
  region block; S6 preference-block comparison). That review uses the
  three-start converged P3a estimates (LL = −19,084.3313) and the
  true-Hessian cluster-robust SEs already computed.
- P3a stays on its **frozen 100-diagonal, unconditional-wage spec** for that
  verdict. Nothing in this memo edits it.
- If P3a passes its review and SA2, it becomes the **comparison point** for
  the NC-baseline rebuild — not the final model. If it fails, the NC cycle
  proceeds regardless (the corrections here are warranted on their own
  evidence).

Keep the two tracks in separate documents and separate run directories. Do
not let the next-cycle redesign delay or contaminate the P3a verdict, and do
not let the P3a verdict gate the read-only design work that has already
produced this memo.

---

## 28. Exact next Claude Code pilot-audit prompt

Use **Claude Code (Sonnet)**, local, **read-only**. This audits feasibility
of the pilot rebuild **without building anything** — it inspects the exact
code paths to be changed and estimates the row counts and parameter changes,
so the spec contract is grounded. It does not modify, draw, run EUROMOD, or
estimate.

```text
Work locally in my RURO/MNL codebase. READ-ONLY pilot-feasibility audit
for the next-cycle opportunity respecification. 

Do NOT modify any file. Do NOT regenerate draws. Do NOT run EUROMOD.
Do NOT rebuild data. Do NOT modify YAML. Do NOT estimate. Do NOT compute
welfare. Do NOT issue SA2. Do NOT promote any model over M1-clean 2016.

Read:
- docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md
- Results/_shared/JMP_opportunity_block_readonly_diagnostic_v1.md
- docs/jmp_methodology/JMP_couples_opportunity_draw_design_note_v1.md
- docs/jmp_methodology/JMP_conditional_wage_on_occupation_decision_note_v1.md
- scripts/enhanced/enh_RURO_draws.py
- scripts/enhanced/enh_RURO_prep_mnl_basic.py
- scripts/maintenance/prepare_pooled_estimation_ready.py
- scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml
- Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet
- Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet
- Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json

Create: Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md

Use exactly these headings:
1. Audit verdict (feasible / blockers)
2. Authorization scope (read-only; M1-clean active; nothing built)
3. Files inspected
4. Couples combine code path — exact lines to change (diagonal -> product)
5. Product-join feasibility — how a 30x30 product would be constructed in
   _reshape_couples_to_wide(), and whether the marginal draws are reusable
   as-is (no re-draw) or must be regenerated
6. Wage draw code path in enh_RURO_draws.py — exact location of the
   unconditional wage draw; what a W1 occupation-intercept draw and a
   two-group 1[loc4=4] draw would each require
7. occ_spec=fixed confirmation — exact code showing occupation is not
   resampled across working draws
8. loc4 placement confirmation — occupation_opportunity block only; no loc4
   in wage_opportunity (quote the YAML blocks)
9. Wage-occupation double-counting surface — list every place loc4 enters
   the choice index now (occupation_opportunity beta_occ_*) and where W1
   delta_occ* would enter (wage_opportunity); state the channel each acts on
   (opportunity weight vs wage level)
10. 2016 single-year couples count and projected pilot row counts at
    400 / 900 / 1600 product points (couples only; confirm 2016 couples n)
11. Halton/Sobol availability — whether scipy.stats.qmc or equivalent is
    importable in the environment; current draw RNG and seed handling
12. Precompute and estimator row-count scaling — which functions iterate
    over choice rows and would pay the per-iteration cost increase
13. EUROMOD re-run surface — which alternatives feed disposable income and
    therefore must pass through EUROMOD on a product rebuild
14. Estimated parameter-count change — NC-baseline (W1) vs G2 (two-group)
    vs current P3a, mean and variance parameters
15. Identified blockers or unknowns for the pilot
16. What was not executed
17. Required final statements (read-only; M1-clean active; no build, no
    estimation, no welfare, no SA2; P3a track unaffected)

Required checks:
- Quote the exact merge lines in _reshape_couples_to_wide().
- Quote the exact wage-draw lines in enh_RURO_draws.py.
- Quote the occ_spec handling that fixes occupation across draws.
- Quote the wage_opportunity and occupation_opportunity YAML blocks.
- Report 2016 couples n directly from the parquet (do not assume 2,577;
  confirm it).
- Compute projected row counts from the confirmed 2016 couples n.
- Confirm whether marginal per-partner draws can be reused for a product
  (combination-rule change only) or require regeneration.
- Be strict, parsimonious, and report blockers honestly.
```

Save as: `Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md`

After that audit: write the pilot **spec contract + data-build
authorization** (`RURO_model_spec_contract_v3_NC.md`) — the first document
that actually authorizes building anything. This memo and the feasibility
audit feed it.

---

**Required final statements:**

- **This is a next-cycle design memo only. It authorizes nothing** — no
  rebuild, no EUROMOD, no estimation, no welfare, no SA2.
- **M1-clean 2016 remains the active JMP baseline.**
- **The corrected pooled P3a track is unaffected** and proceeds to its fresh
  strict post-estimation review on its frozen 100-diagonal, unconditional-
  wage spec.
- **The couples diagonal-to-product correction is a specification fix**; the
  occupation-conditioned wage draw (W1) is the first wage-opportunity
  correction; both are next-cycle data-rebuild decisions, bundled.
- **The two-group wage alternative must be tested against W1 in the pilot.**
- **The accepted-wage vs offer-wage distinction is an open form question**,
  not settled by the diagnostic.
- **The wage–occupation double-counting risk (delta_occ* vs beta_occ_*) must
  be resolved in the spec contract**, with separate-identification verified
  in the pilot.

---

*Status: next-cycle design memo. No authorization implied. M1-clean 2016
active. Frozen pooled P3a spec and its post-estimation track unaffected.
Next document: read-only pilot-feasibility audit (§28), then the pilot spec
contract + data-build authorization.*
