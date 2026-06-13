"""
Fast-Lane F3 — Tasks 1 and 5.

Task 1: All 5,007 singles, V_i^IS on STAGED stem (primary) + CERTIFIED stem (gate + delta).
         Gate-0: certified stem negLL must match pre-registered anchors to <=1e-6.
         Anchor check: UID 200001593700 V_i^IS on staged stem must equal 11.496632024594227 to <=1e-9.
Task 5: All 7,438 couples, V_i^IS on CERTIFIED stem, per-HH parquet.
         Gate-0: certified stem negLL must match pre-registered anchor to <=1e-6.

No EUROMOD, no V_i^dir, no Omega, no measures, no promotion. Read-only at certified theta.
Outputs written to outputs/welfare/fastlane/. Do not commit without separate authorisation.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---- path setup ----
_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "scripts" / "bpool"))
sys.path.insert(0, str(_REPO / "scripts" / "enhanced"))
sys.path.insert(0, str(_REPO / "scripts" / "welfare"))
sys.path.insert(0, str(_REPO / "scripts" / "pilot"))

import jax  # noqa: E402
jax.config.update("jax_enable_x64", True)

import estimation_spec_parser as sp  # noqa: E402
import joint_recovery_test as jrt    # noqa: E402
import welfare_core as wc            # noqa: E402
import yaml                          # noqa: E402
from _bpool_paths import bpool_dir   # noqa: E402

# ---- file paths ----
_CONFIG   = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"
_SPEC     = _REPO / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
_THETA    = _REPO / "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"
_OUT_S    = _REPO / "outputs/welfare/fastlane/singles_Vi_production_v1.parquet"
_OUT_C    = _REPO / "outputs/welfare/fastlane/couples_ViIS_capture_v1.parquet"
_OUT_JSON = _REPO / "outputs/welfare/fastlane/f3_tasks1_5_summary.json"

# ---- pre-registered constants ----
_GATE0_SM  = 28489.042816294535
_GATE0_SF  = 35411.86351549324
_GATE0_COU = 174603.72976561091
_ANCHOR_UID = 200001593700
_ANCHOR_VIS = 11.496632024594227  # V_i^IS for UID 200001593700 on staged stem
_TOL = 1e-6
_ANCHOR_TOL = 1e-9


def _load_cfg() -> tuple[str, str, str]:
    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    w = cfg["welfare"]
    cert   = w["baseline"]["engine_ready_stem"]
    staged = w["stage4"]["welfare_pricing_reference"]["staged_engine_ready_stem"]
    staged_cpl = w["stage4"]["welfare_pricing_reference"].get("staged_couples_stem", staged)
    return cert, staged, staged_cpl


def _load_theta(spec) -> np.ndarray:
    df = pd.read_csv(_THETA)
    lu = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    return np.array([lu.get(n, float(spec.initial_values.get(n, 0.0)))
                     for n in spec.all_param_names], dtype=np.float64)


def _build_bridge_singles(bp: Path, stem: str, group: str) -> dict:
    """group_ids key -> (stacked_hh_uid, year_tag).  Mirrors v_is_and_ess_singles."""
    path = bp / f"{stem}__singles.parquet"
    dgn  = 1.0 if group == "singles_male" else 0.0
    df   = pd.read_parquet(path, columns=["stacked_hh_uid", "idhh", "year_tag", "dgn", "draw"])
    df   = df[(df["dgn"] == dgn) & (df["draw"] == 0)].drop_duplicates("stacked_hh_uid")
    multi = df["year_tag"].nunique() > 1
    key  = (df["idhh"].astype(np.int64) * 10 + df["year_tag"].astype(np.int64)
            if multi else df["idhh"].astype(np.int64))
    df   = df.assign(gkey=key.values)
    return {int(k): (int(uid), int(yt))
            for k, uid, yt in zip(df["gkey"], df["stacked_hh_uid"], df["year_tag"])}


def _build_bridge_couples(bp: Path, stem: str) -> dict:
    """group_ids key -> (stacked_hh_uid, year_tag) for couples."""
    path = bp / f"{stem}__couples.parquet"
    cols = ["stacked_hh_uid", "idhh", "year_tag"]
    try:
        tmp = pd.read_parquet(path, columns=cols + ["is_chosen"])
        df  = tmp[tmp["is_chosen"] == 1].drop_duplicates("stacked_hh_uid")
    except Exception:
        tmp = pd.read_parquet(path, columns=cols + ["draw_joint"])
        df  = tmp[tmp["draw_joint"] == 0].drop_duplicates("stacked_hh_uid")
    multi = df["year_tag"].nunique() > 1
    key   = (df["idhh"].astype(np.int64) * 10 + df["year_tag"].astype(np.int64)
             if multi else df["idhh"].astype(np.int64))
    df    = df.assign(gkey=key.values)
    return {int(k): (int(uid), int(yt))
            for k, uid, yt in zip(df["gkey"], df["stacked_hh_uid"], df["year_tag"])}


def _summary(arr) -> dict:
    a = np.asarray(arr, dtype=np.float64)
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return {
        "n": int(len(a)),
        "min": float(a.min()),    "p05": float(np.percentile(a, 5)),
        "p10": float(np.percentile(a, 10)), "p25": float(np.percentile(a, 25)),
        "median": float(np.median(a)),
        "p75": float(np.percentile(a, 75)), "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)), "max": float(a.max()),
        "mean": float(a.mean()),
    }


def main():
    t_global = time.time()
    bp = bpool_dir()
    cert_stem, staged_stem, staged_cpl_stem = _load_cfg()
    spec  = sp.parse_specification(str(_SPEC))
    theta = _load_theta(spec)

    spec_hash  = hashlib.sha256(_SPEC.read_bytes()).hexdigest()[:16]
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    print(f"spec_hash={spec_hash}  theta_hash={theta_hash}")
    print(f"cert_stem={cert_stem}")
    print(f"staged_stem={staged_stem}  staged_cpl_stem={staged_cpl_stem}")

    _OUT_S.parent.mkdir(parents=True, exist_ok=True)
    (_REPO / "outputs/welfare/fastlane_anchors_v1").mkdir(parents=True, exist_ok=True)

    result: dict = {
        "f3_run": "tasks1_5",
        "spec_hash": spec_hash, "theta_hash": theta_hash,
        "cert_stem": cert_stem, "staged_stem": staged_stem,
        "gate0_anchors": {"singles_male": _GATE0_SM, "singles_female": _GATE0_SF,
                          "couples": _GATE0_COU},
    }

    # ============================================================
    # TASK 1 — Singles V_i^IS on staged + certified stems
    # ============================================================
    print("\n=== TASK 1: Singles V_i^IS ===")
    t1 = time.time()

    print(f"Loading staged singles: {staged_stem}")
    data_sm_s, data_sf_s, _ = jrt.build_data_objects(
        staged_stem, [], 0, couples_stem=staged_cpl_stem)

    print(f"Loading certified singles + couples: {cert_stem}")
    data_sm_c, data_sf_c, data_cou_c = jrt.build_data_objects(
        cert_stem, [], 0, couples_stem=cert_stem)

    print("  compute_group_welfare: singles_male (staged)...")
    gw_sm_s = wc.compute_group_welfare(data_sm_s, spec, theta, "singles_male")
    print("  compute_group_welfare: singles_female (staged)...")
    gw_sf_s = wc.compute_group_welfare(data_sf_s, spec, theta, "singles_female")
    print("  compute_group_welfare: singles_male (certified)...")
    gw_sm_c = wc.compute_group_welfare(data_sm_c, spec, theta, "singles_male")
    print("  compute_group_welfare: singles_female (certified)...")
    gw_sf_c = wc.compute_group_welfare(data_sf_c, spec, theta, "singles_female")

    # Gate-0: certified stem negLL vs pre-registered anchors
    g0_sm = wc.gate0_parity(data_sm_c, spec, theta, "singles_male",   gw_sm_c)
    g0_sf = wc.gate0_parity(data_sf_c, spec, theta, "singles_female", gw_sf_c)
    sm_diff = abs(g0_sm["estimator_negll"] - _GATE0_SM)
    sf_diff = abs(g0_sf["estimator_negll"] - _GATE0_SF)
    gate0_pass = (g0_sm["max_abs"] < _TOL and g0_sf["max_abs"] < _TOL
                  and sm_diff < _TOL and sf_diff < _TOL)
    print(f"  Gate-0: sm_max_abs={g0_sm['max_abs']:.2e}  sf_max_abs={g0_sf['max_abs']:.2e}  "
          f"sm_anchor_diff={sm_diff:.2e}  sf_anchor_diff={sf_diff:.2e}  PASS={gate0_pass}")
    if not gate0_pass:
        raise SystemExit("STOP: Gate-0 singles FAILED — parity or anchor mismatch")

    # Build uid bridges (staged + certified for both genders)
    bridge_sm_s = _build_bridge_singles(bp, staged_stem, "singles_male")
    bridge_sf_s = _build_bridge_singles(bp, staged_stem, "singles_female")
    bridge_sm_c = _build_bridge_singles(bp, cert_stem, "singles_male")
    bridge_sf_c = _build_bridge_singles(bp, cert_stem, "singles_female")

    # Certified IS lookup for delta computation
    uid_vi_cert: dict[int, float] = {}
    for gw_c, data_c, bridge_c in [
        (gw_sm_c, data_sm_c, bridge_sm_c),
        (gw_sf_c, data_sf_c, bridge_sf_c),
    ]:
        for i in range(gw_c.n_groups):
            info = bridge_c.get(int(data_c.group_ids[i]))
            if info:
                uid_vi_cert[info[0]] = float(gw_c.V_is[i])

    # Assemble per-HH rows (staged IS is primary)
    rows_singles = []
    anchor_vi_staged: float | None = None

    for gw_s, data_s, bridge_s, group in [
        (gw_sm_s, data_sm_s, bridge_sm_s, "singles_male"),
        (gw_sf_s, data_sf_s, bridge_sf_s, "singles_female"),
    ]:
        for i in range(gw_s.n_groups):
            info = bridge_s.get(int(data_s.group_ids[i]))
            if not info:
                continue
            uid, year_tag = info
            vi_stg = float(gw_s.V_is[i])
            vi_crt = uid_vi_cert.get(uid, float("nan"))
            delta  = vi_stg - vi_crt if np.isfinite(vi_crt) else float("nan")
            rows_singles.append({
                "uid": uid, "group": group, "year_tag": year_tag,
                "V_i_IS": vi_stg, "ESS": float(gw_s.ess[i]),
                "max_weight": float(gw_s.max_w[i]),
                "V_i_IS_certified": vi_crt,
                "delta_staged_minus_cert": delta,
                # Task-2 columns: populated by the V_i^dir run if/when gate 3b passes
                "S_effective": float("nan"), "V_dir_util": float("nan"),
                "V_dir_fullV": float("nan"), "delta_common": float("nan"),
                "cv2": float("nan"),
            })
            if uid == _ANCHOR_UID:
                anchor_vi_staged = vi_stg

    singles_df = pd.DataFrame(rows_singles)
    n_sm = int((singles_df["group"] == "singles_male").sum())
    n_sf = int((singles_df["group"] == "singles_female").sum())
    print(f"  Singles: {n_sm} singles_male + {n_sf} singles_female = {len(singles_df)} rows")
    singles_df.to_parquet(_OUT_S, index=False)
    print(f"  Saved: {_OUT_S}")

    # Anchor verification (must equal 11.496632024594227 to <=1e-9 on staged stem)
    anchor_diff = abs(anchor_vi_staged - _ANCHOR_VIS) if anchor_vi_staged is not None else None
    anchor_ok   = anchor_diff is not None and anchor_diff <= _ANCHOR_TOL
    diff_str = f"{anchor_diff:.2e}" if anchor_diff is not None else "N/A"
    print(f"  Anchor UID {_ANCHOR_UID}: V_i^IS_staged={anchor_vi_staged}  "
          f"target={_ANCHOR_VIS}  diff={diff_str}  ok(1e-9)={anchor_ok}")

    t1_end = time.time()
    task1_s = t1_end - t1

    # Task-3a: ESS gate (read-only from Task 1)
    sm_ess = singles_df[singles_df["group"] == "singles_male"]["ESS"].values
    sf_ess = singles_df[singles_df["group"] == "singles_female"]["ESS"].values

    result["task1"] = {
        "gate0_pass": gate0_pass,
        "gate0_sm": g0_sm, "gate0_sf": g0_sf,
        "n_singles_male": n_sm, "n_singles_female": n_sf,
        "V_is_summary": {
            "singles_male":   _summary(singles_df[singles_df["group"]=="singles_male"]["V_i_IS"]),
            "singles_female": _summary(singles_df[singles_df["group"]=="singles_female"]["V_i_IS"]),
        },
        "ess_summary": {
            "singles_male":   _summary(sm_ess),
            "singles_female": _summary(sf_ess),
        },
        "delta_staged_vs_cert_summary": {
            "singles_male":   _summary(singles_df[singles_df["group"]=="singles_male"]["delta_staged_minus_cert"]),
            "singles_female": _summary(singles_df[singles_df["group"]=="singles_female"]["delta_staged_minus_cert"]),
        },
        "anchor_uid": _ANCHOR_UID,
        "anchor_vi_staged": anchor_vi_staged,
        "anchor_vi_target": _ANCHOR_VIS,
        "anchor_diff": float(anchor_diff) if anchor_diff is not None else None,
        "anchor_ok_1e9": anchor_ok,
        "runtime_s": task1_s,
        "output": str(_OUT_S),
    }
    result["task3a_ess"] = {
        "note": ("ESS thin (~20/101 singles) — expected. That is WHY the dir cross-check exists, "
                 "not a failure."),
        "singles_male":   {
            "median": float(np.median(sm_ess)),
            "p10": float(np.percentile(sm_ess, 10)),
            "p90": float(np.percentile(sm_ess, 90)),
            "n_below_30": int((sm_ess < 30).sum()),
            "total": int(len(sm_ess)),
        },
        "singles_female": {
            "median": float(np.median(sf_ess)),
            "p10": float(np.percentile(sf_ess, 10)),
            "p90": float(np.percentile(sf_ess, 90)),
            "n_below_30": int((sf_ess < 30).sum()),
            "total": int(len(sf_ess)),
        },
    }
    print(f"  Task 1 runtime: {task1_s:.1f}s")

    # ============================================================
    # TASK 5 — Couples V_i^IS on certified stem
    # ============================================================
    print("\n=== TASK 5: Couples V_i^IS (certified stem) ===")
    t5 = time.time()

    print("  compute_group_welfare: couples (certified)...")
    gw_cou_c = wc.compute_group_welfare(data_cou_c, spec, theta, "couples")
    g0_cou   = wc.gate0_parity(data_cou_c, spec, theta, "couples", gw_cou_c)
    cou_diff = abs(g0_cou["estimator_negll"] - _GATE0_COU)
    gate0_cou_pass = (g0_cou["max_abs"] < _TOL and cou_diff < _TOL)
    print(f"  Gate-0 couples: max_abs={g0_cou['max_abs']:.2e}  "
          f"anchor_diff={cou_diff:.2e}  PASS={gate0_cou_pass}")
    if not gate0_cou_pass:
        raise SystemExit("STOP: Gate-0 couples FAILED — parity or anchor mismatch")

    bridge_cou = _build_bridge_couples(bp, cert_stem)
    gk_cou     = np.asarray(data_cou_c.group_ids)

    cou_rows = []
    for i in range(gw_cou_c.n_groups):
        info = bridge_cou.get(int(gk_cou[i]))
        if not info:
            continue
        uid, year_tag = info
        cou_rows.append({
            "uid": uid, "year_tag": year_tag,
            "V_i_IS": float(gw_cou_c.V_is[i]),
            "ESS":    float(gw_cou_c.ess[i]),
            "max_weight": float(gw_cou_c.max_w[i]),
        })

    couples_df = pd.DataFrame(cou_rows)
    print(f"  Couples: {len(couples_df)} rows, {couples_df['uid'].nunique()} unique HH")
    couples_df.to_parquet(_OUT_C, index=False)
    print(f"  Saved: {_OUT_C}")

    t5_end = time.time()
    task5_s = t5_end - t5
    cou_ess = couples_df["ESS"].values
    result["task5"] = {
        "gate0_pass": gate0_cou_pass,
        "gate0_cou": g0_cou,
        "n_couples": int(len(couples_df)),
        "V_is_summary": _summary(couples_df["V_i_IS"]),
        "ess_summary": _summary(cou_ess),
        "n_ess_below_30": int((cou_ess < 30).sum()),
        "runtime_s": task5_s,
        "output": str(_OUT_C),
    }
    print(f"  Task 5 runtime: {task5_s:.1f}s")

    result["total_runtime_s"] = time.time() - t_global
    result["status"] = "OK"
    _OUT_JSON.write_text(json.dumps(result, indent=2, default=float))
    print(f"\nSaved summary JSON: {_OUT_JSON}")
    print(f"Total runtime: {result['total_runtime_s']:.1f}s")
    print("\n=== TASK 1+5 COMPLETE ===")
    print(f"singles: {_OUT_S}")
    print(f"couples: {_OUT_C}")


if __name__ == "__main__":
    main()
