# JMP Multi-Year Stage M1 — Implementation Report

**Document:** JMP_multi_year_stage_M1_implementation_report_v1.md
**Date:** 2026-05-19
**Reference plan:** docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_implementation_plan_v2.md
**Status:** Scaffolding complete — execution blocked on upstream preconditions

---

## 1. Implementation verdict

Stage M1 scaffolding is **complete**. All six Python scripts and the
PowerShell orchestration runner have been created, pass `--help`, and produce
correct dry-run output. No canonical single-year data was modified. No pooled
parquets were written. The CPI harmonisation template was created; the final
source file was not. P3b remains blocked at the gate level (exit 1). The
implementation is ready for execution as soon as the four upstream preconditions
listed in Section 14 are resolved.

---

## 2. Files created

| File | Type | Purpose |
| --- | --- | --- |
| `scripts/multi_year/m1_stack_years.py` | Python | Stacked-ID builder |
| `scripts/multi_year/m1_harmonise_cpi.py` | Python | CPI/HICP deflation |
| `scripts/multi_year/m1_add_cluster_key.py` | Python | `cluster_id = idorighh` |
| `scripts/multi_year/m1_validate.py` | Python | V1–V9 validation checks |
| `scripts/multi_year/m1_identity_validation.py` | Python | Repeated-person/hh diagnostics |
| `scripts/multi_year/m1_isf_check_2018.py` | Python | ISF/tpr P3b gate check |
| `scripts/multi_year/run_m1_p3a.ps1` | PowerShell | Ordered execution sequence for P3a |
| `scripts/multi_year/__init__.py` | Python | Package marker |
| `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` | CSV | phi_t table template |
| `Data/processed/fr/pooled/` | Directory | Output location for pooled parquets |

---

## 3. Files modified

None. No existing files were modified. `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
was inspected and found to require no changes (see Section 5). `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
was inspected only (see Section 11).

---

## 4. Scripts created under scripts/multi_year

### m1_stack_years.py

Reads per-year MNL parquets from `Data/processed/fr/`, adds `year_tag`
(2015→1, 2016→2, 2017→3, 2018→4), computes `stacked_hh_uid = year_tag * B + idhh`
and `stacked_person_uid = year_tag * B + idperson` with B = 10^11, preserves
`idorighh`, `idorigperson`, `idhh`, `idperson`, and writes
`Data/processed/fr/pooled/fr_p{config}_stacked_raw.parquet`.

CLI: `--config {p2,p3a,p3b,p4}`, `--dry-run`, `--verbose`.

P3b and P4 are guarded at the argument-parsing level: P3b raises `RuntimeError`
immediately (with `--dry-run` or without), requiring the ISF memo at
`Results/M1_ISF_tpr_comparability_check_2018.md` to conclude "proceed with P3b"
before the block is lifted. P4 is similarly blocked as not a priority.

The stacking writes a `Results/M1_stacked_id_manifest_<UTC>.csv` with per-year
row counts, idhh/idperson maxima, and stacked UID ranges.

### m1_harmonise_cpi.py

Reads `Data/external/cpi_hicp_fr_harmonisation.csv`, deflates each monetary
variable listed in §8 of the plan by `{var}_real = {var} * phi_t`, writes
`Data/processed/fr/pooled/fr_p{config}_harmonised.parquet`. Nominal columns are
untouched. Aborts with a clear error if the CPI source file does not exist,
enforcing the §7 decision requirement. Writes `Results/M1_cpi_harmonisation_check_<UTC>.csv`.

CLI: `--config`, `--stacked-file`, `--cpi-source {hicp,insee}`, `--dry-run`, `--verbose`.

### m1_add_cluster_key.py

Adds `cluster_id = idorighh` (direct copy) to a harmonised pooled parquet.
Validates that `idorighh` is non-null before assignment. Operates in-place by
default; accepts `--out` for a separate output path. Writes
`Results/M1_cluster_key_check_<UTC>.csv` including the 2016∩2017 repeat-household
cross-tabulation for P3a.

CLI: `--config` or `--file`, `--out`, `--dry-run`, `--verbose`.

### m1_validate.py

Implements checks V1–V9 from §17 of the plan:

- V1: `stacked_person_uid` unique per row; `stacked_hh_uid` unique per household-year
- V2: row-count agreement (±10 tolerance against expected household-row totals)
- V3: raw-ID completeness (`idorighh`, `idorigperson`, `idhh`, `idperson` non-null)
- V4: `year_tag` set matches config
- V5: CPI deflation spot-check (100 rows per year) + plausibility range for `ils_dispy_real`
- V6: `cluster_id == idorighh`; P3a 2016∩2017 repeat-household count ≈ 8,796 (±200)
- V7: inline identity validation on pooled file (sex, age, suspicious records, hh continuity)
- V8: zero missing `gsur*` values (warns if column absent)
- V9: no `ruro` token in file path or column names

Writes `Results/M1_stacked_id_manifest_<UTC>.csv`, `Results/M1_raw_id_preservation_check_<UTC>.csv`,
`Results/M1_validation_summary_<UTC>.csv`. Exits 1 on any FAIL.

CLI: `--config`, `--file`, `--skip Vn [Vn ...]`, `--verbose`.

### m1_identity_validation.py

For each year-pair present in the stacked-raw file, identifies repeat persons
by `idorigperson`, applies the §13 thresholds (sex stability ≥99.90%, age
progression within ±1 ≥99.50%, suspicious ≤0.20% warn / >1.00% block, hh
continuity ≥97.00%), and writes `Results/M1_identity_validation_summary.md`.
Exits 1 if any pair exceeds the block threshold.

CLI: `--config` or `--file`, `--verbose`.

### m1_isf_check_2018.py

Implements the four-step §16 ISF/tpr comparability check:

1. Distribution of `tpr` in the FR_2018 RURO sample (share affected, percentiles in 2016 euros).
2. Impact on `ils_dispy`: mean and maximum |Δils_dispy/ils_dispy| for affected households.
3. `ils_dispy` comparability: quantile comparison of 2018 (with and without tpr) against 2016/2017.
4. Conclusion: one of "negligible: proceed with P3b", "non-negligible: requires adjustment", or "non-negligible: not recommended".

Writes `Results/M1_ISF_tpr_comparability_check_2018.md`. Aborts if the FR_2018
parquet is absent. Auto-detects 2016/2017 parquets for the comparability step.
The negligibility threshold is 0.5% mean relative impact on `ils_dispy`.

CLI: `--euromod-2018` (required), `--euromod-2016`, `--euromod-2017`, `--phi-2018`, `--verbose`.

### run_m1_p3a.ps1

Ten-step orchestration runner documenting the P3a execution sequence. Steps 1–5
are `[MANUAL]` with explicit TODO markers; steps 6–10 call the Python scripts via
the project `.venv`. Supports `--DryRun` (passes `--dry-run` to all scripts) and
`--StepFrom`/`--StepTo` for resumption. Aborts on any non-zero exit.

---

## 5. Changes to enhanced scripts

### enh_RURO_prep_mnl_basic.py — no changes required

The script already accepts `--year` as an optional CLI argument (line 2091,
added for metadata only). All input and output paths are controlled by explicit
required arguments (`--singles-draws`, `--couples-draws`, `--euromod-combined`,
`--out-base`). There are no hardcoded 2016 paths in the script body that block
multi-year use. No modification was made.

### enh_prepare_FR_gsur_v2.py — not modified (see Section 11)

---

## 6. CPI/HICP template status

`Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` was created with the
required columns: `year`, `price_index_source`, `index_value`, `base_year`,
`phi_t`, `source_url_or_citation`, `notes`. Rows are provided for 2015, 2016,
2017, and 2018, all with `PLACEHOLDER` values.

`Data/external/cpi_hicp_fr_harmonisation.csv` (the final authorised source file)
was **not** created. It must be filled in after the §7 CPI source decision is
documented. `m1_harmonise_cpi.py` aborts with a clear error if this file is
absent, preventing silent substitution of phi_t values.

---

## 7. UID implementation

Single base B = 10^11 is used for both household and person UIDs, as specified
in §10 of the plan:

```python
B = 10**11
stacked_hh_uid     = year_tag * B + idhh      # unique per household-year
stacked_person_uid = year_tag * B + idperson   # unique per person-year row
```

The stacking script validates that `idhh_max < B` and `idperson_max < B` for
each year before computing UIDs. The binding constraint (idperson max = 9,378,990,002
for 2016) is checked at runtime and would raise `ValueError` if violated.

Cross-year uniqueness of `stacked_person_uid` is asserted after concatenation.

---

## 8. Raw-ID preservation logic

The stacking script asserts the presence and non-nullity of all four raw ID
columns (`idorighh`, `idorigperson`, `idhh`, `idperson`) before writing the
pooled file. The assertion runs per-year in `_add_stacked_ids()` before any
UID computation, so a missing column raises a clear `KeyError` with the year
and column name identified.

