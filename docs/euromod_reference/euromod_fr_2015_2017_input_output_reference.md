# EUROMOD France FR_2015-FR_2017 Input and Output Variable Reference

Generated: 2026-05-12

This is a compact project reference for France systems `FR_2015`, `FR_2016`, and `FR_2017`. It is designed for ChatGPT, Claude, and Claude Code: common material appears once, and only verified year-specific differences are listed separately.

## Source files

- `docs/latest_public_model_release/EUROMOD_RELEASES_J2.0+/Input/DRD_FR_training_data.xls`
- `docs/latest_public_model_release/EUROMOD_RELEASES_J2.0+/XMLParam/Countries/FR/FR.xml`
- `docs/latest_public_model_release/EUROMOD_RELEASES_J2.0+/EM3Translation/XMLParam/Config/Variables.xml`
- `docs/DRD_FR_2021_c2_export.txt` is an example DRD text export format, not the controlling source for this index.

## Companion lookup files

- `Data/documentation/euromod_fr_2015_2017_input_variables.csv`: full DRD input-variable index.
- `Data/documentation/euromod_fr_2015_2017_output_variable_index.csv`: standard-output policy configuration for `FR_2015`, `FR_2016`, and `FR_2017`.
- `Data/documentation/euromod_fr_2015_2017_standard_income_concepts.csv`: standardized income-concept components from `IlsDef_fr`.
- `docs/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md`: RURO
  continuous-MNL variables derived after EUROMOD, including `working`,
  `loc4`, `log_q_E/H/W/Occ`, and the singles/couples group conventions.

## One-page rule for LLM use

- Input variables are common across `FR_2015`, `FR_2016`, and `FR_2017`; do not repeat them by year.
- Standard-output structure is common across the three years; only output file names change by year.
- The year-specific differences found in `IlsDef_fr` are limited to the PPE/PA switch listed below: `tinrf_s` is active in 2015 and `bsawk_s` is active in 2016/2017 for the affected means-tested benefit concepts.
- Use the CSV companions for exact lookup; this Markdown is the compact orientation file.
- Do not treat RURO-derived variables as EUROMOD source variables. For example,
  `dgn` is documented here as an EUROMOD input (`0 = female`, `1 = male`),
  while `working`, `loc4`, `loc4_male`, `log_q_Occ`, and `theta_c_singles`
  are RURO pipeline/specification variables documented in
  `docs/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md`.

## DRD input data: common across FR_2015-FR_2017

The France DRD workbook documents one input database used by the local public model release. It is not split into separate 2015, 2016, and 2017 input-variable lists.

| Field | Value |
| --- | --- |
| Country | FR |
| Authors | Katrin Gasior & EUROMOD training team |
| DRD date | 18 Apr 2024 |
| Type of data source | Synthetic data produced by HHoT |
| Final households | 2397 |
| Final individuals | 7482 |

### DRD worksheet coverage

| sheet              |   variables |   monetary_variables |   variables_with_observations |
|:-------------------|------------:|---------------------:|------------------------------:|
| assets             |           2 |                    1 |                             1 |
| expenditure shares |         193 |                    0 |                           193 |
| expenditures       |           8 |                    8 |                             2 |
| hhot               |           2 |                    0 |                             1 |
| income             |          49 |                   45 |                            12 |
| labour             |          11 |                    0 |                             9 |
| personal           |          16 |                    0 |                            14 |

### Selected input variables

This is a short orientation table. Full labels, derivation notes, and summary statistics are in the input CSV.

