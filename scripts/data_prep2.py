#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-10-22 11:10:48
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# %% Bootstrap (Interactive Window friendly paths and helpers)
import os
import sys
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

# Ensure pythonnet uses CoreCLR runtime for Euromod
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

import euromod as em
import numpy as np
import pandas as pd
import matplotlib
#%% 
matplotlib.use("Agg")  # ensure headless plotting for batch runs
import matplotlib.pyplot as plt

# Resolve script paths both in file and notebook modes
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd() / "scripts"

PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()

for candidate in (SCRIPT_DIR, PROJECT_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

os.chdir(PROJECT_ROOT)

from path_helpers import data_root, euromod_root, outputs_root, ensure_dir, euromod_raw_root, DE_DEFAULT_SYSTEMS

# ----- Constants used in multiple places -----
WPM = 52 / 12  # weeks-per-month factor for wage reconstruction (~4.3333)

# Allow importing helper functions from scratch/

# Allow importing helper functions from scratch/
SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

# Import project helpers
try:
    from scratch.my_functions import (
        apply_abnormal_filter,
        compute_wage_recon,
        correct_labor_status,
        apply_filtering_pipeline,
        apply_other_members_filter,
        check_data_quality,
        create_income_columns,
        create_stats_entry,
        export_gender_split_data,
        export_household_data,
        get_head_counts,
        identify_extreme_households,
        log_filtering_step,
        process_couples_data,
        process_singles_data,
        setup_logging,
        validate_household_integrity,
        validate_required_columns,
    )  # type: ignore
except ImportError as e:
    raise ImportError(
        "Missing helpers in scratch/my_functions.py (e.g., create_income_columns, get_head_counts)."
    ) from e

# Canonical project paths (storage-aware)
DATA_ROOT = data_root()
RAW_DIR = (DATA_ROOT / "raw") if (DATA_ROOT / "raw").exists() else DATA_ROOT
PROCESSED_DIR = ensure_dir(DATA_ROOT / "processed")

MODEL_DIR = euromod_root()
OUTPUTS_DIR = ensure_dir(outputs_root() / "prep")
PLOTS_DIR = ensure_dir(OUTPUTS_DIR / "plots")

# Configuration parameters (keep thresholds consistent across the pipeline)
CONFIG = {
    "age_range": (16, 65),
    "replacement_income_cap": 100,
    "allowed_les": [3, 5, 7],
    "extreme_wage_diff": 500,        # monthly absolute gap for extremes
    "wage_bounds": (2, 170),
    "hour_bounds": (10, 70),
    "target_country": "DE",
    "target_system": "DE_2014",
    "target_dataset": "DE_2015_a1",
    "export_format": "parquet",
    "plot_bins": 40,
}

# Variables to plot for quick EDA
PLOT_VARIABLES = {
    "lhw": {"label": "Weekly hours worked (lhw)", "discrete": False},
    "yivwg": {"label": "Gross wage (yivwg)", "discrete": False},
    "ils_disp": {"label": "Disposable income (ils_disp)", "discrete": False},
    "yem": {"label": "Employment income (yem)", "discrete": False},
    "les": {"label": "Labour status code (les)", "discrete": True},
    "loc": {"label": "Occupation class (loc)", "discrete": True},
    "lindi": {"label": "Industry class (lindi)", "discrete": True},
    "dag": {"label": "Age (dag)", "discrete": False},
    "dehde": {"label": "Highest education (dehde)", "discrete": True},
    "num_children_total": {"label": "Number of children", "discrete": True},
}

def _plot_distribution(series: pd.Series, title: str, output_path: Path, *, discrete: bool, bins: int) -> None:
    """Save a histogram/bar plot for a series; silently skip if empty."""
    clean = series.dropna()
    if clean.empty:
        print(f"Skipping '{series.name}' for '{title}': no data after filtering")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    if discrete or (pd.api.types.is_integer_dtype(clean) and clean.nunique() <= bins / 2):
        counts = clean.value_counts().sort_index()
        ax.bar(counts.index.astype(str), counts.values, color="#4C72B0")  # type: ignore
        ax.set_ylabel("Count")
    else:
        ax.hist(clean, bins=bins, color="#4C72B0", edgecolor="white")
        ax.set_ylabel("Frequency")

    ax.set_title(title)
    ax.set_xlabel(title.split(" - ")[0])
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

def _generate_group_plots(df: pd.DataFrame, *, group_name: str, prefix: str, bins: int) -> dict[str, Path]:
    """Create plots for df and return a mapping {variable: saved_path} for that group."""
    saved_paths: dict[str, Path] = {}
    for column, info in PLOT_VARIABLES.items():
        if column not in df.columns:
            print(f"Skipping '{column}' for '{group_name}': column missing")
            continue
        output_path = PLOTS_DIR / f"{prefix}_{column}.png"
        title = f"{info['label']} - {group_name}"
        _plot_distribution(df[column], title, output_path, discrete=info["discrete"], bins=bins)
        saved_paths[column] = output_path
    return saved_paths

def _generate_gender_plots(df: pd.DataFrame, *, base_group: str, prefix: str, bins: int) -> dict[str, dict[str, Path]]:
    """Produce plots for overall and gender-specific subsets (0=female, 1=male)."""
    results: dict[str, dict[str, Path]] = {}
    results["overall"] = _generate_group_plots(df, group_name=base_group, prefix=f"{prefix}_overall", bins=bins)

    for gender_code, gender_label in [(0, "female"), (1, "male")]:
        subset = df[df["dgn"].astype(float) == gender_code]
        if subset.empty:
            print(f"No records for {base_group} - {gender_label}, skipping plots")
            continue
        results[gender_label] = _generate_group_plots(
            subset,
            group_name=f"{base_group} ({gender_label})",
            prefix=f"{prefix}_{gender_label}",
            bins=bins,
        )
    return results



def load_de_txt(raw_path: Path) -> pd.DataFrame:
    """Load DE micro-data stored as tab-delimited text."""
    return pd.read_csv(raw_path, sep="	")

def clean_harmonize(df: pd.DataFrame, *, country: str) -> pd.DataFrame:
    """
    Country-specific wrapper for the harmonisation/cleaning step.

    For now we only support DE explicitly.  Later we can add FR or other
    countries (e.g. clean_harmonize_fr) and dispatch here.
    """
    country = country.upper()

    if country == "DE":
        return clean_harmonize_de(df)

    if country == "FR":
        return clean_harmonize_fr(df)

    raise NotImplementedError(f"clean_harmonize is not implemented for country={country!r}")


def clean_harmonize_de(df: pd.DataFrame) -> pd.DataFrame:
    """Run the EUROMOD simulation and filtering pipeline, returning the merged dataframe."""
    setup_logging("INFO")
    # Run EUROMOD model
    mod = em.Model(str(MODEL_DIR))
    TARGET_SYSTEM = CONFIG["target_system"]
    TARGET_DATASET = CONFIG["target_dataset"]

    country = mod["DE"]
    try:
        system = country[TARGET_SYSTEM]
    except KeyError:
        # Fallback: take the first available system if target not present
        if hasattr(country, "systems"):
            systems_iter = country.systems.values()  # type: ignore[attr-defined]
        else:
            systems_iter = country.values()  # type: ignore[attr-defined]
        system = next(iter(systems_iter))

    dataset = None
    if hasattr(system, "datasets"):
        try:
            dataset = system.datasets[TARGET_DATASET]
        except (KeyError, AttributeError):
            dataset = None

    if dataset is None:
        candidates = [ds for ds in getattr(system, "bestmatch_datasets", []) if getattr(ds, "name", "") == TARGET_DATASET]
        dataset = candidates[0] if candidates else system.bestmatch_datasets[0]

    system_name = getattr(system, "name", TARGET_SYSTEM)
    dataset_name = getattr(dataset, "name", TARGET_DATASET)
    print(f"Running EUROMOD system {system_name} with dataset {dataset_name}")

    sim = system.run(df, dataset.name)
    df_sim = sim.outputs[0]
    print("raw df info (memory_usage='deep'):")
    df.info(memory_usage="deep")  # type: ignore[arg-type]

    # %% Head of Households tags
    df_sim["hh_IsHead"] = (df_sim["tu_hh_de_HeadID"] == df_sim["idperson"]).astype(int)
        # NEW: generic partner flag for downstream code (used instead of tu_hh_de_IsPartner)
    df_sim["hh_IsPartner"] = (df_sim["tu_hh_de_IsPartner"] == 1).astype(int)
    is_single_head = df_sim.groupby("idhh")["hh_IsHead"].sum().eq(1)
    print(f"Number of households with a single head: {is_single_head.sum()}")
    multi_head_count = df_sim.groupby("idhh")["hh_IsHead"].sum().gt(1).sum()
    print(f"Number of households with multiple heads: {multi_head_count}")
    print(f"Number of unique households in the dataset: {df_sim['idhh'].nunique()}")

    # Build income aggregates (EUROMOD -> analysis-friendly columns)
    print("Columns and info before creation of aggregates:")
    df_sim.info(memory_usage="deep")
    df_sim1 = create_income_columns(df_sim)
    print("Columns and info after creation of aggregates:")
    df_sim1.info(memory_usage="deep")

    # %% Keep a contiguous block of relevant columns from the aggregates frame
    start_var = "tu_family2_de_HeadID"
    end_var = "income_total_overall"
    sim1_cols = [col.strip() for col in df_sim1.columns.tolist()]
    try:
        start_index = sim1_cols.index(start_var)
        end_index = sim1_cols.index(end_var)
    except ValueError as err:
        raise ValueError("One or both boundary columns were not found in df_sim1.") from err

    required_columns = sim1_cols[start_index : end_index + 1]
    print("Required columns in df_sim1 to keep:", required_columns)

    # %% Merge original microdata with EUROMOD outputs
    if "idperson" not in df.columns or "idperson" not in df_sim1.columns:
        raise ValueError("idperson is not present in both DataFrames!")

    final_df_sim1 = df.merge(df_sim1[["idperson"] + required_columns], on="idperson", how="left")
    print("Final merged frame shape:", final_df_sim1.shape)

    # %% Sanity checks: required cols & household integrity
    REQUIRED_COLUMNS = ["idperson", "idhh", "dag", "dgn", "les", "yem", "lhw", "yivwg"]
    validate_required_columns(final_df_sim1, REQUIRED_COLUMNS)

    if not validate_household_integrity(final_df_sim1):
        print("Warning: Household integrity issues detected!")

    quality_issues = check_data_quality(final_df_sim1)
    if quality_issues:
        print(f"Data quality issues detected: {quality_issues}")

    # %% Enforce LES (conservative, restricted to {2,3,7}) with dominance logic
    final_df_sim1["les_orig"] = final_df_sim1["les"]

    # Align with main pipeline: rely on default dominance logic (emp_threshold=0)
    final_df_sim1 = correct_labor_status(final_df_sim1, emp_threshold=100)


    # Enforce {2,3,7} with dominance; align emp_threshold with reconstruction (yem>100 considered employee cash)
    chg = final_df_sim1["les_enforced"] != final_df_sim1["les_orig"]
    print("Reclassified away from employee (3->!=3):", int(((final_df_sim1["les_orig"] == 3) & chg).sum()))
    print("Total status changes:", int(chg.sum()))
    print(pd.crosstab(final_df_sim1["les_orig"], final_df_sim1["les_enforced"], rownames=["les_orig"], colnames=["les_enforced"]))

    # %% Wage reconstruction for employees and periodicity diagnostics
    final_df_sim1 = compute_wage_recon(final_df_sim1)

    # Recompute monthly-from-hours (strict)
    yem_from_hours = final_df_sim1["w_emp_strict"] * final_df_sim1["lhw"] * WPM

    # Periodicity tests:
    #  - div12: observed yem looks like annual/12 vs recon monthly
    #  - liwmy: observed yem matches recon scaled by months-worked / 12
    m_div12 = np.isclose(final_df_sim1["yem"], yem_from_hours / 12, rtol=0.05, atol=5)
    m_liwmy = np.isclose(
        final_df_sim1["yem"],
        yem_from_hours * (final_df_sim1["liwmy"].clip(lower=0, upper=12).fillna(0) / 12),
        rtol=0.10,
        atol=5,
    )

    valid_emp = final_df_sim1["les_enforced"].eq(3) & final_df_sim1["lhw"].ge(CONFIG["hour_bounds"][0])
    final_df_sim1["flag_periodicity"] = valid_emp & (m_div12 | m_liwmy)

    # (Enhancement) Describe which rule triggered the fix (purely informational)
    final_df_sim1["periodicity_type"] = np.select(
        [valid_emp & m_div12, valid_emp & m_liwmy],
        ["div12", "liwmy"],
        default=""
    )

    # Correct yem for periodicity; otherwise keep observed
    final_df_sim1["yem_corrected"] = np.where(final_df_sim1["flag_periodicity"], yem_from_hours, final_df_sim1["yem"])

    # Final wage/diff metrics used for screening
    final_df_sim1["wage_final"] = final_df_sim1["w_emp_strict"]
    final_df_sim1["yem2_final"] = np.where(valid_emp, final_df_sim1["wage_final"] * final_df_sim1["lhw"] * WPM, np.nan)
    final_df_sim1["diff_yem_final"] = np.where(valid_emp, final_df_sim1["yem2_final"] - final_df_sim1["yem_corrected"], np.nan)

    CONFIG["extreme_diff_column"] = "diff_yem_final"

    # ==== OPTION 1: ADULT-ONLY SCREENING (exclude minors from outlier test) ====
    adults = final_df_sim1["dag"].fillna(0).ge(18)  # age >= 18
    screen_idx = adults & valid_emp & ~final_df_sim1["flag_periodicity"].fillna(False)

    households_to_remove = identify_extreme_households(final_df_sim1.loc[screen_idx], CONFIG)
    print("Extreme-screened population (adults, valid_emp, not periodicity-flagged):", int(screen_idx.sum()))
    print("Households to remove:", households_to_remove)

    # %% Point diagnostic: how many unresolved large positives/negatives remain?
    count_extreme_negative = (final_df_sim1["diff_yem_final"] <= -CONFIG["extreme_wage_diff"]).sum()


    extreme_positive = final_df_sim1.loc[
        # keep diagnostics consistent with removal policy
        adults & valid_emp &
        (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"]) &
        (~final_df_sim1["flag_periodicity"].fillna(False))
    ]

    print("Count of records with unresolved diff_yem >= 500:", len(extreme_positive))
    print(
        extreme_positive[
            [
                "yem_corrected", "yem2_final", "yds", "yse", "diff_yem_final",
                "lhw", "yivwg", "wage_final", "les_orig", "les_enforced",
                "les_suggested", "lindi", "loc", "lse",
            ]
        ].describe()
    )

    extreme_positive_ids = extreme_positive[["idhh", "idperson"]].to_numpy().tolist()
    print("Count unresolved diff_yem >= 500:", len(extreme_positive), "| IDs:", extreme_positive_ids[:5])
    print("Count diff_yem <= -500:", int(count_extreme_negative))

    # %% Diagnostic audit: characteristics of extreme positive wage differences
    # -----------------------------------------------------------------------------
    # Analyze the adult employee subset where reconstructed monthly wage (yem2_final)
    # exceeds observed (yem_corrected) by >= CONFIG["extreme_wage_diff"] and is not
    # explained by periodicity. This block is diagnostic only; no dropping occurs here.
    # -----------------------------------------------------------------------------
    # --- Diagnostic: unresolved extreme positives (adult + valid_emp + not-periodic) ---
    ep = final_df_sim1.loc[
        adults & valid_emp &
        (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"]) &
        (~final_df_sim1["flag_periodicity"].fillna(False))
    ].copy()

    if ep.empty:
        print("No unresolved extreme positive gaps under adult+valid_emp+not-periodic screen.")
    else:
        prop_yem_zero = (ep["yem_corrected"] == 0).mean()
        print("Share with yem_corrected == 0 in extreme positives:", round(prop_yem_zero, 3))
        print(ep["yem_corrected"].describe())

        eq_rate = np.isclose(ep["wage_final"], ep["yivwg"], rtol=1e-6, atol=1e-6).mean()
        print("Share with wage_final ~= yivwg (imputed):", round(eq_rate, 3))
        print(ep[["wage_final", "yivwg"]].describe())

        median_recon = ep["wage_final"].median() * ep["lhw"].median() * (52 / 12)
        print("Medians - yem2_final, diff_yem_final, recon_estimated:",
              round(ep["yem2_final"].median(), 2),
              round(ep["diff_yem_final"].median(), 2),
              round(median_recon, 2))
        print("Hours distribution among extreme positives:\n", ep["lhw"].describe())

        hp_left  = pd.to_numeric(final_df_sim1["hh_IsHead"], errors="coerce").fillna(0).eq(1)
        hp_right = pd.to_numeric(final_df_sim1["hh_IsPartner"], errors="coerce").fillna(0).eq(1)
        is_head_partner = hp_left | hp_right

        share_hp_in_ep = is_head_partner.loc[ep.index].mean()
        print("Share of heads/partners among extreme positives:", round(share_hp_in_ep, 3))
        counts_hp = is_head_partner.loc[ep.index].value_counts().rename({True: "Head/Partner", False: "Other household member"})
        print("Counts in extreme positives by role:\n", counts_hp)


    # Sanity check on months-worked variables
    print("\nDistribution of liwmy (months worked in income period):")
    print(final_df_sim1["liwmy"].describe())
    print("Number of records with liwmy > 12:", (final_df_sim1["liwmy"] > 12).sum(),
          "\nUnique liwmy values (first 20):", final_df_sim1["liwmy"].unique()[:20])
    print("\nSample of months-worked variables:")
    print(final_df_sim1[["liwmy", "liwftmy", "liwptmy"]].head(10))


    #%% eligibility
    # ---- Final analysis eligibility flags ----

    # Logic:
    # - Keep only target labour-status codes (CONFIG["allowed_les"]).
    # - Apply age band (inclusive).
    # - Apply hours and wage bounds **only for employees (les_enforced==3)**.
    # - Drop any households flagged for extreme unresolved wage diffs.

    is_emp = final_df_sim1["les_enforced"].eq(3)

    ready_allowed_les = final_df_sim1["les_enforced"].isin(CONFIG["allowed_les"])
    ready_age         = final_df_sim1["dag"].between(*CONFIG["age_range"])

    # Hours bounds apply only to employees; non-employees pass this check.
    ready_hours = (~is_emp) | final_df_sim1["lhw"].between(*CONFIG["hour_bounds"])

    # Wage bounds apply only to employees; for non-employees or missing wages, pass.
    ready_wage = (
        (~is_emp)
        | final_df_sim1["wage_final"].between(*CONFIG["wage_bounds"])
        | final_df_sim1["wage_final"].isna()
    )

    ready_no_unresolved_extreme = ~final_df_sim1["idhh"].isin(households_to_remove)

    final_df_sim1["keep_for_analysis"] = (
        ready_allowed_les & ready_age & ready_hours & ready_wage & ready_no_unresolved_extreme
    )

    print(
        "keep_for_analysis: "
        f"{int(final_df_sim1['keep_for_analysis'].sum())} / {len(final_df_sim1)} "
        "rows meet eligibility criteria."
    )

    # ---- Construct parent-level child counts in age bands ----
    # We treat a person as a child if their own age (dag) falls in the band,
    # then attribute that child to each listed parent (idfather/idmother != 0/NaN).

    child_bands = {
        "num_children_0_3":  final_df_sim1["dag"].ge(0)  & final_df_sim1["dag"].le(3),   # include newborns
        "num_children_3_6":  final_df_sim1["dag"].gt(3)  & final_df_sim1["dag"].le(6),
        "num_children_6_11": final_df_sim1["dag"].gt(6)  & final_df_sim1["dag"].le(11),
        "num_children_11_17":final_df_sim1["dag"].gt(11) & final_df_sim1["dag"].le(17),
    }
    child_flags = pd.DataFrame(child_bands, index=final_df_sim1.index)

    # Build long table linking each child to each available parent id
    parent_links = pd.concat(
        [child_flags, final_df_sim1[["idfather", "idmother"]]],
        axis=1,
    )
    parent_links = parent_links.melt(
        id_vars=list(child_bands.keys()),
        value_vars=["idfather", "idmother"],
        var_name="parent_role",
        value_name="parent_id",
    )

    # Keep valid parent ids (non-missing, non-zero)
    valid_parent = parent_links["parent_id"].notna() & parent_links["parent_id"].ne(0)

    # Aggregate child-band indicators to the parent_id level (each parent totals their children)
    parent_counts = (
        parent_links.loc[valid_parent]
        .groupby("parent_id")[list(child_bands.keys())]
        .sum()
    )

    # Add a total children column and order columns
    parent_counts["num_children_total"] = parent_counts.sum(axis=1)
    parent_counts = parent_counts[
        [
            "num_children_total",
            "num_children_0_3",
            "num_children_3_6",
            "num_children_6_11",
            "num_children_11_17",
        ]
    ]

    # Merge parent-level child counts back to the person file on idperson (as parent_id)
    final_df_sim1 = final_df_sim1.merge(
        parent_counts,
        how="left",
        left_on="idperson",
        right_index=True,
    )

    # Fill missing counts with 0 and cast to int
    child_cols = parent_counts.columns.tolist()
    final_df_sim1[child_cols] = final_df_sim1[child_cols].fillna(0).astype(int)

    # ---- Persist prepared master snapshot ----
    prep_path = PROCESSED_DIR / f"{TARGET_DATASET}_prepared_master.csv"
    final_df_sim1.to_csv(prep_path, index=False)
    print("Saved prepared master to:", prep_path)

    # From this point on, use the enforced labour status as canonical
    final_df_sim1["les"] = final_df_sim1["les_enforced"]

    # =============================================================================
    # Couples Filtering Pipeline
    # =============================================================================
    # Applies stepwise filtering to couples households and records stats at each step.

    print("\n=== Couples filtering pipeline ===")
    # Start from the full master (unfiltered) to show all step drops
    df_couples = process_couples_data(final_df_sim1)

    couples_initial = df_couples["idhh"].nunique()    # Initial number of couples households
    print(f"Couples baseline households: {couples_initial}")

    couples_stats_records: list[dict] = []            # List to store stats for each filtering step
    total, female, male = get_head_counts(df_couples) # Get initial counts of heads by gender
    couples_stats_records.append(
        create_stats_entry(
            "Baseline",
            "Initial couples households",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # Apply main filtering pipeline for couples (head and partner roles)
    couples_filtered, couples_pipeline_stats = apply_filtering_pipeline(
        df_couples,
        role_filters=[
            ("hh_IsHead", "Head"),
            ("hh_IsPartner", "Partner"),
        ],
        household_type="couples",
        initial_count=couples_initial,
        config=CONFIG,
    )

    couples_stats_records.extend(couples_pipeline_stats)  # Add stepwise stats

    # Filter out households with ineligible other members (e.g., additional adults)
    before_other = couples_filtered["idhh"].nunique()
    couples_no_other = apply_other_members_filter(couples_filtered, CONFIG)
    after_other = couples_no_other["idhh"].nunique()
    log_filtering_step("Other Household Members", before_other, after_other)
    total, female, male = get_head_counts(couples_no_other)
    couples_stats_records.append(
        create_stats_entry(
            "Other Household Members",
            "Drop households with ineligible other members",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # Final filter: drop households with abnormal wage or labor time for employees
    before_abnormal = couples_no_other["idhh"].nunique()
    couples_final = apply_abnormal_filter(couples_no_other, households_to_remove, CONFIG)
    after_abnormal = couples_final["idhh"].nunique()
    log_filtering_step("Wage & Labor Time", before_abnormal, after_abnormal)
    total, female, male = get_head_counts(couples_final)
    couples_stats_records.append(
        create_stats_entry(
            "Wage & Labor Time",
            "Drop households with les==3 and abnormal wage or hours",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # --- Final Eligibility intersection (to match global keep_for_analysis) ---
    before_final_elig = couples_final["idhh"].nunique()
    couples_final = couples_final.loc[couples_final["keep_for_analysis"]].copy()
    after_final_elig = couples_final["idhh"].nunique()
    log_filtering_step("Final Eligibility (keep_for_analysis)", before_final_elig, after_final_elig)
    total, female, male = get_head_counts(couples_final)
    couples_stats_records.append(
        create_stats_entry(
            "Final Eligibility",
            "Intersect with global eligibility flags (keep_for_analysis)",
            total,
            female,
            male,
            couples_initial,
        )
    )


    # Compile all stepwise stats into a DataFrame for export
    couples_stats_df = pd.DataFrame(couples_stats_records)[
        ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
    ]

    # Export the final filtered couples dataset and the LaTeX summary table (if any rows remain)
    if not couples_final.empty:
        couples_exports = export_household_data(
            df=couples_final,
            stats_df=couples_stats_df,
            output_prefix="couples_filtering",
            output_dir=OUTPUTS_DIR,
            processed_dir=PROCESSED_DIR,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Couples outputs:", couples_exports)
    else:
        print("Couples outputs: skipped (no households after filtering)")

    # =============================================================================
    # Singles Filtering Pipeline
    # =============================================================================
    # Applies stepwise filtering to singles households and records stats at each step.

    print("\n=== Singles filtering pipeline ===")
    # Start from the full master (unfiltered) to show all step drops
    df_singles = process_singles_data(final_df_sim1)

    singles_initial = df_singles["idhh"].nunique()    # Initial number of singles households
    print(f"Singles baseline households: {singles_initial}")

    singles_stats_records: list[dict] = []            # List to store stats for each filtering step
    total, female, male = get_head_counts(df_singles) # Get initial counts of heads by gender
    singles_stats_records.append(
        create_stats_entry(
            "Baseline",
            "Initial singles households",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # Apply main filtering pipeline for singles (head role only)
    singles_filtered, singles_pipeline_stats = apply_filtering_pipeline(
        df_singles,
        role_filters=[("hh_IsHead", "Head")],
        household_type="singles",
        initial_count=singles_initial,
        config=CONFIG,
    )
    singles_stats_records.extend(singles_pipeline_stats)  # Add stepwise stats

    # Filter out singles households with ineligible other members
    before_other = singles_filtered["idhh"].nunique()
    singles_no_other = apply_other_members_filter(singles_filtered, CONFIG)
    after_other = singles_no_other["idhh"].nunique()
    log_filtering_step("Other Household Members (Singles)", before_other, after_other)
    total, female, male = get_head_counts(singles_no_other)
    singles_stats_records.append(
        create_stats_entry(
            "Other Household Members",
            "Drop households with ineligible other members",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # Final filter: drop singles with abnormal wage or labor time for employees
    before_abnormal = singles_no_other["idhh"].nunique()
    singles_final = apply_abnormal_filter(singles_no_other, households_to_remove, CONFIG)
    after_abnormal = singles_final["idhh"].nunique()
    log_filtering_step("Wage & Labor Time (Singles)", before_abnormal, after_abnormal)
    total, female, male = get_head_counts(singles_final)
    singles_stats_records.append(
        create_stats_entry(
            "Wage & Labor Time",
            "Drop singles with les==3 and abnormal wage or hours",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # --- Final Eligibility intersection (to match global keep_for_analysis) ---
    before_final_elig_s = singles_final["idhh"].nunique()
    singles_final = singles_final.loc[singles_final["keep_for_analysis"]].copy()
    after_final_elig_s = singles_final["idhh"].nunique()
    log_filtering_step("Final Eligibility (keep_for_analysis)", before_final_elig_s, after_final_elig_s)
    total, female, male = get_head_counts(singles_final)
    singles_stats_records.append(
        create_stats_entry(
            "Final Eligibility",
            "Intersect with global eligibility flags (keep_for_analysis)",
            total,
            female,
            male,
            singles_initial,
        )
    )


    # Compile all stepwise stats into a DataFrame for export
    singles_stats_df = pd.DataFrame(singles_stats_records)[
        ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
    ]

    # Export the final filtered singles dataset and the LaTeX summary table (if any rows remain)
    if not singles_final.empty:
        singles_exports = export_household_data(
            df=singles_final,
            stats_df=singles_stats_df,
            output_prefix="singles_filtering",
            output_dir=OUTPUTS_DIR,
            processed_dir=PROCESSED_DIR,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Singles outputs:", singles_exports)
    else:
        print("Singles outputs: skipped (no households after filtering)")

    # =============================================================================
    # Gender-Split Exports and Plots
    # =============================================================================
    # Exports gender-specific singles datasets and generates summary plots for singles heads,
    # couples heads, and couples partners.

    # Gender-split exports only if we have singles remaining
    if not singles_final.empty:
        gender_exports = export_gender_split_data(
            singles_final,
            output_prefix="singles_final_filtered",
            processed_dir=PROCESSED_DIR,
            export_pickle=False,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Singles gender-split exports:", gender_exports)
    else:
        print("Singles gender-split exports: skipped (no households)")

    # Plot distributions for singles heads by gender
    plot_bins = int(CONFIG.get("plot_bins", 40))
    singles_heads = singles_final[singles_final["hh_IsHead"] == 1]
    if not singles_heads.empty:
        singles_plot_paths = _generate_gender_plots(
            singles_heads,
            base_group="Singles Heads",
            prefix="singles_heads",
            bins=plot_bins,
        )
        print("Singles head plots saved:", singles_plot_paths)
    else:
        print("Singles head plots: skipped (no data)")

    # Plot distributions for couples heads by gender
    couples_heads = couples_final[couples_final["hh_IsHead"] == 1]
    if not couples_heads.empty:
        couples_head_plot_paths = _generate_gender_plots(
            couples_heads,
            base_group="Couples Heads",
            prefix="couples_heads",
            bins=plot_bins,
        )
        print("Couples head plots saved:", couples_head_plot_paths)
    else:
        print("Couples head plots: skipped (no data)")

    # Plot distributions for couples partners by gender
    couples_partners = couples_final[couples_final["hh_IsPartner"] == 1]
    if not couples_partners.empty:
        couples_partner_plot_paths = _generate_gender_plots(
            couples_partners,
            base_group="Couples Partners",
            prefix="couples_partners",
            bins=plot_bins,
        )
        print("Couples partner plots saved:", couples_partner_plot_paths)
    else:
        print("Couples partner plots: skipped (no data)")
    #%%
    return final_df_sim1



def clean_harmonize_fr(df: pd.DataFrame) -> pd.DataFrame:
    """Run the EUROMOD simulation and filtering pipeline, returning the merged dataframe."""
    setup_logging("INFO")
    # Helper: pick the first available column from a list of candidates
    def _first_available(column_candidates: list[str], df_cols: pd.Index, desc: str) -> str:
        for c in column_candidates:
            if c in df_cols:
                return c
        raise KeyError(f"No column found for {desc}; tried {column_candidates}. Available columns: {list(df_cols)}")

    # Run EUROMOD model
    mod = em.Model(str(MODEL_DIR))
    TARGET_SYSTEM = CONFIG["target_system"]
    TARGET_DATASET = CONFIG["target_dataset"]

    country = mod["FR"]
    try:
        system = country[TARGET_SYSTEM]
    except KeyError:
        # Fallback: take the first available system if target not present
        if hasattr(country, "systems"):
            systems_iter = country.systems.values()  # type: ignore[attr-defined]
        else:
            systems_iter = country.values()  # type: ignore[attr-defined]
        system = next(iter(systems_iter))

    dataset = None
    if hasattr(system, "datasets"):
        try:
            dataset = system.datasets[TARGET_DATASET]
        except (KeyError, AttributeError):
            dataset = None

    if dataset is None:
        candidates = [ds for ds in getattr(system, "bestmatch_datasets", []) if getattr(ds, "name", "") == TARGET_DATASET]
        dataset = candidates[0] if candidates else system.bestmatch_datasets[0]

    system_name = getattr(system, "name", TARGET_SYSTEM)
    dataset_name = getattr(dataset, "name", TARGET_DATASET)
    print(f"Running EUROMOD system {system_name} with dataset {dataset_name}")

    sim = system.run(df, dataset.name)
    df_sim = sim.outputs[0]
    print("raw df info (memory_usage='deep'):")
    df.info(memory_usage="deep")  # type: ignore[arg-type]

    # %% Head of Households tags
    head_col = _first_available(
        [
            "tu_household_fr_HeadID", "tu_household_fr_headid",
            "tu_hh_fr_HeadID", "tu_hh_fr_headid",
            "tu_household_HeadID", "tu_household_headid",
            "tu_hh_HeadID", "tu_hh_headid",
            "tu_household_de_HeadID", "tu_hh_de_HeadID",
        ],
        df_sim.columns,
        "household head ID",
    )
    # Head flag (already fine)
    df_sim["hh_IsHead"] = (df_sim[head_col] == df_sim["idperson"]).astype(int)

    # Partner flag: use EUROMOD partner variable if it exists, otherwise derive from idpartner
    partner_flag_cols = [
        "tu_hh_fr_IsPartner", "tu_hh_fr_ispartner",
        "tu_hh_IsPartner", "tu_hh_ispartner",
        "tu_hh_de_IsPartner",
    ]

    partner_col = next((c for c in partner_flag_cols if c in df_sim.columns), None)

    if partner_col is not None:
        # Simple 0/1 flag from EUROMOD
        df_sim["hh_IsPartner"] = (df_sim[partner_col] == 1).astype(int)
    elif "idpartner" in df_sim.columns:
        # Derive: partner is the person whose idpartner == head_id and is not the head
        head_ids = df_sim[head_col]
        df_sim["hh_IsPartner"] = ((df_sim["idpartner"] == head_ids) & (df_sim["idperson"] != head_ids)).astype(int)
    else:
        # Fallback: no partner info available
        df_sim["hh_IsPartner"] = 0
    is_single_head = df_sim.groupby("idhh")["hh_IsHead"].sum().eq(1)
    print(f"Number of households with a single head: {is_single_head.sum()}")
    multi_head_count = df_sim.groupby("idhh")["hh_IsHead"].sum().gt(1).sum()
    print(f"Number of households with multiple heads: {multi_head_count}")
    print(f"Number of unique households in the dataset: {df_sim['idhh'].nunique()}")

    # Build income aggregates (EUROMOD -> analysis-friendly columns)
    print("Columns and info before creation of aggregates:")
    df_sim.info(memory_usage="deep")
    df_sim1 = create_income_columns(df_sim)
    print("Columns and info after creation of aggregates:")
    df_sim1.info(memory_usage="deep")

    # %% Keep a contiguous block of relevant columns from the aggregates frame
    start_var_candidates = [
        "tu_fiscalunit_fr_HeadID",
        "tu_household_fr_HeadID",
        "tu_family2_fr_HeadID",
        "tu_family2_fr_headid",
        "tu_family2_HeadID",
        "tu_family2_headid",
        "tu_family2_de_HeadID",
    ]
    start_var = _first_available(start_var_candidates, df_sim1.columns, "family/fiscal unit HeadID")
    end_var = "income_total_overall"
    sim1_cols = [col.strip() for col in df_sim1.columns.tolist()]
    try:
        start_index = sim1_cols.index(start_var)
        end_index = sim1_cols.index(end_var)
    except ValueError as err:
        raise ValueError("One or both boundary columns were not found in df_sim1.") from err

    required_columns = sim1_cols[start_index : end_index + 1]
    print("Required columns in df_sim1 to keep:", required_columns)

    # %% Merge original microdata with EUROMOD outputs
    if "idperson" not in df.columns or "idperson" not in df_sim1.columns:
        raise ValueError("idperson is not present in both DataFrames!")

    final_df_sim1 = df.merge(df_sim1[["idperson"] + required_columns], on="idperson", how="left")
    print("Final merged frame shape:", final_df_sim1.shape)

    # %% Sanity checks: required cols & household integrity
    REQUIRED_COLUMNS = ["idperson", "idhh", "dag", "dgn", "les", "yem", "lhw", "yivwg"]
    validate_required_columns(final_df_sim1, REQUIRED_COLUMNS)

    if not validate_household_integrity(final_df_sim1):
        print("Warning: Household integrity issues detected!")

    quality_issues = check_data_quality(final_df_sim1)
    if quality_issues:
        print(f"Data quality issues detected: {quality_issues}")

    # %% Enforce LES (conservative, restricted to {2,3,7}) with dominance logic
    final_df_sim1["les_orig"] = final_df_sim1["les"]

    # Align with main pipeline: rely on default dominance logic (emp_threshold=0)
    final_df_sim1 = correct_labor_status(final_df_sim1, emp_threshold=100)


    # Enforce {2,3,7} with dominance; align emp_threshold with reconstruction (yem>100 considered employee cash)
    chg = final_df_sim1["les_enforced"] != final_df_sim1["les_orig"]
    print("Reclassified away from employee (3->!=3):", int(((final_df_sim1["les_orig"] == 3) & chg).sum()))
    print("Total status changes:", int(chg.sum()))
    print(pd.crosstab(final_df_sim1["les_orig"], final_df_sim1["les_enforced"], rownames=["les_orig"], colnames=["les_enforced"]))

    # %% Wage reconstruction for employees and periodicity diagnostics
    final_df_sim1 = compute_wage_recon(final_df_sim1)

    # Recompute monthly-from-hours (strict)
    yem_from_hours = final_df_sim1["w_emp_strict"] * final_df_sim1["lhw"] * WPM

    # Periodicity tests:
    #  - div12: observed yem looks like annual/12 vs recon monthly
    #  - liwmy: observed yem matches recon scaled by months-worked / 12
    m_div12 = np.isclose(final_df_sim1["yem"], yem_from_hours / 12, rtol=0.05, atol=5)
    m_liwmy = np.isclose(
        final_df_sim1["yem"],
        yem_from_hours * (final_df_sim1["liwmy"].clip(lower=0, upper=12).fillna(0) / 12),
        rtol=0.10,
        atol=5,
    )

    valid_emp = final_df_sim1["les_enforced"].eq(3) & final_df_sim1["lhw"].ge(CONFIG["hour_bounds"][0])
    final_df_sim1["flag_periodicity"] = valid_emp & (m_div12 | m_liwmy)

    # (Enhancement) Describe which rule triggered the fix (purely informational)
    final_df_sim1["periodicity_type"] = np.select(
        [valid_emp & m_div12, valid_emp & m_liwmy],
        ["div12", "liwmy"],
        default=""
    )

    # Correct yem for periodicity; otherwise keep observed
    final_df_sim1["yem_corrected"] = np.where(final_df_sim1["flag_periodicity"], yem_from_hours, final_df_sim1["yem"])

    # Final wage/diff metrics used for screening
    final_df_sim1["wage_final"] = final_df_sim1["w_emp_strict"]
    final_df_sim1["yem2_final"] = np.where(valid_emp, final_df_sim1["wage_final"] * final_df_sim1["lhw"] * WPM, np.nan)
    final_df_sim1["diff_yem_final"] = np.where(valid_emp, final_df_sim1["yem2_final"] - final_df_sim1["yem_corrected"], np.nan)

    CONFIG["extreme_diff_column"] = "diff_yem_final"

    # ==== OPTION 1: ADULT-ONLY SCREENING (exclude minors from outlier test) ====
    adults = final_df_sim1["dag"].fillna(0).ge(18)  # age >= 18
    screen_idx = adults & valid_emp & ~final_df_sim1["flag_periodicity"].fillna(False)

    households_to_remove = identify_extreme_households(final_df_sim1.loc[screen_idx], CONFIG)
    print("Extreme-screened population (adults, valid_emp, not periodicity-flagged):", int(screen_idx.sum()))
    print("Households to remove:", households_to_remove)

    # %% Point diagnostic: how many unresolved large positives/negatives remain?
    count_extreme_negative = (final_df_sim1["diff_yem_final"] <= -CONFIG["extreme_wage_diff"]).sum()


    extreme_positive = final_df_sim1.loc[
        # keep diagnostics consistent with removal policy
        adults & valid_emp &
        (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"]) &
        (~final_df_sim1["flag_periodicity"].fillna(False))
    ]

    print("Count of records with unresolved diff_yem >= 500:", len(extreme_positive))
    print(
        extreme_positive[
            [
                "yem_corrected", "yem2_final", "yds", "yse", "diff_yem_final",
                "lhw", "yivwg", "wage_final", "les_orig", "les_enforced",
                "les_suggested", "lindi", "loc", "lse",
            ]
        ].describe()
    )

    extreme_positive_ids = extreme_positive[["idhh", "idperson"]].to_numpy().tolist()
    print("Count unresolved diff_yem >= 500:", len(extreme_positive), "| IDs:", extreme_positive_ids[:5])
    print("Count diff_yem <= -500:", int(count_extreme_negative))

    # %% Diagnostic audit: characteristics of extreme positive wage differences
    # -----------------------------------------------------------------------------
    # Analyze the adult employee subset where reconstructed monthly wage (yem2_final)
    # exceeds observed (yem_corrected) by >= CONFIG["extreme_wage_diff"] and is not
    # explained by periodicity. This block is diagnostic only; no dropping occurs here.
    # -----------------------------------------------------------------------------
    # --- Diagnostic: unresolved extreme positives (adult + valid_emp + not-periodic) ---
    ep = final_df_sim1.loc[
        adults & valid_emp &
        (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"]) &
        (~final_df_sim1["flag_periodicity"].fillna(False))
    ].copy()

    if ep.empty:
        print("No unresolved extreme positive gaps under adult+valid_emp+not-periodic screen.")
    else:
        prop_yem_zero = (ep["yem_corrected"] == 0).mean()
        print("Share with yem_corrected == 0 in extreme positives:", round(prop_yem_zero, 3))
        print(ep["yem_corrected"].describe())

        eq_rate = np.isclose(ep["wage_final"], ep["yivwg"], rtol=1e-6, atol=1e-6).mean()
        print("Share with wage_final ~= yivwg (imputed):", round(eq_rate, 3))
        print(ep[["wage_final", "yivwg"]].describe())

        median_recon = ep["wage_final"].median() * ep["lhw"].median() * (52 / 12)
        print("Medians - yem2_final, diff_yem_final, recon_estimated:",
              round(ep["yem2_final"].median(), 2),
              round(ep["diff_yem_final"].median(), 2),
              round(median_recon, 2))
        print("Hours distribution among extreme positives:\n", ep["lhw"].describe())

        hp_left  = pd.to_numeric(final_df_sim1["hh_IsHead"], errors="coerce").fillna(0).eq(1)
        hp_right = pd.to_numeric(final_df_sim1["hh_IsPartner"], errors="coerce").fillna(0).eq(1)
        is_head_partner = hp_left | hp_right

        share_hp_in_ep = is_head_partner.loc[ep.index].mean()
        print("Share of heads/partners among extreme positives:", round(share_hp_in_ep, 3))
        counts_hp = is_head_partner.loc[ep.index].value_counts().rename({True: "Head/Partner", False: "Other household member"})
        print("Counts in extreme positives by role:\n", counts_hp)


    # Sanity check on months-worked variables
    print("\nDistribution of liwmy (months worked in income period):")
    print(final_df_sim1["liwmy"].describe())
    print("Number of records with liwmy > 12:", (final_df_sim1["liwmy"] > 12).sum(),
          "\nUnique liwmy values (first 20):", final_df_sim1["liwmy"].unique()[:20])
    print("\nSample of months-worked variables:")
    print(final_df_sim1[["liwmy", "liwftmy", "liwptmy"]].head(10))


    #%% eligibility
    # ---- Final analysis eligibility flags ----

    # Logic:
    # - Keep only target labour-status codes (CONFIG["allowed_les"]).
    # - Apply age band (inclusive).
    # - Apply hours and wage bounds **only for employees (les_enforced==3)**.
    # - Drop any households flagged for extreme unresolved wage diffs.

    is_emp = final_df_sim1["les_enforced"].eq(3)

    ready_allowed_les = final_df_sim1["les_enforced"].isin(CONFIG["allowed_les"])
    ready_age         = final_df_sim1["dag"].between(*CONFIG["age_range"])

    # Hours bounds apply only to employees; non-employees pass this check.
    ready_hours = (~is_emp) | final_df_sim1["lhw"].between(*CONFIG["hour_bounds"])

    # Wage bounds apply only to employees; for non-employees or missing wages, pass.
    ready_wage = (
        (~is_emp)
        | final_df_sim1["wage_final"].between(*CONFIG["wage_bounds"])
        | final_df_sim1["wage_final"].isna()
    )

    ready_no_unresolved_extreme = ~final_df_sim1["idhh"].isin(households_to_remove)

    final_df_sim1["keep_for_analysis"] = (
        ready_allowed_les & ready_age & ready_hours & ready_wage & ready_no_unresolved_extreme
    )

    print(
        "keep_for_analysis: "
        f"{int(final_df_sim1['keep_for_analysis'].sum())} / {len(final_df_sim1)} "
        "rows meet eligibility criteria."
    )

    # ---- Construct parent-level child counts in age bands ----
    # We treat a person as a child if their own age (dag) falls in the band,
    # then attribute that child to each listed parent (idfather/idmother != 0/NaN).

    child_bands = {
        "num_children_0_3":  final_df_sim1["dag"].ge(0)  & final_df_sim1["dag"].le(3),   # include newborns
        "num_children_3_6":  final_df_sim1["dag"].gt(3)  & final_df_sim1["dag"].le(6),
        "num_children_6_11": final_df_sim1["dag"].gt(6)  & final_df_sim1["dag"].le(11),
        "num_children_11_17":final_df_sim1["dag"].gt(11) & final_df_sim1["dag"].le(17),
    }
    child_flags = pd.DataFrame(child_bands, index=final_df_sim1.index)

    # Build long table linking each child to each available parent id
    parent_links = pd.concat(
        [child_flags, final_df_sim1[["idfather", "idmother"]]],
        axis=1,
    )
    parent_links = parent_links.melt(
        id_vars=list(child_bands.keys()),
        value_vars=["idfather", "idmother"],
        var_name="parent_role",
        value_name="parent_id",
    )

    # Keep valid parent ids (non-missing, non-zero)
    valid_parent = parent_links["parent_id"].notna() & parent_links["parent_id"].ne(0)

    # Aggregate child-band indicators to the parent_id level (each parent totals their children)
    parent_counts = (
        parent_links.loc[valid_parent]
        .groupby("parent_id")[list(child_bands.keys())]
        .sum()
    )

    # Add a total children column and order columns
    parent_counts["num_children_total"] = parent_counts.sum(axis=1)
    parent_counts = parent_counts[
        [
            "num_children_total",
            "num_children_0_3",
            "num_children_3_6",
            "num_children_6_11",
            "num_children_11_17",
        ]
    ]

    # Merge parent-level child counts back to the person file on idperson (as parent_id)
    final_df_sim1 = final_df_sim1.merge(
        parent_counts,
        how="left",
        left_on="idperson",
        right_index=True,
    )

    # Fill missing counts with 0 and cast to int
    child_cols = parent_counts.columns.tolist()
    final_df_sim1[child_cols] = final_df_sim1[child_cols].fillna(0).astype(int)

    # ---- Persist prepared master snapshot ----
    prep_path = PROCESSED_DIR / f"{TARGET_DATASET}_prepared_master.csv"
    final_df_sim1.to_csv(prep_path, index=False)
    print("Saved prepared master to:", prep_path)

    # From this point on, use the enforced labour status as canonical
    final_df_sim1["les"] = final_df_sim1["les_enforced"]

    # =============================================================================
    # Couples Filtering Pipeline
    # =============================================================================
    # Applies stepwise filtering to couples households and records stats at each step.

    print("\n=== Couples filtering pipeline ===")
    # Start from the full master (unfiltered) to show all step drops
    df_couples = process_couples_data(final_df_sim1)

    couples_initial = df_couples["idhh"].nunique()    # Initial number of couples households
    print(f"Couples baseline households: {couples_initial}")

    couples_stats_records: list[dict] = []            # List to store stats for each filtering step
    total, female, male = get_head_counts(df_couples) # Get initial counts of heads by gender
    couples_stats_records.append(
        create_stats_entry(
            "Baseline",
            "Initial couples households",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # Apply main filtering pipeline for couples (head and partner roles)
    couples_filtered, couples_pipeline_stats = apply_filtering_pipeline(
        df_couples,
        role_filters=[
            ("hh_IsHead", "Head"),
            ("hh_IsPartner", "Partner"),
        ],
        household_type="couples",
        initial_count=couples_initial,
        config=CONFIG,
    )

    couples_stats_records.extend(couples_pipeline_stats)  # Add stepwise stats

    # Filter out households with ineligible other members (e.g., additional adults)
    before_other = couples_filtered["idhh"].nunique()
    couples_no_other = apply_other_members_filter(couples_filtered, CONFIG)
    after_other = couples_no_other["idhh"].nunique()
    log_filtering_step("Other Household Members", before_other, after_other)
    total, female, male = get_head_counts(couples_no_other)
    couples_stats_records.append(
        create_stats_entry(
            "Other Household Members",
            "Drop households with ineligible other members",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # Final filter: drop households with abnormal wage or labor time for employees
    before_abnormal = couples_no_other["idhh"].nunique()
    couples_final = apply_abnormal_filter(couples_no_other, households_to_remove, CONFIG)
    after_abnormal = couples_final["idhh"].nunique()
    log_filtering_step("Wage & Labor Time", before_abnormal, after_abnormal)
    total, female, male = get_head_counts(couples_final)
    couples_stats_records.append(
        create_stats_entry(
            "Wage & Labor Time",
            "Drop households with les==3 and abnormal wage or hours",
            total,
            female,
            male,
            couples_initial,
        )
    )

    # --- Final Eligibility intersection (to match global keep_for_analysis) ---
    before_final_elig = couples_final["idhh"].nunique()
    couples_final = couples_final.loc[couples_final["keep_for_analysis"]].copy()
    after_final_elig = couples_final["idhh"].nunique()
    log_filtering_step("Final Eligibility (keep_for_analysis)", before_final_elig, after_final_elig)
    total, female, male = get_head_counts(couples_final)
    couples_stats_records.append(
        create_stats_entry(
            "Final Eligibility",
            "Intersect with global eligibility flags (keep_for_analysis)",
            total,
            female,
            male,
            couples_initial,
        )
    )


    # Compile all stepwise stats into a DataFrame for export
    couples_stats_df = pd.DataFrame(couples_stats_records)[
        ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
    ]

    # Export the final filtered couples dataset and the LaTeX summary table (if any rows remain)
    if not couples_final.empty:
        couples_exports = export_household_data(
            df=couples_final,
            stats_df=couples_stats_df,
            output_prefix="couples_filtering",
            output_dir=OUTPUTS_DIR,
            processed_dir=PROCESSED_DIR,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Couples outputs:", couples_exports)
    else:
        print("Couples outputs: skipped (no households after filtering)")

    # =============================================================================
    # Singles Filtering Pipeline
    # =============================================================================
    # Applies stepwise filtering to singles households and records stats at each step.

    print("\n=== Singles filtering pipeline ===")
    # Start from the full master (unfiltered) to show all step drops
    df_singles = process_singles_data(final_df_sim1)

    singles_initial = df_singles["idhh"].nunique()    # Initial number of singles households
    print(f"Singles baseline households: {singles_initial}")

    singles_stats_records: list[dict] = []            # List to store stats for each filtering step
    total, female, male = get_head_counts(df_singles) # Get initial counts of heads by gender
    singles_stats_records.append(
        create_stats_entry(
            "Baseline",
            "Initial singles households",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # Apply main filtering pipeline for singles (head role only)
    singles_filtered, singles_pipeline_stats = apply_filtering_pipeline(
        df_singles,
        role_filters=[("hh_IsHead", "Head")],
        household_type="singles",
        initial_count=singles_initial,
        config=CONFIG,
    )
    singles_stats_records.extend(singles_pipeline_stats)  # Add stepwise stats

    # Filter out singles households with ineligible other members
    before_other = singles_filtered["idhh"].nunique()
    singles_no_other = apply_other_members_filter(singles_filtered, CONFIG)
    after_other = singles_no_other["idhh"].nunique()
    log_filtering_step("Other Household Members (Singles)", before_other, after_other)
    total, female, male = get_head_counts(singles_no_other)
    singles_stats_records.append(
        create_stats_entry(
            "Other Household Members",
            "Drop households with ineligible other members",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # Final filter: drop singles with abnormal wage or labor time for employees
    before_abnormal = singles_no_other["idhh"].nunique()
    singles_final = apply_abnormal_filter(singles_no_other, households_to_remove, CONFIG)
    after_abnormal = singles_final["idhh"].nunique()
    log_filtering_step("Wage & Labor Time (Singles)", before_abnormal, after_abnormal)
    total, female, male = get_head_counts(singles_final)
    singles_stats_records.append(
        create_stats_entry(
            "Wage & Labor Time",
            "Drop singles with les==3 and abnormal wage or hours",
            total,
            female,
            male,
            singles_initial,
        )
    )

    # --- Final Eligibility intersection (to match global keep_for_analysis) ---
    before_final_elig_s = singles_final["idhh"].nunique()
    singles_final = singles_final.loc[singles_final["keep_for_analysis"]].copy()
    after_final_elig_s = singles_final["idhh"].nunique()
    log_filtering_step("Final Eligibility (keep_for_analysis)", before_final_elig_s, after_final_elig_s)
    total, female, male = get_head_counts(singles_final)
    singles_stats_records.append(
        create_stats_entry(
            "Final Eligibility",
            "Intersect with global eligibility flags (keep_for_analysis)",
            total,
            female,
            male,
            singles_initial,
        )
    )


    # Compile all stepwise stats into a DataFrame for export
    singles_stats_df = pd.DataFrame(singles_stats_records)[
        ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
    ]

    # Export the final filtered singles dataset and the LaTeX summary table (if any rows remain)
    if not singles_final.empty:
        singles_exports = export_household_data(
            df=singles_final,
            stats_df=singles_stats_df,
            output_prefix="singles_filtering",
            output_dir=OUTPUTS_DIR,
            processed_dir=PROCESSED_DIR,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Singles outputs:", singles_exports)
    else:
        print("Singles outputs: skipped (no households after filtering)")

    # =============================================================================
    # Gender-Split Exports and Plots
    # =============================================================================
    # Exports gender-specific singles datasets and generates summary plots for singles heads,
    # couples heads, and couples partners.

    # Gender-split exports only if we have singles remaining
    if not singles_final.empty:
        gender_exports = export_gender_split_data(
            singles_final,
            output_prefix="singles_final_filtered",
            processed_dir=PROCESSED_DIR,
            export_pickle=False,
            export_format=CONFIG.get("export_format", "parquet"),
        )
        print("Singles gender-split exports:", gender_exports)
    else:
        print("Singles gender-split exports: skipped (no households)")

    # Plot distributions for singles heads by gender
    plot_bins = int(CONFIG.get("plot_bins", 40))
    singles_heads = singles_final[singles_final["hh_IsHead"] == 1]
    if not singles_heads.empty:
        singles_plot_paths = _generate_gender_plots(
            singles_heads,
            base_group="Singles Heads",
            prefix="singles_heads",
            bins=plot_bins,
        )
        print("Singles head plots saved:", singles_plot_paths)
    else:
        print("Singles head plots: skipped (no data)")

    # Plot distributions for couples heads by gender
    couples_heads = couples_final[couples_final["hh_IsHead"] == 1]
    if not couples_heads.empty:
        couples_head_plot_paths = _generate_gender_plots(
            couples_heads,
            base_group="Couples Heads",
            prefix="couples_heads",
            bins=plot_bins,
        )
        print("Couples head plots saved:", couples_head_plot_paths)
    else:
        print("Couples head plots: skipped (no data)")

    # Plot distributions for couples partners by gender
    couples_partners = couples_final[couples_final["hh_IsPartner"] == 1]
    if not couples_partners.empty:
        couples_partner_plot_paths = _generate_gender_plots(
            couples_partners,
            base_group="Couples Partners",
            prefix="couples_partners",
            bins=plot_bins,
        )
        print("Couples partner plots saved:", couples_partner_plot_paths)
    else:
        print("Couples partner plots: skipped (no data)")
    #%%
    return final_df_sim1


def prepare_one_year(
    *,
    country: str,
    year: int,
    raw_filename: str,
    system_year: Optional[int] = None,
    raw_dir: Optional[Path] = None,
    out_dir: Optional[Path] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Prepare a single micro-data year for the given country and persist the cleaned parquet.

    For now the EUROMOD cleaning is implemented only for DE.  The function is
    written in a way that later allows FR (and others) to be plugged in.
    """
    # Normalise country code (e.g. "de" -> "DE")
    country = country.upper()

    # Where to read raw micro-data from: keep existing euromod_raw_root default
    raw_dir = raw_dir or euromod_raw_root()

    # Where to write processed data: processed/<country>/<year>
    out_dir = out_dir or (data_root() / "processed" / country.lower() / str(year))
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / raw_filename
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw micro-data: {raw_path}")

    # For now the loader is DE-specific in name, but it simply reads a tab-delimited file.
    # If FR uses the same export format, this is fine; if not, we can branch on country later.
    data_df = load_de_txt(raw_path)

    # System year: keep the DE_DEFAULT_SYSTEMS mapping for DE, otherwise fall back to 'year'.
    if country == "DE":
        system_year = system_year or DE_DEFAULT_SYSTEMS.get(year, year)
    else:
        system_year = system_year or year  # placeholder; later FR-specific mapping can go here

    dataset_name = Path(raw_filename).stem
    system_code = f"{country}_{system_year}"

    # Temporarily switch global dirs and CONFIG target fields
    global PROCESSED_DIR, OUTPUTS_DIR, PLOTS_DIR
    prev_processed = PROCESSED_DIR
    prev_outputs = OUTPUTS_DIR
    prev_plots = PLOTS_DIR
    PROCESSED_DIR = ensure_dir(out_dir)
    OUTPUTS_DIR = ensure_dir(out_dir / "outputs")
    PLOTS_DIR = ensure_dir(OUTPUTS_DIR / "plots")

    prev_country = CONFIG.get("target_country", "DE")
    prev_system = CONFIG.get("target_system")
    prev_dataset = CONFIG.get("target_dataset")

    CONFIG["target_country"] = country
    CONFIG["target_system"] = system_code
    CONFIG["target_dataset"] = dataset_name

    try:
        # Use the dispatcher instead of calling the DE function directly
        clean_df = clean_harmonize(data_df, country=country)
    finally:
        # Restore previous global state
        CONFIG["target_country"] = prev_country
        CONFIG["target_system"] = prev_system
        CONFIG["target_dataset"] = prev_dataset
        PROCESSED_DIR = prev_processed
        OUTPUTS_DIR = prev_outputs
        PLOTS_DIR = prev_plots

    clean_df["input_year"] = year
    clean_df["system_year"] = system_year
    clean_df["data_year"] = year

    out_file = out_dir / f"{country.lower()}_{year}_clean.parquet"
    clean_df.to_parquet(out_file, index=False)

    meta: Dict[str, Any] = {
        "country": country,
        "year": year,
        "system_year": system_year,
        "raw_path": str(raw_path),
        "output": str(out_file),
        "dataset_name": dataset_name,
        "n_rows": int(clean_df.shape[0]),
        "n_cols": int(clean_df.shape[1]),
    }
    (out_dir / "prep_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out_dir, meta

def _cli_prepare() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare EUROMOD micro-data for a given country and year."
    )
    parser.add_argument(
        "--country",
        type=str,
        default="DE",
        help="Country code, e.g. DE or FR.",
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--raw-file",
        required=True,
        help="Raw micro-data filename, e.g., DE_2015_a1.txt or FR_2021_a1.txt",
    )
    parser.add_argument(
        "--system-year",
        type=int,
        default=None,
        help="Optional override for EUROMOD system year; defaults to mapping or 'year'.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing the raw file; defaults to euromod_raw_root().",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory to write processed outputs; defaults to data_root()/processed/<country>/<year>.",
    )
    args = parser.parse_args()

    prepare_one_year(
        country=args.country,
        year=args.year,
        raw_filename=args.raw_file,
        system_year=args.system_year,
        raw_dir=args.raw_dir,
        out_dir=args.out_dir,
    )

if __name__ == "__main__":
    _cli_prepare()
