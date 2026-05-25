# RURO France 2016 Continuous Data-Build Audit v1

Date: 2026-05-17

## 1. Purpose

This memo reconstructs the active France 2016 **continuous RURO** data build
from the first raw-file read to the final MNL parquets used by estimation.
It answers four questions:

1. What data are read, transformed, excluded, and retained at each stage?
2. What is the economic or technical reason for each restriction?
3. Does the current code implement the stated rule correctly?
4. Which older documents are still useful, and which statements are now stale?

This is an audit of the active enhanced pipeline, not the archived legacy
pipeline and not the job-choice branch.

## 2. Bottom Line

The active data build is **substantively coherent and mostly well implemented**.
The main logic is correct:

- the sample is selected before simulated draws are created;
- non-deciders are retained through EUROMOD so household disposable income is
  computed correctly, then removed from the final estimation rows;
- the final MNL files have the expected household choice-set structure;
- couples are represented as one household choice over paired male/female
  labour-supply alternatives, with partner-specific hours/wages/leisure and
  shared household consumption.

The main weaknesses are documentation and one live data-side issue:

- the documentation is fragmented across several files rather than collected
  in one current canonical build note;
- `docs/France_case/P3a/design/FR2016_RURO_pipeline_report.md` is a legacy narrative and no longer
  matches the current enhanced pipeline;
- `docs/specifications/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md` still says the estimator
  uses normalized `consumption`/`leisure`, while the active estimator uses the
  raw `consumption` and `leisure` columns;
- the current GSUR merge is mechanically exact but not yet semantically safe,
  because the live `drgn1` coding and the GSUR lookup region coding are not yet
  aligned. This is already documented in
  `docs/France_case/_shared/gsur/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` and
  `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md`.

## 3. Canonical Active Pipeline

The active continuous branch is defined in `docs/PIPELINE_ENTRYPOINTS.md` and
implemented by:

