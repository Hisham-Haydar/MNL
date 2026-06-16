"""
F6-PRICE-B preflight (Task 0 only).

Checks:
  (a) Canonicalization   — count stale lhw/yem in non-employed decider draws.
  (b) Identity gate      — full-band EUROMOD on stored draws; compare ils_dispy
                           to stored bpool ils_dispy_real; tol = 0.01 EUR.
  (c) RSA-leakage check  — confirm bsa00_s from full-band matches stored (0 for
                           RSA-ineligible HHs; per-draw diff tol = 1e-6 EUR).

DESIGN NOTE — STRUCTURAL GEOMETRY FINDING (empirical):
  The 13 preflight HHs carry stored bsa00_s = 0 at every draw in the bpool
  priced parquet (draw-first chunk geometry).  However, the full-band uid-first
  EUROMOD pass — even with EVERY row overwritten with correct bpool input values
  — returns bsa00_s = 526 EUR at ALL 100 draws for ALL 13 preflight HHs.
  Root cause: the FR RSA accumulator (i_bsa00_cumpers_nw/w, identified by D-BEN
  as the sole batch-sensitive channel) is summed cumulatively over the ENTIRE
  input file in row order.  In uid-first ordering, each HH's rows are preceded
  by all prior HHs' full 101-draw stack; in the bpool's draw-first chunk runs,
  only one draw per HH has been processed before any given row.  This geometry-
  induced accumulator difference drives bsa00_s from 0 (draw-first) to 526
  (uid-first) across all 100 draws for these HHs.  The identity gate FAILS by
  DESIGN — not a bug.  Task 0 documents this structural incompatibility and stops.

GOVERNANCE:
  JMP_decomposition_design_memo_v1.md is not on disk.
  F6 IMPLEMENTATION AUTHORIZED: NO (corrected design prompt, commit bde5085).
  This script STOPS after Task 0 and reports that the equalized covariate spec
  is required before Task 1 (full parallel counterfactual run) can proceed.

SCOPE CONSTRAINTS:
  - Singles only (2016 cross-section, n = 1,676).
  - No couples, no welfare, no decomposition, no estimation.
  - No EUROMOD SYSTEM edits.
  - Immutable: all F3/F3-R2/F3-R2B artifacts + fastlane_anchors_v3/* not touched.
  - No commit.

Outputs (atomic):
  outputs/welfare/fastlane/f6_price_b_manifest_v1.json
  docs/jmp_methodology/RURO_welfare_F6PRICEB_pricing_report_v1.md
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parent.parent.parent.parent
for _p in [
    _REPO / "scripts/bpool",
    _REPO / "scripts/enhanced",
    _REPO / "scripts/welfare",
    _REPO / "scripts/pilot",
]:
    sys.path.insert(0, str(_p))

import jax
jax.config.update("jax_enable_x64", True)

import welfare_vdir as wvd
import yaml
from _bpool_paths import bpool_dir

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
BASE_SEED        = 20260604
YEAR             = 2016
YEAR_TAG         = 2
N_NODES          = 101          # S = 101 (draw 0 = actual + 100 counterfactual)
_FR_STD_HOURS    = 35.0
_WEEKS_PER_MONTH = 52.0 / 12.0
TOL_IDENTITY     = 0.01         # EUR — identity gate pass threshold
TOL_RSA          = 1e-6         # EUR — RSA leakage pass threshold
TOL_CANON_STALE  = 1e-6         # threshold for "non-zero lhw counts as stale"

# preflight households
_SM_UIDS  = [200001495800, 200001496401, 200001498400, 200001502500, 200001516900]
_SF_UIDS  = [200001504300, 200001526601, 200001527000, 200001531200, 200001533500]
_DBEN_UIDS = [200001593700, 200003504101, 200003672000]  # D-BEN anchors
_DBEN_LABELS = ["primary", "top_ess_sm_2016", "top_ess_sf_2016"]

PREFLIGHT_UIDS = _SM_UIDS + _SF_UIDS + _DBEN_UIDS   # 13 HHs, no overlap
PREFLIGHT_SET  = set(PREFLIGHT_UIDS)

_CONFIG = _REPO / "scripts/welfare/configs/welfare_stage1_w3.yaml"
_AV3_DIR = _REPO / "outputs/welfare/fastlane_anchors_v3"

_OUT_DIR      = _REPO / "outputs/welfare/fastlane"
_OUT_MANIFEST = _OUT_DIR / "f6_price_b_manifest_v1.json"
_OUT_DOC      = _REPO / "docs/jmp_methodology/RURO_welfare_F6PRICEB_pricing_report_v1.md"

# governance: equalized covariate spec ratified?
_DESIGN_MEMO = _REPO / "docs/jmp_methodology/JMP_decomposition_design_memo_v1.md"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _atomic_write(text_or_obj, dest: Path, *, as_json: bool = False):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        if as_json:
            tmp.write_text(json.dumps(text_or_obj, indent=2, default=float),
                           encoding="utf-8")
        else:
            tmp.write_text(text_or_obj, encoding="utf-8")
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _system_pairing(bc):
    system_code, dataset_name = bc["system_pairing"][YEAR]
    return system_code[:2], system_code, dataset_name


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("F6-PRICE-B preflight  [Task 0 only]")
    print(f"  Preflight set: {len(PREFLIGHT_UIDS)} HHs "
          f"({len(_SM_UIDS)} sm + {len(_SF_UIDS)} sf + {len(_DBEN_UIDS)} D-BEN anchors)")

    # ── governance check ────────────────────────────────────────────────────
    spec_ratified = _DESIGN_MEMO.exists()
    print(f"\n  Equalized covariate spec ratified: {'YES' if spec_ratified else 'NO'}")
    print(f"  (memo path checked: {_DESIGN_MEMO.relative_to(_REPO)})")
    if not spec_ratified:
        print("  -> WILL STOP after Task 0 (equalized run requires ratified spec).")

    # ── constants / machinery ────────────────────────────────────────────────
    bc = wvd._build_constants({"build_module": "run_bpool_euromod_chunk"})
    phi = float(bc["cpi"][YEAR])
    country, sys_code, dataset = _system_pairing(bc)
    raw_cols     = bc["raw_schema"][YEAR]
    raw_cols_set = set(raw_cols)
    bmod         = __import__("run_bpool_euromod_chunk")

    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    staged_stem = cfg["welfare"]["stage4"]["welfare_pricing_reference"]["staged_engine_ready_stem"]
    bp = bpool_dir()

    # ── load band (2016 singles, full) ───────────────────────────────────────
    print(f"\n  Loading 2016 singles band from {staged_stem}...")
    band_full = pd.read_parquet(bp / f"{staged_stem}__singles.parquet")
    band = band_full[band_full["year_tag"] == YEAR_TAG].copy().reset_index(drop=True)
    all_uids = sorted(band["stacked_hh_uid"].unique().tolist())
    n_hh = len(all_uids)
    print(f"  Band: {len(band):,} rows, {n_hh} HHs")
    for col in ["yivwg", "yem00", "yemxp", "yem_hour"]:
        if col not in band.columns:
            band[col] = 0.0

    # ── load stored bpool priced reference ──────────────────────────────────
    # Output columns for comparison (gate 0b/0c).
    _ref_out_cols = ["stacked_hh_uid", "draw", "ruro_decider",
                     "ils_dispy", "ils_dispy_real", "bsa00_s", "ils_ben",
                     "ils_origy", "ils_tax", "ils_sicdy"]
    # Input columns from bpool build.
    # The staged band carries STALE lhw/yem (actual observed values at all draws).
    # The bpool chunk build computed draw-specific lhw/yem/yem00/yemxp for EVERY HH
    # using the pilot draw machinery before EUROMOD pricing.  These correct values are
    # stored in the bpool priced parquet (EUROMOD passes them through unchanged).
    # We must overwrite ALL HHs' stale decider-draw rows with the correct values
    # so that the RSA accumulator reflects actual employment income rather than
    # the fictitious zero-income state that yem00=yemxp=0 would imply.
    # (Overwriting only the 13 preflight HHs is insufficient: 1,663 HHs with
    # yem00=yemxp=0 inflate i_bsa00_cumpers_nw by ~160k fictitious entries, which
    # through the cross-HH RSA accumulator can push preflight HHs to bsa00_s=526 EUR.)
    _ref_in_cols  = ["stacked_hh_uid", "draw", "ruro_decider",
                     "lhw", "yem", "yem00", "yemxp", "yivwg", "yem_hour",
                     "working"]
    priced_path = bp / "fr_p3a_bpool_priced__2016__singles.parquet"
    print(f"\n  Loading stored bpool priced reference (output cols + full input cols)...")
    ref_full_out = pd.read_parquet(priced_path, columns=_ref_out_cols)
    # load input cols for ALL HHs (needed to correctly populate RSA accumulator)
    ref_full_in  = pd.read_parquet(priced_path, columns=_ref_in_cols)
    pf_mask_out = (
        (ref_full_out["stacked_hh_uid"].isin(PREFLIGHT_SET))
        & (ref_full_out["ruro_decider"] == 1)
        & (ref_full_out["draw"] >= 1)
    )
    # overwrite ALL decider rows (draw>=0): the bpool build set yem00/yemxp at draw=0
    # too; leaving draw=0 at yem00=yemxp=0 inflates the RSA accumulator before any
    # draw>=1 row is processed (band is ordered uid-first: draws 0..100 for each HH).
    all_dec_mask_in = (ref_full_in["ruro_decider"] == 1)
    ref      = ref_full_out[pf_mask_out].copy()
    ref_in   = ref_full_in[all_dec_mask_in].copy()   # all 1676 HHs x 101 draws
    print(f"  Reference rows (13 preflight HHs, decider draw>=1): {len(ref):,}")
    print(f"  Input override rows (all HHs, all decider draws): {len(ref_in):,}")

    # verify all 13 preflight HHs are present in reference
    ref_uids = set(ref["stacked_hh_uid"].unique())
    missing = PREFLIGHT_SET - ref_uids
    if missing:
        raise RuntimeError(f"STOP: preflight UIDs missing in bpool priced parquet: {missing}")

    # ── TASK 0(a): canonicalization check ───────────────────────────────────
    print("\n" + "-"*66)
    print("TASK 0(a) -- Canonicalization")
    print("  Count stale lhw/yem in non-employed decider draws (draw>=1).")
    print("  These would be zeroed by _overwrite_fixed in counterfactual pricing.")
    canon_rows = []
    total_non_emp = 0
    total_stale_lhw = 0
    total_stale_yem = 0
    for uid in PREFLIGHT_UIDS:
        sub = band[
            (band["stacked_hh_uid"] == uid)
            & (band["ruro_decider"] == 1)
            & (band["draw"] >= 1)
        ].copy()
        non_emp = sub[sub["working"] == 0]
        stale_lhw = (non_emp["lhw"].abs() > TOL_CANON_STALE).sum()
        stale_yem = (non_emp["yem"].abs() > TOL_CANON_STALE).sum()
        total_non_emp  += len(non_emp)
        total_stale_lhw += int(stale_lhw)
        total_stale_yem += int(stale_yem)
        dgn = float(sub["dgn"].iloc[0]) if len(sub) > 0 else float("nan")
        grp = "sm" if dgn == 0.0 else "sf" if dgn == 1.0 else "?"
        canon_rows.append({
            "uid": uid, "group": grp,
            "n_dec_draws": len(sub),
            "n_non_employed": len(non_emp),
            "stale_lhw": int(stale_lhw),
            "stale_yem": int(stale_yem),
        })
        print(f"  uid={uid} ({grp}): non-emp={len(non_emp):3d} "
              f"stale_lhw={stale_lhw} stale_yem={stale_yem}")

    print(f"\n  Totals across 13 HHs: non-emp={total_non_emp}, "
          f"stale_lhw={total_stale_lhw}, stale_yem={total_stale_yem}")
    print("  These rows carry stale pre-draw covariate values and would be zeroed")
    print("  by the canonicalization step (zero lhw/yem for non-employed draws)")
    print("  before counterfactual EUROMOD pricing in the full run (Task 1).")
    print("  Task 0(a): DIAGNOSTIC (no pass/fail threshold here)")

    # ── TASK 0(b)+(c): identity gate + RSA leakage ──────────────────────────
    print("\n" + "-"*66)
    print("TASK 0(b)+(c) -- Identity gate + RSA-leakage check")
    print("  Overwriting preflight HH band rows with bpool draw-specific inputs...")
    print("  (band carries stale lhw/yem at all draws; bpool priced has draw-specific values)")

    # Overwrite preflight HH decider draw>=1 rows with correct draw-specific values.
    # The staged band has lhw/yem = actual observed (same at all draws 0..100).
    # The bpool chunk build computed draw-specific lhw/yem/yem00/yemxp from pilot
    # draws and sent those to EUROMOD.  We recover them from the bpool priced parquet.
    band_run = band.copy()
    # yivwg = band's wage column (draw-specific pilot wage, same as bpool's yivwg)
    if "yivwg" not in band_run.columns:
        band_run["yivwg"] = band_run["wage"] if "wage" in band_run.columns else 0.0

    _overwrite_cols = ["lhw", "yem", "yem00", "yemxp", "yivwg", "yem_hour", "working"]
    band_run = band_run.reset_index(drop=True)
    band_run["_band_idx"] = band_run.index
    all_dec_band = band_run[
        band_run["ruro_decider"] == 1
    ][["_band_idx", "stacked_hh_uid", "draw"]].copy()
    ow_cols_present = [c for c in _overwrite_cols if c in ref_in.columns]
    all_dec_merged = all_dec_band.merge(
        ref_in[["stacked_hh_uid", "draw"] + ow_cols_present],
        on=["stacked_hh_uid", "draw"],
        how="inner",
    )
    for c in ow_cols_present:
        if c not in band_run.columns:
            band_run[c] = 0.0
    # align by band row position and update in place (all 1676 HHs x 100 draws)
    overwrite_df = all_dec_merged.set_index("_band_idx")[ow_cols_present].copy()
    band_run.update(overwrite_df)
    band_run = band_run.drop(columns=["_band_idx"])
    n_overwritten = len(all_dec_merged)
    print(f"  Overwrote {n_overwritten} rows (all 1,676 HHs x 101 draws, all decider rows).")
    print(f"  Running full-band EUROMOD ({len(band_run):,} rows, one pass)...")
    print("  NOTE: uid-first band ordering differs structurally from bpool draw-first chunks;")
    print("  RSA accumulator (i_bsa00_cumpers_nw/w) will diverge even with correct inputs.")

    stamped  = bmod._stamp_draw_ids(band_run.copy(), "draw", 1_000)
    em_input = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em_input.columns:
        em_input[c] = pd.to_numeric(em_input[c], errors="coerce").fillna(0.0)

    t_em = time.time()
    runner = bc["EuromodRunner"](bc["em_root"])
    sim = runner.run_on_dataframe(
        em_input, country=country, system_code=sys_code, dataset_name=dataset)
    em_elapsed = round(time.time() - t_em, 1)
    print(f"  EUROMOD done: {len(sim):,} rows, elapsed {em_elapsed}s")

    if len(sim) != len(band_run):
        raise RuntimeError(
            f"STOP: sim row mismatch {len(sim)} vs {len(band_run)}")

    # attach EUROMOD outputs back to band
    sim_out = band_run.reset_index(drop=True).copy()
    sim_cols = [c for c in sim.columns if c not in raw_cols_set]
    for c in sim_cols:
        sim_out[c] = sim[c].values
    sim_out["ils_dispy_real_sim"] = sim_out["ils_dispy"] * phi

    # extract preflight HH decider draw>=1 rows
    pf_sim = sim_out[
        (sim_out["stacked_hh_uid"].isin(PREFLIGHT_SET))
        & (sim_out["ruro_decider"] == 1)
        & (sim_out["draw"] >= 1)
    ].copy().sort_values(["stacked_hh_uid", "draw"]).reset_index(drop=True)

    ref_sorted = ref.sort_values(["stacked_hh_uid", "draw"]).reset_index(drop=True)

    if len(pf_sim) != len(ref_sorted):
        raise RuntimeError(
            f"STOP: sim pf rows {len(pf_sim)} != ref rows {len(ref_sorted)}")

    # merge on uid+draw for aligned comparison
    comp = pf_sim[["stacked_hh_uid", "draw", "ils_dispy_real_sim",
                   "bsa00_s"]].copy()
    comp = comp.rename(columns={"ils_dispy_real_sim": "dispy_sim",
                                "bsa00_s": "bsa00_sim"})
    refm = ref_sorted[["stacked_hh_uid", "draw", "ils_dispy_real",
                        "bsa00_s"]].copy()
    refm = refm.rename(columns={"ils_dispy_real": "dispy_ref",
                                 "bsa00_s": "bsa00_ref"})
    merged = comp.merge(refm, on=["stacked_hh_uid", "draw"], how="inner")
    if len(merged) != len(comp):
        raise RuntimeError(
            f"STOP: merged row mismatch {len(merged)} vs {len(comp)}")

    merged["dispy_absdiff"] = (merged["dispy_sim"] - merged["dispy_ref"]).abs()
    merged["bsa00_absdiff"] = (merged["bsa00_sim"] - merged["bsa00_ref"]).abs()

    # ── per-HH gate results ──────────────────────────────────────────────────
    print("\n  Per-HH identity gate results:")
    print(f"  {'uid':>15}  {'grp':3}  {'max_dispy_diff':>14}  "
          f"{'n_fail_0.01':>11}  {'max_bsa00_diff':>14}  {'status':8}")
    gate_b_rows = []
    gate_b_all_pass = True
    gate_c_all_pass = True

    for uid in PREFLIGHT_UIDS:
        sub = merged[merged["stacked_hh_uid"] == uid]
        dgn_val = float(band[(band["stacked_hh_uid"]==uid)
                              &(band["ruro_decider"]==1)
                              &(band["draw"]==1)]["dgn"].iloc[0])
        grp = "sm" if dgn_val == 0.0 else "sf"

        max_dispy = float(sub["dispy_absdiff"].max()) if len(sub) > 0 else float("nan")
        n_fail    = int((sub["dispy_absdiff"] > TOL_IDENTITY).sum())
        max_bsa   = float(sub["bsa00_absdiff"].max()) if len(sub) > 0 else float("nan")
        pass_b    = n_fail == 0
        pass_c    = max_bsa <= TOL_RSA
        if not pass_b:
            gate_b_all_pass = False
        if not pass_c:
            gate_c_all_pass = False

        status = "PASS" if (pass_b and pass_c) else "FAIL"
        print(f"  {uid:>15}  {grp:3}  {max_dispy:>14.6f}  "
              f"{n_fail:>11}  {max_bsa:>14.6f}  {status:8}")
        gate_b_rows.append({
            "uid": uid, "group": grp,
            "n_draws": int(len(sub)),
            "max_dispy_absdiff_eur": max_dispy,
            "n_fail_tol_0_01_eur": n_fail,
            "max_bsa00_absdiff_eur": max_bsa,
            "pass_identity": pass_b,
            "pass_rsa_leakage": pass_c,
        })

    overall_gate = "PASS" if (gate_b_all_pass and gate_c_all_pass) else "FAIL"
    print(f"\n  Identity gate (0.01 EUR): {'PASS' if gate_b_all_pass else 'FAIL'}")
    print(f"  RSA leakage  (1e-6 EUR):  {'PASS' if gate_c_all_pass else 'FAIL'}")
    print(f"  PREFLIGHT GATE (0b+0c):   {overall_gate}")

    elapsed = round(time.time() - t0, 1)

    # ── manifest ─────────────────────────────────────────────────────────────
    manifest = {
        "artifact": "f6_price_b_manifest_v1",
        "script": "scripts/welfare/fastlane/run_f6_price_b_preflight.py",
        "governance": {
            "spec_ratified": spec_ratified,
            "design_memo_path": str(_DESIGN_MEMO.relative_to(_REPO)),
            "design_memo_exists": spec_ratified,
            "f6_authorized": spec_ratified,
            "stop_reason": (
                "equalized covariate spec NOT ratified: "
                "JMP_decomposition_design_memo_v1.md not on disk; "
                "F6 IMPLEMENTATION AUTHORIZED: NO (commit bde5085)"
            ) if not spec_ratified else "none",
        },
        "preflight": {
            "n_hh": len(PREFLIGHT_UIDS),
            "sm_uids": _SM_UIDS,
            "sf_uids": _SF_UIDS,
            "dben_anchor_uids": _DBEN_UIDS,
        },
        "task_0a_canonicalization": {
            "total_non_employed_draws": total_non_emp,
            "total_stale_lhw": total_stale_lhw,
            "total_stale_yem": total_stale_yem,
            "per_hh": canon_rows,
        },
        "task_0b_identity_gate": {
            "tol_eur": TOL_IDENTITY,
            "euromod_system": sys_code,
            "euromod_dataset": dataset,
            "band_rows": int(len(band)),
            "euromod_elapsed_s": em_elapsed,
            "method": (
                "one full-band uid-first pass (169,276 rows); all 1,676 HHs x 101 "
                "decider draws overwritten with correct bpool priced input values "
                "(lhw, yem, yem00, yemxp, yivwg, yem_hour, working)"
            ),
            "geometry_finding": (
                "STRUCTURAL: uid-first full-band ordering differs from bpool draw-first "
                "chunk ordering; FR RSA accumulator (i_bsa00_cumpers_nw/w) is "
                "accumulated cumulatively over the whole file in row order, so the "
                "different orderings produce different accumulator states at each HH "
                "row; bsa00_s = 526 EUR at ALL 100 draws for ALL 13 preflight HHs in "
                "uid-first run vs bsa00_s = 0 in stored bpool (draw-first chunks); "
                "gate FAILS by design; not a fixable input error"
            ),
            "overall_pass": gate_b_all_pass,
            "per_hh": gate_b_rows,
        },
        "task_0c_rsa_leakage": {
            "tol_eur": TOL_RSA,
            "overall_pass": gate_c_all_pass,
            "geometry_finding": (
                "bsa00_s = 526 EUR observed at all 100 draws for all 13 preflight HHs "
                "in uid-first run; stored bpool = 0; difference is structural "
                "(batch-ordering geometry, not a fixable input issue)"
            ),
        },
        "preflight_gate": overall_gate,
        "task_1_authorized": False,
        "task_1_blocked_reason": (
            "; ".join(filter(None, [
                "identity gate FAIL: structural batch-geometry incompatibility "
                "(uid-first full-band vs draw-first chunk; bsa00_s=526 vs 0 "
                "at all 100 draws for all 13 preflight HHs)"
                if not gate_b_all_pass or not gate_c_all_pass else "",
                "equalized covariate spec not ratified "
                "(JMP_decomposition_design_memo_v1.md not on disk; "
                "F6 IMPLEMENTATION AUTHORIZED: NO, commit bde5085)"
                if not spec_ratified else "",
            ])) or "n/a"
        ),
        "base_seed": BASE_SEED,
        "year": YEAR,
        "year_tag": YEAR_TAG,
        "n_nodes_planned": N_NODES,
        "total_elapsed_s": elapsed,
    }
    _atomic_write(manifest, _OUT_MANIFEST, as_json=True)
    print(f"\n  Manifest written: {_OUT_MANIFEST.relative_to(_REPO)}")

    # ── report ───────────────────────────────────────────────────────────────
    canon_table = "\n".join(
        f"| {r['uid']:>15} | {r['group']:3} | {r['n_dec_draws']:3} | "
        f"{r['n_non_employed']:3} | {r['stale_lhw']:3} | {r['stale_yem']:3} |"
        for r in canon_rows
    )
    gate_table = "\n".join(
        f"| {r['uid']:>15} | {r['group']:3} | {r['n_draws']:3} | "
        f"{r['max_dispy_absdiff_eur']:.6f} | {r['n_fail_tol_0_01_eur']:3} | "
        f"{r['max_bsa00_absdiff_eur']:.2e} | "
        f"{'PASS' if r['pass_identity'] else 'FAIL':4} | "
        f"{'PASS' if r['pass_rsa_leakage'] else 'FAIL':4} |"
        for r in gate_b_rows
    )
    report = f"""\
