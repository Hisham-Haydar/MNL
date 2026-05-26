"""
Read-only validation rebuild.

For each (year, mode), take the OBSERVED state (canonical fr_20YY.parquet),
keep earnings as-is (no draw substitution), and price it through the t-1 system:
    2015 data -> FR_2014 ;  2016 -> FR_2015 ;  2017 -> FR_2016.
This yields ils_dispy_tminus1_observed per household.

Then compare to the B-pool chosen-row ils_dispy (the row with is_chosen / is_chosen_joint == 1
and ruro_decider == 1). Expectation: ~0 Eur difference (both price the same observed
earnings through the same t-1 system).

For couples chosen rows with |Delta| > 1000 Eur, list idhh + observed vs chosen earnings.

NO CHANGES; read-only.
"""
from __future__ import annotations
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS / "enhanced"))
from enh_RURO_euromod import EuromodRunner  # noqa: E402

from _bpool_paths import bpool_dir, em_root, FR_PARQUETS  # noqa: E402
_BPOOL   = bpool_dir()
_EM_ROOT = em_root()
_FR      = FR_PARQUETS
_SYSTEM_PAIRING = {
    2015: ("FR_2014", "FR_2015_a2"),
    2016: ("FR_2015", "FR_2016_a3"),
    2017: ("FR_2016", "FR_2017_a2"),
}

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


def price_observed(year: int, runner: EuromodRunner) -> pd.DataFrame:
    """Run EUROMOD t-1 system on the canonical observed state, return per-person ils_dispy."""
    system_code, dataset_name = _SYSTEM_PAIRING[year]
    cf = pd.read_parquet(_FR[year])
    # EUROMOD requires rows sorted by household (then person)
    cf = cf.sort_values(["idhh", "idperson"], kind="mergesort").reset_index(drop=True)
    print(f"  [{year}] canonical: {cf.shape}  HHs={cf['idhh'].nunique():,} (sorted by idhh,idperson)")

    raw_cols = _RAW_SCHEMA[year]
    em_input = cf[[c for c in raw_cols if c in cf.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    print(f"  [{year}] EUROMOD input: {em_input.shape}, running {system_code}/{dataset_name} ...")

    sim = runner.run_on_dataframe(
        em_input, country="FR", system_code=system_code, dataset_name=dataset_name,
    )
    out = cf[["idhh", "idperson", "yem", "lhw", "yivwg"]].copy()
    out["ils_dispy_tminus1_obs"] = sim["ils_dispy"].values
    print(f"  [{year}] priced. ils_dispy mean={out['ils_dispy_tminus1_obs'].mean():.2f}")
    return out


def compare_one(year: int, mode: str, baseline: pd.DataFrame) -> dict:
    p = _BPOOL / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    chosen_flag = "is_chosen" if mode == "singles" else "is_chosen_joint"
    cols = ["idhh_true", "idperson_true", chosen_flag, "ruro_decider",
            "ils_dispy", "yem", "yivwg", "lhw", "dgn"]
    pf = pd.read_parquet(p, columns=cols)
    chosen = pf[(pf[chosen_flag] == 1) & (pf["ruro_decider"] == 1)].copy()
    chosen = chosen.rename(columns={"ils_dispy": "ils_dispy_chosen",
                                     "yem": "yem_chosen", "yivwg": "yivwg_chosen",
                                     "lhw": "lhw_chosen"})

    base = baseline.rename(columns={"yem": "yem_obs", "lhw": "lhw_obs",
                                     "yivwg": "yivwg_obs"})
    m = chosen.merge(
        base, left_on=["idhh_true", "idperson_true"],
        right_on=["idhh", "idperson"], how="inner",
    )
    n_match = len(m)
    diff = (m["ils_dispy_chosen"] - m["ils_dispy_tminus1_obs"]).abs()
    max_d  = float(diff.max())  if n_match else float("nan")
    med_d  = float(diff.median()) if n_match else float("nan")
    n_over = int((diff > 1.0).sum())
    pct    = 100.0 * n_over / max(n_match, 1)
    status = "PASS" if (n_match > 0 and med_d <= 1.0) else "FAIL"

    big = []
    if mode == "couples":
        big_mask = diff > 1000.0
        if big_mask.any():
            anom = m[big_mask][["idhh_true", "dgn",
                                "yem_chosen", "yem_obs",
                                "yivwg_chosen", "yivwg_obs",
                                "lhw_chosen", "lhw_obs",
                                "ils_dispy_chosen", "ils_dispy_tminus1_obs"]].copy()
            anom["abs_delta"] = (anom["ils_dispy_chosen"] - anom["ils_dispy_tminus1_obs"]).abs()
            big = anom.sort_values("abs_delta", ascending=False).head(20)

    return {
        "file": f"{year}_{mode}",
        "n_matched": n_match,
        "max_abs_diff": max_d,
        "median_abs_diff": med_d,
        "n_over_1eur": n_over,
        "pct_over_1eur": round(pct, 3),
        "status": status,
        "anomalies_gt_1000eur": big,
    }


def main() -> None:
    print("Building t-1 observed baseline (EUROMOD on canonical observed state)...")
    runner = EuromodRunner(_EM_ROOT)
    baselines = {}
    for y in (2015, 2016, 2017):
        print(f"\n--- pricing observed {y} ---")
        baselines[y] = price_observed(y, runner)

    print("\n" + "="*100)
    print("CHOSEN vs T-1 OBSERVED BASELINE")
    print("="*100)
    print(f"{'file':<14} {'n_match':>10} {'max|d|':>14} {'med|d|':>14} {'n>1Eur':>10} {'pct':>8}  status")
    print("-"*100)

    all_pass = True
    anomalies = []
    for y in (2015, 2016, 2017):
        for mode in ("singles", "couples"):
            r = compare_one(y, mode, baselines[y])
            print(f"{r['file']:<14} {r['n_matched']:>10,} {r['max_abs_diff']:>14.4f} "
                  f"{r['median_abs_diff']:>14.4f} {r['n_over_1eur']:>10,} "
                  f"{r['pct_over_1eur']:>7}% {r['status']:>6}")
            if r["status"] != "PASS":
                all_pass = False
            if isinstance(r["anomalies_gt_1000eur"], pd.DataFrame) and len(r["anomalies_gt_1000eur"]):
                anomalies.append((r["file"], r["anomalies_gt_1000eur"]))

    print("-"*100)
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")

    if anomalies:
        print("\n" + "="*100)
        print("COUPLES anomalies with |delta| > 1000 EUR (top 20 per file)")
        print("="*100)
        for fname, df in anomalies:
            print(f"\n--- {fname} ---  n_anomalies={len(df)}")
            print(df.to_string(index=False, float_format=lambda x: f"{x:>10.2f}"))
    else:
        print("\nNo couples chosen rows with |delta| > 1000 EUR.")


if __name__ == "__main__":
    main()
