# RURO Model-Specification Contract v4: Stijn-style Occupation (EUROMOD-grounded)

**File to save as:** `RURO_model_spec_contract_v4_stijn_occ.md`
**Supersedes:** `RURO_model_spec_contract_v3_stijn_occ.md`. Sections of v3 that are not contradicted here remain valid; in case of conflict, v4 wins.
**Predecessors retained for traceability:** v1 (`RURO_model_spec_contract_v1.md`), v2 (`RURO_model_spec_contract_v2_stijn_enhanced.md`), v3 (`RURO_model_spec_contract_v3_stijn_occ.md`).
**Audience:** Claude Code, auditing and modifying the **enhanced** Python/GAMSPy pipeline (`scripts/enhanced/`).
**Out of scope:** the job-choice / GMM branch (`scripts/Job_model/`), the welfare layer, the theory paper.
**New in v4:** the contract is grounded in the EUROMOD reference files
(`euromod_fr_2015_2017_input_variables.csv`,
`euromod_fr_2015_2017_output_variable_index.csv`,
`euromod_fr_2015_2017_standard_income_concepts.csv`,
`euromod_fr_2015_2017_input_output_reference.md`),
so the variable names used here are anchored to what EUROMOD France 2015–2017 actually emits.

---

## 1. Purpose of the revised contract

v3 locked occupation as the third opportunity layer of the Stijn-style enhanced RURO model and ruled out `lindi`-based industry at `M0`. v4 keeps that decision and tightens three things that v3 left implicit:

1. **Anchors variable names to the EUROMOD France 2015–2017 dictionary.** The contract no longer relies on free-form column names; every named variable corresponds either to a documented EUROMOD input (`loc`, `lindi`, `lhw`, `les`, `deh`, `dwt`, …) or to a documented EUROMOD output (`ils_dispy`, `ils_earns`, `ils_origy`, …) or to a project-defined derivation of these.
2. **Locks the disposable-income source.** Household consumption `C` in the utility is constructed from EUROMOD's standardized disposable income `ils_dispy` (12 components per the standard income concepts table), not from any ad-hoc reconstruction.
3. **Locks the wording.** ISCO is occupation. NACE is industry. `loc` (ISCO 1-digit per EUROMOD) is the occupation column. `lindi` (NACE 1-digit per EUROMOD) is the industry column and is held out for the `M6` robustness extension only.

The v4 contract is a code-audit document, not paper prose. Output of the audit: `RURO_code_contract_audit_v4.md`. Patches: `RURO_patch_plan_v4.md`. No patches are applied during the audit step.

---

## 2. Why the target is Stijn-style enhanced RURO

Stijn's R implementation (`stijn/Ruro_estimation_H.Rmd`, `stijn/Ruro_estimation_new.Rmd`, `stijn/Ruro_functions_EMRWS.R`) defines the choice index as

```
V = U + hopp + wopp − prior
```

with explicit additive opportunity densities and an explicit proposal correction. The enhanced continuous-draws pipeline in `scripts/enhanced/` reproduces this structure transparently: `enh_RURO_draws.py` draws hours and wages, `enh_RURO_euromod.py` calls EUROMOD on the draws to produce `ils_dispy` and its components, `enh_RURO_prep_mnl_basic.py` builds the proposal correction, `estimation_engine.py` and `gamspy_estimation_vectorized.py` evaluate `U + O^H + O^W − log q`.

The bundled job-choice branch (`scripts/Job_model/`) folds hours, wage, and occupation into a single empirical `q_job`, which is empirically promising but blocks transparent decomposition of welfare inequality into the opportunity components the JMP requires. The Stijn-style enhanced branch keeps each layer cleanly named and cleanly subtracted in the prior. That is what the JMP decomposition needs and is why v4 keeps the enhanced branch as the target.

The v4 model adds one new additive layer, `O^Occ`, based on `loc` (ISCO 1-digit) or its 4-task collapse `loc4`.

---

## 3. Why occupation opportunity is the relevant layer

Three reasons.

First, **availability**. EUROMOD France 2015–2017 emits `loc` directly as a labour-market input (`LABOUR MARKET : Occupation (ISCO 1-Digit)`, codes `0` armed forces, `1` senior officials and managers, `2` professionals, `3` technicians, `4` clerks, `5` service and sales workers, `6` skilled agricultural workers, `7` craft and related trades, `8` plant and machine operators, `9` elementary occupations). The project already computes `loc_ruro` and the four-task collapse `loc4` in `scripts/enhanced/enh_RURO_prep.py` and retains them in `reduce_mnl_columns.py`. No new upstream raw-data work is needed.

Second, **labour-market interpretation**. Occupation captures the kind of work a household member is qualified to do and the set of job offers structurally open to them. A clerk and a craft worker with the same age, education, and region face different hours/wage offer distributions; that variation belongs in opportunity, not preferences.

Third, **alignment with the JMP decomposition**. The JMP decomposes welfare inequality into preference-driven and opportunity-driven components. If occupation availability differs systematically across households — by region, by parental background, by education paths — those differences are the kind of opportunity heterogeneity the paper aims to make compensable. Folding them into preferences (as the current job-choice model does implicitly through `q_job`) would understate the opportunity share.

---

## 4. Distinction between occupation opportunity and industry opportunity

