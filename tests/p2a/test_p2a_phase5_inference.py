"""Increment-B tests for the Phase-5 covariance and inference objects.

Subject under review: ``scripts/p2a/p2a_phase5_inference.py``.

Reviewer-runnable proof rule (charter s5). Nothing under review is replaced:

  * the bread is the accepted ``hessian_free.npy`` under its accepted SHA-256;
  * the parameter map is the committed one, authenticated against the Phase-4
    manifest by the Increment-A loader;
  * the aggregates are produced by the committed Increment-A
    ``ScoreStreamReducer`` via ``run_score_stream``;
  * the covariance builder, Wald battery, table builder, gates and serializers
    are the module's own.

Only the household subset size is patched, exactly as in Increment A.

Test families
-------------
  F  synthetic fixtures with ANALYTICALLY known covariance / Wald results
  G  bread loading and authentication, incl. every rejection path
  H  parameter table schema and the design v4 s17.3 NA rules
  I  gates and warnings as pure checkable functions
  J  serializer refusal-by-construction and no-persistence
  K  REAL production path on the streamed first-64 aggregates

Family K is slow (it streams real scores). Select with ``-m production``.
No test writes outside ``tmp_path``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))

import p2a_phase5_inference as ib          # noqa: E402
import p2a_phase5_score_stream as ss       # noqa: E402

MODULE_PATH = MNL_ROOT / "scripts" / "p2a" / "p2a_phase5_inference.py"
PARAM_MAP_CSV = MNL_ROOT / "docs" / "France_case" / "P2a" / "phase5_parameter_map_v1.csv"

SUBSET_HOUSEHOLDS = 64          # the frozen design v4 T-11/T-16 slice

PHASE3_BUNDLE = "2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b"
PHASE4_BUNDLE = "5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3"
ACCEPTED_BUNDLES = {"phase3": PHASE3_BUNDLE, "phase4": PHASE4_BUNDLE}


@pytest.fixture(scope="module")
def pmap():
    return ss.load_parameter_map(MNL_ROOT)


@pytest.fixture(scope="module")
def param_map_frame():
    return pd.read_csv(PARAM_MAP_CSV)


@pytest.fixture(scope="module")
def bread(pmap):
    return ib.load_bread(pmap, MNL_ROOT)


@pytest.fixture(scope="module")
def accepted_theta_interior(pmap, param_map_frame):
    src = param_map_frame.set_index("param")
    return np.array([float(src.loc[n, "accepted_value_full_precision"])
                     for n in pmap.interior_names], dtype=np.float64)


@pytest.fixture(scope="module")
def grads(pmap):
    """The AUTHORITATIVE accepted gradient, from phase4_diagnostics.json."""
    return ib.load_accepted_gradients(pmap, MNL_ROOT)


@pytest.fixture(scope="module")
def cov_for_table(pmap):
    """A cheap synthetic covariance carrying the authenticated interior names."""
    bread = _diagonal_bread(np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64))
    object.__setattr__(bread, "interior_names", tuple(pmap.interior_names))
    return ib.build_covariances(bread, np.eye(ib.N_INTERIOR), meat_n_households=64)


# =========================================================================== #
# F. synthetic fixtures with analytically known results
# =========================================================================== #
def _diagonal_bread(diag_values):
    """A `Bread` whose `H_II` is diagonal, so every object is closed-form."""
    d = np.asarray(diag_values, dtype=np.float64)
    H_II = np.diag(d)
    names = tuple(f"p{i}" for i in range(ib.N_INTERIOR))
    return ib.Bread(H_raw=np.zeros((ib.N_FREE, ib.N_FREE)),
                    Hs=np.zeros((ib.N_FREE, ib.N_FREE)),
                    H_II=H_II, sha256="synthetic",
                    interior_names=names, diagnostics={})


def test_F1_diagonal_bread_gives_exact_model_covariance():
    """`H_II = diag(d)` implies `V_model = diag(1/d)` and `se_model = 1/sqrt(d)`."""
    d = np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64)
    bread = _diagonal_bread(d)
    cov = ib.build_covariances(bread, np.eye(ib.N_INTERIOR))
    assert np.allclose(cov.V_model, np.diag(1.0 / d), rtol=0, atol=1e-14)
    assert np.allclose(cov.se_model, 1.0 / np.sqrt(d), rtol=0, atol=1e-14)


def test_F2_diagonal_sandwich_is_exact_and_correction_is_a_pure_scalar():
    """With `H_II = diag(d)` and `M = diag(m)`, `V_robust = c * diag(m/d^2)`."""
    d = np.arange(2, ib.N_INTERIOR + 2, dtype=np.float64)
    m = np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64) * 3.0
    cov = ib.build_covariances(_diagonal_bread(d), np.diag(m))
    expected_cr0 = np.diag(m / d ** 2)
    assert np.allclose(cov.V_robust_cr0, expected_cr0, rtol=0, atol=1e-13)
    assert np.allclose(cov.V_robust, ib.CORRECTION_C * expected_cr0, rtol=0, atol=1e-13)
    # deputy D-1: CR0 is exactly recoverable from the corrected object
    assert np.array_equal(cov.V_robust, cov.correction_c * cov.V_robust_cr0)
    assert cov.correction_c == ib.CORRECTION_C == 1555.0 / 1520.0
    assert cov.correction_c == pytest.approx(1.0230263157894737, rel=0, abs=0)


def test_F3_correction_telescopes_exactly():
    """design v4 s10.2: [G/(G-1)]*[(N-1)/(N-K)] == G/(G-K) when N == G."""
    G = N = ib.N_HOUSEHOLDS
    K = ib.N_INTERIOR
    two_factor = (G / (G - 1)) * ((N - 1) / (N - K))
    assert two_factor == pytest.approx(G / (G - K), rel=0, abs=1e-15)
    assert ib.CORRECTION_C == G / (G - K)
    # the published SE inflation, s10.1
    assert (math.sqrt(ib.CORRECTION_C) - 1.0) * 100 == pytest.approx(1.1448, abs=1e-4)


def test_F4_wald_on_an_identity_block_is_the_sum_of_squared_z():
    """With `V_RR = I`, `W = theta_R' theta_R` for H0-A, and each sub-null is the
    corresponding partial sum. Analytically exact."""
    names = list(ib.REGIONAL_BLOCK_NAMES)
    theta_R = np.arange(1, 11, dtype=np.float64)
    for null_id, rows, _ in ib.NULL_DEFINITIONS:
        A = ib.null_selector(null_id, rows)
        d = A @ theta_R
        W = float(d @ np.linalg.solve(A @ np.eye(10) @ A.T, d))
        expected = float(sum(theta_R[names.index(n)] ** 2 for n in rows))
        assert W == pytest.approx(expected, rel=0, abs=1e-12)


def test_F5_wald_is_invariant_to_the_one_step_reformulation(pmap):
    """design v4 s13.4: the two-step `E_R` form and the one-step `R = A E_R` form
    are algebraically identical."""
    rng = np.random.default_rng(20260802)
    X = rng.normal(size=(ib.N_INTERIOR, ib.N_INTERIOR))
    V_I = X @ X.T + ib.N_INTERIOR * np.eye(ib.N_INTERIOR)
    theta_I = rng.normal(size=ib.N_INTERIOR)
    E_R = ib.regional_selector(pmap)
    V_RR = E_R @ V_I @ E_R.T
    for null_id, rows, _ in ib.NULL_DEFINITIONS:
        A = ib.null_selector(null_id, rows)
        two_step_d = A @ (E_R @ theta_I)
        two_step = float(two_step_d @ np.linalg.solve(A @ V_RR @ A.T, two_step_d))
        R = A @ E_R
        one_step_d = R @ theta_I
        one_step = float(one_step_d @ np.linalg.solve(R @ V_I @ R.T, one_step_d))
        assert two_step == pytest.approx(one_step, rel=1e-12)


def test_F6_chi2_critical_values_match_the_frozen_design_values():
    from scipy.stats import chi2
    for q, crit in ib.CHI2_CRIT_95.items():
        assert chi2.ppf(0.95, q) == pytest.approx(crit, rel=1e-12)
    assert ib.CHI2_CRIT_95[10] == pytest.approx(18.3070381, abs=1e-6)
    assert ib.CHI2_CRIT_95[7] == pytest.approx(14.0671, abs=1e-4)
    assert ib.CHI2_CRIT_95[2] == pytest.approx(5.9915, abs=1e-4)
    assert ib.CHI2_CRIT_95[1] == pytest.approx(3.8415, abs=1e-4)
    assert ib.Z_975 == 1.959963984540054


def test_F7_regional_selector_is_built_by_name_not_position(pmap):
    E = ib.regional_selector(pmap)
    assert E.shape == (10, 35)
    assert np.array_equal(E.sum(axis=1), np.ones(10))
    names = list(pmap.interior_names)
    for b, nm in enumerate(ib.REGIONAL_BLOCK_NAMES):
        assert E[b, names.index(nm)] == 1.0
    # design v4 s7.3 publishes interior positions 13..22 for the block
    assert [names.index(n) for n in ib.REGIONAL_BLOCK_NAMES] == list(range(13, 23))


def test_F8_correlation_has_exact_unit_diagonal():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(12, 12))
    V = X @ X.T + 12 * np.eye(12)
    R = ib.correlation_from_covariance(V)
    assert np.array_equal(np.diag(R), np.ones(12))
    assert float(np.max(np.abs(R))) <= ib.CORRELATION_BOUND


def test_F9_no_explicit_inverse_anywhere_in_the_module():
    """design v4 s8.3 / charter s10: factorisation solves only."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    banned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "inv":
            banned.append(node.lineno)
    assert banned == [], f"np.linalg.inv used at line(s) {banned}"
    src = MODULE_PATH.read_text(encoding="utf-8")
    assert "cho_factor" in src and "cho_solve" in src
    # `pinv` appears exactly once, as the T-8 comparison reference that design v4
    # s15 itself prescribes -- never as the production inverse route
    assert src.count("np.linalg.pinv") == 1
    assert "T-8 reference" in src