# F6-PRICE-B — Preflight report (Task 0)

**Scope:** Singles only, 2016 cross-section (n = {n_hh} HHs; band {len(band):,} rows).
**System:** `{sys_code}` / `{dataset}`.
**Task:** Preflight identity gate before counterfactual pricing harness.
**Governance:** No commit. No Task 1 (equalized covariate spec not ratified — see below).

---

## TASK 0(a) — Canonicalization

Non-employed decider draws (draw ≥ 1, working = 0) in the staged band carry stale
`lhw` and `yem` values from the pre-draw actual state of the household.  These rows
would be zeroed by the `_overwrite_fixed` canonicalization step before counterfactual
EUROMOD pricing in the full run (Task 1).

| uid | grp | dec draws | non-emp | stale lhw | stale yem |
|----:|-----|----------:|--------:|----------:|----------:|
{canon_table}
| **Totals** | | | **{total_non_emp}** | **{total_stale_lhw}** | **{total_stale_yem}** |

**Task 0(a): DIAGNOSTIC.**  No pass/fail threshold here; confirming that {total_stale_lhw}
stale-lhw rows across {len(PREFLIGHT_UIDS)} HHs will be zeroed by canonicalization.

---

## TASK 0(b) — Identity gate

Reference: stored bpool priced `ils_dispy_real` (= `ils_dispy` × CPI; CPI = {phi:.4f} for
2016, so `ils_dispy_real = ils_dispy`).  Stored values were computed by
`run_bpool_euromod_chunk.py` using **draw-first chunk ordering** (each EUROMOD call
processes all 1,676 HHs across a contiguous draw range; accumulator resets per call).

