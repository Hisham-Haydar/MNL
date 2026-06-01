# RURO Welfare Gate Report — W^3 (Stage One)

**Date:** 2026-06-01
**Stage:** ONE only — build the welfare scaffold + run W^3 validation gates.
**Status:** **W^3 scaffold built; Gates 0, 2, 3, 4 + Gate 1 part (ii) PASS;
Gate 1 part (i) and the V_i^dir cross-check BLOCKED (inputs/machinery absent).**
**Repo HEAD at build:** `7cac2e3` (working tree; not committed by this run).
**Authority:** `JMP_welfare_spec_v5.md` (now tracked), contract
`RURO_welfare_scaffold_design_contract_v2.md`, proposal audit
`welfare_proposal_individualisation_check.md`.

> **Internal-artifact disclaimer.** Any W^3 welfare distribution or `I(Omega^3)`
> computed during these gates is an **INTERNAL validation artifact, not a welfare
> finding**, pending separate Stage-Two authorisation. Stage One did **not** run
> decomposition, bootstrap, gender-split robustness, stochastic dominance,
> intra-household equivalisation, or `W^1/W^2/W^4/W^5/W^6` as reportable measures.

---

## Gate ↔ contract cross-reference

| This report's gate | Maps to contract `RURO_welfare_scaffold_design_contract_v2.md` |
|---|---|
| **Gate 0 — Engine parity** | **Not in §6.** An implementation-parity gate added to make the contract's "one machine" guarantee (§1) **falsifiable**: the welfare core's logsum-derived likelihood at `theta_hat` must match the estimator's own negLL within tolerance. |
| **Gate 1 parts (i)–(ii)** + **Gate 4** | Together = contract **§6 gate 1** (the three-part welfare-integration gate). **Gate 1(i)** = part (i) draw-growth stability of `V_i^IS`; **Gate 1(ii)** = part (ii) ESS diagnostic + max-normalised-weight + flagged-subset `V_i^dir` cross-check; **Gate 4** = part (iii) reference coverage. |
| **Gate 2 — Inversion sanity** | **§6 gate 2** (reference recovers zero, monotonicity, bracketing convergence). |
| **Gate 3 — Household-unit integrity** | **§6 gate 3** (one `Omega_i` per couple from joint utility/budget; no per-capita split; type-conditional references). |
| *(Shapley-exhaustiveness)* | §6 forward requirement of the deferred **decomposition** contract — out of scope for this W^3 build. |

---

## Preflight results

### Preflight 1 — Reproducibility

| Check | Result | Evidence |
|---|---|---|
| `JMP_welfare_spec_v5.md` tracked & clean | **PASS** | `git ls-files --error-unmatch` resolves; `git status --porcelain` clean (operator committed v5 after the first preflight STOP recorded in the prior version of this report). |
| `theta_hat_realdata_901_v1.csv` exists | PASS | 47 params loaded (`[theta_star] loaded 47/47`). |
| `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` exists | PASS | parsed; 47-param spec. |
| Production 901-alt engine-ready data exists | PASS | `fr_p3a_bpool_engine_ready__{couples,singles}.parquet` + `__mnlmeta.json`. |

### Preflight 2 — Engine parity (design)

Inspected `build_jax_singles_ll` / `build_jax_couples_ll` (`scripts/bpool/jax_ll_probe.py`).
The estimator already forms, per row, `V = u + log_h + log_w + log_market - log_prior`
(lines 260, 461) and, per household, `lse_i = log Σ_j exp(V_j)` via
`jgroup_logsumexp`. **`lse_i` is exactly the welfare core `V_i^IS`** — the ex-ante
attained utility with the household-specific `-log_prior` already in each `V_j`.
The welfare core therefore **reconstructs the same spec-driven `V`** (singles and
couples kernels mirrored term-for-term) and is held honest by Gate 0, which asserts
the reconstructed logsum-negLL equals the estimator's own negLL. No estimator source
was edited (the reconstruction lives entirely in `scripts/welfare/`).

