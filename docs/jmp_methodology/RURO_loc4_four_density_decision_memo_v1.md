# RURO loc4 four-density (S-occ) decision memo — v1

*France RURO / JMP P3a · read-only diagnostic + decision memo · 2026-06-12*
*Roadmap lane S1 (`docs/JMP_results_campaign_roadmap_v1.md:93`). Certified baseline: `joint_pooled_v1_bll0_tlmpin` (47 free parameters).*

**Document class.** Read-only diagnostic and pre-registration memo. No estimation, optimization,
synthetic recovery, or Hessian computation was performed. No engine, builder, parser, spec, or data
file was edited. The descriptive tables below are read-only `pandas`/`pyarrow` reductions of the
certified engine-ready parquets; nothing was written to disk except this memo.

loc4 taxonomy used throughout (from `docs/jmp_methodology/JMP_conditional_wage_on_occupation_decision_note_v1.md:30`
and `.../JMP_next_cycle_opportunity_respecification_plan_v1.md:195-211,222-230`): **1 = routine-manual (RM),
2 = non-routine-manual (NRM), 3 = intellectual (Intel), 4 = non-intellectual (NonInt, the high-wage class);
reference = 1.**

---

## 1. Executive verdict

**Verdict A — a parallel, gated S-occ (occupation-specific residual-dispersion) specification is
warranted.** The descriptive support for the *primary* four-σ alternative (one σ_k per occupation,
**no gender split**, pooled over household type and year) is abundant: every occupation cell holds
between **1,800 and 9,162 chosen workers** drawn from **1,371–5,393 distinct households**, and the
simulated choice sets provide within-set occupation and wage variation in essentially every group.
The accepted-wage residuals under the certified Mincer mean differ across occupations in a real and
non-trivial way (per-occupation residual SD **0.327–0.443** vs the certified σ̂ = 0.390; max/min ≈ **1.35**).

"Warranted" means precisely what Verdict A says: the data support **building and gating** a parallel
specification. It does **not** mean identification is proven, nor that four σ_k will beat common σ.
This read-only diagnostic **cannot** adjudicate common-σ vs S-occ (the Verdict-D concern is real and
is folded in): that decision is deferred to the synthetic-recovery, real-data-Hessian, and
decomposition-sensitivity gates in §11. The implementation gap is genuine — **the certified JAX
estimation path does not support occupation-specific σ and would silently mis-estimate or crash on
the nearest existing wage specs** — but it is tractable and localized (§6).

The **gender × occupation** (eight-σ) saturation is a *distinct, more saturated future extension*,
not the primary alternative; it begins to hit thin cells (singles-male Intel n = 104) and is deferred.

---

## 2. Certified structural wage likelihood (Task 1a)

**wage_spec = `vw`** (`scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml:58`,
`wage_opportunity` block at lines 163-177). The structural wage density is a single shared log-normal:

> log w_ij | X_i, working_ij = 1  ~  Normal(μ_i, σ²),   μ_i = β_w0 + β_wL·educL_i + β_wH·educH_i + β_wpexp·pexp_i + β_wpexp2·pexp_i²

with **exactly six parameters**, all shared across gender, household type, year, **and occupation**:

| Parameter | θ̂ (certified 901) | clustered SE | role |
|---|---|---|---|
| `beta_w0` | 2.196822 | 0.014615 | log-wage anchor |
| `beta_w_educL` | −0.060764 | 0.012257 | return to low education |
| `beta_w_educH` | 0.338203 | 0.008638 | return to high education |
| `beta_w_pexp` | 0.382780 | 0.027955 | return to experience (per decade) |
| `beta_w_pexp2` | −0.082242 | 0.012585 | experience² (per decade) |
| `sigma` | 0.389825 | 0.004277 | residual dispersion (one scalar) |

Source: `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` rows 43-48 (`se_clustered` column).
`pexp`/`pexp²` are per-decade (engine-ready scaling, `..._mnlmeta.json:24`).

**Exact implemented formula (certified JAX path).** The certified production estimator
(`jax_recovery_gate.py`, `step4_realdata_baseline.py`, `jax_optimize.py`) builds the likelihood from
`scripts/bpool/jax_ll_probe.py`. Singles (`jax_ll_probe.py:238-245`):

```text
mu        = Σ_k P(coef_k) * x_k                 # intercept + educL + educH + pexp + pexp2
sigma     = P(sigma_name)                       # single scalar
resid     = (log_wage - mu) / sigma
log_w_full= -0.5*resid**2 - log(sigma) - 0.5*LOG2PI - log_wage      # log-normal + Jacobian
log_w     = where(working > 0, log_w_full, 0.0)                     # worker gate
```

- **Worker gating:** `where(working > 0, …, 0.0)` — non-workers contribute zero to the wage term.
- **Log-normal Jacobian:** the `- log_wage` term converts the density of log w to the density of w
  (the IS proposal `log_q_W` carries the matching `-log(w)`, so the Jacobian cancels in V − log_prior).
- **Singles vs couples:** identical density. Couples (`jax_ll_probe.py:441-449`) sum the **same**
  worker-gated log-normal over the male and female legs, each with its own covariates and
  `working_male`/`working_female` gate, but with `sigma = P(sigma_name)` — **the same scalar** for both
  legs and for both singles groups.
