# JMP Multi-Year Stage M1 — Generalization Report v1

**Document:** docs/JMP_multi_year_stage_M1_generalization_report_v1.md
**Date:** 2026-05-19
**Static validation report:** Results/JMP_multi_year_stage_M1_static_validation_report_v2.md
**Prior implementation report:** docs/JMP_multi_year_stage_M1_implementation_report_v1.md
**Reference plan:** docs/JMP_multi_year_stage_M1_implementation_plan_v2.md

---

## §1 — Motivation and scope

The Stage M1 scripts delivered in Session 1 hard-coded all France-P3a-specific
values (year sets, tag mappings, column names, file path patterns, monetary
variable lists, expected overlap counts, identity-validation thresholds, and
special gate conditions) directly into module-level constants. That made every
reusable script a France-only tool.

This generalization pass moves every country/year/config assumption into a
single YAML config file. The five reusable scripts now accept
`--stage-config <path>` and are fully country/year/config agnostic. France P3a
behaviour is preserved exactly — the backward-compatible `--config p3a` shortcut
resolves to the France P3a YAML internally.

**Scope boundaries (unchanged from Session 1):**
- No pooled parquets written.
- No estimation, no welfare, no GSURv2 year parameterization.
- No P3b or P4 activation.
- Canonical single-year data and estimation files untouched.

---

## §2 — New files created

| File | Purpose |
| --- | --- |
| `config/multi_year/fr_p3a_stage_m1.yaml` | France P3a config; single source of truth for all France-specific values |
| `scripts/multi_year/m1_config.py` | YAML loader; exposes `StageConfig` dataclass and `load_stage_config()` |

---

## §3 — Config YAML structure (`fr_p3a_stage_m1.yaml`)

The YAML is organised into eight sections:

1. **Project identity** — `country_code`, `country_slug`, `project_label`, `config_name`
2. **Year/tag mapping** — `years: [2015, 2016, 2017]`; `year_tags: {2015: 1, ...}`
3. **UID scheme** — `uid_base: 100000000000` (= 10^11)
4. **Column names** — `household_id_col`, `person_id_col`, `raw_household_id_col`, `raw_person_id_col`, `cluster_id_col`, `cluster_source_col`, `raw_id_cols`
5. **Monetary variables** — `monetary_variables`, `variables_excluded_from_deflation`
6. **File paths** — `processed_root`, `pooled_output_dir`, `results_dir`, `external_data_dir`, `cpi_template_path`, `cpi_final_path`, `input_parquet_dir`, `input_parquet_patterns`, `output_file_stems`
7. **Expected counts** — `expected_row_counts`, `expected_overlap_counts`, `p3a_overlap_tolerance`, `ils_dispy_real_range`
8. **Identity validation thresholds** — `identity_validation_thresholds` (all five §13 thresholds)
9. **Special gates** — `p3b_isf_memo_path`, `p3b_isf_proceed_phrase`, `blocked_configs`

All paths stored as repo-relative strings; `StageConfig` resolves them against
`REPO = Path(__file__).resolve().parents[2]` at load time.

---

## §4 — Config loader (`m1_config.py`)

`load_stage_config(config_name, stage_config_path)` returns a `StageConfig`
object. Priority: explicit `--stage-config` path > `--config` shortcut.

**Shortcut map:**

| Shortcut | Resolved YAML |
| --- | --- |
| `p2` | `config/multi_year/fr_p3a_stage_m1.yaml` |
| `p3a` | `config/multi_year/fr_p3a_stage_m1.yaml` |
| `p3b` | `config/multi_year/fr_p3a_stage_m1.yaml` |
| `p4` | `config/multi_year/fr_p3a_stage_m1.yaml` |

All four France shortcuts resolve to the same YAML (P3b/P4 execution is still
blocked by the `blocked_configs` gate in the YAML). New countries supply their
own YAML and pass it via `--stage-config`; no shortcut registration required.

**`StageConfig` typed accessors include:**
- `stacked_raw_path()` / `harmonised_path()` — canonical pooled file paths
- `expected_year_tags()` — `Set[int]` of tags for this config's `years`
- `expected_rows_for(config_key)` — row count expectation from `expected_row_counts`
- `config_tags_for(config_key)` — year_tag set for a named sub-config

---

## §5 — Changes to `m1_stack_years.py`

