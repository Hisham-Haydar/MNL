"""
F3-R2A: Repair F3-R2 Evidence + Dispositive Joint-Batch Diagnosis.

Authorized by the F3-R2A prompt. All F3 and F3-R2 artifacts are immutable.

Tasks:
  1 - Repair metadata: Gate-3b FAIL confirmed, F4 readiness corrected to YES
  2 - Complete durable anchor evidence (v3): frozen nodes + ALL sim cols + V_dir diagnostics
  3 - Dispositive joint-batch diagnosis using exact frozen Task-2 node tables
  4 - Final corrected report

Constraints:
  - No edits to engines, specs, data, existing welfare scripts, or existing F3/F3-R2 artifacts
  - Atomic writes only (temp -> validate -> rename)
  - Never overwrite F3 or F3-R2 immutable artifacts
  - No commit
"""
from __future__ import annotations

import hashlib
import json
import sys
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

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

import estimation_spec_parser as sp
import welfare_core as wc
import welfare_vdir as wvd
import yaml
from _bpool_paths import bpool_dir

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
BASE_SEED           = 20260604
YEAR                = 2016
YEAR_TAG            = 2
N_NODES             = 100
N_DRAWS_EXISTING    = 101       # draws 0..100 in staged parquet
_FR_STD_HOURS       = 35.0
_WEEKS_PER_MONTH    = 52.0 / 12.0
TOTAL_LEISURE_HOURS = 80.0
DCM_MIN_POSITIVE    = 1.0
C_SCALE             = 2034.988978049439
L_SCALE             = 10.0
TOL                 = 1e-6

# Pre-registered anchor UIDs (from F3 manifest / F3-R2)
_PRIMARY_UID    = 200001593700
_TOP_ESS_SM_UID = 200003504101
_TOP_ESS_SF_UID = 200003672000
_ANCHOR_UIDS    = [_PRIMARY_UID, _TOP_ESS_SM_UID, _TOP_ESS_SF_UID]
_ANCHOR_LABELS  = ["primary", "top_ess_sm_2016", "top_ess_sf_2016"]

# Frozen Gate-3b values (from v1 manifest gate3b_verdict.n100_high_ess_median_abs_delta)
_GATE3B_MEDIAN  = 0.7319804266785854
_GATE3B_VERDICT = "FAIL"

# ---------------------------------------------------------------------------
# paths — F3 inputs (immutable)
# ---------------------------------------------------------------------------
_CONFIG      = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"
_SPEC        = _REPO / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
_THETA       = _REPO / "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"
_F3_SINGLES  = _REPO / "outputs/welfare/fastlane/singles_Vi_production_v1.parquet"
_F3_COUPLES  = _REPO / "outputs/welfare/fastlane/couples_ViIS_capture_v1.parquet"
_F3_SUMMARY  = _REPO / "outputs/welfare/fastlane/f3_tasks1_5_summary.json"
_F3_GATE3B   = _REPO / "outputs/welfare/fastlane/f3_task2_gate3b_30hh_100nodes.json"
_V1_MANIFEST = _REPO / "outputs/welfare/fastlane_anchors_v1/manifest.json"

# F3-R2 outputs (also immutable from this script)
_F3R2_MANIFEST = _REPO / "outputs/welfare/fastlane/f3r2_reconciliation_manifest_v1.json"
_F3R2_PARITY   = _REPO / "outputs/welfare/fastlane/f3r2_joint_batch_parity_2016_singles_v1.json"

# New F3-R2A outputs
_OUT_DIR       = _REPO / "outputs/welfare/fastlane"
_OUT_AV3       = _REPO / "outputs/welfare/fastlane_anchors_v3"
_OUT_MANIFEST  = _OUT_DIR / "f3r2a_repair_manifest_v1.json"
_OUT_DIAGNOSIS = _OUT_DIR / "f3r2a_joint_batch_diagnosis_v1.json"
_OUT_DOC       = _REPO / "docs/jmp_methodology/RURO_welfare_F3R2A_repair_diagnosis_v1.md"

