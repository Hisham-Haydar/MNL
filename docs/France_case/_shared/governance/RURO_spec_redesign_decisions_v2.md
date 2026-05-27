# RURO Spec Redesign — Decisions v2

**Project:** Unequal Job Opportunities and Well-Being Inequality (JMP)
**Date:** 2026-05-24
**Status:** LOCKED (economic decisions). Reconciles v1 with the NC pilot + GSURv2/P3a build state. Feeds `RURO_model_spec_contract_v3`.
**Evidence base:** v1 evidence (`RURO_data_audit_v1.md`, `_addendum.md`, `RURO_sample_funnel_v1.md`) + `RURO_pilot_gsurv2_verification_v1.md` + `JMP_NC_pilot_diagnostic_estimation_verdict_v1.md`.
**Supersedes:** `RURO_spec_redesign_decisions_v1.md` (scope/sequencing and D3/D4 status only; economic decisions unchanged).

> What changed from v1: the economic decisions (focal modes, three-bucket taxonomy, endogeneity wall, pi0) all stand. What is rewritten is **scope/sequencing** (v1 assumed a fresh single-year diagonal rebuild; reality is two live tracks, one of which — the NC pilot — already estimates a 900-alt product/W1 spec) and the **status** of several D3/D4/D5 items now verified on disk.

---

## D-SCOPE — Two live tracks (NEW; read first)

v1 implicitly assumed one track. There are two, and the memo governs both:

| Track | What it is | State | Role |
|---|---|---|---|
| **M1-clean 2016** | single-year, diagonal choice set, single Mincer | active baseline | reference / sanity |
| **NC pilot** | couples-only 2016, product 30×30=900 alts, W1 occupation-conditional wages, loc4-complete | **feasibility PASS** (LL=−16,527.14, two starts, `beta_occ` identified); not promoted, no SEs, no welfare | the frontier spec |
| **P3a pooled** | 2015–2017 stacked, distinct stacked UIDs, `idorighh`-clustered | **GSURv2 merge EXECUTED** (`provisioning_label = gsurv2_opportunity_year_aligned`); estimation not authorized | the target sample |

**Implication for v1's D8.** "Rebuild from draws onward, single-year" no longer describes the work. The draws overhaul (focal modes) and the spec graduation (occupation, urbanisation) now ride on the **NC pilot → P3a** path, sequenced by the B0→B3 ladder (D8-NEW). Estimator/runtime is a separate, parked issue (NC pilot verdict §17; not this memo).

---

## D0 — Scope and sample: KEEP the current baseline sample
*(unchanged from v1)* Existing decider sample: 1,676 singles, 2,577 couples. Non-employment thin (6.5% / 2.8% / 3.5%) and structural, not an LES artifact (`les∈{3,5,7}` already includes unemployed+inactive). Baseline opportunity identified on **hours/wage** margins; participation a caveated channel. **E1 (deferred):** relax Step 3 to admit work-capable disabled — robustness only.

---

## D1 — Hours focal structure: FIVE modes
*(unchanged from v1)* PT1≈20 {18–21}, PT2≈30 {29,30}, **F35≈35 {34,35,36}**, FT≈39–40 {37,38,39,40} (lower edge 36.5), **LH≈48 {45–52}+** (esp. men). 35h spike ~24% all groups; men's long-hours cluster rivals it. Modes locked; band tolerances + 37h→FT + mixture form confirmed in `enh_RURO_draws.py`. **Status: not yet in the pilot draws** (pilot used prior bands) → part of the B-ladder draws rebuild.

---

## D2 — Welfare taxonomy: THREE components, ability bracketed
*(unchanged from v1)* preferences / ability / opportunity-access. Opportunity share reported as a **bracket** [access-only, access+ability]. **ability** = Mincer-X returns (educ, exp). **access** = location/local-demand (`gsur`, region, urbanisation, later external). Achieved at the welfare stage, no new structural layer. **Access-purity rule binding:** education/experience never in access; `educH` leisure-taste→preference, `educH` wage-offer→ability.

---

## D3 — Variable routing table (updated status)