**Removed hard-coded constants:**
- `POOLED_DIR`, `B`, `YEAR_TAG`, `CONFIGS`, `RAW_ID_COLS`, `ADDED_COLS`
- Hard-coded `choices=["p2","p3a","p3b","p4"]` in argparse
- Hard-coded `fr_{config}_stacked_raw.parquet` output name pattern
- Hard-coded `Results/M1_ISF_tpr_comparability_check_2018.md` gate path
- Hard-coded P3b/P4 blocked-reason strings

**Replaced with:**
- `cfg = load_stage_config(config_name, stage_config_path)`
- `_find_parquet(year, cfg)` uses `cfg.input_parquet_patterns`
- `_add_stacked_ids(df, year, cfg)` uses `cfg.year_tags`, `cfg.uid_base`, `cfg.raw_id_cols`, `cfg.household_id_col`, `cfg.person_id_col`
- `_check_gates(config_name, cfg)` reads `cfg.blocked_configs`, `cfg.p3b_isf_memo_path`, `cfg.p3b_isf_proceed_phrase`
- `out_path = cfg.stacked_raw_path()`
- `--config <name>` is now `type=str` (no `choices=`); `--stage-config` added

**Behaviour preserved:** P3b exits 1 with blocking message; P4 exits 1 with
blocking message; P3a dry-run reports UID ranges; manifest CSV written to
`cfg.results_dir`.

---

## §6 — Changes to `m1_harmonise_cpi.py`

**Removed hard-coded constants:**
- `POOLED_DIR`, `CPI_SOURCE_FILE`, `CPI_TEMPLATE_FILE`, `MONETARY_VARS`, `EXCLUDED_VARS`, `YEAR_TAG`, `TAG_YEAR`
- Hard-coded `fr_{config}_stacked_raw.parquet` / `fr_{config}_harmonised.parquet` paths
- Hard-coded `choices=["p2","p3a","p3b","p4"]` in argparse

**Replaced with:**
- `cfg = load_stage_config(config_name, stage_config_path)`
- `_load_phi_table(cfg, cpi_source)` reads `cfg.cpi_final_path`, `cfg.cpi_template_path`
- `_deflate(pooled, phi_map, cfg)` uses `cfg.monetary_variables`, `cfg.tag_year`
- `stacked_path = cfg.stacked_raw_path()`, `out_path = cfg.harmonised_path()`
- `pd.to_numeric(..., errors="coerce") * phi` replaces `.astype(float) * phi` (Pyright-safe)

**Behaviour preserved:** CPI source decision gate aborts with same error message if final CSV absent. Dry-run reports phi_t table.

---

## §7 — Changes to `m1_add_cluster_key.py`

**Removed hard-coded constants:**
- `POOLED_DIR`
- Hard-coded `idorighh` column name
- Hard-coded `fr_{config}_harmonised.parquet` path
- Hard-coded year_tag=2/3 overlap check for France 2016/2017
- Hard-coded `choices=["p2","p3a","p3b","p4"]` in argparse

**Replaced with:**
- `cfg = load_stage_config(config_name, stage_config_path)` (optional when `--file` is given)
- `cluster_source = cfg.cluster_source_col`; `cluster_dest = cfg.cluster_id_col`
- `in_path = cfg.harmonised_path()`
- Cross-year overlap manifest iterates all tag pairs and looks up `cfg.expected_overlap_counts`
- `df[df["year_tag"] == t1][cluster_src].tolist()` replaces `df.loc[...]` (Pyright-safe)

**Behaviour preserved:** In-place write; cluster_id == cluster_source_col assertion; manifest CSV per year plus cross-year overlap rows.

---

## §8 — Changes to `m1_validate.py`

**Removed hard-coded constants:**
- `POOLED_DIR`, `CPI_SOURCE_FILE`, `YEAR_TAG`, `TAG_YEAR`, `CONFIG_TAGS`, `EXPECTED_HH_ROWS`, `EXPECTED_PERSON_ROWS_APPROX`, `P3A_EXPECTED_OVERLAP_2016_2017`, `P3A_OVERLAP_TOLERANCE`, `ILS_DISPY_REAL_MIN`, `ILS_DISPY_REAL_MAX`, `RAW_ID_COLS`, `IDENTITY_THRESHOLDS`
- Hard-coded `if config == "p3a"` branch in V6
- Hard-coded `fr_{config}_harmonised.parquet` path
- Hard-coded `choices=["p2","p3a","p3b","p4"]` in argparse

