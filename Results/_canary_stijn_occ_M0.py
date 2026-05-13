"""Canary checks 1-9 for M0_stijn_occ rebuild status."""
import json
import numpy as np
import pandas as pd

SINGLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet"
COUPLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet"

results = {}

def section(title):
    print(f"\n{'='*72}\n{title}\n{'='*72}")

section("FILE METADATA")
import os, datetime
for name, path in [("singles", SINGLES), ("couples", COUPLES)]:
    st = os.stat(path)
    mtime = datetime.datetime.fromtimestamp(st.st_mtime).isoformat()
    print(f"{name}: {path}\n  size={st.st_size:,} bytes  mtime={mtime}")
    results.setdefault("meta", {})[name] = {"size": st.st_size, "mtime": mtime}

section("LOAD")
s = pd.read_parquet(SINGLES)
c = pd.read_parquet(COUPLES)
print(f"singles: {len(s):,} rows, {len(s.columns)} cols")
print(f"couples: {len(c):,} rows, {len(c.columns)} cols")
results["singles_rows"] = len(s)
results["singles_cols"] = len(s.columns)
results["couples_rows"] = len(c)
results["couples_cols"] = len(c.columns)

# ----------------------------------------------------------------------
# Check 4: required column existence
# ----------------------------------------------------------------------
section("CHECK 4 — required column existence")
REQUIRED_SINGLES = ["loc4", "working", "log_q_E", "log_q_H", "log_q_W", "log_q_Occ",
                    "prior", "log_prior", "idhh"]
REQUIRED_COUPLES = ["loc4_male", "loc4_female",
                    "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
                    "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
                    "prior", "log_prior", "idhh"]
# working_{male,female} are preferred; falls back to hours_{male,female} > 0
COUPLES_WORKING_INDICATORS = [("working_male", "hours_male"),
                              ("working_female", "hours_female")]

singles_missing = [c0 for c0 in REQUIRED_SINGLES if c0 not in s.columns]
couples_missing = [c0 for c0 in REQUIRED_COUPLES if c0 not in c.columns]
print(f"singles missing: {singles_missing}")
print(f"couples missing: {couples_missing}")
results["check4_singles_missing"] = singles_missing
results["check4_couples_missing"] = couples_missing
results["check4_pass"] = (not singles_missing) and (not couples_missing)

# Also report log_q_occ (raw layer name) to show whether old/new MNL prep ran
for label, df in [("singles", s), ("couples", c)]:
    raw_cols = [c0 for c0 in ["log_q_occ", "log_q_state", "log_q_hours", "log_q_wage",
                              "log_q_job", "log_q_total"] if c0 in df.columns]
    print(f"  {label} raw/forbidden cols present: {raw_cols}")
    results.setdefault("raw_cols", {})[label] = raw_cols

# ----------------------------------------------------------------------
# Check 3: log_q_Occ exists (subset of check 4 but explicit per spec)
# ----------------------------------------------------------------------
section("CHECK 3 — log_q_Occ exists")
c3_singles = "log_q_Occ" in s.columns
c3_couples = ("log_q_Occ_male" in c.columns) and ("log_q_Occ_female" in c.columns)
print(f"singles log_q_Occ: {c3_singles}")
print(f"couples log_q_Occ_male/female: {c3_couples}")
results["check3_pass"] = c3_singles and c3_couples

# ----------------------------------------------------------------------
# Check 1 + 2: loc4 varies across working alternatives; median distinct >= 3
# ----------------------------------------------------------------------
section("CHECK 1 & 2 — loc4 variation across working alts")

def _working_mask(df, work_col, hours_fallback):
    """Return (mask, source_used) using work_col if present, else hours_fallback > 0."""
    if work_col in df.columns:
        return (df[work_col] == 1), work_col
    if hours_fallback in df.columns:
        return (df[hours_fallback] > 0), f"{hours_fallback} > 0 (fallback)"
    return None, None

def variation(df, loc_col, work_col, hours_fallback, label):
    if loc_col not in df.columns:
        print(f"  {label}: MISSING loc col {loc_col}")
        return None
    mask, source = _working_mask(df, work_col, hours_fallback)
    if mask is None:
        print(f"  {label}: no working indicator ({work_col} and {hours_fallback} both missing)")
        return None
    w = df[mask]
    if "idhh" not in w.columns:
        print(f"  {label}: idhh missing")
        return None
    nu = w.groupby("idhh")[loc_col].nunique()
    desc = nu.describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99])
    pct_eq1 = float((nu == 1).mean())
    print(f"  {label} [working source: {source}]: n_hh={len(nu):,}  median={desc['50%']:.1f}  "
          f"mean={desc['mean']:.2f}  p25={desc['25%']:.1f}  p75={desc['75%']:.1f}  "
          f"p99={desc['99%']:.1f}  max={desc['max']:.0f}  "
          f"frac_eq_1={pct_eq1:.2%}")
    return {"median": float(desc["50%"]), "mean": float(desc["mean"]),
            "frac_hh_eq_1": pct_eq1, "n_hh": int(len(nu)), "working_source": source}

