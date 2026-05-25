# JMP NC Pilot — Spec Contract v1

*France RURO multi-year extension | v1 | 2026-05-22*

**Document category: pilot spec contract.** This document fixes the
specification and authorizes the *scope and conditions* of a future
2016-couples-only pilot build. It does **not** execute the build. It does
not run EUROMOD, estimation, welfare, or SA2. It resolves the five blockers
named by the read-only feasibility audit
(`Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md` §20) so that the build can
be authorized as a separate, gated step. M1-clean 2016 remains the active
JMP baseline throughout. The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To convert the next-cycle design plan
(`docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md`) and the
read-only feasibility audit (`Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md`)
into a fixed, buildable pilot specification, by resolving the five
spec-contract decisions the audit identified as hard blockers:

1. wage-occupation double-counting (§13);
2. accepted-wage vs offer-wage object (§14);
3. joint draw-index convention (§6);
4. row-count guards / pilot driver (§17);
5. Mincer fitting set (§15).

The contract fixes each of these as a *decision*, defines exactly what the
pilot builds, and specifies the validation checks the build report must
satisfy. It is the first document in this track that may authorize building
anything — and it authorizes only the narrow pilot scope of §4, gated by the
halt conditions of §26.

---

## 2. Current status

- **Active baseline:** M1-clean 2016. Not displaced.
- **Corrected pooled P3a:** three starts converged identically (joint LL
  −19,084.3313), region block repaired, true-Hessian cluster-robust SEs
  computed (T3 = 9,657 clusters, T4 = 0, T5 = 0). No welfare, no SA2, no
  canonical promotion. Its next event is a fresh strict post-estimation
  review / SA2-readiness verdict on its **frozen 100-diagonal,
  unconditional-wage spec**. That track is independent of this contract.
- **Read-only diagnostic:** confirmed W1 warranted (η² = 0.159; separation
  concentrated on loc4 = 4) and the couples diagonal (index-paired,
  off-diagonal absent).
- **Read-only feasibility audit:** pilot feasible at 900 alts conditional on
  resolving the five blockers; 2016 couples n confirmed at **2,577**;
  `scipy.stats.qmc` (Halton/Sobol) importable (scipy 1.16.2); marginal draws
  reusable for the product (combination-rule change), but the W1 wage change
  forces a marginal re-draw.

This contract resolves the five blockers and fixes the pilot spec.

---

## 3. Why this is a pilot contract, not a full P3a rebuild

The pilot is a **feasibility-and-design instrument**, not a result. It is
deliberately the smallest build that exercises every changed code path
end-to-end:

- **Scope-limited:** 2016 couples only, one year, one household type, one
  product size (900). This is ~9× the current 2016 couples rows (257,700 →
  2,319,300), not ~9× the full pooled pipeline.
- **Purpose-limited:** to (a) verify the corrected pipeline runs end-to-end,
  (b) *measure* the EUROMOD / precompute / gradient cost the audit could not
  predict, (c) decide W1 vs two-group, (d) test the wage-occupation
  separate-identification question, (e) run the 400/900/1,600
  simulation-consistency points.

A full P3a rebuild (pooled 2015–2017, singles + couples, product at the
chosen size, with the verdict-grade estimation and SE machinery) is a
*later* cycle, authorized by a *different* document only after the pilot
succeeds and reports its measured budget. This contract does not authorize
that.

---

## 4. Pilot scope

**In scope (and authorized as scope, gated by §26):**

- **Population:** couples only.
- **Year:** FR_2016 only (2016 couples n = 2,577, audit-confirmed).
- **Choice set:** product sample at **30 × 30 = 900** joint alternatives per
  couple (couples rows = 2,319,300).
- **Wage:** W1 (occupation intercepts, common slopes, reference loc4 = 1) as
  the pilot baseline; two-group (1[loc4=4]) as the documented comparison.
