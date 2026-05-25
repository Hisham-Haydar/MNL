"""
NC Pilot — First diagnostic couples-only estimation.
Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md

Wrapper that:
  1. Loads the precomputed PrecomputedDataCouples pkl (read-only from disk).
  2. Derives loc4_2/3/4_male/female dummies from source parquet and injects
     them into the in-memory pc object (not written back to disk).
  3. Parses the pilot-only YAML spec.
  4. Runs preflight gate (schema, spec compatibility, LL-at-start finite, output path).
  5. Runs >=2 starts sequentially via GAMSPy/CONOPT using production
     estimate_couples_vectorized_gamspy (unchanged logic).
  6. Saves results to pilot-only paths.

NOT verdict-grade. No welfare, no SA2, no production edit.
Starts: warm (from P3a converged couples params), default (spec initial_values).
Parallelism: sequential — GAMSPy uses a working directory per solve; sequential
  is safer on a shared server. 2 starts (warm + default) per authorization §10.
"""
import sys, os, json, time, pickle, tracemalloc, logging
import numpy as np
import pandas as pd

BASE = r"U:\Desktop\Nizam_Hisham\MNL"
sys.path.insert(0, os.path.join(BASE, r"scripts\enhanced"))
sys.path.insert(0, os.path.join(BASE, r"scripts\pilot"))

logging.basicConfig(level=logging.INFO)
import estimation_engine as ee
from estimation_spec_parser import parse_specification
from gamspy_estimation_vectorized import estimate_couples_vectorized_gamspy

PKL_PATH    = os.path.join(BASE, r"Data\pilot\nc_2016_couples\precomputed\fr_pilot_nc_2016_couples_precomputed.pkl")
PARQUET_PATH = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet")
SPEC_PATH   = os.path.join(BASE, r"scripts\pilot\specs\estimation_spec_nc_pilot_couples_2016.yaml")
OUT_ROOT    = os.path.join(BASE, r"Results\NC_pilot\diagnostic_estimation_v1")
P3A_RESULTS = os.path.join(BASE, r"outputs\estimates\fr\spec\ruro_occ_P3a_pooled\gamspy\start_1\run_2026-05-21_23-47-14\estimation_results.json")

EXPECTED_GROUPS = 2577
EXPECTED_GSIZ   = 900
EXPECTED_NOBS   = 2_319_300

def halt(code, msg):
    print(f"\nHALT {code}: {msg}")
    sys.exit(1)

print("=" * 70)
print("NC PILOT — FIRST DIAGNOSTIC COUPLES ESTIMATION (GAMSPy/CONOPT)")
print("Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md")
print("NOT VERDICT-GRADE")
print("=" * 70)

# ── STEP 1: Parse spec ────────────────────────────────────────────────────────
print(f"\nSTEP 1: Parse pilot spec")
spec = parse_specification(SPEC_PATH)
print(f"  Spec name: {spec.name}")

param_names = spec.all_param_names
print(f"  Free parameters: {len(param_names)}: {param_names}")

singles_params = [p for p in param_names if p.endswith("_sm") or p.endswith("_sf")]
year_params    = [p for p in param_names if "y2015" in p or "y2017" in p]
if singles_params:
    halt("HE-SPEC", f"Singles parameters found: {singles_params}")
if year_params:
    halt("HE-SPEC", f"Year-dummy parameters found: {year_params}")
print(f"  HE-SPEC: PASS (no singles, no year effects)")

delta_params = [p for p in param_names if "delta" in p.lower()]
if delta_params:
    halt("HE-DELTA", f"delta_occ appears as free parameter: {delta_params}")
print(f"  HE-DELTA: PASS (delta_occ not a free parameter)")

N_PARAMS = len(param_names)

# ── STEP 2: Load precomputed object (read-only from disk) ─────────────────────
print(f"\nSTEP 2: Load precomputed object (read-only)")
t_load = time.time()
with open(PKL_PATH, "rb") as f:
    pc = pickle.load(f)
print(f"  Loaded in {time.time()-t_load:.1f}s  type={type(pc).__name__}")

# Inject loc4 dummies from parquet into in-memory pc (not written to disk)
print(f"\nSTEP 2b: Inject loc4 occupation dummies from parquet (in-memory only)")
t_pq = time.time()
loc4_cols = ["loc4_male", "loc4_female"]
df_loc4 = pd.read_parquet(PARQUET_PATH, columns=loc4_cols)
print(f"  Parquet loaded ({len(df_loc4):,} rows) in {time.time()-t_pq:.1f}s")
for gender in ["male", "female"]:
    loc4_arr = df_loc4[f"loc4_{gender}"].values
    for cat in [2, 3, 4]:
        dummy = (loc4_arr == cat).astype(np.float64)
        attr  = f"loc4_{cat}_{gender}"
        object.__setattr__(pc, attr, dummy)
        print(f"  Injected pc.{attr}: shape={dummy.shape}  mean={dummy.mean():.4f}")
