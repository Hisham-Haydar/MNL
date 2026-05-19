# JMP Multi-Year Stage M1 — Static Validation Report

**Document:** Results/JMP_multi_year_stage_M1_static_validation_report_v1.md
**Date:** 2026-05-19
**Implementation report:** docs/JMP_multi_year_stage_M1_implementation_report_v1.md
**Reference plan:** docs/JMP_multi_year_stage_M1_implementation_plan_v2.md

---

## Check 1 — All expected scripts exist

| Script | Expected path | Present |
| --- | --- | --- |
| `m1_stack_years.py` | `scripts/multi_year/m1_stack_years.py` | **YES** |
| `m1_harmonise_cpi.py` | `scripts/multi_year/m1_harmonise_cpi.py` | **YES** |
| `m1_add_cluster_key.py` | `scripts/multi_year/m1_add_cluster_key.py` | **YES** |
| `m1_validate.py` | `scripts/multi_year/m1_validate.py` | **YES** |
| `m1_identity_validation.py` | `scripts/multi_year/m1_identity_validation.py` | **YES** |
| `m1_isf_check_2018.py` | `scripts/multi_year/m1_isf_check_2018.py` | **YES** |
| `run_m1_p3a.ps1` | `scripts/multi_year/run_m1_p3a.ps1` | **YES** |
| `__init__.py` | `scripts/multi_year/__init__.py` | **YES** |
| Template CSV | `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` | **YES** |

**Result: PASS**

---

## Check 2 — All scripts expose --help successfully

Tested using `.venv\Scripts\python.exe <script> --help` with UNC literal paths.

| Script | `--help` exit code |
| --- | --- |
| `m1_stack_years.py` | **0** |
| `m1_harmonise_cpi.py` | **0** |
| `m1_add_cluster_key.py` | **0** |
| `m1_validate.py` | **0** |
| `m1_identity_validation.py` | **0** |
| `m1_isf_check_2018.py` | **0** |

All scripts accept `--dry-run` where applicable. Dry-run mode tested for
`m1_stack_years.py` (p3a and p3b), `m1_harmonise_cpi.py`, and
`m1_add_cluster_key.py` — all exited 0 and produced correct output (see Check 12 below).

**Result: PASS**

---

## Check 3 — No final pooled parquets were written

Directory `Data/processed/fr/pooled/` was created (empty). No `.parquet` files
exist under it. Verified by Glob pattern `Data/processed/fr/pooled/*.parquet`
returning no results.

| Expected absent file | Present |
| --- | --- |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3b_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3b_harmonised.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p4_stacked_raw.parquet` | **NO** |

**Result: PASS**

---

## Check 4 — No pooled MNL estimation parquets were written

No new parquet files were created under `Data/processed/fr/`. The existing
canonical file `fr_2016_RURO_mnl_job_gmm` was not modified. Verified by
`git status --short -- Data/processed/` returning no changes.

**Result: PASS**

---

## Check 5 — No estimation outputs were created

`outputs/estimates/fr/spec/ruro_occ/` and `outputs/post_estimation/fr/spec/ruro_occ/`
are unchanged. `git status --short -- outputs/` returns clean. No GAMS output,
no JSON results files, no HTML reports were written.

**Result: PASS**

---

## Check 6 — No welfare outputs were created

No welfare scaffolding scripts were created. No welfare output files exist.
Stage M1 scripts contain no welfare logic. Verified by absence of any
`welfare` pattern in new scripts:

```
grep -ri "welfare" scripts/multi_year/ → 0 matches
```

**Result: PASS**

---

## Check 7 — Canonical single-year files were not modified

`git status --short -- scripts/enhanced/ outputs/` returns clean (no changes).
The following canonical files were specifically verified unchanged:

| File | Status |
| --- | --- |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | CLEAN |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | CLEAN |
| `scripts/enhanced/RURO_post_estimation_styled.py` | CLEAN |
| `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` | CLEAN |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | CLEAN |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | CLEAN |
| `outputs/estimates/fr/spec/ruro_occ/` | CLEAN |
| `outputs/post_estimation/fr/spec/ruro_occ/` | CLEAN |
| `Data/external/FR_gsur_ruro.parquet` | CLEAN |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | CLEAN |

**Result: PASS**

---

## Check 8 — No final CPI/HICP harmonisation source file was created

`Data/external/cpi_hicp_fr_harmonisation.csv` does **not** exist.

The template `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` was created
(authorised by the task). It contains only `PLACEHOLDER` values and cannot be
used directly by `m1_harmonise_cpi.py`. That script aborts with a clear error
if the final CSV is absent, enforcing the §7 CPI source decision gate.

| File | Expected | Present |
| --- | --- | --- |
| `cpi_hicp_fr_harmonisation.csv` (final, NOT authorised) | Absent | **NO** |
| `cpi_hicp_fr_harmonisation_TEMPLATE.csv` (authorised) | Present | **YES** |

**Result: PASS**

---

## Check 9 — GSURv2 year parameterization was not implemented

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` was not modified. `git status`
confirms the file is clean. `YEAR = 2016` at line 44 remains unchanged.

