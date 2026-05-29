# RURO real-data 2016 estimation — bpool_p3a_v1, all slices, CONOPT

**Date:** 2026-05-29
**Spec:** bpool_p3a_v1 (55 free params; `beta_c=1` numéraire, couples `theta_c=0`)
**Solver:** GAMSPy CONOPT, vectorized
**Data:** real chosen alternatives from `fr_p3a_bpool_engine_ready__{singles,couples}.parquet`,
filtered to 2016 via `scripts/bpool/slice_engine_ready.py` (no synthetic redraw)
**Starts:** warm = theta\* (`recovery_test.generate_theta_star`, seed 20260527);
cold = spec initial values

## TL;DR

**The bpool_p3a_v1 spec is identified and basin-stable on real 2016 data
across all three estimation groups.** Two-start agreement (G2 analog) on
the data-identified ("active") parameters is **machine-epsilon (≤ 9.2e-09)**
on every slice. Warm and cold reach bit-identical LL. The only parameters
that differ between starts are the **inert** ones the slice structurally
cannot identify (cross-group blocks, wrong-year indicators) — they stay
pinned at their starting value, which is correct behavior, not a problem.

## Headline numbers

| group | n_hh | alts | warm LL | cold LL | Δ(warm,cold) LL | wall | iters |
|---|---:|---:|---:|---:|---:|---:|---:|
| singles_male   |   766 | 101 | −9746.176645 | −9746.176645 | 2e-12 | ~25 s | 9 / 10 |
| singles_female | 910 | 101 | **−11684.8391** | **−11684.8391** | 0 | ~27 s | 9 / 10 |
| couples        | 2,577 | 901 | −60767.131083 | −60767.131083 | 8e-11 | **~4.5 h** | 11 / 17 |

