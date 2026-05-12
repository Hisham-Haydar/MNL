I have enough material. Let me construct the contract.

---

# RURO Model-Specification Contract v1

**Purpose.** This is a contract for code auditing, not paper prose. It defines the target RURO model that the France 2016 implementation should match. Claude Code uses this contract to audit `estimation_engine.py`, `gamspy_estimation_vectorized.py`, `gamspy_estimation.py`, `enh_RURO_prep_mnl_basic.py`, `estimation_spec_parser.py`, and the associated YAML specs.

**Save as:** `RURO_model_spec_contract_v1.md`.

---

## 1. Target model class

A Random Utility Random Opportunity (RURO) discrete-choice labor-supply model in the Aaberge–Colombino / Dagsvik tradition, in the Stijn / Jacquet–Jia–Thoresen variant. The choice probability over a sampled set of latent job alternatives takes a multinomial-logit form derived from extreme-value errors, where the systematic part of the choice index is the sum of a preference utility, additive log-opportunity densities (employment, hours, wage, and — if implemented — occupation), and a proposal-density correction.

The choice index for household `h` and alternative `j` is:

```
V_hj = U_hj + O_hj^E + O_hj^H + O_hj^W + O_hj^Occ + O_hj^M - log q_hj
```

where every term on the right corresponds to a distinct economic object defined below. The unconditional choice probability is the McFadden conditional logit applied to `V_hj` summed over the sampled choice set.

The model is empirical and structural. It is not the separate axiomatic theory paper.

---

## 2. Choice unit

The choice unit is the **household**, not the individual.

- Singles sample: a single working-age head (`ruro_decider = 1`). Singles male (`sm`) and singles female (`sf`) are treated as distinct groups with separate preference parameters.
- Couples sample: an opposite-sex couple where both head and partner are `ruro_decider = 1`. The choice is a joint bundle of head and partner job packages. Male partners (`cm`) and female partners (`cf`) carry partner-specific opportunity and leisure parameters.

In couples, household consumption is shared and enters a single household-level consumption term; leisure is partner-specific.

Sample inclusion rules (fixed for the baseline):
- Age 16–65, full-time students excluded.
- One canonical household type: opposite-sex couple with at most one partner; households with additional eligible non-head, non-partner members are dropped.
- Abnormal employee hours / wages filtered upstream.

---

## 3. Alternatives / job packages

The choice set per household is a finite set of **sampled** alternatives.

For singles, an alternative is one of:
- A non-employment state (`h = 0`, `w = 0`).
- A working **job package**: a discrete bundle defined at the basic `job` level as `(hours_bin, wage_bin, isco1, type_id)`, where `hours_bin` is a 4-hour interval and `wage_bin` is a wage vigintile.

For couples, an alternative is a joint pair of head and partner job packages.

Alternatives are drawn from an empirical proposal distribution `q`. The number of alternatives per household must equal the value the prep stage promises (currently: 200 alternatives in the job-choice branch, 100 in the continuous branch). Exactly one alternative per household is marked as observed (`chosen = 1`).

The contract requires:
- `chosen` sums to exactly 1 within each household.
- `working = 1{h > 0}` is consistent with `h`.
- For the working alternative the partner is real; for non-employment the wage is structurally 0 and contributes no wage-density term.

---

## 4. Preference component

Preferences enter `U_hj` as a Box-Cox utility over normalized consumption `C` and normalized leisure `L`. Consumption and leisure must be normalized using the scaling stored in the MNL sidecar; the audit must check that the same scaling is applied at estimation, simulation, and welfare time.

### Singles (group `g ∈ {sm, sf}`)

```
U_g(C, L; Z) =
    β_c_g · BC(C, θ_c_g)
  + β_l_g(Z) · BC(L, θ_l_g)
  + β_cl_g · BC(C, θ_c_g) · BC(L, θ_l_g)        [optional, off by default]
```

with `BC(x, θ) = (x^θ − 1) / θ` if `θ ≠ 0` and `log(x)` if `θ = 0`, and

```
β_l_g(Z) = β_l0_g
         + β_l_age_g · age_norm
         + β_l_age2_g · age_norm2
         + β_l_nkids_g · n_children     [female only in the baseline]
         + β_l_educH_g · educH
```

### Couples

