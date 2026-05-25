# JMP Pooled P3a Estimation — Preflight Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## Preflight verdict: **HALT — DO NOT RUN SOLVER**

**Three blocking issues found. Estimation is not started.**

The preflight checks reveal that the post-estimation cluster-robust SE
path is not callable (PF6 / PF7 — the primary HALT condition), and two
additional data-loading infrastructure gaps would prevent the estimation
from running even if PF6/PF7 were resolved. All three must be resolved
before estimation can proceed.

---

## 1. Preflight checks performed

| # | Check | Status | Detail |
|---|-------|--------|--------|
| PF1 | CLI syntax confirmed: `--mnl-base`, `--spec-config`, `--output-dir`, `--group joint`, `--solver gamspy-conopt`, `--vectorized`, `--warm-start`, `--init-params` | **PASS (with caveat — see PF8)** | All flags exist in `enh_RURO_estimate_FR.py` argparser |
| PF2 | M1-clean warm-start results JSON exists | **PASS** | Path confirmed; 53 parameters; LL = −6487.55; `success=True` |
| PF3 | Start 1 can map 53 M1-clean params → 55 pooled params | **PASS (conditional)** | Mapping is 1:1 for all 53; `beta_E_y2015=0.0`, `beta_E_y2017=0.0`; `--warm-start` mechanism can carry this out via a custom JSON |
| PF4 | Start 2 can run from YAML initial values with `--warm-start none` | **PASS** | `--warm-start none` is a valid flag value |
| PF5 | Start 3 perturbed vector (seed 42, ±0.1) can be created from Start 1 | **PASS (conditional)** | Requires writing the perturbed vector to a JSON and passing via `--init-params`; no solver blocker |
| PF6 | `run_cluster_robust_se.py --mode post-estimation` is implemented and callable | **FAIL — HALT** | Returns "Post-estimation mode not yet implemented in this smoke-test release." (exit code 1) |
| PF7 | If post-estimation mode is only scaffolded or returns "not implemented," HALT | **HALT TRIGGERED** | Explicit halt as specified |
| PF8 | Data loading infrastructure for unified pooled parquet | **FAIL — BLOCKER** | `enh_RURO_estimate_FR.py` requires `__singles.parquet` + `__couples.parquet` split files; no such splits exist for the pooled dataset |
| PF9 | Year-indicator columns in pooled parquet | **FAIL — BLOCKER** | `year_2015_indicator` and `year_2017_indicator` columns are absent from the pooled parquet; `year_tag` (values 1, 2, 3) is present but no indicator dummies have been derived |

---

## 2. PF6/PF7 — Post-estimation mode not implemented (primary HALT)

**Evidence.**

`scripts/enhanced/run_cluster_robust_se.py`, lines 749–754:

```python
elif args.mode == "post-estimation":
    if args.results_json is None or not args.results_json.exists():
        logger.error("--results-json required and must exist for post-estimation mode")
        return 1
    logger.error("Post-estimation mode not yet implemented in this smoke-test release.")
    return 1
```

The post-estimation mode is scaffolded: the CLI flag exists and
`--results-json` is accepted, but the body of the mode returns
`"not implemented"` and exits with code 1 immediately. No
`compute_scores_joint` call, no true-Hessian loading, no sandwich
computation, and no T3/T4/T5 diagnostics are performed.

**Why this is the primary HALT condition.**

The authorization (§7, §14) requires that after each converged start,
cluster-robust SEs are computed with the **true Hessian** (the
numerical Hessian at the converged theta), not the dummy Hessian from
the smoke test. The post-estimation mode of `run_cluster_robust_se.py`
is the GA17 infrastructure's post-estimation interface for this
computation; it is explicitly referenced in the authorization §14 and
§19 as the required path. The smoke-test clearance (dummy Hessian at
initial values) is not a substitute.

Because the post-estimation mode is not implemented, there is no
callable path to the true-Hessian cluster-robust SEs. The inference
deliverable of the pooled estimation cannot be produced. Running the
solver would produce converged theta vectors without the cluster-robust
SEs that are the stated inference output (authorization §14 R1–R4), and
the post-estimation diagnostics D9 (T3 full 9,657-cluster count), D10
(T4 robust-SE positivity), and D11 (T5 robust-versus-Hessian comparison)
could not be completed. These diagnostics are mandatory before any SA2
verdict (authorization §13, §15).

**Per the task instruction: "If post-estimation mode is only scaffolded
or returns 'not implemented,' HALT before running estimation."**
This condition is met. The solver is not run.

---

## 3. PF8 — Data loading infrastructure for unified pooled parquet (additional blocker)