| stage | active script | main output |
| --- | --- | --- |
| 1. Raw cleaning and household sample selection | `scripts/enhanced/enh_france_data_prep.py` | `fr_2016.parquet`, `fr_2016_singles.parquet`, `fr_2016_couples.parquet` |
| 2. RURO covariate construction | `scripts/enhanced/enh_RURO_prep.py` | `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet` |
| 3. Opportunity draws | `scripts/enhanced/enh_RURO_draws.py` | `*_RURO_ready_RURO_draws.parquet` |
| 4. EUROMOD on alternatives | `scripts/enhanced/enh_RURO_euromod.py` | `combined_draws_em.parquet` |
| 5. GSUR preparation | `scripts/enhanced/enh_prepare_FR_gsur.py` | `FR_gsur_ruro.parquet` |
| 6. Final MNL assembly | `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | `fr_2016_RURO_mnl__singles.parquet`, `fr_2016_RURO_mnl__couples.parquet` |
| 7. Estimation input | `scripts/enhanced/enh_RURO_estimate_FR.py` | consumes the two final MNL parquets |

Current realized France 2016 artifact counts:

| artifact | rows | columns | households |
| --- | ---: | ---: | ---: |
| raw `FR_2016.txt` | 26,560 | 124 | 11,459 |
| `fr_2016.parquet` after stage 1 | 10,873 | 547 | 4,253 |
| `fr_2016_singles.parquet` | 2,395 | 547 | 1,676 |
| `fr_2016_couples.parquet` | 8,478 | 547 | 2,577 |
| `singles_RURO_ready.parquet` | 2,395 | 589 | 1,676 |
| `couples_RURO_ready.parquet` | 8,478 | 589 | 2,577 |
| final MNL singles | 167,600 | 75 | 1,676 |
| final MNL couples | 257,700 | 93 | 2,577 |

The final metadata file reports exactly 100 alternatives per household and
records the current draw inputs, GSUR file, scaling constants, and prior-source
metadata.

## 4. Stage 1: Raw Read, EUROMOD Harmonization, and Sample Selection

### 4.1 First read

`enh_france_data_prep.py` reads:

```text
Z:/hisham/EUROMOD-STORAGE/Data/raw/FR_2016.txt
```

with `pd.read_csv(..., sep="\t")`. The raw file currently contains 26,560
persons in 11,459 households. The script then runs EUROMOD on the raw file,
identifies household heads and partners, constructs income fields, merges
EUROMOD outputs back to the raw inputs, harmonizes labour status and wages, and
preserves overlapping raw inputs with `_input` suffixes.

**Assessment:** correct. The code preserves provenance rather than overwriting
raw columns silently.

### 4.2 Household split before filtering

The code separates households before filtering:

- **single household:** exactly one head and no partner;
- **couple household:** exactly one head and at least one partner;
- structurally irregular households are logged and currently treated as
  singles by default.

**Assessment:** operationally correct, but the irregular-household fallback is a
substantive policy choice. It is conservative in the sense of avoiding silent
household loss, but it should be reported whenever such households exist.

### 4.3 Stepwise household filters

The active filter sequence in `stepwise_filter_households` is:

| filter | implemented rule | reason |
| --- | --- | --- |
| head age | head age within 18-65 | define working-age decision units |
| head education status | `dec == 0` for head | exclude persons currently in education |
| retirement/disability | household sum of `benefit_retire_disab` must be zero | exclude households with retirement/disability benefit receipt |
| allowed decider labour status | every decider must have `les in [3, 5, 7]` | retain employees, unemployed, inactive; exclude farmers and self-employed |
| partner age, couples only | partner age within 18-65 | same working-age rule for both deciders |
| partner education status, couples only | `dec == 0` for partner | same education rule for both deciders |
| opposite-sex couples | exactly one `dgn == 1` male and one `dgn == 0` female among deciders | model currently assumes one male and one female partner |
| other household members | drop households where a non-decider is working-age/healthy/non-student or has labour/self-employment income above threshold | simplify the household decision unit |
| hours and wages | cap employee hours above 70 to 70; set 5-10 hours to 10; convert <=5 hours to inactive where allowed; drop households with decider wages outside 2-170 | enforce support and remove implausible decider labour inputs |

The `other_members_income_threshold` defaults to 50. The allowed `les` rule is
applied at the **decider** level, not to all persons in the household.

**Assessment:** the code implements the intended restrictions explicitly and at
household level. Two points matter for interpretation:

1. These are not only data-cleaning rules; several are **sample-definition**
   rules. In particular, excluding households with working-capable other adults
   and excluding self-employed/farmers changes the population to which the
   model applies.
2. Very-low-hours employees are recoded to inactive rather than merely removed.
   This is a modelling transformation and should be disclosed in empirical
   documentation.

### 4.4 Current post-filter sample

After stage 1:

| sample | households | persons retained | decider structure |
| --- | ---: | ---: | --- |
| singles | 1,676 | 2,395 | 1,676 heads, no partners |
| couples | 2,577 | 8,478 | 2,577 heads and 2,577 partners |

Among deciders:

- singles: 766 male heads, 910 female heads;
- couples: 2,577 male deciders and 2,577 female deciders.

**Documentation gap:** the script can export filter-step statistics, but no
current filter-statistics CSV/TEX file was found in the repository or active
processed directory. The code path exists; the realized per-filter current
drop counts are not presently preserved near the active data outputs.

## 5. Stage 2: RURO-Ready Covariates

`enh_RURO_prep.py` enriches the filtered files without changing household
membership. It adds:

- `ruro_sample = 1` for adult deciders;
- education dummies `educL`, `educH` and implicit middle education;
- potential experience `pexp_years`, `pexp_years2`, and scaled `pexp`;
- worker and focal-hours indicators;
- canonical hours and wage aliases;
- age-normalized variables;
- `loc4`, the four-task occupation collapse;
- France regional dummies `reg_nuts1_1` to `reg_nuts1_10`.

The occupation collapse is explicit:

| `loc` source codes | `loc4` |
| --- | ---: |
| non-work | `-1` |
| unknown/invalid working occupation | `-2` |
| 6, 7, 8 | 1 |
| 5 | 2 |
| 4 | 3 |
| 1, 2, 3 | 4 |

Current `ruro_sample` counts:

| file | adult deciders flagged |
| --- | ---: |
| singles ready | 1,676 |
| couples ready | 5,154 |

**Assessment:** correct and internally coherent. The script deliberately keeps
non-deciders because they are still needed later when EUROMOD computes
household disposable income on simulated alternatives.

## 6. Stage 3: Simulated Opportunity Draws

`enh_RURO_draws.py` turns each decider into a choice set:

- `draw = 0` is the observed alternative and is marked chosen;
- draws `1..99` are simulated alternatives;
- non-deciders appear only at `draw = 0` in the draw files;
- deciders receive simulated employment/non-employment, hours, wages, and
  occupation draws;
- proposal-density layers are stored as
  `log_q_state`, `log_q_hours`, `log_q_wage`, `log_q_occ`, `log_q_total`.

For the current continuous occupation branch:

- employment/non-employment mass is gender-specific via `pi0_m`, `pi0_f`;
- hours support is `[5, 70]`;
- wage support is `[2, 170]`;
- occupation can be drawn empirically for working alternatives.

Current realized draw files:

| file | chosen rows | decider rows | non-decider rows | draw range |
| --- | ---: | ---: | ---: | --- |
| singles draws | 1,676 | 167,600 | 719 | 0-99 |
| couples draws | 5,154 | 515,400 | 3,324 | 0-99 |

**Assessment:** correct. The design preserves observed alternatives in support,
keeps proposal components explicit, and delays non-decider replication until
the EUROMOD stage.

## 7. Stage 4: EUROMOD on Simulated Alternatives

`enh_RURO_euromod.py` prepares the tax-benefit simulation input:

- deciders are identified from `is_decider` when available;
- non-deciders are replicated across the draw grid so every simulated
  household alternative remains a complete household for EUROMOD;
- only deciders receive draw-specific hours/wage/earnings overrides;
- non-deciders keep baseline labour inputs;
- orphan household-draw rows with no decider are dropped;
- stable true IDs are retained to reconnect alternatives later.

This is the stage where the distinction between **estimation deciders** and
**household members needed for disposable-income simulation** matters most.

**Assessment:** correct and important. Removing children/other adults before
EUROMOD would miscompute household taxes and transfers.

## 8. Stage 5: GSUR

The current pipeline merges `FR_gsur_ruro.parquet` later during MNL assembly.
The current merge is technically exact, and the final files contain complete
`gsur` / `gsur_male` / `gsur_female` values.

However, the GSUR audit found that the current integer region join is not yet
safe to interpret economically:

- EUROMOD `drgn1` uses the old 10-category French regional coding;
- the current lookup was built from modern NUTS region codes;
- direct integer joining is therefore mechanically valid but not yet
  semantically guaranteed.

**Assessment:** not yet interpretation-safe. GSUR should be treated as
provisional until the v2.1 rebuild specification is implemented and Stage A
re-estimation is completed.

## 9. Stage 6: Final MNL Assembly

`enh_RURO_prep_mnl_basic.py` performs the final conversion from simulated
household alternatives to estimation rows.

### 9.1 Decider restriction

The script explicitly removes non-deciders at this stage:

- singles keep heads;
- couples keep head/partner deciders only.

This is correct because non-deciders were required for EUROMOD but are not
decision makers in the labour-supply likelihood.

### 9.2 Singles

For singles:

- `hours` is the draw-specific labour supply;
- `leisure = 80 - hours`, clipped positive;
- `working` and focal hours indicators are rebuilt from draw-specific hours;
- `consumption = ils_dispy + other_members_income`.

### 9.3 Couples

For couples:

- the long male/female rows are reshaped to one household-alternative row;
- each `(idhh, draw)` must contain exactly one male (`dgn == 1`) and one female
  (`dgn == 0`);
- partner-specific columns become `_male` and `_female`;
- `consumption_male` and `consumption_female` come from partner-specific
  disposable incomes;
- household `consumption` is their sum;
- hours, wage, leisure, work status, and occupation remain partner-specific.

So the model is **not** “one person” for couples. It is one household choice
over a paired male/female labour-supply alternative:

```text
(hours_male, wage_male, loc4_male,
 hours_female, wage_female, loc4_female,
 shared household consumption)
