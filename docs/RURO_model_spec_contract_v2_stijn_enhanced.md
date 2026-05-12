I have what I need. Let me write the revised contract.

---

# RURO Model-Specification Contract v2: Stijn-Style Enhanced

**File to save as:** `RURO_model_spec_contract_v2_stijn_enhanced.md`
**Replaces (for the next estimation step):** `RURO_model_spec_contract_v1.md`, §18 minimum baseline.
**Purpose audience:** Claude Code, auditing and modifying the **enhanced** Python/GAMSPy pipeline (`scripts/enhanced/`), not the `scripts/Job_model/` GMM branch.

---

## 1. Purpose of the revised contract

This contract supersedes v1's choice of the bundled job-choice model as the target specification for the next estimation step. It defines the target as a **Stijn-style enhanced RURO model** built on the continuous-draws enhanced pipeline (`scripts/enhanced/enh_RURO_draws.py` → `enh_RURO_euromod.py` → `enh_RURO_prep_mnl_basic.py` → `enh_RURO_estimate_FR.py`), augmented with one additive occupation-opportunity layer.

The contract has two uses:
1. **Audit** the current enhanced pipeline (data prep, draws, MNL prep, estimator, post-estimation) against the target model defined here, producing `RURO_code_contract_audit_v2.md`.
2. **Modify** the enhanced pipeline where it deviates from the target, with patches collected into `RURO_patch_plan_v2.md`.

The contract is for code, not for paper prose, and does not duplicate the theory paper.

---

## 2. Why the bundled job-choice model is not the next target

The bundled job-choice branch (`scripts/Job_model/run_job_ruro_pipeline.py`, specs `estimation_spec_job_M2h_pruned.yaml` etc.) defines a job alternative as `(hours_bin, wage_bin, isco1, type_id)` drawn from an empirical or GMM-derived `q_job`. It is the strongest current empirical candidate, but it has properties that block its use as the target for the next step:

- **Opportunity layers are not cleanly separated.** Hours, wage, and occupation are folded into the same `q_job`. The likelihood contribution `−log q_job` mixes three different proposal densities and one market-opportunity index, which makes it impossible to attribute identified variation to a specific opportunity component. This is exactly the separation the JMP decomposition requires.
- **Occupation is embedded in the job bundle, not in an opportunity density.** The `beta_offer_isco1_*` terms in the M2h spec are market-access shifters, not an occupation-opportunity density with its own normalization and proposal correction.
- **The proposal correction is not transparently factorized.** `log_q_total = log_q_state + log_q_job` collapses three structural objects into two log-densities, so removing one layer for counterfactual decomposition is not well-defined.
- **A clean Stijn-style reference design exists in the same repository** (the continuous enhanced branch), is closer to the literature (Aaberge–Colombino, Dagsvik–Jia, Jacquet–Jia–Thoresen), and has a transparent additive structure that maps directly onto the welfare-decomposition counterfactuals in the JMP.

The job-choice branch is retained as a **robustness extension**, not the target.

---

## 3. Target Stijn-style enhanced RURO model

The target choice index for household `h` and alternative `j` is:

```
V_hj  =  U_hj                              (preference utility, §7)
       + O_hj^H                            (employment / labour-time opportunity, §8)
       + O_hj^W                            (wage opportunity, §9)
       + O_hj^Occ                          (occupation opportunity, §10)
       − log q_hj                          (proposal / prior correction, §11)
```

All opportunity components are **additive** in the log-density. None is conditional on another at the first specification step (`M0`); conditional structures `O^H | Occ` and `O^W | Occ, H` are explicit later extensions (§19).

For couples, the model is partner-additive in opportunities and partner-additive in leisure, with a single shared household-consumption term:

```
V_hj  =  U_hj(C, L_m, L_f)
       + O_hj^H_m + O_hj^H_f
       + O_hj^W_m + O_hj^W_f
       + O_hj^Occ_m + O_hj^Occ_f
       − log q_hj
```

This structure is what the enhanced pipeline already implements for the first three terms; adding `O^Occ` as a fourth, clearly named, additive component is the substantive change in v2.

---

