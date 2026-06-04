# RURO Rebuild — Stage Three, Increment Three-B3: synthetic-recovery gate on the staged reproducible baseline

**Date:** 2026-06-04
**Increment:** STAGE THREE, INCREMENT THREE-B3 only — synthetic-recovery gate on the staged
reproducible baseline, mirroring the certified 901 gate
(`RURO_jax_recovery_gate_tlmpin_901_v1.md`) **exactly**, with the same Check-5-load-bearing
verdict standard.
**Status:** complete. **FINAL TWO-O VERDICT: OPTION A CONFIRMED.** The load-bearing Check 5
(PD Hessian at the synthetic MLE) **PASSES at min_eig +1.771** (certified +1.706), at a fully
interior, two-start-agreed optimum, with **no new identification pathology** relative to the
certified gate. Combined with Three-B2 (REAL-DATA IMMATERIAL), the certified estimate stands
with the baseline irreproducibility documented as **immaterial**.

> **No `V_i^dir`, no redrawn-node pricing, no `W^3` promotion, no production parquet
> swapped/overwritten/moved/deleted, no promotion to canonical, and the certified / rebuilt
> real-data theta CSVs were NOT overwritten** (the recovered synthetic theta is a new versioned
> diagnostic artifact). Promotion to canonical, production swap, welfare pricing, and `V_i^dir`
> remain SEPARATE authorisations. Not committed automatically.

---

## Task 0 — pre-registered gate standard (frozen before the run)

Recorded in provenance before execution; **not changed after seeing the result**:

| element | value |
|---|---|
| mirrored certified gate | `RURO_jax_recovery_gate_tlmpin_901_v1.md` |
| DGP θ* source | `scripts/bpool/specs/theta_star_joint_v1.csv` |
| fit spec | `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` (47 free, `theta_l_m` pinned −0.8, `beta_ll`=0) |
| draw spec | `estimation_spec_joint_pooled_v1_bll0.yaml` (48 free, `theta_l_m` FREE) — the un-pinned sibling the numpy DGP requires; `theta_l_m` inserted at −0.8 (certified harness's own `_full_theta` convention) |
| staged stem | `fr_p3a_bpool_engine_ready_staged_threeB1` (the **only** change vs the certified gate) |
| seed | 20260530 (certified gate seed) |
| years / n_hh / resolution | 2015–2017 / 0 (all) / couples 901, singles 101 |
| tighten leisure bounds | **No** (certified 901 MLE was interior; tightening would force binds) |
| diagnostic thresholds | Check 2 ≤ 0.05, Check 3 ≤ 0.10, Check 4 ≤ 1e-6 |
| **load-bearing verdict** | **Check 5: PD Hessian at the synthetic MLE, no new bound/pathology vs certified.** Checks 2/3/4 are DIAGNOSTIC (the certified gate's own 2/3/4 mechanically FAILED and were read as flat-but-curved singles-leisure precision caveats). |

The recovery was run through the **certified harness** (`scripts/bpool/jax_recovery_gate.py`)
with the **gate logic unchanged**; only additive `--out-json` / `--out-theta-csv` outputs were
added (a machine-readable dump of the result dict and the recovered theta). The check
definitions, optimiser, DGP, thresholds, and verdict logic are untouched; only the engine-ready
stem was pointed at the staged baseline.

> **Lint note (honesty):** `jax_recovery_gate.py` is a pre-existing harness that does **not**
> pass `ruff` clean (16 legacy style findings — E702 semicolons, I001 import order, F541, SIM105
> — at lines 48/53/167/263/336/342/360/361/376/409/417/422/429/506). **None are in the
> additive lines this increment added** (the new arg defs and the JSON/CSV dump blocks introduce
> zero new violations); the file passes `py_compile`. The legacy style debt was deliberately
> left untouched so the certified gate body stays unmodified (rewriting its check logic would
> undermine the "harness unchanged" guarantee on which Three-B3's validity rests). The
> Three-B3 driver itself (`run_stage3b3_synthetic_recovery.py`) is `ruff`-clean.

---

## Tasks 1–2 — staged synthetic recovery

| Check | role | staged result | certified 901 | status |
|---|---|---|---|---|
| 1 Synthetic DGP | gate | PASS (one chosen alt/HH) | PASS | same |
| **5 Hessian PD @ MLE** | **LOAD-BEARING** | **PD, min_eig +1.7711, SEPARATELY IDENTIFIED** | PD, +1.7061 | **PASS (same sign, marginally higher)** |
| 2 Shared recovery | diagnostic | FAIL, max\|err\|=0.2827 (`beta_E_drgn3`) | FAIL, 0.2891 (`beta_E_drgn3`) | improved vs certified |
| 3 Group-specific | diagnostic | FAIL (see blocks) | FAIL | same pattern |
| 4 Two-start agreement | diagnostic | FAIL, max\|warm−cold\|=1.685e-4 | FAIL, 5.03e-5 | same basin |

**Interiority (the condition that makes Check 5 a valid identification verdict):**

- `warm_converged = True`, **`warm_bound_binding = []`** — no parameter binds any bound,
  identical to the certified gate.
- `beta_l0_m` = **+0.01928 INTERIOR** (certified +0.0191) — the couples-male leisure intercept
  sits interior, not at its 1e-6 floor; the pins (`beta_ll`=0, `theta_l_m`=−0.8) did their job.
- Two-start: warm negLL = **55371.5006** = cold negLL **55371.5006** (max\|warm−cold\| = 1.7e-4,
  tolerance-level, **same basin** — not multimodality).

So Check 5's PD Hessian is evaluated at a genuinely interior, two-start-agreed optimum — the
same textbook condition the certified gate relied on.

**Check 3 blocks (diagnostic) vs certified:**

| block | staged max\|err\| | certified | PASS | direction |
|---|---|---|---|---|
| sm_leisure | 0.4519 | 0.4074 | FAIL | worse (flat direction) |
| sf_leisure | 0.4429 | 0.4388 | FAIL | ~same |
| theta_c_singles | 0.0347 | 0.0330 | **PASS** | ~same |
| **m_leisure (pinned block)** | 0.0767 | 0.0790 | **PASS** | improved |
| f_leisure | 0.1437 | 0.1437 | FAIL | identical |
| beta_ll (removed) | — | — | **PASS** | — |

The failing blocks are **exactly the certified gate's flat singles-leisure directions**
(`sm`/`sf`/`f` leisure) — the same params (`theta_l_sm`, `theta_l_sf`) that dominate both the
elevated Check-3 errors and the slow Check-4 directions. **The pinned `m_leisure` block PASSES**
(0.0767), as in the certified gate — the direction the pins targeted recovers cleanly. No
decomposition-relevant (ability/wage, opportunity/access) block fails.

---

## Task 3 — comparison against the certified 901 gate

Classified per the certified report's own framing (not a stricter standard):

- **Check 5 (load-bearing):** staged **PD, +1.771** vs certified **PD, +1.706** — `same_sign_PD`,
  marginally *higher* curvature in the weakest direction. **Matches the certified load-bearing
  standard.**
- **Bound pattern:** staged `[]` vs certified `[]` — **no new binding direction**; `beta_l0_m`
  interior in both. `introduces_new_pathology = False`.
- **Check 2 residual:** 0.2827 vs 0.2891, worst is the **same** region dummy `beta_E_drgn3` —
  improved, same flat-but-curved interpretation, **not** a new failure.
- **Check 3 residuals:** failures confined to the **same** singles-leisure flat directions; the
  pinned block holds. Mixed small moves (sm/sf grew, region/m_leisure improved) — draw-specific
  realisations along flat directions, exactly as the certified report documents.
- **Check 4:** same basin (negLL agree to 1e-8; coordinate disagreement 1.7e-4 in the flat
  directions), tolerance-level as certified.
- **New decomposition-relevant failure:** **none** (`any_new_pathology = False`). No
  ability/wage or opportunity/access param, and no certified-passing block (`m_leisure`,
  `beta_ll`), fails.

The staged recovery reproduces the certified gate's structure: **load-bearing Check 5 PD at an
interior two-start optimum, with the only failures being the certified gate's own
already-characterised flat singles-leisure precision caveats.**

---

## Task 4 — final Two-O verdict

**OPTION A CONFIRMED.**

- **Three-B2** (controlled real-data re-estimation): **REAL-DATA IMMATERIAL** — converged, PD
  Hessian, clustered SE 47/47, every decomposition-relevant parameter within ≈1 % of one
  certified clustered SE.
- **Three-B3** (this increment, synthetic recovery): **matches the certified synthetic gate's
  load-bearing standard** — Check 5 PD at 901 (min_eig +1.771) at a fully interior,
  two-start-agreed MLE, **no new identification pathology**.

Therefore: **the certified estimate stands, with the baseline irreproducibility (the Two-N
finding) documented as immaterial.** The staged reproducible baseline is the **instrument** that
establishes this result — it is not promoted to canonical, and the certified estimate is not
replaced.

This is the **final A/B verdict** for the Two-O dispositive test (`is_final = True`). It does NOT
authorise any downstream action: **promotion to canonical, production swap, welfare pricing
(`V_i^dir`, redrawn-node pricing, `W^3` promotion) all remain separate authorisations.**

*(Honesty note: the warm synthetic MLE's terminal gradient is the BFGS-family stall-floor, as in
the certified gate; the load-bearing criterion is the PD Hessian at the interior two-start
optimum, exactly as the certified 901 gate — not a strict gradient-convergence claim.)*

---

## Files

- **Driver:** `scripts/welfare/run_stage3b3_synthetic_recovery.py` (pre-registers the standard,
  runs the certified harness on the staged stem, compares vs the certified 901 gate, emits the
  Two-O verdict). Ruff-clean.
- **Certified-harness addition (additive, agnostic):** `scripts/bpool/jax_recovery_gate.py`
  gained `--out-json` + `--out-theta-csv` — no change to the gate logic.
- **Recovered synthetic theta (NEW versioned diagnostic CSV; certified & rebuilt CSVs NOT
  overwritten):** `scripts/bpool/specs/theta_recovered_staged_synth_901_v1.csv`.
- **Staged gate JSON / report:** `outputs/welfare/stage1_w3/stage3b3_staged_gate.json`,
  `outputs/welfare/stage1_w3/stage3b3_staged_gate_report.md`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage3b3_synthetic_recovery.json`
  (pre-registered standard + staged recovery + comparison + Two-O verdict).
- **Certified `theta_hat_realdata_901_v1.csv`, rebuilt `theta_hat_rebuilt_realdata_901_v1.csv`,
  production priced files, staged engine-ready** — all unchanged.

## Explicit scope statement

No `V_i^dir`; no redrawn pricing; no `W^3` promotion; no production swap; no promotion to
canonical; the certified and rebuilt theta CSVs were not overwritten; nothing beyond `W^3`. This
increment runs the synthetic-recovery gate and reports the final Two-O verdict only; every
downstream action remains a separate authorisation.