```
U_couple(C, L_m, L_f; Z_m, Z_f) =
    β_c · BC(C, θ_c)                    [shared household consumption]
  + β_l_m(Z_m) · BC(L_m, θ_l_m)
  + β_l_f(Z_f) · BC(L_f, θ_l_f)
  + β_ll · BC(L_m, θ_l_m) · BC(L_f, θ_l_f)   [optional leisure–leisure interaction]
```

Preference shifters are restricted to: `age_norm`, `age_norm2`, `n_children`, `educH`. Anything else entering `U_hj` is a contract violation unless explicitly added later.

---

## 5. Labor-time opportunity component

The hours opportunity density is the conditional probability density of offered hours given working. On the log scale it adds to `V_hj`. It is **independent of wage** at the first step (Aaberge–Colombino independence assumption), and may depend on observable circumstances.

Baseline structure (per individual, then summed across spouses for couples):

```
O^H_hj = β_work · 1{h_j > 0}
       + β_pt1  · 1{h_j ∈ PT1}
       + β_pt2  · 1{h_j ∈ PT2}
       + β_ft   · 1{h_j ∈ FT}
       + β_gsur · gsur · 1{h_j > 0}
       + β_work_educH · educH · 1{h_j > 0}
```

with focal-point bins fixed at:
- PT1: `h ∈ [18.5, 21.5]` (20-hour peak)
- PT2: `h ∈ [29.5, 30.5]` (30-hour peak)
- FT:  `h ∈ [37.5, 40.5]` (40-hour peak)

For couples, `O^H_hj = O^H_hj,m + O^H_hj,f` with partner-specific covariates.

For non-employment alternatives all hours-opportunity shifters except possibly a constant must vanish — i.e. `O^H = 0` if `h = 0`. The audit must verify this gating.

`gsur` is a labor-demand / unemployment shifter that is **opportunity-only** by exclusion restriction. It must not enter `U_hj`.

---

## 6. Wage opportunity component

The wage opportunity density is log-normal in offered hourly wages, with a Mincer-style mean and a single residual variance.

For each working alternative:

```
log f_W(w | X) = − 0.5 · z² − log σ − log w
z = (log w − μ(X)) / σ
μ(X) = β_w0 + β_w_educL · educL + β_w_educH · educH + β_w_pexp · pexp + β_w_pexp2 · pexp²
σ > 0
```

For non-employment alternatives the wage-density term is set to 0 (no contribution).

For couples, `O^W_hj = O^W_hj,m + O^W_hj,f` using partner-specific wage variables and the partner-specific working indicator.

Identification convention:
- The Mincer mean shifters (`educL`, `educH`, `pexp`, `pexp²`) are **opportunity-only**. They must not appear in `U_hj` at the first step.
- The constant `− log w` term arises from the change of variables for a log-normal in levels; the audit must verify it is implemented when the model is specified on `w` (not on `log w`).
- The audit must verify that exact specification reuses the same scaling and column conventions used in `enh_RURO_prep_mnl_basic.py`.

---

## 7. Occupation or sector opportunity component

The project files state that the final MNL files **do not currently expose a NACE/industry variable**. They expose `isco1`, `loc`, `loc4`, `type_id`, and `job_id`. The first baseline therefore implements an **occupation opportunity** layer, not a sector opportunity layer.

Baseline occupation opportunity:

```
O^Occ_hj = Σ_k β_occ_k · 1{isco1_j = k} · 1{h_j > 0}
```

with one reference category omitted (suggested: `isco1 = 1` or whichever the spec parser sets as reference).

For couples, partner-specific occupation effects:

```
O^Occ_hj = O^Occ_hj,m + O^Occ_hj,f
```

Naming and language requirements:
- This layer must be **labelled occupation opportunity**, not sector opportunity, in code comments, YAML descriptions, and post-estimation reports.
- A separate `sector_opportunity` YAML block must not be introduced unless and until a true NACE / industry variable is carried through the pipeline.
- Occupation shifters enter opportunity **only**, not utility, at the first step.

A finer alternative using `loc4` (routine/non-routine × manual/cognitive) is permitted as a robustness extension but is not part of the baseline.

---

## 8. Market / non-market opportunity component

The market opportunity component is the log-odds that any market alternative (`working = 1`) is available, relative to the non-market alternative (`h = 0`, `w = 0`). It is the RURO analogue of `log(p_1k / p_0k)` in Aaberge–Colombino.

Baseline:

