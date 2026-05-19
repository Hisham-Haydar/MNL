"""
m1_stack_years.py
=================

Stage M1 — stacked-ID builder for the RURO multi-year pooled dataset.

Reads per-year MNL parquets, assigns year_tag, computes stacked UIDs using
the single base B = 10**11, preserves all four raw EU-SILC identifiers, and
writes a stacked-raw parquet to Data/processed/fr/pooled/.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §§10–11, 18.

UID scheme (§10):
    B = 10**11
    stacked_hh_uid     = year_tag * B + idhh       (unique per household-year)
    stacked_person_uid = year_tag * B + idperson    (unique per person-year row)

year_tag mapping:
    2015 → 1   2016 → 2   2017 → 3   2018 → 4

Raw IDs preserved (§11):
    idorighh, idorigperson, idhh, idperson

Not authorised (§21):
    pooled estimation, welfare, canonical MNL promotion, P3b without ISF check.

Usage
-----
    python scripts/multi_year/m1_stack_years.py --config p3a [--dry-run]
    python scripts/multi_year/m1_stack_years.py --config p3b [--dry-run]
    python scripts/multi_year/m1_stack_years.py --config p4  [--dry-run]
    python scripts/multi_year/m1_stack_years.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

B = 10**11  # UID base (§10); sufficient since max idperson = 9,378,990,002 < B

YEAR_TAG: Dict[int, int] = {2015: 1, 2016: 2, 2017: 3, 2018: 4}

# Configuration → (years, blocked_reason)
CONFIGS: Dict[str, Tuple[List[int], Optional[str]]] = {
    "p2":  ([2015, 2016], None),
    "p3a": ([2015, 2016, 2017], None),
    "p3b": ([2015, 2016, 2018],
            "P3b is blocked until Results/M1_ISF_tpr_comparability_check_2018.md "
            "concludes 'proceed'. See §16 of the Stage M1 plan."),
    "p4":  ([2015, 2017, 2018],
            "P4 is not a priority configuration. No authorisation in Stage M1."),
}

# Raw identifiers that must be present and non-null (§11)
RAW_ID_COLS = ["idorighh", "idorigperson", "idhh", "idperson"]

# Stage M1 structural columns added by this script
ADDED_COLS = ["year_tag", "stacked_hh_uid", "stacked_person_uid"]


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _find_parquet(year: int) -> Optional[Path]:
    """
    Locate the MNL parquet for a given year.

    Searches Data/processed/fr/ for the canonical single-year RURO MNL
    job/gmm parquet.  Accepts both the existing 2016 naming pattern and the
    anticipated year-parameterised patterns for 2015, 2017, 2018.
    """
    processed = REPO / "Data" / "processed" / "fr"

    # Ordered candidate glob patterns (most specific first)
    patterns = [
        f"*{year}*RURO*mnl*job*gmm*.parquet",
        f"*{year}*RURO*mnl*job*.parquet",
        f"*{year}*RURO*mnl*.parquet",
        f"*{year}*mnl*.parquet",
    ]

    for pat in patterns:
        candidates = sorted(processed.glob(pat))
        # Prefer files that contain 'combined' or lack 'singles'/'couples' prefix,
        # as the stacking should operate on the combined person-level file.
        combined = [p for p in candidates
                    if "combined" in p.name.lower()
                    or ("singles" not in p.name.lower()
                        and "couples" not in p.name.lower())]
        if combined:
            return combined[0]
        if candidates:
            return candidates[0]

    return None


def _resolve_inputs(years: List[int]) -> Dict[int, Optional[Path]]:
    return {yr: _find_parquet(yr) for yr in years}


# ---------------------------------------------------------------------------
# Guard: P3b requires ISF check
# ---------------------------------------------------------------------------

def _check_p3b_gate() -> None:
    memo = RESULTS_DIR / "M1_ISF_tpr_comparability_check_2018.md"
    if not memo.exists():
        raise FileNotFoundError(
            f"P3b requires the ISF comparability memo at:\n  {memo}\n"
            "Run m1_isf_check_2018.py after FR_2018 EUROMOD output is available."
        )
    text = memo.read_text(encoding="utf-8")
    if "proceed with p3b" not in text.lower():
        raise ValueError(
            f"ISF memo exists but does not conclude 'proceed with P3b'.\n"
            f"Review {memo} before activating P3b."
        )


# ---------------------------------------------------------------------------
# UID computation
# ---------------------------------------------------------------------------

def _add_stacked_ids(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Add year_tag, stacked_hh_uid, stacked_person_uid to a per-year DataFrame."""
    tag = YEAR_TAG[year]
    df = df.copy()
    df["year_tag"] = tag

    # Validate raw IDs exist and are non-null
    for col in RAW_ID_COLS:
        if col not in df.columns:
            raise KeyError(f"Year {year}: required column '{col}' not found in parquet.")
        if df[col].isna().any():
            n_null = df[col].isna().sum()
            raise ValueError(f"Year {year}: column '{col}' has {n_null} null values.")

    # Compute UIDs as int64
    idhh_max = int(df["idhh"].max())
    idperson_max = int(df["idperson"].max())
    if idhh_max >= B:
        raise ValueError(
            f"Year {year}: idhh max ({idhh_max:,}) >= B ({B:,}). UID scheme violated."
        )
    if idperson_max >= B:
        raise ValueError(
            f"Year {year}: idperson max ({idperson_max:,}) >= B ({B:,}). UID scheme violated."
        )

    df["stacked_hh_uid"] = (tag * B + df["idhh"].astype("int64")).astype("int64")
    df["stacked_person_uid"] = (tag * B + df["idperson"].astype("int64")).astype("int64")

    # Verify no collisions within this year
    assert df["stacked_person_uid"].nunique() == len(df), (
        f"Year {year}: stacked_person_uid is not unique per row — collision detected."
    )

    LOGGER.info(
        "  year=%d  tag=%d  rows=%d  "
        "idhh_max=%d  idperson_max=%d  "
        "stacked_hh_uid∈[%d,%d]  stacked_person_uid∈[%d,%d]",
        year, tag, len(df),
        idhh_max, idperson_max,
        int(df["stacked_hh_uid"].min()), int(df["stacked_hh_uid"].max()),
        int(df["stacked_person_uid"].min()), int(df["stacked_person_uid"].max()),
    )
    return df


