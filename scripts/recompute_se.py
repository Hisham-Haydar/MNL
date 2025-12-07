"""
Recompute standard errors for existing estimation results using the fixed method.
"""
import json
import sys
import numpy as np
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from RURO_post_estimation import compute_standard_errors
from RURO_estimate_FR import fast_neg_ll_with_grad_joint, precompute_data_singles, precompute_data_couples
import pandas as pd

# Load estimation results
results_file = Path(__file__).parent.parent / "outputs/estimates/fr/2016/fr_2016_joint.json"
print(f"Loading results from: {results_file}")
with open(results_file, 'r') as f:
    results = json.load(f)

theta = np.array(results['theta'])
param_names = results['param_names']
wage_spec = results['wage_spec']

print("=" * 80)
print("RECOMPUTING STANDARD ERRORS WITH IMPROVED METHOD")
print("=" * 80)
print(f"Number of parameters: {len(theta)}")
print(f"Wage spec: {wage_spec}")
print()

# Load the MNL dataset
mnl_file = Path(__file__).parent.parent / "outputs/FR_2016_MNL_dataset.h5"
print(f"Loading MNL dataset from: {mnl_file}")

import h5py
with h5py.File(mnl_file, 'r') as hf:
    # Load single males
    df_sm = pd.DataFrame({
        key: hf['single_males'][key][:]
        for key in hf['single_males'].keys()
    })

    # Load single females
    df_sf = pd.DataFrame({
        key: hf['single_females'][key][:]
        for key in hf['single_females'].keys()
    })

    # Load couples
    df_cou = pd.DataFrame({
        key: hf['couples'][key][:]
        for key in hf['couples'].keys()
    })

print(f"Loaded {len(df_sm)} single males, {len(df_sf)} single females, {len(df_cou)} couples")
print()

# Precompute data
print("Precomputing data matrices...")
data_sm = precompute_data_singles(df_sm, is_male=True)
data_sf = precompute_data_singles(df_sf, is_male=False)
data_cou = precompute_data_couples(df_cou)
print("Done.")
print()

# Create gradient function
def joint_grad_func(theta):
    """Gradient function for standard error computation."""
    _, neg_grad = fast_neg_ll_with_grad_joint(
        theta,
        data_sm, data_sf, data_cou,
        wage_spec
    )
    return neg_grad

# Compute standard errors using improved method
print("Computing standard errors (this may take a few minutes)...")
print("Using adaptive step sizing and pseudo-inverse fallback...")
print()

se_result = compute_standard_errors(
    theta=theta,
    grad_func=joint_grad_func,
    param_names=param_names,
    method="jacobian",  # Central differences
    delta=1e-4,  # Increased from 1e-5 for stability
)

se = se_result.get("se")
varcov = se_result.get("varcov")
t_values = se_result.get("t_values")
eigenvalues = se_result.get("eigenvalues")

print()
print("=" * 80)
print("RESULTS")
print("=" * 80)

# Count valid SEs
n_valid = np.sum(np.isfinite(se))
print(f"Valid standard errors: {n_valid}/{len(se)}")
print()

# Show eigenvalue summary
print("Hessian eigenvalue summary:")
print(f"  Minimum: {eigenvalues.min():.6e}")
print(f"  Maximum: {eigenvalues.max():.6e}")
print(f"  Condition number: {eigenvalues.max() / eigenvalues.min():.2e}")
print(f"  Negative eigenvalues: {np.sum(eigenvalues < 0)}")
print(f"  Near-zero eigenvalues (|λ| < 1e-8): {np.sum(np.abs(eigenvalues) < 1e-8)}")
print()

# Update JSON file
if n_valid > 0:
    results['std_errors'] = se.tolist()
    results['t_values'] = t_values.tolist()

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Updated {results_file} with new standard errors")
    print()

    # Show parameters with significant estimates (|t| > 1.96)
    param_table = se_result['param_table']
    significant = param_table[np.abs(param_table['t_value']) > 1.96]

    print(f"Significant parameters (|t| > 1.96): {len(significant)}")
    print()
    print(significant.to_string())
else:
    print("ERROR: No valid standard errors computed!")
    print("The Hessian is still singular even with improved method.")
    print("This indicates serious identification issues in the model.")