Occupation and industry are two distinct EUROMOD classifications. The contract draws a sharp line.

| Concept    | EUROMOD label              | EUROMOD variable | Coding system | Used in v4 |
|------------|----------------------------|------------------|---------------|-------------|
| Occupation | `LABOUR MARKET : Occupation (ISCO 1-Digit)` | `loc`           | ISCO-08, 0–9  | **Yes, at `M0`** (with `loc4` collapse) |
| Industry   | `LABOUR MARKET : Industry (NACE) 1 Agriculture 2 Industry 3 Services` | `lindi` | NACE 1-digit, 0–3 | **No, deferred to `M6`** |

Naming rules, enforced by the audit:

- Code, YAML blocks, parameter names (`beta_occ_*`), and post-estimation HTML labels must use the word **"occupation"**.
- The words **"sector"** and **"industry"** must not appear in any `M0` artefact that refers to the `loc` / `loc4` layer.
- A separate `industry_opportunity` block reserved for `lindi` is described in §25 but is not part of `M0`. Until `M6` is activated, the spec parser must not parse an `industry_opportunity` block.

Both `loc` and `loc4` are occupation classifications and follow the same naming rule. The 4-task collapse does not change the interpretation; it only reduces the parameter count.

---

## 5. Target model

The choice index for household `h` and alternative `j` is:

```
V_hj  =  U_hj                              (preference utility, §8)
       + O_hj^E                            (employment intercept, §9)
       + O_hj^H                            (hours-density shifters, §9)
       + O_hj^W                            (wage opportunity, §10)
       + O_hj^Occ                          (occupation opportunity, §11)
       − log q_hj                          (proposal correction, §13)
```

All opportunity components are **additive** at `M0`. No conditional structure (`O^H | Occ`, `O^W | Occ`) is allowed at `M0`. For couples, all opportunity blocks are partner-additive, leisure is partner-specific, consumption is shared at the household level.

Aaberge–Colombino notation correspondence: `O^E + O^H ≈ log g_1`, `O^W ≈ log g_2`, `O^Occ ≈ log g_3`. At `M0` we make the strong simplifying assumption that `g_1`, `g_2`, `g_3` factorize independently of one another.

---

## 6. Choice unit

Unchanged from v3 §6.

The choice unit is the **household**.

- Singles male (`sm`) and singles female (`sf`) are separate groups with separate parameter blocks.
- Couples (`cm`, `cf`) share `β_c`, `θ_c` for household consumption; leisure and opportunities are partner-specific.
- France 2016 baseline: ~1,676 singles households and ~2,577 couples households (4,253 groups total). Joint estimation runs across SM / SF / CM / CF.

Household weight is `dwt` (EUROMOD `DEMOGRAPHIC : Weight`) and is used for descriptive statistics, not for parameter estimation in the MNL likelihood at `M0`. Sample is restricted to RURO-eligible deciders via the `ruro_sample` flag built in `enh_RURO_prep.py`.

---

## 7. Alternatives and proposal distribution

The choice set per household is 100 sampled alternatives generated by `enh_RURO_draws.py` (continuous-draws branch). The job-choice / GMM branch is not used at `M0`.

For singles, an alternative is one of:

