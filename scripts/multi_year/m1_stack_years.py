"""
m1_stack_years.py
=================

Stage M1 — stacked-ID builder for multi-year pooled datasets.

Reads per-year MNL parquets, assigns year_tag, computes stacked UIDs using
the base B from the stage config, preserves all raw identifier columns, and
writes a stacked-raw parquet to the configured pooled output directory.

All country/year/config-specific values are read from a stage-config YAML.
Pass --stage-config config/multi_year/fr_p3a_stage_m1.yaml or use the
backward-compatible shortcut --config p3a (resolves to the France P3a YAML).

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §§10-11, 18.
           docs/JMP_multi_year_stage_M1_generalization_report_v1.md

UID scheme (§10):
    B = uid_base  (from config)
    stacked_hh_uid     = year_tag * B + idhh
    stacked_person_uid = year_tag * B + idperson

Not authorised:
    pooled estimation, welfare, canonical MNL promotion, P3b without ISF check.

Usage
-----
    python scripts/multi_year/m1_stack_years.py --config p3a [--dry-run]
    python scripts/multi_year/m1_stack_years.py \\
        --stage-config config/multi_year/fr_p3a_stage_m1.yaml [--dry-run]
    python scripts/multi_year/m1_stack_years.py --help
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

REPO = Path(__file__).resolve().parents[2]

# TAG_YEAR is also exported here so m1_add_cluster_key.py can import it
# (it imports TAG_YEAR from this module for manifest building).
TAG_YEAR: Dict[int, int] = {}  # populated at runtime from config


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _find_parquet(year: int, cfg: StageConfig) -> Optional[Path]:
    """Locate the MNL parquet for a given year using patterns from the config."""
    for pat_template in cfg.input_parquet_patterns:
        pat = pat_template.replace("{year}", str(year))
        candidates = sorted(cfg.input_parquet_dir.glob(pat))
        combined = [p for p in candidates
                    if "combined" in p.name.lower()
                    or ("singles" not in p.name.lower()
                        and "couples" not in p.name.lower())]
        if combined:
            return combined[0]
        if candidates:
            return candidates[0]
    return None


def _resolve_inputs(years: List[int], cfg: StageConfig) -> Dict[int, Optional[Path]]:
    return {yr: _find_parquet(yr, cfg) for yr in years}


# ---------------------------------------------------------------------------
# Guard: P3b (and other blocked configs) require gate checks
# ---------------------------------------------------------------------------

def _check_gates(config_name: str, cfg: StageConfig) -> None:
    key = config_name.lower()
    if key in cfg.blocked_configs:
        raise RuntimeError(
            f"Config '{key}' is not authorised for execution:\n"
            f"{cfg.blocked_configs[key]}"
        )

    if key == "p3b":
        memo = cfg.p3b_isf_memo_path
        if not memo.exists():
            raise FileNotFoundError(
                f"P3b requires the ISF comparability memo at:\n  {memo}\n"
                "Run m1_isf_check_2018.py after FR_2018 EUROMOD output is available."
            )
        text = memo.read_text(encoding="utf-8")
        if cfg.p3b_isf_proceed_phrase not in text.lower():
            raise ValueError(
                f"ISF memo exists but does not conclude '{cfg.p3b_isf_proceed_phrase}'.\n"
                f"Review {memo} before activating P3b."
            )


# ---------------------------------------------------------------------------
# UID computation
# ---------------------------------------------------------------------------

def _add_stacked_ids(df: pd.DataFrame, year: int, cfg: StageConfig) -> pd.DataFrame:
    """Add year_tag, stacked_hh_uid, stacked_person_uid to a per-year DataFrame."""
    tag = cfg.year_tags[year]
    B = cfg.uid_base
    df = df.copy()
    df["year_tag"] = tag

    for col in cfg.raw_id_cols:
        if col not in df.columns:
            raise KeyError(f"Year {year}: required column '{col}' not found in parquet.")
        if df[col].isna().any():
            n_null = df[col].isna().sum()
            raise ValueError(f"Year {year}: column '{col}' has {n_null} null values.")

    idhh_col = cfg.household_id_col
    idperson_col = cfg.person_id_col

    idhh_max = int(df[idhh_col].max())
    idperson_max = int(df[idperson_col].max())
    if idhh_max >= B:
        raise ValueError(
            f"Year {year}: {idhh_col} max ({idhh_max:,}) >= B ({B:,}). UID scheme violated."
        )
    if idperson_max >= B:
        raise ValueError(
            f"Year {year}: {idperson_col} max ({idperson_max:,}) >= B ({B:,}). UID scheme violated."
        )

    df["stacked_hh_uid"] = (
        tag * B + df[idhh_col].astype("int64")
    ).astype("int64")
    df["stacked_person_uid"] = (
        tag * B + df[idperson_col].astype("int64")
    ).astype("int64")

    assert df["stacked_person_uid"].nunique() == len(df), (
        f"Year {year}: stacked_person_uid is not unique per row — collision detected."
    )

    LOGGER.info(
        "  year=%d  tag=%d  rows=%d  "
        "%s_max=%d  %s_max=%d  "
        "stacked_hh_uid in [%d,%d]  stacked_person_uid in [%d,%d]",
        year, tag, len(df),
        idhh_col, idhh_max, idperson_col, idperson_max,
        int(df["stacked_hh_uid"].min()), int(df["stacked_hh_uid"].max()),
        int(df["stacked_person_uid"].min()), int(df["stacked_person_uid"].max()),
    )
    return df


# ---------------------------------------------------------------------------
# Dry-run reporting
# ---------------------------------------------------------------------------

def _dry_run_report(
    config_name: str,
    cfg: StageConfig,
    inputs: Dict[int, Optional[Path]],
    out_path: Path,
) -> None:
    years = cfg.years
    B = cfg.uid_base
    print(f"\n{'='*70}")
    print(f"DRY RUN -- config={config_name}  years={years}")
    print(f"Config YAML: {cfg.yaml_path}")
    print(f"{'='*70}")
    print("\nInputs:")
    all_present = True
    for yr in years:
        p = inputs[yr]
        if p and p.exists():
            size_mb = p.stat().st_size / 1_048_576
            print(f"  [{yr}]  FOUND  {p}  ({size_mb:.1f} MB)")
        else:
            print(f"  [{yr}]  NOT FOUND  (searched {cfg.input_parquet_dir}/)")
            all_present = False

    print(f"\nPlanned output:  {out_path}")
    if all_present:
        print("\nStatus: all inputs present -- ready to run without --dry-run")
    else:
        print("\nStatus: BLOCKED -- one or more inputs missing")
        print(
            "\nMissing inputs require upstream steps:\n"
            "  2015/2017: run EUROMOD FR_2015/FR_2017 then enh_RURO_prep_mnl_basic.py\n"
            "  2018:      FR_2018 EUROMOD output + ISF check (P3b only)"
        )

    print(f"\nUID scheme (B={B:,}):")
    for yr in years:
        tag = cfg.year_tags[yr]
        print(f"  year={yr}  tag={tag}  "
              f"stacked range = [{tag*B+1:,} to {(tag+1)*B-1:,}]")

    print(f"\nRaw IDs to preserve: {cfg.raw_id_cols}")
    print("No parquet written (dry-run mode).\n")


# ---------------------------------------------------------------------------
# Main stack
# ---------------------------------------------------------------------------

def stack(
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    cfg = load_stage_config(config_name, stage_config_path)
    effective_config = config_name or cfg.config_name

    # Populate module-level TAG_YEAR for callers that import it
    global TAG_YEAR
    TAG_YEAR.update(cfg.tag_year)

    _check_gates(effective_config, cfg)

    years = cfg.years
    inputs = _resolve_inputs(years, cfg)
    out_path = cfg.stacked_raw_path()

    if dry_run:
        _dry_run_report(effective_config, cfg, inputs, out_path)
        return

    missing = [yr for yr, p in inputs.items() if p is None or not p.exists()]
    if missing:
        raise FileNotFoundError(
            f"Config '{effective_config}': missing MNL parquets for years {missing}.\n"
            "Run EUROMOD + enh_RURO_prep_mnl_basic.py for those years first."
        )

    LOGGER.info("Stacking config=%s  years=%s", effective_config, years)
    frames: List[pd.DataFrame] = []

    for yr in years:
        p = inputs[yr]
        assert p is not None
        LOGGER.info("Loading year=%d from %s", yr, p)
        df = pd.read_parquet(p)
        df = _add_stacked_ids(df, yr, cfg)
        frames.append(df)

    pooled = pd.concat(frames, ignore_index=True)

    if pooled["stacked_person_uid"].duplicated().any():
        n_dup = pooled["stacked_person_uid"].duplicated().sum()
        raise ValueError(
            f"Cross-year UID collision: {n_dup} duplicate stacked_person_uid values. "
            "Check uid_base sufficiency for this dataset."
        )

    cfg.pooled_output_dir.mkdir(parents=True, exist_ok=True)
    pooled.to_parquet(out_path, index=False)

    # Manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = cfg.results_dir / f"M1_stacked_id_manifest_{ts}.csv"
    cfg.results_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for yr in years:
        tag = cfg.year_tags[yr]
        sub = pooled[pooled["year_tag"] == tag]
        idhh_col = cfg.household_id_col
        idperson_col = cfg.person_id_col
        rows.append({
            "year": yr,
            "year_tag": tag,
            "n_rows": len(sub),
            "n_households": sub[idhh_col].nunique(),
            f"{idhh_col}_max": int(sub[idhh_col].max()),
            f"{idperson_col}_max": int(sub[idperson_col].max()),
            "stacked_hh_uid_min": int(sub["stacked_hh_uid"].min()),
            "stacked_hh_uid_max": int(sub["stacked_hh_uid"].max()),
            "stacked_person_uid_min": int(sub["stacked_person_uid"].min()),
            "stacked_person_uid_max": int(sub["stacked_person_uid"].max()),
            "stacked_person_uid_unique": sub["stacked_person_uid"].nunique(),
            "raw_id_null_count": int(
                sub[cfg.raw_id_cols].isna().any(axis=1).sum()
            ),
        })

    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    LOGGER.info("Manifest written: %s", manifest_path)
    LOGGER.info(
        "Stacked parquet written: %s  (total rows=%d)", out_path, len(pooled)
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 stacked-ID builder. Reads per-year MNL parquets, "
            "assigns year_tag and stacked UIDs (B from config), writes pooled parquet.\n\n"
            "All country/year-specific values come from the stage-config YAML.\n"
            "Use --stage-config for an explicit path, or --config for a shortcut.\n\n"
            "Dry-run mode checks inputs and reports planned outputs without writing."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        type=str,
        help=(
            "Shortcut config name (e.g. p3a). Resolves to the canonical YAML. "
            "Known shortcuts: p2, p3a, p3b, p4 (all resolve to France P3a YAML)."
        ),
    )
    group.add_argument(
        "--stage-config",
        type=str,
        dest="stage_config",
        metavar="YAML_PATH",
        help="Explicit path to a stage-config YAML file.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Check inputs and report planned outputs without writing any file.",
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
        stack(
            config_name=args.config,
            stage_config_path=args.stage_config,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError, RuntimeError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()