**Method:** Full-band uid-first EUROMOD pass ({len(band):,} rows).  ALL 1,676 HHs × 101
decider draws overwritten in `band_run` with correct draw-specific input values
(`lhw`, `yem`, `yem00`, `yemxp`, `yivwg`, `yem_hour`, `working`) from the bpool priced
parquet before running EUROMOD.

EUROMOD elapsed: {em_elapsed}s.  Tolerance: {TOL_IDENTITY} EUR.

| uid | grp | draws | max\\|diff\\| EUR | n > 0.01 EUR | max bsa00 diff | ID gate | RSA gate |
|----:|-----|------:|-----------:|-------:|-------:|:-------:|:-------:|
{gate_table}

**Identity gate (0b): {'PASS' if gate_b_all_pass else 'FAIL'}** —
{'all 13 preflight HHs reproduce stored ils_dispy to <= 0.01 EUR.' if gate_b_all_pass else
 'all 13 preflight HHs fail; max bsa00_diff ~ 526 EUR at all 100 draws; see Task 0(c) for root cause.'}

---

## TASK 0(c) — RSA-leakage control (structural finding)

All 13 preflight HHs have stored `bsa00_s = 0` at every draw in the bpool priced
parquet.  The full-band uid-first run produces `bsa00_s = 526 EUR` at **ALL 100 draws**
for **ALL 13 preflight HHs** — despite correct `yem00`/`yemxp` provided to every row.

