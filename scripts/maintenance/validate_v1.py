import sys
sys.path.insert(0, "scripts/enhanced")
from pathlib import Path
from estimation_utils import load_and_validate_mnl_data

base = Path("Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready")
df_s, df_c, meta = load_and_validate_mnl_data(
    singles_path=Path(str(base) + "__singles.parquet"),
    couples_path=Path(str(base) + "__couples.parquet"),
    metadata_path=Path(str(base) + "__mnlmeta.json"),
    strict_validation=True,
)
print("V1 PASS: singles=%d rows, couples=%d rows" % (len(df_s), len(df_c)))
print("  n_draws:", meta["n_draws"])
norm = meta["normalization"]
print("  singles c_scale=%.4f l_scale=%.4f" % (norm["singles"]["c_scale"], norm["singles"]["l_scale"]))
print("  couples c_scale=%.4f l_male_scale=%.4f" % (norm["couples"]["c_scale"], norm["couples"]["l_male_scale"]))
print("  year_2015_indicator in singles:", "year_2015_indicator" in df_s.columns)
print("  year_2017_indicator in singles:", "year_2017_indicator" in df_s.columns)
print("  year_2015_indicator in couples:", "year_2015_indicator" in df_c.columns)
print("  year_2017_indicator in couples:", "year_2017_indicator" in df_c.columns)