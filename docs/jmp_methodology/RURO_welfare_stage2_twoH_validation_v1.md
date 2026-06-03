# RURO Welfare — Stage Two, Increment Two-I: read-only validation of the Two-H stop result

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-I only — READ-ONLY validation of the two Two-H
stop findings.
**Status:** complete. **Split verdict:**

- **Two-H finding (b), the couples model-fit diagnostic (P_chosen < 1/901, chosen rank
  median 901/901): MODEL-FIT DIAGNOSTIC ARTIFACT.** The rank was computed on the
  importance-sampling V grid (which carries the `−log_prior` IS de-biasing term and a
  proposal-centered market term), not on structural choice utility. Removing the dominant
  IS term lifts the chosen rank from last to **mid-pack (median 385/901)**. The estimator
  V itself is correct (it reproduces the certified likelihood to machine tolerance) — only
  the *rank interpretation* was the artifact.
- **Two-H finding (a), the collision-free singleton residual (≈ 16 %): REAL.** It is
  collision-free under the full node key, reproduces under an INDEPENDENT isolated parity
  path at the same rate (paired isolated rate 17.5 %, batch-only-false rate 0.8 %), and
  spreads across draw_joints and both decider sexes.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; nothing was
> re-estimated; no `V_i^dir` was computed; no redrawn node was priced; no build / storage
> / engine-ready / priced / precompute / chunk parquet was written or overwritten.**
> EUROMOD was run only on bounded collision-free existing-node control samples. Not
> committed automatically.

---

## Task 1 — couples model-fit diagnostic: MODEL-FIT DIAGNOSTIC ARTIFACT

### 1.1 The V grid is the certified likelihood's V (equivalence holds)
The certified real-data couples likelihood (`build_jax_couples_ll`,
`use_actual_choice=False`) takes the observed term as **column 0** of each household's
901-row block (`jgroup_logsumexp`, `V_obs = Vg[:,0]`). Checks:

| check | result |
|---|---|
| engine-ready row 0 per HH == observed chosen alt (`is_chosen_joint==1`) | **100 %** (7,438/7,438; exactly one chosen per HH) |
| V-grid consumption alignment to node keys (`\|consumption − c_norm\|` max abs) | **0.0** |
| certified estimator negLL vs welfare-grid negLL | 174603.72976561091 vs …094, **max abs 2.9 × 10⁻¹¹** |
| `gate0_parity` max abs | **0.0** |
| sign orientation: corr(V, softmax) over a 200-HH sample | all **> 0** (median ≈ 0.53) |

So the welfare V grid used for the chosen-rank computation **is** the certified
estimator's V at `theta_hat`: same observed row, same `V_obs`, same logsum, same per-HH
LL contribution, correct sign. The chosen-marker convention is **not** the artifact.

### 1.2 The rank-901 result is an importance-sampling weighting artifact
The estimator forms, per row, `V_j = u_j + log_h_j + log_w_j + log_market_j − log_prior_j`.
The `−log_prior` term is the **importance-sampling proposal correction** (the household
logsum is an IS estimate over draws from proposal density `g`): the **observed** chosen
row is drawn with prior = 1 → `log_prior = 0`, while the 900 **simulated** cells carry
`−log_prior > 0` (median **+14.8 nats**). Ranking alternatives by this IS-augmented V
therefore pushes the observed row to the bottom **by construction**, independently of
structural fit.

| ranking basis | chosen-rank median | mean | min | share bottom-half | share top-25 % |
|---|---|---|---|---|---|
| **IS-V** (as Two-H computed) | **901** | 900.9 | 710 | 100 % | 0 % |
| **structural** (IS `−log_prior` removed) | **385** | 420.9 | 1 | 40.5 % | 24.4 % |

The median chosen-to-rowmax IS-V gap is **20.6 nats**, of which **≈ 14.8** is the
`−log_prior` term alone (the remainder includes the proposal-centered `log_market`, also
an IS object — so the structural figures are a *lower bound* on the de-biasing). Removing
the dominant IS term moves the chosen alternative from **dead last** to **mid-pack**
(median 385/901, in the top quartile for 24 % of couples, bottom-half for 40 %).

**Conclusion:** the "model assigns the observed choice the worst utility / near-zero
probability" reading is a **diagnostic artifact** of ranking by the IS-corrected V rather
than by structural choice utility. The estimator's likelihood and V are correct (§1.1);
the *rank/percentile statistics reported in Two-H §2 are not a valid couples-fit measure*
and should not be cited as evidence of pathological misfit. (A structural-fit assessment
would rank by structural utility, where the observed choice sits mid-pack; whether that
mid-pack fit is itself "good" is a separate question not adjudicated here.)

---

## Task 2 — singleton stored-target residual: REAL

