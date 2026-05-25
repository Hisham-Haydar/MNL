# JMP GSURv2 Multi-Year Extension — Design Memo v1

Date: 2026-05-20

Specification class: data-design memo. The memo specifies the
extension of the GSURv2 opportunity-side lookup construction from
the single opportunity year 2016 (currently built) to the three
opportunity years 2014, 2015, and 2016 required by the multi-year
pooled estimation. It is a design document; it does not authorise
or execute the GSURv2 construction, the pooled estimation, or any
welfare work.

Reference documents:
- `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md`
  (the construction verdict naming the GSURv2 extension as the next
  empirical gate)
- `docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule and the GSURv2 final-construction requirement)
- `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md` (the canonical
  GSURv2 construction methodology — crosswalk, denominator,
  benchmark, validation)
- `docs/RURO_GSUR_v2_stageA_implementation_report_v1.md` (the
  existing 2016 GSURv2 build, against which the extension is
  parameterised)
- `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md`
  (the P3a provisional construction the extension will eventually
  replace at the opportunity-side input)
- `Results/JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md`

Scope of memo: the memo specifies what the GSURv2 multi-year
extension must produce, what external inputs it requires, how the
existing 2016 GSURv2 construction code is parameterised for the
additional years, what changes the construction script requires,
and what validation and metadata the extended outputs must carry.
The memo does not run the construction, does not estimate pooled
models, does not compute welfare, and does not authorise pooled
estimation, welfare implementation, or welfare computation.

---

## 1. Purpose

The purpose of this memo is to specify the design of the GSURv2
multi-year extension: the construction of GSURv2 opportunity-side
lookups for opportunity years 2014 and 2015, alongside the
existing opportunity year 2016, so that all three survey years of
the multi-year pooled sample (FR_2015, FR_2016, FR_2017) can be
keyed to GSURv2 opportunity-year-aligned rates rather than v1
fallback rates.

The memo serves five specific functions. First, it establishes
the survey-year-to-opportunity-year mapping that the extension
must satisfy (§3) and audits the current GSUR status of each
survey year and each opportunity year (§4, §5). Second, it
specifies the GSURv2 outputs the extension must produce (§6) and
the external Eurostat and INSEE inputs they require (§7). Third,
it determines whether the existing 2016 GSURv2 construction code
can be parameterised by opportunity year rather than rewritten,
and specifies the script changes the parameterisation requires
(§8, §9), together with the crosswalk, denominator, and benchmark
logic the additional years require (§10, §11, §12). Fourth, it
specifies the validation checks and sidecar metadata the extended
outputs must carry (§13, §14) and the treatment of the existing
2016 GSURv2 build (§15). Fifth, it situates the extension within
the multi-year pipeline by specifying its interaction with the
P3a construction (§16), what remains provisional until the
extension is complete (§17), and whether pooled estimation may
proceed before the extension (§18).

The memo concludes with an implementation-audit task (§19) and
the exact Claude Code prompt that initiates the extension (§20).
The prompt is the memo's operational deliverable; the memo itself
is design only.

---

## 2. Why GSURv2 extension is needed before final pooled estimation

The GSURv2 extension is required before final pooled estimation
for one decisive reason established by the GSUR year-alignment
decision and reaffirmed by the P3a construction verdict: the
final pooled sample must key the opportunity-side GSUR variable to
GSURv2 opportunity-year-aligned rates for every survey year, and
GSURv2 currently exists only for opportunity year 2016.

The GSUR year-alignment decision §6 establishes the requirement
in categorical terms: final pooled estimation requires GSURv2
rebuilt for each opportunity year (2014, 2015, 2016) before any
year's parquet is promoted to final status, and until GSURv2
opportunity-year-aligned parquets exist for all three survey
years, no pooled result may be labelled final. The P3a
construction verdict §18 reaffirms the requirement and names the
GSURv2 extension to opportunity years 2014 and 2015 as the next
empirical gate.

The substantive justification is the internal consistency of the
structural model. The GSUR rate proxies the probability that a
randomly drawn job offer within a region-sex-education cell is
acceptable to the worker; the alignment decision §7 establishes
that this probability is an equilibrium object from the same
institutional environment that determines the EUROMOD-simulated
net incomes — the EUROMOD system year, not the survey collection
year. The current P3a construction satisfies the year-keying
dimension of the alignment rule (the GSUR opportunity year equals
the EUROMOD system year for each survey year) but uses v1 fallback
rates rather than GSURv2 rates. The v1 fallback rates are not
education-stratified and rest on the withdrawn v1 crosswalk; the
GSURv2 rates are education- and sex-stratified and rest on the
verified post-2016-to-pre-2016 NUTS crosswalk that the rebuild
specification §3 and §4 require.

The difference between the v1 and GSURv2 rates is not negligible.
The Stage A implementation report §6 documents that the
corrected (GSURv2) rates differ substantially from the
reconstructed v1 rates because v1 used no education stratification
(collapsing to the cross-education total), used an incorrect
crosswalk with misaligned region codes, and did not apply the
proper post-2016 NUTS codes. The single-year M1-clean baseline is
estimated against the GSURv2 2016 lookup precisely because the v1
rates were judged inadequate for the opportunity-side
specification. A final pooled estimation that mixed GSURv2 2016
rates (for the FR_2017 survey year) with v1 fallback rates (for
the FR_2015 and FR_2016 survey years) would be internally
inconsistent: the opportunity-side variable would be constructed
by two different methodologies across the pooled sample, confounding
any year-fixed-effect interpretation with a methodology artefact.

The GSURv2 extension is therefore the precondition for a final
pooled sample in which the opportunity-side variable is
constructed by a single consistent methodology across all three
survey years. It is required before final pooled estimation, and
it is the next empirical gate.

---

## 3. Required survey years and opportunity years

The multi-year pooled sample comprises three survey years, each
mapped to its EUROMOD system year and its required GSUR
opportunity year per the year-alignment decision §2. Table 1
reproduces the mapping.

| Survey data year | EUROMOD system year | Required GSUR opportunity year |
|---|---|---|
| FR_2015 | FR_2014 | 2014 |
| FR_2016 | FR_2015 | 2015 |
| FR_2017 | FR_2016 | 2016 |

The required opportunity years are therefore 2014, 2015, and
2016. The EUROMOD system year lags the survey data year by one;
the GSUR opportunity year equals the EUROMOD system year. The
mapping is the operative requirement the GSURv2 extension must
satisfy: the extension must produce GSURv2 lookups for opportunity
years 2014 and 2015 (the two years not currently built) so that,
together with the existing opportunity year 2016, all three
required opportunity years are available in GSURv2 form.

The required decisions stated in the task are confirmed: the
survey years are 2015, 2016, and 2017; the required GSUR
opportunity years are 2014, 2015, and 2016; new GSURv2
construction is required for opportunity years 2014 and 2015.

---

## 4. Current GSUR status by survey year

Table 2 audits the current GSUR status of each survey year in the
P3a provisional construction, drawing on the execution report §5
and §26 and the year-alignment decision §2 through §4.

| Survey year | Opportunity year | Current GSUR source | Year-keying status | Source status |
|---|---|---|---|---|
| FR_2015 | 2014 | v1 fallback (`FR_gsur_ruro.parquet`, key year=2014) | aligned | v1 fallback (provisional) |
| FR_2016 | 2015 | v1 fallback (`FR_gsur_ruro.parquet`, key year=2015) | aligned | v1 fallback (provisional) |
| FR_2017 | 2016 | v1 fallback (`FR_gsur_ruro.parquet`, key year=2016) | aligned | v1 fallback (provisional) |

Every survey year in the current P3a construction uses v1 fallback
rates with correct opportunity-year keying. The input parquets are
named to encode the v1-fallback source and the opportunity year
(`fr_2015_RURO_mnl_v1gsurY2014`, `fr_2016_RURO_mnl_v1gsurY2015`,
`fr_2017_RURO_mnl_v1gsurY2016`).

A notable status discontinuity exists between the multi-year P3a
construction and the single-year M1-clean baseline. The single-
year M1-clean 2016 baseline is estimated against the GSURv2 2016
lookup (the `fr_2016_RURO_mnl_GSURv2` parquets), keyed to
opportunity year 2016. In the multi-year P3a construction, the
2016 *opportunity year* is required by the FR_2017 *survey year*
(not the FR_2016 survey year), because the alignment rule maps
FR_2017 → system year 2016 → opportunity year 2016. The FR_2016
survey year in the multi-year construction requires opportunity
year 2015, which does not yet exist in GSURv2. The status by
survey year therefore differs from the single-year baseline: the
single-year baseline's 2016-survey-year GSURv2 rates correspond to
the multi-year construction's FR_2017-survey-year opportunity-year-
2016 requirement, not to the FR_2016-survey-year opportunity-year-
2015 requirement.

The implication is that the existing GSURv2 2016 lookup, built for
the single-year baseline, is the lookup required by the FR_2017
survey year in the multi-year construction, and the two GSURv2
lookups still required (opportunity years 2014 and 2015) serve the
FR_2015 and FR_2016 survey years respectively.

---

## 5. Current GSUR status by opportunity year

Table 3 audits the current GSUR status by opportunity year, which
is the operative dimension for the extension (the GSURv2
construction is keyed by opportunity year, not survey year).

| Opportunity year | Required by survey year | GSURv2 status | v1 fallback status |
|---|---|---|---|
| 2014 | FR_2015 | NOT BUILT — extension required | available (v1 `FR_gsur_ruro.parquet`, year=2014) |
| 2015 | FR_2016 | NOT BUILT — extension required | available (v1 `FR_gsur_ruro.parquet`, year=2015) |
| 2016 | FR_2017 | BUILT — `FR_gsur_ruro_v2_stageA.parquet` (year=2016) | available (v1 `FR_gsur_ruro.parquet`, year=2016) |

The opportunity-year audit isolates the extension requirement
precisely. GSURv2 exists for opportunity year 2016 only (the Stage
A build documented in the implementation report, 54 rows: 48
active drgn1=1..8 cells × educ3 × sex plus 6 drgn1=9 stubs).
GSURv2 does not exist for opportunity years 2014 or 2015. The v1
fallback lookup (`FR_gsur_ruro.parquet`) contains rows for years
2007–2024, so v1 rates are available for all three opportunity
years, which is what enables the current provisional P3a
construction (year-alignment decision §2 and §5).

The extension's task is therefore narrowly defined: produce GSURv2
lookups for opportunity years 2014 and 2015 by the same
methodology that produced the existing opportunity-year-2016
lookup, and verify that the existing opportunity-year-2016 lookup
is documented cleanly enough to be reused without rebuild.

---

## 6. Required GSURv2 outputs

The extension must produce two new GSURv2 lookup parquets and
confirm the provenance of one existing lookup parquet. Table 4
specifies the required outputs.

| Output | Path | Status | Rows (expected) |
|---|---|---|---|
| GSURv2 lookup, opportunity year 2014 | `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet` | TO BE BUILT | 54 (48 active + 6 drgn1=9 stubs) |
| GSURv2 lookup, opportunity year 2015 | `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` | TO BE BUILT | 54 (48 active + 6 drgn1=9 stubs) |
| GSURv2 lookup, opportunity year 2016 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` (existing) or `_y2016.parquet` (renamed) | EXISTING — provenance lock required (§15) | 54 (confirmed) |

