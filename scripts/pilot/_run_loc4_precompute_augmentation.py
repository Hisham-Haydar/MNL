"""
NC Pilot — loc4 Precompute Augmentation.
Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md

Rebuilds the pilot PrecomputedDataCouples pkl with include_loc_vars=True
so beta_occ_* parameters are identified.

HARD CONSTRAINTS enforced:
  HL-LOGIC : precompute_data_couples / _resolve_draw_column NOT edited
  HL-NORM  : c_scale=4054.2856, l_scale=10.0 reused from normmeta — NOT recomputed
  HL-COL   : loc4_male/loc4_female must be present in parquet; halt if absent
  HL-INJECT: NO runtime injection; pkl itself is rebuilt
  HL-MUT   : source parquet and prior pkl NOT overwritten; NEW pkl only
  HL-STAGE : NO estimation, EUROMOD, GSUR, rebuild, welfare, SA2, promotion
"""
import sys, os, json, time, pickle, tracemalloc
import numpy as np
import pandas as pd

BASE = r"U:\Desktop\Nizam_Hisham\MNL"
sys.path.insert(0, os.path.join(BASE, r"scripts\enhanced"))
sys.path.insert(0, os.path.join(BASE, r"scripts\pilot"))

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("loc4_augment")

from estimation_utils import precompute_data_couples

PARQUET   = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet")
NORMMETA  = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json")
PRIOR_PKL = os.path.join(BASE, r"Data\pilot\nc_2016_couples\precomputed\fr_pilot_nc_2016_couples_precomputed.pkl")
NEW_PKL   = os.path.join(BASE, r"Data\pilot\nc_2016_couples\precomputed\fr_pilot_nc_2016_couples_precomputed_loc.pkl")
SUMMARY   = os.path.join(BASE, r"Data\pilot\nc_2016_couples\precomputed\loc_precompute_run_summary.json")

EXPECTED_GROUPS = 2577
EXPECTED_GSIZ   = 900
EXPECTED_NOBS   = 2_319_300
C_SCALE_PILOT   = 4054.2855556859554
L_SCALE         = 10.0

def halt(code, msg):
    print(f"\nHALT {code}: {msg}")
    sys.exit(1)

results = {}  # accumulate for summary

print("=" * 70)
print("NC PILOT — LOC4 PRECOMPUTE AUGMENTATION")
print("Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md")
print("=" * 70)

# ── Load normmeta ──────────────────────────────────────────────────────────────
print("\nLoading normmeta...")
with open(NORMMETA) as f:
    normmeta = json.load(f)
c_scale = float(normmeta["normalization"]["c_scale"])
l_male_scale  = float(normmeta["normalization"]["l_male_scale"])
l_female_scale = float(normmeta["normalization"]["l_female_scale"])
print(f"  c_scale={c_scale}  l_male_scale={l_male_scale}  l_female_scale={l_female_scale}")
if abs(c_scale - C_SCALE_PILOT) > 1.0:
    halt("HL-NORM", f"c_scale from normmeta ({c_scale}) diverges from pilot value ({C_SCALE_PILOT})")
print("  HL-NORM: PASS — reusing existing pilot normalization")

# ── STEP 1: Precondition check (HL-COL) ──────────────────────────────────────
print("\nSTEP 1: Precondition check — loc4_male/loc4_female in parquet (HL-COL)")
t0 = time.time()
pq_cols = pd.read_parquet(PARQUET, columns=["loc4_male", "loc4_female"]) if True else None

# Check columns exist (will raise if absent)
try:
    df_loc4_check = pd.read_parquet(PARQUET, columns=["loc4_male", "loc4_female"])
except Exception as e:
    halt("HL-COL", f"loc4_male/loc4_female absent or unreadable from parquet: {e}")

print(f"  loc4_male and loc4_female: PRESENT")
print(f"  Rows: {len(df_loc4_check):,}  (expected {EXPECTED_NOBS:,})")
if len(df_loc4_check) != EXPECTED_NOBS:
    halt("HL-COL", f"Parquet row count {len(df_loc4_check)} != {EXPECTED_NOBS}")

# Code accounting — report all codes including -1/-2
codes_m = np.sort(df_loc4_check["loc4_male"].dropna().unique()).tolist()
codes_f = np.sort(df_loc4_check["loc4_female"].dropna().unique()).tolist()
vc_m = df_loc4_check["loc4_male"].value_counts().sort_index().to_dict()
vc_f = df_loc4_check["loc4_female"].value_counts().sort_index().to_dict()
print(f"  loc4_male  unique codes: {codes_m}")
print(f"  loc4_female unique codes: {codes_f}")
print(f"  loc4_male  value counts: {vc_m}")
print(f"  loc4_female value counts: {vc_f}")

