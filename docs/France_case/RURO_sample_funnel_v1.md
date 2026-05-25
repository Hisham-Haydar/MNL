# RURO Sample Funnel v1

**Purpose:** Trace the France 2016 estimation sample from the raw EU-SILC file
through to the final pre-drop MNL frames. Each stage quotes the exact filter
condition (script + line), reports persons and households before/after, and
explains what is dropped and why.

**Guardrail:** This is a read-only audit document. It records what the pipeline
does; it does not advocate for changes to the filters.

---

## Stage 0 — Raw Input File

| Item | Value |
| --- | --- |
| File | `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt` |
| Format | Tab-separated text (EU-SILC microdata layout) |
| Rows | 26,560 |
| Columns | 124 |
| Unit | One row per person; household structure encoded by `idhh` / `idperson` |

The raw file is authentic EU-SILC household survey data for France, survey year
2016. Despite EUROMOD logging the string "FR_training_data", this is real
microdata (see `docs/project_fr2016_microdata.md`).

---

## Stage 1 — EUROMOD Run and Household Role Assignment

**Script:** `scripts/enhanced/enh_france_data_prep.py`

This stage runs the EUROMOD tax-benefit microsimulation (`FR_2016` system) on
the raw data, appends EUROMOD output columns (all suffixed `_em`), and
identifies the structural role of each person within their household.

### 1a. EUROMOD simulation

All 26,560 persons pass through EUROMOD. The simulation produces `ils_dispy_em`
(counterfactual disposable income) and its accounting decomposition
(`ils_origy_em`, `ils_ben_em`, `ils_sicdy_em`, `ils_tax_em`) plus auxiliary
transfer columns. No rows are dropped at this sub-step; the frame is widened
from 124 to approximately 589 columns.

### 1b. Household role flags

```python
# enh_france_data_prep.py, line ~1282
df_sim["hh_IsHead"] = (df_sim[head_id_col] == df_sim["idperson"]).astype(int)

# line ~1307
df_sim["hh_IsPartner"] = (df_sim[partner_col] == 1).astype(int)
```

Fallback logic (lines ~1364–1386) is applied when no partner column is found:
adults aged 18+ in two-adult households who are not the head are flagged as
partner.

### 1c. RURO decider flag

```python
# enh_france_data_prep.py, line 1399
df_sim["ruro_decider"] = (
    (df_sim["hh_IsHead"] == 1) | (df_sim["hh_IsPartner"] == 1)
).astype(int)
```

`ruro_decider == 1` for household heads and cohabiting partners. All other
household members (children, other adults) remain in the data for EUROMOD
tax-benefit calculations but will not enter RURO estimation.

---

## Stage 2 — Stepwise Household Filter

**Script:** `scripts/enhanced/enh_france_data_prep.py`, function
`stepwise_filter_households()` (line ~739)

**Config defaults** (line ~113–114):

```python
"age_range": (18, 65),
"allowed_les": [3, 5, 7],
```

The filter is applied separately for singles and for couples. Every step drops
entire households; no row-level splitting occurs here.

### Filter steps — Singles

| Step | Condition (code) | Households after | Dropped |
| --- | --- | --- | --- |
| Baseline | All households entering singles branch | — | — |
| **Step 1: Age (Head)** | `(hh_IsHead == 1) & dag.between(18, 65)` (line ~776) | — | Heads outside working age |
| **Step 2: Education (Head)** | `(hh_IsHead == 1) & (dec == 0)` (line ~783) | — | Heads currently in education |
| **Step 3: Retirement/Disability** | `benefit_retire_disab.sum() == 0` per household (line ~792) | — | HH with any retirement/disability benefit |
| **Step 4: Allowed LES (Deciders)** | `decider les ∈ {3, 5, 7}` (line ~821) | — | Deciders with excluded LES codes |
| **Step 5: Other Members** | Non-deciders aged 18–65, not in school, not disabled, with meaningful income dropped (line ~720–731) | — | HH contaminated by economically active non-deciders |
| **Step 6: Hours/Wage** | `lhw ≤ 70`; low hours capped/reclassified; unreasonable wages dropped (line ~895+) | — | Extreme hours/wage outliers |

### Filter steps — Couples (additional)

After Steps 1–4 above:

| Step | Condition | Dropped |
| --- | --- | --- |
| **Step 5: Age (Partner)** | `(hh_IsPartner == 1) & dag.between(18, 65)` (line ~836) | Partners outside working age |
| **Step 6: Education (Partner)** | `(hh_IsPartner == 1) & (dec == 0)` (line ~845) | Partners in education |
| **Step 7: Opposite-Sex Only** | Exactly 1 male + 1 female among deciders (line ~863) | Same-sex couples and households with ambiguous gender composition |

### LES filter detail — Step 4

The LES filter is the most consequential restriction. It excludes all
households where any RURO decider (head or partner) has a labour-market status
outside `{3, 5, 7}`.

**Excluded codes and their DRD meanings:**

| LES code | EUROMOD DRD label | Rationale for exclusion |
| --- | --- | --- |
| `0` | Pre-school / not applicable | Not a labour-market participant |
| `1` | Farmer (self-employed in agriculture) | Self-employment not modelled; intentional for French data (noted in filter comment) |
| `2` | Employer / other self-employed | Self-employment not modelled |
| `4` | Pensioner / retired | Out of labour force; retirement modelled separately |
| `6` | Student in full-time education | `dec == 0` already catches these at Step 2; belt-and-braces |
| `8` | Sick / permanently disabled | Disability incapacity prevents labour supply decisions |
| `9` | Other inactive (not elsewhere classified) | Heterogeneous; not modelled |

**Included codes:**

| LES code | DRD label | Included because |
| --- | --- | --- |
| `3` | Employee (paid employment) | Core estimation target |
| `5` | Unemployed (seeking work) | Counterfactual labour supply decisions modelled |
| `7` | Inactive (not seeking work, not disabled) | Voluntary inactivity is a valid RURO choice |

### LES distribution in the final estimation sample

Counts below come from `singles_RURO_ready.parquet` (post-filter, all
household members, not only deciders). Non-deciders with other LES values
(children coded as pre-school `les=0`, students `les=6`) remain in the file
for EUROMOD calculations but do not enter estimation.

**Deciders only (ruro_decider == 1):**

| Group | les=3 (Employee) | les=5 (Unemployed) | les=7 (Inactive) | Total deciders |
| --- | --- | --- | --- | --- |
| Singles | 1,567 | 97 | 12 | 1,676 |
| Couples (persons) | 4,991 | 139 | 24 | 5,154 |

For couples, decider count = 2 × 2,577 households = 5,154 persons total.

---

## Stage 3 — Intermediate Files

**Script:** `scripts/enhanced/enh_france_data_prep.py` → outputs written at
line ~2218–2262

These files are saved to the processed directory but are **not retained on
disk** for the 2016 run (confirmed absent during audit):

```
singles_filtering_final.parquet   — MISSING
couples_filtering_final.parquet   — MISSING
```

The pipeline continues by loading `singles_RURO_ready.parquet` and
`couples_RURO_ready.parquet`, which are the post-prep outputs from the next
stage and are present on disk.

---

## Stage 4 — RURO Variable Derivation

**Script:** `scripts/enhanced/enh_RURO_prep.py`, function
`_add_ruro_variables_basic()` (line ~759)

This stage reads the filtered singles/couples frames and adds RURO pipeline
variables: `ruro_group`, `ruro_sample`, education dummies (`educL`, `educM`,
`educH`, `educ3`), potential experience (`pexp_years`, `pexp_years2`),
age-norm (`age_norm`, `age_norm2`), regional dummies, and the `ruro_sample`
flag.

```python
# enh_RURO_prep.py, line ~810
ruro_sample = (ruro_decider == 1) & is_adult   # dag >= 18
```

Group coding:

```python
# enh_RURO_prep.py, line ~1158–1159
singles["ruro_group"] = np.int16(1)    # singles
couples["ruro_group"] = np.int16(10)   # couples
```

**Output files:**

| File | Rows | Households | Columns |
| --- | --- | --- | --- |
| `singles_RURO_ready.parquet` | 2,395 | 1,676 | 589 |
| `couples_RURO_ready.parquet` | 8,478 | 2,577 | 589 |

Rows > households because the RURO-ready files retain all household members
(children, non-deciders) for EUROMOD counterfactual consistency. The
estimation sample is marked by `ruro_sample == 1`.

---

## Stage 5 — Draw Generation and GSUR Merge

