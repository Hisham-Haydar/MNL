#!/usr/bin/env python
"""
NC pilot — Stage 5 v2 adapter: blockwise joint-product EUROMOD inputs
(Strategy C').

Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage5_strategy_amendment_v2.md.
Supersedes Strategy B (v1 adapter export_pilot_euromod_inputs.py) which
halted at HE7. Pilot-only. Production runner not modified.

Strategy C' (per amendment §10 §11 §12):
  - Sweep the 30 x 30 joint product as 30 BLOCKS, one per fixed female
    draw f in {0..29}.
  - Within block f:
      * female partner is fixed at her draw-f job (hours/wage/loc4/yem
        from draw f), presented as a DECIDER (is_decider=1);
      * male partner varies over scalar draw m in {0..29}, decider too;
      * BOTH partners are deciders on every row -> runner recomputes
        yem00/yemxp/yem from final lhw*yivwg for both -> HE7 identity
        holds by construction.
  - Scalar runner draw = male marginal m. NEVER draw_joint.
  - Block constant f is recorded in the drawsmeta sidecar (and on every
    row via a `block_f` column) so the later merge slice can rebuild
    draw_joint = 30*m + f.

Per-block output:
  Data/pilot/nc_2016_couples/em_inputs/block_f{FF}/
    fr_pilot_2016_couples_block_f{FF}_draws.parquet
    fr_pilot_2016_couples_block_f{FF}_draws__drawsmeta.json

This adapter does not import euromod or run EUROMOD.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PILOT_DATA = REPO / "Data" / "pilot" / "nc_2016_couples"
PILOT_PRODUCT = PILOT_DATA / "fr_pilot_nc_2016_couples_product.parquet"
EM_INPUTS_DIR = PILOT_DATA / "em_inputs"

PROD_COUPLES_DRAWS = Path(r"U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet")

PRODUCT_SIZE = 30
N_MALE_DRAWS = 30
ID_MULTIPLIER = 1000
EXPECTED_COUPLES = 2577

STRAY_ILS_COLS = ("ils_earns", "ils_origy", "ils_pen", "ils_sicdy", "ils_earns_real")


def _load_production_baseline_couples() -> pd.DataFrame:
    """Read production FR_2016 couples draws at draw=0 (baseline rows).

    This is the source of the full EUROMOD-template carry columns for
    both partners and any children.
    """
    print(f"[adapter v2] loading production FR_2016 couples baseline (draw=0)...")
    df = pd.read_parquet(PROD_COUPLES_DRAWS)
    d0 = df[df["draw"] == 0].copy()
    print(f"[adapter v2] baseline rows (all household members at draw=0): {len(d0):,}")
    print(f"[adapter v2] unique idhh: {d0['idhh'].nunique():,}")
    return d0


def _load_pilot_partner_slice(side: str) -> pd.DataFrame:
    """Read the pilot wide product parquet to extract per-partner per-draw
    job values (loc4, hours, wage, yem) for partner `side`.

    Returns a tall DataFrame indexed by (idhh, draw_partner) carrying the
    partner-specific job values for every (couple, marginal-draw) pair.
    Distinct rows per couple: 30 (one per marginal draw_partner).
    """
    assert side in ("male", "female")
    other = "female" if side == "male" else "male"

    # Filter pilot wide product to draw_{other}==0 -> 30 unique
    # (couple, draw_{side}) rows; each carries the partner's draw_{side} job.
    decider_draw_col = f"draw_{side}"
    other_draw_col = f"draw_{other}"
    cols = [
        "idhh", decider_draw_col, other_draw_col,
        f"loc4_{side}", f"wage_{side}", f"hours_{side}", f"yem_{side}",
    ]
    wide = pd.read_parquet(PILOT_PRODUCT, columns=cols)
    sub = wide[wide[other_draw_col] == 0][[
        "idhh", decider_draw_col,
        f"loc4_{side}", f"wage_{side}", f"hours_{side}", f"yem_{side}",
    ]].copy()
    sub = sub.rename(columns={
        decider_draw_col: f"draw_{side}",
        f"loc4_{side}": "loc4_pilot",
        f"wage_{side}": "wage_pilot",
        f"hours_{side}": "hours_pilot",
        f"yem_{side}": "yem_pilot",
    })
    n = len(sub)
    print(f"[adapter v2] pilot {side} per-draw slice: {n:,} rows "
          f"(expected {EXPECTED_COUPLES * N_MALE_DRAWS:,})")
    if n != EXPECTED_COUPLES * N_MALE_DRAWS:
        raise RuntimeError(
            f"[adapter v2] pilot {side} slice row count {n:,} != "
            f"expected {EXPECTED_COUPLES * N_MALE_DRAWS:,}"
        )
    return sub


def build_block_input(
    block_f: int,
    baseline: pd.DataFrame,
    male_slice: pd.DataFrame,
    female_slice: pd.DataFrame,
) -> pd.DataFrame:
    """Build the EUROMOD long-format input for block f.

    Construction (per amendment §10, §12, §15):
      - Decider rows: 2,577 couples * 30 m-draws * 2 partners = 154,620
        rows. Each (idperson_partner, draw=m) row has:
          * male partner: draw-m hours/wage/yem (varies across m);
          * female partner: draw-f hours/wage/yem (block constant);
          * is_decider=1 for BOTH partners.
      - Non-decider rows: any children/other household members, kept at
        their production baseline values with draw=0 only; the runner
        will replicate them across draws 0..29.
      - block_f column added to every row for later (m, f) reconstruction.
    """
    print(f"[adapter v2] building block f={block_f:02d} input...")

    # ---------- Decider partners ----------
    # Production baseline decider rows = 5,154 (one per partner per couple).
    is_decider_baseline = baseline["is_decider"] == 1
    decider_baseline = baseline[is_decider_baseline].copy()
    # Drop production-side draw and is_chosen so we set our own scalar draw
    for c in ("draw", "is_chosen"):
        if c in decider_baseline.columns:
            decider_baseline = decider_baseline.drop(columns=[c])

    # Cross-join decider baselines with male-marginal draws m in 0..29
    draws_m = pd.DataFrame({"draw": np.arange(N_MALE_DRAWS, dtype=np.int32), "_k": 1})
    decider_expanded = decider_baseline.assign(_k=1).merge(draws_m, on="_k").drop(columns="_k")
    # decider_expanded now has 5,154 * 30 = 154,620 rows.

    # Apply per-partner per-m pilot values
    # ---- Male partner (dgn==1): join on (idhh, draw=m) to male_slice
    male_keyed = male_slice.rename(columns={"draw_male": "draw"})
    male_keyed["idhh"] = male_keyed["idhh"].astype(decider_expanded["idhh"].dtype)
    # Apply only to dgn==1 rows
    dec_male_mask = decider_expanded["dgn"] == 1.0
    decider_male = decider_expanded[dec_male_mask].merge(
        male_keyed, on=["idhh", "draw"], how="left", suffixes=("", "_PILOTM")
    )
    n_male_matched = int(decider_male["wage_pilot"].notna().sum())
    print(f"[adapter v2]   male decider rows: {len(decider_male):,}  "
          f"pilot-matched: {n_male_matched:,}")

    # ---- Female partner (dgn==0): set values from female_slice at draw_female==block_f
    # The female job is the SAME draw-f job for every m within the block.
    female_at_f = female_slice[female_slice["draw_female"] == block_f].copy()
    if len(female_at_f) != EXPECTED_COUPLES:
        raise RuntimeError(
            f"[adapter v2] female slice at draw_female={block_f} has "
            f"{len(female_at_f):,} rows, expected {EXPECTED_COUPLES:,}"
        )
    female_at_f = female_at_f.drop(columns=["draw_female"])
    female_at_f["idhh"] = female_at_f["idhh"].astype(decider_expanded["idhh"].dtype)
    # Apply to dgn==0 rows (replicate to all 30 m-values per couple)
    dec_female_mask = decider_expanded["dgn"] == 0.0
    decider_female = decider_expanded[dec_female_mask].merge(
        female_at_f, on="idhh", how="left"
    )
    n_female_matched = int(decider_female["wage_pilot"].notna().sum())
    print(f"[adapter v2]   female decider rows: {len(decider_female):,}  "
          f"pilot-matched (block f={block_f}): {n_female_matched:,}")

    # Sanity: each female decider row must be matched
    if n_female_matched != len(decider_female):
        raise RuntimeError(
            f"[adapter v2] {len(decider_female) - n_female_matched:,} female "
            f"decider rows have no pilot match at block f={block_f}"
        )
    if n_male_matched != len(decider_male):
        raise RuntimeError(
            f"[adapter v2] {len(decider_male) - n_male_matched:,} male "
            f"decider rows have no pilot match"
        )

    decider_full = pd.concat([decider_male, decider_female], axis=0, ignore_index=True, sort=False)

    # Overwrite hours/wage/yem/lhw/yivwg/loc4/loc_ruro from pilot values
    decider_full["hours"] = decider_full["hours_pilot"]
    decider_full["lhw"] = decider_full["hours_pilot"]
    decider_full["wage"] = decider_full["wage_pilot"]
    decider_full["yivwg"] = decider_full["wage_pilot"]
    decider_full["yem"] = decider_full["yem_pilot"]
    decider_full["loc4"] = decider_full["loc4_pilot"]
    if "loc_ruro" in decider_full.columns:
        decider_full["loc_ruro"] = decider_full["loc4_pilot"]
    decider_full = decider_full.drop(columns=[
        "hours_pilot", "wage_pilot", "yem_pilot", "loc4_pilot"
    ])
    # is_decider already 1 in baseline; assert
    decider_full["is_decider"] = 1
    decider_full["block_f"] = np.int32(block_f)

    # ---------- Non-deciders (children/other household members) ----------
    non_decider_baseline = baseline[~is_decider_baseline].copy()
    for c in ("draw", "is_chosen"):
        if c in non_decider_baseline.columns:
            non_decider_baseline = non_decider_baseline.drop(columns=[c])
    non_decider_baseline["draw"] = 0  # runner replicates across all draws
    non_decider_baseline["is_decider"] = 0
    non_decider_baseline["block_f"] = np.int32(block_f)
    print(f"[adapter v2]   non-decider rows (children/other): {len(non_decider_baseline):,}")

    # ---------- Combine ----------
    combined = pd.concat(
        [decider_full, non_decider_baseline], axis=0, ignore_index=True, sort=False
    )

    # ---------- Drop the 5 stray ils_* columns ----------
    drop = [c for c in STRAY_ILS_COLS if c in combined.columns]
    if drop:
        combined = combined.drop(columns=drop)
        print(f"[adapter v2]   dropped stray ils_*: {drop}")

    n = len(combined)
    n_dec = int((combined["is_decider"] == 1).sum())
    n_ndec = int((combined["is_decider"] == 0).sum())
    print(f"[adapter v2] block f={block_f:02d} input total: {n:,} rows "
          f"(decider={n_dec:,}, non-decider={n_ndec:,})")
    return combined


def _validate_block_input(block_f: int, df: pd.DataFrame) -> dict:
    """Per-block validation per amendment §16."""
    halts = []
    # scalar draw column values exactly 0..29 on decider rows
    if "draw" not in df.columns:
        halts.append("HE2: scalar 'draw' column absent")
    else:
        dec = df[df["is_decider"] == 1]
        dec_draws = sorted(dec["draw"].unique().tolist())
        expected = list(range(N_MALE_DRAWS))
        if dec_draws != expected:
            halts.append(f"HE2: decider draw set {dec_draws[:5]}..{dec_draws[-5:]} != 0..{N_MALE_DRAWS - 1}")
    # is_decider==1 for BOTH partners
    dec_rows = int((df["is_decider"] == 1).sum())
    expected_dec = EXPECTED_COUPLES * N_MALE_DRAWS * 2  # 154,620
    if dec_rows != expected_dec:
        halts.append(f"HE-DEC: decider rows {dec_rows:,} != expected {expected_dec:,}")
    # dgn split: half male, half female on decider rows
    if "dgn" in df.columns:
        dec = df[df["is_decider"] == 1]
        n_male = int((dec["dgn"] == 1.0).sum())
        n_female = int((dec["dgn"] == 0.0).sum())
        if n_male != EXPECTED_COUPLES * N_MALE_DRAWS or n_female != EXPECTED_COUPLES * N_MALE_DRAWS:
            halts.append(f"HE-DEC: decider gender split male={n_male:,} female={n_female:,} "
                         f"(expected {EXPECTED_COUPLES * N_MALE_DRAWS:,} each)")
    # 5 stray ils_* absent
    stray = [c for c in STRAY_ILS_COLS if c in df.columns]
    if stray:
        halts.append(f"HE2: stray ils_* present: {stray}")
    # required columns present
    for col in ("idperson", "idhh", "draw", "is_decider", "block_f", "hours", "wage", "yem", "yivwg", "lhw"):
        if col not in df.columns:
            halts.append(f"HE2: required column '{col}' absent")
    # block_f matches
    if "block_f" in df.columns and df["block_f"].nunique() == 1:
        if int(df["block_f"].iloc[0]) != block_f:
            halts.append(f"HE2: block_f column = {df['block_f'].iloc[0]} != expected {block_f}")
    return {
        "block_f": block_f,
        "n_rows": int(len(df)),
        "n_decider": dec_rows,
        "expected_decider": expected_dec,
        "decider_draw_range": (
            int(df.loc[df["is_decider"] == 1, "draw"].min()) if dec_rows else None,
            int(df.loc[df["is_decider"] == 1, "draw"].max()) if dec_rows else None,
        ),
        "stray_present": stray,
        "halts": halts,
    }


def _write_drawsmeta(path: Path, block_f: int, n_rows: int, n_decider: int) -> None:
    meta = {
        "schema_version": "nc_pilot_em_input_v2_blockwise",
        "produced_by": "scripts/pilot/export_pilot_euromod_inputs_v2.py",
        "produced_at_utc": datetime.now(timezone.utc).isoformat(),
        "authorization": "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage5_strategy_amendment_v2.md",
        "strategy": "C_prime_blockwise_joint_product",
        "block_f": int(block_f),
        "household_type": "couples",
        "n_draws": N_MALE_DRAWS,
        "max_draw": N_MALE_DRAWS - 1,
        "id_multiplier": ID_MULTIPLIER,
        "n_rows": int(n_rows),
        "n_decider_rows": int(n_decider),
        "both_partners_deciders": True,
        "scalar_draw_meaning": "male marginal m in {0..29}",
        "female_draw_constant": int(block_f),
        "draw_joint_formula": "30*draw_male + draw_female (reconstructed in later merge slice)",
        "source_pilot_product": str(PILOT_PRODUCT),
        "source_production_baseline": str(PROD_COUPLES_DRAWS),
        "stray_ils_columns_dropped": list(STRAY_ILS_COLS),
        "is_decider_set_explicitly": True,
        "wage_provenance": (
            "Both partners decider: male draw-m hours/wage/yem from pilot W1 wide "
            "product parquet (varies); female draw-f hours/wage/yem from pilot wide "
            "product parquet (block constant). delta_occ calibrated via "
            "scripts/pilot/config/pilot_mincer_coefficients_v1.json."
        ),
    }
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[adapter v2] wrote drawsmeta sidecar:\n  {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--block-f", type=int, required=True,
                    help="Female draw index for this block (0..29).")
    args = ap.parse_args()
    block_f = args.block_f
    if not 0 <= block_f <= 29:
        print(f"[adapter v2] ERROR: --block-f must be in 0..29; got {block_f}", file=sys.stderr)
        return 2

    if not PILOT_PRODUCT.exists():
        print(f"[adapter v2] ERROR: pilot product parquet not found at {PILOT_PRODUCT}", file=sys.stderr)
        return 2
    if not PROD_COUPLES_DRAWS.exists():
        print(f"[adapter v2] ERROR: production couples draws file not found at {PROD_COUPLES_DRAWS}", file=sys.stderr)
        return 2

    block_dir = EM_INPUTS_DIR / f"block_f{block_f:02d}"
    block_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = block_dir / f"fr_pilot_2016_couples_block_f{block_f:02d}_draws.parquet"
    out_meta = block_dir / f"fr_pilot_2016_couples_block_f{block_f:02d}_draws__drawsmeta.json"

    baseline = _load_production_baseline_couples()
    male_slice = _load_pilot_partner_slice("male")
    female_slice = _load_pilot_partner_slice("female")

    frame = build_block_input(block_f, baseline, male_slice, female_slice)

    validation = _validate_block_input(block_f, frame)
    print(f"[adapter v2] validation: {validation}")
    if validation["halts"]:
        for h in validation["halts"]:
            print(f"[adapter v2] HALT: {h}", file=sys.stderr)
        return 3

    print(f"[adapter v2] writing block f={block_f:02d} input parquet:\n  {out_parquet}")
    frame.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")
    bytes_ = out_parquet.stat().st_size
    print(f"[adapter v2] wrote {bytes_:,} bytes")
    _write_drawsmeta(out_meta, block_f, n_rows=len(frame), n_decider=validation["n_decider"])
    print(f"[adapter v2] DONE block f={block_f:02d}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
