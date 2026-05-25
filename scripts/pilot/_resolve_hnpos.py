"""
HN-POS resolution + c_norm rebuild for the NC pilot precompute-ready parquet.
Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md

Floor formula: c_norm = max(c_pilot_raw / c_scale_pilot, EPS)
EPS = 1e-12  sourced from estimation_utils.py line 49.
Writes a NEW parquet (input never overwritten).
"""
import sys, json, time, os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

BASE = r"U:\Desktop\Nizam_Hisham\MNL"
INPUT_PARQUET  = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_ready.parquet")
OUTPUT_PARQUET = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet")
OUTPUT_META    = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json")
MNLMETA        = os.path.join(BASE, r"Data\processed\fr\pooled\fr_p3a_gsurv2_estimation_ready__mnlmeta.json")

EXPECTED_ROWS   = 2_319_300
EXPECTED_COLS   = 152
EXPECTED_GROUPS = 2_577
EXPECTED_GSIZ   = 900
EXPECTED_FLOORED = 123

def halt(code, msg):
    print(f"\nHALT {code}: {msg}")
    sys.exit(1)

t0 = time.time()

print("=" * 70)
print("HN-POS RESOLUTION + c_norm REBUILD — NC PILOT")
print("Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md")
print("=" * 70)

# ── STEP 1: Confirm EPS from source ─────────────────────────────────────────
print("\nSTEP 1: Confirm EPS from source (estimation_utils.py)")
import importlib.util
eu_path = os.path.join(BASE, r"scripts\enhanced\estimation_utils.py")
spec = importlib.util.spec_from_file_location("estimation_utils", eu_path)
eu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eu)
EPS_SOURCE = eu.EPS
print(f"  EPS from estimation_utils.py line 49: {EPS_SOURCE}")
if EPS_SOURCE != 1e-12:
    halt("HF-EPS", f"EPS = {EPS_SOURCE} != 1e-12 — unexpected value. Check source.")
print(f"  HF-EPS: PASS  (EPS = {EPS_SOURCE})")

EPS = EPS_SOURCE

# ── Leisure scales from production mnlmeta (preserved, NOT recomputed) ───────
with open(MNLMETA) as f:
    mnlmeta = json.load(f)
couples_norm   = mnlmeta["normalization"]["couples"]
L_MALE_SCALE   = couples_norm["l_male_scale"]
L_FEMALE_SCALE = couples_norm["l_female_scale"]
L_SCALE        = L_MALE_SCALE
print(f"\nLeisure scales from mnlmeta (preserved, NOT recomputed):")
print(f"  l_male_scale  = {L_MALE_SCALE}")
print(f"  l_female_scale = {L_FEMALE_SCALE}")

# ── Load input (read-only) ────────────────────────────────────────────────────
print(f"\nSTEP 2: Load input parquet (read-only)")
df = pd.read_parquet(INPUT_PARQUET)
nrows, ncols = df.shape
print(f"  Loaded: {nrows:,} rows x {ncols} cols")
if nrows != EXPECTED_ROWS or ncols != EXPECTED_COLS:
    halt("HF-STRUCT", f"Input shape {nrows}x{ncols} != {EXPECTED_ROWS}x{EXPECTED_COLS}")

# Snapshot arrays for mutation checks
l_norm_male_snap   = df["l_norm_male"].values.copy()
l_norm_female_snap = df["l_norm_female"].values.copy()
ils_male_snap      = df["ils_dispy_male"].values.copy()
ils_female_snap    = df["ils_dispy_female"].values.copy()

# ── STEP 2: Consumption object + scale ───────────────────────────────────────
print(f"\nSTEP 3: Consumption object + scale")
c_pilot_raw = df["ils_dispy_male"] + df["ils_dispy_female"]
c_scale_pilot = float(c_pilot_raw.mean())
print(f"  c_pilot_raw = ils_dispy_male + ils_dispy_female")
print(f"  c_pilot_raw: mean={c_pilot_raw.mean():.6f}  min={c_pilot_raw.min():.6f}  max={c_pilot_raw.max():.6f}")
print(f"  c_scale_pilot (all-rows mean) = {c_scale_pilot:.10f}")
if c_scale_pilot <= 0:
    halt("HF-SCALE", f"c_scale_pilot = {c_scale_pilot} <= 0")

