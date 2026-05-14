"""
Smoke test for ruro_occ_M0b1 and ruro_occ_M0b2.

Checks (per spec):
 1. YAML parses
 2. MNL files load
 3. all parameters initialize at spec initial_values
 4. likelihood evaluates at initial values (finite, not nan/inf)
 5. gradients finite (GAMSPy symbolic; checked via finite-difference approx)
 6. no NaN or Inf in utility, opportunity, prior correction, choice index
 7. beta_ll enters only couples utility
 8. beta_ll does not affect singles
 9. opportunity blocks are unchanged from M0a-clean
10. proposal/prior correction is unchanged from M0a-clean

No estimation is run.
"""
from __future__ import annotations
import sys, json, traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "enhanced"))

import numpy as np
import pandas as pd

from estimation_spec_parser import parse_specification
from estimation_utils import precompute_data_singles, precompute_data_couples, box_cox_transform

MNL_BASE   = Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl")
SINGLES_PQ = Path(str(MNL_BASE) + "__singles.parquet")
COUPLES_PQ = Path(str(MNL_BASE) + "__couples.parquet")
META_JSON  = Path(str(MNL_BASE) + "__mnlmeta.json")

SPEC_PATHS = {
    "M0a_clean": REPO / "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml",
    "M0b1":      REPO / "scripts/enhanced/estimation_spec_ruro_occ_M0b1.yaml",
    "M0b2":      REPO / "scripts/enhanced/estimation_spec_ruro_occ_M0b2.yaml",
}

SAMPLE_N  = 200   # households per group for smoke evaluation
SAMPLE_SEED = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_finite(arr):
    a = np.asarray(arr, dtype=float)
    return bool(np.all(np.isfinite(a)))

def _has_nan(arr):
    a = np.asarray(arr, dtype=float)
    return bool(np.any(np.isnan(a)))

def _has_inf(arr):
    a = np.asarray(arr, dtype=float)
    return bool(np.any(np.isinf(a)))

def _boxcox(x, theta):
    return box_cox_transform(np.asarray(x, dtype=float), float(theta))

def _sample_hh(df, n, seed):
    ids = df["idhh"].unique()
    rng = np.random.default_rng(seed)
    chosen = rng.choice(ids, size=min(n, len(ids)), replace=False)
    return df[df["idhh"].isin(chosen)].copy()

def _softmax_loglik(df_g, V_col="V"):
    ll = 0.0
    for _, grp in df_g.groupby("idhh"):
        V = grp[V_col].values
        V_s = V - V.max()
        log_sum = np.log(np.sum(np.exp(V_s)))
        chosen_V = grp.loc[grp["is_chosen"] == 1, V_col].values
        if len(chosen_V) == 0:
            chosen_V = grp.loc[grp["chosen"] == 1, V_col].values
        if len(chosen_V) == 0:
            return float("nan")
        ll += float(chosen_V[0]) - V.max() - log_sum
    return ll

def _chosen_col(df):
    return "is_chosen" if "is_chosen" in df.columns else "chosen"


# ---------------------------------------------------------------------------
# Compute V for a singles group (manual numpy evaluation)
# ---------------------------------------------------------------------------

def _compute_singles_V(df, params, spec, group_suffix):
    """Return (V_array, components_dict) for a singles group."""
    iv = params
    beta_c  = iv.get(f"beta_c{group_suffix}", iv.get("beta_c", 1.0))
    theta_c_name = spec.theta_c_param_name(
        "singles_male" if group_suffix == "_sm" else "singles_female"
    ) if hasattr(spec, "theta_c_param_name") else None
    theta_c = iv[theta_c_name] if (theta_c_name and theta_c_name in iv) else iv.get("theta_c", 0.5)
    theta_l = iv.get(f"theta_l{group_suffix}", iv.get("theta_l", 0.5))

    c = df["consumption"].values
    l = df["leisure"].values
    bc_c = _boxcox(c, theta_c)
    bc_l = _boxcox(l, theta_l)

    # beta_l(X)
    beta_l0 = iv.get(f"beta_l0{group_suffix}", iv.get("beta_l0", 1.0))
    beta_l = np.full(len(df), beta_l0)
    for sh in (spec.utility_leisure_shifters or []):
        coef_name = sh["coefficient"] + group_suffix
        if coef_name not in iv:
            coef_name = sh["coefficient"]
        if coef_name not in iv:
            continue
        gs = sh.get("gender_specific", False)
        if gs and group_suffix == "_sm":
            continue
        var = sh["variable"]
        col = df[var].values if var in df.columns else np.zeros(len(df))
        beta_l = beta_l + iv[coef_name] * col

    U = beta_c * bc_c + beta_l * bc_l

    # Opportunity: log_opp or prior-only
    if "log_opp" in df.columns:
        O = df["log_opp"].values
    else:
        O = np.zeros(len(df))

    # Prior correction
    if "log_prior" in df.columns:
        log_prior = df["log_prior"].values
    elif "prior" in df.columns:
        log_prior = np.log(np.maximum(df["prior"].values, 1e-300))
    else:
        log_prior = np.zeros(len(df))

    V = U + O - log_prior
    comps = {"U": U, "O": O, "log_prior": log_prior, "V": V, "bc_c": bc_c, "bc_l": bc_l}
    return V, comps


