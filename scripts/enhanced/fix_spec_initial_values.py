"""
Fix Missing Initial Values in Specification Files

This script adds missing initial values to specification files by:
1. Reading the base spec (estimation_spec.yaml) as reference
2. For each spec with missing values, adding reasonable defaults
3. Backing up original files before modifying

Author: RURO Pipeline
Created: 2026-01-17
"""

import sys
from pathlib import Path
import yaml
from typing import Dict, List

# Add scripts/enhanced to path
sys.path.insert(0, str(Path(__file__).parent))

from estimation_spec_parser import parse_specification


def get_default_initial_values() -> Dict[str, float]:
    """
    Get default initial values for common parameter patterns.

    These are reasonable starting points based on economic theory
    and the base specification.
    """
    return {
        # Consumption parameters
        'beta_c': 1.0,
        'theta_c': 0.5,

        # Leisure parameters (intercepts)
        'beta_l0': 1.0,
        'theta_l': 0.5,

        # Age effects
        'beta_age': 0.0,
        'beta_age2': 0.0,
        'beta_l_age_norm': 0.0,
        'beta_l_age_norm2': 0.0,

        # Children effects
        'beta_nch': 0.1,
        'beta_l_n_children': 0.1,
        'beta_C1': 0.0,
        'beta_C2': 0.0,
        'beta_C3': 0.0,

        # Education effects
        'beta_educL': 0.0,
        'beta_educH': 0.0,
        'beta_l_educL': 0.0,
        'beta_l_educH': 0.0,

        # Hours opportunity (work participation)
        'beta_work': 0.5,
        'beta_working': 0.5,
        'beta_pt1': 0.0,
        'beta_pt2': 0.0,
        'beta_ft': 0.0,
        'beta_PT1': 0.0,
        'beta_PT2': 0.0,
        'beta_FT': 0.0,
        'beta_gsur': 0.0,
        'beta_work_educL': 0.0,
        'beta_work_educH': 0.0,
        'beta_work_female': 0.0,
        'beta_work_couple': 0.0,
        'beta_work_idf': 0.0,

        # Wage equation parameters
        'beta_w0': 2.5,
        'beta_w_educL': -0.2,
        'beta_w_educH': 0.3,
        'beta_exp': 0.02,
        'beta_exp2': -0.001,
        'beta_pexp': 0.02,
        'beta_pexp2': 0.0,
        'sigma': 0.4,
        'sigma_w': 0.4,

        # Couples interaction
        'beta_interact': 0.0,
        'mu0': 0.0,

        # Region effects
        'beta_reg': 0.0,
        'beta_work_reg2': 0.0,
        'beta_work_reg3': 0.0,
    }


def get_param_base_name(param_name: str) -> str:
    """Extract base parameter name by removing gender/group suffixes."""
    suffixes = ['_sm', '_sf', '_m', '_f', '_cm', '_cf']
    for suffix in suffixes:
        if param_name.endswith(suffix):
            return param_name[:-len(suffix)]
    return param_name


def generate_initial_value(param_name: str, defaults: Dict[str, float]) -> float:
    """
    Generate a reasonable initial value for a parameter.

    Strategy:
    1. Look for exact match in defaults
    2. Look for base name match (e.g., beta_c_sm -> beta_c)
    3. Use pattern-based defaults
    4. Fall back to 0.0 or 0.5 depending on parameter type
    """
    # Check exact match
    if param_name in defaults:
        return defaults[param_name]

    # Check base name match
    base_name = get_param_base_name(param_name)
    if base_name in defaults:
        return defaults[base_name]

    # Pattern-based defaults
    if 'theta' in param_name:
        return 0.5  # Box-Cox curvature parameter
    elif 'beta_c' in param_name:
        return 1.0  # Consumption coefficient
    elif 'beta_l0' in param_name:
        return 1.0  # Leisure intercept
    elif 'beta_w0' in param_name:
        return 2.5  # Wage intercept (log scale)
    elif 'sigma' in param_name:
        return 0.4  # Variance parameter
    elif 'beta_work' in param_name or 'beta_PT' in param_name or 'beta_FT' in param_name:
        return 0.5  # Work participation
    else:
        return 0.0  # Default for shifters