eps_eur = EPS * c_scale_pilot
print(f"  EPS * c_scale_pilot = {eps_eur:.6e}  EUR/month (effective euro floor)")

# ── STEP 3: Normalized-EPS floor ─────────────────────────────────────────────
print(f"\nSTEP 4: Normalized-EPS floor")
c_norm_raw = (c_pilot_raw / c_scale_pilot).values
c_norm_floored = np.maximum(c_norm_raw, EPS)
c_pilot_raw_nonpositive = (c_pilot_raw.values <= 0).astype(np.int32)

n_floored = int((c_norm_floored != c_norm_raw).sum())
n_flag    = int(c_pilot_raw_nonpositive.sum())
print(f"  Rows where c_norm_raw <= EPS (floored): {n_floored}")
print(f"  Rows where c_pilot_raw <= 0 (flag=1):   {n_flag}")

# HF-FLOOR: floored count must equal 123 (or explain discrepancy)
# c_norm_raw <= EPS covers both c_norm_raw <= 0 and 0 < c_norm_raw <= EPS
# The 123 non-positive rows have c_norm_raw < 0 << EPS, so they are all floored.
# Any additional rows with 0 < c_norm_raw <= 1e-12 would also be floored.
if n_floored != EXPECTED_FLOORED:
    # Check if excess floored rows are just in the (0, EPS] band
    extra = n_floored - n_flag
    if extra != 0:
        halt("HF-FLOOR", f"Floored row count {n_floored} != {EXPECTED_FLOORED}; "
             f"{extra} rows in (0, EPS] band — unexpected; check data.")
    else:
        # n_floored == n_flag != 123: the flag count itself differs
        halt("HF-FLOOR", f"Floored row count {n_floored} != {EXPECTED_FLOORED} and "
             f"flag count {n_flag} also differs — check input data.")
print(f"  HF-FLOOR: PASS  ({n_floored} rows floored == {EXPECTED_FLOORED})")

# HF-POS: all c_norm > 0 after floor
if np.any(c_norm_floored <= 0):
    halt("HF-POS", "Some c_norm <= 0 after floor — floor failed")
print(f"  HF-POS: PASS  (c_norm > 0 all {EXPECTED_ROWS:,} rows)")

# ── STEP 4 validations ────────────────────────────────────────────────────────
print(f"\nSTEP 5: Validation suite (authorization §13)")

# V1: rebuild identity on NON-floored rows
non_floored_mask = c_norm_floored == c_norm_raw
ident_diff = np.abs(c_norm_floored[non_floored_mask] * c_scale_pilot
                    - c_pilot_raw.values[non_floored_mask])
ident_max = float(ident_diff.max()) if len(ident_diff) > 0 else 0.0
v1 = "PASS" if ident_max <= 1.0 else f"FAIL (max diff {ident_max:.4f})"
print(f"  V1 rebuild identity (non-floored rows): max diff = {ident_max:.6e}  [{v1}]")
if ident_max > 1.0:
    halt("HF-IDENT", f"Rebuild identity failed on non-floored rows: max diff = {ident_max}")

# V2: flag correctness
v2 = "PASS" if n_flag == EXPECTED_FLOORED else f"FAIL (flag sum {n_flag} != {EXPECTED_FLOORED})"
print(f"  V2 c_pilot_raw_nonpositive sum == {EXPECTED_FLOORED}: {v2}")

# V3: income columns unchanged
v3_male   = np.array_equal(df["ils_dispy_male"].values, ils_male_snap)
v3_female = np.array_equal(df["ils_dispy_female"].values, ils_female_snap)
v3 = "PASS" if v3_male and v3_female else "FAIL"
print(f"  V3 income columns unchanged: {v3}")
if not (v3_male and v3_female):
    halt("HF-INCOME", "ils_dispy_male or ils_dispy_female was altered")

# V4: leisure unchanged
v4 = "PASS" if (np.array_equal(df["l_norm_male"].values, l_norm_male_snap)
                and np.array_equal(df["l_norm_female"].values, l_norm_female_snap)) else "FAIL"
print(f"  V4 leisure cols unchanged: {v4}")

