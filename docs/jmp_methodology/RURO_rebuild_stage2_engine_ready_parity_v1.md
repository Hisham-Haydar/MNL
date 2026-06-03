# RURO Rebuild — Stage Three, Increment Three-B1: staged engine-ready assembly + pre-estimation parity gates

**Date:** 2026-06-04
**Increment:** STAGE THREE, INCREMENT THREE-B1 only — assemble the validated reproducible
staged baseline into engine-ready estimation objects and run pre-estimation parity gates
(structure / row-order, consumption blast-radius, likelihood parity at certified `theta_hat`).
**Status:** complete. **VERDICT: READY for Three-B2 (controlled re-estimation).** Structure /
row-order gates PASS, the consumption blast-radius is fully quantified with the `c_scale`
channel separated, the addendum no-change control PASSES at machine epsilon, and the staged
likelihood is computable with the certified JAX machinery at certified `theta_hat`.

The staged engine-ready differs from certified **only** through `ils_dispy_real` →
`consumption` (and the `c_scale`-renormalised `c_norm`) on benefit-recipient rows; every
structural field — rows, households, alternatives-per-HH (101 / 901), the chosen indicator,
draw keys, row order, and the cluster key `idorighh` — is **byte-identical**.

> **No re-estimation; no synthetic recovery; no `V_i^dir`; no redrawn-node pricing; no `W^3`
> promotion; no production parquet swapped, overwritten, moved, or deleted; no promotion of the
> staged baseline to canonical; nothing beyond `W^3`.** Staged engine-ready uses a DISTINCT
> stem (`fr_p3a_bpool_engine_ready_staged_threeB1`); the certified engine-ready files are
> unchanged (2026-05-30). Not committed automatically.

---

## Task 1 — staged engine-ready assembled (STAGING-ONLY)

Built through the **same construction path** as the certified estimate
(`build_bpool_estimation_ready.py` → `harmonise_bpool_engine_ready.py`), with the **only**
redirection being the priced `ils_dispy_real` source: the Three-A-validated Two-N staged
chunks instead of the stored production priced files. Preserved by construction (same code):

- same spec and draw resolution (singles 101 alts; couples 901 = 900-product + chosen);
- same row ordering convention (`sort_values(["idhh", draw])` in harmonise);
- same choice indicators (`is_chosen` / `is_chosen_joint`);
- same cluster key `idorighh` → `cluster_id`;
- same `c_scale = mean(consumption)` over all rows;
- same two-deflation discipline (EUROMOD inputs nominal upstream; estimator wages 2016-real;
  post-EUROMOD CPI `phi_y` per data year) — the staged build re-applies the identical
  `deflate_wages_for_estimation`;
- same system pairing + CPI as the Three-A pinned config (read from the build module).

**Outputs (distinct stem, never overwriting certified):**
`fr_p3a_bpool_engine_ready_staged_threeB1__{singles,couples}.parquet` (51.3 / 341.3 MB,
matching certified sizes) + `__mnlmeta.json`. Staged priced + estimation-ready intermediates
in `…/EUROMOD-STORAGE/new_data/staging_threeB1_priced/` and the staged estimation-ready under
a `…_staged_threeB1` stem. **Certified engine-ready untouched** (still 2026-05-30).

---

## Task 2 — structure / row-order gates (PASS)

Staged vs certified engine-ready, per mode:

| check | singles | couples |
|---|---|---|
| row count match | ✓ | ✓ |
| household count match | ✓ | ✓ |
| alternatives per HH (uniform) | ✓ (101) | ✓ (901) |
| one chosen row per choice set | ✓ | ✓ |
| row order (positional key identity) | ✓ | ✓ |
| draw key identical | ✓ | ✓ |
| chosen indicator identical | ✓ | ✓ |
| cluster key (`idorighh`) identical | ✓ | ✓ |

**Exact structural alignment** — every key, draw, choice indicator, and the cluster key is
positionally identical between certified and staged. The only intended difference is the
consumption value.

---

## Task 3 — consumption blast-radius (descriptive; `c_scale` channel separated)

Per the addendum, the three channels are reported separately.

**(1) Raw `consumption` / `ils_dispy_real` blast** (the intended, benefit-driven change):

| mode | rows changed | share | max |Δ| | choice sets touched |
|---|---|---|---|---|
| singles | 14,276 / 505,707 | 2.82 % | €360.51 | (HH with any changed row) |
| couples | 763,526 / 6,701,638 | 11.39 % | €1,163.68 | — |

The prevalence and magnitudes match the Two-N means-tested divergence exactly (singles ≈ few %,
couples ≈ 11 %, max ~€1.16k). Change is on benefit-recipient rows; income/contributions
unchanged (established upstream).

**(2) `c_scale` old vs new** (mean of consumption over all rows; shifts slightly because the
benefit rows changed):

| mode | cert `c_scale` | staged `c_scale` | % change |
|---|---|---|---|
| singles | 2036.4900 | 2034.9890 | **−0.0737 %** |
| couples | 3936.0089 | 3927.0944 | **−0.2265 %** |

**(3) `c_norm` denominator channel (no-change control).** On rows whose **raw consumption did
NOT change**, staged `c_norm` must equal `cert c_norm × (c_scale_cert / c_scale_staged)` — i.e.
differ ONLY through the global denominator. Result:

| mode | raw-unchanged rows | max rel. residual vs prediction | rows above 1e-9 rel | control |
|---|---|---|---|---|
| singles | 491,431 | **4.78e-16** | 0 | **PASS** |
| couples | 5,938,112 | **5.74e-16** | 0 | **PASS** |

