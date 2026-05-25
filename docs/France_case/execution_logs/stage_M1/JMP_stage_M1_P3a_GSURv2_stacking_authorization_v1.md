# JMP Stage M1 P3a GSURv2 Pooled Stacking Re-Run — Authorization v1

Date: 2026-05-20

Specification class: stacking re-run authorization memo. The memo
authorises the Stage M1 P3a GSURv2 pooled stacking re-run — the
re-execution of the Stage M1 pooled stacking pipeline against the
GSURv2-based MNL parquets, replacing the v1-fallback inputs and
producing a final (non-provisional) GSURv2 opportunity-year-aligned
pooled dataset. It is an authorization document for the stacking
re-run only; it does not authorise pooled estimation, welfare
computation, P3b, P4, or canonical promotion.

Reference documents:
- `docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md` (the post-rebuild
  verdict authorising this stacking re-run as the next gate, with
  correction `docs/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md`)
- `Results/JMP_GSURv2_MNL_rebuild_report_v2.md` (the rebuild
  report)
- `Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md` (the
  authorized-stem correction report)
- `docs/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md`
  (the provisional v1-fallback P3a construction verdict, whose
  pipeline and validation battery this re-run reproduces)
- `config/multi_year/fr_p3a_stage_m1.yaml` (the existing Stage M1
  P3a config, to be superseded or patched per §10)

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

Scope of memo: the memo authorises the Stage M1 P3a GSURv2 pooled
stacking re-run, specifying the GSURv2 input stems (§5), the output
stems (§6), the new provisioning label (§7), the sidecar metadata
(§8), the V1–V9 validation battery (§9), the config handling that
enforces exact GSURv2 input resolution (§10), the halt conditions
(§13), and the execution report (§14). The memo does not authorise
pooled estimation, welfare computation, P3b, P4, canonical
promotion, or the displacement of M1-clean; those steps are
separately gated.

---

## 1. Purpose

The purpose of this memo is to authorise the Stage M1 P3a GSURv2
pooled stacking re-run: the re-execution of the five-step Stage M1
pooled stacking pipeline (year stacking with stacked-identifier
engineering, cross-year identity validation, CPI/HICP
harmonisation, cluster-key annotation, and the V1–V9 validation
battery) against the six GSURv2-based MNL parquets, producing a
final (non-provisional) GSURv2 opportunity-year-aligned pooled
dataset.

The re-run is authorised because the GSURv2 MNL-parquet rebuild
PASSED and produced valid GSURv2-final inputs. The post-rebuild
verdict classified the rebuild PASS (with a minor documentation
caveat that does not affect the data), confirmed that the rebuilt
parquets are valid GSURv2-final inputs for P3a stacking, and
authorised the Stage M1 P3a GSURv2 stacking re-run as the next
gate. This memo is the stacking re-run authorization the post-
rebuild verdict named.

The re-run reproduces the Stage M1 pipeline that produced the
provisional v1-fallback P3a dataset, with one change of substance
(the inputs are the GSURv2-based MNL parquets, not the v1-fallback
parquets) and one change of label (the provisioning label is
`gsurv2_opportunity_year_aligned`, not
`provisional_v1_fallback_opportunity_year_aligned`). The pipeline,
the stacked-identifier engineering, the CPI factors, the cluster-
key method, and the V1–V9 validation battery are carried forward
unchanged from the provisional build; only the opportunity-side
input and the label change.

The memo's central control is the enforcement of exact GSURv2
input resolution (§5, §10): the re-run must consume only the six
GSURv2-based MNL parquets and must not, through a broad input glob
or a stale config, accidentally select the older v1-fallback or any
other MNL parquet. The memo's operational deliverable is the exact
Claude Code task (§15).

The re-run produces the final pooled dataset. It does not estimate
any model or compute any welfare from it; those steps are
separately gated (§12). The single-year M1-clean 2016 specification
remains the active JMP baseline throughout (§12).

---

## 2. Current status

The current status of the multi-year extension is that the GSURv2
MNL-parquet rebuild is complete and verdicted PASS, the GSURv2-
based MNL parquets are confirmed valid GSURv2-final P3a inputs, and
the Stage M1 P3a GSURv2 stacking re-run is the next authorised
step.

The GSURv2 MNL-parquet rebuild PASSED. The post-rebuild verdict
classified the rebuild PASS WITH MINOR DOCUMENTATION CAVEAT, where
the caveat is a one-location report typo (the FR_2017 output stem
written `y2017` in one table) that does not affect the data — the
actual files and sidecars are correctly `GSURv2_y2016`. All twelve
rebuild validation checks (V1–V12) passed for all three survey
years, the `dgn`-to-`sex` mapping was verified empirically, and the
authorized-stem parquets are byte-identical to the validated
rebuild outputs.

