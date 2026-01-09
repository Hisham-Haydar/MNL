#!/usr/bin/env python
"""
==============================================================================
Verify Aaberge-Colombino (2013) Implementation
==============================================================================
Quick verification that all AC2013 components are working correctly.

Author: RURO Pipeline
Created: 2026-01-09
==============================================================================
"""

import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_yaml_parsing():
    """Test that AC2013 YAML spec parses correctly."""
    import yaml
    
    yaml_path = Path(__file__).parent / "estimation_spec_AC2013.yaml"
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    assert config.get('model_version') == 'AC2013', "Model version should be AC2013"
    assert 'singles' in config, "Should have singles block"
    assert 'couples' in config, "Should have couples block"
    assert 'preference' in config['singles'], "Singles should have preference block"
    assert 'opportunity' in config['singles'], "Singles should have opportunity block"
    
    print("✓ YAML parsing test passed")
    return True


def test_spec_parser():
    """Test that EstimationSpec has AC2013 fields."""
    from estimation_spec_parser import EstimationSpec
    
    fields = EstimationSpec.__dataclass_fields__
    
    ac2013_fields = [f for f in fields if 'ac2013' in f or 'model_version' in f]
    
    assert 'model_version' in fields, "Should have model_version field"
    assert 'ac2013_use_log_age' in fields, "Should have ac2013_use_log_age field"
    assert 'ac2013_children_age_groups' in fields, "Should have ac2013_children_age_groups field"
    assert 'ac2013_experience_in_wage' in fields, "Should have ac2013_experience_in_wage field"
    assert 'ac2013_couples_cross_leisure' in fields, "Should have ac2013_couples_cross_leisure field"
    assert 'ac2013_couples_mu_0' in fields, "Should have ac2013_couples_mu_0 field"
    
    print(f"✓ Spec parser test passed ({len(ac2013_fields)} AC2013 fields found)")
    return True


def test_ac2013_utils():
    """Test AC2013 utility functions."""
    import numpy as np
    from estimation_utils_AC2013 import (
        compute_log_age_terms,
        compute_wage_mean_AC2013,
        compute_joint_market_availability,
        get_ac2013_vs_legacy_comparison
    )
    
    # Test log-age
    ages = np.array([25, 35, 45, 55, 65])
    log_age, log_age_sq = compute_log_age_terms(ages)
    assert np.allclose(log_age, np.log(ages)), "Log age should match np.log"
    assert np.allclose(log_age_sq, np.log(ages)**2), "Log age² should match"
    
    # Test wage mean
    params = {
        'beta_w0': 2.5,
        'beta_exp': 0.03,
        'beta_exp2': -0.0005,
        'beta_educL': -0.1,
        'beta_educH': 0.2,
        'sigma_w': 0.4
    }
    data = {
        'exp': np.array([10.0]),
        'exp2': np.array([100.0]),
        'educL': np.array([0.0]),
        'educH': np.array([1.0]),
        'log_wage': np.array([2.8])
    }
    
    mu_w = compute_wage_mean_AC2013(params, data)
    expected = 2.5 + 0.03 * 10 - 0.0005 * 100 + 0.2 * 1
    assert np.allclose(mu_w, expected), f"Wage mean {mu_w} should be {expected}"
    
    # Test joint market availability
    w_m = np.array([1, 1, 0, 0])
    w_f = np.array([1, 0, 1, 0])
    log_f = compute_joint_market_availability(w_m, w_f, mu_0=1.5)
    assert log_f[0] == np.log(1.5), "Both working should have log(μ₀)"
    assert log_f[1] == 0.0, "Only male working should have 0"
    assert log_f[2] == 0.0, "Only female working should have 0"
    assert log_f[3] == 0.0, "Neither working should have 0"
      # Test comparison table
    table = get_ac2013_vs_legacy_comparison()
    assert "A-C 2013" in table or "AC2013" in table, "Comparison table should mention A-C 2013"
    assert "Legacy" in table, "Comparison table should mention Legacy"
    
    print("✓ AC2013 utils test passed")
    return True


def test_estimation_engine_import():
    """Test that estimation engine imports with AC2013 support."""
    import estimation_engine
    
    # Check that the engine module loaded
    assert hasattr(estimation_engine, 'compute_likelihood_singles'), "Should have compute_likelihood_singles"
    
    print("✓ Estimation engine import test passed")
    return True


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("Aaberge-Colombino (2013) Implementation Verification")
    print("=" * 70)
    print()
    
    tests = [
        ("YAML Parsing", test_yaml_parsing),
        ("Spec Parser", test_spec_parser),
        ("AC2013 Utils", test_ac2013_utils),
        ("Estimation Engine", test_estimation_engine_import),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {name} test FAILED: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print()
        print("All AC2013 implementation tests passed!")
        print()
        print("To run estimation with AC2013 specification:")
        print()
        print("  python enh_RURO_estimate_FR.py \\")
        print("    --mnl-base \"<your-mnl-base-path>\" \\")
        print("    --spec-config estimation_spec_AC2013.yaml \\")
        print("    --group joint \\")
        print("    --output-dir outputs/AC2013_test \\")
        print("    --verbose")
        print()
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
