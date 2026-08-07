"""
JMP-M08 Stage-B parity gate — runner.

Binds the committed hash-pinned P2a pricing cache, rebuilds the production pricing
path, reprices each production chunk at production batch geometry, and compares
repriced vs stored ``ils_dispy`` at the frozen 1e-6 EUR tolerance.

    python scripts/welfare/run_m08_p2a_parity_gate.py \
        --config scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml \
        --chunks 0                 # bounded smoke (one chunk)
    python scripts/welfare/run_m08_p2a_parity_gate.py \
        --config scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml \
        --chunks all               # full run, chunk-sequential

VERDICT RULE (tightened by the M08 production-path review, T4). PASS = on EVERY
chunk, zero rows above 1e-6 EUR on the gate column AND zero non-finite values on
both the stored and the repriced side of the gate column AND no EUROMOD hard
error. A non-finite value is treated as an infinite difference, so it cannot be
masked out of the tolerance test. Per-chunk and aggregate non-finite counts are
persisted for both sides of every gate and witness column, together with the
number of rows actually compared. Any failing row is classified and reported;
the runner does not repair.

Writes only under ``<output.root>/attempts/<attempt_id>_<STATUS>`` via the Phases
3-5 transaction pattern (lock -> staging -> atomic rename). ``complete/`` is never
created or promoted here. No production pricing code, config, or stored value is
modified.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))

import m08_p2a_parity as mp  # noqa: E402


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class GateTransaction:
    """Lock + staging + attempts. NEVER creates or promotes complete/."""

    def __init__(self, root: Path, label: str = "parity"):
        self.root, self.label = Path(root), str(label)
        self.lock = self.root / ".welfare_m08.lock"
        self.staging_base = self.root / ".staging"
        self.attempts = self.root / "attempts"
        self.attempt_id: Optional[str] = None
        self.staging: Optional[Path] = None
        self._locked = False

    def acquire(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise mp.GateStop("HP-TXN", "lock",
                              f"another M08 gate run holds {self.lock.name}") from None
        os.close(fd)
        self._locked = True
        self.attempts.mkdir(exist_ok=True)
        self.staging_base.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.attempt_id = f"{stamp}_{os.getpid()}_{uuid.uuid4().hex}_{self.label}"
        self.staging = self.staging_base / self.attempt_id
        self.staging.mkdir(parents=True, exist_ok=False)
        self.lock.write_text(json.dumps({"pid": os.getpid(), "utc": _utcnow(),
                                         "attempt": self.attempt_id}), encoding="utf-8")

    def finish(self, status: str) -> Path:
        assert self.staging is not None and self.attempt_id is not None
        dest = self.attempts / f"{self.attempt_id}_{status}"
        os.replace(self.staging, dest)
        return dest

    def release(self) -> None:
        if self._locked and self.lock.is_file():
            self.lock.unlink()
            self._locked = False


def _write_json(obj: Any, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, default=str)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--chunks", default="0",
                    help="'all', or a comma-separated list of chunk start offsets")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    import yaml

    repo = _THIS.parent.parent.parent
    cfg = yaml.safe_load((repo / args.config).read_text(encoding="utf-8")
                         if not Path(args.config).is_absolute()
                         else Path(args.config).read_text(encoding="utf-8"))

    root = repo / cfg["output"]["root"]
    label = args.label or cfg["output"].get("label", "parity")
    txn = GateTransaction(root, label)
    txn.acquire()
    staging = txn.staging
    assert staging is not None

    manifest: Dict[str, Any] = {
        "gate": cfg["gate"]["name"],
        "cell": cfg["gate"]["cell"],
        "tol_eur": float(cfg["gate"]["tol_eur"]),
        "attempt_id": txn.attempt_id,
        "started_utc": _utcnow(),
        "config": args.config,
        "config_sha256": mp.sha256_file(repo / args.config),
        "runner_sha256": mp.sha256_file(_THIS),
        "library_sha256": mp.sha256_file(_THIS.parent / "m08_p2a_parity.py"),
        "certification_standard": mp.CERTIFICATION_STANDARD,
        "scope": ("reprice-parity validation of the committed P2a pricing cache; "
                  "no redrawn node, no counterfactual, no welfare number, no "
                  "production pricing-code change, no stored value modified"),
    }
    status = "STOPPED"
    recon_log: List[str] = []
    try:
        print(f"[m08:gate] attempt {txn.attempt_id}")

        # (a) bind + verify the artifact
        print("[m08:gate] verifying committed pricing-cache pins ...")
        manifest["artifact_binding"] = mp.verify_pricing_cache_pins(repo, cfg)
        manifest["frozen_inputs"] = mp.verify_frozen_inputs(repo, cfg)
        print(f"  {len(manifest['artifact_binding']['chunks'])} chunk pins verified; "
              f"{manifest['artifact_binding']['observed_rows_total']} rows, "
              f"{manifest['artifact_binding']['observed_hh']} households")
        _write_json(manifest, staging / "gate_manifest.json")

        # (b) rebuild the production pricing path
        print("[m08:gate] reconstructing production pricing path ...")
        t0 = time.time()
        ns = mp.reconstruct_pipeline(repo, cfg, staging, log=recon_log)
        manifest["reconstruction"] = {
            "notebook": cfg["geometry"]["notebook"],
            "cells": list(cfg["geometry"]["reconstruct_cells"]),
            "seconds": round(time.time() - t0, 1),
            "chunk_size": int(ns["CHUNK"]),
            "n_households": int(len(ns["hh_all"])),
            "euromod": {"country": ns["FR_COUNTRY"], "system": ns["FR_SYSTEM"],
                        "dataset": ns["FR_DATASET"],
                        "weeks_per_month": float(ns["WEEKS_PER_MONTH"])},
        }
        manifest["geometry_check"] = mp.verify_reconstructed_geometry(ns, repo, cfg)
        print(f"  rebuilt in {manifest['reconstruction']['seconds']}s; "
              f"draws match frozen geometry: "
              f"{manifest['geometry_check'].get('matches_frozen_geometry')}")
        (staging / "reconstruction_log.txt").write_text(
            "\n".join(recon_log), encoding="utf-8")
        _write_json(manifest, staging / "gate_manifest.json")

        # (c) reprice + compare, chunk-sequential with intermediate persistence
        grid = list(manifest["artifact_binding"]["chunk_grid"])
        if str(args.chunks).strip().lower() == "all":
            chunks = grid
        else:
            chunks = [int(x) for x in str(args.chunks).split(",") if x.strip() != ""]
            bad = [c for c in chunks if c not in grid]
            if bad:
                raise mp.GateStop("HP-ARG", "chunks", f"not on the chunk grid: {bad}")
        manifest["run"] = {"requested_chunks": chunks, "chunk_grid": grid,
                           "is_full_run": chunks == grid}

        alt = mp._alternatives(ns)
        results: List[Dict[str, Any]] = []
        failing_frames = []
        import pandas as pd

        for i, start in enumerate(chunks, 1):
            print(f"[m08:gate] chunk {i}/{len(chunks)} priced_{start:05d} ...")
            r = mp.reprice_chunk(ns, cfg, chunk_start=start, repo=repo, alt=alt)
            fr = r.pop("_failing_rows")
            if fr is not None and len(fr):
                failing_frames.append(fr)
                fr.to_csv(staging / f"failing_rows_priced_{start:05d}.csv", index=False)
            results.append(r)
            gate_col = cfg["comparison"]["gate_columns"][0]
            gs = r["column_summary"][gate_col]
            fin = r["finiteness"]
            print(f"  {r['status']}  hh={r['households_in_batch']} "
                  f"cmp={r['n_rows_compared']}/{r['stored_rows']} "
                  f"{gate_col} max={gs['max_abs_diff']:.3e} "
                  f"bad={r['n_rows_above_tol']} "
                  f"nonfin(gate s/r)={fin['n_nonfinite_gate_stored']}/"
                  f"{fin['n_nonfinite_gate_repriced']} "
                  f"nonfin(wit s/r)={fin['n_nonfinite_witness_stored']}/"
                  f"{fin['n_nonfinite_witness_repriced']} "
                  f"({r['euromod_seconds']}s)")
            # intermediate persistence after EVERY chunk
            manifest["chunk_results"] = results
            _write_json(manifest, staging / "gate_manifest.json")
            _write_json(r, staging / f"chunk_priced_{start:05d}.json")

        # aggregate
        tol = float(cfg["gate"]["tol_eur"])
        gate_col = cfg["comparison"]["gate_columns"][0]
        n_bad = sum(r["n_rows_above_tol"] for r in results)
        n_rows = sum(r["stored_rows"] for r in results)
        n_cmp = sum(r["n_rows_compared"] for r in results)
        if n_cmp != n_rows:
            raise mp.GateStop("HP-CMP", "aggregate",
                              f"rows compared {n_cmp} != stored rows {n_rows}")
        max_abs = max(r["column_summary"][gate_col]["max_abs_diff"] for r in results)
        nf_gate_s = sum(r["finiteness"]["n_nonfinite_gate_stored"] for r in results)
        nf_gate_r = sum(r["finiteness"]["n_nonfinite_gate_repriced"] for r in results)
        nf_gate_rows = sum(r["n_rows_nonfinite_gate"] for r in results)
        nf_wit_s = sum(r["finiteness"]["n_nonfinite_witness_stored"] for r in results)
        nf_wit_r = sum(r["finiteness"]["n_nonfinite_witness_repriced"] for r in results)
        agg = {
            "chunks_run": len(results),
            "chunks_on_grid": len(grid),
            "is_full_run": bool(manifest["run"]["is_full_run"]),
            "rows_compared": n_rows,
            "rows_compared_from_chunks": n_cmp,
            "rows_compared_equals_stored_rows": n_cmp == n_rows,
            "gate_column": gate_col,
            "tol_eur": tol,
            f"{gate_col}_max_abs_diff": max_abs,
            "rows_above_tol": n_bad,
            # finiteness certification (T4)
            "gate_nonfinite_stored": nf_gate_s,
            "gate_nonfinite_repriced": nf_gate_r,
            "rows_with_nonfinite_gate_value": nf_gate_rows,
            "all_gate_values_finite_both_sides": (nf_gate_s == 0 and nf_gate_r == 0
                                                  and nf_gate_rows == 0),
            "chunks_with_nonfinite_gate_value": [
                r["chunk"] for r in results if r["n_rows_nonfinite_gate"]],
            "witness_nonfinite_stored": nf_wit_s,
            "witness_nonfinite_repriced": nf_wit_r,
            "witness_nonfiniteness_gates": False,
            "chunks_failing": [r["chunk"] for r in results if r["status"] != "PASS"],
            "euromod_seconds_total": round(
                sum(r["euromod_seconds"] for r in results), 1),
        }
        for wit in cfg["comparison"]["witness_columns"]:
            vals = [r["column_summary"][wit] for r in results if wit in r["column_summary"]]
            if vals:
                agg[f"{wit}_max_abs_diff"] = max(v["max_abs_diff"] for v in vals)
                agg[f"{wit}_rows_above_tol"] = sum(v["n_rows_above_tol"] for v in vals)
                agg[f"{wit}_nonfinite_stored"] = sum(v["n_nonfinite_stored"] for v in vals)
                agg[f"{wit}_nonfinite_repriced"] = sum(
                    v["n_nonfinite_repriced"] for v in vals)
        # tightened rule: tolerance AND finiteness, on every chunk
        verdict = ("PASS" if (all(r["status"] == "PASS" for r in results)
                              and n_bad == 0 and nf_gate_rows == 0
                              and nf_gate_s == 0 and nf_gate_r == 0)
                   else "FAIL")
        agg["verdict"] = verdict
        agg["certification_standard"] = mp.CERTIFICATION_STANDARD
        manifest["aggregate"] = agg
        manifest["finished_utc"] = _utcnow()

        if failing_frames:
            pd.concat(failing_frames, ignore_index=True).to_csv(
                staging / "failing_rows_all.csv", index=False)

        _write_json(manifest, staging / "gate_manifest.json")
        status = ("PARITY_PASS" if verdict == "PASS" else "PARITY_FAIL") + (
            "_FULL" if manifest["run"]["is_full_run"] else "_SMOKE")
        print(f"\n[m08:gate] VERDICT {verdict} | rows_compared={n_cmp}/{n_rows} "
              f"above_tol={n_bad} max={max_abs:.3e} EUR (tol {tol:g}) | "
              f"gate non-finite stored={nf_gate_s} repriced={nf_gate_r} "
              f"rows={nf_gate_rows} | witness non-finite stored={nf_wit_s} "
              f"repriced={nf_wit_r}")
        return 0 if verdict == "PASS" else 1

    except mp.GateStop as stop:
        manifest["halt"] = {"code": stop.code, "where": stop.where,
                            "detail": stop.detail, "utc": _utcnow()}
        _write_json(manifest, staging / "gate_manifest.json")
        if recon_log:
            (staging / "reconstruction_log.txt").write_text(
                "\n".join(recon_log), encoding="utf-8")
        status = f"STOPPED_{stop.code.replace('-', '_')}"
        print(f"\n[m08:gate] HALT {stop}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - recorded, then re-raised context
        manifest["halt"] = {"code": "HP-UNEXPECTED", "where": type(exc).__name__,
                            "detail": str(exc), "utc": _utcnow()}
        _write_json(manifest, staging / "gate_manifest.json")
        if recon_log:
            (staging / "reconstruction_log.txt").write_text(
                "\n".join(recon_log), encoding="utf-8")
        status = "STOPPED_UNEXPECTED"
        raise
    finally:
        dest = txn.finish(status)
        txn.release()
        print(f"[m08:gate] published -> {dest.relative_to(repo)}")


if __name__ == "__main__":
    raise SystemExit(main())