| Variable | Bucket | Layer | Status on disk | Note |
|---|---|---|---|---|
| consumption (`ils_dispy`→c) | preference | utility (BC) | ✔ in pilot | EUROMOD per-alt; pilot prices all 900 cells |
| leisure / hours | preference | utility + choice | ✔ in pilot | |
| `age_norm`, `age_norm2` | preference | utility (taste) | ✔ | clean |
| `n_children` | preference | utility (taste) | ✔ (`beta_l_nkids_f`) | |
| `educH` (leisure `β_l`) | preference | utility (taste) | spec-dependent | taste channel |
| `educL`, `educH` (Mincer `β_w`) | **ability** | wage | ✔ in pilot (`beta_w_educL/H`) | single Mincer eqn (see wage row) |
| `pexp_years`, `pexp_years2` | **ability** | wage | ✔ in pilot (`beta_w_pexp/pexp2`) | |
| **wage structure** | ability | wage | **W1: single Mincer + `delta_occ2/3/4` fixed at draw time, single `sigma`** | **NOT** 4 free LOC4 wage eqns (that = B3, future) |
| `gsur` | **access** | market/employment opp. | ✔ in pilot (`beta_E_gsur`) | GSURv2 on P3a; single-year GSURv2 unverified (D4) |
| region dummies `reg2..reg8` | **access** | market opp. | ✔ in pilot (`beta_E_drgn2..8`) | NUTS-1 region effects, already in spec |
| urbanisation `drgur/drgmd/drgru` | **access** | (target) | **IN-DATA-NOT-IN-SPEC** → pending | D5: the live "one increment" |
| `educH` in hours/market-opp | — | — | **CONFIRMED OUT** | done; educH only in wage layer |
| `beta_occ_2/3/4` (cm, cf) | access | occupation-opp. mass | ✔ in pilot | offer-availability mass, NOT wage params |
| `drgn2` (NUTS2) | (key only) | — | key | external-data join key, not a regressor |
| `lindi` (industry) | sector-opp. | — | ✖ → M6 | feasible; reserved |
| `ddi,dcz,dms,dehde,dey,dew,dmb,ddt,dcu,dncsy` | — | — | ✖ | excluded (D5 reasons) |
| any `l*`/`y*` outcome | — | — | ✖ NEVER | endogenous (D7) |

---

## D4 — gsur / access employment shifter (updated)

**(a)** Keep `gsur` (+ `gsur_male/female`). **(b) educH out of hours/market-opp — DONE** (verified: `educH` appears only in `wage_opportunity`; hours/market blocks carry no education term). **(c)** Region dummies `reg2..reg8` already in the market-opp block — the "region into access" intent of v1 D4/D5 is **partially implemented** (NUTS-1 dummies present; urbanisation still pending).

**GSURv2 status (verified):** EXECUTED on the **P3a pooled** file (`gsurv2_opportunity_year_aligned`, SHA-256-pinned year-tagged inputs). The untagged single-year `fr_2016_RURO_mnl_GSURv2__*` files carry a **v1** GSUR source in their sidecar → **single-year GSURv2 provenance UNCONFIRMED.** Consequence: on the pooled track GSURv2 is live; if a single-year 2016 GSURv2 baseline is wanted, the single-year merge is an **open task**, not done.

**Evidence (legacy gsur, carried forward):** women's gsur weak (t=−0.58, structural); within-couple `gsur_male≠gsur_female` in 84.9% (mean 3.7pp) → male/female opp. equations separately identified.

---

## D5 — Circumstance promotions (urbanisation now confirmed PENDING)

**PROMOTE (still pending):** urbanisation `drgur/drgmd/drgru` (54/21/25%) into **opportunity-access only**, one increment. Verified **in-data-not-in-spec** → genuinely the next live promotion (add to a market/access block; reference category dropped; 2 df). **RETAIN AS KEY:** `drgn2`. **EXCLUDE (unchanged):** `ddi`(4 obs), `dcz`(69), `dms`, `dehde/dey/dew`, `dmb/ddt/dcu/dncsy`. **Guardrail:** access-only, one at a time, written reason, never both layers.

---

## D6 — External regional demand: deferred (first refinement)
*(unchanged from v1)* Baseline on internal access (`gsur` + region dummies + urbanisation once added); external regional labour-demand (vacancy/job-finding/sector-employment by NUTS, Eurostat/DARES/INSEE) merged on `drgn2`/`drgn1` as the first refinement. Energy = weak proxy, secondary only.

---

