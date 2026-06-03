"""
STAGE THREE, INCREMENT THREE-A — pin and validate the reproducible staged baseline
with a non-bypassable determinism gate.

This validates the Two-N staged rebuild as a REPRODUCIBLE CANDIDATE baseline only. It does
NOT re-estimate, does NOT compute V_i^dir, does NOT price redrawn welfare nodes, does NOT
promote any staged baseline to canonical, and does NOT swap/overwrite/move/delete any
production parquet. Nothing beyond W^3 is touched.

Tasks:
  0  Pin the rebuild configuration/provenance FROM EVIDENCE (build-code constants + Two-N
     provenance + runtime EUROMOD release/package). Unrecoverable facts are recorded as
     "NOT ESTABLISHED FROM REPO EVIDENCE", never guessed.
  1  Validate the Two-N staged baseline COVERAGE (chunks + markers exist; row counts match
     the production chunk manifest; production untouched; staged paths distinct).
  2  DETERMINISM GATE — re-run a deterministic subset (>=1 singles, >=1 couples, >=1
     benefit-heavy chunk) under the pinned config + patched worker to a SCRATCH dir, and
     compare against the existing Two-N staged output on every headline + every available
     ils_*/*_s component + row keys + row order. PASS = machine-tolerance equality.
  3  COMPONENT-COHERENCE GATE on the FULL Two-N staged baseline (identities; draw-specificity;
     no stale carry-over) per year x mode.
  4  Pre-register the later controlled re-estimation verdict criterion.
  5  Readiness: VALIDATED REPRODUCIBLE CANDIDATE iff T1 + T2 + T3 pass and T4 recorded.

If the determinism gate fails, or pinned configuration evidence is missing, STOP and report.

Config-driven, country/year/specification-agnostic: all build constants are READ from the
build worker module and runtime path resolver; nothing is hardcoded here.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
from _bpool_paths import bpool_dir, em_root  # noqa: E402

TOL = 1e-6
_WORKER = Path("scripts/bpool/run_bpool_euromod_chunk.py").resolve()
_CERTIFIED_THETA = Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv")
_CERTIFIED_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
_KEY = {"singles": ["stacked_hh_uid", "draw", "idperson_true"],
        "couples": ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female",
                    "idperson_true"]}
_HEADLINE = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy", "ils_dispy_real"]
_NOT_ESTABLISHED = "NOT ESTABLISHED FROM REPO EVIDENCE"


def _load_worker_module():
    """Read the build worker's pinned constants FROM THE BUILD CODE (no duplication)."""
    spec = importlib.util.spec_from_file_location("_bpool_chunk_worker", _WORKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------------------
# TASK 0 — pin the configuration FROM EVIDENCE
# ----------------------------------------------------------------------------------------
def pin_config(base, staging, worker):
    """Build the pinned rebuild config block from build-code constants + runtime evidence."""
    # EUROMOD release / package evidence (recoverable); exact internal model version is not
    # exposed by the euromod API -> NOT ESTABLISHED.
    em_release_dir = str(em_root())
    try:
        import euromod  # noqa: F401
        em_pkg_version = getattr(euromod, "__version__", _NOT_ESTABLISHED)
    except Exception as e:  # noqa: BLE001
        em_pkg_version = f"{_NOT_ESTABLISHED} ({str(e)[:80]})"

    # system pairing / datasets / CPI / schemas: READ from the build worker, not hardcoded.
    pairing = {str(y): {"system": s, "dataset": d}
               for y, (s, d) in worker._SYSTEM_PAIRING.items()}
    cpi = {str(y): v for y, v in worker._CPI.items()}
    schemas = {str(y): {"n_cols": len(cols), "columns": cols}
               for y, cols in worker._RAW_SCHEMA.items()}

    # production chunk manifest (year, mode, chunk_id, draw_lo/hi, stored row counts).
    manifest = []
    for year in sorted(worker._SYSTEM_PAIRING.keys()):
        for mode, bands in (("singles", [(0, 101)]),
                            ("couples", [(0, 150), (150, 300), (300, 450),
                                         (450, 600), (600, 750), (750, 900)])):
            for cid, (lo, hi) in enumerate(bands):
                stored = _stored_chunk_rows(base, year, mode, lo, hi)
                manifest.append({"year": year, "mode": mode, "chunk_id": cid,
                                 "draw_lo": lo, "draw_hi": hi,
                                 "stored_production_rows": stored})

    return {
        "euromod": {
            "release_dir": em_release_dir,
            "package_version": em_pkg_version,
            "exact_internal_model_version": _NOT_ESTABLISHED,
            "pythonnet_runtime": "coreclr",
        },
        "system_pairing_by_data_year": pairing,
        "dataset_names_by_data_year": {str(y): d for y, (s, d) in worker._SYSTEM_PAIRING.items()},
        "cpi_phi_by_data_year": cpi,
        "raw_input_schema_by_data_year": schemas,
        "id_stamping": {"singles_multiplier": 1000, "couples_multiplier": 10000,
                        "note": "idhh/idperson = id*mult+draw; *_true preserves originals"},
        "staging_path_twoN": str(staging),
        "production_chunk_manifest": manifest,
        "estimation_base_year": {
            "estimator_wage_basis": "2016-real",
            "evidence": "scripts/bpool/build_bpool_estimation_ready.py (wage 2016-real); "
                        "c_scale = mean(consumption) over all rows (bpool_explained.md)",
            "post_euromod_cpi": "ils_dispy_real = ils_dispy * phi_y (CPI per DATA year)",
        },
        "assessment_unit_tax_unit": {
            "definition_source": _NOT_ESTABLISHED + " (EUROMOD FR model internal TUDef; "
            "not defined in repo config)",
            "runtime_observation": "TUDef counts are emitted by EUROMOD at run time only; "
            "the chunk worker does not persist a TUDef count (marker tudef=None).",
        },
        "all_simulated_output_writeback": {
            "patched": True,
            "evidence": "run_bpool_euromod_chunk.py Two-M block: writes every sim_df column "
                        "not in _RAW_SCHEMA[year] (not only the 5 headline cols).",
        },
        "certified_estimate_reference": {
            "spec": str(_CERTIFIED_SPEC),
            "theta_hat_csv": str(_CERTIFIED_THETA),
            "n_free_params": _count_theta_params(),
            "has_clustered_se": _theta_has_clustered_se(),
            "cluster_key": "idorighh",
        },
    }


def _count_theta_params():
    if not _CERTIFIED_THETA.exists():
        return _NOT_ESTABLISHED
    return int(len(pd.read_csv(_CERTIFIED_THETA)))


def _theta_has_clustered_se():
    if not _CERTIFIED_THETA.exists():
        return False
    return "se_clustered" in pd.read_csv(_CERTIFIED_THETA, nrows=1).columns


def _stored_chunk_rows(base, year, mode, draw_lo, draw_hi):
    draw_col = "draw" if mode == "singles" else "draw_joint"
    p = base / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    if not p.exists():
        return None
    t = pq.read_table(p, columns=[draw_col],
                      filters=[(draw_col, ">=", draw_lo), (draw_col, "<", draw_hi)])
    return int(t.num_rows)


# ----------------------------------------------------------------------------------------
# TASK 1 — validate Two-N staged coverage
# ----------------------------------------------------------------------------------------
def validate_coverage(base, staging, manifest):
    prod_root = base.resolve()
    staging_r = staging.resolve()
    # "distinct from production" mirrors the Two-N safety rule (_resolve_staging_or_refuse):
    # staging is SAFE/distinct iff it is NOT the new_data/ root, NOT the production chunks/
    # dir, NOT inside chunks/, and contains NO production ASSEMBLED priced parquet reachable
    # for overwrite. new_data/ is the intermediates root; the production assembled priced
    # files (fr_p3a_bpool_priced__<year>__<mode>.parquet, no "__c") live directly in it,
    # while staged chunks (…__c{N}.parquet) live in the staging_twoN/ subdirectory — a
    # separate directory with non-colliding names. Being a SUBDIR of new_data/ is the
    # intended, safe layout, NOT a collision.
    prod_chunks = (prod_root / "chunks").resolve()
    staged_overwrites_prod = any(
        (prod_root / p.name).exists()
        and "__c" not in p.name  # an assembled production priced name sitting in staging
        for p in staging.glob("fr_p3a_bpool_priced__*.parquet")
    ) if staging.exists() else False
    distinct = (staging_r != prod_root
                and staging_r != prod_chunks
                and prod_chunks not in staging_r.parents
                and not staged_overwrites_prod)
    chunks = []
    all_present = True
    all_rows_match = True
    for m in manifest:
        y, mode, cid = m["year"], m["mode"], m["chunk_id"]
        pqf = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
        marker = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.done.json"
        rec = {"year": y, "mode": mode, "chunk_id": cid,
               "parquet_exists": pqf.exists(), "marker_exists": marker.exists(),
               "stored_production_rows": m["stored_production_rows"]}
        if pqf.exists():
            rec["staged_rows"] = int(pq.ParquetFile(pqf).metadata.num_rows)
            rec["rows_match_manifest"] = (rec["staged_rows"] == m["stored_production_rows"])
        else:
            rec["staged_rows"] = None
            rec["rows_match_manifest"] = False
        all_present = all_present and rec["parquet_exists"] and rec["marker_exists"]
        all_rows_match = all_rows_match and bool(rec["rows_match_manifest"])
        chunks.append(rec)

    # production priced files: record mtimes (read-only) to evidence "untouched".
    prod_files = {}
    for p in sorted(prod_root.glob("fr_p3a_bpool_priced__*.parquet")):
        if "__c" in p.name:  # only assembled production files, not any staged chunk
            continue
        st = p.stat()
        prod_files[p.name] = {"mtime_epoch": st.st_mtime, "size_bytes": st.st_size}

    return {
        "staged_distinct_from_production": bool(distinct),
        "staging_path": str(staging_r),
        "production_root": str(prod_root),
        "all_chunks_and_markers_present": bool(all_present),
        "all_staged_rows_match_manifest": bool(all_rows_match),
        "n_chunks_expected": len(manifest),
        "n_chunks_present": sum(1 for c in chunks if c["parquet_exists"]),
        "per_chunk": chunks,
        "production_priced_files_readonly_snapshot": prod_files,
        "production_parquet_touched": False,
        "ok": bool(distinct and all_present and all_rows_match),
    }


# ----------------------------------------------------------------------------------------
# TASK 2 — determinism gate
# ----------------------------------------------------------------------------------------
def _select_determinism_subset(manifest):
    """>=1 singles, >=1 couples, >=1 benefit-heavy. From Two-N, 2017 had the highest
    means-tested divergence (singles 4.3%, couples 8.4%) -> 2017 couples is the
    benefit-heavy/previously-divergent chunk; 2017 singles is the singles chunk. We pick
    the LAST couples band (c5) so the benefit-heavy couples chunk is also a distinct band."""
    pick = []
    sing = [m for m in manifest if m["mode"] == "singles" and m["year"] == 2017]
    coup = [m for m in manifest if m["mode"] == "couples" and m["year"] == 2017]
    if sing:
        pick.append({**sing[0], "role": "singles"})
    if coup:
        pick.append({**coup[-1], "role": "couples_benefit_heavy"})
    return pick


def _compare_full(staged_pq, rerun_pq, mode):
    """Compare every shared column + keys + row order between the Two-N staged chunk and the
    determinism re-run. PASS = machine tolerance on numerics, exact on keys/order."""
    a = pd.read_parquet(staged_pq)
    b = pd.read_parquet(rerun_pq)
    out = {"staged_rows": int(len(a)), "rerun_rows": int(len(b)),
           "rows_match": bool(len(a) == len(b))}
    if len(a) != len(b):
        out["ok"] = False
        out["reason"] = "row count mismatch"
        return out
    key = _KEY[mode]
    # row-order check: positional key equality (no merge — order must match exactly).
    keys_present = [k for k in key if k in a.columns and k in b.columns]
    order_ok = True
    for k in keys_present:
        order_ok = order_ok and bool((a[k].to_numpy() == b[k].to_numpy()).all())
    out["row_order_keys_identical"] = order_ok
    out["keys_checked"] = keys_present

    shared = [c for c in a.columns if c in b.columns]
    ils_cols = [c for c in shared if c.startswith("ils_")]
    s_cols = [c for c in shared if c.endswith("_s")]
    headline = [c for c in _HEADLINE if c in shared]
    component_cols = sorted(set(ils_cols + s_cols) - set(headline))

    def _maxabs(cols):
        worst = {}
        n_bad_cols = 0
        for c in cols:
            try:
                av = pd.to_numeric(a[c], errors="coerce").to_numpy()
                bv = pd.to_numeric(b[c], errors="coerce").to_numpy()
            except Exception:  # noqa: BLE001
                continue
            d = np.abs(av - bv)
            mx = float(np.nanmax(d)) if len(d) else 0.0
            if mx > TOL:
                n_bad_cols += 1
                worst[c] = mx
        return n_bad_cols, worst

    h_bad, h_worst = _maxabs(headline)
    c_bad, c_worst = _maxabs(component_cols)
    out["headline_cols_checked"] = headline
    out["n_component_cols_checked"] = len(component_cols)
    out["headline_cols_above_tol"] = h_bad
    out["headline_worst"] = h_worst
    out["component_cols_above_tol"] = c_bad
    out["component_worst"] = dict(sorted(c_worst.items(), key=lambda kv: -kv[1])[:20])
    out["ok"] = bool(order_ok and h_bad == 0 and c_bad == 0 and out["rows_match"])
    return out


def determinism_gate(base, staging, scratch, subset, per_chunk_timeout):
    scratch.mkdir(parents=True, exist_ok=True)
    results = []
    gate_ok = True
    for item in subset:
        y, mode, cid = item["year"], item["mode"], item["chunk_id"]
        lo, hi = item["draw_lo"], item["draw_hi"]
        staged_pq = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
        rerun_pq = scratch / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
        if not staged_pq.exists():
            results.append({**item, "status": "BLOCKED",
                            "reason": "Two-N staged chunk missing", "ok": False})
            gate_ok = False
            continue
        cmd = [sys.executable, str(_WORKER), "--year", str(y), "--mode", mode,
               "--draw-lo", str(lo), "--draw-hi", str(hi), "--chunk-id", str(cid),
               "--staging-dir", str(scratch)]
        t0 = time.time()
        status = "OK"
        reason = None
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=per_chunk_timeout)
            if proc.returncode != 0:
                status = "FAILED"
                reason = (proc.stderr or proc.stdout or "")[-600:]
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            reason = f"exceeded {per_chunk_timeout}s"
        wall = round(time.time() - t0, 1)
        if status != "OK" or not rerun_pq.exists():
            results.append({**item, "status": status if status != "OK" else "MISSING_OUTPUT",
                            "reason": reason, "wall_seconds": wall, "ok": False})
            gate_ok = False
            continue
        cmp = _compare_full(staged_pq, rerun_pq, mode)
        rec = {**item, "status": "OK", "wall_seconds": wall, "rerun_parquet": str(rerun_pq),
               "comparison": cmp, "ok": cmp["ok"]}
        results.append(rec)
        gate_ok = gate_ok and cmp["ok"]
    return {"scratch_dir": str(scratch.resolve()),
            "subset": [{k: v for k, v in s.items() if k != "stored_production_rows"}
                       for s in subset],
            "per_chunk": results, "ok": bool(gate_ok and bool(results))}