- **Sharing:** the joint objective optimizes one θ vector over singles-male + singles-female + couples,
  so `beta_w0…beta_w_pexp2` and `sigma` are **a single shared set** across all four worker populations
  and all years; there is **no** gender, household-type, year, or occupation index on any of them.
- The NumPy engine matches exactly: singles `vw` uses `sigma = params[spec.wage_variance_param]`
  (`estimation_engine.py:654`), couples likewise (`:1626`). The certified spec contains **no** occupation
  variable in `wage_opportunity` — the parser's exclusion restriction (`estimation_spec_parser.py:712-725`)
  forbids `loc4`/`loc` in the wage mean.

**Confirmation requested by the task: σ is one scalar, not indexed by any dimension.** Confirmed.
`spec.wage_variance_param` resolves to the single name `sigma`; `theta_hat_realdata_901_v1.csv` has one
`sigma` row; both JAX legs and both NumPy engines read that one scalar.

---

## 3. Occupation-access process (Task 1b)

The occupation coefficients are **access / offer-mass** parameters, **not** wage-mean parameters.

| Parameter | θ̂ (901) | clustered SE | | Parameter | θ̂ (901) | clustered SE |
|---|---|---|---|---|---|---|
| `beta_occ_2_m` | −1.591649 | 0.055322 | | `beta_occ_2_f` | −0.047581 | 0.044892 |
| `beta_occ_3_m` | −2.294101 | 0.070031 | | `beta_occ_3_f` | −0.472919 | 0.049159 |
| `beta_occ_4_m` | 0.290643 | 0.031438 | | `beta_occ_4_f` | 0.771794 | 0.037545 |

Source: `theta_hat_realdata_901_v1.csv:37-42`.

**Routing (parser → engine).** They are declared in the dedicated `occupation_opportunity` block
(`…tlmpin.yaml:241-274`, `variable: loc4`, `reference: 1`, `interaction: [working]`). The parser
(`estimation_spec_parser.py:689-749`) validates the exclusion restriction (loc4 may appear **only** in
`occupation_opportunity`, not in utility / hours / wage / market) and then **appends the occupation
shifters to `market_opportunity_shifters`** so the engine evaluates them inside `log_market`. The
JAX engine therefore folds them into the market term: `V = u + log_h + log_w + log_market − log_prior`
(`jax_ll_probe.py:248-260` singles, `:451-461` couples), with proposal-weighted within-choice-set
centering. They enter **`log_market`** (occupation-offer/access mass), gated by `working`; they do **not**
enter μ_i in the wage density.

- **Gender-specific, pooled across marital status:** `applies_to: male` collapses sm+cm; `applies_to:
  female` collapses sf+cf (`…tlmpin.yaml:17-24, 250-274`). Six coefficients (3 per gender).
- **Conceptually separate from σ_k:** `beta_occ_*` govern *how many offers of each occupation the market
  makes available* (an access channel, normatively compensation-relevant). σ / σ_k govern *the spread of
  the wage paid conditional on working* (a wage-technology channel, normatively ability). These are
  different objects on different sides of the structural model (g-access vs g-ability) and must not be
  merged. The governance cut is explicit:
  `docs/France_case/_shared/governance/JMP_ability_opportunity_cut_v1.md:66,124` —
  "`beta_occ_{2,3,4}_{m,f}` … **offer availability, not wage parameters**" and "loc4 … **offer mass, not wage**".

**Mischaracterization finding (recorded, not edited).** The certified descriptives report
`docs/jmp_methodology/RURO_postestimation_descriptives_v1.md:106-115` states that the baseline implements
"ONE log-wage density with occupation MEAN shifts … occupation enters … as a **mean shift** on `loc4` …
So LOC4 acts purely as a **mean shift on the single shared log-wage density** with common σ," and plots
"four curves sharing σ with means shifted by `beta_occ_*`". **This is incorrect.** `beta_occ_*` are
`log_market` (access) coefficients; the certified structural wage mean μ_i contains **no** occupation
term (`…tlmpin.yaml:165-175`; parser exclusion `estimation_spec_parser.py:712-725`). Treating `beta_occ_*`
as a wage-density mean shift conflates the access block with the wage technology and contradicts the same
project's governance cut (cited above) and the report's own Task-1 table (`…descriptives_v1.md:34`, which
correctly labels occupation "opportunity/access"). The text and the `loc4_wage_densities` figure should be
relabelled: those four "densities" are an *access-weighted illustration*, not occupation-conditional wage
densities, and `beta_occ_*` are not μ-shifters. **No file was edited; this is recorded for correction.**
(For contrast, the NC-pilot reports correctly distinguish the *proposal* `delta_occ` premium — calibrated,
fixed — from the free access `beta_occ`; see `Results/NC_pilot/JMP_NC_pilot_loc4_precompute_augmentation_report_v1.md:30,310`.)

---

## 4. Proposal wage-draw process (Task 1c)

The B-pool importance-sampling proposal (W1) is a **separate** mechanism from the estimated structural
likelihood. Its job is to generate the simulated alternatives and the matching proposal density; it is
divided out of the objective by the `− log_prior` correction.

- **Conditional on loc4? YES.** The W1 proposal draws log w ~ Normal(X·b + δ_occ[loc4], σ_prop²)
  (`scripts/pilot/pilot_wage_draw.py:8-10,56-87`): the proposal mean is shifted by `delta_occ2/3/4`
  with reference loc4 = 1.
