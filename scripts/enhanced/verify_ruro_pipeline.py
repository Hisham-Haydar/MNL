#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_ruro_pipeline.py
=======================

Verification script for RURO pipeline outputs.

Checks:
1. Row counts in draws files (deciders × (n_draws+1))
2. Row counts in EUROMOD output (matches after non-decider replication)
3. Metadata sidecar consistency (id_multiplier, n_draws)
4. Key diagnostics from logs (if available)

Usage:
    python server/verify_ruro_pipeline.py \
        --draws-dir "U:/EUROMOD-STORAGE/Data/processed/fr/2016" \
        --euromod-output "U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet"
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
LOGGER = logging.getLogger(__name__)


def read_parquet_info(path: Path) -> Dict[str, Any]:
    """Read parquet file and return basic info without loading full data."""
    df = pd.read_parquet(path)

    info = {
        "path": str(path),
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": list(df.columns),
        "memory_mb": df.memory_usage(deep=True).sum() / 1024**2,
    }

    # Add key column stats if present
    if "draw" in df.columns:
        info["draws"] = sorted(df["draw"].unique())
        info["n_draws"] = len(info["draws"])

    if "is_decider" in df.columns:
        info["n_deciders"] = (df["is_decider"] == 1).sum()
        info["n_nondeciders"] = (df["is_decider"] == 0).sum()

    if "idperson" in df.columns:
        info["n_unique_persons"] = df["idperson"].nunique()

    if "idperson_true" in df.columns:
        info["n_unique_persons_true"] = df["idperson_true"].nunique()

        # Check decider status by person
        if "is_decider" in df.columns:
            person_decider = df.groupby("idperson_true")["is_decider"].max()
            info["n_decider_persons"] = (person_decider == 1).sum()
            info["n_nondecider_persons"] = (person_decider == 0).sum()

    if "idhh_true" in df.columns:
        info["n_unique_households"] = df["idhh_true"].nunique()

    return info


def read_json_metadata(path: Path) -> Optional[Dict[str, Any]]:
    """Read JSON metadata sidecar file."""
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        LOGGER.warning(f"Failed to read metadata from {path}: {e}")
        return None


def verify_draws_file(draws_path: Path) -> Dict[str, Any]:
    """Verify draws file structure and row counts."""
    LOGGER.info("")
    LOGGER.info("=" * 80)
    LOGGER.info(f"VERIFYING DRAWS FILE: {draws_path.name}")
    LOGGER.info("=" * 80)

    # Read draws file info
    info = read_parquet_info(draws_path)

    LOGGER.info(f"Total rows: {info['n_rows']:,}")
    LOGGER.info(f"Total columns: {info['n_cols']}")
    LOGGER.info(f"Memory usage: {info['memory_mb']:.2f} MB")

    # Check draws
    if "draws" in info:
        LOGGER.info(f"Draws present: {info['draws']}")
        LOGGER.info(f"Number of draws: {info['n_draws']} (0 to {max(info['draws'])})")

    # Check deciders
    if "n_decider_persons" in info:
        LOGGER.info(f"Decider persons: {info['n_decider_persons']:,}")
        LOGGER.info(f"Non-decider persons: {info['n_nondecider_persons']:,}")

        # Expected row count for deciders
        if "n_draws" in info:
            expected_decider_rows = info["n_decider_persons"] * (info["n_draws"])
            LOGGER.info(f"Expected decider rows: {expected_decider_rows:,} "
                       f"({info['n_decider_persons']:,} persons × {info['n_draws']} draws)")

            # Non-deciders should only have draw=0
            expected_nondecider_rows = info["n_nondecider_persons"]
            LOGGER.info(f"Expected non-decider rows: {expected_nondecider_rows:,} "
                       f"({info['n_nondecider_persons']:,} persons × 1 draw)")

            expected_total = expected_decider_rows + expected_nondecider_rows
            LOGGER.info(f"Expected total rows: {expected_total:,}")

            actual_total = info["n_rows"]
            if actual_total == expected_total:
                LOGGER.info(f"✅ Row count matches expected: {actual_total:,}")
            else:
                LOGGER.warning(f"⚠️  Row count mismatch: actual={actual_total:,}, expected={expected_total:,}")

    # Check for metadata sidecar
    meta_path = draws_path.parent / f"{draws_path.stem}__drawsmeta.json"
    metadata = read_json_metadata(meta_path)

    if metadata:
        LOGGER.info("")
        LOGGER.info("Metadata sidecar found:")
        LOGGER.info(f"  id_multiplier: {metadata.get('id_multiplier', 'N/A')}")
        LOGGER.info(f"  n_draws: {metadata.get('n_draws', 'N/A')}")
        LOGGER.info(f"  script: {metadata.get('script', 'N/A')}")
        LOGGER.info(f"  timestamp: {metadata.get('timestamp', 'N/A')}")
        info["metadata"] = metadata
    else:
        LOGGER.warning(f"⚠️  No metadata sidecar found at {meta_path}")

    return info


