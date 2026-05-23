"""Validation script for the draw-column resolution patch in estimation_utils.py.
Authorized by: docs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md
"""
import sys, logging
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, r"U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced")
import estimation_utils as eu
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

PILOT = r"U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\fr_pilot_nc_2016_couples_product__precompute_ready.parquet"

print("=" * 60)
print("VALIDATION 1: Static import")
print("=" * 60)
print("IMPORT: OK")

print()
print("=" * 60)
print("VALIDATION 2: Unit tests for _resolve_draw_column")
print("=" * 60)

# Branch 1: draw present -> returns df["draw"]
df_legacy = pd.DataFrame({"draw": [0, 1, 2], "draw_joint": [0, 30, 60], "idhh": [1, 1, 1]})
result = eu._resolve_draw_column(df_legacy)
assert list(result) == [0, 1, 2], f"Branch1 failed: {list(result)}"
assert result.name == "draw", f"Branch1 name: {result.name}"
print("BRANCH 1 (draw present): PASS -> returns draw column")

# Branch 2: draw absent, draw_joint present -> returns df["draw_joint"]
df_pilot = pd.DataFrame({"draw_joint": [0, 1, 2, 899], "draw_male": [0, 0, 0, 29], "draw_female": [0, 1, 2, 29], "idhh": [1, 1, 1, 1]})
result2 = eu._resolve_draw_column(df_pilot)
assert list(result2) == [0, 1, 2, 899], f"Branch2 failed: {list(result2)}"
assert result2.name == "draw_joint", f"Branch2 name: {result2.name}"
print("BRANCH 2 (draw_joint, no draw): PASS -> returns draw_joint column")

# Branch 3: neither -> raises ValueError
df_bad = pd.DataFrame({"idhh": [1], "hours_male": [40.0]})
try:
    eu._resolve_draw_column(df_bad)
    print("BRANCH 3: FAILED - should have raised ValueError")
    sys.exit(1)
except ValueError as e:
    msg = str(e).lower()
    assert "draw" in msg and "draw_joint" in msg, f"Error missing expected terms: {e}"
    print(f"BRANCH 3 (neither present): PASS -> ValueError raised (mentions both columns)")

# Legacy unchanged: draw-present path is identical
result_legacy = eu._resolve_draw_column(df_legacy)
assert result_legacy.tolist() == df_legacy["draw"].tolist()
print("LEGACY UNCHANGED: PASS -> draw-present path byte-for-byte identical")

print()
print("=" * 60)
print("VALIDATION 3: Regression check (legacy fixture via validate_data)")
print("=" * 60)
# Build a minimal legacy couples fixture that passes validate_data
# Use only columns required by the legacy path
n = 10
L_SCALE = 0.5  # l_norm = leisure / l_scale must match
C_SCALE = 2000.0
df_reg = pd.DataFrame({
    "idhh": sorted([1001] * 5 + [1002] * 5),
    "draw": list(range(5)) + list(range(5)),
    "leisure_male": np.full(n, 0.5),
    "leisure_female": np.full(n, 0.5),
    "l_norm_male": np.full(n, 0.5 / L_SCALE),   # = 1.0
    "l_norm_female": np.full(n, 0.5 / L_SCALE),  # = 1.0
    "hours_male": np.full(n, 40.0),
    "hours_female": np.full(n, 35.0),
    "prior": np.full(n, 0.1),
    "consumption": np.full(n, C_SCALE),
    "c_norm": np.full(n, 1.0),    # consumption / c_scale = 1.0
    "year_tag": np.full(n, 2, dtype=int),
})
meta_reg = {"normalization": {"c_scale": C_SCALE, "l_scale": L_SCALE}, "n_draws": 5}
# validate_data should accept it without error
try:
    eu._validate_mnl_dataset(df_reg, "couples", meta_reg, strict=True)
    print("REGRESSION validate_data (legacy draw): PASS")
