"""
FAST-LANE F5: SINGLES MEASURE-FAMILY INEQUALITY POINT ESTIMATES.

Survey-weighted inequality POINT ESTIMATES for the headline singles welfare measures
(W1, W4, W6) from the frozen F4C outputs. NO decomposition, estimation, bootstrap,
EUROMOD, V_dir, promotion, engine/spec/data edits, or commit. F3/F4 artifacts immutable;
new versioned outputs only.

SCOPE: point estimates only. Conference-reportable claims require cluster-bootstrap
re-estimation CIs (NOT run here; idorighh is the cluster key, 200 replicates per scaffold).

Headline = W1/W4/W6. W3 = validation readout only. W1 working-only = appendix sensitivity.
Primary index = survey-weighted Gini (weight = staged `dwt`). Secondary = weighted CV2,
Theil L, Atkinson eps=1, Atkinson eps=2.
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
for _p in ["scripts/bpool", "scripts/enhanced", "scripts/welfare", "scripts/pilot"]:
    sys.path.insert(0, str(_REPO / _p))
from _bpool_paths import bpool_dir

STAGED_STEM = "fr_p3a_bpool_engine_ready_staged_threeB1"
N_EXPECTED = 5007
BOOTSTRAP_REPLICATES_REQUIRED = 200

_F4C_PARQUET = _REPO / "outputs/welfare/fastlane/singles_measures_F4C_v1.parquet"
_F4C_MANIFEST = _REPO / "outputs/welfare/fastlane/F4C_manifest_v1.json"
_F4C_REPORT = _REPO / "docs/jmp_methodology/RURO_welfare_F4C_final_singles_measures_report_v1.md"

_OUT_SUMMARY = _REPO / "outputs/welfare/fastlane/singles_measure_family_F5_v1.parquet"
_OUT_HH = _REPO / "outputs/welfare/fastlane/singles_measure_family_F5_households_v1.parquet"
_OUT_MANIFEST = _REPO / "outputs/welfare/fastlane/F5_manifest_v1.json"
_OUT_DOC = _REPO / "docs/jmp_methodology/RURO_welfare_singles_measure_family_F5_report_v1.md"

_IMMUTABLE = {_F4C_PARQUET, _F4C_MANIFEST, _F4C_REPORT}

HEADLINE = {"W1": "W1_omega_eur", "W4": "W4_omega_eur", "W6": "W6_omega_eur"}
CONV_FLAG = {"W1": "W1_converged", "W4": "W4_bracket_converged", "W6": "W6_bracket_converged"}


# ---------------------------------------------------------------------------
# atomic writers
# ---------------------------------------------------------------------------
def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard(dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: refuse to overwrite immutable artifact: {dest}")
    if dest.exists():
        raise FileExistsError(f"STOP: completed artifact exists, will not overwrite: {dest}")


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


def _atomic_json(obj, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=_jsonify)); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_parquet(df, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_text(text, dest: Path):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8"); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


# ---------------------------------------------------------------------------
# weighted inequality primitives (local; welfare_core.gini untouched)
# ---------------------------------------------------------------------------
def w_mean(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    return float(np.sum(w * x) / np.sum(w))


def w_quantile(x, w, q):
    x = np.asarray(x, float); w = np.asarray(w, float)
    o = np.argsort(x, kind="mergesort")
    x, w = x[o], w[o]
    cw = np.cumsum(w)
    p = (cw - 0.5 * w) / np.sum(w)
    return float(np.interp(q, p, x))


def w_gini(x, w):
    """Survey-weighted Gini via the standard weighted order-statistic (Lerman-Yitzhaki)
    formula: G = 2/(W·mu) · Σ w_i (x_i − mu)(r_i − 1/2), r_i the midpoint fractional rank."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    o = np.argsort(x, kind="mergesort")
    x, w = x[o], w[o]
    W = np.sum(w)
    mu = np.sum(w * x) / W
    cw = np.cumsum(w)
    r = (cw - 0.5 * w) / W
    return float(2.0 / (W * mu) * np.sum(w * (x - mu) * (r - 0.5)))


