# RURO Rebuild — Stage Three, Increment Three-B2: controlled real-data re-estimation on the staged reproducible baseline

**Date:** 2026-06-04
**Increment:** STAGE THREE, INCREMENT THREE-B2 only — controlled real-data re-estimation on the
validated staged engine-ready baseline (Three-B1), under the pre-registered Three-A movement
criterion. Real-data verdict only; synthetic recovery deferred to Three-B3.
**Status:** complete. **VERDICT: REAL-DATA IMMATERIAL.** The re-estimation converged, the
Hessian is PD, clustered SEs are available for all 47 parameters, and **every
decomposition-relevant parameter moved by at most ≈1 % of its certified clustered SE.**

> **This is NOT the final A/B verdict.** Synthetic recovery on the staged reproducible baseline
> (Three-B3) is still required before the Two-O A/B decision (caveat-and-keep vs replace) can be
> settled. **No synthetic recovery, no `V_i^dir`, no redrawn-node pricing, no `W^3` promotion,
> no production parquet swapped/overwritten/moved/deleted, no promotion to canonical, and the
> certified `theta_hat_realdata_901_v1.csv` was NOT overwritten** (the re-estimate is a new
> versioned artifact). Not committed automatically.

---

## Task 1 — baseline + certified references (confirmed)

- **Staged stem** `fr_p3a_bpool_engine_ready_staged_threeB1` — singles (505,707 rows) + couples
  (6,701,638 rows) engine-ready present; `__mnlmeta.json` present (`n_draws` singles 101,
  couples 901).
- **Resolution guard:** couples alts/HH = **901**, singles = **101** (step4's built-in guard
  passed).
- **Cluster key:** `idorighh` → `cluster_id` (carried on the engine-ready; the step4 result's
  self-describing `cluster_key` field shows the generic fallback label, but the clustering IS
  `idorighh` — 9,657 clusters over 12,445 groups, matching the certified estimate).
- **Spec** `joint_pooled_v1_bll0_tlmpin`: **47 free parameters**, `theta_l_m` pinned −0.8 (in
  `fixed_params`), `beta_ll` fixed 0, `beta_c` fixed 1 (scale numeraire) — none in the free
  vector.
- **Warm start:** certified `theta_hat_realdata_901_v1.csv` (47/47 params loaded).

The re-estimation was run through the **certified estimation path**
(`scripts/bpool/step4_realdata_baseline.py`: warm-start → two-stage L-BFGS-B → optimistix BFGS
polish → exact `jax.hessian` PD check → `idorighh`-clustered sandwich), identical to the path
that produced the certified estimate, only the engine-ready stem changed.

---

## Task 2 — controlled real-data re-estimation (CONVERGED)

| quantity | value |
|---|---|
| start negLL @ certified `theta_hat` (staged data) | 238502.866934 |
| final negLL | 238502.866126 |
| improvement (start − final) | **0.000808 nats** |
| optimizer chosen | scipy L-BFGS-B (box) |
| max\|grad\| (scipy stall-floor) | 44.04 |
| in bounds | True |
| wall time | 896 s (≈ 15 min) |
| n households | sm 2,243 / sf 2,764 / couples 7,438 |

Warm-started from the certified `theta_hat`, the optimizer found it was **already essentially at
the staged-data MLE** — the negLL fell by only 8e-4 nats and the parameters barely moved
(Task 4). The reported `max|grad| ≈ 44` is the **scipy L-BFGS-B stall-floor** (step4 labels this
"the BFGS-family analogue of CONOPT RGmax", i.e. the optimiser's terminal gradient on this
problem family), **not** a sign of non-convergence: the decisive convergence evidence is the
**PD Hessian at the solution** (Task 3) together with the negLL sitting at the staged optimum and
sub-1 %-SE parameter movement. (The certified estimate's own terminal gradient is of the same
order on this BFGS family; the gradient floor is a property of the optimiser/problem, the same
for certified and staged.)

Convergence判定: **converged** (in bounds, finite negLL, rc 0). No STOP.

---

## Task 3 — clustered SEs / uncertainty (PD; full SE availability)

| quantity | value |
|---|---|
| Hessian PD | **True** |
| min eigenvalue | **+0.45888** |
| condition number | 1.29e6 |
| clustered SE available | **47 / 47** |
| cluster key | `idorighh` (9,657 clusters over 12,445 groups) |
| parameters at a bound | 3 |

**Parameters at a bound** (identical pattern to the certified estimate):
`beta_l_age2_sf` at hi (+1.0), `beta_l_age2_f` at hi (+1.0), `beta_l0_m` at lo (1e-6 — the
couples-male leisure floor, the documented "couples-male baseline leisure absent" feature of the
certified baseline). These are **the same bound-active parameters as certified**, not new
instability introduced by the staged data.

No SE failed; the Hessian is PD with full clustered-SE coverage. No STOP.

