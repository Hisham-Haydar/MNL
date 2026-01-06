# Plan: Fix Missing Couples Predicted Hours/Participation in Post-Estimation

## Suspected cause
- `compute_fit_diagnostics` for couples is called with `hours_col='hours_male'` and `hours_col='hours_female'`, but `DynamicUtilityComputer._get_leisure` only looks for `leisure_m/leisure_f`, `hours_m/hours_f`, `lhw_m/lhw_f`, generic `hours/lhw`. If the MNL data is wide with `hours_male/hours_female`, leisure defaults to 1.0, leading to incorrect utilities and `NaN`/zero predicted stats, which then show as blank in the HTML for couples while singles work.

## Inspection steps
1) Check the couples MNL file columns (e.g., `hours_male`, `hours_female`, `is_chosen`, `idhh`, `idhh_true`, `draw`) to confirm naming.
2) Inspect a recent `fit_results` snippet in logs or by re-running `compute_fit_diagnostics` to see if couples predicted stats are `NaN`/zero.
3) Verify parameter names for couples in `fr_2016_joint.json` to ensure they map to group `cou` as expected.

## Code changes (ordered)
1) **Leisure/hour extraction**
   - Extend `_get_leisure` to recognize `hours_male/hours_female` (and `lhw_male/lhw_female`) in addition to existing fallbacks.
   - Optionally allow passing an explicit `hours_col` into `_get_leisure` from `compute_fit_diagnostics` for couples to ensure alignment.
2) **Couples fit diagnostics**
   - In `compute_fit_diagnostics`, when `is_couples=True`, accept both male and female hours columns, or call twice with explicit leisure inputs to match the hours column being evaluated.
   - Add defensive logging if hours column is missing, or if predicted stats stay `NaN/0`, to surface issues in logs.
3) **Utility computation**
   - Ensure `compute_utility_couples` uses the same hours columns as `compute_fit_diagnostics` (possibly by parameterizing the leisure column names per sex, defaulting to detected hours columns).
4) **HTML/plot robustness**
   - Guard fit table/plots to display `0` vs `N/A` consistently and warn when predicted stats are missing for a group.

## Validation
1) Re-run post-estimation on the 2016 joint output and inspect `fit_results` for `cou_m`/`cou_f` (non-NaN predicted participation/mean hours).
2) Regenerate the HTML report (`outputs/post_estimation/fr/2016/joint/*post_estimation_report.html`) and confirm couples’ predicted values and plots appear.
3) Spot-check participation/mean-hours plots (`fit_participation.png`, `fit_mean_hours.png`) to ensure couples bars are populated.
