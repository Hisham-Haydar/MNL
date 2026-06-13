# RURO Welfare F4-B — Inclusive-Value Normalization + W4/W6 Contract Decision Memo

**Date:** 2026-06-13 · **Type:** READ-ONLY diagnostic + decision exhibit. No F5, inequality,
decomposition, EUROMOD, estimation, engine/spec/data edits, or commit. F4A artifacts preserved
as diagnostic checkpoints (not overwritten). · spec_hash `492bcfa9c766bfcb` · theta_hash
`1dd94e9cf1f35464` · stem `fr_p3a_bpool_engine_ready_staged_threeB1` · S = 101 draws/HH.

> **Governance status (restated up front).** This memo is a **mathematical recommendation**, not
> an approval. `JMP_measure_mapping_memo_v1.md` remains **pre-registration / UNRATIFIED**. Nothing
> here ratifies any measure. The recommended contract (Task 6) takes effect only on explicit
> sign-off of Tasks 6.1–6.4.

---

## TASK 1 — Trace of the implemented normalization

### How `V_i^IS` is constructed

Per node the estimator forms the composite value, then sums (not means) within the choice set:

- `estimation_engine.py:365` — `V = u + log_h + log_w + log_market - np.log(data.prior)`
- `estimation_engine.py:380` — `lse = compute_log_sum_exp_by_group(V, data.group_starts, data.group_ends)`
- `estimation_engine.py:386` — `ll = np.sum(V_obs - lse)` (V_obs = `V` at draw 0, line 383)
- `estimation_utils.py:1618–1628` — `compute_log_sum_exp_by_group` returns
  `max_V_i + log(Σ_j exp(V_j − max_V_i))` = **`log Σ_j exp(V_j)`** — a raw log-**sum**, no `1/S`.
- Welfare core mirrors this exactly: `welfare_core.py:119–124` (`_group_lse_and_V`) and the Gate-0
  parity assertion `welfare_core.py:499–517`. F4A consumed the externally stored
  `V_i_IS_staged` and reproduced the staged singles negLL to |Δ|=1.5e-11 (F4A precond, machine-exact).

So `V_i^IS = log Σ_{j=1..S} exp(V_j)` over the S=101 importance-sampling draws.

### Does the importance-sampling estimator mathematically require `1/S`?

Yes, for a **level**. Each `V_j` already carries the IS weight `−log π_j` (`−np.log(data.prior)`,
line 365), so `exp(V_j) = exp(u_j + log ĝ_j) / π_j` is one importance-sampling draw of the
integrand `exp(u + log ĝ)` against proposal `π`. The consistent Monte-Carlo estimate of the
inclusive value `E[max] = log ∫ exp(u + log ĝ)` is the **mean** of those draws:

```
V_i^IS_level  =  log ( (1/S) Σ_j exp(V_j) )  =  log Σ_j exp(V_j) − log S  =  V_i^IS − log S.
```

The raw `log Σ_j exp(V_j)` over-counts by exactly `log S` (= log 101 ≈ 4.61512) relative to the
cardinality-invariant level. As S grows the **log-mean** converges to the continuum inclusive
value; the **log-sum** diverges as `≈ log S + (level)`.

### Why is the likelihood unchanged by omitting `−log S`?

The MNL choice probability is `P_i(obs) = exp(V_obs)/Σ_j exp(V_j)` — its denominator **must** be
the **sum** (a mean would give `S·P_i(obs) > 1`, not a probability). The per-household
log-likelihood `ll_i = V_obs,i − lse_i` (line 386). Replacing `lse_i` by `lse_i − log S` adds the
**θ-independent constant** `+log S` to every `ll_i`; a constant shift of the objective leaves the
argmax, gradient, and Hessian unchanged. Hence the estimator never needed `−log S`: it is
invisible to estimation but **load-bearing for welfare levels**.

### Existing diagnostics already subtract `log(n_draws)`

The like-for-like welfare comparisons in this codebase use `V_i^IS − log(n_draws)`:

- `run_stage4c_singles_vdir_smoke.py:779` — `vis_logmean = vis[uid]["V_i_is"] − np.log(n_draws)`
  (n_draws computed from the staged per-HH draw count; lines 757–763, 796).