---

## Task 4 — parameter comparison under the pre-registered criterion

Per-parameter, certified vs rebuilt, with `|Δ| / certified_clustered_SE`. Band (pre-registered,
unchanged after seeing results): a decomposition-relevant parameter is **immaterial if
`|Δ| ≤ 1.0 × certified_clustered_SE`**.

**Super-block summary:**

| super-block | params | within band | outside band | max \|Δ\|/SE | median \|Δ\|/SE |
|---|---|---|---|---|---|
| ability / wage (`beta_w*`, `sigma`) | 6 | **6** | 0 | 0.0074 | — |
| opportunity / access (`beta_E*`, `beta_h_*`, `beta_occ_*`) | 23 | **23** | 0 | 0.0111 | — |
| preference (`beta_l0_*`, `beta_l_age*`, `beta_l_nkids_*`, `theta_l_*`, `theta_c_singles`) | 18 | **18** | 0 | 0.0054 | — |

**All 47 free parameters are within band.** The largest movement anywhere is
**`beta_h_lh`: |Δ|/SE = 0.0111** (Δ = −5.5e-4 on a certified clustered SE of 0.0495). Top movers:

| param | block | certified | rebuilt | Δ | cert clustered SE | \|Δ\|/SE |
|---|---|---|---|---|---|---|
| `beta_h_lh` | opportunity/access | −1.21848 | −1.21904 | −5.5e-4 | 0.0495 | 0.0111 |
| `beta_E_y2017` | opportunity/access | −0.06947 | −0.07012 | −6.5e-4 | 0.0753 | 0.0086 |
| `beta_w_pexp` | ability/wage | +0.38278 | +0.38257 | −2.1e-4 | 0.0280 | 0.0074 |
| `beta_w0` | ability/wage | +2.19682 | +2.19692 | +1.0e-4 | 0.0146 | 0.0070 |
| `theta_c_singles` | preference | +0.00758 | +0.00713 | −4.5e-4 | 0.0838 | 0.0054 |

Every decomposition-relevant movement is **≤ ~1 % of one certified clustered SE** — far inside
the band. The fixed/pinned set (`theta_l_m` = −0.8, `beta_ll` = 0, `beta_c` = 1) is unchanged by
construction.

---

## Task 5 — real-data verdict

**REAL-DATA IMMATERIAL** — all decomposition-relevant parameter movements are within the
certified clustered-SE band (max ≈1 % of a SE), with a converged fit and a PD Hessian.

**This is NOT the final A/B verdict.** Under the Two-O dispositive test, the controlled
re-estimation has two stages: the real-data movement check (this increment) and the
synthetic-recovery standard on the reproducible baseline (Three-B3). The real-data result here
is consistent with **Two-O Option A** (the irreproducibility is immaterial; the certified
estimate stands with a caveat) — but that conclusion **cannot be finalised** until the
synthetic-recovery gate on the staged reproducible baseline passes.

**Recommended next increment:** **Three-B3 — synthetic recovery on the staged reproducible
baseline** (PD Hessian at production scale + parameter recovery within tolerance, as for the
certified gate `RURO_jax_recovery_gate_tlmpin_901_v1`). Only after Three-B3 can the A/B decision
be settled.

---

## Files

- **Driver:** `scripts/welfare/run_stage3b2_controlled_reestimation.py` (runs the certified
  step4 path on the staged stem, warm-started from certified `theta_hat`; then the per-parameter
  comparison + verdict under the pre-registered band). Ruff-clean.
- **Certified-path addition (additive, agnostic):** `scripts/bpool/step4_realdata_baseline.py`
  gained `--out-json` (dumps the full result dict) and a `start_negLL` diagnostic — no change to
  the estimation itself.
- **Re-estimated theta (NEW versioned artifact, certified CSV NOT overwritten):**
  `scripts/bpool/specs/theta_hat_rebuilt_realdata_901_v1.csv` (`parameter,value,se_hessian,se_clustered`).
- **step4 result JSON / report:** `outputs/welfare/stage1_w3/stage3b2_step4_rebuilt.json`,
  `outputs/welfare/stage1_w3/stage3b2_step4_report.md`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage3b2_controlled_reestimation.json`
  (Tasks 2–5 + per-param comparison + verdict).
- **Staged engine-ready (Three-B1, unchanged):** stem `fr_p3a_bpool_engine_ready_staged_threeB1`
  (NOT canonical). **Certified engine-ready + certified `theta_hat` CSV + production priced files
  all unchanged.**

## Explicit scope statement

No synthetic recovery; no `V_i^dir`; no redrawn pricing; no `W^3` promotion; no production swap;
no promotion to canonical; the certified `theta_hat` CSV was not overwritten; nothing beyond
`W^3`. This increment runs the controlled real-data re-estimation only; the final A/B verdict
awaits the separately authorised Three-B3 synthetic recovery.
