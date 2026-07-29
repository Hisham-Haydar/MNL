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
    rc = runner.main(["--config", str(CONFIG_PATH), "--phase", "4",
                      "--out", str(tmp_path / "p4out")])
    assert rc == 2                                   # phase 4: canonical out only
    rc = runner.main(["--config", str(copied), "--phase", "4",
                      "--out", str(runner.CANONICAL_REGIONLIVE_ROOT)])
    assert rc == 2                                   # phase 4: canonical config only
    rc = runner.main(["--config", str(CONFIG_PATH), "--phase", "5"])
    assert rc == 2                                   # phases > 4 refused


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
    # the ACCEPTED immutable complete/ bundle exists since the real Phase-3 run;
    # the dry-run must leave it byte-identical (recomputed deterministic hash)
    comp = runner.CANONICAL_PHASE3_ROOT / "complete"
    hashes = {n: hashlib.sha256((comp / n).read_bytes()).hexdigest()
              for n in runner.PHASE3_ARTIFACTS}
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    assert (hashlib.sha256(joined.encode("utf-8")).hexdigest()
            == runner.PHASE3_ACCEPTED_BUNDLE_SHA256)


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

# --------------------------------------------------------------------------- #
# Phase 4: curvature, rank and regional identification (no Hessian evaluation
# of the real objective anywhere in this battery)
# --------------------------------------------------------------------------- #
def _mk_fake_p3_bundle(d, gates_ok=True, status="PHASE_3_COMPLETE"):
    d.mkdir(parents=True, exist_ok=True)
    arts = {"phase3_console.log": "log\nFINAL STATUS: PHASE_3_COMPLETE\n",
            "theta_estimated.csv": "param,value\n",
            "optimizer_diagnostics.json": "{}",
            "estimation_results.json": "{}"}
    for n, c in arts.items():
        (d / n).write_text(c, encoding="utf-8")
    hashes = {n: hashlib.sha256((d / n).read_bytes()).hexdigest() for n in arts}
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    bundle = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    man = {"status": status, "optimizer_called": True,
           "artifact_hashes": hashes, "bundle_sha256": bundle,
           "gates": {k: bool(gates_ok) for k in
                     ("g1_ok", "g3_ok", "g15_bound_hits_ok", "g16_inbounds_ok",
                      "g2_optimizer_success", "g_pins_bitwise_unchanged")}}
    (d / "phase3_manifest.json").write_text(json.dumps(man), encoding="utf-8")
    return bundle


def test_33_phase3_bundle_hash_binding(tmp_path):
    d = tmp_path / "complete"
    bundle = _mk_fake_p3_bundle(d)
    rec = runner._phase4_verify_phase3_bundle(d, bundle)
    assert rec["bundle_sha256"] == bundle
    with pytest.raises(runner.StopRun, match="phase3-bundle"):
        runner._phase4_verify_phase3_bundle(d, "0" * 64)   # accepted-sha mismatch
    (d / "estimation_results.json").write_text('{"x":1}', encoding="utf-8")
    with pytest.raises(runner.StopRun, match="phase3-bundle"):
        runner._phase4_verify_phase3_bundle(d, bundle)     # tampered artifact
    d2 = tmp_path / "c2"
    b2 = _mk_fake_p3_bundle(d2)
    (d2 / "theta_estimated.csv").unlink()
    with pytest.raises(runner.StopRun, match="phase3-bundle"):
        runner._phase4_verify_phase3_bundle(d2, b2)        # missing artifact
    d3 = tmp_path / "c3"
    b3 = _mk_fake_p3_bundle(d3, status="REVIEW_REQUIRED_TARGET_MISMATCH")
    with pytest.raises(runner.StopRun, match="phase3-bundle"):
        runner._phase4_verify_phase3_bundle(d3, b3)        # not an accepted result
    d4 = tmp_path / "c4"
    b4 = _mk_fake_p3_bundle(d4, gates_ok=False)
    with pytest.raises(runner.StopRun, match="phase3-bundle"):
        runner._phase4_verify_phase3_bundle(d4, b4)        # recorded gates failing


def test_34_regional_name_binding():
    fillers = [f"free_{i:02d}" for i in range(27)]
    free = fillers[:15] + list(runner.PHASE4_REGIONAL_PARAMS) + fillers[15:]
    got = runner._phase4_regional_names(free, list(runner.PHASE4_REGIONAL_PARAMS))
    assert tuple(got) == runner.PHASE4_REGIONAL_PARAMS
    with pytest.raises(runner.StopRun, match="regional-names"):
        runner._phase4_regional_names(
            free, list(reversed(runner.PHASE4_REGIONAL_PARAMS)))  # config conflict
    with pytest.raises(runner.StopRun, match="regional-names"):
        runner._phase4_regional_names(free + ["beta_E_extra"],
                                      list(runner.PHASE4_REGIONAL_PARAMS))
    with pytest.raises(runner.StopRun, match="regional-names"):
        runner._phase4_regional_names(
            [n for n in free if n != "beta_E_drgn5"],
            list(runner.PHASE4_REGIONAL_PARAMS))              # spec missing one


def test_35_symmetry_gate():
    rng = np.random.default_rng(7)
    A = rng.normal(size=(6, 6))
    H = A + A.T                                  # exactly symmetric
    rec, Hs = runner._phase4_symmetry(H, 1e-8)
    assert rec["ok"] and np.array_equal(Hs, Hs.T)
    bad = H.copy()
    bad[0, 1] += 1e-4 * np.max(np.abs(H))        # asymmetry above threshold
    rec2, _ = runner._phase4_symmetry(bad, 1e-8)
    assert not rec2["ok"] and rec2["max_abs_asymmetry"] > rec2["threshold"]
    ok3, _ = runner._phase4_symmetry(H + 1e-12 * np.triu(np.ones((6, 6)), 1),
                                     1e-8)       # tiny asymmetry within tol
    assert ok3["ok"]


