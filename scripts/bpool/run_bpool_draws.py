"""
B-pool draw orchestration driver.

Runs both singles (100 draws) and couples (30×30=900 product) in sequence,
writes output parquets + sidecar metadata, then runs invariant checks.

Usage:
    python scripts/bpool/run_bpool_draws.py [--seed 2026] [--singles-only] [--couples-only]

Output files (written to U:/EUROMOD-STORAGE/new_data/):
    fr_p3a_bpool_d1w1__singles.parquet
    fr_p3a_bpool_d1w1__singles__bpoolmeta.json
    fr_p3a_bpool_d1w1__couples.parquet
    fr_p3a_bpool_d1w1__couples__bpoolmeta.json
    fr_p3a_bpool_d1w1__run_summary.json

Also mirrored to Z:/hisham/EUROMOD-STORAGE/new_data/ after the first run.

Invariant checks run after each build:
    V1 — Row count: HH × (N_DRAWS+1) for singles; HH × (N_JOINT+1) for couples
    V2 — log_prior = log_q_E + working*(log_q_Occ+log_q_H+log_q_W) for simulated rows
    V3 — log_q columns = 0 on chosen rows (draw==0 / draw_joint==0)
    V4 — gsur values match source (GSURv2 provenance)
    V5 — No loc4 outside {-1,1,2,3,4} on simulated working rows (couples: {-2 allowed on obs})
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "bpool"))
sys.path.insert(0, str(_SCRIPTS / "pilot"))

from build_bpool_singles import (  # noqa: E402
    N_DRAWS as S_N_DRAWS,
    _DATA_DIR,
    _MINCER_JSON,
    _OUT_DIR,
    _OUT_STEM as S_OUT_STEM,
    _SOURCE_STEM as S_SOURCE_STEM,
    _load_mincer,
    build_singles,
    write_metadata as write_singles_meta,
)
from build_bpool_couples import (  # noqa: E402
    N_JOINT,
    _OUT_STEM as C_OUT_STEM,
    _SOURCE_STEM as C_SOURCE_STEM,
    build_couples,
    write_metadata as write_couples_meta,
)


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------

def _check_singles(df: pd.DataFrame, source_df: pd.DataFrame) -> dict:
    results: dict[str, object] = {}

    # V1 — row count (stacked_hh_uid is the unique estimation unit in P3a)
    n_hh = df[df["draw"] == 0]["stacked_hh_uid"].nunique()
    expected = n_hh * (S_N_DRAWS + 1)
    results["V1_row_count"] = {
        "expected": expected,
        "actual": len(df),
        "pass": len(df) == expected,
        "n_stacked_hh": n_hh,
    }

    # V2 — log_prior formula on simulated rows
    sim = df[df["draw"] > 0].copy()
    expected_lp = (
        sim["log_q_E"]
        + sim["working"] * (sim["log_q_Occ"] + sim["log_q_H"] + sim["log_q_W"])
    )
    residual = (sim["log_prior"] - expected_lp).abs()
    results["V2_log_prior_formula"] = {
        "max_residual": float(residual.max()),
        "pass": bool(residual.max() < 1e-9),
    }

    # V3 — log_q = 0 on chosen rows
    chosen = df[df["draw"] == 0]
    lq_cols = ["log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "log_prior"]
    max_lq_chosen = max(chosen[c].abs().max() for c in lq_cols)
    results["V3_chosen_log_q_zero"] = {
        "max_abs": float(max_lq_chosen),
        "pass": bool(max_lq_chosen < 1e-9),
    }

    # V4 — gsur matches source; join on stacked_hh_uid (idhh is NOT unique in P3a)
    src_obs = source_df[source_df["draw"] == 0][["stacked_hh_uid", "gsur"]].rename(columns={"gsur": "gsur_src"})
    out_obs = df[df["draw"] == 0][["stacked_hh_uid", "gsur"]]
    merged = out_obs.merge(src_obs, on="stacked_hh_uid", how="left")
    gsur_diff = (merged["gsur"] - merged["gsur_src"]).abs().max()
    results["V4_gsur_provenance"] = {
        "max_gsur_diff": float(gsur_diff),
        "pass": bool(gsur_diff < 1e-9),
        "note": "gsur values inherited from GSURv2 P3a source parquet",
    }

    # V5 — loc4 valid on simulated working rows
    work_sim = sim[sim["working"] == 1]
    invalid_loc4 = work_sim[~work_sim["loc4"].isin([1, 2, 3, 4])]["loc4"].value_counts()
    results["V5_loc4_valid"] = {
        "n_invalid": int(invalid_loc4.sum()),
        "invalid_values": invalid_loc4.to_dict(),
        "pass": int(invalid_loc4.sum()) == 0,
    }

    return results


def _check_couples(df: pd.DataFrame, source_df: pd.DataFrame) -> dict:
    results: dict[str, object] = {}

    # V1 — row count (couples use is_chosen_joint to identify chosen row)
    n_hh = int(df["is_chosen_joint"].sum())
    expected = n_hh * (N_JOINT + 1)
    results["V1_row_count"] = {
        "expected": expected,
        "actual": len(df),
        "pass": len(df) == expected,
        "n_hh": n_hh,
        "n_joint_per_hh": N_JOINT,
    }

    # V2 — log_prior formula: joint = male + female; per-partner = log_q_E + working*(...)
    sim = df[df["is_chosen_joint"] == 0].copy()
    lp_m = (
        sim["log_q_E_male"]
        + sim["working_male"] * (sim["log_q_Occ_male"] + sim["log_q_H_male"] + sim["log_q_W_male"])
    )
    lp_f = (
        sim["log_q_E_female"]
        + sim["working_female"] * (sim["log_q_Occ_female"] + sim["log_q_H_female"] + sim["log_q_W_female"])
    )
    expected_joint = lp_m + lp_f
    residual = (sim["log_prior"] - expected_joint).abs()
    results["V2_log_prior_formula"] = {
        "max_residual": float(residual.max()),
        "pass": bool(residual.max() < 1e-9),
    }

    # V3 — log_q = 0 on chosen rows
    chosen = df[df["is_chosen_joint"] == 1]
    lq_cols = [
        "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
        "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
        "log_prior",
    ]
    existing_lq = [c for c in lq_cols if c in chosen.columns]
    max_lq_chosen = max(chosen[c].abs().max() for c in existing_lq)
    results["V3_chosen_log_q_zero"] = {
        "max_abs": float(max_lq_chosen),
        "pass": bool(max_lq_chosen < 1e-9),
    }

    # V4 — gsur_male, gsur_female match source; join on stacked_hh_uid (idhh not unique in P3a)
    src_obs = source_df[source_df["draw"] == 0][["stacked_hh_uid", "gsur_male", "gsur_female"]].rename(
        columns={"gsur_male": "gsur_m_src", "gsur_female": "gsur_f_src"}
    )
    out_obs = df[df["is_chosen_joint"] == 1][["stacked_hh_uid", "gsur_male", "gsur_female"]]
    merged = out_obs.merge(src_obs, on="stacked_hh_uid", how="left")
    diff_m = (merged["gsur_male"] - merged["gsur_m_src"]).abs().max()
    diff_f = (merged["gsur_female"] - merged["gsur_f_src"]).abs().max()
    results["V4_gsur_provenance"] = {
        "max_diff_gsur_male": float(diff_m),
        "max_diff_gsur_female": float(diff_f),
        "pass": bool(max(diff_m, diff_f) < 1e-9),
        "note": "gsur_male/female inherited from GSURv2 P3a source parquet",
    }

    # V5 — loc4_male/female valid on simulated working rows
    work_m = sim[sim["working_male"] == 1]
    work_f = sim[sim["working_female"] == 1]
    inv_m = work_m[~work_m["loc4_male"].isin([1, 2, 3, 4])]["loc4_male"].value_counts()
    inv_f = work_f[~work_f["loc4_female"].isin([1, 2, 3, 4])]["loc4_female"].value_counts()
    results["V5_loc4_valid"] = {
        "n_invalid_male": int(inv_m.sum()),
        "n_invalid_female": int(inv_f.sum()),
        "pass": int(inv_m.sum()) == 0 and int(inv_f.sum()) == 0,
    }

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Run B-pool D1+W1 draw builds")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--singles-only", action="store_true")
    parser.add_argument("--couples-only", action="store_true")
    parser.add_argument("--skip-checks", action="store_true", help="Skip invariant checks")
    args = parser.parse_args()

    run_singles = not args.couples_only
    run_couples = not args.singles_only

    summary: dict[str, object] = {
        "run_start": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "singles": None,
        "couples": None,
    }

    mincer = _load_mincer()

    if run_singles:
        print("=" * 60)
        print("SINGLES BUILD")
        print("=" * 60)
        source_s = _DATA_DIR / f"{S_SOURCE_STEM}.parquet"
        out_s = _OUT_DIR / f"{S_OUT_STEM}.parquet"
        build_singles(source_path=source_s, out_path=out_s, seed=args.seed)

        source_df_s = pd.read_parquet(source_s)
        n_hh_s = source_df_s["idhh"].nunique()
        write_singles_meta(out_s, source_s, n_hh_s, S_N_DRAWS, args.seed, mincer)

        if not args.skip_checks:
            print("\nRunning invariant checks (singles)...")
            out_df_s = pd.read_parquet(out_s)
            checks_s = _check_singles(out_df_s, source_df_s)
            all_pass_s = all(v["pass"] for v in checks_s.values() if isinstance(v, dict) and "pass" in v)
            print(f"  {'PASS' if all_pass_s else 'FAIL'} — singles checks")
            for k, v in checks_s.items():
                status = "PASS" if v.get("pass") else "FAIL"
                print(f"    {status} {k}: {v}")
            summary["singles"] = {"checks": checks_s, "all_pass": all_pass_s}
        else:
            summary["singles"] = {"checks": "skipped"}

    if run_couples:
        print("=" * 60)
        print("COUPLES BUILD (30×30=900 product)")
        print("=" * 60)
        source_c = _DATA_DIR / f"{C_SOURCE_STEM}.parquet"
        out_c = _OUT_DIR / f"{C_OUT_STEM}.parquet"
        build_couples(source_path=source_c, out_path=out_c, seed=args.seed)

        source_df_c = pd.read_parquet(source_c)
        n_hh_c = source_df_c[source_df_c["draw"] == 0]["idhh"].nunique()
        write_couples_meta(out_c, source_c, n_hh_c, args.seed, mincer)

        if not args.skip_checks:
            print("\nRunning invariant checks (couples)...")
            out_df_c = pd.read_parquet(out_c)
            checks_c = _check_couples(out_df_c, source_df_c)
            all_pass_c = all(v["pass"] for v in checks_c.values() if isinstance(v, dict) and "pass" in v)
            print(f"  {'PASS' if all_pass_c else 'FAIL'} — couples checks")
            for k, v in checks_c.items():
                status = "PASS" if v.get("pass") else "FAIL"
                print(f"    {status} {k}: {v}")
            summary["couples"] = {"checks": checks_c, "all_pass": all_pass_c}
        else:
            summary["couples"] = {"checks": "skipped"}

    summary["run_end"] = datetime.now(timezone.utc).isoformat()

    summary_path = _OUT_DIR / "fr_p3a_bpool_d1w1__run_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nRun summary written: {summary_path}")

    # Final verdict
    passes = []
    if run_singles and not args.skip_checks and summary["singles"]:
        passes.append(summary["singles"].get("all_pass", False))
    if run_couples and not args.skip_checks and summary["couples"]:
        passes.append(summary["couples"].get("all_pass", False))
    if passes:
        if all(passes):
            print("\nALL INVARIANT CHECKS PASSED")
        else:
            print("\nSOME INVARIANT CHECKS FAILED — review run summary")
            sys.exit(1)


if __name__ == "__main__":
    main()
