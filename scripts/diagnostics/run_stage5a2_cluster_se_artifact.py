"""
STAGE FIVE-A2 — assemble the cluster-robust-SE artifact for the CERTIFIED baseline so the
enhanced styled-reporting layer (RURO_post_estimation_styled.py --cluster-se-json, per
docs/reporting/RURO_post_estimation_styled_general_reporting_enhancement_v1.md) can populate the
inference table + Hessian / T3-T5 / PE6 diagnostics.

READ-ONLY. Does NOT re-estimate, does NOT recompute the sandwich, does NOT price welfare nodes,
does NOT compute V_i^dir, does NOT promote W^3, does NOT touch production/staged pricing
artifacts. It assembles the `cluster_robust_se_artifacts` JSON the styled reporter reads, from
artifacts that ALREADY EXIST:
  - the certified theta + Hessian SE + clustered SE vectors (theta_hat_realdata_901_v1.csv);
  - the certified Hessian / cluster facts (PD, min_eig, condition number, n_clusters) parsed
    from the certified baseline doc's embedded JSON.

Checks emitted (computed from the existing SE vectors, not re-derived):
  T3_cluster_count   — n_clusters (from the certified doc)
  T4_se_positivity   — n SE <= 0 in the free block (strict <= 0, per the enhancement doc)
  T5_robust_vs_hessian — clustered/Hessian SE ratio distribution
  PE6_true_hessian   — condition number + free-block shape (from the certified doc)

Nothing here is country/year/spec-specific: paths are CLI args; param names come from the CSV;
the free mask is "all params present in the certified vector" (the certified vector IS the
identified 47-param block — theta_l_m and beta_ll are pinned/removed and absent from it).
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def _parse_certified_hessian_cluster(baseline_doc: Path):
    """Parse the certified Hessian/cluster facts from the baseline doc's embedded JSON
    (cond, min_eig, pd, n_clusters). Falls back to None fields if the block is absent."""
    facts = {"condition_number": None, "min_eig": None, "pd": None, "n_clusters": None}
    if not baseline_doc.exists():
        return facts
    txt = baseline_doc.read_text(encoding="utf-8")
    for block in re.findall(r"```json\s*(\{.*?\})\s*```", txt, re.S):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            continue
        h = d.get("hessian", d)
        if isinstance(h, dict) and ("cond" in h or "min_eig" in h):
            facts["condition_number"] = h.get("cond")
            facts["min_eig"] = h.get("min_eig")
            facts["pd"] = h.get("pd")
        nc = d.get("n_clusters")
        if nc is None:
            cs = d.get("cluster_summary") or d.get("clustered") or {}
            nc = cs.get("n_clusters") if isinstance(cs, dict) else None
        if nc is not None:
            facts["n_clusters"] = int(nc)
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta-hat", required=True, type=Path,
                    help="certified theta CSV: parameter,value,se_hessian,se_clustered")
    ap.add_argument("--baseline-doc", required=True, type=Path,
                    help="certified baseline doc carrying the embedded Hessian/cluster JSON")
    ap.add_argument("--out-json", required=True, type=Path,
                    help="cluster-robust-SE artifact for --cluster-se-json")
    ap.add_argument("--spec", type=Path, default=None,
                    help="spec YAML; if given, its fixed_params (pinned) are appended as "
                         "NON-FREE rows (free_mask=False, NaN SE) so the styled inference "
                         "table marks them outside the identified block (not free).")
    ap.add_argument("--cluster-col", default="idorighh")
    args = ap.parse_args()

    df = pd.read_csv(args.theta_hat)
    pnames = df["parameter"].astype(str).tolist()
    theta = df["value"].astype(float).to_numpy()
    se_h = df["se_hessian"].astype(float).to_numpy() if "se_hessian" in df.columns else \
        np.full(len(df), np.nan)
    se_r = df["se_clustered"].astype(float).to_numpy() if "se_clustered" in df.columns else \
        np.full(len(df), np.nan)
    n_free = len(pnames)  # the certified CSV is exactly the identified free block
    free_mask = [True] * n_free

    # Append pinned (fixed_params) parameters as NON-FREE rows so the styled inference table
    # does not display them as free with a misleading fixed=False / in_free=True. They carry
    # their pinned value and NaN SEs (not identified), and free_mask=False. AGNOSTIC: names
    # and values come from the spec's fixed_params, not hardcoded.
    pinned = {}
    if args.spec is not None:
        import sys as _sys
        _sys.path.insert(0, "scripts/bpool")
        _sys.path.insert(0, "scripts/enhanced")
        import estimation_spec_parser as _sp
        _spec = _sp.parse_specification(args.spec)
        pinned = dict(getattr(_spec, "fixed_params", {}) or {})
    pinned_names = [p for p in pinned if p not in pnames]
    for pn in pinned_names:
        pnames.append(pn)
        theta = np.append(theta, float(pinned[pn]))
        se_h = np.append(se_h, np.nan)
        se_r = np.append(se_r, np.nan)
        free_mask.append(False)
    n = len(pnames)  # full displayed set = free + pinned

    facts = _parse_certified_hessian_cluster(args.baseline_doc)

    # T4 — SE positivity on the FREE block only (strict <= 0, per the enhancement doc)
    se_r_free = se_r[: n_free]
    n_nonpos = int(np.sum(se_r_free <= 0))
    t4 = {"name": "T4_se_positivity", "n_free": n_free, "n_nonpositive": n_nonpos,
          "passed": bool(n_nonpos == 0), "comparison": "se_free <= 0",
          "note": "evaluated on the identified free block only; pinned params excluded"}

    # T5 — clustered / Hessian ratio distribution on the FREE block (pinned rows have NaN SE
    # and are excluded by isfinite, but slice explicitly for clarity).
    se_h_free, se_r_free2 = se_h[: n_free], se_r[: n_free]
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(se_h_free > 0, se_r_free2 / se_h_free, np.nan)
    rfin = ratio[np.isfinite(ratio)]
    t5 = {"name": "T5_robust_vs_hessian",
          "median_ratio": float(np.median(rfin)) if rfin.size else None,
          "max_ratio": float(np.max(rfin)) if rfin.size else None,
          "min_ratio": float(np.min(rfin)) if rfin.size else None,
          "n_above_2x": int(np.sum(rfin > 2.0)),
          "note": "clustered SE vs Hessian SE; >1 expected with repeat-HH clustering"}

    # T3 — cluster count
    t3 = {"name": "T3_cluster_count", "n_clusters": facts["n_clusters"],
          "cluster_col": args.cluster_col,
          "passed": bool(facts["n_clusters"] is not None and facts["n_clusters"] > 0)}

    # PE6 — true Hessian condition + FREE-block shape (the identified block, n_free x n_free)
    cond = facts["condition_number"]
    pe6 = {"name": "PE6_true_hessian", "condition_number": cond,
           "min_eig": facts["min_eig"], "pd": facts["pd"],
           "hessian_shape_free": [n_free, n_free],
           "near_singular_warning": bool(cond is not None and float(cond) > 1e12)}

    artifact = {
        "cluster_robust_se_artifacts": {
            "param_names": pnames,
            "converged_theta": theta.tolist(),
            "se_hessian_vector": se_h.tolist(),
            "se_robust_vector": se_r.tolist(),
            "free_mask": free_mask,
            "n_free": n_free,
            "n_displayed": n,
            "pinned_params": pinned_names,
            "cluster_col": args.cluster_col,
            "source": (f"certified theta CSV {args.theta_hat.name} + certified Hessian/cluster "
                       f"facts from {args.baseline_doc.name} (read-only; NOT recomputed)"),
        },
        "checks": {
            "T3_cluster_count": t3,
            "T4_se_positivity": t4,
            "T5_robust_vs_hessian": t5,
            "PE6_true_hessian": pe6,
        },
        "provenance": {
            "increment": "stage5a2_cluster_se_artifact_v1",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "read_only": True, "re_estimated": False, "sandwich_recomputed": False,
            "computed_v_dir": False, "computed_welfare": False, "promoted_w3": False,
            "priced_node": False, "production_swapped": False,
            "note": ("Assembled from EXISTING certified artifacts; the sandwich was NOT "
                     "recomputed (the certified clustered SEs are taken as-is from the certified "
                     "CSV). For the styled reporter's enhanced inference/Hessian/T3-T5 layer."),
        },
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(artifact, indent=2, default=float))
    print(f"[5a2] cluster-se artifact -> {args.out_json}")
    print(f"[5a2] n_free={n_free} pinned_non_free={pinned_names} (displayed={n}) "
          f"cond={cond} n_clusters={facts['n_clusters']} "
          f"T4_pass={t4['passed']} T5_median_ratio={t5['median_ratio']}")


if __name__ == "__main__":
    main()