def test_36_rank_tolerance_and_full_rank():
    c = runner.PHASE4_SAFETY_CONSTANTS
    good = np.diag(np.linspace(1.0, 2.0, 37))
    e = runner._phase4_eigen(good, 37, c)
    assert e["rank"] == 37 and e["rank_ok"] and e["pd_ok"] and e["n_nonpos"] == 0
    assert e["rank_tolerance"] == pytest.approx(1e-10 * 2.0)
    deficient = np.diag([1e-15] + list(np.linspace(1.0, 2.0, 36)))
    e2 = runner._phase4_eigen(deficient, 37, c)
    assert e2["rank"] == 36 and not e2["rank_ok"]     # below eps_rank = 1e-10*max
    neg = np.diag([-1e-3] + list(np.linspace(1.0, 2.0, 36)))
    e3 = runner._phase4_eigen(neg, 37, c)
    assert (not e3["pd_ok"]) and e3["n_nonpos"] == 1
    assert e3["condition_number"] == float("inf")
    assert e3["condition_tier"] == "failure" and not e3["condition_ok"]


def test_37_condition_tiers():
    c = runner.PHASE4_SAFETY_CONSTANTS
    def mk(hi):
        return np.diag([1.0] + [hi] * 36)
    assert runner._phase4_eigen(mk(1e6), 37, c)["condition_tier"] == "clean"
    w = runner._phase4_eigen(mk(1e8), 37, c)
    assert w["condition_tier"] == "warning" and w["condition_ok"]
    f = runner._phase4_eigen(mk(1e11), 37, c)
    assert f["condition_tier"] == "failure" and not f["condition_ok"]


def test_38_regional_design_rank():
    rng = np.random.default_rng(11)
    M = rng.normal(size=(200, 10))
    d = runner._phase4_design_rank(M, 1e-10)
    assert d["rank"] == 10 and d["rank_ok"] and d["shape"] == [200, 10]
    M2 = M.copy()
    M2[:, 3] = M2[:, 7]                          # exact collinearity
    d2 = runner._phase4_design_rank(M2, 1e-10)
    assert d2["rank"] == 9 and not d2["rank_ok"]
    assert any({p["i"], p["j"]} == {3, 7} for p in d2["high_corr_pairs"])


def _pd_matrix(n, seed=3):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n))
    return A @ A.T + n * np.eye(n)


def test_39_schur_complement_calculation():
    c = runner.PHASE4_SAFETY_CONSTANTS
    H = _pd_matrix(12)
    reg = [4, 9, 11]
    s = runner._phase4_schur(H, reg, c)
    oth = [i for i in range(12) if i not in reg]
    S_manual = (H[np.ix_(reg, reg)]
                - H[np.ix_(reg, oth)] @ np.linalg.inv(H[np.ix_(oth, oth)])
                @ H[np.ix_(oth, reg)])
    assert np.allclose(s["_S"], 0.5 * (S_manual + S_manual.T),
                       rtol=1e-10, atol=1e-10)
    assert s["raw_subblock_pd_ok"] and s["schur_rank"] == 3
    assert s["schur_rank_ok"] and s["schur_min_eig_ok"]
    assert s["solve_vs_pinv_max_abs_diff"] < 1e-8


def test_40_schur_rank_and_min_eig_gates():
    c = runner.PHASE4_SAFETY_CONSTANTS
    # deterministic negative Schur direction: coupling 1.1 between one nuisance
    # and one regional coordinate drives S[r,r] to exactly 1 - 1.21 = -0.21
    H = np.eye(12)
    H[0, 4] = H[4, 0] = 1.1
    s = runner._phase4_schur(H, [4, 9, 11], c)
    assert s["raw_subblock_pd_ok"] is True          # raw block is the identity
    assert s["schur_min_eig"] == pytest.approx(1.0 - 1.1 ** 2)
    assert s["schur_rank"] == 2 and s["schur_rank_ok"] is False
    assert s["schur_min_eig_ok"] is False
    # deterministic raw-subblock PD failure (review-v1 fix: DIRECT assertions,
    # no disjunction that can pass while raw_subblock_pd_ok is true)
    H2 = np.diag(np.linspace(1.0, 2.0, 12))
    H2[9, 9] = -0.5                                 # regional coordinate
    s2 = runner._phase4_schur(H2, [4, 9, 11], c)
    assert s2["raw_subblock_pd_ok"] is False
    assert s2["raw_subblock_min_eig"] <= 0.0
    # loading shares: regional-dominated smallest eigenvector triggers warning
    eig, vec = np.linalg.eigh(H2)
    ls = runner._phase4_loading_shares(eig, vec, [4, 9, 11], 0.5)
    assert ls["three_smallest"][0]["regional_loading_share"] > 0.5
    assert ls["any_warning"] and "never gates" in ls["note"]


