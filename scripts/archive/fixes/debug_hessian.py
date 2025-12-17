"""
Debug script to diagnose Hessian computation issues for RURO estimation.
"""
import json
import numpy as np
from pathlib import Path

# Load estimation results
results_file = Path(__file__).parent.parent / "outputs/estimates/fr/2016/fr_2016_joint.json"
with open(results_file, 'r') as f:
    results = json.load(f)

theta = np.array(results['theta'])
param_names = results['param_names']

print("=" * 80)
print("HESSIAN COMPUTATION DIAGNOSTICS")
print("=" * 80)
print(f"\nNumber of parameters: {len(theta)}")
print(f"Log-likelihood: {results['log_likelihood']:.2f}")
print(f"Convergence: {results['message']}")
print()

# Check for problematic parameter values
print("-" * 80)
print("PARAMETER VALUE ANALYSIS")
print("-" * 80)

# Count parameters by magnitude
exact_zero = np.sum(theta == 0.0)
near_zero = np.sum((theta != 0.0) & (np.abs(theta) < 1e-6))
small = np.sum((np.abs(theta) >= 1e-6) & (np.abs(theta) < 0.01))
medium = np.sum((np.abs(theta) >= 0.01) & (np.abs(theta) < 1.0))
large = np.sum(np.abs(theta) >= 1.0)

print(f"Exactly zero: {exact_zero}")
print(f"Near zero (|theta| < 1e-6): {near_zero}")
print(f"Small (1e-6 <= |theta| < 0.01): {small}")
print(f"Medium (0.01 <= |theta| < 1.0): {medium}")
print(f"Large (|theta| >= 1.0): {large}")
print()

# List exact zeros
if exact_zero > 0:
    print("Parameters that are exactly zero:")
    for i, (name, val) in enumerate(zip(param_names, theta)):
        if val == 0.0:
            print(f"  [{i:3d}] {name}")
    print()

# List near-zero (machine precision)
if near_zero > 0:
    print("Parameters near machine precision:")
    for i, (name, val) in enumerate(zip(param_names, theta)):
        if val != 0.0 and np.abs(val) < 1e-6:
            print(f"  [{i:3d}] {name:40s} = {val:.6e}")
    print()

# Check if parameters are at bounds
bounds = results.get('bounds', [])
if bounds:
    at_lower = 0
    at_upper = 0
    print("Parameters at or near bounds:")
    for i, (name, val, (lb, ub)) in enumerate(zip(param_names, theta, bounds)):
        if lb is not None and ub is not None:
            tol = 1e-3  # tolerance for "at bound"
            if np.abs(val - lb) < tol:
                print(f"  [{i:3d}] {name:40s} = {val:.6f} (at lower bound {lb})")
                at_lower += 1
            elif np.abs(val - ub) < tol:
                print(f"  [{i:3d}] {name:40s} = {val:.6f} (at upper bound {ub})")
                at_upper += 1
    print(f"\nTotal at lower bound: {at_lower}")
    print(f"Total at upper bound: {at_upper}")
    print()

print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if exact_zero > 0:
    print(f"""
Found {exact_zero} parameters that are exactly zero. This suggests these parameters
are either:
  1. Fixed/constrained during estimation
  2. Converged to exactly zero due to regularization or poor identification
  3. Not estimated (initialization values)

For Hessian computation to work, we need to:
  - Identify which parameters are truly FIXED (not estimated)
  - Only compute Hessian for FREE parameters
  - Or use a different Hessian computation method that handles zeros

Check the estimation code to see if these parameters are truly being optimized
or if they're fixed values.
""")

if near_zero > 0:
    print(f"""
Found {near_zero} parameters near machine precision (< 1e-6). These are likely
numerically unstable for finite difference Hessian computation.

Consider:
  - Using larger step sizes (delta) for near-zero parameters
  - Switching to a different Hessian approximation method
""")

print("\nNext steps:")
print("1. Check which parameters are FIXED vs FREE in the estimation")
print("2. Modify compute_standard_errors() to only compute Hessian for FREE params")
print("3. Or use a more robust Hessian approximation (e.g., BFGS from optimizer)")