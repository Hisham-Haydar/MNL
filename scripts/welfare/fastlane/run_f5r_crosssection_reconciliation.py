"""
FAST-LANE F5-R: CROSS-SECTION SCOPE RECONCILIATION.

Reconciles the cross-section scope of the F5 inequality point estimates against the
governance documents. Inequality RECOMPUTATION ONLY (reuses the validated F5 weighted-index
functions). No F6, decomposition, bootstrap, estimation, EUROMOD, artifact overwrites, or commit.

Governance conflict:
  - JMP_welfare_measurement_decisions_memo_v2.md §13 (l.584-586): under a POOLED specification the
    PRIMARY baseline welfare distribution is option (b) = "the 2016 distribution computed from the
    pooled theta-hat but evaluated on the 2016 cross-section"; pooled (a) and reweighted-2016 (c)
    are SECONDARY sensitivities. The certified baseline joint_pooled_v1_bll0_tlmpin IS pooled.
  - JMP_results_campaign_roadmap_v1.md (l.14) frames the conference population as
    France 2015-2017, but (l.3) "supersedes nothing".
  => F5's pooled result is a valid CALCULATION but cannot be silently labeled PRIMARY.

Terminology: pooled sample = 5,007 household-year observations; original households/clusters =
3,902 idorighh; year_tag 1=2015, 2=2016, 3=2017.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parent.parent.parent.parent
for _p in ["scripts/bpool", "scripts/enhanced", "scripts/welfare", "scripts/pilot",
           "scripts/welfare/fastlane"]:
    sys.path.insert(0, str(_REPO / _p))
import run_f5_singles_measure_family as f5   # validated weighted-index functions (imported, not edited)

_F5_HH = _REPO / "outputs/welfare/fastlane/singles_measure_family_F5_households_v1.parquet"
_F5_MANIFEST = _REPO / "outputs/welfare/fastlane/F5_manifest_v1.json"
_DEC_MEMO = _REPO / "docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md"
_ROADMAP = _REPO / "docs/JMP_results_campaign_roadmap_v1.md"
_MAP_MEMO = _REPO / "docs/jmp_methodology/JMP_measure_mapping_memo_v1.md"

_OUT_PARQUET = _REPO / "outputs/welfare/fastlane/singles_measure_family_F5R_crosssection_v1.parquet"
_OUT_MANIFEST = _REPO / "outputs/welfare/fastlane/F5R_crosssection_manifest_v1.json"
_OUT_DOC = _REPO / "docs/jmp_methodology/RURO_welfare_F5R_crosssection_scope_reconciliation_v1.md"

_IMMUTABLE = {_F5_HH, _F5_MANIFEST, _DEC_MEMO, _ROADMAP, _MAP_MEMO}

HEADLINE = {"W1": "W1_omega_eur", "W4": "W4_omega_eur", "W6": "W6_omega_eur"}
CONV = {"W1": "W1_converged", "W4": "W4_bracket_converged", "W6": "W6_bracket_converged"}
YEAR_TAG = {1: 2015, 2: 2016, 3: 2017}


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard(dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: refuse to overwrite immutable artifact: {dest}")
    if dest.exists():
        raise FileExistsError(f"STOP: completed artifact exists: {dest}")


def _atomic_json(obj, dest):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=f5._jsonify)); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_parquet(df, dest):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _atomic_text(text, dest):
    _guard(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8"); tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def _indices(sub, col, conv_col, w):
    x = sub[col].to_numpy(float)
    c = sub[conv_col].to_numpy(bool)
    v = c & np.isfinite(x) & (x > 0)
    xv, wv = x[v], w[v]
    return {
        "n": int(v.sum()), "sum_weight": float(np.sum(wv)),
        "w_mean": f5.w_mean(xv, wv), "w_p10": f5.w_quantile(xv, wv, .10),
        "w_median": f5.w_quantile(xv, wv, .50), "w_p90": f5.w_quantile(xv, wv, .90),
        "w_p99": f5.w_quantile(xv, wv, .99), "w_max": float(np.max(xv)),
        "w_gini": f5.w_gini(xv, wv), "unw_gini": f5.w_gini(xv, np.ones_like(wv)),
        "w_cv2": f5.w_cv2(xv, wv), "w_theil_l": f5.w_theil_l(xv, wv),
        "w_atkinson_e1": f5.w_atkinson(xv, wv, 1), "w_atkinson_e2": f5.w_atkinson(xv, wv, 2),
        "top1pct_weight_share": f5.top_weight_share(xv, wv, .01),
    }


def main():
    t0 = time.time()
    for d in (_OUT_PARQUET, _OUT_MANIFEST, _OUT_DOC):
        _guard(d)
    print("F5-R start")

    hh = pd.read_parquet(_F5_HH)
    f5man = json.loads(_F5_MANIFEST.read_text())
    prov = {
        "f5_households_sha256": _sha256(_F5_HH),
        "f5_manifest_sha256": _sha256(_F5_MANIFEST),
        "spec_hash": f5man.get("spec_hash"), "theta_hash": f5man.get("theta_hash"),
        "consumption_time_unit": f5man.get("consumption_time_unit"),
    }

    # ---------------- TASK 1 — governance conflict ----------------
    print("\n=== TASK 1: governance conflict ===")
    n_obs = int(len(hh))
    n_clusters = int(hh["idorighh"].nunique())
    year_counts = {int(y): int((hh["year_tag"] == y).sum()) for y in sorted(hh["year_tag"].unique())}
    task1 = {
        "decisions_memo_v2_section13": {
            "rule": "Under a POOLED specification the PRIMARY baseline welfare distribution is option "
                    "(b): the 2016 distribution computed from the pooled theta-hat but evaluated on "
                    "the 2016 cross-section (l.584-586). Secondary sensitivities: (a) pooled across "
                    "all years, (c) reweighted-2016.",
            "applies_because": "the certified baseline joint_pooled_v1_bll0_tlmpin IS a pooled "
                               "specification, so the §13 pooled-case rule governs the primary scope.",
            "primary_scope_per_memo": "2016 cross-section (year_tag==2)",
        },
        "roadmap_v1": {
            "framing": "conference population = single-adult households in France 2015-2017 (l.14)",
            "status": "planning memo, supersedes nothing, pre-registers framing (l.3)",
            "implication": "frames the narrative population but does NOT supersede the §13 primary-"
                           "scope rule; it is a presentational/narrative framing, not a governance "
                           "amendment.",
        },
        "reconciliation": {
            "f5_pooled_validity": "the existing F5 pooled results remain VALID CALCULATIONS but "
                                  "cannot be silently labeled PRIMARY; under §13 the primary is the "
                                  "2016 cross-section and pooled is sensitivity (a).",
            "pooled_sample_obs": n_obs, "original_households_clusters": n_clusters,
            "year_tag_mapping": YEAR_TAG, "year_obs_counts": year_counts,
            "repeated_household_note": (f"{n_obs} household-year observations come from {n_clusters} "
                                        f"distinct original households (idorighh); households present "
                                        f"in multiple years appear as multiple pooled observations."),
        },
    }
    print(f"  pooled obs={n_obs} clusters(idorighh)={n_clusters} year_obs={year_counts}")
    print(f"  decisions-memo §13 -> primary = 2016 cross-section; roadmap 2015-2017 supersedes nothing")

    # ---------------- TASK 2 — recompute scopes ----------------
    print("\n=== TASK 2: recompute inequality by scope ===")
    scopes = {
        "primary_candidate_2016": hh["year_tag"] == 2,
        "pooled_sensitivity_2015_2017": pd.Series(True, index=hh.index),
        "year_2015": hh["year_tag"] == 1,
        "year_2016": hh["year_tag"] == 2,
        "year_2017": hh["year_tag"] == 3,
    }
    groups = {"singles_all": None, "singles_male": "singles_male", "singles_female": "singles_female"}
    rows = []
    nested = {}
    for sc, mask in scopes.items():
        nested[sc] = {}
        for gname, gval in groups.items():
            m = mask.to_numpy() if hasattr(mask, "to_numpy") else np.asarray(mask)
            if gval is not None:
                m = m & (hh["group"] == gval).to_numpy()
            sub = hh[m]
            w = sub["dwt"].to_numpy(float)
            rec = {}
            for meas, col in HEADLINE.items():
                idx = _indices(sub, col, CONV[meas], w)
                idx.update({"scope": sc, "group": gname, "measure": meas})
                rows.append(idx); rec[meas] = idx
            ginis = {me: rec[me]["w_gini"] for me in HEADLINE}
            gmin = min(ginis, key=ginis.get); gmax = max(ginis, key=ginis.get)
            rec["_spread"] = {"min_gini": ginis[gmin], "min_measure": gmin,
                              "max_gini": ginis[gmax], "max_measure": gmax,
                              "bracket": [ginis[gmin], ginis[gmax]],
                              "abs_spread": ginis[gmax] - ginis[gmin]}
            nested[sc][gname] = rec
        s = nested[sc]["singles_all"]
        print(f"  {sc:28s} all: W1={s['W1']['w_gini']:.4f} W4={s['W4']['w_gini']:.4f} "
              f"W6={s['W6']['w_gini']:.4f} spread={s['_spread']['abs_spread']:.4f} "
              f"(min={s['_spread']['min_measure']},max={s['_spread']['max_measure']}) n={s['W1']['n']}")

    # ---------------- TASK 3 — stability comparison ----------------
    print("\n=== TASK 3: stability comparison (2016 vs pooled/years) ===")
    base = nested["primary_candidate_2016"]
    compare = {}
    for other in ["pooled_sensitivity_2015_2017", "year_2015", "year_2017"]:
        compare[other] = {}
        for gname in groups:
            for meas in HEADLINE:
                g16 = base[gname][meas]["w_gini"]
                go = nested[other][gname][meas]["w_gini"]
                compare[other][f"{gname}.{meas}"] = {
                    "gini_2016": g16, "gini_other": go,
                    "abs_diff": go - g16, "rel_diff": (go - g16) / g16 if g16 else None}
    # bracket-measure changes + qualitative conclusion
    bracket_changes = {}
    qual = {}
    for sc in scopes:
        for gname in groups:
            r = nested[sc][gname]
            bracket_changes[f"{sc}.{gname}"] = {"min_measure": r["_spread"]["min_measure"],
                                                "max_measure": r["_spread"]["max_measure"]}
            # full-compensation (W4/W6) > W1 ?
            qual[f"{sc}.{gname}"] = bool(
                r["W4"]["w_gini"] > r["W1"]["w_gini"] and r["W6"]["w_gini"] > r["W1"]["w_gini"])
    min_is_w1_everywhere = all(v["min_measure"] == "W1" for v in bracket_changes.values())
    qual_holds_everywhere = all(qual.values())
    task3 = {
        "gini_diffs_vs_2016": compare,
        "bracket_measures_by_scope_group": bracket_changes,
        "min_measure_is_W1_everywhere": min_is_w1_everywhere,
        "full_compensation_exceeds_W1_everywhere": qual_holds_everywhere,
        "repeated_household_effect": (
            "the pooled scope contains repeated original households (3,902 idorighh across 5,007 "
            "household-year obs); persistent households are counted once per year, so the pooled "
            "cross-section is NOT an independent-household distribution. This affects (i) the "
            "effective sample / weighting interpretation and (ii) any inference (handled by the "
            "idorighh cluster-bootstrap), but does NOT change the point-estimate calculations. The "
            "single-year 2016 scope avoids the repeated-household double-representation."),
    }
    print(f"  min-Gini measure == W1 in every scope×group: {min_is_w1_everywhere}")
    print(f"  full-compensation (W4/W6) > W1 in every scope×group: {qual_holds_everywhere}")
    for other in compare:
        d = compare[other]["singles_all.W4"]
        print(f"  2016 vs {other}: W4(all) Gini {d['gini_2016']:.4f} -> {d['gini_other']:.4f} "
              f"(abs {d['abs_diff']:+.4f}, rel {d['rel_diff']*100:+.1f}%)")

    # ---------------- TASK 4 — recommendation ----------------
    print("\n=== TASK 4: recommendation ===")
    task4 = {
        "recommendation": "A",
        "recommendation_text": (
            "RETAIN the decisions-memo §13 rule: 2016 cross-section (year_tag==2) PRIMARY, pooled "
            "2015-2017 as the pre-registered sensitivity (a). Rationale: §13 is the standing ratified "
            "rule for the pooled-specification case (which the certified joint_pooled baseline is); "
            "the roadmap's 2015-2017 framing explicitly supersedes nothing and is a narrative/"
            "presentational frame served by REPORTING pooled alongside; and the 2016 single-year "
            "scope avoids the repeated-original-household double-representation present in the pooled "
            "cross-section. The qualitative conclusion (full-compensation inequality exceeds W1) and "
            "the min/max bracket measures are STABLE across 2016, pooled, and each year, so the choice "
            "is about labeling/primary-scope governance, not about which numbers are computed."),
        "alternative_B": (
            "AMEND governance explicitly: pooled 2015-2017 PRIMARY, 2016 sensitivity. This requires an "
            "EXPLICIT supersession of decisions-memo §13 (the roadmap cannot do this implicitly), plus "
            "a decision on how repeated original households are represented in the primary pooled "
            "cross-section (count-per-year vs collapse-to-household vs reweight)."),
        "not_ratified": True,
        "required_operator_signoff": (
            "explicit choice: (A) confirm 2016-primary per §13 [pooled = sensitivity], OR (B) ratify "
            "an explicit amendment of §13 to pooled-2015-2017-primary [2016 = sensitivity] together "
            "with the repeated-household representation rule. Until signed, PRIMARY CROSS-SECTION "
            "remains UNRATIFIED and F6 must not start."),
    }
    print(f"  recommendation: A (2016 primary per §13), pooled sensitivity — UNRATIFIED")

    # ---------------- OUTPUTS ----------------
    print("\n=== outputs ===")
    out_rows = []
    for r in rows:
        sc, gname = r["scope"], r["group"]
        sp = nested[sc][gname]["_spread"]
        rr = dict(r)
        rr["abs_w_minus_unw_gini"] = abs(r["w_gini"] - r["unw_gini"])
        rr["across_measure_min_gini"] = sp["min_gini"]
        rr["across_measure_max_gini"] = sp["max_gini"]
        rr["across_measure_min_measure"] = sp["min_measure"]
        rr["across_measure_max_measure"] = sp["max_measure"]
        rr["across_measure_abs_spread"] = sp["abs_spread"]
        rr["spec_hash"] = prov["spec_hash"]; rr["theta_hash"] = prov["theta_hash"]
        rr["scope_status"] = ("primary_candidate_UNRATIFIED" if sc == "primary_candidate_2016"
                              else "sensitivity")
        out_rows.append(rr)
    out_df = pd.DataFrame(out_rows).sort_values(["scope", "group", "measure"]).reset_index(drop=True)
    _atomic_parquet(out_df, _OUT_PARQUET)
    print(f"  wrote {_OUT_PARQUET} rows={len(out_df)}")

    manifest = {
        "f5r_artifact": "F5R_crosssection_manifest_v1",
        "spec_hash": prov["spec_hash"], "theta_hash": prov["theta_hash"],
        "provenance": prov,
        "task1_governance_conflict": task1,
        "task2_scopes": {sc: {g: {m: nested[sc][g][m] for m in HEADLINE} for g in groups}
                         for sc in scopes},
        "task2_spreads": {sc: {g: nested[sc][g]["_spread"] for g in groups} for sc in scopes},
        "task3_stability": task3,
        "task4_recommendation": task4,
        "f5_calculation_status": "valid",
        "primary_cross_section_status": "UNRATIFIED",
        "ready_for_f6_design_memo": False,
        "output_parquet": str(_OUT_PARQUET), "output_parquet_sha256": _sha256(_OUT_PARQUET),
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    _atomic_json(manifest, _OUT_MANIFEST)
    print(f"  wrote {_OUT_MANIFEST}")
    _atomic_text(_report(manifest), _OUT_DOC)
    print(f"  wrote {_OUT_DOC}")

    print("\n--- FINAL STATUS ---")
    print("F5 CALCULATION STATUS: valid")
    print("PRIMARY CROSS-SECTION STATUS: UNRATIFIED")
    print("READY FOR F6 DESIGN MEMO: NO")
    print("REQUIRED NEXT INPUT: explicit 2016-primary or pooled-primary ratification")
    print(f"\nF5-R COMPLETE in {round(time.time()-t0,1)}s")


def _report(m: dict) -> str:
    big = lambda x: ("n/a" if x is None else (f"{x:,.0f}" if isinstance(x, float) else str(x)))
    t1 = m["task1_governance_conflict"]; t3 = m["task3_stability"]; t4 = m["task4_recommendation"]
    sp = m["task2_spreads"]; sc2 = m["task2_scopes"]
    scopes = ["primary_candidate_2016", "pooled_sensitivity_2015_2017", "year_2015", "year_2016", "year_2017"]
    groups = ["singles_all", "singles_male", "singles_female"]
    L = []
    L.append("# RURO Welfare F5-R — Cross-Section Scope Reconciliation\n")
    L.append(f"Date: 2026-06-13 · spec_hash `{m['spec_hash']}` · theta_hash `{m['theta_hash']}` · "
             f"reuses frozen F5 households (recomputation only).\n")
    L.append("Inequality recomputation only; no F6/decomposition/bootstrap/estimation/EUROMOD/commit. "
             "F5 calculations are valid; the PRIMARY cross-section label is a governance decision, "
             "left UNRATIFIED here.\n")

    L.append("## 1. Governance conflict\n")
    L.append(f"- **Decisions memo v2 §13**: {t1['decisions_memo_v2_section13']['rule']} "
             f"{t1['decisions_memo_v2_section13']['applies_because']} → primary = "
             f"**{t1['decisions_memo_v2_section13']['primary_scope_per_memo']}**.")
    L.append(f"- **Roadmap v1**: {t1['roadmap_v1']['framing']}; status = {t1['roadmap_v1']['status']}. "
             f"{t1['roadmap_v1']['implication']}")
    rc = t1["reconciliation"]
    L.append(f"- **Reconciliation**: {rc['f5_pooled_validity']}")
    L.append(f"- Terminology: pooled sample = **{rc['pooled_sample_obs']} household-year observations**; "
             f"original households/clusters = **{rc['original_households_clusters']} idorighh**; "
             f"year_tag 1=2015, 2=2016, 3=2017; year obs counts {rc['year_obs_counts']}.")
    L.append(f"- {rc['repeated_household_note']}\n")

    L.append("## 2. Inequality by scope (weighted Gini, singles_all)\n")
    L.append("| scope | status | n | W1 | W4 | W6 | min→max | spread |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in scopes:
        r = sc2[s]["singles_all"]; z = sp[s]["singles_all"]
        st = "PRIMARY (UNRATIFIED)" if s == "primary_candidate_2016" else "sensitivity"
        L.append(f"| {s} | {st} | {r['W1']['n']} | {r['W1']['w_gini']:.4f} | {r['W4']['w_gini']:.4f} | "
                 f"{r['W6']['w_gini']:.4f} | {z['min_measure']}→{z['max_measure']} | {z['abs_spread']:.4f} |")
    L.append("\nBy group (weighted Gini W1 / W4 / W6):\n")
    L.append("| scope | group | W1 | W4 | W6 | spread |")
    L.append("|---|---|---|---|---|---|")
    for s in scopes:
        for g in groups:
            r = sc2[s][g]; z = sp[s][g]
            L.append(f"| {s} | {g} | {r['W1']['w_gini']:.4f} | {r['W4']['w_gini']:.4f} | "
                     f"{r['W6']['w_gini']:.4f} | {z['abs_spread']:.4f} |")
    L.append("\nSecondary indices, distribution summaries, and tail shares per scope×group×measure "
             "are in the F5R parquet.\n")

    L.append("## 3. Stability comparison (2016 vs pooled / other years)\n")
    L.append(f"- min-Gini measure is **W1 in every scope×group**: {t3['min_measure_is_W1_everywhere']}.")
    L.append(f"- Full-compensation (W4/W6) Gini **exceeds W1 in every scope×group**: "
             f"{t3['full_compensation_exceeds_W1_everywhere']}.")
    L.append("- 2016-vs-other weighted-Gini differences (singles_all):")
    L.append("\n| measure | 2016 | pooled | Δ pooled | 2015 | Δ2015 | 2017 | Δ2017 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for meas in ["W1", "W4", "W6"]:
        g16 = sc2["primary_candidate_2016"]["singles_all"][meas]["w_gini"]
        gp = t3["gini_diffs_vs_2016"]["pooled_sensitivity_2015_2017"][f"singles_all.{meas}"]
        g15 = t3["gini_diffs_vs_2016"]["year_2015"][f"singles_all.{meas}"]
        g17 = t3["gini_diffs_vs_2016"]["year_2017"][f"singles_all.{meas}"]
        L.append(f"| {meas} | {g16:.4f} | {gp['gini_other']:.4f} | {gp['abs_diff']:+.4f} | "
                 f"{g15['gini_other']:.4f} | {g15['abs_diff']:+.4f} | {g17['gini_other']:.4f} | "
                 f"{g17['abs_diff']:+.4f} |")
    L.append(f"\n- Repeated original households: {t3['repeated_household_effect']}\n")

    L.append("## 4. Recommendation (NOT ratified)\n")
    L.append(f"**Recommended: Option {t4['recommendation']}.** {t4['recommendation_text']}\n")
    L.append(f"**Alternative B**: {t4['alternative_B']}\n")
    L.append(f"**Required operator sign-off**: {t4['required_operator_signoff']}\n")

    L.append("## Outputs\n")
    L.append(f"- `{m['output_parquet']}` (sha256 `{m['output_parquet_sha256']}`)")
    L.append(f"- `F5R_crosssection_manifest_v1.json`; this report.\n")

    L.append("---\n")
    L.append("F5 CALCULATION STATUS: valid")
    L.append("PRIMARY CROSS-SECTION STATUS: UNRATIFIED")
    L.append("READY FOR F6 DESIGN MEMO: NO")
    L.append("REQUIRED NEXT INPUT: explicit 2016-primary or pooled-primary ratification")
    return "\n".join(L)


if __name__ == "__main__":
    main()
