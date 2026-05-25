# JMP Multi-Year Stage M1 P3a — Construction Verdict v1

Date: 2026-05-20

Construction under review: Stage M1 P3a provisional pooled
construction (FR 2015 + 2016 + 2017, singles and couples),
provisioning label `provisional_v1_fallback_opportunity_year_aligned`

Output files under review:
- `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet`
  (139 columns, 1,244,500 rows, 168.8 MB)
- `Data/processed/fr/pooled/fr_p3a_harmonised.parquet`
  (143 columns, 1,244,500 rows, 176.9 MB)
- `Data/processed/fr/pooled/fr_p3a_stacked_raw__stage_m1_meta.json`
- `Data/processed/fr/pooled/fr_p3a_harmonised__stage_m1_meta.json`

Primary evidence:
- `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md`
- `Results/JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md`

Governing documents:
- `docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md`
  (the pre-execution authorization and readiness baseline)
- `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule and the v1-fallback provisional regime)
- `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` (welfare
  design, complete; not an execution authorization)
- `docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` (welfare
  scaffolding design, complete; not an execution authorization)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  JMP baseline)
- `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the controlling multi-year strategy, referenced for sequencing)

Scope of verdict: construction-quality assessment of the Stage M1
P3a provisional pooled dataset. The verdict adjudicates whether
the construction is mechanically correct, whether the repair of
the prior couples-only defect succeeded, what downstream uses the
provisional file is fit for, and which empirical gate must be
cleared before any output of this file can enter the JMP. The
verdict does not authorise pooled estimation, welfare
implementation, welfare computation, canonical MNL promotion, or
any Stage M1 re-run; those decisions are separately gated.

---

## 1. Verdict

**PASS WITH PROVISIONAL LIMITATIONS.**

The Stage M1 P3a pooled construction is mechanically correct and
internally validated. All nine validation checks (V1 through V9)
pass; the prior couples-only defect is fully repaired; both
household types are present across all three survey years; the
stacked-identifier engineering is collision-free; the raw
identifiers are preserved without loss; the cross-year identity
validation confirms the expected EU-SILC rotational-panel
structure; the CPI/HICP harmonisation deflates monetary variables
exactly; and the cluster key is correctly annotated at the raw-
household level. On the mechanical-construction criteria, the
build is a clean PASS.

The construction is nonetheless classified PASS WITH PROVISIONAL
LIMITATIONS — not PASS — for one decisive reason: the
opportunity-side GSUR variable is sourced from the v1 fallback
lookup (`FR_gsur_ruro.parquet`) rather than from the GSURv2
opportunity-year-aligned construction. The GSUR year-alignment
decision §6 establishes that final pooled estimation requires
GSURv2 rebuilt for each opportunity year (2014, 2015, 2016)
before any year's parquet is promoted to final status, and that
until GSURv2 opportunity-year-aligned parquets exist for all
three survey years, no pooled result may be labelled final. The
P3a file complies with the alignment rule on the *year-keying*
dimension (GSUR opportunity year equals the EUROMOD system year:
2014 for FR_2015, 2015 for FR_2016, 2016 for FR_2017) but does
not comply on the *source* dimension (v1 fallback rates, not
GSURv2). The provisioning label
`provisional_v1_fallback_opportunity_year_aligned` correctly
encodes both the compliance (opportunity-year-aligned) and the
non-compliance (v1_fallback) dimensions.

The P3a construction is therefore provisional by design and by
explicit label. It is not a final or reportable data product.
The classification PASS WITH PROVISIONAL LIMITATIONS reflects a
build that is mechanically sound but constructed on an
intentionally interim opportunity-side input that must be
replaced before any estimation result derived from the file can
enter the paper.

**Permitted use of the current P3a file under this verdict:**
pipeline diagnostics and construction validation only. The file
is fit for validating pipeline mechanics (stacking, identity
validation, CPI harmonisation, cluster-key annotation, and cross-
year stability diagnostics). This verdict does **not** authorise
pooled estimation, even as a provisional dry-run. Any provisional
pooled estimation would require a separate explicit
authorisation that specifies the estimation scope, the inference
procedure, and the segregation of any dry-run results from the
final registry. The file is **not** fit for final or reportable
estimation. No parameter estimate, elasticity, welfare quantity,
or any other numerical result derived from this file may be
reported as a final JMP result under any framing.

The remainder of this verdict documents the evidence supporting
the classification and specifies the gating decisions for
downstream work.

---

## 2. What Stage M1 P3a constructed

Stage M1 P3a constructed a draw-expanded pooled MNL-input dataset
covering metropolitan France for the three survey years 2015,
2016, and 2017, comprising both singles and couples household
types. The construction executed the five-step Stage M1 pipeline:
year stacking with stacked-identifier engineering (Step 1),
cross-year identity validation (Step 2), CPI/HICP harmonisation
(Step 3), cluster-key annotation (Step 4), and the V1 through V9
validation battery (Step 5).

The two output products are the stacked-raw parquet
(`fr_p3a_stacked_raw.parquet`, 139 columns) and the harmonised
parquet (`fr_p3a_harmonised.parquet`, 143 columns). The
harmonised parquet extends the stacked-raw parquet by three
real-deflated monetary columns (`ils_dispy_real`,
`ils_earns_real`, `yem_real`) and one cluster-key column
(`cluster_id`). Each output product carries a Stage M1 metadata
sidecar recording the provisioning label, the input scope, the
authorization flags, the per-year and per-component row and
household counts, the per-component GSUR means, and the complete
V1 through V9 and identity-validation results.

The pooled dataset contains 1,244,500 draw-expanded rows
representing 12,445 household-years at 100 draws per household.
The household-year composition is 5,007 single household-years
(500,700 rows) and 7,438 couple household-years (743,800 rows).
The pooled sample corresponds to the (P3) configuration of the
multi-year strategy memo — the full three-year pool including the
2016–2017 rotational-panel overlap — and is the data foundation
on which a future pooled estimation, if authorised, would operate
under cluster-robust inference.

The construction realises the Stage M1 design specified in the
multi-year strategy memo §6 (stacked-ID engineering), §5
(CPI harmonisation), and §8 (cluster-key annotation at the raw
household level). The opportunity-side GSUR variable is sourced
from the v1 fallback lookup per the GSUR year-alignment decision
§5 (provisional Stage M1 dry-run under v1 fallback, subject to
explicit labelling), not from the GSURv2 construction that the
final pooled build requires.

