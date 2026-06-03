"""
STAGE THREE, INCREMENT THREE-B1 — assemble the validated reproducible staged baseline into
engine-ready estimation objects and run pre-estimation parity gates.

Builds STAGED engine-ready singles+couples from the Three-A-validated Two-N staged rebuild,
through the SAME construction path as the certified estimate (build_bpool_estimation_ready +
harmonise_bpool_engine_ready), differing ONLY in the priced ils_dispy_real source (staged
chunks instead of the stored production priced files). Then runs:

  TASK 1  assemble staged engine-ready to a STAGING-ONLY stem (never overwrites certified).
  TASK 2  structure / row-order gates vs certified engine-ready.
  TASK 3  consumption blast-radius gate (consumption/c_norm/c_scale; shares, quantiles,
          breakdowns by year/mode/chosen/benefit-recipient).
  TASK 4  likelihood parity at certified theta_hat using the certified JAX machinery
          (joint + per-group dLL; localisation; no-change control).
  TASK 5  readiness for Three-B2.

Does NOT: re-estimate, run synthetic recovery, compute V_i^dir, price redrawn nodes, promote
W^3, swap/overwrite/move/delete any production parquet, or promote the staged baseline to
canonical. The staged engine-ready files use a DISTINCT stem and live in bpool_dir() alongside
(never replacing) the certified files; the staged priced/estimation-ready intermediates go to a
clearly-marked staging dir.

Config-driven: system pairing / CPI / stems are read from the Three-A pinned config and the
certified build modules; nothing France/year-specific is hardcoded here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
sys.path.insert(0, "scripts/enhanced")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

TOL = 1e-6
_STAGED_STEM = "fr_p3a_bpool_engine_ready_staged_threeB1"
_CERT_STEM = "fr_p3a_bpool_engine_ready"
_PINNED_CONFIG = Path("outputs/welfare/stage1_w3/stage3a_pinned_rebuild_config.json")
_CERT_THETA = Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv")
_CERT_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
_YEARS = (2015, 2016, 2017)
_COUPLES_NCHUNKS = 6


# ----------------------------------------------------------------------------------------
# TASK 1 — assemble staged chunks -> staged priced -> staged estimation-ready -> engine-ready
# ----------------------------------------------------------------------------------------
def assemble_staged_priced(staging_in, staged_priced_dir):
    """Concatenate the Two-N staged chunks into per-(year,mode) priced long files, in chunk
    order (= the production assembler's order: c0,c1,... ignore_index, no global sort)."""
    staged_priced_dir.mkdir(parents=True, exist_ok=True)
    out = {}
    for year in _YEARS:
        for mode in ("singles", "couples"):
            n = 1 if mode == "singles" else _COUPLES_NCHUNKS
            parts = []
            for cid in range(n):
                cp = staging_in / f"fr_p3a_bpool_priced__{year}__{mode}__c{cid}.parquet"
                if not cp.exists():
                    raise SystemExit(f"STOP: missing staged chunk {cp}")
                parts.append(pd.read_parquet(cp))
            df = pd.concat(parts, ignore_index=True)
            p = staged_priced_dir / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
            df.to_parquet(p, index=False)
            out[f"{year}_{mode}"] = {"rows": int(len(df)), "path": str(p)}
    return out


def build_staged_engine_ready(staged_priced_dir):
    """Run the certified build + harmonise path, but with the priced-file source redirected
    to the STAGED priced dir, and outputs written to the STAGED stem. Only ils_dispy_real
    (hence consumption / c_norm / c_scale) can differ; every other field is constructed
    identically to the certified path."""
    import build_bpool_estimation_ready as bld
    import harmonise_bpool_engine_ready as harm

    bp = bpool_dir()
    # The build's dispy/urbanisation lookups read priced files from bld._BP. Point ONLY the
    # priced reads at the staged dir by giving the build a _BP whose priced files are staged
    # but whose OTHER inputs (d1w1, FR parquets, child-band sources) resolve to production.
    # bld._BP is used for BOTH priced reads AND d1w1 reads, so we mirror: a staging dir that
    # contains the staged priced files + links to the unchanged d1w1 inputs.
    mirror = staged_priced_dir  # already holds staged priced files
    for needed in ("fr_p3a_bpool_d1w1__singles.parquet",
                   "fr_p3a_bpool_d1w1__couples.parquet"):
        link = mirror / needed
        if not link.exists():
            # hardlink/copy the unchanged d1w1 input so bld._BP resolves it
            src = bp / needed
            try:
                link.hardlink_to(src)
            except (OSError, AttributeError):
                import shutil
                shutil.copy2(src, link)

    # estimation-ready writes: redirect to staged stem under bpool_dir() (loader reads there)
    est_s = bp / "fr_p3a_bpool_estimation_ready_staged_threeB1__singles.parquet"
    est_c = bp / "fr_p3a_bpool_estimation_ready_staged_threeB1__couples.parquet"

    # --- build estimation-ready (singles + couples) with redirected _BP ---
    orig_bld_bp = bld._BP
    bld._BP = mirror
    try:
        df_s = bld.build_singles()
        df_c = bld.build_couples()
    finally:
        bld._BP = orig_bld_bp
    df_s.to_parquet(est_s, index=False)
    df_c.to_parquet(est_c, index=False)

    # --- harmonise to engine-ready (reads estimation-ready from harm._BP) ---
    # harmonise reads "fr_p3a_bpool_estimation_ready__{mode}.parquet" from harm._BP. Point a
    # mirror dir holding the STAGED estimation-ready under the certified names so harmonise
    # reads them; write engine-ready to the staged stem.
    harm_mirror = staged_priced_dir / "_harm_in"
    harm_mirror.mkdir(parents=True, exist_ok=True)
    for src, name in ((est_s, "fr_p3a_bpool_estimation_ready__singles.parquet"),
                      (est_c, "fr_p3a_bpool_estimation_ready__couples.parquet")):
        link = harm_mirror / name
        if link.exists():
            link.unlink()
        try:
            link.hardlink_to(src)
        except (OSError, AttributeError):
            import shutil
            shutil.copy2(src, link)

    eng_s = bp / f"{_STAGED_STEM}__singles.parquet"
    eng_c = bp / f"{_STAGED_STEM}__couples.parquet"
    orig_harm_bp = harm._BP
    harm._BP = harm_mirror
    try:
        hs, scaling_s = harm.harmonise_singles()
        hc, scaling_c = harm.harmonise_couples()
    finally:
        harm._BP = orig_harm_bp
    hs.to_parquet(eng_s, index=False)
    hc.to_parquet(eng_c, index=False)
    write_staged_meta(bp, scaling_s, scaling_c)
    return {"engine_ready_singles": str(eng_s), "engine_ready_couples": str(eng_c),
            "estimation_ready_singles": str(est_s), "estimation_ready_couples": str(est_c),
            "scaling_singles": scaling_s, "scaling_couples": scaling_c}


def write_staged_meta(bp, scaling_s, scaling_c, stem=_STAGED_STEM):
    """Write the staged engine-ready __mnlmeta.json by cloning the CERTIFIED meta structure
    and overriding ONLY the normalization scaling (c_scale/l_scale[s]) with the staged values.
    The loader reads this sidecar for normalization context; the c_norm/l_norm columns
    themselves are already in the parquet. Mirrors harmonise_bpool_engine_ready.main()."""
    cert_meta_path = bp / f"{_CERT_STEM}__mnlmeta.json"
    if cert_meta_path.exists():
        with open(cert_meta_path) as f:
            meta = dict(json.load(f))
    else:
        meta = {}
    meta["source"] = (f"STAGED Three-B1 engine-ready (stem {stem}); cloned normalization "
                      f"structure from certified meta, scaling from staged harmonise")
    meta["normalization"] = {
        "singles": {"c_scale": scaling_s["c_scale"], "l_scale": scaling_s["l_scale"],
                    "n_chosen": scaling_s["n_chosen"]},
        "couples": {"c_scale": scaling_c["c_scale"], "l_male_scale": scaling_c["l_male_scale"],
                    "l_female_scale": scaling_c["l_female_scale"],
                    "n_chosen": scaling_c["n_chosen"]},
    }
    out = bp / f"{stem}__mnlmeta.json"
    with open(out, "w") as f:
        json.dump(meta, f, indent=2, default=float)
    return str(out)


def _scaling_from_parquet(bp, mode):
    """Recompute the harmonise scaling dict from an already-built staged engine-ready parquet
    (for the --skip-build path, where the in-memory scaling is gone). c_scale = mean(raw
    consumption); l_scale[s] = min positive chosen leisure — same rules as harmonise."""
    df = pd.read_parquet(bp / f"{_STAGED_STEM}__{mode}.parquet")
    c_scale = float(pd.to_numeric(df["consumption"], errors="coerce").mean())
    if mode == "singles":
        chosen = df["is_chosen"] == 1
        lp = df.loc[chosen, "leisure"]
        lp = lp[lp > 0]
        l_scale = float(lp.min()) if len(lp) else 1.0
        return {"c_scale": c_scale, "l_scale": l_scale, "n_chosen": int(chosen.sum())}
    chosen = df["is_chosen_joint"] == 1

    def _ls(col):
        lc = df.loc[chosen, col]
        lp = lc[lc > 0]
        return float(lp.min()) if len(lp) else 1.0
    return {"c_scale": c_scale, "l_male_scale": _ls("leisure_male"),
            "l_female_scale": _ls("leisure_female"), "n_chosen": int(chosen.sum())}


# ----------------------------------------------------------------------------------------
# TASK 2 — structure / row-order gates
# ----------------------------------------------------------------------------------------
def _key_cols(mode):
    base = ["stacked_hh_uid"]
    if mode == "singles":
        return base + ["draw", "is_chosen"]
    return base + ["draw_joint", "is_chosen_joint"]


def structure_gate(bp, mode, expected_alts):
    cert = pd.read_parquet(bp / f"{_CERT_STEM}__{mode}.parquet")
    stg = pd.read_parquet(bp / f"{_STAGED_STEM}__{mode}.parquet")
    chosen = "is_chosen" if mode == "singles" else "is_chosen_joint"
    draw = "draw" if mode == "singles" else "draw_joint"
    out = {"mode": mode}
    out["rows_cert"] = int(len(cert))
    out["rows_staged"] = int(len(stg))
    out["rows_match"] = bool(len(cert) == len(stg))
    out["hh_cert"] = int(cert["stacked_hh_uid"].nunique())
    out["hh_staged"] = int(stg["stacked_hh_uid"].nunique())
    out["hh_match"] = bool(out["hh_cert"] == out["hh_staged"])
    # alts per HH
    per_hh = stg.groupby("stacked_hh_uid").size()
    out["alts_per_hh_modal"] = int(per_hh.mode().iloc[0])
    out["alts_per_hh_uniform"] = bool((per_hh == expected_alts).all())
    out["alts_per_hh_expected"] = expected_alts
    # one chosen row per choice set
    chosen_counts = stg[stg[chosen] == 1].groupby("stacked_hh_uid").size()
    out["one_chosen_per_set"] = bool((chosen_counts == 1).all()
                                     and chosen_counts.shape[0] == out["hh_staged"])
    # row order + key alignment (positional, after both are built the same way)
    order_ok = True
    keys = _key_cols(mode)
    keys = [k for k in keys if k in cert.columns and k in stg.columns]
    for k in keys:
        order_ok = order_ok and bool((cert[k].to_numpy() == stg[k].to_numpy()).all())
    out["row_order_keys_identical"] = order_ok
    out["keys_checked"] = keys
    # cluster key alignment
    if "cluster_id" in cert.columns and "cluster_id" in stg.columns:
        out["cluster_id_identical"] = bool(
            (cert["cluster_id"].to_numpy() == stg["cluster_id"].to_numpy()).all())
        out["cluster_key"] = "idorighh(->cluster_id)"
    # draw keys + choice indicator identical
    out["draw_identical"] = bool((cert[draw].to_numpy() == stg[draw].to_numpy()).all()) \
        if draw in cert.columns else None
    out["chosen_indicator_identical"] = bool(
        (cert[chosen].to_numpy() == stg[chosen].to_numpy()).all()) \
        if chosen in cert.columns else None
    out["ok"] = bool(out["rows_match"] and out["hh_match"] and out["alts_per_hh_uniform"]
                     and out["one_chosen_per_set"] and order_ok
                     and out.get("cluster_id_identical", True)
                     and (out["draw_identical"] in (True, None))
                     and (out["chosen_indicator_identical"] in (True, None)))
    return out, cert, stg


# ----------------------------------------------------------------------------------------
# TASK 3 — consumption blast-radius (descriptive); channels separated per the addendum:
#   (1) RAW consumption / ils_dispy_real blast (the intended, benefit-driven change);
#   (2) c_scale old vs new + percent change;
#   (3) c_norm blast INDUCED ONLY by the changed denominator (global c_scale), measured on
#       rows whose RAW consumption did NOT change;
#   plus chosen/nonchosen, year, and benefit-recipient breakdowns.
# ----------------------------------------------------------------------------------------
def blast_radius(cert, stg, mode):
    chosen = "is_chosen" if mode == "singles" else "is_chosen_joint"
    out = {"mode": mode, "n_rows": int(len(cert))}

    # ---- (1) RAW consumption change ----
    cc = pd.to_numeric(cert["consumption"], errors="coerce").to_numpy()
    sc = pd.to_numeric(stg["consumption"], errors="coerce").to_numpy()
    d = np.abs(sc - cc)
    changed = d > TOL                      # RAW-consumption-changed rows
    out["raw_consumption"] = {
        "n_changed": int(changed.sum()),
        "share_changed": round(float(changed.mean()), 6),
        "max_abs": float(np.nanmax(d)) if len(d) else 0.0,
        "median_abs_over_changed": float(np.median(d[changed])) if changed.any() else 0.0,
        "q_over_changed": {str(q): float(np.quantile(d[changed], q))
                           for q in (0.5, 0.9, 0.99, 1.0)} if changed.any() else {},
        "definition": "abs(staged.consumption - cert.consumption) > tol; consumption = "
                      "ils_dispy_real (singles) / joint ils_dispy_real (couples), floored.",
    }
    hh = cert["stacked_hh_uid"].to_numpy()
    touched_hh = pd.unique(hh[changed])
    out["choice_sets_touched_by_raw_change"] = {
        "n_touched": int(len(touched_hh)),
        "share_touched": round(float(len(touched_hh) / cert["stacked_hh_uid"].nunique()), 6)}

    # ---- (2) c_scale old vs new + percent ----
    cs_cert = float(cert["consumption"].mean())
    cs_stg = float(stg["consumption"].mean())
    out["c_scale"] = {"cert": cs_cert, "staged": cs_stg,
                      "abs_diff": abs(cs_stg - cs_cert),
                      "pct_change": (100.0 * (cs_stg - cs_cert) / cs_cert)
                      if cs_cert else None}

    # ---- (3) c_norm blast INDUCED ONLY by the changed denominator ----
    # On RAW-UNCHANGED rows, staged.c_norm should equal cert.c_norm * (cs_cert / cs_stg)
    # to machine tolerance (same numerator, different denominator). Any residual beyond that
    # ratio on a raw-unchanged row is an UNINTENDED change -> STOP signal.
    cn = pd.to_numeric(cert["c_norm"], errors="coerce").to_numpy()
    sn = pd.to_numeric(stg["c_norm"], errors="coerce").to_numpy()
    unchanged = ~changed
    ratio = cs_cert / cs_stg if cs_stg else float("nan")
    predicted_sn_unchanged = cn[unchanged] * ratio      # pure-denominator prediction
    resid = np.abs(sn[unchanged] - predicted_sn_unchanged)
    # relative residual (c_norm ~ O(1)); machine-tolerance band
    resid_rel = resid / np.maximum(np.abs(predicted_sn_unchanged), 1e-12)
    n_resid_bad = int((resid_rel > 1e-9).sum())
    out["c_norm_denominator_channel"] = {
        "rows_raw_unchanged": int(unchanged.sum()),
        "predicted_rule": "staged.c_norm = cert.c_norm * (c_scale_cert / c_scale_staged) on "
                          "raw-unchanged rows (numerator identical, denominator global)",
        "denominator_ratio_cert_over_staged": ratio,
        "max_abs_residual_vs_prediction": float(resid.max()) if resid.size else 0.0,
        "max_rel_residual_vs_prediction": float(resid_rel.max()) if resid_rel.size else 0.0,
        "n_rows_resid_above_1e-9_rel": n_resid_bad,
        "no_change_control_pass": bool(n_resid_bad == 0),
        "interpretation": "if 0, every raw-unchanged row differs ONLY through the global "
                          "c_scale denominator (intended). Nonzero => an unintended row-level "
                          "change beyond the c_scale channel -> STOP.",
    }
    # also report total c_norm change (all rows) for context
    dn = np.abs(sn - cn)
    out["c_norm_total"] = {"n_changed": int((dn > TOL).sum()),
                           "share_changed": round(float((dn > TOL).mean()), 6),
                           "max_abs": float(np.nanmax(dn)) if len(dn) else 0.0,
                           "note": "includes the global c_scale renormalisation on ALL rows; "
                                   "NOT a row-level data-change count."}

    # ---- breakdowns of the RAW change ----
    ch = cert[chosen].to_numpy() == 1
    out["raw_by_chosen"] = {
        "chosen_n_changed": int(changed[ch].sum()),
        "chosen_share_changed": round(float(changed[ch].mean()), 6) if ch.any() else 0.0,
        "nonchosen_n_changed": int(changed[~ch].sum()),
        "nonchosen_share_changed": round(float(changed[~ch].mean()), 6)
        if (~ch).any() else 0.0}
    if "data_year" in cert.columns:
        yb = {}
        yr = cert["data_year"].to_numpy()
        for y in _YEARS:
            m = yr == y
            yb[str(y)] = {"n_changed": int(changed[m].sum()),
                          "share_changed": round(float(changed[m].mean()), 6)
                          if m.any() else 0.0}
        out["raw_by_year"] = yb
    # benefit-recipient breakdown where identifiable (ils_ben>0 on chosen row carried?)
    ben_col = next((c for c in ("ils_ben",) if c in cert.columns), None)
    if ben_col is not None:
        ben = pd.to_numeric(cert[ben_col], errors="coerce").fillna(0).to_numpy() > 0
        out["raw_by_benefit_recipient"] = {
            "recipient_n_changed": int(changed[ben].sum()),
            "recipient_share_changed": round(float(changed[ben].mean()), 6)
            if ben.any() else 0.0,
            "nonrecipient_n_changed": int(changed[~ben].sum()),
            "nonrecipient_share_changed": round(float(changed[~ben].mean()), 6)
            if (~ben).any() else 0.0}
    else:
        out["raw_by_benefit_recipient"] = {"note": "ils_ben not carried on engine-ready; "
                                           "benefit status not separable here"}
    out["no_change_control_pass"] = out["c_norm_denominator_channel"]["no_change_control_pass"]
    return out, changed


# ----------------------------------------------------------------------------------------
# TASK 4 — likelihood parity at certified theta_hat (certified JAX machinery).
# Per the addendum, the staged likelihood is evaluated under THREE c_norm regimes so the
# raw-consumption channel is isolated from the global c_scale channel:
#   (A) certified engine-ready (native cert c_scale)         -> reference negLL
#   (B) staged engine-ready, NATIVE staged c_scale           -> total effect
#   (C) staged engine-ready, FIXED certified c_scale         -> raw-consumption effect only
# The pure c_scale channel = (B) - (C). No optimisation; theta = certified theta_hat.
# ----------------------------------------------------------------------------------------
def _write_fixed_cscale_variant(bp, mode, cs_cert, cs_staged):
    """Write a staged engine-ready variant whose c_norm is re-based to the CERTIFIED c_scale:
    c_norm_fixed = staged.consumption / cs_cert (= staged.c_norm * cs_staged / cs_cert).
    Isolates the raw-consumption channel by removing the staged-c_scale denominator shift."""
    stem_fixed = f"{_STAGED_STEM}_fixedcscale"
    src = bp / f"{_STAGED_STEM}__{mode}.parquet"
    df = pd.read_parquet(src)
    # rescale c_norm and log_c_norm to the certified denominator
    df["c_norm"] = pd.to_numeric(df["c_norm"], errors="coerce") * (cs_staged / cs_cert)
    if "log_c_norm" in df.columns:
        df["log_c_norm"] = np.log(np.clip(df["c_norm"].to_numpy(), 1.0e-12, None))
    out = bp / f"{stem_fixed}__{mode}.parquet"
    df.to_parquet(out, index=False)
    # mnlmeta: copy the staged meta but record the fixed c_scale (loader reads meta for l_scale)
    import shutil
    meta_src = bp / f"{_STAGED_STEM}__mnlmeta.json"
    meta_dst = bp / f"{stem_fixed}__mnlmeta.json"
    if meta_src.exists():
        shutil.copy2(meta_src, meta_dst)
    return stem_fixed, str(out)


def likelihood_parity(bp, cs_singles, cs_couples):
    import jax
    jax.config.update("jax_enable_x64", True)
    import estimation_spec_parser as sp
    import joint_recovery_test as jrt
    from jax_joint_hessian import build_jax_couples_ll, build_jax_singles_ll, build_joint_neg_ll

    spec = sp.parse_specification(_CERT_SPEC)
    spec_gs = set(getattr(spec, "gender_split", []) or [])
    theta = np.asarray(jrt.load_theta_star_from_csv(_CERT_THETA, spec), dtype=np.float64)
    th = np.asarray(theta)
    years = list(_YEARS)

    def _ll(stem):
        d_sm, d_sf, d_cou = jrt.build_data_objects(stem, years, 0, couples_stem=stem)
        joint = build_joint_neg_ll(spec, d_sm, d_sf, d_cou, gender_split=spec_gs or None)
        # per-group builders: signature (data, spec, ...) and each returns (jit_fn, pidx).
        ll_sm, _ = build_jax_singles_ll(d_sm, spec, is_male=True,
                                        gender_split=spec_gs or None)
        ll_sf, _ = build_jax_singles_ll(d_sf, spec, is_male=False,
                                        gender_split=spec_gs or None)
        ll_cou, _ = build_jax_couples_ll(d_cou, spec, gender_split=spec_gs or None)
        return {"joint_negLL": float(joint(th)),
                "singles_male_negLL": float(ll_sm(th)),
                "singles_female_negLL": float(ll_sf(th)),
                "couples_negLL": float(ll_cou(th)),
                "n_sm": int(d_sm.n_groups), "n_sf": int(d_sf.n_groups),
                "n_cou": int(d_cou.n_groups)}

    # (A) certified, (B) staged native c_scale
    cert = _ll(_CERT_STEM)
    staged_native = _ll(_STAGED_STEM)

    # (C) staged fixed certified c_scale — build the variant, then evaluate
    sfx, _ = _write_fixed_cscale_variant(bp, "singles", cs_singles["cert"],
                                         cs_singles["staged"])
    _write_fixed_cscale_variant(bp, "couples", cs_couples["cert"],
                                cs_couples["staged"])  # couples fixed parquet (side-effect)
    # both modes share the same fixed stem name; load that stem
    staged_fixed = _ll(sfx)

    keys = ("joint_negLL", "singles_male_negLL", "singles_female_negLL", "couples_negLL")
    return {
        "theta_source": str(_CERT_THETA),
        "regime_A_certified": cert,
        "regime_B_staged_native_cscale": staged_native,
        "regime_C_staged_fixed_cert_cscale": staged_fixed,
        "delta_total_BminusA": {k: staged_native[k] - cert[k] for k in keys},
        "delta_rawconsumption_CminusA": {k: staged_fixed[k] - cert[k] for k in keys},
        "delta_cscale_channel_BminusC": {k: staged_native[k] - staged_fixed[k] for k in keys},
        "computable_with_certified_machinery": True,
        "note": "negLL at certified theta_hat on each regime; no optimisation. "
                "Total (B-A) = raw-consumption (C-A) + c_scale channel (B-C). The raw "
                "channel localises to groups whose consumption changed; the c_scale channel "
                "is the common renormalisation.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--staging-priced-dir", required=True,
                    help="staging-only dir for the assembled staged priced + intermediates; "
                         "must NOT be production new_data root, chunks/, or staging_twoN")
    ap.add_argument("--skip-build", action="store_true",
                    help="reuse already-built staged engine-ready (resumability)")
    args = ap.parse_args()

    bp = bpool_dir()
    staging_twoN = bp / "staging_twoN"
    staged_priced_dir = Path(args.staging_priced_dir).resolve()
    # refuse dangerous staging targets
    if staged_priced_dir in (bp.resolve(), (bp / "chunks").resolve(),
                             staging_twoN.resolve()):
        raise SystemExit(f"REFUSE: staging-priced-dir '{staged_priced_dir}' must not be "
                         f"production root / chunks/ / staging_twoN.")
    if not _PINNED_CONFIG.exists():
        raise SystemExit(f"STOP: pinned Three-A config missing: {_PINNED_CONFIG}")

    build_info = None
    if not args.skip_build:
        assemble_info = assemble_staged_priced(staging_twoN, staged_priced_dir)
        build_info = build_staged_engine_ready(staged_priced_dir)
        build_info["assembled_staged_priced"] = assemble_info
    else:
        # resumability: staged engine-ready parquets must already exist; ensure the staged
        # __mnlmeta.json sidecar exists too (the loader needs it). Recompute scaling from the
        # built parquets if the meta is missing.
        for mode in ("singles", "couples"):
            if not (bp / f"{_STAGED_STEM}__{mode}.parquet").exists():
                raise SystemExit(f"STOP: --skip-build but staged engine-ready missing for "
                                 f"{mode}; run without --skip-build first.")
        if not (bp / f"{_STAGED_STEM}__mnlmeta.json").exists():
            write_staged_meta(bp, _scaling_from_parquet(bp, "singles"),
                              _scaling_from_parquet(bp, "couples"))

    # TASK 2
    s_struct, cert_s, stg_s = structure_gate(bp, "singles", 101)
    c_struct, cert_c, stg_c = structure_gate(bp, "couples", 901)

    # TASK 3
    s_blast, _ = blast_radius(cert_s, stg_s, "singles")
    c_blast, _ = blast_radius(cert_c, stg_c, "couples")

    structure_ok = s_struct["ok"] and c_struct["ok"]
    # ADDENDUM no-change control: every raw-UNCHANGED row must differ in c_norm ONLY through
    # the global c_scale denominator. A failure here is an UNINTENDED row-level change -> STOP.
    nochange_ok = bool(s_blast["no_change_control_pass"] and c_blast["no_change_control_pass"])

    # TASK 4 — only if structure + no-change control pass (else LL is not interpretable)
    if structure_ok and nochange_ok:
        ll = likelihood_parity(bp, s_blast["c_scale"], c_blast["c_scale"])
        ll_ok = ll["computable_with_certified_machinery"]
    elif not structure_ok:
        ll = {"skipped": True, "reason": "structure/row-order gate FAILED; STOP before LL"}
        ll_ok = False
    else:
        ll = {"skipped": True, "reason": "no-change control FAILED (raw-unchanged rows differ "
              "beyond the c_scale channel); STOP before LL"}
        ll_ok = False

    blast_quantified = all("raw_consumption" in b for b in (s_blast, c_blast))

    ready = bool(structure_ok and nochange_ok and ll_ok and blast_quantified)
    stop_reasons = []
    if not structure_ok:
        stop_reasons.append("structure/row-order gate FAIL")
    if not nochange_ok:
        stop_reasons.append("no-change control FAIL: raw-unchanged rows differ beyond the "
                            "c_scale denominator channel")
    if not ll_ok and structure_ok and nochange_ok:
        stop_reasons.append("likelihood not computable with certified machinery")
    if not blast_quantified:
        stop_reasons.append("blast radius not fully quantified")

    out = {
        "increment": "stage3b1_engine_ready_parity_v1",
        "no_welfare_finding": True, "measures_touched": ["W3_only"],
        "re_estimated": False, "ran_synthetic_recovery": False, "computed_v_dir": False,
        "priced_redrawn_node": False, "promoted_w3": False,
        "promoted_to_canonical": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "staged_stem": _STAGED_STEM, "certified_stem": _CERT_STEM,
        "staging_priced_dir": str(staged_priced_dir),
        "pinned_config": str(_PINNED_CONFIG),
        "certified_theta_hat": str(_CERT_THETA),
        "tol": TOL,
        "build_info": build_info,
        "task2_structure_gates": {"singles": s_struct, "couples": c_struct,
                                  "ok": structure_ok},
        "task3_blast_radius": {"singles": s_blast, "couples": c_blast,
                               "ok": blast_quantified},
        "task4_likelihood_parity": ll,
        "task5_readiness": {
            "ready_for_threeB2": ready,
            "requires": {
                "structure_row_order_pass": structure_ok,
                "no_unintended_field_changes": bool(structure_ok and nochange_ok),
                "no_change_control_pass": nochange_ok,
                "staged_LL_computable_at_certified_theta": ll_ok,
                "blast_radius_quantified": blast_quantified,
            },
            "stop_reasons": stop_reasons,
            "baseline_is_canonical": False,
            "production_swapped": False,
            "controlled_reestimation": "SEPARATE AUTHORISATION REQUIRED (Three-B2)",
            "welfare_computation_authorised": False,
        },
        "scope_statement": (
            "Assembles staged engine-ready and runs pre-estimation parity gates only. No "
            "re-estimation, no synthetic recovery, no V_i^dir, no redrawn pricing, no W^3 "
            "promotion, no production swap, no promotion to canonical. Staged engine-ready "
            "uses a distinct stem; certified files untouched."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)

    print(f"[three-B1] T2 structure: singles ok={s_struct['ok']} couples ok={c_struct['ok']}")
    for lbl, b in (("singles", s_blast), ("couples", c_blast)):
        rc = b["raw_consumption"]
        cn = b["c_norm_denominator_channel"]
        print(f"[three-B1] T3 {lbl}: raw-cons changed {rc['n_changed']}/{b['n_rows']} "
              f"({rc['share_changed']}) max={rc['max_abs']:.2f} | c_scale cert="
              f"{b['c_scale']['cert']:.4f} staged={b['c_scale']['staged']:.4f} "
              f"({b['c_scale']['pct_change']:+.4f}%) | no-change-control "
              f"pass={cn['no_change_control_pass']} (max_rel_resid={cn['max_rel_residual_vs_prediction']:.2e})")
    if not ll.get("skipped"):
        a = ll["regime_A_certified"]["joint_negLL"]
        bn = ll["regime_B_staged_native_cscale"]["joint_negLL"]
        cf = ll["regime_C_staged_fixed_cert_cscale"]["joint_negLL"]
        print(f"[three-B1] T4 joint negLL  A(cert)={a:.6f}  B(staged native)={bn:.6f}  "
              f"C(staged fixed-cscale)={cf:.6f}")
        print(f"[three-B1]   dLL total(B-A)={bn-a:+.6f}  raw(C-A)={cf-a:+.6f}  "
              f"c_scale(B-C)={bn-cf:+.6f}")
    print(f"[three-B1] T5 READY for Three-B2 = {ready}")
    if stop_reasons:
        print(f"[three-B1] STOP reasons: {stop_reasons}")
    print(f"[three-B1] wrote {args.out_json}")


if __name__ == "__main__":
    main()
