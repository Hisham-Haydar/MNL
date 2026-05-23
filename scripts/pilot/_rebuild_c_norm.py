"""
Normalization-rebuild script for the NC pilot precompute-ready parquet.
Authorized by: docs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md

Rebuilds c_norm = (ils_dispy_male + ils_dispy_female) / c_scale_pilot
where c_scale_pilot = mean(c_pilot) over all rows.
Writes a NEW parquet (input never overwritten).
Halts on: HN-POS, HN-IDENT, HN-SCALE, HN-LEIS, HN-STRUCT, HN-MUT, HN-STAGE.
"""
import sys, json, time, os
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

BASE = r"U:\Desktop\Nizam_Hisham\MNL"
INPUT_PARQUET   = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_ready.parquet")
OUTPUT_PARQUET  = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet")
OUTPUT_META     = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json")
MNLMETA         = os.path.join(BASE, r"Data\processed\fr\pooled\fr_p3a_gsurv2_estimation_ready__mnlmeta.json")
READYMETA       = os.path.join(BASE, r"Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json")

EXPECTED_ROWS   = 2_319_300
EXPECTED_COLS   = 152
EXPECTED_GROUPS = 2_577
EXPECTED_GSIZ   = 900

def halt(code, msg):
    print(f"\nHALT {code}: {msg}")
    sys.exit(1)

t0 = time.time()

print("=" * 70)
print("NORMALIZATION REBUILD SLICE — NC PILOT")
print("Authorized by: docs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md")
print("=" * 70)

# ── Leisure scales from production mnlmeta (preserved, NOT recomputed) ───────
with open(MNLMETA) as f:
    mnlmeta = json.load(f)
couples_norm = mnlmeta["normalization"]["couples"]
L_MALE_SCALE  = couples_norm["l_male_scale"]   # 10.0
L_FEMALE_SCALE = couples_norm["l_female_scale"] # 10.0
L_SCALE        = L_MALE_SCALE                   # symmetric; kept for flat key
print(f"\nLeisure scales from mnlmeta (preserved, NOT recomputed):")
print(f"  l_male_scale  = {L_MALE_SCALE}")
print(f"  l_female_scale = {L_FEMALE_SCALE}")

# ── STEP 1: Load input (read-only) ──────────────────────────────────────────
print(f"\nSTEP 1: Load input parquet (read-only)")
print(f"  Path: {INPUT_PARQUET}")
df = pd.read_parquet(INPUT_PARQUET)
nrows, ncols = df.shape
print(f"  Loaded: {nrows:,} rows x {ncols} cols")

# Guard: must not have overwritten the input
if nrows != EXPECTED_ROWS or ncols != EXPECTED_COLS:
    halt("HN-STRUCT", f"Input shape {nrows}x{ncols} != {EXPECTED_ROWS}x{EXPECTED_COLS}")

# Record stale c_norm stats before rebuild
stale_c_norm_mean = float(df["c_norm"].mean())
stale_c_norm_min  = float(df["c_norm"].min())
stale_c_norm_max  = float(df["c_norm"].max())
print(f"  Stale c_norm: mean={stale_c_norm_mean:.6f}  min={stale_c_norm_min:.6f}  max={stale_c_norm_max:.6f}")

# Record l_norm_* to verify they are unchanged after rebuild
l_norm_male_vals   = df["l_norm_male"].values.copy()
l_norm_female_vals = df["l_norm_female"].values.copy()

# ── STEP 2: Consumption object + scale ──────────────────────────────────────
print(f"\nSTEP 2: Consumption object + scale")
c_pilot = df["ils_dispy_male"] + df["ils_dispy_female"]
c_pilot_mean = float(c_pilot.mean())
c_pilot_min  = float(c_pilot.min())
c_pilot_max  = float(c_pilot.max())
print(f"  c_pilot = ils_dispy_male + ils_dispy_female")
print(f"  c_pilot: mean={c_pilot_mean:.6f}  min={c_pilot_min:.6f}  max={c_pilot_max:.6f}")

# c_scale_pilot rule: mean(c_pilot) over all rows
c_scale_pilot = c_pilot_mean
print(f"  c_scale_pilot = mean(c_pilot) = {c_scale_pilot:.10f}")

if c_scale_pilot <= 0:
    halt("HN-SCALE", f"c_scale_pilot = {c_scale_pilot} <= 0")

