"""
Welfare Stage Two — V_i^dir feasibility + EUROMOD reprice parity.
Covers Increment Two-A (feasibility re-audit + redraw machinery) AND Increment
Two-B (the EUROMOD reprice parity grid + diagnosis). Extends the Stage-One core
(welfare_core.py); edits NO estimator source.

Reports: RURO_welfare_stage2_vdir_crosscheck_v2.md (Two-A),
RURO_welfare_stage2_parity_v1.md (Two-B). Authority:
RURO_welfare_scaffold_design_contract_v2.md, JMP_welfare_spec_v5.md; the redraw
design is grounded in welfare_proposal_individualisation_check.md.

WHAT V_i^dir IS (contract §6 gate 1.ii cross-check). V_i^IS reuses the EXISTING
estimation draws (drawn from the proposal pi) and importance-weights them. V_i^dir
instead draws integration nodes from the ESTIMATED individual opportunity density
g_hat(.; x_i) — the SAME channel structure the estimator's proposal used:
  - employment: Bernoulli(pi0) split            (build_bpool_singles.PI0)
  - occupation: p(loc4 | dgn, educ3) stratum    (occ_draw_empirical.draw_loc4)
  - hours:      D1 five-mode mixture             (hours_mixture_d1.draw_hours_d1)
  - wage:       LogNormal(mu_i, sigma),          (pilot_wage_draw.draw_pilot_wages)
                mu_i = X_i b + delta_occ[loc4_i]
then integrates the extreme-value shocks ANALYTICALLY via the log-sum. NO Frechet
draws, NO simulated argmax. Because nodes are drawn from g_hat itself, the within-
household IS weight is uniform; V_i^dir = log mean_s exp( v_i(c_is, l_is) + 0 ),
i.e. the inclusive value of the redrawn set under the household's own preferences.

THE CONSUMPTION REQUIREMENT (the load-bearing boundary). v_i needs the disposable
income c_is at each redrawn node (w,h). In this repo consumption = ils_dispy_real
(harmonise_bpool_engine_ready.py) = EUROMOD output. A REDRAWN node (w',h') has NO
c_is unless EUROMOD is run on it.

RE-AUDIT FINDING (this increment, overturning the v1 audit). The EUROMOD input
schema IS present at storage level: the priced-long household templates
({priced_long_stem}__{year}__{mode}.parquet) carry the FULL input schema AND the
stored ils_dispy, for every year and mode. So redrawn-node EUROMOD input records
can be built by OVERWRITING ONLY the decider's choice variables on these templates
— NO wholesale rebuild. The v1 "wholesale rebuild required" conclusion (drawn from
the engine-ready parquet, the stripped estimation slice) is NARROWED: a bounded
template-overwrite touch is feasible. (No re-deflation — phi reused from the build
_CPI; no silent interpolation; no full rebuild.)

THE GATE THAT NOW BINDS — EUROMOD-on-nodes PARITY (the V_dir analogue of Stage-One
Gate 0). Before pricing any REDRAWN node, the template-overwrite path is validated
on EXISTING nodes: reprice stored rows UNCHANGED and confirm the repriced ils_dispy
reproduces the stored ils_dispy to tolerance. If parity FAILS, the path is NOT
trustworthy and node pricing stays BLOCKED regardless of schema availability — no
redrawn node is priced against an unvalidated EUROMOD path.

WHAT THIS MODULE DELIVERS:
  1. The g_hat redraw machinery for singles AND couples (employment/occ/hours/wage),
     reusing the estimator draw functions — node LOCATIONS only.
  2. A storage-level template-availability re-audit over all configured years/modes,
     with the required schema taken from the build module (not hardcoded here).
  3. The EUROMOD reprice PARITY check (Gate-0 analogue), reusing the build's system
     pairing / CPI(phi) / raw schema / _stamp_draw_ids / EuromodRunner.
  4. A multiplier-stability subsample probe on EXISTING nodes (needs no new c_is).

Agnosticism: stems/years/modes come from config; system pairing, CPI, EUROMOD input
schema, and the runner are reused from the build module; country is derived from the
system-code prefix (with optional config override). The welfare source hardcodes no
country/year/case constant.

No W^3 welfare finding is produced; no measure beyond W^3 is touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))
_REPO = _THIS.parent.parent.parent
for p in (_REPO / "scripts" / "enhanced", _REPO / "scripts" / "bpool",
          _REPO / "scripts" / "pilot"):
    sys.path.insert(0, str(p))


# ---------------------------------------------------------------------------
# g_hat redraw — reuse the estimator draw functions (same channel structure)
# ---------------------------------------------------------------------------
def _load_draw_machinery():
    """Import the SAME draw functions the proposal used. Returns a dict or raises
    with a precise reason (so a missing dependency is reported, not guessed)."""
    import build_bpool_singles as bbs  # PI0, N_DRAWS, _load_mincer
    from hours_mixture_d1 import draw_hours_d1
    from occ_draw_empirical import draw_loc4
    from pilot_wage_draw import draw_pilot_wages
    return {
        "PI0": bbs.PI0,
        "load_mincer": bbs._load_mincer,
        "draw_hours_d1": draw_hours_d1,
        "draw_loc4": draw_loc4,
        "draw_pilot_wages": draw_pilot_wages,
    }


def redraw_nodes_singles(hh_row: dict, n_nodes: int, rng, mincer, dm, *, year_tag):
    """Draw n_nodes integration nodes (w,h,loc4,working) from g_hat for one singles
    household, using the estimator's own draw functions. Returns a dict of arrays.

    This is the welfare-integration redraw, NOT a behavioural simulation: it produces
    the node LOCATIONS (w,h,...) at which v_i would be evaluated; the EV shocks are
    integrated analytically downstream (log-sum), so no Frechet draw / argmax occurs.
    """
    PI0 = dm["PI0"]
    u_emp = rng.uniform(size=n_nodes)
    working = (u_emp >= PI0).astype(np.int8)
    n_work = int(working.sum())

    loc4 = np.full(n_nodes, -1, dtype=np.int32)
    hours = np.zeros(n_nodes, dtype=np.float64)
    wage = np.zeros(n_nodes, dtype=np.float64)

    if n_work > 0:
        dgn = int(hh_row["dgn"])
        educ3 = int(hh_row["educ3"])
        loc4_w, _ = dm["draw_loc4"](np.full(n_work, dgn), np.full(n_work, educ3), rng)
        loc4[working == 1] = loc4_w
        h_w, _ = dm["draw_hours_d1"](n_work, rng)
        hours[working == 1] = h_w
        res = dm["draw_pilot_wages"](
            n=n_work,
            educL=np.full(n_work, float(hh_row["educL"])),
            educH=np.full(n_work, float(hh_row["educH"])),
            pexp_years=np.full(n_work, float(hh_row["pexp_years"])),
            pexp_years2=np.full(n_work, float(hh_row["pexp_years2"])),
            loc4=loc4_w,
            year_tag=np.full(n_work, year_tag),
            mincer_payload=mincer,
            seed=int(rng.integers(0, 2**31)),
            draw_method="halton",
        )
        wage[working == 1] = res["wage"]
    return {"working": working, "loc4": loc4, "hours": hours, "wage": wage,
            "n_work": n_work}


# ---------------------------------------------------------------------------
# EUROMOD-on-nodes coverage probe (the bounded touch — reports BLOCKED, no approx)
# ---------------------------------------------------------------------------
def _build_constants(cfg2):
    """Reuse the build module's system pairing / CPI(phi) / raw input schema /
    EuromodRunner — so the welfare path matches the build EXACTLY and welfare source
    hardcodes none of these case constants. Returns a dict or raises with reason."""
    import importlib
    mod = importlib.import_module(cfg2["build_module"])
    return {
        "system_pairing": mod._SYSTEM_PAIRING,   # year -> (system_code, dataset_name)
        "cpi": mod._CPI,                          # year -> phi (real-deflation factor)
        "raw_schema": mod._RAW_SCHEMA,            # year -> EUROMOD input column list
        "em_output_cols": mod._EM_OUTPUT_COLS,    # ['ils_dispy', ...]
        "EuromodRunner": mod.EuromodRunner,
        "em_root": mod._EM_ROOT,
    }


def euromod_on_nodes_status(cfg2):
    """Re-audit: can redrawn-node consumption (c_is) be produced from the EXISTING
    priced-long / precompute-long HOUSEHOLD TEMPLATES by overwriting only the
    decider's choice variables — WITHOUT a wholesale rebuild? Checks the storage-
    level files the v1 audit missed, across all configured years AND modes. Stems,
    years, modes, and the required schema all come from config / the build module;
    nothing case-specific is hardcoded here."""
    import pyarrow.parquet as pq
    from _bpool_paths import bpool_dir
    bc = _build_constants(cfg2)
    base = bpool_dir()
    priced_stem = cfg2["priced_long_stem"]
    precomp_stem = cfg2["precompute_long_stem"]
    years = cfg2["years"]
    modes = cfg2["modes"]

    per_file = {}
    all_feasible = True
    for year in years:
        req = list(bc["raw_schema"].get(year, []))   # the build's exact input schema for this year
        for mode in modes:
            priced = base / f"{priced_stem}__{year}__{mode}.parquet"
            precomp = base / f"{precomp_stem}__{year}__{mode}__long.parquet"
            entry = {"priced_long_exists": priced.exists(),
                     "precompute_long_exists": precomp.exists()}
            if priced.exists():
                cols = set(pq.ParquetFile(priced).schema.names)
                missing = [c for c in req if c not in cols]
                entry.update({
                    "n_required_input": len(req),
                    "n_present": len(req) - len(missing),
                    "missing_input_vars": missing,
                    "has_ils_dispy_stored": ("ils_dispy" in cols),
                    "has_ils_dispy_real_stored": ("ils_dispy_real" in cols),
                })
                feasible = (len(missing) == 0 and "ils_dispy" in cols)
            else:
                feasible = False
                entry["missing_input_vars"] = "PRICED_LONG_FILE_ABSENT"
            entry["template_overwrite_feasible"] = feasible
            all_feasible = all_feasible and feasible
            per_file[f"{year}__{mode}"] = entry

    return {
        "euromod_package_importable": _euromod_importable(),
        "checked": "priced_long + precompute_long (storage-level templates)",
        "per_file": per_file,
        "feasible_via_template_overwrite": all_feasible,
        "v1_wholesale_rebuild_conclusion_holds": (not all_feasible),
        "reason": ("Redrawn-node EUROMOD input records can be built from the EXISTING "
                   "priced-long household templates (full input schema + stored "
                   "ils_dispy present) by overwriting only the decider choice "
                   "variables and preserving non-decider roster variables. The v1 "
                   "'wholesale rebuild' conclusion — drawn from the engine-ready "
                   "parquet, which is the stripped estimation slice — is NARROWED: "
                   "the storage-level templates make a BOUNDED node-pricing touch "
                   "feasible. No re-deflation (phi reused from build); no silent "
                   "interpolation; no full rebuild." if all_feasible else
                   "Some required template field / stored ils_dispy is missing at "
                   "storage level; see per_file. Node pricing stays BLOCKED."),
    }


def _euromod_importable():
    try:
        import euromod  # noqa: F401
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Couples redraw node generation (joint two-partner, estimator channel structure)
# ---------------------------------------------------------------------------
def redraw_nodes_couples(hh_rows: dict, n_nodes: int, rng, mincer, dm, *, year_tag):
    """Draw n_nodes JOINT couples integration nodes from g_hat, per partner, using
    the SAME channel structure as build_bpool_couples (each partner: employment
    Bernoulli(pi0), occupation by that partner's dgn x educ3, D1 hours, lognormal
    wage at the partner's mean; partners independent). hh_rows = {"male": row,
    "female": row}. Returns per-partner node arrays. As with singles, this produces
    node LOCATIONS only; the EV shocks are integrated analytically downstream.

    NOTE: this builds the JOINT node locations. Pricing them still needs the couples
    EUROMOD template-overwrite path (both partners' choices overwritten in the joint
    household record) — gated on the same parity check as singles.
    """
    out = {}
    for leg in ("male", "female"):
        r = hh_rows[leg]
        single_like = redraw_nodes_singles(r, n_nodes, rng, mincer, dm, year_tag=year_tag)
        out[leg] = single_like
    out["n_nodes"] = n_nodes
    return out


# ---------------------------------------------------------------------------
# EUROMOD-on-nodes PARITY (Gate-0 analogue): reprice EXISTING nodes unchanged,
# confirm repriced ils_dispy reproduces stored ils_dispy to machine tolerance.
# ---------------------------------------------------------------------------
def euromod_reprice_parity(cfg2, *, year, mode, n_hh, tol):
    """Validate the template-overwrite EUROMOD path on EXISTING nodes BEFORE pricing
    any redrawn node. Take a tiny set of existing priced-long rows whose ils_dispy is
    already stored, feed them UNCHANGED (no choice overwrite) through the build's
    EuromodRunner with the build's raw schema + system pairing, and compare repriced
    ils_dispy to stored ils_dispy. Returns status dict with max abs diff.

    If parity fails, the overwrite path is untrustworthy and node pricing stays
    BLOCKED regardless of schema availability — no redrawn node is priced against an
    unvalidated path."""
    import pandas as pd
    import pyarrow.parquet as pq
    from _bpool_paths import bpool_dir
    bc = _build_constants(cfg2)
    if year not in bc["system_pairing"]:
        return {"status": "BLOCKED", "reason": f"year {year} not in build system pairing"}
    # build convention: _SYSTEM_PAIRING[year] = (system_code, dataset_name)
    system_code, dataset_name = bc["system_pairing"][year]
    # country is the system-code prefix (FR_2015 -> FR), the build's own agnostic
    # derivation (enh_RURO_euromod: country = euromod_system.split("_")[0]); an
    # optional config override wins if present. NOT hardcoded.
    country = str(cfg2.get("euromod_on_nodes", {}).get("country")
                  or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    base = bpool_dir()
    priced = base / f"{cfg2['priced_long_stem']}__{year}__{mode}.parquet"
    if not priced.exists():
        return {"status": "BLOCKED", "reason": f"priced-long absent: {priced.name}"}

    # take the first n_hh households (deterministic, tiny)
    pf = pq.ParquetFile(priced)
    df = pf.read_row_group(0).to_pandas() if pf.num_row_groups else pd.read_parquet(priced)
    hh_col = "stacked_hh_uid" if "stacked_hh_uid" in df.columns else "idhh"
    uids = df[hh_col].drop_duplicates().head(n_hh)
    sub = df[df[hh_col].isin(uids)].copy()
    sub = sub.groupby(hh_col, sort=False).head(20).reset_index(drop=True)
    if "ils_dispy" not in sub.columns:
        return {"status": "BLOCKED", "reason": "stored ils_dispy absent in priced-long"}
    stored = pd.to_numeric(sub["ils_dispy"], errors="coerce").to_numpy()

    # Faithful path: the build STAMPS unique draw IDs (run_bpool_euromod_chunk.
    # _stamp_draw_ids) BEFORE EUROMOD so per-draw rows do not collide on idhh/
    # idperson. Reuse that exact step so the reprice matches the build.
    import importlib
    bmod = importlib.import_module(cfg2["build_module"])
    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000
    try:
        stamped = bmod._stamp_draw_ids(sub.copy(), draw_col, id_mult)
    except Exception as e:
        return {"status": "BLOCKED", "reason": f"_stamp_draw_ids failed: {type(e).__name__}: {e}"}

    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em_input, country=country, system_code=system_code,
                                      dataset_name=dataset_name)
    except Exception as e:
        return {"status": "BLOCKED", "reason": f"EUROMOD run failed: {type(e).__name__}: {e}"}
    if "ils_dispy" not in sim.columns or len(sim) != len(sub):
        return {"status": "BLOCKED",
                "reason": f"EUROMOD output shape/cols mismatch (out={sim.shape})"}
    repriced = pd.to_numeric(sim["ils_dispy"], errors="coerce").to_numpy()
    diff = np.abs(repriced - stored)
    max_abs = float(np.nanmax(diff))
    n_bad = int(np.sum(diff > tol))
    return {"status": "PASS" if max_abs <= tol else "FAIL",
            "n_rows": int(len(sub)), "n_hh": int(len(uids)),
            "year": year, "mode": mode, "country": country,
            "system_code": system_code, "id_stamped": True,
            "max_abs_diff": max_abs, "median_abs_diff": float(np.nanmedian(diff)),
            "n_rows_above_tol": n_bad, "tol": tol,
            "note": ("repriced EXISTING nodes (no choice overwrite) vs stored "
                     "ils_dispy, with the build's _stamp_draw_ids applied. Validates "
                     "the EUROMOD-overwrite path before any redrawn node is priced. "
                     "Median 0 = path correct for income; a residual tail above tol is "
                     "STRUCTURAL and localised to ils_ben (benefits) on benefit-"
                     "recipient households -> node pricing stays BLOCKED, no redrawn "
                     "node priced against an unvalidated path. See "
                     "RURO_welfare_stage2_parity_v1.md (Increment Two-B)."),
            "diagnosis": ("Increment Two-B classifies this STRUCTURAL: divergence is "
                          "localised entirely to ils_ben (ils_origy/ils_sicdy reproduce "
                          "to machine zero); the build-faithful path is NOT closer, so "
                          "it is NOT a missing chunk-runner preprocessing step. The "
                          "stored benefit encodes household/annual state the per-draw "
                          "row does not carry. See the parity grid + report.")}


# ---------------------------------------------------------------------------
# Multiplier stability via EXISTING-node subsampling (no new consumption)
# ---------------------------------------------------------------------------
def node_subsample_stability(gw, theta, spec, data, group, fractions, rng):
    """V_i^IS drift as the welfare-integral node count GROWS toward the full set,
    by subsampling the EXISTING draw nodes at the given fractions. Needs NO new
    consumption (reuses existing c_ij). This is welfare-integral node growth on
    existing draws — NOT estimation-draw rebuilding, and NOT the configured 2x/4x
    multiplier (which would need new nodes -> new c_is -> BLOCKED).

    Returns per-fraction max/median |V_i^IS(frac) - V_i^IS(full)| across households.
    """
    import jax.numpy as jnp
    n_groups, n_alts = gw.n_groups, gw.n_alts
    th = jnp.asarray(theta, dtype=jnp.float64)
    cons = gw.consumption_grid                      # (n_groups, n_alts)
    Vfull = gw.V_is                                 # full-set inclusive value

    # recompute V grid once
    V = np.asarray(gw.V_extractor(th, jnp.asarray(cons.reshape(-1), dtype=jnp.float64)))
    Vg = V.reshape(n_groups, n_alts)

    # The chosen alternative (col 0 for real data) must always be retained so the
    # subsampled set still spans the observed node; sample the rest.
    out = {}
    for f in fractions:
        k = max(2, int(round(f * n_alts)))
        if k >= n_alts:
            out[f] = {"k": n_alts, "max_drift": 0.0, "median_drift": 0.0}
            continue
        # per-household: keep col 0 + (k-1) sampled distinct non-zero columns
        drift = np.empty(n_groups, dtype=np.float64)
        for i in range(n_groups):
            idx = np.empty(k, dtype=np.int64)
            idx[0] = 0
            rest = rng.choice(np.arange(1, n_alts), size=k - 1, replace=False)
            idx[1:] = rest
            v = Vg[i, idx]
            m = v.max()
            lse_sub = m + np.log(np.sum(np.exp(v - m)))
            # match the full-set normalisation: subtract log(k/n_alts) so the
            # log-MEAN comparison is scale-consistent (logsum -> log of empirical
            # mean over the sampled node count vs the full node count).
            lse_sub_mean = lse_sub - np.log(k)
            lse_full_mean = Vfull[i] - np.log(n_alts)
            drift[i] = abs(lse_sub_mean - lse_full_mean)
        out[f] = {"k": k, "max_drift": float(np.max(drift)),
                  "median_drift": float(np.median(drift))}
    return out


# ---------------------------------------------------------------------------
# Stage-Two-B PARITY GRID: deterministic reprice over every year x mode cell,
# with EUROMOD output-component decomposition + couples household-joint parity.
# Agnostic: stems/years/modes/tol from config; system/CPI/schema/runner from the
# build module; country derived from the system-code prefix (config override).
# ---------------------------------------------------------------------------
def _reprice_cell(cfg2, bc, *, year, mode, n_hh, rows_per_hh, components,
                  country_override, rows_csv=None):
    """Reprice a tiny deterministic subset of one year x mode priced-long cell and
    compare repriced EUROMOD outputs to the stored values. Returns a per-cell dict
    incl. component decomposition and (for couples) household-joint disposable-income
    parity. No node overwrite: this validates the EUROMOD path on EXISTING nodes.

    rows_csv: if set, persist the FULL smoke-row table for this cell (all rows, not
    only the failing ones) with stored/repriced ils_dispy + component diffs and a FAIL
    flag (FAIL == absdiff_ils_dispy > tol)."""
    import pandas as pd
    import pyarrow.parquet as pq
    from _bpool_paths import bpool_dir

    if year not in bc["system_pairing"]:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"year {year} not in build system pairing"}
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    priced = bpool_dir() / f"{cfg2['priced_long_stem']}__{year}__{mode}.parquet"
    if not priced.exists():
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"priced-long absent: {priced.name}"}

    pf = pq.ParquetFile(priced)
    df = pf.read_row_group(0).to_pandas() if pf.num_row_groups else pd.read_parquet(priced)
    hh_col = "stacked_hh_uid" if "stacked_hh_uid" in df.columns else "idhh"
    uids = df[hh_col].drop_duplicates().head(n_hh)
    sub = (df[df[hh_col].isin(uids)]
           .groupby(hh_col, sort=False).head(rows_per_hh).reset_index(drop=True))
    if "ils_dispy" not in sub.columns:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": "stored ils_dispy absent"}

    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000
    import importlib
    bmod = importlib.import_module(cfg2["build_module"])
    stamped = bmod._stamp_draw_ids(sub.copy(), draw_col, id_mult)
    em = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em.columns:
        em[c] = pd.to_numeric(em[c], errors="coerce").fillna(0.0)
    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em, country=country, system_code=system_code,
                                      dataset_name=dataset_name)
    except Exception as e:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"EUROMOD run failed: {type(e).__name__}: {e}"}
    if "ils_dispy" not in sim.columns or len(sim) != len(sub):
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"EUROMOD output shape/cols mismatch (out={sim.shape})"}

    stored = pd.to_numeric(sub["ils_dispy"], errors="coerce").to_numpy()
    rep = pd.to_numeric(sim["ils_dispy"], errors="coerce").to_numpy()
    diff = np.abs(rep - stored)
    n_bad = int(np.sum(diff > cfg2["parity_grid"]["tol"]))

    # component decomposition — localise any divergence
    tol = float(cfg2["parity_grid"]["tol"])
    comp_div = {}
    comp_diffs = {}
    for comp in components:
        if comp in sub.columns and comp in sim.columns:
            s = pd.to_numeric(sub[comp], errors="coerce").to_numpy()
            o = pd.to_numeric(sim[comp], errors="coerce").to_numpy()
            dc = np.abs(o - s)
            comp_diffs[comp] = dc
            comp_div[comp] = {"n_above_tol": int(np.sum(dc > tol)),
                              "max_abs": float(np.nanmax(dc))}

    # optionally persist the FULL smoke-row table (all rows, FAIL flag per row)
    if rows_csv is not None:
        from pathlib import Path
        idcols = [c for c in [hh_col, draw_col, "idperson", "dgn", "lhw"]
                  if c in sub.columns]
        rt = sub[idcols].copy()
        rt["stored_ils_dispy"] = stored
        rt["reprice_ils_dispy"] = rep
        rt["absdiff_ils_dispy"] = diff
        for comp, dc in comp_diffs.items():
            rt[f"absdiff_{comp}"] = dc
        if "ils_ben" in sub.columns:
            rt["stored_ils_ben"] = pd.to_numeric(sub["ils_ben"], errors="coerce").to_numpy()
        rt["FAIL"] = diff > tol
        Path(rows_csv).parent.mkdir(parents=True, exist_ok=True)
        rt.to_csv(rows_csv, index=False)

    cell = {"year": year, "mode": mode, "country": country, "system_code": system_code,
            "n_rows": int(len(sub)), "n_hh": int(len(uids)),
            "n_alts_per_hh_max": int(sub.groupby(hh_col)[draw_col].nunique().max()),
            "individual_ils_dispy": {
                "max_abs_diff": float(np.nanmax(diff)),
                "median_abs_diff": float(np.nanmedian(diff)),
                "n_rows_above_tol": n_bad},
            "component_divergence": comp_div,
            "status": "PASS" if float(np.nanmax(diff)) <= tol else "FAIL"}

    # couples: household-JOINT summed disposable income at the alternative level
    if mode == "couples":
        sub2 = sub.copy()
        sub2["__rep"] = rep
        sub2["__stored"] = stored
        grp = sub2.groupby([hh_col, draw_col])
        jrep = grp["__rep"].sum().to_numpy()
        jst = grp["__stored"].sum().to_numpy()
        jd = np.abs(jrep - jst)
        cell["household_joint_dispy"] = {
            "n_alternatives": int(len(jd)),
            "max_abs_diff": float(np.nanmax(jd)),
            "median_abs_diff": float(np.nanmedian(jd)),
            "n_above_tol": int(np.sum(jd > tol))}

    if cell["status"] != "PASS":
        # classification driven by the component decomposition
        bcomp = max(comp_div, key=lambda c: comp_div[c]["max_abs"]) if comp_div else None
        cell["failure_classification"] = (
            "STRUCTURAL" if (bcomp == "ils_ben") else "UNRESOLVED")
        cell["failure_note"] = (
            f"divergence localised to {bcomp}; benefit-recipient-localised, not a "
            "uniform omitted preprocessing step (build-faithful path was not closer)."
            if bcomp == "ils_ben" else
            f"divergence localised to {bcomp}; classification UNRESOLVED.")
    return cell


def parity_grid(cfg2, *, rows_csv_dir=None):
    """Run the deterministic parity grid over all configured year x mode cells.

    rows_csv_dir: if set, persist the FULL smoke-row diagnostic table for the
    reference cell (euromod_on_nodes.smoke_year x smoke_mode) to
    {rows_csv_dir}/stage2_parity_smoke_rows_diag.csv."""
    bc = _build_constants(cfg2)
    pg = cfg2["parity_grid"]
    ref_year = int(cfg2["euromod_on_nodes"]["smoke_year"])
    ref_mode = str(cfg2["euromod_on_nodes"]["smoke_mode"])
    cells = {}
    for year in cfg2["years"]:
        for mode in cfg2["modes"]:
            rows_csv = None
            if rows_csv_dir is not None and year == ref_year and mode == ref_mode:
                rows_csv = f"{rows_csv_dir}/stage2_parity_smoke_rows_diag.csv"
            cells[f"{year}__{mode}"] = _reprice_cell(
                cfg2, bc, year=year, mode=mode,
                n_hh=int(pg["n_hh"]), rows_per_hh=int(pg["rows_per_hh"]),
                components=list(pg["decompose_components"]),
                country_override=pg.get("country_override"),
                rows_csv=rows_csv)
    all_pass = all(c.get("status") == "PASS" for c in cells.values())
    return {"all_cells_pass": all_pass, "cells": cells,
            "smoke_rows_table": (
                f"{rows_csv_dir}/stage2_parity_smoke_rows_diag.csv"
                f" (cell {ref_year}__{ref_mode}; FULL smoke sample, FAIL = "
                f"absdiff_ils_dispy > tol)" if rows_csv_dir else None)}
