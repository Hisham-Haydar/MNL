"""FR P2a region-live Phase-5 — dry-run-only runner and transaction (Increment C).

Governed by, in binding order:

  1. docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
  2. docs/France_case/P2a/FR_P2a_region_live_phase5_inference_design_v4.md
  3. docs/France_case/P2a/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md

WHAT THIS MODULE IS
-------------------
The Increment-C deliverable: the orchestration layer over the committed
Increment-A reducer and Increment-B inference objects.

  * a DRY-RUN-ONLY runner -- there is no real-run code path at all;
  * an aggregate-only attempt transaction (addendum s8): lock, unique staging
    directory, closed allowlisted member set, per-file fsync then atomic
    same-volume rename, publication to `attempts/<id>_<status>`;
  * T-12S fresh-process aggregate reproduction (addendum s4, s7);
  * T-23S no-row-level-persistence finalisation (addendum s6);
  * STOPPED truthfulness on any failure (addendum s8);
  * the score-identity gate from the STREAMED aggregate (addendum s5);
  * accepted-artifact and revision binding verified BEFORE any computation.

`complete/` is never created, never promoted, and has no code path.

COMPUTE ROUTES
--------------
The only compute routes are the committed module APIs:

    p2a_phase5_score_stream : load_parameter_map, build_production_binding,
                              run_score_stream
    p2a_phase5_inference    : load_bread, load_accepted_gradients,
                              build_covariances, run_regional_tests,
                              build_parameter_table, gate_*, warning_*,
                              write_matrix, write_table,
                              write_score_aggregate_summary

Nothing here recomputes a score, a Hessian, a covariance or a Wald statistic.

DRY-RUN AUTHORIZATION (addendum s8, design v4 s18.1, charter s9)
----------------------------------------------------------------
The full-population dry run is reachable from the canonical config but refused
until an approved Increment-C review exists and is named on the command line
with its SHA-256, alongside expected HEADs and fully clean worktrees. That
review file does not exist during implementation, so the full dry run cannot be
executed in the implementation task -- which is the intended mechanism, not an
omission. Bounded subsets are permitted only into an explicit `--out` root that
is not the canonical production root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import p2a_phase5_inference as ib          # noqa: E402
import p2a_phase5_score_stream as ss       # noqa: E402

# --------------------------------------------------------------------------- #
# 1. frozen runner constants
# --------------------------------------------------------------------------- #
CONFIG_REL = "scripts/p2a/configs/p2a_phase5_inference_v1.yaml"
# digest binding: the runner refuses to start if the canonical config's bytes
# differ from this recorded value (charter s4-C "config-driven, digest-bound")
CONFIG_SHA256 = "08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9"

CANONICAL_OUTPUT_ROOT = "outputs/p2a_singles2016/region_live_v1/phase5_inference_v1"
# Binding advance, third application of the R-29 / R-48 precedent (disclosed in
# the Increment-C refix report s4). Each superseded review document is immutable
# evidence of a NON-approving verdict -- v1 APPROVE AFTER FIXES, v2 REJECT -- and
# none may ever authorize the run. The authorization is therefore bound to the
# decisive v3 document. Because `--approved-review` must equal this path EXACTLY,
# every superseded path is refused by binding: there is no argument combination
# under which one of them can authorize, whatever its digest.
CANONICAL_APPROVED_REVIEW_REL = Path(
    "docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md")
SUPERSEDED_REVIEW_RELS: Tuple[Path, ...] = (
    Path("docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md"),
    Path("docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md"),
)
APPROVE_LINE = "**FINAL VERDICT: APPROVE**"

STATUS_COMPLETE = "PHASE_5_DRY_RUN_COMPLETE"
STATUS_STOPPED = "STOPPED"

# Runner-owned members, added to the Increment-B aggregate set. The union is the
# CLOSED allowlist: nothing outside it may exist in a published attempt.
RUNNER_OWNED_ARTIFACTS: Tuple[str, ...] = (
    "phase5_diagnostics.json", "phase5_manifest.json", "phase5_console.log")
ALLOWED_ARTIFACTS: Tuple[str, ...] = tuple(ib.AGGREGATE_ARTIFACTS) + RUNNER_OWNED_ARTIFACTS
MANIFEST_MEMBER = "phase5_manifest.json"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class StopRun(Exception):
    """Controlled halt. Carries the halt name and a value-free reason.

    Mirrors the accepted Phase-3/4 runner's `StopRun` contract: the message
    names shapes, counts, hashes and gate identities only, never a household
    quantity.
    """

    def __init__(self, halt: str, stage: str, reason: str):
        super().__init__(f"[{halt}] {stage}: {reason}")
        self.halt = halt
        self.stage = stage
        self.reason = reason


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _bundle_sha256(directory: Path, manifest_member: str) -> str:
    """The accepted bundle hash-of-hashes, reused verbatim from Phase 4."""
    names = sorted(n for n in os.listdir(directory) if n != manifest_member)
    joined = "\n".join(f"{n}:{_sha256_file(directory / n)}" for n in names)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _git(args: Sequence[str], repo: Path) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                         text=True, check=False)
    return out.stdout.strip()


def _git_head(repo: Path) -> str:
    return _git(["rev-parse", "HEAD"], repo)


def _git_gitlink(repo: Path) -> str:
    line = _git(["ls-tree", "HEAD", "dclaborsupply-monorepo"], repo)
    parts = line.split()
    return parts[2] if len(parts) >= 3 else ""


def _git_fully_clean(repo: Path) -> bool:
    return _git(["status", "--porcelain", "--untracked-files=all"], repo) == ""


# --------------------------------------------------------------------------- #
# 2. float64 activation (R-32c) and environment capture
# --------------------------------------------------------------------------- #
def activate_float64_or_refuse() -> Dict[str, Any]:
    """Eagerly enable float64 BEFORE any array is created, or refuse (R-32c).

    `engine_jax._load_jax()` is the accepted float64 initialiser named by design
    v4 s3.3. It is invoked here, at the very top of the run, so no array can be
    created at float32 by an unlucky import order. If the flag is not then set,
    the runner halts rather than proceeding at reduced precision.
    """
    from dclaborsupply.likelihood import engine_jax

    engine_jax._load_jax()
    import jax

    if jax.config.read("jax_enable_x64") is not True:
        raise StopRun("HP-X64", "float64-activation",
                      "jax_enable_x64 is not active after the accepted "
                      "initialiser; the float64 score contract cannot be honoured")
    return {"jax_enable_x64": True,
            "activated_by": "dclaborsupply.likelihood.engine_jax._load_jax"}


def capture_environment() -> Dict[str, Any]:
    """The design v4 s18.5 environment mandate: record what Phases 3-4 never did."""
    import jax
    import jaxlib
    import scipy

    thread_vars = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                   "NUMEXPR_NUM_THREADS", "XLA_FLAGS", "JAX_PLATFORMS",
                   "JAX_ENABLE_X64")
    return {
        "python": sys.version.split()[0],
        "python_full": sys.version,
        "executable": sys.executable,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "jax": jax.__version__,
        "jaxlib": jaxlib.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "jax_default_backend": str(jax.default_backend()),
        "jax_device_count": int(jax.device_count()),
        "threads": {k: os.environ.get(k) for k in thread_vars},
        "cpu_count": os.cpu_count(),
    }


# --------------------------------------------------------------------------- #
# 3. accepted-artifact and revision binding (verified BEFORE any computation)
# --------------------------------------------------------------------------- #
def load_config(repo_root: Path = MNL_ROOT, *, verify_digest: bool = True
                ) -> Tuple[Dict[str, Any], str]:
    path = Path(repo_root) / CONFIG_REL
    if not path.is_file():
        raise StopRun("HP-CONFIG", "config", f"canonical config missing: {CONFIG_REL}")
    digest = _sha256_file(path)
    if verify_digest and digest != CONFIG_SHA256:
        raise StopRun("HP-CONFIG", "config",
                      f"config SHA-256 {digest} != recorded {CONFIG_SHA256}; the "
                      "runner is digest-bound to its canonical configuration")
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if str(cfg["run"]["mode"]) != "dry-run-only":
        raise StopRun("HP-SCOPE", "config",
                      f"run.mode is {cfg['run']['mode']!r}; this runner supports "
                      "dry-run-only and has no real-run code path")
    if bool(cfg["run"].get("real_run_supported", False)):
        raise StopRun("HP-SCOPE", "config", "real_run_supported must be false")
    return cfg, digest


def verify_accepted_binding(cfg: Dict[str, Any], config_sha256: str,
                            repo_root: Path = MNL_ROOT) -> Dict[str, Any]:
    """Bind to the accepted artifacts and revisions. Runs before any compute.

    Verifies: MNL HEAD (recorded), gitlink == nested HEAD, the expected nested
    HEAD, both accepted bundle hashes, the bread hash, the accepted theta-byte
    hash, the certified spec hash, and this config's own digest.
    """
    repo = Path(repo_root)
    nested = repo / "dclaborsupply-monorepo"
    acc = cfg["accepted"]

    head = _git_head(repo)
    nested_head = _git_head(nested)
    gitlink = _git_gitlink(repo)
    if not _HEX40.match(head or ""):
        raise StopRun("HP-REV", "revision-binding", "could not read MNL HEAD")
    if gitlink != nested_head:
        raise StopRun("HP-REV", "revision-binding",
                      f"MNL gitlink {gitlink} != nested HEAD {nested_head}")
    expected_nested = str(cfg["revisions"]["expected_dclaborsupply_head"])
    if nested_head != expected_nested:
        raise StopRun("HP-REV", "revision-binding",
                      f"nested HEAD {nested_head} != accepted {expected_nested}")

    p3_dir = repo / acc["phase3_bundle_dir"]
    p4_dir = repo / acc["phase4_bundle_dir"]
    p3 = _bundle_sha256(p3_dir, acc["phase3_manifest_member"])
    p4 = _bundle_sha256(p4_dir, acc["phase4_manifest_member"])
    if p3 != acc["phase3_bundle_sha256"]:
        raise StopRun("HP-MUT", "accepted-binding",
                      f"Phase-3 bundle {p3} != accepted {acc['phase3_bundle_sha256']}")
    if p4 != acc["phase4_bundle_sha256"]:
        raise StopRun("HP-MUT", "accepted-binding",
                      f"Phase-4 bundle {p4} != accepted {acc['phase4_bundle_sha256']}")

    bread = _sha256_file(repo / ib.PHASE4_BREAD_NPY)
    if bread != acc["bread_sha256"]:
        raise StopRun("HP-BREAD", "accepted-binding",
                      f"bread {bread} != accepted {acc['bread_sha256']}")
    theta = ib.accepted_theta_sha256(repo)
    if theta != acc["theta_bytes_sha256"]:
        raise StopRun("HP-MUT", "accepted-binding",
                      f"theta bytes {theta} != accepted {acc['theta_bytes_sha256']}")
    spec = _sha256_file(repo / ss.CERTIFIED_SPEC_YAML)
    if spec != acc["spec_sha256"]:
        raise StopRun("HP-MUT", "accepted-binding",
                      f"certified spec {spec} != accepted {acc['spec_sha256']}")

    return {
        "checked_at": _utcnow(), "verified": True,
        "mnl_head": head, "dclaborsupply_head": nested_head, "gitlink": gitlink,
        "mnl_worktree_clean": _git_fully_clean(repo),
        "nested_worktree_clean": _git_fully_clean(nested),
        "phase3_bundle_sha256": p3, "phase4_bundle_sha256": p4,
        "bread_sha256": bread, "theta_bytes_sha256": theta,
        "spec_sha256": spec, "config_sha256": config_sha256,
    }


# --------------------------------------------------------------------------- #
# 4. dry-run authorization (addendum s8 / design v4 s18.1 / charter s9)
# --------------------------------------------------------------------------- #
def verify_dry_run_authorization(args, cfg: Dict[str, Any],
                                 repo_root: Path = MNL_ROOT) -> Dict[str, Any]:
    """Authorize the FULL-population dry run, or halt.

    The mechanism the addendum s8 prescribes, implemented exactly as the accepted
    Phase-3/Phase-4 runner implements its own: an approved review document named
    on the command line by its canonical path and SHA-256, an exact APPROVE
    verdict inside it, expected HEADs, and fully clean worktrees. All checks run
    BEFORE any computation.

    During implementation the review file does not exist, so this always halts --
    which is the intended refusal, and is what makes the full dry run a
    separately authorized later step.
    """
    auth = cfg["authorization"]
    if not bool(auth.get("required", True)):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "authorization.required must be true")
    if not getattr(args, "execute_dry_run", False):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "the full-population dry run requires --execute-dry-run")

    repo = Path(repo_root)
    nested = repo / "dclaborsupply-monorepo"
    exp_mnl = getattr(args, "expected_mnl_head", None)
    exp_dcl = getattr(args, "expected_dclaborsupply_head", None)
    review_arg = getattr(args, "approved_review", None)
    review_sha = getattr(args, "approved_review_sha256", None)

    if not (exp_mnl and _HEX40.match(exp_mnl)):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "--expected-mnl-head must be a 40-hex SHA")
    if not (exp_dcl and _HEX40.match(exp_dcl)):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "--expected-dclaborsupply-head must be a 40-hex SHA")
    if not (review_sha and _HEX64.match(review_sha)):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "--approved-review-sha256 must be a 64-hex SHA-256")
    if (review_arg is None or Path(review_arg).as_posix()
            != CANONICAL_APPROVED_REVIEW_REL.as_posix()):
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      f"--approved-review must be exactly "
                      f"{CANONICAL_APPROVED_REVIEW_REL.as_posix()!r}")

    head = _git_head(repo)
    if head != exp_mnl:
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      f"MNL HEAD {head} != expected {exp_mnl}")
    nested_head = _git_head(nested)
    if nested_head != exp_dcl:
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      f"nested HEAD {nested_head} != expected {exp_dcl}")
    if _git_gitlink(repo) != nested_head:
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "MNL gitlink != nested HEAD")
    if bool(auth.get("requires_clean_worktrees", True)):
        if not _git_fully_clean(repo):
            raise StopRun("HP-AUTH", "dry-run-authorization",
                          "MNL worktree not fully clean (--untracked-files=all)")
        if not _git_fully_clean(nested):
            raise StopRun("HP-AUTH", "dry-run-authorization",
                          "dclaborsupply-monorepo worktree not fully clean")

    review = repo / CANONICAL_APPROVED_REVIEW_REL
    if not review.is_file():
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      f"approved Increment-C review missing: "
                      f"{CANONICAL_APPROVED_REVIEW_REL.as_posix()}; the "
                      "full-population dry run is a separately authorized step")
    actual = _sha256_file(review)
    if actual != review_sha:
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "approved review SHA-256 != --approved-review-sha256")
    verdicts = [ln.strip() for ln in review.read_text(encoding="utf-8").splitlines()
                if ln.strip().startswith("**FINAL VERDICT:")]
    if verdicts != [APPROVE_LINE]:
        raise StopRun("HP-AUTH", "dry-run-authorization",
                      "approved review does not carry exactly one APPROVE verdict")
    return {"verified": True, "execution_ready": True,
            "approved_review": CANONICAL_APPROVED_REVIEW_REL.as_posix(),
            "approved_review_sha256": actual,
            "expected_mnl_head": exp_mnl, "expected_dclaborsupply_head": exp_dcl}


# --------------------------------------------------------------------------- #
# 5. aggregate-only attempt transaction (addendum s8)
# --------------------------------------------------------------------------- #
def _fsync_file(path: Path) -> None:
    """Flush one staged file to stable storage.

    Opened "rb+" rather than "rb": Windows refuses `os.fsync` on a read-only
    handle with EBADF, and "rb+" gives a writable handle without truncating.
    """
    with open(path, "rb+") as fh:
        os.fsync(fh.fileno())


def _fsync_dir(path: Path) -> None:
    """Best-effort directory fsync. Windows has no directory fd; skip there."""
    if os.name == "nt":
        return
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Phase5Transaction:
    """Lock + staging + attempts transaction. NEVER creates or promotes complete/.

    Addendum s8. The publication target is always `attempts/<id>_<status>`. There
    is no `complete` attribute, no `success_status` that publishes elsewhere, and
    no code path that constructs a `complete/` path -- the absence is structural,
    not conditional.
    """

    _ALLOC_MAX_TRIES = 100

    def __init__(self, root: Path, label: str = "dryrun"):
        self.root = Path(root)
        self.label = str(label)
        self.lock = self.root / ".phase5.lock"
        self.staging_base = self.root / ".staging"
        self.attempts = self.root / "attempts"
        self.attempt_id: Optional[str] = None
        self.staging: Optional[Path] = None
        self._locked = False

    def _destination_exists(self, attempt_id: str) -> bool:
        if (self.staging_base / attempt_id).exists():
            return True
        if self.attempts.is_dir():
            for p in self.attempts.iterdir():
                if p.name == attempt_id or p.name.startswith(attempt_id + "_"):
                    return True
        return False

    def _allocate(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for _ in range(self._ALLOC_MAX_TRIES):
            attempt_id = f"{stamp}_{os.getpid()}_{uuid.uuid4().hex}_{self.label}"
            if self._destination_exists(attempt_id):
                continue
            try:
                (self.staging_base / attempt_id).mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                continue
            return attempt_id
        raise StopRun("HP-TXN", "attempt-allocation",
                      f"no unique attempt id after {self._ALLOC_MAX_TRIES} tries")

    def acquire(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StopRun("HP-TXN", "lock",
                          f"another Phase-5 run holds {self.lock.name}") from None
        os.close(fd)
        self._locked = True
        self.attempts.mkdir(exist_ok=True)
        self.staging_base.mkdir(exist_ok=True)
        try:
            self.attempt_id = self._allocate()
        except StopRun:
            self.release()
            raise
        self.staging = self.staging_base / self.attempt_id
        self.lock.write_text(json.dumps({"pid": os.getpid(), "utc": _utcnow(),
                                         "attempt": self.attempt_id}),
                             encoding="utf-8")

    def assert_member_allowed(self, name: str) -> None:
        if name not in ALLOWED_ARTIFACTS:
            raise StopRun("HP-ALLOW", "artifact-allowlist",
                          f"{name!r} is not in the closed Phase-5 member set")

    def staged_members(self) -> List[str]:
        if self.staging is None or not self.staging.is_dir():
            return []
        return sorted(p.name for p in self.staging.iterdir() if p.is_file())

    def enforce_allowlist(self) -> List[str]:
        members = self.staged_members()
        extra = [m for m in members if m not in ALLOWED_ARTIFACTS]
        if extra:
            raise StopRun("HP-ALLOW", "artifact-allowlist",
                          f"non-allowlisted member(s) staged: {extra}")
        return members

    def finish(self, status: str) -> Path:
        """Publish atomically to `attempts/<id>_<status>`. Never to complete/."""
        assert self.staging is not None and self.attempt_id is not None
        for p in sorted(self.staging.iterdir()):
            if p.is_file():
                _fsync_file(p)
        _fsync_dir(self.staging)
        dest = self.attempts / f"{self.attempt_id}_{status}"
        os.replace(self.staging, dest)
        _fsync_dir(self.attempts)
        return dest

    def release(self) -> None:
        if self._locked and self.lock.is_file():
            self.lock.unlink()
            self._locked = False


def atomic_write_text(text: str, path: Path) -> None:
    """tmp -> fsync -> same-volume atomic rename (addendum s8 write semantics)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def atomic_write_json(obj: Dict[str, Any], path: Path) -> None:
    atomic_write_text(json.dumps(obj, indent=2, sort_keys=True, default=str), path)


