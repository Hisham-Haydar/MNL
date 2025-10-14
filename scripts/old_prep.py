#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-04-02 10:11:29
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

# %% Libraries
import os
import sys
import time
import pandas as pd
import pickle
import euromod as em
from scratch.my_functions import *
import numpy as np

# %% Direcrtries and Data import
# Get the directory where this script (dataprep.py) is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one directory (from src to the project root)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
# Construct the path to the 'data', 'model', and 'results' folders
data_dir = os.path.join(project_root, "data")
model_dir = os.path.join(project_root, "model")
results_dir = os.path.join(project_root, "results")
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
# %% Data import and 1st simulation to create heads and household partners
data_file = os.path.join(data_dir, "DE_2021_b1.txt")
df = pd.read_csv(data_file, sep="\t")
model_path = os.path.join(model_dir, "EUROMOD_RELEASES_J1.0+")
mod = em.Model(model_path)
dataset = mod.countries[5].systems[14].bestmatch_datasets[0]
sim = mod["DE"]["DE_2021"].run(df, dataset.name)
df_sim = sim.outputs[0]
df_sim.info("memory_usage")
df.info("memory_usage") # type: ignore


# %%Head of Households
# Add column 'hh_IsHead' based on condition
df_sim["hh_IsHead"] = (df_sim["tu_hh_de_HeadID"] == df_sim["idperson"]).astype(int)

# Check if each household has one head
is_single_head = df_sim.groupby("idhh")["hh_IsHead"].sum().eq(1)

# Filter households with more than one head
multiple_heads = df_sim[~df_sim["idhh"].isin(is_single_head[is_single_head].index)]
print(f"Number of households with a single head: {is_single_head.sum()}")
# Print the number of households with multiple heads
print(f"Number of households with multiple heads: {multiple_heads['idhh'].nunique()}")
# Print the number of unique households in the dataset
print(f"Number of unique households in the dataset: {df_sim['idhh'].nunique()}")
# %%Income variables creation
print(
    f"the columns and info before createion of aggregatres{df_sim.info('memory_usage')}"
)
# %% adding the income variables
df_sim1 = create_income_columns(df_sim)
print(
    f"the columns and info After createion of aggregatres{df_sim1.info('memory_usage')}"
)

# %% Column Filtration recreate the input

# --- Step 1: Define boundaries and extract required_columns from df_sim1 ---
# Remove extra spaces from the boundary strings
start_var = "tu_family2_de_HeadID"  # no extra spaces
end_var = "income_total_overall"

# Get df_sim1 column names (stripping any extra whitespace)
sim1_cols = [col.strip() for col in df_sim1.columns.tolist()]

# Try to locate the start and end positions in df_sim1's columns
try:
    start_index = sim1_cols.index(start_var)
    end_index = sim1_cols.index(end_var)
except ValueError as err:
    raise ValueError("One or both boundary columns were not found in df_sim1.") from err

# The required columns (to be preserved from df_sim1)
required_columns = sim1_cols[start_index : end_index + 1]
print("Required columns in df_sim1 to keep:", required_columns)
# %%
# --- Step 2: Determine which columns to bring from df ---
# We want to replace in df_sim1 every column that exists in df.
# (The observation identifier 'idperson' must exist in both.)
if "idperson" not in df.columns or "idperson" not in df_sim1.columns:
    raise ValueError("idperson is not present in both DataFrames!")

# We'll now create a new DataFrame that takes:
# (a) all columns from df (i.e. the standard values), and
# (b) the required columns from df_sim1.

# --- Step 3: Merge into a new version of df_sim1 ---
final_df_sim1 = df.merge(
    df_sim1[["idperson"] + required_columns],  # required extra columns from df_sim1
    on="idperson",
    how="left",
)

print(
    f"the columns and info After createion of aggregatres{final_df_sim1.info('memory_usage')}" # pyright: ignore[reportArgumentType]
)
final_df_sim1.describe(include="all")
# %%LES correction

# Update les: if yem==0, yse!=0 and les==3 then set les to 2, else keep original value
final_df_sim1["les"] = np.where(
    (final_df_sim1["yem"] == 0)
    & (final_df_sim1["yse"] != 0)
    & (final_df_sim1["les"] == 3),
    2,
    final_df_sim1["les"],
)