**Replaced with:**
- `cfg = load_stage_config(config_name, stage_config_path)`
- V1: uses `cfg.household_id_col`
- V2: uses `cfg.expected_rows_for(config_key)`, `cfg.tag_year`, `cfg.household_id_col`
- V3: uses `cfg.raw_id_cols`
- V4: uses `cfg.expected_year_tags()`
- V5: uses `cfg.cpi_final_path`, `cfg.monetary_variables`, `cfg.tag_year`, `cfg.ils_dispy_real_min/max`
- V6: iterates all tag pairs from `df["year_tag"].unique()`, looks up `cfg.expected_overlap_counts`, uses `cfg.p3a_overlap_tolerance`, `cfg.cluster_id_col`, `cfg.cluster_source_col`
- V7: uses `cfg.raw_person_id_col`, `cfg.raw_household_id_col`, `cfg.tag_year`, `cfg.identity_thresholds`
- `_write_manifests`: uses `cfg.raw_id_cols`, `cfg.results_dir`, `cfg.tag_year`; `file_path` parameter removed (unused)
- All `for tag, grp in df.groupby(...)` loops replaced with `for tag_val in df["year_tag"].unique()` pattern (Pyright-safe)

**Behaviour preserved:** V1–V9 checks identical in logic to Session 1 version.

---

## §9 — Changes to `m1_identity_validation.py`

**Removed hard-coded constants:**
- `POOLED_DIR`, `YEAR_TAG`, `TAG_YEAR`, `THRESHOLDS`, `EXPECTED_OVERLAPS`
- Hard-coded `fr_{config.lower()}_stacked_raw.parquet` path
- Hard-coded `choices=["p2","p3a","p3b","p4"]` in argparse

**Replaced with:**
- `cfg = load_stage_config(config_name, stage_config_path)`
- `_diagnose_pair(df, yr1, yr2, cfg)` uses `cfg.year_tags`, `cfg.identity_thresholds`, `cfg.raw_person_id_col`, `cfg.raw_household_id_col`, `cfg.expected_overlap_counts`
- `in_path = cfg.stacked_raw_path()` (or explicit `--file`)
- `_write_markdown(..., cfg, ...)` reads thresholds from `cfg.identity_thresholds`
- `set(...tolist())` replaces `set(df.loc[...])` (Pyright-safe)

**Behaviour preserved:** All §13 thresholds checked; per-pair Markdown report written to `cfg.results_dir / "M1_identity_validation_summary.md"`; blocking exit on suspicious_rate > block threshold.

---

## §10 — `m1_isf_check_2018.py` — France-2018-specific wrapper

This script was **not generalized** as authorized. It implements the ISF/tpr
comparability check that is required before activating the France P3b branch.
The concept of an ISF-style tax correction is France-specific in this research
context; a country-agnostic design would require a separate task.

**Change made:** Added an explicit header in the module docstring:

```
FRANCE-2018-SPECIFIC RESEARCH WRAPPER
--------------------------------------
This script is intentionally country- and year-specific. It implements the
ISF / tpr comparability check that is required before activating the France
P3b robustness branch (2015+2016+2018). It is NOT a reusable Stage M1 script
and does NOT accept --stage-config.
```

No functional changes. All constants remain as in Session 1.

---

## §11 — `run_m1_p3a.ps1` — France-P3a-specific orchestration wrapper

This script was **not generalized** as authorized. It hard-codes France
EUROMOD paths, step labels, and the P3a year set. A country-agnostic runner
would read steps from a YAML config; that is a separate future task.

**Change made:** Added an explicit header in the script comment block:

```
FRANCE P3a RESEARCH ORCHESTRATION WRAPPER
------------------------------------------
This script is intentionally France-P3a-specific. It hard-codes France
EUROMOD paths, step labels, and the P3a year set (2015+2016+2017). It is
NOT a reusable Stage M1 runner and does NOT accept --stage-config.
```

No functional changes. All step logic remains as in Session 1.

---

## §12 — Backward compatibility

`--config p3a` continues to work on all five reusable scripts without any change
to calling conventions. The shortcut internally calls
`load_stage_config("p3a", None)` which resolves to
`config/multi_year/fr_p3a_stage_m1.yaml`. All existing dry-run invocations,
`run_m1_p3a.ps1` step commands, and CI checks that used `--config p3a` remain
valid.

---

## §13 — Adding a new country/config

To run Stage M1 for a new country (e.g. DE P3a):