**Evidence.**

`enh_RURO_estimate_FR.py` lines 1180–1187:

```python
mnl_base = Path(args.mnl_base)
singles_path = Path(str(mnl_base) + "__singles.parquet")
couples_path = Path(str(mnl_base) + "__couples.parquet")
...
metadata_path = Path(str(mnl_base) + "__mnlmeta.json")
```

The script unconditionally appends `__singles.parquet` and
`__couples.parquet` to `--mnl-base`. The pooled dataset is a single
unified parquet file (`fr_p3a_gsurv2_harmonised.parquet`) with
`household_type` column (`single` / `couple`) for the split. No
`__singles.parquet` or `__couples.parquet` files exist in
`Data/processed/fr/pooled/`:

```
Data/processed/fr/pooled/
  fr_p3a_gsurv2_harmonised.parquet         ← exists (unified)
  fr_p3a_gsurv2_harmonised__stage_m1_meta.json
  [no __singles.parquet, no __couples.parquet]
```

An attempt to run `enh_RURO_estimate_FR.py --mnl-base
Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised` would fail because
neither `fr_p3a_gsurv2_harmonised__singles.parquet` nor
`fr_p3a_gsurv2_harmonised__couples.parquet` exists.

**What is required to resolve PF8:**
Either (a) add a `--parquet` flag to `enh_RURO_estimate_FR.py` that
accepts a unified parquet and splits internally by `household_type`, or
(b) split the unified pooled parquet into `__singles.parquet` and
`__couples.parquet` counterparts with a `__mnlmeta.json`, matching the
format `load_and_validate_mnl_data` expects.

---

## 4. PF9 — Year-indicator columns absent from pooled parquet (additional blocker)

**Evidence.**

The pooled parquet schema (confirmed via `pyarrow.parquet`):
- `year_2015_indicator`: **absent**
- `year_2017_indicator`: **absent**
- `year_tag` (integer, values 1/2/3): **present**

The P3a pooled YAML requires `year_2015_indicator` and
`year_2017_indicator` as market-opportunity shifters (positions 35–36).
These enter the estimation via `include_extra_vars` in the precompute
step. The `_extract_or_derive_single` function in `estimation_utils.py`
handles column lookup and a regex-based one-hot derivation for patterns
like `colname_N` (e.g., `year_tag_1`). However, `year_2015_indicator`
and `year_2017_indicator` do not match this pattern — the names end in
`_indicator`, not a bare integer — so the automatic derivation from
`year_tag` will fail, and both will be `None`.

The smoke test already exhibited this failure: warnings of the form
`"skipping 'year_2015_indicator' not found on data"` were produced and
visible in `Results/diagnostics/smoke_test_stdout_20260521.txt`.

**What is required to resolve PF9:**
Either (a) add `year_2015_indicator = (year_tag == 1)` and
`year_2017_indicator = (year_tag == 3)` as columns to the pooled
parquet (or add them as derived columns at load time in the script), or
(b) rename the YAML shifter variables to `year_tag_1` and `year_tag_3`
so the automatic derivation pattern `year_tag_N` is matched (the regex
`^(?P<base>[A-Za-z][A-Za-z0-9_]*)_(?P<level>-?\d+)$` matches
`year_tag_1` with `base=year_tag`, `level=1`).

Option (b) would require modifying the YAML specification, which is not
authorized by the execution authorization. Option (a) — deriving the
indicator columns at load time in the script — does not modify the YAML
or the parquet and is the lower-risk path.

---

## 5. PF1 — CLI syntax confirmation

All flags confirmed present in `enh_RURO_estimate_FR.py`:

| Flag | Confirmed present | Notes |
|------|------------------|-------|
| `--mnl-base` | Yes | Required; appends `__singles.parquet` / `__couples.parquet` |
| `--spec-config` | Yes | Path to YAML spec |
| `--output-dir` | Yes | Required |
| `--group joint` | Yes | Choices: `singles_male`, `singles_female`, `singles_pooled`, `couples`, `joint` |
| `--solver gamspy-conopt` | Yes | Choices: `scipy`, `gamspy-conopt`, `gamspy-ipopt`, `gamspy-knitro` |
| `--vectorized` | Yes | `store_true` flag; enables vectorised GAMSPy mode |
| `--warm-start` | Yes | `auto` / `none` / path to results JSON |
| `--init-params` | Yes | Path to CSV or JSON with custom initial values |

Note: `--mnl-base` cannot be used with the unified pooled parquet in its
current form (see PF8). The command syntax is confirmed callable on the
existing script; a data-loading change is required for the pooled run.