def w_gini_mad_oracle(x, w):
    """O(n^2) weighted mean-absolute-difference Gini oracle (validation only)."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    W = np.sum(w); mu = np.sum(w * x) / W
    num = np.sum(w[:, None] * w[None, :] * np.abs(x[:, None] - x[None, :]))
    return float(num / (2.0 * W * W * mu))


def w_cv2(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    mu = w_mean(x, w)
    var = np.sum(w * (x - mu) ** 2) / np.sum(w)
    return float(var / mu ** 2)


def _require_positive(x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)) or np.any(x <= 0):
        raise ValueError("index requires strictly positive, finite support")
    return x


def w_theil_l(x, w):
    """Mean log deviation: L = ln(mu) − Σ (w_i/W) ln(x_i)."""
    x = _require_positive(x); w = np.asarray(w, float)
    W = np.sum(w); mu = np.sum(w * x) / W
    return float(np.log(mu) - np.sum(w * np.log(x)) / W)


def w_atkinson(x, w, eps):
    x = _require_positive(x); w = np.asarray(w, float)
    W = np.sum(w); mu = np.sum(w * x) / W
    if abs(eps - 1.0) < 1e-12:
        ede = np.exp(np.sum(w * np.log(x)) / W)            # weighted geometric mean
    else:
        m = np.sum(w * x ** (1.0 - eps)) / W
        ede = m ** (1.0 / (1.0 - eps))
    return float(1.0 - ede / mu)


def top_weight_share(x, w, frac=0.01):
    """Share of total weighted welfare held by the top `frac` of weight mass."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    o = np.argsort(x, kind="mergesort")[::-1]              # descending value
    x, w = x[o], w[o]
    cw = np.cumsum(w); W = np.sum(w)
    target = frac * W
    total = np.sum(w * x)
    idx = int(np.searchsorted(cw, target))
    s = np.sum(w[:idx] * x[:idx])
    if idx < len(x):
        prev = cw[idx - 1] if idx > 0 else 0.0
        s += (target - prev) * x[idx]
    return float(s / total)


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    ra -= ra.mean(); rb -= rb.mean()
    return float(np.sum(ra * rb) / np.sqrt(np.sum(ra ** 2) * np.sum(rb ** 2)))


# ---------------------------------------------------------------------------
# TASK 1 — validation of primitives
# ---------------------------------------------------------------------------
def validate_primitives() -> dict:
    rng = np.random.default_rng(20260613)
    res = {}
    # (a) weighted Gini vs O(n^2) MAD oracle on small distinct arrays
    md = 0.0
    for _ in range(200):
        n = int(rng.integers(3, 12))
        x = np.sort(rng.uniform(1, 100, n) + np.arange(n) * 1e-3)  # distinct
        w = rng.uniform(0.1, 5, n)
        md = max(md, abs(w_gini(x, w) - w_gini_mad_oracle(x, w)))
    res["gini_vs_mad_oracle_max"] = md
    # (b) integer-weight replication == unweighted Gini of replicated array
    rep = 0.0
    for _ in range(50):
        n = int(rng.integers(3, 8))
        x = rng.uniform(1, 50, n) + np.arange(n) * 1e-3
        iw = rng.integers(1, 5, n)
        g_w = w_gini(x, iw.astype(float))
        xr = np.repeat(x, iw)
        g_u = w_gini(xr, np.ones_like(xr))
        rep = max(rep, abs(g_w - g_u))
    res["integer_weight_replication_max"] = rep
    # (c) weight-scale invariance (all indices)
    x = rng.uniform(1, 100, 40); w = rng.uniform(0.1, 5, 40)
    c = 7.3
    wsi = max(
        abs(w_gini(x, w) - w_gini(x, w * c)),
        abs(w_cv2(x, w) - w_cv2(x, w * c)),
        abs(w_theil_l(x, w) - w_theil_l(x, w * c)),
        abs(w_atkinson(x, w, 1) - w_atkinson(x, w * c, 1)),
        abs(w_atkinson(x, w, 2) - w_atkinson(x, w * c, 2)),
    )
    res["weight_scale_invariance_max"] = wsi
    # (d) value-scale invariance (Gini/CV2/Theil/Atkinson are relative)
    k = 13.7
    vsi = max(
        abs(w_gini(x, w) - w_gini(x * k, w)),
        abs(w_cv2(x, w) - w_cv2(x * k, w)),
        abs(w_theil_l(x, w) - w_theil_l(x * k, w)),
        abs(w_atkinson(x, w, 1) - w_atkinson(x * k, w, 1)),
        abs(w_atkinson(x, w, 2) - w_atkinson(x * k, w, 2)),
    )
    res["value_scale_invariance_max"] = vsi
    # (e) equal values -> 0 everywhere
    xe = np.full(20, 4.2); we = rng.uniform(0.5, 2, 20)
    eq = max(abs(w_gini(xe, we)), abs(w_cv2(xe, we)), abs(w_theil_l(xe, we)),
             abs(w_atkinson(xe, we, 1)), abs(w_atkinson(xe, we, 2)))
    res["equal_values_zero_max"] = eq
    # (f) non-positive support fails clearly for positive-only indices
    failed_clearly = True
    for fn in (w_theil_l, lambda a, b: w_atkinson(a, b, 1), lambda a, b: w_atkinson(a, b, 2)):
        try:
            fn(np.array([1.0, -2.0, 3.0]), np.ones(3)); failed_clearly = False
        except ValueError:
            pass
    res["nonpositive_fails_clearly"] = failed_clearly
    res["all_pass"] = bool(
        md <= 1e-12 and rep <= 1e-12 and wsi <= 1e-12 and vsi <= 1e-12
        and eq <= 1e-12 and failed_clearly)
    return res


