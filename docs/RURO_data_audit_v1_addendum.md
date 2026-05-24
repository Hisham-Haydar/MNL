# RURO Data Audit v1 — Addendum

**Date:** 2026-05-24
**Source dumps:** `U:\EUROMOD-STORAGE\Data\inspecting\predrop_full__{singles,couples}.parquet`
**Chosen rows only** (is_chosen == 1): 1,676 singles, 2,577 couples households.

---

## Section 1 — 1-Hour-Resolution Working-Hours Histogram

Hours rounded to nearest integer. Non-employment (h = 0) excluded. Contract focal bins:
- **PT1**: h ∈ {18, 19, 20, 21}  (contract band 18.5–21.5)
- **PT2**: h ∈ {29, 30}          (contract band 29.5–30.5)
- **FT**: h ∈ {38, 39, 40}       (contract band 37.5–40.5)

### 1.1 Singles (n working = 1,567)

| Hours | Count | % working | Band |
|------:|------:|----------:|------|
| 10 | 9 | 0.57 | |
| 11 | 1 | 0.06 | |
| 12 | 6 | 0.38 | |
| 13 | 2 | 0.13 | |
| 14 | 6 | 0.38 | |
| 15 | 12 | 0.77 | |
| 16 | 6 | 0.38 | |
| 17 | 11 | 0.70 | |
| 18 | 6 | 0.38 | PT1 |
| 19 | 6 | 0.38 | PT1 |
| **20** | **35** | **2.23** | **PT1** |
| 21 | 4 | 0.26 | PT1 |
| 22 | 6 | 0.38 | |
| 23 | 2 | 0.13 | |
| 24 | 16 | 1.02 | |
| 25 | 21 | 1.34 | |
| 26 | 3 | 0.19 | |
| 27 | 10 | 0.64 | |
| 28 | 25 | 1.60 | |
| 29 | 7 | 0.45 | PT2 |
| **30** | **36** | **2.30** | **PT2** |
| 31 | 12 | 0.77 | |
| 32 | 25 | 1.60 | |
| 33 | 9 | 0.57 | |
| 34 | 10 | 0.64 | |
| **35** | **376** | **23.99** | ← **DOMINANT PEAK** |
| 36 | 34 | 2.17 | |
| 37 | 120 | 7.66 | |
| 38 | 63 | 4.02 | FT |
| 39 | 142 | 9.06 | FT |
| **40** | **178** | **11.36** | **FT** |
| 41 | 15 | 0.96 | |
| 42 | 51 | 3.25 | |
| 43 | 14 | 0.89 | |
| 44 | 14 | 0.89 | |
| 45 | 88 | 5.62 | |
| 46–49 | 17 | 1.08 | |
| 50 | 70 | 4.47 | |
| 51–59 | 13 | 0.83 | |
| 60 | 44 | 2.81 | |
| 65–70 | 19 | 1.21 | |

**Peak resolution — singles:**
- Rank 1: **35 h** (376 obs, 24.0%) — dominant peak, OUTSIDE the FT contract bin
- Rank 2: **40 h** (178 obs, 11.4%) — within FT band ✓
- Rank 3: **39 h** (142 obs, 9.1%) — within FT band ✓
- Rank 4: **37 h** (120 obs, 7.7%) — just below FT band (37.5 threshold)
- FT band total (38+39+40): **383 obs, 24.4%** — nearly identical mass to 35 h alone
- **FLAG:** 35 h is a distinct French contractual norm (the "35-heures" workweek law). It sits between PT2 (30 h) and FT (37.5–40.5 h). It is empirically the single largest spike. The contract FT bin (37.5–40.5) captures 24.4% of working singles, while the 35 h spike alone accounts for 24.0%. The 35 h spike is NOT inside any contract focal bin. **Do not silently add a 35 h focal bin — this requires an explicit spec-contract amendment.**

### 1.2 Couples — Male (n working = 2,504)