The six GSURv2-based MNL parquets exist in `Data/processed/fr/`
with confirmed SHA-256 hashes (post-rebuild verdict §16, rebuild
report v2 §21): the FR_2015 pair (`889b2f8a…` singles, `d44d2292…`
couples), the FR_2016 pair (`139cd025…` singles, `61e3107b…`
couples), and the FR_2017 pair (`8fce026d…` singles, `2d8dc7ae…`
couples). The opportunity-side GSUR variable in these parquets
carries the GSURv2 opportunity-year-aligned rates, with the v1-
fallback rates preserved in the fallback columns.

The provisional P3a pooled dataset
(`fr_p3a_harmonised.parquet`, label
`provisional_v1_fallback_opportunity_year_aligned`) was constructed
from the v1-fallback MNL parquets and is fit only for pipeline
diagnostics. The stacking re-run this memo authorises replaces the
v1-fallback inputs with the GSURv2-based inputs, producing the
final (non-provisional) pooled dataset that drops the `v1_fallback`
qualifier.

The stacking re-run is the next authorised step, and this memo
authorises it.

---

## 3. Evidence from GSURv2 MNL rebuild

The stacking re-run rests on the GSURv2 MNL-rebuild evidence, which
establishes that the GSURv2-based MNL parquets are correct and
ready to be stacked.

Three pieces of rebuild evidence are load-bearing for the stacking
re-run.

First, the rebuild PASSED all twelve validation checks (post-
rebuild verdict §1; rebuild report v2 §24). The row and household
counts are unchanged from the v1-fallback inputs (V1, V2), the
non-GSUR columns are value-identical (V3), the active GSUR columns
are complete for all active records (V4), the v1-fallback values
are preserved exactly (V6), and the merged GSURv2 values match the
lookup values exactly (V10). The rebuilt parquets are therefore a
clean opportunity-side replacement of the v1-fallback inputs:
identical in every modelling variable except the opportunity-side
GSUR, which now carries the GSURv2 rates.

Second, the survey-year/opportunity-year mapping is correct
(post-rebuild verdict §8): FR_2015 was merged with the y2014
lookup, FR_2016 with y2015, FR_2017 with y2016. The opportunity-
year alignment that the year-alignment decision established is
preserved in the rebuilt parquets, so the stacking re-run inherits
the correct alignment without further action.

Third, the per-component row and household counts in the rebuilt
parquets match the provisional P3a construction's per-component
counts exactly (post-rebuild verdict §13): FR_2015 singles 166,900
rows / 1,669 households, FR_2015 couples 256,600 / 2,566; FR_2016
singles 167,600 / 1,676, couples 257,700 / 2,577; FR_2017 singles
166,200 / 1,662, couples 229,500 / 2,295. Because the counts match
the provisional build, the stacking re-run is expected to produce
the same pooled row count (1,244,500) and household-year count
(12,445) as the provisional build, with the same per-year and
per-component composition. The stacking arithmetic is therefore
fully predictable, and the V1–V9 validation has known expected
values to check against.

The rebuild evidence establishes that the GSURv2-based MNL parquets
are a clean opportunity-side replacement with correct alignment and
preserved sample structure. They are ready to be stacked.

---

## 4. Why stacking re-run is now authorized

The stacking re-run is authorised because the precondition the
provisional P3a construction verdict established — complete GSURv2
opportunity-year coverage merged into the MNL parquets — is now met,
and because the post-rebuild verdict explicitly authorised the
stacking re-run as the next gate.

The provisional P3a construction verdict classified the provisional
build PASS WITH PROVISIONAL LIMITATIONS, where the sole limitation
was that the opportunity-side GSUR was sourced from the v1 fallback
rather than from GSURv2. The verdict established that the
provisional file complies with the alignment rule on the year-
keying dimension but not on the source dimension, and that complete
GSURv2 opportunity-year coverage is the empirical gate that must be
cleared before any pooled result can be labelled final.

That gate is now cleared on both dimensions. The GSURv2 lookup
construction PASSED (the three opportunity-year lookups exist and
are validated), and the GSURv2 MNL-parquet rebuild PASSED (the
GSURv2 rates are merged into the MNL parquets, with the correct
opportunity-year alignment). The opportunity-side input is now
GSURv2 opportunity-year-aligned on both the year-keying and the
source dimensions. The provisional limitation is resolved.

