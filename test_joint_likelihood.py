"""
Test joint likelihood function
"""
import sys
sys.path.insert(0, 'scripts/enhanced')

import numpy as np
from pathlib import Path
from estimation_spec_parser import parse_specification
from estimation_utils import load_and_validate_mnl_data, precompute_data_singles, precompute_data_couples
from estimation_engine import compute_likelihood_joint, compute_gradient_joint

print("="*80)
print("Testing Joint Likelihood for 4-Group Architecture")
print("="*80)

# Load specification
spec = parse_specification(Path('scripts/enhanced/estimation_spec.yaml'))
print(f"\n1. Loaded spec with {len(spec.all_param_names)} parameters")

# Load data
mnl_base = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl")
singles_path = mnl_base.parent / f"{mnl_base.stem}__singles.parquet"
couples_path = mnl_base.parent / f"{mnl_base.stem}__couples.parquet"
metadata_path = mnl_base.parent / f"{mnl_base.stem}__mnlmeta.json"

df_singles, df_couples, metadata = load_and_validate_mnl_data(
    singles_path, couples_path, metadata_path, spec
)
print(f"2. Loaded {len(df_singles):,} singles, {len(df_couples):,} couples")

# Filter and precompute
df_male = df_singles[df_singles['dgn'] == 1].copy()
df_female = df_singles[df_singles['dgn'] == 0].copy()

print(f"3. Split: {len(df_male):,} males, {len(df_female):,} females")

data_sm = precompute_data_singles(df_male, metadata, is_male=True)
data_sf = precompute_data_singles(df_female, metadata, is_male=False)
data_c = precompute_data_couples(df_couples, metadata)

print(f"4. Precomputed:")
print(f"   - Singles male: {data_sm.n_groups:,} groups")
print(f"   - Singles female: {data_sf.n_groups:,} groups")
print(f"   - Couples: {data_c.n_groups:,} groups")

# Create initial parameter vector
theta_init = np.array([spec.initial_values[name] for name in spec.all_param_names])
print(f"\n5. Initial theta shape: {theta_init.shape}")

# Test joint likelihood
print("\n" + "="*80)
print("Computing JOINT likelihood...")
print("="*80)
try:
    ll_joint = compute_likelihood_joint(theta_init, data_sm, data_sf, data_c, spec)
    print(f"SUCCESS: Joint negative LL = {ll_joint:.6f}")
    print(f"         Joint LL = {-ll_joint:.6f}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test joint gradient
print("\n" + "="*80)
print("Computing JOINT gradient...")
print("="*80)
try:
    grad_joint = compute_gradient_joint(theta_init, data_sm, data_sf, data_c, spec)
    print(f"SUCCESS: Gradient shape = {grad_joint.shape}")
    print(f"         Gradient norm = {np.linalg.norm(grad_joint):.6f}")
    print(f"         Max gradient = {np.max(np.abs(grad_joint)):.6f}")

    # Check for zeros
    zero_grads = np.abs(grad_joint) < 1e-12
    n_zeros = np.sum(zero_grads)
    print(f"         Zero gradients: {n_zeros} / {len(grad_joint)}")

    if n_zeros > 0:
        print(f"\nWARNING: {n_zeros} parameters have zero gradient!")
        for i in np.where(zero_grads)[0]:
            print(f"  - {spec.all_param_names[i]}")
    else:
        print("\n✓ All parameters have non-zero gradients!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("Joint likelihood test PASSED!")
print("="*80)
