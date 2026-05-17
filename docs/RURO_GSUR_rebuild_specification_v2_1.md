# RURO GSUR Rebuild — Specification Memo v2.1

Date: 2026-05-16

Scope: cleanup revision of `docs/RURO_GSUR_rebuild_specification_v2.md`.
v2.1 preserves the structure and substance of v2 (the 18-section data-
design specification superseding v1) but applies eight targeted cleanup
edits that v2 introduced and that should be tightened before
implementation work begins. v2.1 supersedes v2 in full and is the
canonical reference document for the GSUR rebuild going forward.

The cleanup edits applied in v2.1 are:

1. Removal of unsupported quantitative claims about population-
   weighting bias.
2. Removal of hard-coded national unemployment rate from the
   validation checks; validation report must cite the benchmark used.
3. Reclassification of age-profile sanity checks as diagnostic flags,
   not pass/fail validation rules.
4. Versioned-path-first workflow: v2 MNL parquets are written to
   versioned `_GSURv2` paths; promotion to canonical paths requires
   explicit user approval after Stage A verdict.
5. Downstream consistency with the versioned-first workflow throughout
   §9, §10, §14, §15.
6. Softening of M0c_b2 verdict robustness claims; the verdict remains
   provisional until Stage A re-estimation.
7. Replacement of "byte-equivalent" Parquet requirements with
   "value-identical under schema-aligned column-wise comparison."
8. Preservation of all core v2 decisions and the open-decision /
   readiness-verdict structure.

This memo is a complete revision, not a changelog. The list above is
provided as a one-time index for ease of reading; subsequent
references are to the relevant section numbers below.

Inputs to this memo:
- `RURO_GSUR_rebuild_specification_v2.md` (the document v2.1
  supersedes)
- `RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` (the audit)
- `DRD_FR_2016_a3_export.txt` (the EUROMOD France 2016 input-variable
  documentation)
- `RURO_occ_M0c_b2_verdict_v1.md` (the current frozen baseline)
- `Data/external/FR_gsur.xlsx` (the GSUR source workbook, content
  inspected via the audit)

---

## 1. Purpose of v2.1

(P1) Apply the eight cleanup edits listed above to v2.

(P2) Preserve v2's structural objective: define a data-side rebuild
that aligns GSUR with EUROMOD `drgn1` coding and exposes age-specific
values for downstream specifications.

(P3) Preserve v2's two-stage re-estimation plan that isolates the
region-crosswalk correction from the age-specificity correction.

(P4) Preserve v2's specification of external data assets that must be
acquired before implementation can begin.

(P5) Preserve v2's lookup and MNL validation checks, with the cleanup
edits in §13 and §14.

(P6) Preserve v2's explicit readiness verdict: implementation remains
blocked until the required assets and open decisions are resolved.

v2.1 keeps v2's core decisions:
- `drgn1` is the EUROMOD 10-category regional coding (1–10), with 1–8
  observed in France 2016;
- the v1 crosswalk is withdrawn; an official crosswalk must be
  acquired before implementation;
- labour-force denominators are preferred for weighted aggregation;
  population denominators are an acceptable approximation, with the
  approximation error documented empirically where possible;
- age bins must be source-aligned to Eurostat Y15-24, Y25-34, …,
  Y55-64 (no v1-style overlapping bins);
- Stage A uses corrected broad-age GSUR; Stage B tests age-specific
  GSUR separately;
- implementation is not authorized until external assets and open
  decisions are resolved.

---

## 2. Why v1 should not be implemented as written

These eight issues, identified in v2 and preserved verbatim in v2.1,
establish why v1 cannot be implemented as written. v2.1 does not
revise these; it inherits them.

(W1) **`drgn1` was described as "old 8-region classification."**
This is wrong. The EUROMOD documentation defines `drgn1` as a
10-category coding (1–10), derived from `drgn2` (the older NUTS-2
vintage code, 1–22 for metropolitan France plus 23–26 for DOM and 27
for extra-regio). The France 2016 sample only observes categories
1–8 because DOM and extra-regio households are excluded upstream.
Implementation must preserve the documented 10-category structure
even if categories 9–10 have zero support in this sample.

(W2) **The v1 crosswalk table is speculative.**
v1 presented a mapping from modern NUTS-1/NUTS-2 codes to old EUROMOD
`drgn1` categories that conflated several distinct issues (a NUTS-1
vs NUTS-2 confusion, a pre-2016 vs post-2016 NUTS vintage confusion,
and an unstated weighting assumption). The EUROMOD `drgn2` is the
pre-2016 NUTS-2 vintage (FR10, FR21, …, FR83, FRZZ); the current
GSUR lookup uses post-2016 NUTS reform codes (FR1, FRB, …, FRM).
These two vintages are not in one-to-one correspondence — the 2016
reform consolidated metropolitan French NUTS-2 regions in ways that
cut across the old EUROMOD groupings (e.g., the modern Grand Est
region FRF spans old Champagne-Ardenne FR21 in `drgn1=2` and old
Lorraine + Alsace FR41, FR42 in `drgn1=4`). A correct crosswalk
requires NUTS-3 (département) disaggregation to recover the
pre-2016 NUTS-2 cells. v2.1 does not publish such a crosswalk.

(W3) **"Population-weighted aggregation" was treated as ideal.**
The correct denominator for aggregating unemployment rates is the
labour force in each contributing cell, not the total population.
v1 did not flag this. v2.1 establishes the denominator principle in
§5.