_IMMUTABLE = {
    _F3_SINGLES, _F3_COUPLES, _F3_SUMMARY, _F3_GATE3B, _V1_MANIFEST,
    _F3R2_MANIFEST, _F3R2_PARITY,
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write_parquet(df: pd.DataFrame, dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: would overwrite immutable artifact: {dest}")
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


def _load_cfg():
    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    w = cfg["welfare"]
    cert   = w["baseline"]["engine_ready_stem"]
    staged = w["stage4"]["welfare_pricing_reference"]["staged_engine_ready_stem"]
    return cert, staged


def _load_theta(spec):
    df = pd.read_csv(_THETA)
    lu = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    return np.array([lu.get(n, float(spec.initial_values.get(n, 0.0)))
                     for n in spec.all_param_names], dtype=np.float64)


def _system_pairing(bc):
    system_code, dataset_name = bc["system_pairing"][YEAR]
    country = system_code[:2]
    return country, system_code, dataset_name


# ---------------------------------------------------------------------------
# V_dir helpers (copied from run_stage4c_singles_vdir_smoke.py — no edits to source)
# ---------------------------------------------------------------------------
def _logmeanexp(arr):
    a = np.asarray(arr, dtype=np.float64)
    mx = float(np.max(a))
    return mx + float(np.log(np.mean(np.exp(a - mx))))


def _box_cox(x, theta):
    x = np.asarray(x, dtype=np.float64)
    if abs(float(theta)) < 1e-8:
        return np.log(x)
    return (np.power(x, float(theta)) - 1.0) / float(theta)


class _SinglesNodeShim:
    def __init__(self, *, n_nodes, is_male, **arrays):
        self.n_groups = 1
        self.n_obs = int(n_nodes)
        self.is_male = bool(is_male)
        self.cluster_ids = np.zeros(1, dtype=np.int64)
        self.group_ids = np.zeros(1, dtype=np.int64)
        self.consumption = np.ones(int(n_nodes), dtype=np.float64)
        for k, v in arrays.items():
            setattr(self, k, np.asarray(v, dtype=np.float64))


def _node_V_singles_terms(spec, theta, *, c_norm, l_norm, working, wage, priced_row):
    """Compute full V and utility u for redrawn nodes. Returns (V_full, terms)."""
    df = priced_row.reset_index(drop=True)
    c_norm  = np.asarray(c_norm,  dtype=np.float64)
    l_norm  = np.asarray(l_norm,  dtype=np.float64)
    working = np.asarray(working, dtype=np.float64)
    wage    = np.asarray(wage,    dtype=np.float64)
    n = c_norm.shape[0]

    is_male = bool(int(round(float(df["dgn"].iloc[0]))) == 1)
    suffix  = "_sm" if is_male else "_sf"
    group   = "singles_male" if is_male else "singles_female"

    if "hours" not in df.columns:
        raise RuntimeError("node_V_singles_terms requires per-node 'hours' on priced_row")
    hours = pd.to_numeric(df["hours"], errors="coerce").to_numpy()

    def col(name, default=0.0):
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce").fillna(default).to_numpy()
        return np.full(n, default, dtype=np.float64)

    loc4   = col("loc4", 0.0)
    loc4_2 = (loc4 == 2).astype(np.float64)
    loc4_3 = (loc4 == 3).astype(np.float64)
    loc4_4 = (loc4 == 4).astype(np.float64)

    def reg(k):
        rn = f"reg_nuts1_{k}"
        if rn in df.columns:
            return col(rn, 0.0)
        if "drgn1" in df.columns:
            return (col("drgn1", 0.0) == k).astype(np.float64)
        return np.zeros(n, dtype=np.float64)

    working_pt1 = ((hours >= 18.5) & (hours <= 21.5)).astype(np.float64)
    working_pt2 = ((hours >= 29.5) & (hours <= 30.5)).astype(np.float64)
    working_ft  = ((hours >= 37.5) & (hours <= 40.5)).astype(np.float64)
    if "working_lh" in df.columns:
        working_lh = col("working_lh", 0.0)
    else:
        working_lh = (((hours >= 44.5) & (hours <= 70.0)) & (working > 0)).astype(np.float64)

    log_wage = np.where(working > 0, np.log(np.maximum(wage, 1e-12)), 0.0)
    prior    = np.full(n, 1.0 / max(n, 1), dtype=np.float64)

    shim = _SinglesNodeShim(
        n_nodes=n, is_male=is_male,
        leisure=l_norm, working=working, prior=prior, log_wage=log_wage,
        age_norm=col("age_norm"), age_norm2=col("age_norm2"),
        n_children=(np.zeros(n) if is_male else col("n_children")),
        educL=col("educL"), educH=col("educH"),
        pexp_years=col("pexp_years"), pexp_years2=col("pexp_years2"),
        gsur=col("gsur"),
        working_pt1=working_pt1, working_pt2=working_pt2,
        working_ft=working_ft, working_lh=working_lh,
        reg2=reg(2), reg3=reg(3), reg4=reg(4), reg5=reg(5),
        reg6=reg(6), reg7=reg(7), reg8=reg(8),
        drgur=col("drgur"), drgmd=col("drgmd"),
        year_2015_indicator=col("year_2015_indicator"),
        year_2017_indicator=col("year_2017_indicator"),
        loc4_2=loc4_2, loc4_3=loc4_3, loc4_4=loc4_4)

    Vfn, _meta = wc._build_V_extractor(shim, spec, group)
    th   = jnp.asarray(np.asarray(theta, dtype=np.float64))
    cons = jnp.asarray(c_norm)
    V_full = np.asarray(Vfn(th, cons), dtype=np.float64)

    pidx  = {nm: spec.get_param_index(nm) for nm in spec.all_param_names}
    fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def P(name):
        if name in fixed:
            return float(fixed[name])
        return float(theta[pidx[name]])

    theta_l_name = (spec.utility_leisure_theta + suffix if spec.utility_leisure_theta else None)
    theta_c_name = spec.theta_c_param_name(group)
    theta_l = P(theta_l_name) if theta_l_name else 0.0
    theta_c = P(theta_c_name) if theta_c_name else 0.0
    bc_l = _box_cox(l_norm, theta_l)
    bc_c = _box_cox(c_norm, theta_c)
    beta_l = P(spec.utility_leisure_intercept + suffix)
    for sh in spec.utility_leisure_shifters:
        var, coef = sh["variable"], sh["coefficient"]
        if sh.get("gender_specific", False) and var == "n_children" and is_male:
            continue
        arr = getattr(shim, var, None)
        if arr is None:
            continue
        beta_l = beta_l + P(coef + suffix) * np.asarray(arr, dtype=np.float64)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)
    beta_c = (beta_c_fixed if beta_c_fixed is not None
              else P(spec.utility_consumption_coef + suffix))
    u = beta_l * bc_l + beta_c * bc_c
    return V_full, {"u": u}


def _compute_vdir_diagnostics(priced_nodes: pd.DataFrame, nodes: dict,
                               spec, theta: np.ndarray, V_i_IS: float) -> dict:
    """V_i^dir_util, V_i^dir_fullV, CV2, delta_common for one anchor."""
    n = len(priced_nodes)
    cons_real = pd.to_numeric(priced_nodes["ils_dispy_real"], errors="coerce").to_numpy()
    c_norm = np.clip(cons_real, DCM_MIN_POSITIVE, None) / C_SCALE
    hours = (pd.to_numeric(priced_nodes["hours"], errors="coerce").to_numpy()
             if "hours" in priced_nodes.columns else nodes["hours"][:n])
    leisure = np.clip(TOTAL_LEISURE_HOURS - hours, DCM_MIN_POSITIVE, None)
    l_norm = leisure / L_SCALE
    working = (pd.to_numeric(priced_nodes["working"], errors="coerce").to_numpy()
               if "working" in priced_nodes.columns else nodes["working"][:n])
    wage = (pd.to_numeric(priced_nodes["wage"], errors="coerce").to_numpy()
            if "wage" in priced_nodes.columns else nodes["wage"][:n])

    V_full, terms = _node_V_singles_terms(spec, theta, c_norm=c_norm, l_norm=l_norm,
                                          working=working, wage=wage, priced_row=priced_nodes)
    u = np.asarray(terms["u"], dtype=np.float64)
    V_full = np.asarray(V_full, dtype=np.float64)

    vdir_util  = _logmeanexp(u)
    vdir_fullV = _logmeanexp(V_full)

    # CV2 = var(exp(u)) / mean(exp(u))^2  (numerically stable via shifted weights)
    u_shift = u - np.max(u)
    w_u = np.exp(u_shift)
    mean_w = float(np.mean(w_u))
    cv2 = float(np.var(w_u) / (mean_w ** 2))
    cv2_per_2s = cv2 / (2.0 * n)
    vdir_bias_corrected = vdir_util - cv2_per_2s

    vis_logmean_basis = V_i_IS - float(np.log(N_DRAWS_EXISTING))
    delta_common = vdir_fullV - vis_logmean_basis

    return {
        "V_i_dir_util":          float(vdir_util),
        "V_i_dir_fullV":         float(vdir_fullV),
        "V_i_IS_logmean_basis":  float(vis_logmean_basis),
        "delta_common":          float(delta_common),
        "abs_delta_common":      float(abs(delta_common)),
        "CV2":                   float(cv2),
        "CV2_per_2S":            float(cv2_per_2s),
        "V_i_dir_bias_corrected": float(vdir_bias_corrected),
        "n_nodes":               int(n),
    }


# ---------------------------------------------------------------------------
# EUROMOD helpers
# ---------------------------------------------------------------------------
def _overwrite_choice_vars(band: pd.DataFrame, target_uid: int, nodes: dict, use_draws):
    for k, dr in enumerate(use_draws):
        sel = ((band["stacked_hh_uid"] == target_uid) & (band["draw"] == dr)
               & (band["ruro_decider"] == 1))
        if int(sel.sum()) != 1:
            raise RuntimeError(f"uid={target_uid} draw={dr}: {int(sel.sum())} decider rows (expect 1)")
        wk  = int(nodes["working"][k])
        h   = float(nodes["hours"][k])
        w   = float(nodes["wage"][k])
        lo4 = int(nodes["loc4"][k])
        if wk == 1 and h > 0 and w > 0:
            reg_h = min(h, _FR_STD_HOURS)
            ot_h  = max(h - _FR_STD_HOURS, 0.0)
            yem00 = reg_h * w * _WEEKS_PER_MONTH
            yemxp = ot_h * w * _WEEKS_PER_MONTH
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


def _stamp_and_run_euromod(bc, band: pd.DataFrame, country: str, sys_code: str, dataset: str):
    """Stamp draw IDs, build em_input, run EUROMOD. Returns (sim, em_input, stamped)."""
    bmod    = __import__("run_bpool_euromod_chunk")
    stamped = bmod._stamp_draw_ids(band.copy(), "draw", 1_000)
    raw_cols = bc["raw_schema"][YEAR]
    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    runner = bc["EuromodRunner"](bc["em_root"])
    sim = runner.run_on_dataframe(em_input, country=country,
                                  system_code=sys_code, dataset_name=dataset)
    return sim, em_input, stamped


def _price_anchor_target_only(bc, band_2016: pd.DataFrame, uid: int, nodes: dict,
                               phi: float, country: str, sys_code: str, dataset: str):
    """Target-only pricing for one anchor. Returns (priced_df, em_rows_df, em_meta_df, sim_output_cols, use_draws)
    where em_rows_df = anchor's em_input rows after stamping (raw schema cols),
          em_meta_df = corresponding (draw, idperson_true, stacked_hh_uid) rows.
    Returns (None, None, None, error_str, None) on failure."""
    dec_draws = sorted(
        int(d) for d in band_2016[
            (band_2016["stacked_hh_uid"] == uid)
            & (band_2016["ruro_decider"] == 1)
            & (band_2016["draw"] >= 1)
        ]["draw"].unique()
    )
    if len(dec_draws) < N_NODES:
        return None, None, None, f"only {len(dec_draws)} decider draws for uid={uid}", None
    use_draws = dec_draws[:N_NODES]

    band_mod = band_2016.copy()
    for c in ["yivwg", "yem00", "yemxp", "yem_hour"]:
        if c not in band_mod.columns:
            band_mod[c] = 0.0
    _overwrite_choice_vars(band_mod, uid, nodes, use_draws)

    try:
        sim, em_input, stamped = _stamp_and_run_euromod(bc, band_mod, country, sys_code, dataset)
    except Exception as e:
        return None, None, None, f"EUROMOD failed: {e}", None

    if len(sim) != len(band_mod):
        return None, None, None, f"sim row count mismatch {len(sim)} vs {len(band_mod)}", None

    raw_cols_set = set(bc["raw_schema"][YEAR])
    sim_output_cols = [c for c in sim.columns if c not in raw_cols_set]

    # Build output with idperson_true from band_mod (before stamping)
    out = band_mod.reset_index(drop=True).copy()
    out["idperson_true"] = out["idperson"]
    for col in sim_output_cols:
        out[col] = sim[col].values
    out["ils_dispy_real"] = (out["ils_dispy"] * phi
                             if "ils_dispy" in out.columns
                             else float("nan"))

    tgt = out[
        (out["stacked_hh_uid"] == uid)
        & (out["draw"].isin(set(use_draws)))
        & (out["ruro_decider"] == 1)
    ].copy().sort_values("draw").reset_index(drop=True)

    # Save anchor's em_input rows for Gate B verification
    # stamped.index == band_mod.reset_index(drop=False).index (same positional order)
    anchor_mask = (
        (stamped["stacked_hh_uid"] == uid)
        & (stamped["draw"].isin(set(use_draws)))
        & (stamped["ruro_decider"] == 1)
    )
    em_rows  = em_input[anchor_mask.values].copy().reset_index(drop=True)
    em_meta  = stamped[anchor_mask.values][["draw", "idperson_true", "stacked_hh_uid"]].reset_index(drop=True)

    return tgt, em_rows, em_meta, sim_output_cols, use_draws


# ---------------------------------------------------------------------------
# TASK 1 — Repair metadata
# ---------------------------------------------------------------------------
def task1_repair() -> dict:
    print("\n=== TASK 1: Repair metadata ===")
    with open(_V1_MANIFEST) as f:
        v1 = json.load(f)
    gate3b = v1.get("gate3b_verdict", {})
    manifest_median = float(gate3b.get("n100_high_ess_median_abs_delta", _GATE3B_MEDIAN))
    manifest_status = gate3b.get("status", "FAIL")

    with open(_F3R2_PARITY) as f:
        parity = json.load(f)
    f3r2_verdict = parity.get("verdict", "NOT_LICENSED")

    result = {
        "gate3b_verdict":    _GATE3B_VERDICT,
        "gate3b_median_abs_delta": _GATE3B_MEDIAN,
        "gate3b_source":     "fastlane_anchors_v1/manifest.json → gate3b_verdict.n100_high_ess_median_abs_delta",
        "gate3b_confirmed":  abs(manifest_median - _GATE3B_MEDIAN) < 1e-12 and manifest_status == "FAIL",
        "f4_readiness":      "YES",
        "f4_readiness_basis": (
            "Dual-stem V_i^IS production gate-0 certified (singles+couples PASS). "
            "Joint-batch parity is NOT an F4 dependency: F4 uses V_i^IS as the primary integrator. "
            "Omega readiness is out of scope for this repair."
        ),
        "omega_readiness":   "OUT_OF_SCOPE",
        "f3r2_provisional_verdict": f3r2_verdict,
        "f3r2_provisional_note": (
            "F3-R2 Task 3 used independently redrawn nodes (same frozen RNG formula but separate calls). "
            "F3-R2A Task 3 uses the EXACT frozen Task-2 node tables to provide dispositive evidence."
        ),
        "task1_status": "DONE",
    }
    print(f"  Gate-3b: {result['gate3b_verdict']}  median={result['gate3b_median_abs_delta']}")
    print(f"  F4 readiness: {result['f4_readiness']}")
    return result


# ---------------------------------------------------------------------------
# TASK 2 — Complete durable anchor evidence (v3)
# ---------------------------------------------------------------------------
def task2_anchor_evidence(bp: Path, staged_stem: str, spec, theta: np.ndarray) -> dict:
    print("\n=== TASK 2: Complete durable anchor evidence (v3) ===")
    t0 = time.time()

    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)

    print(f"  Loading 2016 singles band from {staged_stem}...")
    band_full = pd.read_parquet(bp / f"{staged_stem}__singles.parquet")
    band_2016 = band_full[band_full["year_tag"] == YEAR_TAG].copy()
    print(f"  Band: {len(band_2016)} rows, {band_2016['stacked_hh_uid'].nunique()} HHs")

    # V_i^IS, ESS, max_weight from production parquet
    s_df       = pd.read_parquet(_F3_SINGLES)
    vis_lookup = {int(r["uid"]): r for _, r in s_df.iterrows()}

    _OUT_AV3.mkdir(parents=True, exist_ok=True)

    anchor_results   = {}
    sim_output_cols_ref = None

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        print(f"  Anchor uid={uid} ({label})...")
        t_anc = time.time()

        seed = BASE_SEED + (uid % 1_000_000)
        rng  = np.random.default_rng(np.random.PCG64(seed))

        hh0 = band_2016[
            (band_2016["stacked_hh_uid"] == uid)
            & (band_2016["draw"] == 0)
            & (band_2016["ruro_decider"] == 1)
        ]
        if hh0.empty:
            anchor_results[label] = {"status": "BLOCKED", "uid": uid, "reason": "no draw=0 decider row"}
            continue
        hh_row    = hh0.iloc[0].to_dict()
        yt_hh     = int(hh_row.get("year_tag", YEAR_TAG))
        nodes     = wvd.redraw_nodes_singles(hh_row, N_NODES, rng, mincer, dm, year_tag=yt_hh)

        # Save frozen node table
        node_df = pd.DataFrame({
            "draw_slot": np.arange(1, N_NODES + 1, dtype=np.int32),
            "working":   nodes["working"].astype(np.int8),
            "hours":     nodes["hours"].astype(np.float64),
            "wage":      nodes["wage"].astype(np.float64),
            "loc4":      nodes["loc4"].astype(np.int32),
        })
        nodes_pq = _OUT_AV3 / f"anchor_{label}_uid{uid}_nodes_v3.parquet"
        _atomic_write_parquet(node_df, nodes_pq)

        # Price target-only, capture ALL sim output cols
        tgt, em_rows, em_meta, sim_output_cols, use_draws = _price_anchor_target_only(
            bc, band_2016, uid, nodes, phi, country, sys_code, dataset)

        if tgt is None:
            anchor_results[label] = {"status": "BLOCKED", "uid": uid, "reason": sim_output_cols}
            continue

        if sim_output_cols_ref is None:
            sim_output_cols_ref = sim_output_cols

        # Save em_input anchor rows (for Gate B)
        em_combined = em_rows.copy()
        for col in ["draw", "idperson_true", "stacked_hh_uid"]:
            if col in em_meta.columns:
                em_combined[col] = em_meta[col].values
        em_pq = _OUT_AV3 / f"anchor_{label}_uid{uid}_em_input_v3.parquet"
        _atomic_write_parquet(em_combined, em_pq)

        # Save full priced output
        keep = (["stacked_hh_uid", "draw", "year_tag", "ruro_decider", "idperson_true"]
                + sim_output_cols + ["ils_dispy_real"])
        priced_out = tgt[[c for c in keep if c in tgt.columns]].copy()
        priced_pq  = _OUT_AV3 / f"anchor_{label}_uid{uid}_priced_v3.parquet"
        _atomic_write_parquet(priced_out, priced_pq)

        # V_i^IS, ESS from production
        prod = vis_lookup.get(uid)
        V_i_IS = float(prod["V_i_IS"])   if prod is not None else float("nan")
        ESS    = float(prod["ESS"])       if prod is not None else float("nan")
        max_w  = float(prod["max_weight"]) if prod is not None else float("nan")

        # V_dir diagnostics
        vdir = _compute_vdir_diagnostics(tgt, nodes, spec, theta, V_i_IS)

        elapsed = round(time.time() - t_anc, 1)
        prov = {
            "uid": uid, "label": label, "year_tag": yt_hh,
            "seed": seed, "n_nodes": N_NODES,
            "V_i_IS_staged": V_i_IS, "ESS": ESS, "max_weight": max_w,
            **vdir,
            "sim_output_cols": sim_output_cols,
            "nodes_parquet":   str(nodes_pq),
            "em_input_parquet": str(em_pq),
            "priced_parquet":  str(priced_pq),
            "nodes_hash":      _sha256(nodes_pq),
            "em_input_hash":   _sha256(em_pq),
            "priced_hash":     _sha256(priced_pq),
            "elapsed_s":       elapsed,
            "status":          "OK",
        }
        prov_json = _OUT_AV3 / f"anchor_{label}_uid{uid}_provenance_v3.json"
        _atomic_write_json(prov, prov_json)
        anchor_results[label] = prov

        print(f"    OK: V_dir_util={vdir['V_i_dir_util']:.4f}  "
              f"delta_common={vdir['delta_common']:.4f}  "
              f"CV2={vdir['CV2']:.4f}  elapsed={elapsed}s")

    # Utility-only B2 gate: |delta_common| <= 0.5 for each priced anchor
    statuses = [
        "pass" if abs(v.get("delta_common", float("inf"))) <= 0.5 else "fail"
        for v in anchor_results.values() if v.get("status") == "OK"
    ]
    if not statuses:
        b2_gate = "fail"
    elif all(s == "pass" for s in statuses):
        b2_gate = "pass"
    elif any(s == "pass" for s in statuses):
        b2_gate = "mixed"
    else:
        b2_gate = "fail"

    result = {
        "anchors":            anchor_results,
        "sim_output_cols":    sim_output_cols_ref,
        "utility_only_b2_gate": b2_gate,
        "task2_elapsed_s":    round(time.time() - t0, 1),
        "task2_status":       ("DONE" if all(v.get("status") == "OK"
                                             for v in anchor_results.values()) else "PARTIAL"),
    }
    print(f"  Task-2: {result['task2_status']}  B2 gate: {b2_gate}  elapsed: {result['task2_elapsed_s']}s")
    return result


