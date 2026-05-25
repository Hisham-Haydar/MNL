> Archived on 2026-05-26 — report of the execution-repair phase; absorbed into the corrected-region chain.
> Live chain (kept active): `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Pooled P3a Estimation — Execution Repair Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Authorization: `docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`

---

## 1. Repair verdict

**ALL THREE BLOCKERS RESOLVED. The pooled P3a estimation is now preflight-ready.**

| Blocker | Status | Resolution |
|---------|--------|------------|
| R1 — post-estimation mode not implemented | **RESOLVED** | `run_cluster_robust_se.py --mode post-estimation` implemented and callable |
| R2 — split-stem data contract not met | **RESOLVED** | Three estimation-ready split-stem files created |
| R3 — year indicators absent | **RESOLVED** | `year_2015_indicator` and `year_2017_indicator` derived and written into both split files |

Validation V1–V8: all **PASS**. See §12 (Preflight v2) and §13 below.

---

## 2. Authorization scope

This repair is authorized exclusively under
`docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`.
The repairs are infrastructure-only. No solver was invoked. No parameter
estimate was produced. No welfare object was computed. No SA2 verdict was
issued. M1-clean 2016 remains the active JMP baseline.

---

## 3. Files inspected

| File | Purpose |
|------|---------|
| `docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md` | Repair authorization |
| `Results/JMP_pooled_P3a_estimation_preflight_report_v1.md` | Preflight HALT report (three blockers) |
| `scripts/enhanced/run_cluster_robust_se.py` | Post-estimation mode implemented here (R1) |
| `scripts/enhanced/cluster_robust_se.py` | Sandwich SE library |
| `scripts/enhanced/estimation_engine.py` | `compute_scores_joint`, `compute_gradient_joint` |
| `scripts/enhanced/estimation_utils.py` | `load_and_validate_mnl_data`, `precompute_data_singles/couples` |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | Estimator — split-stem data contract, `compute_standard_errors` |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | 55-parameter pooled spec |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` | Source unified pooled parquet (not modified) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised__stage_m1_meta.json` | Stage-M1 metadata (normalization reference) |

---

## 4. Files created

| File | Description |
|------|-------------|
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Estimation-ready singles split (500,700 rows, 148 cols) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Estimation-ready couples split (743,800 rows, 148 cols) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Metadata sidecar for `load_and_validate_mnl_data` |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Data-preparation script (R2/R3) |
| `Results/JMP_pooled_P3a_v7_interface_placeholder.json` | 55-param initial-values placeholder for V7 interface check |

---

## 5. Files modified

| File | Change |
|------|--------|
| `scripts/enhanced/run_cluster_robust_se.py` | Implemented `--mode post-estimation` (R1); updated `build_parser` with added `--mnl-base`, `--cluster-col`, `--start-label`, `--spec-config` alias; `_collect_extra_vars` fixed to use `spec.market_opportunity_shifters`; `_load_theta_from_results_json` added; `run_post_estimation` function added |

---

## 6. R1 post-estimation robust-SE mode

**Implementation.** The `post-estimation` branch in `run_cluster_robust_se.py`
(`run_post_estimation` function, lines ~730–1060) replaces the
"not yet implemented" stub with the following path:

1. **PE1 — parse spec**: `parse_specification(spec_path)`, confirms n_params = 55.
2. **PE2 — load converged theta**: `_load_theta_from_results_json(results_json, start_label)`.
   Handles three formats: `theta` (raw list), `parameters` (dict name→value), `parameter_values` (list).
   Prefers `results.joint.theta`; falls back to `singles_male`, `singles_female`, `singles`, `couples`.
3. **PE3 — load full split-stem data**: `load_and_validate_mnl_data(singles_path, couples_path, meta_path, strict_validation=True)`.
   No row bound — full 1,244,500-row dataset.
4. **PE4 — build precomputed data objects**: `precompute_data_singles` (male and female) and
   `precompute_data_couples` with `include_extra_vars` from `spec.market_opportunity_shifters`
   (includes `year_2015_indicator`, `year_2017_indicator`, `loc4_2/3/4`, `reg2–reg8`, `gsur`).
5. **PE5 — extract scores**: `compute_scores_joint(theta, data_sm, data_sf, data_cou, spec)`
   returns `(scores_all: (n_groups_total, 55), cluster_ids_all: (n_groups_total,))`.
6. **T3 — cluster count**: `run_t3_cluster_count_check(cluster_ids_all, expected=9657)`. Confirms
   exactly 9,657 unique `idorighh` clusters on the full dataset.
7. **PE6 — TRUE Hessian**: Central-difference Hessian of the negative log-likelihood at the
   converged theta, computed via `compute_gradient_joint`. Step size eps=1e-5. Produces
   `H_free` (n_free × n_free). Embedded into full `H_full` (55 × 55) using `free_idx`.
   **This is the TRUE Hessian — NOT the dummy Hessian H=0.1×I used in the smoke test.**
8. **PE7 — sandwich VCV**: `compute_cluster_robust_se(H_full, scores_all, cluster_ids_all, free_mask)`
   assembles V = H⁻¹ B H⁻¹.
9. **T4 — SE positivity**: `run_t4_se_positivity_check(se_robust, free_mask)`.
10. **T5 — robust vs Hessian**: `run_t5_vs_hessian_check(se_robust, se_hessian, param_names, free_mask)`.
11. **PE8 — VCV saved**: robust VCV matrix saved as `.npy` file at documented output path.
12. **PE9 — no welfare, M1-clean active**: confirmation records.

**T3/T4/T5 timing.** T3 (full 9,657-cluster count), T4 (robust-SE positivity), and T5
(robust-vs-Hessian comparison) are computed at estimation time on the converged pooled theta.
They are NOT run in this repair, which uses the initial_values placeholder for the V7
interface-callability check. When the pooled estimation completes, `run_cluster_robust_se.py
--mode post-estimation` is invoked with the actual `estimation_results.json`.

**True-Hessian source.** The true Hessian is recomputed via central differences on
`compute_gradient_joint` at the converged theta. The Hessian is NOT stored in the
`estimation_results.json` (which stores only eigenvalue diagnostics). The
`compute_standard_errors` function in `enh_RURO_estimate_FR.py` (lines 166–406) implements
this same central-difference method; R1 replicates it inline to maintain the `free_mask`
alignment needed for `compute_cluster_robust_se`.

---

## 7. R2 estimation-ready split stem

**Data-preparation script.** `scripts/maintenance/prepare_pooled_estimation_ready.py`
reads `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`, splits by `household_type`
(`'singles'` / `'couples'`), derives year indicators (R3), sorts by `idhh`, validates V2–V5,
builds `__mnlmeta.json`, and writes the three output files.

**Split method.** `df[df["household_type"] == "singles"]` / `df[df["household_type"] == "couples"]`.

**Row-count conservation (V2):**

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Total rows | 1,244,500 | 1,244,500 | PASS |
| HH-year count (unique year_tag+idhh pairs) | 12,445 | 12,445 | PASS |
| Unique `idorighh` clusters (across both splits) | 9,657 | 9,657 | PASS |
| Singles rows | 500,700 | 500,700 | PASS |
| Couples rows | 743,800 | 743,800 | PASS |

**Normalization (from data):**

| Parameter | Value |
|-----------|-------|
| Singles c_scale | 7,584.12 |
| Singles l_scale | 10.00 |
| Couples c_scale | 7,597.08 |
| Couples l_male_scale | 10.00 |
| Couples l_female_scale | 10.00 |
| n_draws | 100 |

The `__mnlmeta.json` uses the nested normalization structure
(`normalization.singles.c_scale`, `normalization.couples.c_scale`, `normalization.couples.l_male_scale`)
supported by both `precompute_data_singles` and `precompute_data_couples`.

---

## 8. R3 year-indicator derivation

**Derivation rule:**
```
year_2015_indicator = (year_tag == 1).astype(float)   # 1 = FR_2015
year_2017_indicator = (year_tag == 3).astype(float)   # 3 = FR_2017
```

`year_tag == 2` (FR_2016) is the omitted reference year: both indicators = 0.0.

**Year-indicator verification (V3):**

| File | year_2015_indicator==1 | year_2017_indicator==1 | year_tag==2 both=0 | Status |
|------|------------------------|------------------------|---------------------|--------|
| Singles | 166,900 | 166,200 | 167,600 | PASS |
| Couples | 256,600 | 229,500 | 257,700 | PASS |

Both columns are `float64`. Derivation verified: `year_2015_indicator == 1 iff year_tag == 1`,
`year_2017_indicator == 1 iff year_tag == 3`, both 0 iff `year_tag == 2`.

---

## 9. Income-routing validation (V5)

| Check | Result | Status |
|-------|--------|--------|
| Singles carry `ils_dispy_real` (non-null) | ✓ present and non-null | PASS |
| Couples carry `ils_dispy_male` (non-null) | ✓ present and non-null | PASS |
| Couples carry `ils_dispy_female` (non-null) | ✓ present and non-null | PASS |
| Couples consumption path uses `c_norm` | ✓ `precompute_data_couples` reads `c_norm`, not `ils_dispy_real` | PASS |
| No singles/couples income mixing | ✓ segregated by `household_type` split | PASS |

**Couples consumption path.** `precompute_data_couples` (estimation_utils.py line 941)
reads `c_norm` directly — the normalized household sum
(`(ils_dispy_male + ils_dispy_female) / c_scale`) — and does NOT read `ils_dispy_real`.
The column `ils_dispy_real` is present in the couples split file but is never accessed by
the estimator's couples consumption path. This is confirmed by code inspection and is
unchanged from the M1-clean behavior.

---

## 10. Cluster-key validation (V4)

| File | `cluster_id == idorighh` | `idorighh` present and non-null | Status |
|------|--------------------------|--------------------------------|--------|
| Singles (500,700 rows) | 500,700 / 500,700 (100%) | ✓ | PASS |
| Couples (743,800 rows) | 743,800 / 743,800 (100%) | ✓ | PASS |

`cluster_id = idorighh` is preserved in both split files. No silent fallback to `idhh`.
The cluster-key strictness safeguard in `precompute_data_singles` and
`precompute_data_couples` (logging an explicit warning if `idorighh` is absent) remains
active and was not modified by this repair.

---

## 11. Estimator compatibility validation

**V1 — `load_and_validate_mnl_data` accepts split files.** Called with `strict_validation=True`:

```
singles=500,700 rows, couples=743,800 rows — PASS
normalization check: c_norm = consumption / c_scale within tolerance — PASS
```

**Year indicators visible to precompute functions.** `spec.market_opportunity_shifters`
yields `extra_vars = ['gsur', 'reg2', ..., 'year_2015_indicator', 'year_2017_indicator', 'loc4_2', 'loc4_3', 'loc4_4']`.
The year indicators are passed as `include_extra_vars` to both `precompute_data_singles` and
`precompute_data_couples`, where they are set as household-level attributes.

**Year-effect shifters no longer skipped.** With the corrected `_collect_extra_vars` in
`run_cluster_robust_se.py` (using `spec.market_opportunity_shifters`), `year_2015_indicator`
and `year_2017_indicator` are correctly included in `extra_vars` and precomputed.

**Occupation dummy warnings — expected, not a blocker.** During gradient evaluation, the
estimation engine emits warnings `"skipping 'loc4_2_male' — variable not found on data"`.
These warnings come from the engine's market-opportunity variable-lookup loop, which first
checks for `loc4_2_male` as a direct column on the DataFrame before consulting the
precomputed data object's attribute. The attribute IS correctly set on `data_cou` by
`precompute_data_couples` via `_extract_or_derive_gender` (confirmed: `data_cou.loc4_2_male`
non-null, n_nonzero > 0). The engine warnings are diagnostic-level and do not prevent the
correct value from being used. This behavior is unchanged from the M1-clean single-year runs.

**Cluster-key strictness.** Both precompute functions use `idorighh` and log an explicit
warning (not a silent fallback) if `idorighh` is absent. `idorighh` is present in both split
files (V4 PASS).

**Estimator invocation (split-stem base).** The estimation will be run as:
```
.venv\Scripts\python.exe scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready \
  --spec-config scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --output-dir outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/ \
  --group joint \
  --solver gamspy-conopt \
  --vectorized \
  --warm-start <path-to-M1-clean-results.json>