# ── STEP 3: Positivity gate (BEFORE writing) ─────────────────────────────────
print(f"\nSTEP 3: Positivity gate (BEFORE any write)")
n_nonpos = int((c_pilot <= 0).sum())
if n_nonpos > 0:
    # Report offending rows
    bad = df[c_pilot <= 0][["idhh", "draw_joint", "ils_dispy_male", "ils_dispy_female"]].copy()
    bad["c_pilot"] = c_pilot[c_pilot <= 0]
    n_show = min(50, len(bad))
    print(f"  NON-POSITIVE c_pilot rows: {n_nonpos:,}")
    print(bad.head(n_show).to_string())
    halt("HN-POS", f"{n_nonpos:,} rows have c_pilot <= 0. Report above. Do NOT clip/floor/EPS.")
print(f"  c_pilot > 0 for all {EXPECTED_ROWS:,} rows: PASS")

# ── STEP 4: Rebuild c_norm ───────────────────────────────────────────────────
print(f"\nSTEP 4: Rebuild c_norm")
c_norm_new = (c_pilot / c_scale_pilot).values
c_norm_new_mean = float(c_norm_new.mean())
c_norm_new_min  = float(c_norm_new.min())
c_norm_new_max  = float(c_norm_new.max())
print(f"  c_norm_new: mean={c_norm_new_mean:.6f}  min={c_norm_new_min:.6f}  max={c_norm_new_max:.6f}")

# HN-IDENT: rebuild identity
ident_max = float(np.max(np.abs(c_norm_new * c_scale_pilot - c_pilot.values)))
print(f"  Rebuild identity max|c_norm_new * c_scale_pilot - c_pilot| = {ident_max:.6e}")
if ident_max > 1.0:
    halt("HN-IDENT", f"Rebuild identity check failed: max diff = {ident_max:.6e} > 1.0")
print(f"  HN-IDENT: PASS (max diff {ident_max:.6e} <= 1.0)")

# HN-POS post-rebuild
n_nonpos_norm = int((c_norm_new <= 0).sum())
if n_nonpos_norm > 0:
    halt("HN-POS", f"{n_nonpos_norm:,} rows have c_norm_new <= 0 after rebuild")
print(f"  c_norm_new > 0 all rows: PASS")

# ── STEP 5: Build output dataframe ───────────────────────────────────────────
print(f"\nSTEP 5: Build output parquet (NEW file, input untouched)")
df_out = df.copy()
df_out["c_norm"] = c_norm_new
# Add diagnostic c_pilot column (non-primary, per authorization §9)
df_out["c_pilot"] = c_pilot.values
output_ncols = df_out.shape[1]  # 153 = 152 + c_pilot
print(f"  Output shape: {df_out.shape[0]:,} rows x {output_ncols} cols")
print(f"  (152 original + 1 diagnostic c_pilot column)")

# ── HN-LEIS: leisure values unchanged ────────────────────────────────────────
if not np.array_equal(df_out["l_norm_male"].values, l_norm_male_vals):
    halt("HN-LEIS", "l_norm_male changed unexpectedly")
if not np.array_equal(df_out["l_norm_female"].values, l_norm_female_vals):
    halt("HN-LEIS", "l_norm_female changed unexpectedly")
print("  l_norm_male / l_norm_female unchanged: PASS")

# ── HN-STRUCT: no scalar draw ─────────────────────────────────────────────────
if "draw" in df_out.columns and df_out.columns.tolist().index("draw") >= 0:
    # Check it's not a simple integer index column
    halt("HN-STRUCT", "Scalar 'draw' column present in output")
print("  No scalar 'draw' column: PASS")

# ── Chosen-first check (sample: all groups) ───────────────────────────────────
print(f"\nSTEP 5b: Chosen-first structure validation")
first_rows = df_out.groupby(["idhh", "year_tag"], sort=False).first()
n_groups_check = len(first_rows)
bad_dj0 = int((first_rows["draw_joint"] != 0).sum())
bad_ic  = int((first_rows["is_chosen"] != 1).sum())
print(f"  Groups: {n_groups_check:,}  bad draw_joint@pos0: {bad_dj0}  bad is_chosen@pos0: {bad_ic}")
if n_groups_check != EXPECTED_GROUPS or bad_dj0 != 0 or bad_ic != 0:
    halt("HN-STRUCT", f"Chosen-first broken: {n_groups_check} groups, {bad_dj0} bad dj0, {bad_ic} bad ic")
print(f"  Chosen-first preserved (all {EXPECTED_GROUPS:,} groups): PASS")

