# MNL Project Memory

## Key Architecture

- Estimation engine: `scripts/enhanced/estimation_engine.py` (numpy gradient), `gamspy_estimation_vectorized.py` (GAMSPy solver)
- Main script: `scripts/enhanced/enh_RURO_estimate_FR.py`
- Post-estimation: `scripts/enhanced/RURO_post_estimation_styled.py`
- Spec parser: `scripts/enhanced/estimation_spec_parser.py`
- Utils (precompute): `scripts/enhanced/estimation_utils.py`

## Running Estimation

- Use `.venv` Python: `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`
- Data on Z: drive: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm`
- Must use PowerShell (not cmd/bash) for UNC paths; use `$var` for UNC strings
- Use `--solver gamspy-conopt --vectorized` for GAMSPy estimation

## Bug Fixes Applied (Feb 2026)

1. **SE=0 for market opportunity params**: Root cause was `logger` not defined at module level in estimation_engine.py + missing `include_extra_vars` in post-estimation precompute. Fixed in both estimation_engine.py and RURO_post_estimation_styled.py.
2. **Diagnostic logging added**: estimation_utils.py now logs which extra vars were derived successfully/failed.
3. **Validation added**: enh_RURO_estimate_FR.py Section 5b validates all market opportunity variables exist on data objects.
4. **M2c catastrophic failure (Feb 19)**: TWO bugs: (a) Leisure shifter variables (age_norm, age_norm2, n_children) were NOT extracted to extra_precompute_vars. Fixed in enh_RURO_estimate_FR.py lines 1230-1236. (b) Household-level n_children column missing for couples (only n_children_male/female existed). Fixed in enh_RURO_prep_mnl_basic.py lines 868-871.

## Market Opportunity Shifters

- Fully generic: any variable × any interactions supported
- Interaction list is multiplied sequentially: `var × int1 × int2 × ...`
- Couples use gender-specific variants: `var_male`, `var_female`
- Extra vars from shifter interactions auto-extracted to `extra_precompute_vars`

## Specification Files

- `estimation_spec_job_M2.yaml`: 23 params, occupation_base=1, 3-way isco1 interactions
- `estimation_spec_job_M2b.yaml`: 26 params, occupation_base=0, 2-way isco1 + education interactions
- `estimation_spec_job_M2c.yaml`: 41 params, M2b + leisure shifters (age, age², children, educH). First run FAILED due to bug #4 above.

## EUROMOD Variable Reference (always check before pipeline questions)

- [reference_euromod_fr_docs.md](reference_euromod_fr_docs.md) — authoritative FR_2015/2016/2017 input & output variable docs; read before answering any question about column existence, income concepts, or data at any pipeline stage
- [reference_drd_fr_input_variables.md](reference_drd_fr_input_variables.md) — FR DRD pre-exported to plain text at `EUROMOD-STORAGE/Data/FR/drd/DRD_FR_{year}_*_export.txt` (2007-2023); grep these first for `les` codes, `yem`/`yem00`/`yemxp`/`yivwg` definitions, monthly periodicity, and the Stata derivation of every input variable
- [project_fr2016_microdata.md](project_fr2016_microdata.md) — `FR_2016.txt` is real EU-SILC (26,560 ind), not training data, despite EUROMOD logging "dataset FR_training_data"

## B-pool Chosen-Row Semantics (read before claiming a build bug)

- [feedback_bpool_chosen_row_is_reconstructed.md](feedback_bpool_chosen_row_is_reconstructed.md) — chosen-row `yem` is reconstructed as `lhw × yivwg × 52/12` (≈ `yem00`), not copied from survey `yem`. The gap to survey `yem` is documented Layer-1 divergence (overtime/bonuses absent).
- [feedback_bpool_les_vs_yem_flips_are_structural.md](feedback_bpool_les_vs_yem_flips_are_structural.md) — the ~1.5% (280/18,283) chosen-row participation flips are 100% explained by `les` vs `yem` survey disagreement (A1: employees w/ zero recorded earnings; A2: unemployed/inactive w/ residual earnings). Not a bug.

## Package Naming (always use)

- [feedback_naming_policy_ruro.md](feedback_naming_policy_ruro.md) — use "RURO" / `ruro_occ_M0`; do not say "Stijn-style" in package-facing code, specs, or reports. Personal acknowledgement lives only in `docs/ACKNOWLEDGEMENTS.md`. Historical artefact paths under `stijn_occ/`, `fr_2016_stijn_occ_*`, `stijn/*.Rmd` are preserved for provenance.

## Stage M1 Status

- [project_stage_m1_status.md](project_stage_m1_status.md) — P3a full construction COMPLETE 2026-05-20: 1,244,500 rows (singles+couples, 3 years), V1–V9 PASS, report v1

## Data Available (81 cols in parquet)

- Education: `educL`, `educM`, `educH` (dummies), `educ3`, `deh`
- Experience: `pexp_years`, `pexp_years2`
- Age: `age_norm`, `age_norm2`, `dag`
- Region: `reg_nuts1_1` through `reg_nuts1_8`
- 974 columns available in upstream data if more needed (modify prep script)