```
O^M_hj = β_offer_working · 1{h_j > 0}
       + Σ_k β_offer_gsur_educ_k · gsur · 1{educ_k} · 1{h_j > 0}
```

Optional centering: the implementation must apply **within-choice-set centering** of `O^M` (and any other within-choice-set components) using proposal weights, matching `market_centering_applied = true` in the current best run. The post-estimation report metadata field `market_centering_applied` must be `true`.

For couples, the market-opportunity term is partner-specific and additive across spouses.

---

## 9. Proposal / prior correction

Alternatives are sampled from a proposal distribution `q`. The McFadden sampling correction subtracts `log q` from each alternative's choice index:

```
V_hj = U_hj + O^H_hj + O^W_hj + O^Occ_hj + O^M_hj − log q_hj
```

Canonical convention (must hold in every MNL file written by `enh_RURO_prep_mnl_basic.py`):

```
prior        = proposal density / probability on the original scale, strictly positive
log_prior    = log(prior)
likelihood   correction subtracts log_prior (equivalently, log(prior))
```

For job-draw files the proposal factorizes as:

```
log_q_total = log_q_state + log_q_job
prior       = exp(log_q_total)
log_prior   = log_q_total
```

For couples job-draw files:

```
log_q_total = log_q_total_male + log_q_total_female
```

For the continuous fallback path (singles and couples), the contract requires:

```python
df["prior"]     = prior_density        # original scale, strictly positive
df["log_prior"] = np.log(prior_density)
```

The existing fallback that sets `df["prior"] = np.log(prior_density)` is a contract violation and must be patched.

The post-estimation report must record `prior_correction_applied = true` and `prior_correction_form = "-log(prior)"`.

---

## 10. Likelihood contribution

The conditional log-likelihood per household is:

```
ℓ_h = V_h,chosen − log Σ_{j ∈ S_h} exp(V_hj)
```

where `S_h` is the sampled choice set for household `h`. The joint log-likelihood is `Σ_h ℓ_h`. For singles + couples joint estimation, both groups contribute to the same objective with group-specific parameters where the spec is gender-specific.

The estimator maximizes the joint log-likelihood with L-BFGS-B (NumPy/SciPy path) or CONOPT / IPOPT / KNITRO (GAMSPy path) using analytical or autodiff gradients. The vectorized GAMSPy Box-Cox uses a fourth-order Taylor expansion around `θ = 0`; the audit must verify agreement with the exact NumPy implementation at the estimated `θ` values, particularly when `|θ| > 1`.

Numerical safeguards:
- Clip `C` and `L` strictly above zero before applying `BC`.
- Compute `log Σ exp` with a row-wise max-stabilization.
- Enforce `σ > 0` in the wage density.

---

## 11. Normalizations required for identification

The following normalizations are required for the model to be identified:

1. **Scale.** The MNL likelihood has the usual unit-scale normalization for the Gumbel error; no Gumbel-scale parameter is estimated.
2. **Reference categories.** Education uses `educM` as the omitted category; `educL` and `educH` are dummies. Occupation uses one reference `isco1` category, omitted from `O^Occ`.
3. **Proposal correction.** Exactly one `−log q` term per alternative, with no double-subtraction. The audit must verify there is no second subtraction of `log_prior` anywhere downstream of `enh_RURO_prep_mnl_basic.py`.
4. **Constants in opportunity densities.** A single working constant `β_work` in `O^H`; occupation effects are deviations from the omitted occupation; market-opportunity centering, if applied, must be applied at most once.
5. **Non-labor income** enters preferences (via consumption `C = disposable income`) but **not** the opportunity density, providing one identification anchor between preferences and opportunities.
6. **Gender separation.** Singles male and singles female have separate preference and opportunity parameters; couples male and female partners have separate leisure and opportunity parameters but a single shared `β_c`, `θ_c` for household consumption.

---

## 12. Parameters to estimate

For the **minimum acceptable baseline** (see §18), the parameter list is:

Preference parameters (singles + couples):
- `β_c_sm`, `β_c_sf`, `β_c` (shared in couples), with corresponding `θ_c_sm`, `θ_c_sf`, `θ_c`
- `β_l0_sm`, `β_l0_sf`, `β_l0_m`, `β_l0_f`
- `θ_l_sm`, `θ_l_sf`, `θ_l_m`, `θ_l_f`
- `β_l_age_g`, `β_l_age2_g`, `β_l_educH_g` for `g ∈ {sm, sf, m, f}`
- `β_l_nkids_sf`, `β_l_nkids_f` (female only)