- **Occupation draw:** `occ_spec = "fixed"` retained.
- **Variance:** single common `sigma`.
- **Draw method:** Halton/Sobol or randomised product if implementable;
  pseudo-random fallback documented.
- **Simulation-consistency points:** 400 / 900 / 1,600 (couples block built
  at each for the convergence check).

**Out of scope (not this contract):**

- Singles rebuild (singles parquet unchanged at 500,700 rows; singles draws
  remain 100/individual). Singles disposable income is already computed and
  is **not** re-run.
- Pooled 2015–2017 stacking.
- W2 (occupation × sex), occupation-specific sigma (S-occ), selection-
  corrected offer Mincer (OFF) — all later refinements.
- Welfare, SA2, canonical promotion, M1-clean displacement.

---

## 5. Couples diagonal-to-product correction

**Decision: replace the index-paired diagonal with a 900-point product
sample.** The combine step in `_reshape_couples_to_wide()`
(`enh_RURO_prep_mnl_basic.py:1058-1065`) — currently an `inner` merge on
`["idhh", "draw"]` producing his_i ↔ her_i — is replaced by a cross-join on
`idhh` over the first 30 male and first 30 female marginal draws, producing
30 × 30 = 900 joint alternatives per couple.

The validation invariants preceding the merge (`prep_mnl_basic.py:922-944`,
exactly 2 rows per (idhh, draw)) are re-expressed for the product: exactly
one male record and one female record per joint key per household.

**Partner-dependence assumption (stated, not implicit):** the pilot adopts
**conditional independence** of the partners' opportunity draws. The product
of the marginal draws is the correct joint sample under this assumption. The
diagonal's silent imposition of maximal dependence is the defect being
corrected. If a later cycle wants assortative opportunity dependence, that
is a different joint draw and a different contract.

**Marginal-draw reuse:** the audit confirms the marginal per-partner draws
are reusable as-is for the *combination-rule* change. The pilot nonetheless
re-draws marginals because the W1 wage change (§9) requires it; the product
then uses the first 30 of each re-drawn marginal.

---

## 6. Joint draw-index convention

**Decision (resolves audit blocker 3).** The pilot preserves three explicit
draw identifiers on every couples row:

- `draw_male` ∈ {0, …, 29} — the male partner's marginal draw index.
- `draw_female` ∈ {0, …, 29} — the female partner's marginal draw index.
- `draw_joint` ∈ {0, …, 899} — the joint key, defined as
  `draw_joint = 30 · draw_male + draw_female`.

Both partner-level indices are retained (not collapsed into the joint key
only) so the marginal structure is auditable and the convergence check can
subset by partner draw. Downstream consumers that previously relied on a
single integer `draw` column read `draw_joint`.

**Required downstream audit (build step, not assumed):** every site that
currently encodes `draw == 0` semantics (precompute, estimation,
post-estimation) must be checked for hard-coded reliance on the single-
integer `draw` column and re-pointed to `draw_joint` where appropriate. The
audit (§20.3) flagged this surface as not exhaustively grepped; the build
must grep it and report the sites it changed.

---

## 7. Chosen alternative convention

**Decision.** The observed (chosen) couple alternative is the row where
`draw_male == 0 AND draw_female == 0`, i.e. `draw_joint == 0`. This
preserves the existing convention that the observed alternative is the
zero-index draw, now expressed jointly. The build must preserve the
invariant `is_chosen_male == is_chosen_female` for that row and assert that
exactly one row per couple satisfies `draw_joint == 0`.

---

## 8. Product-sample size

**Decision: 30 × 30 = 900 for the pilot baseline.** 2016 couples rows =
2,319,300 (9× the current 257,700). The simulation-consistency check (§23)
builds the couples block at **400 (20×20), 900 (30×30), and 1,600 (40×40)**
to test whether estimates and the decomposition stabilise. 10,000 (100×100)
is conceptually clean but infeasible (100× rows) and is not built. If
Halton/Sobol materially reduces the count needed for stable estimates (§16),
a sub-900 product may be reported as sufficient — that is a finding of the
pilot, not a pre-set size.

