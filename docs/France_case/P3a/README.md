# France_case/P3a/ — 3-year stacked 2015-2016-2017 estimation

The P3a track is the current main estimation effort: stack France RURO data from EUROMOD survey years 2015, 2016, and 2017 (with their corresponding opportunity years y2014, y2015, y2016) into a pooled dataset, then estimate a single RURO specification on the pooled data.

P3a is the **active baseline** as of 2026-05.

## Subfolders

- **`design/`** — design memos, spec contracts, next-cycle plans:
  - `FR2016_RURO_pipeline_report.md` — foundational narrative of the single-year FR_2016 RURO pipeline (predates P3a but is the basis for it)
  - `RURO_ruro_occ_baseline_spec_v1.md`, `..._baseline_implementation_report_v1.md` — first feasible continuous RURO baseline with occupation opportunity (M0)
  - `RURO_ruro_occ_M0_rebuild_command_plan_v1.md`, `..._M0_file_sync_check_v1.md`, `..._post_estimation_report_fix_v1.md` — M0 ladder work
  - `JMP_pooled_P3a_estimation_design_memo_v1.md` — pooled P3a design
  - `JMP_next_cycle_opportunity_respecification_plan_v1.md` — next-cycle opportunity respecification

- **`execution_logs/`** — dated run reports + amendments, organized by track stage:
  - `single_year_baseline/{M0a-clean,M0b,M0c,M1}/` — single-year FR_2016 baseline ladder (M0 → M1) that defines the structural specification P3a stacks
  - `multi_year_stage_M1/` — Stage M1 data-engineering layer (stack years, harmonise CPI, identity validation)
  - `pooled_P3a/` — pooled estimation runs
  - `GSURv2/` — GSURv2 build (group-specific unemployment rate, multi-year extension)
  - `Bpool/` — B-pool schema diff and precompute gate

- **`canary_reports/`** — canary checks before estimation runs

- **`consolidated/`** — merged canonical docs from Round 1 + cross-track verification:
  - `JMP_multi_year_2015_2017_consolidated_v1.md`
  - `RURO_GSUR_rebuild_consolidated_v1.md`
  - `RURO_pilot_gsurv2_verification_v1.md` (cross-track: verifies GSURv2 merge AND NC pilot spec structure; see also [`../NC_pilot/README.md`](../NC_pilot/README.md))

## Sibling tracks

- [`../NC_pilot/`](../NC_pilot/) — active couples 30×30=900 alternatives pilot
- [`../job_model/`](../job_model/) — archived (replaced by P3a + NC)
- [`../_shared/`](../_shared/) — cross-track material (EUROMOD ref, GSUR, data audits, governance decisions)