def test_41_phase4_transaction_and_overwrite_refusal(tmp_path, cfg):
    import time as _time
    root = tmp_path / "p4"
    txn = runner.Phase3Transaction(root, "curvature",
                                   success_status="PHASE_4_COMPLETE")
    txn.acquire()
    man = runner._phase4_manifest_skeleton(_args(dry_run=False), cfg, txn, {})
    assert man["phase"] == 4 and man["optimizer_called"] is False
    assert man["hessian_evaluated"] is False
    assert man["execution_ready"] is False
    # incomplete artifact set: success downgraded, complete/ never created
    (txn.staging / "phase4_diagnostics.json").write_text("{}", encoding="utf-8")
    rc = runner._phase4_finalize(txn, man, ["l"], _time.time(),
                                 "PHASE_4_COMPLETE", None, 0)
    assert rc == 2 and not (root / "complete").exists()
    d = next(x for x in (root / "attempts").iterdir())
    m = json.loads((d / "phase4_manifest.json").read_text(encoding="utf-8"))
    assert m["status"] == "STOPPED"
    assert m["stop"]["gate"] == "bundle-completeness"
    assert "phase4_manifest.json" not in m["artifact_hashes"]     # no self-hash
    # complete artifact set publishes the exact eight-file bundle
    txn2 = runner.Phase3Transaction(root, "curvature",
                                   success_status="PHASE_4_COMPLETE")
    txn2.acquire()
    for n in runner.PHASE4_ARTIFACTS:
        if n != "phase4_console.log":
            (txn2.staging / n).write_text("x", encoding="utf-8")
    man2 = runner._phase4_manifest_skeleton(_args(dry_run=False), cfg, txn2, {})
    rc = runner._phase4_finalize(txn2, man2, ["go"], _time.time(),
                                 "PHASE_4_COMPLETE", None, 0)
    assert rc == 0
    pub = sorted(p.name for p in (root / "complete").iterdir())
    assert pub == sorted(list(runner.PHASE4_ARTIFACTS) + ["phase4_manifest.json"])
    # a further success can never overwrite the published complete/ result
    txn3 = runner.Phase3Transaction(root, "curvature",
                                   success_status="PHASE_4_COMPLETE")
    txn3.acquire()
    for n in runner.PHASE4_ARTIFACTS:
        if n != "phase4_console.log":
            (txn3.staging / n).write_text("y", encoding="utf-8")
    man3 = runner._phase4_manifest_skeleton(_args(dry_run=False), cfg, txn3, {})
    rc = runner._phase4_finalize(txn3, man3, ["again"], _time.time(),
                                 "PHASE_4_COMPLETE", None, 0)
    assert rc == 2                              # downgraded, publish refused
    assert (root / "complete" / "phase4_diagnostics.json"
            ).read_text(encoding="utf-8") == "x"
    assert not (root / ".phase3.lock").exists()


