"""Increment-C tests for the Phase-5 dry-run-only runner and transaction.

Subject under review: ``scripts/p2a/run_p2a_phase5_inference.py``.

Reviewer-runnable proof rule (charter s5). Nothing under review is replaced:

  * the reducer is the committed Increment-A ``run_score_stream``;
  * the covariance/Wald/table builders and serializers are the committed
    Increment-B objects;
  * the runner, transaction, T-12S comparison and T-23S gate are the module's own;
  * the T-12S reproduction runs in a REAL subprocess (a fresh interpreter).

Only the household subset size and the output root are patched. Every test that
writes does so under pytest's ``tmp_path`` -- never the production
``outputs/.../phase5_inference_v1`` tree.

Test families
-------------
  L  config, digest binding, and the absence of a real-run path
  M  accepted-artifact and revision binding
  N  dry-run authorization refusals
  O  aggregate-only transaction: allowlist, atomicity, never complete/
  P  bounded-subset runner integration (real end-to-end run)
  Q  T-12S fresh-process reproduction in a real subprocess
  R  T-23S no-row-level persistence: static and behavioural
  S  STOPPED truthfulness

Families P and Q are slow (each streams real scores and Q spawns an
interpreter). Select with ``-m production``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))

import p2a_phase5_inference as ib            # noqa: E402
import run_p2a_phase5_inference as rc        # noqa: E402

RUNNER_PATH = MNL_ROOT / "scripts" / "p2a" / "run_p2a_phase5_inference.py"
CONFIG_PATH = MNL_ROOT / rc.CONFIG_REL

SUBSET = 12          # bounded subset for the integration runs


def _canonical_root_listing():
    """Sorted relative-path listing of the canonical Phase-5 output root.

    Captures ``None`` when the root does not exist. Used for before/after
    equality checks that a refused or bounded-tmp-path run left the
    canonical root untouched -- the root itself may legitimately exist
    (the accepted Phase-5 result), so tests must not assert its absence.
    """
    root = MNL_ROOT / rc.CANONICAL_OUTPUT_ROOT
    if not root.exists():
        return None
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


# Captured at import time, before any fixture or test in this module runs.
_CANONICAL_ROOT_LISTING_AT_COLLECTION = _canonical_root_listing()


@pytest.fixture(scope="module")
def cfg():
    conf, digest = rc.load_config(MNL_ROOT)
    return conf, digest


# =========================================================================== #
# L. config, digest binding, no real-run path
# =========================================================================== #
def test_L1_config_is_digest_bound(cfg):
    conf, digest = cfg
    assert digest == rc.CONFIG_SHA256 == hashlib.sha256(
        CONFIG_PATH.read_bytes()).hexdigest()
    assert conf["run"]["mode"] == "dry-run-only"
    assert conf["run"]["real_run_supported"] is False


def test_L2_a_tampered_config_is_refused(tmp_path):
    """FAILURE DEMONSTRATION: one changed byte breaks the digest binding."""
    fake = tmp_path / "fake"
    (fake / Path(rc.CONFIG_REL).parent).mkdir(parents=True)
    text = CONFIG_PATH.read_text(encoding="utf-8").replace(
        "batch_size: 128", "batch_size: 129", 1)
    (fake / rc.CONFIG_REL).write_text(text, encoding="utf-8")
    with pytest.raises(rc.StopRun, match="HP-CONFIG"):
        rc.load_config(fake)


def test_L3_no_real_run_pathway_exists():
    """STATIC: the runner has no execute-real / production-run code path."""
    src = RUNNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = {n.name for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    forbidden = {"execute_real_run", "run_production", "execute_production",
                 "promote_complete", "publish_complete"}
    assert names & forbidden == set()
    # the only execution entry is the dry run
    assert "execute_dry_run" in names
    # CLI exposes no real-run flag
    parser = rc.build_parser()
    opts = {a.option_strings[0] for a in parser._actions if a.option_strings}
    # note: "--no-reproduction" legitimately contains the substring "production",
    # so the check is against whole option names, not substrings
    assert opts & {"--execute-real", "--real-run", "--production",
                   "--execute-production", "--promote"} == set()
    assert "--execute-dry-run" in opts


def test_L4_transaction_has_no_complete_surface(tmp_path):
    """STATIC + STRUCTURAL: `complete/` cannot be constructed by the transaction."""
    txn = rc.Phase5Transaction(tmp_path / "root")
    assert not hasattr(txn, "complete")
    assert not hasattr(txn, "complete_exists")
    assert not hasattr(txn, "success_status")
    src = RUNNER_PATH.read_text(encoding="utf-8")
    # no write-side construction of a path whose final component is "complete"
    assert 'self.complete' not in src
    assert '/ "complete"' not in src
    assert "'complete'" not in src


def test_L5_status_constants_publish_only_to_attempts():
    assert rc.STATUS_COMPLETE == "PHASE_5_DRY_RUN_COMPLETE"
    assert rc.STATUS_STOPPED == "STOPPED"
    src = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    finish = [n for n in ast.walk(src)
              if isinstance(n, ast.FunctionDef) and n.name == "finish"][0]
    targets = [a.attr for a in ast.walk(finish) if isinstance(a, ast.Attribute)]
    assert "attempts" in targets and "complete" not in targets


def test_L6_allowlist_is_the_closed_union(cfg):
    assert set(rc.ALLOWED_ARTIFACTS) == (
        set(ib.AGGREGATE_ARTIFACTS) | set(rc.RUNNER_OWNED_ARTIFACTS))
    assert len(rc.ALLOWED_ARTIFACTS) == len(set(rc.ALLOWED_ARTIFACTS))
    assert rc.MANIFEST_MEMBER in rc.ALLOWED_ARTIFACTS


# =========================================================================== #
# M. accepted-artifact and revision binding
# =========================================================================== #
def test_M1_binding_verifies_before_any_computation(cfg):
    conf, digest = cfg
    rec = rc.verify_accepted_binding(conf, digest, MNL_ROOT)
    assert rec["verified"] is True
    assert rec["phase3_bundle_sha256"] == conf["accepted"]["phase3_bundle_sha256"]
    assert rec["phase4_bundle_sha256"] == conf["accepted"]["phase4_bundle_sha256"]
    assert rec["bread_sha256"] == ib.BREAD_SHA256
    assert rec["theta_bytes_sha256"] == ib.ACCEPTED_THETA_SHA256
    assert rec["gitlink"] == rec["dclaborsupply_head"]
    assert rec["config_sha256"] == rc.CONFIG_SHA256


@pytest.mark.parametrize("field,halt", [
    ("phase3_bundle_sha256", "HP-MUT"),
    ("phase4_bundle_sha256", "HP-MUT"),
    ("bread_sha256", "HP-BREAD"),
    ("theta_bytes_sha256", "HP-MUT"),
    ("spec_sha256", "HP-MUT"),
])
def test_M2_binding_refuses_a_changed_anchor(cfg, field, halt):
    """FAILURE DEMONSTRATION: each accepted anchor is genuinely load-bearing."""
    conf, digest = cfg
    tampered = json.loads(json.dumps(conf))
    tampered["accepted"][field] = "0" * 64
    with pytest.raises(rc.StopRun, match=halt):
        rc.verify_accepted_binding(tampered, digest, MNL_ROOT)


def test_M3_binding_refuses_a_wrong_expected_nested_head(cfg):
    conf, digest = cfg
    tampered = json.loads(json.dumps(conf))
    tampered["revisions"]["expected_dclaborsupply_head"] = "0" * 40
    with pytest.raises(rc.StopRun, match="HP-REV"):
        rc.verify_accepted_binding(tampered, digest, MNL_ROOT)


def test_M4_binding_refuses_a_gitlink_that_diverges_from_nested_head(
        cfg, monkeypatch):
    """Review C fix F5: the gitlink arm of `verify_accepted_binding`.

    Proved load-bearing in review §3 item 7 but never asserted by the packet.
    `_git_gitlink` is moved away from nested HEAD; the binding must refuse
    BEFORE any computation."""
    conf, digest = cfg
    monkeypatch.setattr(rc, "_git_gitlink", lambda repo: "9" * 40)
    with pytest.raises(rc.StopRun, match="HP-REV") as err:
        rc.verify_accepted_binding(conf, digest, MNL_ROOT)
    assert "gitlink" in err.value.reason
    # unpatched, the same call succeeds -- so the arm, not the fixture, refused
    monkeypatch.undo()
    assert rc.verify_accepted_binding(conf, digest, MNL_ROOT)["verified"] is True


# =========================================================================== #
# N. dry-run authorization
# =========================================================================== #
class _Args:
    def __init__(self, **kw):
        self.execute_dry_run = kw.get("execute_dry_run", False)
        self.expected_mnl_head = kw.get("expected_mnl_head")
        self.expected_dclaborsupply_head = kw.get("expected_dclaborsupply_head")
        self.approved_review = kw.get("approved_review")
        self.approved_review_sha256 = kw.get("approved_review_sha256")


def test_N1_full_population_requires_the_execute_flag(cfg):
    conf, _ = cfg
    with pytest.raises(rc.StopRun, match="requires --execute-dry-run"):
        rc.verify_dry_run_authorization(_Args(), conf, MNL_ROOT)


@pytest.mark.parametrize("kw,pattern", [
    ({"execute_dry_run": True}, "expected-mnl-head"),
    ({"execute_dry_run": True, "expected_mnl_head": "a" * 40},
     "expected-dclaborsupply-head"),
    ({"execute_dry_run": True, "expected_mnl_head": "a" * 40,
      "expected_dclaborsupply_head": "b" * 40}, "approved-review-sha256"),
    ({"execute_dry_run": True, "expected_mnl_head": "a" * 40,
      "expected_dclaborsupply_head": "b" * 40,
      "approved_review_sha256": "c" * 64}, "approved-review must be exactly"),
])
def test_N2_authorization_arguments_are_each_required(cfg, kw, pattern):
    conf, _ = cfg
    with pytest.raises(rc.StopRun, match=pattern):
        rc.verify_dry_run_authorization(_Args(**kw), conf, MNL_ROOT)


def test_N3_authorization_refuses_when_the_approval_is_absent(tmp_path,
                                                              monkeypatch, cfg):
    """The addendum s8 mechanism: with every other arm satisfied, the run is
    refused because the approval document is absent.

    Review C v2 fix F6 — LIFECYCLE-AWARE. The shipped form asserted
    `not (MNL_ROOT / CANONICAL_APPROVED_REVIEW_REL).exists()`, encoding a
    transient property of the pre-approval worktree as a standing invariant, so
    it failed permanently the moment a real approval was created at the
    canonical path. The arm is now isolated against a FIXTURE repository root
    that contains no approval, exactly as `test_N4` isolates the verdict arm.

    This test makes NO assertion about the real canonical path, and is therefore
    green whether or not an approval document exists there.
    """
    conf, _ = cfg
    fake = tmp_path / "repo"
    (fake / rc.CANONICAL_APPROVED_REVIEW_REL.parent).mkdir(parents=True)
    assert not (fake / rc.CANONICAL_APPROVED_REVIEW_REL).exists()

    monkeypatch.setattr(rc, "_git_fully_clean", lambda repo: True)
    monkeypatch.setattr(rc, "_git_head", lambda repo: "a" * 40)
    monkeypatch.setattr(rc, "_git_gitlink", lambda repo: "a" * 40)
    args = _Args(execute_dry_run=True, expected_mnl_head="a" * 40,
                 expected_dclaborsupply_head="a" * 40,
                 approved_review=rc.CANONICAL_APPROVED_REVIEW_REL.as_posix(),
                 approved_review_sha256="d" * 64)
    with pytest.raises(rc.StopRun, match="approved Increment-C review missing"):
        rc.verify_dry_run_authorization(args, conf, fake)


def test_N3a_the_arm_is_green_in_both_lifecycle_states(tmp_path, monkeypatch, cfg):
    """Review C v2 fix F6: the review-file arm behaves correctly in BOTH states.

    Absent  -> refused at the review-file arm.
    Present -> that arm is passed, and the refusal (if any) comes from a LATER
               arm, never from the file's existence.

    Both branches run against fixture roots, so this test asserts nothing about
    the real canonical path either."""
    conf, _ = cfg
    monkeypatch.setattr(rc, "_git_fully_clean", lambda repo: True)
    monkeypatch.setattr(rc, "_git_head", lambda repo: "a" * 40)
    monkeypatch.setattr(rc, "_git_gitlink", lambda repo: "a" * 40)

    def authorize(root, sha):
        args = _Args(execute_dry_run=True, expected_mnl_head="a" * 40,
                     expected_dclaborsupply_head="a" * 40,
                     approved_review=rc.CANONICAL_APPROVED_REVIEW_REL.as_posix(),
                     approved_review_sha256=sha)
        return rc.verify_dry_run_authorization(args, conf, root)

    # (a) approval ABSENT
    absent = tmp_path / "absent"
    (absent / rc.CANONICAL_APPROVED_REVIEW_REL.parent).mkdir(parents=True)
    with pytest.raises(rc.StopRun, match="approved Increment-C review missing"):
        authorize(absent, "d" * 64)

    # (b) approval PRESENT and well-formed -> authorization SUCCEEDS
    present = tmp_path / "present"
    (present / rc.CANONICAL_APPROVED_REVIEW_REL.parent).mkdir(parents=True)
    approval = present / rc.CANONICAL_APPROVED_REVIEW_REL
    approval.write_text(
        "# Review C v3\n\nBody.\n\n**FINAL VERDICT: APPROVE**\n", encoding="utf-8")
    good = authorize(present, hashlib.sha256(approval.read_bytes()).hexdigest())
    assert good["verified"] is True and good["execution_ready"] is True
    assert good["approved_review"] == rc.CANONICAL_APPROVED_REVIEW_REL.as_posix()

    # (c) present but with the WRONG digest -> refused at the digest arm,
    #     proving the earlier existence arm was passed, not skipped
    with pytest.raises(rc.StopRun, match="approved review SHA-256"):
        authorize(present, "f" * 64)


def test_N3b_authorization_refuses_a_wrong_expected_mnl_head(monkeypatch, cfg):
    """Review C fix F5: the MNL-HEAD arm of `verify_dry_run_authorization`.

    A WELL-FORMED but wrong 40-hex head must be refused -- the format check and
    the identity check are separate arms, and only the format one was covered.
    Git cleanliness is stubbed True so the refusal demonstrated is the
    head-identity arm specifically."""
    conf, _ = cfg
    monkeypatch.setattr(rc, "_git_fully_clean", lambda repo: True)
    real_head = rc._git_head(MNL_ROOT)
    wrong_head = ("0" * 40) if real_head != "0" * 40 else "1" * 40
    assert rc._HEX40.match(wrong_head) and wrong_head != real_head
    args = _Args(execute_dry_run=True, expected_mnl_head=wrong_head,
                 expected_dclaborsupply_head=rc._git_head(
                     MNL_ROOT / "dclaborsupply-monorepo"),
                 approved_review=rc.CANONICAL_APPROVED_REVIEW_REL.as_posix(),
                 approved_review_sha256="e" * 64)
    with pytest.raises(rc.StopRun, match="MNL HEAD") as err:
        rc.verify_dry_run_authorization(args, conf, MNL_ROOT)
    assert wrong_head in err.value.reason and real_head in err.value.reason


@pytest.mark.parametrize("superseded_index", range(2))
def test_N3c_a_superseded_review_can_never_authorize(tmp_path, monkeypatch, cfg,
                                                     superseded_index):
    """Binding advance (R-29 / R-48 precedent, third application).

    Review v1 is immutable APPROVE-AFTER-FIXES evidence and review v2 is
    immutable REJECT evidence; neither may ever authorize the run. Since
    `--approved-review` must equal the canonical path EXACTLY, each superseded
    path is refused by binding -- with its CORRECT digest and every other arm
    satisfied, so the refusal is the path arm and nothing else.

    Run against a fixture root carrying the superseded document, so the test is
    lifecycle-robust in the F6 sense: it asserts nothing about which review
    documents happen to exist in the real repository."""
    conf, _ = cfg
    superseded = rc.SUPERSEDED_REVIEW_RELS[superseded_index]
    assert superseded != rc.CANONICAL_APPROVED_REVIEW_REL

    fake = tmp_path / "repo"
    (fake / superseded.parent).mkdir(parents=True)
    doc = fake / superseded
    doc.write_text("# superseded review\n\n**FINAL VERDICT: APPROVE**\n",
                   encoding="utf-8")

    monkeypatch.setattr(rc, "_git_fully_clean", lambda repo: True)
    monkeypatch.setattr(rc, "_git_head", lambda repo: "a" * 40)
    monkeypatch.setattr(rc, "_git_gitlink", lambda repo: "a" * 40)
    args = _Args(execute_dry_run=True, expected_mnl_head="a" * 40,
                 expected_dclaborsupply_head="a" * 40,
                 approved_review=superseded.as_posix(),
                 approved_review_sha256=hashlib.sha256(
                     doc.read_bytes()).hexdigest())
    # even carrying a well-formed APPROVE line and its own correct digest
    with pytest.raises(rc.StopRun, match="approved-review must be exactly"):
        rc.verify_dry_run_authorization(args, conf, fake)


def test_N3d_the_superseded_list_names_v1_and_v2():
    """Legibility: the superseded set is explicit, ordered, and disjoint from
    the canonical binding."""
    names = [p.name for p in rc.SUPERSEDED_REVIEW_RELS]
    assert names == ["FR_P2a_streaming_incrementC_review_v1.md",
                     "FR_P2a_streaming_incrementC_review_v2.md"]
    assert rc.CANONICAL_APPROVED_REVIEW_REL.name == (
        "FR_P2a_streaming_incrementC_review_v3.md")
    assert rc.CANONICAL_APPROVED_REVIEW_REL not in rc.SUPERSEDED_REVIEW_RELS


def test_N4_a_non_approve_review_is_refused(tmp_path, monkeypatch, cfg):
    """FAILURE DEMONSTRATION: a review present but not APPROVE cannot authorize."""
    conf, _ = cfg
    fake = tmp_path / "repo"
    (fake / rc.CANONICAL_APPROVED_REVIEW_REL.parent).mkdir(parents=True)
    review = fake / rc.CANONICAL_APPROVED_REVIEW_REL
    review.write_text("# review\n\n**FINAL VERDICT: REJECT**\n", encoding="utf-8")
    monkeypatch.setattr(rc, "_git_fully_clean", lambda repo: True)
    monkeypatch.setattr(rc, "_git_head", lambda repo: "a" * 40)
    monkeypatch.setattr(rc, "_git_gitlink", lambda repo: "a" * 40)
    args = _Args(execute_dry_run=True, expected_mnl_head="a" * 40,
                 expected_dclaborsupply_head="a" * 40,
                 approved_review=rc.CANONICAL_APPROVED_REVIEW_REL.as_posix(),
                 approved_review_sha256=hashlib.sha256(
                     review.read_bytes()).hexdigest())
    with pytest.raises(rc.StopRun, match="exactly one APPROVE verdict"):
        rc.verify_dry_run_authorization(args, conf, fake)


def test_N5_cli_refuses_the_full_population_run(tmp_path):
    """END-TO-END: the CLI itself refuses, with exit code 2."""
    proc = subprocess.run(
        [sys.executable, str(RUNNER_PATH)],
        capture_output=True, text=True, cwd=str(MNL_ROOT), timeout=900)
    assert proc.returncode == 2
    assert "REFUSED" in proc.stderr
    assert "--execute-dry-run" in proc.stderr


def test_N6_cli_refuses_a_subset_into_the_canonical_root():
    before = _canonical_root_listing()
    proc = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--households", "8",
         "--out", rc.CANONICAL_OUTPUT_ROOT],
        capture_output=True, text=True, cwd=str(MNL_ROOT), timeout=900)
    assert proc.returncode == 2
    assert "canonical production root" in proc.stderr
    # the refused invocation must not change the canonical root's listing,
    # whether or not the root already holds the accepted Phase-5 result
    assert _canonical_root_listing() == before


# =========================================================================== #
# O. transaction
# =========================================================================== #
def test_O1_allowlist_rejects_a_foreign_member(tmp_path):
    txn = rc.Phase5Transaction(tmp_path / "root")
    txn.acquire()
    try:
        (txn.staging / "phase5_scores_free.npy").write_bytes(b"x")
        with pytest.raises(rc.StopRun, match="HP-ALLOW"):
            txn.enforce_allowlist()
    finally:
        txn.release()


def test_O2_lock_is_exclusive(tmp_path):
    root = tmp_path / "root"
    a = rc.Phase5Transaction(root)
    a.acquire()
    b = rc.Phase5Transaction(root)
    try:
        with pytest.raises(rc.StopRun, match="another Phase-5 run holds"):
            b.acquire()
    finally:
        a.release()


def test_O3_publication_is_atomic_and_only_to_attempts(tmp_path):
    txn = rc.Phase5Transaction(tmp_path / "root")
    txn.acquire()
    rc.atomic_write_json({"a": 1}, txn.staging / "phase5_diagnostics.json")
    staging = txn.staging
    dest = txn.finish(rc.STATUS_COMPLETE)
    txn.release()
    assert dest.parent.name == "attempts"
    assert dest.name.endswith(rc.STATUS_COMPLETE)
    assert not staging.exists()                     # renamed, not copied
    assert not (tmp_path / "root" / "complete").exists()


def test_O4_atomic_write_leaves_no_tmp_file(tmp_path):
    target = tmp_path / "phase5_console.log"
    rc.atomic_write_text("hello\n", target)
    assert target.read_text(encoding="utf-8") == "hello\n"
    assert list(tmp_path.glob("*.tmp")) == []


# =========================================================================== #
# P. bounded-subset runner integration
# =========================================================================== #
@pytest.fixture(scope="module")
def bounded_run(tmp_path_factory):
    """One real end-to-end bounded dry run, under a pytest tmp root."""
    out = tmp_path_factory.mktemp("phase5_run")
    conf, digest = rc.load_config(MNL_ROOT)
    outcome = rc.execute_dry_run(conf, digest, out_root=out,
                                 n_households=SUBSET, repo_root=MNL_ROOT,
                                 run_reproduction=True)
    return outcome, out


@pytest.mark.production
def test_P1_bounded_run_completes_and_publishes_to_attempts(bounded_run):
    outcome, out = bounded_run
    assert outcome.status == rc.STATUS_COMPLETE
    assert outcome.attempt_dir.parent.name == "attempts"
    assert not (out / "complete").exists()
    assert not (out / ".phase5.lock").exists()          # lock released
    assert list((out / ".staging").iterdir()) == []      # staging drained


@pytest.mark.production
def test_P2_member_set_is_the_closed_allowlist(bounded_run):
    outcome, _ = bounded_run
    members = sorted(p.name for p in outcome.attempt_dir.iterdir() if p.is_file())
    assert set(members) <= set(rc.ALLOWED_ARTIFACTS)
    for required in ("score_aggregate_summary.json", "score_sum_free37.csv",
                     "meat_free37.npy", "meat_free37.csv",
                     "meat_interior35.npy", "meat_interior35.csv",
                     "phase5_covariance_model.npy", "phase5_covariance_robust.npy",
                     "phase5_parameter_table.csv", "phase5_regional_tests.csv",
                     "phase5_standard_errors.csv",
                     "phase5_diagnostics.json", "phase5_manifest.json",
                     "phase5_console.log"):
        assert required in members, required


@pytest.mark.production
def test_P3_manifest_binds_revisions_environment_and_grade(bounded_run):
    outcome, _ = bounded_run
    m = json.loads((outcome.attempt_dir / "phase5_manifest.json")
                   .read_text(encoding="utf-8"))
    assert m["mode"] == "dry-run-only"
    assert m["real_run_supported"] is False and m["creates_complete"] is False
    b = m["accepted_binding"]
    assert b["verified"] is True and b["gitlink"] == b["dclaborsupply_head"]
    assert b["bread_sha256"] == ib.BREAD_SHA256
    assert b["theta_bytes_sha256"] == ib.ACCEPTED_THETA_SHA256
    assert m["config"]["sha256"] == rc.CONFIG_SHA256
    env = m["environment"]
    for key in ("python", "numpy", "scipy", "jax", "jaxlib", "platform", "threads"):
        assert key in env and env[key] is not None
    assert m["float64_activation"]["jax_enable_x64"] is True
    # R-37a: every serialized artifact record carries the grade
    assert m["inference_grade"] == "subset-diagnostic"
    assert all(r["inference_grade"] == "subset-diagnostic"
               for r in m["artifact_records"])
    # the bundle hash covers every member except the manifest itself
    assert rc.MANIFEST_MEMBER not in m["artifact_hashes"]
    recomputed = hashlib.sha256("\n".join(
        f"{n}:{h}" for n, h in sorted(m["artifact_hashes"].items())
    ).encode("utf-8")).hexdigest()
    assert recomputed == m["bundle_sha256"]


@pytest.mark.production
def test_P4_gate_register_is_complete_and_gating_passes(bounded_run):
    outcome, _ = bounded_run
    d = json.loads((outcome.attempt_dir / "phase5_diagnostics.json")
                   .read_text(encoding="utf-8"))
    seen = {g["gate"] for g in d["gates"]}
    for expected in ("T-5", "T-6", "T-7", "T-8", "T-9", "T-10", "T-14", "T-17",
                     "T-18", "T-19", "T-22", "T-12S", "T-23S", "T-1/T-4",
                     "W-1", "W-2", "W-3", "W-4", "W-5"):
        assert expected in seen, expected
    assert d["gating_failures"] == []
    # the score identity is correctly reported as not applicable on a subset
    ident = [g for g in d["gates"] if g["gate"] == "T-1/T-4"][0]
    assert ident["tier"] == "warning"
    assert ident["observed"]["applicable"] is False


@pytest.mark.production
def test_P5_run_writes_nothing_into_the_repository(bounded_run):
    outcome, _ = bounded_run
    assert outcome.status == rc.STATUS_COMPLETE
    # the bounded tmp-path run must not change the canonical root's listing,
    # whether or not the root already holds the accepted Phase-5 result
    assert _canonical_root_listing() == _CANONICAL_ROOT_LISTING_AT_COLLECTION
    for name in rc.ALLOWED_ARTIFACTS:
        assert not (MNL_ROOT / name).exists()


# =========================================================================== #
# Q. T-12S fresh-process reproduction
# =========================================================================== #
@pytest.mark.production
def test_Q1_reproduction_runs_in_a_real_subprocess_and_matches():
    """A fresh interpreter re-streams and reproduces the aggregate fingerprint."""
    conf, _ = rc.load_config(MNL_ROOT)
    rc.activate_float64_or_refuse()
    parent_result, _ = rc.stream_aggregates(conf, SUBSET, MNL_ROOT)
    parent = rc.aggregate_fingerprint(parent_result)
    child = rc.run_repro_subprocess(SUBSET, MNL_ROOT)

    gate = rc.compare_reproduction(parent, child, conf)
    assert gate.passed, gate.observed
    assert gate.gate == "T-12S" and gate.tier == "gating"
    assert parent["score_stream_sha256"] == child["score_stream_sha256"]
    for k in ("score_sum_free37_max_abs_dev", "meat_free37_max_abs_dev",
              "meat_interior35_max_abs_dev"):
        assert gate.observed[k] == 0.0


@pytest.mark.production
def test_Q2_reproduction_creates_no_second_score_file(tmp_path):
    """addendum s4: no second score file exists at any point.

    Review C fix F1. As shipped this test could not fail: it bound the PARENT's
    cwd with `monkeypatch.chdir` while `run_repro_subprocess` pinned the CHILD's
    cwd to `repo_root`, so the emptiness assertion held no matter what the child
    wrote. The child is now placed in a genuinely empty directory via the `cwd`
    parameter, and the repository tree is additionally compared before and after
    -- so a child that wrote a second score file anywhere would fail this test
    on one of the two arms.
    """
    empty = tmp_path / "child_cwd"
    empty.mkdir()
    assert list(empty.iterdir()) == []
    git_before = rc._git(["status", "--porcelain", "--untracked-files=all"],
                         MNL_ROOT)

    child = rc.run_repro_subprocess(SUBSET, MNL_ROOT, cwd=empty)

    assert child["n_households"] == SUBSET
    # arm 1: the child's OWN working directory is still empty
    assert sorted(p.name for p in empty.rglob("*")) == []
    # arm 2: the repository tree is byte-identical in git's view
    assert rc._git(["status", "--porcelain", "--untracked-files=all"],
                   MNL_ROOT) == git_before
    # the child returns aggregates only -- no row-level payload
    assert set(child) == {
        "score_stream_sha256", "order_sha256", "free_names_sha256",
        "interior_names_sha256", "n_households", "batch_size", "n_batches",
        "idhh_encoding", "dtype", "byte_order", "score_sum_free37",
        "meat_free37", "meat_interior35"}
    assert len(child["score_sum_free37"]) == ib.N_FREE
    assert np.asarray(child["meat_free37"]).shape == (ib.N_FREE, ib.N_FREE)
    assert np.asarray(child["meat_interior35"]).shape == (ib.N_INTERIOR,
                                                          ib.N_INTERIOR)


def test_Q3_cross_tuple_comparison_is_refused(cfg):
    """R-32b: the digest is only defined within the frozen tuple, so a
    cross-tuple comparison is REFUSED rather than reported as a mismatch."""
    conf, _ = cfg
    base = {"score_stream_sha256": "a" * 64, "order_sha256": "b" * 64,
            "free_names_sha256": "c" * 64, "interior_names_sha256": "d" * 64,
            "n_households": 12, "batch_size": 128, "n_batches": 1,
            "idhh_encoding": "int64_le", "dtype": "float64",
            "byte_order": "little",
            "score_sum_free37": [0.0] * ib.N_FREE,
            "meat_free37": np.zeros((ib.N_FREE, ib.N_FREE)).tolist(),
            "meat_interior35": np.zeros((ib.N_INTERIOR, ib.N_INTERIOR)).tolist()}
    assert rc.compare_reproduction(base, dict(base), conf).passed

    for key, bad in (("batch_size", 64), ("idhh_encoding", "int32_le")):
        off = dict(base)
        off[key] = bad
        with pytest.raises(rc.StopRun, match="cross-tuple digest comparison"):
            rc.compare_reproduction(base, off, conf)


def test_Q4_a_digest_mismatch_fails_the_gate(cfg):
    """FAILURE DEMONSTRATION: T-12S is not vacuous."""
    conf, _ = cfg
    base = {"score_stream_sha256": "a" * 64, "order_sha256": "b" * 64,
            "free_names_sha256": "c" * 64, "interior_names_sha256": "d" * 64,
            "n_households": 12, "batch_size": 128, "n_batches": 1,
            "idhh_encoding": "int64_le", "dtype": "float64",
            "byte_order": "little",
            "score_sum_free37": [0.0] * ib.N_FREE,
            "meat_free37": np.zeros((ib.N_FREE, ib.N_FREE)).tolist(),
            "meat_interior35": np.zeros((ib.N_INTERIOR, ib.N_INTERIOR)).tolist()}
    other = dict(base, score_stream_sha256="f" * 64)
    assert not rc.compare_reproduction(base, other, conf).passed
    drifted = dict(base)
    drifted["score_sum_free37"] = [1e-9] + [0.0] * (ib.N_FREE - 1)
    assert not rc.compare_reproduction(base, drifted, conf).passed


# =========================================================================== #
# R. T-23S no row-level persistence
# =========================================================================== #
def test_R1_static_runner_has_no_row_level_write_path():
    """STATIC: the runner never writes a 2-D household-score array.

    All artifact writes are delegated to the Increment-B serializers, which
    refuse row-level content by construction; the runner's own writers are
    text/JSON only."""
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    array_writers = {"save", "savez", "savetxt", "tofile", "to_csv",
                     "to_parquet", "to_pickle", "to_hdf"}
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name in array_writers:
                offenders.append((name, node.lineno))
            # only the BUILTIN open takes a mode; `os.open` is an Attribute call
            # and is used solely for the exclusive lock and the directory fsync
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                mode = None
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                # reads are unrestricted; the ONLY write-capable modes are "w"
                # (the atomic tmp writer) and "rb+" (the fsync handle, which
                # Windows requires be writable). No append/truncate mode exists.
                assert mode in {"r", "rb", "rb+", "w"}, (mode, node.lineno)
    assert offenders == [], f"array write calls in the runner: {offenders}"


def test_R2_static_scanner_is_not_vacuous(tmp_path):
    probe = tmp_path / "probe.py"
    probe.write_text("import numpy as np\ndef f(S,p):\n    np.save(p,S)\n",
                     encoding="utf-8")
    tree = ast.parse(probe.read_text(encoding="utf-8"))
    found = [getattr(n.func, "attr", None) for n in ast.walk(tree)
             if isinstance(n, ast.Call)]
    assert "save" in found


def test_R3_gate_detects_a_planted_row_level_array(tmp_path):
    """BEHAVIOURAL, FAILURE DEMONSTRATION: plant a (12, 37) block and a stray
    temp file; T-23S must fail on both."""
    out = tmp_path / "attempt"
    out.mkdir()
    np.save(out / "meat_free37.npy", np.eye(ib.N_FREE), allow_pickle=False)
    good = rc.gate_T23S_no_row_persistence(["meat_free37.npy"], out, False)
    assert good.passed

    np.save(out / "phase5_covariance_robust.npy",
            np.zeros((12, ib.N_FREE)), allow_pickle=False)
    bad = rc.gate_T23S_no_row_persistence(
        ["meat_free37.npy", "phase5_covariance_robust.npy"], out, False)
    assert not bad.passed
    assert bad.observed["no_row_level_2d_array"] is False

    (out / "phase5_scores_free.npy.tmp").write_bytes(b"x")
    leftover = rc.gate_T23S_no_row_persistence(["meat_free37.npy"], out, False)
    assert not leftover.passed
    assert leftover.observed["no_temporary_batch_remains"] is False


def test_R4_gate_rejects_a_non_allowlisted_member(tmp_path):
    out = tmp_path / "attempt"
    out.mkdir()
    g = rc.gate_T23S_no_row_persistence(
        ["phase5_scores_free.npy", "restricted_store_ref.json"], out, False)
    assert not g.passed
    assert g.observed["member_set_allowlisted"] is False
    assert g.observed["no_restricted_store_member"] is False
    # Review C fix F5: this condition was falsified by the fixture but never
    # asserted, so a gate that stopped computing it would not have been caught
    assert g.observed["no_row_level_score_member"] is False


def test_R5_transient_batch_is_reported_never_serialized(tmp_path):
    """addendum s6: failure finalization reports truthfully WITHOUT serializing."""
    out = tmp_path / "attempt"
    out.mkdir()
    g = rc.gate_T23S_no_row_persistence([], out, True)
    assert g.passed
    assert g.observed["transient_batch_existed_in_memory_only"] is True
    assert g.observed["transient_batch_serialized"] is False
    blob = json.dumps(g.as_dict())
    assert "0.0, 0.0" not in blob                      # no array content
    assert list(out.iterdir()) == []


@pytest.mark.production
def test_R6_published_attempt_holds_no_row_level_array(bounded_run):
    """BEHAVIOURAL on the real published attempt."""
    outcome, _ = bounded_run
    for p in outcome.attempt_dir.glob("*.npy"):
        arr = np.load(p, mmap_mode="r", allow_pickle=False)
        assert arr.ndim == 2 and arr.shape[0] == arr.shape[1]
        assert arr.shape[0] in (ib.N_FREE, ib.N_INTERIOR)
    summary = json.loads((outcome.attempt_dir / "score_aggregate_summary.json")
                         .read_text(encoding="utf-8"))
    long_lists = {k: len(v) for k, v in summary.items()
                  if isinstance(v, list) and len(v) > ib.N_FREE}
    assert long_lists == {}
    d = json.loads((outcome.attempt_dir / "phase5_diagnostics.json")
                   .read_text(encoding="utf-8"))
    t23 = [g for g in d["gates"] if g["gate"] == "T-23S"][0]
    assert t23["passed"] is True
    assert t23["observed"]["transient_batch_serialized"] is False


# =========================================================================== #
# S. STOPPED truthfulness
# =========================================================================== #
@pytest.mark.production
@pytest.mark.parametrize("stage", ["binding", "post_stream", "post_gates"])
def test_S1_injected_failure_publishes_a_truthful_stopped_attempt(
        tmp_path_factory, stage):
    out = tmp_path_factory.mktemp(f"stopped_{stage}")
    conf, digest = rc.load_config(MNL_ROOT)
    outcome = rc.execute_dry_run(conf, digest, out_root=out,
                                 n_households=SUBSET, repo_root=MNL_ROOT,
                                 run_reproduction=False, inject_failure=stage)
    assert outcome.status == rc.STATUS_STOPPED
    assert outcome.attempt_dir.name.endswith(".STOPPED".lstrip("."))
    assert outcome.attempt_dir.parent.name == "attempts"
    assert not (out / "complete").exists()
    assert not (out / ".phase5.lock").exists()

    d = json.loads((outcome.attempt_dir / "phase5_diagnostics.json")
                   .read_text(encoding="utf-8"))
    assert d["status"] == rc.STATUS_STOPPED
    assert d["stop"]["stage"].replace("-", "_") == stage.replace("-", "_")
    assert d["stop"]["halt"] == "HP-TEST"
    # truthful member inventory: exactly what is on disk
    on_disk = sorted(p.name for p in outcome.attempt_dir.iterdir() if p.is_file())
    m = json.loads((outcome.attempt_dir / "phase5_manifest.json")
                   .read_text(encoding="utf-8"))
    assert sorted(m["member_inventory"]) == on_disk
    assert set(on_disk) <= set(rc.ALLOWED_ARTIFACTS)
    # truthful transient-batch report, never serialized
    expected_transient = (stage == "post_stream")
    assert d["transient_batch_existed_in_memory_only"] is expected_transient
    assert d["transient_batch_serialized"] is False
    assert m["transient_batch_serialized"] is False
    # T-23S is evaluated on the failure path too
    assert any(g["gate"] == "T-23S" for g in d["gates"])


@pytest.mark.production
def test_S2_stopped_before_streaming_stages_no_aggregate(tmp_path_factory):
    out = tmp_path_factory.mktemp("stopped_early")
    conf, digest = rc.load_config(MNL_ROOT)
    outcome = rc.execute_dry_run(conf, digest, out_root=out, n_households=SUBSET,
                                 repo_root=MNL_ROOT, run_reproduction=False,
                                 inject_failure="binding")
    members = sorted(p.name for p in outcome.attempt_dir.iterdir() if p.is_file())
    assert members == ["phase5_console.log", "phase5_diagnostics.json",
                       "phase5_manifest.json"]
    assert not any(m in members for m in ib.AGGREGATE_ARTIFACTS)
