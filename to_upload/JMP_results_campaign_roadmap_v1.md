# JMP Results Campaign Roadmap v1
**From certified estimates to a conference-presentable answer to the main question**
Date: 2026-06-12 · Status: planning memo, supersedes nothing, pre-registers the conference framing
Boundary reminder: `updated_draft.tex` is the **Maniquet–Haydar theory paper**, not the JMP. The JMP *uses* the characterized measures empirically and cites the theory paper for the characterizations. Nothing axiomatic migrates into the JMP beyond citation.

---

## 0. What counts as a "result" (pre-registered now, before any number exists)

**The main question:** *How much of observed inequality in money-metric well-being is attributable to unequal job opportunities rather than heterogeneous preferences, once labour supply is modeled as choice among latent jobs?*

**Headline sentence template (what the conference slide must be able to say):**

> "Among single-adult households in France (2015–2017), unequal job opportunities account for **X–Y%** of money-metric well-being inequality across an axiomatically characterized family of well-being measures (W¹, W⁴, W⁶), versus **Z%** attributable to preference heterogeneity, with ability bracketed between them. A standard labour-supply model that does not model opportunities would misattribute **Δ** of this to preferences."

X–Y is the across-measure bracket (normative sensitivity), Z the preference share, Δ the no-opportunities-counterfactual gap (sub-question 1). Every number versioned, cluster-robust CI'd, on the spec-locked baseline.

**Minimum Presentable Product (MPP) ladder — the fallback hierarchy if time runs out:**

- **MPP-2 (target):** singles decomposition across W¹/W⁴/W⁶ (+W³ validation) + no-opportunities counterfactual + couples staged.
- **MPP-1:** singles Gini + across-measure spread (the welfare distributions exist, decomposition partial) + decomposition design + descriptives.
- **MPP-0 (floor):** certified estimates + Five-A opportunity descriptives + measure family + decomposition design, no welfare numbers. Honest but weak; everything above this floor is gained ground.

---

## 1. Strategic decisions (the decisive calls, locked now)

**D1 — Conference spec = the certified baseline (`joint_pooled_v1_bll0_tlmpin`), locked today.** The LOC4 four-density question and the regional-covariate question continue as Path A, but they feed the **paper**, not the talk. Rationale: the welfare machinery in MNL is built and calibrated *for this estimate* (Four-A→C2); re-basing the conference on a spec that doesn't exist yet is the one move guaranteed to miss the deadline. The LOC4 memo verdict shapes the talk's **caveat narrative** either way: verdict (b)/(c) (thin cells / defensible restriction) means the common-σ restriction is *data-justified* — a strong position; verdict (a) means the slide says "occupation-specific dispersion spec in progress, direction of bias discussed." Pre-registering this now prevents outcome-driven spec selection later.

**D2 — Singles carry the conference headline; couples are staged.** Three independent reasons: (i) the `beta_l0_m` lower-bound corner compresses the couples preference component for non-structural reasons — couples must be reported separately anyway; (ii) couples V_i is plausibly design-only (net-new build, F1 confirms); (iii) the question is perfectly well-posed within the singles population. The talk shows couples as "in progress, corner caveat stated."

**D3 — Conference numbers come from the MNL machinery; the dcl Wave-4 migration runs in parallel and the MNL production outputs mint its oracles.** This inverts the dependency: instead of the conference waiting on the migration (FR adapter is a placeholder in `dclaborsupply_app`), the migration gets exactly what it lacked — never-move welfare anchors — from the fast lane. The paper's final numbers are eventually reproduced in dcl; the talk's numbers are versioned, provenance'd MNL outputs.

**D4 — Measure set pre-registered: headline W¹, W⁴, W⁶; validation W³; optional robustness W², W⁵.** Per your stated priority and the theory draft's characterizations. Locked before any Ω distribution exists, so measure selection cannot be outcome-driven. The across-measure spread over {W¹, W⁴, W⁶} *is* the normative-sensitivity headline (sub-question 4).

**D5 — Regional continuous covariates deferred to post-conference robustness.** The flat-by-region finding becomes a *motivation/limitations* slide ("region dummies + gsur only; richer local labour-market conditions in progress"), not a blocker. It requires external data work and new identification arguments — the wrong fight on this clock.

---

## 2. The measure family: theory → empirical mapping (to be locked in F2)

