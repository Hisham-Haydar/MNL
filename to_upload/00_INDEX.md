# JMP Endgame — Upload Bundle Index

30 documents copied from the repo docs tree, grouped by phase. Original repo paths in parentheses.
Generated 2026-07-09 from the JMP endgame documentation triage.

## P1 — Post-estimation report + SEs (trial)
- RURO_certified_styled_report_pointer_v1.md — canonical styled report location + provenance (docs/jmp_methodology/)
- RURO_realdata_2016_postestimation_v1.md — MUC/MUL well-behavedness criteria + certified diagnostics (docs/France_case/P3a/execution_logs/Bpool/)
- RURO_postestimation_descriptives_v1.md — descriptives + opportunity-set readout (docs/jmp_methodology/)
- RURO_cluster_robust_SE_implementation_report_v1.md — clustered/robust SE method (docs/estimation/)
- RURO_cluster_robust_SE_design_audit_v1.md — SE design rationale + pitfalls (docs/estimation/)

## P2 — Paper run (pooled 2015-17, occ-sampled, couples, LR)
- RURO_realdata_2016_2017_joint_901_v1.md — certified anchor provenance, 901 joint pooled run (docs/France_case/P3a/execution_logs/Bpool/)
- RURO_jax_recovery_gate_tlmpin_901_v1.md — synthetic identification gate PASS, tlmpin 901 (docs/France_case/P3a/execution_logs/Bpool/)
- RURO_realdata_lr_pooling_901_v1.md — LR pooling test result (docs/France_case/P3a/execution_logs/Bpool/)
- JMP_pooled_P3a_estimation_design_memo_v1.md — pooled P3a estimation blueprint (docs/France_case/P3a/design/)
- JMP_joint_estimation_spec_v1.md — joint-spec governance + gsur exclusion rule (docs/France_case/_shared/governance/)
- JMP_couples_opportunity_draw_design_note_v1.md — couples 901-product draw design (docs/jmp_methodology/)
- JMP_conditional_wage_on_occupation_decision_note_v1.md — occupation-sampled wage/occ block decision (docs/jmp_methodology/)
- RURO_jax_bll0_realdata_hessian_v1.md — real-data Hessian PD result (docs/France_case/P3a/execution_logs/Bpool/)

## P3 — Welfare layer (W1-W6, V_i, Shapley-Shorrocks)
- JMP_welfare_measurement_decisions_memo_v2.md — authoritative welfare design, newest (docs/jmp_methodology/)
- JMP_measure_mapping_memo_v1.md — theory measures → W1-W6 mapping (docs/jmp_methodology/)
- JMP_welfare_spec_v5.md — current welfare spec, supersedes v1-v4 (docs/jmp_methodology/)
- RURO_welfare_F4C_final_singles_measures_report_v1.md — frozen singles W1/W3/W4/W6 (docs/jmp_methodology/)
- RURO_welfare_singles_Vi_production_report_v1.md — V_i^IS production (docs/jmp_methodology/)
- RURO_welfare_singles_measure_family_F5_report_v1.md — singles inequality / Gini (docs/jmp_methodology/)
- JMP_welfare_scaffolding_design_memo_v2.md — welfare scaffolding architecture, supersedes v1 (docs/jmp_methodology/)

## P4 — Paper writing (data, identification, methods)
- JMP_results_campaign_roadmap_v1.md — certified estimates → conference framing (docs/)
- RURO_CURRENT_STATE_AND_IDENTIFICATION.md — current state + identification narrative (docs/methods/)
- RURO_GSUR_rebuild_specification_v2_1.md — gsur exclusion-restriction / identification spec, v2.1 (docs/France_case/_shared/gsur/)
- RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md — gsur source (Eurostat LFS) + merge recipe (docs/France_case/_shared/gsur/)
- JMP_GSUR_year_alignment_decision_v1.md — opportunity-year lag decision (docs/France_case/_shared/governance/)
- JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md — P3a construction verdict (docs/France_case/P3a/execution_logs/multi_year_stage_M1/)
- JMP_GSURv2_multi_year_extension_construction_report_v1.md — GSURv2 per-year lookup construction (docs/France_case/P3a/execution_logs/GSURv2/)

## Known-pitfall feedback notes
- feedback_bpool_chosen_row_is_reconstructed.md (docs/France_case/About_data/)
- feedback_bpool_les_vs_yem_flips_are_structural.md (docs/France_case/About_data/)
- feedback_naming_policy_ruro.md (docs/France_case/About_data/)

## Caveats carried from the triage
- The repo's RURO_ACTIVE_RESULTS_REGISTRY.md is STALE (points at Feb-2026 job-choice/v3 runs, not this certified chain) — not included here.
- gsur v1 note (docs/estimation/RURO_GSUR_DATA_AND_MERGE_NOTE.md) is SUPERSEDED by the v2.1 spec above — deliberately excluded.
- gsplit variant docs are the FAILED synthetic-gate variant — excluded in favour of tlmpin (certified).
- Welfare/scaffold/recovery-gate docs: only the highest version is included (v5 welfare spec, v2 memos, tlmpin gate).