---

## 9. Wage correction W1

**Decision: pilot baseline wage model is W1.**

```
log w = beta_w0 + beta_w_educL·educL + beta_w_educH·educH
        + beta_w_pexp·pexp_years + beta_w_pexp2·pexp_years2
        + delta_occ2·1[loc4=2] + delta_occ3·1[loc4=3] + delta_occ4·1[loc4=4]
        + epsilon,    epsilon ~ Normal(0, sigma²)
```

Reference category `loc4 = 1` (Routine-Manual), matching the existing
`occupation_opportunity` block reference. Common Mincer slopes; single
common `sigma`.

**Implementation (audit §6–§7):** the current unconditional draw
`Uniform[w_min, w_max]` at `enh_RURO_draws.py:1196-1204` is replaced by
sampling log w from `Normal(X_i β + δ_{loc4_i}, σ²)` and exponentiating,
where `loc4_i` is the simulated person's occupation (= observed occupation
under `occ_spec="fixed"`). **The proposal-density term must be replaced in
lockstep:** the uniform term `-log(w_max − w_min)` at
`enh_RURO_draws.py:1225-1234` becomes the log-normal density at the drawn
wage, or the importance-sampling correction is inconsistent. This is a
named build requirement, not an optional refinement.

A **pre-draw Mincer fit step** is added to the pipeline: fit W1 → write
coefficients (tagged with fitting set, §15) → consume in `enh_RURO_draws.py`.

---

## 10. Two-group wage alternative

**Decision: the two-group model must be estimated or documented as a
comparison; W1 remains the pilot baseline.**

```
log w = X β + delta_NonInt·1[loc4=4] + epsilon
```

One occupation parameter instead of three. Motivated by the diagnostic
finding that RM-vs-NRM IQR overlap is 87–97% and Intel separation is modest
— the binding separation is loc4 = 4 vs the rest. The pilot compares W1 and
two-group on (a) wage-draw realism, (b) the resulting decomposition. **If
two-group reproduces W1's decomposition,** the contract's standing
recommendation is to ship the parsimonious model in the full cycle — but
that promotion is a later-cycle decision, not authorized here. The
comparison is mandatory; the conclusion is reported, not pre-judged.

---

## 11. W2 occupation × sex as later refinement

**Decision: W2 is NOT in the pilot.** Occupation × sex wage intercepts are
supported by the descriptive evidence (loc4 × sex F = 13.86) but contribute
far less than occupation (ΔR² 0.011 vs 0.066), add ~5–8 parameters over W1,
and hit thin cells (Intel-Male n = 104 in singles). W2 is tested only in a
later cycle, only if the W1 pilot runs cleanly and the decomposition
motivates it. The pilot does not estimate W2.

---

## 12. Common sigma versus occupation-specific sigma

**Decision: single common `sigma` for the pilot.** The diagnostic shows
residual SD is heteroskedastic across occupations (NRM ≈0.43–0.46,
Intel-Female ≈0.28), so occupation-specific sigma (S-occ) is a defensible
later variant (+3 variance parameters). But the pilot isolates the
mean-shift correction with one variance parameter; occupation-specific sigma
is tested only if the pilot shows the common-sigma W1 leaves material
residual heteroskedasticity that moves the decomposition. Not in the pilot
baseline.

---

## 13. Wage-occupation double-counting rule

**Decision (resolves audit blocker 1).** loc4 enters the choice index in two
places, on **different channels**:

- `delta_occ*` (wage block, new in W1) shifts the **wage level**, which flows
  into consumption → disposable income → utility. It changes *how much a job
  pays*.
- `beta_occ_*` (occupation_opportunity block, existing, 12 shifters) shifts
  the **opportunity mass / availability** of the occupation in the
  market-opportunity index. It changes *how available a job type is*.