---

## 6. PF2 — M1-clean warm-start results JSON confirmed

**Path:**
```
outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/
  estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-38-37/
  estimation_results.json
```

**Status:** converged = True, LL = −6487.552159, 53 parameters present.

**53 M1-clean converged parameter values (for warm-start mapping record):**

| # | Parameter | M1-clean value |
|---|-----------|---------------|
| 1 | beta_l0_sm | 3.836170 |
| 2 | beta_l_age_sm | 0.004052 |
| 3 | beta_l_age2_sm | 0.001755 |
| 4 | beta_c_sm | 0.553672 |
| 5 | theta_l_sm | −0.712470 |
| 6 | beta_l0_sf | 4.469536 |
| 7 | beta_l_age_sf | 0.000335 |
| 8 | beta_l_age2_sf | 0.003931 |
| 9 | beta_l_nkids_sf | −0.082422 |
| 10 | beta_c_sf | 0.505586 |
| 11 | theta_l_sf | −0.722669 |
| 12 | theta_c_singles | −1.048483 |
| 13 | beta_l0_m | 0.012080 |
| 14 | beta_l_age_m | −0.010336 |
| 15 | beta_l_age2_m | 0.000927 |
| 16 | theta_l_m | −0.731400 |
| 17 | beta_l0_f | 2.592348 |
| 18 | beta_l_age_f | −0.059381 |
| 19 | beta_l_age2_f | 0.003009 |
| 20 | beta_l_nkids_f | 0.169459 |
| 21 | theta_l_f | −0.678130 |
| 22 | beta_c | 4.000030 |
| 23 | beta_E | −2.499276 |
| 24 | beta_h_pt1 | −0.502194 |
| 25 | beta_h_pt2 | 0.372247 |
| 26 | beta_h_ft | 1.449680 |
| 27 | beta_E_gsur | −1.328948 |
| 28 | beta_E_drgn2 | 0.801342 |
| 29 | beta_E_drgn3 | 0.656401 |
| 30 | beta_E_drgn4 | 1.562552 |
| 31 | beta_E_drgn5 | 0.772496 |
| 32 | beta_E_drgn6 | 0.766517 |
| 33 | beta_E_drgn7 | 0.640451 |
| 34 | beta_E_drgn8 | 0.463141 |
| 35 | beta_occ_2_sm | −1.474430 |
| 36 | beta_occ_3_sm | −2.129195 |
| 37 | beta_occ_4_sm | 0.060419 |
| 38 | beta_occ_2_sf | 0.051019 |
| 39 | beta_occ_3_sf | −0.500047 |
| 40 | beta_occ_4_sf | 0.859079 |
| 41 | beta_occ_2_cm | −1.495560 |
| 42 | beta_occ_3_cm | −2.251328 |
| 43 | beta_occ_4_cm | 0.459406 |
| 44 | beta_occ_2_cf | 0.131868 |
| 45 | beta_occ_3_cf | −0.249050 |
| 46 | beta_occ_4_cf | 1.085850 |
| 47 | beta_w0 | 2.016252 |
| 48 | beta_w_educL | −0.040563 |
| 49 | beta_w_educH | 0.323990 |
| 50 | beta_w_pexp | 0.018461 |
| 51 | beta_w_pexp2 | −0.000226 |
| 52 | sigma | 0.427474 |
| 53 | beta_ll | 2.617465 |

**Start 1 pooled vector** = all 53 values above, plus `beta_E_y2015 = 0.0`
and `beta_E_y2017 = 0.0` at positions 35–36 in the pooled ordering.

---

## 7. PF3/PF4/PF5 — Starts 1–3 mappings confirmed (conditional on resolving blockers)

**Start 1 (warm from M1-clean):** The 53-parameter M1-clean vector maps
1:1 to the pooled parameter positions 1–34 and 37–55 (per Gate-A parse
report §3). Positions 35–36 (`beta_E_y2015`, `beta_E_y2017`) are set to
0.0. A 55-entry JSON can be written and passed via `--init-params`. The
`--warm-start` flag can also be used with the M1-clean results JSON
directly; the estimation script sets new parameters to the
`--warm-start-default` value (default 0.0), which is correct for the
two year dummies. Both mechanisms are available.

**Start 2 (spec defaults):** Pass `--warm-start none`. All 55
parameters initialise at `initial_values` from the YAML.

**Start 3 (perturbed Start 1, seed 42, ±0.1):** Perturb the Start 1
vector by applying `np.random.default_rng(42).uniform(-0.1, 0.1, 55)`.
Write to a JSON and pass via `--init-params`. Perturbation file would
be saved as e.g.
`Results/start3_perturbed_warm_start_seed42.json`.

