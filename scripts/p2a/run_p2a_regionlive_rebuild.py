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

HARD REFUSALS (S-0, asserted in code, not just documented):
  - no EUROMOD (no import, no connection, no pricing run)
  - no draw generation/regeneration (no hours_mixture_d1 / occ_draw_empirical /
    pilot_wage_draw / build_bpool_singles import; geometry is a frozen input)
  - no optimizer (scipy.optimize is never imported in Phases 1-2)
  - no notebook I/O; no write outside region_live_v1/
Phases 3-8 are manager-gated: this runner refuses --phase > 2.

Exit codes: 0 = phases completed; 2 = pre-registered stop (STOPPED manifest);
3 = unexpected error (STOPPED manifest, stop code S-0/unexpected).
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

# modules whose presence in sys.modules is an S-0 prohibited-operation stop
_PROHIBITED_MODULES = (
    "dclaborsupply_app.euromod",     # EUROMOD connector / pricing runner
    "hours_mixture_d1",              # draw generation
    "occ_draw_empirical",            # draw generation
    "pilot_wage_draw",               # draw generation
    "build_bpool_singles",           # draw generation
    "scipy.optimize",                # optimizer (Phases 1-2 must not optimize)
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
# orchestration
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="run-config YAML")
    ap.add_argument("--phase", type=int, default=2,
                    help="highest phase to run (1 or 2; 3-8 are manager-gated)")
    ap.add_argument("--out", default=None,
                    help="output root (default: config run.output_root)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Phases 1-2 verification only (mandatory stop after Phase 2)")
    args = ap.parse_args(argv)

    if args.phase > 2:
        print("REFUSED: Phases 3-8 are manager-gated; this runner implements "
              "Phases 1-2 only (plan v2 s24; decisions v2 D-1).", file=sys.stderr)
        return 2

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
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
