"""
PHASE A — verify all 58 spec params BIND on both PrecomputedData objects.

Read-only. Two independent signals per param:
  (1) capture every engine logging warning ('skipping <param>' / 'not found') during a
      full LL evaluation on each object; assert none.
  (2) perturbation test: nudge each param from a non-trivial base theta and confirm the
      LL changes (binds) — the definitive proof the coefficient enters the objective.
      A param that is "present in spec" but whose nudge leaves LL unchanged is a SILENT
      DROP (the failure mode b15adbb fixed for couples; we now confirm singles too).

Runs on the engine-ready B-pool parquets (NOT estimation_ready / d1w1).
Uses a mixed-year slice so year_2015/2017 indicators have variation (else a single-year
slice makes the corresponding year param legitimately inert — not a drop).

NO estimation (no optimizer). Reports per-object bound/not-bound. GATE: any silent drop
or warning on either object -> FAIL.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
from _bpool_paths import bpool_dir  # noqa: E402
import estimation_spec_parser as sp   # noqa: E402
import estimation_utils as eu          # noqa: E402
import estimation_engine as ee         # noqa: E402

_BP = bpool_dir()
_SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
_META = json.load(open(_BP / "fr_p3a_bpool_engine_ready__mnlmeta.json"))

# Params that are couples-only (do not apply to a singles object) — for reporting.
_COUPLES_ONLY = {"beta_ll", "beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "theta_l_m",
                 "beta_l0_f", "beta_l_age_f", "beta_l_age2_f", "beta_l_nkids_f", "theta_l_f",
                 "beta_occ_2_cm", "beta_occ_3_cm", "beta_occ_4_cm",
                 "beta_occ_2_cf", "beta_occ_3_cf", "beta_occ_4_cf", "beta_c"}
_SINGLES_ONLY = {"beta_l0_sm", "beta_l_age_sm", "beta_l_age2_sm", "beta_c_sm", "theta_l_sm",
                 "beta_l0_sf", "beta_l_age_sf", "beta_l_age2_sf", "beta_l_nkids_sf", "beta_c_sf",
                 "theta_l_sf", "theta_c_singles",
                 "beta_occ_2_sm", "beta_occ_3_sm", "beta_occ_4_sm",
                 "beta_occ_2_sf", "beta_occ_3_sf", "beta_occ_4_sf"}


class _WarnCapture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.msgs = []
    def emit(self, record):
        self.msgs.append(record.getMessage())


def _base_theta(spec) -> np.ndarray:
    """Non-trivial base: start from initial vector, set obvious zeros to small values so
    a perturbation test is meaningful (many spec defaults are 0.0)."""
    th = spec.get_initial_vector().astype(float).copy()
    for i, name in enumerate(spec.all_param_names):
        if th[i] == 0.0:
            th[i] = 0.3  # generic non-zero
    # keep box-cox thetas in-bounds (they start negative; leave as-is)
    return th


def _mixed_year_couples_slice(n_per_year=40) -> pd.DataFrame:
    c = pd.read_parquet(_BP / "fr_p3a_bpool_engine_ready__couples.parquet")
    uids = []
    for y, g in c.groupby("data_year"):
        uids += list(pd.Series(g["stacked_hh_uid"].unique()).head(n_per_year))
    sl = c[c["stacked_hh_uid"].isin(uids)].sort_values(["idhh", "draw_joint"]).reset_index(drop=True)
    return sl


def _mixed_year_singles_slice(n_per_year=80) -> pd.DataFrame:
    s = pd.read_parquet(_BP / "fr_p3a_bpool_engine_ready__singles.parquet")
    uids = []
    for y, g in s.groupby("data_year"):
        uids += list(pd.Series(g["stacked_hh_uid"].unique()).head(n_per_year))
    sl = s[s["stacked_hh_uid"].isin(uids)].sort_values(["idhh", "draw"]).reset_index(drop=True)
    return sl


def analyse(obj_label: str, data, spec, ll_func, applicable_predicate) -> dict:
    print(f"\n{'='*70}\nOBJECT: {obj_label}\n{'='*70}")
    th = _base_theta(spec)

    # (1) capture warnings during a clean LL eval
    cap = _WarnCapture()
    elog = logging.getLogger("estimation_engine")
    elog.addHandler(cap); prev = elog.level; elog.setLevel(logging.WARNING)
    ll0 = ll_func(th, data, spec)
    elog.removeHandler(cap); elog.setLevel(prev)
    skip_warnings = [m for m in cap.msgs if "skipping" in m.lower() or "not found" in m.lower()]
    print(f"  LL@base (neg) = {ll0:.4f}   finite={np.isfinite(ll0)}")
    print(f"  engine skip/not-found warnings: {len(skip_warnings)}")
    for m in skip_warnings:
        print(f"    !! {m}")

    # (2) perturbation test per param
    bound, not_bound, na = [], [], []
    for i, name in enumerate(spec.all_param_names):
        applicable = applicable_predicate(name)
        if not applicable:
            na.append(name)
            continue
        thp = th.copy()
        # nudge in-bounds: small additive step, sign away from any bound
        step = 0.2
        lo, hi = -np.inf, np.inf
        b = spec.get_bounds_tuple()
        if b and i < len(b) and b[i] is not None:
            lo = b[i][0] if b[i][0] is not None else -np.inf
            hi = b[i][1] if b[i][1] is not None else np.inf
        if thp[i] + step > hi:
            step = -step
        thp[i] = thp[i] + step
        llp = ll_func(thp, data, spec)
        moved = np.isfinite(llp) and abs(llp - ll0) > 1e-7
        (bound if moved else not_bound).append(name)

    print(f"\n  BOUND ({len(bound)}): nudging moves LL")
    print(f"  NOT-APPLICABLE to this object ({len(na)}): {sorted(na)}")
    if not_bound:
        print(f"  *** NOT BOUND ({len(not_bound)}) — SILENT DROP: {sorted(not_bound)}")
    else:
        print(f"  NOT BOUND: none")

    return {"object": obj_label, "ll0": float(ll0), "skip_warnings": skip_warnings,
            "bound": sorted(bound), "not_bound": sorted(not_bound), "na": sorted(na)}


def main():
    spec = sp.parse_specification(_SPEC)
    n = len(spec.all_param_names)
    print(f"PHASE A — param binding on engine-ready B-pool objects")
    print(f"Spec param count: {n}  ({'OK 58' if n == 58 else 'FAIL — expected 58'})")
    if n != 58:
        sys.exit(1)

    # SINGLES: applicable = not couples-only AND not a couples-block leisure param.
    # Singles objects carry singles-applicable params: singles leisure (_sm/_sf), shared
    # singles theta_c, and the SHARED opportunity/wage params (hours, market, occ_s*, wage).
    # The market-opp household shifters (reg/drgur/drgmd/year) are applies_to:household,
    # which the singles market-opp path SKIPS BY DESIGN (engine line 116-117) -> they are
    # NOT applicable to a singles object and must not be counted as drops.
    shared_opp = {"beta_E","beta_h_pt1","beta_h_pt2","beta_h_ft","beta_h_lh","beta_E_gsur",
                  "beta_w0","beta_w_educL","beta_w_educH","beta_w_pexp","beta_w_pexp2","sigma"}
    household_market = {"beta_E_drgn2","beta_E_drgn3","beta_E_drgn4","beta_E_drgn5","beta_E_drgn6",
                        "beta_E_drgn7","beta_E_drgn8","beta_E_y2015","beta_E_y2017",
                        "beta_E_drgur","beta_E_drgmd"}
    def singles_applicable(name):
        if name in _COUPLES_ONLY:
            return False
        if name in household_market:
            return False  # applies_to:household — singles path skips by design
        return True       # singles leisure, theta_c_singles, shared opp/wage, occ_s*
    def couples_applicable(name):
        return name not in _SINGLES_ONLY  # everything else applies to couples object

    # Singles split into MALE and FEMALE objects (the engine builds one per gender via
    # is_male). _sm params apply to the male object, _sf to the female object; the shared
    # opportunity/wage params apply to both. Test each gender object against its own
    # applicable set — otherwise _sf params look "unbound" on a male object (harness error).
    def singles_male_applicable(name):
        if not singles_applicable(name):
            return False
        if name in _SINGLES_ONLY and name.endswith("_sf"):
            return False  # female-only leisure/occ does not bind on the male object
        return True
    def singles_female_applicable(name):
        if not singles_applicable(name):
            return False
        if name in _SINGLES_ONLY and name.endswith("_sm"):
            return False  # male-only leisure/occ does not bind on the female object
        return True

    sm = _mixed_year_singles_slice()
    print(f"\nsingles slice: {len(sm):,} rows, {sm['stacked_hh_uid'].nunique()} HH, "
          f"years={sorted(sm['data_year'].unique())}")
    d_sm = eu.precompute_data_singles(sm, _META, is_male=True, include_wage_vars=True, include_loc_vars=True)
    res_sm = analyse("singles-MALE (precompute_data_singles, is_male=True)", d_sm, spec,
                     ee.compute_likelihood_singles, singles_male_applicable)
    d_sf = eu.precompute_data_singles(sm, _META, is_male=False, include_wage_vars=True, include_loc_vars=True)
    res_sf = analyse("singles-FEMALE (precompute_data_singles, is_male=False)", d_sf, spec,
                     ee.compute_likelihood_singles, singles_female_applicable)

    cc = _mixed_year_couples_slice()
    print(f"\ncouples slice: {len(cc):,} rows, {cc['stacked_hh_uid'].nunique()} HH, "
          f"years={sorted(cc['data_year'].unique())}")
    d_c = eu.precompute_data_couples(cc, _META, include_wage_vars=True, include_loc_vars=True)
    res_c = analyse("couples (precompute_data_couples)", d_c, spec,
                    ee.compute_likelihood_couples, couples_applicable)

    # GATE
    print("\n" + "="*70)
    print("PHASE A GATE")
    print("="*70)
    fail = False
    for res in (res_sm, res_sf, res_c):
        nb = res["not_bound"]; sw = res["skip_warnings"]
        print(f"  {res['object']}: applicable bound={len(res['bound'])}, "
              f"not-bound={len(nb)}, skip-warnings={len(sw)}")
        if nb:
            print(f"     SILENT DROPS: {nb}")
            fail = True
        if sw:
            print(f"     WARNINGS: {sw}")
            fail = True
    # explicit at-risk confirmation
    atrisk = ["beta_E_drgur","beta_E_drgmd","beta_E_y2015","beta_E_y2017","beta_h_lh",
              "beta_E_gsur","beta_occ_2_cm","beta_occ_3_cf","theta_l_m","theta_l_f","theta_c_singles"]
    print("\n  At-risk param confirmation (couples object):")
    for p in atrisk:
        if p in _SINGLES_ONLY:
            continue
        status = "BOUND" if p in res_c["bound"] else ("N/A" if p in res_c["na"] else "NOT BOUND")
        print(f"    {p:16} {status}")
        if status == "NOT BOUND":
            fail = True

    print(f"\n  PHASE A: {'FAIL — do NOT proceed to Phase B' if fail else 'PASS — clear to proceed to Phase B'}")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