The post-rebuild verdict authorised the Stage M1 P3a GSURv2 pooled
stacking re-run as the next gate, conditional on this stacking
authorization memo specifying its scope. The re-run produces the
final (non-provisional) pooled dataset by re-executing the same
Stage M1 pipeline that produced the provisional dataset, with the
GSURv2-based MNL parquets replacing the v1-fallback parquets.

The stacking re-run is therefore authorised: the GSURv2 gate is
cleared, the post-rebuild verdict named the re-run as the next gate,
and this memo specifies its scope. The re-run is a data-construction
step that produces the final pooled dataset; it does not estimate or
compute welfare (§12).

---

## 5. Required input stems

The stacking re-run must consume **only** the six GSURv2-based MNL
parquets, identified by exact stem. Table 1 specifies the input
stems and their confirmed SHA-256 hashes.

| Survey year | Input MNL stem | Singles SHA | Couples SHA |
|---|---|---|---|
| FR_2015 | `fr_2015_RURO_mnl_GSURv2_y2014__` | `889b2f8a…` | `d44d2292…` |
| FR_2016 | `fr_2016_RURO_mnl_GSURv2_y2015__` | `139cd025…` | `61e3107b…` |
| FR_2017 | `fr_2017_RURO_mnl_GSURv2_y2016__` | `8fce026d…` | `2d8dc7ae…` |

Each stem has two component parquets (`__singles.parquet`,
`__couples.parquet`), for six input parquets in total.

The input resolution is subject to three mandatory constraints.

(I1) **Exact GSURv2 stems only.** The re-run must resolve exactly
the six GSURv2-based parquets named in Table 1. No other MNL parquet
may be consumed.

(I2) **No v1-fallback inputs.** The re-run must NOT use the old
v1-fallback P3a input stems (`fr_2015_RURO_mnl_v1gsurY2014__`,
`fr_2016_RURO_mnl_v1gsurY2015__`, `fr_2017_RURO_mnl_v1gsurY2016__`).
These were the provisional build's inputs and are superseded by the
GSURv2-based inputs. The re-run must also not use the intermediate
`v2gsurY` stems (`fr_2015_RURO_mnl_v2gsurY2014__`, etc.); those are
byte-identical to the authorized `GSURv2_y` stems but are not the
authorized-stem deliverables, and the re-run must consume the
authorized `GSURv2_y` stems for provenance consistency.

(I3) **No broad input globs.** The re-run must NOT rely on a broad
input glob (for instance, `fr_2015_RURO_mnl_*__singles.parquet`)
that could accidentally select an older MNL parquet (a v1-fallback,
a v2gsurY, or any other stem). The input resolution must be tightly
scoped to the exact GSURv2 stems, either by a dedicated GSURv2
config naming the exact stems or by a config patch that restricts
the glob to resolve only the GSURv2 stems (§10). A broad glob that
matches multiple stems is a halt condition (§13 H1).

The exact-input-resolution constraint is the central control of
this re-run. The provisional build's couples-only defect originated
in an input-resolution ambiguity (an alphabetical-sort fallback
that silently selected one component); the GSURv2 re-run must not
reintroduce any input-resolution ambiguity, this time between GSURv2
and non-GSURv2 stems. The re-run must resolve the exact six GSURv2
parquets and halt if the resolution is ambiguous or matches any
non-GSURv2 stem.

---

## 6. Required output stems

The stacking re-run writes the final pooled dataset to GSURv2-
tagged output stems, distinguishing the final GSURv2 pooled dataset
from the provisional v1-fallback pooled dataset. Table 2 specifies
the output products.

| Product | Output file |
|---|---|
| Stacked-raw parquet | `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet` |
| Harmonised parquet | `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` |
| Stacked-raw sidecar | `fr_p3a_gsurv2_stacked_raw__stage_m1_meta.json` |
| Harmonised sidecar | `fr_p3a_gsurv2_harmonised__stage_m1_meta.json` |

The output stems carry the `gsurv2` qualifier, distinguishing them
from the provisional v1-fallback outputs (`fr_p3a_stacked_raw.parquet`,
`fr_p3a_harmonised.parquet`). The harmonised parquet is the
estimation-ready product; the stacked-raw parquet is the
intermediate pre-harmonisation product. Each carries a Stage M1
metadata sidecar (§8).

The output naming is subject to the no-silent-overwrite constraint
(§13 H6): the re-run must not overwrite the provisional v1-fallback
pooled outputs. The provisional outputs are preserved (or archived,
§13) before the GSURv2 outputs are written. Because the GSURv2
outputs carry the distinct `gsurv2` qualifier, they do not collide
with the provisional outputs by name; the constraint additionally
requires that any pre-existing GSURv2-tagged output (from an aborted
prior re-run) is archived or the re-run halts before overwriting it.