---

## 3. Why the first couples-only run was insufficient

The first Stage M1 P3a run produced a couples-only pooled dataset
and was insufficient for a definitive structural reason: it
omitted the entire singles population from the pooled sample.

The defect originated in the component-discovery logic of
`m1_stack_years.py`. The original `_find_parquet(year, cfg)`
function returned a single parquet path per year, selecting
`candidates[0]` after an alphabetical sort of the matching glob
candidates. Because "couples" precedes "singles" in alphabetical
order, the function silently selected the couples parquet for
each year and discarded the singles parquet. The resulting pooled
dataset contained 743,800 rows from 7,438 couple household-years
across the three years and contained zero singles rows.

The omission is not a marginal data-quality issue; it is a
structural sample-definition failure. The RURO labour-supply
model is estimated jointly across four demographic groups
(singles male, singles female, couples male, couples female). A
pooled dataset omitting the singles population would support
estimation of only the couples sub-model, would not deliver the
sample-size augmentation in the singles consumption sub-block
that motivates the pooled extension (the singles consumption
joint-identification limitation documented in the M1-clean
verdict is a singles-group limitation), and would silently
misrepresent the pooled sample as the full RURO sample when it
was in fact a couples-only subset.

The defect was also silent: the original `_find_parquet()`
returned a valid path and the pipeline completed without error,
producing a syntactically well-formed pooled parquet that passed
the validation checks as they were then written. A couples-only
dataset that completes cleanly and passes validation is more
dangerous than one that fails loudly, because it can enter
downstream estimation undetected. The insufficiency is therefore
both a sample-definition failure and a validation-coverage gap:
the original validation battery did not detect the absence of an
entire household type.

---

## 4. Whether the repair resolved the couples-only problem

**Yes. The repair resolved the couples-only defect at its root
cause and added validation coverage to prevent its recurrence.**

The repair replaced the single-path `_find_parquet(year, cfg)`
function with `_find_component_parquets(year, cfg)`, which
iterates over the configured `input_parquet_components` list
(read from the stage-config YAML; default `["singles",
"couples"]`) and, for each component, selects the first glob
candidate whose filename contains the component-name substring.
The function returns a list of `(component_name, path)` tuples,
one per component, rather than a single path. The
`_resolve_inputs()` return type was correspondingly changed from
`Dict[int, Optional[Path]]` to `Dict[int, List[Tuple[str,
Path]]]`, and the `stack()` inner loop was updated to load each
component, annotate it with a `household_type` column equal to
the component name, and concatenate the components within each
year under a schema union (`pd.concat(join='outer')`) before the
stacked-identifier engineering is applied.

The repair addresses the root cause directly: component discovery
is now explicit and exhaustive over the configured component
list, rather than implicit and singular through an alphabetical
fallback. The alphabetical-selection failure mode is structurally
eliminated; the stacker can no longer silently discard a
component because every configured component is loaded by
construction.

The repair also closed the validation-coverage gap. The dry-run
report was updated to print per-component FOUND/NOT FOUND lines
per year (the execution report §5 records all six parquets — two
per year — as FOUND before execution). The V8 GSUR-coverage check
was made household-type-aware (§10 of this verdict), so that the
mixed-schema dataset is validated per component rather than
globally. The identity-validation and V7 checks were made dag-
mask-aware (§9 of this verdict) so that the mixed singles-couples
schema does not produce spurious age-progression warnings. The
manifest was extended with per-component row and household counts.

The prior couples-only outputs were archived to
`Data/processed/fr/pooled/archive_couples_only_20260520_120132/`
(four files: the two parquets and their two sidecars) and removed
from the active pooled directory before the re-run. The archival
is consistent with the readiness report's prohibition on silent
file deletion: the defective outputs are retained under an
explicit archive path rather than overwritten or deleted.

The repair is therefore both corrective (the root-cause logic is
fixed) and preventive (validation coverage is added). The
couples-only problem is resolved.

---

## 5. Whether singles and couples are now both included

**Yes. Both household types are present across all three survey
years, confirmed by row counts, household counts, the
`household_type` column, and per-component GSUR coverage.**

The `household_type` column is present in both output parquets
and is correctly populated with `"singles"` or `"couples"` for
every row. The column is the explicit marker that distinguishes
the two household types in the mixed-schema pooled dataset and
enables the per-component validation logic.

The component composition is confirmed at the row and household
level. The singles population contributes 500,700 rows from 5,007
single household-years; the couples population contributes
743,800 rows from 7,438 couple household-years. Both populations
are present in each of the three survey years: 2015 contributes
1,669 single and 2,566 couple households; 2016 contributes 1,676
single and 2,577 couple households; 2017 contributes 1,662 single
and 2,295 couple households.

The schema-union construction is documented in the execution
report §25. The pooled dataset carries 33 columns common to both
household types, 42 singles-only columns (including the singles
scalar `gsur`, `dag`, `ils_dispy`, the education indicators, and
the region indicators), 60 couples-only columns (including
`gsur_female`, `gsur_male`, the gendered demographic and income
columns), four columns added by the stacker (`year_tag`,
`stacked_hh_uid`, `stacked_person_uid`, `household_type`), three
real-deflated columns added by harmonisation, and one cluster-key
column. The schema union is the correct mechanism for combining
the differing singles and couples column structures into a single
pooled parquet; the household-type-specific columns are NaN for
the non-applicable household type by construction, and the
validation logic accounts for this through the per-component
checks.

The inclusion of both household types is the defining success
criterion of the repair, and it is met. The pooled dataset is the
full RURO sample (singles and couples) for the three-year pool,
not a couples-only subset.

---

## 6. Row-count and household-count validation

The row-count and household-count validation passes without
qualification. Table 1 reports the per-year, per-component
composition confirmed by the execution report §11 and the
addendum §2.

| Year | Component | Households | Draws/HH | Rows |
|---|---|---|---|---|
| 2015 | singles | 1,669 | 100 | 166,900 |
| 2015 | couples | 2,566 | 100 | 256,600 |
| 2016 | singles | 1,676 | 100 | 167,600 |
| 2016 | couples | 2,577 | 100 | 257,700 |
| 2017 | singles | 1,662 | 100 | 166,200 |
| 2017 | couples | 2,295 | 100 | 229,500 |
| **Total** | | **12,445** | | **1,244,500** |