The manifest (`M1_stacked_id_manifest_<UTC>.csv`) includes a `raw_id_null_count`
column for each year, providing a permanent audit record that raw IDs were
non-null at stacking time.

---

## 9. cluster_id implementation

`cluster_id = idorighh` is added as a direct copy with no encoding.
The `m1_add_cluster_key.py` script:

1. Asserts `idorighh` is present in the harmonised parquet.
2. Asserts `idorighh` is non-null (raises `ValueError` with null count if not).
3. Assigns `df["cluster_id"] = df["idorighh"]`.
4. Asserts `(df["cluster_id"] == df["idorighh"]).all()` before writing.
5. Writes `M1_cluster_key_check_<UTC>.csv` with per-year `unique_idorighh`,
   `unique_cluster_id`, and `cluster_id_eq_idorighh` columns, plus the 2016∩2017
   repeat-household overlap count for P3a.

---

## 10. Validation checks implemented

All V1–V9 checks from §17 of the plan are implemented in `m1_validate.py`.
V10 (P3b ISF check) is enforced as a gate condition in `m1_stack_years.py`
rather than as a post-hoc validation — P3b stacking is refused outright until
the ISF memo exists and concludes "proceed". This is a stronger guard than a
validation check.

V5 (CPI deflation correctness) is skipped gracefully when
`cpi_hicp_fr_harmonisation.csv` does not yet exist, with a logged `SKIP` status.

V8 (GSUR coverage) warns rather than fails when no `gsur*` columns are present,
since GSUR merge is performed in the upstream prep script, not in the stacking
scripts. The warning message explicitly states the required action.

---

## 11. GSURv2 year-parameterization audit

**Audit finding: year parameterization IS required for Stage M2 use of GSURv2;
the one-line change is straightforward but is deferred to Stage M2 as instructed.**

