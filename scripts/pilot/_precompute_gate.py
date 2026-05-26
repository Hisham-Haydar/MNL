"""
STEP 1: Inspection gate for precompute-readiness.
Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md
"""
import sys
import json
import tracemalloc
import time
import pickle
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

REPO = Path(__file__).resolve().parents[2]
# Data lives under the configured storage root, not the repo working tree (migrated 2026-05-26).
sys.path.insert(0, str(REPO / "scripts"))
from path_helpers import data_root  # noqa: E402
PILOT = data_root() / "pilot" / "nc_2016_couples"
PARQUET = PILOT / "fr_pilot_nc_2016_couples_product__precompute_ready.parquet"
META_JSON = PILOT / "fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json"
OUT_DIR = PILOT / "precomputed"
OUT_PKL = OUT_DIR / "fr_pilot_nc_2016_couples_precomputed.pkl"

sys.path.insert(0, str(REPO / "scripts" / "enhanced"))
from estimation_utils import precompute_data_couples, _resolve_draw_column  # noqa

# =========================================================================
# STEP 1 — INSPECTION GATE
# =========================================================================
print("\n" + "="*60)
print("STEP 1: INSPECTION GATE")
print("="*60)

schema = pq.read_schema(PARQUET)
cols = [schema.field(i).name for i in range(len(schema))]
print(f"Parquet: {pq.read_metadata(PARQUET).num_rows:,} rows x {len(cols)} cols")

HARD_REQUIRED = ["idhh", "year_tag", "draw_joint", "is_chosen",
                 "c_norm", "l_norm_male", "l_norm_female",
                 "hours_male", "hours_female", "prior"]
WAGE_COLS = ["wage_male", "wage_female", "pexp_years_male", "pexp_years_female"]
GUARDED_COLS = ["gsur_male", "gsur_female", "u_rate_male", "u_rate_female",
                "drgn1", "drgn",
                "reg_nuts1_2", "reg_nuts1_3", "reg_nuts1_4",
                "reg_nuts1_5", "reg_nuts1_6", "reg_nuts1_7", "reg_nuts1_8"]

missing_hard = [c for c in HARD_REQUIRED if c not in cols]
wage_present = [c for c in WAGE_COLS if c in cols]
wage_missing = [c for c in WAGE_COLS if c not in cols]
guarded_present = [c for c in GUARDED_COLS if c in cols]
guarded_absent = [c for c in GUARDED_COLS if c not in cols]

print("\nHARD-REQUIRED columns:")
for c in HARD_REQUIRED:
    status = "PRESENT" if c in cols else "MISSING"
    print(f"  {c}: {status}")

print("\nWAGE columns (include_wage_vars=True):")
for c in WAGE_COLS:
    status = "PRESENT" if c in cols else "MISSING"
    print(f"  {c}: {status}")

print("\nGUARDED/OPTIONAL columns:")
for c in GUARDED_COLS:
    status = "present" if c in cols else "absent"
    print(f"  {c}: {status}")

print(f"\nscalar 'draw' column present: {'draw' in cols}")

if missing_hard:
    print(f"\nHALT HP-COL: Missing hard-required columns: {missing_hard}", file=sys.stderr)
    sys.exit("HALTED: HP-COL")

if wage_missing:
    print(f"\nWARN: Wage columns missing (will zero): {wage_missing}")

print("\nHard-required check: PASS")

# =========================================================================
# NORMALIZATION: derive c_scale and l_scale from the data itself
# Read a bounded sample to compute c_scale = mean(consumption) / mean(c_norm)
# and l_scale = mean(leisure_male) / mean(l_norm_male)
# =========================================================================
print("\n" + "="*60)
print("STEP 1b: NORMALIZATION GATE")
print("="*60)

NORM_COLS = ["c_norm", "l_norm_male", "l_norm_female", "idhh", "year_tag"]
# Also need consumption/leisure_male/leisure_female if present to validate
sample_cols = NORM_COLS[:]
for extra in ["consumption", "leisure_male", "leisure_female"]:
    if extra in cols:
        sample_cols.append(extra)