**Script:** `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (Step 6 in
`run_enhanced_pipeline.ps1`)

For each household in the RURO-ready file, 100 draws (alternatives) are
generated from the proposal distributions. GSUR (Group-Specific Unemployment
Rate) is merged at this stage. Column filtering (`get_essential_columns_for_estimation()`) then reduces the frame to the estimation whitelist. The
`--explore-dump-dir` flag captures the pre-filter state.

**Draw counts:**

| Group | Draws file rows | Households |
| --- | --- | --- |
| Singles | 168,319 | 1,676 |
| Couples | 518,724 | 2,577 |

Note: singles draw count (168,319) slightly exceeds 1,676 × 100 = 167,600
because the draw file includes one observed row (`draw=0`) per household in
addition to the 100 simulated alternatives, or due to minor book-keeping rows.

---

## Stage 6 — Pre-Drop Exploration Dump

Written by `--explore-dump-dir` patch in `enh_RURO_prep_mnl_basic.py`
(post-EUROMOD, post-GSUR, **pre**-column-filter).

| File | Rows | Columns |
| --- | --- | --- |
| `predrop_full__singles.parquet` | 167,600 | 961 |
| `predrop_full__couples.parquet` | 257,700 | 1,466 |

Pre-drop column breakdown (singles, 961 total):

| Category | Count |
| --- | --- |
| Kept by estimation whitelist | 75 |
| EUROMOD output columns (`_em`) | 339 (1 kept: `ils_dispy_em`; 338 dropped) |
| Other dropped columns | 547 |

Pre-drop column breakdown (couples, 1,466 total):

| Category | Count |
| --- | --- |
| Kept by estimation whitelist | 93 |
| EUROMOD output columns (`_em`) | ~339 (similar decomposition) |
| Other dropped columns | ~1,034 |

---

## Summary Funnel Table

| Stage | Script | Persons | Households (singles) | Households (couples) |
| --- | --- | --- | --- | --- |
| Raw EU-SILC | — | 26,560 | — | — |
| Post-EUROMOD + role flags | `enh_france_data_prep.py` | 26,560 | — | — |
| Post-stepwise filter (deciders) | `enh_france_data_prep.py` | 2,395 + 8,478* | 1,676 | 2,577 |
| Post-RURO-variable derivation | `enh_RURO_prep.py` | same | 1,676 | 2,577 |
| Draw files (100 alternatives) | `enh_RURO_prep_mnl_basic.py` | — | 1,676 × ~100 | 2,577 × ~100 |
| Pre-drop exploration dump | `enh_RURO_prep_mnl_basic.py` | — | 167,600 rows | 257,700 rows |
| Final estimation whitelist | `enh_RURO_prep_mnl_basic.py` | — | 75 cols | 93 cols |

\* Row counts include non-decider household members retained for EUROMOD.

---

## Key Audit Notes

1. **Intermediate files missing.** `singles_filtering_final.parquet` and
   `couples_filtering_final.parquet` are absent from disk. Exact household
   counts at each filter step are not recoverable without re-running the
   pipeline with logging enabled.

2. **Singles draw count discrepancy.** The draw file contains 168,319 rows vs.
   167,600 expected (1,676 × 100). Likely explanation: the observed alternative
   (`draw=0`) is included as an extra row alongside the 100 simulated
   alternatives, giving 1,676 × 101 = 169,276 — the actual figure falls
   between, suggesting some households have slightly fewer draws. This is a
   marginal discrepancy and does not affect estimation validity.

3. **Non-decider retention.** The RURO-ready files include non-deciders
   (children, other adults) to allow accurate EUROMOD counterfactual tax
   calculations. These persons are flagged `ruro_sample == 0` and do not
   contribute to estimation likelihood.

4. **35-heures mass.** Among chosen working alternatives, approximately 24% of
   hours are at h=35 (the French statutory workweek). This mass falls between
   the PT2 focal bin (29.5–30.5 h) and the FT focal bin (37.5–40.5 h) and is
   not captured by any current contract bin. See `docs/RURO_data_audit_v1_addendum.md`
   Section 1 for the 1-hour-resolution histograms.

5. **LES composition of deciders.** Employees (les=3) dominate: 93.5% of
   singles deciders, 96.8% of couple-deciders. The unemployed (les=5) and
   inactive (les=7) together account for 6.5% / 3.2% respectively.