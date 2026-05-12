I now have full clarity on the data: `loc` and `loc4` (occupation) exist in current continuous MNL files; `lindi` is the NACE industry variable. Here is the v3 contract.

---

# RURO Model-Specification Contract v3: Stijn-style Occupation

**File to save as:** `RURO_model_spec_contract_v3_stijn_occ.md`
**Replaces (for the next estimation step):** §6 and §10 of `RURO_model_spec_contract_v2_stijn_enhanced.md`. Other sections of v2 remain valid where not contradicted here.
**Audience:** Claude Code, auditing and modifying the **enhanced** Python/GAMSPy pipeline (`scripts/enhanced/`).
**Out of scope:** the job-choice / GMM branch (`scripts/Job_model/`), the theory paper, the welfare layer.

---

## 1. Purpose of the revised contract

This v3 contract narrows the target opportunity layer named in v2. v2 left the third opportunity layer labeled ambiguously between "occupation" and "sector" because the data audit was still pending. The audit is now resolved: in this project, the relevant labour-market classification carried in the data is **occupation**, encoded as `loc` (ISCO 1-digit, the project's `loc_ruro` / `isco1` synonym) and the four-task collapse `loc4`. The industry variable `lindi` (NACE 1-digit: 1 Agriculture, 2 Industry, 3 Services) exists in EUROMOD-input files but is not the main opportunity layer and is held for later robustness.

The v3 contract:

1. Locks the third opportunity layer of the Stijn-style enhanced RURO model as **occupation opportunity** based on `loc` / `loc4`.
2. Forbids the words "sector" and "industry" in the YAML, code comments, and post-estimation labels for this layer.
3. Specifies the additive opportunity structure `U + O^E + O^H + O^W + O^Occ − log q` for `M0`.
4. Reserves conditional structures `O^H | Occ`, `O^W | Occ`, and any `lindi`-based industry opportunity for later extensions only.
5. Gives Claude Code an audit-and-patch checklist against `scripts/enhanced/`.

---

## 2. Why the target is Stijn-style enhanced RURO

Stijn's R implementation (`stijn/Ruro_estimation_H.Rmd`, `stijn/Ruro_estimation_new.Rmd`, `stijn/Ruro_functions_EMRWS.R`) defines the choice index as

```
V = U + hopp + wopp − prior
```

with explicit additive opportunity densities and an explicit proposal correction. The enhanced continuous-draws pipeline (`scripts/enhanced/`) reproduces this structure transparently: `enh_RURO_draws.py` draws hours and wages, `enh_RURO_prep_mnl_basic.py` builds the proposal correction, `estimation_engine.py` and `gamspy_estimation_vectorized.py` evaluate `U + O^H + O^W − log q`.

The bundled job-choice branch (`scripts/Job_model/`) folds hours, wage, and occupation into a single empirical `q_job`, which is empirically promising but blocks transparent decomposition of welfare inequality into the opportunity components the JMP requires. The Stijn-style enhanced branch keeps each layer cleanly named and cleanly subtracted in the prior, which is what the JMP decomposition needs.

The v3 target therefore stays on the enhanced branch and adds **one** new additive layer: `O^Occ` based on `loc` / `loc4`.

---

## 3. Why occupation opportunity is the relevant layer

Three reasons.

First, **availability**. `loc` (ISCO 1-digit) and `loc4` (the project's 4-task collapse) are already computed in `scripts/enhanced/enh_RURO_prep.py` and are retained in the continuous-branch final MNL files according to `scripts/enhanced/reduce_mnl_columns.py`. No new upstream raw-data work is needed to expose them.

Second, **labour-market interpretation**. Occupation captures the kind of work a household member is qualified to do and the set of job offers structurally open to them. A construction worker and a software engineer with the same age, education, and region face very different hours/wage offer distributions; that variation belongs in opportunity, not preferences.

Third, **alignment with the JMP decomposition**. The JMP decomposes welfare inequality into preference-driven and opportunity-driven components. If occupation availability differs systematically across households — by region, by parental background, by education paths — those differences are the kind of opportunity heterogeneity the paper aims to make compensable. Folding them into preferences (as the current job-choice model implicitly does through `q_job`) would understate the opportunity share.

---

## 4. Distinction between occupation opportunity and industry opportunity

Occupation and industry are different classifications of labour-market position. The contract draws a sharp line:

| Concept   | What it classifies         | Project variable | ISCO/NACE   | Used in this contract |
|-----------|----------------------------|------------------|-------------|------------------------|
| Occupation | What the worker does (their job role) | `loc` (1-digit), `loc4` (4-task collapse), `loc_ruro` | ISCO-08    | **Yes, at `M0`**       |
| Industry   | What the employer produces (the sector) | `lindi`        | NACE        | **No, deferred to robustness** |

Naming rule, strictly enforced by the audit:

- The YAML block, the code comments, the parameter names (`beta_occ_*`), and the post-estimation HTML labels must use the word **"occupation"**.
- The words **"sector"** and **"industry"** must not appear in `M0` artefacts that refer to the `loc` / `loc4` layer.
- A separate `industry_opportunity` block reserved for `lindi` may be introduced later (§25). Until then, `lindi` is not in the spec parser.

A finer-grained `loc` (more than 9 codes) or `loc4` (4 task groups) substitution does not change the naming rule. Both are occupation classifications.

---

## 5. Target model

The choice index for household `h` and alternative `j` is:

```
V_hj  =  U_hj                              (preference utility, §8)
       + O_hj^E                            (employment / market intercept, §9)
       + O_hj^H                            (hours-density shifters, §9)
       + O_hj^W                            (wage opportunity, §10)
       + O_hj^Occ                          (occupation opportunity, §11)
       − log q_hj                          (proposal correction, §13)
```

All opportunity components are **additive** at `M0`. No conditional structure (`O^H | Occ`, `O^W | Occ`) is allowed at `M0`. For couples, all opportunity blocks are partner-additive, leisure is partner-specific, consumption is shared.

Aaberge–Colombino notation correspondence: `O^E + O^H ≈ log g_1` (hours density including the market-vs-non-market log-odds), `O^W ≈ log g_2` (wage density), `O^Occ ≈ log g_3` (occupation density). At `M0` we make the strong simplifying assumption that `g_1`, `g_2`, `g_3` factorize independently.

---

## 6. Choice unit

Unchanged from v2 §4. The choice unit is the **household**:

- Singles male (`sm`) and singles female (`sf`) are separate groups with separate parameter blocks.
- Couples (`cm`, `cf`) share `β_c`, `θ_c` for household consumption; leisure and opportunities are partner-specific.
- France 2016 baseline: ~1,676 singles and ~2,577 couples, joint estimation across SM / SF / CM / CF.

---

## 7. Alternatives and proposal distribution

The choice set per household is 100 sampled alternatives generated by `enh_RURO_draws.py` (the continuous-draws branch). The job-choice / GMM branch is not used at `M0`.

For singles, an alternative is one of:

- **Non-employment**: `(h = 0, w = 0)`, with `occ` set to a reserved code (e.g. `−1`) indicating "not applicable".
- **Working**: `(h, w, occ)`, where `h ∈ [h_min, h_max]` and `w ∈ [w_min, w_max]` are continuous draws (Stijn's uniform proposal is acceptable; an empirical proposal may be substituted with documentation in `mnlmeta.json`), and `occ ∈ {1, …, K}` is drawn from a documented occupation proposal `q_Occ`.

For couples, an alternative is a joint pair of singles-style alternatives, one per partner. Partner draws are taken to be conditionally independent at `M0`.

Proposal factorization, per individual:

```
q(e, h, w, occ | X)
  = q_E(e | X)
  · 1{e = 1} · q_H(h | X) · q_W(w | X) · q_Occ(occ | X)
```

For non-employment, `q_H = q_W = q_Occ = 1` (degenerate). On the log scale:

```
log q = log q_E + 1{e = 1} · (log q_H + log q_W + log q_Occ)
```

For couples, `log q_couple = log q_male + log q_female`.

**Minimum `q_Occ` at `M0`.** The simplest acceptable occupation proposal is the empirical occupation share among working deciders in the France 2016 RURO-eligible sample, computed once and reused for every household. A region- or education-conditional `q_Occ` is an extension, not part of `M0`.

---

## 8. Preference utility

Unchanged from v2 §7. Box-Cox utility in normalized consumption and normalized leisure.

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

**`occ` must not enter `U` at `M0`.** See §20.

---

## 9. Employment / labour-time opportunity

Additive log-density block per individual:

```
O^E_hj + O^H_hj
  = β_E             · 1{h_j > 0}                          (employment intercept = log-odds of market vs non-market)
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

All terms are gated by `working = 1{h > 0}`. For couples, partner-additive with partner-specific covariates.

`β_E` is estimated, not normalized to 0; it pins the market-vs-non-market log-odds. `gsur` is opportunity-only (§20).

---

## 10. Wage opportunity

Log-normal wage opportunity with a Mincer-style mean, per working alternative:

```
log f_W(w | X) = − 0.5 · z² − log σ − log w
z = (log w − μ(X)) / σ
μ(X) = β_w0 + β_w_educL · educL + β_w_educH · educH + β_w_pexp · pexp + β_w_pexp² · pexp²
σ > 0
```

For non-employment, `O^W = 0`. For couples, partner-additive.

The `−log w` Jacobian is mandatory and must be present in both engines. Mincer shifters are opportunity-only.

At `M0`, σ is shared across occupations and the Mincer mean does not depend on `occ`. Occupation-conditional Mincer means and variances are `M3`, not `M0`.

---

## 11. Occupation opportunity using ISCO / LOC

A new additive log-density block, named `occupation_opportunity` in the YAML spec (never `sector_opportunity`, never `industry_opportunity`, never `market_opportunity`).

Baseline `M0` form, per individual:

```
O^Occ_hj = Σ_{k ≠ k_ref} β_occ_k · 1{occ_j = k} · 1{h_j > 0}
```

with one reference occupation omitted. Suggested reference: `loc4 = 1` (routine-manual) when using the 4-task collapse, or `loc = 9` (elementary) when using ISCO 1-digit.

Variable choice (set per-spec, not mixed):

- **Preferred at `M0`**: `loc4` — the 4-task collapse (1 routine-manual, 2 nonroutine-manual, 3 routine-cognitive, 4 nonroutine-cognitive). Fewer parameters, more stable identification on ~4,253 households.
- **Permitted at `M0`**: `loc` (ISCO 1-digit, the project's `isco1`/`loc_ruro` synonym), with `K = 9` categories. More flexible but adds 8 parameters per gender.

The audit must verify which of `loc` or `loc4` is actually carried into the final continuous-branch MNL files (`fr_2016_RURO_mnl__singles.parquet`, `fr_2016_RURO_mnl__couples.parquet`). The current evidence indicates `loc` and `loc4` are retained in the continuous MNL files. If `loc4` is present and `loc` is not, the baseline must use `loc4`. If both are present, the patch plan picks one and documents the choice.

For couples, partner-additive:

```
O^Occ_h = O^Occ_h,m + O^Occ_h,f
```

with partner-specific `occ_m`, `occ_f` columns.

**Hard restriction at `M0`:** `occ` enters `O^Occ` only. It does not enter `U`, `O^H`, or `O^W`. Conditional structures `O^H | Occ` and `O^W | Occ` are explicit later extensions (§25). Occupation preferences are also a later extension.

---

## 12. Treatment of non-work alternatives

For every alternative with `h = 0`:

- `working = 0`.
- The hours focal-point indicators `1{h ∈ PT1, PT2, FT}` are 0.
- `gsur · 1{h > 0}` is 0.
- `educH · 1{h > 0}` is 0.
- `O^W = 0` (the wage density does not contribute).
- `occ` is set to a reserved code (`−1`); `1{occ = k}` is 0 for every real category `k`, so `O^Occ = 0`.
- `q_H = q_W = q_Occ = 1`, so `log q_H = log q_W = log q_Occ = 0`.
- `log q = log q_E(e = 0)`.

The only opportunity-side contribution to a non-employment alternative is `O^E = β_E · 0 = 0` plus `−log q_E(e = 0)`. The non-employment alternative therefore has

```
V_h,0 = U_h,0 − log q_E(e = 0)
```

This is the contract's reference for `β_E`'s identification: relative to non-employment, every working alternative gains `β_E + (focal-point terms) + (covariate shifters) + O^Occ_k − log q_E(e = 1) − log q_H − log q_W − log q_Occ`.

The audit must verify this gating in `estimation_engine.py` and `gamspy_estimation_vectorized.py` for both singles and couples.

---

## 13. Proposal / prior correction

Convention, mandatory in every MNL output:

```
prior     = q on the original scale, strictly positive
log_prior = log(prior) = log q_E + 1{e=1} · (log q_H + log q_W + log q_Occ)
likelihood adds −log_prior to V_hj
```

For couples, `log_prior_couple = log_prior_m + log_prior_f`.

**Critical requirement: if occupation is drawn, `q_Occ` must appear in `log_prior`.** This is the change v3 imposes on the prior. The audit must verify, file by file:

```
| log_prior − ( log_q_E + working · (log_q_H + log_q_W + log_q_Occ) ) | < 1e-8
```

Hard constraints in every MNL output:
- `prior > 0`.
- `| log(prior) − log_prior | < 1e-8`.
- Exactly one `−log_prior` subtraction per alternative downstream of MNL prep.
- The known fallback bug in `enh_RURO_prep_mnl_basic.py` (continuous-branch lines around 1448–1451 for singles and 1572–1575 for couples) where `df["prior"] = np.log(prior_density)` must be patched so that `df["prior"] = prior_density` and `df["log_prior"] = np.log(prior_density)`.

If the occupation draw is added but the prior is not updated to include `log_q_Occ`, the model is **misspecified by a missing change-of-variables term**, and the audit must flag this as a blocking failure.

---

## 14. Likelihood contribution

Per-household conditional log-likelihood:

```
ℓ_h = V_h,chosen − log Σ_{j ∈ S_h} exp(V_hj)
```

Joint log-likelihood: `Σ_h ℓ_h` across SM / SF / CM / CF.

Estimator: `enh_RURO_estimate_FR.py --group joint --solver gamspy-conopt --vectorized --spec-config estimation_spec_stijn_occ_M0.yaml`.

Cross-engine check: at the converged `θ`, `joint_ll` from `gamspy_estimation_vectorized.py` must agree with `estimation_engine.py` within `1e-6` per observation, with `O^Occ` included in both code paths.

Numerical safeguards: clip `C, L > 0`; max-stabilized `log-sum-exp`; `σ > 0` enforced; Box-Cox Taylor approximation in GAMSPy validated against NumPy exact `BC` at the estimated `θ` (flag pointwise relative error `> 1e-3`).

---

## 15. Required data columns

The final continuous-branch MNL parquet files must expose, per row (one row = one alternative for one household):

Household / sample:
- `idhh`, `decider_id`, group flag (`singles_male` / `singles_female` / `couples`)
- `chosen` (0/1, summing to 1 per household)

Behavioural / budget:
- `h`, `w`, `working = 1{h > 0}`
- `C` (normalized household disposable income), `L` (normalized leisure); scaling in `mnlmeta.json`
- For couples: `hours_male`, `hours_female`, `wage_male`, `wage_female`, `working_male`, `working_female`

Preference shifters:
- `age_norm`, `age_norm²` (per spouse for couples)
- `n_children`
- `educL`, `educH` (per spouse for couples)

Opportunity shifters:
- `gsur` (per spouse for couples)
- `pexp` or `pexp_years` (per spouse for couples)

Occupation (the new `M0` requirement):
- `loc4` (preferred at `M0`) or `loc` (with `K = 9`), per individual; for couples `loc4_male` and `loc4_female`
- For non-working alternatives, the occupation column is set to `−1`

Proposal / prior:
- `prior` (strictly positive)
- `log_prior` (= `log(prior)` within 1e-8)
- Component log-proposals: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` (with `_male` / `_female` variants for couples)

Columns that **must not** be in the `M0` MNL files:

- `job_id`, `type_id`, `hours_bin`, `wage_bin`, `log_q_job`, `log_q_state`, `log_q_total` (these belong to the job-choice branch and must not contaminate the enhanced-branch `M0`)
- `lindi`, `industry`, `nace`, `sector` (industry is not at `M0`; see §25)
- Any `sector_*` or `industry_*` parameter name

---

## 16. Required changes to the enhanced pipeline

In execution order:

1. **`enh_RURO_prep.py`** — confirm that `loc` and `loc4` are computed for every working decider and carried in singles and couples RURO-ready parquet files. Verify the non-worker convention (`-1`) and the unknown-worker convention (`-2`).

2. **`enh_RURO_draws.py`** — add an occupation-draw step:
   - For every working alternative (`draw ≥ 1`, `e = 1`), draw `loc4_draw` from `q_Occ` (empirical share of `loc4` among working deciders).
   - For the baseline (`draw = 0`), keep the observed `loc4`.
   - Store `log_q_Occ` per row. Non-employment rows: `log_q_Occ = 0`.
   - For couples, store `log_q_Occ_male`, `log_q_Occ_female`.

3. **`enh_RURO_euromod.py`** — confirm EUROMOD disposable income does not depend on `loc4` for the French baseline. If it does (rare), document this and either fix `loc4` to its observed value during EUROMOD simulation or generate occupation-specific EUROMOD outputs.

4. **`enh_RURO_prep_mnl_basic.py`**:
   - Carry `loc4` (and `loc4_male`, `loc4_female`) into the final MNL columns.
   - Compute `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)` from component columns.
   - Patch the fallback bug at the lines noted in §13.
   - Add an assertion harness that runs after every build:
     ```python
     assert (df["prior"] > 0).all()
     assert np.max(np.abs(np.log(df["prior"]) - df["log_prior"])) < 1e-8
     assert df.groupby("idhh")["chosen"].sum().eq(1).all()
     ```

5. **`reduce_mnl_columns.py`** — `loc`, `loc4`, `loc4_*`, `log_q_Occ*` must be in the retained-columns set. `lindi`, `industry`, `nace` must remain excluded at `M0`.

6. **`estimation_spec_parser.py`**:
   - Parse a new YAML block named `occupation_opportunity`, distinct from `market_opportunity` and from any future `industry_opportunity`.
   - Register `β_occ_k` parameters with bounds and initial values.
   - Reject any spec that puts the same variable in both `utility` and any `*_opportunity` block (§20).

7. **`estimation_engine.py`** and **`gamspy_estimation_vectorized.py`**:
   - Add the `O^Occ` term to the choice index, gated by `working`.
   - Use the omitted-reference dummy convention.
   - Partner-additive structure for couples.

8. **`RURO_post_estimation_styled.py`**:
   - Add an "Occupation Opportunity" section reporting `β_occ_k` with SE, t, p.
   - Add an "Observed vs Predicted Occupation Distribution" panel by group (SM / SF / CM / CF) and by `loc4` category.
   - Use the word "occupation" everywhere this layer is described; never "sector" or "industry".

9. **New YAML spec `estimation_spec_stijn_occ_M0.yaml`** in `scripts/enhanced/`, encoding §24.

10. **New diagnostics script `scripts/diagnostics/run_recovery_test_stijn_occ.py`** (stub allowed at audit time; full implementation in the patch plan).

---

## 17. Normalizations and identification restrictions

1. **Gumbel scale** normalized to 1.
2. **Reference categories**: `educM` omitted for education; one omitted occupation pin's the level of `O^Occ`.
3. **Proposal correction** applied exactly once per alternative.
4. **Non-labour income** enters preferences via `C`; not in any opportunity block.
5. **Couples**: shared `β_c`, `θ_c`; partner-specific leisure and opportunity blocks.
6. **`O^Occ` level**: only contrasts vs. the omitted occupation are identified.
7. **Identification anchors** required by exclusion restrictions in §20.

---

## 18. Parameters to estimate

`M0` parameter block.

Preferences (singles + couples):
- `β_c_sm`, `β_c_sf`, `β_c` (shared)
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
- With `loc4`: `β_occ_2`, `β_occ_3`, `β_occ_4` per gender → 12 parameters total (3 × 4 gender groups, but SM and CM share with CF/SF only if the spec marks gender-pooled; the default is gender-specific)
- With `loc` (ISCO 1-digit): `β_occ_k` for `k = 2, …, 9` per gender → 32 parameters

Total at `M0` with `loc4`: roughly 45–55 parameters depending on gender-pooling choices in the hours/wage blocks.

---

## 19. Parameters to fix or bound

- `θ_l_*`, `θ_c_*`: bounded to `[−8.0, 0.95]`. **None hard-fixed at `M0`**; in particular `θ_c_sm` must be free.
- `β_l0_*`: bounded below at `0.05` to keep MU(L) positive at the boundary.
- `σ`: bounded to `[0.1, 20.0]`.
- Soft constraints on `MU(C) > 0`, `MU(L) > 0` may be active but not tight enough to determine point estimates.

Bound-hit diagnostics: every parameter within `1e-3` of a bound at the optimum is flagged. The audit must flag any spec that hard-fixes `θ_c_sm` as non-compliant with `M0`.

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
| Non-labour income              | Yes (via `C`) | No | No | No      |

The spec parser must reject any YAML that puts the same variable in both `utility` and any opportunity block at `M0`.

---

## 21. Specification ladder

Estimate `M0` to convergence and pass the §22 gates before moving up.

| Spec | Adds vs previous                                                       | Status |
|------|------------------------------------------------------------------------|--------|
| `M0` | Baseline: `U + O^E + O^H + O^W + O^Occ − log q`, additive, `loc4`     | **Target for next estimation step** |
| `M1` | Add `β_E_educL`; add region dummies to `O^E + O^H` if variation suffices | First robustness |
| `M2` | Replace `loc4` with `loc` (ISCO 1-digit) for richer occupation         | Occupation granularity |
| `M3` | `O^W` conditional on `occ` (occupation-specific Mincer means, shared σ) | Aaberge–Colombino-style |
| `M4` | `O^H` conditional on `occ` (occupation-specific focal points, β_E)     | Aaberge–Colombino-style |
| `M5` | Optional `β_cl`, `β_ll` interactions in `U`                            | Preference flexibility |
| `M6` | Add `lindi` as a second, separate `industry_opportunity` block         | Industry robustness (§25) |
| `M7` | Job-choice / GMM branch as a separate robustness comparison            | External-branch robustness |

`M3`–`M4` are the conditional opportunity structures explicitly excluded from `M0`. `M6` introduces the industry layer.

---

## 22. Required diagnostics

Every estimation run stores in `estimation_results.json` or sidecars:

1. Optimizer status, iteration count, final gradient norm.
2. `joint_ll`, `ll_null_uniform`, `ll_null_prior_corrected`, McFadden ρ², AIC, BIC.
3. Hessian condition number; number of negative eigenvalues; smallest absolute eigenvalue.
4. SE, t, p for every estimated parameter; flag non-finite SEs.
5. Parameters within `1e-3` of a bound.
6. Poorly-identified parameters.
7. Metadata: `prior_correction_applied = true`, `prior_correction_form = "-log(prior)"`, occupation proposal source, list of opportunity layers active.
8. Observed-vs-predicted fit by group: participation, mean hours, hours histogram, wage KDE, **occupation distribution**.
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
2. For every household, draw 100 alternatives from `q` exactly as in estimation, **including `q_Occ`**.
3. Compute `V_hj⁰` using `θ⁰`, add i.i.d. Gumbel shocks, take the argmax as the synthetic chosen alternative.
4. Re-estimate `M0` from at least three starts (perturbation of `θ⁰`, neutral, random).
5. Run `R ≥ 50` Monte Carlo replications.

Pass criteria:
- Mean bias `< 10%` of the true value (or `< 0.05` absolute when true value is near 0) for every preference and opportunity coefficient.
- 95% coverage in `[0.92, 0.98]` for `β_c`, `θ_c`, `β_l0`, `θ_l`, the leading `β_occ_k`, and `β_E`.
- Convergence rate `≥ 90%`.

Until recovery passes, France `M0` estimates are **provisional**.

---

## 24. Minimum acceptable baseline specification

**Spec name:** `estimation_spec_stijn_occ_M0.yaml`
**Pipeline branch:** enhanced continuous draws (`scripts/enhanced/`).
**Sample:** France 2016 SRCV / EUROMOD-input, ~1,676 singles and ~2,577 couples, joint estimation across SM / SF / CM / CF.
**Alternatives:** 100 per household from `enh_RURO_draws.py` with occupation draws added.
**Choice index:** `V = U + O^E + O^H + O^W + O^Occ − log q`.
**Utility:** Box-Cox in `C, L`; leisure shifters `age_norm`, `age_norm²`, `n_children` (female only), `educH`. No interactions.
**`O^E + O^H`:** `β_E`, `β_pt1`, `β_pt2`, `β_ft`, `β_gsur`, `β_E_educH`.
**`O^W`:** log-normal with `β_w0`, `β_w_educL`, `β_w_educH`, `β_w_pexp`, `β_w_pexp²`, `σ`. Shared across occupations.
**`O^Occ`:** `β_occ_2`, `β_occ_3`, `β_occ_4` per gender using `loc4`. Reference `loc4 = 1` (routine-manual).
**Prior:** `−log_prior` with `log_prior = log_q_E + working · (log_q_H + log_q_W + log_q_Occ)`.
**Forbidden at `M0`:** `loc4` / `loc` in `U`, `O^H`, or `O^W`; `O^H | occ`; `O^W | occ`; `lindi`; `nace`; `industry`; `sector_*` parameters; `job_id`, `type_id`, `log_q_job`, `log_q_state`, `log_q_total`; hard-fixed `θ_c_sm`.

Reportable when (i) it converges with positive-definite Hessian and finite SEs, (ii) §23 recovery passes, (iii) seed-stability passes.

---

## 25. Later extensions, including `lindi` / NACE industry opportunity

Out of scope at `M0`, on the roadmap:

1. **Occupation-conditional hours `O^H | occ`** (`M4`): occupation-specific focal-point shifts.
2. **Occupation-conditional wage `O^W | occ`** (`M3`): occupation-specific Mincer intercepts, slopes, and possibly variance.
3. **Region opportunity** (`M1`): NUTS-1 region dummies in `O^E + O^H` or `O^Occ`.
4. **Finer occupation** (`M2`): replace `loc4` with ISCO 1-digit `loc`.
5. **Occupation preferences**: only after `M0`–`M4` are stable, allowing `loc4` shifters in `β_l` for tested identification.
6. **Industry opportunity using `lindi`** (`M6`): a separate `industry_opportunity` block based on the NACE 1-digit variable (1 Agriculture, 2 Industry, 3 Services). Implementation requirements when activated:
   - Carry `lindi` through `enh_france_data_prep.py`, `enh_RURO_prep.py`, the draw step, `enh_RURO_prep_mnl_basic.py`, and `reduce_mnl_columns.py`.
   - Draw `lindi_draw` from a documented industry proposal `q_Ind`.
   - Store `log_q_Ind`; update `log_prior` to `log_q_E + working · (log_q_H + log_q_W + log_q_Occ + log_q_Ind)`.
   - Define a new YAML block `industry_opportunity` with `β_ind_*` parameters.
   - Re-run identification gates; `lindi` is a 3-category variable, so it is parameter-cheap but adds a co-linearity risk with `loc4`. The audit at `M6` must report the correlation between `loc4` dummies and `lindi` dummies and warn if any cell is empty.
   - Industry opportunity is a **robustness** check vs. occupation, not a replacement at `M0`.
7. **Random preference coefficients** on `β_l0` or `θ_l`.
8. **Multi-year identification** using France 2021.
9. **Cross-country**: Germany, others.
10. **Job-choice / GMM branch comparison** (`M7`): use `scripts/Job_model/` for robustness after `M0`–`M2` stabilize.
11. **Welfare layer**: household AEI-style money-metric welfare, joint non-work reference, two-factor Shapley–Shorrocks decomposition. Downstream of stable `M0` and passed recovery.

---

## Implementation checklist for Claude Code (audit)

1. **Branch check.** Verify all targets live in `scripts/enhanced/`. Do not modify `scripts/Job_model/`.
2. **Column audit.** Read the schema of `fr_2016_RURO_mnl__singles.parquet` and `fr_2016_RURO_mnl__couples.parquet`. Report presence/absence of: `loc`, `loc4`, `loc_ruro`, `loc4_male`, `loc4_female`, `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`, `gsur`, `pexp`. Confirm absence of: `job_id`, `type_id`, `log_q_job`, `log_q_state`, `log_q_total`, `lindi`, `industry`, `nace`.
3. **Prior convention.** Assert `(df["prior"] > 0).all()` and `max|log(df["prior"]) − df["log_prior"]| < 1e-8` for both files. Report the exact code paths where `df["prior"] = np.log(prior_density)` is set (continuous-fallback singles ~1448–1451, couples ~1572–1575). Do not patch yet.
4. **Occupation pipeline gap.** Identify the smallest patch set in `enh_RURO_prep.py`, `enh_RURO_draws.py`, `enh_RURO_prep_mnl_basic.py`, and `reduce_mnl_columns.py` to carry `loc4` and `log_q_Occ` end-to-end. Output as `RURO_patch_plan_v3.md`.
5. **Naming sweep.** Grep `scripts/enhanced/` and `RURO_post_estimation_styled.py` for "sector" and "industry". Where they refer to `loc` / `loc4` / `isco1`, flag for rename to "occupation". Confirm no `sector_opportunity` or `industry_opportunity` block targets occupation data at `M0`.
6. **Spec parser readiness.** Inspect `estimation_spec_parser.py`. Report changes needed to register `occupation_opportunity` distinct from `market_opportunity` and from any future `industry_opportunity`.
7. **Likelihood readiness.** Inspect `estimation_engine.py` and `gamspy_estimation_vectorized.py`. Locate call sites for `O^H`, `O^W`; propose insertion for `O^Occ`. Verify the prior correction is subtracted exactly once.
8. **Exclusion restrictions.** Parse all active `scripts/enhanced/estimation_spec*.yaml`. Report any variable appearing in both `utility` and any `*_opportunity` block per §20.
9. **`θ_c_sm` audit.** Flag any YAML hard-fixing `theta_c_sm`.
10. **Cross-engine consistency.** Locate or scaffold a `joint_ll` comparison script (GAMSPy vectorized vs NumPy/SciPy) at a fixed `θ` after `O^Occ` is added.
11. **Recovery harness.** Verify or scaffold `scripts/diagnostics/run_recovery_test_stijn_occ.py`. Do not run; verify entry point.
12. **`lindi` watch.** Verify that no `M0` artefact references `lindi`, `industry`, or `nace`. Add a single comment in `reduce_mnl_columns.py` noting that `lindi` is reserved for the `M6` industry-opportunity extension.
13. **Audit report.** Emit `RURO_code_contract_audit_v3.md`. For each section §1–§25, status `PASS` / `FAIL` / `PARTIAL` / `N/A`, with file and line references and the minimal patch needed. Do not apply patches in the audit step; collect them in `RURO_patch_plan_v3.md`.

---

**Save this contract as `RURO_model_spec_contract_v3_stijn_occ.md`** in the project root or `docs/`. Use it as input to the next Claude Code task: produce `RURO_code_contract_audit_v3.md` against the current `scripts/enhanced/` codebase. The patch plan is a separate step.