def test_42_phase4_subprocess_dry_run_never_evaluates_hessian():
    r = subprocess.run(
        [sys.executable, str(MNL_ROOT / "scripts/p2a/run_p2a_regionlive_rebuild.py"),
         "--config", str(CONFIG_PATH), "--phase", "4",
         "--out", str(runner.CANONICAL_REGIONLIVE_ROOT)],
        capture_output=True, text=True, timeout=600, cwd=str(MNL_ROOT))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    attempts = runner.CANONICAL_PHASE4_ROOT / "attempts"
    d = max((x for x in attempts.iterdir() if x.name.startswith("2026")),
            key=lambda p: p.name)
    man = json.loads((d / "phase4_manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "PHASE_4_DRY_RUN_COMPLETE"
    assert man["gradient_evaluated"] is False
    assert man["hessian_evaluated"] is False
    assert man["optimizer_called"] is False
    assert man["execution_ready"] is False
    assert man["review_gate"] == "AWAITING_PHASE4_REVIEW_V6_APPROVE"
    assert man["contract_phase4"]["derivative_route"]["loaded"] is True
    assert man["contract_phase4"]["derivative_route"]["evaluated"] is False
    assert (man["accepted_phase3_bundle_sha256"]
            == runner.PHASE3_ACCEPTED_BUNDLE_SHA256)
    assert not (runner.CANONICAL_PHASE4_ROOT / "complete").exists()
    assert not (runner.CANONICAL_PHASE4_ROOT / ".phase3.lock").exists()


def test_43_phase5_refused(cfg):
    for ph in (5, 6, 7, 8):
        rc = runner.main(["--config", str(CONFIG_PATH), "--phase", str(ph)])
        assert rc == 2


def test_44_phase4_execute_without_gates_refused(cfg):
    lock = runner.CANONICAL_PHASE4_ROOT / ".phase3.lock"
    assert not lock.exists()
    with pytest.raises(runner.StopRun):
        runner.run_phase4(_args(dry_run=False, execute_phase4=True), cfg)
    assert not lock.exists()                 # refused before any transaction
    rc = runner._phase4_run(_args(dry_run=False), cfg, {})
    assert rc == 2 and not lock.exists()     # private body refuses unverified too
    # YAML phase4 block must equal the immutable constants exactly
    assert all(runner._validate_phase4_constants(cfg).values())
    bad = _deep(cfg)
    bad["phase4"]["gates"]["condition_warn_max"] = 1.0e9
    with pytest.raises(runner.StopRun, match="phase4-constants"):
        runner._validate_phase4_constants(bad)
    bad2 = _deep(cfg)
    bad2["phase4"]["regional_parameters"][0] = "beta_E_wrong"
    with pytest.raises(runner.StopRun, match="phase4-constants"):
        runner._validate_phase4_constants(bad2)


# --------------------------------------------------------------------------- #
# Phase-4-specific approval gate (review-v1 required fixes 1-2)
# --------------------------------------------------------------------------- #
GOOD_P4_REVIEW = ("# 1. Phase-4 review verdict\n\n**FINAL VERDICT: APPROVE**"
                  "\n\n# 2. Scope\n\ndetails\n")


def _mk_p4_gate_repos(tmp_path, p4_text=GOOD_P4_REVIEW):
    repo, nested, _mnl, dcl, _v6 = _mk_gate_repos(tmp_path)   # v6 file committed
    p4 = repo / runner.CANONICAL_APPROVED_PHASE4_REVIEW_REL
    p4.write_text(p4_text, encoding="utf-8", newline="\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "phase4 review")
    return repo, nested, _git(repo, "rev-parse", "HEAD"), dcl, p4


def _p4_gate_args(mnl, dcl, sha, review=None):
    return _args(dry_run=False, execute_phase4=True, expected_mnl_head=mnl,
                 expected_dclaborsupply_head=dcl,
                 approved_phase4_review=(
                     review if review is not None
                     else str(runner.CANONICAL_APPROVED_PHASE4_REVIEW_REL)),
                 approved_phase4_review_sha256=sha)


def test_45_phase4_gate_pass_path_hash_git_variants(tmp_path):
    repo, nested, mnl, dcl, p4 = _mk_p4_gate_repos(tmp_path)
    sha = hashlib.sha256(p4.read_bytes()).hexdigest()
    rec = runner._verify_phase4_execution_gates(
        _p4_gate_args(mnl, dcl, sha), _repo_root=repo, _nested_root=nested,
        _check_gitlink=False)
    assert rec["verified"] and rec["execution_ready"] and rec["phase"] == 4
    assert rec["approved_phase4_review"] ==         runner.CANONICAL_APPROVED_PHASE4_REVIEW_REL.as_posix()
    # the Phase-3 review-v6 document is explicitly rejected
    with pytest.raises(runner.StopRun, match="cannot authorize"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, sha,
                          review=str(runner.CANONICAL_APPROVED_REVIEW_REL)),
            _repo_root=repo, _nested_root=nested, _check_gitlink=False)
    # any other path (e.g. a phase4 review v1) is rejected
    with pytest.raises(runner.StopRun, match="must be exactly"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, sha, review=(
                "docs/France_case/P2a/"
                "FR_P2a_region_live_phase4_code_review_v1.md")),
            _repo_root=repo, _nested_root=nested, _check_gitlink=False)
    # wrong review hash / malformed hash
    with pytest.raises(runner.StopRun, match="SHA-256"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, "f" * 64), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    with pytest.raises(runner.StopRun, match="64-hex"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, "nothex"), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    # MNL / nested commit mismatches
    with pytest.raises(runner.StopRun, match="MNL HEAD"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args("0" * 40, dcl, sha), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    with pytest.raises(runner.StopRun, match="nested HEAD"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, "0" * 40, sha), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    # dirty MNL worktree (untracked), then dirty nested worktree
    dirt = repo / "untracked.txt"
    dirt.write_text("x", encoding="utf-8")
    with pytest.raises(runner.StopRun, match="not fully clean"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, sha), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    dirt.unlink()
    dirt2 = nested / "untracked.txt"
    dirt2.write_text("x", encoding="utf-8")
    with pytest.raises(runner.StopRun, match="not fully clean"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, sha), _repo_root=repo,
            _nested_root=nested, _check_gitlink=False)
    dirt2.unlink()


def test_46_phase4_review_verdict_and_gitlink_variants(tmp_path):
    variants = {
        "after_fixes": GOOD_P4_REVIEW.replace(
            "**FINAL VERDICT: APPROVE**",
            "**FINAL VERDICT: APPROVE AFTER FIXES**"),
        "reject": GOOD_P4_REVIEW.replace("**FINAL VERDICT: APPROVE**",
                                         "**FINAL VERDICT: REJECT**"),
        "wrong_heading": GOOD_P4_REVIEW.replace(
            "# 1. Phase-4 review verdict", "# 1. Sixth-review verdict"),
        "multi_verdict": GOOD_P4_REVIEW + "\n**FINAL VERDICT: APPROVE**\n",
    }
    for name, text in variants.items():
        repo, nested, mnl, dcl, p4 = _mk_p4_gate_repos(tmp_path / name, text)
        sha = hashlib.sha256(p4.read_bytes()).hexdigest()
        with pytest.raises(runner.StopRun) as e:
            runner._verify_phase4_execution_gates(
                _p4_gate_args(mnl, dcl, sha), _repo_root=repo,
                _nested_root=nested, _check_gitlink=False)
        assert e.value.gate == "phase4-review-gate", name
    # committed wrong gitlink is refused when the gitlink check is live
    repo, nested, mnl, dcl, p4 = _mk_p4_gate_repos(tmp_path / "gitlink")
    sha = hashlib.sha256(p4.read_bytes()).hexdigest()
    _git(repo, "update-index", "--add", "--cacheinfo",
         "160000," + "1" * 40 + ",dclaborsupply-monorepo")
    _git(repo, "commit", "-q", "-m", "wrong gitlink")
    args = _p4_gate_args(_git(repo, "rev-parse", "HEAD"), dcl, sha)
    with pytest.raises(runner.StopRun, match="gitlink"):
        runner._verify_phase4_execution_gates(args, _repo_root=repo,
                                              _nested_root=nested,
                                              _check_gitlink=True)


# --------------------------------------------------------------------------- #
# fake-derivative Phase-4 orchestration (review-v1 fixes 2-3; NO real Hessian)
# --------------------------------------------------------------------------- #
def _mk_p4_ctx(H, design_M=None):
    import pandas as pd
    pmap = _pmap()
    reg_pos = list(range(15, 25))               # production regional positions
    if design_M is None:
        design_M = np.random.default_rng(23).normal(size=(60, 10))
    return {
        "pmap": pmap,
        "ev4": {"theta_hat_sha256": "0" * 64},
        "negll_hat": 0.0,
        "grad_fn": lambda x: np.zeros(37),
        "free_hat": np.zeros(37),
        "pub_grad_free": np.zeros(37),
        "reg_pos_free": reg_pos,
        "reg_names": [pmap["free_names"][i] for i in reg_pos],
        "design": pd.DataFrame(np.asarray(design_M, dtype="float64")),
        "hess_fn": lambda x: np.asarray(H, dtype="float64"),
    }


def _p4_base_H():
    return np.diag(np.linspace(1.0, 2.0, 37))


def _run_p4_diag(H, design_M=None):
    return runner._phase4_diagnose(_mk_p4_ctx(H, design_M), lambda m: None)


def test_47_raw_subblock_pd_failure_orchestration(tmp_path, cfg):
    import time as _time
    H = _p4_base_H()
    H[17, 17] = -0.5                            # regional free position 15..24
    ctx = _mk_p4_ctx(H)
    status, stop, diag, arrays = runner._phase4_diagnose(ctx, lambda m: None)
    assert status == "STOPPED"
    assert stop.code == "S-5" and stop.gate == "G-9"      # registered R-2 stop
    assert diag["regional"]["raw_subblock_pd_ok"] is False
    assert diag["regional"]["raw_subblock_min_eig"] <= 0.0
    assert diag["gates"]["r2_raw_subblock_pd_ok"] is False
    assert diag["hessian_evaluated"] is True    # the fake path reached the gate
    # the STOPPED result publishes to attempts/ and never creates complete/
    root = tmp_path / "p4"
    txn = runner.Phase3Transaction(root, "curvature",
                                   success_status="PHASE_4_COMPLETE")
    txn.acquire()
    man = runner._phase4_manifest_skeleton(_args(dry_run=False), cfg, txn, {})
    runner._phase4_write_artifacts(txn.staging, ctx, diag, arrays)
    rc = runner._phase4_finalize(txn, man, ["x"], _time.time(), "STOPPED",
                                 stop, 2)
    assert rc == 2 and not (root / "complete").exists()
    assert any(x.name.endswith("_STOPPED") for x in (root / "attempts").iterdir())


def test_48_fake_derivative_orchestration_matrix():
    # 1. raw-Hessian symmetry failure -> S-4
    H = _p4_base_H()
    H[0, 1] = 1e-3
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-4" and stop.gate == "curvature"
    assert diag["gates"]["g6_symmetry_ok"] is False
    # 2. full-Hessian non-PD (nuisance direction) -> S-4
    H = _p4_base_H()
    H[0, 0] = -1.0
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-4"
    assert diag["gates"]["g5_pd_ok"] is False
    # 3. rank < 37 (positive eigenvalue below eps_rank) -> S-4
    H = _p4_base_H()
    H[0, 0] = 1e-15
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-4"
    assert diag["gates"]["g5_pd_ok"] is True
    assert diag["gates"]["g7_rank"] == 36 and diag["gates"]["g7_rank_ok"] is False
    # 4. condition > 1e10 -> S-4 with tier failure
    H = _p4_base_H()
    H[0, 0] = 2e-11
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-4"
    assert diag["gates"]["g8_condition_tier"] == "failure"
    # 5. regional design-rank failure -> S-5/G-9
    M = np.random.default_rng(23).normal(size=(60, 10))
    M[:, 2] = M[:, 6]
    status, stop, diag, _a = _run_p4_diag(_p4_base_H(), M)
    assert status == "STOPPED" and stop.code == "S-5" and stop.gate == "G-9"
    assert diag["gates"]["r1_design_rank_ok"] is False
    # 6. raw regional-subblock PD failure -> S-5/G-9 (see also test 47)
    H = _p4_base_H()
    H[20, 20] = -2.0
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-5"
    assert diag["gates"]["r2_raw_subblock_pd_ok"] is False
    # 7. exactly singular nuisance block H_NN -> registered schur-solve stop
    H = _p4_base_H()
    H[0, 0] = H[1, 1] = 1.0
    H[0, 1] = H[1, 0] = 1.0                     # [[1,1],[1,1]] nuisance block
    with pytest.raises(runner.StopRun) as e:
        _run_p4_diag(H)
    assert e.value.code == "S-5" and e.value.gate == "schur-solve"
    # 8./9. Schur rank < 10 and Schur min eigenvalue <= 0 -> S-5/G-9
    H = np.eye(37)
    H[0, 15] = H[15, 0] = 1.1                   # S[reg0,reg0] = -0.21 exactly
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "STOPPED" and stop.code == "S-5" and stop.gate == "G-9"
    assert diag["gates"]["r2_raw_subblock_pd_ok"] is True
    assert diag["gates"]["r4_schur_rank_ok"] is False
    assert diag["gates"]["r4_schur_min_eig_ok"] is False
    # 10. warning-only regional loading share on a clean success
    H = _p4_base_H()
    H[17, 17] = 0.5                             # smallest eig on a regional coord
    status, stop, diag, _a = _run_p4_diag(H)
    assert status == "PHASE_4_COMPLETE" and stop is None
    assert diag["gates"]["r3_loading_share_warning"] is True
    assert any("loading share" in w for w in diag["warnings"])
    # 11. clean successful fake-Hessian route
    status, stop, diag, _a = _run_p4_diag(_p4_base_H())
    assert status == "PHASE_4_COMPLETE" and stop is None
    assert diag["warnings"] == []
    g = diag["gates"]
    assert (g["g5_pd_ok"] and g["g6_symmetry_ok"] and g["g7_rank_ok"]
            and g["g8_condition_tier"] == "clean"
            and g["region_urbanisation_identification"])


def test_49_exact_gate_boundaries():
    c = runner.PHASE4_SAFETY_CONSTANTS
    # symmetry: exactly at 1e-8 * max_abs_H passes; immediately above fails
    H = np.eye(2)
    H[0, 1] = 1e-8                              # max_abs_H = 1.0 -> thr = 1e-8
    rec, _ = runner._phase4_symmetry(H, 1e-8)
    assert rec["max_abs_asymmetry"] == rec["threshold"] and rec["ok"] is True
    H[0, 1] = np.nextafter(1e-8, 1.0)
    rec, _ = runner._phase4_symmetry(H, 1e-8)
    assert rec["ok"] is False
    # rank: eigenvalue exactly at 1e-10 * max is NOT counted; just above is
    e = runner._phase4_eigen(np.diag([1e-10, 1.0]), 2, c)
    assert e["rank"] == 1 and e["rank_ok"] is False
    e = runner._phase4_eigen(np.diag([np.nextafter(1e-10, 1.0), 1.0]), 2, c)
    assert e["rank"] == 2 and e["rank_ok"] is True
    # condition tiers at the exact edges
    assert runner._phase4_eigen(np.diag([1.0, 1e7]), 2,
                                c)["condition_tier"] == "clean"
    assert runner._phase4_eigen(np.diag([1.0, np.nextafter(1e7, np.inf)]), 2,
                                c)["condition_tier"] == "warning"
    assert runner._phase4_eigen(np.diag([1.0, 1e10]), 2,
                                c)["condition_tier"] == "warning"
    assert runner._phase4_eigen(np.diag([1.0, np.nextafter(1e10, np.inf)]), 2,
                                c)["condition_tier"] == "failure"
    # positive definiteness: > 0 passes; exactly 0 and negative fail
    assert runner._phase4_eigen(np.diag([1e-12, 1.0]), 2, c)["pd_ok"] is True
    assert runner._phase4_eigen(np.diag([0.0, 1.0]), 2, c)["pd_ok"] is False
    assert runner._phase4_eigen(np.diag([-1e-12, 1.0]), 2, c)["pd_ok"] is False


# --------------------------------------------------------------------------- #
# review-v2/v3 remediation: exceptional-path finalization + review binding
# --------------------------------------------------------------------------- #
def _p4_stopped_run(tmp_path, cfg, ctx):
    """Drive the production diagnostics-and-finalize body with a fake ctx."""
    import time as _time
    root = tmp_path / "p4"
    txn = runner.Phase3Transaction(root, "curvature",
                                   success_status="PHASE_4_COMPLETE")
    txn.acquire()
    man = runner._phase4_manifest_skeleton(_args(dry_run=False), cfg, txn, {})
    progress = {"gradient_evaluated": False, "hessian_evaluated": False,
                "partial_diagnostics": None, "artifacts_staged": False,
                "diagnostics_artifact_name": None}
    rc = runner._phase4_run_diagnostics(txn, man, ["l"], _time.time(), ctx,
                                        lambda m: None, progress)
    d = next(x for x in (root / "attempts").iterdir())
    m = json.loads((d / "phase4_manifest.json").read_text(encoding="utf-8"))
    return rc, root, d, m


def test_50_gradient_consistency_stopped_finalization(tmp_path, cfg):
    ctx = _mk_p4_ctx(_p4_base_H())
    ctx["grad_fn"] = lambda x: np.ones(37)      # published projection is zeros
    rc, root, d, m = _p4_stopped_run(tmp_path, cfg, ctx)
    assert rc == 2 and d.name.endswith("_STOPPED")
    assert m["status"] == "STOPPED"
    assert m["gradient_evaluated"] is True      # review-v2 fix 1: true/false
    assert m["hessian_evaluated"] is False
    assert m["stop"]["code"] == "S-8" and m["stop"]["gate"] == "phase4-gradient"
    assert m["exception"]["type"] == "StopRun"
    pdg = m["partial_diagnostics"]              # partial gradient preserved
    assert len(pdg["gradient_free"]) == 37
    assert pdg["gradient_consistency_max_abs_dev"] == 1.0
    assert "gates" not in pdg and "eigen" not in pdg   # Hessian never reached
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()


def test_51_singular_schur_stopped_finalization(tmp_path, cfg):
    H = _p4_base_H()
    H[0, 0] = H[1, 1] = 1.0
    H[0, 1] = H[1, 0] = 1.0                     # exactly singular nuisance block
    rc, root, d, m = _p4_stopped_run(tmp_path, cfg, _mk_p4_ctx(H))
    assert rc == 2 and d.name.endswith("_STOPPED")
    assert m["status"] == "STOPPED"
    assert m["gradient_evaluated"] is True      # review-v2 fix 1: true/true
    assert m["hessian_evaluated"] is True
    assert m["stop"]["code"] == "S-5" and m["stop"]["gate"] == "schur-solve"
    assert m["exception"]["type"] == "StopRun"
    pdg = m["partial_diagnostics"]              # pre-solve diagnostics preserved
    assert pdg["hessian_evaluated"] is True
    assert pdg["symmetry"]["ok"] is True
    assert len(pdg["eigen"]["eigenvalues"]) == 37
    assert pdg["design"]["rank"] == 10
    assert "regional" not in pdg                # no pinv substitute for the solve
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()


def test_52_review_v6_binding_and_stale_strings(tmp_path):
    assert (runner.CANONICAL_APPROVED_PHASE4_REVIEW_REL.name
            == "FR_P2a_region_live_phase4_code_review_v6.md")
    repo, nested, mnl, dcl, p4 = _mk_p4_gate_repos(tmp_path)
    sha = hashlib.sha256(p4.read_bytes()).hexdigest()
    # exact synthetic phase4 review-v6 APPROVE contract passes structurally
    rec = runner._verify_phase4_execution_gates(
        _p4_gate_args(mnl, dcl, sha), _repo_root=repo, _nested_root=nested,
        _check_gitlink=False)
    assert rec["approved_phase4_review"].endswith(
        "phase4_code_review_v6.md") and rec["execution_ready"]
    # Phase-4 review v1-v5 paths are all rejected
    for bad in ("docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v1.md",
                "docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v2.md",
                "docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v3.md",
                "docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v4.md",
                "docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v5.md"):
        with pytest.raises(runner.StopRun, match="must be exactly"):
            runner._verify_phase4_execution_gates(
                _p4_gate_args(mnl, dcl, sha, review=bad), _repo_root=repo,
                _nested_root=nested, _check_gitlink=False)
    # Phase-3 review-v6 is rejected with the dedicated message
    with pytest.raises(runner.StopRun, match="cannot authorize"):
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl, dcl, sha,
                          review=str(runner.CANONICAL_APPROVED_REVIEW_REL)),
            _repo_root=repo, _nested_root=nested, _check_gitlink=False)
    # the REAL review-v5 body (APPROVE AFTER FIXES) placed at the v6 path fails
    real_v5 = (MNL_ROOT / "docs/France_case/P2a/"
               "FR_P2a_region_live_phase4_code_review_v5.md").read_text(
        encoding="utf-8")
    repo2, nested2, mnl2, dcl2, p42 = _mk_p4_gate_repos(tmp_path / "v5body",
                                                        real_v5)
    sha2 = hashlib.sha256(p42.read_bytes()).hexdigest()
    with pytest.raises(runner.StopRun) as e:
        runner._verify_phase4_execution_gates(
            _p4_gate_args(mnl2, dcl2, sha2), _repo_root=repo2,
            _nested_root=nested2, _check_gitlink=False)
    assert e.value.gate == "phase4-review-gate"
    # stale-string sweep: generic --dry-run help covers Phase 4; no live
    # Phase-4 text claims Phase-3 review-v6 authorization
    src = (MNL_ROOT / "scripts/p2a/run_p2a_regionlive_rebuild.py").read_text(
        encoding="utf-8")
    seg = src[src.index('"--dry-run"'):src.index('"--execute-phase3"')]
    assert "phase 4" in seg and "Hessian" in seg
    p4_src = src[src.index("def _verify_phase4_execution_gates"):
                 src.index("def _verify_package_identity")]
    p4_src += src[src.index("def _validate_phase4_constants"):
                  src.index("def main(")]
    # every PHASE-3 review-v6 mention in Phase-4 code must be a rejection
    # statement (the Phase-4 approval doc is itself named review v6 now, so
    # only "Phase-3 review-v6" claims are in scope for this sweep)
    for line in p4_src.splitlines():
        low = line.lower()
        if "phase-3 review-v6" in low:
            assert ("reject" in low or "never" in low
                    or "cannot authorize" in low), line
    assert "the same s5/s7 Git + review-v6 gates as Phase 3" not in src
    assert "review-v6 gates (scope doc s5/s7).\" " not in p4_src


