# RURO Continuous-MNL Variable Dictionary v1

**Purpose:** one place for the variable meanings used by the continuous RURO
MNL files and occupation-opportunity specifications. This complements the
EUROMOD reference files, which document EUROMOD inputs and outputs. The
variables below include both EUROMOD variables carried into RURO and
RURO-derived variables created by the project pipeline.

**Current empirical target:** France 2016 continuous RURO files:

```text
fr_2016_RURO_mnl__singles.parquet
fr_2016_RURO_mnl__couples.parquet
```

For exact EUROMOD input labels, derivations, min/max values, and weighted
summary statistics, use:

```text
docs/euromod_reference/euromod_fr_2015_2017_input_variables.csv
docs/euromod_reference/euromod_fr_2015_2017_input_output_reference.md
```

---

## 1. Source-Code Convention

| variable | origin | meaning / coding |
| --- | --- | --- |
| `dgn` | EUROMOD input | Gender: `0 = female`, `1 = male`. This comes from the EUROMOD DRD label `DEMOGRAPHIC : Gender 0: Female 1: Male`; derivation `dgn = rb090 recode dgn (2=0)`. |
| `dag` | EUROMOD input | Age in years. |
| `dwt` | EUROMOD input | Household/person weight from EUROMOD/SILC input. Estimation diagnostics in this project are usually unweighted unless explicitly stated. |
| `idhh` | EUROMOD/RURO | Household identifier used by the MNL long files. Each household has one choice set. |
| `idperson` | EUROMOD/RURO | Person identifier when person-level rows are present upstream. |
| `deh` | EUROMOD input | Highest education status: `0 = not completed primary`, `1 = primary`, `2 = lower secondary`, `3 = upper secondary`, `4 = post-secondary`, `5 = tertiary`. |
| `les` | EUROMOD input | Self-declared economic status. EUROMOD label: `0 = pre-school`, `1 = farmer`, `2 = employer/self-employed`, `3 = employee`, `4 = pensioner`, `5 = unemployed`, `6 = student`, `7 = inactive`, `8 = sick/disabled`, `9 = other`. |
| `lhw` | EUROMOD input / RURO upstream | Usual hours worked per week in main and additional jobs. |
| `yem` | EUROMOD input | Gross employee income. |
| `yse` | EUROMOD input | Self-employment income. |
| `loc` | EUROMOD input | Occupation, ISCO 1-digit style: `0 = armed forces`, `1 = managers/senior officials`, `2 = professionals`, `3 = technicians`, `4 = clerks`, `5 = service/sales`, `6 = skilled agricultural`, `7 = craft/trades`, `8 = plant/machine operators`, `9 = elementary`, `-1 = not applicable`. |
| `lindi` | EUROMOD input | Industry / NACE code. It is not an occupation variable. It is deliberately not active in the M0 occupation-opportunity MNL files. |
| `ils_dispy` | EUROMOD output | Standardized disposable income. In the EUROMOD reference: `ils_dispy = ils_origy + ils_ben - ils_sicdy - ils_tax`. RURO consumption is built from disposable income after EUROMOD is run on alternatives. |

---

## 2. RURO Group Conventions

| RURO group | rows / columns | coding |
| --- | --- | --- |
| `singles_male` / `sm` | singles parquet | `dgn == 1` |
| `singles_female` / `sf` | singles parquet | `dgn == 0` |
| `couples_male` / `cm` | couples parquet | male-suffixed columns such as `hours_male`, `wage_male`, `loc4_male` |
| `couples_female` / `cf` | couples parquet | female-suffixed columns such as `hours_female`, `wage_female`, `loc4_female` |

Do not reverse the `dgn` mapping. It is fixed by the EUROMOD input
documentation and by the final MNL sample counts used in diagnostics:

```text
dgn == 1 -> singles_male
dgn == 0 -> singles_female
```

---

## 3. Choice-Set Structure

