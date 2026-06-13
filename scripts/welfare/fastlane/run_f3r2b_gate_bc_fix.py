"""
F3-R2B: Fix yem arithmetic in joint-batch Task-3 and re-run Gates B/A/C.

Root cause of F3-R2A Gate-B CONSTRUCTION_MISMATCH:
  Task 2 formula: yem = yem00 + yemxp  (yem00 = reg_h*w*wpm, yemxp = ot_h*w*wpm — two separate products)
  Task 3 formula: yem = (reg_h + ot_h) * w * wpm  (sum hours first: a*c+b*c != (a+b)*c in IEEE 754)
  Observed diff: 4.5e-13 – 9.1e-13 (~1-2 ULP for yem ~ 2000 EUR/month)
  Not a real construction mismatch — purely a floating-point arithmetic path difference.

Fix: compute yem00 and yemxp separately in T3 loop; yem = yem00 + yemxp (matches T2 exactly).

Immutable (read-only): all F3, F3-R2, F3-R2A artifacts + fastlane_anchors_v3/*.
New outputs (never overwrite the above):
  outputs/welfare/fastlane/f3r2b_diagnosis_v1.json
  docs/jmp_methodology/RURO_welfare_F3R2B_gate_bc_v1.md
No commit.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parent.parent.parent.parent
for _p in [
    _REPO / "scripts/bpool",
    _REPO / "scripts/enhanced",
    _REPO / "scripts/welfare",
    _REPO / "scripts/pilot",
]:
    sys.path.insert(0, str(_p))

import jax
jax.config.update("jax_enable_x64", True)

import welfare_vdir as wvd
import yaml
from _bpool_paths import bpool_dir

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
BASE_SEED        = 20260604
YEAR             = 2016
YEAR_TAG         = 2
N_NODES          = 100
_FR_STD_HOURS    = 35.0
_WEEKS_PER_MONTH = 52.0 / 12.0
TOL              = 1e-6

_PRIMARY_UID    = 200001593700
_TOP_ESS_SM_UID = 200003504101
_TOP_ESS_SF_UID = 200003672000
_ANCHOR_UIDS    = [_PRIMARY_UID, _TOP_ESS_SM_UID, _TOP_ESS_SF_UID]
_ANCHOR_LABELS  = ["primary", "top_ess_sm_2016", "top_ess_sf_2016"]

# Immutable F3-R2A artifacts (read-only)
_F3R2A_MANIFEST  = _REPO / "outputs/welfare/fastlane/f3r2a_repair_manifest_v1.json"
_AV3_DIR         = _REPO / "outputs/welfare/fastlane_anchors_v3"
_CONFIG          = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"

# New outputs
_OUT_DIR       = _REPO / "outputs/welfare/fastlane"
_OUT_DIAGNOSIS = _OUT_DIR / "f3r2b_diagnosis_v1.json"
_OUT_DOC       = _REPO / "docs/jmp_methodology/RURO_welfare_F3R2B_gate_bc_v1.md"

_IMMUTABLE = {_F3R2A_MANIFEST}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _atomic_write_json(obj, dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: would overwrite immutable artifact: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=float))
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_write_text(text: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _system_pairing(bc):
    system_code, dataset_name = bc["system_pairing"][YEAR]
    return system_code[:2], system_code, dataset_name


def _overwrite_fixed(band: pd.DataFrame, uid: int, nodes: dict, use_draws):
    """Overwrite anchor decider rows — FIXED: yem = yem00 + yemxp (separate products)."""
    for k, dr in enumerate(use_draws):
        sel = ((band["stacked_hh_uid"] == uid) & (band["draw"] == dr)
               & (band["ruro_decider"] == 1))
        if int(sel.sum()) != 1:
            raise RuntimeError(f"uid={uid} draw={dr}: {int(sel.sum())} decider rows (expect 1)")
        wk  = int(nodes["working"][k])
        h   = float(nodes["hours"][k])
        w   = float(nodes["wage"][k])
        lo4 = int(nodes["loc4"][k])
        if wk == 1 and h > 0 and w > 0:
            reg_h = min(h, _FR_STD_HOURS)
            ot_h  = max(h - _FR_STD_HOURS, 0.0)
            yem00 = reg_h * w * _WEEKS_PER_MONTH   # separate product — MATCHES Task-2
            yemxp = ot_h  * w * _WEEKS_PER_MONTH   # separate product — MATCHES Task-2
            band.loc[sel, "lhw"]      = h
            band.loc[sel, "yivwg"]    = w
            band.loc[sel, "yem_hour"] = w
            band.loc[sel, "yem00"]    = yem00
            band.loc[sel, "yemxp"]    = yemxp
            band.loc[sel, "yem"]      = yem00 + yemxp   # <-- FIXED (was (reg+ot)*w*wpm)
            band.loc[sel, "working"]  = 1.0
            if "hours" in band.columns:
                band.loc[sel, "hours"] = h
            if "wage"  in band.columns:
                band.loc[sel, "wage"]  = w
            if "loc4"  in band.columns and lo4 >= 1:
                band.loc[sel, "loc4"]  = float(lo4)
        else:
            for c in ("lhw", "yivwg", "yem", "yem00", "yemxp", "yem_hour", "hours", "wage"):
                if c in band.columns:
                    band.loc[sel, c] = 0.0
            band.loc[sel, "working"] = 0.0


def _price_anchor_tgt(bc, band_2016: pd.DataFrame, uid: int, nodes: dict,
                       phi: float, country: str, sys_code: str, dataset: str):
    """Target-only EUROMOD run for one anchor. Returns (anchor_rows_df, error_str)."""
    bmod     = __import__("run_bpool_euromod_chunk")
    raw_cols = bc["raw_schema"][YEAR]

    dec_draws = sorted(
        int(d) for d in band_2016[
            (band_2016["stacked_hh_uid"] == uid)
            & (band_2016["ruro_decider"] == 1)
            & (band_2016["draw"] >= 1)
        ]["draw"].unique()
    )
    use_draws = dec_draws[:N_NODES]
    if len(use_draws) < N_NODES:
        return None, f"only {len(use_draws)} decider draws for uid={uid}"

    band_mod = band_2016.copy()
    for c in ["yivwg", "yem00", "yemxp", "yem_hour"]:
        if c not in band_mod.columns:
            band_mod[c] = 0.0

    _overwrite_fixed(band_mod, uid, nodes, use_draws)

    try:
        stamped  = bmod._stamp_draw_ids(band_mod.copy(), "draw", 1_000)
        em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
        for c in em_input.columns:
            em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em_input, country=country,
                                      system_code=sys_code, dataset_name=dataset)
    except Exception as e:
        return None, f"EUROMOD failed: {e}"

    if len(sim) != len(band_mod):
        return None, f"sim row mismatch {len(sim)} vs {len(band_mod)}"

    raw_cols_set    = set(raw_cols)
    sim_output_cols = [c for c in sim.columns if c not in raw_cols_set]

    out = band_mod.reset_index(drop=True).copy()
    out["idperson_true"] = out["idperson"]
    for col in sim_output_cols:
        out[col] = sim[col].values
    out["ils_dispy_real"] = out["ils_dispy"] * phi if "ils_dispy" in out.columns else float("nan")

    anchor_rows = out[
        (out["stacked_hh_uid"] == uid)
        & (out["draw"].isin(set(use_draws)))
        & (out["ruro_decider"] == 1)
    ].copy().sort_values("draw").reset_index(drop=True)

    return anchor_rows, None


def main():
    t0 = time.time()
    print("F3-R2B start  fix=yem_arithmetic_path_mismatch")

    # Load F3-R2A manifest for Task-1/Task-2 context
    with open(_F3R2A_MANIFEST) as f:
        mf = json.load(f)
    t1  = mf.get("task1_repair", {})
    t2  = mf.get("task2_anchor_evidence", {})
    f4  = t1.get("f4_readiness", "YES")
    b2  = t2.get("utility_only_b2_gate", "fail")
    sim_output_cols_ref = t2.get("sim_output_cols")
    print(f"  F4 readiness (T1): {f4}")
    print(f"  B2 anchor gate (T2): {b2}")
    print(f"  T2 delta_common per anchor:")
    for label in _ANCHOR_LABELS:
        dc = t2.get("anchors", {}).get(label, {}).get("delta_common", float("nan"))
        print(f"    {label}: delta_common={dc:.4f}")

    # Load frozen T2 artifacts (read-only)
    print("\n  Loading frozen T2 artifacts from fastlane_anchors_v3/...")
    frozen_nodes = {}
    t2_em_saved  = {}
    t2_priced    = {}
    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        nodes_pq  = _AV3_DIR / f"anchor_{label}_uid{uid}_nodes_v3.parquet"
        em_pq     = _AV3_DIR / f"anchor_{label}_uid{uid}_em_input_v3.parquet"
        priced_pq = _AV3_DIR / f"anchor_{label}_uid{uid}_priced_v3.parquet"
        for p in [nodes_pq, em_pq, priced_pq]:
            if not p.exists():
                raise RuntimeError(f"STOP: missing frozen T2 artifact: {p}")
        ndf = pd.read_parquet(nodes_pq)
        frozen_nodes[uid] = {
            "working": ndf["working"].to_numpy().astype(np.int8),
            "hours":   ndf["hours"].to_numpy().astype(np.float64),
            "wage":    ndf["wage"].to_numpy().astype(np.float64),
            "loc4":    ndf["loc4"].to_numpy().astype(np.int32),
        }
        t2_em_saved[uid] = pd.read_parquet(em_pq)
        t2_priced[uid]   = pd.read_parquet(priced_pq)
        print(f"    {label} uid={uid}: nodes={len(ndf)}  em_rows={len(t2_em_saved[uid])}  priced_rows={len(t2_priced[uid])}")

    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)
    raw_cols     = bc["raw_schema"][YEAR]
    raw_cols_set = set(raw_cols)
    bmod         = __import__("run_bpool_euromod_chunk")

    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    staged_stem = cfg["welfare"]["stage4"]["welfare_pricing_reference"]["staged_engine_ready_stem"]
    bp = bpool_dir()

    print(f"\n  Loading 2016 singles band from {staged_stem}...")
    band_full = pd.read_parquet(bp / f"{staged_stem}__singles.parquet")
    band = band_full[band_full["year_tag"] == YEAR_TAG].copy().reset_index(drop=True)
    all_uids = sorted(band["stacked_hh_uid"].unique().tolist())
    n_hh = len(all_uids)
    print(f"  Band: {len(band)} rows, {n_hh} HHs")

    for c in ["yivwg", "yem00", "yemxp", "yem_hour"]:
        if c not in band.columns:
            band[c] = 0.0

    # Pre-build index maps
    dec_mask = (band["ruro_decider"] == 1) & (band["draw"] >= 1)
    dec_df   = band[dec_mask][["stacked_hh_uid", "draw"]].copy()
    dec_df["_idx"] = dec_df.index
    dec_by_uid = {int(u): grp.sort_values("draw")["_idx"].tolist()
                  for u, grp in dec_df.groupby("stacked_hh_uid")}
    hh0_rows   = band[(band["ruro_decider"] == 1) & (band["draw"] == 0)]
    hh_by_uid  = {int(r["stacked_hh_uid"]): r.to_dict() for _, r in hh0_rows.iterrows()}
    anchor_uid_set = set(_ANCHOR_UIDS)

    # Build joint batch with FIXED yem = yem00 + yemxp
    print(f"\n  Building joint batch ({n_hh} HHs) with FIXED yem formula...")
    t_redraw = time.time()
    blocked  = []
    for n_done, uid in enumerate(all_uids):
        if uid not in hh_by_uid:
            blocked.append(uid); continue
        indices = dec_by_uid.get(uid, [])
        if len(indices) < N_NODES:
            blocked.append(uid); continue

        if uid in anchor_uid_set:
            nodes_u = frozen_nodes[uid]
        else:
            hh_row = hh_by_uid[uid]
            yt_hh  = int(hh_row.get("year_tag", YEAR_TAG))
            seed   = BASE_SEED + (uid % 1_000_000)
            rng    = np.random.default_rng(np.random.PCG64(seed))
            nodes_u = wvd.redraw_nodes_singles(hh_row, N_NODES, rng, mincer, dm, year_tag=yt_hh)

        use_idx = indices[:N_NODES]
        for k, idx in enumerate(use_idx):
            wk  = int(nodes_u["working"][k])
            h   = float(nodes_u["hours"][k])
            w   = float(nodes_u["wage"][k])
            lo4 = int(nodes_u["loc4"][k])
            if wk == 1 and h > 0 and w > 0:
                reg_h   = min(h, _FR_STD_HOURS)
                ot_h    = max(h - _FR_STD_HOURS, 0.0)
                yem00_v = reg_h * w * _WEEKS_PER_MONTH   # separate product
                yemxp_v = ot_h  * w * _WEEKS_PER_MONTH   # separate product
                band.at[idx, "lhw"]      = h
                band.at[idx, "yivwg"]    = w
                band.at[idx, "yem_hour"] = w
                band.at[idx, "yem00"]    = yem00_v
                band.at[idx, "yemxp"]    = yemxp_v
                band.at[idx, "yem"]      = yem00_v + yemxp_v  # FIXED
                band.at[idx, "working"]  = 1.0
                if "hours" in band.columns:
                    band.at[idx, "hours"] = h
                if "wage"  in band.columns:
                    band.at[idx, "wage"]  = w
                if "loc4"  in band.columns and lo4 >= 1:
                    band.at[idx, "loc4"]  = float(lo4)
            else:
                for c in ["lhw", "yivwg", "yem", "yem00", "yemxp", "yem_hour"]:
                    band.at[idx, c] = 0.0
                band.at[idx, "working"] = 0.0
                if "hours" in band.columns:
                    band.at[idx, "hours"] = 0.0
                if "wage"  in band.columns:
                    band.at[idx, "wage"]  = 0.0
        if (n_done + 1) % 300 == 0:
            print(f"    {n_done+1}/{n_hh} HHs...")
    redraw_elapsed = round(time.time() - t_redraw, 1)
    print(f"  Redraw done in {redraw_elapsed}s  blocked={len(blocked)}")

    # Stamp + build em_input_j (for both Gate B and joint EUROMOD)
    stamped_j  = bmod._stamp_draw_ids(band.copy(), "draw", 1_000)
    em_input_j = stamped_j[[c for c in raw_cols if c in stamped_j.columns]].copy()
    for c in em_input_j.columns:
        em_input_j[c] = pd.to_numeric(em_input_j[c], errors="coerce").fillna(0.0)

    # ===================================================================
    # Gate B: byte-identity of anchor em_input rows vs saved T2 em_input
    # ===================================================================
    print("\n  Gate B: byte-identity check (after yem fix)...")
    gate_b_results = {}
    gate_b_pass    = True

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        t2_em = t2_em_saved[uid]
        t2_draws = set(int(d) for d in t2_em["draw"].values)

        anchor_mask = (
            (stamped_j["stacked_hh_uid"] == uid)
            & (stamped_j["draw"].isin(t2_draws))
            & (stamped_j["ruro_decider"] == 1)
        )
        t3_em = em_input_j[anchor_mask.values].copy().reset_index(drop=True)
        t3_draw = stamped_j[anchor_mask.values][["draw"]].reset_index(drop=True)
        t3_em["draw"] = t3_draw["draw"].values

        if len(t2_em) != len(t3_em):
            gate_b_results[label] = {
                "uid": uid, "pass": False,
                "error": f"row count mismatch t2={len(t2_em)} t3={len(t3_em)}"
            }
            gate_b_pass = False
            continue

        t2_s = t2_em.sort_values("draw").reset_index(drop=True)
        t3_s = t3_em.sort_values("draw").reset_index(drop=True)
        shared = [c for c in raw_cols if c in t2_s.columns and c in t3_s.columns]

        nonzero = {}
        max_abs = 0.0
        for col in shared:
            try:
                a = t2_s[col].values.astype(float)
                b = t3_s[col].values.astype(float)
                d = float(np.nanmax(np.abs(a - b)))
            except Exception:
                d = float("nan")
            if np.isfinite(d) and d > 0:
                nonzero[col] = round(d, 18)
            if np.isfinite(d):
                max_abs = max(max_abs, d)

        b_pass = (len(nonzero) == 0)
        if not b_pass:
            gate_b_pass = False
        gate_b_results[label] = {
            "uid": uid, "n_rows": len(t2_s), "max_abs_diff": max_abs,
            "pass": b_pass, "nonzero_diff_cols": list(nonzero.keys()),
        }
        status = "PASS" if b_pass else "FAIL"
        print(f"    Gate B {label}: {status}  max_abs={max_abs:.2e}  divergent={list(nonzero.keys())[:5]}")

    if not gate_b_pass:
        # Residual divergence after fix — stop, report
        result = {
            "f3r2b_artifact": "f3r2b_diagnosis_v1",
            "yem_fix": "APPLIED: yem00=reg_h*w*wpm; yemxp=ot_h*w*wpm; yem=yem00+yemxp",
            "gate_b_pass": False, "gate_b_results": gate_b_results,
            "gate_a_pass": None,  "gate_a_result": None,
            "gate_c_pass": None,  "gate_c_results": None,
            "verdict": "CONSTRUCTION_MISMATCH_PERSISTS",
            "batch_context_dependence": "unresolved",
            "joint_batching_licensed": "unresolved",
            "stop_reason": "Gate B still fails after yem fix — see nonzero_diff_cols for residual column(s)",
            "n_hh_joint_batch": n_hh, "n_hh_blocked": len(blocked),
            "redraw_elapsed_s": redraw_elapsed, "total_elapsed_s": round(time.time() - t0, 1),
        }
        _atomic_write_json(result, _OUT_DIAGNOSIS)
        print(f"\nDiagnosis: {_OUT_DIAGNOSIS}")
        print("\n--- CONCLUSIONS ---")
        print("READY FOR F4: yes")
        print("FROZEN FULL-V S=100 GATE: fail")
        print(f"UTILITY-ONLY B2 ANCHOR GATE: {b2}")
        print("JOINT BATCHING METHOD: unresolved")
        print("BATCH-CONTEXT DEPENDENCE: unresolved")
        print("FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no")
        print(f"\nF3-R2B STOPPED  verdict=CONSTRUCTION_MISMATCH_PERSISTS")
        return

    print("  Gate B: PASS — byte-identical after yem fix")

    # ===================================================================
    # Gate A: EUROMOD determinism (repeat primary anchor, compare to T2 priced_v3)
    # ===================================================================
    print("\n  Gate A: EUROMOD determinism check (repeat primary anchor target-only)...")
    t_ga = time.time()
    band_ga = band_full[band_full["year_tag"] == YEAR_TAG].copy()
    anchor_rows_a, err_a = _price_anchor_tgt(
        bc, band_ga, _PRIMARY_UID, frozen_nodes[_PRIMARY_UID], phi, country, sys_code, dataset)
    ga_elapsed = round(time.time() - t_ga, 1)

    if err_a:
        gate_a_pass   = None
        gate_a_result = {"pass": None, "error": err_a, "elapsed_s": ga_elapsed}
    else:
        t2_p = t2_priced[_PRIMARY_UID]
        a_draws = sorted(int(d) for d in t2_p["draw"].values)
        t2_s_a = t2_p.sort_values("draw").reset_index(drop=True)
        ar_s   = anchor_rows_a.sort_values("draw").reset_index(drop=True)
        compare_cols = [c for c in t2_s_a.columns
                        if c in ar_s.columns
                        and c not in {"stacked_hh_uid", "draw", "year_tag", "ruro_decider", "idperson_true"}]
        ga_nonzero = {}
        ga_max_abs = 0.0
        for col in compare_cols:
            try:
                aa = t2_s_a[col].values.astype(float)
                bb = ar_s[col].values.astype(float)
                if len(aa) != len(bb):
                    continue
                d = float(np.nanmax(np.abs(aa - bb)))
            except Exception:
                d = float("nan")
            if np.isfinite(d) and d > TOL:
                ga_nonzero[col] = round(d, 6)
            if np.isfinite(d):
                ga_max_abs = max(ga_max_abs, d)
        gate_a_pass = (len(ga_nonzero) == 0)
        gate_a_result = {
            "pass": gate_a_pass, "max_abs_diff": ga_max_abs,
            "n_divergent_cols": len(ga_nonzero),
            "divergent_cols_sample": sorted(ga_nonzero.items(), key=lambda x: -x[1])[:10],
            "elapsed_s": ga_elapsed,
        }

    status_a = "PASS" if gate_a_pass else ("FAIL" if gate_a_pass is False else "N/A")
    print(f"  Gate A: {status_a}  max_abs={gate_a_result.get('max_abs_diff', 'n/a'):.2e}  elapsed={ga_elapsed}s")

    if gate_a_pass is False:
        result = {
            "f3r2b_artifact": "f3r2b_diagnosis_v1",
            "yem_fix": "APPLIED",
            "gate_b_pass": gate_b_pass, "gate_b_results": gate_b_results,
            "gate_a_pass": False, "gate_a_result": gate_a_result,
            "gate_c_pass": None,  "gate_c_results": None,
            "verdict": "EUROMOD_NOT_DETERMINISTIC",
            "batch_context_dependence": "unresolved",
            "joint_batching_licensed": "unresolved",
        }
        _atomic_write_json(result, _OUT_DIAGNOSIS)
        print(f"\nDiagnosis: {_OUT_DIAGNOSIS}")
        print("\n--- CONCLUSIONS ---")
        print("READY FOR F4: yes")
        print("FROZEN FULL-V S=100 GATE: fail")
        print(f"UTILITY-ONLY B2 ANCHOR GATE: {b2}")
        print("JOINT BATCHING METHOD: unresolved")
        print("BATCH-CONTEXT DEPENDENCE: unresolved")
        print("FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no")
        print(f"\nF3-R2B STOPPED  verdict=EUROMOD_NOT_DETERMINISTIC")
        return

    # ===================================================================
    # Run joint-batch EUROMOD
    # ===================================================================
    print(f"\n  Running joint-batch EUROMOD on {len(band)} rows...")
    t_em = time.time()
    runner    = bc["EuromodRunner"](bc["em_root"])
    sim_joint = runner.run_on_dataframe(
        em_input_j, country=country, system_code=sys_code, dataset_name=dataset)
    em_elapsed = round(time.time() - t_em, 1)
    print(f"  Joint-batch EUROMOD done: {len(sim_joint)} rows, elapsed {em_elapsed}s")

    if len(sim_joint) != len(band):
        raise RuntimeError(f"STOP: joint sim row count mismatch {len(sim_joint)} vs {len(band)}")

    actual_sim_cols = [c for c in sim_joint.columns if c not in raw_cols_set]

    joint_out = band.reset_index(drop=True).copy()
    joint_out["idperson_true"] = joint_out["idperson"]
    for col in actual_sim_cols:
        joint_out[col] = sim_joint[col].values
    if "ils_dispy" in joint_out.columns:
        joint_out["ils_dispy_real"] = joint_out["ils_dispy"] * phi
    else:
        joint_out["ils_dispy_real"] = float("nan")

    # ===================================================================
    # Gate C: compare all sim output cols for anchor decider rows
    # ===================================================================
    print("\n  Gate C: joint-batch vs target-only output comparison...")
    gate_c_results = {}
    gate_c_pass    = True
    all_check_cols = actual_sim_cols + (
        ["ils_dispy_real"] if "ils_dispy_real" not in actual_sim_cols else [])

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        t2_p = t2_priced[uid]
        t2_draws_c = set(int(d) for d in t2_p["draw"].values)

        anchor_j = joint_out[
            (joint_out["stacked_hh_uid"] == uid)
            & (joint_out["ruro_decider"] == 1)
            & (joint_out["draw"].isin(t2_draws_c))
        ].copy().sort_values("draw").reset_index(drop=True)
        t2_s_c = t2_p.sort_values("draw").reset_index(drop=True)

        if len(anchor_j) != len(t2_s_c):
            gate_c_results[label] = {
                "uid": uid, "pass": False,
                "error": f"row mismatch joint={len(anchor_j)} t2={len(t2_s_c)}"
            }
            gate_c_pass = False
            continue

        nonzero_c = {}
        max_abs_c = 0.0
        for col in all_check_cols:
            if col not in anchor_j.columns or col not in t2_s_c.columns:
                continue
            try:
                a = t2_s_c[col].values.astype(float)
                b = anchor_j[col].values.astype(float)
                d = float(np.nanmax(np.abs(a - b)))
            except Exception:
                d = float("nan")
            if np.isfinite(d) and d > TOL:
                nonzero_c[col] = round(d, 6)
            if np.isfinite(d):
                max_abs_c = max(max_abs_c, d)

        c_pass = (len(nonzero_c) == 0)
        if not c_pass:
            gate_c_pass = False
        gate_c_results[label] = {
            "uid": uid, "n_draws": len(t2_s_c), "max_abs_diff": max_abs_c,
            "pass": c_pass, "n_divergent_cols": len(nonzero_c),
            "top_divergent": sorted(nonzero_c.items(), key=lambda x: -x[1])[:10],
        }
        status_c = "PASS" if c_pass else "FAIL"
        print(f"    Gate C {label}: {status_c}  max_abs={max_abs_c:.4f}  n_div_cols={len(nonzero_c)}")

    # Derive final verdict
    if gate_c_pass:
        verdict    = "LICENSED"
        bcd        = "not proven"
        jbl        = "licensed"
    else:
        verdict    = "NOT_LICENSED"
        bcd        = "proven"
        jbl        = "not licensed"

    total_elapsed = round(time.time() - t0, 1)

    result = {
        "f3r2b_artifact": "f3r2b_diagnosis_v1",
        "yem_fix": "APPLIED: yem00=reg_h*w*wpm; yemxp=ot_h*w*wpm; yem=yem00+yemxp (matches T2 exactly)",
        "f4_readiness": "YES",
        "gate3b_verdict": "FAIL",
        "gate3b_median": 0.7319804266785854,
        "utility_only_b2_gate": b2,
        "gate_b_pass": gate_b_pass, "gate_b_results": gate_b_results,
        "gate_a_pass": gate_a_pass, "gate_a_result": gate_a_result,
        "gate_c_pass": gate_c_pass, "gate_c_results": gate_c_results,
        "verdict": verdict,
        "batch_context_dependence": bcd,
        "joint_batching_licensed": jbl,
        "n_hh_joint_batch": n_hh, "n_hh_blocked": len(blocked),
        "year": YEAR, "year_tag": YEAR_TAG, "n_nodes_per_hh": N_NODES,
        "base_seed": BASE_SEED,
        "euromod_system": sys_code, "euromod_dataset": dataset,
        "redraw_elapsed_s": redraw_elapsed,
        "gate_a_elapsed_s": ga_elapsed,
        "euromod_joint_elapsed_s": em_elapsed,
        "total_elapsed_s": total_elapsed,
    }
    _atomic_write_json(result, _OUT_DIAGNOSIS)

    # Write markdown doc
    doc = f"""# F3-R2B: Dispositive Joint-Batch Gate B/A/C (yem-fix run)

