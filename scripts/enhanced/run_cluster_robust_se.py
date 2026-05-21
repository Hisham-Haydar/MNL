#!/usr/bin/env python
"""
==============================================================================
Cluster-Robust SE — Smoke-Test / Dry-Run CLI
==============================================================================
GA17 clearance interface. Loads the pooled parquet (bounded read), builds
precomputed data structures, runs T1–T4 validation checks at a dummy-theta
(initial_values from the YAML), and writes a validation JSON.

Does NOT run estimation. Does NOT require converged parameters.
Does NOT modify data parquets. Does NOT authorize pooled estimation.

Usage (smoke-test / dry-run — GA17 clearance):
    python run_cluster_robust_se.py \\
        --spec scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \\
        --parquet Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet \\
        --output Results/RURO_cluster_robust_SE_static_validation_v1.md \\
        --mode smoke-test

Usage (post-estimation — requires --results-json):
    python run_cluster_robust_se.py \\
        --spec ... \\
        --parquet ... \\
        --results-json outputs/.../estimation_results.json \\
        --output Results/cluster_robust_se_results.json \\
        --mode post-estimation

Author: Enhanced RURO Pipeline
Created: 2026-05-21
==============================================================================
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Setup path
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from estimation_spec_parser import parse_specification
from estimation_utils import (
    precompute_data_singles,
    precompute_data_couples,
)
from estimation_engine import compute_gradient_joint, compute_scores_joint
from cluster_robust_se import (
    assemble_meat_matrix,
    compute_cluster_robust_se,
    run_t1_sign_check,
    run_t2_symmetry_check,
    run_t3_cluster_count_check,
    run_t4_se_positivity_check,
    run_t5_vs_hessian_check,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bounded parquet read (GA13–GA16 compliant)
# ---------------------------------------------------------------------------

_REQUIRED_COLS = [
    "year_tag", "gsur", "cluster_id", "idorighh", "household_type",
    "idhh", "draw", "hours", "prior", "c_norm",
    "l_norm", "l_norm_male", "l_norm_female",
    "hours_male", "hours_female",
    "gsur_male", "gsur_female",
    "ils_dispy_real",
]

_SMOKE_ROW_LIMIT = 200_000  # hard ceiling; never loads full 1.24 M rows in smoke mode


def _bounded_schema_read(parquet_path: Path) -> list:
    """Return column list without loading row data."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(parquet_path)
    return pf.schema_arrow.names