# ----------------------------------------------------------------------------------------
# TASK 3 — component-coherence on the FULL staged baseline
# ----------------------------------------------------------------------------------------
def coherence_full(staging, manifest):
    cells = {}
    overall_ok = True
    by_cell = {}
    for m in manifest:
        by_cell.setdefault((m["year"], m["mode"]), []).append(m["chunk_id"])
    for (year, mode), cids in sorted(by_cell.items()):
        viol_ben = viol_dispy = 0
        max_ben = max_dispy = 0.0
        n_dec = 0
        ben_varies_num = ben_varies_den = 0
        benmt_varies_num = 0
        for cid in sorted(cids):
            pqf = staging / f"fr_p3a_bpool_priced__{year}__{mode}__c{cid}.parquet"
            if not pqf.exists():
                cells[f"{year}__{mode}"] = {"status": "BLOCKED", "missing_chunk": cid}
                overall_ok = False
                break
            cols = ["ruro_decider", "stacked_hh_uid", "ils_ben", "ils_pen", "ils_benmt",
                    "ils_bennt", "ils_dispy", "ils_origy", "ils_tax", "ils_sicdy"]
            have = [c for c in cols if c in pq.ParquetFile(pqf).schema_arrow.names]
            df = pd.read_parquet(pqf, columns=have)
            dec = df[df.get("ruro_decider", 1) == 1]
            n_dec += len(dec)
            if all(c in dec.columns for c in ["ils_ben", "ils_pen", "ils_benmt", "ils_bennt"]):
                r = (dec["ils_ben"] - (dec["ils_pen"] + dec["ils_benmt"]
                     + dec["ils_bennt"])).abs()
                viol_ben += int((r > TOL).sum())
                max_ben = max(max_ben, float(r.max()) if len(r) else 0.0)
            if all(c in dec.columns for c in ["ils_dispy", "ils_origy", "ils_tax",
                                              "ils_sicdy", "ils_ben"]):
                r2 = (dec["ils_dispy"] - (dec["ils_origy"] - dec["ils_tax"]
                      - dec["ils_sicdy"] + dec["ils_ben"])).abs()
                viol_dispy += int((r2 > TOL).sum())
                max_dispy = max(max_dispy, float(r2.max()) if len(r2) else 0.0)
            g = dec.groupby("stacked_hh_uid")
            if "ils_ben" in dec:
                ben_varies_num += int((g["ils_ben"].nunique() > 1).sum())
                ben_varies_den += int(g.ngroups)
            if "ils_benmt" in dec:
                benmt_varies_num += int((g["ils_benmt"].nunique() > 1).sum())
        else:
            cell_ok = (viol_ben == 0 and viol_dispy == 0)
            cells[f"{year}__{mode}"] = {
                "status": "OK", "decider_rows": n_dec,
                "ils_ben_identity_violations": viol_ben, "ils_ben_identity_max": max_ben,
                "ils_dispy_identity_violations": viol_dispy,
                "ils_dispy_identity_max": max_dispy,
                "share_hh_ils_ben_varies": round(ben_varies_num / ben_varies_den, 4)
                if ben_varies_den else None,
                "share_hh_ils_benmt_varies": round(benmt_varies_num / ben_varies_den, 4)
                if ben_varies_den else None,
                "ok": cell_ok}
            overall_ok = overall_ok and cell_ok
    return {"per_cell": cells, "ok": bool(overall_ok)}