# --------------------------------------------------------------------------- #
# review-v3 remediation: failed-authentication diagnostic preservation
# --------------------------------------------------------------------------- #
def test_53_runtime_map_fingerprint_failure_finalization(tmp_path, cfg):
    ctx = _mk_p4_ctx(_p4_base_H())                # clean fake diagnostics
    ctx["rtmap"] = {"lbl": tmp_path / "input.bin"}
    ctx["rtmap_fingerprint"] = "0" * 64           # forced post-eval mismatch
    ctx["input_auth"] = {}
    rc, root, d, m = _p4_stopped_run(tmp_path, cfg, ctx)
    assert rc == 2 and d.name.endswith("_STOPPED")
    assert m["status"] == "STOPPED"
    assert m["stop"]["code"] == "S-8" and m["stop"]["gate"] == "runtime-map"
    assert m["gradient_evaluated"] is True        # review-v3 fix: true/true
    assert m["hessian_evaluated"] is True
    assert m["exception"]["type"] == "StopRun"
    # the FULL live diagnostic record is retained and explicitly labelled
    assert m["diagnostic_evidence_status"] == "FAILED_AUTHENTICATION_ATTEMPT"
    pdg = m["partial_diagnostics"]
    for key in ("gradient_free", "gradient_consistency_max_abs_dev",
                "symmetry", "eigen", "loading_shares", "design",
                "regional", "gates"):                # review-v4 fix 4
        assert key in pdg, key
    assert len(pdg["gradient_free"]) == 37
    assert pdg["symmetry"]["ok"] is True
    assert len(pdg["eigen"]["eigenvalues"]) == 37
    assert pdg["loading_shares"]["three_smallest"]
    assert pdg["design"]["rank"] == 10
    assert pdg["regional"]["schur_rank"] == 10    # Schur evidence retained
    assert pdg["gates"]["region_urbanisation_identification"] is True
    assert m["gates4"]["g5_pd_ok"] is True        # summary presence is NOT
    assert "partial_diagnostics" in m             # ...taken as persistence
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()


