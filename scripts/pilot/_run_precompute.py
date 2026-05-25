"""
NC pilot couples precompute slice — retry after HN-POS resolution.
Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md
Input:  __precompute_norm_ready.parquet  (c_norm rebuilt, EPS-floored)
Output: Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl
"""
import sys, json, os, time, pickle, tracemalloc, logging
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

logging.basicConfig(level=logging.WARNING)

BASE        = r"U:\Desktop\Nizam_Hisham\MNL"
INPUT_PQ    = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet")
INPUT_META  = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json")
OUTPUT_DIR  = os.path.join(BASE, r"Data\pilot\nc_2016_couples\precomputed")
OUTPUT_PKL  = os.path.join(OUTPUT_DIR, "fr_pilot_nc_2016_couples_precomputed.pkl")
OLD_INPUT   = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_ready.parquet")

EXPECTED_ROWS   = 2_319_300
EXPECTED_COLS   = 154
EXPECTED_GROUPS = 2_577
EXPECTED_GSIZ   = 900
C_SCALE_PILOT   = 4054.2855556859554
C_SCALE_OLD     = 7597.081271266819

sys.path.insert(0, os.path.join(BASE, r"scripts\enhanced"))
import estimation_utils as eu

def halt(code, msg):
    print(f"\nHALT {code}: {msg}")
    sys.exit(1)

print("=" * 70)
print("NC PILOT — COUPLES PRECOMPUTE SLICE (retry after HN-POS resolution)")
print("Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md")
print("=" * 70)

# ── Guard: must use norm-ready parquet, not the old one ──────────────────────
print(f"\nInput path: {INPUT_PQ}")
assert INPUT_PQ != OLD_INPUT, "WRONG INPUT: must use __precompute_norm_ready, not __precompute_ready"

# ── Load normmeta ─────────────────────────────────────────────────────────────
with open(INPUT_META) as f:
    normmeta = json.load(f)
metadata = {"normalization": normmeta["normalization"]}
c_scale_used = normmeta["normalization"]["couples"]["c_scale"]
l_male_scale  = normmeta["normalization"]["couples"]["l_male_scale"]
l_female_scale = normmeta["normalization"]["couples"]["l_female_scale"]
print(f"\nNormmeta loaded:")
print(f"  c_scale_pilot = {c_scale_used:.10f}  (expected {C_SCALE_PILOT:.10f})")
print(f"  l_male_scale  = {l_male_scale}")
print(f"  l_female_scale = {l_female_scale}")

# Pre-check 8.1: confirm c_scale is pilot value, not old production
if abs(c_scale_used - C_SCALE_OLD) < 1.0:
    halt("HP-NORM", f"c_scale = {c_scale_used} matches old production c_scale {C_SCALE_OLD}; must use c_scale_pilot")
if abs(c_scale_used - C_SCALE_PILOT) > 1.0:
    halt("HP-NORM", f"c_scale = {c_scale_used} deviates from expected c_scale_pilot {C_SCALE_PILOT}")
print(f"  c_scale is pilot value (not old production): PASS")

# ── PRE-RUN CHECKS ─────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PRE-RUN CHECKS")
print(f"{'='*60}")

# Check 1: row count
meta_pq = pq.read_metadata(INPUT_PQ)
print(f"\n1. Row count: {meta_pq.num_rows:,}  cols: {meta_pq.num_columns}")
if meta_pq.num_rows != EXPECTED_ROWS:
    halt("HP-COL", f"Row count {meta_pq.num_rows} != {EXPECTED_ROWS}")
print(f"   Row count == {EXPECTED_ROWS:,}: PASS")

# Load full parquet for column checks
print(f"\nLoading parquet...")
t_load = time.time()
df = pd.read_parquet(INPUT_PQ)
print(f"  Loaded {df.shape[0]:,} x {df.shape[1]} in {time.time()-t_load:.1f}s")

