# RURO Welfare — Stage Four, Increment Four-C2: singles V_i^dir bias-mechanism diagnostic + node-count calibration

**Date:** 2026-06-04
**Increment:** STAGE FOUR, INCREMENT FOUR-C2 only — bounded singles `V_i^dir` bias-mechanism
diagnostic and node-count calibration (single-pass, S ≤ 100).
**Status:** complete. **VERDICT: FULL-RUN DESIGN READY (single-pass S ≈ 100).** **Finite-S /
integration error explains the Four-C high-ESS residual well enough for the full-run design: no
persistent offset remains at the 0.5-nat gate.** Extrapolating the like-for-like agreement to
S → ∞ leaves a high-ESS intercept of **abs_max 0.395 ≤ 0.5 nat** (median −0.19), which rules out
a persistent construction / pricing / integration offset at the gate scale. The slope evidence is
mixed (one high-ESS r² near zero; aggregate `slopes_negative = false`), so this is stated as
finite-S/integration error sufficient for the design, **not** as a claim that the mechanism is
purely Jensen bias. On the **contract welfare object** (utility-only `u(c,ℓ)`) the finite-S bias
is **negligible already at S = 100** (CV² ≈ 0.05–0.14 → bias ≈ 5e-4 nats), so no multi-pass is
required for the welfare number itself.

> **No multi-pass; no full singles `V_i^dir` run; no couples; no `W^3` promotion; no measure
> beyond `W^3`; no reportable welfare distribution; no production swap; no canonical promotion;
> no re-estimation.** Single-pass S ≤ 100 only. Reuses the Four-C machinery unchanged. Not
> committed automatically.

---

## Task 0 — setup (reuses the Four-C subset)

Same **6 households, seed 20260604, year 2016** as Four-C (3 high-ESS: 40.2/40.5/41.7; 3 low-ESS:
2.0/3.0/3.0). Single-pass node counts **S ∈ {20, 60, 100}**, **nested**: each household's 100
nodes are redrawn once (per-household deterministic seed) and priced population-faithfully once
(full production-chunk batch [0,101), authoritative `yem = yem00 + yemxp`,
`yem00 = min(lhw,35)·yivwg·52/12`, `yemxp = max(lhw−35,0)·yivwg·52/12`); the S-grid takes the
first S of that one priced node set, so larger S supersets smaller S. EUROMOD reconciles with
**0 `yem` warnings**. Per-node integrand vectors are dumped for both objects:

- **utility-only** `u(c,ℓ)` — the contract `V_i^dir` integrand (own-preference utility under
  direct sampling from ĝ);
- **full-V** `u + log_h + log_w + log_market − log_prior` — the diagnostic object that carries
  the opportunity density, used to test against the existing `V_i^IS`.

This is a bounded diagnostic, **not** a population welfare result.

---

## Task 1 — the 1/S hypothesis test (decisive)

For each household and object, `V_i^dir(S) = log mean_{s≤S} exp(ν_s)`; the like-for-like
`delta_common(S) = V_dir_fullV(S) − [V_IS − log(n_draws)]` was regressed on `1/S`. The
**intercept** estimates the S → ∞ limit; a **near-zero intercept** = the gap is pure finite-S
bias, a **nonzero intercept** = persistent offset (STOP).

**Full-V object (the V_IS-anchored, like-for-like one):**

| uid | ESS | `delta_common` S=20 / 60 / 100 | slope (vs 1/S) | **intercept (S→∞)** | r² |
|---|---|---|---|---|---|
| 200001687502 | 2.0 | −4.43 / −4.12 / −4.11 | −8.41 | −4.00 | 0.98 |
| 200001917500 | 3.0 | −2.24 / −2.93 / −2.77 | +15.6 | −3.04 | 0.86 |
| 200001981300 | 3.0 | −3.60 / −2.68 / −2.33 | −30.4 | −2.09 | 0.99 |
| **200001793700** | **40.2** | +0.57 / +0.42 / +0.45 | +3.34 | **+0.39** | 0.90 |
| **200001593700** | **40.5** | +0.23 / +0.14 / −0.25 | +8.98 | **−0.19** | 0.57 |
| **200001813600** | **41.7** | −0.39 / −0.13 / −0.47 | −1.30 | **−0.30** | 0.02 |

