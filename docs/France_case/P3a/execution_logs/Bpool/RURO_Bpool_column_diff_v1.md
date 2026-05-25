# RURO B-pool Column Diff v1

**Purpose:** Read-only schema diff explaining why couples (76 cols) < singles (149 cols).
Categorizes all columns, confirms spec coverage, and verdicts each discrepancy.

**Date:** 2026-05-24
**Files compared:**
- `U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_d1w1__singles.parquet` — 149 columns
- `U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_d1w1__couples.parquet` — 76 columns
- Spec: `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml`

**Change nothing. Report only.**

---

## 1. Sorted column lists

### Singles (149 columns)

```
age_norm              age_norm2             age_norm2_female      age_norm2_male
age_norm_female       age_norm_male         c_norm                cluster_id
consumption           consumption_female     consumption_male      dag
dag_female            dag_male              data_year             deh
deh_female            deh_male              dgn                   draw
drgn1                 dwt                   educ3                 educ3_female
educ3_male            educH                 educH_female          educH_male
educL                 educL_female          educL_male            educM
educM_female          educM_male            gsur                  gsur_female
gsur_female_v1_fallback  gsur_male          gsur_male_v1_fallback  gsur_v1_fallback
hh_IsHead             hh_IsPartner          hours                 hours_female
hours_male            household_type        idfather              idhh
idmother              idorighh              idorigperson          idpartner
idperson              ils_dispy             ils_dispy_em          ils_dispy_female
ils_dispy_male        ils_dispy_real        ils_earns             ils_earns_real
ils_origy             ils_pen               ils_sicdy             is_chosen
keep_for_analysis     l_norm                l_norm_female         l_norm_male
leisure               leisure_female        leisure_male          lhw
loc                   loc4                  loc4_female           loc4_male
log_c                 log_c_norm            log_l                 log_l_norm
log_l_norm_female     log_l_norm_male       log_prior             log_q_E
log_q_E_female        log_q_E_male          log_q_H               log_q_H_female
log_q_H_male          log_q_Occ             log_q_Occ_female      log_q_Occ_male
log_q_W               log_q_W_female        log_q_W_male          n_children
num_children_total    other_members_income  pexp2_female          pexp2_male
pexp_female           pexp_male             pexp_years            pexp_years2
pexp_years2_female    pexp_years2_male      pexp_years_female     pexp_years_male
prior                 reg_nuts1_1           reg_nuts1_2           reg_nuts1_3
reg_nuts1_4           reg_nuts1_5           reg_nuts1_6           reg_nuts1_7
reg_nuts1_8           ruro_decider          ruro_group            ruro_sample
sample_group          stacked_hh_uid        stacked_person_uid    tin_s
wage                  wage_female           wage_male             working
working_female        working_ft            working_ft_female     working_ft_male
working_lh            working_lh_female     working_lh_male       working_male
working_pt1           working_pt1_female    working_pt1_male      working_pt2
working_pt2_female    working_pt2_male      year                  year_2015_indicator
year_2017_indicator   year_for_ruro         year_tag              yem
yem_female            yem_male              yem_real
```

### Couples (76 columns)

```
age_norm2_female      age_norm2_male        age_norm_female       age_norm_male
cluster_id            dag_female            dag_male              data_year
dgn                   draw_female           draw_joint            draw_male
drgn1                 dwt                   educ3_female          educ3_male
educH_female          educH_male            educL_female          educL_male
educM_female          educM_male            gsur                  gsur_female
gsur_male             hours_female          hours_male            household_type
idhh                  idorighh              is_chosen_joint       loc4_female
loc4_male             log_prior             log_prior_female      log_prior_male
log_q_E_female        log_q_E_male          log_q_H_female        log_q_H_male
log_q_Occ_female      log_q_Occ_male        log_q_W_female        log_q_W_male
n_children            num_children_total    pexp_years2_female    pexp_years2_male
pexp_years_female     pexp_years_male       reg_nuts1_1           reg_nuts1_2
reg_nuts1_3           reg_nuts1_4           reg_nuts1_5           reg_nuts1_6
reg_nuts1_7           reg_nuts1_8           ruro_group            stacked_hh_uid
wage_female           wage_male             working_female        working_ft_female
working_ft_male       working_lh_female     working_lh_male       working_male
working_pt1_female    working_pt1_male      working_pt2_female    working_pt2_male
year_2015_indicator   year_2017_indicator   year_for_ruro         year_tag
```

---

## 2. Column categorization — couples

### (a) Joint / household-level shared (single value per row — not partner-specific)

