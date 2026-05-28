# RURO B-pool Recovery Test & Identification — Detailed Report v1

**Date:** 2026-05-27
**Scope:** Phase A (param binding) + Phase B (recovery test) on the 58-param B-pool
spec `estimation_spec_bpool_p3a_v1.yaml`, the engineering needed to run it, the problems
encountered, and the **central finding**: a structural utility-scale (consumption/leisure)
non-identification present across the entire RURO spec lineage.

---

## 0. Executive summary

We set out to run a parameter-recovery test (an identification gate) on the 58-parameter
B-pool couples spec before interpreting any real estimate. Getting there required fixing
several real engineering issues. The recovery test then **failed** — and, crucially,
inspecting prior **real-data** estimates showed the **same failure**. The converging
evidence is:

> **The RURO Box-Cox utility leaves the consumption coefficient `beta_c` and the leisure
> intercepts `beta_l0_*` all free; together they form a (near-)flat scale ridge. The
> likelihood Hessian is therefore not positive-definite (negative eigenvalues), `beta_l0_m`
> collapses to its lower bound, and the optimizer stops on the ridge while reporting
> "NormalCompletion". This is NOT a B-pool issue, NOT a 900-alt issue, NOT a solver issue,
> and NOT a sample-size artifact — it is a structural scale non-identification that has
> been present (and silently flagged) in M0, P3a-pooled, the NC pilot, and B-pool alike.**

The suspected remedy is a **scale normalization** (e.g. fix `beta_c = 1`), to be decided
at governance level because it affects the validity of all prior FR "converged" results.

---

## 1. Goal and method

**Goal.** Confirm the 58-param spec is *identified* on the B-pool design before trusting
any real coefficients. A recovery test does this: set a known `theta*`, generate synthetic
choices from it on the REAL choice sets, re-estimate, and check we recover `theta*` with a
well-conditioned Hessian.

**Spec under test.** `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` — 58 free
params = 55 P3a-pooled + `beta_h_lh` (long-hours) + `beta_E_drgur` + `beta_E_drgmd`
(urbanisation, D5). Couples product design: 900 simulated + 1 chosen = 901 alts/HH.

---

## 2. PHASE A — param binding (PASSED)

**Question.** Do all 58 spec params actually enter the likelihood on both PrecomputedData
objects, or are some silently skipped (a "false 58-param run")?

**What we did.** `scripts/bpool/phase_a_param_binding.py`: precompute on the engine-ready
B-pool parquets, capture all engine warnings, and (the decisive test) perturb each param
and confirm the LL moves.