| Hours | Count | % working | Band |
|------:|------:|----------:|------|
| 10–17 | 13 | 0.52 | |
| 18 | 11 | 0.44 | PT1 |
| 19 | 2 | 0.08 | PT1 |
| **20** | **11** | **0.44** | **PT1** |
| 21 | 1 | 0.04 | PT1 |
| 22–29 | 45 | 1.80 | |
| **30** | **26** | **1.04** | **PT2** |
| 31–34 | 40 | 1.60 | |
| **35** | **573** | **22.88** | ← **DOMINANT PEAK** |
| 36 | 30 | 1.20 | |
| 37 | 169 | 6.75 | |
| 38 | 84 | 3.35 | FT |
| 39 | 233 | 9.31 | FT |
| **40** | **366** | **14.62** | **FT** |
| 41–44 | 132 | 5.27 | |
| **45** | **199** | **7.95** | |
| 46–49 | 49 | 1.96 | |
| **50** | **220** | **8.79** | |
| 51–59 | 79 | 3.15 | |
| **60** | **126** | **5.03** | |
| 65–70 | 81 | 3.23 | |

**Peak resolution — couples male:**
- Rank 1: **35 h** (573 obs, 22.9%) — dominant peak, outside FT bin
- Rank 2: **40 h** (366 obs, 14.6%) — within FT band ✓
- Rank 3: **39 h** (233 obs, 9.3%) — within FT band ✓
- FT band total (38+39+40): **683 obs, 27.3%**
- Notable long-hours mass: 45 h (8.0%), 50 h (8.8%), 60 h (5.0%) — long-hours focal points for men
- **FLAG:** Same 35-heures spike as singles, even larger in absolute terms.

### 1.3 Couples — Female (n working = 2,487)

| Hours | Count | % working | Band |
|------:|------:|----------:|------|
| 10–17 | 98 | 3.94 | |
| 18 | 18 | 0.72 | PT1 |
| 19 | 6 | 0.24 | PT1 |
| **20** | **56** | **2.25** | **PT1** |
| 21 | 11 | 0.44 | PT1 |
| 22–28 | 221 | 8.88 | |
| 29 | 13 | 0.52 | PT2 |
| **30** | **108** | **4.34** | **PT2** |
| 31–34 | 148 | 5.95 | |
| **35** | **606** | **24.37** | ← **DOMINANT PEAK** |
| 36 | 69 | 2.77 | |
| 37 | 203 | 8.16 | |
| 38 | 78 | 3.14 | FT |
| 39 | 181 | 7.28 | FT |
| **40** | **258** | **10.37** | **FT** |
| 41–44 | 78 | 3.13 | |
| 45 | 116 | 4.66 | |
| 46–49 | 23 | 0.92 | |
| 50 | 85 | 3.42 | |
| 51–60 | 60 | 2.41 | |
| 70 | 14 | 0.56 | |

**Peak resolution — couples female:**
- Rank 1: **35 h** (606 obs, 24.4%) — dominant peak, outside FT bin
- Rank 2: **40 h** (258 obs, 10.4%) — within FT band ✓
- Rank 3: **37 h** (203 obs, 8.2%) — just below FT threshold
- Rank 4: **39 h** (181 obs, 7.3%) — within FT band ✓
- FT band total (38+39+40): **517 obs, 20.8%**
- PT2 (30 h): **108 obs, 4.3%** — meaningful secondary spike for women
- **FLAG:** Same 35-heures spike. Also a stronger PT2 spike for women (4.3%) vs men (1.0%).

### 1.4 Cross-group summary and spec-contract implications

| Group | h=35 count | h=35 % | FT band (38–40) % | PT2 (30 h) % | PT1 (20 h) % |
|---|---:|---:|---:|---:|---:|
| Singles | 376 | 24.0% | 24.4% | 2.7% | 2.6% |
| Couples male | 573 | 22.9% | 27.3% | 1.2% | 0.5% |
| Couples female | 606 | 24.4% | 20.8% | 4.9% | 2.9% |

**Conclusion:** The 35 h spike is the single largest discrete mass in all three groups, reflecting the French statutory workweek. The contract FT bin (37.5–40.5 h) captures broadly similar mass (20–27%) but misses 35 h entirely. The previous audit flag ("empirical peak is '35–37.5' bin") was correct: it was driven by the 35 h spike, not by the 37/38 h range. Extending the FT focal bin downward to 35 h is an economic and contractual decision, not a data decision. **Report the 35 h spike as a FLAG and defer to the spec-contract amendment process.**

---

## Section 2 — Variable Decode

All value counts below are from **chosen rows** (n = 1,676 singles). All variables are present in the singles pre-drop dump. Source: EUROMOD DRD FR_2016 (`docs/euromod_reference/DRD_FR_2016_a3_export.txt`).

---

### `ddi` — DEMOGRAPHIC: Disability

