# JMP Couples Opportunity-Draw Design Note v1

*France RURO multi-year extension | v1 | 2026-05-21*

Document class: disposable design note (next-specification-cycle
decision). This note records a conceptual correction to the couples
choice-set construction and the design options for fixing it. It is
NOT an authorization. It does not authorise any data rebuild,
re-estimation, or change to the currently frozen pooled P3a
specification. It is a record for the next specification-and-data-
build cycle, after the current pooled baseline earns (or fails) its
SA2 verdict.

---

## 1. The correction (main point)

**Current couples construction:** for each couple, 100 opportunity
draws are taken for the male partner and 100 for the female partner,
and the two sets are combined **by index** — his draw *i* is paired
with her draw *i* — to form 100 joint couple-alternatives.

**Why this is conceptually weak.** The index pairing (a "zip")
produces the **diagonal** of the male × female joint opportunity
space: the 100 points {(his₁, her₁), (his₂, her₂), …, (his₁₀₀,
her₁₀₀)}. This is a 100-point curve through a 100 × 100 = 10,000-point
joint space. It is wrong as a representation of the couple's feasible
set for two distinct reasons:

1. **It excludes the off-diagonal combinations.** The couple's true
   feasible set is the set of (his job, her job) *combinations* — any
   of his available jobs can co-occur with any of hers. The diagonal
   presents only the index-matched pairs and silently drops every
   combination (his_i, her_j) with i ≠ j. The choice set is therefore
   not the feasible set; it is an arbitrary one-dimensional slice of
   it.

2. **It imposes a spurious dependence between partners.** Index
   pairing mechanically ties his *i*-th draw to her *i*-th draw, which
   is a perfect-rank-matching artifact with no economic content. If
   the model assumes the partners' opportunity draws are conditionally
   independent (the usual assumption), the correct joint sample is the
   **product** of the marginal draws, which represents independence;
   the diagonal represents maximal dependence — the opposite. If the
   model assumes some genuine dependence, the draw must come from the
   modelled joint distribution; the index pairing is still not that
   distribution. Either way, the diagonal is not the right object.

**The fix.** Keep the marginal per-partner draws (drawing 100 jobs per
partner is fine as a marginal sample), but change the **combination
rule** from index-pairing (diagonal) to a **product** — sample the
joint space (his job, her job), not its diagonal. The full product is
100 × 100 = 10,000 joint alternatives per couple; a coarser product
(e.g. 30 × 30 = 900 or 40 × 40 = 1,600) is a manageable approximation
to it.

This is the substantive correction: the move from diagonal to product
is a **specification fix** (the choice set currently mis-represents the
joint feasible set), not merely an accuracy refinement.

---

## 2. Specification fix vs accuracy refinement — be precise

Two separate things are at stake, and they should not be conflated.

**The diagonal → product change is a specification fix.** It corrects
*what the choice set represents*. The diagonal represents the wrong
feasible set (and imposes a spurious partner dependence); the product
represents the right one. This is a correctness issue, and it holds
regardless of how many draws are used: even at the same total alternative
count, a product sample is a more faithful representation of the joint
feasible set than the diagonal.

**The draw-count change (e.g. 900 vs 1,600 vs 10,000) is an accuracy
refinement.** Once the choice set is a product, the number of product
points controls the *simulation error* in the opportunity integral —
more product points means a tighter Monte-Carlo approximation, lower
simulation noise in the likelihood and the welfare integrals. This is a
numerical-accuracy gain, not a model change.

The order of importance is the specification fix first (use a product,
not a diagonal), then the accuracy decision (how dense a product).
Framing the change to a colleague or a referee, the headline is "the
couples choice set was the diagonal of the joint opportunity space; we
corrected it to a product sample," with the draw-count as a secondary
accuracy choice.

---

## 3. Why this matters for the JMP contribution

The couples opportunity structure is not incidental — it feeds the
opportunity-vs-preference decomposition that is the paper's
contribution.

The couples block contributes the joint labour-supply opportunities of
two-earner households to the money-metric well-being and its
decomposition. If the couples choice set is the diagonal, the joint
opportunity set is mis-represented for every couple, and the
opportunity-attributable component of couples' well-being inequality is
computed against a feasible set that is not the couple's actual feasible
set. Because couples are the majority of the sample (≈7,438 of 12,445
pooled household-years; ≈2,577 of 4,253 in the FR_2016 single-year
sample), a mis-specified couples feasible set is a first-order issue for
the decomposition, not a corner case.