(W4) **The age bins in v1 (16-25, 26-35, 36-45, 46-65) cross
source-cell boundaries.** The source workbook uses Eurostat
standard age bands: Y15-24, Y25-34, Y35-44, Y45-54, Y55-64. v1's
bin "16-25" spans Y15-24 (ages 16-24) and one year of Y25-34 (age
25). v2.1 uses source-aligned bins per §6.

(W5) **The output schema collapsed broad-age and age-specific GSUR
into a single column called `gsur`.** This made it impossible to
re-estimate M0c_b2 with corrected regions but unchanged age
specification. v2.1 separates these into distinct columns per §8.

(W6) **The re-estimation plan did not isolate the region-crosswalk
correction from the age-specificity correction.** v2.1 defines a
two-stage plan per §9 and §10.

(W7) **Validation V3 (cell-size audit) required denominator data
that the source workbook may not contain.** v2.1 specifies V3
conditionally on whether denominators are available, in §13.

(W8) **v1 referenced files that may not exist at canonical paths.**
v2.1 does not reference files outside the verified input list at
the top of this memo.

---

## 3. Correct definition of `drgn1`

`drgn1` is the EUROMOD France 2016 variable named in the DRD as:

```
DEMOGRAPHIC : Region : NUTS Level 1
```

It is a 10-category integer coding (1–10), with the following
derivation rule from `drgn2` (as documented in the DRD's data
transformation column):

| `drgn1` | derived from `drgn2` values | pre-2016 NUTS-2 codes | label |
|---|---|---|---|
| 1 | 1 | FR10 | Île-de-France |
| 2 | 2, 3, 4, 5, 6, 7 | FR21, FR22, FR23, FR24, FR25, FR26 | Bassin Parisien |
| 3 | 8 | FR30 | Nord-Pas-de-Calais |
| 4 | 9, 10, 11 | FR41, FR42, FR43 | Est |
| 5 | 12, 13, 14 | FR51, FR52, FR53 | Ouest |
| 6 | 15, 16, 17 | FR61, FR62, FR63 | Sud-Ouest |
| 7 | 18, 19 | FR71, FR72 | Rhône-Alpes / Auvergne |
| 8 | 20, 21, 22 | FR81, FR82, FR83 | Méditerranée |
| 9 | 23, 24, 25, 26 | FR91, FR92, FR93, FR94 | DOM |
| 10 | 27 | FRZZ | Extra-regio / unknown |

This mapping is documented in the EUROMOD DRD and is the
authoritative reference for what `drgn1` means in the MNL data.

In the France 2016 MNL data, observed support is `drgn1 ∈ {1, ..., 8}`.
Categories 9 (DOM) and 10 (extra-regio) are absent because DOM and
extra-regio households are dropped upstream in the EUROMOD pipeline.
v2.1 implementation must preserve the documented 10-category
structure in lookup files even if categories 9–10 have zero support,
because the lookup will be reusable for other EUROMOD samples.

The mapping from `drgn2` to `drgn1` uses pre-2016 NUTS-2 codes (FR10,
FR21, …, FR83, plus FR91–94, FRZZ). The vintage mismatch between
EUROMOD `drgn2` (pre-2016 NUTS-2) and modern Eurostat regional data
(post-2016 NUTS) is the central practical obstacle the rebuild must
address.

---

## 4. Region-crosswalk requirement

v2.1 does not include an implementation-authoritative crosswalk. The
v1 crosswalk table is withdrawn.

Implementation of the rebuild requires acquisition of a crosswalk
meeting the following criteria:

(C1) **Source authority**: the crosswalk must be derived from an
official INSEE or Eurostat document that explicitly maps modern
NUTS-2 or NUTS-3 regions back to pre-2016 NUTS-2 regions. INSEE
publishes the territorial reform documentation; Eurostat publishes
NUTS history tables. Use one of these as the authoritative source.

(C2) **Granularity**: the crosswalk must be at NUTS-3 level (the
French *départements*) where modern NUTS-2 regions span multiple
pre-2016 NUTS-2 regions, because Eurostat regional unemployment
data are typically published at NUTS-2 but départements can be
aggregated to either old or new NUTS-2 unambiguously.

(C3) **Verifiability**: every modern code (FR1, FRB, …, FRM) must
appear in the crosswalk, and every old EUROMOD-relevant code (FR10,
FR21, …, FR83) must be reconstructable from the crosswalk by
aggregation. The crosswalk should be machine-readable and have
units, weights, or aggregation rules explicit.

(C4) **Validation against known facts**: the only unambiguous case is
modern FR1 = old FR10 = `drgn1 = 1` (Île-de-France). All other
cells require the crosswalk to specify the aggregation rule. If
the modern NUTS code spans multiple old EUROMOD groupings, the
crosswalk must specify the rule for splitting it.

(C5) **Provisional crosswalk handling**: if a partial or provisional
crosswalk is constructed during implementation, it must be
labelled `provisional_crosswalk_v0.csv` and not used in the v2.1
GSUR lookup until verified.

(C6) **What v2.1 does NOT do**: v2.1 does not state which INSEE or
Eurostat document is the authoritative source. v2.1 does not
estimate the magnitudes of cross-vintage discrepancies. v2.1 does
not propose a fallback heuristic if the official crosswalk is
unavailable. These are open items in §17.

---

## 5. Weighting and denominator principle

For each (region × sex × education × age) cell that requires
aggregation across multiple modern NUTS components into a single
EUROMOD `drgn1` cell, the aggregation requires weights. v2.1
establishes the following principle:

(D1) **Preferred denominator: matching labour force.** The numerator
of an unemployment rate is the unemployed count in the cell; the
denominator is the labour force in the same cell. When aggregating
multiple cells, the correct method is sum-of-numerators divided by
sum-of-denominators, equivalent to a labour-force-weighted mean of
the rates. This requires labour force data by (modern NUTS × sex ×
education × age) for 2016, in the same disaggregation as the
unemployment rate.

(D2) **Acceptable approximation: matching population.** If Eurostat
or INSEE publishes population (not labour force) at the required
disaggregation, total-population weighting is an acceptable
approximation. Population weighting is an approximation to
labour-force weighting and the approximation error depends on
how labour-force participation rates vary across the contributing
cells; the size of this error in the France 2016 case is not known
*a priori* and must be documented empirically where possible. The
recommended documentation procedure is: identify any subset of
cells where both labour-force and population denominators are
available, compute the aggregated rate under both weightings, and
report the differences in the validation report. Any cell using
population weighting in the final lookup is flagged in the output
per §5(D4).

(D3) **Unweighted fallback: not allowed by default.** If neither
labour-force nor population denominators are available, the
aggregation must not be done by simple unweighted mean of rates.
The cell must instead be:
- (a) flagged as unaggregatable and the lookup must use the broad-
  age national value as a fallback;
- (b) or, with explicit reviewer sign-off, aggregated with a uniform
  weight per modern NUTS component, and the output flagged as
  "approximate-uniform-weighted" so downstream analyses can
  exclude or robustness-check these cells.

(D4) **Per-cell weighting record**: the v2.1 lookup must record, per
output cell, which denominator was used (labour-force /
population / approximate-uniform). A column `weighting_source`
takes one of these three values per row.

(D5) **No silent fallback**: implementation must fail if the
denominator data are missing for a cell without explicit fallback
instruction. v1's silent collapse to `Y20-64` for many cells was
the kind of opacity v2.1 must avoid.

---

## 6. Source-aligned age bins

The source workbook (per the audit §5.4) provides unemployment rates
in the following Eurostat-standard age bands:

| Eurostat label | covers ages |
|---|---|
| `Y15-24` | 15-24 |
| `Y25-34` | 25-34 |
| `Y35-44` | 35-44 |
| `Y45-54` | 45-54 |
| `Y55-64` | 55-64 |
| `Y20-64` | 20-64 (broad working age) |

v2.1 mandates source-aligned binning of MNL ages to source cells.
The mapping from MNL age (`dag`) to source cell is:

| MNL `dag` | source cell |
|---|---|
| 15 | Y15-24 |
| 16, 17, …, 24 | Y15-24 |
| 25, 26, …, 34 | Y25-34 |
| 35, 36, …, 44 | Y35-44 |
| 45, 46, …, 54 | Y45-54 |
| 55, 56, …, 64 | Y55-64 |
| 65 | see §7 |

v1's bins (16-25, 26-35, 36-45, 46-65) are explicitly rejected
because each crosses a source-cell boundary.

The MNL sample's `dag` support starts at 16, so the 15-year-old slot
in Y15-24 is never populated from the MNL data. The lookup file is
still keyed on the full Y15-24 source cell (because the lookup is
reusable for other samples that might include 15-year-olds).

---

## 7. Handling of age 65

The source workbook covers ages 15-64. The MNL sample includes
households with `dag` up to 65. For age 65, there is no source-
aligned cell.

Three options for handling age 65:

(A65-1) **Exclude age-65 households from the estimation sample.**
Cleanest from a methodological standpoint (every household has a
defined source cell), but loses observations. The sample-size cost
depends on how many age-65 households are in the current MNL data.

(A65-2) **Map age 65 to Y55-64 with an explicit flag.** Uses the
nearest available source cell (ages 55-64) for the 65-year-old.
This is defensible if labour market behaviour at age 65 is similar
to age 55-64.

(A65-3) **Map age 65 to Y20-64 broad fallback with explicit flag.**
Uses the broad working-age rate. Conservative; minimises
informativeness gain from age-specificity at age 65.

The decision among (A65-1), (A65-2), (A65-3) is deferred to §17 open
decision O3, contingent on a count of how many age-65 households are
in the current MNL parquets. The decision must be made before
implementation. v2.1 does not pre-commit.

If (A65-1) is chosen, the M0c_b2 sample changes and the GSUR rebuild
becomes coupled to a sample change. In that case, the M0c_b2
verdict's findings must be re-checked after the rebuild.

---

## 8. Corrected output schema

v2.1 separates the broad-age GSUR (the variable used in M0c_b2) from
the age-specific GSUR (the new feature). The MNL parquets, after
the v2.1 rebuild, carry the following columns.

### 8.1 Singles parquet — GSUR columns

| column | description | use case |
|---|---|---|
| `gsur_legacy_misaligned` | the current v1 GSUR (pre-rebuild), preserved verbatim | forensic comparison and reproducibility of v1 estimates |
| `gsur` | corrected broad-age GSUR using Y20-64 cells and corrected `drgn1` region coding | M0c_b2 Stage A re-estimation (replaces `gsur_legacy_misaligned` in YAML) |
| `gsur_age` | age-specific GSUR for this household, using the source-aligned age cell matching `dag` | Stage B age-specific specifications |
| `gsur_y15_24` | unemployment rate for ages 15-24 (cell value, not personalised) | sensitivity analyses |
| `gsur_y25_34` | unemployment rate for ages 25-34 | sensitivity analyses |
| `gsur_y35_44` | unemployment rate for ages 35-44 | sensitivity analyses |
| `gsur_y45_54` | unemployment rate for ages 45-54 | sensitivity analyses |
| `gsur_y55_64` | unemployment rate for ages 55-64 | sensitivity analyses |
| `gsur_age_band_used` | string label of source cell used for this household's `gsur_age` | provenance |
| `gsur_weighting_source` | one of `labour_force`, `population`, `approximate_uniform`, per §5(D4) | provenance |

