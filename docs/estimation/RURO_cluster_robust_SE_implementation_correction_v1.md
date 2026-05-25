# RURO Cluster-Robust SE Implementation Correction v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Correction verdict

**All five corrections applied. GA17 re-confirmed.**

All 17 smoke-test checks pass (C1–C17) after applying the corrections.
The regenerated static validation report is at
`Results/RURO_cluster_robust_SE_static_validation_v1.md`.

---

## 2. Files inspected

| File | Reason inspected |
|------|-----------------|
| `scripts/enhanced/estimation_utils.py` | Cluster-key strictness in both `precompute_data_singles` and `precompute_data_couples` |
| `scripts/enhanced/run_cluster_robust_se.py` | C2 CLI-help check; GA17 wording; next-gate wording |
| `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md` | GA17 wording and next-gate wording in sections 1 and 17 |
| `Results/RURO_cluster_robust_SE_static_validation_v1.md` | Regenerated output — inspected after re-run |
| `Results/smoke_test_stdout.txt` | Untracked stdout capture — archived |

---

## 3. Untracked-output handling

`Results/smoke_test_stdout.txt` (PowerShell stdout capture from a prior
debugging run, UTF-16 LE encoded) was moved to
`Results/diagnostics/smoke_test_stdout_20260521.txt`.

The `Results/diagnostics/` directory is committed as part of this correction.
The original path `Results/smoke_test_stdout.txt` no longer exists.

---

## 4. C2 CLI-help validation

C2 was absent from the v1 smoke test. Added to `run_cluster_robust_se.py`
in `run_smoke_test()` between C1 and C3:

```python
try:
    parser = build_parser()
    parser.parse_args(["--spec", str(spec_path), "--parquet", str(parquet_path), "--help"])
    results["checks"]["C2_cli_help_works"] = {"passed": True, ...}
except SystemExit as exc:
    c2_pass = (exc.code == 0)
    results["checks"]["C2_cli_help_works"] = {"passed": c2_pass, ...}
```

`argparse` raises `SystemExit(0)` on `--help`; the except clause treats
exit code 0 as PASS. C2 appears in the regenerated Markdown report between
C1 and C3. C2 PASS confirmed in regenerated report (exit code 0).

Added `("C2", "CLI --help works", "C2_cli_help_works")` to `check_rows`
in `_write_md_report()`.

---

## 5. GA17 wording correction

**Before (v1):**
- `results["GA17_status"] = "CONFIRMED"`
- `results["final_statements"]["GA17"] = "CONFIRMED"`
- Log: `"All required smoke-test checks passed. GA17 can be recorded as CONFIRMED."`
- Report heading: `## GA17 final status: **CONFIRMED**`

**After (correction v1):**
- `results["GA17_status"] = "CONFIRMED"` (internal sentinel — unchanged for exit-code logic)
- `results["final_statements"]["GA17"] = "smoke-test callability: CONFIRMED"`
- Log: `"GA17 infrastructure smoke-test callability: CONFIRMED."`
- Log: `"Note: T4/T5 robust-SE diagnostics using converged theta and true Hessian remain post-estimation checks."`
- Report heading: `## GA17 final status: **smoke-test callability: CONFIRMED**`
- Added T4/T5 note row to the report's final-status table

**Rationale:** The smoke test confirms the score interface, meat assembly,
and sandwich call are correct at initial_values. It does not confirm
T4 (SE positivity with the correct Hessian) or T5 (robust vs. Hessian
comparison), which require converged theta. The v1 label "CONFIRMED" without
qualification overstated the scope of the clearance.

---

## 6. Next-gate correction

**Before (v1):**
`"next_gate": "SA2 (requires full PASS on GA1-GA17 plus estimation convergence verification)"`

**After (correction v1):**
`"next_gate": "GA17 clearance addendum; if cleared, pooled-estimation execution authorization memo"`