# --------------------------------------------------------------------------- #
# 6. the streaming + inference computation (committed APIs only)
# --------------------------------------------------------------------------- #
@dataclass
class RunOutcome:
    status: str
    attempt_dir: Optional[Path] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    manifest: Dict[str, Any] = field(default_factory=dict)
    console: List[str] = field(default_factory=list)


def stream_aggregates(cfg: Dict[str, Any], n_households: Optional[int],
                      repo_root: Path = MNL_ROOT):
    """Stream the aggregates through the committed Increment-A reducer."""
    binding = ss.build_production_binding(
        repo_root=repo_root,
        household_limit=(None if n_households is None else int(n_households)))
    batch = int(cfg["population"]["batch_size"])
    mode = str(cfg["population"]["ad_mode"])
    return ss.run_score_stream(binding, batch_size=batch, mode=mode), binding


def aggregate_fingerprint(result) -> Dict[str, Any]:
    """The exact comparison surface of T-12S (addendum s4).

    Scalars and hashes only, plus the two meats and the score sum. This is what
    the fresh process prints and what the parent compares -- no score file is
    created by either side.
    """
    return {
        "score_stream_sha256": result.score_stream_sha256,
        "order_sha256": result.order_sha256,
        "free_names_sha256": result.free_names_sha256,
        "interior_names_sha256": result.interior_names_sha256,
        "n_households": int(result.n_households),
        "batch_size": int(result.batch_size),
        "n_batches": int(result.n_batches),
        "idhh_encoding": result.idhh_encoding,
        "dtype": result.dtype,
        "byte_order": result.byte_order,
        "score_sum_free37": [float(v) for v in result.score_sum_free37],
        "meat_free37": [[float(v) for v in row] for row in result.meat_free37],
        "meat_interior35": [[float(v) for v in row] for row in result.meat_interior35],
    }