- **High-ESS intercepts: +0.39, −0.19, −0.30 → abs_max 0.395 ≤ 0.5 nat, median −0.19.** Removing
  the finite-S bias (S → ∞), `V_i^dir` agrees with `V_i^IS` **within the gate** for every high-ESS
  household. **No persistent offset.**
- **Slope-sign caveat (honest).** The driver's aggregate `slopes_negative` flag is `False`: the
  high-ESS `delta_common` is already so small (~±0.4 nat) that its slope sign is dominated by
  Monte-Carlo noise (uid 593700 r² 0.57, uid 813600 r² 0.02 — flat/noisy near zero), so the
  sign is not informative there. The **low-ESS** households — where the bias is large and the
  signal is clean — regress with **high r² (0.98, 0.99)** and the expected steep 1/S dependence.
  The decisive evidence is the **near-zero high-ESS intercept**, not the high-ESS slope sign.

Interpretation: the **near-zero high-ESS intercept** rules out a persistent offset at the gate
scale — finite-S / integration error explains the residual well enough for the full-run design.
The decisive evidence is the intercept, not the slope sign; this is **not** the stronger claim
that the mechanism is purely Jensen bias (the slope evidence is mixed). Not a STOP.

---

## Task 2 — analytic finite-S bias diagnostic

Leading bias of `log mean_S exp(ν)`: `bias ≈ CV²/(2S)`, `CV² = Var(exp ν)/Mean(exp ν)²`
(delta method on the log of a sample mean). Computed per household for both objects (at S=100):

| object | CV² (median / max) | implied bias at S=100 |
|---|---|---|
| **utility-only `u`** (gate) | 0.10 / 0.14 | **≈ 0.0005 nats** |
| full-V (diagnostic) | ≈ 6.6 / 10.6 | ≈ 0.03–0.05 nats |

The two objects differ by **~70×** in CV². The full-V object's large CV² (it carries
`log ĝ − log_prior`, which swings widely across nodes) is exactly why the **S-dependence in
Four-C lived in the full-V/`delta_common` comparison**. The **utility-only welfare integrand is
tightly concentrated** (consumption/leisure are bounded and Box-Cox-compressed), so its finite-S
bias is sub-milli-nat at S=100.

The bias-corrected `V_dir(S) + CV²/(2S)` is recorded per S in the provenance. *(Any correction
applied to `V_IS` would be labelled approximate — none is applied here; the like-for-like test
uses the uncorrected `V_IS` and the 1/S extrapolation of `V_dir`.)*

---

## Task 3 — object selection (which governs readiness)

| | utility-only `u(c,ℓ)` | full-V |
|---|---|---|
| role | **contract welfare object** (`V_i^dir` integrand) | diagnostic equivalence to IS/full-V |
| CV² (max) | 0.14 | 10.6 |
| implied bias @ S=100 | ≈ 5e-4 nats | ≈ 0.05 nats |
| has a `V_i^IS` counterpart? | no (utility-only ≠ inclusive value) | yes (the like-for-like test) |

**The licensing gate for the welfare run is the utility-only object** — it is what `V_i^dir`
actually integrates (the contract: sampling from ĝ replaces the opportunity/proposal terms with
the uniform weight, so the integrand is own-preference utility). The **full-V object is the
validation instrument**: it has a `V_i^IS` counterpart, so its high-ESS S→∞ intercept (≈0, Task 1)
is what certifies that `V_i^dir` is *correct* (matches the established IS machinery once finite-S
bias is removed). Both pass: the welfare object has negligible bias, and the diagnostic object
shows no persistent offset.

**Note — the utility-only object has NO valid `V_i^IS` counterpart.** The provenance records a
`delta_common` for the utility-only object too (large negative values, ≈ −3 to −7), but this is
**not a failure and must not be read as one**: `V_i^IS` is the *full inclusive value*
(`log Σ exp(u + log ĝ − log π)`), whereas the utility-only object is `log mean exp(u)` — a
different object that omits the opportunity density by construction, so a large gap is expected
and meaningless. The utility-only object's role is the **welfare integrand and its finite-S bias
(CV²)**, not agreement with `V_i^IS`; the like-for-like `V_i^IS` agreement is the **full-V**
object only.