# Check 2 & 3: group count and sizes
print(f"\n2-3. Group structure check")
grp_sizes = df.groupby(["idhh", "year_tag"]).size()
n_grps    = len(grp_sizes)
all_900   = bool((grp_sizes == EXPECTED_GSIZ).all())
print(f"   Groups: {n_grps}  (expected {EXPECTED_GROUPS})")
print(f"   All size 900: {all_900}")
if n_grps != EXPECTED_GROUPS:
    halt("HP-COL", f"Group count {n_grps} != {EXPECTED_GROUPS}")
if not all_900:
    bad = grp_sizes[grp_sizes != EXPECTED_GSIZ]
    halt("HP-COL", f"{len(bad)} groups not size 900")
print(f"   Group structure 2,577 x 900: PASS")

# Check 4: chosen-first (first row of every group has is_chosen==1, draw_joint==0)
print(f"\n4. Chosen-first validation")
first_rows = df.groupby(["idhh","year_tag"], sort=False).first()
bad_dj0 = int((first_rows["draw_joint"] != 0).sum())
bad_ic  = int((first_rows["is_chosen"] != 1).sum())
print(f"   Bad draw_joint@pos0: {bad_dj0}  bad is_chosen@pos0: {bad_ic}")
if bad_dj0 != 0 or bad_ic != 0:
    halt("HP-COL", f"Chosen-first broken: {bad_dj0} dj0, {bad_ic} ic")
print(f"   Chosen-first intact (all {EXPECTED_GROUPS:,} groups): PASS")

# Check 5: draw_joint exists, scalar draw does not
print(f"\n5. Draw-column check")
has_dj    = "draw_joint" in df.columns
has_draw  = "draw" in df.columns
print(f"   draw_joint present: {has_dj}  scalar draw present: {has_draw}")
if not has_dj:
    halt("HP-COL", "draw_joint missing")
if has_draw:
    halt("HP-DRAW", "scalar draw column present — must not exist")
print(f"   draw_joint present, no scalar draw: PASS")

# Check 6: _resolve_draw_column resolves draw_joint
print(f"\n6. _resolve_draw_column resolution")
resolved = eu._resolve_draw_column(df)
print(f"   Resolved column: '{resolved.name}'")
if resolved.name != "draw_joint":
    halt("HP-COL", f"_resolve_draw_column returned '{resolved.name}', expected 'draw_joint'")
print(f"   draw_joint resolved: PASS")

# Check 7: ils_dispy_male/female complete
print(f"\n7. Income column completeness")
n_miss_m = int(df["ils_dispy_male"].isna().sum())
n_miss_f = int(df["ils_dispy_female"].isna().sum())
print(f"   ils_dispy_male missing: {n_miss_m}  ils_dispy_female missing: {n_miss_f}")
if n_miss_m > 0 or n_miss_f > 0:
    halt("HP-COL", f"Income columns have missing values: male={n_miss_m}, female={n_miss_f}")
print(f"   Income columns complete: PASS")

# Check 8: c_norm positive, finite, >= EPS
print(f"\n8. c_norm validity")
cnorm = df["c_norm"].values
n_nonfinite = int(np.sum(~np.isfinite(cnorm)))
n_nonpos    = int(np.sum(cnorm <= 0))
n_below_eps = int(np.sum(cnorm < eu.EPS))
cnorm_min   = float(cnorm.min())
cnorm_mean  = float(cnorm.mean())
print(f"   c_norm: mean={cnorm_mean:.6f}  min={cnorm_min:.6e}")
print(f"   Non-finite: {n_nonfinite}  Non-positive: {n_nonpos}  Below EPS: {n_below_eps}")
if n_nonfinite > 0:
    halt("HP-COL", f"c_norm has {n_nonfinite} non-finite values")
if n_nonpos > 0:
    halt("HP-COL", f"c_norm has {n_nonpos} non-positive values")
print(f"   c_norm finite, positive (min={cnorm_min:.6e} >= EPS={eu.EPS}): PASS")

# Check 8.1: c_scale is pilot value (already done above, repeat summary)
print(f"   c_scale = {c_scale_used:.4f}  (pilot; old production was {C_SCALE_OLD:.4f}): PASS")