# --------------------------------------------------------------------------- #
# 7. T-12S fresh-process aggregate reproduction (addendum s4, s7)
# --------------------------------------------------------------------------- #
REPRO_BEGIN = "<<<PHASE5_REPRO_JSON_BEGIN>>>"
REPRO_END = "<<<PHASE5_REPRO_JSON_END>>>"


def run_repro_subprocess(n_households: Optional[int], repo_root: Path = MNL_ROOT,
                         timeout: int = 3600, *,
                         cwd: Optional[Path] = None) -> Dict[str, Any]:
    """Re-stream in a REAL fresh interpreter and return its aggregate fingerprint.

    The child runs this same module with `--repro-json`, re-derives everything
    from the accepted sources, and prints the fingerprint between sentinels on
    stdout. Nothing is written by the child: no second score file exists at any
    point (addendum s4).

    `cwd` selects the child's working directory and defaults to `repo_root`.
    Review C fix F1: every path the child uses is absolute (the module resolves
    `MNL_ROOT` from `__file__`), so the child can be run from an arbitrary
    directory. Exposing that lets a test place the child in a genuinely empty
    directory and observe whether it writes anything -- which the shipped
    `test_Q2` could not do, because it bound only the PARENT's cwd while the
    child stayed pinned to `repo_root`.
    """
    cmd = [sys.executable, str(Path(__file__).resolve()), "--repro-json"]
    if n_households is not None:
        cmd += ["--households", str(int(n_households))]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=str(repo_root if cwd is None else cwd))
    if proc.returncode != 0:
        raise StopRun("HP-REPRO", "T-12S",
                      f"fresh-process reproduction exited {proc.returncode}; "
                      f"stderr tail: {proc.stderr.strip()[-300:]}")
    out = proc.stdout
    if REPRO_BEGIN not in out or REPRO_END not in out:
        raise StopRun("HP-REPRO", "T-12S",
                      "fresh-process reproduction produced no fingerprint block")
    blob = out.split(REPRO_BEGIN, 1)[1].split(REPRO_END, 1)[0]
    return json.loads(blob)