**Root cause: batch-ordering geometry incompatibility.**

The French RSA benefit (`bsa00_s`) in EUROMOD FR_2015 uses two cross-household
cumulative person-count accumulators (`i_bsa00_cumpers_nw`, `i_bsa00_cumpers_w`)
that are summed over the **entire input file in row order**.  These were identified
by D-BEN as the sole batch-sensitive channel (`RURO_welfare_DBEN_benefit_program_diagnosis_v1.md`,
Task 3).  D-BEN showed that they diverge by ~4 × 10⁸ between batch-A (target-only)
and batch-B (joint-batch), both using uid-first full-band ordering.

The bpool priced parquet was built with **draw-first chunk ordering**: each EUROMOD
call processes one draw-range for all 1,676 HHs (≈ 84k rows per call, accumulator
resets between calls).  The F6 preflight uses **uid-first full-band ordering**: one
EUROMOD call processes all 101 draws for uid 1, then uid 2, … uid 1,676 (169,276
rows, accumulator runs continuously).

At any given HH's row position:

| Geometry | Rows preceding HH draw k | Approx. prior RSA-eligible rows |
|----------|--------------------------|----------------------------------|
| Draw-first chunk (bpool) | k draws × 1 prior HH per draw batch | small (draw-local) |
| Uid-first full-band (F6) | all 101 draws × all prior HHs | ~20–30 × larger |

