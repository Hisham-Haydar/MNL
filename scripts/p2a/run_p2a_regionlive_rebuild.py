#!/usr/bin/env python
"""FR P2a region-live production rebuild — Phases 1-2 runner.

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
Phases 4-8 are manager-gated: this runner refuses --phase > 3.

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
# external execution authorization (decision B): created only after third-review APPROVE
AUTH_SCHEMA = "p2a_phase3_execution_authorization_v1"
AUTH_REQUIRED_FIELDS = (
    "schema", "status", "approved_mnl_commit", "approved_dclaborsupply_commit",
    "approved_runner_sha256", "approved_config_sha256", "approved_test_sha256",
    "approved_review_path", "approved_review_sha256", "created_at_utc")
SAFETY_TESTS_PATH = MNL_ROOT / "tests/p2a/test_p2a_regionlive_phase3_safety.py"
# the successful-bundle artifact set; the manifest is written LAST and is NEVER
# part of its own artifact-hash dictionary (decision C / review fix 7)
PHASE3_ARTIFACTS = ("phase3_console.log", "theta_estimated.csv",
                    "optimizer_diagnostics.json", "estimation_results.json")

# modules whose presence in sys.modules is an S-0 prohibited-operation stop
_PROHIBITED_MODULES = (
    "dclaborsupply_app.euromod",     # EUROMOD connector / pricing runner
    "hours_mixture_d1",              # draw generation
    "occ_draw_empirical",            # draw generation
    "pilot_wage_draw",               # draw generation
    "build_bpool_singles",           # draw generation
)
# the optimizer is additionally prohibited everywhere EXCEPT the real Phase-3
# estimation call (Phases 1-2 and every --dry-run must never optimize)
_OPTIMIZER_MODULE = "scipy.optimize"

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


def _assert_no_prohibited_modules(where: str, *, allow_optimizer: bool = False) -> None:
    banned = _PROHIBITED_MODULES if allow_optimizer \
        else (_PROHIBITED_MODULES + (_OPTIMIZER_MODULE,))
    hits = [m for m in sys.modules
            for p in banned if m == p or m.startswith(p + ".")]
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


def _git_tracked_dirty(repo: Path) -> Optional[bool]:
    try:
        r = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "-uno"],
                           capture_output=True, text=True, timeout=15)
        return bool(r.stdout.strip()) if r.returncode == 0 else None
    except Exception:
        return None


def _verify_external_authorization(auth_path: Optional[str],
                                   config_path: Path) -> Dict[str, Any]:
    """External execution-authorization contract for REAL Phase 3 (decision B)."""
    if not auth_path:
        raise StopRun("S-0", "authorization",
                      "real Phase-3 execution requires --authorization "
                      "<absolute-json-path> (created only after third-review APPROVE)")
    p = Path(auth_path)
    if not p.is_absolute():
        raise StopRun("S-0", "authorization", "authorization path must be absolute")
    if not p.is_file():
        raise StopRun("S-0", "authorization", f"authorization file not found: {p}")
    a = json.loads(p.read_text(encoding="utf-8"))
    missing = [f for f in AUTH_REQUIRED_FIELDS if f not in a]
    if missing:
        raise StopRun("S-0", "authorization", f"missing fields: {missing}")
    if a["schema"] != AUTH_SCHEMA or a["status"] != "APPROVED":
        raise StopRun("S-0", "authorization", "schema/status mismatch")
    import re as _re
    hex40 = _re.compile(r"^[0-9a-f]{40}$")
    hex64 = _re.compile(r"^[0-9a-f]{64}$")
    if not (hex40.match(a["approved_mnl_commit"])
            and hex40.match(a["approved_dclaborsupply_commit"])):
        raise StopRun("S-0", "authorization", "commit SHA format invalid")
    for f in ("approved_runner_sha256", "approved_config_sha256",
              "approved_test_sha256", "approved_review_sha256"):
        if not hex64.match(a[f]):
            raise StopRun("S-0", "authorization", f"{f} format invalid")
    head = _git_head_full(MNL_ROOT)
    if head != a["approved_mnl_commit"]:
        raise StopRun("S-0", "authorization",
                      f"MNL HEAD {head} != approved {a['approved_mnl_commit']}")
    if _git_tracked_dirty(MNL_ROOT) is not False:
        raise StopRun("S-0", "authorization", "MNL tracked tree is not clean")
    if _sha256(SCRIPT_PATH) != a["approved_runner_sha256"]:
        raise StopRun("S-0", "authorization", "runner hash != approved")
    if _sha256(Path(config_path)) != a["approved_config_sha256"]:
        raise StopRun("S-0", "authorization", "config hash != approved")
    if _sha256(SAFETY_TESTS_PATH) != a["approved_test_sha256"]:
        raise StopRun("S-0", "authorization", "safety-test hash != approved")
    review = MNL_ROOT / a["approved_review_path"]
    if not review.is_file() or _sha256(review) != a["approved_review_sha256"]:
        raise StopRun("S-0", "authorization", "approved review missing or hash mismatch")
    head_text = review.read_text(encoding="utf-8")[:1000]
    if "APPROVE" not in head_text or "REJECT" in head_text:
        raise StopRun("S-0", "authorization", "approved review verdict is not APPROVE")
    return {"authorization_path": str(p), "verified": True,
            **{k: a[k] for k in AUTH_REQUIRED_FIELDS}}


def _verify_package_identity(expected_commit: Optional[str] = None) -> Dict[str, Any]:
    """dclaborsupply source-identity verification (decision D)."""
    import dclaborsupply.spec.parser as _sp
    import dclaborsupply.data.loader as _dl
    import dclaborsupply.likelihood.engine_jax as _ej
    nested = (MNL_ROOT / "dclaborsupply-monorepo").resolve()
    head = _git_head_full(nested)
    dirty = _git_tracked_dirty(nested)
    gitlink = None
    try:
        r = subprocess.run(["git", "-C", str(MNL_ROOT), "ls-tree", "HEAD",
                            "dclaborsupply-monorepo"],
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            gitlink = r.stdout.split()[2]
    except Exception:
        pass
    mods = {m.__name__: str(Path(m.__file__).resolve()) for m in (_sp, _dl, _ej)}
    module_path_ok = all(str(nested) in mp for mp in mods.values())
    rec = {"nested_repo": str(nested), "nested_head": head, "gitlink": gitlink,
           "tracked_dirty": dirty, "imported_modules": mods,
           "module_path_ok": module_path_ok,
           "expected_commit": expected_commit}
    ok = (nested.is_dir() and module_path_ok and dirty is False
          and gitlink is not None and gitlink == head)
    if expected_commit is not None:
        ok = ok and (head == expected_commit)
    rec["package_identity_ok"] = bool(ok)
    if not ok:
        raise StopRun("S-0", "package-identity",
                      f"dclaborsupply source identity failed: {rec}")
    return rec


def _bundle_hashes(staging: Path) -> Tuple[Dict[str, str], str]:
    """SHA-256 per artifact (manifest NEVER included) + deterministic bundle hash."""
    hashes = {n: _sha256(staging / n) for n in PHASE3_ARTIFACTS
              if (staging / n).is_file()}
    joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
    return hashes, hashlib.sha256(joined.encode("utf-8")).hexdigest()


class Phase3Transaction:
    """Lock + staging/attempts/complete result-directory transaction (decision B)."""

    def __init__(self, root: Path, label: str):
        self.root = Path(root)
        self.lock = self.root / ".phase3.lock"
        self.staging_base = self.root / ".staging"
        self.attempts = self.root / "attempts"
        self.complete = self.root / "complete"
        # pid + nanosecond suffix: unique even for same-second attempts in one process
        self.attempt_id = (f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
                           f"_{os.getpid()}_{time.time_ns() % 1_000_000:06d}_{label}")
        self.staging = self.staging_base / self.attempt_id
        self._locked = False

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
                       "attempt": self.attempt_id}, f)
        self._locked = True
        self.attempts.mkdir(exist_ok=True)
        self.migrate_pre_review_evidence()      # under the lock (decision H)
        self.staging_base.mkdir(exist_ok=True)
        self.staging.mkdir(parents=True)

    def complete_exists(self) -> bool:
        return self.complete.exists()

    def finish(self, status: str) -> Path:
        """Atomic directory-level publication: complete/ on success, attempts/ otherwise.
        A failed/repeated run can never overwrite or mutate a prior successful bundle."""
        if status == "PHASE_3_COMPLETE":
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
        return gates, rows, str(g3["target_mismatch_status"]), None
    return gates, rows, "PHASE_3_COMPLETE", None


def _phase3_contract(out: OutRoot, cfg: Dict[str, Any], config_path: Path,
                     log) -> Dict[str, Any]:
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
    ev["input_authentication"] = _authenticate_inputs(cfg)

    # Phase 1-2 manifest: status + accepted script/config anchors
    man12 = json.loads(out.path("rebuild_manifest.json").read_text(encoding="utf-8"))
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
    spec = EstimationSpec.from_yaml(str(MNL_ROOT / cfg["certified_spec"]["yaml"]))
    names = list(spec.all_param_names)
    accepted_dr = json.loads(out.path("dry_run_report.json").read_text(encoding="utf-8"))
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
    meta = json.loads(out.path(f"{stem}__mnlmeta.json").read_text(encoding="utf-8"))
    norm = meta["normalization"]["singles"]
    if not (int(norm["n_chosen"]) == int(acc["n_hh"])
            and int(meta["row_counts"]["singles"]) == int(acc["n_hh"]) * int(acc["n_alts"])):
        raise StopRun("S-1", "phase3-contract", "mnlmeta metadata != accepted structure")
    ev["mnlmeta"] = {"c_scale": float(norm["c_scale"]), "l_scale": float(norm["l_scale"]),
                     "n_chosen": int(norm["n_chosen"])}

    # explicit 37<->47 parameter map (decision D)
    raw_theta = load_custom_initial_values(MNL_ROOT / cfg["warm_start"]["theta_csv"])
    theta_warm = np.array([float(raw_theta[n]) for n in names], dtype="float64")
    name_idx = {n: i for i, n in enumerate(names)}
    pinned_at = {p: float(theta_warm[name_idx[p]]) for p in cfg_pins}
    pmap = build_phase3_parameter_map(names, cfg_pins, pinned_at)
    bounds_full = list(spec.get_bounds_tuple())
    bounds_free = [bounds_full[i] for i in pmap["free_idx"]]

    # start vector (accepted stored region-live theta) + exact round trips (D.8)
    st_tab = pd.read_csv(MNL_ROOT / p3["start_theta"]["csv"]).set_index("param")
    if list(st_tab.index) != names:
        raise StopRun("S-1", "phase3-contract", "start-theta CSV ordering mismatch")
    theta_trial = st_tab[p3["start_theta"]["column"]].astype(float).reindex(names).to_numpy()
    ev["start_theta_raw_sha256"] = _theta_sha(theta_trial)
    if ev["start_theta_raw_sha256"] != acc["theta_star_sha256"]:
        raise StopRun("S-8", "phase3-contract", "stored theta vector hash != accepted")
    free_start = project_full_to_free(pmap, theta_trial)
    theta_start_full = expand_free_to_full(pmap, free_start)
    rt = {
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
    if not all(rt.values()):
        raise StopRun("S-1", "param-map", f"round-trip validation failed: {rt}")
    ev["parameter_map"] = {
        "all_names": pmap["all_names"], "free_names": pmap["free_names"],
        "pin_names": pmap["pin_names"],
        "free_indices": [int(i) for i in pmap["free_idx"]],
        "pin_indices": [int(i) for i in pmap["pin_idx"]],
        "pin_values": {p: float(v) for p, v in zip(pmap["pin_names"],
                                                   pmap["pin_values"])},
        "round_trips": rt,
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
    er = pd.read_parquet(out.path(f"{stem}__singles.parquet"))
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
    if ev["negll_start_abs_dev"] > float(g3["pre_opt_objective_tol"]):
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
            "input_auth": ev["input_authentication"]}


def _phase3_estimate(ctx: Dict[str, Any], staging: Path, cfg: Dict[str, Any], log,
                     minimize_fn=None, mark_optimizer_called=None
                     ) -> Tuple[str, Dict[str, Any]]:
    """Real Phase-3 estimation over the ordered 37-free vector (decision D), with
    post-optimization input recheck (G), gate battery (F), and atomic staged artifact
    emission (C). `minimize_fn` injection exists for unit tests ONLY; the production
    path imports scipy here and nowhere else."""
    import jax
    import jax.numpy as jnp
    if minimize_fn is None:
        from scipy.optimize import minimize as minimize_fn   # real Phase 3 only

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
        recheck_x, recheck_x_ok = _recheck_inputs(ctx["input_auth"])
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

    # post-optimization input recheck BEFORE any result write (decision G / S-8)
    recheck, recheck_ok = _recheck_inputs(ctx["input_auth"])
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


def run_phase3(args, cfg: Dict[str, Any], *, _contract_fn=None, _estimate_fn=None,
               _txn_root=None, _minimize_fn=None, _package_identity_fn=None) -> int:
    """Phase-3 orchestration under the lock/staging/attempts/complete transaction.

    The PRODUCTION CLI path (main -> run_phase3 with no underscore kwargs) enforces the
    canonical roots exactly and offers no test-root override. The underscore kwargs are
    pure internal seams for non-optimizing unit tests only."""
    production = _txn_root is None
    if production:
        out_resolved = (Path(args.out).resolve() if args.out
                        else (MNL_ROOT / cfg["run"]["output_root"]).resolve())
        canonical = CANONICAL_REGIONLIVE_ROOT.resolve()
        if out_resolved != canonical:
            print(f"REFUSED: Phase-3 --out must equal the canonical production root "
                  f"{canonical} (got {out_resolved}); no test-root override exists.",
                  file=sys.stderr)
            return 2
        if (MNL_ROOT / cfg["run"]["output_root"]).resolve() != canonical:
            print("REFUSED: config run.output_root is not the canonical production root.",
                  file=sys.stderr)
            return 2
        if cfg["phase3"]["output_subdir"] != CANONICAL_PHASE3_SUBDIR:
            print(f"REFUSED: config phase3.output_subdir must equal "
                  f"'{CANONICAL_PHASE3_SUBDIR}'.", file=sys.stderr)
            return 2
        txn_root = CANONICAL_PHASE3_ROOT
        out = OutRoot(CANONICAL_REGIONLIVE_ROOT)
    else:
        txn_root = Path(_txn_root)
        out = OutRoot(txn_root.parent)

    contract_fn = _contract_fn if _contract_fn is not None else _phase3_contract
    estimate_fn = _estimate_fn if _estimate_fn is not None else _phase3_estimate
    identity_fn = (_package_identity_fn if _package_identity_fn is not None
                   else _verify_package_identity)
    # decision B: real execution requires FULL external authorization BEFORE the lock
    auth_arg = getattr(args, "authorization", None)
    auth_record: Dict[str, Any] = {}
    if production and not args.dry_run:
        # decision B: PRODUCTION real runs verify the external authorization BEFORE
        # the lock; unit-test seams (non-production roots) simulate post-auth flows
        auth_record = _verify_external_authorization(auth_arg, Path(args.config))
    txn = Phase3Transaction(txn_root, "dryrun" if args.dry_run else "estimate")

    t0 = time.time()
    lines: List[str] = []

    def log(msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line)
        lines.append(line)

    manifest: Dict[str, Any] = {
        "run": cfg["run"]["name"] + "__phase3",
        "track": cfg["run"]["track"],
        "attempt_id": txn.attempt_id,
        "mode": ("phase3 dry-run (contract only, no optimizer)" if args.dry_run
                 else "phase3 estimation"),
        "authorization": cfg["phase3"]["authorization_doc"],
        "authorization_status": ("EXTERNALLY_AUTHORIZED" if auth_record.get("verified")
                                 else "AWAITING_POST_REVIEW_AUTHORIZATION"),
        "execution_authorization": auth_record or None,
        "execution_ready": bool(auth_record.get("verified", False)),
        "started_at": _utcnow(),
        "status": "RUNNING",
        "stop": None,
        "optimizer_called": False,
        "config": {"path": str(Path(args.config)), "sha256": _sha256(Path(args.config))},
        "script": {"path": str(SCRIPT_PATH), "sha256": _sha256(SCRIPT_PATH)},
        "git": {"MNL": _git_state(MNL_ROOT),
                "dclaborsupply-monorepo": _git_state(MNL_ROOT / "dclaborsupply-monorepo")},
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__, "pandas": pd.__version__},
        "targets": cfg["targets"],
    }

    def finalize(status: str, stop: Optional[StopRun], code: int) -> int:
        # decision C order: final status line -> console -> hashes -> manifest LAST ->
        # atomic directory publication; the manifest is never self-hashed.
        if status == "PHASE_3_COMPLETE" and txn.complete_exists():
            stop = StopRun("S-0", "phase3-immutable",
                           "complete/ appeared during the run; publish refused")
            status, code = "STOPPED", 2
        if status == "PHASE_3_COMPLETE":
            # decision F: the successful bundle must contain EXACTLY the required
            # non-manifest artifacts (the console is written by finalize itself just
            # below; the post-manifest check then enforces the exact final 5-set)
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

    acquired = False
    try:
        txn.acquire()
        acquired = True
        _assert_no_prohibited_modules("phase3-start")
        manifest["package_identity"] = identity_fn(
            expected_commit=auth_record.get("approved_dclaborsupply_commit"))
        if (not args.dry_run) and txn.complete_exists():
            raise StopRun("S-0", "phase3-immutable",
                          "complete/ exists; a successful Phase-3 bundle is immutable "
                          "and a new real estimation is refused (decision B.3)")
        log("Phase 3 - input contract (accepted Phase 1-2 evidence)")
        ctx = contract_fn(out, cfg, Path(args.config), log)
        manifest["contract"] = ctx["ev"]

        if args.dry_run:
            _assert_no_prohibited_modules("phase3-dryrun-end")   # STILL no optimizer
            log("Phase 3 dry-run COMPLETE - contract verified, optimizer NOT called")
            return finalize("PHASE_3_DRY_RUN_COMPLETE", None, 0)

        log("Phase 3 - estimation (real run)")

        def _mark_called() -> None:
            manifest["optimizer_called"] = True     # decision G: before invocation

        status, diag = estimate_fn(ctx, txn.staging, cfg, log,
                                   minimize_fn=_minimize_fn,
                                   mark_optimizer_called=_mark_called)
        manifest["gates"] = diag.get("gates", {})
        manifest["input_recheck_after_optimization"] = diag.get(
            "input_recheck_after_optimization", {})
        _assert_no_prohibited_modules("phase3-end", allow_optimizer=True)
        if status == "PHASE_3_COMPLETE":
            return finalize(status, None, 0)
        if status == "STOPPED":
            s = diag.get("stop") or {}
            return finalize("STOPPED",
                            StopRun(s.get("code", "S-3"), s.get("gate", "phase3"),
                                    s.get("message", "gate failure")), 2)
        return finalize(status, None, 4)    # REVIEW_REQUIRED_TARGET_MISMATCH

    except StopRun as stop:
        log(f"STOP {stop.code} [{stop.gate}] {stop.message}")
        if not acquired:
            print(f"[phase3] STOPPED (no attempt bundle: {stop.message})",
                  file=sys.stderr)
            return 2
        return finalize("STOPPED", stop, 2)
    except Exception:
        tb = traceback.format_exc()
        log("UNEXPECTED ERROR:\n" + tb)
        if not acquired:
            print(tb, file=sys.stderr)
            return 3
        stop = StopRun("S-0", "unexpected", tb.splitlines()[-1] if tb else "unknown")
        return finalize("STOPPED", stop, 3)

# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="run-config YAML")
    ap.add_argument("--phase", type=int, default=2,
                    help="highest phase to run (1, 2 or 3; 4-8 are manager-gated). "
                         "Phase 3 requires the accepted Phase 1-2 evidence in --out.")
    ap.add_argument("--out", default=None,
                    help="output root (default: config run.output_root)")
    ap.add_argument("--dry-run", action="store_true",
                    help="phases 1-2: verification only (stop after Phase 2); "
                         "phase 3: input-contract validation WITHOUT any optimizer call")
    ap.add_argument("--authorization", default=None,
                    help="REAL Phase 3 only: absolute path to the external "
                         "p2a_phase3_execution_authorization_v1 JSON (created only "
                         "after third-review APPROVE); dry-runs run without it")
    args = ap.parse_args(argv)

    if args.phase > 3:
        print("REFUSED: Phases 4-8 are manager-gated; this runner implements "
              "Phases 1-3 only (plan v2 s24; acceptance doc s10).", file=sys.stderr)
        return 2

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    if args.phase == 3:
        # Phase 3 consumes the accepted Phase 1-2 evidence READ-ONLY and writes only
        # under phase3_estimation_v1/ -- it never re-runs or rewrites Phases 1-2.
        return run_phase3(args, cfg)

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