def compare_reproduction(parent: Dict[str, Any], child: Dict[str, Any],
                         cfg: Dict[str, Any]) -> ib.GateResult:
    """T-12S. Digest/fingerprints/counts exact; aggregates by the config rule.

    The comparison is scoped to the FROZEN tuple of ruling R-32b -- idhh
    encoding, batch size and AD mode. A cross-tuple comparison is refused rather
    than reported as a mismatch, because the digest is only defined within a
    tuple.
    """
    tup = cfg["reproduction_tuple"]
    for side, name in ((parent, "parent"), (child, "child")):
        if (side["idhh_encoding"] != tup["idhh_encoding"]
                or side["batch_size"] != int(tup["batch_size"])):
            raise StopRun("HP-REPRO", "T-12S",
                          f"{name} fingerprint is outside the frozen reproduction "
                          f"tuple (encoding={side['idhh_encoding']}, "
                          f"batch_size={side['batch_size']}); cross-tuple digest "
                          "comparison is refused (R-32b)")

    exact_keys = ("score_stream_sha256", "order_sha256", "free_names_sha256",
                  "interior_names_sha256", "n_households", "batch_size",
                  "n_batches", "idhh_encoding", "dtype", "byte_order")
    checks = {f"{k}_exact": (parent[k] == child[k]) for k in exact_keys}

    atol = float(cfg["gates"]["repro_aggregate_atol"])
    rtol = float(cfg["gates"]["repro_aggregate_rtol"])
    deviations = {}
    for k in ("score_sum_free37", "meat_free37", "meat_interior35"):
        a = np.asarray(parent[k], dtype=np.float64)
        b = np.asarray(child[k], dtype=np.float64)
        checks[f"{k}_match"] = bool(np.allclose(a, b, atol=atol, rtol=rtol))
        deviations[f"{k}_max_abs_dev"] = float(np.max(np.abs(a - b))) if a.size else 0.0

    return ib.GateResult(
        gate="T-12S", tier="gating", passed=all(checks.values()),
        statement="Fresh-process aggregate reproduction: a new interpreter "
                  "re-streams from the accepted sources and reproduces the "
                  "score-stream digest, score sum, M_37, M_35, order fingerprint, "
                  "household count, batch size and environment. No second score "
                  "file is created.",
        observed={**{k: bool(v) for k, v in checks.items()}, **deviations,
                  "parent_digest": parent["score_stream_sha256"],
                  "child_digest": child["score_stream_sha256"]},
        bar={"frozen_tuple": dict(tup), "aggregate_atol": atol,
             "aggregate_rtol": rtol, "exact_keys": list(exact_keys)})


