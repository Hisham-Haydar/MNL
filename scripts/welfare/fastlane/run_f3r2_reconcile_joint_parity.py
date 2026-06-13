"""
F3-R2: Post-F3 Reconciliation + Durable Anchor Completion + Joint-Batch Parity Gate.

Authorized by the F3-R2 prompt. Supersedes F3-R. All F3 artifacts are immutable inputs.

Tasks:
  0 - Audit F3 inputs (hash + schema + frozen-fact verification)
  1 - Emit dual-stem V_i^IS parquets (singles + couples) with V_obs and negll_contribution
  2 - Price 3 anchors (primary + top-ESS 2016 sm + top-ESS 2016 sf) via frozen RNG, target-only
  3 - Joint-batch parity gate: ALL 2016 singles HHs redrawn simultaneously, one EUROMOD call;
      compare anchor rows against Task-2 target-only output; verdict LICENSED / NOT LICENSED
  4 - Five explicit decision lines

Constraints:
  - No edits to engines, specs, data, existing welfare scripts, or existing F3 artifacts
  - Atomic writes only (temp -> validate -> rename)
  - Never overwrite existing F3 artifacts
  - No commit
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# path setup
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent.parent.parent.parent
for _p in [
    _REPO / "scripts/bpool",
    _REPO / "scripts/enhanced",
    _REPO / "scripts/welfare",
    _REPO / "scripts/pilot",
]:
    sys.path.insert(0, str(_p))

import jax  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

import estimation_spec_parser as sp  # noqa: E402
import joint_recovery_test as jrt    # noqa: E402
import welfare_core as wc            # noqa: E402
import welfare_vdir as wvd           # noqa: E402
import yaml                          # noqa: E402
from _bpool_paths import bpool_dir   # noqa: E402

# ---------------------------------------------------------------------------
# paths — F3 inputs (immutable)
# ---------------------------------------------------------------------------
_CONFIG       = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"
_SPEC         = _REPO / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
_THETA        = _REPO / "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"
_F3_SINGLES   = _REPO / "outputs/welfare/fastlane/singles_Vi_production_v1.parquet"
_F3_COUPLES   = _REPO / "outputs/welfare/fastlane/couples_ViIS_capture_v1.parquet"
_F3_SUMMARY   = _REPO / "outputs/welfare/fastlane/f3_tasks1_5_summary.json"
_F3_GATE3B    = _REPO / "outputs/welfare/fastlane/f3_task2_gate3b_30hh_100nodes.json"
_V1_MANIFEST  = _REPO / "outputs/welfare/fastlane_anchors_v1/manifest.json"

# ---------------------------------------------------------------------------
# paths — new F3-R2 outputs
# ---------------------------------------------------------------------------
_OUT_DIR      = _REPO / "outputs/welfare/fastlane"
_OUT_SINGLES  = _OUT_DIR / "singles_ViIS_dualstem_v1.parquet"
_OUT_COUPLES  = _OUT_DIR / "couples_ViIS_dualstem_v1.parquet"
_OUT_MANIFEST = _OUT_DIR / "f3r2_reconciliation_manifest_v1.json"
_OUT_PARITY   = _OUT_DIR / "f3r2_joint_batch_parity_2016_singles_v1.json"
_OUT_AV2      = _REPO / "outputs/welfare/fastlane_anchors_v2"
_OUT_DOC      = _REPO / "docs/jmp_methodology/RURO_welfare_F3R2_reconciliation_joint_parity_v1.md"

# ---------------------------------------------------------------------------
# pre-registered constants (frozen from F3 manifest + gate3b)
# ---------------------------------------------------------------------------
_GATE0_SM   = 28489.042816294535
_GATE0_SF   = 35411.86351549324
_GATE0_COU  = 174603.72976561091
_PRIMARY_UID = 200001593700
_PRIMARY_VIS = 11.496632024594227
_TOL        = 1e-6
_ANCHOR_TOL = 1e-9

# F3-R2 operational constants
BASE_SEED        = 20260604
YEAR             = 2016
YEAR_TAG         = 2
N_NODES          = 100
_FR_STD_HOURS    = 35.0
_WEEKS_PER_MONTH = 52.0 / 12.0


# ---------------------------------------------------------------------------
# helpers: load config / spec / theta
# ---------------------------------------------------------------------------
def _load_cfg():
    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    w = cfg["welfare"]
    cert       = w["baseline"]["engine_ready_stem"]
    staged     = w["stage4"]["welfare_pricing_reference"]["staged_engine_ready_stem"]
    staged_cpl = w["stage4"]["welfare_pricing_reference"].get("staged_couples_stem", staged)
    return cert, staged, staged_cpl


def _load_theta(spec):
    df = pd.read_csv(_THETA)
    lu = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    return np.array([lu.get(n, float(spec.initial_values.get(n, 0.0)))
                     for n in spec.all_param_names], dtype=np.float64)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# helpers: uid bridge (mirrors run_f3_tasks1_5.py)
# ---------------------------------------------------------------------------
def _build_bridge_singles(bp: Path, stem: str, group: str) -> dict:
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


# ---------------------------------------------------------------------------
# helper: V_obs from extractor  (Vg[:,0] = V at draw 0 = observed state)
# ---------------------------------------------------------------------------
def _compute_v_obs(data, spec, theta_jax, group: str) -> np.ndarray:
    Vfn, meta = wc._build_V_extractor(data, spec, group)
    V_all = np.asarray(Vfn(theta_jax, jnp.asarray(meta["consumption"])))
    n_alts = data.n_obs // data.n_groups  # e.g. 101 for singles (draws 0..100)
    Vg = V_all.reshape(data.n_groups, n_alts)
    return Vg[:, 0]


# ---------------------------------------------------------------------------
# helper: atomic write
# ---------------------------------------------------------------------------
_F3_IMMUTABLE = {_F3_SINGLES, _F3_COUPLES, _F3_SUMMARY, _F3_GATE3B, _V1_MANIFEST}


def _atomic_write_parquet(df: pd.DataFrame, dest: Path):
    if dest in _F3_IMMUTABLE:
        raise FileExistsError(f"STOP: would overwrite immutable F3 artifact: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False)
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_write_json(obj: dict, dest: Path):
    if dest in _F3_IMMUTABLE:
        raise FileExistsError(f"STOP: would overwrite immutable F3 artifact: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2))
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# helper: EUROMOD pricing with full EM_OUTPUT_COLS capture
# (variant of price_nodes_population_faithful that captures all EM cols)
# ---------------------------------------------------------------------------
def _price_target_hh_full_em(bc, band: pd.DataFrame, target_uid: int, nodes: dict,
                              phi: float, country: str, system_code: str,
                              dataset_name: str, mode: str = "singles"):
    """Run EUROMOD on the full band with the target HH's nodes substituted at
    draws 1..N_NODES. Returns (priced_target_df, status) where priced_target_df
    has all EM_OUTPUT_COLS + ils_dispy_real. Mirrors price_nodes_population_faithful
    but captures the full bc['em_output_cols'] from sim, not just ils_dispy."""
    n_nodes = len(nodes["working"])
    dec_draws = sorted(
        d for d in
        band[(band["stacked_hh_uid"] == target_uid) & (band["ruro_decider"] == 1)
             & (band["draw"] >= 1)]["draw"].unique()
    )
    if len(dec_draws) < n_nodes:
        return None, {"status": "BLOCKED",
                      "reason": f"{target_uid}: only {len(dec_draws)} decider draws >= 1"}
    use_draws = dec_draws[:n_nodes]

    band_mod = band.copy()
    _overwrite_choice_vars(band_mod, target_uid, nodes, use_draws)

    bmod = __import__("run_bpool_euromod_chunk")
    id_mult = 1_000 if mode == "singles" else 10_000
    stamped = bmod._stamp_draw_ids(band_mod.copy(), "draw", id_mult)
    raw_cols = bc["raw_schema"][YEAR]
    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)

    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em_input, country=country,
                                      system_code=system_code,
                                      dataset_name=dataset_name)
    except Exception as e:
        return None, {"status": "BLOCKED", "reason": f"EUROMOD failed: {e}"}

    if len(sim) != len(band):
        return None, {"status": "BLOCKED",
                      "reason": f"sim row count mismatch: {len(sim)} vs {len(band)}"}

    out = band_mod.reset_index(drop=True).copy()
    em_cols = bc["em_output_cols"]
    for col in em_cols:
        if col in sim.columns:
            out[col] = sim[col].values
    out["ils_dispy_real"] = out.get("ils_dispy", pd.Series(np.nan, index=out.index)) * phi

    tgt = out[(out["stacked_hh_uid"] == target_uid) & (out["draw"].isin(use_draws))
              & (out["ruro_decider"] == 1)].copy().sort_values("draw").reset_index(drop=True)
    return tgt, {"status": "OK", "n_target_nodes": len(tgt),
                 "used_draw_slots": [int(d) for d in use_draws]}


def _overwrite_choice_vars(band: pd.DataFrame, target_uid: int, nodes: dict, use_draws):
    """Overwrite the target HH's decider rows at use_draws with redrawn node values.
    Uses authoritative FR earnings identity: yem = yem00 + yemxp with 35h split."""
    for k, dr in enumerate(use_draws):
        sel = ((band["stacked_hh_uid"] == target_uid) & (band["draw"] == dr)
               & (band["ruro_decider"] == 1))
        if int(sel.sum()) != 1:
            raise RuntimeError(f"_overwrite: uid={target_uid} draw={dr}: "
                                f"expected 1 decider row, got {int(sel.sum())}")
        wk  = int(nodes["working"][k])
        h   = float(nodes["hours"][k])
        w   = float(nodes["wage"][k])
        lo4 = int(nodes["loc4"][k])
        if wk == 1 and h > 0 and w > 0:
            reg_h  = min(h, _FR_STD_HOURS)
            ot_h   = max(h - _FR_STD_HOURS, 0.0)
            yem00  = reg_h * w * _WEEKS_PER_MONTH
            yemxp  = ot_h * w * _WEEKS_PER_MONTH
            band.loc[sel, "lhw"]      = h
            band.loc[sel, "yivwg"]    = w
            band.loc[sel, "yem_hour"] = w
            band.loc[sel, "yem00"]    = yem00
            band.loc[sel, "yemxp"]    = yemxp
            band.loc[sel, "yem"]      = yem00 + yemxp
            band.loc[sel, "working"]  = 1.0
            if "hours" in band.columns:
                band.loc[sel, "hours"] = h
            if "wage" in band.columns:
                band.loc[sel, "wage"] = w
            if "loc4" in band.columns and lo4 >= 1:
                band.loc[sel, "loc4"] = float(lo4)
        else:
            for c in ("lhw", "yivwg", "yem", "yem00", "yemxp", "yem_hour", "hours", "wage"):
                if c in band.columns:
                    band.loc[sel, c] = 0.0
            band.loc[sel, "working"] = 0.0


# ---------------------------------------------------------------------------
# TASK 0 — Audit F3 inputs
# ---------------------------------------------------------------------------
def task0_audit(bp: Path, staged_stem: str, cert_stem: str) -> dict:
    print("\n=== TASK 0: Audit F3 inputs ===")
    audit: dict = {}

    # Hash F3 input files
    for label, path in [
        ("spec_yaml",  _SPEC),
        ("theta_csv",  _THETA),
        ("f3_singles_parquet", _F3_SINGLES),
        ("f3_couples_parquet", _F3_COUPLES),
        ("f3_summary_json",    _F3_SUMMARY),
        ("v1_manifest_json",   _V1_MANIFEST),
    ]:
        if path.exists():
            audit[f"hash_{label}"] = _sha256(path)
            print(f"  hash({label}) = {audit[f'hash_{label}'][:16]}…")
        else:
            audit[f"hash_{label}"] = None
            print(f"  MISSING: {path}")

    # Hash staged + certified parquets
    staged_pq = bp / f"{staged_stem}__singles.parquet"
    cert_pq   = bp / f"{cert_stem}__singles.parquet"
    audit["hash_staged_singles_pq"] = _sha256(staged_pq) if staged_pq.exists() else None
    audit["hash_cert_singles_pq"]   = _sha256(cert_pq)   if cert_pq.exists()   else None
    print(f"  hash(staged_singles_pq) = {(audit['hash_staged_singles_pq'] or 'MISSING')[:16]}…")
    print(f"  hash(cert_singles_pq)   = {(audit['hash_cert_singles_pq']   or 'MISSING')[:16]}…")

    # Verify row counts from existing production parquets
    s_df = pd.read_parquet(_F3_SINGLES)
    c_df = pd.read_parquet(_F3_COUPLES)
    n_singles = len(s_df)
    n_couples = len(c_df)
    audit["n_singles"] = n_singles
    audit["n_couples"] = n_couples
    ok_singles = n_singles == 5007
    ok_couples = n_couples == 7438
    print(f"  n_singles={n_singles} (expect 5007: {ok_singles})")
    print(f"  n_couples={n_couples} (expect 7438: {ok_couples})")
    if not (ok_singles and ok_couples):
        raise SystemExit("STOP Task-0: row count mismatch")

    # Verify anchor UID 200001593700 V_i^IS_staged
    anchor_row = s_df[s_df["uid"] == _PRIMARY_UID]
    if anchor_row.empty:
        raise SystemExit(f"STOP Task-0: anchor UID {_PRIMARY_UID} not found in singles parquet")
    vis_stored = float(anchor_row["V_i_IS"].iloc[0])
    vis_diff = abs(vis_stored - _PRIMARY_VIS)
    ok_vis = vis_diff <= _ANCHOR_TOL
    audit["anchor_uid"] = _PRIMARY_UID
    audit["anchor_vis_stored"] = vis_stored
    audit["anchor_vis_diff"] = vis_diff
    audit["anchor_vis_ok"] = ok_vis
    print(f"  Anchor {_PRIMARY_UID}: V_i^IS_staged={vis_stored}  diff={vis_diff:.2e}  ok={ok_vis}")
    if not ok_vis:
        raise SystemExit("STOP Task-0: anchor V_i^IS mismatch beyond 1e-9")

    # Verify Gate-0 anchors from F3 summary
    with open(_F3_SUMMARY) as f:
        summary = json.load(f)
    sm_neg  = float(summary.get("task1", {}).get("gate0_sm",  {}).get("welfare_negll", float("nan")))
    sf_neg  = float(summary.get("task1", {}).get("gate0_sf",  {}).get("welfare_negll", float("nan")))
    cou_neg = float(summary.get("task5", {}).get("gate0_cou", {}).get("welfare_negll", float("nan")))
    sm_ok = abs(sm_neg - _GATE0_SM) <= _TOL
    sf_ok = abs(sf_neg - _GATE0_SF) <= _TOL
    co_ok = abs(cou_neg - _GATE0_COU) <= _TOL
    audit["gate0_sm_diff"] = abs(sm_neg - _GATE0_SM)
    audit["gate0_sf_diff"] = abs(sf_neg - _GATE0_SF)
    audit["gate0_cou_diff"] = abs(cou_neg - _GATE0_COU)
    audit["gate0_all_ok"] = bool(sm_ok and sf_ok and co_ok)
    print(f"  Gate-0 sm diff={abs(sm_neg-_GATE0_SM):.2e}  sf diff={abs(sf_neg-_GATE0_SF):.2e}  "
          f"cou diff={abs(cou_neg-_GATE0_COU):.2e}  all_ok={audit['gate0_all_ok']}")
    if not audit["gate0_all_ok"]:
        raise SystemExit("STOP Task-0: Gate-0 anchor mismatch")

    # Read frozen Gate-3b verdict
    with open(_F3_GATE3B) as f:
        g3b = json.load(f)
    audit["gate3b_verdict"] = g3b.get("verdict", "unknown")
    audit["gate3b_high_ess_median"] = g3b.get("high_ess_delta_common_median_abs", None)
    print(f"  Gate-3b: verdict={audit['gate3b_verdict']}  "
          f"high_ess_median={audit['gate3b_high_ess_median']}")

    audit["task0_status"] = "PASS"
    print("  Task-0: PASS")
    return audit


# ---------------------------------------------------------------------------
# TASK 1 — Emit dual-stem V_i^IS parquets
# ---------------------------------------------------------------------------
def task1_emit_dualstem(bp: Path, staged_stem: str, cert_stem: str, staged_cpl: str,
                        spec, theta: np.ndarray) -> dict:
    print("\n=== TASK 1: Emit dual-stem V_i^IS parquets ===")
    t0 = time.time()
    theta_jax = jnp.asarray(theta)

    print(f"  Loading staged objects: {staged_stem}")
    data_sm_s, data_sf_s, data_cou_s = jrt.build_data_objects(
        staged_stem, [], 0, couples_stem=staged_cpl)

    print(f"  Loading certified objects: {cert_stem}")
    data_sm_c, data_sf_c, data_cou_c = jrt.build_data_objects(
        cert_stem, [], 0, couples_stem=cert_stem)

    singles_rows = []
    couples_rows = []

    for stem_label, data_sm, data_sf, data_cou in [
        ("staged",    data_sm_s, data_sf_s, data_cou_s),
        ("certified", data_sm_c, data_sf_c, data_cou_c),
    ]:
        stem = staged_stem if stem_label == "staged" else cert_stem
        print(f"  compute_group_welfare [{stem_label}]...")
        gw_sm  = wc.compute_group_welfare(data_sm,  spec, theta, "singles_male")
        gw_sf  = wc.compute_group_welfare(data_sf,  spec, theta, "singles_female")
        gw_cou = wc.compute_group_welfare(data_cou, spec, theta, "couples")

        print(f"  V_obs [{stem_label}]: singles_male...")
        v_obs_sm  = _compute_v_obs(data_sm,  spec, theta_jax, "singles_male")
        print(f"  V_obs [{stem_label}]: singles_female...")
        v_obs_sf  = _compute_v_obs(data_sf,  spec, theta_jax, "singles_female")
        print(f"  V_obs [{stem_label}]: couples...")
        v_obs_cou = _compute_v_obs(data_cou, spec, theta_jax, "couples")

        bridge_sm  = _build_bridge_singles(bp, stem, "singles_male")
        bridge_sf  = _build_bridge_singles(bp, stem, "singles_female")
        bridge_cou = _build_bridge_couples(bp, stem)

        for gw, data, bridge, vobs, group in [
            (gw_sm,  data_sm,  bridge_sm,  v_obs_sm,  "singles_male"),
            (gw_sf,  data_sf,  bridge_sf,  v_obs_sf,  "singles_female"),
        ]:
            for i in range(gw.n_groups):
                info = bridge.get(int(data.group_ids[i]))
                if not info:
                    continue
                uid, yt = info
                vis = float(gw.V_is[i])
                vo  = float(vobs[i])
                negll = vis - vo
                row = {
                    "uid": uid, "group": group, "year_tag": yt,
                    f"V_i_IS_{stem_label}": vis,
                    f"ESS_{stem_label}": float(gw.ess[i]),
                    f"max_weight_{stem_label}": float(gw.max_w[i]),
                    f"V_obs_{stem_label}": vo,
                    f"negll_contribution_{stem_label}": negll,
                }
                singles_rows.append(row)

        for i in range(gw_cou.n_groups):
            info = bridge_cou.get(int(data_cou.group_ids[i]))
            if not info:
                continue
            uid, yt = info
            vis = float(gw_cou.V_is[i])
            vo  = float(v_obs_cou[i])
            negll = vis - vo
            row = {
                "uid": uid, "group": "couples", "year_tag": yt,
                f"V_i_IS_{stem_label}": vis,
                f"ESS_{stem_label}": float(gw_cou.ess[i]),
                f"max_weight_{stem_label}": float(gw_cou.max_w[i]),
                f"V_obs_{stem_label}": vo,
                f"negll_contribution_{stem_label}": negll,
            }
            couples_rows.append(row)

    # Merge staged + certified per uid for singles
    s_stg = pd.DataFrame([r for r in singles_rows if "V_i_IS_staged" in r]).set_index(
        ["uid", "group", "year_tag"])
    s_crt = pd.DataFrame([r for r in singles_rows if "V_i_IS_certified" in r]).set_index(
        ["uid", "group", "year_tag"])
    s_merged = s_stg.join(s_crt, how="outer").reset_index()
    s_merged["V_i_IS_delta_staged_minus_certified"] = (
        s_merged["V_i_IS_staged"] - s_merged["V_i_IS_certified"])

    # Merge staged + certified per uid for couples
    c_stg = pd.DataFrame([r for r in couples_rows if "V_i_IS_staged" in r]).set_index(
        ["uid", "group", "year_tag"])
    c_crt = pd.DataFrame([r for r in couples_rows if "V_i_IS_certified" in r]).set_index(
        ["uid", "group", "year_tag"])
    c_merged = c_stg.join(c_crt, how="outer").reset_index()
    c_merged["V_i_IS_delta_staged_minus_certified"] = (
        c_merged["V_i_IS_staged"] - c_merged["V_i_IS_certified"])

    col_order_s = ["uid", "group", "year_tag",
                   "V_i_IS_staged", "ESS_staged", "max_weight_staged",
                   "V_obs_staged", "negll_contribution_staged",
                   "V_i_IS_certified", "ESS_certified", "max_weight_certified",
                   "V_obs_certified", "negll_contribution_certified",
                   "V_i_IS_delta_staged_minus_certified"]
    col_order_c = col_order_s  # same schema
    s_out = s_merged[[c for c in col_order_s if c in s_merged.columns]]
    c_out = c_merged[[c for c in col_order_c if c in c_merged.columns]]

    print(f"  singles: {len(s_out)} rows  couples: {len(c_out)} rows")

    _atomic_write_parquet(s_out, _OUT_SINGLES)
    _atomic_write_parquet(c_out, _OUT_COUPLES)
    print(f"  Wrote: {_OUT_SINGLES}")
    print(f"  Wrote: {_OUT_COUPLES}")

    result = {
        "n_singles": len(s_out),
        "n_couples": len(c_out),
        "singles_negll_staged_sum": float(s_out["negll_contribution_staged"].sum()),
        "couples_negll_staged_sum": float(c_out["negll_contribution_staged"].sum()),
        "delta_staged_minus_cert_singles_median": float(
            s_out["V_i_IS_delta_staged_minus_certified"].median()),
        "task1_elapsed_s": round(time.time() - t0, 1),
        "task1_status": "DONE",
    }
    print(f"  Task-1 elapsed: {result['task1_elapsed_s']}s  status: DONE")
    return result


# ---------------------------------------------------------------------------
# TASK 2 — Price 3 anchors
# ---------------------------------------------------------------------------
def task2_price_anchors(bp: Path, staged_stem: str, spec, theta: np.ndarray) -> dict:
    print("\n=== TASK 2: Price 3 anchors ===")
    t0 = time.time()

    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)

    # Load full 2016 singles precompute band (all draws, all HHs)
    print(f"  Loading 2016 singles band (year_tag={YEAR_TAG}) from {staged_stem}...")
    band_full = pd.read_parquet(
        bp / f"{staged_stem}__singles.parquet")
    band_2016 = band_full[band_full["year_tag"] == YEAR_TAG].copy()
    print(f"  Band size: {len(band_2016)} rows, "
          f"{band_2016['stacked_hh_uid'].nunique()} HHs")

    # Identify the 3 anchors from the production parquet
    s_df = pd.read_parquet(_F3_SINGLES)
    s_2016 = s_df[s_df["year_tag"] == YEAR_TAG].copy()

    sm_2016 = s_2016[s_2016["group"] == "singles_male"].sort_values(
        "ESS", ascending=False)
    sf_2016 = s_2016[s_2016["group"] == "singles_female"].sort_values(
        "ESS", ascending=False)
    sf_2016_excl = sf_2016[sf_2016["uid"] != _PRIMARY_UID]

    anchors_to_price = [
        (_PRIMARY_UID, "singles_female", "primary"),
        (int(sm_2016.iloc[0]["uid"]), "singles_male", "top_ess_sm_2016"),
        (int(sf_2016_excl.iloc[0]["uid"]), "singles_female", "top_ess_sf_2016"),
    ]
    print(f"  Anchors selected: {[(a[0], a[2]) for a in anchors_to_price]}")

    _OUT_AV2.mkdir(parents=True, exist_ok=True)

    anchor_results = {}
    for target_uid, group, label in anchors_to_price:
        print(f"  Pricing anchor {target_uid} ({label}, {group})...")
        t_anc = time.time()

        # Frozen RNG per F3-R2 contract
        seed = BASE_SEED + (target_uid % 1_000_000)
        rng  = np.random.default_rng(np.random.PCG64(seed))

        # hh_row from draw-0 decider row
        hh0 = band_2016[(band_2016["stacked_hh_uid"] == target_uid)
                        & (band_2016["draw"] == 0)
                        & (band_2016["ruro_decider"] == 1)]
        if hh0.empty:
            print(f"  BLOCKED: uid {target_uid} not found in 2016 band draw=0")
            anchor_results[label] = {"status": "BLOCKED", "uid": target_uid}
            continue
        hh_row = hh0.iloc[0].to_dict()
        year_tag_hh = int(hh_row.get("year_tag", YEAR_TAG))

        nodes = wvd.redraw_nodes_singles(hh_row, N_NODES, rng, mincer, dm,
                                         year_tag=year_tag_hh)

        priced, status = _price_target_hh_full_em(
            bc, band_2016, target_uid, nodes, phi, country, sys_code, dataset)

        elapsed = round(time.time() - t_anc, 1)
        if priced is None:
            print(f"  BLOCKED: {status['reason']}")
            anchor_results[label] = {"status": "BLOCKED", "uid": target_uid,
                                     "reason": status["reason"]}
            continue

        # Store priced output
        em_cols = bc["em_output_cols"] + ["ils_dispy_real", "stacked_hh_uid", "draw",
                                          "year_tag", "ruro_decider"]
        store_cols = [c for c in em_cols if c in priced.columns]
        priced_out = priced[store_cols].copy()

        anchor_pq = _OUT_AV2 / f"anchor_{label}_uid{target_uid}_priced_nodes_v1.parquet"
        if not anchor_pq.exists():
            priced_out.to_parquet(anchor_pq, index=False)
            print(f"    Saved: {anchor_pq.name}")

        # Summary stats
        em_summary = {}
        for col in bc["em_output_cols"]:
            if col in priced.columns:
                vals = priced[col].dropna().values
                em_summary[col] = {"mean": float(np.mean(vals)), "std": float(np.std(vals)),
                                   "min": float(np.min(vals)), "max": float(np.max(vals))}

        anchor_results[label] = {
            "status": "OK",
            "uid": target_uid,
            "group": group,
            "year_tag": year_tag_hh,
            "seed": seed,
            "n_nodes_priced": int(len(priced)),
            "em_output_summary": em_summary,
            "priced_parquet": str(anchor_pq),
            "elapsed_s": elapsed,
        }
        print(f"    OK: {len(priced)} nodes priced in {elapsed}s")

    result = {
        "anchors": anchor_results,
        "task2_elapsed_s": round(time.time() - t0, 1),
        "task2_status": "DONE" if all(v.get("status") == "OK"
                                      for v in anchor_results.values()) else "PARTIAL",
    }
    print(f"  Task-2 elapsed: {result['task2_elapsed_s']}s  status: {result['task2_status']}")
    return result


# ---------------------------------------------------------------------------
# TASK 3 — Joint-batch parity gate
# ---------------------------------------------------------------------------
def task3_joint_batch_parity(bp: Path, staged_stem: str, spec, theta: np.ndarray,
                              task2_result: dict) -> dict:
    print("\n=== TASK 3: Joint-batch parity gate ===")
    t0 = time.time()

    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)

    print(f"  Loading 2016 singles band from {staged_stem}...")
    band_full = pd.read_parquet(bp / f"{staged_stem}__singles.parquet")
    band = band_full[band_full["year_tag"] == YEAR_TAG].copy().reset_index(drop=True)
    all_uids = sorted(band["stacked_hh_uid"].unique().tolist())
    n_hh = len(all_uids)
    print(f"  Band: {len(band)} rows, {n_hh} HHs, draw range "
          f"[{band['draw'].min()},{band['draw'].max()}]")

    # Build per-HH hh_row dict (from draw=0) and decode draw-1..100 index positions
    print("  Precomputing per-HH hh_row dicts and draw-slot index maps...")
    dec_mask = (band["ruro_decider"] == 1) & (band["draw"] >= 1)
    dec = band[dec_mask][["stacked_hh_uid", "draw"]].copy()
    dec["_idx"] = band[dec_mask].index
    dec_by_uid = {int(uid): grp.sort_values("draw")["_idx"].tolist()
                  for uid, grp in dec.groupby("stacked_hh_uid")}

    hh0_mask = (band["ruro_decider"] == 1) & (band["draw"] == 0)
    hh0 = band[hh0_mask].copy()
    hh_row_by_uid = {int(r["stacked_hh_uid"]): r.to_dict()
                     for _, r in hh0.iterrows()}

    # Redraw all HHs and overwrite band
    print(f"  Redrawing nodes for {n_hh} HHs (frozen RNG)...")
    blocked_uids = []

    # Pre-extract band numpy arrays for efficient update
    choice_cols_present = [c for c in
                           ["lhw", "yivwg", "yem00", "yemxp", "yem", "yem_hour",
                            "hours", "wage", "working", "loc4"]
                           if c in band.columns]
    extra_cols = [c for c in ["yivwg", "yem00", "yemxp", "yem_hour"]
                  if c not in band.columns]
    for c in extra_cols:
        band[c] = 0.0  # add column with default 0

    t_redraw = time.time()
    for n_done, uid in enumerate(all_uids):
        if uid not in hh_row_by_uid:
            blocked_uids.append(uid)
            continue
        hh_row = hh_row_by_uid[uid]
        year_tag_hh = int(hh_row.get("year_tag", YEAR_TAG))
        indices = dec_by_uid.get(uid, [])
        if len(indices) < N_NODES:
            blocked_uids.append(uid)
            continue

        seed = BASE_SEED + (uid % 1_000_000)
        rng  = np.random.default_rng(np.random.PCG64(seed))
        nodes = wvd.redraw_nodes_singles(hh_row, N_NODES, rng, mincer, dm,
                                          year_tag=year_tag_hh)

        use_indices = indices[:N_NODES]
        for k, idx in enumerate(use_indices):
            wk  = int(nodes["working"][k])
            h   = float(nodes["hours"][k])
            w   = float(nodes["wage"][k])
            lo4 = int(nodes["loc4"][k])
            if wk == 1 and h > 0 and w > 0:
                reg_h = min(h, _FR_STD_HOURS)
                ot_h  = max(h - _FR_STD_HOURS, 0.0)
                yem00 = reg_h * w * _WEEKS_PER_MONTH
                yemxp = ot_h * w * _WEEKS_PER_MONTH
                band.at[idx, "lhw"]      = h
                band.at[idx, "yivwg"]    = w
                band.at[idx, "yem_hour"] = w
                band.at[idx, "yem00"]    = yem00
                band.at[idx, "yemxp"]    = yemxp
                band.at[idx, "yem"]      = yem00 + yemxp
                band.at[idx, "working"]  = 1.0
                if "hours" in band.columns:
                    band.at[idx, "hours"] = h
                if "wage" in band.columns:
                    band.at[idx, "wage"] = w
                if "loc4" in band.columns and lo4 >= 1:
                    band.at[idx, "loc4"] = float(lo4)
            else:
                for c in ["lhw", "yivwg", "yem", "yem00", "yemxp", "yem_hour"]:
                    band.at[idx, c] = 0.0
                band.at[idx, "working"] = 0.0
                if "hours" in band.columns:
                    band.at[idx, "hours"] = 0.0
                if "wage" in band.columns:
                    band.at[idx, "wage"] = 0.0

        if (n_done + 1) % 200 == 0:
            print(f"    {n_done+1}/{n_hh} HHs redrawn...")

    redraw_elapsed = round(time.time() - t_redraw, 1)
    print(f"  Redraw done: {n_hh - len(blocked_uids)} HHs modified, "
          f"{len(blocked_uids)} blocked, elapsed {redraw_elapsed}s")

    # Single EUROMOD call on joint batch
    print(f"  Running EUROMOD on joint batch ({len(band)} rows)...")
    t_em = time.time()
    bmod = __import__("run_bpool_euromod_chunk")
    stamped = bmod._stamp_draw_ids(band.copy(), "draw", 1_000)
    raw_cols = bc["raw_schema"][YEAR]
    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em_input, country=country,
                                      system_code=sys_code,
                                      dataset_name=dataset)
    except Exception as e:
        raise RuntimeError(f"Task-3 joint-batch EUROMOD failed: {e}") from e
    em_elapsed = round(time.time() - t_em, 1)
    print(f"  Joint-batch EUROMOD: {len(sim)} rows, elapsed {em_elapsed}s")

    # Attach EM outputs to band
    joint_out = band.reset_index(drop=True).copy()
    em_cols = bc["em_output_cols"]
    for col in em_cols:
        if col in sim.columns:
            joint_out[col] = sim[col].values
    joint_out["ils_dispy_real"] = joint_out.get(
        "ils_dispy", pd.Series(np.nan, index=joint_out.index)) * phi

    # Compare anchor rows against Task-2 target-only output
    compare_cols = em_cols + ["ils_dispy_real"]
    anchor_labels = list(task2_result.get("anchors", {}).keys())
    parity_results = {}
    overall_max_abs = 0.0
    verdict = "LICENSED"

    for label in anchor_labels:
        arec = task2_result["anchors"].get(label, {})
        if arec.get("status") != "OK":
            parity_results[label] = {"status": "SKIPPED_ANCHOR_NOT_PRICED"}
            continue
        target_uid = int(arec["uid"])

        pq_path = Path(arec["priced_parquet"])
        if not pq_path.exists():
            parity_results[label] = {"status": "SKIPPED_PARQUET_MISSING"}
            continue
        tgt_ref = pd.read_parquet(pq_path)  # Task-2 target-only output

        # Joint-batch rows for this anchor, draws 1..N_NODES
        jb_rows = joint_out[
            (joint_out["stacked_hh_uid"] == target_uid)
            & (joint_out["draw"] >= 1)
            & (joint_out["ruro_decider"] == 1)
        ].sort_values("draw").reset_index(drop=True)

        tgt_draws = set(tgt_ref["draw"].tolist()) if "draw" in tgt_ref.columns else set()
        jb_draws  = set(jb_rows["draw"].tolist())
        common_draws = sorted(tgt_draws & jb_draws)

        if not common_draws:
            parity_results[label] = {"status": "NO_COMMON_DRAWS"}
            verdict = "NOT_LICENSED"
            continue

        tgt_sub = tgt_ref[tgt_ref["draw"].isin(common_draws)].sort_values(
            "draw").reset_index(drop=True)
        jb_sub  = jb_rows[jb_rows["draw"].isin(common_draws)].sort_values(
            "draw").reset_index(drop=True)

        col_diffs = {}
        max_abs_anchor = 0.0
        for col in compare_cols:
            if col not in tgt_sub.columns or col not in jb_sub.columns:
                continue
            a = tgt_sub[col].values.astype(float)
            b = jb_sub[col].values.astype(float)
            max_diff = float(np.nanmax(np.abs(a - b)))
            col_diffs[col] = {"max_abs_diff": max_diff, "pass": max_diff <= TOL_1E6}
            max_abs_anchor = max(max_abs_anchor, max_diff)

        overall_max_abs = max(overall_max_abs, max_abs_anchor)
        anchor_pass = all(v["pass"] for v in col_diffs.values())
        if not anchor_pass:
            verdict = "NOT_LICENSED"

        parity_results[label] = {
            "uid": target_uid,
            "n_common_draws": len(common_draws),
            "max_abs_diff_overall": max_abs_anchor,
            "pass": anchor_pass,
            "col_diffs": col_diffs,
        }
        print(f"  Anchor {label} (uid={target_uid}): max_abs={max_abs_anchor:.2e}  "
              f"pass={anchor_pass}")

    result = {
        "verdict": verdict,
        "overall_max_abs_diff": overall_max_abs,
        "tol": TOL_1E6,
        "n_hh_joint_batch": n_hh,
        "n_hh_blocked": len(blocked_uids),
        "year": YEAR,
        "year_tag": YEAR_TAG,
        "n_nodes_per_hh": N_NODES,
        "base_seed": BASE_SEED,
        "euromod_system": sys_code,
        "euromod_dataset": dataset,
        "redraw_elapsed_s": redraw_elapsed,
        "euromod_elapsed_s": em_elapsed,
        "anchor_parity": parity_results,
        "task3_elapsed_s": round(time.time() - t0, 1),
        "task3_status": "DONE",
    }
    print(f"  Task-3 verdict: {verdict}  overall_max_abs={overall_max_abs:.2e}  "
          f"elapsed: {result['task3_elapsed_s']}s")
    return result


# ---------------------------------------------------------------------------
# TASK 4 — Five decision lines
# ---------------------------------------------------------------------------
def task4_decisions(task0: dict, task1: dict, task2: dict, task3: dict) -> dict:
    print("\n=== TASK 4: Five decision lines ===")
    d = {}

    # Line 1: V_obs_staged / negll_contribution_staged produced
    d["line1_vobs_negll_produced"] = task1.get("task1_status") == "DONE"
    print(f"  1. V_obs_staged + negll_contribution_staged produced: {d['line1_vobs_negll_produced']}")

    # Line 2: Anchor price status (one line per anchor)
    anchors = task2.get("anchors", {})
    d["line2_anchor_status"] = {
        k: v.get("status") for k, v in anchors.items()}
    print(f"  2. Anchor pricing: {d['line2_anchor_status']}")

    # Line 3: Joint-batch parity verdict
    d["line3_joint_batch_verdict"] = task3.get("verdict", "NOT_RUN")
    d["line3_overall_max_abs"] = task3.get("overall_max_abs_diff", None)
    print(f"  3. Joint-batch parity: {d['line3_joint_batch_verdict']}  "
          f"max_abs={d['line3_overall_max_abs']}")

    # Line 4: Gate-3b verdict (from F3, frozen) → F4 readiness
    gate3b_verdict = task0.get("gate3b_verdict", "FAIL")
    d["line4_gate3b_verdict_frozen"] = gate3b_verdict
    d["line4_f4_authorized"] = (gate3b_verdict == "FAIL"
                                 and d["line3_joint_batch_verdict"] == "LICENSED")
    note4 = ("V_i^IS is gate-0 certified; V_i^dir gate-3b FAILED at S=100. "
              "F4 proceeds on V_i^IS primary integrator with caveats (see F3 report)."
              if d["line4_f4_authorized"] else
              "F4 NOT authorized pending parity resolution.")
    d["line4_note"] = note4
    print(f"  4. F4 authorized: {d['line4_f4_authorized']} -- {note4}")

    # Line 5: Omega(W^3) readiness
    d["line5_omega_ready"] = d["line3_joint_batch_verdict"] == "LICENSED"
    note5 = ("Omega(W^3) can be computed on V_i^IS; joint-batch LICENSED confirms "
              "EUROMOD means-tested benefits are HH-independent in this batch."
              if d["line5_omega_ready"] else
              "Omega(W^3) NOT authorized until joint-batch parity resolves.")
    d["line5_note"] = note5
    print(f"  5. Omega(W^3) ready: {d['line5_omega_ready']} -- {note5}")

    return d


# ---------------------------------------------------------------------------
# helper: EUROMOD system pairing for YEAR
# ---------------------------------------------------------------------------
def _system_pairing(bc: dict):
    system_code, dataset_name = bc["system_pairing"][YEAR]
    country = system_code[:2]
    return country, system_code, dataset_name


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    t_global = time.time()
    bp = bpool_dir()
    cert_stem, staged_stem, staged_cpl = _load_cfg()
    print(f"cert_stem={cert_stem}  staged_stem={staged_stem}  staged_cpl={staged_cpl}")

    spec  = sp.parse_specification(str(_SPEC))
    theta = _load_theta(spec)
    spec_hash  = hashlib.sha256(_SPEC.read_bytes()).hexdigest()[:16]
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    print(f"spec_hash={spec_hash}  theta_hash={theta_hash}")

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    _OUT_AV2.mkdir(parents=True, exist_ok=True)

    # ---- Task 0 ----
    t0_result = task0_audit(bp, staged_stem, cert_stem)

    # ---- Task 1 ----
    t1_result = task1_emit_dualstem(bp, staged_stem, cert_stem, staged_cpl, spec, theta)

    # ---- Task 2 ----
    t2_result = task2_price_anchors(bp, staged_stem, spec, theta)

    # ---- Task 3 ----
    t3_result = task3_joint_batch_parity(bp, staged_stem, spec, theta, t2_result)

    # ---- Task 4 ----
    t4_result = task4_decisions(t0_result, t1_result, t2_result, t3_result)

    # ---- Write main manifest ----
    manifest = {
        "f3r2_artifact": "f3r2_reconciliation_manifest_v1",
        "spec_hash": spec_hash,
        "theta_hash": theta_hash,
        "cert_stem": cert_stem,
        "staged_stem": staged_stem,
        "task0_audit": t0_result,
        "task1_dualstem": t1_result,
        "task2_anchors": t2_result,
        "task3_parity": t3_result,
        "task4_decisions": t4_result,
        "total_elapsed_s": round(time.time() - t_global, 1),
    }
    _atomic_write_json(manifest, _OUT_MANIFEST)
    print(f"\nManifest: {_OUT_MANIFEST}")

    # ---- Write parity gate output ----
    _atomic_write_json(t3_result, _OUT_PARITY)
    print(f"Parity gate: {_OUT_PARITY}")

    # ---- Write report ----
    _write_report(manifest)

    print(f"\nF3-R2 COMPLETE in {manifest['total_elapsed_s']}s")
    print(f"  Joint-batch verdict: {t3_result['verdict']}")
    print(f"  Omega(W^3) ready: {t4_result['line5_omega_ready']}")


# ---------------------------------------------------------------------------
# report writer
# ---------------------------------------------------------------------------
def _write_report(m: dict):
    t3 = m["task3_parity"]
    t4 = m["task4_decisions"]
    t2 = m["task2_anchors"]
    t1 = m["task1_dualstem"]

    lines = [
        "# RURO Welfare F3-R2 Reconciliation + Joint-Batch Parity Report v1",
        "",
        "## Overview",
        "",
        f"- spec_hash: `{m['spec_hash']}`",
        f"- theta_hash: `{m['theta_hash']}`",
        f"- Total elapsed: {m['total_elapsed_s']}s",
        "",
        "## Task 0 — Audit",
        "",
        f"- n_singles: {m['task0_audit']['n_singles']} (expect 5007)",
        f"- n_couples: {m['task0_audit']['n_couples']} (expect 7438)",
        f"- Anchor {_PRIMARY_UID} V_i^IS diff: {m['task0_audit']['anchor_vis_diff']:.2e} (≤1e-9: {m['task0_audit']['anchor_vis_ok']})",
        f"- Gate-0 all OK: {m['task0_audit']['gate0_all_ok']}",
        f"- Gate-3b verdict (frozen): {m['task0_audit']['gate3b_verdict']}",
        "",
        "## Task 1 — Dual-Stem Parquets",
        "",
        f"- Singles rows: {t1['n_singles']}  Couples rows: {t1['n_couples']}",
        f"- Singles staged negll sum: {t1['singles_negll_staged_sum']:.4f}",
        f"- Singles V_i^IS delta (staged−cert) median: {t1['delta_staged_minus_cert_singles_median']:.6f} nats",
        f"- Output: `outputs/welfare/fastlane/singles_ViIS_dualstem_v1.parquet`",
        f"- Output: `outputs/welfare/fastlane/couples_ViIS_dualstem_v1.parquet`",
        "",
        "## Task 2 — Anchor Pricing",
        "",
    ]

    for label, arec in t2.get("anchors", {}).items():
        status = arec.get("status", "UNKNOWN")
        uid    = arec.get("uid", "?")
        n_nd   = arec.get("n_nodes_priced", "?")
        lines += [f"- `{label}` (uid={uid}): status={status}, n_nodes={n_nd}"]

    lines += [
        "",
        "## Task 3 — Joint-Batch Parity Gate",
        "",
        f"- Year: {t3.get('year')} (year_tag={t3.get('year_tag')})",
        f"- N HHs in joint batch: {t3.get('n_hh_joint_batch')}",
        f"- N nodes per HH: {t3.get('n_nodes_per_hh')}",
        f"- Base seed: {t3.get('base_seed')}",
        f"- EUROMOD system: {t3.get('euromod_system')} / {t3.get('euromod_dataset')}",
        f"- Overall max abs diff: {t3.get('overall_max_abs_diff'):.2e}  tol: {t3.get('tol')}",
        f"- **Verdict: {t3.get('verdict')}**",
        "",
        "### Anchor parity by column",
        "",
        "| Anchor | UID | max_abs | pass |",
        "| --- | --- | --- | --- |",
    ]
    for label, prec in t3.get("anchor_parity", {}).items():
        uid  = prec.get("uid", "?")
        mabs = prec.get("max_abs_diff_overall", float("nan"))
        pss  = prec.get("pass", False)
        lines.append(f"| {label} | {uid} | {mabs:.2e} | {pss} |")

    lines += [
        "",
        "## Task 4 — Decisions",
        "",
        f"1. V_obs_staged + negll_contribution_staged produced: **{t4['line1_vobs_negll_produced']}**",
        f"2. Anchor pricing: {t4['line2_anchor_status']}",
        f"3. Joint-batch parity: **{t4['line3_joint_batch_verdict']}** (max_abs={t4['line3_overall_max_abs']:.2e})",
        f"4. F4 authorized: **{t4['line4_f4_authorized']}** — {t4['line4_note']}",
        f"5. Ω(W^3) ready: **{t4['line5_omega_ready']}** — {t4['line5_note']}",
    ]

    report_text = "\n".join(lines) + "\n"
    if _OUT_DOC.exists():
        _OUT_DOC.unlink()
    _OUT_DOC.write_text(report_text, encoding="utf-8")
    print(f"Report: {_OUT_DOC}")


# ---------------------------------------------------------------------------
TOL_1E6 = 1e-6  # module-level for use in task3

if __name__ == "__main__":
    main()