| variable | singles | couples | meaning / invariant |
| --- | --- | --- | --- |
| `idhh` | yes | yes | Choice-set identifier. Each `idhh` should have exactly 100 alternatives in current France 2016 MNL files. |
| `draw` | often present upstream | often present upstream | Alternative/draw identifier. `draw = 0` is the observed alternative when present. |
| `is_chosen` | yes | yes | Chosen alternative indicator. Exactly one row per `idhh` must have `is_chosen == 1`. |
| `chosen` | fallback | fallback | Older name for `is_chosen`. |
| `prior` | yes | yes | Proposal density, strictly positive. This is a density/probability value, not a log. |
| `log_prior` | yes | yes | `log(prior)`. Must equal the sum of proposal-component aliases described below. |

---

## 4. Hours, Wages, Work, Consumption, and Leisure

| variable | singles | couples | meaning / coding |
| --- | --- | --- | --- |
| `hours` | yes | no | Weekly hours for the singles alternative. |
| `hours_male`, `hours_female` | no | yes | Partner-specific weekly hours for couples. |
| `wage` | yes | no | Hourly wage for the singles alternative, positive on working alternatives. |
| `wage_male`, `wage_female` | no | yes | Partner-specific hourly wage for couples, positive for the working partner alternative. |
| `working` | yes | no | Binary indicator: `1` if `hours > 0`, else `0`. |
| `working_male`, `working_female` | no | yes | Partner-specific binary indicators: `1` if partner hours are positive, else `0`. |
| `working_pt1` | yes | no | Focal part-time-1 hours indicator, approximately the 20-hour band used by the spec. |
| `working_pt2` | yes | no | Focal part-time-2 hours indicator, approximately the 30-hour band used by the spec. |
| `working_ft` | yes | no | Focal full-time hours indicator, approximately the 38-40 hour band used by the spec. |
| `working_pt1_male`, `working_pt1_female` | no | yes | Partner-specific part-time-1 focal indicators. |
| `working_pt2_male`, `working_pt2_female` | no | yes | Partner-specific part-time-2 focal indicators. |
| `working_ft_male`, `working_ft_female` | no | yes | Partner-specific full-time focal indicators. |
| `consumption` | yes | yes | Normalized household consumption argument in utility, built from EUROMOD disposable income after running EUROMOD on each alternative. In couples, consumption is household-level and shared across partners. |
| `leisure` | yes | no | Singles leisure argument, constructed from total available time minus hours. |
| `leisure_male`, `leisure_female` | no | yes | Partner-specific leisure arguments for couples. |

The estimation utility uses the normalized `consumption` and `leisure` columns
stored in the MNL files. Raw disposable income is upstream evidence; the MNL
utility argument is the processed/normalized value.

---

## 5. Education, Age, Children, Experience, and GSUR

| variable | meaning |
| --- | --- |
| `educL`, `educM`, `educH` | RURO education dummies derived from education status. `educH` is high education. |
| `educ3` | Three-category education code used for GSUR/strata lookups. |
| `age_norm` | Demeaned/normalized age used as a leisure shifter. |
| `age_norm2` | Square of `age_norm`. |
| `n_children` | Number of dependent children. In couples this is a household-level count; partner-suffixed variants may not exist. |
| `pexp_years`, `pexp_years2` | Potential/constructed experience and its square, used in wage-opportunity equations. |
| `gsur` | Group-specific unemployment-rate shifter from the external GSUR lookup. |
| `gsur_male`, `gsur_female` | Partner-specific GSUR values for couples. |

These are RURO pipeline variables, not EUROMOD input variables. Their exact
construction is documented by the RURO prep scripts and pipeline manuals, not
by the EUROMOD DRD workbook.

---

## 6. Occupation Variables

### 6.1 EUROMOD `loc`

`loc` is the original occupation coding carried from EUROMOD/SILC. It is
ISCO 1-digit style and has more categories than the M0 occupation model uses.

### 6.2 RURO `loc4`

`loc4` is a four-task collapse used by the occupation-opportunity M0 family.
It is a RURO project variable derived from `loc`/occupation information, not a
native EUROMOD code.