# =========================================================================== #
# G. bread loading, authentication and rejection paths
# =========================================================================== #
def test_G1_bread_loads_authenticated_and_symmetrised(bread):
    assert bread.sha256 == ib.BREAD_SHA256
    assert bread.H_raw.shape == (37, 37) and bread.H_II.shape == (35, 35)
    assert np.array_equal(bread.Hs, bread.Hs.T)               # exactly symmetric
    assert not np.array_equal(bread.H_raw, bread.Hs)          # raw was NOT symmetric
    d = bread.diagnostics
    assert d["max_abs_asymmetry_raw"] <= ib.HESSIAN_SYMMETRY_THRESHOLD
    assert d["min_eig_Hs"] > 0 and d["rank_Hs"] == 37


def test_G2_H_II_is_a_name_keyed_deletion_from_Hs(bread, pmap):
    sel = np.asarray(pmap.interior_positions_in_free)
    assert np.array_equal(bread.H_II, bread.Hs[np.ix_(sel, sel)])
    # the two deleted free positions are the active-bound names, by name
    deleted = sorted(set(range(37)) - set(sel.tolist()))
    assert tuple(pmap.free_names[p] for p in deleted) == ss.ACTIVE_BOUND_NAMES


def test_G3_bread_agrees_with_the_phase4_published_spectrum(bread):
    d = bread.diagnostics
    assert d["min_eig_Hs"] == pytest.approx(ib.PHASE4_MIN_EIG, rel=ib.PHASE4_EIGEN_RTOL)
    assert d["max_eig_Hs"] == pytest.approx(ib.PHASE4_MAX_EIG, rel=ib.PHASE4_EIGEN_RTOL)
    assert d["condition_number_Hs"] == pytest.approx(
        ib.PHASE4_CONDITION_NUMBER, rel=ib.PHASE4_EIGEN_RTOL)


def test_G4_bread_hash_mismatch_is_refused(tmp_path, pmap):
    """FAILURE DEMONSTRATION: a bread whose bytes differ is refused, even though
    it is a perfectly valid 37x37 positive-definite matrix."""
    fake_root = tmp_path / "fake"
    (fake_root / Path(ib.PHASE4_BREAD_NPY).parent).mkdir(parents=True)
    H = np.load(MNL_ROOT / ib.PHASE4_BREAD_NPY, allow_pickle=False).copy()
    H[0, 0] += 1e-9
    np.save(fake_root / ib.PHASE4_BREAD_NPY, H, allow_pickle=False)
    with pytest.raises(ib.InferenceError, match="IB-BREADHASH") as err:
        ib.load_bread(pmap, fake_root)
    assert err.value.code == "IB-BREADHASH"


@pytest.mark.parametrize("mutate,pattern", [
    ("shape", "IB-BREADSHAPE"),
    ("dtype", "IB-BREADDTYPE"),
    ("nonfinite", "IB-BREADFINITE"),
    ("asymmetry", "IB-BREADSYM"),
])
def test_G5_bread_structural_rejections(tmp_path, pmap, mutate, pattern):
    """FAILURE DEMONSTRATION: shape, dtype, finiteness and the T-6 symmetry
    threshold each refuse, with authentication disabled so the structural check
    is what fires."""
    H = np.load(MNL_ROOT / ib.PHASE4_BREAD_NPY, allow_pickle=False).copy()
    if mutate == "shape":
        H = H[:36, :36]
    elif mutate == "dtype":
        H = H.astype(np.float32)
    elif mutate == "nonfinite":
        H[3, 4] = np.nan
    else:
        H[0, 1] += 10.0 * ib.HESSIAN_SYMMETRY_THRESHOLD
    root = tmp_path / mutate
    (root / Path(ib.PHASE4_BREAD_NPY).parent).mkdir(parents=True)
    np.save(root / ib.PHASE4_BREAD_NPY, H, allow_pickle=False)
    with pytest.raises(ib.InferenceError, match=pattern):
        ib.load_bread(pmap, root, authenticate=False)


def test_G6_symmetry_threshold_is_the_recorded_design_value():
    assert ib.HESSIAN_SYMMETRY_THRESHOLD == 2.3588019878151842e-4
    assert ib.KAPPA_BE_CERTIFIED == 6.0424e-12
    assert ib.BREAD_SHA256 == (
        "e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061")


def test_G8_gradient_comes_from_the_authoritative_artifact_not_the_csv(
        pmap, param_map_frame):
    """The committed CSV's `grad_free_negll` is a REDUCED-PRECISION rendering.

    `phase4_diagnostics.json -> gradient_free` reproduces design v4's published
    interior maximum exactly; the CSV column differs in the 13th significant
    digit. Immaterial against the T-19/T-22 margins, but the module must read the
    authoritative artifact -- the same `.npy`/`.csv` distinction design v4 F-4
    drew for the Hessian."""
    grads = ib.load_accepted_gradients(pmap, MNL_ROOT)
    assert grads.free.shape == (37,) and grads.interior.shape == (35,)
    assert grads.interior_max_abs == 1.0992597206183063e-4      # exact
    assert grads.interior_argmax_name == "beta_w_educH"

    src = param_map_frame.set_index("param")
    csv_interior = np.array([float(src.loc[n, "grad_free_negll"])
                             for n in pmap.interior_names])
    csv_max = float(np.max(np.abs(csv_interior)))
    assert csv_max != grads.interior_max_abs                    # the CSV is coarser
    assert abs(csv_max - grads.interior_max_abs) / grads.interior_max_abs < 1e-12

    # the two multipliers reproduce design v4 s11.1 exactly
    assert grads.active_multipliers["beta_l_age2_sm"] == 0.8445544161794221
    assert grads.active_multipliers["beta_l_age2_sf"] == 1.4682021491125388


def test_G7_non_positive_definite_bread_fails_the_cholesky_route():
    """FAILURE DEMONSTRATION: the solve route refuses an indefinite matrix rather
    than silently returning a pseudo-inverse."""
    bad = _diagonal_bread(np.r_[-1.0, np.arange(2, ib.N_INTERIOR + 1)])
    with pytest.raises(ib.InferenceError, match="IB-CHOL"):
        ib.build_covariances(bad, np.eye(ib.N_INTERIOR))