# --------------------------------------------------------------------------- #
# 8. T-23S no-row-level-persistence finalisation (addendum s6)
# --------------------------------------------------------------------------- #
def gate_T23S_no_row_persistence(members: Sequence[str], out_dir: Path,
                                 transient_batch_in_memory: bool) -> ib.GateResult:
    """T-23S. An artifact-persistence gate, not an application-surface count.

    `transient_batch_in_memory` is reported truthfully and is NEVER serialized:
    the runner records only whether a transient batch existed, never its content.
    """
    out_dir = Path(out_dir)
    non_allowlisted = [m for m in members if m not in ALLOWED_ARTIFACTS]
    row_level_names = [m for m in members
                       if "score" in m.lower() and m not in ib.AGGREGATE_ARTIFACTS
                       and m not in RUNNER_OWNED_ARTIFACTS]
    leftovers = ([str(p.name) for p in out_dir.iterdir()
                  if p.name.endswith(".tmp") or p.name.startswith(".batch")]
                 if out_dir.is_dir() else [])

    row_level_arrays = []
    if out_dir.is_dir():
        for p in sorted(out_dir.glob("*.npy")):
            arr = np.load(p, mmap_mode="r", allow_pickle=False)
            if arr.ndim == 2 and arr.shape[0] != arr.shape[1]:
                row_level_arrays.append(f"{p.name}{arr.shape}")
            elif arr.ndim == 2 and arr.shape[0] not in (ib.N_FREE, ib.N_INTERIOR):
                row_level_arrays.append(f"{p.name}{arr.shape}")

    checks = {
        "member_set_allowlisted": not non_allowlisted,
        "no_row_level_score_member": not row_level_names,
        "no_row_level_2d_array": not row_level_arrays,
        "no_restricted_store_member": not any("restricted" in m.lower()
                                              for m in members),
        "no_temporary_batch_remains": not leftovers,
    }
    return ib.GateResult(
        gate="T-23S", tier="gating", passed=all(checks.values()),
        statement="No row-level score persistence: the member set is "
                  "allowlist-closed and aggregate-only, no restricted-store "
                  "member exists, and no temporary batch remains after success "
                  "or failure.",
        observed={**{k: bool(v) for k, v in checks.items()},
                  "members": list(members),
                  "non_allowlisted": non_allowlisted,
                  "row_level_arrays": row_level_arrays,
                  "leftovers": leftovers,
                  "transient_batch_existed_in_memory_only":
                      bool(transient_batch_in_memory),
                  "transient_batch_serialized": False},
        bar={"allowlist": list(ALLOWED_ARTIFACTS)})


