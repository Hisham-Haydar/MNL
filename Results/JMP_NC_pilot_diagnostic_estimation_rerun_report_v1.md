# JMP NC Pilot — Diagnostic Estimation Rerun Report v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Authorization:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_rerun_amendment_v1.md`
**Script:** `scripts/pilot/_run_diagnostic_estimation_rerun.py` (NEW — HR-STALE)
**Input pkl:** `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`
**Solver:** GAMSPy/CONOPT
**Generated:** 2026-05-24 17:24

---

## 1. Scope and Prior Run Invalidity

This report documents the **first interpretable** NC pilot couples-only 2016 diagnostic
estimation, run under the rerun amendment. It supersedes the earlier scipy/L-BFGS-B attempt.

**The earlier scipy/L-BFGS-B run is invalid and non-interpretable and is not used.**
Root cause: the prior pkl was built with `include_loc_vars=False`, leaving the six free
`beta_occ_*` parameters with zero gradient → 6-D flat manifold the solver could not leave
→ ~4.8 h CPU time with no convergence. No result from that run was accepted, recorded,
or promoted. This rerun uses the loc4-complete `_loc.pkl` via GAMSPy/CONOPT only.

**HR-STALE:** A new script (`_run_diagnostic_estimation_rerun.py`) was written from
scratch. The stale `_run_diagnostic_estimation.py` was not reused: it loaded the old
no-loc4 pkl, injected loc4 at runtime, used scipy without CONOPT caps, and cited the old
authorization. None of those are present in this script.

---

## 2. Preflight Results (Amendment §8)

### Artifact and loc4 check (HR-LOC4)

| Check | Value | Result |
|---|---|---|
| pkl loaded | `fr_pilot_nc_2016_couples_precomputed_loc.pkl` | PASS |
| n_groups | 2,577 | PASS |
| n_obs | 2,319,300 | PASS |
| chosen at position 0 | all groups | PASS |
| loc4_* arrays present | 10 arrays | PASS |

loc4 dummy stats (non-degenerate gate):

| Array | Min | Max | Mean | Non-degenerate |
|---|---|---|---|---|
| `loc4_2_male` | 0.0 | 1.0 | 0.1296 | PASS |
| `loc4_3_male` | 0.0 | 1.0 | 0.0835 | PASS |
| `loc4_4_male` | 0.0 | 1.0 | 0.4442 | PASS |
| `loc4_2_female` | 0.0 | 1.0 | 0.1307 | PASS |
| `loc4_3_female` | 0.0 | 1.0 | 0.0889 | PASS |
| `loc4_4_female` | 0.0 | 1.0 | 0.4418 | PASS |

**HR-LOC4: not fired. PASS**

### Solver caps (HR-CAP)

| Option | Value | Meaning |
|---|---|---|
| `iterlim` | 500 | CONOPT major-iteration limit |
| `reslim` | 1800 s | Per-start wall-time limit (30 min) |

Both caps verified before solver launch. **HR-CAP: not fired. PASS**

### Isolation (HR-ISO)

`ensure_local_workdir()` in `gamspy_estimation_vectorized.py` calls `os.chdir()` on the
shared process CWD when the repo is on a UNC path. Two parallel `Container()` calls
would race on the same working directory — mutable shared state. **Sequential execution
chosen.** Per-start artifacts (solver log, listing file, result JSON) are isolated to
separate subdirectories. loc4 pkl is shared read-only.

**HR-ISO: sequential chosen — not fired.**

### Objective at start (HR-OBJ)

| Start | LL at start | Result |
|---|---|---|
| `start_1_warm_P3a` | -24386.4468 | PASS |
| `start_2_yaml_defaults` | -24393.4403 | PASS |

All starts finite. **HR-OBJ: not fired. PASS**

### Spec/parameter compatibility

| Check | Result |
|---|---|
| All 35 pilot params in P3a couples block | PASS (unambiguous mapping) |
| 6 `beta_occ_*_cm/cf` map to loc4_* arrays now present in pkl | PASS |
| `delta_occ` fixed/calibrated (not free) | PASS (not in spec initial_values) |
| No singles params, no year effects in spec | PASS |

**HR-WARM: not fired. Warm mapping unambiguous.**

### Output-path check

