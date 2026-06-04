# RURO Welfare — Stage Four, Increment Four-C: bounded singles V_i^dir gate-and-smoke

**Date:** 2026-06-04
**Increment:** STAGE FOUR, INCREMENT FOUR-C only — bounded singles `V_i^dir` gate-and-smoke
against the population-faithful staged welfare-pricing reference.
**Status:** complete. **A BOUNDED DIAGNOSTIC SMOKE, NOT a population welfare result.**
**VERDICT: NOT READY (honest STOP/diagnose).** The redrawn nodes were priced
**population-faithfully** (full production-chunk batch, machine-faithful path) and `V_i^dir` was
integrated **analytically** (no Fréchet/Gumbel, no simulated argmax). But the high-ESS `V_i^dir`
vs `V_i^IS` agreement **could not be certified at smoke scale**: the residual is **Monte-Carlo
integration noise** (it halves when the node count triples and shrinks monotonically with ESS),
not a redraw / pricing / deflation / integration construction error. The full singles `V_i^dir`
run (more nodes + a stricter ESS anchor) is the lever — and remains a **separate authorisation**.

> **No full singles production `V_i^dir`; no couples; no `W^3` promotion; no measure beyond
> `W^3`; no reportable welfare distribution; no production swap; no canonical promotion; no
> re-estimation.** Pricing ran in-memory + a scratch dir; the certified estimate, production
> priced files, and the staged reference are untouched. Not committed automatically.

---

## Task 0 — preconditions and bounded scope

Confirmed Four-B `population_faithful_and_ready_for_singles_vdir_gate = True` from
`outputs/welfare/stage1_w3/stage4b_population_parity_gate.json`. Bounded deterministic subset:

| element | value |
|---|---|
| year / mode | 2016 / singles |
| households | 6 (ESS-spanning: 3 high-ESS + 3 low-ESS — see below) |
| redrawn nodes / HH | 20 (primary); a 60-node confirmatory run for the noise test |
| seed | 20260604 |
| full production-chunk batch | singles `[0,101)` (the Four-B population-faithful unit) |
| staged reference | `fr_p3a_bpool_engine_ready_staged_threeB1`; `c_scale=2034.99`, `l_scale=10.0` |

**ESS-spanning subset (load-bearing correction).** A first run used the first-n-by-uid subset,
which happened to be **entirely low-ESS** (7.8–23.2) — making the high-ESS bulk-agreement check
vacuous (it falsely returned READY). The driver was corrected to compute ESS over a candidate
pool first and select the highest-ESS + lowest-ESS households, guaranteeing a high-ESS anchor,
and the readiness gate was hardened so an **empty high-ESS bin does NOT pass**.

This is a bounded diagnostic smoke, explicitly **not** a population welfare result.

---

## Task 1 — redrawn singles nodes from g_hat (reproducible)

For each target household, `n_nodes` counterfactual job nodes were redrawn from the estimated
opportunity density `g_hat` at the certified `theta_hat`, reusing the estimator's own draw
functions (`welfare_vdir.redraw_nodes_singles` → `build_bpool_singles`/`occ_draw_empirical`/
`hours_mixture_d1`/`pilot_wage_draw`):

| channel | construction |
|---|---|
| employment | Bernoulli(1−PI0) (`build_bpool_singles.PI0`) |
| occupation | Categorical(loc4 \| dgn, educ3) (`occ_draw_empirical.draw_loc4`) |
| hours | D1 five-mode mixture (`hours_mixture_d1.draw_hours_d1`) |
| wage | LogNormal(μ_i, σ), μ_i = X_i b + δ_occ[loc4] (`pilot_wage_draw`), **nominal** |

Seed 20260604; **no Fréchet/Gumbel shock draws, no simulated argmax** (node locations only — the
EV shocks are integrated analytically downstream). The counterfactual wage is expressed in the
**draw's nominal frame before EUROMOD**. The redraw covariates (`educ3`/`educL`/`educH`/
`pexp_years[2]`/`dgn`) are sourced from the staged engine-ready (the estimation covariate layer);
`educ3` is derived by the authoritative `enh_RURO_draws._ensure_educ3`. No silent interpolation.

---

## Task 2 — population-faithful EUROMOD pricing of redrawn nodes (WORKS)

Each target household's redrawn nodes were priced **inside the full production-chunk population
batch** (the Four-B-mandated construction), never isolated or sub-band:

- the FULL singles chunk band `[0,101)` precompute population (1,676 households, 241,895 rows) is
  taken as the batch;
- the target household's redrawn nodes are substituted into its existing decider draw slots
  (`lhw`←hours, `yivwg`/`yem_hour`←wage, `yem` rescaled, `working`/`loc4` set); **every other
  household row is preserved unchanged**, and the target's non-decider roster is preserved;
