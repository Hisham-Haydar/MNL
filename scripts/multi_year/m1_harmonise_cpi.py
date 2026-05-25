"""
m1_harmonise_cpi.py
===================

Stage M1 — CPI/HICP deflation for multi-year pooled datasets.

Reads a stacked-raw pooled parquet produced by m1_stack_years.py, deflates
nominal income variables to base-year prices using the phi_t factor table,
and writes a harmonised parquet with *_real columns appended.

All country/year/config-specific values are read from a stage-config YAML.
Pass --stage-config config/multi_year/fr_p3a_stage_m1.yaml or use the
backward-compatible shortcut --config p3a.

Reference: docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_implementation_plan_v2.md §§7-9, 18.
           docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_generalization_report_v1.md

Deflation rule (§8):
    {var}_real = {var} * phi_t
    phi_t looked up from the CPI final CSV by year.
    Nominal columns are PRESERVED alongside real columns.

Source file (§7):
    Configured via cpi_final_path in the stage-config YAML.
    Use the template (cpi_template_path) as a starting point.

IMPORTANT — CPI source decision (§7):
    This script must NOT be run until the CPI CSV exists and has been
    authorised via the §7 decision process. Do not hard-code phi_t values;
    they must always be read from the CSV.

Usage
-----
    python scripts/multi_year/m1_harmonise_cpi.py --config p3a [--dry-run]
    python scripts/multi_year/m1_harmonise_cpi.py \\
        --stage-config config/multi_year/fr_p3a_stage_m1.yaml [--dry-run]
    python scripts/multi_year/m1_harmonise_cpi.py --config p3a \\
        --cpi-source hicp --stacked-file path/to/override.parquet
    python scripts/multi_year/m1_harmonise_cpi.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Ensure stdout/stderr can handle UTF-8 symbols on Windows cp1252 consoles.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf-8-sig"):
    import io  # noqa: F811
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure repo root is on sys.path so this script runs without PYTHONPATH set.
_SCRIPT_REPO = Path(__file__).resolve().parents[2]
if str(_SCRIPT_REPO) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_REPO))

from scripts.multi_year.m1_config import StageConfig, load_stage_config  # noqa: E402

LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Load phi_t table
# ---------------------------------------------------------------------------

def _load_phi_table(
    cfg: StageConfig,
    cpi_source: Optional[str] = None,
) -> Dict[int, float]:
    """
    Load phi_t (deflation factor) from the authorised CPI/HICP CSV.

    Returns dict mapping {year: phi_t}.
    """
    cpi_file = cfg.cpi_final_path
    if not cpi_file.exists():
        raise FileNotFoundError(
            f"CPI harmonisation file not found:\n  {cpi_file}\n\n"
            "This file must be created after the CPI source decision (§7 of the "
            "Stage M1 plan). Use the template at:\n"
            f"  {cfg.cpi_template_path}\n\n"
            "Do NOT run harmonisation until this decision is documented."
        )

    df = pd.read_csv(cpi_file, dtype=str)
    required_cols = {"year", "phi_t"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"CPI CSV is missing columns: {missing}\n"
            f"Check the template: {cfg.cpi_template_path}"
        )

    if cpi_source:
        if "price_index_source" in df.columns:
            df = df[df["price_index_source"].str.lower() == cpi_source.lower()]
            if df.empty:
                raise ValueError(
                    f"No rows for cpi_source='{cpi_source}' in {cpi_file}"
                )
        else:
            LOGGER.warning(
                "Column 'price_index_source' not found; --cpi-source filter ignored."
            )

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["phi_t"] = pd.to_numeric(df["phi_t"], errors="coerce")

    invalid = df[df["phi_t"].isna() | df["year"].isna()]
    if not invalid.empty:
        raise ValueError(
            f"{len(invalid)} rows have null year or phi_t in {cpi_file}"
        )

    phi_map: Dict[int, float] = dict(zip(df["year"].astype(int), df["phi_t"]))
    LOGGER.info("Loaded phi_t factors: %s", phi_map)
    return phi_map


# ---------------------------------------------------------------------------
# Deflation
# ---------------------------------------------------------------------------

def _deflate(
    pooled: pd.DataFrame,
    phi_map: Dict[int, float],
    cfg: StageConfig,
) -> pd.DataFrame:
    """
    Deflate monetary variables in pooled DataFrame.

    For each year_tag present in the data, look up phi_t and multiply every
    monetary variable column by phi_t, writing the result as {var}_real.
    Nominal columns are untouched.
    """
    df = pooled.copy()
    monetary_vars: List[str] = cfg.monetary_variables

    present_monetary = [v for v in monetary_vars if v in df.columns]
    absent_monetary = [v for v in monetary_vars if v not in df.columns]
    if absent_monetary:
        LOGGER.warning(
            "Monetary variables not found in parquet (skipped): %s", absent_monetary
        )

    if "year_tag" not in df.columns:
        raise KeyError(
            "Column 'year_tag' not found. Run m1_stack_years.py first."
        )

    tags_present = sorted(df["year_tag"].unique())
    for tag in tags_present:
        year = cfg.tag_year.get(int(tag))
        if year is None:
            raise ValueError(f"year_tag={tag} has no mapping to a calendar year.")
        phi = phi_map.get(year)
        if phi is None:
            raise KeyError(
                f"No phi_t found for year={year} in CPI CSV. "
                "Add this year to the CPI table."
            )
        mask = df["year_tag"] == tag
        for var in present_monetary:
            real_col = f"{var}_real"
            df.loc[mask, real_col] = pd.to_numeric(df.loc[mask, var], errors="coerce") * phi
            LOGGER.debug(
                "  year=%d  phi_t=%.6f  %s -> %s  (rows=%d)",
                year, phi, var, real_col, mask.sum()
            )

    LOGGER.info(
        "Deflation complete. Real columns added: %s",
        [f"{v}_real" for v in present_monetary]
    )
    return df


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def _dry_run_report(
    config_name: str,
    cfg: StageConfig,
    stacked_path: Path,
    out_path: Path,
    cpi_source: Optional[str],
) -> None:
    print(f"\n{'='*70}")
    print(f"DRY RUN -- config={config_name}  cpi_source={cpi_source or 'not specified'}")
    print(f"Config YAML: {cfg.yaml_path}")
    print(f"{'='*70}")

    print(f"\nInput stacked parquet: {stacked_path}")
    if stacked_path.exists():
        size_mb = stacked_path.stat().st_size / 1_048_576
        print(f"  Status: FOUND  ({size_mb:.1f} MB)")
    else:
        print("  Status: NOT FOUND  (run m1_stack_years.py first)")

    print(f"\nCPI source file:       {cfg.cpi_final_path}")
    if cfg.cpi_final_path.exists():
        print("  Status: FOUND")
        try:
            phi_map = _load_phi_table(cfg, cpi_source)
            for yr, phi in sorted(phi_map.items()):
                print(f"    year={yr}  phi_t={phi:.6f}")
        except Exception as e:
            print(f"  ERROR reading: {e}")
    else:
        print("  Status: NOT FOUND  -- §7 CPI source decision required before running")

    print(f"\nMonetary variables to deflate (§8): {cfg.monetary_variables}")
    print(f"Planned output: {out_path}")
    print("\nNo file written (dry-run mode).\n")


# ---------------------------------------------------------------------------
# Main harmonise
# ---------------------------------------------------------------------------

def harmonise(
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
    stacked_file: Optional[str] = None,
    cpi_source: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    cfg = load_stage_config(config_name, stage_config_path)

    stacked_path = Path(stacked_file) if stacked_file else cfg.stacked_raw_path()
    out_path = cfg.harmonised_path()

    if dry_run:
        _dry_run_report(config_name or cfg.config_name, cfg, stacked_path, out_path, cpi_source)
        return

    if not stacked_path.exists():
        raise FileNotFoundError(
            f"Stacked-raw parquet not found: {stacked_path}\n"
            "Run m1_stack_years.py first."
        )

    phi_map = _load_phi_table(cfg, cpi_source)

    LOGGER.info("Loading stacked-raw parquet: %s", stacked_path)
    pooled = pd.read_parquet(stacked_path)
    LOGGER.info("Loaded %d rows, %d columns.", len(pooled), len(pooled.columns))

    harmonised = _deflate(pooled, phi_map, cfg)

    cfg.pooled_output_dir.mkdir(parents=True, exist_ok=True)
    harmonised.to_parquet(out_path, index=False)
    LOGGER.info("Harmonised parquet written: %s  (%d rows)", out_path, len(harmonised))

    # Manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = cfg.results_dir / f"M1_cpi_harmonisation_check_{ts}.csv"
    cfg.results_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for tag in sorted(harmonised["year_tag"].unique()):
        year = cfg.tag_year.get(int(tag), int(tag))
        phi = phi_map.get(year, float("nan"))
        sub = harmonised[harmonised["year_tag"] == tag]
        row: dict = {
            "year": year, "year_tag": int(tag), "phi_t": phi, "n_rows": len(sub),
        }
        for var in cfg.monetary_variables:
            real_col = f"{var}_real"
            if real_col in sub.columns:
                row[f"{var}_mean_nominal"] = (
                    float(sub[var].mean()) if var in sub.columns else None
                )
                row[f"{var}_mean_real"] = float(sub[real_col].mean())
        rows.append(row)

    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    LOGGER.info("CPI check manifest written: %s", manifest_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 CPI/HICP harmonisation. Deflates nominal income variables "
            "to base-year prices using phi_t factors from the CPI CSV.\n\n"
            "IMPORTANT: The CPI source file must be created after the S7 decision.\n"
            "All country/year-specific values come from the stage-config YAML.\n"
            "Use --stage-config for an explicit path, or --config for a shortcut."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        type=str,
        help="Shortcut config name (e.g. p3a). Resolves to the canonical YAML.",
    )
    group.add_argument(
        "--stage-config",
        type=str,
        dest="stage_config",
        metavar="YAML_PATH",
        help="Explicit path to a stage-config YAML file.",
    )
    ap.add_argument(
        "--stacked-file",
        type=str,
        default=None,
        help="Override path to stacked-raw parquet (default: from stage config).",
    )
    ap.add_argument(
        "--cpi-source",
        choices=["hicp", "insee"],
        default=None,
        help="Filter CPI CSV to this source. If omitted, all rows are used.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Check inputs and print plan without writing any file.",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging.",
    )
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(message)s",
    )
    try:
        harmonise(
            config_name=args.config,
            stage_config_path=args.stage_config,
            stacked_file=args.stacked_file,
            cpi_source=args.cpi_source,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()