- **Proposal occupation effects: fixed/calibrated, not estimated.** `delta_occ*` and the proposal
  coefficients come from a pre-fitted payload (`wage_model_W1.coef`, from
  `pilot_mincer_coefficients_v1.json`; `pilot_wage_draw.py:19-21,136`). The *occupation draw itself*
  (which loc4 each alternative gets) is **empirical**, sampled from frozen stratum frequencies p(loc4 | dgn,
  educ3) (`scripts/bpool/occ_draw_empirical.py:2-15,31-92`). Neither is jointly estimated.
- **Proposal dispersion: common.** A single scalar `sigma = float(mincer_payload["wage_model_W1"]["sigma"])`
  (`pilot_wage_draw.py:137`); the module explicitly notes an occupation-specific-σ proposal would be a
  future payload extension (`pilot_wage_draw.py:37-39`).
- **log_q_W / log_q_Occ / log_prior.** `log_q_W` = log-normal density at the drawn wage with the
  occupation-conditional mean and common σ_prop (`pilot_wage_draw.py:174-188`); `log_q_Occ` = log p(loc4 |
  dgn, educ3) (`occ_draw_empirical.py:13`). The per-alternative prior is
  `log_prior = log_q_E + working·(log_q_Occ + log_q_H + log_q_W)`
  (`scripts/bpool/run_bpool_draws.py:14-22,173-176`). Chosen rows (draw == 0) carry `log_q = 0` (the
  observed alternative is not a proposal draw) (`run_bpool_draws.py:226-229`). The engine subtracts it:
  `V = … − log_prior` (`jax_ll_probe.py:260`; prior convention `…_mnlmeta.json:23`). This `− log_prior`
  term is what separates the proposal from the structural likelihood — the proposal density is divided out,
  leaving the structural model as the estimand.

**Plain statement (as required).** That the W1 *proposal* conditions drawn wages on occupation does **not**
imply that the *estimated structural* wage likelihood has occupation-specific means or variances. The
proposal only determines *where the simulated support lands*; the importance-sampling correction
(`− log_prior`) removes it. The certified estimated density remains common-mean / common-σ (§2). (It is
worth noting the asymmetry: the proposal already "believes" occupation shifts the wage *mean* via
`delta_occ`, while the estimated structural mean omits occupation entirely — but that asymmetry is about
the *mean* channel and is orthogonal to the present S-occ *variance* question.)

---

## 5. Formal S-occ alternative and parameter count (Task 2)

**Primary S-occ alternative (occupation-specific residual dispersion, common mean, no gender split):**

> log w_ij | X_i, loc4_ij = k, working_ij = 1  ~  Normal(X_i·β_w, σ_k²),   k ∈ {1,2,3,4}

with:

- the **same** shared Mincer mean X_i·β_w as the certified baseline (β_w0, β_wL, β_wH, β_wpexp, β_wpexp2 unchanged);
- the **same** separate occupation-access block `beta_occ_*` (unchanged, still in `log_market`);
- four positive occupation-specific dispersions σ_1, σ_2, σ_3, σ_4 replacing the single σ;
- **no gender split** of σ_k in the primary alternative.

**Positivity-preserving parameterization — two candidates:**

1. Four positive levels σ_1, σ_2, σ_3, σ_4, each estimated with a positive lower bound (mirrors the
   baseline `sigma: [0.1, 20.0]` bound, `…tlmpin.yaml:434`).
2. **Anchored log-ratios (recommended):** keep the **existing certified `sigma` parameter as σ_1**,
   directly (its current bound and value unchanged), and add three ratio parameters:

   ```text
   sigma_1 = sigma                                  # the existing direct certified parameter, unchanged
   sigma_k = sigma_1 * exp(delta_log_sigma_k),  k = 2,3,4
   ```

**Recommendation: parameterization 2 (anchored log-ratios), explicitly NOT an exponentiated reference.**
Reasons: (i) it guarantees positivity of σ_2,σ_3,σ_4 by construction while σ_1 retains its existing positive
bound — cleaner Hessian/KKT reading than four free parameters near a floor; (ii) it makes the **nested-model
sanity gate exact**: δ_log_σ_2 = δ_log_σ_3 = δ_log_σ_4 = 0 gives σ_k = σ_1 **identically** (no `exp(log(·))`
round-trip), so the common-σ likelihood reproduces bit-for-bit (gate 3, §10); (iii) because σ_1 **is** the
unchanged certified `sigma`, the **certified-negLL regression gate** (gate 4) reproduces exactly; (iv) the
δ_log_σ_k are directly the log-dispersion *differences* across occupations, the quantity the
decomposition-sensitivity analysis wants. **Correction to v1 draft:** an earlier draft proposed
σ_1 = exp(log_σ_ref); that is rejected — exponentiating the reference both breaks the bit-exact nested/regression
gates and is *not* idiomatic to this estimator (the Box-Cox curvature parameters `theta_*` are bounded
**directly**, not exponentiated; `…tlmpin.yaml:74,79,374-378`). The level parameterization (1) is acceptable
only as a cross-check; it is more prone to a floor-binding artifact in thin sub-cells.

**Parameter count.**