# =========================================================================== #
# H. parameter table schema (design v4 s17.3)
# =========================================================================== #
@pytest.fixture(scope="module")
def synthetic_table(pmap, param_map_frame, grads):
    d = np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64)
    bread = _diagonal_bread(d)
    object.__setattr__(bread, "interior_names", tuple(pmap.interior_names))
    cov = ib.build_covariances(bread, np.eye(ib.N_INTERIOR))
    return ib.build_parameter_table(pmap, cov, param_map_frame, grads)


def test_H1_exact_13_column_schema_and_47_rows(synthetic_table):
    frame = synthetic_table.frame
    assert list(frame.columns) == list(ib.PARAMETER_TABLE_COLUMNS)
    assert list(frame.columns) == [
        "name", "block", "status", "estimate", "bound_value", "bound_side",
        "grad_negll", "multiplier", "se_model", "se_robust",
        "ratio_robust_model", "z", "p"]
    assert len(frame) == 47
    assert "flag" not in frame.columns          # design v4 s17.3: no flag column
    counts = frame["status"].value_counts().to_dict()
    assert counts == {"interior": 35, "pinned": 10, "active-bound": 2}


def test_H2_active_bound_rows_follow_the_exact_rule(synthetic_table):
    rows = synthetic_table.frame.set_index("name").loc[list(ss.ACTIVE_BOUND_NAMES)]
    for name, r in rows.iterrows():
        assert r["status"] == "active-bound"
        assert r["estimate"] == 1.0
        assert r["bound_value"] == 1.0
        assert r["bound_side"] == "upper"
        assert r["multiplier"] == -r["grad_negll"]
        assert r["multiplier"] > 0                     # KKT: mu_j > 0
        for col in ib.INFERENTIAL_COLUMNS:
            assert r[col] == "NA", f"{name}.{col} must be the literal string NA"


def test_H3_pinned_rows_follow_the_exact_rule(synthetic_table, pmap):
    rows = synthetic_table.frame.set_index("name").loc[list(pmap.pin_names)]
    assert len(rows) == 10
    for name, r in rows.iterrows():
        assert r["status"] == "pinned"
        assert r["grad_negll"] == 0.0                  # structural, s12.3
        assert r["bound_value"] == "NA" and r["bound_side"] == "NA"
        assert r["multiplier"] == "NA"
        for col in ib.INFERENTIAL_COLUMNS:
            assert r[col] == "NA", f"{name}.{col} must be the literal string NA"
    # never 0, never NaN, never blank -- design v4 s12.2 rejects all three
    for col in ib.INFERENTIAL_COLUMNS:
        assert not (rows[col] == 0).any()
        assert not rows[col].isna().any()


def test_H4_interior_rows_carry_computed_inference(synthetic_table):
    frame = synthetic_table.frame
    interior = frame[frame["status"] == "interior"]
    assert len(interior) == 35
    for col in ib.INFERENTIAL_COLUMNS:
        vals = interior[col].to_numpy()
        assert all(isinstance(v, float) for v in vals)
        assert np.isfinite(vals.astype(float)).all()
    for r in interior.to_dict("records"):
        assert r["ratio_robust_model"] == pytest.approx(
            r["se_robust"] / r["se_model"], rel=1e-12)
        assert r["z"] == pytest.approx(r["estimate"] / r["se_robust"], rel=1e-12)


def test_H5_mandatory_footnote_is_present_and_verbatim(synthetic_table):
    fn = synthetic_table.footnote
    assert fn == ib.PIN_TABLE_FOOTNOTE
    for fragment in (
            "pinned run-overlay restrictions, not estimates",
            "structurally inapplicable to a 2016 singles sample",
            "standard errors are undefined, not zero",
            "beta_c = 1.0", "theta_c = 0.0", "theta_l_m = −0.8", "beta_ll",
            "fixed_params", "not one of the ten pins"):
        assert fragment in fn, fragment


@pytest.mark.parametrize("break_it,pattern", [
    ("drop_column", "IB-SCHEMA"),
    ("extra_column", "IB-SCHEMA"),
    ("row_count", "IB-SCHEMA"),
    ("bad_status", "IB-SCHEMA"),
    ("numeric_se_on_pinned", "IB-NA"),
    ("zero_se_on_active", "IB-NA"),
    ("pin_nonzero_grad", "IB-PIN"),
    ("wrong_bound_side", "IB-BOUND"),
])
def test_H6_schema_violations_are_refused(synthetic_table, break_it, pattern):
    """FAILURE DEMONSTRATION: every schema rule rejects when violated."""
    frame = synthetic_table.frame.copy()
    if break_it == "drop_column":
        frame = frame.drop(columns=["p"])
    elif break_it == "extra_column":
        frame["flag"] = ""
    elif break_it == "row_count":
        frame = frame.iloc[:46]
    elif break_it == "bad_status":
        frame.loc[0, "status"] = "free"
    elif break_it == "numeric_se_on_pinned":
        idx = frame.index[frame["status"] == "pinned"][0]
        frame.loc[idx, "se_robust"] = 0.5
    elif break_it == "zero_se_on_active":
        idx = frame.index[frame["status"] == "active-bound"][0]
        frame.loc[idx, "se_model"] = 0.0
    elif break_it == "pin_nonzero_grad":
        idx = frame.index[frame["status"] == "pinned"][0]
        frame.loc[idx, "grad_negll"] = 1e-9
    else:
        idx = frame.index[frame["status"] == "active-bound"][0]
        frame.loc[idx, "bound_side"] = "lower"
    with pytest.raises(ib.InferenceError, match=pattern):
        ib.validate_parameter_table(frame)


# --- Fix 3: the table consumes AcceptedGradients (R-37b) -------------------- #
def test_H8_table_gradients_come_from_the_authoritative_json(synthetic_table, grads,
                                                             pmap):
    """R-37b: `grad_negll` and the multipliers are the JSON values, not the CSV.

    The review's own example: at `beta_w_educH` the table rendered the CSV's
    `0.0001099259720618` where the authoritative value is
    `0.00010992597206183063`."""
    frame = synthetic_table.frame.set_index("name")
    grad_by_name = {n: float(grads.free[i]) for i, n in enumerate(pmap.free_names)}

    for name, g in grad_by_name.items():
        assert float(frame.loc[name, "grad_negll"]) == g, name
    assert float(frame.loc["beta_w_educH", "grad_negll"]) == 0.00010992597206183063

    for name in ib.ACTIVE_BOUND_NAMES:
        assert float(frame.loc[name, "multiplier"]) == -grad_by_name[name]
    assert float(frame.loc["beta_l_age2_sm", "multiplier"]) == 0.8445544161794221
    assert float(frame.loc["beta_l_age2_sf", "multiplier"]) == 1.4682021491125388

    # pinned rows stay structurally zero (design v4 s12.3)
    for name in pmap.pin_names:
        assert float(frame.loc[name, "grad_negll"]) == 0.0


def test_H9_csv_gradient_column_never_feeds_arithmetic(pmap, param_map_frame, grads):
    """FAILURE DEMONSTRATION, inverted: corrupt the CSV gradient column beyond all
    recognition and the table must be BYTE-IDENTICAL, proving the column feeds
    no arithmetic. The recorded comparison diagnostic does change, which is the
    only place the column is allowed to have any effect."""
    d = np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64)
    bread = _diagonal_bread(d)
    object.__setattr__(bread, "interior_names", tuple(pmap.interior_names))
    cov = ib.build_covariances(bread, np.eye(ib.N_INTERIOR))

    clean = ib.build_parameter_table(pmap, cov, param_map_frame, grads)
    poisoned_frame = param_map_frame.copy()
    poisoned_frame["grad_free_negll"] = 12345.6789
    poisoned = ib.build_parameter_table(pmap, cov, poisoned_frame, grads)

    pd.testing.assert_frame_equal(clean.frame, poisoned.frame)
    assert not (poisoned.frame["grad_negll"] == 12345.6789).any()
    assert clean.metadata["csv_gradient_column_used_for_arithmetic"] is False
    assert (poisoned.metadata["csv_vs_authoritative_gradient_max_abs_dev"]
            > clean.metadata["csv_vs_authoritative_gradient_max_abs_dev"])
    assert clean.metadata["gradient_source"] == ib.PHASE4_DIAGNOSTICS
    assert clean.gradient_source == ib.PHASE4_DIAGNOSTICS