### Preflight 3 — Draw-multiplier datasets

**BLOCKED input.** The datasets for `core.integration.per_household_stability.draw_multipliers = [1,2,4]`
(2× and 4× the production 901-alt draw count) **do not exist**. Only `20x20`
(=401, a *coarser* grid) and the production `engine_ready` (901) are present. Per
instruction, data was **not** rebuilt and higher-draw inputs were **not** fabricated.
Consequence: the formal draw-growth stability sub-gate (Gate 1(i)) is **BLOCKED**;
production-resolution ESS diagnostics (Gate 1(ii)) are computed instead, and no full
Gate 1 pass is claimed.

---

## Gate results — PRODUCTION pass (all households, 901-alt couples)

Resolution guard: couples alts = **901** (asserted at load). Groups: singles_male
n=2243 (101 alts), singles_female n=2764 (101 alts), couples n=7438 (901 alts).

### Gate 0 — Engine parity — **PASS**

Welfare logsum-derived negLL vs estimator negLL, max abs difference:

| Group | max\|Δ negLL\| | estimator negLL | tol |
|---|---|---|---|
| singles_male | **0.000e+00** | 28489.0428 | 1e-6 |
| singles_female | **0.000e+00** | 35411.8635 | 1e-6 |
| couples | **0.000e+00** | 174603.7298 | 1e-6 |

Machine-exact for all three groups (smoke pass: 1.1e-13 / 0 / 0 at tol 1e-8). The
"one machine" guarantee holds: the welfare core reproduces the estimator's
likelihood construction byte-for-byte. **Failure would stop the run; it did not.**

### Gate 1 — Welfare integration (§6 gate 1)

**Part (i) — per-household `V_i^IS` draw-growth stability: BLOCKED.** The 2×/4×
draw-multiplier datasets do not exist (Preflight 3); not rebuilt, not fabricated. No
full Gate-1 pass is claimed on the strength of part (ii) alone — aggregate
production-resolution diagnostics do not substitute for draw-growth stability.

**Part (ii) — effective-sample-size diagnostic: PASS (computed, reported).**
`ESS_i = (Σ_s ω_is)² / Σ_s ω_is²`, with `ω_is = exp(V_is − lse_i)` the within-household
normalised importance weights. Threshold `core.integration.ess_threshold = 30`.

| Group | ESS min | ESS p05 | ESS median | ESS max | # below 30 / N | max-norm-wt median / max |
|---|---|---|---|---|---|---|
| singles_male | 1.73 | 6.5 | 20.3 | 48.9 | 1918 / 2243 | 0.139 / 0.758 |
| singles_female | 1.58 | 5.7 | 18.8 | 45.7 | 2493 / 2764 | 0.147 / 0.794 |
| couples | 1.79 | 16.4 | 63.2 | 307.0 | 1285 / 7438 | 0.065 / 0.745 |

**Reading.** The low-ESS tail is the **expected** exposure the proposal audit
predicted: the **common** hours (fixed D1 five-mode mixture) and employment (flat
`π0=0.10`) proposal channels are the non-individualised dimensions, so a subset of
households carries concentrated importance weight. Couples are markedly healthier
(median ESS 63 of 901) because the 30×30 joint grid spreads weight better than the
101-alt singles grids. This is a **diagnostic exposure, not a gate failure** — the
contract's escalation trigger is *persistent disagreement of `V_i^dir` on the
flagged subset*, which is BLOCKED below, not the ESS level itself.

**Flagged-subset `V_i^dir` cross-check: BLOCKED.** The redraw-from-`ĝ_i` estimator
(`V_i^dir`) requires redraw machinery (sampling integration nodes from the estimated
individual opportunity density) that is **not implemented in Stage One**. It is
reported BLOCKED, **not** silently approximated. Because the cross-check cannot run,
the **escalation trigger cannot fire** — no household is escalated from `V_i^IS` to
`V_i^dir`. This is a known Stage-One limitation to clear before any W^3 welfare
*finding* (Stage Two): the flagged subset above (households with ESS < 30) is the
exact set that cross-check must later vet.

