"""STAGE FIVE, INCREMENT FIVE-A — post-estimation descriptives driver (READ-ONLY).

Descriptive statistics + opportunity-set readout + certified-estimate diagnostics
+ a self-contained HTML report, all from the CERTIFIED RURO baseline.

READ-ONLY by construction. This driver does NOT:
  - re-estimate; compute V_i^dir; compute / promote any welfare measure (W^3);
  - price any node; change the spec; swap production; touch any estimator or
    welfare source. It reuses welfare_core's V extractor and the estimator data
    loaders UNCHANGED.

KEY DISTINCTION (load-bearing). welfare_core's V composite is
    V_full = u + (log_h + log_w + log_market) - log_prior
where  log_g_hat = log_h + log_w + log_market  is the OPPORTUNITY DENSITY at the
certified theta and  -log_prior  is the proposal correction.

  TASK 2 "pure opportunity-set readout" uses the OPPORTUNITY BLOCK ONLY:
      g_block = log_h + log_w + log_market   (NO utility u, NO log_prior).
  We obtain it as the exact residual  g_block = V_full - u + log_prior, where u is
  recomputed with the SAME spec-driven leisure/consumption term definitions
  welfare_core uses, and log_prior = log(data.prior). This guarantees g_block is
  byte-consistent with the certified extractor and excludes BOTH u and -log_prior.

  TASK 3 "utility-weighted attractiveness" uses softmax(V_full) — the exact object
  the certified likelihood weights over. Labelled choice-attractiveness, NOT
  opportunity-set size.

All inputs (stems, spec, theta, years) come from welfare.baseline; country/year
are never hardcoded. matplotlib Agg backend; float64; jit V on GPU once per group.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent.parent
_WELFARE = _REPO / "scripts" / "welfare"
_BPOOL = _REPO / "scripts" / "bpool"
_ENH = _REPO / "scripts" / "enhanced"
for _p in (_WELFARE, _BPOOL, _ENH):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402
import welfare_core as wc  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_CONFIG = _REPO / "scripts" / "welfare" / "configs" / "welfare_stage1_w3.yaml"
# Fallback literals (used only if config is missing the field).
_FALLBACK_THETA = "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"
_FALLBACK_SPEC = "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
_FALLBACK_STEM = "fr_p3a_bpool_engine_ready"

_GROUPS = ("singles_male", "singles_female", "couples")
_FIG_DIR = _REPO / "outputs" / "figures"
_OUT_PARQUET = _REPO / "outputs" / "opportunity_diagnostics_certified_v1.parquet"
_HTML = _REPO / "docs" / "jmp_methodology" / "RURO_postestimation_descriptives_v1.html"
_PROV = _REPO / "outputs" / "welfare" / "stage1_w3" / "stage5a_postestimation_descriptives.json"

_CAPTION = ("descriptive at certified theta; not welfare; not re-estimation.")


# ---------------------------------------------------------------------------
# Block classification (mirrors scripts/bpool/step4_realdata_baseline.py)
# ---------------------------------------------------------------------------
def classify_block(name: str) -> str:
    """Map a param name to a reporting block. Spec-driven by suffix/prefix."""
    if name.endswith("_sm") or name.endswith("_sf") or name == "theta_c_singles":
        return "singles_leisure"
    if name.endswith("_m") or name.endswith("_f"):
        if name.startswith("beta_occ_"):
            return "occupation_opp"
        return "couples_leisure"
    if name.startswith("beta_E") or name == "beta_E":
        return "market_hours_opp"
    if name.startswith("beta_h_"):
        return "market_hours_opp"
    if name.startswith("beta_occ_"):
        return "occupation_opp"
    if name.startswith("beta_w") or name == "sigma":
        return "wage_opp"
    return "other"


# economic grouping of blocks (wage_opp=ability; market/occ=access; leisure=preference)
_BLOCK_ROLE = {
    "wage_opp": "ability/wage",
    "market_hours_opp": "opportunity/access",
    "occupation_opp": "opportunity/access",
    "singles_leisure": "preference",
    "couples_leisure": "preference",
    "other": "other",
}


# ---------------------------------------------------------------------------
# Config + certified inputs
# ---------------------------------------------------------------------------
def load_config():
    import yaml

    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)["welfare"]
    return cfg


def resolve_inputs(cfg):
    b = cfg.get("baseline", {})
    theta_path = b.get("theta_hat_path", _FALLBACK_THETA)
    spec_path = b.get("spec_yaml_path", _FALLBACK_SPEC)
    stem = b.get("engine_ready_stem", _FALLBACK_STEM)
    couples_stem = b.get("couples_stem", stem)
    years = list(b.get("years", []) or [])
    return {
        "theta_hat_path": theta_path,
        "spec_yaml_path": spec_path,
        "engine_ready_stem": stem,
        "couples_stem": couples_stem,
        "years": years,
    }


def load_theta_table(theta_path):
    """The certified theta CSV carries value, se_hessian, se_clustered per param."""
    df = pd.read_csv(_REPO / theta_path if not Path(theta_path).is_absolute() else theta_path)
    return df


# ---------------------------------------------------------------------------
# Opportunity block g_block = log_h + log_w + log_market  (NO u, NO log_prior)
# Computed as the exact residual V_full - u + log_prior using welfare_core's own
# extractor for V_full and the SAME spec-driven u definition.
# ---------------------------------------------------------------------------
def _box_cox_np(x, theta):
    x = np.asarray(x, dtype=np.float64)
    if abs(float(theta)) < 1e-8:
        return np.log(x)
    return (np.power(x, float(theta)) - 1.0) / float(theta)


def _utility_singles(data, spec, theta, group):
    """u = beta_l(covariates) * boxcox(leisure, theta_l) + beta_c * boxcox(cons, theta_c).

    Mirrors welfare_core._build_V_extractor (singles) lines ~244-252 exactly so the
    residual V_full - u is the opportunity block."""
    suffix = "_sm" if group == "singles_male" else "_sf"
    is_male = group == "singles_male"
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def P(name):
        if name in fixed:
            return float(fixed[name])
        return float(theta[pidx[name]])

    leisure = np.asarray(data.leisure, dtype=np.float64)
    consumption = np.asarray(data.consumption, dtype=np.float64)
    theta_l_name = (spec.utility_leisure_theta + suffix) if spec.utility_leisure_theta else None
    theta_c_name = spec.theta_c_param_name(group)
    theta_l = P(theta_l_name) if theta_l_name else 0.0
    theta_c = P(theta_c_name) if theta_c_name else 0.0
    bc_l = _box_cox_np(leisure, theta_l)
    bc_c = _box_cox_np(consumption, theta_c)
    beta_l = P(spec.utility_leisure_intercept + suffix)
    for sh in spec.utility_leisure_shifters:
        var, coef = sh["variable"], sh["coefficient"]
        if sh.get("gender_specific", False) and var == "n_children" and is_male:
            continue
        arr = getattr(data, var, None)
        if arr is None:
            continue
        beta_l = beta_l + P(coef + suffix) * np.asarray(arr, dtype=np.float64)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)
    beta_c = (beta_c_fixed if beta_c_fixed is not None
              else P(spec.utility_consumption_coef + suffix))
    return beta_l * bc_l + beta_c * bc_c


def _utility_couples(data, spec, theta):
    """u for couples: blc_m*bc_l_m + blc_f*bc_l_f + beta_c*bc_c + beta_ll*bc_l_m*bc_l_f.

    Mirrors welfare_core._build_V_extractor_couples lines ~399-414 exactly."""
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def P(name):
        if name in fixed:
            return float(fixed[name])
        return float(theta[pidx[name]])

    leisure_m = np.asarray(data.leisure_male, dtype=np.float64)
    leisure_f = np.asarray(data.leisure_female, dtype=np.float64)
    consumption = np.asarray(data.consumption, dtype=np.float64)
    n_children = getattr(data, "n_children", None)

    theta_l_m_name = (spec.utility_leisure_theta + "_m") if spec.utility_leisure_theta else None
    theta_l_f_name = (spec.utility_leisure_theta + "_f") if spec.utility_leisure_theta else None
    couples_theta_c_fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None)
    theta_l_m = P(theta_l_m_name) if theta_l_m_name else 0.0
    theta_l_f = P(theta_l_f_name) if theta_l_f_name else 0.0
    theta_c = float(couples_theta_c_fixed) if couples_theta_c_fixed is not None else 0.0
    bc_l_m = _box_cox_np(leisure_m, theta_l_m)
    bc_l_f = _box_cox_np(leisure_f, theta_l_f)
    bc_c = _box_cox_np(consumption, theta_c)

    blc_m = P(spec.utility_leisure_intercept + "_m")
    blc_f = P(spec.utility_leisure_intercept + "_f")
    for sh in spec.utility_leisure_shifters:
        var, coef = sh["variable"], sh["coefficient"]
        if var == "n_children":
            if n_children is not None:
                blc_f = blc_f + P(coef + "_f") * np.asarray(n_children, dtype=np.float64)
            continue
        am = getattr(data, var + "_male", None)
        af = getattr(data, var + "_female", None)
        if am is not None:
            blc_m = blc_m + P(coef + "_m") * np.asarray(am, dtype=np.float64)
        if af is not None:
            blc_f = blc_f + P(coef + "_f") * np.asarray(af, dtype=np.float64)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)
    beta_c = (beta_c_fixed if beta_c_fixed is not None
              else P(spec.utility_consumption_coef))
    interaction_name = spec.couples_interaction_coef
    beta_ll = P(interaction_name) if interaction_name else 0.0
    return (blc_m * bc_l_m + blc_f * bc_l_f + beta_c * bc_c
            + beta_ll * bc_l_m * bc_l_f)


def opportunity_block(data, spec, theta, group):
    """Per-row PURE opportunity block g_block = log_h + log_w + log_market.

    Excludes utility u AND -log_prior. Computed as the exact residual of the
    certified V extractor: g_block = V_full - u + log_prior. Returns (n_groups,
    n_alts) g_block grid, plus the full-V grid for Task 3."""
    Vfn, meta = wc._build_V_extractor(data, spec, group)
    if Vfn is None:
        raise SystemExit(f"STOP: V extractor unavailable for {group} (couples deferred path).")
    n_groups, n_alts = int(meta["n_groups"]), int(meta["n_alts"])
    th = jnp.asarray(np.asarray(theta, dtype=np.float64))
    cons = jnp.asarray(meta["consumption"])
    V_full = np.asarray(Vfn(th, cons), dtype=np.float64)
    if group == "couples":
        u = _utility_couples(data, spec, theta)
    else:
        u = _utility_singles(data, spec, theta, group)
    log_prior = np.log(np.asarray(data.prior, dtype=np.float64))
    g_block = V_full - u + log_prior  # = log_h + log_w + log_market
    return (g_block.reshape(n_groups, n_alts),
            V_full.reshape(n_groups, n_alts),
            n_groups, n_alts, meta)


# ---------------------------------------------------------------------------
# Per-household softmax diagnostics (entropy / eff count / ess count / max)
# ---------------------------------------------------------------------------
def _softmax_diag(grid):
    """grid: (n_groups, n_alts) of (un-normalised) log-weights. Returns dict of
    per-HH series: entropy H = -sum p log p, eff_count = exp(H), ess_count =
    1/sum(p^2), max_w = max p."""
    g = jnp.asarray(grid, dtype=jnp.float64)
    mx = jnp.max(g, axis=1, keepdims=True)
    p = jnp.exp(g - mx)
    p = p / jnp.sum(p, axis=1, keepdims=True)
    logp = jnp.where(p > 0, jnp.log(p), 0.0)
    H = -jnp.sum(p * logp, axis=1)
    eff = jnp.exp(H)
    ess = 1.0 / jnp.sum(p * p, axis=1)
    max_w = jnp.max(p, axis=1)
    return {
        "entropy": np.asarray(H, dtype=np.float64),
        "eff_count": np.asarray(eff, dtype=np.float64),
        "ess_count": np.asarray(ess, dtype=np.float64),
        "max_w": np.asarray(max_w, dtype=np.float64),
    }


# ---------------------------------------------------------------------------
# Engine-ready per-HH covariate join (chosen / draw==0 row per HH)
# ---------------------------------------------------------------------------
def _hh_covariates(stem, group, years):
    """One row per HH (the chosen alternative) with HH-constant covariates, keyed
    by group_id == the SAME group key precompute forms (idhh*10+year_tag if
    multi-year else idhh). Returns (DataFrame indexed by group_key, absent list)."""
    bp = bpool_dir()
    is_couple = group == "couples"
    mode = "couples" if is_couple else "singles"
    path = bp / f"{stem}__{mode}.parquet"
    df = pd.read_parquet(path)
    if years:
        df = df[df["data_year"].isin(years)].copy()
    if not is_couple:
        flag = 1.0 if group == "singles_male" else 0.0
        df = df[df["dgn"] == flag].copy()
    chosen_col = ("is_chosen_joint" if (is_couple and "is_chosen_joint" in df.columns)
                  else "is_chosen")
    if chosen_col in df.columns:
        sel = df[pd.to_numeric(df[chosen_col], errors="coerce").fillna(0) > 0.5].copy()
    else:
        draw_col = "draw_joint" if is_couple else "draw"
        sel = df[df[draw_col] == 0].copy()
    multi_year = df["year_tag"].nunique() > 1 if "year_tag" in df.columns else False
    if multi_year:
        key = sel["idhh"].astype(np.int64) * 10 + sel["year_tag"].astype(np.int64)
    else:
        key = sel["idhh"].astype(np.int64)
    sel = sel.assign(_group_key=key.values)
    sel = sel.drop_duplicates("_group_key").set_index("_group_key")

    absent = []
    out = pd.DataFrame(index=sel.index)
    out["stacked_hh_uid"] = sel.get("stacked_hh_uid", pd.Series(index=sel.index, dtype="float"))

    # year / mode
    out["data_year"] = sel.get("data_year", pd.Series(index=sel.index, dtype="float"))

    # region id (drgn1 1..8 or reg_nuts1_*)
    if "drgn1" in sel.columns and sel["drgn1"].notna().any():
        out["region"] = pd.to_numeric(sel["drgn1"], errors="coerce")
    elif any(f"reg_nuts1_{k}" in sel.columns for k in range(1, 9)):
        reg = np.full(len(sel), np.nan)
        for k in range(1, 9):
            c = f"reg_nuts1_{k}"
            if c in sel.columns:
                mask = pd.to_numeric(sel[c], errors="coerce").fillna(0).to_numpy() > 0.5
                reg[mask] = k
        out["region"] = reg
    else:
        absent.append("region(drgn1/reg_nuts1_*)")
        out["region"] = np.nan

    # educ3 (singles: educ3; couples: educ3_male / educ3_female)
    if not is_couple:
        if "educ3" in sel.columns:
            out["educ3"] = pd.to_numeric(sel["educ3"], errors="coerce")
        else:
            absent.append("educ3")
            out["educ3"] = np.nan
    else:
        for who in ("male", "female"):
            c = f"educ3_{who}"
            if c in sel.columns:
                out[f"educ3_{who}"] = pd.to_numeric(sel[c], errors="coerce")
            else:
                absent.append(c)
                out[f"educ3_{who}"] = np.nan

    # local vars gsur (continuous->bin downstream), drgur, drgmd (HH level)
    for v in ("gsur", "drgur", "drgmd"):
        if v in sel.columns and sel[v].notna().any():
            out[v] = pd.to_numeric(sel[v], errors="coerce")
        else:
            absent.append(v)
            out[v] = np.nan

    return out, sorted(set(absent))


# ---------------------------------------------------------------------------
# Figure helpers
# ---------------------------------------------------------------------------
def _save_fig(fig, name):
    _FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = _FIG_DIR / name
    fig.savefig(path, dpi=110, bbox_inches="tight")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return str(path), b64


def _caption(ax_or_fig, text):
    full = f"{text}  [{_CAPTION}]"
    ax_or_fig.text(0.5, -0.02, full, ha="center", va="top",
                   transform=ax_or_fig.transFigure if hasattr(ax_or_fig, "transFigure")
                   else ax_or_fig.transAxes, fontsize=7, color="dimgray")


# ---------------------------------------------------------------------------
# TASK 1 — estimate / SE table by block
# ---------------------------------------------------------------------------
def task1_estimate_table(theta_df, spec, figures):
    bounds = getattr(spec, "bounds", {}) or {}
    fixed = dict(getattr(spec, "fixed_params", {}) or {})
    # beta_ll is fully removed from the 47-vector but is a structurally fixed=0 param.
    fixed_display = dict(fixed)
    fixed_display.setdefault("beta_ll", 0.0)

    lookup = {str(r["parameter"]): r for _, r in theta_df.iterrows()}
    rows = []
    for n in spec.all_param_names:
        r = lookup.get(n)
        if r is None:
            continue
        val = float(r["value"])
        seh = float(r["se_hessian"]) if pd.notna(r["se_hessian"]) else None
        sec = float(r["se_clustered"]) if pd.notna(r["se_clustered"]) else None
        t = (val / sec) if (sec and sec > 0) else None
        sig = bool(t is not None and abs(t) > 1.96)
        block = classify_block(n)
        lo, hi = bounds.get(n, (None, None))
        at_bound = False
        which_bound = None
        for bnd in (lo, hi):
            if bnd is not None and abs(val - float(bnd)) < 1e-5:
                at_bound = True
                which_bound = float(bnd)
        rows.append({
            "param": n, "block": block, "role": _BLOCK_ROLE.get(block, "other"),
            "value": val, "se_hessian": seh, "se_clustered": sec,
            "t": t, "significant": sig, "fixed": False,
            "at_bound": at_bound, "bound_value": which_bound,
        })
    # append fixed / pinned params for completeness
    for n, v in fixed_display.items():
        rows.append({
            "param": n, "block": classify_block(n),
            "role": _BLOCK_ROLE.get(classify_block(n), "other"),
            "value": float(v), "se_hessian": None, "se_clustered": None,
            "t": None, "significant": False, "fixed": True,
            "at_bound": False, "bound_value": None,
        })

    # block-level SE asymmetry summary
    block_summary = {}
    for block in sorted({r["block"] for r in rows}):
        secs = [r["se_clustered"] for r in rows
                if r["block"] == block and r["se_clustered"] is not None]
        n_sig = sum(1 for r in rows if r["block"] == block and r["significant"])
        n_free = sum(1 for r in rows if r["block"] == block and not r["fixed"])
        block_summary[block] = {
            "role": _BLOCK_ROLE.get(block, "other"),
            "n_free": n_free,
            "n_significant": n_sig,
            "median_se_clustered": float(np.median(secs)) if secs else None,
            "iqr_se_clustered": (float(np.subtract(*np.percentile(secs, [75, 25])))
                                 if len(secs) >= 2 else None),
            "max_se_clustered": float(np.max(secs)) if secs else None,
        }

    # Figure: SE asymmetry by block (median + spread of se_clustered)
    blocks = [b for b in block_summary if block_summary[b]["median_se_clustered"] is not None]
    blocks = sorted(blocks, key=lambda b: block_summary[b]["median_se_clustered"])
    fig, ax = plt.subplots(figsize=(8, 4.2))
    data_by_block = []
    labels = []
    for b in blocks:
        secs = [r["se_clustered"] for r in rows
                if r["block"] == b and r["se_clustered"] is not None]
        data_by_block.append(secs)
        labels.append(f"{b}\n({block_summary[b]['role']})")
    ax.boxplot(data_by_block, tick_labels=labels, showmeans=True)
    ax.set_ylabel("se_clustered")
    ax.set_title("Task 1 — clustered-SE asymmetry by block (tight access vs wide preference)")
    ax.tick_params(axis="x", labelsize=7)
    _caption(fig, "Per-block clustered standard errors at the certified MLE")
    p, b64 = _save_fig(fig, "stage5a_task1_se_asymmetry.png")
    figures.append(("Task 1 — SE asymmetry by block", p, b64))

    return {"rows": rows, "block_summary": block_summary,
            "n_params": len(spec.all_param_names),
            "n_significant_total": sum(1 for r in rows if r["significant"])}


# ---------------------------------------------------------------------------
# TASKS 2 + 3 — opportunity (pure g_hat) vs utility-weighted diagnostics
# ---------------------------------------------------------------------------
def tasks_2_3_opportunity(data_by_group, spec, theta, figures):
    per_group = {}
    parquet_rows = []
    for group, data in data_by_group.items():
        g_grid, V_grid, n_groups, n_alts, _meta = opportunity_block(data, spec, theta, group)
        opp = _softmax_diag(g_grid)        # Task 2 — pure opportunity
        att = _softmax_diag(V_grid)        # Task 3 — utility-weighted (full V)
        cluster_ids = np.asarray(getattr(data, "cluster_ids"))
        group_ids = np.asarray(getattr(data, "group_ids"))
        ratio = att["eff_count"] / np.maximum(opp["eff_count"], 1e-12)
        for i in range(n_groups):
            parquet_rows.append({
                "group": group,
                "group_id": int(group_ids[i]) if i < len(group_ids) else -1,
                "cluster_id": int(cluster_ids[i]) if i < len(cluster_ids) else -1,
                "support": int(n_alts),
                "opp_entropy": float(opp["entropy"][i]),
                "opp_eff_count": float(opp["eff_count"][i]),
                "opp_ess_count": float(opp["ess_count"][i]),
                "opp_max_w": float(opp["max_w"][i]),
                "att_entropy": float(att["entropy"][i]),
                "att_eff_count": float(att["eff_count"][i]),
                "att_ess_count": float(att["ess_count"][i]),
                "att_max_w": float(att["max_w"][i]),
                "att_over_opp_eff_ratio": float(ratio[i]),
            })

        def _summ(d):
            return {k: {"median": float(np.median(d[k])),
                        "mean": float(np.mean(d[k])),
                        "p10": float(np.percentile(d[k], 10)),
                        "p90": float(np.percentile(d[k], 90))}
                    for k in ("entropy", "eff_count", "ess_count", "max_w")}

        per_group[group] = {
            "n_hh": int(n_groups), "support": int(n_alts),
            "opportunity_summary": _summ(opp),
            "attractiveness_summary": _summ(att),
            "att_over_opp_eff_ratio": {
                "median": float(np.median(ratio)),
                "p10": float(np.percentile(ratio, 10)),
                "p90": float(np.percentile(ratio, 90)),
            },
            "_opp": opp, "_att": att, "_ratio": ratio,
        }

    # Task 2 figure: opportunity eff-count histograms, singles vs couples separate
    fig, axes = plt.subplots(1, len(per_group), figsize=(4.2 * len(per_group), 3.6),
                             squeeze=False)
    for ax, (group, d) in zip(axes[0], per_group.items()):
        ax.hist(d["_opp"]["eff_count"], bins=40, color="steelblue", alpha=0.8)
        ax.set_title(f"{group}\nsupport={d['support']}", fontsize=9)
        ax.set_xlabel("effective opportunity count = exp(H)")
        ax.set_ylabel("households")
    fig.suptitle("Task 2 — pure opportunity-set effective count (g_hat only; no u, no log_prior)")
    _caption(fig, "Opportunity entropy effective count per household, by mode")
    p, b64 = _save_fig(fig, "stage5a_task2_opportunity_effcount.png")
    figures.append(("Task 2 — pure opportunity effective count", p, b64))

    # Task 3 figure: scatter opp eff vs att eff + ratio distribution per group
    fig, axes = plt.subplots(2, len(per_group), figsize=(4.2 * len(per_group), 7),
                             squeeze=False)
    for j, (group, d) in enumerate(per_group.items()):
        ax = axes[0][j]
        ax.scatter(d["_opp"]["eff_count"], d["_att"]["eff_count"], s=4, alpha=0.3,
                   color="darkorange")
        lim = max(float(np.max(d["_opp"]["eff_count"])),
                  float(np.max(d["_att"]["eff_count"])))
        ax.plot([0, lim], [0, lim], "k--", lw=0.8)
        ax.set_title(group, fontsize=9)
        ax.set_xlabel("pure opportunity eff count (Task 2)")
        ax.set_ylabel("utility-weighted eff count (Task 3)")
        ax2 = axes[1][j]
        ax2.hist(d["_ratio"], bins=40, color="seagreen", alpha=0.8)
        ax2.axvline(1.0, color="k", ls="--", lw=0.8)
        ax2.set_xlabel("att eff / opp eff (compression<1, expansion>1)")
        ax2.set_ylabel("households")
    fig.suptitle("Task 3 — choice-attractiveness / likelihood-weighted vs pure opportunity")
    _caption(fig, "How preferences+consumption compress/expand effective mass")
    p, b64 = _save_fig(fig, "stage5a_task3_attractiveness_vs_opportunity.png")
    figures.append(("Task 3 — attractiveness vs opportunity", p, b64))

    # strip the heavy arrays before returning JSON-able summaries; keep parquet rows
    for d in per_group.values():
        d.pop("_opp", None)
        d.pop("_att", None)
        d.pop("_ratio", None)
    return per_group, parquet_rows


# ---------------------------------------------------------------------------
# TASK 4 — heterogeneity cross-tabs by covariate
# ---------------------------------------------------------------------------
def task4_heterogeneity(parquet_df, cfg_inputs, figures):
    by_group_cov = {}
    absent_all = set()
    cov_frames = {}
    for group in _GROUPS:
        cov, absent = _hh_covariates(
            cfg_inputs["couples_stem"] if group == "couples" else cfg_inputs["engine_ready_stem"],
            group, cfg_inputs["years"])
        cov_frames[group] = cov
        absent_all.update(f"{group}:{a}" for a in absent)

    diag = parquet_df.copy()
    crosstabs = {}
    for group in _GROUPS:
        sub = diag[diag["group"] == group].copy()
        cov = cov_frames[group]
        # join on group_id == covariate group key
        sub = sub.set_index("group_id")
        joined = sub.join(cov, how="left")

        # gsur continuous -> tertile bin
        if "gsur" in joined.columns and joined["gsur"].notna().any():
            try:
                joined["gsur_bin"] = pd.qcut(joined["gsur"], 3, labels=["low", "mid", "high"],
                                             duplicates="drop")
            except ValueError:
                joined["gsur_bin"] = "all"
        cat_vars = []
        if group == "couples":
            edu_cols = [c for c in ("educ3_male", "educ3_female") if c in joined.columns]
        else:
            edu_cols = [c for c in ("educ3",) if c in joined.columns]
        for v in ["region", *edu_cols, "gsur_bin", "drgur", "drgmd"]:
            if v in joined.columns and joined[v].notna().any():
                cat_vars.append(v)

        gct = {}
        for v in cat_vars:
            grp = joined.groupby(v, observed=True)
            gct[v] = {
                "opp_eff_count_median": grp["opp_eff_count"].median().to_dict(),
                "att_eff_count_median": grp["att_eff_count"].median().to_dict(),
                "n": grp.size().to_dict(),
            }
        crosstabs[group] = gct
        by_group_cov[group] = joined

    # Figure: opp & att eff_count by region per group (where present)
    panels = [(g, "region") for g in _GROUPS
              if "region" in by_group_cov[g].columns
              and by_group_cov[g]["region"].notna().any()]
    if panels:
        fig, axes = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 3.8),
                                 squeeze=False)
        for ax, (g, v) in zip(axes[0], panels):
            j = by_group_cov[g]
            grp = j.groupby(v, observed=True)
            med_opp = grp["opp_eff_count"].median()
            med_att = grp["att_eff_count"].median()
            x = np.arange(len(med_opp))
            ax.bar(x - 0.2, med_opp.values, width=0.4, label="opp (Task 2)", color="steelblue")
            ax.bar(x + 0.2, med_att.values, width=0.4, label="att (Task 3)", color="darkorange")
            ax.set_xticks(x)
            ax.set_xticklabels([str(int(k)) if float(k).is_integer() else str(k)
                                for k in med_opp.index], fontsize=7)
            ax.set_title(f"{g} by {v}", fontsize=9)
            ax.set_ylabel("median eff count")
            ax.legend(fontsize=7)
        fig.suptitle("Task 4 — effective counts by region (opportunity vs attractiveness)")
        _caption(fig, "Median effective counts cross-tabbed by region")
        p, b64 = _save_fig(fig, "stage5a_task4_heterogeneity_region.png")
        figures.append(("Task 4 — heterogeneity by region", p, b64))

    return {"crosstabs": crosstabs, "absent_variables": sorted(absent_all)}


# ---------------------------------------------------------------------------
# TASK 5 — wage / hours / LOC4 structure at certified theta
# ---------------------------------------------------------------------------
def task5_wage_hours_loc4(theta_df, spec, data_by_group, figures):
    lookup = {str(r["parameter"]): float(r["value"]) for _, r in theta_df.iterrows()}

    def P(name):
        return float(lookup.get(name, 0.0))

    # ONE log-wage density: mu = beta_w0 + beta_w_educL*educL + beta_w_educH*educH
    #   + beta_w_pexp*pexp + beta_w_pexp2*pexp2 ; common sigma; occupation enters as
    #   a MEAN SHIFT through the market/occupation block (beta_occ_*), NOT a 4th density.
    sigma = P("sigma")
    # representative covariates (educL=0/educH=0 ref, pexp at sample-ish midpoint)
    pexp = 15.0
    pexp2 = pexp ** 2
    mu_base = (P("beta_w0") + P("beta_w_pexp") * pexp + P("beta_w_pexp2") * pexp2)

    # occupation mean shifts (male block as the illustrative gender; loc4=1 reference=0)
    occ_shift = {
        1: 0.0,
        2: P("beta_occ_2_m"),
        3: P("beta_occ_3_m"),
        4: P("beta_occ_4_m"),
    }
    finding = {
        "one_density_with_occupation_mean_shifts": True,
        "n_sigma": 1,
        "sigma": sigma,
        "explanation": (
            "wage_opportunity declares a SINGLE log-normal with one sigma; occupation "
            "(beta_occ_2/3/4) enters the market/occupation opportunity block as a MEAN "
            "shifter, not as a separate variance. The certified spec implements ONE "
            "log-wage density whose mean is shifted by LOC4; it is NOT four distinct "
            "densities."),
        "occupation_mean_shifts_male_block": occ_shift,
        "mean_shifters": [(s["variable"], s["coefficient"]) for s in spec.wage_mean_shifters],
    }

    # Plot: 4 log-normal wage curves sharing sigma, shifted means (the one-vs-four view)
    wgrid = np.linspace(0.5, 60.0, 600)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for lo4 in (1, 2, 3, 4):
        mu = mu_base + occ_shift[lo4]
        # log-normal density in wage: f(w) = 1/(w sigma sqrt(2pi)) exp(-(ln w - mu)^2/2sigma^2)
        dens = (1.0 / (wgrid * sigma * np.sqrt(2 * np.pi))
                * np.exp(-((np.log(wgrid) - mu) ** 2) / (2 * sigma ** 2)))
        ax.plot(wgrid, dens, label=f"LOC4={lo4} (mu={mu:.2f})")
    ax.set_xlabel("wage (2016-real)")
    ax.set_ylabel("implied density")
    ax.set_title("Task 5 — implied LOC4-conditional wage densities (ONE sigma, shifted means)")
    ax.legend(fontsize=8)
    _caption(fig, "One log-wage density with occupation mean shifts; common sigma")
    p, b64 = _save_fig(fig, "stage5a_task5_loc4_wage_densities.png")
    figures.append(("Task 5 — LOC4 wage densities (one-vs-four)", p, b64))

    # Hours opportunity offsets (beta_h_pt1/pt2/ft/lh as hours-band log-offsets)
    hours_bands = {
        "beta_E (any work)": P("beta_E"),
        "beta_h_pt1": P("beta_h_pt1"),
        "beta_h_pt2": P("beta_h_pt2"),
        "beta_h_ft": P("beta_h_ft"),
        "beta_h_lh": P("beta_h_lh"),
    }
    fig, ax = plt.subplots(figsize=(7, 4))
    keys = list(hours_bands.keys())
    ax.bar(keys, [hours_bands[k] for k in keys], color="slateblue")
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_ylabel("log opportunity offset at certified theta")
    ax.set_title("Task 5 — hours-band opportunity offsets (F35 = reference)")
    ax.tick_params(axis="x", labelsize=8, rotation=20)
    _caption(fig, "Hours-band opportunity offsets at the certified MLE")
    p, b64 = _save_fig(fig, "stage5a_task5_hours_offsets.png")
    figures.append(("Task 5 — hours-band offsets", p, b64))

    # Employment / occupation support summary from certified support (chosen rows)
    occ_support = {}
    for group, data in data_by_group.items():
        # share of alternatives that are 'working' and loc4 distribution over the support
        working = getattr(data, "working", None)
        if working is None:
            working = getattr(data, "working_male", None)
        loc4 = getattr(data, "loc4", None)
        rec = {}
        if working is not None:
            rec["working_share_over_support"] = float(np.mean(np.asarray(working)))
        if loc4 is not None:
            vals, cnts = np.unique(np.asarray(loc4), return_counts=True)
            rec["loc4_share"] = {int(v): float(c / cnts.sum()) for v, c in zip(vals, cnts)}
        occ_support[group] = rec

    finding["hours_band_offsets"] = hours_bands
    finding["occupation_support_summary"] = occ_support
    return finding


# ---------------------------------------------------------------------------
# TASK 6 — ESS distributions via compute_group_welfare(...).ess
# ---------------------------------------------------------------------------
def task6_ess(data_by_group, spec, theta, figures):
    out = {}
    ess_by_group = {}
    for group, data in data_by_group.items():
        gw = wc.compute_group_welfare(data, spec, theta, group)
        ess = np.asarray(gw.ess, dtype=np.float64)
        ess = ess[np.isfinite(ess)]
        ess_by_group[group] = ess
        out[group] = {
            "n_hh": int(gw.n_groups),
            "ess_median": float(np.median(ess)) if ess.size else None,
            "ess_p10": float(np.percentile(ess, 10)) if ess.size else None,
            "ess_p90": float(np.percentile(ess, 90)) if ess.size else None,
            "ess_min": float(np.min(ess)) if ess.size else None,
            "share_below_30": float(np.mean(ess < 30.0)) if ess.size else None,
        }
    fig, axes = plt.subplots(1, len(ess_by_group), figsize=(4.2 * len(ess_by_group), 3.6),
                             squeeze=False)
    for ax, (group, ess) in zip(axes[0], ess_by_group.items()):
        if ess.size:
            ax.hist(ess, bins=40, color="indianred", alpha=0.85)
            ax.axvline(30.0, color="k", ls="--", lw=0.8, label="ESS=30")
            ax.legend(fontsize=7)
        ax.set_title(group, fontsize=9)
        ax.set_xlabel("ESS_i (importance-sampling)")
        ax.set_ylabel("households")
    fig.suptitle("Task 6 — per-household ESS (estimator diagnostics, NOT welfare results)")
    _caption(fig, "ESS_i = 1/sum(omega^2); estimator diagnostic, not a welfare result")
    p, b64 = _save_fig(fig, "stage5a_task6_ess.png")
    figures.append(("Task 6 — ESS distributions", p, b64))
    return out


# ---------------------------------------------------------------------------
# TASK 7 — self-contained HTML
# ---------------------------------------------------------------------------
def _fmt(v, nd):
    return "" if v is None else f"{v:.{nd}f}"


def _t1_table_html(t1):
    head = ("<tr><th>param</th><th>block</th><th>role</th><th>value</th>"
            "<th>se_hessian</th><th>se_clustered</th><th>t</th><th>sig|t|&gt;1.96</th>"
            "<th>fixed</th><th>at_bound</th></tr>")
    body = []
    for r in t1["rows"]:
        seh = _fmt(r["se_hessian"], 4)
        sec = _fmt(r["se_clustered"], 4)
        tt = _fmt(r["t"], 2)
        sig = "YES" if r["significant"] else ""
        fx = "fixed" if r["fixed"] else ""
        bd = "bound" if r["at_bound"] else ""
        body.append(
            "<tr>"
            f"<td>{r['param']}</td><td>{r['block']}</td><td>{r['role']}</td>"
            f"<td>{r['value']:.4f}</td>"
            f"<td>{seh}</td><td>{sec}</td><td>{tt}</td>"
            f"<td>{sig}</td><td>{fx}</td><td>{bd}</td>"
            "</tr>")
    return f"<table class='t'>{''.join([head, *body])}</table>"


def build_html(inputs, t1, t23, t4, t5, t6, figures, prov):
    def fig_block(title, b64):
        # every caption MUST carry the mandatory compliance tag (prompt requirement)
        return (f"<figure><figcaption>{title} — <em>{_CAPTION}</em></figcaption>"
                f"<img src='data:image/png;base64,{b64}'/></figure>")

    figs_html = "\n".join(fig_block(t, b) for (t, _p, b) in figures)
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>RURO post-estimation descriptives v1</title>",
        "<style>body{font-family:system-ui,Arial,sans-serif;margin:24px;color:#222;}"
        "table.t{border-collapse:collapse;font-size:11px;}"
        "table.t th,table.t td{border:1px solid #ccc;padding:2px 6px;text-align:right;}"
        "table.t th{background:#f0f0f0;}"
        "figure{margin:18px 0;}figcaption{font-weight:600;margin-bottom:4px;}"
        "img{max-width:980px;border:1px solid #eee;}"
        "pre{background:#f7f7f7;padding:10px;font-size:11px;overflow:auto;}"
        ".note{color:#a33;font-size:12px;}</style></head><body>",
        "<h1>RURO post-estimation descriptives — v1 (Stage Five, Increment Five-A)</h1>",
        f"<p class='note'>READ-ONLY descriptive report at the certified theta. "
        f"Not welfare; not re-estimation. Generated {prov['generated_utc']}.</p>",
        "<h2>Certified inputs</h2><pre>"
        + json.dumps(inputs, indent=2) + "</pre>",
        "<h2>Task 1 — estimate / SE table by block</h2>",
        f"<p>Total params: {t1['n_params']}; significant (|t|&gt;1.96): "
        f"{t1['n_significant_total']}.</p>",
        _t1_table_html(t1),
        "<h3>Block SE summary</h3><pre>" + json.dumps(t1["block_summary"], indent=2) + "</pre>",
        "<h2>Tasks 2 &amp; 3 — opportunity vs choice-attractiveness</h2>",
        "<p><b>Task 2 (pure opportunity-set):</b> per-HH softmax over the opportunity "
        "block g_block = log_h + log_w + log_market (EXCLUDES utility u AND -log_prior). "
        "Entropy H = -&Sigma; p_g log p_g; effective opportunity count = exp(H); "
        "ESS-style count = 1/&Sigma; p_g&sup2;; support = 101 singles / 901 couples. "
        "Singles and couples are kept SEPARATE (never pooled).</p>",
        "<p><b>Task 3 (choice-attractiveness / likelihood-weighted):</b> per-HH softmax "
        "over the FULL certified V = u + log g_hat - log_prior (the exact object the "
        "likelihood uses). This is NOT opportunity-set size.</p>",
        "<pre>" + json.dumps(t23, indent=2) + "</pre>",
        "<h2>Task 4 — heterogeneity cross-tabs</h2>",
        "<pre>" + json.dumps(t4, indent=2, default=str) + "</pre>",
        "<h2>Task 5 — wage / hours / LOC4 structure</h2>",
        "<p class='note'>ONE log-wage density with occupation MEAN shifts (beta_occ_*) "
        "and a COMMON sigma — NOT four distinct densities.</p>",
        "<pre>" + json.dumps(t5, indent=2, default=str) + "</pre>",
        "<h2>Task 6 — ESS distributions (estimator diagnostics, not welfare)</h2>",
        "<pre>" + json.dumps(t6, indent=2) + "</pre>",
        "<h2>Figures</h2>",
        figs_html,
        "</body></html>",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Stage 5a post-estimation descriptives (read-only).")
    ap.add_argument("--n-hh", type=int, default=0,
                    help="households per group (0 = all; default 0)")
    args = ap.parse_args()

    cfg = load_config()
    inputs = resolve_inputs(cfg)
    inputs["n_hh"] = args.n_hh

    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    theta_df = load_theta_table(inputs["theta_hat_path"])

    # data (reuse estimator loader; n_hh=0 -> all)
    data = wc.load_data(cfg, n_hh=args.n_hh)
    wc.assert_resolution(cfg, data)
    data_by_group = {g: data[g] for g in _GROUPS}

    figures = []

    t1 = task1_estimate_table(theta_df, spec, figures)
    t23, parquet_rows = tasks_2_3_opportunity(data_by_group, spec, theta, figures)

    parquet_df = pd.DataFrame(parquet_rows)
    _OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    parquet_df.to_parquet(_OUT_PARQUET, index=False)

    t4 = task4_heterogeneity(parquet_df, inputs, figures)
    t5 = task5_wage_hours_loc4(theta_df, spec, data_by_group, figures)
    t6 = task6_ess(data_by_group, spec, theta, figures)

    prov = {
        "increment": "stage5a_postestimation_descriptives_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": inputs,
        "deliverables": {
            "opportunity_parquet": str(_OUT_PARQUET),
            "html": str(_HTML),
            "figures": [p for (_t, p, _b) in figures],
        },
        "task1_estimate_table": {
            "n_params": t1["n_params"],
            "n_significant_total": t1["n_significant_total"],
            "block_summary": t1["block_summary"],
        },
        "task2_3_opportunity_attractiveness": t23,
        "task4_heterogeneity": {"crosstabs": t4["crosstabs"]},
        "task5_wage_hours_loc4": t5,
        "task6_ess": t6,
        "absent_variables": t4["absent_variables"],
        "scope": {
            "read_only": True,
            "re_estimated": False,
            "computed_v_dir": False,
            "computed_welfare": False,
            "promoted_w3": False,
            "priced_node": False,
            "spec_changed": False,
            "production_swapped": False,
        },
        "g_block_construction": (
            "g_block = V_full - u + log_prior = log_h + log_w + log_market; "
            "EXCLUDES utility u and -log_prior (opportunity density only)."),
    }

    html = build_html(inputs, t1, t23, t4, t5, t6, figures, prov)
    _HTML.parent.mkdir(parents=True, exist_ok=True)
    _HTML.write_text(html, encoding="utf-8")

    _PROV.parent.mkdir(parents=True, exist_ok=True)
    _PROV.write_text(json.dumps(prov, indent=2, default=float), encoding="utf-8")

    print(f"[stage5a] n_hh={args.n_hh} groups={[d.n_groups for d in data_by_group.values()]}")
    print(f"[stage5a] wrote parquet {_OUT_PARQUET} ({len(parquet_df)} rows)")
    print(f"[stage5a] wrote HTML {_HTML}")
    print(f"[stage5a] wrote provenance {_PROV}")
    print(f"[stage5a] absent variables: {t4['absent_variables']}")


if __name__ == "__main__":
    main()
