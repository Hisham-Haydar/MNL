# RETRACTION NOTICE - 2026-06-03

Two-I (`docs/jmp_methodology/RURO_welfare_stage2_twoH_validation_v1.md`) supersedes the
model-fit interpretation in Section 2 of this report. The Section 2 claim that the
`P_chosen < 1/901` and chosen-rank `901/901` diagnostics show severe couples model
misfit is RETRACTED: Two-I showed that ranking was performed on the
importance-sampling-corrected V, dominated by the `-log_prior` proposal correction, not on
structural utility. On structural utility the chosen alternative is mid-pack
(median rank 385/901), and the estimator V/likelihood equivalence holds to machine
tolerance. The Two-H STOP remains valid for the other reason alone: the real,
non-negligible, unresolved singleton stored-target residual of roughly 16 percent.

# RURO Welfare — Stage Two, Increment Two-H: couples correction prep (residual bound, model fit, gate)

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-H only — bound the unexplained singleton
stored-target residual, characterise couples model fit, and (gate-conditional) produce a
side-artefact correction candidate for the `draw_joint=0` collision block.
**Status:** complete. **GATE OUTCOME: STOP after Tasks 1–2 — NO correction candidate
produced.** The singleton stored-target residual is **non-negligible (16.4 %) and
unresolved**; a residual of that size would contaminate the same share of any corrected
`draw_joint=0` value, so the correction candidate is not authorised to build (reviewer
decision, 2026-06-03). Tasks 3–4 were not run.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; nothing was
> re-estimated; no `V_i^dir` was computed; no redrawn node was priced; no build /
> storage / engine-ready / priced / precompute / chunk parquet was written or
> overwritten.** EUROMOD was run only on bounded collision-free existing-node control
> samples (Task 1) and the V machinery was reused read-only at `theta_hat` (Task 2). Not
> committed automatically.

---

## 1. Singleton stored-target residual (Task 1)

Deterministic sample: first **150 households/year × 3 years**, six singleton `draw_joint`
values per household (`1, 100, 250, 450, 700, 899` — a spread chosen to avoid the Two-G
single-node artefact), batched **per `draw_joint`** under collision-free full-node-key
stamping (resilient to one-bad-node EUROMOD aborts; see §1.1). **2,700 singleton nodes**
clean-repriced and compared to stored nominal.

| metric | value |
|---|---|
| singleton nodes repriced | 2,700 |
| clean-reprice failures | **444 (16.4 %)** |
| blocked nodes | 0 |
| 2015 / 2016 / 2017 fail rate | 13.0 % / 14.9 % / 21.4 % |
| component localisation | `ils_ben` 443, `ils_tax` 1 (`ils_origy`/`ils_sicdy` machine-zero) |
| `\|clean − stored\|` joint disposable | median **0** (most pass exactly); 90th pct €84.8; 99th pct €526.4; max €1,722.3 |

**Cross-decider-benefit hypothesis — REJECTED.** Two-G tentatively suggested a failing
decider's stored value might absorb the partner's child benefit. Across all 444 failures
(each with two deciders), only **2 (0.45 %)** have the stored-minus-clean gap approximate
the partner's stored or clean `ils_ben`. So the residual is **not** a cross-decider
benefit attribution.

**Verdict: NON-NEGLIGIBLE and UNRESOLVED.** ~1 in 6 singleton couples nodes do not
reproduce the stored `ils_ben` under a clean isolated/collision-free reprice, the inputs
are identical (established in Two-G), there is no collision at these nodes (0 TUDef), and
the mechanism is not the cross-decider pattern. The residual rises monotonically with the
data year. This is a genuine stored-target reproducibility gap in the production couples
baseline whose mechanism this increment does not resolve. **Not repaired here** (per
scope).

### 1.1 Instrument robustness note
An initial whole-batch reprice that mixed many households and many `draw_joint` values
aborted the native EUROMOD engine (one bad node aborts the batch). Two-H therefore (a)
uses a **dense per-batch node-ordinal** collision-free stamp that keeps stamped IDs
bounded, and (b) reprices **per `draw_joint`** with a recursive split-on-abort that
isolates any offending node as `BLOCKED` rather than losing the batch. With this, **0
nodes blocked** and **0 TUDef warnings** across all batches — the earlier abort was a
batch-composition artefact, not a per-node failure. The clean instrument continues to
reproduce `ils_origy`/`ils_sicdy` to machine zero.

---

## 2. Couples model-fit characterisation at theta_hat (Task 2)

Reusing the estimator/welfare couples V machinery at `theta_hat` over **all 7,438
couples** (V-grid alignment to node keys: max abs 0.0):

