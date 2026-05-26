#!/usr/bin/env python
"""
NC pilot — Post-EUROMOD merge slice.

Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md

Assembles the 30 Strategy C' EUROMOD block outputs into one wide post-EM
product parquet carrying partner-specific disposable income (ils_dispy_male,
ils_dispy_female) for all 2,319,300 joint alternatives.

Hard constraints (amendment §14):
- HM1: Inputs READ-ONLY; never overwrite Stage-4 product or Stage-5 blocks.
- HM2: Merge on idperson_true/idhh_true ONLY; never encoded idperson/idhh.
- HM3: idhh_true must match product household IDs in scope.
- HM4: Male/female idperson_true mapping must be one-to-one, unambiguous.
- HM5: No duplicate (idperson_true, draw, block_f) decider rows; no
       duplicate (idhh, m, f) in either partner-income table.
- HM6: Exactly one ils_dispy_male and one ils_dispy_female per product row.
- HM7: Reconstructed 30*draw_male + draw_female == product draw_joint on all rows.
- HM8: Merged row count == 2,319,300; chosen-row count == 2,577 at draw_joint==0.
- HM9: ils_dispy_male and ils_dispy_female non-missing on all 2,319,300 rows.
- HM-STAGE: No is_chosen aliasing, chosen-first sorting, GSUR, precompute,
             estimation, welfare, SA2, promotion, or M1-clean displacement.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
# Data lives under the configured storage root, not the repo working tree (migrated 2026-05-26).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from path_helpers import data_root  # noqa: E402
PILOT_DATA = data_root() / "pilot" / "nc_2016_couples"
PRODUCT_PARQUET = PILOT_DATA / "fr_pilot_nc_2016_couples_product.parquet"
EM_INPUTS_DIR = PILOT_DATA / "em_inputs"
EM_OUTPUTS_DIR = PILOT_DATA / "em_outputs"
OUT_PARQUET = PILOT_DATA / "fr_pilot_nc_2016_couples_product__post_em.parquet"
OUT_META = PILOT_DATA / "fr_pilot_nc_2016_couples_product__post_em__mergemeta.json"

PRODUCT_SIZE = 30
EXPECTED_COUPLES = 2577
EXPECTED_ROWS = EXPECTED_COUPLES * PRODUCT_SIZE * PRODUCT_SIZE  # 2,319,300


def halt(code: str, msg: str) -> None:
    print(f"\n[merge] HALT {code}: {msg}", file=sys.stderr)
    sys.exit(f"HALTED: {code} — {msg}")


def load_decider_ids() -> tuple[set, set]:
    """Load the 5,154 decider idperson values from block f=00 adapter input.

    The decider set is constant across all blocks (same 2,577 couples x 2
    partners). We split into male (dgn==1.0) and female (dgn==0.0) subsets.
    Returns (male_ids, female_ids) as sets of float.
    """
    p = EM_INPUTS_DIR / "block_f00" / "fr_pilot_2016_couples_block_f00_draws.parquet"
    df = pd.read_parquet(p, columns=["idperson", "is_decider", "dgn"])
    dec = df[df["is_decider"] == 1][["idperson", "dgn"]].drop_duplicates()
    male_ids = set(dec[dec["dgn"] == 1.0]["idperson"].astype(float).unique())
    female_ids = set(dec[dec["dgn"] == 0.0]["idperson"].astype(float).unique())
    print(f"[merge] decider IDs loaded: {len(male_ids)} male, {len(female_ids)} female")
    return male_ids, female_ids


def load_product_hh_map() -> pd.DataFrame:
    """Load the product parquet household mapping: (idhh, idperson=male, idpartner=female).

    Returns one row per couple (from chosen alternatives at draw_male==0,
    draw_female==0). Columns: idhh, idperson_male_prod, idperson_female_prod.
    """
    prod = pd.read_parquet(
        PRODUCT_PARQUET,
        columns=["idhh", "idperson", "idpartner", "draw_male", "draw_female"],
    )
    chosen = prod[(prod["draw_male"] == 0) & (prod["draw_female"] == 0)].copy()
    hh_map = chosen[["idhh", "idperson", "idpartner"]].rename(
        columns={"idperson": "idperson_male_prod", "idpartner": "idperson_female_prod"}
    )
    if len(hh_map) != EXPECTED_COUPLES:
        halt("HM8", f"Product chosen-row count {len(hh_map)} != {EXPECTED_COUPLES}")
    print(f"[merge] product household map: {len(hh_map):,} couples")
    return hh_map


def validate_partner_mapping(
    male_ids: set,
    female_ids: set,
    hh_map: pd.DataFrame,
) -> None:
    """Validate one-to-one male/female idperson_true -> product partner mapping (HM4)."""
    prod_male = set(hh_map["idperson_male_prod"].astype(float).unique())
    prod_female = set(hh_map["idperson_female_prod"].astype(float).unique())

    # Perfect match
    if male_ids != prod_male:
        missing = len(prod_male - male_ids)
        extra = len(male_ids - prod_male)
        halt("HM4", f"EM male decider IDs don't match product idperson: "
             f"missing={missing}, extra={extra}")
    if female_ids != prod_female:
        missing = len(prod_female - female_ids)
        extra = len(female_ids - prod_female)
        halt("HM4", f"EM female decider IDs don't match product idpartner: "
             f"missing={missing}, extra={extra}")

    # No crossovers
    cross_m_f = len(male_ids & prod_female)
    cross_f_m = len(female_ids & prod_male)
    if cross_m_f > 0:
        halt("HM4", f"EM male IDs appear in product female column: {cross_m_f} crossovers")
    if cross_f_m > 0:
        halt("HM4", f"EM female IDs appear in product male column: {cross_f_m} crossovers")

    print(f"[merge] HM4 partner mapping: PASS (male={len(male_ids)}, female={len(female_ids)}, no crossovers)")


def process_block(
    block_f: int,
    male_ids: set,
    female_ids: set,
    hh_map: pd.DataFrame,
    prod_idhh_set: set,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Process one block's EUROMOD output: filter to deciders, classify by gender,
    extract (idhh_true, draw_male, draw_female, ils_dispy) for each partner.

    Returns (male_income_df, female_income_df) with columns:
      male:   idhh, draw_male, draw_female, ils_dispy_male
      female: idhh, draw_male, draw_female, ils_dispy_female
    """
    block_dir = EM_OUTPUTS_DIR / f"block_f{block_f:02d}"
    em_path = block_dir / "combined_draws_em.parquet"

    df = pd.read_parquet(
        em_path,
        columns=["idhh_true", "idperson_true", "draw", "dgn", "ils_dispy"],
    )

    # Filter to decider rows using the idperson_true membership test
    all_decider_ids = male_ids | female_ids
    dec_mask = df["idperson_true"].astype(float).isin(all_decider_ids)
    dec = df[dec_mask].copy()
    n_dec = len(dec)
    expected_dec = EXPECTED_COUPLES * PRODUCT_SIZE * 2  # 154,620
    if n_dec != expected_dec:
        halt("HM5", f"Block f={block_f}: decider rows {n_dec} != expected {expected_dec}")

    # Validate idhh_true in scope (HM3)
    em_idhh = set(dec["idhh_true"].astype(float).unique())
    missing_idhh = em_idhh - prod_idhh_set
    if missing_idhh:
        halt("HM3", f"Block f={block_f}: {len(missing_idhh)} idhh_true not in product parquet")

    # Add block constant f and reconstruct draw keys
    dec = dec.rename(columns={"idhh_true": "idhh", "draw": "draw_male"})
    dec["idhh"] = dec["idhh"].astype(float)
    dec["draw_female"] = block_f
    dec["draw_male"] = dec["draw_male"].astype(int)

    # Check no duplicate (idperson_true, draw_male, block_f) rows (HM5)
    dup_check = dec.duplicated(subset=["idperson_true", "draw_male"], keep=False)
    if dup_check.any():
        halt("HM5", f"Block f={block_f}: duplicate (idperson_true, draw) decider rows: "
             f"{dup_check.sum()}")

    # Split into male and female income rows
    male_mask_dec = dec["idperson_true"].astype(float).isin(male_ids)
    female_mask_dec = dec["idperson_true"].astype(float).isin(female_ids)

    male_rows = dec[male_mask_dec][["idhh", "draw_male", "draw_female", "ils_dispy"]].copy()
    female_rows = dec[female_mask_dec][["idhh", "draw_male", "draw_female", "ils_dispy"]].copy()

    male_rows = male_rows.rename(columns={"ils_dispy": "ils_dispy_male"})
    female_rows = female_rows.rename(columns={"ils_dispy": "ils_dispy_female"})

    expected_side = EXPECTED_COUPLES * PRODUCT_SIZE  # 77,310 per side per block
    if len(male_rows) != expected_side:
        halt("HM5", f"Block f={block_f}: male income rows {len(male_rows)} != {expected_side}")
    if len(female_rows) != expected_side:
        halt("HM5", f"Block f={block_f}: female income rows {len(female_rows)} != {expected_side}")

    # Validate one row per (idhh, draw_male, draw_female) in each table (HM5)
    dup_m = male_rows.duplicated(subset=["idhh", "draw_male", "draw_female"], keep=False)
    if dup_m.any():
        halt("HM5", f"Block f={block_f}: duplicate (idhh, m, f) in male income table: {dup_m.sum()}")
    dup_f = female_rows.duplicated(subset=["idhh", "draw_male", "draw_female"], keep=False)
    if dup_f.any():
        halt("HM5", f"Block f={block_f}: duplicate (idhh, m, f) in female income table: {dup_f.sum()}")

    return male_rows, female_rows


