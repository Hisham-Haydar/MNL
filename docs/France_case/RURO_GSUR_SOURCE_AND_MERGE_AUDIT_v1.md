# RURO GSUR Source And Merge Audit v1

Date: 2026-05-15

## 1. Purpose

This audit records what the France GSUR data contain before the MNL merge,
how the current enhanced RURO pipeline merges them, and what actually lands
in the final France 2016 continuous-branch MNL parquets.

It complements `docs/estimation/RURO_GSUR_DATA_AND_MERGE_NOTE.md`:

- the existing note documents the intended GSUR pipeline;
- this audit documents the current files and the realized 2016 merge.

## 2. Bottom Line

1. The current estimation pipeline uses:

   ```text
   Data/external/FR_gsur_ruro.parquet
   ```

2. In that prepared lookup, `gsur` is a proportion, not a percent.

3. The current lookup used for France 2016 is not age-specific in practice:
   it contains only `age_group_used = Y20-64`.

4. The merge code is capable of age-specific joins, but in the realized 2016
   merge almost every row uses the `Y20-64` full-age fallback:

   | sample | direct age-specific household matches | fallback household matches |
   | --- | ---: | ---: |
   | singles | 2 / 1,676 | 1,674 / 1,676 |
   | couples male | 0 / 2,577 | 2,577 / 2,577 |
   | couples female | 0 / 2,577 | 2,577 / 2,577 |

5. The realized France 2016 merge is complete and exact:

   - no missing final `gsur`, `gsur_male`, or `gsur_female`;
   - every observed final MNL key exists in the 2016 lookup;
   - every merged final GSUR value equals the value implied by the base lookup
     keys;
   - GSUR is constant within each household choice set, as it should be.

6. A single observation can legitimately receive different unemployment-rate
   values depending on the source concept chosen:

   - regional or national;
   - sex-specific or total-sex;
   - education-specific or total-education;
   - broad `Y20-64` or fine age-group.

   In the final sample, the median within-observation range across the audited
   candidate concepts is `0.056` for singles, `0.056` for couples male, and
   `0.056` for couples female. The current pipeline makes one specific choice:
   region-specific, sex-specific, education-specific, broad-age `Y20-64`.

7. `drgn1` and `gsur` are not duplicates of each other:

   - `drgn1` has 8 observed region levels in the final MNL data;
   - within each `drgn1`, GSUR still varies by sex and education;
   - this is why region dummies can add information beyond GSUR in an M1 model.

8. **Important semantic flag:** the merge is mechanically exact, but the
   integer region coding appears not to be semantically aligned:

   - the EUROMOD France 2016 `drgn1` in the MNL data is the older 10-group
     France coding derived from old `drgn2` regions;
   - the GSUR preparation script independently builds `drgn1` integers from
     modern NUTS codes `FR1, FRB, FRC, ...`;
   - only integer `1` clearly names the same region under both systems.

   The current code joins these integer keys directly. That should be treated
   as a **region-crosswalk issue requiring correction or explicit
   confirmation** before GSUR is interpreted as a correctly region-aligned
   labor-market shifter.

## 3. Files Inspected

### 3.1 Source and prepared GSUR files

| file | role |
| --- | --- |
| `Data/external/FR_gsur.xlsx` | original Eurostat-style workbook source |
| `Data/external/FR_gsur_full.parquet` | parsed long-form source output |
| `Data/external/FR_gsur_simple.parquet` | simplified intermediate lookup |
| `Data/external/FR_gsur_ruro.parquet` | RURO-ready lookup actually passed into MNL prep |

### 3.2 Pipeline code

| file | role |
| --- | --- |
| `scripts/enhanced/enh_prepare_FR_gsur.py` | prepares source GSUR data |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | merges GSUR into singles/couples MNL files |

### 3.3 Final 2016 outputs

| file | role |
| --- | --- |
| `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet` | final singles MNL |
| `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet` | final couples MNL |
| `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__mnlmeta.json` | records the GSUR file actually used |

The metadata confirms the 2026-05-13 MNL rebuild used:

```text
U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet
```

## 4. GSUR Meaning And Units

GSUR means group-specific unemployment rate.

The preparation code converts the source percentage to a proportion:

```python
df["gsur"] = df["gsur"] / 100.0
```

So:

