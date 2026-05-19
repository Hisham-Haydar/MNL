"""
m1_harmonise_cpi.py
===================

Stage M1 — CPI/HICP deflation for the RURO multi-year pooled dataset.

Reads a stacked-raw pooled parquet produced by m1_stack_years.py, deflates
nominal income variables to 2016 prices using the φ_t factor table, writes
a harmonised parquet with *_real columns appended.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §§7–9, 18.

Deflation rule (§8):
    {var}_real = {var} × φ_t
    φ_t looked up from cpi_hicp_fr_harmonisation.csv by year.
    Nominal columns are PRESERVED alongside real columns.

Source file (§7):
    Data/external/cpi_hicp_fr_harmonisation.csv  (must be created after the
    CPI source decision — see §7 of the plan).  Use the TEMPLATE at
    Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv as a starting point.

IMPORTANT — CPI source decision (§7):
    This script must NOT be run until cpi_hicp_fr_harmonisation.csv exists
    and has been authorised via the §7 decision process. Do not hard-code
    φ_t values; they must always be read from the CSV.

Usage
-----
    python scripts/multi_year/m1_harmonise_cpi.py --config p3a [--dry-run]
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

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]
POOLED_DIR = REPO / "Data" / "processed" / "fr" / "pooled"
EXTERNAL_DIR = REPO / "Data" / "external"
RESULTS_DIR = REPO / "Results"

CPI_SOURCE_FILE = EXTERNAL_DIR / "cpi_hicp_fr_harmonisation.csv"
CPI_TEMPLATE_FILE = EXTERNAL_DIR / "cpi_hicp_fr_harmonisation_TEMPLATE.csv"

# Monetary variables to deflate (§8).  Only columns present in the parquet
# are deflated; absent columns are silently skipped with a log message.
MONETARY_VARS: List[str] = [
    "ils_dispy",
    "ils_earns",
    "yem",
    "yse",
    "ypen",
    "ypt",
    "ils_ben",
]

# Variables explicitly excluded from deflation (§9)
EXCLUDED_VARS = frozenset([
    "dgn", "dag", "dms", "deh", "drgn1",
    "idhh", "idperson", "idorighh", "idorigperson",
    "dwt",
    "gsur", "gsur_v2",
    "year_tag", "year",
    "tpr",
    "stacked_hh_uid", "stacked_person_uid", "cluster_id",
])

YEAR_TAG: Dict[int, int] = {2015: 1, 2016: 2, 2017: 3, 2018: 4}
TAG_YEAR: Dict[int, int] = {v: k for k, v in YEAR_TAG.items()}


# ---------------------------------------------------------------------------
# Load φ_t table
# ---------------------------------------------------------------------------

def _load_phi_table(cpi_source: Optional[str] = None) -> Dict[int, float]:
    """
    Load φ_t (deflation factor) from the authorised CPI/HICP harmonisation CSV.

    Returns dict mapping {year: phi_t}.

    If cpi_source is provided ('hicp' or 'insee'), the CSV is filtered to that
    source; otherwise all rows are used (they should already be source-filtered
    in the CSV after the §7 decision).
    """
    if not CPI_SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"CPI harmonisation file not found:\n  {CPI_SOURCE_FILE}\n\n"
            "This file must be created after the CPI source decision (§7 of the "
            "Stage M1 plan). Use the template at:\n"
            f"  {CPI_TEMPLATE_FILE}\n\n"
            "Do NOT run harmonisation until this decision is documented."
        )

    df = pd.read_csv(CPI_SOURCE_FILE, dtype=str)
    required_cols = {"year", "phi_t"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"cpi_hicp_fr_harmonisation.csv is missing columns: {missing}\n"
            f"Check the template: {CPI_TEMPLATE_FILE}"
        )

    if cpi_source:
        if "price_index_source" in df.columns:
            df = df[df["price_index_source"].str.lower() == cpi_source.lower()]
            if df.empty:
                raise ValueError(
                    f"No rows for cpi_source='{cpi_source}' in {CPI_SOURCE_FILE}"
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
            f"{len(invalid)} rows have null year or phi_t in {CPI_SOURCE_FILE}"
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
) -> pd.DataFrame:
    """
    Deflate monetary variables in pooled DataFrame.

    For each year_tag present in the data, look up φ_t and multiply every
    MONETARY_VARS column by φ_t, writing the result as {var}_real.
    Nominal columns are untouched.
    """
    df = pooled.copy()

    present_monetary = [v for v in MONETARY_VARS if v in df.columns]
    absent_monetary = [v for v in MONETARY_VARS if v not in df.columns]
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
        year = TAG_YEAR.get(int(tag))
        if year is None:
            raise ValueError(f"year_tag={tag} has no mapping to a calendar year.")
        phi = phi_map.get(year)
        if phi is None:
            raise KeyError(
                f"No phi_t found for year={year} in cpi_hicp_fr_harmonisation.csv. "
                "Add this year to the CPI table."
            )
        mask = df["year_tag"] == tag
        for var in present_monetary:
            real_col = f"{var}_real"
            df.loc[mask, real_col] = df.loc[mask, var].astype(float) * phi
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
    config: str,
    stacked_path: Path,
    out_path: Path,
    cpi_source: Optional[str],
) -> None:
    print(f"\n{'='*70}")
    print(f"DRY RUN — config={config}  cpi_source={cpi_source or 'not specified'}")
    print(f"{'='*70}")

    print(f"\nInput stacked parquet: {stacked_path}")
    if stacked_path.exists():
        size_mb = stacked_path.stat().st_size / 1_048_576
        print(f"  Status: FOUND  ({size_mb:.1f} MB)")
    else:
        print("  Status: NOT FOUND  (run m1_stack_years.py first)")

    print(f"\nCPI source file:       {CPI_SOURCE_FILE}")
    if CPI_SOURCE_FILE.exists():
        print("  Status: FOUND")
        try:
            phi_map = _load_phi_table(cpi_source)
            for yr, phi in sorted(phi_map.items()):
                print(f"    year={yr}  phi_t={phi:.6f}")
        except Exception as e:
            print(f"  ERROR reading: {e}")
    else:
        print("  Status: NOT FOUND  — §7 CPI source decision required before running")

    print(f"\nMonetary variables to deflate (§8): {MONETARY_VARS}")
    print(f"Planned output: {out_path}")
    print("\nNo file written (dry-run mode).\n")


# ---------------------------------------------------------------------------
# Main harmonise
# ---------------------------------------------------------------------------

def harmonise(
    config: str,
    stacked_file: Optional[str] = None,
    cpi_source: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    config = config.lower()

    stacked_path = Path(stacked_file) if stacked_file else (
        POOLED_DIR / f"fr_{config}_stacked_raw.parquet"
    )
    out_path = POOLED_DIR / f"fr_{config}_harmonised.parquet"

    if dry_run:
        _dry_run_report(config, stacked_path, out_path, cpi_source)
        return

    if not stacked_path.exists():
        raise FileNotFoundError(
            f"Stacked-raw parquet not found: {stacked_path}\n"
            "Run m1_stack_years.py first."
        )

    phi_map = _load_phi_table(cpi_source)

    LOGGER.info("Loading stacked-raw parquet: %s", stacked_path)
    pooled = pd.read_parquet(stacked_path)
    LOGGER.info("Loaded %d rows, %d columns.", len(pooled), len(pooled.columns))

    harmonised = _deflate(pooled, phi_map)

    POOLED_DIR.mkdir(parents=True, exist_ok=True)
    harmonised.to_parquet(out_path, index=False)
    LOGGER.info("Harmonised parquet written: %s  (%d rows)", out_path, len(harmonised))

    # CPI check manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = RESULTS_DIR / f"M1_cpi_harmonisation_check_{ts}.csv"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    tag_year = {v: k for k, v in YEAR_TAG.items()}
    for tag in sorted(harmonised["year_tag"].unique()):
        year = tag_year.get(int(tag), int(tag))
        phi = phi_map.get(year, float("nan"))
        sub = harmonised[harmonised["year_tag"] == tag]
        row: dict = {"year": year, "year_tag": int(tag), "phi_t": phi, "n_rows": len(sub)}
        for var in MONETARY_VARS:
            real_col = f"{var}_real"
            if real_col in sub.columns:
                row[f"{var}_mean_nominal"] = float(sub[var].mean()) if var in sub.columns else None
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
            "to 2016 prices using phi_t factors from cpi_hicp_fr_harmonisation.csv.\n\n"
            "IMPORTANT: The CPI source file must be created after the S7 decision. "
            "See Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--config",
        choices=["p2", "p3a", "p3b", "p4"],
        required=True,
        help="Pooled configuration (must match the stacked-raw parquet filename).",
    )
    ap.add_argument(
        "--stacked-file",
        type=str,
        default=None,
        help="Override path to stacked-raw parquet (default: "
             "Data/processed/fr/pooled/fr_<config>_stacked_raw.parquet).",
    )
    ap.add_argument(
        "--cpi-source",
        choices=["hicp", "insee"],
        default=None,
        help="Filter cpi_hicp_fr_harmonisation.csv to this source. "
             "If omitted, all rows are used.",
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
            config=args.config,
            stacked_file=args.stacked_file,
            cpi_source=args.cpi_source,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()