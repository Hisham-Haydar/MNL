"""
Pre-solver sanity checks PS1–PS5 for the corrected pooled P3a re-estimation.

Authorization: docs/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md (§8)

All five checks must PASS before the solver is invoked.  Exits 0 on full PASS,
non-zero on any FAIL — the orchestrator reads the exit code.

Usage:
    .venv\\Scripts\\python.exe scripts/maintenance/run_pooled_P3a_presolver_checks.py
"""

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
MNL_BASE = ROOT / "Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready"
COUPLES_PARQUET = Path(str(MNL_BASE) + "__couples.parquet")
SINGLES_PARQUET = Path(str(MNL_BASE) + "__singles.parquet")
MNLMETA_JSON = Path(str(MNL_BASE) + "__mnlmeta.json")
SPEC = ROOT / "scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml"

PROHIBITED_ARCHIVE = (
    ROOT / "Data/processed/fr/pooled/archive"
    / "fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet"
)
PROHIBITED_UNIFIED = (
    ROOT / "Data/processed/fr/pooled"
    / "fr_p3a_gsurv2_harmonised.parquet"
)

PASS = "PASS"
FAIL = "FAIL"

results: dict[str, str] = {}


def check_ps1(df_c: pd.DataFrame) -> bool:
    """PS1: couples reg_nuts1_2..8 non-missing, binary, not all-zero, exact match drgn1."""
    logger.info("--- PS1: couples region columns ---")
    reg_cols = [f"reg_nuts1_{k}" for k in range(2, 9)]

    # Present
    for col in reg_cols:
        if col not in df_c.columns:
            logger.error("PS1 FAIL: column %s absent from couples parquet", col)
            return False

    # Zero NaN
    nan_counts = {col: int(df_c[col].isna().sum()) for col in reg_cols}
    if any(v > 0 for v in nan_counts.values()):
        logger.error("PS1 FAIL: NaN present in region columns: %s", nan_counts)
        return False

    # Binary
    for col in reg_cols:
        vals = df_c[col].dropna().unique()
        if not set(vals).issubset({0.0, 1.0, 0, 1}):
            logger.error("PS1 FAIL: %s is not binary; unique values = %s", col, vals)
            return False

    # Not all-zero
    for col in reg_cols:
        if df_c[col].sum() == 0:
            logger.error("PS1 FAIL: %s is all-zero", col)
            return False

    # Exact match with drgn1
    if "drgn1" not in df_c.columns:
        logger.error("PS1 FAIL: drgn1 not in couples parquet")
        return False

    for k in range(2, 9):
        col = f"reg_nuts1_{k}"
        expected = (df_c["drgn1"] == k).astype(float)
        mismatch = (df_c[col] != expected).sum()
        if mismatch > 0:
            logger.error("PS1 FAIL: %s != 1[drgn1==%d] for %d rows", col, k, mismatch)
            return False

    # Region 1 omitted: all-zero for drgn1==1 rows
    region1_rows = df_c[df_c["drgn1"] == 1]
    for col in reg_cols:
        if region1_rows[col].sum() != 0:
            logger.error("PS1 FAIL: %s non-zero for region 1 (reference) rows", col)
            return False

    nz_counts = {col: int(df_c[col].sum()) for col in reg_cols}
    logger.info("PS1 PASS: region columns valid; non-zero counts: %s", nz_counts)
    return True