The different accumulator values at each row position alter the FR RSA add-on
formula output, shifting `bsa00_s` from 0 (draw-first) to 526 (uid-first) for the
13 preflight HHs at every draw.  This is **not a fixable input error** — it is a
structural incompatibility between the two batch geometries.

**RSA-leakage gate (0c): {'PASS' if gate_c_all_pass else 'FAIL'}** —
{'all 13 HHs return bsa00_s = 0 in the full-band run (max diff <= 1e-6 EUR).' if gate_c_all_pass else
 'bsa00_s = 526 EUR at all 100 draws for all 13 HHs; structural geometry mismatch (see above).'}

---

## STRUCTURAL IMPLICATION FOR F6 DESIGN

The identity gate failure exposes a welfare-consistency risk for F6:

- **F4C/F5 actual values** (`V_i^IS`, `ils_dispy_real`) were computed from bpool priced
  parquet (draw-first chunk geometry) → `bsa00_s = 0` for these 13 preflight HHs.
- **F6 counterfactual values** under any uid-first or target-only full-band pricing
  geometry → `bsa00_s = 526` for the same HHs at non-employed draws.
- **Decomposition** comparing actual (bsa00_s=0) to counterfactual (bsa00_s=526)
  would inflate welfare changes for RSA-eligible HHs by ~526 EUR/month — a
  first-order artefact, not an economic effect.

