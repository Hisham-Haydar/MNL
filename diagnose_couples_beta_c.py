"""
Diagnostic script to understand why couples beta_c is negative.

This script will:
1. Load the couples data
2. Compute utility for chosen vs non-chosen alternatives
3. Check if higher consumption actually leads to higher utility
4. Verify gradient computation
5. Look at marginal utilities
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Load data
couples_file = "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet"
results_file = "U:/Desktop/Nizam_Hisham/MNL/outputs/estimation/fr/2016/joint/estimation_results.json"

print("=" * 80)
print("COUPLES BETA_C DIAGNOSTIC")
print("=" * 80)

# Load estimation results
with open(results_file, 'r') as f:
    results = json.load(f)

couples_params = results['results']['couples']['parameters']
beta_c = couples_params['beta_c']
theta_c = couples_params['theta_c']

print(f"\nEstimated parameters:")
print(f"  beta_c = {beta_c:.6f}")
print(f"  theta_c = {theta_c:.6f}")
print(f"  Gradient norm = {results['results']['couples']['gradient_norm']:.2f}")

# Load couples data
df = pd.read_parquet(couples_file)

print(f"\nData loaded: {len(df):,} rows")
print(f"Unique households: {df['idhh'].nunique():,}")

# Check consumption values
print("\n" + "=" * 80)
print("CONSUMPTION ANALYSIS")
print("=" * 80)

print(f"\nConsumption (c_norm) statistics:")
print(df['c_norm'].describe())

# Separate chosen vs non-chosen
chosen = df[df['is_chosen'] == 1]
non_chosen = df[df['is_chosen'] == 0]

print(f"\nChosen observations: {len(chosen):,}")
print(f"Non-chosen observations: {len(non_chosen):,}")

print(f"\nConsumption in CHOSEN alternatives:")
print(chosen['c_norm'].describe())

print(f"\nConsumption in NON-CHOSEN alternatives:")
print(non_chosen['c_norm'].describe())

# Key question: Is consumption higher in chosen or non-chosen?
chosen_c_mean = chosen['c_norm'].mean()
non_chosen_c_mean = non_chosen['c_norm'].mean()

print(f"\n" + "=" * 80)
print("KEY DIAGNOSTIC")
print("=" * 80)
print(f"\nMean consumption in CHOSEN: {chosen_c_mean:.4f}")
print(f"Mean consumption in NON-CHOSEN: {non_chosen_c_mean:.4f}")
print(f"Difference (chosen - non_chosen): {chosen_c_mean - non_chosen_c_mean:.4f}")

if chosen_c_mean < non_chosen_c_mean:
    print("\n⚠️  WARNING: Chosen alternatives have LOWER consumption than non-chosen!")
    print("   This would lead to NEGATIVE beta_c during estimation.")
    print("   This suggests the data structure or chosen indicator may be incorrect.")
else:
    print("\n✓ Chosen alternatives have higher consumption (expected)")

# Check for a sample household
print("\n" + "=" * 80)
print("SAMPLE HOUSEHOLD ANALYSIS")
print("=" * 80)

sample_hh = df['idhh'].iloc[0]
hh_data = df[df['idhh'] == sample_hh].copy()
hh_data = hh_data.sort_values('draw')

print(f"\nHousehold {sample_hh}:")
print(hh_data[['draw', 'hours_male', 'hours_female', 'consumption', 'c_norm', 'is_chosen']].to_string(index=False))

chosen_row = hh_data[hh_data['is_chosen'] == 1]
if len(chosen_row) > 0:
    print(f"\nChosen alternative (draw {chosen_row['draw'].iloc[0]}):")
    print(f"  hours_male = {chosen_row['hours_male'].iloc[0]}")
    print(f"  hours_female = {chosen_row['hours_female'].iloc[0]}")
    print(f"  consumption = {chosen_row['consumption'].iloc[0]:.2f}")
    print(f"  c_norm = {chosen_row['c_norm'].iloc[0]:.4f}")

    # Compare to mean of non-chosen
    non_chosen_hh = hh_data[hh_data['is_chosen'] == 0]
    print(f"\nNon-chosen alternatives (mean of {len(non_chosen_hh)} options):")
    print(f"  Mean consumption = {non_chosen_hh['consumption'].mean():.2f}")
    print(f"  Mean c_norm = {non_chosen_hh['c_norm'].mean():.4f}")

# Box-Cox transform analysis
print("\n" + "=" * 80)
print("BOX-COX TRANSFORM ANALYSIS")
print("=" * 80)

def box_cox(x, theta):
    """Box-Cox transformation."""
    if abs(theta) < 1e-6:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1) / theta

# Compute BC transform of consumption
df_sample = df.head(1000).copy()
df_sample['bc_c'] = df_sample['c_norm'].apply(lambda x: box_cox(x, theta_c))

print(f"\nWith theta_c = {theta_c:.4f}:")
print(f"  c_norm range: [{df_sample['c_norm'].min():.4f}, {df_sample['c_norm'].max():.4f}]")
print(f"  BC(c_norm) range: [{df_sample['bc_c'].min():.4f}, {df_sample['bc_c'].max():.4f}]")

# Check correlation with chosen
if 'is_chosen' in df_sample.columns:
    corr_c = df_sample[['c_norm', 'is_chosen']].corr().iloc[0, 1]
    corr_bc = df_sample[['bc_c', 'is_chosen']].corr().iloc[0, 1]
    print(f"\nCorrelation(c_norm, is_chosen) = {corr_c:.4f}")
    print(f"Correlation(BC(c_norm), is_chosen) = {corr_bc:.4f}")

    if corr_c < 0:
        print("\n⚠️  NEGATIVE correlation: chosen alternatives have LOWER consumption!")
    if corr_bc < 0:
        print("⚠️  NEGATIVE correlation after Box-Cox: This explains negative beta_c!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if chosen_c_mean < non_chosen_c_mean:
    print("\n🔴 ROOT CAUSE IDENTIFIED:")
    print("   Chosen alternatives have LOWER consumption than non-chosen alternatives.")
    print("   This is backwards from what the model expects!")
    print("\n   Possible causes:")
    print("   1. The 'is_chosen' indicator is inverted or incorrect")
    print("   2. The consumption calculation is wrong (sign error?)")
    print("   3. The data merge between draws and EUROMOD output is misaligned")
    print("   4. The chosen alternative (draw=0) has systematically lower income")
else:
    print("\n✓ Consumption pattern looks correct")
    print("   The negative beta_c must be due to another issue in the specification")

print("\n" + "=" * 80)
