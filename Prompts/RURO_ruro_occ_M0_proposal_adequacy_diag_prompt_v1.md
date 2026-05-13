# Claude Code prompt — RURO `ruro_occ_M0` proposal-adequacy diagnostic

Date: 2026-05-13

Purpose: distinguish whether the identification failures of
`ruro_occ_M0` (Hessian indefinite; `β_c_sf`, `θ_c_sf` NA SE;
participation = 1.0000 across all groups) are caused by
over-parameterisation of the spec, by inadequate within-choice-set
variation in the proposal draws, or by both. The diagnostic is
**read-only against the existing parquet files** and does not touch
the estimator, the post-estimator, or the data rebuild pipeline.

**Save the prompt below as a file** in your workspace (suggested:
`prompts/RURO_ruro_occ_M0_proposal_adequacy_diag_prompt_v1.md`), then
paste into Claude Code with the two parquet paths attached.

---

## Prompt to paste into Claude Code

```text
You are auditing the France 2016 RURO continuous-branch MNL parquet
files to determine whether the proposal/draws design produces enough
within-household variation to identify the M0 preference parameters.

INPUT FILES (read-only, do not modify):
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet

If those paths are unreachable from the working environment, try:
- \\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet
- ...\fr_2016_RURO_mnl__couples.parquet

REFERENCE SPEC (read-only, do not modify):
- scripts/enhanced/estimation_spec_ruro_occ_M0.yaml

GOAL: produce a single short Markdown report at
Results/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md that answers two
diagnostic questions, with one quantitative verdict at the end.

GROUP DEFINITIONS (use these throughout):
- singles parquet, split by column `dgn`: dgn == 1 -> singles_male;
  dgn == 0 -> singles_female. Confirm dgn exists; if not, search for
  the gender column ('sex', 'female', 'male', 'gender') and document
  which column was used.
- couples parquet: each row is one household-alternative; the
  partner-suffixed columns supply male/female views. Use
  `working_male`, `consumption`, `leisure_male`, `hours_male`,
  `loc4_male` for couples_male; `_female` variants for couples_female.
- Household ID column: `idhh` (confirm; alternatives: `idhh_true`,
  `hh_id`).
- Alternative ID within household: every household must have exactly
  100 rows. Use the chosen-row indicator `is_chosen` (or `chosen`) to
  identify the observed alternative.

CONSUMPTION COLUMN DISCOVERY:
The contract says C is built from EUROMOD ils_dispy and then
normalised. The most likely column name is `consumption`. If absent,
try in this order: `consumption`, `c_norm`, `C`, `ils_dispy`,
`ils_dispy_em`. Print and log the column found. Do not silently fall
back; if no candidate exists, FAIL with a clear message naming all
present numeric columns whose name contains 'cons', 'disp', 'inc', or
'C'.

LEISURE COLUMN DISCOVERY:
Singles: `leisure` (or `L`, `l_norm`, `leisure_norm`).
Couples: `leisure_male`, `leisure_female` (with same fallbacks).

WORKING INDICATOR:
Singles: `working`. If missing, derive as `(hours > 0).astype(int)`
with `hours` looked up from `hours`, `lhw`, or `h`.
Couples: `working_male`, `working_female`, with same fallback to
`hours_{male,female} > 0`.

------------------------------------------------------------------
D1 — WITHIN-HOUSEHOLD VARIATION IN CONSUMPTION AND LEISURE
------------------------------------------------------------------

The identification of (beta_c, theta_c) in a Box-Cox model depends on
the variance of BC(C, theta_c) WITHIN each household's choice set. The
identification of (beta_l0, theta_l) depends on the variance of
BC(L, theta_l) WITHIN. If within-hh variation is small relative to
between-hh variation, the consumption/leisure block is identified only
from cross-hh variation, which is much weaker.

For each of the four groups (singles_male, singles_female,
couples_male, couples_female):

D1a. RAW CONSUMPTION VARIATION:
  - Compute per-household statistics on the 100 alternatives:
    std(C), max(C) - min(C), and mean(C).
  - Report quantiles across households: q10, q25, q50, q75, q90 of
    each of these three statistics.
  - Compute cross-hh std of mean(C) (the between-hh dispersion).
  - Report the identification ratio: median over hh of [std(C) within
    hh] divided by [cross-hh std of mean(C)]. Call this `R_C_raw`.

D1b. BOX-COX-TRANSFORMED CONSUMPTION VARIATION at the M0 anchor:
  For each of theta in {-1.0, -0.5, 0.0, 0.215, 0.5}:
    - The first four cover the M0 estimated singles theta_c_sf =
      -1.09, theta_c_sm = -0.86, and couples theta_c = 0.215, plus a
      neutral 0.0. The 0.5 is a sanity reference.
    - For C > 0, compute BC(C, theta) = (C^theta - 1) / theta if
      theta != 0, else log(C). Clip C >= 1e-6 before transform.
    - For each hh compute std(BC(C, theta)) within choice set.
    - Report median, q25, q75 across hh of that within-hh std.
    - Compute cross-hh std of mean BC(C, theta).
    - Report `R_BC_C(theta) = median_hh[within_std] / between_std`.

  Interpretation:
    - R_BC_C(theta) > 0.3 -> within-hh variation is substantial at
      this theta; the BC coefficient is identifiable.
    - R_BC_C(theta) in [0.1, 0.3] -> marginal identification.
    - R_BC_C(theta) < 0.1 -> within-hh variation is too small to
      identify theta_c at this curvature; the parameter is identified
      almost entirely from cross-hh variation.

D1c. LEISURE VARIATION (same logic on L):
  Theta grid: {-1.0, -0.7, -0.5, 0.0} (M0 estimated theta_l_g around
  -0.70 to -0.73 across groups).
  Report R_L_raw and R_BC_L(theta) per group.

D1d. JOINT (C, L) VARIATION:
  For each hh, compute the rank correlation of C and L across the 100
  alternatives. Report the median rank correlation per group. If the
  median is below -0.85, C and L are nearly collinear within choice
  sets, which means the model cannot separate the consumption and
  leisure margins.

------------------------------------------------------------------
D2 — NON-EMPLOYMENT MASS IN THE PROPOSAL
------------------------------------------------------------------

The beta_E parameter (market vs non-market log-odds) is identified
from the contrast between working and non-working alternatives within
a household's choice set. If the proposal draws very few non-work
alternatives per hh, beta_E is identified off a thin slice.

For each of the four groups:

D2a. NON-WORK SHARE PER HOUSEHOLD:
  - For each hh, compute share_nonwork = sum(working == 0) / 100.
  - Report quantiles across hh: q10, q25, q50, q75, q90.
  - Report the fraction of hh with share_nonwork < 0.05 (called
    "thin non-work"), < 0.01 ("very thin"), and exactly == 0
    ("absent non-work").

D2b. NON-WORK SHARE OF CHOSEN ALTERNATIVES:
  - Among the chosen alternative (1 per hh), report the fraction
    with working == 0 (this is observed non-employment rate).
  - Compare to the per-hh share_nonwork median from D2a. If chosen
    non-employment is 5-10 percent but median per-hh share_nonwork in
    the proposal is also 5-10 percent, the proposal is mass-matched.
    If chosen is 7 percent but median proposal share is 1 percent,
    the proposal undersamples non-employment relative to observed.

D2c. PRIOR DENSITY ON NON-WORK ALTERNATIVES:
  - For each group, compute the mean of `log_q_E` on rows where
    working == 0 (singles) or working_partner == 0 (couples) and on
    rows where working == 1. Report both. A heavily skewed
    proposal will show large absolute mean differences.

------------------------------------------------------------------
OUTPUT FORMAT
------------------------------------------------------------------

Write the report to Results/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md
in the following structure (use Markdown tables; do NOT include plots):

# RURO ruro_occ_M0 — Proposal-Adequacy Diagnostic v1

Date: <YYYY-MM-DD>

## Verdict

One of:
- PASS: within-hh variation in C, L, and non-work mass is sufficient
  to identify the M0 spec at the anchor theta values. The M0
  identification failure is over-parameterisation; M0a (drop 5 params)
  is the right fix.
- FLAG: within-hh variation is marginal in one or more dimensions.
  M0a will help but the proposal design may also need attention.
  Recommend running M0a first and re-evaluating.
- FAIL: within-hh variation is too small to identify (beta_c,
  theta_c), (beta_l0, theta_l), or beta_E. The proposal/draws need
  redesign before any spec-level repair will hold. M0a is unlikely
  to fix the indefinite Hessian.

Brief 3-5 sentence rationale citing the worst R_BC_C(theta) and
share_nonwork numbers.

## Input files

(table with absolute paths, file sizes, last-modified timestamps,
n rows, n columns, n households)

## Column resolution

(table of what column name was used for: consumption, leisure,
working indicator, household ID, chosen indicator, gender; per
parquet file)

## D1 — Consumption and leisure variation

### D1a Raw consumption (per group, quantiles)

| group | within_hh_std q10 | q25 | q50 | q75 | q90 | between_hh_std | R_C_raw |
...

### D1b BC-transformed consumption (per group, per theta)

| group | theta | within_hh_std q25 | q50 | q75 | between_hh_std | R_BC_C |
...

### D1c Leisure (analogous structure)

### D1d Median within-hh rank-correlation(C, L) per group

| group | median rank corr | q10 | q90 |
...

## D2 — Non-employment mass

### D2a Share of non-work alternatives per household

| group | q10 | q25 | q50 | q75 | q90 | pct hh share < 5% | pct < 1% | pct == 0 |
...

### D2b Observed (chosen) non-employment rate vs proposal median

| group | obs non-employment rate | proposal median share | gap |
...

### D2c Mean log_q_E on work vs non-work

| group | mean log_q_E | working | non-work | difference |
...

## Diagnostic summary

A 5-10 line interpretation that translates the numbers into the
verdict. Reference the specific thresholds (R_BC_C < 0.1 = FAIL,
share_nonwork < 5% at median = FLAG, etc.) so the verdict is
auditable.

## Files produced

| file | purpose |
| Results/_proposal_adequacy_diag_ruro_occ_M0.py | reusable script |
| Results/_proposal_adequacy_diag_ruro_occ_M0.json | machine-readable results |
| Results/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md | this report |

------------------------------------------------------------------
TECHNICAL REQUIREMENTS
------------------------------------------------------------------

- Use pandas + numpy only. No estimator, no GAMSPy, no EUROMOD.
- Read-only on the parquet files. Do not write to the parquet
  directory.
- The script must run in under 5 minutes on a 16 GB machine.
- Save the script to Results/_proposal_adequacy_diag_ruro_occ_M0.py
  so it can be re-run after the next data rebuild.
- Save a machine-readable Results/_proposal_adequacy_diag_ruro_occ_M0.json
  with the same numbers, for later automated comparison.
- The Markdown report must be at most 200 lines and must not embed
  plots or large tables (one row per group per theta is fine).
- Use unweighted statistics; flag in the report that the EUROMOD hh
  weight dwt is not applied (this is a diagnostic, not a population
  estimate).
- Box-Cox safety: clip C, L >= 1e-6 before transforming. If any group
  has C or L of zero or negative, log a warning and proceed with
  clipped values.
- If a column is missing, report it clearly in the column-resolution
  table and continue with the remaining diagnostics if possible.
  Don't abort the whole script on one missing column.
- Print progress to stdout as the script runs (one line per group per
  diagnostic) so it's visible in the Claude Code terminal.

DO NOT:
- Modify the parquet files.
- Modify the YAML.
- Re-run the estimator.
- Run any computation that depends on the M0 estimated theta vector
  (other than using the theta grid above as anchor values).
- Make recommendations about M0a or the welfare layer. The verdict
  is purely about proposal adequacy.

After the report is written, do not proceed to any further task.
Confirm the file paths of the three outputs and stop.
```

---

## What to do with the report once you have it

When Claude Code returns the report, the verdict at the top tells you the
direction:

- **PASS** → M0a as designed is the right next move. Skip the
  participation diagnostic for now (M0a will surface the same evidence)
  and proceed directly to creating
  `estimation_spec_ruro_occ_M0a.yaml`.
- **FLAG** → M0a is still worth running, but plan to re-evaluate the
  proposal after M0a. Specifically, watch whether `R_BC_C(theta_c
  at M0a optimum)` improves once `theta_c` is pooled across singles.
- **FAIL** → stop. M0a will not fix the indefinite Hessian. The next
  step is **not** estimation but a draws-side redesign — widening the
  `q_W` (wage) or `q_H` (hours) proposal so the within-household range
  of C spans more of the empirical range. That is a Step-1 (draws)
  change in `enh_RURO_draws.py`, not a Step-7 (estimation) change.

Either way, save the report verdict alongside the M0a design memo
before re-estimating.

## Suggested filename for the prompt itself

Save this prompt as:
`prompts/RURO_ruro_occ_M0_proposal_adequacy_diag_prompt_v1.md`
(category: coding prompt).
