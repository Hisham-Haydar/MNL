ROLE

Add the controlled production-geometry freeze operation to the active FR-2016 singles P2a development notebook.

This is a notebook-editing and validation task only.

Do not execute the notebook.
Do not run EUROMOD.
Do not run estimation.
Do not run inference.
Do not run post-estimation.
Do not run welfare.
Do not modify fr_singles_pipeline_v1.ipynb.
Do not modify scientific scripts, specifications, theta files, data, or existing outputs.

READ IN FULL

* MNL/dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb
* MNL/docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md
* MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md
* MNL/docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md
* MNL/docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v1.md
* MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
* MNL/scripts/p2a/run_p2a_regionlive_rebuild.py

CURRENT BLOCKER

The Phase 1–2 dry run stopped correctly at G-0 because these frozen-input artifacts do not exist:

* MNL/outputs/p2a_singles2016/region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet
* MNL/outputs/p2a_singles2016/region_live_v1/inputs/fr_p2a_draws_geometry__meta.json

The in-memory draws_p2a object is created in the notebook's P2a draw-generation cell but is not persisted.

MODIFY ONLY

1. MNL/dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb
2. MNL/docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md

Use Python nbformat. Do not edit raw notebook JSON manually.

CONTROL FLAG

Add to the top-level controls:

EXPORT_PRODUCTION_GEOMETRY = False

This must default to False.

GEOMETRY-FREEZE CELL

Insert one code cell immediately after the cell that constructs draws_p2a and completes all its draw-generation gates, and before pricing.

When EXPORT_PRODUCTION_GEOMETRY is False:

* write nothing;
* print:
  [SKIPPED: EXPORT_PRODUCTION_GEOMETRY=False] production geometry freeze not run.

When EXPORT_PRODUCTION_GEOMETRY is True:

1. Require draws_p2a to exist.
2. Load the geometry contract from:
   MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
3. Preserve the complete in-memory draws_p2a column set. Do not select only the required columns.
4. Canonically sort using stable mergesort by:

   * idhh
   * draw
5. Reset the row index.
6. Validate:

   * 157,055 rows;
   * 1,555 households;
   * exactly 101 alternatives per household;
   * all required columns from frozen_inputs.draws_geometry.required_columns exist;
   * exactly one draw==0 row per household;
   * chosen rows have is_chosen==1;
   * chosen rows have log_prior==0;
   * no duplicate (idhh, draw);
   * seed is 2026;
   * prior is positive;
   * log_prior is finite;
   * log_prior equals:
     log_q_E + working * (log_q_H + log_q_W + log_q_Occ)
     within exact floating-point equality used by the existing notebook gate.
7. Write only to:
   MNL/outputs/p2a_singles2016/region_live_v1/inputs/
8. Produce:

   * fr_p2a_draws_geometry__singles.parquet
   * fr_p2a_draws_geometry__meta.json
9. Use an atomic write:

   * write a temporary parquet;
   * hash the completed temporary file with SHA-256;
   * atomically replace the final parquet only after all checks pass.
10. Metadata JSON must include at least:

    * status: frozen_production_input
    * produced_by: notebooks/fr_singles_pipeline_v2.ipynb
    * seed: 2026
    * draw_design
    * sha256
    * n_rows
    * n_households
    * alternatives_per_household
    * n_columns
    * columns
    * dtypes
    * required_columns
    * created_at_utc
    * manager_decisions document
    * production_plan document
11. Existing-file rule:

    * if neither output exists, create both;
    * if both exist and the existing parquet hash agrees with its metadata and its contents satisfy the same contract, print that the geometry is already frozen and do not rewrite it;
    * if only one exists, or the existing files fail their contract, raise an error and do not overwrite either.
12. Do not write any other production artifact.
13. Do not copy or derive the geometry from an engine-ready parquet.
14. Do not invoke any draw-generation function inside the freeze cell; it freezes the already-created in-memory draws_p2a only.

OUTPUT-ISOLATION DOCUMENTATION

Update the notebook banner/addendum to state:

* ordinary notebook outputs remain under notebook_dev_v2;
* the sole authorized production-output exception is the explicit, operator-gated immutable geometry freeze under region_live_v1/inputs;
* this exception requires EXPORT_PRODUCTION_GEOMETRY=True;
* it does not authorize estimation, inference, post-estimation, or welfare writes to region_live_v1.

VALIDATION WITHOUT EXECUTION

* Confirm v1 hash is unchanged.
* Parse v2 with nbformat.
* AST-compile every code cell.
* Confirm all execution counts are None and outputs empty.
* Confirm EXPORT_PRODUCTION_GEOMETRY exists and defaults False.
* Confirm exactly one cell writes to region_live_v1/inputs.
* Confirm no other v2 cell writes anywhere under region_live_v1.
* Confirm the freeze cell cannot run when the flag is False.
* Confirm the notebook still contains all five previous run flags defaulting False.
* Show git diff summaries.

Do not execute the notebook.
Do not commit automatically.
Stop after validation.