Hours opportunity (per gender):
- `β_work`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_work_educH`

Wage opportunity (per gender):
- `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp2`, `σ`

Occupation opportunity (per gender):
- `β_occ_k` for `isco1 ∈ {2, …, 9}` interacted with `working`

Market opportunity:
- `β_offer_working`, `β_offer_gsur_educM`, `β_offer_gsur_educH`

The total parameter count for the baseline is in the 35–55 range depending on whether hours-opportunity and market-opportunity shifters are gender-specific.

---

## 13. Parameters to fix or bound

Required at the first baseline:

- `θ_l_*` and `θ_c_*` bounded to `[−8.0, 0.95]`.
- `β_l0_*` bounded below at `0.05` to keep the leisure marginal utility positive at the boundary.
- `σ > 0`, with `σ ∈ [0.1, 20.0]`.
- The reference education category (`educM`) and reference occupation category have **no** estimated coefficient.

Disallowed at the first baseline:

- Fixing `θ_c_sm` at a warm-start value (as in the current M2h pruned spec) is permitted only if explicitly documented as a temporary measure; the contract considers `θ_c_sm` an estimable parameter and the audit must flag any spec that hard-fixes it.
- Soft penalty constraints on marginal utility of leisure positivity may be active but must not be tight enough to determine point estimates.

Diagnostics to flag (not fail):

- Any parameter ending the optimization at a bound (relative distance < 1e-3 from the bound).
- Any parameter with an estimated SE that is `NaN` or `> 10 × |estimate|`.

---

## 14. Required data columns

The MNL parquet files consumed by the estimator must expose the following columns per row (one row = one alternative for one household):

Household / sample:
- `idhh`, `decider_id`, group flag (`singles_male` / `singles_female` / `couples`)
- `chosen` (0/1, summing to 1 per household)

Behavioral / budget:
- `h` (hours), `w` (hourly wage), `working = 1{h > 0}`
- `C` (normalized household disposable income), `L` (normalized leisure), and the underlying scaling factors in the MNL sidecar
- For couples: `hours_male`, `hours_female`, `wage_male`, `wage_female`, `working_male`, `working_female`

Preference shifters:
- `age_norm`, `age_norm2` (per spouse for couples)
- `n_children`
- `educL`, `educH` (per spouse for couples)

Opportunity shifters:
- `gsur` (per spouse for couples)
- `pexp` or `pexp_years` (per spouse for couples)
- `isco1`, `loc`, `loc4`, `type_id`, `job_id` (per spouse for couples)

Proposal / prior:
- `prior` (strictly positive)
- `log_prior` (equal to `log(prior)` within tolerance)
- For job-draw files: `log_q_state`, `log_q_job`, `log_q_total` (and `_male` / `_female` versions for couples)

Variables that **must not** be in the column list at the first baseline:
- `nace` / `nace1` / `sector` / `industry` — these do not exist in the final MNL files and must not be referenced by the spec parser.

---

## 15. What must not enter both preferences and opportunities at the first step

To anchor preference / opportunity separation, the first baseline enforces the following exclusion restrictions:

| Variable                       | Allowed in preferences | Allowed in opportunity |
|--------------------------------|------------------------|------------------------|
| `age_norm`, `age_norm2`        | Yes                    | No                     |
| `n_children`                   | Yes                    | No                     |
| `educH` (in leisure utility)   | Yes                    | Yes (separately)       |
| `educL`                        | No                     | Yes (wage, hours)      |
| `pexp`, `pexp²`                | No                     | Yes (wage)             |
| `gsur`                         | No                     | Yes                    |
| `isco1`, `loc`, `loc4`         | No                     | Yes (occupation)       |
| `type_id`, `job_id`            | No                     | Yes (opportunity-only) |
| Non-labor income               | Yes (via `C`)          | No                     |

The audit must flag any specification that puts the same variable in both `utility` and any opportunity block at the first baseline. Adding a variable to both is permitted only as a deliberate later extension with a documented identification justification.

---

## 16. Required diagnostics

Every estimation run must produce and store the following diagnostics in `estimation_results.json` (or its sidecars):

1. Convergence: optimizer status, number of iterations, final gradient norm.
2. Log-likelihood: `joint_ll`, `ll_null_uniform`, `ll_null_prior_corrected`, McFadden ρ², adjusted ρ², AIC, BIC.
3. Hessian: condition number, number of negative eigenvalues, smallest absolute eigenvalue.
4. Standard errors: SE, t, p for every estimated parameter; flag any parameter with non-finite SE.
5. Bound diagnostics: list of parameters within 1e-3 of any bound.
6. Identification flags: list of "poorly identified parameters" (large SE, low curvature).
7. Centering and prior metadata: `prior_correction_applied`, `prior_correction_form`, `market_centering_applied`.
8. Observed-vs-predicted fit: participation rate, mean hours, hours-distribution histogram, wage-distribution density, separately for SM / SF / CM / CF.
9. Occupation distribution: observed vs. predicted ISCO shares.
10. Seed / draw stability: a stability suite that re-estimates the baseline with at least two alternative draw seeds and reports the maximum parameter difference.

Hard gates for any claim of "separately identified preferences and opportunities":

- No negative Hessian eigenvalues.
- Condition number < 1e7.
- All baseline parameters have finite SEs.
- No bound-hits on opportunity coefficients of substantive interest.
- Seed stability max-diff < 5 % for all preference and key opportunity coefficients.
- Simulation recovery test (§17) passes.

---

## 17. Recovery-test requirements

A Stijn-style simulation recovery test is required before any identification claim and before any welfare-decomposition results are reported.

Procedure:

1. Fix a "true" parameter vector `θ⁰` for the baseline spec. Use plausible economic values, not the empirical estimates, to avoid circularity.
2. For each household in the France 2016 sample, generate sampled alternatives from the same proposal distribution `q` used in estimation.
3. Compute the true choice index `V_hj^0` using `θ⁰`, draw i.i.d. Gumbel shocks per alternative, and select the alternative with the maximum `V_hj^0 + ε_hj` as the synthetic "chosen" alternative.
4. Re-run the estimator on the synthetic dataset starting from at least three different starting points (including a perturbation of `θ⁰` and a neutral start).
5. Report: max parameter bias `|θ̂ − θ⁰|`, max relative bias, parameter-wise coverage rate over `R ≥ 50` Monte Carlo replications, and convergence rate.

Pass criteria:

- Mean bias of every preference and opportunity coefficient < 10 % of the true value (or < 0.05 in absolute terms when the true value is near zero).
- 95 % coverage between 0.92 and 0.98 for the main preference coefficients (`β_c`, `θ_c`, `β_l0`, `θ_l`).
- Convergence rate ≥ 90 %.

Until the recovery test passes on the France-shaped dataset, the contract treats the France estimates as **provisional**, not as proof of separate identification.

---

## 18. Minimum acceptable baseline specification

The minimum acceptable baseline is the **pruned job-choice specification** with explicit prior correction and market centering, plus a separately named occupation-opportunity layer derived from `isco1`. Concretely:

- Sample: France 2016, SRCV / EUROMOD-input, singles (1,676 households) and couples (2,577 households); joint estimation across the four gender groups (`sm`, `sf`, `cm`, `cf`).
- Alternatives: 200 per household, from the job-draw proposal `q_state · q_job`.
- Utility: Box-Cox in `C` and `L`, with `age_norm`, `age_norm2`, `n_children` (female only), `educH` as leisure shifters. No consumption–leisure interaction. No leisure–leisure interaction in the first pass.
- Hours opportunity: `β_work`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_work_educH`.
- Wage opportunity: log-normal with `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp2`, `σ`.
- Occupation opportunity: `β_occ_k` for `k = 2, …, 9` interacted with `working`. Reference category `isco1 = 1`.
- Market opportunity: `β_offer_working`, `β_offer_gsur_educM`, `β_offer_gsur_educH`, with within-choice-set centering.
- Prior correction: `−log_prior` with `log_prior = log_q_state + log_q_job` (and the partner-summed version for couples).
- No NACE-based sector layer.
- No sector or occupation variables in `utility`.