## 4. Choice unit

The choice unit is the **household**.

- Singles male (`sm`) and singles female (`sf`) are separate groups with separate parameter blocks.
- Couples consist of one male and one female partner (`cm`, `cf`); leisure is partner-specific, consumption is shared at the household level.
- France 2016 baseline: ~1,676 singles households and ~2,577 couples households (total 4,253 groups). Joint estimation runs across all four groups, with gender-specific parameters where the spec requires.

No change vs. v1 §2 except that the v1 statement "the baseline uses the job-choice 200-alternative branch" is replaced by §5 below.

---

## 5. Alternatives and proposal distribution

The choice set per household is a finite set of **sampled continuous-draws alternatives** produced by `enh_RURO_draws.py`, not by the job universe / GMM branch.

For singles, an alternative is one of:
- A **non-employment** state: `(h = 0, w = 0)`.
- A **working** alternative: `(h, w, occ)`, where `h` and `w` are continuous draws and `occ` is the occupation category (see §6).

For couples, an alternative is a joint pair of singles-style alternatives, one for each partner.

The proposal distribution `q` factorizes:

```
q(e, h, w, occ | X)
  = q_E(e | X)                                   employment state proposal
  · 1{e = 1} · q_H(h | X)                        hours proposal, conditional on working
  · 1{e = 1} · q_W(w | X)                        wage proposal, conditional on working
  · 1{e = 1} · q_Occ(occ | X)                    occupation proposal, conditional on working
```

For non-employment (`e = 0`), `q_H = q_W = q_Occ = 1` (degenerate). On the log scale:

```
log q = log q_E + 1{e=1} · ( log q_H + log q_W + log q_Occ )
```

Concretely, the audit must verify or implement:
- `q_E`: probability of non-employment vs. working, with the existing `pi0_m`, `pi0_f` controls.
- `q_H`: a simple draw distribution over `[h_min, h_max]` matching the Stijn convention (uniform plus focal-point smoothing is acceptable; documented in the MNL sidecar).
- `q_W`: a draw distribution over `[w_min, w_max]` (uniform is the Stijn baseline; an empirical distribution may be substituted with explicit documentation).
- `q_Occ`: a draw distribution over the occupation categories from §6. The simplest first version is the **empirical occupation share among working deciders** (overall, not conditional on `X`).

Number of alternatives per household: 100, matching the current enhanced continuous-branch convention. Exactly one alternative per household carries `chosen = 1`.

---

## 6. Required occupation / ISCO variable

The model requires a single occupation variable for every alternative. The pipeline already contains the upstream logic to create this in `scripts/enhanced/enh_RURO_prep.py` (functions `_compute_loc_ruro`, `_collapse_loc_to_loc4`, plus `loc` / `loc_raw` from `enh_france_data_prep.py`).

Required hierarchy of choice, in priority order:

1. **ISCO08 1-digit** (`isco1` or `loc_ruro`): the 9 main ISCO-08 major groups (1 Managers, 2 Professionals, 3 Technicians, 4 Clerical, 5 Service/Sales, 6 Agricultural, 7 Crafts, 8 Operators, 9 Elementary). The audit must verify which column carries this for the **final** MNL parquet outputs and harmonize naming.
2. **LOC4 task groups** (`loc4`): the existing 4-category collapse (1 routine-manual, 2 nonroutine-manual, 3 routine-cognitive, 4 nonroutine-cognitive). Acceptable fallback if `isco1` cannot be carried through to the final MNL files without significant rework.
3. **Coarser binary** (e.g. manual vs. cognitive): only as an emergency fallback if neither of the above is present, with a clear note in the patch plan.

**Naming rule.** Whichever variable is used, the spec block, post-estimation labels, and the JMP writeup must call it **occupation opportunity**, never sector opportunity. ISCO classifies occupations; NACE classifies industries. The project files have already confirmed NACE is not in the final MNL files. Until NACE is carried end-to-end, the word "sector" must not appear in either the YAML spec block names or the post-estimation HTML labels for this layer.