- **Non-employment**: `(h = 0, w = 0)`, with `loc` set to `−1` (RURO non-worker convention from `enh_RURO_prep.py`).
- **Working**: `(h, w, loc)`, where `h ∈ [h_min, h_max]` and `w ∈ [w_min, w_max]` are continuous draws (Stijn's uniform proposal is acceptable; an empirical proposal may be substituted with documentation in `mnlmeta.json`), and `loc ∈ {1, …, 9}` (or the corresponding `loc4 ∈ {1, …, 4}`) is drawn from a documented occupation proposal `q_Occ`.

For couples, an alternative is a joint pair of singles-style alternatives, one per partner. Partner draws are conditionally independent at `M0`.

Proposal factorization, per individual:

```
q(e, h, w, loc | X)
  = q_E(e | X)
  · 1{e = 1} · q_H(h | X) · q_W(w | X) · q_Occ(loc | X)
```

For non-employment, `q_H = q_W = q_Occ = 1`. On the log scale:

```
log q = log q_E + 1{e = 1} · (log q_H + log q_W + log q_Occ)
```

For couples, `log q_couple = log q_male + log q_female`.

**Minimum `q_Occ` at `M0`.** The simplest acceptable occupation proposal is the empirical occupation share among working deciders in the France 2016 RURO-eligible sample (`ruro_sample == 1 & is_worker == 1`), computed once on `loc4` and reused for every household. Region- or education-conditional `q_Occ` is an extension, not part of `M0`.

---

## 8. Preference utility

Box-Cox utility in normalized consumption and normalized leisure. Consumption `C` is normalized **household disposable income** built from EUROMOD's `ils_dispy` (`Standardised Disposable income`, 12 components per the standard income concepts table). The audit must verify that `C` in the MNL files traces to `ils_dispy` or `ils_dispy_em` (not to any ad-hoc reconstruction of `ils_origy − ils_tax − ils_sicee`). Leisure `L` is normalized from observed/drawn hours.

Singles (`g ∈ {sm, sf}`):

```
U_g(C, L; Z) = β_c_g · BC(C, θ_c_g) + β_l_g(Z) · BC(L, θ_l_g)
β_l_g(Z) = β_l0_g + β_l_age_g · age_norm + β_l_age2_g · age_norm² + β_l_nkids_g · n_children + β_l_educH_g · educH
```

Couples:

```
U(C, L_m, L_f) = β_c · BC(C, θ_c) + β_l_m(Z_m) · BC(L_m, θ_l_m) + β_l_f(Z_f) · BC(L_f, θ_l_f)
```

Preference shifters at `M0`: `age_norm`, `age_norm²`, `n_children` (female only), `educH`. No consumption–leisure interaction, no leisure–leisure interaction.

`educH` is derived from EUROMOD `deh` (`DEMOGRAPHIC : Education - Highest Status`), with the project-standard mapping in `enh_france_data_prep.py`. The same `deh`-derived `educL`, `educM`, `educH` dummies are used throughout.

**`loc` / `loc4` must not enter `U` at `M0`.** See §20.

---

## 9. Employment / labour-time opportunity

Additive log-density block per individual:

```
O^E_hj + O^H_hj
  = β_E             · 1{h_j > 0}                          (employment intercept = log-odds market vs non-market)
  + β_pt1           · 1{h_j ∈ PT1}                        (focal 20h)
  + β_pt2           · 1{h_j ∈ PT2}                        (focal 30h)
  + β_ft            · 1{h_j ∈ FT}                         (focal 40h)
  + β_gsur          · gsur · 1{h_j > 0}                   (labour-demand shifter)
  + β_E_educH       · educH · 1{h_j > 0}                  (education shifter on market access)
```

Focal-point bands match the existing pipeline:
- PT1: `h ∈ [18.5, 21.5]`
- PT2: `h ∈ [29.5, 30.5]`
- FT:  `h ∈ [37.5, 40.5]`

All terms are gated by `working = 1{h > 0}`. `working` is built from EUROMOD `lhw` (`LABOUR MARKET : Hours worked per week`) and `les` (`LABOUR MARKET : Economic Status`) via `_compute_is_worker` in `enh_RURO_prep.py`, following the RURO convention `working = (lma == 1 | les ∈ {3,5,7}) & lhw > 0`.

For couples, partner-additive with partner-specific covariates.

`β_E` is estimated, not normalized to 0; it pins the market-vs-non-market log-odds. `gsur` (group-specific unemployment / opportunity rate, prepared by `enh_prepare_FR_gsur.py`) is opportunity-only by exclusion restriction (§20).

---

## 10. Wage opportunity

Log-normal wage opportunity with a Mincer-style mean, per working alternative:

```
log f_W(w | X) = − 0.5 · z² − log σ − log w
z = (log w − μ(X)) / σ
μ(X) = β_w0 + β_w_educL · educL + β_w_educH · educH + β_w_pexp · pexp + β_w_pexp² · pexp²
σ > 0
```

For non-employment, `O^W = 0`. For couples, partner-additive with partner-specific covariates.

Observed wage `w` is built from EUROMOD `yivwg` / `yem` (employment-income variables; `yem` = `INCOME : Employment`, monthly gross employee income) divided by hours per the project convention in `enh_RURO_prep.py`. The audit must confirm that the wage column fed into the wage density (`wage_for_draws` / `wage_ruro` / `wage`) matches the project convention and that the `−log w` Jacobian term is present in both engines.

At `M0`, `σ` is shared across occupations and the Mincer mean does not depend on `loc` / `loc4`. Occupation-conditional Mincer means and variances are `M3`, not `M0`.

Mincer shifters (`educL`, `educH`, `pexp`, `pexp²`) are opportunity-only by exclusion restriction.

---

## 11. Occupation opportunity using ISCO / LOC

A new additive log-density block, named `occupation_opportunity` in the YAML spec.

Baseline `M0` form, per individual:

```
O^Occ_hj = Σ_{k ≠ k_ref} β_occ_k · 1{loc4_j = k} · 1{h_j > 0}
```

with one reference occupation omitted. Suggested reference: `loc4 = 1` (routine-manual) when using the 4-task collapse; or `loc = 9` (elementary) when using ISCO 1-digit.

Variable choice (set per-spec, not mixed within one spec):

- **Preferred at `M0`**: `loc4` (project 4-task collapse: 1 routine-manual, 2 nonroutine-manual, 3 routine-cognitive, 4 nonroutine-cognitive). Fewer parameters, more stable identification on ~4,253 households.
- **Permitted at `M0`**: `loc` (EUROMOD ISCO 1-digit, codes 1–9; `0` armed forces treated separately via `loc_armed` per `enh_RURO_prep.py`; `loc4` then carries the `-1` non-worker and `-2` unknown-worker conventions). More flexible but adds 8 parameters per gender.

The audit must verify which of `loc` / `loc4` is actually carried in the final continuous-branch MNL files (`fr_2016_RURO_mnl__singles.parquet`, `fr_2016_RURO_mnl__couples.parquet`). Current evidence from `reduce_mnl_columns.py` and `RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md` shows that the continuous MNL files carry `loc` and `loc4` but **not necessarily** a clean `isco1`. If `loc4` is present and `loc` is not, the baseline must use `loc4`. If both are present, the patch plan picks one and documents the choice.

For couples, partner-additive:

```
O^Occ_h = O^Occ_h,m + O^Occ_h,f
```

with partner-specific `loc4_male`, `loc4_female` columns.

**Hard restriction at `M0`.** `loc` / `loc4` enter `O^Occ` only. They do not enter `U`, `O^H`, or `O^W`. Conditional structures `O^H | Occ` and `O^W | Occ` are explicit later extensions (§25). Occupation-as-preference is also a later extension.

---

## 12. Treatment of non-work alternatives

For every alternative with `h = 0`:

- `working = 0`.
- Hours focal-point indicators `1{h ∈ PT1, PT2, FT}` are 0.
- `gsur · 1{h > 0}` is 0.
- `educH · 1{h > 0}` is 0.
- `O^W = 0` (the wage density does not contribute).
- `loc` / `loc4` is set to `−1` (RURO non-worker convention); every category indicator `1{loc4 = k}` is 0, so `O^Occ = 0`.
- `q_H = q_W = q_Occ = 1`, so `log q_H = log q_W = log q_Occ = 0`.
- `log q = log q_E(e = 0)`.

The opportunity-side contribution to a non-employment alternative is therefore `O^E = 0` plus `−log q_E(e = 0)`. The non-employment alternative has

```
V_h,0 = U_h,0 − log q_E(e = 0)
```

This is the contract's reference for `β_E`'s identification: every working alternative gains `β_E + (focal-point terms) + (covariate shifters) + O^Occ_k − log q_E(e = 1) − log q_H − log q_W − log q_Occ`.

The audit must verify this gating in `estimation_engine.py` and `gamspy_estimation_vectorized.py` for both singles and couples.

---

## 13. Proposal / prior correction

Convention, mandatory in every MNL output:

```
prior     = q on the original scale, strictly positive
log_prior = log(prior) = log q_E + 1{e = 1} · (log q_H + log q_W + log q_Occ)
likelihood adds −log_prior to V_hj
```

For couples, `log_prior_couple = log_prior_m + log_prior_f`.

**Critical requirement: if occupation is drawn, `q_Occ` must appear in `log_prior`.** The audit must verify, file by file:

```
| log_prior − ( log_q_E + working · (log_q_H + log_q_W + log_q_Occ) ) | < 1e-8
```

Hard constraints in every MNL output:
- `prior > 0` everywhere.
- `| log(prior) − log_prior | < 1e-8`.
- Exactly one `−log_prior` subtraction per alternative downstream of MNL prep.
- The known fallback bug in `enh_RURO_prep_mnl_basic.py` (continuous-branch singles ~lines 1448–1451, couples ~lines 1572–1575) where `df["prior"] = np.log(prior_density)` must be patched so that `df["prior"] = prior_density` and `df["log_prior"] = np.log(prior_density)`.

If the occupation draw is added but the prior is not updated to include `log_q_Occ`, the model is **misspecified by a missing change-of-variables term**. The audit must flag this as a blocking failure.

The `mnlmeta.json` sidecar must record:
- The occupation proposal source (e.g. "empirical loc4 share over working deciders, France 2016").
- The list of active proposal layers (`q_E`, `q_H`, `q_W`, `q_Occ`).
- The non-worker and unknown-worker code conventions for `loc`/`loc4`.

---

## 14. Likelihood contribution

Per-household conditional log-likelihood:

```
ℓ_h = V_h,chosen − log Σ_{j ∈ S_h} exp(V_hj)
```

Joint log-likelihood: `Σ_h ℓ_h` across SM / SF / CM / CF.

Estimator: `enh_RURO_estimate_FR.py --group joint --solver gamspy-conopt --vectorized --spec-config estimation_spec_stijn_occ_M0.yaml`.

Cross-engine check: at the converged `θ`, `joint_ll` from `gamspy_estimation_vectorized.py` must agree with `estimation_engine.py` within `1e-6` per observation, with `O^Occ` included in both code paths.

Numerical safeguards: clip `C, L > 0`; max-stabilized `log-sum-exp`; `σ > 0` enforced; Box-Cox Taylor approximation in GAMSPy validated against the exact NumPy `BC` at the estimated `θ` (flag pointwise relative error `> 1e-3`).

---

## 15. Required data columns

The final continuous-branch MNL parquet files must expose, per row (one row = one alternative for one household):

Household / sample identifiers:
- `idhh`, `idperson` (or `decider_id`), group flag (`singles_male` / `singles_female` / `couples`)
- `chosen` (0/1, summing to 1 per household)
- `dwt` (EUROMOD `DEMOGRAPHIC : Weight`) for descriptives only

Behavioural / budget:
- `h` (or `hours`, `lhw`), `w` (or `wage`, `wage_ruro`), `working = 1{h > 0}`
- `C` (normalized household disposable income built from EUROMOD `ils_dispy` / `ils_dispy_em`), `L` (normalized leisure built from `h`)
- Scaling factors recorded in `mnlmeta.json`
- For couples: `hours_male`, `hours_female`, `wage_male`, `wage_female`, `working_male`, `working_female`

EUROMOD output components used for `C` (from the standard income concepts table; `ils_dispy` has 12 components):
- `ils_dispy` or `ils_dispy_em` (final household disposable income)
- Components `ils_origy`, `ils_earns`, `ils_pen`, `ils_ben`, `ils_tax`, `ils_sicee` (kept for diagnostics and consistency checks, not direct utility inputs)

Preference shifters:
- `age_norm`, `age_norm²` (per spouse for couples), derived from EUROMOD `dag`
- `n_children`, derived from household composition
- `educL`, `educH` (per spouse for couples), derived from EUROMOD `deh`

Opportunity shifters:
- `gsur` (per spouse for couples), from `enh_prepare_FR_gsur.py`
- `pexp` or `pexp_years` (per spouse for couples), derived from `dag`, `deh`, and `liwwh` / `liwmy`

Occupation (the new `M0` requirement):
- `loc4` (preferred at `M0`) and/or `loc` (with `K = 9`), per individual; for couples `loc4_male` / `loc4_female`
- Non-worker convention: `loc4 = loc = −1`
- Unknown-worker convention: `loc4 = loc = −2`

Proposal / prior:
- `prior` (strictly positive)
- `log_prior` (= `log(prior)` within 1e-8)
- Component log-proposals: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` (with `_male` / `_female` variants for couples)

Columns that **must not** be present at `M0`:

- Job-choice branch artefacts: `job_id`, `type_id`, `hours_bin`, `wage_bin`, `log_q_job`, `log_q_state`, `log_q_total`. These belong to `scripts/Job_model/` and must not contaminate the enhanced-branch `M0`.
- Industry-side variables: `lindi`, `industry`, `nace`. These are reserved for the `M6` industry-opportunity extension (§25).
- Any `sector_*` or `industry_*` parameter name.

---

## 16. Required changes to the enhanced pipeline

In execution order, on `scripts/enhanced/` only:

1. **`enh_france_data_prep.py`** — confirm `loc` (EUROMOD `LABOUR MARKET : Occupation (ISCO 1-Digit)`) is read from EUROMOD-input and carried through to the harmonized output. Confirm `lindi` is read (it is in the EUROMOD input dictionary) but kept dormant.

2. **`enh_RURO_prep.py`** — confirm `loc_ruro` and `loc4` are computed for every working decider and carried in the singles and couples RURO-ready parquet files. Verify the conventions: non-worker `= −1`, unknown-worker `= −2`, armed-forces `loc = 0` tracked in `loc_armed` and left as `loc4 = −2` (current code behaviour, per the inspected source).

3. **`enh_RURO_draws.py`** — add an occupation-draw step:
   - For every working alternative (`draw ≥ 1`, `e = 1`), draw `loc4_draw` from `q_Occ` (empirical share of `loc4` among working RURO-eligible deciders).
   - For the baseline (`draw = 0`), keep the observed `loc4`.
   - Store `log_q_Occ` per row. Non-employment rows: `log_q_Occ = 0`.
   - For couples, store `log_q_Occ_male`, `log_q_Occ_female`.

4. **`enh_RURO_euromod.py`** — confirm that EUROMOD disposable income `ils_dispy` does not depend on `loc4` for the French baseline. If it does (rare; armed forces or specific tax regimes), either fix `loc4` to its observed value during EUROMOD simulation or generate occupation-specific EUROMOD outputs. Document the choice in `mnlmeta.json`.

5. **`enh_RURO_prep_mnl_basic.py`**:
   - Carry `loc4` (and `loc4_male`, `loc4_female`) into the final MNL columns.
   - Compute `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)` from component columns.
   - Patch the continuous-fallback bug at the lines noted in §13.
   - Add an assertion harness that runs after every build:
     ```python
     assert (df["prior"] > 0).all()
     assert np.max(np.abs(np.log(df["prior"]) - df["log_prior"])) < 1e-8
     assert df.groupby("idhh")["chosen"].sum().eq(1).all()
     ```

6. **`reduce_mnl_columns.py`** — `loc`, `loc4`, `loc4_1`..`loc4_4`, `loc4_male`, `loc4_female`, `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` (and `_male`/`_female`) must be in the retained-columns set. `lindi`, `industry`, `nace` must remain excluded at `M0`; the current code already lists them in the income/industry block, so the patch is to keep them in the **read** set for upstream traceability but exclude them from the `M0` MNL output.

7. **`estimation_spec_parser.py`**:
   - Parse a new YAML block `occupation_opportunity`, distinct from `market_opportunity` and from any future `industry_opportunity`.
   - Register `β_occ_k` parameters with bounds and initial values.
   - Reject any spec that puts the same variable in both `utility` and any `*_opportunity` block (§20).

8. **`estimation_engine.py`** and **`gamspy_estimation_vectorized.py`**:
   - Add the `O^Occ` term to the choice index, gated by `working`.
   - Use the omitted-reference dummy convention.
   - Partner-additive for couples.

9. **`RURO_post_estimation_styled.py`**:
   - Add an "Occupation Opportunity" section reporting `β_occ_k` with SE, t, p.
   - Add "Observed vs Predicted Occupation Distribution" panels by group (SM / SF / CM / CF) and by `loc4` category.
   - Use the word "occupation" throughout; never "sector" or "industry".

10. **New YAML spec `scripts/enhanced/estimation_spec_stijn_occ_M0.yaml`**, encoding §24.

11. **New diagnostics script `scripts/diagnostics/run_recovery_test_stijn_occ.py`** (stub allowed at audit time; full implementation in the patch plan).

---

## 17. Normalizations and identification restrictions

1. **Gumbel scale** normalized to 1.
2. **Reference categories**: `educM` omitted for education; one omitted occupation category pins the level of `O^Occ`.
3. **Proposal correction** applied exactly once per alternative.
4. **Non-labour income** enters preferences via `C` (through the non-labour components of `ils_dispy`); does not enter any opportunity block.
5. **Couples**: shared `β_c`, `θ_c`; partner-specific leisure and opportunity blocks.
6. **`O^Occ` level**: only contrasts vs. the omitted occupation are identified.
7. **Identification anchors** required by exclusion restrictions in §20.

---

## 18. Parameters to estimate

`M0` parameter block.

Preferences (singles + couples):
- `β_c_sm`, `β_c_sf`, `β_c` (shared in couples)
- `θ_c_sm`, `θ_c_sf`, `θ_c`
- `β_l0_sm`, `β_l0_sf`, `β_l0_m`, `β_l0_f`
- `θ_l_sm`, `θ_l_sf`, `θ_l_m`, `θ_l_f`
- `β_l_age_g`, `β_l_age2_g`, `β_l_educH_g` for `g ∈ {sm, sf, m, f}`
- `β_l_nkids_sf`, `β_l_nkids_f` (female only)

Employment / hours opportunity (per gender):
- `β_E`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_E_educH`

