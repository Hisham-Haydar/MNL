"""
B-pool couples draw builder — 30×30 product (900 alternatives per household).

Sources from: fr_p3a_gsurv2_estimation_ready__couples.parquet
  (provisioning_label = gsurv2_opportunity_year_aligned)

Product construction:
  1. For each household, draw 30 marginal alternatives per partner
     (male-only draws 1..30, female-only draws 1..30).
  2. Cartesian join on idhh → 900 rows per household.
  3. Chosen: draw_male==0 AND draw_female==0 → draw_joint==0.

Draws per partner:
  - Employment: Bernoulli(pi0=0.10)
  - Occupation (working only): empirical loc4 by stratum (dgn × educ3)
  - Hours (working only): D1 five-mode mixture
  - Wage (working only): W1 occupation-conditional log-normal

log_prior (per partner, per alt):
    log_prior_m = log_q_E_male + working_male*(log_q_Occ_male + log_q_H_male + log_q_W_male)
    log_prior_f = log_q_E_female + working_female*(log_q_Occ_female + log_q_H_female + log_q_W_female)
    log_prior = log_prior_m + log_prior_f   (joint: partners independent)

Chosen row (draw_joint==0): observed values retained; all log_q columns = 0.

GSURv2 provenance: gsur_male, gsur_female taken as-is from source parquet
(already gsurv2_opportunity_year_aligned).

Guardrails (D10 / RURO_spec_redesign_decisions_v2.md):
  - No urbanisation added (B2 increment, not this script).
  - No 4-equation LOC4 wages (B3, not this script).
  - educH stays wage-only.
  - No l*/y* variables introduced.
  - Opposite-sex coupling preserved (dgn_male=1, dgn_female=0 hardcoded).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "bpool"))
sys.path.insert(0, str(_SCRIPTS / "pilot"))

from hours_mixture_d1 import draw_hours_d1, D1_SPEC  # noqa: E402
from occ_draw_empirical import draw_loc4              # noqa: E402
from pilot_wage_draw import draw_pilot_wages          # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRODUCT_SIZE = 30          # marginal alternatives per partner
N_JOINT = PRODUCT_SIZE * PRODUCT_SIZE  # = 900 joint alternatives
PI0 = 0.10
LOG_PI0 = np.log(PI0)
LOG_1_PI0 = np.log(1.0 - PI0)

# In couples, opposite-sex only: head=male (dgn=1), partner=female (dgn=0)
DGN_MALE = 1
DGN_FEMALE = 0

from _bpool_paths import bpool_dir, POOLED_DATA_DIR  # noqa: E402

_DATA_DIR = POOLED_DATA_DIR
_MINCER_JSON = (
    Path(_SCRIPTS) / "pilot" / "config" / "pilot_mincer_coefficients_v1.json"
)
# Output goes to EUROMOD-STORAGE/new_data (large parquets off project tree)
_OUT_DIR = bpool_dir()
_SOURCE_STEM = "fr_p3a_gsurv2_estimation_ready__couples"
_OUT_STEM = "fr_p3a_bpool_d1w1__couples"


def _load_mincer() -> dict:
    """Return the full mincer JSON (pilot_wage_draw expects the full payload)."""
    with open(_MINCER_JSON) as f:
        return json.load(f)


def _draw_partner_marginals(
    n: int,
    dgn: int,
    educ3: int,
    educL: float,
    educH: float,
    pexp_years: float,
    pexp_years2: float,
    year_tag: int,
    mincer: dict,
    rng: np.random.Generator,
    seed: int,
) -> dict:
    """Draw n marginal alternatives for one partner.

    Returns dict of arrays length n:
        working, loc4, hours, wage,
        log_q_E, log_q_Occ, log_q_H, log_q_W, log_prior_partner
    """
    # Employment
    u_emp = rng.uniform(size=n)
    working = (u_emp >= PI0).astype(np.int8)
    n_work = int(working.sum())

    log_q_E = np.where(working == 1, LOG_1_PI0, LOG_PI0)

    # Occupation
    loc4 = np.full(n, -1, dtype=np.int32)
    log_q_Occ = np.zeros(n, dtype=np.float64)
    if n_work > 0:
        dgn_arr = np.full(n_work, dgn, dtype=int)
        educ3_arr = np.full(n_work, educ3, dtype=int)
        loc4[working == 1], log_q_Occ[working == 1] = draw_loc4(dgn_arr, educ3_arr, rng)

    # Hours
    hours = np.zeros(n, dtype=np.float64)
    log_q_H = np.zeros(n, dtype=np.float64)
    if n_work > 0:
        hours[working == 1], log_q_H[working == 1] = draw_hours_d1(n_work, rng)

    # Wage
    wage = np.zeros(n, dtype=np.float64)
    log_q_W = np.zeros(n, dtype=np.float64)
    if n_work > 0:
        res = draw_pilot_wages(
            n=n_work,
            educL=np.full(n_work, educL),
            educH=np.full(n_work, educH),
            pexp_years=np.full(n_work, pexp_years),
            pexp_years2=np.full(n_work, pexp_years2),
            loc4=loc4[working == 1],
            year_tag=year_tag,
            mincer_payload=mincer,
            seed=seed,
            draw_method="halton",
        )
        wage[working == 1] = res["wage"]
        log_q_W[working == 1] = res["log_q_wage"]

    log_prior_partner = log_q_E + working * (log_q_Occ + log_q_H + log_q_W)

    return {
        "working": working,
        "loc4": loc4,
        "hours": hours,
        "wage": wage,
        "log_q_E": log_q_E,
        "log_q_Occ": log_q_Occ,
        "log_q_H": log_q_H,
        "log_q_W": log_q_W,
        "log_prior_partner": log_prior_partner,
    }


def _build_product_block(
    obs: dict,
    mincer: dict,
    rng: np.random.Generator,
    seed: int,
) -> pd.DataFrame:
    """Build 900-alt product for one household."""

    year_tag = int(obs["year_tag"])

    # Male marginals (draws 1..30)
    m = _draw_partner_marginals(
        n=PRODUCT_SIZE,
        dgn=DGN_MALE,
        educ3=int(obs["educ3_male"]),
        educL=float(obs["educL_male"]),
        educH=float(obs["educH_male"]),
        pexp_years=float(obs["pexp_years_male"]),
        pexp_years2=float(obs["pexp_years2_male"]),
        year_tag=year_tag,
        mincer=mincer,
        rng=rng,
        seed=seed,
    )

    # Female marginals (draws 1..30)
    f = _draw_partner_marginals(
        n=PRODUCT_SIZE,
        dgn=DGN_FEMALE,
        educ3=int(obs["educ3_female"]),
        educL=float(obs["educL_female"]),
        educH=float(obs["educH_female"]),
        pexp_years=float(obs["pexp_years_female"]),
        pexp_years2=float(obs["pexp_years2_female"]),
        year_tag=year_tag,
        mincer=mincer,
        rng=rng,
        seed=seed + 1,  # distinct seed for female wage draws
    )

    # Cartesian product: 30×30 = 900
    draw_m_idx = np.repeat(np.arange(PRODUCT_SIZE), PRODUCT_SIZE)  # 0..29, repeated 30 times
    draw_f_idx = np.tile(np.arange(PRODUCT_SIZE), PRODUCT_SIZE)    # 0..29, tiled 30 times

    # draw_male/draw_female: 1-indexed (0 reserved for chosen)
    draw_male = draw_m_idx + 1
    draw_female = draw_f_idx + 1
    draw_joint = PRODUCT_SIZE * draw_m_idx + draw_f_idx  # 0..899

    # --- Simulated product row assembly ---
    # Household-constant columns (not partner-specific, not draw-varying)
    hh_const = {
        "idhh": obs["idhh"],
        "idorighh": obs["idorighh"],
        "cluster_id": obs["cluster_id"],
        "stacked_hh_uid": obs["stacked_hh_uid"],
        "data_year": obs["data_year"],
        "year_tag": obs["year_tag"],
        "year_for_ruro": obs.get("year_for_ruro", obs["data_year"]),
        "year_2015_indicator": obs["year_2015_indicator"],
        "year_2017_indicator": obs["year_2017_indicator"],
        "ruro_group": obs.get("ruro_group", 10),
        "household_type": obs.get("household_type", 2),
        "gsur_male": obs["gsur_male"],
        "gsur_female": obs["gsur_female"],
        "gsur": obs["gsur"],
        # Region dummies (household-constant)
        **{f"reg_nuts1_{r}": obs.get(f"reg_nuts1_{r}", 0) for r in range(1, 9)},
        # Demographics (household-constant)
        "educ3_male": obs["educ3_male"],
        "educ3_female": obs["educ3_female"],
        "educL_male": obs["educL_male"],
        "educH_male": obs["educH_male"],
        "educM_male": obs["educM_male"],
        "educL_female": obs["educL_female"],
        "educH_female": obs["educH_female"],
        "educM_female": obs["educM_female"],
        "pexp_years_male": obs["pexp_years_male"],
        "pexp_years2_male": obs["pexp_years2_male"],
        "pexp_years_female": obs["pexp_years_female"],
        "pexp_years2_female": obs["pexp_years2_female"],
        "age_norm_male": obs["age_norm_male"],
        "age_norm2_male": obs["age_norm2_male"],
        "age_norm_female": obs["age_norm_female"],
        "age_norm2_female": obs["age_norm2_female"],
        "dag_male": obs["dag_male"],
        "dag_female": obs["dag_female"],
        "n_children": obs.get("n_children", 0),
        "num_children_total": obs.get("num_children_total", 0),
        "dwt": obs.get("dwt", 1.0),
        "drgn1": obs.get("drgn1", 1),
        "dgn": obs["dgn"],
    }

    # Build 900-row simulated block
    n_joint = N_JOINT
    sim = {k: np.full(n_joint, v) for k, v in hh_const.items()}

    sim["draw_male"] = draw_male
    sim["draw_female"] = draw_female
    sim["draw_joint"] = draw_joint
    sim["is_chosen_joint"] = np.zeros(n_joint, dtype=np.int8)

    # Male draw-varying columns
    for col, arr in [
        ("working_male", m["working"]),
        ("hours_male", m["hours"]),
        ("wage_male", m["wage"]),
        ("loc4_male", m["loc4"]),
        ("log_q_E_male", m["log_q_E"]),
        ("log_q_Occ_male", m["log_q_Occ"]),
        ("log_q_H_male", m["log_q_H"]),
        ("log_q_W_male", m["log_q_W"]),
        ("log_prior_male", m["log_prior_partner"]),
    ]:
        sim[col] = arr[draw_m_idx]

    # Female draw-varying columns
    for col, arr in [
        ("working_female", f["working"]),
        ("hours_female", f["hours"]),
        ("wage_female", f["wage"]),
        ("loc4_female", f["loc4"]),
        ("log_q_E_female", f["log_q_E"]),
        ("log_q_Occ_female", f["log_q_Occ"]),
        ("log_q_H_female", f["log_q_H"]),
        ("log_q_W_female", f["log_q_W"]),
        ("log_prior_female", f["log_prior_partner"]),
    ]:
        sim[col] = arr[draw_f_idx]

    # Joint log_prior
    sim["log_prior"] = sim["log_prior_male"] + sim["log_prior_female"]

    # Derived working-category flags (needed by estimator spec)
    # F35 [33.5,36.5) is the reference — NO working_f35 flag.
    # Net flags: pt1, pt2, ft, lh; F35 = reference.
    wm = sim["working_male"].astype(float)
    wf = sim["working_female"].astype(float)
    hm = sim["hours_male"]
    hf = sim["hours_female"]
    sim["working_ft_male"]   = ((hm >= 36.5) & (hm <= 40.5) & (wm == 1)).astype(float)
    sim["working_pt1_male"]  = ((hm >= 17.5) & (hm <  21.5) & (wm == 1)).astype(float)
    sim["working_pt2_male"]  = ((hm >= 28.5) & (hm <  30.5) & (wm == 1)).astype(float)
    sim["working_lh_male"]   = ((hm >= 44.5) & (hm <= 70.0) & (wm == 1)).astype(float)
    sim["working_ft_female"]  = ((hf >= 36.5) & (hf <= 40.5) & (wf == 1)).astype(float)
    sim["working_pt1_female"] = ((hf >= 17.5) & (hf <  21.5) & (wf == 1)).astype(float)
    sim["working_pt2_female"] = ((hf >= 28.5) & (hf <  30.5) & (wf == 1)).astype(float)
    sim["working_lh_female"]  = ((hf >= 44.5) & (hf <= 70.0) & (wf == 1)).astype(float)

    # --- Chosen row (draw_male=0, draw_female=0, draw_joint=0) ---
    chosen = {k: np.array([v]) for k, v in hh_const.items()}
    chosen["draw_male"] = np.array([0])
    chosen["draw_female"] = np.array([0])
    chosen["draw_joint"] = np.array([0])
    chosen["is_chosen_joint"] = np.array([1], dtype=np.int8)

    # Observed values for draw-varying columns
    for col in ["working_male", "hours_male", "wage_male", "loc4_male",
                "working_female", "hours_female", "wage_female", "loc4_female"]:
        chosen[col] = np.array([obs[col]])

    # Chosen-row band flags: recompute from the chosen row's OWN hours/working
    # so the chosen row carries the same band+gate as sim_df (lines ~301-308).
    #
    # Why this is needed: the upstream pooled parquet has working_ft/pt1/pt2
    # (suffixed) but does NOT carry working_lh_male/working_lh_female. The
    # original code at this point was `chosen[col] = np.array([obs.get(col, 0.0)])`,
    # which silently defaulted working_lh_* to 0.0 on every chosen couples row
    # — zeroing the LH-band indicator for ~30% of male and ~13% of female chosen
    # workers and driving beta_h_lh to the lower bound in estimation. See docs/
    # France_case/P3a/execution_logs/Bpool/RURO_recovery_test_results_singles_v1.md
    # (LH-sparsity / working_lh construction-bug diagnosis, 2026-05-28).
    #
    # pt1/pt2/ft are recomputed as a GUARD against silent upstream/simulated
    # divergence (see singles builder for the same logic).
    for gender, hours_col, work_col in (("male",   "hours_male",   "working_male"),
                                        ("female", "hours_female", "working_female")):
        hg = float(obs[hours_col]) if hours_col in obs else 0.0
        wg = float(obs[work_col])  if work_col  in obs else 0.0
        ft  = float((hg >= 36.5) and (hg <= 40.5) and (wg == 1.0))
        pt1 = float((hg >= 17.5) and (hg <  21.5) and (wg == 1.0))
        pt2 = float((hg >= 28.5) and (hg <  30.5) and (wg == 1.0))
        lh  = float((hg >= 44.5) and (hg <= 70.0) and (wg == 1.0))
        for col_name, fresh in ((f"working_ft_{gender}",  ft),
                                (f"working_pt1_{gender}", pt1),
                                (f"working_pt2_{gender}", pt2)):
            if col_name in obs:
                up = float(obs[col_name])
                if up != fresh:
                    print(f"  WARN: upstream {col_name}={up} disagrees with fresh "
                          f"recompute={fresh} (using fresh).")
            chosen[col_name] = np.array([fresh])
        chosen[f"working_lh_{gender}"] = np.array([lh])

    # All log_q = 0 on chosen row (IS anchor)
    for col in ["log_q_E_male", "log_q_Occ_male", "log_q_H_male", "log_q_W_male",
                "log_prior_male", "log_q_E_female", "log_q_Occ_female",
                "log_q_H_female", "log_q_W_female", "log_prior_female", "log_prior"]:
        chosen[col] = np.array([0.0])

    chosen_df = pd.DataFrame(chosen)
    sim_df = pd.DataFrame(sim)

    return pd.concat([chosen_df, sim_df], ignore_index=True)


def build_couples(
    source_path: Path | None = None,
    out_path: Path | None = None,
    seed: int = 2026,
) -> Path:
    if source_path is None:
        source_path = _DATA_DIR / f"{_SOURCE_STEM}.parquet"
    if out_path is None:
        out_path = _OUT_DIR / f"{_OUT_STEM}.parquet"

    print(f"[build_bpool_couples] Reading {source_path}")
    df = pd.read_parquet(source_path)
    print(f"  Source shape: {df.shape}")

    mincer = _load_mincer()
    print(f"  Mincer loaded: sigma={mincer['wage_model_W1']['sigma']:.6f}")

    # Use observed rows as household templates
    obs_df = df[df["draw"] == 0].copy()
    n_hh = len(obs_df)
    print(f"  Households: {n_hh}")

    rng = np.random.default_rng(seed)
    # Use stacked_hh_uid as the unique key (idhh repeats across years in P3a)
    hh_seeds = {row["stacked_hh_uid"]: int(rng.integers(0, 2**31)) for _, row in obs_df.iterrows()}

    results = []
    for i, (_, row) in enumerate(obs_df.iterrows()):
        if i % 500 == 0:
            print(f"  [{i}/{n_hh}] stacked_hh_uid={row['stacked_hh_uid']}")
        obs = row.to_dict()
        uid = obs["stacked_hh_uid"]
        hh_rng = np.random.default_rng(hh_seeds[uid])
        block = _build_product_block(obs, mincer, hh_rng, seed=hh_seeds[uid])
        results.append(block)

    out_df = pd.concat(results, ignore_index=True)
    print(f"  Output shape: {out_df.shape}")

    # Verify row counts: (N_JOINT + 1) rows per HH
    expected_rows = n_hh * (N_JOINT + 1)
    if len(out_df) != expected_rows:
        print(f"  WARNING: expected {expected_rows} rows, got {len(out_df)}")
    else:
        print(f"  Row count check: PASS ({len(out_df)} = {n_hh} HH × {N_JOINT+1})")

    out_df.to_parquet(out_path, index=False)
    print(f"  Written: {out_path}")
    return out_path


def write_metadata(
    out_path: Path,
    source_path: Path,
    n_hh: int,
    seed: int,
    mincer: dict,
) -> Path:
    meta = {
        "provisioning_label": "bpool_d1w1_gsurv2_opportunity_year_aligned_couples_product",
        "gsur_source": "GSURv2_opportunity_year_aligned",
        "gsur_provenance": "Inherited from source parquet; provisioning_label=gsurv2_opportunity_year_aligned confirmed in stage_m1_meta.json",
        "product_design": f"{PRODUCT_SIZE}x{PRODUCT_SIZE}={N_JOINT} joint alternatives per household",
        "chosen_row": "draw_male=0, draw_female=0, draw_joint=0 (observed outcome)",
        "hours_spec": "D1_five_mode_mixture",
        "hours_spec_ref": "RURO_spec_redesign_decisions_v2.md §D1",
        "hours_d1_bands": D1_SPEC["modes"],
        "hours_boundary_note": D1_SPEC["boundary_note"],
        "wage_spec": "W1_occupation_conditional_lognormal",
        "wage_model": "W1 (occupation-conditioned log-normal); reference loc4 = 1",
        "calibrated_delta_occ": {
            "delta_occ2": mincer["wage_model_W1"]["coef"]["delta_occ2"],
            "delta_occ3": mincer["wage_model_W1"]["coef"]["delta_occ3"],
            "delta_occ4": mincer["wage_model_W1"]["coef"]["delta_occ4"],
            "status": "calibrated, fixed at draw time, NOT free structural parameters",
        },
        "sigma": mincer["wage_model_W1"]["sigma"],
        "occ_spec": "empirical_draw (dgn x educ3 stratum frequencies from P3a observed rows)",
        "pi0": PI0,
        "log_prior_formula": {
            "per_partner": "log_q_E + working*(log_q_Occ + log_q_H + log_q_W)",
            "joint": "log_prior_male + log_prior_female  (partners drawn independently)",
        },
        "log_prior_components": {
            "log_q_E": "log(pi0) if non-employed; log(1-pi0) if working",
            "log_q_Occ": "log p(loc4 | dgn, educ3)",
            "log_q_H": "log(w_k / width_k) for D1 mixture component k",
            "log_q_W": "log-normal density (lockstep with Halton wage draw)",
        },
        "chosen_row_log_q": "0 for all log_q columns (IS anchor)",
        "dgn_coding": "male=1, female=0 (opposite-sex couples only)",
        "n_hh": n_hh,
        "n_joint_per_hh": N_JOINT,
        "expected_rows_per_hh": N_JOINT + 1,
        "expected_total_rows": n_hh * (N_JOINT + 1),
        "seed": seed,
        "source_file": str(source_path),
        "guardrails": [
            "No urbanisation added (B2 increment only)",
            "No 4-equation LOC4 wages (B3 only)",
            "educH in wage layer only",
            "No l*/y* variables (D7 endogeneity wall)",
            "Opposite-sex coupling preserved",
        ],
        "b_ladder_rung": "B2-level couples product (D1 modes + W1 wages on P3a GSURv2 pool)",
    }
    meta_path = out_path.parent / (out_path.stem + "__bpoolmeta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata written: {meta_path}")
    return meta_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build B-pool couples 900-alt product (D1+W1)")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    mincer = _load_mincer()
    source = args.source or (_DATA_DIR / f"{_SOURCE_STEM}.parquet")
    out = args.out or (_OUT_DIR / f"{_OUT_STEM}.parquet")

    df_source = pd.read_parquet(source)
    n_hh = df_source[df_source["draw"] == 0]["idhh"].nunique()

    out_path = build_couples(source_path=source, out_path=out, seed=args.seed)
    write_metadata(out_path, source, n_hh, args.seed, mincer)
    print("Done.")
