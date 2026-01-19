"""
Specification Validation Script for RURO MNL Estimation

This script validates all YAML specification files and documents their structure,
parameter counts, and completeness.

Author: RURO Pipeline
Created: 2026-01-17
"""

import sys
from pathlib import Path
import yaml

# Add scripts/enhanced to path
sys.path.insert(0, str(Path(__file__).parent))

from estimation_spec_parser import parse_specification


def validate_spec(spec_file: Path) -> dict:
    """Validate a single specification file and return summary info."""
    result = {
        'file': spec_file.name,
        'valid': False,
        'n_params': None,
        'spec_name': None,
        'has_4group': None,
        'error': None
    }

    try:
        spec = parse_specification(spec_file)
        result['valid'] = True
        result['n_params'] = len(spec.all_param_names)
        result['spec_name'] = getattr(spec, 'spec_name', None)
        result['has_4group'] = spec.has_couples_gender_specific_params() if hasattr(spec, 'has_couples_gender_specific_params') else None

        # Additional info
        result['all_params'] = list(spec.all_param_names) if hasattr(spec, 'all_param_names') else []
        result['bounds'] = spec.bounds if hasattr(spec, 'bounds') else {}
        result['initial_values'] = spec.initial_values if hasattr(spec, 'initial_values') else {}

    except Exception as e:
        result['error'] = str(e)
        result['all_params'] = []

    return result


def main():
    """Validate all specification files in scripts/enhanced/."""

    spec_dir = Path(__file__).parent
    spec_files = [
        'estimation_spec.yaml',
        'estimation_spec_AC2013.yaml',
        'estimation_spec_v2.yaml',
        'estimation_spec_loc_empirical.yaml'
    ]

    print("="*80)
    print("RURO MNL Specification Validation")
    print("="*80)
    print()

    results = []
    for spec_file_name in spec_files:
        spec_path = spec_dir / spec_file_name

        if not spec_path.exists():
            print(f"[ERROR] {spec_file_name:40s} - FILE NOT FOUND")
            continue

        result = validate_spec(spec_path)
        results.append(result)

        if result['valid']:
            print(f"[OK] {spec_file_name:40s} - {result['n_params']:2d} parameters")
            print(f"  Spec name: {result['spec_name']}")
            print(f"  Has 4-group architecture: {result['has_4group']}")
        else:
            error_preview = result['error'][:100] + '...' if len(result['error']) > 100 else result['error']
            print(f"[ERROR] {spec_file_name:40s} - ERROR")
            print(f"  {error_preview}")
        print()

    # Summary table
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"{'Specification':<40s} {'Status':<10s} {'Params':<8s} {'4-Group':<8s}")
    print("-"*80)

    for result in results:
        status = "[OK]" if result['valid'] else "[ERROR]"
        n_params = str(result['n_params']) if result['n_params'] else "N/A"
        has_4group = str(result['has_4group']) if result['has_4group'] is not None else "N/A"

        print(f"{result['file']:<40s} {status:<10s} {n_params:<8s} {has_4group:<8s}")

    print()

    # Detailed parameter comparison for valid specs
    valid_specs = [r for r in results if r['valid']]

    if len(valid_specs) > 1:
        print("="*80)
        print("PARAMETER COMPARISON")
        print("="*80)
        print()

        # Find parameters unique to each spec
        all_param_sets = {r['spec_name']: set(r['all_params']) for r in valid_specs}

        for spec_name, params in all_param_sets.items():
            print(f"\n{spec_name}:")

            # Params unique to this spec
            unique = params
            for other_name, other_params in all_param_sets.items():
                if other_name != spec_name:
                    unique = unique - other_params

            if unique:
                print(f"  Unique parameters ({len(unique)}):")
                for p in sorted(unique)[:10]:  # Show first 10
                    print(f"    - {p}")
                if len(unique) > 10:
                    print(f"    ... and {len(unique) - 10} more")
            else:
                print("  No unique parameters")

    print()
    print("="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print()

    # Check for missing specs
    invalid_specs = [r for r in results if not r['valid']]
    if invalid_specs:
        print("[WARNING] The following specifications have errors and need to be fixed:")
        for r in invalid_specs:
            print(f"  - {r['file']}: {r['error'][:80]}...")
        print()

    # Check for 4-group architecture
    non_4group_specs = [r for r in valid_specs if not r['has_4group']]
    if non_4group_specs:
        print("[WARNING] The following specifications don't have 4-group architecture:")
        for r in non_4group_specs:
            print(f"  - {r['file']} ({r['spec_name']})")
        print("  Consider updating these to support separate singles_male/singles_female parameters.")
        print()

    # Recommend which spec to use
    if valid_specs:
        print("[OK] Recommended specification for GAMSPy development:")
        # Prefer 4-group specs
        four_group_specs = [r for r in valid_specs if r['has_4group']]
        if four_group_specs:
            recommended = four_group_specs[0]
            print(f"  - {recommended['file']} ({recommended['n_params']} parameters)")
            print(f"    Reason: Has 4-group architecture, fully defined")
        else:
            recommended = valid_specs[0]
            print(f"  - {recommended['file']} ({recommended['n_params']} parameters)")
            print(f"    Reason: Fully defined (but consider adding 4-group support)")


if __name__ == "__main__":
    main()