def gate_score_identity(result, grads: "ib.AcceptedGradients",
                        cfg: Dict[str, Any], full_population: bool) -> ib.GateResult:
    """Addendum s5: sum_i s_i == -grad negLL, from the STREAMED aggregate.

    The identity is a WHOLE-SAMPLE property, so on a bounded subset it is
    reported as `not_applicable` rather than passed or failed -- a subset prefix
    sum is not near the accepted gradient and pretending otherwise would be a
    false gate either way.
    """
    atol = float(cfg["gates"]["score_identity_atol"])
    rtol = float(cfg["gates"]["score_identity_rtol"])
    summed = np.asarray(result.score_sum_free37, dtype=np.float64)
    target = -np.asarray(grads.free, dtype=np.float64)
    dev = float(np.max(np.abs(summed - target)))
    if not full_population:
        return ib.GateResult(
            gate="T-1/T-4", tier="warning", passed=True,
            statement="Score identity sum_i s_i = -grad negLL. NOT APPLICABLE on "
                      "a bounded subset: the first-order condition is a "
                      "whole-sample property. Evaluated only on the full "
                      "population.",
            observed={"applicable": False, "n_households": int(result.n_households),
                      "max_abs_dev_informational": dev},
            bar={"atol": atol, "rtol": rtol})
    ok = bool(np.allclose(summed, target, atol=atol, rtol=rtol))
    return ib.GateResult(
        gate="T-1/T-4", tier="gating", passed=ok,
        statement="Score identity from the streamed aggregate: "
                  "np.allclose(sum_scores, -gradient_free, atol=1e-8, rtol=1e-8)",
        observed={"applicable": True, "max_abs_dev": dev,
                  "n_households": int(result.n_households)},
        bar={"atol": atol, "rtol": rtol,
             "gradient_source": ib.PHASE4_DIAGNOSTICS})