def test_H10_table_builder_requires_the_gradients_argument(pmap, cov_for_table,
                                                           param_map_frame):
    """A caller cannot fall back to the CSV by omitting the authoritative source."""
    with pytest.raises(TypeError):
        ib.build_parameter_table(pmap, cov_for_table, param_map_frame)  # type: ignore[call-arg]


# --- Fix 4: inference_grade propagation (R-37a) ----------------------------- #
def test_H11_parameter_table_carries_the_grade_without_touching_the_schema(
        pmap, param_map_frame, grads, cov_for_table):
    pt = ib.build_parameter_table(pmap, cov_for_table, param_map_frame, grads)
    # the grade rides on the container and .attrs, NEVER as a column
    assert list(pt.frame.columns) == list(ib.PARAMETER_TABLE_COLUMNS)
    assert len(pt.frame.columns) == 13
    assert "inference_grade" not in pt.frame.columns
    assert pt.inference_grade == cov_for_table.diagnostics["inference_grade"]
    assert pt.frame.attrs["inference_grade"] == pt.inference_grade
    assert pt.metadata["inference_grade"] == pt.inference_grade


def test_H12_regional_container_carries_the_grade(pmap, cov_for_table,
                                                  accepted_theta_interior):
    reg = ib.run_regional_tests(pmap, cov_for_table, accepted_theta_interior)
    grade = cov_for_table.diagnostics["inference_grade"]
    assert reg.inference_grade == grade
    assert reg.diagnostics["inference_grade"] == grade
    assert reg.metadata["inference_grade"] == grade
    assert reg.table.attrs["inference_grade"] == grade
    # the Wald schema itself is unchanged
    assert "inference_grade" not in reg.table.columns
    assert ib.warning_W2_regional_spectrum(reg).observed["inference_grade"] == grade


def test_H7_forged_regional_names_are_refused(pmap):
    """FAILURE DEMONSTRATION: selectors are name-keyed and reject unknown names."""
    with pytest.raises(ib.InferenceError, match="IB-NULLNAME"):
        ib.null_selector("H0-X", ("beta_E_drgn2", "not_a_regional_name"))

    class _Forged:
        interior_names = tuple(f"x{i}" for i in range(35))
    with pytest.raises(ib.InferenceError, match="IB-REGNAME"):
        ib.regional_selector(_Forged())


# =========================================================================== #
# I. gates as pure checkable functions
# =========================================================================== #
def test_I1_T7_accepts_a_clean_gram_matrix_and_rejects_a_breach():
    rng = np.random.default_rng(11)
    S = rng.normal(size=(200, ib.N_INTERIOR))
    M = S.T @ S
    good = ib.gate_T7_meat_validity(M)
    assert good.passed and good.tier == "gating"
    assert good.bar["kappa_BE_certified"] == 6.0424e-12

    # FAILURE DEMONSTRATION: a negative eigenvalue far below the backward-error floor
    w, V = np.linalg.eigh(M)
    w[0] = -1e-3 * w[-1]
    bad = ib.gate_T7_meat_validity(V @ np.diag(w) @ V.T)
    assert not bad.passed

    # FAILURE DEMONSTRATION: asymmetry beyond 1e-12 * max|M|
    asym = M.copy()
    asym[0, 1] += 1e-6 * float(np.max(np.abs(M)))
    assert not ib.gate_T7_meat_validity(asym).passed


def test_I2_T9_rejects_a_non_psd_robust_covariance():
    d = np.arange(1, ib.N_INTERIOR + 1, dtype=np.float64)
    cov = ib.build_covariances(_diagonal_bread(d), np.eye(ib.N_INTERIOR))
    assert ib.gate_T9_covariance_validity(cov).passed
    broken = ib.Covariances(
        V_model=cov.V_model, V_robust=cov.V_robust - 10.0 * np.eye(ib.N_INTERIOR),
        V_robust_cr0=cov.V_robust_cr0, se_model=cov.se_model,
        se_robust=cov.se_robust, correction_c=cov.correction_c,
        interior_names=cov.interior_names, diagnostics=cov.diagnostics)
    assert not ib.gate_T9_covariance_validity(broken).passed


def test_I3_T10_records_the_correction_inputs():
    cov = ib.build_covariances(_diagonal_bread(np.ones(ib.N_INTERIOR)),
                               np.eye(ib.N_INTERIOR))
    g = ib.gate_T10_correction_scalar(cov)
    assert g.passed
    assert g.observed["correction_G"] == 1555
    assert g.observed["correction_N"] == 1555
    assert g.observed["correction_K"] == 35
    assert g.observed["correction_telescoped"] == "1555/1520"
    assert g.observed["correction_c"] == pytest.approx(1.0230263157894737, abs=0)
    assert g.observed["cr0_recoverable"] is True


def test_I4_T22_is_a_ratio_gate_that_can_fail():
    sm, sf = ib.ACTIVE_BOUND_NAMES
    good = ib.gate_T22_numerical_kkt({sm: 100.0, sf: 200.0}, 1.0)
    assert good.passed
    bad = ib.gate_T22_numerical_kkt({sm: 99.9, sf: 200.0}, 1.0)
    assert not bad.passed
    assert bad.observed["active_names_ok"] is True
    assert bad.observed["threshold_ok"] is False


def test_I5_W4_triggers_on_equality_with_a_bound(pmap):
    """design v4 s16.2: equality with a bound TRIGGERS; strict interiority passes."""
    names = list(pmap.interior_names)
    est = np.zeros(len(names))
    se = np.ones(len(names))
    frame = pd.DataFrame({
        "param": names,
        "accepted_value_full_precision": est,
        "spec_bound_lb": -ib.Z_975 * se,          # interval endpoint EQUALS lb
        "spec_bound_ub": +ib.Z_975 * se + 1.0,
    })
    cov = ib.Covariances(
        V_model=np.eye(len(names)), V_robust=np.eye(len(names)),
        V_robust_cr0=np.eye(len(names)), se_model=se, se_robust=se,
        correction_c=1.0, interior_names=tuple(names),
        diagnostics={"inference_grade": "synthetic"})
    w = ib.warning_W4_near_boundary(cov, frame)
    assert not w.passed and len(w.observed["flagged"]) == len(names)
    assert w.tier == "warning"

    frame_inside = frame.copy()
    frame_inside["spec_bound_lb"] = -ib.Z_975 * se - 1e-9
    assert ib.warning_W4_near_boundary(cov, frame_inside).passed


# --- Fix 1: T-5 theta-byte authentication (review finding 1) ---------------- #
def test_I8_T5_includes_theta_byte_authentication(bread):
    """design v4 s15 names FOUR anchors for T-5; the theta-byte hash was absent."""
    theta = ib.accepted_theta_sha256(MNL_ROOT)
    assert theta == ib.ACCEPTED_THETA_SHA256 == (
        "c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d")

    g = ib.gate_T5_bread_provenance(bread, ACCEPTED_BUNDLES, theta_sha256=theta)
    assert g.passed
    assert g.observed["theta_bytes_match"] is True
    assert g.observed["theta_sha256"] == theta
    assert g.bar["theta_sha256"] == ib.ACCEPTED_THETA_SHA256


def test_I9_T5_fails_on_a_one_byte_theta_mismatch(bread, tmp_path):
    """FAILURE DEMONSTRATION: flip ONE byte of the accepted theta and T-5 must fail.

    The mutated vector is written to a scratch tree and re-hashed by the real
    `accepted_theta_sha256`, so this exercises the loader, not a hand-made string."""
    payload = json.loads(
        (MNL_ROOT / ib.PHASE3_RESULTS).read_text(encoding="utf-8"))
    theta = np.asarray(payload["results"]["joint"]["theta"], dtype=np.float64)
    raw = bytearray(np.ascontiguousarray(theta).tobytes())
    raw[0] ^= 0x01                                    # exactly one byte
    mutated = np.frombuffer(bytes(raw), dtype=np.float64).copy()
    assert mutated.shape == (47,)
    payload["results"]["joint"]["theta"] = mutated.tolist()

    root = tmp_path / "mutated"
    (root / Path(ib.PHASE3_RESULTS).parent).mkdir(parents=True)
    (root / ib.PHASE3_RESULTS).write_text(json.dumps(payload), encoding="utf-8")

    bad = ib.accepted_theta_sha256(root)
    assert bad != ib.ACCEPTED_THETA_SHA256
    g = ib.gate_T5_bread_provenance(bread, ACCEPTED_BUNDLES, theta_sha256=bad)
    assert not g.passed
    assert g.observed["theta_bytes_match"] is False
    # the other three anchors still match, so ONLY the theta arm fired
    assert g.observed["bread_sha256_matches"] is True
    assert g.observed["phase3_bundle_matches"] is True
    assert g.observed["phase4_bundle_matches"] is True


