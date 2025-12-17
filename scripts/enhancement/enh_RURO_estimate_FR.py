#!/usr/bin/env python
"""
Enhanced wrapper for RURO_estimate_FR (base unchanged)
-----------------------------------------------------
- Singles spec enriched: log age, child buckets, drgn1 dummies (Île-de-France ref=1),
  region interactions in hours/wage opp.
- Couples/joint remain on base spec for now.
- Normalization overrides preserved (--mean-dispy-norm, --mean-lhw-norm).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np

import scripts.RURO_estimate_FR as base

try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enhanced wrapper for RURO_estimate_FR with richer singles spec.",
        add_help=False,
    )
    parser.add_argument("--mean-dispy-norm", type=float, default=base.MEAN_DISPY_NORM)
    parser.add_argument("--mean-lhw-norm", type=float, default=base.MEAN_LHW_NORM)
    parser.add_argument("--country", type=str, default=None)
    parser.add_argument("--year", type=str, default=None)
    parser.add_argument("--use-region-dummies", action="store_true", default=True)
    parser.add_argument("--use-year-dummies", action="store_true", default=False)
    parser.add_argument(
        "--validate-gradient",
        action="store_true",
        help="Run a small numerical vs analytical gradient check on singles before full optimization.",
    )
    parser.add_argument(
        "--validate-gradient-couples",
        action="store_true",
        help="Run a small numerical vs analytical gradient check on couples before full optimization.",
    )
    parser.add_argument(
        "--validate-gradient-joint",
        action="store_true",
        help="Run a small numerical vs analytical gradient check on the joint objective (tiny subset).",
    )
    parser.add_argument(
        "--joint-n-jobs",
        type=int,
        default=1,
        help="Optional parallelization for joint gradient (joblib) if available.",
    )
    args, forward_args = parser.parse_known_args()

    # If user did not override normalization, try to load from meta adjacent to mnl-file
    mean_dispy = args.mean_dispy_norm
    mean_lhw = args.mean_lhw_norm
    years_present: List[int] = []

    # Locate mnl-file in forwarded args
    mnl_path: Path | None = None
    for i, tok in enumerate(forward_args):
        if tok == "--mnl-file" and i + 1 < len(forward_args):
            mnl_path = Path(forward_args[i + 1]).resolve()
            break
    # Attempt to read meta JSON
    if mnl_path is not None:
        meta_path = mnl_path.with_name(f"{mnl_path.stem}_meta.json")
        if meta_path.exists():
            try:
                meta = base.json.load(meta_path.open("r"))
                if mean_dispy == base.MEAN_DISPY_NORM and meta.get("mean_dispy_norm") is not None:
                    mean_dispy = float(meta["mean_dispy_norm"])
                if mean_lhw == base.MEAN_LHW_NORM and meta.get("mean_lhw_norm") is not None:
                    mean_lhw = float(meta["mean_lhw_norm"])
                if args.use_year_dummies and meta.get("years_present"):
                    years_present = [int(y) for y in meta["years_present"]]
            except Exception:
                pass
        # As a fallback, derive from parquet if still defaults
        if (mean_dispy == base.MEAN_DISPY_NORM or mean_lhw == base.MEAN_LHW_NORM) and mnl_path.exists():
            try:
                df_norm = base.pd.read_parquet(mnl_path)  # type: ignore[attr-defined]
                obs_mask = None
                if "is_chosen" in df_norm.columns:
                    obs_mask = df_norm["is_chosen"] == 1
                elif "draw" in df_norm.columns:
                    obs_mask = df_norm["draw"] == 0
                else:
                    obs_mask = base.np.ones(len(df_norm), dtype=bool)
                if mean_dispy == base.MEAN_DISPY_NORM:
                    if "ils_dispy" in df_norm.columns:
                        mean_dispy = base.pd.to_numeric(df_norm.loc[obs_mask, "ils_dispy"], errors="coerce").mean()
                    elif "dispy_util" in df_norm.columns:
                        mean_dispy = base.pd.to_numeric(df_norm.loc[obs_mask, "dispy_util"], errors="coerce").mean()
                if mean_lhw == base.MEAN_LHW_NORM:
                    if "lhw" in df_norm.columns:
                        mean_lhw = base.pd.to_numeric(df_norm.loc[obs_mask, "lhw"], errors="coerce").mean()
                    elif "hours" in df_norm.columns:
                        hrs = base.pd.to_numeric(df_norm.loc[obs_mask, "hours"], errors="coerce")
                        mean_lhw = hrs.mean()
                    elif "hours_male" in df_norm.columns and "hours_female" in df_norm.columns:
                        hrs_m = base.pd.to_numeric(df_norm.loc[obs_mask, "hours_male"], errors="coerce")
                        hrs_f = base.pd.to_numeric(df_norm.loc[obs_mask, "hours_female"], errors="coerce")
                        mean_lhw = base.np.nanmean(base.np.concatenate([hrs_m.values, hrs_f.values]))
                if args.use_year_dummies and not years_present and "year" in df_norm.columns:
                    years_present = sorted(int(y) for y in base.pd.to_numeric(df_norm["year"], errors="coerce").dropna().unique())
            except Exception:
                pass

    base.MEAN_DISPY_NORM = mean_dispy
    base.MEAN_LHW_NORM = mean_lhw

    use_region = args.use_region_dummies
    use_year = args.use_year_dummies

    REGION_CODES = list(range(2, 9)) if use_region else []
    YEAR_CODES: List[int] = []
    if use_year and years_present:
        ref_year = min(years_present)
        YEAR_CODES = [y for y in years_present if y != ref_year]

    @dataclass
    class PrecomputedDataSinglesEnh:
        c: np.ndarray
        l: np.ndarray
        log_age: np.ndarray
        log_age2: np.ndarray
        child0_3: np.ndarray
        child4_6: np.ndarray
        child7_9: np.ndarray
        educL: np.ndarray
        educH: np.ndarray
        working: np.ndarray
        working_pt1: np.ndarray
        working_pt2: np.ndarray
        working_ft: np.ndarray
        gsur: np.ndarray
        log_wage: np.ndarray
        pexp: np.ndarray
        pexp2: np.ndarray
        log_prior: np.ndarray
        group_idx: np.ndarray
        n_groups: int
        is_obs: np.ndarray
        group_starts: np.ndarray
        group_ends: np.ndarray
        obs_indices: np.ndarray
        region_matrix: np.ndarray
        year_matrix: np.ndarray

    def get_param_names_singles_enh(wage_spec: str = "fw") -> List[str]:
        names: List[str] = []
        names += [
            "pref.beta_l0",
            "pref.beta_l_log_age",
            "pref.beta_l_log_age2",
            "pref.beta_l_child0_3",
            "pref.beta_l_child4_6",
            "pref.beta_l_child7_9",
            "pref.beta_l_educL",
            "pref.beta_l_educH",
        ]
        for r in REGION_CODES:
            names.append(f"pref.beta_l_drgn1_{r}")
        for y in YEAR_CODES:
            names.append(f"pref.beta_l_year_{y}")
        names += ["pref.beta_c", "pref.theta_l", "pref.theta_c"]
        names += [
            "hopp.beta_work",
            "hopp.beta_pt1",
            "hopp.beta_pt2",
            "hopp.beta_ft",
            "hopp.beta_gsur",
            "hopp.beta_work_educL",
            "hopp.beta_work_educH",
        ]
        for r in REGION_CODES:
            names.append(f"hopp.beta_work_drgn1_{r}")
        for y in YEAR_CODES:
            names.append(f"hopp.beta_work_year_{y}")
        if wage_spec == "vw":
            names += [
                "wopp.beta0",
                "wopp.beta_educL",
                "wopp.beta_educH",
                "wopp.beta_pexp",
                "wopp.beta_pexp2",
                "wopp.sigma",
            ]
            for r in REGION_CODES:
                names.append(f"wopp.beta_drgn1_{r}")
            for y in YEAR_CODES:
                names.append(f"wopp.beta_year_{y}")
        return names

    def get_initial_theta_singles_enh(wage_spec: str = "fw") -> np.ndarray:
        theta: List[float] = [
            1.0, 0.0, 0.0,  # beta_l0, log_age, log_age2
            0.1, 0.1, 0.1,  # child0_3/4_6/7_9
            0.0, 0.0,       # educL/H
        ]
        theta += [0.0] * len(REGION_CODES)  # region
        theta += [0.0] * len(YEAR_CODES)    # year
        theta += [1.0, 0.5, 0.5]  # beta_c, theta_l, theta_c
        theta += [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # hours
        theta += [0.0] * len(REGION_CODES)  # hours×region
        theta += [0.0] * len(YEAR_CODES)    # hours×year
        if wage_spec == "vw":
            theta += [1.5, -0.2, 0.2, 0.05, -0.001, 0.5]  # wage
            theta += [0.0] * len(REGION_CODES)  # wage×region
            theta += [0.0] * len(YEAR_CODES)    # wage×year
        return np.array(theta, dtype=float)

    def precompute_data_singles_enh(df: base.pd.DataFrame, is_male: bool = True) -> PrecomputedDataSinglesEnh:
        n = len(df)

        def get(col: str, default: float = 0.0) -> np.ndarray:
            if col in df.columns:
                arr = base.pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
            else:
                arr = np.full(n, default)
            return np.ascontiguousarray(arr, dtype=np.float64)

        data_tmp = base.precompute_data_singles(df, is_male=is_male)
        c = data_tmp.c
        l = data_tmp.l

        dag = get("dag", 1.0)
        dag = np.clip(dag, 1e-6, None)
        log_age = np.log(dag)
        log_age2 = log_age * log_age

        child0_3 = get("children0_3")
        child4_6 = get("children4_6")
        child7_9 = get("children7_9")

        if REGION_CODES and "drgn1" in df.columns:
            dr = base.pd.to_numeric(df["drgn1"], errors="coerce").fillna(0).astype(int).to_numpy()
        else:
            dr = np.zeros(n, dtype=int)
        region_mat = np.zeros((n, len(REGION_CODES)), dtype=np.float64)
        for idx, r in enumerate(REGION_CODES):
            region_mat[:, idx] = (dr == r).astype(np.float64)

        # year matrix
        if YEAR_CODES and "year" in df.columns:
            yr = base.pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int).to_numpy()
        else:
            yr = np.zeros(n, dtype=int)
        year_mat = np.zeros((n, len(YEAR_CODES)), dtype=np.float64)
        for idx, y in enumerate(YEAR_CODES):
            year_mat[:, idx] = (yr == y).astype(np.float64)

        # year matrix (reference = min observed if present)
        if YEAR_CODES and "year" in df.columns:
            yr = base.pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int).to_numpy()
        else:
            yr = np.zeros(n, dtype=int)
        year_mat = np.zeros((n, len(YEAR_CODES)), dtype=np.float64)
        for idx, y in enumerate(YEAR_CODES):
            year_mat[:, idx] = (yr == y).astype(np.float64)

        return PrecomputedDataSinglesEnh(
            c=c,
            l=l,
            log_age=log_age,
            log_age2=log_age2,
            child0_3=child0_3,
            child4_6=child4_6,
            child7_9=child7_9,
            educL=data_tmp.educL,
            educH=data_tmp.educH,
            working=data_tmp.working,
            working_pt1=data_tmp.working_pt1,
            working_pt2=data_tmp.working_pt2,
            working_ft=data_tmp.working_ft,
            gsur=data_tmp.gsur,
            log_wage=data_tmp.log_wage,
            pexp=data_tmp.pexp,
            pexp2=data_tmp.pexp2,
            log_prior=data_tmp.log_prior,
            group_idx=data_tmp.group_idx,
            n_groups=data_tmp.n_groups,
            is_obs=data_tmp.is_obs,
            group_starts=data_tmp.group_starts,
            group_ends=data_tmp.group_ends,
            obs_indices=data_tmp.obs_indices,
            region_matrix=region_mat,
            year_matrix=year_mat,
        )

    def fast_log_likelihood_singles_enh(theta: np.ndarray, data: PrecomputedDataSinglesEnh, wage_spec: str = "fw") -> float:
        idx = 0
        beta_l0 = theta[idx]; idx += 1
        beta_l_log_age = theta[idx]; idx += 1
        beta_l_log_age2 = theta[idx]; idx += 1
        beta_l_c0 = theta[idx]; idx += 1
        beta_l_c1 = theta[idx]; idx += 1
        beta_l_c2 = theta[idx]; idx += 1
        beta_l_educL = theta[idx]; idx += 1
        beta_l_educH = theta[idx]; idx += 1
        beta_l_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_l_year = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)
        beta_c = theta[idx]; idx += 1
        theta_l = theta[idx]; idx += 1
        theta_c = theta[idx]; idx += 1

        beta_work = theta[idx]; idx += 1
        beta_pt1 = theta[idx]; idx += 1
        beta_pt2 = theta[idx]; idx += 1
        beta_ft = theta[idx]; idx += 1
        beta_gsur = theta[idx]; idx += 1
        beta_work_educL = theta[idx]; idx += 1
        beta_work_educH = theta[idx]; idx += 1
        beta_work_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_work_year = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)

        if wage_spec == "vw":
            w_beta0 = theta[idx]; idx += 1
            w_educL = theta[idx]; idx += 1
            w_educH = theta[idx]; idx += 1
            w_pexp = theta[idx]; idx += 1
            w_pexp2 = theta[idx]; idx += 1
            sigma = abs(theta[idx]) + 1e-6; idx += 1
            w_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
            w_year = theta[idx:idx+len(YEAR_CODES)]
        else:
            w_beta0 = w_educL = w_educH = w_pexp = w_pexp2 = sigma = 0.0
            w_region = np.zeros(len(REGION_CODES))
            w_year = np.zeros(len(YEAR_CODES))

        l_bc = base._fast_boxcox(data.l, theta_l)
        c_bc = base._fast_boxcox(data.c, theta_c)
        beta_leisure = (
            beta_l0
            + beta_l_log_age * data.log_age
            + beta_l_log_age2 * data.log_age2
            + beta_l_c0 * data.child0_3
            + beta_l_c1 * data.child4_6
            + beta_l_c2 * data.child7_9
            + beta_l_educL * data.educL
            + beta_l_educH * data.educH
            + data.region_matrix.dot(beta_l_region)
            + data.year_matrix.dot(beta_l_year)
        )
        u = beta_leisure * l_bc + beta_c * c_bc

        h_opp = (
            beta_work * data.working
            + beta_pt1 * data.working_pt1
            + beta_pt2 * data.working_pt2
            + beta_ft * data.working_ft
            + beta_gsur * data.working * data.gsur
            + beta_work_educL * data.working * data.educL
            + beta_work_educH * data.working * data.educH
            + (data.working[:, None] * data.region_matrix).dot(beta_work_region)
            + (data.working[:, None] * data.year_matrix).dot(beta_work_year)
        )

        if wage_spec == "vw":
            mean_logw = (
                w_beta0
                + w_educL * data.educL + w_educH * data.educH
                + w_pexp * data.pexp + w_pexp2 * data.pexp2
                + data.region_matrix.dot(w_region)
                + data.year_matrix.dot(w_year)
            )
            z = (data.log_wage - mean_logw) / sigma
            w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        else:
            w_opp = 0.0

        V = u + h_opp + w_opp - data.log_prior
        V_max_per_group = np.maximum.reduceat(V, data.group_starts)
        V_max = V_max_per_group[data.group_idx]
        exp_V_shifted = np.exp(V - V_max)
        sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
        log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
        V_obs = V[data.obs_indices]
        ll = np.sum(V_obs - log_sum_exp_per_group)
        return ll

    def fast_analytical_gradient_singles_enh(theta: np.ndarray, data: PrecomputedDataSinglesEnh, wage_spec: str = "fw") -> np.ndarray:
        n = len(data.c)
        n_params = len(theta)
        grad = np.zeros(n_params, dtype=float)

        idx = 0
        beta_l0 = theta[idx]; idx += 1
        beta_l_log_age = theta[idx]; idx += 1
        beta_l_log_age2 = theta[idx]; idx += 1
        beta_l_c0 = theta[idx]; idx += 1
        beta_l_c1 = theta[idx]; idx += 1
        beta_l_c2 = theta[idx]; idx += 1
        beta_l_educL = theta[idx]; idx += 1
        beta_l_educH = theta[idx]; idx += 1
        beta_l_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_c = theta[idx]; idx += 1
        theta_l = theta[idx]; idx += 1
        theta_c = theta[idx]; idx += 1

        beta_work = theta[idx]; idx += 1
        beta_pt1 = theta[idx]; idx += 1
        beta_pt2 = theta[idx]; idx += 1
        beta_ft = theta[idx]; idx += 1
        beta_gsur = theta[idx]; idx += 1
        beta_work_educL = theta[idx]; idx += 1
        beta_work_educH = theta[idx]; idx += 1
        beta_work_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)

        if wage_spec == "vw":
            w_beta0 = theta[idx]; idx += 1
            w_educL = theta[idx]; idx += 1
            w_educH = theta[idx]; idx += 1
            w_pexp = theta[idx]; idx += 1
            w_pexp2 = theta[idx]; idx += 1
            sigma = abs(theta[idx]) + 1e-6; idx += 1
            w_region = theta[idx:idx+len(REGION_CODES)]
        else:
            w_beta0 = w_educL = w_educH = w_pexp = w_pexp2 = sigma = 0.0
            w_region = np.zeros(len(REGION_CODES))

        l_bc = base._fast_boxcox(data.l, theta_l)
        c_bc = base._fast_boxcox(data.c, theta_c)
        dl_bc_dtheta_l = base._fast_d_boxcox_dtheta(data.l, theta_l)
        dc_bc_dtheta_c = base._fast_d_boxcox_dtheta(data.c, theta_c)

        beta_leisure = (
            beta_l0
            + beta_l_log_age * data.log_age
            + beta_l_log_age2 * data.log_age2
            + beta_l_c0 * data.child0_3
            + beta_l_c1 * data.child4_6
            + beta_l_c2 * data.child7_9
            + beta_l_educL * data.educL
            + beta_l_educH * data.educH
            + data.region_matrix.dot(beta_l_region)
        )
        u = beta_leisure * l_bc + beta_c * c_bc

        h_opp = (
            beta_work * data.working
            + beta_pt1 * data.working_pt1
            + beta_pt2 * data.working_pt2
            + beta_ft * data.working_ft
            + beta_gsur * data.working * data.gsur
            + beta_work_educL * data.working * data.educL
            + beta_work_educH * data.working * data.educH
            + (data.working[:, None] * data.region_matrix).dot(beta_work_region)
        )

        if wage_spec == "vw":
            mean_logw = (
                w_beta0
                + w_educL * data.educL + w_educH * data.educH
                + w_pexp * data.pexp + w_pexp2 * data.pexp2
                + data.region_matrix.dot(w_region)
            )
            z = (data.log_wage - mean_logw) / sigma
            w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
            z_s = z / sigma
        else:
            w_opp = 0.0
            z_s = None

        V = u + h_opp + w_opp - data.log_prior
        V_max_per_group = np.maximum.reduceat(V, data.group_starts)
        V_max = V_max_per_group[data.group_idx]
        exp_V = np.exp(V - V_max)
        sum_exp = np.bincount(data.group_idx, weights=exp_V, minlength=data.n_groups)
        P = exp_V / sum_exp[data.group_idx]

        dV = np.zeros((n, n_params), dtype=float)
        idx = 0
        dV[:, idx] = l_bc; idx += 1
        dV[:, idx] = data.log_age * l_bc; idx += 1
        dV[:, idx] = data.log_age2 * l_bc; idx += 1
        dV[:, idx] = data.child0_3 * l_bc; idx += 1
        dV[:, idx] = data.child4_6 * l_bc; idx += 1
        dV[:, idx] = data.child7_9 * l_bc; idx += 1
        dV[:, idx] = data.educL * l_bc; idx += 1
        dV[:, idx] = data.educH * l_bc; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.region_matrix[:, k] * l_bc
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.year_matrix[:, k] * l_bc
        idx += len(YEAR_CODES)
        dV[:, idx] = c_bc; idx += 1
        dV[:, idx] = beta_leisure * dl_bc_dtheta_l; idx += 1
        dV[:, idx] = beta_c * dc_bc_dtheta_c; idx += 1

        dV[:, idx] = data.working; idx += 1
        dV[:, idx] = data.working_pt1; idx += 1
        dV[:, idx] = data.working_pt2; idx += 1
        dV[:, idx] = data.working_ft; idx += 1
        dV[:, idx] = data.working * data.gsur; idx += 1
        dV[:, idx] = data.working * data.educL; idx += 1
        dV[:, idx] = data.working * data.educH; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.working * data.region_matrix[:, k]
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.working * data.year_matrix[:, k]
        idx += len(YEAR_CODES)

        if wage_spec == "vw" and z_s is not None:
            dV[:, idx] = np.where(data.working > 0, z_s, 0.0); idx += 1
            dV[:, idx] = np.where(data.working > 0, z_s * data.educL, 0.0); idx += 1
            dV[:, idx] = np.where(data.working > 0, z_s * data.educH, 0.0); idx += 1
            dV[:, idx] = np.where(data.working > 0, z_s * data.pexp, 0.0); idx += 1
            dV[:, idx] = np.where(data.working > 0, z_s * data.pexp2, 0.0); idx += 1
            dV[:, idx] = np.where(data.working > 0, (z * z - 1.0) / sigma, 0.0); idx += 1
            for k in range(len(REGION_CODES)):
                dV[:, idx + k] = np.where(data.working > 0, z_s * data.region_matrix[:, k], 0.0)
            idx += len(REGION_CODES)
            for k in range(len(YEAR_CODES)):
                dV[:, idx + k] = np.where(data.working > 0, z_s * data.year_matrix[:, k], 0.0)
            idx += len(YEAR_CODES)

        P_dV = P[:, None] * dV
        E_dV = np.zeros((data.n_groups, n_params), dtype=float)
        for k in range(n_params):
            E_dV[:, k] = np.bincount(data.group_idx, weights=P_dV[:, k], minlength=data.n_groups)

        grad = (dV[data.is_obs, :] - E_dV[data.group_idx[data.is_obs], :]).sum(axis=0)
        return grad

    base.get_param_names_singles = get_param_names_singles_enh
    base.get_initial_theta_singles = get_initial_theta_singles_enh
    base.precompute_data_singles = precompute_data_singles_enh
    base.fast_log_likelihood_singles = fast_log_likelihood_singles_enh
    base.fast_analytical_gradient_singles = fast_analytical_gradient_singles_enh

    # ------------------------------------------------------------------
    # Enhanced couples specification (log age, child buckets, drgn1 dummies)
    # ------------------------------------------------------------------
    @dataclass
    class PrecomputedDataCouplesEnh:
        c: np.ndarray
        l_male: np.ndarray
        l_female: np.ndarray
        log_age_m: np.ndarray
        log_age2_m: np.ndarray
        log_age_f: np.ndarray
        log_age2_f: np.ndarray
        child0_3: np.ndarray
        child4_6: np.ndarray
        child7_9: np.ndarray
        educL_m: np.ndarray
        educH_m: np.ndarray
        educL_f: np.ndarray
        educH_f: np.ndarray
        working_male: np.ndarray
        working_pt1_male: np.ndarray
        working_pt2_male: np.ndarray
        working_ft_male: np.ndarray
        gsur_male: np.ndarray
        working_female: np.ndarray
        working_pt1_female: np.ndarray
        working_pt2_female: np.ndarray
        working_ft_female: np.ndarray
        gsur_female: np.ndarray
        log_wage_m: np.ndarray
        pexp_male: np.ndarray
        pexp2_male: np.ndarray
        log_wage_f: np.ndarray
        pexp_female: np.ndarray
        pexp2_female: np.ndarray
        log_prior: np.ndarray
        group_idx: np.ndarray
        n_groups: int
        is_obs: np.ndarray
        group_starts: np.ndarray
        group_ends: np.ndarray
        obs_indices: np.ndarray
        region_matrix: np.ndarray
        year_matrix: np.ndarray

    def get_param_names_couples_enh(wage_spec: str = "fw") -> List[str]:
        names: List[str] = []
        # Male prefs
        names += [
            "pref.beta_lm0",
            "pref.beta_lm_log_age",
            "pref.beta_lm_log_age2",
            "pref.beta_lm_child0_3",
            "pref.beta_lm_child4_6",
            "pref.beta_lm_child7_9",
            "pref.beta_lm_educL",
            "pref.beta_lm_educH",
        ]
        for r in REGION_CODES:
            names.append(f"pref.beta_lm_drgn1_{r}")
        for y in YEAR_CODES:
            names.append(f"pref.beta_lm_year_{y}")
        # Female prefs
        names += [
            "pref.beta_lf0",
            "pref.beta_lf_log_age",
            "pref.beta_lf_log_age2",
            "pref.beta_lf_child0_3",
            "pref.beta_lf_child4_6",
            "pref.beta_lf_child7_9",
            "pref.beta_lf_educL",
            "pref.beta_lf_educH",
        ]
        for r in REGION_CODES:
            names.append(f"pref.beta_lf_drgn1_{r}")
        for y in YEAR_CODES:
            names.append(f"pref.beta_lf_year_{y}")
        # Shared
        names += ["pref.beta_c", "pref.theta_lm", "pref.theta_lf", "pref.theta_c", "pref.beta_interact"]
        # Hours male
        names += [
            "hopp.beta_work_m",
            "hopp.beta_pt1_m",
            "hopp.beta_pt2_m",
            "hopp.beta_ft_m",
            "hopp.beta_gsur_m",
            "hopp.beta_work_educL_m",
            "hopp.beta_work_educH_m",
        ]
        for r in REGION_CODES:
            names.append(f"hopp.beta_work_drgn1_m_{r}")
        for y in YEAR_CODES:
            names.append(f"hopp.beta_work_year_m_{y}")
        # Hours female
        names += [
            "hopp.beta_work_f",
            "hopp.beta_pt1_f",
            "hopp.beta_pt2_f",
            "hopp.beta_ft_f",
            "hopp.beta_gsur_f",
            "hopp.beta_work_educL_f",
            "hopp.beta_work_educH_f",
        ]
        for r in REGION_CODES:
            names.append(f"hopp.beta_work_drgn1_f_{r}")
        for y in YEAR_CODES:
            names.append(f"hopp.beta_work_year_f_{y}")
        if wage_spec == "vw":
            # Wage male
            names += [
                "wopp.beta0_m",
                "wopp.beta_educL_m",
                "wopp.beta_educH_m",
                "wopp.beta_pexp_m",
                "wopp.beta_pexp2_m",
                "wopp.sigma_m",
            ]
            for r in REGION_CODES:
                names.append(f"wopp.beta_drgn1_m_{r}")
            for y in YEAR_CODES:
                names.append(f"wopp.beta_year_m_{y}")
            # Wage female
            names += [
                "wopp.beta0_f",
                "wopp.beta_educL_f",
                "wopp.beta_educH_f",
                "wopp.beta_pexp_f",
                "wopp.beta_pexp2_f",
                "wopp.sigma_f",
            ]
            for r in REGION_CODES:
                names.append(f"wopp.beta_drgn1_f_{r}")
            for y in YEAR_CODES:
                names.append(f"wopp.beta_year_f_{y}")
        return names

    def get_initial_theta_couples_enh(wage_spec: str = "fw") -> np.ndarray:
        theta: List[float] = []
        # Male prefs
        theta += [1.0, 0.0, 0.0, 0.1, 0.1, 0.1, 0.0, 0.0]
        theta += [0.0] * len(REGION_CODES)
        theta += [0.0] * len(YEAR_CODES)
        # Female prefs
        theta += [1.0, 0.0, 0.0, 0.1, 0.1, 0.1, 0.0, 0.0]
        theta += [0.0] * len(REGION_CODES)
        theta += [0.0] * len(YEAR_CODES)
        # Shared
        theta += [1.0, 0.5, 0.5, 0.5, 0.1]  # beta_c, theta_lm, theta_lf, theta_c, beta_interact
        # Hours male
        theta += [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        theta += [0.0] * len(REGION_CODES)
        theta += [0.0] * len(YEAR_CODES)
        # Hours female
        theta += [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        theta += [0.0] * len(REGION_CODES)
        theta += [0.0] * len(YEAR_CODES)
        if wage_spec == "vw":
            theta += [1.5, -0.2, 0.2, 0.05, -0.001, 0.5]
            theta += [0.0] * len(REGION_CODES)
            theta += [0.0] * len(YEAR_CODES)
            theta += [1.5, -0.2, 0.2, 0.05, -0.001, 0.5]
            theta += [0.0] * len(REGION_CODES)
            theta += [0.0] * len(YEAR_CODES)
        return np.array(theta, dtype=float)

    def precompute_data_couples_enh(df: base.pd.DataFrame) -> PrecomputedDataCouplesEnh:
        n = len(df)

        def get(col: str, default: float = 0.0) -> np.ndarray:
            if col in df.columns:
                arr = base.pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
            else:
                arr = np.full(n, default)
            return np.ascontiguousarray(arr, dtype=np.float64)

        data_tmp = base.precompute_data_couples(df)

        dag_m = get("dag_m", 1.0)
        dag_f = get("dag_f", 1.0)
        dag_m = np.clip(dag_m, 1e-6, None)
        dag_f = np.clip(dag_f, 1e-6, None)
        log_age_m = np.log(dag_m)
        log_age2_m = log_age_m * log_age_m
        log_age_f = np.log(dag_f)
        log_age2_f = log_age_f * log_age_f

        child0_3 = get("children0_3")
        child4_6 = get("children4_6")
        child7_9 = get("children7_9")

        if REGION_CODES and "drgn1" in df.columns:
            dr = base.pd.to_numeric(df["drgn1"], errors="coerce").fillna(0).astype(int).to_numpy()
        else:
            dr = np.zeros(n, dtype=int)
        region_mat = np.zeros((n, len(REGION_CODES)), dtype=np.float64)
        for idx, r in enumerate(REGION_CODES):
            region_mat[:, idx] = (dr == r).astype(np.float64)

        return PrecomputedDataCouplesEnh(
            c=data_tmp.c,
            l_male=data_tmp.l_male,
            l_female=data_tmp.l_female,
            log_age_m=log_age_m,
            log_age2_m=log_age2_m,
            log_age_f=log_age_f,
            log_age2_f=log_age2_f,
            child0_3=child0_3,
            child4_6=child4_6,
            child7_9=child7_9,
            educL_m=data_tmp.educL_male,
            educH_m=data_tmp.educH_male,
            educL_f=data_tmp.educL_female,
            educH_f=data_tmp.educH_female,
            working_male=data_tmp.working_male,
            working_pt1_male=data_tmp.working_pt1_male,
            working_pt2_male=data_tmp.working_pt2_male,
            working_ft_male=data_tmp.working_ft_male,
            gsur_male=data_tmp.gsur_male,
            working_female=data_tmp.working_female,
            working_pt1_female=data_tmp.working_pt1_female,
            working_pt2_female=data_tmp.working_pt2_female,
            working_ft_female=data_tmp.working_ft_female,
            gsur_female=data_tmp.gsur_female,
            log_wage_m=data_tmp.log_wage_m,
            pexp_male=data_tmp.pexp_male,
            pexp2_male=data_tmp.pexp2_male,
            log_wage_f=data_tmp.log_wage_f,
            pexp_female=data_tmp.pexp_female,
            pexp2_female=data_tmp.pexp2_female,
            log_prior=data_tmp.log_prior,
            group_idx=data_tmp.group_idx,
            n_groups=data_tmp.n_groups,
            is_obs=data_tmp.is_obs,
            group_starts=data_tmp.group_starts,
            group_ends=data_tmp.group_ends,
            obs_indices=data_tmp.obs_indices,
            region_matrix=region_mat,
            year_matrix=year_mat,
        )

    def fast_neg_ll_with_grad_couples_enh(theta: np.ndarray, data: PrecomputedDataCouplesEnh, wage_spec: str = "fw") -> Tuple[float, np.ndarray]:
        n_params = len(theta)
        n = len(data.c)

        idx = 0
        # Male prefs
        beta_lm0 = theta[idx]; idx += 1
        beta_lm_log_age = theta[idx]; idx += 1
        beta_lm_log_age2 = theta[idx]; idx += 1
        beta_lm_c0 = theta[idx]; idx += 1
        beta_lm_c1 = theta[idx]; idx += 1
        beta_lm_c2 = theta[idx]; idx += 1
        beta_lm_educL = theta[idx]; idx += 1
        beta_lm_educH = theta[idx]; idx += 1
        beta_lm_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_lm_year = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)
        # Female prefs
        beta_lf0 = theta[idx]; idx += 1
        beta_lf_log_age = theta[idx]; idx += 1
        beta_lf_log_age2 = theta[idx]; idx += 1
        beta_lf_c0 = theta[idx]; idx += 1
        beta_lf_c1 = theta[idx]; idx += 1
        beta_lf_c2 = theta[idx]; idx += 1
        beta_lf_educL = theta[idx]; idx += 1
        beta_lf_educH = theta[idx]; idx += 1
        beta_lf_region = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_lf_year = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)
        # Shared
        beta_c = theta[idx]; idx += 1
        theta_lm = theta[idx]; idx += 1
        theta_lf = theta[idx]; idx += 1
        theta_c = theta[idx]; idx += 1
        beta_interact = theta[idx]; idx += 1

        # Hours male
        beta_work_m = theta[idx]; idx += 1
        beta_pt1_m = theta[idx]; idx += 1
        beta_pt2_m = theta[idx]; idx += 1
        beta_ft_m = theta[idx]; idx += 1
        beta_gsur_m = theta[idx]; idx += 1
        beta_work_educL_m = theta[idx]; idx += 1
        beta_work_educH_m = theta[idx]; idx += 1
        beta_work_region_m = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_work_year_m = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)
        # Hours female
        beta_work_f = theta[idx]; idx += 1
        beta_pt1_f = theta[idx]; idx += 1
        beta_pt2_f = theta[idx]; idx += 1
        beta_ft_f = theta[idx]; idx += 1
        beta_gsur_f = theta[idx]; idx += 1
        beta_work_educL_f = theta[idx]; idx += 1
        beta_work_educH_f = theta[idx]; idx += 1
        beta_work_region_f = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
        beta_work_year_f = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)

        if wage_spec == "vw":
            w_beta0_m = theta[idx]; idx += 1
            w_educL_m = theta[idx]; idx += 1
            w_educH_m = theta[idx]; idx += 1
            w_pexp_m = theta[idx]; idx += 1
            w_pexp2_m = theta[idx]; idx += 1
            sigma_m = abs(theta[idx]) + 1e-6; idx += 1
            w_region_m = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
            w_year_m = theta[idx:idx+len(YEAR_CODES)]; idx += len(YEAR_CODES)

            w_beta0_f = theta[idx]; idx += 1
            w_educL_f = theta[idx]; idx += 1
            w_educH_f = theta[idx]; idx += 1
            w_pexp_f = theta[idx]; idx += 1
            w_pexp2_f = theta[idx]; idx += 1
            sigma_f = abs(theta[idx]) + 1e-6; idx += 1
            w_region_f = theta[idx:idx+len(REGION_CODES)]; idx += len(REGION_CODES)
            w_year_f = theta[idx:idx+len(YEAR_CODES)]
        else:
            w_beta0_m = w_educL_m = w_educH_m = w_pexp_m = w_pexp2_m = sigma_m = 0.0
            w_region_m = np.zeros(len(REGION_CODES))
            w_year_m = np.zeros(len(YEAR_CODES))
            w_beta0_f = w_educL_f = w_educH_f = w_pexp_f = w_pexp2_f = sigma_f = 0.0
            w_region_f = np.zeros(len(REGION_CODES))
            w_year_f = np.zeros(len(YEAR_CODES))

        lm_bc = base._fast_boxcox(data.l_male, theta_lm)
        lf_bc = base._fast_boxcox(data.l_female, theta_lf)
        c_bc = base._fast_boxcox(data.c, theta_c)
        dlm_bc = base._fast_d_boxcox_dtheta(data.l_male, theta_lm)
        dlf_bc = base._fast_d_boxcox_dtheta(data.l_female, theta_lf)
        dc_bc = base._fast_d_boxcox_dtheta(data.c, theta_c)

        beta_lm = (
            beta_lm0
            + beta_lm_log_age * data.log_age_m
            + beta_lm_log_age2 * data.log_age2_m
            + beta_lm_c0 * data.child0_3
            + beta_lm_c1 * data.child4_6
            + beta_lm_c2 * data.child7_9
            + beta_lm_educL * data.educL_m
            + beta_lm_educH * data.educH_m
            + data.region_matrix.dot(beta_lm_region)
            + data.year_matrix.dot(beta_lm_year)
        )
        beta_lf = (
            beta_lf0
            + beta_lf_log_age * data.log_age_f
            + beta_lf_log_age2 * data.log_age2_f
            + beta_lf_c0 * data.child0_3
            + beta_lf_c1 * data.child4_6
            + beta_lf_c2 * data.child7_9
            + beta_lf_educL * data.educL_f
            + beta_lf_educH * data.educH_f
            + data.region_matrix.dot(beta_lf_region)
            + data.year_matrix.dot(beta_lf_year)
        )

        u = beta_lm * lm_bc + beta_lf * lf_bc + beta_c * c_bc + beta_interact * (lm_bc * lf_bc)

        h_opp_m = (
            beta_work_m * data.working_male
            + beta_pt1_m * data.working_pt1_male
            + beta_pt2_m * data.working_pt2_male
            + beta_ft_m * data.working_ft_male
            + beta_gsur_m * data.working_male * data.gsur_male
            + beta_work_educL_m * data.working_male * data.educL_m
            + beta_work_educH_m * data.working_male * data.educH_m
            + (data.working_male[:, None] * data.region_matrix).dot(beta_work_region_m)
            + (data.working_male[:, None] * data.year_matrix).dot(beta_work_year_m)
        )
        h_opp_f = (
            beta_work_f * data.working_female
            + beta_pt1_f * data.working_pt1_female
            + beta_pt2_f * data.working_pt2_female
            + beta_ft_f * data.working_ft_female
            + beta_gsur_f * data.working_female * data.gsur_female
            + beta_work_educL_f * data.working_female * data.educL_f
            + beta_work_educH_f * data.working_female * data.educH_f
            + (data.working_female[:, None] * data.region_matrix).dot(beta_work_region_f)
            + (data.working_female[:, None] * data.year_matrix).dot(beta_work_year_f)
        )
        h_opp = h_opp_m + h_opp_f

        if wage_spec == "vw":
            mean_logw_m = (
                w_beta0_m
                + w_educL_m * data.educL_m
                + w_educH_m * data.educH_m
                + w_pexp_m * data.pexp_male
                + w_pexp2_m * data.pexp2_male
                + data.region_matrix.dot(w_region_m)
                + data.year_matrix.dot(w_year_m)
            )
            z_m = (data.log_wage_m - mean_logw_m) / sigma_m
            w_opp_m = np.where(data.working_male > 0, -0.5 * z_m * z_m - np.log(sigma_m) - data.log_wage_m, 0.0)

            mean_logw_f = (
                w_beta0_f
                + w_educL_f * data.educL_f
                + w_educH_f * data.educH_f
                + w_pexp_f * data.pexp_female
                + w_pexp2_f * data.pexp2_female
                + data.region_matrix.dot(w_region_f)
                + data.year_matrix.dot(w_year_f)
            )
            z_f = (data.log_wage_f - mean_logw_f) / sigma_f
            w_opp_f = np.where(data.working_female > 0, -0.5 * z_f * z_f - np.log(sigma_f) - data.log_wage_f, 0.0)
            w_opp = w_opp_m + w_opp_f
        else:
            w_opp = 0.0
            z_m = z_f = None

        V = u + h_opp + w_opp - data.log_prior
        V_max_per_group = np.maximum.reduceat(V, data.group_starts)
        V_max = V_max_per_group[data.group_idx]
        exp_V = np.exp(V - V_max)
        sum_exp = np.bincount(data.group_idx, weights=exp_V, minlength=data.n_groups)
        log_sum_exp = V_max_per_group + np.log(sum_exp)
        ll = np.sum(V[data.obs_indices] - log_sum_exp)

        # Gradient
        dV = np.zeros((n, n_params), dtype=float)
        idx = 0
        dV[:, idx] = lm_bc; idx += 1
        dV[:, idx] = data.log_age_m * lm_bc; idx += 1
        dV[:, idx] = data.log_age2_m * lm_bc; idx += 1
        dV[:, idx] = data.child0_3 * lm_bc; idx += 1
        dV[:, idx] = data.child4_6 * lm_bc; idx += 1
        dV[:, idx] = data.child7_9 * lm_bc; idx += 1
        dV[:, idx] = data.educL_m * lm_bc; idx += 1
        dV[:, idx] = data.educH_m * lm_bc; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.region_matrix[:, k] * lm_bc
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.year_matrix[:, k] * lm_bc
        idx += len(YEAR_CODES)

        dV[:, idx] = lf_bc; idx += 1
        dV[:, idx] = data.log_age_f * lf_bc; idx += 1
        dV[:, idx] = data.log_age2_f * lf_bc; idx += 1
        dV[:, idx] = data.child0_3 * lf_bc; idx += 1
        dV[:, idx] = data.child4_6 * lf_bc; idx += 1
        dV[:, idx] = data.child7_9 * lf_bc; idx += 1
        dV[:, idx] = data.educL_f * lf_bc; idx += 1
        dV[:, idx] = data.educH_f * lf_bc; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.region_matrix[:, k] * lf_bc
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.year_matrix[:, k] * lf_bc
        idx += len(YEAR_CODES)

        dV[:, idx] = c_bc; idx += 1
        dV[:, idx] = beta_lm * dlm_bc; idx += 1
        dV[:, idx] = beta_lf * dlf_bc; idx += 1
        dV[:, idx] = beta_c * dc_bc; idx += 1
        dV[:, idx] = lm_bc * lf_bc; idx += 1

        # Hours male
        dV[:, idx] = data.working_male; idx += 1
        dV[:, idx] = data.working_pt1_male; idx += 1
        dV[:, idx] = data.working_pt2_male; idx += 1
        dV[:, idx] = data.working_ft_male; idx += 1
        dV[:, idx] = data.working_male * data.gsur_male; idx += 1
        dV[:, idx] = data.working_male * data.educL_m; idx += 1
        dV[:, idx] = data.working_male * data.educH_m; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.working_male * data.region_matrix[:, k]
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.working_male * data.year_matrix[:, k]
        idx += len(YEAR_CODES)

        # Hours female
        dV[:, idx] = data.working_female; idx += 1
        dV[:, idx] = data.working_pt1_female; idx += 1
        dV[:, idx] = data.working_pt2_female; idx += 1
        dV[:, idx] = data.working_ft_female; idx += 1
        dV[:, idx] = data.working_female * data.gsur_female; idx += 1
        dV[:, idx] = data.working_female * data.educL_f; idx += 1
        dV[:, idx] = data.working_female * data.educH_f; idx += 1
        for k in range(len(REGION_CODES)):
            dV[:, idx + k] = data.working_female * data.region_matrix[:, k]
        idx += len(REGION_CODES)
        for k in range(len(YEAR_CODES)):
            dV[:, idx + k] = data.working_female * data.year_matrix[:, k]
        idx += len(YEAR_CODES)

        if wage_spec == "vw" and z_m is not None and z_f is not None:
            z_s_m = z_m / sigma_m
            z_s_f = z_f / sigma_f
            dV[:, idx] = np.where(data.working_male > 0, z_s_m, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_male > 0, z_s_m * data.educL_m, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_male > 0, z_s_m * data.educH_m, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_male > 0, z_s_m * data.pexp_male, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_male > 0, z_s_m * data.pexp2_male, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_male > 0, (z_m * z_m - 1.0) / sigma_m, 0.0); idx += 1
            for k in range(len(REGION_CODES)):
                dV[:, idx + k] = np.where(data.working_male > 0, z_s_m * data.region_matrix[:, k], 0.0)
            idx += len(REGION_CODES)
            for k in range(len(YEAR_CODES)):
                dV[:, idx + k] = np.where(data.working_male > 0, z_s_m * data.year_matrix[:, k], 0.0)
            idx += len(YEAR_CODES)

            dV[:, idx] = np.where(data.working_female > 0, z_s_f, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_female > 0, z_s_f * data.educL_f, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_female > 0, z_s_f * data.educH_f, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_female > 0, z_s_f * data.pexp_female, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_female > 0, z_s_f * data.pexp2_female, 0.0); idx += 1
            dV[:, idx] = np.where(data.working_female > 0, (z_f * z_f - 1.0) / sigma_f, 0.0); idx += 1
            for k in range(len(REGION_CODES)):
                dV[:, idx + k] = np.where(data.working_female > 0, z_s_f * data.region_matrix[:, k], 0.0)
            idx += len(REGION_CODES)
            for k in range(len(YEAR_CODES)):
                dV[:, idx + k] = np.where(data.working_female > 0, z_s_f * data.year_matrix[:, k], 0.0)
            idx += len(YEAR_CODES)

        P = exp_V / sum_exp[data.group_idx]
        P_dV = P[:, None] * dV
        E_dV = np.zeros((data.n_groups, n_params), dtype=float)
        for k in range(n_params):
            E_dV[:, k] = np.bincount(data.group_idx, weights=P_dV[:, k], minlength=data.n_groups)
        grad = (dV[data.is_obs, :] - E_dV[data.group_idx[data.is_obs], :]).sum(axis=0)
        return -ll, -grad

    base.precompute_data_couples = precompute_data_couples_enh
    base.get_param_names_couples = get_param_names_couples_enh
    base.get_initial_theta_couples = get_initial_theta_couples_enh
    base.fast_log_likelihood_couples = lambda t, d, wage_spec="fw": -fast_neg_ll_with_grad_couples_enh(t, d, wage_spec)[0]
    base.fast_neg_ll_with_grad_couples = fast_neg_ll_with_grad_couples_enh

    # ------------------------------------------------------------------
    # Joint mapping: concatenate enhanced SM/SF and enhanced couples params
    # ------------------------------------------------------------------
    def get_param_names_joint_enh(wage_spec: str = "fw") -> List[str]:
        names_sm = [f"sm.{n}" for n in get_param_names_singles_enh(wage_spec)]
        names_sf = [f"sf.{n}" for n in get_param_names_singles_enh(wage_spec)]
        names_cou = [f"cou.{n}" for n in get_param_names_couples_enh(wage_spec)]
        return names_sm + names_sf + names_cou

    def get_initial_theta_joint_enh(wage_spec: str = "fw") -> np.ndarray:
        return np.concatenate(
            [
                get_initial_theta_singles_enh(wage_spec),
                get_initial_theta_singles_enh(wage_spec),
                get_initial_theta_couples_enh(wage_spec),
            ]
        )

    joint_n_jobs = args.joint_n_jobs
    use_joblib = JOBLIB_AVAILABLE and joint_n_jobs and joint_n_jobs > 1

    def fast_neg_ll_with_grad_joint_enh(theta: np.ndarray, df_sm, df_sf, df_cou, wage_spec: str = "fw") -> Tuple[float, np.ndarray]:
        theta_sm = get_initial_theta_singles_enh(wage_spec)
        theta_sf = get_initial_theta_singles_enh(wage_spec)
        theta_cou = get_initial_theta_couples_enh(wage_spec)
        len_sm = len(theta_sm)
        len_sf = len(theta_sf)
        theta_sm = theta[:len_sm]
        theta_sf = theta[len_sm:len_sm+len_sf]
        theta_cou = theta[len_sm+len_sf:]

        def compute_sm():
            data_sm = precompute_data_singles_enh(df_sm, is_male=True)
            ll = fast_log_likelihood_singles_enh(theta_sm, data_sm, wage_spec=wage_spec)
            grad = fast_analytical_gradient_singles_enh(theta_sm, data_sm, wage_spec=wage_spec)
            return ll, grad

        def compute_sf():
            data_sf = precompute_data_singles_enh(df_sf, is_male=False)
            ll = fast_log_likelihood_singles_enh(theta_sf, data_sf, wage_spec=wage_spec)
            grad = fast_analytical_gradient_singles_enh(theta_sf, data_sf, wage_spec=wage_spec)
            return ll, grad

        def compute_cou():
            data_cou = precompute_data_couples_enh(df_cou)
            neg_ll, neg_grad = fast_neg_ll_with_grad_couples_enh(theta_cou, data_cou, wage_spec=wage_spec)
            return -neg_ll, -neg_grad

        if use_joblib:
            results = Parallel(n_jobs=joint_n_jobs)(
                delayed(func)() for func in (compute_sm, compute_sf, compute_cou)
            )
            (ll_sm, grad_sm), (ll_sf, grad_sf), (ll_cou, grad_cou) = results
        else:
            ll_sm, grad_sm = compute_sm()
            ll_sf, grad_sf = compute_sf()
            ll_cou, grad_cou = compute_cou()

        total_ll = ll_sm + ll_sf + ll_cou
        total_grad = np.concatenate([grad_sm, grad_sf, grad_cou])
        return -total_ll, -total_grad

    base.get_param_names_joint = get_param_names_joint_enh
    base.get_initial_theta_joint = get_initial_theta_joint_enh
    base.fast_neg_ll_with_grad_joint = fast_neg_ll_with_grad_joint_enh

    # Determine wage_spec from forwarded args (best-effort)
    wage_spec_val = "vw"
    for i, tok in enumerate(forward_args):
        if tok in ("--wage-spec", "--wage_spec") and i + 1 < len(forward_args):
            wage_spec_val = forward_args[i + 1]
            break

    # Log features in use
    print(f"[INFO] Enhanced estimator: regions={'on' if use_region else 'off'}, years={'on' if use_year else 'off'}")
    if use_year and years_present:
        ref_year = min(years_present)
        print(f"[INFO] Year dummies (ref={ref_year}): {YEAR_CODES}")
    # Optional small gradient validation on singles (subset) before running optimizer
    if args.validate_gradient and mnl_path is not None and mnl_path.exists():
        try:
            df_val = base.pd.read_parquet(mnl_path)  # type: ignore[attr-defined]
            if "ruro_group" in df_val.columns:
                df_val = df_val[df_val["ruro_group"] == 1].copy()
            # Take a small subset of individuals
            id_col = "idperson" if "idperson" in df_val.columns else None
            if id_col:
                unique_ids = df_val[id_col].unique()[:50]
                df_val = df_val[df_val[id_col].isin(unique_ids)].copy()
            data_val = precompute_data_singles_enh(df_val, is_male=True)
            theta0 = get_initial_theta_singles_enh(wage_spec_val)

            def neg_ll_only(t: np.ndarray) -> float:
                return -fast_log_likelihood_singles_enh(t, data_val, wage_spec=wage_spec_val)

            grad_ana = fast_analytical_gradient_singles_enh(theta0, data_val, wage_spec=wage_spec_val)
            grad_num = base.numerical_gradient(neg_ll_only, theta0, eps=1e-5)
            diff = np.max(np.abs(grad_ana + grad_num))  # note sign
            print(f"[VALIDATE] Max grad diff (singles subset): {diff:.4e}")
        except Exception as e:
            print(f"[VALIDATE] Gradient check skipped due to error: {e}")

    # Optional couples gradient validation
    if args.validate_gradient_couples and mnl_path is not None and mnl_path.exists():
        try:
            df_val = base.pd.read_parquet(mnl_path)  # type: ignore[attr-defined]
            if "ruro_group" in df_val.columns:
                df_val = df_val[df_val["ruro_group"] == 10].copy()
            id_col = "idhh" if "idhh" in df_val.columns else None
            if id_col:
                uniq = df_val[id_col].unique()[:20]
                df_val = df_val[df_val[id_col].isin(uniq)].copy()
            data_val = precompute_data_couples_enh(df_val)
            theta0 = get_initial_theta_couples_enh(wage_spec_val)
            def neg_ll_cou(t: np.ndarray) -> float:
                nll, _ = fast_neg_ll_with_grad_couples_enh(t, data_val, wage_spec=wage_spec_val)
                return nll
            nll, grad_ana = fast_neg_ll_with_grad_couples_enh(theta0, data_val, wage_spec=wage_spec_val)
            grad_num = base.numerical_gradient(neg_ll_cou, theta0, eps=1e-5)
            diff = np.max(np.abs(grad_ana - grad_num))
            print(f"[VALIDATE COU] Max grad diff (subset): {diff:.4e}")
        except Exception as e:
            print(f"[VALIDATE COU] Gradient check skipped due to error: {e}")

    # Optional joint gradient validation (tiny subset)
    if args.validate_gradient_joint and mnl_path is not None and mnl_path.exists():
        try:
            df_val = base.pd.read_parquet(mnl_path)  # type: ignore[attr-defined]
            # Split groups
            df_sm = df_val[df_val.get("ruro_group", 1) == 1].copy() if 1 in df_val.get("ruro_group", [1]).values else None
            df_cou = df_val[df_val.get("ruro_group", 10) == 10].copy() if 10 in df_val.get("ruro_group", [10]).values else None
            df_sf = df_sm  # pooled singles split into sm/sf not available; reuse pooled
            # Sample small subsets
            def sample_df(dfin, n_ids=20):
                if dfin is None:
                    return None
                id_col = "idperson" if "idperson" in dfin.columns else None
                if id_col is None:
                    return dfin.head(200).copy()
                uniq = dfin[id_col].unique()[:n_ids]
                return dfin[dfin[id_col].isin(uniq)].copy()
            df_sm_s = sample_df(df_sm)
            df_sf_s = sample_df(df_sf)
            df_cou_s = sample_df(df_cou)
            if df_sm_s is None or df_sf_s is None or df_cou_s is None:
                raise RuntimeError("Insufficient data for joint validation subset.")

            theta0 = get_initial_theta_joint_enh(wage_spec_val)
            def joint_neg_ll(t: np.ndarray) -> float:
                nll, _ = fast_neg_ll_with_grad_joint_enh(t, df_sm_s, df_sf_s, df_cou_s, wage_spec=wage_spec_val)
                return nll
            nll, grad_ana = fast_neg_ll_with_grad_joint_enh(theta0, df_sm_s, df_sf_s, df_cou_s, wage_spec=wage_spec_val)
            grad_num = base.numerical_gradient(joint_neg_ll, theta0, eps=1e-5)
            diff = np.max(np.abs(grad_ana - grad_num))
            print(f"[VALIDATE JOINT] Max grad diff (subset): {diff:.4e}")
        except Exception as e:
            print(f"[VALIDATE JOINT] Gradient check skipped due to error: {e}")

    sys.argv = [sys.argv[0]] + forward_args
    base.main()


if __name__ == "__main__":
    main()
