"""
Empirical occupation (loc4) draw for B-pool W1 wage model.

Each working alternative draws an occupation category (loc4 in {1,2,3,4})
from the empirical distribution within the stratum (dgn × educ3).

Cells with loc4 = -2 (working but occupation unknown) are excluded from the
frequency table and assigned to the most common stratum cell (loc4=1 for
low-educated; see _FALLBACK below). Cells with loc4 = -1 are non-workers
and never enter this draw.

The log-proposal contribution from the occupation draw is:
    log_q_Occ = log(p_{loc4=k | dgn, educ3})

This is the HP2-required term: draw loc4 from Categorical(p), then record
the log-probability of the drawn outcome.

Empirical frequencies are hard-coded from the P3a GSURv2 pooled observed
row (draw==0) distribution. They must be re-derived if the sample changes.
Source: fr_p3a_gsurv2_estimation_ready__singles.parquet, observed rows,
workers (working==1 and loc4>0), stratified by (dgn, educ3).

Stratum key: (dgn: 0=female,1=male, educ3: 0=low,1=mid,2=high).
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Empirical frequency table (dgn, educ3) -> array of length 4 (loc4=1..4)
# Derived from P3a GSURv2 pooled observed rows (working==1, loc4 in 1..4)
# ---------------------------------------------------------------------------
_FREQ: dict[tuple[int, int], np.ndarray] = {
    #       loc4:  1          2          3          4
    (0, 0): np.array([0.576687, 0.217791, 0.122699, 0.082822]),
    (0, 1): np.array([0.277525, 0.300273, 0.159236, 0.262966]),
    (0, 2): np.array([0.031634, 0.077329, 0.111599, 0.779438]),
    (1, 0): np.array([0.650155, 0.099071, 0.068111, 0.182663]),
    (1, 1): np.array([0.596091, 0.130293, 0.056460, 0.217155]),
    (1, 2): np.array([0.098259, 0.053483, 0.037313, 0.810945]),
}
LOC4_VALUES: np.ndarray = np.array([1, 2, 3, 4], dtype=np.int32)

# Fallback for any stratum not covered (should not occur in P3a)
_FALLBACK: np.ndarray = np.array([0.40, 0.25, 0.15, 0.20])


def _get_freq(dgn: int, educ3: int) -> np.ndarray:
    key = (int(dgn), int(educ3))
    p = _FREQ.get(key, _FALLBACK).copy()
    p /= p.sum()  # renormalize to absorb float rounding
    return p


def draw_loc4(
    dgn: np.ndarray,
    educ3: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw occupation (loc4) for n working alternatives.

    Parameters
    ----------
    dgn : ndarray of int (0=female, 1=male), shape (n,)
    educ3 : ndarray of int (0/1/2), shape (n,)
    rng : numpy Generator

    Returns
    -------
    loc4 : ndarray of int32, shape (n,), values in {1,2,3,4}
    log_q_Occ : ndarray of float64, shape (n,)
        log of the drawn occupation's empirical probability.
    """
    dgn = np.asarray(dgn, dtype=int)
    educ3 = np.asarray(educ3, dtype=int)
    n = len(dgn)
    loc4_out = np.empty(n, dtype=np.int32)
    log_q_out = np.empty(n, dtype=np.float64)

    for stratum_key in set(zip(dgn.tolist(), educ3.tolist())):
        d, e = stratum_key
        mask = (dgn == d) & (educ3 == e)
        n_k = int(mask.sum())
        if n_k == 0:
            continue
        probs = _get_freq(d, e)
        drawn_idx = rng.choice(4, size=n_k, p=probs)
        loc4_out[mask] = LOC4_VALUES[drawn_idx]
        log_q_out[mask] = np.log(probs[drawn_idx])

    return loc4_out, log_q_out


def log_q_loc4(
    loc4: np.ndarray,
    dgn: np.ndarray,
    educ3: np.ndarray,
) -> np.ndarray:
    """Evaluate log(p_{loc4 | dgn, educ3}) for given loc4 assignments.

    Used for lockstep verification.
    """
    loc4 = np.asarray(loc4, dtype=int)
    dgn = np.asarray(dgn, dtype=int)
    educ3 = np.asarray(educ3, dtype=int)
    n = len(loc4)
    log_q = np.empty(n, dtype=np.float64)
    for stratum_key in set(zip(dgn.tolist(), educ3.tolist())):
        d, e = stratum_key
        mask = (dgn == d) & (educ3 == e)
        if not mask.any():
            continue
        probs = _get_freq(d, e)
        idx = loc4[mask] - 1  # loc4=1..4 -> index 0..3
        idx = np.clip(idx, 0, 3)
        log_q[mask] = np.log(probs[idx])
    return log_q


# Exported frequency table for verification report
FREQ_TABLE: dict[tuple[int, int], np.ndarray] = _FREQ