**Audit step (required before estimation).** Claude Code must inspect the actual columns of `fr_2016_RURO_mnl__singles.parquet` and `fr_2016_RURO_mnl__couples.parquet` and report which of `isco1`, `loc_ruro`, `loc4`, `loc` are present. Do not assume any of them are present in the *continuous-branch* final MNL files. The current continuous MNL files are documented as carrying `loc` / `loc4` but **not necessarily** a clean `isco1`. Carrying `isco1` end-to-end through the continuous branch is one of the required pipeline changes (§14).

---

## 7. Preference utility

Identical to v1 §4. Box-Cox utility in normalized consumption and normalized leisure.

Singles (`g ∈ {sm, sf}`):

```
U_g(C, L; Z) = β_c_g · BC(C, θ_c_g) + β_l_g(Z) · BC(L, θ_l_g)
β_l_g(Z) = β_l0_g + β_l_age_g · age_norm + β_l_age2_g · age_norm² + β_l_nkids_g · n_children + β_l_educH_g · educH
```

Couples:

```
U(C, L_m, L_f) = β_c · BC(C, θ_c) + β_l_m(Z_m) · BC(L_m, θ_l_m) + β_l_f(Z_f) · BC(L_f, θ_l_f)
```

Preference shifters allowed at `M0`: `age_norm`, `age_norm²`, `n_children` (female only), `educH`. Consumption–leisure and within-couple leisure–leisure interactions are off at `M0`.

Critically: **occupation does not enter `U` at `M0`**. See §18.

---

## 8. Employment / labour-time opportunity

Single additive log-density block, per individual:

```
O^H_hj = β_E · 1{h_j > 0}                                       employment intercept
       + β_pt1 · 1{h_j ∈ PT1}                                   focal-point 20h
       + β_pt2 · 1{h_j ∈ PT2}                                   focal-point 30h
       + β_ft  · 1{h_j ∈ FT}                                    focal-point 40h
       + β_gsur · gsur · 1{h_j > 0}                             labor-demand shifter
       + β_E_educH · educH · 1{h_j > 0}                         education shifter
```

Focal-point ranges:
- PT1: `h ∈ [18.5, 21.5]`
- PT2: `h ∈ [29.5, 30.5]`
- FT:  `h ∈ [37.5, 40.5]`

All terms are gated by `working = 1{h > 0}`. For couples, partner-additive with partner-specific covariates.

`β_E` plays the role of the Aaberge–Colombino market-vs-non-market log-odds (`log(p_1 / p_0)`). It must be estimated, not normalized to 0.

`gsur` is opportunity-only by exclusion restriction (§18). The audit must verify `gsur` does not enter `U`.

---

## 9. Wage opportunity

Log-normal wage opportunity with a Mincer-style mean and a single residual variance. Identical in form to v1 §6.

For each working alternative:

```
log f_W(w | X) = − 0.5 · z² − log σ − log w
z = (log w − μ(X)) / σ
μ(X) = β_w0 + β_w_educL · educL + β_w_educH · educH + β_w_pexp · pexp + β_w_pexp² · pexp²
σ > 0
```

For non-employment, `O^W = 0` (no density contribution).

For couples, partner-additive with partner-specific covariates.

Mincer shifters (`educL`, `educH`, `pexp`, `pexp²`) are opportunity-only and must not appear in `U`. The audit must verify this gating against the active YAML spec.

The `−log w` Jacobian term must be present (level-density Jacobian when the density is specified on `w`). The audit must verify this is correctly implemented in both `estimation_engine.py` and `gamspy_estimation_vectorized.py`.

---

## 10. Occupation opportunity

A new additive log-density block, separately named in the YAML spec as `occupation_opportunity` (not `sector_opportunity` and not `market_opportunity`).

Baseline `M0` form, per individual:

```
O^Occ_hj = Σ_k β_occ_k · 1{occ_j = k} · 1{h_j > 0}
```

with one reference occupation omitted (suggested: `occ = 1` = Managers, or `occ = 1` = routine-manual when `loc4` is used). Gating by `working` is mandatory; the term is zero at non-employment.

For couples, partner-additive with partner-specific occupation covariates.