These are conceptually distinct (pay level vs availability weight), which is
what permits separate identification **in principle**. The contract requires
this be **verified, not assumed**, via a mandatory pilot check (§23):

1. Information-matrix diagonals on `delta_occ*` and `beta_occ_*` (no
   near-singularity / no extreme correlation between the two blocks).
2. Cross-start stability of both coefficient sets.
3. Comparison of estimated `delta_occ*` against the pre-fitted Mincer values
   to flag drift.

**Pilot resolution of the free-vs-calibrated question:** in the pilot, the
W1 `delta_occ*` are **calibrated** — fit in the pre-draw Mincer step (§15),
fixed at the draw stage, and **not re-estimated as free structural
parameters**. This is the audit's §11 fallback adopted *as the pilot
default*, because it removes the double-counting risk by construction: the
occupation premium enters the wage *draw distribution* (data-build input),
while `beta_occ_*` remains the only *free* occupation parameter at the
structural stage. Free structural estimation of `delta_occ*` is deferred to
a later cycle and only if the separate-identification check (run as a
diagnostic even under calibration) supports it.

Consequently the pilot's structural free-parameter count stays at **55**
(the calibrated `delta_occ*` add no free parameters); the W1/two-group
distinction lives entirely in the draw distribution.

---

## 14. Accepted-wage versus offer-wage object

**Decision (resolves audit blocker 2).** The pilot fits W1 on **accepted
wages** (observed draw=0 working alternatives) and uses this as a
**documented approximation** to the wage-offer distribution. No
selection-corrected offer model is required for the first pilot.

The build report and any write-up must state explicitly: the wage-
opportunity layer is conceptually an *offer* distribution; the pilot's
accepted-wage fit is selected on employment within each occupation; if
selection differs across loc4, the offer separation may differ from the
measured accepted separation. This is recorded as a stated limitation, with
an occupation-conditional selection-corrected offer Mincer (OFF) named as
the next refinement if the pilot motivates it. The keep/condition decision
is unaffected (sharp accepted separation is strong evidence against an
unconditional offer draw); only the *form* carries the caveat.

---

## 15. Mincer fitting set

**Decision (resolves audit blocker 5).** The W1 (and two-group) Mincer is
fit on the **working observed (draw=0) sample, loc4 ∈ {1,2,3,4}, wage > 0,
pooled across singles and couples**.

On the year dimension: **use pooled 2015–2017 accepted working wages with
year controls if the pooled working sample is available at fit time;
otherwise fall back to 2016-only and flag thin-cell risk** (some loc4 × sex
cells are thin, e.g. Intel-Male n = 104 in singles). The pooled fit is
preferred because it strengthens the wage equation even though the pilot
rebuild is 2016-only; using out-of-pilot years to inform the wage draw is a
deliberate, documented choice, not a leak. The fitted coefficients are
tagged with their fitting set (years, population) so the draw stage is
auditable.

---

## 16. Draw method and randomization

**Decision.** Use a low-discrepancy sequence for the couples product if
implementable: **Halton preferred** (less sensitive to non-power-of-2
lengths than Sobol; 30 and 900 are not powers of 2), Sobol acceptable with
scrambling. `scipy.stats.qmc` is confirmed importable (scipy 1.16.2). If the
low-discrepancy implementation is not cleanly droppable into the four
`rng.uniform` call sites (`enh_RURO_draws.py`, audit §14), the **pseudo-
random fallback (PCG64, current seed discipline) is documented and used**,
and the consistency check (§23) carries the full accuracy burden. Record
sequence + seed + scramble in the build report. Seed-and-log discipline is
already in place (couples seed = singles seed + 1, logged to run JSON).

---

## 17. Row-count guards and pilot driver

