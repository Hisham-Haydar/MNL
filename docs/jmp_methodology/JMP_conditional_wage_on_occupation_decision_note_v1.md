# Conditional Wage Distributions on Occupation — Decision Note v1

*France RURO multi-year extension | v1 | 2026-05-21*

Document class: design decision note. Lightweight — this records a
decision and the diagnostic that arbitrates it. It is not an
authorization chain. The diagnostic below is read-only and may be run
now; any resulting model change is a next-rebuild-cycle decision and
does not touch the currently frozen pooled estimation.

---

## 1. The issue

In the RURO opportunity framework the wage offer is one component of the
opportunity measure, and the standard simplification draws the wage
**independently** of the other job attributes (the orthogonality /
factorisation assumption): a wage is drawn from a common distribution and
attached to a separately drawn job.

This is defensible on the **labour-time** margin: hours are quasi-
continuous, and after conditioning on the wage-equation covariates the
wage–hours relationship is weak, so an unconditional wage draw does not
badly misrepresent feasible (wage, hours) bundles.

It is **not** automatically defensible on the **occupation** margin. The
occupation layer is four coarse, economically distinct classes
(routine-manual / non-routine-manual / intellectual / non-intellectual —
the `loc4` taxonomy), and these classes plausibly sit at systematically
different locations *and spreads* of the wage distribution. Drawing a wage
unconditionally and attaching it to a drawn occupation can produce
incoherent job packages — a routine-manual job paid at a professional
wage, or vice versa. The coarseness is precisely what breaks the
near-continuity defence that works for hours.

This matters for the JMP because the wage offer distribution **is** the
wage-opportunity layer of the decomposition. If wages and occupations are
correlated in the true opportunity structure but the model imposes
independence, the wage-opportunity and occupation-opportunity components
are mis-attributed relative to each other — a soft spot in a paper whose
contribution is the consistent treatment of opportunities.

The colleague's point is correct in structure: the orthogonality defence
transfers to hours but not to coarse occupation classes.

---

## 2. Decision

**We will condition the wage draw on occupation if — and the evidence is
expected to show this — the occupation-conditional wage distributions are
materially separated. The diagnostic in §4 is the arbiter, and it is run
before the next data build.**

Concretely:

- **Decided now:** run the read-only conditional-wage-by-occupation
  diagnostic (§4) on the existing data. This commits no model change and
  touches no frozen artifact.

- **Decision rule (pre-committed):**
  - If the occupation-conditional wage distributions are **materially
    separated** (§4 criteria) → **adopt occupation-conditional wage draws**
    in the next respecification-and-rebuild cycle. This is the expected
    outcome given the labour literature on these occupation classes.
  - If they **substantially overlap** → **retain the unconditional draw**
    and document the empirical justification (the diagnostic itself becomes
    the citable defence of the simplification).

- **Timing:** any change to conditional draws is a **next-cycle data
  rebuild** (the wage draws are set at data preparation, upstream of
  EUROMOD and GSUR), bundled with the couples product-sample correction,
  since both require the same rebuild. It does **not** alter the currently
  authorized pooled estimation; the current baseline finishes on the frozen
  spec.

This is a real decision: it fixes the *rule* and the *test* now, and
pre-commits the action to the evidence, rather than leaving the question
open.

---

## 3. One thing that sharpens the decision

Where occupation `loc4` currently sits in the model affects how strong the
fix needs to be:

- If occupation is in the **opportunity** layer (and the wage opportunity
  is drawn independently of it), occupation-conditional wages are arguably
  *required* for internal consistency — the occupation-opportunity layer is
  supposed to capture "what kinds of jobs, with their characteristic pay,
  are available," which an unconditional wage contradicts.
- If occupation enters only as a **utility** shifter and the opportunity
  layer is purely hours/wage, the concern changes shape (it becomes whether
  the utility-side occupation effect is silently absorbing the
  wage–occupation correlation).

Confirm which case applies before finalising the modelling form. The
diagnostic in §4 is informative either way.

---

## 4. The diagnostic (read-only, run now)

On the existing MNL data, using each worker's **observed/chosen**
alternative (not the simulated draws), restricted to workers (`loc4` in
the positive occupation codes; exclude the `-2` unknown-working and `-1`
non-worker stubs):

**Compute, by `loc4` × sex (`dgn`), for the wage variable used in the
Mincer block (log wage recommended):**
- count, mean, median, SD, and the p10 / p25 / p50 / p75 / p90 quantiles.

**Compare to the unconditional (pooled-over-occupation) wage distribution,
separately by sex.**

**Separation metrics:**
- A one-way ANOVA of log wage on `loc4` (by sex): report η² (the share of
  log-wage variance explained by occupation).
- Pairwise occupation mean-log-wage differences.
- Overlap of the occupation interquartile ranges.

**Reading the result (guide, not rigid cutoffs):**
- η² **large** (roughly > 0.10–0.15), means well separated, IQRs largely
  non-overlapping → **materially separated** → condition wages on
  occupation (next cycle).
- η² **small** (roughly < 0.05), means close, IQRs largely overlapping →
  **overlap** → retain unconditional draw, document the defence.
- In between → judgement, leaning on the IQR-overlap picture and the
  decomposition stakes.

**Output:** a short table (the conditional vs unconditional summaries) plus
occupation-conditional density plots, by sex. This is a few lines of pandas
on the existing parquet; it modifies nothing.

A subtlety to note when reading the result: observed wages are conditional
on holding the job, i.e. they reflect the *accepted-wage* distribution, not
the pure *offer* distribution. Selection can compress or shift the
conditional distributions. This does not change the decision rule (sharp
separation in accepted wages is still strong evidence against an
unconditional offer draw), but it should be flagged when the result is
written up, and it is one more reason an occupation-conditional offer
distribution — properly handling selection — is the cleaner object if the
diagnostic confirms separation.

---

## 5. Bottom line for your colleague

The point is right and is taken. The orthogonality defence holds for hours
(near-continuous) but not for the four coarse occupation classes
(systematically different wage distributions). The decision is: run the
read-only conditional-wage-by-occupation diagnostic now; if the
distributions are materially separated (expected), adopt
occupation-conditional wage draws in the next rebuild cycle, bundled with
the couples product-sample correction; if they overlap, keep the
unconditional draw with the diagnostic as the documented justification. The
current authorized pooled estimation is unaffected — this is a next-cycle
specification decision, pre-committed to the evidence.

---

*Status: design decision note. The diagnostic is read-only and may be run
now. Any conditional-wage model change is a next-cycle data-rebuild
decision, bundled with the couples product-sample correction, and does not
affect the frozen pooled P3a spec or the currently authorized estimation.*
