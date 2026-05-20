# RURO GSUR Rebuild — Specification Memo v1

Date: 2026-05-15

Scope: design document for rebuilding the GSUR (group-specific
unemployment rate) data lookup and merge to resolve two issues
identified by the GSUR source-and-merge audit:
(1) the integer region crosswalk mismatch between EUROMOD `drgn1`
    (old 8-region classification) and the current GSUR lookup
    (modern 13-region NUTS classification);
(2) the unused age-specificity in the source workbook, which the
    current pipeline collapses to `Y20-64` for all observations.

This memo locks the data design decisions before any code is written.
It is parallel in structure to the M0b and M0c design memos and is the
reference document for the implementation prompt that follows.

Inputs to this memo:
- `docs/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md`
- `docs/RURO_occ_M0c_b2_verdict_v1.md`
- `docs/JMP_ability_vs_opportunity_framework_v1.md`
- `scripts/enhanced/enh_prepare_FR_gsur.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- The source GSUR workbook: `Data/external/FR_gsur.xlsx`
- The published INSEE crosswalk: modern NUTS → old EUROMOD `drgn1`

---

## 1. Purpose

The current GSUR variable in the MNL parquets fails on two fronts that
together prevent clean substantive interpretation in M1-clean:

(a) **Semantic misalignment**: integer keys mean different regions in
the EUROMOD `drgn1` system and the current GSUR lookup. Only integer 1
(Île-de-France) is unambiguously matched; integers 2–8 represent
different regional classifications in each system.

(b) **Age-collapse**: the source workbook supports fine age groups
(Y15-24, Y25-34, Y35-44, Y45-54, Y55-64) but the current lookup
collapses to Y20-64 for everyone. The audit (§5.2 of the audit memo)
shows the empirical impact can be 4× for young low-education workers.

The rebuild produces:
- A regionally-corrected GSUR lookup using the published INSEE
  crosswalk from modern NUTS regions to old EUROMOD `drgn1` codes.
- Multiple age-specific GSUR variables (UR1, UR2, ...) exposed in the
  MNL parquets, replacing the current single `gsur`.
- Documentation of the chosen aggregation methodology.

After the rebuild, M0c_b2 is re-estimated against the corrected data.
The estimated parameters should shift only slightly (the verdict
memo's findings stand); the substantive interpretation of `β_E_gsur`
becomes clean for the first time.

---

## 2. The three locked decisions

From the chat dialogue on 2026-05-15:

(D1) **Use Option A: align GSUR to the EUROMOD `drgn1` 8-region
coding** (rather than re-derive `drgn1` from modern NUTS). Rationale:
the EUROMOD pipeline is the authoritative source for the rest of the
project's variables; re-deriving `drgn1` would require touching the
EUROMOD prep pipeline and possibly the EU-SILC raw data, which is on
a separate access agreement. Aggregating modern NUTS into old EUROMOD
regions uses the published INSEE crosswalk and is a clean, defensible
data operation.

(D2) **Use population-weighted aggregation** when collapsing multiple
modern NUTS regions into one old EUROMOD region. Rationale: this is
the INSEE convention for backward-compatible regional aggregation,
preserves the labour-market relevance of the aggregated rate, and is
the literature standard.

(D3) **Expose multiple age-specific levels of the unemployment rate**
(UR1, UR2, ...). The MNL parquets will carry not one `gsur` but
several (e.g., UR_Y20_29, UR_Y30_44, UR_Y45_64, etc.) so the structural
model can use age-appropriate unemployment shifters via interactions
or as alternative covariates. This is the user-requested feature from
the dialogue.

---

## 3. The INSEE crosswalk: modern NUTS → old EUROMOD `drgn1`

The crosswalk for aggregating modern NUTS-1 / NUTS-2 regions into the
old EUROMOD 8-region grouping:

| EUROMOD `drgn1` | Old name | Modern NUTS-1/NUTS-2 components |
|---|---|---|
| 1 | Île-de-France | FR1 (= FR10 = Île-de-France) |
| 2 | Bassin Parisien | FRB (Centre-Val de Loire) + FRD (Normandie, Basse-Normandie portion only) + parts of FRD (Haute-Normandie portion) + parts of FRG (Pays de la Loire, certain departments only) |
| 3 | Nord-Pas-de-Calais | Part of FRE (Hauts-de-France, Nord-Pas-de-Calais portion only) |
| 4 | Est | Part of FRE (Hauts-de-France, Picardie portion) + FRF (Grand Est, eastern portion: Alsace + Lorraine) |
| 5 | Ouest | Part of FRG (Pays de la Loire, western portion) + FRH (Bretagne) + part of FRJ (Poitou-Charentes / Nouvelle-Aquitaine western portion) |
| 6 | Sud-Ouest | Part of FRI + FRJ (Aquitaine + Limousin + parts of Midi-Pyrénées) |
| 7 | Rhône-Alpes / Auvergne | FRK (Auvergne-Rhône-Alpes) |
| 8 | Méditerranée | FRL (Provence-Alpes-Côte d'Azur) + FRM (Corse) + parts of FRJ (Languedoc-Roussillon portion) |

**Important note**: the modern French NUTS reform in 2016 consolidated
22 regions into 13. The old EUROMOD 8-region groupings sometimes split
a modern NUTS region (e.g., the old Bassin Parisien used Lower Normandy
but not the rest of Normandie). The crosswalk is therefore not a clean
many-to-one map; it requires the **NUTS-2 or NUTS-3 level disaggregation**
within some modern NUTS-1 regions.

**Implementation decision**: use the most-granular available NUTS level
(NUTS-2 or NUTS-3) in the Eurostat source, then aggregate to old EUROMOD
groupings using population weights at the NUTS-2/3 level.

If NUTS-2 disaggregation is not available for a particular GSUR cell in
the source data, the cell is excluded (rather than misallocated). The
implementation prompt should track which cells were excluded.

---

## 4. The age-specificity decision

The source workbook supports the following age groups:

| age group code | range |
|---|---|
| Y15-24 | 15-24 |
| Y25-34 | 25-34 |
| Y35-44 | 35-44 |
| Y45-54 | 45-54 |
| Y55-64 | 55-64 |
| Y20-64 | broad working age (current collapse) |

The MNL data are age-restricted to working-age adults; specifically the
RURO sample has age 16-65. The age-specific GSUR lookup should expose
**four age groups** (UR1 through UR4) with the following partition:

| MNL covariate | covers ages | source GSUR concept |
|---|---|---|
| UR1 | 16-25 | Y15-24 (best available; small discrepancy at age 15 not in MNL) |
| UR2 | 26-35 | Y25-34 |
| UR3 | 36-45 | Y35-44 |
| UR4 | 46-65 | combines Y45-54 and Y55-64 via population-weighted average within each region × sex × education cell |

(The user can refine the partition; UR4 spanning 46-65 is one possible
choice, but UR4/UR5 could be split if there's empirical reason.)

**Sample-level UR variable**: each household carries the UR variable
corresponding to its head-of-household age. For couples, both
`UR_male` and `UR_female` are exposed (partner-specific, matching the
current sex-by-education-by-region-by-age cell structure).

**Backward compatibility**: the legacy single `gsur` column (effective
Y20-64) is also kept in the parquet for parametric continuity with
M0c_b2. Estimation specs can choose to use the legacy `gsur` or the
new age-specific UR variables, but not both.

---

## 5. The GSUR rebuild output schema

After the rebuild, the MNL parquets will carry:

### 5.1 Singles parquet — new columns

| column | type | description |
|---|---|---|
| `gsur_legacy` | float | the current Y20-64 GSUR (renamed from `gsur`) |
| `gsur` | float | UR-by-age for the singles person; same as one of UR1-UR4 |
| `UR1` | float | unemployment rate for ages 16-25 |
| `UR2` | float | unemployment rate for ages 26-35 |
| `UR3` | float | unemployment rate for ages 36-45 |
| `UR4` | float | unemployment rate for ages 46-65 |
| `age_group_used` | string | one of Y15-24, Y25-34, ..., Y45-54, Y55-64; determined by `dag` |

All UR variables are in proportion form (0.00 = 0%, 1.00 = 100%) per the
existing convention.

### 5.2 Couples parquet — new columns

| column | type | description |
|---|---|---|
| `gsur_male_legacy`, `gsur_female_legacy` | float | the current Y20-64 partner-specific GSUR |
| `gsur_male`, `gsur_female` | float | UR-by-age for each partner |
| `UR1_male`, ..., `UR4_male` | float | male unemployment rates by age band |
| `UR1_female`, ..., `UR4_female` | float | female unemployment rates by age band |
| `age_group_used_male`, `age_group_used_female` | string | per-partner age group used |

### 5.3 Variable interpretation

All UR variables are correctly aligned to the EUROMOD `drgn1` 8-region
classification. The merge integer matches the EUROMOD documentation
(integer 1 = Île-de-France, integer 2 = Bassin Parisien, ..., integer 8
= Méditerranée).

For each (region × sex × education × age) cell, the UR is the
population-weighted average of the corresponding modern NUTS regions'
unemployment rate for that sex × education × age cell.

If a cell has fewer than 100 individuals across the modern NUTS
components (a Eurostat small-cell threshold), the cell is flagged as
"imputed-small-cell" and uses the next-coarser age group as fallback.
The implementation prompt should specify the small-cell handling.

---

## 6. The implementation pipeline

The rebuild consists of three sequential code changes:

### 6.1 Step 1: New GSUR preparation script

**Create**: `scripts/enhanced/enh_prepare_FR_gsur_v2.py` (new file,
not modification of the existing v1).

**Inputs**:
- `Data/external/FR_gsur.xlsx` (the existing source workbook)
- A new file `Data/external/insee_nuts_to_drgn1_crosswalk.csv` (created
  in this rebuild) containing the modern NUTS code, the EUROMOD `drgn1`
  integer, and the population weight for each modern NUTS region

**Output**:
- `Data/external/FR_gsur_ruro_v2.parquet`

**Key operations**:
1. Read source workbook
2. Extract GSUR cells at the finest available aggregation (region × sex
   × education × age_group)
3. Apply the INSEE crosswalk to remap modern NUTS regions to old
   EUROMOD `drgn1` integers
4. Apply population weights to aggregate when multiple modern regions
   map to a single old region
5. Convert percent to proportion (existing code uses `df["gsur"] / 100`)
6. For each age group, produce a separate lookup keyed on
   `(year, drgn1, dgn, educ3, age_group)`
7. Validate cell sizes; flag small-cell imputations
8. Save the v2 lookup parquet

### 6.2 Step 2: New MNL merge script

**Create**: `scripts/enhanced/enh_RURO_prep_mnl_basic_v2.py` (new file)
or modify the existing `enh_RURO_prep_mnl_basic.py` (preferred — keeps
the merge logic in one place).

**Modifications to merge logic**:
- For singles: based on each household's `dag`, look up the appropriate
  age group and merge the matching UR. Also expose all four UR1-UR4 as
  separate columns.
- For couples: separately for `dag_male` and `dag_female`, look up the
  matching UR. Both `UR1_male...UR4_male` and `UR1_female...UR4_female`
  are exposed.

### 6.3 Step 3: Regenerate the MNL parquets

**Run** the modified `enh_RURO_prep_mnl_basic.py` (or v2) end-to-end
to produce:
- `Z:/.../fr_2016_RURO_mnl__singles_v2.parquet`
- `Z:/.../fr_2016_RURO_mnl__couples_v2.parquet`

The v2 parquets contain everything in v1 plus the new UR columns. They
must be byte-equivalent to v1 on all non-GSUR columns. Verify with a
diff check.

After verification, the v2 parquets become the new canonical MNL
files. The v1 parquets are retained in `archive/` for reference.

---

## 7. The validation plan

After the rebuild, run the following checks before declaring the
rebuild successful:

(V1) **Île-de-France parity check**. For all Île-de-France households
(`drgn1 = 1`), the v2 GSUR must be within 1% of the v1 GSUR for the
same (sex × education × Y20-64) cell. This confirms the rebuild has not
moved the one region whose coding was correct in v1.

(V2) **Cross-region GSUR comparison**. For each `drgn1 = 2..8`, compute
the mean v1 GSUR and the mean v2 GSUR. The differences quantify the
crosswalk correction. Expected pattern: v2 GSUR for `drgn1 = 2` (Bassin
Parisien) should reflect the aggregate of multiple modern NUTS regions
including Centre-Val de Loire, parts of Normandie, etc., averaged with
population weights.

(V3) **Cell-size audit**. For each (region × sex × education × age)
cell, report the implied population from the source. Flag any cell with
< 100 individuals (the Eurostat small-cell threshold) and document
the fallback used.

(V4) **Age-monotonicity sanity check**. Unemployment rates should
generally peak for ages 16-24 (UR1) and decline for older age bands
(UR4). If the pattern is reversed for a substantial number of cells,
the age-specific rebuild may have an error.

(V5) **Magnitude sanity check**. The mean UR across the working-age
population should be close to the published French total unemployment
rate for 2016 (~9.8% per INSEE). If the rebuild produces a mean that
differs by > 0.5 percentage points, debug.

(V6) **M0c_b2 re-estimation validation**. After the rebuild, re-run
M0c_b2 with the corrected `gsur` (use age-appropriate UR via a single
column for back-compatibility; the multi-UR exposure is for M1-clean).
Verify the estimated `β_E_gsur` changes but other parameters are
essentially unchanged.

---

## 8. Implementation phases and deliverables

| phase | deliverable | tool | time |
|---|---|---|---|
| Phase 1 | INSEE crosswalk CSV: modern NUTS → drgn1 → population weight | manual data work + Claude Code | 1 hour |
| Phase 2 | `enh_prepare_FR_gsur_v2.py` script | Claude Code | 2 hours |
| Phase 3 | Validation V1-V5 of the v2 GSUR lookup | Claude Code | 30 min |
| Phase 4 | Modified MNL merge (`enh_RURO_prep_mnl_basic.py` update) | Claude Code | 1 hour |
| Phase 5 | Regenerated v2 MNL parquets | Claude Code | 30 min |
| Phase 6 | V6 — re-run M0c_b2 with corrected GSUR | Claude Code | 5 min compute + analysis |
| Phase 7 | Comparative analysis: v1 vs v2 GSUR-coefficient changes | this chat + Claude Code | 30 min |

Total estimated time: ~5-6 hours of focused work spread across the
phases. Phases 1-5 are pure data work and produce a corrected dataset.
Phase 6 confirms the M0c_b2 result is stable under the corrected data.
Phase 7 is the substantive interpretation.

---

## 9. Expected impact on the M0c_b2 estimates

The audit measured the median absolute difference between the current
(misaligned-region) GSUR and the (correctly-aligned) alternative
extractions. For the same-region total-sex/total-education concept, the
median difference is `0.003` for couples and `0.003` for singles (§5.2).
This is the right comparison for the rebuild's impact: the rebuild
aligns the region but the sex × education × age dimensions remain.

Expected impact on M0c_b2:
- `β_E_gsur` shift: roughly 5-15% of its current magnitude (`−0.74`),
  potentially in either direction. The new value will reflect the
  correctly-aligned region-by-sex-by-education-by-age unemployment
  rate.
- Other parameters: unchanged within 1% (numerical noise). The GSUR
  variable is one of 47 inputs; correcting its values mainly affects
  the coefficient on that variable.
- LL: marginal change (probably < 5 nats either direction).
- AIC: ranking of model fit unchanged.
- Verdict: the M0c_b2 verdict memo's findings stand.

The substantive paper-ready findings (R5.1-R5.5) from the verdict memo
do not depend on the GSUR rebuild and remain valid.

---

## 10. What this rebuild does NOT change

The rebuild is strictly a data-side fix. The following are not
affected and not modified:

- The RURO estimation engine (`gamspy_estimation_vectorized.py`, etc.)
- The post-estimation reporter (`RURO_post_estimation_styled.py`)
- The estimation specification parser (`estimation_spec_parser.py`)
- The YAML specifications for M0c_b, M0c_b2 (these continue to use
  `gsur` as a single shifter; the multi-UR exposure is for M1-clean)
- The wage draws (`enh_RURO_create_wage_draws_FR.py` or similar)
- The hours draws (similar)
- The EUROMOD computation of disposable income per alternative
- The expression constraint evaluator

The rebuild does change:
- `enh_prepare_FR_gsur.py` (new v2 file)
- `enh_RURO_prep_mnl_basic.py` (modified to expose multi-UR)
- The MNL parquet files (regenerated as v2)

---

## 11. Risks and contingencies

(K1) **NUTS-2 disaggregation may not be available for all sex-education-
age cells in the source workbook.** The Eurostat source uses NUTS-1 by
default; NUTS-2 disaggregation may be missing for some cells. In that
case, the population-weighted aggregation cannot be done at the
NUTS-2 level and falls back to NUTS-1.

Mitigation: implement the small-cell flagging and document any
fallbacks in the v2 lookup. The validation V3 step exposes this.

(K2) **The INSEE crosswalk may have edge cases**. Old EUROMOD regions
sometimes split a modern NUTS region at the NUTS-3 (department) level,
which is rarely available in Eurostat unemployment data.

Mitigation: when a department-level split is required but not
available, allocate the entire NUTS-2 region's GSUR to the old EUROMOD
group that contains the majority of its population. Document the
choice. The validation V5 step catches gross misallocations.

(K3) **The age-specificity may produce sparse cells for some
sex-education-region-age combinations**. Particularly for older ages
(45-64) at low-education levels and small regions, the Eurostat cells
may have < 100 individuals.

Mitigation: use the documented Eurostat small-cell handling: in
sparse cells, aggregate to the next-coarser sex-education-region level
while keeping the age dimension. Flag these as imputed in the lookup.

(K4) **The verdict memo claims the M0c_b2 verdict stands after rebuild.
This may be wrong.** The corrected GSUR could substantively change the
estimated structure if `β_E_gsur` shifts more than expected.

Mitigation: V6 (re-run M0c_b2) catches this. If `β_E_gsur` shifts by
> 50% or other parameters shift by > 5%, the verdict memo must be
updated to v2.

---

## 12. Sequenced after this rebuild

The verdict memo §9 sequenced next steps. Updated for the rebuild:

| step | action | when |
|---|---|---|
| P1 (this memo) | GSUR rebuild specification | now (locked) |
| P1.5 | INSEE crosswalk data file | next (~1 hour) |
| P2 | GSUR rebuild implementation | next (~5 hours of focused work) |
| P3 | M0c_b2 re-estimation with corrected GSUR | after P2 (~5 min compute) |
| P4 | M0c_b2 verdict memo update (if substantive changes) | after P3 |
| P5 | M1-clean implementation prompt and estimation | after P4 |
| P6 | Welfare scaffolding development | parallel with P5 |

The 6-step sequence runs over roughly one week of part-time work.

---

## 13. Suggested filename

Save this memo as: `docs/RURO_GSUR_rebuild_specification_v1.md`
(category: data-design memo / rebuild specification).

This memo is referenced by the implementation prompt that follows
(which will be written separately as a Claude Code prompt). The
implementation prompt operationalizes the design here into a single
copy-paste-ready instruction.