| Spec | free parameters |
|---|---|
| Certified baseline (`joint_pooled_v1_bll0_tlmpin`) | **47** (49 nominal − `beta_ll`=0 − `theta_l_m` pinned) |
| Primary S-occ: 4 σ_k replace 1 σ | 47 − 1 + 4 = **50** (+3) |

**Distinct, more-saturated future extension (NOT the primary alternative):** gender × occupation
dispersion — eight σ replacing one common σ, **+7** free parameters (54 total). This must **not** be
inferred from the gender-specific `beta_occ_*`: the access block being gender-segmented says nothing about
whether *dispersion* needs a gender split. It is reported here only as a future option and, per §7c, is
descriptively thinner (singles-male Intel n = 104). It corresponds to the deferred "W2" in
`…JMP_next_cycle_opportunity_respecification_plan_v1.md:220-236`.

---

## 6. Existing implementation-support audit (Task 3)

**Conclusion: the primary S-occ model is not supported by the certified JAX estimation path, and the two
nearest existing wage specs neither match the S-occ mathematics nor run under JAX.** A source-code change
is required. It is *not* config-only.

| Existing path | Exact model | Matches S-occ? | Singles | Couples | JAX estimation | Tests / certified | Fail-closed? |
|---|---|---|---|---|---|---|---|
| `vw` (certified) | common mean, **one** σ (`engine_jax`/`jax_ll_probe`; NumPy `:654,:1626`) | No (no σ_k) | yes | yes | **yes (certified)** | yes — this is the baseline | n/a |
| `loc_empirical` | per-occupation **intercept** μ_g = intercept_g + common_shift **and** per-occupation σ_g (NumPy `estimation_engine.py:666-744` singles, `:1633-1700` couples) | **No** — also varies the *mean* by occupation (extra intercepts); S-occ keeps the common Mincer mean | yes (NumPy) | yes (NumPy) | **no** — no JAX branch | no certified reproduction | **Crashes under JAX**: `wage_variance_param` stays `None` for `loc_empirical` (`parser:599-606`) → `sigma_name=None` → `pidx[None]` KeyError. Fail-closed. |
| `vw_occupation` | occupation × **gender** Mincer (intercept/exp/exp²/educ/**variance**), `_sm`/`_sf` only (`parser:1565-1575`) | No — occupation-specific *means*, gender-coupled, **singles-only** param construction | partial (legacy) | **no** (no `_m`/`_f` couples params) | **no** | no | **Mixed/unsafe**: the NumPy main engine raises `ValueError("Unknown wage_spec")` (`estimation_engine.py:353-360`) → fail-closed there; but the certified **JAX builder does not branch on `wage_spec` at all** (`jax_ll_probe.py:172-184`), so a `vw_occupation` spec fed to JAX would read only `wage_mean_shifters` + one `sigma`, **silently ignoring** the occupation params (orphaned, zero-gradient) → **silent wrong formula**. |
| `occupation_specific_log_normal` (`wage_form`) | sets `occupation_specific_wages=True` flag (`parser:596`); realized only via the legacy occupation-choice utilities | No | legacy only | legacy only | no | no | flag only |
| Legacy occupation-choice (`occupation_choice_utils.py`) | occupation in **utility** (preferences) + occupation-specific Mincer + availability MNL (`occupation_choice_utils.py:1-21,32-67`) | **No** — different parameter meaning (occupation as a *choice/taste*, not residual dispersion) | yes | partial | no | no | separate path; not invoked by certified spec |

**Package-native (dcl monorepo).** Same picture: `engine_jax.py` reads one `sigma = P(sigma_name)`
(`packages/dclaborsupply/.../likelihood/engine_jax.py:184,194,256,389,469`); `known_limitations.md:17-29`
states plainly that `loc_empirical` and `vw_occupation` are "parser-recognized but the JAX engine has no
dedicated implementation … remain unproven and out of scope." The package-native loader
(`data/loader.py`) requires a `wage` column whenever `wage_spec != "fw"`
(`dclaborsupply-monorepo/docs/engine_ready_contract.md:65`) but has **no** σ_k contract.

**Critical correctness flag.** The certified JAX builders (`jax_ll_probe.py:172-184`, and the lifted
`engine_jax.py`) do **not validate `wage_spec`**; they unconditionally compute the common-σ `vw` density.
Therefore a future S-occ spec must add an explicit, **fail-closed** branch — a four-σ spec must either be
fully implemented or rejected, never silently collapsed to one σ.

**Minimal expected change (do not implement here).**

1. **Parser/parameter-construction:** a new wage path (e.g. `wage_spec: "vw_occ_sigma"` or a
   `wage_opportunity.variance.by_occupation` block) that emits the common five mean coefficients **plus**
   the anchored log-ratio dispersion parameters (§5: σ_1 = existing `sigma`; three `delta_log_sigma_k`),
   with the loc4 exclusion restriction preserved and the occupation-access block untouched.
2. **JAX singles + couples wage block:** select σ by the alternative's `loc4` — build a per-alternative σ
   from {σ_1, σ_1·exp(δ_2), σ_1·exp(δ_3), σ_1·exp(δ_4)} keyed on loc4 (singles `jax_ll_probe.py:242-245`;
   couples `:446-449`, per leg via `loc4_male`/`loc4_female`), with the worker gate and `− log_wage`
   Jacobian unchanged.
3. **Unknown-loc4 contract (REQUIRED, not "drop consistently").** 128 chosen workers carry loc4 ∈ {−2,−1}
   (working but occupation unknown/non-worker stub; §7a). Under common-σ they currently contribute a wage
   density at the single σ. A four-σ branch has **no σ for "unknown occupation"**, so their treatment must
   be **explicitly defined and pre-registered**, because each option changes the likelihood: (a) assign them
   σ_1 (the certified anchor) — closest to current behaviour, near-zero negLL change; (b) add a fifth
   "unknown" σ_0 (then 51 free parameters, contradicting the 50-parameter binding gate); or (c) drop their
   wage-density term — which **removes** 128 log-density contributions and therefore **breaks the certified
   negLL regression gate**. They cannot be "dropped consistently" without altering the estimand. Recommended:
   **(a)**, documented in the spec and the engine-ready contract. This must be settled before estimation.
4. **Parameter binding / bounds / initial values:** σ_1 keeps the certified bound `[0.1, 20.0]`; three
   `delta_log_sigma_k` bounded (e.g. `[−2, 2]`), init 0 (≡ common σ).
5. **Fail-closed guard:** the builders must reject any wage_spec they do not explicitly implement (closes
   the silent-`vw_occupation` / crash-`loc_empirical` hazards in §6).
6. **Regression gates:** the full gate suite in §10, with the hard oracle that the certified common-σ
   negLL **238504.6360973987** reproduces to ≤ 1e-4 under the nested restriction (exact with the anchored
   parameterization since σ_1 is the unchanged certified `sigma`).

This is **not config-only**: the certified JAX objective, the parser parameter construction, and the
loader/contract all require code. Per `…roadmap_v1.md:95`, the natural home is the dcl package, not the
research MNL engine.

---

## 7. Identification-support tables (Task 4)

Population: certified engine-ready stems
`C:\Users\hisham\MNL\EUROMOD-STORAGE\new_data\fr_p3a_bpool_engine_ready__{singles,couples}.parquet`
(singles 101 alts, couples 901 alts). **Chosen/observed alternative = `is_chosen == 1`** (cluster =
`cluster_id`=`idorighh`; year_tag 1=2015, 2=2016, 3=2017). Residuals computed as log w − μ̂_i with the
certified θ̂ Mincer mean (§2). Read-only; nothing written.

**Selection note (v1 correction).** The chosen alternative is `is_chosen == 1`, **not** `draw_joint == 0`.
For couples each group has **two** `draw_joint == 0` rows (the observed row plus the first simulated product
draw, which is a valid working alternative with a drawn loc4/wage); only one carries `is_chosen == 1`.
Selecting on `draw_joint == 0` double-counts couples chosen workers. Singles are unaffected (`draw == 0`
coincides with `is_chosen == 1`, 5,007 = 5,007). All couples figures below use `is_chosen == 1`.

### 7a. Observed/chosen workers (the descriptive support for σ_k)

Gate applied to chosen rows: `is_chosen == 1`, `working == 1`, finite positive wage, loc4 ∈ {1,2,3,4}.

**Pooled by occupation — the primary (no-gender-split) S-occ support:**

| loc4 | chosen workers | distinct HH | wage mean | **resid SD** |
|---|---|---|---|---|
| 1 (RM) | 5,219 | 3,586 | 13.62 | 0.3719 |
| 2 (NRM) | 2,705 | 2,055 | 12.55 | **0.4426** |
| 3 (Intel) | 1,800 | 1,371 | 14.45 | **0.3270** |
| 4 (NonInt) | 9,162 | 5,393 | 18.95 | 0.3823 |
| **all** | **18,886** | — | — | 0.3930 (σ̂ = 0.3898) |

The residual SD is **highest in NRM (0.443)** and **lowest in Intel (0.327)** — a real spread
(ratio ≈ **1.35**) that a common-σ model cannot represent. The spread is the single most decision-relevant
fact for σ_k, and it is **sharper** after the chosen-row correction (the inflated draw_joint==0 sample
masked it).

**By population × occupation (counts / residual SD):**

| population | loc4=1 n / SD | loc4=2 n / SD | loc4=3 n / SD | loc4=4 n / SD |
|---|---|---|---|---|
| couples_male | 2,626 / 0.3464 | 560 / 0.3733 | 285 / 0.2993 | 3,663 / 0.3856 |
| couples_female | 1,226 / 0.4012 | 1,461 / 0.4514 | 1,069 / 0.3292 | 3,385 / 0.3570 |
| singles_female | 529 / 0.3691 | 489 / 0.4696 | 342 / 0.3011 | 1,203 / 0.3557 |
| singles_male | 838 / 0.3666 | 195 / 0.4424 | 104 / 0.4052 | 911 / 0.4156 |
| **all** | **5,219** | **2,705** | **1,800** | **9,162** |

Wage distribution detail (chosen workers, €/h, median/p10/p90): couples_male loc4=1 13.5/9.3/19.7,
loc4=4 18.4/12.0/31.6; couples_female loc4=2 11.5/6.8/15.6, loc4=3 13.5/9.6/18.8; singles loc4=4 17.1/10.9/27.8.
By year (singles, pooled over loc4): resid SD 2015 0.397, 2016 0.419, 2017 0.370 — stable across years.

**Data-quality counts among chosen workers:** non-positive/NaN wage = **0** in every population.
Missing/unknown loc4 (loc4 = −2/−1 among chosen *working* rows, excluded above): singles 21, couples-male
94, couples-female 13 (**total 128**). Small relative to the cells, but their σ-assignment under a four-σ
spec is a required contract decision (§6 item 3), not a silent drop.

### 7b. All working engine-ready alternatives (likelihood support, not independent observations)

| population | groups | total working alts | groups w/ occ variation (≥2 loc4) | per-occ presence (share of groups) | within-occ wage variation |
|---|---|---|---|---|---|
| singles_male | 2,243 | 203,749 | 2,243 (100%) | loc4 1/2/3/4 = 1.00/0.999/0.984/1.00 | ≥2 wages in 92–100% of containing groups |
| singles_female | 2,764 | 251,063 | 2,764 (100%) | 0.981/1.00/1.00/1.00 | high |
| couples_male | 7,438 | 6,032,968 | 7,431 (99.9%) | 0.976/0.898/0.752/0.999 | loc4=3 in 3,040/5,597 groups; others higher |
| couples_female | 7,438 | 6,027,854 | 7,432 (99.9%) | 0.804/0.948/0.979/0.989 | high |

Every choice set spans ≥2 occupations among its working alternatives (≈100%), every occupation appears in
**75–100%** of choice groups (rarest: couples-male Intel, 75.2%), and within-occupation wage variation is
present in the large majority of containing groups. The likelihood therefore has ample support to evaluate
four occupation-conditional densities. **Caveat:** these simulated alternatives are importance-sampling
draws, **not** independent wage observations; they supply likelihood support and proposal coverage, but the
actual information for σ_k comes from the chosen workers' residuals (§7a) evaluated against the
occupation-conditional density over this support.

### 7c. Thin-cell assessment (pre-registered diagnostic flags, not identification proofs)

Flags: <100 chosen workers = severe; 100–299 = moderate; <30 distinct HH in any year-specific cell =
severe; insufficient within-set occupation/wage variation = structural.

- **Primary four-σ spec (pooled by occupation):** **no flags.** Smallest cell = Intel, **1,800 workers /
  1,371 HH** (chosen-row corrected). Within-set variation ample (§7b). Support is clearly adequate.
- **Gender × occupation (eight-σ extension):** the σ_{gender,k} cells pool singles + couples of that
  gender; smallest = **male-Intel ≈ 389** (singles-male 104 + couples-male 285) — moderate. The
  singles-only sub-cell (male-Intel **104**) is near-severe, and the fine loc4 × sex × year grid (singles)
  has minimum cell **31** (six cells < 100, **zero < 30**). So the eight-σ split is workable at the
  gender×occupation level but thins quickly under any further (household-type / year) interaction. **Defer
  the eight-σ extension** as the more-saturated future option (the deferred "W2",
  `…JMP_next_cycle_opportunity_respecification_plan_v1.md:220-236`).

**Explicit scope of this task.** This is a support/readiness diagnostic only. It **cannot** prove
recoverability or fitted-Hessian identification. Distinct accepted-wage residual SDs are *suggestive*, not
dispositive: they are accepted-wage (selection-affected) residuals, the spread is modest, and the full
structural model has many compensating channels (§8). Actual identification requires the synthetic-recovery
plus real-data Hessian and stability gates in §11. **No estimation was performed.**

---

## 8. Decomposition-impact reasoning (Task 5)

**The mechanism (stated as a mechanism, not as an empirical claim).**

- The common-σ baseline imposes **equal conditional residual wage dispersion across all four occupations**
  after the shared Mincer mean. If true residual dispersion differs by occupation (the §7a residuals show a
  non-trivial accepted-wage difference — SD ratio ≈ 1.35 — but do not prove it structurally), the
  likelihood is **misspecified along the wage-density channel**.
- Under such misspecification, estimation has no single "error-variance" sink to absorb the mismatch.
  There is **no estimated preference residual variance**: the choice-error scale is the *fixed* unit
  extreme-value scale, not a free parameter. Compensation must instead flow through the parameters that
  *are* free — the common σ (a population-average compromise), the shared Mincer coefficients
  (β_w0…β_wpexp2), the occupation-access mass (`beta_occ_*`), the hours/market access parameters, and the
  deterministic preference coefficients (leisure/curvature). None of these is a clean variance sponge; each
  distortion is a genuine parameter shift.
- `beta_occ_*` are **access** parameters, not wage-mean shifts (§3). A wage-density misspecification can
  nonetheless leak into them, because both the access term and the wage term enter the same composite V
  over the same choice sets — a further reason the access/ability split is the quantity at risk.
- In the planned decomposition, the wage-technology block — including residual dispersion — is assigned to
  the **broad ability** component
  (`JMP_ability_opportunity_cut_v1.md:47-58,126,130`; roadmap equalization scheme `…roadmap_v1.md:81`).
  σ specifically "travels with the broad ability block … but must be reported with a caveat" that residual
  dispersion may also contain **unobserved access, matching frictions, or noise**
  (`JMP_ability_opportunity_cut_v1.md:53,58,130`). Therefore imposing a single σ can alter the **measured
  ability/access/preference split**: the ability component's size depends on how residual productivity
  dispersion is modelled, and forcing it equal across occupations changes that input.
- **But σ_k is not automatically "pure ability."** Occupation-specific dispersion can reflect unobserved
  productivity, unobserved access, matching frictions, measurement error, or noise. A four-σ model that
  improves fit does not, by itself, license attributing the extra dispersion structure to ability; the
  same residual-heterogeneity caveat that applies to σ applies to each σ_k.
- This is a **specification-sensitivity** mechanism, **not** evidence that the certified results are
  biased. The certified baseline stands; S-occ is a robustness/sensitivity arm whose materiality is an
  empirical question for the gates, not a foregone conclusion.

### Conference-ready caveat

> *The certified baseline restricts residual wage dispersion to a single parameter σ common to all four
> occupation classes, after a shared Mincer wage equation; occupation enters the model only as a separate
> job-offer-availability (access) channel, never as a wage parameter. Because residual wage dispersion is
> assigned to the broad ability component of our opportunity decomposition, holding it equal across
> occupations can move the measured ability-versus-access split if true dispersion in fact differs by
> occupation. Occupation-specific dispersion has not yet been estimated; our accepted-wage residuals differ
> across the four classes (residual-SD ratio ≈ 1.35), but we claim no direction or magnitude for any effect
> on the decomposition — that is reserved for a separately gated four-density specification.*

---

## 9. Verdict (Task 6)

**Verdict A — a parallel, gated S-occ specification is warranted.** Both of Verdict A's preconditions are
met from verified Tasks 1–5:

1. **Descriptive support is adequate** for the primary four-σ (no-gender-split) alternative: **1,800–9,162
   chosen workers and 1,371–5,393 distinct households** per occupation (chosen-row corrected), no thin-cell
   flags, near-universal within-choice-set occupation and within-occupation wage variation (§7a–c), and a
   real cross-occupation residual-SD spread (**0.327–0.443 vs σ̂ 0.390, ratio ≈ 1.35**; §7a).
2. **The implementation gap is tractable** though non-trivial: a localized fail-closed σ_k branch in the
   JAX singles/couples wage block plus parser parameter construction and an explicit unknown-loc4 contract
   (§6). It is not config-only, and the nearest existing specs (`loc_empirical`, `vw_occupation`) neither
   match the S-occ math nor run under JAX.

This is explicitly **not** Verdict C (common σ is *not* obviously cost-justified to retain: support is
abundant and the dispersion spread is real, and the project has already pre-committed to taking occupation
seriously in the wage block — `JMP_conditional_wage_on_occupation_decision_note_v1.md:48-69`). It is also
not Verdict B (the *primary* spec is **not** thin; thinness applies only to the deferred eight-σ extension).
The Verdict-D reservation — that a read-only diagnostic cannot choose common-σ vs S-occ — is **accepted and
incorporated**: Verdict A here warrants *building and gating* the parallel spec, and the actual choice
between common σ and S-occ is deferred to the recovery, Hessian, and decomposition-sensitivity gates (§10).
No four-density estimation is authorized by this memo; the parallel specification is scheduled after the
conference (`…roadmap_v1.md:93-97`).

**What the future estimation harness must change (Verdict A → §6 minimal change, restated as a checklist):**

- **configuration:** new wage path with the **anchored log-ratio** dispersion (σ_1 = existing `sigma`;
  three `delta_log_sigma_k`); occupation-access block and Mincer mean unchanged.
- **parser:** emit the three ratio parameters (σ_1 reuses the certified `sigma`); preserve the loc4
  exclusion restriction; no silent drops.
- **package-native loader:** σ_k requires no new data column (loc4 + wage already present), but the
  engine-ready contract should document the σ_k dependence on `loc4` **and** the unknown-loc4 σ-assignment.
- **JAX singles likelihood:** select σ by the alternative's `loc4`.
- **JAX couples likelihood:** select σ per leg by `loc4_male` / `loc4_female`.
- **unknown-loc4 contract:** explicit σ-assignment for loc4 ∈ {−2,−1} (recommended: σ_1; §6 item 3).
- **parameter binding / bounds / initial values:** σ_1 keeps `[0.1,20.0]`; three `delta_log_sigma_k`
  bounded, init 0 (≡ common σ).
- **optimizer:** unchanged (L-BFGS-B / certified JAX optimizer); expect **50** free parameters.
- **recovery and regression gates:** the full suite in §10, including the certified-negLL oracle.

---

## 10. Required future gates (define, do not run) (Task 7)

1. **Parser/binding gate** — exactly **50** free parameters (σ_1 = reused certified `sigma` + three
   `delta_log_sigma_k`); all bind and appear in `all_param_names`; the unknown-loc4 σ-assignment is the
   declared one (no extra silent parameter); no silent drops; fail-closed on any unimplemented wage_spec.
2. **Synthetic recovery gate** — simulate with **known** occupation-specific σ_k and adequate support in
   every occupation; recover all σ_k within a pre-registered SE band; exact-JAX Hessian positive definite
   (apply the gender-split lesson: LR/descriptive separation ≠ recoverability —
   `project_gsplit_not_synthetic_identified`).
3. **Nested-model sanity gate** — δ_log_σ_2 = δ_log_σ_3 = δ_log_σ_4 = 0 gives σ_k = σ_1 **identically** and
   reproduces the common-σ likelihood **bit-for-bit** (the anchored parameterization makes this exact, with
   no `exp(log(·))` round-trip).
4. **Certified-baseline regression gate** — the existing certified common-σ spec is unchanged and its
   negLL reproduces **238504.6360973987 to ≤ 1e-4** (exact under the anchored parameterization, since σ_1
   is the unchanged certified `sigma` and the deltas are 0).
5. **Real-data parallel-estimation gate** — convergence + KKT diagnostics; no unexplained bound activity
   (esp. σ_k floors); Hessian/SE diagnostics; parameter stability; likelihood comparison vs baseline
   interpreted with the correct **three** added degrees of freedom (LR / AIC / BIC).
6. **Decomposition-sensitivity gate** — compare the ability/access/preference decomposition under common-σ
   vs S-occ **only after both** specifications pass their estimation **and** welfare gates; report
   sensitivity (the bracket shift), **not** automatic superiority of S-occ.

---

## 11. Explicit uncertainties

- **Descriptive ≠ identified.** The §7a residual spread (0.327–0.443, ratio ≈ 1.35) is suggestive; it does
  not establish that a structural four-σ model will recover four *distinct* σ_k or that the Hessian will be
  PD. Gate 2/5 decide this, not this memo.
- **Selection.** §7a residuals are **accepted-wage** residuals; selection into work (and into occupation)
  can compress or shift the conditional dispersions, so the descriptive σ_k pattern is not the pure offer
  dispersion (`JMP_conditional_wage_on_occupation_decision_note_v1.md:135-144`).
- **Materiality unknown.** Even if σ_k are distinguishable, whether they materially move the
  ability/access bracket is unknown until gate 6.
- **loc4 missingness is a contract item, not a footnote.** 128 chosen working rows carry loc4 ∈ {−2,−1}
  (singles 21, couples-male 94, couples-female 13). Under a four-σ spec these have **no** occupation σ;
  their σ-assignment must be **explicitly pre-registered** (§6 item 3) because dropping their wage-density
  term would change negLL and break the regression gate. They cannot merely be "dropped consistently."
- **Couples leg dependence.** Within a couple, the two legs share a household cluster; σ_k SEs must use the
  clustered sandwich (chunked — naive `jacrev` OOMs, per `project_step4_realdata_baseline`).
- **Engine choice.** The certified MNL JAX path vs the dcl package path differ in `fw` handling; the
  S-occ change should land in **one** chosen engine (roadmap favors dcl, `…roadmap_v1.md:95`) with the
  other left unchanged or kept in lockstep.
- **Proposal/structural asymmetry.** The W1 proposal already conditions the wage *mean* on occupation
  (`delta_occ`) while the structural mean does not; this is a separate (mean-channel) respecification
  question (`…JMP_next_cycle_opportunity_respecification_plan_v1.md:193-216`) and should not be conflated
  with the S-occ *variance* question.
- **Mischaracterization to correct.** `RURO_postestimation_descriptives_v1.md:106-115` (and its
  `loc4_wage_densities` figure) describe `beta_occ_*` as wage-mean shifts; recorded in §3, not yet corrected.

---

## 12. REQUIRED NEXT INPUT

Conditional on **Verdict A**, a future parallel-estimation prompt must supply / confirm:

1. **Authorization** to make a source-code change to the chosen estimation engine (MNL JAX *or* dcl
   package — **specify which**) and to add a new wage specification; this memo authorizes **no** code change.
2. **Engine target** decision: research `scripts/bpool` JAX path, or the dcl package
   (`packages/dclaborsupply`) — the roadmap (S2) favors dcl.
3. **Parameterization** confirmation: **anchored log-ratios** (recommended: σ_1 = existing certified
   `sigma`; three `delta_log_sigma_k`) vs four σ_k levels; the bounds and initial values for the deltas.
4. **Unknown-loc4 σ-contract** (loc4 ∈ {−2,−1}, 128 chosen workers): which σ they take (recommended: σ_1),
   pre-registered so the binding and regression gates are well-defined (§6 item 3, §11).
5. **Spec artifact**: a new YAML deriving from `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` with the
   anchored four-σ wage block and the access/mean blocks unchanged (target **50** free parameters).
6. **Gate thresholds**: the pre-registered SE recovery band for gate 2, and confirmation that the
   certified negLL oracle 238504.6360973987 (≤1e-4) is the regression target for gate 4.
7. **Synthetic-recovery data plan**: how σ_k truth values are set and how occupation support is guaranteed
   in the synthetic draws (loc4 draw + W1 proposal coverage).
8. **Scope confirmation**: primary four-σ only (no gender split); the eight-σ gender×occupation extension
   remains deferred (§7c).
9. **Decision rule** for gate 6: what bracket movement counts as "materially changes the decomposition,"
   pre-registered before estimation.

If instead the decision is to record **Verdict C/D** at review time, the next input is only the
documentation correction in §3 plus a note that the common-σ baseline stands; no estimation harness change
is then scheduled.

---

## Scope statements

- **No estimation performed.** (Descriptive `pandas`/`pyarrow` reductions only.)
- **No identification claim beyond descriptive support.**
- **No decomposition recomputed.**
- **No engine, builder, parser, spec, or data edited.**
- **No scripts or scratch artifacts created.** (Read-only inline inspection; nothing written but this memo.)
- **No commit made.**

*Verdict: A — parallel, gated four-density (S-occ) specification warranted; building/gating authorized only
by a future prompt per §12; identification deferred to the §10 gates; eight-σ gender×occupation extension
deferred for thin cells.*