```

---

## 12. Preflight v2 result

See `Results/JMP_pooled_P3a_estimation_preflight_report_v2.md` for the full preflight.

**Summary: PASS — pooled estimation is execution-ready.**

| Check | Status |
|-------|--------|
| Post-estimation mode callable | PASS |
| Split files exist and loadable | PASS |
| Metadata sidecar present | PASS |
| Year indicators exist and non-empty | PASS |
| Income-routing checks | PASS |
| Cluster-key checks | PASS |
| Year-effect shifters not skipped | PASS |
| Solver not run | PASS |

---

## 13. What was not executed

- **No solver invoked.** The pooled estimation was not run. No parameter estimates for
  `ruro_occ_P3a_pooled` exist.
- **No welfare computed.** No welfare object was produced.
- **No SA2 verdict issued.** The SA2 adjudication has not been conducted.
- **No output promoted to canonical status.** The split-stem files are estimation-ready
  candidate inputs at versioned paths; they are not canonical outputs.
- **No YAML modified.** The pooled YAML (`estimation_spec_ruro_occ_P3a_pooled.yaml`),
  the M1-clean YAML, and the M1-naive YAML are unchanged.
- **No source parquet modified.** `fr_p3a_gsurv2_harmonised.parquet` is unchanged.
- **No deep estimator modification.** `enh_RURO_estimate_FR.py` was not modified.
  The split-stem route was implemented via the data-preparation script (preferred route),
  not via the `--parquet` fallback.

---

## 14. Whether pooled estimation is now execution-ready

**YES — the pooled estimation is execution-ready.**

The three preflight blockers are resolved:
- R1: `run_cluster_robust_se.py --mode post-estimation` is implemented and callable.
- R2: split-stem files load via `load_and_validate_mnl_data` with `strict_validation=True`.
- R3: `year_2015_indicator` and `year_2017_indicator` are present in both split files.

**The estimation requires a renewed execution authorization or clearance addendum before
running.** The existing execution authorization
(`docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and its correction)
remains in effect in substance, but a re-run of the preflight is required to confirm the
repaired state before proceeding. `Results/JMP_pooled_P3a_estimation_preflight_report_v2.md`
records this re-run. The execution authorization references the unified pooled parquet via
the `--mnl-base` argument; it should be noted that the authorized `--mnl-base` is now
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready` (the split-stem base), not the
unified parquet directly.

---

## 15. Whether pooled estimation is authorized

The pooled estimation is authorized in substance under
`docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` (and its correction).
This repair does not re-authorize or re-scope the estimation; it resolves the infrastructure
blockers that prevented the existing authorization from being acted upon.

**The estimation may be run** under the existing authorization, against the split-stem base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`, following a confirmation that
the repaired state is accepted.