### 2.1 Sampled nodes are genuinely collision-free
Every sampled singleton node has exactly one `(draw_male, draw_female)` pair in its
`(stacked_hh_uid, draw_joint)` block (full-node-key check); **all failures are
collision-free** and fire **0 TUDef** warnings. Stored and clean rows are matched on the
exact `(stacked_hh_uid, draw_joint, draw_male, draw_female, idperson_true, ruro_decider)`
within the same year and system pairing.

### 2.2 The residual reproduces under an INDEPENDENT parity path
The decisive test: reprice the **same** node both via the Two-H dense-batch instrument and
via the independent **isolated Two-E `_compare`** path (single household, original IDs),
and tabulate agreement (n = 120; 40 HH × 3 years, node `(draw_joint=1, draw_male=1,
draw_female=2)`):

| year | n | isolated fail | batch fail | both | batch-only | isolated-only |
|---|---|---|---|---|---|---|
| 2015 | 40 | 5 | 5 | 5 | 0 | 0 |
| 2016 | 40 | 7 | 8 | 7 | 1 | 0 |
| 2017 | 40 | 9 | 8 | 8 | 0 | 1 |
| **total** | **120** | **21 (17.5 %)** | 21 | 20 | **1 (0.8 %)** | 1 |

The **independent isolated path fails at 17.5 %** — essentially the same as the dense-batch
rate — and the dense batch produces **only 1 batch-only false failure in 120 (0.8 %)** at
this scale. So the residual is **not** a measurement artifact of the Two-H instrument: it
is confirmed by a second, independent comparison implementation. (A caveat on the
instrument: at much larger dense-batch sizes — e.g. 150 HH in one batch — a few additional
batch-only failures appear, so the dense-batch collision-free stamp has a mild scale
sensitivity and should be confirmed isolated when used at scale; this does **not** affect
the residual's reality, only the instrument's large-batch precision.)

### 2.3 Clustering
- **By year:** rising — 9.6 % (2015) / 12.5 % (2016) / 22.5 % (2017).
- **By draw_joint:** spread across the sampled values (dj 1/100/250/450/700/899 each carry
  12–21 failures of 120) — **not** confined to one node.
- **By decider sex of the diverging decider:** male 60, female 47 — both sexes, no strong
  skew.
- **Component:** localised to `ils_ben` (as Two-G/Two-H), with `ils_origy`/`ils_sicdy`
  reproduced to machine zero.

The Two-G cross-decider-benefit hypothesis remains **rejected** (Two-H). The residual is a
genuine stored-target reproducibility gap on ~16–18 % of singleton couples nodes, real and
unresolved as to mechanism, **not repaired here**.

---

## Verdict

This increment produces a **split** outcome against the prompt's four options:

- **For Two-H finding (b) — MODEL-FIT DIAGNOSTIC ARTIFACT (option 2).** The rank-901 /
  `P_chosen ≈ 0` couples-fit claim is an artifact of ranking by the importance-sampling V
  (the `−log_prior` IS correction dominates); on structural utility the observed choice is
  mid-pack (median 385/901). The estimator likelihood/V are correct (equivalence to machine
  tolerance). **The Two-H §2 "severe misfit" framing should be retracted; it is not a
  basis for any decision.**
- **For Two-H finding (a) — RESIDUAL VALIDATED AS REAL (option 1, for this half).** The
  ≈ 16 % collision-free singleton residual is real: collision-free, reproduced by an
  independent isolated parity path at the same rate (17.5 %), spread across draw_joints and
  both decider sexes, localised to `ils_ben`, mechanism unresolved.

**Consequence for the Two-H gate decision.** Two-H stopped before the correction candidate
for two stated reasons. One of them (the model-fit severity) is now shown to be an
artifact and is withdrawn. **The other (the real, unresolved ≈ 16 % singleton residual)
stands and independently justifies the stop**: a non-negligible unresolved residual would
contaminate the same share of any corrected `draw_joint=0` value. So the Two-H STOP remains
correct, but for **one** valid reason, not two. The next step before any correction or
controlled re-estimation is still to **diagnose the singleton residual mechanism**; the
model-fit concern should be re-expressed (if at all) as a structural-rank statement, not
the IS-rank artifact.

---

## Files

- **Source:** `scripts/welfare/run_stage2_twoH_validation.py` (read-only; reuses
  `welfare_core`, `welfare_assessment_unit_diag`, `welfare_correction_prep`,
  `jax_ll_probe`).
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_twoH_validation.json`
  (Task 1 equivalence + IS/structural rank decomposition; Task 2 clustering + paired
  isolated-vs-batch).
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_twoH_validation_euromod_console.log`.

## Explicit scope statement

No W^3 welfare finding is produced; no measure beyond W^3 is touched; nothing was
re-estimated; no `V_i^dir` was computed; no redrawn node was priced; and no build / storage
/ engine-ready / priced / precompute / chunk parquet was written or overwritten. EUROMOD
was run only on bounded collision-free existing-node control samples. This increment is
read-only validation; it produced no correction candidate and authorises nothing.