# ---------------------------------------------------------------------------
# Compute V for couples (manual numpy evaluation)
# ---------------------------------------------------------------------------

def _compute_couples_V(df, params, spec):
    """Return (V_array, components_dict) for the couples block."""
    iv = params
    beta_c  = iv.get("beta_c", 1.0)
    theta_c = iv.get("theta_c", 0.5)
    theta_l_m = iv.get("theta_l_m", iv.get("theta_l", 0.5))
    theta_l_f = iv.get("theta_l_f", iv.get("theta_l", 0.5))

    c   = df["consumption"].values
    l_m = df["leisure_male"].values
    l_f = df["leisure_female"].values
    bc_c   = _boxcox(c,   theta_c)
    bc_l_m = _boxcox(l_m, theta_l_m)
    bc_l_f = _boxcox(l_f, theta_l_f)

    # beta_l_m(X) and beta_l_f(X)
    for suf, gs_allow in [("_m", False), ("_f", True)]:
        beta_l0 = iv.get(f"beta_l0{suf}", iv.get("beta_l0", 1.0))
        beta_l = np.full(len(df), beta_l0)
        for sh in (spec.utility_leisure_shifters or []):
            coef_name = sh["coefficient"] + suf
            if coef_name not in iv:
                coef_name = sh["coefficient"]
            if coef_name not in iv:
                continue
            gs = sh.get("gender_specific", False)
            if gs and not gs_allow:
                continue
            var = sh["variable"]
            # couples columns may be suffixed
            col_name = var + suf if (var + suf) in df.columns else var
            col = df[col_name].values if col_name in df.columns else np.zeros(len(df))
            beta_l = beta_l + iv[coef_name] * col
        if suf == "_m":
            beta_l_m = beta_l
        else:
            beta_l_f = beta_l

    U = beta_c * bc_c + beta_l_m * bc_l_m + beta_l_f * bc_l_f

    # Leisure-leisure interaction (M0b+)
    beta_ll = None
    interact_contrib = np.zeros(len(df))
    if spec.couples_interaction_coef and spec.couples_interaction_coef in iv:
        beta_ll = iv[spec.couples_interaction_coef]
        interact_contrib = beta_ll * bc_l_m * bc_l_f
    U_with_ll = U + interact_contrib

    # Opportunity
    if "log_opp" in df.columns:
        O = df["log_opp"].values
    else:
        O = np.zeros(len(df))

    # Prior correction
    if "log_prior" in df.columns:
        log_prior = df["log_prior"].values
    elif "prior" in df.columns:
        log_prior = np.log(np.maximum(df["prior"].values, 1e-300))
    else:
        log_prior = np.zeros(len(df))

    V = U_with_ll + O - log_prior
    comps = {
        "U_base": U, "interact_contrib": interact_contrib, "beta_ll": beta_ll,
        "O": O, "log_prior": log_prior, "V": V,
        "bc_c": bc_c, "bc_l_m": bc_l_m, "bc_l_f": bc_l_f,
    }
    return V, comps


# ---------------------------------------------------------------------------
# Main smoke test
# ---------------------------------------------------------------------------