def fix_spec_file(spec_path: Path, defaults: Dict[str, float], dry_run: bool = False) -> bool:
    """
    Fix missing initial values in a specification file.

    Returns True if file was modified, False otherwise.
    """
    print(f"\nProcessing: {spec_path.name}")
    print("="*70)

    try:
        # Try parsing with current parser
        spec = parse_specification(spec_path)
        print(f"[OK] Specification parses successfully")
        print(f"  Parameters: {len(spec.all_param_names)}")
        return False  # No changes needed

    except ValueError as e:
        error_msg = str(e)
        if "Missing initial values" not in error_msg:
            print(f"[ERROR] Unexpected error: {error_msg[:100]}")
            return False

        # Extract missing parameters from error message
        # Format: "Missing initial values for parameters: ['param1', 'param2', ...]"
        import re
        match = re.search(r"\['([^']+(?:',\s*'[^']+)*)'\]", error_msg)
        if not match:
            print(f"[ERROR] Could not parse missing parameters from error")
            return False

        missing_params_str = match.group(1)
        missing_params = [p.strip() for p in missing_params_str.split("', '")]

        print(f"[WARNING] Missing initial values for {len(missing_params)} parameters")
        print(f"  First 10: {missing_params[:10]}")
        if len(missing_params) > 10:
            print(f"  ... and {len(missing_params) - 10} more")

        # Load YAML file
        with open(spec_path, 'r') as f:
            spec_data = yaml.safe_load(f)

        # Ensure initial_values section exists
        if 'initial_values' not in spec_data:
            spec_data['initial_values'] = {}

        # Add missing initial values
        added_count = 0
        for param in missing_params:
            if param not in spec_data['initial_values']:
                value = generate_initial_value(param, defaults)
                spec_data['initial_values'][param] = value
                added_count += 1

        print(f"[INFO] Generated {added_count} initial values")

        if dry_run:
            print(f"[DRY RUN] Would add to initial_values:")
            for param in missing_params[:5]:
                value = generate_initial_value(param, defaults)
                print(f"  {param}: {value}")
            if len(missing_params) > 5:
                print(f"  ... and {len(missing_params) - 5} more")
            return False

        # Backup original file
        backup_path = spec_path.with_suffix('.yaml.backup')
        if not backup_path.exists():
            import shutil
            shutil.copy2(spec_path, backup_path)
            print(f"[INFO] Created backup: {backup_path.name}")

        # Write updated YAML
        with open(spec_path, 'w') as f:
            yaml.safe_dump(spec_data, f, default_flow_style=False, sort_keys=False)

        print(f"[SUCCESS] Updated {spec_path.name}")

        # Verify the fix worked
        try:
            spec = parse_specification(spec_path)
            print(f"[OK] Verification: specification now parses successfully")
            print(f"  Parameters: {len(spec.all_param_names)}")
            return True
        except Exception as verify_error:
            print(f"[ERROR] Verification failed: {verify_error}")
            return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fix all specification files with missing initial values."""

    print("="*70)
    print("Fix Missing Initial Values in Specification Files")
    print("="*70)

    # Get default initial values
    defaults = get_default_initial_values()
    print(f"\nLoaded {len(defaults)} default initial values")

    # Specification files to check
    spec_dir = Path(__file__).parent / "specifications"
    spec_files = [
        'estimation_spec_AC2013.yaml',
        'estimation_spec_loc_empirical.yaml',
    ]

    # Process each file
    modified_files = []
    for spec_file_name in spec_files:
        spec_path = spec_dir / spec_file_name

        if not spec_path.exists():
            print(f"\n[ERROR] File not found: {spec_file_name}")
            continue

        if fix_spec_file(spec_path, defaults, dry_run=False):
            modified_files.append(spec_file_name)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    if modified_files:
        print(f"\n[SUCCESS] Fixed {len(modified_files)} specification file(s):")
        for fname in modified_files:
            print(f"  - {fname}")
        print("\nBackup files created with .yaml.backup extension")
    else:
        print("\n[INFO] No files needed fixing (all specs already valid)")

    print("\nRun validate_specs.py to verify all specifications")


if __name__ == "__main__":
    main()