**Decision (resolves audit blocker 4).** The hard-coded guards in
`prepare_pooled_estimation_ready.py:70-72`
(`EXPECTED_TOTAL_ROWS = 1_244_500`, `EXPECTED_HH_YEARS = 12_445`) are
pooled-3-year diagonal expectations and will raise on the pilot parquet.
**The pilot must NOT edit the production guards in place.** Resolve by:

- **A separate pilot driver/config** (preferred) with pilot-specific
  expected counts (2016 couples: 2,319,300 rows at 900 alts; singles
  unchanged), **or**
- an explicit **`--pilot` mode** that swaps the expected counts when the flag
  is set, leaving the production defaults untouched.

The production P3a pipeline must remain runnable on its frozen spec with no
behavioural change when the pilot flag/driver is absent.

**Country/year/spec-agnostic design requirement.** Where feasible, the pilot
code (product join, joint-draw keying, conditional wage draw, expected-count
config) must be written **without hard-coding France / P3a / 2016 / 900**.
Use parameters/config for: country, year set, product size (the 30 and the
joint-key multiplier), reference occupation, and the Mincer fitting set. The
goal is that the pilot code can later be promoted into the reusable package
(for France 2021, singles, Germany, other product sizes) without a rewrite.
Hard-coded constants are permitted only where genuinely unavoidable and must
be flagged in the build report as promotion debt.

---

## 18. Required data-prep changes

(Authorized as pilot scope; gated by §26.)

1. **`enh_RURO_draws.py`** — replace unconditional wage draw (lines
   1196-1204) and its proposal-density term (lines 1225-1234) with the W1
   log-normal draw + matching density; retain `occ_spec="fixed"` (line 114
   default); switch couples product draws to Halton/Sobol if implementable
   (else documented pseudo-random). Regenerate marginals (forced by the wage
   change).
2. **`enh_RURO_prep_mnl_basic.py`, `_reshape_couples_to_wide()`** — replace
   diagonal merge (lines 1058-1065) with a 30×30 cross-join on `idhh`; emit
   `draw_male`, `draw_female`, `draw_joint`; preserve validation invariants
   under the new keying.
3. **Pre-draw Mincer fit step (new)** — fit W1 and two-group on the §15
   sample; write tagged coefficients consumed by `enh_RURO_draws.py`.
4. **Pilot driver / `--pilot` mode** — pilot-specific expected counts (§17),
   production guards untouched.
5. **Spec config (new, not an edit to P3a YAML)** — record W1 calibration,
   reference loc4 = 1, common sigma, product size, draw method, fitting set.

---

## 19. Required EUROMOD rerun

EUROMOD must run on **every new joint product alternative** to obtain
couples disposable income (`ils_dispy_male`, `ils_dispy_female`). Pilot
surface: **2,577 couples × 900 = 2,319,300 EUROMOD evaluations.** Singles
are not re-run (singles draws unchanged; singles disposable income already
computed). This is the binding data-build cost and the reason the
correction is not a quick edit. Throughput/wall time is one of the pilot's
measurement objectives.

---

## 20. Required GSURv2 merge

After EUROMOD: re-merge GSUR market-opportunity proxies on the product
alternatives. The P3a GSUR is **centred within choice set**
(`center_within_choice_set: true`, proposal weights); because the choice set
changes from 100 to 900, the centring is **re-computed on the new product
set**, not copied from P3a. The build must verify GSUR centring is re-run,
not inherited.

---

## 21. Required MNL rebuild

Rebuild the couples wide-format parquet under the product combine rule
(§5–§7). Produce the split-stem `__singles` (unchanged) / `__couples`
(product) parquets and a pilot `__mnlmeta.json` with **couples `n_draws`
redefined to 900** (singles `n_draws` remains 100). Verify income routing
intact; re-apply the R1 region repair if the rebuild reintroduces the
all-NaN couples region columns (the P3a defect that was repaired). Verify
the one-region-per-household partition holds on the product rows.

---

## 22. Required precompute checks

Before any estimation timing, the build must confirm on the pilot parquet:

- `precompute_data_couples()` (`estimation_utils.py:902`) runs to completion
  on 2,319,300 couples rows; report transient memory and wall time (≈9×
  couples factor expected).
- Region arrays non-zero and matching the one-region partition (the PS1/PS2
  checks from the P3a report, re-applied to the pilot).
- `draw_joint == 0` selects exactly one chosen row per couple; chosen-row
  invariants hold.
- Income routing (`ils_dispy_male/female`) populated for all product
  alternatives; no all-NaN couples disposable-income regression.

---

## 23. Required pilot validation checks

The pilot build report (§27) must contain:

1. **Pipeline end-to-end confirmation** — draws → EUROMOD → GSUR merge →
   MNL build → precompute, with row counts at each stage.
2. **Wage-occupation separate-identification check** (§13) — information-
   matrix diagonals, cross-start stability, calibrated-vs-estimated drift.
   (Run as a diagnostic even though `delta_occ*` are calibrated in the
   pilot, to inform the later free-estimation decision.)
3. **W1 vs two-group comparison** (§10) — wage-draw realism and decomposition
   effect.
4. **Simulation-consistency** (§8, §23 of plan) — estimates and decomposition
   at 400 / 900 / 1,600; verdict on the sufficient product size.
5. **Computational budget** — measured precompute and gradient/Hessian wall
   time at 900 alts, to size the full cycle.
6. **Draw-method record** — sequence, seed, scramble; whether Halton/Sobol
   reduced the count needed below 900.
7. **Accepted-wage caveat** (§14) stated.
8. **Promotion-debt list** — any hard-coded France/P3a/2016/900 constants
   (§17).

---

## 24. What is authorized

This contract authorizes, **and only as the pilot scope of §4, gated by the
halt conditions of §26**:

- Building the 2016 couples-only pilot data: the W1 (and two-group) pre-draw
  Mincer fit; regenerated marginal draws with the W1 wage draw; the 30×30
  product couples parquet at 900 alts; the pilot driver / `--pilot` mode with
  pilot-specific guards.
- Running EUROMOD on the 2,319,300 pilot couples alternatives.
- The GSURv2 re-merge and MNL rebuild for the pilot couples block.
- The precompute checks (§22) and the simulation-consistency builds at
  400/900/1,600.
- A pilot estimation **for the purpose of the validation checks in §23**
  (separate-identification, W1-vs-two-group, consistency, budget timing) —
  explicitly **not** a verdict-grade or canonical estimation.

---

## 25. What is not authorized

- Full P3a rebuild (pooled 2015–2017, singles + couples).
- Pooled stacking.
- Singles rebuild or singles EUROMOD re-run.
- W2, occupation-specific sigma, free structural `delta_occ*`, selection-
  corrected offer Mincer — all later cycle.
- Welfare computation.
- SA2 verdict.
- Canonical promotion of any pilot output.
- Displacement of M1-clean 2016.
- Any edit to the frozen pooled P3a YAML or any in-place edit to the
  production `prepare_pooled_estimation_ready.py` guards.
- Any interruption of the corrected pooled P3a post-estimation track.

---

## 26. Halt conditions

The build halts and reports (does not work around) if any of these fire:

| Halt | Condition |
|---|---|
| **HP1** | Production P3a pipeline behaviour changes when the pilot flag/driver is absent (guard edit leaked into production). |
| **HP2** | The W1 proposal-density term is not updated in lockstep with the wage draw (importance-sampling inconsistency). |
| **HP3** | `draw_joint == 0` does not select exactly one chosen row per couple, or `is_chosen_male ≠ is_chosen_female`. |
| **HP4** | Couples disposable income is all-NaN or unpopulated for any product alternative after EUROMOD. |
| **HP5** | GSUR centring is inherited from P3a rather than re-computed on the product choice set. |
| **HP6** | Region columns reintroduce the all-NaN couples defect and R1 is not re-applied. |
| **HP7** | The separate-identification check (§13) shows `delta_occ*` and `beta_occ_*` are not separately identified **and** the pilot has nonetheless estimated `delta_occ*` as free (it must not — pilot calibrates). |
| **HP8** | Any attempt to compute welfare, issue SA2, promote a pilot output, displace M1-clean, or run beyond couples-2016 scope. |
| **HP9** | Pilot row count ≠ 2,577 × (product size) for couples, or singles parquet row count changes from 500,700. |

