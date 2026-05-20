# JMP Multi-Year Stage M1 — Static Validation Report v2

**Document:** Results/JMP_multi_year_stage_M1_static_validation_report_v2.md
**Date:** 2026-05-19
**Generalization report:** docs/JMP_multi_year_stage_M1_generalization_report_v1.md
**Prior static validation:** Results/JMP_multi_year_stage_M1_static_validation_report_v1.md

---

## Check 1 — Config YAML and loader exist

| File | Expected path | Present |
| --- | --- | --- |
| `fr_p3a_stage_m1.yaml` | `config/multi_year/fr_p3a_stage_m1.yaml` | **YES** |
| `m1_config.py` | `scripts/multi_year/m1_config.py` | **YES** |

Config YAML contains all required sections: project identity, year/tag mapping,
uid_base, column names, raw_id_cols, monetary_variables,
variables_excluded_from_deflation, file paths, expected_row_counts,
expected_overlap_counts, identity_validation_thresholds, special_gates.

**Result: PASS**

---

## Check 2 — All reusable scripts expose --help successfully

Tested using `.venv\Scripts\python.exe <script> --help` with `PYTHONPATH` set
to the repo root.

| Script | `--help` exit code |
| --- | --- |
| `m1_stack_years.py` | **0** |
| `m1_harmonise_cpi.py` | **0** |
| `m1_add_cluster_key.py` | **0** |
| `m1_validate.py` | **0** |
| `m1_identity_validation.py` | **0** |

All five scripts show both `--config` and `--stage-config` in their usage line.
`--config` is no longer restricted to `choices=["p2","p3a","p3b","p4"]`.

**Result: PASS**

---

## Check 3 — `--config p3a` dry-run produces correct output

```
m1_stack_years.py --config p3a --dry-run   → exit 0
```

Output confirms:
- `Config YAML: ...config/multi_year/fr_p3a_stage_m1.yaml`
- `years=[2015, 2016, 2017]`
- `B=100,000,000,000`
- UID ranges `[1×10^11+1 to 4×10^11−1]` for tags 1–3
- Raw IDs: `['idorighh', 'idorigperson', 'idhh', 'idperson']`
- No parquet written

```
m1_harmonise_cpi.py --config p3a --dry-run  → exit 0
```

Output confirms:
- CPI file absent (§7 decision not yet made)
- Monetary variables list from YAML
- Correct output path `fr_p3a_harmonised.parquet`

```
m1_add_cluster_key.py --config p3a --dry-run  → exit 0
```

Output confirms:
- `cluster_id = idorighh` (from config `cluster_source_col`)
- Correct harmonised parquet path

**Result: PASS**

---

## Check 4 — `--stage-config` explicit path works identically to `--config p3a`

```
m1_stack_years.py \
    --stage-config config/multi_year/fr_p3a_stage_m1.yaml --dry-run  → exit 0
```

Output is byte-identical to `--config p3a --dry-run`. Both display:
`Config YAML: ...config/multi_year/fr_p3a_stage_m1.yaml`

**Result: PASS**

---

## Check 5 — P3b gate still blocks at exit 1

```
m1_stack_years.py --config p3b --dry-run  → exit 1
```

Error message:
```
ERROR  Config 'p3b' is not authorised for execution:
P3b is blocked until Results/M1_ISF_tpr_comparability_check_2018.md
concludes 'proceed'. See §16 of the Stage M1 plan.
```

Gate condition is read from `cfg.blocked_configs["p3b"]` in the YAML; not
hard-coded in Python. P3b exits 1 whether or not `--dry-run` is passed.

**Result: PASS**

---

## Check 6 — No hard-coded country/year constants remain in reusable scripts

Verified by inspection of all five refactored scripts. The following
module-level constants were removed in this pass:

