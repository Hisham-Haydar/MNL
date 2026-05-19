"""
m1_validate.py
==============

Stage M1 — validation checks V1-V9 for multi-year pooled datasets.

Implements all validation checks specified in §17 of the Stage M1 plan.
Writes Results/M1_* manifests and prints a pass/fail summary to stdout.

All country/year/config-specific values are read from a stage-config YAML.
Pass --stage-config config/multi_year/fr_p3a_stage_m1.yaml or use the
backward-compatible shortcut --config p3a.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §17, 19.
           docs/JMP_multi_year_stage_M1_generalization_report_v1.md

Checks implemented:
    V1  stacked_person_uid unique per row; stacked_hh_uid unique per hh-year
    V2  row-count agreement with expected totals
    V3  raw-ID completeness (raw_id_cols non-null)
    V4  year_tag coverage matches config
    V5  CPI deflation correctness (spot sample + range check)
    V6  cluster_id == cluster_source_col; expected overlap counts
    V7  person-identity validation (delegates to m1_identity_validation.py logic)
    V8  GSUR coverage (zero missing gsur values; warns if gsur column absent)
    V9  no 'stijn' token in output file path or column names

Usage
-----
    python scripts/multi_year/m1_validate.py --config p3a [--file path/override.parquet]
    python scripts/multi_year/m1_validate.py \\
        --stage-config config/multi_year/fr_p3a_stage_m1.yaml
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

from scripts.multi_year.m1_config import StageConfig, load_stage_config  # noqa: E402

LOGGER = logging.getLogger(__name__)


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

def check_v1(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    if "stacked_person_uid" not in df.columns:
        result.fail("Column 'stacked_person_uid' not found.")
        return
    if "stacked_hh_uid" not in df.columns:
        result.fail("Column 'stacked_hh_uid' not found.")
        return
    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

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

    idhh_col = cfg.household_id_col
    if idhh_col in df.columns:
        n_hh_uid_groups = df.groupby(["year_tag", "stacked_hh_uid"]).ngroups
        n_hh_idhh_groups = df[["year_tag", idhh_col]].drop_duplicates().shape[0]
        if n_hh_uid_groups != n_hh_idhh_groups:
            result.fail(
                f"stacked_hh_uid groupby year_tag mismatch: "
                f"stacked_hh_uid groups={n_hh_uid_groups}, "
                f"(year_tag,{idhh_col}) groups={n_hh_idhh_groups}."
            )
        else:
            result.details.append(
                f"stacked_hh_uid unique per hh-year: "
                f"{n_hh_uid_groups} hh-year groups."
            )
    else:
        result.warn(f"Column '{idhh_col}' not found; skipping hh-uid group check.")

    if result.passed is None:
        result.ok()


# ---------------------------------------------------------------------------
# V2 — row-count agreement
# ---------------------------------------------------------------------------

def check_v2(df: pd.DataFrame, config_key: str, cfg: StageConfig, result: CheckResult) -> None:
    expected = cfg.expected_rows_for(config_key)
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
                f"Row count {n:,} approx expected {expected:,} (diff={diff})."
            )
    else:
        result.warn(
            f"No expected row count for config='{config_key}'. Manual check required."
        )

    if "year_tag" in df.columns:
        idhh_col = cfg.household_id_col
        for tag_val in sorted(df["year_tag"].unique()):
            tag_int = int(tag_val)  # type: ignore[arg-type]
            grp = df[df["year_tag"] == tag_val]
            yr = cfg.tag_year.get(tag_int, tag_int)
            result.details.append(
                f"  year={yr} (tag={tag_int}): {len(grp):,} rows, "
                f"{grp[idhh_col].nunique() if idhh_col in grp.columns else '?'} households"
            )

    result.ok()


# ---------------------------------------------------------------------------
# V3 — raw-ID completeness
# ---------------------------------------------------------------------------

def check_v3(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    raw_id_cols = cfg.raw_id_cols
    missing_cols = [c for c in raw_id_cols if c not in df.columns]
    if missing_cols:
        result.fail(f"Raw ID columns missing: {missing_cols}")
        return

    null_counts = {c: int(df[c].isna().sum()) for c in raw_id_cols}
    any_null = any(v > 0 for v in null_counts.values())
    if any_null:
        result.fail(
            "Null values found in raw ID columns: "
            + ", ".join(f"{c}={n}" for c, n in null_counts.items() if n > 0)
        )
    else:
        result.ok(f"All raw IDs present and non-null: {raw_id_cols}")


# ---------------------------------------------------------------------------
# V4 — year_tag coverage
# ---------------------------------------------------------------------------

def check_v4(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    expected_tags: Set[int] = cfg.expected_year_tags()

    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

    actual_tags = set(int(t) for t in df["year_tag"].unique())
    if actual_tags != expected_tags:
        result.fail(
            f"year_tag set {actual_tags} != expected {expected_tags} "
            f"for config='{cfg.config_name}'."
        )
    else:
        result.ok(f"year_tags {actual_tags} match config='{cfg.config_name}'.")


# ---------------------------------------------------------------------------
# V5 — CPI deflation correctness
# ---------------------------------------------------------------------------

def check_v5(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    if not cfg.cpi_final_path.exists():
        result.skipped(
            f"{cfg.cpi_final_path.name} not found; "
            "§7 CPI source decision not yet completed."
        )
        return

    try:
        cpi_df = pd.read_csv(cfg.cpi_final_path, dtype=str)
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

    nominal_col = cfg.monetary_variables[0] if cfg.monetary_variables else "ils_dispy"
    real_col = f"{nominal_col}_real"

    if real_col not in df.columns or nominal_col not in df.columns:
        result.warn(
            f"Columns '{nominal_col}' and/or '{real_col}' not found. "
            "CPI deflation spot-check skipped."
        )
        return

    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found.")
        return

    errors: List[str] = []
    for tag_val in sorted(df["year_tag"].unique()):
        tag_int = int(tag_val)  # type: ignore[arg-type]
        grp = df[df["year_tag"] == tag_val]
        yr = cfg.tag_year.get(tag_int, None)
        if yr is None:
            continue
        phi = phi_map.get(yr)
        if phi is None:
            result.warn(f"No phi_t for year={yr} in CPI file.")
            continue

        sample = grp.sample(min(100, len(grp)), random_state=42)
        tol = 1e-4
        diffs = (
            sample[real_col]
            - pd.to_numeric(sample[nominal_col], errors="coerce") * phi
        ).abs()
        bad = diffs[diffs > tol]
        if not bad.empty:
            errors.append(
                f"year={yr}: {len(bad)} rows have |{real_col} - {nominal_col}*{phi:.6f}| > {tol}"
            )

        mean_real = float(grp[real_col].mean())
        if not (cfg.ils_dispy_real_min <= mean_real <= cfg.ils_dispy_real_max):
            result.warn(
                f"year={yr}: mean {real_col}={mean_real:,.0f} "
                f"outside expected range "
                f"[{cfg.ils_dispy_real_min:,}-{cfg.ils_dispy_real_max:,}]. "
                "Check RURO sample filter and phi_t."
            )
        else:
            result.details.append(
                f"year={yr}: mean {real_col}={mean_real:,.0f}  phi_t={phi:.6f}  OK"
            )

    if errors:
        result.fail("  ".join(errors))
    else:
        result.ok("CPI spot-checks passed.")


# ---------------------------------------------------------------------------
# V6 — clustering key integrity
# ---------------------------------------------------------------------------

def check_v6(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    cluster_dest = cfg.cluster_id_col
    cluster_src = cfg.cluster_source_col

    if cluster_dest not in df.columns:
        result.fail(
            f"Column '{cluster_dest}' not found (run m1_add_cluster_key.py)."
        )
        return
    if cluster_src not in df.columns:
        result.fail(f"Column '{cluster_src}' not found.")
        return

    if not (df[cluster_dest] == df[cluster_src]).all():
        n_bad = (df[cluster_dest] != df[cluster_src]).sum()
        result.fail(f"{cluster_dest} != {cluster_src} for {n_bad} rows.")
        return

    result.details.append(f"{cluster_dest} == {cluster_src} for all rows")

    if "year_tag" not in df.columns:
        result.ok()
        return

    # Check expected overlap counts from config
    tags: List[int] = sorted(int(t) for t in df["year_tag"].unique())
    for i, t1 in enumerate(tags):
        for t2 in tags[i+1:]:
            yr1: int = cfg.tag_year.get(t1, t1)
            yr2: int = cfg.tag_year.get(t2, t2)
            overlap_key: Tuple[int, int] = (min(yr1, yr2), max(yr1, yr2))
            expected = cfg.expected_overlap_counts.get(overlap_key)
            if expected is None:
                continue

            hh1: set = set(df[df["year_tag"] == t1][cluster_src].tolist())
            hh2: set = set(df[df["year_tag"] == t2][cluster_src].tolist())
            overlap = len(hh1 & hh2)
            diff = abs(overlap - expected)
            msg = (
                f"{yr1} x {yr2} repeat-hh overlap: {overlap:,} "
                f"(expected approx {expected:,}, diff={diff})"
            )
            if diff > cfg.p3a_overlap_tolerance:
                result.warn(
                    f"{msg} -- exceeds tolerance {cfg.p3a_overlap_tolerance}."
                )
            else:
                result.details.append(f"{msg}")

    result.ok()


# ---------------------------------------------------------------------------
# V7 — person-identity validation (inline version)
# ---------------------------------------------------------------------------

def check_v7(df: pd.DataFrame, cfg: StageConfig, result: CheckResult) -> None:
    raw_person = cfg.raw_person_id_col
    raw_hh = cfg.raw_household_id_col
    thr = cfg.identity_thresholds

    if raw_person not in df.columns:
        result.fail(f"Column '{raw_person}' not found; V7 cannot run.")
        return
    if "year_tag" not in df.columns:
        result.fail("Column 'year_tag' not found; V7 cannot run.")
        return

    tags: List[int] = sorted(int(t) for t in df["year_tag"].unique())
    any_overlap = False

    for i, t1 in enumerate(tags):
        for t2 in tags[i+1:]:
            p1: set = set(df[df["year_tag"] == t1][raw_person].tolist())
            p2: set = set(df[df["year_tag"] == t2][raw_person].tolist())
            repeat = p1 & p2
            if not repeat:
                continue
            any_overlap = True
            yr1 = cfg.tag_year.get(t1, t1)
            yr2 = cfg.tag_year.get(t2, t2)
            pair_label = f"{yr1}->{yr2}"

            s1 = df[df["year_tag"] == t1].set_index(raw_person)
            s2 = df[df["year_tag"] == t2].set_index(raw_person)
            common = list(repeat)
            s1 = s1.loc[common]
            s2 = s2.loc[common]

            if "dgn" in s1.columns and "dgn" in s2.columns:
                sex_ok = float((s1["dgn"] == s2["dgn"]).mean())
                if sex_ok < thr["sex_stability_min"]:
                    result.warn(
                        f"{pair_label}: sex stability {sex_ok:.4f} < "
                        f"{thr['sex_stability_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: sex_stability={sex_ok:.4f}"
                    )

            if "dag" in s1.columns and "dag" in s2.columns:
                expected_gap = yr2 - yr1
                delta = s2["dag"] - s1["dag"]
                within_1 = float(((delta - expected_gap).abs() <= 1).mean())
                if within_1 < thr["age_progression_min"]:
                    result.warn(
                        f"{pair_label}: age_progression within_1 = {within_1:.4f} < "
                        f"{thr['age_progression_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: age_progression_within_1={within_1:.4f}"
                    )

                sex_mismatch = (
                    (s1["dgn"] != s2["dgn"])
                    if "dgn" in s1.columns
                    else pd.Series(False, index=s1.index)
                )
                age_off = (delta - expected_gap).abs() > 1
                suspicious = float((sex_mismatch | age_off).mean())
                if suspicious > thr["suspicious_block_max"]:
                    result.fail(
                        f"{pair_label}: suspicious_rate={suspicious:.4f} > "
                        f"block threshold {thr['suspicious_block_max']}"
                    )
                elif suspicious > thr["suspicious_warn_max"]:
                    result.warn(
                        f"{pair_label}: suspicious_rate={suspicious:.4f} > "
                        f"warn threshold {thr['suspicious_warn_max']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: suspicious_rate={suspicious:.4f}"
                    )

            if raw_hh in s1.columns and raw_hh in s2.columns:
                hh_cont = float((s1[raw_hh] == s2[raw_hh]).mean())
                if hh_cont < thr["hh_continuity_min"]:
                    result.warn(
                        f"{pair_label}: hh_continuity={hh_cont:.4f} < "
                        f"{thr['hh_continuity_min']}"
                    )
                else:
                    result.details.append(
                        f"{pair_label}: hh_continuity={hh_cont:.4f}"
                    )

    if not any_overlap:
        result.details.append(
            "No overlapping persons found across year pairs (expected for disjoint panel)."
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
            "Expected after m1_stack_years -> GSUR merge step."
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

    result.ok(f"GSUR columns {gsur_candidates}: zero missing values")


# ---------------------------------------------------------------------------
# V9 — no 'stijn' token
# ---------------------------------------------------------------------------

def check_v9(file_path: Path, df: pd.DataFrame, result: CheckResult) -> None:
    if "stijn" in str(file_path).lower():
        result.fail(f"File path contains 'stijn': {file_path}")
        return

    stijn_cols = [c for c in df.columns if "stijn" in c.lower()]
    if stijn_cols:
        result.fail(f"Columns contain 'stijn' token: {stijn_cols}")
        return

    result.ok("No 'stijn' token in file path or column names")


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def _write_manifests(
    config_key: str,
    df: pd.DataFrame,
    cfg: StageConfig,
    results: Dict[str, CheckResult],
    ts: str,
) -> None:
    cfg.results_dir.mkdir(parents=True, exist_ok=True)

    sid_path = cfg.results_dir / f"M1_stacked_id_manifest_{ts}.csv"
    if "year_tag" in df.columns:
        rows = []
        for tag_val in sorted(df["year_tag"].unique()):
            tag_int = int(tag_val)  # type: ignore[arg-type]
            grp = df[df["year_tag"] == tag_val]
            yr = cfg.tag_year.get(tag_int, tag_int)
            r: dict = {
                "config": config_key,
                "year": yr,
                "year_tag": tag_int,
                "n_rows": len(grp),
            }
            track_cols = cfg.raw_id_cols + ["stacked_hh_uid", "stacked_person_uid"]
            for col in track_cols:
                if col in grp.columns:
                    r[f"{col}_null"] = int(grp[col].isna().sum())
                    r[f"{col}_min"] = int(grp[col].min())  # type: ignore[arg-type]
                    r[f"{col}_max"] = int(grp[col].max())  # type: ignore[arg-type]
                    r[f"{col}_unique"] = grp[col].nunique()
            rows.append(r)
        pd.DataFrame(rows).to_csv(sid_path, index=False)

    rid_path = cfg.results_dir / f"M1_raw_id_preservation_check_{ts}.csv"
    rid_rows = []
    for col in cfg.raw_id_cols:
        rid_rows.append({
            "column": col,
            "present": col in df.columns,
            "null_count": int(df[col].isna().sum()) if col in df.columns else "N/A",
            "total_rows": len(df),
        })
    pd.DataFrame(rid_rows).to_csv(rid_path, index=False)

    summary_path = cfg.results_dir / f"M1_validation_summary_{ts}.csv"
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
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
    file_path: Optional[str] = None,
    skip_checks: Optional[List[str]] = None,
) -> bool:
    cfg = load_stage_config(config_name, stage_config_path)
    config_key = config_name or cfg.config_name
    skip = {s.upper() for s in (skip_checks or [])}

    resolved_path = Path(file_path) if file_path else cfg.harmonised_path()

    if not resolved_path.exists():
        LOGGER.error(
            "Harmonised parquet not found: %s\n"
            "Run m1_stack_years.py -> m1_harmonise_cpi.py -> m1_add_cluster_key.py first.",
            resolved_path
        )
        return False

    LOGGER.info("Loading: %s", resolved_path)
    df = pd.read_parquet(resolved_path)
    LOGGER.info("Loaded %d rows, %d columns.", len(df), len(df.columns))

    checks: Dict[str, CheckResult] = {f"V{i}": CheckResult(f"V{i}") for i in range(1, 10)}

    if "V1" not in skip:
        check_v1(df, cfg, checks["V1"])
    else:
        checks["V1"].skipped("skipped by --skip argument")

    if "V2" not in skip:
        check_v2(df, config_key, cfg, checks["V2"])
    else:
        checks["V2"].skipped("skipped by --skip argument")

    if "V3" not in skip:
        check_v3(df, cfg, checks["V3"])
    else:
        checks["V3"].skipped("skipped by --skip argument")

    if "V4" not in skip:
        check_v4(df, cfg, checks["V4"])
    else:
        checks["V4"].skipped("skipped by --skip argument")

    if "V5" not in skip:
        check_v5(df, cfg, checks["V5"])
    else:
        checks["V5"].skipped("skipped by --skip argument")

    if "V6" not in skip:
        check_v6(df, cfg, checks["V6"])
    else:
        checks["V6"].skipped("skipped by --skip argument")

    if "V7" not in skip:
        check_v7(df, cfg, checks["V7"])
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

    print(f"\n{'='*70}")
    print(f"M1 Validation Summary -- config={config_key}")
    print(f"File: {resolved_path}")
    print(f"Config YAML: {cfg.yaml_path}")
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
    _write_manifests(config_key, df, cfg, checks, ts)

    overall = "PASS" if all_passed else "FAIL"
    print(f"\nOverall: {overall}\n")
    return all_passed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 validation -- runs checks V1-V9 on a harmonised pooled parquet. "
            "Writes Results/M1_* manifests.\n\n"
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
        config_name=args.config,
        stage_config_path=args.stage_config,
        file_path=args.file,
        skip_checks=args.skip,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()