Wage opportunity (per gender):
- `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp²`, `σ`

Occupation opportunity (per gender, omitting reference):
- With `loc4`: `β_occ_2`, `β_occ_3`, `β_occ_4` per gender → 12 parameters across 4 gender groups (or fewer if gender-pooled).
- With `loc` (ISCO 1-digit): `β_occ_k` for `k = 2, …, 9` per gender → up to 32 parameters across 4 groups.

Total at `M0` with `loc4`: roughly 45–55 parameters depending on gender-pooling choices.

---

## 19. Parameters to fix or bound

- `θ_l_*`, `θ_c_*`: bounded to `[−8.0, 0.95]`. **None hard-fixed at `M0`**; in particular `θ_c_sm` must be free.
- `β_l0_*`: bounded below at `0.05` to keep MU(L) positive at the boundary.
- `σ`: bounded to `[0.1, 20.0]`.
- Soft constraints on `MU(C) > 0`, `MU(L) > 0` may be active but not tight enough to determine point estimates.

Bound-hit diagnostics: every parameter within `1e-3` of a bound at the optimum is flagged. The audit flags any spec that hard-fixes `θ_c_sm`.

---

## 20. What must not enter both utility and opportunity at the first step

| Variable                       | `U` | `O^E + O^H` | `O^W` | `O^Occ` |
|--------------------------------|-----|-------------|-------|---------|
| `age_norm`, `age_norm²`        | Yes | No          | No    | No      |
| `n_children`                   | Yes | No          | No    | No      |
| `educH` (in leisure)           | Yes | Yes (separately) | Yes (separately) | No |
| `educL`                        | No  | No          | Yes   | No      |
| `pexp`, `pexp²`                | No  | No          | Yes   | No      |
| `gsur`                         | No  | Yes         | No    | No      |
| `loc4` / `loc`                 | **No** | No       | No    | Yes     |
| `lindi` (industry)             | No  | No          | No    | No (reserved for `M6`) |
| Non-labour income (via `C` from `ils_dispy`) | Yes | No | No | No |