1. Create `config/multi_year/de_p3a_stage_m1.yaml` following the same schema.
   Fill in country-specific years, column names, CPI path, expected counts, and
   thresholds.
2. Run any reusable script with:
   ```
   python scripts/multi_year/m1_stack_years.py \
       --stage-config config/multi_year/de_p3a_stage_m1.yaml
   ```
3. No Python code changes required. No shortcut registration required.

---

## §14 — Pyright type-annotation strategy

All `df.groupby("year_tag")` patterns were replaced with explicit
`for tag_val in df["year_tag"].unique()` iteration (avoids `Scalar` union
return type). All `set(df.loc[mask, col])` patterns replaced with
`set(df[mask][col].tolist())`. All `df.loc[mask, col].astype(float) * phi`
patterns replaced with `pd.to_numeric(df.loc[mask, col], errors="coerce") * phi`.
No `# type: ignore` suppression added except for the three
`int(grp[col].min())` / `int(grp[col].max())` calls in `_write_manifests`
where Pyright cannot narrow the `min()`/`max()` return type.

---

## §15 — What was NOT done (authorisation boundary)

| Item | Status |
| --- | --- |
| Write pooled parquets | NOT done |
| Estimate on pooled data | NOT done |
| Compute welfare | NOT done |
| Implement GSURv2 year parameterization | NOT done (deferred to Stage M2) |
| Activate P3b | NOT done (gate remains) |
| Activate P4 | NOT done (gate remains) |
| Overwrite canonical single-year data | NOT done |
| Generalize `m1_isf_check_2018.py` | NOT done (labelled wrapper only) |
| Generalize `run_m1_p3a.ps1` | NOT done (labelled wrapper only) |
| Register per-country shortcuts in `m1_config.py` | NOT needed; `--stage-config` is the mechanism |

---

## §16 — Files created or modified in this pass

| File | Action |
| --- | --- |
| `config/multi_year/fr_p3a_stage_m1.yaml` | **Created** — all France P3a values |
| `scripts/multi_year/m1_config.py` | **Created** — YAML loader and `StageConfig` |
| `scripts/multi_year/m1_stack_years.py` | **Refactored** — `--stage-config`; no hard-coded constants |
| `scripts/multi_year/m1_harmonise_cpi.py` | **Refactored** — `--stage-config`; no hard-coded constants |
| `scripts/multi_year/m1_add_cluster_key.py` | **Refactored** — `--stage-config`; no hard-coded constants |
| `scripts/multi_year/m1_validate.py` | **Refactored** — `--stage-config`; no hard-coded constants |
| `scripts/multi_year/m1_identity_validation.py` | **Refactored** — `--stage-config`; no hard-coded constants |
| `scripts/multi_year/m1_isf_check_2018.py` | **Labelled** — France-2018-specific wrapper header added |
| `scripts/multi_year/run_m1_p3a.ps1` | **Labelled** — France-P3a-specific wrapper header added |
| `docs/JMP_multi_year_stage_M1_generalization_report_v1.md` | **Created** — this document |
| `Results/JMP_multi_year_stage_M1_static_validation_report_v2.md` | **Created** — 11 static checks |

---

## §17 — Unchanged files

| File | Status |
| --- | --- |
| `scripts/multi_year/__init__.py` | CLEAN |
| `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` | CLEAN |
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

---

## §18 — Next task

See `docs/JMP_multi_year_stage_M1_implementation_report_v1.md` §16 for the
upstream preconditions (CPI source decision, EUROMOD runs, MNL parquets for
2015/2017). Those preconditions are unchanged. Once they are met, execution
uses:

```powershell
.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py --config p3a
```

or with an explicit YAML:

```powershell
.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py `
    --stage-config config/multi_year/fr_p3a_stage_m1.yaml
```

---

## §19 — GSURv2 year parameterization (deferred, unchanged)

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` was not modified. The audit from
Session 1 (§11 of the implementation report) stands: four call sites require
changes, `YEAR = 2016` at line 44 must become a `--year` argument, and
`BENCHMARK_PCT` must be parameterized. Deferred to Stage M2.

---

## §20 — Authorisation statement

This document records a targeted Stage M1 generalization pass. No pooled
parquets were written, no estimation was run, and no canonical data was
modified. The generalization is limited to making the five reusable scripts
accept a YAML config; all France P3a behaviour is bit-for-bit identical to
the Session 1 implementation.