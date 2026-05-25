"""
Stage A GSUR lookup builder for RURO MNL France — parameterised by opportunity year.

Authorization: docs/RURO_GSUR_StageA_authorization_v1.md (2026-05-17)
               docs/archive/2026-05-26_round2_chain_compression/audit_reaudit_chain/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md
Specification: docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md
Decisions:     docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md

Inputs (year-parameterised):
  Data/external/FR_gsur.xlsx                       -- unemployment rates (lfst_r_lfu3rt; multi-year)
  Data/external/fr_drgn1_to_nuts2_crosswalk.csv
  Data/external/lfst_r_lfsd2pop_FR_{YEAR}.tsv      -- D2 population denominators (operational)
  Data/external/lfst_r_lfp2acedu_FR_{YEAR}.tsv     -- D1 labour-force denominators (diagnostic only)
  Data/external/insee_001688526_{YEAR}.csv          -- national benchmark (annual average read at runtime)

Outputs (year-tagged):
  Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}.parquet
  Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json

This script builds the Stage A lookup only (broad-age Y20-64 gsur per
drgn1 x educ3 x sex). It does NOT write MNL parquets, does NOT estimate,
does NOT touch canonical paths.

Restrictions enforced:
  - No write to fr_2016_RURO_mnl_GSURv2__*.parquet
  - No write to canonical fr_2016_RURO_mnl__*.parquet
  - O7 sign-off (required before MNL merge) is NOT performed here

Usage:
  python scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016
  python scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2015
  python scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2014
"""

import pathlib
import re
import sys
import warnings
import argparse
import datetime
import json
import subprocess
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

REPO = pathlib.Path(__file__).resolve().parents[2]
EXT  = REPO / "Data" / "external"
OUT     = None   # set in main() from --opportunity-year (C6)
SIDECAR = None   # set in main() from --opportunity-year (C6)

YEAR = 2016
BENCHMARK_PCT  = 9.725         # overridden in main() via C5 CSV read
BENCHMARK_PROP = BENCHMARK_PCT / 100.0
BENCHMARK_TOL  = 0.010         # +/- 1 ppt tolerance for L5 (O9)
IDF_TOL        = 0.001         # Ile-de-France parity tolerance (O8)

METRO_NUTS2 = [                # 22 metropolitan France NUTS-2 (post-2016 codes)
    "FR10","FRB0","FRC1","FRC2","FRD1","FRD2","FRE1","FRE2",
    "FRF1","FRF2","FRF3","FRG0","FRH0","FRI1","FRI2","FRI3",
    "FRJ1","FRJ2","FRK1","FRK2","FRL0","FRM0",
]

ISCED_TO_EDUC3 = {"ED0-2": 0, "ED3_4": 1, "ED5-8": 2}
EDUC3_TO_ISCED = {0: "ED0-2", 1: "ED3_4", 2: "ED5-8"}

SEX_MF = ["M", "F"]

# O2: D3 cells that have missing OBS_VALUE in lfst_r_lfsd2pop
# These require approximate_uniform weight = 1/N, N=3 NUTS-2 components of drgn1=8
D3_CELLS = {
    ("FRM0", "F", "Y25-34", "ED0-2"),
    ("FRM0", "F", "Y15-24", "ED5-8"),
}
D3_N_COMPONENTS = 3   # drgn1=8 spans FRJ1, FRL0, FRM0

# Suppression flag regions per O2 resolution memo (flagged-u in lfst_r_lfsd2pop Y20-64)
FRM0_Y2064_FLAGGED_U = {"FRM0"}   # all sex x educ3 cells flagged u at Y20-64

# FRI2 all narrow-band cells flagged-u (but valued) -- note in validation report
FRI2_FLAGGED_BANDS = {"Y15-24","Y25-34","Y35-44","Y45-54","Y55-64"}


# ---------------------------------------------------------------------------
# 1. Load crosswalk
# ---------------------------------------------------------------------------

def load_crosswalk() -> pd.DataFrame:
    cw = pd.read_csv(EXT / "fr_drgn1_to_nuts2_crosswalk.csv", dtype=str)
    cw["drgn1"] = cw["drgn1"].astype(int)
    assert (cw["verified_against_eurostat"] == "YES").all(), \
        "Crosswalk contains unverified rows"
    assert set(cw["new_nuts2_code_2016"].unique()) <= set(METRO_NUTS2), \
        "Unexpected NUTS2 codes in crosswalk"
    return cw


# ---------------------------------------------------------------------------
# 2. Parse FR_gsur.xlsx
# ---------------------------------------------------------------------------