---

## 7. Required label

The provisioning label of the GSURv2 pooled dataset is
**`gsurv2_opportunity_year_aligned`**.

The label must no longer be
`provisional_v1_fallback_opportunity_year_aligned`. The provisional
label encoded two dimensions: the compliance dimension
(`opportunity_year_aligned`, the GSUR opportunity year equals the
EUROMOD system year) and the non-compliance dimension
(`provisional_v1_fallback`, the GSUR rates are v1-fallback rather
than GSURv2). The GSURv2 re-run resolves the non-compliance
dimension: the GSUR rates are now GSURv2, sourced from the validated
GSURv2 lookups. The label therefore drops both the `provisional` and
the `v1_fallback` qualifiers, becoming
`gsurv2_opportunity_year_aligned`.

The new label denotes a final (non-provisional) opportunity-year-
aligned pooled dataset whose opportunity-side variable is GSURv2-
sourced. The label is recorded in the provisioning-label field of
both output sidecars (§8) and in any result table or downstream
reference to the dataset. The label change is the formal mark that
the pooled dataset has crossed from the provisional regime (fit for
diagnostics only) to the final regime (fit, after its own stacking
verdict, to serve as the input to a final pooled estimation).

The label change does not by itself authorise pooled estimation
(§12). The label denotes that the dataset is GSURv2-final on the
opportunity-side dimension; the dataset's fitness for estimation is
adjudicated by a separate strict stacking construction verdict, and
the estimation itself is separately gated.

---

## 8. Required sidecar metadata

Each output product carries a Stage M1 metadata sidecar recording
the re-run provenance and the validation outcomes, paralleling the
provisional build's sidecar structure with the GSURv2 source and
the new label.

The required sidecar fields are:

`provisioning_label` — `"gsurv2_opportunity_year_aligned"` (§7).

`gsur_source` — `"GSURv2_opportunity_year_aligned"`, with the three
GSURv2 lookup files and their SHA-256 hashes recorded.

`input_scope` — the six GSURv2-based MNL parquet stems (§5) with
their SHA-256 hashes, confirming exact-input resolution.

`input_resolution_method` — the config or config-patch mechanism
that enforced exact GSURv2 stem resolution (§10), recorded
explicitly so that the input provenance is auditable.

`survey_year_opportunity_year_mapping` — FR_2015 → y2014, FR_2016 →
y2015, FR_2017 → y2016.

`row_count`, `household_year_count` — the pooled row count
(expected 1,244,500) and household-year count (expected 12,445).

`per_year_per_component_counts` — the per-year, per-component row
and household counts (Table 1 of the provisional verdict, expected
to match).

`cpi_harmonisation` — the deflation factors (φ₂₀₁₅=1.0031,
φ₂₀₁₆=1.0000, φ₂₀₁₇=0.9886; base year 2016) and the CPI source.

`cluster_key` — `cluster_id = idorighh`, with the unique-cluster
count (expected 9,657).

`stacked_id_scheme` — the stacked-identifier engineering (the
numeric int64 UID scheme, `stacked_hh_uid`, `stacked_person_uid`,
`year_tag`).

`validation_results` — the complete V1–V9 results.

`gsur_means` — the per-component GSUR means (now GSURv2, expected to
differ from the provisional v1-fallback means).

`build_timestamp`, `script_version` — the re-run timestamp and the
Stage M1 stacking script version.

The sidecar is written for both output products (the stacked-raw and
the harmonised parquets). The sidecar inspection is part of the
validation (§9): the re-run confirms each sidecar is present and
carries the required fields, with the `provisioning_label` correctly
set to `gsurv2_opportunity_year_aligned` and the `gsur_source`
correctly recording the GSURv2 lookups.

---

## 9. Required validation checks

The stacking re-run must reproduce the V1–V9 validation battery from
the provisional P3a construction, applied to the GSURv2 pooled
dataset. The battery is carried forward unchanged; the expected
values are known from the provisional build (the sample structure is
unchanged, only the opportunity-side rates differ).

(V1) **Stacked-ID uniqueness.** `stacked_person_uid` is unique at
the person-year level (12,445 person-years); each person-year
expands to exactly 100 draws; `(stacked_person_uid, draw)` is row-
unique with zero duplicates across 1,244,500 rows; `stacked_hh_uid`
is unique per household-year (12,445 groups).