The fix also interacts with the wage-density and wage-equation questions
raised separately (the occupation-conditional wage distributions and the
one-vs-two wage equations). All three are about how richly the couples'
opportunity/wage structure is represented. They share a computational
budget (§5) and should be decided together (§6).

---

## 4. Cost of the product options

The choice-set size is a property of the MNL parquet, fixed at data
preparation. Table 1 gives the per-couple alternative count and the
resulting couples row counts at the two sample scales (using the
established couple counts: 7,438 couple household-years pooled; 2,577
couples in FR_2016 single-year).

| Combination rule | Alt./couple | Couples rows (pooled, 7,438) | Couples rows (single-year, 2,577) |
|---|---|---|---|
| Diagonal (current) | 100 | 743,800 | 257,700 |
| Product 30 × 30 | 900 | 6,694,200 | 2,319,300 |
| Product 40 × 40 | 1,600 | 11,900,800 | 4,123,200 |
| Product 100 × 100 (ideal) | 10,000 | 74,380,000 | 25,770,000 |

The current 743,800 pooled couples rows confirm 100 alternatives per
couple. The full product (10,000) multiplies the couples data by 100×
— ~74M rows pooled — which is impractical for the precompute step and
for every gradient/Hessian evaluation. The 30 × 30 (900) and 40 × 40
(1,600) options are the manageable compromises your colleague
identified: ~6.7M and ~11.9M couples rows pooled, respectively.

Every figure above is the *couples* row count; the singles rows
(unchanged at 100/individual) add on top. The cost lands on three
places: storage/data-management of the parquet, the one-time precompute,
and — most bindingly — the per-iteration cost of the estimator, which
scales with the total choice-row count and is paid at every optimisation
step and every Hessian evaluation.

---

## 5. The wage-density interaction (binding on the sizing)

The couples draw-count decision must not be made in isolation from the
4-density wage extension (occupation-conditional wage distributions).
The two compete for the same computational budget:

- A richer per-job wage draw (occupation-conditional densities) raises
  the cost *per choice row* and adds parameters.
- A denser couples product raises the *number of choice rows*.

Doing both at full ambition (10,000-point couples product × 4-density
occupation-conditional wages) is the dimensionality explosion you
flagged. The two must be sized **jointly against one budget**: a
moderate couples product (e.g. 900) with occupation-conditional wages
may be both more correct *and* cheaper than a large couples product
(1,600) with a single wage density — and it fixes two specification
issues at once. The right move is to treat the couples product size and
the wage-density richness as a single joint design choice, not two
independent knobs.

---

## 6. How to size the product — convergence, not feel