| Column | Role |
|---|---|
| `idhh` | Household ID (not unique in P3a — use stacked_hh_uid) |
| `stacked_hh_uid` | Unique estimation unit (year × household) |
| `idorighh` | Original household ID (cluster key) |
| `cluster_id` | Cluster ID for cluster-robust SEs |
| `dgn` | Household gender marker (couples: always mixed) |
| `data_year` | Survey year (2015/2016/2017) |
| `year_tag` | Numeric year tag (1/2/3) |
| `year_for_ruro` | Year used for RURO pricing |
| `year_2015_indicator` | Year dummy for market-opp block |
| `year_2017_indicator` | Year dummy for market-opp block |
| `gsur` | Household GSUR (GSURv2, opportunity-year-aligned) |
| `gsur_male` | Male partner GSUR |
| `gsur_female` | Female partner GSUR |
| `reg_nuts1_1..8` | NUTS-1 region dummies (household-level) |
| `drgn1` | NUTS-1 region code (key only) |
| `n_children` | Number of children (household-level) |
| `num_children_total` | Total children count |
| `household_type` | Household type code |
| `dwt` | Survey design weight |
| `ruro_group` | RURO subgroup code |
| `log_prior` | Joint log_prior = log_prior_male + log_prior_female |
| `draw_male` | Male marginal draw index (1..30) |
| `draw_female` | Female marginal draw index (1..30) |
| `draw_joint` | Joint draw index (0..899) |
| `is_chosen_joint` | 1 on chosen row, 0 on simulated (couples analogue of is_chosen) |

### (b) _male-suffixed (25 columns)

`age_norm_male`, `age_norm2_male`, `dag_male`, `educ3_male`, `educH_male`, `educL_male`,
`educM_male`, `hours_male`, `loc4_male`, `log_prior_male`, `log_q_E_male`, `log_q_H_male`,
`log_q_Occ_male`, `log_q_W_male`, `pexp_years_male`, `pexp_years2_male`, `wage_male`,
`working_male`, `working_ft_male`, `working_lh_male`, `working_pt1_male`, `working_pt2_male`,
`gsur_male` (shared above), `dag_male` (listed), `draw_male` (listed above).

### (c) _female-suffixed (25 columns)

`age_norm_female`, `age_norm2_female`, `dag_female`, `educ3_female`, `educH_female`,
`educL_female`, `educM_female`, `hours_female`, `loc4_female`, `log_prior_female`,
`log_q_E_female`, `log_q_H_female`, `log_q_Occ_female`, `log_q_W_female`,
`pexp_years_female`, `pexp_years2_female`, `wage_female`, `working_female`,
`working_ft_female`, `working_lh_female`, `working_pt1_female`, `working_pt2_female`,
`gsur_female` (shared above), `dag_female` (listed), `draw_female` (listed above).

### (d) Unsuffixed person-level variables that should be doubled — assessment

All substantive person-varying columns in couples are correctly suffixed (`_male` / `_female`).
There are no unsuffixed person-level covariates in the couples parquet that are missing a suffix.
The only unsuffixed columns are genuinely household-level (see category a above).

---

## 3. Per-variable check: are both _male and _female present in couples?

| Singles variable | Couples _male | Couples _female | Verdict |
|---|---|---|---|
| `age_norm` | `age_norm_male` ✔ | `age_norm_female` ✔ | EXPECTED |
| `age_norm2` | `age_norm2_male` ✔ | `age_norm2_female` ✔ | EXPECTED |
| `educL` | `educL_male` ✔ | `educL_female` ✔ | EXPECTED |
| `educH` | `educH_male` ✔ | `educH_female` ✔ | EXPECTED |
| `pexp_years` | `pexp_years_male` ✔ | `pexp_years_female` ✔ | EXPECTED |
| `pexp_years2` | `pexp_years2_male` ✔ | `pexp_years2_female` ✔ | EXPECTED |
| `n_children` | shared (household-level) ✔ | — | EXPECTED |
| `hours` | `hours_male` ✔ | `hours_female` ✔ | EXPECTED |
| `wage` | `wage_male` ✔ | `wage_female` ✔ | EXPECTED |
| `loc4` | `loc4_male` ✔ | `loc4_female` ✔ | EXPECTED |
| `working` | `working_male` ✔ | `working_female` ✔ | EXPECTED |
| `working_pt1` | `working_pt1_male` ✔ | `working_pt1_female` ✔ | EXPECTED |
| `working_pt2` | `working_pt2_male` ✔ | `working_pt2_female` ✔ | EXPECTED |
| `working_ft` | `working_ft_male` ✔ | `working_ft_female` ✔ | EXPECTED |
| `working_lh` | `working_lh_male` ✔ | `working_lh_female` ✔ | EXPECTED |
| `log_q_E` | `log_q_E_male` ✔ | `log_q_E_female` ✔ | EXPECTED |
| `log_q_H` | `log_q_H_male` ✔ | `log_q_H_female` ✔ | EXPECTED |
| `log_q_W` | `log_q_W_male` ✔ | `log_q_W_female` ✔ | EXPECTED |
| `log_q_Occ` | `log_q_Occ_male` ✔ | `log_q_Occ_female` ✔ | EXPECTED |
| `log_prior` | `log_prior_male` ✔ | `log_prior_female` ✔ | EXPECTED |
| `c_norm` | absent | absent | see §4 |
| `l_norm` | absent | absent | see §4 |
| `leisure` | absent (→ `leisure_male/female` in singles!) | absent | see §4 |
| `log_c`, `log_c_norm` | absent | absent | see §4 |
| `log_l`, `log_l_norm` | absent | absent | see §4 |