Each new GSURv2 lookup must replicate the schema of the existing
2016 lookup (implementation report §4): eleven columns comprising
`year`, `drgn1`, `educ3`, `sex`, `gsur`, `weighting_source`,
`gsur_age_band_used`, `gsur_legacy_misaligned`, `denom_flag`,
`n_components`, and `gsur_unreliable`. The `year` column carries
the opportunity year (2014 or 2015 respectively). The row count is
54 (48 active drgn1=1..8 cells across educ3 ∈ {0,1,2} and sex ∈
{M,F}, plus 6 drgn1=9 stubs carrying NaN), matching the existing
2016 lookup's row count.

The construction methodology for each new lookup is identical to
the existing 2016 build per the rebuild specification §5: for each
(drgn1, educ3, sex) cell, the GSUR rate is the population-weighted
mean of the contributing NUTS-2 unemployment rates, where the
weights are the D2 population denominators and the sum runs over
the NUTS-2 components of the drgn1 group (implementation report
§3 O2). The only inputs that change across opportunity years are
the year-specific Eurostat unemployment rates and population
denominators and the year-specific INSEE national benchmark (§7);
the crosswalk and the aggregation logic are year-invariant (§10,
§11).

The extension does not produce MNL parquets. The MNL-parquet
rebuild (merging the GSURv2 lookups into the FR_2015 and FR_2016
MNL inputs) is a downstream step, gated separately, that follows
the lookup construction. The extension's outputs are the three
opportunity-year lookups; the MNL merge is out of scope for this
memo and for the construction it specifies.