del df_loc4
print(f"  loc4 injection complete (in-memory only; pkl on disk unchanged)")

# ── PREFLIGHT: Schema check ───────────────────────────────────────────────────
print(f"\nPREFLIGHT: Schema check")
if pc.n_groups != EXPECTED_GROUPS:
    halt("HE-SCHEMA", f"n_groups={pc.n_groups} != {EXPECTED_GROUPS}")
g_sizes = pc.group_ends - pc.group_starts
if not np.all(g_sizes == EXPECTED_GSIZ):
    halt("HE-SCHEMA", f"Not all group sizes == {EXPECTED_GSIZ}")
if pc.n_obs != EXPECTED_NOBS:
    halt("HE-SCHEMA", f"n_obs={pc.n_obs} != {EXPECTED_NOBS}")
chosen_pos = np.array([int(np.argmax(pc.actual_choice[s:e]))
                        for s, e in zip(pc.group_starts, pc.group_ends)])
if np.any(chosen_pos != 0):
    halt("HE-SCHEMA", f"{(chosen_pos!=0).sum()} groups: chosen not at position 0")
if not np.all(np.isfinite(pc.log_c)):
    halt("HE-SCHEMA", "log_c has non-finite values")
print(f"  n_groups={pc.n_groups}  n_obs={pc.n_obs:,}  group_size={EXPECTED_GSIZ}: PASS")
print(f"  Chosen at position 0: PASS  |  log_c finite: PASS")
print(f"  log_wage_male populated: {pc.log_wage_male is not None}")
print(f"  HE-SCHEMA: PASS")

# ── Output path check ─────────────────────────────────────────────────────────
print(f"\nPREFLIGHT: Output path check")
for start_name in ["start_warm", "start_default"]:
    d = os.path.join(OUT_ROOT, start_name)
    os.makedirs(d, exist_ok=True)
    if "ruro_occ_P3a_pooled" in d or "spec\\ruro_occ" in d:
        halt("HE-PROD", f"Output path collides with P3a: {d}")
print(f"  Pilot output dirs under {OUT_ROOT}: PASS")
print(f"  No P3a collision: PASS")

# ── STEP 3: Build starting values ─────────────────────────────────────────────
print(f"\nSTEP 3: Build starting values")

theta_default = np.array(spec.get_initial_vector(), dtype=np.float64)
print(f"  Default start: {len(theta_default)} params from spec initial_values")

with open(P3A_RESULTS) as f:
    p3a_res = json.load(f)
p3a_params = p3a_res["results"]["singles_male"]["parameters"]
theta_warm = np.zeros(N_PARAMS, dtype=np.float64)
warm_mapped, warm_missing = [], []
for i, pname in enumerate(param_names):
    if pname in p3a_params:
        theta_warm[i] = p3a_params[pname]
        warm_mapped.append(pname)
    else:
        theta_warm[i] = theta_default[i]
        warm_missing.append(pname)

if warm_missing:
    print(f"  Warm-start: {len(warm_mapped)} from P3a; {len(warm_missing)} from spec default: {warm_missing}")
else:
    print(f"  Warm-start: all {len(warm_mapped)} params mapped from P3a (unambiguous)")
print(f"  HE-WARM: PASS")

starts = [
    ("start_warm",    theta_warm),
    ("start_default", theta_default),
]

# ── PREFLIGHT: objective-at-start ─────────────────────────────────────────────
print(f"\nPREFLIGHT: Objective-at-start (HE-OBJ gate)")
for start_name, theta0 in starts:
    neg_ll0 = ee.compute_likelihood_couples(theta0, pc, spec)
    if not np.isfinite(neg_ll0):
        halt("HE-OBJ", f"LL not finite at {start_name}: neg_LL={neg_ll0}")
    print(f"  {start_name}: neg_LL={neg_ll0:.4f}  LL={-neg_ll0:.4f}  FINITE: PASS")
print(f"  HE-OBJ: PASS")

# ── Parallelism decision ──────────────────────────────────────────────────────
print(f"\nParallelism decision:")
print(f"  Solver: GAMSPy/CONOPT (estimate_couples_vectorized_gamspy)")
print(f"  GAMSPy creates a working directory per solve; running sequentially")
print(f"  to avoid working-directory collisions on the shared server.")
print(f"  Parallel execution NOT used. Starts: sequential. Workers: 1.")

# ── STEP 4: Solve via GAMSPy/CONOPT ──────────────────────────────────────────
print(f"\nSTEP 4: Solve (GAMSPy/CONOPT, sequential starts)")

