from pathlib import Path
import pandas as pd

root = Path(r"U:/EUROMOD-STORAGE/Data/processed/fr/2021")

singles = pd.read_parquet(root / "singles_RURO_ready.parquet")
couples = pd.read_parquet(root / "couples_RURO_ready.parquet")

print("=== Singles RURO-ready ===")
print(singles.shape)
print(singles[["idhh", "idperson", "dag", "lhw", "les",
               "is_worker", "working", "working_pt1", "working_pt2", "working_ft",
               "wage_ruro", "pexp_years", "yd1", "yd2", "yd3",
               "ruro_group"]].describe(include="all"))

print("\n=== Couples RURO-ready ===")
print(couples.shape)
print(couples[["idhh", "idperson", "dag", "lhw", "les",
               "is_worker", "working", "working_pt1", "working_pt2", "working_ft",
               "wage_ruro", "pexp_years", "yd1", "yd2", "yd3",
               "ruro_group"]].describe(include="all"))