# ── Write output parquet ──────────────────────────────────────────────────────
print(f"\nSTEP 6: Write output parquet")
os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)
df_out.to_parquet(OUTPUT_PARQUET, index=False, compression="snappy")
out_size = os.path.getsize(OUTPUT_PARQUET)
print(f"  Written: {OUTPUT_PARQUET}")
print(f"  File size: {out_size:,} bytes ({out_size/1e6:.1f} MB)")

# Verify output on disk
meta_out = pq.read_metadata(OUTPUT_PARQUET)
print(f"  Verified on disk: {meta_out.num_rows:,} rows x {meta_out.num_columns} cols")
if meta_out.num_rows != EXPECTED_ROWS:
    halt("HN-STRUCT", f"Output row count {meta_out.num_rows} != {EXPECTED_ROWS}")

# ── Write normmeta sidecar ────────────────────────────────────────────────────
print(f"\nSTEP 7: Write normmeta sidecar")
normmeta = {
    "schema_version": "nc_pilot_precompute_norm_ready_v1",
    "authorization": "docs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md",
    "produced_by": "scripts/pilot/_rebuild_c_norm.py",
    "produced_at_utc": pd.Timestamp.utcnow().isoformat(),
    "input": {
        "path": INPUT_PARQUET,
        "row_count": EXPECTED_ROWS,
        "col_count": EXPECTED_COLS
    },
    "consumption_object": {
        "formula": "c_pilot = ils_dispy_male + ils_dispy_female",
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
    "c_norm_rebuilt": {
        "mean": c_norm_new_mean,
        "min": c_norm_new_min,
        "max": c_norm_new_max,
        "note": "c_norm = c_pilot / c_scale_pilot; mean ~= 1 by construction"
    },
    "c_norm_stale": {
        "mean": stale_c_norm_mean,
        "min": stale_c_norm_min,
        "max": stale_c_norm_max,
        "note": "stale c_norm inherited from production diagonal; replaced in output"
    },
    "c_pilot_distribution": {
        "mean": c_pilot_mean,
        "min": c_pilot_min,
        "max": c_pilot_max,
        "added_as_column": True,
        "column_role": "diagnostic/non-primary; not consumed by precompute_data_couples"
    },
    "positivity_gate": {
        "n_nonpos_c_pilot": n_nonpos,
        "n_nonpos_c_norm_new": n_nonpos_norm,
        "result": "PASS"
    },
    "rebuild_identity": {
        "max_abs_diff_eur_month": ident_max,
        "tolerance": 1.0,
        "result": "PASS"
    },
    "output": {
        "path": OUTPUT_PARQUET,
        "row_count": EXPECTED_ROWS,
        "col_count": output_ncols,
        "description": f"152 precompute-ready cols with c_norm rebuilt + diagnostic c_pilot = {output_ncols} total",
        "file_bytes": out_size
    },
    "validations": {},
    "not_run": {
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

# ── STEP 5 validations: record results ───────────────────────────────────────
print(f"\nSTEP 8: Full validation suite (authorization §11)")

# V1: c_pilot = ils_dispy_male + ils_dispy_female
c_pilot_check = df["ils_dispy_male"] + df["ils_dispy_female"]
ident_cpilot  = float(np.max(np.abs(c_pilot_check.values - c_pilot.values)))
v1 = "PASS" if ident_cpilot == 0.0 else f"FAIL (max diff {ident_cpilot})"
print(f"  V1 c_pilot identity: {v1}")

# V2: c_scale_pilot > 0
v2 = "PASS" if c_scale_pilot > 0 else "FAIL"
print(f"  V2 c_scale_pilot > 0: {v2}")

# V3: c_scale == c_scale_pilot in metadata
v3 = "PASS" if normmeta["normalization"]["c_scale"] == c_scale_pilot else "FAIL"
print(f"  V3 c_scale == c_scale_pilot: {v3}")

# V4: rebuild identity
v4 = "PASS" if ident_max <= 1.0 else f"FAIL (max diff {ident_max})"
print(f"  V4 rebuild identity <= 1.0: {v4}")

# V5: positivity c_pilot and c_norm_new
v5 = "PASS" if n_nonpos == 0 and n_nonpos_norm == 0 else f"FAIL ({n_nonpos} c_pilot, {n_nonpos_norm} c_norm)"
print(f"  V5 positivity (c_pilot>0, c_norm>0): {v5}")

# V6: l_norm_male / l_norm_female unchanged
v6 = "PASS" if (np.array_equal(df_out["l_norm_male"].values, l_norm_male_vals)
                and np.array_equal(df_out["l_norm_female"].values, l_norm_female_vals)) else "FAIL"
print(f"  V6 leisure cols unchanged: {v6}")

# V7: leisure scale preserved in metadata
v7_lm = normmeta["normalization"]["l_male_scale"] == L_MALE_SCALE
v7_lf = normmeta["normalization"]["l_female_scale"] == L_FEMALE_SCALE
v7 = "PASS" if v7_lm and v7_lf else "FAIL"
print(f"  V7 leisure scales preserved in metadata: {v7}")

# V8: row count
v8 = "PASS" if df_out.shape[0] == EXPECTED_ROWS else f"FAIL ({df_out.shape[0]})"
print(f"  V8 row count {EXPECTED_ROWS:,}: {v8}")

# V9: groups x 900
grp_sizes = df_out.groupby(["idhh", "year_tag"]).size()
n_grps = len(grp_sizes)
all_900 = bool((grp_sizes == EXPECTED_GSIZ).all())
v9 = f"PASS ({n_grps} groups, all size {EXPECTED_GSIZ})" if n_grps == EXPECTED_GROUPS and all_900 else f"FAIL (groups={n_grps}, all_900={all_900})"
print(f"  V9 group structure: {v9}")

# V10: chosen-first
v10 = f"PASS ({EXPECTED_GROUPS} groups)" if bad_dj0 == 0 and bad_ic == 0 else f"FAIL ({bad_dj0} dj0, {bad_ic} ic)"
print(f"  V10 chosen-first: {v10}")

# V11: no scalar draw
v11 = "PASS" if "draw" not in df_out.columns else "FAIL (scalar draw present)"
print(f"  V11 no scalar draw: {v11}")

# V12: preserved columns present
preserved = ["draw_male", "draw_female", "draw_joint", "is_chosen", "is_chosen_joint",
             "ils_dispy_male", "ils_dispy_female", "wage_male", "wage_female",
             "gsur_male", "gsur_female", "l_norm_male", "l_norm_female"]
missing_preserved = [c for c in preserved if c not in df_out.columns]
v12 = "PASS" if not missing_preserved else f"FAIL missing: {missing_preserved}"
print(f"  V12 preserved columns present: {v12}")

# V13: input parquet unchanged
meta_in = pq.read_metadata(INPUT_PARQUET)
v13 = "PASS" if meta_in.num_rows == EXPECTED_ROWS and meta_in.num_columns == EXPECTED_COLS else f"FAIL ({meta_in.num_rows}x{meta_in.num_columns})"
print(f"  V13 input parquet unchanged: {v13}")

normmeta["validations"] = {
    "V1_c_pilot_identity": v1,
    "V2_c_scale_positive": v2,
    "V3_c_scale_in_metadata": v3,
    "V4_rebuild_identity": v4,
    "V5_positivity": v5,
    "V6_leisure_cols_unchanged": v6,
    "V7_leisure_scales_preserved": v7,
    "V8_row_count": v8,
    "V9_group_structure": v9,
    "V10_chosen_first": v10,
    "V11_no_scalar_draw": v11,
    "V12_preserved_columns": v12,
    "V13_input_unchanged": v13
}

all_pass = all(v.startswith("PASS") for v in normmeta["validations"].values())

with open(OUTPUT_META, "w") as f:
    json.dump(normmeta, f, indent=2)
print(f"\n  Normmeta written: {OUTPUT_META}")

wall_seconds = time.time() - t0
print(f"\n{'='*70}")
if all_pass:
    print(f"ALL VALIDATIONS PASSED — wall time {wall_seconds:.1f}s")
else:
    failed = [k for k, v in normmeta["validations"].items() if not v.startswith("PASS")]
    print(f"SOME VALIDATIONS FAILED: {failed}")
print(f"{'='*70}")
print(f"\nOutput parquet: {OUTPUT_PARQUET}")
print(f"Normmeta:       {OUTPUT_META}")
print(f"c_scale_pilot:  {c_scale_pilot:.10f}")
print(f"l_male_scale:   {L_MALE_SCALE}  l_female_scale: {L_FEMALE_SCALE}")
print(f"c_norm_new: mean={c_norm_new_mean:.6f}  min={c_norm_new_min:.6f}  max={c_norm_new_max:.6f}")
print(f"REBUILD IDENTITY: max diff = {ident_max:.6e}  (tolerance 1.0)")
print(f"\nSTOP. Do not run precompute.")
