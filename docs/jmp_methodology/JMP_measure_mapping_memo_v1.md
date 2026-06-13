# JMP Measure-Mapping & Pre-Registration Memo v1 (F2)

Date: 2026-06-12 · Status: pre-registration — locks the empirical implementation contracts for the
well-being measure family BEFORE any inversion code is written or any Ω computed. Companion to
`JMP_results_campaign_roadmap_v1.md` (D1–D5) and informed by
`04_welfare_migration_inventory_and_matrix_v1.md` (F1) and `updated_draft.tex` (theory paper).
Boundary: the theory paper supplies the axiomatic characterizations; this memo supplies the
ex-ante structural implementations. The two papers remain distinct.

---

## 1. Scope and conventions (locked)

- **Population:** singles (2,243 m + 2,764 f = 5,007 HH). Couples = stretch goal (IS-only,
  reported separately, beta_l0_m corner caveat); never pooled with singles.
- **Unit:** household. One Ω per household, never split, not equivalized.
- **Units of Ω:** 2016-real € (the `ils_dispy_real` consumption scale). W¹/W⁴/W⁶ return a
  consumption *level* w*; W³ returns a *shift* (≈0 by construction).
- **θ and spec:** certified `joint_pooled_v1_bll0_tlmpin`, `theta_hat_realdata_901_v1.csv`. Never moves.
- **Baseline stem for reportable welfare numbers (supervisor decision, recommended default):**
  staged reproducible reference `fr_p3a_bpool_engine_ready_staged_threeB1` at certified θ̂ — the
  role it was assigned (`welfare_pricing_reference_candidate_only`), where Four-B/C pricing gates
  were proven. F3 additionally records certified-stem V_i^IS per HH as a delta exhibit. Sign-off
  required; default applies if unamended.
- **Actual-side integrator:** V_i^IS over existing draws (PRIMARY). V_i^dir at single-pass S≈100
  is the calibrated cross-check (Four-C2 design), never the headline integrator.
- **Measure set (locked per roadmap D4):** headline W¹, W⁴, W⁶; validation W³; deferred W², W⁵.
- **Key structural fact the contracts exploit:** utility is u(c, ℓ) — occupation and wage enter
  preferences ONLY through consumption; occupation is opportunity-layer only. Therefore any
  reference object with consumption set directly needs no wage draw, no occupation assignment,
  and **no EUROMOD pricing** on the reference side. This confirms the roadmap §2 hypothesis for
  the entire priority set: **the conference path requires no new EUROMOD pricing beyond the
  V_i^dir cross-check already designed.**

## 2. The ex-ante mapping rule (one rule, applied to every measure)

The theory measures compare a realized bundle z to max_R over a modified set B. The ex-ante
structural analogue replaces both sides with inclusive values under the estimated model:

> **Solve for w:  V_i^actual = V_i^ref(B(w))**, where V_i^actual is the household's inclusive
> value over its own latent opportunity set (V_i^IS), and V_i^ref is the inclusive value over the
> reference object B(w) defined per measure below.

Discipline anchor: the implemented-and-validated W³ machinery already obeys this rule — at the
own set with zero shift, V_ref ≡ V_actual, hence Ω ≡ 0 (zero-recovery φ₀ = 0.0 confirmed in the
Stage-1 production gate). Every new measure reuses the same solver pattern (monotone in w,
bracketed, per-household convergence check) with a different B(w).

## 3. Per-measure implementation contracts

**W³ — Laissez-Faire (VALIDATION ONLY).**
B(w) = own latent set, consumption shifted: c_j + w at every node. Same draws, same
(log ĝ − log π) weights as V_actual. Gate: Ω ≈ 0 at machine level for ~all households **on the
conference stem** — this re-validates the ported/extended solver before any real measure runs.
Never reported as a welfare result.

**W⁴ — Staying-Home Equivalent (HEADLINE; build first among the real measures).**
B(w) = the single home node o at consumption w: V_ref(w) = u(w, ℓ_home) — a one-element logsum,
no shocks, no weights. Solve u(w, ℓ_home) = V_i^actual.
Contract gate: W⁴ admits an **analytic inversion** of the consumption term given the Box-Cox form;
F4 implements the numerical solve AND the analytic cross-check; agreement ≤ 1e-8 per household.
Interpretation: full-compensation endpoint — the consumption level at home equivalent to the whole
opportunity situation; opportunity AND wage differences are priced into w.

**W¹ — Equal-Pay over the OWN set (HEADLINE).**
B(w) = own latent set with consumption REPLACED by w at every node (employment and home alike;
default per theory: o ∈ A and all jobs in B pay w). Same draws, same (log ĝ − log π) weights —
the own set's *composition* (hours availability, market access, occupation mix via ĝ) still
matters; pay does not. V_ref(w) = log Σ_j exp(u(w, ℓ_j) + log ĝ_j − log π_j). Solve = V_actual.
Interpretation: Independence-of-y — wellbeing depends on what jobs you can get and your
preferences, never on what they pay. The W¹-vs-W⁴ contrast isolates the wage channel.
Pre-registered sensitivity (computed, reported in appendix only): replacement at working nodes
only, home keeps actual non-employment consumption.