def _scope_mask(df, scope):
    if scope == "singles_all":
        return np.ones(len(df), dtype=bool)
    return (df["group"] == scope).to_numpy()


def _indices_for(df, value_col, conv_col, w):
    """Return (valid_mask, dict-of-indices) for a measure on a scope subset."""
    x = df[value_col].to_numpy(dtype=float)
    conv = df[conv_col].to_numpy(dtype=bool)
    valid = conv & np.isfinite(x) & (x > 0)
    xv, wv = x[valid], w[valid]
    out = {
        "n": int(valid.sum()), "n_total": int(len(df)),
        "sum_weight": float(np.sum(wv)),
        "w_mean": w_mean(xv, wv), "w_p10": w_quantile(xv, wv, 0.10),
        "w_median": w_quantile(xv, wv, 0.50), "w_p90": w_quantile(xv, wv, 0.90),
        "w_p99": w_quantile(xv, wv, 0.99), "w_max": float(np.max(xv)),
        "w_gini": w_gini(xv, wv), "unw_gini": w_gini(xv, np.ones_like(wv)),
        "w_cv2": w_cv2(xv, wv), "w_theil_l": w_theil_l(xv, wv),
        "w_atkinson_e1": w_atkinson(xv, wv, 1), "w_atkinson_e2": w_atkinson(xv, wv, 2),
        "top1pct_weight_share": top_weight_share(xv, wv, 0.01),
    }
    out["abs_w_minus_unw_gini"] = abs(out["w_gini"] - out["unw_gini"])
    # winsorized-at-p99 Gini (sensitivity only)
    cap = out["w_p99"]
    out["w_gini_winsor_p99"] = w_gini(np.minimum(xv, cap), wv)
    out["all_finite_positive_converged"] = bool(valid.sum() > 0 and np.all(np.isfinite(xv)) and np.all(xv > 0))
    out["gini_in_unit_interval"] = bool(0.0 <= out["w_gini"] <= 1.0 and np.isfinite(out["w_gini"]))
    return valid, out