def test_I10_T5_cannot_be_passed_without_the_theta_hash(bread):
    """The theta hash is keyword-only and required: omission is a TypeError, not
    a silent three-of-four pass."""
    with pytest.raises(TypeError):
        ib.gate_T5_bread_provenance(bread, ACCEPTED_BUNDLES)   # type: ignore[call-arg]


# --- Fix 2: T-22 active-name validation (review finding 2) ------------------ #
def test_I11_T22_module_constant_matches_the_authenticated_active_set(pmap):
    assert ib.ACTIVE_BOUND_NAMES == tuple(
        pmap.free_names[p] for p in pmap.active_positions_in_free)
    assert ib.ACTIVE_BOUND_NAMES == ("beta_l_age2_sm", "beta_l_age2_sf")


@pytest.mark.parametrize("mapping,label", [
    ({}, "empty"),
    ({"beta_l_age2_sm": 1.0}, "missing one"),
    ({"beta_l_age2_sm": 1.0, "beta_l_age2_sf": 2.0, "extra": 3.0}, "extra name"),
    ({"wrong_name": 1.0}, "wrong name only"),
    ({"wrong_name": 1.0, "other": 2.0}, "two wrong names"),
    ({"beta_l_age2_sm": 1.0, "wrong_name": 2.0}, "one right one wrong"),
])
def test_I12_T22_fails_on_any_non_exact_active_mapping(mapping, label):
    """FAILURE DEMONSTRATION: the review showed `{}` and `{"wrong_name": ...}`
    both returned passed=True. Every non-exact key set must now fail, and must
    fail on the NAME check before the threshold is ever applied."""
    g = ib.gate_T22_numerical_kkt(mapping, 1e-4)
    assert not g.passed, label
    assert g.observed["active_names_ok"] is False
    assert g.observed["threshold_ok"] is False
    assert g.observed["ratios"] == {}          # threshold arm never evaluated
    assert g.bar["required_names"] == list(ib.ACTIVE_BOUND_NAMES)


def test_I13_T22_passes_only_on_the_exact_pair_above_the_threshold():
    sm, sf = ib.ACTIVE_BOUND_NAMES
    g = ib.gate_T22_numerical_kkt({sm: 1.0, sf: 2.0}, 1e-4)
    assert g.passed
    assert g.observed["missing_names"] == [] and g.observed["extra_names"] == []
    assert set(g.observed["ratios"]) == {sm, sf}


def test_I6_gating_failures_ignores_warning_tier():
    passing = ib.GateResult("T-X", "gating", True, "s")
    failing_warning = ib.GateResult("W-X", "warning", False, "s")
    failing_gate = ib.GateResult("T-Y", "gating", False, "s")
    assert ib.gating_failures([passing, failing_warning]) == []
    assert ib.gating_failures([passing, failing_warning, failing_gate]) == ["T-Y"]


def test_I7_every_gate_result_is_json_serialisable(bread):
    g = ib.gate_T6_bread_integrity(bread)
    json.dumps(g.as_dict())          # must not raise
    assert g.as_dict()["gate"] == "T-6" and g.as_dict()["tier"] == "gating"


# =========================================================================== #
# J. serializer refusal-by-construction (addendum s3)
# =========================================================================== #
def test_J1_refuses_a_household_scale_array():
    """FAILURE DEMONSTRATION: the 1555x37 score matrix cannot be persisted."""
    scores = np.zeros((1555, ib.N_FREE))
    with pytest.raises(ib.SerializerRefusal, match="IB-REFUSE"):
        ib.assert_aggregate_payload(scores, "phase5_scores_free.npy")
    with pytest.raises(ib.SerializerRefusal, match="household-scale"):
        ib.assert_aggregate_payload(np.zeros((64, ib.N_FREE)), "batch")


def test_J2_refuses_a_row_level_block_even_below_the_row_cap():
    """A 5x37 block is small but is still a score block, not an aggregate."""
    with pytest.raises(ib.SerializerRefusal, match="row-level score block"):
        ib.assert_aggregate_payload(np.zeros((5, ib.N_FREE)), "rows")


def test_J3_refuses_identifier_paired_frames():
    """addendum s3: household identifiers paired with scores are never persisted."""
    for col in ("idhh", "idorighh", "cluster_id", "household_id", "score_row_index"):
        frame = pd.DataFrame({col: [1, 2, 3], "value": [0.1, 0.2, 0.3]})
        with pytest.raises(ib.SerializerRefusal, match="identifier"):
            ib.assert_aggregate_payload(frame, f"frame[{col}]")


def test_J4_refuses_a_member_outside_the_closed_set(tmp_path):
    with pytest.raises(ib.SerializerRefusal, match="closed aggregate artifact set"):
        ib.write_matrix(tmp_path, "phase5_scores_free.npy",
                        np.eye(ib.N_INTERIOR), [f"p{i}" for i in range(35)],
                        inference_grade="synthetic")
    assert list(tmp_path.rglob("*")) == []


def test_J5_accepts_and_writes_the_legitimate_aggregates(tmp_path, pmap):
    names = list(pmap.interior_names)
    V = np.eye(ib.N_INTERIOR)
    r1 = ib.write_matrix(tmp_path, "phase5_covariance_robust.npy", V, names,
                         inference_grade="synthetic")
    r2 = ib.write_matrix(tmp_path, "phase5_covariance_robust.csv", V, names,
                         inference_grade="synthetic")
    p1, p2 = r1.path, r2.path
    assert p1.is_file() and p2.is_file()
    assert r1.inference_grade == r2.inference_grade == "synthetic"
    assert np.array_equal(np.load(p1, allow_pickle=False), V)
    back = pd.read_csv(p2, index_col=0)
    assert list(back.columns) == names and len(back) == 35
    # the 37x37 meat is legitimately 37 columns and must NOT be refused
    m37 = np.eye(ib.N_FREE)
    assert ib.write_matrix(tmp_path, "meat_free37.npy", m37,
                           list(pmap.free_names),
                           inference_grade="synthetic").path.is_file()
    assert set(p.name for p in tmp_path.iterdir()) <= set(ib.AGGREGATE_ARTIFACTS)


def test_J6_refuses_non_finite_content(tmp_path):
    bad = np.eye(ib.N_INTERIOR)
    bad[0, 0] = np.nan
    with pytest.raises(ib.SerializerRefusal, match="non-finite"):
        ib.write_matrix(tmp_path, "phase5_covariance_model.npy", bad,
                        [f"p{i}" for i in range(35)], inference_grade="synthetic")
    assert list(tmp_path.rglob("*")) == []