### Gate 2 — Inversion sanity (§6 gate 2) — **PASS**

W^3 laissez-faire inversion solves `Phi_i(w) = lse_i(consumption + w) − V_i = 0` by
bracketing bisection (`Phi_i` strictly increasing in `w` ⇒ unique root).

| Group | zero-recovery max\|Φ_i(0)\| | monotone all | bracketed all | converged all | # non-converged |
|---|---|---|---|---|---|
| singles_male | **0.00e+00** | True | True | True | 0 |
| singles_female | **0.00e+00** | True | True | True | 0 |
| couples | **0.00e+00** | True | True | True | 0 |

- **Reference recovers zero:** `Φ_i(0) = 0` exactly for every household (the W^3
  reference *is* the household's own set, so the shifted set at `w=0` is the actual
  set). This is the contract's "reference recovers zero" check, met exactly.
- **Monotonicity:** `Φ_i(+ε) > Φ_i(−ε)` for every household.
- **Convergence:** the bracketing solve converged for all 12,445 households; zero
  per-household failures.

**Resulting Ω (W^3 against the own set) ≈ −2.91e-10 for every household** (min = p05
= median = p95 = max, at solver tolerance). This is **correct by construction**: the
laissez-faire equivalent income of a household evaluated against its *own* feasible
set is identically zero (no counterfactual reference is imposed at Stage One). The
non-trivial Ω variation arises only once a decomposition imposes an equalised
channel (Stage Two), which this contract does not implement.

### Gate 3 — Household-unit integrity (§6 gate 3) — **PASS**

| Group | one Ω per group | per-capita split | type-conditional ref | unique idorighh clusters |
|---|---|---|---|---|
| singles_male | True | False | True | 1738 |
| singles_female | True | False | True | 2164 |
| couples | True | False | True | 5838 |

Couples carry exactly one `Omega_i` per household from **joint** utility and joint
budget (couples consumption = household disposable-income sum; one logsum per
`group_starts` row). No per-capita split. References are type-conditional (singles
male / singles female / couples processed separately).

### Gate 4 — W^3 reference coverage (§6 gate 1 part iii) — **PASS**

W^3 laissez-faire uses the household's **own set with pay**; the reference "package"
is the per-alternative consumption `c_ij` already on the engine-ready data — **no
`Ā/J/o` and no EUROMOD evaluation required**.

| Group | all `c_ij` finite | all `c_ij` positive | # non-positive |
|---|---|---|---|
| singles_male | True | True | 0 |
| singles_female | True | True | 0 |
| couples | True | True | 0 |

`abar_j_o_required = false`. As the contract notes, the `Ā/J/o` EUROMOD exposure is a
later W^5/W^6/W^4 issue, **not** triggered by W^3.

---

## Smoke pass (25 HH/group) — cleared before production

| Gate | singles_male | singles_female | couples |
|---|---|---|---|
| Gate 0 max\|Δ\| (tol 1e-8) | 1.14e-13 | 0.0 | 0.0 |
| Gate 2 Φ_i(0) / monotone / converged | 0 / ✓ / ✓ | 0 / ✓ / ✓ | 0 / ✓ / ✓ |
| ESS median (of 101 / 901) | 21.6 | 17.5 | 68.5 |

Production was run only because the smoke pass cleared Gate 0 and basic runtime checks.

---

## Decomposition-readiness interfaces (exposed, not computed)

Per contract §7 — interfaces only, **no decomposition implemented**:

- Outputs exposed: `Omega_i^k`, `V_i` (= `V_i^IS`), `I(Omega^k)`, config-read block
  structure (`welfare.blocks`: preference 20 / ability 6 / access 23 names).
- `preference_equalisation_pinned_switch: held` (default; `theta_l_m`, `beta_ll`
  pinned, held — `swapped` available as a flag for Stage Two).