---

## 7. Required Eurostat / INSEE inputs

The extension requires year-specific external inputs for
opportunity years 2014 and 2015, matching the structure of the
inputs used for the existing 2016 build (implementation report
§2). Table 5 specifies the required inputs.

| Input | Role | 2016 (existing) | 2014 (required) | 2015 (required) |
|---|---|---|---|---|
| Eurostat `lfst_r_lfu3rt` unemployment rates by NUTS-2 × sex × ISCED × age band | UR numerator | `Data/external/FR_gsur.xlsx` (dataset `lfst_r_lfu3rt__custom_19204794`) | retrieve 2014 extract | retrieve 2015 extract |
| Eurostat `lfst_r_lfsd2pop` population denominators (D2) | population weights | `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | `lfst_r_lfsd2pop_FR_2014.tsv` | `lfst_r_lfsd2pop_FR_2015.tsv` |
| INSEE BDM 001688526 national unemployment benchmark | L5 benchmark | `Data/external/insee_001688526_2016.csv` (9.725%) | `insee_001688526_2014.csv` | `insee_001688526_2015.csv` |
| `fr_drgn1_to_nuts2_crosswalk.csv` | drgn1→NUTS2 crosswalk (O1) | `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | reuse (year-invariant) | reuse (year-invariant) |
| `NUTS2013-NUTS2016.xlsx` | NUTS renaming reference | `Data/external/NUTS2013-NUTS2016.xlsx` | reuse (year-invariant) | reuse (year-invariant) |

The required new inputs are the year-specific unemployment-rate
extracts, population-denominator files, and national-benchmark
files for 2014 and 2015. The Eurostat `lfst_r_lfu3rt` and
`lfst_r_lfsd2pop` series are published back to 2009 and earlier in
the Eurostat data warehouse, so the 2014 and 2015 extracts are
expected to be available pending retrieval confirmation. The INSEE
BDM 001688526 series is published continuously, so the 2014 and
2015 annual values are expected to be available pending retrieval.

The crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`) and the NUTS
renaming reference (`NUTS2013-NUTS2016.xlsx`) are year-invariant
and are reused without modification: the drgn1-to-NUTS-2 mapping
is a function of the EUROMOD regional coding and the NUTS vintage
correspondence, neither of which depends on the opportunity year.
The crosswalk's 22 rows (all carrying `verified_against_eurostat
= YES` per implementation report §3 O1) apply equally to all three
opportunity years.

One acquisition caveat warrants explicit note. The Eurostat
unemployment-rate series at the NUTS-2 × sex × ISCED × age-band
level carries reliability flags (the `u` unreliable flag) for
small cells. The existing 2016 build documents `u` flags for
several drgn1 groups (implementation report §3 O2 and §5: drgn1
groups 2, 4, 5, 6, 7, and 8 carry `u` flags on some cells, and
drgn1=8 Méditerranée carries `u_u` flags reflecting both an
unreliable UR source and an unreliable denominator). The 2014 and
2015 extracts may carry different reliability-flag patterns; the
extension must record the year-specific flag patterns in the
`denom_flag` and `gsur_unreliable` columns and in the validation
report, rather than assuming the 2016 flag pattern carries over.

---

## 8. Whether existing GSURv2 2016 code can be parameterized

**Yes. The existing GSURv2 2016 construction script can be
parameterised by opportunity year rather than rewritten, subject
to a small number of changes specified in §9.**

The existing construction script
(`scripts/enhanced/enh_prepare_FR_gsur_v2.py`, implementation
report header) produced the 2016 GSURv2 lookup by a methodology
that is year-invariant in its logic and year-specific only in its
inputs. The aggregation logic (population-weighted mean of NUTS-2
unemployment rates within each drgn1 group), the crosswalk
consumption (the drgn1-to-NUTS-2 mapping applied at lookup-
construction time), the schema (the eleven-column output), the
education alignment (educ3 ∈ {0,1,2} to ISCED ED0-2 / ED3_4 /
ED5-8), the age-band handling (Y20-64 broad-age for Stage A), and
the drgn1=9 stub treatment are all independent of the opportunity
year. Only three input families are year-specific: the Eurostat
unemployment rates, the Eurostat population denominators, and the
INSEE national benchmark.

The script is therefore a natural candidate for parameterisation
by opportunity year. The parameterisation adds an opportunity-year
argument (e.g., `--opportunity-year 2014`) that selects the year-
specific input files and writes the year-tagged output, while
leaving the year-invariant logic unchanged. The parameterised
script can then be invoked three times (once per opportunity year)
to produce the three lookups, or twice (for 2014 and 2015) if the
existing 2016 lookup is reused under the provenance lock specified
in §15.

The parameterisation is preferable to a rewrite for three reasons.
First, it preserves the verified construction logic that produced
the accepted 2016 lookup; a rewrite would reintroduce the risk of
divergence from the validated methodology. Second, it ensures that
the three opportunity-year lookups are produced by identical logic,
which is the property required for internal consistency of the
pooled opportunity-side variable (§2). Third, it isolates the
year-specific inputs in the script's argument interface, which is
the package-hygiene pattern (the construction logic is year-
agnostic; the year-specific values are passed as arguments),
consistent with the multi-year strategy memo's hygiene rules.

The parameterisation is the recommended approach. The required
changes are specified in §9.

---

## 9. Required changes to enh_prepare_FR_gsur_v2.py

The parameterisation of the existing construction script requires
the following changes. Each change isolates a year-specific input
or output behind a configurable argument while preserving the
year-invariant construction logic.

*Change C1 — Opportunity-year argument.* Add a required command-
line argument `--opportunity-year` (integer) that specifies the
opportunity year for the construction run. The argument value
populates the `year` column of the output lookup and selects the
year-specific input files (Changes C2 through C4). The existing
hard-coded reference to year 2016 (implementation report §4: the
`year` column carries 2016) is replaced by the argument value.

*Change C2 — Year-specific unemployment-rate input.* Replace the
hard-coded reference to `Data/external/FR_gsur.xlsx` (the 2016
unemployment-rate workbook) with a year-parameterised input path.
The script must accept the year-specific unemployment-rate extract
(the `lfst_r_lfu3rt` data for the specified opportunity year). If
the 2014 and 2015 extracts are delivered as separate workbooks
(e.g., `FR_gsur_2014.xlsx`, `FR_gsur_2015.xlsx`) or as additional
sheets within a single workbook, the script's input-resolution
logic must select the correct year's data. The recommended pattern
is a year-keyed input-path template read from a configuration
mapping, so that the input path is `{external_dir}/FR_gsur_{year}.
xlsx` or equivalent.

*Change C3 — Year-specific population-denominator input.* Replace
the hard-coded reference to `Data/external/lfst_r_lfsd2pop_FR_2016.
tsv` with a year-parameterised path
`Data/external/lfst_r_lfsd2pop_FR_{year}.tsv`. The D2 population
denominators are year-specific; the 2014 and 2015 files must be
acquired (§7) and the script must select the file matching the
opportunity year.

*Change C4 — Year-specific national-benchmark input.* Replace the
hard-coded reference to `Data/external/insee_001688526_2016.csv`
with a year-parameterised path
`Data/external/insee_001688526_{year}.csv`. The INSEE national
benchmark is year-specific (the 2016 value is 9.725 per cent per
implementation report §2); the 2014 and 2015 benchmark values must
be acquired and the script must select the value matching the
opportunity year for the L5 validation check (§12).

*Change C5 — Year-tagged output path.* Replace the hard-coded
output path `Data/external/FR_gsur_ruro_v2_stageA.parquet` with a
year-tagged path `Data/external/FR_gsur_ruro_v2_stageA_y{year}.
parquet` for the new years. The existing 2016 lookup may either
remain at its current un-tagged path (with the provenance lock of
§15) or be renamed to `_y2016.parquet` for naming consistency
across the three years; the renaming decision is recorded in §15.

*Change C6 — Year-invariant logic preserved.* The crosswalk
consumption (the drgn1-to-NUTS-2 mapping; §10), the population-
weighted aggregation (§11), the education alignment (educ3 to
ISCED), the age-band handling (Y20-64 broad-age), the drgn1=9 stub
treatment, and the eleven-column output schema must remain
byte-unchanged from the existing 2016 build. No change to the
construction logic is authorised by this parameterisation; the
parameterisation changes only the year-specific input selection
and the output tagging.

*Change C7 — Year recorded in provenance.* The script must record
the opportunity year, the input file paths used, and the
construction timestamp in the output sidecar (§14), so that each
year-specific lookup carries an auditable record of which year-
specific inputs produced it.

The seven changes are confined to the input-selection and output-
tagging layers of the script. The construction logic — the load-
bearing methodology that produced the validated 2016 lookup — is
preserved unchanged.

---

## 10. Required crosswalk logic

The crosswalk logic is year-invariant and is reused without
modification across all three opportunity years.

The crosswalk maps each of the 22 metropolitan-France pre-2016
NUTS-2 codes to the post-2016 NUTS-2 codes, verified against the
Eurostat `NUTS2013-NUTS2016.xlsx` correspondence reference, and
thence to the EUROMOD `drgn1` regional coding via the DRD-
documented derivation (rebuild specification §3). The crosswalk is
materialised in `fr_drgn1_to_nuts2_crosswalk.csv` (22 rows, all
carrying `verified_against_eurostat = YES`; implementation report
§3 O1), and the drgn1 compositions are fixed: drgn1=1 comprises
one NUTS-2 component (FR10, Île-de-France); drgn1=2 comprises six
components; drgn1=4, 5, 6, 8 comprise three components each;
drgn1=7 comprises two components; drgn1=3 comprises one component
(FRE1, Nord-Pas-de-Calais); drgn1=9 is the DOM stub with zero
components.

The crosswalk's year-invariance follows from its construction. The
mapping from the EUROMOD `drgn1` coding to the pre-2016 NUTS-2
codes is a function of the EUROMOD regional definition (rebuild
specification §3 Table), which does not change across opportunity
years. The mapping from the pre-2016 NUTS-2 codes to the post-2016
NUTS-2 codes is a function of the 2016 NUTS reform correspondence
(the `NUTS2013-NUTS2016.xlsx` reference), which is a fixed
historical correspondence independent of the year of the
unemployment-rate data. The crosswalk therefore applies
identically to the 2014, 2015, and 2016 unemployment-rate data:
the same NUTS-2 components contribute to each drgn1 group
regardless of the opportunity year.

One consistency requirement attaches to the crosswalk reuse. The
2014 and 2015 Eurostat unemployment-rate extracts must report
rates at the same post-2016 NUTS-2 vintage as the 2016 extract
(the post-2016 codes FR10, FRB0, FRC1, etc.). Eurostat regional
data published after the 2016 reform reports historical years at
the post-2016 vintage (the 2016 NUTS classification is applied
retrospectively to earlier years in the current data warehouse
release), so the 2014 and 2015 extracts retrieved from the current
warehouse are expected to use the post-2016 codes and to be
crosswalk-compatible. The extension must verify this at retrieval
time: if the 2014 or 2015 extract uses a different NUTS vintage,
the crosswalk would not apply directly and a vintage-correction
step would be required. The validation check L-vintage (§13)
confirms NUTS-vintage compatibility before the crosswalk is
applied.

The crosswalk logic is reused unchanged, subject to the NUTS-
vintage compatibility verification.

---

## 11. Required denominator logic

The denominator logic is year-invariant in method and year-
specific in data, and is reused without methodological
modification across all three opportunity years.

The denominator method is the D2 population denominator (rebuild
specification §5(D2); implementation report §3 O2): for each
(drgn1, educ3, sex) cell, the GSUR rate is the population-weighted
mean of the contributing NUTS-2 unemployment rates, with the
weights given by the D2 population-in-private-households
denominators from the Eurostat `lfst_r_lfsd2pop` series. The
aggregation formula is

$$\mathrm{gsur}(d, e, s) = \frac{\sum_{n \in N(d)} \mathrm{ur}(n, e, s) \cdot \mathrm{pop}(n, e, s)}{\sum_{n \in N(d)} \mathrm{pop}(n, e, s)},$$

where $d$ indexes the drgn1 group, $e$ the education group, $s$
the sex, and $N(d)$ the set of post-2016 NUTS-2 components of the
drgn1 group $d$ (rebuild specification §5; implementation report
§3 O2).

The method is year-invariant: the D2 population-weighting
aggregation applies identically to each opportunity year. The data
is year-specific: the population denominators $\mathrm{pop}(n, e,
s)$ are drawn from the year-specific `lfst_r_lfsd2pop` file (§7,
Change C3). The 2014 and 2015 population denominators differ from
the 2016 denominators (population composition shifts modestly
across years), so the year-specific denominator files must be used
for the year-specific aggregations.

Two denominator caveats from the existing 2016 build must be
re-examined for each new year. First, the D1 labour-force
denominator (`lfst_r_lfp2acedu`) does not publish the Y20-64 age
band for any EU country (implementation report §3 O2), so the D2
population denominator is the operational denominator for all
years; this constraint is year-invariant and the D2 denominator is
used for 2014 and 2015 as for 2016. Second, the existing 2016
build documents D2 fallback cells flagged `u` (unreliable) for
FRM0 (Corse) and FRI2 (Limousin) at Y20-64 (implementation report
§3 O2). The 2014 and 2015 denominator files may carry different
unreliability patterns; the extension must record the year-
specific `denom_flag` values rather than assuming the 2016 pattern
carries over, and must flag any year-specific cells where the
denominator is suppressed or unreliable.

The denominator logic is reused unchanged in method, with year-
specific denominator data and year-specific reliability flagging.

---

## 12. Required benchmark logic

The benchmark logic is year-invariant in method and year-specific
in the benchmark value, and is reused without methodological
modification across all three opportunity years.

The benchmark method is the L5 national-benchmark validation check
(rebuild specification §11(E4) and §13 L5; implementation report
§2 O9): the population-weighted national GSUR implied by the
constructed lookup is compared against the INSEE BDM 001688526
national unemployment-rate benchmark for the opportunity year, and
the validation report cites the benchmark used. The rebuild
specification §13 (cleanup edit 2) requires that the validation
report cite the benchmark rather than hard-coding a national rate;
the year-parameterisation honours this by selecting the year-
specific benchmark value (§9, Change C4).

The benchmark value is year-specific: the 2016 benchmark is 9.725
per cent (implementation report §2); the 2014 and 2015 benchmark
values are the corresponding INSEE BDM 001688526 annual averages,
which must be acquired (§7) and which differ from the 2016 value
(the French national unemployment rate rose from 2014 to 2015 and
declined slightly toward 2016). The L5 check for each opportunity
year compares the constructed national GSUR against that year's
benchmark; the check is documented per year with the year-specific
benchmark cited.

The benchmark logic is reused unchanged in method, with the year-
specific benchmark value selected per opportunity year and cited
in each year's validation report. The L5 check is a validation
diagnostic, not a construction input: the benchmark does not enter
the lookup construction (the lookup is built from the cell-level
unemployment rates and population denominators), but is used to
verify that the constructed national aggregate is consistent with
the independent national rate.

---

## 13. Required validation checks

Each new opportunity-year lookup must pass the lookup-validation
battery specified in the rebuild specification §13, applied per
year. The validation checks are inherited from the existing 2016
build and are re-run against each new year's lookup. Table 6
specifies the required checks.

| Check | Description | Per-year requirement |
|---|---|---|
| L-vintage | NUTS-vintage compatibility (new — §10) | The year-specific unemployment-rate extract uses the post-2016 NUTS-2 vintage compatible with the crosswalk. |
| L1 | Schema integrity | The lookup carries the eleven-column schema; 54 rows (48 active + 6 stubs). |
| L4 | Île-de-France parity | drgn1=1 (single-component FR10) matches the FR10 source values exactly (tolerance 0.001 per O8). |
| L5 | National-benchmark consistency | The population-weighted national GSUR is consistent with the year-specific INSEE BDM 001688526 benchmark; the benchmark is cited. |
| L-coverage | Cell coverage | All 48 active (drgn1, educ3, sex) cells carry a non-null GSUR; the 6 drgn1=9 stubs carry NaN. |
| L-flag | Reliability flagging | The `denom_flag` and `gsur_unreliable` columns correctly record the year-specific Eurostat reliability flags. |
| L-range | Rate plausibility | All GSUR values fall in the plausible proportion range [0, 1]; the diagnostic age-profile and education-gradient sanity checks are recorded as diagnostic flags, not pass/fail rules (rebuild specification cleanup edit 3). |

The L4 Île-de-France parity check is the load-bearing correctness
check: because drgn1=1 is a single-component group (FR10), the
constructed GSUR for drgn1=1 must match the FR10 source
unemployment rates exactly (the population-weighted mean of a
single component is that component's value). The existing 2016
build confirms L4 parity at diff = 0.000000 for all six educ3 ×
sex cells (implementation report §6). Each new year's lookup must
confirm the same parity against that year's FR10 source values.

The L5 national-benchmark check is the consistency diagnostic:
the constructed national aggregate must be consistent with the
independent INSEE national rate for the year. The check is
documented per year with the year-specific benchmark cited
(rebuild specification §13 cleanup edit 2).

The validation checks are run per opportunity year and recorded in
a per-year validation report. A new opportunity-year lookup is
accepted only if it passes the validation battery; a lookup that
fails L4 (Île-de-France parity) or L-vintage (NUTS-vintage
compatibility) is rejected and the construction is diagnosed before
re-running.

The lookup validation is distinct from the MNL-rebuild validation
(rebuild specification §14, checks M1 through M10), which applies
at the downstream MNL-merge step and is out of scope for this
memo. The extension produces and validates the lookups; the MNL
merge and its validation are separately gated.

---

## 14. Required sidecar metadata

Each new opportunity-year lookup must carry a metadata sidecar
recording its provenance, inputs, and validation results, so that
each year-specific lookup is independently auditable. The sidecar
schema extends the provenance pattern of the existing 2016 build.

The required sidecar fields are:

`opportunity_year` — the opportunity year (2014 or 2015).

`gsur_source` — the construction methodology, set to `"GSURv2"`
(distinguishing the lookup from the v1 fallback).

`construction_script` — the script and version that produced the
lookup (`enh_prepare_FR_gsur_v2.py` with the parameterisation of
§9).

`input_unemployment_rate_file` — the path and Eurostat dataset
identifier of the year-specific unemployment-rate extract.

`input_population_denominator_file` — the path of the year-specific
`lfst_r_lfsd2pop` file.

`input_national_benchmark_file` — the path of the year-specific
INSEE BDM 001688526 file and the benchmark value.

`crosswalk_file` — the path of the crosswalk
(`fr_drgn1_to_nuts2_crosswalk.csv`) and its verification status
(`verified_against_eurostat = YES`).

`nuts_vintage` — the NUTS vintage of the unemployment-rate extract
(expected post-2016) and the L-vintage check result.

`denominator_type` — `"D2_population"` (the operational denominator).

`age_band` — `"Y20-64"` (the broad-age Stage A band).

`reliability_flags` — the year-specific `denom_flag` and
`gsur_unreliable` summary (which drgn1 groups carry `u` or `u_u`
flags).

`validation_results` — the per-year L-check results (L-vintage,
L1, L4, L5, L-coverage, L-flag, L-range), including the L4 Île-de-
France parity difference and the L5 benchmark comparison.

`construction_timestamp` — the construction run timestamp.

The sidecar makes each year-specific lookup independently
auditable, so that a future reader can verify which year-specific
inputs produced each lookup and whether the lookup passed
validation. The sidecar pattern is the data-product-provenance
discipline that the year-alignment decision §6 requires (the
FR_2016 sidecar correction noted there is an instance of the same
discipline applied to the MNL parquet).

---

## 15. Treatment of existing 2016 GSURv2

The existing 2016 GSURv2 lookup (`FR_gsur_ruro_v2_stageA.parquet`)
may be reused for the opportunity-year-2016 requirement (the
FR_2017 survey year) only if its provenance and sidecar
documentation are locked cleanly. The required decision, per the
task, is that the existing 2016 GSURv2 may be reused only if
provenance and sidecar documentation are locked cleanly; this memo
specifies what "locked cleanly" requires.

The existing 2016 lookup was built by the Stage A construction
(implementation report) and carries the eleven-column schema with
54 rows. Its provenance is documented in the implementation
report: the inputs (the 2016 unemployment-rate workbook, the 2016
D2 population denominators, the 2016 INSEE benchmark of 9.725 per
cent, the crosswalk), the methodology (population-weighted
aggregation, Y20-64 broad-age, educ3-to-ISCED alignment), and the
validation (L4 Île-de-France parity at diff = 0.000000). The
existing lookup is therefore well-documented in the implementation
report, but its parquet-level sidecar may not carry the full
provenance metadata specified in §14.

Three provenance-lock requirements attach to the reuse of the
existing 2016 lookup.

*Lock requirement K1 — Sidecar parity.* The existing 2016 lookup
must carry a sidecar matching the §14 schema, with
`opportunity_year = 2016`, the input file references, the
crosswalk verification, the denominator type, the reliability
flags (the documented `u` and `u_u` flags for drgn1 groups 2, 4,
5, 6, 7, 8), and the validation results (L4 parity at diff =
0.000000). If the existing lookup's sidecar does not carry these
fields, a sidecar must be written (a documentation step, not a
rebuild) to bring the existing lookup to provenance parity with
the new 2014 and 2015 lookups.

*Lock requirement K2 — Naming consistency.* For naming consistency
across the three opportunity-year lookups, the existing 2016
lookup should either be referenced under its current un-tagged
path (`FR_gsur_ruro_v2_stageA.parquet`) with an explicit note that
it is the opportunity-year-2016 lookup, or be renamed to
`FR_gsur_ruro_v2_stageA_y2016.parquet` to match the year-tagged
naming of the new lookups (§6). The renaming is the cleaner option
for the multi-year construction (it makes the opportunity-year
keying explicit in every lookup filename) but requires updating any
existing reference to the un-tagged path (notably the single-year
M1-clean MNL merge, which uses the 2016 lookup). The renaming
decision is recorded at implementation time; if the existing
un-tagged path is retained, the construction must document
explicitly that the un-tagged lookup is the opportunity-year-2016
lookup.

*Lock requirement K3 — Provenance discrepancy resolution.* The
year-alignment decision §2 notes that the FR_2016 MNL parquet's
sidecar "cites wrong source file" and §6 requires the FR_2016
sidecar correction as a documentation fix. This sidecar
discrepancy is at the MNL-parquet level, not the lookup level, but
the lookup-level provenance must be confirmed consistent: the
existing 2016 lookup's documented provenance (the implementation
report) must be the authoritative record, and any conflicting
sidecar reference must be corrected to match. The provenance-lock
step confirms that the existing 2016 lookup's provenance is
unambiguous and consistent across the implementation report, the
lookup sidecar, and any downstream reference.

If all three lock requirements are satisfied, the existing 2016
GSURv2 lookup is reused for the opportunity-year-2016 requirement
without rebuild. If any lock requirement cannot be satisfied — for
instance, if the existing lookup's provenance cannot be confirmed
consistent — the existing 2016 lookup must be rebuilt under the
parameterised script (§9) with `--opportunity-year 2016`,
producing a fresh lookup with clean provenance. The rebuild option
is the fallback; the reuse option (under the provenance lock) is
preferred because it avoids re-running a validated construction.

---

## 16. Interaction with P3a construction

The GSURv2 extension interacts with the existing P3a provisional
construction at the opportunity-side input layer. The extension
does not modify the P3a stacking, harmonisation, identity-
validation, or cluster-key logic; it replaces the opportunity-side
GSUR input on which a future final P3a construction would draw.

The current P3a construction uses the v1-fallback MNL parquets
(`fr_2015_RURO_mnl_v1gsurY2014`, `fr_2016_RURO_mnl_v1gsurY2015`,
`fr_2017_RURO_mnl_v1gsurY2016`; execution report §5). These
parquets merge the v1-fallback GSUR rates keyed to the correct
opportunity years. When the GSURv2 extension is complete, the
FR_2015 and FR_2016 MNL parquets would be rebuilt to merge the
GSURv2 opportunity-year-2014 and opportunity-year-2015 rates
respectively, and the FR_2017 MNL parquet would merge the existing
(or rebuilt) GSURv2 opportunity-year-2016 rates. A final P3a
construction would then stack these GSURv2-based MNL parquets,
producing a final pooled dataset with the opportunity-side
variable constructed by a single consistent GSURv2 methodology
across all three survey years.

The interaction is sequenced as follows. First, the GSURv2
extension produces the opportunity-year-2014 and opportunity-year-
2015 lookups (the construction this memo specifies). Second, a
downstream MNL-merge step (separately gated, out of scope for this
memo) rebuilds the FR_2015 and FR_2016 MNL parquets to merge the
GSURv2 rates, producing GSURv2-based MNL parquets named to encode
the GSURv2 source and the opportunity year (e.g.,
`fr_2015_RURO_mnl_GSURv2_y2014`). Third, a final P3a construction
(also separately gated) re-runs the Stage M1 pipeline against the
GSURv2-based MNL parquets, producing a final pooled dataset whose
provisioning label drops the `v1_fallback` qualifier.

The current provisional P3a output
(`fr_p3a_harmonised.parquet`, label
`provisional_v1_fallback_opportunity_year_aligned`) is not
modified or invalidated by the GSURv2 extension. It remains the
provisional pooled dataset, fit for pipeline-diagnostics and
provisional-estimation use per the construction verdict §1, until
the final GSURv2-based P3a construction supersedes it. The
extension prepares the inputs for the eventual final construction;
it does not itself produce the final pooled dataset.

The P3a construction's pipeline logic is confirmed reusable for
the final construction: the addendum §8 establishes that the
stacking logic is country- and year-agnostic, and the harmonisation
and cluster-key logic operate on whichever MNL parquets are
configured. The final P3a construction would re-run the same
pipeline against the GSURv2-based MNL parquets, with no change to
the stacking, harmonisation, identity-validation, or cluster-key
logic.

---

## 17. What remains provisional until GSURv2 extension is complete

Until the GSURv2 extension is complete and the GSURv2-based MNL
parquets are constructed, the following remain provisional or
unavailable.

*The P3a pooled dataset remains provisional.* The current
`fr_p3a_harmonised.parquet` carries the
`provisional_v1_fallback_opportunity_year_aligned` label and
remains fit for pipeline-diagnostics and provisional-estimation
use only (construction verdict §1). No parameter estimate,
elasticity, or other numerical result derived from the provisional
P3a dataset may be reported as final (year-alignment decision §5;
construction verdict §1).

*Final pooled estimation is unavailable.* The year-alignment
decision §6 establishes that no pooled result may be labelled
final until GSURv2 opportunity-year-aligned parquets exist for all
three survey years. Until the extension is complete, the only
pooled estimation available is a provisional v1-fallback dry-run,
whose outputs are strictly segregated dry-run diagnostics
(year-alignment decision §5; construction verdict §21).

*The opportunity-side variable is methodologically inconsistent
across the pooled sample.* The current provisional P3a dataset
uses v1-fallback GSUR rates for all three survey years; these rates
are not education-stratified and rest on the withdrawn v1
crosswalk (§2). The single-year M1-clean baseline uses GSURv2
rates for its 2016 survey year. A final pooled estimation requires
the opportunity-side variable to be GSURv2-constructed across all
three survey years, which the extension provides; until then, the
pooled and single-year opportunity-side variables are constructed
by different methodologies.

*The GSURv2-based MNL parquets do not exist for FR_2015 and
FR_2016.* The downstream MNL-merge step (§16) cannot proceed until
the opportunity-year-2014 and opportunity-year-2015 lookups exist.
The GSURv2-based MNL parquets, and consequently the final P3a
construction, are blocked behind the extension.

What does not remain provisional, and is unaffected by the
extension, is the single-year M1-clean baseline. The M1-clean 2016
baseline is estimated against the GSURv2 opportunity-year-2016
lookup and is the accepted active JMP baseline (construction
verdict §20). The extension does not modify the M1-clean baseline,
its GSURv2 2016 lookup (subject to the provenance lock of §15), or
its accepted status.

---

## 18. Whether pooled estimation may proceed before GSURv2 extension

**No final pooled estimation may proceed before the GSURv2
extension is complete. A provisional v1-fallback pooled estimation
dry-run would require a separate explicit authorisation and is not
authorised by this memo.**

The distinction is between final pooled estimation (blocked) and
provisional pooled estimation dry-run (separately gated,
unauthorised here, and non-reportable unless explicitly authorised
as a segregated diagnostic).

*Final pooled estimation is blocked.* The year-alignment decision
§6 establishes categorically that final pooled estimation requires
GSURv2 rebuilt for each opportunity year before any year's parquet
is promoted to final status. The GSURv2 extension is the
prerequisite; until it is complete, no final pooled result is
available. This memo does not alter the requirement and does not
authorise any pooled estimation.

*Provisional pooled estimation dry-run is separately gated and not
authorised here.* The year-alignment decision §5 permits the P3a
data product to be used for a provisional Stage M1 diagnostic under
the v1 fallback, subject to explicit labelling, and the construction
verdict §21 records that path as a possible parallel diagnostic
activity. However, estimating any pooled model, even as a dry-run,
requires a cluster-robust SE wrapper, a pooled estimation
specification, and its own authorisation memo (construction verdict
§17). This GSURv2 design memo does not authorise that dry-run; it
notes only that a separately authorised dry-run path could exist
apart from the GSURv2 extension.

The required decision stated in the task is confirmed: final
pooled estimation should not be authorised until GSURv2 exists and
is documented for all required opportunity years, unless a separate
verdict explicitly accepts the v1 fallback. This memo does not
provide such a verdict and does not authorise pooled estimation in
any form. The GSURv2 extension is the empirical gate that, once
cleared, enables final pooled estimation to be considered under a
subsequent authorisation.

The recommended sequencing is that the GSURv2 extension proceeds as
the next empirical gate, and that the cluster-robust SE wrapper and
the pooled specification are built after the extension clears, so
that the estimation infrastructure is exercised against the final
GSURv2-based data product rather than against the provisional
v1-fallback data. A provisional dry-run could be requested as a
separate diagnostic authorization if the estimation mechanics must
be validated before the extension completes, but it is not the
recommended critical-path activity and is not authorised by this
memo.

---

## 19. Implementation audit task

Before the GSURv2 extension construction is executed, an
implementation audit must confirm the readiness of the inputs and
the parameterisation. The audit is a verification step, not an
execution step, and is the analogue for the extension of the
feasibility audit specified in the multi-year strategy memo.

The audit covers six conditions.

*Condition A1 — Eurostat unemployment-rate availability.* The
audit confirms that the `lfst_r_lfu3rt` unemployment-rate extracts
for opportunity years 2014 and 2015 are retrievable at the NUTS-2
× sex × ISCED × age-band granularity matching the 2016 extract,
and records the dataset identifiers and retrieval parameters.

*Condition A2 — Eurostat population-denominator availability.* The
audit confirms that the `lfst_r_lfsd2pop` population-denominator
files for 2014 and 2015 are retrievable, and records the file
paths.

*Condition A3 — INSEE benchmark availability.* The audit confirms
that the INSEE BDM 001688526 national-benchmark values for 2014
and 2015 are retrievable, and records the annual-average values.

*Condition A4 — NUTS-vintage compatibility.* The audit confirms
that the 2014 and 2015 unemployment-rate extracts use the post-
2016 NUTS-2 vintage compatible with the crosswalk (the L-vintage
check, §10 and §13). If either extract uses a different vintage,
the audit identifies the vintage-correction requirement.

*Condition A5 — Existing 2016 provenance lock.* The audit confirms
whether the existing 2016 GSURv2 lookup satisfies the three
provenance-lock requirements (§15 K1, K2, K3) for reuse, or whether
a rebuild under the parameterised script is required.

*Condition A6 — Script parameterisation readiness.* The audit
confirms that the construction script
(`enh_prepare_FR_gsur_v2.py`) can accommodate the seven
parameterisation changes (§9 C1 through C7) without modification to
the year-invariant construction logic, and identifies any
hard-coded year reference not covered by the seven changes.

The audit produces a readiness report
(`Results/JMP_GSURv2_multi_year_extension_audit_v1.md` or
equivalent) that records the status of each condition and, if any
condition fails, identifies the operational response. If all six
conditions pass, the audit may recommend that a separate GSURv2
construction authorisation prompt be issued. The audit does not
authorise construction by itself. The audit is the immediate next
operational step for the extension; the construction itself is
sequenced after the audit confirms readiness and after a separate
construction authorisation is issued.

The audit does not run the GSURv2 construction, does not estimate
pooled models, does not compute welfare, and does not authorise
pooled estimation or welfare work. It is a readiness-verification
step that precedes the construction.

---

## 20. Exact next Claude Code prompt

The following prompt initiates the implementation-audit task (§19)
in Claude Code Sonnet. The prompt is the audit prompt, not the
construction prompt: the construction prompt is written after the
audit confirms readiness. The audit prompt does not authorise
construction, estimation, or welfare work.

Tool path: Claude Code Sonnet (local codebase and external-data
inspection).

Files to place in the workspace or confirm present: the existing
2016 GSURv2 lookup (`Data/external/FR_gsur_ruro_v2_stageA.parquet`)
and its provenance documentation
(`docs/RURO_GSUR_v2_stageA_implementation_report_v1.md`); the
crosswalk (`Data/external/fr_drgn1_to_nuts2_crosswalk.csv`); the
construction script
(`scripts/enhanced/enh_prepare_FR_gsur_v2.py`); the rebuild
specification (`docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md`); the
year-alignment decision
(`docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md`); and this design
memo.

Prompt to use:

> Audit the readiness of the GSURv2 multi-year extension to
> opportunity years 2014 and 2015, per
> `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_design_memo_v1.md` §19.
> Do not run the GSURv2 construction. Do not write any GSURv2
> lookup. Do not estimate any model. Do not compute welfare.
> Produce a readiness report only.
>
> Specifically:
>
> 1. Confirm whether the Eurostat `lfst_r_lfu3rt` unemployment-rate
>    extracts for opportunity years 2014 and 2015 are available in
>    `Data/external/` (or document what must be retrieved), at the
>    NUTS-2 × sex × ISCED × age-band granularity matching the 2016
>    extract used in `FR_gsur.xlsx`. Record dataset identifiers.
>
> 2. Confirm whether the Eurostat `lfst_r_lfsd2pop` population-
>    denominator files for 2014 and 2015 are available (or document
>    what must be retrieved). Record file paths.
>
> 3. Confirm whether the INSEE BDM 001688526 national-benchmark
>    values for 2014 and 2015 are available (or document what must
>    be retrieved). Record the annual-average values.
>
> 4. For any 2014 or 2015 unemployment-rate extract already
>    present, confirm whether it uses the post-2016 NUTS-2 vintage
>    compatible with `fr_drgn1_to_nuts2_crosswalk.csv` (the
>    L-vintage check). Flag any vintage mismatch.
>
> 5. Inspect the existing 2016 GSURv2 lookup
>    (`Data/external/FR_gsur_ruro_v2_stageA.parquet`) and its
>    sidecar (if any). Report whether it satisfies the three
>    provenance-lock requirements in the design memo §15 (K1
>    sidecar parity, K2 naming consistency, K3 provenance-
>    discrepancy resolution), or whether a rebuild under the
>    parameterised script is required.
>
> 6. Inspect `scripts/enhanced/enh_prepare_FR_gsur_v2.py` and
>    report whether it can accommodate the seven parameterisation
>    changes in the design memo §9 (C1 opportunity-year argument,
>    C2 year-specific UR input, C3 year-specific denominator input,
>    C4 year-specific benchmark input, C5 year-tagged output, C6
>    year-invariant logic preserved, C7 year recorded in
>    provenance) without modifying the year-invariant construction
>    logic. Identify any hard-coded year reference not covered by
>    these seven changes.
>
> Save the readiness report as
> `Results/JMP_GSURv2_multi_year_extension_audit_v1.md`. Do not
> modify any data file, any script, or any canonical path. Do not
> proceed to construction; the construction prompt is written
> separately after this audit.

Output to save: the readiness report at
`Results/JMP_GSURv2_multi_year_extension_audit_v1.md`.

What to do next: return the readiness report to this chat for a
construction-authorisation decision. If all six conditions pass,
the next step is the GSURv2 construction prompt (which this memo
does not provide; it is written after the audit). If any condition
fails — particularly A1 (unemployment-rate availability), A4
(NUTS-vintage compatibility), or A5 (provenance lock) — the
readiness report identifies the operational response, and the
construction is deferred until the failing condition is resolved.

The audit prompt is the extension's immediate next operational
step. It does not authorise GSURv2 construction, pooled estimation,
welfare implementation, or welfare computation; it verifies
readiness so that the subsequent construction prompt can proceed
against confirmed inputs.