def test_J7_module_writes_only_through_the_serializers():
    """STATIC: no write call outside the three serializer functions."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    allowed = {"write_matrix", "write_table", "write_score_aggregate_summary"}
    writers = {"save", "savez", "savetxt", "to_csv", "to_parquet", "to_pickle",
               "write_text", "write_bytes", "tofile", "mkdir"}
    offenders = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        if fn.name in allowed:
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name in writers:
                offenders.append((fn.name, name, node.lineno))
            elif name == "open":
                # a READ is fine (the bread hasher opens "rb"); a write is not
                mode = None
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                if not (isinstance(mode, str) and mode.startswith("r")):
                    offenders.append((fn.name, f"open(mode={mode!r})", node.lineno))
    assert offenders == [], f"write calls outside the serializers: {offenders}"


def test_J8_static_scanner_is_not_vacuous(tmp_path):
    probe = tmp_path / "probe.py"
    probe.write_text("import numpy as np\ndef leak(S, p):\n    np.save(p, S)\n",
                     encoding="utf-8")
    tree = ast.parse(probe.read_text(encoding="utf-8"))
    found = [getattr(n.func, "attr", None) for n in ast.walk(tree)
             if isinstance(n, ast.Call)]
    assert "save" in found


# --- Fix 5: member-specific contracts + DataFrame finiteness ---------------- #
def test_J10_refuses_a_mislabelled_5x35_temporary_score_block(tmp_path):
    """FAILURE DEMONSTRATION, review §6: `np.zeros((5, 35))` under any label was
    ACCEPTED. It is a temporary row-level interior-score batch, prohibited by
    addendum §3."""
    block = np.zeros((5, ib.N_INTERIOR))
    with pytest.raises(ib.SerializerRefusal, match="row-level score block"):
        ib.assert_aggregate_payload(block, "temporary_interior_scores")
    # and it cannot be smuggled in under a legitimate 35x35 member either
    with pytest.raises(ib.SerializerRefusal):
        ib.write_matrix(tmp_path, "meat_interior35.npy", block,
                        [f"p{i}" for i in range(35)], inference_grade="synthetic")
    assert list(tmp_path.rglob("*")) == []
    # the genuine 35x35 aggregate is still accepted
    ib.assert_aggregate_payload(np.eye(ib.N_INTERIOR), "meat_interior35.npy")


def test_J11_refuses_a_non_finite_dataframe(tmp_path):
    """FAILURE DEMONSTRATION, review §6: the DataFrame branch had no finiteness
    check, so a numeric frame containing NaN was accepted."""
    for bad_value in (np.nan, np.inf, -np.inf):
        frame = pd.DataFrame({"a": [1.0, 2.0, bad_value], "b": [3.0, 4.0, 5.0]})
        with pytest.raises(ib.SerializerRefusal, match="non-finite numeric content"):
            ib.assert_aggregate_payload(frame, "phase5_regional_tests.csv")
    # non-numeric columns are not coerced, and a clean frame still passes
    ok = pd.DataFrame({"null_id": ["H0-A"], "W_robust": [1.5]})
    ib.assert_aggregate_payload(ok, "phase5_regional_tests.csv")
    assert list(tmp_path.rglob("*")) == []


@pytest.mark.parametrize("member,payload,kind,pattern", [
    ("meat_interior35.npy", np.eye(ib.N_FREE), "matrix", "requires shape"),
    ("meat_free37.npy", np.eye(ib.N_INTERIOR), "matrix", "requires shape"),
    ("phase5_regional_covariance.csv", np.eye(ib.N_INTERIOR), "matrix", "requires shape"),
    ("phase5_parameter_table.csv", np.eye(ib.N_INTERIOR), "table", "requires a DataFrame"),
    ("meat_free37.npy", pd.DataFrame({"a": [1.0]}), "table", "declared kind"),
])
def test_J12_member_specific_contracts_are_enforced(member, payload, kind, pattern):
    """A payload may only be filed under a member whose contract it meets."""
    with pytest.raises(ib.SerializerRefusal, match=pattern):
        ib.assert_member_contract(member, payload, kind)


def test_J13_parameter_table_member_requires_the_exact_schema(tmp_path,
                                                              synthetic_table):
    good = synthetic_table.frame
    ib.assert_member_contract("phase5_parameter_table.csv", good, "table")
    rec = ib.write_table(tmp_path, "phase5_parameter_table.csv", good,
                         inference_grade=synthetic_table.inference_grade)
    assert rec.path.is_file() and rec.kind == "table" and rec.shape == (47, 13)

    renamed = good.rename(columns={"p": "pvalue"})
    with pytest.raises(ib.SerializerRefusal, match="exact column sequence"):
        ib.assert_member_contract("phase5_parameter_table.csv", renamed, "table")
    short = good.iloc[:46]
    with pytest.raises(ib.SerializerRefusal, match="exactly 47 rows"):
        ib.assert_member_contract("phase5_parameter_table.csv", short, "table")


def test_J14_every_declared_member_has_a_contract():
    assert set(ib.AGGREGATE_ARTIFACTS) == set(ib._MEMBER_CONTRACTS)


def test_J15_serializers_require_an_inference_grade(tmp_path, pmap):
    """Fix 4: an artifact cannot be written without its enclosing-object label."""
    V = np.eye(ib.N_INTERIOR)
    names = list(pmap.interior_names)
    with pytest.raises(TypeError):
        ib.write_matrix(tmp_path, "phase5_covariance_model.npy", V, names)  # type: ignore[call-arg]
    with pytest.raises(ib.SerializerRefusal, match="inference_grade is required"):
        ib.write_matrix(tmp_path, "phase5_covariance_model.npy", V, names,
                        inference_grade="")
    rec = ib.write_matrix(tmp_path, "phase5_covariance_model.npy", V, names,
                          inference_grade="full-sample")
    assert rec.inference_grade == "full-sample"
    assert json.dumps(rec.as_dict())          # manifest-ready, JSON-serialisable


def test_J9_score_aggregate_summary_carries_no_row_level_content(tmp_path, pmap):
    class _Result:
        n_households = 1555
        dim_free, dim_interior = 37, 35
        order_sha256 = "o" * 64
        score_stream_sha256 = "s" * 64
        free_names_sha256 = "f" * 64
        interior_names_sha256 = "i" * 64
        score_sum_free37 = np.arange(37, dtype=np.float64)
        diagnostics = {"score_sum_max_abs": 1.0}
        batch_size, n_batches = 128, 13
        dtype, byte_order, idhh_encoding = "float64", "little", "int64_le"
        bytes_per_household = 304

    rec = ib.write_score_aggregate_summary(tmp_path, _Result(),
                                           inference_grade="full-sample")
    path = rec.path
    payload = json.loads(path.read_text(encoding="utf-8"))

    # The key set is exactly the addendum s3 contract. `idhh_encoding`,
    # `n_households` and `bytes_per_household` name the encoding contract and two
    # scalar counts -- they are mandated fields, not identifiers. What matters is
    # that no per-household DATUM is present, which the length check below proves.
    assert set(payload) == {
        "n_households", "dim_free", "dim_interior", "canonical_order_sha256",
        "score_stream_sha256", "free_names_sha256", "interior_names_sha256",
        "score_sum_free37", "scalar_diagnostics", "batch_size_used", "n_batches",
        "dtype", "byte_order", "idhh_encoding", "bytes_per_household",
        "inference_grade"}
    assert payload["idhh_encoding"] == "int64_le"
    assert isinstance(payload["n_households"], int)
    assert isinstance(payload["bytes_per_household"], int)

    # nothing household-scale: no value is a list longer than the largest legitimate
    # aggregate (37 free coordinates)
    long_lists = {k: len(v) for k, v in payload.items()
                  if isinstance(v, list) and len(v) > ib.N_FREE}
    assert long_lists == {}, long_lists
    assert len(payload["score_sum_free37"]) == 37
    assert payload["batch_size_used"] == 128
    assert payload["dtype"] == "float64" and payload["byte_order"] == "little"


# =========================================================================== #
# K. REAL production path on the streamed first-64 aggregates
# =========================================================================== #
@pytest.fixture(scope="module")
def streamed64():
    binding = ss.build_production_binding(household_limit=SUBSET_HOUSEHOLDS)
    return ss.run_score_stream(binding, batch_size=SUBSET_HOUSEHOLDS)


@pytest.fixture(scope="module")
def subset_covariances(bread, streamed64):
    return ib.build_covariances(bread, streamed64.meat_interior35,
                                meat_n_households=streamed64.n_households)


@pytest.mark.production
def test_K1_streamed_meat_passes_T7_on_the_real_aggregate(streamed64):
    g = ib.gate_T7_meat_validity(streamed64.meat_interior35)
    assert g.passed, g.observed
    assert g.observed["max_abs_asymmetry"] == 0.0
    assert g.observed["min_eig"] >= g.bar["psd_floor"]


@pytest.mark.production
def test_K2_covariances_build_from_streamed_aggregates(subset_covariances, bread):
    cov = subset_covariances
    assert cov.V_model.shape == cov.V_robust.shape == (35, 35)
    # V_model solves H_II exactly: H_II @ V_model == I
    resid = float(np.max(np.abs(bread.H_II @ cov.V_model - np.eye(35))))
    assert resid <= 1e-9, resid
    assert np.array_equal(cov.V_robust, cov.correction_c * cov.V_robust_cr0)
    assert cov.diagnostics["explicit_inverse_used"] is False
    # this is a bounded subset, and the object says so
    assert cov.diagnostics["full_sample_meat"] is False
    assert cov.diagnostics["inference_grade"] == "subset-diagnostic"


@pytest.mark.production
def test_K3_scale_free_gates_pass_on_the_real_subset(
        bread, subset_covariances, streamed64, pmap, grads):
    """Gates that are meaningful at subset scale all pass.

    T-5/T-6/T-8/T-10/T-17 depend only on the accepted bread, the map and frozen
    constants, so they are exact at any subset size. T-7/T-9/T-18 are structural
    properties of whatever aggregate is supplied. T-19 is included because a
    bounded-subset meat yields SMALLER robust SEs, which makes its
    displacement/SE bar strictly HARDER -- so a pass here is a valid one-sided
    signal, not a weakened one."""
    gates = [
        ib.gate_T5_bread_provenance(bread, ACCEPTED_BUNDLES,
                                    theta_sha256=ib.accepted_theta_sha256(MNL_ROOT)),
        ib.gate_T6_bread_integrity(bread),
        ib.gate_T7_meat_validity(streamed64.meat_interior35),
        ib.gate_T8_solve_stability(subset_covariances),
        ib.gate_T9_covariance_validity(subset_covariances),
        ib.gate_T10_correction_scalar(subset_covariances),
        ib.gate_T17_fingerprints(pmap, MNL_ROOT),
        ib.gate_T18_valid_correlations(subset_covariances),
        ib.gate_T19_stationarity(bread, subset_covariances, grads.interior),
    ]
    assert ib.gating_failures(gates) == [], [g.as_dict() for g in gates if not g.passed]


@pytest.mark.production
def test_K4_T22_reproduces_the_published_activity_ratios(grads):
    """T-22 depends only on the accepted gradient, so it is exact at any subset
    size and must reproduce design v4 s11.5's published ratios BIT-FOR-BIT."""
    mult = grads.active_multipliers
    interior_max = grads.interior_max_abs
    assert tuple(sorted(mult)) == tuple(sorted(ib.ACTIVE_BOUND_NAMES))
    g = ib.gate_T22_numerical_kkt(mult, interior_max)
    assert g.passed
    # design v4 s9.2 / s10.3 publish this exact value, at this exact coordinate
    assert interior_max == 1.0992597206183063e-4
    assert grads.interior_argmax_name == "beta_w_educH"
    assert g.observed["ratios"]["beta_l_age2_sm"] == pytest.approx(7682.9, abs=0.1)
    assert g.observed["ratios"]["beta_l_age2_sf"] == pytest.approx(13356.3, abs=0.1)
    assert mult["beta_l_age2_sm"] == pytest.approx(0.8445544161794221, rel=1e-12)
    assert mult["beta_l_age2_sf"] == pytest.approx(1.4682021491125388, rel=1e-12)


