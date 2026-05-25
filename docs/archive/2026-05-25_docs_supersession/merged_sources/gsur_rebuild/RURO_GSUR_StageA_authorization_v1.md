> Merged into `docs/France_case/consolidated/RURO_GSUR_rebuild_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# RURO GSUR Stage A Authorization Memo v1

Date: 2026-05-17

---

## 1. Purpose

This memo is the single authoritative reconciliation of the three GSUR
decision documents produced during the 2026-05-17 acquisition and O2
resolution work. It resolves the apparent contradiction between the
acquisition completion memo (which declared Stage A NOT authorized) and
the open-decisions resolution memo (which declares Stage A AUTHORIZED),
and states unambiguously what is and is not authorized as of this date.

All future implementation prompts must cite this memo as the authorization
source, not the acquisition completion memo.

---

## 2. Why the acquisition completion memo initially blocked implementation

`docs/RURO_GSUR_external_acquisition_completion_v1.md` was written
immediately after the external file downloads concluded on 2026-05-17.
At that point, decision O2 (denominator data requirement) had not been
resolved: the acquisition had confirmed that the preferred D1 source
(`lfst_r_lfp2acedu`, Eurostat labour force by NUTS-2 × sex × age ×
education) does not publish Y20-64 or any narrow 10-year age band for
France or any other EU country. This was a blocking finding because v2.1
§9 requires Y20-64 as the Stage A denominator and §6 requires narrow bands
for Stage B.

The completion memo's verdict — "PARTIAL ACQUISITION SUCCESS; O2
unresolved; Stage A NOT authorized" — was correct at the time it was
written. The document correctly identified D2 (`lfst_r_lfsd2pop`,
population in private households) as the fallback requiring an explicit
denominator-source binding decision before implementation could proceed.
That decision had not yet been made.

---

## 3. How O2 was subsequently resolved

Following the acquisition completion memo, `docs/RURO_GSUR_O2_denominator_resolution_v1.md`
was produced. It answers the three O2 questions with data evidence and
records a binding decision:

**(Q1)** Since D1 structurally cannot provide Y20-64 or any narrow band
for any EU country, the rebuild uses D2 for both Stage A and Stage B.
This is not a concession; D1 cannot serve the purpose and D2 is the
explicitly authorised acceptable approximation per v2.1 §5(D2).

**(Q2)** No alternative official labour-force denominator at the required
(NUTS-2 × sex × education × Y20-64) granularity exists in the Eurostat
catalogue. The finding was confirmed by checking `lfst_r_lfe2eedu`,
`lfst_r_lfu3pers`, and the full Eurostat NUTS-2 dataflow catalogue.

**(Q3)** v2.1 §5 does not require revision. Its D2 fallback path and
documentation requirements already authorise population weighting when
labour-force denominators at the required disaggregation are unavailable.
An O2 addendum in the open-decisions memo is sufficient to record the
binding decision.

The O2 resolution memo is factually correct and methodologically sound.
Its binding decision is recorded in `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md`
as the O2 addendum.

---

## 4. Current authoritative decision documents

| Document | Role | Status |
|----------|------|--------|
| `docs/RURO_GSUR_rebuild_specification_v2_1.md` | Governing specification | Authoritative; unchanged |
| `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md` | Open-decisions record | Authoritative; all O1/O2/O9 now resolved; AUTHORIZED |
| `docs/RURO_GSUR_O2_denominator_resolution_v1.md` | O2 evidence and binding decision | Authoritative; binding |
| `docs/RURO_GSUR_external_acquisition_completion_v1.md` | Acquisition provenance and file inventory | Superseded with respect to O2 authorization only; factual content (file provenance, suppression inventory, crosswalk chain) remains valid and must be cited for those purposes |
| `docs/RURO_GSUR_StageA_authorization_v1.md` (this memo) | Authorization reconciliation | Authoritative for implementation authorization decisions |

`docs/RURO_GSUR_external_acquisition_completion_v1.md` is superseded only
with respect to its O2 authorization verdict. All other content —
the file provenance records, the NUTS-2 crosswalk chain documentation,
the suppression inventory, the acquisition details — remains valid and
is not superseded.

---

## 5. Stage A implementation authorization

**Stage A lookup implementation is authorized as of 2026-05-17.**

The authorization rests on the following resolved decisions:

| Decision | Resolution |
|----------|------------|
| O1 | `fr_drgn1_to_nuts2_crosswalk.csv` constructed and verified; all 22 NUTS-2 codes resolved without ambiguity |
| O2 | D2 (`lfst_r_lfsd2pop`) operational for Stage A (Y20-64) and Stage B (narrow bands); D1 diagnostic only at Y15-74; FRI2 flagged-but-valued cells use D2 with validation note; FRM0 2 missing cells → D3 (weight=1/3) with reviewer sign-off |
| O3 | Age 65 → Y20-64 broad fallback with `gsur_age_band_used = "Y20-64_fallback_age65"` flag |
| O4 | deh 0/1/2→educ3=0, 3/4→1, 5→2; mapping already encoded in upstream parquets |
| O5 | drgn1=9 in output schema; NaN for FR 2016 metropolitan sample |
| O7 | Mandatory manual sign-off before merge; sign-off is a procedural step, not an implementation blocker |
| O8 | Île-de-France parity tolerance 0.001 absolute |
| O9 | INSEE BDM 001688526; 2016 annual average 9.725% |
| O10 | Versioned-path-first; canonical paths untouched until Stage A verdict + user approval |

Decision O6 (Stage B necessity) is deferred to post-Stage-A review and
does not block Stage A. It is not a hard blocker at any point before
Stage A verdict.

The governing specification `docs/RURO_GSUR_rebuild_specification_v2_1.md`
does not require revision. The O2 denominator-source change is a D2
fallback path already specified in §5(D2); the O2 addendum in the
open-decisions memo is the complete authorisation record.

---

## 6. O7 crosswalk sign-off status

O7 requires an explicit user approval message referencing the crosswalk
file (`Data/external/fr_drgn1_to_nuts2_crosswalk.csv`) and the merge key
used, before any write to versioned GSURv2 parquet paths. This requirement
is:

- **Not a blocker for writing the Stage A lookup script or running pre-merge
  build steps.** The script may be written, reviewed, and tested in dry-run
  mode before sign-off.
- **A blocker for the merge step** that writes
  `fr_2016_RURO_mnl_GSURv2__singles.parquet` and
  `fr_2016_RURO_mnl_GSURv2__couples.parquet`. No parquet write may occur
  until sign-off is obtained as a recorded approval message.
- **Required once**, at crosswalk-construction time, before the first merge.
  It does not need to be repeated for subsequent Stage A re-runs unless the
  crosswalk file is modified.

The O7 sign-off has not yet been obtained. It must be solicited
explicitly at the point in the Stage A implementation when the crosswalk
is presented to the user and the merge key is specified.

---

## 7. What is authorized now

The following work is authorized as of the date of this memo:

1. **Stage A lookup table construction**: build the GSUR lookup from
   `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` and the crosswalk
   `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`, following the
   O2 addendum denominator-source decision and the O3/O4/O5 handling
   rules. The lookup may be written to a working or intermediate path.

2. **Stage A merge script**: write and test (dry-run) the script that
   joins the lookup to the MNL parquets via the drgn1→NUTS-2→GSUR join
   key, producing enriched parquets at the versioned paths. Dry-run
   testing against the canonical parquets is permitted without O7
   sign-off as long as no parquet is written.

3. **D1 vs D2 diagnostic comparison**: compute the aggregated GSUR rate
   at Y15-74 under D1 and D2 weighting and prepare the comparison for
   inclusion in the Stage A validation report, per v2.1 §5(D2)
   documentation requirements.

4. **Stage A validation framework**: write the validation report template,
   Île-de-France parity check (tolerance 0.001), national benchmark
   comparison (9.725%), and Stage A decision-rule scaffolding (SA-STANDS,
   SA-REVISION, SA-OVERTURNED) as defined in v2.1 §9.

---

## 8. What is not authorized yet

The following work is explicitly not authorized:

1. **Versioned parquet write**: writing
   `fr_2016_RURO_mnl_GSURv2__singles.parquet` or
   `fr_2016_RURO_mnl_GSURv2__couples.parquet` is blocked until O7 crosswalk
   sign-off is obtained as a recorded user approval message.

2. **Canonical parquet overwrite**: writing to
   `fr_2016_RURO_mnl__singles.parquet` or `fr_2016_RURO_mnl__couples.parquet`
   is not authorized at any point during Stage A. Canonical promotion
   requires (a) a Stage A verdict of SA-STANDS or SA-REVISION, and (b) an
   explicit user approval message after the verdict is issued. A verdict of
   SA-OVERTURNED does not authorise promotion.

3. **Re-estimation**: running estimation against any parquet (versioned or
   canonical) is not authorized until the Stage A lookup table and
   versioned MNL rebuild pass all Stage A validations and a Stage A verdict
   has been issued.

4. **Stage B implementation**: Stage B (age-specific GSUR, narrow age bands,
   O6 necessity decision) is deferred to post-Stage-A review. No Stage B
   work may begin until Stage A produces a verdict and O6 is resolved.

5. **Modification of existing canonical parquets, estimation engine,
   post-estimation scripts, or specification files** outside the GSUR
   rebuild scope.

---

## 9. Exact next implementation task

**Task**: Write and run the Stage A GSUR lookup table build script.

Inputs:
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` (D2 operational denominator)
- `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` (drgn1→NUTS-2 mapping)
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` (D1 diagnostic, Y15-74 only)

Key outputs (intermediate, not merged):
- Stage A GSUR lookup table: one row per (drgn1, educ3, sex) combination,
  `gsur` = unemployment rate from D2 Y20-64, `weighting_source` column,
  `gsur_age_band_used` column
- D1 vs D2 rate comparison at Y15-74 for the Stage A validation report

Handling rules to implement (from resolved decisions):
- O2: D2 operational; FRI2 flagged-but-valued → use D2, flag in report;
  FRM0 2 missing cells → D3 weight=1/3 with reviewer sign-off; FRM0 Y20-64
  flagged-but-valued → use D2, flag in report
- O3: age 65 rows → Y20-64 fallback; `gsur_age_band_used = "Y20-64_fallback_age65"`
- O4: educ3 mapping already in parquets; join key is (new_nuts2_code_2016, sex, educ3)
- O5: drgn1=9 rows → NaN for all GSUR columns; no special treatment needed
  for FR 2016 metropolitan sample

Before running the merge step (writing GSURv2 parquets): present the
crosswalk and merge key to the user and obtain explicit O7 sign-off as a
recorded approval message.
