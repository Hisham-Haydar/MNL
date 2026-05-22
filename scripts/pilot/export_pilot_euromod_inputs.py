#!/usr/bin/env python
"""
NC pilot — Stage 5 adapter: export per-partner long-format EUROMOD inputs.

Authorized by: docs/JMP_NC_pilot_stage5_euromod_amendment_v1.md (Stages 1-2
of the Stage-5 §20 task). Pilot-only. Production runner not modified.

Strategy B: project the pilot wide product parquet (and the production
long-format draws file as the source of EUROMOD-input baseline columns)
into TWO long-format frames — one per partner — each in the shape the
production runner expects:

  - one row per (idperson_partner_being_varied, draw) with draw in {0..29};
  - the other partner and any children appear as non-deciders at draw=0,
    replicated across draws 0..29 by the runner's existing logic;
  - is_decider = 1 set EXPLICITLY on decider rows (HE-DEC).

Outputs:
  Data/pilot/nc_2016_couples/em_inputs/
    fr_pilot_2016_couples_male_partner_draws.parquet
    fr_pilot_2016_couples_male_partner_draws__drawsmeta.json
    fr_pilot_2016_couples_female_partner_draws.parquet
    fr_pilot_2016_couples_female_partner_draws__drawsmeta.json

Notes:
  - Five stray ils_* columns from the pilot wide parquet are explicitly
    dropped here (ils_earns, ils_origy, ils_pen, ils_sicdy, ils_earns_real).
  - id_multiplier = 1000 is hard-set in both drawsmeta sidecars (HE-DRAWSMETA).
  - Per-partner W1 wages come from the pilot wide product parquet
    (wage_{male,female}); the per-row Mincer covariates (educL/H, pexp_years,
    pexp_years2) likewise come from the wide parquet; the rest of the EUROMOD
    template carry comes from the production FR_2016 couples draws file
    (the SAME baseline `draw=0` rows the production pipeline already validated).

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
PROD_COUPLES_DRAWSMETA = Path(r"U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws__drawsmeta.json")

YEAR_TAG_2016 = 2
PRODUCT_SIZE = 30
N_DRAWS = 30  # pilot per-partner marginal draws
ID_MULTIPLIER = 1000

STRAY_ILS_COLS = ("ils_earns", "ils_origy", "ils_pen", "ils_sicdy", "ils_earns_real")


def _load_production_couples_baseline() -> pd.DataFrame:
    """Load the production FR_2016 couples draws file at draw=0 only.

    This is the source of EUROMOD-template carry columns. Filtering to
    draw=0 gives one baseline row per person; for the pilot we will
    re-draw the decider's hours/wage/yem at 30 new draws using the W1
    values from the pilot wide product parquet, while non-decider rows
    (children, other-partner-during-its-non-decider-pass) are kept at
    their observed baseline.
    """
    print(f"[adapter] reading production FR_2016 couples draws (baseline rows)...")
    df = pd.read_parquet(PROD_COUPLES_DRAWS)
    df0 = df[df["draw"] == 0].copy()
    print(f"[adapter] production couples draws=0 baseline rows: {len(df0):,}")
    print(f"[adapter] unique idhh in baseline: {df0['idhh'].nunique():,}")
    return df0


def _load_pilot_partner_draws(side: str) -> pd.DataFrame:
    """Read the pilot wide product parquet and project to one-row-per
    (idperson_<side>, draw_<side>) for the partner side.

    The pilot product parquet has 2,319,300 rows. For the decider partner,
    we need 30 rows per partner-person — one per marginal draw. We obtain
    these by taking the rows where the OTHER partner's marginal draw == 0
    (which keeps one record per (idperson_partner, draw_partner)).
    """
    assert side in ("male", "female")
    other = "female" if side == "male" else "male"

    print(f"[adapter] reading pilot wide product parquet for {side} decider rows...")
    # Filter to draw_{other} == 0 so we get exactly 30 rows per couple.
    # That gives 2,577 * 30 = 77,310 rows per pass.
    other_filter_col = f"draw_{other}"
    decider_draw_col = f"draw_{side}"

    needed = [
        "idhh",
        decider_draw_col,
        other_filter_col,
        f"loc4_{side}",
        f"wage_{side}",
        f"hours_{side}",
        f"yem_{side}",
        f"educL_{side}",
        f"educH_{side}",
        f"pexp_years_{side}",
        f"pexp_years2_{side}",
    ]
    wide = pd.read_parquet(PILOT_PRODUCT, columns=needed)
    sub = wide[wide[other_filter_col] == 0].copy()
    sub = sub.rename(columns={decider_draw_col: "draw_partner"})
    sub = sub.drop(columns=[other_filter_col])
    print(f"[adapter] {side} decider product slice: {len(sub):,} rows "
          f"(expected {2577 * 30:,})")
    return sub


def _build_partner_pass_input(side: str, prod_baseline: pd.DataFrame,
                              pilot_slice: pd.DataFrame) -> pd.DataFrame:
    """Build the long-format EUROMOD input frame for one partner pass.

    Decider rows: one per (idperson_side, draw in 0..29), with hours/wage/yem
    from the pilot product slice (W1-calibrated).

    Non-decider rows: one per remaining person in the household (the other
    partner + any children), at the production baseline values, draw=0 only
    (the runner will replicate them across draws 0..29).
    """
    other = "female" if side == "male" else "male"
    dgn_decider = 1.0 if side == "male" else 0.0
    print(f"[adapter] building {side} partner pass input...")

    # Identify decider persons: those in prod_baseline who are
    # RURO deciders (head/partner) AND of the partner's gender. This
    # excludes adult co-residents of the same sex (e.g., adult sons)
    # who appear in the household but are not the labour-supply decider.
    is_ruro_decider = prod_baseline["is_decider"] == 1
    is_target_gender = prod_baseline["dgn"] == dgn_decider
    deciders_baseline = prod_baseline[is_ruro_decider & is_target_gender].copy()
    # Drop the production draw column (all 0) before expansion to avoid
    # duplicate-column collisions in the subsequent merges
    if "draw" in deciders_baseline.columns:
        deciders_baseline = deciders_baseline.drop(columns=["draw"])
    n_decider_persons = len(deciders_baseline)
    print(f"[adapter] decider baseline persons ({side}, RURO-decider + dgn={dgn_decider}): "
          f"{n_decider_persons:,}")
    if n_decider_persons != 2577:
        print(f"[adapter] WARN: expected 2,577 {side} deciders (one per couple); "
              f"got {n_decider_persons:,}", file=sys.stderr)

    # Cross-join decider baselines with draws 0..29
    draws = pd.DataFrame({"draw": np.arange(N_DRAWS, dtype=np.int32), "_k": 1})
    deciders_keyed = deciders_baseline.assign(_k=1)
    decider_expanded = deciders_keyed.merge(draws, on="_k").drop(columns="_k")
    print(f"[adapter] decider rows after 30-draw expansion: {len(decider_expanded):,}")

    # Replace decider hours/wage/yem from pilot product slice on (idhh, draw)
    # Map idhh -> decider's idperson to do a (idhh, draw) join
    pilot_keyed = pilot_slice.rename(columns={"draw_partner": "draw"})
    pilot_keyed = pilot_keyed[[
        "idhh", "draw",
        f"loc4_{side}", f"wage_{side}", f"hours_{side}", f"yem_{side}",
    ]].rename(columns={
        f"loc4_{side}": "loc4_pilot",
        f"wage_{side}": "wage_pilot",
        f"hours_{side}": "hours_pilot",
        f"yem_{side}": "yem_pilot",
    })
    # Production baseline's idhh is float; convert pilot idhh to same type
    pilot_keyed["idhh"] = pilot_keyed["idhh"].astype(decider_expanded["idhh"].dtype)
    decider_expanded = decider_expanded.merge(pilot_keyed, on=["idhh", "draw"], how="left")

    # For decider rows: overwrite hours, wage, yem, loc4 with pilot values
    # (draw==0 should match observed; draws 1..29 are W1-redrawn).
    mask_pilot = decider_expanded["wage_pilot"].notna()
    n_pilot_applied = int(mask_pilot.sum())
    print(f"[adapter] decider rows with pilot W1 values applied: {n_pilot_applied:,} "
          f"(expected {2577 * 30:,})")
    # Apply: hours -> lhw too; wage -> yivwg too
    decider_expanded.loc[mask_pilot, "hours"] = decider_expanded.loc[mask_pilot, "hours_pilot"]
    decider_expanded.loc[mask_pilot, "lhw"] = decider_expanded.loc[mask_pilot, "hours_pilot"]
    decider_expanded.loc[mask_pilot, "wage"] = decider_expanded.loc[mask_pilot, "wage_pilot"]
    decider_expanded.loc[mask_pilot, "yivwg"] = decider_expanded.loc[mask_pilot, "wage_pilot"]
    decider_expanded.loc[mask_pilot, "yem"] = decider_expanded.loc[mask_pilot, "yem_pilot"]
    decider_expanded.loc[mask_pilot, "loc4"] = decider_expanded.loc[mask_pilot, "loc4_pilot"]
    # loc_ruro is the alternative occupation code; if present, set to loc4 too
    if "loc_ruro" in decider_expanded.columns:
        decider_expanded.loc[mask_pilot, "loc_ruro"] = decider_expanded.loc[mask_pilot, "loc4_pilot"]

    decider_expanded = decider_expanded.drop(columns=[
        "loc4_pilot", "wage_pilot", "hours_pilot", "yem_pilot"
    ])
    decider_expanded["is_decider"] = 1

    # Non-deciders: all production baseline rows that are NOT the decider partner;
    # i.e. other-partner (dgn != dgn_decider) AND children (whose dgn may be anything).
    # We use is_decider==0 from the production baseline to identify children;
    # for the other adult partner, we mark is_decider=0 explicitly for this pass.
    other_baseline = prod_baseline[
        (prod_baseline["dgn"] != dgn_decider) | (prod_baseline["is_decider"] == 0)
    ].copy()
    # Avoid double-counting: a person is in other_baseline if (dgn!=decider OR is_decider==0).
    # That correctly excludes the decider partner himself/herself.
    other_baseline["is_decider"] = 0
    other_baseline["draw"] = 0  # runner replicates draw=0 non-deciders across all draws
    print(f"[adapter] non-decider rows (other partner + children) at draw=0: {len(other_baseline):,}")

    # Combine
    combined = pd.concat([decider_expanded, other_baseline], axis=0, ignore_index=True, sort=False)

    # Drop the five stray ils_* columns if present (paranoid: they live on the
    # pilot wide parquet, NOT on the production baseline; but if they leaked
    # in via column reuse, drop them).
    drop_cols = [c for c in STRAY_ILS_COLS if c in combined.columns]
    if drop_cols:
        combined = combined.drop(columns=drop_cols)
        print(f"[adapter] dropped stray ils_* columns: {drop_cols}")
    else:
        print(f"[adapter] no stray ils_* columns present (already absent from production baseline)")

    print(f"[adapter] total rows for {side} pass: {len(combined):,}")
    print(f"[adapter]   decider rows (is_decider==1): {(combined['is_decider']==1).sum():,}")
    print(f"[adapter]   non-decider rows (is_decider==0): {(combined['is_decider']==0).sum():,}")
    print(f"[adapter]   draw range: {combined['draw'].min()}..{combined['draw'].max()}")
    return combined


def _validate_partner_input(side: str, df: pd.DataFrame) -> dict:
    """Stage-5 §15 per-pass adapter validations BEFORE running EUROMOD."""
    halts = []
    # 1. Scalar draw column present, decider values exactly 0..29
    if "draw" not in df.columns:
        halts.append("HE2: scalar 'draw' column absent")
    else:
        decider = df[df["is_decider"] == 1]
        decider_draws = sorted(decider["draw"].unique().tolist())
        expected = list(range(N_DRAWS))
        if decider_draws != expected:
            halts.append(f"HE2: decider draw set {decider_draws[:5]}..{decider_draws[-5:]} "
                         f"!= expected 0..{N_DRAWS-1}")
    # 2. is_decider == 1 on decider rows (count = couples * 30)
    n_decider = int((df["is_decider"] == 1).sum())
    expected_decider = 2577 * N_DRAWS
    if n_decider != expected_decider:
        halts.append(f"HE-DEC: decider rows {n_decider:,} != expected {expected_decider:,}")
    # 3. 5 stray ils_* columns absent
    stray_present = [c for c in STRAY_ILS_COLS if c in df.columns]
    if stray_present:
        halts.append(f"HE2: stray ils_* columns present: {stray_present}")
    # 4. idperson and idhh present
    for col in ("idperson", "idhh", "draw", "is_decider"):
        if col not in df.columns:
            halts.append(f"HE2: required column '{col}' absent")
    return {
        "n_decider": n_decider,
        "expected_decider": expected_decider,
        "decider_draw_range": (
            int(df.loc[df["is_decider"] == 1, "draw"].min()) if n_decider else None,
            int(df.loc[df["is_decider"] == 1, "draw"].max()) if n_decider else None,
        ),
        "stray_ils_present": stray_present,
        "halts": halts,
    }


def _write_drawsmeta(path: Path, side: str, n_rows: int) -> None:
    meta = {
        "schema_version": "nc_pilot_em_input_v1",
        "produced_by": "scripts/pilot/export_pilot_euromod_inputs.py",
        "produced_at_utc": datetime.now(timezone.utc).isoformat(),
        "authorization": "docs/JMP_NC_pilot_stage5_euromod_amendment_v1.md",
        "partner_side": side,
        "household_type": "couples",
        "n_draws": N_DRAWS,
        "max_draw": N_DRAWS - 1,
        "id_multiplier": ID_MULTIPLIER,
        "n_rows": int(n_rows),
        "source_pilot_product": str(PILOT_PRODUCT),
        "source_production_baseline": str(PROD_COUPLES_DRAWS),
        "wage_provenance": (
            "Decider hours/wage/yem on draws 1..29 sourced from pilot wide "
            "product parquet (W1 occupation-conditioned log-normal draws "
            "calibrated by scripts/pilot/config/pilot_mincer_coefficients_v1.json). "
            "Decider draw=0 values match observed baseline. "
            "Non-decider rows held at production baseline; runner replicates "
            "across draws."
        ),
        "is_decider_set_explicitly": True,
        "stray_ils_columns_dropped": list(STRAY_ILS_COLS),
    }
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[adapter] wrote drawsmeta sidecar:\n  {path}")


def main() -> int:
    # Read shared inputs
    if not PILOT_PRODUCT.exists():
        print(f"[adapter] ERROR: pilot product parquet not found at {PILOT_PRODUCT}", file=sys.stderr)
        return 2
    if not PROD_COUPLES_DRAWS.exists():
        print(f"[adapter] ERROR: production couples draws file not found at {PROD_COUPLES_DRAWS}", file=sys.stderr)
        return 2

    EM_INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load baseline once
    prod_baseline = _load_production_couples_baseline()
    # Restrict to FR_2016 idhh (production single-year)
    print(f"[adapter] production baseline already FR_2016 only ({len(prod_baseline):,} rows)")

    halts_total = []

    for side in ("male", "female"):
        print(f"\n=== {side.upper()} PARTNER PASS ===")
        pilot_slice = _load_pilot_partner_draws(side)
        frame = _build_partner_pass_input(side, prod_baseline, pilot_slice)
        validation = _validate_partner_input(side, frame)
        print(f"[adapter] validation: {validation}")
        if validation["halts"]:
            for h in validation["halts"]:
                print(f"[adapter] HALT: {h}", file=sys.stderr)
            halts_total.extend(validation["halts"])
            continue
        out_parquet = EM_INPUTS_DIR / f"fr_pilot_2016_couples_{side}_partner_draws.parquet"
        out_meta = EM_INPUTS_DIR / f"fr_pilot_2016_couples_{side}_partner_draws__drawsmeta.json"
        print(f"[adapter] writing {side} input parquet:\n  {out_parquet}")
        frame.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")
        bytes_ = out_parquet.stat().st_size
        print(f"[adapter] wrote {bytes_:,} bytes")
        _write_drawsmeta(out_meta, side, n_rows=len(frame))

    if halts_total:
        print(f"\n[adapter] HALTED: {len(halts_total)} validation failures", file=sys.stderr)
        return 3
    print(f"\n[adapter] DONE. Both partner inputs + drawsmeta written.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    _ = ap.parse_args()
    sys.exit(main())