# --------------------------------------------------------------------------- #
# 9. the run
# --------------------------------------------------------------------------- #
def execute_dry_run(cfg: Dict[str, Any], config_sha256: str, *,
                    out_root: Path, n_households: Optional[int],
                    repo_root: Path = MNL_ROOT,
                    run_reproduction: bool = True,
                    inject_failure: Optional[str] = None) -> RunOutcome:
    """The single execution path. Dry run only; publishes to attempts/ only.

    `inject_failure` is a TEST SEAM for the STOPPED probe. It names a stage at
    which to raise a controlled StopRun; it cannot make a failing run succeed,
    and it does not alter any computation.
    """
    console: List[str] = []

    def log(msg: str) -> None:
        line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
        console.append(line)

    full_population = (n_households is None
                       or int(n_households) == int(cfg["population"]["n_households_full"]))
    gates: List[ib.GateResult] = []
    transient_batch_in_memory = False
    txn = Phase5Transaction(out_root, label="dryrun")
    status = STATUS_STOPPED
    stop: Optional[StopRun] = None
    diagnostics: Dict[str, Any] = {"generated_at": _utcnow()}
    manifest: Dict[str, Any] = {}

    txn.acquire()
    try:
        # -- pre-compute binding -------------------------------------------- #
        env_x64 = activate_float64_or_refuse()
        environment = capture_environment()
        binding_record = verify_accepted_binding(cfg, config_sha256, repo_root)
        log(f"accepted binding verified: MNL {binding_record['mnl_head'][:12]} "
            f"gitlink {binding_record['gitlink'][:12]}")
        if inject_failure == "binding":
            raise StopRun("HP-TEST", "binding", "injected failure at binding")

        pmap = ss.load_parameter_map(repo_root)
        bread = ib.load_bread(pmap, repo_root)
        grads = ib.load_accepted_gradients(pmap, repo_root)
        param_map_frame = pd.read_csv(Path(repo_root) / ss.PARAMETER_MAP_CSV)

        # -- stream (transient batches exist ONLY in memory) ----------------- #
        transient_batch_in_memory = True
        result, _bind = stream_aggregates(cfg, n_households, repo_root)
        transient_batch_in_memory = False
        log(f"streamed {result.n_households} households, batch "
            f"{result.batch_size}, digest {result.score_stream_sha256[:12]}")
        if inject_failure == "post_stream":
            transient_batch_in_memory = True
            raise StopRun("HP-TEST", "post-stream", "injected failure after streaming")

        # -- inference objects (Increment-B APIs only) ----------------------- #
        cov = ib.build_covariances(bread, result.meat_interior35,
                                   meat_n_households=result.n_households)
        theta_interior = np.array(
            [float(param_map_frame.set_index("param")
                   .loc[n, "accepted_value_full_precision"])
             for n in pmap.interior_names], dtype=np.float64)
        reg = ib.run_regional_tests(pmap, cov, theta_interior)
        table = ib.build_parameter_table(pmap, cov, param_map_frame, grads)
        grade = cov.diagnostics["inference_grade"]
        log(f"inference objects built (inference_grade={grade})")

        # -- gates ----------------------------------------------------------- #
        gates.append(ib.gate_T5_bread_provenance(
            bread, {"phase3": binding_record["phase3_bundle_sha256"],
                    "phase4": binding_record["phase4_bundle_sha256"]},
            theta_sha256=binding_record["theta_bytes_sha256"]))
        gates.append(ib.gate_T6_bread_integrity(bread))
        gates.append(ib.gate_T7_meat_validity(result.meat_interior35))
        gates.append(ib.gate_T8_solve_stability(cov))
        gates.append(ib.gate_T9_covariance_validity(cov))
        gates.append(ib.gate_T10_correction_scalar(cov))
        gates.append(ib.gate_T14_regional(reg))
        gates.append(ib.gate_T17_fingerprints(pmap, repo_root))
        gates.append(ib.gate_T18_valid_correlations(cov))
        gates.append(ib.gate_T19_stationarity(bread, cov, grads.interior))
        gates.append(ib.gate_T22_numerical_kkt(grads.active_multipliers,
                                               grads.interior_max_abs))
        gates.append(gate_score_identity(result, grads, cfg, full_population))
        gates.append(ib.warning_W1_ratio(cov))
        gates.append(ib.warning_W2_regional_spectrum(reg))
        gates.append(ib.warning_W3_effective_rank(result.meat_interior35))
        gates.append(ib.warning_W4_near_boundary(cov, param_map_frame))
        sel = np.asarray(pmap.interior_positions_in_free)
        gates.append(ib.warning_W5_centring(result.score_sum_free37[sel], cov,
                                            result.n_households))

        # -- T-12S fresh-process reproduction -------------------------------- #
        repro: Optional[Dict[str, Any]] = None
        if run_reproduction:
            child = run_repro_subprocess(n_households, repo_root)
            t12s = compare_reproduction(aggregate_fingerprint(result), child, cfg)
            gates.append(t12s)
            repro = {"child_digest": child["score_stream_sha256"],
                     "child_environment_recorded": True,
                     "second_score_file_created": False}
            log(f"T-12S fresh-process reproduction: "
                f"{'PASS' if t12s.passed else 'FAIL'}")
        if inject_failure == "post_gates":
            raise StopRun("HP-TEST", "post-gates", "injected failure after gates")

        # -- serialize the aggregate-only member set ------------------------- #
        assert txn.staging is not None
        records = write_aggregate_artifacts(txn.staging, result, cov, reg, table,
                                            pmap, grade)
        log(f"staged {len(records)} aggregate artifacts")

        failures = ib.gating_failures(gates)
        if failures:
            raise StopRun("HP-GATE", "gate-battery",
                          f"gating failures: {failures}")
        status = STATUS_COMPLETE

    except StopRun as exc:
        stop = exc
        status = STATUS_STOPPED
        log(f"STOPPED: {exc}")
    except Exception as exc:                       # sanitized, value-free
        stop = StopRun("HP-INTERNAL", "run",
                       f"{type(exc).__module__}.{type(exc).__name__} raised; "
                       "message suppressed to guarantee no household quantity "
                       "reaches the record")
        status = STATUS_STOPPED
        log(f"STOPPED: {stop}")

    # -- finalisation: truthful either way ---------------------------------- #
    assert txn.staging is not None
    members_before = txn.staged_members()
    t23s = gate_T23S_no_row_persistence(members_before, txn.staging,
                                        transient_batch_in_memory)
    gates.append(t23s)
    if status == STATUS_COMPLETE and not t23s.passed:
        status = STATUS_STOPPED
        stop = stop or StopRun("HP-PERSIST", "T-23S", "row-level persistence gate failed")
        log(f"STOPPED: {stop}")

    diagnostics.update({
        "status": status,
        "attempt_id": txn.attempt_id,
        "full_population": full_population,
        "n_households_requested": n_households,
        "gates": [g.as_dict() for g in gates],
        "gating_failures": ib.gating_failures(gates),
        "stop": None if stop is None else
                {"halt": stop.halt, "stage": stop.stage, "reason": stop.reason},
        "transient_batch_existed_in_memory_only": bool(transient_batch_in_memory),
        "transient_batch_serialized": False,
    })
    manifest = build_manifest(cfg, config_sha256, txn, status, diagnostics,
                              locals().get("binding_record"),
                              locals().get("environment"), env_x64=locals().get("env_x64"),
                              repro=locals().get("repro"),
                              records=locals().get("records"))

    atomic_write_json(diagnostics, txn.staging / "phase5_diagnostics.json")
    atomic_write_text("\n".join(console) + f"\nFINAL STATUS: {status}\n",
                      txn.staging / "phase5_console.log")
    manifest["artifact_hashes"] = {
        n: _sha256_file(txn.staging / n) for n in sorted(txn.staged_members())
        if n != MANIFEST_MEMBER}
    manifest["bundle_sha256"] = hashlib.sha256(
        "\n".join(f"{n}:{h}" for n, h in sorted(manifest["artifact_hashes"].items()))
        .encode("utf-8")).hexdigest()
    manifest["member_inventory"] = sorted(manifest["artifact_hashes"]) + [MANIFEST_MEMBER]
    atomic_write_json(manifest, txn.staging / MANIFEST_MEMBER)

    txn.enforce_allowlist()
    dest = txn.finish(status)
    txn.release()
    return RunOutcome(status=status, attempt_dir=dest, diagnostics=diagnostics,
                      manifest=manifest, console=console)