The validation check V2 (row-count agreement, execution report
§16) confirms the total of 1,244,500 rows against the YAML
expected count `p3a: 1244500` with a difference of zero. The
per-year row breakdown is 423,500 (2015), 425,300 (2016), and
395,700 (2017), each matching the sum of its singles and couples
components exactly. The per-year household breakdown is 4,235
(2015), 4,253 (2016), and 3,957 (2017).

Two cross-checks confirm the counts are not artefacts of the
stacking arithmetic. First, the 2016 household count of 4,253
matches the established single-year M1-clean 2016 sample size
(766 singles male + 910 singles female + 2,577 couples = 4,253
households), confirming that the 2016 component of the pool
corresponds to the same sample as the accepted single-year
baseline. Second, the addendum §2 records that the observed
household counts match the `sample_sizes.singles_deciders` and
`sample_sizes.couples_deciders` fields in each component's
`__mnlmeta.json` sidecar exactly, confirming that the stacking
preserved the per-component sample definition without inadvertent
filtering or duplication.

The draw-expansion arithmetic is internally consistent:
$12{,}445 \text{ household-years} \times 100 \text{ draws} =
1{,}244{,}500 \text{ rows}$, matching the observed total exactly.
The validation check V1 (execution report §15) confirms that
`(stacked_person_uid, draw)` is row-unique with zero duplicates,
establishing that the draw expansion did not introduce
collisions.

The row-count and household-count validation is a clean PASS.

---

## 7. Stacked-ID validation

The stacked-identifier engineering passes validation without
qualification. The construction adds two stacked identifiers
(`stacked_hh_uid`, `stacked_person_uid`) and a year tag
(`year_tag`) to disambiguate records across the three survey
years.

The validation check V1 (execution report §15) confirms four
properties of the stacked identifiers. The `stacked_person_uid`
is unique at the person-year level across 12,445 person-years.
Each person-year is expanded to exactly 100 draws. The composite
`(stacked_person_uid, draw)` is row-unique with zero duplicates
across all 1,244,500 rows. The `stacked_hh_uid` is unique per
household-year across 12,445 household-year groups.

The cross-year UID collision check (execution report §11)
confirms zero collisions: no stacked identifier constructed for a
record in one survey year coincides with a stacked identifier
constructed for a record in a different survey year. This is the
defining property the stacked-identifier engineering must
guarantee — that records from different years are globally
distinguishable in the pooled identifier space — and it is
confirmed empirically.

The year-tag coverage check V4 (execution report §18) confirms
that the year tags {1, 2, 3} are present in the pooled file and
match the configured expected tags {1, 2, 3} for the p3a
configuration. The year tags correctly partition the pooled
dataset into its three constituent survey years.

The stacked-identifier validation is a clean PASS. The
collision-free property and the per-year/per-household uniqueness
properties together establish that the pooled identifier space is
correctly engineered for downstream estimation and diagnostics.

---

## 8. Raw-ID preservation

The raw-identifier preservation passes validation without
qualification. The construction preserves the original EUROMOD
identifiers under their native column names alongside the derived
stacked identifiers, consistent with the two-layer identifier
design specified in the multi-year strategy memo §6.

The validation check V3 (raw-ID completeness, execution report
§17) confirms that the four raw-identifier columns — `idorighh`,
`idorigperson`, `idhh`, `idperson` — are all present and non-null
across all 1,244,500 rows. The completeness of the raw
identifiers is the precondition for two downstream operations:
the cluster-key annotation (which uses `idorighh` as the raw
household-level clustering key) and any future overlap or panel-
sensitivity diagnostic (which requires the raw household
identifiers to detect the 2016–2017 rotational overlap).

The preservation of the raw identifiers under their native names,
distinct from the engineered stacked identifiers, respects the
division of labour articulated in the multi-year strategy memo §6
Element I6: the stacked identifiers serve the engineering purpose
of cross-year disambiguation, while the raw household identifiers
serve the inferential purpose of cluster-robust standard-error
computation. The two identifier layers coexist in the pooled
dataset without conflation, and the raw layer is complete.

The raw-ID preservation is a clean PASS.

---

## 9. Identity-validation evidence

The cross-year identity validation passes and confirms the
expected EU-SILC rotational-panel structure. The validation
(execution report §12 and §21) examines the three pairwise year
combinations for repeat persons and households and computes
stability metrics on the repeat sets.

The 2015→2016 and 2015→2017 pairs exhibit zero repeat persons and
zero repeat households, confirming the disjoint structure
established in the raw-data findings: the 2015 cross-section
shares no households with either the 2016 or the 2017 cross-
section. Both pairs PASS as disjoint.

The 2016→2017 pair exhibits 2,743 repeat persons across 2,788
repeat households. The execution report §12 documents that the
observed repeat-household count of 2,788 is below the full
EU-SILC rotational-design expectation of 8,796, and attributes
the difference to the RURO working-age sample filter: not all
panel members who appear in both raw cross-sections meet the
RURO inclusion criteria (age 25–65, the sample-perimeter
restrictions). The difference is expected and does not constitute
a validation failure; it is the predictable consequence of
applying the RURO sample selection to the rotational panel.

The stability metrics on the 2016→2017 repeat set are strong. The
sex-stability rate is 1.0000 (every repeat person retains a
consistent sex code across the two years). The age-progression-
within-one-year rate is 1.0000, computed on the dag-non-null
singles subset (N ≈ 1,105 singles repeaters with valid `dag` in
both years). The suspicious-record rate is 0.0000. The household-
continuity rate is 0.9985. The working-age education-stability
rate is 0.9754.

The age-progression metric warrants a methodological note. In the
mixed singles-couples schema, the `dag` (age) variable is NaN for
couples rows. The original identity-validation logic computed the
age difference over all repeat persons, producing `NaN − NaN =
NaN` for couples repeaters; because pandas evaluates `NaN <= 1`
as False, the age-progression rate was diluted to a spurious
0.4028 (reflecting the 59.7 per cent couples share of repeaters
rather than any genuine age-progression failure). The repair
added a dag-mask (`dag_mask = s1["dag"].notna() &
s2["dag"].notna()`) that restricts the age-progression check to
the singles repeaters with valid age data and reports the check
as not-checked when all repeaters are couples. The post-fix
age-progression rate of 1.0000 is computed on the genuine
singles-repeater subset and is correct. The dag-mask fix is a
validation-logic correction, not a data correction; the
underlying age data is unaffected.