The spec parser must reject any YAML that puts the same variable in both `utility` and any opportunity block at `M0`.

---

## 21. Specification ladder

Estimate `M0` to convergence and pass the §22 gates before moving up.

| Spec | Adds vs previous                                                       | Status |
|------|------------------------------------------------------------------------|--------|
| `M0` | Baseline: `U + O^E + O^H + O^W + O^Occ − log q`, additive, `loc4`     | **Target for next estimation step** |
| `M1` | Add `β_E_educL`; add region dummies (NUTS-1 from `drgn1`) to `O^E + O^H` if variation suffices | First robustness |
| `M2` | Replace `loc4` with `loc` (ISCO 1-digit, 9 codes) for richer occupation | Occupation granularity |
| `M3` | `O^W` conditional on `loc` (occupation-specific Mincer means, shared σ) | Aaberge–Colombino-style |
| `M4` | `O^H` conditional on `loc` (occupation-specific focal points, `β_E`)   | Aaberge–Colombino-style |
| `M5` | Optional `β_cl`, `β_ll` interactions in `U`                            | Preference flexibility |
| `M6` | Add `lindi` as a second, separate `industry_opportunity` block         | NACE industry robustness (§25) |
| `M7` | Job-choice / GMM branch as a separate robustness comparison            | External-branch robustness |