# ---------------------------------------------------------------------------
# TASK 3 — Dispositive joint-batch diagnosis
# ---------------------------------------------------------------------------
def task3_diagnosis(bp: Path, staged_stem: str, spec, theta: np.ndarray,
                    t2: dict) -> dict:
    print("\n=== TASK 3: Dispositive joint-batch diagnosis ===")
    t0 = time.time()

    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)
    raw_cols     = bc["raw_schema"][YEAR]
    raw_cols_set = set(raw_cols)
    bmod         = __import__("run_bpool_euromod_chunk")

    print(f"  Loading 2016 singles band from {staged_stem}...")
    band_full = pd.read_parquet(bp / f"{staged_stem}__singles.parquet")
    band = band_full[band_full["year_tag"] == YEAR_TAG].copy().reset_index(drop=True)
    all_uids = sorted(band["stacked_hh_uid"].unique().tolist())
    n_hh = len(all_uids)
    print(f"  Band: {len(band)} rows, {n_hh} HHs")

    for c in ["yivwg", "yem00", "yemxp", "yem_hour"]:
        if c not in band.columns:
            band[c] = 0.0

    # Index maps for efficient overwrite
    dec_mask = (band["ruro_decider"] == 1) & (band["draw"] >= 1)
    dec      = band[dec_mask][["stacked_hh_uid", "draw"]].copy()
    dec["_idx"] = dec.index
    dec_by_uid  = {int(uid): grp.sort_values("draw")["_idx"].tolist()
                   for uid, grp in dec.groupby("stacked_hh_uid")}
    hh0_rows    = band[(band["ruro_decider"] == 1) & (band["draw"] == 0)]
    hh_by_uid   = {int(r["stacked_hh_uid"]): r.to_dict() for _, r in hh0_rows.iterrows()}

    # Load frozen Task-2 node tables for anchor HHs
    frozen_nodes = {}
    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        nodes_pq = _OUT_AV3 / f"anchor_{label}_uid{uid}_nodes_v3.parquet"
        if not nodes_pq.exists():
            alt = t2.get("anchors", {}).get(label, {}).get("nodes_parquet", "")
            if alt and Path(alt).exists():
                nodes_pq = Path(alt)
        if not nodes_pq.exists():
            raise RuntimeError(f"STOP: frozen nodes missing for {label} uid={uid}: {nodes_pq}")
        ndf = pd.read_parquet(nodes_pq)
        frozen_nodes[uid] = {
            "working": ndf["working"].to_numpy().astype(np.int8),
            "hours":   ndf["hours"].to_numpy().astype(np.float64),
            "wage":    ndf["wage"].to_numpy().astype(np.float64),
            "loc4":    ndf["loc4"].to_numpy().astype(np.int32),
        }
        print(f"  Loaded frozen nodes uid={uid} ({label}): {len(ndf)} draws")

    # Build joint batch (anchors use frozen, others redraw)
    print(f"  Building joint batch ({n_hh} HHs)...")
    t_redraw = time.time()
    blocked  = []
    for n_done, uid in enumerate(all_uids):
        if uid not in hh_by_uid:
            blocked.append(uid); continue
        indices = dec_by_uid.get(uid, [])
        if len(indices) < N_NODES:
            blocked.append(uid); continue

        if uid in frozen_nodes:
            nodes = frozen_nodes[uid]
        else:
            hh_row = hh_by_uid[uid]
            yt_hh  = int(hh_row.get("year_tag", YEAR_TAG))
            seed   = BASE_SEED + (uid % 1_000_000)
            rng    = np.random.default_rng(np.random.PCG64(seed))
            nodes  = wvd.redraw_nodes_singles(hh_row, N_NODES, rng, mincer, dm, year_tag=yt_hh)

        use_idx = indices[:N_NODES]
        for k, idx in enumerate(use_idx):
            wk  = int(nodes["working"][k])
            h   = float(nodes["hours"][k])
            w   = float(nodes["wage"][k])
            lo4 = int(nodes["loc4"][k])
            if wk == 1 and h > 0 and w > 0:
                reg_h = min(h, _FR_STD_HOURS)
                ot_h  = max(h - _FR_STD_HOURS, 0.0)
                band.at[idx, "lhw"]      = h
                band.at[idx, "yivwg"]    = w
                band.at[idx, "yem_hour"] = w
                band.at[idx, "yem00"]    = reg_h * w * _WEEKS_PER_MONTH
                band.at[idx, "yemxp"]    = ot_h  * w * _WEEKS_PER_MONTH
                band.at[idx, "yem"]      = (reg_h + ot_h) * w * _WEEKS_PER_MONTH
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

    # Stamp and build em_input (used for both Gate B and EUROMOD call)
    stamped_j = bmod._stamp_draw_ids(band.copy(), "draw", 1_000)
    em_input_j = stamped_j[[c for c in raw_cols if c in stamped_j.columns]].copy()
    for c in em_input_j.columns:
        em_input_j[c] = pd.to_numeric(em_input_j[c], errors="coerce").fillna(0.0)

    # ---- Gate B: byte-identity of em_input rows ----
    print("  Gate B: byte-identity check...")
    gate_b_results = {}
    gate_b_pass    = True

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        arec = t2.get("anchors", {}).get(label, {})
        if arec.get("status") != "OK":
            gate_b_results[label] = {"status": "SKIPPED_ANCHOR_NOT_PRICED", "uid": uid}
            gate_b_pass = False
            continue

        em_pq = _OUT_AV3 / f"anchor_{label}_uid{uid}_em_input_v3.parquet"
        if not em_pq.exists():
            gate_b_results[label] = {"status": "MISSING_T2_EM_INPUT", "uid": uid}
            gate_b_pass = False
            continue

        t2_em = pd.read_parquet(em_pq)    # has raw_schema cols + draw + idperson_true + stacked_hh_uid
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
                "uid": uid, "status": "ROW_COUNT_MISMATCH",
                "t2_rows": len(t2_em), "t3_rows": len(t3_em)
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
                nonzero[col] = d
            if np.isfinite(d):
                max_abs = max(max_abs, d)

        b_pass = len(nonzero) == 0
        if not b_pass:
            gate_b_pass = False
        gate_b_results[label] = {
            "uid": uid, "n_rows": len(t2_s), "max_abs_diff": max_abs,
            "pass": b_pass, "nonzero_diff_cols": list(nonzero.keys()),
        }
        print(f"    Gate B {label}: pass={b_pass}  max_abs={max_abs:.2e}  "
              f"divergent_cols={list(nonzero.keys())[:5]}")

    if not gate_b_pass:
        return {
            "gate_b_pass": False, "gate_b_results": gate_b_results,
            "gate_a_pass": None,  "gate_a_result":  None,
            "gate_c_pass": None,  "gate_c_results": None,
            "first_divergent_component": None,
            "verdict": "CONSTRUCTION_MISMATCH",
            "batch_context_dependence": "unresolved",
            "joint_batching_licensed": "unresolved",
            "stop_reason": "Gate B failed: em_input rows differ between target-only and joint-batch",
            "n_hh_joint_batch": n_hh, "n_hh_blocked": len(blocked),
            "year": YEAR, "year_tag": YEAR_TAG, "n_nodes_per_hh": N_NODES,
            "base_seed": BASE_SEED, "euromod_system": sys_code, "euromod_dataset": dataset,
            "redraw_elapsed_s": redraw_elapsed, "euromod_elapsed_s": None,
            "task3_elapsed_s": round(time.time() - t0, 1),
        }
    print("  Gate B: PASS")

    # ---- Run joint-batch EUROMOD ----
    print(f"  Running joint-batch EUROMOD on {len(band)} rows...")
    t_em = time.time()
    try:
        runner    = bc["EuromodRunner"](bc["em_root"])
        sim_joint = runner.run_on_dataframe(
            em_input_j, country=country, system_code=sys_code, dataset_name=dataset)
    except Exception as e:
        raise RuntimeError(f"Joint-batch EUROMOD failed: {e}") from e
    em_elapsed = round(time.time() - t_em, 1)
    print(f"  Joint-batch EUROMOD: {len(sim_joint)} rows, elapsed {em_elapsed}s")

    if len(sim_joint) != len(band):
        raise RuntimeError(f"STOP: joint sim row count mismatch {len(sim_joint)} vs {len(band)}")

    actual_sim_cols = [c for c in sim_joint.columns if c not in raw_cols_set]

    joint_out = band.reset_index(drop=True).copy()
    joint_out["idperson_true"] = joint_out["idperson"]
    for col in actual_sim_cols:
        joint_out[col] = sim_joint[col].values
    joint_out["ils_dispy_real"] = (joint_out["ils_dispy"] * phi
                                   if "ils_dispy" in joint_out.columns else float("nan"))

    # ---- Gate A: EUROMOD determinism (repeat primary anchor target-only) ----
    print("  Gate A: EUROMOD determinism check (repeat primary anchor)...")
    t_ga = time.time()
    nodes_primary = frozen_nodes.get(_PRIMARY_UID)
    if nodes_primary is None:
        gate_a_result = {"pass": None, "reason": "frozen nodes not available"}
    else:
        tgt_a, _, _, _, _ = _price_anchor_target_only(
            bc, band_full[band_full["year_tag"] == YEAR_TAG].copy(),
            _PRIMARY_UID, nodes_primary, phi, country, sys_code, dataset)
        priced_orig_pq = _OUT_AV3 / f"anchor_primary_uid{_PRIMARY_UID}_priced_v3.parquet"
        if tgt_a is None or not priced_orig_pq.exists():
            gate_a_result = {"pass": None, "reason": "could not obtain original or repeat pricing"}
        else:
            orig_a = pd.read_parquet(priced_orig_pq)
            cmp_a  = [c for c in actual_sim_cols + ["ils_dispy_real"]
                      if c in orig_a.columns and c in tgt_a.columns]
            orig_s = orig_a.sort_values("draw").reset_index(drop=True)
            rpt_s  = tgt_a.sort_values("draw").reset_index(drop=True)
            n_cmp  = min(len(orig_s), len(rpt_s))
            max_a  = 0.0
            fail_a = []
            for col in cmp_a:
                d = float(np.nanmax(np.abs(
                    orig_s[col].values[:n_cmp].astype(float)
                    - rpt_s[col].values[:n_cmp].astype(float)
                )))
                max_a = max(max_a, d)
                if d > TOL:
                    fail_a.append(col)
            gate_a_result = {
                "pass": len(fail_a) == 0,
                "max_abs_diff": max_a,
                "n_rows": n_cmp,
                "failing_cols": fail_a,
            }
    ga_elapsed = round(time.time() - t_ga, 1)
    gate_a_pass = gate_a_result.get("pass")
    print(f"  Gate A: pass={gate_a_pass}  "
          f"max_abs={gate_a_result.get('max_abs_diff', 'N/A')}  elapsed={ga_elapsed}s")

    if gate_a_pass is False:
        return {
            "gate_b_pass": True,  "gate_b_results": gate_b_results,
            "gate_a_pass": False, "gate_a_result":  gate_a_result,
            "gate_c_pass": None,  "gate_c_results": None,
            "first_divergent_component": None,
            "verdict": "EUROMOD_REPRODUCIBILITY_UNRESOLVED",
            "batch_context_dependence": "unresolved",
            "joint_batching_licensed": "unresolved",
            "stop_reason": "Gate A failed: EUROMOD output not reproducible to 1e-6",
            "n_hh_joint_batch": n_hh, "n_hh_blocked": len(blocked),
            "year": YEAR, "year_tag": YEAR_TAG, "n_nodes_per_hh": N_NODES,
            "base_seed": BASE_SEED, "euromod_system": sys_code, "euromod_dataset": dataset,
            "redraw_elapsed_s": redraw_elapsed, "euromod_elapsed_s": em_elapsed,
            "task3_elapsed_s": round(time.time() - t0, 1),
        }

    # ---- Gate C: compare all shared sim output cols by (uid, draw, idperson_true) ----
    print("  Gate C: comparing joint-batch vs target-only sim outputs...")
    gate_c_results  = {}
    gate_c_pass     = True
    first_divergent = None

    for uid, label in zip(_ANCHOR_UIDS, _ANCHOR_LABELS):
        arec = t2.get("anchors", {}).get(label, {})
        if arec.get("status") != "OK":
            gate_c_results[label] = {"status": "SKIPPED"}
            continue

        priced_pq = _OUT_AV3 / f"anchor_{label}_uid{uid}_priced_v3.parquet"
        if not priced_pq.exists():
            gate_c_results[label] = {"status": "MISSING_T2_PRICED", "uid": uid}
            gate_c_pass = False
            continue
        t2_priced = pd.read_parquet(priced_pq)

        jb_rows = joint_out[
            (joint_out["stacked_hh_uid"] == uid)
            & (joint_out["draw"] >= 1)
            & (joint_out["ruro_decider"] == 1)
        ].sort_values("draw").reset_index(drop=True)

        t2_s = t2_priced.sort_values("draw").reset_index(drop=True)
        jb_s = jb_rows.sort_values("draw").reset_index(drop=True)

        if len(t2_s) != len(jb_s):
            gate_c_results[label] = {
                "uid": uid, "status": "ROW_COUNT_MISMATCH",
                "t2_rows": len(t2_s), "t3_rows": len(jb_s),
            }
            gate_c_pass = False
            continue

        compare_cols = [c for c in actual_sim_cols + ["ils_dispy_real"]
                        if c in t2_s.columns and c in jb_s.columns]
        col_diffs  = {}
        max_anchor = 0.0
        for col in compare_cols:
            a = t2_s[col].values.astype(float)
            b = jb_s[col].values.astype(float)
            d = float(np.nanmax(np.abs(a - b)))
            col_diffs[col] = {"max_abs_diff": d, "pass": d <= TOL}
            max_anchor = max(max_anchor, d)

        anchor_pass = all(v["pass"] for v in col_diffs.values())
        if not anchor_pass:
            gate_c_pass = False
            if first_divergent is None:
                for col in compare_cols:
                    a = t2_s[col].values.astype(float)
                    b = jb_s[col].values.astype(float)
                    rows_div = np.where(np.abs(a - b) > TOL)[0]
                    if len(rows_div) > 0:
                        ri = int(rows_div[0])
                        first_divergent = {
                            "anchor_label": label, "uid": uid,
                            "column": col,
                            "draw": int(t2_s.iloc[ri]["draw"]) if "draw" in t2_s.columns else None,
                            "idperson_true": (int(t2_s.iloc[ri]["idperson_true"])
                                             if "idperson_true" in t2_s.columns else None),
                            "t2_value": float(a[ri]),
                            "joint_batch_value": float(b[ri]),
                            "abs_diff": float(abs(a[ri] - b[ri])),
                        }
                        break

        gate_c_results[label] = {
            "uid": uid, "n_rows": len(t2_s),
            "max_abs_diff": max_anchor, "pass": anchor_pass,
            "col_diffs": col_diffs,
        }
        print(f"    Gate C {label}: pass={anchor_pass}  max_abs={max_anchor:.2e}")

    # Interpret
    if gate_b_pass and not gate_c_pass:
        verdict   = "NOT_LICENSED"
        batch_ctx = "proven"
        jb_lic    = "not licensed"
    elif gate_b_pass and gate_c_pass:
        verdict   = "LICENSED"
        batch_ctx = "not proven"
        jb_lic    = "licensed"
        first_divergent = None
    else:
        verdict   = "UNRESOLVED"
        batch_ctx = "unresolved"
        jb_lic    = "unresolved"

    failing_c = sorted({
        col
        for rec in gate_c_results.values()
        if isinstance(rec, dict) and "col_diffs" in rec
        for col, cv in rec["col_diffs"].items()
        if not cv["pass"]
    })

    return {
        "gate_b_pass": True,
        "gate_b_results": gate_b_results,
        "gate_a_pass": gate_a_pass,
        "gate_a_result": gate_a_result,
        "gate_c_pass": gate_c_pass,
        "gate_c_results": gate_c_results,
        "first_divergent_component": first_divergent,
        "failing_cols_gate_c": failing_c,
        "verdict": verdict,
        "batch_context_dependence": batch_ctx,
        "joint_batching_licensed": jb_lic,
        "n_hh_joint_batch": n_hh,
        "n_hh_blocked": len(blocked),
        "year": YEAR, "year_tag": YEAR_TAG,
        "n_nodes_per_hh": N_NODES,
        "base_seed": BASE_SEED,
        "euromod_system": sys_code, "euromod_dataset": dataset,
        "redraw_elapsed_s": redraw_elapsed,
        "euromod_elapsed_s": em_elapsed,
        "task3_elapsed_s": round(time.time() - t0, 1),
    }