The identity-validation evidence is a clean PASS, with the
2016→2017 repeat structure correctly characterised and the
mixed-schema age-progression check correctly computed on the
applicable subset.

---

## 10. CPI/HICP harmonisation evidence

The CPI/HICP harmonisation passes validation, with one expected
range warning that does not affect the deflation correctness.

The harmonisation (execution report §13) applies the year-
specific deflation factor $\phi_t$ to the monetary variables,
producing the real-deflated columns `ils_dispy_real`,
`ils_earns_real`, and `yem_real`. The deflation factors are
$\phi_{2015} = 1.0031$, $\phi_{2016} = 1.0000$, and $\phi_{2017}
= 0.9886$, with 2016 as the base year (deflation factor of unity,
consistent with the multi-year strategy memo §5 decision D1 that
fixes the base year at 2016). The factors are consistent with the
expected direction: 2015 monetary values are inflated slightly to
2016 prices (the 2015 price level was below 2016), and 2017
monetary values are deflated slightly to 2016 prices (the 2017
price level was above 2016).

The CPI source is `Data/external/cpi_hicp_fr_harmonisation.csv`
(the EUROMOD HICPCONFIG.xml option), and the CPI spot-check
maximum error is 0.0 (exact). The validation check V5 (CPI
deflation correctness, execution report §19) confirms that the
deflation formula `real = nominal * phi_t` holds exactly (maximum
error 0.0) across all rows where the nominal value is non-null.

The harmonisation correctly handles the mixed schema. The
`ils_dispy_real` column is computed for singles rows (where
`ils_dispy` is non-null) and is NaN for couples rows (the couples
parquets do not carry the `ils_dispy` column, carrying instead
the gendered `ils_dispy_female` and `ils_dispy_male`). This is
the intended behaviour for the mixed schema, not a defect.

The V5 range warning is expected and documented. The validation
configuration sets an `ils_dispy_real` range of [25,000–55,000],
calibrated for couple-household disposable income (the couples
mean is approximately 35,000–40,000 EUR). In the mixed dataset,
`ils_dispy_real` is NaN for couples rows, so the pandas `.mean()`
returns the singles-only mean of approximately 7,500 EUR per year
(2015: 7,583; 2016: 7,587; 2017: 7,492), which falls below the
couples-calibrated range and triggers a WARN. The warning
reflects a calibration mismatch in the validation range, not a
deflation error; the deflation formula check passed exactly. The
range mismatch is recorded as a pre-publication validation-
quality item (§15 and §16 of this verdict).

The harmonisation skipped four monetary columns absent from the
parquets (`yse`, `ypen`, `ypt`, `ils_ben`), which is expected
given the MNL-stage output schema.

The CPI/HICP harmonisation evidence is a PASS, with the range
warning correctly classified as a validation-calibration item
rather than a deflation error.

---

## 11. Cluster-key evidence

The cluster-key annotation passes validation. The construction
(execution report §14) annotates every row with a `cluster_id`
equal to the raw original-household identifier `idorighh`, for
use in the cluster-robust standard-error computation that any
future pooled estimation requires.

The annotation is complete: `cluster_id = idorighh` for all
1,244,500 rows, with `null_count(idorighh) = 0`. The validation
check V6 (clustering-key integrity, execution report §20)
confirms the identity `cluster_id == idorighh` across all rows.

The number of unique clusters is 9,657. The execution report §14
documents that this increased from 5,838 in the couples-only run,
the increase reflecting the addition of the singles households.
The unique-cluster count is the number of distinct raw households
in the pooled sample; it is below the household-year count of
12,445 because the 2,788 households appearing in both 2016 and
2017 (the rotational-panel overlap) are counted once in the
cluster space but twice in the household-year space.

The cluster-key choice is correct per the multi-year strategy
memo §6 Element I6 and §8 Treatment T1: the clustering key is the
raw household identifier (`idorighh`), not the engineered stacked
identifier. Clustering on the raw household identifier correctly
treats the two annual appearances of a 2016–2017 overlap
household as a single cluster, preserving the within-household
serial correlation that the cluster-robust correction is designed
to account for. Clustering on the stacked identifier would
instead treat each annual appearance as an independent cluster,
defeating the purpose of the correction. The construction uses
the correct key.

The V6 overlap warning is expected. The cross-year overlap check
records 2,788 repeat households in the 2016×2017 pair against an
expected 8,796 (the full EU-SILC rotational design), a difference
of 6,008 that exceeds the validation tolerance of 200 and
triggers a WARN. As with the identity validation (§9), the
difference reflects the RURO working-age sample filter and is
expected; the full rotational overlap is not preserved after the
RURO sample selection. The warning does not affect the clustering
validity: the 2,788 overlap households are correctly assigned to
shared clusters, which is the property the cluster key must
guarantee. The warning is a tolerance-calibration item, not a
clustering error.

The cluster-key evidence is a PASS, with the overlap warning
correctly classified as an expected consequence of the sample
filter.

---

## 12. GSUR coverage

The GSUR coverage passes validation. The validation check V8
(execution report §22) confirms that the opportunity-side GSUR
variable is fully populated within each household type, with zero
missing values in the applicable GSUR columns for each component.

The coverage is checked per component, reflecting the differing
GSUR column structure of the two household types. The singles
population (500,700 rows) carries the scalar `gsur` column with
zero missing values. The couples population (743,800 rows)
carries the gendered `gsur_female` and `gsur_male` columns, each
with zero missing values. The per-component check was introduced
in the repair (§10 of the execution report) to replace a global
GSUR check that would have failed on the mixed schema: a global
check would treat the couples-only `gsur_female`/`gsur_male`
columns as having missing values for all singles rows, and the
singles-only `gsur` column as having missing values for all
couples rows, producing a spurious failure. The household-type-
aware check correctly validates each component against its
applicable GSUR columns.

