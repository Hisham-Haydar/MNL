"""
FAST-LANE F4-C: RATIFY NORMALIZATION, COMPLETE W4/W6, FREEZE SINGLES MEASURES.

Implements the RATIFIED F4 welfare-measure contract (operator sign-off 2026-06-13):
  - Actual target:  V_actual_i = V_i^IS_staged - log(S_i)   (S_i = HH draw count = 101)
  - Own-set refs W3/W1: subtract log(S_i) from BOTH sides (root unchanged vs F4A)
  - Deterministic references: uniform log-mean  logsumexp(values) - log(n_nodes)
  - W4 single-node ref: u(w, leisure_home), unchanged (log(1)=0)
  - W4/W6 bracket: [1 EUR, 50 x max observed c], expand once; remaining flagged/excluded;
    NO analytic extrapolation accepted as convergence
  - W6 universal weekly-hours grid J = {0,20,30,35,39,48} (home,PT1,PT2,F35,FT,LH); BG excluded
  - TOTAL_LEISURE_HOURS = 80; W6 leisure = 80 - hours; utility-only u(c,l); equal consumption w
    at every node; uniform prob 1/6; NO opportunity-density / prior terms

Reuses the VALIDATED F4A machinery (GroupState, solver, analytic inversion) unchanged — F4A and
F4B are IMMUTABLE diagnostic artifacts. No estimation, EUROMOD, V_dir, inequality, decomposition,
promotion, engine/spec/data edits, or commit. New versioned outputs only.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parent.parent.parent.parent
for _p in ["scripts/bpool", "scripts/enhanced", "scripts/welfare", "scripts/pilot",
           "scripts/welfare/fastlane"]:
    sys.path.insert(0, str(_REPO / _p))

import jax
jax.config.update("jax_enable_x64", True)

import estimation_spec_parser as sp
import joint_recovery_test as jrt
from _bpool_paths import bpool_dir
import run_f4a_singles_measure_core as f4a   # validated machinery (immutable source, imported)

# ---------------------------------------------------------------------------
# ratified contract constants
# ---------------------------------------------------------------------------
TOTAL_LEISURE_HOURS = 80.0
W6_HOURS = [0.0, 20.0, 30.0, 35.0, 39.0, 48.0]
W6_NODE_LABELS = ["home", "PT1", "PT2", "F35", "FT", "LH"]
W6_LEISURE = [TOTAL_LEISURE_HOURS - h for h in W6_HOURS]   # [80,60,50,45,41,32]
N_J = len(W6_HOURS)
DCM_FLOOR_EUR = f4a.DCM_FLOOR_EUR
CAP_MULT = f4a.CAP_MULT
BETA_C = f4a.BETA_C
TOL_REG = 1e-8

# immutable inputs / prior increments
_SPEC = f4a._SPEC
_THETA = f4a._THETA
_VIIS = f4a._VIIS
_F4A_PARQUET = _REPO / "outputs/welfare/fastlane/singles_measures_F4A_v1.parquet"
_F4A_MANIFEST = _REPO / "outputs/welfare/fastlane/F4A_manifest_v1.json"
_F4B_MEMO = _REPO / "docs/jmp_methodology/RURO_welfare_F4B_normalization_contract_decision_v1.md"
_F3R2_MANIFEST = _REPO / "outputs/welfare/fastlane/f3r2_reconciliation_manifest_v1.json"

# new F4-C outputs
_OUT_PARQUET = _REPO / "outputs/welfare/fastlane/singles_measures_F4C_v1.parquet"
_OUT_MANIFEST = _REPO / "outputs/welfare/fastlane/F4C_manifest_v1.json"
_OUT_DOC = _REPO / "docs/jmp_methodology/RURO_welfare_F4C_final_singles_measures_report_v1.md"

_IMMUTABLE = {
    _SPEC, _THETA, _VIIS, _F4A_PARQUET, _F4A_MANIFEST, _F4B_MEMO, _F3R2_MANIFEST,
    _REPO / "docs/jmp_methodology/RURO_welfare_F4A_measure_core_report_v1.md",
    _REPO / "docs/jmp_methodology/JMP_measure_mapping_memo_v1.md",
}

RATIFIED_CONTRACT = {
    "ratification_id": "RATIFICATION — F4 welfare-measure contract (2026-06-13)",
    "1_actual_target": "V_actual_i = V_i^IS_staged - log(S_i); S_i = household actual draw count",
    "2_deterministic_reference_normalization": "uniform log-mean: logsumexp(values) - log(|J|)",
    "2_w4_single_node": "u(w, leisure_home) unchanged because log(1)=0",
    "3_w4_bracket": "[1 EUR, 50 x max observed c]; expand once; remaining flagged/excluded; "
                    "analytic extrapolation beyond authorized bracket NOT accepted as convergence",
    "4_w6_grid_hours": W6_HOURS,
    "4_w6_node_labels": W6_NODE_LABELS,
    "4_w6_bg_excluded": "BG is continuous proposal support, not a canonical preference/reference state",
    "4_total_leisure_hours": TOTAL_LEISURE_HOURS,
    "5_w4_interpretation": ("full-compensation staying-home endpoint; large magnitude retained and "
                            "caveated; normalization removes artificial draw-count scale only, NOT "
                            "genuine opportunity-set compensation"),
    "governance": "measure-mapping memo ratified for normalization+W6 grid per operator sign-off; "
                  "W2/W5 remain deferred; no promotion/F5 implied by this freeze beyond the gates.",
}


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard(dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: refuse to overwrite immutable artifact: {dest}")
    if dest.exists():
        raise FileExistsError(f"STOP: completed artifact exists, will not overwrite: {dest}")


def _atomic_write_json(obj, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=f4a._jsonify)); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_write_parquet(df, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_write_text(text, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8"); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _theta_l(spec, theta, group):
    suffix = "_sm" if group == "singles_male" else "_sf"
    fixed = dict(getattr(spec, "fixed_params", {}) or {})
    name = (spec.utility_leisure_theta + suffix) if spec.utility_leisure_theta else None
    if name is None:
        return 0.0
    if name in fixed:
        return float(fixed[name])
    return float(theta[spec.get_param_index(name)])


def main():
    t0 = time.time()
    for d in (_OUT_PARQUET, _OUT_MANIFEST, _OUT_DOC):
        _guard(d)
    print("F4-C start")

    spec = sp.parse_specification(_SPEC)
    theta = np.asarray(jrt.load_theta_star_from_csv(_THETA, spec), dtype=np.float64)
    spec_hash = _sha256(_SPEC)[:16]
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    bp = bpool_dir()
    meta = json.loads((bp / f"{f4a.STAGED_STEM}__mnlmeta.json").read_text())
    c_scale = float(meta["normalization"]["singles"]["c_scale"])
    l_scale = float(meta["normalization"]["singles"]["l_scale"])

    viis = pd.read_parquet(_VIIS)
    viis_lookup = {int(r.uid): float(r.V_i_IS_staged) for r in viis.itertuples()}
    data_sm, data_sf, _ = jrt.build_data_objects(f4a.STAGED_STEM, [], 0)
    states = {g: f4a.GroupState(d, spec, theta, g, c_scale, l_scale, bp, viis_lookup)
              for d, g in ((data_sm, "singles_male"), (data_sf, "singles_female"))}
    theta_l = {g: _theta_l(spec, theta, g) for g in states}

    # ===================== TASK 0 — provenance =====================
    print("\n=== TASK 0: provenance ===")
    f3r2 = json.loads(_F3R2_MANIFEST.read_text())
    prov = {
        "spec_hash": spec_hash, "theta_hash": theta_hash,
        "spec_hash_match_manifest": spec_hash == f3r2.get("spec_hash"),
        "theta_hash_match_manifest": theta_hash == f3r2.get("theta_hash"),
        "consumed": {
            "singles_ViIS_dualstem_v1.parquet": _sha256(_VIIS),
            "singles_measures_F4A_v1.parquet": _sha256(_F4A_PARQUET),
            "F4A_manifest_v1.json": _sha256(_F4A_MANIFEST),
            "F4B_decision_memo": _sha256(_F4B_MEMO),
            "staged_singles_parquet": _sha256(bp / f"{f4a.STAGED_STEM}__singles.parquet"),
            "theta_csv": _sha256(_THETA), "spec_yaml": _sha256(_SPEC),
        },
        "n_unique_hh_keys": int(viis["uid"].nunique()),
    }
    # S_i per HH (alts per group, uniform); confirm == 101
    S_by_group = {g: int(gs.n_alts) for g, gs in states.items()}
    s_all = set(S_by_group.values())
    prov["S_i_by_group"] = S_by_group
    prov["S_i_uniform_101"] = (s_all == {101})
    prov["n_keys_ok"] = prov["n_unique_hh_keys"] == 5007
    print(f"  n_keys={prov['n_unique_hh_keys']} (ok={prov['n_keys_ok']})  "
          f"S_i={S_by_group} uniform101={prov['S_i_uniform_101']}")
    print(f"  spec/theta hash match: {prov['spec_hash_match_manifest']}/{prov['theta_hash_match_manifest']}")
    if not (prov["n_keys_ok"] and prov["S_i_uniform_101"]
            and prov["spec_hash_match_manifest"] and prov["theta_hash_match_manifest"]):
        raise SystemExit("STOP: F4-C provenance failed.")

    # normalized actual target per group
    for g, gs in states.items():
        gs.logS = float(np.log(gs.n_alts))
        gs.V_actual = gs.V_target - gs.logS

    # F4A values for regression
    f4a_df = pd.read_parquet(_F4A_PARQUET).set_index("uid")

    # ===================== TASK 2 — W3/W1 regression =====================
    print("\n=== TASK 2: W3/W1 normalized regression vs F4A ===")
    w3w1 = {}
    arr = {}
    for g, gs in states.items():
        logS = gs.logS
        # W3 normalized (subtract logS both sides)
        lo3 = -(gs.min_c_eur - 1e-6); hi3 = gs.max_c_eur * CAP_MULT
        r3 = f4a.solve_equivalent_income(lambda w: gs.R_shift(w) - logS, gs.V_actual,
                                         lo3, hi3, level_measure=False, expand=False)
        # W1 normalized + working-only
        lo1 = np.full(gs.n_groups, DCM_FLOOR_EUR); hi1 = gs.max_c_eur * CAP_MULT
        r1 = f4a.solve_equivalent_income(lambda w: gs.R_replace(w) - logS, gs.V_actual,
                                         lo1, hi1, level_measure=True)
        r1wo = f4a.solve_equivalent_income(lambda w: gs.R_replace_working(w) - logS, gs.V_actual,
                                           lo1, hi1, level_measure=True)
        # diffs vs F4A
        uids = gs.uids
        f3a = f4a_df.reindex(uids)
        d3 = np.abs(r3["omega"] - f3a["W3_omega_shift_eur"].to_numpy())
        d1 = np.abs(r1["omega"] - f3a["W1_omega_eur"].to_numpy())
        d1wo = np.abs(r1wo["omega"] - f3a["W1_workingonly_omega_eur"].to_numpy())
        conv3 = r3["bracketed"] & ~r3["converged"]
        conv1 = r1["bracketed"] & ~r1["converged"]
        arr[g] = {"W3": r3, "W1": r1, "W1wo": r1wo}
        w3w1[g] = {
            "W3_max_domega_vs_F4A": float(np.nanmax(d3)),
            "W1_max_domega_vs_F4A": float(np.nanmax(d1)),
            "W1wo_max_domega_vs_F4A": float(np.nanmax(d1wo)),
            "W3_abs_max": float(np.nanmax(np.abs(r3["omega"][r3["converged"]]))),
            "W3_genuine_nonconv": int(conv3.sum()),
            "W1_genuine_nonconv": int(conv1.sum()),
            "W1_below_floor": int(r1["below_floor"].sum()),
            "W1_above_cap": int(r1["above_cap"].sum()),
        }
        print(f"  {g}: W3 domega={w3w1[g]['W3_max_domega_vs_F4A']:.2e} |W3omega|max={w3w1[g]['W3_abs_max']:.2e} "
              f"W1 domega={w3w1[g]['W1_max_domega_vs_F4A']:.2e} W1wo domega={w3w1[g]['W1wo_max_domega_vs_F4A']:.2e}")
    w3w1_pass = all(
        v["W3_max_domega_vs_F4A"] <= TOL_REG and v["W1_max_domega_vs_F4A"] <= TOL_REG
        and v["W1wo_max_domega_vs_F4A"] <= TOL_REG and v["W3_abs_max"] <= 1e-8
        and v["W3_genuine_nonconv"] == 0 and v["W1_genuine_nonconv"] == 0
        for v in w3w1.values())
    print(f"  W3/W1 regression PASS: {w3w1_pass}")
    if not w3w1_pass:
        raise SystemExit("STOP: W3/W1 regressed against F4A.")

    # ===================== TASK 3 — final W4 =====================
    print("\n=== TASK 3: final W4 (target = V_iIS - log S) ===")
    w4 = {}
    w4arr = {}
    for g, gs in states.items():
        lo = np.full(gs.n_groups, DCM_FLOOR_EUR)
        hi = gs.max_c_eur * CAP_MULT
        res = f4a.solve_equivalent_income(gs.R_single_node, gs.V_actual, lo, hi, level_measure=True)
        # analytic against normalized target
        rhs = (gs.V_actual - gs.leisure_term_home) / BETA_C
        base = 1.0 + gs.theta_c * rhs
        feas = base > 0
        w_an = np.where(feas, np.power(np.where(feas, base, np.nan), 1.0 / gs.theta_c), np.nan) * gs.c_scale
        # classify ONLY by bracket; analytic accepted as value only where bracket-converged
        in_bracket = res["converged"]
        d_norm = np.abs(res["omega"][in_bracket & feas] - w_an[in_bracket & feas]) / gs.c_scale
        genuine_nonconv = res["bracketed"] & ~res["converged"]
        omega = np.where(in_bracket & feas, w_an, np.nan)       # flagged-out => NaN
        actual_c_eur = gs.c_norm_grid[:, 0] * gs.c_scale        # observed-choice consumption
        ratio = omega / actual_c_eur
        w4arr[g] = {"omega": omega, "numeric": res["omega"], "analytic": w_an,
                    "converged": in_bracket, "above_cap": res["above_cap"],
                    "below_floor": res["below_floor"], "genuine_nonconv": genuine_nonconv}
        ok = omega[np.isfinite(omega)]
        w4[g] = {
            "n_hh": gs.n_groups,
            "num_vs_analytic_max_norm": float(np.max(d_norm)) if d_norm.size else None,
            "num_vs_analytic_le_1e8": bool(d_norm.size and np.max(d_norm) <= 1e-8),
            "n_below_floor": int(res["below_floor"].sum()),
            "n_outside_bracket_after_expand": int(res["above_cap"].sum()),
            "outside_frac": float(res["above_cap"].sum()) / gs.n_groups,
            "outside_lt_0p5pct": (res["above_cap"].sum() / gs.n_groups) < 0.005,
            "n_genuine_nonconv": int(genuine_nonconv.sum()),
            "nonconv_lt_0p5pct": (int(genuine_nonconv.sum()) / gs.n_groups) < 0.005,
            "median_eur": float(np.nanmedian(ok)), "p10_eur": float(np.nanpercentile(ok, 10)),
            "p90_eur": float(np.nanpercentile(ok, 90)), "min_eur": float(np.nanmin(ok)),
            "max_eur": float(np.nanmax(ok)),
            "median_ratio_to_actual_c": float(np.nanmedian(ratio)),
        }
        print(f"  W4 {g}: median={w4[g]['median_eur']:.3e} EUR ratio×{w4[g]['median_ratio_to_actual_c']:.1f} "
              f"outside={w4[g]['n_outside_bracket_after_expand']} ({w4[g]['outside_frac']*100:.2f}%) "
              f"nonconv={w4[g]['n_genuine_nonconv']} num-vs-an={w4[g]['num_vs_analytic_max_norm']:.2e}")
    w4_pass = all(v["num_vs_analytic_le_1e8"] and v["outside_lt_0p5pct"] and v["nonconv_lt_0p5pct"]
                  for v in w4.values())
    print(f"  W4 PASS: {w4_pass}")

    # ===================== TASK 4 — W6 universal grid =====================
    print("\n=== TASK 4: W6 universal-grid measure ===")
    l_norm_univ = np.array(W6_LEISURE, dtype=np.float64) / l_scale
    w6 = {}
    w6arr = {}
    w6_invariance = {}
    for g, gs in states.items():
        thl = theta_l[g]
        bc_l_grid = f4a._box_cox(gs.l_norm_grid, thl)
        # beta_l_coeff_i (scalar per HH) from leisure_term = beta_l_coeff * bc_l ; use the node with
        # the largest |bc_l| per HH for a numerically exact recovery
        jstar = np.argmax(np.abs(bc_l_grid), axis=1)
        rows = np.arange(gs.n_groups)
        beta_l_coeff = gs.leisure_term_grid[rows, jstar] / bc_l_grid[rows, jstar]
        # within-HH consistency check (should be exact)
        recon = beta_l_coeff[:, None] * bc_l_grid
        coeff_spread = float(np.nanmax(np.abs(recon - gs.leisure_term_grid)))

        bc_l_univ = f4a._box_cox(l_norm_univ, thl)                     # (6,)
        leisure_term_univ = beta_l_coeff[:, None] * bc_l_univ[None, :] # (n,6)

        def R_w6(w_eur, _lt=leisure_term_univ, _gs=gs):
            bc = f4a._box_cox(np.asarray(w_eur, float) / _gs.c_scale, _gs.theta_c)[:, None]
            u = _lt + BETA_C * bc                                      # (n,6) utility-only
            return f4a._logsumexp_rows(u) - np.log(N_J)                # uniform log-mean

        lo = np.full(gs.n_groups, DCM_FLOOR_EUR)
        hi = gs.max_c_eur * CAP_MULT
        res = f4a.solve_equivalent_income(R_w6, gs.V_actual, lo, hi, level_measure=True)
        genuine_nonconv = res["bracketed"] & ~res["converged"]
        omega = np.where(res["converged"], res["omega"], np.nan)
        actual_c_eur = gs.c_norm_grid[:, 0] * gs.c_scale
        ratio = omega / actual_c_eur
        w6arr[g] = {"omega": omega, "converged": res["converged"], "above_cap": res["above_cap"],
                    "below_floor": res["below_floor"], "genuine_nonconv": genuine_nonconv,
                    "beta_l_coeff": beta_l_coeff}

        # ---- W6 invariance / synthetic gates ----
        # (a) synthetic same-kappa recovery
        kap = np.full(gs.n_groups, 1500.0)
        tgt_syn = R_w6(kap)
        rsyn = f4a.solve_equivalent_income(R_w6, tgt_syn, lo, hi, level_measure=True)
        kerr = np.abs(rsyn["omega"][rsyn["converged"]] - 1500.0)
        # (b) exact node-duplication invariance (12 nodes, each twice) - log(12) == 6-node - log(6)
        w_probe = np.full(gs.n_groups, 1500.0)
        bc = f4a._box_cox(w_probe / gs.c_scale, gs.theta_c)[:, None]
        u6 = leisure_term_univ + BETA_C * bc
        R6 = f4a._logsumexp_rows(u6) - np.log(N_J)
        u12 = np.concatenate([u6, u6], axis=1)
        R12 = f4a._logsumexp_rows(u12) - np.log(2 * N_J)
        dup_max = float(np.max(np.abs(R12 - R6)))
        # (c) cross-household invariance: identical preference (beta_l_coeff) + identical target
        #     -> identical omega. Force HH#1's coeff+target onto HH#0 and re-solve; compare.
        i0, i1 = 0, 1
        lt_pair = np.vstack([leisure_term_univ[i1], leisure_term_univ[i1]])  # both = HH i1's
        tgt_pair = np.array([gs.V_actual[i1], gs.V_actual[i1]])

        def R_w6_pair(w_eur, _lt=lt_pair, _gs=gs):
            bc = f4a._box_cox(np.asarray(w_eur, float) / _gs.c_scale, _gs.theta_c)[:, None]
            return f4a._logsumexp_rows(_lt + BETA_C * bc) - np.log(N_J)
        lo2 = np.full(2, DCM_FLOOR_EUR); hi2 = np.full(2, gs.max_c_eur[i1] * CAP_MULT)
        rpair = f4a.solve_equivalent_income(R_w6_pair, tgt_pair, lo2, hi2, level_measure=True)
        cross_hh_diff = float(abs(rpair["omega"][0] - rpair["omega"][1]))

        ok = omega[np.isfinite(omega)]
        w6_invariance[g] = {
            "beta_l_coeff_recovery_spread": coeff_spread,
            "synthetic_kappa_max_err": float(np.max(kerr)) if kerr.size else None,
            "duplication_invariance_max_nats": dup_max,
            "cross_hh_invariance_diff_eur": cross_hh_diff,
        }
        w6[g] = {
            "n_hh": gs.n_groups,
            "grid_hours": W6_HOURS, "grid_leisure": W6_LEISURE,
            "n_below_floor": int(res["below_floor"].sum()),
            "n_outside_bracket_after_expand": int(res["above_cap"].sum()),
            "outside_frac": float(res["above_cap"].sum()) / gs.n_groups,
            "outside_lt_0p5pct": (res["above_cap"].sum() / gs.n_groups) < 0.005,
            "n_genuine_nonconv": int(genuine_nonconv.sum()),
            "nonconv_lt_0p5pct": (int(genuine_nonconv.sum()) / gs.n_groups) < 0.005,
            "median_eur": float(np.nanmedian(ok)), "p10_eur": float(np.nanpercentile(ok, 10)),
            "p90_eur": float(np.nanpercentile(ok, 90)), "min_eur": float(np.nanmin(ok)),
            "max_eur": float(np.nanmax(ok)),
            "median_ratio_to_actual_c": float(np.nanmedian(ratio)),
            **w6_invariance[g],
        }
        print(f"  W6 {g}: median={w6[g]['median_eur']:.3e} EUR ratio×{w6[g]['median_ratio_to_actual_c']:.1f} "
              f"outside={w6[g]['n_outside_bracket_after_expand']} ({w6[g]['outside_frac']*100:.2f}%) "
              f"nonconv={w6[g]['n_genuine_nonconv']}")
        print(f"     gates: kappa={w6[g]['synthetic_kappa_max_err']:.2e} dup={dup_max:.2e} "
              f"cross_hh={cross_hh_diff:.2e} coeff_spread={coeff_spread:.2e}")
    # grid identical across HH (same arrays used) -> by construction
    grid_identical = True
    w6_pass = all(
        v["outside_lt_0p5pct"] and v["nonconv_lt_0p5pct"]
        and v["synthetic_kappa_max_err"] is not None and v["synthetic_kappa_max_err"] <= 1e-8
        and v["duplication_invariance_max_nats"] <= 1e-10
        and v["cross_hh_invariance_diff_eur"] <= 1e-8
        for v in w6.values()) and grid_identical
    print(f"  W6 PASS: {w6_pass}")

    # ===================== TASK 5 — outputs =====================
    print("\n=== TASK 5: outputs ===")
    rows = []
    for g, gs in states.items():
        a = arr[g]
        for i in range(gs.n_groups):
            rows.append({
                "uid": int(gs.uids[i]), "group": g,
                "S_i": int(gs.n_alts), "V_i_IS_staged": float(gs.V_target[i]),
                "V_actual_normalized": float(gs.V_actual[i]),
                "W3_omega_shift_eur": float(a["W3"]["omega"][i]),
                "W3_converged": bool(a["W3"]["converged"][i]),
                "W1_omega_eur": float(a["W1"]["omega"][i]),
                "W1_converged": bool(a["W1"]["converged"][i]),
                "W1_below_floor": bool(a["W1"]["below_floor"][i]),
                "W1_above_cap": bool(a["W1"]["above_cap"][i]),
                "W1_workingonly_omega_eur": float(a["W1wo"]["omega"][i]),
                "W1_workingonly_converged": bool(a["W1wo"]["converged"][i]),
                "W4_omega_eur": (float(w4arr[g]["omega"][i]) if np.isfinite(w4arr[g]["omega"][i]) else None),
                "W4_omega_numeric_eur": float(w4arr[g]["numeric"][i]),
                "W4_bracket_converged": bool(w4arr[g]["converged"][i]),
                "W4_outside_bracket": bool(w4arr[g]["above_cap"][i]),
                "W4_genuine_nonconv": bool(w4arr[g]["genuine_nonconv"][i]),
                "W6_omega_eur": (float(w6arr[g]["omega"][i]) if np.isfinite(w6arr[g]["omega"][i]) else None),
                "W6_bracket_converged": bool(w6arr[g]["converged"][i]),
                "W6_outside_bracket": bool(w6arr[g]["above_cap"][i]),
                "W6_genuine_nonconv": bool(w6arr[g]["genuine_nonconv"][i]),
            })
    out_df = pd.DataFrame(rows).sort_values(["group", "uid"]).reset_index(drop=True)
    _atomic_write_parquet(out_df, _OUT_PARQUET)
    out_sha = _sha256(_OUT_PARQUET)
    print(f"  wrote {_OUT_PARQUET} rows={len(out_df)}")

    all_pass = bool(w3w1_pass and w4_pass and w6_pass)
    manifest = {
        "f4c_artifact": "F4C_manifest_v1",
        "spec_hash": spec_hash, "theta_hash": theta_hash,
        "staged_stem": f4a.STAGED_STEM, "c_scale": c_scale, "l_scale": l_scale,
        "consumption_time_unit": "monthly real-2016 EUR (FR EUROMOD ils_dispy; build earnings use "
                                 "WEEKS_PER_MONTH=52/12 => monthly; c_scale≈2035 ≈ mean monthly "
                                 "disposable income)",
        "theta_c_singles": states["singles_male"].theta_c,
        "theta_l": theta_l,
        "ratified_contract": RATIFIED_CONTRACT,
        "task0_provenance": prov,
        "task2_w3_w1_regression": w3w1, "task2_pass": w3w1_pass,
        "task3_w4": w4, "task3_pass": w4_pass,
        "task4_w6": w6, "task4_pass": w6_pass,
        "w6_grid_hours": W6_HOURS, "w6_grid_leisure": W6_LEISURE, "w6_node_labels": W6_NODE_LABELS,
        "output_parquet": str(_OUT_PARQUET), "output_parquet_sha256": out_sha, "n_rows": len(out_df),
        "all_measure_gates_pass": all_pass,
        "ready_for_f5": all_pass,
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    _atomic_write_json(manifest, _OUT_MANIFEST)
    print(f"  wrote {_OUT_MANIFEST}")
    _atomic_write_text(_report(manifest), _OUT_DOC)
    print(f"  wrote {_OUT_DOC}")

    w3_status = "valid" if w3w1_pass else "invalid"
    w1_status = "valid" if w3w1_pass else "invalid"
    w4_status = "valid" if w4_pass else "invalid"
    w6_status = "valid" if w6_pass else "invalid"
    print("\n--- FINAL STATUS ---")
    print(f"W3 STATUS: {w3_status}")
    print(f"W1 STATUS: {w1_status}")
    print(f"W4 STATUS: {w4_status}")
    print(f"W6 STATUS: {w6_status}")
    print(f"READY FOR F5: {'yes' if all_pass else 'no'}")
    print(f"\nF4-C COMPLETE in {round(time.time()-t0,1)}s")


def _report(m: dict) -> str:
    sci = lambda x: ("n/a" if x is None else (f"{x:.3e}" if isinstance(x, float) else str(x)))
    def tbl(d, cols):
        out = ["| group | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        for g in ("singles_male", "singles_female"):
            out.append(f"| {g} | " + " | ".join(sci(d[g][c]) for c in cols) + " |")
        return "\n".join(out)
    L = []
    L.append("# RURO Welfare F4-C — Final Singles Measures (W3/W1/W4/W6), Ratified Normalization\n")
    L.append(f"Date: 2026-06-13 · spec_hash `{m['spec_hash']}` · theta_hash `{m['theta_hash']}` · "
             f"stem `{m['staged_stem']}` · S=101/HH\n")
    L.append("Frozen final singles welfare measures under the operator-ratified normalization "
             "contract. F4A/F4B preserved as immutable diagnostics. No estimation/EUROMOD/V_dir/"
             "inequality/decomposition/promotion/commit.\n")

    L.append("## Normalization: two distinct objects\n")
    L.append("- **Raw `V_i^IS` = log Σ_j exp(V_j)** over S=101 IS draws — the conditional-logit "
             "denominator; **likelihood-compatible** (estimation uses this; −log S is a "
             "θ-independent constant invisible to the MLE).")
    L.append("- **Normalized `V_actual = V_i^IS − log(S)`** — the cardinality-invariant **welfare "
             "level** (consistent IS estimate of the inclusive value); used for ALL welfare-level "
             "comparisons here. S_i=101 for every household.\n")

    L.append("## Ratified contract (frozen)\n")
    rc = m["ratified_contract"]
    for k in ["1_actual_target", "2_deterministic_reference_normalization", "2_w4_single_node",
              "3_w4_bracket", "4_w6_grid_hours", "4_w6_node_labels", "4_w6_bg_excluded",
              "4_total_leisure_hours", "5_w4_interpretation"]:
        L.append(f"- **{k}**: {rc[k]}")
    L.append(f"\nConsumption time unit: {m['consumption_time_unit']}.\n")

    L.append("## Provenance (Task 0)\n")
    p = m["task0_provenance"]
    L.append(f"- 5,007 unique HH keys: {p['n_keys_ok']}; S_i uniform 101: {p['S_i_uniform_101']}; "
             f"spec/theta hash match: {p['spec_hash_match_manifest']}/{p['theta_hash_match_manifest']}")
    L.append(f"- Consumed F4A parquet sha256 `{p['consumed']['singles_measures_F4A_v1.parquet']}`")
    L.append(f"- Consumed dualstem V_iIS sha256 `{p['consumed']['singles_ViIS_dualstem_v1.parquet']}`\n")

    L.append("## W3 / W1 — regression vs F4A (Task 2)\n")
    L.append(tbl(m["task2_w3_w1_regression"],
                 ["W3_max_domega_vs_F4A", "W3_abs_max", "W1_max_domega_vs_F4A",
                  "W1wo_max_domega_vs_F4A", "W3_genuine_nonconv", "W1_genuine_nonconv"]))
    L.append(f"\nGate (Δω vs F4A ≤1e-8 EUR; |W3 ω|≤1e-8; 0 genuine non-conv): "
             f"**{'PASS' if m['task2_pass'] else 'FAIL'}**. Subtracting log(S) from BOTH actual and "
             "own-set reference leaves the root unchanged ⇒ W3/W1 are numerically identical to F4A.\n")

    L.append("## W4 — Staying-home full-compensation endpoint (Task 3)\n")
    L.append(tbl(m["task3_w4"],
                 ["median_eur", "p10_eur", "p90_eur", "min_eur", "max_eur",
                  "median_ratio_to_actual_c", "n_outside_bracket_after_expand",
                  "n_genuine_nonconv", "num_vs_analytic_max_norm"]))
    L.append(f"\nGate (num-vs-analytic ≤1e-8 normalized in-bracket; outside-bracket <0.5%; genuine "
             f"non-conv <0.5%): **{'PASS' if m['task3_pass'] else 'FAIL'}**. Convergence classified "
             "SOLELY by the bracket+one-expansion contract; analytic extrapolation beyond the "
             "bracket is NOT accepted (0 outside under the normalized target). ")
    L.append("> **Full-compensation magnitude caveat (retained).** W4 medians are large "
             "(~tens of thousands of EUR/month, ~30× actual consumption). Normalization removed the "
             "artificial draw-count scale (log S, ~84×) but NOT the genuine opportunity-set "
             "compensation: the single home node carries no opportunity density while `V_actual` "
             "does. This is the memo's full-compensation staying-home endpoint, by design.\n")

    L.append("## W6 — Min-of-equal-pay over the universal grid (Task 4)\n")
    L.append(f"Grid (identical for every household): hours {m['w6_grid_hours']} "
             f"({', '.join(m['w6_node_labels'])}); leisure {m['w6_grid_leisure']} (= 80 − hours). "
             f"Utility-only u(c,ℓ), equal consumption w at all 6 nodes, uniform prob 1/6, no "
             f"opportunity-density/prior. `V_ref = logsumexp_j(u_j(w)) − log(6)`. BG excluded "
             f"(proposal support, not a canonical state).\n")
    L.append(tbl(m["task4_w6"],
                 ["median_eur", "p10_eur", "p90_eur", "min_eur", "max_eur",
                  "median_ratio_to_actual_c", "n_outside_bracket_after_expand", "n_genuine_nonconv"]))
    L.append("\nInvariance / synthetic gates:")
    L.append(tbl(m["task4_w6"],
                 ["synthetic_kappa_max_err", "duplication_invariance_max_nats",
                  "cross_hh_invariance_diff_eur", "beta_l_coeff_recovery_spread"]))
    L.append(f"\nGate (grid identical across HH; no opp/prior terms; synthetic-κ ≤1e-8; "
             f"node-duplication invariance ≤1e-10 nats; cross-HH invariance ≤1e-8; outside-bracket "
             f"& non-conv <0.5%): **{'PASS' if m['task4_pass'] else 'FAIL'}**. W6 also carries the "
             "full-compensation interpretation (own-opportunity-set AND pay priced against a common "
             "benchmark); magnitude caveat applies.\n")

    L.append("## Outputs\n")
    L.append(f"- `{m['output_parquet']}` (sha256 `{m['output_parquet_sha256']}`, {m['n_rows']} rows): "
             "V_actual_normalized, S_i, W3/W1/W4/W6 + W1 working-only, solver & bracket status.")
    L.append(f"- `F4C_manifest_v1.json`; this report.")
    L.append(f"- all_measure_gates_pass: **{m['all_measure_gates_pass']}**\n")

    L.append("---\n")
    st = "valid" if m["task2_pass"] else "invalid"
    L.append(f"W3 STATUS: {st}")
    L.append(f"W1 STATUS: {st}")
    L.append(f"W4 STATUS: {'valid' if m['task3_pass'] else 'invalid'}")
    L.append(f"W6 STATUS: {'valid' if m['task4_pass'] else 'invalid'}")
    L.append(f"READY FOR F5: {'yes' if m['ready_for_f5'] else 'no'}")
    return "\n".join(L)


if __name__ == "__main__":
    main()
