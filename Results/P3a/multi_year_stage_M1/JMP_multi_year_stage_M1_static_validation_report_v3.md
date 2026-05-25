# JMP Multi-Year Stage M1 — Static Validation Report v3

**Document:** Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_static_validation_report_v3.md
**Date:** 2026-05-19
**Generalization report:** docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_report_v1.md
**Fix report:** docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_fix_report_v1.md
**Prior static validation:** Results/JMP_multi_year_stage_M1_static_validation_report_v2.md

All tests run directly from repo root using `.\.venv\Scripts\python.exe` with
no `PYTHONPATH` or `$env:PYTHONPATH` set. This validates the sys.path injection
fix (Issue 1) and the per-config YAML fix (Issue 2).

---

## Check 1 — Direct script execution works without PYTHONPATH

Invocation (no `$env:PYTHONPATH`):

```
.\.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py --config p3a --dry-run
```

Previously produced `ModuleNotFoundError: No module named 'scripts.multi_year'`.

After fix, output:

```
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml
...
No parquet written (dry-run mode).
```

Exit code: 0.

The `_SCRIPT_REPO` injection block was verified present in all five scripts by
code inspection. `m1_config.py` requires no such fix (it is imported as a
module, not run directly).

**Result: PASS**

---

## Check 2 — All five reusable scripts expose `--help` at exit 0

```
m1_stack_years.py        --help  → exit 0
m1_harmonise_cpi.py      --help  → exit 0
m1_add_cluster_key.py    --help  → exit 0
m1_validate.py           --help  → exit 0
m1_identity_validation.py --help → exit 0
```

All five show both `--config` and `--stage-config` in their usage line.

**Result: PASS**

---

## Check 3 — `--config p2` resolves to the P2 YAML and produces P2 outputs

```
m1_stack_years.py --config p2 --dry-run  → exit 0
```

Output confirms:
- `Config YAML: ...config/multi_year/fr_p2_stage_m1.yaml`
- `years=[2015, 2016]`
- UID ranges for tags 1–2 only (no tag 3)
- Planned output `fr_p2_stacked_raw.parquet`

Previously: `years=[2015, 2016, 2017]` and `fr_p3a_stacked_raw.parquet` (wrong).

**Result: PASS**

---

## Check 4 — `--config p3a` is unchanged from Session 2

```
m1_stack_years.py --config p3a --dry-run  → exit 0
```

Output confirms (identical to v2 Check 3):
- `Config YAML: ...config/multi_year/fr_p3a_stage_m1.yaml`
- `years=[2015, 2016, 2017]`
- UID ranges `[1×10^11+1 to 4×10^11−1]` for tags 1–3
- Planned output `fr_p3a_stacked_raw.parquet`
- No parquet written

**Result: PASS**

---

## Check 5 — `--config p3b` resolves to the P3b YAML and blocks at exit 1

```
m1_stack_years.py --config p3b --dry-run  → exit 1
```

Error message:

```
ERROR  Config 'p3b' is not authorised for execution:
P3b is blocked until Results/M1_ISF_tpr_comparability_check_2018.md
concludes 'proceed'. See §16 of the Stage M1 plan.
```

Previously: `--config p3b` was showing P3a output (`years=[2015,2016,2017]`)
instead of blocking. After fix: correctly resolves to
`config/multi_year/fr_p3b_stage_m1.yaml` (years [2015, 2016, 2018]) and the
`blocked_configs["p3b"]` gate triggers immediately.

**Result: PASS**

---

## Check 6 — `--config p4` resolves to the P4 YAML and blocks at exit 1

```
m1_stack_years.py --config p4 --dry-run  → exit 1
```

Error message:

```
ERROR  Config 'p4' is not authorised for execution:
P4 is not a priority configuration. No authorisation in Stage M1.
```

Previously: `--config p4` was showing P3a output instead of blocking. After
fix: correctly resolves to `config/multi_year/fr_p4_stage_m1.yaml`
(years [2015, 2017, 2018]) and the `blocked_configs["p4"]` gate triggers.

**Result: PASS**

---

## Check 7 — Explicit `--stage-config` path works and produces output identical to `--config p3a`

```
m1_stack_years.py \
    --stage-config config/multi_year/fr_p3a_stage_m1.yaml --dry-run  → exit 0
```

Output is identical to `--config p3a --dry-run`:
- Same YAML path displayed
- Same years, UID ranges, planned output path

**Result: PASS**

---

## Check 8 — No pooled parquets written

`Data/processed/fr/pooled/` contains no `.parquet` files.

| Expected absent file | Present |
| --- | --- |
| `Data/processed/fr/pooled/fr_p2_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3b_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p4_stacked_raw.parquet` | **NO** |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | **NO** |

`git status --short -- Data/processed/` returns clean.

**Result: PASS**

---

## Check 9 — No estimation or welfare outputs written

`git status --short -- outputs/ scripts/enhanced/` returns clean.

| Expected absent output | Present |
| --- | --- |
| Any file under `outputs/estimates/` (new) | **NO** |
| Any file under `outputs/post_estimation/` (new) | **NO** |
| Any welfare or policy-simulation output | **NO** |

**Result: PASS**

---

## Check 10 — Canonical single-year files and data unchanged

`git status` confirms the following are clean:

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
| `config/multi_year/fr_p3a_stage_m1.yaml` | CLEAN |

**Result: PASS**

---

## Final: PASS / FAIL for Stage M1 generalization (post-fix)

**PASS**

All 10 static checks pass. Both blockers identified in the post-v2 review have
been resolved:

- **Issue 1 (sys.path)**: All five reusable scripts now self-inject the repo
  root into `sys.path` and run correctly without `PYTHONPATH` set.
- **Issue 2 (shortcut map)**: Each `--config` shortcut now resolves to its own
  YAML. P2 produces P2 outputs; P3b and P4 block correctly with their own gate
  messages.

The France P3a golden path is unchanged. `run_m1_p3a.ps1` will function
correctly without any `PYTHONPATH` change because the scripts are now
self-contained.

**Stage M1 generalization is complete and verified.**