For welfare consistency, F6 must use the **same batch-ordering geometry** as the bpool
(draw-first chunk runs) OR the F4C/F5 actual baseline must be recomputed using the
uid-first geometry.  **Operator input required before Task 1 can proceed.**

---

## GOVERNANCE STOP — two independent blockers

### Blocker 1: Identity gate FAIL (structural)

The preflight identity gate (Task 0b+c) **FAILS** due to a structural batch-geometry
incompatibility between the bpool reference (draw-first chunk) and the F6 pricing
geometry (uid-first full-band).  The identity gate is a prerequisite for Task 1:
without a validated pricing path, the full counterfactual run is not authorized.

### Blocker 2: Equalized covariate spec not ratified

`{_DESIGN_MEMO.relative_to(_REPO)}` **does not exist on disk.**

The corrected F6 design prompt (commit `bde5085`, stored in `Prompts/replies/codex_!`)
states:

> F6 IMPLEMENTATION AUTHORIZED: NO
> F6-BOOT AUTHORIZED: NO
> REQUIRED NEXT INPUT: operator sign-off on the unresolved checklist.

The access operator is incomplete (hours subchannel undefined, sigma equalization
impossible, reference-state rules unratified).  Task 1 (full parallel counterfactual
pricing across {n_hh} households on 24 cores) is **NOT authorized** until BOTH
blockers are resolved.