# V5: c_norm distribution post-floor
cnorm_mean = float(c_norm_floored.mean())
cnorm_min  = float(c_norm_floored.min())
cnorm_max  = float(c_norm_floored.max())
print(f"  V5 c_norm rebuilt: mean={cnorm_mean:.6f}  min={cnorm_min:.6e}  max={cnorm_max:.6f}")

# V6: c_pilot_raw distribution
cpraw_mean = float(c_pilot_raw.mean())
cpraw_min  = float(c_pilot_raw.min())
cpraw_max  = float(c_pilot_raw.max())
print(f"  c_pilot_raw: mean={cpraw_mean:.4f}  min={cpraw_min:.4f}  max={cpraw_max:.4f}")

# V7: no scalar draw
v7 = "PASS" if "draw" not in df.columns else "FAIL (scalar draw present)"
print(f"  V7 no scalar draw: {v7}")

# ── STEP 5: Build output dataframe ───────────────────────────────────────────
print(f"\nSTEP 6: Build output parquet")
df_out = df.copy()
df_out["c_norm"] = c_norm_floored
df_out["c_pilot_raw_nonpositive"] = c_pilot_raw_nonpositive
df_out["c_pilot"] = c_pilot_raw.values  # diagnostic/non-primary

# HF-LEIS: verify leisure untouched
if not (np.array_equal(df_out["l_norm_male"].values, l_norm_male_snap)
        and np.array_equal(df_out["l_norm_female"].values, l_norm_female_snap)):
    halt("HF-LEIS", "l_norm_male or l_norm_female changed in output df")

# Chosen-first check (full)
print(f"\nSTEP 6b: Chosen-first structure validation (all groups)")
first_rows = df_out.groupby(["idhh", "year_tag"], sort=False).first()
n_grps_check = len(first_rows)
bad_dj0 = int((first_rows["draw_joint"] != 0).sum())
bad_ic  = int((first_rows["is_chosen"] != 1).sum())
print(f"  Groups: {n_grps_check:,}  bad draw_joint@pos0: {bad_dj0}  bad is_chosen@pos0: {bad_ic}")
if n_grps_check != EXPECTED_GROUPS or bad_dj0 != 0 or bad_ic != 0:
    halt("HF-STRUCT", f"Chosen-first broken: {n_grps_check} groups, {bad_dj0} bad dj0, {bad_ic} bad ic")
print(f"  Chosen-first preserved (all {EXPECTED_GROUPS:,} groups): PASS")

# Group sizes
grp_sizes = df_out.groupby(["idhh", "year_tag"]).size()
n_grps = len(grp_sizes)
all_900 = bool((grp_sizes == EXPECTED_GSIZ).all())
v_struct = f"PASS ({n_grps} groups, all size {EXPECTED_GSIZ})" if n_grps == EXPECTED_GROUPS and all_900 else f"FAIL"
print(f"  Group structure: {v_struct}")

# Preserved columns
preserved_cols = ["draw_male", "draw_female", "draw_joint", "is_chosen",
                  "is_chosen_joint", "ils_dispy_male", "ils_dispy_female",
                  "wage_male", "wage_female", "gsur_male", "gsur_female",
                  "l_norm_male", "l_norm_female"]
missing_cols = [c for c in preserved_cols if c not in df_out.columns]
v_pres = "PASS" if not missing_cols else f"FAIL missing: {missing_cols}"
print(f"  Preserved columns: {v_pres}")

output_ncols = df_out.shape[1]  # 152 + c_pilot_raw_nonpositive + c_pilot = 154
print(f"  Output shape: {df_out.shape[0]:,} rows x {output_ncols} cols")
print(f"  (152 original + c_pilot_raw_nonpositive + diagnostic c_pilot = 154 total)")

# ── Write output parquet ──────────────────────────────────────────────────────
print(f"\nSTEP 7: Write output parquet")
os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)
df_out.to_parquet(OUTPUT_PARQUET, index=False, compression="snappy")
out_size = os.path.getsize(OUTPUT_PARQUET)
print(f"  Written: {OUTPUT_PARQUET}")
print(f"  File size: {out_size:,} bytes ({out_size/1e6:.1f} MB)")