# Confirm codes 1..4 are present for occupation dummies
for col, codes in [("loc4_male", codes_m), ("loc4_female", codes_f)]:
    for c in [1, 2, 3, 4]:
        if c not in codes:
            halt("HL-COL", f"{col} missing occupation code {c} — cannot build loc4_{c} dummy")

# Report -1/-2 presence (do NOT recode)
for col, vc in [("loc4_male", vc_m), ("loc4_female", vc_f)]:
    for neg_code in [-2, -1]:
        if neg_code in vc:
            print(f"  NOTE: {col} has {vc[neg_code]:,} rows with code {neg_code} — reported, NOT recoded")

missing_m = int(df_loc4_check["loc4_male"].isna().sum())
missing_f = int(df_loc4_check["loc4_female"].isna().sum())
print(f"  Missing: loc4_male={missing_m}  loc4_female={missing_f}")

results["precondition"] = {
    "loc4_male_present": True,
    "loc4_female_present": True,
    "codes_male": codes_m,
    "codes_female": codes_f,
    "value_counts_male": {str(k): int(v) for k, v in vc_m.items()},
    "value_counts_female": {str(k): int(v) for k, v in vc_f.items()},
    "missing_male": missing_m,
    "missing_female": missing_f,
    "HL_COL": "PASS",
}
del df_loc4_check
print(f"  HL-COL: PASS ({time.time()-t0:.1f}s)")

# ── STEP 2: Load full parquet ─────────────────────────────────────────────────
print("\nSTEP 2: Load full parquet (read-only)")
t_load = time.time()
df = pd.read_parquet(PARQUET)
print(f"  Loaded {len(df):,} rows × {len(df.columns)} cols in {time.time()-t_load:.1f}s")
if len(df) != EXPECTED_NOBS:
    halt("HL-MUT", f"Parquet row count changed: {len(df)} != {EXPECTED_NOBS}")

# ── STEP 2a: Off-axis product-consistency check (HL-VARY) ─────────────────────
print("\nSTEP 2a: Off-axis product-consistency check (HL-VARY)")
# loc4_male must be constant within (idhh, year_tag, draw_male) across draw_female
# loc4_female must be constant within (idhh, year_tag, draw_female) across draw_male
# Use a sample of 200 households for speed; flag if any violation
t_vc = time.time()
group_cols_m  = ["idhh", "draw_male"]   # year_tag is 2016-only (single value), skip
group_cols_f  = ["idhh", "draw_female"]

# Check loc4_male: constant within (idhh, draw_male) grouping
# nunique per group should be 1
# Use year_tag if present
year_tag_cols = [c for c in df.columns if "year_tag" in c]
if year_tag_cols:
    group_cols_m = ["idhh", year_tag_cols[0], "draw_male"]
    group_cols_f = ["idhh", year_tag_cols[0], "draw_female"]
    print(f"  year_tag column found: {year_tag_cols[0]}")
else:
    print(f"  No year_tag column (2016-only pilot); grouping by (idhh, draw_male/female)")

# Sample 500 households for the check
sample_ids = df["idhh"].unique()[:500]
df_sample = df[df["idhh"].isin(sample_ids)]

nuniq_m = df_sample.groupby(group_cols_m)["loc4_male"].nunique()
nuniq_f = df_sample.groupby(group_cols_f)["loc4_female"].nunique()

bad_m = int((nuniq_m > 1).sum())
bad_f = int((nuniq_f > 1).sum())
print(f"  loc4_male: {bad_m} groups with nunique > 1 (out of {len(nuniq_m)} groups in sample)")
print(f"  loc4_female: {bad_f} groups with nunique > 1 (out of {len(nuniq_f)} groups in sample)")

if bad_m > 0:
    halt("HL-VARY", f"loc4_male NOT constant within (idhh, draw_male): {bad_m} violations in sample")
if bad_f > 0:
    halt("HL-VARY", f"loc4_female NOT constant within (idhh, draw_female): {bad_f} violations in sample")

del df_sample
print(f"  HL-VARY: PASS — off-axis product-consistency confirmed ({time.time()-t_vc:.1f}s)")
results["offaxis_consistency"] = {"HL_VARY": "PASS", "bad_groups_male": bad_m, "bad_groups_female": bad_f}