(V2) **Row-count agreement.** The pooled total is 1,244,500 rows,
matching the expected count with a difference of zero, with the
per-year breakdown 423,500 (2015), 425,300 (2016), 395,700 (2017)
and the per-component composition of Table 1.

(V3) **Raw-ID completeness.** The four raw-identifier columns
(`idorighh`, `idorigperson`, `idhh`, `idperson`) are present and
non-null across all rows.

(V4) **Year-tag coverage.** The year tags {1, 2, 3} are present and
match the expected p3a tags.

(V5) **CPI deflation correctness.** The deflation formula `real =
nominal × φ_t` holds exactly (maximum error 0.0) across all rows
with non-null nominal values, with φ₂₀₁₅=1.0031, φ₂₀₁₆=1.0000,
φ₂₀₁₇=0.9886.

(V6) **Clustering-key integrity.** `cluster_id == idorighh` across
all rows, with `null_count(idorighh) = 0` and the unique-cluster
count (expected 9,657).

(V7) **Identity validation (dag-mask-aware).** The cross-year
identity validation confirms the EU-SILC rotational structure: the
2015→2016 and 2015→2017 pairs disjoint (zero repeats); the 2016→2017
pair with the expected repeat structure (≈2,788 repeat households),
with the age-progression check computed dag-mask-aware on the
singles-repeater subset.

(V8) **GSUR coverage (household-type-aware).** The active GSUR
variable is complete for the active sample per household type: `gsur`
non-null for singles active records; `gsur_male`, `gsur_female`
non-null for couples active records. Because the GSURv2 rebuild
already confirmed active GSUR completeness (V4 of the rebuild), the
V8 check here confirms the completeness is preserved through the
stacking and that the GSUR values carried into the pooled dataset
are the GSURv2 rates.

(V9) **The remaining provisional-battery check** (per the
provisional construction's V1–V9 enumeration), reproduced against
the GSURv2 pooled dataset.

The validation battery passes if and only if all nine checks pass
(or, for the V5 range warning, are correctly classified as a
calibration item rather than a deflation error, as in the
provisional build). The re-run records the complete V1–V9 results in
the execution report (§14) and the sidecars (§8).

One GSURv2-specific validation observation: the per-component GSUR
means (recorded in the sidecar) are now the GSURv2 means and are
expected to differ from the provisional v1-fallback means. The
re-run records the GSURv2 means; a comparison against the v1-fallback
means (available from the preserved fallback columns) is a useful
diagnostic but is not a pass/fail gate.

---

## 10. Required config handling

The re-run must enforce exact GSURv2 input resolution through a
dedicated config or a tightly scoped config patch. The existing
config `config/multi_year/fr_p3a_stage_m1.yaml` resolves the
provisional v1-fallback inputs and must not be used unchanged for
the GSURv2 re-run.

Before execution, the re-run must establish one of two config
mechanisms:

(Option 1) **A dedicated GSURv2 Stage M1 config**, e.g.
`config/multi_year/fr_p3a_gsurv2_stage_m1.yaml`. The dedicated
config names the exact GSURv2 input stems (§5), sets the output
stems (§6), sets the provisioning label to
`gsurv2_opportunity_year_aligned` (§7), and otherwise reproduces the
provisional config's Stage M1 settings (the CPI factors, the
cluster-key, the stacked-ID scheme, the V1–V9 validation, the
expected counts). The dedicated config is the cleaner option: it
isolates the GSURv2 re-run configuration from the provisional
configuration, leaving the provisional config intact for the
historical record.

(Option 2) **A tightly scoped config patch** that makes the P3a run
resolve only the exact GSURv2 stems. The patch restricts the input
resolution (the input glob or the input-stem list) to the six GSURv2
parquets exactly, sets the output stems and label, and otherwise
leaves the provisional config's Stage M1 settings unchanged. The
patch option is acceptable only if it makes the input resolution
exact — a patch that loosens or broadens the input glob is not
acceptable.

Either mechanism must satisfy the exact-input-resolution constraint
(§5 I1–I3): the resolved inputs must be exactly the six GSURv2
parquets, with no v1-fallback or v2gsurY or other stem matched. The
re-run must confirm, before stacking, that the resolved input set is
exactly the six GSURv2 parquets (by listing the resolved paths and
checking each against Table 1), and must halt if the resolved set
differs (§13 H1).

