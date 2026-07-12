"""
P3-1 STAGING — copy/augment the P2a singles baseline into the storage layout the
welfare loaders (joint_recovery_test._load_parquet_slice / estimation_utils.
precompute_data_singles) expect.  NEW FILE; edits no existing script.

WHAT THIS BRIDGES (from RURO_welfare_layer_input_contract_and_reuse_audit_v1.md):
  1. Data must live under bpool_dir() as `{stem}__singles.parquet` + `{stem}__mnlmeta.json`
     (joint_recovery_test.py:203, 247-249).
  2. The loader sorts by `stacked_hh_uid` (joint_recovery_test.py:216) and the engine
     groups by `idhh` (estimation_utils.py:824); the P2a parquet has `idhh` but lacks
     `stacked_hh_uid` and `year_tag`.

CERTIFIED DERIVATION MIRRORED (harmonise_bpool_engine_ready.py):
  - `idhh = stacked_hh_uid` (harmonise_bpool_engine_ready.py:130) — an IDENTITY in the
    certified pipeline, so we invert it: `stacked_hh_uid = idhh`.  Exact for single-year
    data where stacked_hh_uid is unique per household.
  - `year_tag = data_year.map({2015:1, 2016:2, 2017:3})` (harmonise_bpool_engine_ready.py:20,131).
    P2a is a single 2016 wave (fr_p2a_singles2016__mnlmeta.json:31-34) so year_tag = 2 for
    every row; we also stamp data_year = 2016 for loader completeness.

COUPLES ABSENCE (documented choice — SINGLES-ONLY CODE PATH, not an empty couples frame):
  build_data_objects (joint_recovery_test.py:271) ALWAYS loads a couples slice via
  `_load_parquet_slice(cou_stem, "couples", …)`, which requires a `{stem}__couples.parquet`
  that does not exist for a singles-only baseline.  Rather than fabricate an empty couples
  frame (which would then hit the couples resolution guard, welfare_core.py:107-113,
  asserting couples_alts == 901), the P3-1 RUNNER bypasses build_data_objects and calls the
  singles primitives directly — `_load_parquet_slice(stem,"singles",…)` (joint_recovery_test.py:189)
  + `precompute_data_singles(…)` (joint_recovery_test.py:274) — mirroring build_data_objects
  lines 269-279 MINUS the two couples lines (271, 280).  This staging step therefore writes
  NO couples artifact by design.

THETA (authoritative source):
  The fitted P2a θ is `estimation_results_p2a_singles2016.json → results.joint.parameters`
  (the step4-schema block).  In the provenance CSV `theta_p2a_singles_2016_v1.csv` the columns
  are `param,certified,trial,moved`: `certified` = warm-start / initial values, `trial` = the
  fitted P2a value, `moved` = |trial-certified|.  We emit a canonical `parameter,value` CSV
  from the JSON parameters (so it loads via jrt.load_theta_star_from_csv, joint_recovery_test.py:72-91)
  and CROSS-CHECK it against the CSV `trial` column.

Outputs (idempotent, atomic):
  <storage>/new_data/fr_p2a_singles2016_welfare__singles.parquet
  <storage>/new_data/fr_p2a_singles2016_welfare__mnlmeta.json
  scripts/welfare/configs/theta_hat_p2a_singles2016_v1.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parent.parent.parent
for _p in ["scripts/bpool", "scripts/enhanced"]:
    sys.path.insert(0, str(_REPO / _p))
from _bpool_paths import bpool_dir  # noqa: E402

# --- inputs (P2a baseline) ---
_SRC_DIR = _REPO / "outputs" / "p2a_singles2016"
_SRC_PARQUET = _SRC_DIR / "fr_p2a_singles2016__singles.parquet"
_SRC_META = _SRC_DIR / "fr_p2a_singles2016__mnlmeta.json"
_SRC_RESULTS = _SRC_DIR / "estimation_results_p2a_singles2016.json"
_SRC_THETA_CSV = _REPO / "theta_p2a_singles_2016_v1.csv"   # provenance diff table

# --- staged outputs ---
STAGED_STEM = "fr_p2a_singles2016_welfare"
_DST_PARQUET = bpool_dir() / f"{STAGED_STEM}__singles.parquet"
_DST_META = bpool_dir() / f"{STAGED_STEM}__mnlmeta.json"
_DST_THETA = _REPO / "scripts" / "welfare" / "configs" / "theta_hat_p2a_singles2016_v1.csv"

_YEAR_TAG = {2015: 1, 2016: 2, 2017: 3}   # harmonise_bpool_engine_ready.py:20
P2A_YEAR = 2016


def _atomic_parquet(df: pd.DataFrame, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False)
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_text(text: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def stage_parquet() -> dict:
    df = pd.read_parquet(_SRC_PARQUET)
    n0 = len(df)
    info = {"src_rows": int(n0), "src_cols": int(df.shape[1])}

    # --- stacked_hh_uid = idhh  (invert harmonise_bpool_engine_ready.py:130) ---
    if "idhh" not in df.columns:
        raise SystemExit("STOP: P2a parquet lacks idhh; cannot derive stacked_hh_uid.")
    if "stacked_hh_uid" in df.columns:
        # already present (unexpected for P2a) — verify identity, do not clobber silently
        if not (df["stacked_hh_uid"].astype("int64") == df["idhh"].astype("int64")).all():
            raise SystemExit("STOP: existing stacked_hh_uid != idhh; certified identity broken.")
    else:
        df["stacked_hh_uid"] = df["idhh"].astype("int64")

    # --- year_tag from data_year (harmonise_bpool_engine_ready.py:20,131) ---
    if "data_year" not in df.columns:
        df["data_year"] = np.int64(P2A_YEAR)
    df["year_tag"] = df["data_year"].map(_YEAR_TAG).astype("int64")
    bad = df["year_tag"].isna().sum()
    if bad:
        raise SystemExit(f"STOP: {bad} rows with data_year outside {list(_YEAR_TAG)}.")

    info["n_unique_stacked_hh_uid"] = int(df["stacked_hh_uid"].nunique())
    info["year_tag_values"] = sorted(int(v) for v in df["year_tag"].unique())
    info["alts_per_hh"] = int(df.groupby("stacked_hh_uid").size().mode().iloc[0])

    # loader sorts by [stacked_hh_uid, draw] (joint_recovery_test.py:216); pre-sort so the
    # staged file is already group-contiguous (estimation_utils.py:819 requirement).
    df = df.sort_values(["stacked_hh_uid", "draw"]).reset_index(drop=True)
    _atomic_parquet(df, _DST_PARQUET)
    info["dst_parquet"] = str(_DST_PARQUET)
    info["dst_rows"] = int(len(df))

    # mnlmeta copied verbatim (normalization block carries c_scale/l_scale used downstream)
    meta = json.loads(_SRC_META.read_text())
    _atomic_text(json.dumps(meta, indent=2), _DST_META)
    info["dst_meta"] = str(_DST_META)
    info["c_scale"] = float(meta["normalization"]["singles"]["c_scale"])
    info["l_scale"] = float(meta["normalization"]["singles"]["l_scale"])
    info["n_draws_singles"] = int(meta["n_draws"]["singles"])
    return info


def stage_theta() -> dict:
    """Emit a canonical `parameter,value` θ CSV from the results JSON and cross-check the
    provenance CSV `trial` column."""
    res = json.loads(_SRC_RESULTS.read_text())
    params = res["results"]["joint"]["parameters"]
    out = pd.DataFrame({"parameter": list(params.keys()),
                        "value": [float(v) for v in params.values()]})
    _atomic_text(out.to_csv(index=False), _DST_THETA)

    info = {"dst_theta": str(_DST_THETA), "n_params": int(len(out))}
    # cross-check against theta_p2a_singles_2016_v1.csv `trial` column
    prov = pd.read_csv(_SRC_THETA_CSV)
    prov_map = dict(zip(prov["param"].astype(str), prov["trial"].astype(float)))
    max_abs = 0.0
    n_checked = 0
    for k, v in params.items():
        if k in prov_map:
            max_abs = max(max_abs, abs(float(v) - prov_map[k]))
            n_checked += 1
    info["xcheck_vs_trial_col_max_abs"] = float(max_abs)
    info["xcheck_n_matched"] = int(n_checked)
    info["xcheck_pass"] = bool(max_abs < 1e-9)
    return info


def main():
    print("P3-1 staging start")
    pinfo = stage_parquet()
    print(f"  parquet: {pinfo['dst_rows']} rows, {pinfo['n_unique_stacked_hh_uid']} HH, "
          f"alts/HH={pinfo['alts_per_hh']}, year_tag={pinfo['year_tag_values']}, "
          f"c_scale={pinfo['c_scale']:.3f}, l_scale={pinfo['l_scale']:.3f}")
    tinfo = stage_theta()
    print(f"  theta: {tinfo['n_params']} params -> {Path(tinfo['dst_theta']).name}; "
          f"xcheck vs trial col: max_abs={tinfo['xcheck_vs_trial_col_max_abs']:.2e} "
          f"(matched {tinfo['xcheck_n_matched']}, pass={tinfo['xcheck_pass']})")
    if not tinfo["xcheck_pass"]:
        raise SystemExit("STOP: JSON parameters disagree with provenance CSV `trial` column.")
    print("P3-1 staging done")
    return {"parquet": pinfo, "theta": tinfo}


if __name__ == "__main__":
    main()