The first specification step uses **unconditional** occupation opportunity. Conditional structures `O^H | Occ` and `O^W | Occ, H` (Aaberge–Colombino-style occupation-specific hours and wage densities) are **explicit later extensions** in §19. Adding them at `M0` makes identification harder and adds many parameters; they must wait until `M0`–`M2` are stable.

Occupation must **not** enter `U` at `M0` (see §18).

---

## 11. Proposal / prior correction

The proposal correction subtracts `log q` once per alternative. The convention is:

```
prior      = q on the original scale, strictly positive
log_prior  = log(prior) = log q_E + 1{e=1} · ( log q_H + log q_W + log q_Occ )
likelihood correction adds −log_prior to V_hj
```

**Explicit requirement.** If occupation is drawn (`q_Occ` is not degenerate), the `log_prior` column **must include `log q_Occ`**. The audit must verify, file by file, that `log_prior` in the final MNL parquet exactly equals the sum of the per-layer log-proposals:

```
| log_prior − ( log q_E + working · (log q_H + log q_W + log q_Occ) ) | < 1e-8
```

For couples:

```
log_prior_couple = log_prior_m + log_prior_f
```

with each partner's `log_prior` computed as above.

**Hard constraints (must hold in every MNL output):**
- `prior > 0` everywhere.
- `| log(prior) − log_prior | < 1e-8`.
- No second subtraction of `log_prior` anywhere downstream of MNL prep.
- The current continuous-fallback bug in `enh_RURO_prep_mnl_basic.py` that sets `df["prior"] = np.log(prior_density)` must be patched before estimation (carried over from v1).

If a later step replaces the occupation proposal with a non-uniform empirical density, the patch must update both `q_Occ` and the stored `log_prior` consistently and produce a sidecar `mnlmeta.json` entry documenting the occupation proposal source.

---

## 12. Likelihood contribution

Per-household conditional log-likelihood:

```
ℓ_h  =  V_h,chosen  −  log Σ_{j ∈ S_h} exp(V_hj)
```

Joint log-likelihood: `Σ_h ℓ_h` summed across SM / SF / CM / CF groups with group-specific parameter blocks where the spec requires.

Estimator path: enhanced pipeline, joint mode, `enh_RURO_estimate_FR.py --group joint --solver gamspy-conopt --vectorized --spec-config <new spec>`. The audit must verify that the vectorized GAMSPy and the NumPy/SciPy reference engines produce the same log-likelihood at the same parameter vector within tolerance `1e-6` per observation, with the new `O^Occ` term included in both code paths.

Numerical safeguards:
- `C, L > 0` strictly (clip).
- Row-wise max-stabilized `log-sum-exp`.
- `σ > 0` enforced.
- Box-Cox: at the estimated `θ` values, compare the GAMSPy Taylor-approximated `BC` to the exact NumPy `BC` on the observed `(C, L)` grid; flag pointwise relative error `> 1e-3`.

---

## 13. Required data columns

The final MNL parquet files consumed by the enhanced estimator must expose, at minimum, the following columns per row (one row = one alternative for one household):

Household / sample:
- `idhh`, `decider_id`, group flag (`singles_male` / `singles_female` / `couples`)
- `chosen` (0/1, summing to 1 per household)

Behavioral / budget:
- `h`, `w`, `working = 1{h > 0}`
- `C` (normalized household disposable income), `L` (normalized leisure)
- Scaling factors recorded in `mnlmeta.json`
- For couples: `hours_male`, `hours_female`, `wage_male`, `wage_female`, `working_male`, `working_female`

Preference shifters:
- `age_norm`, `age_norm²` (per spouse for couples)
- `n_children`
- `educL`, `educH` (per spouse for couples)

Opportunity shifters:
- `gsur` (per spouse for couples)
- `pexp` or `pexp_years` (per spouse for couples)

Occupation (new requirement vs. current continuous MNL files):
- `isco1` (preferred) or `loc_ruro` or `loc4`, per individual; for couples, `isco1_male` and `isco1_female`
- For non-working alternatives, occupation is set to a reserved code (e.g. `-1`) and is gated out by `working` in `O^Occ`.