| value | meaning |
| ---: | --- |
| `0.040` | 4.0 percent unemployment |
| `0.100` | 10.0 percent unemployment |
| `0.210` | 21.0 percent unemployment |

The current model uses GSUR as an opportunity-side labor-market shifter, not
as a utility/preference shifter.

## 5. Why The Same Observation Can Have Several GSUR Values

GSUR is not a primitive observed once per person before aggregation. The source
workbook is a multidimensional table of unemployment rates. For the same
person, several valid source-level concepts can be extracted depending on the
conditioning set:

| dimension | examples of possible extraction choices |
| --- | --- |
| geography | national France, NUTS1-style region, finer region |
| sex | male/female-specific, total-sex |
| education | low/medium/high-specific, total-education |
| age | `Y15-24`, `Y25-34`, `Y35-44`, `Y45-54`, `Y55-64`, `Y20-64`, etc. |

The current pipeline chooses:

```text
region-specific x sex-specific x education-specific x Y20-64
```

This is an economic modeling choice, not the only number that exists in the
source file.

### 5.1 Audited alternative concepts

For each final household/partner observation, this audit compared:

| audited concept | description |
| --- | --- |
| current concept | current integer-region key, sex-specific, education-specific, `Y20-64` |
| same-region sex total-education | same region and sex, but education collapsed to `TOTAL` |
| same-region total-sex education | same region and education, but sex collapsed to `T` |
| same-region total | same region, total-sex, total-education |
| national sex education | national France, sex-specific, education-specific |
| national total | national France, total-sex, total-education |
| same-region sex education actual-age | same region, sex, education, but fine age-group when available |

These comparisons deliberately hold the current integer-region assignment
fixed. Section 13.3 separately audits whether that region assignment is
semantically aligned with the EUROMOD `drgn1` coding.

### 5.2 Empirical range across concepts for the same final observations

| sample | observations | concepts available for nearly all observations | median within-observation range | max range |
| --- | ---: | ---: | ---: | ---: |
| singles | 1,676 | 7 for 1,672; 6 for 4 | 0.056 | 0.447 |
| couples male | 2,577 | 7 for all | 0.056 | 0.411 |
| couples female | 2,577 | 7 for 2,573; 6 for 4 | 0.056 | 0.447 |

Median absolute difference from the current concept:

| alternative concept | singles | couples male | couples female |
| --- | ---: | ---: | ---: |
| same-region sex total-education | 0.030 | 0.031 | 0.030 |
| same-region total-sex education | 0.003 | 0.003 | 0.003 |
| same-region total | 0.032 | 0.032 | 0.033 |
| national sex education | 0.010 | 0.011 | 0.010 |
| national total | 0.032 | 0.030 | 0.032 |
| same-region sex education actual-age | 0.027 | 0.026 | 0.024 |

Age is especially consequential for some young low-education observations. One
observed female low-education case has:

| concept | GSUR |
| --- | ---: |
| current broad-age concept | 0.124 |
| same-region total-sex, same education | 0.148 |
| national sex-specific, same education | 0.172 |
| fine actual-age concept (`Y15-24`) | 0.524 |

So the statement "this person has GSUR = 0.124" is correct only after stating
the extraction rule. The source itself also contains plausible values such as
`0.148`, `0.172`, or `0.524` for different conditioning choices.

### 5.3 Current choice versus richer source support

The source workbook contains rich age support, but the current
`FR_gsur_ruro.parquet` reduces the RURO lookup to `Y20-64` only. Therefore the
final MNL files currently use a broad working-age unemployment concept even
though the full source can support finer age-specific alternatives.

### 5.4 Grouping-level lattice available in the 2016 source

The source file allows GSUR to be defined at many aggregation levels. The table
below shows direct source concepts available in 2016. Values are percentages in
the source file before the RURO `divide by 100` conversion.

