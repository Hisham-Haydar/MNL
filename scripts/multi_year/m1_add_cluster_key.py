"""
m1_add_cluster_key.py
=====================

Stage M1 — cluster_id annotation for multi-year pooled datasets.

Adds cluster_id = <cluster_source_col> (from the stage config) to a
harmonised pooled parquet, validates that the source column is non-missing,
and writes the annotated file in place (or to a specified output path).

All country/year/config-specific values are read from a stage-config YAML.
Pass --stage-config config/multi_year/fr_p3a_stage_m1.yaml or use the
backward-compatible shortcut --config p3a.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §12, 18.
           docs/JMP_multi_year_stage_M1_generalization_report_v1.md

Clustering key rule (§12):
    cluster_id = cluster_source_col   (direct copy; no encoding)

For France: cluster_source_col = idorighh (original EU-SILC household ID).

Usage
-----
    python scripts/multi_year/m1_add_cluster_key.py --config p3a [--dry-run]
    python scripts/multi_year/m1_add_cluster_key.py \\
        --stage-config config/multi_year/fr_p3a_stage_m1.yaml [--dry-run]
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

# Ensure repo root is on sys.path so this script runs without PYTHONPATH set.
_SCRIPT_REPO = Path(__file__).resolve().parents[2]
if str(_SCRIPT_REPO) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_REPO))

from scripts.multi_year.m1_config import StageConfig, load_stage_config  # noqa: E402

LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def add_cluster_key(
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
    file_path: Optional[str] = None,
    out_path: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Add cluster_id = cluster_source_col to a pooled parquet.

    Either --stage-config/--config (resolves canonical harmonised path) or
    --file must be supplied.  If --out is not supplied, the file is updated
    in place.
    """
    cfg: Optional[StageConfig] = None

    if file_path:
        in_path = Path(file_path)
        # Still load config if provided (for cluster_source_col name)
        if config_name or stage_config_path:
            cfg = load_stage_config(config_name, stage_config_path)
        cluster_source = cfg.cluster_source_col if cfg else "idorighh"
        cluster_dest = cfg.cluster_id_col if cfg else "cluster_id"
        results_dir = cfg.results_dir if cfg else Path(__file__).resolve().parents[2] / "Results"
    else:
        cfg = load_stage_config(config_name, stage_config_path)
        in_path = cfg.harmonised_path()
        cluster_source = cfg.cluster_source_col
        cluster_dest = cfg.cluster_id_col
        results_dir = cfg.results_dir

    resolved_out = Path(out_path) if out_path else in_path

    if dry_run:
        print(f"\n{'='*60}")
        print("DRY RUN -- m1_add_cluster_key")
        if cfg:
            print(f"Config YAML: {cfg.yaml_path}")
        print(f"{'='*60}")
        print(f"Input:         {in_path}")
        if in_path.exists():
            size_mb = in_path.stat().st_size / 1_048_576
            print(f"Status:        FOUND  ({size_mb:.1f} MB)")
        else:
            print("Status:        NOT FOUND  (run m1_harmonise_cpi.py first)")
        print(f"Output:        {resolved_out}  (in-place)" if resolved_out == in_path
              else f"Output:        {resolved_out}")
        print(f"Action:        {cluster_dest} = {cluster_source}  (direct copy)")
        print("No file written (dry-run mode).\n")
        return

    if not in_path.exists():
        raise FileNotFoundError(
            f"Harmonised parquet not found: {in_path}\n"
            "Run m1_harmonise_cpi.py first."
        )

    LOGGER.info("Loading: %s", in_path)
    df = pd.read_parquet(in_path)

    if cluster_source not in df.columns:
        raise KeyError(
            f"Column '{cluster_source}' not found. "
            "Ensure raw IDs were preserved in m1_stack_years.py (§11)."
        )

    null_count = int(df[cluster_source].isna().sum())
    if null_count > 0:
        raise ValueError(
            f"'{cluster_source}' has {null_count} null values. "
            f"Cannot set {cluster_dest} = {cluster_source} with missing values."
        )

    df[cluster_dest] = df[cluster_source]

    assert (df[cluster_dest] == df[cluster_source]).all(), (
        f"{cluster_dest} != {cluster_source} after assignment (should not happen)"
    )

    resolved_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(resolved_out, index=False)
    LOGGER.info(
        "%s written to %s  (rows=%d  unique_%s=%d)",
        cluster_dest, resolved_out, len(df),
        cluster_dest, df[cluster_dest].nunique(),
    )

    # Manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = results_dir / f"M1_cluster_key_check_{ts}.csv"
    results_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    tag_year = cfg.tag_year if cfg else {}
    if "year_tag" in df.columns:
        for tag in sorted(df["year_tag"].unique()):
            sub = df[df["year_tag"] == tag]
            rows.append({
                "year": tag_year.get(int(tag), int(tag)),
                "year_tag": int(tag),
                "n_rows": len(sub),
                f"unique_{cluster_source}": sub[cluster_source].nunique(),
                f"unique_{cluster_dest}": sub[cluster_dest].nunique(),
                f"{cluster_dest}_eq_{cluster_source}": bool(
                    (sub[cluster_dest] == sub[cluster_source]).all()
                ),
            })

        # Cross-year overlap for any overlapping year pairs
        if cfg:
            tags = sorted(df["year_tag"].unique())
            for i, t1 in enumerate(tags):
                for t2 in tags[i+1:]:
                    yr1 = tag_year.get(int(t1), int(t1))
                    yr2 = tag_year.get(int(t2), int(t2))
                    overlap_key = (min(yr1, yr2), max(yr1, yr2))
                    expected = cfg.expected_overlap_counts.get(overlap_key, "unknown")
                    hh1 = set(df[df["year_tag"] == t1][cluster_source])
                    hh2 = set(df[df["year_tag"] == t2][cluster_source])
                    overlap = len(hh1 & hh2)
                    rows.append({
                        "year": f"{yr1}-{yr2} overlap",
                        "year_tag": "cross",
                        "n_rows": overlap,
                        f"unique_{cluster_source}": overlap,
                        f"unique_{cluster_dest}": overlap,
                        f"{cluster_dest}_eq_{cluster_source}": True,
                        "expected_overlap": expected,
                    })
    else:
        rows.append({
            "year": "all",
            "n_rows": len(df),
            f"unique_{cluster_dest}": df[cluster_dest].nunique(),
            f"{cluster_dest}_eq_{cluster_source}": True,
        })

    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    LOGGER.info("Cluster-key manifest written: %s", manifest_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 cluster-key annotation. Adds cluster_id = cluster_source_col "
            "to a harmonised pooled parquet.\n\n"
            "All country/year-specific values come from the stage-config YAML.\n"
            "Use --stage-config for an explicit path, or --config for a shortcut."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    config_group = ap.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config",
        type=str,
        help="Shortcut config name (e.g. p3a). Resolves to the canonical YAML.",
    )
    config_group.add_argument(
        "--stage-config",
        type=str,
        dest="stage_config",
        metavar="YAML_PATH",
        help="Explicit path to a stage-config YAML file.",
    )
    ap.add_argument(
        "--file",
        type=str,
        default=None,
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
    if not args.config and not args.stage_config and not args.file:
        LOGGER.error("Provide --config, --stage-config, or --file.")
        sys.exit(1)
    try:
        add_cluster_key(
            config_name=args.config,
            stage_config_path=args.stage_config,
            file_path=args.file,
            out_path=args.out,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()