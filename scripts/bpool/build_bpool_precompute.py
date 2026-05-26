"""
B-pool EUROMOD precompute builder.

Produces per-year alternative-expanded individual-level long files for EUROMOD repricing.
Each output file is a strict superset of the raw EUROMOD input schema for that year.

Design:
  For each bpool alternative (draw) of each household:
    - Replicate the full HH roster (all persons including children / non-deciders)
    - Non-deciders: all columns held at observed values
    - Deciders: lhw ← drawn hours; yivwg ← drawn wage; yem00/yemxp/yem recomputed
      using the canonical earnings identity from enh_RURO_euromod.py §11 (lines 725-768)

Canonical earnings identity (verbatim from enh_RURO_euromod.py):
    FRANCE_STANDARD_HOURS = 35.0
    WEEKS_PER_MONTH       = 52.0 / 12.0
    regular_hours = min(lhw, 35.0)
    overtime_hours = max(lhw - 35.0, 0.0)
    yem00 = regular_hours * yivwg * WEEKS_PER_MONTH
    yemxp = overtime_hours * yivwg * WEEKS_PER_MONTH
    yem   = yem00 + yemxp                              (asserted)
    non-working (lhw==0): yem00=yemxp=yem=0; yivwg preserved

Do NOT touch: lhw_f, liwwh, liwwh_f, yem_f, yempv (previous-year / flags / ranges).

Per-year output (one file per year, matching that year's own raw input schema):
  U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_precompute__2015__long.parquet  (122 cols + extras)
  U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_precompute__2016__long.parquet  (124 cols + extras)
  U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_precompute__2017__long.parquet  (128 cols + extras)
  U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_precompute__meta.json

Gate checks (from RURO_Bpool_precompute_gate_v1.md §3/§4/§5):
  G1: Every raw input column present per year — hard stop if missing
  G2: idhh/idperson intact; one row per person per alternative
  G3: Full HH roster in every alternative (incl. children, non-deciders)
  G4: Non-decider lhw/yem/yem00/yemxp constant across draws
  G5: Decider lhw varies across draws
  G6: yem == yem00 + yemxp (max residual < 1e-6)
  G7: Parent pointers (idmother/idfather/idpartner) replicated intact

Usage:
    python scripts/bpool/build_bpool_precompute.py [--singles-only] [--couples-only]
    python scripts/bpool/build_bpool_precompute.py --skip-gate   # skip post-build gate
    python scripts/bpool/build_bpool_precompute.py --gate-only   # run gate on existing files

Output location: U:/EUROMOD-STORAGE/new_data/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_SCRIPTS = Path(__file__).resolve().parent.parent
from _bpool_paths import bpool_dir, FR_PARQUETS  # noqa: E402
_BPOOL_DIR = bpool_dir()
_FR_PARQUET = FR_PARQUETS
_BPOOL_SINGLES = _BPOOL_DIR / "fr_p3a_bpool_d1w1__singles.parquet"
_BPOOL_COUPLES = _BPOOL_DIR / "fr_p3a_bpool_d1w1__couples.parquet"

_OUT_STEM = "fr_p3a_bpool_precompute"

# ---------------------------------------------------------------------------
# Canonical constants — verbatim from enh_RURO_euromod.py lines 82-83
# ---------------------------------------------------------------------------
WEEKS_PER_MONTH = 52.0 / 12.0      # = 4.3333...
FRANCE_STANDARD_HOURS = 35.0

# ---------------------------------------------------------------------------
# Per-year raw EUROMOD input schemas (derived from raw FR_20XX_aY.txt headers)
# These are the EXACT column sets each year's EUROMOD system reads.
# Superset assertion checks the long file against these per year.
# ---------------------------------------------------------------------------
_RAW_SCHEMA = {
    2015: [
        'aca','aco','afc','amrrm','amrtn','ate',
        'bch00','bchcc','bched','bchlg','bchot','bchyc',
        'bdi','bed','bfa','bhl','bho','bhoot','bhotn',
        'bsa','bsa00','bsaoa','bsaot','bsuwd','bun','bunct','bunmt','bunmy',
        'dag','dct','dcu','dcz','ddi','ddt','dec','decde','deh','dehde',
        'dew','dey','dgn','dms','dncsy','drg01','drgmd','drgn1','drgn2','drgru','drgur',
        'dsu00','dsu01','dsu02','dwt',
        'e20ps_o','e20pslw_o','e20psmd_o','e20pspo_o',
        'idfather','idhh','idmother','idorighh','idorigperson','idpartner','idperson',
        'kfb','kfbcc','kfbmy','kivho',
        'lcs','les','lfs','lhw','lhw_f','lindi','liwftmy','liwmy','liwmy_f',
        'liwptmy','liwwh','liwwh_f','loc','lowas','lpemy','lse','lunmy','lunmy_f',
        'pdi','pdi00','pdimy','poa','poa00','poamy','psu','psumy',
        'tad','tis','tpr','tscer',
        'xhc','xhcmomi','xhcot','xhcrt','xmp','xpp',
        'yds','ydses_o','yem','yem00','yem_f','yem_hour','yemmy','yempv','yemxp',
        'yivwg','yiy','yot','ypp','ypr','ypt','yse','yse_f','ysemy',
    ],
    2016: [
        'aca','aco','afc','amrrm','amrtn','ate',
        'bch00','bchcc','bched','bchlg','bchot','bchyc',
        'bdi','bed','bfa','bhl','bho','bhoot','bhotn',
        'bsa','bsa00','bsaoa','bsaot','bsuwd','bun','bunct','bunmt','bunmy',
        'dag','dct','dcu','dcz','ddi','ddt','dec','decde','deh','dehde',
        'dew','dey','dgn','dmb','dms','dncsy','drg01','drgmd','drgn1','drgn2','drgru','drgur',
        'dsu00','dsu01','dsu02','dwt',
        'e20ps_o','e20pslw_o','e20psmd_o','e20pspo_o',
        'idfather','idhh','idmother','idorighh','idorigperson','idpartner','idperson',
        'kfb','kfbcc','kfbmy','kivho',
        'lcs','les','lfs','lhw','lhw_f','lindi','liwftmy','liwmy','liwmy_f',
        'liwptmy','liwwh','liwwh_f','loc','lowas','lpemy','lse','lunmy','lunmy_f',
        'pdi','pdi00','pdimy','poa','poa00','poamy','psu','psumy',
        'tad','tis','tscer','twl',
        'xhc','xhcmomi','xhcot','xhcrt','xmp','xpp',
        'yds','ydses_o','yem','yem00','yem_f','yem_hour','yemmy','yempv','yemxp',
        'yivwg','yiy','yot','ypp','ypr','ypt','yptmp','yse','yse_f','ysemy',
    ],
    2017: [
        'aca','aco','afc','amrrm','amrtn','ate',
        'bch00','bchba','bchcc','bched','bchlg','bchot','bchyc',
        'bdi','bed','bfa','bhl','bho','bhoot','bhotn',
        'bsa','bsa00','bsaoa','bsaot','bsawk','bsuwd','bun','bunct','bunmt','bunmy',
        'dag','dct','dcu','dcz','ddi','ddt','dec','decde','deh','dehde',
        'dew','dey','dgn','dmb','dms','dncsy','drg01','drgmd','drgn1','drgn2','drgru','drgur',
        'dsu00','dsu01','dsu02','dwt',
        'e20ps_o','e20pslw_o','e20psmd_o','e20pspo_o',
        'idfather','idhh','idmother','idorighh','idorigperson','idpartner','idperson',
        'kfb','kfbcc','kfbmy','kivho',
        'lcs','les','lfs','lhw','lhw_f','lindi','liwftmy','liwmy','liwmy_f',
        'liwptmy','liwwh','liwwh_f','loc','lowas','lpemy','lse','ltr','lunmy','lunmy_f',
        'pdi','pdi00','pdimy','poa','poa00','poamy','psu','psumy',
        'tad','tis','tscer','twl',
        'xhc','xhcmomi','xhcot','xhcrt','xmp','xpp',
        'yds','ydses_o','yem','yem00','yem_f','yem_hour','yemmy','yempv','yemxp',
        'yivwg','yiy','ymwdt','yot','ypp','ypr','ypt','yptmp','yse','yse_f','ysemy',
    ],
}

# Extra bpool columns that ride alongside EUROMOD input cols (allowed, EUROMOD ignores)
_EXTRA_COLS = [
    "draw", "draw_joint", "draw_male", "draw_female",
    "stacked_hh_uid", "year_tag", "data_year",
    "is_chosen", "is_chosen_joint",
    "hours", "hours_male", "hours_female",
    "wage", "wage_male", "wage_female",
    "loc4", "loc4_male", "loc4_female",
    "working", "working_male", "working_female",
    "log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "log_prior",
    "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male", "log_prior_male",
    "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female", "log_prior_female",
    "working_pt1", "working_pt2", "working_ft", "working_lh",
    "working_pt1_male", "working_pt2_male", "working_ft_male", "working_lh_male",
    "working_pt1_female", "working_pt2_female", "working_ft_female", "working_lh_female",
    "gsur", "gsur_male", "gsur_female",
    "ruro_group", "ruro_decider", "household_type",
    "stacked_hh_uid_bpool",   # join key bookkeeping
]


# ---------------------------------------------------------------------------
# Earnings block — canonical identity from enh_RURO_euromod.py §11 (lines 725-768)
# ---------------------------------------------------------------------------

def _apply_earnings(df: pd.DataFrame, is_decider: np.ndarray) -> pd.DataFrame:
    """Apply canonical French earnings identity to decider rows.

    Reads lhw (final drawn weekly hours) and yivwg (final drawn hourly wage)
    already set on decider rows. Computes yem00/yemxp/yem and asserts identity.
    Also sets yemmy=12/lunmy=0 for working deciders (full-year employment assumption)
    per enh_RURO_euromod.py §12 (YEMMY/LUNMY block).
    Non-deciders: all observed values preserved.
    Non-working deciders (lhw==0): yem00=yemxp=yem=0; yemmy=0; lunmy=12.
    Do NOT touch: lhw_f, liwwh, liwwh_f, yem_f, yempv.
    """
    final_lhw   = pd.to_numeric(df["lhw"],   errors="coerce").fillna(0.0).values
    final_yivwg = pd.to_numeric(df["yivwg"], errors="coerce").fillna(0.0).values

    # Baseline observed values for non-deciders
    baseline_yem00 = pd.to_numeric(df["yem00"] if "yem00" in df.columns else 0.0, errors="coerce").fillna(0.0).values
    baseline_yemxp = pd.to_numeric(df["yemxp"] if "yemxp" in df.columns else 0.0, errors="coerce").fillna(0.0).values
    baseline_yem   = pd.to_numeric(df["yem"]   if "yem"   in df.columns else 0.0, errors="coerce").fillna(0.0).values

    # Canonical split at 35h standard week
    regular_hours  = np.minimum(final_lhw, FRANCE_STANDARD_HOURS)
    overtime_hours = np.maximum(final_lhw - FRANCE_STANDARD_HOURS, 0.0)

    yem00_computed = regular_hours  * final_yivwg * WEEKS_PER_MONTH
    yemxp_computed = overtime_hours * final_yivwg * WEEKS_PER_MONTH
    yem_computed   = yem00_computed + yemxp_computed

    df = df.copy()
    df["yem00"] = np.where(is_decider, yem00_computed, baseline_yem00)
    df["yemxp"] = np.where(is_decider, yemxp_computed, baseline_yemxp)
    df["yem"]   = np.where(is_decider, yem_computed,   baseline_yem)

    # Assert identity yem == yem00 + yemxp
    resid = (df["yem"] - (df["yem00"] + df["yemxp"])).abs()
    max_resid = resid.max()
    n_viol = (resid > 1e-6).sum()
    if n_viol > 0:
        raise ValueError(
            f"ASSERTION FAILED: yem != yem00+yemxp in {n_viol} rows "
            f"(max residual={max_resid:.2e})"
        )

    # Employment duration months — mirrors enh_RURO_euromod.py §12 YEMMY/LUNMY block
    # working = (lhw > 0); full-year employment assumption for every drawn alternative
    is_working_dec = is_decider & (final_lhw > 0)
    is_nonwork_dec = is_decider & (final_lhw == 0)
    if "yemmy" in df.columns:
        baseline_yemmy = df["yemmy"].values.copy()
        df["yemmy"] = np.where(is_working_dec, 12.0,
                      np.where(is_nonwork_dec, 0.0, baseline_yemmy))
    if "lunmy" in df.columns:
        baseline_lunmy = df["lunmy"].values.copy()
        df["lunmy"] = np.where(is_working_dec, 0.0,
                      np.where(is_nonwork_dec, 12.0, baseline_lunmy))

    return df


# ---------------------------------------------------------------------------
# Singles builder — vectorized join
# ---------------------------------------------------------------------------

def _build_singles_year(
    bpool_s: pd.DataFrame,
    roster: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """Expand singles bpool alternatives into full individual-level long file for one year.

    Vectorized: merge all bpool draw rows with full roster on idhh, then apply
    column overrides in bulk. No Python-level row iteration.

    Parameters
    ----------
    bpool_s : bpool singles parquet filtered to this year (all draws 0..100).
    roster  : fr_20YY.parquet (all individuals, all HH).
    year    : 2015 / 2016 / 2017.
    """
    n_hh = bpool_s[bpool_s["draw"] == 0]["idhh"].nunique()
    draws_per_hh = bpool_s["draw"].nunique()  # = 101 (0..100)
    print(f"  [singles {year}] HH={n_hh}, draws per HH={draws_per_hh}, bpool rows={len(bpool_s)}")

    # Columns to carry from bpool into long file
    bpool_carry_cols = [
        "idhh", "stacked_hh_uid", "data_year", "year_tag", "draw",
        "working", "hours", "wage", "loc4",
        "log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "log_prior",
        "working_pt1", "working_pt2", "working_ft", "working_lh",
        "gsur", "ruro_group", "is_chosen",
    ]
    bpool_carry_cols = [c for c in bpool_carry_cols if c in bpool_s.columns]

    draw_df = bpool_s[bpool_carry_cols].copy()
    draw_df["idhh"] = draw_df["idhh"].astype(float)

    # Roster: keep all persons; drop any bpool-carry cols that clash (except idhh)
    roster_year = roster.copy()
    roster_year["idhh"]     = roster_year["idhh"].astype(float)
    roster_year["idperson"] = roster_year["idperson"].astype(float)
    # Drop any columns from roster that will be overwritten by bpool (except idhh itself)
    bpool_extra = [c for c in bpool_carry_cols if c != "idhh" and c in roster_year.columns]
    if bpool_extra:
        roster_year = roster_year.drop(columns=bpool_extra)

    # Vectorized merge: each bpool draw row × full HH roster
    long_df = draw_df.merge(roster_year, on="idhh", how="inner")
    print(f"  [singles {year}] merged rows: {len(long_df)}")

    # Overwrite decider lhw / yivwg:
    #   drawn_hours = hours if working else 0
    #   drawn_wage  = wage (preserved even for non-working, for future use)
    is_decider = (long_df["ruro_decider"] == 1).values
    drawn_hours = np.where(long_df["working"].values == 1, long_df["hours"].values, 0.0)
    drawn_wage  = long_df["wage"].values

    orig_lhw   = long_df["lhw"].values.copy()
    orig_yivwg = long_df["yivwg"].values.copy()
    long_df["lhw"]   = np.where(is_decider, drawn_hours, orig_lhw)
    long_df["yivwg"] = np.where(is_decider, drawn_wage,  orig_yivwg)

    # Apply canonical earnings identity
    long_df = _apply_earnings(long_df, is_decider)

    print(f"  [singles {year}] final long file rows: {len(long_df)}")
    return long_df


# ---------------------------------------------------------------------------
# Couples builder — vectorized join
# ---------------------------------------------------------------------------

def _build_couples_year(
    bpool_c: pd.DataFrame,
    roster: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """Expand couples bpool alternatives into full individual-level long file for one year.

    Vectorized: merge all bpool joint alternatives with full roster on idhh.
    Both decider partners overwritten independently; non-deciders hold observed values.
    """
    n_hh = bpool_c[bpool_c["is_chosen_joint"] == 1]["idhh"].nunique()
    n_alts = bpool_c["draw_joint"].nunique()
    print(f"  [couples {year}] HH={n_hh}, joint alts per HH={n_alts}, bpool rows={len(bpool_c)}")

    bpool_carry_cols = [
        "idhh", "stacked_hh_uid", "data_year", "year_tag",
        "draw_male", "draw_female", "draw_joint", "is_chosen_joint",
        "working_male", "hours_male", "wage_male", "loc4_male",
        "working_female", "hours_female", "wage_female", "loc4_female",
        "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male", "log_prior_male",
        "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female", "log_prior_female",
        "log_prior",
        "working_pt1_male", "working_pt2_male", "working_ft_male", "working_lh_male",
        "working_pt1_female", "working_pt2_female", "working_ft_female", "working_lh_female",
        "gsur", "gsur_male", "gsur_female", "ruro_group",
    ]
    bpool_carry_cols = [c for c in bpool_carry_cols if c in bpool_c.columns]

    draw_df = bpool_c[bpool_carry_cols].copy()
    draw_df["idhh"] = draw_df["idhh"].astype(float)

    roster_year = roster.copy()
    roster_year["idhh"]     = roster_year["idhh"].astype(float)
    roster_year["idperson"] = roster_year["idperson"].astype(float)
    bpool_extra = [c for c in bpool_carry_cols if c != "idhh" and c in roster_year.columns]
    if bpool_extra:
        roster_year = roster_year.drop(columns=bpool_extra)

    # Pre-build decider id lookup for male/female partner per HH
    dec_roster = roster_year[roster_year["ruro_decider"] == 1][["idhh", "idperson", "dgn"]].copy()
    dec_males   = dec_roster[dec_roster["dgn"] == 1][["idhh", "idperson"]].rename(columns={"idperson": "_idp_male"})
    dec_females = dec_roster[dec_roster["dgn"] == 0][["idhh", "idperson"]].rename(columns={"idperson": "_idp_female"})
    decider_ids = dec_males.merge(dec_females, on="idhh", how="inner")

    # Vectorized merge: all joint alternatives × full HH roster
    long_df = draw_df.merge(roster_year, on="idhh", how="inner")
    print(f"  [couples {year}] merged rows: {len(long_df)}")

    # Attach decider idperson tags for vectorized override logic
    long_df = long_df.merge(decider_ids, on="idhh", how="left")

    is_decider_m = (long_df["idperson"] == long_df["_idp_male"]).values
    is_decider_f = (long_df["idperson"] == long_df["_idp_female"]).values
    is_any_decider = is_decider_m | is_decider_f

    # Drawn hours: 0 if non-working
    drawn_hours_m = np.where(long_df["working_male"].values == 1,   long_df["hours_male"].values,   0.0)
    drawn_hours_f = np.where(long_df["working_female"].values == 1, long_df["hours_female"].values, 0.0)
    drawn_wage_m  = long_df["wage_male"].values
    drawn_wage_f  = long_df["wage_female"].values

    orig_lhw   = long_df["lhw"].values.copy()
    orig_yivwg = long_df["yivwg"].values.copy()

    long_df["lhw"]   = np.where(is_decider_m, drawn_hours_m,
                       np.where(is_decider_f, drawn_hours_f, orig_lhw))
    long_df["yivwg"] = np.where(is_decider_m, drawn_wage_m,
                       np.where(is_decider_f, drawn_wage_f, orig_yivwg))

    long_df = _apply_earnings(long_df, is_any_decider)

    # Drop internal join helpers
    long_df = long_df.drop(columns=["_idp_male", "_idp_female"], errors="ignore")

    print(f"  [couples {year}] final long file rows: {len(long_df)}")
    return long_df


# ---------------------------------------------------------------------------
# Gate checks
# ---------------------------------------------------------------------------

def _run_gate(long_df: pd.DataFrame, year: int, mode: str) -> dict:
    """Run all gate checks on a long file. Returns results dict."""
    raw_cols = set(_RAW_SCHEMA[year])
    long_cols = set(long_df.columns)
    results: dict = {}

    # G1 — Superset: every raw column present
    missing = sorted(raw_cols - long_cols)
    results["G1_superset"] = {
        "missing_cols": missing,
        "n_missing": len(missing),
        "pass": len(missing) == 0,
    }
    if missing:
        raise RuntimeError(
            f"HARD STOP [G1]: {len(missing)} raw column(s) missing from {year} long file: "
            f"{missing}"
        )

    # G2 — idhh/idperson intact; one row per person per alternative
    # Singles: key = (draw, idhh, idperson)
    # Couples: draw_joint=0 is reused (chosen row + first simulated cell); use (draw_male, draw_female) instead
    draw_col = "draw" if mode == "singles" else "draw_joint"
    if mode == "singles" and "draw" in long_df.columns:
        dup_count = long_df.groupby(["draw", "idhh", "idperson"]).size()
        n_dups = int((dup_count > 1).sum())
        results["G2_unique_person_per_alt"] = {"n_duplicates": n_dups, "pass": n_dups == 0}
    elif mode == "couples" and "draw_male" in long_df.columns and "draw_female" in long_df.columns:
        dup_count = long_df.groupby(["draw_male", "draw_female", "idhh", "idperson"]).size()
        n_dups = int((dup_count > 1).sum())
        results["G2_unique_person_per_alt"] = {
            "n_duplicates": n_dups, "pass": n_dups == 0,
            "note": "keyed on (draw_male,draw_female) — draw_joint=0 intentionally shared by chosen+first sim cell",
        }
    else:
        results["G2_unique_person_per_alt"] = {"pass": None, "note": f"{draw_col} not found"}

    # G3 — Full HH roster: every alternative has same person count as chosen/observed
    if draw_col in long_df.columns:
        # Expected: each HH has same person count across all alternatives
        persons_per_alt = long_df.groupby(["idhh", draw_col])["idperson"].nunique()
        # Each HH should have constant person count across draws
        hh_counts = persons_per_alt.groupby("idhh").nunique()  # should all be 1
        n_bad_hh = (hh_counts > 1).sum()
        results["G3_roster_complete"] = {
            "n_hh_with_varying_roster": int(n_bad_hh),
            "pass": n_bad_hh == 0,
        }
    else:
        results["G3_roster_complete"] = {"pass": None, "note": f"{draw_col} not found"}

    # G4 — Non-decider lhw/yem/yem00 constant across draws
    if draw_col in long_df.columns and "ruro_decider" in long_df.columns:
        nondec = long_df[long_df["ruro_decider"] != 1]
        g4_results = {}
        for col in ["lhw", "yem", "yem00", "yemxp"]:
            if col not in long_df.columns:
                g4_results[col] = "col_absent"
                continue
            n_varying = nondec.groupby(["idhh", "idperson"])[col].nunique()
            n_bad = (n_varying > 1).sum()
            g4_results[col] = int(n_bad)
        all_pass = all(v == 0 for v in g4_results.values() if isinstance(v, int))
        results["G4_nondecider_constant"] = {"per_col": g4_results, "pass": all_pass}
    else:
        results["G4_nondecider_constant"] = {"pass": None, "note": "ruro_decider or draw col absent"}

    # G5 — Decider lhw varies across draws (at least some HH should have variation)
    if draw_col in long_df.columns and "ruro_decider" in long_df.columns:
        dec = long_df[long_df["ruro_decider"] == 1]
        n_varying_hh = (dec.groupby("idhh")["lhw"].nunique() > 1).sum()
        results["G5_decider_lhw_varies"] = {
            "n_hh_with_variation": int(n_varying_hh),
            "pass": n_varying_hh > 0,
        }
    else:
        results["G5_decider_lhw_varies"] = {"pass": None, "note": "cols absent"}

    # G6 — yem == yem00 + yemxp
    if all(c in long_df.columns for c in ["yem", "yem00", "yemxp"]):
        resid = (long_df["yem"] - (long_df["yem00"] + long_df["yemxp"])).abs()
        n_viol = int((resid > 1e-6).sum())
        results["G6_yem_identity"] = {
            "max_residual": float(resid.max()),
            "n_violations": n_viol,
            "pass": n_viol == 0,
        }
    else:
        results["G6_yem_identity"] = {"pass": None, "note": "yem/yem00/yemxp absent"}

    # G7 — Parent pointers intact
    for col in ["idmother", "idfather", "idpartner"]:
        if col not in long_df.columns:
            results[f"G7_parent_{col}"] = {"pass": None, "note": "col absent"}
            continue
        if draw_col in long_df.columns:
            n_varying = long_df.groupby(["idhh", "idperson"])[col].nunique()
            n_bad = (n_varying > 1).sum()
            results[f"G7_parent_{col}"] = {"n_varying": int(n_bad), "pass": n_bad == 0}
        else:
            results[f"G7_parent_{col}"] = {"pass": None, "note": f"{draw_col} absent"}

    return results


# ---------------------------------------------------------------------------
# Main build + gate loop
# ---------------------------------------------------------------------------

def _print_gate_table(gate_results: dict, year: int, mode: str) -> bool:
    all_pass = True
    print(f"\n  Gate results [{mode} {year}]:")
    for k, v in gate_results.items():
        p = v.get("pass")
        status = "PASS" if p else ("FAIL" if p is False else "SKIP")
        if p is False:
            all_pass = False
        print(f"    {status} {k}: {v}")
    return all_pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Build B-pool EUROMOD precompute long files")
    parser.add_argument("--singles-only", action="store_true")
    parser.add_argument("--couples-only", action="store_true")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--gate-only", action="store_true",
                        help="Run gate checks on existing output files only; do not rebuild")
    parser.add_argument("--year", type=int, choices=[2015, 2016, 2017], default=None,
                        help="Process a single year only")
    args = parser.parse_args()

    run_singles = not args.couples_only
    run_couples = not args.singles_only
    years = [args.year] if args.year else [2015, 2016, 2017]

    summary: dict = {
        "run_start": datetime.now(timezone.utc).isoformat(),
        "mode": "gate_only" if args.gate_only else "build+gate",
        "years": years,
        "earnings_formula": (
            "yem00 = min(lhw,35) * yivwg * (52/12); "
            "yemxp = max(lhw-35,0) * yivwg * (52/12); "
            "yem = yem00 + yemxp  [deciders only; WEEKS_PER_MONTH=52/12=4.3333]"
        ),
        "overwritten_cols": ["lhw", "yivwg", "yem00", "yemxp", "yem"],
        "preserved_cols": ["lhw_f", "liwwh", "liwwh_f", "yem_f", "yempv"],
        "singles": {},
        "couples": {},
    }

    # Load rosters (one per year; reused for both singles and couples)
    print("Loading individual-level rosters...")
    rosters: dict[int, pd.DataFrame] = {}
    for yr in years:
        path = _FR_PARQUET[yr]
        print(f"  Loading {path}")
        rosters[yr] = pd.read_parquet(path)
        print(f"    {rosters[yr].shape}")

    # -----------------------------------------------------------------------
    # Load bpool parquets (needed even for gate-only to get structure)
    # -----------------------------------------------------------------------
    if not args.gate_only:
        print("\nLoading bpool parquets...")
        bpool_s_all = pd.read_parquet(_BPOOL_SINGLES) if run_singles else None
        bpool_c_all = pd.read_parquet(_BPOOL_COUPLES) if run_couples else None

    all_gates_pass = True

    for yr in years:
        roster = rosters[yr]

        # ----------------------------------------------------------------
        # SINGLES
        # ----------------------------------------------------------------
        if run_singles:
            out_path = _BPOOL_DIR / f"{_OUT_STEM}__{yr}__singles__long.parquet"

            if not args.gate_only:
                print(f"\n{'='*60}")
                print(f"SINGLES {yr}")
                print(f"{'='*60}")
                bpool_s = bpool_s_all[bpool_s_all["data_year"] == yr].copy()
                print(f"  bpool rows for {yr}: {len(bpool_s)}")

                long_s = _build_singles_year(bpool_s, roster, yr)

                # Reorder: raw EUROMOD cols first, then extras
                raw_present = [c for c in _RAW_SCHEMA[yr] if c in long_s.columns]
                extra_present = [c for c in long_s.columns if c not in set(_RAW_SCHEMA[yr])]
                long_s = long_s[raw_present + extra_present]

                long_s.to_parquet(out_path, index=False)
                print(f"  Written: {out_path}  shape={long_s.shape}")

            else:
                print(f"\nGate-only: loading {out_path}")
                long_s = pd.read_parquet(out_path)

            if not args.skip_gate:
                print(f"  Running gate checks (singles {yr})...")
                try:
                    gate_s = _run_gate(long_s, yr, "singles")
                    ok = _print_gate_table(gate_s, yr, "singles")
                    all_gates_pass &= ok
                    summary["singles"][yr] = {"gate": gate_s, "all_pass": ok}
                except RuntimeError as e:
                    print(f"  HARD STOP: {e}")
                    summary["singles"][yr] = {"gate": {"error": str(e)}, "all_pass": False}
                    all_gates_pass = False
            else:
                summary["singles"][yr] = {"gate": "skipped"}

        # ----------------------------------------------------------------
        # COUPLES
        # ----------------------------------------------------------------
        if run_couples:
            out_path = _BPOOL_DIR / f"{_OUT_STEM}__{yr}__couples__long.parquet"

            if not args.gate_only:
                print(f"\n{'='*60}")
                print(f"COUPLES {yr}")
                print(f"{'='*60}")
                bpool_c = bpool_c_all[bpool_c_all["data_year"] == yr].copy()
                print(f"  bpool rows for {yr}: {len(bpool_c)}")

                long_c = _build_couples_year(bpool_c, roster, yr)

                raw_present = [c for c in _RAW_SCHEMA[yr] if c in long_c.columns]
                extra_present = [c for c in long_c.columns if c not in set(_RAW_SCHEMA[yr])]
                long_c = long_c[raw_present + extra_present]

                long_c.to_parquet(out_path, index=False)
                print(f"  Written: {out_path}  shape={long_c.shape}")

            else:
                print(f"\nGate-only: loading {out_path}")
                long_c = pd.read_parquet(out_path)

            if not args.skip_gate:
                print(f"  Running gate checks (couples {yr})...")
                try:
                    gate_c = _run_gate(long_c, yr, "couples")
                    ok = _print_gate_table(gate_c, yr, "couples")
                    all_gates_pass &= ok
                    summary["couples"][yr] = {"gate": gate_c, "all_pass": ok}
                except RuntimeError as e:
                    print(f"  HARD STOP: {e}")
                    summary["couples"][yr] = {"gate": {"error": str(e)}, "all_pass": False}
                    all_gates_pass = False
            else:
                summary["couples"][yr] = {"gate": "skipped"}

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    summary["run_end"] = datetime.now(timezone.utc).isoformat()
    summary_path = _BPOOL_DIR / f"{_OUT_STEM}__meta.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nRun summary written: {summary_path}")

    if not args.skip_gate:
        if all_gates_pass:
            print("\nALL GATE CHECKS PASSED — long files are EUROMOD-ready")
        else:
            print("\nSOME GATE CHECKS FAILED — review summary before running EUROMOD")
            sys.exit(1)


if __name__ == "__main__":
    main()
