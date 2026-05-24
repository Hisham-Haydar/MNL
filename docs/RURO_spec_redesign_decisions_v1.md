# RURO Spec Redesign — Decisions v1

**Project:** Unequal Job Opportunities and Well-Being Inequality (JMP)
**Baseline:** France 2016, RURO / latent-jobs labour supply, singles + couples
**Date:** 2026-05-24
**Status:** LOCKED for baseline. Feeds `RURO_model_spec_contract_v3`.
**Evidence base:** `RURO_data_audit_v1.md`, `RURO_data_audit_v1_addendum.md`, `RURO_sample_funnel_v1.md`
**Supersedes:** focal-bin and variable-routing provisions of the v1/v2 spec contract.

> Purpose: convert the pre-drop audit + sample funnel + addendum into a fixed set of
> baseline decisions, so the rebuild is surgical (draws → estimate), not an open refactor.
> Each decision states the call, the evidence, the implementation locus, and any caveat.

---

## D0 — Scope and sample: KEEP the current baseline sample

**Decision.** The baseline uses the existing decider sample unchanged: 1,676 singles, 2,577 couple households. No edits to `enh_france_data_prep.py` or `enh_RURO_prep.py` for the baseline.

**Evidence / rationale.** The funnel shows `les ∈ {3,5,7}` already *includes* the unemployed (5) and voluntary inactive (7); non-employment is genuinely thin (singles 6.5%, couple-men 2.8%, couple-women 3.5%), not an artifact of an over-tight LES set. The thinness is structural — prime-age, non-self-employed, non-retired French adults are ~90%+ employed — and no defensible filter change manufactures a large participation margin.

**Consequence.** Baseline opportunity is identified primarily on the **hours and wage** margins; participation is a small, explicitly caveated channel. This must be stated plainly in the paper.

**Deferred extension (E1, NOT baseline).** Relax Step 3 (which drops entire households holding any disability/retirement benefit) to admit *work-capable* disabled individuals — the restricted-feasible-set population the paper is about. Cost: full rebuild from `data_prep` + a work-capability criterion. Documented robustness only.

---

## D1 — Hours focal structure: FIVE modes (adds 35h and a long-hours mode)

**Decision.** The France focal modes are:

| Mode | Center | Recommended band (h) | Role | Evidence (share of working) |
|---|---|---|---|---|
| PT1 | 20 | {18,19,20,21} | part-time | S 2.6% · M 0.5% · F 2.9% |
| PT2 | 30 | {29,30} | part-time (stronger for women) | S 2.7% · M 1.2% · F 4.9% |
| **F35** | **35** | **{34,35,36}** | **statutory full-time (NEW)** | **S 24.0% · M 22.9% · F 24.4%** |
| FT | 39–40 | {37,38,39,40} (lower edge → 36.5) | common full-time | S 24.4% · M 27.3% · F 20.8% |
| **LH** | **~48** | **{45,…,52}+** | **long hours (NEW, esp. men)** | **M: 45h 8.0% + 50h 8.8% + 60h 5.0%** |

**Evidence / rationale.** The 1-hour histogram shows a sharp 35h spike (the *35-heures* law) carrying ~24% in every group and sitting outside all prior bins; the 37h mass fell just below the old 37.5 threshold; and the men's long-hours cluster (45/50/60) rivals the 35h spike in mass. In a latent-jobs model the focal points are where offered hours cluster, so 35h and a long-hours mode are required, not optional.

**Implementation.** Proposal modes/priors in `enh_RURO_draws.py`; `working_*` band indicators in `_build_mnl_block` / `_build_mnl_block_couples_wide`; focal-bin section of the spec contract.

**Caveat / open item.** The 37h boundary is assigned to FT (lower edge 36.5), not F35 — confirm in the draws script. Exact band tolerances and the continuous-density mixture form are an implementation detail to verify on the rebuilt draws; the **modes are locked**.

---

## D2 — Welfare taxonomy: THREE reported components, ability bracketed

**Decision.** Decompose money-metric well-being inequality into **preferences / ability / opportunity-access**, and report the opportunity share as a **bracket**:
- lower bound = **access only** (ability treated as responsibility/effort),
- upper bound = **access + ability** (ability treated as circumstance).

The normatively relevant figure lives inside the bracket; the reader's responsibility view selects it. This bracket *is* the contribution — it engages the responsibility-cut literature (Roemer/Fleurbaey) instead of asserting one cut.