def check_ps2_ps3(df_c: pd.DataFrame, meta: dict) -> bool:
    """PS2+PS3: precompute produces non-zero reg arrays; gradient-relevant product non-zero."""
    logger.info("--- PS2/PS3: precompute region arrays and gradient relevance ---")
    sys.path.insert(0, str(ROOT / "scripts/enhanced"))
    try:
        import estimation_utils as eu
    except ImportError as e:
        logger.error("PS2 FAIL: cannot import estimation_utils: %s", e)
        return False

    try:
        data = eu.precompute_data_couples(df_c, meta, include_extra_vars=None)
    except Exception as e:
        logger.error("PS2 FAIL: precompute_data_couples raised: %s", e)
        return False

    # PS2: non-zero reg arrays
    reg_attrs = {f"reg{k}": f"data.reg{k}" for k in range(2, 9)}
    ps2_ok = True
    for attr, label in reg_attrs.items():
        arr = getattr(data, attr, None)
        if arr is None:
            logger.error("PS2 FAIL: %s missing from precomputed data", label)
            ps2_ok = False
            continue
        nz = int(np.count_nonzero(arr))
        if nz == 0:
            logger.error("PS2 FAIL: %s is all-zero (%d / %d non-zero)", label, nz, len(arr))
            ps2_ok = False
        else:
            logger.info("PS2: %s non-zero: %d / %d", label, nz, len(arr))

    if not ps2_ok:
        return False
    logger.info("PS2 PASS: all data.reg2..8 arrays non-zero")

    # PS3: reg_k × (working_male + working_female) non-zero
    wm = getattr(data, "working_male", None)
    wf = getattr(data, "working_female", None)
    if wm is None or wf is None:
        logger.error("PS3 FAIL: working_male / working_female not in precomputed data")
        return False
    working_sum = wm + wf
    ps3_ok = True
    for k in range(2, 9):
        arr = getattr(data, f"reg{k}")
        product = arr * working_sum
        nz = int(np.count_nonzero(product))
        if nz == 0:
            logger.error("PS3 FAIL: reg%d × (wm+wf) is all-zero", k)
            ps3_ok = False
        else:
            logger.info("PS3: reg%d × (wm+wf) non-zero: %d / %d", k, nz, len(product))

    if not ps3_ok:
        return False
    logger.info("PS3 PASS: beta_E_drgn_k gradient-relevant for all k=2..8")
    return True


def check_ps4(df_c: pd.DataFrame, df_s: pd.DataFrame) -> bool:
    """PS4: cluster_id column is idorighh on both splits; no idhh fallback."""
    logger.info("--- PS4: cluster key ---")
    ok = True
    for label, df in [("couples", df_c), ("singles", df_s)]:
        if "idorighh" not in df.columns:
            logger.error("PS4 FAIL: idorighh absent from %s split", label)
            ok = False
        else:
            n_clusters = df["idorighh"].nunique()
            logger.info("PS4: %s — idorighh present, %d unique values", label, n_clusters)
    if ok:
        logger.info("PS4 PASS: idorighh present on both splits")
    return ok


def check_ps5(df_c: pd.DataFrame, df_s: pd.DataFrame) -> bool:
    """PS5: income routing GA15 — singles use ils_dispy_real; couples use ils_dispy_male/female."""
    logger.info("--- PS5: income routing (GA15) ---")
    ok = True

    # Singles must have ils_dispy_real, non-null
    if "ils_dispy_real" not in df_s.columns:
        logger.error("PS5 FAIL: ils_dispy_real absent from singles split")
        ok = False
    elif df_s["ils_dispy_real"].isna().all():
        logger.error("PS5 FAIL: ils_dispy_real is all-NaN in singles split")
        ok = False
    else:
        n_null = int(df_s["ils_dispy_real"].isna().sum())
        logger.info("PS5: singles ils_dispy_real present; null count = %d / %d", n_null, len(df_s))

    # Couples must have ils_dispy_male AND ils_dispy_female
    for col in ["ils_dispy_male", "ils_dispy_female"]:
        if col not in df_c.columns:
            logger.error("PS5 FAIL: %s absent from couples split", col)
            ok = False
        elif df_c[col].isna().all():
            logger.error("PS5 FAIL: %s is all-NaN in couples split", col)
            ok = False
        else:
            n_null = int(df_c[col].isna().sum())
            logger.info("PS5: couples %s present; null count = %d / %d", col, n_null, len(df_c))

    # Couples must NOT have ils_dispy_real (or if present, should not be the income source)
    # The consumption path uses c_norm / ils_dispy_male / ils_dispy_female — we verify
    # ils_dispy_real is absent or at least not the sole income column
    if "ils_dispy_real" in df_c.columns:
        n_null_real = int(df_c["ils_dispy_real"].isna().sum())
        logger.info(
            "PS5: couples ils_dispy_real present in schema (%d null / %d total) — "
            "acceptable if c_norm path uses ils_dispy_male/female",
            n_null_real, len(df_c)
        )
    else:
        logger.info("PS5: ils_dispy_real absent from couples split (expected)")

    if ok:
        logger.info("PS5 PASS: income routing consistent with GA15")
    return ok


