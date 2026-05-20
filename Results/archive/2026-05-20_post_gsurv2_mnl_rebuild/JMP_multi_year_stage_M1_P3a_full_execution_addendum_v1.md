# JMP Multi-Year Stage M1 P3a Full Execution Addendum v1

**Document:** `Results/JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md`
**Date:** 2026-05-20
**Supplements:** `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md`
**Source documents read:**
- `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md`
- `docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md`
- `scripts/multi_year/m1_stack_years.py`
- `scripts/multi_year/m1_config.py`
- `config/multi_year/fr_p3a_stage_m1.yaml`

---

## 1. Purpose

This addendum to the Stage M1 P3a full execution report serves three purposes:

1. Confirms that both singles and couples are now stacked and provides a clean cross-check of the row counts against the authorization memo.
2. Corrects two stale statements in `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` §30 (next-task suggestions that implied couples-only pooled estimation and welfare implementation, neither of which is authorized).
3. Audits whether the new `input_parquet_components` mechanism in `m1_stack_years.py` is fully config-driven and safe for future use, and flags any pre-publication package-cleanup items without patching them in this task.

---

## 2. Confirmation that singles and couples are now stacked

The current `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` contains both singles and couples rows for all three data years. The `household_type` column is present and correctly populated.

**Row counts — observed vs authorized input set:**

| Year | Component | Authorized input (readiness v2 §4) | Observed rows | Draws/HH | Observed HH |
| --- | --- | --- | --- | --- | --- |
| 2015 | singles | `fr_2015_RURO_mnl_v1gsurY2014__singles` | 166,900 | 100 | 1,669 |
| 2015 | couples | `fr_2015_RURO_mnl_v1gsurY2014__couples` | 256,600 | 100 | 2,566 |
| 2016 | singles | `fr_2016_RURO_mnl_v1gsurY2015__singles` | 167,600 | 100 | 1,676 |
| 2016 | couples | `fr_2016_RURO_mnl_v1gsurY2015__couples` | 257,700 | 100 | 2,577 |
| 2017 | singles | `fr_2017_RURO_mnl_v1gsurY2016__singles` | 166,200 | 100 | 1,662 |
| 2017 | couples | `fr_2017_RURO_mnl_v1gsurY2016__couples` | 229,500 | 100 | 2,295 |
| **Total** | | | **1,244,500** | | **12,445** |

Readiness report v2 §4 lists all nine files (six parquets + three sidecars) as the authorized input set. All six parquets contributed to the stacked output. The observed HH counts match the `sample_sizes.singles_deciders` and `sample_sizes.couples_deciders` fields in each `__mnlmeta.json` sidecar (readiness v2 §§5–7) exactly.

**GSUR coverage confirmation:**

- Singles rows (500,700): `gsur` column — 0 missing values. ✓
- Couples rows (743,800): `gsur_female` and `gsur_male` — 0 missing values each. ✓

**V1–V9 overall: PASS.** Construction is confirmed complete.

---

## 3. Correction to prior couples-only status

The prior execution report (`Results/JMP_multi_year_stage_M1_P3a_execution_report_v1.md`) produced a couples-only stacked dataset (743,800 rows, 7,438 HH-years). That file has been archived to `Data/processed/fr/pooled/archive_couples_only_20260520_120132/` and is no longer the active output.

The readiness report v2 §12 dry-run output showed only the couples file found per year (old `_find_parquet()` alphabetical fallback). That dry-run is now superseded. The new dry-run format (introduced in this task) shows per-component FOUND/NOT FOUND lines and is reproduced in the full execution report §5.

The following statement in readiness report v2 §12 is stale:

> *"[2015] FOUND → `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` (glob pattern 3)"*

The current stacker selects `couples` via explicit component filtering, not alphabetical fallback. The dry-run now reports both components per year. No correction is required to the readiness report itself (it is a pre-execution document); this note is for record-keeping only.

---

## 4. Report-heading compliance note

The full execution report uses the `## §N Title` heading format consistently across all 30 sections. This format is compliant with the established convention used in prior Stage M1 documents (`JMP_multi_year_stage_M1_implementation_plan_v2.md`, `JMP_multi_year_stage_M1_execution_readiness_report_v2.md`).

One inconsistency: the YAML comment in `config/multi_year/fr_p3a_stage_m1.yaml` now reads:

```yaml
# expected_row_counts: draw-expanded row totals per config (singles+couples, 100 draws/HH)
```

This comment is accurate for p3a but the p2, p3b, and p4 entries below it (`22849`, `33725`, `33334`) are still household-level counts from the original generalization work, not draw-expanded totals. They are not wrong (they are pre-execution placeholder values for those configs) but the comment is misleading as written. This is a pre-publication YAML cleanup item; see §10 below.

---

## 5. Correction to exact next task

The full execution report §30 offers three options as the next task:

> **Option A:** Implement a cluster-robust SE wrapper for the RURO estimator, then define a pooled RURO estimation spec, then seek authorization for provisional pooled estimation **on couples-only first** (simpler scope) before extending to full singles+couples.

> **Option C (welfare implementation):** Begin welfare implementation using the existing scaffolding design. **This does not require pooled estimation authorization and can proceed in parallel with Options A and B.**

Both of these suggestions are incorrect and are superseded here.

**Option A correction:** The sub-suggestion "couples-only first" is stale. The full singles+couples dataset is now complete; there is no remaining motivation to run couples-only pooled estimation as a stepping stone. If pooled estimation is eventually authorized, it would proceed on the full dataset (or an explicitly scoped subset) under a separate authorization memo, not by resuming the prior couples-only path.

**Option C correction:** Welfare implementation is NOT AUTHORIZED. The readiness report v2 §15 lists "Welfare scaffolding implementation: NOT AUTHORIZED — design is complete; implementation remains deferred." Readiness report v2 §18 states explicitly: "Even after one of those baseline decisions, welfare implementation and welfare computation require their own implementation report, audit, and authorization." The existence of `docs/JMP_welfare_measurement_decisions_memo_v2.md` and `docs/JMP_welfare_scaffolding_design_memo_v2.md` authorizes neither implementation nor computation.

The statement in §30 Option C that welfare implementation "does not require pooled estimation authorization" is technically true in a narrow sense but is misleading: welfare implementation has its own separate authorization requirement that has not been met. It is not a currently unblocked task.

The corrected statement for both options is given in §12 below.

---

## 6. Welfare authorization correction

For the record, the complete welfare authorization status as of 2026-05-20 is:

| Item | Status | Source |
| --- | --- | --- |
| Welfare measurement decisions memo (v2) | COMPLETE | `docs/JMP_welfare_measurement_decisions_memo_v2.md` |
| Welfare scaffolding design memo (v2) | COMPLETE | `docs/JMP_welfare_scaffolding_design_memo_v2.md` |
| Welfare scaffolding implementation | NOT AUTHORIZED | Readiness v2 §15 |
| Welfare computation | NOT AUTHORIZED | Readiness v2 §15, §18 |

The welfare decisions and scaffolding design documents lock the welfare object, inequality/decomposition approach, and code architecture. They do not constitute implementation or computation authorization. Welfare computation additionally requires an accepted empirical baseline — either the pooled route (which is itself not yet authorized for estimation) or an explicit M1-clean 2016 fallback decision. Neither baseline decision has been made.

No welfare work of any kind — including implementation, coding, or test runs — is authorized by the Stage M1 P3a construction completion.

---

## 7. Package-hygiene audit of component loading

The new component-loading mechanism in `m1_stack_years.py::_find_component_parquets()` is audited here.

**Mechanism:**

For each component name in `cfg.input_parquet_components` (e.g., `["singles", "couples"]`), the function:
1. Iterates over the configured glob patterns in order.
2. Filters each pattern's candidates to files whose name (lowercased) contains the component string as a substring.
3. Returns the first match per component; breaks after the first matching pattern.

**Config-driven assessment:**

The component list is fully config-driven. `StageConfig.input_parquet_components` reads `raw.get("input_parquet_components", ["singles", "couples"])` — the default is `["singles", "couples"]`, and the YAML override is `input_parquet_components: [singles, couples]` in `fr_p3a_stage_m1.yaml`. Any future YAML can specify different components or a single component without touching the script.

**Safety properties:**

