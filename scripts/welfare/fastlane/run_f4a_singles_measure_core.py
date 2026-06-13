"""
FAST-LANE F4-A: SINGLES MEASURE CORE + W3/W4/W1 + W6 DESIGN AUDIT.

Authorized by the F4-A prompt. Consumes V_i^IS only (joint batching irrelevant —
F3-R2B reports READY FOR F4: YES). NO inequality statistics, decomposition, V_dir,
EUROMOD pricing, promotion, commit, or edits to engines/specs/data/existing scripts.
W6 is NOT computed (design audit only) — its universal hours grid is unratified.

The ONE rule (JMP_measure_mapping_memo_v1.md §2): solve for w such that
    V_i^actual ( = V_i^IS_staged )  =  V_i^ref( B(w) )
with B(w) the per-measure reference object, V monotone in w.

Measures:
  W3 shift(w):       lse_j[ u(c_j + w, l_j) + opp_j ]            (Omega ~ 0 by construction)
  W4 single_node(w): u(w, l_home)                                 (analytic + numeric)
  W1 replace(w):     lse_j[ u(w, l_j) + opp_j ]                   (zero-recovery kappa gate)
  W1 working-only:   lse_j[ u(c'_j(w), l_j) + opp_j ], c'=w if working else actual (sensitivity)
  W6:                BLOCKED_PENDING_GRID_RATIFICATION (design table only)

Units (memo §1, prompt Task 0.2): engine consumption = c_norm = consumption_eur / c_scale;
the public solver takes/returns real-2016 EUR and normalizes internally (w_norm = w_eur/c_scale).
beta_c is FIXED = 1.0; theta_c_singles = +0.00758 (>0 => u unbounded above in c, no hard cap).

Atomic writes only; never overwrite completed artifacts.
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
for _p in ["scripts/bpool", "scripts/enhanced", "scripts/welfare", "scripts/pilot"]:
    sys.path.insert(0, str(_REPO / _p))

import jax
jax.config.update("jax_enable_x64", True)

import estimation_spec_parser as sp
import joint_recovery_test as jrt
import estimation_engine as ee
import welfare_core as wc
from _bpool_paths import bpool_dir

# ---------------------------------------------------------------------------
# constants / paths
# ---------------------------------------------------------------------------
STAGED_STEM = "fr_p3a_bpool_engine_ready_staged_threeB1"
CERT_STEM   = "fr_p3a_bpool_engine_ready"
N_SINGLES_EXPECTED = 5007
DCM_FLOOR_EUR = 1.0                  # engine-ready consumption floor (real-2016 EUR)
CAP_MULT      = 50.0                 # bracket cap = 50 x max observed c_j (memo decision 2)
TOL_W_EUR     = 1e-9                 # bisection bracket-width tolerance (EUR)
TOL_V_RESID   = 1e-6                 # convergence residual on V (nats)
MAXIT         = 200
BETA_C        = 1.0                  # spec: utility_consumption_coef_fixed = 1.0

_SPEC   = _REPO / "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
_THETA  = _REPO / "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"
_VIIS   = _REPO / "outputs/welfare/fastlane/singles_ViIS_dualstem_v1.parquet"
_F3R2_MANIFEST = _REPO / "outputs/welfare/fastlane/f3r2_reconciliation_manifest_v1.json"
_MEMO   = _REPO / "docs/jmp_methodology/JMP_measure_mapping_memo_v1.md"

_OUT_PARQUET  = _REPO / "outputs/welfare/fastlane/singles_measures_F4A_v1.parquet"
_OUT_MANIFEST = _REPO / "outputs/welfare/fastlane/F4A_manifest_v1.json"
_OUT_DOC      = _REPO / "docs/jmp_methodology/RURO_welfare_F4A_measure_core_report_v1.md"

# Inputs + prior-increment artifacts that must never be overwritten by this run.
_IMMUTABLE = {
    _SPEC, _THETA, _VIIS, _F3R2_MANIFEST, _MEMO,
    _REPO / "outputs/welfare/fastlane/singles_Vi_production_v1.parquet",
    _REPO / "outputs/welfare/fastlane/couples_ViIS_dualstem_v1.parquet",
    _REPO / "outputs/welfare/fastlane/f3r2a_repair_manifest_v1.json",
    _REPO / "outputs/welfare/fastlane/f3r2a_joint_batch_diagnosis_v1.json",
    _REPO / "outputs/welfare/fastlane/f3r2b_diagnosis_v1.json",
}


# ---------------------------------------------------------------------------
# atomic writers (refuse to clobber immutable inputs / completed artifacts)
# ---------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _guard(dest: Path):
    if dest in _IMMUTABLE:
        raise FileExistsError(f"STOP: refuse to overwrite immutable artifact: {dest}")
    if dest.exists():
        raise FileExistsError(
            f"STOP: completed artifact already exists, will not overwrite: {dest} "
            "(bump the _vN suffix to re-run).")


def _atomic_write_json(obj, dest: Path):
    _guard(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=_jsonify))
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_write_parquet(df: pd.DataFrame, dest: Path):
    _guard(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        df.to_parquet(tmp, index=False)
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_write_text(text: str, dest: Path):
    _guard(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.rename(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _jsonify(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return float(o)


# ---------------------------------------------------------------------------
# math helpers
# ---------------------------------------------------------------------------
def _box_cox(x, theta):
    x = np.asarray(x, dtype=np.float64)
    if abs(float(theta)) < 1e-8:
        return np.log(x)
    return (np.power(x, float(theta)) - 1.0) / float(theta)


def _logsumexp_rows(M):
    """Row-wise logsumexp of a (n, k) array -> (n,)."""
    M = np.asarray(M, dtype=np.float64)
    mx = np.max(M, axis=1, keepdims=True)
    return (mx[:, 0] + np.log(np.sum(np.exp(M - mx), axis=1)))


# ---------------------------------------------------------------------------
# group bridge: engine group index -> uid (mirror welfare_vdir / precompute key)
# ---------------------------------------------------------------------------
def _key_to_uid(bp: Path, group: str) -> dict:
    flag = 1.0 if group == "singles_male" else 0.0
    br = pd.read_parquet(bp / f"{STAGED_STEM}__singles.parquet",
                         columns=["stacked_hh_uid", "idhh", "year_tag", "dgn"])
    br = br[br["dgn"] == flag]
    multi_year = br["year_tag"].nunique() > 1
    if multi_year:
        key = br["idhh"].astype(np.int64) * 10 + br["year_tag"].astype(np.int64)
    else:
        key = br["idhh"].astype(np.int64)
    br = br.assign(_key=key.values)
    m = br.drop_duplicates("_key").set_index("_key")["stacked_hh_uid"]
    return {int(k): int(v) for k, v in m.items()}


# ---------------------------------------------------------------------------
# per-group welfare state (engine components -> fixed reference building blocks)
# ---------------------------------------------------------------------------
class GroupState:
    """Holds the fixed (consumption-independent) building blocks for one singles
    group, so the reference value R_mode(w) only recomputes the Box-Cox of the
    candidate consumption."""

    def __init__(self, data, spec, theta, group, c_scale, l_scale, bp, viis_lookup):
        self.group = group
        self.c_scale = float(c_scale)
        self.l_scale = float(l_scale)
        ng = int(data.n_groups)
        na = int(data.n_obs // data.n_groups)
        self.n_groups, self.n_alts = ng, na

        comp = ee.compute_likelihood_singles(theta, data, spec, return_components=True)
        u = np.asarray(comp["u"], dtype=np.float64).reshape(ng, na)
        V = np.asarray(comp["V"], dtype=np.float64).reshape(ng, na)
        self.lse_engine = np.asarray(comp["lse"], dtype=np.float64)        # V_i^IS engine
        self.u_grid = u
        self.opp_grid = V - u                                             # held fixed
        self.c_norm_grid = np.asarray(data.consumption, dtype=np.float64).reshape(ng, na)
        self.l_norm_grid = np.asarray(data.leisure, dtype=np.float64).reshape(ng, na)
        self.working_grid = np.asarray(data.working, dtype=np.float64).reshape(ng, na)

        # theta_c (shared singles) for the consumption Box-Cox
        fixed = dict(getattr(spec, "fixed_params", {}) or {})

        def P(name):
            if name in fixed:
                return float(fixed[name])
            return float(theta[spec.get_param_index(name)])
        self.theta_c = P(spec.theta_c_param_name(group))

        # leisure_term_j = beta_l_coeff_i * bc_l(l_j) = u_j - beta_c * bc_c(c_norm_j)
        bc_c_actual = _box_cox(self.c_norm_grid, self.theta_c)
        self.leisure_term_grid = self.u_grid - BETA_C * bc_c_actual

        # home node = lowest-draw working==0 alternative (col order == draw order)
        is_home = (self.working_grid == 0)
        self.home_count = is_home.sum(axis=1).astype(int)
        self.home_idx = np.argmax(is_home, axis=1)                       # first True
        rows = np.arange(ng)
        self.leisure_term_home = self.leisure_term_grid[rows, self.home_idx]
        self.l_norm_home = self.l_norm_grid[rows, self.home_idx]

        # within-HH home-leisure uniqueness audit (model-relevant state for W4)
        nonunique = 0
        for i in range(ng):
            hl = self.l_norm_grid[i][is_home[i]]
            if hl.size and np.unique(np.round(hl, 9)).size > 1:
                nonunique += 1
        self.home_audit_nonunique = int(nonunique)
        self.home_audit_zero_home = int((self.home_count == 0).sum())

        # uid bridge + external V_i^IS_staged target
        k2u = _key_to_uid(bp, group)
        gk = np.asarray(data.group_ids)
        self.uids = np.array([k2u.get(int(gk[i]), -1) for i in range(ng)], dtype=np.int64)
        self.V_target = np.array([viis_lookup.get(int(self.uids[i]), np.nan)
                                  for i in range(ng)], dtype=np.float64)

        # per-HH bracket extents in EUR
        self.min_c_eur = np.min(self.c_norm_grid, axis=1) * self.c_scale
        self.max_c_eur = np.max(self.c_norm_grid, axis=1) * self.c_scale

    # ----- reference value functions R_mode(w_eur) ; w is (n_groups,) -----
    def _bc_c_of_eur(self, w_eur_vec):
        return _box_cox(np.asarray(w_eur_vec, dtype=np.float64) / self.c_scale, self.theta_c)

    def R_shift(self, w_eur):
        c = self.c_norm_grid + (np.asarray(w_eur, float) / self.c_scale)[:, None]
        # consumption must stay positive for Box-Cox; the valid bracket keeps it so,
        # but guard against numerical excursions WITHOUT silently clipping the result:
        bad = np.any(c <= 0.0, axis=1)
        c_safe = np.where(c <= 0.0, np.nan, c)
        u = self.leisure_term_grid + BETA_C * _box_cox(c_safe, self.theta_c)
        R = _logsumexp_rows(u + self.opp_grid)
        return np.where(bad, -np.inf, R)

    def R_replace(self, w_eur):
        bc = self._bc_c_of_eur(w_eur)[:, None]
        u = self.leisure_term_grid + BETA_C * bc
        return _logsumexp_rows(u + self.opp_grid)

    def R_replace_working(self, w_eur):
        bc_w = self._bc_c_of_eur(w_eur)[:, None]                          # (ng,1)
        bc_actual = _box_cox(self.c_norm_grid, self.theta_c)             # (ng,na)
        bc = np.where(self.working_grid > 0, bc_w, bc_actual)
        u = self.leisure_term_grid + BETA_C * bc
        return _logsumexp_rows(u + self.opp_grid)

    def R_single_node(self, w_eur):
        return self.leisure_term_home + BETA_C * self._bc_c_of_eur(w_eur)


# ---------------------------------------------------------------------------
# monotone bracketing solver (public API in EUR; per-HH bounds)
# ---------------------------------------------------------------------------
def solve_equivalent_income(R_func, target, lo, hi, *, expand=True,
                            level_measure=True, floor_eur=DCM_FLOOR_EUR):
    """Vectorised monotone root solve of R_func(w) = target over per-HH [lo, hi] (EUR).

    Returns dict of (n,) arrays: omega, residual, converged, below_floor, above_cap,
    monotone, n_expand. Does NOT clip the root: out-of-domain outcomes are FLAGGED.
    """
    n = target.shape[0]
    lo = np.array(lo, dtype=np.float64).copy()
    hi = np.array(hi, dtype=np.float64).copy()

    f_lo = R_func(lo) - target
    f_hi = R_func(hi) - target

    # monotonicity probe (R strictly increasing => f(hi) > f(lo))
    monotone = f_hi > f_lo

    n_expand = np.zeros(n, dtype=int)
    if expand:
        need = f_hi < 0
        if np.any(need):
            hi = np.where(need, hi * CAP_MULT, hi)
            f_hi = np.where(need, R_func(hi) - target, f_hi)
            n_expand = np.where(need, 1, n_expand)

    below_floor = f_lo > 0 if level_measure else np.zeros(n, dtype=bool)  # target < R(floor)
    above_cap = f_hi < 0                                                 # target > R(cap)
    bracketed = (f_lo <= 0) & (f_hi >= 0)

    a = lo.copy()
    b = hi.copy()
    for _ in range(MAXIT):
        mid = 0.5 * (a + b)
        fm = R_func(mid) - target
        go_right = fm < 0
        a = np.where(go_right, mid, a)
        b = np.where(go_right, b, mid)
        if np.nanmax(b - a) < TOL_W_EUR:
            break
    omega = 0.5 * (a + b)
    resid = R_func(omega) - target
    converged = bracketed & (np.abs(resid) < TOL_V_RESID)
    return {
        "omega": omega, "residual": resid, "converged": converged,
        "below_floor": below_floor, "above_cap": above_cap,
        "monotone": monotone, "n_expand": n_expand, "bracketed": bracketed,
    }


def analytic_w4(gs: GroupState):
    """Closed-form Box-Cox inversion of u(w, l_home) = V_target for singles W4.
        bc_c(w_norm) = (V_target - leisure_term_home) / beta_c =: RHS
        theta_c != 0 : feasible iff 1 + theta_c*RHS > 0 ; w_norm = (1+theta_c*RHS)^(1/theta_c)
        theta_c ~ 0 : w_norm = exp(RHS)
    Returns (omega_eur, feasible_mask)."""
    rhs = (gs.V_target - gs.leisure_term_home) / BETA_C
    tc = gs.theta_c
    if abs(tc) < 1e-8:
        w_norm = np.exp(rhs)
        feasible = np.isfinite(w_norm)
    else:
        base = 1.0 + tc * rhs
        feasible = base > 0.0
        with np.errstate(invalid="ignore"):
            w_norm = np.where(feasible, np.power(np.where(feasible, base, np.nan), 1.0 / tc), np.nan)
    return w_norm * gs.c_scale, feasible


# ---------------------------------------------------------------------------
# synthetic kappa-recovery gates (recompute target from the SAME ref at known kappa)
# ---------------------------------------------------------------------------
def _synthetic_gate(gs: GroupState, mode: str, kappa_eur: float):
    """Build target = R_mode(kappa) then solve R_mode(w)=target; report max|w-kappa|."""
    n = gs.n_groups
    kap = np.full(n, kappa_eur, dtype=np.float64)
    if mode == "replace":
        Rf = gs.R_replace
        lo = np.full(n, DCM_FLOOR_EUR); hi = gs.max_c_eur * CAP_MULT
        level = True
    elif mode == "single_node":
        Rf = gs.R_single_node
        lo = np.full(n, DCM_FLOOR_EUR); hi = gs.max_c_eur * CAP_MULT
        level = True
    elif mode == "shift":
        Rf = gs.R_shift
        lo = -(gs.min_c_eur - DCM_FLOOR_EUR); hi = gs.max_c_eur * CAP_MULT
        level = False
    else:
        raise ValueError(mode)
    target = Rf(kap)
    res = solve_equivalent_income(Rf, target, lo, hi, level_measure=level,
                                  expand=(mode != "shift"))
    err = np.abs(res["omega"][res["converged"]] - kappa_eur)
    return {
        "mode": mode, "kappa_eur": kappa_eur, "n": int(n),
        "n_converged": int(res["converged"].sum()),
        "max_abs_recovery_err": float(np.max(err)) if err.size else None,
        "median_abs_recovery_err": float(np.median(err)) if err.size else None,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    for d in (_OUT_PARQUET, _OUT_MANIFEST, _OUT_DOC):
        _guard(d)   # fail fast before any compute if an artifact already exists

    print("F4-A start")
    spec = sp.parse_specification(_SPEC)
    theta = np.asarray(jrt.load_theta_star_from_csv(_THETA, spec), dtype=np.float64)
    spec_hash = _sha256(_SPEC)[:16]
    theta_hash = hashlib.sha256(theta.tobytes()).hexdigest()[:16]
    print(f"  spec_hash={spec_hash}  theta_hash={theta_hash}")

    bp = bpool_dir()
    meta = json.loads((bp / f"{STAGED_STEM}__mnlmeta.json").read_text())
    c_scale = float(meta["normalization"]["singles"]["c_scale"])
    l_scale = float(meta["normalization"]["singles"]["l_scale"])

    # ---------------- PRECONDITIONS ----------------
    print("\n=== PRECONDITIONS ===")
    f3r2 = json.loads(_F3R2_MANIFEST.read_text())
    man_spec = f3r2.get("spec_hash"); man_theta = f3r2.get("theta_hash")
    viis_sha = _sha256(_VIIS)
    viis = pd.read_parquet(_VIIS)
    n_keys = int(viis["uid"].nunique())
    n_nonnull = int(viis["uid"].notna().sum())

    # Gate-0: welfare-core logsum negLL parity on staged data + reproduce staged negll sum
    data_sm, data_sf, _ = jrt.build_data_objects(STAGED_STEM, [], 0)
    gate0 = {}
    eng_negll_sum = 0.0
    for data, grp in ((data_sm, "singles_male"), (data_sf, "singles_female")):
        gw = wc.compute_group_welfare(data, spec, theta, grp)
        g0 = wc.gate0_parity(data, spec, theta, grp, gw)
        eng_negll_sum += float(g0["estimator_negll"])
        gate0[grp] = {"max_abs": float(g0["max_abs"]), "estimator_negll": float(g0["estimator_negll"])}
    staged_negll_parquet = float(viis["negll_contribution_staged"].sum())
    staged_negll_manifest = float(f3r2["task1_dualstem"]["singles_negll_staged_sum"])
    gate0_parity_max = max(gate0[g]["max_abs"] for g in gate0)
    negll_reproduce_diff = abs(eng_negll_sum - staged_negll_manifest)

    precond = {
        "consumed_singles_viis_parquet": str(_VIIS),
        "consumed_singles_viis_sha256": viis_sha,
        "n_unique_nonnull_hh_keys": n_keys,
        "n_keys_ok": (n_keys == N_SINGLES_EXPECTED and n_nonnull == len(viis)),
        "spec_hash_recomputed": spec_hash, "spec_hash_manifest": man_spec,
        "spec_hash_match": (spec_hash == man_spec),
        "theta_hash_recomputed": theta_hash, "theta_hash_manifest": man_theta,
        "theta_hash_match": (theta_hash == man_theta),
        "manifest_file_hash_spec_yaml": f3r2["task0_audit"]["hash_spec_yaml"],
        "recomputed_file_hash_spec_yaml": _sha256(_SPEC),
        "manifest_file_hash_theta_csv": f3r2["task0_audit"]["hash_theta_csv"],
        "recomputed_file_hash_theta_csv": _sha256(_THETA),
        "manifest_file_hash_staged_singles_pq": f3r2["task0_audit"]["hash_staged_singles_pq"],
        "recomputed_file_hash_staged_singles_pq": _sha256(bp / f"{STAGED_STEM}__singles.parquet"),
        "gate0_logsum_parity_max_abs": gate0_parity_max,
        "gate0_parity_per_group": gate0,
        "engine_singles_negll_sum": eng_negll_sum,
        "staged_negll_sum_parquet": staged_negll_parquet,
        "staged_negll_sum_manifest": staged_negll_manifest,
        "staged_negll_reproduce_diff": negll_reproduce_diff,
    }
    file_hashes_match = (
        precond["recomputed_file_hash_spec_yaml"] == precond["manifest_file_hash_spec_yaml"]
        and precond["recomputed_file_hash_theta_csv"] == precond["manifest_file_hash_theta_csv"]
        and precond["recomputed_file_hash_staged_singles_pq"] == precond["manifest_file_hash_staged_singles_pq"])
    precond["all_file_hashes_match"] = bool(file_hashes_match)
    precond_ok = bool(
        precond["n_keys_ok"] and precond["spec_hash_match"] and precond["theta_hash_match"]
        and file_hashes_match and gate0_parity_max < 1e-6 and negll_reproduce_diff < 1e-6)
    precond["PRECONDITIONS_PASS"] = precond_ok
    for k in ["n_keys_ok", "spec_hash_match", "theta_hash_match", "all_file_hashes_match"]:
        print(f"  {k}: {precond[k]}")
    print(f"  gate0_logsum_parity_max_abs: {gate0_parity_max:.2e}")
    print(f"  staged_negll reproduce diff: {negll_reproduce_diff:.2e} "
          f"(engine {eng_negll_sum:.5f} vs manifest {staged_negll_manifest:.5f})")
    print(f"  PRECONDITIONS_PASS: {precond_ok}")
    if not precond_ok:
        raise SystemExit("STOP: preconditions failed; refusing to run measures.")

    viis_lookup = {int(r.uid): float(r.V_i_IS_staged) for r in viis.itertuples()}

    # ---------------- build per-group state ----------------
    states = {}
    for data, grp in ((data_sm, "singles_male"), (data_sf, "singles_female")):
        states[grp] = GroupState(data, spec, theta, grp, c_scale, l_scale, bp, viis_lookup)

    # ---------------- TASK 0 — contract + design audit ----------------
    print("\n=== TASK 0: contract + design audit ===")
    memo_txt = _MEMO.read_text(encoding="utf-8", errors="ignore")
    memo_is_prereg = "pre-registration" in memo_txt.lower()
    memo_signoff_unchecked = memo_txt.count("- [ ]")
    task0 = {
        "memo": {
            "path": str(_MEMO),
            "status_line_pre_registration": memo_is_prereg,
            "signoff_checklist_unchecked_count": int(memo_signoff_unchecked),
            "explicit_ratification_artifact_found": False,
            "verdict": ("PRE-REGISTRATION (UNRATIFIED): no signed/ratified artifact found; "
                        "memo header says pre-registration and the sign-off checklist is unchecked."),
        },
        "units": {
            "engine_consumption": "c_norm = consumption_eur / c_scale (dimensionless)",
            "c_scale": c_scale, "l_scale": l_scale,
            "solver_io": "real-2016 EUR (public); internally w_norm = w_eur / c_scale",
            "wage_convention": "w_eur converted to w_eur / c_scale before Box-Cox (not used on reference side; occupation/wage enter u only via consumption)",
            "beta_c_fixed": BETA_C, "theta_c_singles": states["singles_male"].theta_c,
            "consumption_floor_eur": DCM_FLOOR_EUR,
            "omega_units": "2016-real EUR (W1/W4 = consumption level; W3 = shift ~0)",
        },
        "w4_home_state_audit": {},
        "w6_source_audit": {},
    }
    w4_audit_stop = False
    for grp, gs in states.items():
        a = {
            "n_hh": gs.n_groups,
            "n_hh_zero_home_nodes": gs.home_audit_zero_home,
            "n_hh_nonunique_home_leisure": gs.home_audit_nonunique,
            "home_node_selection": "lowest-draw working==0 alternative (deterministic)",
            "unique_home_state": (gs.home_audit_nonunique == 0 and gs.home_audit_zero_home == 0),
        }
        if not a["unique_home_state"]:
            w4_audit_stop = True
        task0["w4_home_state_audit"][grp] = a
    task0["w4_home_state_audit"]["STOP_W4"] = bool(w4_audit_stop)

    # W6 design source audit (report only — do NOT invent representative points)
    task0["w6_source_audit"] = {
        "rule_locked": ("J = {home node} U {one node per canonical hours band of the estimation "
                        "spec}, all at consumption w, uniform weights (no g_hat, no pi)."),
        "estimation_focal_bands_hours": {
            "F35_reference": [33.5, 36.5], "pt1": [18.5, 21.5], "pt2": [29.5, 30.5],
            "ft": [37.5, 40.5], "lh": [44.5, 70.0], "home": 0.0,
        },
        "note_band_vs_reporting_bins": ("estimation working_* indicators (precompute) differ "
                                        "slightly from the reporting hours_bins in the spec; the "
                                        "estimation bands are the model-relevant ones."),
        "d1_proposal_mixture_modes": {
            "PT1": "~20h band [17.5,21.5]", "PT2": "~30h band [28.5,30.5]",
            "F35": "~35h", "FT": "~39h", "LH": "~48h band [44.5,70]",
            "BG": "background uniform over FULL support [5,70], weight 0.21 (proposal density only)",
        },
        "unresolved_governance_decisions": [
            "Representative hours value WITHIN each band: each band is a RANGE; u depends on "
            "leisure = (TOTAL_LEISURE_HOURS - hours), so one hours point per band must be chosen "
            "(band midpoint? D1 modal hours? chosen-hours mean?). NOT invented here.",
            "BG support band treatment: BG is a proposal-density background over [5,70], not a "
            "preference focal band. Include a J node for it? If so, at what representative hours "
            "(the band spans the whole support)? UNRESOLVED.",
            "F35 reference band: opportunity reference (beta_h=0). In W6 opportunity betas do not "
            "enter (uniform weights), so include an F35 leisure node? Default yes, but confirm.",
            "TOTAL_LEISURE_HOURS time endowment used to map hours->leisure for J nodes (80h here) "
            "must be ratified as the universal mapping constant.",
        ],
        "blocked": True,
    }
    print(f"  memo: {task0['memo']['verdict']}")
    print(f"  W4 home audit STOP: {w4_audit_stop}")
    print(f"  W6: BLOCKED (design audit only)")

    # ---------------- TASK 1 — synthetic gates (machinery validation) ----------------
    print("\n=== TASK 1: solver / evaluator synthetic gates ===")
    # utility-only evaluator gate vs engine u (independent reconstruction <= 1e-9)
    util_gate = {}
    for grp, gs in states.items():
        u_recon = gs.leisure_term_grid + BETA_C * _box_cox(gs.c_norm_grid, gs.theta_c)
        md = float(np.max(np.abs(u_recon - gs.u_grid)))
        util_gate[grp] = {"max_abs_u_diff_vs_engine": md, "pass": md <= 1e-9}
        print(f"  util-gate {grp}: max|du|={md:.2e} pass={md<=1e-9}")
    synth = {}
    for grp, gs in states.items():
        synth[grp] = {
            "replace_kappa1500": _synthetic_gate(gs, "replace", 1500.0),
            "single_node_kappa1500": _synthetic_gate(gs, "single_node", 1500.0),
            "shift_kappa200": _synthetic_gate(gs, "shift", 200.0),
        }
        for k, v in synth[grp].items():
            print(f"  synth {grp}.{k}: max_err={v['max_abs_recovery_err']:.2e}"
                  if v["max_abs_recovery_err"] is not None else f"  synth {grp}.{k}: no converged")
    # analytic-vs-numeric single_node on a synthetic target (closed-form check)
    analytic_synth = {}
    for grp, gs in states.items():
        kap = np.full(gs.n_groups, 1500.0)
        tgt = gs.R_single_node(kap)
        # numeric solve
        res = solve_equivalent_income(gs.R_single_node, tgt,
                                      np.full(gs.n_groups, DCM_FLOOR_EUR),
                                      gs.max_c_eur * CAP_MULT, level_measure=True)
        # analytic inversion against the SAME target
        rhs = (tgt - gs.leisure_term_home) / BETA_C
        base = 1.0 + gs.theta_c * rhs
        w_an = np.power(np.where(base > 0, base, np.nan), 1.0 / gs.theta_c) * gs.c_scale
        d_num = np.abs(res["omega"][res["converged"]] - 1500.0)
        d_an = np.abs(w_an - 1500.0)
        analytic_synth[grp] = {
            "numeric_max_err": float(np.max(d_num)) if d_num.size else None,
            "analytic_max_err": float(np.nanmax(d_an)),
            "num_vs_analytic_max_abs": float(np.nanmax(np.abs(res["omega"] - w_an))),
        }

    # ---------------- TASK 2 — W3 revalidation (shift) ----------------
    print("\n=== TASK 2: W3 revalidation ===")
    w3 = {}
    w3_arrays = {}
    for grp, gs in states.items():
        phi0 = gs.R_shift(np.zeros(gs.n_groups)) - gs.V_target          # ref value at w=0 vs target
        # lo strictly negative so f_lo < 0 even when the min node sits at the 1.0 EUR
        # assembly floor: a W3 shift only needs consumption > 0 for Box-Cox (the floor is a
        # data-assembly clip, not a solver-domain bound), and the root is 0 by construction.
        lo = -(gs.min_c_eur - 1e-6)
        hi = gs.max_c_eur * CAP_MULT
        res = solve_equivalent_income(gs.R_shift, gs.V_target, lo, hi,
                                      level_measure=False, expand=False)
        w3_arrays[grp] = {"omega": res["omega"], "converged": res["converged"],
                          "residual": res["residual"]}
        nconv = int((res["bracketed"] & ~res["converged"]).sum())       # genuine non-convergence
        conv = res["converged"]
        omega_abs_max = float(np.max(np.abs(res["omega"][conv]))) if conv.any() else None
        w3[grp] = {
            "ref_at_w0_max_abs_vs_ViIS_staged": float(np.max(np.abs(phi0))),
            "ref_at_w0_le_1e9": bool(np.max(np.abs(phi0)) <= 1e-9),
            "omega_abs_max_converged": omega_abs_max,
            "omega_le_1e8": bool(omega_abs_max is not None and omega_abs_max <= 1e-8),
            "n_nonconverged": nconv,
            "nonconv_frac": nconv / gs.n_groups,
            "nonconv_lt_0p5pct": (nconv / gs.n_groups) < 0.005,
            "monotone_all": bool(np.all(res["monotone"])),
        }
        print(f"  W3 {grp}: phi0_max={w3[grp]['ref_at_w0_max_abs_vs_ViIS_staged']:.2e} "
              f"omega_abs_max={omega_abs_max} nonconv={nconv}")
    w3_pass = all(w3[g]["ref_at_w0_le_1e9"] and w3[g]["omega_le_1e8"]
                  and w3[g]["nonconv_lt_0p5pct"] for g in w3)
    print(f"  W3 PASS: {w3_pass}")

    # ---------------- TASK 3 — W4 staying-home (numeric + analytic) ----------------
    print("\n=== TASK 3: W4 staying-home ===")
    w4 = {}
    w4_arrays = {}
    for grp, gs in states.items():
        lo = np.full(gs.n_groups, DCM_FLOOR_EUR)
        hi = gs.max_c_eur * CAP_MULT
        res = solve_equivalent_income(gs.R_single_node, gs.V_target, lo, hi, level_measure=True)
        w_an, feasible_an = analytic_w4(gs)                              # exact closed form (primary)
        # Agreement gate: compare numeric vs analytic where the numeric root lies IN-BRACKET
        # (converged) and the analytic is feasible. The Box-Cox inversion's natural scale is
        # NORMALIZED consumption (w_norm = w_eur / c_scale); gate there. (In raw EUR the bisection
        # hits the float-precision floor for near-log utility at very large omega; that is a
        # representation limit, not a method disagreement — the analytic is exact.)
        both = res["converged"] & feasible_an & np.isfinite(w_an)
        d_eur = np.abs(res["omega"][both] - w_an[both]) if both.any() else np.array([])
        d_norm = d_eur / gs.c_scale
        # category separation: below_floor / above_cap (domain outcomes) vs genuine non-convergence
        genuine_nonconv = res["bracketed"] & ~res["converged"]
        nconv = int(genuine_nonconv.sum())
        w4_arrays[grp] = {
            "omega_numeric": res["omega"], "omega_analytic": w_an,
            "converged": res["converged"], "below_floor": res["below_floor"],
            "above_cap": res["above_cap"], "feasible_analytic": feasible_an,
            "genuine_nonconv": genuine_nonconv, "residual": res["residual"],
        }
        # primary omega = analytic where feasible (exact, defined beyond the cap), else NaN
        omega_primary = np.where(feasible_an, w_an, np.nan)
        w4[grp] = {
            "n_hh": gs.n_groups,
            "num_vs_analytic_max_abs_norm": float(np.max(d_norm)) if d_norm.size else None,
            "num_vs_analytic_max_abs_eur": float(np.max(d_eur)) if d_eur.size else None,
            "num_vs_analytic_le_1e8_norm": bool(d_norm.size and np.max(d_norm) <= 1e-8),
            "n_compared_in_bracket": int(both.sum()),
            "n_below_floor": int(res["below_floor"].sum()),
            "n_above_cap": int(res["above_cap"].sum()),
            "above_cap_frac": float(res["above_cap"].sum()) / gs.n_groups,
            "n_genuine_nonconverged": nconv,
            "nonconv_frac": nconv / gs.n_groups,
            "nonconv_lt_0p5pct": (nconv / gs.n_groups) < 0.005,
            "n_analytic_infeasible": int((~feasible_an).sum()),
            "omega_primary_median_eur": float(np.nanmedian(omega_primary)),
            "omega_primary_is_analytic": True,
            "above_cap_note": ("home-equivalent income exceeds 50x max observed c; with near-log "
                               "consumption utility (theta_c~0.0076) high-V households require very "
                               "large compensating home consumption. Analytic value is exact/finite "
                               "and is the primary W4 omega; numeric cross-check brackets in-domain."),
        }
        print(f"  W4 {grp}: num-vs-analytic max_norm={w4[grp]['num_vs_analytic_max_abs_norm']:.2e} "
              f"(eur {w4[grp]['num_vs_analytic_max_abs_eur']:.2e}) below_floor={w4[grp]['n_below_floor']} "
              f"above_cap={w4[grp]['n_above_cap']} genuine_nonconv={nconv}")
    w4_pass = all(w4[g]["num_vs_analytic_le_1e8_norm"] and w4[g]["nonconv_lt_0p5pct"] for g in w4)
    print(f"  W4 PASS: {w4_pass}")

    # ---------------- TASK 4 — W1 equal-pay (+ working-only sensitivity) ----------------
    print("\n=== TASK 4: W1 equal-pay ===")
    w1 = {}
    w1_arrays = {}
    for grp, gs in states.items():
        lo = np.full(gs.n_groups, DCM_FLOOR_EUR)
        hi = gs.max_c_eur * CAP_MULT
        res = solve_equivalent_income(gs.R_replace, gs.V_target, lo, hi, level_measure=True)
        res_wo = solve_equivalent_income(gs.R_replace_working, gs.V_target, lo, hi, level_measure=True)
        # corrected synthetic zero-recovery: all c_j = kappa -> w* = kappa
        zr = _synthetic_gate(gs, "replace", 1234.0)
        w1_arrays[grp] = {
            "omega": res["omega"], "converged": res["converged"],
            "below_floor": res["below_floor"], "above_cap": res["above_cap"],
            "omega_working_only": res_wo["omega"], "converged_working_only": res_wo["converged"],
            "below_floor_wo": res_wo["below_floor"], "above_cap_wo": res_wo["above_cap"],
        }
        nconv = int((res["bracketed"] & ~res["converged"]).sum())
        nconv_wo = int((res_wo["bracketed"] & ~res_wo["converged"]).sum())
        w1[grp] = {
            "n_hh": gs.n_groups,
            "n_below_floor": int(res["below_floor"].sum()),
            "n_above_cap": int(res["above_cap"].sum()),
            "n_nonconverged": nconv, "nonconv_frac": nconv / gs.n_groups,
            "nonconv_lt_0p5pct": (nconv / gs.n_groups) < 0.005,
            "omega_median_eur": float(np.median(res["omega"][res["converged"]])) if res["converged"].any() else None,
            "working_only_n_below_floor": int(res_wo["below_floor"].sum()),
            "working_only_n_above_cap": int(res_wo["above_cap"].sum()),
            "working_only_n_nonconverged": nconv_wo,
            "working_only_nonconv_lt_0p5pct": (nconv_wo / gs.n_groups) < 0.005,
            "working_only_omega_median_eur": float(np.median(res_wo["omega"][res_wo["converged"]])) if res_wo["converged"].any() else None,
            "synthetic_zero_recovery_kappa": zr,
        }
        print(f"  W1 {grp}: below_floor={w1[grp]['n_below_floor']} above_cap={w1[grp]['n_above_cap']} "
              f"nonconv={nconv} | working-only nonconv={nconv_wo} | "
              f"zero-recovery max_err={zr['max_abs_recovery_err']:.2e}")
    w1_pass = all(w1[g]["nonconv_lt_0p5pct"]
                  and w1[g]["synthetic_zero_recovery_kappa"]["max_abs_recovery_err"] is not None
                  and w1[g]["synthetic_zero_recovery_kappa"]["max_abs_recovery_err"] <= 1e-6
                  for g in w1)
    print(f"  W1 PASS: {w1_pass}")

    # ---------------- TASK 6 — assemble per-HH parquet ----------------
    print("\n=== TASK 6: outputs ===")
    rows = []
    for grp, gs in states.items():
        for i in range(gs.n_groups):
            rows.append({
                "uid": int(gs.uids[i]), "group": grp,
                "V_i_IS_staged": float(gs.V_target[i]),
                # W3
                "W3_omega_shift_eur": float(w3_arrays[grp]["omega"][i]),
                "W3_converged": bool(w3_arrays[grp]["converged"][i]),
                "W3_residual": float(w3_arrays[grp]["residual"][i]),
                # W4 (primary = exact analytic Box-Cox inversion; numeric = in-bracket cross-check)
                "W4_omega_eur": (float(w4_arrays[grp]["omega_analytic"][i])
                                 if bool(w4_arrays[grp]["feasible_analytic"][i]) else None),
                "W4_omega_numeric_eur": float(w4_arrays[grp]["omega_numeric"][i]),
                "W4_converged_numeric": bool(w4_arrays[grp]["converged"][i]),
                "W4_genuine_nonconv": bool(w4_arrays[grp]["genuine_nonconv"][i]),
                "W4_below_floor": bool(w4_arrays[grp]["below_floor"][i]),
                "W4_above_cap": bool(w4_arrays[grp]["above_cap"][i]),
                "W4_analytic_feasible": bool(w4_arrays[grp]["feasible_analytic"][i]),
                # W1
                "W1_omega_eur": float(w1_arrays[grp]["omega"][i]),
                "W1_converged": bool(w1_arrays[grp]["converged"][i]),
                "W1_below_floor": bool(w1_arrays[grp]["below_floor"][i]),
                "W1_above_cap": bool(w1_arrays[grp]["above_cap"][i]),
                # W1 working-only sensitivity
                "W1_workingonly_omega_eur": float(w1_arrays[grp]["omega_working_only"][i]),
                "W1_workingonly_converged": bool(w1_arrays[grp]["converged_working_only"][i]),
                "W1_workingonly_below_floor": bool(w1_arrays[grp]["below_floor_wo"][i]),
                "W1_workingonly_above_cap": bool(w1_arrays[grp]["above_cap_wo"][i]),
                # W6 blocked
                "W6_omega_eur": None,
                "W6_status": "BLOCKED_PENDING_GRID_RATIFICATION",
            })
    out_df = pd.DataFrame(rows).sort_values(["group", "uid"]).reset_index(drop=True)
    _atomic_write_parquet(out_df, _OUT_PARQUET)
    out_sha = _sha256(_OUT_PARQUET)
    print(f"  wrote {_OUT_PARQUET}  rows={len(out_df)}")

    gates_all_pass = bool(
        all(util_gate[g]["pass"] for g in util_gate) and w3_pass and w4_pass and w1_pass)

    manifest = {
        "f4a_artifact": "F4A_manifest_v1",
        "spec_hash": spec_hash, "theta_hash": theta_hash,
        "staged_stem": STAGED_STEM, "cert_stem": CERT_STEM,
        "c_scale": c_scale, "l_scale": l_scale, "beta_c_fixed": BETA_C,
        "theta_c_singles": states["singles_male"].theta_c,
        "preconditions": precond,
        "task0_contract_design_audit": task0,
        "task1_utility_gate": util_gate,
        "task1_synthetic_kappa_gates": synth,
        "task1_analytic_vs_numeric": analytic_synth,
        "task2_w3": w3, "task2_w3_pass": w3_pass,
        "task3_w4": w4, "task3_w4_pass": w4_pass,
        "task4_w1": w1, "task4_w1_pass": w1_pass,
        "task5_w6_design": task0["w6_source_audit"],
        "output_parquet": str(_OUT_PARQUET), "output_parquet_sha256": out_sha,
        "n_rows": int(len(out_df)),
        "gates_all_pass": gates_all_pass,
        "ready_for_f5": False,
        "ready_for_f5_reason": "W6 grid remains unratified",
        "total_elapsed_s": round(time.time() - t0, 1),
    }
    _atomic_write_json(manifest, _OUT_MANIFEST)
    print(f"  wrote {_OUT_MANIFEST}")

    _atomic_write_text(_build_report(manifest), _OUT_DOC)
    print(f"  wrote {_OUT_DOC}")

    print("\n--- CONCLUSIONS ---")
    print(f"PRECONDITIONS_PASS: {precond_ok}")
    print(f"UTILITY GATE (<=1e-9): {all(util_gate[g]['pass'] for g in util_gate)}")
    print(f"W3 (validation): {'PASS' if w3_pass else 'FAIL'}")
    print(f"W4 (num vs analytic <=1e-8): {'PASS' if w4_pass else 'FAIL'}")
    print(f"W1 (synthetic kappa + conv): {'PASS' if w1_pass else 'FAIL'}")
    print("")
    print("READY FOR F5: NO — W6 grid remains unratified.")
    print("REQUIRED NEXT INPUT: explicit ratification of the W6 universal hours grid.")
    print(f"\nF4-A COMPLETE in {round(time.time()-t0,1)}s")


def _build_report(m: dict) -> str:
    pc = m["preconditions"]; t0 = m["task0_contract_design_audit"]
    def grp_tbl(d, cols, fmt):
        lines = ["| group | " + " | ".join(cols) + " |",
                 "|---|" + "---|" * len(cols)]
        for g in ("singles_male", "singles_female"):
            vals = [fmt(d[g][c]) for c in cols]
            lines.append(f"| {g} | " + " | ".join(vals) + " |")
        return "\n".join(lines)
    sci = lambda x: ("n/a" if x is None else (f"{x:.3e}" if isinstance(x, float) else str(x)))
    w6 = t0["w6_source_audit"]
    L = []
    L.append("# RURO Welfare F4-A — Singles Measure Core (W3/W4/W1) + W6 Design Audit\n")
    L.append(f"Date: 2026-06-13 · spec_hash `{m['spec_hash']}` · theta_hash `{m['theta_hash']}` · "
             f"stem `{m['staged_stem']}`\n")
    L.append("Internal validation artifact. No inequality statistic, decomposition, V_dir, EUROMOD "
             "pricing, promotion, or commit. W6 NOT computed (grid unratified).\n")

    L.append("## Provenance & preconditions\n")
    L.append(f"- Consumed: `{pc['consumed_singles_viis_parquet']}`")
    L.append(f"  - SHA256 `{pc['consumed_singles_viis_sha256']}`")
    L.append(f"- Unique non-null HH keys: **{pc['n_unique_nonnull_hh_keys']}** "
             f"(expected {N_SINGLES_EXPECTED}; ok={pc['n_keys_ok']})")
    L.append(f"- spec_hash match: {pc['spec_hash_match']}; theta_hash match: {pc['theta_hash_match']}; "
             f"all input file hashes match manifest: {pc['all_file_hashes_match']}")
    L.append(f"- Gate-0 welfare/engine logsum-negLL parity max|Δ|: **{pc['gate0_logsum_parity_max_abs']:.2e}**")
    L.append(f"- Staged singles negLL reproduced: engine {pc['engine_singles_negll_sum']:.5f} vs "
             f"manifest {pc['staged_negll_sum_manifest']:.5f} (|Δ|={pc['staged_negll_reproduce_diff']:.2e})")
    L.append(f"- **PRECONDITIONS_PASS: {pc['PRECONDITIONS_PASS']}**\n")

    L.append("## Units & scaling (Task 0.2)\n")
    u = t0["units"]
    L.append(f"- Engine consumption: {u['engine_consumption']}; c_scale={u['c_scale']}, l_scale={u['l_scale']}")
    L.append(f"- Solver I/O: {u['solver_io']}")
    L.append(f"- beta_c (fixed) = {u['beta_c_fixed']}; theta_c_singles = {u['theta_c_singles']:.10f} (>0 ⇒ u unbounded above in c)")
    L.append(f"- Consumption floor = {u['consumption_floor_eur']} EUR; Ω units = {u['omega_units']}\n")

    L.append("## Memo status (Task 0.1)\n")
    L.append(f"{t0['memo']['verdict']}")
    L.append(f"(sign-off checklist unchecked items: {t0['memo']['signoff_checklist_unchecked_count']})\n")

    L.append("## W4 home-node audit (Task 0.3)\n")
    L.append("| group | n_hh | zero-home HH | non-unique home leisure | unique state |")
    L.append("|---|---|---|---|---|")
    for g in ("singles_male", "singles_female"):
        a = t0["w4_home_state_audit"][g]
        L.append(f"| {g} | {a['n_hh']} | {a['n_hh_zero_home_nodes']} | "
                 f"{a['n_hh_nonunique_home_leisure']} | {a['unique_home_state']} |")
    L.append(f"\nHome node selection: lowest-draw working==0 alternative (deterministic). "
             f"STOP_W4 = {t0['w4_home_state_audit']['STOP_W4']}.\n")

    L.append("## Utility-only evaluator gate (Task 1)\n")
    L.append(grp_tbl(m["task1_utility_gate"], ["max_abs_u_diff_vs_engine", "pass"],
                     lambda x: (f"{x:.2e}" if isinstance(x, float) else str(x))))
    L.append("\nReconstructed u = leisure_term + beta_c·BoxCox(c_norm; theta_c) vs "
             "estimation_engine.compute_likelihood_singles(return_components=True)['u'].\n")

    L.append("## Synthetic kappa-recovery gates (Task 1 / Task 4)\n")
    L.append("Target recomputed from the SAME transformed reference at known κ, then re-solved.\n")
    L.append("| group | replace κ=1500 max_err | single_node κ=1500 | shift κ=200 | W1 zero-recovery κ=1234 |")
    L.append("|---|---|---|---|---|")
    for g in ("singles_male", "singles_female"):
        s = m["task1_synthetic_kappa_gates"][g]
        zr = m["task4_w1"][g]["synthetic_zero_recovery_kappa"]
        L.append(f"| {g} | {sci(s['replace_kappa1500']['max_abs_recovery_err'])} | "
                 f"{sci(s['single_node_kappa1500']['max_abs_recovery_err'])} | "
                 f"{sci(s['shift_kappa200']['max_abs_recovery_err'])} | "
                 f"{sci(zr['max_abs_recovery_err'])} |")
    L.append("")

    L.append("## W3 — Laissez-faire revalidation (Task 2)\n")
    L.append(grp_tbl(m["task2_w3"],
                     ["ref_at_w0_max_abs_vs_ViIS_staged", "omega_abs_max_converged",
                      "n_nonconverged", "nonconv_lt_0p5pct"], sci))
    L.append(f"\nW3 PASS: **{m['task2_w3_pass']}** (ref value at w=0 ≡ V_i^IS_staged ≤1e-9; "
             "|Ω³|≤1e-8; non-convergence <0.5%).\n")

    L.append("## W4 — Staying-home equivalent (Task 3)\n")
    L.append(grp_tbl(m["task3_w4"],
                     ["num_vs_analytic_max_abs_norm", "n_compared_in_bracket", "n_below_floor",
                      "n_above_cap", "n_genuine_nonconverged", "omega_primary_median_eur"], sci))
    L.append(f"\nW4 PASS: **{m['task3_w4_pass']}** (numerical vs **exact analytic** Box-Cox "
             "inversion ≤1e-8 in normalized consumption units, in-bracket & feasible; below-floor, "
             "above-cap, and genuine non-convergence reported separately; genuine non-convergence "
             "<0.5%).")
    L.append(f"\nPrimary W4 Ω = exact analytic inversion (defined beyond the bracket cap). "
             f"`above_cap` flags households whose staying-home-equivalent income exceeds 50× their "
             f"max observed consumption — not a solver failure. "
             f"Rates: singles_male {m['task3_w4']['singles_male']['above_cap_frac']*100:.1f}%, "
             f"singles_female {m['task3_w4']['singles_female']['above_cap_frac']*100:.1f}%.\n")
    L.append("> **Substantive scale observation (flagged for F5; contract NOT changed).** "
             "W4 Ω values are very large (median ≈ several million EUR). This is correct under the "
             "locked memo definition but is structural, not a bug: the W4 reference is a SINGLE home "
             "node with `no weights` — it carries NO opportunity-density term — whereas the target "
             "V_i^actual = V_i^IS = logsumexp_j(u_j + log ĝ_j − log π_j) DOES. W1/W3 stay at sane "
             "monthly scales because BOTH sides carry the same (log ĝ − log π) terms, which cancel; "
             "W4's single node does not, so the entire opportunity-set inclusive-value scale "
             "(including the −log π importance-sampling correction) must be compensated through "
             "consumption. With near-log consumption utility (theta_c≈"
             f"{m['theta_c_singles']:.4f}) that compensation is exponentially large. This is the "
             "memo's explicit `full-compensation endpoint` (opportunity AND wage priced into w). "
             "Whether the W4 reference target should net out the opportunity-density / IS-correction "
             "scale is a DEFINITIONAL question for ratification at F5 — surfaced here, not resolved.\n")

    L.append("## W1 — Equal-pay over own set (Task 4)\n")
    L.append(grp_tbl(m["task4_w1"],
                     ["n_below_floor", "n_above_cap", "n_nonconverged", "omega_median_eur",
                      "working_only_omega_median_eur"], sci))
    L.append(f"\nW1 PASS: **{m['task4_w1_pass']}**. Pre-registered working-only sensitivity computed "
             "separately (home keeps actual non-employment consumption). Corrected synthetic "
             "zero-recovery (all c_j=κ ⇒ w*=κ) gate reported above.\n")

    L.append("## W6 — Design decision (Task 5, NOT COMPUTED)\n")
    L.append(f"Rule (locked): {w6['rule_locked']}\n")
    L.append("| J node | candidate source | proposed value | BG included? | unresolved decision |")
    L.append("|---|---|---|---|---|")
    L.append("| home | working==0 leisure state | 0h → leisure=TOTAL_LEISURE_HOURS | n/a | time-endowment constant ratification |")
    L.append("| pt1 | estimation band [18.5,21.5] | UNSET (representative hours) | no | which point in band |")
    L.append("| pt2 | estimation band [29.5,30.5] | UNSET | no | which point in band |")
    L.append("| F35 (ref) | estimation reference [33.5,36.5] | UNSET | no | include reference node? |")
    L.append("| ft | estimation band [37.5,40.5] | UNSET | no | which point in band |")
    L.append("| lh | estimation band [44.5,70] | UNSET | no | which point in band |")
    L.append("| (BG?) | D1 background uniform [5,70] | UNSET | UNRESOLVED | include at all? at what hours? |")
    L.append("\nUnresolved governance decisions:")
    for d in w6["unresolved_governance_decisions"]:
        L.append(f"- {d}")
    L.append(f"\nW6 status in output: `BLOCKED_PENDING_GRID_RATIFICATION`.\n")

    L.append("## Outputs\n")
    L.append(f"- `{m['output_parquet']}` (sha256 `{m['output_parquet_sha256']}`, {m['n_rows']} rows)")
    L.append(f"- `{_OUT_MANIFEST.name}` (this manifest)")
    L.append(f"- gates_all_pass: **{m['gates_all_pass']}**\n")

    L.append("---\n")
    L.append("READY FOR F5: NO — W6 grid remains unratified.")
    L.append("REQUIRED NEXT INPUT: explicit ratification of the W6 universal hours grid.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