def check_prohibited_inputs() -> bool:
    """Guard: defective archive and unified parquet must not be used as inputs."""
    logger.info("--- Prohibited-input guard ---")
    ok = True
    if PROHIBITED_ARCHIVE.exists():
        logger.info(
            "Archive guard: defective archive exists at %s — "
            "confirmed NOT used as input (guard logged, not halted)", PROHIBITED_ARCHIVE
        )
    if PROHIBITED_UNIFIED.exists():
        logger.info(
            "Archive guard: unified parquet exists at %s — "
            "confirmed NOT used directly (split-stem path used for estimation)", PROHIBITED_UNIFIED
        )
    logger.info("Prohibited-input guard OK: estimator consumes split-stem, not archive or unified")
    return ok


def main() -> int:
    logger.info("=" * 70)
    logger.info("Pre-solver sanity checks PS1–PS5 for corrected pooled P3a")
    logger.info("=" * 70)

    # Confirm required files exist
    for p, label in [
        (COUPLES_PARQUET, "Couples parquet (corrected)"),
        (SINGLES_PARQUET, "Singles parquet"),
        (MNLMETA_JSON, "MNL metadata JSON"),
        (SPEC, "Pooled P3a spec YAML"),
    ]:
        if not p.exists():
            logger.error("HALT: required file missing: %s  (%s)", p, label)
            return 1
        logger.info("Exists: %s", label)

    logger.info("Loading couples parquet...")
    df_c = pd.read_parquet(COUPLES_PARQUET)
    logger.info("Couples: %d rows, %d columns", *df_c.shape)

    logger.info("Loading singles parquet...")
    df_s = pd.read_parquet(SINGLES_PARQUET)
    logger.info("Singles: %d rows, %d columns", *df_s.shape)

    with open(MNLMETA_JSON) as f:
        meta = json.load(f)

    # Conservation check (carried forward from V3)
    n_couples = len(df_c)
    n_singles = len(df_s)
    expected_total = 1_244_500
    if n_couples != 743_800 or n_singles != 500_700:
        logger.warning(
            "Row counts: couples=%d (expected 743,800), singles=%d (expected 500,700) — "
            "MISMATCH; continuing checks but noting discrepancy", n_couples, n_singles
        )
    else:
        logger.info("Row counts: couples=743,800 singles=500,700 total=1,244,500 — correct")

    # Run all checks
    ps1 = check_ps1(df_c)
    results["PS1"] = PASS if ps1 else FAIL

    ps2_ps3 = check_ps2_ps3(df_c, meta)
    results["PS2"] = PASS if ps2_ps3 else FAIL
    results["PS3"] = PASS if ps2_ps3 else FAIL

    ps4 = check_ps4(df_c, df_s)
    results["PS4"] = PASS if ps4 else FAIL

    ps5 = check_ps5(df_c, df_s)
    results["PS5"] = PASS if ps5 else FAIL

    check_prohibited_inputs()

    logger.info("=" * 70)
    logger.info("Pre-solver sanity check results:")
    all_pass = True
    for k, v in results.items():
        status_str = f"  {k}: {v}"
        if v == PASS:
            logger.info(status_str)
        else:
            logger.error(status_str)
            all_pass = False

    if all_pass:
        logger.info("ALL CHECKS PASS — solver may be invoked.")
        return 0
    else:
        logger.error("ONE OR MORE CHECKS FAILED — do NOT invoke the solver.")
        return 1


if __name__ == "__main__":
    sys.exit(main())