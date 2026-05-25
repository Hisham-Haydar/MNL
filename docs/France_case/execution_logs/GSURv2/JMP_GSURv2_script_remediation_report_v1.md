# JMP GSURv2 Script Remediation Report v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Remediation verdict

**COMPLETE.** All C1–C7 parameterisation changes have been applied to
`scripts/enhanced/enh_prepare_FR_gsur_v2.py`. The config change (K2
naming decision) has been applied to
`config/multi_year/fr_p3a_stage_m1.yaml`. Static validation (V4 per
authorization §14) passed on all checks. No script was invoked with
`--opportunity-year`. No parquet was written. No MNL parquet was
touched.

---

## 2. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | Parameterisation (C1–C7) | argparse, benchmark CSV read, year-tagged paths, sidecar write, import additions |
| `config/multi_year/fr_p3a_stage_m1.yaml` | Config (K2) | Removed `gsur_v2` from `variables_excluded_from_deflation` |

---

## 3. C1 — `--opportunity-year` argument

**Change:** `main()` now opens with an `argparse.ArgumentParser` block.
The `--opportunity-year` argument is type `int`, required, with
`metavar="YEAR"` and a help string listing the valid years (2014,
2015, 2016). `YEAR` is set from `args.opportunity_year` as the first
action in `main()`.

**Module-level default:** The module-level `YEAR = 2016` constant is
retained as a guard against accidental use of module globals before
`main()` runs. It is overridden unconditionally by the `global YEAR`
assignment in `main()`.

**Verification:** `--help` output lists `--opportunity-year YEAR` and
the description string. See static validation §V4b.

---

## 4. C2 — `_find_year_col` already uses `YEAR` global

**No code change required.** `_find_year_col(df_raw, YEAR)` was already
called with the module-level `YEAR` global in `load_gsur_workbook()`
(line ~169). Since `main()` sets `global YEAR` before any function
calls, all downstream callers of `_find_year_col` automatically use
the parameterised year.

---

## 5. C3 — D2 denominator path parameterised

**Change:** In `load_d2()`, the hard-coded literal
`"lfst_r_lfsd2pop_FR_2016.tsv"` was replaced with the f-string
`f"lfst_r_lfsd2pop_FR_{YEAR}.tsv"`.

**Scope:** This is the only occurrence of a year-specific D2 filename
in the script. The change is confined to a single `pd.read_csv` call.

---

## 6. C4 — D1 denominator path parameterised

**Change:** In `load_d1()`, the hard-coded literal
`"lfst_r_lfp2acedu_FR_2016.tsv"` was replaced with the f-string
`f"lfst_r_lfp2acedu_FR_{YEAR}.tsv"`.

**Scope:** Single `pd.read_csv` call; no other D1-path references in
the script.

---

## 7. C5 — BENCHMARK_PCT read from year-specific INSEE CSV

**Change:** In `main()`, after `YEAR` is set, the script reads the
year-specific INSEE CSV:

```python
benchmark_csv = EXT / f"insee_001688526_{YEAR}.csv"
bdf = pd.read_csv(benchmark_csv)
avg_row = bdf[bdf["period"].astype(str) == str(YEAR)]
BENCHMARK_PCT  = float(avg_row.iloc[0]["value_pct"])
BENCHMARK_PROP = BENCHMARK_PCT / 100.0
```

The CSV contains one `annual_average` row whose `period` field equals
the four-digit year. If the row is absent, a `ValueError` is raised
with the filename and the missing period value.

**Values at runtime:** y2014 → 9.9; y2015 → 10.025; y2016 → 9.725.
These are cross-referenced in `Data/external/gsur_benchmark_source.txt`
and the CSV files themselves.

**Module-level default:** `BENCHMARK_PCT = 9.725` and
`BENCHMARK_PROP = BENCHMARK_PCT / 100.0` are retained at module level
as guards. Both are overridden unconditionally by the `global
BENCHMARK_PCT, BENCHMARK_PROP` assignment in `main()`.

---

## 8. C6 — Year-tagged output and sidecar paths

**Change:** At module level, `OUT = EXT / "FR_gsur_ruro_v2_stageA.parquet"`
was replaced with `OUT = None` and `SIDECAR = None`. Both are set in
`main()` after `YEAR` is known:

```python
OUT     = EXT / f"FR_gsur_ruro_v2_stageA_y{YEAR}.parquet"
SIDECAR = EXT / f"FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json"
```

**Path templates:**

| YEAR | OUT | SIDECAR |
|------|-----|---------|
| 2014 | `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet` | `…y2014__sidecar.json` |
| 2015 | `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` | `…y2015__sidecar.json` |
| 2016 | `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` | `…y2016__sidecar.json` |

**Safety guard:** The `FORBIDDEN` list check in `main()` now uses
`assert OUT != f` (identity comparison), replacing the fragile
`str(OUT).endswith(f.name) or OUT != f` pattern.

---

## 9. C7 — Sidecar JSON provenance write

**Change:** After `lookup_out.to_parquet(OUT, ...)`, `main()` writes a
sidecar JSON to `SIDECAR`. The JSON contains all 14 fields required by
authorization §9:

| Field | Source |
|-------|--------|
| `opportunity_year` | `YEAR` (from argparse) |
| `gsur_column_name` | literal `"gsur"` (K2 decision) |
| `output_path` | `OUT.relative_to(REPO)` (POSIX slash) |
| `input_d2` | `f"Data/external/lfst_r_lfsd2pop_FR_{YEAR}.tsv"` |
| `input_d1` | `f"Data/external/lfst_r_lfp2acedu_FR_{YEAR}.tsv"` |
| `input_unemployment_workbook` | `"Data/external/FR_gsur.xlsx"` |
| `input_benchmark_csv` | `f"Data/external/insee_001688526_{YEAR}.csv"` |
| `benchmark_pct` | `BENCHMARK_PCT` (read from CSV at runtime) |
| `nuts_vintage` | `"NUTS2016"` |
| `idf_parity_difference` | `val["IDF_parity"]["max_abs_diff"]` |
| `benchmark_difference_pct` | `val["L5_national_benchmark"]["diff_pct"]` |
| `row_count` | `len(lookup_out)` |
| `build_timestamp` | `datetime.datetime.now(datetime.timezone.utc).isoformat()` |
| `script_version` | `git log -1 --format=%H -- <script path>` |

`script_version` falls back to `"unknown"` if the `git` call fails
(e.g. in a non-git environment). `build_timestamp` uses timezone-aware
UTC via `datetime.timezone.utc` (not the deprecated `utcnow()`).

---

## 10. K2 naming decision applied

**Active column name:** `gsur` (unchanged). The K2 decision confirmed
that the MNL column name visible to all downstream code remains `gsur`.
No rename of the column in the parquet schema was required.

**Provenance:** The sidecar JSON field `gsur_column_name: "gsur"` makes
the naming decision explicit and auditable per-build.

**Config change:** `- gsur_v2` was removed from
`variables_excluded_from_deflation` in
`config/multi_year/fr_p3a_stage_m1.yaml`. The `- gsur` entry is
retained. `gsur_v2` was a transient alias that was never merged into
any MNL parquet; removing it from the exclusion list eliminates a
dead entry and prevents confusion if a future column of that name were
added with different semantics.

---

## 11. Backward-compatibility behaviour

The script is **not backward-compatible** with the old no-argument
invocation (`python enh_prepare_FR_gsur_v2.py`). Argparse will print
a usage error and exit 2 if `--opportunity-year` is omitted, because
the argument is declared `required=True`. This is intentional: the
old default-year behaviour was the source of the provenance ambiguity
being remediated. Any caller must now explicitly state the year.

The year-invariant construction logic (aggregation, education
alignment, Y20-64 age-band selection, drgn1=9 stub handling, IDF
parity check, benchmark validation, output schema) is unchanged.

---

## 12. Tests run (static validation only)

All validation performed without invoking the script with
`--opportunity-year`. See `Results/JMP_GSURv2_script_remediation_static_validation_v1.md`
for the full seven-check report.

| Check | Result |
|-------|--------|
| V4a — import without error | PASS |
| V4b — `--help` lists `--opportunity-year` | PASS |
| V4c — path templates: OUT and SIDECAR match `y{YEAR}` pattern | PASS |
| V4c — C3 f-string (`lfst_r_lfsd2pop_FR_{YEAR}.tsv`) present | PASS |
| V4c — C4 f-string (`lfst_r_lfp2acedu_FR_{YEAR}.tsv`) present | PASS |
| V4c — C5 f-string (`insee_001688526_{YEAR}.csv`) present | PASS |
| V4c — all 14 C7 sidecar fields present in source | PASS |
| V4c — hardcoded `FR_gsur_ruro_v2_stageA.parquet` absent | PASS |
| V4c — module-level `OUT = None` present | PASS |
| V4c — module-level `SIDECAR = None` present | PASS |

---

## 13. What was NOT executed

- The script was NOT invoked with `--opportunity-year 2014`.
- The script was NOT invoked with `--opportunity-year 2015`.
- The script was NOT invoked with `--opportunity-year 2016`.
- No Stage A lookup parquet was written for any year.
- No MNL parquet was read or written.
- No canonical data path was touched.
- No O7 sign-off was performed.

Construction authorization (the memo that will authorize running the
script for y2016, performing the value-identity regression, and locking
provenance) is a separate document not produced in this remediation.

---

## 14. GSURv2 construction audit readiness

The parameterised script is now structurally ready for construction
authorization. The preconditions are:

| Precondition | Status |
|---|---|
| C1–C7 implemented | PASS (this remediation) |
| All 6 external files present | PASS (external-file remediation: files in commit `e4dd6c2`, report in commit `df873d0`) |
| Authorization memo internally consistent | PASS (final wording fix, commit `372237b`) |
| Static validation V4a/V4b/V4c all PASS | PASS (this remediation) |
| K2 naming decision applied | PASS (this remediation) |
| y2016 provenance lock plan | DEFERRED — authorization §9 specifies this as a separate document |
| Construction authorization memo | NOT YET PRODUCED — prerequisite for running script |

The next step is the construction authorization memo (§9 lock-plan
document + construction authorization), which is explicitly outside
the scope of this script remediation.