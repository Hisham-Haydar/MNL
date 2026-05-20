# JMP GSURv2 Script Remediation — Documentation Fix v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Fix verdict

Two targeted documentation corrections applied across two files. No
code was changed. No script was run. No parquet was written.

| # | File | Issue | Action |
|---|------|-------|--------|
| F1 | `Results/JMP_GSURv2_script_remediation_static_validation_v1.md` | Commands written as bare `python` — validated interpreter not identified | Added venv interpreter note in Validation scope; replaced `python` with `.venv\Scripts\python.exe` in all three command blocks (V3, V4a, V6) |
| F2 | `docs/JMP_GSURv2_script_remediation_report_v1.md` | §14 audit-readiness table cited external-file remediation as a single commit `df873d0` | Corrected to: files in commit `e4dd6c2`, report in commit `df873d0` |

---

## 2. Files inspected

| File | Purpose |
|------|---------|
| `docs/JMP_GSURv2_script_remediation_report_v1.md` | Subject to F2; §14 table read in full |
| `Results/JMP_GSURv2_script_remediation_static_validation_v1.md` | Subject to F1; all sections read in full |

No code files were read. No data files were read. No scripts were run.

---

## 3. Interpreter clarification

All static validation commands in
`Results/JMP_GSURv2_script_remediation_static_validation_v1.md` were
run with the project virtual environment, not with system Python.

**Validated interpreter:** `.venv\Scripts\python.exe`
(absolute path: `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`)

**System Python** is not the validated interpreter for this project
and should not be used to run any MNL or GSURv2 scripts. The original
report omitted the venv qualifier from the three command blocks in
sections V3, V4a (V4 — V4a), and V6. This fix makes the interpreter
explicit in all three locations:

| Section | Command before fix | Command after fix |
|---------|--------------------|-------------------|
| V3 | `python scripts/enhanced/enh_prepare_FR_gsur_v2.py --help` | `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --help` |
| V4a | `python -c "import scripts.enhanced.enh_prepare_FR_gsur_v2; ..."` | `.venv\Scripts\python.exe -c "import scripts.enhanced.enh_prepare_FR_gsur_v2; ..."` |
| V6 | `python -c "import pathlib; ..."` | `.venv\Scripts\python.exe -c "import pathlib; ..."` |

A venv-interpreter note was also added to the Validation scope section
so that the interpreter is declared once at the top of the report
before any commands are listed.

---

## 4. Commit-reference clarification

The external-file remediation produced two commits, not one:

| Commit | Content |
|--------|---------|
| `e4dd6c2` | The six external files themselves: `lfst_r_lfsd2pop_FR_2014.tsv`, `lfst_r_lfp2acedu_FR_2014.tsv`, `lfst_r_lfsd2pop_FR_2015.tsv`, `lfst_r_lfp2acedu_FR_2015.tsv`, `insee_001688526_2014.csv`, `insee_001688526_2015.csv`; plus extensions to `gsur_denominator_source.txt` and `gsur_benchmark_source.txt` |
| `df873d0` | `Results/JMP_GSURv2_external_file_remediation_report_v1.md` only |

The §14 audit-readiness table in
`docs/JMP_GSURv2_script_remediation_report_v1.md` originally read:

> PASS (external-file remediation, commit `df873d0`)

This is misleading: `df873d0` is the report commit, not the data
commit. The data — the files whose presence is the actual precondition
— landed in `e4dd6c2`. The corrected entry reads:

> PASS (external-file remediation: files in commit `e4dd6c2`, report
> in commit `df873d0`)

No other commit references in either file required correction.

---

## 5. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `Results/JMP_GSURv2_script_remediation_static_validation_v1.md` | Documentation fix (F1) | Venv interpreter note added to Validation scope; `python` → `.venv\Scripts\python.exe` in V3, V4a, V6 command blocks |
| `docs/JMP_GSURv2_script_remediation_report_v1.md` | Documentation fix (F2) | §14 external-file remediation commit reference corrected to `e4dd6c2` (files) + `df873d0` (report) |
| `docs/JMP_GSURv2_script_remediation_documentation_fix_v1.md` | New file | This report |

No code was changed. No data was built.

---

## 6. Final status

Both documentation fixes are applied. The two subject files now
accurately record:

- that static validation was performed with the project venv
  (`.venv\Scripts\python.exe`), not system Python; and
- that the external-file remediation consisted of two commits —
  `e4dd6c2` for the data files and `df873d0` for the report.

All substantive content in both files (validation verdicts, check
results, C1–C7 descriptions, sidecar fields, backward-compatibility
note, audit-readiness table) is unchanged. The underlying
authorizations and naming decisions are unchanged.