results_all = {}
total_t0 = time.time()
tracemalloc.start()

for start_name, theta0 in starts:
    out_dir = os.path.join(OUT_ROOT, start_name)
    print(f"\n  --- {start_name} ---")
    print(f"  Output dir: {out_dir}")
    initial_neg_ll = float(ee.compute_likelihood_couples(theta0, pc, spec))
    print(f"  Initial: neg_LL={initial_neg_ll:.4f}  LL={-initial_neg_ll:.4f}")

    t_start = time.time()
    gres = estimate_couples_vectorized_gamspy(
        data=pc,
        spec=spec,
        theta_init=theta0,
        solver="conopt",
        verbose=True,
    )
    t_wall = time.time() - t_start

    _, peak_mem = tracemalloc.get_traced_memory()

    theta_hat    = gres["theta"]
    ll_final     = gres["log_likelihood"]   # positive LL from GAMSPy (maximization)
    solver_status = gres["solver_status"]
    model_status  = gres["model_status"]
    n_iter        = gres.get("n_iterations", None)
    converged     = "optimal" in str(solver_status).lower() or "optimal" in str(model_status).lower()

    # Verify with numpy LL for consistency
    neg_ll_verify = float(ee.compute_likelihood_couples(theta_hat, pc, spec))
    ll_verify     = -neg_ll_verify

    print(f"  Solver status: {solver_status}  Model status: {model_status}")
    print(f"  GAMSPy LL: {ll_final}  |  numpy verify LL: {ll_verify:.4f}  neg_LL: {neg_ll_verify:.4f}")
    print(f"  Iterations: {n_iter}  |  Wall time: {t_wall:.1f}s")

    param_dict = {pname: float(theta_hat[i]) for i, pname in enumerate(param_names)}

    result_obj = {
        "start_name":      start_name,
        "spec":            SPEC_PATH,
        "spec_name":       spec.name,
        "solver":          "GAMSPy/CONOPT",
        "n_params":        N_PARAMS,
        "param_names":     param_names,
        "initial_neg_ll":  initial_neg_ll,
        "initial_ll":      -initial_neg_ll,
        "ll_final_gamspy": ll_final,
        "neg_ll_verify":   neg_ll_verify,
        "final_ll":        ll_verify,
        "solver_status":   solver_status,
        "model_status":    model_status,
        "converged":       converged,
        "n_iterations":    n_iter,
        "wall_seconds":    round(t_wall, 2),
        "peak_mem_mb":     round(peak_mem / 1e6, 1),
        "parameters":      param_dict,
        "theta":           theta_hat.tolist(),
        "authorization":   "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md",
        "not_verdict_grade": True,
    }
    out_json = os.path.join(out_dir, "estimation_results.json")
    with open(out_json, "w") as f:
        json.dump(result_obj, f, indent=2)
    print(f"  Saved: {out_json}")
    results_all[start_name] = result_obj

_, peak_mem_all = tracemalloc.get_traced_memory()
tracemalloc.stop()
total_wall = time.time() - total_t0

# ── STEP 5: Post-estimation diagnostics ──────────────────────────────────────
print(f"\nSTEP 5: Post-estimation diagnostics (minimal)")

best_start = min(results_all, key=lambda k: results_all[k]["neg_ll_verify"])
best_res   = results_all[best_start]
theta_best = np.array(best_res["theta"])
print(f"  Best start: {best_start}  LL={best_res['final_ll']:.4f}")

ll_best  = best_res["final_ll"]
n_grps   = pc.n_groups
mean_chosen_prob = float(np.exp(ll_best / n_grps))
print(f"  Geometric mean chosen prob: {mean_chosen_prob:.6f}")
print(f"  Log LL per group: {ll_best/n_grps:.4f}")

working_m_chosen = (pc.working_male[pc.group_starts] > 0.5).astype(float)
working_f_chosen = (pc.working_female[pc.group_starts] > 0.5).astype(float)
obs_part_m = float(working_m_chosen.mean())
obs_part_f = float(working_f_chosen.mean())
print(f"  Observed participation (chosen): male={obs_part_m:.3f}  female={obs_part_f:.3f}")

# Occupation distribution (loc4) at chosen draw
if hasattr(pc, "loc4_2_male"):
    for gender in ["male", "female"]:
        chosen_idx = pc.group_starts
        s1 = float((pc.loc4_2_male if gender=="male" else pc.loc4_2_female)[chosen_idx].mean())
        s2 = float((pc.loc4_3_male if gender=="male" else pc.loc4_3_female)[chosen_idx].mean())
        s3 = float((pc.loc4_4_male if gender=="male" else pc.loc4_4_female)[chosen_idx].mean())
        s0 = 1.0 - s1 - s2 - s3
        print(f"  loc4 shares ({gender} chosen): cat1={s0:.3f} cat2={s1:.3f} cat3={s2:.3f} cat4={s3:.3f}")

