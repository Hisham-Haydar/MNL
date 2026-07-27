"""Safety tests for the P2a region-live Phase-3 runner under the simplified
research-grade execution scope (FR_P2a_region_live_phase3_execution_scope_v1.md).

No test invokes the real optimizer. The canonical dry-run test (test 29) runs
in a subprocess and intentionally writes one preserved attempt bundle under the
production attempts/ history, consistent with the never-delete evidence
discipline; no other test writes any production output path. Estimator-route
tests monkeypatch scipy.optimize.minimize in-process. Adversarial-caller
defenses are out of scope by manager decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace as _NS

import numpy as np
import pytest
import yaml

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))

import run_p2a_regionlive_rebuild as runner  # noqa: E402

CONFIG_PATH = MNL_ROOT / "scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml"
TARGET = 19053.46553160094
OPTS = {"maxiter": 5000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10}
GOOD_REVIEW = ("# 1. Sixth-review verdict\n\n**FINAL VERDICT: APPROVE**\n\n"
               "# 2. Scope\n\ndetails\n")


@pytest.fixture(scope="module")
def cfg():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def _args(dry_run=True, **kw):
    base = dict(config=str(CONFIG_PATH), out=None, dry_run=dry_run, phase=3,
                execute_phase3=False, expected_mnl_head=None,
                expected_dclaborsupply_head=None, approved_review=None,
                approved_review_sha256=None)
    base.update(kw)
    return argparse.Namespace(**base)


def _names47():
    free = list(runner.EXPECTED_AT_BOUND_NAMES) + [f"dummy_{i:02d}" for i in range(35)]
    return list(runner.ACCEPTED_PIN_NAMES) + free


def _pmap():
    vals = {p: float(k + 1) for k, p in enumerate(runner.ACCEPTED_PIN_NAMES)}
    return runner.build_phase3_parameter_map(
        _names47(), list(runner.ACCEPTED_PIN_NAMES), vals)


def _bounds_full(pmap):
    return [(-1.0, 1.0) if n in runner.EXPECTED_AT_BOUND_NAMES else (-100.0, 100.0)
            for n in pmap["all_names"]]


def _theta_ok(pmap):
    theta = np.zeros(47)
    theta[pmap["pin_idx"]] = pmap["pin_values"]
    for n in runner.EXPECTED_AT_BOUND_NAMES:
        theta[pmap["name_idx"][n]] = 1.0
    return theta


def _gates_cfg(cfg):
    return cfg["phase3"]["gates"]


def _deep(cfg):
    return json.loads(json.dumps(cfg))


def _git(repo, *argv):
    r = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True,
                       text=True, timeout=30)
    assert r.returncode == 0, (argv, r.stderr)
    return r.stdout.strip()


# --------------------------------------------------------------------------- #
# parameter mapping and pins
# --------------------------------------------------------------------------- #
def test_01_mapping_counts_and_ordering():
    pmap = _pmap()
    assert len(pmap["all_names"]) == 47 and len(pmap["free_names"]) == 37
    assert tuple(pmap["pin_names"]) == runner.ACCEPTED_PIN_NAMES
    assert [pmap["all_names"][i] for i in pmap["free_idx"]] == pmap["free_names"]
    assert [pmap["all_names"][i] for i in pmap["pin_idx"]] == pmap["pin_names"]


def test_02_round_trip_and_pin_bitwise():
    pmap = _pmap()
    free = np.arange(37, dtype=np.float64) + 0.5
    full = runner.expand_free_to_full(pmap, free)
    assert np.array_equal(runner.project_full_to_free(pmap, full), free)
    for k in range(10):
        assert (np.float64(full[pmap["pin_idx"][k]]).tobytes()
                == np.float64(pmap["pin_values"][k]).tobytes())


def test_03_bad_pin_sets_refused():
    names, vals = _names47(), {p: 1.0 for p in runner.ACCEPTED_PIN_NAMES}
    for bad in (list(runner.ACCEPTED_PIN_NAMES[:9]) + [runner.ACCEPTED_PIN_NAMES[0]],
                list(reversed(runner.ACCEPTED_PIN_NAMES)),
                list(runner.ACCEPTED_PIN_NAMES[:9]) + ["beta_E"]):
        with pytest.raises(runner.StopRun):
            runner.build_phase3_parameter_map(names, bad, vals)


def test_04_real_spec_interleaved_ordering():
    from dclaborsupply import EstimationSpec
    spec = EstimationSpec.from_yaml(str(
        MNL_ROOT / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"))
    names = list(spec.all_param_names)
    assert [names.index(p) for p in runner.ACCEPTED_PIN_NAMES] == \
        [10, 11, 12, 13, 14, 15, 16, 17, 31, 32]


# --------------------------------------------------------------------------- #
# post-optimization gates (G-16, bounds, gradient, target)
# --------------------------------------------------------------------------- #
def test_05_gates_pass_and_expected_bounds(cfg):
    pmap = _pmap()
    gates, rows, status, stop = runner._phase3_post_gates(
        100.0, _theta_ok(pmap), np.zeros(47), pmap, _bounds_full(pmap),
        _gates_cfg(cfg), 100.0, True, "ok")
    assert status == "PHASE_3_COMPLETE" and stop is None
    assert gates["g15_bound_hits_detected"] == sorted(runner.EXPECTED_AT_BOUND_NAMES)
    assert gates["g_nonbound_free_count"] == 35 and gates["g16_inbounds_ok"]


def test_06_unexpected_bound_and_gradient_gates(cfg):
    pmap = _pmap()
    theta = _theta_ok(pmap)
    theta[pmap["name_idx"]["dummy_01"]] = 100.0
    gates, _r, status, stop = runner._phase3_post_gates(
        100.0, theta, np.zeros(47), pmap, _bounds_full(pmap), _gates_cfg(cfg),
        100.0, True, "ok")
    assert status == "STOPPED" and stop["gate"] == "G-15"
    grad = np.zeros(47)
    grad[pmap["name_idx"]["dummy_02"]] = 0.5
    gates, _r, status, stop = runner._phase3_post_gates(
        100.0, _theta_ok(pmap), grad, pmap, _bounds_full(pmap), _gates_cfg(cfg),
        100.0, True, "ok")
    assert status == "STOPPED" and stop["gate"] == "G-3"


def test_07_g16_exact_epsilon_boundaries(cfg):
    pmap = _pmap()
    lo, hi = -100.0, 100.0
    eps = runner.PHASE3_SAFETY_CONSTANTS["g16_inbounds_epsilon"]
    for v, expect_ok in ((lo - eps, True), (hi + eps, True),
                         (np.nextafter(lo - eps, -np.inf), False),
                         (np.nextafter(hi + eps, np.inf), False)):
        theta = _theta_ok(pmap)
        theta[pmap["name_idx"]["dummy_05"]] = v
        gates, rows, _s, _p = runner._phase3_post_gates(
            100.0, theta, np.zeros(47), pmap, _bounds_full(pmap), _gates_cfg(cfg),
            100.0, True, "ok")
        row = next(r for r in rows if r["param"] == "dummy_05")
        assert row["in_bounds"] == expect_ok
        assert gates["g16_inbounds_ok"] == expect_ok


def test_08_target_mismatch_status_immutable(cfg):
    pmap = _pmap()
    hacked = dict(_gates_cfg(cfg))
    hacked["target_mismatch_status"] = "PHASE_3_COMPLETE"
    for dev in (+1e-3, -1e-3):
        _g, _r, status, stop = runner._phase3_post_gates(
            100.0 + dev, _theta_ok(pmap), np.zeros(47), pmap, _bounds_full(pmap),
            hacked, 100.0, True, "ok")
        assert status == runner.PHASE3_TARGET_MISMATCH_STATUS and stop is None


def test_09_optimizer_contract_and_safety_constants(cfg):
    assert runner._validate_optimizer_contract(cfg)["options"] == OPTS
    assert runner._validate_safety_constants(cfg)
    for mutate in (lambda c: c["phase3"]["optimizer"]["options"].update(maxcor=10),
                   lambda c: c["phase3"]["optimizer"]["options"].update(maxls=60),
                   lambda c: c["phase3"]["gates"].update(pre_opt_objective_tol=1e-3),
                   lambda c: c["phase3"]["gates"].update(
                       target_mismatch_status="PHASE_3_COMPLETE"),
                   lambda c: c["targets"].update(negll_full=19053.5)):
        bad = _deep(cfg)
        mutate(bad)
        with pytest.raises(runner.StopRun):
            runner._validate_safety_constants(bad)


# --------------------------------------------------------------------------- #
# canonical paths, aliases, input authentication
# --------------------------------------------------------------------------- #
def test_10_canonical_out_and_config_refused(tmp_path):
    rc = runner.main(["--config", str(CONFIG_PATH), "--phase", "3",
                      "--out", str(tmp_path)])
    assert rc == 2 and list(tmp_path.iterdir()) == []
    copied = tmp_path / "copy.yaml"
    copied.write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    rc = runner.main(["--config", str(copied), "--phase", "3",
                      "--out", str(runner.CANONICAL_REGIONLIVE_ROOT)])
    assert rc == 2
    rc = runner.main(["--config", str(CONFIG_PATH), "--phase", "4"])
    assert rc == 2                                   # phases > 3 refused


def test_11_alias_mutations_refused(cfg):
    muts = [lambda c: c["certified_spec"].update(yaml="scripts/bpool/specs/x.yaml"),
            lambda c: c["warm_start"].update(theta_csv="theta_p2a_singles_2016_v2.csv"),
            lambda c: c["phase3"]["start_theta"].update(
                csv="theta_p2a_singles_2016_v2.csv"),
            lambda c: c["stored_region_live_theta"].update(
                v1_csv="theta_p2a_singles_2016_v2.csv")]
    for mut in muts:
        bad = _deep(cfg)
        mut(bad)
        with pytest.raises(runner.StopRun) as e:
            runner._phase3_contract(None, bad, CONFIG_PATH, lambda m: None)
        assert e.value.gate == "alias-identity"


def test_12_input_authentication_exact_map(tmp_path):
    f = tmp_path / "geom.parquet"
    f.write_bytes(b"data")
    sha = hashlib.sha256(b"data").hexdigest()
    rt = {"geometry_parquet": f}
    with pytest.raises(runner.StopRun):              # wrong configured path
        runner._authenticate_inputs(
            {"phase3": {"input_authentication": {
                "geometry_parquet": {"path": "somewhere/else.parquet",
                                     "sha256": sha}}}}, runtime_paths=rt)
    with pytest.raises(runner.StopRun):              # missing / extra labels
        runner._authenticate_inputs({"phase3": {"input_authentication": {}}},
                                    runtime_paths=rt)


def test_13_recheck_detects_mutation(tmp_path):
    f = tmp_path / "input.bin"
    f.write_bytes(b"original")
    sha = hashlib.sha256(b"original").hexdigest()
    rt = {"x": f}
    pre = {"x": {"runtime_path": str(f.resolve()), "actual": sha, "expected": sha}}
    _t, ok = runner._recheck_inputs(pre, runtime_paths=rt)
    assert ok
    f.write_bytes(b"tampered")
    _t, ok = runner._recheck_inputs(pre, runtime_paths=rt)
    assert not ok


# --------------------------------------------------------------------------- #
# transaction, lock, publication
# --------------------------------------------------------------------------- #
def test_14_success_bundle_immutable(tmp_path):
    txn = runner.Phase3Transaction(tmp_path / "p3", "estimate")
    txn.acquire()
    (txn.staging / "estimation_results.json").write_text("{}", encoding="utf-8")
    dest = txn.finish("PHASE_3_COMPLETE")
    txn.release()
    marker = hashlib.sha256((dest / "estimation_results.json").read_bytes()).hexdigest()
    txn2 = runner.Phase3Transaction(tmp_path / "p3", "estimate")
    txn2.acquire()
    (txn2.staging / "estimation_results.json").write_text('{"x":1}', encoding="utf-8")
    with pytest.raises(RuntimeError):
        txn2.finish("PHASE_3_COMPLETE")
    txn2.release()
    assert hashlib.sha256(
        (dest / "estimation_results.json").read_bytes()).hexdigest() == marker
    txn3 = runner.Phase3Transaction(tmp_path / "p3", "estimate")
    txn3.acquire()
    d3 = txn3.finish(runner.PHASE3_TARGET_MISMATCH_STATUS)
    txn3.release()
    assert d3.parent.name == "attempts"              # mismatch never publishes


def test_15_lock_contention_and_no_migration(tmp_path):
    root = tmp_path / "p3"
    root.mkdir()
    (root / ".phase3.lock").write_text("held", encoding="utf-8")
    legacy = root / "phase3_manifest.json"
    legacy.write_text("legacy", encoding="utf-8")
    txn = runner.Phase3Transaction(root, "dryrun")
    with pytest.raises(runner.StopRun):
        txn.acquire()
    assert legacy.read_text(encoding="utf-8") == "legacy"
    assert not (root / "attempts").exists()


def test_16_finalize_manifest_console_and_completeness(tmp_path, cfg):
    import time as _time
    root = tmp_path / "p3"
    txn = runner.Phase3Transaction(root, "estimate")
    txn.acquire()
    manifest = runner._phase3_manifest_skeleton(_args(dry_run=False), cfg, txn, {})
    assert manifest["review_gate"] == "AWAITING_REVIEW_V6_APPROVE"
    assert manifest["execution_ready"] is False
    # incomplete bundle: success downgraded, complete/ never created
    (txn.staging / "estimation_results.json").write_text("{}", encoding="utf-8")
    rc = runner._phase3_finalize(txn, manifest, ["line1"], _time.time(),
                                 "PHASE_3_COMPLETE", None, 0)
    assert rc == 2 and not (root / "complete").exists()
    d = next(x for x in (root / "attempts").iterdir())
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "STOPPED"
    assert man["stop"]["gate"] == "bundle-completeness"
    assert "phase3_manifest.json" not in man["artifact_hashes"]      # no self-hash
    console = (d / "phase3_console.log").read_text(encoding="utf-8")
    assert console.rstrip().endswith("FINAL STATUS: STOPPED")
    # complete bundle publishes the exact five-file set
    txn2 = runner.Phase3Transaction(root, "estimate")
    txn2.acquire()
    for n in ("theta_estimated.csv", "optimizer_diagnostics.json",
              "estimation_results.json"):
        (txn2.staging / n).write_text("x", encoding="utf-8")
    man2 = runner._phase3_manifest_skeleton(_args(dry_run=False), cfg, txn2, {})
    rc = runner._phase3_finalize(txn2, man2, ["go"], _time.time(),
                                 "PHASE_3_COMPLETE", None, 0)
    assert rc == 0
    pub = sorted(p.name for p in (root / "complete").iterdir())
    assert pub == sorted(list(runner.PHASE3_ARTIFACTS) + ["phase3_manifest.json"])


# --------------------------------------------------------------------------- #
# estimator route (scipy.optimize.minimize monkeypatched; never invoked)
# --------------------------------------------------------------------------- #
def _mk_ctx(tmp_path, monkeypatch, c0=0.0):
    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    tmp_path.mkdir(parents=True, exist_ok=True)
    from dclaborsupply import EstimationSpec
    spec = EstimationSpec.from_yaml(str(
        MNL_ROOT / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"))
    names = list(spec.all_param_names)
    pin_vals = {p: float(i + 1) for i, p in enumerate(runner.ACCEPTED_PIN_NAMES)}
    pmap = runner.build_phase3_parameter_map(
        names, list(runner.ACCEPTED_PIN_NAMES), pin_vals)
    bounds_full = [(-1.0, 1.0) if n in runner.EXPECTED_AT_BOUND_NAMES
                   else (-100.0, 100.0) for n in names]
    free_start = np.zeros(37)
    for k, n in enumerate(pmap["free_names"]):
        if n in runner.EXPECTED_AT_BOUND_NAMES:
            free_start[k] = 1.0
    start_full = runner.expand_free_to_full(pmap, free_start)
    center = jnp.asarray(start_full)

    def tot(t):
        return TARGET + c0 + 0.5 * jnp.sum((t - center) ** 2)

    f = tmp_path / "authinp.bin"
    f.write_bytes(b"frozen-input")
    sha = hashlib.sha256(b"frozen-input").hexdigest()
    rt = {"authinp": f}
    input_auth = {"authinp": {"runtime_path": str(f.resolve()), "actual": sha,
                              "expected": sha}}
    ev = {"optimizer_contract": {"method": "L-BFGS-B", "options": dict(OPTS)},
          "start_theta_raw_sha256": "x", "start_theta_applied_sha256": "y",
          "negll_start": TARGET + c0, "parameter_map": {"fake": True},
          "at_bound_expected_derived": list(runner.EXPECTED_AT_BOUND_NAMES)}
    return {"spec": None, "names": names, "pmap": pmap, "bounds_full": bounds_full,
            "bounds_free": [bounds_full[i] for i in pmap["free_idx"]],
            "theta_trial": start_full.copy(), "free_start": free_start,
            "theta_start_full": start_full, "tot": tot, "target": TARGET,
            "ev": ev, "input_auth": input_auth, "rtmap": rt,
            "rtmap_fingerprint": runner._runtime_map_fingerprint(rt),
            "_authfile": f}


class FakeMin:
    """Asserting stand-in patched over scipy.optimize.minimize (never the real one)."""

    def __init__(self, x_out=None, success=True, raise_after=False, mutate=None):
        self.x_out, self.success = x_out, success
        self.raise_after, self.mutate = raise_after, mutate
        self.called = False
        self.pmap = None

    def __call__(self, fun, x0, jac=None, method=None, bounds=None, options=None):
        self.called = True
        assert len(x0) == 37 and len(bounds) == 37 and jac is True
        assert method == "L-BFGS-B" and dict(options) == OPTS
        v0, g0 = fun(np.asarray(x0))
        k = next(i for i, n in enumerate(self.pmap["free_names"])
                 if n not in runner.EXPECTED_AT_BOUND_NAMES)
        e = np.array(x0, dtype=float)
        e[k] += 1.0
        v1, g1 = fun(e)
        assert abs((v1 - v0) - 0.5) < 1e-8 and abs(g1[k] - 1.0) < 1e-8
        assert abs(g0[k]) < 1e-8 and v0 >= 0
        if self.mutate is not None:
            self.mutate()
        if self.raise_after:
            raise RuntimeError("fake optimizer exploded after invocation")
        x = np.asarray(self.x_out if self.x_out is not None else x0, dtype=float)
        return _NS(x=x, success=self.success, status=0 if self.success else 2,
                   message="fake", nit=3, nfev=4, njev=4)


def _run_est(tmp_path, monkeypatch, cfg, fake, c0=0.0):
    import scipy.optimize
    ctx = _mk_ctx(tmp_path, monkeypatch, c0=c0)
    fake.pmap = ctx["pmap"]
    monkeypatch.setattr(scipy.optimize, "minimize", fake)
    staging = tmp_path / "staging"
    staging.mkdir()
    marks = []
    status, diag = runner._phase3_estimate(
        ctx, staging, cfg, lambda m: None,
        mark_optimizer_called=lambda: marks.append(True))
    return ctx, staging, marks, status, diag


def test_17_estimate_success_route(tmp_path, monkeypatch, cfg):
    fake = FakeMin()
    ctx, staging, marks, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert fake.called and marks == [True] and status == "PHASE_3_COMPLETE"
    assert diag["gates"]["g15_bound_hits_detected"] == sorted(
        runner.EXPECTED_AT_BOUND_NAMES)
    theta = np.asarray(diag["final_theta"])
    for k in range(10):
        assert (np.float64(theta[ctx["pmap"]["pin_idx"][k]]).tobytes()
                == np.float64(ctx["pmap"]["pin_values"][k]).tobytes())
    assert diag["rtmap_fingerprint"] == diag["rtmap_fingerprint_post"]
    assert (staging / "estimation_results.json").is_file()


def test_18_estimate_failure_routes(tmp_path, monkeypatch, cfg):
    _c, _s, marks, status, diag = _run_est(tmp_path / "a", monkeypatch, cfg,
                                           FakeMin(success=False))
    assert status == "STOPPED" and diag["stop"]["gate"] == "G-2" and marks == [True]
    _c, staging, marks, status, diag = _run_est(tmp_path / "b", monkeypatch, cfg,
                                                FakeMin(raise_after=True))
    assert status == "STOPPED" and diag["stop"]["gate"] == "optimizer-exception"
    assert marks == [True]                    # optimizer_called set pre-invocation
    assert not (staging / "estimation_results.json").exists()


def test_19_estimate_target_mismatch_both_directions(tmp_path, monkeypatch, cfg):
    for sub, c0 in (("hi", +1e-3), ("lo", -1e-3)):
        _c, _s, _m, status, diag = _run_est(tmp_path / sub, monkeypatch, cfg,
                                            FakeMin(), c0=c0)
        assert status == runner.PHASE3_TARGET_MISMATCH_STATUS
        assert diag["gates"]["g1_ok"] is False


def test_20_estimate_input_mutation_s8(tmp_path, monkeypatch, cfg):
    holder = {}
    fake = FakeMin(mutate=lambda: holder["f"].write_bytes(b"TAMPERED"))
    import scipy.optimize
    ctx = _mk_ctx(tmp_path, monkeypatch)
    holder["f"] = ctx["_authfile"]
    fake.pmap = ctx["pmap"]
    monkeypatch.setattr(scipy.optimize, "minimize", fake)
    staging = tmp_path / "staging"
    staging.mkdir()
    status, diag = runner._phase3_estimate(ctx, staging, cfg, lambda m: None,
                                           mark_optimizer_called=lambda: None)
    assert status == "STOPPED" and diag["stop"]["code"] == "S-8"
    assert list(staging.iterdir()) == []


def test_21_single_runtime_map_threading(tmp_path, monkeypatch, cfg):
    ctx = _mk_ctx(tmp_path, monkeypatch)
    calls = {"n": 0}

    def factory():
        calls["n"] += 1
        return {"other": tmp_path / "changed.bin"}

    monkeypatch.setattr(runner, "_phase3_runtime_paths", factory)
    import scipy.optimize
    fake = FakeMin()
    fake.pmap = ctx["pmap"]
    monkeypatch.setattr(scipy.optimize, "minimize", fake)
    staging = tmp_path / "staging"
    staging.mkdir()
    status, diag = runner._phase3_estimate(ctx, staging, cfg, lambda m: None,
                                           mark_optimizer_called=lambda: None)
    assert status == "PHASE_3_COMPLETE" and calls["n"] == 0


def test_22_contract_threads_injected_map(monkeypatch, cfg):
    rtmap = runner._phase3_runtime_paths()
    monkeypatch.setattr(runner, "_phase3_runtime_paths",
                        lambda: (_ for _ in ()).throw(AssertionError("rebuilt")))
    ctx = runner._phase3_contract(None, cfg, CONFIG_PATH, lambda m: None,
                                  rtmap=rtmap)
    assert ctx["rtmap"] is rtmap
    assert ctx["ev"]["input_authentication"]["frozen_stem_parquet"]["ok"]


# --------------------------------------------------------------------------- #
# package identity (Git-canonical blob equality)
# --------------------------------------------------------------------------- #
def test_23_package_inventory_and_blob_identity(tmp_path):
    rec = runner._verify_package_identity()
    for name in runner.REQUIRED_PACKAGE_MODULES:
        info = rec["imported_modules"][name]
        assert info["ancestry_ok"] and info["blob_equal"]
        assert info["working_blob_id"] == info["blob_id"]
    evil = _NS(__name__="dclaborsupply.likelihood._numpy_primitives",
               __file__=str(tmp_path / "evil" / "_numpy_primitives.py"))
    (tmp_path / "evil").mkdir()
    Path(evil.__file__).write_text("# evil", encoding="utf-8")
    with pytest.raises(runner.StopRun):
        runner._verify_package_identity(_modules=[evil])
    with pytest.raises(runner.StopRun):
        runner._verify_package_identity(_modules=[_NS(__name__="ghost")])


def test_24_untracked_or_modified_source_refused(tmp_path):
    nested = tmp_path / "nested"
    srcdir = nested / "packages/dclaborsupply/src/dclaborsupply"
    srcdir.mkdir(parents=True)
    _git(nested, "init", "-q")
    _git(nested, "config", "user.email", "t@t")
    _git(nested, "config", "user.name", "t")
    tracked = srcdir / "tracked_mod.py"
    tracked.write_text("# tracked v1", encoding="utf-8", newline="\n")
    _git(nested, "add", "-A")
    _git(nested, "commit", "-q", "-m", "pkg")
    root = nested / "packages/dclaborsupply/src"
    mk = lambda p, name: _NS(__name__=name, __file__=str(p))  # noqa: E731
    assert runner._verify_package_identity(
        _modules=[mk(tracked, "dclaborsupply.tracked_mod")],
        _package_root=root, _nested_root=nested)["package_identity_ok"]
    untracked = srcdir / "untracked_mod.py"
    untracked.write_text("# untracked", encoding="utf-8", newline="\n")
    with pytest.raises(runner.StopRun):
        runner._verify_package_identity(
            _modules=[mk(untracked, "dclaborsupply.untracked_mod")],
            _package_root=root, _nested_root=nested)
    untracked.unlink()
    tracked.write_text("# MODIFIED", encoding="utf-8", newline="\n")
    with pytest.raises(runner.StopRun):
        runner._verify_package_identity(
            _modules=[mk(tracked, "dclaborsupply.tracked_mod")],
            _package_root=root, _nested_root=nested)


# --------------------------------------------------------------------------- #
# execution gates (Git identity + review v6) on temporary repositories
# --------------------------------------------------------------------------- #
def _mk_gate_repos(tmp_path, review_text=GOOD_REVIEW):
    repo, nested = tmp_path / "repo", tmp_path / "nested"
    for d in (repo, nested):
        d.mkdir(parents=True)
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t")
        _git(d, "config", "user.name", "t")
    review = repo / runner.CANONICAL_APPROVED_REVIEW_REL
    review.parent.mkdir(parents=True)
    review.write_text(review_text, encoding="utf-8", newline="\n")
    (nested / "a.txt").write_text("x", encoding="utf-8", newline="\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "state")
    _git(nested, "add", "-A")
    _git(nested, "commit", "-q", "-m", "nested")
    return (repo, nested, _git(repo, "rev-parse", "HEAD"),
            _git(nested, "rev-parse", "HEAD"), review)


def _gate_args(mnl, dcl, sha):
    return _args(dry_run=False, execute_phase3=True, expected_mnl_head=mnl,
                 expected_dclaborsupply_head=dcl,
                 approved_review=str(runner.CANONICAL_APPROVED_REVIEW_REL),
                 approved_review_sha256=sha)


def test_25_execution_gates_pass_and_git_variants(tmp_path):
    repo, nested, mnl, dcl, review = _mk_gate_repos(tmp_path)
    sha = hashlib.sha256(review.read_bytes()).hexdigest()
    rec = runner._verify_execution_gates(_gate_args(mnl, dcl, sha),
                                         _repo_root=repo, _nested_root=nested,
                                         _check_gitlink=False)
    assert rec["verified"] and rec["execution_ready"]
    with pytest.raises(runner.StopRun, match="MNL HEAD"):
        runner._verify_execution_gates(_gate_args("0" * 40, dcl, sha),
                                       _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)
    with pytest.raises(runner.StopRun, match="nested HEAD"):
        runner._verify_execution_gates(_gate_args(mnl, "0" * 40, sha),
                                       _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)
    (repo / "untracked.txt").write_text("x", encoding="utf-8")
    with pytest.raises(runner.StopRun, match="fully clean"):
        runner._verify_execution_gates(_gate_args(mnl, dcl, sha),
                                       _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)
    (repo / "untracked.txt").unlink()
    (nested / "stray.bin").write_text("x", encoding="utf-8")
    with pytest.raises(runner.StopRun, match="fully clean"):
        runner._verify_execution_gates(_gate_args(mnl, dcl, sha),
                                       _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)


def test_26_execution_gates_review_variants(tmp_path):
    for i, (text, ok) in enumerate((
            (GOOD_REVIEW, True),
            ("# 1. Sixth-review verdict\n\n**FINAL VERDICT: APPROVE AFTER FIXES**\n",
             False),
            ("# 1. Sixth-review verdict\n\n**FINAL VERDICT: REJECT**\n", False),
            ("# 1. Wrong heading\n\n**FINAL VERDICT: APPROVE**\n", False),
            ("# 1. Sixth-review verdict\n\nprose APPROVE only\n", False),
            ("# 1. Sixth-review verdict\n\n**FINAL VERDICT: APPROVE**\n\n"
             "# 2. X\n\n**FINAL VERDICT: REJECT**\n", False))):
        repo, nested, mnl, dcl, review = _mk_gate_repos(tmp_path / f"v{i}", text)
        sha = hashlib.sha256(review.read_bytes()).hexdigest()
        args = _gate_args(mnl, dcl, sha)
        if ok:
            assert runner._verify_execution_gates(
                args, _repo_root=repo, _nested_root=nested,
                _check_gitlink=False)["verified"]
        else:
            with pytest.raises(runner.StopRun):
                runner._verify_execution_gates(args, _repo_root=repo,
                                               _nested_root=nested,
                                               _check_gitlink=False)
    repo, nested, mnl, dcl, review = _mk_gate_repos(tmp_path / "wrongpath")
    sha = hashlib.sha256(review.read_bytes()).hexdigest()
    bad = _gate_args(mnl, dcl, sha)
    bad.approved_review = \
        "docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v5.md"
    with pytest.raises(runner.StopRun, match="exactly"):
        runner._verify_execution_gates(bad, _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)
    bad = _gate_args(mnl, dcl, "not-a-sha")
    with pytest.raises(runner.StopRun, match="SHA-256"):
        runner._verify_execution_gates(bad, _repo_root=repo, _nested_root=nested,
                                       _check_gitlink=False)


def test_27_real_gitlink_matches_nested_head():
    nested_head = _git(MNL_ROOT / "dclaborsupply-monorepo", "rev-parse", "HEAD")
    assert runner._git_gitlink(MNL_ROOT) == nested_head


def test_28_execute_without_gates_refused(cfg):
    lock = runner.CANONICAL_PHASE3_ROOT / ".phase3.lock"
    assert not lock.exists()
    with pytest.raises(runner.StopRun):
        runner.run_phase3(_args(dry_run=False, execute_phase3=True), cfg)
    assert not lock.exists()                 # refused before any transaction
    rc = runner._phase3_run(_args(dry_run=False), cfg, {})
    assert rc == 2 and not lock.exists()     # private body refuses unverified too


# --------------------------------------------------------------------------- #
# canonical dry-run via subprocess (never optimizing)
# --------------------------------------------------------------------------- #
def test_29_subprocess_dry_run_never_optimizes():
    r = subprocess.run(
        [sys.executable, str(MNL_ROOT / "scripts/p2a/run_p2a_regionlive_rebuild.py"),
         "--config", str(CONFIG_PATH), "--phase", "3",
         "--out", str(runner.CANONICAL_REGIONLIVE_ROOT)],
        capture_output=True, text=True, timeout=300, cwd=str(MNL_ROOT))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    attempts = runner.CANONICAL_PHASE3_ROOT / "attempts"
    d = max((x for x in attempts.iterdir() if x.name.startswith("2026")),
            key=lambda p: p.name)
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "PHASE_3_DRY_RUN_COMPLETE"
    assert man["optimizer_called"] is False
    assert man["execution_ready"] is False
    assert man["review_gate"] == "AWAITING_REVIEW_V6_APPROVE"
    assert not (runner.CANONICAL_PHASE3_ROOT / "complete").exists()


def test_30_gitlink_mismatch_refused(tmp_path):
    repo, nested, mnl, dcl, review = _mk_gate_repos(tmp_path)
    sha = hashlib.sha256(review.read_bytes()).hexdigest()
    _git(repo, "update-index", "--add", "--cacheinfo",
         "160000," + "1" * 40 + ",dclaborsupply-monorepo")
    _git(repo, "commit", "-q", "-m", "wrong gitlink")
    args = _gate_args(_git(repo, "rev-parse", "HEAD"), dcl, sha)
    with pytest.raises(runner.StopRun, match="gitlink"):
        runner._verify_execution_gates(args, _repo_root=repo,
                                       _nested_root=nested, _check_gitlink=True)


# --------------------------------------------------------------------------- #
# collision-resistant attempt allocation (review-v6 required fixes 1-2)
# --------------------------------------------------------------------------- #
class _FrozenDT:
    """Freeze the attempt-id timestamp so a repeated UUID forces an id collision."""

    @staticmethod
    def now(tz=None):
        import datetime as _d
        return _d.datetime(2026, 7, 25, 12, 0, 0, tzinfo=tz)


def _uuid_seq(monkeypatch, hexes):
    """uuid4 stub returning the given hex tokens in order (last one repeats)."""
    calls = {"n": 0}

    def fake_uuid4():
        i = min(calls["n"], len(hexes) - 1)
        calls["n"] += 1
        return _NS(hex=hexes[i])

    monkeypatch.setattr(runner.uuid, "uuid4", fake_uuid4)
    return calls


def test_31_attempt_allocation_collision_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "datetime", _FrozenDT)
    calls = _uuid_seq(monkeypatch, ["a" * 32, "a" * 32, "a" * 32, "b" * 32])
    root = tmp_path / "p3"
    txn1 = runner.Phase3Transaction(root, "estimate")
    txn1.acquire()
    id1 = txn1.attempt_id
    assert "a" * 32 in id1                       # full untruncated uuid4 hex
    (txn1.staging / "evidence.txt").write_text("first", encoding="utf-8")
    txn1.finish("STOPPED")
    txn1.release()
    assert calls["n"] == 1

    txn2 = runner.Phase3Transaction(root, "estimate")   # same label, same status
    txn2.acquire()
    id2 = txn2.attempt_id
    assert calls["n"] == 4                       # 2 detected collisions, then fresh
    assert id2 != id1 and "b" * 32 in id2
    (txn2.staging / "evidence.txt").write_text("second", encoding="utf-8")
    txn2.finish("STOPPED")
    txn2.release()

    dests = sorted(p.name for p in (root / "attempts").iterdir())
    assert dests == sorted([f"{id1}_STOPPED", f"{id2}_STOPPED"])
    assert ((root / "attempts" / f"{id1}_STOPPED" / "evidence.txt")
            .read_text(encoding="utf-8") == "first")     # nothing overwritten
    assert ((root / "attempts" / f"{id2}_STOPPED" / "evidence.txt")
            .read_text(encoding="utf-8") == "second")
    assert list((root / ".staging").iterdir()) == []     # no stranded staging
    assert not (root / ".phase3.lock").exists()          # lock released normally
    # a stranded .staging directory also counts as an occupied destination
    planted = root / ".staging" / "someone_elses_attempt"
    planted.mkdir()
    probe = runner.Phase3Transaction(root, "estimate")
    assert probe._attempt_destination_exists("someone_elses_attempt")
    planted.rmdir()


def test_32_attempt_allocation_retry_exhaustion(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "datetime", _FrozenDT)
    calls = _uuid_seq(monkeypatch, ["f" * 32])           # every candidate collides
    root = tmp_path / "p3"
    txn1 = runner.Phase3Transaction(root, "estimate")
    txn1.acquire()
    id1 = txn1.attempt_id
    (txn1.staging / "evidence.txt").write_text("first", encoding="utf-8")
    txn1.finish("STOPPED")
    txn1.release()

    txn2 = runner.Phase3Transaction(root, "estimate")
    with pytest.raises(runner.StopRun, match="attempt-allocation"):
        txn2.acquire()
    assert calls["n"] == 1 + txn2._ATTEMPT_ALLOC_MAX_TRIES   # finite retry bound
    assert txn2.attempt_id is None and txn2.staging is None
    assert not (root / ".phase3.lock").exists()   # controlled release, not stranded
    assert list((root / ".staging").iterdir()) == []         # no stranded evidence
    assert sorted(p.name for p in (root / "attempts").iterdir()) == [
        f"{id1}_STOPPED"]                                    # nothing published
    assert ((root / "attempts" / f"{id1}_STOPPED" / "evidence.txt")
            .read_text(encoding="utf-8") == "first")         # first attempt intact
    assert not (root / "complete").exists()
    # after the controlled stop the root remains usable by a fresh transaction
    _uuid_seq(monkeypatch, ["e" * 32])
    txn3 = runner.Phase3Transaction(root, "estimate")
    txn3.acquire()
    txn3.finish("STOPPED")
    txn3.release()
    assert not (root / ".phase3.lock").exists()
