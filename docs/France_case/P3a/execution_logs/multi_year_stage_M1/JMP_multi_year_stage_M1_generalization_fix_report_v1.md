# JMP Multi-Year Stage M1 — Generalization Fix Report v1

**Document:** docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_fix_report_v1.md
**Date:** 2026-05-19
**Fixes applied to:** Stage M1 generalization work documented in
  docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_report_v1.md
**Prior validation:** Results/JMP_multi_year_stage_M1_static_validation_report_v2.md

---

## Background

The Stage M1 generalization (Session 2) refactored five reusable scripts to be
country/year/config-agnostic and introduced a YAML config interface.
Post-review identified two real blockers before the v2 static validation could
be accepted as final.

---

## Issue 1 — Direct script execution fails with ModuleNotFoundError

### Symptom

Running any reusable script directly without manually setting `PYTHONPATH`:

```
.\.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py --config p3a --dry-run
```

produced:

```
ModuleNotFoundError: No module named 'scripts.multi_year'
```

### Root cause

Each script imports `from scripts.multi_year.m1_config import ...`, which
requires the repo root on `sys.path`. The v2 static validation tests were run
with `$env:PYTHONPATH` set to the repo root, masking the failure. The
`run_m1_p3a.ps1` orchestration wrapper does NOT set `PYTHONPATH`, so it would
have failed at every Python step.

### Fix applied

In each of the five reusable scripts, immediately before the
`from scripts.multi_year.m1_config import` line, inserted:

```python
# Ensure repo root is on sys.path so this script runs without PYTHONPATH set.
_SCRIPT_REPO = Path(__file__).resolve().parents[2]
if str(_SCRIPT_REPO) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_REPO))
```

This is idempotent: if the repo root is already on `sys.path` (e.g. when the
script is imported as a module or run from a launcher that sets `PYTHONPATH`),
the insertion is skipped.

### Files modified

- `scripts/multi_year/m1_stack_years.py` — line inserted before import
- `scripts/multi_year/m1_harmonise_cpi.py` — line inserted before import
- `scripts/multi_year/m1_add_cluster_key.py` — line inserted before import
- `scripts/multi_year/m1_validate.py` — line inserted before import
- `scripts/multi_year/m1_identity_validation.py` — line inserted before import

---

## Issue 2 — `--config p2/p3b/p4` all resolved to the P3a config

### Symptom

```
.\.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py --config p2 --dry-run
```

reported `years=[2015, 2016, 2017]` and planned output
`fr_p3a_stacked_raw.parquet` — the P3a values. All four shortcuts
(`p2`, `p3a`, `p3b`, `p4`) resolved to the same YAML.

### Root cause

The `_SHORTCUT_MAP` in `scripts/multi_year/m1_config.py` mapped all four
shortcuts to `config/multi_year/fr_p3a_stage_m1.yaml`:

```python
_SHORTCUT_MAP: Dict[str, str] = {
    "p2":  "config/multi_year/fr_p3a_stage_m1.yaml",   # wrong
    "p3a": "config/multi_year/fr_p3a_stage_m1.yaml",
    "p3b": "config/multi_year/fr_p3a_stage_m1.yaml",   # wrong
    "p4":  "config/multi_year/fr_p3a_stage_m1.yaml",   # wrong
}
```

This was a copy-paste error from the initial scaffolding pass.

### Fix applied

**Step 1 — Created three new per-config YAML files:**

| File | Years | config_name | Blocked? |
| --- | --- | --- | --- |
| `config/multi_year/fr_p2_stage_m1.yaml` | [2015, 2016] | p2 | No |
| `config/multi_year/fr_p3b_stage_m1.yaml` | [2015, 2016, 2018] | p3b | Yes — ISF gate |
| `config/multi_year/fr_p4_stage_m1.yaml` | [2015, 2017, 2018] | p4 | Yes — not a priority |

The existing `config/multi_year/fr_p3a_stage_m1.yaml` (years [2015, 2016, 2017])
was unchanged.

Each new YAML is a complete, self-contained config (all required sections
populated) so that `--stage-config <path>` works directly with any of them.

**Step 2 — Updated `_SHORTCUT_MAP` in `scripts/multi_year/m1_config.py`:**

```python
_SHORTCUT_MAP: Dict[str, str] = {
    "p2":  "config/multi_year/fr_p2_stage_m1.yaml",
    "p3a": "config/multi_year/fr_p3a_stage_m1.yaml",
    "p3b": "config/multi_year/fr_p3b_stage_m1.yaml",
    "p4":  "config/multi_year/fr_p4_stage_m1.yaml",
}
```

Also updated the module docstring to document all four shortcuts with their
year sets and block status.

### Files created or modified

- `config/multi_year/fr_p2_stage_m1.yaml` — **NEW**
- `config/multi_year/fr_p3b_stage_m1.yaml` — **NEW**
- `config/multi_year/fr_p4_stage_m1.yaml` — **NEW**
- `scripts/multi_year/m1_config.py` — `_SHORTCUT_MAP` corrected; docstring updated

---

## Verification

All smoke tests run directly without `PYTHONPATH`:

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| `--config p3a --dry-run` | years=[2015,2016,2017], `fr_p3a_stacked_raw.parquet`, exit 0 | As expected | **PASS** |
| `--config p2 --dry-run` | years=[2015,2016], `fr_p2_stacked_raw.parquet`, exit 0 | As expected | **PASS** |
| `--config p3b --dry-run` | exit 1, ISF gate message | exit 1, correct message | **PASS** |
| `--config p4 --dry-run` | exit 1, not-a-priority message | exit 1, correct message | **PASS** |
| `--stage-config config/multi_year/fr_p3a_stage_m1.yaml --dry-run` | identical to `--config p3a` | Identical | **PASS** |
| `--help` (all 5 scripts) | exit 0 | exit 0 (all 5) | **PASS** |

Full static validation: `Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_static_validation_report_v3.md`

---

## Files affected by this fix pass

### New files

- `config/multi_year/fr_p2_stage_m1.yaml`
- `config/multi_year/fr_p3b_stage_m1.yaml`
- `config/multi_year/fr_p4_stage_m1.yaml`
- `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_fix_report_v1.md` (this file)
- `Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_static_validation_report_v3.md`

### Modified files

- `scripts/multi_year/m1_config.py` — `_SHORTCUT_MAP` + docstring
- `scripts/multi_year/m1_stack_years.py` — `sys.path` injection
- `scripts/multi_year/m1_harmonise_cpi.py` — `sys.path` injection
- `scripts/multi_year/m1_add_cluster_key.py` — `sys.path` injection
- `scripts/multi_year/m1_validate.py` — `sys.path` injection
- `scripts/multi_year/m1_identity_validation.py` — `sys.path` injection

### Unchanged files

- `config/multi_year/fr_p3a_stage_m1.yaml` — not touched
- `scripts/multi_year/m1_isf_check_2018.py` — not touched
- `scripts/multi_year/run_m1_p3a.ps1` — not touched (sys.path injection in
  scripts makes PYTHONPATH setting in the wrapper unnecessary)
- All canonical single-year scripts and data — not touched