results["check1_2"] = {}
results["check1_2"]["singles"] = variation(s, "loc4", "working", "lhw", "singles")
results["check1_2"]["couples_male"] = variation(c, "loc4_male", "working_male", "hours_male", "couples_male")
results["check1_2"]["couples_female"] = variation(c, "loc4_female", "working_female", "hours_female", "couples_female")

def median_ok(d):
    return d is not None and d["median"] >= 3.0
results["check1_pass"] = all(d is not None and d["median"] > 1.0 for d in results["check1_2"].values())
results["check2_pass"] = all(median_ok(d) for d in results["check1_2"].values())
print(f"\n  Check 1 (any variation, median > 1): {results['check1_pass']}")
print(f"  Check 2 (median >= 3):                {results['check2_pass']}")

# ----------------------------------------------------------------------
# Check 5: prior > 0
# ----------------------------------------------------------------------
section("CHECK 5 — prior > 0")
for label, df in [("singles", s), ("couples", c)]:
    if "prior" not in df.columns:
        print(f"  {label}: prior column MISSING")
        results.setdefault("check5", {})[label] = "missing"
        continue
    p = df["prior"]
    pmin = float(p.min())
    n_nonpos = int((p <= 0).sum())
    n_nan = int(p.isna().sum())
    print(f"  {label}: min={pmin:.6e}  n<=0: {n_nonpos}  n_nan: {n_nan}")
    results.setdefault("check5", {})[label] = {"min": pmin, "n_nonpos": n_nonpos, "n_nan": n_nan}
results["check5_pass"] = all(
    isinstance(v, dict) and v["n_nonpos"] == 0 and v["n_nan"] == 0
    for v in results["check5"].values()
)

# ----------------------------------------------------------------------
# Check 6: log_prior == log(prior)
# ----------------------------------------------------------------------
section("CHECK 6 — log_prior == log(prior)")
for label, df in [("singles", s), ("couples", c)]:
    if "prior" not in df.columns or "log_prior" not in df.columns:
        print(f"  {label}: missing prior or log_prior")
        results.setdefault("check6", {})[label] = "missing"
        continue
    p = df["prior"].to_numpy()
    lp = df["log_prior"].to_numpy()
    mask = (p > 0) & np.isfinite(p) & np.isfinite(lp)
    diff = np.abs(np.log(p[mask]) - lp[mask])
    print(f"  {label}: max |log(prior) - log_prior| = {diff.max():.6e}  "
          f"(n_eval={mask.sum():,}, rows |diff|>1e-6: {(diff>1e-6).sum()})")
    results.setdefault("check6", {})[label] = {"max_diff": float(diff.max()),
                                                "n_eval": int(mask.sum()),
                                                "n_diff_gt_1e6": int((diff > 1e-6).sum())}
results["check6_pass"] = all(
    isinstance(v, dict) and v["max_diff"] < 1e-9
    for v in results["check6"].values()
)