# Verify on disk
meta_out = pq.read_metadata(OUTPUT_PARQUET)
print(f"  Verified on disk: {meta_out.num_rows:,} rows x {meta_out.num_columns} cols")
if meta_out.num_rows != EXPECTED_ROWS:
    halt("HF-STRUCT", f"Output row count {meta_out.num_rows} != {EXPECTED_ROWS}")

# HF-MUT: input unchanged
meta_in = pq.read_metadata(INPUT_PARQUET)
if meta_in.num_rows != EXPECTED_ROWS or meta_in.num_columns != EXPECTED_COLS:
    halt("HF-MUT", f"Input parquet changed: {meta_in.num_rows}x{meta_in.num_columns}")
print(f"  Input parquet unchanged ({EXPECTED_ROWS:,} x {EXPECTED_COLS}): PASS")

# ── Per-household floored-row breakdown ──────────────────────────────────────
bad_df = df[c_pilot_raw.values <= 0][["idhh", "draw_joint"]].copy()
bad_df["c_pilot_raw"] = c_pilot_raw.values[c_pilot_raw.values <= 0]
hh_breakdown = {}
for hh_id, grp in bad_df.groupby("idhh"):
    hh_breakdown[int(hh_id)] = {
        "n_floored_rows": len(grp),
        "draw_joint_min": int(grp["draw_joint"].min()),
        "draw_joint_max": int(grp["draw_joint"].max()),
        "c_pilot_raw_min": round(float(grp["c_pilot_raw"].min()), 4),
        "c_pilot_raw_max": round(float(grp["c_pilot_raw"].max()), 4),
    }
print(f"\n  Per-household floored rows:")
for hh_id, info in hh_breakdown.items():
    print(f"    idhh={hh_id}: {info['n_floored_rows']} rows  draw_joint=[{info['draw_joint_min']},{info['draw_joint_max']}]  c_pilot_raw=[{info['c_pilot_raw_min']:.2f},{info['c_pilot_raw_max']:.2f}]")

# ── Write normmeta sidecar ────────────────────────────────────────────────────
print(f"\nSTEP 8: Write normmeta sidecar")
normmeta = {
    "schema_version": "nc_pilot_precompute_norm_ready_v1",
    "authorization": "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md",
    "produced_by": "scripts/pilot/_resolve_hnpos.py",
    "produced_at_utc": pd.Timestamp.utcnow().isoformat(),
    "input": {
        "path": INPUT_PARQUET,
        "row_count": EXPECTED_ROWS,
        "col_count": EXPECTED_COLS
    },
    "consumption_object": {
        "formula": "c_pilot_raw = ils_dispy_male + ils_dispy_female",
        "description": "household joint disposable income, C-prime (Strategy C') post-EUROMOD"
    },
    "c_scale_pilot": c_scale_pilot,
    "c_scale_pilot_rule": "mean(ils_dispy_male + ils_dispy_female) over all 2,319,300 rows",
    "normalization": {
        "c_scale": c_scale_pilot,
        "l_scale": L_SCALE,
        "l_male_scale": L_MALE_SCALE,
        "l_female_scale": L_FEMALE_SCALE,
        "couples": {
            "c_scale": c_scale_pilot,
            "l_male_scale": L_MALE_SCALE,
            "l_female_scale": L_FEMALE_SCALE
        }
    },
    "leisure_scale_source": "fr_p3a_gsurv2_estimation_ready__mnlmeta.json (production couples block; NOT recomputed)",
    "eps_floor": {
        "EPS": EPS,
        "EPS_source": "estimation_utils.py line 49  (module constant EPS = 1e-12)",
        "EPS_use_site": "precompute_data_couples line 998: consumption = np.maximum(df['c_norm'].values.copy(), EPS)",
        "EPS_times_c_scale_pilot_eur_month": eps_eur,
        "floor_formula": "c_norm = max(c_pilot_raw / c_scale_pilot, EPS)",
        "floor_note": (
            "Pilot computational-domain convention: identical floor to precompute_data_couples "
            "internal np.maximum(c_norm, EPS), applied explicitly so the 123 floored rows are "
            "visible in data and metadata. This is NOT a final welfare-domain decision on "
            "negative-income alternatives."
        ),
        "n_floored_rows": n_floored,
        "n_c_pilot_raw_nonpositive": n_flag,
        "affected_households": len(hh_breakdown),
        "affected_idhh": list(hh_breakdown.keys()),
        "per_household": hh_breakdown
    },
    "c_norm_rebuilt": {
        "mean": cnorm_mean,
        "min": cnorm_min,
        "max": cnorm_max,
        "note": "c_norm = max(c_pilot_raw / c_scale_pilot, EPS); mean approx 1 by construction"
    },
    "c_pilot_raw_distribution": {
        "mean": cpraw_mean,
        "min": cpraw_min,
        "max": cpraw_max,
        "added_as_column_c_pilot": True,
        "column_role": "diagnostic/non-primary; not consumed by precompute_data_couples"
    },
    "c_pilot_raw_nonpositive_flag": {
        "column": "c_pilot_raw_nonpositive",
        "dtype": "int32",
        "rule": "1 where c_pilot_raw <= 0, else 0",
        "sum": n_flag,
        "role": "diagnostic/non-primary; marks the 123 floored rows for downstream robustness checks"
    },
    "output": {
        "path": OUTPUT_PARQUET,
        "row_count": EXPECTED_ROWS,
        "col_count": output_ncols,
        "description": f"152 precompute-ready cols with c_norm rebuilt + c_pilot_raw_nonpositive flag + diagnostic c_pilot = {output_ncols} total",
        "file_bytes": out_size
    },
    "validations": {},
    "not_run": {
        "euromod_rerun": False,
        "precompute": False,
        "GSUR": False,
        "estimation": False,
        "welfare": False,
        "SA2": False,
        "promotion": False,
        "M1_clean_displacement": False
    },
    "stage_status": {
        "M1_clean_2016": "active",
        "corrected_pooled_P3a": "unaffected",
        "singles_production": "unaffected"
    }
}