This baseline is reportable when (i) it converges with a positive-definite Hessian, (ii) the recovery test in §17 passes, and (iii) the seed-stability diagnostic passes.

---

## 19. Later extensions

The following are explicitly **not** part of the baseline and must not be added before the baseline meets the gates in §16–§18:

1. **True NACE / industry sector opportunity layer** (`O^S`). Requires carrying `nace` or equivalent through `enh_france_data_prep.py`, `enh_RURO_prep.py`, the job-draw scripts, the MNL prep, and the spec parser, plus a factorized proposal `q_e · q_s · q_h|s · q_w|h,s`.
2. Stijn-style **clean factorized opportunity** with separate hours density `g_1` and wage density `g_2`, conditional on occupation or sector.
3. Random coefficients on `β_l0` or `θ_l` (continuous unobserved preference heterogeneity).
4. Consumption–leisure interaction `β_cl` and within-couple leisure–leisure interaction `β_ll`.
5. Multi-year identification using France 2021 in addition to 2016.
6. Cross-country extensions (Germany, others).
7. Welfare layer: household AEI-style money-metric welfare and the two-factor Shapley-Shorrocks decomposition of the household welfare Gini. These are downstream of the baseline and require the recovery test to have passed first.

These extensions remain on the roadmap but are out of scope for the first-pass audit.

