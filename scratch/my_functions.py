# =============================================================================
# STEPWISE HOUSEHOLD FILTERING & LATEX EXPORT HELPERS
# =============================================================================

def stepwise_filter_households(df, household_type="couples", config=None):
    """
    Performs stepwise filtering on couples or singles households, returning filtered df and stats DataFrame.
    Steps: Baseline, Age, Education, Replacement Income, Les, Allowed LES, Other Members, Wage/Labor Time.
    """
    if config is None:
        config = {
            "age_range": (16, 65),
            "replacement_income_cap": 100,
            "allowed_les": [3, 5, 7],
            "wage_bounds": (2, 170),
            "hour_bounds": (5, 79),
        }
    stats = []
    df_work = df.copy()
    initial_households = df_work["idhh"].nunique()
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Baseline",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": 100.0,
    })

    # Step 1: Age (Head)
    age_mask = (df_work["hh_IsHead"] == 1) & df_work["dag"].between(*config["age_range"])
    keep_idhh = df_work.loc[age_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Age (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Step 2: Education (Head)
    edu_mask = (df_work["hh_IsHead"] == 1) & (df_work["dec"] == 0)
    keep_idhh = df_work.loc[edu_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Education (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Step 3: Replacement Income (Head)
    inc_mask = (df_work["hh_IsHead"] == 1) & (df_work["replacement_income_total"] <= config["replacement_income_cap"])
    keep_idhh = df_work.loc[inc_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Replacement Income (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Step 4: Les (Head)
    les_mask = (df_work["hh_IsHead"] == 1) & (df_work["les"] != 5)
    keep_idhh = df_work.loc[les_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Les (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Step 5: Allowed LES (Head)
    allowed_mask = (df_work["hh_IsHead"] == 1) & (df_work["les"].isin(config["allowed_les"]))
    keep_idhh = df_work.loc[allowed_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Allowed LES (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Partner steps (for couples only)
    if household_type == "couples":
        # Step 6: Age (Partner)
        age_mask = (df_work["tu_hh_de_IsPartner"] == 1) & df_work["dag"].between(*config["age_range"])
        keep_idhh = df_work.loc[age_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique()
        male = heads[heads["dgn"] == 1]["idhh"].nunique()
        stats.append({
            "Step": "Age (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })

        # Step 7: Education (Partner)
        edu_mask = (df_work["tu_hh_de_IsPartner"] == 1) & (df_work["dec"] == 0)
        keep_idhh = df_work.loc[edu_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique()
        male = heads[heads["dgn"] == 1]["idhh"].nunique()
        stats.append({
            "Step": "Education (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })

        # Step 8: Replacement Income (Partner)
        inc_mask = (df_work["tu_hh_de_IsPartner"] == 1) & (df_work["replacement_income_total"] <= config["replacement_income_cap"])
        keep_idhh = df_work.loc[inc_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique()
        male = heads[heads["dgn"] == 1]["idhh"].nunique()
        stats.append({
            "Step": "Replacement Income (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })

        # Step 9: Les (Partner)
        les_mask = (df_work["tu_hh_de_IsPartner"] == 1) & (df_work["les"] != 5)
        keep_idhh = df_work.loc[les_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique()
        male = heads[heads["dgn"] == 1]["idhh"].nunique()
        stats.append({
            "Step": "Les (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })

        # Step 10: Allowed LES (Partner)
        allowed_mask = (df_work["tu_hh_de_IsPartner"] == 1) & (df_work["les"].isin(config["allowed_les"]))
        keep_idhh = df_work.loc[allowed_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique()
        male = heads[heads["dgn"] == 1]["idhh"].nunique()
        stats.append({
            "Step": "Allowed LES (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })

    # Step: Other Household Members
    # Drop households if any non-head/non-partner meets:
    #   Either: age is between 16 and 65, with ddi == 0 and dec == 0,
    #   OR: has yem > 50 or yse > 0.
    cond = (
        (df_work["hh_IsHead"] == 0)
        & (df_work["tu_hh_de_IsPartner"] == 0)
        & (
            (
                df_work["dag"].between(*config["age_range"])
                & (df_work["ddi"] == 0)
                & (df_work["dec"] == 0)
            )
            | ((df_work["yem"] > 50) | (df_work["yse"] != 0))
        )
    )
    households_to_drop = df_work.loc[cond, "idhh"].unique()
    df_work = df_work[~df_work["idhh"].isin(households_to_drop)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Other Household Members",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    # Step: Wage & Labor Time (abnormal)
    abnormal_mask = (
        (df_work["les"] == 3)
        & (
            (df_work["lhw"] < config["hour_bounds"][0])
            | (df_work["lhw"] > config["hour_bounds"][1])
            | (df_work["wage_final"] < config["wage_bounds"][0])
            | (df_work["wage_final"] > config["wage_bounds"][1])
        )
        & (
            (df_work["hh_IsHead"] == 1)
            | (df_work["tu_hh_de_IsPartner"] == 1 if household_type == "couples" else False)
        )
    )
    households_to_drop = df_work.loc[abnormal_mask, "idhh"].unique()
    df_work = df_work[~df_work["idhh"].isin(households_to_drop)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    stats.append({
        "Step": "Wage & Labor Time",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })

    stats_df = pd.DataFrame(stats)
    return df_work, stats_df


def export_stepwise_stats_latex(stats_df, latex_path, caption, label):
    """
    Export a stepwise stats DataFrame to a LaTeX table file.
    """
    latex_table = stats_df.to_latex(index=False, caption=caption, label=label, column_format="lrrrr")
    with open(latex_path, "w") as f:
        f.write(latex_table)
    print(f"LaTeX table exported to {latex_path}")

#!/usr/bin/env python
# @Date    : 2025-10-08 15:13:40
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0

import logging
import os
from typing import Any

import numpy as np
import pandas as pd


def sum_nonhead_income(df: pd.DataFrame, income_col: str) -> pd.Series:
    """
    Sum income for non-head household members.

    Returns a Series indexed by household id (idhh) with summed income.
    """
    required_columns = {"idhh", "hh_IsHead", income_col}
    missing = required_columns - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    head_flags = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0)
    non_head_mask = head_flags != 1
    income_values = pd.to_numeric(df[income_col], errors="coerce")

    grouped = (
        income_values.where(non_head_mask)
        .groupby(df["idhh"])
        .sum(min_count=1)
    )
    return grouped


def correct_labor_status(df, emp_threshold=0):
    """
    Enforce labor status correction based on cash income, self-employment, unemployment benefit, and hours.
    Returns a DataFrame with columns: les_enforced, les_suggested, les_change_reason.
    """
    df = df.copy()
    emp_cash = df["yem"].fillna(0) > emp_threshold
    se_cash  = df["yse"].fillna(0) > 0
    hrs10    = df["lhw"].fillna(0) >= 10
    has_unemp = df.get("replacement_unemployment", pd.Series(0, index=df.index)).fillna(0) > 0

    # Enforced status
    les_enforced = np.select(
        [emp_cash, (~emp_cash) & se_cash, (~emp_cash) & (~se_cash) & has_unemp],
        [3, 2, 5],
        default=7
    ).astype(float)
    mask_flip_away = (df["les_orig"] == 3) & (~emp_cash)
    les_enforced = np.where(mask_flip_away, les_enforced, df["les_orig"])
    df["les_enforced"] = les_enforced

    # Suggested status
    is_emp_code  = pd.to_numeric(df["les_orig"], errors="coerce").eq(3)
    is_se_code   = pd.to_numeric(df["les_orig"], errors="coerce").eq(2)
    has_emp_cash = df["yem"].fillna(0) > 100
    has_se_cash  = ~np.isclose(df["yse"].fillna(0), 0, atol=1e-6)
    works_hours  = df["lhw"].fillna(0) >= 10
    les_suggested = df["les_orig"].copy()
    cond_emp_to_se = is_emp_code & has_se_cash & (~has_emp_cash) & works_hours
    cond_se_to_emp = is_se_code  & has_emp_cash & (~has_se_cash) & works_hours
    les_suggested = np.where(cond_emp_to_se, 2, les_suggested)
    les_suggested = np.where(cond_se_to_emp, 3, les_suggested)
    df["les_suggested"] = les_suggested
    reason = np.full(len(df), "", dtype=object)
    reason[cond_emp_to_se] = "SWITCH 3→2: yem<=100, yse>0, hours>=10"
    reason[cond_se_to_emp] = "SWITCH 2→3: yem>100, yse≈0, hours>=10"
    df["les_change_reason"] = reason
    return df

def compute_wage_recon(df):
    """
    Compute wage and income reconstruction columns for employees.
    Returns DataFrame with columns: w_emp_strict, yem2_strict, diff_yem_strict, w_emp_loose, yem2_loose, diff_yem_loose.
    """
    df = df.copy()
    WPM = 52 / 12
    is_emp = df["les_enforced"].eq(3)
    den = df["lhw"].replace(0, np.nan) * WPM
    w_obs      = df["yem"] / den
    work_hrs   = df["lhw"].fillna(0) >= 10
    no_selfemp = np.isclose(df["yse"].fillna(0), 0, atol=1e-6)
    use_obs = is_emp & (df["yem"] > 100) & work_hrs
    use_imp = is_emp & (df["yem"] <= 100) & work_hrs & no_selfemp
    df["w_emp_strict"] = np.select(
        [use_obs, use_imp],
        [w_obs,   df["yivwg"]],
        default=np.nan
    )
    valid_emp = use_obs | use_imp
    df["yem2_strict"] = np.where(
        valid_emp,
        df["w_emp_strict"] * df["lhw"] * WPM,
        np.nan
    )
    df["diff_yem_strict"] = np.where(
        valid_emp,
        df["yem2_strict"] - df["yem"],
        np.nan
    )
    df["w_emp_loose"]   = np.where(df["lhw"].fillna(0) >= 10, df["yivwg"], np.nan)
    df["yem2_loose"]    = df["w_emp_loose"] * df["lhw"] * WPM
    df["diff_yem_loose"] = df["yem2_loose"] - df["yem"]
    return df



# Utility Functions
def find_missing_columns(main_df, target_df, target_name):
    """
    Finds columns in main_df but not in target_df.
    """
    missing_columns = set(main_df.columns) - set(target_df.columns)
    print(f"Columns in df but not in {target_name}: {missing_columns}")
    return missing_columns


def retrieve_and_add_missing_columns(main_df, target_df, missing_columns, target_name):
    """
    Retrieves and adds missing columns to target_df based on 'idperson'.
    """
    if "idperson" not in target_df.columns:
        print(f"'idperson' column is missing in {target_name}. Skipping.")
        return target_df

    columns_to_add = ["idperson"] + list(missing_columns)
    missing_data = main_df[columns_to_add]
    updated_df = target_df.merge(missing_data, on="idperson", how="left")
    print(f"Added missing columns to {target_name}.")
    return updated_df


def filter_columns(main_df, target_df, target_name, specific_columns):
    """
    Filters columns in target_df to retain only those in main_df and specific_columns.
    """
    columns_to_keep = (
        set(main_df.columns).intersection(target_df.columns).union(specific_columns)
    )
    filtered_df = target_df[
        [col for col in columns_to_keep if col in target_df.columns]
    ]
    print(f"Columns retained in {target_name}: {filtered_df.columns.tolist()}")
    return filtered_df


def match_column_types(main_df, target_df):
    """
    Matches column types in target_df to those in main_df.
    """
    for col in main_df.columns:
        if col in target_df.columns:
            target_df[col] = target_df[col].astype(main_df[col].dtype)
    return target_df


def sort_and_rename_columns(main_df, filtered_df, specific_columns):
    """
    Sorts columns in filtered_df to match main_df and renames specific columns.
    """
    sorted_columns = [col for col in main_df.columns if col in filtered_df.columns]
    specific_columns_in_filtered = [
        col for col in specific_columns if col in filtered_df.columns
    ]
    sorted_columns += specific_columns_in_filtered
    renamed_columns = {
        col: col.replace("tu_", "sim_") for col in specific_columns_in_filtered
    }
    return filtered_df[sorted_columns].rename(columns=renamed_columns)


# Filtering Functions
def filter_households(df_sim, conditions, drop_extra_members=True):
    """
    Filters households based on specified conditions and optionally drops extra members.
    """
    filtered_df = df_sim.query(conditions)
    if drop_extra_members:
        extra_members_condition = (
            (filtered_df["hh_IsHead"] == 0)
            & (filtered_df["tu_hh_de_IsPartner"] == 0)
            & (filtered_df["dag"] > 16)
            & (filtered_df["dag"] < 64)
            & (filtered_df["ddi"] == 0)
            & (filtered_df["les"].isin([3, 5, 7]))
            & (filtered_df["dec"] == 0)
        )
        households_to_drop = filtered_df.loc[extra_members_condition, "idhh"].unique()
        filtered_df = filtered_df[~filtered_df["idhh"].isin(households_to_drop)]
    return filtered_df


def filter_couples(df_sim, results_dir):
    """
    Filters couples based on specific conditions and saves the result to a CSV file.
    """
    df_sim["hh_IsHead"] = (df_sim["tu_hh_de_headid"] == df_sim["idperson"]).astype(int)
    couples_conditions = "(hh_IsHead == 1 and dag >= 16 and dag <= 64 and ddi == 0 and dec == 0 and les in [3, 5, 7])"
    couples_df = filter_households(df_sim, couples_conditions)
    output_path = os.path.join(results_dir, "couples_sample.csv")
    couples_df.to_csv(output_path, index=False)
    print(f"Couples sample saved to {output_path}")
    return couples_df


# Create a helper to compute head counts for households
def get_head_counts(df):
    heads = df[df["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique()
    male = heads[heads["dgn"] == 1]["idhh"].nunique()
    return total, female, male


def filter_singles(df_sim):
    """
    Filters singles based on specific conditions.
    """
    singles_conditions = "(hh_IsHead == 1 and dag >= 16 and dag <= 64 and ddi == 0 and dec == 0 and les in [3, 5, 7])"
    return filter_households(df_sim, singles_conditions)


def filter_by_gender(df_singles, gender):
    """
    Filters singles by gender (0 for female, 1 for male).
    """
    gender_condition = f"(hh_IsHead == 1 and dgn == {gender})"
    gender_households = df_singles.query(gender_condition)["idhh"].unique()
    return df_singles[df_singles["idhh"].isin(gender_households)]


# Job Assignment Functions using wage_bin and lhw_interval (for workers only)


def assign_job_variable(df, new_var, key_cols):
    """
    Assign a job-related code using the same factorization scheme as jobs_2
    """
    df = df.copy()
    df[new_var] = "N"

    # eligibility
    elig = (
        df["dag"].between(16, 65)
        & (df["dec"] == 0)
        & df["les"].isin([3, 5, 7])
    )

    # unemployed
    mask_un = elig & (df["lhw_interval"] == 1) & (df["les"] == 5)
    df.loc[mask_un, new_var] = "j_un"

    # inactive by choice
    mask_j0 = elig & (df["lhw_interval"] == 1) & (df["les"] == 7)
    df.loc[mask_j0, new_var] = "j_0"

    # true workers to cluster
    mask_work = (
        elig
        & df["lhw_interval"].notna() & (df["lhw_interval"] > 1)
        & df["wage_bin"].notna()     & (df["wage_bin"] > 1)
        & (df["les"] == 3)
    )

    if mask_work.any():
        # Create the combination string
        combo_str = df.loc[mask_work, key_cols].astype(str).agg("_".join, axis=1)
        
        # Factorize into j_1, j_2, etc.
        codes, uniques = pd.factorize(combo_str)
        df.loc[mask_work, new_var] = "j_" + (codes + 1).astype(str)

    return df


def assign_job_variables(df):
    """
    Creates four parallel job codes:
      - job     by [wage_bin, lhw_interval]
      - jobloc  by [wage_bin, lhw_interval, loc]
      - joblind by [wage_bin, lhw_interval, lindi]
      - jobtot  by [wage_bin, lhw_interval, loc, lindi]
    """
    df = assign_job_variable(df, "job",    ["wage_bin", "lhw_interval"])
    df = assign_job_variable(df, "jobloc", ["wage_bin", "lhw_interval", "loc"])
    df = assign_job_variable(df, "joblind",["wage_bin", "lhw_interval", "lindi"])
    df = assign_job_variable(df, "jobtot", ["wage_bin", "lhw_interval", "loc", "lindi"])
    return df



def create_income_columns(df):
    """
    Add columns aggregating replacement income and total income to the DataFrame.

    This function creates new columns for various types of replacement income
    and overall income aggregates. The new columns are added directly to the DataFrame.

    Replacement Income Categories:
        1. replacement_unemployment : Sum of unemployment benefits.
        2. replacement_disability   : Sum of disability benefits.
        3. replacement_old_age      : Sum of old-age / retirement benefits.
        4. replacement_survivors    : Sum of survivors' benefits.
        5. replacement_private_pension : Private pension income.
        6. replacement_severance    : Severance pay.
        7. replacement_family_leave : Sum of maternity and parental leave benefits.
        8. replacement_income_total : Total replacement income (sum of 1-7).

    Overall Income Categories:
        1. income_employment        : Employment income.
        2. income_self_employment   : Self-employment income.
        3. income_fringe            : Sum of fringe benefits.
        4. income_investment        : Investment income.
        5. income_property          : Property income.
        6. income_private_transfers : Sum of private transfers.
        7. income_other             : Other income.
        8. income_total_non_replacement : Sum of the above non-replacement incomes.
        9. income_total_overall     : Grand total (replacement and non-replacement income).

    Parameters:
        df (pd.DataFrame): The input DataFrame that contains the raw income columns.

    Returns:
        pd.DataFrame: The DataFrame with new income aggregate columns added.
    """

    # ---------------------------
    # REPLACEMENT INCOME AGGREGATES
    # ---------------------------

    # 1. Unemployment Benefits
    unemployment_vars = ["bun", "bunct", "bunnc", "buntr", "bunot", "bunls"]
    df["replacement_unemployment"] = df[unemployment_vars].sum(axis=1)

    # 2. Disability Benefits
    disability_vars = ["pdi", "pdi00", "pdica", "pdiss", "pdiwr", "pdiot"]
    df["replacement_disability"] = df[disability_vars].sum(axis=1)

    # 3. Old Age / Retirement Benefits (including early retirement)
    old_age_vars = [
        "poa",
        "poa00",
        "poaab",
        "poacs",
        "poadi",
        "poaps",
        "poapu",
        "poass",
        "poawr",
        "byr",
    ]
    df["replacement_old_age"] = df[old_age_vars].sum(axis=1)

    # 4. Survivors' Benefits
    survivors_vars = ["psu", "psuor", "psuwd"]
    df["replacement_survivors"] = df[survivors_vars].sum(axis=1)

    # 5. Private Pensions
    df["replacement_private_pension"] = df["ypp"]

    # 6. Severance Pay
    df["replacement_severance"] = df["ysv"]

    # 7. Family Leave Benefits (maternity/parental-leave)
    family_leave_vars = ["bmact", "bplct"]
    df["replacement_family_leave"] = df[family_leave_vars].sum(axis=1)

    # Total Replacement Income Aggregate
    replacement_income_vars = [
        "replacement_unemployment",
        "replacement_disability",
        "replacement_old_age",
        "replacement_survivors",
        "replacement_private_pension",
        "replacement_severance",
        "replacement_family_leave",
    ]
    df["replacement_income_total"] = df[replacement_income_vars].sum(axis=1)

    # ---------------------------
    # TOTAL (ALL TYPES OF) INCOME AGGREGATES
    # ---------------------------

    # Employment Income
    df["income_employment"] = df["yem"]

    # Self-Employment Income
    df["income_self_employment"] = df["yse"]

    # Fringe Benefits
    fringe_vars = ["kfb", "kfbcc"]
    df["income_fringe"] = df[fringe_vars].sum(axis=1)

    # Investment Income
    df["income_investment"] = df["yiy"]

    # Property Income
    df["income_property"] = df["ypr"]

    # Private Transfers
    transfers_vars = ["ypt", "yptmp"]
    df["income_private_transfers"] = df[transfers_vars].sum(axis=1)

    # Other Income
    df["income_other"] = df["yot"]

    # Total Non-Replacement Income Aggregate
    non_replacement_income_vars = [
        "income_employment",
        "income_self_employment",
        "income_fringe",
        "income_investment",
        "income_property",
        "income_private_transfers",
        "income_other",
    ]
    df["income_total_non_replacement"] = df[non_replacement_income_vars].sum(axis=1)

    # Overall Total Income Aggregate (replacement + non-replacement)
    df["income_total_overall"] = (
        df["replacement_income_total"] + df["income_total_non_replacement"]
    )

    return df



def assign_jobs_2(df, threshold=5):
    """
    Assigns job categories with progressive collapsing to ensure minimum frequency.
    Each job code will have at least `threshold` observations unless it's at the most basic level.
    Uses hierarchy: jobtot â†’ jobloc â†’ job (removing joblind from hierarchy).

    Returns df with columns:
      - job, jobloc, joblind, jobtot, jobs_2
      - jobs_2_key: the raw combo string behind the final jobs_2 code (e.g. "12_3_2_5")
    """
    df = df.copy()

    # 0ï¸âƒ£ Initialize all columns
    for col in ("job", "jobloc", "joblind", "jobtot", "jobs_2", "jobs_2_key"):
        df[col] = "N"

    # 1ï¸âƒ£ Handle special cases: Unemployed and Inactive
    elig = (
        df["dag"].between(16, 65) &
        (df["dec"] == 0) &
        df["les"].isin([3, 5, 7])
    )

    # Unemployed
    m_un = elig & (df["lhw_interval"] == 1) & (df["les"] == 5)
    for col in ("job", "jobloc", "joblind", "jobtot", "jobs_2"):
        df.loc[m_un, col] = "j_un"
    df.loc[m_un, "jobs_2_key"] = df.loc[m_un, "job"]  # mark key

    # Inactive by choice
    m_0 = elig & (df["lhw_interval"] == 1) & (df["les"] == 7)
    for col in ("job", "jobloc", "joblind", "jobtot", "jobs_2"):
        df.loc[m_0, col] = "j_0"
    df.loc[m_0, "jobs_2_key"] = df.loc[m_0, "job"]  # mark key

    # 2ï¸âƒ£ Handle workers
    m_work = elig & (df["lhw_interval"] > 1) & (df["les"] == 3)

    if m_work.any():
        # work on copy
        workers = df.loc[m_work].copy()

        # raw combos
        workers["_raw_job"] = workers[["wage_bin", "lhw_interval"]].astype(str).agg("_".join, axis=1)
        workers["_raw_jobloc"] = workers[["wage_bin", "lhw_interval", "loc"]].astype(str).agg("_".join, axis=1)
        workers["_raw_joblind"] = workers[["wage_bin", "lhw_interval", "lindi"]].astype(str).agg("_".join, axis=1)
        workers["_raw_jobtot"] = workers[["wage_bin", "lhw_interval", "loc", "lindi"]].astype(str).agg("_".join, axis=1)

        # start collapse
        workers["current_level"] = "jobtot"
        workers["current_key"]   = workers["_raw_jobtot"]

        level_hierarchy = ["jobtot", "jobloc", "job"]

        for i in range(len(level_hierarchy) - 1):
            nxt = level_hierarchy[i + 1]
            counts = workers["current_key"].value_counts()
            small = counts[counts < threshold].index
            mask = workers["current_key"].isin(small)
            if mask.any():
                workers.loc[mask, "current_level"] = nxt
                workers.loc[mask, "current_key"]   = workers.loc[mask, f"_raw_{nxt}"]

        # factorize each job type
        for jt in ["job", "jobloc", "joblind", "jobtot"]:
            raws = workers[f"_raw_{jt}"].unique()
            mapping = {v: f"j_{i+1}" for i, v in enumerate(raws)}
            workers[jt] = workers[f"_raw_{jt}"].map(mapping)

        # build jobs_2 from collapsed key
        workers["jobs_2"] = "N"
        for level in level_hierarchy:
            lvl_mask = workers["current_level"] == level
            if lvl_mask.any():
                raws = workers.loc[lvl_mask, f"_raw_{level}"].unique()
                map2 = {v: f"j_{i+1}" for i, v in enumerate(raws)}
                workers.loc[lvl_mask, "jobs_2"] = workers.loc[lvl_mask, f"_raw_{level}"].map(map2)

        # record the raw key used
        workers["jobs_2_key"] = workers["current_key"]

        # write back to df
        for col in ["job", "jobloc", "joblind", "jobtot", "jobs_2", "jobs_2_key"]:
            df.loc[m_work, col] = workers[col].values

    return df

def assigning_jobs(df):
    """
    Creates two job variables without collapsing:
      - job: based on [wage_bin, lhw_interval]
      - jobloc: based on [wage_bin, lhw_interval, loc]
    
    Special cases for unemployed (j_un) and inactive (j_0) are handled 
    the same way as in assign_jobs_2().
    
    Parameters:
        df (DataFrame): Input DataFrame with wage_bin and lhw_interval columns
        
    Returns:
        DataFrame: Copy of input with job and jobloc columns added
    """
    df = df.copy()
    
    # Initialize columns
    for col in ("job", "jobloc"):
        df[col] = "N"
    
    # Define eligibility
    elig = (
        df["dag"].between(16, 65) &
        (df["dec"] == 0) &
        df["les"].isin([3, 5, 7])
    )
    
    # Special case 1: Unemployed
    mask_un = elig & (df["lhw_interval"] == 1) & (df["les"] == 5)
    df.loc[mask_un, "job"] = "j_un"
    df.loc[mask_un, "jobloc"] = "j_un"
    
    # Special case 2: Inactive by choice
    mask_j0 = elig & (df["lhw_interval"] == 1) & (df["les"] == 7)
    df.loc[mask_j0, "job"] = "j_0"
    df.loc[mask_j0, "jobloc"] = "j_0"
    
    # Working individuals
    mask_work = (
        elig
        & df["lhw_interval"].notna() & (df["lhw_interval"] > 1)
        & df["wage_bin"].notna() & (df["wage_bin"] > 1)
        & (df["les"] == 3)
    )
    
    if mask_work.any():
        # Create job variable (wage_bin + lhw_interval)
        job_combo = df.loc[mask_work, ["wage_bin", "lhw_interval"]].astype(str).agg("_".join, axis=1)
        job_codes, job_uniques = pd.factorize(job_combo)
        df.loc[mask_work, "job"] = "j_" + (job_codes + 1).astype(str)
        
        # Create jobloc variable (wage_bin + lhw_interval + loc)
        jobloc_combo = df.loc[mask_work, ["wage_bin", "lhw_interval", "loc"]].astype(str).agg("_".join, axis=1)
        jobloc_codes, jobloc_uniques = pd.factorize(jobloc_combo)
        df.loc[mask_work, "jobloc"] = "j_" + (jobloc_codes + 1).astype(str)
    
    return df


# Helper functions
def reduce_memory_usage(df):
    """Reduce memory usage by downcasting numeric columns."""
    for col in df.select_dtypes(include=['int64']):
        df[col] = pd.to_numeric(df[col], downcast='integer')
    for col in df.select_dtypes(include=['float64']):
        df[col] = pd.to_numeric(df[col], downcast='float')
    return df

def handle_outliers(df, wage_bounds=(2, 300), exp_bound=960):
    bad_wage = (df["wage"] < wage_bounds[0]) | (df["wage"] > wage_bounds[1])
    bad_exp = df["liwwh"].notna() & df["liwwh"].gt(exp_bound)
    return df.loc[~(bad_wage | bad_exp)].copy()


# Add this function to myfunctions.py

def display_value_counts(df, columns):
    """
    Displays value counts and frequencies for specified columns in a DataFrame.
    
    Parameters:
        df (DataFrame): Input DataFrame
        columns (list): List of column names to analyze
    
    Returns:
        None: Results are printed to console
    """
    for col in columns:
        counts = df[col].value_counts()
        print(f"\nCounts of {col} values:")
        print(counts)
        frequencies = counts.value_counts()
        print(f"\nFrequencies of {col} values:")
        print(frequencies)


# Add this function to myfunctions.py

def preprocess_data(df, tgt, threshold=5):
    """
    Preprocesses data by collapsing categories, handling outliers, and creating features.
    
    Parameters:
        df (DataFrame): Input DataFrame
        tgt (str): Target column name
        threshold (int): Minimum frequency threshold for categories
    
    Returns:
        DataFrame: Preprocessed DataFrame
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("Processing job categoriesâ€¦")
    df = df.copy()
    df["job_dec"] = df[tgt].fillna("N")
    counts = df["job_dec"].value_counts()
    small = counts[counts < threshold].index
    df["job_dec"] = df["job_dec"].apply(lambda j: "j_other" if j in small else j)

    # Handle outliers
    df = handle_outliers(df)

    # Create features
    df["dag2"] = df["dag"] ** 2
    df["exp_years"] = df["liwwh"] / 12
    df["exp_years2"] = df["exp_years"] ** 2
    df["log_wage"] = np.log1p(df["wage"])

    return df


# Add this function to myfunctions.py

def analyze_ability_sets(df_ml, probs_all, lb, tau_star=0.1):
    """
    Analyzes ability sets and computes metrics based on probability thresholds.
    """
    import numpy as np
    
    df_ml = df_ml.copy()
    
    # Initial sets
    df_ml["ability_idx"] = [list(np.where(row >= tau_star)[0]) for row in probs_all]

    # Ensure "N" is not included in ability sets
    n_idx = np.where(lb.classes_ == "N")[0][0] if "N" in lb.classes_ else None
    if n_idx is not None:
        df_ml["ability_idx"] = [
            [idx for idx in idxs if idx != n_idx] 
            for idxs in df_ml["ability_idx"]
        ]

    # Enforce j_0 and true label
    j0_idx = np.where(lb.classes_ == "j_0")[0][0] if "j_0" in lb.classes_ else None
    true_job_indices = [
        (np.where(lb.classes_ == job)[0][0] if job in lb.classes_ else 0)
        for job in df_ml["job_dec"]
    ]
    if j0_idx is not None:
        df_ml["ability_idx"] = [
            sorted(set(idxs) | {j0_idx, true_idx})
            for idxs, true_idx in zip(df_ml["ability_idx"], true_job_indices)
        ]
    else:
        df_ml["ability_idx"] = [
            sorted(set(idxs) | {true_idx})
            for idxs, true_idx in zip(df_ml["ability_idx"], true_job_indices)
        ]

    # Map to names & sizes
    df_ml["ability_jobs"] = [lb.classes_[idxs].tolist() for idxs in df_ml["ability_idx"]]
    df_ml["ability_size"] = df_ml["ability_jobs"].apply(len)

    return df_ml




def ref_scores(idx, job_list, probs_all, lb_classes):

    """
    Return probability scores for all jobs in the job_list if they exist in model classes.
    
    Parameters:
        idx (int): Index of the individual
        job_list (list): List of job codes
        probs_all (array): Probability array from model prediction
        lb_classes (array): Classes from the label binarizer
    
    Returns:
        dict: Dictionary mapping job codes to probability scores
    """
    import numpy as np
    
    scores = {}
    for j in job_list:
        # Check if job exists in model classes
        matches = np.where(lb_classes == j)[0]
        if len(matches) > 0:
            # Job exists in model, get its probability
            scores[j] = float(probs_all[idx, matches[0]])
        else:
            # Job not in model classes, assign a small default probability
            scores[j] = 0.001
    return scores


# =============================================================================
# ENHANCED DATA PREPARATION FUNCTIONS
# =============================================================================

def create_stats_entry(step: str, desc: str, total: int, female: int, male: int, initial: int) -> dict[str, Any]:
    """Standardized stats entry creation."""
    return {
        "Step": step,
        "Description": desc,
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial, 2) if initial > 0 else 0.0
    }


def validate_required_columns(df: pd.DataFrame, required_cols: list[str]) -> None:
    """Ensure essential columns exist before processing."""
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_household_integrity(df: pd.DataFrame) -> bool:
    """Ensure each household has exactly one head."""
    logger = logging.getLogger(__name__)
    head_counts = df.groupby("idhh")["hh_IsHead"].sum()
    invalid_households = head_counts[head_counts != 1]
    
    if len(invalid_households) > 0:
        logger.warning(f"Found {len(invalid_households)} households with != 1 head")
        return False
    return True


def check_data_quality(df: pd.DataFrame) -> list[str]:
    """Comprehensive data quality checks."""
    issues = []
    
    # Check for negative wages/hours
    if (df["yem"] < 0).any():
        issues.append("Negative employment income found")
    
    # Check for extreme values
    if (df["dag"] > 100).any() or (df["dag"] < 0).any():
        issues.append("Unrealistic ages found") 
        
    return issues


def log_filtering_step(step_name: str, before_count: int, after_count: int) -> None:
    """Log filtering step results."""
    logger = logging.getLogger(__name__)
    dropped = before_count - after_count
    if before_count > 0:
        percentage = dropped/before_count*100
        logger.info(f"{step_name}: {before_count:,} â†’ {after_count:,} households (-{dropped:,}, -{percentage:.1f}%)")
    else:
        logger.info(f"{step_name}: {before_count:,} â†’ {after_count:,} households")


def apply_single_filter(df: pd.DataFrame, role_column: str, condition: str, role_name: str) -> pd.DataFrame:
    """Apply a single filter condition to a dataframe based on role."""
    eligible_households = df[df[role_column] == 1].query(condition)["idhh"].unique()
    return df[df["idhh"].isin(eligible_households)]


def apply_filtering_pipeline(df: pd.DataFrame, 
                           role_filters: list[tuple[str, str]], 
                           household_type: str = "couples", 
                           initial_count: int | None = None,
                           config: dict | None = None) -> tuple[pd.DataFrame, list[dict]]:
    """
    Generic filtering pipeline for any role (head/partner).
    
    Args:
        df: Input dataframe
        role_filters: List of (role_column, role_name) tuples
        household_type: Type of households being processed
        initial_count: Initial household count for percentage calculation
        config: Configuration dictionary with filtering parameters
    
    Returns:
        Tuple of (filtered_dataframe, stats_list)
    """
    if config is None:
        config = {
            "age_range": (16, 65),
            "replacement_income_cap": 100,
            "allowed_les": [3, 5, 7]
        }
    
    if initial_count is None:
        initial_count = df["idhh"].nunique()
    
    age_min, age_max = config["age_range"]
    replacement_cap = config["replacement_income_cap"]
    allowed_les = config["allowed_les"]
    
    # Define filtering steps
    filters = [
        ("Age", f"{age_min} <= dag <= {age_max}"),
        ("Education", "dec == 0"), 
        ("Replacement Income", f"replacement_income_total <= {replacement_cap}"),
        ("Les Exclusion", "les != 5"),
        ("Les Inclusion", f"les in {allowed_les}")
    ]
    
    stats = []
    current_df = df.copy()
    
    for role_column, role_name in role_filters:
        for step_name, condition in filters:
            step_label = f"{step_name} ({role_name})"
            before_count = current_df["idhh"].nunique()
            
            current_df = apply_single_filter(current_df, role_column, condition, role_name)
            
            total, female, male = get_head_counts(current_df)
            stats.append(create_stats_entry(
                step_label, 
                f"Keep households where {role_name.lower()}'s {condition}", 
                total, female, male, initial_count
            ))
            
            after_count = current_df["idhh"].nunique()
            log_filtering_step(step_label, before_count, after_count)
    
    return current_df, stats


def apply_other_members_filter(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    """Apply filter for other household members (non-head/non-partner)."""
    if config is None:
        config = {"age_range": (16, 65)}
    
    age_min, age_max = config["age_range"]
    
    condition = (
        (df["hh_IsHead"] == 0)
        & (df["tu_hh_de_IsPartner"] == 0)
        & (
            (
                (df["dag"] >= age_min)
                & (df["dag"] <= age_max)
                & (df["ddi"] == 0)
                & (df["dec"] == 0)
            )
            | ((df["yem"] > 50) | (df["yse"] != 0))
        )
    )
    
    households_to_drop = df.loc[condition, "idhh"].unique() # type: ignore
    return df[~df["idhh"].isin(households_to_drop)]


def apply_abnormal_filter(df: pd.DataFrame, households_to_remove: np.ndarray, config: dict | None = None) -> pd.DataFrame:
    """Apply abnormal wage and labor time filter."""
    if config is None:
        config = {
            "wage_bounds": (2, 170),
            "hour_bounds": (5, 79)
        }
    
    wage_min, wage_max = config["wage_bounds"]
    hour_min, hour_max = config["hour_bounds"]
    
    condition_remove = (
        (df["les"] == 3)
        & (
            (df["lhw"] < hour_min)
            | (df["lhw"] > hour_max)
            | (df["yivwg"] < wage_min)
            | (df["yivwg"] > wage_max)
        )
        & ((df["hh_IsHead"] == 1) | (df["tu_hh_de_IsPartner"] == 1))
    )
    
    households_to_drop_abnormal = df.loc[condition_remove, "idhh"].unique() # type: ignore
    all_households_to_drop = np.union1d(households_to_drop_abnormal, households_to_remove)
    
    return df[~df["idhh"].isin(all_households_to_drop)]


def _write_dataframe(df: pd.DataFrame, base_path, export_format: str = "parquet"):
    """Write a DataFrame in the requested format with sensible fallbacks.

    export_format: one of {"parquet", "feather", "pickle", "csv"}
    Returns the full path used.
    """
    fmt = (export_format or "parquet").lower()
    if fmt == "parquet":
        try:
            path = base_path.with_suffix(".parquet")
            df.to_parquet(path, engine="pyarrow", compression="snappy")  # type: ignore[arg-type]
            return path
        except Exception:
            fmt = "pickle"
    if fmt == "feather":
        try:
            path = base_path.with_suffix(".feather")
            df.to_feather(path)  # type: ignore[arg-type]
            return path
        except Exception:
            fmt = "pickle"
    if fmt == "pickle":
        path = base_path.with_suffix(".pkl")
        df.to_pickle(path)
        return path
    path = base_path.with_suffix(".csv")
    df.to_csv(path, index=False)
    return path


def export_household_data(df: pd.DataFrame,
                         stats_df: pd.DataFrame,
                         output_prefix: str,
                         output_dir,
                         processed_dir,
                         export_format: str = "parquet") -> dict[str, Any]:
    """
    Unified export function for any household type, with efficient data format.

    Args:
        df: Dataframe to export
        stats_df: Statistics dataframe
        output_prefix: Prefix for output files
        output_dir: Directory for outputs (stats and LaTeX)
        processed_dir: Directory for processed data
        export_format: parquet (default), feather, pickle, or csv

    Returns:
        Dictionary with paths to exported files
    """
    # Data export (efficient format)
    data_base = processed_dir / f"{output_prefix}_final"
    data_path = _write_dataframe(df, data_base, export_format)
    
    # Stats CSV (small, human-readable) and LaTeX
    stats_path = output_dir / f"{output_prefix}_filtering_summary.csv"
    stats_df.to_csv(stats_path, index=False)
    
    latex_path = output_dir / f"{output_prefix}_summary.tex"
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(stats_df.to_latex(index=False))
    
    return {
        "data_path": data_path,
        "stats_path": stats_path,
        "latex_path": latex_path
    }


def export_gender_split_data(df: pd.DataFrame, 
                           output_prefix: str, 
                           processed_dir,
                           export_pickle: bool = False,
                           export_format: str = "parquet") -> dict[str, dict]:
    """
    Export gender-split datasets using efficient format.

    Households are assigned to a gender group based on the head's `dgn` value.
    All members belonging to those households are retained in the export.
    
    Args:
        df: Input dataframe containing at least `idhh`, `hh_IsHead`, and `dgn`
        output_prefix: Prefix for output files
        processed_dir: Directory for processed data
        export_pickle: Deprecated; kept for backwards compatibility
        export_format: parquet (default), feather, pickle, or csv
    
    Returns:
        Dictionary with export paths and data for each gender
    """
    required_cols = {"idhh", "hh_IsHead", "dgn"}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns for gender export: {sorted(missing)}")
    
    heads = df[df["hh_IsHead"] == 1][["idhh", "dgn"]].copy()
    heads["dgn"] = pd.to_numeric(heads["dgn"], errors="coerce")
    heads = heads.dropna(subset=["dgn"]).drop_duplicates(subset="idhh")
    
    female_households = heads.loc[heads["dgn"] == 0, "idhh"]
    male_households = heads.loc[heads["dgn"] == 1, "idhh"]
    
    results: dict[str, dict] = {}
    
    for gender, household_ids, gender_name in [
        ("female", female_households, "female"),
        ("male", male_households, "male"),
    ]:
        household_ids = household_ids.astype(df["idhh"].dtype, copy=False)
        gender_df = df[df["idhh"].isin(household_ids)]
        rows = int(gender_df.shape[0])
        households = int(gender_df["idhh"].nunique())
        head_rows = int(gender_df["hh_IsHead"].eq(1).sum())
        base = processed_dir / f"{output_prefix}_{gender_name}"
        fmt = "pickle" if export_pickle else export_format
        data_path = _write_dataframe(gender_df, base, fmt) if rows else None
        results[gender] = {
            "data_path": data_path,
            "rows": rows,
            "households": households,
            "head_rows": head_rows,
        }
    
    return results


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def cleanup_intermediate_vars(var_names: list[str]) -> None:
    """Clean up large intermediate variables."""
    import gc
    frame = globals()
    for var in var_names:
        if var in frame:
            del frame[var]
    gc.collect()


def identify_extreme_households(df: pd.DataFrame, config: dict | None = None) -> np.ndarray:
    """Identify households with extreme wage differences."""
    if config is None:
        config = {"extreme_wage_diff": 500}

    threshold = config["extreme_wage_diff"]
    diff_col_candidates = (
        config.get("extreme_diff_column"),
        "diff_yem_strict",
        "diff_yem",
        "diff_yem_loose",
    )

    diff_col = None
    for candidate in diff_col_candidates:
        if candidate and candidate in df.columns:
            diff_col = candidate
            break

    if diff_col is None:
        raise KeyError(
            "No wage difference column found. Expected one of: "
            f"{[c for c in diff_col_candidates if c is not None]}"
        )

    extreme_positive = df[df[diff_col] >= threshold]
    return extreme_positive["idhh"].unique()


def process_couples_data(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and process couples data."""
    # Create subset with partners
    df_couples = df[
        df["idhh"].isin(
            df[df["tu_hh_de_IsPartner"] == 1]["idhh"].unique()
        )
    ]
    
    # Filter for opposite-sex couples only
    same_sex_households = df_couples[
        (df_couples["tu_hh_de_IsPartner"] == 1) & (df_couples["hh_IsHead"] == 0)
    ].merge(
        df_couples[
            (df_couples["tu_hh_de_IsPartner"] == 0) & (df_couples["hh_IsHead"] == 1)
        ],
        on="idhh",
        suffixes=("_1", "_0"),
    ).query("dgn_1 == dgn_0")["idhh"]
    
    return df_couples[~df_couples["idhh"].isin(same_sex_households)]


def process_singles_data(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and process singles data."""
    return df.groupby("idhh").filter(
        lambda group: (group["tu_hh_de_IsPartner"] == 0).all()
    )