**DRD definition:** `ddi = 1 if pl031 == 8; ddi = 0 if pl031 != 8 & pl031 != .`
"ddi contains basic information on whether a person is permanently disabled or/and unfit to work."

| Value | DRD label | Count | % |
|---|---|---:|---:|
| 0.0 | Not disabled | 1,672 | 99.8% |
| 1.0 | Disabled | 4 | 0.2% |

**Note:** Only 4 working-age singles in the estimation sample report disability. The RURO sample already excludes out-of-labour-force statuses (les=8), so this captures only those who report disability status but remain in the active sample. Potentially useful as a preference or opportunity shifter for robustness but near-zero variation makes it unidentifiable as a standalone regressor.

---

### `dcz` — DEMOGRAPHIC: Citizenship

**DRD definition:** `dcz = 1 if pb220a == "LOC"; dcz = 2 if pb220a == "EU"; dcz = 3 if pb220a == "OTH"`

| Value | DRD label | Count | % |
|---|---:|---:|---:|
| 1.0 | This country (French citizen) | 1,607 | 95.9% |
| 2.0 | Other EU citizen | 22 | 1.3% |
| 3.0 | Non-EU citizen | 47 | 2.8% |

**Category:** Immigration/citizenship status. Could proxy for labour market integration barriers (opportunity shifter candidate) but very low non-citizen counts (69 obs combined) limit statistical power.

---

### `dms` — DEMOGRAPHIC: Marital Status

**DRD definition:** `dms = pb190`

| Value | DRD label | Count | % |
|---|---:|---:|---:|
| 1.0 | Single (never married) | 1,124 | 67.1% |
| 2.0 | Married | 75 | 4.5% |
| 4.0 | Divorced | 454 | 27.1% |
| 5.0 | Widowed | 23 | 1.4% |

**Note:** Value 3 (Separated) is absent in chosen rows. Singles sample is by definition not cohabiting couples, so married/separated values reflect legal status vs living arrangement. Divorced singles are 27% of the sample — a substantial group. Could inform preference heterogeneity (household formation history) but is not a standard RURO candidate.

---

### `dmb` — DEMOGRAPHIC: Month of Birth (proxied by quarter)

**DRD definition:** Quarter of birth derived from `rb070`. Values represent mid-month of each quarter.

| Value | DRD label | Count | % |
|---|---:|---:|---:|
| 2.0 | Q1 (Jan–Mar) | 403 | 24.0% |
| 5.0 | Q2 (Apr–Jun) | 465 | 27.7% |
| 8.0 | Q3 (Jul–Sep) | 411 | 24.5% |
| 11.0 | Q4 (Oct–Dec) | 397 | 23.7% |

**Category:** Birth quarter. Roughly uniform distribution (expected). A valid instrument candidate in some IVs for education or earnings, but no obvious RURO role.

---

### `ddt` — DEMOGRAPHIC: Date of Interview

**DRD definition:** `ddt = pb100 * 10000 + pb110` (year × 10000 + month)

| Value | Decoded | Count | % |
|---|---|---:|---:|
| 22016.0 | February 2016 | 1,673 | 99.8% |
| 32016.0 | March 2016 | 3 | 0.2% |

**Note:** All interviews in the RURO 2016 singles sample were conducted in February 2016 (99.8%). Essentially a constant — zero variation. No estimation use.

---

### `dcu` — DEMOGRAPHIC: Consensual Union

**DRD definition:** Indicator for cohabiting without formal marriage. Binary: 1 = in consensual union, 0 = not.

| Value | DRD label | Count | % |
|---|---:|---:|---:|
| 0.0 | Not in consensual union | 1,601 | 95.5% |
| 1.0 | In consensual union | 75 | 4.5% |

**Note:** Singles sample definition allows consensual unions (not cohabiting opposite-sex partners counted as couples). The 75 individuals in consensual unions are cohabiting but classified as singles in RURO (partner not a ruro_decider or different household type). Could overlap with `dms = 2` (married).

---

### `dncsy` — DEMOGRAPHIC: Number of children born in survey year

**DRD definition:** Children born after income reference period (`rb080 = rb010`), assigned to parent.

| Value | Count | % |
|---|---:|---:|
| 0.0 | 1,675 | 99.9% |
| 1.0 | 1 | 0.1% |

**Note:** Near-zero variation (1 obs). Not usable as a regressor.

---

### `dehde` — DEMOGRAPHIC: Education — Highest Status (detailed ISCED)

