# RURO Post-Estimation Styled — General Reporting Enhancement v1

**File**: `scripts/enhanced/RURO_post_estimation_styled.py`  
**Date**: 2026-05-21  
**Status**: Implemented

---

## 1. Purpose and Scope

This document describes the general-purpose extended diagnostics layer added to
`RURO_post_estimation_styled.py` in v1 of this enhancement.  The goal is to make
the script a reusable post-estimation reporting tool that works with any RURO
estimation run, not a project-specific reporter.

No project-specific values are hard-coded: no specification names, no fixed cluster
counts, no welfare authorization gates, no country/year labels.  Every field degrades
gracefully to the sentinel string *"Not available in supplied solver artifacts"* when
input artifacts are absent.

---

## 2. Backward Compatibility

The existing command-line interface is fully preserved.  All prior invocations continue
to work unchanged:

```
python RURO_post_estimation_styled.py \
    --results-json path/to/estimation_results.json \
    --mnl-base path/to/data_base \
    --output-dir path/to/output \
    --spec-config path/to/spec.yaml
```

The new options are additive.  They activate extended diagnostics only when explicitly
supplied; the base styled HTML report is always produced first, exactly as before.

---

## 3. New CLI Options

Ten new optional arguments are added to `main()`:

| Argument | Type | Description |
|----------|------|-------------|
| `--cluster-se-json PATH` | Path | Cluster-robust SE JSON from `cluster_robust_se.py`.  Enables inference table, Hessian diagnostics, T3/T4/T5 checks. |
| `--solver-log PATH` | Path | Plain-text GAMS/CONOPT solver log.  Parsed for convergence info. |
| `--listing-file PATH` | Path | GAMS `.lst` listing file.  Parsed for RGmax, RTOL/FTOL, equations/variables/nonzeros, active bounds. |
| `--gamspy-diagnostics` | flag | Include GAMSPy/CONOPT diagnostics section.  Auto-enabled when `--listing-file` or `--solver-log` are given. |
| `--gradient-diagnostics` | flag | Compute Python likelihood gradient (score) at convergence.  Requires `--mnl-base` and `--spec-config`. |
| `--comparison-results-json PATH` | Path | Second `estimation_results.json` for parameter L∞ comparison. |
| `--comparison-label LABEL` | str | Label for the comparison run (default: "Comparison"). |
| `--cluster-col COL` | str | Cluster column name (informational; appears in report header). |
| `--report-title TITLE` | str | Custom title for the Markdown diagnostics report. |
| `--strict-report` | flag | Raise an error if critical diagnostics (Hessian condition, data checks) are unavailable. |

Extended diagnostics are produced automatically when any of the following are supplied:
`--cluster-se-json`, `--solver-log`, `--listing-file`, `--gamspy-diagnostics`,
`--gradient-diagnostics`, `--comparison-results-json`, `--strict-report`.

---

## 4. Output Artifacts

When extended diagnostics run, two files are written to the same output directory as the
styled HTML report:

| File | Description |
|------|-------------|
| `{prefix}extended_diagnostics.md` | Human-readable Markdown report (8 sections) |
| `{prefix}extended_diagnostics.json` | Machine-readable diagnostics bundle |

The Markdown report has these sections:

1. Inference Table
2. Solver Convergence Diagnostics
3. CONOPT / GAMS Solver Diagnostics
4. Python Likelihood Gradient Diagnostics
5. Hessian Diagnostics
6. Data Diagnostics
7. Comparison Run
8. Reproducibility Metadata

---

## 5. Inference Table

The inference table (`_build_enhanced_param_df`) combines parameter estimates from
`estimation_results.json` with cluster-robust SE vectors from `--cluster-se-json`:

| Column | Source |
|--------|--------|
| `param` | parameter name |
| `theta` | converged estimate (from cluster SE JSON `converged_theta` if available, else results JSON) |
| `se_hessian` | Hessian-based SE from `se_hessian_vector` |
| `se_robust` | Cluster-robust SE from `se_robust_vector` |
| `t_robust` | `theta / se_robust` |
| `p_robust` | two-tailed p-value from standard normal |
| `at_lower_bound` | from bound diagnostics object |
| `at_upper_bound` | from bound diagnostics object |
| `in_free_mask` | whether parameter is in the identified (free) block |