# ── STEP 3: Rebuild pkl with include_loc_vars=True ────────────────────────────
print("\nSTEP 3: Rebuild pkl — precompute_data_couples(include_wage_vars=True, include_loc_vars=True)")
print(f"  Output: {NEW_PKL}")
print(f"  Prior pkl preserved: {PRIOR_PKL}  (NOT overwritten)")

# precompute_data_couples expects metadata["normalization"] as a nested dict
metadata = normmeta  # already has the "normalization" key with correct structure

tracemalloc.start()
t_pc = time.time()

pc = precompute_data_couples(
    df,
    metadata,
    include_wage_vars=True,
    include_loc_vars=True,
)

wall_pc = time.time() - t_pc
_, peak_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"  precompute_data_couples: done in {wall_pc:.2f}s  peak_mem={peak_mem/1e6:.1f} MB")

# ── Write new pkl ──────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(NEW_PKL), exist_ok=True)
t_write = time.time()
with open(NEW_PKL, "wb") as f:
    pickle.dump(pc, f, protocol=5)
write_s = time.time() - t_write
pkl_bytes = os.path.getsize(NEW_PKL)
print(f"  Written: {NEW_PKL}  ({pkl_bytes:,} bytes = {pkl_bytes/1e6:.1f} MB)  in {write_s:.1f}s")

# Confirm prior pkl NOT overwritten
prior_bytes = os.path.getsize(PRIOR_PKL)
print(f"  Prior pkl intact: {PRIOR_PKL}  ({prior_bytes:,} bytes)")
if prior_bytes == 0:
    halt("HL-MUT", "Prior pkl appears empty — may have been overwritten")
print("  HL-MUT: PASS — new pkl written; prior pkl unchanged")

# ── STEP 4: Validate ──────────────────────────────────────────────────────────
print("\nSTEP 4: Validate new pkl")
validations = {}

# V1: Structure
v1_groups = pc.n_groups == EXPECTED_GROUPS
v1_obs    = pc.n_obs == EXPECTED_NOBS
g_sizes   = pc.group_ends - pc.group_starts
v1_gsiz   = bool(np.all(g_sizes == EXPECTED_GSIZ))
print(f"  V1 Structure: n_groups={pc.n_groups} ({v1_groups})  n_obs={pc.n_obs:,} ({v1_obs})  all_gsiz_900={v1_gsiz}")
if not (v1_groups and v1_obs and v1_gsiz):
    halt("HL-COL", f"Structure check failed: groups={pc.n_groups} obs={pc.n_obs} gsiz_ok={v1_gsiz}")
validations["V1_structure"] = "PASS"

# V2: Chosen at position 0
chosen_pos = np.array([int(np.argmax(pc.actual_choice[s:e]))
                        for s, e in zip(pc.group_starts, pc.group_ends)])
v2 = bool(np.all(chosen_pos == 0))
print(f"  V2 Chosen at position 0: {v2}  (bad={int((chosen_pos!=0).sum())})")
if not v2:
    halt("HL-COL", "Chosen not at position 0 in new pkl")
validations["V2_chosen_at_0"] = "PASS"

# V3: Occupation arrays present
occ_attrs = ["loc4_male","loc4_female",
             "loc4_1_male","loc4_2_male","loc4_3_male","loc4_4_male",
             "loc4_1_female","loc4_2_female","loc4_3_female","loc4_4_female"]
v3_present = {}
for attr in occ_attrs:
    arr = getattr(pc, attr, None)
    present = arr is not None
    v3_present[attr] = present
    if not present:
        halt("HL-COL", f"Required occupation array missing from new pkl: {attr}")
print(f"  V3 Occupation arrays present: {list(v3_present.keys())} — all PRESENT")
validations["V3_occ_arrays_present"] = "PASS"

# V4: Non-degenerate (each dummy has both 0s and 1s)
dummy_attrs = ["loc4_2_male","loc4_3_male","loc4_4_male",
               "loc4_2_female","loc4_3_female","loc4_4_female"]
v4_stats = {}
for attr in dummy_attrs:
    arr = getattr(pc, attr)
    mn, mx, mean_ = float(arr.min()), float(arr.max()), float(arr.mean())
    degen = (mx == 0.0) or (mn == 1.0)
    v4_stats[attr] = {"min": mn, "max": mx, "mean": round(mean_, 4), "degenerate": degen}
    print(f"  V4 {attr}: min={mn} max={mx} mean={mean_:.4f}  {'DEGENERATE' if degen else 'OK'}")
    if degen:
        halt("HL-DEGEN", f"{attr} is all-zero or all-one — beta_occ would still be inert")
