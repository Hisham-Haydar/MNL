"""
Joint-recovery test harness for the RURO pooled joint MNL.

Step 3a smoke-test only. Full recovery (Checks 1-6) is Step 3b and requires
separate authorization.

This harness tests the 49-parameter joint spec
(estimation_spec_joint_pooled_v1.yaml) against the pooled 2015-2017 singles +
couples engine-ready parquets. It validates that:

  - compute_likelihood_joint / compute_gradient_joint / compute_scores_joint
    all evaluate correctly at a generic theta_star derived from the joint spec.
  - The shared theta_star covers singles_male, singles_female, and couples via
    one common 49-element parameter vector.
  - cluster_ids are non-null on all three data objects.
  - The new occupation params (beta_occ_*_m / beta_occ_*_f) are present and the
    old marital-status-specific occupation params (beta_occ_*_sm / *_cf etc.)
    are absent.

Six scaffolded check stages are defined (Checks 1-6) but are NOT run at
smoke-test time; they require --run and separate authorization (Step 3b).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Give numba/BLAS the core budget BEFORE importing the engine.
_DEFAULT_THREADS = min(28, os.cpu_count() or 1)
os.environ.setdefault("NUMBA_NUM_THREADS", str(_DEFAULT_THREADS))

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

from _bpool_paths import bpool_dir          # noqa: E402
import estimation_spec_parser as sp         # noqa: E402
import estimation_utils as eu               # noqa: E402
import estimation_engine as ee              # noqa: E402


# ---------------------------------------------------------------------------
# NEW / OLD occupation param names — used by the smoke-test header check
# ---------------------------------------------------------------------------
_NEW_OCC_PARAMS = {
    "beta_occ_2_m", "beta_occ_3_m", "beta_occ_4_m",
    "beta_occ_2_f", "beta_occ_3_f", "beta_occ_4_f",
}
_OLD_OCC_PARAMS = {
    "beta_occ_2_sm", "beta_occ_3_sm", "beta_occ_4_sm",
    "beta_occ_2_sf", "beta_occ_3_sf", "beta_occ_4_sf",
    "beta_occ_2_cm", "beta_occ_3_cm", "beta_occ_4_cm",
    "beta_occ_2_cf", "beta_occ_3_cf", "beta_occ_4_cf",
}


# ---------------------------------------------------------------------------
# Shared theta* generation (reused from recovery_test.py, spec-agnostic)
# ---------------------------------------------------------------------------
def generate_theta_star(spec, rng, scale_perturb: float = 0.25,
                        shifter_frac: float = 0.12) -> np.ndarray:
    """
    Build a plausible, non-trivial, in-bounds theta* WITHOUT naming any parameter.

    Rule, per param, from (initial value v0, bounds [lo, hi]):
      - |v0| > eps  -> theta* = v0 * (1 + scale_perturb * s), s alternating +/-1.
      - v0 == 0     -> assign non-zero alternating-sign signal:
                       sign * shifter_frac * half-width-of-finite-bounds.
    Deterministic given rng seed; fully driven by the spec.
    """
    names = spec.all_param_names
    th = np.array([float(spec.initial_values.get(n, 0.0)) for n in names], dtype=float)
    bt = spec.get_bounds_tuple()
    eps = 1e-6
    sign = 1.0
    for i, n in enumerate(names):
        v0 = th[i]
        lo, hi = -np.inf, np.inf
        if bt and i < len(bt) and bt[i] is not None:
            lo = bt[i][0] if bt[i][0] is not None else -np.inf
            hi = bt[i][1] if bt[i][1] is not None else np.inf
        if abs(v0) > eps:
            val = v0 * (1.0 + scale_perturb * sign)
        else:
            half = 0.5 * (hi - lo) if (np.isfinite(hi) and np.isfinite(lo)) else 1.0
            val = sign * shifter_frac * half
        pad = 1e-6
        if np.isfinite(lo):
            val = max(val, lo + pad)
        if np.isfinite(hi):
            val = min(val, hi - pad)
        th[i] = val
        sign = -sign
    return th


# ---------------------------------------------------------------------------
# Vectorized synthetic-choice draw (Gumbel-max, no per-group loop)
# ---------------------------------------------------------------------------
def draw_synthetic_choice(V: np.ndarray, group_starts: np.ndarray,
                           group_ends: np.ndarray, rng) -> np.ndarray:
    """
    One draw per group from softmax(V), fully vectorized.
    Returns actual_choice (1.0 at drawn alt per group, else 0.0).
    """
    n = V.shape[0]
    g = np.repeat(np.arange(len(group_starts)), group_ends - group_starts)
    gumbel = -np.log(-np.log(rng.uniform(size=n)))
    key = V + gumbel
    order = np.lexsort((-key, g))
    g_sorted = g[order]
    first_in_group = np.ones(n, dtype=bool)
    first_in_group[1:] = g_sorted[1:] != g_sorted[:-1]
    chosen_global = order[first_in_group]
    out = np.zeros(n)
    out[chosen_global] = 1.0
    return out


# ---------------------------------------------------------------------------
# Numerical Hessian (central differences; columns independent)
# ---------------------------------------------------------------------------
def numerical_hessian(theta: np.ndarray, grad_func, eps: float = 1e-5,
                       workers: int = 1) -> np.ndarray:
    """
    Central-difference Hessian. Columns are independent finite-difference pairs.
    """
    from concurrent.futures import ThreadPoolExecutor
    n = len(theta)
    H = np.empty((n, n))

    def col(i):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        return i, (grad_func(tp) - grad_func(tm)) / (2 * eps)

    if workers and workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for i, c in ex.map(col, range(n)):
                H[:, i] = c
    else:
        for i in range(n):
            _, c = col(i)
            H[:, i] = c
    return 0.5 * (H + H.T)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
def _load_parquet_slice(stem: str, mode: str, years: list[int], n_hh: int,
                         sex: Optional[str] = None) -> tuple[pd.DataFrame, dict]:
    """
    Load an engine-ready parquet slice for mode in {singles, couples}.

    For mode=singles, `sex` ('male'|'female') filters by dgn BEFORE the HH
    sampling so n_hh counts unique households within the requested sex.
    """
    path = bpool_dir() / f"{stem}__{mode}.parquet"
    df = pd.read_parquet(path)
    if years:
        df = df[df["data_year"].isin(years)].copy()
    if mode == "singles" and sex is not None:
        flag = 1.0 if sex == "male" else 0.0
        df = df[df["dgn"] == flag].copy()

    draw_col = "draw" if mode == "singles" else "draw_joint"
    uids = pd.Series(df["stacked_hh_uid"].unique())
    if n_hh and n_hh < len(uids):
        uids = uids.iloc[:n_hh]
    df = (df[df["stacked_hh_uid"].isin(uids)]
          .sort_values(["idhh", draw_col])
          .reset_index(drop=True))

    meta_path = bpool_dir() / f"{stem}__mnlmeta.json"
    meta = json.load(open(meta_path))
    return df, meta


def build_data_objects(stem: str, years: list[int], n_hh: int):
    """
    Return (data_sm, data_sf, data_cou) for the joint estimation.

    n_hh is the per-group household count.
    """
    df_sm, meta = _load_parquet_slice(stem, "singles", years, n_hh, sex="male")
    df_sf, _ = _load_parquet_slice(stem, "singles", years, n_hh, sex="female")
    df_cou, _ = _load_parquet_slice(stem, "couples", years, n_hh)

    data_sm = eu.precompute_data_singles(df_sm, meta, is_male=True,
                                          include_wage_vars=True,
                                          include_loc_vars=True)
    data_sf = eu.precompute_data_singles(df_sf, meta, is_male=False,
                                          include_wage_vars=True,
                                          include_loc_vars=True)
    data_cou = eu.precompute_data_couples(df_cou, meta,
                                           include_wage_vars=True,
                                           include_loc_vars=True)
    return data_sm, data_sf, data_cou


# ---------------------------------------------------------------------------
# G3b / Hessian-identification helpers (3-state verdict; copied from recovery_test.py)
# ---------------------------------------------------------------------------
def _hessian_verdict(spec, H: np.ndarray):
    """
    Compute PD status, condition number, SEs, covariance, and eigenvector diagnostics.
    Returns a dict of results ready for printing / reporting.
    """
    pnames = spec.all_param_names
    H = 0.5 * (H + H.T)
    eig_w, eig_v = np.linalg.eigh(H)
    pd_ok = bool(np.all(eig_w > 0))
    cond = float(eig_w.max() / eig_w.min()) if eig_w.min() > 0 else float("inf")

    cov_caveat = None
    if pd_ok:
        cov = np.linalg.inv(H)
        d = np.diag(cov)
        se = np.where(d > 0, np.sqrt(np.maximum(d, 0.0)), np.nan)
    else:
        cov = np.linalg.pinv(H, hermitian=True, rcond=1e-10)
        d = np.diag(cov)
        se = np.where(d > 0, np.sqrt(d), np.nan)
        cov_caveat = ("Hessian non-PD; cov via pinv(rcond=1e-10). "
                      "SE=NaN on non-positive diagonal directions.")

    loading_thresh = 0.20
    bad_dirs = []
    for k in range(len(eig_w)):
        if eig_w[k] <= 0:
            v = eig_v[:, k]
            loaders = sorted(
                ((pnames[i], float(abs(v[i]))) for i in range(len(v))
                 if abs(v[i]) > loading_thresh),
                key=lambda kv: -kv[1])
            bad_dirs.append((float(eig_w[k]), loaders))

    # G3b: market-opportunity collinearity
    mkt = [s["coefficient"] for s in
           getattr(spec, "market_opportunity_shifters", []) or []]

    def _corr(a, b):
        if a not in pnames or b not in pnames:
            return np.nan
        ia = spec.get_param_index(a)
        ib = spec.get_param_index(b)
        daa, dbb = cov[ia, ia], cov[ib, ib]
        if daa > 0 and dbb > 0:
            return float(cov[ia, ib] / np.sqrt(daa * dbb))
        return np.nan

    pair_corrs = {f"{a}|{b}": _corr(a, b) for j, a in enumerate(mkt)
                  for b in mkt[j + 1:]}
    worst = max(
        ((abs(v), k) for k, v in pair_corrs.items() if np.isfinite(v)),
        default=(np.nan, None))

    if not pd_ok:
        first_loaders = bad_dirs[0][1] if bad_dirs and bad_dirs[0][1] else []
        loader_str = (", ".join(f"{n} ({w:.2f})" for n, w in first_loaders[:5])
                      if first_loaders else "no loadings above threshold")
        verdict_str = (f"NON-IDENTIFIED — Hessian non-PD "
                       f"({len(bad_dirs)} non-positive eigenvalue(s)); "
                       f"first bad direction loads on: {loader_str}")
    elif np.isfinite(worst[0]) and worst[0] > 0.9:
        verdict_str = f"NEAR-COLLINEAR at {worst[1]} (|corr| = {worst[0]:.3f})"
    else:
        verdict_str = "SEPARATELY IDENTIFIED"

    return dict(pd_ok=pd_ok, cond=cond, eig=eig_w, cov=cov, se=se,
                bad_dirs=bad_dirs, pair_corrs=pair_corrs, worst=worst,
                cov_caveat=cov_caveat, verdict_str=verdict_str)


# ===========================================================================
# CHECK 1 — Synthetic DGP from shared theta
# ===========================================================================
def run_synthetic_dgp(spec, data_sm, data_sf, data_cou, theta_star,
                       rng) -> tuple:
    """
    CHECK 1 (SCAFFOLDED — Step 3b).

    Generate synthetic choices for all three groups under theta_star using
    the PRODUCTION choice sets (singles: 101 alts, couples: 901 alts).
    Returns copies of the three data objects with synthetic actual_choice
    arrays installed.

    The theta_star must use ONE shared opportunity block across all groups;
    this is guaranteed by generate_theta_star operating on the joint spec.
    """
    import copy

    def _draw_for(data, theta, spec_obj, rng_obj):
        comp = ee.compute_likelihood_singles(theta, data, spec_obj,
                                             return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_obj)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    def _draw_for_cou(data, theta, spec_obj, rng_obj):
        comp = ee.compute_likelihood_couples(theta, data, spec_obj,
                                              return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_obj)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    sm2 = _draw_for(data_sm, theta_star, spec, rng)
    sf2 = _draw_for(data_sf, theta_star, spec, rng)
    cou2 = _draw_for_cou(data_cou, theta_star, spec, rng)

    print(f"  [CHECK 1] synthetic chosen alts: "
          f"sm={int(sm2.actual_choice.sum())} "
          f"sf={int(sf2.actual_choice.sum())} "
          f"cou={int(cou2.actual_choice.sum())}")
    return sm2, sf2, cou2


# ===========================================================================
# CHECK 2 — Shared-from-pooled recovery
# ===========================================================================
def run_shared_recovery(spec, data_sm, data_sf, data_cou, theta_star,
                         solver: str = "scipy") -> dict:
    """
    CHECK 2 (SCAFFOLDED — Step 3b).

    Re-estimate from pooled joint likelihood (compute_likelihood_joint) and
    assess recovery of the 29 shared parameters:

      max|theta_hat - theta_star| on shared param subset.

    Shared params are all params that appear in spec.all_param_names but
    whose name does NOT carry a group-specific suffix (_sm, _sf, _m, _f).

    Does NOT run the optimizer at smoke-test time.  Call explicitly with
    --run after Step 3b authorization.
    """
    raise NotImplementedError(
        "run_shared_recovery is Step 3b — requires separate authorization. "
        "Call with --run after explicit approval."
    )


# ===========================================================================
# CHECK 3 — Group-specific recovery
# ===========================================================================
def run_group_specific_recovery(spec, data_sm, data_sf, data_cou,
                                  theta_star, theta_hat,
                                  solver: str = "scipy") -> dict:
    """
    CHECK 3 (SCAFFOLDED — Step 3b).

    Assess recovery of the 20 group-specific preference parameters:
      - Singles-male leisure block (_sm suffix + theta_c_singles)
      - Singles-female leisure block (_sf suffix)
      - Couples leisure blocks (_m, _f suffixes) + beta_ll

    If beta_ll recovery fails under pooled DGP, flag §5 fallback:
    couples-only estimation for the interaction parameter.

    Does NOT run at smoke-test time.
    """
    raise NotImplementedError(
        "run_group_specific_recovery is Step 3b — requires separate authorization."
    )


# ===========================================================================
# CHECK 4 — Two-start agreement
# ===========================================================================
def run_two_start_agreement(spec, data_sm, data_sf, data_cou, theta_star,
                              solver: str = "scipy") -> dict:
    """
    CHECK 4 (SCAFFOLDED — Step 3b).

    Run optimizer from two starts:
      warm = theta_star   (should converge to the DGP value)
      cold = spec initial values

    Check full 49-vector agreement: max|theta_warm - theta_cold|.
    No inert params are expected in the joint spec (all params have
    cross-group identification via the pooled likelihood).

    Does NOT run at smoke-test time.
    """
    raise NotImplementedError(
        "run_two_start_agreement is Step 3b — requires separate authorization."
    )


# ===========================================================================
# CHECK 5 — Hessian identification
# ===========================================================================
def run_hessian_check(theta_hat: np.ndarray, grad_func, spec,
                       hess_workers: int = 1) -> dict:
    """
    CHECK 5 (SCAFFOLDED — Step 3b).

    Compute the numerical Hessian at theta_hat and apply the 3-state G3b
    verdict (copied logic from recovery_test.py):
      - IDENTIFIED       : Hessian is PD
      - NEAR-COLLINEAR   : PD but worst market-opp |corr| > 0.9
      - NON-IDENTIFIED   : Hessian non-PD (real joint identification failure;
                           NOT expected inert-param slice behavior)

    Non-PD here is a genuine joint ID failure, not a slice artefact.

    Does NOT run at smoke-test time.
    """
    raise NotImplementedError(
        "run_hessian_check is Step 3b — requires separate authorization."
    )


# ===========================================================================
# CHECK 6 — Contamination characterization
# ===========================================================================
def run_contamination_check(spec, data_sm, data_sf, data_cou, theta_star,
                              theta_hat, solver: str = "scipy") -> dict:
    """
    CHECK 6 (SCAFFOLDED — Step 3b).

    Perturb one group's leisure parameters in theta_star and re-estimate
    forcing the shared opportunity block g.  Report shared-param movement
    (not welfare decomposition).

    # HOOK: welfare decomposition shares — add here in Step 4

    Does NOT run at smoke-test time.
    """
    raise NotImplementedError(
        "run_contamination_check is Step 3b — requires separate authorization."
    )


# ===========================================================================
# SMOKE TEST
# ===========================================================================
def run_smoke_test(args, spec) -> bool:
    """
    Load n_hh households per group, build precomputed data, generate theta_star,
    evaluate LL / gradient / scores at theta_star, and print a PASS/FAIL table.

    Does NOT launch the optimizer and does NOT produce estimation outputs.
    Returns True if all checks pass.
    """
    print("\n" + "=" * 72)
    print("JOINT RECOVERY SMOKE TEST  (Step 3a)")
    print("=" * 72)
    print(f"  spec   : {getattr(spec, 'name', '?')}  ({len(spec.all_param_names)} params)")
    print(f"  stem   : {args.engine_ready_stem}")
    print(f"  years  : {args.years}")
    print(f"  n_hh   : {args.n_hh} per group")
    print(f"  seed   : {args.seed}")

    rng = np.random.default_rng(args.seed)
    years = ([] if args.years.strip().lower() == "all"
             else [int(y) for y in args.years.split(",")])
    pnames = spec.all_param_names

    checks: list[tuple[str, bool, str]] = []

    # ------------------------------------------------------------------
    # C0: param-vector header checks
    # ------------------------------------------------------------------
    n_params = len(pnames)
    new_present = _NEW_OCC_PARAMS.issubset(set(pnames))
    old_absent = _OLD_OCC_PARAMS.isdisjoint(set(pnames))

    checks.append(("n_params == 49", n_params == 49,
                   f"got {n_params}"))
    checks.append(("new occ params present",  new_present,
                   f"missing: {_NEW_OCC_PARAMS - set(pnames)}"))
    checks.append(("old occ params absent", old_absent,
                   f"still present: {_OLD_OCC_PARAMS & set(pnames)}"))

    # ------------------------------------------------------------------
    # C1: load data
    # ------------------------------------------------------------------
    print(f"\nLoading data ({args.n_hh} HH per group) ...")
    t0 = time.time()
    try:
        data_sm, data_sf, data_cou = build_data_objects(
            args.engine_ready_stem, years, args.n_hh)
        load_ok = True
        load_msg = (f"sm={data_sm.n_groups} sf={data_sf.n_groups} "
                    f"cou={data_cou.n_groups} groups  "
                    f"[{time.time()-t0:.1f}s]")
    except Exception as exc:
        load_ok = False
        load_msg = str(exc)
        data_sm = data_sf = data_cou = None

    checks.append(("data objects load", load_ok, load_msg))
    if not load_ok:
        _print_table(checks)
        return False

    print(f"  {load_msg}")

    # ------------------------------------------------------------------
    # C2: cluster_ids non-null on all data objects
    # ------------------------------------------------------------------
    def _cids_ok(d, label):
        if d is None:
            return False, f"{label}: data is None"
        if d.cluster_ids is None or len(d.cluster_ids) == 0:
            return False, f"{label}: cluster_ids is None/empty"
        if np.any(np.isnan(d.cluster_ids.astype(float))):
            return False, f"{label}: cluster_ids contains NaN"
        return True, f"{label}: {len(d.cluster_ids)} ids OK"

    ok_sm, msg_sm = _cids_ok(data_sm, "singles_male")
    ok_sf, msg_sf = _cids_ok(data_sf, "singles_female")
    ok_cou, msg_cou = _cids_ok(data_cou, "couples")
    checks.append(("cluster_ids non-null (sm)", ok_sm, msg_sm))
    checks.append(("cluster_ids non-null (sf)", ok_sf, msg_sf))
    checks.append(("cluster_ids non-null (cou)", ok_cou, msg_cou))

    # ------------------------------------------------------------------
    # C3: generate theta_star
    # ------------------------------------------------------------------
    theta_star = generate_theta_star(spec, rng)
    ts_ok = (len(theta_star) == n_params
             and np.all(np.isfinite(theta_star)))
    checks.append(("theta_star finite", ts_ok,
                   f"len={len(theta_star)} n_nonzero="
                   f"{int(np.sum(np.abs(theta_star) > 1e-8))}"))

    if not ts_ok:
        _print_table(checks)
        return False

    # ------------------------------------------------------------------
    # C4: compute_likelihood_joint at theta_star
    # ------------------------------------------------------------------
    try:
        ll_val = ee.compute_likelihood_joint(
            theta_star, data_sm, data_sf, data_cou, spec)
        ll_ok = np.isfinite(ll_val)
        ll_msg = f"negLL={ll_val:.6f}"
    except Exception as exc:
        ll_ok = False
        ll_msg = str(exc)
    checks.append(("compute_likelihood_joint finite", ll_ok, ll_msg))

    # ------------------------------------------------------------------
    # C5: compute_gradient_joint at theta_star
    # ------------------------------------------------------------------
    try:
        grad_val = ee.compute_gradient_joint(
            theta_star, data_sm, data_sf, data_cou, spec)
        grad_ok = (grad_val is not None
                   and len(grad_val) == n_params
                   and np.all(np.isfinite(grad_val)))
        grad_msg = (f"shape={grad_val.shape} "
                    f"max|g|={np.max(np.abs(grad_val)):.3e}")
    except Exception as exc:
        grad_ok = False
        grad_msg = str(exc)
    checks.append(("compute_gradient_joint finite", grad_ok, grad_msg))

    # ------------------------------------------------------------------
    # C6: compute_scores_joint at theta_star — finite + aligned cluster_ids
    # ------------------------------------------------------------------
    try:
        scores_all, cids_all = ee.compute_scores_joint(
            theta_star, data_sm, data_sf, data_cou, spec)
        n_groups_total = (data_sm.n_groups + data_sf.n_groups
                          + data_cou.n_groups)
        scores_shape_ok = (scores_all.shape == (n_groups_total, n_params))
        scores_finite = np.all(np.isfinite(scores_all))
        cids_aligned = (len(cids_all) == n_groups_total)
        scores_ok = scores_shape_ok and scores_finite and cids_aligned
        scores_msg = (f"shape={scores_all.shape} "
                      f"finite={scores_finite} "
                      f"cids_len={len(cids_all)} "
                      f"expected_groups={n_groups_total}")
    except Exception as exc:
        scores_ok = False
        scores_msg = str(exc)
    checks.append(("compute_scores_joint finite+aligned", scores_ok, scores_msg))

    # ------------------------------------------------------------------
    # C7: sign consistency T1  sum(scores) == -gradient
    # ------------------------------------------------------------------
    if grad_ok and scores_ok:
        try:
            score_sum = scores_all.sum(axis=0)
            neg_grad = -grad_val
            max_diff = float(np.max(np.abs(score_sum - neg_grad)))
            t1_ok = max_diff < 1e-6
            t1_msg = f"max|score_sum - (-grad)|={max_diff:.3e}"
        except Exception as exc:
            t1_ok = False
            t1_msg = str(exc)
    else:
        t1_ok = False
        t1_msg = "skipped (upstream check failed)"
    checks.append(("T1 score_sum == -gradient", t1_ok, t1_msg))

    # ------------------------------------------------------------------
    # Print table and verdict
    # ------------------------------------------------------------------
    _print_table(checks)
    all_pass = all(ok for _, ok, _ in checks)
    print()
    if all_pass:
        print("SMOKE TEST PASSED")
    else:
        n_fail = sum(1 for _, ok, _ in checks if not ok)
        print(f"SMOKE TEST FAILED ({n_fail} check(s) failed — see table above)")
    print("=" * 72)
    return all_pass


def _print_table(checks: list[tuple[str, bool, str]]) -> None:
    print()
    w = max(len(c[0]) for c in checks) + 2
    print(f"  {'Check':<{w}} {'Result':<8}  Detail")
    print("  " + "-" * (w + 8 + 40))
    for name, ok, detail in checks:
        result = "PASS" if ok else "FAIL"
        print(f"  {name:<{w}} {result:<8}  {detail}")


# ===========================================================================
# CLI
# ===========================================================================
def _default_spec() -> Path:
    return (_script_dir / "specs" / "estimation_spec_joint_pooled_v1.yaml")


def _default_report() -> Path:
    return (Path("U:/Desktop/Nizam_Hisham/MNL/docs/France_case/P3a/"
                 "execution_logs/Bpool")
            / "joint_recovery_smoke_test_results.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path, default=_default_spec(),
                    help="Joint estimation spec YAML (default: joint_pooled_v1)")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_d1w1",
                    help="Stem of the engine-ready parquets: "
                         "{stem}__singles.parquet, {stem}__couples.parquet, "
                         "{stem}__mnlmeta.json  (resolved under bpool_dir())")
    ap.add_argument("--years", default="2015,2016,2017",
                    help="Comma-separated data years or 'all' (default: 2015,2016,2017)")
    ap.add_argument("--n-hh", type=int, default=100,
                    help="Households per group to load for the smoke test (default: 100)")
    ap.add_argument("--seed", type=int, default=20260530,
                    help="RNG seed for theta_star generation and synthetic draws")
    ap.add_argument("--solver", default="scipy",
                    choices=["scipy", "scipy-trustconstr", "gamspy-conopt"],
                    help="Optimizer for full recovery runs (Step 3b only)")
    ap.add_argument("--starts", default="warm,cold",
                    help="Comma-separated start points for full recovery: warm,cold")
    ap.add_argument("--threads", type=int, default=_DEFAULT_THREADS,
                    help="numba threads for per-household LL/gradient")
    ap.add_argument("--report", type=Path, default=_default_report(),
                    help="Output path for the Markdown report")
    ap.add_argument("--smoke", action="store_true",
                    help="Run the smoke test (Step 3a). "
                         "Full Checks 1-6 require --run (Step 3b).")
    ap.add_argument("--run", action="store_true",
                    help="Run full recovery checks 1-6 (Step 3b; requires authorization).")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # Python < 3.7 or non-text-mode stdout

    # numba thread setup
    if hasattr(ee, "HAS_NUMBA") and ee.HAS_NUMBA:
        try:
            import numba
            numba.set_num_threads(max(1, args.threads))
            print(f"numba threads: {numba.get_num_threads()}")
        except Exception as _e:
            print(f"numba thread set skipped: {_e}")
    else:
        print("numba not available — vectorized single-process (BLAS-threaded)")

    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    print(f"spec '{getattr(spec, 'name', '?')}': {len(pnames)} params")

    if args.run:
        print("\nFull recovery (Checks 1-6) is Step 3b and requires separate "
              "authorization. Scaffolded stubs are present but raise "
              "NotImplementedError until authorization is granted.")
        sys.exit(0)

    if args.smoke:
        ok = run_smoke_test(args, spec)
        sys.exit(0 if ok else 1)

    # Default: print usage guidance
    print("\nUsage:")
    print("  --smoke   Run the Step 3a smoke test (loads data, checks LL/grad/scores).")
    print("  --run     Full recovery (Step 3b) — requires separate authorization.")
    print("\nExample smoke test:")
    print(f'  python "{Path(__file__)}" --smoke --n-hh 100 --years 2015,2016,2017')
    print("\nTo run in a terminal with live output:")
    _py = r"C:\Users\hisham\Repo\MNL\.venv\Scripts\python.exe"
    print(f'  & "{_py}" -u "{Path(__file__)}" --smoke '
          f'--engine-ready-stem {args.engine_ready_stem} '
          f'--n-hh {args.n_hh} --years {args.years}')


if __name__ == "__main__":
    main()