Proposal / prior:
- `prior` (strictly positive)
- `log_prior` (= `log(prior)` within 1e-8)
- Component log-proposals: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` (and `_male` / `_female` for couples)

Variables that **must not** be present at `M0`:
- `job_id`, `type_id`, `log_q_job`, `log_q_state` (these belong to the job-choice branch and would create confusion)
- `nace`, `nace1`, `sector`, `industry` (not available; the spec parser must not reference them)

---

## 14. Required changes to the enhanced pipeline

The current enhanced pipeline (`scripts/enhanced/`) implements `O^H`, `O^W`, and the prior correction, but does not implement `O^Occ` or carry `isco1` through to the final MNL files. The required modifications, in order:

1. **`enh_RURO_prep.py`**: confirm that `isco1` (or equivalently `loc_ruro`) is computed for every working decider and is carried in the singles and couples RURO-ready parquet files. Verify the non-worker convention (`isco1 = -1`).

2. **`enh_RURO_draws.py`**:
   - Add an occupation-draw step. For every working alternative, draw `isco1_draw` from the chosen `q_Occ`. The simplest first version is uniform over the observed working occupation set, or proportional to empirical occupation shares.
   - For the baseline (`draw = 0`), keep the observed `isco1`.
   - Store `log_q_Occ` per row.
   - The non-employment alternative gets `isco1 = -1` and `log_q_Occ = 0`.

3. **`enh_RURO_euromod.py`**: no change required if EUROMOD disposable income does not depend on occupation. Confirm this is the case for the French baseline.

4. **`enh_RURO_prep_mnl_basic.py`**:
   - Carry `isco1` (and `isco1_male`, `isco1_female` for couples) into the final MNL columns.
   - Compute `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)` from the component columns.
   - Patch the continuous-fallback bug at lines 1448–1451 and 1572–1575 so `df["prior"] = prior_density` (original scale) and `df["log_prior"] = np.log(prior_density)`.
   - Add an assertion harness that runs after every build: `(prior > 0).all()`, `max|log(prior) − log_prior| < 1e-8`, `chosen.groupby(idhh).sum() == 1`.

5. **`estimation_spec_parser.py`**:
   - Parse a new YAML block `occupation_opportunity` distinct from `market_opportunity`.
   - Register `β_occ_k` parameters with bounds and initial values.
   - Reject any spec where the same variable appears in both `utility` and any `*_opportunity` block (§18).

6. **`estimation_engine.py`** and **`gamspy_estimation_vectorized.py`**:
   - Add the `O^Occ` term to the choice index, gated by `working`.
   - Use the reference occupation category and the omitted-dummy convention.
   - Mirror partner-additive structure for couples.

7. **`RURO_post_estimation_styled.py`**:
   - Add an "Occupation Opportunity" block reporting estimated `β_occ_k` with SE, t, p.
   - Add an "Observed vs Predicted Occupation Distribution" panel.
   - In all labels, use "occupation", not "sector".

8. **New YAML spec file `estimation_spec_stijn_enhanced_M0.yaml`** in `scripts/enhanced/`, encoding §22.

9. **New script `scripts/diagnostics/run_recovery_test_stijn_enhanced.py`** (stub allowed at audit time; full implementation in patch plan).

---

## 15. Normalizations and identification restrictions

1. **Gumbel scale** normalized to 1; no scale parameter estimated.
2. **Reference categories**: `educM` omitted for education; one occupation category omitted (`occ = 1`); reference is not estimated.
3. **Proposal correction** applied exactly once per alternative, with no double-subtraction downstream.
4. **Non-labor income** enters preferences via `C` only, not opportunity.
5. **Couples**: shared `β_c`, `θ_c`; partner-specific leisure and opportunity blocks.
6. **`O^Occ` reference**: the omitted occupation pins the level of `O^Occ`; only contrasts are identified.
7. **Identification anchors** required by exclusion restrictions in §18.

---

## 16. Parameters to estimate

`M0` parameter block:

Preference (singles + couples):
- `β_c_sm`, `β_c_sf`, `β_c` (shared couples)
- `θ_c_sm`, `θ_c_sf`, `θ_c`
- `β_l0_sm`, `β_l0_sf`, `β_l0_m`, `β_l0_f`
- `θ_l_sm`, `θ_l_sf`, `θ_l_m`, `θ_l_f`
- `β_l_age_g`, `β_l_age2_g`, `β_l_educH_g` for `g ∈ {sm, sf, m, f}`
- `β_l_nkids_sf`, `β_l_nkids_f` (female only)

Hours opportunity (per gender):
- `β_E`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_E_educH`