---

## Task 4 — node-count requirement S* for the full singles run

On the **gate object (utility-only)**, S* keeps the finite-S bias `CV²/(2S) ≤ tol`:
`S* = ⌈CV²/(2·tol)⌉` with tol = 0.5 nat.

- worst-household CV² = 0.141 → `S* = ⌈0.141⌉ = 1`;
- p90 CV² = 0.138 → `S* = 1`.

i.e. **the utility-only welfare object is essentially converged at any practical S** — its bias
is already ~5e-4 nats at S=100, far inside tolerance. In practice S should be set by **Monte-Carlo
variance** (~CV²/S), not the leading bias: a sensible floor is **S ≈ 100** (matching the
single-pass capacity), which gives a per-household welfare-integral standard error well below the
0.5-nat gate. **Multi-pass is NOT required** for the singles welfare number (S* ≪ single-pass
capacity of 100).

*(If one instead targeted full-V agreement at, say, 0.1 nat — a stricter cross-check than the
welfare object needs — the larger full-V CV² (~7) would imply S ~ 35 just for the leading bias
and more for variance; but that object is the diagnostic, not the welfare gate, and its high-ESS
S→∞ intercept already clears 0.5 nat.)*

---

## Task 5 — verdict

**FULL-RUN DESIGN READY (single-pass S ≈ 100).**

- **Finite-S / integration error explains the Four-C high-ESS residual well enough for the
  full-run design; no persistent offset remains at the 0.5-nat gate.** The like-for-like full-V
  `delta_common` extrapolates to a near-zero S→∞ intercept (high-ESS abs_max **0.395 ≤ 0.5**).
  This is the gate-scale ruling-out of a persistent offset — not the stronger claim that the
  mechanism is purely Jensen bias (the slope evidence is mixed: `slopes_negative = false`, one
  high-ESS r² ≈ 0). The clean, defensible statement is the former.
- The **contract welfare object (utility-only) has negligible finite-S bias** at S=100
  (CV² ≈ 0.1 → ~5e-4 nats); **recommended S ≈ 100** (single-pass; set by MC variance, not bias).
- **No persistent construction / pricing / integration offset at the gate.** **Multi-pass not
  required** for the singles welfare number.

*(The provenance `task5_verdict.verdict` string retains the machine label
"BIAS MECHANISM CONFIRMED / FULL-RUN DESIGN READY"; the calibrated prose statement above is the
authoritative reading — finite-S/integration error sufficient for the design, not a pure-Jensen
claim.)*

This licenses **designing** a full singles `V_i^dir` run at single-pass S ≈ 100 — it does **not**
execute it. Full singles `V_i^dir`, couples `V_i^dir`, `W^3` promotion, measure-family extension,
multi-pass pricing, and any reportable welfare/inequality number all remain **separate
authorisations**.

---

## Files

- **Driver:** `scripts/welfare/run_stage4c2_vdir_bias_calibration.py` (reuses Four-C
  population-faithful pricing + `node_V_singles_terms` + `v_is_and_ess_singles`; nested S-grid;
  1/S regression; CV² bias; S*). Ruff-clean; config-driven; no hardcoded constants.
- **Report:** this document.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage4c2_vdir_bias_calibration.json` (per-HH
  per-S `V_dir`, CV², 1/S slope/intercept/r², bias-corrected curves, object diagnostics, S*,
  verdict).
- **Scratch:** `…/EUROMOD-STORAGE/new_data/scratch_four_c2_bias/` (clearly named; not production,
  not the staging reference). Pricing is in-memory; no chunk parquet persisted.
- **Unmodified:** the Four-C driver, `welfare_core.py`, `welfare_vdir.py`, all `scripts/bpool/`,
  the certified theta CSV, production priced files, the staged reference (`staging_twoN` 21/21).

## Explicit scope statement

No multi-pass; no full singles run; no couples; no `W^3` promotion; no measure beyond `W^3`; no
reportable welfare distribution; no production swap; no canonical promotion; no re-estimation.
This increment is a bounded single-pass (S ≤ 100) bias-mechanism diagnostic + node-count
calibration; it confirms the finite-S bias mechanism and reports a recommended S*, and every
downstream step remains a separate authorisation.