---

## Implementation checklist for Claude Code

Concrete checks Claude Code must perform when auditing the implementation against this contract:

1. **Column existence and types.** Verify that every column listed in §14 exists in `fr_2016_RURO_mnl_job_gmm__singles.parquet` and `fr_2016_RURO_mnl_job_gmm__couples.parquet`, with the expected dtypes. Verify that `nace`, `nace1`, `sector`, `industry` are **absent** and that the spec parser does not reference them.

2. **Prior convention.** Assert `(df["prior"] > 0).all()` and `max(abs(np.log(df["prior"]) - df["log_prior"])) < 1e-8` for every MNL file. Specifically inspect `enh_RURO_prep_mnl_basic.py` lines around 1448-1451 (singles continuous fallback) and 1572-1575 (couples continuous fallback) and patch any path that sets `df["prior"] = np.log(prior_density)`.

3. **One chosen per household.** Assert `df.groupby("idhh")["chosen"].sum() == 1` for every household, every file.

4. **No double prior subtraction.** Grep `estimation_engine.py`, `gamspy_estimation.py`, `gamspy_estimation_vectorized.py` for `log_prior` and `log(prior)`; verify the subtraction occurs exactly once per alternative.

5. **Exclusion restrictions.** Parse the active YAML spec (`estimation_spec_job_M2h_pruned.yaml`). For each variable in §15, verify it appears in at most the allowed blocks. Report any violation as a hard fail.

6. **Occupation naming.** Search the YAML, the spec parser, and `RURO_post_estimation_styled.py` for the word "sector". If `isco1` or `loc4` is being described as "sector", rename to "occupation" in YAML descriptions, in HTML report labels, and in code comments. Verify no `sector_opportunity` YAML block exists at the first baseline.

7. **Non-employment gating.** Verify that for every row with `h == 0`: `O^H` reduces to 0 (no focal-point contribution), `O^W` is 0 (no log-normal contribution), and `O^Occ` is 0 (occupation indicators gated by `working`).

8. **Box-Cox consistency.** At the estimated `θ` values from the current best run, compare the vectorized GAMSPy Taylor-approximated `BC` to the exact NumPy `BC` for the observed `(C, L)` grid. Flag any pointwise relative error `> 1e-3`.

9. **Hessian and bounds.** For the latest run, read `estimation_results.json` and assert: `n_negative_eigenvalues == 0`, condition number `< 1e7`, no preference or main opportunity parameter within `1e-3` of a bound. List violations.

10. **Metadata flags.** Assert `prior_correction_applied == true`, `prior_correction_form == "-log(prior)"`, and `market_centering_applied == true` in the run metadata.

11. **Recovery harness.** Verify the existence (and, if absent, scaffold the stub) of a script `scripts/diagnostics/run_recovery_test.py` implementing the procedure in §17. Do not run it as part of the audit; only check that the harness exists and points at the baseline spec.

12. **Audit report.** Emit a single Markdown file `RURO_code_contract_audit_v1.md` listing, per section of this contract (§1–§19), the status `PASS`, `FAIL`, or `N/A`, the file and line numbers checked, and the minimal patch needed for each `FAIL`. Do not apply any patches inside the audit step; patches belong to a separate `RURO_patch_plan_v1.md`.

---

**Save this contract as `RURO_model_spec_contract_v1.md`** in the project root or in `docs/`. Use it as the input to the next Claude Code task, which is the audit step (output: `RURO_code_contract_audit_v1.md`).