Any halt → stop, write the build report up to the halt, await a contract
amendment. Do not silently fix and continue.

---

## 27. Required pilot build report

The build produces **one** report:
`Results/NC_pilot/JMP_NC_pilot_build_report_v1.md`, with headings covering: scope and
authorization provenance; data-prep changes made (with the exact files and
line ranges changed, and the downstream `draw_joint` re-pointing sites);
pre-draw Mincer fit (coefficients, fitting set, accepted-wage caveat);
draw-method record; EUROMOD run (counts, wall time); GSUR re-merge (centring
re-computed confirmation); MNL rebuild (row counts, n_draws=900 for couples);
precompute checks (§22); the §23 validation checks including the
separate-identification diagnostic, W1-vs-two-group comparison, and the
400/900/1,600 consistency results; measured computational budget; halt-
condition status (none/which fired); promotion-debt list; and the required
final statements (M1-clean active; P3a track unaffected; no welfare; no SA2;
no canonical promotion; pilot scope only).

---

## 28. Exact Claude Code pilot-build prompt

Use **Claude Code (Sonnet)**, local. This is the first build step in the
track — it writes/regenerates pilot data on the **pilot driver only**, and
must not touch production guards or the frozen P3a spec.

```text
Work locally in my RURO/MNL codebase. PILOT BUILD — 2016 couples only,
authorized by docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md (pilot scope only).

HARD CONSTRAINTS (halt and report if any would be violated):
- Do NOT edit the production prepare_pooled_estimation_ready.py guards in
  place. Use a SEPARATE pilot driver/config OR a --pilot mode that leaves
  production defaults untouched.
- Do NOT modify estimation_spec_ruro_occ_P3a_pooled.yaml.
- Do NOT touch the corrected pooled P3a estimation, its artifacts, or its
  run directories.
- Do NOT compute welfare. Do NOT issue SA2. Do NOT promote any output.
  Do NOT displace M1-clean 2016.
- Couples only, FR_2016 only, 900 (30x30) product. Singles parquet must NOT
  change (assert 500,700 rows unchanged).
- delta_occ* are CALIBRATED (fit in a pre-draw Mincer step, fixed at draw
  time), NOT free structural parameters. Structural free-parameter count
  stays 55.

Read first (do not assume; confirm from these):
- docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md
- Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md
- docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md
- scripts/enhanced/enh_RURO_draws.py
- scripts/enhanced/enh_RURO_prep_mnl_basic.py
- scripts/maintenance/prepare_pooled_estimation_ready.py
- scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml

Build steps (pilot driver only):
1. Pre-draw Mincer fit: fit W1 (delta_occ2/3/4, ref loc4=1, common slopes,
   common sigma) AND two-group (delta_NonInt on 1[loc4=4]) on working
   observed (draw=0) wages, loc4 in {1,2,3,4}, wage>0, singles+couples,
   pooled 2015-2017 with year controls if available else 2016-only (flag
   thin cells). Write tagged coefficients (years, population) to a pilot
   config consumed by the draw stage.
2. enh_RURO_draws.py (pilot path): replace the Uniform[w_min,w_max] wage
   draw (lines ~1196-1204) with a Normal(Xb + delta_loc4, sigma^2) log-wage
   draw + EXPONENTIATE; replace the proposal-density term (lines ~1225-1234)
   with the matching log-normal density IN LOCKSTEP. Retain occ_spec=fixed.
   Use Halton (preferred) or Sobol via scipy.stats.qmc for the couples
   product if cleanly droppable; else documented PCG64 fallback. Record
   sequence+seed+scramble.
3. _reshape_couples_to_wide(): replace the inner merge on ["idhh","draw"]
   (lines ~1058-1065) with a 30x30 cross-join on idhh over draws 0..29 each;
   emit draw_male, draw_female, draw_joint = 30*draw_male + draw_female;
   chosen row = (draw_male==0 AND draw_female==0); preserve invariants
   (one male + one female per draw_joint; is_chosen_male==is_chosen_female).
4. Re-point downstream draw==0 semantics to draw_joint where needed; GREP
   for hard-coded single-integer "draw" reliance and report every site
   changed.
5. EUROMOD: run on the 2,577 x 900 = 2,319,300 pilot couples alternatives.
   Report counts and wall time.
6. GSURv2 merge: RE-COMPUTE GSUR centring within the new 900-alt choice set
   (do NOT inherit P3a centred values). Confirm in report.
7. MNL rebuild + pilot split stem: couples n_draws=900 in __mnlmeta.json,
   singles n_draws=100 unchanged; re-apply R1 region repair if the all-NaN
   couples region defect reappears; verify one-region-per-household.
8. Precompute checks (spec contract section 22): precompute_data_couples
   completes; region arrays non-zero; draw_joint==0 unique per couple;
   disposable income populated.
9. Build the consistency-check couples blocks at 400 (20x20) and 1600
   (40x40) as well as 900, for the section 23 convergence test.

Then run a PILOT estimation FOR DIAGNOSTICS ONLY (not verdict-grade):
- Report the wage-occupation separate-identification diagnostic
  (information-matrix diagonals on delta_occ* vs beta_occ_*, cross-start
  stability, calibrated-vs-implied drift).
- W1 vs two-group comparison.
- 400/900/1600 simulation-consistency on estimates + decomposition.
- Measured precompute and gradient/Hessian wall time at 900.

Halt conditions: see spec contract section 26 (HP1-HP9). If any fires,
STOP, write the report up to that point, and await amendment. Do not work
around a halt.

Write ONE report: Results/NC_pilot/JMP_NC_pilot_build_report_v1.md, with the
headings and contents required by spec contract section 27. End with the
required final statements (M1-clean active; P3a unaffected; no welfare;
no SA2; no promotion; pilot scope only).
```