```

That matches the intended unitary-couple construction.

### 9.4 Scaling and priors

The MNL builder still writes normalized helper columns:

- singles: `c_norm`, `l_norm`;
- couples: `c_norm`, `l_norm_male`, `l_norm_female`.

But the active estimator currently uses the **raw** `consumption` and
`leisure` columns in its utility expressions, not the normalized helper
columns. The normalized columns remain useful diagnostics/legacy artifacts.

The script also creates explicit proposal aliases:

- singles: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`;
- couples: partner-specific versions of the same layers.

The final invariant is:

```text
log_prior = sum of active proposal-density components
```

### 9.5 Final MNL validation

Current final files satisfy:

| check | singles | couples |
| --- | ---: | ---: |
| households | 1,676 | 2,577 |
| alternatives per household | 100 | 100 |
| chosen alternatives per household | exactly 1 | exactly 1 |
| chosen gender split | 766 male, 910 female | 2,577 male + 2,577 female views |

**Assessment:** correct. The final estimation inputs have the expected shape
and decider interpretation.

## 10. What Is Excluded, and Why

| exclusion or transformation | where | reason | audit view |
| --- | --- | --- | --- |
| households outside head/partner age 18-65 | stage 1 | working-age sample | correct, substantive |
| current students among deciders | stage 1 | avoid education participation margin | correct, substantive |
| households with retirement/disability benefit receipt | stage 1 | avoid retirement/disability participation margin | correct, substantive |
| farmers and self-employed deciders | stage 1 | wage/offered-job model is employee-oriented | correct, substantive |
| same-sex couples | stage 1 | current couple model assumes one male and one female partner | correctly implemented; scope limitation |
| households with working-capable or labour-income other members | stage 1 | simplify decision unit | correctly implemented; sample restriction |
| decider wages outside 2-170 | stage 1 | keep wage support coherent | technically correct; economically consequential |
| children/other adults from final MNL rows | stage 6 | not labour-supply decision makers | correct; retained earlier for EUROMOD |
| non-work occupation contribution | stage 6/spec | occupation opportunity should be gated off for non-work | correct |