- `run_stage4c2_vdir_bias_calibration.py:137,212` — `log_ndraws = log(n_draws)`;
  `vis_logmean = h["V_i_is"] − log_ndraws`.
- `run_f3r2a_repair_diagnosis.py:323` — `vis_logmean_basis = V_i_IS − np.log(N_DRAWS_EXISTING)`
  (`N_DRAWS_EXISTING = 101`).
- `welfare_vdir.py:21–24` (docstring) — V_i^dir is a **log-mean**; the IS weight is uniform under
  redraw, so the like-for-like basis subtracts `log(n)`.

### Verdict

- **(a)** Raw `V_i^IS` **is** a likelihood-compatible **unnormalized log-sum** (the conditional-logit
  denominator). Correct for estimation; carries `+log S` of draw-count scale.
- **(b)** `V_i^IS − log S` **is** the **cardinality-invariant welfare-level** object (the consistent
  IS estimate of the inclusive value), and it is already the basis used by every existing welfare
  cross-check.

---

## TASK 2 — Cardinality-invariance diagnostic (algebra + numeric)

**Algebra.** For values `v` of length `n`:
`logsumexp([v; v]) = log(2 Σ exp v) = log 2 + logsumexp(v)` — an **unnormalized** reference shifts
by `log 2` under exact node duplication. The **normalized** reference
`logsumexp(values) − log(n)` gives `log 2 + logsumexp(v) − log(2n) = logsumexp(v) − log n` —
**invariant** to duplication.

