"""
B-pool singles draw builder.

Sources from: fr_p3a_gsurv2_estimation_ready__singles.parquet
  (provisioning_label = gsurv2_opportunity_year_aligned)

Replaces the current uniform hours + uniform wage draws with:
  - D1 five-mode hours mixture  (hours_mixture_d1.py)
  - W1 occupation-conditional log-normal wages  (pilot_wage_draw.py)
  - Empirical loc4 draw  (occ_draw_empirical.py)

n_draws per household: N_DRAWS = 100 (same as current P3a production)

log_prior formula (per-alternative):
    log_prior = log_q_E + working * (log_q_Occ + log_q_H + log_q_W)

  log_q_E   : log(pi0) for non-employed; log(1-pi0) for working
  log_q_Occ : log p(loc4 | dgn, educ3)  — NEW (was 0 with occ_spec=fixed)
  log_q_H   : log mixture density for drawn hours  — NEW (was -log(65))
  log_q_W   : log-normal density at drawn wage  — NEW (was -log(168))

Chosen row (draw == 0): preserves observed hours / wage / loc4; log_q columns
set to 0 to match the IS identity (the observed choice is the importance anchor).

GSURv2 provenance: gsur column is taken as-is from the source parquet
(already gsurv2_opportunity_year_aligned, verified in stage_m1_meta.json).

Guardrails (D10 / RURO_spec_redesign_decisions_v2.md):
  - No urbanisation added (B2 increment, not this script).
  - No 4-eqn LOC4 wages (B3, not this script).
  - educH stays wage-only — no hours/market block changes.
  - No l*/y* variables introduced.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SCRIPTS = Path(__file__).resolve().parent.parent   # scripts/
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "bpool"))
sys.path.insert(0, str(_SCRIPTS / "pilot"))

from hours_mixture_d1 import draw_hours_d1, D1_SPEC  # noqa: E402
from occ_draw_empirical import draw_loc4, FREQ_TABLE  # noqa: E402
from pilot_wage_draw import draw_pilot_wages          # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_DRAWS = 100
PI0 = 0.10
LOG_PI0 = np.log(PI0)
LOG_1_PI0 = np.log(1.0 - PI0)

from _bpool_paths import bpool_dir, POOLED_DATA_DIR  # noqa: E402

_DATA_DIR = POOLED_DATA_DIR
_MINCER_JSON = (
    Path(_SCRIPTS) / "pilot" / "config" / "pilot_mincer_coefficients_v1.json"
)
# Output goes to EUROMOD-STORAGE/new_data (large parquets off project tree)
_OUT_DIR = bpool_dir()
_SOURCE_STEM = "fr_p3a_gsurv2_estimation_ready__singles"
_OUT_STEM = "fr_p3a_bpool_d1w1__singles"


def _load_mincer() -> dict:
    """Return the full mincer JSON (pilot_wage_draw expects the full payload)."""
    with open(_MINCER_JSON) as f:
        return json.load(f)



def _draw_singles_block(
    df_hh: pd.DataFrame,
    mincer: dict,
    rng: np.random.Generator,
    seed: int,
) -> pd.DataFrame:
    """Draw N_DRAWS alternatives for a single-household block.

    Parameters
    ----------
    df_hh : DataFrame for ONE household (all existing draws; we rebuild from scratch).
    mincer : W1 coefficient dict.
    rng : numpy Generator for occupation + hours + employment draws.
    seed : base seed for wage Halton draws (use idhh-based value for reproducibility).

    Returns
    -------
    DataFrame with N_DRAWS+1 rows (draw=0 is chosen/observed, draw=1..N_DRAWS
    are simulated alternatives).
    """
    # Take observed row (draw==0) as template for household-constant columns
    obs = df_hh[df_hh["draw"] == 0].iloc[0].to_dict()

    dgn = int(obs["dgn"])
    educ3 = int(obs["educ3"])
    educL = float(obs["educL"])
    educH = float(obs["educH"])
    pexp_years = float(obs["pexp_years"])
    pexp_years2 = float(obs["pexp_years2"])
    year_tag = int(obs["year_tag"])

    n_sim = N_DRAWS  # simulated alternatives (draw 1..N_DRAWS)

    # ------------------------------------------------------------------
    # Employment state: pi0 = 0.10
    # ------------------------------------------------------------------
    u_emp = rng.uniform(size=n_sim)
    working_sim = (u_emp >= PI0).astype(np.int8)
    n_working = int(working_sim.sum())

    log_q_E_sim = np.where(working_sim == 1, LOG_1_PI0, LOG_PI0)

    # ------------------------------------------------------------------
    # Occupation draw (working alternatives only) — empirical loc4
    # ------------------------------------------------------------------
    loc4_sim = np.full(n_sim, -1, dtype=np.int32)
    log_q_Occ_sim = np.zeros(n_sim, dtype=np.float64)

    if n_working > 0:
        dgn_arr = np.full(n_working, dgn, dtype=int)
        educ3_arr = np.full(n_working, educ3, dtype=int)
        loc4_w, lq_occ_w = draw_loc4(dgn_arr, educ3_arr, rng)
        loc4_sim[working_sim == 1] = loc4_w
        log_q_Occ_sim[working_sim == 1] = lq_occ_w

    # ------------------------------------------------------------------
    # Hours draw (working alternatives only) — D1 mixture
    # ------------------------------------------------------------------
    hours_sim = np.zeros(n_sim, dtype=np.float64)
    log_q_H_sim = np.zeros(n_sim, dtype=np.float64)

    if n_working > 0:
        h_w, lq_h_w = draw_hours_d1(n_working, rng)
        hours_sim[working_sim == 1] = h_w
        log_q_H_sim[working_sim == 1] = lq_h_w

    # ------------------------------------------------------------------
    # Wage draw (working alternatives only) — W1 log-normal
    # ------------------------------------------------------------------
    wage_sim = np.zeros(n_sim, dtype=np.float64)
    log_q_W_sim = np.zeros(n_sim, dtype=np.float64)

    if n_working > 0:
        loc4_w_arr = loc4_sim[working_sim == 1]
        result = draw_pilot_wages(
            n=n_working,
            educL=np.full(n_working, educL),
            educH=np.full(n_working, educH),
            pexp_years=np.full(n_working, pexp_years),
            pexp_years2=np.full(n_working, pexp_years2),
            loc4=loc4_w_arr,
            year_tag=year_tag,
            mincer_payload=mincer,
            seed=seed,
            draw_method="halton",
        )
        wage_sim[working_sim == 1] = result["wage"]
        log_q_W_sim[working_sim == 1] = result["log_q_wage"]

    # ------------------------------------------------------------------
    # log_prior: log_q_E + working*(log_q_Occ + log_q_H + log_q_W)
    # ------------------------------------------------------------------
    log_prior_sim = log_q_E_sim + working_sim * (
        log_q_Occ_sim + log_q_H_sim + log_q_W_sim
    )

    # ------------------------------------------------------------------
    # Build simulated rows DataFrame
    # ------------------------------------------------------------------
    # Carry all household-constant columns from the observed row
    hh_const_cols = [
        c for c in df_hh.columns
        if c not in {
            "draw", "working", "hours", "wage", "loc4",
            "log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "log_prior",
            "consumption", "ils_dispy", "ils_dispy_em", "ils_dispy_real",
            "log_c", "log_c_norm", "c_norm",
            "working_ft", "working_pt1", "working_pt2", "working_lh",
            "leisure", "l_norm", "log_l", "log_l_norm",
            "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
            "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
            "is_chosen",
        }
    ]

    sim_df = pd.DataFrame(
        {c: [obs[c]] * n_sim for c in hh_const_cols}
    )
    sim_df["draw"] = np.arange(1, n_sim + 1)
    sim_df["working"] = working_sim.astype(np.float64)
    sim_df["hours"] = hours_sim
    sim_df["wage"] = wage_sim
    sim_df["loc4"] = loc4_sim.astype(np.float64)
    sim_df["log_q_E"] = log_q_E_sim
    sim_df["log_q_H"] = log_q_H_sim
    sim_df["log_q_W"] = log_q_W_sim
    sim_df["log_q_Occ"] = log_q_Occ_sim
    sim_df["log_prior"] = log_prior_sim
    sim_df["is_chosen"] = np.int8(0)

    # Derived working category flags (needed by estimator spec)
    # F35 [33.5,36.5) is the reference — NO working_f35 flag.
    # Net flags: pt1, pt2, ft, lh; F35 = reference.
    sim_df["working_ft"]  = ((sim_df["hours"] >= 36.5) & (sim_df["hours"] <= 40.5) & (sim_df["working"] == 1)).astype(np.float64)
    sim_df["working_pt1"] = ((sim_df["hours"] >= 17.5) & (sim_df["hours"] <  21.5) & (sim_df["working"] == 1)).astype(np.float64)
    sim_df["working_pt2"] = ((sim_df["hours"] >= 28.5) & (sim_df["hours"] <  30.5) & (sim_df["working"] == 1)).astype(np.float64)
    sim_df["working_lh"]  = ((sim_df["hours"] >= 44.5) & (sim_df["hours"] <= 70.0) & (sim_df["working"] == 1)).astype(np.float64)

    # ------------------------------------------------------------------
    # Chosen row (draw==0): keep observed values; log_q = 0 (IS anchor)
    # ------------------------------------------------------------------
    obs_row = df_hh[df_hh["draw"] == 0].copy()
    obs_row["log_q_E"] = 0.0
    obs_row["log_q_H"] = 0.0
    obs_row["log_q_W"] = 0.0
    obs_row["log_q_Occ"] = 0.0
    obs_row["log_prior"] = 0.0
    obs_row["is_chosen"] = np.int8(1)

    return pd.concat([obs_row, sim_df], ignore_index=True)


def build_singles(
    source_path: Path | None = None,
    out_path: Path | None = None,
    seed: int = 2026,
) -> Path:
    """Build B-pool singles draws.

    Parameters
    ----------
    source_path : path to fr_p3a_gsurv2_estimation_ready__singles.parquet.
    out_path : output parquet path.
    seed : master seed (used to derive per-household seeds).
    n_workers : parallel workers (uses multiprocessing if > 1).

    Returns
    -------
    Path to output parquet.
    """
    if source_path is None:
        source_path = _DATA_DIR / f"{_SOURCE_STEM}.parquet"
    if out_path is None:
        out_path = _OUT_DIR / f"{_OUT_STEM}.parquet"

    print(f"[build_bpool_singles] Reading {source_path}")
    df = pd.read_parquet(source_path)
    print(f"  Source shape: {df.shape}")

    mincer = _load_mincer()
    print(f"  Mincer loaded: sigma={mincer['wage_model_W1']['sigma']:.6f}")

    # Estimation unit is stacked_hh_uid (unique per year×household in P3a)
    stacked_ids = df["stacked_hh_uid"].unique()
    n_hh = len(stacked_ids)
    print(f"  Stacked HH units: {n_hh}")

    rng = np.random.default_rng(seed)
    hh_seeds = {uid: int(rng.integers(0, 2**31)) for uid in stacked_ids}

    results = []
    for i, uid in enumerate(stacked_ids):
        if i % 500 == 0:
            print(f"  [{i}/{n_hh}] stacked_hh_uid={uid}")
        df_hh = df[df["stacked_hh_uid"] == uid].copy()
        hh_rng = np.random.default_rng(hh_seeds[uid])
        block = _draw_singles_block(df_hh, mincer, hh_rng, seed=hh_seeds[uid])
        results.append(block)

    out_df = pd.concat(results, ignore_index=True)
    print(f"  Output shape: {out_df.shape}")

    # Verify row counts
    expected_rows = n_hh * (N_DRAWS + 1)
    if len(out_df) != expected_rows:
        print(f"  WARNING: expected {expected_rows} rows, got {len(out_df)}")
    else:
        print(f"  Row count check: PASS ({len(out_df)} = {n_hh} HH × {N_DRAWS+1})")

    out_df.to_parquet(out_path, index=False)
    print(f"  Written: {out_path}")
    return out_path


def write_metadata(
    out_path: Path,
    source_path: Path,
    n_hh: int,
    n_draws: int,
    seed: int,
    mincer: dict,
) -> Path:
    """Write draw metadata sidecar JSON."""
    meta = {
        "provisioning_label": "bpool_d1w1_gsurv2_opportunity_year_aligned",
        "gsur_source": "GSURv2_opportunity_year_aligned",
        "gsur_provenance": "Inherited from source parquet (fr_p3a_gsurv2_estimation_ready); provisioning_label=gsurv2_opportunity_year_aligned confirmed in stage_m1_meta.json",
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
        "occ_freq_table_strata": {
            f"dgn{d}_educ3{e}": list(v)
            for (d, e), v in FREQ_TABLE.items()
        },
        "pi0": PI0,
        "log_prior_formula": "log_q_E + working * (log_q_Occ + log_q_H + log_q_W)",
        "log_prior_components": {
            "log_q_E": "log(pi0) if non-employed; log(1-pi0) if working",
            "log_q_Occ": "log p(loc4 | dgn, educ3) — drawn from empirical stratum frequencies",
            "log_q_H": "log(w_k / width_k) for D1 mixture component k",
            "log_q_W": "log-normal density: -log(w) - 0.5*log(2*pi*sigma^2) - (log(w)-mu)^2/(2*sigma^2)",
        },
        "chosen_row_log_q": "0 for all log_q columns (IS anchor: draw==0 is observed choice)",
        "n_draws": n_draws,
        "n_households": n_hh,
        "expected_rows_per_hh": n_draws + 1,
        "expected_total_rows": n_hh * (n_draws + 1),
        "seed": seed,
        "source_file": str(source_path),
        "guardrails": [
            "No urbanisation added (B2 increment only)",
            "No 4-equation LOC4 wages (B3 only)",
            "educH in wage layer only (never in hours/market-opp)",
            "No l*/y* variables (D7 endogeneity wall)",
        ],
        "b_ladder_rung": "B1/B2-level singles (D1 modes + W1 wages on P3a GSURv2 pool)",
    }
    meta_path = out_path.parent / (out_path.stem + "__bpoolmeta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata written: {meta_path}")
    return meta_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build B-pool singles draws (D1+W1)")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    mincer = _load_mincer()
    source = args.source or (_DATA_DIR / f"{_SOURCE_STEM}.parquet")
    out = args.out or (_OUT_DIR / f"{_OUT_STEM}.parquet")

    df_source = pd.read_parquet(source)
    n_hh = df_source["idhh"].nunique()

    out_path = build_singles(source_path=source, out_path=out, seed=args.seed)
    write_metadata(out_path, source, n_hh, N_DRAWS, args.seed, mincer)
    print("Done.")