`M3`–`M4` are the conditional opportunity structures explicitly excluded from `M0`. `M6` introduces the industry layer using `lindi`.

---

## 22. Required diagnostics

Every estimation run stores in `estimation_results.json` or sidecars:

1. Optimizer status, iteration count, final gradient norm.
2. `joint_ll`, `ll_null_uniform`, `ll_null_prior_corrected`, McFadden ρ², AIC, BIC.
3. Hessian condition number; number of negative eigenvalues; smallest absolute eigenvalue.
4. SE, t, p for every estimated parameter; flag non-finite SEs.
5. Parameters within `1e-3` of a bound.
6. Poorly-identified parameters.
7. Metadata: `prior_correction_applied = true`, `prior_correction_form = "-log(prior)"`, occupation proposal source, list of opportunity layers active, EUROMOD system tag (e.g. `fr_2016`), `ils_dispy` source column.
8. Observed-vs-predicted fit by group: participation, mean hours, hours histogram (with PT1 / PT2 / FT bins), wage KDE, **occupation distribution by `loc4`**.
9. Seed/draw stability: re-estimate `M0` with at least two alternative draw seeds; report max parameter difference.
10. Cross-engine consistency: `joint_ll` agreement between GAMSPy vectorized and NumPy/SciPy at the same `θ`, within `1e-6` per observation.