# ---------------------------------------------------------------------------
# TASK 4 — Final corrected report
# ---------------------------------------------------------------------------
def task4_report(t1: dict, t2: dict, t3: dict, manifest: dict):
    verdict   = t3.get("verdict",   "UNRESOLVED")
    batch_ctx = t3.get("batch_context_dependence", "unresolved")
    jb_lic    = t3.get("joint_batching_licensed",  "unresolved")
    b2_gate   = t2.get("utility_only_b2_gate", "fail")
    gate_b    = t3.get("gate_b_pass")
    gate_a    = t3.get("gate_a_pass")
    gate_c    = t3.get("gate_c_pass")

    conclusions = [
        "READY FOR F4: yes",
        "FROZEN FULL-V S=100 GATE: fail",
        f"UTILITY-ONLY B2 ANCHOR GATE: {b2_gate}",
        f"JOINT BATCHING METHOD: {jb_lic}",
        f"BATCH-CONTEXT DEPENDENCE: {batch_ctx}",
        "FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no",
    ]

    lines = [
        "# RURO Welfare F3-R2A Repair + Dispositive Joint-Batch Diagnosis v1",
        "",
        "## Overview",
        "",
        f"- spec_hash: `{manifest['spec_hash']}`",
        f"- theta_hash: `{manifest['theta_hash']}`",
        f"- Total elapsed: {manifest['total_elapsed_s']}s",
        "",
        "## Task 1 — Metadata Repair",
        "",
        f"- Gate-3b verdict (frozen): **{t1['gate3b_verdict']}**",
        f"- Gate-3b high-ESS median |delta_common|: {t1['gate3b_median_abs_delta']}",
        f"- F4 readiness: **{t1['f4_readiness']}**",
        f"- F4 basis: {t1['f4_readiness_basis']}",
        f"- Omega readiness: {t1['omega_readiness']}",
        f"- F3-R2 provisional verdict: {t1['f3r2_provisional_verdict']}",
        "",
        "## Task 2 — Durable Anchor Evidence (v3)",
        "",
        f"- Utility-only B2 anchor gate: **{b2_gate}**",
        f"- Sim output cols captured: {len(t2.get('sim_output_cols') or [])}",
        "",
        "| Anchor | UID | V_i^IS | ESS | V_dir_util | delta_common | B2 pass |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label, arec in t2.get("anchors", {}).items():
        if arec.get("status") != "OK":
            lines.append(f"| {label} | {arec.get('uid','?')} | BLOCKED | - | - | - | - |")
        else:
            b2p = "yes" if abs(arec.get("delta_common", float("inf"))) <= 0.5 else "no"
            lines.append(
                f"| {label} | {arec['uid']} | {arec['V_i_IS_staged']:.6f} "
                f"| {arec['ESS']:.1f} | {arec['V_i_dir_util']:.4f} "
                f"| {arec['delta_common']:.4f} | {b2p} |"
            )

    lines += [
        "",
        "## Task 3 — Dispositive Joint-Batch Diagnosis",
        "",
        f"- N HHs in joint batch: {t3.get('n_hh_joint_batch')}",
        f"- N nodes per HH: {t3.get('n_nodes_per_hh')}",
        f"- Base seed: {t3.get('base_seed')}",
        f"- EUROMOD: {t3.get('euromod_system')} / {t3.get('euromod_dataset')}",
        "",
        f"- **Gate B (byte-identity of em_input rows): {'PASS' if gate_b else 'FAIL'}**",
        f"- **Gate A (EUROMOD determinism): {'PASS' if gate_a else 'FAIL' if gate_a is not None else 'NOT RUN'}**",
        f"- **Gate C (output comparison): {'PASS' if gate_c else 'FAIL' if gate_c is not None else 'NOT RUN'}**",
        "",
        f"- **Verdict: {verdict}**",
        f"- Batch-context dependence: **{batch_ctx}**",
        f"- Joint batching method: **{jb_lic}**",
    ]

    first_div = t3.get("first_divergent_component")
    if first_div:
        lines += [
            "",
            "### First Divergent Component",
            "",
            f"- Anchor: `{first_div.get('anchor_label')}` (uid={first_div.get('uid')})",
            f"- Column: `{first_div.get('column')}`",
            f"- Draw: {first_div.get('draw')}",
            f"- idperson_true: {first_div.get('idperson_true')}",
            f"- Target-only value: {first_div.get('t2_value')}",
            f"- Joint-batch value: {first_div.get('joint_batch_value')}",
            f"- Abs diff: {first_div.get('abs_diff'):.6f}",
        ]
        failing = t3.get("failing_cols_gate_c", [])
        if failing:
            lines.append(f"- All failing columns: {failing}")
        lines += [
            "",
            "> Batch-context dependence is PROVEN: Gate B passed (identical EUROMOD inputs) "
            "but Gate C failed (divergent outputs). Divergence is in the EUROMOD output layer. "
            "No speculation about the policy mechanism without source evidence.",
        ]
    elif verdict == "LICENSED":
        lines += [
            "",
            "> All gates pass: EUROMOD outputs are identical between target-only and joint-batch "
            "when inputs are byte-identical. Joint batching is LICENSED. Note: full V_i^dir at "
            "S=100 remains unauthorized because the frozen full-V convergence gate failed.",
        ]

    lines += [
        "",
        "## Conclusions",
        "",
    ] + conclusions

    report_text = "\n".join(lines) + "\n"
    if _OUT_DOC.exists():
        _OUT_DOC.unlink()
    _OUT_DOC.write_text(report_text, encoding="utf-8")
    print(f"  Report: {_OUT_DOC}")

    print("\n--- CONCLUSIONS ---")
    for line in conclusions:
        print(line)

    return conclusions


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    t_global = time.time()
    bp = bpool_dir()
    cert_stem, staged_stem = _load_cfg()

    spec       = sp.parse_specification(str(_SPEC))
    theta      = _load_theta(spec)
    spec_hash  = hashlib.sha256(_SPEC.read_bytes()).hexdigest()[:16]
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    print(f"F3-R2A start  spec_hash={spec_hash}  theta_hash={theta_hash}")
    print(f"  cert_stem={cert_stem}  staged_stem={staged_stem}")

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    _OUT_AV3.mkdir(parents=True, exist_ok=True)

    t1 = task1_repair()
    t2 = task2_anchor_evidence(bp, staged_stem, spec, theta)
    t3 = task3_diagnosis(bp, staged_stem, spec, theta, t2)

    manifest = {
        "f3r2a_artifact":   "f3r2a_repair_manifest_v1",
        "spec_hash":        spec_hash,
        "theta_hash":       theta_hash,
        "staged_stem":      staged_stem,
        "cert_stem":        cert_stem,
        "task1_repair":          t1,
        "task2_anchor_evidence": t2,
        "task3_diagnosis":       t3,
        "total_elapsed_s":  round(time.time() - t_global, 1),
    }

    _atomic_write_json(manifest, _OUT_MANIFEST)
    print(f"\nManifest: {_OUT_MANIFEST}")

    diagnosis = {k: t3[k] for k in [
        "gate_b_pass", "gate_b_results",
        "gate_a_pass", "gate_a_result",
        "gate_c_pass", "gate_c_results",
        "first_divergent_component", "failing_cols_gate_c",
        "verdict", "batch_context_dependence", "joint_batching_licensed",
    ] if k in t3}
    _atomic_write_json(diagnosis, _OUT_DIAGNOSIS)
    print(f"Diagnosis: {_OUT_DIAGNOSIS}")

    task4_report(t1, t2, t3, manifest)

    print(f"\nF3-R2A COMPLETE in {manifest['total_elapsed_s']}s")
    print(f"  Verdict: {t3.get('verdict')}")
    print(f"  Batch-context dependence: {t3.get('batch_context_dependence')}")


if __name__ == "__main__":
    main()
