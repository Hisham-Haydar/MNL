"""
D-BEN: Program-level decomposition of the Two-L / F3 benefit wobble.

READ-ONLY FORENSIC. No welfare, no decomposition, no V_i, no estimation, no
EUROMOD SYSTEM edits, no fix applied, no promotion, no commit.

Purpose: attribute the F3 joint-batch `ils_ben` divergence (EUR 127-310 on
means-tested benefits, F3-R2/F3-R2B) to SPECIFIC ils_benmt programs, and classify
each moving program INCOME-DRIVEN vs DEMOGRAPHIC-ARTIFACT, WITHIN- vs CROSS-household.

The contrast (identical to F3-R2B Gate C):
  batch-A = TARGET-ONLY  (each HH priced individually; the production geometry / "stored").
            Source: frozen fastlane_anchors_v3/*_priced_v3.parquet (Gate A proved
            re-run == stored at max_abs=0, so priced_v3 is the faithful target-only run).
  batch-B = JOINT-BATCH  (anchor priced inside the full 1676 HH x 100 draw = 169,276-row
            batch). Re-run here, deterministically, with the F3-R2B FIXED yem formula.

Outputs (atomic; never overwrites immutable F3/F3-R2 artifacts):
  outputs/welfare/fastlane/diag_dben_program_attribution_v1.parquet
  docs/jmp_methodology/RURO_welfare_DBEN_benefit_program_diagnosis_v1.md  (written separately)
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
# constants (identical to F3-R2B)
# ---------------------------------------------------------------------------
BASE_SEED        = 20260604
YEAR             = 2016
YEAR_TAG         = 2
N_NODES          = 100
_FR_STD_HOURS    = 35.0
_WEEKS_PER_MONTH = 52.0 / 12.0
TOL              = 1e-6          # batch-sensitivity threshold (EUR)
TOL_VAR          = 1e-6          # within-draw variation threshold (EUR)

_PRIMARY_UID    = 200001593700
_TOP_ESS_SM_UID = 200003504101
_TOP_ESS_SF_UID = 200003672000
_ANCHOR_UIDS    = [_PRIMARY_UID, _TOP_ESS_SM_UID, _TOP_ESS_SF_UID]
_ANCHOR_LABELS  = ["primary", "top_ess_sm_2016", "top_ess_sf_2016"]

_AV3_DIR  = _REPO / "outputs/welfare/fastlane_anchors_v3"
_CONFIG   = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"

_OUT_DIR     = _REPO / "outputs/welfare/fastlane"
_OUT_PARQUET = _OUT_DIR / "diag_dben_program_attribution_v1.parquet"
_OUT_JSON    = _OUT_DIR / "diag_dben_program_attribution_v1_summary.json"

# ils_benmt component programs present in EUROMOD FR output (simulated *_s amounts).
# Names per the operator's list; EUROMOD program -> French scheme.
PROGRAMS = {
    "bsa00_s":   "RSA (revenu de solidarite active) - means-tested income floor",
    "bhotn_s":   "AL (aide au logement) - means-tested housing benefit",
    "bunmt_s":   "ASS (allocation de solidarite specifique) - means-tested unemployment",
    "tinrf_s":   "PPE (prime pour l'emploi) - in-work means-tested transfer",
    "bdi_s":     "AAH (allocation adulte handicape) - disability (income-tested)",
    "bched_s":   "ARS (allocation de rentree scolaire) - school-start (income-tested)",
    "bchyc_s":   "PAJE (prestation accueil jeune enfant) - young-child",
    "bchlg_s":   "CF (complement familial) - family complement",
    "bchba_s":   "PN / birth-grant family line",
    "bsaoa_s":   "ASPA (minimum vieillesse) - old-age minimum",
    "bsuwd_s":   "AV / supplementary line",
    "bch00_s":   "AF (allocations familiales) - family allowance (demographic)",
    "bchot_s":   "other child line",
    "bchor_s":   "other child line",
    "bchcc_s":   "complement de libre choix / childcare line",
    "bunct_s":   "contributory unemployment line",
    "bunctmy_s": "contributory unemployment (monthly) line",
}
PROGRAM_COLS = list(PROGRAMS.keys())

AGG_COLS = ["ils_benmt", "ils_bennt", "ils_pen", "ils_ben", "ils_dispy"]

# bsa00 internal accumulators — used as MECHANISM EVIDENCE (cross-household leakage).
ACC_COLS = [
    "i_bsa00_cumpers_nw", "i_bsa00_cumpers_w", "i_bsa00_cumpers",
    "i_bsa00_cumexp", "i_bsa00_amt", "i_bsa00_faminc", "i_bsa00_wkinc",
    "i_bsa00_elig", "i_bsa00_elig_w", "i_bsa00_elig_nw",
]


def _atomic_write_parquet(df: pd.DataFrame, dest: Path):
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


def _atomic_write_json(obj, dest: Path):
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


def _system_pairing(bc):
    system_code, dataset_name = bc["system_pairing"][YEAR]
    return system_code[:2], system_code, dataset_name


def main():
    t0 = time.time()
    print("D-BEN start  (read-only program-level attribution)")

    # -- Load frozen TARGET-ONLY (batch-A / stored) priced artifacts -----------
    print("\n  Loading frozen target-only priced_v3 (batch-A / stored)...")
    frozen_nodes, t2_priced = {}, {}
    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        nodes_pq  = _AV3_DIR / f"anchor_{label}_uid{uid}_nodes_v3.parquet"
        priced_pq = _AV3_DIR / f"anchor_{label}_uid{uid}_priced_v3.parquet"
        for p in (nodes_pq, priced_pq):
            if not p.exists():
                raise RuntimeError(f"STOP: missing frozen artifact: {p}")
        ndf = pd.read_parquet(nodes_pq)
        frozen_nodes[uid] = {
            "working": ndf["working"].to_numpy().astype(np.int8),
            "hours":   ndf["hours"].to_numpy().astype(np.float64),
            "wage":    ndf["wage"].to_numpy().astype(np.float64),
            "loc4":    ndf["loc4"].to_numpy().astype(np.int32),
        }
        t2_priced[uid] = pd.read_parquet(priced_pq)
        print(f"    {label} uid={uid}: priced_rows={len(t2_priced[uid])}")

    # -- Constants / machinery -------------------------------------------------
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

    dec_mask = (band["ruro_decider"] == 1) & (band["draw"] >= 1)
    dec_df   = band[dec_mask][["stacked_hh_uid", "draw"]].copy()
    dec_df["_idx"] = dec_df.index
    dec_by_uid = {int(u): grp.sort_values("draw")["_idx"].tolist()
                  for u, grp in dec_df.groupby("stacked_hh_uid")}
    hh0_rows  = band[(band["ruro_decider"] == 1) & (band["draw"] == 0)]
    hh_by_uid = {int(r["stacked_hh_uid"]): r.to_dict() for _, r in hh0_rows.iterrows()}
    anchor_uid_set = set(_ANCHOR_UIDS)

    # -- Build joint batch (FIXED yem = yem00+yemxp) ---------------------------
    print(f"\n  Building joint batch ({n_hh} HHs) with FIXED yem formula...")
    t_redraw = time.time()
    blocked = []
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
                yem00_v = reg_h * w * _WEEKS_PER_MONTH
                yemxp_v = ot_h  * w * _WEEKS_PER_MONTH
                band.at[idx, "lhw"]      = h
                band.at[idx, "yivwg"]    = w
                band.at[idx, "yem_hour"] = w
                band.at[idx, "yem00"]    = yem00_v
                band.at[idx, "yemxp"]    = yemxp_v
                band.at[idx, "yem"]      = yem00_v + yemxp_v
                band.at[idx, "working"]  = 1.0
                if "hours" in band.columns: band.at[idx, "hours"] = h
                if "wage"  in band.columns: band.at[idx, "wage"]  = w
                if "loc4"  in band.columns and lo4 >= 1: band.at[idx, "loc4"] = float(lo4)
            else:
                for c in ["lhw", "yivwg", "yem", "yem00", "yemxp", "yem_hour"]:
                    band.at[idx, c] = 0.0
                band.at[idx, "working"] = 0.0
                if "hours" in band.columns: band.at[idx, "hours"] = 0.0
                if "wage"  in band.columns: band.at[idx, "wage"]  = 0.0
        if (n_done + 1) % 400 == 0:
            print(f"    {n_done+1}/{n_hh} HHs...")
    redraw_elapsed = round(time.time() - t_redraw, 1)
    print(f"  Redraw done in {redraw_elapsed}s  blocked={len(blocked)}")

    stamped_j  = bmod._stamp_draw_ids(band.copy(), "draw", 1_000)
    em_input_j = stamped_j[[c for c in raw_cols if c in stamped_j.columns]].copy()
    for c in em_input_j.columns:
        em_input_j[c] = pd.to_numeric(em_input_j[c], errors="coerce").fillna(0.0)

    # -- Run joint-batch EUROMOD (batch-B) -------------------------------------
    print(f"\n  Running joint-batch EUROMOD on {len(band)} rows...")
    t_em = time.time()
    runner    = bc["EuromodRunner"](bc["em_root"])
    sim_joint = runner.run_on_dataframe(
        em_input_j, country=country, system_code=sys_code, dataset_name=dataset)
    em_elapsed = round(time.time() - t_em, 1)
    print(f"  Joint EUROMOD done: {len(sim_joint)} rows, elapsed {em_elapsed}s")
    if len(sim_joint) != len(band):
        raise RuntimeError(f"STOP: joint sim row mismatch {len(sim_joint)} vs {len(band)}")

    actual_sim_cols = [c for c in sim_joint.columns if c not in raw_cols_set]
    joint_out = band.reset_index(drop=True).copy()
    for col in actual_sim_cols:
        joint_out[col] = sim_joint[col].values

    # -- TASK 0: reproduce the failing contrast on anchor decider nodes --------
    # -- TASK 1/2/3: per-program per-node attribution & classification ---------
    all_track = PROGRAM_COLS + AGG_COLS + ACC_COLS
    long_rows = []
    repro = {}

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        t2_p = t2_priced[uid].sort_values("draw").reset_index(drop=True)
        t2_draws = set(int(d) for d in t2_p["draw"].values)
        anchor_j = joint_out[
            (joint_out["stacked_hh_uid"] == uid)
            & (joint_out["ruro_decider"] == 1)
            & (joint_out["draw"].isin(t2_draws))
        ].copy().sort_values("draw").reset_index(drop=True)

        if len(anchor_j) != len(t2_p):
            raise RuntimeError(f"STOP: anchor {label} row mismatch joint={len(anchor_j)} t2={len(t2_p)}")

        draws = t2_p["draw"].astype(int).values
        dispy_t = (t2_p["ils_dispy"].values.astype(float)
                   if "ils_dispy" in t2_p.columns else np.full(len(t2_p), np.nan))

        # Task-0 reproduction: the headline ils_ben divergence on this anchor
        ben_t = t2_p["ils_ben"].values.astype(float)
        ben_j = anchor_j["ils_ben"].values.astype(float)
        repro[label] = {
            "uid": uid,
            "ils_ben_max_abs_diff": float(np.nanmax(np.abs(ben_j - ben_t))),
            "ils_ben_n_nodes_above_tol": int(np.sum(np.abs(ben_j - ben_t) > TOL)),
        }

        for col in all_track:
            if col not in t2_p.columns or col not in anchor_j.columns:
                continue
            vt = t2_p[col].values.astype(float)       # target-only (batch-A/stored)
            vj = anchor_j[col].values.astype(float)   # joint (batch-B)
            d  = vj - vt
            within_var = float(np.nanstd(vt))         # variation across draws, faithful run
            for i in range(len(draws)):
                long_rows.append({
                    "anchor": label, "uid": uid, "draw": int(draws[i]),
                    "program": col,
                    "val_target_only": float(vt[i]),   # batch-A == stored
                    "val_joint_batch": float(vj[i]),   # batch-B
                    "abs_diff": float(abs(d[i])),
                    "signed_diff": float(d[i]),
                    "ils_dispy_target": float(dispy_t[i]),
                    "within_draw_std_targetonly": within_var,
                })

    long_df = pd.DataFrame(long_rows)

    # -- Program-level rollup & classification ---------------------------------
    prog_summ = []
    # total ils_ben divergence magnitude (per anchor max), for share computation
    ben_div_per_anchor = {lab: repro[lab]["ils_ben_max_abs_diff"] for lab in _ANCHOR_LABELS}

    for col in all_track:
        sub = long_df[long_df["program"] == col]
        if sub.empty:
            continue
        max_abs = float(sub["abs_diff"].max())
        med_abs = float(sub["abs_diff"].median())
        n_above = int((sub["abs_diff"] > TOL).sum())
        # within-draw variation: max std across the three anchors (target-only run)
        within_std = float(sub.groupby("anchor")["within_draw_std_targetonly"].first().max())
        within_varies = bool(within_std > TOL_VAR)
        batch_sensitive = bool(max_abs > TOL)
        is_program = col in PROGRAM_COLS

        if batch_sensitive and within_varies:
            cls = "INCOME-DRIVEN"
        elif batch_sensitive and not within_varies:
            cls = "DEMOGRAPHIC-ARTIFACT"
        elif (not batch_sensitive) and within_varies:
            cls = "inert (income-linked, not batch-sensitive)"
        else:
            cls = "inert"

        # share of the ils_ben divergence (use program max-abs / anchor ils_ben max-abs, max over anchors)
        shares = []
        for lab in _ANCHOR_LABELS:
            den = ben_div_per_anchor[lab]
            num = float(sub[sub["anchor"] == lab]["abs_diff"].max()) if not sub[sub["anchor"] == lab].empty else 0.0
            shares.append(num / den if den > TOL else 0.0)
        share_of_ben = float(np.max(shares)) if is_program else None

        prog_summ.append({
            "program": col,
            "is_benmt_program": is_program,
            "is_aggregate": col in AGG_COLS,
            "is_accumulator": col in ACC_COLS,
            "max_abs_diff": max_abs,
            "median_abs_diff": med_abs,
            "n_nodes_above_tol": n_above,
            "within_draw_std_targetonly": within_std,
            "within_draw_varies": within_varies,
            "batch_sensitive": batch_sensitive,
            "share_of_ils_ben_div": share_of_ben,
            "classification": cls,
        })

    summ_df = pd.DataFrame(prog_summ).sort_values("max_abs_diff", ascending=False).reset_index(drop=True)

    # row-kind metadata so the parquet is self-describing (programs vs aggregates vs
    # accumulators): an accumulator/aggregate row is a MECHANISM/closure carrier, NOT a
    # benefit program — downstream code must filter on is_benmt_program for attribution.
    long_df["is_benmt_program"] = long_df["program"].isin(PROGRAM_COLS)
    long_df["is_aggregate"]     = long_df["program"].isin(AGG_COLS)
    long_df["is_accumulator"]   = long_df["program"].isin(ACC_COLS)

    # attach program-level flags back onto the long table
    flag_map = summ_df.set_index("program")[["within_draw_varies", "batch_sensitive", "classification"]].to_dict("index")
    long_df["within_draw_varies"] = long_df["program"].map(lambda c: flag_map.get(c, {}).get("within_draw_varies"))
    long_df["batch_sensitive"]    = long_df["program"].map(lambda c: flag_map.get(c, {}).get("batch_sensitive"))
    long_df["classification"]     = long_df["program"].map(lambda c: flag_map.get(c, {}).get("classification"))
    long_df["frac_of_dispy"] = long_df.apply(
        lambda r: (r["abs_diff"] / abs(r["ils_dispy_target"])) if abs(r["ils_dispy_target"]) > TOL else np.nan, axis=1)

    _atomic_write_parquet(long_df, _OUT_PARQUET)

    # -- Closure check: sum of moving program diffs == ils_benmt diff == ils_ben diff
    closure = {}
    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        t2_p = t2_priced[uid].sort_values("draw").reset_index(drop=True)
        anchor_j = joint_out[
            (joint_out["stacked_hh_uid"] == uid)
            & (joint_out["ruro_decider"] == 1)
            & (joint_out["draw"].isin(set(int(d) for d in t2_p["draw"].values)))
        ].copy().sort_values("draw").reset_index(drop=True)
        prog_diff_sum = np.zeros(len(t2_p))
        for col in PROGRAM_COLS:
            if col in t2_p.columns and col in anchor_j.columns:
                prog_diff_sum += (anchor_j[col].values.astype(float) - t2_p[col].values.astype(float))
        benmt_diff = (anchor_j["ils_benmt"].values.astype(float) - t2_p["ils_benmt"].values.astype(float))
        ben_diff   = (anchor_j["ils_ben"].values.astype(float)   - t2_p["ils_ben"].values.astype(float))
        bennt_diff = (anchor_j["ils_bennt"].values.astype(float) - t2_p["ils_bennt"].values.astype(float))
        pen_diff   = (anchor_j["ils_pen"].values.astype(float)   - t2_p["ils_pen"].values.astype(float))
        closure[label] = {
            "sum_program_diffs_max_abs": float(np.max(np.abs(prog_diff_sum))),
            "ils_benmt_diff_max_abs":    float(np.max(np.abs(benmt_diff))),
            "ils_ben_diff_max_abs":      float(np.max(np.abs(ben_diff))),
            "closure_residual_programs_vs_benmt": float(np.max(np.abs(prog_diff_sum - benmt_diff))),
            "closure_residual_benmt_vs_ben":      float(np.max(np.abs(benmt_diff - ben_diff))),
            "ils_bennt_diff_max_abs":    float(np.max(np.abs(bennt_diff))),
            "ils_pen_diff_max_abs":      float(np.max(np.abs(pen_diff))),
        }

    summary = {
        "diag": "diag_dben_program_attribution_v1",
        "read_only": True, "no_commit": True,
        "contrast": "batch-A=target-only (priced_v3, stored/production) vs batch-B=joint-batch (169276 rows)",
        "n_hh_joint_batch": n_hh, "n_hh_blocked": len(blocked),
        "year": YEAR, "n_nodes_per_hh": N_NODES, "base_seed": BASE_SEED,
        "euromod_system": sys_code, "euromod_dataset": dataset,
        "task0_reproduce": repro,
        "closure": closure,
        "program_summary": summ_df.to_dict("records"),
        "redraw_elapsed_s": redraw_elapsed,
        "euromod_joint_elapsed_s": em_elapsed,
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    _atomic_write_json(summary, _OUT_JSON)

    # -- console report --------------------------------------------------------
    print("\n==== TASK 0: reproduce failing contrast ====")
    for lab in _ANCHOR_LABELS:
        print(f"  {lab}: ils_ben max|diff| = {repro[lab]['ils_ben_max_abs_diff']:.6f} EUR "
              f"({repro[lab]['ils_ben_n_nodes_above_tol']} nodes > tol)")

    print("\n==== TASK 1: ranked per-program attribution (movers) ====")
    movers = summ_df[(summ_df["max_abs_diff"] > TOL)]
    print(f"  {'program':22s} {'max|diff|':>14s} {'med|diff|':>12s} {'n>tol':>6s} {'class':>22s}")
    for _, r in movers.iterrows():
        print(f"  {r['program']:22s} {r['max_abs_diff']:14.4f} {r['median_abs_diff']:12.4f} "
              f"{r['n_nodes_above_tol']:6d} {r['classification']:>22s}")

    print("\n==== CLOSURE ====")
    for lab in _ANCHOR_LABELS:
        c = closure[lab]
        print(f"  {lab}: sum(prog)-benmt residual={c['closure_residual_programs_vs_benmt']:.2e}  "
              f"benmt-ben residual={c['closure_residual_benmt_vs_ben']:.2e}  "
              f"bennt|diff|={c['ils_bennt_diff_max_abs']:.2e}  pen|diff|={c['ils_pen_diff_max_abs']:.2e}")

    print(f"\n  Parquet: {_OUT_PARQUET}")
    print(f"  Summary JSON: {_OUT_JSON}")
    print(f"\nD-BEN done in {round(time.time()-t0,1)}s")


if __name__ == "__main__":
    main()