Wage opportunity (per gender):
- `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp²`, `σ`

Occupation opportunity (per gender, omitting reference):
- `β_occ_k` for `k = 2, …, K` (where `K = 9` for `isco1`, `K = 4` for `loc4`)

Total parameters at `M0` with `isco1`: roughly 50–65 depending on whether hours/wage shifters are gender-specific.

---

## 17. Parameters to fix or bound

- `θ_l_*`, `θ_c_*`: bounded to `[−8.0, 0.95]`. **None hard-fixed at `M0`** — in particular `θ_c_sm` must be free, unlike in the M2h pruned spec. The audit must flag any spec that hard-fixes `θ_c_sm`.
- `β_l0_*`: bounded below at `0.05` to keep MU(L) positive at the boundary.
- `σ`: bounded to `[0.1, 20.0]`.
- Soft constraints on `MU(C) > 0`, `MU(L) > 0` may be active but not tight enough to determine point estimates.

Bound-hit diagnostics: every parameter within `1e-3` of a bound at the optimum is flagged in the run report.

---

## 18. What must not enter both utility and opportunity at the first step

| Variable                             | Utility (`U`) | `O^H` | `O^W` | `O^Occ` |
|--------------------------------------|---------------|-------|-------|---------|
| `age_norm`, `age_norm²`              | Yes           | No    | No    | No      |
| `n_children`                         | Yes           | No    | No    | No      |
| `educH` (in leisure utility)         | Yes           | Yes (separately) | Yes (separately) | No |
| `educL`                              | No            | No    | Yes   | No      |
| `pexp`, `pexp²`                      | No            | No    | Yes   | No      |
| `gsur`                               | No            | Yes   | No    | No      |
| `isco1` / `loc_ruro` / `loc4`        | **No**        | No    | No    | Yes     |
| Non-labor income                     | Yes (via `C`) | No    | No    | No      |

Critical at `M0`: **occupation must enter `O^Occ` only**, never `U`, never `O^H`, never `O^W`. Adding it to multiple blocks creates a known double-counting identification problem and is permitted only as a deliberate later extension after `M0`–`M3` are stable.

The audit must reject any YAML spec where the same variable appears in both `utility` and any `*_opportunity` block at `M0`.

---

## 19. Specification ladder

Estimate `M0` to convergence before proceeding. Move up the ladder only after the previous step passes the diagnostic gates in §20.

| Spec | Adds vs previous | Status |
|------|------------------|--------|
| `M0` | Baseline: `U + O^H + O^W + O^Occ − log q`, with additive unconditional `O^Occ` | **Target for next estimation step** |
| `M1` | Add `β_E_educL` and `β_offer_gsur_educ_k` interactions to `O^H` | First robustness |
| `M2` | Add region dummies to `O^H` or `O^Occ` if region variation is sufficient | Region opportunity |
| `M3` | `O^W` conditional on `Occ` (occupation-specific Mincer means, shared σ) | Aaberge–Colombino-style |
| `M4` | `O^H` conditional on `Occ` (occupation-specific focal points and `β_E`) | Aaberge–Colombino-style |
| `M5` | Optional `β_cl` consumption–leisure interaction, `β_ll` leisure–leisure for couples | Preference flexibility |
| `M6` | Move from continuous-draws to GMM job universe (`scripts/Job_model`) for robustness comparison | Robustness only |

`M3`–`M4` are the conditional opportunity structures referenced in §10. They are explicit later extensions, not part of `M0`.

---

## 20. Required diagnostics

Every estimation run must produce, in `estimation_results.json` or sidecars:

1. Optimizer status, number of iterations, final gradient norm.
2. `joint_ll`, `ll_null_uniform`, `ll_null_prior_corrected`, McFadden ρ², AIC, BIC.
3. Hessian condition number; number of negative eigenvalues; smallest absolute eigenvalue.
4. SE, t, p for every estimated parameter; flag non-finite SEs.
5. List of parameters within `1e-3` of any bound.
6. List of poorly-identified parameters (low curvature, large SE).
7. Metadata: `prior_correction_applied = true`, `prior_correction_form = "-log(prior)"`, occupation proposal source, list of opportunity layers active.
8. Observed-vs-predicted fit by group: participation, mean hours, hours histogram with PT1/PT2/FT bins, wage KDE, **occupation distribution by group**.
9. Seed/draw stability: re-estimate `M0` with at least two alternative draw seeds; report max parameter difference.
10. Cross-engine consistency: log-likelihood agreement between `gamspy_estimation_vectorized.py` and `estimation_engine.py` at the estimated `θ` within `1e-6` per observation.

Hard gates for any identification claim or any downstream welfare/decomposition computation:
- No negative Hessian eigenvalues.
- Condition number `< 1e7`.
- All `M0` parameters with finite SEs.
- No bound-hits on substantive parameters.
- Seed stability max-diff `< 5%` for preference and key opportunity coefficients.
- Recovery test (§21) passes.

---

## 21. Recovery-test requirements

Stijn-style simulation recovery on France-shaped data:

1. Fix a "true" `θ⁰` for the `M0` spec at plausible economic values (not the empirical estimates).
2. For each household, generate 100 sampled alternatives from `q` exactly as in estimation (including `q_Occ`).
3. Compute `V_hj⁰` using `θ⁰`, add i.i.d. Gumbel shocks, take the argmax as the synthetic chosen alternative.
4. Re-estimate `M0` from at least three starts (perturbation of `θ⁰`, neutral start, random start).
5. Repeat `R ≥ 50` Monte Carlo replications.

Pass criteria:
- Mean bias `< 10%` of true value for every preference and opportunity coefficient (or `< 0.05` absolute when true value is near 0).
- 95% coverage in `[0.92, 0.98]` for `β_c`, `θ_c`, `β_l0`, `θ_l`, the leading `β_occ_k`, and `β_E`.
- Convergence rate `≥ 90%`.

Until recovery passes on France-shaped data, all France `M0` estimates are **provisional** and must not be used downstream for the welfare layer.

---

## 22. Minimum acceptable baseline specification

