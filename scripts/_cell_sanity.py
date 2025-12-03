import pandas as pd
from pathlib import Path

# Point this to the MNL dataset produced by RURO_prep_mnl_basic.py
DATA_PATH = Path(r"U:\EUROMOD-STORAGE\Data\processed\fr\2021\fr_2021_RURO_mnl.parquet")


def _read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format for {path}")


def main() -> None:
    df = _read_any(DATA_PATH)
    print(f"Loaded {DATA_PATH} with shape {df.shape}")
    print("\nColumns:")
    print(sorted(df.columns))

    # Columns starting with 'd'
    d_cols = [c for c in df.columns if c.lower().startswith("d")]
    print("\nColumns starting with 'd':")
    print(sorted(d_cols))

    # Basic head
    print("\nHead:")
    print(df.head())

    # Duplicate check
    dup = df.duplicated(subset=["idperson", "draw"]).sum()
    print(f"\nDuplicate (idperson, draw) rows: {dup}")

    # Grouped counts
    by_id = df.groupby("idperson").agg(
        n_alts=("draw", "size"),
        chosen_sum=("is_chosen", "sum"),
        draw_min=("draw", "min"),
        draw_max=("draw", "max"),
    )
    print("\nBy-person draw summary (n_alts, chosen_sum, draw_min, draw_max):")
    print(by_id.describe())

    # Core variable summaries
    for col in ["consumption", "hours", "leisure"]:
        if col in df.columns:
            stats = df[col].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99])
            print(f"\n{col} summary:")
            print(stats)
            neg = (df[col] <= 0).sum()
            print(f"{col} <= 0 count: {neg}")

    # Missing check on core fields
    core = ["idperson", "draw", "is_chosen", "consumption", "hours", "leisure"]
    missing = df[core].isna().sum()
    print("\nMissing counts (core fields):")
    print(missing)


if __name__ == "__main__":
    main()