The audit of what year parameterization requires is documented in
`docs/JMP_multi_year_stage_M1_implementation_report_v1.md` §11:

- **Line 44:** `YEAR = 2016` → change to `argparse --year` argument
- **Lines 165, 167, 497, 675:** four call sites that use `YEAR` — all already pass `YEAR` to the year-generic `_find_year_col()` function
- **`BENCHMARK_PCT`:** must be parameterised to a year→rate lookup after INSEE BDM retrieval
- **`OUT` path:** should include year in filename for multi-year runs

This change is deferred to Stage M2 as instructed. No Stage M1 execution is
blocked by this deferral (`FR_gsur_ruro.parquet` v1 covers 2015, 2017, 2018).

**Result: PASS (not implemented; audit documented)**

---

## Check 10 — Naming uses RURO / ruro_occ, not old personal labels

All new script filenames use `m1_` prefix with descriptive names — no `stijn`
in any filename.

The V9 validation check in `m1_validate.py` contains 8 occurrences of the
string `"stijn"` — these are inside the detection function `check_v9()` which
*searches for* the token in output files. They are the detector, not labels.
No script, output file, column name, or result file uses `stijn` as a label.

Grep for `stijn` in `scripts/multi_year/`:
- `m1_validate.py`: 8 hits — all inside `check_v9()` function that detects the token
- All other scripts: 0 hits

**Result: PASS**

---

## Check 11 — Dry-run behaviour verified

| Dry-run test | Exit code | Output correct |
| --- | --- | --- |
| `m1_stack_years.py --config p3a --dry-run` | 0 | YES — reports 3 inputs missing, shows correct UID ranges `[1×10^11+1 to 4×10^11−1]` |
| `m1_stack_years.py --config p3b --dry-run` | **1** | YES — blocked: "Config 'p3b' is not authorised for execution" with ISF memo reference |
| `m1_harmonise_cpi.py --config p3a --dry-run` | 0 | YES — reports stacked parquet absent, CPI file absent, lists §8 monetary variables |
| `m1_add_cluster_key.py --config p3a --dry-run` | 0 | YES — reports harmonised parquet absent, states action: cluster_id = idorighh |

P3b correctly exits 1 with a blocking message whether `--dry-run` is passed or
not. P4 is similarly blocked. P2 and P3a are unblocked (inputs not yet present,
but the gate check itself passes).

**Result: PASS**

---

## Check 12 — Validation checks V1–V9 implemented in m1_validate.py

| Check | Implementation status |
| --- | --- |
| V1 — stacked_person_uid unique per row; stacked_hh_uid unique per hh-year | Implemented |
| V2 — row-count agreement (±10 tolerance; per-year breakdown) | Implemented |
| V3 — raw-ID completeness (4 columns non-null) | Implemented |
| V4 — year_tag set matches config | Implemented |
| V5 — CPI deflation correctness (spot sample + range check; skips if CPI file absent) | Implemented |
| V6 — cluster_id == idorighh; P3a 2016∩2017 repeat-household count ≈ 8,796 (±200) | Implemented |
| V7 — inline identity validation (sex, age, suspicious records, hh continuity) | Implemented |
| V8 — zero missing gsur values (warns if column absent) | Implemented |
| V9 — no stijn token in file path or column names | Implemented |
| V10 — P3b ISF check | Enforced as gate in m1_stack_years.py (stronger than post-hoc check) |

**Result: PASS**

---

## Final: PASS / FAIL for Stage M1 scaffolding readiness

**PASS**

All 12 static checks pass. Stage M1 scaffolding is complete and correct:

- All 6 Python scripts and the PS1 runner are present and functional.
- No canonical data or estimation files were modified.
- No unauthorised outputs were produced.
- P3b is hard-blocked at the execution gate.
- The CPI decision gate prevents silent phi_t substitution.
- Dry-run mode works correctly for all applicable scripts.
- UID scheme, raw-ID preservation, cluster_id assignment, and all V1–V9 checks
  are implemented exactly as specified in §§10–12, 17 of the Stage M1 plan.

**Stage M1 scaffolding is ready for execution** once the four upstream
preconditions are met (CPI source decision, EUROMOD runs for FR_2015/FR_2017,
MNL parquets for 2015/2017, Eurostat/INSEE data acquisition).

See `docs/JMP_multi_year_stage_M1_implementation_report_v1.md` §16 for the
exact next task.