| Removed constant | Script(s) |
| --- | --- |
| `POOLED_DIR` | all 5 |
| `YEAR_TAG`, `TAG_YEAR` | stack, harmonise, validate, identity |
| `B = 10**11` | stack |
| `CONFIGS` dict | stack |
| `RAW_ID_COLS` | stack, validate |
| `MONETARY_VARS`, `EXCLUDED_VARS` | harmonise |
| `CPI_SOURCE_FILE` | harmonise, validate |
| `CONFIG_TAGS`, `EXPECTED_HH_ROWS` | validate |
| `P3A_EXPECTED_OVERLAP_*` | validate |
| `ILS_DISPY_REAL_MIN/MAX` | validate |
| `IDENTITY_THRESHOLDS` | validate |
| `EXPECTED_OVERLAPS` | identity |
| `THRESHOLDS` | identity |
| Hard-coded `choices=["p2","p3a","p3b","p4"]` | all 5 |
| Hard-coded `fr_{config}_*.parquet` path patterns | all 5 |

Grep for module-level assignment of any of the above in the five scripts
returns zero results.

**Result: PASS**

---

## Check 7 — France-specific wrapper files correctly labelled

| File | Label present |
| --- | --- |
| `m1_isf_check_2018.py` | YES — "FRANCE-2018-SPECIFIC RESEARCH WRAPPER" header in module docstring |
| `run_m1_p3a.ps1` | YES — "FRANCE P3a RESEARCH ORCHESTRATION WRAPPER" header in comment block |

Both files retain all original functionality unchanged.

**Result: PASS**

---

## Check 8 — No final pooled parquets or estimation outputs written

`Data/processed/fr/pooled/` contains no `.parquet` files.
`git status --short -- Data/processed/ outputs/` returns clean.
`git status --short -- scripts/enhanced/` returns clean.

| Expected absent file | Present |
| --- | --- |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | **NO** |
| Any file under `outputs/estimates/` | **NO new files** |

**Result: PASS**

---

## Check 9 — Canonical single-year files unchanged

`git status` confirms the following files are clean:

| File | Status |
| --- | --- |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | CLEAN |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | CLEAN |
| `scripts/enhanced/RURO_post_estimation_styled.py` | CLEAN |
| `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` | CLEAN |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | CLEAN |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | CLEAN |
| `Data/external/FR_gsur_ruro.parquet` | CLEAN |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | CLEAN |

**Result: PASS**

---

## Check 10 — StageConfig loads correctly and exposes expected values

Verified by dry-run output and code inspection:

| StageConfig attribute | Expected value | Verified via |
| --- | --- | --- |
| `country_code` | `FR` | YAML |
| `years` | `[2015, 2016, 2017]` | dry-run output |
| `uid_base` | `100000000000` | dry-run UID ranges |
| `cluster_source_col` | `idorighh` | dry-run `cluster_id = idorighh` |
| `monetary_variables[0]` | `ils_dispy` | dry-run monetary vars list |
| `cpi_final_path` stem | `cpi_hicp_fr_harmonisation.csv` | dry-run CPI path |
| `blocked_configs["p3b"]` | non-empty string | exit-1 error message |
| `identity_thresholds["sex_stability_min"]` | `0.999` | YAML |
| `expected_overlap_counts[(2016,2017)]` | `8796` | YAML |

**Result: PASS**

---

## Check 11 — `--help` on non-reusable scripts unchanged

| Script | `--help` exit code | Wrapper label present |
| --- | --- | --- |
| `m1_isf_check_2018.py` | **0** | YES (module docstring) |

`run_m1_p3a.ps1` is a PowerShell script; it produces no `--help` output but
the wrapper header is present at lines 2–10 of the file.

**Result: PASS**

---

## Final: PASS / FAIL for Stage M1 generalization

**PASS**

All 11 static checks pass. Stage M1 generalization is complete and correct:

- All five reusable scripts accept `--stage-config` and `--config` interchangeably.
- No hard-coded country/year/config assumptions remain in any reusable script.
- France P3a behaviour (dry-run output, UID ranges, gate messages, file paths)
  is identical to the Session 1 implementation.
- The P3b execution gate continues to block at exit 1.
- The CPI source decision gate continues to block execution.
- `m1_isf_check_2018.py` and `run_m1_p3a.ps1` are correctly labelled as
  France-specific research wrappers.
- No canonical data or estimation files were modified.
- No pooled parquets were written.

**Stage M1 generalization is complete.** Adding a new country requires only a
new YAML config file and `--stage-config <path>` — no Python changes.
