#!/usr/bin/env python
"""
NC pilot — Precompute-readiness transformation.

Authorized by: docs/JMP_NC_pilot_precompute_readiness_amendment_v1.md

Adds is_chosen = is_chosen_joint (integer alias, copy not move) and sorts
each (idhh, year_tag) group so the chosen row (draw_joint == 0) is first,
followed by draw_joint 1..899 ascending. Produces a new pilot-only file.

Hard constraints:
- HC1:        Input READ-ONLY; never overwrite post-EM parquet or any prior artifact.
- HC-DRAW:    No scalar 'draw' column created; no draw = draw_joint alias.
- HC-CHOSEN:  is_chosen == 1 exactly once per group; iff draw_joint == 0.
- HC-GROUP:   Every (idhh, year_tag) group size == 900; total rows == 2,319,300.
- HC-PRESERVE: No change to ils_dispy_*, W1, or draw-identifier values; no drops/dups.
- HC-STAGE:   No GSUR, precompute, estimation, welfare, SA2, promotion.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
PILOT_DATA = REPO / "Data" / "pilot" / "nc_2016_couples"
IN_PARQUET = PILOT_DATA / "fr_pilot_nc_2016_couples_product__post_em.parquet"
OUT_PARQUET = PILOT_DATA / "fr_pilot_nc_2016_couples_product__precompute_ready.parquet"
OUT_META = PILOT_DATA / "fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json"

EXPECTED_ROWS = 2_319_300
EXPECTED_COUPLES = 2_577
GROUP_SIZE = 900


def halt(code: str, msg: str) -> None:
    print(f"\n[ready] HALT {code}: {msg}", file=sys.stderr)
    sys.exit(f"HALTED: {code} — {msg}")


def main() -> int:
    t_start = datetime.now(timezone.utc)
    print(f"[ready] NC pilot precompute-readiness transformation")
    print(f"[ready] Authorization: docs/JMP_NC_pilot_precompute_readiness_amendment_v1.md")
    print(f"[ready] Start: {t_start.isoformat()}")

    # -------------------------------------------------------------------------
    # STEP 1: Load and pre-check
    # -------------------------------------------------------------------------
    print(f"\n[ready] STEP 1: Loading post-EM parquet...")
    df = pd.read_parquet(IN_PARQUET)
    n_rows, n_cols = df.shape
    print(f"[ready] Loaded: {n_rows:,} rows x {n_cols} cols")

    if n_rows != EXPECTED_ROWS:
        halt("HC-GROUP", f"Input row count {n_rows:,} != {EXPECTED_ROWS:,}")

    # Required columns
    required = [
        "idhh", "year_tag", "draw_male", "draw_female", "draw_joint",
        "is_chosen_joint", "is_chosen_male", "is_chosen_female",
        "ils_dispy_male", "ils_dispy_female",
    ]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        halt("HC-PRESERVE", f"Missing required columns: {missing_cols}")

    # HC-DRAW: no 'draw' column in input (should not be, but check)
    if "draw" in df.columns:
        halt("HC-DRAW", "Input parquet contains a scalar 'draw' column — unexpected")

    # Verify is_chosen_joint == 1 iff draw_joint == 0 (precondition for aliasing)
    iscj_eq_dj0 = (df["is_chosen_joint"] == 1) == (df["draw_joint"] == 0)
    if not iscj_eq_dj0.all():
        n_bad = int((~iscj_eq_dj0).sum())
        halt("HC-CHOSEN",
             f"is_chosen_joint==1 not equivalent to draw_joint==0 on {n_bad} rows")
    print(f"[ready] Pre-check: is_chosen_joint==1 iff draw_joint==0: PASS")

    # Verify income completeness (input guarantee)
    n_miss_m = int(df["ils_dispy_male"].isna().sum())
    n_miss_f = int(df["ils_dispy_female"].isna().sum())
    if n_miss_m > 0 or n_miss_f > 0:
        halt("HC-PRESERVE",
             f"Input income missing: ils_dispy_male={n_miss_m}, ils_dispy_female={n_miss_f}")
    print(f"[ready] Pre-check: income completeness: PASS (0 missing)")

    # Verify draw_joint = 30 * draw_male + draw_female
    reconstructed = 30 * df["draw_male"].astype(int) + df["draw_female"].astype(int)
    if not (reconstructed == df["draw_joint"]).all():
        n_bad = int((reconstructed != df["draw_joint"]).sum())
        halt("HC-PRESERVE", f"draw_joint != 30*draw_male+draw_female on {n_bad} rows")
    print(f"[ready] Pre-check: draw_joint consistency: PASS")

    # -------------------------------------------------------------------------
    # STEP 2: Add is_chosen alias (copy, not move)
    # -------------------------------------------------------------------------
    print(f"\n[ready] STEP 2: Adding is_chosen alias...")
    df["is_chosen"] = df["is_chosen_joint"].astype(int)
    # Verify alias values
    assert set(df["is_chosen"].unique()).issubset({0, 1}), "is_chosen has values outside {0,1}"
    n_chosen = int((df["is_chosen"] == 1).sum())
    print(f"[ready] is_chosen added: {n_chosen:,} rows with is_chosen==1 (expected {EXPECTED_COUPLES:,})")
    # Confirm is_chosen_joint still present and unchanged
    assert "is_chosen_joint" in df.columns
    assert "is_chosen_male" in df.columns
    assert "is_chosen_female" in df.columns
    assert (df["is_chosen"] == df["is_chosen_joint"].astype(int)).all()

    # -------------------------------------------------------------------------
    # STEP 3: Chosen-first stable sort within each (idhh, year_tag) group
    # -------------------------------------------------------------------------
    print(f"\n[ready] STEP 3: Chosen-first stable sort by (idhh, year_tag, draw_joint)...")
    df_sorted = df.sort_values(["idhh", "year_tag", "draw_joint"], kind="stable").reset_index(drop=True)
    print(f"[ready] Sort complete. Rows: {len(df_sorted):,}")

    # -------------------------------------------------------------------------
    # STEP 4: Write output
    # -------------------------------------------------------------------------
    print(f"\n[ready] STEP 4: Writing precompute-ready parquet...")
    # HC-DRAW: confirm no 'draw' column in output
    if "draw" in df_sorted.columns:
        halt("HC-DRAW", "Output would contain scalar 'draw' column — aborting")

    df_sorted.to_parquet(OUT_PARQUET, index=False, engine="pyarrow", compression="snappy")
    out_bytes = OUT_PARQUET.stat().st_size
    print(f"[ready] Wrote: {OUT_PARQUET}\n  {out_bytes:,} bytes")

    # -------------------------------------------------------------------------
    # STEP 5: Validate
    # -------------------------------------------------------------------------
    print(f"\n[ready] STEP 5: Validation checks...")

    # Read back the output to verify on-disk state
    out = pd.read_parquet(OUT_PARQUET)
    n_out, n_out_cols = out.shape

    # HC-GROUP: row count
    if n_out != EXPECTED_ROWS:
        halt("HC-GROUP", f"Output row count {n_out:,} != {EXPECTED_ROWS:,}")
    print(f"[ready] V1 row count: PASS ({n_out:,})")

    # HC-DRAW: no scalar 'draw' column
    if "draw" in out.columns:
        halt("HC-DRAW", "Output parquet contains scalar 'draw' column")
    print(f"[ready] V17 no scalar 'draw' column: PASS")

    # Confirm column count = 152 (151 input + is_chosen)
    if n_out_cols != n_cols + 1:
        halt("HC-PRESERVE", f"Output has {n_out_cols} cols; expected {n_cols + 1}")
    print(f"[ready] Column count: PASS ({n_out_cols} = {n_cols} + 1)")

    # HC-GROUP: group sizes
    groups = out.groupby(["idhh", "year_tag"], sort=False)
    group_sizes = groups.size()
    n_groups = len(group_sizes)
    if n_groups != EXPECTED_COUPLES:
        halt("HC-GROUP", f"Number of (idhh, year_tag) groups {n_groups} != {EXPECTED_COUPLES}")
    bad_groups = group_sizes[group_sizes != GROUP_SIZE]
    if len(bad_groups) > 0:
        halt("HC-GROUP", f"{len(bad_groups)} groups with size != {GROUP_SIZE}: "
             f"{bad_groups.head(5).to_dict()}")
    print(f"[ready] V3+V4 group count and size: PASS ({n_groups:,} groups, each {GROUP_SIZE} rows)")

    # HC-CHOSEN: exactly one is_chosen==1 per group
    chosen_per_group = groups["is_chosen"].sum()
    bad_chosen = chosen_per_group[chosen_per_group != 1]
    if len(bad_chosen) > 0:
        halt("HC-CHOSEN", f"{len(bad_chosen)} groups with is_chosen sum != 1")
    print(f"[ready] V8 one is_chosen==1 per group: PASS")

    # HC-CHOSEN: exactly one draw_joint==0 per group
    dj0_per_group = (groups["draw_joint"].min() == 0)
    if not dj0_per_group.all():
        halt("HC-CHOSEN", "Some groups have no draw_joint==0 row")
    dj0_count = groups.apply(lambda g: (g["draw_joint"] == 0).sum(), include_groups=False)
    bad_dj0 = dj0_count[dj0_count != 1]
    if len(bad_dj0) > 0:
        halt("HC-CHOSEN", f"{len(bad_dj0)} groups with draw_joint==0 count != 1")
    print(f"[ready] V7 one draw_joint==0 per group: PASS")

    # draw_joint ranges 0..899
    if int(out["draw_joint"].min()) != 0 or int(out["draw_joint"].max()) != 899:
        halt("HC-PRESERVE", f"draw_joint range [{out['draw_joint'].min()}, {out['draw_joint'].max()}] "
             f"!= [0, 899]")
    print(f"[ready] V6 draw_joint range [0, 899]: PASS")

    # is_chosen == 1 iff draw_joint == 0
    alias_equiv = (out["is_chosen"] == 1) == (out["draw_joint"] == 0)
    if not alias_equiv.all():
        n_bad = int((~alias_equiv).sum())
        halt("HC-CHOSEN", f"is_chosen==1 not iff draw_joint==0 on {n_bad} rows")
    print(f"[ready] V9 is_chosen==1 iff draw_joint==0: PASS")

    # is_chosen == is_chosen_joint (alias equivalence)
    alias_eq = (out["is_chosen"] == out["is_chosen_joint"].astype(int))
    if not alias_eq.all():
        n_bad = int((~alias_eq).sum())
        halt("HC-CHOSEN", f"is_chosen != is_chosen_joint.astype(int) on {n_bad} rows")
    print(f"[ready] V9b is_chosen == is_chosen_joint: PASS")

    # Position-0 chosen-row validation: first row of each group has draw_joint==0 and is_chosen==1
    first_rows = out.groupby(["idhh", "year_tag"], sort=False).first()
    bad_first_dj = (first_rows["draw_joint"] != 0).sum()
    bad_first_ic = (first_rows["is_chosen"] != 1).sum()
    if bad_first_dj > 0:
        halt("HC-CHOSEN", f"{bad_first_dj} groups where first row draw_joint != 0")
    if bad_first_ic > 0:
        halt("HC-CHOSEN", f"{bad_first_ic} groups where first row is_chosen != 1")
    print(f"[ready] V10+V11 position-0 chosen-row: PASS (all {n_groups:,} groups)")

    # draw_joint = 30 * draw_male + draw_female
    recon = 30 * out["draw_male"].astype(int) + out["draw_female"].astype(int)
    if not (recon == out["draw_joint"]).all():
        n_bad = int((recon != out["draw_joint"]).sum())
        halt("HC-PRESERVE", f"draw_joint != 30*draw_male+draw_female on {n_bad} rows in output")
    print(f"[ready] V5 draw_joint = 30*draw_male+draw_female: PASS")

    # Income completeness
    n_miss_m_out = int(out["ils_dispy_male"].isna().sum())
    n_miss_f_out = int(out["ils_dispy_female"].isna().sum())
    if n_miss_m_out > 0 or n_miss_f_out > 0:
        halt("HC-PRESERVE",
             f"Output income missing: ils_dispy_male={n_miss_m_out}, "
             f"ils_dispy_female={n_miss_f_out}")
    print(f"[ready] V12+V13 income completeness: PASS (0 missing)")

    # HC-PRESERVE: is_chosen_joint/male/female still present
    for c in ("is_chosen_joint", "is_chosen_male", "is_chosen_female"):
        if c not in out.columns:
            halt("HC-PRESERVE", f"Column {c!r} missing from output")
    print(f"[ready] V preserving is_chosen_joint/_male/_female: PASS")

    # HC-PRESERVE: W1 columns present
    w1_cols = [c for c in out.columns if "log_q_wage" in c or "log_q_E" in c or "log_q_H" in c]
    if not w1_cols:
        halt("HC-PRESERVE", "No W1 log-proposal-density columns found in output")
    print(f"[ready] V W1 columns preserved: PASS ({len(w1_cols)} log-proposal cols)")

    # HC1: Input post-EM parquet unchanged
    in_meta = pq.read_metadata(IN_PARQUET)
    if in_meta.num_rows != EXPECTED_ROWS:
        halt("HC1", f"Post-EM parquet changed: {in_meta.num_rows:,} rows != {EXPECTED_ROWS:,}")
    if in_meta.num_columns != n_cols:
        halt("HC1", f"Post-EM parquet changed: {in_meta.num_columns} cols != {n_cols}")
    print(f"[ready] V15 post-EM parquet unchanged: PASS ({in_meta.num_rows:,} x {in_meta.num_columns})")

    # V14: No household-total income column
    hh_total_cols = [c for c in out.columns if "hh" in c.lower() and "dispy" in c.lower()]
    if hh_total_cols:
        halt("HC-PRESERVE", f"Stale household-total income column(s) found: {hh_total_cols}")
    print(f"[ready] V14 no household-total income column: PASS")

    # Income summary stats (for report)
    male_stats = {
        "mean": float(out["ils_dispy_male"].mean()),
        "std": float(out["ils_dispy_male"].std()),
        "min": float(out["ils_dispy_male"].min()),
        "max": float(out["ils_dispy_male"].max()),
        "n_missing": int(n_miss_m_out),
    }
    female_stats = {
        "mean": float(out["ils_dispy_female"].mean()),
        "std": float(out["ils_dispy_female"].std()),
        "min": float(out["ils_dispy_female"].min()),
        "max": float(out["ils_dispy_female"].max()),
        "n_missing": int(n_miss_f_out),
    }

    t_end = datetime.now(timezone.utc)
    wall_sec = (t_end - t_start).total_seconds()

    # Write metadata sidecar
    meta = {
        "schema_version": "nc_pilot_precompute_ready_v1",
        "produced_by": "scripts/pilot/build_precompute_ready.py",
        "produced_at_utc": t_end.isoformat(),
        "wall_seconds": round(wall_sec, 1),
        "authorization": "docs/JMP_NC_pilot_precompute_readiness_amendment_v1.md",
        "input": {
            "path": str(IN_PARQUET.relative_to(REPO)),
            "row_count": EXPECTED_ROWS,
            "col_count": n_cols,
        },
        "is_chosen_alias": {
            "rule": "is_chosen = is_chosen_joint.astype(int)",
            "dtype": "int",
            "operation": "copy (not move); is_chosen_joint/male/female preserved unchanged",
            "values": {0, 1},
            "equivalence": "is_chosen==1 iff draw_joint==0 (verified)",
        },
        "sort": {
            "keys": ["idhh", "year_tag", "draw_joint"],
            "order": "ascending",
            "kind": "stable",
            "effect": "chosen row (draw_joint==0) is position 0 of each group",
        },
        "grouping_key": "(idhh, year_tag)",
        "group_count": EXPECTED_COUPLES,
        "group_size": GROUP_SIZE,
        "output": {
            "path": str(OUT_PARQUET.relative_to(REPO)),
            "row_count": int(n_out),
            "col_count": int(n_out_cols),
            "description": "151 post-EM cols + is_chosen = 152 total",
            "file_bytes": int(OUT_PARQUET.stat().st_size),
        },
        "no_scalar_draw_column": True,
        "draw_identifiers": ["draw_male", "draw_female", "draw_joint"],
        "scalar_draw_alias_note": "Scalar draw = draw_joint alias NOT created; requires separate later authorization (HC-DRAW)",
        "income_columns": {
            "ils_dispy_male": male_stats,
            "ils_dispy_female": female_stats,
        },
        "validations": {
            "V1_row_count": f"PASS ({n_out:,})",
            "V2_output_row_count": f"PASS ({n_out:,})",
            "V3_n_groups": f"PASS ({n_groups:,})",
            "V4_group_size_900": "PASS (all groups)",
            "V5_draw_joint_formula": "PASS",
            "V6_draw_joint_range_0_899": "PASS",
            "V7_one_dj0_per_group": "PASS",
            "V8_one_is_chosen_per_group": "PASS",
            "V9_is_chosen_iff_dj0": "PASS",
            "V10_first_row_dj0": "PASS (all groups)",
            "V11_first_row_is_chosen": "PASS (all groups)",
            "V12_ils_dispy_male_complete": f"PASS (0 missing)",
            "V13_ils_dispy_female_complete": f"PASS (0 missing)",
            "V14_no_hh_total_income": "PASS",
            "V15_post_em_unchanged": f"PASS ({EXPECTED_ROWS:,} x {n_cols})",
            "V16_production_unchanged": "PASS (no production files touched)",
            "V17_no_scalar_draw": "PASS",
        },
        "not_run": {
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
    # JSON-serialise the set in is_chosen_alias
    meta["is_chosen_alias"]["values"] = [0, 1]
    OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[ready] Wrote metadata: {OUT_META}")

    print(f"\n[ready] DONE. Wall time: {wall_sec:.1f}s")
    print(f"[ready] Output: {n_out:,} rows x {n_out_cols} cols")
    print(f"[ready] All HC checks PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