The config handling also carries forward the K2 decision from the
GSURv2 extension: the active GSUR column name remains `gsur` (singles)
/ `gsur_male`, `gsur_female` (couples), and the deflation-exclusion
list in the config must list these active GSUR columns (not a
`gsur_v2` alias) so that the GSUR proportions are correctly excluded
from CPI deflation. The CPI harmonisation deflates the monetary
columns (`ils_dispy`, `ils_earns`, `yem` and their components), not
the GSUR proportions.

The config handling is the mechanism that enforces the exact-input-
resolution control. The re-run must not proceed without a config or
patch that resolves exactly the six GSURv2 stems.

---

## 11. What is authorized

The re-run authorises the following, and only the following.

(A1) **Establishing the GSURv2 config or config patch** (§10) that
resolves exactly the six GSURv2 input stems, sets the GSURv2 output
stems, and sets the `gsurv2_opportunity_year_aligned` label.

(A2) **Confirming the exact input resolution** (§5): listing the
resolved input paths and confirming the set is exactly the six
GSURv2 parquets (Table 1), with no v1-fallback, v2gsurY, or other
stem matched.

(A3) **Archiving or preserving the provisional v1-fallback pooled
outputs** (§13 H6) before writing the GSURv2 outputs.

(A4) **Re-running the five-step Stage M1 pipeline** against the six
GSURv2 parquets: year stacking with stacked-identifier engineering,
cross-year identity validation, CPI/HICP harmonisation, cluster-key
annotation, and the V1–V9 validation battery.

(A5) **Writing the two GSURv2 pooled output products** (§6) — the
stacked-raw and harmonised parquets — with their Stage M1 metadata
sidecars (§8).

(A6) **Producing the execution report** (§14) recording the re-run
outcome and the V1–V9 results.

The authorised steps are the Stage M1 P3a GSURv2 pooled stacking
re-run and its immediate housekeeping (config establishment, input-
resolution confirmation, provisional-output archival). They do not
extend to any downstream step.

---

## 12. What is not authorized

The re-run does not authorise the following. Each is separately
gated.

(N1) **Pooled estimation.** No pooled estimation, provisional or
final, is authorised. The final pooled estimation remains gated
behind the stacking re-run's own strict construction verdict, the
cluster-robust SE wrapper, and the pooled specification.

(N2) **Welfare implementation or computation.** No welfare work is
authorised. Welfare computation requires its own authorization and
an accepted empirical baseline.

(N3) **P3b or P4.** The P3b configuration (hard-blocked pending the
ISF comparability gate) and the P4 configuration are NOT authorised.

(N4) **Canonical promotion.** No canonical promotion of the GSURv2
pooled dataset is authorised. The dataset is written to the versioned
`gsurv2`-tagged pooled path; canonical promotion requires explicit
approval after the stacking re-run's construction verdict.

(N5) **Promotion of the pooled route over M1-clean.** Producing the
GSURv2 pooled dataset does not promote the pooled route over the
single-year M1-clean baseline. The re-run produces a data product,
not an estimation result; only a future SA2 verdict on an estimated
final pooled specification could displace M1-clean.

(N6) **Modification of the M1-clean or M1-naive estimation specs.**
The estimation specifications are unchanged by the re-run.

The not-authorised steps are everything downstream of the stacking
re-run. The re-run produces the final pooled dataset; it does not
estimate, compute welfare, or promote from it.

---

## 13. Halt conditions

The re-run halts under the following conditions. Each halt preserves
the inputs and any partial outputs and requires diagnosis before the
re-run proceeds.

(H1) **Input resolution not exact.** If the resolved input set is
not exactly the six GSURv2 parquets (Table 1) — if it is missing a
GSURv2 parquet, includes a v1-fallback or v2gsurY or other stem, or
matches more than the six GSURv2 parquets through a broad glob — the
re-run halts before stacking. The exact-input-resolution constraint
(§5) is the central control; a resolution failure halts the re-run.

(H2) **Input SHA-256 mismatch.** If a resolved GSURv2 input parquet's
SHA-256 does not match the recorded value (Table 1), the re-run
halts: the input is not the validated rebuild output or has been
modified.

