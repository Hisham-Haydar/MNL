"""
m1_add_cluster_key.py
=====================

Stage M1 — cluster_id annotation for the RURO multi-year pooled dataset.

Adds cluster_id = idorighh to a harmonised pooled parquet, validates that
idorighh is non-missing, and writes the annotated file in place (or to a
specified output path).

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §12, 18.

Clustering key rule (§12):
    cluster_id = idorighh       (direct copy; no encoding)

Rationale: EUROMOD assigns idhh independently within each year; idorighh is
the stable cross-wave EU-SILC household identifier linking repeat households.
The T1 cluster-robust variance estimator clusters on cluster_id.

P2 note: For the 2015+2016 configuration, idorighh overlaps are zero
(2015 is a different EU-SILC panel). Standard SEs are sufficient but
cluster_id is still written for schema consistency.

Usage
-----
    python scripts/multi_year/m1_add_cluster_key.py --config p3a [--dry-run]
    python scripts/multi_year/m1_add_cluster_key.py \\
        --file path/to/parquet [--out path/to/out.parquet] [--dry-run]
    python scripts/multi_year/m1_add_cluster_key.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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
RESULTS_DIR = REPO / "Results"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def add_cluster_key(
    config: Optional[str] = None,
    file_path: Optional[str] = None,
    out_path: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Add cluster_id = idorighh to a pooled parquet.

    Either --config (resolves to canonical harmonised path) or --file must be
    supplied.  If --out is not supplied, the file is updated in place.
    """
    if file_path:
        in_path = Path(file_path)
    elif config:
        in_path = POOLED_DIR / f"fr_{config.lower()}_harmonised.parquet"
    else:
        raise ValueError("Provide either --config or --file.")

    resolved_out = Path(out_path) if out_path else in_path

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — m1_add_cluster_key")
        print(f"{'='*60}")
        print(f"Input:   {in_path}")
        if in_path.exists():
            size_mb = in_path.stat().st_size / 1_048_576
            print(f"Status:  FOUND  ({size_mb:.1f} MB)")
        else:
            print("Status:  NOT FOUND  (run m1_harmonise_cpi.py first)")
        print(f"Output:  {resolved_out}  (in-place)" if resolved_out == in_path
              else f"Output:  {resolved_out}")
        print("Action:  cluster_id = idorighh  (direct copy)")
        print("No file written (dry-run mode).\n")
        return

    if not in_path.exists():
        raise FileNotFoundError(
            f"Harmonised parquet not found: {in_path}\n"
            "Run m1_harmonise_cpi.py first."
        )

    LOGGER.info("Loading: %s", in_path)
    df = pd.read_parquet(in_path)

    if "idorighh" not in df.columns:
        raise KeyError(
            "Column 'idorighh' not found. "
            "Ensure raw IDs were preserved in m1_stack_years.py (§11)."
        )

    null_count = int(df["idorighh"].isna().sum())
    if null_count > 0:
        raise ValueError(
            f"'idorighh' has {null_count} null values. "
            "Cannot set cluster_id = idorighh with missing values."
        )

    df["cluster_id"] = df["idorighh"]

    # Verify
    assert (df["cluster_id"] == df["idorighh"]).all(), \
        "cluster_id != idorighh after assignment (should not happen)"

    resolved_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(resolved_out, index=False)
    LOGGER.info(
        "cluster_id written to %s  (rows=%d  unique_cluster_id=%d)",
        resolved_out, len(df), df["cluster_id"].nunique()
    )

    # Manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = RESULTS_DIR / f"M1_cluster_key_check_{ts}.csv"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    if "year_tag" in df.columns:
        from scripts.multi_year.m1_stack_years import TAG_YEAR  # type: ignore
        tag_year_map = TAG_YEAR
        for tag in sorted(df["year_tag"].unique()):
            sub = df[df["year_tag"] == tag]
            rows.append({
                "year": tag_year_map.get(int(tag), int(tag)),
                "year_tag": int(tag),
                "n_rows": len(sub),
                "unique_idorighh": sub["idorighh"].nunique(),
                "unique_cluster_id": sub["cluster_id"].nunique(),
                "cluster_id_eq_idorighh": bool(
                    (sub["cluster_id"] == sub["idorighh"]).all()
                ),
            })

        # Cross-year overlap for P3a (2016 ∩ 2017)
        if 2 in df["year_tag"].values and 3 in df["year_tag"].values:
            hh_2016 = set(df.loc[df["year_tag"] == 2, "idorighh"])
            hh_2017 = set(df.loc[df["year_tag"] == 3, "idorighh"])
            overlap_2016_2017 = len(hh_2016 & hh_2017)
            rows.append({
                "year": "2016∩2017 overlap",
                "year_tag": "cross",
                "n_rows": overlap_2016_2017,
                "unique_idorighh": overlap_2016_2017,
                "unique_cluster_id": overlap_2016_2017,
                "cluster_id_eq_idorighh": True,
            })
    else:
        rows.append({
            "year": "all",
            "n_rows": len(df),
            "unique_cluster_id": df["cluster_id"].nunique(),
            "cluster_id_eq_idorighh": True,
        })

    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    LOGGER.info("Cluster-key manifest written: %s", manifest_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 cluster-key annotation. Adds cluster_id = idorighh "
            "to a harmonised pooled parquet."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        choices=["p2", "p3a", "p3b", "p4"],
        help="Pooled configuration (resolves to canonical harmonised parquet path).",
    )
    group.add_argument(
        "--file",
        type=str,
        help="Explicit path to the harmonised parquet to annotate.",
    )
    ap.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output path. Defaults to in-place update of the input file.",
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
        add_cluster_key(
            config=args.config,
            file_path=args.file,
            out_path=args.out,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()