# ----------------------------------------------------------------------
# Check 7: singles log_prior reconstruction
# ----------------------------------------------------------------------
section("CHECK 7 — singles log_prior reconstruction")
required = ["log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "working", "log_prior"]
miss = [c0 for c0 in required if c0 not in s.columns]
if miss:
    print(f"  singles missing required cols: {miss}")
    results["check7"] = {"status": "missing", "missing": miss}
    results["check7_pass"] = False
else:
    w = (s["working"] == 1).astype(float).to_numpy()
    recon = (s["log_q_E"].to_numpy()
             + w * (s["log_q_H"].to_numpy() + s["log_q_W"].to_numpy() + s["log_q_Occ"].to_numpy()))
    diff = np.abs(s["log_prior"].to_numpy() - recon)
    print(f"  singles: max |log_prior - recon| = {diff.max():.6e}  "
          f"rows |diff|>1e-6: {(diff > 1e-6).sum()}")
    results["check7"] = {"max_diff": float(diff.max()), "n_diff_gt_1e6": int((diff > 1e-6).sum())}
    results["check7_pass"] = diff.max() < 1e-9

# ----------------------------------------------------------------------
# Check 8: couples log_prior reconstruction (male + female components)
# ----------------------------------------------------------------------
section("CHECK 8 — couples log_prior reconstruction (male + female)")
required_c = ["log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
              "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
              "log_prior"]
miss = [c0 for c0 in required_c if c0 not in c.columns]
m_mask, m_src = _working_mask(c, "working_male", "hours_male")
f_mask, f_src = _working_mask(c, "working_female", "hours_female")
if miss or m_mask is None or f_mask is None:
    print(f"  couples missing required cols: {miss}; "
          f"male_work_src={m_src!r}; female_work_src={f_src!r}")
    results["check8"] = {"status": "missing", "missing": miss,
                          "male_work_src": m_src, "female_work_src": f_src}
    results["check8_pass"] = False
else:
    print(f"  working indicators: male={m_src!r}, female={f_src!r}")
    wm = m_mask.astype(float).to_numpy()
    wf = f_mask.astype(float).to_numpy()
    recon = (
        c["log_q_E_male"].to_numpy()
        + wm * (c["log_q_H_male"].to_numpy() + c["log_q_W_male"].to_numpy() + c["log_q_Occ_male"].to_numpy())
        + c["log_q_E_female"].to_numpy()
        + wf * (c["log_q_H_female"].to_numpy() + c["log_q_W_female"].to_numpy() + c["log_q_Occ_female"].to_numpy())
    )
    diff = np.abs(c["log_prior"].to_numpy() - recon)
    print(f"  couples: max |log_prior - recon| = {diff.max():.6e}  "
          f"rows |diff|>1e-6: {(diff > 1e-6).sum()}")
    results["check8"] = {"max_diff": float(diff.max()), "n_diff_gt_1e6": int((diff > 1e-6).sum())}
    results["check8_pass"] = diff.max() < 1e-9

# ----------------------------------------------------------------------
# Check 9: non-work alternatives have occupation contribution gated off
# ----------------------------------------------------------------------
section("CHECK 9 — non-work alts: log_q_Occ contribution gated off")
def nonwork_check(df, work_col, hours_fallback, occ_col, loc_col, label):
    out = {}
    mask, source = _working_mask(df, work_col, hours_fallback)
    if mask is None:
        print(f"  {label}: no working indicator ({work_col} and {hours_fallback} both missing)")
        return None
    nw = df[~mask]
    out["working_source"] = source
    print(f"  {label} [working source: {source}]: n_nonwork={len(nw):,}")
    if occ_col in df.columns:
        v = nw[occ_col].to_numpy()
        n_nonzero = int((v != 0).sum())
        print(f"    {occ_col} on non-work: nonzero={n_nonzero}  max|.|={np.abs(v).max() if len(v) else 0:.6e}")
        out[occ_col] = {"n_nonzero": n_nonzero, "max_abs": float(np.abs(v).max() if len(v) else 0)}
    if loc_col in df.columns:
        unique = sorted(nw[loc_col].unique().tolist())
        print(f"    {loc_col} on non-work uniques (first 5): {unique[:5]}")
        out[loc_col + "_uniques_nonwork"] = unique[:10]
    return out

results["check9"] = {}
results["check9"]["singles"] = nonwork_check(s, "working", "lhw", "log_q_Occ", "loc4", "singles")
results["check9"]["couples_male"] = nonwork_check(c, "working_male", "hours_male", "log_q_Occ_male", "loc4_male", "couples_male")
results["check9"]["couples_female"] = nonwork_check(c, "working_female", "hours_female", "log_q_Occ_female", "loc4_female", "couples_female")
def nw_ok(d, key):
    return d is not None and d.get(key, {}).get("n_nonzero", 1) == 0
results["check9_pass"] = (
    nw_ok(results["check9"]["singles"], "log_q_Occ")
    and nw_ok(results["check9"]["couples_male"], "log_q_Occ_male")
    and nw_ok(results["check9"]["couples_female"], "log_q_Occ_female")
)

# ----------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------
section("SUMMARY")
checks = [
    (1, "loc4 varies across working alts (any variation)", results.get("check1_pass")),
    (2, "median distinct loc4 per hh >= 3", results.get("check2_pass")),
    (3, "log_q_Occ exists", results.get("check3_pass")),
    (4, "all required Stijn alias columns exist", results.get("check4_pass")),
    (5, "prior > 0", results.get("check5_pass")),
    (6, "log_prior == log(prior)", results.get("check6_pass")),
    (7, "singles log_prior reconstruction", results.get("check7_pass")),
    (8, "couples log_prior reconstruction", results.get("check8_pass")),
    (9, "non-work alts gate off log_q_Occ", results.get("check9_pass")),
]
for n, name, ok in checks:
    print(f"  C{n}: {'PASS' if ok else 'FAIL'} — {name}")

with open(r"U:/Desktop/Nizam_Hisham/MNL/Results/_canary_stijn_occ_M0_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved results JSON.")