| Property | Assessment |
| --- | --- |
| Config-driven component list | YES — no hardcoded component names in `m1_stack_years.py` |
| `household_type` values are config-derived | YES — values written to column come directly from the `cfg.input_parquet_components` strings |
| Missing-component detection | YES — `missing_desc` check requires all listed components to be found before execution |
| Empty-list edge case | LATENT BUG — if `input_parquet_components: []`, `missing_desc` stays empty and the inner loop produces `year_frames = []`; `year_frames[0]` raises `IndexError`. Low risk (no current config sets this); pre-publication guard recommended. |
| Component name collision risk | LOW — component-string filter combined with year-specific glob pattern (e.g. `*2016*RURO*mnl*.parquet`) limits false positives; no file in the current input directory creates an ambiguous match. |
| Schema union safety | YES — `pd.concat(join='outer')` fills cross-component missing columns with NaN; `household_type` is added before concat so it is never NaN. |

**Overall audit verdict:** Component loading is correct and config-driven for the current use case. Two pre-publication items are flagged in §10.

---

## 8. Whether m1_stack_years remains country/year agnostic

**Yes.**

All country/year-specific values are read from the stage-config YAML through `StageConfig`. The stack logic contains no hardcoded country codes, year lists, file-stem patterns, or component names. Specifically:

| Attribute | Source |
| --- | --- |
| Input directory | `cfg.input_parquet_dir` (from `input_parquet_dir` in YAML) |
| Glob patterns | `cfg.input_parquet_patterns` (from `input_parquet_patterns` in YAML) |
| Component names | `cfg.input_parquet_components` (from `input_parquet_components` in YAML, default `["singles", "couples"]`) |
| Year list | `cfg.years` (from `years` in YAML) |
| UID scheme | `cfg.uid_base`, `cfg.year_tags` (from YAML) |
| Output directory | `cfg.pooled_output_dir` (from YAML) |
| `household_type` column values | Taken directly from the component name strings at runtime — no hardcoding |

A future country (e.g., DE, NL) would produce a correct, separately labelled stacked parquet by providing its own stage-config YAML with appropriate `country_slug`, `years`, `year_tags`, `input_parquet_patterns`, and `input_parquet_components`. No changes to any shared script would be needed.

One implicit assumption holds: the component name (e.g., `"singles"`) must appear as a case-insensitive substring in the filename of the corresponding parquet. This is consistent with the current FR naming convention (`__singles.parquet`, `__couples.parquet`) and is the RURO pipeline's established convention. A future country deviating from this naming convention would need to either align its filenames or override `input_parquet_components` with matching substrings.

---

## 9. Whether legacy single-file or combined-file configs remain supported

**No — and this is a pre-publication cleanup item.**

The original `_find_parquet()` function (removed in Task 2) supported three fallback cases:

1. A file with `"combined"` in the name was preferred.
2. A file with neither `"singles"` nor `"couples"` in the name was next preferred.
3. Alphabetical `candidates[0]` (which happened to pick `"couples"` over `"singles"`) was the final fallback.

The replacement `_find_component_parquets()` does not implement any of these cases. Its filtering logic matches `component in p.name.lower()`, so:

- A combined file (e.g., `fr_2016_RURO_mnl_combined.parquet`) with neither `"singles"` nor `"couples"` in the name would not be matched by either component entry.
- A combined file would be reachable only if a component named `"combined"` is added to `input_parquet_components` in the YAML.
- A single-file config (e.g., `input_parquet_components: []`) would silently produce no frames and raise `IndexError` at runtime (the latent bug noted in §7).

**Consequence:** Any future country or configuration that uses a single combined parquet per year rather than separate singles/couples files cannot use `m1_stack_years.py` as currently written without either (a) naming the combined file to contain one of the listed component strings, or (b) setting `input_parquet_components: [combined]` and naming the file accordingly.

This is a behavioral regression relative to the pre-Task-2 stacker for the combined-file use case. It does not affect France P3a (which has always used separate singles/couples files) and is not a defect for the current work. However, it should be documented and optionally restored before the package is used for a new country or dataset configuration.

**Recommended pre-publication cleanup:** Either restore a `combined` fallback mode (e.g., `input_parquet_components: [combined]` triggers the old preferred-file logic) or add a docstring noting that combined-file inputs require listing a matching component name explicitly.

---

## 10. Required follow-up code cleanup if any

The following items do not require patching now. They are recorded here for pre-publication action.