# Verify the changes
print(
    final_df_sim1.loc[
        (final_df_sim1["yem"] == 0)
        & (final_df_sim1["yse"] != 0)
        & (final_df_sim1["les"] == 2),
        ["yem", "yse", "les"],
    ].head()
)

# %%Wage
# Create the new 'wage' column using np.where:
final_df_sim1["wage"] = np.where(
    final_df_sim1["yem"] > 100,
    final_df_sim1["yem"] / (final_df_sim1["lhw"] * (52 / 12)),
    final_df_sim1["yivwg"],
)
#  print a few rows to verify the result
print(final_df_sim1[["yem", "lhw", "yivwg", "wage"]].head())

final_df_sim1["yem2"] = final_df_sim1["wage"] * final_df_sim1["lhw"] * (52 / 12)
final_df_sim1["diff_yem"] = final_df_sim1["yem2"] - final_df_sim1["yem"]

# %%
# Filter records with hh_IsHead == 1, tu_hh_de_IsPartner == 1 and diff_yem >= 50
filtered = final_df_sim1[
    (final_df_sim1["hh_IsHead"] == 1)
    | (final_df_sim1["tu_hh_de_IsPartner"] == 1) & (final_df_sim1["diff_yem"] >= 50)
]

diff_yem_ge_50 = filtered["diff_yem"]

# Print the count
print("Count of diff_yem >= 50:", diff_yem_ge_50.count())

# Print the distribution
print("Distribution of diff_yem for diff_yem >= 50:")
print(diff_yem_ge_50.describe())

# Count observations where diff_yem is greater than or equal to 500
extreme_positive = final_df_sim1[final_df_sim1["diff_yem"] >= 500]
count_extreme_positive = extreme_positive.shape[0]
print("Count of records with diff_yem >= 500:", count_extreme_positive)

# Similarly, count observations where diff_yem is less than or equal to -500
extreme_negative = final_df_sim1[final_df_sim1["diff_yem"] <= -500]
count_extreme_negative = extreme_negative.shape[0]
print("Count of records with diff_yem <= -500:", count_extreme_negative)

extreme_positive[
    ["yem", "lhw", "yivwg", "wage", "diff_yem", "les", "lindi", "loc", "lse", "yse"]
].describe()


# %%
# Identify households to remove based on extreme_positive
households_to_remove = extreme_positive["idhh"].unique()
print("Households to remove:", households_to_remove)


# %%Creation of Couples
# Create a subset of the dataset where households have at least one member with tu_hh_de_IsPartner = 1
df_couples = final_df_sim1[
    final_df_sim1["idhh"].isin(
        final_df_sim1[final_df_sim1["tu_hh_de_IsPartner"] == 1]["idhh"].unique()
    )
]

# Use df_couples as the independent dataset from now on
print(f"Number of households in couples : {df_couples['idhh'].nunique()}")
# %% Filtration - Stepwise Filtering on couple households

# -------------------------------
# Baseline: df_couples (the starting point)
# -------------------------------
stats = []
initial_households = df_couples["idhh"].nunique()
total, female, male = get_head_counts(df_couples)
stats.append(
    {
        "Step": "Baseline",
        "Description": "Initial households",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": 100.0,
    }
)
# Save baseline dataset for retrieval
baseline = df_couples.copy()

# -------------------------------
# Stepwise Head Filtering Pipeline
# -------------------------------
head_stages = {}  # dictionary to store intermediate head-filtered datasets