**DRD definition:** Detailed ISCED classification (`pe040`). Values are ISCED numeric codes.

| Value | ISCED label | Count | % |
|---|---|---:|---:|
| 0.0 | Less than primary / pre-school | 48 | 2.9% |
| 100.0 | Primary (ISCED 1) | 44 | 2.6% |
| 200.0 | Lower secondary (ISCED 2) | 164 | 9.8% |
| 344.0 | General upper secondary — access to tertiary (ISCED 3A) | 183 | 10.9% |
| 353.0 | Vocational upper secondary — no access to tertiary (ISCED 3C) | 465 | 27.7% |
| 354.0 | Vocational upper secondary — with access to tertiary (ISCED 3B/3C) | 88 | 5.3% |
| 440.0 | Post-secondary non-tertiary (ISCED 4) | 5 | 0.3% |
| 500.0 | Tertiary (ISCED 5+) | 679 | 40.5% |

**Note:** This is the detailed version of `deh` (which collapses to 3 categories: L/M/H). The `educH` dummy in the model corresponds to value 500 (40.5% of sample). Vocational upper secondary (353) is the single largest non-tertiary group (27.7%). Could justify splitting `educM` into vocational vs general upper secondary as a robustness extension — but that is a spec-contract decision.

---

### `dey` — DEMOGRAPHIC: Education — Number of Years

**DRD definition:** Years of schooling derived from `deh` bracket.

| Value | Mapped from deh | Count | % |
|---|---|---:|---:|
| 0.0 | deh = 0 (no primary) | 48 | 2.9% |
| 5.0 | deh = 1 (primary) | 44 | 2.6% |
| 8.0 | deh = 2 (lower secondary) | 164 | 9.8% |
| 13.0 | deh = 3 or 4 (upper secondary / post-secondary) | 741 | 44.2% |
| 18.0 | deh = 5 (tertiary) | 679 | 40.5% |

**Note:** Ordinal version of `deh`. Five distinct values, all coarsely mapped. The `pexp_years` variable already uses a Mincer-style potential experience measure. `dey` is a blunt alternative — less precise than `deh` dummies and not additionally informative given those dummies are already in the model.

---

### `dew` — DEMOGRAPHIC: Education — Year When Highest Status Achieved

**DRD definition:** `dew = pe030` — year when highest education level was completed. Value -1 indicates not applicable (no education or pre-primary).

| Value | Interpretation | Count | % |
|---|---|---:|---:|
| -1.0 | Not applicable / no education | 48 | 2.9% |
| 1965–1979 | Graduated before 1980 | 147 | 8.8% |
| 1980–1989 | Graduated 1980–1989 | 374 | 22.3% |
| 1990–1999 | Graduated 1990–1999 | 409 | 24.4% |
| 2000–2009 | Graduated 2000–2009 | 339 | 20.2% |
| 2010–2016 | Graduated 2010–2016 | 359 | 21.4% |

(Full 1-year distribution available in variable_inventory_singles.csv)

**Note:** Can be used to construct an alternative experience proxy `pexp_alt = survey_year - dew` alongside `pexp_years`. However, `pexp_years` is already in the model as the Mincer experience variable. `dew` provides the same information via a different construction path. Redundant with `pexp_years` for the wage equation but may be useful as a cross-check.

---

### `drgn2` — DEMOGRAPHIC: Region — NUTS Level 2

**DRD definition:** Derived from `db040` (NUTS-2 region code). 22 categories for metropolitan France (codes FR10–FR83); overseas territories coded 23–26 (FR91–FR94) and FRZZ (code 27). In the RURO sample, only codes 1–22 appear (no overseas).

