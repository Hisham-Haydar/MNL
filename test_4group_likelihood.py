"""
Test script to debug 4-group likelihood computation
"""
import sys
sys.path.insert(0, 'scripts/enhanced')

import numpy as np
from pathlib import Path
from estimation_spec_parser import parse_specification
from estimation_utils import load_and_validate_mnl_data, precompute_data_singles
from estimation_engine import compute_likelihood_singles

# Load specification
spec = parse_specification(Path('scripts/enhanced/estimation_spec.yaml'))
print(f"Loaded spec with {len(spec.all_param_names)} parameters")
print(f"First 10 params: {spec.all_param_names[:10]}")

# Load data
mnl_base = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl")
singles_path = mnl_base.parent / f"{mnl_base.stem}__singles.parquet"
couples_path = mnl_base.parent / f"{mnl_base.stem}__couples.parquet"
metadata_path = mnl_base.parent / f"{mnl_base.stem}__mnlmeta.json"
df_singles, df_couples, metadata = load_and_validate_mnl_data(
    singles_path, couples_path, metadata_path, spec
)
print(f"\nLoaded {len(df_singles)} singles, {len(df_couples)} couples")

# Filter males (dgn==1 is male, dgn==0 is female)
df_male = df_singles[df_singles['dgn'] == 1].copy()
print(f"Filtered to {len(df_male)} males")

# Precompute
data_male = precompute_data_singles(df_male, metadata, is_male=True)
print(f"Precomputed data: {data_male.n_groups} groups, {data_male.n_obs} observations")

# Create initial parameter vector
theta_init = np.array([spec.initial_values[name] for name in spec.all_param_names])
print(f"\nInitial theta shape: {theta_init.shape}")
print(f"First 10 values: {theta_init[:10]}")

# Unpack to dict to verify
params_dict = spec.unpack_parameters(theta_init)
print(f"\nParams dict has {len(params_dict)} keys")
print(f"Sample keys: {list(params_dict.keys())[:15]}")

# Test if gender-specific keys exist
test_keys = ['beta_l0_sm', 'theta_l_sm', 'beta_c_sm']
for key in test_keys:
    if key in params_dict:
        print(f"OK {key} = {params_dict[key]}")
    else:
        print(f"MISSING {key}!")

# Try to compute likelihood
print("\n" + "="*60)
print("Computing likelihood for singles male...")
print("="*60)
try:
    ll = compute_likelihood_singles(theta_init, data_male, spec)
    print(f"SUCCESS: Log-likelihood = {ll}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
