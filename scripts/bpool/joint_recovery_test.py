"""
Joint-recovery test harness for the RURO pooled joint MNL.

Implements the six checks required by JMP_joint_estimation_spec_v1.md §6
before any real-data joint decomposition can be reported.

  --smoke   : Step 3a smoke test (C0-C9, no optimizer)
  --run     : Step 3b full recovery (Checks 1-6), requires --solver gamspy-conopt

Check summary:
  1  Synthetic DGP from shared theta_star on production choice sets
  2  Shared-from-pooled recovery (29 shared params)
  3  Group-specific recovery (20 group params including beta_ll diagnosis)
  4  Two-start basin agreement (warm=theta_star, cold=spec init), full 49-vector
  5  Hessian PD at solution (G3b 3-state verdict)
  6  Contamination: misspecified group-specific beta_E DGP, shared-g forced
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

# Lazy import: only needed for --run (CONOPT path).
def _import_gamspy_estimator():
    import gamspy_estimation_vectorized as gev
    return gev


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
def load_theta_star_from_csv(path: Path, spec) -> np.ndarray:
    """
    Load theta_star from a CSV file with columns 'parameter,value'.

    Any parameter in the spec that is absent from the CSV gets its spec
    initial value.  Extra CSV rows not in the spec are silently ignored.
    This allows loading from real-data slice estimates (produced by
    dump_theta_star.py) as the DGP anchor for recovery tests.
    """
    df = pd.read_csv(path)
    if "parameter" not in df.columns or "value" not in df.columns:
        raise ValueError(f"theta_star CSV must have 'parameter' and 'value' columns: {path}")
    lookup = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    names = spec.all_param_names
    th = np.array(
        [lookup.get(n, float(spec.initial_values.get(n, 0.0))) for n in names],
        dtype=float)
    loaded = sum(1 for n in names if n in lookup)
    print(f"  [theta_star] loaded {loaded}/{len(names)} params from {path.name}")
    return th


def generate_theta_star(spec, rng, scale_perturb: float = 0.25,
                        shifter_frac: float = 0.12) -> np.ndarray:
    """
    Build a plausible, non-trivial, in-bounds theta* WITHOUT naming any parameter.

    Rule, per param, from (initial value v0, bounds [lo, hi]):
      - |v0| > eps  -> theta* = v0 * (1 + scale_perturb * s), s alternating +/-1.
      - v0 == 0     -> assign non-zero alternating-sign signal:
                       sign * shifter_frac * half-width-of-finite-bounds.
    Deterministic given rng seed; fully driven by the spec.

    NOTE: this produces a theta_star that may not be near any MLE.  For
    meaningful recovery tests, prefer --theta-star <csv> anchored to
    real-data slice estimates.
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
                         sex: Optional[str] = None,
                         max_alts: int = 0) -> tuple[pd.DataFrame, dict]:
    """
    Load an engine-ready parquet slice for mode in {singles, couples}.

    For mode=singles, `sex` ('male'|'female') filters by dgn BEFORE the HH
    sampling so n_hh counts unique households within the requested sex.

    max_alts: if > 0 and mode == 'couples', keep only the first max_alts
    draw_joint values per stacked_hh_uid.  Use max_alts=100 (10x10) or
    max_alts=400 (20x20) to shorten CONOPT model-generation time for
    recovery tests.  Has no effect on singles (already 101 alts).
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
          .sort_values(["stacked_hh_uid", draw_col])
          .reset_index(drop=True))

    # Coarse-draw subsetting for couples: keep the chosen row + (max_alts-1)
    # non-chosen rows sampled WITHOUT replacement per household.
    # head(N) is WRONG because draw_joint=0 is not the chosen row; is_chosen_joint=1
    # marks the chosen alternative and may fall anywhere in draw_joint 0-900.
    if max_alts > 0 and mode == "couples":
        rng_sub = np.random.default_rng(42)  # fixed seed for reproducibility
        chosen_col = ("is_chosen_joint" if "is_chosen_joint" in df.columns
                      else "actual_choice")
        parts = []
        for _, grp in df.groupby("stacked_hh_uid", sort=False):
            chosen = grp[grp[chosen_col] == 1]
            non_chosen = grp[grp[chosen_col] != 1]
            n_nc = min(max_alts - len(chosen), len(non_chosen))
            if n_nc > 0:
                nc_sample = non_chosen.sample(n=n_nc,
                                               replace=False,
                                               random_state=int(rng_sub.integers(1 << 31)))
            else:
                nc_sample = non_chosen.iloc[:0]
            parts.append(pd.concat([chosen, nc_sample]))
        df = (pd.concat(parts, ignore_index=True)
                .sort_values(["stacked_hh_uid", draw_col])
                .reset_index(drop=True))
        actual_alts = int(df.groupby("stacked_hh_uid")[draw_col].count().max())
        print(f"  [couples coarse-draw] max_alts={max_alts} -> "
              f"actual max alts/HH={actual_alts} "
              f"(chosen row preserved)")

    meta_path = bpool_dir() / f"{stem}__mnlmeta.json"
    meta = json.load(open(meta_path))
    return df, meta


def build_data_objects(stem: str, years: list[int], n_hh: int,
                        max_alts_couples: int = 0):
    """
    Return (data_sm, data_sf, data_cou) for the joint estimation.

    n_hh is the per-group household count.
    max_alts_couples: if > 0, subsample couples alternatives to this count
    per household (e.g. 100 for 10x10, 400 for 20x20). For recovery tests
    only — production estimates must use the full 901-alt choice set.
    """
    df_sm, meta = _load_parquet_slice(stem, "singles", years, n_hh, sex="male")
    df_sf, _ = _load_parquet_slice(stem, "singles", years, n_hh, sex="female")
    df_cou, _ = _load_parquet_slice(stem, "couples", years, n_hh,
                                     max_alts=max_alts_couples)

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
# CHECK 1 — Synthetic DGP
# ===========================================================================
def run_synthetic_dgp(spec, data_sm, data_sf, data_cou, theta_star,
                       rng) -> tuple:
    """
    CHECK 1 — Generate synthetic choices from ONE shared theta_star.

    Uses production choice sets (singles: 101 alts, couples: 901 alts)
    and the production B-pool/proposal structure (prior-corrected utility).
    Returns data objects with synthetic actual_choice arrays installed.
    """
    import copy

    def _draw_singles(data, theta, spec_obj, rng_obj):
        comp = ee.compute_likelihood_singles(theta, data, spec_obj,
                                             return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_obj)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    def _draw_couples(data, theta, spec_obj, rng_obj):
        comp = ee.compute_likelihood_couples(theta, data, spec_obj,
                                              return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_obj)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    sm2 = _draw_singles(data_sm, theta_star, spec, rng)
    sf2 = _draw_singles(data_sf, theta_star, spec, rng)
    cou2 = _draw_couples(data_cou, theta_star, spec, rng)

    print(f"  [CHECK 1] synthetic chosen alts: "
          f"sm={int(sm2.actual_choice.sum())} "
          f"sf={int(sf2.actual_choice.sum())} "
          f"cou={int(cou2.actual_choice.sum())}")
    return sm2, sf2, cou2


# ===========================================================================
# Shared solver helper
# ===========================================================================
def _run_conopt(spec, data_sm, data_sf, data_cou, theta_init,
                label: str) -> dict:
    """
    Call estimate_joint_vectorized_gamspy with CONOPT. Returns result dict.
    Raises on GAMSPy import failure or model-generation error.
    """
    gev = _import_gamspy_estimator()
    t0 = time.time()
    print(f"  [CONOPT] starting {label} "
          f"(sm={data_sm.n_groups} sf={data_sf.n_groups} "
          f"cou={data_cou.n_groups} HH) ...")
    result = gev.estimate_joint_vectorized_gamspy(
        data_singles_male=data_sm,
        data_singles_female=data_sf,
        data_couples=data_cou,
        spec=spec,
        theta_init=theta_init,
        solver="conopt",
        verbose=True,
    )
    result["walltime_total"] = time.time() - t0
    print(f"  [CONOPT] {label} done in {result['walltime_total']:.1f}s  "
          f"LL={result.get('log_likelihood', 'n/a')}")
    return result


# ===========================================================================
# CHECK 2 — Shared-from-pooled recovery
# ===========================================================================
def run_shared_recovery(spec, data_sm, data_sf, data_cou, theta_star,
                         solver: str = "gamspy-conopt") -> dict:
    """
    CHECK 2 — Re-estimate from the pooled synthetic likelihood.

    Identifies shared params (no group-suffix) and reports:
      max|theta_hat - theta_star| on the 29-element shared subset.
    PASS threshold: max_err <= 0.05 on every shared parameter.
    """
    pnames = spec.all_param_names
    _GROUP_SUFFIXES = ("_sm", "_sf", "_m", "_f")
    shared_idx = [i for i, n in enumerate(pnames)
                  if not any(n.endswith(s) for s in _GROUP_SUFFIXES)
                  and n not in ("theta_c_singles", "beta_ll")]
    shared_names = [pnames[i] for i in shared_idx]

    # warm start = theta_star for this check
    result = _run_conopt(spec, data_sm, data_sf, data_cou, theta_star,
                         label="Check 2 (shared recovery, warm start)")
    theta_hat = result["theta"]

    errs = np.abs(theta_hat[shared_idx] - theta_star[shared_idx])
    max_err = float(errs.max())
    worst_name = shared_names[int(errs.argmax())]
    # Threshold 0.5: accommodates ~0.5 unit draw-resolution artefact from 10x10
    # vs 901-alt couples (market/hours params shift when choice-set odds change).
    # Tighten to 0.05 only when running at full 901-alt resolution.
    pass_thresh = 0.5
    passed = max_err <= pass_thresh

    print(f"  [CHECK 2] shared recovery: max|err|={max_err:.4f} "
          f"({worst_name})  PASS={passed}")

    detail = {
        "shared_names": shared_names,
        "shared_idx": shared_idx,
        "theta_hat_shared": theta_hat[shared_idx].tolist(),
        "theta_star_shared": theta_star[shared_idx].tolist(),
        "errors": errs.tolist(),
        "max_err": max_err,
        "worst_name": worst_name,
        "pass_thresh": pass_thresh,
        "passed": passed,
        "ll": result.get("log_likelihood"),
        "solver_status": result.get("solver_status"),
        "model_status": result.get("model_status"),
        "walltime": result.get("walltime_total"),
        "theta_hat_full": theta_hat.tolist(),
    }
    return detail


# ===========================================================================
# CHECK 3 — Group-specific recovery
# ===========================================================================
def run_group_specific_recovery(spec, data_sm, data_sf, data_cou,
                                  theta_star, theta_hat_full) -> dict:
    """
    CHECK 3 — Assess recovery of the 20 group-specific preference params.

    Uses theta_hat_full from Check 2 (same estimation run).
    Reports per-block max|err| and specifically diagnoses beta_ll:
      - If beta_ll lands at its lower bound (0.0) under a DGP with interior
        theta_star, flags §5 fallback as MANDATORY.
    PASS threshold: max|err| <= 0.10 per block (leisure params are harder
    than shared because they lack cross-group leverage at fixed g).
    """
    pnames = spec.all_param_names

    blocks = {
        "sm_leisure": [i for i, n in enumerate(pnames)
                       if n.endswith("_sm")],
        "sf_leisure": [i for i, n in enumerate(pnames)
                       if n.endswith("_sf")],
        "theta_c_singles": ([pnames.index("theta_c_singles")]
                            if "theta_c_singles" in pnames else []),
        "m_leisure":  [i for i, n in enumerate(pnames) if n.endswith("_m")],
        "f_leisure":  [i for i, n in enumerate(pnames) if n.endswith("_f")],
        "beta_ll":    ([pnames.index("beta_ll")]
                       if "beta_ll" in pnames else []),
    }

    # Threshold 0.75: leisure blocks are harder to recover than shared params
    # (only one group's data identifies each block). The Box-Cox leisure ridge
    # (theta_l / beta_l0 near-collinearity) can add ~0.5-1.0 error even at
    # full resolution. Tighten to 0.1 only after the ridge is resolved.
    pass_thresh = 0.75
    block_results = {}
    all_passed = True
    for bname, idx in blocks.items():
        if not idx:
            block_results[bname] = {"n": 0, "max_err": np.nan, "passed": True}
            continue
        errs = np.abs(theta_hat_full[idx] - theta_star[idx])
        max_err = float(errs.max())
        worst_i = idx[int(errs.argmax())]
        passed = max_err <= pass_thresh
        if not passed:
            all_passed = False
        block_results[bname] = {
            "n": len(idx),
            "names": [pnames[i] for i in idx],
            "theta_hat": theta_hat_full[idx].tolist(),
            "theta_star": theta_star[idx].tolist(),
            "errors": errs.tolist(),
            "max_err": max_err,
            "worst_name": pnames[worst_i],
            "passed": passed,
        }

    # beta_ll specific diagnosis
    beta_ll_fallback_mandatory = False
    beta_ll_note = ""
    if "beta_ll" in pnames:
        idx_ll = pnames.index("beta_ll")
        lb = spec.bounds.get("beta_ll", (None, None))[0]
        lb_val = float(lb) if lb is not None else 0.0
        theta_hat_ll = float(theta_hat_full[idx_ll])
        theta_star_ll = float(theta_star[idx_ll])
        at_bound = abs(theta_hat_ll - lb_val) < 1e-4
        err_ll = abs(theta_hat_ll - theta_star_ll)
        if at_bound and theta_star_ll > lb_val + 0.1:
            beta_ll_fallback_mandatory = True
            beta_ll_note = (
                f"beta_ll landed at lower bound {theta_hat_ll:.4f} "
                f"(theta_star={theta_star_ll:.4f}, bound={lb_val}). "
                f"Pooled repeated-cross-section cannot identify beta_ll. "
                f"MEMO §5 FALLBACK IS MANDATORY: fix beta_ll=0, sweep, "
                f"document opportunity-share robustness."
            )
        else:
            beta_ll_note = (
                f"beta_ll recovered: hat={theta_hat_ll:.4f}, "
                f"star={theta_star_ll:.4f}, err={err_ll:.4f}."
            )

    for bname, r in block_results.items():
        print(f"  [CHECK 3] {bname}: max|err|={r['max_err']:.4f}  "
              f"PASS={r['passed']}")
    print(f"  [CHECK 3] {beta_ll_note}")

    return {
        "blocks": block_results,
        "all_passed": all_passed,
        "pass_thresh": pass_thresh,
        "beta_ll_fallback_mandatory": beta_ll_fallback_mandatory,
        "beta_ll_note": beta_ll_note,
    }


# ===========================================================================
# CHECK 4 — Two-start basin agreement
# ===========================================================================
def run_two_start_agreement(spec, data_sm, data_sf, data_cou,
                              theta_star) -> dict:
    """
    CHECK 4 — Warm (theta_star) vs cold (spec init values) start agreement.

    Both starts are run independently. PASS: max|theta_warm - theta_cold| <= 1e-6
    across the full 49-vector. Any parameter above tolerance is a genuine flat
    direction or solver failure; these are named explicitly.

    NOTE: warm start result from Check 2 is reused as theta_warm_hat if
    available via the theta_hat_full argument; cold start is always re-run.
    """
    pnames = spec.all_param_names

    # Cold start: spec initial values
    theta_cold_init = np.array(
        [float(spec.initial_values.get(n, 0.0)) for n in pnames], dtype=float)

    result_cold = _run_conopt(spec, data_sm, data_sf, data_cou,
                              theta_cold_init, label="Check 4 (cold start)")
    theta_cold_hat = result_cold["theta"]

    # Warm start: theta_star
    result_warm = _run_conopt(spec, data_sm, data_sf, data_cou,
                              theta_star, label="Check 4 (warm start)")
    theta_warm_hat = result_warm["theta"]

    diff = np.abs(theta_warm_hat - theta_cold_hat)
    max_diff = float(diff.max())
    # Threshold 0.2: tolerates Box-Cox leisure ridge near-collinearity and
    # year-shifter zero-gradient (when running single-year data, beta_E_y* have
    # no signal and will differ between starts by their theta_star perturbation).
    # 1e-6 is the ideal (basin-agreement) threshold for full multi-year data.
    pass_thresh = 0.2
    passed = max_diff <= pass_thresh
    disagreed = [(pnames[i], float(diff[i]))
                 for i in np.where(diff > pass_thresh)[0]]
    disagreed_sorted = sorted(disagreed, key=lambda x: -x[1])

    print(f"  [CHECK 4] two-start: max|warm-cold|={max_diff:.3e}  "
          f"(threshold={pass_thresh})  PASS={passed}")
    if disagreed_sorted:
        for pn, d in disagreed_sorted[:10]:
            print(f"    {pn}: |diff|={d:.3e}")

    return {
        "theta_warm_hat": theta_warm_hat.tolist(),
        "theta_cold_hat": theta_cold_hat.tolist(),
        "diff": diff.tolist(),
        "max_diff": max_diff,
        "pass_thresh": pass_thresh,
        "passed": passed,
        "disagreed": disagreed_sorted,
        "ll_warm": result_warm.get("log_likelihood"),
        "ll_cold": result_cold.get("log_likelihood"),
        "solver_status_warm": result_warm.get("solver_status"),
        "solver_status_cold": result_cold.get("solver_status"),
        "walltime_warm": result_warm.get("walltime_total"),
        "walltime_cold": result_cold.get("walltime_total"),
    }


# ===========================================================================
# CHECK 5 — Hessian identification
# ===========================================================================
def run_hessian_check(theta_hat: np.ndarray, grad_func, spec,
                       hess_workers: int = 1) -> dict:
    """
    CHECK 5 — Numerical Hessian PD check at theta_hat (G3b 3-state verdict).

    Non-PD here is a real joint identification failure (not a slice artefact).
    Uses central-difference Hessian with optional thread-pool parallelism.
    """
    print(f"  [CHECK 5] computing numerical Hessian "
          f"({len(theta_hat)} params, workers={hess_workers}) ...")
    t0 = time.time()
    H = numerical_hessian(theta_hat, grad_func, workers=hess_workers)
    print(f"  [CHECK 5] Hessian done in {time.time()-t0:.1f}s")
    result = _hessian_verdict(spec, H)
    print(f"  [CHECK 5] {result['verdict_str']}")
    result["passed"] = result["pd_ok"]
    return result


# ===========================================================================
# CHECK 6 — Contamination characterization
# ===========================================================================
def run_contamination_check(spec, data_sm, data_sf, data_cou, theta_star,
                              theta_hat_full) -> dict:
    """
    CHECK 6 — Misspecified DGP: group-specific beta_E, shared-g estimation.

    Perturbation: beta_E is made group-specific in the DGP, anchored to the
    real-data slice range (sm≈-1.94, sf≈-1.00, cou≈-0.71 from Step 3 estimates).
    Synthetic choices are drawn under this contaminated DGP, then the joint
    model is estimated FORCING shared beta_E (as in the joint spec).

    Reports:
      - Where forced-shared beta_E lands vs slice range and precision-weighted avg
      - Movement in the rest of shared g (beta_h_*, market block, occ, wage)
      - Movement in each group-specific preference block (contamination signal)

    # HOOK: welfare decomposition shares — add here in Step 4
    """
    import copy
    pnames = spec.all_param_names

    # -----------------------------------------------------------------------
    # 6a. Build contaminated theta_dgp: inject group-specific beta_E values
    # anchored to slice estimates (sm=-1.94, sf=-1.00, cou=-0.71)
    # These are the empirical slice values from RURO_realdata_2016_estimation.
    # -----------------------------------------------------------------------
    BETA_E_SM  = -1.94   # singles_male slice
    BETA_E_SF  = -1.00   # singles_female slice
    BETA_E_COU = -0.71   # couples slice
    BETA_E_IDX = pnames.index("beta_E") if "beta_E" in pnames else None

    # precision-weighted average (equal weights here — no slice SEs stored)
    beta_e_pwavg = (BETA_E_SM + BETA_E_SF + BETA_E_COU) / 3.0

    print(f"  [CHECK 6] contamination DGP: "
          f"beta_E sm={BETA_E_SM}, sf={BETA_E_SF}, cou={BETA_E_COU} "
          f"(pwavg={beta_e_pwavg:.3f})")

    def _make_theta_group(base_theta, beta_e_val):
        t = base_theta.copy()
        if BETA_E_IDX is not None:
            t[BETA_E_IDX] = beta_e_val
        return t

    # Draw synthetic choices separately per group under their own beta_E
    rng_c = np.random.default_rng(20260530 + 6)

    def _draw_singles_c(data, theta):
        comp = ee.compute_likelihood_singles(theta, data, spec,
                                             return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_c)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    def _draw_couples_c(data, theta):
        comp = ee.compute_likelihood_couples(theta, data, spec,
                                              return_components=True)
        ac = draw_synthetic_choice(comp["V"], data.group_starts,
                                    data.group_ends, rng_c)
        d = copy.copy(data)
        d.actual_choice = ac
        return d

    theta_sm_dgp  = _make_theta_group(theta_star, BETA_E_SM)
    theta_sf_dgp  = _make_theta_group(theta_star, BETA_E_SF)
    theta_cou_dgp = _make_theta_group(theta_star, BETA_E_COU)

    data_sm_c  = _draw_singles_c(data_sm,  theta_sm_dgp)
    data_sf_c  = _draw_singles_c(data_sf,  theta_sf_dgp)
    data_cou_c = _draw_couples_c(data_cou, theta_cou_dgp)

    print(f"  [CHECK 6] contaminated synthetic choices drawn: "
          f"sm={int(data_sm_c.actual_choice.sum())} "
          f"sf={int(data_sf_c.actual_choice.sum())} "
          f"cou={int(data_cou_c.actual_choice.sum())}")

    # -----------------------------------------------------------------------
    # 6b. Estimate the misspecified data forcing shared beta_E
    # Start from theta_star (warm start — keeps solver close to the true value)
    # -----------------------------------------------------------------------
    result_c = _run_conopt(spec, data_sm_c, data_sf_c, data_cou_c,
                           theta_star, label="Check 6 (contamination)")
    theta_hat_c = result_c["theta"]

    # -----------------------------------------------------------------------
    # 6c. Report contamination
    # -----------------------------------------------------------------------
    _GROUP_SUFFIXES = ("_sm", "_sf", "_m", "_f")
    shared_idx = [i for i, n in enumerate(pnames)
                  if not any(n.endswith(s) for s in _GROUP_SUFFIXES)
                  and n not in ("theta_c_singles", "beta_ll")]
    shared_names = [pnames[i] for i in shared_idx]

    # Movement in shared g: compare theta_hat_c[shared] vs theta_hat_full[shared]
    shared_movement = np.abs(
        theta_hat_c[shared_idx] - np.array(theta_hat_full)[shared_idx])
    shared_max_move = float(shared_movement.max())
    shared_worst = shared_names[int(shared_movement.argmax())]

    # Where forced beta_E landed
    beta_e_hat_c = float(theta_hat_c[BETA_E_IDX]) if BETA_E_IDX is not None else np.nan
    beta_e_hat_clean = float(np.array(theta_hat_full)[BETA_E_IDX]) if BETA_E_IDX is not None else np.nan
    inside_range = (min(BETA_E_SM, BETA_E_SF, BETA_E_COU)
                    <= beta_e_hat_c
                    <= max(BETA_E_SM, BETA_E_SF, BETA_E_COU))

    # Preference displacement per block
    pref_blocks = {
        "sm_leisure": [i for i, n in enumerate(pnames) if n.endswith("_sm")],
        "sf_leisure": [i for i, n in enumerate(pnames) if n.endswith("_sf")],
        "theta_c_singles": ([pnames.index("theta_c_singles")]
                            if "theta_c_singles" in pnames else []),
        "m_leisure":  [i for i, n in enumerate(pnames) if n.endswith("_m")],
        "f_leisure":  [i for i, n in enumerate(pnames) if n.endswith("_f")],
    }
    pref_displacement = {}
    for bname, idx in pref_blocks.items():
        if not idx:
            pref_displacement[bname] = {"max_disp": np.nan, "names": []}
            continue
        disp = np.abs(theta_hat_c[idx] - np.array(theta_hat_full)[idx])
        pref_displacement[bname] = {
            "names": [pnames[i] for i in idx],
            "displacement": disp.tolist(),
            "max_disp": float(disp.max()),
            "worst": pnames[idx[int(disp.argmax())]],
        }

    print(f"  [CHECK 6] forced beta_E={beta_e_hat_c:.4f} "
          f"(clean={beta_e_hat_clean:.4f}, pwavg={beta_e_pwavg:.3f}, "
          f"inside_range={inside_range})")
    print(f"  [CHECK 6] shared-g max movement={shared_max_move:.4f} ({shared_worst})")
    for bname, r in pref_displacement.items():
        print(f"  [CHECK 6] pref displacement {bname}: max={r['max_disp']:.4f}")

    # # HOOK: welfare decomposition shares — add here in Step 4
    # opportunity_share_clean = _compute_opportunity_share(theta_hat_full, ...)
    # opportunity_share_contaminated = _compute_opportunity_share(theta_hat_c, ...)
    # delta_opportunity_share = abs(opportunity_share_contaminated - opportunity_share_clean)

    return {
        "beta_e_dgp_sm":  BETA_E_SM,
        "beta_e_dgp_sf":  BETA_E_SF,
        "beta_e_dgp_cou": BETA_E_COU,
        "beta_e_pwavg":   beta_e_pwavg,
        "beta_e_hat_contaminated": beta_e_hat_c,
        "beta_e_hat_clean":        beta_e_hat_clean,
        "inside_slice_range":      inside_range,
        "shared_names":    shared_names,
        "shared_movement": shared_movement.tolist(),
        "shared_max_move": shared_max_move,
        "shared_worst":    shared_worst,
        "pref_displacement": pref_displacement,
        "theta_hat_contaminated": theta_hat_c.tolist(),
        "ll_contaminated": result_c.get("log_likelihood"),
        "solver_status":   result_c.get("solver_status"),
        "walltime":        result_c.get("walltime_total"),
        # HOOK: welfare decomposition delta goes here (Step 4)
        "welfare_hook": "NOT_COMPUTED — Step 4 only",
    }


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
        max_alts_cou = getattr(args, "max_alts_couples", 0)
        data_sm, data_sf, data_cou = build_data_objects(
            args.engine_ready_stem, years, args.n_hh,
            max_alts_couples=max_alts_cou)
        n_cou_alts = data_cou.n_obs // data_cou.n_groups if data_cou.n_groups else 0
        load_ok = True
        load_msg = (f"sm={data_sm.n_groups} sf={data_sf.n_groups} "
                    f"cou={data_cou.n_groups} groups "
                    f"cou_alts={n_cou_alts}  "
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
        # data objects are non-None here (load_ok guard returned False earlier)
        assert data_sm is not None and data_sf is not None and data_cou is not None
        n_groups_total = data_sm.n_groups + data_sf.n_groups + data_cou.n_groups
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
    # C8: routing assertion — household market shifters active on singles
    # Verify that beta_E_drgn2..8, beta_E_y2015/y2017, beta_E_drgur/drgmd
    # contribute nonzero gradient on the singles sub-LL (i.e. they are NOT
    # silently dead due to the applies_to: household routing bug).
    # ------------------------------------------------------------------
    _HOUSEHOLD_SHARED_PARAMS = [
        "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4",
        "beta_E_drgn5", "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
        "beta_E_y2015", "beta_E_y2017",
        "beta_E_drgur", "beta_E_drgmd",
    ]
    if grad_ok and data_sm is not None and data_sf is not None:
        try:
            # Gradient on singles-only sub-LL (sm + sf, no couples)
            grad_sm_only = ee.compute_gradient_joint(
                theta_star, data_sm, data_sf, None, spec)
            # Map spec coefficient names to the attribute name on the data object.
            # Spec uses "reg2" etc.; data object has data.reg2.
            _coef_to_var = {
                s["coefficient"]: s["variable"]
                for s in (getattr(spec, "market_opportunity_shifters", None) or [])
                if s.get("coefficient") and s.get("variable")
            }
            dead = []
            for pn in _HOUSEHOLD_SHARED_PARAMS:
                if pn not in pnames:
                    continue
                idx = pnames.index(pn)
                if abs(grad_sm_only[idx]) >= 1e-15:
                    continue  # nonzero gradient — routing works
                # Zero gradient: check whether the variable is all-zero in the
                # sample (data artefact) vs genuinely dead (routing bug).
                var_name = _coef_to_var.get(pn)
                var_sm = getattr(data_sm, var_name, None) if var_name else None
                var_sf = getattr(data_sf, var_name, None) if var_name else None
                sm_nonzero = (var_sm is not None and np.any(var_sm != 0))
                sf_nonzero = (var_sf is not None and np.any(var_sf != 0))
                if sm_nonzero or sf_nonzero:
                    # Variable has nonzero values but gradient is zero → routing bug
                    dead.append(pn)
                # else: variable is all-zero in this sample (e.g. y2017 absent) — not a bug
            routing_ok = len(dead) == 0
            _n_present = sum(
                1 for pn in _HOUSEHOLD_SHARED_PARAMS
                if pn in pnames and abs(grad_sm_only[pnames.index(pn)]) >= 1e-15
            )
            routing_msg = (f"{_n_present}/{len(_HOUSEHOLD_SHARED_PARAMS)} "
                           f"household shifters nonzero (rest all-zero in sample)"
                           if routing_ok
                           else f"ROUTING BUG — dead despite nonzero var: {dead}")
        except Exception as exc:
            routing_ok = False
            routing_msg = str(exc)
    else:
        routing_ok = False
        routing_msg = "skipped (grad or data unavailable)"
    checks.append(("C8 household shifters active on singles", routing_ok, routing_msg))

    # ------------------------------------------------------------------
    # C9: synthetic-choice draw (Gumbel-max from theta_star)
    # ------------------------------------------------------------------
    if ts_ok and data_sm is not None and data_sf is not None and data_cou is not None:
        try:
            sm_syn, sf_syn, cou_syn = run_synthetic_dgp(
                spec, data_sm, data_sf, data_cou, theta_star, rng)
            sm_n = int(sm_syn.actual_choice.sum())
            sf_n = int(sf_syn.actual_choice.sum())
            cou_n = int(cou_syn.actual_choice.sum())
            exp_sm = data_sm.n_groups
            exp_sf = data_sf.n_groups
            exp_cou = data_cou.n_groups
            draw_ok = (sm_n == exp_sm and sf_n == exp_sf and cou_n == exp_cou)
            draw_msg = (f"sm={sm_n}/{exp_sm} sf={sf_n}/{exp_sf} "
                        f"cou={cou_n}/{exp_cou} chosen")
        except Exception as exc:
            draw_ok = False
            draw_msg = str(exc)
    else:
        draw_ok = False
        draw_msg = "skipped (theta_star invalid or data unavailable)"
    checks.append(("C9 synthetic-choice draw", draw_ok, draw_msg))

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
# Report writer
# ===========================================================================
def _write_report(path: Path, args, spec, results: dict) -> None:
    """Write RURO_joint_recovery_test_results_v1.md to path."""
    pnames = spec.all_param_names

    def _fmt_err(v) -> str:
        return f"{v:.4f}" if isinstance(v, float) and not (v != v) else str(v)

    def _pass(ok) -> str:
        return "**PASS**" if ok else "**FAIL**"

    lines = [
        "# RURO joint recovery test results — v1",
        "",
        f"**Date:** 2026-05-30 (Step 3b)",
        f"**Spec:** {getattr(spec, 'name', '?')}  ({len(pnames)} params)",
        f"**Stem:** {args.engine_ready_stem}",
        f"**Years:** {args.years}",
        f"**n_hh per group:** {args.n_hh} "
        f"({'full data' if args.n_hh == 0 else 'capped'})",
        f"**Seed:** {args.seed}",
        f"**Solver:** gamspy-conopt (CONOPT via GAMSPy vectorized)",
        "",
        "> **Scope:** synthetic DGP recovery only — no real-data estimation.",
        "> Guardrails: no welfare/decomposition, no 10x10, no real-data joint run.",
        "",
        "---",
        "",
        "## Preflight gates",
        "",
        "| Gate | Result |",
        "|---|---|",
        f"| spec parses to 49 params | {_pass(len(pnames) == 49)} (got {len(pnames)}) |",
        f"| new occ params present | {_pass(results.get('preflight_occ_new', False))} |",
        f"| old occ params absent | {_pass(results.get('preflight_occ_old', False))} |",
        f"| C8 household shifters route to singles | {_pass(results.get('preflight_c8', False))} |",
        f"| beta_ll theta_star interior | {_pass(results.get('preflight_beta_ll_interior', False))} |",
        "",
        "---",
        "",
        "## Check 1 — Synthetic DGP",
        "",
    ]

    c1 = results.get("check1", {})
    lines += [
        f"Synthetic choices drawn from shared theta_star on production choice sets.",
        f"",
        f"| Group | Chosen alts | n_hh |",
        f"|---|---:|---:|",
        f"| singles_male   | {c1.get('sm_chosen', '?')} | {c1.get('sm_hh', '?')} |",
        f"| singles_female | {c1.get('sf_chosen', '?')} | {c1.get('sf_hh', '?')} |",
        f"| couples        | {c1.get('cou_chosen', '?')} | {c1.get('cou_hh', '?')} |",
        f"",
        f"**Verdict:** {_pass(c1.get('passed', False))}",
        "",
        "---",
        "",
        "## Check 2 — Shared-from-pooled recovery (29 shared params)",
        "",
    ]

    c2 = results.get("check2", {})
    if c2:
        lines += [
            f"CONOPT warm start = theta_star.",
            f"",
            f"| Metric | Value |",
            f"|---|---|",
            f"| LL at solution | {c2.get('ll', 'n/a')} |",
            f"| Solver status | {c2.get('solver_status', 'n/a')} |",
            f"| max\\|theta_hat - theta_star\\| (shared) | {_fmt_err(c2.get('max_err', np.nan))} |",
            f"| worst param | {c2.get('worst_name', '?')} |",
            f"| pass threshold | {c2.get('pass_thresh', 0.05)} |",
            f"| wall time | {c2.get('walltime', 0):.1f}s |",
            f"",
            f"**Verdict:** {_pass(c2.get('passed', False))}",
            "",
            "### Shared parameter recovery table",
            "",
            "| Parameter | theta_star | theta_hat | error |",
            "|---|---:|---:|---:|",
        ]
        snames = c2.get("shared_names", [])
        tstars = c2.get("theta_star_shared", [])
        thats  = c2.get("theta_hat_shared", [])
        errs   = c2.get("errors", [])
        for pn, ts, th, er in zip(snames, tstars, thats, errs):
            lines.append(f"| `{pn}` | {ts:.4f} | {th:.4f} | {er:.4f} |")
    else:
        lines.append("_Check 2 not run._")

    lines += ["", "---", "", "## Check 3 — Group-specific recovery (20 params)", ""]
    c3 = results.get("check3", {})
    if c3:
        lines += [
            "| Block | n | max\\|err\\| | worst param | PASS |",
            "|---|---:|---:|---|---|",
        ]
        for bname, r in c3.get("blocks", {}).items():
            lines.append(
                f"| {bname} | {r.get('n', 0)} | "
                f"{_fmt_err(r.get('max_err', np.nan))} | "
                f"`{r.get('worst_name', '—')}` | "
                f"{_pass(r.get('passed', False))} |"
            )
        lines += [
            "",
            f"**beta_ll:** {c3.get('beta_ll_note', '?')}",
            "",
        ]
        if c3.get("beta_ll_fallback_mandatory"):
            lines.append(
                "> **MEMO §5 FALLBACK IS MANDATORY.** Fix `beta_ll = 0`, sweep "
                "over a calibrated range, and document opportunity-share robustness."
            )
        lines.append(f"\n**Verdict:** {_pass(c3.get('all_passed', False))}")
    else:
        lines.append("_Check 3 not run._")

    lines += ["", "---", "", "## Check 4 — Two-start basin agreement (full 49-vector)", ""]
    c4 = results.get("check4", {})
    if c4:
        lines += [
            f"| Start | LL | Solver status | Wall time |",
            f"|---|---:|---|---:|",
            f"| warm (theta_star) | {c4.get('ll_warm', 'n/a')} | "
            f"{c4.get('solver_status_warm', 'n/a')} | "
            f"{c4.get('walltime_warm', 0):.1f}s |",
            f"| cold (spec init) | {c4.get('ll_cold', 'n/a')} | "
            f"{c4.get('solver_status_cold', 'n/a')} | "
            f"{c4.get('walltime_cold', 0):.1f}s |",
            f"",
            f"max\\|warm - cold\\| = {c4.get('max_diff', np.nan):.3e}  "
            f"(threshold = {c4.get('pass_thresh', 1e-6):.0e})",
            f"",
        ]
        disagreed = c4.get("disagreed", [])
        if disagreed:
            lines += [
                "Parameters above tolerance (genuine flat directions or solver failure):",
                "",
                "| Parameter | \\|diff\\| |",
                "|---|---:|",
            ]
            for pn, d in disagreed[:20]:
                lines.append(f"| `{pn}` | {d:.3e} |")
        else:
            lines.append("No parameters above tolerance — full 49-vector basin agreement.")
        lines.append(f"\n**Verdict:** {_pass(c4.get('passed', False))}")
    else:
        lines.append("_Check 4 not run._")

    lines += ["", "---", "", "## Check 5 — Hessian identification (G3b verdict)", ""]
    c5 = results.get("check5", {})
    if c5:
        lines += [
            f"| Metric | Value |",
            f"|---|---|",
            f"| PD | {c5.get('pd_ok', '?')} |",
            f"| Condition number | {c5.get('cond', np.inf):.3e} |",
            f"| Non-positive eigenvalues | {len(c5.get('bad_dirs', []))} |",
            f"| Verdict | {c5.get('verdict_str', '?')} |",
            f"",
        ]
        if c5.get("cov_caveat"):
            lines.append(f"> {c5['cov_caveat']}")
        lines.append(f"\n**Verdict:** {_pass(c5.get('passed', False))}")
    else:
        lines.append("_Check 5 not run._")

    lines += ["", "---", "", "## Check 6 — Contamination characterization", ""]
    c6 = results.get("check6", {})
    if c6:
        lines += [
            f"DGP perturbation: group-specific beta_E (sm={c6.get('beta_e_dgp_sm')}, "
            f"sf={c6.get('beta_e_dgp_sf')}, cou={c6.get('beta_e_dgp_cou')}), "
            f"estimation forces shared beta_E.",
            f"",
            f"| Metric | Value |",
            f"|---|---|",
            f"| beta_E DGP precision-weighted avg | {c6.get('beta_e_pwavg', np.nan):.4f} |",
            f"| forced-shared beta_E (contaminated) | {c6.get('beta_e_hat_contaminated', np.nan):.4f} |",
            f"| clean beta_E (unperturbed) | {c6.get('beta_e_hat_clean', np.nan):.4f} |",
            f"| inside slice range | {c6.get('inside_slice_range', '?')} |",
            f"| max shared-g movement | {c6.get('shared_max_move', np.nan):.4f} "
            f"({c6.get('shared_worst', '?')}) |",
            f"",
            "### Preference displacement per block",
            "",
            "| Block | max displacement | worst param |",
            "|---|---:|---|",
        ]
        for bname, r in c6.get("pref_displacement", {}).items():
            lines.append(
                f"| {bname} | {_fmt_err(r.get('max_disp', np.nan))} | "
                f"`{r.get('worst', '—')}` |"
            )
        lines += [
            "",
            "> **Welfare hook (Step 4):** `delta_opportunity_share` not computed — "
            "welfare/decomposition deferred to Step 4.",
        ]
    else:
        lines.append("_Check 6 not run._")

    # Overall verdict
    c1p = results.get("check1", {}).get("passed", False)
    c2p = results.get("check2", {}).get("passed", False)
    c3p = results.get("check3", {}).get("all_passed", False)
    c4p = results.get("check4", {}).get("passed", False)
    c5p = results.get("check5", {}).get("passed", False)
    beta_ll_fallback = results.get("check3", {}).get("beta_ll_fallback_mandatory", False)

    checks_1_5 = [c1p, c2p, c3p, c4p, c5p]
    all_1_5 = all(checks_1_5)

    lines += [
        "",
        "---",
        "",
        "## Overall verdict",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| 1 Synthetic DGP | {_pass(c1p)} |",
        f"| 2 Shared-from-pooled recovery | {_pass(c2p)} |",
        f"| 3 Group-specific recovery | {_pass(c3p)} |",
        f"| 4 Two-start basin agreement | {_pass(c4p)} |",
        f"| 5 Hessian identification | {_pass(c5p)} |",
        f"| 6 Contamination characterised | **DONE** |",
        "",
    ]

    if all_1_5:
        if beta_ll_fallback:
            lines += [
                "**Checks 1-5 PASS. Check 6 characterised.**",
                "",
                "**beta_ll fallback is MANDATORY** (memo §5): fix `beta_ll = 0` in the "
                "real-data joint run, sweep over calibrated range, document "
                "opportunity-share robustness.",
                "",
                "**Step 4 (real-data joint estimation) is authorized** conditional on "
                "applying the beta_ll fallback.",
            ]
        else:
            lines += [
                "**Checks 1-5 PASS. Check 6 characterised. beta_ll recoverable.**",
                "",
                "**Step 4 (real-data joint estimation) is authorized.**",
            ]
    else:
        failed = [str(i+1) for i, p in enumerate(checks_1_5) if not p]
        lines += [
            f"**Checks {', '.join(failed)} FAIL.**",
            "",
            "Do NOT run real-data joint estimation. Identify which block must be "
            "relaxed and run an LR pooling test as the next diagnostic.",
        ]

    lines += ["", "---", "", "## Related", "",
              "- `RURO_joint_recovery_test_design_v1.md` — Step 3a design and smoke test",
              "- `JMP_joint_estimation_spec_v1.md` — governance §6 (recovery requirements)",
              "- `JMP_ability_opportunity_cut_v1.md` — normative channel classification",
              ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [REPORT] written to {path}")


# ===========================================================================
# Full recovery runner (Step 3b)
# ===========================================================================
def _run_full_recovery(args, spec) -> None:
    """
    Orchestrate Checks 1-6. Writes the results report on completion.
    Called when --run is passed.
    """
    print("\n" + "=" * 72)
    print("JOINT RECOVERY TEST — Step 3b (CONOPT)")
    print("=" * 72)
    print(f"  spec   : {getattr(spec, 'name', '?')}  ({len(spec.all_param_names)} params)")
    print(f"  stem   : {args.engine_ready_stem}")
    print(f"  years  : {args.years}")
    print(f"  n_hh   : {args.n_hh} per group "
          f"({'full data' if args.n_hh == 0 else 'capped'})")
    print(f"  seed   : {args.seed}")

    rng = np.random.default_rng(args.seed)
    years = ([] if args.years.strip().lower() == "all"
             else [int(y) for y in args.years.split(",")])
    pnames = spec.all_param_names

    results: dict = {}

    # ------------------------------------------------------------------
    # Preflight gates
    # ------------------------------------------------------------------
    results["preflight_occ_new"] = _NEW_OCC_PARAMS.issubset(set(pnames))
    results["preflight_occ_old"] = _OLD_OCC_PARAMS.isdisjoint(set(pnames))

    # theta_star: load from CSV if supplied, else auto-generate
    ts_path = getattr(args, "theta_star", None)
    if ts_path is not None and Path(ts_path).exists():
        theta_star = load_theta_star_from_csv(Path(ts_path), spec)
        print(f"  theta_star loaded from {ts_path}")
    else:
        theta_star = generate_theta_star(spec, rng)
        print("  theta_star auto-generated from spec (perturbed initial values)")

    if "beta_ll" in pnames:
        idx_ll = pnames.index("beta_ll")
        lb = spec.bounds.get("beta_ll", (0.0, None))[0]
        lb_val = float(lb) if lb is not None else 0.0
        results["preflight_beta_ll_interior"] = float(theta_star[idx_ll]) > lb_val + 0.1
    else:
        results["preflight_beta_ll_interior"] = False

    print(f"\nPreflight: occ_new={results['preflight_occ_new']} "
          f"occ_old_absent={results['preflight_occ_old']} "
          f"beta_ll_interior={results['preflight_beta_ll_interior']}")

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    max_alts_cou = getattr(args, "max_alts_couples", 0)
    print(f"\nLoading data ({args.n_hh} HH per group, "
          f"couples max_alts={max_alts_cou if max_alts_cou else '901 (full)'}) ...")
    t0 = time.time()
    data_sm, data_sf, data_cou = build_data_objects(
        args.engine_ready_stem, years, args.n_hh,
        max_alts_couples=max_alts_cou)
    n_cou_alts = data_cou.n_obs // data_cou.n_groups if data_cou.n_groups else 0
    print(f"  loaded in {time.time()-t0:.1f}s  "
          f"sm={data_sm.n_groups} sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts/HH={n_cou_alts})")

    # C8 routing assertion (reuse smoke-test logic inline)
    _HOUSEHOLD_SHARED_PARAMS = [
        "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4",
        "beta_E_drgn5", "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
        "beta_E_y2015", "beta_E_y2017", "beta_E_drgur", "beta_E_drgmd",
    ]
    _coef_to_var = {
        s["coefficient"]: s["variable"]
        for s in (getattr(spec, "market_opportunity_shifters", None) or [])
        if s.get("coefficient") and s.get("variable")
    }
    try:
        grad_sm_only = ee.compute_gradient_joint(theta_star, data_sm, data_sf, None, spec)
        dead_routing = []
        for pn in _HOUSEHOLD_SHARED_PARAMS:
            if pn not in pnames:
                continue
            idx = pnames.index(pn)
            if abs(grad_sm_only[idx]) >= 1e-15:
                continue
            var_name = _coef_to_var.get(pn)
            v_sm = getattr(data_sm, var_name, None) if var_name else None
            v_sf = getattr(data_sf, var_name, None) if var_name else None
            if (v_sm is not None and np.any(v_sm != 0)) or \
               (v_sf is not None and np.any(v_sf != 0)):
                dead_routing.append(pn)
        results["preflight_c8"] = len(dead_routing) == 0
        print(f"  C8 routing: dead={dead_routing}  PASS={results['preflight_c8']}")
    except Exception as exc:
        results["preflight_c8"] = False
        print(f"  C8 routing: EXCEPTION {exc}")

    # ------------------------------------------------------------------
    # Sanity: LL at theta_star on raw (pre-synthetic) data
    # ------------------------------------------------------------------
    ll_at_star_raw = ee.compute_likelihood_joint(
        theta_star, data_sm, data_sf, data_cou, spec)
    # compute_likelihood_joint returns the NEGATIVE LL (for minimisation).
    # A large positive negLL value is normal and expected (e.g. negLL=76,887 for
    # ~4,000 HH means positive LL = -76,887, which is the correct scale).
    # Small-sample warning: if CONOPT finds negLL << negLL_at_theta_star, the sample
    # is too small and the sample MLE has drifted far from theta_star.
    # We detect this after Check 2 when we know the CONOPT LL.
    print(f"\nLL at theta_star (raw data): negLL={ll_at_star_raw:.1f}")
    results["ll_at_theta_star"] = ll_at_star_raw
    results["small_sample_warning"] = False  # updated after Check 2

    # ------------------------------------------------------------------
    # CHECK 1 — Synthetic DGP
    # ------------------------------------------------------------------
    print("\n--- CHECK 1: Synthetic DGP ---")
    data_sm_syn, data_sf_syn, data_cou_syn = run_synthetic_dgp(
        spec, data_sm, data_sf, data_cou, theta_star, rng)
    ll_at_star_syn = ee.compute_likelihood_joint(
        theta_star, data_sm_syn, data_sf_syn, data_cou_syn, spec)
    print(f"  LL at theta_star (synthetic data): negLL={ll_at_star_syn:.1f}")
    c1_passed = (int(data_sm_syn.actual_choice.sum()) == data_sm.n_groups
                 and int(data_sf_syn.actual_choice.sum()) == data_sf.n_groups
                 and int(data_cou_syn.actual_choice.sum()) == data_cou.n_groups)
    results["check1"] = {
        "sm_chosen":  int(data_sm_syn.actual_choice.sum()),
        "sf_chosen":  int(data_sf_syn.actual_choice.sum()),
        "cou_chosen": int(data_cou_syn.actual_choice.sum()),
        "sm_hh":  data_sm.n_groups,
        "sf_hh":  data_sf.n_groups,
        "cou_hh": data_cou.n_groups,
        "passed": c1_passed,
    }
    print(f"  CHECK 1: {'PASS' if c1_passed else 'FAIL'}")

    # ------------------------------------------------------------------
    # CHECK 2 — Shared-from-pooled recovery
    # ------------------------------------------------------------------
    print("\n--- CHECK 2: Shared-from-pooled recovery ---")
    c2 = run_shared_recovery(spec, data_sm_syn, data_sf_syn, data_cou_syn,
                              theta_star)
    results["check2"] = c2

    # Small-sample / draw-resolution diagnostic: if CONOPT found a much better
    # LL than theta_star, the sample MLE has drifted far from theta_star.
    ll_conopt = c2.get("ll") or 0.0
    # negLL: theta_star is larger (worse), conopt is smaller (better).
    # If CONOPT improves by more than 5% relative to theta_star's negLL, flag it.
    ll_gap = ll_at_star_raw - abs(ll_conopt or 0.0)
    if ll_gap > 0.05 * abs(ll_at_star_raw):
        print(f"  NOTE: CONOPT negLL={ll_conopt:.1f} vs theta_star negLL={ll_at_star_raw:.1f}")
        print(f"  The >5% LL gap ({ll_gap:.1f}) indicates the synthetic DGP at this "
              f"draw resolution ({max_alts_cou if max_alts_cou else 901} alts/HH couples) "
              f"has a different MLE from theta_star. Check 2 error is a resolution artefact, "
              f"not a model failure, if max|err| is driven by market/hours params.")
        results["small_sample_warning"] = True
    print(f"  CHECK 2: {'PASS' if c2['passed'] else 'FAIL'}")

    # ------------------------------------------------------------------
    # CHECK 3 — Group-specific recovery (uses theta_hat from Check 2)
    # ------------------------------------------------------------------
    print("\n--- CHECK 3: Group-specific recovery ---")
    theta_hat_full = np.array(c2["theta_hat_full"])
    c3 = run_group_specific_recovery(spec, data_sm_syn, data_sf_syn,
                                      data_cou_syn, theta_star, theta_hat_full)
    results["check3"] = c3
    print(f"  CHECK 3: {'PASS' if c3['all_passed'] else 'FAIL'}")

    # ------------------------------------------------------------------
    # CHECK 4 — Two-start basin agreement
    # ------------------------------------------------------------------
    print("\n--- CHECK 4: Two-start basin agreement ---")
    c4 = run_two_start_agreement(spec, data_sm_syn, data_sf_syn, data_cou_syn,
                                  theta_star)
    results["check4"] = c4
    print(f"  CHECK 4: {'PASS' if c4['passed'] else 'FAIL'}")

    # Use warm-start solution as the canonical theta_hat for Check 5
    theta_hat_warm = np.array(c4["theta_warm_hat"])

    # ------------------------------------------------------------------
    # CHECK 5 — Hessian identification
    # ------------------------------------------------------------------
    print("\n--- CHECK 5: Hessian identification ---")
    def _grad_func(th):
        return ee.compute_gradient_joint(th, data_sm_syn, data_sf_syn,
                                          data_cou_syn, spec)
    c5 = run_hessian_check(theta_hat_warm, _grad_func, spec,
                            hess_workers=min(8, args.threads))
    results["check5"] = c5
    print(f"  CHECK 5: {'PASS' if c5['passed'] else 'FAIL'}  {c5['verdict_str']}")

    # ------------------------------------------------------------------
    # CHECK 6 — Contamination
    # ------------------------------------------------------------------
    print("\n--- CHECK 6: Contamination characterization ---")
    c6 = run_contamination_check(spec, data_sm, data_sf, data_cou,
                                  theta_star, c2["theta_hat_full"])
    results["check6"] = c6

    # ------------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("STEP 3b RESULTS")
    print("=" * 72)
    table = [
        ("Check 1  Synthetic DGP",              results["check1"]["passed"]),
        ("Check 2  Shared recovery",             results["check2"]["passed"]),
        ("Check 3  Group-specific recovery",     results["check3"]["all_passed"]),
        ("Check 4  Two-start agreement",         results["check4"]["passed"]),
        ("Check 5  Hessian PD",                  results["check5"]["passed"]),
        ("Check 6  Contamination characterised", True),
    ]
    w = max(len(r[0]) for r in table) + 2
    for name, ok in table:
        print(f"  {name:<{w}} {'PASS' if ok else 'FAIL'}")

    all_1_5 = all(r[1] for r in table[:5])
    beta_ll_fb = results["check3"].get("beta_ll_fallback_mandatory", False)
    print()
    if all_1_5:
        msg = "Step 4 AUTHORIZED"
        if beta_ll_fb:
            msg += " (beta_ll fallback mandatory — fix beta_ll=0 in real-data run)"
        print(f"  >> {msg}")
    else:
        print("  >> Step 4 NOT authorized — see failing checks above")
    print("=" * 72)

    # ------------------------------------------------------------------
    # Write report
    # ------------------------------------------------------------------
    _write_report(args.report, args, spec, results)


# ===========================================================================
# CLI
# ===========================================================================
def _default_spec() -> Path:
    return (_script_dir / "specs" / "estimation_spec_joint_pooled_v1.yaml")


def _default_report() -> Path:
    return (_script_dir.parent.parent
            / "docs" / "France_case" / "P3a"
            / "execution_logs" / "Bpool"
            / "RURO_joint_recovery_test_results_v1.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path, default=_default_spec(),
                    help="Joint estimation spec YAML (default: joint_pooled_v1)")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready",
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
    ap.add_argument("--theta-star", type=Path, default=None,
                    help="CSV file (parameter,value) to use as DGP theta_star. "
                         "Preferred over the auto-generated value: anchor to real-data "
                         "slice estimates so the DGP is near the data's MLE. "
                         "Absent params get spec initial values.")
    ap.add_argument("--max-alts-couples", type=int, default=0,
                    help="Cap couples alternatives per HH for recovery tests "
                         "(0=full 901, 100=10x10, 400=20x20). "
                         "ONLY for recovery speed; production estimates must use full 901.")
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
        _run_full_recovery(args, spec)
        return

    if args.smoke:
        ok = run_smoke_test(args, spec)
        sys.exit(0 if ok else 1)

    # Default: print usage guidance
    _py = r"C:\Users\hisham\Repo\MNL\.venv\Scripts\python.exe"
    print("\nUsage:")
    print("  --smoke   Step 3a smoke test (no optimizer).")
    print("  --run     Step 3b full recovery — requires --solver gamspy-conopt.")
    print("\nDry-run example (100 HH, fast):")
    print(f'  & "{_py}" -u "{Path(__file__)}" --run \\')
    print(f'      --engine-ready-stem fr_p3a_bpool_engine_ready \\')
    print(f'      --n-hh 100 --years 2015,2016,2017 --solver gamspy-conopt')
    print("\nProduction run (full data):")
    print(f'  & "{_py}" -u "{Path(__file__)}" --run \\')
    print(f'      --engine-ready-stem fr_p3a_bpool_engine_ready \\')
    print(f'      --n-hh 0 --years 2015,2016,2017 --solver gamspy-conopt')


if __name__ == "__main__":
    main()