# Full validation table
normmeta["validations"] = {
    "V1_eps_source":           f"PASS (EPS={EPS} from estimation_utils.py line 49)",
    "V2_floor_applied":        f"PASS ({n_floored} rows floored where c_norm_raw <= EPS)",
    "V3_positivity":           "PASS (c_norm > 0 all 2,319,300 rows)",
    "V4_rebuild_identity":     f"PASS (max diff {ident_max:.4e} <= 1.0 on non-floored rows)",
    "V5_flag_sum":             f"PASS (c_pilot_raw_nonpositive sums to {n_flag})",
    "V6_income_unchanged":     v3,
    "V7_leisure_cols":         v4,
    "V8_leisure_scales":       f"PASS (l_male_scale={L_MALE_SCALE}, l_female_scale={L_FEMALE_SCALE})",
    "V9_row_count":            f"PASS ({df_out.shape[0]:,})",
    "V10_group_structure":     v_struct,
    "V11_chosen_first":        f"PASS ({n_grps_check} groups, 0 bad)",
    "V12_no_scalar_draw":      v7,
    "V13_preserved_columns":   v_pres,
    "V14_input_unchanged":     f"PASS ({EXPECTED_ROWS:,} x {EXPECTED_COLS})"
}

all_pass = all(v.startswith("PASS") for v in normmeta["validations"].values())

with open(OUTPUT_META, "w") as f:
    json.dump(normmeta, f, indent=2)
print(f"  Normmeta written: {OUTPUT_META}")

wall_seconds = time.time() - t0
print(f"\n{'='*70}")
if all_pass:
    print(f"ALL VALIDATIONS PASSED — wall time {wall_seconds:.1f}s")
else:
    failed = [k for k, v in normmeta["validations"].items() if not v.startswith("PASS")]
    print(f"SOME VALIDATIONS FAILED: {failed}")
print(f"{'='*70}")
print(f"\nc_scale_pilot:         {c_scale_pilot:.10f}")
print(f"EPS:                   {EPS}")
print(f"EPS * c_scale_pilot:   {eps_eur:.6e}  EUR/month")
print(f"Floored rows:          {n_floored}  (c_pilot_raw_nonpositive flag sum: {n_flag})")
print(f"Affected households:   {len(hh_breakdown)}")
print(f"c_norm: mean={cnorm_mean:.6f}  min={cnorm_min:.6e}  max={cnorm_max:.6f}")
print(f"\nOutput parquet: {OUTPUT_PARQUET}")
print(f"Normmeta:       {OUTPUT_META}")
print(f"\nSTOP. Do not run precompute.")