| grouping level | direct source cells | non-missing cells | distinct GSUR values | min | max |
| --- | ---: | ---: | ---: | ---: | ---: |
| France total | 1 | 1 | 1 | 9.8 | 9.8 |
| female only, France total | 1 | 1 | 1 | 9.6 | 9.6 |
| region only | 14 | 14 | 12 | 7.5 | 21.9 |
| female x region | 14 | 14 | 13 | 7.4 | 23.0 |
| age only, France total | 10 | 10 | 9 | 7.2 | 24.6 |
| female x age, France total | 10 | 10 | 9 | 6.3 | 24.0 |
| region x age | 140 | 140 | 85 | 3.1 | 45.7 |
| female x region x age | 140 | 138 | 85 | 4.7 | 47.7 |
| region x sex x education, `Y20-64` | 84 | 84 | 62 | 3.7 | 35.5 |
| region x sex x education x age | 840 | 800 | 279 | 2.0 | 72.9 |

This is the exact reason one observation can have several defensible GSUR
values. Example interpretations:

| concept | what it answers |
| --- | --- |
| France total | "What is the national unemployment rate?" |
| female only | "What is the unemployment rate for women nationally?" |
| region only | "What is unemployment in this region, ignoring sex and education?" |
| female x region | "What is unemployment for women in this region?" |
| age only | "What is unemployment for this age bracket nationally?" |
| female x age | "What is unemployment for women of this age bracket nationally?" |
| female x region x age | "What is unemployment for women of this age bracket in this region?" |
| region x sex x education x age | "What is unemployment for this region-sex-education-age cell?" |

The current RURO lookup uses one specific member of this family:

```text
region x sex x education x Y20-64
```

It does not currently use:

```text
region x sex x education x actual age group
```

even though the full source file contains that richer support.

## 6. Data Cardinality Overview

### 6.1 Cardinality by GSUR file

