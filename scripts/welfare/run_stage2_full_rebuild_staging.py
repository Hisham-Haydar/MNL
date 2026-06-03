"""
Stage Two — Increment Two-N: full production rebuild to STAGING under the patched chunk
worker, at exact production chunk granularity. Gated on full-scale validation.

Runs the PATCHED scripts/bpool/run_bpool_euromod_chunk.py for every production chunk
(same year/mode cells, same chunk IDs, same draw bands, same system pairing + CPI) with
--staging-dir set, so outputs go ONLY to a clearly-marked staging directory and NEVER the
production path. Each chunk runs as its own subprocess so one aborting chunk does not kill
the run; per-chunk status / rows / wall are captured.

DOES NOT: swap/overwrite/move/delete any production parquet, re-estimate, compute V_i^dir,
price redrawn welfare nodes, promote W^3, or touch any measure beyond W^3.

Usage:
    python run_stage2_full_rebuild_staging.py --out-json <provenance.json> [--per-chunk-timeout SEC]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import pyarrow.parquet as pq  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_WORKER = Path("scripts/bpool/run_bpool_euromod_chunk.py").resolve()

# Exact production chunk manifest (from the production chunk meta JSONs):
#   singles: 1 chunk/year, draws [0,101)  (all 3 years have draws 0-100)
#   couples: 6 chunks/year, draw_joint bands of 150 over [0,900)
_COUPLES_BANDS = [(0, 150), (150, 300), (300, 450), (450, 600), (600, 750), (750, 900)]
_SINGLES_BANDS = [(0, 101)]


def _manifest(years):
    man = []
    for year in years:
        man.append({"year": year, "mode": "singles", "chunk_id": 0,
                    "draw_lo": _SINGLES_BANDS[0][0], "draw_hi": _SINGLES_BANDS[0][1]})
        for cid, (lo, hi) in enumerate(_COUPLES_BANDS):
            man.append({"year": year, "mode": "couples", "chunk_id": cid,
                        "draw_lo": lo, "draw_hi": hi})
    return man


_HEADLINE = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy", "ils_dispy_real"]


def _resolve_staging_or_refuse(base, staging_arg):
    """TASK 0 — production-write impossible on this entry point. The staging dir is a
    REQUIRED arg; this REFUSES (raises SystemExit) if the resolved path IS, or is INSIDE,
    the production chunks/ directory, or if it is the production new_data/ root, or if any
    production priced/chunk parquet would be reachable for overwrite. No production default
    is reachable through this driver."""
    if not staging_arg:
        raise SystemExit("REFUSE: --staging-dir is REQUIRED (no production default).")
    staging = Path(staging_arg).resolve()
    prod_chunks = (base / "chunks").resolve()
    prod_root = base.resolve()
    if staging == prod_chunks or prod_chunks in staging.parents:
        raise SystemExit(f"REFUSE: staging '{staging}' is/inside production chunks/ "
                         f"'{prod_chunks}'.")
    if staging == prod_root:
        raise SystemExit(f"REFUSE: staging '{staging}' is the production new_data/ root.")
    # never let an existing production parquet sit in the staging dir (would be overwritten)
    if staging.exists():
        for p in staging.glob("fr_p3a_bpool_priced__*.parquet"):
            # a same-named production priced/chunk file present in staging is a red flag
            if (prod_root / p.name).exists() and (prod_root / p.name).resolve() == p.resolve():
                raise SystemExit(f"REFUSE: staging contains a production parquet "
                                 f"reachable for overwrite: {p}")
    staging.mkdir(parents=True, exist_ok=True)
    return staging


def _stored_chunk_rows(base, year, mode, draw_lo, draw_hi):
    """Row count of the EXISTING production (assembled) priced file restricted to this
    chunk's draw band — for a rows-vs-production comparison."""
    draw_col = "draw" if mode == "singles" else "draw_joint"
    p = base / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    if not p.exists():
        return None
    t = pq.read_table(p, columns=[draw_col],
                      filters=[(draw_col, ">=", draw_lo), (draw_col, "<", draw_hi)])
    return int(t.num_rows)


def _chunk_coherence_selfcheck(parquet_path):
    """Per-chunk component-coherence self-check (for the completion marker): identity
    violations on decider rows. Cheap read of just the needed columns."""
    import pandas as pd
    cols = ["ruro_decider", "ils_ben", "ils_pen", "ils_benmt", "ils_bennt",
            "ils_dispy", "ils_origy", "ils_tax", "ils_sicdy"]
    have = [c for c in cols if c in pq.ParquetFile(parquet_path).schema_arrow.names]
    df = pd.read_parquet(parquet_path, columns=have)
    dec = df[df.get("ruro_decider", 1) == 1]
    out = {}
    if all(c in dec.columns for c in ["ils_ben", "ils_pen", "ils_benmt", "ils_bennt"]):
        r = (dec["ils_ben"] - (dec["ils_pen"] + dec["ils_benmt"] + dec["ils_bennt"])).abs()
        out["ils_ben_identity_violations"] = int((r > 1e-6).sum())
    if all(c in dec.columns for c in ["ils_dispy", "ils_origy", "ils_tax", "ils_sicdy", "ils_ben"]):
        r2 = (dec["ils_dispy"] - (dec["ils_origy"] - dec["ils_tax"] - dec["ils_sicdy"]
              + dec["ils_ben"])).abs()
        out["ils_dispy_identity_violations"] = int((r2 > 1e-6).sum())
    return out


