# RURO GAMSPy Solver Artifact Capture — v1

## 1. Purpose

When running RURO MNL estimation with a GAMSPy solver (CONOPT, IPOPT, KNITRO), the solver
produces two diagnostic files that are normally discarded:

- **`solver.log`** — plain-text convergence log from the solver (CONOPT prints RGmax and
  iteration details here).
- **`solver.lst`** — GAMS listing file containing full solution details, solver statistics,
  and CONOPT tolerance lines.

This feature saves those artifacts alongside the estimation output so that
`RURO_post_estimation_styled.py` can parse CONOPT RGmax / reduced-gradient diagnostics
and include them in the post-estimation report.

---

## 2. New CLI flags

Added to `enh_RURO_estimate_FR.py`:

| Flag | Type | Default | Effect |
|------|------|---------|--------|
| `--save-solver-artifacts` | flag | off | Save `solver.log` and `solver.lst` to the run output directory |
| `--solver-log PATH` | string | none | Explicit path for solver log (implies `--save-solver-artifacts`) |
| `--listing-file PATH` | string | none | Explicit path for GAMS listing file (implies `--save-solver-artifacts`) |

All three flags are no-ops when using the SciPy solver path — they only take effect when
`--solver` is `gamspy-conopt`, `gamspy-ipopt`, or `gamspy-knitro`.

---

## 3. Files created

When `--save-solver-artifacts` is active and explicit paths are not supplied:

```
<run_output_dir>/
    solver.log      ← CONOPT / IPOPT convergence log
    solver.lst      ← GAMS listing file
```

Explicit paths override the defaults:

```bash
--solver-log   /path/to/my.log
--listing-file /path/to/my.lst
```

Artifact paths are resolved to absolute paths immediately after `output_dir` is resolved,
before any GAMSPy call changes the process working directory.

---

## 4. How solver.log is used

`solver.log` is a plain-text file written by the GAMS/solver integration. For CONOPT it
contains per-iteration lines including:

```
...  RGmax = 1.23e-07  ...
```

`RURO_post_estimation_styled.py → _parse_solver_log_file()` reads this file and extracts
convergence information (RGmax, iteration count, termination reason) for the diagnostics
section of the post-estimation report.

---

## 5. How solver.lst is used

`solver.lst` is the full GAMS listing file. It contains:

- Solution values for all variables and equations
- Solver statistics (iterations, time, marginals)
- CONOPT tolerance lines (`Tol_Optimality`, `Lim_Iteration`, etc.)

`RURO_post_estimation_styled.py → _parse_listing_file()` parses this file and adds
structured listing diagnostics to the report.

---

## 6. How post-estimation reporting consumes the artifacts

After estimation completes, run post-estimation with the artifact paths:

```bash
.venv\Scripts\python.exe scripts/enhanced/RURO_post_estimation_styled.py \
    --results-json  outputs/.../estimation_results.json \
    --mnl-base      "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" \
    --output-dir    outputs/post_estimation \
    --solver-log    outputs/.../solver.log \
    --listing-file  outputs/.../solver.lst \
    --gamspy-diagnostics
```

The `--solver-log` and `--listing-file` flags are existing arguments in
`RURO_post_estimation_styled.py` (unchanged by this feature). The artifact paths are also
stored in `estimation_results.json` under `metadata.solver_artifacts` for reference.

---

## 7. Backward compatibility

- **No flags supplied**: behavior is identical to before — no artifact files are written,
  and all GAMSPy `model.solve()` calls use the same paths as before.
- **SciPy solver path**: the new flags are parsed but never acted upon; SciPy estimation
  is unaffected.
- **Existing `--solver-options` behavior**: preserved in all cases. When both
  `--solver-options` and `--save-solver-artifacts` are given, both `solver_options` and
  `options=Options(...)` are passed to `model.solve()`.
- **Function signatures**: `solver_artifacts=None` is the default in all six GAMSPy
  estimation functions, so existing call sites without the argument continue to work.

---

## 8. Validation performed

```
.venv\Scripts\python.exe scripts/enhanced/enh_RURO_estimate_FR.py --help
```
Confirms three new flags appear: `--save-solver-artifacts`, `--solver-log`, `--listing-file`.

```
.venv\Scripts\python.exe scripts/enhanced/RURO_post_estimation_styled.py --help
```
Confirms `--solver-log` and `--listing-file` remain available (pre-existing flags,
unchanged).

Estimation was not run. The solver was not invoked.
