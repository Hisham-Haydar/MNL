"""
Read-only checks for the urbanisation access increment (D5) added to
estimation_spec_bpool_p3a_v1.yaml. No estimation, no data changes.

1. drgur/drgmd/drgru exist in both estimation-ready parquets; mutually exclusive,
   sum to 1 per household, 0 nulls.
2. household-constant within stacked_hh_uid.
3. REDUNDANCY vs region: cross-tab urbanisation (3-cat) x NUTS-1 region (reg2..8 / drgn1).
   Flag if urban/middle are near-spanned by region dummies (weak identification once
   region is in). Report cross-tab + collinearity flag; drop nothing.
4. GUARDRAIL: urbanisation enters access (market_opportunity) ONLY; educH stays
   wage-only; one increment.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from _bpool_paths import bpool_dir  # noqa: E402

_BP = bpool_dir()
_SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
_URB = ["drgur", "drgmd", "drgru"]
_REG = [f"reg{k}" for k in range(2, 9)]


def hh_level(mode: str) -> pd.DataFrame:
    """One row per household (chosen row) with urbanisation + region dummies."""
    chosen = "is_chosen" if mode == "singles" else "is_chosen_joint"
    cols = ["stacked_hh_uid", chosen] + _URB + _REG + ["drgn1"]
    f = _BP / f"fr_p3a_bpool_estimation_ready__{mode}.parquet"
    import pyarrow.parquet as pq
    present = set(pq.read_schema(f).names)
    cols = [c for c in cols if c in present]
    df = pd.read_parquet(f, columns=cols)
    return df, chosen


def check_1_2(mode: str) -> None:
    df, chosen = hh_level(mode)
    print(f"\n--- {mode} : CHECK 1 (exclusive/sum1/nonnull) + CHECK 2 (HH-constant) ---")
    have = [c for c in _URB if c in df.columns]
    print(f"  urbanisation present: {have}")
    nulls = {c: int(df[c].isna().sum()) for c in _URB}
    s = df[_URB].sum(axis=1)
    print(f"  nulls: {nulls}")
    print(f"  rowsum distribution: {s.value_counts().to_dict()}  (want all == 1)")
    print(f"  exclusive & sum-to-1: {bool((s == 1).all()) and sum(nulls.values()) == 0}")
    # per-HH shares (chosen row only -> one row per HH)
    hh = df[df[chosen] == 1] if chosen in df.columns else df
    print(f"  per-HH shares: urban={hh['drgur'].mean():.3f} middle={hh['drgmd'].mean():.3f} rural={hh['drgru'].mean():.3f}")
    nun = df.groupby("stacked_hh_uid")[_URB].nunique().max().to_dict()
    print(f"  household-constant (max nunique within HH, want 1): {nun}")


def check_3_redundancy(mode: str) -> None:
    df, chosen = hh_level(mode)
    hh = df[df[chosen] == 1] if chosen in df.columns else df
    print(f"\n--- {mode} : CHECK 3 (redundancy vs region) ---")
    # 3-cat urbanisation label
    urb = np.where(hh["drgur"] == 1, "urban",
          np.where(hh["drgmd"] == 1, "middle", "rural"))
    # NUTS-1 region label: reg2..8 one-hot; region 1 = base (all reg2..8 == 0)
    reg_mat = hh[_REG].values if all(c in hh.columns for c in _REG) else None
    if reg_mat is None:
        print("  region dummies absent — skipping")
        return
    reg_label = np.where(reg_mat.sum(axis=1) == 0, "reg1",
                pd.Categorical.from_codes(reg_mat.argmax(axis=1), [f"reg{k}" for k in range(2, 9)]).astype(str))
    ct = pd.crosstab(pd.Series(reg_label, name="NUTS1"), pd.Series(urb, name="urbanisation"))
    print("  cross-tab NUTS-1 region x urbanisation:")
    print(ct.to_string())

    # Collinearity diagnostic: regress each urbanisation dummy on the region dummies
    # (linear probability) and report R^2. High R^2 => near-spanned by region.
    X = np.column_stack([np.ones(len(hh))] + [hh[c].values for c in _REG]).astype(float)
    flags = {}
    for u in ("drgur", "drgmd"):
        y = hh[u].values.astype(float)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        yhat = X @ beta
        ss_res = float(((y - yhat) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        flags[u] = r2
        print(f"  R^2({u} ~ region dummies) = {r2:.4f}")
    worst = max(flags.values())
    if worst >= 0.90:
        verdict = "HIGH collinearity — urbanisation near-spanned by region; beta_E_drgur/drgmd weakly identified once region is in."
    elif worst >= 0.50:
        verdict = "MODERATE collinearity — region absorbs a sizeable share of urbanisation variation; watch identification."
    else:
        verdict = "LOW collinearity — urbanisation carries independent variation beyond NUTS-1 region; identification OK."
    print(f"  COLLINEARITY FLAG: {verdict}")


def check_4_guardrail() -> None:
    print("\n--- CHECK 4 (access-only guardrail) ---")
    spec = yaml.safe_load(_SPEC.read_text())

    def coefs_in(block_shifters):
        out = []
        for sh in block_shifters or []:
            out.append((sh.get("variable"), sh.get("coefficient")))
        return out

    blocks = {
        "utility.leisure": spec["utility"]["leisure"].get("shifters", []),
        "hours_opportunity": spec["hours_opportunity"].get("shifters", []),
        "wage_opportunity": spec["wage_opportunity"].get("mean_shifters", []),
        "market_opportunity": spec["market_opportunity"].get("shifters", []),
        "occupation_opportunity": spec["occupation_opportunity"].get("shifters", []),
    }
    urb_locations = []
    educH_locations = []
    for name, shifters in blocks.items():
        for var, coef in coefs_in(shifters):
            if var in _URB:
                urb_locations.append((name, var, coef))
            if var == "educH":
                educH_locations.append((name, var, coef))
    print(f"  urbanisation appears ONLY in: {sorted(set(b for b,_,_ in urb_locations))}")
    print(f"     entries: {urb_locations}")
    access_only = all(b == "market_opportunity" for b, _, _ in urb_locations) and len(urb_locations) > 0
    print(f"  access-only (market_opportunity only): {access_only}")
    print(f"  educH appears in: {sorted(set(b for b,_,_ in educH_locations))}  (want wage_opportunity only)")
    educH_wage_only = all(b == "wage_opportunity" for b, _, _ in educH_locations)
    print(f"  educH wage-only: {educH_wage_only}")
    n_urb_params = len(urb_locations)
    print(f"  urbanisation params added: {n_urb_params} (want 2: drgur, drgmd; rural=reference)")
    print(f"  GUARDRAIL PASS: {access_only and educH_wage_only and n_urb_params == 2}")


def main():
    print("=" * 78)
    print("URBANISATION (D5) — read-only checks")
    print("=" * 78)
    for mode in ("singles", "couples"):
        check_1_2(mode)
    for mode in ("singles", "couples"):
        check_3_redundancy(mode)
    check_4_guardrail()


if __name__ == "__main__":
    main()