def _parse_sheet_meta(df_raw: pd.DataFrame) -> dict:
    """Extract isced11, sex, age from rows 4-7 of a workbook sheet."""
    def extract_code(cell_val):
        if pd.isna(cell_val):
            return None
        m = re.search(r"\[(\S+)\]", str(cell_val))
        return m.group(1) if m else str(cell_val).strip()

    return {
        "isced11": extract_code(df_raw.iloc[5, 2]),
        "sex":     extract_code(df_raw.iloc[6, 2]),
        "age":     extract_code(df_raw.iloc[7, 2]),
    }


def _find_year_col(df_raw: pd.DataFrame, year: int) -> int:
    """Return column index for the target year in row 10."""
    row10 = df_raw.iloc[10, :]
    for c, v in row10.items():
        try:
            if int(float(str(v).strip())) == year:
                return c
        except (ValueError, TypeError):
            continue
    raise KeyError(f"Year {year} not found in row 10 of sheet")


def _extract_geo_values(df_raw: pd.DataFrame, col_val: int) -> dict:
    """Return {geo_code: (rate_pct, flag)} from data rows (row 12+)."""
    result = {}
    for i in range(12, len(df_raw)):
        geo = df_raw.iloc[i, 0]
        if pd.isna(geo) or not isinstance(geo, str):
            continue
        geo = geo.strip()
        val = df_raw.iloc[i, col_val]
        flag = df_raw.iloc[i, col_val + 1] if col_val + 1 < len(df_raw.columns) else None
        try:
            rate = float(val) if pd.notna(val) else np.nan
        except (ValueError, TypeError):
            rate = np.nan
        flag_str = str(flag).strip() if pd.notna(flag) else ""
        result[geo] = (rate, flag_str)
    return result


def load_gsur_workbook() -> pd.DataFrame:
    """
    Parse FR_gsur.xlsx and return a tidy DataFrame:
      columns: geo, isced11, sex, age, ur_pct, ur_flag
    Only sheets for (isced in [ED0-2,ED3_4,ED5-8], sex in [M,F]) are loaded.
    Also loads TOTAL sex for diagnostic purposes.
    """
    xl = pd.ExcelFile(EXT / "FR_gsur.xlsx")
    records = []
    wanted_isced = {"ED0-2", "ED3_4", "ED5-8", "TOTAL"}
    wanted_sex   = {"M", "F", "T"}
    wanted_age   = {"Y20-64", "Y15-74"}   # Y20-64 operational; Y15-74 diagnostic

    for sh in xl.sheet_names:
        if not sh.startswith("Sheet "):
            continue
        df_raw = pd.read_excel(xl, sheet_name=sh, header=None)
        meta = _parse_sheet_meta(df_raw)
        if meta["isced11"] not in wanted_isced:
            continue
        if meta["sex"] not in wanted_sex:
            continue
        if meta["age"] not in wanted_age:
            continue
        try:
            col_val = _find_year_col(df_raw, YEAR)
        except KeyError:
            print(f"  WARNING: year {YEAR} not found in {sh}, skipping")
            continue
        geo_vals = _extract_geo_values(df_raw, col_val)
        for geo, (rate, flag) in geo_vals.items():
            records.append({
                "geo":     geo,
                "isced11": meta["isced11"],
                "sex":     meta["sex"],
                "age":     meta["age"],
                "ur_pct":  rate,
                "ur_flag": flag,
            })

    df = pd.DataFrame(records)
    # Keep only metropolitan NUTS-2 codes (and FR for national diagnostic)
    df = df[df["geo"].isin(METRO_NUTS2 + ["FR"])]
    df = df.reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# 3. Load D2 denominators (operational)
# ---------------------------------------------------------------------------

def load_d2() -> pd.DataFrame:
    d2 = pd.read_csv(EXT / f"lfst_r_lfsd2pop_FR_{YEAR}.tsv", sep="\t", dtype=str)
    d2["OBS_VALUE"] = pd.to_numeric(d2["OBS_VALUE"], errors="coerce")
    d2["OBS_FLAG"]  = d2["OBS_FLAG"].fillna("").str.strip()
    # Restrict to metro NUTS-2, educ3 ISCED codes, M/F sex
    d2 = d2[
        d2["geo"].isin(METRO_NUTS2) &
        d2["isced11"].isin(["ED0-2", "ED3_4", "ED5-8"]) &
        d2["sex"].isin(["M", "F"])
    ].copy()
    return d2


# ---------------------------------------------------------------------------
# 4. Load D1 denominators (diagnostic only at Y15-74)
# ---------------------------------------------------------------------------

