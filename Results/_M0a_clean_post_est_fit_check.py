"""Fast post-estimation fit-diagnostic check for ruro_occ_M0a_clean.

Calls compute_fit_diagnostics_from_data on the existing M0a-clean run JSON
after the post-estimation reporting patch. No re-estimation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "enhanced"))

from RURO_post_estimation_styled import (  # noqa: E402
    compute_fit_diagnostics_from_data,
    load_estimation_results_from_json,
)
from estimation_spec_parser import parse_specification  # noqa: E402

RESULTS = REPO_ROOT / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy" / \
    "estimation_spec_ruro_occ_M0a_clean" / "run_2026-05-13_19-24-38" / "estimation_results.json"
SPEC = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0a_clean.yaml"
MNL_BASE = Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl")

parsed, data = load_estimation_results_from_json(RESULTS)
spec = parse_specification(SPEC)

fit = compute_fit_diagnostics_from_data(parsed, MNL_BASE, spec=spec)

print("\n=== POST-PATCH fit diagnostics (M0a-clean) ===")
for k, v in fit.items():
    print(f"\n[{k}]")
    print(f"  participation_observed  = {v.get('participation_observed'):.4f}")
    pp = v.get('participation_predicted')
    print(f"  participation_predicted = {pp:.4f}" if pp == pp else "  participation_predicted = nan")
    print(f"  mean_hours_observed     = {v.get('mean_hours_observed'):.2f}")
    mh = v.get('mean_hours_predicted')
    print(f"  mean_hours_predicted    = {mh:.2f}" if mh == mh else "  mean_hours_predicted    = nan")

out = REPO_ROOT / "Results" / "_M0a_clean_post_est_fit_check.json"
serial = {
    g: {kk: (float(vv) if hasattr(vv, '__float__') and not isinstance(vv, dict) else vv)
        for kk, vv in row.items() if not isinstance(vv, dict)}
    for g, row in fit.items()
}
out.write_text(json.dumps(serial, indent=2))
print(f"\nWrote {out}")
