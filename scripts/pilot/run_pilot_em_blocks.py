#!/usr/bin/env python
"""
NC pilot — Stage 5 v2 driver: run EUROMOD for blocks f=lo..hi sequentially.

Authorized by docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage5_strategy_amendment_v2.md §22 STEP 5
("Blocks f=1..29 (only after checkpoint)").

This driver:
  1. For each block f in [lo, hi], builds the adapter input (via
     scripts/pilot/export_pilot_euromod_inputs_v2.py --block-f f).
  2. Launches the production EUROMOD runner on the block input.
  3. Verifies the runner exit code and the output combined_draws_em.parquet
     presence.
  4. Skips blocks whose output already exists (per-block checkpoint per §14).

NOT executed: the post-EUROMOD merge, GSUR, precompute, estimation, welfare,
SA2, promotion, M1-clean displacement. Production runner not modified.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# Data lives under the configured storage root, not the repo working tree (migrated 2026-05-26).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from path_helpers import data_root, euromod_root  # noqa: E402
ADAPTER = REPO / "scripts" / "pilot" / "export_pilot_euromod_inputs_v2.py"
RUNNER = REPO / "scripts" / "enhanced" / "enh_RURO_euromod.py"
PYTHON = REPO / ".venv" / "Scripts" / "python.exe"
PILOT = data_root() / "pilot" / "nc_2016_couples"
EM_IN = PILOT / "em_inputs"
EM_OUT = PILOT / "em_outputs"
MICRO = data_root() / "raw" / "FR_2016.txt"
EM_ROOT = euromod_root()


def run_block(f: int) -> dict:
    """Run one block; return a status dict."""
    block_in_dir = EM_IN / f"block_f{f:02d}"
    block_out_dir = EM_OUT / f"block_f{f:02d}"
    block_in_dir.mkdir(parents=True, exist_ok=True)
    block_out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = block_out_dir / "combined_draws_em.parquet"

    if out_parquet.exists():
        print(f"[blocks] f={f:02d}: output already exists, skipping ({out_parquet.stat().st_size:,} bytes)")
        return {"f": f, "skipped": True, "exit_adapter": None, "exit_runner": None,
                "wall_sec": 0.0, "output_bytes": out_parquet.stat().st_size}

    # Build adapter input
    print(f"\n=== BLOCK f={f:02d} ===")
    t0 = time.time()
    adp_cmd = [str(PYTHON), str(ADAPTER), "--block-f", str(f)]
    print(f"[blocks] adapter: {' '.join(adp_cmd)}")
    rc_adp = subprocess.call(adp_cmd)
    t_adp = time.time() - t0
    print(f"[blocks] adapter f={f:02d} exit={rc_adp}, {t_adp:.1f}s")
    if rc_adp != 0:
        return {"f": f, "exit_adapter": rc_adp, "exit_runner": None,
                "wall_sec": t_adp, "adapter_failed": True}

    # Launch EUROMOD pass
    log_path = block_out_dir / "run.log"
    env = os.environ.copy()
    env["PYTHONNET_RUNTIME"] = "coreclr"
    env["PYTHONUNBUFFERED"] = "1"
    runner_cmd = [
        str(PYTHON), str(RUNNER),
        "--singles-draws", str(block_in_dir / f"fr_pilot_2016_couples_block_f{f:02d}_draws.parquet"),
        "--microdata-template", str(MICRO),
        "--euromod-root", str(EM_ROOT),
        "--euromod-system", "FR_2015",
        "--euromod-dataset", "FR_2016",
        "--scenario-dir", str(block_out_dir),
    ]
    print(f"[blocks] runner: " + " ".join(f'"{x}"' if " " in x else x for x in runner_cmd))
    t1 = time.time()
    with log_path.open("w", encoding="utf-8") as logf:
        rc_run = subprocess.call(runner_cmd, stdout=logf, stderr=subprocess.STDOUT, env=env)
    t_run = time.time() - t1
    output_ok = out_parquet.exists()
    output_bytes = out_parquet.stat().st_size if output_ok else 0
    print(f"[blocks] runner f={f:02d} exit={rc_run}, {t_run:.1f}s, output_ok={output_ok}, bytes={output_bytes:,}")
    return {"f": f, "exit_adapter": rc_adp, "exit_runner": rc_run,
            "wall_sec": t_adp + t_run, "adapter_sec": t_adp, "runner_sec": t_run,
            "output_bytes": output_bytes, "output_ok": output_ok}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lo", type=int, required=True, help="First block index (inclusive)")
    ap.add_argument("--hi", type=int, required=True, help="Last block index (inclusive)")
    args = ap.parse_args()
    results = []
    overall_start = time.time()
    for f in range(args.lo, args.hi + 1):
        status = run_block(f)
        results.append(status)
        if not status.get("skipped") and (status.get("exit_runner") != 0 or not status.get("output_ok")):
            print(f"[blocks] BLOCK f={f:02d} FAILED; stopping sweep.", file=sys.stderr)
            break
    overall = time.time() - overall_start
    # Write a summary JSON
    summary_path = EM_OUT / f"sweep_summary_f{args.lo:02d}_to_f{args.hi:02d}.json"
    with summary_path.open("w", encoding="utf-8") as fjs:
        json.dump({"lo": args.lo, "hi": args.hi, "overall_wall_sec": overall,
                   "blocks": results}, fjs, indent=2)
    print(f"\n[blocks] DONE. summary: {summary_path}; overall {overall:.1f}s")
    # Exit code: 0 only if every block ran and outputted
    bad = [r for r in results if not r.get("skipped") and not r.get("output_ok")]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