def verify_euromod_output(euromod_path: Path, draws_info: Dict[str, Any]) -> Dict[str, Any]:
    """Verify EUROMOD output structure and row counts."""
    LOGGER.info("")
    LOGGER.info("=" * 80)
    LOGGER.info(f"VERIFYING EUROMOD OUTPUT: {euromod_path.name}")
    LOGGER.info("=" * 80)

    # Read EUROMOD output info
    info = read_parquet_info(euromod_path)

    LOGGER.info(f"Total rows: {info['n_rows']:,}")
    LOGGER.info(f"Total columns: {info['n_cols']}")
    LOGGER.info(f"Memory usage: {info['memory_mb']:.2f} MB")

    # Check draws
    if "draws" in info:
        LOGGER.info(f"Draws present: {info['draws']}")
        LOGGER.info(f"Number of draws: {info['n_draws']} (0 to {max(info['draws'])})")

    # Check persons
    if "n_unique_persons_true" in info:
        LOGGER.info(f"Unique persons (idperson_true): {info['n_unique_persons_true']:,}")

    # Expected row count after non-decider replication
    if draws_info and "n_draws" in draws_info:
        n_draws = draws_info["n_draws"]

        if "n_decider_persons" in draws_info and "n_nondecider_persons" in draws_info:
            # Deciders: N_deciders × n_draws
            expected_decider_rows = draws_info["n_decider_persons"] * n_draws

            # Non-deciders: replicated for each draw
            expected_nondecider_rows = draws_info["n_nondecider_persons"] * n_draws

            expected_total = expected_decider_rows + expected_nondecider_rows

            LOGGER.info("")
            LOGGER.info("Expected row counts after non-decider replication:")
            LOGGER.info(f"  Decider rows: {expected_decider_rows:,} "
                       f"({draws_info['n_decider_persons']:,} persons × {n_draws} draws)")
            LOGGER.info(f"  Non-decider rows: {expected_nondecider_rows:,} "
                       f"({draws_info['n_nondecider_persons']:,} persons × {n_draws} draws)")
            LOGGER.info(f"  Total expected: {expected_total:,}")

            actual_total = info["n_rows"]
            LOGGER.info(f"  Actual total: {actual_total:,}")

            if actual_total == expected_total:
                LOGGER.info(f"✅ Row count matches expected: {actual_total:,}")
            else:
                diff = actual_total - expected_total
                pct = (diff / expected_total) * 100 if expected_total > 0 else 0
                LOGGER.warning(f"⚠️  Row count mismatch: diff={diff:,} ({pct:+.2f}%)")

    # Check for ils_dispy variation across draws (sample check)
    if "ils_dispy" in info["columns"] and "draw" in info["columns"] and "idperson_true" in info["columns"]:
        LOGGER.info("")
        LOGGER.info("Checking ils_dispy variation across draws (sample)...")

        df = pd.read_parquet(euromod_path)

        # Sample up to 100 persons
        unique_persons = df["idperson_true"].unique()
        n_sample = min(100, len(unique_persons))
        sampled_persons = np.random.choice(unique_persons, size=n_sample, replace=False)

        person_stds = []
        for person_id in sampled_persons:
            person_data = df[df["idperson_true"] == person_id]["ils_dispy"]
            if len(person_data) > 1:
                person_stds.append(person_data.std())

        if person_stds:
            person_stds_arr = np.array(person_stds)
            min_std = person_stds_arr.min()
            median_std = np.median(person_stds_arr)
            max_std = person_stds_arr.max()

            LOGGER.info(f"  Within-person std of ils_dispy (n={n_sample} sampled persons):")
            LOGGER.info(f"    min={min_std:.6f}, median={median_std:.6f}, max={max_std:.6f}")

            near_zero_count = (person_stds_arr < 1e-6).sum()
            near_zero_pct = near_zero_count / len(person_stds_arr) * 100

            if near_zero_pct > 50:
                LOGGER.warning(f"  ⚠️  {near_zero_pct:.1f}% of sampled persons have ils_dispy std < 1e-6!")
                LOGGER.warning(f"      This suggests EUROMOD may not be recalculating across draws.")
            else:
                LOGGER.info(f"  ✅ ils_dispy varies across draws ({near_zero_pct:.1f}% near-zero std)")

    # Check for metadata sidecar
    meta_path = euromod_path.parent / f"{euromod_path.stem}__euromodmeta.json"
    metadata = read_json_metadata(meta_path)

    if metadata:
        LOGGER.info("")
        LOGGER.info("EUROMOD metadata sidecar found:")
        LOGGER.info(f"  system: {metadata.get('system', 'N/A')}")
        LOGGER.info(f"  dataset: {metadata.get('dataset', 'N/A')}")
        LOGGER.info(f"  n_rows: {metadata.get('n_rows', 'N/A')}")
        LOGGER.info(f"  n_draws: {metadata.get('n_draws', 'N/A')}")
        LOGGER.info(f"  id_multiplier: {metadata.get('id_multiplier', 'N/A')}")
        LOGGER.info(f"  script: {metadata.get('script', 'N/A')}")
        LOGGER.info(f"  timestamp: {metadata.get('timestamp', 'N/A')}")

        # Check consistency with draws metadata
        if draws_info and "metadata" in draws_info:
            draws_meta = draws_info["metadata"]

            if "id_multiplier" in draws_meta and "id_multiplier" in metadata:
                if draws_meta["id_multiplier"] == metadata["id_multiplier"]:
                    LOGGER.info(f"  ✅ id_multiplier consistent with draws: {metadata['id_multiplier']}")
                else:
                    LOGGER.warning(f"  ⚠️  id_multiplier mismatch: draws={draws_meta['id_multiplier']}, euromod={metadata['id_multiplier']}")

        info["metadata"] = metadata
    else:
        LOGGER.warning(f"⚠️  No EUROMOD metadata sidecar found at {meta_path}")

    return info


