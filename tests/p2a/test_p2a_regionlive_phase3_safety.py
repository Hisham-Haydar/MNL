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
    pre = {"some_input": {"path": str(f), "actual": sha, "expected": sha}}
    table, ok = runner._recheck_inputs(pre)
    assert ok and table["some_input"]["ok"]
    f.write_bytes(b"tampered")
    table, ok = runner._recheck_inputs(pre)
    assert not ok and not table["some_input"]["ok"]


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