df_norm = pd.read_parquet(PARQUET, columns=sample_cols)

c_norm_mean = float(df_norm["c_norm"].mean())
c_norm_min = float(df_norm["c_norm"].min())
l_norm_m_mean = float(df_norm["l_norm_male"].mean())
l_norm_f_mean = float(df_norm["l_norm_female"].mean())
l_norm_m_min = float(df_norm["l_norm_male"].min())
l_norm_f_min = float(df_norm["l_norm_female"].min())

print(f"c_norm:      mean={c_norm_mean:.6f}  min={c_norm_min:.6f}")
print(f"l_norm_male: mean={l_norm_m_mean:.6f}  min={l_norm_m_min:.6f}")
print(f"l_norm_fem:  mean={l_norm_f_mean:.6f}  min={l_norm_f_min:.6f}")

# The normalization convention is c_norm = consumption / c_scale  =>  c_scale = consumption / c_norm
# If consumption column is absent (it was dropped at Stage 4 for income cols),
# derive c_scale from metadata or from the ratio on a sample.
# Check production couples metadata for the scale used.
PROD_META_PATH = data_root() / "processed" / "fr" / "pooled" / "fr_p3a_gsurv2_estimation_ready__mnlmeta.json"
alt_meta_path  = data_root() / "processed" / "fr" / "pooled" / "fr_p3a_gsurv2_estimation_ready__couples__mnlmeta.json"

norm_source = None
c_scale = None
l_scale = None

for mp in [PROD_META_PATH, alt_meta_path]:
    if mp.exists():
        with mp.open(encoding="utf-8") as f:
            prod_meta = json.load(f)
        norm_block = prod_meta.get("normalization", {})
        if "couples" in norm_block:
            c_scale = norm_block["couples"].get("c_scale")
            l_scale = norm_block["couples"].get("l_male_scale") or norm_block["couples"].get("l_scale")
        else:
            c_scale = norm_block.get("c_scale")
            l_scale = norm_block.get("l_scale")
        if c_scale is not None and l_scale is not None:
            norm_source = str(mp.name)
            break

if c_scale is None or l_scale is None:
    # Fallback: derive from the data's consumption/c_norm ratio (if consumption present)
    if "consumption" in df_norm.columns:
        ratio = (df_norm["consumption"] / df_norm["c_norm"]).dropna()
        ratio_std = float(ratio.std())
        c_scale_derived = float(ratio.mean())
        print(f"Derived c_scale from consumption/c_norm ratio: {c_scale_derived:.4f}  std={ratio_std:.6f}")
        if ratio_std > 1.0:
            print("HALT HP-NORM: c_scale derived from data has high variance — normalization inconsistent", file=sys.stderr)
            sys.exit("HALTED: HP-NORM")
        c_scale = c_scale_derived
        norm_source = "derived from data (consumption/c_norm)"
    if "leisure_male" in df_norm.columns:
        ratio_l = (df_norm["leisure_male"] / df_norm["l_norm_male"]).dropna()
        l_scale_derived = float(ratio_l.mean())
        l_scale = l_scale_derived
        norm_source = (norm_source or "") + " + leisure derived"

if c_scale is None or l_scale is None:
    # Last resort: if c_norm is already normalized to mean~1, use c_scale=1
    # Check if c_norm ~= 1.0 (already unit-normalized)
    if 0.8 < c_norm_mean < 1.2:
        # c_norm appears to be pre-divided; use mean of the actual c_norm array
        # to infer c_scale = mean(consumption_raw) if available
        # Cannot proceed without knowing the actual scale — HALT
        pass
    print("HALT HP-NORM: normalization metadata not found in production meta files and cannot be derived from data", file=sys.stderr)
    sys.exit("HALTED: HP-NORM")

print(f"\nNormalization source: {norm_source}")
print(f"  c_scale = {c_scale:.4f}")
print(f"  l_scale = {l_scale:.4f}")

# Build the metadata dict precompute_data_couples expects
metadata = {
    "normalization": {
        "c_scale": c_scale,
        "l_scale": l_scale,
    },
    "n_draws": 900,
}

