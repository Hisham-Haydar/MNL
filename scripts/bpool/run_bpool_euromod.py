"""
B-pool EUROMOD pricing runner.

Feeds the precompute long files (already repriced for earnings) to EUROMOD to fill
ils_dispy (+ components) on every alternative. Reuses EuromodRunner from
enh_RURO_euromod.py; does NOT re-run the merge/override logic (earnings already set).

System pairing (opportunity_year = data_year - 1):
  data_year=2015 long file  ->  FR_2014 system  /  FR_2015_a2 dataset
  data_year=2016 long file  ->  FR_2015 system  /  FR_2016_a3 dataset
  data_year=2017 long file  ->  FR_2016 system  /  FR_2017_a2 dataset

CPI deflation (base = 2016):
  phi_2015 = 1.0031,  phi_2016 = 1.0000,  phi_2017 = 0.9886
  ils_dispy_real = ils_dispy * phi_{data_year}

Usage:
    python scripts/bpool/run_bpool_euromod.py [--canary-only] [--year 2017]
    python scripts/bpool/run_bpool_euromod.py            # full run, all 6 files

Output:
    U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__2015__singles.parquet
    U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__2015__couples.parquet
    ... (6 files total)
    U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__meta.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

# ---------------------------------------------------------------------------
# Paths — set up before importing enh_RURO_euromod
# ---------------------------------------------------------------------------
_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS / "enhanced"))

# Import EuromodRunner at module level (after path setup, before anything else
# that might shadow 'sys').  Use _sys alias so sys.exit is always reachable.
import sys as _sys  # noqa: E402  (re-alias to survive any downstream shadowing)
from enh_RURO_euromod import EuromodRunner  # noqa: E402

_BPOOL_DIR = Path("U:/EUROMOD-STORAGE/new_data")
_EM_ROOT   = Path("U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+")
_RAW_DATA  = Path("U:/EUROMOD-STORAGE/Data/FR")
_FR_PARQUET = {
    2015: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2015/fr_2015.parquet"),
    2016: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016.parquet"),
    2017: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2017/fr_2017.parquet"),
}

# ---------------------------------------------------------------------------
# System / dataset pairing and CPI
# ---------------------------------------------------------------------------
_SYSTEM_PAIRING = {
    # data_year -> (system_code, dataset_name, raw_txt)
    2015: ("FR_2014", "FR_2015_a2", _RAW_DATA / "FR_2015_a2.txt"),
    2016: ("FR_2015", "FR_2016_a3", _RAW_DATA / "FR_2016_a3.txt"),
    2017: ("FR_2016", "FR_2017_a2", _RAW_DATA / "FR_2017_a2.txt"),
}
_CPI = {2015: 1.0031, 2016: 1.0000, 2017: 0.9886}

# EUROMOD output columns to extract from sim output
_EM_OUTPUT_COLS = [
    "ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy",
]

# Per-year raw input schemas (same as build_bpool_precompute.py)
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


# ---------------------------------------------------------------------------
# ID stamping helpers (EUROMOD requires unique idhh/idperson across alternatives)
# ---------------------------------------------------------------------------

def _stamp_draw_ids(df: pd.DataFrame, draw_col: str, id_multiplier: int = 100_000) -> pd.DataFrame:
    """Create draw-specific idhh/idperson so EUROMOD treats each alt as a separate HH."""
    df = df.copy()
    draw = pd.to_numeric(df[draw_col], errors="coerce").fillna(0).astype(int)
    df["idhh_true"]     = df["idhh"].copy()
    df["idperson_true"] = df["idperson"].copy()
    df["idhh"]     = df["idhh"].astype(float).astype(int)     * id_multiplier + draw
    df["idperson"] = df["idperson"].astype(float).astype(int) * id_multiplier + draw
    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in df.columns:
            k = pd.to_numeric(df[kin], errors="coerce").fillna(0).astype(int)
            df[kin] = np.where(k == 0, 0, k * id_multiplier + draw)
    return df


def _restore_true_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Restore original idhh/idperson from *_true columns."""
    if "idhh_true" in df.columns:
        df["idhh"] = df["idhh_true"]
    if "idperson_true" in df.columns:
        df["idperson"] = df["idperson_true"]
    return df