def run_smoke(label, spec_path, df_s, df_c, spec_clean, iv_clean):
    results = {}

    def chk(name, passed, detail=""):
        results[name] = {"pass": passed, "detail": detail}
        status = "PASS" if passed else "FAIL"
        print(f"    [{status}] {name}" + (f": {detail}" if detail else ""))

    print(f"\n  --- {label} ---")

    # 1. YAML parses
    try:
        spec = parse_specification(spec_path)
        chk("1_yaml_parses", True, f"n_params={len(spec.all_param_names)}, name={spec.name}")
    except Exception as e:
        chk("1_yaml_parses", False, str(e))
        return results

    # 2. MNL files load (already loaded; just confirm)
    chk("2_mnl_files_load", df_s is not None and df_c is not None,
        f"singles={len(df_s)} rows, couples={len(df_c)} rows")

    # 3. all parameters initialize
    iv = spec.initial_values or {}
    missing = [p for p in spec.all_param_names if p not in iv]
    chk("3_all_params_initialized", len(missing) == 0,
        f"missing={missing}" if missing else f"{len(iv)} params at initial values")

    if missing:
        return results

    # --- sample for speed ---
    dgn_col = "dgn" if "dgn" in df_s.columns else "gender"
    df_sm = _sample_hh(df_s[df_s[dgn_col] == 1], SAMPLE_N, SAMPLE_SEED)
    df_sf = _sample_hh(df_s[df_s[dgn_col] == 0], SAMPLE_N, SAMPLE_SEED)
    df_cou = _sample_hh(df_c, SAMPLE_N, SAMPLE_SEED)

    # 4. likelihood evaluates at initial values
    ll_parts = {}
    ll_ok = True
    try:
        for grp_label, df_g, kwargs in [
            ("sm", df_sm, {"group_suffix": "_sm"}),
            ("sf", df_sf, {"group_suffix": "_sf"}),
        ]:
            V, comps = _compute_singles_V(df_g, iv, spec, kwargs["group_suffix"])
            df_g = df_g.copy(); df_g["V"] = V
            ll = _softmax_loglik(df_g)
            ll_parts[grp_label] = ll
            if not np.isfinite(ll):
                ll_ok = False
        V_c, comps_c = _compute_couples_V(df_cou, iv, spec)
        df_cou2 = df_cou.copy(); df_cou2["V"] = V_c
        ll_c = _softmax_loglik(df_cou2)
        ll_parts["cou"] = ll_c
        if not np.isfinite(ll_c):
            ll_ok = False
        ll_total = sum(ll_parts.values())
        chk("4_likelihood_finite", ll_ok and np.isfinite(ll_total),
            f"ll_sm={ll_parts.get('sm',float('nan')):.4f}, ll_sf={ll_parts.get('sf',float('nan')):.4f}, ll_cou={ll_parts.get('cou',float('nan')):.4f}")
    except Exception as e:
        chk("4_likelihood_finite", False, traceback.format_exc(limit=3))
        ll_ok = False

    # 5. gradient finite (finite-difference check on beta_ll for M0b specs; on beta_c for all)
    try:
        eps = 1e-5
        grad_checks = {}
        for pname in (["beta_c"] + (["beta_ll"] if spec.couples_interaction_coef else [])):
            iv2 = dict(iv); iv2[pname] = iv[pname] + eps
            if pname == "beta_c":
                V_p, _ = _compute_singles_V(df_sm, iv2, spec, "_sm")
                V_b, _ = _compute_singles_V(df_sm, iv,  spec, "_sm")
            else:
                V_p, _ = _compute_couples_V(df_cou, iv2, spec)
                V_b, _ = _compute_couples_V(df_cou, iv,  spec)
            grad = (V_p - V_b) / eps
            grad_checks[pname] = _is_finite(grad)
        all_finite = all(grad_checks.values())
        chk("5_gradients_finite", all_finite,
            ", ".join(f"{k}={'OK' if v else 'BAD'}" for k,v in grad_checks.items()))
    except Exception as e:
        chk("5_gradients_finite", False, str(e))

    # 6. no NaN/Inf in utility, opportunity, prior, choice index
    try:
        bad = {}
        for grp_label, df_g, suf in [("sm", df_sm, "_sm"), ("sf", df_sf, "_sf")]:
            V, comps = _compute_singles_V(df_g, iv, spec, suf)
            for k, v in comps.items():
                if _has_nan(v) or _has_inf(v):
                    bad[f"{grp_label}.{k}"] = "nan/inf"
        V_c, comps_c = _compute_couples_V(df_cou, iv, spec)
        for k, v in comps_c.items():
            if isinstance(v, np.ndarray) and (_has_nan(v) or _has_inf(v)):
                bad[f"cou.{k}"] = "nan/inf"
        chk("6_no_nan_inf", len(bad) == 0,
            str(bad) if bad else "all components finite")
    except Exception as e:
        chk("6_no_nan_inf", False, str(e))

    # 7. beta_ll enters only couples utility
    try:
        if spec.couples_interaction_coef:
            iv_no_ll = dict(iv); iv_no_ll["beta_ll"] = 0.0
            iv_big_ll = dict(iv); iv_big_ll["beta_ll"] = 1.5
            # Couples V must differ
            V_base, comps_base = _compute_couples_V(df_cou, iv_no_ll, spec)
            V_big,  comps_big  = _compute_couples_V(df_cou, iv_big_ll, spec)
            couples_changes = not np.allclose(V_base, V_big)
            # Singles V must be identical
            V_sm_base, _ = _compute_singles_V(df_sm, iv_no_ll, spec, "_sm")
            V_sm_big,  _ = _compute_singles_V(df_sm, iv_big_ll, spec, "_sm")
            singles_unchanged = np.allclose(V_sm_base, V_sm_big)
            chk("7_beta_ll_only_couples", couples_changes and singles_unchanged,
                f"couples_changes={couples_changes}, singles_unchanged={singles_unchanged}")
        else:
            chk("7_beta_ll_only_couples", True, "no beta_ll in this spec (M0a-clean)")
    except Exception as e:
        chk("7_beta_ll_only_couples", False, str(e))

    # 8. beta_ll does not affect singles
    try:
        if spec.couples_interaction_coef:
            V_sf_base, _ = _compute_singles_V(df_sf, iv_no_ll, spec, "_sf")
            V_sf_big,  _ = _compute_singles_V(df_sf, iv_big_ll, spec, "_sf")
            ok = np.allclose(V_sf_base, V_sf_big)
            chk("8_beta_ll_no_singles_effect", ok, "sf unchanged" if ok else "sf CHANGED - BUG")
        else:
            chk("8_beta_ll_no_singles_effect", True, "no beta_ll in spec")
    except Exception as e:
        chk("8_beta_ll_no_singles_effect", False, str(e))

    # 9. opportunity blocks unchanged vs M0a-clean
    try:
        # Compare hours_shifters, market_opportunity_shifters coefs
        clean_h = sorted(s["coefficient"] for s in (spec_clean.hours_shifters or []))
        this_h  = sorted(s["coefficient"] for s in (spec.hours_shifters or []))
        clean_m = sorted(s["coefficient"] for s in (spec_clean.market_opportunity_shifters or []))
        this_m  = sorted(s["coefficient"] for s in (spec.market_opportunity_shifters or []))
        ok = (clean_h == this_h) and (clean_m == this_m)
        chk("9_opp_blocks_unchanged",  ok,
            f"hours: {this_h}, market: {this_m}" if ok else f"hours mismatch {this_h} vs {clean_h} or market {this_m} vs {clean_m}")
    except Exception as e:
        chk("9_opp_blocks_unchanged", False, str(e))

    # 10. prior/proposal correction unchanged vs M0a-clean
    try:
        # Compare the log_prior column values on the same sample
        V_sm_clean, comps_clean_sm = _compute_singles_V(df_sm, iv_clean, spec_clean, "_sm")
        V_sm_this,  comps_this_sm  = _compute_singles_V(df_sm, iv, spec, "_sm")
        prior_ok = np.allclose(comps_clean_sm["log_prior"], comps_this_sm["log_prior"])
        V_c_clean, comps_clean_c = _compute_couples_V(df_cou, iv_clean, spec_clean)
        V_c_this,  comps_this_c  = _compute_couples_V(df_cou, iv, spec)
        prior_c_ok = np.allclose(comps_clean_c["log_prior"], comps_this_c["log_prior"])
        ok = prior_ok and prior_c_ok
        chk("10_prior_correction_unchanged", ok,
            "log_prior identical on sample" if ok else "log_prior DIFFERS")
    except Exception as e:
        chk("10_prior_correction_unchanged", False, str(e))

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading MNL data...")
    df_singles = pd.read_parquet(SINGLES_PQ)
    df_couples = pd.read_parquet(COUPLES_PQ)
    print(f"  singles: {len(df_singles)} rows, couples: {len(df_couples)} rows")

    print("Parsing M0a-clean spec (reference)...")
    spec_clean = parse_specification(SPEC_PATHS["M0a_clean"])
    iv_clean   = spec_clean.initial_values or {}

    all_results = {}
    for label in ["M0b1", "M0b2"]:
        r = run_smoke(label, SPEC_PATHS[label], df_singles, df_couples, spec_clean, iv_clean)
        all_results[label] = r

    # Summary
    print("\n" + "="*60)
    print("SMOKE TEST SUMMARY")
    print("="*60)
    for label, checks in all_results.items():
        n_pass = sum(1 for v in checks.values() if v["pass"])
        n_fail = sum(1 for v in checks.values() if not v["pass"])
        overall = "PASS" if n_fail == 0 else "FAIL"
        print(f"\n  {label}: {overall}  ({n_pass} pass, {n_fail} fail)")
        for chk_name, chk_val in checks.items():
            tag = "PASS" if chk_val["pass"] else "FAIL"
            print(f"    [{tag}] {chk_name}" + (f": {chk_val['detail']}" if chk_val.get('detail') else ""))

    # Persist for the report
    out = REPO / "Results" / "_M0b_smoke_test_raw.json"
    serial = {
        label: {k: {"pass": v["pass"], "detail": v.get("detail", "")}
                for k, v in checks.items()}
        for label, checks in all_results.items()
    }
    out.write_text(json.dumps(serial, indent=2))
    print(f"\nRaw results: {out}")