The reported GSUR means (from the couples sidecar) are
`gsur_female = 0.0902` and `gsur_male = 0.0961`. The singles
`gsur` mean is not reported in the evidence (the execution report
§22 notes it as a v1 scalar GSUR with couples-calibrated
reference values).

The GSUR coverage — the completeness of the GSUR variable within
each household type — is a clean PASS. The coverage evidence
establishes that every row carries a populated opportunity-side
GSUR value of the appropriate type. The coverage PASS, however,
concerns only the *completeness* of the GSUR variable, not its
*provenance*; the provenance is the subject of §13 and is the
basis for the provisional classification of the entire
construction.

---

## 13. GSUR provenance and provisional status

The GSUR provenance is the v1 fallback lookup, and this is the
decisive basis for the PASS WITH PROVISIONAL LIMITATIONS
classification of the construction. The provenance is correct on
the year-keying dimension and provisional on the source
dimension.

*Year-keying dimension (compliant).* The GSUR year-alignment
decision §2 establishes that the GSUR opportunity year must equal
the EUROMOD system year, which lags the survey data year by one.
The P3a construction (execution report §26) applies this rule
correctly: FR_2015 uses GSUR opportunity year 2014, FR_2016 uses
GSUR opportunity year 2015, and FR_2017 uses GSUR opportunity year
2016. The input parquets are named accordingly
(`fr_2015_RURO_mnl_v1gsurY2014`, `fr_2016_RURO_mnl_v1gsurY2015`,
`fr_2017_RURO_mnl_v1gsurY2016`), encoding the opportunity-year
alignment in the filename. The alignment is consistent across all
three years. On the year-keying dimension, the construction
complies with the alignment decision.

*Source dimension (provisional).* The GSUR rates are drawn from
the v1 fallback lookup (`FR_gsur_ruro.parquet`), not from the
GSURv2 opportunity-year-aligned construction. The GSUR year-
alignment decision §5 explicitly authorises the v1 fallback for a
provisional Stage M1 dry-run subject to explicit labelling, and
§6 establishes that final pooled estimation requires GSURv2
rebuilt for each opportunity year (2014, 2015, 2016) before any
year's parquet is promoted to final status. The decision §6
states unambiguously that until GSURv2 opportunity-year-aligned
parquets exist for all three survey years, no pooled result may
be labelled final.

The GSURv2 construction currently exists only for opportunity
year 2016 (the year used in the single-year M1-clean baseline).
Complete GSURv2 coverage for the P3a pooled build requires
opportunity years 2014, 2015, and 2016. New GSURv2 construction
is required for opportunity years 2014 and 2015; the existing
2016 GSURv2 provenance and sidecar documentation must also be
locked before any final pooled construction is promoted. The new
2014 and 2015 work requires Eurostat denominator acquisition and
INSEE BDM retrieval, which the alignment decision §6 and §8
designate as out of scope for the current sprint and as a
separate task. Until complete GSURv2 opportunity-year coverage is
available and documented, the pooled construction remains a v1
fallback construction.

The provisioning label
`provisional_v1_fallback_opportunity_year_aligned` correctly
encodes both dimensions: `opportunity_year_aligned` records the
year-keying compliance, and `v1_fallback` records the source-
dimension provisional status. The `provisional` prefix records
that the construction as a whole is not final.

The provenance is therefore the determining factor in the
construction's classification. The construction is mechanically
correct and the GSUR variable is complete and correctly year-
aligned, but the GSUR rates are interim v1 fallback values that
must be replaced by GSURv2 opportunity-year-aligned rates before
any estimation result derived from the file can enter the JMP.
The construction is provisional because it uses the v1 GSUR
fallback. This is the basis for the PASS WITH PROVISIONAL
LIMITATIONS classification and for the restriction of this
verdict's permitted use to pipeline diagnostics and construction
validation only.

---

## 14. V1–V9 validation

The complete validation battery passes. Table 2 summarises the
nine checks (execution report §15 through §24).

| Check | Description | Result |
|---|---|---|
| V1 | Stacked-UID uniqueness | PASS |
| V2 | Row-count agreement | PASS |
| V3 | Raw-ID completeness | PASS |
| V4 | Year-tag coverage | PASS |
| V5 | CPI deflation correctness | PASS (expected range warning) |
| V6 | Clustering-key integrity | PASS (expected overlap warning) |
| V7 | Person-identity validation | PASS |
| V8 | GSUR coverage (per-component) | PASS |
| V9 | Naming-convention check as implemented (`ruro` token absence) | PASS, with cleanup caveat |
| **Overall** | | **PASS** |

The nine checks span the full set of construction-integrity
properties: identifier uniqueness (V1), sample-size agreement
(V2), raw-identifier completeness (V3), year-partition coverage
(V4), monetary-deflation correctness (V5), clustering-key
integrity (V6), cross-year person-identity stability (V7),
opportunity-variable completeness (V8), and naming-convention
compliance (V9). Each check passes.

The V9 wording is itself a package-cleanup issue. In the current
RURO codebase, a naming check should target deprecated
Stijn/person-specific labels rather than the absence of the RURO
token. This does not change the construction result or the V1
through V9 PASS; it only records that the V9 label and future
implementation should be corrected before the validation package
is reused or published.

Two checks (V5, V6) carry expected warnings that are correctly
classified as calibration or sample-filter consequences rather
than construction errors. The V5 range warning reflects the
couples-calibrated income range applied to a mixed dataset whose
`ils_dispy_real` mean is dominated by the lower singles incomes
(§10 of this verdict). The V6 overlap warning reflects the
2,788-versus-8,796 repeat-household difference attributable to
the RURO working-age sample filter (§11 of this verdict). Neither
warning indicates a construction defect; both are documented and
both have correctness-preserving explanations confirmed by the
exact deflation-formula check (V5) and the exact cluster-key
identity check (V6).

The V1 through V9 validation is an overall PASS. The validation
battery establishes the mechanical integrity of the construction.
It does not, and cannot, validate the GSUR provenance: the
validation checks the completeness and structure of the GSUR
variable (V8) but not whether the GSUR rates are v1 fallback or
GSURv2. The provenance limitation (§13) is therefore orthogonal
to the V1 through V9 PASS and is the reason the construction is
classified PASS WITH PROVISIONAL LIMITATIONS despite the clean
validation battery.

---

## 15. Remaining validation caveats