At machine epsilon, **every raw-unchanged row differs only through the shared `c_scale`
denominator** — there is no unintended row-level data change. (Total `c_norm` changes on all
rows via the renormalisation; that is expected and is NOT a row-level data-change count.)

*Note:* `ils_ben` is not carried on engine-ready (only `consumption` / `c_norm`), so the
benefit-recipient split is not separable at this layer; it was quantified upstream
(Two-N / Three-A). Reported as such, not guessed.

---

## Task 4 — likelihood parity at certified `theta_hat` (certified JAX machinery)

The certified joint negLL (`build_joint_neg_ll`, spec `joint_pooled_v1_bll0_tlmpin`, 47 params)
evaluated at the certified `theta_hat` (loaded from `theta_hat_realdata_901_v1.csv`) under three
`c_norm` regimes, **no optimisation**:

| regime | joint negLL | singles_male | singles_female | couples |
|---|---|---|---|---|
| **A** certified | 238504.6361 | 28489.0428 | 35411.8635 | 174603.7298 |
| **B** staged, native staged `c_scale` | 238502.8669 | 28489.1663 | 35411.8310 | 174601.8697 |
| **C** staged, fixed certified `c_scale` | 238502.8667 | 28489.1665 | 35411.8305 | 174601.8697 |

**ΔnegLL decomposition** (total = raw-consumption channel + `c_scale` channel):

| channel | joint | singles_male | singles_female | couples |
|---|---|---|---|---|
| **total (B − A)** | **−1.76916** | +0.12347 | −0.03255 | **−1.86007** |
| raw-consumption (C − A) | −1.76938 | +0.12368 | −0.03299 | −1.86007 |
| **`c_scale` channel (B − C)** | **+0.00022** | −0.00022 | +0.00043 | +0.00000 |

Findings:

- The staged likelihood is **computable with the certified machinery** at certified `theta_hat`
  (the prerequisite Three-B2 needs).
- The total ΔnegLL is **−1.77** (staged fits marginally *better* at the certified θ̂),
  **localised to couples** (−1.86) — the benefit-heavy group whose consumption changed — with
  small offsetting singles moves (+0.12 / −0.03).
- The **pure `c_scale` channel is +0.0002 across all groups** (machine-negligible): the LL
  change is **entirely the raw-consumption channel**, not the global renormalisation. This is
  the addendum's no-change control at the likelihood level — groups/rows whose raw consumption
  is unchanged contribute essentially identical V (the residual is the `c_scale` denominator
  only, ~1e-4 nats total).

This is **descriptive**: it quantifies the blast radius of the corrected baseline on the
certified likelihood. **It is NOT a re-estimation** and does not interpret parameter movement —
that is Three-B2.

---

## Task 5 — readiness for Three-B2

| requirement | result |
|---|---|
| structure / row-order gates pass | ✓ |
| no unintended field changes (beyond the intended consumption + `c_scale` channel) | ✓ |
| no-change control passes (raw-unchanged rows differ only via `c_scale`) | ✓ |
| staged LL computable at certified `theta_hat` with certified machinery | ✓ |
| blast radius fully quantified | ✓ |

**`ready_for_threeB2 = TRUE`.**

Explicitly:

- **No re-estimation, no synthetic recovery** were run.
- **No `V_i^dir`, no redrawn-node pricing, no `W^3` promotion**, nothing beyond `W^3`.
- **No production parquet swapped, overwritten, moved, or deleted**; certified engine-ready
  unchanged (2026-05-30).
- **The staged baseline is NOT canonical**; the staged engine-ready uses a distinct stem.
- **Controlled re-estimation (Three-B2) is a SEPARATE authorisation** and was NOT performed.

The corrected staged baseline is assembled, structurally identical to the certified engine-ready
except for the intended benefit-driven consumption change, and its likelihood is computable at
the certified `theta_hat` — the conditions Three-B2 (the Two-O dispositive controlled
re-estimation) requires before it can run.

---

## Files

- **Driver:** `scripts/welfare/run_stage3b1_engine_ready_parity.py` (Tasks 1–5; reuses the
  certified `build_bpool_estimation_ready` + `harmonise_bpool_engine_ready` build path with the
  priced source redirected to staged; 3-regime LL via the certified `build_joint_neg_ll` /
  per-group builders). Ruff-clean; config-driven; no hardcoded country/year/spec constants.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage3b1_engine_ready_parity.json`
  (all tasks + readiness + the 3-regime LL decomposition).
- **Staged engine-ready (distinct stem, staging-only):**
  `…/EUROMOD-STORAGE/new_data/fr_p3a_bpool_engine_ready_staged_threeB1__{singles,couples}.parquet`
  (+ `__mnlmeta.json`); fixed-`c_scale` diagnostic variant
  `…_staged_threeB1_fixedcscale__{singles,couples}.parquet`; staged estimation-ready under
  `…_estimation_ready_staged_threeB1` stem; staged priced + intermediates in
  `…/EUROMOD-STORAGE/new_data/staging_threeB1_priced/`. **NOT canonical, NOT committed.**

## Explicit scope statement

No re-estimation; no synthetic recovery; no `V_i^dir`; no redrawn pricing; no `W^3` promotion;
no production swap; no promotion to canonical; nothing beyond `W^3`. This increment assembles
the staged engine-ready objects and runs pre-estimation parity gates only; the controlled
re-estimation is the separately authorised Three-B2.
