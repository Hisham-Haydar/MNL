"""
JMP-M08 Stage-B parity gate — library.

Reprices the COMMITTED, HASH-PINNED P2a singles-2016 pricing cache
(``fr_singles_pricing_p2a/priced_*.parquet``) through the SAME production pricing
path that produced it, at the SAME batch geometry, and compares repriced vs stored
``ils_dispy`` at the frozen 1e-6 EUR tolerance.

WHY THIS FILE EXISTS (and why it is not an edit to ``welfare_vdir.py``). The
documented failure was measured by ``welfare_vdir._reprice_cell`` against a
*different artifact* (the P3a b-pool cell) at ``n_hh = 5``. The diagnosis memo
§3.6 established that the M08 baseline is not that artifact, and §4 Route 6
directs the gate at the artifact M08 consumes. §3.1/§3.3 established that the
n_hh=5 batch is itself the dominant defect. Both corrections live entirely in this
gate path: **no production pricing code is modified, and no stored value is
touched.** ``welfare_vdir.py`` is left exactly as it stands so the documented
failure remains reproducible as recorded.

GEOMETRY (D-BEN Option B, target-only). Option B holds every non-target household
at its actual staged state while the target carries the node being priced. In a
PARITY run the target node *is* the stored node, so nothing is displaced from its
actual state and Option B degenerates onto the production batch itself — D-BEN
batch A, the certified production method. Concretely: ``hh_all = sorted(single
idhh)``, chunks of 200 source households, ONE ``EuromodPricingRunner.price()`` call
per chunk, ``alt_key_cols=['draw']``, each alternative replicated as an isolated
synthetic household. This is the notebook loop that wrote the cache, re-executed.

COMPARISON STANDARD (tightened by the M08 production-path review, T4). The
review established that the original comparator failed OPEN: both sides were
coerced with ``errors='coerce'`` and the only gate mask was ``d > tol``, so a
non-numeric or ``NaN`` value produced ``NaN > tol == False`` and was neither
counted nor captured, while ``np.nanmax`` hid it from the summary. Finiteness is
now first-class:

* every compared value is accounted on the side it occurred (raw null,
  non-coercible, ``NaN``, ``+/-inf``), per chunk, per column, and persisted;
* a non-finite value on EITHER side makes the row incomparable, so its absolute
  difference is ``+inf`` -- never a masked ``NaN``. ``d > tol`` is therefore a
  closed test and such a row both fails and is captured;
* a chunk PASSes only if there are zero rows above the frozen 1e-6 EUR tolerance
  AND zero non-finite values on both sides of every gate column AND no EUROMOD
  hard error. Witness non-finiteness is counted, captured and reported, but does
  not gate: the review's falsification is stated against the gate mask.

Nothing else moved: pin verification, reconstruction, batch geometry, join keys,
tolerance and the transaction pattern are byte-for-byte the reviewed logic.

SCOPE. No redrawn node. No counterfactual covariate. No welfare number. No
estimator input touched. EUROMOD is executed for parity validation only; every
stored value is read-only.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd


class GateStop(RuntimeError):
    """Halt condition. Carries a code so the runner can classify the stop."""

    def __init__(self, code: str, where: str, detail: str):
        super().__init__(f"[{code}] {where}: {detail}")
        self.code, self.where, self.detail = code, where, detail


# ---------------------------------------------------------------------------
# hashing / pin verification
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_pricing_cache_pins(repo: Path, cfg: dict) -> Dict[str, Any]:
    """(a) Bind the committed hash-pinned P2a pricing cache.

    Reads the pins from the committed production config (single source of truth,
    never re-declared in the gate config) and verifies EVERY chunk. Any mismatch or
    absence is a halt — the gate refuses to compare against an unverified artifact.
    """
    import yaml

    art = cfg["artifact"]
    pin_src = repo / art["pin_source"]
    if not pin_src.is_file():
        raise GateStop("HP-PIN", "pin-source", f"absent: {art['pin_source']}")
    node: Any = yaml.safe_load(pin_src.read_text(encoding="utf-8"))
    for key in art["pin_path"]:
        node = node[key]

    cache_dir = repo / art["dir"]
    pins = node["sha256"]
    verified: List[Dict[str, Any]] = []
    for name in sorted(pins):
        path = cache_dir / name
        if not path.is_file():
            raise GateStop("HP-PIN", "pinned-chunk", f"absent: {path}")
        got = sha256_file(path)
        ok = got == pins[name]
        verified.append({"chunk": name, "expected_sha256": pins[name],
                         "observed_sha256": got, "match": ok,
                         "bytes": path.stat().st_size})
        if not ok:
            raise GateStop("HP-PIN", "pinned-chunk",
                           f"{name} sha256 {got} != committed {pins[name]}")

    # declared shape contract
    total = 0
    hh = set()
    for entry in verified:
        d = pd.read_parquet(cache_dir / entry["chunk"], columns=["source_idhh", "draw"])
        entry["rows"] = int(len(d))
        entry["households"] = int(d["source_idhh"].nunique())
        entry["draws"] = int(d["draw"].nunique())
        total += len(d)
        hh.update(d["source_idhh"].unique().tolist())
    if total != int(node["expected_rows_total"]):
        raise GateStop("HP-PIN", "cache-shape",
                       f"rows {total} != declared {node['expected_rows_total']}")
    if len(hh) != int(node["expected_hh"]):
        raise GateStop("HP-PIN", "cache-shape",
                       f"households {len(hh)} != declared {node['expected_hh']}")

    return {"pin_source": art["pin_source"],
            "pin_path": list(art["pin_path"]),
            "dir": art["dir"],
            "chunk_grid": list(node["chunk_grid"]),
            "declared_columns": list(node["columns"]),
            "expected_rows_total": int(node["expected_rows_total"]),
            "expected_hh": int(node["expected_hh"]),
            "observed_rows_total": total,
            "observed_hh": len(hh),
            "all_pins_match": True,
            "chunks": verified}


def verify_frozen_inputs(repo: Path, cfg: dict) -> Dict[str, Any]:
    """Verify the upstream pinned inputs the reconstruction consumes.

    The raw FR microdata and the frozen draws geometry are both hash-pinned in the
    production config. The reconstruction reads the raw file; the geometry parquet
    is the independent check on the rebuilt draw frame.
    """
    import yaml

    pin_src = repo / cfg["artifact"]["pin_source"]
    fi = yaml.safe_load(pin_src.read_text(encoding="utf-8"))["frozen_inputs"]
    out: Dict[str, Any] = {}
    for key in ("raw_fr_txt", "gsur_lookup"):
        spec = fi[key]
        p = Path(spec["path"])
        if not p.is_file():
            raise GateStop("HP-PIN", f"frozen-input:{key}", f"absent: {p}")
        got = sha256_file(p)
        out[key] = {"path": str(p), "expected_sha256": spec["sha256"],
                    "observed_sha256": got, "match": got == spec["sha256"]}
        if got != spec["sha256"]:
            raise GateStop("HP-PIN", f"frozen-input:{key}",
                           f"sha256 {got} != committed {spec['sha256']}")

    geo = fi["draws_geometry"]
    gp = repo / geo["parquet"]
    gm = repo / geo["meta"]
    entry: Dict[str, Any] = {"path": geo["parquet"], "present": gp.is_file()}
    if gp.is_file():
        entry["observed_sha256"] = sha256_file(gp)
        if gm.is_file():
            declared = json.loads(gm.read_text(encoding="utf-8")).get("sha256")
            entry["declared_sha256"] = declared
            entry["match"] = declared == entry["observed_sha256"]
            if not entry["match"]:
                raise GateStop("HP-PIN", "frozen-input:draws_geometry",
                               "geometry parquet does not match its meta sha256")
    out["draws_geometry"] = entry

    # EUROMOD system files: not hash-pinned anywhere on disk, but their mtimes are
    # load-bearing evidence (F6-PRICE-B0 Task 2 traced the P3a residual to an
    # FR.xml update that post-dated that build). Recorded, never gated on.
    root = Path(cfg["geometry"]["euromod"]["model_root"])
    country = cfg["geometry"]["euromod"]["country"]
    sysfiles = {}
    for fname in (f"{country}.xml", f"{country}_DataConfig.xml"):
        p = root / "XMLParam" / "Countries" / country / fname
        if p.is_file():
            st = p.stat()
            sysfiles[fname] = {"path": str(p), "bytes": st.st_size,
                               "mtime_utc": time.strftime(
                                   "%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime))}
    out["euromod_system_files"] = sysfiles
    return out


# ---------------------------------------------------------------------------
# production-path reconstruction
# ---------------------------------------------------------------------------
def reconstruct_pipeline(repo: Path, cfg: dict, scratch: Path,
                         log: Optional[List[str]] = None) -> Dict[str, Any]:
    """Rebuild the notebook state that the production pricing loop ran inside.

    Executes the production notebook's code cells over the configured span in a
    single namespace. Every expensive stage in that notebook is flag-guarded and
    OFF by default (``RUN_PRICING=False``, ``EXPORT_PRODUCTION_GEOMETRY=False``),
    so this rebuild performs NO EUROMOD call and makes NO production write. The
    notebook's own dev-artifact root is redirected into the run's scratch area so
    the repository worktree is untouched.

    Returns the namespace containing ``runner_full``, ``baseline_full``,
    ``draws_p2a``, ``hh_all``, ``CHUNK`` and ``KEEP`` — the exact objects the
    pricing loop consumed.
    """
    geom = cfg["geometry"]
    nb_path = repo / geom["notebook"]
    if not nb_path.is_file():
        raise GateStop("HP-RECON", "notebook", f"absent: {geom['notebook']}")
    lo, hi = (int(x) for x in geom["reconstruct_cells"])
    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    # The notebook is authored for an IPython kernel and calls the interactive
    # display builtins. Outside a kernel they do not exist, so the namespace is
    # seeded with inert shims. These affect presentation only -- no notebook logic
    # branches on them, and nothing computational is substituted.
    ns: Dict[str, Any] = {
        "__name__": "__m08_parity_reconstruction__",
        "display": lambda *a, **k: None,
        "get_ipython": lambda *a, **k: None,
    }
    cwd0 = Path.cwd()
    os.chdir(repo)
    try:
        for idx in range(lo, hi + 1):
            cell = nb["cells"][idx]
            if cell["cell_type"] != "code":
                continue
            src = "".join(cell["source"])
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    exec(compile(src, f"<nb-cell-{idx}>", "exec"), ns)
            except Exception as exc:  # noqa: BLE001 - reported, not swallowed
                raise GateStop("HP-RECON", f"cell-{idx}",
                               f"{type(exc).__name__}: {exc}") from exc
            if log is not None:
                for line in buf.getvalue().splitlines():
                    log.append(f"cell{idx:02d}| {line}")
            # Immediately after the controls cell, force the guards OFF and
            # redirect the notebook's dev-artifact root out of the worktree.
            if idx == lo:
                if ns.get("RUN_PRICING") or ns.get("EXPORT_PRODUCTION_GEOMETRY"):
                    raise GateStop("HP-RECON", "guards",
                                   "notebook execution guards are not OFF by default")
                ns["RUN_PRICING"] = False
                ns["EXPORT_PRODUCTION_GEOMETRY"] = False
                ns["NOTEBOOK_OUTPUT_ROOT"] = scratch / "notebook_dev"
    finally:
        os.chdir(cwd0)

    missing = [k for k in ("runner_full", "baseline_full", "draws_p2a", "hh_all",
                           "CHUNK", "KEEP", "WEEKS_PER_MONTH",
                           "FR_COUNTRY", "FR_SYSTEM", "FR_DATASET")
               if k not in ns]
    if missing:
        raise GateStop("HP-RECON", "namespace", f"missing objects: {missing}")
    if int(ns["CHUNK"]) != int(geom["chunk_size"]):
        raise GateStop("HP-RECON", "geometry",
                       f"notebook CHUNK={ns['CHUNK']} != declared {geom['chunk_size']}")
    return ns


def verify_reconstructed_geometry(ns: dict, repo: Path, cfg: dict) -> Dict[str, Any]:
    """Check the rebuilt draw frame against the committed frozen geometry parquet.

    The rebuilt ``draws_p2a`` is what the pricing loop consumed; the frozen parquet
    is the hash-pinned freeze of that same in-memory frame (notebook cell 32 writes
    it under ``sort_values(['idhh','draw'])``). Agreement on the pricing-relevant
    columns is independent evidence that the reconstruction reproduces production.
    """
    import yaml

    pin_src = repo / cfg["artifact"]["pin_source"]
    geo_spec = yaml.safe_load(pin_src.read_text(encoding="utf-8"))[
        "frozen_inputs"]["draws_geometry"]
    gp = repo / geo_spec["parquet"]
    out: Dict[str, Any] = {"frozen_geometry_present": gp.is_file()}

    live = ns["draws_p2a"]
    out["rebuilt_rows"] = int(len(live))
    out["rebuilt_households"] = int(live["idhh"].nunique())
    out["expected_rows"] = int(geo_spec["expected_rows"])
    out["expected_households"] = int(geo_spec["expected_hh"])
    if out["rebuilt_rows"] != out["expected_rows"]:
        raise GateStop("HP-RECON", "draws-shape",
                       f"rebuilt rows {out['rebuilt_rows']} != {out['expected_rows']}")
    if out["rebuilt_households"] != out["expected_households"]:
        raise GateStop("HP-RECON", "draws-shape",
                       f"rebuilt hh {out['rebuilt_households']} != "
                       f"{out['expected_households']}")

    if gp.is_file():
        froz = pd.read_parquet(gp)
        key = ["idhh", "draw"]
        cmp_cols = [c for c in ("hours", "wage", "working", "loc4", "log_prior",
                                "is_chosen", "idhh_true", "idperson_true")
                    if c in froz.columns and c in live.columns]
        a = live.sort_values(key, kind="mergesort").reset_index(drop=True)
        b = froz.sort_values(key, kind="mergesort").reset_index(drop=True)
        agree: Dict[str, Any] = {}
        worst = 0.0
        for c in cmp_cols:
            x, y = a[c], b[c]
            if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
                d = float(np.nanmax(np.abs(x.to_numpy(dtype="float64")
                                           - y.to_numpy(dtype="float64"))))
                agree[c] = d
                worst = max(worst, d)
            else:
                agree[c] = "non-numeric (skipped)"
        out["compared_columns"] = cmp_cols
        out["max_abs_diff_by_column"] = agree
        out["max_abs_diff_overall"] = worst
        out["matches_frozen_geometry"] = worst == 0.0
        if worst != 0.0:
            raise GateStop("HP-RECON", "draws-geometry",
                           f"rebuilt draws differ from frozen geometry (max abs {worst})")
    return out


# ---------------------------------------------------------------------------
# the parity comparison
# ---------------------------------------------------------------------------
def _alternatives(ns: dict) -> pd.DataFrame:
    """``alt2`` exactly as the production pricing cell built it."""
    alt = ns["draws_p2a"].copy()
    alt["source_idhh"] = alt["idhh_true"]
    alt["decider_idperson"] = alt["idperson_true"]
    return alt


def _numeric_side(col: pd.Series):
    """Coerce ONE side of a compared column to float64 and account its finiteness.

    Returns ``(values, nonfinite_mask, counts)``. The counts separate the ways a
    value can fail to be a finite number so the evidence packet can distinguish a
    stored null, a value that would not coerce at all, a computed ``NaN`` and an
    ``+/-inf``. This is the T4 fix: finiteness is recorded, not summarised away.
    """
    raw_null = col.isna().to_numpy()
    v = pd.to_numeric(col, errors="coerce").to_numpy(dtype="float64")
    is_nan = np.isnan(v)
    is_inf = np.isinf(v)
    nonfinite = is_nan | is_inf
    counts = {
        "n_raw_null": int(raw_null.sum()),
        "n_noncoercible": int((is_nan & ~raw_null).sum()),
        "n_nan": int(is_nan.sum()),
        "n_inf": int(is_inf.sum()),
        "n_nonfinite": int(nonfinite.sum()),
    }
    return v, nonfinite, counts


CERTIFICATION_STANDARD = (
    "PASS requires, on EVERY chunk: zero rows above the frozen tol_eur on every "
    "gate column AND zero non-finite values on BOTH the stored and the repriced "
    "side of every gate column AND zero EUROMOD hard errors. A non-finite value on "
    "either side is treated as an infinite absolute difference, never a masked "
    "NaN, so it both fails the chunk and appears in the failing-row capture. "
    "Witness-column non-finiteness is counted, captured and reported but does not "
    "gate."
)


def reprice_chunk(ns: dict, cfg: dict, *, chunk_start: int,
                  repo: Path, alt: pd.DataFrame) -> Dict[str, Any]:
    """Reprice ONE production chunk at production geometry and compare to stored.

    The batch handed to EUROMOD is the chunk's 200 source households at their
    ACTUAL staged state across all 101 alternatives — the production batch, not a
    subset of it. Nothing is overwritten with a counterfactual: this is a reprice
    of stored nodes.
    """
    geom, comp = cfg["geometry"], cfg["comparison"]
    tol = float(cfg["gate"]["tol_eur"])
    chunk_size = int(geom["chunk_size"])
    hh_all, KEEP = ns["hh_all"], ns["KEEP"]

    part = hh_all[chunk_start:chunk_start + chunk_size]
    stored_path = repo / cfg["artifact"]["dir"] / f"priced_{chunk_start:05d}.parquet"
    stored = pd.read_parquet(stored_path)

    t0 = time.time()
    res = ns["runner_full"].price(
        alt[alt["source_idhh"].isin(part)],
        ns["baseline_full"][ns["baseline_full"]["idhh"].isin(part)],
        country=ns["FR_COUNTRY"], system=ns["FR_SYSTEM"], dataset=ns["FR_DATASET"],
        alt_key_cols=list(geom["alt_key_cols"]),
        weeks_per_month=ns["WEEKS_PER_MONTH"])
    secs = time.time() - t0

    hard_errors = [e for e in res.errors if "uprate" not in e.lower()]
    out = res.output

    keys = list(comp["join_keys"])
    if out.duplicated(subset=keys).any() or stored.duplicated(subset=keys).any():
        raise GateStop("HP-CMP", f"chunk-{chunk_start:05d}",
                       "duplicate join keys in repriced or stored frame")
    exp = set(map(tuple, stored[keys].itertuples(index=False, name=None)))
    got = set(map(tuple, out[keys].itertuples(index=False, name=None)))
    if exp != got:
        raise GateStop("HP-CMP", f"chunk-{chunk_start:05d}",
                       f"row-set mismatch: {len(exp - got)} stored-only, "
                       f"{len(got - exp)} repriced-only")

    # row-order identity of the two batches (evidence, not a gate)
    order_identical = bool(
        len(out) == len(stored)
        and (out[keys].reset_index(drop=True)
             == stored[keys].reset_index(drop=True)).all().all())

    gate_cols = list(comp["gate_columns"])
    wit_cols = [c for c in comp["witness_columns"] if c in stored.columns]
    comp_cols = [c for c in comp["decompose_components"] if c in out.columns]
    acc_cols = [c for c in comp["accumulator_witnesses"] if c in out.columns]

    merged = stored.merge(
        out[keys + [c for c in set(gate_cols + wit_cols + comp_cols + acc_cols)
                    if c in out.columns]],
        on=keys, how="inner", suffixes=("__stored", "__repriced"), validate="one_to_one")
    if len(merged) != len(stored):
        raise GateStop("HP-CMP", f"chunk-{chunk_start:05d}",
                       f"join produced {len(merged)} rows, expected {len(stored)}")

    # rows actually compared -- asserted equal to the stored row count before any
    # statistic is computed, and persisted as evidence
    n_rows_compared = int(len(merged))
    stored_rows = int(len(stored))
    if n_rows_compared != stored_rows:
        raise GateStop("HP-CMP", f"chunk-{chunk_start:05d}",
                       f"rows compared {n_rows_compared} != stored rows {stored_rows}")

    summary: Dict[str, Any] = {}
    fail_mask = np.zeros(n_rows_compared, dtype=bool)
    gate_nonfinite_mask = np.zeros(n_rows_compared, dtype=bool)
    any_nonfinite_mask = np.zeros(n_rows_compared, dtype=bool)
    for c in gate_cols + wit_cols:
        s, s_bad, s_counts = _numeric_side(merged[f"{c}__stored"])
        r, r_bad, r_counts = _numeric_side(merged[f"{c}__repriced"])
        bad = s_bad | r_bad
        # A non-finite value on EITHER side makes the row incomparable: its
        # difference is +infinity, never a masked NaN. This is what closes
        # `d > tol` -- the mask can no longer be silently False.
        d = np.where(bad, np.inf, np.abs(r - s))
        merged[f"absdiff_{c}"] = d
        merged[f"nonfinite_{c}"] = bad
        finite_d = d[~bad]
        summary[c] = {
            "max_abs_diff": float(np.max(d)),
            "median_abs_diff": float(np.median(d)),
            "max_abs_diff_finite_rows": (float(np.max(finite_d))
                                         if finite_d.size else None),
            "n_rows_above_tol": int(np.sum(d > tol)),
            "n_rows_compared": n_rows_compared,
            "n_nonfinite_stored": s_counts["n_nonfinite"],
            "n_nonfinite_repriced": r_counts["n_nonfinite"],
            "n_rows_nonfinite_either_side": int(bad.sum()),
            "stored_side_counts": s_counts,
            "repriced_side_counts": r_counts,
            "is_gate_column": c in gate_cols,
        }
        any_nonfinite_mask |= bad
        if c in gate_cols:
            fail_mask |= d > tol
            gate_nonfinite_mask |= bad

    n_fail = int(fail_mask.sum())
    n_gate_nonfinite = int(gate_nonfinite_mask.sum())
    n_any_nonfinite = int(any_nonfinite_mask.sum())

    # Capture every failing row AND every row carrying a non-finite value in any
    # compared column. Only `fail_mask` gates; `fails_gate` says which is which.
    capture_mask = fail_mask | any_nonfinite_mask
    n_captured = int(capture_mask.sum())
    failing: Optional[pd.DataFrame] = None
    if n_captured:
        cols = keys + ["ruro_decider", "dgn"]
        cols += [f"{c}__stored" for c in gate_cols + wit_cols]
        cols += [f"{c}__repriced" for c in gate_cols + wit_cols]
        cols += [f"absdiff_{c}" for c in gate_cols + wit_cols]
        cols += [f"nonfinite_{c}" for c in gate_cols + wit_cols]
        cols += comp_cols + acc_cols
        failing = merged.loc[capture_mask, [c for c in cols if c in merged.columns]].copy()
        failing.insert(0, "nonfinite_gate_column", gate_nonfinite_mask[capture_mask])
        failing.insert(0, "fails_gate", fail_mask[capture_mask])
        failing.insert(0, "chunk", f"priced_{chunk_start:05d}")

    finiteness = {
        "n_rows_compared": n_rows_compared,
        "stored_rows": stored_rows,
        "rows_compared_equals_stored_rows": n_rows_compared == stored_rows,
        "gate_columns": list(gate_cols),
        "witness_columns": list(wit_cols),
        "n_nonfinite_gate_stored": int(sum(summary[c]["n_nonfinite_stored"]
                                           for c in gate_cols)),
        "n_nonfinite_gate_repriced": int(sum(summary[c]["n_nonfinite_repriced"]
                                             for c in gate_cols)),
        "n_rows_nonfinite_gate_either_side": n_gate_nonfinite,
        "n_nonfinite_witness_stored": int(sum(summary[c]["n_nonfinite_stored"]
                                              for c in wit_cols)),
        "n_nonfinite_witness_repriced": int(sum(summary[c]["n_nonfinite_repriced"]
                                                for c in wit_cols)),
        "n_rows_nonfinite_any_compared_column": n_any_nonfinite,
        "all_gate_values_finite_both_sides": n_gate_nonfinite == 0,
        "all_compared_values_finite_both_sides": n_any_nonfinite == 0,
        "witness_nonfiniteness_gates": False,
    }

    return {
        "certification_standard": CERTIFICATION_STANDARD,
        "n_rows_compared": n_rows_compared,
        "finiteness": finiteness,
        "n_rows_nonfinite_gate": n_gate_nonfinite,
        "n_rows_captured": n_captured,
        "chunk": f"priced_{chunk_start:05d}",
        "chunk_start": chunk_start,
        "households_in_batch": int(len(part)),
        "alternatives_in_batch": int(alt[alt["source_idhh"].isin(part)]
                                     .groupby(["source_idhh", "draw"]).ngroups),
        "euromod_rows_in_batch": int(len(out)),
        "stored_rows": int(len(stored)),
        "row_order_identical_to_stored": order_identical,
        "euromod_seconds": round(secs, 1),
        "euromod_hard_errors": hard_errors,
        "euromod_uprate_notes": len(res.errors) - len(hard_errors),
        "kept_columns": list(KEEP),
        "components_available_repriced": comp_cols,
        "accumulators_available": acc_cols,
        "column_summary": summary,
        "n_rows_above_tol": n_fail,
        # tightened rule: tolerance AND finiteness AND no hard error (T4)
        "status": ("PASS" if (n_fail == 0 and n_gate_nonfinite == 0
                              and not hard_errors) else "FAIL"),
        "_failing_rows": failing,
    }