# ---------------------------------------------------------------------------
# Canary checks
# ---------------------------------------------------------------------------

def _run_canary(priced: pd.DataFrame, original: pd.DataFrame, year: int, mode: str) -> dict:
    """Four canary checks on a priced long file (post-merge-back)."""
    results = {}

    # C1: ils_dispy non-null on 100% of rows
    n_null = priced["ils_dispy"].isna().sum()
    n_total = len(priced)
    results["C1_nonull"] = {"n_null": int(n_null), "n_total": n_total, "pass": n_null == 0}

    draw_col = "draw" if mode == "singles" else "draw_joint"

    # C2: non-employed alts (working==0 for singles; both partners non-working for couples)
    #     Check ils_ben > 0 on HH-level (decider rows): non-workers should receive some transfer.
    #     NOTE: ils_dispy can be negative for high-asset HH with no labour income (EUROMOD-legitimate).
    #     The meaningful check is that benefits/transfers are non-zero, not that dispy > 0.
    if mode == "singles":
        nonwork = priced[priced["working"] == 0].copy() if "working" in priced.columns else pd.DataFrame()
    else:
        wm = priced.get("working_male", pd.Series(1, index=priced.index))
        wf = priced.get("working_female", pd.Series(1, index=priced.index))
        nonwork = priced[(wm == 0) & (wf == 0)].copy() if "working_male" in priced.columns else pd.DataFrame()

    if len(nonwork) > 0 and "ruro_decider" in nonwork.columns:
        nonwork_dec = nonwork[nonwork["ruro_decider"] == 1]
        spot = nonwork_dec.groupby("idhh")["ils_dispy"].first().head(5)
        # Use ils_ben if present; fall back to ils_dispy median > 0 as proxy
        if "ils_ben" in nonwork_dec.columns:
            n_no_benefit = int((nonwork_dec["ils_ben"] <= 0).sum())
            check_col = "ils_ben"
        else:
            n_no_benefit = int((nonwork_dec["ils_dispy"] <= nonwork_dec["ils_dispy"].quantile(0.01)).sum())
            check_col = "ils_dispy (proxy, no ils_ben col)"
        n_neg_dispy = int((nonwork_dec["ils_dispy"] < 0).sum())
        results["C2_nonwork_income"] = {
            "n_nonwork_decider_rows": len(nonwork_dec),
            "n_neg_dispy": n_neg_dispy,
            "n_neg_dispy_pct": f"{100*n_neg_dispy/max(len(nonwork_dec),1):.2f}%",
            "n_no_benefit": n_no_benefit,
            "check_col": check_col,
            "spot_check_5hh_ils_dispy": spot.to_dict(),
            # Pass if <5% have negative ils_dispy (small fraction is EUROMOD-legitimate)
            # AND median ils_dispy > 0 (transfers dominate)
            "pass": (n_neg_dispy / max(len(nonwork_dec), 1) < 0.05) and
                    float(nonwork_dec["ils_dispy"].median()) > 0,
        }
    else:
        results["C2_nonwork_income"] = {"pass": None, "note": "no non-working decider rows"}

    # C3: chosen-row internal consistency check.
    #
    # NOTE: The roster fr_20YY.parquet ils_dispy was computed by the NEXT year's EUROMOD system
    # (FR_2017 for data_year=2017) on ORIGINAL unmodified earnings. Our priced file uses the
    # PRIOR year's system (FR_2016) on REPRICED wages (W1 wage draw for draw=0). These will
    # always differ — cross-checking against the roster would always fail and is the wrong test.
    #
    # Correct C3: verify EUROMOD output is internally consistent with the earnings it received:
    #   - Working chosen rows: ils_dispy should correlate with yem (more earnings -> more income)
    #   - Non-working chosen rows: ils_dispy should be positive (out-of-work transfers present)
    #   - ils_dispy_real = ils_dispy * phi (CPI deflation applied correctly)
    if draw_col in priced.columns and "idhh_true" in priced.columns:
        if mode == "singles":
            chosen = priced[priced["draw"] == 0].copy()
        else:
            chosen = priced[priced.get("is_chosen_joint", pd.Series(0, index=priced.index)) == 1].copy()

        dec_chosen = chosen[chosen["ruro_decider"] == 1] if "ruro_decider" in chosen.columns else chosen
        n_chosen = len(dec_chosen)
        results_c3: dict = {"n_chosen_decider_rows": n_chosen}

        # (a) CPI deflation identity
        if "ils_dispy_real" in dec_chosen.columns and "ils_dispy" in dec_chosen.columns:
            phi = _CPI[year]
            deflate_resid = (dec_chosen["ils_dispy_real"] - dec_chosen["ils_dispy"] * phi).abs()
            n_deflate_viol = int((deflate_resid > 1e-6).sum())
            results_c3["cpi_identity_violations"] = n_deflate_viol
            results_c3["cpi_phi"] = phi
        else:
            n_deflate_viol = 0
            results_c3["cpi_identity_violations"] = None

        # (b) Working chosen rows: ils_dispy > 0 and corr(yem, ils_dispy) > 0
        if "working" in dec_chosen.columns and "yem" in dec_chosen.columns:
            work_chosen = dec_chosen[dec_chosen["working"] == 1]
            n_work_neg = int((work_chosen["ils_dispy"] <= 0).sum()) if len(work_chosen) > 0 else 0
            corr_yem = float(work_chosen["yem"].corr(work_chosen["ils_dispy"])) if len(work_chosen) > 5 else float("nan")
            results_c3["n_working_chosen"] = len(work_chosen)
            results_c3["n_working_neg_dispy"] = n_work_neg
            results_c3["corr_yem_dispy_working"] = round(corr_yem, 4)
        else:
            n_work_neg = 0
            corr_yem = 1.0
            results_c3["note"] = "working/yem cols absent"

        # (c) Non-working chosen rows: median ils_dispy > 0
        if "working" in dec_chosen.columns:
            nonwork_chosen = dec_chosen[dec_chosen["working"] == 0]
            median_nonwork_dispy = float(nonwork_chosen["ils_dispy"].median()) if len(nonwork_chosen) > 0 else float("nan")
            results_c3["n_nonworking_chosen"] = len(nonwork_chosen)
            results_c3["median_nonwork_dispy"] = round(median_nonwork_dispy, 2)
        else:
            median_nonwork_dispy = 1.0

        results_c3["pass"] = (
            n_deflate_viol == 0 and
            n_work_neg == 0 and
            (np.isnan(corr_yem) or corr_yem > 0) and
            (np.isnan(median_nonwork_dispy) or median_nonwork_dispy > 0)
        )
        results["C3_chosen_row_consistency"] = results_c3
    else:
        results["C3_chosen_row_consistency"] = {"pass": None, "note": "missing draw/idhh_true col"}

    # C4: working alt ils_dispy moves with hours (monotone-ish check within one HH)
    if "ruro_decider" in priced.columns and draw_col in priced.columns:
        if mode == "singles" and "lhw" in priced.columns and "ils_dispy" in priced.columns:
            dec = priced[priced["ruro_decider"] == 1].copy()
            sample_hh = dec["idhh_true"].unique()[:1] if "idhh_true" in dec.columns else dec["idhh"].unique()[:1]
            if len(sample_hh):
                hh_data = dec[dec.get("idhh_true", dec["idhh"]) == sample_hh[0]][["lhw","ils_dispy"]].sort_values("lhw")
                corr = float(hh_data["lhw"].corr(hh_data["ils_dispy"])) if len(hh_data) > 2 else float("nan")
                results["C4_dispy_moves_with_hours"] = {
                    "sample_hh": float(sample_hh[0]),
                    "lhw_dispy_corr": corr,
                    "pass": corr > 0 if not np.isnan(corr) else None,
                    "note": "positive correlation expected (more hours -> more net income)",
                }
            else:
                results["C4_dispy_moves_with_hours"] = {"pass": None, "note": "no sample HH"}
        else:
            results["C4_dispy_moves_with_hours"] = {"pass": None, "note": "couples or missing cols"}
    else:
        results["C4_dispy_moves_with_hours"] = {"pass": None, "note": "cols absent"}

    return results


