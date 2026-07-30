#!/usr/bin/env python
"""FR P2a region-live production rebuild -- Phases 1-4 runner.

Phases 1-4 implemented. A REAL Phase-3 run is gated by the research-grade
execution contract of FR_P2a_region_live_phase3_execution_scope_v1.md: the
documented CLI with --execute-phase3, expected MNL/nested HEADs, full worktree
cleanliness, and the review-v6 APPROVE file hash. A REAL Phase-4 run is gated
by the PHASE-4-SPECIFIC approval (--execute-phase4 + the same Git gates + the
FR_P2a_region_live_phase4_code_review_v7.md APPROVE file hash; Phase-4 reviews
v1-v6 and the Phase-3 review-v6 are rejected there). Without the execute flag,
--phase 3 / --phase 4
perform only the non-optimizing / non-evaluating dry-run. Phases 5-8 are
unsupported and refused.

Binding documents (in order):
  docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md      (canonical)
  docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md
  docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md
Frozen reference: dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb
(read-only checkpoint; this runner is a faithful production port of its
deterministic Phase-1 transforms and never executes or modifies it).

Phase 1 (D-1 v2 boundary): frozen already-priced P2a draw artifacts
  -> assemble_singles -> independent region/urbanisation/GSUR revival
  -> B-pool band overwrite -> er_b -> freeze under region_live_v1/.
Phase 2: package load + stored-theta objective reproduction (G-19). NO optimizer.
Phase 3 (AUTHORIZED by FR_P2a_region_live_phase12_manager_acceptance_v1.md s9):
  input contract against the accepted Phase 1-2 evidence, then L-BFGS-B estimation
  with the pre-registered checkpoint options over the package JAX objective.
  Writes ONLY under region_live_v1/phase3_estimation_v1/. With --dry-run the
  contract is verified and NO optimizer is called.

HARD REFUSALS (S-0, asserted in code, not just documented):
  - no EUROMOD (no import, no connection, no pricing run)
  - no draw generation/regeneration (no hours_mixture_d1 / occ_draw_empirical /
    pilot_wage_draw / build_bpool_singles import; geometry is a frozen input)
  - no optimizer in Phases 1-2 and in every --dry-run (scipy.optimize may load
    only inside the real Phase-3 estimation call)
  - no Phase-4+ computation in Phase 3 (no Hessian / eigenvalues / rank /
    per-household scores / sandwich SE / post-estimation / welfare / synthetic
    recovery code path exists in the Phase-3 route)
  - no notebook I/O; no write outside region_live_v1/ (Phase 3: only its subdir)
Phase 4 (AUTHORIZED by FR_P2a_region_live_phase3_manager_acceptance_v1.md s15):
  curvature/rank/regional-identification diagnostics of the ACCEPTED immutable
  Phase-3 bundle. NO optimizer, NO theta change, NO standard errors. Writes ONLY
  under region_live_v1/phase4_curvature_v1/. Dry-run never evaluates the
  Hessian; real execution additionally requires the Phase-4 review-v7 APPROVE.
Phases 5-8 are manager-gated and unsupported: this runner refuses --phase > 4.

Exit codes: 0 = phases completed; 2 = pre-registered stop (STOPPED manifest);
3 = unexpected error (STOPPED manifest, stop code S-0/unexpected);
4 = Phase-3 REVIEW_REQUIRED_TARGET_MISMATCH (estimation finished, target not
reproduced within tolerance -- manager review required, never auto-accepted).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml

MNL_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path(__file__).resolve()

# --- canonical Phase-3 production identity (review fixes 4/6; decisions A/E/H) ---
# The production CLI enforces these EXACTLY; only pure internal helpers may accept
# temporary roots (unit tests). No production CLI test-root override exists.
CANONICAL_REGIONLIVE_ROOT = MNL_ROOT / "outputs/p2a_singles2016/region_live_v1"
CANONICAL_PHASE3_SUBDIR = "phase3_estimation_v1"
CANONICAL_PHASE3_ROOT = CANONICAL_REGIONLIVE_ROOT / CANONICAL_PHASE3_SUBDIR
CANONICAL_STEM = "fr_p2a_singles2016_regionlive"
# review-v3 canonical identities (decisions B/E/G) + immutable gate controls (D)
CANONICAL_PHASE3_CONFIG = MNL_ROOT / "scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml"
CANONICAL_APPROVED_REVIEW_REL = Path(
    "docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md")
PACKAGE_SOURCE_ROOT = (MNL_ROOT / "dclaborsupply-monorepo"
                       / "packages/dclaborsupply/src")
PHASE3_PREOPT_OBJECTIVE_TOL = 1.0e-4
PHASE3_TARGET_MISMATCH_STATUS = "REVIEW_REQUIRED_TARGET_MISMATCH"
# decision D: the EXACT dclaborsupply module inventory of the Phase-3
# contract/objective route; each must be a tracked blob at the expected nested
# commit with Git-canonical content equality (git hash-object --path; under
# autocrlf the raw worktree bytes may legitimately differ from the LF blob).
# Ignored/untracked substitutions therefore fail.
REQUIRED_PACKAGE_MODULES = (
    "dclaborsupply", "dclaborsupply.models", "dclaborsupply.data",
    "dclaborsupply.data.loader", "dclaborsupply.spec",
    "dclaborsupply.spec.parser", "dclaborsupply.likelihood",
    "dclaborsupply.likelihood.index", "dclaborsupply.likelihood.engine_jax",
    "dclaborsupply.likelihood._numpy_primitives",
)
# accepted pin identity -- exact ordered ten-name tuple (decision E); the YAML list
# must equal this exactly (order included); any deviation is a STOP
ACCEPTED_PIN_NAMES = (
    "beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "beta_l0_f", "beta_l_age_f",
    "beta_l_age2_f", "beta_l_nkids_f", "theta_l_f", "beta_E_y2015", "beta_E_y2017",
)
EXPECTED_AT_BOUND_NAMES = ("beta_l_age2_sm", "beta_l_age2_sf")
# immutable safety-critical constants (decision C): the YAML must equal these exactly
PHASE3_SAFETY_CONSTANTS = {
    "target_negll_full": 19053.46553160094,
    "objective_tol_full": 1e-4, "g16_inbounds_epsilon": 1e-9,
    "gradient_max_abs_35free": 1e-2, "bound_hit_eps": 1e-5,
    "n_params": 47, "n_free": 37, "n_nonbound_free": 35, "n_pinned": 10,
    "n_hh": 1555, "n_alts": 101,
    "optimizer_method": "L-BFGS-B",
    "optimizer_options": {"maxiter": 5000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10},
}
# review-v6 is the canonical approval document (scope doc s7); reviews v1-v5
# (all REJECT) cannot authorize execution
REVIEW_V6_HEADING = "# 1. Sixth-review verdict"
APPROVE_LINE = "**FINAL VERDICT: APPROVE**"
# the successful-bundle artifact set; the manifest is written LAST and is NEVER
# part of its own artifact-hash dictionary (decision C / review fix 7)
PHASE3_ARTIFACTS = ("phase3_console.log", "theta_estimated.csv",
                    "optimizer_diagnostics.json", "estimation_results.json")

# --- Phase 4: curvature & regional identification (acceptance doc s15) ---------
# Phase 4 diagnoses the ACCEPTED immutable Phase-3 result only: no optimizer, no
# theta change, no standard errors. Gates are the ratified D-3/D-4 values
# (plan v2 s13-s14, G-5..G-9); the YAML phase4 block must equal these exactly.
CANONICAL_PHASE4_SUBDIR = "phase4_curvature_v1"
CANONICAL_PHASE4_ROOT = CANONICAL_REGIONLIVE_ROOT / CANONICAL_PHASE4_SUBDIR
# Phase-4-specific approval (review-v1 fix 1; rebound after every conditional
# review and after the R1 audit correction): a real Phase-4 run is authorized
# ONLY by the PHASE-4 review below -- Phase-4 reviews v1-v6 and the PHASE-3
# review-v6 are all rejected
CANONICAL_APPROVED_PHASE4_REVIEW_REL = Path(
    "docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v7.md")
PHASE4_REVIEW_HEADING = "# 1. Phase-4 review verdict"
PHASE3_ACCEPTED_BUNDLE_SHA256 = (
    "2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b")
PHASE3_ACCEPTED_NEGLL_FINAL = 19053.46553160093
# exact regional block (plan v2 s5/s14, decision D-3): derived from the accepted
# spec at run time and REQUIRED to equal this tuple AND the YAML list -- any
# conflict between the sources is a STOP, never a guess
PHASE4_REGIONAL_PARAMS = (
    "beta_E_gsur", "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4",
    "beta_E_drgn5", "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
    "beta_E_drgur", "beta_E_drgmd")
# R-1 household-level design columns, position-matched to PHASE4_REGIONAL_PARAMS
PHASE4_REGIONAL_DESIGN_COLUMNS = (
    "gsur", "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8",
    "drgur", "drgmd")
PHASE4_SAFETY_CONSTANTS = {
    "symmetry_rel_tol": 1e-8,               # G-6 (D-4)
    "rank_rel_tol": 1e-10,                  # eps_rank (D-3): G-7 / R-1 / R-4
    "nonpos_count_eig_tol": 1e-8,           # G-5 n_nonpos counter (plan v2 s19)
    "condition_clean_max": 1e7,             # G-8 three-tier (D-4)
    "condition_warn_max": 1e10,
    "pooled_baseline_condition": 1.295e6,   # D-4 comparison anchor
    "n_free": 37, "regional_n": 10,
    "loading_share_warn": 0.5,              # R-3 warning-only (D-3)
    "consistency_negll_tol": 1e-6,          # |negLL(theta_hat) - accepted final|
    "consistency_grad_tol": 1e-6,           # max|grad - published gradient_final|
}
PHASE4_ARTIFACTS = (
    "phase4_console.log", "hessian_free.csv", "hessian_free.npy",
    "hessian_eigenvalues.csv", "regional_hessian_subblock.csv",
    "regional_schur_complement.csv", "phase4_diagnostics.json")

# modules whose presence in sys.modules is an S-0 prohibited-operation stop
_PROHIBITED_MODULES = (
    "dclaborsupply_app.euromod",     # EUROMOD connector / pricing runner
    "hours_mixture_d1",              # draw generation
    "occ_draw_empirical",            # draw generation
    "pilot_wage_draw",               # draw generation
    "build_bpool_singles",           # draw generation
)


# funnel constants — verbatim from the frozen checkpoint (cell 6, ec=3)
FUNNEL_CONFIG = dict(
    age_range=(20, 60),
    allowed_les=(3, 5, 7),
    wage_bounds=(2.0, 170.0),
    other_member_income_threshold=50.0,
    hours_cap_high=70, hours_floor_low=10, hours_inactive_threshold=5,
    retire_cols=("byr", "pdi", "poa", "psu"),
)

REVIVED_COLS = ["drgn1", "drgur", "drgmd", "drgru", "gsur"]
BAND_COLS = ["working_pt1", "working_pt2", "working_ft", "working_lh"]

# columns the dclaborsupply loader consumes from an engine-ready singles frame
# (hard-equality set for frame reconciliation; plan v2 s8 step 4)
ENGINE_CONSUMED_COLS = [
    "idhh", "source_idhh", "source_idorighh", "idorighh", "cluster_id", "draw",
    "is_chosen", "dgn", "consumption", "c_norm", "l_norm", "c_scale", "l_scale",
    "leisure", "prior", "log_prior", "log_q_E", "log_q_H", "log_q_W", "log_q_Occ",
    "age_norm", "age_norm2", "n_children", "educL", "educM", "educH",
    "working", "working_pt1", "working_pt2", "working_ft", "working_lh",
    "hours", "wage", "log_wage", "pexp_years", "pexp_years2",
    "loc4", "loc4_1", "loc4_2", "loc4_3", "loc4_4",
    "gsur", "drgn1", "drgur", "drgmd", "drgru",
    "year_2015_indicator", "year_2017_indicator",
]


# --------------------------------------------------------------------------- #
# infrastructure
# --------------------------------------------------------------------------- #
class StopRun(Exception):
    """Pre-registered stop condition (S-0/S-1/S-8/S-9)."""

    def __init__(self, code: str, gate: str, message: str):
        super().__init__(f"{code} [{gate}] {message}")
        self.code, self.gate, self.message = code, gate, message


class OutRoot:
    """All writes must resolve inside region_live_v1/ (S-0 enforced)."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def path(self, *rel: str) -> Path:
        p = self.root.joinpath(*rel).resolve()
        if p != self.root and self.root not in p.parents:
            raise StopRun("S-0", "write-guard",
                          f"write outside region_live_v1 refused: {p}")
        return p


def _assert_no_prohibited_modules(where: str) -> None:
    hits = [m for m in sys.modules
            for p in _PROHIBITED_MODULES if m == p or m.startswith(p + ".")]
    if hits:
        raise StopRun("S-0", "prohibited-modules",
                      f"prohibited module(s) loaded ({where}): {sorted(set(hits))}")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _py(o: Any):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _dump_json(obj: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_py)