**Spec name:** `estimation_spec_stijn_enhanced_M0.yaml`
**Pipeline branch:** enhanced continuous draws (`scripts/enhanced/`), not `scripts/Job_model/`.
**Sample:** France 2016 SRCV / EUROMOD-input, singles (~1,676) and couples (~2,577), joint estimation across SM / SF / CM / CF.
**Alternatives:** 100 per household, drawn by `enh_RURO_draws.py` with occupation draws added.
**Choice index:** `V = U + O^H + O^W + O^Occ − log q`.
**Utility:** Box-Cox in `C` and `L`; leisure shifters `age_norm`, `age_norm²`, `n_children` (female only), `educH`. No interactions.
**`O^H`:** `β_E`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_E_educH`.
**`O^W`:** log-normal with `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp²`, `σ`.
**`O^Occ`:** `β_occ_k` for `k = 2, …, K` using `isco1` if available, else `loc4`; reference omitted.
**Prior correction:** `−log_prior` with `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)`.
**No occupation in `U`, `O^H`, or `O^W`.**
**No `O^H | Occ`, no `O^W | Occ`.**
**No `nace` / sector layer.**
**No `job_id` / `type_id` / GMM.**

Reportable when (i) it converges with positive-definite Hessian and finite SEs, (ii) §21 recovery passes, (iii) seed stability passes.

---

## 23. Later extensions

The following are **explicitly out of scope at `M0`**:

1. **Occupation-conditional hours `O^H | Occ`** (`M4`): occupation-specific PT1/PT2/FT clustering.
2. **Occupation-conditional wage `O^W | Occ`** (`M3`): occupation-specific Mincer intercepts, slopes, and possibly variance.
3. **Region opportunity** (`M2`): region-level dummies in `O^H` or `O^Occ`.
4. **True NACE / industry sector layer** (`O^S`): requires carrying NACE through the entire enhanced pipeline; must be named `sector_opportunity` only when this is done.
5. **Random preference coefficients** on `β_l0` or `θ_l`.
6. **Consumption–leisure** (`β_cl`) and **within-couple leisure–leisure** (`β_ll`) interactions.
7. **Multi-year identification** using France 2021.
8. **Cross-country extensions**: Germany, others.
9. **GMM job-universe comparison** (`M6`): use `scripts/Job_model/` as a robustness check after `M0`–`M2` are stable.
10. **Welfare layer**: household AEI-style money-metric welfare, joint non-work reference, and the two-factor Shapley-Shorrocks decomposition of the household welfare Gini. These are downstream of a stable `M0` plus passed recovery test.

These extensions are tracked on the roadmap but excluded from the v2 audit.

---

## Implementation checklist for Claude Code (audit)

1. **Branch check.** Verify all referenced scripts live in `scripts/enhanced/` (enhanced continuous branch). Do **not** modify `scripts/Job_model/`.
2. **Column audit on current MNL files.** Read schema of `fr_2016_RURO_mnl__singles.parquet` and `fr_2016_RURO_mnl__couples.parquet`. Report presence/absence of: `isco1`, `loc_ruro`, `loc4`, `loc`, `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`. Confirm absence of: `job_id`, `type_id`, `nace*`, `sector*`, `industry*`.
3. **Prior convention.** Assert `(df["prior"] > 0).all()` and `max|log(df["prior"]) − df["log_prior"]| < 1e-8` for both files. Identify and report (do not patch yet) any code path where `df["prior"] = np.log(prior_density)` is set.
4. **Occupation pipeline gap.** Identify the smallest set of patches in `enh_RURO_prep.py`, `enh_RURO_draws.py`, and `enh_RURO_prep_mnl_basic.py` needed to carry `isco1` and `log_q_Occ` end-to-end. Output as `RURO_patch_plan_v2.md`.
5. **Exclusion restrictions.** Parse all `scripts/enhanced/estimation_spec*.yaml` and report, per spec, any variable appearing in both `utility` and any `*_opportunity` block (per §18 matrix).
6. **Occupation naming.** Grep `scripts/enhanced/` and `RURO_post_estimation_styled.py` for the word "sector". Where it refers to `isco1` / `loc4` / `loc`, flag for rename to "occupation". Verify no `sector_opportunity` YAML block targets occupation data.
7. **Spec parser readiness.** Inspect `estimation_spec_parser.py`. Report what is needed to register a new `occupation_opportunity` block separate from `market_opportunity`.
8. **Likelihood readiness.** Inspect `estimation_engine.py` and `gamspy_estimation_vectorized.py`. Identify the call sites where `O^H`, `O^W` are added to the choice index, and propose the insertion point for `O^Occ`. Verify both engines apply the prior correction exactly once.
9. **`θ_c_sm` fix audit.** Grep all active YAML for hard-fixing `theta_c_sm`. Flag any such spec as non-compliant with `M0`.
10. **Cross-engine consistency.** Locate or scaffold the script that compares `joint_ll` between the NumPy and GAMSPy paths at a fixed `θ`. Confirm it can be run after `O^Occ` is added.
11. **Recovery harness.** Verify or scaffold `scripts/diagnostics/run_recovery_test_stijn_enhanced.py`. Do not run; only verify the entry point.
12. **Audit report.** Emit `RURO_code_contract_audit_v2.md`. For each section §1–§23 of this contract, status `PASS` / `FAIL` / `PARTIAL` / `N/A`, with file and line references and the minimal patch needed for each non-`PASS`. Patches are described, not applied; application happens in `RURO_patch_plan_v2.md` as a separate step.

---

**Save this file as `RURO_model_spec_contract_v2_stijn_enhanced.md`** in the project root or `docs/`. Use it as input to the next Claude Code task: produce `RURO_code_contract_audit_v2.md` against the current `scripts/enhanced/` codebase.