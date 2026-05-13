"""M0a-clean validation gates A-D.

Runs four gates against the new spec, the previous M0 spec, and the touched
Python files. Exits non-zero on any FAIL.

Read-only against parquets and existing JSON; no estimator invocation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "enhanced"))

from estimation_spec_parser import parse_specification  # noqa: E402

M0A_CLEAN_YAML = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0a_clean.yaml"
M0_YAML = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0.yaml"

EXPECTED_M0A_CLEAN_PARAMS = 47
EXPECTED_M0_PARAMS = 52


def status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


# ----------------------------------------------------------------------------
# Gate A — M0a-clean parse
# ----------------------------------------------------------------------------

def gate_a() -> Tuple[bool, List[str]]:
    notes: List[str] = []
    spec = parse_specification(M0A_CLEAN_YAML)

    checks = []
    checks.append(("spec.name == 'ruro_occ_M0a_clean'", spec.name == "ruro_occ_M0a_clean"))
    checks.append((
        f"len(spec.all_param_names) == {EXPECTED_M0A_CLEAN_PARAMS}",
        len(spec.all_param_names) == EXPECTED_M0A_CLEAN_PARAMS,
    ))
    checks.append((
        "'theta_c_singles' in spec.all_param_names",
        "theta_c_singles" in spec.all_param_names,
    ))
    checks.append((
        "'theta_c_sm' NOT in spec.all_param_names",
        "theta_c_sm" not in spec.all_param_names,
    ))
    checks.append((
        "'theta_c_sf' NOT in spec.all_param_names",
        "theta_c_sf" not in spec.all_param_names,
    ))
    educh_present = [
        n for n in spec.all_param_names if n.startswith("beta_l_educH")
    ]
    checks.append((
        "no beta_l_educH_* in spec.all_param_names",
        len(educh_present) == 0,
    ))
    has_theta_param_diff = any(
        (c.get("expression") == "param_diff"
         and "theta_c" in str(c.get("lhs_param", ""))
         and "theta_c" in str(c.get("rhs_param", "")))
        for c in spec.expression_constraints
    )
    checks.append((
        "no param_diff constraint links theta_c_* to theta_c_*",
        not has_theta_param_diff,
    ))
    mul_constraint_names = {c.get("name") for c in spec.expression_constraints}
    checks.append((
        "mul_cou_m_positive and mul_cou_f_positive constraints present",
        {"mul_cou_m_positive", "mul_cou_f_positive"}.issubset(mul_constraint_names),
    ))
    checks.append((
        "spec.utility_consumption_theta_singles_shared == 'theta_c_singles'",
        getattr(spec, "utility_consumption_theta_singles_shared", None) == "theta_c_singles",
    ))

    all_ok = all(ok for _, ok in checks)
    notes.append(f"n_estimated_params = {len(spec.all_param_names)}")
    notes.append(f"educH residuals: {educh_present}")
    for desc, ok in checks:
        notes.append(f"  {status(ok)}: {desc}")
    return all_ok, notes


# ----------------------------------------------------------------------------
# Gate B — backward compatibility (M0 still parses unchanged)
# ----------------------------------------------------------------------------

def gate_b() -> Tuple[bool, List[str]]:
    notes: List[str] = []
    spec = parse_specification(M0_YAML)
    checks = [
        ("spec.name == 'ruro_occ_M0'", spec.name == "ruro_occ_M0"),
        (
            f"len(spec.all_param_names) == {EXPECTED_M0_PARAMS}",
            len(spec.all_param_names) == EXPECTED_M0_PARAMS,
        ),
        ("'theta_c_sm' in M0 params", "theta_c_sm" in spec.all_param_names),
        ("'theta_c_sf' in M0 params", "theta_c_sf" in spec.all_param_names),
        ("'theta_c_singles' NOT in M0 params", "theta_c_singles" not in spec.all_param_names),
        (
            "M0 singles_box_cox_exponent is None",
            getattr(spec, "utility_consumption_theta_singles_shared", None) is None,
        ),
    ]
    # Opportunity blocks unchanged
    expected_hours_coefs = ["beta_E", "beta_h_pt1", "beta_h_pt2", "beta_h_ft"]
    hours_coefs = [s["coefficient"] for s in spec.hours_shifters]
    checks.append(("M0 hours_opportunity coefs unchanged", hours_coefs == expected_hours_coefs))
    expected_wage_coefs = ["beta_w0", "beta_w_educL", "beta_w_educH", "beta_w_pexp", "beta_w_pexp2"]
    wage_coefs = [s["coefficient"] for s in spec.wage_mean_shifters]
    checks.append(("M0 wage_opportunity mean_shifter coefs unchanged", wage_coefs == expected_wage_coefs))

    all_ok = all(ok for _, ok in checks)
    notes.append(f"n_estimated_params = {len(spec.all_param_names)}")
    for desc, ok in checks:
        notes.append(f"  {status(ok)}: {desc}")
    return all_ok, notes


# ----------------------------------------------------------------------------
# Gate C — engine resolver test (no estimation)
# ----------------------------------------------------------------------------

def gate_c() -> Tuple[bool, List[str]]:
    """Verify EstimationSpec.theta_c_param_name routes the four groups
    correctly under both M0a-clean and M0 specs."""
    notes: List[str] = []
    spec_clean = parse_specification(M0A_CLEAN_YAML)
    spec_legacy = parse_specification(M0_YAML)

    checks = [
        # M0a-clean routes both singles groups to theta_c_singles
        (
            "M0a-clean: theta_c_param_name('singles_male') == 'theta_c_singles'",
            spec_clean.theta_c_param_name("singles_male") == "theta_c_singles",
        ),
        (
            "M0a-clean: theta_c_param_name('singles_female') == 'theta_c_singles'",
            spec_clean.theta_c_param_name("singles_female") == "theta_c_singles",
        ),
        (
            "M0a-clean: theta_c_param_name('sm') == 'theta_c_singles'",
            spec_clean.theta_c_param_name("sm") == "theta_c_singles",
        ),
        (
            "M0a-clean: theta_c_param_name('sf') == 'theta_c_singles'",
            spec_clean.theta_c_param_name("sf") == "theta_c_singles",
        ),
        # M0a-clean keeps couples on theta_c
        (
            "M0a-clean: theta_c_param_name('couples_household') == 'theta_c'",
            spec_clean.theta_c_param_name("couples_household") == "theta_c",
        ),
        (
            "M0a-clean: theta_c_param_name('couples_male') == 'theta_c'",
            spec_clean.theta_c_param_name("couples_male") == "theta_c",
        ),
        (
            "M0a-clean: theta_c_param_name('couples_female') == 'theta_c'",
            spec_clean.theta_c_param_name("couples_female") == "theta_c",
        ),
        # Confirm M0a-clean doesn't accidentally emit theta_c_sf
        (
            "M0a-clean: 'theta_c_sf' resolves to nothing the engine would request",
            "theta_c_sf" not in spec_clean.all_param_names
            and spec_clean.theta_c_param_name("singles_female") != "theta_c_sf",
        ),
        # M0 legacy still uses suffix
        (
            "M0 legacy: theta_c_param_name('singles_male') == 'theta_c_sm'",
            spec_legacy.theta_c_param_name("singles_male") == "theta_c_sm",
        ),
        (
            "M0 legacy: theta_c_param_name('singles_female') == 'theta_c_sf'",
            spec_legacy.theta_c_param_name("singles_female") == "theta_c_sf",
        ),
        (
            "M0 legacy: theta_c_param_name('couples_household') == 'theta_c'",
            spec_legacy.theta_c_param_name("couples_household") == "theta_c",
        ),
    ]
    all_ok = all(ok for _, ok in checks)
    for desc, ok in checks:
        notes.append(f"  {status(ok)}: {desc}")

    notes.append(
        "  NOTE: Engines invoke spec.theta_c_param_name(group) at every "
        "consumption Box-Cox site (estimation_engine.py L412+, L836+; "
        "gamspy_estimation_vectorized.py L381 + L714; gamspy_estimation.py "
        "5 sites). With the param vector already correct (Gate A), the "
        "engines will look up the right name. Full forward-pass invocation "
        "would require GAMSPy + a precomputed data container; that is "
        "outside this read-only check."
    )
    return all_ok, notes


# ----------------------------------------------------------------------------
# Gate D — syntax: every touched Python file compiles
# ----------------------------------------------------------------------------

def gate_d() -> Tuple[bool, List[str]]:
    notes: List[str] = []
    touched = [
        REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_parser.py",
        REPO_ROOT / "scripts" / "enhanced" / "estimation_engine.py",
        REPO_ROOT / "scripts" / "enhanced" / "gamspy_estimation_vectorized.py",
        REPO_ROOT / "scripts" / "enhanced" / "gamspy_estimation.py",
        Path(__file__).resolve(),
    ]
    all_ok = True
    for f in touched:
        if not f.exists():
            notes.append(f"  FAIL: {f} does not exist")
            all_ok = False
            continue
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(f)],
            capture_output=True, text=True, check=False,
        )
        if r.returncode == 0:
            notes.append(f"  PASS: py_compile {f.relative_to(REPO_ROOT)}")
        else:
            notes.append(
                f"  FAIL: py_compile {f.relative_to(REPO_ROOT)}\n"
                f"         stderr: {r.stderr.strip()}"
            )
            all_ok = False
    return all_ok, notes


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def main() -> int:
    print("=" * 72)
    print("M0a-clean validation gates")
    print("=" * 72)
    print()

    gates = [
        ("Gate A: M0a-clean parse", gate_a),
        ("Gate B: M0 backward compatibility", gate_b),
        ("Gate C: engine resolver routing", gate_c),
        ("Gate D: py_compile on touched files", gate_d),
    ]

    overall_ok = True
    for name, fn in gates:
        print(name)
        print("-" * len(name))
        try:
            ok, notes = fn()
        except Exception as exc:  # noqa: BLE001
            ok = False
            notes = [f"  FAIL: gate raised {type(exc).__name__}: {exc}"]
        for line in notes:
            print(line)
        print(f"  -> {status(ok)}")
        print()
        if not ok:
            overall_ok = False

    print("=" * 72)
    print(f"OVERALL: {status(overall_ok)}")
    print("=" * 72)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
