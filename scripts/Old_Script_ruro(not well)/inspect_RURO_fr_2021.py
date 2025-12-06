from pathlib import Path
import pandas as pd

root = Path(r"U:/EUROMOD-STORAGE/Data/processed/fr/2021")

singles = pd.read_parquet(root / "singles_RURO_ready_RURO_draws.parquet")
couples = pd.read_parquet(root / "couples_RURO_ready_RURO_draws.parquet")

COLUMNS = [
    "idhh",
    "idperson",
    "dag",
    "lhw",
    "les",
    "is_worker",
    "working",
    "working_pt1",
    "working_pt2",
    "working_ft",
    "wage_ruro",
    "pexp_years",
    "yd1",
    "yd2",
    "yd3",
    "ruro_group",
]

def show_subset(df: pd.DataFrame, title: str) -> None:
    with pd.option_context("display.max_columns", None, "display.width", None):
        print(f"=== {title} ===")
        print("Shape:", df.shape)
        sub = df[COLUMNS]
        print(sub.describe(include="all"))

show_subset(singles, "Singles RURO-ready")
print()
show_subset(couples, "Couples RURO-ready")