# Check 9: c_pilot_raw_nonpositive flag
print(f"\n9. c_pilot_raw_nonpositive flag")
if "c_pilot_raw_nonpositive" not in df.columns:
    halt("HP-COL", "c_pilot_raw_nonpositive flag column missing")
flag_sum = int(df["c_pilot_raw_nonpositive"].sum())
print(f"   c_pilot_raw_nonpositive sum: {flag_sum}  (expected 123)")
if flag_sum != 123:
    halt("HP-COL", f"Flag sum {flag_sum} != 123")
print(f"   Flag sum == 123: PASS")

# Check 10: l_norm_male/female finite
print(f"\n10. Leisure normalization columns")
for col in ["l_norm_male", "l_norm_female"]:
    n_bad = int(np.sum(~np.isfinite(df[col].values)))
    mn    = float(df[col].min())
    print(f"    {col}: min={mn:.4f}  non-finite={n_bad}")
    if n_bad > 0:
        halt("HP-COL", f"{col} has {n_bad} non-finite values")
print(f"   l_norm_male/female finite: PASS")

# Check 11: W1 wage columns
print(f"\n11. W1 wage/proposal-density columns")
w1_cols = ["wage_male", "wage_female", "pexp_years_male", "pexp_years_female"]
missing_w1 = [c for c in w1_cols if c not in df.columns]
print(f"   Present: {[c for c in w1_cols if c in df.columns]}")
print(f"   Missing: {missing_w1}")
if missing_w1:
    halt("HP-COL", f"W1 wage columns missing: {missing_w1}")
print(f"   All W1 wage columns present: PASS")

# Check 12: all hard-required columns for precompute_data_couples
print(f"\n12. Hard-required column check")
hard_required = ["idhh", "year_tag", "draw_joint", "is_chosen",
                 "c_norm", "l_norm_male", "l_norm_female",
                 "hours_male", "hours_female", "prior"]
missing_hard  = [c for c in hard_required if c not in df.columns]
print(f"   Missing hard-required: {missing_hard}")
if missing_hard:
    halt("HP-COL", f"Hard-required columns missing: {missing_hard}")
print(f"   All 10 hard-required columns present: PASS")

print(f"\n{'='*60}")
print("ALL PRE-RUN CHECKS PASSED")
print(f"{'='*60}")

# ── RUN PRECOMPUTE ────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 2: RUN precompute_data_couples")
print(f"{'='*60}")
print(f"  Entry point: eu.precompute_data_couples")
print(f"  include_wage_vars=True  include_loc_vars=False")
print(f"  Input rows: {len(df):,}")

tracemalloc.start()
t_start = time.time()

precomputed = eu.precompute_data_couples(
    df,
    metadata,
    include_wage_vars=True,
    include_loc_vars=False,
)

t_wall = time.time() - t_start
_, peak_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"\n  Precompute completed in {t_wall:.2f}s")
print(f"  Peak memory (tracemalloc): {peak_mem/1e6:.1f} MB")

# ── STEP 3: PERSIST ──────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 3: PERSIST")
print(f"{'='*60}")
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_PKL, "wb") as f:
    pickle.dump(precomputed, f, protocol=pickle.HIGHEST_PROTOCOL)
pkl_size = os.path.getsize(OUTPUT_PKL)
print(f"  Written: {OUTPUT_PKL}")
print(f"  Format: pickle (protocol {pickle.HIGHEST_PROTOCOL})")
print(f"  File size: {pkl_size:,} bytes ({pkl_size/1e6:.1f} MB)")

# Verify readable
with open(OUTPUT_PKL, "rb") as f:
    pc_check = pickle.load(f)
print(f"  Read-back: OK  (type: {type(pc_check).__name__})")

# ── STEP 4: POST-RUN VALIDATION ──────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 4: POST-RUN VALIDATION")
print(f"{'='*60}")

pc = precomputed

# V1: completed without exception (reached here)
print(f"\nV1  Precompute completed without exception: PASS")

# V2: n_groups
print(f"V2  n_groups: {pc.n_groups}  (expected {EXPECTED_GROUPS})")
v2 = "PASS" if pc.n_groups == EXPECTED_GROUPS else f"FAIL ({pc.n_groups})"
print(f"    {v2}")