def main() -> int:
    t_start = datetime.now(timezone.utc)
    print(f"[merge] NC pilot post-EUROMOD merge slice")
    print(f"[merge] Authorization: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md")
    print(f"[merge] Start: {t_start.isoformat()}")

    # STEP 1: Confirm product partner-ID columns
    print("\n[merge] STEP 1: Loading product parquet and decider IDs...")
    male_ids, female_ids = load_decider_ids()
    hh_map = load_product_hh_map()
    prod_idhh_set = set(hh_map["idhh"].astype(float).unique())
    validate_partner_mapping(male_ids, female_ids, hh_map)

    # STEP 2+3: Per-block processing
    print(f"\n[merge] STEP 2+3: Processing {PRODUCT_SIZE} blocks...")
    all_male = []
    all_female = []
    block_stats = []

    for block_f in range(PRODUCT_SIZE):
        m_df, f_df = process_block(block_f, male_ids, female_ids, hh_map, prod_idhh_set)
        all_male.append(m_df)
        all_female.append(f_df)
        block_stats.append({
            "block_f": block_f,
            "male_rows": len(m_df),
            "female_rows": len(f_df),
        })
        if block_f % 5 == 0 or block_f == PRODUCT_SIZE - 1:
            print(f"[merge]   block f={block_f:02d}: male={len(m_df):,}  female={len(f_df):,}")

    male_income = pd.concat(all_male, ignore_index=True)
    female_income = pd.concat(all_female, ignore_index=True)
    print(f"[merge] Combined male income table: {len(male_income):,} rows")
    print(f"[merge] Combined female income table: {len(female_income):,} rows")

    # Final duplicate check across all blocks (HM5)
    dup_m_all = male_income.duplicated(subset=["idhh", "draw_male", "draw_female"], keep=False)
    if dup_m_all.any():
        halt("HM5", f"Global male income table has {dup_m_all.sum()} duplicate (idhh, m, f) rows")
    dup_f_all = female_income.duplicated(subset=["idhh", "draw_male", "draw_female"], keep=False)
    if dup_f_all.any():
        halt("HM5", f"Global female income table has {dup_f_all.sum()} duplicate (idhh, m, f) rows")

    expected_income_rows = EXPECTED_COUPLES * PRODUCT_SIZE * PRODUCT_SIZE  # 2,319,300
    if len(male_income) != expected_income_rows:
        halt("HM8", f"Male income table {len(male_income):,} != {expected_income_rows:,}")
    if len(female_income) != expected_income_rows:
        halt("HM8", f"Female income table {len(female_income):,} != {expected_income_rows:,}")

    # STEP 4: Wide merge onto product parquet
    print(f"\n[merge] STEP 4: Loading product parquet and merging income...")
    product = pd.read_parquet(PRODUCT_PARQUET)
    print(f"[merge] Product parquet: {len(product):,} rows x {len(product.columns)} cols")

    # Cast merge keys to consistent types
    product["idhh"] = product["idhh"].astype(float)
    product["draw_male"] = product["draw_male"].astype(int)
    product["draw_female"] = product["draw_female"].astype(int)
    male_income["idhh"] = male_income["idhh"].astype(float)
    male_income["draw_male"] = male_income["draw_male"].astype(int)
    male_income["draw_female"] = male_income["draw_female"].astype(int)
    female_income["idhh"] = female_income["idhh"].astype(float)
    female_income["draw_male"] = female_income["draw_male"].astype(int)
    female_income["draw_female"] = female_income["draw_female"].astype(int)

    merged = product.merge(
        male_income, on=["idhh", "draw_male", "draw_female"], how="left"
    )
    merged = merged.merge(
        female_income, on=["idhh", "draw_male", "draw_female"], how="left"
    )
    print(f"[merge] After merge: {len(merged):,} rows x {len(merged.columns)} cols")

    # HM6: Exactly one income per product row (check no merge fan-out)
    if len(merged) != len(product):
        halt("HM6", f"Merge produced {len(merged):,} rows vs product {len(product):,}; "
             f"check for duplicate income keys causing fan-out")

    # HM7: draw_joint reconstruction consistency
    reconstructed_dj = 30 * merged["draw_male"] + merged["draw_female"]
    dj_mismatch = (reconstructed_dj != merged["draw_joint"]).sum()
    if dj_mismatch > 0:
        halt("HM7", f"{dj_mismatch} rows where 30*draw_male+draw_female != draw_joint")
    print(f"[merge] HM7 draw_joint consistency: PASS (all {len(merged):,} rows consistent)")

    # STEP 6: Validate
    print(f"\n[merge] STEP 6: Final validation checks...")

    # HM8: Row count
    if len(merged) != EXPECTED_ROWS:
        halt("HM8", f"Merged row count {len(merged):,} != {EXPECTED_ROWS:,}")
    print(f"[merge] HM8 row count: PASS ({len(merged):,})")

    # HM8: Chosen row count
    chosen_rows = merged[(merged["draw_male"] == 0) & (merged["draw_female"] == 0) &
                         (merged["draw_joint"] == 0)]
    if len(chosen_rows) != EXPECTED_COUPLES:
        halt("HM8", f"Chosen-row count {len(chosen_rows)} != {EXPECTED_COUPLES}")
    print(f"[merge] HM8 chosen rows: PASS ({len(chosen_rows):,} at draw_joint==0)")

    # HM9: Income completeness
    n_missing_male = merged["ils_dispy_male"].isna().sum()
    n_missing_female = merged["ils_dispy_female"].isna().sum()
    if n_missing_male > 0:
        halt("HM9", f"ils_dispy_male missing on {n_missing_male:,} rows")
    if n_missing_female > 0:
        halt("HM9", f"ils_dispy_female missing on {n_missing_female:,} rows")
    print(f"[merge] HM9 income completeness: PASS (0 missing on both columns)")

    # HM6: Confirm no multiple-match artifacts
    if merged["ils_dispy_male"].isna().any() or merged["ils_dispy_female"].isna().any():
        halt("HM6", "Income columns have unexpected NaN (join coverage gap)")

    # HM1: Check product and block outputs unchanged (row counts)
    import pyarrow.parquet as pq
    prod_rows = pq.read_metadata(PRODUCT_PARQUET).num_rows
    if prod_rows != EXPECTED_ROWS:
        halt("HM1", f"Stage-4 product parquet changed: {prod_rows:,} rows != {EXPECTED_ROWS:,}")
    print(f"[merge] HM1 Stage-4 product unchanged: PASS ({prod_rows:,} rows)")

    block_row_check = []
    for block_f in range(PRODUCT_SIZE):
        em_path = EM_OUTPUTS_DIR / f"block_f{block_f:02d}" / "combined_draws_em.parquet"
        n = pq.read_metadata(em_path).num_rows
        block_row_check.append({"block_f": block_f, "rows": n, "ok": n == 254340})
        if n != 254340:
            halt("HM1", f"Block f={block_f} output changed: {n} rows != 254,340")
    print(f"[merge] HM1 all 30 block outputs unchanged: PASS")

    # STEP 5: Write output
    print(f"\n[merge] STEP 5: Writing output...")
    # Final column set: 149 base + ils_dispy_male + ils_dispy_female = 151
    out_cols = [c for c in merged.columns if c in product.columns or c in ("ils_dispy_male", "ils_dispy_female")]
    merged_out = merged[out_cols]
    print(f"[merge] Output columns: {len(merged_out.columns)} (expected 151)")

    merged_out.to_parquet(OUT_PARQUET, index=False, engine="pyarrow", compression="snappy")
    out_bytes = OUT_PARQUET.stat().st_size
    print(f"[merge] Wrote: {OUT_PARQUET}\n  {out_bytes:,} bytes")

    # Income summary stats
    male_income_stats = {
        "mean": float(merged["ils_dispy_male"].mean()),
        "std": float(merged["ils_dispy_male"].std()),
        "min": float(merged["ils_dispy_male"].min()),
        "max": float(merged["ils_dispy_male"].max()),
        "n_missing": int(n_missing_male),
    }
    female_income_stats = {
        "mean": float(merged["ils_dispy_female"].mean()),
        "std": float(merged["ils_dispy_female"].std()),
        "min": float(merged["ils_dispy_female"].min()),
        "max": float(merged["ils_dispy_female"].max()),
        "n_missing": int(n_missing_female),
    }

    t_end = datetime.now(timezone.utc)
    wall_sec = (t_end - t_start).total_seconds()

    meta = {
        "schema_version": "nc_pilot_couples_post_em_merge_v1",
        "produced_by": "scripts/pilot/merge_pilot_em_outputs.py",
        "produced_at_utc": t_end.isoformat(),
        "wall_seconds": round(wall_sec, 1),
        "authorization": "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md",
        "merge_keys": {
            "household": "idhh == idhh_true (decoded, not encoded)",
            "male_income": "(idhh, draw_male, draw_female) via idperson_true in male_ids",
            "female_income": "(idhh, draw_male, draw_female) via idperson_true in female_ids",
            "note": "NEVER merged on encoded idperson/idhh (HM2 compliance)",
        },
        "partner_id_columns_confirmed": {
            "product_male_person_id": "idperson",
            "product_female_person_id": "idpartner",
            "em_male_decider_id": "idperson_true where dgn==1.0 and is_decider==1",
            "em_female_decider_id": "idperson_true where dgn==0.0 and is_decider==1",
            "mapping_validation": "HM4 PASS: 2577 male IDs and 2577 female IDs each match exactly; zero crossovers",
        },
        "decider_filter": {
            "total_rows_per_block": 254340,
            "decider_rows_per_block": 154620,
            "non_decider_rows_per_block": 99720,
            "decider_source": "is_decider==1 from adapter input block_f00 (set constant across all blocks)",
        },
        "draw_joint_reconstruction": {
            "formula": "30 * draw_male + draw_female",
            "draw_male_source": "scalar 'draw' column in EUROMOD output (= male marginal m)",
            "draw_female_source": "block constant f (from directory block_f{NN})",
            "consistency_check": f"HM7 PASS: all {EXPECTED_ROWS:,} rows consistent",
        },
        "block_outputs": [
            {
                "block_f": s["block_f"],
                "path": f"Data/pilot/nc_2016_couples/em_outputs/block_f{s['block_f']:02d}/combined_draws_em.parquet",
                "rows": block_row_check[s["block_f"]]["rows"],
                "ok": block_row_check[s["block_f"]]["ok"],
            }
            for s in block_stats
        ],
        "output": {
            "path": str(OUT_PARQUET.relative_to(REPO)),
            "row_count": int(len(merged_out)),
            "n_base_columns": 149,
            "n_income_columns_added": 2,
            "total_columns": int(len(merged_out.columns)),
            "chosen_rows": int(len(chosen_rows)),
            "chosen_condition": "draw_male==0 AND draw_female==0 AND draw_joint==0",
        },
        "income_columns": {
            "ils_dispy_male": {
                "description": "Male partner EUROMOD disposable income (joint household tax-benefit)",
                "primary": True,
                **male_income_stats,
            },
            "ils_dispy_female": {
                "description": "Female partner EUROMOD disposable income (joint household tax-benefit)",
                "primary": True,
                **female_income_stats,
            },
            "ils_dispy_hh_derived": {
                "added": False,
                "note": "Not created per amendment §11 (would be non-primary only if added)",
            },
        },
        "validations": {
            "HM1_inputs_unchanged": "PASS",
            "HM2_no_encoded_ids": "PASS",
            "HM3_idhh_true_matches_product": "PASS",
            "HM4_partner_mapping_one_to_one": "PASS",
            "HM5_no_duplicate_income_rows": "PASS",
            "HM6_one_income_per_product_row": "PASS",
            "HM7_draw_joint_consistency": "PASS",
            "HM8_row_count": f"PASS ({EXPECTED_ROWS:,})",
            "HM8_chosen_row_count": f"PASS ({EXPECTED_COUPLES:,})",
            "HM9_income_completeness": "PASS (0 missing on both income columns)",
        },
        "not_run": {
            "is_chosen_aliasing": False,
            "chosen_first_sorting": False,
            "GSUR": False,
            "precompute": False,
            "estimation": False,
            "welfare": False,
            "SA2": False,
            "promotion": False,
            "M1_clean_displacement": False,
        },
        "stage_status": {
            "M1_clean_2016": "active",
            "corrected_pooled_P3a": "unaffected",
            "singles_production": "unaffected",
        },
    }
    OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[merge] Wrote metadata: {OUT_META}")
    print(f"\n[merge] DONE. Wall time: {wall_sec:.1f}s")
    print(f"[merge] Output: {len(merged_out):,} rows x {len(merged_out.columns)} cols")
    print(f"[merge] All HM1-HM9 checks PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
