"""FR P2a region-live Phase-5 — covariance and inference objects (Increment B).

Governed by, in binding order:

  1. docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
  2. docs/France_case/P2a/FR_P2a_region_live_phase5_inference_design_v4.md
  3. docs/missions/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md (JMP)

WHAT THIS MODULE IS
-------------------
The Increment-B deliverable: **pure functions** that turn the Increment-A
streamed aggregates -- the 37-score sum, `M_37` and `M_35` -- plus the accepted
Phase-3/Phase-4 artifacts into

  * the authenticated bread `H_II` (35x35), loaded and symmetrised, never recomputed;
  * the model-based covariance `V_model = H_II^-1`;
  * the corrected robust conditional-35 sandwich `V_robust = c * H_II^-1 M_35 H_II^-1`;
  * the exact 13-column 47-row parameter table of design v4 s17.3;
  * the regional Wald battery H0-A / H0-B / H0-C / H0-G, model and robust;
  * every design-v4 T/W gate computable at this layer, as checkable functions;
  * serializers for the addendum s3 aggregate artifact set.

Nothing here holds state, orchestrates, or writes except through the explicit
serializers in section 8.

WHAT THIS MODULE IS NOT
-----------------------
Not a runner, transaction, staging directory, manifest, console log, lock, or
reproduction gate -- those are Increment C. It performs no optimisation, no
Hessian evaluation, no score evaluation, and no full-population run. It never
persists a row-level score: the serializers refuse household-scale content by
construction (section 8).

SIGN AND SCALE CONVENTIONS (design v4 s5.3, s8.2)
------------------------------------------------
`H` is the Hessian of negLL, positive definite. `M` is an outer-product meat and
is invariant to the score's sign. `negLL` is an unweighted SUM over households,
so `H` is already at sum scale and `H^-1` carries the `1/G` implicitly: **no
sample scaling is applied at any point**. Every inverse-like operation is a
Cholesky factorisation solve -- never `numpy.linalg.inv`.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

MNL_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- #
# 1. frozen contract constants (design v4 s3.2, s3.3, s10, s15, s16)
# --------------------------------------------------------------------------- #
N_FULL = 47
N_FREE = 37
N_INTERIOR = 35
N_REGIONAL = 10
N_HOUSEHOLDS = 1555

# design v4 s3.3 / s7.2: the two active-bound coordinates, at free positions
# {2, 6}, both at their UPPER bound 1.0. Named here so T-22 can validate the
# exact active set rather than trusting whatever mapping a caller supplies.
ACTIVE_BOUND_NAMES: Tuple[str, ...] = ("beta_l_age2_sm", "beta_l_age2_sf")

# accepted artifacts
PHASE4_BREAD_NPY = ("outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/"
                    "complete/hessian_free.npy")
PHASE4_DIAGNOSTICS = ("outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/"
                      "complete/phase4_diagnostics.json")
PHASE4_MANIFEST = ("outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/"
                   "complete/phase4_manifest.json")
PHASE3_RESULTS = ("outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/"
                  "complete/estimation_results.json")
BREAD_SHA256 = "e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061"
# design v4 s15 T-5: the accepted theta-BYTE hash is part of bread provenance
ACCEPTED_THETA_SHA256 = "c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d"
PHASE3_BUNDLE_SHA256 = "2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b"
PHASE4_BUNDLE_SHA256 = "5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3"

# design v4 s16.1 -- reused certified tolerances
HESSIAN_SYMMETRY_THRESHOLD = 2.3588019878151842e-4   # T-6, Phase-4 recorded
RANK_TOLERANCE_REL = 1e-10                           # x max_eig
SOLVE_VS_PINV_ATOL = 1e-8                            # T-8
PHASE4_MIN_EIG = 0.1037326963880782                  # T-6 agreement anchor
PHASE4_MAX_EIG = 42048.457934380494
PHASE4_CONDITION_NUMBER = 405353.94719781954
PHASE4_EIGEN_RTOL = 1e-10

# design v4 s16.2 -- new tolerances
KAPPA_BE_CERTIFIED = 6.0424e-12       # T-7 meat PSD, upward-rounded K*gamma_G
COVARIANCE_PSD_REL = 1e-10            # T-9, equal to the rank convention
SYMMETRY_REL = 1e-12                  # T-7 / T-9 accumulated-matrix symmetry
STATIONARITY_SE_FRACTION = 0.05       # T-19
KKT_ACTIVITY_FACTOR = 100.0           # T-22
CORRELATION_BOUND = 1.0 + 1e-10       # T-18
Z_975 = 1.959963984540054             # W-4, s10.5
W1_RATIO_RANGE = (0.2, 5.0)           # W-1

# design v4 s10.1 -- the finite-sample correction, telescoped
CORRECTION_G = N_HOUSEHOLDS
CORRECTION_N = N_HOUSEHOLDS
CORRECTION_K = N_INTERIOR
CORRECTION_C = 1555.0 / 1520.0        # = [G/(G-1)] * [(N-1)/(N-K)] = G/(G-K)

# design v4 s10.5 / s13.4 -- frozen critical values
CHI2_CRIT_95 = {10: 18.307038053275146, 7: 14.067140449340169,
                2: 5.991464547107979, 1: 3.841458820694124}

# design v4 s13.4 -- the four pre-registered nulls, rows keyed BY NAME
REGIONAL_BLOCK_NAMES: Tuple[str, ...] = (
    "beta_E_gsur", "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4",
    "beta_E_drgn5", "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
    "beta_E_drgur", "beta_E_drgmd")
NULL_DEFINITIONS: Tuple[Tuple[str, Tuple[str, ...], str], ...] = (
    ("H0-A", REGIONAL_BLOCK_NAMES, "confirmatory"),
    ("H0-B", ("beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4", "beta_E_drgn5",
              "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8"), "secondary"),
    ("H0-C", ("beta_E_drgur", "beta_E_drgmd"), "secondary"),
    ("H0-G", ("beta_E_gsur",), "secondary"),
)

# design v4 s17.3 -- the exact 13-column schema, in this order
PARAMETER_TABLE_COLUMNS: Tuple[str, ...] = (
    "name", "block", "status", "estimate", "bound_value", "bound_side",
    "grad_negll", "multiplier", "se_model", "se_robust",
    "ratio_robust_model", "z", "p")
INFERENTIAL_COLUMNS: Tuple[str, ...] = (
    "se_model", "se_robust", "ratio_robust_model", "z", "p")
NA = "NA"
STATUS_VALUES = frozenset({"interior", "active-bound", "pinned"})

# design v4 s12.4 -- the mandatory footnote, verbatim
PIN_TABLE_FOOTNOTE = (
    "Ten coordinates are pinned run-overlay restrictions, not estimates. All ten "
    "are structurally inapplicable to a 2016 singles sample and carry exactly "
    "zero gradient for structural reasons; standard errors are undefined, not "
    "zero. The specification's genuine normalisations — beta_c = 1.0, couples "
    "theta_c = 0.0, theta_l_m = −0.8, and the removed beta_ll — lie outside the "
    "47-vector and outside this table; theta_l_m in particular is a fixed_params "
    "entry and is not one of the ten pins.")


class InferenceError(RuntimeError):
    """Increment-B contract violation.

    Messages carry shapes, counts, names, dtypes and scalar diagnostics only.
    Mirrors the Increment-A `ScoreStreamError` discipline: no household-level
    quantity is ever interpolated into a message.
    """

    def __init__(self, message: str, code: str = "IB-CONTRACT"):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# 2. gate result plumbing (design v4 s14, s15)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GateResult:
    """One design-v4 gate or warning, as a checkable structured record."""

    gate: str
    tier: str                      # "gating" | "warning"
    passed: bool
    statement: str
    observed: Dict[str, Any] = field(default_factory=dict)
    bar: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"gate": self.gate, "tier": self.tier, "passed": bool(self.passed),
                "statement": self.statement,
                "observed": _jsonable(self.observed), "bar": _jsonable(self.bar)}


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (bool, int, float, str)) or obj is None:
        return obj
    return str(obj)


def gating_failures(gates: Sequence[GateResult]) -> List[str]:
    """Names of failed GATING gates. Warning-tier never determines the verdict
    (design v4 s14: warnings are informational, following the Phase-4 precedent)."""
    return [g.gate for g in gates if g.tier == "gating" and not g.passed]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_text_lines(names: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest()


def _sym_dev(a: np.ndarray) -> float:
    return float(np.max(np.abs(a - a.T))) if a.size else 0.0


def _eig_sym(a: np.ndarray) -> np.ndarray:
    """Eigenvalues of a symmetric matrix, ascending. `eigvalsh` only -- never a
    general eigensolver on an object the design declares symmetric."""
    return np.linalg.eigvalsh((a + a.T) / 2.0)


# --------------------------------------------------------------------------- #
# 3. bread: load, authenticate, symmetrise, name-reduce (design v4 s8.1)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Bread:
    """The authenticated Phase-4 bread and its by-name interior reduction.

    `H_raw` is the persisted, UNSYMMETRISED 37x37 array; `Hs` is the mandatory
    symmetrisation (design v4 s8.1 point 2 -- Phase 4's own `Hs` is persisted
    nowhere, so a Phase 5 that skipped this would not be using the object Phase 4
    accepted); `H_II` is the 35x35 interior block obtained by NAME-KEYED deletion
    from `Hs`, never from a persisted Phase-4 subblock (design v4 s11.2).
    """

    H_raw: np.ndarray
    Hs: np.ndarray
    H_II: np.ndarray
    sha256: str
    interior_names: Tuple[str, ...]
    diagnostics: Dict[str, Any]


def load_bread(pmap, repo_root: Path = MNL_ROOT, *, authenticate: bool = True) -> Bread:
    """Load `hessian_free.npy`, authenticate it, symmetrise, reduce by name.

    The bread is **never recomputed**: recomputing the Hessian would constitute
    invoking it, which charter s6 forbids (design v4 s2).
    """
    path = Path(repo_root) / PHASE4_BREAD_NPY
    sha = _sha256_file(path)
    if authenticate and sha != BREAD_SHA256:
        raise InferenceError(
            f"[IB-BREADHASH] hessian_free.npy sha256 {sha} != accepted "
            f"{BREAD_SHA256}; the authoritative bread is not the accepted object",
            code="IB-BREADHASH")

    H_raw = np.load(path, allow_pickle=False)
    if H_raw.shape != (N_FREE, N_FREE):
        raise InferenceError(
            f"[IB-BREADSHAPE] bread shape {H_raw.shape} != {(N_FREE, N_FREE)}",
            code="IB-BREADSHAPE")
    if H_raw.dtype != np.float64:
        raise InferenceError(
            f"[IB-BREADDTYPE] bread dtype {H_raw.dtype} != float64",
            code="IB-BREADDTYPE")
    if not np.isfinite(H_raw).all():
        raise InferenceError("[IB-BREADFINITE] bread contains non-finite entries",
                             code="IB-BREADFINITE")

    asym = _sym_dev(H_raw)
    if asym > HESSIAN_SYMMETRY_THRESHOLD:
        raise InferenceError(
            f"[IB-BREADSYM] bread asymmetry {asym!r} exceeds the Phase-4 recorded "
            f"threshold {HESSIAN_SYMMETRY_THRESHOLD!r} (T-6)", code="IB-BREADSYM")
    Hs = (H_raw + H_raw.T) / 2.0

    sel = np.asarray(pmap.interior_positions_in_free, dtype=np.int64)
    if sel.size != N_INTERIOR:
        raise InferenceError(
            f"[IB-INTERIOR] interior selector has {sel.size} entries != {N_INTERIOR}",
            code="IB-INTERIOR")
    interior_names = tuple(pmap.interior_names)
    if tuple(pmap.free_names[p] for p in sel) != interior_names:
        raise InferenceError(
            "[IB-INTERIOR] interior selector positions do not reproduce the "
            "authenticated interior name sequence", code="IB-INTERIOR")
    H_II = Hs[np.ix_(sel, sel)]

    eig_full = _eig_sym(Hs)
    max_eig = float(eig_full[-1])
    diagnostics = {
        "bread_sha256": sha,
        "max_abs_H": float(np.max(np.abs(H_raw))),
        "max_abs_asymmetry_raw": asym,
        "symmetry_threshold": HESSIAN_SYMMETRY_THRESHOLD,
        "min_eig_Hs": float(eig_full[0]),
        "max_eig_Hs": max_eig,
        "condition_number_Hs": float(max_eig / eig_full[0]) if eig_full[0] != 0 else math.inf,
        "rank_tolerance": RANK_TOLERANCE_REL * max_eig,
        "rank_Hs": int(np.sum(eig_full > RANK_TOLERANCE_REL * max_eig)),
        "interior_reduction": "name-keyed deletion of the two active-bound free "
                              "positions from Hs",
    }
    return Bread(H_raw=H_raw, Hs=Hs, H_II=H_II, sha256=sha,
                 interior_names=interior_names, diagnostics=diagnostics)


@dataclass(frozen=True)
class AcceptedGradients:
    """The accepted free gradient of negLL, from the AUTHORITATIVE artifact.

    Read from `phase4_diagnostics.json -> gradient_free`, which carries the
    37 components at full float64 precision. The committed
    `phase5_parameter_map_v1.csv` also has a `grad_free_negll` column, but it is
    a REDUCED-PRECISION rendering (13 significant digits): its interior maximum
    is `1.099259720618e-4` where the authoritative value is
    `1.0992597206183063e-4`, a relative difference of ~2.8e-13. That is
    immaterial against the T-19/T-22 margins, but the same `.npy`-authoritative /
    `.csv`-rendering distinction that design v4 F-4 drew for the Hessian applies
    here, so this module reads the JSON and never the CSV for gradient values.
    """

    free: np.ndarray                       # (37,)
    interior: np.ndarray                   # (35,)
    active_multipliers: Dict[str, float]   # name -> mu_j = -grad_negll_j
    interior_max_abs: float
    interior_argmax_name: str


def load_accepted_gradients(pmap, repo_root: Path = MNL_ROOT) -> AcceptedGradients:
    """Load the accepted free gradient and project it BY NAME."""
    path = Path(repo_root) / PHASE4_DIAGNOSTICS
    payload = json.loads(path.read_text(encoding="utf-8"))
    free = np.asarray(payload["gradient_free"], dtype=np.float64)
    if free.shape != (N_FREE,):
        raise InferenceError(
            f"[IB-GRADSHAPE] accepted gradient_free shape {free.shape} != "
            f"{(N_FREE,)}", code="IB-GRADSHAPE")
    sel = np.asarray(pmap.interior_positions_in_free, dtype=np.int64)
    interior = free[sel]
    mults = {pmap.free_names[p]: -float(free[p])
             for p in pmap.active_positions_in_free}
    k = int(np.argmax(np.abs(interior)))
    return AcceptedGradients(
        free=free, interior=interior, active_multipliers=mults,
        interior_max_abs=float(np.abs(interior[k])),
        interior_argmax_name=pmap.interior_names[k])


# --------------------------------------------------------------------------- #
# 4. covariance objects (design v4 s8.2, s8.3, s9.1, s10)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Covariances:
    """The two reported covariance objects and their construction diagnostics.

    `V_model = H_II^-1` is the specification diagnostic (design v4 s8.4);
    `V_robust = c * B M B` is the certified headline (design v4 s9.1, s11.3).
    `V_robust_cr0` is the SAME sandwich with `c = 1` -- the uncorrected CR0
    object, carried in diagnostics so the correction is recoverable rather than
    baked in irreversibly (deputy D-1).
    """

    V_model: np.ndarray
    V_robust: np.ndarray
    V_robust_cr0: np.ndarray
    se_model: np.ndarray
    se_robust: np.ndarray
    correction_c: float
    interior_names: Tuple[str, ...]
    diagnostics: Dict[str, Any]


def _cho_inverse(a: np.ndarray, label: str) -> np.ndarray:
    """`a^-1` by Cholesky factorisation solve against the identity.

    Design v4 s8.2 names exactly this route: `cho_solve(cho_factor(H_II), I)`.
    `numpy.linalg.inv` is never called anywhere in this module (charter s10 /
    design v4 s8.3).
    """
    from scipy.linalg import cho_factor, cho_solve

    try:
        c, low = cho_factor(np.ascontiguousarray(a, dtype=np.float64))
    except Exception as exc:                       # not positive definite
        raise InferenceError(
            f"[IB-CHOL] Cholesky factorisation of {label} failed "
            f"({type(exc).__name__}); the matrix is not positive definite",
            code="IB-CHOL") from None
    return cho_solve((c, low), np.eye(a.shape[0], dtype=np.float64))


def _cho_solve_against(a: np.ndarray, rhs: np.ndarray, label: str) -> np.ndarray:
    from scipy.linalg import cho_factor, cho_solve

    try:
        c, low = cho_factor(np.ascontiguousarray(a, dtype=np.float64))
    except Exception as exc:
        raise InferenceError(
            f"[IB-CHOL] Cholesky factorisation of {label} failed "
            f"({type(exc).__name__}); the matrix is not positive definite",
            code="IB-CHOL") from None
    return cho_solve((c, low), rhs)


def build_covariances(bread: Bread, meat_interior35: np.ndarray, *,
                      meat_n_households: Optional[int] = None,
                      correction_c: float = CORRECTION_C) -> Covariances:
    """`V_model = H_II^-1` and `V_robust = c * H_II^-1 M_35 H_II^-1`.

    `meat_interior35` is the Increment-A streamed `M_35` -- an aggregate, never a
    score matrix. It is symmetrised here (design v4 s9.1: "with `M` symmetrised
    after gate T-7 to remove accumulation asymmetry"); T-7 must therefore be
    evaluated on the RAW aggregate, before this call.

    `meat_n_households` is the household count the meat was accumulated over. It
    is recorded, and compared against the accepted `G = 1555`, purely so that a
    MIXED-SCALE object cannot be silently mistaken for an inferential result: the
    bread is always the whole-sample Phase-4 Hessian, so pairing it with a
    bounded-subset meat yields a covariance whose scale is wrong by `G/n`. That
    combination is legitimate for exercising algebra and structural gates, and is
    meaningless as inference. The distinction is carried on every object built
    here as `inference_grade`, and echoed by W-1 and W-4, rather than being left
    to prose. This is an implementation safeguard, not a design gate: no design
    gate, tolerance or constant is altered by it.
    """
    M = np.asarray(meat_interior35, dtype=np.float64)
    if M.shape != (N_INTERIOR, N_INTERIOR):
        raise InferenceError(
            f"[IB-MEATSHAPE] meat shape {M.shape} != {(N_INTERIOR, N_INTERIOR)}",
            code="IB-MEATSHAPE")
    if not np.isfinite(M).all():
        raise InferenceError("[IB-MEATFINITE] meat contains non-finite entries",
                             code="IB-MEATFINITE")
    M = (M + M.T) / 2.0

    B = _cho_inverse(bread.H_II, "H_II")
    V_model = B
    V_robust_cr0 = B @ M @ B
    V_robust = float(correction_c) * V_robust_cr0

    diag_model = np.diag(V_model)
    diag_robust = np.diag(V_robust)
    if np.any(diag_model <= 0) or not np.isfinite(diag_model).all():
        raise InferenceError(
            "[IB-VDIAG] V_model has a non-positive or non-finite diagonal entry",
            code="IB-VDIAG")
    if np.any(diag_robust <= 0) or not np.isfinite(diag_robust).all():
        raise InferenceError(
            "[IB-VDIAG] V_robust has a non-positive or non-finite diagonal entry",
            code="IB-VDIAG")

    # T-8 reference: the same inverse via a pseudo-inverse, for deviation only
    pinv_ref = np.linalg.pinv(bread.H_II)
    full_sample = (meat_n_households == N_HOUSEHOLDS)
    diagnostics = {
        "meat_n_households": (int(meat_n_households)
                              if meat_n_households is not None else None),
        "full_sample_meat": bool(full_sample),
        "inference_grade": ("full-sample" if full_sample else "subset-diagnostic"),
        "scale_note": (
            "bread is always the whole-sample Phase-4 Hessian; a meat accumulated "
            "over n < 1555 households yields a covariance scaled by ~n/G. Such an "
            "object exercises algebra and structural gates only and is not an "
            "inferential result."),
        "correction_c": float(correction_c),
        "correction_formula": "[G/(G-1)] * [(N-1)/(N-K)] = G/(G-K)",
        "correction_G": CORRECTION_G,
        "correction_N": CORRECTION_N,
        "correction_K": CORRECTION_K,
        "correction_telescoped": f"{CORRECTION_G}/{CORRECTION_G - CORRECTION_K}",
        "correction_se_inflation_pct": float((math.sqrt(correction_c) - 1.0) * 100.0),
        "cr0_recoverable": True,
        "cr0_note": "V_robust_cr0 is the uncorrected sandwich; "
                    "V_robust = correction_c * V_robust_cr0 exactly (deputy D-1)",
        "solve_vs_pinv_max_abs_dev": float(np.max(np.abs(B - pinv_ref))),
        "meat_symmetrised": True,
        "explicit_inverse_used": False,
        "inverse_route": "scipy.linalg.cho_solve(cho_factor(H_II), I_35)",
    }
    return Covariances(
        V_model=V_model, V_robust=V_robust, V_robust_cr0=V_robust_cr0,
        se_model=np.sqrt(diag_model), se_robust=np.sqrt(diag_robust),
        correction_c=float(correction_c),
        interior_names=bread.interior_names, diagnostics=diagnostics)


def correlation_from_covariance(V: np.ndarray) -> np.ndarray:
    """Correlation matrix with an exactly unit diagonal (T-18)."""
    d = np.sqrt(np.diag(V))
    R = V / np.outer(d, d)
    np.fill_diagonal(R, 1.0)
    return R


# --------------------------------------------------------------------------- #
# 5. regional inference (design v4 s13.2, s13.4)
# --------------------------------------------------------------------------- #
def regional_selector(pmap) -> np.ndarray:
    """`E_R` in R^{10x35}: row b is the unit vector for the interior position of
    access-block name b. Built BY NAME from the authenticated map, never
    positionally (design v4 s13.4 / s7.2)."""
    names = list(pmap.interior_names)
    E = np.zeros((N_REGIONAL, N_INTERIOR), dtype=np.float64)
    for b, nm in enumerate(REGIONAL_BLOCK_NAMES):
        if nm not in names:
            raise InferenceError(
                f"[IB-REGNAME] access-block name {nm!r} is absent from the "
                "authenticated interior name sequence", code="IB-REGNAME")
        E[b, names.index(nm)] = 1.0
    return E


def null_selector(null_id: str, rows: Sequence[str]) -> np.ndarray:
    """`A` in R^{qx10}, rows keyed by parameter name within the access block."""
    A = np.zeros((len(rows), N_REGIONAL), dtype=np.float64)
    for i, nm in enumerate(rows):
        if nm not in REGIONAL_BLOCK_NAMES:
            raise InferenceError(
                f"[IB-NULLNAME] {null_id}: {nm!r} is not an access-block name",
                code="IB-NULLNAME")
        A[i, REGIONAL_BLOCK_NAMES.index(nm)] = 1.0
    return A


@dataclass(frozen=True)
class RegionalTests:
    """The four pre-registered nulls in both model and robust form.

    Fix 4 / ruling R-37a: `inference_grade` travels on this container, on
    `diagnostics`, and on `table.attrs`, so a subset-derived Wald statistic can
    never be serialized without its label.
    """

    table: pd.DataFrame
    V_RR_model: np.ndarray
    V_RR_robust: np.ndarray
    corr_RR_robust: np.ndarray
    theta_R: np.ndarray
    diagnostics: Dict[str, Any]
    inference_grade: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


def _wald(A: np.ndarray, theta_R: np.ndarray, V_RR: np.ndarray, label: str) -> float:
    d = A @ theta_R
    AVA = A @ V_RR @ A.T
    return float(d @ _cho_solve_against(AVA, d, f"A V_RR A' ({label})"))


def run_regional_tests(pmap, cov: Covariances, theta_interior: np.ndarray
                       ) -> RegionalTests:
    """H0-A / H0-B / H0-C / H0-G, each in model and robust form.

    Statistic per design v4 s13.4: `d = A theta_R - r` with `r = 0`,
    `W = d' (A V_RR A')^-1 d` via `cho_factor`/`cho_solve`, `W ~ chi2(q)`.
    Separate `p_model` and `p_robust` are reported, never a single p-value.
    """
    from scipy.stats import chi2

    theta_I = np.asarray(theta_interior, dtype=np.float64)
    if theta_I.shape != (N_INTERIOR,):
        raise InferenceError(
            f"[IB-THETASHAPE] interior theta shape {theta_I.shape} != {(N_INTERIOR,)}",
            code="IB-THETASHAPE")
    E_R = regional_selector(pmap)
    theta_R = E_R @ theta_I
    V_RR_model = E_R @ cov.V_model @ E_R.T
    V_RR_robust = E_R @ cov.V_robust @ E_R.T

    rows = []
    for null_id, names, tier in NULL_DEFINITIONS:
        A = null_selector(null_id, names)
        q = len(names)
        w_model = _wald(A, theta_R, V_RR_model, f"{null_id}/model")
        w_robust = _wald(A, theta_R, V_RR_robust, f"{null_id}/robust")
        rows.append({
            "null_id": null_id,
            "q": q,
            "restriction_names": ";".join(names),
            "W_model": w_model,
            "W_robust": w_robust,
            "p_model": float(chi2.sf(w_model, q)),
            "p_robust": float(chi2.sf(w_robust, q)),
            "chi2_crit_95": CHI2_CRIT_95[q],
            "tier": tier,
        })
    table = pd.DataFrame(rows, columns=[
        "null_id", "q", "restriction_names", "W_model", "W_robust",
        "p_model", "p_robust", "chi2_crit_95", "tier"])

    eig_rr = _eig_sym(V_RR_robust)
    weakest = int(np.argmin(eig_rr))
    grade = cov.diagnostics.get("inference_grade", "unknown")
    metadata = {
        "inference_grade": grade,
        "meat_n_households": cov.diagnostics.get("meat_n_households"),
        "full_sample_meat": cov.diagnostics.get("full_sample_meat"),
        "correction_c": cov.correction_c,
        "scale_note": cov.diagnostics.get("scale_note"),
    }
    diagnostics = {
        "regional_names": list(REGIONAL_BLOCK_NAMES),
        "interior_positions": [list(pmap.interior_names).index(n)
                               for n in REGIONAL_BLOCK_NAMES],
        "V_RR_robust_eigenvalues": eig_rr.tolist(),
        "V_RR_robust_min_eig": float(eig_rr[0]),
        "V_RR_robust_rank": int(np.sum(eig_rr > RANK_TOLERANCE_REL * float(eig_rr[-1]))),
        "weakest_direction_index": weakest,
        "weakest_direction_eigenvalue": float(eig_rr[weakest]),
        **metadata,
    }
    table.attrs.update(metadata)
    return RegionalTests(table=table, V_RR_model=V_RR_model,
                         V_RR_robust=V_RR_robust,
                         corr_RR_robust=correlation_from_covariance(V_RR_robust),
                         theta_R=theta_R, diagnostics=diagnostics,
                         inference_grade=grade, metadata=metadata)


# --------------------------------------------------------------------------- #
# 6. the 47-row reporting table (design v4 s11.3, s12.2, s17.3)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ParameterTable:
    """The 47-row table plus its ENCLOSING-OBJECT metadata.

    Fix 4 / ruling R-37a: `inference_grade` and the gradient source travel on
    this container, never as extra columns -- the 13-column schema is fixed.
    """

    frame: pd.DataFrame
    footnote: str
    inference_grade: str = "unknown"
    gradient_source: str = PHASE4_DIAGNOSTICS
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_parameter_table(pmap, cov: Covariances, param_map_frame: pd.DataFrame,
                          grads: "AcceptedGradients") -> ParameterTable:
    """The exact 13-column, 47-row table, with literal `NA` where design v4 s17.3
    requires it.

    Population rules, exhaustive by status (design v4 s17.3):

    | column      | interior          | active-bound      | pinned            |
    | estimate    | accepted value    | 1.0               | pinned value      |
    | bound_value | NA                | 1.0               | NA                |
    | bound_side  | NA                | upper             | NA                |
    | grad_negll  | AUTHORITATIVE grad| AUTHORITATIVE grad| 0.0 (structural)  |
    | multiplier  | NA                | -grad_negll       | NA                |
    | 5 inferential| computed         | NA                | NA                |

    Fix 3 / ruling R-37b: `grad_negll` and the two multipliers come from
    `grads` -- i.e. from `phase4_diagnostics.json -> gradient_free`, projected by
    authenticated name. The `grad_free_negll` column of the parameter-map CSV is
    a REDUCED-PRECISION rendering; it is read here only to compute an explicit
    non-authoritative comparison recorded in `metadata`, and it never feeds any
    arithmetic that reaches the table.
    """
    from scipy.stats import norm

    src = param_map_frame.sort_values("full_index_0based").reset_index(drop=True)
    if [str(n) for n in src["param"]] != list(pmap.all_names):
        raise InferenceError(
            "[IB-MAPNAMES] the supplied parameter-map frame does not carry the "
            "authenticated 47-name sequence in certified order", code="IB-MAPNAMES")
    interior_names = list(cov.interior_names)
    if interior_names != list(pmap.interior_names):
        raise InferenceError(
            "[IB-MAPNAMES] covariance interior names differ from the authenticated "
            "interior name sequence", code="IB-MAPNAMES")
    se_m = {n: float(cov.se_model[i]) for i, n in enumerate(interior_names)}
    se_r = {n: float(cov.se_robust[i]) for i, n in enumerate(interior_names)}

    # AUTHORITATIVE gradient, keyed by free name (design v4 F-4 discipline)
    if np.asarray(grads.free).shape != (N_FREE,):
        raise InferenceError(
            f"[IB-GRADSHAPE] authoritative free gradient shape "
            f"{np.asarray(grads.free).shape} != {(N_FREE,)}", code="IB-GRADSHAPE")
    grad_by_name = {n: float(grads.free[i]) for i, n in enumerate(pmap.free_names)}

    rows: List[Dict[str, Any]] = []
    for rec in src.to_dict("records"):
        name = str(rec["param"])
        status_raw = str(rec["status"])
        status = "active-bound" if status_raw == "active_bound" else status_raw
        if status not in STATUS_VALUES:
            raise InferenceError(
                f"[IB-STATUS] parameter {name!r} has status {status!r}, not one of "
                f"{sorted(STATUS_VALUES)}", code="IB-STATUS")
        row: Dict[str, Any] = {"name": name, "block": str(rec["block"]),
                               "status": status}
        if status == "interior":
            est = float(rec["accepted_value_full_precision"])
            g = grad_by_name[name]                    # AUTHORITATIVE, not the CSV
            s_m, s_r = se_m[name], se_r[name]
            z = est / s_r
            row.update({
                "estimate": est, "bound_value": NA, "bound_side": NA,
                "grad_negll": g, "multiplier": NA,
                "se_model": s_m, "se_robust": s_r,
                "ratio_robust_model": s_r / s_m,
                "z": z, "p": float(2.0 * norm.sf(abs(z))),
            })
        elif status == "active-bound":
            g = grad_by_name[name]                    # AUTHORITATIVE, not the CSV
            row.update({
                "estimate": 1.0, "bound_value": 1.0, "bound_side": "upper",
                "grad_negll": g, "multiplier": -g,
            })
            row.update({c: NA for c in INFERENTIAL_COLUMNS})
        else:                                            # pinned
            row.update({
                "estimate": float(rec["pin_value"]), "bound_value": NA,
                "bound_side": NA, "grad_negll": 0.0, "multiplier": NA,
            })
            row.update({c: NA for c in INFERENTIAL_COLUMNS})
        rows.append(row)

    frame = pd.DataFrame(rows, columns=list(PARAMETER_TABLE_COLUMNS))
    validate_parameter_table(frame)

    # EXPLICIT non-authoritative comparison. The CSV column is read here and
    # nowhere else; its only effect is this recorded deviation.
    csv_by_name = {str(r["param"]): float(r["grad_free_negll"])
                   for r in src.to_dict("records")
                   if str(r["param"]) in grad_by_name}
    csv_dev = max((abs(csv_by_name[n] - grad_by_name[n]) for n in csv_by_name),
                  default=0.0)
    grade = cov.diagnostics.get("inference_grade", "unknown")
    metadata = {
        "inference_grade": grade,
        "gradient_source": PHASE4_DIAGNOSTICS,
        "gradient_source_authoritative": True,
        "csv_gradient_column_used_for_arithmetic": False,
        "csv_vs_authoritative_gradient_max_abs_dev": float(csv_dev),
        "csv_gradient_note": (
            "phase5_parameter_map_v1.csv grad_free_negll is a reduced-precision "
            "rendering, compared here and never used in any computation"),
        "meat_n_households": cov.diagnostics.get("meat_n_households"),
        "full_sample_meat": cov.diagnostics.get("full_sample_meat"),
        "correction_c": cov.correction_c,
    }
    frame.attrs.update(metadata)
    return ParameterTable(frame=frame, footnote=PIN_TABLE_FOOTNOTE,
                          inference_grade=grade,
                          gradient_source=PHASE4_DIAGNOSTICS,
                          metadata=metadata)


def validate_parameter_table(frame: pd.DataFrame) -> None:
    """Enforce the s17.3 schema. Raises `InferenceError` on any violation."""
    if list(frame.columns) != list(PARAMETER_TABLE_COLUMNS):
        raise InferenceError(
            f"[IB-SCHEMA] parameter table columns {list(frame.columns)} != the "
            f"exact 13-column schema {list(PARAMETER_TABLE_COLUMNS)}",
            code="IB-SCHEMA")
    if len(frame) != N_FULL:
        raise InferenceError(
            f"[IB-SCHEMA] parameter table has {len(frame)} rows != {N_FULL}",
            code="IB-SCHEMA")
    bad = sorted(set(frame["status"]) - STATUS_VALUES)
    if bad:
        raise InferenceError(
            f"[IB-SCHEMA] unknown status value(s) {bad}", code="IB-SCHEMA")
    n_active = int((frame["status"] == "active-bound").sum())
    n_pinned = int((frame["status"] == "pinned").sum())
    n_interior = int((frame["status"] == "interior").sum())
    if (n_interior, n_active, n_pinned) != (N_INTERIOR, 2, 10):
        raise InferenceError(
            f"[IB-SCHEMA] status counts (interior, active-bound, pinned) = "
            f"({n_interior}, {n_active}, {n_pinned}) != (35, 2, 10)",
            code="IB-SCHEMA")
    non_inferential = frame[frame["status"] != "interior"]
    for col in INFERENTIAL_COLUMNS:
        offenders = [r["name"] for r in non_inferential.to_dict("records")
                     if r[col] != NA]
        if offenders:
            raise InferenceError(
                f"[IB-NA] column {col!r} must be the literal string 'NA' for every "
                f"active-bound and pinned row; offenders: {offenders}", code="IB-NA")
    for rec in frame.to_dict("records"):
        if rec["status"] == "active-bound":
            if rec["bound_value"] != 1.0 or rec["bound_side"] != "upper":
                raise InferenceError(
                    f"[IB-BOUND] active-bound row {rec['name']!r} must carry "
                    "bound_value 1.0 and bound_side 'upper'", code="IB-BOUND")
            if not np.isclose(rec["multiplier"], -rec["grad_negll"], rtol=0, atol=0):
                raise InferenceError(
                    f"[IB-BOUND] active-bound row {rec['name']!r}: multiplier must "
                    "equal -grad_negll exactly", code="IB-BOUND")
        elif rec["status"] == "pinned":
            if rec["grad_negll"] != 0.0:
                raise InferenceError(
                    f"[IB-PIN] pinned row {rec['name']!r} must carry grad_negll 0.0 "
                    "(structural, design v4 s12.3)", code="IB-PIN")
            if rec["bound_value"] != NA or rec["bound_side"] != NA \
                    or rec["multiplier"] != NA:
                raise InferenceError(
                    f"[IB-PIN] pinned row {rec['name']!r} must carry NA for "
                    "bound_value, bound_side and multiplier", code="IB-PIN")


# --------------------------------------------------------------------------- #
# 7. gates (design v4 s14, s15, s16)
# --------------------------------------------------------------------------- #
def accepted_theta_sha256(repo_root: Path = MNL_ROOT) -> str:
    """SHA-256 of the accepted 47-vector's float64 BYTES (design v4 s15, T-5).

    Fix 1 / review finding 1. Read from the Phase-3 bundle's
    `estimation_results.json -> results.joint.theta`, hashed exactly the way the
    accepted anchor `c024b893...` was produced: C-contiguous float64 `tobytes()`.
    """
    payload = json.loads((Path(repo_root) / PHASE3_RESULTS).read_text(encoding="utf-8"))
    theta = np.asarray(payload["results"]["joint"]["theta"], dtype=np.float64)
    if theta.shape != (N_FULL,):
        raise InferenceError(
            f"[IB-THETASHAPE] accepted theta shape {theta.shape} != {(N_FULL,)}",
            code="IB-THETASHAPE")
    return hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest()


def gate_T5_bread_provenance(bread: Bread, bundle_hashes: Dict[str, str], *,
                             theta_sha256: str) -> GateResult:
    """T-5, complete per design v4 s15.

    Fix 1: the gate covers all FOUR anchors the design names -- the bread hash,
    the Phase-3 bundle, the Phase-4 bundle, AND the accepted theta bytes. The
    theta hash is a required keyword: a caller cannot omit it and still obtain a
    pass, which is how the previous version silently checked only three of four.
    """
    expected = {"phase3": PHASE3_BUNDLE_SHA256, "phase4": PHASE4_BUNDLE_SHA256}
    checks = {
        "bread_sha256_matches": bread.sha256 == BREAD_SHA256,
        "phase3_bundle_matches": bundle_hashes.get("phase3") == expected["phase3"],
        "phase4_bundle_matches": bundle_hashes.get("phase4") == expected["phase4"],
        "theta_bytes_match": theta_sha256 == ACCEPTED_THETA_SHA256,
    }
    return GateResult(
        gate="T-5", tier="gating", passed=all(checks.values()),
        statement="Bread provenance: hessian_free.npy SHA-256, the Phase-3 and "
                  "Phase-4 bundle hashes, and the accepted theta-byte hash all "
                  "match their design v4 s15 anchors",
        observed={**{k: bool(v) for k, v in checks.items()},
                  "bread_sha256": bread.sha256,
                  "theta_sha256": theta_sha256, **bundle_hashes},
        bar={"bread_sha256": BREAD_SHA256,
             "theta_sha256": ACCEPTED_THETA_SHA256, **expected})


def gate_T6_bread_integrity(bread: Bread) -> GateResult:
    d = bread.diagnostics
    checks = {
        "asymmetry_within_threshold": d["max_abs_asymmetry_raw"] <= HESSIAN_SYMMETRY_THRESHOLD,
        "min_eig_positive": d["min_eig_Hs"] > 0.0,
        "rank_is_37": d["rank_Hs"] == N_FREE,
        "min_eig_matches_phase4": bool(np.isclose(d["min_eig_Hs"], PHASE4_MIN_EIG,
                                                  rtol=PHASE4_EIGEN_RTOL, atol=0.0)),
        "condition_matches_phase4": bool(np.isclose(d["condition_number_Hs"],
                                                    PHASE4_CONDITION_NUMBER,
                                                    rtol=PHASE4_EIGEN_RTOL, atol=0.0)),
        "H_II_cholesky_succeeds": _cholesky_ok(bread.H_II),
    }
    return GateResult(
        gate="T-6", tier="gating", passed=all(checks.values()),
        statement="Bread integrity on load: symmetry, PD, rank 37, Phase-4 eigen "
                  "agreement at rtol 1e-10, name-keyed H_II, Cholesky of H_II",
        observed={**{k: bool(v) for k, v in checks.items()},
                  "min_eig_Hs": d["min_eig_Hs"],
                  "condition_number_Hs": d["condition_number_Hs"],
                  "rank_Hs": d["rank_Hs"],
                  "max_abs_asymmetry_raw": d["max_abs_asymmetry_raw"]},
        bar={"symmetry_threshold": HESSIAN_SYMMETRY_THRESHOLD,
             "phase4_min_eig": PHASE4_MIN_EIG,
             "phase4_condition_number": PHASE4_CONDITION_NUMBER,
             "eigen_rtol": PHASE4_EIGEN_RTOL})


def _cholesky_ok(a: np.ndarray) -> bool:
    try:
        np.linalg.cholesky(a)
        return True
    except np.linalg.LinAlgError:
        return False


def gate_T7_meat_validity(meat_raw: np.ndarray) -> GateResult:
    """Meat validity on the RAW streamed aggregate, BEFORE symmetrisation."""
    M = np.asarray(meat_raw, dtype=np.float64)
    max_abs = float(np.max(np.abs(M))) if M.size else 0.0
    asym = _sym_dev(M)
    eig = _eig_sym(M)
    min_eig, max_eig = float(eig[0]), float(eig[-1])
    floor = -KAPPA_BE_CERTIFIED * max_eig
    checks = {
        "symmetric_before_symmetrisation": asym <= SYMMETRY_REL * max_abs,
        "psd_within_backward_error": min_eig >= floor,
    }
    return GateResult(
        gate="T-7", tier="gating", passed=all(checks.values()),
        statement="Meat validity: max|M - M'| <= 1e-12*max|M| before "
                  "symmetrisation; min_eig(M) >= -kappa_BE_certified * max_eig(M)",
        observed={**{k: bool(v) for k, v in checks.items()},
                  "max_abs_asymmetry": asym, "max_abs_M": max_abs,
                  "min_eig": min_eig, "max_eig": max_eig,
                  "rank": int(np.sum(eig > RANK_TOLERANCE_REL * max_eig))},
        bar={"symmetry_rel": SYMMETRY_REL,
             "kappa_BE_certified": KAPPA_BE_CERTIFIED, "psd_floor": floor})


def gate_T8_solve_stability(cov: Covariances) -> GateResult:
    dev = cov.diagnostics["solve_vs_pinv_max_abs_dev"]
    return GateResult(
        gate="T-8", tier="gating", passed=bool(dev <= SOLVE_VS_PINV_ATOL),
        statement="Solve stability: every inverse-like operation by "
                  "factorisation; max abs deviation from a pseudo-inverse "
                  "reference <= 1e-8",
        observed={"solve_vs_pinv_max_abs_dev": dev,
                  "explicit_inverse_used": cov.diagnostics["explicit_inverse_used"],
                  "inverse_route": cov.diagnostics["inverse_route"]},
        bar={"atol": SOLVE_VS_PINV_ATOL})


def gate_T9_covariance_validity(cov: Covariances) -> GateResult:
    out: Dict[str, Any] = {}
    checks: Dict[str, bool] = {}
    for label, V in (("V_model", cov.V_model), ("V_robust", cov.V_robust)):
        max_abs = float(np.max(np.abs(V)))
        asym = _sym_dev(V)
        eig = _eig_sym(V)
        out[f"{label}_max_abs_asymmetry"] = asym
        out[f"{label}_min_eig"] = float(eig[0])
        out[f"{label}_max_eig"] = float(eig[-1])
        checks[f"{label}_symmetric"] = asym <= SYMMETRY_REL * max_abs
        checks[f"{label}_diag_positive_finite"] = bool(
            np.all(np.diag(V) > 0) and np.isfinite(np.diag(V)).all())
    checks["V_model_positive_definite"] = float(_eig_sym(cov.V_model)[0]) > 0.0
    rob_eig = _eig_sym(cov.V_robust)
    checks["V_robust_psd"] = float(rob_eig[0]) >= -COVARIANCE_PSD_REL * float(rob_eig[-1])
    return GateResult(
        gate="T-9", tier="gating", passed=all(checks.values()),
        statement="Covariance validity: symmetry to 1e-12 relative; V_model PD; "
                  "V_robust PSD at min_eig >= -1e-10*max_eig; all 35 diagonals "
                  "strictly positive and finite",
        observed={**{k: bool(v) for k, v in checks.items()}, **out},
        bar={"symmetry_rel": SYMMETRY_REL, "psd_rel": COVARIANCE_PSD_REL})


def gate_T10_correction_scalar(cov: Covariances) -> GateResult:
    d = cov.diagnostics
    ok = (d["correction_G"] == CORRECTION_G and d["correction_N"] == CORRECTION_N
          and d["correction_K"] == CORRECTION_K
          and abs(cov.correction_c - CORRECTION_C) == 0.0)
    return GateResult(
        gate="T-10", tier="gating", passed=bool(ok),
        statement="Correction scalar recorded as an explicit number with its "
                  "formula, G, N, K and the telescoped form G/(G-K)",
        observed={k: d[k] for k in ("correction_c", "correction_formula",
                                    "correction_G", "correction_N", "correction_K",
                                    "correction_telescoped",
                                    "correction_se_inflation_pct",
                                    "cr0_recoverable")},
        bar={"correction_c": CORRECTION_C})


def gate_T14_regional(reg: RegionalTests) -> GateResult:
    eig = np.asarray(reg.diagnostics["V_RR_robust_eigenvalues"], dtype=np.float64)
    finite = bool(np.isfinite(reg.table[["W_model", "W_robust"]].to_numpy()).all())
    dfs = list(reg.table["q"])
    checks = {
        "V_RR_positive_definite": float(eig[0]) > 0.0,
        "V_RR_rank_10": reg.diagnostics["V_RR_robust_rank"] == N_REGIONAL,
        "all_W_finite": finite,
        "degrees_of_freedom": dfs == [10, 7, 2, 1],
        "both_forms_present": {"W_model", "W_robust", "p_model", "p_robust"}
                              <= set(reg.table.columns),
    }
    return GateResult(
        gate="T-14", tier="gating", passed=all(bool(v) for v in checks.values()),
        statement="Regional tests: V_RR PD, rank 10; W finite for H0-A/B/C/G; "
                  "both model and robust computed; df recorded as 10, 7, 2, 1",
        observed={**{k: bool(v) if not isinstance(v, list) else v
                     for k, v in checks.items()},
                  "V_RR_robust_min_eig": reg.diagnostics["V_RR_robust_min_eig"]},
        bar={"rank": N_REGIONAL, "degrees_of_freedom": [10, 7, 2, 1]})


def gate_T17_fingerprints(pmap, repo_root: Path = MNL_ROOT) -> GateResult:
    manifest = json.loads((Path(repo_root) / PHASE4_MANIFEST).read_text(encoding="utf-8"))
    free_names = list(manifest["contract"]["parameter_map"]["free_names"])
    interior = [n for n in free_names
                if n not in (free_names[p] for p in pmap.active_positions_in_free)]
    recomputed_free = _sha256_text_lines(free_names)
    recomputed_interior = _sha256_text_lines(interior)
    checks = {
        "free_names_match": free_names == list(pmap.free_names),
        "interior_names_match": interior == list(pmap.interior_names),
        "free_fingerprint_match": recomputed_free == pmap.free_names_sha256,
        "interior_fingerprint_match": recomputed_interior == pmap.interior_names_sha256,
    }
    return GateResult(
        gate="T-17", tier="gating", passed=all(checks.values()),
        statement="Parameter-order fingerprint: SHA-256 of the newline-joined "
                  "ordered 37 free names and 35 interior names equal the values "
                  "recomputed from phase4_manifest.json contract.parameter_map",
        observed={**{k: bool(v) for k, v in checks.items()},
                  "free_names_sha256": pmap.free_names_sha256,
                  "interior_names_sha256": pmap.interior_names_sha256},
        bar={"free_names_sha256": recomputed_free,
             "interior_names_sha256": recomputed_interior})


def gate_T18_valid_correlations(cov: Covariances) -> GateResult:
    out, checks = {}, {}
    for label, V in (("model", cov.V_model), ("robust", cov.V_robust)):
        R = correlation_from_covariance(V)
        mx = float(np.max(np.abs(R)))
        out[f"{label}_max_abs_rho"] = mx
        out[f"{label}_max_diag_dev"] = float(np.max(np.abs(np.diag(R) - 1.0)))
        checks[f"{label}_bounded"] = mx <= CORRELATION_BOUND
        checks[f"{label}_unit_diagonal"] = out[f"{label}_max_diag_dev"] == 0.0
    return GateResult(
        gate="T-18", tier="gating", passed=all(checks.values()),
        statement="Valid correlations: |rho_ij| <= 1 + 1e-10 for all pairs in both "
                  "covariances; unit diagonal after construction",
        observed={**{k: bool(v) for k, v in checks.items()}, **out},
        bar={"correlation_bound": CORRELATION_BOUND})


def gate_T19_stationarity(bread: Bread, cov: Covariances,
                          gradient_interior: np.ndarray) -> GateResult:
    """Implied Newton displacement per interior coordinate vs its robust SE."""
    g = np.asarray(gradient_interior, dtype=np.float64)
    if g.shape != (N_INTERIOR,):
        raise InferenceError(
            f"[IB-GRADSHAPE] interior gradient shape {g.shape} != {(N_INTERIOR,)}",
            code="IB-GRADSHAPE")
    step = _cho_solve_against(bread.H_II, g, "H_II (T-19)")
    ratio = np.abs(step) / cov.se_robust
    worst = int(np.argmax(ratio))
    return GateResult(
        gate="T-19", tier="gating", passed=bool(np.max(ratio) <= STATIONARITY_SE_FRACTION),
        statement="Conditional-35 stationarity: |(H_II^-1 g_I)_j| <= 0.05 * "
                  "se_robust_j for every interior coordinate",
        observed={"max_ratio": float(np.max(ratio)),
                  "worst_coordinate_index": worst,
                  "worst_coordinate_name": cov.interior_names[worst],
                  "displacement_l2": float(np.linalg.norm(step))},
        bar={"se_fraction": STATIONARITY_SE_FRACTION})


def gate_T22_numerical_kkt(multipliers: Dict[str, float],
                           interior_max_abs_grad: float) -> GateResult:
    """T-22 numerical KKT activity, over the EXACT authenticated active set.

    The key set is validated against the two authenticated active-bound names
    BEFORE the 100x threshold is applied: an empty, missing, extra or
    wrong-named mapping fails on the key check and never reaches the threshold.

    Closure B-1 (Review B v2 s7.1). The expected-name set was previously an
    `active_names` parameter defaulting to `ACTIVE_BOUND_NAMES`, so a caller
    could supply its own authority --
    `gate_T22_numerical_kkt({'forged_active': 1.0}, 1e-4,
    active_names=('forged_active',))` returned `passed=True`. That parameter is
    removed. The gate now binds unconditionally to the module's frozen
    `ACTIVE_BOUND_NAMES`; it accepts OBSERVED gradient values from the caller,
    never a replacement expected-name authority. The frozen constant's equality
    with the authenticated parameter map is asserted by `test_I11` and by probe
    B-1 item 3.
    """
    expected = tuple(ACTIVE_BOUND_NAMES)
    supplied = tuple(sorted(multipliers))
    missing = sorted(set(expected) - set(multipliers))
    extra = sorted(set(multipliers) - set(expected))
    names_ok = (not missing) and (not extra)

    floor = KKT_ACTIVITY_FACTOR * float(interior_max_abs_grad)
    if names_ok:
        ratios = {k: float(multipliers[k]) / float(interior_max_abs_grad)
                  for k in expected}
        threshold_ok = all(float(multipliers[k]) >= floor for k in expected)
    else:
        ratios = {}
        threshold_ok = False

    return GateResult(
        gate="T-22", tier="gating", passed=bool(names_ok and threshold_ok),
        statement="Numerical KKT activity (sample-level, not a population claim): "
                  "the multiplier mapping must carry EXACTLY the two authenticated "
                  "active-bound names, and each multiplier must be >= 100 x the "
                  "interior max |grad negLL|",
        observed={"active_names_ok": bool(names_ok),
                  "threshold_ok": bool(threshold_ok),
                  "supplied_names": list(supplied),
                  "missing_names": missing, "extra_names": extra,
                  "multipliers": {k: float(v) for k, v in multipliers.items()},
                  "ratios": ratios,
                  "interior_max_abs_grad": float(interior_max_abs_grad)},
        bar={"required_names": list(expected),
             "factor": KKT_ACTIVITY_FACTOR, "floor": floor})


def warning_W1_ratio(cov: Covariances) -> GateResult:
    ratio = cov.se_robust / cov.se_model
    lo, hi = W1_RATIO_RANGE
    flagged = [cov.interior_names[i] for i in np.flatnonzero((ratio < lo) | (ratio > hi))]
    return GateResult(
        gate="W-1", tier="warning", passed=(len(flagged) == 0),
        statement="Robust/model SE ratio per parameter; flag any ratio outside "
                  "[0.2, 5]. Warning-tier: never determines the verdict",
        observed={"min_ratio": float(np.min(ratio)), "max_ratio": float(np.max(ratio)),
                  "flagged": flagged,
                  "inference_grade": cov.diagnostics["inference_grade"]},
        bar={"range": list(W1_RATIO_RANGE)})


def warning_W2_regional_spectrum(reg: RegionalTests) -> GateResult:
    d = reg.diagnostics
    return GateResult(
        gate="W-2", tier="warning", passed=True,
        statement="Eigenspectrum of V_RR reported with its weakest direction "
                  "identified (reporting requirement, not a gate)",
        observed={"eigenvalues": d["V_RR_robust_eigenvalues"],
                  "weakest_direction_index": d["weakest_direction_index"],
                  "weakest_direction_eigenvalue": d["weakest_direction_eigenvalue"],
                  "inference_grade": reg.inference_grade},
        bar={})


def warning_W3_effective_rank(meat_raw: np.ndarray) -> GateResult:
    eig = _eig_sym(np.asarray(meat_raw, dtype=np.float64))
    pos = eig[eig > 0]
    eff = float(np.sum(pos) ** 2 / np.sum(pos ** 2)) if pos.size else 0.0
    return GateResult(
        gate="W-3", tier="warning", passed=True,
        statement="Effective-rank summary of M relative to 35",
        observed={"effective_rank_participation": eff,
                  "numerical_rank": int(np.sum(eig > RANK_TOLERANCE_REL * float(eig[-1]))),
                  "min_eig": float(eig[0]), "max_eig": float(eig[-1])},
        bar={"dimension": N_INTERIOR})


def warning_W4_near_boundary(cov: Covariances, param_map_frame: pd.DataFrame
                             ) -> GateResult:
    """Robust 95% interval strictly inside the spec bounds; equality triggers."""
    src = param_map_frame.set_index("param")
    flagged = []
    detail = {}
    for i, name in enumerate(cov.interior_names):
        est = float(src.loc[name, "accepted_value_full_precision"])
        lb = float(src.loc[name, "spec_bound_lb"])
        ub = float(src.loc[name, "spec_bound_ub"])
        half = Z_975 * float(cov.se_robust[i])
        lo, hi = est - half, est + half
        if lo <= lb or hi >= ub:
            flagged.append(name)
            detail[name] = {"lo": lo, "hi": hi, "lb": lb, "ub": ub}
    return GateResult(
        gate="W-4", tier="warning", passed=(len(flagged) == 0),
        statement="Near-boundary containment on the ROBUST 95% interval: "
                  "theta_j +- z_0.975 * se_robust_j must lie strictly inside "
                  "[lb_j, ub_j]; equality with a bound triggers the warning "
                  "(mandatory escalation)",
        observed={"flagged": flagged, "detail": detail, "z_975": Z_975,
                  "inference_grade": cov.diagnostics["inference_grade"]},
        bar={"rule": "strict interiority; <= lb or >= ub triggers"})


def warning_W5_centring(score_sum_interior: np.ndarray, cov: Covariances,
                        n_households: int) -> GateResult:
    """Records the centring correction that is deliberately NOT applied."""
    s = np.asarray(score_sum_interior, dtype=np.float64)
    correction = np.outer(s, s) / float(n_households)
    return GateResult(
        gate="W-5", tier="warning", passed=True,
        statement="Centring diagnostic: record ||sum_g s_{g,I}||_inf and the "
                  "magnitude of the centring correction to M that is NOT applied "
                  "(design v4 s9.2 baseline: do not centre)",
        observed={"score_sum_interior_max_abs": float(np.max(np.abs(s))),
                  "score_sum_interior_l2": float(np.linalg.norm(s)),
                  "uncentred": True,
                  "omitted_correction_max_abs": float(np.max(np.abs(correction))),
                  "inference_grade": cov.diagnostics.get("inference_grade")},
        bar={})


# --------------------------------------------------------------------------- #
# 8. aggregate artifact serializers (addendum s3; charter s8)
# --------------------------------------------------------------------------- #
# The persistable set. Anything not on this list cannot be written by this module.
AGGREGATE_ARTIFACTS: Tuple[str, ...] = (
    "score_aggregate_summary.json",
    "score_sum_free37.csv",
    "meat_free37.npy", "meat_free37.csv",
    "meat_interior35.npy", "meat_interior35.csv",
    "phase5_covariance_model.npy", "phase5_covariance_model.csv",
    "phase5_covariance_robust.npy", "phase5_covariance_robust.csv",
    "phase5_correlation_model.csv", "phase5_correlation_robust.csv",
    "phase5_parameter_table.csv",
    "phase5_regional_covariance.csv",
    "phase5_regional_tests.csv",
    "phase5_standard_errors.csv",
)

# Addendum s3 "Do not persist": row-level scores, household identifiers paired
# with scores, row-level score digests, temporary score batches. The largest
# legitimate leading dimension in the persistable set is 47 (the parameter table).
MAX_AGGREGATE_ROWS = N_FULL
_IDENTIFIER_TOKENS = ("idhh", "idorighh", "cluster_id", "household", "hh_id",
                      "row_index", "score_row")

# Fix 5 / review finding 5: MEMBER-SPECIFIC contracts. The closed filename set
# alone did not repair the shape gap -- `write_table` accepted any frame under
# any allowed member, so a mislabelled 5x35 temporary interior-score batch got
# through. Every member now declares its kind and its exact expected shape, so a
# payload can only be written under a member whose contract it actually meets.
#   kind: "matrix" (square, names x names) | "table" (rows x named columns) | "json"
_MEMBER_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "score_aggregate_summary.json": {"kind": "json"},
    "score_sum_free37.csv": {"kind": "table", "rows": N_FREE},
    "meat_free37.npy": {"kind": "matrix", "shape": (N_FREE, N_FREE)},
    "meat_free37.csv": {"kind": "matrix", "shape": (N_FREE, N_FREE)},
    "meat_interior35.npy": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "meat_interior35.csv": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_covariance_model.npy": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_covariance_model.csv": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_covariance_robust.npy": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_covariance_robust.csv": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_correlation_model.csv": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_correlation_robust.csv": {"kind": "matrix", "shape": (N_INTERIOR, N_INTERIOR)},
    "phase5_parameter_table.csv": {"kind": "table", "rows": N_FULL,
                                   "columns": PARAMETER_TABLE_COLUMNS},
    "phase5_regional_covariance.csv": {"kind": "matrix",
                                       "shape": (N_REGIONAL, N_REGIONAL)},
    "phase5_regional_tests.csv": {"kind": "table", "rows": len(NULL_DEFINITIONS)},
    "phase5_standard_errors.csv": {"kind": "table", "rows": N_INTERIOR},
}


class SerializerRefusal(InferenceError):
    """Raised when a serializer is asked to persist non-aggregate content."""

    def __init__(self, message: str):
        super().__init__(message, code="IB-REFUSE")


def assert_aggregate_payload(obj: Any, label: str) -> None:
    """Refuse row-level or id-paired score content BY CONSTRUCTION.

    Addendum s3 / s6 and gate T-23S. The rules are structural, not name-based
    alone, so a mislabelled household-scale array is refused just as firmly as a
    correctly-labelled one:

      * any ndarray or frame whose leading dimension exceeds 47 -- the largest
        legitimate aggregate row count -- is household-scale and refused;
      * any 2-D ndarray with 37 OR 35 columns whose row count does not equal that
        column count is a score block, not the `M_37`/`M_35` aggregate, and is
        refused. Fix 5: the 35-column arm was missing, so a mislabelled 5x35
        temporary interior-score batch was accepted;
      * any frame carrying an identifier-like column is refused, because addendum
        s3 forbids household identifiers paired with scores;
      * non-finite numeric content is refused, in BOTH the ndarray and the
        DataFrame branch. Fix 5: the DataFrame branch previously had no
        finiteness check, so a frame containing NaN was accepted.
    """
    if isinstance(obj, pd.DataFrame):
        if len(obj) > MAX_AGGREGATE_ROWS:
            raise SerializerRefusal(
                f"[IB-REFUSE] {label}: {len(obj)} rows exceeds the aggregate "
                f"maximum {MAX_AGGREGATE_ROWS}; this is household-scale content "
                "and addendum s3 forbids persisting it")
        lowered = {str(c).strip().lower() for c in obj.columns}
        hits = sorted(c for c in lowered if any(t in c for t in _IDENTIFIER_TOKENS))
        if hits:
            raise SerializerRefusal(
                f"[IB-REFUSE] {label}: identifier-like column(s) {hits} present; "
                "addendum s3 forbids persisting household identifiers")
        numeric = obj.select_dtypes(include=[np.number])
        for width in (N_FREE, N_INTERIOR):
            if numeric.shape[1] == width and len(obj) != width:
                raise SerializerRefusal(
                    f"[IB-REFUSE] {label}: {len(obj)} x {width} numeric block is a "
                    "row-level score matrix, not an aggregate")
        if numeric.size and not np.isfinite(numeric.to_numpy(dtype="float64")).all():
            raise SerializerRefusal(
                f"[IB-REFUSE] {label}: non-finite numeric content in a DataFrame")
        return
    arr = np.asarray(obj)
    if arr.dtype.kind in "fiu" and arr.size and not np.isfinite(arr).all():
        raise SerializerRefusal(f"[IB-REFUSE] {label}: non-finite content")
    if arr.ndim >= 1 and arr.shape[0] > MAX_AGGREGATE_ROWS:
        raise SerializerRefusal(
            f"[IB-REFUSE] {label}: leading dimension {arr.shape[0]} exceeds the "
            f"aggregate maximum {MAX_AGGREGATE_ROWS}; this is household-scale "
            "content and addendum s3 forbids persisting it")
    for width in (N_FREE, N_INTERIOR):
        if arr.ndim == 2 and arr.shape[1] == width and arr.shape[0] != width:
            raise SerializerRefusal(
                f"[IB-REFUSE] {label}: {arr.shape} is a row-level score block, not "
                f"the {width}x{width} aggregate")


def assert_member_contract(member: str, obj: Any, kind: str) -> None:
    """Enforce the MEMBER-SPECIFIC type/shape contract (Fix 5).

    The closed filename set fixes *which* names may be written; this fixes *what*
    may be written under each. A payload that satisfies the generic aggregate
    rules but not the contract of the member it is being filed under is refused.
    """
    contract = _MEMBER_CONTRACTS.get(member)
    if contract is None:
        raise SerializerRefusal(
            f"[IB-REFUSE] {member!r} has no declared member contract")
    if contract["kind"] != kind:
        raise SerializerRefusal(
            f"[IB-REFUSE] {member!r} is declared kind {contract['kind']!r} but was "
            f"written as {kind!r}")
    if kind == "matrix":
        arr = np.asarray(obj)
        if arr.shape != contract["shape"]:
            raise SerializerRefusal(
                f"[IB-REFUSE] {member!r} requires shape {contract['shape']}, got "
                f"{arr.shape}")
        if arr.shape[0] != arr.shape[1]:
            raise SerializerRefusal(
                f"[IB-REFUSE] {member!r} must be square, got {arr.shape}")
    elif kind == "table":
        if not isinstance(obj, pd.DataFrame):
            raise SerializerRefusal(
                f"[IB-REFUSE] {member!r} requires a DataFrame, got "
                f"{type(obj).__name__}")
        if "rows" in contract and len(obj) != contract["rows"]:
            raise SerializerRefusal(
                f"[IB-REFUSE] {member!r} requires exactly {contract['rows']} rows, "
                f"got {len(obj)}")
        if "columns" in contract and list(obj.columns) != list(contract["columns"]):
            raise SerializerRefusal(
                f"[IB-REFUSE] {member!r} requires the exact column sequence "
                f"{list(contract['columns'])}, got {list(obj.columns)}")


def _target(out_dir: Path, member: str) -> Path:
    if member not in AGGREGATE_ARTIFACTS:
        raise SerializerRefusal(
            f"[IB-REFUSE] {member!r} is not in the closed aggregate artifact set; "
            "the persistable set is fixed by addendum s3")
    return Path(out_dir) / member


@dataclass(frozen=True)
class ArtifactRecord:
    """What a serializer wrote, plus its ENCLOSING-OBJECT metadata (Fix 4).

    `inference_grade` rides here rather than inside any artifact's own schema, so
    the fixed 13-column parameter table is untouched while a subset-derived
    output can still never be filed without its label. Increment C's manifest
    consumes these records directly.
    """

    member: str
    path: Path
    kind: str
    shape: Tuple[int, ...]
    sha256: str
    inference_grade: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"member": self.member, "path": str(self.path), "kind": self.kind,
                "shape": list(self.shape), "sha256": self.sha256,
                "inference_grade": self.inference_grade,
                "metadata": _jsonable(self.metadata)}


def _require_grade(member: str, inference_grade: Any) -> None:
    """Validate `inference_grade` BEFORE any filesystem write action.

    Closure B-2 (Review B v2 s7.2). This check previously lived only in
    `_record`, which every writer called AFTER creating its target, so an
    empty-grade `IB-REFUSE` left the destination written. It is now called at
    the top of each writer -- before `mkdir`, before `open`, before any
    temporary file -- so a refusal leaves the destination byte-untouched.
    """
    if not isinstance(inference_grade, str) or not inference_grade.strip():
        raise SerializerRefusal(
            f"[IB-REFUSE] {member!r}: inference_grade is required metadata; a "
            "covariance-derived artifact may not be written unlabelled (R-37a)")


def _record(member: str, path: Path, kind: str, shape: Tuple[int, ...],
            inference_grade: str, metadata: Optional[Dict[str, Any]]
            ) -> ArtifactRecord:
    # defence in depth: the writers validate before writing (`_require_grade`),
    # so this can no longer be the first check to fire
    _require_grade(member, inference_grade)
    return ArtifactRecord(member=member, path=path, kind=kind, shape=shape,
                          sha256=_sha256_file(path),
                          inference_grade=str(inference_grade),
                          metadata=dict(metadata or {}))


def write_matrix(out_dir: Path, member: str, matrix: np.ndarray,
                 names: Sequence[str], *, inference_grade: str,
                 metadata: Optional[Dict[str, Any]] = None) -> ArtifactRecord:
    """Write one aggregate matrix as `.npy` (authoritative) or `.csv` (rendering).

    Closure B-2: every refusal condition -- member, grade, payload, contract,
    names -- is evaluated before the first filesystem write action.
    """
    path = _target(out_dir, member)
    _require_grade(member, inference_grade)
    assert_aggregate_payload(matrix, member)
    assert_member_contract(member, matrix, "matrix")
    arr = np.asarray(matrix)
    if len(names) != arr.shape[0]:
        raise SerializerRefusal(
            f"[IB-REFUSE] {member!r}: {len(names)} names supplied for a "
            f"{arr.shape} matrix")
    path.parent.mkdir(parents=True, exist_ok=True)
    if member.endswith(".npy"):
        np.save(path, np.ascontiguousarray(arr, dtype=np.float64), allow_pickle=False)
    else:
        frame = pd.DataFrame(arr, index=list(names), columns=list(names))
        assert_aggregate_payload(frame.reset_index(drop=True), member)
        frame.to_csv(path, float_format="%.17g")
    return _record(member, path, "matrix", tuple(int(v) for v in arr.shape),
                   inference_grade, metadata)


def write_table(out_dir: Path, member: str, frame: pd.DataFrame, *,
                inference_grade: str,
                metadata: Optional[Dict[str, Any]] = None) -> ArtifactRecord:
    """Write one aggregate table under its member-specific contract.

    Closure B-2: all refusal conditions are evaluated before any write action.
    """
    path = _target(out_dir, member)
    _require_grade(member, inference_grade)
    assert_aggregate_payload(frame, member)
    assert_member_contract(member, frame, "table")
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.17g")
    merged = {**dict(frame.attrs), **dict(metadata or {})}
    return _record(member, path, "table", (len(frame), len(frame.columns)),
                   inference_grade, merged)


def write_score_aggregate_summary(out_dir: Path, stream_result, *,
                                  inference_grade: str) -> ArtifactRecord:
    """`score_aggregate_summary.json` exactly per addendum s3.

    Carries the household count, dimension, canonical-order fingerprint, global
    score-stream SHA-256, the aggregate score vector, scalar norm/moment
    diagnostics, the batch size actually used, and the dtype/byte-order contract.
    It carries no row-level score and no identifier.

    `inference_grade` is a required keyword and is written INTO the JSON, so the
    one artifact with a free-form schema also carries the label.

    Closure B-3 (Review B v2 s7.3). This function previously accepted an
    unrestricted `extra: Optional[Dict[str, Any]]` mapping that was merged into
    the payload after construction. `extra={'temporary_scores_free37':
    np.zeros((5,37)).tolist()}` therefore persisted a complete row-level score
    block, and `extra={'inference_grade': ''}` overwrote a protected field while
    the returned record still reported the true grade. The channel is REMOVED,
    which is the preferred baseline of the proportionality decision s3 B-3:
    Increment C has declared no accepted need for named scalar extensions.

    Every payload field is now constructed exclusively here from
    `stream_result` and `inference_grade`. There is no caller-supplied content
    path into this artifact at all, so no allowlist, type screen or
    protected-field collision check is needed -- the surface is closed by
    construction rather than by filtering.
    """
    _require_grade("score_aggregate_summary.json", inference_grade)
    vec = np.asarray(stream_result.score_sum_free37, dtype=np.float64)
    assert_aggregate_payload(vec, "score_sum_free37")
    assert_member_contract("score_aggregate_summary.json", None, "json")
    payload = {
        "n_households": int(stream_result.n_households),
        "dim_free": int(stream_result.dim_free),
        "dim_interior": int(stream_result.dim_interior),
        "canonical_order_sha256": stream_result.order_sha256,
        "score_stream_sha256": stream_result.score_stream_sha256,
        "free_names_sha256": stream_result.free_names_sha256,
        "interior_names_sha256": stream_result.interior_names_sha256,
        "score_sum_free37": vec.tolist(),
        "scalar_diagnostics": _jsonable(dict(stream_result.diagnostics)),
        "batch_size_used": int(stream_result.batch_size),
        "n_batches": int(stream_result.n_batches),
        "dtype": stream_result.dtype,
        "byte_order": stream_result.byte_order,
        "idhh_encoding": stream_result.idhh_encoding,
        "bytes_per_household": int(stream_result.bytes_per_household),
        "inference_grade": str(inference_grade),
    }
    path = _target(out_dir, "score_aggregate_summary.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return _record("score_aggregate_summary.json", path, "json",
                   (len(payload),), inference_grade,
                   {"n_households": payload["n_households"]})


__all__ = [
    "ACCEPTED_THETA_SHA256", "ACTIVE_BOUND_NAMES", "AGGREGATE_ARTIFACTS",
    "ArtifactRecord", "Bread", "CHI2_CRIT_95", "CORRECTION_C", "Covariances",
    "GateResult", "InferenceError", "KAPPA_BE_CERTIFIED", "MNL_ROOT",
    "NULL_DEFINITIONS", "N_FREE", "N_FULL", "N_INTERIOR", "N_REGIONAL",
    "PARAMETER_TABLE_COLUMNS", "PIN_TABLE_FOOTNOTE", "ParameterTable",
    "REGIONAL_BLOCK_NAMES", "RegionalTests", "SerializerRefusal", "Z_975",
    "accepted_theta_sha256", "assert_aggregate_payload", "assert_member_contract",
    "build_covariances", "build_parameter_table",
    "correlation_from_covariance", "gate_T5_bread_provenance",
    "gate_T6_bread_integrity", "gate_T7_meat_validity", "gate_T8_solve_stability",
    "gate_T9_covariance_validity", "gate_T10_correction_scalar",
    "gate_T14_regional", "gate_T17_fingerprints", "gate_T18_valid_correlations",
    "gate_T19_stationarity", "gate_T22_numerical_kkt", "gating_failures",
    "AcceptedGradients", "load_accepted_gradients",
    "load_bread", "null_selector", "regional_selector", "run_regional_tests",
    "validate_parameter_table", "warning_W1_ratio", "warning_W2_regional_spectrum",
    "warning_W3_effective_rank", "warning_W4_near_boundary", "warning_W5_centring",
    "write_matrix", "write_score_aggregate_summary", "write_table",
]