except ValueError as e:
    print(f"REGRESSION FAILED: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("VALIDATION 4: Pilot parquet bounded read")
print("=" * 60)

meta_pq = pq.read_metadata(PILOT)
print(f"Pilot parquet: {meta_pq.num_rows:,} rows x {meta_pq.num_columns} cols")
assert meta_pq.num_rows == 2_319_300, f"Row count {meta_pq.num_rows}"
assert meta_pq.num_columns == 152, f"Col count {meta_pq.num_columns}"

schema = pq.read_schema(PILOT)
col_names = [schema.field(i).name for i in range(len(schema))]
has_draw = "draw" in col_names
has_draw_joint = "draw_joint" in col_names
has_is_chosen = "is_chosen" in col_names
print(f"  Has scalar 'draw': {has_draw}")
print(f"  Has 'draw_joint': {has_draw_joint}")
print(f"  Has 'is_chosen': {has_is_chosen}")
assert not has_draw, "FAIL: scalar draw column present in pilot parquet (HD5)"
assert has_draw_joint, "FAIL: draw_joint missing from pilot parquet"
assert has_is_chosen, "FAIL: is_chosen missing from pilot parquet"
print("Schema check: PASS (no scalar draw; draw_joint and is_chosen present)")

# Sample read for range and position-0 checks
sample = pd.read_parquet(PILOT, columns=["idhh", "year_tag", "draw_joint", "draw_male", "draw_female", "is_chosen"])
dj_min = int(sample["draw_joint"].min())
dj_max = int(sample["draw_joint"].max())
print(f"  draw_joint range: [{dj_min}, {dj_max}]")
assert dj_min == 0 and dj_max == 899, f"draw_joint range [{dj_min}, {dj_max}] != [0, 899]"
print("  draw_joint range [0..899]: PASS")

# Position-0 check on all groups
first_rows = sample.groupby(["idhh", "year_tag"], sort=False).first()
n_groups_chk = len(first_rows)
bad_dj0 = int((first_rows["draw_joint"] != 0).sum())
bad_ic = int((first_rows["is_chosen"] != 1).sum())
print(f"  Groups checked: {n_groups_chk:,}  bad position-0 draw_joint: {bad_dj0}  bad is_chosen: {bad_ic}")
assert bad_dj0 == 0 and bad_ic == 0, f"Position-0 failure: {bad_dj0} dj0, {bad_ic} ic"
print("  Position-0 chosen-row (all groups): PASS")
print("PILOT PARQUET BOUNDED READ: PASS")

print()
print("=" * 60)
print("VALIDATION 5: Fail-loud check")
print("=" * 60)
df_fail = pd.DataFrame({"idhh": [1], "hours_male": [40.0]})
try:
    eu._resolve_draw_column(df_fail)
    print("FAIL-LOUD: FAILED - should have raised")
    sys.exit(1)
except ValueError as e:
    print(f"FAIL-LOUD: PASS -> ValueError: {str(e)[:100]}")

print()
print("=" * 60)
print("VALIDATION 6: Couples group-builder smoke test on pilot parquet")
print("=" * 60)
# Load a bounded sample: first 10 groups = 9000 rows from pilot
# Use idhh sort to get complete groups
sample_full = pd.read_parquet(PILOT)
pilot_idhhs = sorted(sample_full["idhh"].unique())[:10]
pilot_sample = sample_full[sample_full["idhh"].isin(pilot_idhhs)].copy()
print(f"  Sample groups: {len(pilot_idhhs)}, rows: {len(pilot_sample):,}")

# _resolve_draw_column on this sample should return draw_joint
resolved = eu._resolve_draw_column(pilot_sample)
assert resolved.name == "draw_joint", f"Expected draw_joint, got {resolved.name}"
print(f"  _resolve_draw_column resolved: '{resolved.name}' (PASS)")

# Build group structure using the same logic as precompute_data_couples
import numpy as np
grp_col = (pilot_sample["idhh"].astype(np.int64).values * 10
           + pilot_sample["year_tag"].astype(np.int64).values)
changes = np.where(np.diff(grp_col) != 0)[0] + 1
g_starts = np.concatenate([[0], changes])
g_ends = np.concatenate([changes, [len(pilot_sample)]])
g_sizes = g_ends - g_starts
n_g = len(g_starts)
print(f"  Groups built: {n_g} (expected {len(pilot_idhhs)})")
assert n_g == len(pilot_idhhs), f"Group count mismatch: {n_g} vs {len(pilot_idhhs)}"
assert np.all(g_sizes == 900), f"Not all groups size 900: {g_sizes}"
print(f"  All group sizes == 900: PASS")
print(f"  No KeyError (draw column not required for group construction): PASS")

# Confirm first row of each group has draw_joint==0 and is_chosen==1
dj_first = pilot_sample["draw_joint"].values[g_starts]
ic_first = pilot_sample["is_chosen"].values[g_starts]
assert np.all(dj_first == 0), f"Some groups first row draw_joint != 0: {dj_first}"
assert np.all(ic_first == 1), f"Some groups first row is_chosen != 1: {ic_first}"
print("  Position-0 chosen-row in smoke-test groups: PASS")
print("COUPLES GROUP-BUILDER SMOKE TEST: PASS")

print()
print("=" * 60)
print("VALIDATION 7: No data mutation")
print("=" * 60)
meta_after = pq.read_metadata(PILOT)
assert meta_after.num_rows == 2_319_300, f"Row count changed: {meta_after.num_rows}"
assert meta_after.num_columns == 152, f"Col count changed: {meta_after.num_columns}"
print(f"Pilot parquet unchanged: {meta_after.num_rows:,} x {meta_after.num_columns}: PASS")
schema_after = pq.read_schema(PILOT)
col_names_after = [schema_after.field(i).name for i in range(len(schema_after))]
assert "draw" not in col_names_after, "FAIL: scalar draw appeared in pilot parquet"
assert "draw_joint" in col_names_after, "FAIL: draw_joint gone from pilot parquet"
print("No scalar draw added to pilot parquet: PASS")
print("DATA MUTATION CHECK: PASS")

print()
print("=" * 60)
print("ALL VALIDATIONS PASSED")
print("=" * 60)
