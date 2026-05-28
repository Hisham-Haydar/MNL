"""
Bring the B-pool priced/estimation-ready track to the engine-ready contract so the
58-param spec (estimation_spec_bpool_p3a_v1.yaml) can be estimated on its OWN design
(900-product couples, 101 singles, working_lh, urbanisation).

Mirrors the Stage-M1 / MNL-prep normalization EXACTLY (enh_RURO_prep_mnl_basic.py):
  TOTAL_LEISURE_HOURS = 80.0 ; DCM_MIN_POSITIVE = 1.0
  leisure        = clip(80 - hours, 1.0)                      (per gender for couples)
  consumption    = ils_dispy_real (singles) ;
                   household joint ils_dispy_real (couples; = sum over tax unit, already
                   summed in build_bpool_estimation_ready)
  c_scale        = mean(consumption)  over ALL rows
  l_scale        = min(positive leisure on CHOSEN rows)        (per gender for couples)
  c_norm         = consumption / c_scale
  l_norm[_g]     = leisure[_g] / l_scale[_g]
  prior          = clip(exp(clip(log_prior, -700, 700)), 1e-16, None)   (density scale)
                   bpool log_prior IS the layered log_q the prep builds; engine uses
                   V = ... - log(prior), so prior = exp(log_prior) reconciles exactly.
  idhh           = stacked_hh_uid (per-alt repeated, HH-constant) ; sorted, monotonic
  year_tag       = {2015:1, 2016:2, 2017:3} from data_year
  is_chosen      = is_chosen (singles) / is_chosen_joint (couples)
  cluster_id     = idorighh

Carries through unchanged: working_lh(+_male/_female), drgur/drgmd/drgru,
year_2015/2017_indicator, reg2..8, gsur(+_male/_female), and all preference covariates.
Preserves the 901/101 product design (no diagonal collapse).

Writes: fr_p3a_bpool_engine_ready__{singles,couples}.parquet + __mnlmeta.json
NO estimation.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

import numpy as np
import pandas as pd

from _bpool_paths import bpool_dir  # noqa: E402

_BP = bpool_dir()
TOTAL_LEISURE_HOURS = 80.0
DCM_MIN_POSITIVE = 1.0
_YEAR_TAG = {2015: 1, 2016: 2, 2017: 3}

_OUT_BASE = _BP / "fr_p3a_bpool_engine_ready"
_OUT_S = Path(str(_OUT_BASE) + "__singles.parquet")
_OUT_C = Path(str(_OUT_BASE) + "__couples.parquet")
_OUT_META = Path(str(_OUT_BASE) + "__mnlmeta.json")


def _prior_from_log_prior(log_prior: pd.Series) -> np.ndarray:
    lp = pd.to_numeric(log_prior, errors="coerce").to_numpy()
    prior = np.exp(np.clip(lp, -700, 700))
    return np.clip(prior, 1e-16, None)


# Squared regressors entered in raw units are badly scaled for the optimizer: their
# gradient is multiplied by the (large) regressor values, so the coefficient's |g|
# dominates |g|max and blocks the convergence test even at the optimum (recovery-test
# diagnosis: beta_w_pexp2 worst, then beta_l_age2_*). Fix: rescale each LINEAR term so its
# SQUARE is O(1-6) — comparable across regressors. Coefficients reinterpret per the scale.
#   pexp_years (0-49) -> /20  => pexp_years2 in [0,~6]   (decades was /10 -> still ~24,
#                                 left pexp2 dominant; /20 standardizes it to age_norm2's scale)
#   age_norm (+/-24)  -> /10  => age_norm2  in [0,~6.4]
# Per-pair scale so pexp can be scaled harder than age.
_SQUARED_PAIRS = [
    # (linear_base, squared_base, scale)
    ("pexp_years",         "pexp_years2",         20.0),
    ("pexp_years_male",    "pexp_years2_male",    20.0),
    ("pexp_years_female",  "pexp_years2_female",  20.0),
    ("age_norm",           "age_norm2",           10.0),
    ("age_norm_male",      "age_norm2_male",      10.0),
    ("age_norm_female",    "age_norm2_female",    10.0),
]


def _rescale_squared_regressors(df: pd.DataFrame) -> pd.DataFrame:
    """Rescale linear terms by their per-pair scale and recompute squares, in place.
    Idempotency guard: only rescale a linear term still in raw-ish units (max|.| > 6)."""
    for lin, sq, _SCALE in _SQUARED_PAIRS:
        if lin not in df.columns:
            continue
        v = pd.to_numeric(df[lin], errors="coerce").fillna(0.0)
        if float(v.abs().max()) > 6.0:   # raw units (decade-scaled would be <=~5)
            df[lin] = v / _SCALE
        if sq in df.columns:
            df[sq] = df[lin] ** 2  # recompute square from the (now-decade) linear term
    return df


def harmonise_singles() -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet(_BP / "fr_p3a_bpool_estimation_ready__singles.parquet")

    # --- leisure (80 - hours, floored) ---
    hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)
    leisure = (TOTAL_LEISURE_HOURS - hours).clip(lower=DCM_MIN_POSITIVE)
    df["leisure"] = leisure

    # --- consumption = real disposable income, floored ---
    cons = pd.to_numeric(df["ils_dispy_real"], errors="coerce").clip(lower=DCM_MIN_POSITIVE)
    df["consumption"] = cons

    # --- normalization (STEP 1 singles formulas) ---
    chosen_mask = df["is_chosen"] == 1
    c_scale = float(df["consumption"].mean())
    if c_scale <= 0:
        raise ValueError(f"Invalid c_scale={c_scale}")
    l_pos = df.loc[chosen_mask, "leisure"]
    l_pos = l_pos[l_pos > 0]
    if len(l_pos) == 0:
        l_pos = df["leisure"][df["leisure"] > 0]
    l_scale = float(l_pos.min()) if len(l_pos) > 0 else 1.0

    df["c_norm"] = df["consumption"] / c_scale
    df["l_norm"] = df["leisure"] / l_scale
    df["log_c_norm"] = np.log(df["c_norm"].clip(lower=DCM_MIN_POSITIVE))
    df["log_l_norm"] = np.log(df["l_norm"].clip(lower=DCM_MIN_POSITIVE))

    # --- prior (density) from carried log_prior ---
    df["prior"] = _prior_from_log_prior(df["log_prior"])

    # --- engine grouping / keys ---
    df["idhh"] = df["stacked_hh_uid"].astype("int64")
    df["year_tag"] = df["data_year"].map(_YEAR_TAG).astype("int64")
    df["cluster_id"] = df["idorighh"]

    df = _rescale_squared_regressors(df)  # wage + leisure conditioning fix (pexp, age)

    df = df.sort_values(["idhh", "draw"]).reset_index(drop=True)

    scaling = {"c_scale": c_scale, "l_scale": l_scale, "n_chosen": int(chosen_mask.sum())}
    return df, scaling


def harmonise_couples() -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet(_BP / "fr_p3a_bpool_estimation_ready__couples.parquet")

    # --- per-gender leisure ---
    for g in ("male", "female"):
        h = pd.to_numeric(df[f"hours_{g}"], errors="coerce").fillna(0.0)
        df[f"leisure_{g}"] = (TOTAL_LEISURE_HOURS - h).clip(lower=DCM_MIN_POSITIVE)

    # --- household consumption = joint real disposable income (already summed over tax
    #     unit in build_bpool_estimation_ready), floored ---
    cons = pd.to_numeric(df["ils_dispy_real"], errors="coerce").clip(lower=DCM_MIN_POSITIVE)
    df["consumption"] = cons

    # --- normalization (STEP 1 couples formulas) ---
    chosen_mask = df["is_chosen_joint"] == 1
    c_scale = float(df["consumption"].mean())
    if c_scale <= 0:
        raise ValueError(f"Invalid c_scale={c_scale}")

    def _lscale(col):
        lc = df.loc[chosen_mask, col]
        lp = lc[lc > 0]
        return float(lp.min()) if len(lp) > 0 else 1.0

    l_male_scale = _lscale("leisure_male")
    l_female_scale = _lscale("leisure_female")

    df["c_norm"] = df["consumption"] / c_scale
    df["log_c_norm"] = np.log(df["c_norm"].clip(lower=DCM_MIN_POSITIVE))
    for g, ls in (("male", l_male_scale), ("female", l_female_scale)):
        df[f"l_norm_{g}"] = df[f"leisure_{g}"] / ls
        df[f"log_l_norm_{g}"] = np.log(df[f"l_norm_{g}"].clip(lower=DCM_MIN_POSITIVE))

    # --- prior (density) from carried joint log_prior ---
    df["prior"] = _prior_from_log_prior(df["log_prior"])

    # --- engine grouping / keys ---
    df["idhh"] = df["stacked_hh_uid"].astype("int64")
    df["year_tag"] = df["data_year"].map(_YEAR_TAG).astype("int64")
    df["cluster_id"] = df["idorighh"]
    # engine reads is_chosen for the chosen-row id on couples too (precompute checks
    # 'is_chosen' or 'chosen'); mirror is_chosen_joint into is_chosen.
    df["is_chosen"] = df["is_chosen_joint"].astype(float)

    df = _rescale_squared_regressors(df)  # wage + leisure conditioning fix (pexp, age)

    df = df.sort_values(["idhh", "draw_joint"]).reset_index(drop=True)

    scaling = {"c_scale": c_scale, "l_male_scale": l_male_scale,
               "l_female_scale": l_female_scale, "n_chosen": int(chosen_mask.sum())}
    return df, scaling


def main() -> None:
    print("Harmonising B-pool track to engine-ready contract...\n")

    print("=== SINGLES ===")
    ds, scs = harmonise_singles()
    print(f"  shape={ds.shape}  c_scale={scs['c_scale']:.2f}  l_scale={scs['l_scale']:.4f}")
    ds.to_parquet(_OUT_S, index=False)
    print(f"  written: {_OUT_S}")

    print("\n=== COUPLES ===")
    dc, scc = harmonise_couples()
    print(f"  shape={dc.shape}  c_scale={scc['c_scale']:.2f}  "
          f"l_male_scale={scc['l_male_scale']:.4f}  l_female_scale={scc['l_female_scale']:.4f}")
    dc.to_parquet(_OUT_C, index=False)
    print(f"  written: {_OUT_C}")

    meta = {
        "source": "fr_p3a_bpool_engine_ready (harmonised from fr_p3a_bpool_estimation_ready__{singles,couples})",
        "produced_by": "scripts/bpool/harmonise_bpool_engine_ready.py",
        "design": "B-pool D1+W1 product (singles 101 alts, couples 900-product + chosen = 901)",
        "normalization_method": "mirrors enh_RURO_prep_mnl_basic.py (TOTAL_LEISURE_HOURS=80, "
                                "leisure=clip(80-hours,1); c_scale=mean(consumption) ALL rows; "
                                "l_scale=min(positive chosen leisure); per-gender for couples)",
        "consumption_source": {
            "singles": "ils_dispy_real",
            "couples": "household joint ils_dispy_real (sum over tax unit)",
        },
        "prior_convention": "prior = clip(exp(clip(log_prior,-700,700)),1e-16,None); engine uses V = ... - log(prior)",
        "squared_regressor_scaling": "Linear terms rescaled to DECADES (/10) and squares "
                            "recomputed: pexp_years(2)[_male/_female] and age_norm(2)[_male/_female]. "
                            "Fixes optimizer conditioning: in raw units pexp_years2 reached ~2400 and "
                            "age_norm2 ~640, so beta_w_pexp2 / beta_l_age2_* dominated |g|max and blocked "
                            "the convergence test at the optimum (recovery-test diagnosis). Interpret "
                            "beta_w_pexp/pexp2 and beta_l_age/age2 as per-decade.",
        "n_draws": {"singles": 101, "couples": 901},
        "normalization": {
            "singles": {"c_scale": scs["c_scale"], "l_scale": scs["l_scale"], "n_chosen": scs["n_chosen"]},
            "couples": {"c_scale": scc["c_scale"], "l_male_scale": scc["l_male_scale"],
                        "l_female_scale": scc["l_female_scale"], "n_chosen": scc["n_chosen"]},
        },
        "row_counts": {"singles": int(len(ds)), "couples": int(len(dc)),
                       "total": int(len(ds) + len(dc))},
        "year_indicators": {
            "year_2015_indicator": "1[year_tag == 1]",
            "year_2017_indicator": "1[year_tag == 3]",
            "note": "year_tag 1=2015, 2=2016, 3=2017; 2016 reference",
        },
        "cluster_key": {"cluster_id_col": "cluster_id", "source_col": "idorighh"},
    }
    with open(_OUT_META, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"\nmnlmeta written: {_OUT_META}")
    print("Done. (No estimation run.)")


if __name__ == "__main__":
    main()
