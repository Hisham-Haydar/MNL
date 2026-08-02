"""FR P2a region-live Phase-5 — streaming household-score reducer (Increment A).

Governed by, in binding order:

  1. docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
  2. docs/France_case/P2a/FR_P2a_region_live_phase5_inference_design_v4.md
  3. docs/missions/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md (JMP)

WHAT THIS MODULE IS
-------------------
The Increment-A deliverable: a *streaming* reducer that walks the 1,555 P2a
singles households in canonical ``idhh``-ascending order, computes their
37-dimensional scores in bounded transient batches on the accepted per-group
likelihood route, and folds each batch into

    g_37  += sum_{i in b} s_i                      (37,)
    M_37  += S_b^T S_b                             (37, 37)
    M_35  += S_{b,I}^T S_{b,I}                     (35, 35)   I = interior selector
    digest = sha256( ... || idhh_i || s_i bytes || ... )      canonical order

and then releases the batch array. Addendum s2. The full ``(G, 37)`` score
matrix is never concatenated, never returned, and never written anywhere.

WHAT THIS MODULE IS NOT
-----------------------
It is not a runner, not a transaction, not a covariance builder. It performs no
I/O other than *reading* the accepted, authenticated inputs it is bound to. It
contains no write path of any kind: no ``open(..., "w")``, no ``np.save``, no
``to_csv``, no ``pickle``, no logging of array contents. Increment B (covariance
and inference objects) and Increment C (runner, transaction, reproduction) are
out of scope here and are not stubbed.

SCORE ROUTE (accepted, import-only)
-----------------------------------
``dclaborsupply.likelihood.engine_jax.build_jax_singles_ll(..., per_group=True)``
returns the ``(n_groups,)`` POSITIVE log-likelihood vector [design v4 s5.2,
audit s10]. The Phase-4 pin-fixed reparameterisation is reused verbatim:

    negll_free-style:  x_free (37,) -> base_full_47.at[free_idx].set(x_free)

so pins never enter differentiation [design v4 s5.1]. The score is

    s_g(x) = grad_x l_g(x)          l_g = positive per-group log-likelihood

obtained with ``jax.jacfwd`` over whole-household batches [design v4 s5.4
baseline]. Chunking by whole households is exact: ``l_g`` depends only on group
``g``'s rows (within-group log-sum-exp; within-choice-set proposal centering),
so no term couples households [design v4 s5.4].

CANONICAL ORDER
---------------
Order (b) of design v4 s6.3: ``idhh``-ascending across both genders, obtained by
a stable argsort of the concatenated loader group ids. The order is taken from
the ACTUAL loader group ids (``PrecomputedDataSingles.group_ids``), never from
a re-read of the frame.

DIGEST BYTE CONTRACT (fixed here, recorded in the result)
---------------------------------------------------------
Addendum s2 fixes the digest composition -- ``idhh canonical encoding || 37
float64 little-endian score values`` -- but not the integer encoding. This
module fixes it as:

    per household:  struct.pack("<q", int(idhh))        8 bytes, int64 LE
                    s_g.astype("<f8").tobytes()       296 bytes, 37 x float64 LE
    total                                             304 bytes / household

fed to a single running ``hashlib.sha256`` in canonical order. The constants are
published on the result object (``idhh_encoding``, ``dtype``, ``byte_order``,
``bytes_per_household``) so the addendum s3 ``score_aggregate_summary.json``
"dtype and byte-order contract" field is satisfiable without re-deriving them.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, NoReturn, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

MNL_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- #
# frozen contract constants (design v4 s3.3, s7.2; addendum s1)
# --------------------------------------------------------------------------- #
N_HOUSEHOLDS = 1555
N_FREE = 37
N_INTERIOR = 35
N_ALTERNATIVES = 101
ACTIVE_BOUND_NAMES: Tuple[str, ...] = ("beta_l_age2_sm", "beta_l_age2_sf")

SCORE_DTYPE = "float64"
SCORE_BYTE_ORDER = "little"
IDHH_ENCODING = "int64_le"
_IDHH_STRUCT = struct.Struct("<q")
_SCORE_ROW_DTYPE = np.dtype("<f8")
BYTES_PER_HOUSEHOLD = _IDHH_STRUCT.size + N_FREE * _SCORE_ROW_DTYPE.itemsize  # 304

# Fix A-2: the single canonical household-ID representation accepted at the
# reducer boundary. Native signed int64 -- the dtype `build_canonical_order`
# produces. `np.dtype('>i8') != np.dtype(np.int64)`, so this comparison also
# rejects non-native byte order.
_CANONICAL_ID_DTYPE = np.dtype(np.int64)
_INT64_MAX = int(np.iinfo(np.int64).max)
# beyond 2**53 a float64 no longer represents every integer exactly, so a
# float->int conversion above it cannot be certified loss-free
_FLOAT64_EXACT_INT_MAX = float(2 ** 53)

DEFAULT_BATCH_SIZE = 128

# accepted, committed inputs this module is bound to (MNL-repo-relative)
PARAMETER_MAP_CSV = "docs/France_case/P2a/phase5_parameter_map_v1.csv"
PHASE4_MANIFEST = ("outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/"
                   "complete/phase4_manifest.json")
PHASE3_RESULTS = ("outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/"
                  "complete/estimation_results.json")
CERTIFIED_SPEC_YAML = "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
CERTIFIED_SPEC_SHA256 = "492bcfa9c766bfcb5d8536f5e920cc0b00ffa600b7b89db60b250365f331f211"
ACCEPTED_THETA_SHA256 = "c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d"
FROZEN_STEM = "outputs/p2a_singles2016/region_live_v1/fr_p2a_singles2016_regionlive"


class ScoreStreamError(RuntimeError):
    """Streaming-contract violation.

    Messages carry shapes, counts, names, dtypes and canonical positions ONLY.
    No score value and no score byte is ever interpolated into a message:
    addendum s6 / T-23S forbids row-level scores reaching logs or exceptions.

    ``code`` is a short stable identifier (``SS-*``) so callers can branch on the
    failure class without parsing prose. Fix A-1.
    """

    def __init__(self, message: str, code: str = "SS-CONTRACT"):
        super().__init__(message)
        self.code = code


def _sanitize(exc: BaseException, boundary_code: str) -> ScoreStreamError:
    """Build the caller-visible error, detached from the failing object graph.

    Fix A-1 / review finding NP-1. The returned error is a NEW object whose
    ``__traceback__``, ``__cause__`` and ``__context__`` are all ``None``, so
    none of the frames that were live at the point of failure -- and therefore
    none of the transient ``(batch, 37)`` score arrays held in their locals --
    is reachable from what the caller receives.

    Message policy:

    * a `ScoreStreamError` message is authored by this module and is guaranteed
      value-free, so it is preserved verbatim;
    * a FOREIGN exception's message is suppressed and replaced by its type and
      the boundary code, because a third-party message (NumPy, JAX, pandas) may
      embed array contents. This trades some debuggability for the guarantee
      that no score value can reach a log or a failure report; the type name and
      boundary code are retained so the failure remains diagnosable.
    """
    if isinstance(exc, ScoreStreamError):
        clean = ScoreStreamError(str(exc), code=exc.code)
    else:
        clean = ScoreStreamError(
            f"[{boundary_code}] "
            f"{type(exc).__module__}.{type(exc).__name__} was raised inside the "
            "score stream; its message is suppressed because a foreign "
            "exception may embed array values (addendum s6). The exception type "
            "and this boundary code are the whole diagnostic surface.",
            code=boundary_code)
    clean.__traceback__ = None
    clean.__cause__ = None
    clean.__context__ = None
    clean.__suppress_context__ = True
    return clean


def _raise_clean(error: ScoreStreamError) -> NoReturn:
    """Raise ``error`` from a frame whose only local is the error itself.

    Fix A-1. Called only from OUTSIDE an ``except`` block, so Python attaches no
    implicit ``__context__``; the chaining fields are cleared immediately before
    the raise as well. The frame this adds to the traceback holds one name,
    ``error``, which is the exception itself -- never a score array.
    """
    error.__traceback__ = None
    error.__cause__ = None
    error.__context__ = None
    error.__suppress_context__ = True
    raise error


# --------------------------------------------------------------------------- #
# 1. authenticated parameter map (design v4 s7; T-17 fingerprints)
# --------------------------------------------------------------------------- #
def _sha256_text_lines(names: Sequence[str]) -> str:
    """T-17 fingerprint: SHA-256 of the newline-joined ordered names."""
    return hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class ParameterMap:
    """The 47 / 37 / 35 index spaces, established BY NAME from two agreeing
    committed sources (design v4 s7.1): ``phase5_parameter_map_v1.csv`` and
    ``phase4_manifest.json -> contract.parameter_map``.

    ``interior_positions_in_free`` is the ordered 35-interior selector ``I`` of
    addendum s2 -- positions within the free-37 vector, derived by name.
    """

    all_names: Tuple[str, ...]
    free_names: Tuple[str, ...]
    interior_names: Tuple[str, ...]
    pin_names: Tuple[str, ...]
    free_indices: Tuple[int, ...]
    pin_indices: Tuple[int, ...]
    pin_values: Tuple[float, ...]
    interior_positions_in_free: Tuple[int, ...]
    active_positions_in_free: Tuple[int, ...]
    free_names_sha256: str
    interior_names_sha256: str

    @property
    def free_index_array(self) -> np.ndarray:
        return np.asarray(self.free_indices, dtype=np.int64)

    @property
    def interior_selector(self) -> np.ndarray:
        return np.asarray(self.interior_positions_in_free, dtype=np.int64)


def load_parameter_map(repo_root: Path = MNL_ROOT) -> ParameterMap:
    """Load and cross-authenticate the parameter map.

    Every projection is by NAME (design v4 s7.2 / plan S-1). A positional
    derivation that happens to agree is rejected: the CSV free/interior indices
    are recomputed from names and asserted equal to the stored columns, and the
    CSV free-name sequence is asserted equal to the Phase-4 manifest's.
    """
    import json

    csv_path = repo_root / PARAMETER_MAP_CSV
    man_path = repo_root / PHASE4_MANIFEST
    df = pd.read_csv(csv_path)
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    pm = manifest["contract"]["parameter_map"]

    df = df.sort_values("full_index_0based", kind="mergesort").reset_index(drop=True)
    all_names = [str(n) for n in df["param"]]
    if list(pm["all_names"]) != all_names:
        raise ScoreStreamError(
            "parameter-map authentication failed: CSV all_names sequence differs "
            "from phase4_manifest.json contract.parameter_map.all_names")
    if len(all_names) != 47 or len(set(all_names)) != 47:
        raise ScoreStreamError(f"expected 47 unique parameter names, got {len(all_names)}")

    status = {str(n): str(s) for n, s in zip(df["param"], df["status"])}
    pin_names = [n for n in all_names if status[n] == "pinned"]
    free_names = [n for n in all_names if status[n] != "pinned"]
    interior_names = [n for n in free_names if status[n] == "interior"]
    active_names = [n for n in free_names if status[n] == "active_bound"]

    if list(pm["free_names"]) != free_names:
        raise ScoreStreamError(
            "parameter-map authentication failed: free-name sequence derived by "
            "status from the CSV differs from the Phase-4 manifest free_names")
    if list(pm["pin_names"]) != pin_names:
        raise ScoreStreamError(
            "parameter-map authentication failed: pin-name sequence differs from "
            "the Phase-4 manifest pin_names")
    if len(free_names) != N_FREE or len(interior_names) != N_INTERIOR:
        raise ScoreStreamError(
            f"expected {N_FREE} free / {N_INTERIOR} interior, got "
            f"{len(free_names)} / {len(interior_names)}")
    if tuple(active_names) != ACTIVE_BOUND_NAMES:
        raise ScoreStreamError(
            f"active-bound name set {tuple(active_names)} != accepted "
            f"{ACTIVE_BOUND_NAMES} (design v4 s3.3)")

    name_to_full = {n: i for i, n in enumerate(all_names)}
    free_indices = [name_to_full[n] for n in free_names]
    pin_indices = [name_to_full[n] for n in pin_names]
    if list(pm["free_indices"]) != free_indices or list(pm["pin_indices"]) != pin_indices:
        raise ScoreStreamError(
            "parameter-map authentication failed: name-derived free/pin index "
            "arrays differ from the Phase-4 manifest index arrays")

    # stored CSV positional columns must agree with the name-derived ones
    stored_free = df.loc[df["param"].isin(free_names), "free_index_0based"]
    if [int(v) for v in stored_free] != list(range(N_FREE)):
        raise ScoreStreamError(
            "parameter-map authentication failed: CSV free_index_0based column is "
            "not the 0..36 sequence in full-index order")
    stored_int = df.loc[df["param"].isin(interior_names), "interior_index_0based"]
    if [int(v) for v in stored_int] != list(range(N_INTERIOR)):
        raise ScoreStreamError(
            "parameter-map authentication failed: CSV interior_index_0based column "
            "is not the 0..34 sequence in full-index order")

    free_pos = {n: k for k, n in enumerate(free_names)}
    interior_positions = [free_pos[n] for n in interior_names]
    active_positions = [free_pos[n] for n in active_names]

    pin_value_map = {str(k): float(v) for k, v in pm["pin_values"].items()}
    pin_values = [pin_value_map[n] for n in pin_names]

    return ParameterMap(
        all_names=tuple(all_names),
        free_names=tuple(free_names),
        interior_names=tuple(interior_names),
        pin_names=tuple(pin_names),
        free_indices=tuple(free_indices),
        pin_indices=tuple(pin_indices),
        pin_values=tuple(pin_values),
        interior_positions_in_free=tuple(interior_positions),
        active_positions_in_free=tuple(active_positions),
        free_names_sha256=_sha256_text_lines(free_names),
        interior_names_sha256=_sha256_text_lines(interior_names),
    )


# --------------------------------------------------------------------------- #
# 2. canonical household iterator (design v4 s6.3 order (b))
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class HouseholdBatch:
    """One bounded, transient unit of work: whole households only."""

    position: int                # canonical position of the first household
    idhh: np.ndarray             # (n_b,) int64, strictly increasing
    is_male: np.ndarray          # (n_b,) bool, aligned with idhh

    @property
    def size(self) -> int:
        return int(self.idhh.size)


@dataclass(frozen=True)
class CanonicalOrder:
    """The canonical ``idhh``-ascending household order and its fingerprint.

    Built from the loader group ids of the two singles builders. The male and
    female id sets must be disjoint (one decision-maker per single household,
    design v4 s6.1) and the merged order strictly increasing (T-3).
    """

    idhh: np.ndarray             # (G,) int64 strictly increasing
    is_male: np.ndarray          # (G,) bool
    order_sha256: str

    @property
    def n_households(self) -> int:
        return int(self.idhh.size)

    def batches(self, batch_size: int) -> Iterator[HouseholdBatch]:
        if not isinstance(batch_size, (int, np.integer)) or int(batch_size) < 1:
            raise ScoreStreamError(f"batch_size must be a positive int, got {batch_size!r}")
        batch_size = int(batch_size)
        for start in range(0, self.n_households, batch_size):
            stop = min(start + batch_size, self.n_households)
            yield HouseholdBatch(position=start,
                                 idhh=self.idhh[start:stop].copy(),
                                 is_male=self.is_male[start:stop].copy())


def _require_canonical_ids(ids: Any, where: str) -> np.ndarray:
    """STRICT, LOSS-FREE gate on the canonical household-ID representation.

    Fix A-2 / review finding DG-1. The reducer boundary accepts exactly ONE
    representation -- the one `build_canonical_order` produces and
    `CanonicalOrder.batches` slices:

        a 1-D, C-contiguous, native-byte-order, signed ``int64`` numpy array.

    **No cast of any kind happens in this function**, so nothing can be
    truncated, wrapped or rounded before it has been validated. Every rejection
    class the design requires follows from the dtype gate alone, without a
    probing cast:

    * floating point -- *including numerically integral floats* such as `10.0`
      and forged fractional ones such as `10.5` -- is not ``int64``;
    * `NaN`, `+Inf`, `-Inf` and fractional values cannot exist in an ``int64``
      array, so they can only arrive under a rejected floating dtype;
    * magnitudes outside the signed-64-bit range cannot be represented in
      ``int64`` either, so they too can only arrive under a rejected dtype
      (``uint64``, ``object``, ``float64``);
    * ``object``, ``str``/``bytes``, ``bool``, ``complex``, unsigned and
      narrower/wider integer dtypes, and non-native byte order are each a dtype
      other than native ``int64`` and are rejected as non-canonical.

    Rejecting rather than coercing is the point: the published ``int64_le``
    digest contract is only meaningful if a non-canonical representation can
    never reach the hash.
    """
    if not isinstance(ids, np.ndarray):
        raise ScoreStreamError(
            f"[SS-IDTYPE] {where}: household identifiers must be a numpy array, "
            f"got {type(ids).__name__}", code="SS-IDTYPE")
    if ids.dtype != _CANONICAL_ID_DTYPE:
        raise ScoreStreamError(
            f"[SS-IDDTYPE] {where}: household identifiers have dtype "
            f"'{ids.dtype.str}', which is not the canonical production "
            f"representation '{_CANONICAL_ID_DTYPE.str}' (native signed int64). "
            "No coercion is attempted: a non-canonical representation is "
            f"rejected, never cast, so the {IDHH_ENCODING} digest encoding "
            "cannot be fed a truncated or rounded identifier",
            code="SS-IDDTYPE")
    if ids.ndim != 1:
        raise ScoreStreamError(
            f"[SS-IDSHAPE] {where}: household identifiers must be 1-D, got "
            f"{ids.ndim}-D with shape {ids.shape}", code="SS-IDSHAPE")
    if not ids.flags["C_CONTIGUOUS"]:
        raise ScoreStreamError(
            f"[SS-IDLAYOUT] {where}: household identifiers must be C-contiguous",
            code="SS-IDLAYOUT")
    return ids


def _loader_ids_to_canonical(values: Any, tag: str) -> np.ndarray:
    """Convert LOADER group ids to the canonical representation, loss-free.

    Fix A-2. This is the one place a conversion is permitted, because the
    package loader is free to hand back whatever integer or float dtype the
    frozen stem carries. Every check runs on the ORIGINAL dtype *before* any
    cast, so a value is never truncated or wrapped and then inspected
    afterwards -- the defect the previous `_as_int64_ids` contained.

    Everything downstream of this function -- `CanonicalOrder`,
    `HouseholdBatch`, the reducer boundary -- is strict native ``int64`` and is
    policed by `_require_canonical_ids`.
    """
    arr = np.asarray(values)
    if arr.ndim != 1:
        raise ScoreStreamError(
            f"[SS-IDSHAPE] {tag}: loader group ids must be 1-D, got shape {arr.shape}",
            code="SS-IDSHAPE")
    kind = arr.dtype.kind
    if arr.dtype == _CANONICAL_ID_DTYPE:
        return np.ascontiguousarray(arr)
    if kind == "i":
        # any signed integer dtype (incl. non-native byte order) widens exactly
        return np.ascontiguousarray(arr.astype(np.int64))
    if kind == "u":
        if arr.size and int(arr.max()) > _INT64_MAX:
            raise ScoreStreamError(
                f"[SS-IDRANGE] {tag}: unsigned loader group id exceeds the signed "
                f"64-bit maximum {_INT64_MAX}; it cannot be encoded as int64_le",
                code="SS-IDRANGE")
        return np.ascontiguousarray(arr.astype(np.int64))
    if kind == "f":
        if not np.isfinite(arr).all():
            raise ScoreStreamError(
                f"[SS-IDNONFINITE] {tag}: non-finite loader group id present",
                code="SS-IDNONFINITE")
        if not np.array_equal(arr, np.trunc(arr)):
            raise ScoreStreamError(
                f"[SS-IDFRACTIONAL] {tag}: loader group ids are not integral; the "
                f"{IDHH_ENCODING} digest encoding is undefined for them",
                code="SS-IDFRACTIONAL")
        if arr.size and float(np.max(np.abs(arr))) > _FLOAT64_EXACT_INT_MAX:
            raise ScoreStreamError(
                f"[SS-IDRANGE] {tag}: loader group id magnitude exceeds "
                f"{_FLOAT64_EXACT_INT_MAX} (2**53), beyond which a float64 no "
                "longer represents every integer exactly, so the conversion "
                "cannot be certified loss-free",
                code="SS-IDRANGE")
        return np.ascontiguousarray(arr.astype(np.int64))
    raise ScoreStreamError(
        f"[SS-IDDTYPE] {tag}: loader group ids have unsupported dtype "
        f"'{arr.dtype.str}' (kind '{kind}'); only signed/unsigned integer and "
        "exactly-integral float64 representations can be converted to the "
        "canonical int64 identifier",
        code="SS-IDDTYPE")


def build_canonical_order(male_group_ids: np.ndarray,
                          female_group_ids: np.ndarray) -> CanonicalOrder:
    """Design v4 s6.3 order (b): stable argsort of the concatenated group ids.

    Also enforces the T-3 fragment that Increment A owns: strictly increasing,
    elementwise equal to ``np.sort(np.unique(idhh))``, every household once.

    Fix A-2: the loader's own dtype is converted here, once, by the loss-free
    `_loader_ids_to_canonical`. Everything the conversion produces -- and
    therefore every `HouseholdBatch` sliced from it -- is strict native int64,
    which is what `_require_canonical_ids` demands at the reducer boundary.
    """
    m = _loader_ids_to_canonical(male_group_ids, "male loader group_ids")
    f = _loader_ids_to_canonical(female_group_ids, "female loader group_ids")
    merged = np.concatenate([m, f])
    is_male = np.concatenate([np.ones(m.size, dtype=bool), np.zeros(f.size, dtype=bool)])
    perm = np.argsort(merged, kind="stable")
    idhh = merged[perm]
    is_male = is_male[perm]

    if idhh.size and not np.all(np.diff(idhh) > 0):
        raise ScoreStreamError(
            "canonical order is not strictly increasing: the male and female "
            "loader group-id sets are not disjoint or contain duplicates")
    if not np.array_equal(idhh, np.sort(np.unique(merged))):
        raise ScoreStreamError(
            "canonical order != np.sort(np.unique(idhh)) (T-3)")

    fingerprint = hashlib.sha256(
        "\n".join(str(int(v)) for v in idhh).encode("utf-8")).hexdigest()
    idhh.flags.writeable = False
    is_male.flags.writeable = False
    return CanonicalOrder(idhh=idhh, is_male=is_male, order_sha256=fingerprint)


# --------------------------------------------------------------------------- #
# 3. streaming reducer (addendum s2)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ScoreStreamResult:
    """Aggregate-only output. Carries no row-level score, by construction."""

    n_households: int
    dim_free: int
    dim_interior: int
    score_sum_free37: np.ndarray
    meat_free37: np.ndarray
    meat_interior35: np.ndarray
    score_stream_sha256: str
    order_sha256: str
    free_names_sha256: str
    interior_names_sha256: str
    batch_size: int
    n_batches: int
    dtype: str = SCORE_DTYPE
    byte_order: str = SCORE_BYTE_ORDER
    idhh_encoding: str = IDHH_ENCODING
    bytes_per_household: int = BYTES_PER_HOUSEHOLD
    diagnostics: Dict[str, float] = field(default_factory=dict)


class ScoreStreamReducer:
    """Running accumulators + the global canonical score-stream digest.

    ``update`` is the only entry point. It validates the batch against the
    canonical order, folds it into the accumulators, hashes it into the running
    digest, and returns None -- it never stores, returns or re-emits ``S_b``.
    """

    def __init__(self, pmap: ParameterMap, order: CanonicalOrder, *, batch_size: int):
        self._pmap = pmap
        self._order = order
        self._batch_size = int(batch_size)
        self._interior = pmap.interior_selector
        self._digest = hashlib.sha256()
        self._g37 = np.zeros(N_FREE, dtype=np.float64)
        self._m37 = np.zeros((N_FREE, N_FREE), dtype=np.float64)
        self._m35 = np.zeros((N_INTERIOR, N_INTERIOR), dtype=np.float64)
        self._cursor = 0
        self._n_batches = 0
        self._max_abs_score = 0.0
        self._closed = False
        self._failed = False          # Fix A-1: poisoned after any failed batch

    # -- validation ------------------------------------------------------- #
    def _check_batch(self, batch: HouseholdBatch, scores: np.ndarray) -> None:
        if self._closed:
            raise ScoreStreamError(
                "[SS-STATE] reducer already finalized; update() after result()",
                code="SS-STATE")
        if self._failed:
            raise ScoreStreamError(
                "[SS-POISONED] reducer already recorded a failed batch; its "
                "accumulators and digest are no longer a valid stream",
                code="SS-POISONED")
        # Fix A-2: the identifier representation is gated FIRST and without any
        # cast, so a forged non-canonical batch can never reach the digest.
        _require_canonical_ids(
            batch.idhh, f"batch at canonical position {self._cursor}")
        if batch.position != self._cursor:
            raise ScoreStreamError(
                f"[SS-ORDER] out-of-order batch: expected canonical position "
                f"{self._cursor}, got {batch.position}", code="SS-ORDER")
        stop = self._cursor + batch.size
        if stop > self._order.n_households:
            raise ScoreStreamError(
                f"[SS-OVERRUN] batch overruns the canonical order: positions "
                f"[{self._cursor}, {stop}) but only "
                f"{self._order.n_households} households exist", code="SS-OVERRUN")
        expected = self._order.idhh[self._cursor:stop]
        # no .astype here: the strict gate above already guarantees int64
        if not np.array_equal(batch.idhh, expected):
            raise ScoreStreamError(
                f"[SS-IDMATCH] batch identifiers do not match the canonical order "
                f"at positions [{self._cursor}, {stop})", code="SS-IDMATCH")
        if batch.size and not np.all(np.diff(batch.idhh) > 0):
            raise ScoreStreamError(
                f"[SS-IDORDER] batch identifiers are not strictly increasing at "
                f"position {self._cursor}", code="SS-IDORDER")
        if not isinstance(scores, np.ndarray):
            raise ScoreStreamError(
                f"[SS-TYPE] batch scores must be a numpy array, got "
                f"{type(scores).__name__}", code="SS-TYPE")
        if scores.shape != (batch.size, N_FREE):
            raise ScoreStreamError(
                f"[SS-SHAPE] corrupted batch at position {self._cursor}: score "
                f"shape {scores.shape} != {(batch.size, N_FREE)}", code="SS-SHAPE")
        if scores.dtype != np.float64:
            raise ScoreStreamError(
                f"[SS-DTYPE] corrupted batch at position {self._cursor}: score "
                f"dtype {scores.dtype} != float64", code="SS-DTYPE")
        if not np.isfinite(scores).all():
            n_bad = int((~np.isfinite(scores)).sum())
            raise ScoreStreamError(
                f"[SS-NONFINITE] non-finite score entries in batch at position "
                f"{self._cursor}: {n_bad} of {scores.size} entries are not finite",
                code="SS-NONFINITE")

    # -- streaming update -------------------------------------------------- #
    def update(self, batch: HouseholdBatch, scores: np.ndarray) -> None:
        """Fold one transient batch. ``scores`` is (n_b, 37) float64.

        The array is read, never retained: the reducer keeps no reference to it
        after this call returns (addendum s2 "the batch score array must be
        released").

        Fix A-1: this is a sanitized public failure boundary. Any exception
        raised inside is replaced by a detached `ScoreStreamError` and this
        frame's reference to ``scores`` is dropped BEFORE the raise, so the
        caller-visible exception graph -- traceback frames, ``__cause__``,
        ``__context__`` and payloads -- cannot reach the transient score array.
        """
        failure = None
        try:
            self._check_batch(batch, scores)
            self._accumulate(batch, scores)
        except Exception as exc:                      # sanitized immediately below
            self._failed = True
            failure = _sanitize(exc, "SS-UPDATE")
        finally:
            # drop THIS frame's binding whether or not the fold succeeded, so the
            # traceback frame appended by the raise below carries no score array.
            # `del` removes the name from the frame entirely, not merely rebinds it.
            del scores
        if failure is not None:
            _raise_clean(failure)

    def _accumulate(self, batch: HouseholdBatch, scores: np.ndarray) -> None:
        """Fold a validated batch. Internal: never a public failure boundary."""
        block = np.ascontiguousarray(scores, dtype=np.float64)
        self._g37 += block.sum(axis=0)
        self._m37 += block.T @ block
        interior = block[:, self._interior]
        self._m35 += interior.T @ interior
        m = float(np.max(np.abs(block))) if block.size else 0.0
        if m > self._max_abs_score:
            self._max_abs_score = m

        # global canonical score-stream digest, computed INSIDE the stream
        le_block = block.astype(_SCORE_ROW_DTYPE, copy=False)
        pack = _IDHH_STRUCT.pack
        digest = self._digest
        for k in range(batch.size):
            digest.update(pack(int(batch.idhh[k])))
            digest.update(le_block[k].tobytes())

        self._cursor += batch.size
        self._n_batches += 1
        # release every local view onto the batch before returning
        del block, interior, le_block, digest

    # -- finalisation ------------------------------------------------------ #
    def result(self) -> ScoreStreamResult:
        # Fix A-1: a reducer that recorded a failed batch can never produce a
        # result -- partial accumulators and a partial digest are not a stream.
        if self._failed:
            _raise_clean(ScoreStreamError(
                "[SS-POISONED] the reducer recorded a failed batch; its "
                "accumulators and digest are not a valid stream result",
                code="SS-POISONED"))
        if self._cursor != self._order.n_households:
            _raise_clean(ScoreStreamError(
                f"[SS-INCOMPLETE] incomplete stream: {self._cursor} of "
                f"{self._order.n_households} households consumed",
                code="SS-INCOMPLETE"))
        self._closed = True
        g = self._g37.copy()
        m37 = self._m37.copy()
        m35 = self._m35.copy()
        diagnostics = {
            "score_sum_max_abs": float(np.max(np.abs(g))) if g.size else 0.0,
            "score_sum_l2": float(np.linalg.norm(g)),
            "meat_free37_trace": float(np.trace(m37)),
            "meat_interior35_trace": float(np.trace(m35)),
            "meat_free37_max_asymmetry": float(np.max(np.abs(m37 - m37.T))),
            "meat_interior35_max_asymmetry": float(np.max(np.abs(m35 - m35.T))),
            "max_abs_score_entry": float(self._max_abs_score),
        }
        return ScoreStreamResult(
            n_households=int(self._cursor),
            dim_free=N_FREE,
            dim_interior=N_INTERIOR,
            score_sum_free37=g,
            meat_free37=m37,
            meat_interior35=m35,
            score_stream_sha256=self._digest.hexdigest(),
            order_sha256=self._order.order_sha256,
            free_names_sha256=self._pmap.free_names_sha256,
            interior_names_sha256=self._pmap.interior_names_sha256,
            batch_size=self._batch_size,
            n_batches=self._n_batches,
            diagnostics=diagnostics,
        )


# --------------------------------------------------------------------------- #
# 4. production likelihood binding (accepted route, import-only)
# --------------------------------------------------------------------------- #
@dataclass
class LikelihoodBinding:
    """Everything the batch evaluator needs, bound to the accepted sources.

    ``household_limit`` is the ONLY subsetting knob: it truncates the canonical
    order to its first ``k`` households. Nothing else about the evaluator, the
    loader or the reducer is parameterised (charter s5).
    """

    spec: Any
    metadata: Dict[str, Any]
    male_frame: pd.DataFrame
    female_frame: pd.DataFrame
    pmap: ParameterMap
    theta_hat_full: np.ndarray          # (47,)
    x_hat_free: np.ndarray              # (37,)
    base_full: np.ndarray               # (47,) pins at pin values, free zeroed
    order: CanonicalOrder
    full_order: CanonicalOrder
    household_limit: Optional[int]
    spec_sha256: str
    theta_hat_sha256: str


def _theta_sha256(theta: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(theta, dtype=np.float64).tobytes()).hexdigest()


def build_production_binding(*, repo_root: Path = MNL_ROOT,
                             household_limit: Optional[int] = None,
                             authenticate: bool = True) -> LikelihoodBinding:
    """Bind to the accepted P2a singles-2016 sources through the REAL loader.

    Reads (never writes): the certified spec YAML, the frozen stem parquet and
    its ``__mnlmeta.json``, the accepted 47-vector from the Phase-3 bundle, and
    the authenticated parameter map. Runs ``dclaborsupply.data.loader.
    load_singles`` on both genders to obtain the loader group order.
    """
    import json

    from dclaborsupply import EstimationSpec
    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood import engine_jax

    # float64 is source-established at engine_jax._load_jax(), "before every array
    # creation on the accepted route" [design v4 s3.3, audit s17]. That helper is
    # invoked lazily by the first builder call, which makes the guarantee depend on
    # call ordering: a caller that materialises a jnp array before the first
    # build_jax_singles_ll() would silently get float32. Trigger the accepted
    # initialiser EAGERLY here so the binding, not the ordering, carries the
    # contract. The package is read-only and unmodified: this only calls it.
    engine_jax._load_jax()
    import jax

    if jax.config.read("jax_enable_x64") is not True:
        raise ScoreStreamError(
            "jax_enable_x64 is not active after the accepted float64 initialiser; "
            "the float64 score contract cannot be honoured")

    repo_root = Path(repo_root)
    spec_path = repo_root / CERTIFIED_SPEC_YAML
    spec_sha = _sha256_file(spec_path)
    if authenticate and spec_sha != CERTIFIED_SPEC_SHA256:
        raise ScoreStreamError(
            f"certified spec YAML sha256 {spec_sha} != accepted {CERTIFIED_SPEC_SHA256}")
    spec = EstimationSpec.from_yaml(str(spec_path))

    pmap = load_parameter_map(repo_root)
    if list(spec.all_param_names) != list(pmap.all_names):
        raise ScoreStreamError(
            "certified spec all_param_names differs from the authenticated "
            "parameter-map name sequence")

    results = json.loads((repo_root / PHASE3_RESULTS).read_text(encoding="utf-8"))
    theta_hat = np.asarray(results["results"]["joint"]["theta"], dtype=np.float64)
    if theta_hat.shape != (47,):
        raise ScoreStreamError(f"accepted theta shape {theta_hat.shape} != (47,)")
    theta_sha = _theta_sha256(theta_hat)
    if authenticate and theta_sha != ACCEPTED_THETA_SHA256:
        raise ScoreStreamError(
            f"accepted theta sha256 {theta_sha} != accepted {ACCEPTED_THETA_SHA256}")

    free_idx = pmap.free_index_array
    pin_idx = np.asarray(pmap.pin_indices, dtype=np.int64)
    pin_vals = np.asarray(pmap.pin_values, dtype=np.float64)
    if not all(np.float64(theta_hat[pin_idx[k]]).tobytes() == np.float64(pin_vals[k]).tobytes()
               for k in range(pin_idx.size)):
        raise ScoreStreamError(
            "accepted theta pins are not bitwise identical to the accepted pin values")
    x_hat_free = theta_hat[free_idx].copy()
    base_full = np.zeros(47, dtype=np.float64)
    base_full[pin_idx] = pin_vals

    parquet = repo_root / f"{FROZEN_STEM}__singles.parquet"
    meta_path = repo_root / f"{FROZEN_STEM}__mnlmeta.json"
    frame = pd.read_parquet(parquet)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    male_frame = frame[pd.to_numeric(frame["dgn"]) == 1].reset_index(drop=True)
    female_frame = frame[pd.to_numeric(frame["dgn"]) == 0].reset_index(drop=True)

    dm = load_singles(male_frame.copy(), spec, is_male=True, metadata=metadata)
    df_ = load_singles(female_frame.copy(), spec, is_male=False, metadata=metadata)
    full_order = build_canonical_order(dm.group_ids, df_.group_ids)

    if authenticate and full_order.n_households != N_HOUSEHOLDS:
        raise ScoreStreamError(
            f"loader yields {full_order.n_households} households != accepted {N_HOUSEHOLDS}")

    order = full_order
    if household_limit is not None:
        k = int(household_limit)
        if k < 1 or k > full_order.n_households:
            raise ScoreStreamError(
                f"household_limit {k} outside [1, {full_order.n_households}]")
        idhh = full_order.idhh[:k].copy()
        is_male = full_order.is_male[:k].copy()
        fp = hashlib.sha256("\n".join(str(int(v)) for v in idhh).encode("utf-8")).hexdigest()
        idhh.flags.writeable = False
        is_male.flags.writeable = False
        order = CanonicalOrder(idhh=idhh, is_male=is_male, order_sha256=fp)

    return LikelihoodBinding(
        spec=spec, metadata=metadata,
        male_frame=male_frame, female_frame=female_frame,
        pmap=pmap, theta_hat_full=theta_hat, x_hat_free=x_hat_free,
        base_full=base_full, order=order, full_order=full_order,
        household_limit=household_limit,
        spec_sha256=spec_sha, theta_hat_sha256=theta_sha)


# --------------------------------------------------------------------------- #
# 5. bounded batch score computation (design v4 s5.4 baseline: jacfwd)
# --------------------------------------------------------------------------- #
def _gender_score_block(binding: LikelihoodBinding, ids: np.ndarray,
                        is_male: bool, *, mode: str) -> np.ndarray:
    """Scores for one gender's households of one batch, in ``idhh``-ascending order.

    Slices the production frame to whole households, runs the REAL loader on the
    slice, builds the accepted per-group likelihood on it, and differentiates the
    pin-fixed free-37 reparameterisation. Chunking by whole households is exact
    (design v4 s5.4).
    """
    import jax
    import jax.numpy as jnp

    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll

    if ids.size == 0:
        return np.zeros((0, N_FREE), dtype=np.float64)

    frame = binding.male_frame if is_male else binding.female_frame
    sub = frame[pd.to_numeric(frame["idhh"]).isin(set(int(v) for v in ids))].copy()
    sub = sub.reset_index(drop=True)
    expected_rows = int(ids.size) * N_ALTERNATIVES
    if len(sub) != expected_rows:
        raise ScoreStreamError(
            f"household slice has {len(sub)} rows != {expected_rows} "
            f"({ids.size} households x {N_ALTERNATIVES} alternatives)")

    data = load_singles(sub, binding.spec, is_male=is_male, metadata=binding.metadata)
    loaded_ids = _loader_ids_to_canonical(data.group_ids, "batch loader group_ids")
    if not np.array_equal(loaded_ids, np.sort(ids)):
        raise ScoreStreamError(
            "batch loader group order does not match the requested household set")

    ll_vec, _ = build_jax_singles_ll(data, binding.spec, is_male=is_male, per_group=True)
    free_idx = jnp.asarray(binding.pmap.free_index_array)
    base_full = jnp.asarray(binding.base_full)

    def per_group_free(x_free):
        return ll_vec(base_full.at[free_idx].set(x_free))

    if mode == "jacfwd":
        jac = jax.jacfwd(per_group_free)
    elif mode == "jacrev":
        jac = jax.jacrev(per_group_free)
    else:
        raise ScoreStreamError(f"unknown derivative mode {mode!r}")

    raw = jac(jnp.asarray(binding.x_hat_free))
    # T-15 / design v4 s3.3: float64 is established by engine_jax._load_jax()
    # before any array creation on the accepted route. Check the RAW device dtype
    # -- np.asarray(..., dtype=float64) below would silently upcast a float32
    # result and hide the loss, and the digest byte contract is float64-specific.
    if np.dtype(raw.dtype) != np.dtype(np.float64):
        raise ScoreStreamError(
            f"derivative route returned dtype {raw.dtype} != float64: "
            "jax_enable_x64 is not active on the accepted route")
    block = np.asarray(raw, dtype=np.float64)
    if block.shape != (ids.size, N_FREE):
        raise ScoreStreamError(
            f"gender score block shape {block.shape} != {(ids.size, N_FREE)}")
    return np.ascontiguousarray(block)


def compute_batch_scores(binding: LikelihoodBinding, batch: HouseholdBatch, *,
                         mode: str = "jacfwd") -> np.ndarray:
    """Bounded, transient ``(n_b, 37)`` float64 score block in canonical order.

    ``mode`` selects the AD direction on the SAME accepted likelihood route:
    ``jacfwd`` is the design v4 s5.4 baseline; ``jacrev`` exists so the T-16
    cross-mode check has an independent reference. Both differentiate the exact
    same production object -- neither replaces the evaluator.

    Fix A-1: sanitized public failure boundary. `_gender_score_block` holds
    partial score arrays in its frame locals, so any exception escaping from it
    is replaced by a detached error carrying no traceback.
    """
    failure = None
    try:
        return _compute_batch_scores(binding, batch, mode)
    except Exception as exc:                          # sanitized immediately below
        failure = _sanitize(exc, "SS-EVAL")
    _raise_clean(failure)


def _compute_batch_scores(binding: LikelihoodBinding, batch: HouseholdBatch,
                          mode: str) -> np.ndarray:
    """Internal evaluator. Not a public failure boundary."""
    male_ids = batch.idhh[batch.is_male]
    female_ids = batch.idhh[~batch.is_male]
    male_block = _gender_score_block(binding, male_ids, True, mode=mode)
    female_block = _gender_score_block(binding, female_ids, False, mode=mode)

    out = np.empty((batch.size, N_FREE), dtype=np.float64)
    male_pos = np.flatnonzero(batch.is_male)
    female_pos = np.flatnonzero(~batch.is_male)
    # each gender block is idhh-ascending; the batch positions of that gender are
    # idhh-ascending too, so the assignment is order-preserving
    out[male_pos] = male_block
    out[female_pos] = female_block
    return out


# --------------------------------------------------------------------------- #
# 6. the stream (addendum s2) -- the only orchestration Increment A owns
# --------------------------------------------------------------------------- #
def run_score_stream(binding: LikelihoodBinding, *,
                     batch_size: int = DEFAULT_BATCH_SIZE,
                     mode: str = "jacfwd") -> ScoreStreamResult:
    """Walk the canonical order in bounded batches and return aggregates only.

    No score row survives an iteration: each batch block is folded into the
    accumulators and the digest, then dropped. Nothing is written to disk.

    Fix A-1: sanitized public failure boundary. The ``finally`` clause releases
    this frame's ``block`` binding during unwinding -- i.e. BEFORE the exception
    leaves the frame -- so the traceback the caller receives cannot reach the
    transient score array through this frame either.
    """
    reducer = ScoreStreamReducer(binding.pmap, binding.order, batch_size=batch_size)
    for batch in binding.order.batches(batch_size):
        failure = None
        block = None
        try:
            block = compute_batch_scores(binding, batch, mode=mode)
            reducer.update(batch, block)
        except Exception as exc:                  # sanitized immediately below
            failure = _sanitize(exc, "SS-STREAM")
        finally:
            del block                   # release the transient batch (addendum s2)
        if failure is not None:
            _raise_clean(failure)
    return reducer.result()


__all__ = [
    "ACTIVE_BOUND_NAMES",
    "BYTES_PER_HOUSEHOLD",
    "CanonicalOrder",
    "DEFAULT_BATCH_SIZE",
    "HouseholdBatch",
    "IDHH_ENCODING",
    "LikelihoodBinding",
    "MNL_ROOT",
    "N_ALTERNATIVES",
    "N_FREE",
    "N_HOUSEHOLDS",
    "N_INTERIOR",
    "ParameterMap",
    "SCORE_BYTE_ORDER",
    "SCORE_DTYPE",
    "ScoreStreamError",
    "ScoreStreamReducer",
    "ScoreStreamResult",
    "build_canonical_order",
    "build_production_binding",
    "compute_batch_scores",
    "load_parameter_map",
    "run_score_stream",
]