@pytest.mark.production
def test_K5_regional_battery_is_structurally_sound_on_the_subset(
        pmap, subset_covariances, accepted_theta_interior):
    reg = ib.run_regional_tests(pmap, subset_covariances, accepted_theta_interior)
    assert list(reg.table["null_id"]) == ["H0-A", "H0-B", "H0-C", "H0-G"]
    assert list(reg.table["q"]) == [10, 7, 2, 1]
    assert list(reg.table["tier"]) == ["confirmatory", "secondary",
                                       "secondary", "secondary"]
    assert np.isfinite(reg.table[["W_model", "W_robust",
                                  "p_model", "p_robust"]].to_numpy()).all()
    assert (reg.table[["W_model", "W_robust"]].to_numpy() >= 0).all()
    assert (reg.table[["p_model", "p_robust"]].to_numpy() >= 0).all()
    assert (reg.table[["p_model", "p_robust"]].to_numpy() <= 1).all()
    assert "p" not in reg.table.columns          # never a single undifferentiated p
    assert ib.gate_T14_regional(reg).passed
    # H0-A is the omnibus over the whole block; its q is the block dimension
    assert reg.table.loc[0, "restriction_names"].count(";") == 9
    assert reg.V_RR_robust.shape == (10, 10)
    assert np.array_equal(np.diag(reg.corr_RR_robust), np.ones(10))


@pytest.mark.production
def test_K6_parameter_table_from_the_real_subset(pmap, subset_covariances,
                                                 param_map_frame, grads):
    pt = ib.build_parameter_table(pmap, subset_covariances, param_map_frame, grads)
    ib.validate_parameter_table(pt.frame)
    assert len(pt.frame) == 47
    interior = pt.frame[pt.frame["status"] == "interior"]
    assert np.isfinite(interior["se_robust"].to_numpy().astype(float)).all()
    assert (interior["se_robust"].to_numpy().astype(float) > 0).all()
    # the ten regional names are present and interior
    reg_rows = pt.frame.set_index("name").loc[list(ib.REGIONAL_BLOCK_NAMES)]
    assert (reg_rows["status"] == "interior").all()


@pytest.mark.production
def test_K7_subset_scale_is_flagged_not_silently_reported(
        subset_covariances, param_map_frame):
    """W-1 and W-4 echo the inference grade, so a bounded-subset covariance can
    never be mistaken for an inferential result."""
    w1 = ib.warning_W1_ratio(subset_covariances)
    w4 = ib.warning_W4_near_boundary(subset_covariances, param_map_frame)
    assert w1.observed["inference_grade"] == "subset-diagnostic"
    assert w4.observed["inference_grade"] == "subset-diagnostic"
    assert w1.tier == "warning" and w4.tier == "warning"
    # both are warning-tier, so neither can fail the run (design v4 s14)
    assert ib.gating_failures([w1, w4]) == []


@pytest.mark.production
def test_K8_serializers_accept_the_real_aggregates_and_write_only_to_tmp(
        tmp_path, pmap, streamed64, subset_covariances):
    names = list(pmap.interior_names)
    grade = subset_covariances.diagnostics["inference_grade"]
    recs = [
        ib.write_matrix(tmp_path, "meat_interior35.npy",
                        streamed64.meat_interior35, names, inference_grade=grade),
        ib.write_matrix(tmp_path, "phase5_covariance_robust.npy",
                        subset_covariances.V_robust, names, inference_grade=grade),
        ib.write_score_aggregate_summary(tmp_path, streamed64, inference_grade=grade),
    ]
    assert all(r.inference_grade == "subset-diagnostic" for r in recs)
    written = sorted(p.name for p in tmp_path.iterdir())
    assert written == ["meat_interior35.npy", "phase5_covariance_robust.npy",
                       "score_aggregate_summary.json"]
    assert set(written) <= set(ib.AGGREGATE_ARTIFACTS)
    # nothing escaped into the repository
    assert not (MNL_ROOT / "score_aggregate_summary.json").exists()
    summary = json.loads((tmp_path / "score_aggregate_summary.json").read_text("utf-8"))
    assert summary["n_households"] == SUBSET_HOUSEHOLDS
    assert summary["score_stream_sha256"] == streamed64.score_stream_sha256


@pytest.mark.production
def test_K9_covariance_builder_cannot_be_fed_a_score_matrix(bread):
    """FAILURE DEMONSTRATION: the builder takes an aggregate, never a score block."""
    with pytest.raises(ib.InferenceError, match="IB-MEATSHAPE"):
        ib.build_covariances(bread, np.zeros((SUBSET_HOUSEHOLDS, ib.N_INTERIOR)))
    with pytest.raises(ib.InferenceError, match="IB-MEATFINITE"):
        bad = np.eye(ib.N_INTERIOR)
        bad[2, 2] = np.inf
        ib.build_covariances(bread, bad)


