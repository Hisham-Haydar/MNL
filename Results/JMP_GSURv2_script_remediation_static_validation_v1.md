# JMP GSURv2 Script Remediation — Static Validation Report v1

*France 2014–2015–2016 | v1 | 2026-05-20*

Authorization reference: `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` §14 V4

---

## Validation scope

All checks in this report are static or import-time only. The script
was NOT invoked with `--opportunity-year` for any year. No output
parquet was written. No MNL parquet was touched.

---

## V1 — No parquet written

**Verdict: PASS**

No `to_parquet()` call was made. No file matching
`FR_gsur_ruro_v2_stageA_y*.parquet` exists in `Data/external/` prior
to this remediation. Script was not run with `--opportunity-year`.

---

## V2 — No MNL parquet modified

**Verdict: PASS**

`git diff --stat HEAD` shows changes only to:
- `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
- `config/multi_year/fr_p3a_stage_m1.yaml`

No parquet file under `Data/processed/` or `Data/external/` was
touched.

---

## V3 — `--opportunity-year` accepted by argparse

**Verdict: PASS**

Command: `python scripts/enhanced/enh_prepare_FR_gsur_v2.py --help`

Output (relevant excerpt):
```
usage: enh_prepare_FR_gsur_v2.py [-h] --opportunity-year YEAR

Stage A GSUR lookup builder — parameterised by opportunity year.

options:
  -h, --help            show this help message and exit
  --opportunity-year YEAR
                        Opportunity year for GSURv2 construction (2014, 2015,
                        or 2016).
```

`--opportunity-year` is listed as a required argument. `--help` exits
0 and writes no output parquet (standard argparse behaviour).

---

## V4 — V4a: Import without error

**Verdict: PASS**

Command:
```
python -c "import scripts.enhanced.enh_prepare_FR_gsur_v2; print('IMPORT: OK')"
```

Output: `IMPORT: OK`

No `ImportError`, no `ModuleNotFoundError`, no `SyntaxError`.

---

## V5 — V4b: `--help` lists `--opportunity-year`

**Verdict: PASS**

Confirmed by V3 output above. The `--opportunity-year YEAR` argument
appears in the help text with the correct metavar and description.

---

## V6 — V4c: Year-tagged path templates present in source

**Verdict: PASS**

Source-inspection check via import-time string scan:

| Template string | Present |
|-----------------|---------|
| `FR_gsur_ruro_v2_stageA_y{YEAR}.parquet` | YES |
| `FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json` | YES |
| `lfst_r_lfsd2pop_FR_{YEAR}.tsv` (C3) | YES |
| `lfst_r_lfp2acedu_FR_{YEAR}.tsv` (C4) | YES |
| `insee_001688526_{YEAR}.csv` (C5) | YES |
| `FR_gsur_ruro_v2_stageA.parquet` (hardcoded — must be absent) | ABSENT |
| `OUT     = None` (module-level) | YES |
| `SIDECAR = None` (module-level) | YES |

All 14 C7 sidecar fields confirmed present in source:
`opportunity_year`, `gsur_column_name`, `output_path`, `input_d2`,
`input_d1`, `input_unemployment_workbook`, `input_benchmark_csv`,
`benchmark_pct`, `nuts_vintage`, `idf_parity_difference`,
`benchmark_difference_pct`, `row_count`, `build_timestamp`,
`script_version`.

Check command:
```
python -c "
import pathlib
src = pathlib.Path('scripts/enhanced/enh_prepare_FR_gsur_v2.py').read_text(encoding='utf-8')
assert 'FR_gsur_ruro_v2_stageA_y{YEAR}.parquet' in src
assert 'FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json' in src
assert '\"FR_gsur_ruro_v2_stageA.parquet\"' not in src
assert 'OUT     = None' in src
assert 'SIDECAR = None' in src
assert 'lfst_r_lfsd2pop_FR_{YEAR}.tsv' in src
assert 'lfst_r_lfp2acedu_FR_{YEAR}.tsv' in src
assert 'insee_001688526_{YEAR}.csv' in src
for field in ['opportunity_year','gsur_column_name','output_path','input_d2',
              'input_d1','input_unemployment_workbook','input_benchmark_csv',
              'benchmark_pct','nuts_vintage','idf_parity_difference',
              'benchmark_difference_pct','row_count','build_timestamp','script_version']:
    assert f'\"' + field + '\"' in src
print('PATH-TEMPLATE CHECK: ALL PASS')
"
```

Output: `PATH-TEMPLATE CHECK: ALL PASS`

---

## V7 — Overall static validation

**Verdict: PASS**

| Check | Result |
|-------|--------|
| V1 — No parquet written | PASS |
| V2 — No MNL parquet modified | PASS |
| V3 — `--opportunity-year` accepted | PASS |
| V4a — Import without error | PASS |
| V4b — `--help` lists `--opportunity-year` | PASS |
| V4c — Path templates in source | PASS |
| V4c — C7 sidecar fields in source | PASS |

All seven checks PASS. The C1–C7 parameterisation is structurally
complete and consistent with the authorization §14 V4 requirements.

The script is ready for construction authorization (next stage).
Construction authorization will perform the empirical value-identity
regression and write the first parquet for a specific year.