"""
D1 five-mode hours mixture for B-pool draws.

Economic decision: D1 (RURO_spec_redesign_decisions_v2.md §D1).
Five focal modes derived from the French chosen-hours distribution:

    PT1  ≈ 20 h   band [17.5, 21.5)    width = 4.0
    PT2  ≈ 30 h   band [28.5, 30.5)    width = 2.0
    F35  ≈ 35 h   band [33.5, 36.5)    width = 3.0
    FT   ≈ 39 h   band [36.5, 40.5)    width = 4.0
    LH   ≈ 48 h   band [44.5, 70.0]    width = 25.5

Boundary note: F35 upper edge == FT lower edge == 36.5.
Any draw exactly at 36.5 or above goes to FT.

Background component covers full support [h_min=5, h_max=70] uniformly.
The mixture is a finite mixture of six uniforms (five focal + one background).

Draw mechanics
--------------
1. Sample a component index k ~ Categorical(weights) for each of n draws.
2. Draw hours uniform within that component's band.
3. Compute log_q_H = log(w_k / width_k)   — the mixture density at h.

Density at h:
    q(h) = sum_k  w_k * Uniform(h | a_k, b_k)
           = sum_k  w_k / width_k   * 1_{h in [a_k, b_k)}

Because the mixture components have overlapping support only at the single
point h=36.5 (measure zero), for any drawn h the density collapses to the
single term w_k/width_k of the component it was drawn from.  This is the
HP2-safe approach: log_q_H matches the draw exactly.

Default weights (approximate; calibrated from France chosen-hours distribution):
    PT1=0.15, PT2=0.10, F35=0.24, FT=0.20, LH=0.10, BG=0.21.
Weights sum to 1.0 and can be overridden per stratum.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Band definitions — (name, lo_inclusive, hi_exclusive, default_weight)
# ---------------------------------------------------------------------------
# The background band covers the full support; its contribution to density
# is w_BG / (H_MAX - H_MIN) at any point in [H_MIN, H_MAX].

H_MIN: float = 5.0
H_MAX: float = 70.0

# (lo, hi) are closed/open intervals [lo, hi) except BG and LH which use H_MAX
_BANDS: list[tuple[str, float, float, float]] = [
    ("PT1", 17.5, 21.5, 0.15),
    ("PT2", 28.5, 30.5, 0.10),
    ("F35", 33.5, 36.5, 0.24),
    ("FT",  36.5, 40.5, 0.20),
    ("LH",  44.5, H_MAX, 0.10),
    ("BG",  H_MIN, H_MAX, 0.21),
]

BAND_NAMES: list[str] = [b[0] for b in _BANDS]
BAND_LO: np.ndarray = np.array([b[1] for b in _BANDS])
BAND_HI: np.ndarray = np.array([b[2] for b in _BANDS])
BAND_WIDTHS: np.ndarray = BAND_HI - BAND_LO                  # [4,2,3,4,25.5,65]
DEFAULT_WEIGHTS: np.ndarray = np.array([b[3] for b in _BANDS])


def _validate_weights(weights: np.ndarray | None) -> np.ndarray:
    if weights is None:
        w = DEFAULT_WEIGHTS.copy()
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != (len(_BANDS),):
            raise ValueError(f"weights must have length {len(_BANDS)} (one per component including BG); got {w.shape}")
    if not np.isclose(w.sum(), 1.0, atol=1e-9):
        raise ValueError(f"weights must sum to 1.0; got {w.sum():.6f}")
    if np.any(w < 0):
        raise ValueError("weights must be non-negative")
    return w


def draw_hours_d1(
    n: int,
    rng: np.random.Generator,
    weights: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw n hours values from the D1 five-mode mixture.

    Parameters
    ----------
    n : int
        Number of draws.
    rng : np.random.Generator
        PCG64/Halton-seeded RNG (passed in; not created here for reproducibility).
    weights : array-like of length 6, optional
        Mixture weights [PT1, PT2, F35, FT, LH, BG]. Must sum to 1.
        Defaults to DEFAULT_WEIGHTS.

    Returns
    -------
    hours : ndarray, shape (n,)
        Drawn hours in [H_MIN, H_MAX].
    log_q_H : ndarray, shape (n,)
        Log mixture density at each drawn hours value.
        log_q_H[i] = log(w_k / width_k) where k is the component drawn for i.
    """
    w = _validate_weights(weights)

    # Sample component index for each draw
    k = rng.choice(len(_BANDS), size=n, p=w)

    # Draw uniform within each component's band
    lo = BAND_LO[k]
    hi = BAND_HI[k]
    u = rng.uniform(size=n)
    hours = lo + u * (hi - lo)
    hours = np.clip(hours, H_MIN, H_MAX)

    # log density = log(w_k / width_k) — lockstep with draw
    log_density_k = np.log(w[k] / BAND_WIDTHS[k])
    log_q_H = log_density_k

    return hours.astype(np.float64), log_q_H.astype(np.float64)