From `updated_draft.tex` (theory numbering — coincides with the MNL scaffold where they overlap; F2 verifies no residual conflict):

| W | Name (theory) | Characterization | Reference object (ex-ante empirical analogue) | Reference-side pricing | Priority |
|---|---|---|---|---|---|
| W¹ | Equal-Pay | Independence of **y** + Responsibility For Equal Pay | **Own** opportunity set, all jobs at common consumption *w*; solve indifference for *w* | **None** — consumption set directly | **Headline** |
| W² | Best-paid-equivalent | Full Responsibility + Comp. for horizontal ref. preference R^h | Own set under uniform shift −t; report max pay −t | Pay-based shift (the expensive one) | Optional |
| W³ | Laissez-Faire | Full Responsibility + Indep. of Irrelevant Jobs | Own set + uniform consumption shift *w*; degenerate Ω≈0 ex-ante | None (shift on disposable income) | **Validation** |
| W⁴ | Staying-Home Equivalent | Full Compensation + Indep. of Prefs over Infeasible Jobs | Single home node *o* at consumption *w* | **None** — one node, consumption direct | **Headline** |
| W⁵ | Reference-Ability LF | Indep. of A + IIJ + responsibility rel. to Ā | Common reference set Ā (special case Ā=𝒥) + uniform subsidy *w* | Depends on subsidy convention | Optional |
| W⁶ | Min-of-Equal-Pay | Full Compensation + Weak Responsibility | **Universal** set 𝒥, all jobs at common consumption *w* | **None** — consumption direct, but 𝒥 needs an operational grid definition | **Headline** |

**The observation that compresses the timeline (F2 must confirm it):** every measure in the priority set {W¹, W³, W⁴, W⁶} has a **consumption-direct reference side** — the inversion sets or shifts disposable consumption directly and never reprices counterfactual wages through EUROMOD. If the frozen welfare-spec conventions confirm this (money-metric shifts are post-tax, per the existing W³ design), then the conference path needs **no new EUROMOD pricing at all**: the actual side uses V_i^IS over existing priced draws (primary integrator), V_i^dir at S≈100 remains the calibrated cross-check, and the reference side is utility-only inversion over known leisure nodes. The expensive Ā/J/o EUROMOD exposure flagged in the W³ gate report attaches to W²/W⁵ — exactly the deprioritized measures.

**Two things F2 must pin:** (i) the **ex-ante mapping** — the theory measures compare a realized bundle z to a max over a modified set; the JMP object is ex-ante, so each implementation replaces both sides with inclusive values (V_i^actual = V_i^ref(w), solve for w) per the scaffold's existing convention; (ii) the **operational 𝒥 for W⁶** — the universal job grid (hours × occupation nodes; wage irrelevant since consumption is set directly) must be defined once, pre-registered.

---

## 3. Lane F — Conference fast lane (MNL, certified baseline, singles)

One change → one gate throughout. Versioned outputs; no canonical promotion without a separate memo.

**F1. Welfare inventory + migration matrix** *(prompt already drafted last turn — run now, in parallel with S1)*
Tool: Claude Code · Opus · high · thinking ON. Dual purpose with one addendum appended to the drafted prompt:
> *ADDENDUM — FAST-LANE STATUS READOUT: In addition to the migration plan, state explicitly what exists and runs TODAY in MNL beyond V_i: is there any implemented reference-set construction, equivalent-income inversion solver (Gate-2 machinery), or measure-family scaffolding, or is everything past V_i design-only? For each: file path, runnable yes/no, what it would take to run. This readout serves a parallel fast lane that will compute the first welfare numbers in MNL while the migration proceeds.*
Output: `docs/migration/04_welfare_migration_inventory_and_matrix_v1.md`. Gate: the 7-point completeness check from the drafted prompt + the status readout.

