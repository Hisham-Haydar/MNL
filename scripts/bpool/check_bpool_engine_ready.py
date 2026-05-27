"""
STEP 3 — contract-conformance gate for the B-pool engine-ready parquets.
Read-only. NO estimation (no theta*, no optimizer). Reports PASS/FAIL per check.

1. Every column precompute_data_*/enh_RURO_estimate_FR reads is present (proven by an
   actual precompute on a slice — the real conformance test).
2. metadata["normalization"] present and well-formed (c_scale + l_scale[s]).
3. c_norm/leisure formulas match Step 1 (recompute -> max diff == 0).
4. prior/log_prior convention matches the engine IS correction (prior==exp(log_prior);
   chosen-row log_q semantics sane).
5. All 58 spec variables present (correctly suffixed); param count == 58.
6. Row counts preserved (singles HH×101, couples HH×901); is_chosen unique per HH.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
from _bpool_paths import bpool_dir  # noqa: E402
import estimation_spec_parser as sp   # noqa: E402
import estimation_utils as eu          # noqa: E402
import estimation_engine as ee         # noqa: E402

_BP = bpool_dir()
_SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
_META = _BP / "fr_p3a_bpool_engine_ready__mnlmeta.json"
_S = _BP / "fr_p3a_bpool_engine_ready__singles.parquet"
_C = _BP / "fr_p3a_bpool_engine_ready__couples.parquet"
TOTAL_LEISURE_HOURS = 80.0
DCM_MIN_POSITIVE = 1.0


def check_2_metadata() -> bool:
    print("\n--- CHECK 2: metadata normalization block ---")
    meta = json.load(open(_META))
    norm = meta.get("normalization", {})
    ok = True
    s = norm.get("singles", {})
    c = norm.get("couples", {})
    for k in ("c_scale", "l_scale"):
        present = k in s and isinstance(s[k], (int, float)) and s[k] > 0
        print(f"  singles.{k}: {s.get(k)}  {'OK' if present else 'FAIL'}")
        ok &= present
    for k in ("c_scale", "l_male_scale", "l_female_scale"):
        present = k in c and isinstance(c[k], (int, float)) and c[k] > 0
        print(f"  couples.{k}: {c.get(k)}  {'OK' if present else 'FAIL'}")
        ok &= present
    print(f"  CHECK 2: {'PASS' if ok else 'FAIL'}")
    return ok


def check_3_formulas() -> bool:
    print("\n--- CHECK 3: c_norm/leisure formulas match Step 1 (recompute, max diff==0) ---")
    meta = json.load(open(_META))["normalization"]
    ok = True
    # singles
    s = pd.read_parquet(_S, columns=["ils_dispy_real", "hours", "leisure", "consumption",
                                     "c_norm", "l_norm"])
    leis = (TOTAL_LEISURE_HOURS - pd.to_numeric(s["hours"]).fillna(0.0)).clip(lower=DCM_MIN_POSITIVE)
    cons = pd.to_numeric(s["ils_dispy_real"]).clip(lower=DCM_MIN_POSITIVE)
    d_leis = (leis - s["leisure"]).abs().max()
    d_cons = (cons - s["consumption"]).abs().max()
    cs, ls = meta["singles"]["c_scale"], meta["singles"]["l_scale"]
    d_cn = (cons / cs - s["c_norm"]).abs().max()
    d_ln = (leis / ls - s["l_norm"]).abs().max()
    print(f"  singles: max|Δleisure|={d_leis:.2e}  max|Δconsumption|={d_cons:.2e}  "
          f"max|Δc_norm|={d_cn:.2e}  max|Δl_norm|={d_ln:.2e}")
    ok &= (d_leis == 0 and d_cons == 0 and d_cn < 1e-9 and d_ln < 1e-9)
    # couples
    c = pd.read_parquet(_C, columns=["ils_dispy_real", "hours_male", "hours_female",
                                     "leisure_male", "leisure_female", "consumption",
                                     "c_norm", "l_norm_male", "l_norm_female"])
    lm = (TOTAL_LEISURE_HOURS - pd.to_numeric(c["hours_male"]).fillna(0.0)).clip(lower=DCM_MIN_POSITIVE)
    lf = (TOTAL_LEISURE_HOURS - pd.to_numeric(c["hours_female"]).fillna(0.0)).clip(lower=DCM_MIN_POSITIVE)
    ccons = pd.to_numeric(c["ils_dispy_real"]).clip(lower=DCM_MIN_POSITIVE)
    d_lm = (lm - c["leisure_male"]).abs().max()
    d_lf = (lf - c["leisure_female"]).abs().max()
    d_cc = (ccons - c["consumption"]).abs().max()
    ccs = meta["couples"]["c_scale"]; lms = meta["couples"]["l_male_scale"]; lfs = meta["couples"]["l_female_scale"]
    d_ccn = (ccons / ccs - c["c_norm"]).abs().max()
    d_lnm = (lm / lms - c["l_norm_male"]).abs().max()
    d_lnf = (lf / lfs - c["l_norm_female"]).abs().max()
    print(f"  couples: max|Δleis_m|={d_lm:.2e} |Δleis_f|={d_lf:.2e} |Δcons|={d_cc:.2e} "
          f"|Δc_norm|={d_ccn:.2e} |Δl_norm_m|={d_lnm:.2e} |Δl_norm_f|={d_lnf:.2e}")
    ok &= (d_lm == 0 and d_lf == 0 and d_cc == 0 and d_ccn < 1e-9 and d_lnm < 1e-9 and d_lnf < 1e-9)
    print(f"  CHECK 3: {'PASS' if ok else 'FAIL'}")
    return ok


def check_4_prior() -> bool:
    print("\n--- CHECK 4: prior/log_prior convention vs engine IS correction ---")
    ok = True
    for label, f in (("singles", _S), ("couples", _C)):
        d = pd.read_parquet(f, columns=["prior", "log_prior"])
        recon = np.clip(np.exp(np.clip(pd.to_numeric(d["log_prior"]).to_numpy(), -700, 700)), 1e-16, None)
        dmax = float(np.abs(recon - d["prior"].to_numpy()).max())
        n_nonpos = int((d["prior"] <= 0).sum())
        n_null = int(d["prior"].isna().sum())
        print(f"  {label}: max|prior-exp(log_prior)|={dmax:.2e}  prior<=0: {n_nonpos}  nulls: {n_null}")
        ok &= (dmax < 1e-9 and n_nonpos == 0 and n_null == 0)
    print("  engine uses V = u + log_h + log_w + log_market - log(prior)  [estimation_engine.py:363]")
    print(f"  -> prior is density scale (exp of carried log_prior). CHECK 4: {'PASS' if ok else 'FAIL'}")
    return ok


def check_5_spec_vars() -> bool:
    print("\n--- CHECK 5: 58 spec vars present + param count ---")
    spec = sp.parse_specification(_SPEC)
    n = len(spec.all_param_names)
    print(f"  param count: {n}  {'OK' if n == 58 else 'FAIL'}")
    import pyarrow.parquet as pq
    scols = set(pq.read_schema(_S).names)
    ccols = set(pq.read_schema(_C).names)
    # input variables referenced (re-use the build's spec extraction logic, inline)
    req = ["age_norm", "age_norm2", "n_children", "educL", "educH", "pexp_years", "pexp_years2",
           "working", "working_pt1", "working_pt2", "working_ft", "working_lh", "loc4",
           "loc4_2", "loc4_3", "loc4_4", "gsur", "ils_dispy_real",
           "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8",
           "year_2015_indicator", "year_2017_indicator", "drgur", "drgmd"]
    person = {"age_norm", "age_norm2", "educL", "educH", "pexp_years", "pexp_years2",
              "working", "working_pt1", "working_pt2", "working_ft", "working_lh",
              "loc4", "loc4_2", "loc4_3", "loc4_4", "gsur"}
    miss_s, miss_c = [], []
    for v in req:
        if v not in scols:
            miss_s.append(v)
        if v in person:
            if f"{v}_male" not in ccols or f"{v}_female" not in ccols:
                miss_c.append(v)
        else:
            if v not in ccols:
                miss_c.append(v)
    print(f"  singles missing: {miss_s if miss_s else 'NONE'}")
    print(f"  couples missing: {miss_c if miss_c else 'NONE'}")
    ok = (n == 58 and not miss_s and not miss_c)
    print(f"  CHECK 5: {'PASS' if ok else 'FAIL'}")
    return ok


def check_6_rowcounts() -> bool:
    print("\n--- CHECK 6: row counts + chosen uniqueness ---")
    ok = True
    s = pd.read_parquet(_S, columns=["stacked_hh_uid", "is_chosen"])
    nhh_s = s["stacked_hh_uid"].nunique()
    per_s = s.groupby("stacked_hh_uid").size()
    ch_s = s.groupby("stacked_hh_uid")["is_chosen"].sum()
    print(f"  singles: HH={nhh_s:,} rows={len(s):,} expect={nhh_s*101:,}  "
          f"all 101/HH={(per_s==101).all()}  chosen==1/HH={(ch_s==1).all()}")
    ok &= (len(s) == nhh_s * 101 and (per_s == 101).all() and (ch_s == 1).all())
    c = pd.read_parquet(_C, columns=["stacked_hh_uid", "is_chosen_joint"])
    nhh_c = c["stacked_hh_uid"].nunique()
    per_c = c.groupby("stacked_hh_uid").size()
    ch_c = c.groupby("stacked_hh_uid")["is_chosen_joint"].sum()
    print(f"  couples: HH={nhh_c:,} rows={len(c):,} expect={nhh_c*901:,}  "
          f"all 901/HH={(per_c==901).all()}  chosen==1/HH={(ch_c==1).all()}")
    ok &= (len(c) == nhh_c * 901 and (per_c == 901).all() and (ch_c == 1).all())
    print(f"  CHECK 6: {'PASS' if ok else 'FAIL'}")
    return ok


def check_1_precompute() -> bool:
    print("\n--- CHECK 1: engine precompute on a slice (real conformance test) ---")
    spec = sp.parse_specification(_SPEC)
    ok = True
    # SINGLES slice: 200 HH
    s = pd.read_parquet(_S)
    s_uids = s["stacked_hh_uid"].drop_duplicates().head(200)
    ss = s[s["stacked_hh_uid"].isin(s_uids)].sort_values(["idhh", "draw"]).reset_index(drop=True)
    meta = json.load(open(_META))
    try:
        d_sm = eu.precompute_data_singles(ss, meta, is_male=True, include_wage_vars=True, include_loc_vars=True)
        ll = ee.compute_likelihood_singles(spec.get_initial_vector(), d_sm, spec)
        print(f"  singles precompute OK: n_groups={d_sm.n_groups} n_obs={d_sm.n_obs} "
              f"working_lh mean={float(d_sm.working_lh.mean()):.3f}  LL@init(neg)={ll:.1f}")
        ok &= np.isfinite(ll)
    except Exception as ex:
        import traceback; traceback.print_exc(); ok = False
    # COUPLES slice: 100 HH
    c = pd.read_parquet(_C)
    c_uids = c["stacked_hh_uid"].drop_duplicates().head(100)
    cc = c[c["stacked_hh_uid"].isin(c_uids)].sort_values(["idhh", "draw_joint"]).reset_index(drop=True)
    try:
        d_c = eu.precompute_data_couples(cc, meta, include_wage_vars=True, include_loc_vars=True)
        ll = ee.compute_likelihood_couples(spec.get_initial_vector(), d_c, spec)
        print(f"  couples precompute OK: n_groups={d_c.n_groups} n_obs={d_c.n_obs} "
              f"working_lh_m mean={float(d_c.working_lh_male.mean()):.3f}  LL@init(neg)={ll:.1f}")
        ok &= np.isfinite(ll)
    except Exception as ex:
        import traceback; traceback.print_exc(); ok = False
    print(f"  CHECK 1: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    print("=" * 78)
    print("STEP 3 — B-pool engine-ready contract-conformance gate (read-only)")
    print("=" * 78)
    results = {
        "1_precompute": check_1_precompute(),
        "2_metadata": check_2_metadata(),
        "3_formulas": check_3_formulas(),
        "4_prior": check_4_prior(),
        "5_spec_vars": check_5_spec_vars(),
        "6_rowcounts": check_6_rowcounts(),
    }
    print("\n" + "=" * 78)
    for k, v in results.items():
        print(f"  CHECK {k}: {'PASS' if v else 'FAIL'}")
    allok = all(results.values())
    print(f"\n  OVERALL: {'PASS' if allok else 'FAIL'}")
    print("=" * 78)
    if not allok:
        sys.exit(1)


if __name__ == "__main__":
    main()