All GSUR variables are in proportion units (0.04 = 4%), preserving v1's
convention.

### 8.2 Couples parquet — GSUR columns

All of §8.1's columns, each appearing with `_male` and `_female`
suffixes. Partner-specific sex × education × age cells are looked up
independently.

### 8.3 Naming rationale

The naming convention is deliberate:
- `gsur` is the corrected broad-age variable, same column name as the
  v1 column, so existing YAML specs (M0c_b2) continue to reference
  `gsur` without modification. Stage A re-estimation therefore
  requires zero YAML changes.
- `gsur_age` is the age-specific personalised variable, new column
  name, requiring a Stage B YAML change to use it.
- `gsur_y*` are the separate source-band exposed variables, available
  for analyses that want to interact UR with age dummies or use
  multiple bands jointly.
- `gsur_legacy_misaligned` is the forensic record of what the current
  MNL parquets contain.

---

## 9. Stage A: corrected broad-age GSUR

Stage A is the minimal rebuild that isolates the region-crosswalk
correction from any other change.

### 9.1 What Stage A changes
- The `gsur` column in the **versioned** v2.1 MNL parquets is the
  v2.1 region-corrected Y20-64 broad-age value.
- `gsur_legacy_misaligned` is added for forensic comparison.
- All other MNL columns are value-identical to the current parquets
  under schema-aligned comparison (see §14).
- The M0c_b2 YAML is unchanged (continues to reference `gsur`).
- Stage A operates against the **versioned** GSURv2 parquets at the
  paths in §12(F6), not against canonical parquets. Promotion to
  canonical paths is a separate step requiring explicit user approval
  after the Stage A verdict.

### 9.2 Stage A re-estimation
Re-run M0c_b2 against the versioned GSURv2 MNL parquets. Multi-start
with three starts to match the M0c_b2 multistart standard:
1. Warm-start from the current M0c_b2 (v1 GSUR) parameter vector;
2. Spec defaults;
3. Dispersed interior.

The estimation command uses the GSURv2-versioned `--mnl-base` path
per §15.

### 9.3 Stage A decision rule
Compare the new estimates to the current M0c_b2 estimates. Three
outcomes:

(SA-STANDS) **Verdict stands**: `β_E_gsur` shifts by < 50% of its
M0c_b2 magnitude; all other parameters shift by < 5%; fit moments
shift by < 0.5 percentage points (participation) and < 0.5 hours
(mean hours); log-likelihood changes by < 10 nats. The corrected
GSUR refines `β_E_gsur` but does not change the structural picture.
M0c_b2_GSURv2 becomes the new working baseline and promotion to
canonical paths is recommended.

(SA-REVISION) **Verdict needs minor revision**: `β_E_gsur` shifts by
> 50% but other parameters are stable, or one fit moment shifts
substantially while the overall pattern holds. M0c_b2_GSURv2
becomes the new baseline; the verdict memo is updated to v2
documenting the changes. Promotion to canonical paths is
recommended after the verdict update.

(SA-OVERTURNED) **Verdict overturned**: any preference parameter
(`β_ll`, `θ_l_*`, `β_c_*`) shifts by > 10%, or fit moments regress
materially, or log-likelihood changes by > 50 nats. Stop. Write a
supervisor memo. Do not proceed to Stage B. Do not promote
GSURv2 parquets to canonical. The M0c_b2 verdict memo must be
re-examined.

### 9.4 What Stage A does NOT do
Stage A does not introduce age-specificity. Stage A does not
overwrite canonical MNL paths. Stage A does not modify any
estimation, engine, or post-estimation code.

---

## 10. Stage B: age-specific GSUR

Stage B is sequenced after a Stage A verdict that is either
SA-STANDS or SA-REVISION. If Stage A is SA-OVERTURNED, Stage B does
not run.

### 10.1 Stage B sub-specifications
Two candidate specifications, each estimated separately:

(SB-1) **Single age-personalised GSUR**: replace `gsur` with
`gsur_age` in the YAML. Each household's GSUR is the source value
for its own age band. One empirical content addition (age-
specificity) without changing model dimensionality.

(SB-2) **Multiple age-band GSURs jointly**: use four of the five
`gsur_y*` variables in the YAML (the fifth is the reference)
interacted with working. Five parameters replace one;
identification depends on within-region age variation. Likely
poorly identified at the current sample size; included as a
sensitivity exercise.

### 10.2 Stage B identification check
For SB-1 and SB-2, check whether the resulting Hessian is positive
semi-definite, whether all parameters are interior, and whether
multi-start convergence is stable. If SB-2 is non-identified, drop
to SB-1 as the primary age-specific spec.

### 10.3 Stage B decision rule
Compare SB-1 to the Stage A baseline (M0c_b2_GSURv2):

(SB-USEFUL) Age-specific GSUR adds substantively (AIC improves by
> 5; fit moments improve; `β_E_gsur_age` significant): SB-1 becomes
the preferred specification for M1-clean and welfare work.