**Numeric (singles_male HH#0, 101 nodes):**

| quantity | value |
|---|---|
| `logsumexp(v)` | 10.059536 |
| `logsumexp([v; v])` | 10.752683 |
| diff | **0.6931471806** (= log 2 = 0.6931471806) |
| `logmean(v)` vs `logmean([v;v])` diff | **−1.78e-15** (invariant) |

**W3 / W1 invariance to subtracting `log(101)` from both sides** (target and own-set reference are
both 101-node log-sums, so `−log S` cancels and the root is identical):

| group | W3 max\|Δω\| raw vs normalized | W1 max\|Δω\| raw vs normalized |
|---|---|---|
| singles_male | **0.00e+00 EUR** | **0.00e+00 EUR** |
| singles_female | **1.10e-10 EUR** | **1.69e-10 EUR** |

**Gate (≤1e-8 EUR): PASS.** W3 and W1 are cardinality-consistent by construction — both sides carry
the same S=101 scale, which cancels. This is precisely why F4A's W3 (Ω≈0) and W1 (~1.6–1.7k EUR)
are valid regardless of the `log S` convention.

---

## TASK 3 — W4 normalization sensitivity (decision exhibit; A/B not selected in code)

W4 reference = one-node home utility `u(w, ℓ_home)`; the single node has no `log S` to cancel.

- **A. Current F4A:** target = raw `V_i^IS`; reference = one-node utility.
- **B. Cardinality-normalized candidate:** target = `V_i^IS − log 101`; reference = one-node utility.

| group | conv | W4 median (EUR) | p10 | p90 | min | max | below-floor | above **initial** cap | outside after **1 expand** | num-vs-analytic (norm) |
|---|---|---|---|---|---|---|---|---|---|---|
| singles_male | **A** | 4.492e6 | 2.117e6 | 9.746e6 | 3.49e5 | 5.306e7 | 0 | **2243 (100%)** | **111 (4.95%)** | 1.83e-10 |
| singles_male | **B** | 5.368e4 | 2.465e4 | 1.196e5 | 3.82e3 | 6.894e5 | 0 | 27 (1.20%) | **0 (0.00%)** | 4.69e-12 |
| singles_female | **A** | 5.566e6 | 2.800e6 | 9.982e6 | 4.57e5 | 7.347e7 | 0 | **2764 (100%)** | **73 (2.64%)** | 4.69e-10 |
| singles_female | **B** | 6.701e4 | 3.293e4 | 1.226e5 | 5.05e3 | 9.650e5 | 0 | 5 (0.18%) | **0 (0.00%)** | 6.58e-12 |

**Readings.**
- Normalization B reduces W4 by ≈84× (the `log S` shift of 4.615 nats, amplified by the
  `1/θc ≈ 132` Box-Cox exponent: a 4.615-nat drop in the target scales `w` by roughly
  `exp(−4.615/θc · θc) ≈ exp(−4.615)` on the relevant branch → ~1.2% of A).
- Under **A every household (100%) overflows the initial bracket** — a strong signal that raw
  `V_i^IS` is the wrong target scale for a one-node reference.
- Under **B no household falls outside the bracket after the single authorized expand-and-retry.**
- Numerical-vs-analytic agreement is ≤1e-8 (normalized) under both — the solver/evaluator machinery
  is sound; only the **target scale** differs.
- **Residual note (not a normalization error):** even under B, W4 medians (~54–67k EUR/mo) sit well
  above W1 (~1.6–1.7k). This residual is the **opportunity-density content the memo's W4 prices in
  by design**: `V_i^IS − log S = log mean_j exp(u_j + log ĝ_j − log π_j)` still carries the
  `(log ĝ − log π)` opportunity density, while the home node does not. `log S` fixes the
  **cardinality** mismatch (101 vs 1 nodes); the remaining gap is the memo's explicit
  "full-compensation endpoint" (opportunity AND wage priced into w), **not** a further normalization
  defect. Whether to additionally net out opportunity density is a deeper *measure-definition*
  question, distinct from this normalization ratification (see Task 6, item flagged).

---

## TASK 4 — W4 bracket-contract audit vs the memo verbatim

Memo `JMP_measure_mapping_memo_v1.md` §4 (locked defaults):
- Decision 2: "Bracketing bounds: w ∈ [DCM_MIN_POSITIVE = 1.0, 50 × max observed c_j],
  **expand-and-retry once, else flag HH**."
- Decision 4: "Non-convergent households: **flagged, excluded from Gini, COUNT REPORTED**
  (gate: **< 0.5% per group, else stop**)."
- §5.3: W4 "numerical vs analytic agreement ≤ 1e-8" — the analytic inversion is a **cross-check**,
  not a licence to accept households whose root lies beyond the bracket.

**Finding.** F4A accepted the 184 above-cap households (111 male + 73 female) via **unbounded
analytic inversion** beyond the bracket. Per the memo these are out-of-bracket after the single
authorized expand-and-retry and should have been **flagged / excluded / counted** toward the
<0.5% gate.

| group | conv | outside-bracket after 1 expand | rate | memo `<0.5%` gate |
|---|---|---|---|---|
| singles_male | A | 111 / 2243 | 4.95% | **FAIL** |
| singles_female | A | 73 / 2764 | 2.64% | **FAIL** |
| singles_male | B | 0 / 2243 | 0.00% | **PASS** |
| singles_female | B | 0 / 2764 | 0.00% | **PASS** |

**Conclusion.** Under convention **A**, W4 **fails** the memo's bracket contract in both groups
(the 184 households should have been flagged, not extrapolated; F4A's acceptance was a contract
deviation). Under convention **B**, the bracket gate **passes** with zero flagged households. The
bracket contract is therefore satisfiable **only under the cardinality-normalized target**.

---

## TASK 5 — W6 normalization contract (formalized; no hours points chosen)

W6 reference over the universal hours grid `J` (memo §3: "uniform weights … no ĝ, no π"):

- **A. Raw deterministic-set sum:** `V_ref(w) = log Σ_{j∈J} exp(u_j(w))` — **NOT** cardinality-
  invariant: adding/removing/duplicating a grid node shifts `V_ref` by `log(|J'|/|J|)`, so Ω depends
  on the arbitrary node count, not just the economic content.
- **B. Uniform-probability reference:** `V_ref(w) = log Σ_{j∈J} exp(u_j(w)) − log|J|` — the log-MEAN;
  **cardinality-invariant** (duplication-proof, per Task 2).

**Which matches "uniform weights"?** A uniform distribution puts probability `1/|J|` on each node:
`log Σ_j (1/|J|) exp(u_j) = logsumexp_j(u_j) − log|J|` = **B**. Convention B is the literal
implementation of the memo's "uniform weights"; convention A corresponds to *unit* (counting)
weights, which is not a probability and not what the memo states.

**Comparability with the actual side.** If the actual target is normalized to `V_i^IS − log S`
(Task 6.1) but the reference uses raw-sum A, the cardinality mismatch reappears as a `log(S/|J|)`
bias in Ω — re-importing exactly the W4 pathology at the grid level. For a coherent solve
`V_i^IS − log S = V_ref(w)`, **both** sides must be log-MEANS ⇒ the W6 reference must be **B**.

---

## TASK 6 — Ratification recommendation

### Mathematical recommendation (coherent contract)

1. **Actual-side welfare target:** **`V_i^IS − log S`** (S = per-HH draw count = 101). Rationale:
   the consistent IS estimate of the inclusive value; cardinality-invariant; already the basis of
   every existing Four-C / F3 welfare cross-check (Task 1); the only target under which W4 satisfies
   the memo bracket contract (Task 4).
2. **Deterministic reference normalization (W6, and any one-node/finite-set reference):** **uniform
   log-mean** `logsumexp_j(u_j) − log|J|`. Rationale: the literal meaning of "uniform weights";
   cardinality-invariant; required for like-for-like comparison against the normalized actual target
   (Task 5). (For W4, `|J| = 1` so the home reference value is unchanged — consistent with keeping
   "W4 single node unchanged".)
3. **W4 treatment beyond the memo's bracket:** **flag / exclude / count** per memo decisions 2 & 4 —
   do **not** accept unbounded analytic extrapolation. Under the recommended normalized target this
   is moot (0% outside bracket after one expand, both groups); the analytic inversion stays as the
   ≤1e-8 numerical cross-check only. The F4A behaviour (accepting 184 via extrapolation) is a
   contract deviation to be retired.
4. **Exact W6 grid still requires SEPARATE ratification** (independent of the above normalization):
   the representative hours point per estimation band {pt1, pt2, F35-ref, ft, lh}, whether the D1
   **BG** background band [5,70] contributes a node and at what hours, and the `TOTAL_LEISURE_HOURS`
   (=80) hours→leisure mapping constant. F4-B does **not** choose these (per F4A W6 design audit).

### Net effect on existing measures (no re-run authorized here)

- **W3, W1:** numerically **unchanged** (Task 2: Δω ≤ 1.7e-10 EUR). Remain valid.
- **W4:** target moves from raw `V_i^IS` to `V_i^IS − log 101`; reference (one-node) unchanged;
  medians ~54k/67k EUR; bracket gate passes (0% flagged). Recompute under the ratified contract at
  F5 build time, not here.
- **Open deeper question (flagged, NOT part of this normalization ratification):** even normalized,
  W4 retains the opportunity-density (`log ĝ − log π`) scale by the memo's design. If the ratifier
  judges the residual magnitude (~30× actual consumption) economically unacceptable, that is a
  **measure-definition** change (whether W4's target should be utility-only rather than the full
  inclusive value), to be raised separately from the cardinality normalization decided here.

### Governance status (separated from the math)

The mathematical recommendation above is internally coherent and evidence-backed by Tasks 2–5. It is
**not** approved. `JMP_measure_mapping_memo_v1.md` stays **pre-registration / UNRATIFIED** until an
explicit sign-off of Tasks 6.1–6.4 is recorded. No production W4/W6 and no F5 may proceed before
that sign-off.

---

## Artifacts preserved (not overwritten)

- `outputs/welfare/fastlane/singles_measures_F4A_v1.parquet` — F4A diagnostic checkpoint (raw-target W4).
- `outputs/welfare/fastlane/F4A_manifest_v1.json`,
  `docs/jmp_methodology/RURO_welfare_F4A_measure_core_report_v1.md` — F4A record (W4 large-scale
  caveat already flagged there).
- This memo is the only artifact written by F4-B. No commit.

---

W3 STATUS: valid
W1 STATUS: valid
W4 STATUS: BLOCKED PENDING NORMALIZATION RATIFICATION
W6 STATUS: BLOCKED PENDING NORMALIZATION + GRID RATIFICATION
READY FOR F5: NO
REQUIRED NEXT INPUT: explicit ratification of Tasks 6.1–6.4