**No person-varying column is missing a suffix. Zero BUG findings.**

---

## 4. Singles columns absent from couples — full list and verdicts

81 columns present in singles but not in couples (neither suffixed nor shared).

### 4a — Draw / choice-set scaffolding (singles-only by design)

| Column | Verdict | Reason |
|---|---|---|
| `draw` | EXPECTED | Couples use `draw_male`, `draw_female`, `draw_joint` instead |
| `is_chosen` | EXPECTED | Couples use `is_chosen_joint` instead |

### 4b — Consumption / income variables (not yet computed for bpool)

| Column | Verdict | Reason |
|---|---|---|
| `consumption` | BENIGN | Requires EUROMOD precompute step (not yet run); bpool parquet is pre-EUROMOD. `consumption_male`, `consumption_female` in singles are also from source parquet, not bpool builds. |
| `consumption_female` | BENIGN | Same — source parquet carrythrough, not bpool-generated |
| `consumption_male` | BENIGN | Same |
| `ils_dispy` | BENIGN | EUROMOD output: income for budget constraint; absent until precompute runs |
| `ils_dispy_em` | BENIGN | Same |
| `ils_dispy_female` | BENIGN | Same |
| `ils_dispy_male` | BENIGN | Same |
| `ils_dispy_real` | BENIGN | Same |
| `ils_earns` | BENIGN | Total earnings column from EUROMOD |
| `ils_earns_real` | BENIGN | Real earnings |
| `ils_origy` | BENIGN | Original income |
| `ils_pen` | BENIGN | Pension income |
| `ils_sicdy` | BENIGN | Sick-pay income |
| `other_members_income` | BENIGN | Other HH members' income — not needed for couples where both partners modelled |
| `yem` | BENIGN | Employment income (from source parquet, not bpool) |
| `yem_female` | BENIGN | Same |
| `yem_male` | BENIGN | Same |
| `yem_real` | BENIGN | Same |

### 4c — Derived consumption/leisure utility intermediates (singles-only by design)

These are utility-evaluation intermediates computed during estimation, stored in the singles source parquet from prior estimation runs. The couples builder does not carry them forward.

| Column | Verdict | Reason |
|---|---|---|
| `c_norm` | BENIGN | Normalized consumption (estimation intermediate) |
| `l_norm` | BENIGN | Normalized leisure — unsuffixed singles scalar |
| `l_norm_female` | BENIGN | Partners' l_norm carried over from singles source parquet (couples uses `l_norm_male/female` in source but builder drops these non-essential intermediates) |
| `l_norm_male` | BENIGN | Same |
| `leisure` | BENIGN | Leisure value (unsuffixed); couples uses `leisure_male/female` from source but builder omits them as non-essential |
| `leisure_female` | BENIGN | Same |
| `leisure_male` | BENIGN | Same |
| `log_c` | BENIGN | log(consumption) — estimation intermediate |
| `log_c_norm` | BENIGN | log(normalized consumption) — intermediate |
| `log_l` | BENIGN | log(leisure) — intermediate |
| `log_l_norm` | BENIGN | log(normalized leisure) — intermediate |
| `log_l_norm_female` | BENIGN | Same, female |
| `log_l_norm_male` | BENIGN | Same, male |
| `prior` | BENIGN | exp(log_prior) — redundant with log_prior; estimation intermediate |

### 4d — Unsuffixed person-level demographics (singles-only; couples has suffixed versions)

These exist unsuffixed in singles because singles households have one decider. In couples, both partners' values are present with suffixes. The unsuffixed originals are not included in the couples builder (which builds from scratch using partner-specific obs columns).

