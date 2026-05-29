"""Dump theta* (the synthetic-recovery true vector) to JSON / CSV for use
as --init-params on a real-data estimation run.

This makes the multi-basin hypothesis testable on REAL chosen data: feed
the same starting vector to both CONOPT and scipy L-BFGS-B; if scipy traps
far from CONOPT on real data too, multi-basin is structural, not synthetic.

Output format is chosen by the --out file extension:
  - .csv  -> parameter,value rows (consumable by enh_RURO_estimate_FR --init-params)
  - .json -> {param_names: [...], theta: [...]} (also consumable)

Usage:
  python scripts/bpool/dump_theta_star.py \
      --spec scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml \
      --seed 20260527 \
      --out theta_star_bpool_p3a_v1_seed20260527.csv
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
    ap.add_argument("--out", required=True, help="Output path (.csv or .json)")
    args = ap.parse_args()

    spec = parse_specification(Path(args.spec))
    rng = np.random.default_rng(args.seed)
    theta_star = recovery_test.generate_theta_star(spec, rng)
    pnames = spec.all_param_names
    assert len(pnames) == len(theta_star), f"len mismatch: {len(pnames)} vs {len(theta_star)}"

    out_path = Path(args.out)
    if out_path.suffix.lower() == ".csv":
        import csv
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["parameter", "value"])
            for n, v in zip(pnames, theta_star):
                w.writerow([n, float(v)])
    elif out_path.suffix.lower() == ".json":
        payload = {"param_names": list(pnames), "theta": [float(v) for v in theta_star]}
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        raise SystemExit(f"Unsupported extension {out_path.suffix}; use .csv or .json")

    print(f"Wrote {len(pnames)} params -> {out_path}")
    print(f"  first 5: {dict(zip(pnames[:5], theta_star[:5]))}")


if __name__ == "__main__":
    main()