**W⁶ — Min-of-Equal-Pay over the UNIVERSAL set (HEADLINE).**
B(w) = the common universal grid 𝒥 at equal pay w, identical for every household:
V_ref(w) = log Σ_{j∈𝒥} exp(u(w, ℓ_j)), uniform weights (the set is handed deterministically; no
ĝ, no π). Solve = V_actual.
**Universal grid rule (locked):** because occupation never enters u, the payoff-relevant
dimension of 𝒥 is hours/leisure only. 𝒥 = {home node} ∪ {one node per canonical hours band of
the estimation spec}, all at consumption w. F4 reads the exact band values from the certified
spec and RECORDS them in its report before any Ω is computed; the rule (not the values) is what
is pre-registered here. Same 𝒥 for every single; couples analogue (product grid) deferred to the
couples stretch.
Interpretation: full-compensation against a common benchmark — differences in own opportunity
sets AND pay are both priced; only preferences over (c, ℓ) separate households.

**W² and W⁵ — DEFERRED (not built pre-conference).** W² requires pay-based shifts (pre-tax y(j)
mapping — the one genuinely EUROMOD-exposed reference); W⁵ requires the reference-set-Ā subsidy
convention. Both are post-conference robustness; slots stay `null` in config.

## 4. Contract decisions table (defaults locked now; each is one sentence in the paper's appendix)

| # | Decision | Locked default | Sensitivity (appendix only) |
|---|---|---|---|
| 1 | W¹ home-node treatment | home included in B, consumption = w | working-nodes-only replacement |
| 2 | Bracketing bounds | w ∈ [DCM_MIN_POSITIVE = 1.0, 50 × max observed c_j], expand-and-retry once, else flag HH | — |
| 3 | Solver | reuse/extend `welfare_core.w3_inversion` pattern: monotone check, bracket, converge per HH; add transform mode `replace(w)` alongside `shift(w)` | — |
| 4 | Non-convergent households | flagged, excluded from Gini, COUNT REPORTED (gate: < 0.5% per group, else stop) | — |
| 5 | Inequality index | Gini per measure + across-measure spread (the headline); Atkinson(1) as appendix companion | — |
| 6 | W³ role | validation gate only; Gini(W³)=0 by construction never appears in results | — |
| 7 | Consumption floor | inherited from engine-ready assembly (clip ≥ 1.0); no re-flooring in welfare layer | — |
| 8 | Missing-loc4 chosen workers (128) | irrelevant to measures (occupation ∉ u); relevant only to S2 post-conference | — |

## 5. What F4 must deliver (gates, in build order)

1. **Solver extension** (`replace` mode + single-node reference) — unit tests on synthetic
   utilities (known closed-form solutions).
2. **W³ re-validation on the conference stem**: Ω ≈ 0 machine-level, all singles. STOP if not.
3. **W⁴**: numerical vs analytic agreement ≤ 1e-8; Ω distribution sanity (all ≥ floor; monotone
   in V_actual within preference type).
4. **W¹**: zero-recovery special case test — if all c_j in the own set are artificially set equal
   to a constant κ, then w* = κ exactly (the solver must recover it).
5. **W⁶**: grid recorded from spec; same-κ special case test on 𝒥; cross-household invariance
   check (two households with identical preferences and identical V_actual must get identical w*).
6. **Outputs**: per-HH Ω parquet per measure (UID, group, Ω, convergence flag, bracket info),
   provenance block (θ-hash, spec-hash, stem, c_scale, solver version) — feeding F5 directly.

## 6. Sign-off checklist (reply in chat)

- [ ] Stem decision: staged reference at certified θ̂ for reportable welfare numbers (default) — confirm/override
- [ ] Measure set W¹/W⁴/W⁶ + W³-validation, W²/W⁵ deferred — confirm
- [ ] Contract decisions 1–8 — confirm/amend
- [ ] Universal-grid rule for W⁶ — confirm
- [ ] Couples stretch = IS-only per-HH capture in F3, measures only if Day-9 checkpoint is green — confirm

*Save as: `JMP_measure_mapping_memo_v1.md` (project). Successor of roadmap §2; supersedes nothing.*

---

## Addendum (2026-06-13) — primary evaluation scope + inference contract

Recorded in `RURO_welfare_F5_primary_scope_ratification_v1.md`. The §1 population (2,243 m + 2,764 f
= 5,007 singles) describes the **pooled 2015–2017 household-year output set**. Following the operator
ratification of the F5 primary cross-section (and decisions-memo §13 option (b)):

- **Primary welfare evaluation scope = the 2016 singles cross-section** (`year_tag == 2`, n = 1,676
  households), at the pooled `theta_hat`. The pooled 5,007 set and the separate 2015/2017 years are
  **sensitivities**.
- The W1/W4/W6 measure contracts (§3) and the ratified normalization (F4-C) are unchanged; only the
  reported headline **scope** is fixed to 2016.
- **Inference (pre-registered):** cluster bootstrap over the **full joint estimation sample, 9,657
  `idorighh`**, re-estimating `theta` per replicate (B = 200), then recomputing measures on the 2016
  singles scope. The 3,902 singles welfare-output `idorighh` are descriptive, not the resampling
  unit; fixed-`theta` resampling is insufficient.
