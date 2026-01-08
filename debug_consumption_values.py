"""
Debug script to inspect consumption_male and consumption_female values
and understand why beta_c is negative for couples.
"""

import pandas as pd
import numpy as np

# Load couples data
couples_file = "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl___couples.parquet"
df = pd.read_parquet(couples_file)

print("=" * 80)
print("COUPLES CONSUMPTION DATA INSPECTION")
print("=" * 80)
print(f"\nTotal observations: {len(df):,}")
print(f"Unique households: {df['idhh'].nunique():,}")

# Check consumption_male
print("\n" + "=" * 80)
print("CONSUMPTION_MALE")
print("=" * 80)
print(df['consumption_male'].describe())
print(f"\nNegative values: {(df['consumption_male'] < 0).sum():,}")
print(f"Zero values: {(df['consumption_male'] == 0).sum():,}")
print(f"At floor (1.0): {(df['consumption_male'] == 1.0).sum():,}")

# Check consumption_female
print("\n" + "=" * 80)
print("CONSUMPTION_FEMALE")
print("=" * 80)
print(df['consumption_female'].describe())
print(f"\nNegative values: {(df['consumption_female'] < 0).sum():,}")
print(f"Zero values: {(df['consumption_female'] == 0).sum():,}")
print(f"At floor (1.0): {(df['consumption_female'] == 1.0).sum():,}")

# Check sum
print("\n" + "=" * 80)
print("CONSUMPTION_MALE + CONSUMPTION_FEMALE")
print("=" * 80)
df['consumption_sum'] = df['consumption_male'] + df['consumption_female']
print(df['consumption_sum'].describe())
print(f"\nNegative values: {(df['consumption_sum'] < 0).sum():,}")
print(f"Zero values: {(df['consumption_sum'] == 0).sum():,}")

# Check chosen vs non-chosen
print("\n" + "=" * 80)
print("CHOSEN VS NON-CHOSEN")
print("=" * 80)
chosen = df[df['is_chosen'] == 1]
non_chosen = df[df['is_chosen'] == 0]

print(f"\nChosen observations: {len(chosen):,}")
print(f"Non-chosen observations: {len(non_chosen):,}")

print("\nCONSUMPTION_SUM for CHOSEN:")
print(chosen['consumption_sum'].describe())

print("\nCONSUMPTION_SUM for NON-CHOSEN:")
print(non_chosen['consumption_sum'].describe())

# Check correlation with hours
print("\n" + "=" * 80)
print("CORRELATION WITH HOURS")
print("=" * 80)
print(f"\nCorrelation(consumption_male, hours_male): {df['consumption_male'].corr(df['hours_male']):.4f}")
print(f"Correlation(consumption_female, hours_female): {df['consumption_female'].corr(df['hours_female']):.4f}")

# Sample some households
print("\n" + "=" * 80)
print("SAMPLE HOUSEHOLD (First household, all draws)")
print("=" * 80)
first_hh = df[df['idhh'] == df['idhh'].iloc[0]].copy()
first_hh = first_hh.sort_values('draw')
print(first_hh[['idhh', 'draw', 'hours_male', 'hours_female',
                'consumption_male', 'consumption_female', 'consumption_sum',
                'is_chosen']].to_string(index=False))

# Check if consumption varies by draw for same household
print("\n" + "=" * 80)
print("CONSUMPTION VARIATION BY DRAW (First 3 households)")
print("=" * 80)
for i, hh in enumerate(df['idhh'].unique()[:3]):
    hh_data = df[df['idhh'] == hh].copy()
    hh_data = hh_data.sort_values('draw')

    print(f"\nHousehold {i+1} (idhh={hh}):")
    print(f"  consumption_male range: [{hh_data['consumption_male'].min():.2f}, {hh_data['consumption_male'].max():.2f}]")
    print(f"  consumption_female range: [{hh_data['consumption_female'].min():.2f}, {hh_data['consumption_female'].max():.2f}]")
    print(f"  consumption_sum range: [{hh_data['consumption_sum'].min():.2f}, {hh_data['consumption_sum'].max():.2f}]")
    print(f"  Unique consumption_male values: {hh_data['consumption_male'].nunique()}")
    print(f"  Unique consumption_female values: {hh_data['consumption_female'].nunique()}")

# Compare to singles data
print("\n" + "=" * 80)
print("COMPARISON WITH SINGLES DATA")
print("=" * 80)

singles_male_file = "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl___singles_male.parquet"
singles_female_file = "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl___singles_female.parquet"

try:
    df_sm = pd.read_parquet(singles_male_file)
    print(f"\nSingles Male consumption:")
    print(df_sm['consumption'].describe())
except Exception as e:
    print(f"\nCould not load singles male: {e}")

try:
    df_sf = pd.read_parquet(singles_female_file)
    print(f"\nSingles Female consumption:")
    print(df_sf['consumption'].describe())
except Exception as e:
    print(f"\nCould not load singles female: {e}")

print("\n" + "=" * 80)
print("END OF DIAGNOSTIC")
print("=" * 80)