Three validation caveats remain on the record. None constitutes a
construction defect; each is a documented item to resolve before
the validation output is cited in any final document.

*Caveat C1 — V5 income-range calibration.* The
`ils_dispy_real_range` of [25,000–55,000] in the stage-config
YAML is calibrated for couple-household disposable income and
triggers an expected WARN against the singles-dominated mean of
approximately 7,500 EUR. The deflation formula check passed
exactly; the warning is a range-calibration mismatch, not a
deflation error. The caveat is that the validation range should
be updated to cover the singles population (or split by
`household_type`) before the V5 validation output is cited. This
is a validation-quality item, recorded as package-cleanup item C
(§16).

*Caveat C2 — V6 overlap tolerance.* The cross-year overlap check
records 2,788 repeat households in 2016×2017 against an expected
8,796, a difference exceeding the validation tolerance of 200 and
triggering a WARN. The difference is the expected consequence of
the RURO working-age sample filter applied to the EU-SILC
rotational panel. The caveat is that the validation tolerance or
the expected count should be recalibrated to reflect the post-
filter overlap expectation, so that the V6 output does not carry a
warning that requires narrative explanation each time it is cited.
This is a validation-quality item.

*Caveat C3 — singles GSUR mean unreported.* The execution report
§22 does not report the singles `gsur` mean, noting it as a v1
scalar GSUR with couples-calibrated reference values. The caveat
is that the singles GSUR mean should be recorded in the sidecar
and the validation output for completeness, so that the singles
opportunity-side coverage can be audited at the same level of
detail as the couples coverage. This is a documentation-
completeness item.

These three caveats are validation-quality and documentation
items. They do not affect the correctness of the constructed data
(the deflation is exact, the clustering is correct, the GSUR
coverage is complete) and do not alter the V1 through V9 PASS.
They are recorded so that the validation output is publication-
ready before it is cited; they are not blockers for the pipeline-
diagnostics and construction-validation uses for which the file
is fit under this verdict.

The overarching caveat, distinct from the three above, is the
GSUR v1-fallback provenance (§13), which is not a validation-
quality item but a substantive provisional-status limitation that
restricts the file's permitted use and determines the
construction's classification.

---

## 16. Package-cleanup items before reuse

The addendum §10 records six package-cleanup items for pre-
publication action. None affects the correctness of the France
P3a construction; each concerns the reusability of the stacking
package for future configurations or the publication-readiness of
the validation output. Table 3 reproduces the items with their
priorities.

| Item | Location | Description | Priority |
|---|---|---|---|
| A | `m1_stack_years.py` | Combined-file mode removed; `_find_component_parquets()` does not implement the legacy combined-file fallback. A future single-combined-parquet config cannot use the stacker without naming the file to contain a listed component substring or adding a `combined` component. | Pre-publication |
| B | `m1_stack_years.py` | Empty `input_parquet_components` raises `IndexError` at runtime. Add a config-load validation guard. | Pre-publication |
| C | `fr_p3a_stage_m1.yaml` | `ils_dispy_real_range` calibrated for couples; singles mean ~7,500 triggers V5 WARN. Split range by `household_type` or add separate keys. | Pre-publication |
| D | `fr_p3a_stage_m1.yaml` | `expected_row_counts` comment says "draw-expanded" but p2/p3b/p4 entries are still HH-level placeholders. | When p2/p3b/p4 run |
| E | `m1_stack_years.py` docstring | Module docstring does not mention `input_parquet_components` or schema-union behaviour. | Pre-publication |
| F | `m1_validate.py` | `check_v8()` global-fallback branch could silently pass a mixed-type file lacking the `household_type` column. Add a docstring note. | Low priority |
| G | `m1_validate.py` | V9 is worded as a check for absence of `ruro`; future validation should instead check for deprecated Stijn/person-specific labels. | Pre-publication |

Items A and B are the only two with a correctness implication for
future use. Item A is a behavioural regression relative to the
pre-repair stacker for the combined-file use case: the repair
optimised for the France separate-singles-couples convention and
removed the combined-file fallback path. The regression does not
affect France P3a (which has always used separate component
files) but should be documented or restored before the stacker is
reused for a country or dataset that uses a single combined
parquet per year. Item B is a latent failure mode: an empty
component list would silently produce no frames and raise an
`IndexError` rather than a clear configuration error; a config-
load guard would convert the silent failure into an explicit one.

The audit (addendum §8) confirms that the stacker remains country-
and year-agnostic in its core logic: all country-specific and
year-specific values (input directory, glob patterns, component
names, year list, UID scheme, output directory) are read from the
stage-config YAML through `StageConfig`, with no hardcoded
country codes, year lists, file-stem patterns, or component names
in the shared script. A future country would produce a correct,
separately labelled stacked parquet by providing its own stage-
config YAML, subject to the one implicit assumption that the
component name appears as a case-insensitive substring in the
component filenames (the France `__singles.parquet` /
`__couples.parquet` convention satisfies this).

The package-cleanup items are pre-publication and reuse-readiness
items. They are not blockers for the current France P3a work and
do not affect the construction's classification. They are
recorded for action before the stacking package is published or
reused for a new configuration.

---

## 17. Whether pooled estimation is authorized

**No. Pooled estimation is not authorized.**

The construction verdict does not authorise pooled estimation in
any configuration. Three distinct prerequisites are unmet, each
independently sufficient to withhold authorisation.

First, no cluster-robust standard-error wrapper exists for the
RURO estimator. The execution report §29 and the addendum §11
both record that no cluster-robust SE wrapper is implemented. The
(P3) configuration's 2016–2017 rotational overlap means that
approximately half of the pooled observation rows derive from
repeated households (the multi-year strategy memo §2 establishes
the 51.9 per cent repeated-row share at the raw-data level), so
naive independence-based standard errors would be biased downward.
Cluster-robust inference at the raw household level (the cluster
key annotated in §11 of this verdict) is required for valid
inference and is not yet available.

Second, no pooled RURO estimation specification exists. The
execution report §29 records that no pooled spec (YAML or
equivalent) is defined. The pooled specification
`ruro_occ_M1_clean_pooled` articulated in the multi-year strategy
memo §7 (with year fixed effects `beta_E_year2015` and
`beta_E_year2017` and 2016 as the reference year) has not been
implemented as an estimation-ready YAML.