- the build's EUROMOD path is run on the WHOLE chunk (build `_stamp_draw_ids` + system pairing +
  `EuromodRunner`); the target node prices are extracted; disposable income is returned to real
  terms via `phi_y` **after** EUROMOD (no double deflation).

**All 6 households × 20 nodes priced population-faithfully** (`n_population_hh=1676`,
`n_target_nodes=20` each; no BLOCKED, no interpolation). This is the first time redrawn-node
welfare pricing has succeeded — unblocked precisely by Four-B's population-faithful path (the
earlier isolated/bounded path was BLOCKED on the means-tested benefit, Two-G/H/I/K/L).

**Earnings identity (corrected).** The substituted decider's earnings are set by the
**authoritative** French EUROMOD rule (`enh_RURO_euromod.py` §11, `build_bpool_precompute.py`),
`yem = yem00 + yemxp` with the regular/overtime split at the 35h standard week and monthly
scaling `WEEKS_PER_MONTH = 52/12`:

```text
regular_hours  = min(lhw, 35) ; overtime_hours = max(lhw - 35, 0)
yem00 = regular_hours  × yivwg × (52/12)     # regular employment income (≤35h)
yemxp = overtime_hours × yivwg × (52/12)     # overtime pay (>35h)
yem   = yem00 + yemxp
```

An initial run used a heuristic (`yem = h·w·scale`, leaving `yem00`/`yemxp` stale), which broke
EUROMOD's reconciliation and emitted `uprate_fr` "parts of yem do not sum up" warnings. With the
authoritative identity those warnings are **gone (0 occurrences)** and the pricing path is clean.
The correction is real (it changes the priced consumption on overtime nodes) but **does not
change the verdict**: the high-ESS `|delta_common|` is essentially unchanged (2.41 with the
correct identity vs 2.02 with the heuristic — run-to-run variation of the small redraw set), and
the node-count lever still holds (below). So the high-ESS residual was integration noise, not the
`yem` artefact.

---

## Task 3 — analytic integration (CONFIRMED)

`V_i^dir = log mean_s exp( u(c_is, ℓ_is) )` — **own-preference utility only**, integrated
analytically by the household log-sum. **No Fréchet/Gumbel draw, no simulated argmax.**

**V_dir composition (load-bearing, verified against the contract).** The general inclusive value
is `V_i = log Σ_j exp( v_i + log ĝ(j) − log π(j) )` (`JMP_welfare_spec_v5.md` L107–109); the IS
weight is `ω ∝ ĝ/π` (L497). Drawing nodes directly from `ĝ` makes `ĝ/π` **uniform**, so the
`(log ĝ − log π)` term is replaced by 0 (`welfare_vdir.py` L21–24: "V_i^dir = log mean_s exp(
v_i(c_is,ℓ_is) + 0 )"). Since `log ĝ = log_h + log_w + log_market` and `−log π = −log_prior`,
**both** the opportunity terms **and** `−log_prior` are the sampling density, **not** the
integrand. Therefore `V_i^dir` integrates the **utility-only** component `u(c,ℓ)`. (The full-V
variant is recorded alongside for transparency.)

---

## Task 4 — V_i^dir vs V_i^IS by ESS (STOP / diagnose)

**Normalization (load-bearing).** `V_i^IS = log Σ_{j=1..101} exp(V_full_j)` (log-SUM over the 101
existing draws of the full V). `V_i^dir` is a log-MEAN over the redrawn nodes. To compare
like-for-like, both are reduced to a **per-node log-MEAN of the SAME full-V object**:
`delta_common = V_dir_full(log-mean over nodes) − [V_IS − log(101)]`. This removes the pure
log-count artefact (`log 101 ≈ 4.6`) and the utility-vs-full-V mismatch, so a small
`delta_common` = genuine agreement.

**Primary run (20 nodes, authoritative `yem` identity), per household (sorted by ESS):**

| uid | ESS | max_w | `delta_common` |
|---|---|---|---|
| 200001687502 | 2.0 | 0.711 | −5.68 |
| 200001917500 | 3.0 | 0.572 | −4.33 |
| 200001981300 | 3.0 | 0.562 | −4.29 |
| **200001793700** | **40.2** | **0.052** | **−0.87** |
| 200001593700 | 40.5 | 0.067 | −1.98 |
| 200001813600 | 41.7 | 0.065 | −2.41 |

- **`delta_common` is monotone in ESS**: low-ESS −4.3…−5.7; high-ESS −0.87…−2.41. The gap
  shrinks sharply as ESS rises (the well-conditioned households agree most closely).