| Item | Location | Description | Priority |
| --- | --- | --- | --- |
| **A. Combined-file mode removed** | `scripts/multi_year/m1_stack_years.py` | `_find_parquet()` was replaced; no combined-file fallback path. See §9. | Pre-publication |
| **B. Empty `input_parquet_components` guard** | `scripts/multi_year/m1_stack_years.py` | `year_frames = []` case raises `IndexError`. Add a validation guard at config-load time: `if not cfg.input_parquet_components: raise ValueError(...)`. | Pre-publication |
| **C. `ils_dispy_real_range` calibrated for couples** | `config/multi_year/fr_p3a_stage_m1.yaml` | Range `[25000, 55000]` is for couple-household income; singles mean is ~7,500. V5 warns but does not fail. Either (a) split range by `household_type`, or (b) add separate `ils_dispy_real_range_singles` and `ils_dispy_real_range_couples` keys, or (c) suppress the range check for singles explicitly. | Pre-publication |
| **D. `expected_row_counts` comment misleading** | `config/multi_year/fr_p3a_stage_m1.yaml` | Comment says "draw-expanded row totals" but p2/p3b/p4 entries are still HH-level placeholder counts. Update when those configs are executed. | When p2/p3b/p4 are run |
| **E. Legacy combined-file docstring** | `scripts/multi_year/m1_stack_years.py` module docstring | Docstring does not mention the `input_parquet_components` key or the schema-union behavior. Update before package publication. | Pre-publication |
| **F. `check_v8()` fallback branch** | `scripts/multi_year/m1_validate.py` | The global GSUR check (no `household_type` column) could silently pass a mixed-type file that lacked the column. Not a current risk; add a note in the docstring. | Low priority |

Items A and B are the only ones with a correctness implication for future use. All others are documentation or calibration improvements.

---

## 11. Updated verdict

**Stage M1 P3a full provisional construction: COMPLETE.**

- Pooled file: `Data/processed/fr/pooled/fr_p3a_harmonised.parquet`
- Rows: 1,244,500 (singles + couples, all three years, 100 draws/HH)
- Columns: 143
- V1–V9: PASS
- Provisioning label: `provisional_v1_fallback_opportunity_year_aligned`
- `household_type` column present: `"singles"` or `"couples"` for every row
- GSUR: per-component zero missing (V8 PASS)
- Identity validation: PASS (2016→2017 sex_stability=1.0000, age=1.0000, suspicious=0.0000)
- `cluster_id = idorighh`, unique_cluster_id = 9,657

**What is NOT authorized and is NOT the next task:**

- Pooled estimation (no cluster-robust SE wrapper; no pooled spec; no authorization memo)
- Welfare implementation (requires its own implementation report, audit, and authorization)
- Welfare computation (same; additionally requires an accepted empirical baseline)
- P3b or P4 execution (hard-blocked gates)
- Canonical MNL promotion (provisional label in effect)

---

## 12. Exact next authorized task

The exact next authorized task is a **Stage M1 P3a construction audit and verdict** — a structured review and decision memo covering the following open questions. This is a documentation and decision task, not an execution task.

**Questions for the construction audit:**

1. **v1 GSUR fallback verdict:** Is the `v1_fallback_opportunity_year_aligned` label acceptable as final for 2015 and 2017, or must GSURv2 extension proceed before any downstream use? A written verdict one way or the other is required before any estimation result from this file can be cited.

2. **Pooled estimation authorization pathway:** What is the intended sequence — (a) implement cluster-robust SE first, then write a pooled estimation spec, then seek authorization; or (b) defer pooled estimation entirely and proceed with single-year M1-clean as the paper's empirical baseline? A written decision forecloses both options remaining indefinitely open.

3. **V5 range update:** Update or annotate `ils_dispy_real_range` in the YAML to cover the singles population (mean ≈ 7,500 EUR/year). This is a validation-quality item, not a data correctness item, but should be resolved before the validation output is cited in any document.

4. **Package cleanup items A–B from §10:** Decide whether to patch the combined-file regression (§10 item A) and the empty-list guard (item B) before the stacker is reused for another config. These do not affect France P3a.

**What the construction audit does not authorize:**

The audit produces written decisions. It does not authorize pooled estimation, welfare implementation, welfare computation, or any Stage M1 re-run. Execution of any downstream step continues to require its own separate authorization.