| variable   | sheet        | label_short                                                                                | description_short                                                                                                        | monetary   |   obs |
|:-----------|:-------------|:-------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|:-----------|------:|
| idperson   | personal     | IDENTIFIER : person                                                                        | idperson = rb030                                                                                                         | 0          |  7482 |
| idhh       | personal     | IDENTIFIER : hh                                                                            | idhh = db030                                                                                                             | 0          |  7482 |
| dwt        | personal     | DEMOGRAPHIC : Weight                                                                       | dwt = db090                                                                                                              | 0          |  7482 |
| dag        | personal     | DEMOGRAPHIC : Age                                                                          | dag = age                                                                                                                | 0          |  7482 |
| dgn        | personal     | DEMOGRAPHIC : Gender 0: Female 1: Male                                                     | dgn = rb090 recode dgn (2=0)                                                                                             | 0          |  7482 |
| dms        | personal     | DEMOGRAPHIC : Marital Status 1: Single 2: Married 3: Separated 4: Divorced 5: Widowed      | dms = pb190 recode dms (5=4) (4=5) individuals with missing marital status and without a partner are considered as si... | 0          |  7482 |
| ddi        | personal     | DEMOGRAPHIC : Disability 0: Not disabled 1: Disabled -1: not applicable (individual you... | ddi = 1 if pl031 == 8 ddi = 0 if pl031 != 8 & pl031 != . ddi = -1 if pl031 == . & pb030 == . replace ddi=1 if ddi==....  | 0          |  7482 |
| deh        | personal     | DEMOGRAPHIC : Education - Highest Status 0: Not completed Primary 1: Primary 2: Lower S... | gen temp_pe040 = pe040 recode temp_pe040 (100 = 1) (200 = 2) (300/399 = 3) (400/499 = 4) (500/800 = 5) gen deh = temp... | 0          |  6843 |
| dec        | personal     | DEMOGRAPHIC : Education - Current Status 0: Not in Education 1: Pre-primary 2: Primary...  | gen temp_pe020 = pe020 recode temp_pe020 (10 = 1) (20 = 2) (30/39 = 3) (40/49 = 4) (50/80 = 5) gen dec = temp_pe020 r... | 0          |  2046 |
| les        | labour       | LABOUR MARKET : Economic Status 0 Pre-school 1 Farmer 2 Employer or self-employed 3 Emp... | basic labour information on the self-declared current activity status and current main job, including information on...  | 0          |  6843 |
| lcs        | labour       | LABOUR MARKET : Civil Servant 1 yes 0 no                                                   | civil servant                                                                                                            | 0          |     0 |
| lhw        | labour       | LABOUR MARKET : Hours worked per week                                                      | number of hours usually worked per week in main job and in second, third... Jobs                                         | 0          |  3408 |
| lindi      | labour       | LABOUR MARKET : Industry (NACE) 1 Agriculture 2 Industry 3 Services 0 Not appl : Detail... | economic activity of the main job for respondents who are currently at work                                              | 0          |  7482 |
| liwwh      | labour       | LABOUR MARKET : In work : Work history (length of time in months)                          | number of months spent in paid work                                                                                      | 0          |  5436 |
| lunmy      | labour       | LABOUR MARKET : Unemployed : Months per year                                               | number of months spent in unemployment                                                                                   | 0          |    58 |
| yem        | income       | INCOME : Employment                                                                        | gross employee cash or near cash income                                                                                  | 1          |  2744 |
| yse        | income       | INCOME : Self Employment                                                                   | self-employment income                                                                                                   | 1          |   664 |
| yiy        | income       | INCOME : Investment                                                                        | income from interest, dividends, and profit from capital investments in unincorporated business                          | 1          |     0 |
| ypp        | income       | INCOME : Private Pension                                                                   | income received from pensions from individual private plans                                                              | 1          |     0 |
| ypr        | income       | INCOME : Property                                                                          | income from rent                                                                                                         | 1          |     0 |
| ypt        | income       | INCOME : Private Transfers                                                                 | regular inter-household cash transfers received                                                                          | 1          |     0 |
| bch00      | income       | BENEFIT/PENSION : Child : Main/Basic                                                       | monthly Family Allowance (Allocation Familiale AF)                                                                       | 1          |     0 |
| bsa00      | income       | BENEFIT/PENSION : Social Assistance : Main/Basic                                           | monthly mean-tested minimum income (Revenu minimum d'insertion RMI)                                                      | 1          |     0 |
| bsaot      | income       | MEAN-TESTED MINIMUM INCOME (RSA): store remaining exclusion benefits                       | RSA store remaining exclusion benefits                                                                                   | 1          |     0 |
| bunmy      | income       | BENEFIT/PENSION : Unemployment : Months per year                                           | number of months while receiving unemployment benefits                                                                   | 0          |    58 |
| pdi00      | income       | BENEFIT/PENSION : Disability : Main/Basic                                                  | monthly amount from invalidity pension                                                                                   | 1          |     0 |
| xhc        | expenditures | EXPENDITURE : Housing cost                                                                 | total housing cost                                                                                                       | 1          |  2397 |
| xhcrt      | expenditures | EXPENDITURE : Housing cost : Rent                                                          | current rent related to occupied dwelling                                                                                | 1          |  2397 |
| xhcmomi    | expenditures | EXPENDITURE : Housing cost : Mortgage Interest                                             | interest repayments on mortgage                                                                                          | 1          |     0 |
| amrtn      | assets       | ASSETS : Main Residence : Tenure 1 Owned on mortgage 2 Owned outright 3 Rented 4 Reduce... | tenure status                                                                                                            | 0          |  7482 |
| afc        | assets       | ASSETS : Financial Capital                                                                 | financial income                                                                                                         | 1          |     0 |
| sid_h      | hhot         | household id for HHoT household                                                            |                                                                                                                          |            |  7482 |
| sft_h      | hhot         | family type for HHoT household                                                             |                                                                                                                          |            |     0 |

## Standard output: common configuration

Across `FR_2015`, `FR_2016`, and `FR_2017`, the individual-level standard-output policy is switched on and the household-level standard-output policy is switched off.

### Output files by system

| system   | output_std_fr   | output_std_hh_fr   |
|:---------|:----------------|:-------------------|
| FR_2015  | FR_2015_std     | FR_2015_std_hh     |
| FR_2016  | FR_2016_std     | FR_2016_std_hh     |
| FR_2017  | FR_2017_std     | FR_2017_std_hh     |

### Individual-level standard output

- Policy: `output_std_fr`
- Switch: `on` in all three systems
- Comment: `DEF: STANDARD OUTPUT INDIVIDUAL LEVEL`
- Tax unit: `tu_individual_fr`

Variable groups included:

| group   | meaning                 |
|:--------|:------------------------|
| a*      | Asset variables         |
| b*      | Benefit variables       |
| d*      | Demographic variables   |
| i_*     | Intermediate Variables  |
| id*     | ID variables            |
| k*      | In kind income          |
| l*      | Labour market variables |
| p*      | Pension variables       |
| s*      | Auxiliary Variables     |
| t*      | Tax variables           |
| x*      | Expenditure variables   |
| y*      | Market income variables |

Income-list groups included:

| group   | meaning                   |
|:--------|:--------------------------|
| ils_*   | Standardized income lists |
| il_*    |                           |

Interpretation: the standard `FR_YYYY_std` output is configured at individual level and includes identifiers, demographics, labour variables, market income, pensions, benefits, taxes, expenditures, assets, in-kind variables, intermediate/auxiliary variables, and standardized income lists through wildcard groups.

### Household-level standard output

- Policy: `output_std_hh_fr`
- Switch: `off` in all three systems
- Comment: `DEF: STANDARD OUTPUT HOUSEHOLD LEVEL`
- If switched on, it writes `FR_YYYY_std_hh` with `idhh`, `dwt`, `ils*`, and tax unit `tu_household_fr`.

### Tax units in standard-output configuration

| policy           | tax_unit         |
|:-----------------|:-----------------|
| output_std_fr    | tu_individual_fr |
| output_std_hh_fr | tu_household_fr  |

## Standardized income concepts: common formulas

The formulas below use the `FR_2015` definition as the baseline. Differences for 2016/2017 are listed in the next section. Signs are EUROMOD `DefIl` signs: `+`, `-`, or `n/a`.

| concept    | FR_2015_formula                                                                                                                                                                                                                                                      |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ils_earns  | + yse; + yem00; + yemxp; n/a yemmc_s                                                                                                                                                                                                                                 |
| ils_origy  | + ils_earns; + ypp; + yiy; + ypr; + yot; + ypt; - xmp                                                                                                                                                                                                                |
| ils_ben    | + ils_pen; + ils_benmt; + ils_bennt                                                                                                                                                                                                                                  |
| ils_benmt  | + bchyc_s; + bsuwd_s; + bunmt_s; + bchlg_s; + bched_s; + bchba_s; + bsaoa_s; + bdi_s; n/a bchlp_s; + bsa00_s; + bhotn_s; + tinrf_s; + bchot_s; + bsaot; + bhoot; + bed; n/a bsawk_s; n/a bsaeccm_s; n/a binxp_s; n/a bhoey_s; n/a binpb_s                            |
| ils_bensim | + bunct_s; + bunmt_s; + bdi_s; + bsuwd_s; + bch00_s; + bchba_s; + bchyc_s; + bchlg_s; + bched_s; n/a bchlp_s; n/a bsa00_s; + bsaoa_s; + bhotn_s; + tinrf_s; n/a bsawk_s; + bchcc_s; + bchor_s; n/a bwkmcee_s; n/a bwkmcse_s; n/a bsaeccm_s; n/a bseec_s; n/a bhoey_s |
| ils_tax    | + tin_s; + tpr; + tscxc_s; + tscdf_s; + tsckt_s; + tinto_s; n/a tinto01_s; + twl; + tmu                                                                                                                                                                              |
| ils_taxsim | + tin_s; + tscxc_s; + tscdf_s; + tsckt_s; + tinto_s; n/a tinto01_s                                                                                                                                                                                                   |
| ils_dispy  | + ils_origy; + ils_ben; - ils_sicdy; - ils_tax                                                                                                                                                                                                                       |

Most important disposable-income identity:

```text
ils_dispy = ils_origy + ils_ben - ils_sicdy - ils_tax
```

## Year-specific differences

Input variables are common. Standard-output policy structure is common. The meaningful differences found in the parsed standard income concepts concern the transition from the working tax credit/PPE refund to the activity allowance/PA component.

| concept    | component   | component_comment                      | FR_2015   | FR_2016   | FR_2017   |
|:-----------|:------------|:---------------------------------------|:----------|:----------|:----------|
| ils_b1_bsa | bsawk_s     | Activity Allowance (PA)                | n/a       | +         | +         |
| ils_b1_bsa | tinrf_s     | Refund of the working tax credit (PPE) | +         | n/a       | n/a       |
| ils_benmt  | bsawk_s     | Activity allowance                     | n/a       | +         | +         |
| ils_benmt  | tinrf_s     | Refund of the working tax credit (PPE) | +         | n/a       | n/a       |
| ils_bensim | bsawk_s     | Activity allowance                     | n/a       | +         | +         |
| ils_bensim | tinrf_s     | Refund of the working tax credit (PPE) | +         | n/a       | n/a       |

Interpretation:

- `FR_2015` includes `tinrf_s` in the affected benefit/income-list concepts and treats `bsawk_s` as `n/a`.
- `FR_2016` and `FR_2017` treat `tinrf_s` as `n/a` and include `bsawk_s`.
- Do not describe the 2015 and 2016/2017 means-tested-benefit concepts as identical without noting this PPE/PA switch.

## Caveats

- This reference is based on local DRD and XML configuration files. It does not prove that a particular `FR_YYYY_std` file was generated or that every wildcard variable is nonzero in output.
- The DRD file is training/synthetic input data. Use it for variable meanings and availability, not as real survey documentation.
- If a France run is later produced, validate the actual output columns against this configuration before writing empirical claims.
- The input CSV is the authoritative full input index; this Markdown repeats only selected variables to remain compact and useful in LLM project knowledge.

## Prompt fragment for reuse

> Use `Data/documentation/euromod_fr_2015_2017_input_output_reference.md` as the compact reference. Input variables are common across `FR_2015`, `FR_2016`, and `FR_2017`; do not repeat them by year. For output, use the common `output_std_fr` configuration and then apply only the listed year-specific `IlsDef_fr` differences, especially the 2015 `tinrf_s` vs 2016/2017 `bsawk_s` switch in means-tested benefit concepts.
