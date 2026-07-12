"""
P3-1 RUNNER — V_i^IS + W-measure family (W1/W3/W4/W6) + F5 inequality on the NEW P2a
singles-2016 baseline.  NEW FILE; edits no existing script or config.

REUSE MODEL
  - Imports the PROVEN, stem-independent primitives from run_f4a_singles_measure_core.py
    (f4a): `solve_equivalent_income`, `_box_cox`, `_logsumexp_rows`, and the constants
    DCM_FLOOR_EUR / CAP_MULT / BETA_C.  These are pure functions — importing and calling
    them is reuse, not modification.
  - COPY-ADAPTS the per-group building blocks (f4a.GroupState, run_f4a…py:184-275) into
    P2aGroupState because f4a.GroupState._key_to_uid is hard-wired to the certified stem
    (run_f4a…py:168); every mirrored line is cited.
  - COPY-ADAPTS the W1/W3/W4/W6 orchestration VERBATIM from run_f4c_final_singles_measures.py
    (Tasks 2-4) and the survey-weighted inequality battery from run_f5_singles_measure_family.py.

KEY DEVIATION FROM F4C (documented, deliverable 5)
  F4C reads the actual target V_i^IS from an EXTERNAL, F3-reconciled parquet
  (singles_ViIS_dualstem_v1.parquet; run_f4c…py:159-160).  No such file exists for P2a — the
  whole point of P3-1 is to PRODUCE V_i^IS.  We therefore set the target
  V_target = engine inclusive value `lse` (estimation_engine.py:380,404) directly.  Because
  R_shift(0) == lse by construction (see below), the W3 zero-recovery identity
  (welfare_core.py:44-46; run_f4c…py:512-513) is EXACT here — that is deliverable 4's
  consistency check.

V_i^IS DEFINITION
  V_i^IS = lse_i = log Σ_j exp(V_j) over the S=101 alternatives (welfare_core.py:20-22;
  estimation_engine.py:380).  Normalized welfare level V_actual = V_i^IS - log(S), S=101
  (run_f4c…py:196-199).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
for _p in ["scripts/bpool", "scripts/enhanced", "scripts/welfare",
           "scripts/welfare/fastlane", "scripts/pilot"]:
    sys.path.insert(0, str(_REPO / _p))

import jax  # noqa: E402
jax.config.update("jax_enable_x64", True)

import estimation_spec_parser as sp                 # noqa: E402
import joint_recovery_test as jrt                   # noqa: E402
import estimation_utils as eu                       # noqa: E402
import estimation_engine as ee                      # noqa: E402
import run_f4a_singles_measure_core as f4a          # noqa: E402  proven solver + helpers
from _bpool_paths import bpool_dir                  # noqa: E402
from path_helpers import resolve_storage_root       # noqa: E402

_CONFIG = _REPO / "scripts/welfare/configs/welfare_p2a_singles2016.yaml"

# proven pure primitives (imported, not re-implemented)
_box_cox = f4a._box_cox                    # run_f4a…py:149-153
_logsumexp_rows = f4a._logsumexp_rows      # run_f4a…py:156-160
solve = f4a.solve_equivalent_income        # run_f4a…py:281-327
DCM_FLOOR_EUR = f4a.DCM_FLOOR_EUR          # run_f4a…py:56
CAP_MULT = f4a.CAP_MULT                    # run_f4a…py:57
BETA_C = f4a.BETA_C                        # run_f4a…py:61 (utility_consumption_coef_fixed = 1.0)

GROUPS = ("singles_male", "singles_female")
_SUFFIX = {"singles_male": "_sm", "singles_female": "_sf"}


# ---------------------------------------------------------------------------
# per-group state — copy-adapted from f4a.GroupState (run_f4a…py:184-275)
# ---------------------------------------------------------------------------
class P2aGroupState:
    def __init__(self, data, spec, theta, group, c_scale, l_scale):
        self.group = group
        self.c_scale = float(c_scale)
        self.l_scale = float(l_scale)
        ng = int(data.n_groups)
        na = int(data.n_obs // data.n_groups)
        self.n_groups, self.n_alts = ng, na

        # engine components (run_f4a…py:197-205): u, V, lse from the estimator's own kernel
        comp = ee.compute_likelihood_singles(theta, data, spec, return_components=True)
        u = np.asarray(comp["u"], dtype=np.float64).reshape(ng, na)
        V = np.asarray(comp["V"], dtype=np.float64).reshape(ng, na)
        self.lse_engine = np.asarray(comp["lse"], dtype=np.float64)   # V_i^IS
        self.u_grid = u
        self.opp_grid = V - u                                         # held fixed (run_f4a…py:202)
        self.c_norm_grid = np.asarray(data.consumption, np.float64).reshape(ng, na)
        self.l_norm_grid = np.asarray(data.leisure, np.float64).reshape(ng, na)
        self.working_grid = np.asarray(data.working, np.float64).reshape(ng, na)

        fixed = dict(getattr(spec, "fixed_params", {}) or {})

        def P(name):
            if name in fixed:
                return float(fixed[name])
            return float(theta[spec.get_param_index(name)])
        self.theta_c = P(spec.theta_c_param_name(group))             # run_f4a…py:214
        # theta_l for this group (mirror run_f4c…py:133-141)
        tl_name = (spec.utility_leisure_theta + _SUFFIX[group]) if spec.utility_leisure_theta else None
        self.theta_l = 0.0 if tl_name is None else P(tl_name)

        # leisure_term_j = u_j - beta_c * bc_c(c_norm_j)  (run_f4a…py:217-218)
        bc_c_actual = _box_cox(self.c_norm_grid, self.theta_c)
        self.leisure_term_grid = self.u_grid - BETA_C * bc_c_actual

        # home node = lowest-draw working==0 alternative (run_f4a…py:220-226)
        is_home = (self.working_grid == 0)
        self.home_count = is_home.sum(axis=1).astype(int)
        self.home_idx = np.argmax(is_home, axis=1)
        rows = np.arange(ng)
        self.leisure_term_home = self.leisure_term_grid[rows, self.home_idx]

        # group_ids == idhh == stacked_hh_uid for single-year data
        # (estimation_utils.py:824,832 ; harmonise_bpool_engine_ready.py:130)
        self.uids = np.asarray(data.group_ids, dtype=np.int64)

        # V_target = engine inclusive value (P3-1 DEVIATION: produced here, not external)
        self.V_target = self.lse_engine.copy()

        self.min_c_eur = np.min(self.c_norm_grid, axis=1) * self.c_scale   # run_f4a…py:245
        self.max_c_eur = np.max(self.c_norm_grid, axis=1) * self.c_scale

    # reference value functions — verbatim from run_f4a…py:249-275
    def _bc_c_of_eur(self, w_eur_vec):
        return _box_cox(np.asarray(w_eur_vec, np.float64) / self.c_scale, self.theta_c)

    def R_shift(self, w_eur):
        c = self.c_norm_grid + (np.asarray(w_eur, float) / self.c_scale)[:, None]
        bad = np.any(c <= 0.0, axis=1)
        c_safe = np.where(c <= 0.0, np.nan, c)
        u = self.leisure_term_grid + BETA_C * _box_cox(c_safe, self.theta_c)
        R = _logsumexp_rows(u + self.opp_grid)
        return np.where(bad, -np.inf, R)

    def R_replace(self, w_eur):
        bc = self._bc_c_of_eur(w_eur)[:, None]
        u = self.leisure_term_grid + BETA_C * bc
        return _logsumexp_rows(u + self.opp_grid)

    def R_replace_working(self, w_eur):
        bc_w = self._bc_c_of_eur(w_eur)[:, None]
        bc_actual = _box_cox(self.c_norm_grid, self.theta_c)
        bc = np.where(self.working_grid > 0, bc_w, bc_actual)
        u = self.leisure_term_grid + BETA_C * bc
        return _logsumexp_rows(u + self.opp_grid)

    def R_single_node(self, w_eur):
        return self.leisure_term_home + BETA_C * self._bc_c_of_eur(w_eur)


# ---------------------------------------------------------------------------
# singles-only data load — mirrors build_data_objects (joint_recovery_test.py:269-279)
# MINUS the two couples lines (271, 280). Documented in stage_p2a_singles_welfare.py.
# ---------------------------------------------------------------------------
def load_singles(stem):
    df_sm, meta = jrt._load_parquet_slice(stem, "singles", [], 0, sex="male")   # jrt:189,269
    df_sf, _ = jrt._load_parquet_slice(stem, "singles", [], 0, sex="female")    # jrt:270
    data_sm = eu.precompute_data_singles(df_sm, meta, is_male=True,
                                          include_wage_vars=True, include_loc_vars=True)  # jrt:274-276
    data_sf = eu.precompute_data_singles(df_sf, meta, is_male=False,
                                          include_wage_vars=True, include_loc_vars=True)  # jrt:277-279
    return {"singles_male": data_sm, "singles_female": data_sf}, meta


# ---------------------------------------------------------------------------
# V_i^IS + softmax ESS diagnostic (welfare_core.py:483-487)
# ---------------------------------------------------------------------------
def compute_viis(gs):
    comp_V = gs.leisure_term_grid + BETA_C * _box_cox(gs.c_norm_grid, gs.theta_c) + gs.opp_grid
    lse = _logsumexp_rows(comp_V)
    w = np.exp(comp_V - lse[:, None])            # softmax within HH
    ess = 1.0 / np.sum(w * w, axis=1)
    return lse, ess


# ---------------------------------------------------------------------------
# W measures — VERBATIM from run_f4c_final_singles_measures.py Tasks 2-4
# ---------------------------------------------------------------------------
def compute_measures(gs):
    logS = float(np.log(gs.n_alts))              # run_f4c…py:198
    V_actual = gs.V_target - logS                # run_f4c…py:199
    n = gs.n_groups
    rows = np.arange(n)

    # --- W3 (own set + uniform transfer) : run_f4c…py:211-213 ---
    lo3 = -(gs.min_c_eur - 1e-6); hi3 = gs.max_c_eur * CAP_MULT
    r3 = solve(lambda w: gs.R_shift(w) - logS, V_actual, lo3, hi3,
               level_measure=False, expand=False)

    # --- W1 (replace consumption at all nodes) : run_f4c…py:215-217 ---
    lo1 = np.full(n, DCM_FLOOR_EUR); hi1 = gs.max_c_eur * CAP_MULT
    r1 = solve(lambda w: gs.R_replace(w) - logS, V_actual, lo1, hi1, level_measure=True)
    r1wo = solve(lambda w: gs.R_replace_working(w) - logS, V_actual, lo1, hi1, level_measure=True)

    # --- W4 (single home node, full compensation) : run_f4c…py:257-267 ---
    res4 = solve(gs.R_single_node, V_actual, lo1, hi1, level_measure=True)
    rhs = (V_actual - gs.leisure_term_home) / BETA_C
    base = 1.0 + gs.theta_c * rhs
    feas = base > 0
    w_an = np.where(feas, np.power(np.where(feas, base, np.nan), 1.0 / gs.theta_c), np.nan) * gs.c_scale
    in_bracket4 = res4["converged"]
    omega4 = np.where(in_bracket4 & feas, w_an, np.nan)

    # --- W6 (universal hours grid, min-of-equal-pay) : run_f4c…py:298-324 ---
    W6_LEISURE = np.array(CFG["measures"]["_w6_leisure"], dtype=np.float64)
    N_J = len(W6_LEISURE)
    bc_l_grid = _box_cox(gs.l_norm_grid, gs.theta_l)
    jstar = np.argmax(np.abs(bc_l_grid), axis=1)                      # run_f4c…py:307
    beta_l_coeff = gs.leisure_term_grid[rows, jstar] / bc_l_grid[rows, jstar]  # run_f4c…py:309
    coeff_spread = float(np.nanmax(np.abs(beta_l_coeff[:, None] * bc_l_grid - gs.leisure_term_grid)))
    l_norm_univ = W6_LEISURE / gs.l_scale
    bc_l_univ = _box_cox(l_norm_univ, gs.theta_l)
    leisure_term_univ = beta_l_coeff[:, None] * bc_l_univ[None, :]    # run_f4c…py:315

    def R_w6(w_eur, _lt=leisure_term_univ, _gs=gs, _nj=N_J):
        bc = _box_cox(np.asarray(w_eur, float) / _gs.c_scale, _gs.theta_c)[:, None]
        return _logsumexp_rows(_lt + BETA_C * bc) - np.log(_nj)       # run_f4c…py:317-320
    res6 = solve(R_w6, V_actual, lo1, hi1, level_measure=True)
    omega6 = np.where(res6["converged"], res6["omega"], np.nan)

    return {
        "V_target": gs.V_target, "V_actual": V_actual, "logS": logS,
        "W3": r3["omega"], "W3_converged": r3["converged"],
        "W1": r1["omega"], "W1_converged": r1["converged"],
        "W1_below_floor": r1["below_floor"], "W1_above_cap": r1["above_cap"],
        "W1wo": r1wo["omega"], "W1wo_converged": r1wo["converged"],
        "W4": omega4, "W4_bracket_converged": in_bracket4, "W4_above_cap": res4["above_cap"],
        "W6": omega6, "W6_bracket_converged": res6["converged"], "W6_above_cap": res6["above_cap"],
        "w6_coeff_spread": coeff_spread,
    }


# ---------------------------------------------------------------------------
# survey-weighted inequality — copy-adapted from run_f5_singles_measure_family.py:107-171
# ---------------------------------------------------------------------------
def w_mean(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    return float(np.sum(w * x) / np.sum(w))


def w_gini(x, w):                                # run_f5…py:121-131 (Lerman-Yitzhaki)
    x = np.asarray(x, float); w = np.asarray(w, float)
    o = np.argsort(x, kind="mergesort"); x, w = x[o], w[o]
    W = np.sum(w); mu = np.sum(w * x) / W
    cw = np.cumsum(w); r = (cw - 0.5 * w) / W
    return float(2.0 / (W * mu) * np.sum(w * (x - mu) * (r - 0.5)))


def w_cv2(x, w):                                 # run_f5…py:142-146
    mu = w_mean(x, w)
    var = float(np.sum(np.asarray(w, float) * (np.asarray(x, float) - mu) ** 2) / np.sum(w))
    return var / mu ** 2


def w_theil_l(x, w):                             # run_f5…py:156-160
    x = np.asarray(x, float); w = np.asarray(w, float)
    W = np.sum(w); mu = np.sum(w * x) / W
    return float(np.log(mu) - np.sum(w * np.log(x)) / W)


def w_atkinson(x, w, eps):                       # run_f5…py:163-171
    x = np.asarray(x, float); w = np.asarray(w, float)
    W = np.sum(w); mu = np.sum(w * x) / W
    if abs(eps - 1.0) < 1e-12:
        ede = np.exp(np.sum(w * np.log(x)) / W)
    else:
        m = np.sum(w * x ** (1.0 - eps)) / W
        ede = m ** (1.0 / (1.0 - eps))
    return float(1.0 - ede / mu)


def inequality_battery(x, w):
    """All F5 indices on the positive, finite subset (Theil/Atkinson need x>0)."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (x > 0)
    xo, wo = x[ok], w[ok]
    if xo.size == 0:
        return {"n": 0}
    return {
        "n": int(xo.size), "n_dropped_nonpos_or_nan": int((~ok).sum()),
        "weighted_mean": w_mean(xo, wo),
        "gini": w_gini(xo, wo), "cv2": w_cv2(xo, wo), "theil_l": w_theil_l(xo, wo),
        "atkinson_0p5": w_atkinson(xo, wo, 0.5),
        "atkinson_1": w_atkinson(xo, wo, 1.0),
        "atkinson_2": w_atkinson(xo, wo, 2.0),
    }