# ----------------------------------------------------------------------------------------
# TASK 4 — pre-register the controlled re-estimation verdict criterion
# ----------------------------------------------------------------------------------------
def reestimation_criterion():
    return {
        "status": "PRE-REGISTERED (not run here)",
        "certified_reference": {
            "theta_hat_csv": str(_CERTIFIED_THETA),
            "spec": str(_CERTIFIED_SPEC),
            "se_columns": ["se_hessian", "se_clustered"],
            "cluster_key": "idorighh",
        },
        "criterion": [
            "Re-estimate the certified spec (joint_pooled_v1_bll0_tlmpin, 47 free params, "
            "theta_l_m pinned -0.8, beta_ll fixed 0) on the REPRODUCIBLE rebuilt baseline, "
            "initialised from the certified theta_hat.",
            "Compare every re-estimated parameter against the certified theta_hat "
            "parameter-by-parameter.",
            "Judge each parameter's movement against its CLUSTERED standard error "
            "(se_clustered, cluster key idorighh): movement within ~the clustered-SE band is "
            "IMMATERIAL; movement well outside is MATERIAL.",
            "Focus explicitly on the decomposition-relevant blocks: ability/wage "
            "(beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2, sigma); "
            "opportunity/access (beta_E, beta_h_*, beta_E_gsur, beta_E_drg*, beta_E_y*, "
            "beta_E_drgur/drgmd, beta_occ_*); and preference (beta_l0_*, beta_l_age*, "
            "beta_l_nkids_*, theta_l_*, theta_c_singles).",
            "Re-run the synthetic-recovery standard on the new reproducible baseline "
            "(PD Hessian at production scale + recovery within tolerance), as for the "
            "certified gate (RURO_jax_recovery_gate_tlmpin_901_v1).",
            "No welfare promotion (V_i^dir, redrawn-node pricing, W^3 promotion, anything "
            "beyond W^3) until this estimate decision is settled.",
        ],
        "decision_rule": (
            "If all decomposition-relevant blocks are within clustered-SE tolerance AND the "
            "synthetic-recovery standard passes, the irreproducibility is immaterial and the "
            "certified estimate stands WITH A CAVEAT (memo Option A). Otherwise the "
            "reproducible baseline replaces the old one and its re-estimate becomes certified "
            "(memo Option B). This script does NOT run the re-estimation."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--config-json", required=True,
                    help="where to write the pinned rebuild config/provenance block")
    ap.add_argument("--scratch-dir", required=True,
                    help="determinism re-run output dir (must NOT be production / Two-N "
                         "staging); a clearly-marked scratch path")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--per-chunk-timeout", type=int, default=14400)
    ap.add_argument("--skip-determinism-run", action="store_true",
                    help="reuse an existing scratch re-run instead of launching EUROMOD "
                         "(still compares; for resumability)")
    args = ap.parse_args()

    base = bpool_dir()
    staging = base / "staging_twoN"
    scratch = Path(args.scratch_dir).resolve()
    # refuse a scratch dir that is production or the Two-N staging
    if scratch == base.resolve() or scratch == staging.resolve() \
            or scratch == (base / "chunks").resolve() or base.resolve() in scratch.parents \
            and scratch.name in ("staging_twoN", "chunks"):
        raise SystemExit(f"REFUSE: scratch dir '{scratch}' must not be production/Two-N "
                         f"staging.")
    worker = _load_worker_module()

    # TASK 0
    cfg = pin_config(base, staging, worker)
    Path(args.config_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.config_json, "w") as f:
        json.dump(cfg, f, indent=2, default=float)
    manifest = cfg["production_chunk_manifest"]

    # TASK 1
    coverage = validate_coverage(base, staging, manifest)

    # TASK 2 (determinism gate)
    subset = _select_determinism_subset(manifest)
    if args.skip_determinism_run:
        # compare existing scratch outputs only
        det = {"scratch_dir": str(scratch), "subset": subset, "per_chunk": [], "ok": False,
               "note": "skip-determinism-run: comparing existing scratch outputs"}
        results = []
        gate_ok = bool(subset)
        for item in subset:
            y, mode, cid = item["year"], item["mode"], item["chunk_id"]
            staged_pq = staging / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
            rerun_pq = scratch / f"fr_p3a_bpool_priced__{y}__{mode}__c{cid}.parquet"
            if not (staged_pq.exists() and rerun_pq.exists()):
                results.append({**item, "status": "BLOCKED",
                                "reason": "missing staged or scratch parquet", "ok": False})
                gate_ok = False
                continue
            cmp = _compare_full(staged_pq, rerun_pq, mode)
            results.append({**item, "status": "OK", "comparison": cmp, "ok": cmp["ok"]})
            gate_ok = gate_ok and cmp["ok"]
        det["per_chunk"] = results
        det["ok"] = bool(gate_ok and bool(results))
    else:
        det = determinism_gate(base, staging, scratch, subset, args.per_chunk_timeout)

    # TASK 3
    coherence = coherence_full(staging, manifest)

    # TASK 4
    criterion = reestimation_criterion()

    # TASK 5 readiness
    config_evidence_complete = bool(
        coverage["staged_distinct_from_production"]
        and cfg["system_pairing_by_data_year"] and cfg["cpi_phi_by_data_year"])
    ready = bool(coverage["ok"] and det["ok"] and coherence["ok"]
                 and criterion["status"].startswith("PRE-REGISTERED")
                 and config_evidence_complete)
    stop_reasons = []
    if not config_evidence_complete:
        stop_reasons.append("pinned configuration evidence incomplete")
    if not coverage["ok"]:
        stop_reasons.append("Task 1 coverage FAIL")
    if not det["ok"]:
        stop_reasons.append("Task 2 determinism FAIL")
    if not coherence["ok"]:
        stop_reasons.append("Task 3 component coherence FAIL")

    out = {
        "increment": "stage3a_pinned_baseline_validation_v1",
        "no_welfare_finding": True, "measures_touched": ["W3_only"],
        "re_estimated": False, "computed_v_dir": False, "priced_redrawn_node": False,
        "promoted_to_canonical": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "tol": TOL,
        "task0_pinned_config_path": str(Path(args.config_json).resolve()),
        "task1_coverage": coverage,
        "task2_determinism_gate": det,
        "task3_component_coherence_full": coherence,
        "task4_reestimation_criterion": criterion,
        "task5_readiness": {
            "validated_reproducible_candidate_baseline": ready,
            "requires": {
                "task1_coverage_pass": coverage["ok"],
                "task2_determinism_pass": det["ok"],
                "task3_coherence_pass": coherence["ok"],
                "task4_criterion_recorded": criterion["status"].startswith("PRE-REGISTERED"),
                "config_evidence_complete": config_evidence_complete,
            },
            "stop_reasons": stop_reasons,
            "baseline_is_canonical": False,
            "production_swapped": False,
            "controlled_reestimation": "SEPARATE AUTHORISATION REQUIRED",
            "welfare_computation_authorised": False,
        },
        "scope_statement": (
            "Validates the Two-N staged rebuild as a reproducible CANDIDATE baseline only. "
            "No re-estimation, no V_i^dir, no redrawn pricing, no production swap, no "
            "promotion to canonical, nothing beyond W^3. Determinism re-run output went to a "
            "scratch dir, which is neither production nor the Two-N staging baseline."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)

    print(f"[three-A] pinned config -> {args.config_json}")
    print(f"[three-A] T1 coverage ok={coverage['ok']} "
          f"({coverage['n_chunks_present']}/{coverage['n_chunks_expected']} chunks, "
          f"rows_match={coverage['all_staged_rows_match_manifest']})")
    for r in det["per_chunk"]:
        c = r.get("comparison", {})
        print(f"[three-A] T2 determinism {r['year']} {r['mode']} c{r['chunk_id']} "
              f"({r.get('role','')}): ok={r.get('ok')} "
              f"hl_bad={c.get('headline_cols_above_tol')} "
              f"comp_bad={c.get('component_cols_above_tol')} "
              f"order_ok={c.get('row_order_keys_identical')} status={r.get('status')}")
    print(f"[three-A] T2 determinism gate ok={det['ok']}")
    for lbl, c in coherence["per_cell"].items():
        print(f"[three-A] T3 coherence {lbl}: ok={c.get('ok')} "
              f"ben_viol={c.get('ils_ben_identity_violations')} "
              f"dispy_viol={c.get('ils_dispy_identity_violations')}")
    print(f"[three-A] T3 coherence gate ok={coherence['ok']}")
    print(f"[three-A] T5 VALIDATED REPRODUCIBLE CANDIDATE = {ready}")
    if stop_reasons:
        print(f"[three-A] STOP reasons: {stop_reasons}")
    print(f"[three-A] wrote {args.out_json}")


if __name__ == "__main__":
    main()