## 11. Documentation Audit

### 11.1 Still useful and broadly current

- `docs/methods/RURO_METHODS_AND_PIPELINE_MANUAL_v1.md`
- `docs/PIPELINE_ENTRYPOINTS.md`
- `docs/France_case/_shared/gsur/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md`
- `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md`
- `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_output_reference.md`

### 11.2 Useful but currently stale or incomplete

| document | issue |
| --- | --- |
| `docs/France_case/P3a/design/FR2016_RURO_pipeline_report.md` | legacy script names and a single combined MNL artifact; not safe as the current execution guide |
| `docs/specifications/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md` | states that utility uses normalized `consumption`/`leisure`; active estimator uses raw columns |
| older GSUR note documents | superseded by the GSUR source/merge audit and v2.1 rebuild specification |

### 11.3 Missing canonical artifact

Before this memo, no single current document described:

- the exact active enhanced script chain;
- the complete current filter sequence;
- the decider versus non-decider lifecycle;
- the current final artifact counts;
- the known documentation drift;
- the GSUR interpretation caveat.

That is the main documentation gap this audit closes.

## 12. Recommended Follow-Up

1. Treat this memo as the current canonical **data-build audit** for the active
   France 2016 continuous branch.
2. Update `docs/specifications/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md` so it no longer
   claims the estimator uses normalized utility inputs.
3. Mark `docs/France_case/P3a/design/FR2016_RURO_pipeline_report.md` clearly as historical/legacy or
   replace it with a current enhanced-pipeline narrative.
4. Preserve filter-step CSV outputs next time stage 1 is rerun; current code can
   write them, but the active artifacts do not preserve the realized per-filter
   counts near the processed data.
5. Finish the GSUR v2.1 rebuild before interpreting GSUR-based regional
   opportunity results as economically aligned.