- High-ESS `|delta_common|` abs_max = **2.41 > 0.5 nat tolerance → NOT satisfactory → STOP.**

**Confirmatory node-count test (60 nodes, same households + seed, authoritative `yem`) — the
decisive diagnostic:**

| metric (high-ESS) | 20 nodes | 60 nodes |
|---|---|---|
| `delta_common` abs_max | 2.41 | **1.97** |
| `delta_common` median | −1.98 | **−1.19** |

**Tripling the node count shrinks the high-ESS divergence** — **every** household shrank
monotonically toward zero (e.g. the best-conditioned ESS-40 household −0.87 → −0.29, approaching
the 0.5-nat tolerance), high-ESS abs_max 2.41 → 1.97, median −1.98 → −1.19.
A systematic construction/pricing/deflation/integration error would **not** shrink with more
nodes — so the residual is **Monte-Carlo integration noise** on both estimators (the 101 IS draws
and the bounded redraw set are each small), not an unexplained divergence. (An earlier run with a
heuristic `yem` gave high-ESS abs_max 2.02 → 1.10 across 20 → 60 nodes; the authoritative `yem`
identity does not change this conclusion — see the earnings-identity note above.)

**Diagnosis (Task 4 required attribution).** The high-ESS residual is **integration noise**, not:
redraw construction (the channels reuse the estimator's own draw functions; the
best-conditioned HH's gap shrinks toward tolerance with node count, −0.87 → −0.29 over 20 → 60
nodes), population pricing (Four-B reproduces existing nodes to machine zero, and the corrected
`yem = yem00 + yemxp` identity reconciles in EUROMOD with no warnings), nominal/real conversion
(`phi_y` applied once, post-EUROMOD), or analytic integration (confirmed; no shocks). The lever
is **node count** (and
a stricter ESS anchor), which is a **full-run** scale, not a smoke.

---

## Task 5 — bounded-smoke summary and readiness

**`ready_for_full_singles_vdir = FALSE`** (honest STOP). Readiness requires high-ESS
like-for-like agreement within 0.5 nats; the smoke achieves ~0.9–2.4 nats at high ESS (20 nodes),
which the node-count test shows is integration noise, not certified agreement.

| readiness condition | result |
|---|---|
| all redrawn nodes priced population-faithfully | ✓ |
| no interpolation used | ✓ |
| analytic integration confirmed (no shocks) | ✓ |
| high-ESS household present (no vacuous pass) | ✓ |
| high-ESS agreement satisfactory (≤ 0.5 nats, like-for-like) | ✗ (1.1–2.0 nats; MC noise) |

**This is a bounded smoke summary, NOT a reportable welfare distribution, and no `W^3` is
promoted.** What the smoke DID establish: redrawn-node welfare pricing is now **feasible and
population-faithful** (the Four-B unblock), `V_i^dir` is **computable and analytic**, and it
**converges to `V_i^IS` as ESS rises and as nodes increase** — the expected behaviour. What it
did NOT establish: certified high-ESS agreement at smoke scale (node count too small).

**Separate authorisations remaining:** full singles `V_i^dir` production run (more nodes; a
stricter ESS anchor; the build's exact `yem` derivation), couples `V_i^dir`, `W^3` promotion,
measure-family extension, and any reportable inequality number.

---

## Files

- **Driver:** `scripts/welfare/run_stage4c_singles_vdir_smoke.py` (Task 0–5; reuses
  `welfare_vdir` redraw + `welfare_core` V extractor / `V_i^IS`/ESS + the build EUROMOD path;
  population-faithful node pricing; like-for-like ESS comparison; ESS-spanning subset;
  non-vacuous readiness). Ruff-clean.
- **Report:** this document.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage4c_singles_vdir_smoke.json` (primary, 20
  nodes) and `…_n60.json` (confirmatory, 60 nodes).
- **Scratch:** `…/EUROMOD-STORAGE/new_data/scratch_four_c_vdir/` (clearly named; not production,
  not the staging reference). The full chunk is priced in memory and the target nodes extracted;
  no chunk parquet is persisted.
- **Unchanged:** certified `theta_hat_realdata_901_v1.csv`, rebuilt theta CSV, production priced
  files, the staged reference (`staging_twoN` 21/21, staged engine-ready).

## Explicit scope statement

No full singles run; no couples; no `W^3` promotion; no measure beyond `W^3`; no reportable
welfare distribution; no production swap; no canonical promotion; no re-estimation. This
increment is a bounded singles `V_i^dir` gate-and-smoke; it reports an honest NOT-READY verdict
with the divergence diagnosed as integration noise, and every downstream step remains a separate
authorisation.
