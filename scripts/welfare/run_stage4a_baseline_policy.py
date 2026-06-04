"""
STAGE FOUR, INCREMENT FOUR-A — post-Two-O baseline policy + welfare-pricing config preparation
+ metadata/path readiness gate.

Reads the Four-A welfare-pricing config block (welfare.stage4 in welfare_stage1_w3.yaml) and the
Three-A / Three-B1 / Three-B3 provenance, then runs a METADATA/PATH readiness gate ONLY:
confirm every referenced staged path exists and matches the recorded provenance (row counts,
101/901 resolution, component coherence, staged-stem identity). It PRICES NOTHING and writes no
parquet.

Does NOT: swap/overwrite/move/delete production parquet, promote any baseline to canonical,
re-estimate, compute V_i^dir, price redrawn nodes, promote W^3, or touch any measure beyond W^3.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import pyarrow.parquet as pq  # noqa: E402
import yaml  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_CONFIG = Path("scripts/welfare/configs/welfare_stage1_w3.yaml")
_THREE_A_VAL = Path("outputs/welfare/stage1_w3/stage3a_pinned_baseline_validation.json")
_THREE_A_CFG = Path("outputs/welfare/stage1_w3/stage3a_pinned_rebuild_config.json")
_THREE_B1 = Path("outputs/welfare/stage1_w3/stage3b1_engine_ready_parity.json")
_THREE_B3 = Path("outputs/welfare/stage1_w3/stage3b3_synthetic_recovery.json")
_CERT_THETA = Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv")


def _load_json(p):
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def readiness_gate(cfg_stage4):
    """TASK 3 — metadata/path readiness gate ONLY. No pricing, no parquet writes."""
    bp = bpool_dir()
    wpr = cfg_stage4["welfare_pricing_reference"]
    stem = wpr["staged_engine_ready_stem"]
    checks = {}

    # 1) staged engine-ready parquet + meta exist; record row counts + resolution
    eng = {}
    for mode, exp_alts in (("singles", wpr["resolution_guard"]["singles_alts"]),
                           ("couples", wpr["resolution_guard"]["couples_alts"])):
        p = bp / f"{stem}__{mode}.parquet"
        rec = {"path": str(p), "exists": p.exists()}
        if p.exists():
            pf = pq.ParquetFile(p)
            rec["rows"] = int(pf.metadata.num_rows)
            # alts/HH from a cheap groupby on the key column
            import pandas as pd
            key = "stacked_hh_uid"
            df = pd.read_parquet(p, columns=[key])
            per_hh = df.groupby(key).size()
            rec["modal_alts_per_hh"] = int(per_hh.mode().iloc[0])
            rec["alts_uniform"] = bool((per_hh == exp_alts).all())
            rec["expected_alts"] = exp_alts
            rec["n_hh"] = int(per_hh.shape[0])
        eng[mode] = rec
    meta_p = bp / f"{stem}__mnlmeta.json"
    eng["mnlmeta_exists"] = meta_p.exists()
    checks["staged_engine_ready"] = eng

    # 2) staged priced dir + staged chunk dir exist (metadata only — count files)
    priced_dir = bp / wpr["staged_priced_dir_name"]
    chunk_dir = bp / wpr["staged_chunk_dir_name"]
    checks["staged_priced_dir"] = {
        "path": str(priced_dir), "exists": priced_dir.exists(),
        "n_priced_parquet": (len(list(priced_dir.glob("fr_p3a_bpool_priced__*.parquet")))
                             if priced_dir.exists() else 0)}
    checks["staged_chunk_dir"] = {
        "path": str(chunk_dir), "exists": chunk_dir.exists(),
        "n_chunk_parquet": (len(list(chunk_dir.glob("fr_p3a_bpool_priced__*__c*.parquet")))
                            if chunk_dir.exists() else 0),
        "n_done_markers": (len(list(chunk_dir.glob("*.done.json")))
                           if chunk_dir.exists() else 0)}

    # 3) cross-check against Three-A / Three-B1 provenance (stem identity, rows, coherence)
    b1 = _load_json(_THREE_B1)
    a = _load_json(_THREE_A_VAL)
    xref = {"three_b1_present": b1 is not None, "three_a_present": a is not None}
    if b1:
        xref["staged_stem_matches_three_b1"] = (b1.get("staged_stem") == stem)
        for mode in ("singles", "couples"):
            sg = b1.get("task2_structure_gates", {}).get(mode, {})
            this = eng.get(mode, {})
            xref[f"{mode}_rows_match_b1"] = (
                this.get("rows") == sg.get("rows_staged") if this.get("rows") is not None
                else None)
            xref[f"{mode}_alts_match_b1"] = (
                this.get("expected_alts") == sg.get("alts_per_hh_expected"))
    if a:
        xref["three_a_determinism_ok"] = a.get("task2_determinism_gate", {}).get("ok")
        xref["three_a_coherence_ok"] = a.get("task3_component_coherence_full", {}).get("ok")
        xref["three_a_candidate"] = a.get("task5_readiness", {}).get(
            "validated_reproducible_candidate_baseline")
    checks["provenance_cross_reference"] = xref

    # 4) pinned references resolvable (build module constants + Three-A pinned config)
    pin = cfg_stage4["pinned_euromod"]
    pinned_cfg = _load_json(Path(pin["pinned_config_json"]))
    build_ok = None
    try:
        import importlib
        bm = importlib.import_module(pin["build_module"])
        build_ok = bool(getattr(bm, "_SYSTEM_PAIRING", None)
                        and getattr(bm, "_CPI", None)
                        and getattr(bm, "_RAW_SCHEMA", None))
    except Exception as e:  # noqa: BLE001
        build_ok = f"import failed: {str(e)[:120]}"
    checks["pinned_references"] = {
        "pinned_config_present": pinned_cfg is not None,
        "build_module_constants_resolvable": build_ok,
        "system_pairing": (pinned_cfg or {}).get("system_pairing_by_data_year"),
        "cpi_phi": (pinned_cfg or {}).get("cpi_phi_by_data_year"),
    }

    # 5) baseline policy invariants (estimation canonical unchanged; no swap authorised)
    bpol = cfg_stage4["baseline_policy"]
    cert_unchanged = Path(bpol["estimation_canonical_theta_hat"]).resolve() == _CERT_THETA.resolve()
    checks["baseline_policy_invariants"] = {
        "estimation_canonical_is_certified_theta_hat": bool(cert_unchanged),
        "production_swap_authorised": bpol["production_swap_authorised"],
        "promote_staged_to_canonical": bpol["promote_staged_to_canonical"],
        "two_o_verdict": bpol["two_o_verdict"],
    }

    # ---- overall readiness (metadata/path only) ----
    eng_ok = all(eng[m]["exists"] and eng[m].get("alts_uniform")
                 for m in ("singles", "couples")) and eng["mnlmeta_exists"]
    paths_ok = (checks["staged_priced_dir"]["exists"]
                and checks["staged_chunk_dir"]["exists"])
    xref_ok = bool(xref.get("staged_stem_matches_three_b1")
                   and xref.get("singles_rows_match_b1") and xref.get("couples_rows_match_b1")
                   and xref.get("three_a_coherence_ok") and xref.get("three_a_candidate"))
    pin_ok = bool(checks["pinned_references"]["pinned_config_present"]
                  and checks["pinned_references"]["build_module_constants_resolvable"] is True)
    policy_ok = (cert_unchanged and bpol["production_swap_authorised"] is False
                 and bpol["promote_staged_to_canonical"] is False)
    overall = bool(eng_ok and paths_ok and xref_ok and pin_ok and policy_ok)
    checks["readiness_summary"] = {
        "staged_engine_ready_ok": eng_ok, "staged_paths_ok": paths_ok,
        "provenance_xref_ok": xref_ok, "pinned_refs_ok": pin_ok,
        "baseline_policy_ok": policy_ok,
        "overall_ready_for_population_faithful_existing_node_parity": overall,
    }
    return checks, overall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    if not _CONFIG.exists():
        raise SystemExit(f"STOP: welfare config missing: {_CONFIG}")
    with open(_CONFIG) as f:
        full_cfg = yaml.safe_load(f)
    stage4 = full_cfg.get("welfare", {}).get("stage4")
    if stage4 is None:
        raise SystemExit("STOP: welfare.stage4 config block missing (Task 2 not applied)")

    checks, overall = readiness_gate(stage4)
    b3 = _load_json(_THREE_B3)

    out = {
        "increment": "stage4a_baseline_policy_v1",
        "no_production_swap": True, "no_canonical_promotion": True, "no_v_dir": True,
        "priced_redrawn_node": False, "promoted_w3": False, "re_estimated": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "measures_touched": ["W3_only"],
        "two_o_verdict_carried": (b3 or {}).get("task4_two_o_verdict", {}).get("two_o_verdict"),
        "two_o_is_final": (b3 or {}).get("task4_two_o_verdict", {}).get("is_final"),
        "task1_baseline_policy": {
            "estimation_canonical_theta_hat": stage4["baseline_policy"][
                "estimation_canonical_theta_hat"],
            "certified_engine_ready_stem": stage4["baseline_policy"][
                "certified_engine_ready_stem"],
            "certified_production_not_swapped": True,
            "staged_role": stage4["welfare_pricing_reference"]["role"],
            "production_swap_authorised": stage4["baseline_policy"]["production_swap_authorised"],
            "promote_staged_to_canonical": stage4["baseline_policy"][
                "promote_staged_to_canonical"],
            "swap_is_supervisor_level_separate_authorisation": True,
        },
        "task2_welfare_pricing_config": {
            "config_path": str(_CONFIG),
            "config_block": "welfare.stage4",
            "staged_engine_ready_stem": stage4["welfare_pricing_reference"][
                "staged_engine_ready_stem"],
            "staged_priced_dir_name": stage4["welfare_pricing_reference"][
                "staged_priced_dir_name"],
            "staged_chunk_dir_name": stage4["welfare_pricing_reference"][
                "staged_chunk_dir_name"],
            "population_batch_required": stage4["pricing_discipline"][
                "population_batch_required"],
            "no_double_deflation": stage4["pricing_discipline"]["no_double_deflation"],
            "pinned_euromod": stage4["pinned_euromod"],
        },
        "task3_readiness_gate": checks,
        "overall_ready_for_population_faithful_existing_node_parity": overall,
        "scope_statement": (
            "Declares the post-Two-O baseline policy and prepares the welfare-pricing config; "
            "runs a metadata/path readiness gate ONLY. No production swap, no canonical "
            "promotion, no re-estimation, no V_i^dir, no redrawn pricing, no W^3 promotion, "
            "nothing beyond W^3. Prices nothing and writes no parquet."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)

    rs = checks["readiness_summary"]
    print(f"[four-A] Two-O carried: {out['two_o_verdict_carried']} (final={out['two_o_is_final']})")
    print(f"[four-A] estimation canonical = {out['task1_baseline_policy']['estimation_canonical_theta_hat']}")
    print(f"[four-A] staged pricing reference stem = "
          f"{out['task2_welfare_pricing_config']['staged_engine_ready_stem']} "
          f"(role: {out['task1_baseline_policy']['staged_role']})")
    print(f"[four-A] readiness: engine_ready={rs['staged_engine_ready_ok']} "
          f"paths={rs['staged_paths_ok']} xref={rs['provenance_xref_ok']} "
          f"pins={rs['pinned_refs_ok']} policy={rs['baseline_policy_ok']}")
    print(f"[four-A] OVERALL READY (metadata/path) = {overall}")
    print(f"[four-A] wrote {args.out_json}")


if __name__ == "__main__":
    main()
