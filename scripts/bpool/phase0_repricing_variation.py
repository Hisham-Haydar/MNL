"""
PHASE 0 — read-only verification that EUROMOD repricing produced the data variation
the likelihood needs, BEFORE any spec change. No estimation, no data modification.

0a. within-HH mean/std of ils_dispy_real across simulated alternatives; count HH with
    within-HH std == 0; percentiles 5/25/50/75/95 of within-HH std.
0b. working alternatives: ils_dispy_real vs drawn earnings (hours*wage*52/12) on 50 random
    HH; per-HH Spearman rank corr (expect monotone/concave -> high positive rank corr).
0c. non-working alternatives: distribution of ils_dispy_real across HH (expect positive,
    benefit-driven, cross-HH variation).
0d. PASS/FAIL verdict per check.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _bpool_paths import bpool_dir  # noqa: E402

_BP = bpool_dir()
_RNG = np.random.default_rng(20260527)
WEEKS_PER_MONTH = 52.0 / 12.0


def _load(mode):
    f = _BP / f"fr_p3a_bpool_engine_ready__{mode}.parquet"
    cols = ["stacked_hh_uid", "ils_dispy_real"]
    if mode == "singles":
        cols += ["draw", "is_chosen", "working", "hours", "wage"]
    else:
        cols += ["draw_joint", "is_chosen_joint", "working_male", "working_female",
                 "hours_male", "hours_female", "wage_male", "wage_female"]
    return pd.read_parquet(f, columns=cols)


def check_0a(df, mode):
    print(f"\n--- 0a within-HH variation of ils_dispy_real [{mode}] ---")
    g = df.groupby("stacked_hh_uid")["ils_dispy_real"]
    sd = g.std(ddof=0)
    mn = g.mean()
    n_hh = len(sd)
    n_zero = int((sd <= 1e-9).sum())
    pct = np.percentile(sd.values, [5, 25, 50, 75, 95])
    print(f"  n_HH={n_hh:,}  mean within-HH std={sd.mean():.1f}  median std={np.median(sd):.1f} EUR/mo")
    print(f"  within-HH std percentiles [5,25,50,75,95]: {np.round(pct,1).tolist()}")
    print(f"  HH with within-HH std==0: {n_zero}")
    print(f"  mean of within-HH MEAN dispy: {mn.mean():.1f}")
    ok = (n_zero == 0) and (np.median(sd) >= 100.0)
    print(f"  0a verdict: {'PASS' if ok else 'FAIL'} (need 0 zero-var HH and median std >= 100)")
    return ok


def check_0b(df, mode):
    print(f"\n--- 0b working alts: dispy vs drawn earnings (monotone/concave) [{mode}] ---")
    if mode == "singles":
        w = df[df["working"] == 1].copy()
        w["earn"] = pd.to_numeric(w["hours"]) * pd.to_numeric(w["wage"]) * WEEKS_PER_MONTH
    else:
        # household earnings = sum of working partners' drawn earnings
        em = pd.to_numeric(df["hours_male"]) * pd.to_numeric(df["wage_male"]) * WEEKS_PER_MONTH * (df["working_male"] == 1)
        ef = pd.to_numeric(df["hours_female"]) * pd.to_numeric(df["wage_female"]) * WEEKS_PER_MONTH * (df["working_female"] == 1)
        w = df.copy()
        w["earn"] = em.values + ef.values
        w = w[(df["working_male"] == 1) | (df["working_female"] == 1)]
    uids = pd.Series(w["stacked_hh_uid"].unique())
    samp = uids.sample(min(50, len(uids)), random_state=0)
    rhos = []
    for u in samp:
        sub = w[w["stacked_hh_uid"] == u]
        if sub["earn"].nunique() > 3 and sub["ils_dispy_real"].nunique() > 3:
            rho, _ = spearmanr(sub["earn"], sub["ils_dispy_real"])
            if np.isfinite(rho):
                rhos.append(rho)
    rhos = np.array(rhos)
    print(f"  per-HH Spearman(earn, dispy) over {len(rhos)} HH: "
          f"median={np.median(rhos):.3f} mean={rhos.mean():.3f} "
          f"frac>0.5={np.mean(rhos>0.5):.2f} frac<0={np.mean(rhos<0):.2f}")
    ok = (np.median(rhos) > 0.5) and (np.mean(rhos > 0) > 0.8)
    print(f"  0b verdict: {'PASS' if ok else 'FAIL'} (need median rank-corr > 0.5, >80% HH positive)")
    return ok


def check_0c(df, mode):
    print(f"\n--- 0c non-working alts: dispy distribution across HH [{mode}] ---")
    if mode == "singles":
        nw = df[df["working"] == 0]
    else:
        nw = df[(df["working_male"] == 0) & (df["working_female"] == 0)]
    if len(nw) == 0:
        print("  no non-working alternatives found")
        return False
    # one value per HH (any non-working alt; they share the same frozen non-work dispy per HH-ish)
    per_hh = nw.groupby("stacked_hh_uid")["ils_dispy_real"].mean()
    pct = np.percentile(per_hh.values, [5, 25, 50, 75, 95])
    n_pos = int((per_hh > 0).sum()); n = len(per_hh)
    print(f"  non-working HH: {n:,}  positive dispy: {n_pos:,} ({100*n_pos/n:.1f}%)")
    print(f"  cross-HH dispy percentiles [5,25,50,75,95]: {np.round(pct,1).tolist()}")
    print(f"  cross-HH std of non-work dispy: {per_hh.std():.1f}")
    ok = (n_pos / n > 0.9) and (per_hh.std() > 50.0)
    print(f"  0c verdict: {'PASS' if ok else 'FAIL'} (need >90% positive, cross-HH std > 50)")
    return ok


def main():
    print("=" * 72)
    print("PHASE 0 — repricing variation verification (read-only)")
    print("=" * 72)
    results = {}
    for mode in ("singles", "couples"):
        df = _load(mode)
        print(f"\n##### {mode}: {len(df):,} rows, {df['stacked_hh_uid'].nunique():,} HH #####")
        a = check_0a(df, mode)
        b = check_0b(df, mode)
        c = check_0c(df, mode)
        results[mode] = {"0a": a, "0b": b, "0c": c}
    print("\n" + "=" * 72)
    print("PHASE 0 VERDICT")
    print("=" * 72)
    allpass = True
    for mode, r in results.items():
        for k, v in r.items():
            print(f"  {mode} {k}: {'PASS' if v else 'FAIL'}")
            allpass &= v
    print(f"\n  PHASE 0: {'PASS — proceed to Phase 1 (after user picks B-strict/B-extended)' if allpass else 'FAIL — HALT, escalate for diagnosis'}")
    if not allpass:
        sys.exit(1)


if __name__ == "__main__":
    main()