def log_q_H_d1(
    hours: np.ndarray,
    weights: np.ndarray | None = None,
) -> np.ndarray:
    """Evaluate D1 mixture log-density at given hours values.

    Used for lockstep verification: must match log_q_H from draw_hours_d1
    when evaluated at the same drawn hours values.

    The mixture density at h is:
        q(h) = sum_k  w_k * I(h in [lo_k, hi_k)) / width_k

    For the lockstep check we sum over ALL components that contain h.
    For draws, each h belongs to exactly one drawn component.
    """
    w = _validate_weights(weights)
    hours = np.asarray(hours, dtype=float)
    q = np.zeros(hours.shape)
    for k, (lo, hi, width) in enumerate(zip(BAND_LO, BAND_HI, BAND_WIDTHS)):
        mask = (hours >= lo) & (hours < hi)
        q[mask] += w[k] / width
    # Handle h == H_MAX exactly (right-closed at top)
    mask_max = hours == H_MAX
    k_last = len(_BANDS) - 1  # BG
    q[mask_max] += w[k_last] / BAND_WIDTHS[k_last]
    # Also LH covers up to H_MAX
    k_lh = BAND_NAMES.index("LH")
    q[mask_max] += w[k_lh] / BAND_WIDTHS[k_lh]
    return np.log(q)


def lockstep_check_d1(
    hours: np.ndarray,
    log_q_H_drawn: np.ndarray,
    component_k: np.ndarray,
    weights: np.ndarray | None = None,
    rtol: float = 1e-6,
) -> dict:
    """Verify that log_q_H from draw matches log(w_k/width_k) for drawn component.

    Parameters
    ----------
    hours : ndarray
    log_q_H_drawn : ndarray
    component_k : ndarray of int
        The component index drawn for each observation.
    weights : optional override.
    rtol : relative tolerance.

    Returns
    -------
    dict with keys: pass (bool), max_abs_err (float), n_mismatch (int).
    """
    w = _validate_weights(weights)
    expected = np.log(w[component_k] / BAND_WIDTHS[component_k])
    err = np.abs(log_q_H_drawn - expected)
    n_mismatch = int(np.sum(err > rtol * np.abs(expected + 1e-30)))
    return {
        "pass": n_mismatch == 0,
        "max_abs_err": float(err.max()),
        "n_mismatch": n_mismatch,
        "n_total": len(hours),
    }


def hours_bin_summary(
    hours_chosen: np.ndarray,
    weights: np.ndarray | None = None,
) -> dict:
    """Bin chosen-hours array into D1 focal bands; return share per band.

    Used in verification report (TASK 4) to confirm 35h and LH modes
    are captured by the focal bins.
    """
    hours = np.asarray(hours_chosen, dtype=float)
    w = _validate_weights(weights)
    n = len(hours)
    summary: dict[str, object] = {}
    in_focal = np.zeros(n, dtype=bool)
    for k, (name, lo, hi, _) in enumerate(zip(BAND_NAMES, BAND_LO, BAND_HI, DEFAULT_WEIGHTS)):
        mask = (hours >= lo) & (hours < hi)
        if name in ("LH",):
            mask = (hours >= lo) & (hours <= H_MAX)
        count = int(mask.sum())
        summary[name] = {
            "band": f"[{lo}, {hi})",
            "n": count,
            "pct": round(100 * count / n, 2) if n > 0 else 0.0,
            "default_weight": float(w[k]),
        }
        if name != "BG":
            in_focal |= mask
    summary["focal_total_pct"] = round(100 * in_focal.sum() / n, 2) if n > 0 else 0.0
    summary["n_total"] = n
    return summary


# ---------------------------------------------------------------------------
# Module-level constants exported for use by bpool draw scripts
# ---------------------------------------------------------------------------
D1_SPEC: dict = {
    "version": "D1",
    "doc": "RURO_spec_redesign_decisions_v2.md §D1",
    "modes": {
        b[0]: {"lo": b[1], "hi": b[2], "default_weight": b[3]}
        for b in _BANDS
    },
    "boundary_note": "F35 hi == FT lo == 36.5; draws at h>=36.5 go to FT when drawn from FT component",
    "H_MIN": H_MIN,
    "H_MAX": H_MAX,
}