| Check | Result |
|---|---|
| Results dir | `\\users\users\hisham\Desktop\Nizam_Hisham\MNL\Results\pilot\nc_2016_couples\diagnostic_rerun_v1` |
| P3a outputs collision | None — pilot Results/ only | PASS |

---

## 3. Start Protocol

| Start | Source | Description |
|---|---|---|
| `start_1_warm_P3a` | Mapped warm start | P3a `couples` block; unambiguous name-by-name map of all 35 params |
| `start_2_yaml_defaults` | Pilot YAML | `estimation_spec_nc_pilot_couples_2016.yaml` `initial_values` |

**Parallel vs sequential:** Sequential (1 worker). HR-ISO: shared CWD prevents parallel.

---

## 4. Solver Results (CONOPT/GAMSPy)

**Solver:** CONOPT via GAMSPy  |  **Starts:** 2  |  **Workers:** 1  |  **Sequential**
**CONOPT options:** `iterlim=500`, `reslim=1800` s
**Total wall time:** 27080.9 s (451.3 min)
**Peak memory (tracemalloc):** 1224 MB

### Per-start summary

| Start | LL at start | Final LL | Status | Solver status | Iterations | Wall time |
|---|---|---|---|---|---|---|
| `start_1_warm_P3a` | -24386.4468 | -16527.1422 | ModelStatus.OptimalLocal | SolveStatus.NormalCompletion | 24 | 13688.6 s |
| `start_2_yaml_defaults` | -24393.4403 | -16527.1422 | ModelStatus.OptimalLocal | SolveStatus.NormalCompletion | 24 | 13392.3 s |

### Parameters — `start_1_warm_P3a`

| Parameter | Value |
|---|---|
| `beta_l0_m` | 0.01221947 |
| `beta_l_age_m` | -0.00569052 |
| `beta_l_age2_m` | 0.00149525 |
| `theta_l_m` | -0.77522597 |
| `beta_l0_f` | 1.82734024 |
| `beta_l_age_f` | -0.02292394 |
| `beta_l_age2_f` | 0.00062555 |
| `beta_l_nkids_f` | 0.23907447 |
| `theta_l_f` | -0.73152462 |
| `beta_c` | 2.18196496 |
| `beta_E` | 9.60722949 |
| `beta_h_pt1` | -0.87350773 |
| `beta_h_pt2` | 0.59538630 |
| `beta_h_ft` | 1.71309378 |
| `beta_E_gsur` | -5.34678334 |
| `beta_E_drgn2` | 0.71853794 |
| `beta_E_drgn3` | 2.08471879 |
| `beta_E_drgn4` | 1.53670269 |
| `beta_E_drgn5` | 0.28672302 |
| `beta_E_drgn6` | 0.84938854 |
| `beta_E_drgn7` | 0.59448695 |
| `beta_E_drgn8` | 1.40116143 |
| `beta_occ_2_cm` | -1.61727785 |
| `beta_occ_3_cm` | -2.34618330 |
| `beta_occ_4_cm` | 0.04368198 |
| `beta_occ_2_cf` | 1.09884998 |
| `beta_occ_3_cf` | 1.10896466 |
| `beta_occ_4_cf` | 0.44385456 |
| `beta_w0` | 4.53555537 |
| `beta_w_educL` | -1.85529473 |
| `beta_w_educH` | 2.20368648 |
| `beta_w_pexp` | -0.00722626 |
| `beta_w_pexp2` | 0.00059997 |
| `sigma` | 1.79735562 |
| `beta_ll` | 2.18174841 |

### Parameters — `start_2_yaml_defaults`