**Definitions.**
- **ability** = productivity returns to education and experience (the Mincer-X line of the wage-opportunity layer).
- **opportunity-access** = location / local-demand / environment factors the individual does not control (`gsur`, urbanisation, and later external regional demand).

**Structural note.** No new structural layer is needed for the baseline. Ability and access are *already* separable: ability is the Mincer-X piece of the wage/opportunity layer; access is the region/demand piece. The three-way split is achieved at the **welfare/decomposition stage** by attributing the opportunity-layer contribution between these two pieces.

**Access-purity rule (binding).** Education and experience NEVER enter the access bucket — they are ability (productivity) or preference (taste). Education straddles two buckets and both must be tracked: its leisure-taste effect (`β_l_educH`) → preference; its wage-offer effect (`β_w_educH`) → ability. Neither may leak into access.

---

## D3 — Variable routing table (baseline)

| Variable | Bucket | Layer | In baseline? | Note |
|---|---|---|---|---|
| consumption (`ils_dispy` → c) | preference | utility (BC) | ✔ | from EUROMOD per alternative |
| leisure / hours | preference | utility + choice | ✔ | |
| `age_norm`, `age_norm2` | preference | utility (taste) | ✔ | VIF ≤ 1.2, clean |
| `n_children` | preference | utility (taste) | ✔ | |
| `educH` (leisure interaction `β_l`) | preference | utility (taste) | ✔ | taste channel |
| `educL`, `educH` (Mincer `β_w`) | **ability** | wage-opportunity | ✔ | clean (VIF 1.2) |
| `pexp_years`, `pexp_years2` | **ability** | wage-opportunity | ✔ | polynomial VIF mechanical, keep |
| `gsur` (`gsur_male/female`) | **access** | hours/employment opp. | ✔ | keep; see D4 |
| urbanisation `drgur/drgmd/drgru` | **access** | opportunity layer | ✔ NEW | one increment; see D5 |
| `educH` in **hours**-opportunity | — | — | ✖ REMOVE | collinear with `gsur` (r=−0.77); see D4 |
| `drgn2` (NUTS2) | (key only) | — | key | merge key for external data, NOT a regressor |
| `loc`/`loc4` (occupation) | occupation-opp. | opportunity | ✔ | existing |
| `lindi` (industry, 13 cat) | sector-opp. | opportunity | ✖ → M6 | feasible; reserved for sector extension |
| `ddi`, `dcz`, `dms`, `dehde`, `dey`, `dew`, `dmb`, `ddt`, `dcu`, `dncsy` | — | — | ✖ | excluded; reasons in D5 |
| any `l*`/`y*` labour/income outcome | — | — | ✖ NEVER | endogenous to the choice (see D7) |

---

## D4 — gsur (access employment shifter)

**Decisions.** (a) Keep `gsur` / `gsur_male` / `gsur_female` as the access employment shifter. (b) **Drop `educH` from the hours-opportunity layer** at baseline — let `gsur` carry the education-linked opportunity variation. (c) Keep `gsur_male` and `gsur_female` as distinct shifters for couples.

**Evidence.** `gsur`↔`educH` correlate −0.77/−0.74/−0.81 (VIF 2.42) because `gsur` is built on education×age×region cells; the cleaner exclusion variable should carry it. gsur strength conditional on preference shifters: singles −0.601 (t=−2.72, strong), men −0.339 (t=−3.10, strong), **women −0.091 (t=−0.58, weak — accept; structural, not fixable here)**. Within-couple, 84.9% of households have `gsur_male ≠ gsur_female` (mean gap 3.7pp), so the male/female opportunity equations are separately identified.

**Caveat.** gsur is coarse (24–40 cells) and education-loaded; this is the main reason external regional demand (D6) is needed to sharpen and de-confound access.

---

## D5 — Circumstance promotions

**PROMOTE (baseline):** urbanisation `drgur` / `drgmd` / `drgru` (54.1% / 20.6% / 25.3%) into **opportunity-access only**, as one increment — urban labour-market density plausibly shifts the feasible job set, is exogenous, and has clean variation.

**RETAIN AS KEY:** `drgn2` (NUTS2, 22 regions) — join key for external regional data in D6; not used as fixed effects (cells as small as n=6).