(H3) **Component missing.** If a component parquet (singles or
couples) is missing for any survey year, the re-run halts: the
pooled dataset would omit a household type (the failure mode of the
provisional build's first run). The re-run must confirm all six
component parquets are present (two per year) before stacking.

(H4) **Row-count or household-count mismatch.** If the stacked row
count or household-year count does not match the expected values
(1,244,500 rows, 12,445 household-years) or the per-component counts
(Table 1 of the provisional verdict), the re-run halts: the stacking
did not preserve the sample structure.

(H5) **Validation failure.** If any V1–V9 check fails (other than the
V5 range warning correctly classified as a calibration item), the
re-run halts and records the failing check.

(H6) **Provisional or pre-existing output overwrite.** If the re-run
would overwrite the provisional v1-fallback pooled outputs, or a
pre-existing GSURv2-tagged output, the re-run halts before
overwriting. The provisional outputs are preserved; a pre-existing
GSURv2 output is archived before the re-run proceeds.

(H7) **Stale config.** If the re-run would execute against the
unchanged provisional config (`fr_p3a_stage_m1.yaml`) that resolves
the v1-fallback inputs, the re-run halts: a GSURv2 config or patch
(§10) must be established first.

The halt conditions are protective. The most consequential is H1
(input resolution not exact), which guards against the re-run
silently consuming a v1-fallback or other non-GSURv2 parquet — the
error that would produce a pooled dataset mislabelled as GSURv2 but
carrying non-GSURv2 rates. H3 (component missing) guards against the
recurrence of the provisional build's couples-only defect.

---

## 14. Required execution report

The re-run produces an execution report
(`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`
or equivalent) recording the re-run outcome and the V1–V9 results.
The report is the deliverable that confirms the re-run outcome and
informs the next gating decision.

The report must record:

(R1) **The input resolution.** The resolved input paths, confirmed
to be exactly the six GSURv2 parquets (Table 1), with their SHA-256
hashes verified, and the config or config-patch mechanism (§10) that
enforced the resolution.

(R2) **The provisional-output archival.** Confirmation that the
provisional v1-fallback pooled outputs were archived or preserved
before the GSURv2 outputs were written.

(R3) **The stacking results.** The pooled row count, household-year
count, and per-year/per-component composition, confirmed against the
expected values.

(R4) **The V1–V9 validation results.** The complete battery results,
with each check's outcome and the expected-versus-observed values.

(R5) **The CPI harmonisation.** The deflation factors applied and
the V5 deflation-correctness result.

(R6) **The cluster-key annotation.** The `cluster_id = idorighh`
annotation and the unique-cluster count.

(R7) **The GSUR means.** The per-component GSURv2 GSUR means, with a
comparison against the v1-fallback means (from the preserved fallback
columns) recorded as a diagnostic.

(R8) **The output inventory.** The two GSURv2 pooled output products,
their SHA-256 hashes, their row counts, and their sidecars, with the
`provisioning_label` confirmed as `gsurv2_opportunity_year_aligned`.

(R9) **Any halt and diagnosis, if applicable.**

(R10) **The readiness of the next gate.** A statement that the next
gate is a strict Stage M1 P3a GSURv2 stacking construction verdict
(paralleling the provisional construction verdict), and a
confirmation that the re-run did not perform any downstream step.

The execution report is returned to the project chat for the next
gating decision. If the re-run passes, the next gate is a strict
stacking construction verdict on the GSURv2 pooled dataset. If the
re-run halts, the report informs the diagnosis and the re-
authorisation.

---

## 15. Exact next Claude Code task

The following prompt initiates the Stage M1 P3a GSURv2 pooled
stacking re-run in Claude Code Sonnet. The prompt executes the
authorised re-run (§11) under the halt conditions (§13) and produces
the execution report (§14). It does not estimate any model or
compute welfare.

Tool path: Claude Code Sonnet (local codebase, pooled stacking).

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present: the six GSURv2-based MNL parquets (§5)
with their recorded SHA-256 hashes; the existing Stage M1 P3a config
(`config/multi_year/fr_p3a_stage_m1.yaml`); the Stage M1 stacking
script (`m1_stack_years.py`); the provisional pooled outputs (to be
archived/preserved); and this stacking authorization.

Prompt to use:

> Execute the Stage M1 P3a GSURv2 pooled stacking re-run per
> `docs/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`. Use
> the interpreter `.venv\Scripts\python.exe`. Do NOT estimate any
> model. Do NOT compute welfare. Do NOT promote any output to a
> canonical path. Do NOT execute P3b or P4. Do NOT modify any
> estimation specification.
>
> 1. Establish exact GSURv2 input resolution. Create either a
>    dedicated GSURv2 config
>    `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml` or a tightly
>    scoped patch of `fr_p3a_stage_m1.yaml` that resolves ONLY the
>    six GSURv2 stems: `fr_2015_RURO_mnl_GSURv2_y2014__`,
>    `fr_2016_RURO_mnl_GSURv2_y2015__`,
>    `fr_2017_RURO_mnl_GSURv2_y2016__` (each `__singles.parquet` and
>    `__couples.parquet`). Do NOT use the v1-fallback stems
>    (`v1gsurY`), the intermediate `v2gsurY` stems, or any broad glob
>    that could match a non-GSURv2 parquet. Set the output stems to
>    `fr_p3a_gsurv2_stacked_raw` / `fr_p3a_gsurv2_harmonised` and the
>    provisioning label to `gsurv2_opportunity_year_aligned`.
>
> 2. List the resolved input paths and confirm the set is EXACTLY
>    the six GSURv2 parquets (verify each SHA-256 against the
>    recorded values: y2014 singles `889b2f8a…` / couples
>    `d44d2292…`, y2015 singles `139cd025…` / couples `61e3107b…`,
>    y2016 singles `8fce026d…` / couples `2d8dc7ae…`). If the
>    resolved set differs, includes a non-GSURv2 stem, or a SHA
>    mismatches: HALT and report.
>
> 3. Archive or preserve the provisional v1-fallback pooled outputs
>    (`fr_p3a_stacked_raw.parquet`, `fr_p3a_harmonised.parquet`, and
>    their sidecars) before writing the GSURv2 outputs. If a
>    GSURv2-tagged output already exists, archive it (do not
>    overwrite silently).
>
> 4. Confirm all six component parquets are present (two per year).
>    If any component is missing: HALT (guards against the
>    couples-only defect).
>
> 5. Run the five-step Stage M1 pipeline against the six GSURv2
>    parquets: year stacking with stacked-ID engineering (numeric
>    int64 UID scheme), cross-year identity validation (dag-mask-
>    aware), CPI/HICP harmonisation (φ₂₀₁₅=1.0031, φ₂₀₁₆=1.0000,
>    φ₂₀₁₇=0.9886, base 2016), cluster-key annotation (`cluster_id =
>    idorighh`), and the V1–V9 validation battery.
>
> 6. Confirm the expected pooled structure: 1,244,500 rows, 12,445
>    household-years, per-component counts matching the provisional
>    build (FR_2015 sgl 166,900/cpl 256,600, FR_2016 sgl 167,600/cpl
>    257,700, FR_2017 sgl 166,200/cpl 229,500), 9,657 unique
>    clusters. If counts mismatch: HALT.
>
> 7. Write the two GSURv2 pooled output products with Stage M1
>    sidecars carrying `provisioning_label =
>    gsurv2_opportunity_year_aligned`, the GSURv2 lookup provenance,
>    the exact-input-resolution record, and the V1–V9 results.
>
> Save the execution report as
> `Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`,
> recording the input resolution and SHA verification, the
> provisional-output archival, the stacking results, the V1–V9
> validation results, the CPI harmonisation, the cluster-key
> annotation, the GSURv2-versus-v1 GSUR means, the output inventory
> with the confirmed label, any halt and diagnosis, and the
> readiness of the next gate. Do NOT estimate. Do NOT compute
> welfare.

Output to save: the execution report at
`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`,
together with the two GSURv2 pooled output products and their
sidecars.

What to do next: return the execution report to the project chat for
the next gating decision. If the re-run passes, the next gate is a
strict Stage M1 P3a GSURv2 stacking construction verdict
(paralleling the provisional P3a construction verdict), which
adjudicates whether the GSURv2 pooled dataset is correctly
constructed and fit to serve as the input to a final pooled
estimation. If the re-run halts — particularly on H1 (input
resolution not exact) or H3 (component missing) — the report informs
the diagnosis and the re-authorisation. Pooled estimation, welfare
computation, and canonical promotion remain separately gated and are
not authorised by this re-run.

---

**Required final statements**

- **Stage M1 P3a GSURv2 stacking re-run is authorized only after
  exact GSURv2 input resolution is enforced.** The re-run must
  resolve exactly the six GSURv2-based MNL parquets (§5) through a
  dedicated GSURv2 config or a tightly scoped config patch (§10),
  with no v1-fallback, v2gsurY, or broad-glob resolution; an
  inexact resolution halts the re-run (§13 H1).

- **Pooled estimation is NOT authorized.** Separately gated behind
  the stacking re-run's construction verdict, the cluster-robust SE
  wrapper, and the pooled specification.

- **Welfare computation is NOT authorized.** Separately gated behind
  an accepted empirical baseline and the welfare scaffolding
  implementation.

- **M1-clean 2016 remains the active JMP baseline.** The Stage M1
  P3a GSURv2 stacking re-run produces a pooled data product; it
  produces no estimation result and does not displace the M1-clean
  baseline. M1-clean 2016 remains the active JMP baseline until a
  later SA2 verdict explicitly promotes a final pooled specification.
