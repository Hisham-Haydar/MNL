#!/usr/bin/env python
"""Quick verification that all fixes are in place."""

import sys
from pathlib import Path

def check_gamspy_fix():
    """Verify GAMSPY Options fix is in place."""
    print("=" * 80)
    print("CHECKING GAMSPY OPTIONS FIX")
    print("=" * 80)
    
    gamspy_file = Path("scripts/enhanced/gamspy_estimation.py")
    
    if not gamspy_file.exists():
        print("❌ GAMSPY estimation file not found")
        return False
    
    content = gamspy_file.read_text(encoding='utf-8')
    
    # Check 1: Options imported
    if "from gamspy import" in content and "Options" in content:
        print("✅ Options class imported")
    else:
        print("❌ Options class NOT imported")
        return False
    
    # Check 2: Options() used instead of {}
    if "solver_options = Options()" in content:
        print("✅ Options() constructor used")
    else:
        print("❌ Options() constructor NOT used")
        return False
    
    # Check 3: No dict-style options (old way)
    dict_pattern = 'solver_options = {'
    if dict_pattern in content:
        print("⚠️  WARNING: Old dict-style options still found")
        print("   (This might be in comments or unused code)")
    else:
        print("✅ No old dict-style options found")
    
    print("\n✅ GAMSPY Options fix verified!")
    return True

def check_column_filtering():
    """Verify column filtering is in Step 6."""
    print("\n" + "=" * 80)
    print("CHECKING COLUMN FILTERING IN STEP 6")
    print("=" * 80)
    
    step6_file = Path("scripts/enhanced/enh_RURO_prep_mnl_basic.py")
    
    if not step6_file.exists():
        print("❌ Step 6 file not found")
        return False
    
    content = step6_file.read_text(encoding='utf-8')
    
    # Check 1: Function defined
    if "def get_essential_columns_for_estimation()" in content:
        print("✅ get_essential_columns_for_estimation() defined")
    else:
        print("❌ get_essential_columns_for_estimation() NOT defined")
        return False
    
    # Check 2: Filter function defined
    if "def filter_to_essential_columns(" in content:
        print("✅ filter_to_essential_columns() defined")
    else:
        print("❌ filter_to_essential_columns() NOT defined")
        return False
    
    # Check 3: User-requested columns included
    if '"loc4"' in content and '"lindi"' in content:
        print("✅ User-requested columns (loc4, lindi) included")
    else:
        print("❌ User-requested columns NOT found")
        return False
    
    # Check 4: CLI flag added
    if "--no-column-filter" in content:
        print("✅ --no-column-filter CLI flag added")
    else:
        print("❌ --no-column-filter CLI flag NOT added")
        return False
    
    print("\n✅ Column filtering verified!")
    return True

def check_reduced_euromod():
    """Check if reduced EUROMOD file exists."""
    print("\n" + "=" * 80)
    print("CHECKING REDUCED EUROMOD FILE")
    print("=" * 80)
    
    reduced_file = Path("U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet")
    
    if not reduced_file.exists():
        print("⚠️  Reduced EUROMOD file not found")
        print(f"   Expected: {reduced_file}")
        print("   Run reduce_mnl_columns.py first!")
        return False
    
    size_mb = reduced_file.stat().st_size / (1024 * 1024)
    print(f"✅ Reduced EUROMOD file exists: {size_mb:.1f} MB")
    
    if size_mb < 100:
        print("✅ File size looks good (< 100 MB)")
    else:
        print("⚠️  File size seems large (expected ~63 MB)")
    
    return True

def main():
    """Run all checks."""
    print("\n" + "=" * 80)
    print("OPTIMIZATION VERIFICATION")
    print("=" * 80 + "\n")
    
    results = []
    
    # Check 1: GAMSPY fix
    try:
        results.append(("GAMSPY Options Fix", check_gamspy_fix()))
    except Exception as e:
        print(f"❌ GAMSPY check failed: {e}")
        results.append(("GAMSPY Options Fix", False))
    
    # Check 2: Column filtering
    try:
        results.append(("Column Filtering", check_column_filtering()))
    except Exception as e:
        print(f"❌ Column filtering check failed: {e}")
        results.append(("Column Filtering", False))
    
    # Check 3: Reduced EUROMOD
    try:
        results.append(("Reduced EUROMOD", check_reduced_euromod()))
    except Exception as e:
        print(f"❌ Reduced EUROMOD check failed: {e}")
        results.append(("Reduced EUROMOD", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    all_good = all(status for _, status in results)
    
    if all_good:
        print("\n" + "=" * 80)
        print("🎉 ALL CHECKS PASSED - READY TO RUN!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run: .\\RUN_PIPELINE_WITH_REDUCED_FILES.ps1")
        print("  2. Select option 2 (Full pipeline)")
        print("  3. Enjoy 2-3x faster pipeline! 🚀")
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