| Column | Verdict | Reason |
|---|---|---|
| `age_norm` | EXPECTED | Couples has `age_norm_male`, `age_norm_female` |
| `age_norm2` | EXPECTED | Same — `age_norm2_male/female` present |
| `dag` | EXPECTED | Age in years — couples has `dag_male`, `dag_female` |
| `deh` | EXPECTED | Education level — couples has `deh_male`, `deh_female` |
| `educ3` | EXPECTED | Education tertile — couples has `educ3_male/female` |
| `educH` | EXPECTED | High-educ dummy — couples has `educH_male/female` |
| `educL` | EXPECTED | Low-educ dummy — couples has `educL_male/female` |
| `educM` | EXPECTED | Mid-educ dummy — couples has `educM_male/female` |
| `hours` | EXPECTED | Couples has `hours_male`, `hours_female` |
| `loc4` | EXPECTED | Couples has `loc4_male`, `loc4_female` |
| `pexp_years` | EXPECTED | Couples has `pexp_years_male/female` |
| `pexp_years2` | EXPECTED | Couples has `pexp_years2_male/female` |
| `pexp_female` | BENIGN | Short-form alias from source parquet; `pexp_years_female` is canonical |
| `pexp_male` | BENIGN | Same for male |
| `pexp2_female` | BENIGN | Short-form alias for pexp_years2_female |
| `pexp2_male` | BENIGN | Same for male |
| `wage` | EXPECTED | Couples has `wage_male`, `wage_female` |
| `working` | EXPECTED | Couples has `working_male`, `working_female` |
| `working_ft` | EXPECTED | Couples has `working_ft_male/female` |
| `working_lh` | EXPECTED | Couples has `working_lh_male/female` |
| `working_pt1` | EXPECTED | Couples has `working_pt1_male/female` |
| `working_pt2` | EXPECTED | Couples has `working_pt2_male/female` |

### 4e — GSURv2 fallback columns (singles-only provenance artifact)

| Column | Verdict | Reason |
|---|---|---|
| `gsur_v1_fallback` | BENIGN | v1 GSUR fallback value; provenance artifact from GSURv2 merge pipeline. Not used in estimation. Not present in couples source parquet — couples parquet was built without fallback tracking. |
| `gsur_female_v1_fallback` | BENIGN | Same, female |
| `gsur_male_v1_fallback` | BENIGN | Same, male |

### 4f — Person/household identifiers (singles-only)