| Value | NUTS-2 code | Region name | Count | % |
|---|---|---|---:|---:|
| 1 | FR10 | Île-de-France | 271 | 16.2% |
| 2 | FR21 | Champagne-Ardenne | 30 | 1.8% |
| 3 | FR22 | Picardie | 50 | 3.0% |
| 4 | FR23 | Haute-Normandie | 47 | 2.8% |
| 5 | FR24 | Centre | 66 | 3.9% |
| 6 | FR25 | Basse-Normandie | 29 | 1.7% |
| 7 | FR26 | Bourgogne | 47 | 2.8% |
| 8 | FR30 | Nord-Pas-de-Calais | 126 | 7.5% |
| 9 | FR41 | Lorraine | 64 | 3.8% |
| 10 | FR42 | Alsace | 47 | 2.8% |
| 11 | FR43 | Franche-Comté | 34 | 2.0% |
| 12 | FR51 | Pays de la Loire | 126 | 7.5% |
| 13 | FR52 | Bretagne | 120 | 7.2% |
| 14 | FR53 | Poitou-Charentes | 51 | 3.0% |
| 15 | FR61 | Aquitaine | 79 | 4.7% |
| 16 | FR62 | Midi-Pyrénées | 93 | 5.6% |
| 17 | FR63 | Limousin | 18 | 1.1% |
| 18 | FR71 | Rhône-Alpes | 179 | 10.7% |
| 19 | FR72 | Auvergne | 18 | 1.1% |
| 20 | FR81 | Languedoc-Roussillon | 70 | 4.2% |
| 21 | FR82 | Provence-Alpes-Côte d'Azur | 105 | 6.3% |
| 22 | FR83 | Corse | 6 | 0.4% |

**Note:** Fine-grained regional variation. The model already uses `reg_nuts1_1` through `reg_nuts1_8` (NUTS-1 dummies) in kept columns. `drgn2` is the more granular NUTS-2 level, currently dropped. Could be a promotion candidate for regional opportunity shifters (e.g., regional labour market conditions beyond `gsur`), but sample sizes at NUTS-2 are thin (Limousin n=18, Auvergne n=18, Corse n=6).

---

### `drgur` / `drgmd` / `drgru` — DEMOGRAPHIC: Urban / Middle density / Rural region

**DRD definition:** Derived from `db100` (degree of urbanisation, Eurostat classification).

| Variable | DRD label | Condition | Count (=1) | % |
|---|---|---|---:|---:|
| `drgur` | Urban region | `db100 == 1` | 907 | 54.1% |
| `drgmd` | Middle density region | `db100 == 2` | 345 | 20.6% |
| `drgru` | Rural region | `db100 == 3` | 424 | 25.3% |

**Note:** These three are mutually exclusive and exhaustive (each person is in exactly one). Together they form the degree-of-urbanisation classification. Could be useful as opportunity shifters (urban labour markets vs rural) or as additional preference shifters (commuting costs, local amenities). Together they add 2 df (one is reference). Non-trivial variation across all three groups.

---

## Section 3 — GSUR Variation and Non-Working Chosen Rows

### 3.1 GSUR variation (chosen rows only)

| Variable | Group | Std | Min | Max | N distinct cells |
|---|---|---:|---:|---:|---:|
| `gsur` | Singles | 0.0420 | 0.040 | 0.210 | 40 |
| `gsur_male` | Couples male | 0.0444 | 0.040 | 0.210 | 24 |
| `gsur_female` | Couples female | 0.0384 | 0.048 | 0.200 | 24 |

**Interpretation:** GSUR varies across 40 distinct cells for singles and 24 for each gender in couples. The cells are defined by `(educ3 × age_group × year)` strata from the GSUR lookup table. The narrower range for `gsur_female` (0.048–0.200) vs `gsur_male` (0.040–0.210) reflects lower unemployment rates for the highest-education female group. This variation is sufficient for identification of the opportunity shifter coefficient but is coarser than a continuous variable.

### 3.2 Non-working chosen rows (h = 0 at observed alternative)

| Group | Non-working | Total chosen | % non-working |
|---|---:|---:|---:|
| Singles | 109 | 1,676 | 6.5% |
| Couples — male | 73 | 2,577 | 2.8% |
| Couples — female | 90 | 2,577 | 3.5% |

**Note:** Non-employment rates are low in this sample because the RURO prep already filters to working-age deciders and the SRCV/EU-SILC sample skews toward employed respondents. The 6.5% singles non-employment rate drives the importance of the opportunity model (it is not merely a preference model — a non-trivial share choose h = 0).

### 3.3 Within-household gsur_male vs gsur_female divergence (couples)

Within the 2,577 chosen couple households:

- Households where `gsur_male ≠ gsur_female`: **2,188** (84.9% of households)
- Mean absolute difference conditional on divergence: **0.0370**

**Interpretation:** In 85% of couple households the male and female partner face different group-specific unemployment rates. This is expected and correct — the GSUR is stratified by `(gender × educ3 × age_group)`, so spouses typically fall in different cells. The mean gap of 3.7 percentage points is economically meaningful. This confirms that `gsur_male` and `gsur_female` are genuinely distinct instruments for the male and female opportunity equations, not duplicates.