# Validate consistency: c_norm * c_scale should approximate consumption
# If consumption column is present; otherwise check c_norm > 0 and finite
if "consumption" in df_norm.columns:
    c_reconstructed = df_norm["c_norm"] * c_scale
    max_diff = float((c_reconstructed - df_norm["consumption"]).abs().max())
    print(f"Normalization consistency: max |c_norm*c_scale - consumption| = {max_diff:.4e}")
    if max_diff > 1.0:  # EUR/month tolerance
        print(f"HALT HP-NORM: normalization inconsistency {max_diff:.4e} > 1.0", file=sys.stderr)
        sys.exit("HALTED: HP-NORM")
    print("Normalization consistency: PASS")
else:
    # No consumption column — validate c_norm is positive and finite
    n_bad = int((df_norm["c_norm"] <= 0).sum() + df_norm["c_norm"].isna().sum())
    print(f"c_norm positive+finite check (no consumption col): {n_bad} bad rows")
    if n_bad > 0:
        print(f"HALT HP-NORM: {n_bad} non-positive/NaN c_norm values", file=sys.stderr)
        sys.exit("HALTED: HP-NORM")
    print("c_norm positive+finite: PASS (no raw consumption col to cross-check)")

print("\nNormalization gate: PASS")
print(f"\nGuarded fallbacks WILL fire:")
print(f"  GSUR (gsur_male/gsur_female): {'present - will use' if 'gsur_male' in cols else 'ABSENT -> zeros + warning'}")
print(f"  Region (reg_nuts1_2..8):      {'present' if 'reg_nuts1_2' in cols else 'ABSENT'}")
print(f"  Region (drgn1):               {'present' if 'drgn1' in cols else 'ABSENT'}")

# =========================================================================
# STEP 2 — RUN PRECOMPUTE
# =========================================================================
print("\n" + "="*60)
print("STEP 2: RUN precompute_data_couples")
print("="*60)

df = pd.read_parquet(PARQUET)
print(f"Loaded: {len(df):,} rows x {len(df.columns)} cols")

# Confirm no scalar draw in the loaded dataframe
if "draw" in df.columns:
    print("HALT HP-DRAW: scalar draw found in loaded parquet", file=sys.stderr)
    sys.exit("HALTED: HP-DRAW")

# Test resolve before calling
resolved = _resolve_draw_column(df)
print(f"_resolve_draw_column returned: '{resolved.name}'")
assert resolved.name == "draw_joint", f"Expected draw_joint, got {resolved.name}"
print("Draw resolution: draw_joint (PASS)")

# Run with tracemalloc for peak memory
tracemalloc.start()
t0 = time.perf_counter()

result = precompute_data_couples(
    df,
    metadata,
    include_wage_vars=True,
    include_loc_vars=False,
    include_extra_vars=None,
)

t_elapsed = time.perf_counter() - t0
_, peak_bytes = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"\nWall time:  {t_elapsed:.2f} s")
print(f"Peak memory (tracemalloc): {peak_bytes / 1e6:.1f} MB")

# =========================================================================
# STEP 3 — PERSIST
# =========================================================================
print("\n" + "="*60)
print("STEP 3: PERSIST")
print("="*60)

OUT_DIR.mkdir(parents=True, exist_ok=True)
with OUT_PKL.open("wb") as f:
    pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
pkl_bytes = OUT_PKL.stat().st_size
print(f"Saved: {OUT_PKL}")
print(f"Size:  {pkl_bytes:,} bytes ({pkl_bytes/1e6:.1f} MB)")

# =========================================================================
# STEP 4 — VALIDATE
# =========================================================================
print("\n" + "="*60)
print("STEP 4: VALIDATE")
print("="*60)

n_obs = result.n_obs
n_groups = result.n_groups

print(f"n_obs:    {n_obs:,}  (expected 2,319,300)")
print(f"n_groups: {n_groups:,}  (expected 2,577)")

assert n_obs == 2_319_300, f"n_obs {n_obs} != 2,319,300"
assert n_groups == 2_577, f"n_groups {n_groups} != 2,577"