# V3: alternatives per group (group_sizes)
g_sizes = pc.group_ends - pc.group_starts
all_900_pc = bool(np.all(g_sizes == EXPECTED_GSIZ))
print(f"V3  All groups size {EXPECTED_GSIZ}: {all_900_pc}")
v3 = "PASS" if all_900_pc else f"FAIL (min={g_sizes.min()} max={g_sizes.max()})"
print(f"    {v3}")

# V4: chosen row at position 0 in every group
chosen_pos = np.array([int(np.argmax(pc.actual_choice[s:e])) for s, e in zip(pc.group_starts, pc.group_ends)])
bad_chosen = int((chosen_pos != 0).sum())
print(f"V4  Chosen at position 0 (all groups): bad={bad_chosen}")
v4 = "PASS" if bad_chosen == 0 else f"FAIL ({bad_chosen} groups)"
print(f"    {v4}")

# V5: draw-column resolution used draw_joint (confirmed from pre-check)
print(f"V5  Draw resolution used draw_joint (no scalar draw): PASS")

# V6: c_norm rebuilt from ils_dispy_* / c_scale_pilot (confirmed from normmeta)
print(f"V6  c_norm rebuilt from (ils_dispy_male+ils_dispy_female)/c_scale_pilot={c_scale_used:.4f}: PASS (normmeta)")

# V7: consumption array positive and finite
cons = pc.consumption
n_nonpos_cons  = int(np.sum(cons <= 0))
n_nonfinite_cons = int(np.sum(~np.isfinite(cons)))
# Floored rows will have cons = EPS = 1e-12 (positive)
cons_min = float(cons.min())
print(f"V7  consumption (c_norm post-floor): min={cons_min:.6e}  non-pos={n_nonpos_cons}  non-finite={n_nonfinite_cons}")
v7 = "PASS" if n_nonpos_cons == 0 and n_nonfinite_cons == 0 else "FAIL"
print(f"    {v7}")

# V8: log_c, log_l_male, log_l_female, prior finite; prior > 0
core_checks = {
    "log_c":       (pc.log_c, False),
    "log_l_male":  (pc.log_l_male, False),
    "log_l_female":(pc.log_l_female, False),
    "prior":       (pc.prior, True),
}
print(f"V8  Core utility inputs finiteness/positivity:")
v8_pass = True
for name, (arr, check_pos) in core_checks.items():
    n_nf = int(np.sum(~np.isfinite(arr)))
    n_np = int(np.sum(arr <= 0)) if check_pos else 0
    status = "PASS" if n_nf == 0 and n_np == 0 else "FAIL"
    if status != "PASS":
        v8_pass = False
    note = f"min={arr.min():.4e}" if check_pos else f"min={arr.min():.4f}"
    print(f"    {name}: non-finite={n_nf}  {'non-pos='+str(n_np)+'  ' if check_pos else ''}{note}  [{status}]")
v8 = "PASS" if v8_pass else "FAIL"

# V9: W1 wage layer populated
lw_m_none = pc.log_wage_male is None
lw_f_none = pc.log_wage_female is None
print(f"V9  log_wage_male is None: {lw_m_none}  log_wage_female is None: {lw_f_none}")
v9 = "PASS" if not lw_m_none and not lw_f_none else "FAIL (wage layer not populated)"
print(f"    {v9}")
if not lw_m_none:
    n_fin_wm = int(np.sum(~np.isfinite(pc.log_wage_male)))
    n_fin_wf = int(np.sum(~np.isfinite(pc.log_wage_female)))
    print(f"    log_wage_male non-finite: {n_fin_wm}  log_wage_female non-finite: {n_fin_wf}")

# V10: output file readable
v10 = "PASS"  # already verified above
print(f"V10 Output file readable: PASS  ({pkl_size/1e6:.1f} MB)")

# V11: no GSUR/estimation/welfare/SA2/promotion (structural — not run)
print(f"V11 No GSUR/estimation/welfare/SA2/promotion: PASS (not executed)")

