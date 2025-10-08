#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-10-08 15:13:40
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0

import pandas as pd
import os
import numpy as np


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
    Uses hierarchy: jobtot → jobloc → job (removing joblind from hierarchy).

    Returns df with columns:
      - job, jobloc, joblind, jobtot, jobs_2
      - jobs_2_key: the raw combo string behind the final jobs_2 code (e.g. "12_3_2_5")
    """
    df = df.copy()

    # 0️⃣ Initialize all columns
    for col in ("job", "jobloc", "joblind", "jobtot", "jobs_2", "jobs_2_key"):
        df[col] = "N"

    # 1️⃣ Handle special cases: Unemployed and Inactive
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

    # 2️⃣ Handle workers
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
            cur = level_hierarchy[i]
            nxt = level_hierarchy[i+1]
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
    
    logger.info("Processing job categories…")
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

def analyze_ability_sets(df_ml, probs_all, lb, τ_star=0.1):
    """
    Analyzes ability sets and computes metrics based on probability thresholds.
    """
    import numpy as np
    
    df_ml = df_ml.copy()
    
    # Initial sets
    df_ml["ability_idx"] = [list(np.where(row >= τ_star)[0]) for row in probs_all]

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


