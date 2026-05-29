"""Unit test for recovery_test.py G3b/cov verdict path (work item: cov-poison fix).

Constructs synthetic Hessians (PD, near-collinear, and non-PD) and verifies the
cov/eig/verdict logic from recovery_test._gates_and_report produces:
  - PD + low |corr|         -> "SEPARATELY IDENTIFIED"
  - PD + |corr| > 0.9       -> "NEAR-COLLINEAR at ..."
  - non-PD (negative eig)   -> "NON-IDENTIFIED — Hessian non-PD..." with loaders named

Replicates the verdict-computation block from recovery_test.py so a future change
to the script must update either the script or this test (intentional duplication
as a regression guard, kept small to avoid drift).
"""
from __future__ import annotations
import numpy as np


def _verdict_from_hessian(H, pnames, mkt_pairs=None):
    """Mirror of the verdict-construction logic in recovery_test._gates_and_report.

    mkt_pairs: optional list of (name_a, name_b) for the G3b correlation probe.
    Returns dict with keys: pd_ok, min_eig, bad_dirs, worst_corr, verdict_str.
    """
    H = 0.5 * (H + H.T)
    eig_w, eig_v = np.linalg.eigh(H)
    pd_ok = bool(np.all(eig_w > 0))
    if pd_ok:
        cov = np.linalg.inv(H)
    else:
        cov = np.linalg.pinv(H, hermitian=True, rcond=1e-10)

    loading_thresh = 0.20
    bad_dirs = []
    for k in range(len(eig_w)):
        if eig_w[k] <= 0:
            v = eig_v[:, k]
            loaders = sorted(
                ((pnames[i], float(abs(v[i]))) for i in range(len(v)) if abs(v[i]) > loading_thresh),
                key=lambda kv: -kv[1])
            bad_dirs.append((float(eig_w[k]), loaders))

    worst = (np.nan, None)
    if mkt_pairs:
        corrs = []
        for a, b in mkt_pairs:
            ia, ib = pnames.index(a), pnames.index(b)
            if cov[ia, ia] > 0 and cov[ib, ib] > 0:
                c = float(cov[ia, ib] / np.sqrt(cov[ia, ia] * cov[ib, ib]))
                corrs.append((abs(c), f"{a}|{b}"))
        if corrs:
            worst = max(corrs)

    if not pd_ok:
        first = bad_dirs[0][1] if bad_dirs and bad_dirs[0][1] else []
        loader_str = (", ".join(f"{n} ({w:.2f})" for n, w in first[:5])
                      if first else "no loadings above threshold")
        verdict_str = (f"NON-IDENTIFIED — Hessian non-PD ({len(bad_dirs)} non-positive "
                       f"eigenvalue(s)); first bad direction loads on: {loader_str}")
    elif np.isfinite(worst[0]) and worst[0] > 0.9:
        verdict_str = f"NEAR-COLLINEAR at {worst[1]} (|corr| = {worst[0]:.3f})"
    else:
        verdict_str = "SEPARATELY IDENTIFIED"

    return dict(pd_ok=pd_ok, min_eig=float(eig_w.min()), bad_dirs=bad_dirs,
                worst_corr=worst, verdict_str=verdict_str)


def test_pd_well_conditioned_verdict_identified():
    pnames = ["a", "b", "c", "d"]
    H = np.diag([1.0, 2.0, 3.0, 4.0])
    out = _verdict_from_hessian(H, pnames, mkt_pairs=[("a", "b"), ("c", "d")])
    assert out["pd_ok"] is True
    assert out["min_eig"] > 0
    assert out["bad_dirs"] == []
    assert out["verdict_str"] == "SEPARATELY IDENTIFIED"


def test_pd_near_collinear_verdict_named_pair():
    # H whose inverse has a high a|b correlation: build cov first, then invert.
    pnames = ["a", "b", "c"]
    rho = 0.97
    cov = np.array([[1.0, rho, 0.0],
                    [rho, 1.0, 0.0],
                    [0.0, 0.0, 1.0]])
    H = np.linalg.inv(cov)
    out = _verdict_from_hessian(H, pnames, mkt_pairs=[("a", "b"), ("a", "c")])
    assert out["pd_ok"] is True
    assert "NEAR-COLLINEAR at a|b" in out["verdict_str"]
    assert abs(out["worst_corr"][0] - rho) < 1e-6


def test_non_pd_verdict_names_loaders_not_separately_identified():
    # Build H = Q diag(eig) Q.T with one negative eigenvalue whose eigenvector
    # loads on params 0 and 1.
    pnames = ["beta_w", "beta_l", "beta_c", "beta_h"]
    Q = np.linalg.qr(np.random.RandomState(0).randn(4, 4))[0]
    # Force the first column of Q (the eigenvector for the negative eigenvalue)
    # to load on params 0 and 1 specifically.
    v_neg = np.array([0.7, 0.7, 0.1, 0.05])
    v_neg = v_neg / np.linalg.norm(v_neg)
    Q[:, 0] = v_neg
    # Re-orthonormalize the remaining columns against v_neg.
    Q[:, 1:], _ = np.linalg.qr(Q[:, 1:] - np.outer(v_neg, v_neg @ Q[:, 1:]))
    eig = np.array([-0.5, 1.0, 2.0, 3.0])
    H = Q @ np.diag(eig) @ Q.T

    out = _verdict_from_hessian(H, pnames, mkt_pairs=None)

    assert out["pd_ok"] is False
    assert out["min_eig"] < 0
    assert len(out["bad_dirs"]) == 1
    # Verdict must NOT be the vacuous "SEPARATELY IDENTIFIED".
    assert "SEPARATELY IDENTIFIED" not in out["verdict_str"]
    assert out["verdict_str"].startswith("NON-IDENTIFIED")
    # Both top loaders must be named.
    assert "beta_w" in out["verdict_str"]
    assert "beta_l" in out["verdict_str"]


def test_non_pd_pinv_finite_diagonal_no_silent_zero():
    # Regression: original code did np.linalg.inv(non-PD) -> negative diag ->
    # clip(diag, 0, None) -> SE=0 -> err/se=NaN -> verdict vacuously "SEPARATELY
    # IDENTIFIED". The fix uses pinv (regularized) and leaves SE=NaN on
    # non-positive directions instead of zeroing.
    pnames = ["a", "b"]
    Q = np.array([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2)
    eig = np.array([-1.0, 2.0])
    H = Q @ np.diag(eig) @ Q.T
    out = _verdict_from_hessian(H, pnames)
    assert out["pd_ok"] is False
    # The verdict change is the key user-visible fix.
    assert "NON-IDENTIFIED" in out["verdict_str"]


if __name__ == "__main__":
    test_pd_well_conditioned_verdict_identified()
    test_pd_near_collinear_verdict_named_pair()
    test_non_pd_verdict_names_loaders_not_separately_identified()
    test_non_pd_pinv_finite_diagonal_no_silent_zero()
    print("OK")
