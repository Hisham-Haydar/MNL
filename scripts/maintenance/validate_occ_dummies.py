"""Check that occupation dummies are correctly set on couples precomputed data."""
import sys
sys.path.insert(0, "scripts/enhanced")
import pandas as pd
import numpy as np
from pathlib import Path
from estimation_spec_parser import parse_specification
from estimation_utils import load_and_validate_mnl_data, precompute_data_couples

SPEC = Path("scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml")
BASE = Path("Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready")

spec = parse_specification(SPEC)
extra_vars = []
for s in getattr(spec, "market_opportunity_shifters", []):
    var = s.get("variable", "")
    if var and var not in extra_vars:
        extra_vars.append(var)

print("extra_vars:", extra_vars)

df_s, df_c, meta = load_and_validate_mnl_data(
    singles_path=Path(str(BASE) + "__singles.parquet"),
    couples_path=Path(str(BASE) + "__couples.parquet"),
    metadata_path=Path(str(BASE) + "__mnlmeta.json"),
    strict_validation=True,
)
df_c_sub = df_c.head(20000).copy()

data_cou = precompute_data_couples(
    df=df_c_sub, metadata=meta,
    include_wage_vars=True, include_loc_vars=False,
    include_extra_vars=extra_vars,
)

# Check each occupation dummy attribute
for var in ["loc4_2", "loc4_3", "loc4_4"]:
    for suffix in ["", "_male", "_female"]:
        attr = var + suffix
        arr = getattr(data_cou, attr, None)
        status = "SET  n_nonzero=%d" % int(np.count_nonzero(arr)) if arr is not None else "NONE"
        print(f"  data_cou.{attr}: {status}")

for var in ["year_2015_indicator", "year_2017_indicator"]:
    arr_hh = getattr(data_cou, var, None)
    arr_m  = getattr(data_cou, var + "_male", None)
    arr_f  = getattr(data_cou, var + "_female", None)
    print(f"  {var}: household={arr_hh is not None}, _male={arr_m is not None}, _female={arr_f is not None}")
    if arr_hh is not None:
        print(f"    n_ones={int((arr_hh==1).sum())}/{len(arr_hh)}")