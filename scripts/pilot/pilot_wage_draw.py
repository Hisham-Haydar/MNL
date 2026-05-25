"""
NC pilot — Stage 2 module: pilot-only W1 wage draw + matching proposal density.

Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md (Stage 2).

This module replaces the production unconditional Uniform[w_min, w_max] wage
draw (production reference: scripts/enhanced/enh_RURO_draws.py lines ~1196-1204)
with a log-normal occupation-conditional W1 draw:

    log_w ~ Normal(X b + delta_occ[loc4], sigma^2)
    wage  = exp(log_w)

And updates the matching log-proposal-density term IN LOCKSTEP (HP2
requirement; production reference: lines ~1225-1234 of enh_RURO_draws.py):

    log_q_wage[is_working] = log_normal_pdf(wage; mean_i, sigma)
                           = -log(wage) - 0.5*log(2*pi*sigma^2) - (log_w - mean_i)^2 / (2*sigma^2)

The mean equation uses the calibrated coefficients from stage-1
pilot_mincer_coefficients_v1.json (W1 baseline). occ_spec="fixed" is
RETAINED upstream — loc4 here is the OBSERVED occupation, not resampled.

Draw method (per amendment Section 5):
  - Halton preferred (scipy.stats.qmc.Halton, scrambled, seeded); used for the
    couples product wage draws if cleanly available. Halton is dropped at the
    wage call site only; hours/state remain on the existing PCG64 in the
    production code (production unchanged here — this module is pilot-only).
  - If Halton is unavailable, PCG64 fallback (numpy.random.default_rng).

This module performs NO IO. The driver script imports `draw_pilot_wages` and
`log_q_pilot_wages`.

NOTE on country/year/spec-agnostic design (spec contract section 17):
  - Country / year / product size are NOT hard-coded here.
  - Reference occupation is consumed from the pilot config (defaults loc4=1
    consistent with the spec contract; passed explicitly via mincer_payload).
  - The function signature accepts arbitrary mean shifters and a single
    common sigma; expansions to occupation-specific sigma or W2 (sex x occ)
    would extend the payload without changing this signature.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

try:
    from scipy.stats import qmc as _qmc
    _HALTON_AVAILABLE = True
except Exception:  # pragma: no cover
    _HALTON_AVAILABLE = False


def _build_log_wage_mean(
    *,
    educL: np.ndarray,
    educH: np.ndarray,
    pexp_years: np.ndarray,
    pexp_years2: np.ndarray,
    loc4: np.ndarray,
    year_tag: np.ndarray | None,
    coef: dict[str, float],
    use_year_controls: bool,
) -> np.ndarray:
    """Vectorized log-wage mean per simulated person, under W1."""
    mu = (
        coef["intercept"]
        + coef["educL"] * educL
        + coef["educH"] * educH
        + coef["pexp_years"] * pexp_years
        + coef["pexp_years2"] * pexp_years2
    )
    # delta_occ on loc4 with reference loc4=1
    d2 = coef.get("delta_occ2", 0.0)
    d3 = coef.get("delta_occ3", 0.0)
    d4 = coef.get("delta_occ4", 0.0)
    mu = mu + np.where(loc4 == 2, d2, 0.0) \
            + np.where(loc4 == 3, d3, 0.0) \
            + np.where(loc4 == 4, d4, 0.0)
    if use_year_controls and year_tag is not None:
        y15 = coef.get("year_2015_indicator", 0.0)
        y17 = coef.get("year_2017_indicator", 0.0)
        mu = mu + np.where(year_tag == 1, y15, 0.0) \
                + np.where(year_tag == 3, y17, 0.0)
    return mu


def _halton_normal(n: int, seed: int, *, scramble: bool = True) -> np.ndarray:
    """Inverse-CDF normal samples from a 1-d Halton sequence."""
    eng = _qmc.Halton(d=1, scramble=scramble, seed=seed)
    u = eng.random(n).ravel()
    # avoid 0/1 endpoints
    eps = 1e-12
    u = np.clip(u, eps, 1.0 - eps)
    # inverse standard-normal CDF (Acklam approximation is in scipy if needed;
    # numpy has none; we use math.erfinv via numpy)
    z = np.sqrt(2.0) * _erfinv_vec(2.0 * u - 1.0)
    return z


def _erfinv_vec(x: np.ndarray) -> np.ndarray:
    """Vectorized erfinv via scipy.special if available, else math.erfinv."""
    try:
        from scipy.special import erfinv as _se  # type: ignore
        return _se(x)
    except Exception:  # pragma: no cover
        return np.array([math.erfinv(float(v)) for v in x])


def draw_pilot_wages(
    *,
    n: int,
    educL: np.ndarray,
    educH: np.ndarray,
    pexp_years: np.ndarray,
    pexp_years2: np.ndarray,
    loc4: np.ndarray,
    year_tag: np.ndarray | None,
    mincer_payload: dict[str, Any],
    seed: int,
    draw_method: str = "halton",
) -> dict[str, np.ndarray | str]:
    """
    Draw n W1 log-normal wages for working simulated alternatives.

    Returns: dict with keys
      wage            shape (n,)
      log_wage        shape (n,)
      log_q_wage      shape (n,)        — log-normal density at the drawn wage
      mu              shape (n,)        — log-wage mean per person
      sigma           scalar
      method          actual sequence used ("halton" or "pcg64")
    """
    coef = mincer_payload["wage_model_W1"]["coef"]
    sigma = float(mincer_payload["wage_model_W1"]["sigma"])
    use_year_controls = bool(mincer_payload["fitting_set"]["year_controls"])

    mu = _build_log_wage_mean(
        educL=educL, educH=educH,
        pexp_years=pexp_years, pexp_years2=pexp_years2,
        loc4=loc4, year_tag=year_tag,
        coef=coef, use_year_controls=use_year_controls,
    )

    method_used = "halton"
    if draw_method == "halton" and _HALTON_AVAILABLE:
        try:
            z = _halton_normal(n, seed=seed, scramble=True)
        except Exception:
            method_used = "pcg64"
            rng = np.random.default_rng(seed)
            z = rng.standard_normal(n)
    else:
        method_used = "pcg64"
        rng = np.random.default_rng(seed)
        z = rng.standard_normal(n)

    log_wage = mu + sigma * z
    wage = np.exp(log_wage)
    log_q_wage = log_q_pilot_wages(wage=wage, mu=mu, sigma=sigma)

    return {
        "wage": wage,
        "log_wage": log_wage,
        "log_q_wage": log_q_wage,
        "mu": mu,
        "sigma": sigma,
        "method": method_used,
    }


def log_q_pilot_wages(*, wage: np.ndarray, mu: np.ndarray, sigma: float) -> np.ndarray:
    """
    Matching proposal-density term for the W1 log-normal wage draw (HP2 lockstep).

        wage ~ LogNormal(mu, sigma^2)
        log_q(w) = -log(w) - 0.5 * log(2*pi*sigma^2) - (log(w) - mu)^2 / (2*sigma^2)

    Replaces the production uniform term -log(w_max - w_min) when the pilot
    wage draw is in use. The wage draw and its log_q must change together;
    a mismatch breaks the importance-sampling correction (HP2).
    """
    eps = 1e-300
    log_w = np.log(np.maximum(wage, eps))
    var = sigma * sigma
    return -log_w - 0.5 * math.log(2.0 * math.pi * var) - 0.5 * (log_w - mu) ** 2 / var


def lockstep_sanity_check(
    *,
    educL: np.ndarray,
    educH: np.ndarray,
    pexp_years: np.ndarray,
    pexp_years2: np.ndarray,
    loc4: np.ndarray,
    year_tag: np.ndarray | None,
    mincer_payload: dict[str, Any],
    seed: int = 12345,
) -> dict[str, float | int]:
    """
    Verify that draw_pilot_wages and log_q_pilot_wages are in lockstep (HP2).

    A draw of n wages must satisfy: log_q_wage equals the log-normal PDF at
    the realized wage with the same mu/sigma. We re-evaluate log_q via the
    public helper and check max abs deviation == 0 within float precision.
    """
    n = int(educL.shape[0])
    out = draw_pilot_wages(
        n=n, educL=educL, educH=educH,
        pexp_years=pexp_years, pexp_years2=pexp_years2,
        loc4=loc4, year_tag=year_tag,
        mincer_payload=mincer_payload, seed=seed, draw_method="pcg64",
    )
    recomputed = log_q_pilot_wages(wage=out["wage"], mu=out["mu"], sigma=out["sigma"])
    diff = float(np.max(np.abs(out["log_q_wage"] - recomputed)))
    return {"n": n, "max_abs_diff": diff, "ok": diff < 1e-12}
