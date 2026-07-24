"""Non-production safety tests for the P2a region-live Phase-3 runner.

Review fix 8 / decision K: fake objectives, fake optimizer results and dependency
injection ONLY -- no real optimizer call, no estimation data, no production write.
Every temporary root lives under pytest's tmp_path; the production CLI path (which
enforces the canonical roots) is exercised only for its REFUSAL branches, which
return before any filesystem write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))

import run_p2a_regionlive_rebuild as runner  # noqa: E402

CONFIG_PATH = MNL_ROOT / "scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml"


# --------------------------------------------------------------------------- #
# fixtures / helpers
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def cfg():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def _names47():
    """Synthetic 47-name vector: the 10 accepted pins + the 2 expected-bound names
    + 35 dummies (bound names must exist for the gate tests)."""
    free = list(runner.EXPECTED_AT_BOUND_NAMES) + [f"dummy_{i:02d}" for i in range(35)]
    return list(runner.ACCEPTED_PIN_NAMES) + free


def _pmap():
    names = _names47()
    pin_values = {p: float(k + 1) for k, p in enumerate(runner.ACCEPTED_PIN_NAMES)}
    return runner.build_phase3_parameter_map(names, list(runner.ACCEPTED_PIN_NAMES),
                                             pin_values)


def _bounds_full(pmap):
    bounds = []
    for n in pmap["all_names"]:
        if n in runner.EXPECTED_AT_BOUND_NAMES:
            bounds.append((-1.0, 1.0))
        else:
            bounds.append((-100.0, 100.0))
    return bounds


def _theta_ok(pmap):
    theta = np.zeros(47)
    theta[pmap["pin_idx"]] = pmap["pin_values"]
    for n in runner.EXPECTED_AT_BOUND_NAMES:      # the two expected bound hits
        theta[pmap["name_idx"][n]] = 1.0
    return theta


def _gates_cfg(cfg):
    return cfg["phase3"]["gates"]


def _args(dry_run=True):
    return argparse.Namespace(config=str(CONFIG_PATH), out=None,
                              dry_run=dry_run, phase=3)


def _fake_contract(ev=None):
    def contract(out, cfg_, config_path, log):
        return {"ev": ev or {"ok": True, "fake": True}}
    return contract


class _Raiser:
    def __init__(self):
        self.called = False

    def __call__(self, *a, **k):
        self.called = True
        raise AssertionError("optimizer/estimate must not be called")


# --------------------------------------------------------------------------- #
# 1-4: mapping, round trips, pins
# --------------------------------------------------------------------------- #
def test_1_mapping_counts_and_ordering():
    pmap = _pmap()
    assert len(pmap["all_names"]) == 47
    assert len(pmap["free_names"]) == 37
    assert tuple(pmap["pin_names"]) == runner.ACCEPTED_PIN_NAMES
    assert [pmap["all_names"][i] for i in pmap["free_idx"]] == pmap["free_names"]
    assert [pmap["all_names"][i] for i in pmap["pin_idx"]] == pmap["pin_names"]
    assert set(pmap["free_names"]) & set(pmap["pin_names"]) == set()


def test_2_free_full_free_round_trip():
    pmap = _pmap()
    free = np.arange(37, dtype=np.float64) + 0.5
    full = runner.expand_free_to_full(pmap, free)
    assert np.array_equal(runner.project_full_to_free(pmap, full), free)
    template = np.arange(47, dtype=np.float64) * 1.25
    rebuilt = runner.expand_free_to_full(pmap, runner.project_full_to_free(pmap, template))
    assert np.array_equal(rebuilt[pmap["free_idx"]], template[pmap["free_idx"]])


def test_3_exact_pin_preservation():
    pmap = _pmap()
    full = runner.expand_free_to_full(pmap, np.random.default_rng(0).normal(size=37))
    for k in range(10):
        assert (np.float64(full[pmap["pin_idx"][k]]).tobytes()
                == np.float64(pmap["pin_values"][k]).tobytes())


def test_4_duplicate_or_incorrect_pin_set_refused():
    names = _names47()
    vals = {p: 1.0 for p in runner.ACCEPTED_PIN_NAMES}
    bad_dup = list(runner.ACCEPTED_PIN_NAMES[:9]) + [runner.ACCEPTED_PIN_NAMES[0]]
    with pytest.raises(runner.StopRun):
        runner.build_phase3_parameter_map(names, bad_dup, vals)
    with pytest.raises(runner.StopRun):   # reordered list is a STOP (decision E)
        runner.build_phase3_parameter_map(
            names, list(reversed(runner.ACCEPTED_PIN_NAMES)), vals)
    with pytest.raises(runner.StopRun):   # wrong member
        runner.build_phase3_parameter_map(
            names, list(runner.ACCEPTED_PIN_NAMES[:9]) + ["beta_E"], vals)


# --------------------------------------------------------------------------- #
# 5-7: G-16 and bound-set gates
# --------------------------------------------------------------------------- #
def test_5_g16_pass(cfg):
    pmap = _pmap()
    theta = _theta_ok(pmap)
    gates, rows, status, stop = runner._phase3_post_gates(
        100.0, theta, np.zeros(47), pmap, _bounds_full(pmap), _gates_cfg(cfg),
        100.0, True, "ok")
    assert gates["g16_inbounds_ok"] and status == "PHASE_3_COMPLETE" and stop is None
    assert all(r["in_bounds"] for r in rows)


def test_6_g16_fail(cfg):
    pmap = _pmap()
    theta = _theta_ok(pmap)
    theta[pmap["name_idx"]["dummy_00"]] = 100.0 + 2e-9   # beyond hi + 1e-9
    gates, _rows, status, stop = runner._phase3_post_gates(
        100.0, theta, np.zeros(47), pmap, _bounds_full(pmap), _gates_cfg(cfg),
        100.0, True, "ok")
    assert not gates["g16_inbounds_ok"]
    assert status == "STOPPED" and stop["gate"] == "G-16"


def test_7_expected_bound_set_validation(cfg):
    pmap = _pmap()
    theta = _theta_ok(pmap)
    theta[pmap["name_idx"]["dummy_01"]] = 100.0          # extra (valid) bound hit
    gates, _rows, status, stop = runner._phase3_post_gates(
        100.0, theta, np.zeros(47), pmap, _bounds_full(pmap), _gates_cfg(cfg),
        100.0, True, "ok")
    assert not gates["g15_bound_hits_ok"]
    assert status == "STOPPED" and stop["gate"] == "G-15"
    assert gates["g_nonbound_free_count"] == 35


# --------------------------------------------------------------------------- #
# 8-10: canonical refusals and optimizer contract
# --------------------------------------------------------------------------- #
def test_8_canonical_output_root_refused(tmp_path):
    rc = runner.main(["--config", str(CONFIG_PATH), "--phase", "3",
                      "--out", str(tmp_path), "--dry-run"])
    assert rc == 2
    assert list(tmp_path.iterdir()) == []          # refused before any write


def test_9_wrong_phase3_subdirectory_refused(tmp_path, cfg):
    bad = dict(cfg)
    bad_cfg_path = tmp_path / "bad.yaml"
    text = CONFIG_PATH.read_text(encoding="utf-8").replace(
        "output_subdir: phase3_estimation_v1", "output_subdir: somewhere_else")
    bad_cfg_path.write_text(text, encoding="utf-8")
    lock = runner.CANONICAL_PHASE3_ROOT / ".phase3.lock"
    assert not lock.exists()
    rc = runner.main(["--config", str(bad_cfg_path), "--phase", "3",
                      "--out", str(runner.CANONICAL_REGIONLIVE_ROOT), "--dry-run"])
    assert rc == 2
    assert not lock.exists()                       # refused before the transaction


def test_10_optimizer_contract_mismatch_refused(cfg):
    good = {"phase3": {"optimizer": {"method": "L-BFGS-B",
                                     "options": {"maxiter": 5000, "maxcor": 30,
                                                 "ftol": 1e-15, "gtol": 1e-10}}}}
    assert runner._validate_optimizer_contract(good)["options"]["maxcor"] == 30
    bad_method = json.loads(json.dumps(good))
    bad_method["phase3"]["optimizer"]["method"] = "BFGS"
    with pytest.raises(runner.StopRun):
        runner._validate_optimizer_contract(bad_method)
    bad_keys = json.loads(json.dumps(good))
    bad_keys["phase3"]["optimizer"]["options"]["maxls"] = 60
    with pytest.raises(runner.StopRun):
        runner._validate_optimizer_contract(bad_keys)
    bad_val = json.loads(json.dumps(good))
    bad_val["phase3"]["optimizer"]["options"]["maxcor"] = 10
    with pytest.raises(runner.StopRun):
        runner._validate_optimizer_contract(bad_val)


# --------------------------------------------------------------------------- #
# 11-16: transaction, publication, manifest, console
# --------------------------------------------------------------------------- #
def test_11_dry_run_cannot_call_injected_optimizer(tmp_path, cfg):
    raiser = _Raiser()
    rc = runner.run_phase3(_args(dry_run=True), cfg,
                           _contract_fn=_fake_contract(), _estimate_fn=raiser,
                           _txn_root=tmp_path / "p3")
    assert rc == 0 and not raiser.called
    attempts = list((tmp_path / "p3" / "attempts").iterdir())
    dirs = [d for d in attempts if d.name.endswith("PHASE_3_DRY_RUN_COMPLETE")]
    assert len(dirs) == 1
    man = json.loads((dirs[0] / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "PHASE_3_DRY_RUN_COMPLETE"
    assert man["optimizer_called"] is False


def test_12_successful_bundle_cannot_be_overwritten(tmp_path, cfg):
    root = tmp_path / "p3"
    txn = runner.Phase3Transaction(root, "estimate")
    txn.acquire()
    (txn.staging / "estimation_results.json").write_text("{}", encoding="utf-8")
    dest = txn.finish("PHASE_3_COMPLETE")
    txn.release()
    assert dest == root / "complete" and dest.is_dir()
    marker = hashlib.sha256(
        (dest / "estimation_results.json").read_bytes()).hexdigest()
    txn2 = runner.Phase3Transaction(root, "estimate")
    txn2.acquire()
    (txn2.staging / "estimation_results.json").write_text('{"x": 1}', encoding="utf-8")
    with pytest.raises(RuntimeError):
        txn2.finish("PHASE_3_COMPLETE")
    txn2.release()
    assert hashlib.sha256(
        (dest / "estimation_results.json").read_bytes()).hexdigest() == marker
    # CLI-level B.3: a real run refuses before contract/estimate when complete/ exists
    raiser = _Raiser()
    rc = runner.run_phase3(_args(dry_run=False), cfg,
                           _contract_fn=raiser, _estimate_fn=raiser, _txn_root=root)
    assert rc == 2 and not raiser.called


def test_13_failed_attempt_cannot_mutate_successful_bundle(tmp_path, cfg):
    root = tmp_path / "p3"
    txn = runner.Phase3Transaction(root, "estimate")
    txn.acquire()
    (txn.staging / "estimation_results.json").write_text('{"good": 1}', encoding="utf-8")
    txn.finish("PHASE_3_COMPLETE")
    txn.release()
    before = hashlib.sha256(
        (root / "complete" / "estimation_results.json").read_bytes()).hexdigest()

    def failing_contract(out, cfg_, config_path, log):
        raise runner.StopRun("S-1", "test", "synthetic failure")

    rc = runner.run_phase3(_args(dry_run=True), cfg,
                           _contract_fn=failing_contract, _txn_root=root)
    assert rc == 2
    after = hashlib.sha256(
        (root / "complete" / "estimation_results.json").read_bytes()).hexdigest()
    assert before == after
    stopped = [d for d in (root / "attempts").iterdir() if d.name.endswith("_STOPPED")]
    assert len(stopped) == 1


def test_14_artifact_set_publication(tmp_path):
    root = tmp_path / "p3"
    txn = runner.Phase3Transaction(root, "estimate")
    txn.acquire()
    for name in runner.PHASE3_ARTIFACTS:
        (txn.staging / name).write_text(f"content of {name}", encoding="utf-8")
    (txn.staging / "phase3_manifest.json").write_text("{}", encoding="utf-8")
    dest = txn.finish("PHASE_3_COMPLETE")
    txn.release()
    assert sorted(p.name for p in dest.iterdir()) == sorted(
        list(runner.PHASE3_ARTIFACTS) + ["phase3_manifest.json"])
    assert not txn.staging.exists()                # staging fully moved, not copied


def test_15_manifest_does_not_self_hash(tmp_path, cfg):
    rc = runner.run_phase3(_args(dry_run=True), cfg,
                           _contract_fn=_fake_contract(), _txn_root=tmp_path / "p3")
    assert rc == 0
    d = next(d for d in (tmp_path / "p3" / "attempts").iterdir()
             if d.name.endswith("PHASE_3_DRY_RUN_COMPLETE"))
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert "phase3_manifest.json" not in man["artifact_hashes"]
    console_sha = hashlib.sha256((d / "phase3_console.log").read_bytes()).hexdigest()
    assert man["artifact_hashes"]["phase3_console.log"] == console_sha


def test_16_console_contains_final_status(tmp_path, cfg):
    rc = runner.run_phase3(_args(dry_run=True), cfg,
                           _contract_fn=_fake_contract(), _txn_root=tmp_path / "p3")
    assert rc == 0
    d = next(d for d in (tmp_path / "p3" / "attempts").iterdir()
             if d.name.endswith("PHASE_3_DRY_RUN_COMPLETE"))
    console = (d / "phase3_console.log").read_text(encoding="utf-8")
    assert console.rstrip().endswith("FINAL STATUS: PHASE_3_DRY_RUN_COMPLETE")


# --------------------------------------------------------------------------- #
# 17-18: input recheck and STOPPED evidence
# --------------------------------------------------------------------------- #
def test_17_pre_post_input_hash_change_detected(tmp_path):
    f = tmp_path / "input.bin"
    f.write_bytes(b"original")
    sha = hashlib.sha256(b"original").hexdigest()
    rt = {"some_input": f}
    pre = {"some_input": {"runtime_path": str(f.resolve()), "actual": sha,
                          "expected": sha}}
    table, ok = runner._recheck_inputs(pre, runtime_paths=rt)
    assert ok and table["some_input"]["ok"]
    f.write_bytes(b"tampered")
    table, ok = runner._recheck_inputs(pre, runtime_paths=rt)
    assert not ok and not table["some_input"]["ok"]
    # a label missing from the pre-table can never pass the recheck
    table, ok = runner._recheck_inputs({}, runtime_paths=rt)
    assert not ok


def test_18_stopped_evidence_written_before_exit(tmp_path, cfg):
    def failing_contract(out, cfg_, config_path, log):
        raise runner.StopRun("S-8", "test-gate", "synthetic S-8")

    rc = runner.run_phase3(_args(dry_run=False), cfg,
                           _contract_fn=failing_contract, _txn_root=tmp_path / "p3")
    assert rc == 2
    d = next(d for d in (tmp_path / "p3" / "attempts").iterdir()
             if d.name.endswith("_STOPPED"))
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "STOPPED"
    assert man["stop"] == {"code": "S-8", "gate": "test-gate",
                           "message": "synthetic S-8"}
    console = (d / "phase3_console.log").read_text(encoding="utf-8")
    assert console.rstrip().endswith("FINAL STATUS: STOPPED")
    assert man["optimizer_called"] is False


# --------------------------------------------------------------------------- #
# 19+: remediation-v2 integration tests (review v2 / decisions E-H)
# Real certified 47-name interleaved ordering; fake minimizer through the real
# _phase3_estimate seam; scipy.optimize is never touched.
# --------------------------------------------------------------------------- #
from types import SimpleNamespace

TARGET = 19053.46553160094
OPTS = {"maxiter": 5000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10}


def _real_names():
    from dclaborsupply import EstimationSpec
    spec = EstimationSpec.from_yaml(str(
        MNL_ROOT / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"))
    return list(spec.all_param_names)


def _mk_ctx(tmp_path, monkeypatch, c0=0.0):
    """Real interleaved ordering + jax quadratic objective centered at the start."""
    import jax
    jax.config.update('jax_enable_x64', True)   # float64, as the engine enforces
    import jax.numpy as jnp
    tmp_path.mkdir(parents=True, exist_ok=True)
    names = _real_names()
    pin_vals = {p: float(i + 1) for i, p in enumerate(runner.ACCEPTED_PIN_NAMES)}
    pmap = runner.build_phase3_parameter_map(
        names, list(runner.ACCEPTED_PIN_NAMES), pin_vals)
    bounds_full = [(-1.0, 1.0) if n in runner.EXPECTED_AT_BOUND_NAMES
                   else (-100.0, 100.0) for n in names]
    bounds_free = [bounds_full[i] for i in pmap["free_idx"]]
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
    monkeypatch.setattr(runner, "_phase3_runtime_paths", lambda: rt)
    input_auth = {"authinp": {"runtime_path": str(f.resolve()), "actual": sha,
                              "expected": sha}}
    ev = {"optimizer_contract": {"method": "L-BFGS-B", "options": dict(OPTS)},
          "start_theta_raw_sha256": "x", "start_theta_applied_sha256": "y",
          "negll_start": TARGET + c0, "parameter_map": {"fake": True},
          "at_bound_expected_derived": list(runner.EXPECTED_AT_BOUND_NAMES)}
    return {"spec": None, "names": names, "pmap": pmap, "bounds_full": bounds_full,
            "bounds_free": bounds_free, "theta_trial": start_full.copy(),
            "free_start": free_start, "theta_start_full": start_full,
            "tot": tot, "target": TARGET, "ev": ev, "input_auth": input_auth,
            "_authfile": f}


class FakeMin:
    """Asserting fake minimizer (decision E). Never touches scipy.optimize."""

    def __init__(self, x_out=None, success=True, raise_after=False, mutate=None):
        self.x_out, self.success = x_out, success
        self.raise_after, self.mutate = raise_after, mutate
        self.called = False

    def __call__(self, fun, x0, jac=None, method=None, bounds=None, options=None):
        self.called = True
        assert len(x0) == 37 and len(bounds) == 37 and jac is True
        assert method == "L-BFGS-B" and dict(options) == OPTS
        v0, g0 = fun(np.asarray(x0))
        assert abs(v0 - TARGET) < 10.0 and v0 >= 0        # objective sign: +negLL
        e = np.array(x0, dtype=float)
        k = next(i for i, n in enumerate(self.pmap["free_names"])
                 if n not in runner.EXPECTED_AT_BOUND_NAMES)
        e[k] += 1.0
        v1, g1 = fun(e)
        assert abs((v1 - v0) - 0.5) < 1e-8                # expansion correct
        assert abs(g1[k] - 1.0) < 1e-8 and abs(g0[k]) < 1e-8   # grad sign + order
        if self.mutate is not None:
            self.mutate()
        if self.raise_after:
            raise RuntimeError("fake optimizer exploded after invocation")
        x = np.asarray(self.x_out if self.x_out is not None else x0, dtype=float)
        return SimpleNamespace(x=x, success=self.success,
                               status=0 if self.success else 2, message="fake",
                               nit=3, nfev=4, njev=4)


def _run_est(tmp_path, monkeypatch, cfg, fake, c0=0.0):
    ctx = _mk_ctx(tmp_path, monkeypatch, c0=c0)
    fake.pmap = ctx["pmap"]
    staging = tmp_path / "staging"
    staging.mkdir()
    marks = []
    status, diag = runner._phase3_estimate(
        ctx, staging, cfg, lambda m: None, minimize_fn=fake,
        mark_optimizer_called=lambda: marks.append(True))
    return ctx, staging, marks, status, diag


def test_19_fake_route_success_and_expected_bounds(tmp_path, monkeypatch, cfg):
    fake = FakeMin()
    ctx, staging, marks, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert fake.called and marks == [True]
    assert status == "PHASE_3_COMPLETE"
    assert diag["gates"]["g15_bound_hits_detected"] == sorted(
        runner.EXPECTED_AT_BOUND_NAMES)
    for n in runner.PHASE3_ARTIFACTS:
        if n != "phase3_console.log":
            assert (staging / n).is_file()


def test_20_pins_bitwise_and_interleaved_ordering(tmp_path, monkeypatch, cfg):
    names = _real_names()
    pin_idx = [names.index(p) for p in runner.ACCEPTED_PIN_NAMES]
    assert pin_idx == [10, 11, 12, 13, 14, 15, 16, 17, 31, 32]   # interleaved
    fake = FakeMin()
    ctx, staging, _m, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    theta = np.asarray(diag["final_theta"])
    for k, p in enumerate(runner.ACCEPTED_PIN_NAMES):
        assert (np.float64(theta[ctx["pmap"]["pin_idx"][k]]).tobytes()
                == np.float64(ctx["pmap"]["pin_values"][k]).tobytes())
    assert ctx["pmap"]["free_names"] == [n for n in names
                                         if n not in runner.ACCEPTED_PIN_NAMES]


def test_21_optimizer_success_false(tmp_path, monkeypatch, cfg):
    fake = FakeMin(success=False)
    _c, _s, marks, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert status == "STOPPED" and diag["stop"]["gate"] == "G-2"
    assert marks == [True]


def test_22_optimizer_exception_after_invocation(tmp_path, monkeypatch, cfg):
    fake = FakeMin(raise_after=True)
    _c, staging, marks, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert status == "STOPPED" and diag["stop"]["gate"] == "optimizer-exception"
    assert diag["exception"]["type"] == "RuntimeError"
    assert marks == [True]                       # decision G: marked BEFORE call
    assert not (staging / "estimation_results.json").exists()


def test_23_target_too_high_and_lower_review(tmp_path, monkeypatch, cfg):
    for c0 in (+1e-3, -1e-3):                    # materially above AND below
        fake = FakeMin()
        _c, _s, _m, status, diag = _run_est(tmp_path / f"c{c0 > 0}", monkeypatch,
                                            cfg, fake, c0=c0)
        assert status == "REVIEW_REQUIRED_TARGET_MISMATCH"
        assert diag["gates"]["g1_ok"] is False


def test_24_gradient_gate_failure(tmp_path, monkeypatch, cfg):
    ctx0 = _mk_ctx(tmp_path / "probe", monkeypatch)
    k = next(i for i, n in enumerate(ctx0["pmap"]["free_names"])
             if n not in runner.EXPECTED_AT_BOUND_NAMES)
    x = ctx0["free_start"].copy()
    x[k] += 0.5                                  # grad 0.5 > 1e-2
    fake = FakeMin(x_out=x)
    _c, _s, _m, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert status == "STOPPED" and diag["stop"]["gate"] == "G-3"


def test_25_g16_failure_via_estimate(tmp_path, monkeypatch, cfg):
    ctx0 = _mk_ctx(tmp_path / "probe", monkeypatch)
    k = next(i for i, n in enumerate(ctx0["pmap"]["free_names"])
             if n not in runner.EXPECTED_AT_BOUND_NAMES)
    x = ctx0["free_start"].copy()
    x[k] = 100.0 + 5e-9                          # beyond hi + 1e-9
    fake = FakeMin(x_out=x)
    _c, _s, _m, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert status == "STOPPED" and diag["stop"]["gate"] == "G-16"


def test_26_unexpected_bound_hit_via_estimate(tmp_path, monkeypatch, cfg):
    ctx0 = _mk_ctx(tmp_path / "probe", monkeypatch)
    k = next(i for i, n in enumerate(ctx0["pmap"]["free_names"])
             if n not in runner.EXPECTED_AT_BOUND_NAMES)
    x = ctx0["free_start"].copy()
    x[k] = 100.0                                 # exact bound: in-bounds, unexpected hit
    fake = FakeMin(x_out=x)
    _c, _s, _m, status, diag = _run_est(tmp_path, monkeypatch, cfg, fake)
    assert status == "STOPPED" and diag["stop"]["gate"] == "G-15"


def test_27_input_mutation_during_call_s8(tmp_path, monkeypatch, cfg):
    holder = {}

    def mutate():
        holder["f"].write_bytes(b"TAMPERED DURING OPTIMIZATION")

    fake = FakeMin(mutate=mutate)
    ctx = _mk_ctx(tmp_path, monkeypatch)
    holder["f"] = ctx["_authfile"]
    fake.pmap = ctx["pmap"]
    staging = tmp_path / "staging"
    staging.mkdir()
    status, diag = runner._phase3_estimate(ctx, staging, cfg, lambda m: None,
                                           minimize_fn=fake,
                                           mark_optimizer_called=lambda: None)
    assert status == "STOPPED" and diag["stop"]["code"] == "S-8"
    assert not diag["input_recheck_after_optimization"]["authinp"]["ok"]
    assert list(staging.iterdir()) == []         # nothing written, nothing published


def test_28_no_publication_after_failure_and_called_flag(tmp_path, monkeypatch, cfg):
    ctx = _mk_ctx(tmp_path, monkeypatch)

    def contract(out, cfg_, config_path, log):
        return ctx

    def estimate(c, staging, cfg_, log, minimize_fn=None, mark_optimizer_called=None):
        fake = FakeMin(raise_after=True)
        fake.pmap = c["pmap"]
        return runner._phase3_estimate(c, staging, cfg_, log, minimize_fn=fake,
                                       mark_optimizer_called=mark_optimizer_called)

    rc = runner.run_phase3(_args(dry_run=False), cfg, _contract_fn=contract,
                           _estimate_fn=estimate, _txn_root=tmp_path / "p3",
                           _package_identity_fn=lambda **k: {"test_seam": True})
    assert rc == 2
    root = tmp_path / "p3"
    assert not (root / "complete").exists()
    d = next(d for d in (root / "attempts").iterdir() if d.name.endswith("_STOPPED"))
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["optimizer_called"] is True       # decision G, persisted on raise
    assert man["stop"]["gate"] == "optimizer-exception"


def test_29_bundle_completeness_refusals(tmp_path, cfg):
    def contract(out, cfg_, config_path, log):
        return {"ev": {"ok": True}}

    def est_incomplete(c, staging, cfg_, log, minimize_fn=None,
                       mark_optimizer_called=None):
        (staging / "estimation_results.json").write_text("{}", encoding="utf-8")
        return "PHASE_3_COMPLETE", {"gates": {}}

    rc = runner.run_phase3(_args(dry_run=False), cfg, _contract_fn=contract,
                           _estimate_fn=est_incomplete, _txn_root=tmp_path / "a",
                           _package_identity_fn=lambda **k: {})
    assert rc == 2 and not (tmp_path / "a" / "complete").exists()

    def est_extra(c, staging, cfg_, log, minimize_fn=None,
                  mark_optimizer_called=None):
        for n in ("theta_estimated.csv", "optimizer_diagnostics.json",
                  "estimation_results.json"):
            (staging / n).write_text("x", encoding="utf-8")
        (staging / "unexpected.bin").write_text("x", encoding="utf-8")
        return "PHASE_3_COMPLETE", {"gates": {}}

    rc = runner.run_phase3(_args(dry_run=False), cfg, _contract_fn=contract,
                           _estimate_fn=est_extra, _txn_root=tmp_path / "b",
                           _package_identity_fn=lambda **k: {})
    assert rc == 2 and not (tmp_path / "b" / "complete").exists()

    def est_full(c, staging, cfg_, log, minimize_fn=None,
                 mark_optimizer_called=None):
        for n in ("theta_estimated.csv", "optimizer_diagnostics.json",
                  "estimation_results.json"):
            (staging / n).write_text("x", encoding="utf-8")
        return "PHASE_3_COMPLETE", {"gates": {}}

    rc = runner.run_phase3(_args(dry_run=False), cfg, _contract_fn=contract,
                           _estimate_fn=est_full, _txn_root=tmp_path / "c",
                           _package_identity_fn=lambda **k: {})
    assert rc == 0
    pub = sorted(p.name for p in (tmp_path / "c" / "complete").iterdir())
    assert pub == sorted(list(runner.PHASE3_ARTIFACTS) + ["phase3_manifest.json"])


def test_30_lock_contention_no_migration(tmp_path, cfg):
    root = tmp_path / "p3"
    root.mkdir(parents=True)
    (root / ".phase3.lock").write_text("held", encoding="utf-8")
    legacy = root / "phase3_manifest.json"
    legacy.write_text("legacy", encoding="utf-8")
    raiser = _Raiser()
    rc = runner.run_phase3(_args(dry_run=True), cfg, _contract_fn=raiser,
                           _txn_root=root,
                           _package_identity_fn=lambda **k: {})
    assert rc == 2 and not raiser.called
    assert legacy.read_text(encoding="utf-8") == "legacy"    # NOT migrated (decision H)
    assert not (root / "attempts").exists()


def test_31_real_run_requires_external_authorization(tmp_path, cfg):
    with pytest.raises(runner.StopRun):
        runner._verify_external_authorization(None, CONFIG_PATH)
    with pytest.raises(runner.StopRun):
        runner._verify_external_authorization("relative/path.json", CONFIG_PATH)
    bad = tmp_path / "auth.json"
    bad.write_text(json.dumps({"schema": "wrong", "status": "APPROVED"}),
                   encoding="utf-8")
    with pytest.raises(runner.StopRun):
        runner._verify_external_authorization(str(bad.resolve()), CONFIG_PATH)


def test_32_dry_run_reports_awaiting_authorization(tmp_path, cfg):
    rc = runner.run_phase3(_args(dry_run=True), cfg,
                           _contract_fn=_fake_contract(),
                           _txn_root=tmp_path / "p3",
                           _package_identity_fn=lambda **k: {"test_seam": True})
    assert rc == 0
    d = next(d for d in (tmp_path / "p3" / "attempts").iterdir()
             if d.name.endswith("PHASE_3_DRY_RUN_COMPLETE"))
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    assert man["authorization_status"] == "AWAITING_POST_REVIEW_AUTHORIZATION"
    assert man["execution_ready"] is False
    assert man["optimizer_called"] is False


def test_33_safety_constants_yaml_deviation_stops(cfg):
    assert runner._validate_safety_constants(cfg)
    bad = json.loads(json.dumps({k: cfg[k] for k in
                                 ("targets", "certified_spec", "run_overlay")}))
    bad["phase3"] = json.loads(json.dumps(cfg["phase3"]))
    bad["targets"]["negll_full"] = 19053.5
    with pytest.raises(runner.StopRun):
        runner._validate_safety_constants(bad)


def test_34_authentication_label_set_and_path_identity(tmp_path, cfg):
    f = tmp_path / "geom.parquet"
    f.write_bytes(b"data")
    sha = hashlib.sha256(b"data").hexdigest()
    rt = {"geometry_parquet": f}
    good = {"phase3": {"input_authentication": {
        "geometry_parquet": {
            "path": str(f.relative_to(f.anchor)), "sha256": sha}}}}
    # configured path resolves elsewhere -> path_identity failure
    wrong = {"phase3": {"input_authentication": {
        "geometry_parquet": {"path": "somewhere/else.parquet", "sha256": sha}}}}
    with pytest.raises(runner.StopRun):
        runner._authenticate_inputs(wrong, runtime_paths=rt)
    # missing / extra labels refused
    with pytest.raises(runner.StopRun):
        runner._authenticate_inputs({"phase3": {"input_authentication": {}}},
                                    runtime_paths=rt)
    with pytest.raises(runner.StopRun):
        runner._authenticate_inputs(
            {"phase3": {"input_authentication": {
                "geometry_parquet": {"path": "x", "sha256": sha},
                "extra_label": {"path": "y", "sha256": sha}}}},
            runtime_paths=rt)