### Current state

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` has the following hardcoded
constants at lines 44–48:

```python
YEAR = 2016
BENCHMARK_PCT = 9.725          # INSEE BDM 001688526 annual average (O9)
BENCHMARK_PROP = BENCHMARK_PCT / 100.0
BENCHMARK_TOL  = 0.010
IDF_TOL        = 0.001
```

`YEAR` is referenced at lines 165, 167, 497, 675 (four call sites):

| Line | Usage |
| --- | --- |
| 165 | `col_val = _find_year_col(df_raw, YEAR)` — selects the correct year column from the xlsx |
| 167 | Warning message: `f"year {YEAR} not found in {sh}"` |
| 497 | `lookup["year"] = YEAR` — writes the year into the output parquet |
| 675 | `col_yr = _find_year_col(df_sh, YEAR)` — second call site for year column lookup |

`BENCHMARK_PCT` (9.725, the INSEE 2016 unemployment rate benchmark) is used in
`_validate_national_rate()` at line 614. For 2015 and 2017, this must also change
to the respective annual average (2015: ~10.35%, 2017: ~9.4% — exact values
require INSEE BDM series 001688526 retrieval).

`OUT` (line 42) is hardcoded to `FR_gsur_ruro_v2_stageA.parquet`. For multi-year
runs, this should be parameterised or a year-suffixed file should be written.

### Required changes for Stage M2 (one-line edit + benchmark lookup)

The `_find_year_col()` function (line 109) is already year-generic — it accepts
`year: int` as a parameter. The refactor needed is:

1. Replace `YEAR = 2016` with `argparse` argument `--year` (int, required).
2. Replace `BENCHMARK_PCT = 9.725` with a lookup from a year→benchmark CSV or
   inline dict (requires INSEE BDM values for 2015 and 2017 from Step 1c of
   `run_m1_p3a.ps1`).
3. Optionally parameterise `OUT` to include the year in the filename, or accept
   `--out` as a CLI argument.

### Stage M1 impact

Stage M1 does not require `enh_prepare_FR_gsur_v2.py` to be run for 2015 or
2017. GSUR v1 (`FR_gsur_ruro.parquet`) covers 2015, 2017, and 2018 and is
sufficient for Stage M1 stacking and validation. The GSURv2 year parameterization
is a Stage M2 prerequisite, not a Stage M1 prerequisite.

The `run_m1_p3a.ps1` Step 5 documents this deferred status with an explicit
note: the GSURv2 `--year` argument must be implemented before that step can run.

---

## 12. Dry-run tests performed

All dry-run tests were executed and passed.

| Test | Command | Outcome |
| --- | --- | --- |
| p3a stack dry-run | `m1_stack_years.py --config p3a --dry-run` | Exit 0; reports 3 inputs missing, correct UID ranges |
| p3b stack dry-run (blocked) | `m1_stack_years.py --config p3b --dry-run` | Exit 1; blocked with ISF-check message |
| harmonise dry-run | `m1_harmonise_cpi.py --config p3a --dry-run` | Exit 0; reports CPI file absent (§7 decision pending) |
| cluster key dry-run | `m1_add_cluster_key.py --config p3a --dry-run` | Exit 0; reports harmonised parquet absent |
| --help on all 6 scripts | all | Exit 0 |

Dry-run output confirmed:
- Correct B=10^11 UID ranges for each year-tag
- Correct planned output paths
- Correct blocking messages citing the relevant plan sections
- No files written

---

## 13. What was not executed

Per the authorization constraints:

- No pooled parquets written (P3a, P3b, or P4)
- No pooled MNL estimation parquets produced
- No estimation run of any kind
- No welfare computation or scaffolding
- No canonical model promotion
- No GSUR Stage B
- No final `cpi_hicp_fr_harmonisation.csv` (template only)
- No GSURv2 year parameterization implemented
- No changes to `estimation_spec_ruro_occ_M0.yaml` or any estimation spec
- No changes to `enh_RURO_estimate_FR.py`, `gamspy_estimation_vectorized.py`, or `RURO_post_estimation_styled.py`
- No changes to `outputs/` directories
- No changes to `enh_prepare_FR_gsur_v2.py`

---

## 14. What remains blocked

| Item | Blocking condition |
| --- | --- |
| P3a stacking execution | MNL parquets for 2015 and 2017 absent (EUROMOD runs + prep script required) |
| P3a harmonisation | `cpi_hicp_fr_harmonisation.csv` absent (§7 CPI source decision required) |
| P3b activation | `M1_ISF_tpr_comparability_check_2018.md` absent; FR_2018 EUROMOD output required |
| GSURv2 for 2015/2017 | `enh_prepare_FR_gsur_v2.py` year parameterization not implemented; Eurostat denominator files absent |
| Pooled estimation | Requires pooled parquet + cluster-robust SE wrapper + pooled estimation spec (none written) |
| Welfare scaffolding | Not authorised in Stage M1 |
| P4 | Not a priority; no authorisation given |

---

## 15. Whether Stage M1 scaffolding is ready

**Yes.** All scripts specified in §18 of the plan have been created. All pass
`--help`. Dry-run mode works correctly for all scripts. The P3b gate enforces
the ISF check requirement with a hard block. The CPI source decision gate
prevents silent phi_t substitution. Raw-ID preservation and UID computation are
implemented exactly as specified in §§10–11.

The scaffolding is ready for execution once the four upstream preconditions are
met: (1) CPI source decision made and CSV written, (2) EUROMOD runs for FR_2015
and FR_2017 completed, (3) `enh_RURO_prep_mnl_basic.py` run for 2015 and 2017,
(4) Eurostat denominators and INSEE benchmark downloaded.

---

## 16. Exact next task

**Next task: resolve the four Stage M1 preconditions.**

1. **CPI source decision (§7).** Retrieve INSEE IPC series or formally adopt
   EUROMOD HICP. Fill in `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv`
   and save as `Data/external/cpi_hicp_fr_harmonisation.csv` with the authorised
   phi_t values. Document the decision in the JMP draft as specified in §7.

2. **Eurostat + INSEE acquisition (§15).** Run a single Eurostat API call for
   `lfst_r_lfsd2pop` and `lfst_r_lfp2acedu` with `startPeriod=2015&endPeriod=2017`.
   Retrieve INSEE BDM series 001688526 annual averages for 2015 and 2017.
   Save to `Data/external/` as specified in `run_m1_p3a.ps1` Step 1.

3. **EUROMOD runs for FR_2015 and FR_2017 (§3).** Manual EUROMOD UI steps.
   Output to separate multi-year directories on Z: drive (not overwriting existing
   2016 canonical output).

4. **MNL parquets for 2015 and 2017 (§3).** Run `enh_RURO_prep_mnl_basic.py`
   for each year with explicit `--singles-draws`, `--euromod-combined`, and
   `--out-base` arguments (see `run_m1_p3a.ps1` Step 4 for the exact command template).

Once all four are complete, execute `run_m1_p3a.ps1` starting from Step 6 (or
use `--StepFrom 6`).