# Group sizes
group_sizes = result.group_ends - result.group_starts
assert np.all(group_sizes == 900), f"Not all groups 900: {np.unique(group_sizes)}"
print(f"All groups size 900: PASS")

# Array lengths
for name, arr in [("consumption", result.consumption),
                  ("log_c", result.log_c),
                  ("leisure_male", result.leisure_male),
                  ("log_l_male", result.log_l_male),
                  ("leisure_female", result.leisure_female),
                  ("log_l_female", result.log_l_female),
                  ("prior", result.prior)]:
    assert len(arr) == 2_319_300, f"{name} length {len(arr)} != 2,319,300"
print(f"All core arrays length 2,319,300: PASS")

# Finiteness checks
for name, arr in [("log_c", result.log_c),
                  ("log_l_male", result.log_l_male),
                  ("log_l_female", result.log_l_female),
                  ("prior", result.prior)]:
    assert np.all(np.isfinite(arr)), f"{name} has non-finite values"
print("Finiteness (log_c, log_l_male, log_l_female, prior): PASS")

# Prior > 0 (EPS-floored)
from estimation_utils import EPS
assert np.all(result.prior >= EPS), f"prior below EPS: min={result.prior.min()}"
print(f"prior >= EPS ({EPS}): PASS")

# Wage layer
assert result.log_wage_male is not None, "log_wage_male is None (wage layer zeroed)"
assert result.log_wage_female is not None, "log_wage_female is None (wage layer zeroed)"
assert len(result.log_wage_male) == 2_319_300
assert len(result.log_wage_female) == 2_319_300
print(f"Wage layer populated (log_wage_male/female non-None, length 2,319,300): PASS")

# No scalar draw in the output artifact
import dataclasses
field_names = [f.name for f in dataclasses.fields(result)]
assert "draw" not in field_names, f"draw field appeared in PrecomputedDataCouples"
print("No scalar draw in precomputed artifact: PASS")

# Parquet unchanged
meta_after = pq.read_metadata(PARQUET)
assert meta_after.num_rows == 2_319_300 and meta_after.num_columns == 152
print(f"Precompute-ready parquet unchanged (2,319,300 x 152): PASS")

# chosen_row check: actual_choice sums to 1 per group
chosen_sums = np.array([result.actual_choice[s:e].sum()
                        for s, e in zip(result.group_starts, result.group_ends)])
assert np.allclose(chosen_sums, 1.0), f"Not exactly 1 chosen per group: {chosen_sums[:5]}"
print("Exactly 1 chosen per group (2,577 total): PASS")

# Projection
projection_factor = 7438 / 2577
projected_wall = t_elapsed * projection_factor
projected_peak_mb = (peak_bytes / 1e6) * projection_factor

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"n_obs:              {n_obs:,}")
print(f"n_groups:           {n_groups:,}")
print(f"group_size:         900")
print(f"Wall time:          {t_elapsed:.2f} s")
print(f"Peak memory:        {peak_bytes/1e6:.1f} MB")
print(f"Output pkl:         {OUT_PKL}  ({pkl_bytes/1e6:.1f} MB)")
print(f"Guarded (GSUR):     {'present' if 'gsur_male' in cols else 'absent -> zeros'}")
print(f"Guarded (region):   {'reg_nuts1_* present' if 'reg_nuts1_2' in cols else 'absent'} / {'drgn1 present' if 'drgn1' in cols else 'absent'}")
print(f"Wage layer:         populated (log_wage_male/female non-None)")
print(f"Norm source:        {norm_source}")
print(f"c_scale:            {c_scale:.4f}")
print(f"l_scale:            {l_scale:.4f}")
print(f"\nPooled-cycle projection (7,438/2,577 = {projection_factor:.2f}x):")
print(f"  Projected wall:    {projected_wall:.0f} s  ({projected_wall/60:.1f} min)")
print(f"  Projected peak:    {projected_peak_mb:.0f} MB")
print("\nALL VALIDATION CHECKS PASSED")