Third, pooled estimation on the provisional file requires a
separate authorisation memo (execution report §29). The
construction verdict authorises only construction-quality use of
the file: pipeline diagnostics and construction validation.
Initiating pooled estimation — even a provisional pooled dry-run
under the v1-fallback label — requires its own authorisation that
specifies the estimation scope, the specification, the inference
procedure, and the segregation of any dry-run results from the
final registry.

The construction verdict's permitted-use determination (§1) does
not authorise pooled estimation. It confirms that the file is
mechanically coherent enough to support pipeline diagnostics; it
does not authorize the act of estimating a pooled RURO model.
That act requires the cluster-robust SE wrapper, the pooled
specification, and a separate authorisation. Pooled estimation is
not authorized by this verdict.

---

## 18. Whether GSURv2 extension is required before final pooled estimation

**Yes. Complete GSURv2 coverage for opportunity years 2014, 2015,
and 2016 is required before final pooled estimation, and it is the
next empirical gate for the multi-year track.**

The GSUR year-alignment decision §6 establishes the requirement
unambiguously: final pooled estimation requires GSURv2 rebuilt for
each opportunity year (2014, 2015, 2016) before any year's parquet
is promoted to final status, and until GSURv2 opportunity-year-
aligned parquets exist for all three survey years, no pooled
result may be labelled final. The current P3a construction
satisfies the year-keying dimension of the alignment rule but
uses v1 fallback rates for all three opportunity years. New
GSURv2 construction is required for opportunity years 2014 and
2015, and the existing 2016 GSURv2 provenance/sidecar
documentation must be locked before a final pooled build can be
claimed.

The GSURv2 coverage gate is therefore the determining empirical
prerequisite for any final or reportable pooled estimation. Its
new data-construction component requires Eurostat denominator
acquisition (the regional unemployment-by-NUTS-2 and population-
denominator series for 2014 and 2015) and INSEE BDM retrieval
(the national unemployment-rate benchmark for 2014 and 2015), per
the alignment decision §6 and §8. Its documentation component
locks the 2016 GSURv2 provenance and sidecar status. The
construction methodology for GSURv2 is governed by the separate
GSUR rebuild specification, not by this verdict; the scheduling
and resourcing of the extension are likewise out of scope for the
construction verdict.

The GSURv2 extension is named as the next empirical gate for the
multi-year track. The distinction between an empirical gate and
the immediate next task (§22) is that the empirical gate is the
substantive prerequisite that must be cleared before final pooled
estimation can produce reportable results, whereas the immediate
next task is the documentation or decision step that initiates
the path to clearing the gate. The GSURv2 extension is the empirical
gate; the construction verdict (this document) and any subsequent
GSURv2 scoping memo are the documentation steps that precede the
gate's execution.

The verdict does not initiate the GSURv2 extension (that requires
its own implementation prompt against the GSUR rebuild
specification) and does not foreclose the alternative path the
addendum §12 records — a future verdict that explicitly accepts
the v1 fallback rates as final for 2015 and 2017. The alignment
decision §6 as currently adopted requires GSURv2; a future
verdict could in principle revise this requirement if the v1-
versus-GSURv2 rate difference (the alignment decision §2 records
a mean absolute difference of approximately 0.010, roughly 10 per
cent of the mean GSUR of 0.095, for the 2015 misalignment case)
is judged immaterial for the pooled estimates. Absent such a
future verdict, the GSURv2 extension is required, and it is the
next empirical gate.

---

## 19. Whether welfare implementation is authorized

**No. Welfare implementation is not authorized, and welfare
computation is not authorized.**

The construction verdict does not authorise welfare
implementation or welfare computation. The addendum §5 and §6
correct a stale statement in the execution report §30 that
implied welfare implementation was an unblocked parallel task; the
correction is adopted in this verdict.

The welfare-measurement decisions memo v2 and the welfare-
scaffolding design memo v2 are both complete (execution report
§29; addendum §6). Their completeness establishes the welfare
*design* — the functional, the inequality index, the
decomposition method, the reference distributions, the gender
attribution rule, and the scaffolding code architecture — but
does not constitute execution authorisation. The readiness report
v2 §15 records welfare scaffolding implementation as NOT
AUTHORISED with the design complete and implementation deferred,
and §18 states that even after a baseline decision, welfare
implementation and welfare computation require their own
implementation report, audit, and authorisation. The existence of
the two design memos authorises neither implementation nor
computation.

The distinction is between welfare design (complete) and welfare
execution (unauthorised). The design memos specify how welfare
will be implemented and computed once authorised; they do not
authorise the implementation or the computation. Welfare
implementation — the construction of the welfare functional, the
inequality index, the reference distributions, and the
decomposition procedure as executable code — requires its own
implementation report and authorisation. Welfare computation —
the numerical production of the JMP's welfare results — requires
the implementation to be complete and additionally requires an
accepted empirical baseline against which the welfare
decomposition is computed.

The empirical-baseline prerequisite for welfare computation is
particularly relevant here. The welfare decomposition must be
computed against an accepted structural baseline. The current
accepted baseline is the single-year M1-clean specification (§20).
A pooled specification would become an accepted baseline only
through a future SA2-style verdict, which requires pooled
estimation, which is itself unauthorised (§17) and gated behind
the GSURv2 extension (§18). The provisional P3a file cannot serve
as the basis for any welfare computation, both because welfare
computation is unauthorised and because the file is provisional.

Welfare implementation is not authorized. Welfare computation is
not authorized. The welfare design work is complete and may inform
the welfare-implementation prompt when that step is separately
authorised, but no welfare execution is authorised by this
construction verdict.

---

## 20. Whether M1-clean remains the active baseline

**Yes. The single-year M1-clean 2016 specification remains the
active JMP structural baseline.**

The construction verdict does not alter the active baseline. The
M1-clean verdict established `ruro_occ_M1_clean` as the preferred
single-year structural baseline under the SA1-STANDS decision,
and the M1-naive robustness verdict confirmed M1-clean as
preferred after the ability-versus-opportunity robustness
exposure. The multi-year strategy memo §10 establishes the
default position that the M1-clean single-year SA1-STANDS verdict
governs until a pooled specification earns its own SA2-style
verdict.