**EXCLUDE (baseline), with documented reasons:**
- `ddi` disability — only **4 obs** (sample already removed the disabled via Step 3 + les=8); unidentifiable.
- `dcz` citizenship — **69 non-citizens** total; underpowered.
- `dms` marital, incl. 27% divorced — preference-side household history, not access.
- `dehde` detailed ISCED / `dey` years / `dew` completion-year — ability-side refinements, redundant with `deh`/`pexp`.
- `dmb` birth quarter, `ddt` interview date (constant), `dcu`, `dncsy` (≈constant) — instruments or no variation.

**Guardrail.** Circumstance variables enter **opportunity-access only**, **one at a time**, each with a written reason; never added to both utility and opportunity.

---

## D6 — External regional demand: DEFERRED to first refinement (Phase 5), not baseline

**Decision.** Run the first baseline on internal access (`gsur` + urbanisation). Immediately after the baseline + recovery test, merge external regional labour-demand data to sharpen the access/ability split — treat this as the *first* refinement, not a distant extension.

**Rationale.** Internal access variation is thin (§D4–D5), so the access/ability split is identification-fragile on internal data alone (recall: without exclusion restrictions only the product of preference and opportunity is identified). External region-level demand shifters that move the feasible set without shifting own productivity/tastes are what make the split credible.

**Admissibility bar.** Region (×time×sector) level; plausibly shifts the feasible job set; plausibly excludable from own productivity and preferences. **Prefer direct demand measures** (regional/sectoral vacancy rate, job-finding rate, sector employment share, regional employment growth; Eurostat regional LFS, DARES/INSEE). **Energy consumption is a secondary robustness proxy at most** (confounded with sector mix/climate/housing; weak excludability). Merge key: `drgn2`/`drgn1`.

---

## D7 — Permanent inadmissibility (the endogeneity wall)

No EUROMOD/SILC **labour or income outcome** ever enters preferences or opportunity — they are functions of the choice being modelled and would let the model explain the choice with the choice, contaminating both buckets and invalidating the decomposition. This applies regardless of perfect coverage. Explicitly: `les`, `lfs`, `liwwh`, `liwmy`, `liwftmy`, `liwptmy`, `lhw`, `lse`, `lowas`, `lcs`, `lpemy`, `yem00`, `yse`, `yemxp`, `yivwg`, etc. Sampling/bookkeeping IDs (`dsu01/02`, raw weights) are likewise out.

---

## D8 — Rebuild scope and order

Sample unchanged ⇒ `enh_france_data_prep.py` and `enh_RURO_prep.py` are **frozen** for the baseline. The focal-mode change forces a rebuild **from draws onward** (new proposal → new draws → EUROMOD re-run → MNL build).

1. **Lock** — this memo → `RURO_model_spec_contract_v3`. *(this chat)*
2. **Implement** — edit `enh_RURO_draws.py` (5 modes/proposal), `_build_mnl_block(*)` (bands), whitelist (+urbanisation; `drgn2` as key), `enh_RURO_estimate_FR.py` (urbanisation in access layer; `educH` out of hours-opp). Rebuild draws → EUROMOD → MNL; re-run explorer to confirm the 35h and LH modes are captured. *(Claude Code)*
3. **Estimate → recovery test** — the identification gate. **Report nothing before it passes.** *(Claude Code)*
4. **Welfare + bracketed decomposition** — opportunity share as [access-only, access+ability]. *(this chat + Claude Code)*
5. **External regional demand merge** — first refinement (D6). *(later)*
6. **M6 sector** via `lindi` (feasible) — extension. *(later)*

---

## D9 — pi0 / empty-feasible-set requirement

The opportunity layer must be able to represent a *tiny or empty* feasible set (the `pi0` / market-opportunity mass). Otherwise a forced h=0 is misattributed to a taste for leisure, wrongly shifting opportunity inequality into the preference bucket — directly corrupting the headline decomposition. Confirm during implementation.

---

## D10 — Standing guardrails (do-not list)

- No endogenous `l*`/`y*` variables in any layer (D7).
- No circumstance variable in both utility and opportunity; one increment at a time, each with a written reason.
- Education and experience never in access (D2).
- Ability never silently folded into opportunity — always reported as a bracket (D2).
- Variable role is a theory/economic decision implemented via the whitelist + spec contract; data decides feasibility, choice-space shape, and within-role redundancy only.
- No reported decomposition before the recovery test passes (D8.3).

---

## Open items to confirm during implementation

1. 37h boundary → FT (lower edge 36.5); LH band tolerance; continuous-density mixture form (draws script).
2. `pi0` empty-set representation (D9).
3. Recovery-test design — separate memo (`RURO_recovery_test_design_v1.md`).