---

## 8. Required resolutions before estimation may run

The estimation is HALTED. Three issues must be resolved before the
solver is invoked:

### Resolution R1 (primary — must resolve): Implement `run_cluster_robust_se.py --mode post-estimation`

The post-estimation mode must be fully implemented:
- Accept `--results-json` pointing to a converged-theta estimation
  results JSON.
- Load the converged theta for the nominated start.
- Load the full pooled parquet (1,244,500 rows, no bound).
- Build precomputed data for singles and couples.
- Call `compute_scores_joint(theta_converged, ...)` to extract scores
  on the full dataset.
- Compute the true Hessian (numerical second derivative of negative LL
  at converged theta) as the sandwich bread.
- Call `compute_cluster_robust_se(hessian_true, scores_all,
  cluster_ids_all, free_mask)` to assemble the sandwich VCV.
- Run T3 (confirm 9,657 unique `idorighh` clusters on the full dataset),
  T4 (robust-SE positivity), T5 (robust-vs-Hessian comparison).
- Write the cluster-robust SE vector, the VCV matrix, and the
  T3/T4/T5 diagnostic results to output files.

### Resolution R2 (required to load data): Add pooled parquet loading to `enh_RURO_estimate_FR.py`

The estimation script must be extended to accept a unified pooled
parquet via a new `--parquet` flag (or an equivalent mechanism), splitting
internally by `household_type` column instead of requiring pre-split
`__singles.parquet` and `__couples.parquet` files. The pooled
`__stage_m1_meta.json` must be accepted as the metadata source.

### Resolution R3 (required for year effects): Add year-indicator derivation

`year_2015_indicator` and `year_2017_indicator` must be available to
the precompute functions. The lowest-risk resolution is to derive them
at load time from `year_tag` (without modifying the parquet or the
YAML): `df["year_2015_indicator"] = (df["year_tag"] == 1).astype(float)`
and `df["year_2017_indicator"] = (df["year_tag"] == 3).astype(float)`.
This derivation should happen immediately after the parquet is loaded,
before precomputation.

---

## 9. What was confirmed working

The following infrastructure is confirmed correct and requires no
changes:

- The 55-parameter pooled YAML parses correctly (53 M1-clean + 2 year
  dummies, Gate-A PASS).
- The pooled parquet exists at `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
  (1,244,500 rows, 146 columns, `idorighh` present, `cluster_id ==
  idorighh` confirmed).
- The M1-clean results JSON exists and contains 53 converged parameters.
- The warm-start mapping (53 M1-clean → 55 pooled with two year dummies
  at 0.0) is straightforward.
- The `--solver gamspy-conopt --vectorized` flags exist in the CLI.
- `reg_nuts1_2`–`reg_nuts1_8` exist in the parquet (region dummies
  build correctly via the existing code path in `estimation_utils.py`).
- `loc4`, `loc4_male`, `loc4_female` exist (occupation dummies build
  correctly as `loc4_2`, `loc4_3`, `loc4_4` via the existing code path).
- `ils_dispy_real`, `ils_dispy_male`, `ils_dispy_female` all exist
  (GA15 income routing confirmed present).
- Cluster-key strictness safeguard confirmed active: both
  `precompute_data_singles` and `precompute_data_couples` will use
  `idorighh` and will log an explicit warning if it is absent.
- GA17 smoke-test callability CONFIRMED (C1–C17 all pass).

---

## 10. What was not executed

- No solver was invoked.
- No estimation was run.
- No welfare computation was performed.
- The pooled parquet was not modified.
- The YAML specification was not modified.
- No output was promoted to a canonical path.
- No SA2 verdict was issued.

---

## 11. Final statements

- **Preflight passed: NO.** Three blocking issues found (PF6/PF7
  primary HALT; PF8 data-loading blocker; PF9 year-indicator blocker).

- **Solver not run.** Per the task instruction, estimation is halted
  when post-estimation mode is only scaffolded.

- **SA2 verdict is NOT issued by this report.**

- **The immediate next task is to resolve the three blocking issues**
  (R1: implement post-estimation mode; R2: add unified-parquet loading;
  R3: add year-indicator derivation), then re-run the preflight. The
  estimation may proceed only after a clean preflight pass.

- **Welfare computation is NOT authorized.** Separately gated.

- **M1-clean 2016 remains the active JMP baseline.** No pooled estimate
  exists; no displacement has occurred.

---

*Report generated: 2026-05-21. No solver invoked. No estimation run.*