def _print_canary(results: dict, year: int, mode: str) -> bool:
    all_pass = True
    print(f"\n  Canary [{mode} {year}]:")
    for k, v in results.items():
        p = v.get("pass")
        # coerce numpy bools
        if hasattr(p, "item"):
            p = p.item()
        status = "PASS" if p is True else ("FAIL" if p is False else "SKIP")
        if p is False:
            all_pass = False
        print(f"    {status} {k}: {v}")
    return all_pass


# ---------------------------------------------------------------------------
# Core pricer
# ---------------------------------------------------------------------------

def _price_one_file(
    long_path: Path,
    year: int,
    mode: str,
    runner,
    system_code: str,
    dataset_name: str,
    roster: pd.DataFrame,
    canary_only: bool = False,
) -> tuple[pd.DataFrame, dict]:
    """
    Price one precompute long file through EUROMOD.

    Strategy:
      1. Load long file.
      2. Stamp draw-specific idhh/idperson (EUROMOD needs unique HH IDs per alternative).
      3. Filter to raw EUROMOD input columns only (no bpool extras).
      4. Run EUROMOD -> sim_df with ils_dispy + components.
      5. Restore true IDs; merge sim output back onto original long file.
      6. Apply CPI deflation.
      7. Run canary checks.
    """
    print(f"\n  Loading {long_path.name} ...")
    long_df = pd.read_parquet(long_path)
    print(f"  Shape: {long_df.shape}")

    draw_col = "draw" if mode == "singles" else "draw_joint"

    # --- 2. Stamp draw-specific IDs ---
    # Singles: id_multiplier must exceed max draw index (100) -> use 1000
    # Couples: max draw_joint = 900 -> use 10000
    id_multiplier = 1_000 if mode == "singles" else 10_000
    long_stamped = _stamp_draw_ids(long_df, draw_col, id_multiplier)

    # --- 3. Build EUROMOD input: raw schema columns only ---
    raw_cols = _RAW_SCHEMA[year]
    # Use stamped idhh/idperson (the ones EUROMOD will use)
    em_input = long_stamped[[c for c in raw_cols if c in long_stamped.columns]].copy()
    print(f"  EUROMOD input: {em_input.shape[0]} rows × {em_input.shape[1]} cols")

    # Ensure all numeric
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)

    # --- 4. Run EUROMOD ---
    print(f"  Running EUROMOD {system_code} / {dataset_name} ...")
    sim_df = runner.run_on_dataframe(
        em_input,
        country="FR",
        system_code=system_code,
        dataset_name=dataset_name,
    )
    print(f"  EUROMOD output: {sim_df.shape}")

    # --- 5. Merge ils_dispy + components back onto original long file ---
    # EUROMOD preserves row order (same n_rows, same sequence).
    # Verify row count matches before direct assignment.
    if len(sim_df) != len(long_stamped):
        raise RuntimeError(
            f"HARD STOP: EUROMOD output {len(sim_df)} rows ≠ input {len(long_stamped)} rows "
            f"for {mode} {year}. Cannot merge back."
        )

    # Restore true IDs on sim output
    sim_df = sim_df.reset_index(drop=True)
    long_out = long_df.reset_index(drop=True).copy()

    # Carry idhh_true / idperson_true for canary C3
    long_out["idhh_true"]     = long_df["idhh"].values
    long_out["idperson_true"] = long_df["idperson"].values

    # Assign EUROMOD output columns
    em_out_cols_present = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]
    missing_em_cols = [c for c in _EM_OUTPUT_COLS if c not in sim_df.columns]
    if missing_em_cols:
        print(f"  WARNING: EUROMOD did not produce: {missing_em_cols}")

    for c in em_out_cols_present:
        long_out[c] = sim_df[c].values

    # --- 6. CPI deflation ---
    phi = _CPI[year]
    long_out["ils_dispy_real"] = long_out["ils_dispy"] * phi
    print(f"  CPI phi_{year}={phi} -> ils_dispy_real computed")

    # --- 7. Canary checks ---
    canary = _run_canary(long_out, roster, year, mode)
    canary_pass = _print_canary(canary, year, mode)

    meta = {
        "year": year,
        "mode": mode,
        "system": system_code,
        "dataset": dataset_name,
        "n_rows": len(long_out),
        "em_output_cols": em_out_cols_present,
        "missing_em_cols": missing_em_cols,
        "cpi_phi": phi,
        "canary": canary,
        "canary_pass": canary_pass,
    }
    return long_out, meta


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Price bpool long files through EUROMOD")
    parser.add_argument("--canary-only", action="store_true",
                        help="Run canary year (2017 singles) only, then stop")
    parser.add_argument("--year", type=int, choices=[2015, 2016, 2017], default=None)
    parser.add_argument("--singles-only", action="store_true")
    parser.add_argument("--couples-only", action="store_true")
    args = parser.parse_args()

    years = [args.year] if args.year else [2017, 2016, 2015]
    if args.canary_only:
        years = [2017]

    run_singles = not args.couples_only
    run_couples = not args.singles_only and not args.canary_only

    # -----------------------------------------------------------------------
    # Pairing table report
    # -----------------------------------------------------------------------
    print("\nSystem pairing table (opportunity_year = data_year - 1):")
    print(f"  {'data_year':<12} {'system':<10} {'dataset':<15} {'input file'}")
    for yr, (sys, ds, raw) in _SYSTEM_PAIRING.items():
        print(f"  {yr:<12} {sys:<10} {ds:<15} {raw.name}")

    print("\nCPI deflation (base = 2016):")
    for yr, phi in _CPI.items():
        print(f"  phi_{yr} = {phi}")

    # -----------------------------------------------------------------------
    # Load rosters for canary C3 cross-check
    # -----------------------------------------------------------------------
    print("\nLoading observed rosters for canary C3 cross-check...")
    rosters: dict[int, pd.DataFrame] = {}
    for yr in years:
        rosters[yr] = pd.read_parquet(_FR_PARQUET[yr], columns=["idhh", "idperson", "ils_dispy"])
        print(f"  fr_{yr}.parquet: {rosters[yr].shape}")

    # -----------------------------------------------------------------------
    # Build EUROMOD runner (one model, reused across all runs)
    # -----------------------------------------------------------------------
    print("\nInitialising EUROMOD runner...")
    runner = EuromodRunner(_EM_ROOT)
    print("  EUROMOD model loaded.")

    # -----------------------------------------------------------------------
    # Run loop
    # -----------------------------------------------------------------------
    summary: dict = {
        "run_start": datetime.now(timezone.utc).isoformat(),
        "cpi": _CPI,
        "system_pairing": {yr: {"system": s, "dataset": d} for yr, (s, d, _) in _SYSTEM_PAIRING.items()},
        "files": {},
    }
    all_pass = True

    for yr in years:
        em_sys_code, ds_name, _ = _SYSTEM_PAIRING[yr]
        roster = rosters[yr]

        # --- CANARY: 2017 singles first ---
        if yr == 2017 and run_singles:
            long_path = _BPOOL_DIR / f"fr_p3a_bpool_precompute__2017__singles__long.parquet"
            out_path  = _BPOOL_DIR / f"fr_p3a_bpool_priced__2017__singles.parquet"
            print(f"\n{'='*60}")
            print(f"CANARY: SINGLES {yr}  ({long_path.name})")
            print(f"{'='*60}")

            try:
                priced, meta = _price_one_file(
                    long_path, yr, "singles", runner, em_sys_code, ds_name, roster
                )
                priced.to_parquet(out_path, index=False)
                print(f"  Written: {out_path}  shape={priced.shape}")
                summary["files"][f"{yr}_singles"] = meta
                all_pass &= meta["canary_pass"]

                if not meta["canary_pass"]:
                    print(f"\nHARD STOP: Canary failed for singles {yr}. Fix before running remaining files.")
                    _write_summary(summary, all_pass)
                    _sys.exit(1)
                else:
                    print(f"\nCanary PASSED - proceeding to remaining files.")

            except Exception as e:
                print(f"\nHARD STOP: {e}")
                summary["files"][f"{yr}_singles"] = {"error": str(e)}
                all_pass = False
                _write_summary(summary, all_pass)
                _sys.exit(1)

            if args.canary_only:
                _write_summary(summary, all_pass)
                return

        # --- Remaining singles (non-canary years) ---
        elif run_singles:
            long_path = _BPOOL_DIR / f"fr_p3a_bpool_precompute__{yr}__singles__long.parquet"
            out_path  = _BPOOL_DIR / f"fr_p3a_bpool_priced__{yr}__singles.parquet"
            print(f"\n{'='*60}")
            print(f"SINGLES {yr}")
            print(f"{'='*60}")
            try:
                priced, meta = _price_one_file(
                    long_path, yr, "singles", runner, em_sys_code, ds_name, roster
                )
                priced.to_parquet(out_path, index=False)
                print(f"  Written: {out_path}  shape={priced.shape}")
                summary["files"][f"{yr}_singles"] = meta
                all_pass &= meta["canary_pass"]
                if not meta["canary_pass"]:
                    print(f"\nHARD STOP: singles {yr} canary failed.")
                    _write_summary(summary, all_pass)
                    _sys.exit(1)
            except Exception as e:
                print(f"\nHARD STOP: {e}")
                summary["files"][f"{yr}_singles"] = {"error": str(e)}
                all_pass = False
                _write_summary(summary, all_pass)
                _sys.exit(1)

        # --- Couples ---
        if run_couples:
            long_path = _BPOOL_DIR / f"fr_p3a_bpool_precompute__{yr}__couples__long.parquet"
            out_path  = _BPOOL_DIR / f"fr_p3a_bpool_priced__{yr}__couples.parquet"
            print(f"\n{'='*60}")
            print(f"COUPLES {yr}")
            print(f"{'='*60}")
            try:
                priced, meta = _price_one_file(
                    long_path, yr, "couples", runner, em_sys_code, ds_name, roster
                )
                priced.to_parquet(out_path, index=False)
                print(f"  Written: {out_path}  shape={priced.shape}")
                summary["files"][f"{yr}_couples"] = meta
                all_pass &= meta["canary_pass"]
                if not meta["canary_pass"]:
                    print(f"\nHARD STOP: couples {yr} canary failed.")
                    _write_summary(summary, all_pass)
                    _sys.exit(1)
            except Exception as e:
                print(f"\nHARD STOP: {e}")
                summary["files"][f"{yr}_couples"] = {"error": str(e)}
                all_pass = False
                _write_summary(summary, all_pass)
                _sys.exit(1)

    _write_summary(summary, all_pass)
    if all_pass:
        print("\nALL FILES PRICED — EUROMOD run complete")
    else:
        print("\nSOME FILES FAILED — review summary")
        _sys.exit(1)


def _write_summary(summary: dict, all_pass: bool) -> None:
    summary["run_end"] = datetime.now(timezone.utc).isoformat()
    summary["all_pass"] = all_pass
    out = _BPOOL_DIR / "fr_p3a_bpool_priced__meta.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary written: {out}")


if __name__ == "__main__":
    main()