def test_54_input_recheck_failure_finalization(tmp_path, cfg):
    f = tmp_path / "input.bin"
    f.write_text("original", encoding="utf-8")
    orig_sha = hashlib.sha256(f.read_bytes()).hexdigest()
    rtmap = {"lbl": f}
    ctx = _mk_p4_ctx(_p4_base_H())
    ctx["rtmap"] = rtmap
    ctx["rtmap_fingerprint"] = runner._runtime_map_fingerprint(rtmap)
    ctx["input_auth"] = {"lbl": {"runtime_path": str(f.resolve()),
                                 "actual": orig_sha, "expected": orig_sha}}
    f.write_text("tampered", encoding="utf-8")    # authenticated input changed
    rc, root, d, m = _p4_stopped_run(tmp_path, cfg, ctx)
    assert rc == 2 and d.name.endswith("_STOPPED")
    assert m["status"] == "STOPPED"
    assert m["stop"]["code"] == "S-8" and m["stop"]["gate"] == "input-recheck"
    assert m["gradient_evaluated"] is True        # review-v3 fix: true/true
    assert m["hessian_evaluated"] is True
    assert m["diagnostic_evidence_status"] == "FAILED_AUTHENTICATION_ATTEMPT"
    rec = m["input_recheck_after_evaluation"]["lbl"]   # pre/post hash evidence
    assert rec["pre"] == orig_sha and rec["accepted"] == orig_sha
    assert rec["post"] is not None and rec["post"] != orig_sha
    assert rec["ok"] is False
    pdg = m["partial_diagnostics"]                # all pre-recheck diagnostics
    for key in ("gradient_free", "gradient_consistency_max_abs_dev",
                "symmetry", "eigen", "loading_shares", "design",
                "regional", "gates"):                # review-v4 fix 4
        assert key in pdg, key
    assert len(pdg["gradient_free"]) == 37
    assert len(pdg["eigen"]["eigenvalues"]) == 37
    assert pdg["design"]["rank"] == 10
    assert pdg["regional"]["schur_min_eig_ok"] is True
    table = m["input_recheck_after_evaluation"]
    assert all(v["pre"] and v["accepted"] and v["post"] is not None
               for v in table.values())              # complete evidence
    assert any(v["ok"] is False for v in table.values())
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()