| quantity | value |
|---|---|
| `P_chosen` median | 7.68 × 10⁻¹¹ |
| `P_chosen` mean / max / min | 3.06 × 10⁻⁸ / 5.22 × 10⁻⁵ / 4.0 × 10⁻²⁰ |
| uniform benchmark `1/901` | 1.11 × 10⁻³ |
| share of HH with `P_chosen < 1/901` | **100 %** |
| chosen-alt **rank** within its 901-set (1 = best) | median **901**, mean 900.9, min 710, max 901 |
| chosen-alt **percentile rank** (1 = best) | median **0.0011** (bottom ~0.1 %) |
| share with chosen alt in top 1 % / 5 % / 10 % / 25 % | **0 % / 0 % / 0 % / 0 %** |
| share with chosen alt in **bottom half** | **100 %** |

**Interpretation (stated cautiously, not overclaimed).** Near-zero absolute `P_chosen`
*could* reflect grid fineness (probability spread thinly over 901 near-equivalent
alternatives) — but that benign reading requires the chosen alternative to sit **near the
top** of the set. Here the opposite holds: the observed chosen alternative ranks **last
(901st) for the median couple**, in the **bottom half for 100 %** of couples, and in the
**top 25 % for none**. That pattern is **genuine misfit**, not grid fineness: at
`theta_hat` the couples model systematically assigns the observed household choice among
the *lowest*-utility alternatives in its own choice set.

This is a **model-fit characterisation**, not a welfare finding, and it is not a claim
about identification or about whether re-estimation would change it. It does, however,
bear directly on the chosen-node contamination question of Two-G: because the chosen
alternative already carries ~0 probability and the worst rank, perturbing its consumption
moves the choice probabilities negligibly (consistent with Two-G's tiny `|ΔP_chosen|`);
the contamination's first-order effect runs through the direct `V_obs` term, not the
choice-probability channel.

---

## 3. Gate before Task 3

| condition | required | observed | pass? |
|---|---|---|---|
| clean-reprice instrument usable | yes | yes (income/contrib machine-zero; 0 blocked) | ✓ |
| singleton residual **negligible** (≤ 2 %) | yes | **16.4 %, unresolved** | ✗ |
| mapping corrected→engine-ready node keys unambiguous | yes | yes (alignment max abs 0.0) | ✓ |

**GATE FAILS on the residual condition.** A non-negligible, unresolved singleton residual
(16.4 %) would contaminate the same share of any corrected `draw_joint=0` value, which
would defeat the purpose of the correction candidate. Per the increment's stop rule —
and the reviewer decision recorded 2026-06-03 — the increment **STOPS after Tasks 1–2**.
**No correction candidate is produced; Tasks 3–4 were not run; no side artefact was
written.** (The gate is config-driven: `welfare.stage2.correction_prep.gate`
`require_residual_negligible: true`, `max_singleton_residual_fail_rate: 0.02`.)

---

## 4. What a later (separately authorised) increment must do first

Because the gate stopped on the residual, the next step is **not** a correction candidate
but **diagnosing the 16.4 % singleton stored-target residual**:

- it is localised to `ils_ben`, has identical inputs (Two-G), no collision (0 TUDef), and
  is **not** the cross-decider pattern (rejected here);
- candidate mechanisms to test under separate authorisation: a full production-chunk
  (~1.13 M-row) assessment-unit/tax-unit attribution effect not reconstructible from
  bounded batches; a build-time policy-system or ordering subtlety; or a stored-value
  provenance gap. Until the residual reproduces, clean reprice magnitudes on
  `draw_joint=0` cannot be trusted as a *correction* (they remain valid as a
  *contamination measure*, as in Two-F/Two-G).

The severe couples misfit (§2) is logged as a separate, prior question for any controlled
re-estimation: a model that ranks the observed choice last for the median couple should be
understood before its stored consumption inputs are corrected.

---

## 5. Files

- **Source (Two-H):** `scripts/welfare/welfare_correction_prep.py` (dense collision-free
  stamp, resilient batched reprice, cross-decider signature),
  `scripts/welfare/run_stage2_correction_prep.py` (Tasks 1–2, gate, Tasks 3–4 scaffold —
  gated off).
- **Config block:** `welfare.stage2.correction_prep` in
  `scripts/welfare/configs/welfare_stage1_w3.yaml`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_couples_correction_prep.json`
  (Task 1 residual + per-`draw_joint` batches + cross-decider samples; Task 2 fit; gate
  with explicit reason; `task3`/`task4` null).
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_correction_prep_euromod_console.log`.
- **Correction candidate:** **NOT produced** (gate stopped).

## Explicit scope statement

No W^3 welfare finding is produced; no measure beyond W^3 is touched; nothing was
re-estimated; no `V_i^dir` was computed; no redrawn node was priced; no build / storage /
engine-ready / priced / precompute / chunk parquet was written or overwritten. EUROMOD
was run only on bounded collision-free existing-node control samples. No correction
candidate was produced; had one been produced it would NOT have been authorised as
estimator input until separately reviewed. Resolving the singleton residual and any
controlled re-estimation remain out of scope and require separate authorisation.