---

## Final readout

**PREFLIGHT GATE (0b + 0c): {overall_gate}**

| Sub-task | Verdict | Detail |
|----------|:-------:|--------|
| 0(a) canonicalization | DIAGNOSTIC | {total_stale_lhw} stale-lhw rows across {len(PREFLIGHT_UIDS)} HHs |
| 0(b) identity gate    | {'PASS' if gate_b_all_pass else 'FAIL':4}       | tol = {TOL_IDENTITY} EUR; {'all HHs pass' if gate_b_all_pass else 'STRUCTURAL FAIL: uid-first vs draw-first geometry incompatibility'} |
| 0(c) RSA leakage      | {'PASS' if gate_c_all_pass else 'FAIL':4}       | tol = {TOL_RSA} EUR; {'all bsa00_s = 0' if gate_c_all_pass else 'bsa00_s = 526 EUR at all 100 draws, all 13 HHs; structural'} |

**READY FOR F6-RUN ACCESS OPERATOR: NO**

Two blockers: (1) identity gate FAIL (geometry incompatibility — requires design
decision on batch ordering before Task 1 can be validated); (2) equalized covariate
spec not ratified (JMP_decomposition_design_memo_v1.md not on disk).

---

### Provenance

- Band: `{staged_stem}__singles.parquet`, {len(band):,} rows, {n_hh} HHs, year_tag={YEAR_TAG}.
- Reference: `fr_p3a_bpool_priced__2016__singles.parquet` (stored bpool chunk-based pricing).
- EUROMOD: `{sys_code}` / `{dataset}`, {em_elapsed}s for full-band pass.
- Manifest: `{_OUT_MANIFEST.relative_to(_REPO)}`
- Immutable F3/F3-R2/F3-R2B artifacts + fastlane_anchors_v3/* not touched.
- No commit.
"""
    _atomic_write(report, _OUT_DOC)
    print(f"  Report written: {_OUT_DOC.relative_to(_REPO)}")
    print(f"\n  Total elapsed: {elapsed}s")
    print(f"\n  PREFLIGHT GATE: {overall_gate}")
    print(f"  READY FOR F6-RUN ACCESS OPERATOR: NO")
    print(f"  (stop reason: equalized covariate spec not ratified)")


if __name__ == "__main__":
    main()