def load_d1() -> pd.DataFrame:
    d1 = pd.read_csv(EXT / f"lfst_r_lfp2acedu_FR_{YEAR}.tsv", sep="\t", dtype=str)
    d1["OBS_VALUE"] = pd.to_numeric(d1["OBS_VALUE"], errors="coerce")
    d1["OBS_FLAG"]  = d1["OBS_FLAG"].fillna("").str.strip()
    d1 = d1[
        d1["geo"].isin(METRO_NUTS2) &
        d1["isced11"].isin(["ED0-2", "ED3_4", "ED5-8"]) &
        d1["sex"].isin(["M", "F"]) &
        (d1["age"] == "Y15-74")
    ].copy()
    return d1


# ---------------------------------------------------------------------------
# 5. Aggregate NUTS-2 rates to drgn1 (population-weighted)
# ---------------------------------------------------------------------------

def aggregate_drgn1(
    gsur_df: pd.DataFrame,
    d2: pd.DataFrame,
    cw: pd.DataFrame,
    age_band: str,
) -> pd.DataFrame:
    """
    For each (drgn1, educ3, sex) compute the D2-population-weighted
    unemployment rate from the contributing NUTS-2 cells.

    Returns DataFrame with columns:
      drgn1, educ3, sex, gsur, weighting_source,
      gsur_age_band_used, denom_flag, n_components
    """
    # Filter GSUR to the target age band and MF sex
    ur = gsur_df[
        (gsur_df["age"]  == age_band) &
        (gsur_df["sex"].isin(["M", "F"]))
    ][["geo", "isced11", "sex", "ur_pct", "ur_flag"]].copy()
    ur["ur_prop"] = ur["ur_pct"] / 100.0

    # D2 denominators for this age band
    d2_age = d2[d2["age"] == age_band][
        ["geo", "isced11", "sex", "OBS_VALUE", "OBS_FLAG"]
    ].copy().rename(columns={"OBS_VALUE": "pop", "OBS_FLAG": "pop_flag"})

    records = []
    for drgn1_val, grp in cw.groupby("drgn1"):
        nuts2_list = list(grp["new_nuts2_code_2016"])
        for isced_code, educ3_val in ISCED_TO_EDUC3.items():
            for sex_val in SEX_MF:
                row = _build_cell(
                    drgn1_val, educ3_val, isced_code, sex_val,
                    nuts2_list, ur, d2_age, age_band,
                )
                records.append(row)

    df = pd.DataFrame(records)
    return df


def _build_cell(
    drgn1_val, educ3_val, isced_code, sex_val,
    nuts2_list, ur, d2_age, age_band
) -> dict:
    """Compute one (drgn1, educ3, sex) cell with D2 population weighting."""
    rates  = []
    pops   = []
    flags  = []
    ws_list = []

    for nuts2 in nuts2_list:
        # Unemployment rate from FR_gsur.xlsx
        ur_row = ur[
            (ur["geo"] == nuts2) &
            (ur["isced11"] == isced_code) &
            (ur["sex"] == sex_val)
        ]
        if len(ur_row) == 0:
            # Source workbook missing this cell — skip
            continue
        ur_val  = ur_row.iloc[0]["ur_prop"]
        ur_flag = ur_row.iloc[0]["ur_flag"]
        if np.isnan(ur_val):
            continue

        # D2 population weight
        pop_row = d2_age[
            (d2_age["geo"]     == nuts2) &
            (d2_age["isced11"] == isced_code) &
            (d2_age["sex"]     == sex_val)
        ]

        # Check for D3 cell (missing OBS_VALUE)
        d3_key = (nuts2, sex_val, age_band, isced_code)
        if d3_key in D3_CELLS:
            # O2 D3: approximate_uniform weight = 1/N
            pop_weight = 1.0 / D3_N_COMPONENTS
            rates.append(ur_val)
            pops.append(pop_weight)
            flags.append("D3_approximate_uniform")
            ws_list.append("approximate_uniform")
        elif len(pop_row) == 0 or np.isnan(pop_row.iloc[0]["pop"]):
            # Missing D2 — should not happen for Y20-64 except D3 cells
            rates.append(ur_val)
            pops.append(np.nan)
            flags.append("D2_missing")
            ws_list.append("population")
        else:
            pop_val  = pop_row.iloc[0]["pop"]
            pop_flag = pop_row.iloc[0]["pop_flag"]
            flag_str = "u" if "u" in pop_flag else ""
            # Combine UR source flag and pop flag
            combined_flag = "_".join(f for f in [ur_flag, flag_str] if f)
            rates.append(ur_val)
            pops.append(pop_val)
            flags.append(combined_flag)
            ws_list.append("population")

    if not rates:
        return {
            "drgn1": drgn1_val, "educ3": educ3_val, "sex": sex_val,
            "gsur": np.nan, "weighting_source": "population",
            "gsur_age_band_used": age_band, "denom_flag": "no_data",
            "n_components": 0, "gsur_unreliable": True,
        }

    rates = np.array(rates)
    pops  = np.array(pops, dtype=float)

    # If any pop is NaN (rare), fall back to equal weight
    if np.any(np.isnan(pops)):
        pops_valid = np.where(np.isnan(pops), 0.0, pops)
        if pops_valid.sum() == 0:
            pops_valid = np.ones(len(rates))
    else:
        pops_valid = pops

    total_pop = pops_valid.sum()
    if total_pop == 0:
        gsur_val = float(np.mean(rates))
    else:
        gsur_val = float(np.dot(rates, pops_valid) / total_pop)

    any_d3        = any("D3" in f for f in flags)
    any_unreliable = any("u" in f for f in flags if f)
    combined_denom_flag = "; ".join(sorted(set(f for f in flags if f)))

    weighting_source = "approximate_uniform" if any_d3 else "population"

    return {
        "drgn1":             drgn1_val,
        "educ3":             educ3_val,
        "sex":               sex_val,
        "gsur":              round(gsur_val, 6),
        "weighting_source":  weighting_source,
        "gsur_age_band_used": age_band,
        "denom_flag":        combined_denom_flag,
        "n_components":      len(rates),
        "gsur_unreliable":   any_unreliable,
    }