| file / slice | rows | years | regions | sexes | education groups | age groups | distinct GSUR values | missing GSUR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FR_gsur_full.parquet`, all years | 90,720 | 18 | 42 | 3 | 4 | 10 | 701 | 25,863 |
| `FR_gsur_simple.parquet`, all years | 9,720 | 18 | 15 | 3 | 4 | 3 | 394 | 1,011 |
| `FR_gsur_ruro.parquet`, all years | 2,160 | 18 | 15 | 2 | 4 | 1 | 246 | 132 |
| `FR_gsur_full.parquet`, 2016 only | 5,040 | 1 | 42 | 3 | 4 | 10 | 468 | 429 |
| `FR_gsur_simple.parquet`, 2016 only | 540 | 1 | 15 | 3 | 4 | 3 | 195 | 6 |
| `FR_gsur_ruro.parquet`, 2016 only | 120 | 1 | 15 | 2 | 4 | 1 | 82 | 0 |

Interpretation:

- the original source is rich: 42 region codes, 3 sex categories, 4 education
  groups, and 10 age groups;
- the simplified file keeps only short NUTS-style regions and 3 age groups;
- the RURO-ready file further keeps only male/female rows and one broad age
  bracket.

### 6.2 Cardinality in the final France 2016 MNL files

| final sample | households | region levels | sex levels | education levels | observed age-group levels | distinct GSUR values | observed joint cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| singles | 1,676 | 8 `drgn1` | 2 `dgn` | 3 `educ3` | 6 | 40 `gsur` | 48 `drgn1 x dgn x educ3` |
| couples male view | 2,577 | 8 `drgn1` | fixed male | 3 `educ3_male` | 5 | 24 `gsur_male` | 24 `drgn1 x educ3_male` |
| couples female view | 2,577 | 8 `drgn1` | fixed female | 3 `educ3_female` | 5 | 24 `gsur_female` | 24 `drgn1 x educ3_female` |

If age were used in the final merge, the observed support is much richer:

| final sample view | observed joint cells with age |
| --- | ---: |
| singles `drgn1 x dgn x educ3 x age-group` | 221 |
| couples male `drgn1 x educ3_male x age-group` | 115 |
| couples female `drgn1 x educ3_female x age-group` | 118 |

The current merged GSUR cardinality is therefore lower than the available
observed household support because the RURO-ready lookup collapses age to
`Y20-64`.

## 7. Source-Lineage Summary

### 7.1 Parsed full source: `FR_gsur_full.parquet`

| property | value |
| --- | ---: |
| rows | 90,720 |
| columns | 8 |
| years | 18 |
| region codes | 42 |
| sexes | 3 (`F`, `M`, `T`) |
| education groups | 4 |
| age groups | 10 |
| missing GSUR rows | 25,863 |
| GSUR unit | percent |

GSUR distribution in percent:

| statistic | value |
| --- | ---: |
| min | 1.3 |
| p25 | 6.5 |
| median | 9.6 |
| p75 | 16.1 |
| max | 93.7 |

### 7.2 Simplified intermediate: `FR_gsur_simple.parquet`

| property | value |
| --- | ---: |
| rows | 9,720 |
| columns | 9 |
| years | 18 |
| region codes | 15 |
| sexes | 3 (`F`, `M`, `T`) |
| education groups | 4 |
| age groups | 3 (`Y20-64`, `Y25-34`, `Y_GE25`) |
| missing GSUR rows | 1,011 |
| GSUR unit | percent |

### 7.3 RURO-ready lookup: `FR_gsur_ruro.parquet`

| property | value |
| --- | ---: |
| rows | 2,160 |
| columns | 12 |
| years | 18 |
| `drgn1` values | 15 (`0` through `14`) |
| sexes | 2 (`dgn = 0`, `dgn = 1`) |
| education codes | 4 (`educ3 = -1, 0, 1, 2`) |
| age groups retained | 1 (`Y20-64`) |
| missing GSUR rows | 132 |
| GSUR unit | proportion |

GSUR distribution in proportions:

| statistic | value |
| --- | ---: |
| min | 0.025 |
| p25 | 0.062 |
| median | 0.083 |
| p75 | 0.117 |
| max | 0.388 |

## 8. The 2016 Source Slice Before Merge

For `year = 2016`, `FR_gsur_ruro.parquet` contains:

| property | value |
| --- | ---: |
| rows | 120 |
| missing GSUR rows | 0 |
| `drgn1` support | `0` through `14` |
| `dgn` support | `0`, `1` |
| `educ3` support | `-1`, `0`, `1`, `2` |
| age-group support | `Y20-64` only |

2016 source distribution by sex and education:

| `dgn` | `educ3` | rows | min | median | max |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | -1 | 15 | 0.074 | 0.096 | 0.230 |
| 0 | 0 | 15 | 0.124 | 0.159 | 0.355 |
| 0 | 1 | 15 | 0.077 | 0.103 | 0.242 |
| 0 | 2 | 15 | 0.037 | 0.059 | 0.079 |
| 1 | -1 | 15 | 0.073 | 0.095 | 0.209 |
| 1 | 0 | 15 | 0.091 | 0.167 | 0.295 |
| 1 | 1 | 15 | 0.069 | 0.100 | 0.198 |
| 1 | 2 | 15 | 0.037 | 0.056 | 0.069 |

Low-education cells have the highest unemployment rates; high-education cells
have the lowest rates. That pattern is already present in the external lookup
before any MNL merge.

## 9. How The Current Code Builds The Lookup

`scripts/enhanced/enh_prepare_FR_gsur.py` performs the following steps:

1. Parses the workbook into long form by year, region, sex, education, and age
   group.
2. Filters the RURO-ready output to male/female rows only.
3. Chooses an age-group candidate, defaulting to `Y20-64`, with fallbacks.
4. Maps source region codes to `drgn1`.
5. Maps sex to RURO `dgn`:

   ```text
   female -> 0
   male   -> 1
   ```

6. Maps education to `educ3`:

   ```text
   ED0-2 -> 0
   ED3_4 -> 1
   ED5-8 -> 2
   TOTAL -> -1
   ```

7. Converts GSUR from percent to proportion.
8. Enforces uniqueness on:

   ```text
   year, drgn1, dgn, educ3
   ```

9. Validates values remain within `[0, 1]`.

Important consequence: the RURO-ready file intentionally collapses the richer
source age support to one selected age bracket. In the current file, that
selected bracket is `Y20-64`.

## 10. How The MNL Merge Code Works

### 10.1 Shared helper behavior

`scripts/enhanced/enh_RURO_prep_mnl_basic.py` first standardizes the lookup:

- if the lookup has `age_group_used` but not `age_group`,
  `_standardize_gsur_age_group_column(...)` copies
  `age_group_used -> age_group`;
- ages are mapped to labels by `_map_age_to_gsur_group(...)`:

  | age range | attempted GSUR age group |
  | --- | --- |
  | `< 25` | `Y15-24` |
  | `25-34` | `Y25-34` |
  | `35-44` | `Y35-44` |
  | `45-54` | `Y45-54` |
  | `55-64` | `Y55-64` |
  | otherwise/default | `Y20-64` |

- if the age-specific join misses, `_pick_gsur_full_age_fallback(...)`
  prefers:

  ```text
  Y20-64 -> Y15-74 -> Y_GE15 -> Y_GE25
  ```

### 10.2 Singles merge

`_merge_gsur_singles(...)`:

1. ensures `year` exists;
2. derives `educ3` from `deh` when needed;
3. uses base keys:

   ```text
   year, drgn1, dgn, educ3
   ```

4. if age-group information is available, first attempts:

   ```text
   year, drgn1, dgn, educ3, age_group
   ```

5. fills misses from a full-age fallback lookup;
6. validates the merge did not change row count;
7. writes final column:

   ```text
   gsur
   ```

### 10.3 Couples merge

`_merge_gsur_couples_wide(...)` merges twice:

| partner view | forced `dgn` | final output |
| --- | ---: | --- |
| male | 1 | `gsur_male` |
| female | 0 | `gsur_female` |

For each partner it uses:

```text
year, drgn1, educ3_partner
```

plus the partner age-group field on the first attempted age-aware join when
age information is available. Misses then fall back to the full-age bracket.

The merge is partner-specific. Couples are not assigned one shared GSUR value;
the male and female partners receive their own labor-market shifter.

## 11. What Actually Happened In The Final France 2016 Merge

### 11.1 Region support used

The 2016 source lookup has `drgn1 = 0..14`, but the final France 2016 MNL files
use only:

```text
drgn1 = 1, 2, 3, 4, 5, 6, 7, 8
```

Observed final MNL household counts by region:

| `drgn1` | singles | couples |
| ---: | ---: | ---: |
| 1 | 271 | 383 |
| 2 | 269 | 446 |
| 3 | 126 | 191 |
| 4 | 145 | 227 |
| 5 | 297 | 484 |
| 6 | 190 | 292 |
| 7 | 197 | 305 |
| 8 | 181 | 249 |

### 11.2 Realized age-aware merge behavior

Because `FR_gsur_ruro.parquet` has only `Y20-64`, the first age-aware join
finds almost no matches:

| sample | households | direct age-aware matches | fallback needed |
| --- | ---: | ---: | ---: |
| singles | 1,676 | 2 | 1,674 |
| couples male | 2,577 | 0 | 2,577 |
| couples female | 2,577 | 0 | 2,577 |

Attempted singles age-group labels:

| attempted label | households |
| --- | ---: |
| `Y15-24` | 86 |
| `Y25-34` | 304 |
| `Y35-44` | 443 |
| `Y45-54` | 525 |
| `Y55-64` | 316 |
| `Y20-64` | 2 |

Attempted couples male labels:

| attempted label | households |
| --- | ---: |
| `Y15-24` | 62 |
| `Y25-34` | 567 |
| `Y35-44` | 913 |
| `Y45-54` | 700 |
| `Y55-64` | 335 |

Attempted couples female labels:

| attempted label | households |
| --- | ---: |
| `Y15-24` | 107 |
| `Y25-34` | 696 |
| `Y35-44` | 924 |
| `Y45-54` | 612 |
| `Y55-64` | 238 |

So the current final MNL files effectively use a region-sex-education GSUR
lookup at the broad `Y20-64` bracket, even though the merge code can support
finer age groups if the lookup supplied them.

### 11.3 Merge coverage and exactness

| sample | observed household-level lookup keys | missing lookup keys | final missing GSUR | final equals base-key lookup |
| --- | ---: | ---: | ---: | ---: |
| singles | 48 | 0 | 0 | 1,676 / 1,676 |
| couples male | 24 | 0 | 0 | 2,577 / 2,577 |
| couples female | 24 | 0 | 0 | 2,577 / 2,577 |

Within-choice-set constancy:

| sample | households with exactly one GSUR value across 100 alternatives |
| --- | ---: |
| singles | 1,676 / 1,676 |
| couples male | 2,577 / 2,577 |
| couples female | 2,577 / 2,577 |

This is the expected structure: GSUR is a decider/partner characteristic, not
an alternative-varying draw.

## 12. Final Merged Distribution In The 2016 MNL Files

### 12.1 Household-level summaries

| variable | households | distinct values | min | p10 | p25 | median | p75 | p90 | max | mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| singles `gsur` | 1,676 | 40 | 0.040 | 0.052 | 0.058 | 0.089 | 0.125 | 0.159 | 0.210 | 0.096 |
| couples `gsur_male` | 2,577 | 24 | 0.040 | 0.049 | 0.056 | 0.089 | 0.120 | 0.164 | 0.210 | 0.095 |
| couples `gsur_female` | 2,577 | 24 | 0.048 | 0.052 | 0.058 | 0.077 | 0.130 | 0.131 | 0.200 | 0.091 |

### 12.2 Education support actually used

Singles:

| `dgn` | `educ3` | households |
| ---: | ---: | ---: |
| 0 | 0 | 123 |
| 0 | 1 | 396 |
| 0 | 2 | 391 |
| 1 | 0 | 133 |
| 1 | 1 | 345 |
| 1 | 2 | 288 |

Couples:

| partner | `educ3` | households |
| --- | ---: | ---: |
| male | 0 | 369 |
| male | 1 | 1,201 |
| male | 2 | 1,007 |
| female | 0 | 308 |
| female | 1 | 1,035 |
| female | 2 | 1,234 |

No final estimation sample uses `educ3 = -1`; the total-education rows remain
in the external lookup but are not used by these final MNL samples.

### 12.3 Couples partner comparison

Only 389 of 2,577 couples households, or 15.1 percent, have identical
`gsur_male` and `gsur_female`.

That is expected because the lookup is partner-specific by sex and education.
The two partner views should not be collapsed into one household GSUR variable.

## 13. Detailed Description Of `drgn1` In The Current Data

### 13.1 EUROMOD meaning

In the France 2016 EUROMOD documentation, `drgn1` is:

```text
DEMOGRAPHIC : Region : NUTS Level 1
```

It is a household region-of-residence variable derived from older `drgn2`
codes. The documented derivation is:

| EUROMOD `drgn1` | old-region definition |
| ---: | --- |
| 1 | `drgn2 = 1` (`FR10`, Ile-de-France) |
| 2 | `drgn2 = 2..7` (Bassin Parisien) |
| 3 | `drgn2 = 8` (Nord-Pas-de-Calais) |
| 4 | `drgn2 = 9..11` (Est) |
| 5 | `drgn2 = 12..14` (Ouest) |
| 6 | `drgn2 = 15..17` (Sud-Ouest) |
| 7 | `drgn2 = 18..19` (Rhone-Alpes, Auvergne) |
| 8 | `drgn2 = 20..22` (Mediterranee) |
| 9 | `drgn2 = 23..26` (DOM) |
| 10 | `drgn2 = 27` (extra-regio / unknown) |

The DRD reports observed `drgn1` support from `1` to `8` for the France 2016
input. The final continuous-branch MNL files also observe only `1..8`.

### 13.2 Final MNL support

| `drgn1` | singles households | couples households | all households |
| ---: | ---: | ---: | ---: |
| 1 | 271 | 383 | 654 |
| 2 | 269 | 446 | 715 |
| 3 | 126 | 191 | 317 |
| 4 | 145 | 227 | 372 |
| 5 | 297 | 484 | 781 |
| 6 | 190 | 292 | 482 |
| 7 | 197 | 305 | 502 |
| 8 | 181 | 249 | 430 |

In singles, the final MNL file contains one-hot dummies:

```text
reg_nuts1_1, ..., reg_nuts1_8
```

Their row sums equal exactly one for all 1,676 singles households, and each
dummy count matches the corresponding `drgn1` count. In the full combined
intermediate file, `reg_nuts1_1` through `reg_nuts1_10` exist; the reduced
final singles file keeps only the observed `1..8` dummies.

`drgn1` is household-level and therefore constant across all 100 alternatives
within a decider's choice set.

### 13.3 Semantic alignment with the GSUR lookup

The current external GSUR preparation script does not reuse the EUROMOD
old-region `drgn1` coding. It independently creates a fresh integer `drgn1`
from modern NUTS codes:

| integer key | GSUR lookup region code | GSUR lookup region name |
| ---: | --- | --- |
| 0 | `FR` | France |
| 1 | `FR1` | Ile de France |
| 2 | `FRB` | Centre - Val de Loire |
| 3 | `FRC` | Bourgogne-Franche-Comte |
| 4 | `FRD` | Normandie |
| 5 | `FRE` | Hauts-de-France |
| 6 | `FRF` | Grand Est |
| 7 | `FRG` | Pays de la Loire |
| 8 | `FRH` | Bretagne |
| ... | ... | ... |

Comparing the observed integer keys:

| integer key | EUROMOD `drgn1` meaning | GSUR lookup meaning for same integer |
| ---: | --- | --- |
| 1 | Ile-de-France | Ile de France |
| 2 | Bassin Parisien | Centre - Val de Loire |
| 3 | Nord-Pas-de-Calais | Bourgogne-Franche-Comte |
| 4 | Est | Normandie |
| 5 | Ouest | Hauts-de-France |
| 6 | Sud-Ouest | Grand Est |
| 7 | Rhone-Alpes, Auvergne | Pays de la Loire |
| 8 | Mediterranee | Bretagne |

Only integer `1` clearly has the same meaning in both systems. The current
direct integer merge therefore appears to be **mechanically valid but
semantically misaligned** for regions `2..8`.

This deserves correction or explicit crosswalk validation before using the
current GSUR coefficients as region-correct labor-market effects. It also
means that the M1 region-dummy work should distinguish:

- region dummies based on the valid EUROMOD `drgn1` variable;
- GSUR values, which need the region-code alignment checked independently.

## 14. Relation Between `drgn1` And `gsur`

`drgn1` is the EUROMOD region category. Under the current merge, `gsur` is an
integer-region-key x sex x education unemployment-rate value; Section 13.3
flags that the integer region key appears semantically misaligned with the
EUROMOD `drgn1` meaning after code `1`.

Distinct GSUR values within each final `drgn1`:

| final variable | within-region distinct values |
| --- | --- |
| singles `gsur` | 5 or 6 per region |
| couples `gsur_male` | 3 per region |
| couples `gsur_female` | 3 per region |

Therefore:

- the current GSUR column varies with the joined integer region key;
- GSUR is not equivalent to a complete region dummy set;
- adding `drgn1` region dummies can still add residual location information
  beyond the existing GSUR shifter.

## 15. Interpretation For Current RURO Modeling

1. In the current M0/M0b/M0c models, GSUR is intended as an opportunity-side
   unemployment shifter.

2. Ignoring the region-key alignment concern for the moment, the current
   realized GSUR extraction rule is effectively:

   ```text
   region x sex x education x broad working-age bracket
   ```

   not:

   ```text
   region x sex x education x fine age bracket
   ```

3. If the goal of a future specification is to add pure regional heterogeneity,
   `drgn1` dummies are not redundant with GSUR.

4. If the goal is to make GSUR age-specific, the current prepared RURO lookup
   would need to retain multiple age groups. The merge code already has support
   for that; the current lookup file does not exploit it.

5. Because GSUR is constant within a household choice set, it helps identify
   between-household opportunity differences, not within-household choice-set
   variation. It enters the model interacted with working status, so it still
   shifts the market-vs-nonmarket margin.

6. Before interpreting the current estimated GSUR coefficient structurally,
   resolve the region-coding issue in Section 13.3. The current column is a
   valid numerical covariate, but the local evidence does not yet support
   calling it a correctly region-matched unemployment rate for all `drgn1`
   groups.

## 16. Audit Verdict

**PASS for mechanical merge integrity.**

The source lookup, actual 2016 merge, and final MNL outputs are internally
consistent:

- correct file used;
- correct units;
- correct sex coding;
- complete coverage for all observed final keys;
- no missing merged GSUR values;
- no row multiplication;
- partner-specific couples values preserved;
- final values exactly match the base-key lookup.

**FLAG for semantic region alignment.**

The integer `drgn1` codes used by EUROMOD final data and the integer `drgn1`
codes generated by the GSUR preparation script appear to represent different
regional classifications after key `1`. The current direct integer join needs
an explicit historical-to-modern regional crosswalk or a GSUR source prepared
under the same regional coding as the EUROMOD `drgn1` variable.

**Important modeling limitation, not a merge bug:**

The current prepared lookup collapses age to `Y20-64`, so the final MNL data do
not currently use age-specific GSUR despite the merge code being able to do so.

**Recommended next data task before structural interpretation of GSUR:**

1. decide whether GSUR should be expressed in the old EUROMOD France region
   coding or in modern NUTS geography;
2. build and document the required region crosswalk explicitly;
3. regenerate the RURO-ready GSUR lookup under that chosen geography;
4. rebuild the MNL files and re-check the merged GSUR values before treating
   the GSUR coefficient as economically interpretable.

## 17. Code Anchors

| behavior | file:line |
| --- | --- |
| RURO lookup construction | `scripts/enhanced/enh_prepare_FR_gsur.py:359` |
| percent-to-proportion conversion | `scripts/enhanced/enh_prepare_FR_gsur.py:468` |
| lookup uniqueness on `year, drgn1, dgn, educ3` | `scripts/enhanced/enh_prepare_FR_gsur.py:473` |
| age-group standardization | `scripts/enhanced/enh_RURO_prep_mnl_basic.py:202` |
| age-to-bracket mapping | `scripts/enhanced/enh_RURO_prep_mnl_basic.py:210` |
| full-age fallback order | `scripts/enhanced/enh_RURO_prep_mnl_basic.py:223` |
| singles merge | `scripts/enhanced/enh_RURO_prep_mnl_basic.py:431` |
| couples merge | `scripts/enhanced/enh_RURO_prep_mnl_basic.py:550` |

## Appendix A. Exact Final Household-Level GSUR Counts

### A.1 Singles `gsur`

| `gsur` | households |
| ---: | ---: |
| 0.040 | 31 |
| 0.048 | 91 |
| 0.049 | 24 |
| 0.050 | 19 |
| 0.052 | 84 |
| 0.053 | 33 |
| 0.056 | 108 |
| 0.058 | 80 |
| 0.062 | 34 |
| 0.066 | 44 |
| 0.068 | 91 |
| 0.070 | 40 |
| 0.074 | 43 |
| 0.077 | 31 |
| 0.080 | 27 |
| 0.086 | 44 |
| 0.089 | 16 |
| 0.095 | 40 |
| 0.098 | 50 |
| 0.099 | 74 |
| 0.103 | 55 |
| 0.105 | 66 |
| 0.110 | 27 |
| 0.120 | 47 |
| 0.124 | 11 |
| 0.125 | 101 |
| 0.130 | 78 |
| 0.131 | 59 |
| 0.149 | 18 |
| 0.153 | 24 |
| 0.159 | 37 |
| 0.163 | 13 |
| 0.164 | 16 |
| 0.165 | 15 |
| 0.172 | 10 |
| 0.174 | 15 |
| 0.189 | 13 |
| 0.200 | 28 |
| 0.202 | 11 |
| 0.210 | 28 |

### A.2 Couples `gsur_male`

| `gsur_male` | households |
| ---: | ---: |
| 0.040 | 95 |
| 0.048 | 143 |
| 0.049 | 88 |
| 0.050 | 82 |
| 0.052 | 117 |
| 0.056 | 203 |
| 0.062 | 118 |
| 0.068 | 161 |
| 0.074 | 131 |
| 0.080 | 110 |
| 0.089 | 85 |
| 0.099 | 240 |
| 0.105 | 108 |
| 0.110 | 131 |
| 0.120 | 134 |
| 0.125 | 262 |
| 0.159 | 63 |
| 0.163 | 31 |
| 0.164 | 49 |
| 0.165 | 44 |
| 0.172 | 24 |
| 0.200 | 40 |
| 0.202 | 57 |
| 0.210 | 61 |

### A.3 Couples `gsur_female`

| `gsur_female` | households |
| ---: | ---: |
| 0.048 | 190 |
| 0.052 | 152 |
| 0.053 | 102 |
| 0.056 | 94 |
| 0.058 | 221 |
| 0.066 | 140 |
| 0.068 | 204 |
| 0.070 | 131 |
| 0.077 | 81 |
| 0.086 | 119 |
| 0.095 | 118 |
| 0.098 | 83 |
| 0.103 | 114 |
| 0.105 | 101 |
| 0.124 | 16 |
| 0.125 | 59 |
| 0.130 | 222 |
| 0.131 | 197 |
| 0.149 | 35 |
| 0.153 | 48 |
| 0.159 | 24 |
| 0.174 | 34 |
| 0.189 | 34 |
| 0.200 | 58 |