**F2. Measure-mapping + pre-registration memo** *(Claude project chat — I draft it next turn from the tex + scaffold contract + F1's status readout)*
Locks: the table in §2 with full ex-ante implementation contracts per measure; the consumption-direct confirmation; the 𝒥 grid for W⁶; the reporting format (Gini + across-measure spread + bracket). Save as `JMP_measure_mapping_memo_v1.md`. This is the prose-design-memo-before-code gate for F4.

**F3. Full singles V_i production run** *(Claude Code · Sonnet — it's a calibrated lift, not architecture)*
All 5,007 singles (2,243 m + 2,764 f): V_i^IS over existing draws (primary) + V_i^dir cross-check at single-pass S≈100 per the Four-C2 approved design, under the carried-forward Four-B constraints (full-chunk population batch, no sub-bands, authoritative yem identity, no double deflation). Gate: ESS/stability diagnostics + IS-vs-dir like-for-like on the utility-only gate object ≤0.5 nats; per-group readout. Output: per-HH V_i parquet + `RURO_welfare_singles_Vi_production_report_v1.md`. **No Ω, no Gini yet.**

**F4. Reference sets + inversion** *(Claude Code · Opus high for the solver design if F1 says design-only; Sonnet if porting)*
Build order: **W³ first** (own-set shift; gate = Ω≈0 at machine level for ~all singles — the inversion's falsifiable sanity test, contract Gates 2/3/4), then **W⁴** (single home node — cheapest real measure), then **W¹** (own-set equal-pay), then **W⁶** (universal-grid equal-pay). Each its own bounded increment with monotonicity/bracketing checks per household.

**F5. Singles measure-family run → first reportable number**
{Ω_i} per measure → singles Gini per measure + the across-measure spread. **This is the first inequality number in the project's history**; versioned output + `RURO_welfare_singles_measure_family_report_v1.md`. Pre-registered read: the spread over {W¹, W⁴, W⁶} is the normative-sensitivity result; W³ stays a validation artifact, never a headline.

**F6. Decomposition design memo → Shapley-Shorrocks run** *(memo in project chat first — mandatory)*
The memo pre-registers the **equalization scheme**: operationally, what "equalize opportunities / ability / preferences" means (which parameter blocks or characteristics are set to reference values: access block = beta_E, beta_h_*, beta_E_gsur/drg*/y*, beta_occ_* → opportunity; wage block = beta_w_*, σ → ability; leisure/age block → preference, per the established responsibility cut), the 3! orderings, order-independence verification, the bracketed opportunity share (access-only lower / access+ability upper), and cluster-robust CIs. Save `JMP_decomposition_design_memo_v1.md`. Then implement + run on singles. **This produces X–Y and Z.**

**F7. No-opportunities counterfactual** *(dcl package — its first production research use)*
Estimate the RUM special case (v = u, opportunity terms absent) on FR singles via the package-native loader; synthetic recovery not required for a *comparison* spec but fit + identification diagnostics reported. Compare: preference-parameter dispersion vs RURO, and the decomposition under the RUM (opportunity share ≡ 0 by construction). **This produces Δ — the answer to sub-question 1** and the talk's sharpest slide ("what you'd misattribute to preferences").

**F8. Conference freeze**
Results memo (`JMP_conference_results_freeze_v1.md`: every number, spec, gate, caveat) + slides skeleton. Caveat list locked: common-σ wage restriction (with the S1 verdict), region dummies + gsur only, couples staged with corner caveat, singles population scope.

---

## 4. Lane S — Specification lane (Path A continues; feeds the paper)

**S1. LOC4 four-density decision memo** *(prompt drafted two turns ago — run now, parallel with F1)*. Claude Code · Opus high. Output `docs/jmp_methodology/RURO_loc4_four_density_decision_memo_v1.md`. Pre-registered: verdict (b) thin-cells is an acceptable, informative outcome — not to be overridden.

**S2. If verdict (a): four-density estimation in dcl** — not MNL. Precondition: the occupation-specific wage path in the JAX engine is currently fail-closed/unproven (`vw_occupation`); validating it (possibly a small core change = finding + gate + **FR oracle 238504.6360973987 must hold to ≤1e-4**) is the first sub-increment. Then estimate with the **mandatory synthetic recovery gate** (the gender-split lesson: LR preference ≠ recoverability). Recovery failure or thin cells = recorded verdict, baseline stands.

**S3. Spec-impact memo (if S2 estimates):** does the ability/opportunity-relevant block move materially? Feeds the paper's robustness section; enters the talk only as one slide if timing allows.

**S4. Regional continuous covariates:** deferred post-conference (D5). The Five-A flat-by-region readout becomes the motivation exhibit.

---

## 5. Lane E — Engineering lane (dcl Wave 4, parallel, non-blocking)

Proceeds per F1's matrix: 4.1 pure/general math port → 4.2 FR app-pricing wire (population batch) → 4.3 reproduce the single-HH V_i^IS oracle (**minted from F3's outputs**) ≤1e-4 → 4.4 singles V_i^dir reproduction → 4.5 couples V_i (likely BUILD; this is where the couples leg lives) → 4.6 measure family → 4.7 decomposition. The paper's final tables are eventually re-derived here; nothing in Lane F waits on Lane E.

---

## 6. Ordering, parallelism, decision points

**Run now, in parallel:** F1 (with addendum) and S1 — both read-only, independent, Opus-high sessions.
**Then:** F2 (me, next turn, needs F1's status readout) → F3 → F4 → F5 → F6 → F7 → F8, serialized within Lane F; S2 and Lane E proceed alongside without blocking.
**Rough sizing (focused Claude Code sessions):** F1+S1 = 2 · F3 = 1–2 · F4 = 2–3 (more if inversion is design-only) · F5 = 1 · F6 = memo + 1–2 · F7 = 1–2 · F8 = 1–2. **Total ≈ 9–13 sessions ≈ 3–5 weeks at steady cadence.** Honest unknowns: F4's port-vs-build status (F1 resolves) and EUROMOD throughput if F2 *disconfirms* the consumption-direct hypothesis (then reference pricing re-enters and F4–F5 grow).

**Decision points needing you:**
1. **Conference date** → pins the calendar and the MPP go/no-go dates (e.g., "if F5 not green by T−3 weeks, freeze at MPP-1").
2. Sign-off on **D1–D5** (this memo *is* the pre-registration; say so explicitly or amend).
3. **F2 sign-off** (measure implementations + 𝒥 grid) before F4 codes anything.
4. **F6 memo sign-off** (equalization scheme) before the decomposition runs.

---

## 7. Explicitly deferred / avoid

Germany or any second-country welfare; country/year ranking framing; regional-covariate re-estimation pre-conference; W²/W⁵ unless free; couples headline numbers pre-corner-resolution; any canonical/production promotion without its own memo; importing axiomatic content into the JMP beyond citing the characterizations; broad new literature work (the DR03-gated four sources still need manual verification before citation — schedule inside F8, not before).

## 8. Risk register

| Risk | Exposure | Mitigation (pre-registered) |
|---|---|---|
| Couples V_i is net-new | Conference scope | D2: singles headline; couples = staged slide |
| Inversion machinery design-only in MNL | F4 grows | F1 addendum surfaces it now; Opus-high build with W³ degeneracy as the gate |
| Consumption-direct hypothesis fails in F2 | F4–F5 grow (EUROMOD reference pricing) | Four-B population-batch path already proven; S≈100 design caps cost; MPP-1 fallback |
| Four-density identified AND materially different | Talk caveat strength | D1 narrative: "in progress, direction of bias discussed"; paper carries it |
| W⁶ universal-grid definition contested | F4 | Pre-registered in F2 before code |
| Timeline slips | Conference | MPP ladder; freeze at highest green rung |

---
*Save as: roadmap memo → project workspace as `JMP_results_campaign_roadmap_v1.md`. Supersedes the open fork from two sessions ago (Path A vs V_i^dir-first) by running both as parallel lanes with the conference lane primary.*

---

## Addendum (2026-06-13) — primary evaluation scope reconciliation + inference contract

Recorded in `RURO_welfare_F5_primary_scope_ratification_v1.md`. This roadmap "supersedes nothing"
(status line above); the France **2015–2017** framing is the **narrative/empirical-setting** frame
and does **not** amend decisions-memo §13. Reconciled with that §13 and the operator ratification:

- **Primary welfare evaluation scope = the 2016 singles cross-section** (`year_tag == 2`, n = 1,676),
  at the pooled `theta_hat` (decisions-memo §13 option (b)). The 2015–2017 narrative population is
  served by **reporting the pooled and per-year distributions as sensitivities**; the headline
  numbers are 2016. Primary Ginis W1 = 0.173, W4 = 0.329, W6 = 0.337; bracket [0.173, 0.337], the
  X–Y across-measure sensitivity is computed on this 2016 scope.
- **Cluster-robust CIs (the "cluster-robust CI'd" requirement above):** cluster bootstrap over the
  **full certified joint estimation sample, 9,657 `idorighh`**, **re-estimating `theta` per
  replicate** (B = 200), then recomputing F4C measures on the 2016 singles scope. Fixed-`theta`
  household resampling is **not** the pre-registered inference. Point estimates exist (F5); CIs are
  pending this re-estimation bootstrap.