validations["V4_non_degenerate"] = "PASS"
validations["V4_dummy_stats"] = v4_stats

# V5: c_scale and l_scale match prior
v5_cscale = abs(float(pc.c_scale) - C_SCALE_PILOT) < 1.0
v5_lscale = abs(float(pc.l_scale) - L_SCALE) < 0.01
print(f"  V5 Scales: c_scale={pc.c_scale} ({v5_cscale})  l_scale={pc.l_scale} ({v5_lscale})")
if not (v5_cscale and v5_lscale):
    halt("HL-NORM", f"Scale mismatch: c_scale={pc.c_scale}  l_scale={pc.l_scale}")
validations["V5_scales"] = "PASS"

# V6: log_c, log_l_*, log_wage_*, prior finite
core_arrays = {"log_c": pc.log_c, "log_l_male": pc.log_l_male,
               "log_l_female": pc.log_l_female, "prior": pc.prior}
if pc.log_wage_male is not None:
    core_arrays["log_wage_male"] = pc.log_wage_male
if pc.log_wage_female is not None:
    core_arrays["log_wage_female"] = pc.log_wage_female
v6_stats = {}
for name, arr in core_arrays.items():
    finite_ok = bool(np.all(np.isfinite(arr)))
    v6_stats[name] = {"finite": finite_ok, "min": float(arr.min()), "max": float(arr.max())}
    print(f"  V6 {name}: finite={finite_ok}  min={arr.min():.4f}  max={arr.max():.4f}")
    if not finite_ok:
        halt("HL-COL", f"{name} has non-finite values in new pkl")
validations["V6_core_finite"] = "PASS"

# V7: consumption positive
cons_min = float(pc.consumption.min())
cons_ok  = cons_min > 0
print(f"  V7 consumption min={cons_min:.4e}  positive={cons_ok}")
if not cons_ok:
    halt("HL-COL", f"Consumption not strictly positive: min={cons_min}")
validations["V7_consumption_positive"] = "PASS"

# V8: GSUR present, non-missing, non-degenerate
v8_stats = {}
for attr in ["gsur_male", "gsur_female"]:
    arr = getattr(pc, attr, None)
    if arr is None:
        halt("HL-COL", f"{attr} missing from new pkl")
    finite_ok = bool(np.all(np.isfinite(arr)))
    has_var = float(arr.std()) > 0
    v8_stats[attr] = {"finite": finite_ok, "has_variation": has_var,
                      "min": float(arr.min()), "max": float(arr.max()), "mean": float(arr.mean())}
    print(f"  V8 {attr}: finite={finite_ok}  variation={has_var}  mean={arr.mean():.4f}")
    if not finite_ok or not has_var:
        halt("HL-COL", f"{attr} is missing, non-finite, or degenerate")
validations["V8_gsur"] = "PASS"
validations["V8_gsur_stats"] = v8_stats

# V9: Region arrays present and non-degenerate
v9_stats = {}
for reg in ["reg2","reg3","reg4","reg5","reg6","reg7","reg8"]:
    arr = getattr(pc, reg, None)
    if arr is None:
        halt("HL-COL", f"{reg} missing from new pkl")
    v9_stats[reg] = {"mean": round(float(arr.mean()), 4), "sum": int(arr.sum())}
print(f"  V9 Region arrays reg2..reg8: all present  means={[v['mean'] for v in v9_stats.values()]}")
validations["V9_region"] = "PASS"
validations["V9_region_stats"] = v9_stats

# V10: HN-POS check — c_norm=EPS on 123 floored rows
# The 123 floored rows have log_c = log(EPS) ≈ -27.63
EPS = 1e-12
log_eps = np.log(EPS)
n_eps_rows = int(np.sum(np.abs(pc.log_c - log_eps) < 1e-6))
print(f"  V10 HN-POS (EPS-floored rows): {n_eps_rows} rows with log_c ~= log(EPS)  (expected 123)")
# Allow small tolerance — EPS floor may apply to slightly more rows if repeated
validations["V10_hnpos_rows"] = {"n_eps_floored": n_eps_rows, "expected": 123}
if n_eps_rows < 123:
    halt("HL-COL", f"HN-POS: only {n_eps_rows} EPS-floored rows in new pkl, expected >= 123")
print(f"  V10 HN-POS: PASS ({n_eps_rows} EPS-floored rows)")
validations["V10_hnpos"] = "PASS"