Save the build report as: `Results/NC_pilot/JMP_NC_pilot_build_report_v1.md`

---

**Required final statements:**

- **This contract applies only to the 2016 couples-only pilot.** It does not
  authorize a full P3a rebuild, pooled estimation, welfare, or SA2.
- **M1-clean 2016 remains the active JMP baseline.**
- **The corrected pooled P3a track is unaffected** and continues on its
  frozen 100-diagonal, unconditional-wage spec to its post-estimation review.
- **The five audit blockers are resolved:** (1) double-counting → `delta_occ*`
  calibrated, not free, removing the risk by construction; (2) accepted-vs-
  offer → accepted-wage approximation, documented, no selection model
  required for the pilot; (3) joint draw-index → `draw_male`/`draw_female`/
  `draw_joint = 30·draw_male + draw_female`, chosen at `draw_joint == 0`;
  (4) row guards → separate pilot driver / `--pilot` mode, production
  untouched; (5) Mincer set → pooled 2015–2017 working accepted wages with
  year controls if available, else 2016-only with thin-cell flag.
- **No build is executed by this document.** The build is authorized as scope
  and executed only by the §28 prompt, under the §26 halt conditions.

---

*Status: pilot spec contract v1. Authorizes the 2016-couples-only pilot
scope under halt conditions; executes nothing. M1-clean 2016 active. Frozen
pooled P3a spec and post-estimation track unaffected. Next document: the
pilot build report (§27), produced by the §28 build.*