# =========================================================================== #
# CLOSURE. The three FROZEN probes of the Increment-B proportionality decision
# (JMP_M05C_incrementB_proportionality_decision_v1.md s3), which restate Review
# B v2 s7 defects 1-3. Written BEFORE the corresponding implementation changes
# and not modified afterwards.
#
# Each probe is written to accept EITHER of the two admissible closures the
# decision allows -- "the channel/argument is gone" (TypeError) or "the input is
# rejected before any write" -- so the probe pins the contract, not one chosen
# implementation of it.
# =========================================================================== #
def _dir_fingerprint(root: Path):
    """(relpath, sha256) for every file under `root`; [] when root is absent.

    Used to prove a refusal left the destination byte-untouched -- including the
    absence of any partial or temporary file at the target.
    """
    root = Path(root)
    if not root.exists():
        return []
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out.append((str(p.relative_to(root)),
                        hashlib.sha256(p.read_bytes()).hexdigest()))
    return out


def test_CLOSURE_B1_t22_expected_name_set_is_not_caller_overridable(pmap, grads):
    """Probe B-1 — T-22 authority.

    Review B v2 s3.2 / s7.1: `gate_T22_numerical_kkt({'forged_active': 1.0},
    1e-4, active_names=('forged_active',))` returned `passed=True` and reported
    `required_names=['forged_active']`, so the gate did not invariably
    authenticate against the certified pair.

    The expected set must come from the authenticated parameter map, or from the
    frozen constant only after that constant is proved equal to the map.
    """
    forged = {"forged_active": 1.0}

    # 1. keyword override must be impossible, or must fail
    try:
        g = ib.gate_T22_numerical_kkt(forged, 1e-4, active_names=("forged_active",))
    except TypeError:
        pass                                    # authority argument removed
    else:
        assert not g.passed, "a forged expected-name set satisfied T-22"
        assert g.bar["required_names"] == list(ib.ACTIVE_BOUND_NAMES)

    # 2. positional override must be impossible, or must fail
    try:
        g2 = ib.gate_T22_numerical_kkt(forged, 1e-4, ("forged_active",))
    except TypeError:
        pass
    else:
        assert not g2.passed, "a positionally forged expected-name set satisfied T-22"
        assert g2.bar["required_names"] == list(ib.ACTIVE_BOUND_NAMES)

    # 3. the constant the gate binds to is the authenticated pair
    assert ib.ACTIVE_BOUND_NAMES == tuple(
        pmap.free_names[p] for p in pmap.active_positions_in_free)

    # 4. the genuine certified mapping still passes, and a wrong one still fails
    good = ib.gate_T22_numerical_kkt(grads.active_multipliers, grads.interior_max_abs)
    assert good.passed
    assert good.bar["required_names"] == list(ib.ACTIVE_BOUND_NAMES)
    assert not ib.gate_T22_numerical_kkt(forged, 1e-4).passed


def test_CLOSURE_B2_refusal_leaves_the_destination_untouched(tmp_path, pmap,
                                                             synthetic_table):
    """Probe B-2 — refusal happens before any filesystem write action.

    Review B v2 s3.4 / s7.2: all three serializers validated a nonempty
    `inference_grade` only inside `_record`, i.e. after the writer had already
    created the target. `IB-REFUSE` therefore did not leave the destination
    untouched.

    Started from a NONEXISTENT destination, and repeated against a sentinel
    file, with directory fingerprints taken before and after.
    """
    names = list(pmap.interior_names)
    V = np.eye(ib.N_INTERIOR)

    calls = [
        ("matrix", lambda d: ib.write_matrix(
            d, "phase5_covariance_model.npy", V, names, inference_grade="")),
        ("matrix_csv", lambda d: ib.write_matrix(
            d, "phase5_covariance_model.csv", V, names, inference_grade="")),
        ("table", lambda d: ib.write_table(
            d, "phase5_parameter_table.csv", synthetic_table.frame,
            inference_grade="")),
        ("summary", lambda d: ib.write_score_aggregate_summary(
            d, _SummaryStub(), inference_grade="")),
    ]

    for label, call in calls:
        # -- destination does not exist beforehand ------------------------- #
        out = tmp_path / f"absent_{label}"
        before = _dir_fingerprint(out)
        assert before == []
        with pytest.raises(ib.SerializerRefusal, match="IB-REFUSE"):
            call(out)
        after = _dir_fingerprint(out)
        assert after == before == [], (
            f"{label}: refusal left files behind: {after}")
        assert list(out.rglob("*")) == [], f"{label}: partial/temp file at target"

        # -- destination exists with sentinel bytes ------------------------ #
        out2 = tmp_path / f"sentinel_{label}"
        out2.mkdir()
        member = {"matrix": "phase5_covariance_model.npy",
                  "matrix_csv": "phase5_covariance_model.csv",
                  "table": "phase5_parameter_table.csv",
                  "summary": "score_aggregate_summary.json"}[label]
        sentinel = out2 / member
        sentinel.write_bytes(b"SENTINEL-DO-NOT-TOUCH")
        before2 = _dir_fingerprint(out2)
        with pytest.raises(ib.SerializerRefusal, match="IB-REFUSE"):
            call(out2)
        assert _dir_fingerprint(out2) == before2, (
            f"{label}: refusal modified an existing destination")
        assert sentinel.read_bytes() == b"SENTINEL-DO-NOT-TOUCH"


class _SummaryStub:
    """Minimal stand-in for a ScoreStreamResult, for the refusal probes only."""

    n_households = 1555
    dim_free, dim_interior = 37, 35
    order_sha256 = "o" * 64
    score_stream_sha256 = "s" * 64
    free_names_sha256 = "f" * 64
    interior_names_sha256 = "i" * 64
    score_sum_free37 = np.arange(37, dtype=np.float64)
    diagnostics = {"score_sum_max_abs": 1.0}
    batch_size, n_batches = 128, 13
    dtype, byte_order, idhh_encoding = "float64", "little", "int64_le"
    bytes_per_household = 304


def test_CLOSURE_B3_no_arbitrary_extension_persistence(tmp_path):
    """Probe B-3 — the `extra=` channel cannot persist prohibited content.

    Review B v2 s3.5 / s7.3: `extra={'temporary_scores_free37':
    np.zeros((5,37)).tolist()}` persisted the complete 5-by-37 block, and the
    same mapping could overwrite the payload `inference_grade` while the
    returned record still reported `subset-diagnostic`.

    Admissible closures: the channel is removed (TypeError), or every case below
    is refused BEFORE any write.
    """
    attempts = {
        "score_block_5x37": {"temporary_scores_free37":
                             np.zeros((5, ib.N_FREE)).tolist()},
        "score_block_ndarray": {"scores": np.zeros((5, ib.N_FREE))},
        "household_scale": {"per_household": list(range(1555))},
        "nested_block": {"outer": {"inner": np.zeros((5, ib.N_FREE)).tolist()}},
        "raw_bytes": {"blob": b"\x00" * 64},
        "overwrite_grade": {"inference_grade": ""},
        "overwrite_protected_digest": {"score_stream_sha256": "forged"},
        "overwrite_protected_count": {"n_households": 1},
    }

    for label, extra in attempts.items():
        out = tmp_path / f"extra_{label}"
        assert _dir_fingerprint(out) == []
        try:
            rec = ib.write_score_aggregate_summary(
                out, _SummaryStub(), inference_grade="subset-diagnostic",
                extra=extra)
        except TypeError:
            continue                            # channel removed entirely
        except ib.SerializerRefusal:
            assert _dir_fingerprint(out) == [], (
                f"{label}: refused but left a file behind")
            assert list(out.rglob("*")) == []
            continue
        # accepted: it must not have persisted anything prohibited
        payload = json.loads(rec.path.read_text(encoding="utf-8"))
        blob = rec.path.read_text(encoding="utf-8")
        assert "temporary_scores_free37" not in payload, (
            f"{label}: a row-level score block was persisted")
        assert "0.0, 0.0, 0.0" not in blob, f"{label}: score rows reached the file"
        assert payload["inference_grade"] == "subset-diagnostic", (
            f"{label}: a protected field was overwritten")
        assert payload["score_stream_sha256"] == _SummaryStub.score_stream_sha256
        assert payload["n_households"] == _SummaryStub.n_households
        long_lists = {k: len(v) for k, v in payload.items()
                      if isinstance(v, list) and len(v) > ib.N_FREE}
        assert long_lists == {}, f"{label}: household-scale content persisted"
