"""
Step 4 — real-data joint MNL baseline estimate (the paper baseline).

Runs the certified 47-param spec (estimation_spec_joint_pooled_v1_bll0_tlmpin:
beta_ll=0, theta_l_m=-0.8 pinned) on REAL observed choices, full pooled
2015-2017, couples at production 901-alt resolution. Authorized by the 901
Check-5 re-gate (RURO_jax_recovery_gate_tlmpin_901_v1.md, PD min_eig +1.706).

NARROW scope — the single certified-baseline estimate. NO spec exploration, NO
external data, NO welfare. Backend: validated JAX (jax_ll_probe builders), the
same machine-precision path the gate used. CONSTRAINED two-stage optimizer
(scipy L-BFGS-B box-constrained -> optimistix BFGS polish), warm-started from
theta_star, with a bounds-projection guard so the polish cannot escape bounds.

DELIVERABLES produced here:
  1. Full 47-param estimate: converged negLL, max|grad|, in-bounds confirm,
     parameter table.
  2. BOTH SE flavors:
       - unclustered: Hessian-based (exact jax.hessian at the MLE), SE=sqrt(diag(H^-1))
       - idorighh-clustered: cluster-robust sandwich V = H^-1 B H^-1,
         B = sum_j s_j s_j', s_j = sum_{g in cluster j} score_g
         (scores via jax.jacrev of the per-group LL vector; cluster_ids =
         data.cluster_ids == idorighh). Report both + ratio, grouped by block.
       Expected asymmetry (from the 901 gate): shared OPPORTUNITY block tight;
       SINGLES-LEISURE block wide (flattest directions). Confirmed + reported.
  4. beta_l0_m reading: interior (small-but-present couples-male baseline
     leisure preference) or at its 1e-6 floor (effectively absent)? Reported
     with its gradient. Not pre-assumed.

  (Deliverable 3, the LR pooling test for beta_E/beta_h_pt2, is run by a
  separate step once the gender-relaxation design is fixed — it requires a
  spec/routing decision, not just a re-fit.)

Hessian MUST be PD at the real-data MLE. If non-PD despite the synthetic gate
passing, STOP and report (real data revealing a flat direction the synthetic
DGP didn't is a real signal).

USAGE:
  python step4_realdata_baseline.py \
    --spec specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml \
    --couples-stem fr_p3a_bpool_engine_ready --n-hh 0 \
    --out-csv specs/theta_hat_realdata_901_v1.csv \
    --report ../../docs/France_case/P3a/execution_logs/Bpool/RURO_realdata_2016_2017_joint_901_v1.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp          # noqa: E402
import joint_recovery_test as jrt            # noqa: E402

import jax                                    # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp                       # noqa: E402

from jax_ll_probe import build_jax_singles_ll, build_jax_couples_ll  # noqa: E402
from jax_joint_hessian import build_joint_neg_ll  # noqa: E402


# ---- block partition (for grouped SE reporting) ----
def _classify_block(name: str) -> str:
    """Map a param name to a reporting block. Spec-driven by suffix/prefix."""
    if name.endswith("_sm") or name.endswith("_sf") or name == "theta_c_singles":
        return "singles_leisure"
    if name.endswith("_m") or name.endswith("_f"):
        # couples-leisure preference (incl. occupation beta_occ_*_m/_f? no — occ is opportunity)
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


def _bounds_list(spec):
    out = []
    for n in spec.all_param_names:
        lo, hi = spec.bounds.get(n, (None, None))
        out.append((None if lo is None else float(lo),
                    None if hi is None else float(hi)))
    return out


def _two_stage_optimize(joint, theta0, bnds, gtol, maxiter, pnames,
                       checkpoint_csv=None):
    """scipy L-BFGS-B (box) -> optimistix BFGS polish, projected back in-bounds.
    Returns (theta_hat, negLL, max|grad|, which_optimizer).

    checkpoint_csv: if set, write the converged Stage-1 (scipy) theta there
    BEFORE the optimistix stage, so a Stage-2 failure can never lose the ~30-min
    scipy result. The final theta overwrites it on success."""
    jval = jax.jit(joint)
    jgrad = jax.jit(jax.grad(joint))

    def fun(x):
        return float(jval(jnp.asarray(x)))

    def grad(x):
        return np.asarray(jgrad(jnp.asarray(x)), dtype=np.float64)

    # warm compile
    _ = fun(theta0); _ = grad(theta0)
    print(f"  warm-start negLL = {fun(theta0):.6f}", flush=True)

    t0 = time.time()
    _it = {"k": 0}
    def cb(xk):
        _it["k"] += 1
        if _it["k"] % 25 == 0 or _it["k"] == 1:
            print(f"    [iter {_it['k']:4d}] negLL={fun(xk):.4f} "
                  f"max|g|={float(np.max(np.abs(grad(xk)))):.3e} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    print("  Stage 1: scipy L-BFGS-B (box-constrained) ...", flush=True)
    res = minimize(fun, theta0, jac=grad, method="L-BFGS-B", bounds=bnds,
                   callback=cb, options={"maxiter": maxiter, "gtol": gtol,
                                         "ftol": 1e-15, "maxls": 60})
    t_stage1 = time.time() - t0
    th_scipy = res.x
    ll_scipy = fun(th_scipy)
    g_scipy = float(np.max(np.abs(grad(th_scipy))))
    print(f"    Stage1 done {t_stage1:.0f}s negLL={ll_scipy:.6f} "
          f"max|g|={g_scipy:.3e} iters={res.nit}", flush=True)

    # checkpoint the scipy MLE so a Stage-2 crash never loses it
    if checkpoint_csv is not None:
        try:
            import csv as _csv
            Path(checkpoint_csv).parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_csv, "w", newline="") as f:
                w = _csv.writer(f); w.writerow(["parameter", "value"])
                for n, v in zip(pnames, th_scipy):
                    w.writerow([n, float(v)])
            print(f"    [checkpoint] scipy theta -> {checkpoint_csv}", flush=True)
        except Exception as exc:  # checkpoint is best-effort, never fatal
            print(f"    [checkpoint] WARN could not write: {exc}", flush=True)

    # Stage 2: optimistix BFGS (unconstrained) — kept only if it improves AND,
    # after projection back into bounds, the projected point is still better.
    import optimistix as optx
    print("  Stage 2: optimistix BFGS polish ...", flush=True)
    t0 = time.time()
    _t2_start = t0
    # NOTE: optimistix >=0.1.0 changed BFGS(verbose=...) — it no longer accepts a
    # frozenset, only True or a callable. The scipy callback above already streams
    # live iterations; optimistix is the fast final polish, so we omit verbose
    # (matching jax_recovery_gate.py's working call).
    sol = optx.minimise(lambda y, _a: joint(y),
                        optx.BFGS(rtol=gtol, atol=gtol),
                        jnp.asarray(th_scipy), max_steps=maxiter, throw=False)
    th_ox = np.asarray(sol.value, dtype=np.float64)
    th_ox_clip = th_ox.copy()
    n_clipped = 0
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None and th_ox_clip[i] < lo:
            th_ox_clip[i] = lo; n_clipped += 1
        if hi is not None and th_ox_clip[i] > hi:
            th_ox_clip[i] = hi; n_clipped += 1
    t_stage2 = time.time() - _t2_start
    ll_ox = fun(th_ox_clip)
    print(f"    Stage2 done {t_stage2:.0f}s negLL={ll_ox:.6f} "
          f"(clipped {n_clipped} coord(s)) result={sol.result}", flush=True)

    cands = [(ll_scipy, th_scipy, "scipy")]
    if np.isfinite(ll_ox):
        cands.append((ll_ox, th_ox_clip, "optimistix"))
    ll_best, th_best, which = min(cands, key=lambda c: c[0])
    g_best = float(np.max(np.abs(grad(th_best))))
    print(f"  -> chose {which}: negLL={ll_best:.6f} max|grad|={g_best:.3e}", flush=True)
    # diagnostics for the report: iters, fn-evals, per-stage + total times,
    # solver identity, and the FINAL gradient (scipy max|grad| -- the analogue
    # of CONOPT's RGmax for this solver family).
    diag = {
        "solver": "L-BFGS-B (scipy, box) -> optimistix BFGS polish (JAX)",
        "solver_family": "bfgs",
        "chosen_optimizer": which,
        "n_iterations": int(res.nit),
        "n_function_evaluations": int(res.nfev),
        "scipy_stage1_seconds": float(t_stage1),
        "optimistix_stage2_seconds": float(t_stage2),
        "estimation_seconds": float(t_stage1 + t_stage2),
        "final_max_grad": float(g_best),
        "scipy_final_max_grad": float(g_scipy),
        "gradient_kind": "max|grad| (analytical JAX gradient; scipy L-BFGS-B "
                         "stall floor -- the BFGS-family analogue of CONOPT RGmax)",
    }
    return th_best, ll_best, g_best, which, diag


def _slice_data_groups(data, g0, g1):
    """Shallow-copy a precomputed data object keeping only groups [g0, g1).

    All per-alternative arrays are laid out row-major (n_groups * n_alts,); we
    slice the corresponding [g0*n_alts, g1*n_alts) span and reset n_groups /
    n_obs / cluster_ids. Used to chunk score computation so jax.jacrev never
    materialises the full-dataset Jacobian (which is ~TB at 901 alts)."""
    import copy as _copy
    n_alts = int(data.n_obs // data.n_groups)
    a0, a1 = g0 * n_alts, g1 * n_alts
    d = _copy.copy(data)
    for attr in dir(data):
        if attr.startswith("_"):
            continue
        v = getattr(data, attr, None)
        if isinstance(v, np.ndarray):
            if v.shape and v.shape[0] == data.n_obs:
                setattr(d, attr, v[a0:a1])
            elif v.shape and v.shape[0] == data.n_groups:
                setattr(d, attr, v[g0:g1])
    d.n_groups = g1 - g0
    d.n_obs = (g1 - g0) * n_alts
    return d


def _chunked_scores(build_fn, data, spec, theta_hat, *, is_male=None,
                    chunk_groups=400, gender_split=None):
    """Per-group score matrix (n_groups, n_params) computed in group-chunks so
    jax.jacrev memory stays bounded. build_fn is build_jax_singles_ll or
    build_jax_couples_ll; is_male is passed through for the singles builder.
    gender_split is threaded through so the scores match the (possibly relaxed)
    joint LL used for the estimate + Hessian."""
    th = jnp.asarray(theta_hat, dtype=jnp.float64)
    n_groups = int(data.n_groups)
    out = []
    for g0 in range(0, n_groups, chunk_groups):
        g1 = min(g0 + chunk_groups, n_groups)
        dchunk = _slice_data_groups(data, g0, g1)
        if is_male is None:
            f, _ = build_fn(dchunk, spec, per_group=True, gender_split=gender_split)
        else:
            f, _ = build_fn(dchunk, spec, is_male=is_male, per_group=True,
                            gender_split=gender_split)
        out.append(np.asarray(jax.jacrev(f)(th)))
    return np.vstack(out)


def _clustered_sandwich(spec, data_sm, data_sf, data_cou, theta_hat, Hinv,
                        chunk_groups=400, gender_split=None):
    """Cluster-robust sandwich V = H^-1 B H^-1 with B = sum_j s_j s_j'.

    Per-group scores via jax.jacrev of the per-group POSITIVE-LL vector (the
    validated builders with per_group=True), computed in GROUP-CHUNKS so the
    Jacobian never materialises full-dataset-wide (that needs ~TB at 901 alts).
    Cluster key = data.cluster_ids (== idorighh).
    """
    th = jnp.asarray(theta_hat, dtype=jnp.float64)

    S_sm = _chunked_scores(build_jax_singles_ll, data_sm, spec, theta_hat,
                           is_male=True, chunk_groups=chunk_groups,
                           gender_split=gender_split)
    S_sf = _chunked_scores(build_jax_singles_ll, data_sf, spec, theta_hat,
                           is_male=False, chunk_groups=chunk_groups,
                           gender_split=gender_split)
    S_cou = _chunked_scores(build_jax_couples_ll, data_cou, spec, theta_hat,
                            chunk_groups=chunk_groups, gender_split=gender_split)
    scores = np.vstack([S_sm, S_sf, S_cou])

    cids = np.concatenate([
        np.asarray(data_sm.cluster_ids),
        np.asarray(data_sf.cluster_ids),
        np.asarray(data_cou.cluster_ids),
    ])
    n_groups = scores.shape[0]
    assert len(cids) == n_groups, (len(cids), n_groups)

    # SANITY: row-sum of scores must equal -grad(negLL) (the T1 identity), a
    # guard that the chunked scores are correct and aligned.
    # (computed by the caller's gradient; checked there if desired)

    # sum scores within cluster, then B = sum_j s_j s_j'
    uniq = np.unique(cids)
    n_params = scores.shape[1]
    B = np.zeros((n_params, n_params))
    # group rows by cluster id
    order = np.argsort(cids, kind="stable")
    cids_sorted = cids[order]
    scores_sorted = scores[order]
    boundaries = np.searchsorted(cids_sorted, uniq, side="left")
    boundaries = np.append(boundaries, n_groups)
    for k in range(len(uniq)):
        s_j = scores_sorted[boundaries[k]:boundaries[k + 1]].sum(axis=0)
        B += np.outer(s_j, s_j)

    V_cluster = Hinv @ B @ Hinv
    V_cluster = 0.5 * (V_cluster + V_cluster.T)

    # how many clusters have >1 group (the 2016-2017 repeat HHs)
    counts = np.array([boundaries[k + 1] - boundaries[k] for k in range(len(uniq))])
    cluster_summary = {
        "n_clusters": int(len(uniq)),
        "n_groups": int(n_groups),
        "n_multi_group_clusters": int(np.sum(counts > 1)),
        "max_groups_per_cluster": int(counts.max()),
    }
    return V_cluster, cluster_summary


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=0)
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--gtol", type=float, default=1e-6)
    ap.add_argument("--maxiter", type=int, default=3000)
    ap.add_argument("--out-csv", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=None)
    ap.add_argument("--gender-split", default="",
                    help="Comma list of hours-shifter base coefs to relax "
                         "male-vs-female (coef -> coef_m/coef_f), e.g. "
                         "'beta_E,beta_h_pt2'. The spec MUST declare the "
                         "gendered names (initial_values + bounds). Used to "
                         "estimate a pooling-relaxed baseline. Empty -> the "
                         "shared spec (default).")
    args = ap.parse_args()
    _run_t0 = time.time()  # total walltime (load + estimate + Hessian + sandwich)
    # gender_split: CLI override OR (default) the spec's own gender_split block
    # (spec-driven, agnostic). The two must be consistent with the spec's params.
    cli_gs = {c.strip() for c in args.gender_split.split(",") if c.strip()}

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}  "
          f"x64={jax.config.read('jax_enable_x64')}")
    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    # gender_split: prefer the CLI override; else the spec's own block (the
    # parser has already renamed beta_X -> beta_X_m/_f in all_param_names, so the
    # LL builders must apply the same split via gender_split).
    spec_gs = set(getattr(spec, "gender_split", []) or [])
    gender_split = cli_gs or spec_gs
    print(f"spec: {spec.name}  ({len(pnames)} params)  "
          f"fixed_params={dict(getattr(spec, 'fixed_params', {}) or {})}  "
          f"gender_split={sorted(gender_split)}")

    # ---- load REAL data ----
    t0 = time.time()
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh, couples_stem=args.couples_stem)
    cou_alts = data_cou.n_obs // data_cou.n_groups
    sm_alts = data_sm.n_obs // data_sm.n_groups
    print(f"loaded in {time.time()-t0:.1f}s  sm={data_sm.n_groups} "
          f"sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts={cou_alts}, singles alts={sm_alts})")
    # RESOLUTION GUARD: couples must be 901 (production 30x30), singles 101.
    if cou_alts != 901:
        raise SystemExit(f"STOP: couples alts/HH = {cou_alts}, expected 901 "
                         f"(production 30x30). Wrong --couples-stem? Got "
                         f"'{args.couples_stem}'.")
    print(f"  RESOLUTION GUARD: couples alts/HH = {cou_alts} (901 OK), "
          f"singles = {sm_alts}")

    # ---- warm start (theta_star, clamped in-bounds) ----
    bnds = _bounds_list(spec)
    theta0 = np.asarray(jrt.load_theta_star_from_csv(args.theta_star, spec),
                        dtype=np.float64)
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            theta0[i] = max(theta0[i], lo + 1e-9)
        if hi is not None:
            theta0[i] = min(theta0[i], hi - 1e-9)

    # ---- joint negLL (REAL data: col-0 observed-choice path, the validated one) ----
    joint = build_joint_neg_ll(spec, data_sm, data_sf, data_cou,
                               gender_split=gender_split or None)
    if gender_split:
        print(f"  [gender-split] relaxing {sorted(gender_split)} -> _m/_f")

    # ===== DELIVERABLE 1: estimate =====
    print("\n=== DELIVERABLE 1: real-data 47-param estimate ===")
    _ckpt = (args.out_csv.with_suffix(".scipy.csv")
             if args.out_csv is not None else None)
    theta_hat, negLL, gnorm, which, opt_diag = _two_stage_optimize(
        joint, theta0, bnds, args.gtol, args.maxiter, pnames,
        checkpoint_csv=_ckpt)

    # in-bounds + at-bound report
    at_bound = []
    for i, (lo, hi) in enumerate(bnds):
        v = theta_hat[i]
        if lo is not None and abs(v - lo) < 1e-5:
            at_bound.append((pnames[i], "lo", float(lo), float(v)))
        if hi is not None and abs(v - hi) < 1e-5:
            at_bound.append((pnames[i], "hi", float(hi), float(v)))
    out_of_bounds = []
    for i, (lo, hi) in enumerate(bnds):
        v = theta_hat[i]
        if lo is not None and v < lo - 1e-9:
            out_of_bounds.append((pnames[i], "below_lo", float(v), float(lo)))
        if hi is not None and v > hi + 1e-9:
            out_of_bounds.append((pnames[i], "above_hi", float(v), float(hi)))
    print(f"  converged negLL={negLL:.6f}  max|grad|={gnorm:.3e}  optimizer={which}")
    print(f"  in-bounds: {'PASS (all params within bounds)' if not out_of_bounds else 'FAIL ' + str(out_of_bounds)}")
    if at_bound:
        print(f"  params AT a bound ({len(at_bound)}): "
              f"{[(n, s) for n, s, _, _ in at_bound]}")

    # ===== exact Hessian @ MLE (PD verification + unclustered SE) =====
    print("\n=== Hessian @ MLE (PD verification + unclustered SE) ===")
    t0 = time.time()
    H = np.asarray(jax.jit(jax.hessian(joint))(jnp.asarray(theta_hat)))
    H = 0.5 * (H + H.T)
    t_hessian = time.time() - t0
    print(f"  jax.hessian {t_hessian:.1f}s")
    verdict = jrt._hessian_verdict(spec, H)
    eig = verdict["eig"]
    pd_ok = verdict["pd_ok"]
    print(f"  PD={pd_ok}  min_eig={float(eig.min()):.3e}  "
          f"cond={verdict['cond']:.3e}  verdict={verdict['verdict_str']}")
    if not pd_ok:
        print("\n  ** STOP CONDITION: Hessian NON-PD at the real-data MLE. **")
        print("  The synthetic gate passed but real data reveals a flat direction.")
        bd = verdict["bad_dirs"][0][1] if verdict["bad_dirs"] else []
        print(f"  flat direction loads on: "
              f"{', '.join(f'{n}({w:.2f})' for n, w in bd[:6])}")
        # still write what we have, then exit non-zero
    se_hess = verdict["se"]
    Hinv = verdict["cov"]

    # ===== DELIVERABLE 2: clustered SE (idorighh sandwich) =====
    print("\n=== DELIVERABLE 2: idorighh-clustered sandwich SE ===")
    t0 = time.time()
    V_cluster, csum = _clustered_sandwich(spec, data_sm, data_sf, data_cou,
                                          theta_hat, Hinv,
                                          gender_split=gender_split or None)
    t_sandwich = time.time() - t0
    se_clu = np.sqrt(np.maximum(np.diag(V_cluster), 0.0))
    print(f"  sandwich {t_sandwich:.1f}s  clusters={csum['n_clusters']} "
          f"groups={csum['n_groups']} multi-group-clusters="
          f"{csum['n_multi_group_clusters']} (max {csum['max_groups_per_cluster']}/cluster)")

    # ===== assemble parameter table, grouped by block =====
    blocks = {}
    for i, n in enumerate(pnames):
        b = _classify_block(n)
        blocks.setdefault(b, []).append(i)

    rows = []
    for i, n in enumerate(pnames):
        seh = float(se_hess[i]) if np.isfinite(se_hess[i]) else None
        sec = float(se_clu[i]) if np.isfinite(se_clu[i]) else None
        ratio = (sec / seh) if (seh and sec and seh > 0) else None
        rows.append({
            "param": n, "block": _classify_block(n),
            "estimate": float(theta_hat[i]),
            "se_hessian": seh, "se_clustered": sec, "clu_over_hess": ratio,
            "at_bound": any(n == ab[0] for ab in at_bound),
        })

    # block-level SE asymmetry summary
    block_se = {}
    for b, idx in blocks.items():
        sehs = [se_hess[i] for i in idx if np.isfinite(se_hess[i])]
        secs = [se_clu[i] for i in idx if np.isfinite(se_clu[i])]
        block_se[b] = {
            "n": len(idx),
            "median_se_hessian": float(np.median(sehs)) if sehs else None,
            "median_se_clustered": float(np.median(secs)) if secs else None,
            "max_se_hessian": float(np.max(sehs)) if sehs else None,
        }
    print("\n  SE by block (median Hessian-SE | median clustered-SE):")
    for b in ("market_hours_opp", "occupation_opp", "wage_opp",
              "couples_leisure", "singles_leisure", "other"):
        if b in block_se:
            d = block_se[b]
            mh = "n/a" if d["median_se_hessian"] is None else f"{d['median_se_hessian']:.4f}"
            mc = "n/a" if d["median_se_clustered"] is None else f"{d['median_se_clustered']:.4f}"
            print(f"    {b:<18} n={d['n']:<3} med_H={mh:<10} med_clu={mc}")

    # ===== DELIVERABLE 4: beta_l0_m reading =====
    print("\n=== DELIVERABLE 4: beta_l0_m reading ===")
    bl0m = None
    if "beta_l0_m" in pnames:
        ix = pnames.index("beta_l0_m")
        val = float(theta_hat[ix])
        lo, hi = bnds[ix]
        grad_full = np.asarray(jax.jit(jax.grad(joint))(jnp.asarray(theta_hat)))
        g_at = float(grad_full[ix])
        at_floor = (lo is not None and abs(val - lo) < 1e-5)
        bl0m = {"value": val, "floor": float(lo) if lo is not None else None,
                "gradient": g_at, "at_floor": bool(at_floor),
                "se_hessian": float(se_hess[ix]) if np.isfinite(se_hess[ix]) else None,
                "se_clustered": float(se_clu[ix]) if np.isfinite(se_clu[ix]) else None}
        reading = ("AT FLOOR (couples-male baseline leisure preference effectively absent)"
                   if at_floor else
                   "INTERIOR (small-but-present couples-male baseline leisure preference)")
        print(f"  beta_l0_m = {val:.6g}  (floor={lo})  gradient={g_at:.3e}  -> {reading}")
        print(f"    SE_hessian={bl0m['se_hessian']}  SE_clustered={bl0m['se_clustered']}")

    # ===== persist =====
    R = {
        "spec": spec.name, "n_params": len(pnames),
        "fixed_params": dict(getattr(spec, "fixed_params", {}) or {}),
        "n_hh": {"sm": data_sm.n_groups, "sf": data_sf.n_groups, "cou": data_cou.n_groups},
        "couples_alts": int(cou_alts), "singles_alts": int(sm_alts),
        "negLL": float(negLL), "max_grad": float(gnorm), "optimizer": which,
        "in_bounds": not out_of_bounds, "out_of_bounds": out_of_bounds,
        "at_bound": [(n, s, b) for n, s, b, v in at_bound],
        "hessian": {"pd": bool(pd_ok), "min_eig": float(eig.min()),
                    "cond": float(verdict["cond"]), "verdict": verdict["verdict_str"]},
        "cluster_summary": csum,
        "block_se": block_se,
        "beta_l0_m": bl0m,
        "params": rows,
        # solver / timing diagnostics for the post-estimation report
        "diagnostics": {
            **opt_diag,
            "hessian_seconds": float(t_hessian),
            "sandwich_seconds": float(t_sandwich),
            "post_estimation_seconds": float(t_hessian + t_sandwich),
            "total_seconds": float(time.time() - _run_t0),
        },
    }
    # Self-describing AGNOSTIC fields for the post-estimation report (so it needs
    # no hardcoded cluster name / spec param names). cluster_key is read off the
    # data object if it carries one, else a generic label. flat_directions = the
    # group-specific params with the largest clustered SE (the weak directions),
    # derived from the data, not hardcoded.
    _ckey = (getattr(data_cou, "cluster_id_name", None)
             or getattr(data_cou, "cluster_key", None) or "cluster")
    R["cluster_key"] = str(_ckey)
    _GROUPSPEC = {"couples_leisure", "singles_leisure"}
    _gp = [r for r in rows if r["block"] in _GROUPSPEC
           and r.get("se_clustered") is not None]
    _gp.sort(key=lambda r: -float(r["se_clustered"]))
    R["flat_directions"] = [r["param"] for r in _gp[:3]]

    if args.out_csv:
        import csv as _csv
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_csv, "w", newline="") as f:
            w = _csv.writer(f)
            w.writerow(["parameter", "value", "se_hessian", "se_clustered"])
            for r in rows:
                w.writerow([r["param"], r["estimate"], r["se_hessian"], r["se_clustered"]])
        print(f"\n  [csv] theta_hat + SEs -> {args.out_csv}")

    if args.report:
        _write_report(args.report, R)
        print(f"  [report] {args.report}")

    print("\n" + "=" * 72)
    print("STEP 4 BASELINE — SUMMARY")
    print(f"  negLL={negLL:.4f}  max|grad|={gnorm:.2e}  in-bounds={not out_of_bounds}")
    print(f"  Hessian PD={pd_ok}  min_eig={float(eig.min()):.3e}")
    if bl0m:
        print(f"  beta_l0_m={bl0m['value']:.4g} ({'floor' if bl0m['at_floor'] else 'interior'})")
    print("=" * 72)

    if not pd_ok:
        sys.exit(2)  # STOP condition signalled


def _fmt(x, nd=4):
    if x is None:
        return "—"
    return f"{x:.{nd}f}"


def _write_report(path, R):
    L = [f"# Step 4 — real-data joint baseline ({R['spec']})", "",
         f"**Params:** {R['n_params']}  **Couples alts:** {R['couples_alts']}  "
         f"**Singles alts:** {R['singles_alts']}  "
         f"**HH:** sm={R['n_hh']['sm']} sf={R['n_hh']['sf']} cou={R['n_hh']['cou']}",
         f"**Pinned:** {R['fixed_params']}", "",
         "> The certified-baseline real-data joint MNL estimate (paper baseline). "
         "47-param spec (beta_ll=0, theta_l_m=-0.8). REAL observed choices, pooled "
         "2015-2017, couples 901 (30x30), singles 101. JAX backend, constrained "
         "two-stage optimizer warm-started from theta_star. Authorized by the 901 "
         "Check-5 re-gate (RURO_jax_recovery_gate_tlmpin_901_v1.md, PD min_eig +1.706).",
         "",
         "## Deliverable 1 — estimate", "",
         f"- **negLL** = {R['negLL']:.6f}",
         f"- **max|grad|** = {R['max_grad']:.3e}  (optimizer: {R['optimizer']})",
         f"- **in-bounds**: {'PASS — all params within spec bounds' if R['in_bounds'] else 'FAIL: ' + str(R['out_of_bounds'])}",
         f"- **params at a bound**: {R['at_bound'] if R['at_bound'] else 'none (interior MLE)'}",
         "",
         "## Hessian @ MLE (PD verification)", "",
         f"- **PD** = {R['hessian']['pd']}  **min_eig** = {R['hessian']['min_eig']:.3e}  "
         f"**cond** = {R['hessian']['cond']:.3e}",
         f"- verdict: {R['hessian']['verdict']}",
         ("" if R['hessian']['pd'] else
          "\n> ** STOP: Hessian NON-PD on real data despite the synthetic gate "
          "passing — a flat direction the synthetic DGP did not reveal. Investigate "
          "before this is the baseline. **"),
         "",
         "## Deliverable 2 — both SE flavors", "",
         f"Clustered on **idorighh** (cluster_id == idorighh): "
         f"{R['cluster_summary']['n_clusters']} clusters over "
         f"{R['cluster_summary']['n_groups']} choice-sets; "
         f"{R['cluster_summary']['n_multi_group_clusters']} clusters span >1 "
         f"choice-set (the 2016-2017 repeat HHs; max "
         f"{R['cluster_summary']['max_groups_per_cluster']}/cluster). "
         "Sandwich V = H⁻¹ B H⁻¹, B = Σⱼ sⱼsⱼ′.", "",
         "### SE asymmetry by block (EXPECTED: opportunity tight, singles-leisure wide)",
         "", "| Block | n | median SE (Hessian) | median SE (clustered) |",
         "|---|---|---|---|"]
    for b in ("market_hours_opp", "occupation_opp", "wage_opp",
              "couples_leisure", "singles_leisure", "other"):
        if b in R["block_se"]:
            d = R["block_se"][b]
            L.append(f"| {b} | {d['n']} | {_fmt(d['median_se_hessian'])} | "
                     f"{_fmt(d['median_se_clustered'])} |")
    L += ["", "### Full parameter table", "",
          "| Param | Block | Estimate | SE (Hessian) | SE (clustered) | clu/H |",
          "|---|---|---|---|---|---|"]
    for r in R["params"]:
        star = " *" if r["at_bound"] else ""
        L.append(f"| {r['param']}{star} | {r['block']} | {r['estimate']:.5f} | "
                 f"{_fmt(r['se_hessian'])} | {_fmt(r['se_clustered'])} | "
                 f"{_fmt(r['clu_over_hess'], 2)} |")
    L += ["", "(* = param at a bound)", "",
          "## Deliverable 4 — beta_l0_m reading", ""]
    if R["beta_l0_m"]:
        b = R["beta_l0_m"]
        reading = ("**AT FLOOR** — couples-male baseline leisure preference "
                   "effectively absent" if b["at_floor"] else
                   "**INTERIOR** — small-but-present couples-male baseline "
                   "leisure preference")
        L += [f"- beta_l0_m = **{b['value']:.6g}** (floor = {b['floor']})",
              f"- gradient at MLE = {b['gradient']:.3e}",
              f"- SE (Hessian) = {_fmt(b['se_hessian'])}, SE (clustered) = {_fmt(b['se_clustered'])}",
              f"- **Reading: {reading}.**",
              "",
              "> At the 901 SYNTHETIC gate beta_l0_m was interior at +0.019 (did not "
              "jam its floor). This real-data reading is the finding the synthetic "
              "result anticipated — stated, not pre-assumed."]
    L += ["", "## Deliverable 3 — LR pooling test", "",
          "> Run separately once the gender-relaxation design for beta_E / "
          "beta_h_pt2 is fixed (it requires a spec/routing decision, not just a "
          "re-fit). Pending. Check 6 of the 901 gate flagged beta_E lands outside "
          "the group-specific range under forced sharing — the motivation for the test.",
          "", "## Full JSON", "", "```json", json.dumps(R, indent=2), "```", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