All SE columns are `NaN` when `--cluster-se-json` is not supplied.

---

## 6. Cluster-Robust SE Integration

The `--cluster-se-json` artifact produced by `cluster_robust_se.py` carries:

- `cluster_robust_se_artifacts.converged_theta` — canonical theta vector
- `cluster_robust_se_artifacts.se_robust_vector` — sandwich SE vector
- `cluster_robust_se_artifacts.se_hessian_vector` — Hessian-only SE vector
- `cluster_robust_se_artifacts.free_mask` — boolean mask for identified block
- `cluster_robust_se_artifacts.n_free` — number of identified parameters
- `checks.T3_cluster_count` — cluster count check
- `checks.T4_se_positivity` — SE positivity check (uses `se_free ≤ 0`)
- `checks.T5_robust_vs_hessian` — ratio test
- `checks.PE6_true_hessian` — condition number, shape

When this artifact is present, `_extract_extended_hessian_diagnostics` reports the
VCV condition number, near-singular warning, and SE ranges directly from the artifact.

---

## 7. GAMS/CONOPT Solver Diagnostics

Fields parsed from the GAMS `.lst` listing file (`--listing-file`):

| Field | GAMS source |
|-------|-------------|
| `gams_solver` | header (e.g. CONOPT4) |
| `solver_status` | SOLVER STATUS line |
| `model_status` | MODEL STATUS line |
| `equations` | model statistics block |
| `variables` | model statistics block |
| `nonzeros` | model statistics block |
| `max_infeasibility` | infeasibility report |
| `solve_time_s` | Resource usage line |
| `generation_time_s` | Generation time line |
| `rgmax` | `RGmax =` line (CONOPT reduced gradient norm) |
| `conopt_rtol` | `RTOL =` line (optimality tolerance) |
| `conopt_ftol` | `FTOL =` line (feasibility tolerance) |
| `rgmax_below_tol` | derived: `rgmax ≤ conopt_rtol` |
| `active_bounds` | count of active/binding bound lines |
| `solver_warnings` | `*** WARNING` lines (capped at 10) |

If `--listing-file` is not supplied, all fields report
*"Not available in supplied solver artifacts"*.

**Best practice**: configure the estimator to save the GAMS listing file and solver log
for every run so these fields are always populated.  The current GAMSPy interface stores
high-level status (`SolveStatus`, `ModelStatus`) in `estimation_results.json`, but
RGmax and tolerances require the listing file.

---

## 8. Python Likelihood Gradient vs. CONOPT Reduced Gradient

Two distinct gradient quantities appear in the extended report:

**CONOPT RGmax** (Section 3 of the Markdown report):
- Produced internally by the GAMS/CONOPT solver
- Measures how far the solver's reduced gradient is from zero at the final iterate
- Available only from the GAMS listing file (`--listing-file`)
- Directly comparable to `conopt_rtol`

**Python likelihood gradient** (Section 4 of the Markdown report):
- Computed by the RURO Python engine via central-difference numerical differentiation
  of the log-likelihood function `∂ log L / ∂ θ` at the converged parameter vector
- Enabled by `--gradient-diagnostics` (also requires `--mnl-base` and `--spec-config`)
- Reports: `‖∇‖₂`, `‖∇‖∞`, parameter with largest component, top-10 by magnitude
- **Never conflated with CONOPT RGmax** — the two quantities are computed differently,
  operate on different function formulations, and are reported in separate sections

Both should be near zero at a local optimum, but they measure different things.  The
Python gradient is useful for verifying that the Python-side log-likelihood is also
at a stationary point, independent of the GAMS solver.

---

## 9. Hessian Diagnostics

`_extract_extended_hessian_diagnostics` reports:

| Field | Description |
|-------|-------------|
| `condition_number` | VCV condition number (prefers cluster SE JSON `PE6_true_hessian`) |
| `near_singular_warning` | True if `condition_number > 1e12` |
| `n_free` | number of parameters in identified block |
| `hessian_shape_free` | shape of the free Hessian block |
| `se_hessian_min/max` | range of positive Hessian SEs |
| `se_robust_min/max` | range of positive robust SEs |
| `t5_robust_vs_hessian` | T5 check dict from cluster SE JSON |