# Step 1: Age Filter for Heads: head's age between 16 and 65
head_age = baseline[
    baseline["idhh"].isin(
        baseline[baseline["hh_IsHead"] == 1].query("16 <= dag <= 65")["idhh"].unique()
    )
]
head_stages["Age"] = head_age.copy()
total, female, male = get_head_counts(head_age)
stats.append(
    {
        "Step": "Age Filter (Head)",
        "Description": "Keep households where head's age in [16,65]",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 2: Education Filter for Heads: head not in education (dec == 0)
head_edu = head_age[
    head_age["idhh"].isin(
        head_age[head_age["hh_IsHead"] == 1].query("dec == 0")["idhh"].unique()
    )
]
head_stages["Education"] = head_edu.copy()
total, female, male = get_head_counts(head_edu)
stats.append(
    {
        "Step": "Education Filter (Head)",
        "Description": "Keep households where head's dec == 0",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 3: Replacement Income Filter for Heads: head's replacement_income_total <= 100
head_inc = head_edu[
    head_edu["idhh"].isin(
        head_edu[head_edu["hh_IsHead"] == 1]
        .query("replacement_income_total <= 100")["idhh"]
        .unique()
    )
]
head_stages["Replacement Income"] = head_inc.copy()
total, female, male = get_head_counts(head_inc)
stats.append(
    {
        "Step": "Replacement Income Filter (Head)",
        "Description": "Keep households where head's replacement_income_total <= 100",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 4: Les Filter for Heads: remove households where head has les == 5
head_les = head_inc[
    head_inc["idhh"].isin(
        head_inc[head_inc["hh_IsHead"] == 1].query("les != 5")["idhh"].unique()
    )
]
head_stages["Les"] = head_les.copy()
total, female, male = get_head_counts(head_les)
stats.append(
    {
        "Step": "Les Filter (Head)",
        "Description": "Remove households where head has les == 5",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Additional Step for Heads: Allowed LES Filter (Head)
# Keep only households where the head's 'les' is in [3, 5, 7]
head_allowed = head_les[
    head_les["idhh"].isin(
        head_les[head_les["hh_IsHead"] == 1].query("les in [3, 5, 7]")["idhh"].unique()
    )
]
head_stages["Allowed LES"] = head_allowed.copy()
total, female, male = get_head_counts(head_allowed)
stats.append(
    {
        "Step": "Allowed LES Filter (Head)",
        "Description": "Keep households where head's les in [3,5,7]",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# -------------------------------
# Stepwise Partner Filtering Pipeline
# -------------------------------
# Continue directly on the head-filtered data (using head_allowed as baseline)
partner_stages = {}  # dictionary to store intermediate partner-filtered datasets

# Step 1: Age Filter for Partners: partner's age between 16 and 65
partner_age = head_allowed[
    head_allowed["idhh"].isin(
        head_allowed[head_allowed["tu_hh_de_IsPartner"] == 1]
        .query("16 <= dag <= 65")["idhh"]
        .unique()
    )
]
partner_stages["Age"] = partner_age.copy()
total_p, female_p, male_p = get_head_counts(partner_age)
stats.append(
    {
        "Step": "Age Filter (Partner)",
        "Description": "Keep households where at least one partner's age in [16,65]",
        "Total Households": total_p,
        "Female Heads": female_p,
        "Male Heads": male_p,
        "% Remaining": round(100 * total_p / initial_households, 2),
    }
)

# Step 2: Education Filter for Partners: partner not in education (dec == 0)
partner_edu = partner_age[
    partner_age["idhh"].isin(
        partner_age[partner_age["tu_hh_de_IsPartner"] == 1]
        .query("dec == 0")["idhh"]
        .unique()
    )
]
partner_stages["Education"] = partner_edu.copy()
total_p, female_p, male_p = get_head_counts(partner_edu)
stats.append(
    {
        "Step": "Education Filter (Partner)",
        "Description": "Keep households where partner's dec == 0",
        "Total Households": total_p,
        "Female Heads": female_p,
        "Male Heads": male_p,
        "% Remaining": round(100 * total_p / initial_households, 2),
    }
)

# Step 3: Replacement Income Filter for Partners: partner's replacement_income_total <= 100
partner_inc = partner_edu[
    partner_edu["idhh"].isin(
        partner_edu[partner_edu["tu_hh_de_IsPartner"] == 1]
        .query("replacement_income_total <= 100")["idhh"]
        .unique()
    )
]
partner_stages["Replacement Income"] = partner_inc.copy()
total_p, female_p, male_p = get_head_counts(partner_inc)
stats.append(
    {
        "Step": "Replacement Income Filter (Partner)",
        "Description": "Keep households where partner's replacement_income_total <= 100",
        "Total Households": total_p,
        "Female Heads": female_p,
        "Male Heads": male_p,
        "% Remaining": round(100 * total_p / initial_households, 2),
    }
)

# Step 4: Les Filter for Partners: remove households where partner has les == 5
partner_les = partner_inc[
    partner_inc["idhh"].isin(
        partner_inc[partner_inc["tu_hh_de_IsPartner"] == 1]
        .query("les != 5")["idhh"]
        .unique()
    )
]
partner_stages["Les"] = partner_les.copy()
total_p, female_p, male_p = get_head_counts(partner_les)
stats.append(
    {
        "Step": "Les Filter (Partner)",
        "Description": "Remove households where partner has les == 5",
        "Total Households": total_p,
        "Female Heads": female_p,
        "Male Heads": male_p,
        "% Remaining": round(100 * total_p / initial_households, 2),
    }
)

# Additional Step for Partners: Allowed LES Filter (Partner)
# Keep only households where the partner's 'les' is in [3, 5, 7]
partner_allowed = partner_les[
    partner_les["idhh"].isin(
        partner_les[partner_les["tu_hh_de_IsPartner"] == 1]
        .query("les in [3, 5, 7]")["idhh"]
        .unique()
    )
]
partner_stages["Allowed LES"] = partner_allowed.copy()
total_p, female_p, male_p = get_head_counts(partner_allowed)
stats.append(
    {
        "Step": "Allowed LES Filter (Partner)",
        "Description": "Keep households where partner's les in [3,5,7]",
        "Total Households": total_p,
        "Female Heads": female_p,
        "Male Heads": male_p,
        "% Remaining": round(100 * total_p / initial_households, 2),
    }
)
# Step 5 (updated): Filter on other household members conditions for partnerships
# Drop households if any non-head/non-partner satisfies:
#    Either:
#       - Age between 16 and 65, with ddi == 0 and dec == 0
#    OR:
#       - Has yem > 50 or yse > 50 (regardless of age, ddi, or dec)
condition = (
    (partner_allowed["hh_IsHead"] == 0)
    & (partner_allowed["tu_hh_de_IsPartner"] == 0)
    & (
        (
            (partner_allowed["dag"] >= 16)
            & (partner_allowed["dag"] <= 65)
            & (partner_allowed["ddi"] == 0)
            & (partner_allowed["dec"] == 0)
        )
        | ((partner_allowed["yem"] > 50) | (partner_allowed["yse"] != 0))
    )
)

households_to_drop = partner_allowed.loc[condition, "idhh"].unique()
partner_les1 = partner_allowed[~partner_allowed["idhh"].isin(households_to_drop)]
# Debug: print the number of households after Step 5
new_household_count = partner_les1["idhh"].nunique()
print("After Other Household Members Filter, unique households:", new_household_count)

# Option 1: Using get_head_counts:
total_p_new, female_p_new, male_p_new = get_head_counts(partner_les1)

stats.append(
    {
        "Step": "Other Household Members Filter (Partner)",
        "Description": "Drop households based on other members' conditions",
        "Total Households": total_p_new,
        "Female Heads": female_p_new,
        "Male Heads": male_p_new,
        "% Remaining": round(100 * total_p_new / initial_households, 2),
    }
)

# Additional Filtering for Couples: Abnormal wage & labor time filter
df_final = partner_les1.copy()  # Starting dataset for abnormal filtering

condition_remove = (
    (df_final["les"] == 3)
    & (
        (df_final["lhw"] < 5)
        | (df_final["lhw"] > 79)
        | (df_final["yivwg"] < 2)
        | (df_final["yivwg"] > 170)
    )
    & ((df_final["hh_IsHead"] == 1) | (df_final["tu_hh_de_IsPartner"] == 1))
)

# Get households to drop due to abnormal conditions
households_to_drop_abnormal = df_final.loc[condition_remove, "idhh"].unique()
# Combine with the pre-computed households_to_drop
all_households_to_drop = np.union1d(households_to_drop_abnormal, households_to_remove)

# Drop all records from these households (no error if some IDs are already absent)
df_final_filtered = df_final[~df_final["idhh"].isin(all_households_to_drop)]
print(
    "After abnormal wage & labor time filter (couples), unique households:",
    df_final_filtered["idhh"].nunique(),
)
total_ab, female_ab, male_ab = get_head_counts(df_final_filtered)
stats.append(
    {
        "Step": "Wage & Labor Time Filter (Abnormal)",
        "Description": "Drop households with les==3 and abnormal wage or lhw",
        "Total Households": total_ab,
        "Female Heads": female_ab,
        "Male Heads": male_ab,
        "% Remaining": round(100 * total_ab / initial_households, 2),
    }
)

# -------------------------------
# Combine statistics and export the summary
# -------------------------------
stats_df = pd.DataFrame(stats)
print("\nStepwise Filtering Summary for Couples (Head & Partner):")
print(stats_df)

export_path = os.path.join(data_dir, "couples_filtering_summary_stepwise.csv")
stats_df.to_csv(export_path, index=False)
print(f"\nFiltering summary table exported to {export_path}")


# %%LATEX table export
# Export stats_df to a LaTeX table file
latex_table = stats_df.to_latex(
    index=False
)  # convert the DataFrame to a LaTeX table string
latex_export_path = os.path.join(data_dir, "couples_filtering_summary.tex")
with open(latex_export_path, "w") as f:
    f.write(latex_table)
print(f"LaTeX table exported to {latex_export_path}")


# %% DATA couples export

df_final_filtered.to_csv(os.path.join(data_dir, "couplesfinal.csv"), index=False)

# %%SINGLES
# Create a subset of the dataset where households have no member with tu_hh_de_IsPartner = 1 (i.e. all members have 0)
df_singles = final_df_sim1.groupby("idhh").filter(
    lambda group: (group["tu_hh_de_IsPartner"] == 0).all()
)
print("Unique households in singles:", df_singles["idhh"].nunique())


# %% Filtration - Stepwise Filtering on single households

# -------------------------------
# Baseline: df_singles (the starting point)
# -------------------------------
stats_singles = []
initial_households = df_singles["idhh"].nunique()
total, female, male = get_head_counts(df_singles)
stats_singles.append(
    {
        "Step": "Baseline (Singles)",
        "Description": "Initial singles households",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": 100.0,
    }
)
# Save baseline dataset for retrieval
baseline_singles = df_singles.copy()

# -------------------------------
# Stepwise Head Filtering Pipeline for Singles
# -------------------------------
head_stages_singles = {}  # dictionary to store intermediate head-filtered datasets

# Step 1: Age Filter for Heads: head's age between 16 and 65
head_age_singles = baseline_singles[
    baseline_singles["idhh"].isin(
        baseline_singles[baseline_singles["hh_IsHead"] == 1]
        .query("16 <= dag <= 65")["idhh"]
        .unique()
    )
]
head_stages_singles["Age"] = head_age_singles.copy()
total, female, male = get_head_counts(head_age_singles)
stats_singles.append(
    {
        "Step": "Age Filter (Head, Singles)",
        "Description": "Keep singles households where head's age in [16,65]",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 2: Education Filter for Heads: head not in education (dec == 0)
head_edu_singles = head_age_singles[
    head_age_singles["idhh"].isin(
        head_age_singles[head_age_singles["hh_IsHead"] == 1]
        .query("dec == 0")["idhh"]
        .unique()
    )
]
head_stages_singles["Education"] = head_edu_singles.copy()
total, female, male = get_head_counts(head_edu_singles)
stats_singles.append(
    {
        "Step": "Education Filter (Head, Singles)",
        "Description": "Keep singles households where head's dec == 0",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 3: Replacement Income Filter for Heads: head's replacement_income_total <= 100
head_inc_singles = head_edu_singles[
    head_edu_singles["idhh"].isin(
        head_edu_singles[head_edu_singles["hh_IsHead"] == 1]
        .query("replacement_income_total <= 100")["idhh"]
        .unique()
    )
]
head_stages_singles["Replacement Income"] = head_inc_singles.copy()
total, female, male = get_head_counts(head_inc_singles)
stats_singles.append(
    {
        "Step": "Replacement Income Filter (Head, Singles)",
        "Description": "Keep singles households where head's replacement_income_total <= 100",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 4: Les Filter for Heads: remove households where head has les == 5
head_les_singles = head_inc_singles[
    head_inc_singles["idhh"].isin(
        head_inc_singles[head_inc_singles["hh_IsHead"] == 1]
        .query("les != 5")["idhh"]
        .unique()
    )
]
head_stages_singles["Les"] = head_les_singles.copy()
total, female, male = get_head_counts(head_les_singles)
stats_singles.append(
    {
        "Step": "Les Filter (Head, Singles)",
        "Description": "Remove singles households where head has les == 5",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Additional Step for Heads: Allowed LES Filter (Singles)
# Drop households where the head's les is not in [3, 5, 7]
head_allowed_singles = head_les_singles[
    head_les_singles["idhh"].isin(
        head_les_singles[head_les_singles["hh_IsHead"] == 1]
        .query("les in [3, 5, 7]")["idhh"]
        .unique()
    )
]
head_stages_singles["Allowed LES"] = head_allowed_singles.copy()
total, female, male = get_head_counts(head_allowed_singles)
stats_singles.append(
    {
        "Step": "Allowed LES Filter (Head, Singles)",
        "Description": "Keep singles households where head's les in [3,5,7]",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    }
)

# Step 5 (updated): Filter on other household members conditions for singles
# Drop households if any non-head/non-partner meets:
#   Either: age is between 16 and 65, with ddi == 0 and dec == 0,
#   OR: has yem > 50 or yse > 50.
condition = (
    (head_allowed_singles["hh_IsHead"] == 0)
    & (head_allowed_singles["tu_hh_de_IsPartner"] == 0)
    & (
        (
            (head_allowed_singles["dag"] >= 16)
            & (head_allowed_singles["dag"] <= 65)
            & (head_allowed_singles["ddi"] == 0)
            & (head_allowed_singles["dec"] == 0)
        )
        | ((head_allowed_singles["yem"] > 50) | (head_allowed_singles["yse"] != 0))
    )
)
households_to_drop = head_allowed_singles.loc[condition, "idhh"].unique()
head_final_singles = head_allowed_singles[
    ~head_allowed_singles["idhh"].isin(households_to_drop)
]

# Debug: print the number of households after Step 5
new_household_count = head_final_singles["idhh"].nunique()
print(
    "After Other Household Members Filter (Singles), unique households:",
    new_household_count,
)

# Option 1: Using get_head_counts:
total_new, female_new, male_new = get_head_counts(head_final_singles)
stats_singles.append(
    {
        "Step": "Other Household Members Filter (Singles)",
        "Description": "Drop households based on other members' conditions",
        "Total Households": total_new,
        "Female Heads": female_new,
        "Male Heads": male_new,
        "% Remaining": round(100 * total_new / initial_households, 2),
    }
)

# Additional Filtering for Singles: Abnormal wage & labor time filter on heads
df_final_singles = head_final_singles.copy()  # Starting dataset for abnormal filtering

condition_remove = (
    (df_final_singles["les"] == 3)
    & (
        (df_final_singles["lhw"] < 5)
        | (df_final_singles["lhw"] > 79)
        | (df_final_singles["yivwg"] < 2)
        | (df_final_singles["yivwg"] > 170)
    )
    & (df_final_singles["hh_IsHead"] == 1)
)

households_to_drop_abnormal = df_final_singles.loc[condition_remove, "idhh"].unique()
all_households_to_drop = np.union1d(households_to_drop_abnormal, households_to_remove)

df_final_filtered_singles = df_final_singles[
    ~df_final_singles["idhh"].isin(all_households_to_drop)
]
print(
    "After abnormal wage & labor time filter (singles), unique households:",
    df_final_filtered_singles["idhh"].nunique(),
)
# Compute counts for the additional filtering step
total_ab, female_ab, male_ab = get_head_counts(df_final_filtered_singles)
stats_singles.append(
    {
        "Step": "Wage & Labor Time Filter (Abnormal, Singles)",
        "Description": "Drop singles households with les==3 and abnormal wage or lhw",
        "Total Households": total_ab,
        "Female Heads": female_ab,
        "Male Heads": male_ab,
        "% Remaining": round(100 * total_ab / initial_households, 2),
    }
)

# -------------------------------
# Combine statistics and export the summary for singles
# -------------------------------
stats_singles_df = pd.DataFrame(stats_singles)
print("\nStepwise Filtering Summary for Singles (Head):")
print(stats_singles_df)

export_path = os.path.join(data_dir, "singles_filtering_summary_stepwise.csv")
stats_singles_df.to_csv(export_path, index=False)
print(f"\nFiltering summary table exported to {export_path}")

# -------------------------------
# Export final singles dataset and subsets by head's gender
# -------------------------------
# Export general final singles dataset
final_singles_path = os.path.join(data_dir, "singles_final_filtered.csv")
df_final_filtered_singles.to_csv(final_singles_path, index=False)
print(f"Final singles dataset exported to {final_singles_path}")

# Split into female-headed and male-headed singles
female_singles = df_final_filtered_singles[
    df_final_filtered_singles["hh_IsHead"] == 1
].query("dgn == 0")
male_singles = df_final_filtered_singles[
    df_final_filtered_singles["hh_IsHead"] == 1
].query("dgn == 1")

female_text_path = os.path.join(data_dir, "singles_final_filtered_female.txt")
male_text_path = os.path.join(data_dir, "singles_final_filtered_male.txt")
female_pickle_path = os.path.join(data_dir, "singles_final_filtered_female.pkl")
male_pickle_path = os.path.join(data_dir, "singles_final_filtered_male.pkl")

# Export as text (using tab-separated format)
female_singles.to_csv(female_text_path, index=False, sep="\t")
male_singles.to_csv(male_text_path, index=False, sep="\t")

# Export as pickle
with open(female_pickle_path, "wb") as f:
    pickle.dump(female_singles, f)
with open(male_pickle_path, "wb") as f:
    pickle.dump(male_singles, f)

print(
    f"Female-headed singles exported to text: {female_text_path} and pickle: {female_pickle_path}"
)
print(
    f"Male-headed singles exported to text: {male_text_path} and pickle: {male_pickle_path}"
)

# %%LATEX singles table export
# Export stats_singles_df to a LaTeX table file
latex_table = stats_singles_df.to_latex(
    index=False
)  # convert the DataFrame to a LaTeX table string
latex_export_path = os.path.join(data_dir, "signles_filtering_summary.tex")
with open(latex_export_path, "w") as f:
    f.write(latex_table)
print(f"LaTeX table exported to {latex_export_path}")
# %%


# Check for overlapping idperson and idhh

# Extract the sets from each dataset
couples_idperson = set(df_final_filtered["idperson"])
females_idperson = set(female_singles["idperson"])
males_idperson = set(male_singles["idperson"])

couples_idhh = set(df_final_filtered["idhh"])
females_idhh = set(female_singles["idhh"])
males_idhh = set(male_singles["idhh"])

# Check overlaps for idperson
overlap_idperson_fm = females_idperson.intersection(males_idperson)
overlap_idperson_cf = couples_idperson.intersection(females_idperson)
overlap_idperson_cm = couples_idperson.intersection(males_idperson)

# Check overlaps for idhh
overlap_idhh_fm = females_idhh.intersection(males_idhh)
overlap_idhh_cf = couples_idhh.intersection(females_idhh)
overlap_idhh_cm = couples_idhh.intersection(males_idhh)

print("Overlap idperson between female_singles and male_singles:", overlap_idperson_fm)
print("Overlap idhh between female_singles and male_singles:", overlap_idhh_fm)
print("Overlap idperson between couples and female_singles:", overlap_idperson_cf)
print("Overlap idhh between couples and female_singles:", overlap_idhh_cf)
print("Overlap idperson between couples and male_singles:", overlap_idperson_cm)
print("Overlap idhh between couples and male_singles:", overlap_idhh_cm)

# If there is no overlap at all, pile the datasets together
if not (
    overlap_idperson_fm
    or overlap_idperson_cf
    or overlap_idperson_cm
    or overlap_idhh_fm
    or overlap_idhh_cf
    or overlap_idhh_cm
):
    df_filtered_piled = pd.concat(
        [df_final_filtered, female_singles, male_singles], axis=0
    )
    print(
        "No overlapping IDs found. Combined dataset has",
        df_filtered_piled["idhh"].nunique(),
        "unique households and",
        df_filtered_piled["idperson"].nunique(),
        "unique persons.",
    )

    # Export the combined dataset
    piled_export_path = os.path.join(data_dir, "filtered_piled.csv")
    df_filtered_piled.to_csv(piled_export_path, index=False)
    print(f"Combined filtered dataset exported to {piled_export_path}")
else:
    print(
        "Overlapping IDs were found between the datasets. Please review before combining."
    )
# %%


# %% CLEANIN
import gc

# Delete loaded DataFrames (adjust the names to match your code)
del df, df_sim, df_sim1, final_df_sim1, df_couples, baseline
del head_age, head_edu, head_inc, head_les
del partner_age, partner_edu, partner_inc, partner_les, partner_les1
del df_final, df_final_filtered
del female_singles, male_singles, df_filtered_piled

# Force garbage collection
gc.collect()

print("Memory freed.")
# %%