## D7 — Permanent inadmissibility (endogeneity wall)
*(unchanged from v1)* No `l*`/`y*` labour/income outcome in any layer, ever (`les, lfs, liwwh, liwmy, liwftmy, liwptmy, lhw, lse, lowas, lcs, lpemy, yem00, yse, yemxp, yivwg`…). Sampling/bookkeeping IDs out.

---

## D8-NEW — Sequencing: the B0→B3 ladder (replaces v1 D8)

The pilot is **between rungs**: it has the product 900-alt design and W1 wages (ahead of B0/B1) but not the focal modes, not urbanisation, not GSURv2-single-year, not the pool, not 4 LOC4 wage eqns, not SEs/welfare. Re-anchor as one diagnosable ladder, each rung one change, recovery/equivalence-gated:

| Rung | Spec | Sample | Change vs prior | Gate |
|---|---|---|---|---|
| **B0** | M1-clean, single Mincer, diagonal, **D1 focal modes**, **GSURv2** | single-year 2016 | focal modes + GSURv2-single-year merge | recovery test |
| **B1** | B0 spec | **P3a pool**, `idorighh`-clustered | pooling + cluster-robust SEs | SEs sane; LL/fit |
| **B2** | + product 900-draw couples (+ urbanisation, D5) | P3a | draw design + 1 access increment | stable vs B1 |
| **B3** | + 4 free LOC4 wage equations | P3a | wage structure W1→4-eqn | recovery test (≈40 wage params) |

Notes: the **NC pilot ≈ a B2-flavoured couples-only probe** (product+W1) that skipped B0/B1 — its feasibility PASS de-risks B2's machinery but does not substitute for the gated ladder. Estimator choice + runtime (pilot §17) are parked and orthogonal to this economic ladder.

---

## D9 — pi0 / empty-feasible-set requirement
*(unchanged from v1)* Opportunity layer must represent a tiny/empty feasible set (`pi0`/market mass) or a forced h=0 leaks into preferences and understates opportunity inequality. Confirm in implementation.

---

## D10 — Standing guardrails
*(unchanged from v1)* No `l*`/`y*` in any layer; no circumstance var in both layers; one increment at a time with a written reason; education/experience never in access; ability always bracketed, never folded into opportunity; data decides feasibility/shape/redundancy only, not roles; no reported decomposition before the recovery test passes.

---

## D11 — Observed participation definition (chosen-row anchor + welfare margin)

**Decision.** `working == 1` iff `lhw_obs > 0` (equivalently `les ∈ {1,2,3,10}` and `lhw > 0`). The chosen alternative encodes observed `(working, lhw, occ, wage)`; earnings reconstruct deterministically as `lhw × yivwg × (52/12) = yem00`-equivalent, identical to the simulated-draw earnings map.

**Evidence.** The 280 chosen-vs-survey participation "flips" (1.5%) are 100% the EU-SILC reference-period mismatch (`lhw` = reference week; `yem` = prior calendar year): 102 A1 employees (`les = 3`, `lhw > 0`, `yem_obs = 0`, late job start) recovered as workers; 178 A2 non-employed (`les ∈ {5,7}`, `lhw = 0`, residual `yem`) placed at the non-work corner. `les_obs` is preserved in every case. No build defect. Verified read-only across all 6 priced files.

---

## D12 — Welfare object: base employment income (yem00), overtime/bonus excluded

**Decision.** Structural earnings = `lhw × yivwg × (52/12)`, which is `yem00`-equivalent (base pay at the imputed hourly wage). `yemxp` (overtime + bonus + multi-job, per DRD `yem = yem00 + yemxp`) is NOT in the priced consumption; `yivwg` is a base hourly rate by construction. Money-metric well-being is therefore measured on base employment income.

**Consequence.** For the worker tail, `yemxp` reaches €9k-€21k; results must state this boundary explicitly and, at the welfare stage, report robustness to the 102 wage-imputed-earnings households. Defensible: overtime/bonus is not a clean chosen-hours decision.

---

## Open items to confirm during implementation

1. **Single-year 2016 GSURv2 merge** — run it (the untagged GSURv2 files carry v1 in sidecar) if B0 single-year-GSURv2 is wanted; else B0 starts directly on P3a-GSURv2 and B1 collapses into B0.
2. D1 band tolerances, 37h→FT, mixture form (draws script).
3. `pi0` empty-set representation (D9).
4. Recovery-test design — `RURO_recovery_test_design_v1.md`.
5. Estimator/runtime — parked (pilot §17), orthogonal to this memo.