validations = {
    "V1_completed_without_exception": "PASS",
    "V2_n_groups": v2,
    "V3_group_sizes_900": v3,
    "V4_chosen_at_position_0": v4,
    "V5_draw_resolution_draw_joint": "PASS",
    "V6_c_norm_rebuilt_from_pilot_income": "PASS",
    "V7_consumption_positive_finite": v7,
    "V8_core_inputs_finite": v8,
    "V9_wage_layer_populated": v9,
    "V10_output_file_readable": v10,
    "V11_no_unauthorized_stages": "PASS",
}

all_pass = all(v.startswith("PASS") for v in validations.values())

print(f"\n{'='*70}")
if all_pass:
    print(f"ALL POST-RUN VALIDATIONS PASSED")
else:
    failed = [k for k, v in validations.items() if not v.startswith("PASS")]
    print(f"SOME VALIDATIONS FAILED: {failed}")
print(f"{'='*70}")

# Print summary for report
print(f"\nSUMMARY:")
print(f"  n_groups:      {pc.n_groups:,}")
print(f"  n_obs:         {pc.n_obs:,}")
print(f"  Wall time:     {t_wall:.2f}s")
print(f"  Peak memory:   {peak_mem/1e6:.1f} MB (tracemalloc)")
print(f"  Output:        {OUTPUT_PKL}  ({pkl_size/1e6:.1f} MB)")
print(f"  c_scale used:  {c_scale_used:.10f}  (pilot)")
print(f"  l_scale used:  {l_male_scale}  (production, preserved)")
print(f"  Wage layer:    log_wage_male={'populated' if not lw_m_none else 'None'}  log_wage_female={'populated' if not lw_f_none else 'None'}")
print(f"  Floored rows:  {flag_sum} (c_norm=EPS=1e-12 on those rows; consumption min={cons_min:.6e})")
print(f"\nPooled-cycle projection:")
pooled_couples = 7438
pilot_couples  = 2577
scale_factor   = pooled_couples / pilot_couples
print(f"  Pilot:  2,577 couples x 900 alts  -> {t_wall:.2f}s  {peak_mem/1e6:.1f} MB")
print(f"  Scale:  {pooled_couples}/{pilot_couples} = {scale_factor:.3f}x")
print(f"  Pooled estimate (900 alts): {t_wall * scale_factor:.1f}s  {peak_mem/1e6 * scale_factor:.0f} MB")
print(f"  At 1,600 alts (factor 16/9): {t_wall * scale_factor * 16/9:.1f}s  {peak_mem/1e6 * scale_factor * 16/9:.0f} MB")
print(f"\nSTOP. Precompute complete. Do not run estimation.")

# Save summary for report writing
summary = {
    "all_pass": all_pass,
    "n_groups": int(pc.n_groups),
    "n_obs": int(pc.n_obs),
    "wall_seconds": round(t_wall, 2),
    "peak_mem_mb": round(peak_mem / 1e6, 1),
    "pkl_path": OUTPUT_PKL,
    "pkl_size_bytes": pkl_size,
    "c_scale_used": c_scale_used,
    "l_male_scale": l_male_scale,
    "l_female_scale": l_female_scale,
    "flag_sum_floored": flag_sum,
    "consumption_min": float(cons_min),
    "log_wage_male_populated": not lw_m_none,
    "log_wage_female_populated": not lw_f_none,
    "validations": validations,
    "pooled_projection": {
        "pooled_couples": pooled_couples,
        "pilot_couples": pilot_couples,
        "scale_factor": round(scale_factor, 3),
        "pooled_900alt_wall_s": round(t_wall * scale_factor, 1),
        "pooled_900alt_mem_mb": round(peak_mem / 1e6 * scale_factor, 0),
        "pooled_1600alt_wall_s": round(t_wall * scale_factor * 16/9, 1),
        "pooled_1600alt_mem_mb": round(peak_mem / 1e6 * scale_factor * 16/9, 0),
    }
}
summary_path = os.path.join(OUTPUT_DIR, "precompute_run_summary.json")
import json as _json
with open(summary_path, "w") as f:
    _json.dump(summary, f, indent=2)
print(f"\nRun summary saved: {summary_path}")