(SB-NEUTRAL) Age-specific GSUR adds nothing (AIC change small,
`β_E_gsur_age` not significant): SB-1 documented as estimated but
M1-clean uses broad-age `gsur` from Stage A.

(SB-FAILS) Identification fails: documented; M1-clean uses broad-
age `gsur` from Stage A.

### 10.4 What Stage B does NOT do
Stage B does not change the M1-clean specification (region dummies,
removing `β_E_educH` from `q`). Those are M1-clean decisions
sequenced after Stage B. Stage B answers only: which GSUR variable
should M1-clean use?

Stage B operates against the same versioned GSURv2 parquets as Stage
A. If canonical promotion has occurred between Stages A and B, Stage
B may equivalently use the canonical paths.

---

## 11. Required external data assets

Implementation requires acquiring or constructing the following
external assets. None are provided in v2.1; each is an open
acquisition task.

(E1) **Modern-to-old NUTS crosswalk**.
- Source: INSEE territorial reform documentation or Eurostat NUTS
  history tables.
- Format: machine-readable CSV with columns at minimum
  `modern_nuts_code`, `old_euromod_drgn2`, `drgn1`, and a weight or
  aggregation-rule column for cases where modern NUTS spans multiple
  old groupings.
- Granularity: NUTS-3 (département) where modern NUTS-2 spans old
  EUROMOD boundaries.

(E2) **Labour-force denominators by cell**.
- Source: INSEE labour-force survey (Enquête Emploi) regional
  aggregates, or Eurostat regional labour market statistics
  (lfst_r_lfu_2010 series or successor).
- Disaggregation: at least (modern NUTS-2 × sex × education × age
  band) for 2016. Ideally also by NUTS-3 if cross-vintage
  aggregation is needed.
- Acceptable substitute: population data at the same disaggregation
  if labour force is unavailable (with the approximation flagged per
  §5(D2) and documented empirically per the procedure in §5(D2)).

(E3) **Eurostat unemployment rates by region × sex × education × age
band**.
- This is the existing source workbook (`Data/external/FR_gsur.xlsx`)
  and is already in hand. No new acquisition needed.

(E4) **National benchmark for validation**.
- The validation check in §13(L5) requires a citable national French
  unemployment rate for 2016. Acceptable sources include INSEE main
  publications (e.g., INSEE Première or the annual labour-market
  reports) or Eurostat (one_a series). The specific source and
  value used must be cited in the validation report; v2.1 does not
  pre-commit to a specific number.

(E5) **DOM and extra-regio decision**.
- Confirm whether the EUROMOD France 2016 sample's exclusion of DOM
  and extra-regio households is permanent or potentially reversible.
  If the JMP might include DOM in later analyses, the v2.1 lookup
  must support `drgn1 = 9, 10` cells. Otherwise these remain
  zero-support categories in the lookup.

If E1 and E2 cannot be acquired, the rebuild cannot proceed in its
intended form.

---

## 12. Required implementation files

These are files the implementation will create. v2.1 does not
authorize their creation in this memo; v2.1 specifies them as
deliverables once the acquisition tasks in §11 are complete and the
open decisions in §17 are resolved.

(F1) `Data/external/fr_modern_nuts_to_euromod_drgn1_crosswalk.csv`
— the verified crosswalk from §4.

(F2) `Data/external/fr_labour_force_weights_by_cell.csv` (or
`fr_population_weights_by_cell.csv` if labour force unavailable) —
the denominators from §11(E2).

(F3) `scripts/enhanced/enh_prepare_FR_gsur_v2.py` — the new
preparation script.

(F4) `Data/external/FR_gsur_ruro_v2.parquet` — the rebuilt lookup
file.

(F5) Modifications to `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
to handle the v2.1 lookup and produce versioned GSURv2 MNL parquets
with the schema in §8.

(F6) **Versioned GSURv2 MNL parquets**, written to versioned paths
(NOT canonical paths):
```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/
  fr_2016_RURO_mnl_GSURv2__singles.parquet
  fr_2016_RURO_mnl_GSURv2__couples.parquet
```
These files are the rebuild's primary output. They are used for
Stage A re-estimation per §9 and Stage B re-estimation per §10.

(F6-promote) **Canonical promotion** — a separate step, not part of
the initial implementation. After the Stage A verdict has produced
either SA-STANDS or SA-REVISION, and after explicit user approval,
the canonical paths are updated:
```
old canonical (archived):
  Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/archive/
    fr_2016_RURO_mnl__singles_GSURv1.parquet
    fr_2016_RURO_mnl__couples_GSURv1.parquet

new canonical:
  Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/
    fr_2016_RURO_mnl__singles.parquet   ← was previously v1
    fr_2016_RURO_mnl__couples.parquet   ← was previously v1