# ---------------------------------------------------------------------------
def _quantiles(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if x.size == 0:
        return {q: None for q in ("p05", "p25", "p50", "p75", "p95")}
    p = np.quantile(x, [0.05, 0.25, 0.50, 0.75, 0.95])
    return {"p05": float(p[0]), "p25": float(p[1]), "p50": float(p[2]),
            "p75": float(p[3]), "p95": float(p[4]), "n_finite": int(x.size)}


def _dwt_by_uid(stem, group):
    flag = 1.0 if group == "singles_male" else 0.0
    df = pd.read_parquet(bpool_dir() / f"{stem}__singles.parquet",
                         columns=["stacked_hh_uid", "dgn", "dwt"])
    df = df[df["dgn"] == flag].drop_duplicates("stacked_hh_uid")
    return {int(u): float(w) for u, w in zip(df["stacked_hh_uid"], df["dwt"])}


CFG = None


def main():
    global CFG
    t0 = time.time()
    cfg_all = yaml.safe_load(_CONFIG.read_text())["welfare_p2a"]
    CFG = cfg_all
    b = cfg_all["baseline"]
    stem = b["engine_ready_stem"]
    S_expected = int(cfg_all["normalization"]["S_i"])
    w6_hours = list(cfg_all["measures"]["w6_hours"])
    TLH = float(cfg_all["normalization"]["total_leisure_hours"])
    CFG["measures"]["_w6_leisure"] = [TLH - h for h in w6_hours]     # run_f4c…py:49
    n_expected = int(cfg_all["verification"]["expect_n_hh"])
    w3_tol = float(cfg_all["verification"]["w3_zero_recovery_tol_eur"])

    print("P3-1 runner start")
    spec = sp.parse_specification(_REPO / b["spec_yaml_path"])
    theta = np.asarray(jrt.load_theta_star_from_csv(_REPO / b["theta_hat_path"], spec), np.float64)
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    data, meta = load_singles(stem)
    c_scale = float(meta["normalization"]["singles"]["c_scale"])
    l_scale = float(meta["normalization"]["singles"]["l_scale"])
    print(f"  theta_hash={theta_hash}  c_scale={c_scale:.3f}  l_scale={l_scale:.3f}")

    states, viis_rows, meas_rows = {}, [], []
    per_group_ineq, checks = {}, {}
    for g in GROUPS:
        gs = P2aGroupState(data[g], spec, theta, g, c_scale, l_scale)
        states[g] = gs
        if gs.n_alts != S_expected:
            raise SystemExit(f"STOP: {g} has {gs.n_alts} alts, expected S={S_expected}.")
        lse, ess = compute_viis(gs)
        # parity: our reconstructed logsum must equal the engine's own lse
        parity = float(np.max(np.abs(lse - gs.lse_engine)))
        m = compute_measures(gs)
        dwt_map = _dwt_by_uid(stem, g)
        dwt = np.array([dwt_map.get(int(u), np.nan) for u in gs.uids], float)

        for i in range(gs.n_groups):
            viis_rows.append({"uid": int(gs.uids[i]), "group": g, "S_i": gs.n_alts,
                              "V_i_IS": float(lse[i]),
                              "V_actual_normalized": float(lse[i] - m["logS"]),
                              "ess": float(ess[i]), "dwt": float(dwt[i])})
            meas_rows.append({"uid": int(gs.uids[i]), "group": g, "dwt": float(dwt[i]),
                              "W1_omega_eur": float(m["W1"][i]), "W1_converged": bool(m["W1_converged"][i]),
                              "W1_workingonly_omega_eur": float(m["W1wo"][i]),
                              "W3_omega_shift_eur": float(m["W3"][i]), "W3_converged": bool(m["W3_converged"][i]),
                              "W4_omega_eur": (float(m["W4"][i]) if np.isfinite(m["W4"][i]) else None),
                              "W4_bracket_converged": bool(m["W4_bracket_converged"][i]),
                              "W6_omega_eur": (float(m["W6"][i]) if np.isfinite(m["W6"][i]) else None),
                              "W6_bracket_converged": bool(m["W6_bracket_converged"][i])})

        # per-group inequality on headline W1/W4/W6
        per_group_ineq[g] = {W: inequality_battery(m[W], dwt) for W in ("W1", "W4", "W6")}
        checks[g] = {
            "n_hh": gs.n_groups,
            "viis_parity_vs_engine_max_abs": parity,
            "V_i_all_finite": bool(np.isfinite(lse).all()),
            "W3_zero_recovery_max_abs_eur": float(np.nanmax(np.abs(m["W3"]))),
            "w6_coeff_spread": m["w6_coeff_spread"],
            "W1_finite": int(np.isfinite(m["W1"]).sum()),
            "W4_finite": int(np.isfinite(m["W4"]).sum()),
            "W6_finite": int(np.isfinite(m["W6"]).sum()),
        }
        print(f"  {g}: n={gs.n_groups} parity={parity:.2e} "
              f"W3|max|={checks[g]['W3_zero_recovery_max_abs_eur']:.2e} "
              f"W1med={np.nanmedian(m['W1']):.0f} W4med={np.nanmedian(m['W4']):.0f} "
              f"W6med={np.nanmedian(m['W6']):.0f}")

    viis_df = pd.DataFrame(viis_rows).sort_values(["group", "uid"]).reset_index(drop=True)
    meas_df = pd.DataFrame(meas_rows).sort_values(["group", "uid"]).reset_index(drop=True)

    # pooled inequality (both singles groups) on headline measures
    pooled = {}
    for W, col in (("W1", "W1_omega_eur"), ("W4", "W4_omega_eur"), ("W6", "W6_omega_eur")):
        x = meas_df[col].to_numpy(dtype=float)
        w = meas_df["dwt"].to_numpy(dtype=float)
        pooled[W] = inequality_battery(x, w)
    quant = {}
    for W, col in (("W1", "W1_omega_eur"), ("W3", "W3_omega_shift_eur"),
                   ("W4", "W4_omega_eur"), ("W6", "W6_omega_eur")):
        quant[W] = _quantiles(meas_df[col].to_numpy(dtype=float))

    # ---------- verification (deliverable 4) ----------
    n_total = int(meas_df.shape[0])
    ver = {}
    ver["n_hh_ok"] = (n_total == n_expected)
    ver["V_i_all_finite"] = bool(np.isfinite(viis_df["V_i_IS"]).all())
    ver["viis_parity_ok"] = all(checks[g]["viis_parity_vs_engine_max_abs"] < 1e-9 for g in GROUPS)
    ver["W_all_finite_counts"] = {W: int(np.isfinite(meas_df[c].to_numpy(dtype=float)).sum())
                                  for W, c in (("W1", "W1_omega_eur"), ("W4", "W4_omega_eur"),
                                               ("W6", "W6_omega_eur"))}
    ver["gini_in_unit_interval"] = {W: (0.0 < pooled[W]["gini"] < 1.0) for W in ("W1", "W4", "W6")}
    ver["W3_zero_recovery_ok"] = all(checks[g]["W3_zero_recovery_max_abs_eur"] < w3_tol for g in GROUPS)
    ver["W3_identity_quote"] = ("F4C: 'Subtracting log(S) from BOTH actual and own-set reference "
                                "leaves the root unchanged => W3 numerically identical' "
                                "(run_f4c…py:512-513); welfare_core.py:44-46 'Phi_i(0)=0 the W^3 "
                                "reference-recovers-zero sanity check'. Here V_target==engine lse "
                                "so R_shift(0)==lse exactly => W3 omega == 0.")
    all_pass = bool(ver["n_hh_ok"] and ver["V_i_all_finite"] and ver["viis_parity_ok"]
                    and all(v > 0 for v in ver["W_all_finite_counts"].values())
                    and all(ver["gini_in_unit_interval"].values())
                    and ver["W3_zero_recovery_ok"])
    ver["ALL_PASS"] = all_pass

    # ---------- outputs ----------
    outdir = resolve_storage_root() / cfg_all["output"]["storage_subdir"]
    outdir.mkdir(parents=True, exist_ok=True)
    viis_path = outdir / cfg_all["output"]["viis_parquet"]
    meas_path = outdir / cfg_all["output"]["measures_parquet"]
    ineq_path = outdir / cfg_all["output"]["inequality_json"]
    manifest_path = outdir / cfg_all["output"]["manifest_json"]
    report_path = _REPO / cfg_all["output"]["report_md"]

    viis_df.to_parquet(viis_path, index=False)
    meas_df.to_parquet(meas_path, index=False)

    ineq_obj = {"pooled_headline": pooled, "per_group": per_group_ineq, "quantiles": quant,
                "weight_col": cfg_all["weighting"]["weight_col"]}
    ineq_path.write_text(json.dumps(ineq_obj, indent=2, default=_jsonify))

    spec_hash = hashlib.sha256((_REPO / b["spec_yaml_path"]).read_bytes()).hexdigest()[:16]
    manifest = {
        "artifact": "run_manifest_p2a_v1",
        "produced_by": "scripts/welfare/run_p2a_singles_welfare.py",
        "staged_stem": stem, "spec_yaml_path": b["spec_yaml_path"], "spec_hash": spec_hash,
        "theta_hat_path": b["theta_hat_path"], "theta_hash": theta_hash,
        "source_results_json": b["source_results_json"],
        "c_scale": c_scale, "l_scale": l_scale, "S_i": S_expected,
        "row_counts": {"viis": int(len(viis_df)), "measures": int(len(meas_df)),
                       "by_group": {g: int(states[g].n_groups) for g in GROUPS}},
        "checks": checks, "verification": ver,
        "outputs": {"viis": str(viis_path), "measures": str(meas_path),
                    "inequality": str(ineq_path), "report": str(report_path)},
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=_jsonify))
    report_path.write_text(_report(manifest, pooled, quant, checks), encoding="utf-8")

    print("\n--- VERIFICATION ---")
    for k in ("n_hh_ok", "V_i_all_finite", "viis_parity_ok", "W3_zero_recovery_ok"):
        print(f"  {k}: {ver[k]}")
    print(f"  gini_in_unit_interval: {ver['gini_in_unit_interval']}")
    print(f"  ALL_PASS: {all_pass}")
    print(f"\n  wrote: {viis_path.name}, {meas_path.name}, {ineq_path.name}, "
          f"{manifest_path.name}, {report_path.name}")
    print(f"P3-1 runner done in {round(time.time()-t0,1)}s  (PASS={all_pass})")


