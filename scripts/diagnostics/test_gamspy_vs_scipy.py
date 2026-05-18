#!/usr/bin/env python
"""
==============================================================================
Phase 5 Test: GAMSPy vs SciPy Comparison
==============================================================================
Compare GAMSPy estimation results against SciPy baseline.

Expected results:
- GAMSPy LL ≈ -5148 (same as SciPy)
- Parameters match SciPy (within 1-2%)
- GAMSPy faster (< 5 minutes vs 20 minutes for SciPy)

Usage:
    python test_gamspy_vs_scipy.py

Author: Phase 5 Testing
Created: 2026-01-17
==============================================================================
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_scipy_baseline(baseline_path: Path) -> dict:
    """Load SciPy baseline results for comparison."""
    logger.info(f"Loading SciPy baseline from: {baseline_path}")

    with open(baseline_path) as f:
        data = json.load(f)

    # Extract joint estimation results
    if 'joint' in data['results']:
        result = data['results']['joint']
        return {
            'll': result['final_ll'],
            'parameters': result['parameters'],
            'theta': np.array(result['theta']),
            'walltime': result['walltime_seconds'],
            'n_iterations': result['n_iterations'],
        }
    else:
        raise ValueError("No joint estimation results found in baseline")


def load_gamspy_results(gamspy_path: Path) -> dict:
    """Load GAMSPy results."""
    logger.info(f"Loading GAMSPy results from: {gamspy_path}")

    with open(gamspy_path) as f:
        data = json.load(f)

    # Extract joint estimation results
    if 'joint' in data['results']:
        result = data['results']['joint']
        return {
            'll': result['final_ll'],
            'parameters': result['parameters'],
            'theta': np.array(result['theta']),
            'walltime': result['walltime_seconds'],
            'n_iterations': result['n_iterations'],
        }
    else:
        raise ValueError("No joint estimation results found in GAMSPy output")


def compare_results(scipy_res: dict, gamspy_res: dict, spec_path: Path) -> dict:
    """
    Compare SciPy and GAMSPy results.

    Returns
    -------
    dict with comparison metrics:
        - ll_diff: Difference in log-likelihood
        - ll_pct_diff: Percentage difference
        - param_diffs: Parameter-wise differences
        - max_param_diff: Maximum absolute difference
        - max_param_pct_diff: Maximum percentage difference
        - speedup: GAMSPy speedup factor
        - all_params_match: True if all params within 2%
    """
    logger.info("")
    logger.info("="*80)
    logger.info("COMPARISON: GAMSPy vs SciPy")
    logger.info("="*80)

    # Log-likelihood comparison
    ll_diff = gamspy_res['ll'] - scipy_res['ll']
    ll_pct_diff = (ll_diff / abs(scipy_res['ll'])) * 100

    logger.info(f"\n1. LOG-LIKELIHOOD COMPARISON")
    logger.info(f"   SciPy  LL: {scipy_res['ll']:.6f}")
    logger.info(f"   GAMSPy LL: {gamspy_res['ll']:.6f}")
    logger.info(f"   Difference: {ll_diff:.6f} ({ll_pct_diff:+.4f}%)")

    if abs(ll_diff) <= 2.0:
        logger.info(f"   ✓ PASS: LL within 2 units")
    else:
        logger.warning(f"   ✗ FAIL: LL difference > 2 units!")

    # Parameter comparison
    logger.info(f"\n2. PARAMETER COMPARISON")
    logger.info(f"   Total parameters: {len(scipy_res['theta'])}")

    param_diffs = {}
    param_pct_diffs = {}

    for param_name in scipy_res['parameters'].keys():
        scipy_val = scipy_res['parameters'][param_name]
        gamspy_val = gamspy_res['parameters'].get(param_name, np.nan)

        diff = gamspy_val - scipy_val

        # Percentage difference (handle divide by zero)
        if abs(scipy_val) > 1e-6:
            pct_diff = (diff / scipy_val) * 100
        else:
            pct_diff = np.nan if diff == 0 else np.inf

        param_diffs[param_name] = diff
        param_pct_diffs[param_name] = pct_diff

    # Find largest differences
    abs_diffs = {k: abs(v) for k, v in param_diffs.items() if not np.isnan(v)}
    abs_pct_diffs = {k: abs(v) for k, v in param_pct_diffs.items()
                     if not np.isnan(v) and not np.isinf(v)}

    max_param_name = max(abs_diffs.keys(), key=lambda k: abs_diffs[k])
    max_pct_param_name = max(abs_pct_diffs.keys(), key=lambda k: abs_pct_diffs[k])

    max_diff = param_diffs[max_param_name]
    max_pct_diff = param_pct_diffs[max_pct_param_name]

    logger.info(f"   Max absolute diff: {max_diff:+.6f} ({max_param_name})")
    logger.info(f"   Max % diff: {max_pct_diff:+.2f}% ({max_pct_param_name})")

    # Check how many parameters are within 2%
    n_within_2pct = sum(1 for pct in abs_pct_diffs.values() if pct <= 2.0)
    n_total = len(abs_pct_diffs)
    pct_within_2pct = (n_within_2pct / n_total) * 100

    logger.info(f"   Parameters within 2%: {n_within_2pct}/{n_total} ({pct_within_2pct:.1f}%)")

    all_params_match = (n_within_2pct == n_total)

    if all_params_match:
        logger.info(f"   ✓ PASS: All parameters within 2%")
    else:
        logger.warning(f"   ✗ PARTIAL: {n_total - n_within_2pct} parameters exceed 2% difference")

    # Timing comparison
    logger.info(f"\n3. TIMING COMPARISON")
    logger.info(f"   SciPy walltime:  {scipy_res['walltime']:.1f} sec ({scipy_res['walltime']/60:.1f} min)")
    logger.info(f"   GAMSPy walltime: {gamspy_res['walltime']:.1f} sec ({gamspy_res['walltime']/60:.1f} min)")

    speedup = scipy_res['walltime'] / gamspy_res['walltime']
    logger.info(f"   Speedup: {speedup:.2f}x")

    if speedup >= 3.0:
        logger.info(f"   ✓ EXCELLENT: GAMSPy is {speedup:.1f}x faster!")
    elif speedup >= 1.5:
        logger.info(f"   ✓ GOOD: GAMSPy is {speedup:.1f}x faster")
    else:
        logger.warning(f"   ✗ SLOW: GAMSPy only {speedup:.1f}x faster (expected 3-10x)")

    # Convergence comparison
    logger.info(f"\n4. CONVERGENCE COMPARISON")
    logger.info(f"   SciPy iterations:  {scipy_res['n_iterations']}")
    logger.info(f"   GAMSPy iterations: {gamspy_res['n_iterations']}")

    # Overall assessment
    logger.info(f"\n" + "="*80)
    logger.info("OVERALL ASSESSMENT")
    logger.info("="*80)

    checks = []

    # Check 1: LL within 2 units
    ll_check = abs(ll_diff) <= 2.0
    checks.append(ll_check)
    logger.info(f"  {'✓' if ll_check else '✗'} Log-likelihood within 2 units: {ll_check}")

    # Check 2: All parameters within 2%
    checks.append(all_params_match)
    logger.info(f"  {'✓' if all_params_match else '✗'} All parameters within 2%: {all_params_match}")

    # Check 3: GAMSPy faster
    speed_check = speedup > 1.0
    checks.append(speed_check)
    logger.info(f"  {'✓' if speed_check else '✗'} GAMSPy faster than SciPy: {speed_check}")

    all_pass = all(checks)

    logger.info(f"\n{'='*80}")
    if all_pass:
        logger.info("RESULT: ✓ ALL CHECKS PASSED - GAMSPy matches SciPy!")
    else:
        logger.warning("RESULT: ✗ SOME CHECKS FAILED - Review differences above")
    logger.info(f"{'='*80}\n")

    return {
        'll_diff': ll_diff,
        'll_pct_diff': ll_pct_diff,
        'param_diffs': param_diffs,
        'param_pct_diffs': param_pct_diffs,
        'max_param_diff': max_diff,
        'max_param_pct_diff': max_pct_diff,
        'speedup': speedup,
        'all_params_match': all_params_match,
        'checks_passed': all_pass,
    }


def save_comparison_report(comparison: dict, scipy_res: dict, gamspy_res: dict,
                           output_path: Path):
    """Save detailed comparison report to CSV."""
    logger.info(f"Saving comparison report to: {output_path}")

    rows = []
    for param_name in sorted(scipy_res['parameters'].keys()):
        scipy_val = scipy_res['parameters'][param_name]
        gamspy_val = gamspy_res['parameters'].get(param_name, np.nan)
        diff = comparison['param_diffs'][param_name]
        pct_diff = comparison['param_pct_diffs'][param_name]

        rows.append({
            'parameter': param_name,
            'scipy_value': scipy_val,
            'gamspy_value': gamspy_val,
            'absolute_diff': diff,
            'percent_diff': pct_diff,
            'within_2pct': abs(pct_diff) <= 2.0 if not np.isnan(pct_diff) else False,
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Comparison report saved")


def main():
    """Main test routine."""
    logger.info("="*80)
    logger.info("PHASE 5 TEST: GAMSPy vs SciPy Comparison")
    logger.info("="*80)
    logger.info(f"Started: {datetime.now().isoformat()}\n")

    # Paths
    baseline_path = Path("outputs/estimates/fr/2016/estimation_results.json")
    gamspy_path = Path("outputs/estimates/fr/2016_gamspy/estimation_results.json")
    spec_path = Path("scripts/enhanced/specifications/estimation_spec.yaml")

    # Check files exist
    if not baseline_path.exists():
        logger.error(f"SciPy baseline not found: {baseline_path}")
        logger.error("Please run SciPy estimation first:")
        logger.error("  python scripts/enhanced/enh_RURO_estimate_FR.py \\")
        logger.error("    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl \\")
        logger.error("    --output-dir outputs/estimates/fr/2016 \\")
        logger.error("    --group joint --solver scipy")
        return 1

    if not gamspy_path.exists():
        logger.error(f"GAMSPy results not found: {gamspy_path}")
        logger.error("Please run GAMSPy estimation first:")
        logger.error("  python scripts/enhanced/enh_RURO_estimate_FR.py \\")
        logger.error("    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl \\")
        logger.error("    --output-dir outputs/estimates/fr/2016_gamspy \\")
        logger.error("    --group joint --solver gamspy-conopt")
        return 1

    # Load results
    try:
        scipy_res = load_scipy_baseline(baseline_path)
        gamspy_res = load_gamspy_results(gamspy_path)
    except Exception as e:
        logger.error(f"Failed to load results: {e}")
        return 1

    # Compare
    comparison = compare_results(scipy_res, gamspy_res, spec_path)

    # Save detailed report
    output_dir = Path("outputs/estimates/fr/2016_gamspy")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "comparison_gamspy_vs_scipy.csv"
    save_comparison_report(comparison, scipy_res, gamspy_res, report_path)

    logger.info(f"\nTest completed: {datetime.now().isoformat()}")

    return 0 if comparison['checks_passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
