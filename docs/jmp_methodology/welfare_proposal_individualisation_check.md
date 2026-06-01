# Welfare proposal individualisation check

**Date:** 2026-06-01
**Class:** read-only findings note. No edits, no script execution; file/grep
inspection only. Answers, for the welfare `-log π(j)` correction: does the
proposal distribution condition on individual/household characteristics `x_i`, or
is it a common distribution identical across individuals?

**Verdict (one line): the proposal is PARTLY individualised.** The wage and
occupation channels condition on `x_i` (education, experience, occupation,
gender), so `log_prior` **does vary across households for the same `(w,h)` node**.
The hours channel and the employment-state channel are **common** (identical
across all households).

---

## Where the draws and `log_prior` are built

- **Singles:** `scripts/bpool/build_bpool_singles.py`
  (`_draw_singles_block`, 100 simulated alts + 1 chosen = 101).
- **Couples:** `scripts/bpool/build_bpool_couples.py`
  (`_draw_partner_marginals`, 30 marginal alts per partner → 30×30 = 900 joint +
  1 chosen = 901).
- **Channel draw functions:**
  `scripts/pilot/pilot_wage_draw.py` (`draw_pilot_wages`),
  `scripts/bpool/occ_draw_empirical.py` (`draw_loc4`),
  `scripts/bpool/hours_mixture_d1.py` (`draw_hours_d1`).
- **`log_prior` formula** (identical for singles and per couples-partner):
  `log_prior = log_q_E + working * (log_q_Occ + log_q_H + log_q_W)`
  (`build_bpool_singles.py:175`; couples
  `log_prior = log_prior_m + log_prior_f`, partners independent,
  `build_bpool_couples.py:20-22`).
- **Engine consumption:** the per-alternative `prior = exp(log_prior)` column is
  read row-by-row and the estimator forms
  `V = u + log_h + log_w + log_market − log_prior`
  (`jax_ll_probe.py:132-133,260` and `:307-308,461`). So whatever
  household-variation is baked into `log_prior` at draw time flows directly into
  estimation and into the welfare `V_i`.

---

## (a) Exact variables entering the proposal

| Channel | Term | Conditions on | Source |
|---|---|---|---|
| Employment | `log_q_E` | **nothing** — fixed `pi0 = 0.10` (`log(pi0)` / `log(1−pi0)`) | `build_bpool_singles.py:60,123`; couples `:60,110` |
| Occupation | `log_q_Occ` | **`dgn` (gender) × `educ3` (education band)** — empirical stratum frequencies `p(loc4 | dgn, educ3)` | `occ_draw_empirical.py:13,21,49-56`; called `build_bpool_singles.py:134` |
| Hours | `log_q_H` | **nothing** — fixed D1 five-mode mixture weights; `draw_hours_d1(n, rng, weights=None)` takes no covariate | `hours_mixture_d1.py:83-86`; `D1_SPEC` |
| Wage | `log_q_W` | **`educL`, `educH`, `pexp_years`, `pexp_years2`, `loc4`** (mean `μ_i = X_i·b + δ_occ[loc4_i]`); common `σ` | `pilot_wage_draw.py:68-81`; called `build_bpool_singles.py:157-170` |

The wage coefficients `b` and `σ` are **calibrated and common** across households
(`pilot_mincer_coefficients_v1.json`, W1 baseline); individualisation enters
through the **covariates `X_i`**, not through per-household coefficients.

---

## (b) Are wage / hours / market(-intensity) draws individualised or common?

- **Wage draws — INDIVIDUALISED.** The proposal log-wage is
  `log w ~ Normal(μ_i, σ²)` with
  `μ_i = intercept + b_educL·educL_i + b_educH·educH_i + b_pexp·pexp_i + b_pexp2·pexp_i² + δ_occ[loc4_i]`
  (`pilot_wage_draw.py:68-81`). The mean is household-specific; the drawn wages
  and the wage density both depend on `x_i`. (`σ` common.)
- **Hours draws — COMMON.** `draw_hours_d1` samples a five-mode focal mixture with
  fixed weights and band widths, independent of any `x_i`
  (`hours_mixture_d1.py:83-86`). Every household faces the **same** hours grid and
  the same hours density.
- **Occupation draws — INDIVIDUALISED (by gender × education).** `draw_loc4` draws
  `loc4` from empirical frequencies in the `(dgn, educ3)` stratum
  (`occ_draw_empirical.py:49-56`); `log_q_Occ` is the log of that
  stratum-conditional probability, so it varies across the gender×education cells.
- **Employment-state ("market / non-market intensity") — COMMON.** The
  non-employment probability is a fixed `pi0 = 0.10` for everyone
  (`log_q_E ∈ {log 0.10, log 0.90}`); it does **not** condition on region, GSUR,
  or any `x_i`. (Note: the **structural** market-opportunity block — GSUR, region,
  year — enters utility `g` via `log_market` and is estimated; it is **not** part
  of the *proposal* `π`. The proposal employment split is the flat 10%.)

---

## (c) Does `log_prior` vary across households for the same `(w, h)` node?

**Yes — through the wage and occupation channels.** For two households evaluated
at the *same* drawn wage `w` and hours `h`:

- `log_q_W` differs whenever their `(educL, educH, pexp, pexp², loc4)` differ,
  because the log-normal density is evaluated at the household-specific mean `μ_i`
  (`pilot_wage_draw.py:68-81`). Same `w`, different `x_i` ⇒ different `log_q_W`.
- `log_q_Occ` differs whenever their `(dgn, educ3)` stratum differs
  (`occ_draw_empirical.py`).
- `log_q_H` is identical (hours common) and `log_q_E` is identical (flat `pi0`).

So `log_prior` is **not** a single common function of `(w, h)`; it is
household-specific via education, experience, occupation, and gender. The
individualisation is **covariate-driven** (common coefficients/weights/`σ`/`pi0`,
individual `X_i`), not coefficient-driven.

The chosen row (`draw == 0`) is the importance-sampling anchor: all `log_q_*` are
set to 0 there (`build_bpool_singles.py:225-229`), so the individualisation
applies to the simulated alternatives, which is where the proposal correction
operates.

---

## Implication for the welfare contract (recorded, not acted on)

The welfare `-log π(j)` term (`RURO_welfare_scaffold_design_contract_v1.md` §3.1)
inherits this structure unchanged, because the welfare core reads the **same**
`prior` column and the same engine construction. Two consequences worth flagging
for the welfare/decomposition work, neither requiring any change here:

1. The proposal is **partly `x_i`-conditional** (wage + occupation), so the
   correction term is not a household-invariant constant; any welfare or
   simulation-consistency check must treat `log π(j)` as household-specific, which
   the existing per-row `prior` column already supports.
2. The hours and employment channels are **common**; if a later robustness ever
   needs an individualised hours or employment proposal, that is a draw-builder
   change (`hours_mixture_d1.py` / the `pi0` constant), not an engine or welfare
   change — out of scope for the current contract.

No files were modified and no scripts were executed in producing this note.
