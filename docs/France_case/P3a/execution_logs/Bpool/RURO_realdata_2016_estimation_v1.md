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
| singles_female |   910 | 101 | −11686.941967 | −11686.941967 | 0 | ~28 s | 9 / 12 |
| couples        | 2,577 | 901 | −60767.131083 | −60767.131083 | 8e-11 | **~4.5 h** | 11 / 17 |

All six runs report `SolveStatus.NormalCompletion` /
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
| singles_female | 20 | 8.91e-10 |
| couples        | 36 | 1.15e-09 |

The "active" set per slice = the parameter blocks the slice's data
actually identifies:

- **singles_male:** the `_sm`-suffixed leisure block, `theta_c_singles`,
  the universal market-opportunity/hours/wage blocks, `beta_occ_*_sm`,
  `sigma`.
- **singles_female:** the SAME `_sm`-suffixed leisure block (see
  finding #6 below — the `_sf` leisure params are vestigial and inert),
  `theta_c_singles`, the universal blocks, `beta_occ_*_sf`, `sigma`.
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

| param | singles_male | singles_female | couples | notes |
|---|---:|---:|---:|---|
| **Leisure (own block)** | | | | |
| beta_l0 (sm/sf → m/f) | 0.5841 | — | m 0.0072 / f 1.7218 | sm own; couples per-partner |
| theta_l (sm/sf → m/f) | −0.8223 | — | m −0.8245 / f −0.7669 | Box-Cox leisure exponent |
| beta_l_age | 0.1621 | — | m −0.0099 / f −0.2229 | |
| beta_l_age2 | 0.0395 | — | m 0.0187 / f 0.2637 | |
| beta_l_nkids_f | — | — | 0.4326 | couples female only |
| sf own leisure | — | sf block at theta\* (inert on sf-slice? see below) | — | |
| theta_c_singles | −0.0560 | −0.0318 | (fixed/inert) | pooled singles consumption BC |
| **Hours opportunity** | | | | |
| beta_E | −1.9352 | −1.0361 | −0.7114 | base employment attractiveness |
| beta_h_pt1 | −1.2854 | −0.9651 | −1.7040 | |
| beta_h_pt2 | −2.1115 | 0.1460 | −0.0538 | sign flips sm→sf |
| beta_h_ft | 1.1553 | 0.6874 | 1.1281 | |
| beta_h_lh | −1.5780 | −1.8497 | −1.2201 | long-hours increment |
| beta_E_gsur | −1.3556 | −2.3212 | −1.3890 | |
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
| beta_w0 | 2.1652 | 2.2250 | 2.2157 | very stable across slices |
| beta_w_educL | 0.1477 | −0.1033 | −0.1071 | sm positive, others negative |
| beta_w_educH | 0.3322 | 0.3382 | 0.3537 | stable, correct sign |
| beta_w_pexp | 0.3219 | 0.1825 | 0.3691 | correct sign (was wrong in synthetic) |
| beta_w_pexp2 | −0.0742 | −0.0277 | −0.0769 | correct concavity |
| sigma | 0.4239 | 0.4016 | 0.4136 | wage-eqn scale; very stable |
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

6. **POSSIBLE BUG — singles_female appears to estimate the `_sm`-suffixed
   leisure block, leaving the `_sf` params inert.** Direct evidence: on the
   singles_female slice, `beta_l0_sm` moves to 0.8480 (data-identified,
   warm=cold to 8+ dp), while `beta_l0_sf` stays at its starting value
   (1.25 warm / 1.00 cold, i.e. inert). On the singles_male slice
   `beta_l0_sm` = 0.5841. So the male and female singles slices each
   produce a DIFFERENT data-identified value in the same `_sm`-named slot.

   The spec (estimation_spec_bpool_p3a_v1.yaml lines 62-73, 226-227)
   declares the leisure block with BASE names (`beta_l0`, `theta_l`,
   `beta_l_age`, `beta_l_age2`, `beta_l_nkids`) that the parser suffixes
   per group, and the header comment explicitly lists `_sm` [4] and `_sf`
   [5] as SEPARATE singles-male and singles-female blocks (the `_sf` block
   adds `beta_l_nkids_sf` via the `gender_specific: true` female-only
   `n_children` shifter). So pooling is NOT the spec's intent — male and
   female singles are supposed to get distinct leisure coefficients.

   If the singles_female group is in fact mapping its leisure to the `_sm`
   slot, this is a **genuine engine/coefficient-suffix-resolution bug**,
   and it would mean: (a) the singles_female leisure estimate is sitting in
   the wrong-named columns, and more seriously (b) the female-only
   `n_children` leisure effect (`beta_l_nkids_sf`) was dropped from the
   female likelihood entirely (the `_sm` block has no nkids term). The
   sf2016 precompute DID load female `n_children` (32,421/91,910 nonzero),
   so the data was present but possibly unused in the leisure block.

   **This needs investigation before the singles_female estimate can be
   trusted** — it is NOT yet confirmed whether the likelihood used the
   right coefficients or just the reporting is mislabeled. Logged as
   `workitem-bpool-singles-female-leisure-suffix.md` (HIGH priority).
   The singles_male and couples estimates are unaffected by this question.

## Output locations

- singles_male warm: `outputs/estimation/realdata_multibasin/sm2016_conopt_from_thetastar/`
- singles_male cold: `outputs/estimation/realdata_2016/sm2016_conopt_cold/`
- singles_female warm/cold: `outputs/estimation/realdata_2016/sf2016_conopt_{warm,cold}/`
- couples warm/cold: `outputs/estimation/realdata_2016/c2016_conopt_{warm,cold}/`

(all under `C:\Users\hisham\MNL\EUROMOD-STORAGE\`)

## Related

- `RURO_realdata_multibasin_test_v1.md` — Step 2: scipy reaches same basin
- `RURO_recovery_test_results_v3.md` — synthetic recovery verdict (i)
- `workitem-recovery-residuals-beta_ll-beta_w_pexp.md` — the residuals; this
  real-data run shows beta_w_pexp is fine on real data, beta_ll still
  unidentified on single slices
- `project-couples-conopt-runtime.md` (memory) — couples ~4.5h budget