**Problem found & fixed (harness).** First pass flagged 9 `_sf` params "not bound" — a
harness bug (female params can't bind on a male-only object). Fixed by testing singles as
**both** male and female objects.

**Result: PASS.** Zero silent drops on any object. 40/40 applicable on couples; 21/21
(male) + 22/22 (female) on singles. All at-risk params bound: `beta_E_drgur/drgmd/y2015/
y2017`, `beta_h_lh`, `beta_occ_*`, `beta_E_gsur`, the thetas. (Confirms commit b15adbb's
wiring fix covers both tracks.) → cleared to Phase B.

---

## 3. PHASE B — the engineering problems we had to solve first

Before the recovery test could even run, we hit and resolved a chain of real issues.

### 3.1 Data contract gap — engine-ready normalization layer
The engine consumes a specific MNL-prep contract (`c_norm`, `l_norm_*`, `leisure`,
`prior`, `idhh`, `year_tag`, `is_chosen`) + a `__mnlmeta.json` normalization block. The
B-pool track had only raw covariates + `ils_dispy_real`. **Fix:** wrote
`harmonise_bpool_engine_ready.py`, reproducing the Stage-M1/`enh_RURO_prep_mnl_basic.py`
normalization byte-for-byte (leisure = clip(80−hours,1); c_scale = mean(consumption);
l_scale = min positive chosen leisure; prior = exp(log_prior)), preserving the 901/101
design. Wrote `fr_p3a_bpool_engine_ready__{singles,couples}.parquet` + meta. Conformance
gate (`check_bpool_engine_ready.py`): 6/6 PASS.

### 3.2 Engine wiring gaps (committed)
- **`working_lh`** was referenced by the spec (`beta_h_lh`) but absent from the
  `PrecomputedData` dataclasses → the LL would crash. **Fix (commit 7912535):** added
  `working_lh[_male/_female]` to both dataclasses + builders; made the fallback **fail-loud**
  (the bpool definition is `1[hours∈[44.5,70]] AND working==1`; a 2-condition fallback would
  silently mis-flag, so we raise instead of deriving).
- **`drgur/drgmd/year_2015/2017_indicator`** were read by the couples market-opp block via
  `getattr` and **silently skipped** (only `reg2..8` were carried) → 4 of 58 params would
  not load. **Fix (commit b15adbb):** added all four (+`drgru`) to both dataclasses +
  builders, mirroring the `reg2..8` pattern. Verified the 4 now move the couples LL.

### 3.3 Solver behaviour
- **L-BFGS-B (spec default): STALLS** — ground 500+ iters with `|g|max` oscillating
  1e2–1e4, never converging. Reproduces the NC-pilot finding.
- **CONOPT/GAMSPy: works but ~3.5 h/start.** We initially misread the long GAMS model
  generation as a "hang" (it is documented at ~3.4–3.5 h/start at full size; the user
  correctly pushed back — it was not hung). A prototype (`proto_gamspy_intermediate_var.py`)
  **disproved** an O(n_alts²) symbolic-build hypothesis: the Python build is flat; the cost
  is GAMS *solving* the dense NLP (≈ quadratic in cells, crashes ~200k cells on a toy).
  CONOPT genuinely solves but is overnight-scale; the equivalence of an intermediate-variable
  reformulation was proven (|Δobj|=0) but it does NOT help (build was never the bottleneck).
- **scipy trust-constr (Hessian/trust-region): the practical choice** — navigates the
  curved manifold L-BFGS-B can't, no GAMS cost. Wired into `recovery_test.py`.

### 3.4 Variable-scaling problems (genuine sub-issues, fixed)
The per-iteration `@param` diagnostic (which param owns `max|g|`) revealed a cascade of
badly-scaled SQUARED regressors blocking the gradient test:
- **`beta_w_pexp2`**: `pexp_years2` ranged 0–2400 (coef bound 0.1) → gradient ~2400× too
  large. Fixed by rescaling `pexp_years` to decades, then /20 (→ `pexp_years2 ∈ [0,6]`).
- **`beta_l_age2_*`**: `age_norm2` ranged 0–636 → fixed by /10 (→ [0,5.7]).
These were real and necessary (they're standard regressor conditioning), applied in the
harmoniser; engine-ready parquets rebuilt; conformance gate still 6/6. But they only
**revealed** the deeper issue below.

---

## 4. PHASE B — recovery result: FAILED

**Setup.** `recovery_test.py` (package-grade: spec/country/year/mode-agnostic; `theta*`
generated generically from each param's (initial, bounds), no hardcoded names; vectorized
Gumbel-max synthetic choice on the real alternatives). Slice: couples 2016, 300 HH ×
901 = 270,300 rows. Solver: scipy trust-constr, warm start, maxiter 400.

**Outcome (synthetic recovery):**
- Did **not** converge (hit maxiter, `success=False`).
- **Hessian NOT positive-definite**: min eigenvalue **−0.0124**, condition number **inf**.
- **3 / 38 testable params** within tolerance & correct sign.
- Failure concentrated in the **couples consumption/leisure SCALE block**:
  `beta_c` (θ*=0.75 → 22.45), `beta_l0_m` (0.0125 → 21.05), `theta_l_m` (−0.75 → −4.96),
  all drifting to / toward their bounds. Other blocks (occupation, region, urbanisation)
  showed wrong signs/large errors **because the optimizer never reached the optimum** on
  the flat ridge — not necessarily because they are individually unidentified.

**Gate-by-gate:** G1 not interpretable (non-converged); G2 n/a (single start); **G3 FAIL**
(non-PD Hessian); **G3b unreliable** (covariance non-invertible → nan correlations);
G4 not cleanly recovered.

---

## 5. The central finding — corroborated on REAL data (3 independent sources)

The user directed us to prior real-data estimates. They show the **identical pathology** —
proving the recovery failure is structural, not a synthetic-`theta*` artifact:

| Source | n_neg eig | condition number | scale-param signature |
|---|---|---|---|
| **B-pool recovery** (synthetic, 58-param) | ≥1 (min eig −0.012) | inf | `beta_c`→22, `beta_l0_m`→21 drift to bounds |
| **M0c_b2** (real, couples occ) | 1 | ≥ 1e10 | `beta_l0_m` = 0.0119 (≈ lower bound); "not at a local maximum"; param corrs > 1 |
| **P3a-pooled** (real, 55-param, the direct bpool predecessor) | **5** | **3.32e9** | `beta_l0_m` = **1.0e-6** (AT lower bound); `beta_c` = 4.31; min eig −1.38e6; corrs up to 4.9 |

Every one reported `SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)` yet every one
carried the diagnostics' own flags: `negative_eigenvalues_present`, `parameters_at_bounds`,
"not at a local maximum or numerically singular". The "convergence" was the solver stopping
on a flat ridge / hitting the bounding box — not a true optimum.

---

## 6. Suspected root cause (diagnosis)

The RURO couples utility is
```
U = beta_c·BC(c) + beta_l0_m·BC(l_m) + beta_l0_f·BC(l_f) + (shifters) ,  theta_c fixed = 0
```
with `beta_c`, `beta_l0_m`, `beta_l0_f` ALL freely estimated. These multiply the level
(Box-Cox) terms and form a (near-)flat direction in the likelihood: the data weakly pins
their absolute scale, so the optimizer slides along the ridge — `beta_l0_m` to its lower
bound, `beta_c` large — producing the negative Hessian eigenvalue(s) and the inflated
parameter correlations (|corr| > 1, only possible with a non-PD covariance).

Earlier in this investigation we briefly hypothesised the additive, unscaled opportunity
terms (`log_h + log_w + log_market − log(prior)`) would anchor the scale and that the
failure might be a synthetic-`theta*` artifact. **The real-data diagnostics refute this:**
even with real choices and the full opportunity structure, the Hessian has up to 5 negative
eigenvalues and `beta_l0_m` pins at its bound. The scale is genuinely under-identified.

**What it is NOT:** not B-pool-specific (P3a-pooled shows it worst, with 5 neg eig); not a
900-alt/product issue (P3a-pooled is the 100-alt diagonal); not solver-specific (L-BFGS-B,
CONOPT, and trust-constr all hit it); not sample-size (a normalization indeterminacy does
not sharpen with N — present at 300 HH and at the full 2,577-HH pilot alike).

---

## 7. Suspected remedy (NOT yet applied — governance decision)

Standard fix for a utility-scale indeterminacy: **fix one scale parameter** to pin the
ridge. Conventional choice in Box-Cox labour supply (AC2013-style): **normalize
`beta_c = 1`** (consumption as numéraire; all other utility weights relative to it),
dropping it from the free set (58→57). The engine already supports fixing a parameter to a
compile-time constant via the `couples_fixed_box_cox_exponent` mechanism (parser omits it
from `all_param_names`; engine uses the constant) — `beta_c` could be fixed the same way,
across BOTH the LL and gradient paths, singles and couples.

This must be decided at governance level because:
- it changes the estimation design (one fewer free param + a normalization convention), and
- it implies prior FR "converged" results (M0, P3a-pooled, NC pilot) were ill-conditioned
  / not at a true optimum — i.e. their point estimates and any welfare numbers derived from
  them are suspect until re-estimated under a normalized scale.

**Validation path once chosen:** apply the normalization, re-run the *cheap* recovery test
(trust-constr, minutes). Expect: PD Hessian, `theta*` recovered, then G3b
urbanisation×region becomes meaningful.

---

## 8. Artifacts produced

**Scripts (scripts/bpool/):** `phase_a_param_binding.py`, `recovery_test.py` (package-grade,
vectorized, agnostic), `harmonise_bpool_engine_ready.py`, `check_bpool_engine_ready.py`,
`proto_gamspy_intermediate_var.py` (prototype that disproved the build-cost hypothesis),
plus superseded `phase_b_recovery_test.py`.

**Engine fixes (committed):** `estimation_utils.py` — `working_lh` (7912535) and
urbanisation/year indicators (b15adbb) wired into PrecomputedData.

**Data (storage `new_data/`):** `fr_p3a_bpool_engine_ready__{singles,couples}.parquet` +
`__mnlmeta.json` (with decade-scaled pexp/age); a `_2016c` couples subset prepared for a
potential CONOPT diagnostic (not run).

**Docs:** `RURO_recovery_test_results_v1.md` (per-param table + corrected VERDICT); this
report.

**Recommendation recorded:** do NOT spend ~3.8 h on a full-data CONOPT run — it would
reproduce the same ill-conditioned `NormalCompletion` already seen in M0c_b2 and P3a-pooled.
The high-value next step is the scale-normalization decision + a fast re-test.

---

## 9. Solver verdict (for the spec)

- L-BFGS-B: stalls on this manifold — do not use as the primary solver.
- CONOPT (GAMSPy, vectorized): converges-as-far-as-the-ridge-allows but ~3.5 h/start
  generation; and it masks non-identification behind "NormalCompletion".
- scipy trust-constr: best at navigating the manifold + exposes conditioning honestly
  (computes the Hessian) — recommended for recovery/diagnostic work.
- **No solver was written into `optimization.method`** because none cleanly converged to an
  identified optimum on the un-normalized spec. The solver choice should be revisited AFTER
  the scale normalization fixes identification.
