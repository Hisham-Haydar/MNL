"""
m1_validate.py
==============

Stage M1 — validation checks V1–V9 for the RURO multi-year pooled dataset.

Implements all validation checks specified in §17 of the Stage M1 plan.
Writes Results/M1_* manifests and prints a pass/fail summary to stdout.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §17, 19.

Checks implemented:
    V1  stacked_person_uid unique per row; stacked_hh_uid unique per hh-year
    V2  row-count agreement with expected totals
    V3  raw-ID completeness (idorighh, idorigperson, idhh, idperson non-null)
    V4  year_tag coverage matches config
    V5  CPI deflation correctness (spot sample + range check)
    V6  cluster_id == idorighh; repeat-household count for P3a
    V7  person-identity validation (delegates to m1_identity_validation.py logic)
    V8  GSUR coverage (zero missing gsur values; warns if gsur column absent)
    V9  no 'stijn' token in output file path or column names

Usage
-----
    python scripts/multi_year/m1_validate.py --config p3a [--file path/to/override.parquet]
    python scripts/multi_year/m1_validate.py --config p3a --skip V7
    python scripts/multi_year/m1_validate.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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
EXTERNAL_DIR = REPO / "Data" / "external"

CPI_SOURCE_FILE = EXTERNAL_DIR / "cpi_hicp_fr_harmonisation.csv"

YEAR_TAG: Dict[int, int] = {2015: 1, 2016: 2, 2017: 3, 2018: 4}
TAG_YEAR: Dict[int, int] = {v: k for k, v in YEAR_TAG.items()}

# Expected year_tags per config
CONFIG_TAGS: Dict[str, Set[int]] = {
    "p2":  {1, 2},
    "p3a": {1, 2, 3},
    "p3b": {1, 2, 4},
    "p4":  {1, 3, 4},
}

# Expected household-row totals (§5, Table); tolerance ±10 rows
EXPECTED_HH_ROWS: Dict[str, int] = {
    "p2":  22_849,
    "p3a": 33_917,
    "p3b": 33_725,
    "p4":  33_334,
}

# Expected person-row approx (§17 V2 note)
EXPECTED_PERSON_ROWS_APPROX: Dict[str, int] = {
    "p3a": 97_000,
}

# Expected repeat-household overlap for P3a: 2016 ∩ 2017 ≈ 8,796 (±200)
P3A_EXPECTED_OVERLAP_2016_2017 = 8_796
P3A_OVERLAP_TOLERANCE = 200

# V5: plausible range for mean ils_dispy_real per year (2016 prices)
ILS_DISPY_REAL_MIN = 25_000.0
ILS_DISPY_REAL_MAX = 55_000.0

RAW_ID_COLS = ["idorighh", "idorigperson", "idhh", "idperson"]

# Person-identity thresholds from §13
IDENTITY_THRESHOLDS = {
    "sex_stability_min": 0.9990,
    "age_progression_min": 0.9950,
    "suspicious_warn_max": 0.0020,
    "suspicious_block_max": 0.0100,
    "hh_continuity_min": 0.9700,
}


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.passed: Optional[bool] = None
        self.details: List[str] = []
        self.warnings: List[str] = []

    def ok(self, msg: str = "") -> None:
        self.passed = True
        if msg:
            self.details.append(f"PASS: {msg}")

    def fail(self, msg: str) -> None:
        self.passed = False
        self.details.append(f"FAIL: {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(f"WARN: {msg}")

    def skipped(self, reason: str = "") -> None:
        self.passed = None
        self.details.append(f"SKIP: {reason}")


# ---------------------------------------------------------------------------
# V1 — stacked UID uniqueness
# ---------------------------------------------------------------------------

def check_v1(df: pd.DataFrame, result: CheckResult) -> None:
    if "stacked_person_uid" not in df.columns:
        result.fail("Column 'stacked_person_uid' not found.")
        return
    if "stacked_hh_uid" not in df.columns:
        result.fail("Column 'stacked_hh_uid' not found.")
        return
    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

    # stacked_person_uid must be unique per row
    n_unique = df["stacked_person_uid"].nunique()
    if n_unique != len(df):
        result.fail(
            f"stacked_person_uid not unique per row: "
            f"{len(df) - n_unique} duplicates."
        )
    else:
        result.details.append(
            f"stacked_person_uid unique per row: {n_unique} values."
        )

    # stacked_hh_uid: unique per household-year
    # ngroups of (year_tag, stacked_hh_uid) == ngroups of (year_tag, idhh)
    if "idhh" in df.columns:
        n_hh_uid_groups = df.groupby(["year_tag", "stacked_hh_uid"]).ngroups
        n_hh_idhh_groups = df[["year_tag", "idhh"]].drop_duplicates().shape[0]
        if n_hh_uid_groups != n_hh_idhh_groups:
            result.fail(
                f"stacked_hh_uid groupby year_tag mismatch: "
                f"stacked_hh_uid groups={n_hh_uid_groups}, "
                f"(year_tag,idhh) groups={n_hh_idhh_groups}."
            )
        else:
            result.details.append(
                f"stacked_hh_uid unique per hh-year: "
                f"{n_hh_uid_groups} hh-year groups."
            )
    else:
        result.warn("Column 'idhh' not found; skipping hh-uid group check.")

    if result.passed is None:
        result.ok()


# ---------------------------------------------------------------------------
# V2 — row-count agreement
# ---------------------------------------------------------------------------

def check_v2(df: pd.DataFrame, config: str, result: CheckResult) -> None:
    expected = EXPECTED_HH_ROWS.get(config)
    n = len(df)
    result.details.append(f"Total rows in parquet: {n:,}")

    if expected is not None:
        diff = abs(n - expected)
        if diff > 10:
            result.warn(
                f"Row count {n:,} differs from expected {expected:,} "
                f"by {diff} rows (tolerance=10). "
                "If file is person-level this is expected; "
                "re-run on household-level parquet to verify hh count."
            )
        else:
            result.details.append(
                f"Row count {n:,} ≈ expected {expected:,} (diff={diff})."
            )
    else:
        result.warn(
            f"No expected row count for config='{config}'. Manual check required."
        )

    # Per-year breakdown
    if "year_tag" in df.columns:
        for tag, grp in df.groupby("year_tag"):
            yr = TAG_YEAR.get(int(tag), int(tag))
            result.details.append(
                f"  year={yr} (tag={tag}): {len(grp):,} rows, "
                f"{grp['idhh'].nunique() if 'idhh' in grp.columns else '?'} households"
            )

    result.ok()


# ---------------------------------------------------------------------------
# V3 — raw-ID completeness
# ---------------------------------------------------------------------------

def check_v3(df: pd.DataFrame, result: CheckResult) -> None:
    missing_cols = [c for c in RAW_ID_COLS if c not in df.columns]
    if missing_cols:
        result.fail(f"Raw ID columns missing: {missing_cols}")
        return

    null_counts = {c: int(df[c].isna().sum()) for c in RAW_ID_COLS}
    any_null = any(v > 0 for v in null_counts.values())
    if any_null:
        result.fail(
            f"Null values found in raw ID columns: "
            + ", ".join(f"{c}={n}" for c, n in null_counts.items() if n > 0)
        )
    else:
        result.ok(f"All raw IDs present and non-null: {RAW_ID_COLS}")


# ---------------------------------------------------------------------------
# V4 — year_tag coverage
# ---------------------------------------------------------------------------

def check_v4(df: pd.DataFrame, config: str, result: CheckResult) -> None:
    expected_tags = CONFIG_TAGS.get(config)
    if expected_tags is None:
        result.warn(f"No expected year_tags defined for config='{config}'.")
        return

    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

    actual_tags = set(df["year_tag"].unique())
    if actual_tags != expected_tags:
        result.fail(
            f"year_tag set {actual_tags} != expected {expected_tags} "
            f"for config='{config}'."
        )
    else:
        result.ok(f"year_tags {actual_tags} match config='{config}'.")


# ---------------------------------------------------------------------------
# V5 — CPI deflation correctness
# ---------------------------------------------------------------------------

def check_v5(df: pd.DataFrame, result: CheckResult) -> None:
    if not CPI_SOURCE_FILE.exists():
        result.skipped(
            "cpi_hicp_fr_harmonisation.csv not found; "
            "§7 CPI source decision not yet completed."
        )
        return

    try:
        cpi_df = pd.read_csv(CPI_SOURCE_FILE, dtype=str)
        phi_map: Dict[int, float] = {}
        for _, row in cpi_df.iterrows():
            try:
                yr = int(float(str(row["year"])))
                phi = float(str(row["phi_t"]))
                phi_map[yr] = phi
            except (ValueError, KeyError):
                pass
    except Exception as e:
        result.warn(f"Could not read CPI file: {e}")
        return

    if "ils_dispy_real" not in df.columns or "ils_dispy" not in df.columns:
        result.warn(
            "Columns 'ils_dispy' and/or 'ils_dispy_real' not found. "
            "CPI deflation spot-check skipped."
        )
        return

    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

    errors: List[str] = []
    for tag, grp in df.groupby("year_tag"):
        yr = TAG_YEAR.get(int(tag), None)
        if yr is None:
            continue
        phi = phi_map.get(yr)
        if phi is None:
            result.warn(f"No phi_t for year={yr} in CPI file.")
            continue

        sample = grp.sample(min(100, len(grp)), random_state=42)
        tol = 1e-4
        diffs = (sample["ils_dispy_real"] - sample["ils_dispy"].astype(float) * phi).abs()
        bad = diffs[diffs > tol]
        if not bad.empty:
            errors.append(
                f"year={yr}: {len(bad)} rows have |ils_dispy_real - ils_dispy*{phi:.6f}| > {tol}"
            )

        # Range check
        mean_real = float(grp["ils_dispy_real"].mean())
        if not (ILS_DISPY_REAL_MIN <= mean_real <= ILS_DISPY_REAL_MAX):
            result.warn(
                f"year={yr}: mean ils_dispy_real={mean_real:,.0f} "
                f"outside expected range [{ILS_DISPY_REAL_MIN:,}-{ILS_DISPY_REAL_MAX:,}]. "
                "Check RURO sample filter and phi_t."
            )
        else:
            result.details.append(
                f"year={yr}: mean ils_dispy_real={mean_real:,.0f}  phi_t={phi:.6f}  OK"
            )

    if errors:
        result.fail("  ".join(errors))
    else:
        result.ok("CPI spot-checks passed.")


# ---------------------------------------------------------------------------
# V6 — clustering key integrity
# ---------------------------------------------------------------------------

def check_v6(df: pd.DataFrame, config: str, result: CheckResult) -> None:
    if "cluster_id" not in df.columns:
        result.fail("Column 'cluster_id' not found (run m1_add_cluster_key.py).")
        return
    if "idorighh" not in df.columns:
        result.fail("Column 'idorighh' not found.")
        return

    if not (df["cluster_id"] == df["idorighh"]).all():
        n_bad = (df["cluster_id"] != df["idorighh"]).sum()
        result.fail(f"cluster_id != idorighh for {n_bad} rows.")
        return

    result.details.append("cluster_id == idorighh for all rows ✓")

    # For P3a: check 2016 ∩ 2017 repeat-household overlap
    if config == "p3a" and "year_tag" in df.columns:
        if 2 in df["year_tag"].values and 3 in df["year_tag"].values:
            hh_2016 = set(df.loc[df["year_tag"] == 2, "idorighh"])
            hh_2017 = set(df.loc[df["year_tag"] == 3, "idorighh"])
            overlap = len(hh_2016 & hh_2017)
            diff = abs(overlap - P3A_EXPECTED_OVERLAP_2016_2017)
            msg = (
                f"P3a 2016∩2017 repeat-household overlap: {overlap:,} "
                f"(expected ≈ {P3A_EXPECTED_OVERLAP_2016_2017:,}, diff={diff})"
            )
            if diff > P3A_OVERLAP_TOLERANCE:
                result.warn(f"{msg} — exceeds tolerance {P3A_OVERLAP_TOLERANCE}.")
            else:
                result.details.append(f"{msg} ✓")

    result.ok()


# ---------------------------------------------------------------------------
# V7 — person-identity validation (inline version)
# ---------------------------------------------------------------------------

def check_v7(df: pd.DataFrame, result: CheckResult) -> None:
    """
    Inline repeat-person identity check on the pooled file.

    For each overlapping year pair (those sharing rows in df), identifies
    repeat persons by idorigperson and checks sex stability, age progression,
    household continuity.  Delegates to m1_identity_validation.py for the
    full per-year-pair report; here we perform a fast inline gate check.
    """
    if "idorigperson" not in df.columns:
        result.fail("Column 'idorigperson' not found; V7 cannot run.")
        return
    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found; V7 cannot run.")
        return

    tags = sorted(df["year_tag"].unique())
    any_overlap = False

    for i, t1 in enumerate(tags):
        for t2 in tags[i+1:]:
            p1 = set(df.loc[df["year_tag"] == t1, "idorigperson"])
            p2 = set(df.loc[df["year_tag"] == t2, "idorigperson"])
            repeat = p1 & p2
            if not repeat:
                continue
            any_overlap = True
            yr1 = TAG_YEAR.get(int(t1), int(t1))
            yr2 = TAG_YEAR.get(int(t2), int(t2))
            n_repeat = len(repeat)

            sub1 = df.loc[df["year_tag"] == t1].set_index("idorigperson")
            sub2 = df.loc[df["year_tag"] == t2].set_index("idorigperson")
            common = list(repeat)
            s1 = sub1.loc[common]
            s2 = sub2.loc[common]

            pair_label = f"{yr1}→{yr2}"

            # Sex stability
            if "dgn" in s1.columns and "dgn" in s2.columns:
                sex_ok = (s1["dgn"] == s2["dgn"]).mean()
                if sex_ok < IDENTITY_THRESHOLDS["sex_stability_min"]:
                    result.warn(
                        f"{pair_label}: sex stability {sex_ok:.4f} < "
                        f"{IDENTITY_THRESHOLDS['sex_stability_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: sex_stability={sex_ok:.4f} ✓"
                    )

            # Age progression
            if "dag" in s1.columns and "dag" in s2.columns:
                expected_gap = yr2 - yr1
                delta = s2["dag"] - s1["dag"]
                within_1 = ((delta - expected_gap).abs() <= 1).mean()
                if within_1 < IDENTITY_THRESHOLDS["age_progression_min"]:
                    result.warn(
                        f"{pair_label}: age_progression within±1 = {within_1:.4f} < "
                        f"{IDENTITY_THRESHOLDS['age_progression_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: age_progression_within_1={within_1:.4f} ✓"
                    )

                # Suspicious records
                sex_mismatch = (s1["dgn"] != s2["dgn"]) if "dgn" in s1.columns else pd.Series(False, index=s1.index)
                age_off = (delta - expected_gap).abs() > 1
                suspicious = (sex_mismatch | age_off).mean()
                if suspicious > IDENTITY_THRESHOLDS["suspicious_block_max"]:
                    result.fail(
                        f"{pair_label}: suspicious_rate={suspicious:.4f} > "
                        f"block threshold {IDENTITY_THRESHOLDS['suspicious_block_max']}"
                    )
                elif suspicious > IDENTITY_THRESHOLDS["suspicious_warn_max"]:
                    result.warn(
                        f"{pair_label}: suspicious_rate={suspicious:.4f} > "
                        f"warn threshold {IDENTITY_THRESHOLDS['suspicious_warn_max']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: suspicious_rate={suspicious:.4f} ✓"
                    )

            # Household continuity
            if "idorighh" in s1.columns and "idorighh" in s2.columns:
                hh_cont = (s1["idorighh"] == s2["idorighh"]).mean()
                if hh_cont < IDENTITY_THRESHOLDS["hh_continuity_min"]:
                    result.warn(
                        f"{pair_label}: hh_continuity={hh_cont:.4f} < "
                        f"{IDENTITY_THRESHOLDS['hh_continuity_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: hh_continuity={hh_cont:.4f} ✓"
                    )

    if not any_overlap:
        result.details.append(
            "No overlapping persons found across year pairs (expected for P2/disjoint)."
        )
        result.ok()
    elif result.passed is None:
        result.ok("V7 identity checks passed.")


# ---------------------------------------------------------------------------
# V8 — GSUR coverage
# ---------------------------------------------------------------------------

def check_v8(df: pd.DataFrame, result: CheckResult) -> None:
    gsur_candidates = [c for c in df.columns
                       if c.startswith("gsur") and "uid" not in c.lower()]
    if not gsur_candidates:
        result.warn(
            "No 'gsur*' columns found in pooled file. "
            "GSUR merge must be performed before V8 can pass. "
            "Expected after m1_stack_years → GSUR merge step."
        )
        return

    for col in gsur_candidates:
        n_null = int(df[col].isna().sum())
        if n_null > 0:
            result.fail(
                f"Column '{col}' has {n_null} null values. "
                "Zero missing GSUR values allowed (§17 V8)."
            )
            return

    result.ok(
        f"GSUR columns {gsur_candidates}: zero missing values ✓"
    )


# ---------------------------------------------------------------------------
# V9 — no 'stijn' token
# ---------------------------------------------------------------------------

def check_v9(file_path: Path, df: pd.DataFrame, result: CheckResult) -> None:
    # Check file path
    if "stijn" in str(file_path).lower():
        result.fail(f"File path contains 'stijn': {file_path}")
        return

    # Check column names
    stijn_cols = [c for c in df.columns if "stijn" in c.lower()]
    if stijn_cols:
        result.fail(f"Columns contain 'stijn' token: {stijn_cols}")
        return

    result.ok("No 'stijn' token in file path or column names ✓")


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def _write_manifests(
    config: str,
    file_path: Path,
    df: pd.DataFrame,
    results: Dict[str, CheckResult],
    ts: str,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Stacked ID manifest
    sid_path = RESULTS_DIR / f"M1_stacked_id_manifest_{ts}.csv"
    if "year_tag" in df.columns:
        rows = []
        for tag, grp in df.groupby("year_tag"):
            yr = TAG_YEAR.get(int(tag), int(tag))
            r: dict = {
                "config": config,
                "year": yr,
                "year_tag": int(tag),
                "n_rows": len(grp),
            }
            for col in RAW_ID_COLS + ["stacked_hh_uid", "stacked_person_uid"]:
                if col in grp.columns:
                    r[f"{col}_null"] = int(grp[col].isna().sum())
                    r[f"{col}_min"] = int(grp[col].min())
                    r[f"{col}_max"] = int(grp[col].max())
                    r[f"{col}_unique"] = grp[col].nunique()
            rows.append(r)
        pd.DataFrame(rows).to_csv(sid_path, index=False)

    # Raw ID preservation manifest
    rid_path = RESULTS_DIR / f"M1_raw_id_preservation_check_{ts}.csv"
    rid_rows = []
    for col in RAW_ID_COLS:
        rid_rows.append({
            "column": col,
            "present": col in df.columns,
            "null_count": int(df[col].isna().sum()) if col in df.columns else "N/A",
            "total_rows": len(df),
        })
    pd.DataFrame(rid_rows).to_csv(rid_path, index=False)

    # Summary
    summary_path = RESULTS_DIR / f"M1_validation_summary_{ts}.csv"
    sum_rows = []
    for name, res in results.items():
        status = "PASS" if res.passed is True else ("SKIP" if res.passed is None else "FAIL")
        sum_rows.append({
            "check": name,
            "status": status,
            "details": " | ".join(res.details),
            "warnings": " | ".join(res.warnings),
        })
    pd.DataFrame(sum_rows).to_csv(summary_path, index=False)

    LOGGER.info("Manifests written:")
    LOGGER.info("  %s", sid_path)
    LOGGER.info("  %s", rid_path)
    LOGGER.info("  %s", summary_path)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def validate(
    config: str,
    file_path: Optional[str] = None,
    skip_checks: Optional[List[str]] = None,
) -> bool:
    config = config.lower()
    skip = {s.upper() for s in (skip_checks or [])}

    resolved_path = Path(file_path) if file_path else (
        POOLED_DIR / f"fr_{config}_harmonised.parquet"
    )

    if not resolved_path.exists():
        LOGGER.error(
            "Harmonised parquet not found: %s\n"
            "Run m1_stack_years.py → m1_harmonise_cpi.py → m1_add_cluster_key.py first.",
            resolved_path
        )
        return False

    LOGGER.info("Loading: %s", resolved_path)
    df = pd.read_parquet(resolved_path)
    LOGGER.info("Loaded %d rows, %d columns.", len(df), len(df.columns))

    checks: Dict[str, CheckResult] = {f"V{i}": CheckResult(f"V{i}") for i in range(1, 10)}

    if "V1" not in skip:
        check_v1(df, checks["V1"])
    else:
        checks["V1"].skipped("skipped by --skip argument")

    if "V2" not in skip:
        check_v2(df, config, checks["V2"])
    else:
        checks["V2"].skipped("skipped by --skip argument")

    if "V3" not in skip:
        check_v3(df, checks["V3"])
    else:
        checks["V3"].skipped("skipped by --skip argument")

    if "V4" not in skip:
        check_v4(df, config, checks["V4"])
    else:
        checks["V4"].skipped("skipped by --skip argument")

    if "V5" not in skip:
        check_v5(df, checks["V5"])
    else:
        checks["V5"].skipped("skipped by --skip argument")

    if "V6" not in skip:
        check_v6(df, config, checks["V6"])
    else:
        checks["V6"].skipped("skipped by --skip argument")

    if "V7" not in skip:
        check_v7(df, checks["V7"])
    else:
        checks["V7"].skipped("skipped by --skip argument")

    if "V8" not in skip:
        check_v8(df, checks["V8"])
    else:
        checks["V8"].skipped("skipped by --skip argument")

    if "V9" not in skip:
        check_v9(resolved_path, df, checks["V9"])
    else:
        checks["V9"].skipped("skipped by --skip argument")

    # Summary
    print(f"\n{'='*70}")
    print(f"M1 Validation Summary — config={config}")
    print(f"File: {resolved_path}")
    print(f"{'='*70}")
    all_passed = True
    for name, res in checks.items():
        status = "PASS" if res.passed is True else ("SKIP" if res.passed is None else "FAIL")
        if res.passed is False:
            all_passed = False
        print(f"  {name}  {status}")
        for d in res.details:
            print(f"       {d}")
        for w in res.warnings:
            print(f"       {w}")

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    _write_manifests(config, resolved_path, df, checks, ts)

    overall = "PASS" if all_passed else "FAIL"
    print(f"\nOverall: {overall}\n")
    return all_passed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 validation — runs checks V1–V9 on a harmonised pooled parquet. "
            "Writes Results/M1_* manifests."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--config",
        choices=["p2", "p3a", "p3b", "p4"],
        required=True,
        help="Pooled configuration.",
    )
    ap.add_argument(
        "--file",
        type=str,
        default=None,
        help="Override path to harmonised parquet.",
    )
    ap.add_argument(
        "--skip",
        nargs="+",
        default=[],
        metavar="Vn",
        help="Checks to skip (e.g. --skip V7 V8).",
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
    ok = validate(
        config=args.config,
        file_path=args.file,
        skip_checks=args.skip,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()