| value | meaning in RURO occupation-opportunity M0 |
| --- | --- |
| `-2` | Unknown-worker sentinel. The observed row is working but occupation cannot be classified. This is not an occupation category. |
| `-1` | Non-worker / non-work alternative sentinel. Occupation opportunity is gated off by `working == 0`. |
| `1` | Routine-manual reference group. This category is omitted from `O^Occ` at M0. |
| `2` | Nonroutine-manual. |
| `3` | Routine-cognitive. |
| `4` | Nonroutine-cognitive. |

M0 estimates occupation opportunity with dummies for `loc4 = 2`, `loc4 = 3`,
and `loc4 = 4`, using `loc4 = 1` as the reference. Therefore:

- `loc4 = -1` contributes zero because `working == 0`;
- `loc4 = -2` contributes zero because it is not one of the estimated dummies;
- simulated working alternatives should draw valid `loc4` values in
  `{1, 2, 3, 4}`;
- if many simulated working alternatives have `loc4 = -2`, the occupation
  draw pipeline is wrong.

Couples use:

```text
loc4_male
loc4_female
```

with the same coding.

Derived dummy columns such as `loc4_2`, `loc4_3`, `loc4_4` may be materialized
or computed lazily by the estimation/precompute layer. The M0 reference
category is always `loc4 = 1`.

---

## 7. Proposal-Density Component Aliases

The final MNL files for the continuous RURO occupation branch should carry
proposal-density components in explicit layers.

### Singles

| variable | meaning |
| --- | --- |
| `log_q_E` | Employment/non-employment proposal component. |
| `log_q_H` | Hours proposal component, active only for working alternatives. |
| `log_q_W` | Wage proposal component, active only for working alternatives. |
| `log_q_Occ` | Occupation proposal component, active only for working alternatives. |

Required invariant:

```text
log_prior = log_q_E + working * (log_q_H + log_q_W + log_q_Occ)
```

### Couples

| variable | meaning |
| --- | --- |
| `log_q_E_male`, `log_q_E_female` | Partner-specific employment proposal components. |
| `log_q_H_male`, `log_q_H_female` | Partner-specific hours proposal components. |
| `log_q_W_male`, `log_q_W_female` | Partner-specific wage proposal components. |
| `log_q_Occ_male`, `log_q_Occ_female` | Partner-specific occupation proposal components. |

Required invariant:

```text
log_prior =
    log_q_E_male
  + working_male   * (log_q_H_male   + log_q_W_male   + log_q_Occ_male)
  + log_q_E_female
  + working_female * (log_q_H_female + log_q_W_female + log_q_Occ_female)
```

Non-work alternatives must have zero hours, wage, and occupation proposal
contributions after the employment component is accounted for.

---

## 8. Variables Deliberately Not Active In M0

The following may exist upstream but must not be active in the final M0
occupation-opportunity MNL artifacts:

| variable | reason |
| --- | --- |
| `lindi`, `industry`, `nace` | Industry/NACE variables are not occupation. They are reserved for later industry-opportunity robustness models, not M0 occupation opportunity. |
| `job_id`, `type_id` | Job-choice branch artifacts. They are not part of the continuous M0 occupation model. |
| `hours_bin`, `wage_bin` | Job-choice/discretized artifacts. Continuous M0 uses continuous hours and wage draws plus focal indicators. |
| `log_q_job` | Job-choice proposal component. |
| `log_q_state`, `log_q_total` | Raw or legacy proposal names. Final M0 uses explicit aliases `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` and `log_prior`. |

---

## 9. Documentation Boundary

Use this rule when adding or checking variables:

- **EUROMOD input/output variable:** document exact source label and derivation
  in `docs/euromod_reference/`.
- **RURO pipeline variable:** document construction and coding here and in the
  relevant RURO spec/pipeline report.
- **Model parameter:** document in the YAML specification and in the model
  implementation report.

This prevents future code or prompt work from guessing whether a variable such
as `dgn`, `loc4`, `working`, or `log_q_Occ` is an EUROMOD source variable or a
RURO-derived estimation artifact.