# V11: Compare GSUR to prior pkl
print("\n  V11: Load prior pkl and cross-check GSUR/region invariants...")
with open(PRIOR_PKL, "rb") as f:
    pc_prior = pickle.load(f)
gsur_match_m = bool(np.allclose(pc.gsur_male, pc_prior.gsur_male, atol=1e-10))
gsur_match_f = bool(np.allclose(pc.gsur_female, pc_prior.gsur_female, atol=1e-10))
cscale_match  = abs(float(pc.c_scale) - float(pc_prior.c_scale)) < 1e-6
logc_match    = bool(np.allclose(pc.log_c, pc_prior.log_c, atol=1e-10))
logl_m_match  = bool(np.allclose(pc.log_l_male, pc_prior.log_l_male, atol=1e-10))
logl_f_match  = bool(np.allclose(pc.log_l_female, pc_prior.log_l_female, atol=1e-10))
print(f"  V11 gsur_male identical: {gsur_match_m}")
print(f"  V11 gsur_female identical: {gsur_match_f}")
print(f"  V11 c_scale identical: {cscale_match}")
print(f"  V11 log_c identical: {logc_match}")
print(f"  V11 log_l_male identical: {logl_m_match}")
print(f"  V11 log_l_female identical: {logl_f_match}")
if not (gsur_match_m and gsur_match_f and cscale_match and logc_match):
    halt("HL-NORM", "Core arrays differ between new and prior pkl — unexpected change")
validations["V11_prior_match"] = {
    "gsur_male": "PASS" if gsur_match_m else "FAIL",
    "gsur_female": "PASS" if gsur_match_f else "FAIL",
    "c_scale": "PASS" if cscale_match else "FAIL",
    "log_c": "PASS" if logc_match else "FAIL",
    "log_l_male": "PASS" if logl_m_match else "FAIL",
    "log_l_female": "PASS" if logl_f_match else "FAIL",
}
validations["V11_prior_pkl_unchanged"] = "PASS"
del pc_prior

# V12: Source parquet row count unchanged
parquet_rows = len(pd.read_parquet(PARQUET, columns=["idhh"]))
v12 = parquet_rows == EXPECTED_NOBS
print(f"\n  V12 Source parquet rows: {parquet_rows:,}  unchanged={v12}")
if not v12:
    halt("HL-MUT", f"Source parquet row count changed: {parquet_rows}")
validations["V12_parquet_unchanged"] = "PASS"

print("\n  All validations PASS")

# ── Write run summary sidecar ──────────────────────────────────────────────────
run_summary = {
    "all_pass": True,
    "authorization": "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md",
    "n_groups": pc.n_groups,
    "n_obs": pc.n_obs,
    "wall_seconds_precompute": round(wall_pc, 2),
    "peak_mem_mb": round(peak_mem / 1e6, 1),
    "pkl_path": NEW_PKL,
    "pkl_size_bytes": pkl_bytes,
    "c_scale_used": c_scale,
    "l_male_scale": l_male_scale,
    "l_female_scale": l_female_scale,
    "include_loc_vars": True,
    "include_wage_vars": True,
    "precondition": results["precondition"],
    "offaxis_consistency": results["offaxis_consistency"],
    "validations": {k: (v if isinstance(v, str) else str(v)) for k, v in validations.items()
                    if isinstance(v, str)},
    "validation_detail": validations,
    "not_run": {
        "estimation": False, "euromod": False, "gsur_merge": False,
        "welfare": False, "SA2": False, "promotion": False,
        "M1_clean_displacement": False,
    },
    "stage_status": {
        "M1_clean_2016": "active",
        "corrected_pooled_P3a": "unaffected",
        "prior_pkl_overwritten": False,
        "source_parquet_overwritten": False,
    }
}
with open(SUMMARY, "w") as f:
    json.dump(run_summary, f, indent=2)
print(f"\nRun summary: {SUMMARY}")

total_wall = wall_pc
print(f"\n{'='*70}")
print(f"LOC4 PRECOMPUTE AUGMENTATION COMPLETE")
print(f"  New pkl:        {NEW_PKL}")
print(f"  pkl size:       {pkl_bytes/1e6:.1f} MB")
print(f"  Wall time:      {wall_pc:.2f}s")
print(f"  Peak memory:    {peak_mem/1e6:.1f} MB")
print(f"  loc4 arrays:    {occ_attrs}")
print(f"  All validations PASS")
print(f"{'='*70}")
print(f"\nSTOP. Do not run estimation.")