Do not pick 900 vs 1,600 by judgement. Convert it into a **simulation-
consistency check**: build the couples block at several product sizes
(e.g. 400, 900, 1,600) and evaluate whether the key estimates and the
welfare quantities **stabilise** as the product grows. If 900 gives
materially the same parameter estimates and decomposition as 1,600,
then 900 is sufficient and 1,600 buys only cost. If they are still
moving, go denser. This yields a citable justification ("estimates were
stable beyond N product points") that referees in this literature
expect for couple models.

Two refinements that relieve the dimensionality pressure directly:

1. **Quasi-random draws (Halton / Sobol).** If the current draws are
   pseudo-random, switching the couples draws to a low-discrepancy
   sequence cuts the number of product points needed for a given
   accuracy substantially — often a moderate product with Halton draws
   matches a much larger product with pseudo-random draws. This is the
   highest-leverage, lowest-cost lever: it reduces the *count* you need
   without changing the *correctness* (it's still a product, just a
   better-spread one).

2. **Asymmetric / randomised product.** The product need not be a fixed
   30 × 30 grid; a random subsample of the 100 × 100 product (e.g. 900
   randomly drawn (i, j) pairs) is also a valid joint sample and avoids
   the grid-edge artifacts of a fixed coarse grid. A randomised product
   is generally preferable to a coarse deterministic grid for the same
   point count.

---

## 7. One factual item to confirm

Confirm, on the current couples parquet, that the 100 alternatives are
indeed the index-paired diagonal (his_i with her_i), not some other
structure. The note proceeds on your statement that they are index-
combined, which the 743,800 pooled couples row count is consistent with.
The confirmation matters because it determines whether the fix is purely
a combination-rule change (diagonal → product, marginal draws preserved)
or also requires re-drawing the marginals. The former is the expected
case.

A second item to confirm at design time: the **partner-dependence
assumption**. If the model treats the partners' opportunity draws as
conditionally independent, the product is the correct joint sample. If
some dependence is intended (e.g. assortative matching in opportunity),
the joint draw must encode it, and the product-of-independent-marginals
is itself an approximation. State the assumption explicitly in the
respecification memo; do not leave it implicit (as the diagonal currently
does, where it silently imposes maximal dependence).

---

## 8. Gating and timing — this is a next-cycle data rebuild

This change is upstream of nearly everything in the current pipeline. The
couples choice set is set at **data preparation**, before EUROMOD and
before the GSUR merge. Moving from the diagonal to a product means
re-doing the couples data preparation, re-running EUROMOD on the new
joint alternatives to obtain their disposable incomes, re-merging GSUR,
and re-stacking the pool — i.e. re-running the GSURv2 pipeline (the work
of this entire session) for the couples, on a parquet ~7–14× larger.

Therefore:

- **Do NOT fold this into the currently authorized pooled P3a
  estimation.** That estimation runs on the frozen 100-alternative
  spec. This change would invalidate that spec and the run.
- **The current pooled baseline should finish on the existing spec** and
  earn (or fail) its SA2 verdict. The diagonal-vs-product correction is a
  property of the *next* data build and the *next* specification, not a
  mid-flight edit.
- **Even the simulation-consistency investigation is not read-only here.**
  Unlike the wage-distribution diagnostics (which read existing
  parquets), the convergence check requires *building* denser-product
  couples samples to test on. That is itself a data-build task and
  belongs to the next cycle.

This correction, bundled with the wage-occupation-conditioning and the
one-vs-two-wage-equation questions, defines the **next respecification-
and-rebuild cycle**. All three are "enrich the couples opportunity/wage
structure" decisions; they share a computational budget and should be
specified together in a single respecification memo, gated as a new
specification (not a silent edit to the baseline), after a credible
pooled baseline exists.

---

## 9. Recommended sequencing

1. **Now:** let the authorized pooled P3a estimation run on the frozen
   100-alternative spec; complete the post-estimation review / SA2-
   readiness verdict and, if it passes, the SA2 verdict. (This note
   changes none of that.)

2. **Confirm the factual items (§7)** — that the current couples
   alternatives are the index-paired diagonal, and the intended partner-
   dependence assumption. These can be settled by inspection / discussion
   without a data build.

3. **Next cycle — respecification memo.** Specify jointly: (a) couples
   choice set = product sample (not diagonal), with the product size
   chosen by simulation-consistency + Halton/Sobol; (b) the wage-density
   decision (occupation-conditional vs common); (c) the wage-equation
   decision (one vs two). Size (a) and (b) against one computational
   budget (§5). Gate this as a new specification with its own spec
   contract and data-build authorization.

4. **Next cycle — data rebuild + re-estimation** of the product-based
   couples specification, evaluated against the current baseline (the
   diagonal-based pooled spec becomes the comparison point, not the
   final).

---

## 10. Bottom line

Your colleague is right that couples need the joint space, and you are
right that the current index-paired diagonal is the conceptual weak
point — it is the primary correction, and it is a *specification* fix
(the choice set mis-represents the joint feasible set), not just an
accuracy gain. The fix is a product sample; the full 100 × 100 is ideal
but impractical; a 900- or 1,600-point product (preferably a randomised /
Halton product, sized by a simulation-consistency check) is the
manageable and more-correct compromise. It must be sized jointly with the
wage-density extension, and it is a next-cycle data-rebuild decision — not
a change to the currently authorized estimation. Let the baseline finish;
carry this into the next respecification cycle, bundled with the two wage-
structure questions.

---

*Status: disposable design note. No authorization implied. Next-cycle
decision. The current pooled P3a estimation and the frozen 100-alternative
spec are unaffected. M1-clean 2016 remains the active JMP baseline.*