# --------------------------------------------------------------------------- #
# review-v4 remediation: post-staging exceptional-evidence consistency
# --------------------------------------------------------------------------- #
def test_55_post_staging_exception_finalization(tmp_path, cfg, monkeypatch):
    real_fin = runner._phase4_finalize
    calls = {"n": 0}

    def flaky_finalize(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:                     # first call AFTER staging
            raise RuntimeError("forced post-staging failure")
        return real_fin(*a, **k)

    monkeypatch.setattr(runner, "_phase4_finalize", flaky_finalize)
    ctx = _mk_p4_ctx(_p4_base_H())              # clean fake diagnostics
    rc, root, d, m = _p4_stopped_run(tmp_path, cfg, ctx)
    assert rc == 3 and d.name.endswith("_STOPPED")
    assert calls["n"] == 2                      # forced raise, then real final
    assert m["status"] == "STOPPED"
    assert m["gradient_evaluated"] is True and m["hessian_evaluated"] is True
    assert m["exception"]["type"] == "RuntimeError"
    assert m["exception"]["message"] == "forced post-staging failure"
    assert m["stop"]["code"] == "S-0" and m["stop"]["gate"] == "unexpected"
    # the staged artifact is the SOLE authoritative record: no duplicate,
    # no "partial" label
    assert "partial_diagnostics" not in m
    assert (m["diagnostic_evidence_status"]
            == "FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT")
    assert m["diagnostic_artifact_authority"] == "phase4_diagnostics.json"
    assert m["diagnostic_artifact_staged"] is True
    full = json.loads((d / "phase4_diagnostics.json").read_text(
        encoding="utf-8"))
    for key in ("gradient_free", "symmetry", "eigen", "loading_shares",
                "design", "regional", "gates"):
        assert key in full, key                 # full scientific record staged
    assert len(full["eigen"]["eigenvalues"]) == 37
    assert sorted(p.name for p in d.iterdir()) == sorted(
        list(runner.PHASE4_ARTIFACTS) + ["phase4_manifest.json"])
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()


# --------------------------------------------------------------------------- #
# review-v5 closure: the OUTER _phase4_run() post-staging exception fallback
# --------------------------------------------------------------------------- #
def test_56_outer_phase4_run_post_staging_fallback(tmp_path, cfg, monkeypatch):
    """Drives _phase4_run() itself (not _phase4_run_diagnostics) on a temporary
    root: the diagnostic-call boundary stages the FULL fake artifact set via the
    production writer, updates the genuine shared progress state, then raises a
    RuntimeError that escapes to the outer unexpected-exception handler. Both
    handlers must route through the single production merge policy."""
    root = tmp_path / "p4root"
    monkeypatch.setattr(runner, "CANONICAL_PHASE4_ROOT", root)
    monkeypatch.setattr(runner, "_verify_package_identity",
                        lambda expected_commit=None: {"stub": True})
    ctx = _mk_p4_ctx(_p4_base_H())              # clean fake diagnostics
    ctx["ev"] = {"stub_contract": True}
    monkeypatch.setattr(runner, "_phase4_contract",
                        lambda out, c, p, log, rtmap=None: ctx)
    merges = []
    real_merge = runner._merge_phase4_exception_evidence

    def spy_merge(man, prog, exc):              # same policy, observed
        merges.append(type(exc).__name__)
        return real_merge(man, prog, exc)

    monkeypatch.setattr(runner, "_merge_phase4_exception_evidence", spy_merge)

    def fake_diag_boundary(txn, manifest, lines, t0, c, log, progress):
        status, stop, diag, arrays = runner._phase4_diagnose(
            c, log, progress=progress)          # genuine progress object
        assert status == "PHASE_4_COMPLETE"
        runner._phase4_write_artifacts(txn.staging, c, diag, arrays)
        progress["artifacts_staged"] = True
        progress["diagnostics_artifact_name"] = "phase4_diagnostics.json"
        raise RuntimeError("forced outer post-staging failure")

    monkeypatch.setattr(runner, "_phase4_run_diagnostics", fake_diag_boundary)
    rc = runner._phase4_run(_args(dry_run=False), cfg,
                            {"verified": True, "execution_ready": True})
    assert rc == 3                              # controlled unexpected failure
    d = next(x for x in (root / "attempts").iterdir())
    assert d.name.endswith("_STOPPED")
    m = json.loads((d / "phase4_manifest.json").read_text(encoding="utf-8"))
    assert m["mode"] == "phase4 curvature diagnostics"   # reached _phase4_run
    assert m["status"] == "STOPPED"
    assert m["stop"]["code"] == "S-0" and m["stop"]["gate"] == "unexpected"
    assert m["exception"]["type"] == "RuntimeError"
    assert m["exception"]["message"] == "forced outer post-staging failure"
    assert m["gradient_evaluated"] is True and m["hessian_evaluated"] is True
    assert m["diagnostic_artifact_staged"] is True
    assert m["diagnostic_artifact_authority"] == "phase4_diagnostics.json"
    assert (m["diagnostic_evidence_status"]
            == "FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT")
    assert "partial_diagnostics" not in m
    assert merges == ["RuntimeError"]           # ONE shared merge policy fired
    full = json.loads((d / "phase4_diagnostics.json").read_text(
        encoding="utf-8"))
    for key in ("gradient_free", "symmetry", "eigen", "loading_shares",
                "design", "regional", "gates"):
        assert key in full, key                 # complete fake record retained
    assert len(full["eigen"]["eigenvalues"]) == 37
    assert sorted(p.name for p in d.iterdir()) == sorted(
        list(runner.PHASE4_ARTIFACTS) + ["phase4_manifest.json"])
    assert not (root / "complete").exists()
    assert list((root / ".staging").iterdir()) == []
    assert not (root / ".phase3.lock").exists()