> **singles_female numbers are the FIXED runs** (`sf2016_conopt_{warm,cold}_FIXED`).
> The original Step-3 singles_female runs (LL −11686.9420) hit the
> `_sm`/`_sf` leisure-suffix bug (finding #6) and are SUPERSEDED. The fix
> (passing `group=` to the GAMSPy singles path) added the female leisure
> block + female `n_children` effect, improving the LL by +2.10. The
> singles_male and couples runs were never affected.

All runs report `SolveStatus.NormalCompletion` /
`ModelStatus.OptimalLocal`. All Hessians are non-PD (cond=inf) — expected,
driven by the inert cross-group parameters; the active-block estimates are
unaffected.

**Note on couples runtime:** ~4.5 h is intrinsic single-threaded CONOPT
solve time on the 2,577×901 NLP, NOT core contention (CONOPT uses ~2% CPU
= 1 core of 64). See `project-couples-conopt-runtime.md` in memory. Budget
couples-full as a multi-hour job.

## G2 — two-start agreement on active parameters

| group | n_active | max\|warm − cold\| (active) |
|---|---:|---:|
| singles_male   | 20 | 9.21e-09 |
| singles_female (FIXED) | 21 | 9.93e-12 |
| couples        | 36 | 1.15e-09 |

The "active" set per slice = the parameter blocks the slice's data
actually identifies:

- **singles_male:** the `_sm`-suffixed leisure block, `theta_c_singles`,
  the universal market-opportunity/hours/wage blocks, `beta_occ_*_sm`,
  `sigma`.
- **singles_female:** (post-fix) the `_sf`-suffixed leisure block
  including the female-only `beta_l_nkids_sf`, `theta_c_singles`, the
  universal blocks, `beta_occ_*_sf`, `sigma`. (Before the fix it
  incorrectly used the `_sm` block — see finding #6.)
- **couples:** couples male+female (`_m`/`_f`) leisure blocks, the full
  market-opportunity block (region drgn2-8, urban/middle access),
  `beta_occ_*_cm/cf`, universal hours/wage/sigma.

Everything outside a slice's active set (e.g. singles-female params on the
singles-male slice; year-2015/2017 indicators on a 2016-only slice;
singles params on the couples slice) is inert: it stays at its starting
value and therefore differs by up to 1.2 between warm and cold. That is
the expected fingerprint of a single-slice / single-year run, not an
identification failure.

## Parameter estimates (active blocks; warm-start values, identical to cold to 8+ dp)

singles_female values are the FIXED runs (`sf2016_conopt_*_FIXED`).

| param | singles_male | singles_female | couples | notes |
|---|---:|---:|---:|---|
| **Leisure (own block)** | (`_sm`) | (`_sf`) | (`_m` / `_f`) | each group's own suffix |
| beta_l0 | 0.5841 | 0.4198 | m 0.0072 / f 1.7218 | leisure intercept |
| theta_l | −0.8223 | −0.8092 | m −0.8245 / f −0.7669 | Box-Cox leisure exponent |
| beta_l_age | 0.1621 | −0.0254 | m −0.0099 / f −0.2229 | |
| beta_l_age2 | 0.0395 | 0.3365 | m 0.0187 / f 0.2637 | |
| beta_l_nkids | — (male: none) | **0.6341** | 0.4326 (f) | female-only n_children leisure shifter |
| theta_c_singles | −0.0560 | −0.0204 | (fixed/inert) | pooled singles consumption BC |
| **Hours opportunity** | | | | |
| beta_E | −1.9352 | −1.0048 | −0.7114 | base employment attractiveness |
| beta_h_pt1 | −1.2854 | −0.9686 | −1.7040 | |
| beta_h_pt2 | −2.1115 | 0.1488 | −0.0538 | sign flips sm→sf |
| beta_h_ft | 1.1553 | 0.6951 | 1.1281 | |
| beta_h_lh | −1.5780 | −1.8428 | −1.2201 | long-hours increment |
| beta_E_gsur | −1.3556 | −2.3237 | −1.3890 | |
| **Market opportunity (region/access)** | | | | |
| beta_E_drgn2..8 | (inert) | (inert) | 0.084 … −0.008 | identified on couples only |
| beta_E_drgur | (inert) | (inert) | −0.1654 | urban access |
| beta_E_drgmd | (inert) | (inert) | −0.7119 | middle access |
| **Occupation** | | | | |
| beta_occ_2/3/4_sm | −1.498 / −2.087 / 0.064 | (inert) | (inert) | sm-slice only |
| beta_occ_2/3/4_sf | (inert) | −0.021 / −0.498 / 0.831 | (inert) | sf-slice only |
| beta_occ_2/3/4_cm | (inert) | (inert) | −1.579 / −2.403 / 0.326 | couples only |
| beta_occ_2/3/4_cf | (inert) | (inert) | 0.094 / −0.355 / 0.807 | couples only |
| **Wage** | | | | |
| beta_w0 | 2.1652 | 2.2249 | 2.2157 | very stable across slices |
| beta_w_educL | 0.1477 | −0.1023 | −0.1071 | sm positive, others negative |
| beta_w_educH | 0.3322 | 0.3376 | 0.3537 | stable, correct sign |
| beta_w_pexp | 0.3219 | 0.1839 | 0.3691 | correct sign (was wrong in synthetic) |
| beta_w_pexp2 | −0.0742 | −0.0285 | −0.0769 | correct concavity |
| sigma | 0.4239 | 0.4017 | 0.4136 | wage-eqn scale; very stable |
| beta_ll | 2.5000 (inert) | 2.5000 (inert) | 0.0000 (at bound/inert) | see note |

Full 55-param vectors per slice (including inert) are in the per-group CSVs:
`estimation_results_{singles_male,singles_female,couples}.csv` under each
output dir.

## Observations

1. **`beta_w_pexp` recovers with the CORRECT (positive) sign on real data**
   for all three slices (0.18–0.37). This is notable because the synthetic
   recovery test left it wrong-signed (see
   `workitem-recovery-residuals-beta_ll-beta_w_pexp.md`). On real chosen
   data the experience-profile is identified correctly — another sign that
   the synthetic harness, not the spec, produced the recovery residuals.

2. **`beta_ll` is inert / at bound on every real-data slice.** On singles
   it stays at the warm/cold start (2.5 / 2.0); on couples it lands at 0.0
   (a bound). `beta_ll` (the "leisure-leisure" or long-leisure term) is not
   identified by any single 2016 slice. This matches the v3 recovery
   residual finding and means `beta_ll` needs either the full multi-year
   pool or a different identification strategy.

3. **The wage block (`beta_w0`, `beta_w_educH`, `sigma`) is remarkably
   stable across all three groups** (beta_w0 ≈ 2.17–2.23, sigma ≈
   0.40–0.42), as expected for a shared wage technology.

4. **`beta_h_pt2` flips sign between singles_male (−2.11) and
   singles_female (+0.15).** Plausible behavioral heterogeneity (men and
   women differ in the attractiveness of the pt2 hours band) but worth a
   look in the post-estimation report (Step 4).

5. **Hessian non-PD on every slice** is fully explained by the inert
   cross-group parameters (they create exact flat directions). The patched
   recovery_test G3b diagnostic (commit c90d47a) would name these
   directions if run; for the production estimator the
   `identification_diagnostics.txt` in each output dir already flags
   which params have non-positive variance.

6. **CONFIRMED BUG (now FIXED) — singles_female was estimating the
   `_sm`-suffixed leisure block.** The original Step-3 singles_female runs
   (LL −11686.94) incorrectly used the male leisure coefficients and
   silently dropped the female-only `beta_l_nkids_sf`. Root cause:
   `enh_RURO_estimate_FR.py` single-group GAMSPy path called
   `estimate_singles_gamspy(data=data_sf, ...)` WITHOUT `group=`, which
   defaults to `"singles_male"`, so coefficient lookup resolved to the
   `_sm` suffix. The joint path (passes `group="singles_female"`) and the
   numpy path (derives suffix from `data.is_male`) were never affected.

   **Fix:** pass `group=group_name` at both single-group call sites, plus a
   `group`/`data.is_male` consistency guard in both GAMSPy singles entry
   points so the mismatch can never be silent again.

   **Verified (fixed runs, warm = cold):** LL −11686.94 → **−11684.84**
   (+2.10); `beta_l0_sf` 1.25(inert) → 0.4198; `theta_l_sf` → −0.8092;
   `beta_l_nkids_sf` → **+0.6341** (single mothers value leisure more — the
   effect that was silently absent); `beta_l0_sm` returns to its untouched
   start. Two-start agreement on the corrected `_sf` block is 9.93e-12.
   All numbers in this report's tables are the FIXED singles_female runs.

   See `workitem-bpool-singles-female-leisure-suffix.md` (CLOSED). The
   singles_male and couples estimates were never affected.

## Output locations

- singles_male warm: `outputs/estimation/realdata_multibasin/sm2016_conopt_from_thetastar/`
- singles_male cold: `outputs/estimation/realdata_2016/sm2016_conopt_cold/`
- singles_female warm/cold (**FIXED, canonical**): `outputs/estimation/realdata_2016/sf2016_conopt_{warm,cold}_FIXED/`
- singles_female warm/cold (buggy, superseded): `outputs/estimation/realdata_2016/sf2016_conopt_{warm,cold}/`
- couples warm/cold: `outputs/estimation/realdata_2016/c2016_conopt_{warm,cold}/`

(all under `C:\Users\hisham\MNL\EUROMOD-STORAGE\`)

## Related

- `RURO_realdata_multibasin_test_v1.md` — Step 2: scipy reaches same basin
- `RURO_recovery_test_results_v3.md` — synthetic recovery verdict (i)
- `workitem-recovery-residuals-beta_ll-beta_w_pexp.md` — the residuals; this
  real-data run shows beta_w_pexp is fine on real data, beta_ll still
  unidentified on single slices
- `project-couples-conopt-runtime.md` (memory) — couples ~4.5h budget
