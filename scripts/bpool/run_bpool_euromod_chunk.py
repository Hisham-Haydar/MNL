"""
B-pool EUROMOD chunk worker.

Prices one draw-range band of one precompute long file through EUROMOD.
Intended to be launched in parallel (one process per chunk) by the
parallel launcher script.

Usage (one chunk):
    python run_bpool_euromod_chunk.py --year 2017 --mode couples \
        --draw-lo 0 --draw-hi 150 --chunk-id 0

Writes:
    U:/EUROMOD-STORAGE/new_data/chunks/fr_p3a_bpool_priced__2017__couples__c0.parquet
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS / "enhanced"))

import sys as _sys
from enh_RURO_euromod import EuromodRunner  # noqa: E402

from _bpool_paths import bpool_dir, em_root, raw_data_dir  # noqa: E402
_BPOOL_DIR  = bpool_dir()
_CHUNK_DIR  = _BPOOL_DIR / "chunks"
_EM_ROOT    = em_root()
_RAW_DATA   = raw_data_dir()

_SYSTEM_PAIRING = {
    2015: ("FR_2014", "FR_2015_a2"),
    2016: ("FR_2015", "FR_2016_a3"),
    2017: ("FR_2016", "FR_2017_a2"),
}
_CPI = {2015: 1.0031, 2016: 1.0000, 2017: 0.9886}

_EM_OUTPUT_COLS = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy"]

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


def _stamp_draw_ids(df: pd.DataFrame, draw_col: str, id_multiplier: int) -> pd.DataFrame:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year",     type=int, required=True, choices=[2015, 2016, 2017])
    ap.add_argument("--mode",     required=True, choices=["singles", "couples"])
    ap.add_argument("--draw-lo",  type=int, required=True, help="inclusive lower bound of draw_joint range")
    ap.add_argument("--draw-hi",  type=int, required=True, help="exclusive upper bound of draw_joint range")
    ap.add_argument("--chunk-id", type=int, required=True, help="chunk index (for output filename)")
    args = ap.parse_args()

    year, mode, draw_lo, draw_hi, chunk_id = args.year, args.mode, args.draw_lo, args.draw_hi, args.chunk_id
    draw_col    = "draw" if mode == "singles" else "draw_joint"
    id_mult     = 1_000  if mode == "singles" else 10_000
    system_code, dataset_name = _SYSTEM_PAIRING[year]
    phi         = _CPI[year]

    long_path   = _BPOOL_DIR / f"fr_p3a_bpool_precompute__{year}__{mode}__long.parquet"
    chunk_path  = _CHUNK_DIR / f"fr_p3a_bpool_priced__{year}__{mode}__c{chunk_id}.parquet"
    meta_path   = _CHUNK_DIR / f"fr_p3a_bpool_priced__{year}__{mode}__c{chunk_id}.json"

    _CHUNK_DIR.mkdir(exist_ok=True)

    print(f"[chunk {chunk_id}] {year} {mode} draw_joint in [{draw_lo},{draw_hi})")
    print(f"[chunk {chunk_id}] Loading {long_path.name} (push-down filter [{draw_lo},{draw_hi})) ...")
    table = pq.read_table(
        long_path,
        filters=[(draw_col, ">=", draw_lo), (draw_col, "<", draw_hi)],
        use_threads=False,
    )
    chunk_df = table.to_pandas().reset_index(drop=True)
    print(f"[chunk {chunk_id}] Chunk rows: {len(chunk_df):,}")

    if len(chunk_df) == 0:
        print(f"[chunk {chunk_id}] Empty chunk — writing empty parquet.")
        chunk_df.to_parquet(chunk_path, index=False)
        _sys.exit(0)

    # Stamp IDs
    chunk_stamped = _stamp_draw_ids(chunk_df, draw_col, id_mult)

    # Build EUROMOD input
    raw_cols = _RAW_SCHEMA[year]
    em_input = chunk_stamped[[c for c in raw_cols if c in chunk_stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)
    print(f"[chunk {chunk_id}] EUROMOD input: {em_input.shape[0]:,} rows x {em_input.shape[1]} cols")

    # Run EUROMOD
    runner = EuromodRunner(_EM_ROOT)
    print(f"[chunk {chunk_id}] Running EUROMOD {system_code} / {dataset_name} ...")
    sim_df = runner.run_on_dataframe(
        em_input, country="FR", system_code=system_code, dataset_name=dataset_name,
    )
    print(f"[chunk {chunk_id}] EUROMOD output: {sim_df.shape}")

    if len(sim_df) != len(chunk_df):
        raise RuntimeError(
            f"[chunk {chunk_id}] Row count mismatch: EUROMOD={len(sim_df)}, expected={len(chunk_df)}"
        )

    # Assemble output
    out_df = chunk_df.reset_index(drop=True).copy()
    out_df["idhh_true"]     = chunk_df["idhh"].values
    out_df["idperson_true"] = chunk_df["idperson"].values

    # ---- Two-M write-back fix ----------------------------------------------------------
    # PREVIOUSLY only the 5 headline columns (_EM_OUTPUT_COLS) were written back from the
    # per-draw EUROMOD sim_df, leaving every other simulated output column (ils_benmt,
    # ils_bennt, ils_pen, *_s, t*_s, ...) as a STALE precompute carry-over, constant across
    # draws (diagnosed in Two-L). FIX: write back EVERY SIMULATED OUTPUT column EUROMOD
    # produced for this draw, so each row's ils_*/*_s correspond to the scenario actually
    # run. We overwrite the simulated-output columns only -- columns that are NOT raw EUROMOD
    # INPUTS (those are echoed unchanged and left untouched) and are not keys/bookkeeping
    # (stacked_hh_uid/draw*/ruro_decider/idhh_true/idperson_true are not in sim_df, so they
    # are preserved automatically). The 5 headline columns are a subset of this set and so
    # remain byte-identical to the previous behaviour (headline invariance, Two-M Gate A).
    _raw_input_cols = set(_RAW_SCHEMA[year])
    sim_output_cols = [c for c in sim_df.columns if c not in _raw_input_cols]
    for c in sim_output_cols:
        out_df[c] = sim_df[c].values
    em_out_cols = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]
    # ------------------------------------------------------------------------------------

    out_df["ils_dispy_real"] = out_df["ils_dispy"] * phi

    n_null = int(out_df["ils_dispy"].isna().sum())
    print(f"[chunk {chunk_id}] ils_dispy nulls: {n_null}")
    print(f"[chunk {chunk_id}] ils_dispy mean: {out_df['ils_dispy'].mean():.2f}")

    out_df.to_parquet(chunk_path, index=False)
    print(f"[chunk {chunk_id}] Written: {chunk_path}  shape={out_df.shape}")

    meta = {
        "year": year, "mode": mode, "chunk_id": chunk_id,
        "draw_lo": draw_lo, "draw_hi": draw_hi,
        "n_rows": len(out_df), "n_null_dispy": n_null,
        "em_output_cols": em_out_cols,
        "n_simulated_output_cols_written": len(sim_output_cols),  # Two-M: all sim outputs
        "cpi_phi": phi,
        "output_path": str(chunk_path),
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[chunk {chunk_id}] Meta: {meta_path}")
    print(f"[chunk {chunk_id}] DONE")


if __name__ == "__main__":
    main()
