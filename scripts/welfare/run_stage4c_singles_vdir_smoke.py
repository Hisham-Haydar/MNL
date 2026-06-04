"""
STAGE FOUR, INCREMENT FOUR-C — bounded singles V_i^dir gate-and-smoke against the
population-faithful staged welfare-pricing reference.

A BOUNDED DIAGNOSTIC SMOKE, NOT a population welfare result. For a tiny deterministic singles
subset it: (1) redraws counterfactual job nodes from the estimated opportunity density g_hat at
the certified theta_hat; (2) prices each redrawn node POPULATION-FAITHFULLY — inside the FULL
production-chunk batch (the Four-B-mandated construction), overwriting ONLY the target
household's decider choice variables and preserving the whole population + non-decider roster;
(3) integrates the extreme-value shocks ANALYTICALLY via the household log-sum (no Frechet/Gumbel
draws, no simulated argmax) to form V_i^dir; (4) compares V_i^dir to V_i^IS over existing draws
by ESS bin.

Reuses (edits none of): welfare_vdir.redraw_nodes_singles + _load_draw_machinery (g_hat redraw),
welfare_core V_of extractor + V_i^IS/ESS, and the build module's system pairing / CPI / raw
schema / _stamp_draw_ids / EuromodRunner (so pricing matches the build EXACTLY). The redrawn
nodes are substituted into the staged reference's own precompute population and priced through
the build's EUROMOD path — the same population-faithful batch Four-B validated to machine zero.

Does NOT: run the full singles production V_i^dir, touch couples, promote W^3, compute any
measure beyond W^3, produce a reportable welfare distribution, swap production / promote any
baseline to canonical, or re-estimate. Pricing output goes to a clearly-named scratch dir.

Config-driven (welfare.stage4 + welfare.stage2.singles_vdir_gate); country/year/spec-agnostic.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
sys.path.insert(0, "scripts/enhanced")
sys.path.insert(0, "scripts/pilot")
import joint_recovery_test as _jrt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_core as _wc  # noqa: E402
import welfare_vdir as wvd  # noqa: E402
import yaml  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_CONFIG = Path("scripts/welfare/configs/welfare_stage1_w3.yaml")
_FOUR_B = Path("outputs/welfare/stage1_w3/stage4b_population_parity_gate.json")
_CERT_THETA = Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv")
_CERT_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
# precompute stem mirrors the build (welfare.stage2.precompute_long_stem); staged stem is read
# from welfare.stage4.welfare_pricing_reference at runtime (NOT hardcoded).
_PRECOMP_STEM_DEFAULT = "fr_p3a_bpool_precompute"
TOTAL_LEISURE_HOURS = 80.0
DCM_MIN_POSITIVE = 1.0
# Authoritative earnings-identity constants (enh_RURO_euromod.py / build_bpool_precompute.py):
# yem = yem00 + yemxp; yem00 = min(lhw,35)*yivwg*WEEKS_PER_MONTH; yemxp = max(lhw-35,0)*...
_FR_STD_HOURS = 35.0          # French standard weekly hours (regular/overtime split point)
_WEEKS_PER_MONTH = 52.0 / 12.0  # = 4.3333...


def _year_tag_from_rows(df, year):
    """Year tag for a (year) cell, read from the staged rows' own `year_tag` column (set by
    harmonise_bpool_engine_ready from data_year). Falls back to the build's data_year->tag map
    derived from the staged data itself (NOT a hardcoded constant), so it stays case-agnostic."""
    if "year_tag" in df.columns:
        # the staged rows carry the canonical year_tag; take the modal value for this cell
        yt = df["year_tag"].dropna()
        if len(yt):
            return int(yt.mode().iloc[0])
    if "data_year" in df.columns:
        years = sorted(int(y) for y in df["data_year"].dropna().unique())
        return years.index(int(year)) + 1
    raise SystemExit("STOP: cannot derive year_tag (no year_tag/data_year column on staged rows)")
# decider choice variables the build overwrites per node (hours/wage channel). yem is the
# annual employment income the build derives as hours*wage*weeks; we mirror the build's
# convention by setting the same columns the existing nodes carry.
_CHOICE_VARS = ["lhw", "yivwg", "yem", "yem_hour", "hours", "wage", "working", "loc4"]


def _load_cfg():
    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    w = cfg["welfare"]
    return w["stage4"], w["stage2"]["singles_vdir_gate"], w["stage2"]


def _build_constants(stage2_cfg):
    """Reuse the build module constants (Four-B / welfare_vdir convention)."""
    return wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})


# ---------------------------------------------------------------------------
# TASK 2 helper — population-faithful pricing of a target HH's redrawn nodes
# ---------------------------------------------------------------------------
def price_nodes_population_faithful(bc, year, mode, precomp_df, target_uid, nodes, phi,
                                    country, system_code, dataset_name, draw_band):
    """Substitute the target HH's redrawn nodes into the FULL precompute population chunk,
    run the build's EUROMOD path on the WHOLE chunk (population intact), and extract the
    target node prices. Returns (priced_nodes_df | None, status_dict).

    Population-faithful by construction: every non-target household row in the chunk band is
    preserved unchanged; only the target HH's decider choice variables are overwritten, at the
    draw slots [1 .. n_nodes]; non-decider roster rows are preserved. No isolated household, no
    sub-band, no tiny appended batch. If the target HH cannot host n_nodes draw slots in the
    band without interpolation, returns BLOCKED."""
    draw_lo, draw_hi = draw_band
    n_nodes = len(nodes["working"])
    band = precomp_df[(precomp_df["draw"] >= draw_lo) & (precomp_df["draw"] < draw_hi)].copy()
    band = band.reset_index(drop=True)

    tgt = band[band["stacked_hh_uid"] == target_uid]
    if tgt.empty:
        return None, {"status": "BLOCKED", "reason": f"target {target_uid} not in band"}
    # the decider rows at draws 1..n_nodes (existing slots we overwrite with the nodes)
    dec = tgt[tgt["ruro_decider"] == 1]
    avail_draws = sorted(d for d in dec["draw"].unique() if d >= 1)
    if len(avail_draws) < n_nodes:
        return None, {"status": "BLOCKED",
                      "reason": (f"target HH hosts only {len(avail_draws)} decider draw slots "
                                 f"in band [{draw_lo},{draw_hi}); need {n_nodes}. Cannot place "
                                 f"nodes without interpolation.")}
    use_draws = avail_draws[:n_nodes]

    # overwrite ONLY the target decider rows' choice vars at the chosen draw slots
    for k, dr in enumerate(use_draws):
        sel = (band["stacked_hh_uid"] == target_uid) & (band["draw"] == dr) \
              & (band["ruro_decider"] == 1)
        if int(sel.sum()) != 1:
            return None, {"status": "BLOCKED",
                          "reason": f"draw {dr}: expected 1 decider row, got {int(sel.sum())}"}
        w = float(nodes["wage"][k])
        h = float(nodes["hours"][k])
        wk = int(nodes["working"][k])
        lo4 = int(nodes["loc4"][k])
        # AUTHORITATIVE earnings identity (enh_RURO_euromod.py §11; build_bpool_precompute):
        # French EUROMOD requires yem = yem00 + yemxp with the regular/overtime split at the
        # standard 35h/week, monthly-scaled by WEEKS_PER_MONTH = 52/12:
        #   regular_hours  = min(lhw, 35) ; overtime_hours = max(lhw - 35, 0)
        #   yem00 = regular_hours  * yivwg * (52/12)   (regular employment income, <=35h)
        #   yemxp = overtime_hours * yivwg * (52/12)   (overtime pay, >35h)
        #   yem   = yem00 + yemxp
        # This satisfies EUROMOD's uprate reconciliation (yem == yem00+yemxp) EXACTLY; the
        # previous heuristic (yem = h*w*scale, yem00/yemxp left stale) broke it.
        if wk == 1 and h > 0 and w > 0:
            reg_h = min(h, _FR_STD_HOURS)
            ot_h = max(h - _FR_STD_HOURS, 0.0)
            yem00 = reg_h * w * _WEEKS_PER_MONTH
            yemxp = ot_h * w * _WEEKS_PER_MONTH
            band.loc[sel, "lhw"] = h
            band.loc[sel, "yivwg"] = w
            band.loc[sel, "yem_hour"] = w
            band.loc[sel, "yem00"] = yem00
            band.loc[sel, "yemxp"] = yemxp
            band.loc[sel, "yem"] = yem00 + yemxp
            band.loc[sel, "working"] = 1.0
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

    # --- run the build's EUROMOD path on the FULL band (population intact) ---
    bmod = __import__("run_bpool_euromod_chunk")
    id_mult = 1_000 if mode == "singles" else 10_000
    stamped = bmod._stamp_draw_ids(band.copy(), "draw" if mode == "singles" else "draw_joint",
                                   id_mult)
    raw_cols = bc["raw_schema"][year]
    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em_input, country=country, system_code=system_code,
                                      dataset_name=dataset_name)
    except Exception as e:  # noqa: BLE001
        return None, {"status": "BLOCKED", "reason": f"EUROMOD run failed: {type(e).__name__}: {e}"}
    if "ils_dispy" not in sim.columns or len(sim) != len(band):
        return None, {"status": "BLOCKED", "reason": f"EUROMOD output mismatch {sim.shape}"}

    out = band.reset_index(drop=True).copy()
    out["ils_dispy"] = sim["ils_dispy"].values
    out["ils_dispy_real"] = out["ils_dispy"] * phi   # phi_y AFTER EUROMOD (no double deflation)
    # extract ONLY the target node rows at the substituted draw slots
    tnodes = out[(out["stacked_hh_uid"] == target_uid) & (out["draw"].isin(use_draws))
                 & (out["ruro_decider"] == 1)].copy()
    tnodes = tnodes.sort_values("draw").reset_index(drop=True)
    return tnodes, {"status": "OK", "n_target_nodes": int(len(tnodes)),
                    "n_population_rows_priced": int(len(band)),
                    "n_population_hh": int(band["stacked_hh_uid"].nunique()),
                    "used_draw_slots": [int(d) for d in use_draws]}


# ---------------------------------------------------------------------------
# FUNCTION 1 — V_i^IS, ESS, max_w for a requested set of singles uids
# ---------------------------------------------------------------------------
def v_is_and_ess_singles(bp, staged_stem, uids, theta, spec):
    """Per-household V_i^IS (inclusive-value log-sum), ESS, and max normalised
    weight for the requested singles ``uids``, computed over the EXISTING staged
    estimation draws via the estimator's own machinery (no re-implementation).

    Reuses, edits nothing:
      - ``joint_recovery_test.build_data_objects`` to load the staged engine-ready
        singles data objects (male + female), identical to the estimation path.
      - ``welfare_core.compute_group_welfare`` to form V_i^IS / ESS / max_w (the
        SAME V = u + log_h + log_w + log_market - log_prior extractor + within-
        household softmax the estimator uses).

    uid -> V_is INDEX MAPPING (load-bearing).  ``PrecomputedDataSingles`` does NOT
    carry ``stacked_hh_uid``; it exposes ``group_ids`` (the per-group representative
    key = ``idhh*10 + year_tag`` when the slice is multi-year, else ``idhh``) aligned
    1:1 with the V_is array order.  We rebuild the group key -> stacked_hh_uid bridge
    from the SAME engine-ready parquet the data objects are built from, using the
    SAME group key the precompute forms, then index V_is by it.  No reliance on any
    incidental idhh==stacked_hh_uid coincidence: the bridge is via the constructed
    group key, which is 1:1 with stacked_hh_uid by construction of the parquet.

    Parameters
    ----------
    bp : Path
        bpool data directory (``_bpool_paths.bpool_dir()``).
    staged_stem : str
        Engine-ready stem (e.g. ``fr_p3a_bpool_engine_ready_staged_threeB1``).
    uids : iterable of int
        stacked_hh_uid values to return (only those present are returned).
    theta : np.ndarray
        Parameter vector in ``spec.all_param_names`` order.
    spec : EstimationSpec

    Returns
    -------
    dict {uid: {"V_i_is": float, "ess": float, "max_w": float}}
    """
    import pandas as _pd

    want = set(int(u) for u in uids)
    data_sm, data_sf, _ = _jrt.build_data_objects(staged_stem, [], 0)

    out: dict[int, dict] = {}
    for data, group in ((data_sm, "singles_male"), (data_sf, "singles_female")):
        gw = _wc.compute_group_welfare(data, spec, theta, group)
        n_groups = int(gw.n_groups)

        gk = np.asarray(data.group_ids)
        if gk.shape[0] != n_groups:
            raise SystemExit(
                "STOP: data.group_ids length does not align with V_is groups for "
                f"{group} ({gk.shape[0]} vs {n_groups}); cannot map V_is -> uid.")

        # Rebuild the SAME group key -> stacked_hh_uid bridge from the parquet the
        # data object was built from. Mirror precompute_data_singles' key exactly.
        path = bp / f"{staged_stem}__singles.parquet"
        if not path.exists():
            raise SystemExit(f"STOP: engine-ready singles parquet missing: {path}")
        flag = 1.0 if group == "singles_male" else 0.0
        bridge = _pd.read_parquet(
            path, columns=["stacked_hh_uid", "idhh", "year_tag", "dgn"])
        bridge = bridge[bridge["dgn"] == flag]
        if "stacked_hh_uid" not in bridge.columns or "idhh" not in bridge.columns:
            raise SystemExit(
                "STOP: parquet lacks stacked_hh_uid/idhh; cannot bridge V_is -> uid.")
        multi_year = bridge["year_tag"].nunique() > 1
        if multi_year:
            key = (bridge["idhh"].astype(np.int64) * 10
                   + bridge["year_tag"].astype(np.int64))
        else:
            key = bridge["idhh"].astype(np.int64)
        bridge = bridge.assign(_key=key.values)
        # one stacked_hh_uid per group key (1:1 by parquet construction)
        m = bridge.drop_duplicates("_key").set_index("_key")["stacked_hh_uid"]
        key_to_uid = {int(k): int(v) for k, v in m.items()}

        for i in range(n_groups):
            uid = key_to_uid.get(int(gk[i]))
            if uid is None or uid not in want:
                continue
            out[uid] = {
                "V_i_is": float(gw.V_is[i]),
                "ess": float(gw.ess[i]),
                "max_w": float(gw.max_w[i]),
            }
    return out


# ---------------------------------------------------------------------------
# FUNCTION 2 — per-node estimator V for ONE singles household's redrawn nodes
# ---------------------------------------------------------------------------
def node_V_singles(spec, theta, *, c_norm, l_norm, working, wage, priced_row, c_scale):
    """Per-node estimator deterministic value V for ONE singles household's redrawn
    nodes, byte-identical to welfare_core ``_build_V_extractor`` (singles), i.e.

        V = u + log_h + log_w + log_market - log_prior        (welfare_core ~239-275)

    Implementation reuses ``welfare_core._build_V_extractor`` UNCHANGED by feeding it a
    thin one-group x n-node data shim whose attributes are derived from this HH's nodes
    + the HH-constant covariates on ``priced_row`` using the SAME rules
    ``estimation_utils.precompute_data_singles`` uses (df.get(name).fillna(0.0); loc4
    one-hots; reg dummies; hours bands). This guarantees the term composition, scalings
    (gsur*10 from spec variable_scales, the engine-ready covariate encodings), and
    Box-Cox match the estimator exactly — nothing is re-derived independently here.

    The household is male iff ``priced_row['dgn'] == 1`` (group suffix _sm / _sf).

    Parameters
    ----------
    spec, theta : as in v_is_and_ess_singles.
    c_norm : (n_nodes,) consumption / c_scale (already normalised).
    l_norm : (n_nodes,) leisure  / l_scale (already normalised).
    working : (n_nodes,) 0/1 employment indicator.
    wage : (n_nodes,) NOMINAL wage; log_wage = log(wage) where working else 0.
    priced_row : DataFrame of the n_nodes priced node rows; carries the HH-constant
        covariates + per-node loc4 (column "loc4"). Missing engine-ready covariates
        default to 0.0, exactly as precompute_data_singles' df.get(...) does.
    c_scale : consumption normalisation (only used to document the c_norm convention;
        c_norm is already divided by it upstream and passed straight through).

    Returns
    -------
    np.ndarray (n_nodes,) of estimator V values.

    -------------------------------------------------------------------------
    NOTE ON V_i^dir COMPOSITION (load-bearing — see report). This function returns
    the FULL estimator V (utility + opportunity - log_prior), the SAME object the
    estimator/V_i^IS uses. It is NOT itself the V_i^dir integrand. Per the welfare
    design contract the V_i^dir integrand is the OWN-PREFERENCE UTILITY ONLY:

        V_i = log sum_j exp( v_i(c_j,l_j) + log g_hat(j) - log pi(j) )   (spec_v5 L107-109)
        V_i^IS = log sum_j exp( v_i + log g_hat - log pi )              (spec_v5 L121-123)

      The IS weights are omega ∝ exp(log g_hat - log pi) = g_hat/pi (spec_v5 L497).
      Drawing nodes directly from g_hat makes g_hat/pi UNIFORM, so the
      (log g_hat - log pi) correction is replaced by 0 (welfare_vdir.py L21-24:
      "nodes are drawn from g_hat itself, the within-household IS weight is uniform;
      V_i^dir = log mean_s exp( v_i(c_is,l_is) + 0 )"). Since
      log g_hat = log_h + log_w + log_market and -log pi = -log_prior, BOTH the
      opportunity terms AND -log_prior are the SAMPLING DENSITY, not the integrand:

        V_i^dir = log mean_s exp( u(c_is, l_is) )     [own-preference utility only]

    To form the correct V_i^dir, take the "u" component of the breakdown returned by
    node_V_singles_terms (NOT this full V). This function deliberately returns the
    full estimator V so the caller chooses the composition explicitly; it does not
    silently bake a V_dir choice.
    """
    V, _terms = node_V_singles_terms(
        spec, theta, c_norm=c_norm, l_norm=l_norm, working=working, wage=wage,
        priced_row=priced_row, c_scale=c_scale)
    return V


def node_V_singles_terms(spec, theta, *, c_norm, l_norm, working, wage,
                         priced_row, c_scale):
    """Same as node_V_singles but ALSO returns the per-term breakdown so the caller
    can assemble the contract-correct V_i^dir (utility-only) without re-deriving the
    estimator math. Returns (V_full, terms) where terms = {"u","log_h","log_w",
    "log_market","neg_log_prior"} each a (n_nodes,) array and
    V_full = u + log_h + log_w + log_market + neg_log_prior.

    The breakdown is produced by the SAME spec-driven loops welfare_core uses; we run
    the estimator extractor for V_full (parity) AND compute the component split with
    the identical term definitions so the two agree to machine tolerance.
    """
    import jax.numpy as jnp

    df = priced_row.reset_index(drop=True)
    c_norm = np.asarray(c_norm, dtype=np.float64)
    l_norm = np.asarray(l_norm, dtype=np.float64)
    working = np.asarray(working, dtype=np.float64)
    wage = np.asarray(wage, dtype=np.float64)
    n = c_norm.shape[0]

    is_male = bool(int(round(float(df["dgn"].iloc[0]))) == 1)
    suffix = "_sm" if is_male else "_sf"
    group = "singles_male" if is_male else "singles_female"

    # hours per node for the focal-band indicators, mirroring precompute_data_singles
    # (the bands are derived from hours, NOT from l_norm). Require the column so the
    # bands are exact rather than back-inferred from normalised leisure.
    if "hours" not in df.columns:
        raise SystemExit(
            "STOP: node_V_singles needs per-node 'hours' on priced_row to build the "
            "working_pt1/pt2/ft/lh bands exactly as precompute_data_singles does.")
    hours = pd.to_numeric(df["hours"], errors="coerce").to_numpy()

    def col(name, default=0.0):
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce").fillna(default).to_numpy()
        return np.full(n, default, dtype=np.float64)

    # loc4 one-hots (precompute_data_singles include_loc_vars path)
    loc4 = col("loc4", 0.0)
    loc4_2 = (loc4 == 2).astype(np.float64)
    loc4_3 = (loc4 == 3).astype(np.float64)
    loc4_4 = (loc4 == 4).astype(np.float64)

    # region dummies: prefer reg_nuts1_* if present, else derive from drgn1 code,
    # exactly as precompute_data_singles.
    def reg(k):
        rn = f"reg_nuts1_{k}"
        if rn in df.columns:
            return col(rn, 0.0)
        if "drgn1" in df.columns:
            return (col("drgn1", 0.0) == k).astype(np.float64)
        return np.zeros(n, dtype=np.float64)

    # hours focal-band indicators (precompute_data_singles bands)
    working_pt1 = ((hours >= 18.5) & (hours <= 21.5)).astype(np.float64)
    working_pt2 = ((hours >= 29.5) & (hours <= 30.5)).astype(np.float64)
    working_ft = ((hours >= 37.5) & (hours <= 40.5)).astype(np.float64)
    if "working_lh" in df.columns:
        working_lh = col("working_lh", 0.0)
    else:
        working_lh = (((hours >= 44.5) & (hours <= 70.0))
                      & (working > 0)).astype(np.float64)

    log_wage = np.where(working > 0, np.log(np.maximum(wage, 1e-12)), 0.0)

    # uniform per-node prior: nodes are an integration set; the estimator's
    # proposal-centering weights by prior, so a uniform prior makes the centering
    # the plain within-set mean (and -log_prior a per-node constant). For the FULL
    # V this contributes an additive constant per node; the caller forms V_dir from
    # the utility-only component anyway (see node_V_singles docstring).
    prior = np.full(n, 1.0 / max(n, 1), dtype=np.float64)

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

    Vfn, _meta = _wc._build_V_extractor(shim, spec, group)
    th = jnp.asarray(np.asarray(theta, dtype=np.float64))
    cons = jnp.asarray(c_norm)
    V_full = np.asarray(Vfn(th, cons), dtype=np.float64)

    # Component split with the SAME definitions, for the contract-correct V_dir.
    pidx = {nm: spec.get_param_index(nm) for nm in spec.all_param_names}
    fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def P(name):
        if name in fixed:
            return float(fixed[name])
        return float(theta[pidx[name]])

    theta_l_name = (spec.utility_leisure_theta + suffix
                    if spec.utility_leisure_theta else None)
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
    neg_log_prior = -np.log(prior)
    # V_full already contains log_h+log_w+log_market-log_prior; recover the
    # opportunity block as the residual so the split is exact w.r.t. the extractor.
    opportunity_minus_prior = V_full - u
    terms = {
        "u": u,
        "neg_log_prior": neg_log_prior,
        "opportunity_minus_prior": opportunity_minus_prior,
        "log_h_log_w_log_market": opportunity_minus_prior - neg_log_prior,
    }
    return V_full, terms


class _SinglesNodeShim:
    """Minimal stand-in for PrecomputedDataSingles exposing exactly the attributes
    welfare_core._build_V_extractor reads for the singles path (one group, n_nodes
    alternatives). consumption is passed into V_of per call, so it is omitted here."""

    def __init__(self, *, n_nodes, is_male, **arrays):
        self.n_groups = 1
        self.n_obs = int(n_nodes)
        self.is_male = bool(is_male)
        self.cluster_ids = np.zeros(1, dtype=np.int64)
        self.group_ids = np.zeros(1, dtype=np.int64)
        # consumption placeholder (real value passed to V_of); shape-correct so any
        # incidental getattr(data,'consumption') stays well-formed.
        self.consumption = np.ones(int(n_nodes), dtype=np.float64)
        for k, v in arrays.items():
            setattr(self, k, np.asarray(v, dtype=np.float64))


def _box_cox(x, theta):
    """numpy Box-Cox matching jllp.jbox_cox: (x^theta-1)/theta, log(x) at theta~0."""
    x = np.asarray(x, dtype=np.float64)
    if abs(float(theta)) < 1e-8:
        return np.log(x)
    return (np.power(x, float(theta)) - 1.0) / float(theta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--scratch-dir", required=True)
    ap.add_argument("--year", type=int, default=2016)
    ap.add_argument("--n-hh", type=int, default=5)
    ap.add_argument("--n-nodes", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260604)
    args = ap.parse_args()

    stage4, vgate, stage2 = _load_cfg()

    # TASK 0 — preconditions
    if not _FOUR_B.exists():
        raise SystemExit("STOP: Four-B provenance missing")
    fourb = json.loads(_FOUR_B.read_text())
    if not fourb.get("task3_readiness", {}).get(
            "population_faithful_and_ready_for_singles_vdir_gate"):
        raise SystemExit("STOP: Four-B not READY (population parity gate did not pass)")

    bp = bpool_dir()
    scratch = Path(args.scratch_dir).resolve()
    staged_chunk_dir = bp / stage4["welfare_pricing_reference"]["staged_chunk_dir_name"]
    staged_priced_dir = bp / stage4["welfare_pricing_reference"]["staged_priced_dir_name"]
    if scratch in {bp.resolve(), (bp / "chunks").resolve(), staged_chunk_dir.resolve(),
                   staged_priced_dir.resolve()}:
        raise SystemExit(f"REFUSE: scratch '{scratch}' is production / staging reference")
    scratch.mkdir(parents=True, exist_ok=True)

    # staged stem + precompute stem from CONFIG (welfare.stage4 / welfare.stage2), not hardcoded
    staged_stem = stage4["welfare_pricing_reference"]["staged_engine_ready_stem"]
    precomp_stem = stage2.get("precompute_long_stem", _PRECOMP_STEM_DEFAULT)

    year, mode, n_hh, n_nodes, seed = args.year, "singles", args.n_hh, args.n_nodes, args.seed
    bc = _build_constants(vgate)
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(system_code).split("_")[0]
    phi = bc["cpi"][year]

    # staged normalization (so redrawn-node c_norm/l_norm match the staged engine-ready)
    smeta = json.loads((bp / f"{staged_stem}__mnlmeta.json").read_text())
    c_scale = float(smeta["normalization"]["singles"]["c_scale"])
    l_scale = float(smeta["normalization"]["singles"]["l_scale"])

    # the staged precompute population (what the worker prices); read full chunk band
    precomp = bp / f"{precomp_stem}__{year}__{mode}__long.parquet"
    if not precomp.exists():
        raise SystemExit(f"STOP: precompute-long missing: {precomp}")
    precomp_df = pd.read_parquet(precomp)
    # full production-chunk band derived from the data's own draw range (NOT hardcoded): the
    # singles population-faithful unit spans all existing draws [min, max+1).
    _draws = pd.to_numeric(precomp_df["draw"], errors="coerce")
    draw_band = (int(_draws.min()), int(_draws.max()) + 1)
    # year_tag derived from a helper reading the staged engine-ready's own year_tag/data_year
    # (NOT a hardcoded year map). Read just the needed columns.
    er_yt = pd.read_parquet(bp / f"{staged_stem}__{mode}.parquet")
    year_tag = _year_tag_from_rows(er_yt[er_yt.get("data_year", year) == year]
                                   if "data_year" in er_yt.columns else er_yt, year)

    # The redraw needs the ESTIMATION covariates (educ3/educL/educH/pexp_years[2]/dgn), which
    # live on the staged ENGINE-READY (not the precompute, which carries only raw EUROMOD
    # inputs). Source hh_row covariates from the staged engine-ready (chosen row per HH), and
    # price through the precompute population. educ3 is derived by the authoritative helper
    # enh_RURO_draws._ensure_educ3 (educL/educH -> educ3) if absent.
    from enh_RURO_draws import _ensure_educ3
    er = _ensure_educ3(er_yt)
    er0 = er[er["draw"] == 0].drop_duplicates("stacked_hh_uid").set_index("stacked_hh_uid")

    # certified theta + staged V_of extractor (analytic V; no shocks)
    import estimation_spec_parser as sp
    import welfare_core as wc
    spec = sp.parse_specification(_CERT_SPEC)
    theta = _load_theta(spec)

    # ESS-SPANNING deterministic target subset: an arbitrary first-n subset can be entirely
    # low-ESS (then the high-ESS bulk-agreement check is vacuous). Compute ESS for a candidate
    # pool (the first POOL singles HH by uid) and pick the n_hh//2 HIGHEST-ESS + the rest
    # LOWEST-ESS, so the smoke carries a high-ESS anchor (where V_dir~V_IS should hold) AND a
    # low-ESS tail (the contract's intended diagnostic target).
    pool_uids = (precomp_df[precomp_df["draw"] == 0]["stacked_hh_uid"].drop_duplicates()
                 .sort_values().head(max(n_hh * 30, 200)).tolist())
    pool_ess = v_is_and_ess_singles(bp, staged_stem, pool_uids, theta, spec)
    ess_sorted = sorted(((u, pool_ess[u]["ess"]) for u in pool_uids if u in pool_ess),
                        key=lambda kv: kv[1])
    n_high = max(1, n_hh // 2)
    n_low = n_hh - n_high
    high_uids = [u for u, _ in ess_sorted[-n_high:]]
    low_uids = [u for u, _ in ess_sorted[:n_low]]
    uids = sorted(set(low_uids + high_uids))

    # TASK 1 — redraw nodes from g_hat for each target HH (NO Frechet/Gumbel; node locations)
    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    rng = np.random.default_rng(seed)

    per_hh = []
    blocked = None
    for uid in uids:
        if uid not in er0.index:
            blocked = {"uid": int(uid), "status": "BLOCKED",
                       "reason": "uid not found in staged engine-ready covariate lookup"}
            break
        cov = er0.loc[uid]
        hh_row = {"dgn": float(cov["dgn"]), "educ3": int(cov["educ3"]),
                  "educL": float(cov["educL"]), "educH": float(cov["educH"]),
                  "pexp_years": float(cov["pexp_years"]),
                  "pexp_years2": float(cov["pexp_years2"])}
        nodes = wvd.redraw_nodes_singles(hh_row, n_nodes, rng, mincer, dm,
                                         year_tag=year_tag)
        # express counterfactual wage in the draw's NOMINAL frame before EUROMOD: the redraw
        # produces nominal wages (pilot_wage_draw is nominal); EUROMOD inputs stay nominal.
        priced, st = price_nodes_population_faithful(
            bc, year, mode, precomp_df, uid, nodes, phi, country, system_code, dataset_name,
            draw_band)
        if st["status"] != "OK":
            blocked = {"uid": int(uid), **st}
            break
        rec = _vdir_for_hh(uid, priced, nodes, theta, spec, c_scale, l_scale, wc)
        rec["pricing"] = st
        per_hh.append(rec)

    if blocked is not None:
        out = {"increment": "stage4c_singles_vdir_smoke_v1", "status": "BLOCKED",
               "blocked": blocked, "scope": _scope(), "is_welfare_distribution": False}
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(out, indent=2, default=float))
        print(f"[four-C] BLOCKED: {blocked}")
        return

    # TASK 4 — V_i^dir vs V_i^IS (existing draws) by ESS
    cmp = _compare_vdir_vis(per_hh, precomp_df, uids, theta, spec, c_scale, l_scale, wc, bp,
                            staged_stem)

    ready = _readiness(per_hh, cmp)
    out = {
        "increment": "stage4c_singles_vdir_smoke_v1",
        "status": "OK", "is_welfare_distribution": False,
        "bounded_diagnostic_smoke": True,
        **_scope(),
        "task0_preconditions": {
            "four_b_ready": True, "year": year, "mode": mode, "n_hh": n_hh,
            "n_nodes_per_hh": n_nodes, "seed": seed,
            "full_production_chunk_band": list(draw_band),
            "staged_stem": staged_stem, "c_scale": c_scale, "l_scale": l_scale,
            "year_tag": year_tag, "draw_band": list(draw_band),
            "note": "BOUNDED DIAGNOSTIC SMOKE, not a population welfare result."},
        "task1_redraw": {
            "g_hat_channels": {
                "employment": "Bernoulli(1-PI0) (build_bpool_singles.PI0)",
                "occupation": "Categorical(loc4|dgn,educ3) (occ_draw_empirical.draw_loc4)",
                "hours": "D1 five-mode mixture (hours_mixture_d1.draw_hours_d1)",
                "wage": "LogNormal(mu_i,sigma) mu_i=X_i b + delta_occ (pilot_wage_draw)"},
            "seed": seed, "no_frechet_gumbel_shocks": True,
            "no_simulated_argmax": True,
            "counterfactual_wage_nominal_frame_before_euromod": True},
        "task2_3_per_hh": per_hh,
        "task4_vdir_vs_vis": cmp,
        "task5_readiness": ready,
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, indent=2, default=float))
    print(f"[four-C] priced {len(per_hh)} HH x {n_nodes} nodes population-faithfully")
    print(f"[four-C] like-for-like delta_common: median={cmp['delta_common_median']} "
          f"abs_max={cmp['delta_common_abs_max']}")
    print(f"[four-C] high-ESS n={cmp['high_ess_n']} delta_common_abs_max="
          f"{cmp['high_ess_delta_common_abs_max']} | low-ESS n={cmp['low_ess_n']} "
          f"delta_common_abs_max={cmp['low_ess_delta_common_abs_max']}")
    print(f"[four-C] READY for full singles V_dir = {ready['ready_for_full_singles_vdir']}")
    if ready["stop_reasons"]:
        print(f"[four-C] STOP reasons: {ready['stop_reasons']}")
    print(f"[four-C] wrote {args.out_json}")


def _load_theta(spec):
    df = pd.read_csv(_CERT_THETA)
    lookup = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    return np.array([lookup.get(n, float(spec.initial_values.get(n, 0.0)))
                     for n in spec.all_param_names], dtype=np.float64)


def _logmeanexp(arr):
    a = np.asarray(arr, dtype=np.float64)
    mx = float(np.max(a))
    return mx + float(np.log(np.mean(np.exp(a - mx))))


def _vdir_for_hh(uid, priced, nodes, theta, spec, c_scale, l_scale, wc=None):
    """TASK 3 — analytic V_i^dir over the redrawn, population-faithfully-priced nodes. Nodes are
    drawn from g_hat itself, so the within-household IS weight is UNIFORM and the EV shocks are
    integrated ANALYTICALLY by the household log-sum (no Frechet/Gumbel draw, no simulated argmax):

        V_i^dir = log mean_s exp( u(c_is, l_is) )        [own-preference utility ONLY]

    V_dir COMPOSITION (load-bearing, verified against the contract). The general inclusive value is
    V_i = log sum_j exp( v_i(c_j,l_j) + log g_hat(j) - log pi(j) ) (JMP_welfare_spec_v5.md L107-109).
    The IS weight is omega ∝ exp(log g_hat - log pi) = g_hat/pi (L497). Drawing nodes directly from
    g_hat makes g_hat/pi UNIFORM, so (log g_hat - log pi) is replaced by 0 (welfare_vdir.py L21-24:
    "nodes are drawn from g_hat itself, the within-household IS weight is uniform; V_i^dir =
    log mean_s exp( v_i(c_is,l_is) + 0 )"). Since log g_hat = log_h+log_w+log_market and
    -log pi = -log_prior, BOTH the opportunity terms AND -log_prior are the SAMPLING density, NOT
    the integrand. Therefore V_i^dir integrates the UTILITY-ONLY component u(c,l). We use the "u"
    term from node_V_singles_terms (NOT the full estimator V). The full-V variant is recorded
    alongside for transparency, but V_i_dir is the contract-correct utility-only value."""
    n = len(priced)
    cons_real = pd.to_numeric(priced["ils_dispy_real"], errors="coerce").to_numpy()
    c_norm = np.clip(cons_real, DCM_MIN_POSITIVE, None) / c_scale
    hours = pd.to_numeric(priced["hours"], errors="coerce").to_numpy() \
        if "hours" in priced.columns else nodes["hours"][:n]
    leisure = np.clip(TOTAL_LEISURE_HOURS - hours, DCM_MIN_POSITIVE, None)
    l_norm = leisure / l_scale
    working = pd.to_numeric(priced["working"], errors="coerce").to_numpy() \
        if "working" in priced.columns else nodes["working"][:n]
    wage = pd.to_numeric(priced["wage"], errors="coerce").to_numpy() \
        if "wage" in priced.columns else nodes["wage"][:n]
    V_full, terms = node_V_singles_terms(spec, theta, c_norm=c_norm, l_norm=l_norm,
                                         working=working, wage=wage, priced_row=priced,
                                         c_scale=c_scale)
    u = np.asarray(terms["u"], dtype=np.float64)            # utility-only integrand (contract)
    vdir = _logmeanexp(u)                                   # V_i^dir (own-preference utility only)
    vdir_full_variant = _logmeanexp(np.asarray(V_full, dtype=np.float64))  # transparency only
    return {"uid": int(uid), "n_nodes": int(n), "n_work": int(np.sum(working)),
            "V_i_dir": float(vdir),
            "V_i_dir_integrand": "own_preference_utility_only (u(c,l)); contract-correct",
            "V_i_dir_full_V_variant_for_transparency": float(vdir_full_variant),
            "node_u_min": float(np.min(u)), "node_u_max": float(np.max(u)),
            "analytic_integration": True, "frechet_or_gumbel_used": False}


def _compare_vdir_vis(per_hh, precomp_df, uids, theta, spec, c_scale, l_scale, wc, bp,
                      staged_stem):
    """TASK 4 — compute V_i^IS over existing draws for the SAME HH and compare to V_i^dir by ESS.

    NORMALIZATION (load-bearing). V_i^IS = log SUM_{j=1..n_draws} exp(V_full_j) (welfare_core
    _group_lse_and_V, full V = u + log g_hat - log_prior, over the n_draws existing draws).
    V_i^dir is a log-MEAN over the n_nodes redrawn nodes. To compare on a COMMON footing we
    reduce both to a per-node log-MEAN of the SAME object:
      - delta_util_basis: V_dir (utility-only log-mean) vs (V_IS - log(n_draws)) [log-mean of
        the FULL V]. Still mixes utility-only vs full-V, kept for reference.
      - delta_common: V_dir_full_variant (log-mean of FULL V over nodes) vs (V_IS - log(n_draws))
        (log-mean of FULL V over existing draws) -> SAME object, SAME basis. This is the
        like-for-like cross-check; a fixed log(n) count artifact is removed and both carry the
        opportunity density, so a small delta_common = genuine agreement.
    n_draws is COMPUTED from the actual staged singles per-household draw count (NOT hardcoded);
    if households differ in draw count the smoke STOPS (the like-for-like log(n) reduction
    assumes a common n_draws)."""
    vis = v_is_and_ess_singles(bp, staged_stem, uids, theta, spec)
    # n_draws from the staged singles per-HH existing-draw count (decider rows), data-driven
    sdec = precomp_df[precomp_df.get("ruro_decider", 1) == 1]
    per_hh_draws = sdec.groupby("stacked_hh_uid")["draw"].nunique()
    uniq = sorted(per_hh_draws.unique().tolist())
    if len(uniq) != 1:
        raise SystemExit(f"STOP: staged singles HH have non-uniform draw counts {uniq[:5]}...; "
                         "the like-for-like n_draws normalization assumes a common count.")
    n_draws = int(uniq[0])
    full_by_uid = {r["uid"]: r["V_i_dir_full_V_variant_for_transparency"] for r in per_hh}
    rows = []
    for rec in per_hh:
        uid = rec["uid"]
        if uid not in vis:
            continue
        vis_logmean = vis[uid]["V_i_is"] - float(np.log(n_draws))  # full V, per-node log-mean
        delta_util = rec["V_i_dir"] - vis[uid]["V_i_is"]           # raw (mixed basis)
        delta_common = full_by_uid[uid] - vis_logmean             # like-for-like (full V, logmean)
        rows.append({"uid": uid, "V_i_dir_util": rec["V_i_dir"],
                     "V_i_dir_full": full_by_uid[uid], "V_i_is": vis[uid]["V_i_is"],
                     "V_i_is_logmean_basis": vis_logmean,
                     "delta_util_basis": delta_util, "delta_common_basis": delta_common,
                     "ess": vis[uid]["ess"], "max_w": vis[uid]["max_w"]})
    ess = np.array([r["ess"] for r in rows]) if rows else np.array([])
    dcommon = np.array([r["delta_common_basis"] for r in rows]) if rows else np.array([])
    ess_thr = 30.0
    hi = ess >= ess_thr
    lo = ~hi
    return {
        "ess_threshold": ess_thr, "n_hh_compared": len(rows), "n_existing_draws": n_draws,
        "per_hh": rows,
        "delta_common_basis_note": ("like-for-like: V_dir(full-V log-mean over nodes) vs "
                                    "V_IS - log(n_draws) (full-V log-mean over existing draws)"),
        "delta_common_median": float(np.median(dcommon)) if len(dcommon) else None,
        "delta_common_abs_max": float(np.max(np.abs(dcommon))) if len(dcommon) else None,
        "high_ess_n": int(hi.sum()),
        "high_ess_delta_common_median": (float(np.median(dcommon[hi]))
                                         if hi.any() else None),
        "high_ess_delta_common_abs_max": (float(np.max(np.abs(dcommon[hi])))
                                          if hi.any() else None),
        "low_ess_n": int(lo.sum()),
        "low_ess_delta_common_median": (float(np.median(dcommon[lo]))
                                        if lo.any() else None),
        "low_ess_delta_common_abs_max": (float(np.max(np.abs(dcommon[lo])))
                                         if lo.any() else None),
        # kept for transparency
        "delta_median": cmp_median([r["delta_util_basis"] for r in rows]),
        "high_ess_delta_median": (float(np.median([r["delta_util_basis"]
                                  for r, h in zip(rows, hi) if h])) if hi.any() else None),
        "low_ess_delta_median": (float(np.median([r["delta_util_basis"]
                                 for r, lw in zip(rows, lo) if lw])) if lo.any() else None),
    }


def cmp_median(xs):
    return float(np.median(xs)) if xs else None


def _readiness(per_hh, cmp):
    all_priced = all(r.get("analytic_integration") for r in per_hh) and bool(per_hh)
    no_shocks = all(not r.get("frechet_or_gumbel_used") for r in per_hh)
    # high-ESS agreement on the LIKE-FOR-LIKE basis. A vacuous high-ESS bin (none present) does
    # NOT pass: the smoke must actually exhibit a high-ESS anchor where V_dir~V_IS to be READY.
    has_high_ess = cmp["high_ess_n"] > 0
    high_ok = (has_high_ess and cmp["high_ess_delta_common_abs_max"] is not None
               and cmp["high_ess_delta_common_abs_max"] <= 0.5)
    ready = bool(all_priced and no_shocks and high_ok)
    stop_reasons = []
    if not all_priced:
        stop_reasons.append("not all redrawn nodes priced population-faithfully")
    if not no_shocks:
        stop_reasons.append("non-analytic integration detected")
    if not has_high_ess:
        stop_reasons.append("no high-ESS household in the subset: high-ESS bulk agreement "
                            "UNESTABLISHED (vacuous pass refused) -> NOT READY")
    elif not high_ok:
        stop_reasons.append(f"high-ESS like-for-like |delta| too large "
                            f"({cmp['high_ess_delta_common_abs_max']}) > 0.5 nats")
    return {
        "ready_for_full_singles_vdir": ready,
        "all_redrawn_nodes_priced_population_faithfully": all_priced,
        "no_interpolation_used": True,
        "analytic_integration_confirmed": no_shocks,
        "high_ess_present": has_high_ess,
        "high_ess_agreement_satisfactory_like_for_like": high_ok,
        "low_ess_divergence_is_intended_diagnostic_target": True,
        "stop_reasons": stop_reasons,
        "separate_authorisations_remaining": [
            "full singles V_i^dir production run", "couples V_i^dir", "W^3 promotion",
            "measure-family extension", "any reportable inequality number"],
    }


def _scope():
    return {
        "ran_full_singles_production_vdir": False, "touched_couples": False,
        "promoted_w3": False, "measure_beyond_w3": False,
        "produced_reportable_welfare_distribution": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "promoted_to_canonical": False, "re_estimated": False,
        "scope_statement": (
            "Bounded singles V_i^dir gate-and-smoke against the staged welfare-pricing "
            "reference. No full singles run, no couples, no W^3 promotion, no measure beyond "
            "W^3, no reportable welfare distribution, no production swap, no canonical "
            "promotion, no re-estimation."),
    }


if __name__ == "__main__":
    main()