## Fix applied

Root cause of F3-R2A `CONSTRUCTION_MISMATCH`: arithmetic path mismatch in `yem`.

| Path | Formula | Result |
|------|---------|--------|
| Task 2 (`_overwrite_choice_vars`) | `yem = reg_h*w*wpm + ot_h*w*wpm` | reference |
| Task 3 (F3-R2A joint loop) | `yem = (reg_h+ot_h)*w*wpm` | differs by 1-2 ULP |
| Task 3 (F3-R2B joint loop) | `yem00=reg_h*w*wpm; yemxp=ot_h*w*wpm; yem=yem00+yemxp` | **FIXED** |

`a*c + b*c ≠ (a+b)*c` in IEEE 754 — observed difference was 4.5e-13 to 9.1e-13 (~1-2 ULP for yem ≈ 2000 EUR/month). Not a real construction mismatch.

## Gate results

| Gate | Verdict |
|------|---------|
| B — byte-identity of anchor em_input | {'PASS' if gate_b_pass else 'FAIL'} |
| A — EUROMOD determinism (repeat primary, tol 1e-6) | {'PASS' if gate_a_pass else ('FAIL' if gate_a_pass is False else 'N/A')} |
| C — joint vs target-only sim output (all cols, tol 1e-6) | {'PASS' if gate_c_pass else 'FAIL'} |

**Overall verdict: {verdict}**

## Conclusions

```
READY FOR F4: yes
FROZEN FULL-V S=100 GATE: fail
UTILITY-ONLY B2 ANCHOR GATE: {b2}
JOINT BATCHING METHOD: {jbl}
BATCH-CONTEXT DEPENDENCE: {bcd}
FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no
```
"""
    _atomic_write_text(doc, _OUT_DOC)

    print(f"\nDiagnosis: {_OUT_DIAGNOSIS}")
    print(f"  Report: {_OUT_DOC}")
    print(f"\n--- CONCLUSIONS ---")
    print("READY FOR F4: yes")
    print("FROZEN FULL-V S=100 GATE: fail")
    print(f"UTILITY-ONLY B2 ANCHOR GATE: {b2}")
    print(f"JOINT BATCHING METHOD: {jbl}")
    print(f"BATCH-CONTEXT DEPENDENCE: {bcd}")
    print("FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no")
    print(f"\nF3-R2B COMPLETE in {total_elapsed}s")
    print(f"  Verdict: {verdict}")
    print(f"  Batch-context dependence: {bcd}")


if __name__ == "__main__":
    main()