Hard gates for any identification claim or downstream welfare computation:
- No negative Hessian eigenvalues.
- Condition number `< 1e7`.
- All `M0` parameters with finite SEs.
- No bound-hits on substantive parameters.
- Seed-stability max-diff `< 5%` for preference and key opportunity coefficients.
- Recovery test (§23) passes.

---

## 23. Recovery-test requirements

Stijn-style simulation recovery on France-shaped data:

1. Fix `θ⁰` for the `M0` spec at plausible economic values (not the empirical estimates).
2. For every household in the France 2016 RURO-eligible sample, draw 100 alternatives from `q` exactly as in estimation, **including `q_Occ`**.
3. Compute `V_hj⁰` using `θ⁰`, add i.i.d. Gumbel shocks, take the argmax as the synthetic chosen alternative.
4. Re-estimate `M0` from at least three starts (perturbation of `θ⁰`, neutral, random).
5. Run `R ≥ 50` Monte Carlo replications.

Pass criteria:
- Mean bias `< 10%` of the true value (or `< 0.05` absolute when true value is near 0) for every preference and opportunity coefficient.
- 95% coverage in `[0.92, 0.98]` for `β_c`, `θ_c`, `β_l0`, `θ_l`, the leading `β_occ_k`, and `β_E`.
- Convergence rate `≥ 90%`.

Until recovery passes, France `M0` estimates are **provisional** and must not enter the welfare layer.

---

## 24. Minimum acceptable baseline specification