def main():
    t0 = time.time()
    for d in (_OUT_SUMMARY, _OUT_HH, _OUT_MANIFEST, _OUT_DOC):
        _guard(d)
    print("F5 start")

    # ---------------- TASK 0 — provenance + join ----------------
    print("\n=== TASK 0: provenance + weight join ===")
    f4cman = json.loads(_F4C_MANIFEST.read_text())
    f4c_sha = _sha256(_F4C_PARQUET)
    prov = {
        "f4c_parquet_sha256": f4c_sha,
        "f4c_manifest_recorded_sha256": f4cman.get("output_parquet_sha256"),
        "f4c_parquet_hash_match": f4c_sha == f4cman.get("output_parquet_sha256"),
        "f4c_manifest_sha256": _sha256(_F4C_MANIFEST),
        "f4c_report_sha256": _sha256(_F4C_REPORT),
        "spec_hash": f4cman.get("spec_hash"), "theta_hash": f4cman.get("theta_hash"),
        "all_gates_pass_f4c": f4cman.get("all_measure_gates_pass"),
    }
    f4c = pd.read_parquet(_F4C_PARQUET)
    bp = bpool_dir()
    staged = pd.read_parquet(
        bp / f"{STAGED_STEM}__singles.parquet",
        columns=["idhh", "stacked_hh_uid", "is_chosen", "dwt", "idorighh", "year_tag", "dgn"])
    # constancy within uid (over all 101 alts)
    g = staged.groupby("stacked_hh_uid")
    const_ok = bool((g["dwt"].nunique() == 1).all() and (g["idorighh"].nunique() == 1).all()
                    and (g["year_tag"].nunique() == 1).all() and (g["dgn"].nunique() == 1).all())
    dwt_ok = bool(staged["dwt"].notna().all() and (staged["dwt"] > 0).all())

    chosen = staged[staged["is_chosen"] == 1].copy()
    if chosen["idhh"].duplicated().any():
        raise SystemExit("STOP: duplicate idhh among chosen rows.")
    chosen = chosen.rename(columns={"idhh": "uid"})[
        ["uid", "dwt", "idorighh", "year_tag", "dgn"]]
    merged = f4c.merge(chosen, on="uid", how="inner", validate="one_to_one")

    # group vs dgn agreement: dgn==1 male
    grp_from_dgn = np.where(merged["dgn"] == 1, "singles_male", "singles_female")
    group_agrees = bool(np.all(grp_from_dgn == merged["group"].to_numpy()))

    join_gate = {
        "n_joined": int(len(merged)),
        "n_joined_eq_5007": int(len(merged)) == N_EXPECTED,
        "no_missing_extra_dup": (int(len(merged)) == N_EXPECTED
                                 and int(f4c["uid"].nunique()) == N_EXPECTED
                                 and not merged["uid"].duplicated().any()),
        "dwt_finite_positive": dwt_ok,
        "within_uid_constant": const_ok,
        "group_agrees_dgn": group_agrees,
    }
    # descriptive counts
    desc = {
        "overall": {"n_hh": int(len(merged)), "sum_dwt": float(merged["dwt"].sum()),
                    "n_idorighh": int(merged["idorighh"].nunique())},
        "by_group": {}, "by_year": {},
    }
    for grp, sub in merged.groupby("group"):
        desc["by_group"][grp] = {"n_hh": int(len(sub)), "sum_dwt": float(sub["dwt"].sum()),
                                 "n_idorighh": int(sub["idorighh"].nunique())}
    for yr, sub in merged.groupby("year_tag"):
        desc["by_year"][int(yr)] = {"n_hh": int(len(sub)), "sum_dwt": float(sub["dwt"].sum()),
                                    "n_idorighh": int(sub["idorighh"].nunique())}
    prov["join_gate"] = join_gate
    prov["descriptives"] = desc
    print(f"  joined={join_gate['n_joined']} (==5007:{join_gate['n_joined_eq_5007']}) "
          f"dwt_ok={dwt_ok} const_ok={const_ok} group_agrees={group_agrees} "
          f"f4c_hash_match={prov['f4c_parquet_hash_match']}")
    print(f"  sum_dwt={desc['overall']['sum_dwt']:.1f} n_idorighh={desc['overall']['n_idorighh']}")
    task0_pass = bool(join_gate["n_joined_eq_5007"] and join_gate["no_missing_extra_dup"]
                      and dwt_ok and const_ok and group_agrees and prov["f4c_parquet_hash_match"])
    if not task0_pass:
        raise SystemExit(f"STOP: Task 0 gates failed: {join_gate}")

    w_all = merged["dwt"].to_numpy(dtype=float)

    # ---------------- TASK 1 — primitives validation ----------------
    print("\n=== TASK 1: primitive validation ===")
    prim = validate_primitives()
    for k, v in prim.items():
        print(f"  {k}: {v}")
    if not prim["all_pass"]:
        raise SystemExit("STOP: weighted-index primitives failed validation.")

    # ---------------- TASK 2-5 — per scope x measure ----------------
    print("\n=== TASK 2-5: scope x measure indices ===")
    scopes = ["singles_all", "singles_male", "singles_female"]
    rows = []
    by_scope = {}
    for scope in scopes:
        m = _scope_mask(merged, scope)
        sub = merged[m]
        w = w_all[m]
        scope_rec = {}
        for meas, col in HEADLINE.items():
            valid, idx = _indices_for(sub, col, CONV_FLAG[meas], w)
            idx["scope"] = scope; idx["measure"] = meas
            scope_rec[meas] = idx
            rows.append(idx)
            print(f"  {scope:15s} {meas}: n={idx['n']} wGini={idx['w_gini']:.4f} "
                  f"unwGini={idx['unw_gini']:.4f} CV2={idx['w_cv2']:.3f} "
                  f"AtkE1={idx['w_atkinson_e1']:.4f} median={idx['w_median']:.1f}")
        # across-measure spread (Task 3)
        ginis = {me: scope_rec[me]["w_gini"] for me in HEADLINE}
        gmin_m = min(ginis, key=ginis.get); gmax_m = max(ginis, key=ginis.get)
        scope_rec["_spread"] = {
            "min_gini": ginis[gmin_m], "min_measure": gmin_m,
            "max_gini": ginis[gmax_m], "max_measure": gmax_m,
            "bracket": [ginis[gmin_m], ginis[gmax_m]],
            "abs_spread": ginis[gmax_m] - ginis[gmin_m],
        }
        # rank correlations among W1/W4/W6 (Task 5) over common valid set
        common = np.ones(len(sub), dtype=bool)
        for meas, col in HEADLINE.items():
            common &= sub[CONV_FLAG[meas]].to_numpy(bool) & np.isfinite(sub[col].to_numpy(float)) \
                      & (sub[col].to_numpy(float) > 0)
        rc = {}
        for a, b in (("W1", "W4"), ("W1", "W6"), ("W4", "W6")):
            rc[f"{a}_{b}"] = spearman(sub[HEADLINE[a]].to_numpy(float)[common],
                                      sub[HEADLINE[b]].to_numpy(float)[common])
        scope_rec["_rankcorr"] = rc
        by_scope[scope] = scope_rec
        print(f"  {scope:15s} spread: [{scope_rec['_spread']['min_gini']:.4f} "
              f"({gmin_m}), {scope_rec['_spread']['max_gini']:.4f} ({gmax_m})] "
              f"= {scope_rec['_spread']['abs_spread']:.4f}")

    # W1 working-only appendix Gini (per scope)
    w1wo = {}
    for scope in scopes:
        m = _scope_mask(merged, scope); sub = merged[m]; w = w_all[m]
        x = sub["W1_workingonly_omega_eur"].to_numpy(float)
        conv = sub["W1_workingonly_converged"].to_numpy(bool)
        v = conv & np.isfinite(x) & (x > 0)
        w1wo[scope] = {"n": int(v.sum()), "w_gini": w_gini(x[v], w[v]),
                       "w_median": w_quantile(x[v], w[v], 0.5)}

    # W3 validation readout
    w3_abs_max = float(np.max(np.abs(merged["W3_omega_shift_eur"].to_numpy(float))))
    w3_readout = {"max_abs_w3_omega": w3_abs_max, "w3_le_1e8": bool(w3_abs_max <= 1e-8),
                  "headlined": False}
    print(f"  W3 readout: max|omega|={w3_abs_max:.2e} <=1e-8:{w3_readout['w3_le_1e8']}")

    # ---------------- TASK 6 — inference readiness ----------------
    print("\n=== TASK 6: inference-readiness audit ===")
    clusters_by_group = {grp: int(sub["idorighh"].nunique())
                         for grp, sub in merged.groupby("group")}
    cl = merged.groupby("idorighh")["year_tag"].nunique()
    multi_year_clusters = int((cl > 1).sum())
    infer = {
        "bootstrap_cluster_key": "idorighh",
        "n_clusters_overall": int(merged["idorighh"].nunique()),
        "n_clusters_by_group": clusters_by_group,
        "n_clusters_multi_pooled_year": multi_year_clusters,
        "required_external_operation": ("cluster-bootstrap re-estimation: resample idorighh clusters, "
                                        "RE-ESTIMATE theta per replicate, then recompute F4C measures; "
                                        "fixed-theta household resampling alone is NOT the pre-registered "
                                        "inference and cannot produce final headline CIs"),
        "required_replicates": BOOTSTRAP_REPLICATES_REQUIRED,
        "bootstrap_run_here": False,
    }
    print(f"  clusters={infer['n_clusters_overall']} by_group={clusters_by_group} "
          f"multi_year={multi_year_clusters} replicates_required={BOOTSTRAP_REPLICATES_REQUIRED}")

    # ---------------- gates ----------------
    point_ok = bool(task0_pass and prim["all_pass"]
                    and all(r["all_finite_positive_converged"] and r["gini_in_unit_interval"]
                            for r in rows))
    spread_ok = bool(all(np.isfinite(by_scope[s]["_spread"]["abs_spread"])
                         and by_scope[s]["_spread"]["abs_spread"] >= 0 for s in scopes))
    ready_f6 = bool(point_ok and spread_ok)

    # ---------------- TASK 7 — outputs ----------------
    print("\n=== TASK 7: outputs ===")
    sum_rows = []
    for r in rows:
        sc = r["scope"]
        rr = dict(r)
        rr["across_measure_min_gini"] = by_scope[sc]["_spread"]["min_gini"]
        rr["across_measure_max_gini"] = by_scope[sc]["_spread"]["max_gini"]
        rr["across_measure_abs_spread"] = by_scope[sc]["_spread"]["abs_spread"]
        rr["spearman_W1_W4"] = by_scope[sc]["_rankcorr"]["W1_W4"]
        rr["spearman_W1_W6"] = by_scope[sc]["_rankcorr"]["W1_W6"]
        rr["spearman_W4_W6"] = by_scope[sc]["_rankcorr"]["W4_W6"]
        rr["spec_hash"] = prov["spec_hash"]; rr["theta_hash"] = prov["theta_hash"]
        rr["f4c_parquet_sha256"] = f4c_sha
        sum_rows.append(rr)
    summary_df = pd.DataFrame(sum_rows)
    _atomic_parquet(summary_df, _OUT_SUMMARY)
    print(f"  wrote {_OUT_SUMMARY} rows={len(summary_df)}")

    hh_out = merged.copy()
    _atomic_parquet(hh_out, _OUT_HH)
    print(f"  wrote {_OUT_HH} rows={len(hh_out)}")

    manifest = {
        "f5_artifact": "F5_manifest_v1",
        "spec_hash": prov["spec_hash"], "theta_hash": prov["theta_hash"],
        "consumption_time_unit": f4cman.get("consumption_time_unit"),
        "weight_variable": "dwt", "cluster_key": "idorighh",
        "primary_index": "survey_weighted_gini",
        "headline_measures": list(HEADLINE.keys()),
        "task0_provenance": prov, "task0_pass": task0_pass,
        "task1_primitive_validation": prim,
        "task2_5_by_scope": {s: {m: by_scope[s][m] for m in HEADLINE} for s in scopes},
        "task3_across_measure_spread": {s: by_scope[s]["_spread"] for s in scopes},
        "task4_w1_working_only_appendix": w1wo,
        "task4_w3_validation_readout": w3_readout,
        "task5_rank_correlations": {s: by_scope[s]["_rankcorr"] for s in scopes},
        "task6_inference_readiness": infer,
        "point_estimate_status": "valid" if point_ok else "invalid",
        "across_measure_spread_status": "valid" if spread_ok else "invalid",
        "ready_for_f6_design_memo": ready_f6,
        "conference_reportable_with_ci": False,
        "output_summary_parquet": str(_OUT_SUMMARY),
        "output_summary_sha256": _sha256(_OUT_SUMMARY),
        "output_households_parquet": str(_OUT_HH),
        "output_households_sha256": _sha256(_OUT_HH),
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    _atomic_json(manifest, _OUT_MANIFEST)
    print(f"  wrote {_OUT_MANIFEST}")
    _atomic_text(_report(manifest), _OUT_DOC)
    print(f"  wrote {_OUT_DOC}")

    print("\n--- FINAL STATUS ---")
    print(f"F5 POINT-ESTIMATE STATUS: {'valid' if point_ok else 'invalid'}")
    print(f"ACROSS-MEASURE SPREAD STATUS: {'valid' if spread_ok else 'invalid'}")
    print(f"READY FOR F6 DESIGN MEMO: {'yes' if ready_f6 else 'no'}")
    print("CONFERENCE-REPORTABLE WITH CI: NO — cluster-bootstrap re-estimation pending")
    print(f"\nF5 COMPLETE in {round(time.time()-t0,1)}s")


def _report(m: dict) -> str:
    sci = lambda x: ("n/a" if x is None else (f"{x:.4f}" if isinstance(x, float) else str(x)))
    big = lambda x: ("n/a" if x is None else (f"{x:,.0f}" if isinstance(x, float) else str(x)))
    bs = m["task2_5_by_scope"]; sp = m["task3_across_measure_spread"]
    scopes = ["singles_all", "singles_male", "singles_female"]
    L = []
    L.append("# RURO Welfare F5 — Singles Measure-Family Inequality Point Estimates\n")
    L.append(f"Date: 2026-06-13 · spec_hash `{m['spec_hash']}` · theta_hash `{m['theta_hash']}` · "
             f"weight `dwt` · cluster `idorighh` · unit {m['consumption_time_unit']}\n")
    L.append("**POINT ESTIMATES ONLY.** Conference-reportable claims require cluster-bootstrap "
             "re-estimation CIs (not run; see Inference status). Headline = survey-weighted Gini of "
             "W1/W4/W6. W3 = validation only; W1 working-only = appendix.\n")

    p = m["task0_provenance"]; d = p["descriptives"]
    L.append("## Provenance & weight join (Task 0)\n")
    L.append(f"- F4C parquet sha256 match: {p['f4c_parquet_hash_match']}; F4C gates pass: {p['all_gates_pass_f4c']}")
    jg = p["join_gate"]
    L.append(f"- Joined households: **{jg['n_joined']}** (==5007: {jg['n_joined_eq_5007']}); "
             f"no missing/extra/dup: {jg['no_missing_extra_dup']}; dwt finite>0: {jg['dwt_finite_positive']}; "
             f"within-uid constant: {jg['within_uid_constant']}; group==dgn: {jg['group_agrees_dgn']}")
    L.append(f"- Overall: n={d['overall']['n_hh']}, Σdwt={d['overall']['sum_dwt']:,.0f}, "
             f"unique idorighh={d['overall']['n_idorighh']}")
    L.append("- By group: " + "; ".join(
        f"{g} n={v['n_hh']} Σdwt={v['sum_dwt']:,.0f} clusters={v['n_idorighh']}"
        for g, v in d["by_group"].items()))
    L.append("- By year_tag: " + "; ".join(
        f"{y} n={v['n_hh']} Σdwt={v['sum_dwt']:,.0f}" for y, v in d["by_year"].items()) + "\n")

    pv = m["task1_primitive_validation"]
    L.append("## Weighted-index primitives validated (Task 1)\n")
    L.append(f"- Gini vs O(n²) MAD oracle: {pv['gini_vs_mad_oracle_max']:.2e}; integer-weight "
             f"replication: {pv['integer_weight_replication_max']:.2e}; weight-scale invariance: "
             f"{pv['weight_scale_invariance_max']:.2e}; value-scale invariance: "
             f"{pv['value_scale_invariance_max']:.2e}; equal-values→0: {pv['equal_values_zero_max']:.2e}; "
             f"non-positive fails clearly: {pv['nonpositive_fails_clearly']}. ALL ≤1e-12: "
             f"**{pv['all_pass']}**\n")

    L.append("## Headline survey-weighted Gini (Task 2)\n")
    L.append("| scope | measure | n | Σweight | w-mean | w-median | **w-Gini** | unw-Gini | |Δ| |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for s in scopes:
        for me in ["W1", "W4", "W6"]:
            r = bs[s][me]
            L.append(f"| {s} | {me} | {r['n']} | {r['sum_weight']:,.0f} | {big(r['w_mean'])} | "
                     f"{big(r['w_median'])} | **{r['w_gini']:.4f}** | {r['unw_gini']:.4f} | "
                     f"{r['abs_w_minus_unw_gini']:.4f} |")
    L.append("\n(Unweighted Gini is a labeled sensitivity, never the headline.)\n")

    L.append("## Across-measure Gini bracket / spread (Task 3)\n")
    L.append("| scope | min Gini (measure) | max Gini (measure) | bracket | abs spread |")
    L.append("|---|---|---|---|---|")
    for s in scopes:
        z = sp[s]
        L.append(f"| {s} | {z['min_gini']:.4f} ({z['min_measure']}) | {z['max_gini']:.4f} "
                 f"({z['max_measure']}) | [{z['bracket'][0]:.4f}, {z['bracket'][1]:.4f}] | "
                 f"{z['abs_spread']:.4f} |")
    L.append("\nPre-registered across-measure normative-sensitivity result. NOT a decomposition or "
             "opportunity share.\n")

    L.append("## Secondary weighted indices (Task 4)\n")
    L.append("| scope | measure | CV² | Theil L | Atkinson ε=1 | Atkinson ε=2 |")
    L.append("|---|---|---|---|---|---|")
    for s in scopes:
        for me in ["W1", "W4", "W6"]:
            r = bs[s][me]
            L.append(f"| {s} | {me} | {r['w_cv2']:.4f} | {r['w_theil_l']:.4f} | "
                     f"{r['w_atkinson_e1']:.4f} | {r['w_atkinson_e2']:.4f} |")
    wo = m["task4_w1_working_only_appendix"]
    L.append("\nAppendix — W1 working-only weighted Gini: " + "; ".join(
        f"{s} {wo[s]['w_gini']:.4f} (n={wo[s]['n']})" for s in scopes))
    wr = m["task4_w3_validation_readout"]
    L.append(f"\nW3 validation readout (NOT headlined): max|Ω³| = {wr['max_abs_w3_omega']:.2e} "
             f"(≤1e-8: {wr['w3_le_1e8']}).\n")

    L.append("## Tail & stability diagnostics (Task 5)\n")
    L.append("| scope | measure | w-p99 | w-max | top-1% wt share | Gini winsor@p99 (sens.) |")
    L.append("|---|---|---|---|---|---|")
    for s in scopes:
        for me in ["W1", "W4", "W6"]:
            r = bs[s][me]
            L.append(f"| {s} | {me} | {big(r['w_p99'])} | {big(r['w_max'])} | "
                     f"{r['top1pct_weight_share']:.4f} | {r['w_gini_winsor_p99']:.4f} |")
    L.append("\nRank correlations (Spearman) among headline measures:")
    for s in scopes:
        rc = m["task5_rank_correlations"][s]
        L.append(f"- {s}: W1–W4 {rc['W1_W4']:.3f}, W1–W6 {rc['W1_W6']:.3f}, W4–W6 {rc['W4_W6']:.3f}")
    L.append("\nWinsorized results are sensitivity only and do not replace the primary unwinsorized "
             "Gini. W4/W6 are full-compensation measures with large levels (F4C caveat retained).\n")

    inf = m["task6_inference_readiness"]
    L.append("## Inference status (Task 6) — NO bootstrap run\n")
    L.append(f"- Cluster key: **{inf['bootstrap_cluster_key']}**; clusters overall "
             f"**{inf['n_clusters_overall']}** (by group {inf['n_clusters_by_group']}); "
             f"multi-pooled-year clusters {inf['n_clusters_multi_pooled_year']}.")
    L.append(f"- Required: {inf['required_external_operation']}.")
    L.append(f"- Required replicates (scaffold): **{inf['required_replicates']}**.")
    L.append("- Fixed-theta household resampling alone is **not** the pre-registered inference and "
             "cannot produce final headline CIs.\n")

    L.append("## Outputs\n")
    L.append(f"- `{m['output_summary_parquet']}` (sha256 `{m['output_summary_sha256']}`)")
    L.append(f"- `{m['output_households_parquet']}` (sha256 `{m['output_households_sha256']}`)")
    L.append(f"- `F5_manifest_v1.json`; this report.\n")

    L.append("---\n")
    L.append(f"F5 POINT-ESTIMATE STATUS: {m['point_estimate_status']}")
    L.append(f"ACROSS-MEASURE SPREAD STATUS: {m['across_measure_spread_status']}")
    L.append(f"READY FOR F6 DESIGN MEMO: {'yes' if m['ready_for_f6_design_memo'] else 'no'}")
    L.append("CONFERENCE-REPORTABLE WITH CI: NO — cluster-bootstrap re-estimation pending")
    return "\n".join(L)


if __name__ == "__main__":
    main()