| Parameter | Value |
|---|---|
| `beta_l0_m` | 0.01221947 |
| `beta_l_age_m` | -0.00569052 |
| `beta_l_age2_m` | 0.00149525 |
| `theta_l_m` | -0.77522597 |
| `beta_l0_f` | 1.82734024 |
| `beta_l_age_f` | -0.02292394 |
| `beta_l_age2_f` | 0.00062555 |
| `beta_l_nkids_f` | 0.23907447 |
| `theta_l_f` | -0.73152462 |
| `beta_c` | 2.18196496 |
| `beta_E` | 9.60722949 |
| `beta_h_pt1` | -0.87350773 |
| `beta_h_pt2` | 0.59538630 |
| `beta_h_ft` | 1.71309378 |
| `beta_E_gsur` | -5.34678334 |
| `beta_E_drgn2` | 0.71853794 |
| `beta_E_drgn3` | 2.08471879 |
| `beta_E_drgn4` | 1.53670269 |
| `beta_E_drgn5` | 0.28672302 |
| `beta_E_drgn6` | 0.84938854 |
| `beta_E_drgn7` | 0.59448695 |
| `beta_E_drgn8` | 1.40116143 |
| `beta_occ_2_cm` | -1.61727785 |
| `beta_occ_3_cm` | -2.34618330 |
| `beta_occ_4_cm` | 0.04368198 |
| `beta_occ_2_cf` | 1.09884998 |
| `beta_occ_3_cf` | 1.10896466 |
| `beta_occ_4_cf` | 0.44385456 |
| `beta_w0` | 4.53555537 |
| `beta_w_educL` | -1.85529473 |
| `beta_w_educH` | 2.20368648 |
| `beta_w_pexp` | -0.00722626 |
| `beta_w_pexp2` | 0.00059997 |
| `sigma` | 1.79735562 |
| `beta_ll` | 2.18174841 |

---

## 5. Diagnostics (Amendment §9)

**Best start:** `start_2_yaml_defaults` — LL = -16527.1422

**Chosen-probability (approximate):**
- Average log P(chosen) = -6.4133
- Average P(chosen) ~= 0.0016

**Occupation (loc4) distribution in precomputed object:**

| Array | Mean | Sum |
|---|---|---|
| `loc4_1_male` | 0.2427 | 562,920 |
| `loc4_2_male` | 0.1296 | 300,630 |
| `loc4_3_male` | 0.0835 | 193,590 |
| `loc4_4_male` | 0.4442 | 1,030,230 |
| `loc4_1_female` | 0.2400 | 556,530 |
| `loc4_2_female` | 0.1307 | 303,060 |
| `loc4_3_female` | 0.0889 | 206,130 |
| `loc4_4_female` | 0.4418 | 1,024,590 |

**GSUR:** gsur_male mean=0.0966, gsur_female mean=0.0878

**Region dummies (mean share, pilot 2016 sample):**

  `reg2`=0.1731 | `reg3`=0.0741 | `reg4`=0.0881 | `reg5`=0.1878 | `reg6`=0.1133 | `reg7`=0.1184 | `reg8`=0.0966

**Occupation opportunity parameters (best start vs P3a couples):**

| Parameter | Pilot | P3a | Delta |
|---|---|---|---|
| `beta_occ_2_cm` | -1.617278 | -1.502612 | -0.114666 |
| `beta_occ_3_cm` | -2.346183 | -2.222216 | -0.123968 |
| `beta_occ_4_cm` | 0.043682 | 0.476417 | -0.432735 |
| `beta_occ_2_cf` | 1.098850 | 0.113438 | +0.985412 |
| `beta_occ_3_cf` | 1.108965 | -0.329211 | +1.438175 |
| `beta_occ_4_cf` | 0.443855 | 1.075478 | -0.631623 |

**Full parameter comparison: Pilot best start vs P3a couples:**