def _jsonify(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def _report(m, pooled, quant, checks):
    L = []
    L.append("# RURO Welfare P2a — V_i^IS + W-measure family (singles 2016)\n")
    L.append(f"Date: 2026-07-12 · spec_hash `{m['spec_hash']}` · theta_hash `{m['theta_hash']}` · "
             f"stem `{m['staged_stem']}` · S={m['S_i']}/HH · n={m['row_counts']['measures']}\n")
    L.append("Produced by `scripts/welfare/run_p2a_singles_welfare.py` on the NEW P2a baseline. "
             "No re-estimation; θ is a fixed input (results.joint.parameters).\n")

    L.append("## What was run\n")
    L.append("1. Staging (`stage_p2a_singles_welfare.py`): `stacked_hh_uid=idhh` "
             "(invert harmonise_bpool_engine_ready.py:130), `year_tag=2` "
             "(harmonise:20,131; single 2016 wave), canonical θ CSV from results JSON.")
    L.append("2. V_i^IS = engine logsum `lse` (estimation_engine.py:380); normalized "
             "`V_actual = V_i^IS − log(101)` (run_f4c…py:196-199).")
    L.append("3. W1/W3/W4/W6 verbatim from F4C Tasks 2-4; inequality from F5 primitives.\n")

    L.append("## Deviation from F4C literals (and why)\n")
    L.append("- **Actual target source.** F4C reads V_i^IS from the external F3-reconciled "
             "`singles_ViIS_dualstem_v1.parquet` (run_f4c…py:159-160). P2a has no such file — "
             "P3-1 PRODUCES V_i^IS — so `V_target = engine lse` directly. Consequence: the W3 "
             "zero-recovery identity is EXACT (not merely ≈ F4A).")
    L.append("- **Couples path.** `build_data_objects` always loads couples (jrt:271); P2a is "
             "singles-only, so the runner calls the singles primitives directly (jrt:189,274-279), "
             "no couples artifact written.")
    L.append("- **No S=101/N=5007 hard guard.** F4C asserts N=5007 (run_f4c…py:188); P2a has "
             "1,555 HH, so the runner checks `n==expect_n_hh` (1,555) and `alts==S_i` (101) instead.\n")

    L.append("## Headline numbers\n")
    L.append("| measure | median ω (EUR) | p05 | p95 | weighted Gini (pooled) |")
    L.append("|---|---:|---:|---:|---:|")
    for W in ("W1", "W4", "W6"):
        q = quant[W]; g = pooled[W]["gini"]
        L.append(f"| {W} | {q['p50']:.0f} | {q['p05']:.0f} | {q['p95']:.0f} | {g:.4f} |")
    L.append(f"\nW3 (own-set laissez-faire transfer) is the identity readout: median "
             f"{quant['W3']['p50']:.2e} EUR, |max| "
             f"{max(checks[g]['W3_zero_recovery_max_abs_eur'] for g in GROUPS):.2e} EUR ≈ 0.\n")

    L.append("## Inequality battery (pooled, dwt-weighted, headline)\n")
    L.append("| measure | Gini | CV² | Theil-L | Atkinson(0.5) | Atkinson(1) | Atkinson(2) |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for W in ("W1", "W4", "W6"):
        p = pooled[W]
        L.append(f"| {W} | {p['gini']:.4f} | {p['cv2']:.4f} | {p['theil_l']:.4f} | "
                 f"{p['atkinson_0p5']:.4f} | {p['atkinson_1']:.4f} | {p['atkinson_2']:.4f} |")

    L.append("\n## Verification (deliverable 4)\n")
    v = m["verification"]
    L.append(f"- V_i finite for all {m['row_counts']['measures']} HH: **{v['V_i_all_finite']}**")
    L.append(f"- reconstructed-logsum vs engine lse parity < 1e-9: **{v['viis_parity_ok']}**")
    L.append(f"- W finite counts: {v['W_all_finite_counts']}")
    L.append(f"- pooled Gini(W) ∈ (0,1): {v['gini_in_unit_interval']}")
    L.append(f"- W3 zero-recovery identity holds: **{v['W3_zero_recovery_ok']}** — {v['W3_identity_quote']}")
    L.append(f"\n**ALL_PASS: {v['ALL_PASS']}**\n")

    L.append("## Outputs\n")
    for k, p in m["outputs"].items():
        L.append(f"- {k}: `{p}`")
    L.append("\nNo existing script/config modified; no commit.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
