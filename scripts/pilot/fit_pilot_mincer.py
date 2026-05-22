#!/usr/bin/env python
"""
NC pilot — Stage 1: pre-draw Mincer fit.

Authorized by: docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md (Stage 1).
Pilot scope only. Reads production parquets read-only. Writes ONE pilot
config file under scripts/pilot/config/.

Fits two wage models on working observed (draw=0) accepted wages:

    W1:        log w = beta_w0 + beta_w_educL*educL + beta_w_educH*educH
                       + beta_w_pexp*pexp + beta_w_pexp2*pexp^2
                       + delta_occ2*1[loc4=2] + delta_occ3*1[loc4=3] + delta_occ4*1[loc4=4]
                       + (optional) year_2015_indicator + year_2017_indicator
                       + epsilon,   epsilon ~ N(0, sigma^2)

    two-group: log w = beta_w0 + ... (same baseline) + delta_NonInt*1[loc4=4]
                       + (year controls if pooled) + epsilon

Sample: singles + couples, draw=0, loc4 in {1,2,3,4}, wage > 0.
Year set: pooled 2015-2017 with year controls (preferred per amendment).

The delta_occ* / delta_NonInt are CALIBRATED inputs to the draw stage,
NOT free structural parameters. Output tagged with fitting set.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
POOLED = REPO / "Data" / "processed" / "fr" / "pooled"
SINGLES = POOLED / "fr_p3a_gsurv2_estimation_ready__singles.parquet"
COUPLES = POOLED / "fr_p3a_gsurv2_estimation_ready__couples.parquet"
OUT_DIR = REPO / "scripts" / "pilot" / "config"
OUT_FILE = OUT_DIR / "pilot_mincer_coefficients_v1.json"


def _ols(y: np.ndarray, X: np.ndarray, colnames: list[str]) -> dict:
    """OLS with closed-form coefficients + sigma + residual stats. No regularization."""
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    resid = y - yhat
    ssr = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ssr / tss
    sigma2 = ssr / (n - k)
    sigma = float(np.sqrt(sigma2))
    # standard errors
    XtX_inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(XtX_inv) * sigma2)
    coef_dict = {name: float(beta[i]) for i, name in enumerate(colnames)}
    se_dict = {name: float(se[i]) for i, name in enumerate(colnames)}
    return {
        "coef": coef_dict,
        "se": se_dict,
        "sigma": sigma,
        "r2": float(r2),
        "n": int(n),
        "k": int(k),
        "ssr": ssr,
    }


def _load_pooled_working_wages(year_tags: list[int] | None) -> pd.DataFrame:
    """Pool singles + couples observed draw=0 working wages, loc4 in {1..4}, wage>0."""
    cols_singles = ["draw", "loc4", "wage", "educL", "educH",
                    "pexp_years", "pexp_years2", "dgn", "year_tag"]
    s = pd.read_parquet(SINGLES, columns=cols_singles)
    s = s[s["draw"] == 0].copy()
    s["source"] = "singles"

    cols_couples = ["draw", "loc4_male", "loc4_female", "wage_male", "wage_female",
                    "educL_male", "educL_female", "educH_male", "educH_female",
                    "pexp_years_male", "pexp_years_female",
                    "pexp_years2_male", "pexp_years2_female",
                    "year_tag"]
    c = pd.read_parquet(COUPLES, columns=cols_couples)
    c = c[c["draw"] == 0].copy()

    male = pd.DataFrame({
        "loc4": c["loc4_male"], "wage": c["wage_male"],
        "educL": c["educL_male"], "educH": c["educH_male"],
        "pexp_years": c["pexp_years_male"],
        "pexp_years2": c["pexp_years2_male"],
        "dgn": 1.0, "year_tag": c["year_tag"],
    })
    male["source"] = "couples_male"

    female = pd.DataFrame({
        "loc4": c["loc4_female"], "wage": c["wage_female"],
        "educL": c["educL_female"], "educH": c["educH_female"],
        "pexp_years": c["pexp_years_female"],
        "pexp_years2": c["pexp_years2_female"],
        "dgn": 0.0, "year_tag": c["year_tag"],
    })
    female["source"] = "couples_female"

    s_keep = s[["loc4", "wage", "educL", "educH",
                "pexp_years", "pexp_years2", "dgn", "year_tag", "source"]]
    pooled = pd.concat([s_keep, male, female], ignore_index=True)

    pooled = pooled[(pooled["wage"] > 0) &
                    (pooled["loc4"].isin([1, 2, 3, 4]))].copy()
    if year_tags is not None:
        pooled = pooled[pooled["year_tag"].isin(year_tags)].copy()
    pooled["log_wage"] = np.log(pooled["wage"])
    return pooled


def _build_X(df: pd.DataFrame, model: str, pooled_years: bool) -> tuple[np.ndarray, list[str]]:
    n = len(df)
    cols = []
    arrays = []

    # intercept
    arrays.append(np.ones(n)); cols.append("intercept")
    # baseline Mincer covariates
    arrays.append(df["educL"].astype(float).to_numpy()); cols.append("educL")
    arrays.append(df["educH"].astype(float).to_numpy()); cols.append("educH")
    arrays.append(df["pexp_years"].astype(float).to_numpy()); cols.append("pexp_years")
    arrays.append(df["pexp_years2"].astype(float).to_numpy()); cols.append("pexp_years2")

    if model == "W1":
        # loc4 reference = 1
        for k in (2, 3, 4):
            arrays.append((df["loc4"].to_numpy() == k).astype(float))
            cols.append(f"delta_occ{k}")
    elif model == "two_group":
        arrays.append((df["loc4"].to_numpy() == 4).astype(float))
        cols.append("delta_NonInt")
    else:
        raise ValueError(f"Unknown model: {model}")

    if pooled_years:
        arrays.append((df["year_tag"].to_numpy() == 1).astype(float))
        cols.append("year_2015_indicator")
        arrays.append((df["year_tag"].to_numpy() == 3).astype(float))
        cols.append("year_2017_indicator")

    X = np.column_stack(arrays)
    return X, cols


def main(out_file: Path, force_2016: bool = False) -> int:
    print(f"[stage-1] reading pooled working wages from\n  {SINGLES}\n  {COUPLES}")
    year_tags = [2] if force_2016 else [1, 2, 3]
    df = _load_pooled_working_wages(year_tags=year_tags)
    if df.empty:
        print("[stage-1] ERROR: empty pooled sample", file=sys.stderr)
        return 2

    pooled = (not force_2016) and df["year_tag"].nunique() >= 2

    # cell counts for the report / thin-cell flag
    cell_counts = (df.groupby(["loc4", "dgn", "year_tag"]).size()
                     .rename("n").reset_index())
    cell_counts_dict = (cell_counts.assign(
        key=lambda d: d.apply(lambda r: f"loc4={int(r.loc4)}|dgn={int(r.dgn)}|year_tag={int(r.year_tag)}", axis=1)
    )[["key", "n"]].set_index("key")["n"].to_dict())

    thin_cells = {k: int(v) for k, v in cell_counts_dict.items() if v < 50}

    # Fit W1
    yw1 = df["log_wage"].to_numpy()
    Xw1, colsw1 = _build_X(df, "W1", pooled_years=pooled)
    res_w1 = _ols(yw1, Xw1, colsw1)

    # Fit two-group
    Xtg, colstg = _build_X(df, "two_group", pooled_years=pooled)
    res_tg = _ols(yw1, Xtg, colstg)

    payload = {
        "schema_version": "nc_pilot_mincer_v1",
        "produced_by": "scripts/pilot/fit_pilot_mincer.py",
        "produced_at_utc": datetime.now(timezone.utc).isoformat(),
        "authorization": "docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md (Stage 1)",
        "stage": 1,
        "calibrated_not_free": True,
        "accepted_wage_caveat": (
            "Coefficients are fit on accepted (selected-on-employment) wages, "
            "i.e. observed draw=0 working wages with loc4 in {1,2,3,4} and "
            "wage>0. This is a documented approximation to the wage-offer "
            "distribution; offer-vs-accepted selection across loc4 is not "
            "corrected (per spec contract section 14)."
        ),
        "fitting_set": {
            "years": (sorted(df["year_tag"].unique().tolist())),
            "year_labels": {1: 2015, 2: 2016, 3: 2017},
            "year_set_label": "pooled_2015_2017_with_year_controls" if pooled else "2016_only",
            "year_controls": pooled,
            "population": "singles + couples (head + partner)",
            "selection": "draw==0, loc4 in {1,2,3,4}, wage>0",
            "n_total": int(len(df)),
            "n_singles": int((df["source"] == "singles").sum()),
            "n_couples_male": int((df["source"] == "couples_male").sum()),
            "n_couples_female": int((df["source"] == "couples_female").sum()),
            "cell_counts_loc4_dgn_year": cell_counts_dict,
            "thin_cells_lt_50": thin_cells,
            "thin_cell_warning": bool(thin_cells),
        },
        "reference": {
            "loc4_reference": 1,
            "year_tag_reference": 2,
        },
        "wage_model_W1": {
            "specification": (
                "log_w = beta_w0 + beta_w_educL*educL + beta_w_educH*educH "
                "+ beta_w_pexp*pexp_years + beta_w_pexp2*pexp_years2 "
                "+ delta_occ2*1[loc4=2] + delta_occ3*1[loc4=3] + delta_occ4*1[loc4=4] "
                "+ year_2015_indicator + year_2017_indicator (if pooled)"
            ),
            "coef": res_w1["coef"],
            "se": res_w1["se"],
            "sigma": res_w1["sigma"],
            "sigma_note": "common scalar; not occupation-specific (spec contract section 12)",
            "r2": res_w1["r2"],
            "n": res_w1["n"],
            "k": res_w1["k"],
            "calibrated_delta_occ": {
                "delta_occ2": res_w1["coef"]["delta_occ2"],
                "delta_occ3": res_w1["coef"]["delta_occ3"],
                "delta_occ4": res_w1["coef"]["delta_occ4"],
            },
        },
        "wage_model_two_group": {
            "specification": (
                "log_w = beta_w0 + baseline Mincer + delta_NonInt*1[loc4=4] "
                "+ year_2015_indicator + year_2017_indicator (if pooled)"
            ),
            "coef": res_tg["coef"],
            "se": res_tg["se"],
            "sigma": res_tg["sigma"],
            "r2": res_tg["r2"],
            "n": res_tg["n"],
            "k": res_tg["k"],
            "calibrated_delta_NonInt": res_tg["coef"]["delta_NonInt"],
        },
        "use_in_pilot_draw": {
            "selected_model_for_pilot_baseline": "W1",
            "two_group_role": "documented comparison; pilot writes draws under W1 baseline; two-group artifacts produced as parallel variant in Stage 2 record",
            "delta_status": "calibrated and fixed at draw time; not free structural parameters",
        },
        "promotion_debt": [
            "year tags hard-coded as {1:2015, 2:2016, 3:2017} per project convention",
            "loc4 categories hard-coded as {1,2,3,4}",
        ],
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)

    print(f"[stage-1] wrote pilot Mincer coefficients to:\n  {out_file}")
    print(f"[stage-1] W1: n={res_w1['n']}, sigma={res_w1['sigma']:.4f}, R^2={res_w1['r2']:.4f}")
    for nm in ("delta_occ2", "delta_occ3", "delta_occ4"):
        print(f"[stage-1]   {nm} = {res_w1['coef'][nm]:+.4f}  (SE {res_w1['se'][nm]:.4f})")
    print(f"[stage-1] two-group: n={res_tg['n']}, sigma={res_tg['sigma']:.4f}, R^2={res_tg['r2']:.4f}")
    print(f"[stage-1]   delta_NonInt = {res_tg['coef']['delta_NonInt']:+.4f}  (SE {res_tg['se']['delta_NonInt']:.4f})")
    if thin_cells:
        print(f"[stage-1] WARNING: {len(thin_cells)} thin (loc4,dgn,year_tag) cells with n<50")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force-2016", action="store_true",
                    help="Force the 2016-only fallback (do not use pooled years)")
    ap.add_argument("--out", type=Path, default=OUT_FILE)
    args = ap.parse_args()
    sys.exit(main(args.out, force_2016=args.force_2016))