def _atomic_write_text(text: str, path: Path) -> None:
    """tmp-then-os.replace atomic write (Phase-3 artifact contract)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _atomic_write_json(obj: Dict[str, Any], path: Path) -> None:
    _atomic_write_text(json.dumps(obj, indent=2, default=_py), path)


def _atomic_write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def _theta_sha(v: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(np.asarray(v, dtype="float64")).tobytes()).hexdigest()


def _git_state(repo: Path) -> Dict[str, Any]:
    def run(*a: str) -> Optional[str]:
        try:
            r = subprocess.run(["git", "-C", str(repo), *a],
                               capture_output=True, text=True, timeout=15)
            return r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            return None
    head = run("rev-parse", "HEAD")
    dirty = run("status", "--porcelain")
    return {"repo": str(repo), "head": head,
            "dirty": bool(dirty) if dirty is not None else None}


def _canonical_prior(log_prior: np.ndarray) -> np.ndarray:
    return np.clip(np.exp(np.clip(np.asarray(log_prior, dtype="float64"),
                                  -700, 700)), 1e-16, None)


# --------------------------------------------------------------------------- #
# G-0 — frozen-inputs gate (Phase 1 precondition; D-1 v2)
# --------------------------------------------------------------------------- #
def gate_g0(cfg: Dict[str, Any], log) -> Dict[str, Any]:
    fi = cfg["frozen_inputs"]
    ev: Dict[str, Any] = {"checked_at": _utcnow(), "items": {}, "ok": True}

    def check_file(key: str, path: Path, expected_sha: Optional[str]) -> Optional[str]:
        item: Dict[str, Any] = {"path": str(path), "exists": path.is_file()}
        if item["exists"]:
            item["sha256"] = _sha256(path)
            item["size"] = path.stat().st_size
            if expected_sha:
                item["sha256_expected"] = expected_sha
                item["sha256_match"] = (item["sha256"] == expected_sha)
                item["ok"] = item["sha256_match"]
            else:
                item["ok"] = True
        else:
            item["ok"] = False
        ev["items"][key] = item
        if not item["ok"]:
            ev["ok"] = False
        return item.get("sha256")

    # certified spec + warm start + raw + gsur lookup + stored thetas + frames
    check_file("certified_spec_yaml", MNL_ROOT / cfg["certified_spec"]["yaml"],
               cfg["certified_spec"]["sha256"])
    check_file("warm_start_theta_csv", MNL_ROOT / cfg["warm_start"]["theta_csv"],
               cfg["warm_start"]["sha256"])
    check_file("raw_fr_txt", Path(fi["raw_fr_txt"]["path"]), fi["raw_fr_txt"]["sha256"])
    check_file("gsur_lookup", Path(fi["gsur_lookup"]["path"]), fi["gsur_lookup"]["sha256"])
    st = cfg["stored_region_live_theta"]
    check_file("stored_theta_v1", MNL_ROOT / st["v1_csv"], st["v1_sha256"])
    check_file("stored_theta_v2", MNL_ROOT / st["v2_csv"], st["v2_sha256"])
    for i, fr in enumerate(cfg["comparison_frames"]):
        check_file(f"comparison_frame_{i}", MNL_ROOT / fr["path"], fr["sha256"])
    check_file("comparison_mnlmeta", MNL_ROOT / cfg["comparison_mnlmeta"]["path"],
               cfg["comparison_mnlmeta"]["sha256"])

    # pricing cache: 8 chunks, hashes, coverage
    pc = fi["pricing_cache"]
    pdir = MNL_ROOT / pc["dir"]
    chunks_ok, frames = True, []
    for i in pc["chunk_grid"]:
        name = f"priced_{i:05d}.parquet"
        sha = check_file(f"pricing_{name}", pdir / name, pc["sha256"][name])
        if sha is None or not ev["items"][f"pricing_{name}"]["ok"]:
            chunks_ok = False
        elif ev["items"][f"pricing_{name}"]["ok"]:
            frames.append(pd.read_parquet(pdir / name))
    pcheck: Dict[str, Any] = {"chunks_ok": chunks_ok}
    if chunks_ok and len(frames) == len(pc["chunk_grid"]):
        priced = pd.concat(frames, ignore_index=True)
        pcheck.update(
            rows=int(len(priced)), rows_expected=pc["expected_rows_total"],
            hh=int(priced["source_idhh"].nunique()), hh_expected=pc["expected_hh"],
            columns=sorted(priced.columns.tolist()),
            columns_match=(sorted(priced.columns) == sorted(pc["columns"])),
        )
        pcheck["ok"] = (pcheck["rows"] == pcheck["rows_expected"]
                        and pcheck["hh"] == pcheck["hh_expected"]
                        and pcheck["columns_match"])
        ev["_priced_df"] = priced          # handed to Phase 1 (not serialized)
    else:
        pcheck["ok"] = False
    ev["items"]["pricing_cache_contract"] = {k: v for k, v in pcheck.items()
                                             if k != "_priced_df"}
    if not pcheck["ok"]:
        ev["ok"] = False

    # frozen draw-geometry artifact (stabilization deliverable)
    ge = fi["draws_geometry"]
    gpath, mpath = MNL_ROOT / ge["parquet"], MNL_ROOT / ge["meta"]
    gitem: Dict[str, Any] = {"parquet": str(gpath), "meta": str(mpath),
                             "parquet_exists": gpath.is_file(),
                             "meta_exists": mpath.is_file()}
    if not (gitem["parquet_exists"] and gitem["meta_exists"]):
        gitem["ok"] = False
        gitem["reason"] = ("frozen draws_p2a geometry artifact MISSING - notebook "
                           "stabilization (fr_singles_pipeline_v2.ipynb geometry-freeze "
                           "cell) has not been executed; Phase 1 may not start (D-1 v2). "
                           "The runner is prohibited from regenerating draws and from "
                           "substituting an engine-ready parquet.")
    else:
        meta = json.loads(mpath.read_text(encoding="utf-8"))
        gitem["sha256"] = _sha256(gpath)
        gitem["sha256_meta_declared"] = meta.get("sha256")
        gitem["sha256_match"] = (gitem["sha256"] == meta.get("sha256"))
        gitem["seed"] = meta.get("seed")
        gitem["seed_ok"] = (meta.get("seed") == ge["expected_seed"])
        geo = pd.read_parquet(gpath)
        gitem["rows"] = int(len(geo))
        gitem["rows_ok"] = (len(geo) == ge["expected_rows"])
        sz = geo.groupby("idhh").size() if "idhh" in geo.columns else pd.Series(dtype=int)
        gitem["hh"] = int(sz.shape[0])
        gitem["alts_ok"] = bool((sz == ge["expected_alts_per_hh"]).all()) if len(sz) else False
        missing = [c for c in ge["required_columns"] if c not in geo.columns]
        gitem["missing_required_columns"] = missing
        ch = geo[geo["draw"] == 0] if "draw" in geo.columns else pd.DataFrame()
        gitem["chosen_contract_ok"] = bool(
            len(ch) == ge["expected_hh"]
            and (pd.to_numeric(ch.get("log_prior"), errors="coerce") == 0).all()
            and (pd.to_numeric(ch.get("is_chosen"), errors="coerce") == 1).all()
        ) if len(ch) else False
        gitem["ok"] = bool(gitem["sha256_match"] and gitem["seed_ok"] and gitem["rows_ok"]
                           and gitem["alts_ok"] and not missing and gitem["chosen_contract_ok"])
        if gitem["ok"]:
            ev["_geometry_df"] = geo
    ev["items"]["draws_geometry"] = gitem
    if not gitem["ok"]:
        ev["ok"] = False

    log(f"G-0 frozen-inputs gate: {'PASS' if ev['ok'] else 'FAIL'}")
    for k, v in ev["items"].items():
        if isinstance(v, dict) and not v.get("ok", True):
            log(f"  G-0 FAIL item: {k}: "
                f"{v.get('reason', 'missing or hash/contract mismatch')}")
    return ev


# --------------------------------------------------------------------------- #
# Phase 1 — deterministic pre-assembly (checkpoint cells 2-27, exact port)
# --------------------------------------------------------------------------- #
def _classify_households(raw: pd.DataFrame) -> pd.DataFrame:
    ADULT = FUNNEL_CONFIG["age_range"][0]
    idp = pd.to_numeric(raw["idpartner"], errors="coerce").fillna(0).astype("int64")
    id2partner = dict(zip(raw["idperson"].astype("int64"), idp))
    idset = set(raw["idperson"].astype("int64"))

    def _mutual(a: int, b: int) -> bool:
        return b != 0 and b in idset and id2partner.get(b, 0) == a

    cls: Dict[Any, str] = {}
    for hh, g in raw.groupby("idhh"):
        ad = g[pd.to_numeric(g["dag"], errors="coerce") >= ADULT]
        n = len(ad)
        if n == 0:
            cls[hh] = "excl_no_adult"
        elif n == 1:
            cls[hh] = "single" if int(ad["idpartner"].iloc[0]) == 0 else "excl_2adult_no_link"
        elif n == 2:
            a, b = ad["idperson"].astype("int64").tolist()
            if _mutual(a, b) and _mutual(b, a):
                gens = sorted(pd.to_numeric(ad["dgn"], errors="coerce").tolist())
                cls[hh] = "couple_mf" if gens == [0, 1] else "excl_same_sex"
            else:
                cls[hh] = "excl_2adult_no_link"
        else:
            cls[hh] = "excl_3plus_adults"

    raw = raw.copy()
    raw["household_class"] = raw["idhh"].map(cls)
    raw["ruro_decider"] = (raw["household_class"].isin(["single", "couple_mf"])
                           & (pd.to_numeric(raw["dag"], errors="coerce") >= ADULT)).astype(int)
    return raw


def _run_funnel(raw: pd.DataFrame, log) -> Tuple[pd.DataFrame, Dict[str, int], Dict[str, int]]:
    C = FUNNEL_CONFIG
    counts: Dict[str, int] = {}
    mut: Dict[str, int] = {}

    def keep_all_deciders(df: pd.DataFrame, cond: pd.Series) -> pd.DataFrame:
        dec = df["ruro_decider"] == 1
        bad = df.loc[dec & ~cond.reindex(df.index), "idhh"]
        return df[~df["idhh"].isin(pd.unique(bad))].copy()

    def drop_hh(df: pd.DataFrame, bad_idhh: pd.Series) -> pd.DataFrame:
        return df[~df["idhh"].isin(pd.unique(bad_idhh))].copy()

    work = raw[raw["household_class"].isin(["single", "couple_mf"])].copy()
    counts["baseline"] = int(work["idhh"].nunique())

    lo, hi = C["age_range"]
    dag = pd.to_numeric(work["dag"], errors="coerce")
    work = keep_all_deciders(work, dag.between(lo, hi))
    counts["age"] = int(work["idhh"].nunique())

    if "dec" in work.columns:
        dec = pd.to_numeric(work["dec"], errors="coerce")
        work = keep_all_deciders(work, dec.eq(0))
    counts["education"] = int(work["idhh"].nunique())

    rc = [c for c in C["retire_cols"] if c in work.columns]
    if rc:
        retire = work[rc].apply(pd.to_numeric, errors="coerce").fillna(0.0).sum(axis=1)
        work["_retire"] = retire
        hh_retire = work.groupby("idhh")["_retire"].sum()
        work = drop_hh(work, hh_retire.index[hh_retire > 0]).drop(columns="_retire")
    counts["retirement"] = int(work["idhh"].nunique())

    les = pd.to_numeric(work["les"], errors="coerce")
    work = keep_all_deciders(work, les.isin(C["allowed_les"]))
    counts["les"] = int(work["idhh"].nunique())

    lo, hi = C["age_range"]
    thr = C["other_member_income_threshold"]
    nondec = work["ruro_decider"] == 0
    dag = pd.to_numeric(work["dag"], errors="coerce")
    ddi = pd.to_numeric(work.get("ddi", 0), errors="coerce").fillna(0)
    dec = pd.to_numeric(work.get("dec", 0), errors="coerce").fillna(0)
    yem = pd.to_numeric(work.get("yem", 0.0), errors="coerce").fillna(0.0)
    yse = pd.to_numeric(work.get("yse", 0.0), errors="coerce").fillna(0.0)
    capable = dag.between(lo, hi) & ddi.eq(0) & dec.eq(0)
    earning = (yem > thr) | (yse.abs() > thr)
    work = drop_hh(work, work.loc[nondec & (capable | earning), "idhh"])
    counts["other_members"] = int(work["idhh"].nunique())

    cap, floor, inact = C["hours_cap_high"], C["hours_floor_low"], C["hours_inactive_threshold"]
    wlo, whi = C["wage_bounds"]
    dec_mask = work["ruro_decider"] == 1
    les = pd.to_numeric(work["les"], errors="coerce")
    lhw = pd.to_numeric(work["lhw"], errors="coerce").fillna(0.0)
    emp = dec_mask & les.eq(3)

    mut["capped_over_70h"] = int((emp & (lhw > cap)).sum())
    work.loc[emp & (lhw > cap), "lhw"] = cap
    lhw = pd.to_numeric(work["lhw"], errors="coerce").fillna(0.0)
    work.loc[emp & (lhw > inact) & (lhw <= floor), "lhw"] = floor
    lhw = pd.to_numeric(work["lhw"], errors="coerce").fillna(0.0)

    very_low = emp & (lhw <= inact)
    become_inactive = very_low & les.isin(C["allowed_les"])
    mut["to_inactive_le5h"] = int(become_inactive.sum())
    work.loc[become_inactive, "lhw"] = 0
    work.loc[become_inactive, "les"] = 7
    for c in ("yem", "yse", "yemse"):
        if c in work.columns:
            work.loc[become_inactive, c] = 0.0
    work = drop_hh(work, work.loc[very_low & ~les.isin(C["allowed_les"]), "idhh"])

    les = pd.to_numeric(work["les"], errors="coerce")
    lhw = pd.to_numeric(work["lhw"], errors="coerce").fillna(0.0)
    dec_mask = work["ruro_decider"] == 1
    nonemp_hours = dec_mask & les.isin([5, 7]) & (lhw > 0)
    mut["nonemp_hours_zeroed"] = int(nonemp_hours.sum())
    work.loc[nonemp_hours, "lhw"] = 0

    if "yivwg" in work.columns:
        dec_mask = work["ruro_decider"] == 1
        les = pd.to_numeric(work["les"], errors="coerce")
        yivwg = pd.to_numeric(work["yivwg"], errors="coerce")
        bad_wage = dec_mask & les.eq(3) & yivwg.notna() & ((yivwg < wlo) | (yivwg > whi))
        work = drop_hh(work, work.loc[bad_wage, "idhh"])

    work = work.reset_index(drop=True)
    counts["hours_wage"] = int(work["idhh"].nunique())
    log(f"funnel households: {counts} | mutations: {mut}")
    return work, counts, mut


def _build_features(work: pd.DataFrame, log) -> pd.DataFrame:
    from dclaborsupply_app.de.data_prep import collapse_loc_to_loc4

    df = work.copy()
    lhw = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
    les = pd.to_numeric(df["les"], errors="coerce")

    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0)
        use_lma = bool((lma == 1).any() and lma.nunique(dropna=True) > 1)
    else:
        use_lma = False
    if use_lma:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0)
        df["is_worker"] = ((lma == 1) & (lhw > 0)).astype("int8")
    else:
        df["is_worker"] = (les.eq(3) & (lhw > 0)).astype("int8")
    df["working"] = (lhw > 0).astype("int8")

    df["working_pt1"] = ((lhw >= 18.5) & (lhw <= 20.5)).astype("int8")
    df["working_pt2"] = ((lhw >= 29.5) & (lhw <= 30.5)).astype("int8")
    df["working_ft"] = ((lhw >= 37.5) & (lhw <= 40.5)).astype("int8")
    df["working_lh"] = ((df["working"] == 1) & (lhw >= 44.5) & (lhw <= 70.0)).astype("int8")

    deh = pd.to_numeric(df["deh"], errors="coerce")
    df["educL"] = deh.isin([0, 1, 2]).astype("int8")
    df["educM"] = deh.isin([3, 4]).astype("int8")
    df["educH"] = deh.eq(5).astype("int8")

    yivwg = pd.to_numeric(df["yivwg"], errors="coerce").fillna(0.0)
    df["wage_for_draws"] = yivwg
    df["wage_ruro"] = np.where(df["is_worker"].to_numpy() == 1, yivwg.to_numpy(), 0.0)

    dagn = pd.to_numeric(df["dag"], errors="coerce")
    mean_age = float(dagn[df["ruro_decider"] == 1].mean())
    df["age_norm"] = dagn - mean_age
    df["age_norm2"] = df["age_norm"] ** 2
    df["female"] = (pd.to_numeric(df["dgn"], errors="coerce") == 0).astype("int8")

    if "loc" not in df.columns:
        raise StopRun("S-1", "G-18", "raw occupation column 'loc' missing; cannot build loc4")
    if "loc_raw" not in df.columns:
        df["loc_raw"] = df["loc"]
    loc_src = pd.to_numeric(df["loc"], errors="coerce").fillna(-2).astype("int16")
    isw = pd.to_numeric(df["is_worker"], errors="coerce").fillna(0).astype(int)
    df["loc_ruro"] = loc_src
    valid_worker_loc = loc_src.isin(list(range(0, 10)))
    df.loc[(isw == 1) & ~valid_worker_loc, "loc_ruro"] = -2
    df.loc[isw != 1, "loc_ruro"] = -1
    loc4, loc_armed = collapse_loc_to_loc4(df["loc_ruro"])
    df["loc4"] = loc4.astype("int16")
    df["loc_armed"] = loc_armed.astype("int8")

    model_worker = isw == 1
    bad_worker = model_worker & ~pd.to_numeric(df["loc4"], errors="coerce").isin([-2, 1, 2, 3, 4])
    bad_nonworker = (~model_worker) & (pd.to_numeric(df["loc4"], errors="coerce") != -1)
    if bad_worker.any() or bad_nonworker.any():
        raise StopRun("S-1", "G-18", "loc4 state contract violated in feature build")
    log(f"features built: workers={int(isw.sum())}, "
        f"unknown-occ workers={int((model_worker & (df['loc4'] == -2)).sum())}")
    return df


def _restrict_singles(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    singles_df = df[df["household_class"] == "single"].reset_index(drop=True)
    singles_dec = singles_df[singles_df["ruro_decider"] == 1].reset_index(drop=True)
    if "educ3" not in singles_dec.columns:
        singles_dec["educ3"] = np.select(
            [singles_dec["educL"] == 1, singles_dec["educM"] == 1, singles_dec["educH"] == 1],
            [0, 1, 2], default=-1).astype(int)
    return singles_df.copy(), singles_dec


def _merge_gsur_pexp(singles_dec: pd.DataFrame, cfg: Dict[str, Any], log) -> pd.DataFrame:
    lkp_path = Path(cfg["frozen_inputs"]["gsur_lookup"]["path"])
    lkp = pd.read_parquet(lkp_path)
    lkp = lkp.loc[lkp["gsur"].notna(), ["drgn1", "educ3", "sex", "gsur"]]
    if not (len(lkp) == cfg["frozen_inputs"]["gsur_lookup"]["n_valid_rows"]
            and lkp["gsur"].between(0, 1).all()):
        raise StopRun("S-1", "G-18", f"gsur lookup contract violated ({len(lkp)} valid rows)")
    keys = pd.DataFrame({
        "drgn1": pd.to_numeric(singles_dec["drgn1"], errors="coerce").astype("int64"),
        "educ3": pd.to_numeric(singles_dec["educ3"], errors="coerce").astype("int64"),
        "sex": pd.to_numeric(singles_dec["dgn"], errors="coerce").map({1: "M", 0: "F"}),
    })
    if not keys.notna().all().all():
        raise StopRun("S-1", "G-18", "gsur merge keys contain NaN (dgn/drgn1/educ3)")
    mm = keys.merge(lkp, on=["drgn1", "educ3", "sex"], how="left", validate="many_to_one")
    if not mm["gsur"].notna().all():
        raise StopRun("S-1", "G-18", "gsur match rate < 100%")
    singles_dec = singles_dec.assign(gsur=mm["gsur"].to_numpy())
    log(f"gsur merged: n={len(singles_dec)} "
        f"range [{float(lkp['gsur'].min()):.4f},{float(lkp['gsur'].max()):.4f}]")

    dag = pd.to_numeric(singles_dec["dag"], errors="coerce")
    year = pd.Series(2016.0, index=singles_dec.index)
    p_liwwh = pd.Series(np.nan, index=singles_dec.index)
    if "liwwh" in singles_dec:
        liwwh = pd.to_numeric(singles_dec["liwwh"], errors="coerce")
        p_liwwh = (liwwh / 12.0).where(liwwh.notna() & (liwwh > 0), np.nan)
    p_dew = pd.Series(np.nan, index=singles_dec.index)
    if "dew" in singles_dec:
        dew = pd.to_numeric(singles_dec["dew"], errors="coerce")
        ok = dew.notna() & (dew != -1) & (dew >= 1900) & (dew <= 2100) & (dew <= year)
        p_dew = (year - dew).where(ok, np.nan)
    p_dey = pd.Series(np.nan, index=singles_dec.index)
    if "dey" in singles_dec:
        dey = pd.to_numeric(singles_dec["dey"], errors="coerce")
        ok = dey.notna() & (dey >= 0) & (dey <= 100)
        p_dey = (dag - 6.0 - dey).where(ok, np.nan)
    pexp_raw = p_liwwh.where(p_liwwh.notna(), p_dew).where(lambda s: s.notna(), p_dey)
    cap = (dag - 15.0).clip(lower=0.0)
    singles_dec["pexp_years_raw"] = np.minimum(
        pexp_raw.fillna(0.0).clip(lower=0.0), cap.fillna(0.0)).astype(float)
    singles_dec["pexp_years"] = singles_dec["pexp_years_raw"] / 20.0
    singles_dec["pexp_years2"] = singles_dec["pexp_years"] ** 2
    if not singles_dec["pexp_years"].between(0, 2.6).all():
        raise StopRun("S-1", "G-18", "pexp_years outside [0, 2.6]")
    return singles_dec


def _region_map(singles_dec: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    m = pd.DataFrame({
        "idhh": pd.to_numeric(singles_dec["idhh"], errors="coerce").astype("int64"),
        "idorighh": pd.to_numeric(singles_dec["idorighh"], errors="coerce").astype("int64"),
        "drgn1": pd.to_numeric(singles_dec["drgn1"], errors="coerce").astype("float64"),
        "drgur": pd.to_numeric(singles_dec["drgur"], errors="coerce").astype("float64"),
        "drgmd": pd.to_numeric(singles_dec["drgmd"], errors="coerce").astype("float64"),
        "drgru": pd.to_numeric(singles_dec["drgru"], errors="coerce").astype("float64"),
        "gsur": pd.to_numeric(singles_dec["gsur"], errors="coerce").astype("float64"),
        "educ3": pd.to_numeric(singles_dec["educ3"], errors="coerce").astype("int64"),
        "sex": pd.to_numeric(singles_dec["dgn"], errors="coerce").map({1: "M", 0: "F"}),
    })
    exp = cfg["phase1_expected"]
    checks = {
        "n_rows": int(len(m)),
        "n_rows_ok": len(m) == exp["n_hh_singles"],
        "idhh_unique": bool(m["idhh"].is_unique),
        "no_missing": bool(m.notna().all().all()),
        "drgn1_support_ok": bool(m["drgn1"].between(1, 8).all()),
        "drgn1_counts": {int(k): int(v) for k, v in
                         m["drgn1"].value_counts().sort_index().items()},
        "drgn1_counts_ok": ({int(k): int(v) for k, v in
                             m["drgn1"].value_counts().sort_index().items()}
                            == {int(k): int(v) for k, v in exp["drgn1_counts"].items()}),
        "urbanisation_one_hot_ok": bool((m[["drgur", "drgmd", "drgru"]].sum(axis=1) == 1).all()
                                        and m[["drgur", "drgmd", "drgru"]].isin([0.0, 1.0]).all().all()),
        "gsur_in_range_ok": bool(m["gsur"].between(*exp["gsur_range"]).all()),
        "gsur_nunique": int(m["gsur"].nunique()),
        "gsur_nunique_ok": int(m["gsur"].nunique()) == exp["gsur_nunique"],
        "gsur_mean": float(m["gsur"].mean()),
    }
    checks["ok"] = all(v for k, v in checks.items() if k.endswith("_ok")) \
        and checks["idhh_unique"] and checks["no_missing"]
    return m, checks


def _takeup_traits(priced: pd.DataFrame, singles_dec: pd.DataFrame,
                   cfg: Dict[str, Any], log) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    exp = cfg["phase1_expected"]
    rng_seed = int(exp["takeup_seed"])
    d0 = (priced[(priced["ruro_decider"] == 1) & (priced["draw"] == 0)]
          [["source_idhh", "source_idorighh", "bsa00_s"]].rename(columns={"bsa00_s": "ent0"}))
    tt = d0.merge(
        singles_dec[["idhh", "is_worker"]].assign(
            reported=pd.to_numeric(singles_dec.get("bsa00", 0), errors="coerce").fillna(0) > 0),
        left_on="source_idhh", right_on="idhh", how="left")
    tt["entitled0"] = tt["ent0"] > 0
    nw, wk = tt[tt.is_worker == 0], tt[tt.is_worker == 1]
    rate_nw = float(nw.loc[nw.entitled0, "reported"].mean())
    rate_w = float(wk.loc[wk.entitled0, "reported"].mean())
    tt = tt.sort_values("source_idorighh").reset_index(drop=True)
    rng = np.random.default_rng(rng_seed)
    bern_nw = rng.random(len(tt)) < rate_nw
    bern_w = rng.random(len(tt)) < rate_w
    revealed = tt["entitled0"] | tt["reported"]
    own_taker = tt["reported"]
    tt["takeup_nw"] = np.where(tt.is_worker == 0, np.where(revealed, own_taker, bern_nw), bern_nw)
    tt["takeup_w"] = np.where(tt.is_worker == 1, np.where(revealed, own_taker, bern_w), bern_w)
    trait = tt[["source_idhh", "takeup_nw", "takeup_w"]]
    ev = {
        "seed": rng_seed,
        "rate_nw": round(rate_nw, 3), "rate_nw_expected": exp["takeup_rate_nw"],
        "rate_w": round(rate_w, 3), "rate_w_expected": exp["takeup_rate_w"],
        "n_entitled_nw": int(nw.entitled0.sum()), "n_entitled_w": int(wk.entitled0.sum()),
        "share_nw": round(float(trait["takeup_nw"].mean()), 3),
        "share_w": round(float(trait["takeup_w"].mean()), 3),
    }
    ev["ok"] = (ev["rate_nw"] == ev["rate_nw_expected"]
                and ev["rate_w"] == ev["rate_w_expected"])
    log(f"take-up traits: nw={ev['rate_nw']} w={ev['rate_w']} "
        f"(expected {ev['rate_nw_expected']}/{ev['rate_w_expected']}) ok={ev['ok']}")
    return trait, ev


def _assemble_er_b(geo: pd.DataFrame, priced: pd.DataFrame, trait: pd.DataFrame,
                   singles_df: pd.DataFrame, singles_dec: pd.DataFrame,
                   region_map: pd.DataFrame, cfg: Dict[str, Any], log
                   ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    from dclaborsupply_app.de.engine_ready import assemble_singles

    exp = cfg["phase1_expected"]
    ev: Dict[str, Any] = {}

    # feat2 — checkpoint cell 37 first half (exact port)
    feat2 = geo.copy()
    dagm = pd.to_numeric(singles_dec.set_index("idhh")["dag"], errors="coerce")
    feat2["age_norm"] = (feat2["idhh_true"].map(dagm) - float(dagm.mean())) / 10.0
    feat2["age_norm2"] = feat2["age_norm"] ** 2
    kid = pd.to_numeric(singles_df["dag"], errors="coerce") < FUNNEL_CONFIG["age_range"][0]
    feat2["n_children"] = feat2["idhh_true"].map(
        kid.groupby(singles_df["idhh"]).sum()).fillna(0).astype("int16")
    feat2["source_idhh"] = feat2["idhh_true"]
    feat2["source_idorighh"] = pd.to_numeric(feat2["idorighh"], errors="coerce").astype("int64")
    if "educM" not in feat2.columns:
        feat2["educM"] = (pd.to_numeric(feat2["educ3"], errors="coerce") == 1).astype(float)
    if "prior" not in feat2.columns:
        feat2["prior"] = _canonical_prior(
            pd.to_numeric(feat2["log_prior"], errors="coerce").to_numpy())

    # draw-0 unknown-occupation mode imputation (checkpoint rule)
    h0 = pd.to_numeric(feat2["hours"], errors="coerce").fillna(0.0)
    l40 = pd.to_numeric(feat2["loc4"], errors="coerce").fillna(-2).astype(int)
    bad0 = (h0 > 0) & ~l40.isin([1, 2, 3, 4])
    n_bad0 = int(bad0.sum())
    if n_bad0:
        if not (pd.to_numeric(feat2.loc[bad0, "draw"], errors="coerce") == 0).all():
            raise StopRun("S-1", "G-18",
                          "non-draw-0 working rows with invalid loc4 in frozen geometry")
        pool0 = pd.to_numeric(
            singles_dec.loc[(pd.to_numeric(singles_dec["is_worker"], errors="coerce") == 1)
                            & pd.to_numeric(singles_dec["loc4"], errors="coerce").isin([1, 2, 3, 4]),
                            "loc4"], errors="coerce").astype(int).to_numpy()
        mode0 = int(np.argmax(np.bincount(pool0, minlength=5)[1:5]) + 1)
        feat2.loc[bad0, "loc4"] = mode0
    else:
        mode0 = None
    ev["draw0_mode_imputed_rows"] = n_bad0
    ev["draw0_mode_imputed_loc4"] = mode0
    ev["mode_imputation_ok"] = (n_bad0 == exp["draw0_mode_imputed_rows"]
                                and mode0 == exp["draw0_mode_imputed_loc4"])

    pre_bands = feat2[["source_idhh", "draw", *BAND_COLS]].copy()

    # take-up income mask + assembly (checkpoint cell 37 second half)
    pm2 = (priced.merge(feat2[["source_idhh", "draw", "hours"]].drop_duplicates(),
                        on=["source_idhh", "draw"])
                 .merge(trait, on="source_idhh", how="left"))
    take = np.where(pm2["hours"] > 0, pm2["takeup_w"], pm2["takeup_nw"]).astype(bool)
    pm2["ils_dispy_takeup"] = (pd.to_numeric(pm2["ils_dispy"])
                               - pd.to_numeric(pm2["bsa00_s"]).fillna(0) * (~take))

    er_p2a = assemble_singles(pm2, feat2, alt_keys=("draw",),
                              income_source="ils_dispy_takeup")
    ev["er_rows"] = int(len(er_p2a))
    ev["er_cols"] = int(er_p2a.shape[1])
    ev["er_chosen"] = int(pd.to_numeric(er_p2a["is_chosen"]).sum())
    ev["er_shape_ok"] = (len(er_p2a) == exp["er_rows"]
                         and ev["er_chosen"] == exp["n_hh_singles"])
    log(f"assembled er_p2a: {er_p2a.shape} chosen={ev['er_chosen']}")

    # band-convention comparison (assembler recompute vs bpool flags)
    post = er_p2a[["source_idhh", "draw", *BAND_COLS]]
    cmpb = pre_bands.merge(post, on=["source_idhh", "draw"], suffixes=("_bpool", "_asm"))
    reflag = {b: int((cmpb[f"{b}_bpool"] != cmpb[f"{b}_asm"]).sum()) for b in BAND_COLS}
    ev["band_reflag_counts"] = reflag
    ev["band_reflag_ok"] = (reflag == {k: int(v) for k, v in
                                       exp["band_reflag_counts"].items()})

    # 12b revival — independently from the source mapping (never an engine-ready frame)
    src = region_map.set_index("idhh")
    for c in REVIVED_COLS:
        er_p2a[c] = er_p2a["idhh"].map(pd.to_numeric(src[c], errors="coerce")).astype("float64")
    s = er_p2a.groupby("idhh")[REVIVED_COLS].first()
    rev = {
        "drgn1_support_ok": bool(s["drgn1"].between(1, 8).all()),
        "urbanisation_one_hot_ok": bool((s[["drgur", "drgmd", "drgru"]].sum(axis=1) == 1).all()),
        "gsur_ok": bool(s["gsur"].between(0.05, 0.23).all() and s["gsur"].nunique() > 1),
        "drgn1_counts": {int(k): int(v) for k, v in
                         s["drgn1"].value_counts().sort_index().items()},
        "gsur_hh_mean": float(s["gsur"].mean()),
        "gsur_nunique": int(s["gsur"].nunique()),
        "within_household_constancy_ok": bool(
            (er_p2a.groupby("idhh")[REVIVED_COLS].nunique() == 1).all().all()),
    }
    rev["drgn1_counts_ok"] = (rev["drgn1_counts"]
                              == {int(k): int(v) for k, v in exp["drgn1_counts"].items()})
    # no cross-household leakage: engine rows equal the mapping row for that idhh exactly
    leak = er_p2a[["idhh", *REVIVED_COLS]].merge(
        region_map[["idhh", *REVIVED_COLS]], on="idhh", suffixes=("", "_map"))
    rev["no_leakage_ok"] = bool(all(
        (leak[c] == leak[f"{c}_map"]).all() for c in REVIVED_COLS))
    rev["ok"] = all(v for k, v in rev.items() if k.endswith("_ok"))
    ev["revival"] = rev
    log(f"revival: drgn1 counts ok={rev['drgn1_counts_ok']} "
        f"gsur mean={rev['gsur_hh_mean']:.4f} n_unique={rev['gsur_nunique']}")

    # B-pool band overwrite -> er_b (checkpoint cell 40)
    er_b = er_p2a.merge(pre_bands, on=["source_idhh", "draw"], suffixes=("", "_bpool"))
    for b in BAND_COLS:
        er_b[b] = er_b[f"{b}_bpool"]
        er_b.drop(columns=f"{b}_bpool", inplace=True)
    nz = er_b.loc[pd.to_numeric(er_b["working"]) == 0, BAND_COLS]
    ev["bpool_nonworking_zero_ok"] = bool((nz == 0).all().all())
    ev["er_b_shape"] = [int(x) for x in er_b.shape]
    ev["er_b_cols_expected_checkpoint"] = exp["er_cols_checkpoint"]
    ev["ok"] = (ev["mode_imputation_ok"] and ev["er_shape_ok"] and ev["band_reflag_ok"]
                and rev["ok"] and ev["bpool_nonworking_zero_ok"])
    return er_b, ev


def _freeze_and_reconcile(er_b: pd.DataFrame, region_map: pd.DataFrame,
                          out: OutRoot, cfg: Dict[str, Any], log
                          ) -> Tuple[Dict[str, Any], Dict[str, str]]:
    exp = cfg["phase1_expected"]
    stem = cfg["run"]["frozen_stem_name"]
    atol = float(cfg["gates"]["g18_frame_reconciliation_atol"])

    # freeze the canonical stem
    p_parquet = out.path(f"{stem}__singles.parquet")
    p_meta = out.path(f"{stem}__mnlmeta.json")
    er_b.to_parquet(p_parquet)
    c_scale = float(er_b["c_scale"].iloc[0])
    l_scale = float(er_b["l_scale"].iloc[0])
    mnlmeta = {
        "source": "P2a bpool draws (101 alts/HH)",
        "produced_by": "scripts/p2a/run_p2a_regionlive_rebuild.py",
        "n_draws": {"singles": 101},
        "normalization": {"singles": {"c_scale": c_scale, "l_scale": l_scale,
                                      "n_chosen": int(exp["n_hh_singles"])}},
        "row_counts": {"singles": int(len(er_b)), "total": int(len(er_b))},
        "cluster_key": {"cluster_id_col": "cluster_id", "source_col": "idorighh"},
        "prior_convention": "prior=clip(exp(clip(log_prior,-700,700)),1e-16,None)",
    }
    _dump_json(mnlmeta, p_meta)

    # reconcile normalization scales against the committed adapter mnlmeta
    cmp_meta = json.loads((MNL_ROOT / cfg["comparison_mnlmeta"]["path"]).read_text())
    n0 = cmp_meta["normalization"]["singles"]
    rec: Dict[str, Any] = {
        "c_scale": c_scale, "l_scale": l_scale,
        "c_scale_committed": float(n0["c_scale"]), "l_scale_committed": float(n0["l_scale"]),
        "scales_ok": (abs(c_scale - float(n0["c_scale"])) <= atol
                      and abs(l_scale - float(n0["l_scale"])) <= atol),
    }

    # frame reconciliation — comparison artifacts only, never inputs
    frames = cfg["comparison_frames"]
    shas = {f["path"]: _sha256(MNL_ROOT / f["path"]) for f in frames}
    rec["comparison_frame_sha256"] = shas
    rec["frames_byte_identical"] = (len(set(shas.values())) == 1)

    ref = pd.read_parquet(MNL_ROOT / frames[0]["path"])
    a = er_b.sort_values(["source_idhh", "draw"], kind="mergesort").reset_index(drop=True)
    b = ref.sort_values(["source_idhh", "draw"], kind="mergesort").reset_index(drop=True)
    rec["rebuilt_shape"] = [int(x) for x in a.shape]
    rec["reference_shape"] = [int(x) for x in b.shape]
    cols_a, cols_b = set(a.columns), set(b.columns)
    rec["columns_only_in_rebuilt"] = sorted(cols_a - cols_b)
    rec["columns_only_in_reference"] = sorted(cols_b - cols_a)
    common = sorted(cols_a & cols_b)
    missing_engine = [c for c in ENGINE_CONSUMED_COLS if c not in common]
    rec["engine_consumed_missing_from_common"] = missing_engine

    diffs: Dict[str, Any] = {}
    n_bad_cols = 0
    if len(a) == len(b):
        for c in common:
            va, vb = a[c], b[c]
            na = pd.to_numeric(va, errors="coerce")
            nb = pd.to_numeric(vb, errors="coerce")
            if na.notna().all() and nb.notna().all():
                d = float(np.max(np.abs(na.to_numpy(dtype="float64")
                                        - nb.to_numpy(dtype="float64")))) if len(na) else 0.0
                ok = d <= atol
                if not ok or d > 0:
                    diffs[c] = {"max_abs_diff": d, "ok": ok}
                if not ok:
                    n_bad_cols += 1
            else:
                eq = bool((va.astype(str) == vb.astype(str)).all())
                if not eq:
                    diffs[c] = {"equal": False, "ok": False}
                    n_bad_cols += 1
    rec["n_common_columns"] = len(common)
    rec["column_diffs"] = diffs
    rec["rows_match"] = (len(a) == len(b))
    rec["values_ok"] = (rec["rows_match"] and n_bad_cols == 0)

    # idempotence: applying the source mapping to the reference reproduces it unchanged
    src = region_map.set_index("idhh")
    idem_ok = True
    for c in REVIVED_COLS:
        mapped = b["idhh"].map(pd.to_numeric(src[c], errors="coerce")).astype("float64")
        if not np.allclose(mapped.to_numpy(),
                           pd.to_numeric(b[c], errors="coerce").to_numpy(),
                           rtol=0.0, atol=atol):
            idem_ok = False
    rec["five_column_idempotence_ok"] = idem_ok

    rec["ok"] = (rec["scales_ok"] and rec["frames_byte_identical"] and rec["values_ok"]
                 and not rec["columns_only_in_reference"] and not missing_engine
                 and idem_ok)
    log(f"reconciliation: frames byte-identical={rec['frames_byte_identical']} "
        f"values_ok={rec['values_ok']} n_diff_cols={n_bad_cols} idempotence={idem_ok}")

    hashes = {f"{stem}__singles.parquet": _sha256(p_parquet),
              f"{stem}__mnlmeta.json": _sha256(p_meta)}
    return rec, hashes


# --------------------------------------------------------------------------- #
# Phase 2 — package load + objective reproduction (G-19; NO optimizer)
# --------------------------------------------------------------------------- #
def phase2(out: OutRoot, cfg: Dict[str, Any], log) -> Dict[str, Any]:
    from dclaborsupply import EstimationSpec
    from dclaborsupply.spec.parser import load_custom_initial_values
    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll
    from dclaborsupply.likelihood.index import compute_index
    import jax
    import jax.numpy as jnp

    g = cfg["gates"]
    rep: Dict[str, Any] = {"started_at": _utcnow()}

    # ---- specification & binding -------------------------------------------------
    spec_path = MNL_ROOT / cfg["certified_spec"]["yaml"]
    rep["spec_sha256"] = _sha256(spec_path)
    rep["spec_sha256_unchanged"] = (rep["spec_sha256"] == cfg["certified_spec"]["sha256"])
    if not rep["spec_sha256_unchanged"]:
        raise StopRun("S-8", "G-0", "certified spec YAML hash changed mid-run")
    spec = EstimationSpec.from_yaml(str(spec_path))
    names = list(spec.all_param_names)
    rep["n_params"] = len(names)
    rep["param_names"] = names
    rep["wage_spec"] = str(spec.wage_spec)
    rep["fixed_params"] = {k: float(v) for k, v in spec.fixed_params.items()}
    rep["centering"] = {
        "market_opportunity_center_within_choice_set":
            bool(spec.market_opportunity_center_within_choice_set),
        "center_weights": str(spec.market_opportunity_center_weights),
    }
    mos = list(getattr(spec, "market_opportunity_shifters", []) or [])
    rep["occupation_shifters_in_log_market"] = [
        {k: sh.get(k) for k in ("variable", "applies_to")}
        for sh in mos if str(sh.get("variable", "")).startswith("loc4")]
    rep["wage_loc_groups_absent"] = (getattr(spec, "wage_loc_groups", None) in (None, [], {}))
    rep["spec_checks_ok"] = (
        rep["n_params"] == cfg["certified_spec"]["n_params"]
        and rep["wage_spec"] == cfg["certified_spec"]["wage_spec"]
        and rep["fixed_params"] == {k: float(v) for k, v in
                                    cfg["certified_spec"]["fixed_params_expected"].items()}
        and rep["centering"]["market_opportunity_center_within_choice_set"]
        and rep["centering"]["center_weights"] == "proposal"
        and rep["wage_loc_groups_absent"]
        and len(rep["occupation_shifters_in_log_market"]) > 0
    )

    # warm start + pins (bounds clamped to warm-start values — checkpoint mechanism)
    raw_theta = load_custom_initial_values(MNL_ROOT / cfg["warm_start"]["theta_csv"])
    theta0 = np.array([float(raw_theta[n]) for n in names], dtype="float64")
    idx = {n: i for i, n in enumerate(names)}
    pins: List[str] = list(cfg["run_overlay"]["pinned_params"])
    missing_pins = [p for p in pins if p not in idx]
    if missing_pins:
        raise StopRun("S-9", "G-19", f"pinned parameter(s) not in spec: {missing_pins}")
    b4 = list(spec.get_bounds_tuple())
    pin_table = []
    for p in pins:
        b4[idx[p]] = (float(theta0[idx[p]]), float(theta0[idx[p]]))
        pin_table.append({"param": p, "index": idx[p], "pinned_at": float(theta0[idx[p]])})
    free = [n for n in names if n not in set(pins)]
    rep["pins"] = pin_table
    rep["n_pinned"] = len(pins)
    rep["n_free"] = len(free)
    rep["bounds_free"] = [{"param": n, "lb": b4[idx[n]][0], "ub": b4[idx[n]][1]}
                          for n in free]
    rep["overlay_ok"] = (len(pins) == 10
                         and rep["n_free"] == int(cfg["run_overlay"]["n_free_expected"]))

    # ---- stored region-live theta ------------------------------------------------
    st = cfg["stored_region_live_theta"]
    t1 = pd.read_csv(MNL_ROOT / st["v1_csv"]).set_index("param")
    t2 = pd.read_csv(MNL_ROOT / st["v2_csv"]).set_index("param")
    rep["theta_order_v1_ok"] = (list(t1.index) == names)
    rep["theta_order_v2_ok"] = (list(t2.index) == names)
    trial1 = t1[st["value_column"]].astype(float).reindex(names).to_numpy()
    trial2 = t2[st["value_column"]].astype(float).reindex(names).to_numpy()
    rep["trial_v1_vs_v2_max_abs"] = float(np.max(np.abs(trial1 - trial2)))
    rep["trial_v1_vs_v2_ok"] = (rep["trial_v1_vs_v2_max_abs"]
                                <= float(g["trial_v1_v2_equality_atol"]))
    cert2 = t2[st["warmstart_column"]].astype(float).reindex(names).to_numpy()
    cert1 = t1[st["warmstart_column"]].astype(float).reindex(names).to_numpy()
    rep["warmstart_vs_v2_max_abs"] = float(np.max(np.abs(theta0 - cert2)))
    rep["warmstart_vs_v1_max_abs"] = float(np.max(np.abs(theta0 - cert1)))
    rep["warmstart_equality_ok"] = (
        rep["warmstart_vs_v2_max_abs"] <= float(g["warmstart_equality_tol_v2"])
        and rep["warmstart_vs_v1_max_abs"] <= float(g["warmstart_equality_tol_v1"]))
    theta_star = trial1
    rep["theta_star_sha256"] = hashlib.sha256(
        np.ascontiguousarray(theta_star).tobytes()).hexdigest()
    rep["theta_star_source"] = st["v1_csv"]

    # ---- frozen-stem load through the package loader -----------------------------
    stem = cfg["run"]["frozen_stem_name"]
    p_parquet = out.path(f"{stem}__singles.parquet")
    p_meta = out.path(f"{stem}__mnlmeta.json")
    if not (p_parquet.is_file() and p_meta.is_file()):
        raise StopRun("S-9", "G-19", "frozen stem missing — Phase 1 did not complete")
    er = pd.read_parquet(p_parquet)
    meta = json.loads(p_meta.read_text(encoding="utf-8"))
    sm_df = er[pd.to_numeric(er["dgn"]) == 1].reset_index(drop=True)
    sf_df = er[pd.to_numeric(er["dgn"]) == 0].reset_index(drop=True)
    rep["n_hh_sm"] = int(sm_df["idhh"].nunique())
    rep["n_hh_sf"] = int(sf_df["idhh"].nunique())
    rep["split_ok"] = (rep["n_hh_sm"] == int(cfg["phase1_expected"]["n_sm"])
                       and rep["n_hh_sf"] == int(cfg["phase1_expected"]["n_sf"]))
    dm = load_singles(sm_df, spec, is_male=True, metadata=meta)
    df_ = load_singles(sf_df, spec, is_male=False, metadata=meta)

    # loader liveness — region/gsur arrays must be nonzero and equal the frozen columns
    def _liveness(d, frame: pd.DataFrame, tag: str) -> Dict[str, Any]:
        drgn1_col = pd.to_numeric(frame["drgn1"], errors="coerce").to_numpy(dtype="float64")
        lv = {
            "n_groups": int(d.n_groups), "n_obs": int(d.n_obs),
            "reg_means": {f"reg{k}": float(np.mean(getattr(d, f"reg{k}")))
                          for k in range(2, 9)},
            "reg_nonzero_ok": bool(any(np.any(getattr(d, f"reg{k}") != 0)
                                       for k in range(2, 9))),
            "reg_equals_frozen_ok": bool(all(
                np.array_equal(getattr(d, f"reg{k}"),
                               (drgn1_col == k).astype("float64"))
                for k in range(2, 9))),
            "gsur_mean": float(np.mean(d.gsur)),
            "gsur_nonzero_ok": bool(np.any(d.gsur != 0)),
            "gsur_equals_frozen_ok": bool(np.array_equal(
                d.gsur, pd.to_numeric(frame["gsur"], errors="coerce")
                .to_numpy(dtype="float64"))),
            "urb_one_hot_ok": bool(np.all(d.drgur + d.drgmd + d.drgru == 1.0)),
            "urb_equals_frozen_ok": bool(all(
                np.array_equal(getattr(d, c), pd.to_numeric(frame[c], errors="coerce")
                               .to_numpy(dtype="float64"))
                for c in ("drgur", "drgmd", "drgru"))),
            "prior_positive_ok": bool(np.all(d.prior > 0)),
            "log_prior_max_abs_dev": float(np.max(np.abs(
                np.log(np.asarray(d.prior))
                - pd.to_numeric(frame["log_prior"], errors="coerce")
                .to_numpy(dtype="float64")))),
        }
        lv["log_prior_consistent_ok"] = (lv["log_prior_max_abs_dev"]
                                         <= float(g["log_prior_consistency_atol"]))
        lv["ok"] = all(v for k, v in lv.items() if k.endswith("_ok"))
        log(f"loader liveness [{tag}]: reg2 mean={lv['reg_means']['reg2']:.4f} "
            f"gsur mean={lv['gsur_mean']:.4f} ok={lv['ok']}")
        return lv

    rep["liveness_sm"] = _liveness(dm, sm_df, "sm")
    rep["liveness_sf"] = _liveness(df_, sf_df, "sf")

    # cluster resolution (D-6 — self-ratifying under the four conditions)
    cl = np.concatenate([np.asarray(dm.cluster_ids), np.asarray(df_.cluster_ids)])
    n_groups_total = int(dm.n_groups + df_.n_groups)
    k_stem = int(pd.unique(cl[np.isfinite(cl)]).size)
    map_path = out.path("region_map_p2a_singles2016.parquet")
    k_map = int(pd.read_parquet(map_path)["idorighh"].nunique())
    lob, hib = cfg["gates"]["cluster_count_bounds"]
    rep["cluster"] = {
        "column": cfg["cluster"]["column"],
        "n_groups_total": n_groups_total,
        "resolved_t3_count": k_stem,
        "map_idorighh_nunique": k_map,
        "consistency_ok": (k_stem == k_map),
        "no_missing_ok": bool(np.all(np.isfinite(cl))),
        "one_cluster_per_household_ok": (len(cl) == n_groups_total),
        "bounds_ok": (int(lob) <= k_stem <= int(hib)),
    }
    rep["cluster"]["ok"] = all(v for k, v in rep["cluster"].items()
                               if k.endswith("_ok"))

    # ---- objective reproduction (G-19; NO optimizer call anywhere) ---------------
    nm, _ = build_jax_singles_ll(dm, spec, is_male=True)
    nf, _ = build_jax_singles_ll(df_, spec, is_male=False)
    tot = jax.jit(lambda t: nm(t) + nf(t))
    t_j0 = time.time()
    negll_jax = float(tot(jnp.asarray(theta_star)))
    rep["negll_jax"] = negll_jax
    rep["negll_jax_seconds"] = round(time.time() - t_j0, 2)
    t_n0 = time.time()
    negll_np = float(compute_index(spec, (dm, df_, None), theta_star,
                                   ruro=True, backend="numpy"))
    rep["negll_numpy"] = negll_np
    rep["negll_numpy_seconds"] = round(time.time() - t_n0, 2)

    tgt = cfg["targets"]
    rep["target_full"] = float(tgt["negll_full"])
    rep["abs_dev_full"] = abs(negll_jax - float(tgt["negll_full"]))
    rep["abs_dev_4dp"] = abs(negll_jax - float(tgt["negll_4dp"]))
    rep["backend_abs_dev"] = abs(negll_jax - negll_np)
    rep["g19_full_ok"] = rep["abs_dev_full"] <= float(g["g19_theta_eval_tol_full"])
    rep["g19_anchor_ok"] = rep["abs_dev_4dp"] < float(g["g19_anchor_tol_4dp"])
    rep["g19_backend_ok"] = rep["backend_abs_dev"] <= float(g["g19_backend_agreement_tol"])
    log(f"G-19 objective: jax={negll_jax:.10f} numpy={negll_np:.10f} "
        f"|dev_full|={rep['abs_dev_full']:.2e} |jax-np|={rep['backend_abs_dev']:.2e}")

    rep["ok"] = (rep["spec_checks_ok"] and rep["overlay_ok"]
                 and rep["theta_order_v1_ok"] and rep["theta_order_v2_ok"]
                 and rep["trial_v1_vs_v2_ok"] and rep["warmstart_equality_ok"]
                 and rep["split_ok"] and rep["liveness_sm"]["ok"]
                 and rep["liveness_sf"]["ok"] and rep["cluster"]["ok"]
                 and rep["g19_full_ok"] and rep["g19_anchor_ok"]
                 and rep["g19_backend_ok"])
    rep["finished_at"] = _utcnow()
    if not rep["ok"]:
        # persist the evidence before stopping (caller writes the report JSON)
        return rep
    return rep


# --------------------------------------------------------------------------- #
# Phase 3 -- estimation (AUTHORIZED: FR_P2a_region_live_phase12_manager_acceptance_v1.md s9;
# remediated per FR_P2a_region_live_phase3_code_review_v1.md s18, fixes 1-8).
# Consumes the ACCEPTED Phase 1-2 evidence read-only; writes ONLY inside the
# canonical phase3_estimation_v1/ transaction layout. NO Phase-4+ computation.
# --------------------------------------------------------------------------- #
def build_phase3_parameter_map(all_names: Sequence[str], pin_names: Sequence[str],
                               pin_values: Dict[str, float]) -> Dict[str, Any]:
    """Explicit 37-free <-> 47-full mapping (review fix 1 / decision D).

    Asserts: 47 unique full names; 10 unique pins; every pin exists; pin tuple equals
    ACCEPTED_PIN_NAMES exactly (order included, decision E); 37 free; disjoint; union
    complete. Returns integer index arrays and immutable pin values.
    """
    names = list(all_names)
    if len(names) != 47 or len(set(names)) != 47:
        raise StopRun("S-1", "param-map", f"expected 47 unique names, got {len(names)}")
    pins = tuple(pin_names)
    if len(pins) != 10 or len(set(pins)) != 10:
        raise StopRun("S-1", "param-map", f"expected 10 unique pins, got {pins}")
    if pins != ACCEPTED_PIN_NAMES:
        raise StopRun("S-1", "param-map",
                      f"pin list != accepted pin identity (order included): {pins}")
    missing = [p for p in pins if p not in names]
    if missing:
        raise StopRun("S-1", "param-map", f"pin(s) not in spec: {missing}")
    free = [n for n in names if n not in set(pins)]
    if len(free) != 37 or set(free) & set(pins):
        raise StopRun("S-1", "param-map", "free/pin partition invalid")
    if sorted(free + list(pins)) != sorted(names):
        raise StopRun("S-1", "param-map", "free+pins != all names")
    name_idx = {n: i for i, n in enumerate(names)}
    free_idx = np.array([name_idx[n] for n in free], dtype=np.int64)
    pin_idx = np.array([name_idx[p] for p in pins], dtype=np.int64)
    pin_vals = np.array([float(pin_values[p]) for p in pins], dtype=np.float64)
    return {"all_names": names, "free_names": free, "pin_names": list(pins),
            "name_idx": name_idx, "free_idx": free_idx, "pin_idx": pin_idx,
            "pin_values": pin_vals}


def project_full_to_free(pmap: Dict[str, Any], full: np.ndarray) -> np.ndarray:
    full = np.asarray(full, dtype=np.float64)
    if full.shape != (47,):
        raise StopRun("S-1", "param-map", f"full vector shape {full.shape} != (47,)")
    return full[pmap["free_idx"]].copy()


def expand_free_to_full(pmap: Dict[str, Any], free_vec: np.ndarray) -> np.ndarray:
    free_vec = np.asarray(free_vec, dtype=np.float64)
    if free_vec.shape != (37,):
        raise StopRun("S-1", "param-map", f"free vector shape {free_vec.shape} != (37,)")
    full = np.empty(47, dtype=np.float64)
    full[pmap["free_idx"]] = free_vec
    full[pmap["pin_idx"]] = pmap["pin_values"]   # immutable pin injection
    return full


def _validate_optimizer_contract(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Exact optimizer contract (review fix 6 / decision I)."""
    ob = cfg["phase3"]["optimizer"]
    if set(ob.keys()) != {"method", "options"}:
        raise StopRun("S-1", "optimizer-contract",
                      f"optimizer block keys {sorted(ob.keys())} != ['method','options']")
    if ob["method"] != "L-BFGS-B":
        raise StopRun("S-1", "optimizer-contract", f"method {ob['method']!r} != 'L-BFGS-B'")
    opts = ob["options"]
    if set(opts.keys()) != {"maxiter", "maxcor", "ftol", "gtol"}:
        raise StopRun("S-1", "optimizer-contract",
                      f"option keys {sorted(opts.keys())} != registered four")
    if not (int(opts["maxiter"]) == 5000 and int(opts["maxcor"]) == 30
            and float(opts["ftol"]) == 1e-15 and float(opts["gtol"]) == 1e-10):
        raise StopRun("S-1", "optimizer-contract",
                      f"option values {opts} != registered values")
    return {"method": "L-BFGS-B",
            "options": {"maxiter": 5000, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10}}