def _inline_parity_sample(base, staging_parquet, year, mode, n_hh=20):
    """TASK 2 — inline fail-fast: sample decider-row headline of a freshly built staging
    chunk vs stored production. Returns per-column n_above_tol over the sampled rows."""
    import numpy as np
    import pandas as pd
    key = (["stacked_hh_uid", "draw", "idperson_true"] if mode == "singles"
           else ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female", "idperson_true"])
    cols = key + ["ruro_decider"] + _HEADLINE
    reb = pd.read_parquet(staging_parquet, columns=[c for c in cols
                          if c in pq.ParquetFile(staging_parquet).schema_arrow.names])
    reb = reb[reb.get("ruro_decider", 1) == 1]
    uids = reb["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist()
    reb = reb[reb["stacked_hh_uid"].isin(uids)]
    prod_path = base / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    pcols = [c for c in cols if c in pq.ParquetFile(prod_path).schema_arrow.names]
    prod = pd.read_parquet(prod_path, columns=pcols)
    prod = prod[(prod.get("ruro_decider", 1) == 1) & (prod["stacked_hh_uid"].isin(uids))]
    m = reb.merge(prod.drop_duplicates(key), on=key, how="inner", suffixes=("_reb", "_prod"))
    res = {}
    for c in _HEADLINE:
        if f"{c}_reb" in m.columns and f"{c}_prod" in m.columns:
            d = np.abs(pd.to_numeric(m[f"{c}_reb"], errors="coerce").to_numpy()
                       - pd.to_numeric(m[f"{c}_prod"], errors="coerce").to_numpy())
            res[c] = {"n_above_tol": int(np.sum(d > 1e-6)),
                      "max_abs": float(np.nanmax(d)) if len(d) else 0.0}
    return {"n_rows_sampled": int(len(m)), "per_column": res}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--staging-dir", required=True,
                    help="REQUIRED staging output dir; the driver REFUSES to run if this "
                         "is/inside the production chunks/ dir or the new_data/ root, or "
                         "would overwrite a production parquet (Task 0). Use a dated dir, "
                         "e.g. a 'rebuild_v2' sibling of chunks/.")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--per-chunk-timeout", type=int, default=14400,  # 4h per chunk cap
                    help="seconds before a single chunk subprocess is treated as timed out")
    args = ap.parse_args()

    base = bpool_dir()
    staging = _resolve_staging_or_refuse(base, args.staging_dir)   # TASK 0 safety gate
    years = [int(y) for y in args.years.split(",")]
    manifest = _manifest(years)

    results = []
    inline_parity = []
    run_start = time.time()
    for item in manifest:
        y, mode, cid = item["year"], item["mode"], item["chunk_id"]
        lo, hi = item["draw_lo"], item["draw_hi"]
        out_parquet = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
        marker = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.done.json"

        # TASK 1 resumability: skip if a valid parquet + completion marker already exist.
        if out_parquet.exists() and marker.exists():
            try:
                with open(marker) as f:
                    mk = json.load(f)
                if int(mk.get("row_count", -1)) == int(pq.ParquetFile(out_parquet).metadata.num_rows):
                    rec = {**item, "status": "SKIPPED_EXISTS", "reason": None,
                           "rebuilt_rows": mk.get("row_count"),
                           "stored_production_rows": mk.get("stored_production_rows"),
                           "rows_match": mk.get("rows_match"),
                           "wall_seconds": mk.get("euromod_wall_seconds"),
                           "coherence_selfcheck": mk.get("coherence_selfcheck"),
                           "staging_parquet": str(out_parquet)}
                    results.append(rec)
                    print(f"[two-N rebuild] {y} {mode} c{cid}: SKIPPED (valid marker)", flush=True)
                    # still record inline parity for the audit/fail-fast trail (cheap read)
                    try:
                        ip = _inline_parity_sample(base, out_parquet, y, mode)
                        ip.update({"year": y, "mode": mode, "chunk_id": cid, "from_skip": True})
                        inline_parity.append(ip)
                    except Exception as e:  # noqa: BLE001
                        inline_parity.append({"year": y, "mode": mode, "chunk_id": cid,
                                              "error": str(e)[:200]})
                    continue
            except (json.JSONDecodeError, OSError):
                pass  # invalid marker -> rebuild

        cmd = [sys.executable, str(_WORKER), "--year", str(y), "--mode", mode,
               "--draw-lo", str(lo), "--draw-hi", str(hi), "--chunk-id", str(cid),
               "--staging-dir", str(staging)]
        t0 = time.time()
        status = "OK"
        reason = None
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=args.per_chunk_timeout)
            if proc.returncode != 0:
                status = "FAILED"
                reason = (proc.stderr or proc.stdout or "")[-600:]
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            reason = f"exceeded {args.per_chunk_timeout}s"
        wall = round(time.time() - t0, 1)

        rebuilt_rows = None
        tudef = None
        coherence = None
        if status == "OK" and out_parquet.exists():
            rebuilt_rows = int(pq.ParquetFile(out_parquet).metadata.num_rows)
            coherence = _chunk_coherence_selfcheck(out_parquet)
            # (the chunk worker does not persist a TUDef count in its meta; left None.)
        elif status == "OK":
            status = "MISSING_OUTPUT"
            reason = "subprocess returned 0 but no staging parquet found"

        stored_rows = _stored_chunk_rows(base, y, mode, lo, hi)
        rows_match = (rebuilt_rows == stored_rows
                      if rebuilt_rows is not None and stored_rows is not None else None)
        rec = {**item, "status": status, "reason": reason,
               "rebuilt_rows": rebuilt_rows, "stored_production_rows": stored_rows,
               "rows_match": rows_match, "wall_seconds": wall,
               "coherence_selfcheck": coherence, "staging_parquet": str(out_parquet)}
        results.append(rec)

        # TASK 1: write a completion marker per chunk (resumability + audit).
        if status == "OK":
            with open(marker, "w") as f:
                json.dump({"year": y, "mode": mode, "chunk_id": cid,
                           "draw_lo": lo, "draw_hi": hi, "row_count": rebuilt_rows,
                           "euromod_wall_seconds": wall, "tudef": tudef,
                           "stored_production_rows": stored_rows, "rows_match": rows_match,
                           "coherence_selfcheck": coherence,
                           "output_path": str(out_parquet)}, f, indent=2, default=float)

        # progress line to the real console (this script is not fd-captured)
        print(f"[two-N rebuild] {y} {mode} c{cid} [{lo},{hi}): {status} "
              f"rows={rebuilt_rows} vs prod={stored_rows} wall={wall}s", flush=True)

        # TASK 2: inline fail-fast headline parity on the freshly built chunk.
        if status == "OK":
            try:
                ip = _inline_parity_sample(base, out_parquet, y, mode)
                ip.update({"year": y, "mode": mode, "chunk_id": cid})
                inline_parity.append(ip)
                ben_bad = ip["per_column"].get("ils_ben", {}).get("n_above_tol", 0)
                print(f"   inline parity: ils_ben bad={ben_bad}/{ip['n_rows_sampled']} sampled",
                      flush=True)
            except Exception as e:  # noqa: BLE001
                inline_parity.append({"year": y, "mode": mode, "chunk_id": cid,
                                      "error": str(e)[:200]})

        # STOP on the FIRST abort/timeout per the increment rule.
        if status in ("FAILED", "TIMEOUT", "MISSING_OUTPUT"):
            break

    total_wall = round(time.time() - run_start, 1)
    n_total = len(manifest)
    covered = [r for r in results if r["status"] in ("OK", "SKIPPED_EXISTS")]
    completed = [r for r in results if r["status"] == "OK"]
    skipped = [r for r in results if r["status"] == "SKIPPED_EXISTS"]
    failed = [r for r in results if r["status"] in ("FAILED", "MISSING_OUTPUT")]
    timed_out = [r for r in results if r["status"] == "TIMEOUT"]
    full_coverage = (len(covered) == n_total)
    # TASK 2: is inline couples parity SYSTEMATICALLY failing (first couples chunk)?
    couples_inline = [p for p in inline_parity if p.get("mode") == "couples"
                      and "per_column" in p]
    first_couples_systematic_fail = bool(
        couples_inline and couples_inline[0]["n_rows_sampled"] > 0
        and couples_inline[0]["per_column"].get("ils_ben", {}).get("n_above_tol", 0)
        > 0.5 * couples_inline[0]["n_rows_sampled"])

    out = {"increment": "stage2_full_rebuild_staging_v1__task1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False, "priced_redrawn_node": False,
           "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
           "staging_dir": str(staging),
           "worker": str(_WORKER),
           "manifest_n_chunks": n_total,
           "manifest": manifest,
           "chunk_results": results,
           "inline_parity_per_chunk": inline_parity,
           "first_couples_chunk_inline_systematic_fail": first_couples_systematic_fail,
           "n_completed": len(completed), "n_skipped_existing": len(skipped),
           "n_failed": len(failed), "n_timed_out": len(timed_out),
           "full_chunk_coverage": bool(full_coverage),
           "all_rows_match_production": bool(covered) and all(
               r["rows_match"] for r in covered),
           "total_wall_seconds": total_wall,
           "scope_statement": (
               "Full rebuild to STAGING only. No production parquet swapped, overwritten, "
               "moved, or deleted. No re-estimation, no V_i^dir, no redrawn pricing, no W^3 "
               "finding, nothing beyond W^3.")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[two-N rebuild] DONE: {len(completed)}/{n_total} completed, "
          f"{len(failed)} failed, {len(timed_out)} timed out, wall={total_wall}s")
    print(f"[two-N rebuild] staging: {staging}")
    print(f"[two-N rebuild] wrote {args.out_json}")


if __name__ == "__main__":
    main()
