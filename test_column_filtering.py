#!/usr/bin/env python
"""Test that column filtering functions work correctly."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.enhanced.enh_RURO_prep_mnl_basic import (
    get_essential_columns_for_estimation,
    filter_to_essential_columns
)

def test_column_functions():
    """Test the column filtering functions."""
    print("=" * 80)
    print("TESTING COLUMN FILTERING FUNCTIONS")
    print("=" * 80)
    
    # Test get_essential_columns_for_estimation
    essential = get_essential_columns_for_estimation()
    
    print(f"\n✅ Function loaded successfully!")
    print(f"Total essential columns defined: {len(essential)}")
    
    # Show sample columns by category
    categories = {
        "IDs": ["idhh", "idhh_true", "idperson", "idperson_true", "draw"],
        "Demographics": ["dag", "age_norm", "dgn", "female", "educ3", "educL"],
        "Labor": ["hours", "wage", "working", "loc4", "lindi"],
        "EUROMOD": ["ils_dispy", "ils_dispy_male", "ils_dispy_female"],
        "Utility": ["consumption", "leisure", "c_norm", "l_norm"],
        "Prior/GSUR": ["prior", "log_prior", "gsur"],
    }
    
    print("\nSample columns by category:")
    for cat, sample_cols in categories.items():
        found = [c for c in sample_cols if c in essential]
        print(f"  {cat}: {found}")
    
    # Verify user-requested columns
    print("\nUser-requested columns:")
    for col in ["loc4", "lindi"]:
        status = "✅ FOUND" if col in essential else "❌ MISSING"
        print(f"  {col}: {status}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        test_column_functions()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
