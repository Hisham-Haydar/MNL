"""
Welfare Stage Two — Increment Two-F: couples collision-exposure AUDIT (audit-only).

Quantifies how much of the STORED couples baseline is "collision-exposed" — i.e. lives
in a (data_year, stacked_hh_uid, draw_joint) block that contains more than one distinct
(draw_male, draw_female) alternative, so that production `_stamp_draw_ids` (which stamps
couples on draw_joint) collapses those distinct alternatives onto the same stamped
idperson. Two-E showed such nodes can carry a collision-contaminated stored value.

This module covers:
  Task 1 — alternative-level PREVALENCE audit (no EUROMOD).
  Task 2 — likelihood-RELEVANCE screen at theta_hat (reuse the estimator/welfare V
           machinery; NO re-estimation). Maps collision-exposed node keys onto the
           engine-ready couples alternatives and sums model-implied probability mass.

Terminology: nodes are "collision-exposed" / "potentially contaminated" until a clean
reprice (Task 3, separate runner) confirms a nonzero stored-vs-clean difference. Not
every exposed node is materially contaminated.

STRUCTURAL FACT (build-documented): build_bpool_precompute.py gate G2 states
"draw_joint=0 intentionally shared by chosen+first sim cell" — the collision is a known
build convention, dominated by draw_joint=0 carrying two alternatives.

DOES NOT: re-estimate, price redrawn nodes, compute V_i^dir, run growth, promote W^3,
touch any measure beyond W^3, or write any storage/precompute/priced/chunk/engine-ready
parquet. EUROMOD is NOT called here (Task 3 is a separate bounded runner).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
sys.path.insert(0, "scripts/enhanced")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

NODE_KEY = ["data_year", "stacked_hh_uid", "draw_joint", "draw_male", "draw_female"]
BLOCK_KEY = ["data_year", "stacked_hh_uid", "draw_joint"]


# ---------------------------------------------------------------------------
# Task 1 — prevalence (no EUROMOD), works on engine-ready couples key columns
# ---------------------------------------------------------------------------
def _block_distinct_alts(df):
    """Per-row int: number of distinct (draw_male, draw_female) pairs in this row's
    (data_year, stacked_hh_uid, draw_joint) block. One vectorized groupby-transform on a
    hashed pair — no Python-level per-block apply (the file has ~7M blocks)."""
    pair = (df["draw_male"].astype("int64") * 100000
            + df["draw_female"].astype("int64"))
    return pair.groupby([df[k] for k in BLOCK_KEY]).transform("nunique").to_numpy()


def _exposed_mask(df):
    """Per-row boolean: row is collision-exposed iff its block has >1 distinct
    (draw_male, draw_female) pair."""
    return _block_distinct_alts(df) > 1


def prevalence_audit(key_cols_df):
    """key_cols_df: engine-ready couples key columns
    (data_year, stacked_hh_uid, draw_joint, draw_male, draw_female, is_chosen_joint).
    Returns the per-year + pooled prevalence dict (alternative-level). Fully vectorized:
    one block-distinct-alts transform; all other stats are vectorized reductions."""
    df = key_cols_df.copy()
    df["__block_alts"] = _block_distinct_alts(df)      # distinct (dm,df) per block
    df["__exposed"] = df["__block_alts"] > 1
    chosen_col = "is_chosen_joint"

    def _block(sub):
        n_alts = len(sub)
        n_hh = int(sub["stacked_hh_uid"].nunique())
        n_exposed = int(sub["__exposed"].sum())
        # one row per block: (block keys, block_alts). collision block = block_alts>1.
        block_tbl = sub.drop_duplicates(BLOCK_KEY)[BLOCK_KEY + ["__block_alts"]]
        coll_blocks = block_tbl[block_tbl["__block_alts"] > 1]
        hh_with_coll = int(sub.loc[sub["__exposed"], "stacked_hh_uid"].nunique())
        chosen = sub[sub[chosen_col] == 1] if chosen_col in sub else sub.iloc[:0]
        chosen_exposed = int(chosen["__exposed"].sum())
        node000 = sub[(sub["draw_joint"] == 0) & (sub["draw_male"] == 0)
                      & (sub["draw_female"] == 0)]
        node000_exposed_hh = int(node000.loc[node000["__exposed"],
                                             "stacked_hh_uid"].nunique())
        # distribution: how many draw_joint blocks carry k distinct alternatives
        apd = block_tbl["__block_alts"].value_counts().sort_index()
        return {
            "n_households": n_hh,
            "n_alternatives": int(n_alts),
            "n_alternatives_exposed": n_exposed,
            "share_alternatives_exposed": float(n_exposed / n_alts) if n_alts else 0.0,
            "n_collision_blocks": int(len(coll_blocks)),
            "n_blocks_total": int(len(block_tbl)),
            "n_households_with_collision": hh_with_coll,
            "share_households_with_collision": float(hh_with_coll / n_hh) if n_hh else 0.0,
            "n_chosen_alternatives": int(len(chosen)),
            "n_chosen_exposed": chosen_exposed,
            "share_chosen_exposed": float(chosen_exposed / len(chosen)) if len(chosen) else 0.0,
            "node_000_exposed_households": node000_exposed_hh,
            "alts_per_draw_joint_block_distribution": {int(k): int(v) for k, v in apd.items()},
        }

    out = {"by_year": {}, "pooled": {}}
    for yr, sub in df.groupby("data_year"):
        out["by_year"][int(yr)] = _block(sub)
    out["pooled"] = _block(df)
    return out


# ---------------------------------------------------------------------------
# Task 2 — likelihood-relevance at theta_hat (reuse welfare/estimator V machinery)
# ---------------------------------------------------------------------------
def _reproduce_engine_order(cfg2):
    """Reproduce the EXACT row order the couples data object consumes, so the V grid's
    positional alternatives map unambiguously onto node keys. Mirrors
    joint_recovery_test._load_parquet_slice (sort by [stacked_hh_uid, draw_joint])
    followed by estimation_utils.precompute_data_couples (re-sort [idhh, year_tag] for
    pooled, stable). Returns the engine-ready couples frame (key cols + c_norm) in that
    final order, plus a per-row collision-exposed mask aligned to it."""
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    b = cfg2  # baseline block
    stem = b["couples_stem"]
    path = base / f"{stem}__couples.parquet"
    years = list(b.get("years", []) or [])
    cols = ["idhh", "stacked_hh_uid", "data_year", "year_tag", "draw_joint",
            "draw_male", "draw_female", "is_chosen_joint", "c_norm"]
    df = pq.read_table(path, columns=cols).to_pandas()
    if years:
        df = df[df["data_year"].isin(years)].copy()
    # sort 1: _load_parquet_slice
    df = (df.sort_values(["stacked_hh_uid", "draw_joint"], kind="stable")
          .reset_index(drop=True))
    # sort 2: precompute_data_couples (pooled only)
    if "year_tag" in df.columns and df["year_tag"].nunique() > 1:
        df = df.sort_values(["idhh", "year_tag"], kind="stable").reset_index(drop=True)
    df["__exposed"] = _exposed_mask(df)
    return df


def likelihood_relevance(cfg, thresholds):
    """Reuse welfare_core to build the couples V-extractor at theta_hat and compute,
    per household, the model-implied probability mass on collision-exposed alternatives.
    NO re-estimation. Returns dict + per-household arrays for downstream CSV.

    Alignment gate: asserts the reproduced engine order's c_norm equals the data
    object's consumption to machine zero; STOPs (returns mapping_ambiguous) otherwise."""
    import welfare_core as wc
    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    data = wc.load_data(cfg, n_hh=0)
    wc.assert_resolution(cfg, data)
    cou = data["couples"]
    n_groups = int(cou.n_groups)
    n_alts = int(cou.n_obs // cou.n_groups)

    ordered = _reproduce_engine_order(cfg["baseline"])
    if len(ordered) != n_groups * n_alts:
        return {"status": "mapping_ambiguous",
                "reason": (f"row count mismatch: engine-ready ordered={len(ordered)} "
                           f"vs data object n_obs={n_groups * n_alts}")}
    # ALIGNMENT GATE: c_norm in reproduced order must equal data.consumption exactly
    cons_obj = np.asarray(cou.consumption, dtype=np.float64)
    cons_ord = np.maximum(ordered["c_norm"].to_numpy(np.float64), 1e-12)
    max_align = float(np.nanmax(np.abs(cons_obj - cons_ord)))
    if max_align > 1e-9:
        return {"status": "mapping_ambiguous",
                "reason": (f"positional alignment failed: max|consumption(data) - "
                           f"c_norm(reproduced order)|={max_align:.3e} > 1e-9; the V "
                           f"grid cannot be mapped to node keys unambiguously."),
                "max_align_abs": max_align}

    # Build V at theta_hat (reuse estimator kernel) and per-household softmax weights.
    Vfn, _ = wc._build_V_extractor_couples(cou, spec)
    import jax.numpy as jnp
    V = np.asarray(Vfn(jnp.asarray(theta), jnp.asarray(cons_obj)))
    Vg = V.reshape(n_groups, n_alts)
    mx = Vg.max(axis=1, keepdims=True)
    w = np.exp(Vg - mx)
    w = w / w.sum(axis=1, keepdims=True)            # softmax prob per alt, sums to 1

    exposed = ordered["__exposed"].to_numpy().reshape(n_groups, n_alts)
    mass = (w * exposed).sum(axis=1)                # collision-exposed prob mass per hh

    # chosen-alt exposure per household
    chosen = (ordered["is_chosen_joint"].to_numpy() == 1).reshape(n_groups, n_alts)
    chosen_is_exposed = (exposed & chosen).any(axis=1)
    has_chosen = chosen.any(axis=1)

    # year per household (first row of each group)
    yr_grid = ordered["data_year"].to_numpy().reshape(n_groups, n_alts)[:, 0]
    hh_grid = ordered["stacked_hh_uid"].to_numpy().reshape(n_groups, n_alts)[:, 0]

    qs = [0.0, 0.5, 0.9, 0.99, 0.999, 1.0]
    res = {
        "status": "ok",
        "alignment_max_abs": max_align,
        "n_households": int(n_groups),
        "n_alts_per_hh": int(n_alts),
        "exposed_mass": {
            "mean": float(mass.mean()),
            "median": float(np.median(mass)),
            "max": float(mass.max()),
            "quantiles": {str(q): float(np.quantile(mass, q)) for q in qs},
        },
        "share_hh_above_threshold": {
            str(t): float(np.mean(mass > float(t))) for t in thresholds},
        "n_hh_above_threshold": {
            str(t): int(np.sum(mass > float(t))) for t in thresholds},
        "chosen_alt_exposed": {
            "n_households_with_chosen": int(has_chosen.sum()),
            "n_chosen_exposed": int(chosen_is_exposed.sum()),
            "share_chosen_exposed": float(
                chosen_is_exposed.sum() / max(1, has_chosen.sum())),
        },
    }
    per_hh = pd.DataFrame({
        "stacked_hh_uid": hh_grid.astype("int64"),
        "data_year": yr_grid.astype("int64"),
        "exposed_prob_mass": mass,
        "chosen_alt_exposed": chosen_is_exposed.astype(int),
    })
    return res, per_hh, {"n_groups": n_groups, "n_alts": n_alts}