The Stage M1 P3a construction is a data-construction step within
the multi-year track. It produces the pooled dataset on which a
future pooled estimation, if authorised and executed, would
operate. It does not produce any estimation result, any structural
parameter, or any welfare quantity. It cannot, and does not,
displace the M1-clean baseline: a data-construction step is not a
specification verdict, and only a SA2-style verdict on an
estimated pooled specification could replace M1-clean as the
active baseline.

The pooled specification has not been estimated (§17), the GSURv2
prerequisite for final pooled estimation has not been cleared
(§18), and no SA2 verdict has been written. The conditions under
which M1-clean would be replaced are therefore not met and are
several gates distant. M1-clean 2016 remains the active JMP
baseline, and all welfare design, robustness reporting, and paper-
text references continue to treat M1-clean as the primary
structural specification until and unless a future SA2 verdict on
a final (GSURv2-based) pooled specification determines otherwise.

The construction verdict reaffirms M1-clean as the active baseline
without qualification.

---

## 21. Recommended next gate

The recommended next gate is **complete GSURv2 opportunity-year
coverage for 2014, 2015, and 2016**, which is the empirical
prerequisite for any final or reportable pooled estimation (§18).
The gate has three components: data acquisition for the missing
years, construction for opportunity years 2014 and 2015, and
provenance/sidecar locking for the existing 2016 GSURv2 lookup.

The data-acquisition component obtains the Eurostat regional
unemployment and population-denominator series for 2014 and 2015
and the INSEE BDM national-benchmark series for 2014 and 2015,
per the GSUR year-alignment decision §6 and §8 and the multi-year
strategy memo §4 feasibility conditions F3 and F4. The
construction component rebuilds the GSURv2 opportunity-year-
aligned lookup for 2014 and 2015 per the GSUR rebuild
specification. The documentation component locks the source and
sidecar provenance for the existing 2016 GSURv2 lookup. Together,
these components produce complete GSURv2 coverage for all three
opportunity years (2014, 2015, 2016) and enable the P3a MNL-input
parquets to be rebuilt with GSURv2 rates.

The recommended next gate is *not* pooled estimation, *not*
welfare implementation, and *not* the cluster-robust SE wrapper.
Those steps are downstream of the GSURv2 gate: pooled estimation
on a final (GSURv2-based) pooled dataset cannot produce reportable
results until the GSURv2 rates exist, so clearing the GSURv2 gate
is logically prior to investing in the estimation infrastructure
for a *final* pooled run. The cluster-robust SE wrapper and the
pooled specification remain necessary prerequisites for pooled
estimation, but they are most efficiently built once the GSURv2
gate is cleared (or once a future verdict accepts v1 as final),
so that the estimation infrastructure is exercised against the
data product that will actually enter the paper.

An alternative sequencing, recorded for completeness, would defer
the GSURv2 gate and instead request a separate authorisation to
use the current provisional P3a file for a v1-fallback pooled
dry-run. That would exercise the cluster-robust SE wrapper and
the pooled specification against provisional data to validate
estimation mechanics before the final data is available. This
alternative is **not** authorised by this verdict. If later
authorised, its outputs would be strictly dry-run diagnostics
segregated from the final registry, and it would still require
the GSURv2 gate to be cleared before any reportable pooled
result. The recommended primary path is to clear the GSURv2 gate
first.

The recommended next gate is therefore complete GSURv2 coverage
for opportunity years 2014, 2015, and 2016.

---

## 22. Immediate next task

The immediate next task is a **GSURv2 extension scoping and
data-acquisition memo** that operationalises the recommended next
gate (§21). The memo is a documentation and planning task, not an
execution task, and is the natural successor to this construction
verdict.

Tool path: the scoping memo is a Claude Project chat task (design
and planning). The subsequent GSURv2 data acquisition and lookup
construction are Claude Code Sonnet tasks (Eurostat and INSEE BDM
retrieval, lookup rebuild) executed against the GSUR rebuild
specification.

The scoping memo specifies complete GSURv2 coverage for
opportunity years 2014, 2015, and 2016. For 2014 and 2015, it
specifies the exact Eurostat series and extraction parameters
required (the regional unemployment-by-NUTS-2 × sex × education ×
age series and the population-denominator series, matching the
structure of the 2016 GSURv2 retrieval), the INSEE BDM national-
benchmark series and the years required, the construction steps
that rebuild the GSURv2 opportunity-year-aligned lookup, and the
validation steps that confirm the rebuilt lookup against the
national benchmark. For 2016, it records the provenance and
sidecar-locking action for the existing GSURv2 lookup. The memo
also specifies the parquet-rebuild steps that regenerate the P3a
MNL-input parquets with GSURv2 rates.

The scoping memo does not authorise the GSURv2 construction; it
specifies the construction so that a subsequent implementation
prompt can execute it. The execution of the GSURv2 extension —
the data acquisition, the lookup rebuild, the parquet
regeneration — is the empirical work that clears the next gate and
is sequenced after the scoping memo.

Tasks explicitly not authorised by this verdict, and not the
immediate next task:

- Pooled estimation in any configuration (§17): gated behind the
  cluster-robust SE wrapper, the pooled specification, and a
  separate authorisation, and behind the GSURv2 gate for any
  final result.
- Welfare implementation and welfare computation (§19): gated
  behind their own implementation reports, audits, and
  authorisations, and behind an accepted empirical baseline.
- Canonical MNL promotion: the P3a file carries the provisional
  label and is not eligible for promotion.
- P3b execution: hard-blocked pending the ISF comparability gate
  (execution report §2).
- P4 execution: not authorised (execution report §2).
- Any Stage M1 P3a re-run: the construction is complete; no
  re-run is authorised.
- Modification of the M1-clean specification or displacement of
  the M1-clean baseline (§20): M1-clean remains active until a
  future SA2 verdict on a final pooled specification.

The construction verdict's disposition is therefore: the Stage M1
P3a provisional construction PASSES WITH PROVISIONAL LIMITATIONS;
the file is fit for pipeline diagnostics and construction
validation under this verdict; any provisional pooled estimation
requires separate explicit authorisation; complete GSURv2
coverage for opportunity years 2014, 2015, and 2016 is the next
empirical gate; the immediate next task is the GSURv2 extension
scoping memo; and M1-clean 2016 remains the active JMP baseline.
