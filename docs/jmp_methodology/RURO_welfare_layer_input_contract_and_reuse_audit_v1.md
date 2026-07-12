# Welfare layer — input contract & reusability audit (read-only)

**Date:** 2026-07-12 · **Scope:** `scripts/welfare/` (+ `fastlane/`), reuse onto `outputs/trial_singles2016/`.
**Method:** static read of source + config + new artifacts. Every claim cites file:line. READ-ONLY; no code run against the welfare pipeline.

---

## 1. INPUTS — what each entry point reads, and whether paths are parameterized

**`welfare_core.py` — fully config-driven (hardcodes nothing):**
- Config loader requires a top-level `welfare:` block ([welfare_core.py:78-84](scripts/welfare/welfare_core.py#L78-L84)).
- θ from `cfg["baseline"]["theta_hat_path"]` via `jrt.load_theta_star_from_csv` ([welfare_core.py:87-91](scripts/welfare/welfare_core.py#L87-L91)).
- spec from `cfg["baseline"]["spec_yaml_path"]` ([welfare_core.py:94-95](scripts/welfare/welfare_core.py#L94-L95)).
- data from `build_data_objects(engine_ready_stem, years, n_hh, couples_stem=…)` ([welfare_core.py:98-104](scripts/welfare/welfare_core.py#L98-L104)).
- Resolved config = [welfare_stage1_w3.yaml](scripts/welfare/configs/welfare_stage1_w3.yaml): `spec_yaml_path` = `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` ([:12](scripts/welfare/configs/welfare_stage1_w3.yaml#L12)); `theta_hat_path` = `theta_hat_realdata_901_v1.csv` ([:13](scripts/welfare/configs/welfare_stage1_w3.yaml#L13)); `engine_ready_stem`/`couples_stem` = `fr_p3a_bpool_engine_ready` ([:14-15](scripts/welfare/configs/welfare_stage1_w3.yaml#L14-L15)); couples resolution guard = 901 ([:18](scripts/welfare/configs/welfare_stage1_w3.yaml#L18)).

**Data always come from EUROMOD storage, not the repo:** `build_data_objects` → `_load_parquet_slice` reads `bpool_dir()/{stem}__{mode}.parquet` ([joint_recovery_test.py:203](scripts/bpool/joint_recovery_test.py#L203)) and filters on columns `data_year` ([:206](scripts/bpool/joint_recovery_test.py#L206)), `dgn` ([:209](scripts/bpool/joint_recovery_test.py#L209)), `stacked_hh_uid` ([:212-215](scripts/bpool/joint_recovery_test.py#L212-L215)). It **always loads a couples slice too** ([:271](scripts/bpool/joint_recovery_test.py#L271)) even when the caller discards it.

**The fastlane runners HARDCODE every path (not config-driven):**
- **F4A** — `_SPEC`, `_THETA`, `_VIIS` literals ([run_f4a…py:63-65](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L63-L65)); `STAGED_STEM="fr_p3a_bpool_engine_ready_staged_threeB1"` ([:53](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L53)); consumes precomputed `singles_ViIS_dualstem_v1.parquet` ([:65](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L65)).
- **F4C** — inherits F4A literals (`_SPEC=f4a._SPEC`, `_THETA=f4a._THETA`, `_VIIS=f4a._VIIS`) ([run_f4c…py:57](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L57)); reads `{STAGED_STEM}__mnlmeta.json` for `c_scale`/`l_scale` ([:155-157](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L155-L157)); reads V_i^IS parquet ([:159-160](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L159-L160)); `build_data_objects(f4a.STAGED_STEM, [], 0)` ([:161](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L161)).
- **F5** — reads `singles_measures_F4C_v1.parquet` ([run_f5…py:36](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L36)); `STAGED_STEM` hardcoded ([:32](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L32)); survey weight `dwt` pulled from the staged parquet.
- **F6 preflight** — config `welfare_stage1_w3.yaml` ([run_f6…py:90](scripts/welfare/fastlane/run_f6_price_b_preflight.py#L90)) + hardcoded preflight UIDs ([:82-87](scripts/welfare/fastlane/run_f6_price_b_preflight.py#L82-L87)); reads bpool priced/precompute long files (EUROMOD storage).

---

## 2. MEASURES — implemented welfare objects & defining functions

- **Attained utility V_i^IS** = household inclusive value `lse_i = logΣ_j exp(V_j)`, with per-row proposal correction `−log_prior` baked in: `compute_group_welfare` ([welfare_core.py:463-493](scripts/welfare/welfare_core.py#L463-L493)), `_group_lse_and_V` ([:119-124](scripts/welfare/welfare_core.py#L119-L124)). Engine-parity gate: `gate0_parity` ([:499-517](scripts/welfare/welfare_core.py#L499-L517)).
- **Normalized welfare level** `V_actual = V_i^IS − log(S)`, S=101 ([run_f4c…py:196-199](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L196-L199)).
- **Equivalent income** solved by monotone bracketing root of `R(w) − V_actual = 0`: `w3_inversion` ([welfare_core.py:523-575](scripts/welfare/welfare_core.py#L523-L575)) and `f4a.solve_equivalent_income`. The reference-set objects (`R`):
  - **W3** — laissez-faire, own set with pay (shift consumption at every node): `GroupState.R_shift` ([run_f4a…py:252-260](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L252-L260)).
  - **W1** — own opportunity set, *replace* consumption at all nodes with w: `R_replace` ([:262-265](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L262-L265)); working-only sensitivity `R_replace_working` ([:267-272](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L267-L272)).
  - **W4** — single home node, full-compensation endpoint `u(w, ℓ_home)`: `R_single_node` ([:274-275](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L274-L275)); finalized in F4C Task 3 ([run_f4c…py:250-294](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L250-L294)).
  - **W6** — universal weekly-hours grid J={0,20,30,35,39,48}, uniform 1/6, utility-only (no opportunity density): F4C Task 4 ([:296-395](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L296-L395)), grid at [:47-49](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L47-L49).
  - **W2 / W5** — deferred (not implemented) ([run_f4c…py:91](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L91)).
- **Reference job/opportunity set** per measure: W3 = own set + uniform transfer; W1 = own set, consumption→w; W4 = one home (non-work) node; W6 = common 6-node hours grid priced at equal pay w with no prior/opportunity term ([run_f4c…py:12,530-535](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L530-L535)).
- **EV / CV** — no function named "EV"/"CV". The W-family equivalent incomes are compensating-transfer objects but are **not** labeled Hicksian EV/CV anywhere. State: **not implemented as named EV/CV**.
- **Inequality** — `welfare_core.gini` (MAD form, internal only) ([welfare_core.py:581-594](scripts/welfare/welfare_core.py#L581-L594)); F5 survey-weighted family: `w_gini` ([run_f5…py:121-131](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L121-L131)), `w_cv2`, `w_theil_l`, `w_atkinson` ([:142-171](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L142-L171)).

---

## 3. COUNTERFACTUALS & "price_b"

- **Opportunity- / ability- / preference-equalized counterfactual distributions: NOT IMPLEMENTED.** Only *interfaces* exist: block membership `preference`/`ability`/`access` ([welfare_stage1_w3.yaml:58-71](scripts/welfare/configs/welfare_stage1_w3.yaml#L58-L71)) and a `decomposition_readiness` stub with a `preference_equalisation_pinned_switch: held|swapped` flag explicitly marked "interfaces only; NOT implemented this stage" ([:76-80](scripts/welfare/configs/welfare_stage1_w3.yaml#L76-L80)).
- **"price_b" = F6-PRICE-B**, the counterfactual EUROMOD *re-pricing* branch: reprice stored draws through EUROMOD and check identity of `ils_dispy` vs stored `ils_dispy_real` before any equalized-covariate run ([run_f6…py:4-9](scripts/welfare/fastlane/run_f6_price_b_preflight.py#L4-L9)). It is a **preflight only** and is **BLOCKED**: identity gate fails on a structural batch-geometry incompatibility, the EUROMOD FR system was updated after the stored baseline, and the equalized covariate spec (`JMP_decomposition_design_memo_v1.md`) is absent — F6 IMPLEMENTATION AUTHORIZED: NO ([run_f6…py:11-29](scripts/welfare/fastlane/run_f6_price_b_preflight.py#L11-L29); see [RURO_welfare_F6PRICEB0_geometry_audit_v1.md](docs/jmp_methodology/RURO_welfare_F6PRICEB0_geometry_audit_v1.md)).

## 4. DECOMPOSITION (Shapley-Shorrocks / ordered removal)

**NOT FOUND** as implemented code. No Shapley/Shorrocks/ordered-removal estimator exists in `scripts/`; "decomposition" appears only as prose in docs and as the not-implemented `decomposition_readiness` config stub ([welfare_stage1_w3.yaml:76](scripts/welfare/configs/welfare_stage1_w3.yaml#L76)). Every fast-lane runner explicitly disclaims decomposition (e.g. [run_f5…py:6](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L6)). The would-be design doc `JMP_decomposition_design_memo_v1.md` is **not on disk**.

---

## 5. ADAPTATION — running F4C/F5 on `outputs/trial_singles2016/`

New artifacts (from [fr_trial_singles2016__mnlmeta.json](outputs/trial_singles2016/fr_trial_singles2016__mnlmeta.json)): singles-only, **100 alts/HH**, **1,555 HH**, 155,500 rows ([:17-30](outputs/trial_singles2016/fr_trial_singles2016__mnlmeta.json#L17-L30)); `c_scale=7209.9`, `l_scale=10.0` ([:22-24](outputs/trial_singles2016/fr_trial_singles2016__mnlmeta.json#L22-L24)). Parquet has `idhh, dgn, dwt, idorighh, cluster_id, consumption, leisure, working, prior, log_prior, log_wage, wage` but is **MISSING `stacked_hh_uid` and `year_tag`** (verified by column read). Concrete deltas:

1. **Storage vs repo path.** Loader reads `bpool_dir()/{stem}__singles.parquet` ([joint_recovery_test.py:203](scripts/bpool/joint_recovery_test.py#L203)); trial lives in repo `outputs/trial_singles2016/`. → stage/copy into storage or override the path.
2. **Stem name.** Hardcoded `fr_p3a_bpool_engine_ready_staged_threeB1` in F4A/F4C/F5 must become `fr_trial_singles2016` (config for `welfare_core`; **source edit** for the fastlane runners).
3. **Missing keys.** `stacked_hh_uid` required at [joint_recovery_test.py:212](scripts/bpool/joint_recovery_test.py#L212) and by the uid bridge `_key_to_uid` ([run_f4a…py:166-178](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L166-L178)); `year_tag` required by that bridge ([:169,173](scripts/welfare/fastlane/run_f4a_singles_measure_core.py#L169-L173)). Loader also filters `data_year` ([joint_recovery_test.py:206](scripts/bpool/joint_recovery_test.py#L206)). → add `stacked_hh_uid`, `year_tag`, `data_year` to the trial parquet.
4. **Couples file required.** `build_data_objects` always loads a couples slice ([joint_recovery_test.py:271](scripts/bpool/joint_recovery_test.py#L271)); trial is singles-only → crash. → supply a `couples_stem` or patch the loader to skip couples.
5. **100 vs 101 alternatives.** F4C provenance gate hard-asserts `S_i==101` and `n_keys==5007` ([run_f4c…py:184-194](scripts/welfare/fastlane/run_f4c_final_singles_measures.py#L184-L194)); F5 expects `N_EXPECTED=5007` ([run_f5…py:33](scripts/welfare/fastlane/run_f5_singles_measure_family.py#L33)). The 100-alt trial FAILS both (S=101 = draw-0 actual + 100 counterfactual, [run_f6…py:74](scripts/welfare/fastlane/run_f6_price_b_preflight.py#L74)). → use the **101-alt successor fit**, or relax the S/N guards.
6. **θ + spec.** Trial reuses the SAME spec YAML (`estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`, [estimation_results…json:8](outputs/trial_singles2016/estimation_results_trial_singles2016.json#L8)) → no spec change. But θ differs and is stored in JSON/`params.csv`, not the 901 CSV welfare hardcodes. Loader needs a 2-column `parameter,value` CSV ([joint_recovery_test.py:82](scripts/bpool/joint_recovery_test.py#L82)); missing params fall back to spec initials ([:87](scripts/bpool/joint_recovery_test.py#L87)), so the 16 trial-pinned params ([estimation_results…json:14-31](outputs/trial_singles2016/estimation_results_trial_singles2016.json#L14-L31)) must all be in the CSV. → emit a trial θ CSV.
7. **V_i^IS must be regenerated.** F4A/F4C consume a *precomputed* `singles_ViIS_dualstem_v1.parquet` keyed by uid (built from the OLD baseline). → rerun the V_i^IS production step (F3-analogue via `welfare_core.compute_group_welfare`) on the trial θ/data before F4C.
8. **Weights/cluster present.** `dwt` (F5 weight) and `idorighh` (cluster) exist in the trial parquet → no change.

**Reuse verdict per script:**

| Script | Reads (inputs) | Writes (outputs) | Reuse verdict |
|---|---|---|---|
| `welfare_core.py` | config YAML → spec, θ CSV, engine-ready stem (storage), couples stem | V_i^IS, ESS, W3 inversion, gate0 | **SMALL ADAPTER** — new config (stem/θ); couples load needs a stem or skip |
| `run_f4a_singles_measure_core.py` | hardcoded spec/θ/`singles_ViIS_dualstem`; staged stem (storage) | `singles_measures_F4A_v1.parquet` (W3/W1/W4) | **MEDIUM ADAPTER** — edit hardcoded literals; regen V_i^IS; supply couples-free data |
| `run_f4c_final_singles_measures.py` | F4A literals + `{stem}__mnlmeta.json`, V_i^IS parquet, F4A parquet | `singles_measures_F4C_v1.parquet` (W3/W1/W4/W6) | **MEDIUM ADAPTER** — same + relax S=101/N=5007 guards (use 101-alt fit) |
| `run_f5_singles_measure_family.py` | F4C parquet + `dwt` from staged parquet | F5 inequality parquet/manifest | **SMALL ADAPTER** — repoint F4C parquet + staged stem; math reusable as-is |
| `run_f6_price_b_preflight.py` | config + bpool priced/precompute (EUROMOD) | F6 manifest/report | **BLOCKED** — independent of new estimates (geometry + system-version + spec) |

Math kernels (Box-Cox, logsumexp, bracketing solver, weighted inequality) are estimate-agnostic → **no rewrite needed**; all work is plumbing (stems, keys, V_i^IS regen, 100→101 alts, couples-free path).

---

## 6. DOCS — welfare-measure & F-series definitions

`doc_folder_structure.md` **does not exist**; the repo-root map is [Project_files_structure.md](Project_files_structure.md).

Measure definitions:
- [JMP_welfare_spec_v5.md](docs/jmp_methodology/JMP_welfare_spec_v5.md) — canonical welfare spec grounding `welfare_core` — **LARGE (570 lines)**; extract the W^3/W-family definition and normalization sections.
- [JMP_measure_mapping_memo_v1.md](docs/jmp_methodology/JMP_measure_mapping_memo_v1.md) — "the ONE rule" W1-W6 → reference-object mapping (on disk, 145 lines) — **SMALL**.
- [RURO_welfare_F4B_normalization_contract_decision_v1.md](docs/jmp_methodology/RURO_welfare_F4B_normalization_contract_decision_v1.md) — `V_actual=V_i^IS−log S` normalization contract (254 lines) — **LARGE**; extract the ratified-contract section.

F-series stages:
- [RURO_welfare_F4C_final_singles_measures_report_v1.md](docs/jmp_methodology/RURO_welfare_F4C_final_singles_measures_report_v1.md) — frozen W3/W1/W4/W6 (79 lines) — **SMALL**.
- [RURO_welfare_singles_measure_family_F5_report_v1.md](docs/jmp_methodology/RURO_welfare_singles_measure_family_F5_report_v1.md) — F5 weighted inequality (101 lines) — **SMALL**.
- (context) [RURO_welfare_F4A_measure_core_report_v1.md](docs/jmp_methodology/RURO_welfare_F4A_measure_core_report_v1.md) (117 lines, SMALL); [RURO_welfare_F6PRICEB0_geometry_audit_v1.md](docs/jmp_methodology/RURO_welfare_F6PRICEB0_geometry_audit_v1.md) (F6 blocker).

---

**Provenance:** static read only; no welfare script executed. Trial column set verified by direct parquet read (`stacked_hh_uid`, `year_tag` absent). No commit; no artifact modified.