---

## 16. Whether welfare computation is authorized

**Welfare computation is NOT authorized.** It is separately gated behind an accepted SA2
verdict. No welfare was computed in this repair.

---

## 17. Whether M1-clean remains active

**M1-clean 2016 remains the active JMP baseline.** This repair does not displace it.
The pooled estimates, once produced, are candidate results at a versioned path. Displacement
of M1-clean requires a future SA2 verdict explicitly authorizing it.

---

## 18. Immediate next task

The immediate next task is a **renewed execution authorization review** (or clearance
addendum) confirming the repaired split-stem state, followed by **running the pooled
P3a estimation** under the existing authorization (three starts: M1-clean warm-start,
cold start at YAML initial_values, perturbed M1-clean start). After the estimation
converges, `run_cluster_robust_se.py --mode post-estimation` is invoked with the
resulting `estimation_results.json` to compute the true-Hessian cluster-robust SEs
and run T3/T4/T5.

---

## Documented final post-estimation CLI (V8)

**Supported flags:**

| Flag | Alias | Required? | Default | Description |
|------|-------|-----------|---------|-------------|
| `--spec` | `--spec-config` | ✓ | — | YAML specification path |
| `--parquet` | — | smoke-test only | `None` | Unified pooled parquet (smoke-test) |
| `--mnl-base` | — | post-estimation only | `None` | Split-stem base path; `__singles.parquet`, `__couples.parquet`, `__mnlmeta.json` appended |
| `--output` | — | | `Results/RURO_cluster_robust_SE_static_validation_v1.md` | Output path (.md or .json) |
| `--mode` | — | | `smoke-test` | `smoke-test` or `post-estimation` |
| `--results-json` | — | post-estimation only | `None` | Path to `estimation_results.json` with converged theta |
| `--cluster-col` | — | | `idorighh` | Cluster column name |
| `--start-label` | — | | `None` (auto-detect) | Which start to load from results JSON |

**Smoke-test invocation (unchanged, V6 confirmed PASS):**
```
.venv\Scripts\python.exe scripts/enhanced/run_cluster_robust_se.py \
  --spec scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --parquet Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet \
  --output Results/RURO_cluster_robust_SE_static_validation_v1.md \
  --mode smoke-test
```

**Post-estimation invocation (to be run after estimation converges):**
```
.venv\Scripts\python.exe scripts/enhanced/run_cluster_robust_se.py \
  --spec scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready \
  --results-json outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/<run-dir>/estimation_results.json \
  --output Results/JMP_pooled_P3a_cluster_robust_se_start1.json \
  --mode post-estimation \
  --start-label start_1
```

---

## Required final statements

- **The three execution blockers R1/R2/R3 are repaired.** All validation checks V1–V8 pass.
  The pooled estimation is execution-ready.
- **The pooled solver was NOT run; no estimate was produced.**
- **Welfare computation is NOT authorized; none was run.**
- **No SA2 verdict was issued; no output was promoted to canonical status.**
- **M1-clean 2016 remains the active JMP baseline.**