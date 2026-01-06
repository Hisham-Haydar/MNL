# RURO Python Enrichment Plan (France)

## Goals
- Bring `scripts/RURO_estimate_FR.py` closer to the richer R specification while keeping current performance optimizations.
- Add France-specific region effects using `drgn1` (Île-de-France as reference, dummies for other regions).
- Preserve joint estimation workflow and post-estimation outputs.

## Data Mapping
- Consumption/leisure normalization: allow reading dataset means (disposable income, leisure hours) instead of fixed constants.
- Age: switch from demeaned age to `log(age)` and `log(age)^2` (align with R).
- Children: add buckets `children0_3`, `children4_6`, `children7_9` (keep total children if useful for pooled runs).
- Education: keep `educL`, `educH` as in current code.
- Regions: derive region dummies from `drgn1` with reference `drgn1 == 1` (Île-de-France); create `region_rX` for other values present in the data (check unique values first).
- Year: add year dummies if multi-year estimation is needed.

## Code Changes (ordered)
1) **Parameter layouts/names**
   - Expand singles/couples/joint parameter vectors to include child buckets, region effects, year dummies.
   - Update helper functions: `get_param_names_*`, `get_initial_theta_*`, joint index mapping.

2) **Precompute structures**
   - Extend `PrecomputedDataSingles`/`PrecomputedDataCouples` to carry: `log_age`, `log_age2`, child buckets, region dummies, year dummies.
   - Keep contiguous `float64` arrays; guard against missing columns.

3) **Utility functions**
   - Modify `fast_log_likelihood_singles` and couples variants to use Box-Cox leisure with log-age terms, child buckets, education, region effects; add Box-Cox-based leisure–leisure interaction for couples.
   - Adjust consumption scaling to use passed normalization constants; allow override via CLI.

4) **Hours opportunity (HOPP)**
   - Add region-by-working terms (`working * region_rX`) and keep PT1/PT2/FT peaks, gsur, education interactions.
   - Ensure couples have sex-specific blocks with the new region terms.

5) **Wage opportunity (WOPP)**
   - Extend mean log-wage to include region dummies and optional year dummies; keep experience terms and sex-specific sigmas.
   - For fixed-wage runs, keep wage part zeroed but parameter mapping consistent.

6) **CLI/config**
   - Add flags for normalization constants and toggles for region/year effects.
   - Validate gradient option after expansion (analytical vs numerical spot checks).

7) **Joint estimation path**
   - Update joint parameter slicing/mapping to include the new parameters for SM/SF/COU.
   - Ensure joblib/Numba paths still use the expanded structures.

8) **Testing/validation**
   - Run a small-sample LL/grad check (numerical vs analytical) after changes.
   - Re-run a France 2016 joint estimation; monitor gradient norms and LL.
   - Verify post-estimation outputs regenerate (HTML/JSON) with new parameters.

## Region Notes (France)
- `drgn1 == 1` → Île-de-France (reference).
- Create dummies for other `drgn1` values observed (e.g., 2–8) and apply consistently in utility, HOPP, and WOPP components.

## Open Questions
- Do we need separate region effects for preferences vs opportunities, or share one set?
- Should male preferences also load child effects (R only applies to female; decide for France)?
- Do we keep both total-children and bucketed-children terms for flexibility?