# ---------------------------------------------------------------------------
# Dry-run reporting
# ---------------------------------------------------------------------------

def _dry_run_report(
    config: str,
    years: List[int],
    inputs: Dict[int, Optional[Path]],
    out_path: Path,
) -> None:
    print(f"\n{'='*70}")
    print(f"DRY RUN — config={config}  years={years}")
    print(f"{'='*70}")
    print("\nInputs:")
    all_present = True
    for yr in years:
        p = inputs[yr]
        if p and p.exists():
            size_mb = p.stat().st_size / 1_048_576
            print(f"  [{yr}]  FOUND  {p}  ({size_mb:.1f} MB)")
        else:
            status = f"NOT FOUND  (searched Data/processed/fr/)"
            print(f"  [{yr}]  {status}")
            all_present = False

    print(f"\nPlanned output:  {out_path}")
    if all_present:
        print("\nStatus: all inputs present — ready to run without --dry-run")
    else:
        print("\nStatus: BLOCKED — one or more inputs missing")
        print(
            "\nMissing inputs require upstream steps:\n"
            "  2015/2017: run EUROMOD FR_2015/FR_2017 then enh_RURO_prep_mnl_basic.py\n"
            "  2018:      FR_2018 EUROMOD output + ISF check (P3b only)"
        )

    print(f"\nUID scheme (B={B:,}):")
    for yr in years:
        tag = YEAR_TAG[yr]
        print(f"  year={yr}  tag={tag}  "
              f"stacked range = [{tag*B+1:,} to {(tag+1)*B-1:,}]")

    print(f"\nRaw IDs to preserve: {RAW_ID_COLS}")
    print("No parquet written (dry-run mode).\n")


# ---------------------------------------------------------------------------
# Main stack
# ---------------------------------------------------------------------------

def stack(config: str, dry_run: bool = False) -> None:
    config = config.lower()
    if config not in CONFIGS:
        raise ValueError(f"Unknown config '{config}'. Choose from: {list(CONFIGS)}")

    years, blocked = CONFIGS[config]

    if blocked:
        raise RuntimeError(f"Config '{config}' is not authorised for execution:\n{blocked}")

    if config == "p3b":
        _check_p3b_gate()

    inputs = _resolve_inputs(years)
    out_path = POOLED_DIR / f"fr_{config}_stacked_raw.parquet"

    if dry_run:
        _dry_run_report(config, years, inputs, out_path)
        return

    # Check all inputs present
    missing = [yr for yr, p in inputs.items() if p is None or not p.exists()]
    if missing:
        raise FileNotFoundError(
            f"Config '{config}': missing MNL parquets for years {missing}.\n"
            "Run EUROMOD + enh_RURO_prep_mnl_basic.py for those years first."
        )

    LOGGER.info("Stacking config=%s  years=%s", config, years)
    frames: List[pd.DataFrame] = []

    for yr in years:
        p = inputs[yr]
        assert p is not None  # already checked via `missing` guard above
        LOGGER.info("Loading year=%d from %s", yr, p)
        df = pd.read_parquet(p)
        df = _add_stacked_ids(df, yr)
        frames.append(df)

    pooled = pd.concat(frames, ignore_index=True)

    # Cross-year uniqueness of stacked_person_uid
    if pooled["stacked_person_uid"].duplicated().any():
        n_dup = pooled["stacked_person_uid"].duplicated().sum()
        raise ValueError(
            f"Cross-year UID collision: {n_dup} duplicate stacked_person_uid values. "
            "Check B sufficiency for this dataset."
        )

    POOLED_DIR.mkdir(parents=True, exist_ok=True)
    pooled.to_parquet(out_path, index=False)

    # Manifest
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_path = RESULTS_DIR / f"M1_stacked_id_manifest_{ts}.csv"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for yr in years:
        sub = pooled[pooled["year_tag"] == YEAR_TAG[yr]]
        rows.append({
            "year": yr,
            "year_tag": YEAR_TAG[yr],
            "n_rows": len(sub),
            "n_households": sub["idhh"].nunique(),
            "idhh_max": int(sub["idhh"].max()),
            "idperson_max": int(sub["idperson"].max()),
            "stacked_hh_uid_min": int(sub["stacked_hh_uid"].min()),
            "stacked_hh_uid_max": int(sub["stacked_hh_uid"].max()),
            "stacked_person_uid_min": int(sub["stacked_person_uid"].min()),
            "stacked_person_uid_max": int(sub["stacked_person_uid"].max()),
            "stacked_person_uid_unique": sub["stacked_person_uid"].nunique(),
            "raw_id_null_count": int(
                sub[RAW_ID_COLS].isna().any(axis=1).sum()
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
            "assigns year_tag and stacked UIDs (B=10^11), writes pooled parquet.\n\n"
            "Dry-run mode checks inputs and reports planned outputs without writing."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--config",
        choices=["p2", "p3a", "p3b", "p4"],
        required=True,
        help="Pooled configuration. p3a=primary (2015+2016+2017); p3b=robustness "
             "(blocked until ISF check); p4=not a priority.",
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
        stack(args.config, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError, RuntimeError, KeyError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()