```
Promotion involves: (a) archiving the v1 canonical files with a
`_GSURv1` suffix; (b) copying or renaming the GSURv2 versioned files
to the canonical paths. Promotion is **not** authorized by v2.1; it
requires the Stage A verdict and a separate user-approval step.

(F7) `docs/RURO_GSUR_v2_implementation_report_v1.md` — the
implementation report.

(F8) `Results/RURO_GSUR_v2_lookup_validation_report_v1.md` — the
lookup-level validation report (§13).

(F9) `Results/RURO_GSUR_v2_MNL_rebuild_report_v1.md` — the MNL-
rebuild validation report (§14). This report covers the GSURv2
versioned parquets, not the canonical paths.

(F10) `Results/RURO_GSUR_v2_canonical_promotion_report_v1.md` — the
canonical promotion report. Produced only after Stage A verdict and
explicit user approval. Records what was archived where, what was
promoted, and the date of promotion.

---

## 13. Lookup validation checks

These checks are run on the v2.1 lookup file (F4) before it is merged
into the MNL parquets. Checks are partitioned into pass/fail
validation rules and diagnostic flags. Diagnostic flags are
informational only and do not block downstream steps.

### 13.1 Pass/fail validation rules

(L1) **Unique keys**. The lookup is keyed on `(year, drgn1, dgn,
educ3, age_band)`. Each combination appears exactly once. No
duplicates. No missing combinations for `drgn1 ∈ {1, ..., 8}`.

(L2) **Proportion units**. All GSUR values are in [0.00, 1.00]. The
unit conversion from the source workbook (percent) must be applied
exactly once.

(L3) **`drgn1` support**. Categories 1–8 are present in the lookup.
Categories 9 and 10 are present as schema rows but contain only
NaN or zero-support markers in the France 2016 sample.

(L4) **Cross-vintage reconstruction sanity**. Aggregating from modern
NUTS to old EUROMOD `drgn1` produces values that are internally
consistent. Aggregating from modern NUTS to `drgn1 = 1`
(Île-de-France) recovers exactly the modern FR1 source value (the
one unambiguous case). For other `drgn1` categories, the aggregated
value must lie within the range of the contributing modern NUTS
values (min-max bound check, not equality).

(L5) **National-level benchmark consistency**. Aggregating all
`drgn1` categories using the chosen weighting produces a national
rate consistent with an INSEE- or Eurostat-published 2016 French
unemployment rate. The validation report must cite the specific
INSEE or Eurostat publication used as the benchmark and state the
tolerance applied (recommended: ±1 percentage point). v2.1 does
not hard-code the benchmark value; the implementation team
selects and cites it in the validation report.

(L7) **Weighting-source documentation**. Per-cell `weighting_source`
column records the denominator type used. Aggregate counts of
(labour_force / population / approximate_uniform) cells are
reported in the validation report.

(L8) **Per-cell flagging of approximations**. Cells where the
aggregation rule is non-trivial (modern NUTS spans multiple old
EUROMOD groupings) are flagged. The validation report lists these
cells explicitly.

(L9) **Cell-size denominator check** — runs only if denominator data
are available per §5. Otherwise skipped, with a note in the
validation report that exact cell-size validation cannot be
performed without acquiring denominator data.

### 13.2 Diagnostic flags (informational, not pass/fail)

(L6-diag) **Age-monotonicity diagnostic**. Unemployment rates by
age band typically follow `Y15-24 > Y25-34 > Y35-44 > Y45-54` with
`Y55-64` potentially rising above `Y45-54` due to early-retirement
dynamics. The aggregated values typically respect this pattern.
Cells reversing the pattern (e.g., `Y15-24 << Y45-54`) are flagged
in the validation report for review. This is a diagnostic flag,
not a pass/fail rule — reversed patterns are not in themselves a
failure; they are an alert to examine the cell's source data and
weighting.

(L10-diag) **Comparison to v1 (forensic)**. For each `(drgn1, dgn,
educ3)` cell in the existing v1 lookup, compute the v2.1 value
under the corrected coding and report the difference. Île-de-France
(`drgn1 = 1`) values should match within the tolerance set in
§17(O8) (the one unambiguous region). Other `drgn1` categories
show the correction magnitudes. This comparison is diagnostic, not
pass/fail; the v1 lookup is misaligned by design and large
differences are expected.

(L11-diag) **Population vs labour-force weighting comparison**. If
both labour-force and population denominators are available for any
subset of cells, the validation report includes a comparison of
aggregated rates under both weightings on this subset. This
diagnostic informs the empirical magnitude of the population-
weighting approximation per §5(D2). Not pass/fail.

---

## 14. MNL rebuild validation checks

These checks are run on the versioned GSURv2 MNL parquets (F6)
before any consideration of canonical promotion. Checks are
partitioned into pass/fail validation rules and diagnostic flags.

### 14.1 Pass/fail validation rules

(M1) **Value-identical non-GSUR columns under schema-aligned
comparison**. Every non-GSUR column in the GSURv2 parquets has
values identical to the v1 canonical parquets at the same row
position when columns are compared row-wise. Verify via column-wise
pandas comparison (`assert_series_equal` with appropriate `check_
dtype` and `check_index_type` options, or equivalent), not via
file-byte hashing. Parquet regeneration may legitimately produce
non-identical file bytes due to compression, row-group sizing, or
metadata differences; value-identity at the cell level is the
correct semantic equivalence.

(M2) **GSUR column schema**. All columns in §8.1 (singles) and §8.2
(couples) are present. Names match exactly.

(M3) **No missing values in `gsur`**. The corrected broad-age `gsur`
has no NaN for any household in the sample. (Age-specific
variables may have NaN for ages outside source-cell coverage,
handled per §7.)

(M4) **Île-de-France parity**. For all households with
`drgn1 = 1`, `gsur` is within the tolerance set in §17(O8) of
`gsur_legacy_misaligned` (the one unambiguous case from §13 L4).

(M5) **Age-band assignment**. `gsur_age_band_used` matches the
appropriate source cell for each household's `dag`, per §6.

(M6) **Partner-specific consistency in couples**. `gsur_male` and
`gsur_female` are independently looked up; only ~15% of couples
have identical values (per the audit §12.3). The fraction is
preserved in the GSURv2 parquets.

(M7) **Row count preservation**. Row counts in GSURv2 parquets match
v1 exactly (no row-multiplication from the merge, no row loss).

(M8) **Forensic record preservation**. `gsur_legacy_misaligned` is
present and equals the v1 `gsur` values under schema-aligned
column-wise comparison.

(M9) **Cross-stage compatibility**. The GSURv2 versioned parquets
are readable by the existing engine and post-estimator without code
changes. Specifically: `scripts/enhanced/gamspy_estimation_vector
ized.py` reads the `gsur` column by name from the GSURv2 versioned
path, finds it, and proceeds.

(M10) **Versioned path location**. The GSURv2 parquets are written
to the versioned paths in §12(F6), not to canonical paths. The
canonical paths still point to v1 content until promotion (F6-
promote). This check explicitly confirms that the rebuild did not
silently overwrite canonical files.

### 14.2 Diagnostic flags

(M11-diag) **GSUR value distribution comparison**. The validation
report includes summary statistics (mean, median, quantiles) of
`gsur` and `gsur_legacy_misaligned` by `drgn1`, by `dgn`, and by
`educ3`. Large differences are expected per the W2 issue; the
diagnostic informs interpretation of any subsequent shifts in
`β_E_gsur` in Stage A.

(M12-diag) **Age-personalised value distribution**. The validation
report includes summary statistics of `gsur_age` overall and by
age-band-used, alongside the broad-age `gsur` for comparison.
Informational; informs Stage B identification expectations.

---

## 15. Re-estimation plan

Sequenced after F1–F9 are produced and validated.

(R1) **Stage A re-estimation against versioned GSURv2 parquets.**
Estimate M0c_b2 with the GSURv2 versioned MNL parquets at F6
paths. The estimation command's `--mnl-base` flag points to:
```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2
```
which resolves to `fr_2016_RURO_mnl_GSURv2__singles.parquet` and
`fr_2016_RURO_mnl_GSURv2__couples.parquet`. Multi-start with three
runs per §9.2. Decision rule per §9.3.

Output:
- M0c_b2_GSURv2 estimation report;
- new verdict memo if SA-STANDS or SA-REVISION;
- supervisor memo if SA-OVERTURNED.

(R2) **Canonical promotion (conditional)**. If R1 is SA-STANDS or
SA-REVISION, and after explicit user approval, promote GSURv2
versioned parquets to canonical paths per F6-promote. v1 canonical
parquets are archived. Produces F10 (canonical promotion report).
If R1 is SA-OVERTURNED, no promotion. Canonical paths remain at v1
content.

(R3) **Stage B re-estimation (conditional)**. Only if R1 is
SA-STANDS or SA-REVISION. Estimate SB-1 (single age-personalised
GSUR) against the same GSURv2 parquets used in Stage A (versioned or
canonical depending on promotion status). Decision rule per §10.3.

(R4) **Stage B sensitivity (conditional)**. Only if R3 is SB-USEFUL.
Estimate SB-2 as a sensitivity check.

(R5) **Frozen baseline declaration**. After R1, R2 (if promoted),
R3, and optionally R4 complete, declare which spec is the working
baseline for M1-clean. Default decision tree:
- If R3 is SB-USEFUL: baseline is SB-1 (age-personalised GSUR);
- Otherwise: baseline is the Stage A result (broad-age GSUR).

(R6) **M1-clean implementation prompt**. After R5, write the
M1-clean implementation prompt using the chosen baseline's MNL
parquets (canonical or versioned depending on R2 status) and YAML.

---

## 16. What must not be changed

The rebuild is strictly a data-side correction. The following remain
unmodified:

(N1) Wage draws: `enh_RURO_create_wage_draws_FR.py` and its outputs.

(N2) Hours draws: the hours sampler script and its outputs.

(N3) Occupation draws.

(N4) EUROMOD computation of disposable income per alternative.

(N5) The proposal-density correction (`−log_prior` subtraction).

(N6) The M0c_b2 YAML specification: `estimation_spec_ruro_occ_M0c_b2.
yaml`. Stage A uses this YAML unchanged.

(N7) The estimation engine: `gamspy_estimation_vectorized.py`,
`estimation_engine.py`.

(N8) The estimation specification parser: `estimation_spec_parser.py`.

(N9) The post-estimation reporter: `RURO_post_estimation_styled.py`.

(N10) The expression-constraint evaluator: `expression_constraints.py`.

(N11) All non-GSUR MNL columns (verified per §14 M1).

(N12) The frozen identification structure of M0c_b2:
- `θ_c` fixed at 0 (couples log-utility);
- `β_l0_m` lower bound at 1e-6;
- `β_ll` bound [0, 10];
- 47-parameter parameter vector.

(N13) **The current M0c_b2 verdict remains provisional until Stage A
re-estimation is complete.** The verdict memo's findings R5.1–R5.5
(the substantive paper-ready results) are not frozen for paper
citation purposes until Stage A confirms whether the corrected GSUR
materially affects these magnitudes. The expectation in the M0c_b2
verdict memo §6 is that other parameters shift by less than 5%, but
this expectation must be verified empirically by Stage A
re-estimation. If Stage A is SA-OVERTURNED, the M0c_b2 verdict
memo must be re-examined and may be revised.

(N14) Canonical MNL paths until explicit promotion approval per
F6-promote. The implementation must write only to versioned paths.

---

## 17. Open decisions before coding

Implementation is blocked on the following decisions. Each must be
resolved (by user decision, by supervisor input, or by data
inspection) before any code is written.

(O1) **Crosswalk source**. Which specific INSEE or Eurostat
publication provides the authoritative crosswalk from modern NUTS
codes to pre-2016 NUTS-2 codes (which then map to `drgn1` via the
DRD-documented derivation)? The implementation cannot proceed
without a verified source. Possible candidates: INSEE territorial
reform technical documentation (the 2016 régionalisation
publication), Eurostat Regulation (EU) 2016/2066 amending NUTS and
related correlation tables, or a NUTS-3 lookup published with
Eurostat regional accounts.

(O2) **Denominator data availability**. Are labour-force
denominators by (modern NUTS-2 or NUTS-3 × sex × education × age
band) available for 2016 in Eurostat or INSEE? If yes, use them
per §5(D1). If not, are population denominators available? If
neither, the rebuild's aggregation must be flagged as approximate
per §5(D3).

(O3) **Age-65 handling**. Decision among (A65-1), (A65-2), (A65-3)
in §7. Requires a count of age-65 households in the current MNL
parquets to inform the trade-off. A simple `df[df['dag'] ==
65].shape[0]` query on the singles and couples parquets resolves
this.

(O4) **Education concept alignment**. The source workbook reports
unemployment rates by an `educ` variable that uses Eurostat's
educational attainment groupings (commonly ISCED 0-2, 3-4, 5-8).
The MNL parquets use `educ3 ∈ {0, 1, 2}`. Confirm that the mapping
from Eurostat `educ` to MNL `educ3` is correct.

(O5) **DOM inclusion**. Will the JMP include DOM households in
future analyses? If yes, the v2.1 lookup must populate `drgn1 = 9`
cells, requiring DOM-specific Eurostat data. If no, `drgn1 = 9`
cells in the lookup remain NaN.

(O6) **Stage B necessity**. If Stage A produces a stable SA-STANDS
verdict, is Stage B (age-specific) strictly necessary for the JMP?
The decision affects timeline. Stage B adds robustness exposure but
the JMP's main result might be defensible with broad-age GSUR
only. Decision can be made after Stage A verdict.

(O7) **Reviewer sign-off on crosswalk**. Once the crosswalk in O1 is
constructed, is supervisor or RA sign-off required before merging
into the MNL parquets? Recommended yes — the crosswalk is a
load-bearing data asset and silent errors propagate to all
downstream estimates.

(O8) **Tolerance for Île-de-France parity (M4 in §14)** and for v1
forensic comparison (L10 in §13). What absolute or relative
tolerance counts as "matches"? Recommended: absolute tolerance of
0.001 (i.e., values within 0.1 percentage points) for the Île-de-
France parity check. Decision can be made by user.

(O9) **National benchmark for L5**. Which specific INSEE or Eurostat
publication provides the 2016 French national unemployment rate to
be used in the L5 validation check? See §11(E4). The implementation
team selects this source and cites it in the validation report.

(O10) **Canonical promotion authorization**. The criteria for
promoting GSURv2 versioned parquets to canonical paths: are
SA-STANDS and SA-REVISION both sufficient for promotion, or is only
SA-STANDS sufficient? Recommended: both, since SA-REVISION still
produces a defensible baseline (the verdict memo just updates to
v2 documenting the changes). Decision can be made by user.

---

## 18. Final implementation readiness verdict

**Implementation is NOT authorized by v2.1.**

v2.1 is a data-design specification. It defines what the rebuild must
look like and what external assets it depends on. It does not
provide the assets, and it does not authorize the implementation.

Specifically:

(V1) The crosswalk asset (E1, F1) does not yet exist in
implementation-authoritative form. v2.1 explicitly withdraws the
crosswalk table that v1 published.

(V2) The denominator data (E2, F2) is not yet confirmed available.

(V3) The national benchmark for validation (E4) is not yet selected.

(V4) Open decisions O1–O10 in §17 are unresolved.

The next phase is:

(P1) **Acquisition phase**. Resolve open decisions, particularly O1
(crosswalk source), O2 (denominator availability), and O9 (national
benchmark). Build the verified crosswalk file. Build the
denominator file or document the substitute.

(P2) **v3 specification** (if needed). If the acquisition phase
reveals data limitations that v2.1 did not anticipate, produce a v3
specification documenting the limitation and the chosen workaround.

(P3) **Implementation prompt**. After acquisition and any v3
revision, write a Claude Code prompt that takes the crosswalk and
denominator files as explicit inputs, applies them per v2.1 (or
v3), and produces the deliverables F3–F9. The prompt must specify
that F6 outputs are written to versioned GSURv2 paths only.

(P4) **Verification**. Run the lookup validation (§13) and MNL
rebuild validation (§14) against the versioned outputs.

(P5) **Stage A re-estimation**. Per §15(R1), against versioned
parquets.

(P6) **Conditional canonical promotion**. Per §15(R2), only after
Stage A verdict and explicit user approval.

(P7) **Stage B re-estimation (conditional)**. Per §15(R3).

The acquisition phase (P1) is the immediate next task. v2.1
explicitly prefers acquisition delay over speculative implementation.

The current M0c_b2 baseline remains the working baseline until Stage
A re-estimation is complete. The M0c_b2 verdict memo's findings
remain provisional pending Stage A re-estimation.

---

## 19. Suggested filename

Save this memo as: `docs/RURO_GSUR_rebuild_specification_v2_1.md`
(category: data-design memo / rebuild specification, supersedes v2,
which supersedes v1).

The v1 and v2 memos should be retained as historical record (move to
`archive/` or leave with a clear note that v2.1 supersedes them).
