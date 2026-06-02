"""
Stage Two — Increment Two-F runner (Tasks 1 & 2): couples collision-exposure audit.

Task 1: alternative-level prevalence (no EUROMOD).
Task 2: likelihood-relevance at theta_hat (reuse welfare/estimator V machinery; no
        re-estimation). STOPs (records mapping_ambiguous) if the node-key -> engine-ready
        alternative mapping cannot be made unambiguous.

Writes provenance JSON + a per-household CSV under outputs/welfare/stage1_w3/. Does NOT
re-estimate, price any node, compute V_i^dir, or write any parquet. Task 3 (bounded
EUROMOD clean-reprice) is a separate runner (run_stage2_couples_reprice.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import pyarrow.parquet as pq  # noqa: E402
import welfare_core as wc  # noqa: E402
import welfare_couples_contamination_audit as au  # noqa: E402


def _engine_ready_key_cols(cfg):
    """Read just the couples key columns from the engine-ready file (fast projection)."""
    from _bpool_paths import bpool_dir
    b = cfg["baseline"]
    stem = b["couples_stem"]
    path = bpool_dir() / f"{stem}__couples.parquet"
    cols = ["data_year", "stacked_hh_uid", "draw_joint", "draw_male", "draw_female",
            "is_chosen_joint"]
    df = pq.read_table(path, columns=cols).to_pandas()
    years = list(b.get("years", []) or [])
    if years:
        df = df[df["data_year"].isin(years)].copy()
    return df, str(path)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    acfg = cfg["stage2"]["couples_contamination_audit"]
    thresholds = list(acfg["prob_mass_thresholds"])

    out = {"increment": "stage2_couples_contamination_audit_v1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "priced_any_node": False,
           "computed_v_dir": False, "wrote_parquet": False,
           "collision_definition": {
               "full_node_key": au.NODE_KEY,
               "collision_block_key": au.BLOCK_KEY,
               "rule": ("a (data_year, stacked_hh_uid, draw_joint) block is a collision "
                        "block iff it contains >1 distinct (draw_male, draw_female) pair; "
                        "every alternative in such a block is collision-exposed."),
               "build_provenance": ("build_bpool_precompute.py gate G2: 'draw_joint=0 "
                                    "intentionally shared by chosen+first sim cell' — the "
                                    "collision is a known build convention.")}}

    # ---- Task 1: prevalence (no EUROMOD) ----
    key_df, er_path = _engine_ready_key_cols(cfg)
    out["engine_ready_couples_path"] = er_path
    out["task1_prevalence"] = au.prevalence_audit(key_df)

    # ---- Task 2: likelihood-relevance at theta_hat (reuse V machinery) ----
    lr = au.likelihood_relevance(cfg, thresholds)
    if isinstance(lr, dict):                       # mapping_ambiguous -> STOP path
        out["task2_likelihood_relevance"] = lr
        per_hh = None
    else:
        res, per_hh, _ = lr
        out["task2_likelihood_relevance"] = res

    out["scope_statement"] = (
        "Audit-only. No W^3 welfare finding produced; no measure beyond W^3 touched; "
        "nothing re-estimated; no node priced; no V_i^dir computed; no "
        "storage/precompute/priced/chunk/engine-ready parquet written. Collision-exposed "
        "= potentially contaminated until a clean reprice (Task 3) confirms a nonzero "
        "stored-vs-clean difference.")

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    if per_hh is not None:
        per_hh.to_csv(args.out_csv, index=False)

    print(f"[stage2:couples-audit] wrote {args.out_json}")
    p = out["task1_prevalence"]["pooled"]
    print(f"  POOLED: {p['n_households']} hh, {p['n_alternatives']} alts | "
          f"exposed alts={p['n_alternatives_exposed']} "
          f"({p['share_alternatives_exposed']*100:.3f}%) | "
          f"hh with collision={p['n_households_with_collision']} "
          f"({p['share_households_with_collision']*100:.2f}%) | "
          f"chosen exposed={p['n_chosen_exposed']}/{p['n_chosen_alternatives']}")
    lr2 = out["task2_likelihood_relevance"]
    if lr2.get("status") == "ok":
        em = lr2["exposed_mass"]
        print(f"  theta_hat exposed prob mass: mean={em['mean']:.3e} "
              f"median={em['median']:.3e} max={em['max']:.3e}")
        print(f"  share hh above thresholds: {lr2['share_hh_above_threshold']}")
        print(f"  chosen-alt exposed hh: {lr2['chosen_alt_exposed']['n_chosen_exposed']}"
              f"/{lr2['chosen_alt_exposed']['n_households_with_chosen']}")
    else:
        print(f"  TASK2 STATUS: {lr2.get('status')} — {lr2.get('reason')}")


if __name__ == "__main__":
    main()