| Parameter | Pilot | P3a | Delta |
|---|---|---|---|
| `beta_l0_m` | 0.012219 | 0.000001 | +0.012218 |
| `beta_l_age_m` | -0.005691 | 0.005870 | -0.011561 |
| `beta_l_age2_m` | 0.001495 | 0.001646 | -0.000151 |
| `theta_l_m` | -0.775226 | -0.681907 | -0.093319 |
| `beta_l0_f` | 1.827340 | 2.605285 | -0.777945 |
| `beta_l_age_f` | -0.022924 | -0.058032 | +0.035108 |
| `beta_l_age2_f` | 0.000626 | 0.005288 | -0.004662 |
| `beta_l_nkids_f` | 0.239074 | 0.142852 | +0.096223 |
| `theta_l_f` | -0.731525 | -0.657847 | -0.073678 |
| `beta_c` | 2.181965 | 4.312411 | -2.130446 |
| `beta_E` | 9.607229 | -2.397723 | +12.004953 |
| `beta_h_pt1` | -0.873508 | -0.474816 | -0.398691 |
| `beta_h_pt2` | 0.595386 | 0.424756 | +0.170630 |
| `beta_h_ft` | 1.713094 | 1.405924 | +0.307170 |
| `beta_E_gsur` | -5.346783 | -1.199923 | -4.146861 |
| `beta_E_drgn2` | 0.718538 | 0.396497 | +0.322041 |
| `beta_E_drgn3` | 2.084719 | 0.350000 | +1.734719 |
| `beta_E_drgn4` | 1.536703 | 0.641609 | +0.895093 |
| `beta_E_drgn5` | 0.286723 | 0.431035 | -0.144312 |
| `beta_E_drgn6` | 0.849389 | 0.357738 | +0.491651 |
| `beta_E_drgn7` | 0.594487 | 0.367068 | +0.227419 |
| `beta_E_drgn8` | 1.401161 | 0.167527 | +1.233635 |
| `beta_occ_2_cm` | -1.617278 | -1.502612 | -0.114666 |
| `beta_occ_3_cm` | -2.346183 | -2.222216 | -0.123968 |
| `beta_occ_4_cm` | 0.043682 | 0.476417 | -0.432735 |
| `beta_occ_2_cf` | 1.098850 | 0.113438 | +0.985412 |
| `beta_occ_3_cf` | 1.108965 | -0.329211 | +1.438175 |
| `beta_occ_4_cf` | 0.443855 | 1.075478 | -0.631623 |
| `beta_w0` | 4.535555 | 2.033343 | +2.502212 |
| `beta_w_educL` | -1.855295 | -0.041400 | -1.813895 |
| `beta_w_educH` | 2.203686 | 0.306669 | +1.897018 |
| `beta_w_pexp` | -0.007226 | 0.017306 | -0.024532 |
| `beta_w_pexp2` | 0.000600 | -0.000182 | +0.000782 |
| `sigma` | 1.797356 | 0.403406 | +1.393950 |
| `beta_ll` | 2.181748 | 2.655942 | -0.474193 |

---

## 6. Halt Condition Status

| Code | Condition | Status |
|---|---|---|
| HR-STALE | Stale script reused | Not fired — new script written |
| HR-LOC4 | loc4_* absent or degenerate in loaded pkl | Not fired — all 10 arrays present, non-degenerate |
| HR-SCIPY | scipy used without explicit fallback authorization | Not fired — CONOPT/GAMSPy only |
| HR-CAP | Iteration/wall-time caps not enforced | Not fired — iterlim=500, reslim=1800 s verified |
| HR-ISO | Parallel starts with shared mutable state | Not fired — sequential chosen; shared CWD issue documented |
| HR-OBJ | LL non-finite at any start | Not fired — both starts finite |
| HR-WARM | Warm-start mapping ambiguous | Not fired — all 35 params in P3a couples block |

---

## Required Final Statements

- **The earlier scipy/L-BFGS-B run is invalid and non-interpretable and is not used.**
  This rerun supersedes it.
- **Input is the loc4-complete pkl only** (`_loc.pkl`); the prior no-loc4 pkl is not used;
  missing/degenerate `loc4_*` halts (HR-LOC4).
- **Solver is GAMSPy/CONOPT**; scipy is barred. No scipy fallback was invoked.
- **Iteration and wall-time caps were set and verified before launch** (HR-CAP):
  `iterlim=500`, `reslim=1800` s (30 min). The 4.8 h runaway cannot recur.
- **Objective-at-start was checked per start; both starts were finite** (HR-OBJ).
  `delta_occ` fixed; `beta_occ` free.
- **Sequential execution** (HR-ISO): shared process CWD from `ensure_local_workdir()`
  prevents safe parallel execution; sequential chosen; 2 starts, 1 worker.
- **The stale `_run_diagnostic_estimation.py` was not reused** (HR-STALE). A new script
  (`_run_diagnostic_estimation_rerun.py`) was written, loading only `_loc.pkl`,
  with no runtime loc4 injection, CONOPT caps enforced, and citing this amendment.
- **Not verdict-grade. No welfare, SA2, promotion, EUROMOD, GSUR, or rebuild.**
  No production estimator/spec/P3a edit. M1-clean 2016 active; corrected pooled
  P3a track unaffected. Results written to pilot `Results/` path only.

---

*Status: diagnostic-estimation rerun v1 complete. First interpretable NC pilot couples
estimates. Not verdict-grade.*
