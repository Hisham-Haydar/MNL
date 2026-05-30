"""
CONOPT model-generation benchmark for the RURO joint likelihood.

PURPOSE
-------
The joint recovery gate (joint_recovery_test.py --run) spends most of its wall
time in GAMS/GAMSPy MODEL GENERATION for the 49-parameter joint likelihood over
~3.5M alternative rows (couples block dominates). Each of Checks 2, 4-warm,
4-cold, 6 rebuilds a fresh Container + Model, so generation is paid ~4x.

This module benchmarks ways to reduce that cost WITHOUT changing economics:
  1. Model REUSE across solves (build container+model once, reset variable
     levels/bounds, re-solve) vs REBUILD (fresh container per solve).
  2. Frozen-model feasibility probe (Model.freeze requires Parameters as
     modifiables; the 49 unknowns are Variables -> reports whether freeze is
     applicable without restructuring the likelihood).
  3. solve_link_type = "memory" vs "disk".
  4. threads in {1, 4, 8, 16, 28}.
  5. suppress_compiler_listing=True + write_listing_file=False.
  6. step_summary=True with model_generation_time / solve_model_time /
     total_solve_time separated from the GAMSPy model object.

GUARANTEE: this module imports and calls the SAME internal expression builders
(_build_singles_ll_vectorized, _build_couples_ll_vectorized,
_apply_expression_constraints) that production uses. The likelihood formula,
parameter names, bounds, and theta_star are untouched. Every variant ASSERTS
the recovered LL matches a reference within 1e-6, proving no economic change.

It does NOT touch joint_recovery_test.py, the spec, or the recovery thresholds.

USAGE
-----
  # Capped probe first (fast):
  python bench_conopt_modelgen.py --n-hh 300 --couples-stem fr_p3a_bpool_engine_ready_20x20

  # Full data (slow; same scale as the real gate):
  python bench_conopt_modelgen.py --n-hh 0 --couples-stem fr_p3a_bpool_engine_ready_20x20
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

_DEFAULT_THREADS = min(28, os.cpu_count() or 1)
os.environ.setdefault("NUMBA_NUM_THREADS", str(_DEFAULT_THREADS))

import numpy as np  # noqa: E402

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp                  # noqa: E402
import gamspy_estimation_vectorized as gev           # noqa: E402

# Reuse the joint harness's data loading + theta_star so the benchmark runs on
# EXACTLY the data the recovery gate uses. (No estimation logic imported.)
import joint_recovery_test as jrt                    # noqa: E402

from gamspy import Container, Model, Variable, Options  # noqa: E402


# ---------------------------------------------------------------------------
# Build the joint model (container + ll expr + model) — mirrors
# estimate_joint_vectorized_gamspy steps 1-3 EXACTLY, with timing hooks.
# ---------------------------------------------------------------------------
def build_joint_model(spec, data_sm, data_sf, data_cou, theta_init, logger=None):
    """
    Construct Container, 49 parameter Variables, the joint LL expression, and the
    Model. Returns (container, model, param_vars, build_times). Identical
    expressions to production -> identical LL.
    """
    import logging
    logger = logger or logging.getLogger("bench")
    t = {}

    t0 = time.time()
    gev.ensure_local_workdir()
    container = Container()
    t["container_create"] = time.time() - t0

    # 49 parameter variables (free), levels = theta_init, bounds from spec.
    t0 = time.time()
    param_vars = {}
    for i, pname in enumerate(spec.all_param_names):
        var = Variable(container, pname, type="free")
        var.l = float(theta_init[i])
        if pname in spec.bounds:
            lb, ub = spec.bounds[pname]
            if lb is not None:
                var.lo = float(lb)
            if ub is not None:
                var.up = float(ub)
        param_vars[pname] = var
    t["param_vars"] = time.time() - t0

    # Build the three group LL expressions (the heavy Python-side expression build)
    t0 = time.time()
    ll_sm, _ = gev._build_singles_ll_vectorized(
        container=container, data=data_sm, spec=spec, param_vars=param_vars,
        group="singles_male", prefix="sm_", logger=logger)
    ll_sf, _ = gev._build_singles_ll_vectorized(
        container=container, data=data_sf, spec=spec, param_vars=param_vars,
        group="singles_female", prefix="sf_", logger=logger)
    ll_cou, _ = gev._build_couples_ll_vectorized(
        container=container, data=data_cou, spec=spec, param_vars=param_vars,
        prefix="cou_", logger=logger)
    ll_joint = ll_sm + ll_sf + ll_cou
    ll_joint, hard_eqs = gev._apply_expression_constraints(
        container=container, spec=spec, param_vars=param_vars, ll_expr=ll_joint,
        active_groups=("singles_male", "singles_female", "couples_male",
                       "couples_female", "couples_household"),
        name_prefix="joint", logger=logger)
    t["ll_expr_build"] = time.time() - t0

    t0 = time.time()
    if hard_eqs:
        model = Model(container, name="ruro_joint_bench", problem="nlp",
                      sense="max", equations=hard_eqs, objective=ll_joint)
    else:
        model = Model(container, name="ruro_joint_bench", problem="nlp",
                      sense="max", objective=ll_joint)
    t["model_create"] = time.time() - t0

    return container, model, param_vars, t


def _reset_starts_and_bounds(param_vars, spec, theta_init):
    """Reset variable levels (theta start) and bounds in place for model reuse."""
    for i, pname in enumerate(spec.all_param_names):
        v = param_vars[pname]
        v.l = float(theta_init[i])
        if pname in spec.bounds:
            lb, ub = spec.bounds[pname]
            if lb is not None:
                v.lo = float(lb)
            if ub is not None:
                v.up = float(ub)


def _solve_and_time(model, param_vars, spec, options, solver="conopt"):
    """Solve once; return (theta_hat, ll, timing dict from the model object)."""
    t0 = time.time()
    model.solve(solver=solver, options=options)
    wall = time.time() - t0
    theta_hat = np.array([gev._extract_var_level(param_vars[p])
                          for p in spec.all_param_names])
    ll = getattr(model, "objective_value", None)
    timing = {
        "wall_solve_call": wall,
        "model_generation_time": getattr(model, "model_generation_time", None),
        "solve_model_time": getattr(model, "solve_model_time", None),
        "total_solve_time": getattr(model, "total_solve_time", None),
        "total_solver_time": getattr(model, "total_solver_time", None),
        "algorithm_time": getattr(model, "algorithm_time", None),
        "num_iterations": gev._extract_num_iterations(model),
        "ll": float(ll) if ll is not None else None,
        "solve_status": str(getattr(model, "solve_status", "")),
        "model_status": str(getattr(model, "status", "")),
    }
    return theta_hat, ll, timing


def _mk_options(solve_link: str, threads: int, suppress_listing: bool,
                step_summary: bool) -> Options:
    return Options(
        solve_link_type=solve_link,
        threads=threads,
        suppress_compiler_listing=suppress_listing,
        write_listing_file=not suppress_listing,
        step_summary=step_summary,
    )


# ---------------------------------------------------------------------------
# Benchmark driver
# ---------------------------------------------------------------------------
def run_benchmark(args) -> dict:
    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    rng = np.random.default_rng(args.seed)
    years = ([] if args.years.strip().lower() == "all"
             else [int(y) for y in args.years.split(",")])

    # theta_star (DGP) loaded the same way the gate loads it
    ts_path = Path(args.theta_star) if args.theta_star else None
    if ts_path and ts_path.exists():
        theta_star = jrt.load_theta_star_from_csv(ts_path, spec)
    else:
        theta_star = jrt.generate_theta_star(spec, rng)

    # cold start = spec init values (same as Check 4 cold)
    theta_cold = np.array([float(spec.initial_values.get(n, 0.0)) for n in pnames])

    print(f"\n{'='*72}\nCONOPT MODEL-GEN BENCHMARK\n{'='*72}")
    print(f"  spec   : {getattr(spec,'name','?')} ({len(pnames)} params)")
    print(f"  stem   : {args.engine_ready_stem}  couples_stem={args.couples_stem}")
    print(f"  years  : {args.years}   n_hh: {args.n_hh}")

    # Load data ONCE — synthetic DGP installed (same as Check 1 in the gate)
    print("\nLoading data ...")
    t0 = time.time()
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh,
        couples_stem=args.couples_stem)
    print(f"  loaded in {time.time()-t0:.1f}s  "
          f"sm={data_sm.n_groups} sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts/HH={data_cou.n_obs // max(data_cou.n_groups,1)})")
    n_alt_rows = data_sm.n_obs + data_sf.n_obs + data_cou.n_obs
    print(f"  total alternative rows: {n_alt_rows:,}")

    # Synthetic choices from theta_star (so the LL is well-posed; identical to gate)
    data_sm, data_sf, data_cou = jrt.run_synthetic_dgp(
        spec, data_sm, data_sf, data_cou, theta_star, rng)

    results = {"meta": {
        "n_params": len(pnames),
        "n_alt_rows": int(n_alt_rows),
        "n_hh": {"sm": data_sm.n_groups, "sf": data_sf.n_groups, "cou": data_cou.n_groups},
        "couples_alts": data_cou.n_obs // max(data_cou.n_groups, 1),
        "years": args.years,
    }, "configs": []}

    reference_ll = None

    def _record(label, theta_hat, ll, timing, extra=None):
        nonlocal reference_ll
        if ll is not None:
            if reference_ll is None:
                reference_ll = float(ll)
                ll_match = True
            else:
                ll_match = abs(float(ll) - reference_ll) < 1e-6
        else:
            ll_match = None
        row = {"label": label, "ll_match_reference": ll_match, **timing}
        if extra:
            row.update(extra)
        results["configs"].append(row)
        mg = timing.get("model_generation_time")
        sm = timing.get("solve_model_time")
        print(f"  [{label}]  wall={timing['wall_solve_call']:.1f}s  "
              f"modelgen={mg if mg is None else round(mg,1)}s  "
              f"solve={sm if sm is None else round(sm,1)}s  "
              f"iters={timing.get('num_iterations')}  "
              f"LL={None if ll is None else round(float(ll),3)}  "
              f"match={ll_match}")
        return ll_match

    # ----- PART A: option matrix on a SINGLE solve (fresh model each) -----
    print(f"\n--- PART A: option matrix (fresh model per solve) ---")
    if args.full_matrix:
        link_opts = ["disk", "memory"]
        thread_opts = [int(x) for x in args.threads_list.split(",")]
    else:
        # Lean probe: memory vs disk at default threads + thread sweep at memory
        link_opts = ["disk", "memory"]
        thread_opts = [int(x) for x in args.threads_list.split(",")]

    # baseline: disk, 1 thread, listing on, no step summary  (closest to current prod)
    container, model, pvars, bt = build_joint_model(spec, data_sm, data_sf, data_cou, theta_star)
    opt = Options(solve_link_type="disk", threads=1,
                  suppress_compiler_listing=False, write_listing_file=True,
                  step_summary=args.step_summary)
    th, ll, tm = _solve_and_time(model, pvars, spec, opt)
    tm.update({"build_" + k: v for k, v in bt.items()})
    _record("A.baseline_disk_t1_listing-on", th, ll, tm,
            extra={"solve_link": "disk", "threads": 1, "suppress_listing": False})

    # listing suppression at disk/1
    container, model, pvars, bt = build_joint_model(spec, data_sm, data_sf, data_cou, theta_star)
    opt = _mk_options("disk", 1, suppress_listing=True, step_summary=args.step_summary)
    th, ll, tm = _solve_and_time(model, pvars, spec, opt)
    tm.update({"build_" + k: v for k, v in bt.items()})
    _record("A.disk_t1_listing-off", th, ll, tm,
            extra={"solve_link": "disk", "threads": 1, "suppress_listing": True})

    # solve_link x threads sweep (listing always suppressed for speed)
    for link in link_opts:
        for nth in thread_opts:
            label = f"A.{link}_t{nth}_listing-off"
            container, model, pvars, bt = build_joint_model(
                spec, data_sm, data_sf, data_cou, theta_star)
            opt = _mk_options(link, nth, suppress_listing=True,
                              step_summary=args.step_summary)
            th, ll, tm = _solve_and_time(model, pvars, spec, opt)
            tm.update({"build_" + k: v for k, v in bt.items()})
            _record(label, th, ll, tm,
                    extra={"solve_link": link, "threads": nth, "suppress_listing": True})

    # ----- PART B: model REUSE across 3 solves (build once, reset, re-solve) -----
    # This is the Checks-2/4warm/4cold case: SAME data, different starts/bounds.
    print(f"\n--- PART B: model reuse (build once, 3 solves: warm, warm, cold) ---")
    best_link = "memory"  # memory generally best for repeated in-process solves
    container, model, pvars, bt = build_joint_model(
        spec, data_sm, data_sf, data_cou, theta_star)
    print(f"  [reuse] one-time build: "
          f"ll_expr={bt['ll_expr_build']:.1f}s model_create={bt['model_create']:.1f}s")
    reuse_opt = _mk_options(best_link, args.reuse_threads, suppress_listing=True,
                            step_summary=args.step_summary)
    for k, start_vec, tag in [(1, theta_star, "warm1"),
                              (2, theta_star, "warm2"),
                              (3, theta_cold, "cold")]:
        _reset_starts_and_bounds(pvars, spec, start_vec)
        th, ll, tm = _solve_and_time(model, pvars, spec, reuse_opt)
        tm.update({"reuse_solve_index": k,
                   "build_ll_expr_build": bt["ll_expr_build"],
                   "build_model_create": bt["model_create"]})
        _record(f"B.reuse_{tag}", th, ll, tm,
                extra={"solve_link": best_link, "threads": args.reuse_threads,
                       "reuse": True})

    # ----- PART C: FROZEN MODEL (model instance) — executed, not just probed -----
    # GAMSPy docs (advanced/model_instance): freeze generates the model instance
    # ONCE and re-solves repeatedly without regeneration. modifiables accepts
    # variable attributes .l/.lo/.up (each an ImplicitParameter), and .l is
    # "mainly used for starting non-linear models from different starting points"
    # -- exactly the warm/cold case. CONOPT has no frozen-model limitations.
    # This branch MEASURES whether model_generation_time collapses on solves 2-3.
    print(f"\n--- PART C: FROZEN MODEL (freeze once, re-solve warm/warm/cold) ---")
    results["freeze_executed"] = False
    try:
        _fc_container, fc_model, fc_pvars, fc_bt = build_joint_model(
            spec, data_sm, data_sf, data_cou, theta_star)
        print(f"  [freeze] one-time build: "
              f"ll_expr={fc_bt['ll_expr_build']:.1f}s")

        # Modifiables: the level (.l), lower (.lo), upper (.up) of every param var.
        modifiables = []
        for pname in spec.all_param_names:
            v = fc_pvars[pname]
            modifiables += [v.l, v.lo, v.up]

        fc_opt = _mk_options(best_link, args.reuse_threads, suppress_listing=True,
                             step_summary=args.step_summary)
        t_freeze0 = time.time()
        fc_model.freeze(modifiables=modifiables)
        freeze_call_s = time.time() - t_freeze0
        print(f"  [freeze] freeze() call: {freeze_call_s:.1f}s")

        def _set_frozen_start(start_vec):
            # Assign scalar level/bounds on the frozen instance's modifiables.
            for i, pname in enumerate(spec.all_param_names):
                v = fc_pvars[pname]
                v.l = float(start_vec[i])
                if pname in spec.bounds:
                    lb, ub = spec.bounds[pname]
                    if lb is not None:
                        v.lo = float(lb)
                    if ub is not None:
                        v.up = float(ub)

        for k, start_vec, tag in [(1, theta_star, "warm1"),
                                  (2, theta_star, "warm2"),
                                  (3, theta_cold, "cold")]:
            _set_frozen_start(start_vec)
            t0 = time.time()
            fc_model.solve(solver="conopt", options=fc_opt)
            wall = time.time() - t0
            theta_hat = np.array([gev._extract_var_level(fc_pvars[p])
                                  for p in spec.all_param_names])
            ll = getattr(fc_model, "objective_value", None)
            tm = {
                "wall_solve_call": wall,
                "model_generation_time": getattr(fc_model, "model_generation_time", None),
                "solve_model_time": getattr(fc_model, "solve_model_time", None),
                "total_solve_time": getattr(fc_model, "total_solve_time", None),
                "num_iterations": gev._extract_num_iterations(fc_model),
                "ll": float(ll) if ll is not None else None,
                "freeze_solve_index": k,
                "freeze_call_s": freeze_call_s,
            }
            _record(f"C.frozen_{tag}", theta_hat, ll, tm,
                    extra={"solve_link": best_link, "threads": args.reuse_threads,
                           "frozen": True})

        fc_model.unfreeze()
        results["freeze_executed"] = True
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"  [freeze] EXCEPTION: {exc}")
        results["freeze_error"] = str(exc)
        results["freeze_traceback"] = tb

    return results


def _write_markdown(results: dict, out_path: Path) -> None:
    m = results["meta"]
    lines = [
        "# CONOPT model-generation benchmark — results",
        "",
        f"**Params:** {m['n_params']}  **Alt rows:** {m['n_alt_rows']:,}  "
        f"**Couples alts/HH:** {m['couples_alts']}  **Years:** {m['years']}",
        f"**HH:** sm={m['n_hh']['sm']} sf={m['n_hh']['sf']} cou={m['n_hh']['cou']}",
        "",
        "All configs solve the IDENTICAL likelihood; `ll_match` confirms no "
        "economic change (LL equal to reference within 1e-6).",
        "",
        "## Timing table",
        "",
        "| Config | link | thr | wall (s) | modelgen (s) | solve (s) | iters | LL match |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for c in results["configs"]:
        def _r(x):
            return "" if x is None else (f"{x:.1f}" if isinstance(x, float) else str(x))
        lines.append(
            f"| {c['label']} | {c.get('solve_link','')} | {c.get('threads','')} "
            f"| {_r(c.get('wall_solve_call'))} | {_r(c.get('model_generation_time'))} "
            f"| {_r(c.get('solve_model_time'))} | {c.get('num_iterations','')} "
            f"| {c.get('ll_match_reference')} |")
    # Frozen-model outcome: did model_generation_time collapse on re-solves?
    frozen_rows = [c for c in results["configs"]
                   if c.get("label", "").startswith("C.frozen_")]
    lines += ["", "## Frozen model (model instance) — did generation collapse?", ""]
    if results.get("freeze_executed") and frozen_rows:
        lines += [
            "Freeze generates the model instance ONCE; subsequent solves modify "
            "variable .l/.lo/.up and re-solve. If `modelgen` drops to ~0 on "
            "frozen_warm2 / frozen_cold, generation is skipped -> 4x solves pay "
            "generation once. LL match confirms no economic change.",
            "",
            "| Solve | wall (s) | modelgen (s) | solve (s) | iters | LL match |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for c in frozen_rows:
            def _r2(x):
                return "" if x is None else (f"{x:.1f}" if isinstance(x, float) else str(x))
            lines.append(
                f"| {c['label']} | {_r2(c.get('wall_solve_call'))} "
                f"| {_r2(c.get('model_generation_time'))} "
                f"| {_r2(c.get('solve_model_time'))} | {c.get('num_iterations','')} "
                f"| {c.get('ll_match_reference')} |")
        # verdict
        mg = [c.get("model_generation_time") for c in frozen_rows
              if c.get("model_generation_time") is not None]
        if len(mg) >= 2 and mg[0] and mg[1] is not None:
            collapse = mg[1] < 0.25 * mg[0]
            lines += ["", f"**Generation collapse on re-solve: "
                          f"{'YES' if collapse else 'NO'}** "
                          f"(solve1 modelgen={mg[0]:.1f}s -> solve2 modelgen={mg[1]:.1f}s)."]
    elif results.get("freeze_error"):
        lines += [f"Freeze raised an exception: `{results['freeze_error']}`",
                  "", "```", results.get("freeze_traceback", ""), "```"]
    else:
        lines += ["_Frozen-model branch did not execute._"]
    lines.append("")

    # Build-phase breakdown from the first config (one-time Python expr build)
    first = results["configs"][0] if results["configs"] else {}
    build_keys = {k: v for k, v in first.items() if k.startswith("build_")}
    if build_keys:
        lines += ["## One-time build-phase breakdown (Python expression build)", "",
                  "| Phase | seconds |", "|---|---:|"]
        for k, v in build_keys.items():
            lines.append(f"| {k.replace('build_','')} | "
                         f"{'' if v is None else round(float(v),2)} |")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[markdown] {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready_20x20")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=300,
                    help="HH/group cap for the probe (0 = full data).")
    ap.add_argument("--seed", type=int, default=20260530)
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--threads-list", default="1,4,8,16,28")
    ap.add_argument("--reuse-threads", type=int, default=8)
    ap.add_argument("--full-matrix", action="store_true",
                    help="Run the full link x threads matrix (default already does).")
    ap.add_argument("--step-summary", action="store_true",
                    help="Enable GAMS step_summary in solve options.")
    ap.add_argument("--report", type=Path,
                    default=(_script_dir.parent.parent / "docs" / "France_case" / "P3a"
                             / "execution_logs" / "Bpool"
                             / "RURO_conopt_modelgen_benchmark.md"))
    ap.add_argument("--out-json", type=Path, default=None)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    results = run_benchmark(args)
    _write_markdown(results, args.report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_json, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"[json] {args.out_json}")

    # Final: confirm all LL matched reference (no economic change)
    matches = [c["ll_match_reference"] for c in results["configs"]
               if c["ll_match_reference"] is not None]
    all_match = all(matches) if matches else False
    print(f"\nLL-equality across all configs: {'PASS' if all_match else 'FAIL'} "
          f"({sum(matches)}/{len(matches)} matched reference)")
    sys.exit(0 if all_match else 1)


if __name__ == "__main__":
    main()
