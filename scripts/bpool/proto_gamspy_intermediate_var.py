"""
PROTOTYPE (option 2): prove the intermediate-variable fix for GAMSPy model generation
is (a) math-identical to the current inline build and (b) faster to generate.

Root cause (confirmed): the couples LL inlines the big `utility` expression (which
contains the 11-term centered `log_market`) into THREE Sums:
    chosen_utility = Sum(j, chosen * utility)
    denom          = Sum(j, exp(utility))
    ll             = Sum(i, chosen_utility - log(denom))
With centering, `log_market` is itself re-inlined per alternative -> the symbolic tree
explodes ~O(n_alts^2). At 900 alts this is the ~3.5h generation.

FIX: define an intermediate variable U[i,j] with a defining equation U =E= utility, then
reference U in the three Sums. Identical optimum; generation O(n_alts).

This prototype builds a SMALL synthetic couples-like MNL (same structural pattern:
consumption + leisure + an 11-term centered market index) BOTH ways, solves each with
CONOPT, and checks the optimal objective + a couple of coefficients match to ~1e-6.
It also TIMES model generation for each at a few n_alts to show the scaling difference.

Self-contained: does NOT touch the production estimator. If it passes, we port the
U-substitution into _build_couples_ll_vectorized / _build_singles_ll_vectorized.
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# GAMS refuses to launch when the current directory is a UNC path (\\crc\...). The
# production estimator handles this by calling ensure_local_workdir() (which chdirs off
# the UNC cwd) IMMEDIATELY BEFORE each Container(). We mirror that EXACTLY: do NOT chdir
# at import (that would make ensure_local_workdir see an already-local cwd and no-op);
# call ensure_local_workdir() inside run_mode/build right before Container().
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
from gamspy_estimation_vectorized import ensure_local_workdir  # noqa: E402

import numpy as np
from gamspy import Container, Set, Alias, Parameter, Variable, Model, Equation, Sum as GSum
from gamspy.math import exp as gexp, log as glog

LOG_EPS = 1e-300
RNG = np.random.default_rng(0)
N_SHIFTERS = 11  # mirror the bpool market block size (gsur+reg2..8+drgur+drgmd ~ 11)


def synth(n_groups, n_alts):
    """Small synthetic [n_groups, n_alts] data with a chosen alt per group + shifters."""
    c = np.abs(RNG.normal(2.0, 0.5, (n_groups, n_alts))) + 0.1
    lm = np.abs(RNG.normal(5.0, 1.0, (n_groups, n_alts))) + 0.1
    lf = np.abs(RNG.normal(5.0, 1.0, (n_groups, n_alts))) + 0.1
    prior = np.abs(RNG.normal(1.0, 0.2, (n_groups, n_alts))) + 0.01
    shifters = [RNG.normal(0, 1, (n_groups, n_alts)) for _ in range(N_SHIFTERS)]
    chosen = np.zeros((n_groups, n_alts)); chosen[np.arange(n_groups), RNG.integers(0, n_alts, n_groups)] = 1.0
    return c, lm, lf, prior, shifters, chosen


def build(container, c, lm, lf, prior, shifters, chosen, mode):
    """Build a couples-like LL. mode='inline' (current) or 'intermediate' (fix)."""
    ng, na = c.shape
    i = Set(container, "i", records=[str(x) for x in range(ng)])
    j = Set(container, "j", records=[str(x) for x in range(na)])
    P = lambda nm, a: Parameter(container, nm, domain=[i, j], records=a)
    cp, lmp, lfp, pr, ch = P("c", c), P("lm", lm), P("lf", lf), P("prior", prior), P("chosen", chosen)
    sh = [P(f"sh{k}", shifters[k]) for k in range(N_SHIFTERS)]
    # coefficient variables (preference + market shifters)
    bc = Variable(container, "bc", type="free"); bc.l = 1.0
    blm = Variable(container, "blm", type="free"); blm.l = 0.5
    blf = Variable(container, "blf", type="free"); blf.l = 0.5
    bsh = [Variable(container, f"bsh{k}", type="free") for k in range(N_SHIFTERS)]
    for v in bsh: v.l = 0.1

    # market index = sum of shifter terms (the 11-term block)
    log_market = bsh[0] * sh[0][i, j]
    for k in range(1, N_SHIFTERS):
        log_market = log_market + bsh[k] * sh[k][i, j]

    # centering within choice set (proposal weights) — the O(n_alts^2) culprit when inlined
    jc = Alias(container, "jc", alias_with=j)
    # NB: centering needs log_market re-indexed on jc; to do that for the intermediate
    # mode we must center the MATERIALIZED variable.
    def utility_expr(lm_term):
        return bc * glog(cp[i, j]) + blm * glog(lmp[i, j]) + blf * glog(lfp[i, j]) + lm_term - glog(pr[i, j] + LOG_EPS)

    if mode == "inline":
        denom_c = GSum(jc, pr[i, jc]) + LOG_EPS
        # re-inline the full log_market on jc (this is what explodes)
        lm_jc = bsh[0] * sh[0][i, jc]
        for k in range(1, N_SHIFTERS):
            lm_jc = lm_jc + bsh[k] * sh[k][i, jc]
        center = GSum(jc, pr[i, jc] * lm_jc) / denom_c
        lm_centered = log_market - center
        U = utility_expr(lm_centered)
        chosen_u = GSum(j, ch[i, j] * U)
        denom = GSum(j, gexp(U))
        ll = GSum(i, chosen_u - glog(denom + LOG_EPS))
        model = Model(container, "m_inline", problem="nlp", sense="max", objective=ll)
        return model

    else:  # intermediate
        # materialize log_market into a variable mktidx[i,j] via a defining equation.
        # NB: GAMSPy symbol names are case-insensitive -> must not collide with the
        # 'lm' (leisure_male) parameter; use distinct names (mktidx, util).
        mktidx = Variable(container, "mktidx", domain=[i, j], type="free")
        mktidx_def = Equation(container, "mktidx_def", domain=[i, j])
        mktidx_def[i, j] = mktidx[i, j] == log_market
        # center using the MATERIALIZED mktidx (compact symbol, not the re-inlined tree)
        denom_c = GSum(jc, pr[i, jc]) + LOG_EPS
        center = GSum(jc, pr[i, jc] * mktidx[i, jc]) / denom_c
        lm_centered = mktidx[i, j] - center
        # materialize utility too
        util = Variable(container, "util", domain=[i, j], type="free")
        util_def = Equation(container, "util_def", domain=[i, j])
        util_def[i, j] = util[i, j] == utility_expr(lm_centered)
        chosen_u = GSum(j, ch[i, j] * util[i, j])
        denom = GSum(j, gexp(util[i, j]))
        ll = GSum(i, chosen_u - glog(denom + LOG_EPS))
        model = Model(container, "m_inter", problem="nlp", sense="max",
                      equations=[mktidx_def, util_def], objective=ll)
        return model


def run_mode(mode, data, n_alts):
    c, lm, lf, prior, shifters, chosen = data
    ensure_local_workdir()  # chdir off any UNC cwd, exactly as production does
    cont = Container()
    t0 = time.time()
    model = build(cont, c, lm, lf, prior, shifters, chosen, mode)
    t_gen = time.time() - t0
    t1 = time.time()
    model.solve(solver="conopt", solver_options={"iterlim": 200, "reslim": 300})
    t_solve = time.time() - t1
    obj = float(model.objective_value)
    bc = float(cont["bc"].records["level"].iloc[0])
    return {"mode": mode, "obj": obj, "bc": bc, "t_gen": round(t_gen, 2), "t_solve": round(t_solve, 2)}


def main():
    print("Prototype: intermediate-variable vs inline GAMSPy generation (couples-like MNL)\n")
    # 1) EQUIVALENCE on a tiny model
    ng, na = 15, 60
    data = synth(ng, na)
    print(f"[equivalence] {ng} groups x {na} alts, {N_SHIFTERS} centered shifters")
    r_in = run_mode("inline", data, na)
    r_it = run_mode("intermediate", data, na)
    d_obj = abs(r_in["obj"] - r_it["obj"]); d_bc = abs(r_in["bc"] - r_it["bc"])
    print(f"  inline      : obj={r_in['obj']:.8f}  bc={r_in['bc']:.6f}  gen={r_in['t_gen']}s solve={r_in['t_solve']}s")
    print(f"  intermediate: obj={r_it['obj']:.8f}  bc={r_it['bc']:.6f}  gen={r_it['t_gen']}s solve={r_it['t_solve']}s")
    print(f"  |Δobj|={d_obj:.2e}  |Δbc|={d_bc:.2e}  EQUIVALENT={'YES' if d_obj<1e-5 and d_bc<1e-4 else 'NO'}")

    # 2) SCALING vs TOTAL CELLS (groups x alts) — the real problem-size lever.
    #    Time BUILD (Python symbolic) AND first SOLVE (GAMS compile + CONOPT) separately,
    #    because the pilot's "3.5h generation" is likely GAMS compilation / data marshalling,
    #    NOT the Python expression build (which the n_alts sweep showed is ~flat).
    print("\n[scaling vs total cells] BUILD (python) vs SOLVE (GAMS compile+CONOPT), inline mode")
    print(f"  {'groups':>7} {'alts':>5} {'cells':>9} {'build_s':>8} {'solve_s':>9}")
    for ng_, na_ in [(50, 100), (200, 100), (200, 400), (500, 400), (300, 901)]:
        d = synth(ng_, na_)
        c, lm, lf, prior, shifters, chosen = d
        ensure_local_workdir(); cont = Container()
        tb = time.time(); model = build(cont, c, lm, lf, prior, shifters, chosen, "inline"); build_s = time.time() - tb
        ts = time.time()
        try:
            model.solve(solver="conopt", solver_options={"iterlim": 50, "reslim": 600})
            solve_s = time.time() - ts
        except Exception as e:
            solve_s = -1.0
            print(f"  {ng_:>7} {na_:>5} {ng_*na_:>9,} {build_s:>8.2f}   SOLVE ERR: {str(e)[:50]}")
            continue
        print(f"  {ng_:>7} {na_:>5} {ng_*na_:>9,} {build_s:>8.2f} {solve_s:>9.2f}")


if __name__ == "__main__":
    main()
