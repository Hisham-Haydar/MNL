"""
Stage Two — Increment Two-B runner: EUROMOD reprice parity grid.

Diagnoses-then-grids the v2 parity gap. The diagnosis (persisted separately in the
report + diagnostic CSV) found the divergence is localised to ils_ben (benefits) on
benefit-recipient households; ils_origy / ils_sicdy reproduce exactly. This runner
executes the deterministic parity grid over all production year x mode cells, with
EUROMOD output-component decomposition and (for couples) household-joint
disposable-income parity, and writes a provenance JSON.

Agnostic: stems/years/modes/tol from config; system pairing / CPI / schema / runner
from the build module; country derived from the system-code prefix (config override).

No W^3 welfare finding is produced; no measure beyond W^3 is touched. No production
redrawn-node pricing, no production V_i^dir, no 2x/4x growth.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))
import welfare_core as wc  # noqa: E402
import welfare_vdir as wv  # noqa: E402


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]

    R = {"increment": "stage2_parity_v1",
         "no_welfare_finding": True, "measures_touched": ["W3_only"],
         "scope": ("EUROMOD reprice parity diagnosis + grid; NO production node "
                   "pricing, NO production V_i^dir, NO 2x/4x growth."),
         "parity_grid": wv.parity_grid(cfg2, rows_csv_dir=cfg["output"]["dir"])}

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(R, f, indent=2, default=float)
    print(f"[stage2:parity] wrote {args.out_json}")
    print(f"  all cells pass: {R['parity_grid']['all_cells_pass']}")
    for name, c in R["parity_grid"]["cells"].items():
        if c.get("status") == "BLOCKED":
            print(f"  {name}: BLOCKED ({c.get('reason')})")
            continue
        ind = c["individual_ils_dispy"]
        line = (f"  {name}: {c['status']} n={c['n_rows']} hh={c['n_hh']} "
                f"max={ind['max_abs_diff']:.3f} med={ind['median_abs_diff']:.3f} "
                f"bad={ind['n_rows_above_tol']}")
        if "household_joint_dispy" in c:
            j = c["household_joint_dispy"]
            line += f" | joint max={j['max_abs_diff']:.3f} bad={j['n_above_tol']}"
        if c.get("failure_classification"):
            line += f" | {c['failure_classification']}"
        print(line)


if __name__ == "__main__":
    main()
