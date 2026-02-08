"""
Generate LOC distribution plots by DEHDE level (pre-draw data).

Example:
  python scripts/Job_model/plot_loc_by_dehde.py ^
    --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" ^
    --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" ^
    --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/diagnostics/loc_by_dehde"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def _plot_loc_by_dehde(
    df: pd.DataFrame,
    dehde_col: str,
    loc_col: str,
    output_dir: Path,
    label: str,
    normalize: bool,
) -> None:
    df = df[[dehde_col, loc_col]].dropna()
    # Make sure values are clean integers for labels
    df[dehde_col] = df[dehde_col].astype(int)
    df[loc_col] = df[loc_col].astype(int)

    counts = (
        df.groupby([dehde_col, loc_col], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    # Precompute totals per dehde
    totals = counts.groupby(dehde_col)["count"].sum().rename("total")
    counts = counts.merge(totals, on=dehde_col, how="left")
    counts["value"] = counts["count"] / counts["total"] * 100.0 if normalize else counts["count"]

    for dehde_val in sorted(counts[dehde_col].unique()):
        sub = counts[counts[dehde_col] == dehde_val].copy()
        sub = sub.sort_values(loc_col)
        n_obs = int(sub["total"].iloc[0]) if not sub.empty else 0

        plt.figure(figsize=(8, 4.5))
        plt.bar(sub[loc_col].astype(str), sub["value"])
        plt.xlabel(f"{loc_col}")
        plt.ylabel("Percent (%)" if normalize else "Count")
        plt.title(f"{label}: {loc_col} distribution by {dehde_col} = {dehde_val} (n={n_obs})")
        plt.tight_layout()

        out_name = f"{label.lower()}_{loc_col}_by_{dehde_col}_{dehde_val}.png"
        plt.savefig(output_dir / out_name, dpi=150)
        plt.close()


def _filter_deciders(
    df: pd.DataFrame,
    head_col: str,
    partner_col: str,
    label: str,
) -> pd.DataFrame:
    if head_col not in df.columns or partner_col not in df.columns:
        print(
            f"[plot_loc_by_dehde] Decider columns missing for {label}; "
            f"expected '{head_col}' and '{partner_col}'. Skipping decider filter."
        )
        return df
    return df[(df[head_col] == 1) | (df[partner_col] == 1)]


def _load_df(
    path: Optional[str],
    dehde_col: str,
    loc_col: str,
    include_nondeciders: bool,
    head_col: str,
    partner_col: str,
    label: str,
) -> Optional[tuple[pd.DataFrame, str]]:
    if not path:
        return None
    base_cols = [dehde_col, loc_col]
    if not include_nondeciders:
        base_cols.extend([head_col, partner_col])
    try:
        df = pd.read_parquet(path, columns=base_cols)
        if not include_nondeciders:
            df = _filter_deciders(df, head_col, partner_col, label)
        return df, loc_col
    except Exception:
        # Fallback to loc4 if loc is not present
        fallback_col = "loc4" if loc_col != "loc4" else "loc"
        try:
            fallback_cols = [dehde_col, fallback_col]
            if not include_nondeciders:
                fallback_cols.extend([head_col, partner_col])
            df = pd.read_parquet(path, columns=fallback_cols)
        except Exception as exc:
            raise RuntimeError(
                f"Neither '{loc_col}' nor '{fallback_col}' is available in {path}."
            ) from exc
        print(f"[plot_loc_by_dehde] '{loc_col}' not found in {path}, using '{fallback_col}'.")
        if not include_nondeciders:
            df = _filter_deciders(df, head_col, partner_col, label)
        return df, fallback_col


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot LOC distribution by DEHDE level.")
    parser.add_argument("--singles-path", type=str, default=None, help="Path to singles_RURO_ready.parquet")
    parser.add_argument("--couples-path", type=str, default=None, help="Path to couples_RURO_ready.parquet")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for plots")
    parser.add_argument("--dehde-col", type=str, default="dehde", help="DEHDE column name")
    parser.add_argument("--loc-col", type=str, default="loc", help="LOC column name")
    parser.add_argument("--counts", action="store_true", help="Plot counts instead of percentages")
    parser.add_argument(
        "--include-nondeciders",
        action="store_true",
        help="Include non-deciders (default: deciders only).",
    )
    parser.add_argument("--head-col", type=str, default="hh_IsHead", help="Decider head indicator column")
    parser.add_argument("--partner-col", type=str, default="hh_IsPartner", help="Decider partner indicator column")

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    normalize = not args.counts

    singles = _load_df(
        args.singles_path,
        args.dehde_col,
        args.loc_col,
        args.include_nondeciders,
        args.head_col,
        args.partner_col,
        "singles",
    )
    couples = _load_df(
        args.couples_path,
        args.dehde_col,
        args.loc_col,
        args.include_nondeciders,
        args.head_col,
        args.partner_col,
        "couples",
    )

    if singles is None and couples is None:
        raise SystemExit("Provide at least one of --singles-path or --couples-path.")

    if singles is not None:
        singles_df, singles_loc_col = singles
        _plot_loc_by_dehde(
            singles_df, args.dehde_col, singles_loc_col, output_dir, "Singles", normalize
        )
    if couples is not None:
        couples_df, couples_loc_col = couples
        _plot_loc_by_dehde(
            couples_df, args.dehde_col, couples_loc_col, output_dir, "Couples", normalize
        )


if __name__ == "__main__":
    main()
