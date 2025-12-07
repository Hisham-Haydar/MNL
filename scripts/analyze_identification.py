"""
Analyze parameter identification from RURO estimation results.
Creates a summary table showing which parameters are well-identified.
"""
import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Set UTF-8 encoding for Windows console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load results
results_file = Path(__file__).parent.parent / "outputs/estimates/fr/2016/fr_2016_joint.json"
with open(results_file, 'r') as f:
    results = json.load(f)

theta = np.array(results['theta'])
se = np.array(results['std_errors'])
t_values = np.array(results['t_values'])
param_names = results['param_names']

# Categorize parameters
categories = []
identification_status = []
issues = []

for i, (name, est, se_val, t_val) in enumerate(zip(param_names, theta, se, t_values)):
    # Determine category
    if name.startswith('sm.pref'):
        cat = 'SM Preferences'
    elif name.startswith('sf.pref'):
        cat = 'SF Preferences'
    elif name.startswith('cou.pref'):
        cat = 'Couple Preferences'
    elif name.startswith('hopp'):
        cat = 'Hours Opportunity'
    elif name.startswith('wopp'):
        cat = 'Wage Opportunity'
    else:
        cat = 'Other'

    categories.append(cat)

    # Determine identification status
    if not np.isfinite(se_val):
        status = '❌ Not Identified'
        issue = 'NaN SE'
    elif se_val < 1e-10:
        status = '⚠️ Numerical Issue'
        issue = f'SE too small ({se_val:.2e})'
    elif abs(est) < 1e-10:
        status = '⚠️ Zero Estimate'
        issue = 'Estimate ~0'
    elif abs(t_val) > 1e6:
        status = '⚠️ Extreme t-value'
        issue = f't={t_val:.2e}'
    elif abs(t_val) > 1.96:
        status = '✅ Well Identified'
        issue = '-'
    else:
        status = '⚙️ Weakly Significant'
        issue = f'|t|={abs(t_val):.2f} < 1.96'

    identification_status.append(status)
    issues.append(issue)

# Create summary DataFrame
df = pd.DataFrame({
    'Param': [f"[{i}] {name}" for i, name in enumerate(param_names)],
    'Category': categories,
    'Estimate': theta,
    'Std Error': se,
    't-value': t_values,
    'Status': identification_status,
    'Issue': issues
})

# Print summary statistics
print("=" * 100)
print("PARAMETER IDENTIFICATION SUMMARY - FRANCE 2016 JOINT ESTIMATION")
print("=" * 100)
print()

print("OVERALL STATISTICS:")
print("-" * 100)
status_counts = df['Status'].value_counts()
for status, count in status_counts.items():
    pct = 100 * count / len(df)
    print(f"{status:25s}: {count:3d} / {len(df)} ({pct:5.1f}%)")
print()

print("BY CATEGORY:")
print("-" * 100)
for cat in df['Category'].unique():
    cat_df = df[df['Category'] == cat]
    well_id = (cat_df['Status'] == '✅ Well Identified').sum()
    total = len(cat_df)
    pct = 100 * well_id / total if total > 0 else 0
    print(f"{cat:25s}: {well_id:3d} / {total:3d} well-identified ({pct:5.1f}%)")
print()

# Print problematic parameters
print("=" * 100)
print("PROBLEMATIC PARAMETERS (NaN or Extreme Values)")
print("=" * 100)
problematic = df[df['Status'].isin(['❌ Not Identified', '⚠️ Numerical Issue', '⚠️ Extreme t-value'])]
if len(problematic) > 0:
    print(problematic[['Param', 'Category', 'Estimate', 'Std Error', 'Status', 'Issue']].to_string(index=False))
else:
    print("No problematic parameters!")
print()

# Print well-identified parameters
print("=" * 100)
print("WELL-IDENTIFIED PARAMETERS (|t| > 1.96)")
print("=" * 100)
well_identified = df[df['Status'] == '✅ Well Identified']
print(f"Total: {len(well_identified)} parameters")
print()

# Group by category
for cat in df['Category'].unique():
    cat_well = well_identified[well_identified['Category'] == cat]
    if len(cat_well) > 0:
        print(f"\n{cat} ({len(cat_well)} parameters):")
        print("-" * 100)
        for _, row in cat_well.iterrows():
            print(f"  {row['Param']:60s}  Est={row['Estimate']:8.4f}  SE={row['Std Error']:8.4f}  t={row['t-value']:8.2f}")

# Save detailed table to CSV
output_file = Path(__file__).parent.parent / "outputs/estimates/fr/2016/identification_analysis.csv"
df.to_csv(output_file, index=False)
print()
print("=" * 100)
print(f"✅ Detailed analysis saved to: {output_file}")
print("=" * 100)