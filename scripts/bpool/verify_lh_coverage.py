"""
LH-coverage gate for the couples product grid (CHECK-7 style).

Verifies that reducing the couples grid from 30x30 (901 alts) to 20x20 (400 alts)
does NOT starve the LH band [44.5, 70.0] — the long-hours mode that historically
caused the working_lh failures. The reduction drops marginal draws per partner
from 30 to 20, so LH (D1 mixture weight 0.10) goes from an expected ~3.0 to ~2.0
draws per partner. This gate confirms the realized coverage is adequate.

Reports (per build):
  1. Per-partner marginal mass in each of the five focal bands (PT1/PT2/F35/FT/LH)
     computed on UNIQUE marginal draws (deduped on draw_male / draw_female).
  2. Chosen-row LH counts vs the behavioural benchmark (couple-male / couple-female
     LH choosers from the D1 figures: ~764 male, ~317 female on the full pool).
  3. The critical stop-signal check: for households whose CHOSEN worker is in LH,
     how many have at least one non-chosen LH draw on the same partner side
     (importance-sampling needs support near each chosen LH worker).

PASS/FAIL:
  - LH per-partner mean marginal draws >= LH_MIN_DRAWS_PER_PARTNER (default 1.5)
  - >= LH_CHOSEN_SUPPORT_FRAC of chosen-LH households have a non-chosen LH draw
    on the chosen worker's side (default 0.95)

Usage:
  python verify_lh_coverage.py --couples <engine_ready_couples.parquet>
  python verify_lh_coverage.py --couples <...> --benchmark-male 764 --benchmark-female 317
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_script_dir))
from hours_mixture_d1 import BAND_NAMES, BAND_LO, BAND_HI, H_MAX, DEFAULT_WEIGHTS  # noqa: E402

# Stop-signal thresholds
LH_MIN_DRAWS_PER_PARTNER = 1.5     # mean realized LH marginal draws per partner
LH_CHOSEN_SUPPORT_FRAC = 0.95      # frac of chosen-LH HHs with a non-chosen LH draw same side

# D1 focal bands (exclude BG); LH is right-closed at H_MAX
_FOCAL = [(n, lo, hi) for n, lo, hi in zip(BAND_NAMES, BAND_LO, BAND_HI) if n != "BG"]


def _band_of(hours: np.ndarray, working: np.ndarray) -> np.ndarray:
    """Assign each (hours, working) to a focal band name or '' (non-working / BG)."""
    out = np.full(len(hours), "", dtype=object)
    for name, lo, hi in _FOCAL:
        if name == "LH":
            mask = (hours >= lo) & (hours <= H_MAX) & (working == 1)
        else:
            mask = (hours >= lo) & (hours < hi) & (working == 1)
        out[mask] = name
    return out


def _marginal_mass(df: pd.DataFrame, side: str) -> dict:
    """Per-partner marginal band counts on UNIQUE draws (deduped on draw_<side>)."""
    draw_col = f"draw_{side}"
    hcol, wcol = f"hours_{side}", f"working_{side}"
    sim = df[df["is_chosen_joint"] == 0]
    # Unique marginal draws per HH: dedupe on (stacked_hh_uid, draw_<side>)
    uniq = sim.drop_duplicates(subset=["stacked_hh_uid", draw_col])
    n_hh = uniq["stacked_hh_uid"].nunique()
    bands = _band_of(uniq[hcol].values, uniq[wcol].values)
    counts = {name: int((bands == name).sum()) for name, _, _ in _FOCAL}
    per_partner = {name: round(c / max(n_hh, 1), 4) for name, c in counts.items()}
    return {
        "n_hh": n_hh,
        "n_unique_marginal_draws": len(uniq),
        "band_counts_total": counts,
        "band_mean_draws_per_partner": per_partner,
    }


def _chosen_lh(df: pd.DataFrame) -> dict:
    """Chosen-row LH counts for each partner side."""
    chosen = df[df["is_chosen_joint"] == 1]
    out = {}
    for side in ("male", "female"):
        hcol, wcol = f"hours_{side}", f"working_{side}"
        bands = _band_of(chosen[hcol].values, chosen[wcol].values)
        out[side] = int((bands == "LH").sum())
    out["n_chosen_hh"] = len(chosen)
    return out


def _chosen_lh_support(df: pd.DataFrame) -> dict:
    """
    For each HH whose CHOSEN worker is in LH on a given side, check whether that
    HH has at least one NON-CHOSEN draw in LH on the SAME side. IS support test.
    """
    chosen = df[df["is_chosen_joint"] == 1]
    sim = df[df["is_chosen_joint"] == 0]
    result = {}
    for side in ("male", "female"):
        hcol, wcol = f"hours_{side}", f"working_{side}"
        draw_col = f"draw_{side}"
        ch_bands = _band_of(chosen[hcol].values, chosen[wcol].values)
        lh_uids = set(chosen.loc[ch_bands == "LH", "stacked_hh_uid"])
        if not lh_uids:
            result[side] = {"n_chosen_lh_hh": 0, "n_with_support": 0, "frac": 1.0}
            continue
        # For these HHs, do any non-chosen marginal draws hit LH on this side?
        sim_lh = sim[sim["stacked_hh_uid"].isin(lh_uids)]
        sb = _band_of(sim_lh[hcol].values, sim_lh[wcol].values)
        uids_with_support = set(
            sim_lh.loc[sb == "LH", "stacked_hh_uid"].unique())
        n_support = len(uids_with_support & lh_uids)
        result[side] = {
            "n_chosen_lh_hh": len(lh_uids),
            "n_with_support": n_support,
            "frac": round(n_support / len(lh_uids), 4),
        }
    return result


def run_gate(couples_path: Path, bench_male: int, bench_female: int) -> dict:
    df = pd.read_parquet(couples_path)
    n_hh = df["stacked_hh_uid"].nunique()
    alts_per_hh = int(df.groupby("stacked_hh_uid").size().mode().iloc[0])
    product_size = int(round((alts_per_hh - 1) ** 0.5))

    male_mass = _marginal_mass(df, "male")
    female_mass = _marginal_mass(df, "female")
    chosen = _chosen_lh(df)
    support = _chosen_lh_support(df)

    lh_expected = product_size * DEFAULT_WEIGHTS[BAND_NAMES.index("LH")]

    # PASS/FAIL evaluation
    lh_male_mean = male_mass["band_mean_draws_per_partner"]["LH"]
    lh_female_mean = female_mass["band_mean_draws_per_partner"]["LH"]
    pass_mass = (lh_male_mean >= LH_MIN_DRAWS_PER_PARTNER
                 and lh_female_mean >= LH_MIN_DRAWS_PER_PARTNER)
    pass_support = (support["male"]["frac"] >= LH_CHOSEN_SUPPORT_FRAC
                    and support["female"]["frac"] >= LH_CHOSEN_SUPPORT_FRAC)
    gate_pass = pass_mass and pass_support

    return {
        "couples_path": str(couples_path),
        "n_hh": n_hh,
        "alts_per_hh": alts_per_hh,
        "product_size": product_size,
        "lh_expected_draws_per_partner": round(float(lh_expected), 4),
        "male_marginal_mass": male_mass,
        "female_marginal_mass": female_mass,
        "chosen_lh": chosen,
        "chosen_lh_benchmark": {"male": bench_male, "female": bench_female},
        "chosen_lh_support": support,
        "thresholds": {
            "lh_min_draws_per_partner": LH_MIN_DRAWS_PER_PARTNER,
            "lh_chosen_support_frac": LH_CHOSEN_SUPPORT_FRAC,
        },
        "pass_mass": pass_mass,
        "pass_support": pass_support,
        "gate_pass": gate_pass,
    }


def _print_report(r: dict) -> None:
    print("\n" + "=" * 72)
    print(f"LH-COVERAGE GATE  ({r['product_size']}x{r['product_size']} = "
          f"{r['alts_per_hh']} alts/HH, {r['n_hh']} HH)")
    print("=" * 72)
    print(f"  LH expected draws/partner (weight x product_size): "
          f"{r['lh_expected_draws_per_partner']}")
    print(f"\n  Per-partner marginal mass (mean draws/partner):")
    print(f"  {'band':<6} {'male':>8} {'female':>8}")
    for name, _, _ in _FOCAL:
        m = r["male_marginal_mass"]["band_mean_draws_per_partner"][name]
        f = r["female_marginal_mass"]["band_mean_draws_per_partner"][name]
        flag = "  <-- LH" if name == "LH" else ""
        print(f"  {name:<6} {m:>8.3f} {f:>8.3f}{flag}")

    print(f"\n  Chosen-row LH workers:")
    print(f"    male   : {r['chosen_lh']['male']:>5}  "
          f"(benchmark {r['chosen_lh_benchmark']['male']})")
    print(f"    female : {r['chosen_lh']['female']:>5}  "
          f"(benchmark {r['chosen_lh_benchmark']['female']})")

    print(f"\n  Chosen-LH IS support (non-chosen LH draw same side):")
    for side in ("male", "female"):
        s = r["chosen_lh_support"][side]
        print(f"    {side:<6}: {s['n_with_support']}/{s['n_chosen_lh_hh']} "
              f"= {s['frac']:.3f}")

    print(f"\n  Thresholds: LH mass/partner >= {r['thresholds']['lh_min_draws_per_partner']}, "
          f"chosen-LH support >= {r['thresholds']['lh_chosen_support_frac']}")
    print(f"  pass_mass={r['pass_mass']}  pass_support={r['pass_support']}")
    print(f"\n  GATE: {'PASS' if r['gate_pass'] else 'FAIL — LH band starved; do NOT trust recovery'}")
    print("=" * 72)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--couples", type=Path, required=True,
                    help="Engine-ready (or bpool d1w1) couples parquet to check.")
    ap.add_argument("--benchmark-male", type=int, default=764,
                    help="Expected chosen-row LH male workers (D1 figures, default 764).")
    ap.add_argument("--benchmark-female", type=int, default=317,
                    help="Expected chosen-row LH female workers (D1 figures, default 317).")
    ap.add_argument("--out-json", type=Path, default=None,
                    help="Optional path to write the full JSON report.")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    r = run_gate(args.couples, args.benchmark_male, args.benchmark_female)
    _print_report(r)

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_json, "w") as f:
            json.dump(r, f, indent=2)
        print(f"  [JSON] {args.out_json}")

    sys.exit(0 if r["gate_pass"] else 1)


if __name__ == "__main__":
    main()