def _bounded_col_read(parquet_path: Path, cols: Optional[list], max_rows: int) -> pd.DataFrame:
    """Read selected columns (or all if cols is None) up to max_rows via row-group iteration."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(parquet_path)
    schema_names = pf.schema_arrow.names
    if cols is not None:
        cols_to_read = [c for c in cols if c in schema_names]
    else:
        cols_to_read = schema_names
    frames = []
    total = 0
    for rg in range(pf.metadata.num_row_groups):
        chunk = pf.read_row_group(rg, columns=cols_to_read)
        df_chunk = chunk.to_pandas()
        frames.append(df_chunk)
        total += len(df_chunk)
        if total >= max_rows:
            break
    df = pd.concat(frames, ignore_index=True).head(max_rows)
    return df


def _load_full_split(
    parquet_path: Path,
    household_type_singles: str = "single",
    household_type_couples: str = "couple",
) -> tuple:
    """
    Load full parquet and split into singles/couples DataFrames.
    Only called in post-estimation mode.
    """
    logger.info(f"Loading full parquet: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    logger.info(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

    if "household_type" in df.columns:
        df_singles = df[df["household_type"] == household_type_singles].copy()
        df_couples = df[df["household_type"] == household_type_couples].copy()
    else:
        # Fallback: use presence of gender-specific columns
        has_hours_male = "hours_male" in df.columns
        if has_hours_male:
            df_couples = df[df["hours_male"].notna()].copy()
            df_singles = df[~df.index.isin(df_couples.index)].copy()
        else:
            df_singles = df.copy()
            df_couples = pd.DataFrame()

    logger.info(f"  Singles: {len(df_singles):,} rows  |  Couples: {len(df_couples):,} rows")
    return df_singles, df_couples


# ---------------------------------------------------------------------------
# Smoke-test mode
# ---------------------------------------------------------------------------

def run_smoke_test(
    spec_path: Path,
    parquet_path: Path,
    output_path: Path,
) -> dict:
    """
    GA17 smoke test.

    Validates the score interface and sandwich infrastructure at initial_values
    (dummy theta). Does NOT run estimation.

    Returns dict with all validation results; also writes to output_path.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = {
        "run_timestamp": ts,
        "mode": "smoke-test",
        "spec": str(spec_path),
        "parquet": str(parquet_path),
        "checks": {},
    }

    # ------------------------------------------------------------------
    # C1: Module imports
    # ------------------------------------------------------------------
    results["checks"]["C1_module_imports"] = {"passed": True, "note": "all imports succeeded"}
    logger.info("[C1] Module imports: PASS")

    # ------------------------------------------------------------------
    # C2: CLI --help works
    # ------------------------------------------------------------------
    try:
        parser = build_parser()
        parser.parse_args(["--spec", str(spec_path), "--parquet", str(parquet_path), "--help"])
        # parse_args with --help raises SystemExit(0) — catch it as success
        results["checks"]["C2_cli_help_works"] = {"passed": True, "note": "argparse --help exits cleanly"}
    except SystemExit as exc:
        c2_pass = (exc.code == 0)
        results["checks"]["C2_cli_help_works"] = {
            "passed": c2_pass,
            "note": f"argparse --help exited with code {exc.code}",
        }
        logger.info(f"[C2] CLI --help: {'PASS' if c2_pass else 'FAIL'}")
    except Exception as exc:
        results["checks"]["C2_cli_help_works"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C2] CLI --help FAILED: {exc}")

    # ------------------------------------------------------------------
    # C3: Parse spec
    # ------------------------------------------------------------------
    try:
        spec = parse_specification(spec_path)
        n_params = len(spec.all_param_names)
        results["checks"]["C3_spec_parses"] = {"passed": True, "n_params": n_params}
        logger.info(f"[C3] Spec parses: PASS  (n_params={n_params})")
    except Exception as exc:
        results["checks"]["C3_spec_parses"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C3] Spec parse FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # C4: Free-parameter vector length == 55
    # ------------------------------------------------------------------
    expected_n = 55
    c4_pass = (n_params == expected_n)
    results["checks"]["C4_free_param_length"] = {
        "passed": c4_pass, "n_params": n_params, "expected": expected_n,
    }
    logger.info(f"[C4] Free-param length = {n_params}: {'PASS' if c4_pass else 'FAIL'}")

    # ------------------------------------------------------------------
    # C5: Schema readable
    # ------------------------------------------------------------------
    try:
        schema_cols = _bounded_schema_read(parquet_path)
        results["checks"]["C5_schema_readable"] = {
            "passed": True, "n_columns": len(schema_cols),
        }
        logger.info(f"[C5] Schema readable: PASS  ({len(schema_cols)} columns)")
    except Exception as exc:
        results["checks"]["C5_schema_readable"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C5] Schema read FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # C6: cluster_id exists
    # ------------------------------------------------------------------
    c6_pass = "cluster_id" in schema_cols
    results["checks"]["C6_cluster_id_exists"] = {"passed": c6_pass}
    logger.info(f"[C6] cluster_id column exists: {'PASS' if c6_pass else 'FAIL'}")

    # ------------------------------------------------------------------
    # C7: cluster_id == idorighh on bounded sample
    # ------------------------------------------------------------------
    try:
        df_sample = _bounded_col_read(
            parquet_path,
            cols=["cluster_id", "idorighh", "year_tag", "household_type", "idhh", "draw"],
            max_rows=50_000,
        )
        if "cluster_id" in df_sample.columns and "idorighh" in df_sample.columns:
            equal_count = (df_sample["cluster_id"] == df_sample["idorighh"]).sum()
            total_count = len(df_sample)
            pct = equal_count / total_count * 100
            c7_pass = (equal_count == total_count)
            results["checks"]["C7_cluster_id_eq_idorighh"] = {
                "passed": c7_pass,
                "rows_checked": total_count,
                "rows_equal": int(equal_count),
                "pct_equal": round(pct, 4),
            }
            logger.info(f"[C7] cluster_id == idorighh: {equal_count}/{total_count} ({pct:.2f}%): {'PASS' if c7_pass else 'FAIL'}")
        else:
            results["checks"]["C7_cluster_id_eq_idorighh"] = {
                "passed": False, "note": "cluster_id or idorighh missing from bounded sample",
            }
            logger.warning("[C7] cluster_id or idorighh missing")
    except Exception as exc:
        results["checks"]["C7_cluster_id_eq_idorighh"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C7] FAILED: {exc}")

    # ------------------------------------------------------------------
    # C8: Cluster count documented (bounded sample only — cannot require 9,657 without full load)
    # ------------------------------------------------------------------
    try:
        if "idorighh" in df_sample.columns:
            n_unique_sample = df_sample["idorighh"].nunique()
            results["checks"]["C8_cluster_count_documented"] = {
                "passed": True,
                "note": f"Bounded sample ({len(df_sample):,} rows) contains {n_unique_sample} unique idorighh. "
                        "Full dataset expected 9,657 clusters per GA16.",
                "n_unique_in_sample": n_unique_sample,
                "expected_full": 9657,
            }
            logger.info(f"[C8] Clusters in bounded sample: {n_unique_sample} (full expected 9,657): PASS (documented)")
    except Exception as exc:
        results["checks"]["C8_cluster_count_documented"] = {"passed": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Load bounded data for smoke test
    # ------------------------------------------------------------------
    # Load a bounded subset to build precomputed data and run the score interface.
    # Use first row-group(s) up to _SMOKE_ROW_LIMIT rows.
    logger.info(f"Loading bounded parquet data for smoke test (max {_SMOKE_ROW_LIMIT:,} rows)...")
    try:
        df_smoke = _bounded_col_read(parquet_path, cols=None, max_rows=_SMOKE_ROW_LIMIT)
        logger.info(f"  Loaded {len(df_smoke):,} rows, {len(df_smoke.columns)} cols")
    except Exception as exc:
        results["checks"]["smoke_data_load"] = {"passed": False, "error": str(exc)}
        logger.error(f"Smoke data load FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # Split by household_type
    if "household_type" in df_smoke.columns:
        htypes = df_smoke["household_type"].unique().tolist()
        results["household_types_found"] = htypes
        df_s = df_smoke[df_smoke["household_type"].isin(["single", "singles", "s"])].copy()
        df_c = df_smoke[df_smoke["household_type"].isin(["couple", "couples", "c"])].copy()
    else:
        df_s = df_smoke.copy()
        df_c = pd.DataFrame()
    logger.info(f"  Singles: {len(df_s):,} rows | Couples: {len(df_c):,} rows")

    # Sort by idhh (required by precompute functions)
    if "idhh" in df_s.columns:
        df_s = df_s.sort_values("idhh").reset_index(drop=True)
    if len(df_c) > 0 and "idhh" in df_c.columns:
        df_c = df_c.sort_values("idhh").reset_index(drop=True)

    # Build minimal metadata
    metadata = _build_minimal_metadata(df_s, df_c)

    # ------------------------------------------------------------------
    # Determine gender split for singles
    # ------------------------------------------------------------------
    gender_col = "dgn" if "dgn" in df_s.columns else ("sex" if "sex" in df_s.columns else None)
    if gender_col and len(df_s) > 0:
        df_sm = df_s[df_s[gender_col] == 1].copy() if gender_col == "dgn" else df_s[df_s[gender_col].isin([1, "M", "m"])].copy()
        df_sf = df_s[df_s[gender_col] == 0].copy() if gender_col == "dgn" else df_s[df_s[gender_col].isin([0, "F", "f"])].copy()
    else:
        df_sm = df_s.copy()
        df_sf = pd.DataFrame()

    # ------------------------------------------------------------------
    # Precompute data
    # ------------------------------------------------------------------
    data_sm = data_sf = data_cou = None
    include_wage = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc = (spec.wage_spec == "loc_empirical")

    # Collect extra vars from spec
    extra_vars = _collect_extra_vars(spec)

    try:
        if len(df_sm) > 0 and "idhh" in df_sm.columns and "c_norm" in df_sm.columns:
            if df_sm["idhh"].is_monotonic_increasing:
                data_sm = precompute_data_singles(
                    df=df_sm, metadata=metadata, is_male=True,
                    include_wage_vars=include_wage, include_loc_vars=include_loc,
                    include_extra_vars=extra_vars,
                )
        if len(df_sf) > 0 and "idhh" in df_sf.columns and "c_norm" in df_sf.columns:
            if df_sf["idhh"].is_monotonic_increasing:
                data_sf = precompute_data_singles(
                    df=df_sf, metadata=metadata, is_male=False,
                    include_wage_vars=include_wage, include_loc_vars=include_loc,
                    include_extra_vars=extra_vars,
                )
        if len(df_c) > 0 and "idhh" in df_c.columns and "c_norm" in df_c.columns:
            if df_c["idhh"].is_monotonic_increasing:
                data_cou = precompute_data_couples(
                    df=df_c, metadata=metadata,
                    include_wage_vars=include_wage, include_loc_vars=include_loc,
                    include_extra_vars=extra_vars,
                )
    except Exception as exc:
        results["checks"]["precompute"] = {"passed": False, "error": str(exc)}
        logger.error(f"Precompute FAILED: {exc}")
        _write_output(results, output_path)
        return results

    if data_sm is None and data_sf is None and data_cou is None:
        results["checks"]["precompute"] = {
            "passed": False,
            "note": "No data objects built — check parquet columns (c_norm, idhh, household_type, etc.)",
        }
        logger.error("No PrecomputedData objects built — smoke test cannot proceed")
        _write_output(results, output_path)
        return results

    groups_built = {
        "singles_male": data_sm.n_groups if data_sm else 0,
        "singles_female": data_sf.n_groups if data_sf else 0,
        "couples": data_cou.n_groups if data_cou else 0,
    }
    logger.info(f"  Groups built: {groups_built}")
    results["checks"]["precompute"] = {"passed": True, "groups": groups_built}

    # ------------------------------------------------------------------
    # Build dummy theta (initial_values from spec)
    # ------------------------------------------------------------------
    theta_dummy = spec.get_initial_vector()
    results["theta_source"] = "initial_values (smoke test — no estimation)"
    logger.info(f"  Dummy theta: initial_values, shape={theta_dummy.shape}")

    # ------------------------------------------------------------------
    # C9: Score interface callable
    # ------------------------------------------------------------------
    try:
        scores_all, cluster_ids_all = compute_scores_joint(
            theta_dummy, data_sm, data_sf, data_cou, spec
        )
        c9_pass = True
        results["checks"]["C9_score_interface_callable"] = {
            "passed": True,
            "scores_shape": list(scores_all.shape),
            "cluster_ids_shape": list(cluster_ids_all.shape),
        }
        logger.info(f"[C9] Score interface callable: PASS  shape={scores_all.shape}")
    except Exception as exc:
        results["checks"]["C9_score_interface_callable"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C9] Score interface FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # C10: Score matrix shape == (n_groups_total, 55)
    # ------------------------------------------------------------------
    n_groups_total = sum(groups_built.values())
    c10_shape_ok = (scores_all.shape == (n_groups_total, n_params))
    results["checks"]["C10_score_matrix_shape"] = {
        "passed": c10_shape_ok,
        "actual_shape": list(scores_all.shape),
        "expected_shape": [n_groups_total, n_params],
    }
    logger.info(f"[C10] Score matrix shape {scores_all.shape} == ({n_groups_total},{n_params}): {'PASS' if c10_shape_ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # C11: Cluster ids aligned
    # ------------------------------------------------------------------
    c11_pass = (len(cluster_ids_all) == scores_all.shape[0])
    results["checks"]["C11_cluster_ids_aligned"] = {
        "passed": c11_pass,
        "n_cluster_ids": len(cluster_ids_all),
        "n_score_rows": scores_all.shape[0],
    }
    logger.info(f"[C11] Cluster ids aligned: {'PASS' if c11_pass else 'FAIL'}")

    # ------------------------------------------------------------------
    # C12 / T1: Sign check  scores.sum(axis=0) == -grad_joint
    # ------------------------------------------------------------------
    try:
        neg_grad = compute_gradient_joint(theta_dummy, data_sm, data_sf, data_cou, spec)
        t1 = run_t1_sign_check(scores_all, neg_grad, atol=1e-6)
        results["checks"]["C12_T1_sign_check"] = t1
        logger.info(f"[C12/T1] Sign check: {'PASS' if t1['passed'] else 'FAIL'}  max_diff={t1['max_abs_diff']:.2e}")
    except Exception as exc:
        results["checks"]["C12_T1_sign_check"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C12/T1] FAILED: {exc}")

    # ------------------------------------------------------------------
    # C13 / T2: Meat matrix symmetry
    # ------------------------------------------------------------------
    try:
        free_mask = np.ones(n_params, dtype=bool)
        B, n_clusters_found = assemble_meat_matrix(scores_all, cluster_ids_all)
        t2 = run_t2_symmetry_check(B)
        results["checks"]["C13_T2_meat_symmetry"] = {
            **t2, "n_clusters_found": n_clusters_found,
            "B_shape": list(B.shape),
        }
        logger.info(f"[C13/T2] Meat symmetry: {'PASS' if t2['passed'] else 'FAIL'}  max_diff={t2['max_abs_diff']:.2e}")
    except Exception as exc:
        results["checks"]["C13_T2_meat_symmetry"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C13/T2] FAILED: {exc}")

    # ------------------------------------------------------------------
    # C14: Sandwich covariance interface callable (dummy Hessian)
    # ------------------------------------------------------------------
    try:
        H_dummy = np.eye(n_params) * 0.1  # well-conditioned dummy bread
        se_robust, varcov_robust, _ = compute_cluster_robust_se(
            hessian=H_dummy,
            scores_all=scores_all,
            cluster_ids_all=cluster_ids_all,
            free_mask=free_mask,
        )
        c14_pass = True
        results["checks"]["C14_sandwich_callable"] = {
            "passed": True,
            "se_finite": bool(np.all(np.isfinite(se_robust))),
            "varcov_shape": list(varcov_robust.shape),
        }
        logger.info(f"[C14] Sandwich interface callable: PASS  SE finite={np.all(np.isfinite(se_robust))}")
    except Exception as exc:
        results["checks"]["C14_sandwich_callable"] = {"passed": False, "error": str(exc)}
        logger.error(f"[C14] FAILED: {exc}")
        se_robust = None

    # ------------------------------------------------------------------
    # C15: Robust SE finite
    # ------------------------------------------------------------------
    if se_robust is not None:
        n_finite = int(np.sum(np.isfinite(se_robust)))
        c15_pass = (n_finite == n_params)
        results["checks"]["C15_robust_se_finite"] = {
            "passed": c15_pass,
            "n_finite": n_finite,
            "n_params": n_params,
            "note": "dummy Hessian H=0.1*I used; actual SEs will differ post-estimation",
        }
        logger.info(f"[C15] Robust SE finite: {n_finite}/{n_params}: {'PASS' if c15_pass else 'FAIL'}")
    else:
        results["checks"]["C15_robust_se_finite"] = {"passed": False, "note": "sandwich not callable"}

    # ------------------------------------------------------------------
    # C16: No pooled estimation run
    # ------------------------------------------------------------------
    results["checks"]["C16_no_estimation_run"] = {
        "passed": True,
        "note": "Smoke test only. No solver invoked.",
    }
    logger.info("[C16] No pooled estimation run: PASS")

    # ------------------------------------------------------------------
    # C17: No welfare computation
    # ------------------------------------------------------------------
    results["checks"]["C17_no_welfare_run"] = {
        "passed": True,
        "note": "Welfare not authorized. Not computed.",
    }
    logger.info("[C17] No welfare computation: PASS")

    # ------------------------------------------------------------------
    # GA17 final status
    # ------------------------------------------------------------------
    required_checks = ["C9_score_interface_callable", "C12_T1_sign_check",
                       "C13_T2_meat_symmetry", "C14_sandwich_callable", "C15_robust_se_finite"]
    all_required = all(results["checks"].get(k, {}).get("passed", False) for k in required_checks)
    ga17_label = "smoke-test callability: CONFIRMED" if all_required else "PENDING"
    results["GA17_status"] = "CONFIRMED" if all_required else "PENDING"
    results["final_statements"] = {
        "GA17": ga17_label,
        "T4_T5_note": (
            "T4 (SE positivity) and T5 (robust vs Hessian comparison) are post-estimation checks "
            "requiring converged theta and the true Hessian. They are not part of the smoke-test clearance."
        ),
        "pooled_estimation": "NOT authorized",
        "welfare_computation": "NOT authorized",
        "active_baseline": "M1-clean 2016",
        "next_gate": (
            "GA17 clearance addendum; if cleared, pooled-estimation execution authorization memo"
        ),
    }
    logger.info(f"\nGA17 status: {results['GA17_status']}")
    if all_required:
        logger.info("All required smoke-test checks passed. GA17 infrastructure smoke-test callability: CONFIRMED.")
        logger.info("Note: T4/T5 robust-SE diagnostics using converged theta and true Hessian remain post-estimation checks.")
    else:
        failed = [k for k in required_checks if not results["checks"].get(k, {}).get("passed", False)]
        logger.warning(f"GA17 PENDING. Failed checks: {failed}")

    _write_output(results, output_path)
    return results


def _build_minimal_metadata(df_singles: pd.DataFrame, df_couples: pd.DataFrame) -> dict:
    """Build minimal metadata dict from data if no metadata JSON is available."""
    metadata = {"normalization": {}, "n_draws": 100}

    # Singles normalization
    if len(df_singles) > 0 and "c_norm" in df_singles.columns:
        c_mean = float(df_singles["c_norm"].mean())
        metadata["normalization"]["singles"] = {
            "c_scale": c_mean if c_mean > 0 else 1.0,
            "l_scale": 1.0,
        }
    else:
        metadata["normalization"]["singles"] = {"c_scale": 1.0, "l_scale": 1.0}

    # Couples normalization
    if len(df_couples) > 0 and "c_norm" in df_couples.columns:
        c_mean_c = float(df_couples["c_norm"].mean())
        metadata["normalization"]["couples"] = {
            "c_scale": c_mean_c if c_mean_c > 0 else 1.0,
            "l_male_scale": 1.0,
            "l_female_scale": 1.0,
        }
    else:
        metadata["normalization"]["couples"] = {
            "c_scale": 1.0, "l_male_scale": 1.0, "l_female_scale": 1.0,
        }

    return metadata


def _collect_extra_vars(spec) -> list:
    """Collect extra variable names required by the spec's market/hours shifters."""
    extra = []
    for s in getattr(spec, "market_opportunity_shifters", getattr(spec, "market_shifters", [])):
        var = s.get("variable", "")
        if var and var not in extra:
            extra.append(var)
    for s in getattr(spec, "hours_shifters", []):
        var = s.get("variable", "")
        if var and var not in extra:
            extra.append(var)
    for s in getattr(spec, "occupation_shifters", []):
        var = s.get("variable", "")
        if var and var not in extra:
            extra.append(var)
    return extra


def _write_output(results: dict, output_path: Path) -> None:
    """Write results to JSON or Markdown depending on extension."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix == ".json":
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results written to: {output_path}")
    else:
        # Write as Markdown
        _write_md_report(results, output_path)


def _write_md_report(results: dict, output_path: Path) -> None:
    """Write a Markdown validation report."""
    checks = results.get("checks", {})
    ga17 = results.get("GA17_status", "UNKNOWN")

    def _status(k: str) -> str:
        r = checks.get(k, {})
        return "PASS" if r.get("passed", False) else ("FAIL" if "passed" in r else "N/A")

    lines = [
        "# RURO Cluster-Robust SE Static Validation",
        "",
        f"*Generated: {results.get('run_timestamp', 'unknown')} | Mode: {results.get('mode', 'unknown')}*",
        "",
        "---",
        "",
        "## Validation checks",
        "",
        f"| # | Check | Status | Notes |",
        f"|---|-------|--------|-------|",
    ]

    check_rows = [
        ("C1",  "Module imports",                        "C1_module_imports"),
        ("C2",  "CLI --help works",                      "C2_cli_help_works"),
        ("C3",  "P3a pooled YAML parses",                "C3_spec_parses"),
        ("C4",  "Free-parameter vector length = 55",     "C4_free_param_length"),
        ("C5",  "Pooled parquet schema readable",        "C5_schema_readable"),
        ("C6",  "cluster_id column exists",              "C6_cluster_id_exists"),
        ("C7",  "cluster_id == idorighh (bounded)",      "C7_cluster_id_eq_idorighh"),
        ("C8",  "9,657 clusters documented",             "C8_cluster_count_documented"),
        ("C9",  "Score interface callable (smoke-test)", "C9_score_interface_callable"),
        ("C10", "Score matrix shape correct",            "C10_score_matrix_shape"),
        ("C11", "Cluster ids aligned to score rows",     "C11_cluster_ids_aligned"),
        ("C12/T1", "Sign check: sum(scores)==-grad",     "C12_T1_sign_check"),
        ("C13/T2", "Meat matrix B symmetric",            "C13_T2_meat_symmetry"),
        ("C14", "Sandwich covariance callable",          "C14_sandwich_callable"),
        ("C15", "Robust SE output finite",               "C15_robust_se_finite"),
        ("C16", "No pooled estimation run",              "C16_no_estimation_run"),
        ("C17", "No welfare computation run",            "C17_no_welfare_run"),
    ]

    for num, label, key in check_rows:
        status = _status(key)
        r = checks.get(key, {})
        note = r.get("note", r.get("error", ""))
        if "n_params" in r and "expected" in r:
            note = f"n={r['n_params']}, expected={r['expected']}"
        elif "n_clusters_found" in r:
            note = f"{r['n_clusters_found']} clusters in smoke sample"
        elif "max_abs_diff" in r:
            note = f"max_diff={r['max_abs_diff']:.2e}"
        lines.append(f"| {num} | {label} | **{status}** | {note} |")

    fs = results.get("final_statements", {})
    ga17_display = fs.get("GA17", ga17)
    lines += [
        "",
        "---",
        "",
        f"## GA17 final status: **{ga17_display}**",
        "",
        "| Item | Status |",
        "|------|--------|",
    ]
    lines.append(f"| GA17 | **{ga17_display}** |")
    t45 = fs.get("T4_T5_note", "")
    if t45:
        lines.append(f"| T4/T5 note | {t45} |")
    lines.append(f"| Pooled estimation | {fs.get('pooled_estimation', 'NOT authorized')} |")
    lines.append(f"| Welfare computation | {fs.get('welfare_computation', 'NOT authorized')} |")
    lines.append(f"| Active JMP baseline | {fs.get('active_baseline', 'M1-clean 2016')} |")
    lines.append(f"| Next gate | {fs.get('next_gate', '')} |")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Markdown report written to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Post-estimation mode
# ---------------------------------------------------------------------------

def _load_theta_from_results_json(results_json: Path, start_label: Optional[str]) -> np.ndarray:
    """
    Load the converged theta vector from an estimation_results.json.

    The JSON produced by enh_RURO_estimate_FR.py stores parameters under
    results.<group>.parameters  (e.g. results.singles_male.parameters or
    results.joint.parameters).  We prefer the joint key; fall back to the
    first available results key.

    start_label: if provided (e.g. "start_1"), look in that sub-key first.
    """
    with open(results_json, "r") as f:
        data = json.load(f)

    # Navigate to the parameter list
    results_block = data.get("results", data)  # some JSONs are flat

    def _extract_theta(block) -> Optional[list]:
        """Return a flat list of floats from various result block formats."""
        if not isinstance(block, dict):
            return None
        # Prefer 'theta' (raw float list) over 'parameters' (may be a dict)
        for key in ["theta", "parameter_values"]:
            val = block.get(key)
            if isinstance(val, (list, tuple)) and len(val) > 0:
                try:
                    return [float(v) for v in val]
                except (TypeError, ValueError):
                    pass
        # 'parameters' may be a dict {name: value} or a list
        val = block.get("parameters")
        if isinstance(val, dict) and len(val) > 0:
            try:
                return [float(v) for v in val.values()]
            except (TypeError, ValueError):
                pass
        if isinstance(val, (list, tuple)) and len(val) > 0:
            try:
                return [float(v) for v in val]
            except (TypeError, ValueError):
                pass
        return None

    theta_list = None

    # Try start_label first
    if start_label and start_label in results_block:
        theta_list = _extract_theta(results_block[start_label])

    # Try common group keys
    if theta_list is None:
        for key in ["joint", "singles_male", "singles_female", "singles", "couples"]:
            if key in results_block:
                theta_list = _extract_theta(results_block[key])
                if theta_list:
                    logger.info(f"  Loaded theta from results.{key} ({len(theta_list)} values)")
                    break

    # Last resort: top-level theta / parameter_values
    if theta_list is None:
        theta_list = _extract_theta(data)

    if theta_list is None or len(theta_list) == 0:
        raise ValueError(
            f"Could not find non-empty parameter vector in {results_json}. "
            "Expected at results.<group>.theta or results.<group>.parameters."
        )

    return np.array(theta_list, dtype=float)


def run_post_estimation(
    spec_path: Path,
    mnl_base: Path,
    results_json: Path,
    output_path: Path,
    cluster_col: str = "idorighh",
    start_label: Optional[str] = None,
) -> dict:
    """
    Post-estimation cluster-robust SE computation.

    Requires a converged theta from results_json.
    Loads the full split-stem estimation-ready data (no row bound).
    Computes the TRUE Hessian via central differences at the converged theta.
    Assembles the sandwich covariance and runs T3/T4/T5.

    Parameters
    ----------
    spec_path : Path
        YAML specification.
    mnl_base : Path
        Split-stem base path (stem without __singles.parquet / __couples.parquet).
        E.g. Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready
    results_json : Path
        Converged estimation_results.json.
    output_path : Path
        Output path for the results JSON.
    cluster_col : str
        Cluster column name (default: idorighh).
    start_label : str, optional
        Which start to load from results_json (e.g. "start_1").
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = {
        "run_timestamp": ts,
        "mode": "post-estimation",
        "spec": str(spec_path),
        "mnl_base": str(mnl_base),
        "results_json": str(results_json),
        "cluster_col": cluster_col,
        "checks": {},
    }

    # ------------------------------------------------------------------
    # PE1: Parse spec
    # ------------------------------------------------------------------
    try:
        spec = parse_specification(spec_path)
        n_params = len(spec.all_param_names)
        results["checks"]["PE1_spec_parses"] = {"passed": True, "n_params": n_params}
        logger.info(f"[PE1] Spec parses: PASS  (n_params={n_params})")
    except Exception as exc:
        results["checks"]["PE1_spec_parses"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE1] Spec parse FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # PE2: Load converged theta
    # ------------------------------------------------------------------
    try:
        theta = _load_theta_from_results_json(results_json, start_label)
        if len(theta) != n_params:
            raise ValueError(f"Theta length {len(theta)} != n_params {n_params}")
        results["checks"]["PE2_theta_loaded"] = {
            "passed": True, "n_params": len(theta),
            "theta_norm": float(np.linalg.norm(theta)),
        }
        logger.info(f"[PE2] Converged theta loaded: {len(theta)} params, ||theta||={np.linalg.norm(theta):.4f}")
    except Exception as exc:
        results["checks"]["PE2_theta_loaded"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE2] Theta load FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # PE3: Load full split-stem data (no row bound)
    # ------------------------------------------------------------------
    singles_path = Path(str(mnl_base) + "__singles.parquet")
    couples_path = Path(str(mnl_base) + "__couples.parquet")
    meta_path    = Path(str(mnl_base) + "__mnlmeta.json")

    try:
        from estimation_utils import load_and_validate_mnl_data
        df_singles, df_couples, metadata = load_and_validate_mnl_data(
            singles_path=singles_path,
            couples_path=couples_path if couples_path.exists() else None,
            metadata_path=meta_path,
            strict_validation=True,
        )
        logger.info(f"[PE3] Data loaded: singles={len(df_singles):,} rows, couples={len(df_couples) if df_couples is not None else 0:,} rows")
        results["checks"]["PE3_data_loaded"] = {
            "passed": True,
            "n_singles": len(df_singles),
            "n_couples": len(df_couples) if df_couples is not None else 0,
        }
    except Exception as exc:
        results["checks"]["PE3_data_loaded"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE3] Data load FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # PE4: Build precomputed data objects
    # ------------------------------------------------------------------
    include_wage = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc  = (spec.wage_spec == "loc_empirical")
    extra_vars   = _collect_extra_vars(spec)

    gender_col = "dgn" if "dgn" in df_singles.columns else None
    if gender_col:
        df_sm = df_singles[df_singles[gender_col] == 1].copy()
        df_sf = df_singles[df_singles[gender_col] == 0].copy()
    else:
        df_sm = df_singles.copy()
        df_sf = pd.DataFrame()

    # Ensure sorted by idhh
    if "idhh" in df_sm.columns and not df_sm["idhh"].is_monotonic_increasing:
        df_sm = df_sm.sort_values("idhh").reset_index(drop=True)
    if len(df_sf) > 0 and "idhh" in df_sf.columns and not df_sf["idhh"].is_monotonic_increasing:
        df_sf = df_sf.sort_values("idhh").reset_index(drop=True)
    df_c = df_couples if df_couples is not None else pd.DataFrame()
    if len(df_c) > 0 and "idhh" in df_c.columns and not df_c["idhh"].is_monotonic_increasing:
        df_c = df_c.sort_values("idhh").reset_index(drop=True)

    try:
        data_sm = data_sf = data_cou = None
        if len(df_sm) > 0:
            data_sm = precompute_data_singles(
                df=df_sm, metadata=metadata, is_male=True,
                include_wage_vars=include_wage, include_loc_vars=include_loc,
                include_extra_vars=extra_vars,
            )
        if len(df_sf) > 0:
            data_sf = precompute_data_singles(
                df=df_sf, metadata=metadata, is_male=False,
                include_wage_vars=include_wage, include_loc_vars=include_loc,
                include_extra_vars=extra_vars,
            )
        if len(df_c) > 0:
            data_cou = precompute_data_couples(
                df=df_c, metadata=metadata,
                include_wage_vars=include_wage, include_loc_vars=include_loc,
                include_extra_vars=extra_vars,
            )
        groups_built = {
            "singles_male":   data_sm.n_groups  if data_sm  else 0,
            "singles_female": data_sf.n_groups  if data_sf  else 0,
            "couples":        data_cou.n_groups if data_cou else 0,
        }
        results["checks"]["PE4_precompute"] = {"passed": True, "groups": groups_built}
        logger.info(f"[PE4] Precompute: {groups_built}")
    except Exception as exc:
        results["checks"]["PE4_precompute"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE4] Precompute FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # PE5: Extract per-choice-set scores (compute_scores_joint)
    # ------------------------------------------------------------------
    try:
        scores_all, cluster_ids_all = compute_scores_joint(
            theta, data_sm, data_sf, data_cou, spec
        )
        results["checks"]["PE5_scores_extracted"] = {
            "passed": True,
            "scores_shape": list(scores_all.shape),
            "n_cluster_ids": int(len(cluster_ids_all)),
        }
        logger.info(f"[PE5] Scores extracted: shape={scores_all.shape}")
    except Exception as exc:
        results["checks"]["PE5_scores_extracted"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE5] Score extraction FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # T3: Full cluster count (9,657 unique idorighh on full dataset)
    # ------------------------------------------------------------------
    t3 = run_t3_cluster_count_check(cluster_ids_all, expected=9657)
    results["checks"]["T3_cluster_count"] = t3
    logger.info(f"[T3] Cluster count {t3['n_unique_clusters']} (expected 9,657): {'PASS' if t3['passed'] else 'FAIL'}")

    # ------------------------------------------------------------------
    # PE6: Compute TRUE Hessian via central differences at converged theta
    # ------------------------------------------------------------------
    # The true Hessian is the numerical Hessian of the negative LL at theta.
    # We use the same central-differences method as compute_standard_errors in
    # enh_RURO_estimate_FR.py, applied directly here so we control free_mask
    # alignment with the sandwich assembly.
    logger.info("[PE6] Computing TRUE Hessian (central differences on compute_gradient_joint)...")
    logger.info("  This is NOT the dummy Hessian H=0.1*I used in smoke-test.")

    try:
        # Determine free parameters (at bounds -> fixed)
        bounds = spec.get_bounds_tuple() if hasattr(spec, "get_bounds_tuple") else None
        bound_tol = 1e-6

        free_mask = np.ones(n_params, dtype=bool)
        if bounds is not None and len(bounds) == n_params:
            for i, (lb, ub) in enumerate(bounds):
                if lb is None and ub is None:
                    continue
                if lb is not None and ub is not None and (ub - lb) <= 1e-6:
                    free_mask[i] = False
                    continue
                if lb is not None and abs(theta[i] - lb) <= bound_tol:
                    free_mask[i] = False
                elif ub is not None and abs(theta[i] - ub) <= bound_tol:
                    free_mask[i] = False

        free_idx = np.where(free_mask)[0]
        n_free   = int(free_mask.sum())
        logger.info(f"  Free parameters: {n_free}/{n_params}")

        # Build gradient function closure
        def grad_func(t):
            return compute_gradient_joint(t, data_sm, data_sf, data_cou, spec)

        eps = 1e-5
        H_free = np.zeros((n_free, n_free))
        for col_idx, i in enumerate(free_idx):
            theta_plus  = theta.copy(); theta_plus[i]  += eps
            theta_minus = theta.copy(); theta_minus[i] -= eps
            g_plus  = grad_func(theta_plus)
            g_minus = grad_func(theta_minus)
            H_free[:, col_idx] = (g_plus[free_idx] - g_minus[free_idx]) / (2 * eps)
            if (col_idx + 1) % 10 == 0:
                logger.info(f"  Hessian column {col_idx+1}/{n_free} done")

        H_free = 0.5 * (H_free + H_free.T)  # symmetrize

        # Also compute Hessian-based SEs for T5 comparison
        try:
            H_free_inv = np.linalg.pinv(H_free, rcond=1e-10)
            se_hessian_free = np.sqrt(np.abs(np.diag(H_free_inv)))
        except Exception:
            se_hessian_free = np.full(n_free, np.nan)

        se_hessian = np.full(n_params, np.nan)
        se_hessian[free_idx] = se_hessian_free

        # Embed n_free × n_free Hessian into full n_params × n_params matrix
        # for compute_cluster_robust_se (which indexes by free_mask)
        H_full = np.zeros((n_params, n_params))
        H_full[np.ix_(free_idx, free_idx)] = H_free

        cond_number = float(np.linalg.cond(H_free)) if n_free > 0 else np.inf
        results["checks"]["PE6_true_hessian"] = {
            "passed": True,
            "hessian_shape_free": [n_free, n_free],
            "condition_number": cond_number,
            "note": "TRUE Hessian (central differences on compute_gradient_joint at converged theta). NOT dummy Hessian.",
        }
        logger.info(f"[PE6] True Hessian computed: shape=({n_free},{n_free}), cond={cond_number:.2e}")
    except Exception as exc:
        results["checks"]["PE6_true_hessian"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE6] True Hessian FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # PE7: Cluster-robust sandwich VCV
    # ------------------------------------------------------------------
    try:
        se_robust, varcov_robust, _ = compute_cluster_robust_se(
            hessian=H_full,
            scores_all=scores_all,
            cluster_ids_all=cluster_ids_all,
            free_mask=free_mask,
        )
        results["checks"]["PE7_sandwich"] = {
            "passed": True,
            "varcov_shape": list(varcov_robust.shape),
            "n_finite_se": int(np.sum(np.isfinite(se_robust))),
        }
        logger.info(f"[PE7] Sandwich VCV assembled: {np.sum(np.isfinite(se_robust))}/{n_params} finite SEs")
    except Exception as exc:
        results["checks"]["PE7_sandwich"] = {"passed": False, "error": str(exc)}
        logger.error(f"[PE7] Sandwich FAILED: {exc}")
        _write_output(results, output_path)
        return results

    # ------------------------------------------------------------------
    # T4: Robust SE positivity for free parameters
    # ------------------------------------------------------------------
    t4 = run_t4_se_positivity_check(se_robust, free_mask)
    results["checks"]["T4_se_positivity"] = t4
    logger.info(f"[T4] SE positivity ({t4['n_free']} free params): {'PASS' if t4['passed'] else 'FAIL'} "
                f"({t4['n_nonpositive']} non-positive)")

    # ------------------------------------------------------------------
    # T5: Robust vs Hessian SE comparison
    # ------------------------------------------------------------------
    t5 = run_t5_vs_hessian_check(
        se_robust=se_robust,
        se_hessian=se_hessian,
        param_names=spec.all_param_names,
        free_mask=free_mask,
    )
    results["checks"]["T5_robust_vs_hessian"] = t5
    logger.info(f"[T5] Robust vs Hessian: {t5['n_below']} params where robust < hessian SE")

    # ------------------------------------------------------------------
    # PE8: Save VCV matrix
    # ------------------------------------------------------------------
    vcv_path = output_path.parent / (output_path.stem + "_vcv.npy")
    try:
        np.save(str(vcv_path), varcov_robust)
        results["vcv_output_path"] = str(vcv_path)
        results["checks"]["PE8_vcv_saved"] = {"passed": True, "path": str(vcv_path)}
        logger.info(f"[PE8] VCV matrix saved: {vcv_path}")
    except Exception as exc:
        results["checks"]["PE8_vcv_saved"] = {"passed": False, "error": str(exc)}
        logger.warning(f"[PE8] VCV save failed: {exc}")

    # ------------------------------------------------------------------
    # PE9: No welfare, no SA2, M1-clean active
    # ------------------------------------------------------------------
    results["checks"]["PE9_no_welfare"] = {"passed": True, "note": "No welfare computed (not authorized)."}
    results["checks"]["PE9_m1clean_active"] = {"passed": True, "note": "M1-clean 2016 remains active JMP baseline."}

    # ------------------------------------------------------------------
    # Collect cluster-robust SE artifacts
    # ------------------------------------------------------------------
    results["cluster_robust_se_artifacts"] = {
        "converged_theta": theta.tolist(),
        "hessian_source": "TRUE Hessian — numerical Hessian of negative LL (central differences on compute_gradient_joint at converged theta). NOT the dummy Hessian H=0.1*I.",
        "cluster_count_T3": t3,
        "se_robust_vector": se_robust.tolist(),
        "se_hessian_vector": se_hessian.tolist(),
        "vcv_path": str(vcv_path) if "vcv_output_path" in results else None,
        "T4_se_positivity": t4,
        "T5_robust_vs_hessian": {**t5, "n_robust_below_hessian": t5["n_below"]},
        "no_welfare": "CONFIRMED",
        "m1clean_active": "CONFIRMED — M1-clean 2016 remains the active JMP baseline",
        "free_mask": free_mask.tolist(),
        "n_free": n_free,
        "n_params": n_params,
    }

    _write_output(results, output_path)
    logger.info(f"\nPost-estimation cluster-robust SE results written to: {output_path}")
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cluster-robust SE smoke-test and post-estimation CLI (GA17 clearance)"
    )
    p.add_argument("--spec", "--spec-config", dest="spec", type=Path, required=True,
                   help="Path to YAML specification (e.g. estimation_spec_ruro_occ_P3a_pooled.yaml). "
                        "Alias: --spec-config")
    p.add_argument("--parquet", type=Path, default=None,
                   help="[smoke-test] Path to pooled parquet (fr_p3a_gsurv2_harmonised.parquet). "
                        "Required for --mode smoke-test.")
    p.add_argument("--mnl-base", dest="mnl_base", type=Path, default=None,
                   help="[post-estimation] Split-stem base path "
                        "(e.g. Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready). "
                        "Suffixes __singles.parquet / __couples.parquet / __mnlmeta.json are appended.")
    p.add_argument("--output", type=Path, default=Path("Results/RURO_cluster_robust_SE_static_validation_v1.md"),
                   help="Output path (.md for smoke-test; .json for post-estimation). "
                        "Default: Results/RURO_cluster_robust_SE_static_validation_v1.md")
    p.add_argument("--mode", choices=["smoke-test", "post-estimation"], default="smoke-test",
                   help="'smoke-test': GA17 clearance at initial_values (default). "
                        "'post-estimation': compute true-Hessian cluster-robust SEs using converged theta.")
    p.add_argument("--results-json", type=Path, default=None,
                   help="[post-estimation only] Path to estimation_results.json with converged theta.")
    p.add_argument("--cluster-col", dest="cluster_col", type=str, default="idorighh",
                   help="[post-estimation] Cluster column name. Default: idorighh")
    p.add_argument("--start-label", dest="start_label", type=str, default=None,
                   help="[post-estimation] Which start to load from results JSON (e.g. start_1). "
                        "Default: auto-detect from joint / singles_male / singles_female / couples.")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("RURO Cluster-Robust SE — GA17 Infrastructure")
    logger.info(f"Mode: {args.mode}")
    logger.info("=" * 70)

    if not args.spec.exists():
        logger.error(f"Spec not found: {args.spec}")
        return 1

    if args.mode == "smoke-test":
        if args.parquet is None:
            logger.error("--parquet is required for --mode smoke-test")
            return 1
        if not args.parquet.exists():
            logger.error(f"Parquet not found: {args.parquet}")
            return 1
        results = run_smoke_test(
            spec_path=args.spec,
            parquet_path=args.parquet,
            output_path=args.output,
        )
        ga17 = results.get("GA17_status", "PENDING")
        logger.info(f"\nFinal GA17 status: {ga17}")
        return 0 if ga17 == "CONFIRMED" else 1

    elif args.mode == "post-estimation":
        if args.results_json is None or not args.results_json.exists():
            logger.error("--results-json required and must exist for --mode post-estimation")
            return 1

        # Determine data source: prefer --mnl-base, fall back to --parquet stem
        if args.mnl_base is not None:
            mnl_base = args.mnl_base
        elif args.parquet is not None:
            # Allow --parquet to act as the mnl_base stem (drop trailing suffixes if present)
            stem = str(args.parquet)
            for suf in ["__singles.parquet", "__couples.parquet", ".parquet"]:
                if stem.endswith(suf):
                    stem = stem[: -len(suf)]
                    break
            mnl_base = Path(stem)
            logger.info(f"  --mnl-base derived from --parquet stem: {mnl_base}")
        else:
            logger.error("Either --mnl-base or --parquet must be provided for --mode post-estimation")
            return 1

        results = run_post_estimation(
            spec_path=args.spec,
            mnl_base=mnl_base,
            results_json=args.results_json,
            output_path=args.output,
            cluster_col=args.cluster_col,
            start_label=args.start_label,
        )
        all_pass = all(
            v.get("passed", False)
            for v in results.get("checks", {}).values()
            if isinstance(v, dict) and "passed" in v
        )
        return 0 if all_pass else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())