Source preference: cluster SE JSON (`PE6_true_hessian`) > `estimation_results.json`
metadata `standard_errors` block > unavailable.

---

## 10. Data Diagnostics

Populated from the `checks` block of `--cluster-se-json`:

| Check | Key | Description |
|-------|-----|-------------|
| T3 | `T3_cluster_count` | Number of clusters found; checks minimum cluster size requirement |
| T4 | `T4_se_positivity` | SE positivity: uses `se_free ≤ 0` (not `< 0`); passes if `n_nonpositive == 0` |
| T5 | `T5_robust_vs_hessian` | Ratio of robust to Hessian SE; flags large inflation |
| PE3 | `PE3_data_loaded` | Data shape check at SE computation time |

T4 uses strict `≤ 0` comparison.  Parameters with SE at machine-epsilon scale
(e.g. `~1e-14`) are technically positive and pass T4, even though they display as
`0.000000` in 6-decimal-place formatting.  The `in_free_mask` column of the inference
table identifies which parameters are in the free block checked by T4.

---

## 11. Reproducibility Metadata

`_build_reproducibility_metadata` records:

- UTC timestamp at report generation time
- Python version and platform
- Package versions: `numpy`, `pandas`, `scipy`, `gamspy`, `pyarrow`, `yaml`
- Git SHA, branch, dirty-flag (via `_git_revision_info`)
- SHA-256 (first 16 hex digits) of: `results_json`, `spec_config`,
  `mnl_base__singles.parquet`, `mnl_base__couples.parquet`
- Key fields from `estimation_results.json` metadata: `run_timestamp`,
  `specification`, `solver`, `gamspy_version`, `command_line`

---

## 12. Comparison Run

`_build_comparison_diagnostics` loads two parameter vectors and computes:

- L∞ distance and the parameter where it is achieved
- Top-5 parameter differences (sorted by absolute difference)
- Full `param_diff_table` list (one entry per parameter)

Theta extraction preference: cluster SE JSON `converged_theta` > results JSON
`parameters` block.  The function handles vector-length mismatches gracefully.

---

## 13. Strict-Report Mode

When `--strict-report` is set, `run_extended_diagnostics` raises `RuntimeError`
after writing artifacts if any of the following are unavailable:

- Hessian condition number (requires `--cluster-se-json`)
- Data diagnostics T3/T4/T5 (requires `--cluster-se-json`)

This mode is intended for automated pipelines that require complete diagnostic
coverage.  The `main()` function catches `RuntimeError` from this check and
returns exit code 1.

---

## 14. Implementation Notes

**Helper functions added** (inserted before `# === CLI INTERFACE ===`):

| Function | Role |
|----------|------|
| `_load_cluster_se_json` | Load cluster SE JSON artifact |
| `_parse_listing_file` | Parse GAMS `.lst` for CONOPT diagnostics |
| `_parse_solver_log_file` | Parse plain-text solver log |
| `_extract_solver_convergence_diagnostics` | Combine results JSON + listing + log |
| `_compute_gradient_diagnostics` | Python-side ∂ log L / ∂ θ at convergence |
| `_extract_extended_hessian_diagnostics` | VCV condition, SE ranges, T5 |
| `_build_reproducibility_metadata` | Git, Python, packages, file hashes |
| `_build_comparison_diagnostics` | L∞ diff table between two runs |
| `_build_enhanced_param_df` | Full parameter DataFrame with SE and bounds |
| `_fmt_solver_diag_md` | Markdown renderer for solver section |
| `_fmt_conopt_md` | Markdown renderer for CONOPT section |
| `_fmt_gradient_md` | Markdown renderer for Python gradient section |
| `_fmt_hessian_md` | Markdown renderer for Hessian section |
| `_fmt_comparison_md` | Markdown renderer for comparison section |
| `run_extended_diagnostics` | Orchestrator; writes `.md` and `.json` artifacts |

**`run_styled_post_estimation`**: signature extended with `report_title: Optional[str] = None`.

**`main()`**: 10 new `add_argument` calls added before `parse_args()`.  Extended
diagnostics are triggered automatically when any extended argument is present.  The
base styled report always runs first; failures in extended diagnostics do not suppress
the base report (they return exit code 1 after the base report succeeds).