def _runtime_map_fingerprint(rtmap: Dict[str, Path]) -> str:
    """Deterministic fingerprint of ONE runtime-path map (decision E)."""
    joined = "\n".join(f"{k}:{Path(v).resolve()}" for k, v in
                        sorted(rtmap.items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _phase3_runtime_paths() -> Dict[str, Path]:
    """Immutable label -> INDEPENDENTLY constructed runtime path (decision A).
    Never derived from YAML; built only from MNL_ROOT / canonical constants."""
    return {
        "geometry_parquet": CANONICAL_REGIONLIVE_ROOT
            / "inputs/fr_p2a_draws_geometry__singles.parquet",
        "geometry_meta": CANONICAL_REGIONLIVE_ROOT
            / "inputs/fr_p2a_draws_geometry__meta.json",
        "frozen_stem_parquet": CANONICAL_REGIONLIVE_ROOT
            / f"{CANONICAL_STEM}__singles.parquet",
        "frozen_stem_mnlmeta": CANONICAL_REGIONLIVE_ROOT
            / f"{CANONICAL_STEM}__mnlmeta.json",
        "certified_spec_yaml": MNL_ROOT
            / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml",
        "certified_warm_start_theta": MNL_ROOT
            / "scripts/bpool/specs/theta_hat_realdata_901_v1.csv",
        "stored_region_live_start_theta": MNL_ROOT / "theta_p2a_singles_2016_v1.csv",
        "phase12_rebuild_manifest": CANONICAL_REGIONLIVE_ROOT / "rebuild_manifest.json",
        "phase12_dry_run_report": CANONICAL_REGIONLIVE_ROOT / "dry_run_report.json",
        "pre_estimation_reload_verification": CANONICAL_REGIONLIVE_ROOT
            / "pre_estimation_reload_verification.json",
    }


def _authenticate_inputs(cfg: Dict[str, Any],
                         runtime_paths: Optional[Dict[str, Path]] = None
                         ) -> Dict[str, Any]:
    """Exact label<->runtime-path<->hash authentication (decision A): the YAML key set
    must equal the immutable label set; every configured path must resolve to the
    independently constructed runtime path; every file must exist and hash-match."""
    runtime = runtime_paths if runtime_paths is not None else _phase3_runtime_paths()
    ycfg = cfg["phase3"]["input_authentication"]
    if set(ycfg.keys()) != set(runtime.keys()):
        raise StopRun("S-8", "input-authentication",
                      f"YAML label set mismatch: missing "
                      f"{sorted(set(runtime) - set(ycfg))}, "
                      f"extra {sorted(set(ycfg) - set(runtime))}")
    table: Dict[str, Any] = {}
    bad: List[str] = []
    for label, rpath in runtime.items():
        entry = ycfg[label]
        rp = Path(rpath).resolve()
        cpath = (MNL_ROOT / entry["path"]).resolve()
        path_ok = (cpath == rp)
        is_file = rp.is_file()
        actual = _sha256(rp) if is_file else None
        expected = entry["sha256"]
        hash_ok = (actual is not None and actual == expected)
        table[label] = {"label": label, "runtime_path": str(rp),
                        "configured_path": str(cpath), "path_identity_ok": path_ok,
                        "is_file": is_file, "expected": expected, "actual": actual,
                        "hash_ok": hash_ok, "ok": path_ok and is_file and hash_ok}
        if not table[label]["ok"]:
            bad.append(label)
    if bad:
        raise StopRun("S-8", "input-authentication",
                      f"authentication failed for: {bad}")
    return table


def _recheck_inputs(pre_table: Dict[str, Any],
                    runtime_paths: Optional[Dict[str, Path]] = None
                    ) -> Tuple[Dict[str, Any], bool]:
    """Post-optimization recheck over the SAME immutable mapping (decision A):
    recompute every label's runtime path + hash; compare to pre-run AND accepted."""
    runtime = runtime_paths if runtime_paths is not None else _phase3_runtime_paths()
    out: Dict[str, Any] = {}
    all_ok = True
    for label, rpath in runtime.items():
        pre = pre_table.get(label) or {}
        p = Path(rpath).resolve()
        now = _sha256(p) if p.is_file() else None
        ok = (label in pre_table and str(p) == pre.get("runtime_path")
              and now is not None and now == pre.get("actual") == pre.get("expected"))
        out[label] = {"runtime_path": str(p), "pre": pre.get("actual"), "post": now,
                      "accepted": pre.get("expected"), "ok": ok}
        all_ok &= ok
    return out, all_ok


def _validate_safety_constants(cfg: Dict[str, Any]) -> Dict[str, bool]:
    """YAML equality against the immutable safety constants (decision C)."""
    C = PHASE3_SAFETY_CONSTANTS
    g3 = cfg["phase3"]["gates"]
    acc = cfg["phase3"]["accepted_evidence"]
    checks = {
        "target_negll_full": float(cfg["targets"]["negll_full"]) == C["target_negll_full"],
        "objective_tol_full": float(g3["objective_tol_full"]) == C["objective_tol_full"],
        "g16_inbounds_epsilon": float(g3["g16_inbounds_epsilon"]) == C["g16_inbounds_epsilon"],
        "gradient_max_abs_35free":
            float(g3["gradient_max_abs_35free"]) == C["gradient_max_abs_35free"],
        "bound_hit_eps": float(g3["bound_hit_eps"]) == C["bound_hit_eps"],
        "n_params": int(cfg["certified_spec"]["n_params"]) == C["n_params"],
        "n_free": int(acc["n_free"]) == C["n_free"],
        "n_pinned": int(acc["n_pinned"]) == C["n_pinned"],
        "n_hh": int(acc["n_hh"]) == C["n_hh"],
        "n_alts": int(acc["n_alts"]) == C["n_alts"],
        "at_bound_tuple":
            tuple(cfg["run_overlay"]["at_bound_expected"]) == EXPECTED_AT_BOUND_NAMES,
        "pin_tuple": tuple(cfg["run_overlay"]["pinned_params"]) == ACCEPTED_PIN_NAMES,
        "n_free_expected": int(cfg["run_overlay"]["n_free_expected"]) == C["n_free"],
        "pre_opt_objective_tol":
            float(g3["pre_opt_objective_tol"]) == PHASE3_PREOPT_OBJECTIVE_TOL,
        "target_mismatch_status":
            str(g3["target_mismatch_status"]) == PHASE3_TARGET_MISMATCH_STATUS,
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise StopRun("S-1", "safety-constants",
                      f"YAML deviates from immutable constants: {bad}")
    oc = _validate_optimizer_contract(cfg)
    if (oc["method"] != C["optimizer_method"]
            or oc["options"] != C["optimizer_options"]):
        raise StopRun("S-1", "safety-constants", "optimizer contract != constants")
    return checks


def _git_head_full(repo: Path) -> Optional[str]:
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def _git_run(repo: Path, *argv: str) -> Tuple[int, str]:
    try:
        r = subprocess.run(["git", "-C", str(repo), *argv],
                           capture_output=True, timeout=30)
        return r.returncode, r.stdout.decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return 999, str(exc)


def _git_fully_clean(repo: Path) -> bool:
    """FULL cleanliness: tracked, staged AND untracked (never -uno; scope doc
    s5). The review-v6 approval file is committed/tracked, so it does not
    conflict with this gate."""
    rc, out = _git_run(repo, "status", "--porcelain", "--untracked-files=all")
    return rc == 0 and out.strip() == ""


def _git_gitlink(repo: Path, sub: str = "dclaborsupply-monorepo"
                 ) -> Optional[str]:
    rc, out = _git_run(repo, "ls-tree", "HEAD", sub)
    return out.split()[2] if rc == 0 and out.strip() else None


def _parse_review_verdict_v6(text: str) -> None:
    """Scope doc s7: exactly one ordinary '**FINAL VERDICT: APPROVE**' line, under
    the exact first heading '# 1. Sixth-review verdict'. AFTER FIXES/REJECT refused."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != REVIEW_V6_HEADING:
        raise StopRun("S-0", "review-gate",
                      f"review must start with the exact heading {REVIEW_V6_HEADING!r}")
    hits = [(i, ln.strip()) for i, ln in enumerate(lines)
            if ln.strip().startswith("**FINAL VERDICT:")]
    if len(hits) != 1:
        raise StopRun("S-0", "review-gate",
                      f"review must contain exactly one FINAL VERDICT line "
                      f"(found {len(hits)})")
    idx, line = hits[0]
    heads = [i for i, ln in enumerate(lines) if ln.startswith("# ")]
    if len(heads) >= 2 and idx > heads[1]:
        raise StopRun("S-0", "review-gate",
                      "FINAL VERDICT line is not in the first verdict section")
    if line != APPROVE_LINE:
        raise StopRun("S-0", "review-gate",
                      f"review final verdict is not an exact APPROVE: {line!r}")


def _parse_review_verdict_phase4(text: str) -> None:
    """Phase-4 approval form (review-v1 fix 1): exactly one ordinary
    '**FINAL VERDICT: APPROVE**' line, under the exact first heading
    '# 1. Phase-4 review verdict'. AFTER FIXES/REJECT refused."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != PHASE4_REVIEW_HEADING:
        raise StopRun("S-0", "phase4-review-gate",
                      f"Phase-4 review must start with the exact heading "
                      f"{PHASE4_REVIEW_HEADING!r}")
    hits = [(i, ln.strip()) for i, ln in enumerate(lines)
            if ln.strip().startswith("**FINAL VERDICT:")]
    if len(hits) != 1:
        raise StopRun("S-0", "phase4-review-gate",
                      f"Phase-4 review must contain exactly one FINAL VERDICT "
                      f"line (found {len(hits)})")
    idx, line = hits[0]
    heads = [i for i, ln in enumerate(lines) if ln.startswith("# ")]
    if len(heads) >= 2 and idx > heads[1]:
        raise StopRun("S-0", "phase4-review-gate",
                      "FINAL VERDICT line is not in the first verdict section")
    if line != APPROVE_LINE:
        raise StopRun("S-0", "phase4-review-gate",
                      f"Phase-4 review final verdict is not an exact APPROVE: "
                      f"{line!r}")


def _verify_execution_gates(args, *, _repo_root: Optional[Path] = None,
                            _nested_root: Optional[Path] = None,
                            _check_gitlink: bool = True) -> Dict[str, Any]:
    """Reproducibility gates for a REAL Phase-3 run (scope doc s5/s7): expected
    HEADs, gitlink identity, FULL cleanliness of both worktrees, and the exact
    review-v6 path/hash/verdict. Research-grade checks, not adversarial
    authorization. The _repo_root/_nested_root/_check_gitlink parameters are
    ordinary test seams for temporary-repository unit tests."""
    import re as _re
    repo = Path(_repo_root) if _repo_root is not None else MNL_ROOT
    nested = (Path(_nested_root) if _nested_root is not None
              else MNL_ROOT / "dclaborsupply-monorepo")
    exp_mnl = getattr(args, "expected_mnl_head", None)
    exp_dcl = getattr(args, "expected_dclaborsupply_head", None)
    review_arg = getattr(args, "approved_review", None)
    review_sha = getattr(args, "approved_review_sha256", None)
    hex40 = _re.compile(r"^[0-9a-f]{40}$")
    hex64 = _re.compile(r"^[0-9a-f]{64}$")
    if not (exp_mnl and hex40.match(exp_mnl)):
        raise StopRun("S-0", "git-gate", "--expected-mnl-head must be a 40-hex SHA")
    if not (exp_dcl and hex40.match(exp_dcl)):
        raise StopRun("S-0", "git-gate",
                      "--expected-dclaborsupply-head must be a 40-hex SHA")
    if not (review_sha and hex64.match(review_sha)):
        raise StopRun("S-0", "review-gate",
                      "--approved-review-sha256 must be a 64-hex SHA-256")
    if review_arg is None or Path(review_arg).as_posix() !=             CANONICAL_APPROVED_REVIEW_REL.as_posix():
        raise StopRun("S-0", "review-gate",
                      f"--approved-review must be exactly "
                      f"{CANONICAL_APPROVED_REVIEW_REL.as_posix()!r}")
    head_mnl = _git_head_full(repo)
    if head_mnl != exp_mnl:
        raise StopRun("S-0", "git-gate",
                      f"MNL HEAD {head_mnl} != expected {exp_mnl}")
    head_dcl = _git_head_full(nested)
    if head_dcl != exp_dcl:
        raise StopRun("S-0", "git-gate",
                      f"nested HEAD {head_dcl} != expected {exp_dcl}")
    gitlink = _git_gitlink(repo) if _check_gitlink else head_dcl
    if gitlink != head_dcl:
        raise StopRun("S-0", "git-gate",
                      f"MNL gitlink {gitlink} != nested HEAD {head_dcl}")
    if not _git_fully_clean(repo):
        raise StopRun("S-0", "git-gate",
                      "MNL worktree not fully clean (--untracked-files=all)")
    if not _git_fully_clean(nested):
        raise StopRun("S-0", "git-gate",
                      "dclaborsupply-monorepo worktree not fully clean")
    review = repo / CANONICAL_APPROVED_REVIEW_REL
    if not review.is_file():
        raise StopRun("S-0", "review-gate", f"approved review missing: {review}")
    actual_sha = _sha256(review)
    if actual_sha != review_sha:
        raise StopRun("S-0", "review-gate",
                      "approved review SHA-256 != --approved-review-sha256")
    _parse_review_verdict_v6(review.read_text(encoding="utf-8"))
    return {"verified": True, "execution_ready": True,
            "expected_mnl_head": exp_mnl, "expected_dclaborsupply_head": exp_dcl,
            "gitlink": gitlink, "approved_review":
                CANONICAL_APPROVED_REVIEW_REL.as_posix(),
            "approved_review_sha256": actual_sha}


def _verify_phase4_execution_gates(args, *, _repo_root: Optional[Path] = None,
                                   _nested_root: Optional[Path] = None,
                                   _check_gitlink: bool = True) -> Dict[str, Any]:
    """Reproducibility gates for a REAL Phase-4 run (review-v1 required fix 1):
    expected HEADs, gitlink identity, FULL cleanliness of both worktrees, and
    the exact PHASE-4 review path/hash/verdict
    (FR_P2a_region_live_phase4_code_review_v7.md). Phase-4 reviews v1-v6
    and the Phase-3 review-v6 are all explicitly rejected here. All checks run
    BEFORE any gradient or Hessian evaluation. The _repo_root/_nested_root/
    _check_gitlink parameters are ordinary test seams."""
    import re as _re
    repo = Path(_repo_root) if _repo_root is not None else MNL_ROOT
    nested = (Path(_nested_root) if _nested_root is not None
              else MNL_ROOT / "dclaborsupply-monorepo")
    exp_mnl = getattr(args, "expected_mnl_head", None)
    exp_dcl = getattr(args, "expected_dclaborsupply_head", None)
    review_arg = getattr(args, "approved_phase4_review", None)
    review_sha = getattr(args, "approved_phase4_review_sha256", None)
    hex40 = _re.compile(r"^[0-9a-f]{40}$")
    hex64 = _re.compile(r"^[0-9a-f]{64}$")
    if not (exp_mnl and hex40.match(exp_mnl)):
        raise StopRun("S-0", "git-gate", "--expected-mnl-head must be a 40-hex SHA")
    if not (exp_dcl and hex40.match(exp_dcl)):
        raise StopRun("S-0", "git-gate",
                      "--expected-dclaborsupply-head must be a 40-hex SHA")
    if not (review_sha and hex64.match(review_sha)):
        raise StopRun("S-0", "phase4-review-gate",
                      "--approved-phase4-review-sha256 must be a 64-hex SHA-256")
    if (review_arg is not None and Path(review_arg).as_posix()
            == CANONICAL_APPROVED_REVIEW_REL.as_posix()):
        raise StopRun("S-0", "phase4-review-gate",
                      "the Phase-3 review-v6 document cannot authorize Phase-4 "
                      "execution; a Phase-4-specific approved review is required")
    if (review_arg is None or Path(review_arg).as_posix()
            != CANONICAL_APPROVED_PHASE4_REVIEW_REL.as_posix()):
        raise StopRun("S-0", "phase4-review-gate",
                      f"--approved-phase4-review must be exactly "
                      f"{CANONICAL_APPROVED_PHASE4_REVIEW_REL.as_posix()!r}")
    head_mnl = _git_head_full(repo)
    if head_mnl != exp_mnl:
        raise StopRun("S-0", "git-gate",
                      f"MNL HEAD {head_mnl} != expected {exp_mnl}")
    head_dcl = _git_head_full(nested)
    if head_dcl != exp_dcl:
        raise StopRun("S-0", "git-gate",
                      f"nested HEAD {head_dcl} != expected {exp_dcl}")
    gitlink = _git_gitlink(repo) if _check_gitlink else head_dcl
    if gitlink != head_dcl:
        raise StopRun("S-0", "git-gate",
                      f"MNL gitlink {gitlink} != nested HEAD {head_dcl}")
    if not _git_fully_clean(repo):
        raise StopRun("S-0", "git-gate",
                      "MNL worktree not fully clean (--untracked-files=all)")
    if not _git_fully_clean(nested):
        raise StopRun("S-0", "git-gate",
                      "dclaborsupply-monorepo worktree not fully clean")
    review = repo / CANONICAL_APPROVED_PHASE4_REVIEW_REL
    if not review.is_file():
        raise StopRun("S-0", "phase4-review-gate",
                      f"approved Phase-4 review missing: {review}")
    actual_sha = _sha256(review)
    if actual_sha != review_sha:
        raise StopRun("S-0", "phase4-review-gate",
                      "approved Phase-4 review SHA-256 != "
                      "--approved-phase4-review-sha256")
    _parse_review_verdict_phase4(review.read_text(encoding="utf-8"))
    return {"verified": True, "execution_ready": True, "phase": 4,
            "expected_mnl_head": exp_mnl, "expected_dclaborsupply_head": exp_dcl,
            "gitlink": gitlink,
            "approved_phase4_review":
                CANONICAL_APPROVED_PHASE4_REVIEW_REL.as_posix(),
            "approved_phase4_review_sha256": actual_sha}


def _verify_package_identity(expected_commit: Optional[str] = None,
                             *, _modules=None,
                             _package_root: Optional[Path] = None,
                             _nested_root: Optional[Path] = None) -> Dict[str, Any]:
    """dclaborsupply source-identity verification (decision D): the COMPLETE loaded
    module inventory of the Phase-3 route must resolve under the reviewed source
    root AND match its tracked blob (Git-canonical) at the expected nested commit
    (nested HEAD for dry-runs). Private seams are for unit tests only."""
    root = (Path(_package_root) if _package_root is not None
            else PACKAGE_SOURCE_ROOT).resolve()
    nested = (Path(_nested_root) if _nested_root is not None
              else MNL_ROOT / "dclaborsupply-monorepo").resolve()
    head = _git_head_full(nested)
    dirty = not _git_fully_clean(nested)
    gitlink = None
    if _nested_root is None:
        try:
            r = subprocess.run(["git", "-C", str(MNL_ROOT), "ls-tree", "HEAD",
                                "dclaborsupply-monorepo"],
                               capture_output=True, text=True, timeout=15)
            if r.returncode == 0 and r.stdout.strip():
                gitlink = r.stdout.split()[2]
        except Exception:  # noqa: BLE001
            pass
    commit_ref = expected_commit or head

    if _modules is None:
        import importlib
        mods = [importlib.import_module(n) for n in REQUIRED_PACKAGE_MODULES]
        seen = {m.__name__ for m in mods}
        for name, m in sorted(sys.modules.items()):
            if ((name == "dclaborsupply" or name.startswith("dclaborsupply."))
                    and name not in seen and m is not None
                    and getattr(m, "__file__", None)):
                mods.append(m)
                seen.add(name)
    else:
        mods = list(_modules)

    records: Dict[str, Any] = {}
    failures: List[str] = []
    for m in mods:
        name = getattr(m, "__name__", repr(m))
        rec: Dict[str, Any] = {}
        f = getattr(m, "__file__", None)
        if not f:
            rec.update(path=None, ancestry_ok=False, reason="missing __file__")
            failures.append(name)
            records[name] = rec
            continue
        p = Path(f).resolve()
        try:
            ancestry_ok = p.is_relative_to(root)
        except Exception:  # noqa: BLE001
            ancestry_ok = False
        rec.update(path=str(p), ancestry_ok=ancestry_ok)
        if not ancestry_ok:
            rec["reason"] = "outside reviewed source root"
            failures.append(name)
            records[name] = rec
            continue
        try:
            rel = p.relative_to(nested).as_posix()
        except ValueError:
            rec["reason"] = "not under nested repository"
            failures.append(name)
            records[name] = rec
            continue
        rec["relative_path"] = rel
        rc, blob_id = _git_run(nested, "rev-parse", f"{commit_ref}:{rel}")
        if rc != 0 or not blob_id.strip():
            rec["reason"] = "not a tracked blob at the approved commit"
            failures.append(name)
            records[name] = rec
            continue
        rec["blob_id"] = blob_id.strip()
        try:
            r = subprocess.run(["git", "-C", str(nested), "cat-file", "blob",
                                blob_id.strip()], capture_output=True, timeout=30)
            blob_bytes = r.stdout if r.returncode == 0 else None
        except Exception:  # noqa: BLE001
            blob_bytes = None
        if blob_bytes is None:
            rec["reason"] = "cannot read committed blob"
            failures.append(name)
            records[name] = rec
            continue
        # equality in Git's OWN canonical form: hash-object with the module's
        # attribute/eol filters applied (--path) must reproduce the tracked blob
        # id. Raw byte comparison would false-fail on autocrlf checkouts while
        # this still rejects every real modification or substitution.
        rc2, working_id = _git_run(nested, "hash-object", "--path", rel,
                                   "--", str(p))
        rec["committed_sha256"] = hashlib.sha256(blob_bytes).hexdigest()
        rec["working_sha256"] = _sha256(p)
        rec["working_blob_id"] = working_id.strip() if rc2 == 0 else None
        rec["blob_equal"] = (rc2 == 0
                             and working_id.strip() == blob_id.strip())
        if not rec["blob_equal"]:
            rec["reason"] = "working file differs from committed blob"
            failures.append(name)
        records[name] = rec

    rec_out = {"nested_repo": str(nested), "nested_head": head,
               "commit_ref": commit_ref, "gitlink": gitlink,
               "fully_dirty": dirty, "package_source_root": str(root),
               "imported_modules": records,
               "module_path_ok": not failures,
               "module_failures": failures,
               "expected_commit": expected_commit}
    ok = (not failures and dirty is False and head is not None)
    if _nested_root is None:
        ok = ok and gitlink is not None and gitlink == head
        if _modules is None:
            required_missing = [n for n in REQUIRED_PACKAGE_MODULES
                                if n not in records]
            ok = ok and not required_missing
    if expected_commit is not None:
        ok = ok and (head == expected_commit)
    rec_out["package_identity_ok"] = bool(ok)
    if not ok:
        raise StopRun("S-0", "package-identity",
                      f"dclaborsupply source identity failed "
                      f"(failures={failures}): see record")
    return rec_out


def _bundle_hashes(staging: Path) -> Tuple[Dict[str, str], str]:
    """SHA-256 per artifact (manifest NEVER included) + deterministic bundle hash."""
    hashes = {n: _sha256(staging / n) for n in PHASE3_ARTIFACTS
              if (staging / n).is_file()}
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    return hashes, hashlib.sha256(joined.encode("utf-8")).hexdigest()


class Phase3Transaction:
    """Lock + staging/attempts/complete result-directory transaction (decision B)."""

    _ATTEMPT_ALLOC_MAX_TRIES = 100   # defensive bound; uuid4 repeats are ~impossible

    def __init__(self, root: Path, label: str,
                 success_status: str = "PHASE_3_COMPLETE"):
        self.root = Path(root)
        self.label = str(label)
        self.success_status = str(success_status)   # publishes to complete/
        self.lock = self.root / ".phase3.lock"
        self.staging_base = self.root / ".staging"
        self.attempts = self.root / "attempts"
        self.complete = self.root / "complete"
        # review-v6 fix 1: the attempt id is NOT chosen here -- it is allocated
        # collision-resistantly (full uuid4 hex) in acquire(), under the lock
        self.attempt_id: Optional[str] = None
        self.staging: Optional[Path] = None
        self._locked = False

    def _attempt_destination_exists(self, attempt_id: str) -> bool:
        """True if any prior destination clashes with this attempt id: its staging
        directory, or an attempts/ entry under ANY status suffix. complete/ has a
        fixed name (never attempt-id derived) so it cannot clash with an id."""
        if (self.staging_base / attempt_id).exists():
            return True
        if self.attempts.is_dir():
            for p in self.attempts.iterdir():
                if p.name == attempt_id or p.name.startswith(attempt_id + "_"):
                    return True
        return False

    def _allocate_unique_attempt(self, label: str) -> str:
        """Collision-resistant attempt allocation (review-v6 required fix 1).
        Called ONLY while the exclusive lock is held, so no two normal Phase-3
        processes can reserve the same destination; the staging mkdir with
        exist_ok=False is the atomic reservation itself."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for _ in range(self._ATTEMPT_ALLOC_MAX_TRIES):
            attempt_id = f"{stamp}_{os.getpid()}_{uuid.uuid4().hex}_{label}"
            if self._attempt_destination_exists(attempt_id):
                continue
            try:
                (self.staging_base / attempt_id).mkdir(parents=True,
                                                       exist_ok=False)
            except FileExistsError:
                continue
            return attempt_id
        raise StopRun("S-0", "attempt-allocation",
                      f"no unique attempt id after "
                      f"{self._ATTEMPT_ALLOC_MAX_TRIES} tries (label={label})")

    def migrate_pre_review_evidence(self) -> None:
        """One-time byte-preserving relocation of the pre-review loose dry-run files."""
        legacy = [self.root / "phase3_manifest.json", self.root / "phase3_console.log"]
        if any(p.is_file() for p in legacy):
            dst = self.attempts / "pre_review_dryrun_0_REJECTED_REVIEW"
            dst.mkdir(parents=True, exist_ok=True)
            for p in legacy:
                if p.is_file():
                    os.replace(p, dst / p.name)

    def acquire(self) -> None:
        # decision H order: lock FIRST; any one-time legacy migration only under lock
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StopRun("S-0", "phase3-lock",
                          f"lock exists ({self.lock}); refusing to run -- a prior run "
                          "may be active or crashed; manual inspection required "
                          "(the lock is never deleted automatically)")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "utc": _utcnow(),
                       "attempt": None}, f)     # attempt allocated below
        self._locked = True
        self.attempts.mkdir(exist_ok=True)
        self.migrate_pre_review_evidence()      # under the lock (decision H)
        self.staging_base.mkdir(exist_ok=True)
        # review-v6 fix 2: allocate the unique attempt AFTER the lock is held;
        # on the (defensive) exhaustion stop, no evidence has been staged, so
        # the lock is released through the normal controlled path
        try:
            self.attempt_id = self._allocate_unique_attempt(self.label)
        except StopRun:
            self.release()
            raise
        self.staging = self.staging_base / self.attempt_id
        self.lock.write_text(json.dumps({"pid": os.getpid(), "utc": _utcnow(),
                                         "attempt": self.attempt_id}),
                             encoding="utf-8")

    def complete_exists(self) -> bool:
        return self.complete.exists()

    def finish(self, status: str) -> Path:
        """Atomic directory-level publication: complete/ on success, attempts/ otherwise.
        A failed/repeated run can never overwrite or mutate a prior successful bundle."""
        if status == self.success_status:
            if self.complete.exists():
                raise RuntimeError("complete/ already exists -- publish refused")
            os.replace(self.staging, self.complete)
            return self.complete
        dest = self.attempts / f"{self.attempt_id}_{status}"
        os.replace(self.staging, dest)
        return dest

    def release(self) -> None:
        if self._locked and self.lock.is_file():
            self.lock.unlink()
            self._locked = False


def _phase3_post_gates(negll_hat: float, theta_hat_full: np.ndarray,
                       grad_full: np.ndarray, pmap: Dict[str, Any],
                       bounds_full: List[Tuple[Optional[float], Optional[float]]],
                       g3: Dict[str, Any], target: float,
                       opt_success: bool, opt_message: str
                       ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str,
                                  Optional[Dict[str, str]]]:
    """Pure post-optimization gate battery: G-16, G-15, G-3, pins, G-1 (decision F/J)."""
    eps15 = float(g3["bound_hit_eps"])
    eps16 = float(g3["g16_inbounds_epsilon"])
    names = pmap["all_names"]
    name_idx = pmap["name_idx"]
    free_set = set(pmap["free_names"])
    pin_set = set(pmap["pin_names"])

    rows: List[Dict[str, Any]] = []
    hits: List[str] = []
    g16_violations: List[str] = []
    for n in names:
        i = name_idx[n]
        lo, hi = bounds_full[i]
        v = float(theta_hat_full[i])
        pinned = n in pin_set
        at_bound = (n in free_set) and (
            (lo is not None and abs(v - lo) < eps15)
            or (hi is not None and abs(v - hi) < eps15))
        in_bounds = True
        if n in free_set:
            if lo is not None and v < lo - eps16:
                in_bounds = False
            if hi is not None and v > hi + eps16:
                in_bounds = False
            if not in_bounds:
                g16_violations.append(n)
        if at_bound:
            hits.append(n)
        rows.append({"param": n, "value": v, "pinned": pinned, "at_bound": at_bound,
                     "lb": lo, "ub": hi,
                     "dist_lb": (v - lo) if lo is not None else None,
                     "dist_ub": (hi - v) if hi is not None else None,
                     "in_bounds": in_bounds, "grad": float(grad_full[i])})

    expected = sorted(EXPECTED_AT_BOUND_NAMES)
    nonbound_free = [n for n in pmap["free_names"] if n not in set(expected)]
    pins_bitwise = all(
        np.float64(theta_hat_full[pmap["pin_idx"][k]]).tobytes()
        == np.float64(pmap["pin_values"][k]).tobytes()
        for k in range(len(pmap["pin_names"])))
    max_grad_35 = float(np.max(np.abs(
        np.array([grad_full[name_idx[n]] for n in nonbound_free]))))
    abs_dev = abs(float(negll_hat) - float(target))

    gates = {
        "g2_optimizer_success": bool(opt_success),
        "g_structure_37_free_10_pins": (len(pmap["free_names"]) == 37
                                        and len(pmap["pin_names"]) == 10),
        "g_pins_bitwise_unchanged": bool(pins_bitwise),
        "g16_inbounds_epsilon": eps16,
        "g16_violations": g16_violations,
        "g16_inbounds_ok": not g16_violations,
        "g15_bound_hits_detected": sorted(hits),
        "g15_bound_hits_expected": expected,
        "g15_bound_hits_ok": sorted(hits) == expected,
        "g_nonbound_free_count": len(nonbound_free),
        "g_nonbound_free_count_ok": len(nonbound_free) == 35,
        "g3_max_abs_grad_35free": max_grad_35,
        "g3_ok": max_grad_35 < float(g3["gradient_max_abs_35free"]),
        "g1_abs_dev_full": abs_dev,
        "g1_ok": abs_dev <= float(g3["objective_tol_full"]),
    }
    if not gates["g2_optimizer_success"]:
        return gates, rows, "STOPPED", {"code": "S-2", "gate": "G-2",
                                        "message": f"optimizer failure: {opt_message}"}
    if not (gates["g_structure_37_free_10_pins"] and gates["g_pins_bitwise_unchanged"]):
        return gates, rows, "STOPPED", {"code": "S-3", "gate": "pins",
                                        "message": "pin/free structure violated"}
    if not gates["g16_inbounds_ok"]:
        return gates, rows, "STOPPED", {"code": "S-3", "gate": "G-16",
                                        "message": f"free parameter(s) out of bounds: "
                                                   f"{g16_violations}"}
    if not (gates["g15_bound_hits_ok"] and gates["g_nonbound_free_count_ok"]):
        return gates, rows, "STOPPED", {"code": "S-3", "gate": "G-15",
                                        "message": f"bound-hit set {sorted(hits)} != "
                                                   f"expected {expected}"}
    if not gates["g3_ok"]:
        return gates, rows, "STOPPED", {"code": "S-3", "gate": "G-3",
                                        "message": f"max|grad| {max_grad_35:.3e} over gate"}
    if not gates["g1_ok"]:
        return gates, rows, PHASE3_TARGET_MISMATCH_STATUS, None
    return gates, rows, "PHASE_3_COMPLETE", None


def _phase3_contract(out: OutRoot, cfg: Dict[str, Any], config_path: Path,
                     log, rtmap: Optional[Dict[str, Path]] = None
                     ) -> Dict[str, Any]:
    """Pre-optimization input contract (decisions D-I). Raises StopRun on failure."""
    from dclaborsupply import EstimationSpec
    from dclaborsupply.spec.parser import load_custom_initial_values
    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll
    import jax
    import jax.numpy as jnp

    p3 = cfg["phase3"]
    acc = p3["accepted_evidence"]
    g3 = p3["gates"]
    ev: Dict[str, Any] = {"checked_at": _utcnow()}

    # safety-critical constants + optimizer + pin-identity + canonical-stem
    ev["safety_constants_ok"] = _validate_safety_constants(cfg)
    ev["optimizer_contract"] = _validate_optimizer_contract(cfg)
    # decision A: ONE immutable runtime map is the sole source of every Phase-3
    # file open; every retained legacy config alias must resolve EXACTLY onto it
    rt = rtmap if rtmap is not None else _phase3_runtime_paths()
    _aliases = {
        "certified_spec.yaml": (cfg["certified_spec"]["yaml"], "certified_spec_yaml"),
        "warm_start.theta_csv": (cfg["warm_start"]["theta_csv"],
                                 "certified_warm_start_theta"),
        "phase3.start_theta.csv": (cfg["phase3"]["start_theta"]["csv"],
                                   "stored_region_live_start_theta"),
        "stored_region_live_theta.v1_csv": (cfg["stored_region_live_theta"]["v1_csv"],
                                            "stored_region_live_start_theta"),
    }
    alias_ev = {}
    for aname, (aval, label) in _aliases.items():
        resolved = (MNL_ROOT / aval).resolve()
        ok = resolved == Path(rt[label]).resolve()
        alias_ev[aname] = {"alias_value": str(aval), "resolves_to": str(resolved),
                           "runtime_map_path": str(rt[label]), "ok": ok}
        if not ok:
            raise StopRun("S-8", "alias-identity",
                          f"config alias {aname!r} does not resolve to the immutable "
                          f"runtime-map path for {label!r}")
    ev["alias_identity"] = alias_ev
    cfg_pins = list(cfg["run_overlay"]["pinned_params"])
    if tuple(cfg_pins) != ACCEPTED_PIN_NAMES:
        raise StopRun("S-1", "pin-identity",
                      f"config pin list != accepted ordered pin tuple: {cfg_pins}")
    if cfg["run"]["frozen_stem_name"] != CANONICAL_STEM:
        raise StopRun("S-1", "canonical-stem",
                      f"frozen_stem_name {cfg['run']['frozen_stem_name']!r} != "
                      f"{CANONICAL_STEM!r}")
    ia = cfg["phase3"]["input_authentication"]
    if not str(ia["frozen_stem_parquet"]["path"]).endswith(
            f"{CANONICAL_STEM}__singles.parquet"):
        raise StopRun("S-1", "canonical-stem", "stem parquet path is not canonical")
    if not str(ia["frozen_stem_mnlmeta"]["path"]).endswith(
            f"{CANONICAL_STEM}__mnlmeta.json"):
        raise StopRun("S-1", "canonical-stem", "mnlmeta path is not the stem companion")

    # exact label->runtime-path->hash authentication (decision A)
    ev["input_authentication"] = _authenticate_inputs(cfg, runtime_paths=rt)

    # Phase 1-2 manifest: status + accepted script/config anchors
    man12 = json.loads(Path(rt["phase12_rebuild_manifest"]).read_text(encoding="utf-8"))
    ev["phase12_manifest_status"] = man12.get("status")
    if man12.get("status") != acc["manifest_status_required"]:
        raise StopRun("S-1", "phase3-contract",
                      f"Phase 1-2 manifest status {man12.get('status')!r} != "
                      f"{acc['manifest_status_required']!r}")
    anchors = cfg["phase3"]["accepted_phase12_anchors"]
    ev["phase12_anchor_check"] = {
        "manifest_script": (man12.get("script") or {}).get("sha256"),
        "anchor_script": anchors["script_sha256"],
        "manifest_config": (man12.get("config") or {}).get("sha256"),
        "anchor_config": anchors["config_sha256"],
    }
    if ((man12.get("script") or {}).get("sha256") != anchors["script_sha256"]
            or (man12.get("config") or {}).get("sha256") != anchors["config_sha256"]):
        raise StopRun("S-8", "phase3-contract",
                      "Phase 1-2 manifest script/config hashes != accepted anchors")

    # spec + ordering vs the authenticated accepted dry run
    spec = EstimationSpec.from_yaml(str(rt["certified_spec_yaml"]))
    names = list(spec.all_param_names)
    accepted_dr = json.loads(Path(rt["phase12_dry_run_report"]).read_text(encoding="utf-8"))
    if names != list(accepted_dr.get("param_names", [])):
        raise StopRun("S-1", "phase3-contract",
                      "parameter ordering differs from the accepted dry run")
    ev["n_params"] = len(names)

    # structural route (vw; loc_empirical / vw_occupation inactive; proposal centering)
    ev["wage_spec"] = str(spec.wage_spec)
    ev["wage_loc_groups_absent"] = getattr(spec, "wage_loc_groups", None) in (None, [], {})
    ev["centering"] = {
        "within_choice_set": bool(spec.market_opportunity_center_within_choice_set),
        "center_weights": str(spec.market_opportunity_center_weights)}
    if not (ev["wage_spec"] == "vw" and ev["wage_loc_groups_absent"]
            and ev["centering"]["within_choice_set"]
            and ev["centering"]["center_weights"] == "proposal"):
        raise StopRun("S-1", "phase3-contract", "structural route check failed")

    # stem metadata content (hash-authenticated above; explicit field asserts, decision H)
    stem = CANONICAL_STEM
    meta = json.loads(Path(rt["frozen_stem_mnlmeta"]).read_text(encoding="utf-8"))
    norm = meta["normalization"]["singles"]
    if not (int(norm["n_chosen"]) == int(acc["n_hh"])
            and int(meta["row_counts"]["singles"]) == int(acc["n_hh"]) * int(acc["n_alts"])):
        raise StopRun("S-1", "phase3-contract", "mnlmeta metadata != accepted structure")
    ev["mnlmeta"] = {"c_scale": float(norm["c_scale"]), "l_scale": float(norm["l_scale"]),
                     "n_chosen": int(norm["n_chosen"])}

    # explicit 37<->47 parameter map (decision D)
    raw_theta = load_custom_initial_values(Path(rt["certified_warm_start_theta"]))
    theta_warm = np.array([float(raw_theta[n]) for n in names], dtype="float64")
    name_idx = {n: i for i, n in enumerate(names)}
    pinned_at = {p: float(theta_warm[name_idx[p]]) for p in cfg_pins}
    pmap = build_phase3_parameter_map(names, cfg_pins, pinned_at)
    bounds_full = list(spec.get_bounds_tuple())
    bounds_free = [bounds_full[i] for i in pmap["free_idx"]]

    # start vector (accepted stored region-live theta) + exact round trips (D.8)
    st_tab = pd.read_csv(Path(rt["stored_region_live_start_theta"])).set_index("param")
    if list(st_tab.index) != names:
        raise StopRun("S-1", "phase3-contract", "start-theta CSV ordering mismatch")
    theta_trial = st_tab[p3["start_theta"]["column"]].astype(float).reindex(names).to_numpy()
    ev["start_theta_raw_sha256"] = _theta_sha(theta_trial)
    if ev["start_theta_raw_sha256"] != acc["theta_star_sha256"]:
        raise StopRun("S-8", "phase3-contract", "stored theta vector hash != accepted")
    free_start = project_full_to_free(pmap, theta_trial)
    theta_start_full = expand_free_to_full(pmap, free_start)
    rtrip = {
        "project_expand_free_exact": bool(np.array_equal(
            project_full_to_free(pmap, expand_free_to_full(pmap, free_start)),
            free_start)),
        "expand_project_full_free_coords_exact": bool(np.array_equal(
            expand_free_to_full(pmap, project_full_to_free(pmap, theta_trial))[
                pmap["free_idx"]],
            theta_trial[pmap["free_idx"]])),
        "pins_bitwise_accepted": bool(all(
            np.float64(theta_start_full[pmap["pin_idx"][k]]).tobytes()
            == np.float64(pmap["pin_values"][k]).tobytes()
            for k in range(10))),
    }
    if not all(rtrip.values()):
        raise StopRun("S-1", "param-map", f"round-trip validation failed: {rtrip}")
    ev["parameter_map"] = {
        "all_names": pmap["all_names"], "free_names": pmap["free_names"],
        "pin_names": pmap["pin_names"],
        "free_indices": [int(i) for i in pmap["free_idx"]],
        "pin_indices": [int(i) for i in pmap["pin_idx"]],
        "pin_values": {p: float(v) for p, v in zip(pmap["pin_names"],
                                                   pmap["pin_values"])},
        "round_trips": rtrip,
    }
    ev["start_theta_applied_sha256"] = _theta_sha(theta_start_full)
    ev["start_pin_adjust_max_abs"] = float(np.max(np.abs(theta_start_full - theta_trial)))

    # expected at-bound set derived from the accepted input (decision F)
    eps = float(g3["bound_hit_eps"])
    derived = []
    for n in pmap["free_names"]:
        lo, hi = bounds_full[name_idx[n]]
        v = float(theta_trial[name_idx[n]])
        if (lo is not None and abs(v - lo) < eps) or (hi is not None and abs(v - hi) < eps):
            derived.append(n)
    ev["at_bound_expected_derived"] = derived
    ev["at_bound_expected_config"] = list(cfg["run_overlay"]["at_bound_expected"])
    if not (sorted(derived) == sorted(ev["at_bound_expected_config"])
            == sorted(EXPECTED_AT_BOUND_NAMES)):
        raise StopRun("S-1", "phase3-contract",
                      f"at-bound expectation mismatch: derived {derived}")
    if len([n for n in pmap["free_names"] if n not in set(derived)]) != 35:
        raise StopRun("S-1", "phase3-contract", "non-bound free count != 35")

    # frozen-stem load: household/alternative structure + prior-correction liveness
    er = pd.read_parquet(Path(rt["frozen_stem_parquet"]))
    sm_df = er[pd.to_numeric(er["dgn"]) == 1].reset_index(drop=True)
    sf_df = er[pd.to_numeric(er["dgn"]) == 0].reset_index(drop=True)
    dm = load_singles(sm_df, spec, is_male=True, metadata=meta)
    df_ = load_singles(sf_df, spec, is_male=False, metadata=meta)
    n_groups = int(dm.n_groups + df_.n_groups)
    n_alts = int(acc["n_alts"])
    if n_groups != int(acc["n_hh"]) or not (
            int(dm.n_obs) == int(dm.n_groups) * n_alts
            and int(df_.n_obs) == int(df_.n_groups) * n_alts):
        raise StopRun("S-1", "phase3-contract",
                      f"household/alternative structure mismatch ({n_groups} HH)")
    ev["n_hh"] = n_groups
    lp_dev = 0.0
    for d, frame in ((dm, sm_df), (df_, sf_df)):
        if not bool(np.all(np.asarray(d.prior) > 0)):
            raise StopRun("S-1", "phase3-contract", "loader prior not strictly positive")
        lp_dev = max(lp_dev, float(np.max(np.abs(
            np.log(np.asarray(d.prior))
            - pd.to_numeric(frame["log_prior"], errors="coerce")
            .to_numpy(dtype="float64")))))
    ev["log_prior_max_abs_dev"] = lp_dev
    if lp_dev > float(cfg["gates"]["log_prior_consistency_atol"]):
        raise StopRun("S-1", "phase3-contract", "prior-correction identity failed")

    # JAX pre-optimization objective at the applied start (evaluation only)
    nm, _ = build_jax_singles_ll(dm, spec, is_male=True)
    nf, _ = build_jax_singles_ll(df_, spec, is_male=False)
    tot = jax.jit(lambda t: nm(t) + nf(t))
    negll_start = float(tot(jnp.asarray(theta_start_full)))
    target = float(cfg["targets"]["negll_full"])
    ev["negll_start"] = negll_start
    ev["negll_start_abs_dev"] = abs(negll_start - target)
    if ev["negll_start_abs_dev"] > PHASE3_PREOPT_OBJECTIVE_TOL:
        raise StopRun("S-9", "phase3-contract",
                      f"pre-optimization objective deviates "
                      f"{ev['negll_start_abs_dev']:.3e}")
    log(f"phase3 contract: pins/map/round-trips ok | derived at-bound {derived} | "
        f"negLL(start)={negll_start:.10f} (dev {ev['negll_start_abs_dev']:.2e})")
    ev["ok"] = True
    return {"spec": spec, "names": names, "pmap": pmap, "bounds_full": bounds_full,
            "bounds_free": bounds_free, "theta_trial": theta_trial,
            "free_start": free_start, "theta_start_full": theta_start_full,
            "tot": tot, "target": target, "ev": ev,
            "input_auth": ev["input_authentication"],
            "rtmap": rt,
            "rtmap_fingerprint": _runtime_map_fingerprint(rt),
            # the EXACT production loader data objects behind `tot` (consumed by
            # the Phase-4 R-1 design; audit fix -- returning them changes no
            # Phase-3 behavior)
            "loader_data": (dm, df_)}


def _phase3_estimate(ctx: Dict[str, Any], staging: Path, cfg: Dict[str, Any], log,
                     mark_optimizer_called=None) -> Tuple[str, Dict[str, Any]]:
    """Real Phase-3 estimation over the ordered 37-free vector (decision D), with
    post-optimization input recheck (G), gate battery (F), and atomic staged artifact
    emission (C). Unit tests monkeypatch scipy.optimize.minimize; the production
    path imports scipy here and nowhere else."""
    import jax
    import jax.numpy as jnp
    import scipy.optimize as _sopt          # resolved at call time so ordinary
    minimize_fn = _sopt.minimize            # test monkeypatching of the symbol works

    p3 = cfg["phase3"]
    g3 = p3["gates"]
    oc = ctx["ev"]["optimizer_contract"]
    pmap = ctx["pmap"]
    tot, target = ctx["tot"], ctx["target"]

    vg_full = jax.jit(jax.value_and_grad(tot))

    def f_free(x_free):
        full = expand_free_to_full(pmap, x_free)
        v, g = vg_full(jnp.asarray(full))
        return float(v), np.asarray(g, dtype="float64")[pmap["free_idx"]]

    log(f"phase3 optimize: 37-free L-BFGS-B, options={oc['options']}")
    if mark_optimizer_called is not None:
        mark_optimizer_called()      # decision G: set BEFORE invocation
    t0 = time.time()
    try:
        res = minimize_fn(f_free, np.asarray(ctx["free_start"]), jac=True,
                          method=oc["method"], bounds=list(ctx["bounds_free"]),
                          options=dict(oc["options"]))
    except Exception as exc:
        recheck_x, recheck_x_ok = _recheck_inputs(
            ctx["input_auth"], runtime_paths=ctx["rtmap"])
        return "STOPPED", {
            "generated_at": _utcnow(), "verdict": "STOPPED",
            "stop": {"code": "S-2", "gate": "optimizer-exception",
                     "message": f"{type(exc).__name__}: {exc}"},
            "exception": {"type": type(exc).__name__, "message": str(exc)},
            "input_recheck_after_optimization": recheck_x, "gates": {},
        }
    elapsed = time.time() - t0
    theta_hat_full = expand_free_to_full(pmap, np.asarray(res.x, dtype="float64"))
    v_fin, g_fin = vg_full(jnp.asarray(theta_hat_full))
    negll_hat = float(v_fin)
    grad_full = np.asarray(g_fin, dtype="float64")
    log(f"phase3 fit: negLL {negll_hat:.10f}  iters={int(res.nit)} "
        f"nfev={int(res.nfev)} success={bool(res.success)}  ({elapsed:.1f}s)")

    # post-optimization input recheck BEFORE any result write, over the SAME
    # single runtime-map object threaded from the contract (decisions E + G)
    fp_post = _runtime_map_fingerprint(ctx["rtmap"])
    if fp_post != ctx["rtmap_fingerprint"]:
        raise StopRun("S-8", "runtime-map",
                      "runtime-map fingerprint changed during the attempt")
    recheck, recheck_ok = _recheck_inputs(ctx["input_auth"],
                                          runtime_paths=ctx["rtmap"])
    if not recheck_ok:
        return "STOPPED", {
            "generated_at": _utcnow(), "verdict": "STOPPED",
            "stop": {"code": "S-8", "gate": "input-recheck",
                     "message": "consumed input changed during optimization"},
            "input_recheck_after_optimization": recheck, "gates": {},
        }

    gates, rows, status, stop = _phase3_post_gates(
        negll_hat, theta_hat_full, grad_full, pmap, ctx["bounds_full"],
        g3, target, bool(res.success), str(res.message))

    diag = {
        "generated_at": _utcnow(),
        "optimizer": {"method": oc["method"], "options": oc["options"],
                      "route": cfg["phase3"]["optimizer_route_note"]["route"],
                      "settings_sources":
                          list(cfg["phase3"]["optimizer_route_note"]["settings_sources"]),
                      "free_vector_length": 37},
        "start_theta_raw_sha256": ctx["ev"]["start_theta_raw_sha256"],
        "start_theta_applied_sha256": ctx["ev"]["start_theta_applied_sha256"],
        "start_theta": [float(x) for x in ctx["theta_start_full"]],
        "final_theta_sha256": _theta_sha(theta_hat_full),
        "final_theta": [float(x) for x in theta_hat_full],
        "negll_start": float(ctx["ev"]["negll_start"]),
        "negll_final": negll_hat,
        "target_full": float(target),
        "success": bool(res.success), "status_code": int(res.status),
        "message": str(res.message),
        "n_iter": int(res.nit), "n_fev": int(res.nfev),
        "n_jev": int(getattr(res, "njev", res.nfev)),
        "elapsed_seconds": round(elapsed, 2),
        "gradient_final": [float(g) for g in grad_full],
        "gradient_free_projection": [float(grad_full[i]) for i in pmap["free_idx"]],
        "parameter_map": ctx["ev"]["parameter_map"],
        "bounds_and_distances": rows,
        "input_recheck_after_optimization": recheck,
        "rtmap_fingerprint": ctx["rtmap_fingerprint"],
        "rtmap_fingerprint_post": fp_post,
        "gates": gates,
        "stop": stop,
        "verdict": status,
    }
    _atomic_write_json(diag, staging / "optimizer_diagnostics.json")
    _atomic_write_csv(pd.DataFrame(rows), staging / "theta_estimated.csv")
    est = {
        "specification": "joint_pooled_v1_bll0_tlmpin_p2a_singles2016_regionlive_phase3",
        "wage_spec": "vw",
        "timestamp": _utcnow(),
        "command_line": "scripts/p2a/run_p2a_regionlive_rebuild.py --phase 3",
        "status": ("PROVISIONAL - Phase 3 estimation; Phases 4-8 pending; "
                   "no identification claim (D-7)"),
        "verdict": status,
        "metadata": {
            "spec_config": cfg["certified_spec"]["yaml"],
            "authorization": cfg["phase3"]["authorization_doc"],
            "pinned_params": pmap["pin_names"],
            "at_bound": gates["g15_bound_hits_detected"],
            "start_theta_source": cfg["phase3"]["start_theta"]["csv"],
            "optimizer_options": oc["options"],
            "n_free": 37, "n_pinned": 10,
        },
        "results": {"joint": {
            "success": bool(res.success),
            "message": ("Phase-3 estimation (singles-only; frozen stem; 37-free vector; "
                        "10 immutable pins injected; region-live)"),
            "final_ll": -negll_hat,
            "parameters": {n: float(theta_hat_full[pmap["name_idx"][n]])
                           for n in pmap["all_names"]},
            "initial_values": {n: float(ctx["theta_start_full"][pmap["name_idx"][n]])
                               for n in pmap["all_names"]},
            "theta": [float(x) for x in theta_hat_full],
        }},
        "summary": {"joint_ll": -negll_hat,
                    "n_obs_total": int(p3["accepted_evidence"]["n_hh"]),
                    "n_groups_total": int(p3["accepted_evidence"]["n_hh"])},
    }
    _atomic_write_json(est, staging / "estimation_results.json")
    return status, diag


def run_phase3(args, cfg: Dict[str, Any]) -> int:
    """The ONLY production Phase-3 entrypoint (scope doc s8). Without
    --execute-phase3 this performs the non-optimizing dry-run; with it, the s5/s7
    Git + review-v6 gates must pass before the real estimation starts."""
    cfg_resolved = Path(args.config).resolve()
    if cfg_resolved != CANONICAL_PHASE3_CONFIG.resolve():
        print(f"REFUSED: Phase 3 requires the canonical config "
              f"{CANONICAL_PHASE3_CONFIG} (got {cfg_resolved}).", file=sys.stderr)
        return 2
    out_resolved = (Path(args.out).resolve() if args.out
                    else (MNL_ROOT / cfg["run"]["output_root"]).resolve())
    canonical = CANONICAL_REGIONLIVE_ROOT.resolve()
    if out_resolved != canonical:
        print(f"REFUSED: Phase-3 --out must equal the canonical production root "
              f"{canonical} (got {out_resolved}).", file=sys.stderr)
        return 2
    if (MNL_ROOT / cfg["run"]["output_root"]).resolve() != canonical:
        print("REFUSED: config run.output_root is not the canonical production root.",
              file=sys.stderr)
        return 2
    if cfg["phase3"]["output_subdir"] != CANONICAL_PHASE3_SUBDIR:
        print(f"REFUSED: config phase3.output_subdir must equal "
              f"'{CANONICAL_PHASE3_SUBDIR}'.", file=sys.stderr)
        return 2
    execute = bool(getattr(args, "execute_phase3", False))
    if not execute:
        args.dry_run = True          # --phase 3 without --execute-phase3 == dry-run
        return _phase3_run(args, cfg, {})
    gates_record = _verify_execution_gates(args)
    args.dry_run = False
    return _phase3_run(args, cfg, gates_record)


def _phase3_manifest_skeleton(args, cfg: Dict[str, Any], txn: "Phase3Transaction",
                              gates_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "run": cfg["run"]["name"] + "__phase3",
        "track": cfg["run"]["track"],
        "attempt_id": txn.attempt_id,
        "mode": ("phase3 dry-run (contract only, no optimizer)" if args.dry_run
                 else "phase3 estimation"),
        "authorization": cfg["phase3"]["authorization_doc"],
        "review_gate": ("REVIEW_V6_APPROVED" if gates_record.get("verified")
                        else "AWAITING_REVIEW_V6_APPROVE"),
        "execution_gates": gates_record or None,
        "execution_ready": bool(gates_record.get("verified", False)
                                and gates_record.get("execution_ready", False)),
        "started_at": _utcnow(),
        "status": "RUNNING",
        "stop": None,
        "optimizer_called": False,
        "config": {"path": str(Path(args.config)),
                   "sha256": _sha256(Path(args.config))},
        "script": {"path": str(SCRIPT_PATH), "sha256": _sha256(SCRIPT_PATH)},
        "git": {"MNL": _git_state(MNL_ROOT),
                "dclaborsupply-monorepo": _git_state(
                    MNL_ROOT / "dclaborsupply-monorepo")},
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__, "pandas": pd.__version__},
        "targets": cfg["targets"],
    }


def _phase3_finalize(txn: "Phase3Transaction", manifest: Dict[str, Any],
                     lines: List[str], t0: float, status: str,
                     stop: Optional[StopRun], code: int) -> int:
    """Shared attempt finalization (decision C order preserved; takes NO injectable
    component and NO root -- only the already-validated transaction)."""
    if status == "PHASE_3_COMPLETE" and txn.complete_exists():
        stop = StopRun("S-0", "phase3-immutable",
                       "complete/ appeared during the run; publish refused")
        status, code = "STOPPED", 2
    if status == "PHASE_3_COMPLETE":
        required_pre = sorted(n for n in PHASE3_ARTIFACTS
                              if n != "phase3_console.log")
        present = sorted(p.name for p in txn.staging.iterdir())
        if (present != required_pre
                or any(not (txn.staging / n).is_file() for n in required_pre)):
            stop = StopRun("S-3", "bundle-completeness",
                           f"staging artifact set {present} != required "
                           f"{required_pre} plus console")
            status, code = "STOPPED", 2
    lines.append(f"FINAL STATUS: {status}")
    _atomic_write_text("\n".join(lines) + "\n", txn.staging / "phase3_console.log")
    artifact_hashes, bundle_sha = _bundle_hashes(txn.staging)
    manifest["status"] = status
    if stop is not None:
        manifest["stop"] = {"code": stop.code, "gate": stop.gate,
                            "message": stop.message}
    manifest["finished_at"] = _utcnow()
    manifest["wall_seconds"] = round(time.time() - t0, 1)
    manifest["artifact_hashes"] = artifact_hashes
    manifest["bundle_sha256"] = bundle_sha
    _atomic_write_json(manifest, txn.staging / "phase3_manifest.json")
    if status == "PHASE_3_COMPLETE":
        final_set = sorted(p.name for p in txn.staging.iterdir())
        if final_set != sorted(list(PHASE3_ARTIFACTS) + ["phase3_manifest.json"]):
            raise RuntimeError(f"post-manifest staging set invalid: {final_set}")
    dest = txn.finish(status)
    txn.release()
    print(f"[phase3] {status} -> {dest}")
    return code


def _phase3_run(args, cfg: Dict[str, Any],
                gates_record: Dict[str, Any]) -> int:
    """Production Phase-3 attempt body (private; not a supported external
    interface). Real estimation requires the verified gates record from
    run_phase3; dry-runs are structurally non-optimizing (the estimation branch
    is never reached)."""
    if not args.dry_run and not (gates_record.get("verified") is True
                                 and gates_record.get("execution_ready") is True):
        print("REFUSED: real Phase-3 execution requires the verified Git + "
              "review-v6 gates (scope doc s5/s7).", file=sys.stderr)
        return 2
    txn = Phase3Transaction(CANONICAL_PHASE3_ROOT,
                            "dryrun" if args.dry_run else "estimate")
    t0 = time.time()
    lines: List[str] = []

    def log(msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line)
        lines.append(line)

    manifest = _phase3_manifest_skeleton(args, cfg, txn, gates_record)
    out = OutRoot(CANONICAL_REGIONLIVE_ROOT)
    acquired = False
    try:
        txn.acquire()
        acquired = True
        manifest["attempt_id"] = txn.attempt_id     # allocated under the lock
        _assert_no_prohibited_modules("phase3-start")
        if (not args.dry_run) and txn.complete_exists():
            raise StopRun("S-0", "phase3-immutable",
                          "complete/ exists; a successful Phase-3 bundle is "
                          "immutable and a new real estimation is refused")
        manifest["package_identity"] = _verify_package_identity(
            expected_commit=gates_record.get("expected_dclaborsupply_head"))
        log("Phase 3 - input contract (accepted Phase 1-2 evidence)")
        rtmap = _phase3_runtime_paths()          # ONE map per attempt
        manifest["rtmap_fingerprint"] = _runtime_map_fingerprint(rtmap)
        ctx = _phase3_contract(out, cfg, Path(args.config), log, rtmap=rtmap)
        manifest["contract"] = ctx["ev"]

        if args.dry_run:
            log("Phase 3 dry-run COMPLETE - contract verified, optimizer NOT called")
            return _phase3_finalize(txn, manifest, lines, t0,
                                    "PHASE_3_DRY_RUN_COMPLETE", None, 0)

        log("Phase 3 - estimation (real run)")

        def _mark_called() -> None:
            manifest["optimizer_called"] = True

        status, diag = _phase3_estimate(ctx, txn.staging, cfg, log,
                                        mark_optimizer_called=_mark_called)
        manifest["gates"] = diag.get("gates", {})
        manifest["input_recheck_after_optimization"] = diag.get(
            "input_recheck_after_optimization", {})
        if status == "PHASE_3_COMPLETE":
            return _phase3_finalize(txn, manifest, lines, t0, status, None, 0)
        if status == "STOPPED":
            s = diag.get("stop") or {}
            return _phase3_finalize(
                txn, manifest, lines, t0, "STOPPED",
                StopRun(s.get("code", "S-3"), s.get("gate", "phase3"),
                        s.get("message", "gate failure")), 2)
        return _phase3_finalize(txn, manifest, lines, t0, status, None, 4)

    except StopRun as stop:
        log(f"STOP {stop.code} [{stop.gate}] {stop.message}")
        if not acquired:
            print(f"[phase3] STOPPED (no attempt bundle: {stop.message})",
                  file=sys.stderr)
            return 2
        return _phase3_finalize(txn, manifest, lines, t0, "STOPPED", stop, 2)
    except Exception:
        tb = traceback.format_exc()
        log("UNEXPECTED ERROR:\n" + tb)
        if not acquired:
            print(tb, file=sys.stderr)
            return 3
        stop = StopRun("S-0", "unexpected", tb.splitlines()[-1] if tb else "unknown")
        return _phase3_finalize(txn, manifest, lines, t0, "STOPPED", stop, 3)


# --------------------------------------------------------------------------- #
# Phase 4: curvature, rank and regional identification (acceptance doc s15)
# --------------------------------------------------------------------------- #
def _validate_phase4_constants(cfg: Dict[str, Any]) -> Dict[str, bool]:
    """YAML phase4 block must equal the immutable ratified constants exactly."""
    p4 = cfg.get("phase4") or {}
    g4 = p4.get("gates") or {}
    ok: Dict[str, bool] = {}
    for k, v in PHASE4_SAFETY_CONSTANTS.items():
        ok[k] = (k in g4) and float(g4[k]) == float(v)
    ok["regional_parameters"] = (tuple(p4.get("regional_parameters") or ())
                                 == PHASE4_REGIONAL_PARAMS)
    ok["regional_design_columns"] = (tuple(p4.get("regional_design_columns") or ())
                                     == PHASE4_REGIONAL_DESIGN_COLUMNS)
    ok["regional_design_source"] = (p4.get("regional_design_source")
                                    == "production_likelihood_loader_arrays")
    ok["output_subdir"] = p4.get("output_subdir") == CANONICAL_PHASE4_SUBDIR
    b = p4.get("accepted_phase3_bundle") or {}
    ok["bundle_sha256"] = b.get("bundle_sha256") == PHASE3_ACCEPTED_BUNDLE_SHA256
    ok["negll_final"] = (float(b.get("negll_final", float("nan")))
                         == PHASE3_ACCEPTED_NEGLL_FINAL)
    if not all(ok.values()):
        raise StopRun("S-0", "phase4-constants",
                      f"YAML phase4 block != immutable ratified constants: "
                      f"{sorted(k for k, v in ok.items() if not v)}")
    return ok


def _phase4_verify_phase3_bundle(complete_dir: Path,
                                 expected_bundle_sha: str) -> Dict[str, Any]:
    """Bind Phase 4 to the ACCEPTED immutable Phase-3 bundle (acceptance s2/s4):
    exact five-file set, per-artifact hash equality with the Phase-3 manifest,
    recomputed deterministic bundle hash == manifest == the accepted constant,
    and a fully-passing recorded gate battery."""
    d = Path(complete_dir)
    required = sorted(list(PHASE3_ARTIFACTS) + ["phase3_manifest.json"])
    if not d.is_dir():
        raise StopRun("S-1", "phase3-bundle", f"accepted bundle missing: {d}")
    present = sorted(p.name for p in d.iterdir())
    if present != required:
        raise StopRun("S-1", "phase3-bundle",
                      f"bundle set {present} != required {required}")
    man = json.loads((d / "phase3_manifest.json").read_text(encoding="utf-8"))
    hashes = {n: _sha256(d / n) for n in PHASE3_ARTIFACTS}
    if man.get("artifact_hashes") != hashes:
        raise StopRun("S-8", "phase3-bundle",
                      "artifact hashes != Phase-3 manifest record")
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    bundle_sha = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    if not (bundle_sha == man.get("bundle_sha256") == expected_bundle_sha):
        raise StopRun("S-8", "phase3-bundle",
                      f"bundle sha {bundle_sha} != accepted {expected_bundle_sha}")
    if man.get("status") != "PHASE_3_COMPLETE" or man.get("optimizer_called") is not True:
        raise StopRun("S-1", "phase3-bundle",
                      "manifest is not an accepted PHASE_3_COMPLETE result")
    g = man.get("gates") or {}
    needed = ("g1_ok", "g3_ok", "g15_bound_hits_ok", "g16_inbounds_ok",
              "g2_optimizer_success", "g_pins_bitwise_unchanged")
    missing = [k for k in needed if g.get(k) is not True]
    if missing:
        raise StopRun("S-1", "phase3-bundle",
                      f"recorded Phase-3 gates not all passing: {missing}")
    return {"dir": str(d), "artifact_hashes": hashes,
            "bundle_sha256": bundle_sha, "manifest_status": man["status"],
            "manifest": man}


def _phase4_regional_names(free_names: Sequence[str],
                           cfg_list: Sequence[str]) -> List[str]:
    """Derive the regional block from the accepted spec ordering (the free
    `beta_E_*` covariate parameters; the year dummies are pinned and the plain
    `beta_E` intercept does not match) and require exact agreement with the
    canonical plan list (constant AND YAML). Conflict = STOP, never a guess."""
    derived = [n for n in free_names if n.startswith("beta_E_")]
    if (tuple(derived) != PHASE4_REGIONAL_PARAMS
            or tuple(cfg_list) != PHASE4_REGIONAL_PARAMS):
        raise StopRun("S-5", "regional-names",
                      f"regional-parameter sources conflict: spec-derived "
                      f"{derived}; config {list(cfg_list)}; plan "
                      f"{list(PHASE4_REGIONAL_PARAMS)}")
    return derived


def _phase4_regional_design(dm, dfem) -> Tuple[np.ndarray, np.ndarray,
                                               Dict[str, Any]]:
    """R-1 design from the EXACT production loader arrays that enter the JAX
    likelihood (R1 audit fix: the frozen stem's STORED reg2..reg8 are
    identically-zero region-dead placeholders the likelihood never reads; the
    loader derives its dummies from drgn1). Extracts the canonical ordered ten
    attributes directly from the two loaded singles data objects, verifies
    finiteness and within-household-block constancy, and reduces to one row per
    household at the loader's OWN group boundaries."""
    blocks: List[np.ndarray] = []
    ids: List[np.ndarray] = []
    binding = {"within_block_constant": True, "all_finite": True,
               "groups": 0}
    for d in (dm, dfem):
        arrs = [np.asarray(getattr(d, n), dtype="float64")
                for n in PHASE4_REGIONAL_DESIGN_COLUMNS]
        starts = np.asarray(d.group_starts, dtype="int64")
        ends = np.asarray(d.group_ends, dtype="int64")
        binding["groups"] += int(len(starts))
        for a in arrs:
            if not bool(np.all(np.isfinite(a))):
                binding["all_finite"] = False
            for s, e in zip(starts, ends):
                if not bool(np.all(a[s:e] == a[s])):
                    binding["within_block_constant"] = False
        blocks.append(np.column_stack([a[starts] for a in arrs]))
        ids.append(np.asarray(d.group_ids))
    M = np.vstack(blocks)
    gid = np.concatenate(ids)
    order = np.argsort(gid, kind="stable")
    binding["unique_households"] = int(np.unique(gid).size)
    return M[order], gid[order], binding


def _phase4_symmetry(H: np.ndarray,
                     rel_tol: float) -> Tuple[Dict[str, Any], np.ndarray]:
    """G-6 (D-4): max|H - H'| <= rel_tol * max|H| BEFORE symmetrization."""
    H = np.asarray(H, dtype="float64")
    max_abs = float(np.max(np.abs(H)))
    asym = float(np.max(np.abs(H - H.T)))
    thr = float(rel_tol) * max_abs
    return ({"max_abs_H": max_abs, "max_abs_asymmetry": asym,
             "threshold": thr, "ok": bool(asym <= thr)},
            0.5 * (H + H.T))


def _phase4_eigen(Hs: np.ndarray, n_expected: int,
                  c: Dict[str, Any]) -> Dict[str, Any]:
    """G-5 (PD, n_nonpos), G-7 (rank under eps_rank), G-8 (condition tier)."""
    eig, vec = np.linalg.eigh(np.asarray(Hs, dtype="float64"))
    min_eig, max_eig = float(eig[0]), float(eig[-1])
    max_abs = float(np.max(np.abs(eig)))
    tol = float(c["rank_rel_tol"]) * max_abs
    rank = int(np.sum(eig > tol))
    cond = float(max_eig / min_eig) if min_eig > 0.0 else float("inf")
    tier = ("clean" if cond <= float(c["condition_clean_max"])
            else "warning" if cond <= float(c["condition_warn_max"])
            else "failure")
    return {"eigenvalues": [float(x) for x in eig],
            "min_eig": min_eig, "max_eig": max_eig,
            "rank_tolerance": tol, "rank": rank,
            "rank_expected": int(n_expected),
            "rank_ok": bool(rank == int(n_expected)),
            "n_nonpos": int(np.sum(eig <= float(c["nonpos_count_eig_tol"]))),
            "pd_ok": bool(min_eig > 0.0),
            "condition_number": cond, "condition_tier": tier,
            "condition_ok": bool(tier != "failure"),
            "pooled_baseline_condition": float(c["pooled_baseline_condition"]),
            "_eigvecs": vec}


def _phase4_design_rank(M: np.ndarray, rank_rel_tol: float) -> Dict[str, Any]:
    """R-1 (D-3): household-level regional design matrix rank under eps_rank,
    with singular values and |corr| > 0.9 sub-check reported."""
    M = np.asarray(M, dtype="float64")
    sv = np.linalg.svd(M, compute_uv=False)
    tol = float(rank_rel_tol) * float(sv[0])
    rank = int(np.sum(sv > tol))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.corrcoef(M, rowvar=False)
    flags = [{"i": int(i), "j": int(j), "corr": float(corr[i, j])}
             for i in range(M.shape[1]) for j in range(i + 1, M.shape[1])
             if np.isfinite(corr[i, j]) and abs(float(corr[i, j])) > 0.9]
    return {"shape": [int(M.shape[0]), int(M.shape[1])],
            "singular_values": [float(x) for x in sv],
            "rank_tolerance": tol, "rank": rank,
            "rank_ok": bool(rank == int(M.shape[1])),
            "high_corr_pairs": flags}


def _phase4_schur(Hs: np.ndarray, reg_pos: Sequence[int],
                  c: Dict[str, Any]) -> Dict[str, Any]:
    """R-2 + R-4 (D-3): raw regional sub-block PD, and the conditional regional
    Schur complement H_RR - H_RO H_OO^{-1} H_OR computed via a numerically
    stable SOLVE (never an explicit inverse); the plan-v1 pinv(rcond 1e-10)
    construction is recomputed only as an informational cross-check."""
    Hs = np.asarray(Hs, dtype="float64")
    n = Hs.shape[0]
    reg = np.asarray(sorted(int(i) for i in reg_pos), dtype="int64")
    oth = np.asarray([i for i in range(n) if i not in set(reg.tolist())],
                     dtype="int64")
    H_RR = Hs[np.ix_(reg, reg)]
    H_RO = Hs[np.ix_(reg, oth)]
    H_OO = Hs[np.ix_(oth, oth)]
    raw_sym = 0.5 * (H_RR + H_RR.T)
    raw_eig = np.linalg.eigvalsh(raw_sym)
    try:
        X = np.linalg.solve(H_OO, H_RO.T)          # H_OO X = H_OR (stable solve)
    except np.linalg.LinAlgError as exc:
        raise StopRun("S-5", "schur-solve", f"H_OO solve failed: {exc}")
    S = H_RR - H_RO @ X
    S_sym = 0.5 * (S + S.T)
    eig = np.linalg.eigvalsh(S_sym)
    tol = float(c["rank_rel_tol"]) * float(np.max(np.abs(eig)))
    S_pinv = H_RR - H_RO @ np.linalg.pinv(H_OO, rcond=1e-10) @ H_RO.T
    return {"regional_positions_free": [int(i) for i in reg],
            "raw_subblock_eigenvalues": [float(x) for x in raw_eig],
            "raw_subblock_min_eig": float(raw_eig[0]),
            "raw_subblock_pd_ok": bool(float(raw_eig[0]) > 0.0),
            "schur_eigenvalues": [float(x) for x in eig],
            "schur_min_eig": float(eig[0]),
            "schur_min_eig_ok": bool(float(eig[0]) > 0.0),
            "schur_rank_tolerance": tol,
            "schur_rank": int(np.sum(eig > tol)),
            "schur_rank_ok": bool(int(np.sum(eig > tol)) == len(reg)),
            "solve_vs_pinv_max_abs_diff": float(np.max(np.abs(
                S_sym - 0.5 * (S_pinv + S_pinv.T)))),
            "_H_RR": H_RR, "_S": S_sym}


def _phase4_loading_shares(eigvals: np.ndarray, eigvecs: np.ndarray,
                           reg_pos: Sequence[int], warn: float) -> Dict[str, Any]:
    """R-3 (D-3, warning only, never gates): regional squared-loading share of
    every eigenvector; the three smallest carry the warning flag at >= warn."""
    reg = np.asarray(sorted(int(i) for i in reg_pos), dtype="int64")
    shares = [float(np.sum(eigvecs[reg, j] ** 2) / np.sum(eigvecs[:, j] ** 2))
              for j in range(eigvecs.shape[1])]
    smallest = [{"eig_index": j, "eigenvalue": float(eigvals[j]),
                 "regional_loading_share": shares[j],
                 "warning_ge_threshold": bool(shares[j] >= float(warn))}
                for j in range(min(3, len(shares)))]
    return {"all_shares": shares, "three_smallest": smallest,
            "threshold": float(warn),
            "any_warning": bool(any(s["warning_ge_threshold"] for s in smallest)),
            "note": "warning-only diagnostic (D-3); never gates"}


def _phase4_contract(out: OutRoot, cfg: Dict[str, Any], config_path: Path,
                     log, rtmap: Optional[Dict[str, Path]] = None
                     ) -> Dict[str, Any]:
    """Phase-4 input contract: full Phase-3 contract revalidation, immutable
    accepted-bundle binding, accepted-theta load (never altered), exact
    regional-name binding, design-source validation, objective consistency at
    theta_hat, and derivative-route construction WITHOUT evaluation."""
    import jax
    import jax.numpy as jnp

    p4 = cfg["phase4"]
    ev: Dict[str, Any] = {"checked_at": _utcnow()}
    ev["phase4_constants_ok"] = _validate_phase4_constants(cfg)
    ctx3 = _phase3_contract(out, cfg, config_path, log, rtmap=rtmap)

    bundle_dir = (MNL_ROOT / p4["accepted_phase3_bundle"]["dir"]).resolve()
    if bundle_dir != (CANONICAL_PHASE3_ROOT / "complete").resolve():
        raise StopRun("S-1", "phase3-bundle",
                      "configured accepted bundle dir is not the canonical "
                      "phase3_estimation_v1/complete")
    bundle = _phase4_verify_phase3_bundle(bundle_dir, PHASE3_ACCEPTED_BUNDLE_SHA256)
    man3 = bundle.pop("manifest")
    ev["phase3_bundle"] = bundle

    names, pmap = ctx3["names"], ctx3["pmap"]
    tab = pd.read_csv(bundle_dir / "theta_estimated.csv")
    if list(tab["param"]) != names:
        raise StopRun("S-1", "phase4-contract",
                      "accepted theta_estimated.csv ordering != specification")
    theta_csv = tab["value"].astype("float64").to_numpy()
    res3 = json.loads((bundle_dir / "estimation_results.json")
                      .read_text(encoding="utf-8"))
    # the JSON theta is the authoritative full-precision vector: it is bitwise
    # consistent with optimizer_diagnostics final_theta + its recorded sha; the
    # CSV table carries pandas ~16-digit formatting (<= 1 ulp representational)
    theta_hat = np.asarray(res3["results"]["joint"]["theta"], dtype="float64")
    diag3 = json.loads((bundle_dir / "optimizer_diagnostics.json")
                       .read_text(encoding="utf-8"))
    if not np.array_equal(theta_hat, np.asarray(diag3["final_theta"],
                                                dtype="float64")):
        raise StopRun("S-8", "phase4-contract",
                      "bundle results/diagnostics theta vectors disagree")
    if diag3.get("final_theta_sha256") != _theta_sha(theta_hat):
        raise StopRun("S-8", "phase4-contract",
                      "bundle final_theta_sha256 != recomputed theta hash")
    if not np.allclose(theta_csv, theta_hat, rtol=1e-12, atol=0.0):
        raise StopRun("S-8", "phase4-contract",
                      "bundle theta csv/json vectors disagree beyond "
                      "representational round-off")
    if not all(np.float64(theta_hat[pmap["pin_idx"][k]]).tobytes()
               == np.float64(pmap["pin_values"][k]).tobytes()
               for k in range(len(pmap["pin_names"]))):
        raise StopRun("S-8", "phase4-contract",
                      "accepted theta pins not bitwise-identical to pin values")
    free_hat = project_full_to_free(pmap, theta_hat)
    ev["theta_hat_sha256"] = _theta_sha(theta_hat)
    diag3 = json.loads((bundle_dir / "optimizer_diagnostics.json")
                       .read_text(encoding="utf-8"))
    pub_grad_free = np.asarray(diag3["gradient_free_projection"], dtype="float64")
    if pub_grad_free.shape != (len(pmap["free_names"]),):
        raise StopRun("S-1", "phase4-contract",
                      "published free-gradient projection has wrong length")

    reg_names = _phase4_regional_names(pmap["free_names"],
                                       p4["regional_parameters"])
    reg_pos_free = [pmap["free_names"].index(n) for n in reg_names]
    ev["regional"] = {"names": reg_names,
                      "free_positions": [int(i) for i in reg_pos_free],
                      "design_columns": list(PHASE4_REGIONAL_DESIGN_COLUMNS),
                      "column_to_parameter": dict(zip(
                          PHASE4_REGIONAL_DESIGN_COLUMNS, reg_names))}

    # R-1 source (R1 audit fix / CURRENT_R1_FALSE_FAILURE): the EXACT
    # production loader arrays behind the likelihood objective -- NEVER the
    # stem's stored reg2..reg8 (identically-zero region-dead placeholders)
    dcols = list(PHASE4_REGIONAL_DESIGN_COLUMNS)
    dm_l, df_l = ctx3["loader_data"]
    design_M, design_ids, binding = _phase4_regional_design(dm_l, df_l)
    n_hh = int(cfg["phase3"]["accepted_evidence"]["n_hh"])
    if design_M.shape != (n_hh, len(dcols)):
        raise StopRun("S-5", "phase4-contract",
                      f"design shape {design_M.shape} != ({n_hh}, {len(dcols)})")
    if binding["unique_households"] != n_hh or binding["groups"] != n_hh:
        raise StopRun("S-5", "phase4-contract",
                      "loader group structure does not yield one row per "
                      "household")
    if not (binding["within_block_constant"] and binding["all_finite"]):
        raise StopRun("S-5", "phase4-contract",
                      f"loader design arrays invalid: {binding}")
    design = pd.DataFrame(
        design_M, columns=dcols,
        index=pd.Index(design_ids.astype("int64"), name="idhh"))
    ev["regional_design_source"] = "production_likelihood_loader_arrays"
    ev["design_shape"] = [int(x) for x in design_M.shape]
    ev["design_column_names"] = dcols
    ev["design_column_to_parameter"] = dict(zip(dcols, reg_names))
    ev["design_loader_binding"] = binding

    # objective consistency at the ACCEPTED estimate (evaluation only)
    negll_hat = float(ctx3["tot"](jnp.asarray(theta_hat)))
    ev["negll_at_theta_hat"] = negll_hat
    ev["negll_abs_dev_accepted"] = abs(negll_hat - PHASE3_ACCEPTED_NEGLL_FINAL)
    ev["negll_abs_dev_target"] = abs(negll_hat - float(ctx3["target"]))
    if ev["negll_abs_dev_accepted"] > PHASE4_SAFETY_CONSTANTS[
            "consistency_negll_tol"]:
        raise StopRun("S-8", "phase4-contract",
                      f"negLL(theta_hat) deviates "
                      f"{ev['negll_abs_dev_accepted']:.3e} from the accepted "
                      f"final value")

    # derivative route: CONSTRUCTED here, evaluated only in the real run
    free_idx = jnp.asarray(np.asarray(pmap["free_idx"], dtype="int64"))
    base_full = jnp.asarray(expand_free_to_full(pmap, np.zeros(len(free_hat))))
    tot = ctx3["tot"]

    def negll_free(x_free):
        return tot(base_full.at[free_idx].set(x_free))

    hess_fn = jax.hessian(negll_free)
    grad_fn = jax.grad(negll_free)
    ev["derivative_route"] = {
        "objective": "package build_jax_singles_ll sm+sf (float64)",
        "hessian": "jax.hessian over the ordered 37-free vector (pins fixed)",
        "gradient": "jax.grad over the same free vector",
        "loaded": True, "evaluated": False}
    ev["ok"] = True
    log(f"phase4 contract: bundle {bundle['bundle_sha256'][:12]}... ok | "
        f"negLL(theta_hat)={negll_hat:.10f} "
        f"(dev {ev['negll_abs_dev_accepted']:.2e}) | regional {len(reg_names)}")
    return {**ctx3, "ev4": ev, "theta_hat": theta_hat, "free_hat": free_hat,
            "reg_names": reg_names, "reg_pos_free": reg_pos_free,
            "design": design, "hess_fn": hess_fn, "grad_fn": grad_fn,
            "negll_hat": negll_hat, "pub_grad_free": pub_grad_free,
            "man3": man3}


def _phase4_diagnose(ctx: Dict[str, Any], log,
                     progress: Optional[Dict[str, Any]] = None
                     ) -> Tuple[str, Optional[StopRun], Dict[str, Any],
                                Dict[str, np.ndarray]]:
    """Real Phase-4 diagnostics at the accepted estimate: gradient consistency,
    exact 37x37 JAX Hessian, G-5..G-8 and R-1..R-4 batteries. NEVER optimizes,
    never alters theta, never computes standard errors. `progress` (review-v2
    fix 1) is the orchestration-owned mutable attempt state: each derivative
    flag flips IMMEDIATELY after its callable returns, and the live diag dict
    is exposed as partial_diagnostics so exception finalization stays accurate."""
    import jax.numpy as jnp

    c = PHASE4_SAFETY_CONSTANTS
    pmap = ctx["pmap"]
    if progress is None:
        progress = {}
    progress.setdefault("gradient_evaluated", False)
    progress.setdefault("hessian_evaluated", False)
    diag: Dict[str, Any] = {"generated_at": _utcnow(),
                            "theta_hat_sha256": ctx["ev4"]["theta_hat_sha256"],
                            "negll_at_theta_hat": ctx["negll_hat"]}
    progress["partial_diagnostics"] = diag      # live reference, never copied

    grad_free = np.asarray(ctx["grad_fn"](jnp.asarray(ctx["free_hat"])),
                           dtype="float64")
    progress["gradient_evaluated"] = True       # set BEFORE any gradient gate
    grad_dev = float(np.max(np.abs(grad_free - ctx["pub_grad_free"])))
    diag["gradient_free"] = [float(x) for x in grad_free]
    diag["gradient_consistency_max_abs_dev"] = grad_dev
    if grad_dev > float(c["consistency_grad_tol"]):
        raise StopRun("S-8", "phase4-gradient",
                      f"free gradient deviates {grad_dev:.3e} from the "
                      f"published Phase-3 gradient")
    nb = [i for i, n in enumerate(pmap["free_names"])
          if n not in set(EXPECTED_AT_BOUND_NAMES)]
    diag["g3_consistency_max_abs_grad_35free"] = float(
        np.max(np.abs(grad_free[nb])))

    log("phase4: evaluating exact 37x37 JAX Hessian at the accepted estimate")
    t0 = time.time()
    H = np.asarray(ctx["hess_fn"](jnp.asarray(ctx["free_hat"])),
                   dtype="float64")
    progress["hessian_evaluated"] = True        # set BEFORE any Hessian gate
    diag["hessian_evaluated"] = True
    diag["hessian_wall_seconds"] = round(time.time() - t0, 1)
    log(f"phase4: Hessian evaluated ({diag['hessian_wall_seconds']}s)")

    sym, Hs = _phase4_symmetry(H, c["symmetry_rel_tol"])
    diag["symmetry"] = sym
    eigen = _phase4_eigen(Hs, int(c["n_free"]), c)
    vec = eigen.pop("_eigvecs")
    diag["eigen"] = eigen
    diag["loading_shares"] = _phase4_loading_shares(
        np.asarray(eigen["eigenvalues"]), vec, ctx["reg_pos_free"],
        c["loading_share_warn"])
    diag["design"] = _phase4_design_rank(
        ctx["design"].to_numpy(dtype="float64"), c["rank_rel_tol"])
    diag["design"]["regional_design_source"] = ctx.get("ev4", {}).get(
        "regional_design_source", "test_fake_context")
    schur = _phase4_schur(Hs, ctx["reg_pos_free"], c)
    H_RR = schur.pop("_H_RR")
    S = schur.pop("_S")
    diag["regional"] = schur

    gates = {
        "g5_pd_ok": eigen["pd_ok"],
        "g5_n_nonpos": eigen["n_nonpos"],
        "g6_symmetry_ok": sym["ok"],
        "g7_rank": eigen["rank"],
        "g7_rank_ok": eigen["rank_ok"],
        "g8_condition_number": eigen["condition_number"],
        "g8_condition_tier": eigen["condition_tier"],
        "g8_condition_ok": eigen["condition_ok"],
        "r1_design_rank": diag["design"]["rank"],
        "r1_design_rank_ok": bool(diag["design"]["rank"]
                                  == int(c["regional_n"])),
        "r2_raw_subblock_pd_ok": schur["raw_subblock_pd_ok"],
        "r4_schur_rank_ok": schur["schur_rank_ok"],
        "r4_schur_min_eig_ok": schur["schur_min_eig_ok"],
        "r3_loading_share_warning": diag["loading_shares"]["any_warning"],
    }
    gates["region_urbanisation_identification"] = bool(
        gates["r1_design_rank_ok"] and gates["r2_raw_subblock_pd_ok"]
        and gates["r4_schur_rank_ok"] and gates["r4_schur_min_eig_ok"])
    diag["gates"] = gates
    warnings = []
    if gates["g8_condition_tier"] == "warning":
        warnings.append("condition number in the 1e7-1e10 warning tier")
    if gates["r3_loading_share_warning"]:
        warnings.append("regional loading share >= 0.5 on a smallest eigenvector")
    if diag["design"]["high_corr_pairs"]:
        warnings.append("regional design |corr| > 0.9 pair(s)")
    diag["warnings"] = warnings
    diag["identification_scope"] = ("real-data LOCAL identification diagnostics "
                                    "only; no synthetic-recovery claim (D-7)")

    curvature_ok = (gates["g5_pd_ok"] and gates["g6_symmetry_ok"]
                    and gates["g7_rank_ok"] and gates["g8_condition_ok"])
    arrays = {"H": H, "Hs": Hs, "H_RR": H_RR, "S": S,
              "eigvals": np.asarray(eigen["eigenvalues"]),
              "shares": np.asarray(diag["loading_shares"]["all_shares"])}
    # review-v1 fix (raw-subblock coverage): when the regional hard conjunction
    # fails, S-5/G-9 is the registered stop even if curvature gates also fail --
    # eigenvalue interlacing makes a non-PD regional subblock imply a non-PD
    # full Hessian, so the joint failure is the typical R-2 case; curvature
    # flags remain recorded in gates either way
    if not gates["region_urbanisation_identification"]:
        return ("STOPPED",
                StopRun("S-5", "G-9",
                        "region x urbanisation hard gates failed "
                        "(R-1/R-2/R-4); evidence to the manager"),
                diag, arrays)
    if not curvature_ok:
        return ("STOPPED",
                StopRun("S-4", "curvature",
                        f"curvature gate failure: G-5 {gates['g5_pd_ok']}, "
                        f"G-6 {gates['g6_symmetry_ok']}, "
                        f"G-7 {gates['g7_rank_ok']}, "
                        f"G-8 {gates['g8_condition_tier']}"),
                diag, arrays)
    return "PHASE_4_COMPLETE", None, diag, arrays


def _phase4_write_artifacts(staging: Path, ctx: Dict[str, Any],
                            diag: Dict[str, Any],
                            arrays: Dict[str, np.ndarray]) -> None:
    """Stage every non-console Phase-4 artifact atomically."""
    fn = list(ctx["pmap"]["free_names"])
    hdf = pd.DataFrame(arrays["H"], columns=fn)
    hdf.insert(0, "param", fn)
    _atomic_write_csv(hdf, staging / "hessian_free.csv")
    tmp = staging / "hessian_free.npy.tmp"
    with open(tmp, "wb") as f:
        np.save(f, arrays["H"])
    os.replace(tmp, staging / "hessian_free.npy")
    edf = pd.DataFrame({
        "index": range(len(arrays["eigvals"])),
        "eigenvalue": arrays["eigvals"],
        "regional_loading_share": arrays["shares"]})
    _atomic_write_csv(edf, staging / "hessian_eigenvalues.csv")
    rn = list(ctx["reg_names"])
    rdf = pd.DataFrame(arrays["H_RR"], columns=rn)
    rdf.insert(0, "param", rn)
    _atomic_write_csv(rdf, staging / "regional_hessian_subblock.csv")
    sdf = pd.DataFrame(arrays["S"], columns=rn)
    sdf.insert(0, "param", rn)
    _atomic_write_csv(sdf, staging / "regional_schur_complement.csv")
    _atomic_write_json(diag, staging / "phase4_diagnostics.json")


def _phase4_manifest_skeleton(args, cfg: Dict[str, Any],
                              txn: "Phase3Transaction",
                              gates_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "run": cfg["run"]["name"] + "__phase4",
        "track": cfg["run"]["track"],
        "phase": 4,
        "attempt_id": txn.attempt_id,
        "mode": ("phase4 dry-run (contract only, no Hessian)" if args.dry_run
                 else "phase4 curvature diagnostics"),
        "authorization": cfg["phase4"]["authorization_doc"],
        "review_gate": ("PHASE4_REVIEW_V7_APPROVED"
                        if gates_record.get("verified")
                        else "AWAITING_PHASE4_REVIEW_V7_APPROVE"),
        "execution_gates": gates_record or None,
        "execution_ready": bool(gates_record.get("verified", False)
                                and gates_record.get("execution_ready", False)),
        "accepted_phase3_bundle_sha256": PHASE3_ACCEPTED_BUNDLE_SHA256,
        "started_at": _utcnow(),
        "status": "RUNNING",
        "stop": None,
        "optimizer_called": False,       # Phase 4 NEVER optimizes
        "gradient_evaluated": False,
        "hessian_evaluated": False,
        "config": {"path": str(Path(args.config)),
                   "sha256": _sha256(Path(args.config))},
        "script": {"path": str(SCRIPT_PATH), "sha256": _sha256(SCRIPT_PATH)},
        "git": {"MNL": _git_state(MNL_ROOT),
                "dclaborsupply-monorepo": _git_state(
                    MNL_ROOT / "dclaborsupply-monorepo")},
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__, "pandas": pd.__version__},
        "targets": cfg["targets"],
    }


def _phase4_finalize(txn: "Phase3Transaction", manifest: Dict[str, Any],
                     lines: List[str], t0: float, status: str,
                     stop: Optional[StopRun], code: int) -> int:
    """Phase-4 attempt finalization: decision-C order (console, artifact hashes
    with NO manifest self-hash, manifest LAST, exact-set check, atomic publish)."""
    if status == "PHASE_4_COMPLETE" and txn.complete_exists():
        stop = StopRun("S-0", "phase4-immutable",
                       "complete/ appeared during the run; publish refused")
        status, code = "STOPPED", 2
    if status == "PHASE_4_COMPLETE":
        required_pre = sorted(n for n in PHASE4_ARTIFACTS
                              if n != "phase4_console.log")
        present = sorted(p.name for p in txn.staging.iterdir())
        if (present != required_pre
                or any(not (txn.staging / n).is_file() for n in required_pre)):
            stop = StopRun("S-3", "bundle-completeness",
                           f"staging artifact set {present} != required "
                           f"{required_pre} plus console")
            status, code = "STOPPED", 2
    lines.append(f"FINAL STATUS: {status}")
    _atomic_write_text("\n".join(lines) + "\n", txn.staging / "phase4_console.log")
    hashes = {n: _sha256(txn.staging / n) for n in PHASE4_ARTIFACTS
              if (txn.staging / n).is_file()}
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    manifest["status"] = status
    if stop is not None:
        manifest["stop"] = {"code": stop.code, "gate": stop.gate,
                            "message": stop.message}
    manifest["finished_at"] = _utcnow()
    manifest["wall_seconds"] = round(time.time() - t0, 1)
    manifest["artifact_hashes"] = hashes
    manifest["bundle_sha256"] = hashlib.sha256(
        joined.encode("utf-8")).hexdigest()
    _atomic_write_json(manifest, txn.staging / "phase4_manifest.json")
    if status == "PHASE_4_COMPLETE":
        final_set = sorted(p.name for p in txn.staging.iterdir())
        if final_set != sorted(list(PHASE4_ARTIFACTS)
                               + ["phase4_manifest.json"]):
            raise RuntimeError(f"post-manifest staging set invalid: {final_set}")
    dest = txn.finish(status)
    txn.release()
    print(f"[phase4] {status} -> {dest}")
    return code


def _phase4_merge_progress(manifest: Dict[str, Any],
                           progress: Dict[str, Any]) -> None:
    """Flags-only merge of the live derivative-progress state (review-v2 fix
    1) for the successful/gated route. Every EXCEPTIONAL path goes through the
    single policy in _merge_phase4_exception_evidence (review-v4 fix 2)."""
    manifest["gradient_evaluated"] = bool(progress.get("gradient_evaluated"))
    manifest["hessian_evaluated"] = bool(progress.get("hessian_evaluated"))


def _phase4_evidence_status(gate: Optional[str]) -> str:
    """Evidence label for retained pre-staging exceptional diagnostics
    (review-v3 fix 3): post-evaluation authentication stops are labelled
    distinctly."""
    return ("FAILED_AUTHENTICATION_ATTEMPT"
            if gate in ("runtime-map", "input-recheck")
            else "STOPPED_ATTEMPT_PARTIAL_EVIDENCE")


def _merge_phase4_exception_evidence(manifest: Dict[str, Any],
                                     progress: Dict[str, Any],
                                     stop_or_exc: BaseException) -> None:
    """THE single exceptional-evidence merge policy (review-v4 fixes 1-2), used
    by every Phase-4 exception handler. Whether partial diagnostics attach is
    decided ONLY by progress["artifacts_staged"]:

    - artifacts NOT staged: the live record attaches as partial_diagnostics
      with the pre-staging evidence label (FAILED_AUTHENTICATION_ATTEMPT for
      the runtime-map/input-recheck gates, STOPPED_ATTEMPT_PARTIAL_EVIDENCE
      otherwise);
    - artifacts staged: the staged phase4_diagnostics.json is the SOLE
      authoritative scientific record -- no duplicate manifest copy, any stale
      partial_diagnostics key is removed, and the evidence is labelled
      FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT with the artifact named
      as the authority."""
    manifest["gradient_evaluated"] = bool(progress.get("gradient_evaluated"))
    manifest["hessian_evaluated"] = bool(progress.get("hessian_evaluated"))
    if isinstance(stop_or_exc, StopRun):
        manifest["exception"] = {"type": "StopRun",
                                 "message": stop_or_exc.message,
                                 "code": stop_or_exc.code,
                                 "gate": stop_or_exc.gate}
        gate: Optional[str] = stop_or_exc.gate
    else:
        manifest["exception"] = {"type": type(stop_or_exc).__name__,
                                 "message": str(stop_or_exc)}
        gate = None
    if progress.get("artifacts_staged"):
        manifest.pop("partial_diagnostics", None)
        manifest["diagnostic_evidence_status"] = (
            "FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT")
        manifest["diagnostic_artifact_authority"] = (
            progress.get("diagnostics_artifact_name")
            or "phase4_diagnostics.json")
        manifest["diagnostic_artifact_staged"] = True
    elif progress.get("partial_diagnostics") is not None:
        manifest["partial_diagnostics"] = progress["partial_diagnostics"]
        manifest["diagnostic_evidence_status"] = _phase4_evidence_status(gate)


def _phase4_run_diagnostics(txn: "Phase3Transaction", manifest: Dict[str, Any],
                            lines: List[str], t0: float, ctx: Dict[str, Any],
                            log, progress: Dict[str, Any]) -> int:
    """Real-run diagnostic body (review-v2 fixes 1-2; also driven by the
    exceptional-path tests with fake-derivative contexts): evaluates via
    _phase4_diagnose under live progress accounting, merges that state into
    the manifest on EVERY outcome -- including a StopRun raised mid-diagnostics
    after a derivative already evaluated -- and finalizes. The post-evaluation
    input recheck runs whenever the ctx carries the production runtime map."""
    try:
        status, stop, diag, arrays = _phase4_diagnose(ctx, log,
                                                      progress=progress)
        _phase4_merge_progress(manifest, progress)
        manifest["gates4"] = diag.get("gates", {})
        manifest["warnings"] = diag.get("warnings", [])
        if "rtmap" in ctx and "input_auth" in ctx:
            # post-evaluation input recheck BEFORE any result write (decision G)
            fp_post = _runtime_map_fingerprint(ctx["rtmap"])
            if fp_post != ctx["rtmap_fingerprint"]:
                raise StopRun("S-8", "runtime-map",
                              "runtime-map fingerprint changed during the "
                              "attempt")
            recheck, recheck_ok = _recheck_inputs(ctx["input_auth"],
                                                  runtime_paths=ctx["rtmap"])
            manifest["input_recheck_after_evaluation"] = recheck
            if not recheck_ok:
                raise StopRun("S-8", "input-recheck",
                              "input hash recheck failed after evaluation")
        _phase4_write_artifacts(txn.staging, ctx, diag, arrays)
        # review-v4 fix 1: staging state lives in the SHARED progress object,
        # set only after every required numerical artifact was written
        progress["artifacts_staged"] = True
        progress["diagnostics_artifact_name"] = "phase4_diagnostics.json"
        if status == "PHASE_4_COMPLETE":
            return _phase4_finalize(txn, manifest, lines, t0, status, None, 0)
        return _phase4_finalize(txn, manifest, lines, t0, "STOPPED", stop, 2)
    except StopRun as stop:
        log(f"STOP {stop.code} [{stop.gate}] {stop.message}")
        _merge_phase4_exception_evidence(manifest, progress, stop)
        return _phase4_finalize(txn, manifest, lines, t0, "STOPPED", stop, 2)
    except Exception as exc:
        # review-v4 fix 1: unexpected post-contract failures (including any
        # raised AFTER artifact staging) finalize here, where the shared
        # staging state is available to the single merge policy
        tb = traceback.format_exc()
        log("UNEXPECTED ERROR:\n" + tb)
        _merge_phase4_exception_evidence(manifest, progress, exc)
        stop = StopRun("S-0", "unexpected", tb.splitlines()[-1] if tb else
                       "unknown")
        return _phase4_finalize(txn, manifest, lines, t0, "STOPPED", stop, 3)


def _phase4_run(args, cfg: Dict[str, Any],
                gates_record: Dict[str, Any]) -> int:
    """Production Phase-4 attempt body (private). Real diagnostics require the
    verified gates record from run_phase4; dry-runs never evaluate the Hessian
    (the evaluation branch is structurally unreachable)."""
    if not args.dry_run and not (gates_record.get("verified") is True
                                 and gates_record.get("execution_ready") is True):
        print("REFUSED: real Phase-4 diagnostics require the verified Git + "
              "Phase-4 review-v7 approval gates.", file=sys.stderr)
        return 2
    txn = Phase3Transaction(CANONICAL_PHASE4_ROOT,
                            "dryrun" if args.dry_run else "curvature",
                            success_status="PHASE_4_COMPLETE")
    t0 = time.time()
    lines: List[str] = []

    def log(msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line)
        lines.append(line)

    manifest = _phase4_manifest_skeleton(args, cfg, txn, gates_record)
    out = OutRoot(CANONICAL_REGIONLIVE_ROOT)
    acquired = False
    # orchestration-owned live attempt state (review-v2 fix 1; review-v4 fix
    # 1): visible to every finalization path, including exceptions after
    # evaluation and after artifact staging
    progress: Dict[str, Any] = {"gradient_evaluated": False,
                                "hessian_evaluated": False,
                                "partial_diagnostics": None,
                                "artifacts_staged": False,
                                "diagnostics_artifact_name": None}
    try:
        txn.acquire()
        acquired = True
        manifest["attempt_id"] = txn.attempt_id     # allocated under the lock
        _assert_no_prohibited_modules("phase4-start")
        if (not args.dry_run) and txn.complete_exists():
            raise StopRun("S-0", "phase4-immutable",
                          "complete/ exists; a successful Phase-4 bundle is "
                          "immutable and a new real run is refused")
        manifest["package_identity"] = _verify_package_identity(
            expected_commit=gates_record.get("expected_dclaborsupply_head"))
        log("Phase 4 - contract (accepted Phase-3 bundle + inputs)")
        rtmap = _phase4_runtime_paths()             # ONE map per attempt
        manifest["rtmap_fingerprint"] = _runtime_map_fingerprint(rtmap)
        ctx = _phase4_contract(out, cfg, Path(args.config), log, rtmap=rtmap)
        manifest["contract"] = ctx["ev"]
        manifest["contract_phase4"] = ctx["ev4"]

        if args.dry_run:
            log("Phase 4 dry-run COMPLETE - contract verified, Hessian NOT "
                "evaluated")
            return _phase4_finalize(txn, manifest, lines, t0,
                                    "PHASE_4_DRY_RUN_COMPLETE", None, 0)

        log("Phase 4 - curvature diagnostics (real run)")
        return _phase4_run_diagnostics(txn, manifest, lines, t0, ctx, log,
                                       progress)

    except StopRun as stop:
        log(f"STOP {stop.code} [{stop.gate}] {stop.message}")
        if not acquired:
            print(f"[phase4] STOPPED (no attempt bundle: {stop.message})",
                  file=sys.stderr)
            return 2
        _merge_phase4_exception_evidence(manifest, progress, stop)
        return _phase4_finalize(txn, manifest, lines, t0, "STOPPED", stop, 2)
    except Exception as exc:
        tb = traceback.format_exc()
        log("UNEXPECTED ERROR:\n" + tb)
        if not acquired:
            print(tb, file=sys.stderr)
            return 3
        # review-v4 fix 3: the SAME single merge policy, consulting the shared
        # progress["artifacts_staged"] state -- never unconditional
        _merge_phase4_exception_evidence(manifest, progress, exc)
        stop = StopRun("S-0", "unexpected", tb.splitlines()[-1] if tb else
                       "unknown")
        return _phase4_finalize(txn, manifest, lines, t0, "STOPPED", stop, 3)


def _phase4_runtime_paths() -> Dict[str, Path]:
    """Phase 4 consumes exactly the Phase-3 runtime map (same ten labels); the
    accepted Phase-3 bundle is bound separately by its deterministic hash."""
    return _phase3_runtime_paths()


def run_phase4(args, cfg: Dict[str, Any]) -> int:
    """The ONLY production Phase-4 entrypoint (acceptance doc s15). Without
    --execute-phase4 this performs the non-evaluating dry-run; with it, the
    Git gates plus the PHASE-4-SPECIFIC review-v7 APPROVE must pass first
    (Phase-4 reviews v1-v6 and the Phase-3 review-v6 are rejected)."""
    cfg_resolved = Path(args.config).resolve()
    if cfg_resolved != CANONICAL_PHASE3_CONFIG.resolve():
        print(f"REFUSED: Phase 4 requires the canonical config "
              f"{CANONICAL_PHASE3_CONFIG} (got {cfg_resolved}).", file=sys.stderr)
        return 2
    out_resolved = (Path(args.out).resolve() if args.out
                    else (MNL_ROOT / cfg["run"]["output_root"]).resolve())
    canonical = CANONICAL_REGIONLIVE_ROOT.resolve()
    if out_resolved != canonical:
        print(f"REFUSED: Phase-4 --out must equal the canonical production root "
              f"{canonical} (got {out_resolved}).", file=sys.stderr)
        return 2
    if (MNL_ROOT / cfg["run"]["output_root"]).resolve() != canonical:
        print("REFUSED: config run.output_root is not the canonical production "
              "root.", file=sys.stderr)
        return 2
    if (cfg.get("phase4") or {}).get("output_subdir") != CANONICAL_PHASE4_SUBDIR:
        print(f"REFUSED: config phase4.output_subdir must equal "
              f"'{CANONICAL_PHASE4_SUBDIR}'.", file=sys.stderr)
        return 2
    execute = bool(getattr(args, "execute_phase4", False))
    if not execute:
        args.dry_run = True          # --phase 4 without --execute-phase4 == dry-run
        return _phase4_run(args, cfg, {})
    # review v1-v6 + R1-audit fixes: the PHASE-4-SPECIFIC gate must pass
    # before any gradient/Hessian evaluation -- it accepts phase4 review v7
    # only (never Phase-4 reviews v1-v6, never the Phase-3 review-v6)
    gates_record = _verify_phase4_execution_gates(args)
    args.dry_run = False
    return _phase4_run(args, cfg, gates_record)


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="run-config YAML")
    ap.add_argument("--phase", type=int, default=2,
                    help="highest phase to run (1-4; 5-8 are manager-gated and "
                         "refused). Phase 3 requires the accepted Phase 1-2 "
                         "evidence; Phase 4 requires the accepted Phase-3 "
                         "complete/ bundle.")
    ap.add_argument("--out", default=None,
                    help="output root (default: config run.output_root)")
    ap.add_argument("--dry-run", action="store_true",
                    help="phase 1: deterministic rebuild verification; "
                         "phase 2: stored-theta objective check (stop after "
                         "Phase 2, no optimizer); phase 3: input-contract "
                         "validation WITHOUT any optimizer call; phase 4: "
                         "bundle/contract validation WITHOUT any gradient or "
                         "Hessian evaluation")
    ap.add_argument("--execute-phase3", action="store_true",
                    help="REQUIRED for a real Phase-3 estimation; without it, "
                         "--phase 3 performs only the non-optimizing dry-run")
    ap.add_argument("--execute-phase4", action="store_true",
                    help="REQUIRED for real Phase-4 curvature diagnostics; "
                         "without it, --phase 4 performs only the "
                         "non-evaluating dry-run (no Hessian)")
    ap.add_argument("--expected-mnl-head", default=None,
                    help="real run: 40-hex SHA the current MNL HEAD must equal")
    ap.add_argument("--expected-dclaborsupply-head", default=None,
                    help="real run: 40-hex SHA the nested HEAD (and MNL gitlink) "
                         "must equal")
    ap.add_argument("--approved-review",
                    default=None,
                    help="real run: must be exactly "
                         "docs/France_case/P2a/"
                         "FR_P2a_region_live_phase3_code_review_v6.md")
    ap.add_argument("--approved-review-sha256", default=None,
                    help="real Phase-3 run: 64-hex SHA-256 of the review-v6 "
                         "file, which must carry one exact "
                         "'**FINAL VERDICT: APPROVE**' line under "
                         "'# 1. Sixth-review verdict'")
    ap.add_argument("--approved-phase4-review", default=None,
                    help="real Phase-4 run: must be exactly "
                         "docs/France_case/P2a/"
                         "FR_P2a_region_live_phase4_code_review_v7.md "
                         "(Phase-4 reviews v1-v6 and the Phase-3 "
                         "review-v6 are rejected)")
    ap.add_argument("--approved-phase4-review-sha256", default=None,
                    help="real Phase-4 run: 64-hex SHA-256 of the Phase-4 "
                         "review-v7 file, which must carry one exact "
                         "'**FINAL VERDICT: APPROVE**' line under "
                         "'# 1. Phase-4 review verdict'")
    args = ap.parse_args(argv)

    if args.phase > 4:
        print("REFUSED: Phases 5-8 are manager-gated; this runner implements "
              "Phases 1-4 only (phase3 acceptance doc s16).", file=sys.stderr)
        return 2

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    if args.phase == 3:
        if Path(args.config).resolve() != CANONICAL_PHASE3_CONFIG.resolve():
            print(f"REFUSED: Phase 3 requires the canonical config "
                  f"{CANONICAL_PHASE3_CONFIG}.", file=sys.stderr)
            return 2
        # Phase 3 consumes the accepted Phase 1-2 evidence READ-ONLY and writes only
        # under phase3_estimation_v1/ -- it never re-runs or rewrites Phases 1-2.
        return run_phase3(args, cfg)

    if args.phase == 4:
        if Path(args.config).resolve() != CANONICAL_PHASE3_CONFIG.resolve():
            print(f"REFUSED: Phase 4 requires the canonical config "
                  f"{CANONICAL_PHASE3_CONFIG}.", file=sys.stderr)
            return 2
        # Phase 4 diagnoses the ACCEPTED immutable Phase-3 bundle READ-ONLY and
        # writes only under phase4_curvature_v1/ -- no optimizer, no theta change.
        return run_phase4(args, cfg)

    out_root = Path(args.out) if args.out else (MNL_ROOT / cfg["run"]["output_root"])
    out = OutRoot(out_root)
    out.root.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    lines: List[str] = []

    def log(msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line)
        lines.append(line)

    manifest: Dict[str, Any] = {
        "run": cfg["run"]["name"],
        "track": cfg["run"]["track"],
        "mode": "dry-run (Phases 1-2)" if args.dry_run else f"phases<={args.phase}",
        "started_at": _utcnow(),
        "status": "RUNNING",
        "stop": None,
        "phases": {},
        "config": {"path": str(Path(args.config)), "sha256": _sha256(Path(args.config))},
        "script": {"path": str(SCRIPT_PATH), "sha256": _sha256(SCRIPT_PATH)},
        "git": {"MNL": _git_state(MNL_ROOT),
                "dclaborsupply-monorepo": _git_state(MNL_ROOT / "dclaborsupply-monorepo")},
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__, "pandas": pd.__version__,
        },
        "targets": cfg["targets"],
    }
    validation: Dict[str, Any] = {"generated_at": _utcnow(), "phase1": {}}
    provenance: Dict[str, Any] = {
        "generated_at": _utcnow(),
        "run": cfg["run"]["name"],
        "binding_documents": [
            "docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md",
            "docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md",
            "docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md",
        ],
        "frozen_reference_notebook":
            "dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb",
        "lineage": {
            "walkthrough_cell": "7c42e9bd (fr_data_walkthrough.ipynb P2a-10)",
            "propagate_regionlive_py": "missing from disk; superseded by this runner",
        },
        "targets": cfg["targets"],
        "input_hashes": {},
        "output_hashes": {},
    }

    def finalize(status: str, stop: Optional[StopRun], code: int) -> int:
        manifest["status"] = status
        if stop is not None:
            manifest["stop"] = {"code": stop.code, "gate": stop.gate,
                                "message": stop.message}
        manifest["finished_at"] = _utcnow()
        manifest["wall_seconds"] = round(time.time() - t0, 1)
        manifest["log"] = lines
        _dump_json(validation, out.path("data_wiring_validation.json"))
        _dump_json(provenance, out.path("provenance.json"))
        _dump_json(manifest, out.path("rebuild_manifest.json"))
        log(f"manifest status: {status}"
            + (f" | stop: {manifest['stop']}" if manifest["stop"] else ""))
        return code

    try:
        _assert_no_prohibited_modules("startup")

        # ---------------- Phase 1 ----------------
        log("Phase 1 - G-0 frozen-inputs gate")
        g0 = gate_g0(cfg, log)
        validation["phase1"]["g0"] = {k: v for k, v in g0.items()
                                      if not k.startswith("_")}
        provenance["input_hashes"] = {
            k: v.get("sha256") for k, v in g0["items"].items()
            if isinstance(v, dict) and v.get("sha256")}
        if not g0["ok"]:
            raise StopRun("S-1", "G-0",
                          "frozen-input gate failed (see data_wiring_validation.json "
                          "g0 items; geometry artifact is the stabilization "
                          "deliverable of fr_singles_pipeline_v2.ipynb)")

        priced: pd.DataFrame = g0["_priced_df"]
        geo: pd.DataFrame = g0["_geometry_df"]

        log("Phase 1 - deterministic pre-assembly (funnel port)")
        raw = pd.read_csv(Path(cfg["frozen_inputs"]["raw_fr_txt"]["path"]), sep="\t")
        raw = _classify_households(raw)
        work, funnel_counts, mutations = _run_funnel(raw, log)
        validation["phase1"]["funnel"] = {
            "households": funnel_counts, "mutations": mutations,
            "expected": cfg["phase1_expected"]["funnel_households"],
            "ok": funnel_counts == {k: int(v) for k, v in
                                    cfg["phase1_expected"]["funnel_households"].items()},
        }
        feats = _build_features(work, log)
        singles_df, singles_dec = _restrict_singles(feats)
        validation["phase1"]["singles_sample"] = {
            "n_hh": int(singles_dec["idhh"].nunique()),
            "n_persons": int(len(singles_df)),
            "ok": (singles_dec["idhh"].nunique() == cfg["phase1_expected"]["n_hh_singles"]
                   and len(singles_df) == cfg["phase1_expected"]["n_persons_singles"]),
        }
        singles_dec = _merge_gsur_pexp(singles_dec, cfg, log)

        region_map, map_checks = _region_map(singles_dec, cfg)
        validation["phase1"]["region_map"] = map_checks
        p_map = out.path("region_map_p2a_singles2016.parquet")
        region_map.to_parquet(p_map)
        provenance["output_hashes"]["region_map_p2a_singles2016.parquet"] = _sha256(p_map)

        trait, takeup_ev = _takeup_traits(priced, singles_dec, cfg, log)
        validation["phase1"]["takeup"] = takeup_ev

        log("Phase 1 - assemble_singles -> revival -> band overwrite -> er_b")
        er_b, asm_ev = _assemble_er_b(geo, priced, trait, singles_df, singles_dec,
                                      region_map, cfg, log)
        validation["phase1"]["assembly"] = asm_ev

        log("Phase 1 - freeze + frame reconciliation")
        rec, stem_hashes = _freeze_and_reconcile(er_b, region_map, out, cfg, log)
        validation["phase1"]["reconciliation"] = rec
        provenance["output_hashes"].update(stem_hashes)

        phase1_ok = (validation["phase1"]["funnel"]["ok"]
                     and validation["phase1"]["singles_sample"]["ok"]
                     and map_checks["ok"] and takeup_ev["ok"]
                     and asm_ev["ok"] and rec["ok"])
        validation["phase1"]["ok"] = phase1_ok
        manifest["phases"]["phase1"] = "PASS" if phase1_ok else "FAIL"
        if not phase1_ok:
            raise StopRun("S-1", "G-18",
                          "Phase-1 data-wiring gate failed (see data_wiring_validation.json)")
        log("Phase 1 COMPLETE")
        if args.phase == 1:
            _assert_no_prohibited_modules("end")
            return finalize("PHASE_1_COMPLETE", None, 0)

        # ---------------- Phase 2 ----------------
        log("Phase 2 - package load + stored-theta objective reproduction (no optimizer)")
        rep = phase2(out, cfg, log)
        _dump_json(rep, out.path("dry_run_report.json"))
        provenance["output_hashes"]["dry_run_report.json"] = _sha256(
            out.path("dry_run_report.json"))
        manifest["phases"]["phase2"] = "PASS" if rep["ok"] else "FAIL"
        if not rep["ok"]:
            raise StopRun("S-9", "G-19",
                          "Phase-2 dry-run verification failed (see dry_run_report.json)")
        log("Phase 2 COMPLETE - dry-run stops here by design (plan v2 s24 step 4)")
        _assert_no_prohibited_modules("end")
        return finalize("DRY_RUN_PHASES_1_2_COMPLETE", None, 0)

    except StopRun as stop:
        log(f"STOP {stop.code} [{stop.gate}] {stop.message}")
        return finalize("STOPPED", stop, 2)
    except Exception:
        tb = traceback.format_exc()
        log("UNEXPECTED ERROR:\n" + tb)
        stop = StopRun("S-0", "unexpected", tb.splitlines()[-1] if tb else "unknown")
        return finalize("STOPPED", stop, 3)


if __name__ == "__main__":
    sys.exit(main())