def main():
    parser = argparse.ArgumentParser(description="Verify RURO pipeline outputs")
    parser.add_argument(
        "--draws-dir",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016"),
        help="Directory containing draws files (singles/couples)"
    )
    parser.add_argument(
        "--euromod-output",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet"),
        help="Path to combined EUROMOD output file"
    )
    parser.add_argument(
        "--singles-draws",
        type=str,
        default="singles_RURO_ready_RURO_draws.parquet",
        help="Singles draws filename"
    )
    parser.add_argument(
        "--couples-draws",
        type=str,
        default="couples_RURO_ready_RURO_draws.parquet",
        help="Couples draws filename"
    )

    args = parser.parse_args()

    # Verify draws files
    draws_dir = args.draws_dir

    singles_path = draws_dir / args.singles_draws
    couples_path = draws_dir / args.couples_draws

    all_draws_info = {}

    if singles_path.exists():
        singles_info = verify_draws_file(singles_path)
        all_draws_info["singles"] = singles_info
    else:
        LOGGER.warning(f"⚠️  Singles draws file not found: {singles_path}")

    if couples_path.exists():
        couples_info = verify_draws_file(couples_path)
        all_draws_info["couples"] = couples_info
    else:
        LOGGER.info(f"Couples draws file not found (optional): {couples_path}")

    # Combine draws info for EUROMOD verification
    combined_draws_info = None
    if all_draws_info:
        # Aggregate counts
        combined_draws_info = {
            "n_decider_persons": sum(info.get("n_decider_persons", 0) for info in all_draws_info.values()),
            "n_nondecider_persons": sum(info.get("n_nondecider_persons", 0) for info in all_draws_info.values()),
        }

        # Get n_draws from first available file
        for info in all_draws_info.values():
            if "n_draws" in info:
                combined_draws_info["n_draws"] = info["n_draws"]
                break

        # Get metadata from first available file
        for info in all_draws_info.values():
            if "metadata" in info:
                combined_draws_info["metadata"] = info["metadata"]
                break

    # Verify EUROMOD output
    euromod_path = args.euromod_output

    if euromod_path.exists():
        euromod_info = verify_euromod_output(euromod_path, combined_draws_info)
    else:
        LOGGER.error(f"❌ EUROMOD output file not found: {euromod_path}")

    # Final summary
    LOGGER.info("")
    LOGGER.info("=" * 80)
    LOGGER.info("VERIFICATION SUMMARY")
    LOGGER.info("=" * 80)

    if all_draws_info:
        LOGGER.info("Draws files:")
        for name, info in all_draws_info.items():
            LOGGER.info(f"  {name}: {info['n_rows']:,} rows")

    if euromod_path.exists():
        LOGGER.info(f"EUROMOD output: {euromod_info['n_rows']:,} rows")

    LOGGER.info("")
    LOGGER.info("✅ Verification complete!")


if __name__ == "__main__":
    main()
