"""
Stage Two — Increment Two-D runner: bounded node-pricing EUROMOD re-simulation
FEASIBILITY probe. Existing nodes only; prices no redrawn node; computes no V_i^dir;
runs no 2x/4x growth; writes no parquet. No W^3 welfare finding; no measure beyond W^3.

Materially different from the Two-B reprice: EUROMOD input is built from the
PRECOMPUTE-LONG source with ROSTER-COMPLETE household selection (Two-B read priced
rows with head(N), which can truncate a multi-person household's roster at a draw
boundary, making EUROMOD compute household-level benefits against an incomplete
household). See welfare_resim_probe.py docstring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import welfare_core as wc  # noqa: E402
import welfare_resim_probe as wr  # noqa: E402


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]

    # Process-level capture around the whole grid: the native EUROMOD engine writes
    # its assessment-unit (TUDef) warnings to the process CONSOLE bound to fd 1
    # (stdout), not fd 2 -- a per-cell in-Python fd-2 redirect misses them entirely
    # (it returned 0 while 114 warnings fired). Redirect BOTH fd 1 and fd 2 to the log
    # around the grid; all runner print() summaries happen AFTER the grid, outside the
    # capture window. Persisted log + JSON make the warning evidence reproducible
    # (OBSERVED signal, NOT a proven root cause).
    import os
    import re
    import tempfile
    em_log = Path(args.out_json).with_name("stage2_resim_euromod_console.log")
    em_log.parent.mkdir(parents=True, exist_ok=True)
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd-redirect lifecycle)
    _saved_out, _saved_err = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        grid = wr.resim_grid(cfg2)
    finally:
        os.dup2(_saved_out, 1)
        os.dup2(_saved_err, 2)
        os.close(_saved_out)
        os.close(_saved_err)
        _tmp.seek(0)
        console_text = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console_text, encoding="utf-8")
    tudef_lines = [ln for ln in console_text.splitlines()
                   if "TUDef" in ln or "DefTu" in ln or "possible partner" in ln]
    tudef_units = sorted(set(re.findall(r"assessment unit '([^']+)'", console_text)))

    R = {"increment": "stage2_resim_feasibility_v1",
         "no_welfare_finding": True, "measures_touched": ["W3_only"],
         "no_production_pricing": True,
         "materially_different_from_two_b": (
             "YES: input from precompute-long (build's EUROMOD input source) with "
             "roster-complete household selection, vs Two-B reading priced rows with "
             "head(N) that can truncate a household roster at a draw boundary."),
         "assessment_unit_warning_evidence": {
             "process_level_capture": True,
             "tudef_partner_warning_lines": len(tudef_lines),
             "distinct_assessment_units": tudef_units,
             "sample_lines": tudef_lines[:3],
             "euromod_stderr_log": str(em_log),
             "interpretation_caveat": (
                 "OBSERVED signal, NOT a proven root cause: these warnings indicate "
                 "EUROMOD could not uniquely resolve some tax/assessment units for the "
                 "stamped multi-person rows; whether they fully explain the ils_ben "
                 "(singles) and ils_origy (couples) parity gaps is not proven here.")},
         "resim_grid": grid}

    # throughput projection from the tiny probe's measured wall-time per EUROMOD eval
    proj = cfg2["resim"]["projection"]
    walls = [c.get("euromod_wall_seconds") for c in R["resim_grid"]["cells"].values()
             if isinstance(c.get("euromod_wall_seconds"), (int, float))]
    rows = [c.get("n_euromod_input_rows") for c in R["resim_grid"]["cells"].values()
            if isinstance(c.get("n_euromod_input_rows"), (int, float))]
    per_row = (sum(walls) / sum(rows)) if walls and rows and sum(rows) else None
    total_hh = proj["singles_male_hh"] + proj["singles_female_hh"] + proj["couples_flagged_hh"]
    R["throughput"] = {
        "measured_wall_seconds_total_probe": round(sum(walls), 3) if walls else None,
        "measured_euromod_input_rows_total_probe": int(sum(rows)) if rows else None,
        "approx_seconds_per_input_row": (round(per_row, 6) if per_row else None),
        "designed_crosscheck_total_households": total_hh,
        "projection_note": (
            "EUROMOD prices PERSON-rows (roster), not household-draws; production "
            "node pricing must run one full-roster household-draw per node. The "
            "per-input-row figure is a wall-time BASIS only; it does not account for "
            "EUROMOD batch overhead, model load, or process spin-up, so it is a LOWER "
            "bound on per-node cost. No tractability threshold is configured -> "
            "projection reported, tractability NOT declared."),
        "projection_seconds": {}}
    if per_row is not None:
        for npn in proj["nodes_per_hh"]:
            # ~ (per-row sec) * (avg roster rows per node ~ from probe) * nodes * HH
            avg_roster = (sum(rows) / sum(c.get("n_decider_rows_matched", 1)
                          for c in R["resim_grid"]["cells"].values()
                          if isinstance(c.get("n_decider_rows_matched"), (int, float)))
                          if rows else 1.0)
            sec = per_row * avg_roster * npn * total_hh
            R["throughput"]["projection_seconds"][str(npn)] = {
                "nodes_per_hh": npn,
                "approx_euromod_input_rows": int(avg_roster * npn * total_hh),
                "approx_seconds": round(sec, 1),
                "approx_hours": round(sec / 3600.0, 2)}
        R["throughput"]["avg_roster_rows_per_node"] = round(avg_roster, 3)

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(R, f, indent=2, default=float)
    print(f"[stage2:resim] wrote {args.out_json}")
    print(f"  all cells pass: {R['resim_grid']['all_cells_pass']}")
    for name, c in R["resim_grid"]["cells"].items():
        if c.get("status") == "BLOCKED":
            print(f"  {name}: BLOCKED ({c.get('reason')})")
            continue
        cd = c.get("component_divergence", {})
        ben = cd.get("ils_ben", {})
        line = (f"  {name}: {c['status']} roster_complete={c.get('roster_complete')} "
                f"dispy max={c['ils_dispy']['max_abs_diff']:.3f} bad={c['ils_dispy']['n_rows_above_tol']} "
                f"| ils_ben max={ben.get('max_abs', float('nan')):.3f} bad={ben.get('n_above_tol')}")
        if c.get("failure_localised_to"):
            line += f" | localised={c['failure_localised_to']}"
        print(line)


if __name__ == "__main__":
    main()