def write_aggregate_artifacts(staging: Path, result, cov, reg, table, pmap,
                              grade: str) -> List[ib.ArtifactRecord]:
    """Serialize the addendum s3 member set through the Increment-B serializers.

    Every write goes through `write_matrix` / `write_table` /
    `write_score_aggregate_summary`, which refuse row-level or id-paired content
    by construction. This function adds no write path of its own.
    """
    interior = list(pmap.interior_names)
    free = list(pmap.free_names)
    recs: List[ib.ArtifactRecord] = []

    recs.append(ib.write_score_aggregate_summary(staging, result,
                                                 inference_grade=grade))
    recs.append(ib.write_table(
        staging, "score_sum_free37.csv",
        pd.DataFrame({"name": free,
                      "score_sum": [float(v) for v in result.score_sum_free37]}),
        inference_grade=grade))
    for member, mat, names in (
            ("meat_free37.npy", result.meat_free37, free),
            ("meat_free37.csv", result.meat_free37, free),
            ("meat_interior35.npy", result.meat_interior35, interior),
            ("meat_interior35.csv", result.meat_interior35, interior),
            ("phase5_covariance_model.npy", cov.V_model, interior),
            ("phase5_covariance_model.csv", cov.V_model, interior),
            ("phase5_covariance_robust.npy", cov.V_robust, interior),
            ("phase5_covariance_robust.csv", cov.V_robust, interior),
            ("phase5_correlation_model.csv",
             ib.correlation_from_covariance(cov.V_model), interior),
            ("phase5_correlation_robust.csv",
             ib.correlation_from_covariance(cov.V_robust), interior),
            ("phase5_regional_covariance.csv", reg.V_RR_robust,
             list(ib.REGIONAL_BLOCK_NAMES))):
        recs.append(ib.write_matrix(staging, member, mat, names,
                                    inference_grade=grade))
    recs.append(ib.write_table(
        staging, "phase5_standard_errors.csv",
        pd.DataFrame({"name": interior,
                      "se_model": [float(v) for v in cov.se_model],
                      "se_robust": [float(v) for v in cov.se_robust],
                      "ratio_robust_model": [float(r / m) for r, m
                                             in zip(cov.se_robust, cov.se_model)]}),
        inference_grade=grade))
    recs.append(ib.write_table(staging, "phase5_parameter_table.csv", table.frame,
                               inference_grade=grade,
                               metadata=dict(table.metadata)))
    recs.append(ib.write_table(staging, "phase5_regional_tests.csv", reg.table,
                               inference_grade=grade,
                               metadata=dict(reg.metadata)))
    return recs


def build_manifest(cfg, config_sha256, txn, status, diagnostics, binding_record,
                   environment, *, env_x64, repro, records) -> Dict[str, Any]:
    return {
        "run": cfg["run"]["name"], "phase": 5, "mode": "dry-run-only",
        "attempt_id": txn.attempt_id, "status": status,
        "generated_at": _utcnow(),
        "real_run_supported": False,
        "creates_complete": False,
        "config": {"path": CONFIG_REL, "sha256": config_sha256},
        "accepted_binding": binding_record,
        "environment": environment,
        "float64_activation": env_x64,
        "reproduction": repro,
        "reproduction_tuple": dict(cfg["reproduction_tuple"]),
        "artifact_records": [r.as_dict() for r in (records or [])],
        "inference_grade": (records[0].inference_grade if records else None),
        "allowlist": list(ALLOWED_ARTIFACTS),
        "gating_failures": diagnostics.get("gating_failures", []),
        "stop": diagnostics.get("stop"),
        "transient_batch_existed_in_memory_only":
            diagnostics.get("transient_batch_existed_in_memory_only"),
        "transient_batch_serialized": False,
    }


# --------------------------------------------------------------------------- #
# 10. CLI -- the single entry point
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_p2a_phase5_inference",
        description="FR P2a Phase-5 inference DRY-RUN-ONLY runner (Increment C). "
                    "There is no real-run pathway.")
    p.add_argument("--out", default=None,
                   help="output root; required for any bounded-subset run")
    p.add_argument("--households", type=int, default=None,
                   help="bounded subset size; omit for the full population")
    p.add_argument("--no-reproduction", action="store_true",
                   help="skip the T-12S fresh-process reproduction")
    p.add_argument("--repro-json", action="store_true",
                   help="internal: re-stream and print the aggregate fingerprint")
    p.add_argument("--execute-dry-run", action="store_true",
                   help="request the authorized FULL-population dry run")
    p.add_argument("--expected-mnl-head", default=None)
    p.add_argument("--expected-dclaborsupply-head", default=None)
    p.add_argument("--approved-review", default=None)
    p.add_argument("--approved-review-sha256", default=None)
    p.add_argument("--inject-failure", default=None,
                   choices=["binding", "post_stream", "post_gates"],
                   help="test seam: raise a controlled StopRun at a named stage")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg, config_sha = load_config()

        if args.repro_json:
            activate_float64_or_refuse()
            result, _ = stream_aggregates(cfg, args.households)
            print(REPRO_BEGIN)
            print(json.dumps(aggregate_fingerprint(result), sort_keys=True))
            print(REPRO_END)
            return 0

        full = args.households is None or int(args.households) == int(
            cfg["population"]["n_households_full"])
        out_root = (Path(args.out) if args.out
                    else Path(MNL_ROOT) / cfg["run"]["output_root"])
        canonical = (Path(MNL_ROOT) / CANONICAL_OUTPUT_ROOT).resolve()

        if full:
            # the full-population dry run is a separately authorized step
            verify_dry_run_authorization(args, cfg)
        elif out_root.resolve() == canonical:
            raise StopRun("HP-AUTH", "output-root",
                          "a bounded subset may not be written into the canonical "
                          "production root; pass an explicit --out")

        outcome = execute_dry_run(
            cfg, config_sha, out_root=out_root, n_households=args.households,
            run_reproduction=not args.no_reproduction,
            inject_failure=args.inject_failure)
        print(f"FINAL STATUS: {outcome.status}")
        print(f"ATTEMPT: {outcome.attempt_dir}")
        return 0 if outcome.status == STATUS_COMPLETE else 3
    except StopRun as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