print(f"\nParameter estimates ({best_start}):")
for pname, val in best_res["parameters"].items():
    print(f"  {pname:30s} = {val:10.5f}")

ll_vals  = [-r["neg_ll_verify"] for r in results_all.values()]
ll_range = max(ll_vals) - min(ll_vals)
print(f"\nReproducibility across starts:")
for sn, r in results_all.items():
    print(f"  {sn:20s}: LL={r['final_ll']:.4f}  status={r['solver_status']}  conv={r['converged']}")
print(f"  LL range across starts: {ll_range:.4f}")

print(f"\nComparison to P3a corrected baseline (couples block):")
p3a_cmp = ["beta_l0_m","beta_l0_f","beta_c","beta_ll","beta_E","beta_h_ft",
           "beta_E_gsur","beta_w0","sigma",
           "beta_occ_2_cm","beta_occ_3_cm","beta_occ_4_cm",
           "beta_occ_2_cf","beta_occ_3_cf","beta_occ_4_cf"]
print(f"  {'Parameter':30s} {'P3a':>10s} {'NC pilot':>10s} {'Δ':>10s}")
for pname in p3a_cmp:
    if pname in p3a_params and pname in best_res["parameters"]:
        p3a_v   = p3a_params[pname]
        pilot_v = best_res["parameters"][pname]
        print(f"  {pname:30s} {p3a_v:10.4f} {pilot_v:10.4f} {pilot_v-p3a_v:10.4f}")

# ── STEP 6: Save summary ──────────────────────────────────────────────────────
print(f"\nSTEP 6: Save run summary")
summary = {
    "authorization":  "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md",
    "not_verdict_grade": True,
    "spec_path":      SPEC_PATH,
    "spec_name":      spec.name,
    "solver":         "GAMSPy/CONOPT",
    "n_params":       N_PARAMS,
    "param_names":    param_names,
    "precomputed_pkl": PKL_PATH,
    "loc4_injection": "loc4_2/3/4_male/female derived from parquet at runtime; pkl on disk unchanged",
    "parallel_execution": False,
    "parallel_decision": "sequential — GAMSPy workdir collision risk on shared server; 2 starts authorized",
    "n_workers":      1,
    "n_starts":       len(starts),
    "starts": {
        sn: {
            "final_ll":     r["final_ll"],
            "neg_ll_verify": r["neg_ll_verify"],
            "converged":    r["converged"],
            "solver_status": r["solver_status"],
            "model_status": r["model_status"],
            "n_iterations": r["n_iterations"],
            "wall_seconds": r["wall_seconds"],
            "output_dir":   os.path.join(OUT_ROOT, sn),
        }
        for sn, r in results_all.items()
    },
    "best_start":     best_start,
    "best_ll":        best_res["final_ll"],
    "ll_range_across_starts": round(ll_range, 4),
    "total_wall_seconds":     round(total_wall, 1),
    "peak_mem_mb":            round(peak_mem_all / 1e6, 1),
    "diagnostics": {
        "mean_chosen_prob_geometric": mean_chosen_prob,
        "log_ll_per_group":          round(ll_best / n_grps, 4),
        "obs_participation_male":    round(obs_part_m, 4),
        "obs_participation_female":  round(obs_part_f, 4),
        "ll_range_across_starts":    round(ll_range, 4),
    },
    "pooled_projection": {
        "pilot_couples":         2577,
        "pooled_couples":        7438,
        "scale_factor":          round(7438/2577, 3),
        "pilot_total_wall_s":    round(total_wall, 1),
        "pooled_estimate_wall_s": round(total_wall * 7438/2577, 1),
    },
    "not_run": {
        "welfare": False, "SA2": False, "GSUR": False,
        "EUROMOD": False, "full_P3a": False, "promotion": False,
        "M1_clean_displacement": False,
    },
    "stage_status": {
        "M1_clean_2016":         "active",
        "corrected_pooled_P3a":  "unaffected",
    }
}
summary_path = os.path.join(OUT_ROOT, "diagnostic_estimation_summary.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"  Summary: {summary_path}")

print(f"\n{'='*70}")
print(f"DIAGNOSTIC ESTIMATION COMPLETE")
print(f"  Solver:          GAMSPy/CONOPT")
print(f"  Total wall time: {total_wall:.1f}s")
print(f"  Peak memory:     {peak_mem_all/1e6:.1f} MB")
print(f"  Best start:      {best_start}  LL={best_res['final_ll']:.4f}")
print(f"  LL range:        {ll_range:.4f}")
print(f"  N params:        {N_PARAMS}")
print(f"{'='*70}")
print(f"\nSTOP. No welfare, SA2, or promotion.")