**Spec name:** `estimation_spec_stijn_occ_M0.yaml`
**Pipeline branch:** enhanced continuous draws (`scripts/enhanced/`).
**EUROMOD system:** France 2016 (`fr_2016`), inputs from EU-SILC + EUROMOD-input dictionary documented in `euromod_fr_2015_2017_input_variables.csv`; standardized disposable income `ils_dispy` per `euromod_fr_2015_2017_standard_income_concepts.csv`.
**Sample:** ~1,676 singles and ~2,577 couples, joint estimation across SM / SF / CM / CF, RURO-eligible deciders.
**Alternatives:** 100 per household from `enh_RURO_draws.py` with occupation draws added.
**Choice index:** `V = U + O^E + O^H + O^W + O^Occ − log q`.
**Utility:** Box-Cox in `C` (built from `ils_dispy`) and `L` (built from `lhw`/`h`); leisure shifters `age_norm`, `age_norm²`, `n_children` (female only), `educH` (from `deh`). No interactions.
**`O^E + O^H`:** `β_E`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_E_educH`.
**`O^W`:** log-normal with `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp²`, `σ`. Shared across occupations.
**`O^Occ`:** `β_occ_2`, `β_occ_3`, `β_occ_4` per gender using `loc4`. Reference `loc4 = 1` (routine-manual).
**Prior:** `−log_prior` with `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)`.
**Forbidden at `M0`:** `loc4` / `loc` in `U`, `O^H`, or `O^W`; `O^H | occ`; `O^W | occ`; `lindi`; `nace`; `industry`; `sector_*` parameters; `job_id`, `type_id`, `log_q_job`, `log_q_state`, `log_q_total`; hard-fixed `θ_c_sm`.

Reportable when (i) it converges with positive-definite Hessian and finite SEs, (ii) §23 recovery passes, (iii) seed-stability passes.

---

## 25. Later extensions, including `lindi` / NACE industry opportunity

Out of scope at `M0`, on the roadmap:

1. **Occupation-conditional hours `O^H | loc`** (`M4`): occupation-specific focal-point shifts.
2. **Occupation-conditional wage `O^W | loc`** (`M3`): occupation-specific Mincer intercepts, slopes, and possibly variance.
3. **Region opportunity** (`M1`): NUTS-1 region dummies from `drgn1` in `O^E + O^H` or `O^Occ`.
4. **Finer occupation** (`M2`): replace `loc4` with ISCO 1-digit `loc`.
5. **Occupation preferences**: only after `M0`–`M4` are stable, allowing `loc4` shifters in `β_l` for tested identification.
6. **Industry opportunity using `lindi`** (`M6`): a separate `industry_opportunity` block based on EUROMOD `lindi` (`LABOUR MARKET : Industry (NACE) 1 Agriculture 2 Industry 3 Services`). Implementation requirements when activated:
   - Carry `lindi` through `enh_france_data_prep.py`, `enh_RURO_prep.py`, the draw step, `enh_RURO_prep_mnl_basic.py`, and `reduce_mnl_columns.py`.
   - Define the non-worker convention for `lindi` (suggested `−1`, mirroring `loc`).
   - Draw `lindi_draw` from a documented industry proposal `q_Ind` (empirical NACE 1-digit share among working RURO-eligible deciders).
   - Store `log_q_Ind`; update `log_prior` to `log_q_E + working · (log_q_H + log_q_W + log_q_Occ + log_q_Ind)`.
   - Define a new YAML block `industry_opportunity` with `β_ind_*` parameters; the reference category is the most common observed `lindi` value (likely `3 = Services` in France).
   - Re-run identification gates. `lindi` is a 3-category variable, so it is parameter-cheap, but it adds a co-linearity risk with `loc4`. The audit at `M6` must report the cross-tabulation of `loc4` × `lindi` and warn if any cell is empty or near-empty.
   - Industry opportunity is a **robustness** check vs. occupation, not a replacement at `M0`.
7. **Random preference coefficients** on `β_l0` or `θ_l`.
8. **Multi-year identification** using France 2021 (EUROMOD system `fr_2021`).
9. **Cross-country**: Germany, others.
10. **Job-choice / GMM branch comparison** (`M7`): use `scripts/Job_model/` for robustness after `M0`–`M2` stabilize.
11. **Welfare layer**: household AEI-style money-metric welfare based on `ils_dispy`, joint non-work reference, two-factor Shapley–Shorrocks decomposition. Downstream of stable `M0` and passed recovery.

---

## Implementation checklist for Claude Code (audit)

1. **Branch check.** Verify all targets live in `scripts/enhanced/`. Do not modify `scripts/Job_model/`.
2. **EUROMOD-variable column audit.** Read the schema of `fr_2016_RURO_mnl__singles.parquet` and `fr_2016_RURO_mnl__couples.parquet`. Report presence/absence of: `loc`, `loc4`, `loc_ruro`, `loc4_1`–`loc4_4`, `loc4_male`, `loc4_female`, `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`, `gsur`, `pexp` / `pexp_years`, `educL` / `educH`, `dwt`, `ils_dispy` / `ils_dispy_em`. Confirm absence of: `job_id`, `type_id`, `log_q_job`, `log_q_state`, `log_q_total`, `lindi`, `industry`, `nace`.
3. **Disposable-income provenance.** Verify the normalization input for `C` traces to `ils_dispy` or `ils_dispy_em` and not to an ad-hoc reconstruction. Confirm `mnlmeta.json` records the source column name.
4. **Prior convention.** Assert `(df["prior"] > 0).all()` and `max|log(df["prior"]) − df["log_prior"]| < 1e-8` for both files. Report exact code locations where `df["prior"] = np.log(prior_density)` is currently set (continuous-fallback singles ~1448–1451, couples ~1572–1575). Do not patch yet.
5. **Occupation pipeline gap.** Identify the smallest patch set in `enh_RURO_prep.py`, `enh_RURO_draws.py`, `enh_RURO_prep_mnl_basic.py`, and `reduce_mnl_columns.py` to carry `loc4` and `log_q_Occ` end-to-end. Output as `RURO_patch_plan_v4.md`.
6. **Naming sweep.** Grep `scripts/enhanced/` and `RURO_post_estimation_styled.py` for the strings "sector" and "industry". Where they refer to `loc` / `loc4` / `isco1`, flag for rename to "occupation". Confirm no `sector_opportunity` or `industry_opportunity` block targets occupation data at `M0`.
7. **Spec parser readiness.** Inspect `estimation_spec_parser.py`. Report changes needed to register `occupation_opportunity` distinct from `market_opportunity` and from a future `industry_opportunity`.
8. **Likelihood readiness.** Inspect `estimation_engine.py` and `gamspy_estimation_vectorized.py`. Locate call sites for `O^H`, `O^W`; propose insertion for `O^Occ`. Verify the prior correction is subtracted exactly once.
9. **Exclusion restrictions.** Parse all active `scripts/enhanced/estimation_spec*.yaml`. Report any variable appearing in both `utility` and any `*_opportunity` block per §20.
10. **`θ_c_sm` audit.** Flag any YAML hard-fixing `theta_c_sm`.
11. **Cross-engine consistency.** Locate or scaffold a `joint_ll` comparison script (GAMSPy vectorized vs NumPy/SciPy) at a fixed `θ` after `O^Occ` is added.
12. **Recovery harness.** Verify or scaffold `scripts/diagnostics/run_recovery_test_stijn_occ.py`. Do not run; verify the entry point.
13. **`lindi` watch.** Verify that no `M0` artefact references `lindi`, `industry`, or `nace`. Add a single comment in `reduce_mnl_columns.py` noting that `lindi` (EUROMOD `LABOUR MARKET : Industry (NACE)`) is reserved for the `M6` industry-opportunity extension and that `loc` (EUROMOD `LABOUR MARKET : Occupation (ISCO 1-Digit)`) is the `M0` occupation layer.
14. **Audit report.** Emit `RURO_code_contract_audit_v4.md`. For each section §1–§25, status `PASS` / `FAIL` / `PARTIAL` / `N/A`, with file and line references and the minimal patch needed. Do not apply patches in the audit step; collect them in `RURO_patch_plan_v4.md`.

---

**Save this contract as `RURO_model_spec_contract_v4_stijn_occ.md`** in the project root or `docs/`. The next Claude Code task is to produce `RURO_code_contract_audit_v4.md` against the current `scripts/enhanced/` codebase. The patch plan is a separate step.