Applied in:
- `run_cluster_robust_se.py`: `results["final_statements"]["next_gate"]`
- `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md`: section 1 and section 17

**Rationale:** SA2 is not the immediate next gate. The correct sequencing
is: smoke-test clearance → GA17 clearance addendum → if cleared,
pooled-estimation execution authorization memo.

---

## 7. Cluster-key strictness correction

**`precompute_data_singles`** (already corrected before this document):

The old terse `logger.warning("...; using 'idhh' as cluster_ids fallback")`
was replaced with an explicit multi-line warning that names the fallback as
NOT valid for pooled P3a GA17 clearance, states the distinction between
`idhh` (household-year key) and `idorighh` (cross-year cluster key), and
instructs the user to ensure `idorighh` is present in the P3a pooled parquet.

**`precompute_data_couples`** (corrected in this task):

Same replacement applied. The old one-line warning
`"  [WARN] 'idorighh' column not found; using 'idhh' as cluster_ids fallback"`
was replaced with the identical explicit multi-line warning, with the
data-type label changed from "singles data" to "couples data".

Both functions now carry a four-line header comment explaining why silent
fallback is unacceptable for pooled P3a GA17 clearance:

```
# Silent fallback to idhh is NOT acceptable for GA17 clearance.
# idhh clusters at the household-year level; idorighh clusters across years.
# The fallback path is retained only for legacy single-year datasets (pre-pooling)
# and must never be silently invoked on the P3a pooled parquet.
```

The fallback path itself is retained for backwards compatibility with
legacy single-year runs (where `idhh == idorighh` holds), but it is now
loudly documented as invalid for the P3a / GA17 context.

---

## 8. Files modified

| File | Change summary |
|------|---------------|
| `scripts/enhanced/estimation_utils.py` | `precompute_data_couples`: replaced terse fallback warning with explicit multi-line warning; added four-line comment block matching `precompute_data_singles` |
| `scripts/enhanced/run_cluster_robust_se.py` | Added C2 CLI-help check between C1 and C3; corrected GA17 label to "smoke-test callability: CONFIRMED"; added T4/T5 note; corrected next-gate wording; added C2 row to `_write_md_report` |
| `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md` | Corrected GA17 label in sections 1 and 17; corrected next-gate wording in section 17; updated check count from 16 to 17 |
| `Results/RURO_cluster_robust_SE_static_validation_v1.md` | Regenerated: C2 added (PASS); GA17 label corrected; T4/T5 note added; next-gate corrected |
| `Results/diagnostics/smoke_test_stdout_20260521.txt` | Archived from `Results/smoke_test_stdout.txt` (untracked output) |

No YAML specifications, parquets, or estimation results were modified.

---

## 9. What was not executed

- Pooled estimation was not run.
- GAMSPy solver was not invoked.
- Welfare computation was not run.
- The pooled parquet was not modified.
- YAML specification files were not modified.
- Existing estimation outputs were not modified.
- Full 1,244,500-row load was not performed (bounded to 200,000 rows).
- T4 (SE positivity) and T5 (robust vs. Hessian comparison) were not run
  (require converged theta and true Hessian; deferred to post-estimation).

---

## 10. Final status

| Item | Status |
|------|--------|
| GA17 infrastructure smoke-test callability | **CONFIRMED** |
| C1–C17 (17 checks) | **ALL PASS** |
| C2 CLI-help | **PASS** (added in this correction) |
| T4/T5 post-estimation checks | DEFERRED — require converged theta |
| Cluster-key strictness (singles) | **CORRECTED** |
| Cluster-key strictness (couples) | **CORRECTED** |
| GA17 wording | **CORRECTED** |
| Next-gate wording | **CORRECTED** |
| Untracked output | **ARCHIVED** |
| Pooled estimation | NOT authorized |
| Welfare computation | NOT authorized |
| Active JMP baseline | M1-clean 2016 |
| Next gate | GA17 clearance addendum; if cleared, pooled-estimation execution authorization memo |