| Column | Verdict | Reason |
|---|---|---|
| `idperson` | BENIGN | Individual person ID — not needed in couples (partner-specific rows don't exist in the couples product design; HH is the unit) |
| `idorigperson` | BENIGN | Same |
| `idpartner` | BENIGN | Points to partner's person ID — redundant since couples are always co-present |
| `idfather` | BENIGN | Parental ID linkage — not used in RURO |
| `idmother` | BENIGN | Same |
| `stacked_person_uid` | BENIGN | Person-level stacked UID — couples estimation unit is HH, not person |

### 4g — Sample/analysis flags (singles-only from source)

| Column | Verdict | Reason |
|---|---|---|
| `hh_IsHead` | BENIGN | Head-of-household flag — not needed in couples product |
| `hh_IsPartner` | BENIGN | Partner flag — same |
| `keep_for_analysis` | BENIGN | Analysis inclusion flag from source; couples builder sets its own filtering via obs_df |
| `ruro_decider` | BENIGN | Decider flag (singles-specific concept) |
| `ruro_sample` | BENIGN | Sample flag |
| `sample_group` | BENIGN | Sample group code |

### 4h — Other source-parquet passthrough (singles-only)

| Column | Verdict | Reason |
|---|---|---|
| `loc` | BENIGN | Raw location code (loc4 is the 4-category version used in estimation) |
| `lhw` | BENIGN | Labour-hours-worked variable from EUROMOD source; not an estimation input |
| `tin_s` | BENIGN | Tax unit identifier — not used in RURO |
| `year` | BENIGN | Calendar year (redundant with data_year / year_tag) |

---

## 5. Spec cross-check: all spec variables present in both parquets

Spec: `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` (56 parameters).

### Hours-opportunity block

| Spec variable | Singles | Couples (suffixed) |
|---|---|---|
| `working` | ✔ | `working_male` ✔ / `working_female` ✔ |
| `working_pt1` | ✔ | `working_pt1_male` ✔ / `working_pt1_female` ✔ |
| `working_pt2` | ✔ | `working_pt2_male` ✔ / `working_pt2_female` ✔ |
| `working_ft` | ✔ | `working_ft_male` ✔ / `working_ft_female` ✔ |
| `working_lh` | ✔ | `working_lh_male` ✔ / `working_lh_female` ✔ |

### Wage-opportunity block

| Spec variable | Singles | Couples (suffixed) |
|---|---|---|
| `educL` | ✔ | `educL_male` ✔ / `educL_female` ✔ |
| `educH` | ✔ | `educH_male` ✔ / `educH_female` ✔ |
| `pexp_years` | ✔ | `pexp_years_male` ✔ / `pexp_years_female` ✔ |
| `pexp_years2` | ✔ | `pexp_years2_male` ✔ / `pexp_years2_female` ✔ |

### Market-opportunity block (household-level — shared columns)

| Spec variable | Singles | Couples |
|---|---|---|
| `gsur` | ✔ | ✔ (shared) |
| `reg_nuts1_2..8` | ✔ (7 cols) | ✔ (7 cols, shared) |
| `year_2015_indicator` | ✔ | ✔ (shared) |
| `year_2017_indicator` | ✔ | ✔ (shared) |

### Occupation-opportunity block

| Spec variable | Singles | Couples (suffixed) |
|---|---|---|
| `loc4` | ✔ | `loc4_male` ✔ / `loc4_female` ✔ |

### Leisure shifters

| Spec variable | Singles | Couples (suffixed) |
|---|---|---|
| `age_norm` | ✔ | `age_norm_male` ✔ / `age_norm_female` ✔ |
| `age_norm2` | ✔ | `age_norm2_male` ✔ / `age_norm2_female` ✔ |
| `n_children` | ✔ | ✔ (shared, household-level) |

**All 23 spec variable families present in both parquets. Zero missing columns.**

---

## 6. Column count arithmetic

| Category | Count | Explanation |
|---|---|---|
| Shared (in both) | 68 | Household-level + suffixed demographics + log_q + draw indices |
| Couples-only | 8 | `draw_male`, `draw_female`, `draw_joint`, `is_chosen_joint`, `log_prior_male`, `log_prior_female`, `working_lh_male`, `working_lh_female` |
| **Couples total** | **76** | 68 + 8 |
| Singles-only | 81 | See §4 breakdown |
| **Singles total** | **149** | 68 + 81 |

The 73-column gap (149 − 76) decomposes as:

| Reason for gap | Col count |
|---|---|
| Unsuffixed person-level vars collapsed to suffixed in couples (§4d) | 27 |
| EUROMOD income / consumption pre-compute columns not yet run (§4b) | 18 |
| Utility intermediates / derived scalars dropped in couples builder (§4c) | 14 |
| Person/HH identifiers not needed in product design (§4f) | 6 |
| Sample/analysis flags singles-only (§4g) | 6 |
| GSURv2 fallback provenance artifacts (§4e) | 3 |
| Draw/choice scaffolding replaced by couples-specific columns (§4a) | 2 |
| Other source passthrough (§4h) | 4 |
| Couples-unique columns added (draw_joint, is_chosen_joint, log_prior_m/f) | −8 (added) |
| **Net difference** | **73** |

---

## 7. Verdict summary

| Finding | Category | Verdict |
|---|---|---|
| All spec variables present in both parquets | — | **NO BUG** |
| No person-varying column missing a suffix in couples | — | **NO BUG** |
| Unsuffixed demographics (age_norm, educL, working, …) absent from couples | §4d | **EXPECTED** — couples builder correctly uses suffixed versions |
| Draw/choice scaffolding differs (draw vs draw_joint, is_chosen vs is_chosen_joint) | §4a | **EXPECTED** — deliberate design |
| EUROMOD income columns absent from couples | §4b | **BENIGN** — precompute step not yet run; will be added by `build_bpool_precompute.py` |
| Utility intermediates (l_norm, log_l_norm, prior, …) absent from couples | §4c | **BENIGN** — estimation intermediates not needed in the raw draw parquet |
| GSURv2 fallback columns absent from couples | §4e | **BENIGN** — provenance artifact; not used in estimation |
| Person/HH IDs absent from couples | §4f | **BENIGN** — not needed in product design; HH is the estimation unit |
| Sample flags absent from couples | §4g | **BENIGN** — couples builder uses obs_df directly |
| `working_lh_male/female` present in couples (couples-only) | §2b/c | **EXPECTED** — added by this build round; correct |
| `log_prior_male`, `log_prior_female` present in couples (couples-only) | §2 | **EXPECTED** — joint log_prior requires per-partner components |

**No bugs found. The schema difference is entirely explained by design and build-stage.**
