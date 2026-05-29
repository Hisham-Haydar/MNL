"""Dump theta* (the synthetic-recovery true vector) to JSON for use as
init-params on a real-data estimation run.

This makes the multi-basin hypothesis testable on REAL chosen data: feed
the same starting vector to both CONOPT and scipy L-BFGS-B; if scipy traps
far from CONOPT on real data too, multi-basin is structural, not synthetic.

Usage:
  python scripts/bpool/dump_theta_star.py \
      --spec scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml \
      --seed 20260527 \
      --out theta_star_bpool_p3a_v1_seed20260527.json
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "enhanced"))

import recovery_test  # noqa: E402  (script is in same dir)
from estimation_spec_parser import parse_specification  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to spec YAML")
    ap.add_argument("--seed", type=int, required=True, help="RNG seed (must match recovery test for reproducibility)")
    ap.add_argument("--out", required=True, help="Output JSON path")
    args = ap.parse_args()

    spec = parse_specification(Path(args.spec))
    rng = np.random.default_rng(args.seed)
    theta_star = recovery_test.generate_theta_star(spec, rng)
    pnames = spec.all_param_names
    assert len(pnames) == len(theta_star), f"len mismatch: {len(pnames)} vs {len(theta_star)}"

    out = {n: float(v) for n, v in zip(pnames, theta_star)}
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} params -> {args.out}")
    print(f"  first 5: {dict(list(out.items())[:5])}")


if __name__ == "__main__":
    main()
