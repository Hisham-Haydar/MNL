ROLE

Implement and execute only Phases 1 and 2 of the FR-2016 singles P2a region-live production rebuild.

Do not run Phase 3.
Do not optimize.
Do not estimate.
Do not run EUROMOD.
Do not regenerate draws.
Do not run inference.
Do not run post-estimation.
Do not run welfare.

BINDING DOCUMENTS

Read in full:

* MNL/docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md
* MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md
* MNL/docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md
* Job_Market_paper/docs/JMP_cross_repo_manager_handoff_v1.md
* Job_Market_paper/docs/JMP_cross_repo_artifact_manifest_v1.md
* MNL/dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md
* MNL/dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb

NOTEBOOK STATUS

* fr_singles_pipeline_v1.ipynb is the frozen region-live reference checkpoint.
* fr_singles_pipeline_v2.ipynb is the active interactive-development notebook.
* Neither notebook is a production certification artifact.
* Do not execute or modify either notebook.

CREATE

1. MNL/scripts/p2a/run_p2a_regionlive_rebuild.py
2. MNL/scripts/p2a/verify_p2a_regionlive_reload.py
3. MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
4. MNL/docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v1.md

WRITE OUTPUTS ONLY UNDER

MNL/outputs/p2a_singles2016/region_live_v1/

Do not write elsewhere.

PHASE 1 — RECONSTRUCT er_b

Use the exact frozen, already-priced upstream P2a draw artifacts identified in the canonical v2 plan.

Do not use an existing engine-ready frame as construction input.

Reconstruct:

frozen priced draws
→ assemble_singles
→ independent region/urbanisation/GSUR revival
→ B-pool band overwrite
→ er_b

Authoritative live-variable sources:

* FR_2016_a3.txt:
  drgn1, drgur, drgmd, drgru

* FR_gsur_ruro_v2_stageA_y2015.parquet:
  gsur, merged using the canonical keys

Validate:

* exactly 1,555 households;
* unique and complete idhh mapping;
* no missing or duplicate households;
* drgn1 support 1–8;
* exactly one urbanisation category per household;
* GSUR in the declared range and nonconstant;
* within-household constancy;
* no cross-household leakage;
* 101 alternatives per household;
* row count and choice geometry unchanged;
* chosen indicators unchanged;
* hours, wages, consumption, leisure, occupation and proposal quantities unchanged relative to reconciliation frames;
* stable sorting, aligned columns and normalized dtypes;
* all declared comparison frames reconciled.

Any substantive discrepancy must:

* write partial evidence;
* mark rebuild_manifest.json as STOPPED;
* stop under S-1.

PHASE-1 OUTPUTS

* region_map_p2a_singles2016.parquet
* data_wiring_validation.json
* fr_p2a_singles2016_regionlive__singles.parquet
* fr_p2a_singles2016_regionlive__mnlmeta.json
* input and output SHA-256 hashes
* rebuild_manifest.json with status PHASE_1_COMPLETE or STOPPED

PHASE 2 — PACKAGE LOAD AND OBJECTIVE REPRODUCTION

Load the frozen stem using dclaborsupply package APIs.

Verify:

* certified YAML remains unchanged;
* P2a run overlay has exactly 10 pins;
* 37 run-level parameters remain free;
* names, positions and bounds are explicit;
* structural wage_spec is plain vw;
* loc_empirical is not active structurally;
* vw_occupation is not active structurally;
* occupation-conditioned proposal information enters through prior/log_prior;
* structural occupation enters through loc4 access terms;
* region and GSUR arrays loaded for JAX are nonzero;
* loaded arrays equal the frozen columns;
* prior is positive;
* log_prior equals log(prior);
* proposal correction is applied exactly once;
* proposal-weighted centering is active;
* unique nonmissing idorighh count is measured and persisted;
* every household has exactly one cluster ID;
* cluster count is between 1 and 1,555.

OBJECTIVE CHECK — NO OPTIMIZER

Load the existing stored region-live theta.

Before objective evaluation, verify:

* parameter ordering;
* all 10 run pins;
* spec-level fixings;
* theta hash;
* no bound or parameter mutation.

Evaluate without optimization:

* JAX negLL must reproduce 19053.46553160094 within 1e-4;
* NumPy negLL must agree with JAX within 1e-6.

A materially higher or lower objective is a STOP condition.

The verify script must be executable in a fresh process, but this dry-run is a pre-estimation reload check, not the final post-estimation strict cold-reload gate.

RUNNER CONTRACT

The runner must support:

* --config
* --phase
* --out
* --dry-run

The dry-run must stop after Phase 2.

Use package APIs for:

* spec parsing;
* engine-ready loading;
* JAX likelihood;
* NumPy likelihood.

Do not duplicate likelihood mathematics.

Do not modify:

* either notebook;
* any file in dclaborsupply-monorepo;
* any file in Job_Market_paper;
* the certified YAML;
* certified pooled theta/results;
* root P2a theta files;
* root P2a provenance;
* root P2a parquets;
* anything outside region_live_v1.

EXECUTE

Parse the YAML.
Compile/import both scripts.
Run:

python MNL/scripts/p2a/run_p2a_regionlive_rebuild.py 
--config MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml 
--phase 2 
--out MNL/outputs/p2a_singles2016/region_live_v1 
--dry-run

Do not proceed beyond Phase 2.

DRY-RUN REPORT HEADINGS

1. Dry-run verdict
2. Files created
3. Authoritative inputs
4. Frozen priced-draw inputs
5. Existing-frame reconciliation
6. Household mapping validation
7. Region support
8. Urbanisation validation
9. GSUR validation
10. Choice-geometry invariance
11. Proposal-density invariance
12. Frozen stem
13. Specification and pin binding
14. JAX loader liveness
15. Wage and occupation route
16. Proposal-correction checks
17. JAX objective reproduction
18. NumPy/JAX agreement
19. Resolved cluster count
20. Hashes and provenance
21. Stop-condition status
22. Git diff summary
23. Whether Phase 3 may run
24. Immediate next action

FINAL VERDICT

Use one:

* PASS
* PASS WITH WARNINGS
* STOPPED

Do not commit automatically.
Show git diffs and stop.