# ---------------------------------------------------------------------------
# 6. Add drgn1=9 stub (O5) and rename gsur_legacy_misaligned
# ---------------------------------------------------------------------------

def add_drgn9_stub(df: pd.DataFrame) -> pd.DataFrame:
    """O5: drgn1=9 in schema, all GSUR columns NaN for FR 2016 metropolitan."""
    rows = []
    for educ3 in [0, 1, 2]:
        for sex in SEX_MF:
            rows.append({
                "drgn1":             9,
                "educ3":             educ3,
                "sex":               sex,
                "gsur":              np.nan,
                "weighting_source":  "population",
                "gsur_age_band_used": "Y20-64_fallback_dom_absent",
                "denom_flag":        "drgn1_9_dom_absent_fr2016",
                "n_components":      0,
                "gsur_unreliable":   True,
            })
    stub = pd.DataFrame(rows)
    return pd.concat([df, stub], ignore_index=True)


# ---------------------------------------------------------------------------
# 7. D1 vs D2 diagnostic at Y15-74 (v2.1 §5 D2 documentation requirement)
# ---------------------------------------------------------------------------

def d1_vs_d2_diagnostic(
    gsur_df: pd.DataFrame,
    d1: pd.DataFrame,
    d2: pd.DataFrame,
    cw: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute the aggregated GSUR rate at Y15-74 under D1 and D2 weighting.
    Returns a comparison DataFrame for the validation report.
    """
    # D2 at Y15-74
    d2_agg = aggregate_drgn1(gsur_df, d2, cw, age_band="Y15-74")
    d2_agg = d2_agg.rename(columns={"gsur": "gsur_d2_y1574"})

    # D1 at Y15-74 -- same logic, using D1 populations instead of D2
    d1_for_agg = d1.rename(columns={"OBS_VALUE": "OBS_VALUE", "OBS_FLAG": "OBS_FLAG"})
    # Need same column structure as D2 for the aggregator
    d1_like_d2 = d1_for_agg.copy()
    d1_like_d2["age"] = "Y15-74"
    d1_agg = aggregate_drgn1(gsur_df, d1_like_d2, cw, age_band="Y15-74")
    d1_agg = d1_agg.rename(columns={"gsur": "gsur_d1_y1574"})

    diag = d2_agg[["drgn1","educ3","sex","gsur_d2_y1574"]].merge(
        d1_agg[["drgn1","educ3","sex","gsur_d1_y1574"]],
        on=["drgn1","educ3","sex"], how="left"
    )
    diag["diff_d2_minus_d1"] = diag["gsur_d2_y1574"] - diag["gsur_d1_y1574"]
    diag["abs_diff"] = diag["diff_d2_minus_d1"].abs()
    return diag


# ---------------------------------------------------------------------------
# 8. Build legacy gsur from FR_gsur.xlsx (TOTAL sex, Y20-64, no education)
#    for gsur_legacy_misaligned -- what v1 used
# ---------------------------------------------------------------------------

def build_legacy_gsur(gsur_df: pd.DataFrame) -> pd.DataFrame:
    """
    The legacy v1 GSUR assigned a single rate per (drgn1) with no sex/educ
    stratification, using TOTAL sex and Y20-64. We reconstruct this from
    FR10 (Ile-de-France) directly (drgn1=1) and the TOTAL sex Y20-64 value
    for the other regions.

    The legacy assignment was also misaligned (v1 crosswalk errors), but we
    store the best reconstruction we can make of v1 assignment per drgn1.
    Returns: {drgn1 -> legacy_gsur_prop}
    """
    total_y2064 = gsur_df[
        (gsur_df["age"] == "Y20-64") &
        (gsur_df["sex"] == "T") &
        (gsur_df["isced11"] == "TOTAL")
    ][["geo","ur_pct"]].set_index("geo")["ur_pct"]

    # We need a single value per drgn1 -- use unweighted mean across NUTS-2 components
    # (this is the v1 approximation; we flag it as misaligned)
    cw = load_crosswalk()
    records = {}
    for drgn1_val, grp in cw.groupby("drgn1"):
        rates = []
        for nuts2 in grp["new_nuts2_code_2016"]:
            if nuts2 in total_y2064.index and pd.notna(total_y2064[nuts2]):
                rates.append(total_y2064[nuts2] / 100.0)
        records[drgn1_val] = float(np.mean(rates)) if rates else np.nan
    return records


# ---------------------------------------------------------------------------
# 9. Main build
# ---------------------------------------------------------------------------

def build_lookup() -> pd.DataFrame:
    print("Loading crosswalk...")
    cw = load_crosswalk()
    print(f"  {len(cw)} NUTS-2 rows, drgn1 range {cw['drgn1'].min()}-{cw['drgn1'].max()}")

    print("Loading FR_gsur.xlsx unemployment rates...")
    gsur_df = load_gsur_workbook()
    print(f"  {len(gsur_df)} geo x isced x sex x age records")

    print("Loading D2 population denominators (operational)...")
    d2 = load_d2()
    print(f"  {len(d2)} D2 rows")

    print("Loading D1 labour-force denominators (diagnostic only)...")
    d1 = load_d1()
    print(f"  {len(d1)} D1 rows")

    print("Building legacy gsur reconstruction...")
    legacy = build_legacy_gsur(gsur_df)

    print("Aggregating Y20-64 rates to drgn1 x educ3 x sex (Stage A)...")
    lookup = aggregate_drgn1(gsur_df, d2, cw, age_band="Y20-64")
    print(f"  {len(lookup)} rows before drgn1=9 stub")

    # Add drgn1=9 stub (O5)
    lookup = add_drgn9_stub(lookup)

    # Add legacy gsur_legacy_misaligned (unweighted TOTAL sex mean per drgn1)
    lookup["gsur_legacy_misaligned"] = lookup["drgn1"].map(legacy)

    # Add year
    lookup["year"] = YEAR

    # Add gsur_age_band_used for standard Y20-64 rows
    # (already set in aggregate_drgn1; O3 flag for age-65 rows is set at merge time)
    # For the lookup itself, document the age_band as Y20-64
    lookup.loc[lookup["drgn1"] != 9, "gsur_age_band_used"] = "Y20-64"

    # Sort
    lookup = lookup.sort_values(["drgn1","educ3","sex"]).reset_index(drop=True)

    # D1 vs D2 diagnostic
    print("Computing D1 vs D2 diagnostic at Y15-74...")
    diag = d1_vs_d2_diagnostic(gsur_df, d1, d2, cw)
    # Store diagnostic in a separate attribute (not in the main parquet)
    lookup._d1_vs_d2_diagnostic = diag

    return lookup


# ---------------------------------------------------------------------------
# 10. Validation checks
# ---------------------------------------------------------------------------

def run_validations(lookup: pd.DataFrame, gsur_df: pd.DataFrame, cw: pd.DataFrame) -> dict:
    results = {}

    # -- L1: Unique keys (drgn1, educ3, sex) --
    key_cols = ["drgn1","educ3","sex"]
    n_dupes = lookup.duplicated(subset=key_cols).sum()
    results["L1_unique_keys"] = {
        "pass": n_dupes == 0,
        "n_duplicates": int(n_dupes),
        "n_rows": len(lookup),
    }

    # -- L2: Proportion units [0,1] --
    valid_rows = lookup[lookup["gsur"].notna()]
    in_range = ((valid_rows["gsur"] >= 0) & (valid_rows["gsur"] <= 1)).all()
    results["L2_proportion_units"] = {
        "pass": bool(in_range),
        "min": float(valid_rows["gsur"].min()) if len(valid_rows) > 0 else None,
        "max": float(valid_rows["gsur"].max()) if len(valid_rows) > 0 else None,
    }

    # -- L3: drgn1 support --
    drgn1_present = set(lookup["drgn1"].unique())
    expected = set(range(1, 10))   # 1-9 (9 = stub NaN)
    results["L3_drgn1_support"] = {
        "pass": expected <= drgn1_present,
        "present": sorted(drgn1_present),
        "missing": sorted(expected - drgn1_present),
    }

    # -- L4: Ile-de-France sanity (drgn1=1 = FR10, unambiguous 1:1) --
    idf_rows = lookup[lookup["drgn1"] == 1]
    idf_src = gsur_df[
        (gsur_df["geo"] == "FR10") &
        (gsur_df["age"] == "Y20-64") &
        (gsur_df["sex"].isin(["M","F"]))
    ]
    idf_checks = []
    for _, row in idf_rows.iterrows():
        isced = EDUC3_TO_ISCED[row["educ3"]]
        src = idf_src[(idf_src["isced11"] == isced) & (idf_src["sex"] == row["sex"])]
        if len(src) > 0:
            expected_val = src.iloc[0]["ur_pct"] / 100.0
            diff = abs(row["gsur"] - expected_val)
            idf_checks.append({
                "educ3": row["educ3"], "sex": row["sex"],
                "computed": row["gsur"], "source": expected_val, "diff": diff,
                "pass": diff <= IDF_TOL,
            })
    idf_pass = all(c["pass"] for c in idf_checks)
    results["L4_idf_crosswalk_sanity"] = {
        "pass": idf_pass,
        "tolerance": IDF_TOL,
        "checks": idf_checks,
    }

    # -- L5: National benchmark consistency --
    # Aggregate all drgn1=1..8 using D2 population weights to produce national rate
    d2 = load_d2()
    d2_y2064 = d2[
        (d2["age"] == "Y20-64") &
        d2["isced11"].isin(["ED0-2","ED3_4","ED5-8"]) &
        d2["sex"].isin(["M","F"])
    ]
    # Compute educ3-sex national rate: sum(ur * pop) / sum(pop)
    metro_rows = lookup[lookup["drgn1"].between(1, 8)]
    # Join populations from D2 for drgn1=1..8 NUTS-2 components
    nat_num = 0.0
    nat_den = 0.0
    for drgn1_val, grp_cw in cw.groupby("drgn1"):
        for nuts2 in grp_cw["new_nuts2_code_2016"]:
            for isced_code in ["ED0-2","ED3_4","ED5-8"]:
                for sex_val in SEX_MF:
                    gsur_row = gsur_df[
                        (gsur_df["geo"] == nuts2) &
                        (gsur_df["isced11"] == isced_code) &
                        (gsur_df["sex"] == sex_val) &
                        (gsur_df["age"] == "Y20-64")
                    ]
                    pop_row = d2_y2064[
                        (d2_y2064["geo"] == nuts2) &
                        (d2_y2064["isced11"] == isced_code) &
                        (d2_y2064["sex"] == sex_val)
                    ]
                    if len(gsur_row) == 0 or len(pop_row) == 0:
                        continue
                    ur  = gsur_row.iloc[0]["ur_pct"] / 100.0
                    pop = pop_row.iloc[0]["OBS_VALUE"]
                    if np.isnan(ur) or np.isnan(pop):
                        continue
                    nat_num += ur * pop
                    nat_den += pop

    nat_rate = nat_num / nat_den if nat_den > 0 else np.nan
    diff_from_benchmark = abs(nat_rate - BENCHMARK_PROP) if not np.isnan(nat_rate) else np.nan
    results["L5_national_benchmark"] = {
        "pass": bool(diff_from_benchmark <= BENCHMARK_TOL) if not np.isnan(diff_from_benchmark) else False,
        "computed_national_rate_pct": round(nat_rate * 100, 4) if not np.isnan(nat_rate) else None,
        "benchmark_pct": BENCHMARK_PCT,
        "diff_pct": round(diff_from_benchmark * 100, 4) if not np.isnan(diff_from_benchmark) else None,
        "tolerance_pct": BENCHMARK_TOL * 100,
        "benchmark_source": f"INSEE BDM 001688526, {YEAR} annual average (O9)",
    }

    # -- L7: Weighting-source documentation --
    ws_counts = lookup["weighting_source"].value_counts().to_dict()
    results["L7_weighting_source"] = {
        "pass": True,
        "counts": {str(k): int(v) for k, v in ws_counts.items()},
    }

    # -- L8: Approximation flags --
    d3_rows = lookup[lookup["weighting_source"] == "approximate_uniform"]
    results["L8_approximation_flags"] = {
        "pass": True,
        "n_d3_rows": len(d3_rows),
        "d3_cells": d3_rows[["drgn1","educ3","sex","denom_flag"]].to_dict("records"),
    }

    # -- Missing value check --
    n_gsur_nan = lookup[lookup["drgn1"].between(1, 8)]["gsur"].isna().sum()
    results["missing_values"] = {
        "pass": n_gsur_nan == 0,
        "n_gsur_nan_drgn1_1_8": int(n_gsur_nan),
        "n_gsur_nan_drgn1_9": int(lookup[lookup["drgn1"] == 9]["gsur"].isna().sum()),
    }

    # -- L10-diag: Old vs corrected comparison --
    both_valid = lookup[lookup["gsur"].notna() & lookup["gsur_legacy_misaligned"].notna()]
    abs_diffs = (both_valid["gsur"] - both_valid["gsur_legacy_misaligned"]).abs()
    results["L10_diag_old_vs_corrected"] = {
        "n_comparable": len(both_valid),
        "mean_abs_diff_pct": round(float(abs_diffs.mean()) * 100, 4),
        "max_abs_diff_pct":  round(float(abs_diffs.max()) * 100, 4),
        "note": "Diagnostic only. v1 legacy is misaligned by design; large diffs expected.",
    }

    # -- IDF parity check against source workbook FR10 (spec §13 L4, §14 M4) --
    # Correct comparison: drgn1=1 is a single-NUTS-2 group (FR10 only),
    # so computed gsur must equal the FR10 source value exactly.
    # Comparing against gsur_legacy_misaligned is wrong because v1 stored
    # TOTAL-sex / TOTAL-educ rates, not stratified values.
    xl_idf = pd.ExcelFile(EXT / "FR_gsur.xlsx")
    IDF_SHEET_MAP = {
        ("ED0-2", "M"): "Sheet 45",
        ("ED0-2", "F"): "Sheet 55",
        ("ED3_4", "M"): "Sheet 75",
        ("ED3_4", "F"): "Sheet 85",
        ("ED5-8", "M"): "Sheet 105",
        ("ED5-8", "F"): "Sheet 115",
    }
    idf_checks_src = []
    for (isced_code, sex_val), sh in IDF_SHEET_MAP.items():
        df_sh = pd.read_excel(xl_idf, sheet_name=sh, header=None)
        try:
            col_yr = _find_year_col(df_sh, YEAR)
        except KeyError:
            continue
        for i in range(12, len(df_sh)):
            geo = df_sh.iloc[i, 0]
            if str(geo).strip() != "FR10":
                continue
            try:
                src_val = float(df_sh.iloc[i, col_yr]) / 100.0
            except (ValueError, TypeError):
                src_val = np.nan
            educ3_val = ISCED_TO_EDUC3[isced_code]
            lu_row = lookup[(lookup["drgn1"] == 1) & (lookup["educ3"] == educ3_val) & (lookup["sex"] == sex_val)]
            computed = float(lu_row.iloc[0]["gsur"]) if len(lu_row) > 0 else np.nan
            diff = abs(computed - src_val) if not (np.isnan(computed) or np.isnan(src_val)) else np.nan
            idf_checks_src.append({
                "isced11": isced_code, "educ3": educ3_val, "sex": sex_val,
                "source_pct": round(src_val * 100, 2), "computed": computed,
                "diff": diff, "pass": diff <= IDF_TOL if not np.isnan(diff) else False,
            })
            break

    idf_parity_pass = all(c["pass"] for c in idf_checks_src)
    idf_parity_max = max((c["diff"] for c in idf_checks_src if not np.isnan(c["diff"])), default=np.nan)
    results["IDF_parity"] = {
        "pass": idf_parity_pass,
        "max_abs_diff": round(idf_parity_max, 6) if not np.isnan(idf_parity_max) else None,
        "tolerance": IDF_TOL,
        "checks": idf_checks_src,
        "note": (
            "Compared against FR10 source workbook values (spec §13 L4). "
            "drgn1=1 has a single NUTS-2 component (FR10) so diff must be 0.000."
        ),
    }

    return results


# ---------------------------------------------------------------------------
# 11. Entry point
# ---------------------------------------------------------------------------

def main():
    global YEAR, BENCHMARK_PCT, BENCHMARK_PROP, OUT, SIDECAR

    # C1: parse --opportunity-year
    parser = argparse.ArgumentParser(
        description="Stage A GSUR lookup builder — parameterised by opportunity year."
    )
    parser.add_argument(
        "--opportunity-year", type=int, required=True,
        metavar="YEAR",
        help="Opportunity year for GSURv2 construction (2014, 2015, or 2016).",
    )
    args = parser.parse_args()
    YEAR = args.opportunity_year

    # C5: read BENCHMARK_PCT from year-specific INSEE CSV (annual_average row)
    benchmark_csv = EXT / f"insee_001688526_{YEAR}.csv"
    bdf = pd.read_csv(benchmark_csv)
    avg_row = bdf[bdf["period"].astype(str) == str(YEAR)]
    if len(avg_row) == 0:
        raise ValueError(
            f"Annual-average row (period={YEAR}) not found in {benchmark_csv}"
        )
    BENCHMARK_PCT  = float(avg_row.iloc[0]["value_pct"])
    BENCHMARK_PROP = BENCHMARK_PCT / 100.0

    # C6: year-tagged output and sidecar paths
    OUT     = EXT / f"FR_gsur_ruro_v2_stageA_y{YEAR}.parquet"
    SIDECAR = EXT / f"FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json"

    print("=" * 70)
    print("enh_prepare_FR_gsur_v2.py — Stage A GSUR lookup build")
    print(f"  Opportunity year : {YEAR}")
    print(f"  Benchmark PCT    : {BENCHMARK_PCT}")
    print(f"  Output           : {OUT}")
    print("=" * 70)

    # Safety guard: refuse to write MNL parquets
    FORBIDDEN = [
        REPO / "fr_2016_RURO_mnl_GSURv2__singles.parquet",
        REPO / "fr_2016_RURO_mnl_GSURv2__couples.parquet",
        REPO / "fr_2016_RURO_mnl__singles.parquet",
        REPO / "fr_2016_RURO_mnl__couples.parquet",
    ]
    for f in FORBIDDEN:
        assert OUT != f, f"GUARD: script must not write to {f}"

    lookup = build_lookup()

    print("\nRunning validation checks...")
    gsur_df = load_gsur_workbook()
    cw = load_crosswalk()
    val = run_validations(lookup, gsur_df, cw)

    print("\nValidation summary:")
    overall_pass = True
    for k, v in val.items():
        if isinstance(v, dict) and "pass" in v:
            status = "PASS" if v["pass"] else "FAIL"
            if not v["pass"]:
                overall_pass = False
            print(f"  {k}: {status}")
    print(f"\nOverall: {'PASS' if overall_pass else 'FAIL'}")

    # D3 sign-off notice
    d3_rows = lookup[lookup["weighting_source"] == "approximate_uniform"]
    if len(d3_rows) > 0:
        print("\nNOTICE: D3 (approximate_uniform) cells present — reviewer sign-off required (O2/v2.1 §5(D3)(b)):")
        for _, r in d3_rows.iterrows():
            print(f"  drgn1={r['drgn1']} educ3={r['educ3']} sex={r['sex']}  denom_flag={r['denom_flag']}")

    # Drop private diagnostic attribute before writing
    diag = getattr(lookup, "_d1_vs_d2_diagnostic", None)

    cols_order = [
        "year", "drgn1", "educ3", "sex",
        "gsur", "weighting_source", "gsur_age_band_used",
        "gsur_legacy_misaligned",
        "denom_flag", "n_components", "gsur_unreliable",
    ]
    lookup_out = lookup[[c for c in cols_order if c in lookup.columns]]

    print(f"\nWriting lookup to {OUT} ...")
    lookup_out.to_parquet(OUT, index=False, engine="pyarrow")
    print(f"  Wrote {len(lookup_out)} rows x {len(lookup_out.columns)} columns")

    # Print D1 vs D2 diagnostic summary
    if diag is not None:
        print("\nD1 vs D2 diagnostic summary (Y15-74):")
        print(f"  Mean |D2-D1| = {diag['abs_diff'].mean()*100:.3f} ppt")
        print(f"  Max  |D2-D1| = {diag['abs_diff'].max()*100:.3f} ppt")

    # C7: write sidecar JSON with provenance metadata
    try:
        script_sha = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--",
             str(pathlib.Path(__file__).resolve())],
            cwd=str(REPO), stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        script_sha = "unknown"

    idf_diff       = val.get("IDF_parity", {}).get("max_abs_diff")
    benchmark_diff = val.get("L5_national_benchmark", {}).get("diff_pct")

    sidecar_data = {
        "opportunity_year":            YEAR,
        "gsur_column_name":            "gsur",
        "output_path":                 str(OUT.relative_to(REPO)).replace("\\", "/"),
        "input_d2":                    f"Data/external/lfst_r_lfsd2pop_FR_{YEAR}.tsv",
        "input_d1":                    f"Data/external/lfst_r_lfp2acedu_FR_{YEAR}.tsv",
        "input_unemployment_workbook": "Data/external/FR_gsur.xlsx",
        "input_benchmark_csv":         f"Data/external/insee_001688526_{YEAR}.csv",
        "benchmark_pct":               BENCHMARK_PCT,
        "nuts_vintage":                "NUTS2016",
        "idf_parity_difference":       idf_diff,
        "benchmark_difference_pct":    benchmark_diff,
        "row_count":                   len(lookup_out),
        "build_timestamp":             datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script_version":              script_sha,
    }
    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump(sidecar_data, fh, indent=2)
    print(f"  Wrote sidecar to {SIDECAR}")

    return lookup_out, val, diag


if __name__ == "__main__":
    main()