- `pool_opportunity_share: false` (singles/couples opportunity shares kept
  separable; no pooled headline object emitted).

---

## Gate summary

| Gate | Status |
|---|---|
| Gate 0 — Engine parity (impl-parity; makes §1 falsifiable) | **PASS** (machine-exact, all 3 groups) |
| Gate 1(i) — `V_i^IS` draw-growth stability (§6 gate 1.i) | **BLOCKED** (2×/4× datasets absent; not rebuilt/fabricated) |
| Gate 1(ii) — ESS diagnostic (§6 gate 1.ii) | **PASS** (computed + reported; low-ESS tail is the predicted common-channel exposure) |
| Gate 1 — `V_i^dir` flagged-subset cross-check (§6 gate 1.ii) | **BLOCKED** (redraw machinery not in Stage One; not approximated) |
| Gate 2 — Inversion sanity (§6 gate 2) | **PASS** (zero-recovery exact, monotone, all converged) |
| Gate 3 — Household-unit integrity (§6 gate 3) | **PASS** |
| Gate 4 — W^3 reference coverage (§6 gate 1.iii) | **PASS** (own-set `c_ij` complete; no `Ā/J/o`) |

**Overall:** the W^3 welfare core is **built and validated** for the gates whose
inputs exist. Two items are **BLOCKED on absent inputs/machinery** (draw-multiplier
datasets; `V_i^dir` redraw) — reported, not approximated. Neither blocks the Stage-One
*build*; both must clear before any W^3 welfare *finding* in Stage Two.

---

## Artifacts

- **Source:** `scripts/welfare/welfare_core.py` (parity extractor, `V_i^IS`, ESS,
  W^3 inversion, inequality, decomposition-readiness),
  `scripts/welfare/run_stage1_w3.py` (preflights + two passes + Gates 0–4).
- **Resolved config:** `scripts/welfare/configs/welfare_stage1_w3.yaml` (all
  country/year/spec values; source hardcodes none).
- **Results JSON (provenance):** `outputs/welfare/stage1_w3/smoke_results.json`,
  `outputs/welfare/stage1_w3/production_results.json`.

---

## Commands run

```
# Preflight (read-only)
git ls-files --error-unmatch docs/jmp_methodology/JMP_welfare_spec_v5.md   # now PASS
git status --porcelain docs/jmp_methodology/JMP_welfare_spec_v5.md          # clean

# Smoke pass (25 HH/group)
.venv\Scripts\python.exe scripts/welfare/run_stage1_w3.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --pass smoke --out-json outputs/welfare/stage1_w3/smoke_results.json

# Production pass (all households, 901-alt couples)
.venv\Scripts\python.exe scripts/welfare/run_stage1_w3.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --pass production --out-json outputs/welfare/stage1_w3/production_results.json
```

Tolerances: smoke parity 1e-8, production parity 1e-6 (both met machine-exactly);
inversion convergence 1e-6 residual / 1e-9 bracket width; ESS threshold 30.

---

## Internal-artifact statement (restated)

The W^3 `Omega_i` distribution and `I(Omega^3)` (Gini = 0, degenerate-by-construction
because Ω ≈ 0 against the own set) computed in these gates are **INTERNAL validation
artifacts, not welfare findings**. No welfare result is claimed. Reportable W^3
welfare and any decomposition are gated on separate Stage-Two authorisation, which
must first clear the two BLOCKED items (draw-multiplier stability; `V_i^dir`
flagged-subset cross-check).

## Next action (for the operator — not performed here)

1. Provide (or authorise building) the 2×/4× draw-multiplier datasets to clear
   Gate 1(i); and implement the `V_i^dir` redraw-from-`ĝ_i` machinery to clear the
   flagged-subset cross-check. Until both clear, W^3 stays validation-only.
2. This run did **not** commit (per "Do not commit automatically"). Source, config,
   and report are on disk for review.
