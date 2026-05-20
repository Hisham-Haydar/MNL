# JMP GSURv2 y2016 Provenance Lock Plan v1

*France 2016 | v1 | 2026-05-20*

Governing authorization:
`docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` §9
(as corrected by
`docs/JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md`)

---

## 1. Purpose

This document is remediation output O5 per the authorization §13.
Its purpose is to specify the required sidecar fields and lock
procedure for the y2016 GSURv2 lookup so that the construction
authorization can execute the y2016 reproduction in one step against
a pre-specified and agreed target.

The existing y2016 lookup (`Data/external/FR_gsur_ruro_v2_stageA.parquet`)
was built on 2026-05-17 under
`docs/RURO_GSUR_StageA_authorization_v1.md`. It is correct by all
Stage A validation checks documented in
`docs/RURO_GSUR_v2_stageA_implementation_report_v1.md`, but it
carries two unresolved provenance deficits: the sidecar JSON required
by authorization §9 was never written (K1 FAIL), and the file uses
the un-tagged stem `FR_gsur_ruro_v2_stageA.parquet` rather than the
year-tagged stem adopted under the C6 decision (K1/K3 context). Both
deficits are resolved when the construction authorization executes
the y2016 reproduction under the parameterised script.

This document does not run the script, does not write any parquet,
and does not retire the existing un-tagged file. All of those actions
are deferred to the construction authorization.

---

## 2. Existing y2016 lookup

**File:** `Data/external/FR_gsur_ruro_v2_stageA.parquet`

**Status:** present, correct, untracked by git (written outside the
git workflow by the Stage A build on 2026-05-17; not included in any
commit).

**File identity:**
- Size: 7,444 bytes
- SHA-256: `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`
- mtime: 2026-05-17T20:44:25 (local)

**Schema (11 columns, 54 rows):**

| Column | Type | Notes |
|--------|------|-------|
| `year` | int64 | 2016 for all rows |
| `drgn1` | int64 | 1–9 |
| `educ3` | int64 | 0=low, 1=med, 2=high |
| `sex` | object | M / F |
| `gsur` | float64 | Y20-64 pop-weighted rate (proportion) |
| `weighting_source` | object | `population` for all rows |
| `gsur_age_band_used` | object | `Y20-64` (or `Y20-64_fallback_dom_absent` for drgn1=9) |
| `gsur_legacy_misaligned` | float64 | Reconstructed v1 rate (diagnostic) |
| `denom_flag` | object | D2 cell reliability flag |
| `n_components` | int64 | NUTS-2 components in drgn1 group |
| `gsur_unreliable` | bool | True if any contributing D2 cell is flagged u |

**Content summary:**
- 48 active rows (drgn1=1..8, all 6 educ3×sex combinations)
- 6 drgn1=9 stub rows (gsur=NaN, `Y20-64_fallback_dom_absent`)
- `weighting_source = population` throughout (D2 operational denominator)
- `gsur_unreliable = True` for 36 of 54 rows (all drgn1 groups
  include at least one NUTS-2 with suppressed D2 cells, except drgn1=1
  and drgn1=3 which are fully clean)
- gsur range (drgn1=1..8): 0.047036–0.234000; mean 0.111113

**Stage A validation outcomes (from implementation report §5 and
the build log):**

| Check | Result |
|-------|--------|
| IDF parity (drgn1=1 = FR10 source) | PASS — diff = 0.000000 for all 6 educ3×sex cells |
| L5 national benchmark (vs INSEE 9.725%) | PASS — within ±1 ppt tolerance |
| Missing values (drgn1=1..8) | PASS — 0 NaN gsur values |
| drgn1=9 stubs | PASS — 6 rows, gsur=NaN as required |
| Weighting-source documentation | PASS |

**Git status:** the file is not tracked in any commit. It was written
directly to `Data/external/` by the Stage A script run on 2026-05-17.
The construction authorization will produce the year-tagged replacement
`FR_gsur_ruro_v2_stageA_y2016.parquet`, at which point the un-tagged
file is retired (archived, not silently deleted) and the year-tagged
file is committed.

---

## 3. Missing sidecar issue

The construction script as built on 2026-05-17 did not include a C7
sidecar-write block. No sidecar JSON was written for the y2016 build.
The file `Data/external/FR_gsur_ruro_v2_stageA__sidecar.json` does
not exist.

**Consequence (K1 FAIL):** the y2016 lookup has no machine-readable
provenance record. There is no file recording the opportunity year,
the input files used, the benchmark value, the NUTS vintage, the
validation outcomes, or the build timestamp. The only provenance
record is the Stage A implementation report
(`docs/RURO_GSUR_v2_stageA_implementation_report_v1.md`) and the
Stage A authorization (`docs/RURO_GSUR_StageA_authorization_v1.md`),
which are human-readable documents.

**Why post-hoc sidecar creation is addressed in §5 below.**

**Resolution path:** the C7 sidecar block was implemented in the
script remediation (commit `178ca72`). When the construction
authorization runs the parameterised script with
`--opportunity-year 2016`, the C7 block writes the sidecar to
`Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json`
automatically. K1 is resolved by the C7 block at construction time,
not before. The sidecar is not written during this remediation.

---

## 4. Required sidecar fields

The C7 block in the parameterised script writes a JSON sidecar with
the following 14 fields. All fields are mandatory. The y2016-specific
values are given where deterministic from the existing lookup or the
authorization decisions; values stamped at build time are marked as
such.

| Field | Required value for y2016 | Source |
|-------|--------------------------|--------|
| `opportunity_year` | `2016` | argparse `--opportunity-year 2016` |
| `gsur_column_name` | `"gsur"` | K2 decision (authorization §6) |
| `output_path` | `"Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet"` | C6 year-tagged path |
| `input_d2` | `"Data/external/lfst_r_lfsd2pop_FR_2016.tsv"` | C3 f-string at YEAR=2016 |
| `input_d1` | `"Data/external/lfst_r_lfp2acedu_FR_2016.tsv"` | C4 f-string at YEAR=2016 |
| `input_unemployment_workbook` | `"Data/external/FR_gsur.xlsx"` | Hardcoded constant in script |
| `input_benchmark_csv` | `"Data/external/insee_001688526_2016.csv"` | C5 f-string at YEAR=2016 |
| `benchmark_pct` | `9.725` | Annual average read from `insee_001688526_2016.csv` (C5) |
| `nuts_vintage` | `"NUTS2016"` | Hardcoded constant in script; confirmed by A4 PASS |
| `idf_parity_difference` | Expected: `0.000000` (or `null` if check not run) | `val["IDF_parity"]["max_abs_diff"]` at build time |
| `benchmark_difference_pct` | Expected: within 1.0 ppt of 9.725% | `val["L5_national_benchmark"]["diff_pct"]` at build time |
| `row_count` | Expected: `54` (48 active + 6 drgn1=9 stubs) | `len(lookup_out)` at build time |
| `build_timestamp` | UTC ISO 8601, stamped at build time | `datetime.datetime.now(datetime.timezone.utc).isoformat()` |
| `script_version` | SHA of `enh_prepare_FR_gsur_v2.py` at build time | `git log -1 --format=%H -- <script path>` |

**Current script SHA (post-remediation, commit `178ca72`):**
`178ca72` is the commit containing the parameterised script. The
`script_version` field will record the full SHA of the HEAD commit of
`scripts/enhanced/enh_prepare_FR_gsur_v2.py` at the moment the
construction authorization runs. If the script is not modified between
now and that run, the SHA will be the `git log -1 --format=%H` output
for that file at commit `178ca72`.

**Value-identity expectation:** the 14-field sidecar for y2016 is
the provenance companion to a lookup that must be value-identical to
the existing un-tagged lookup. The `idf_parity_difference`,
`benchmark_difference_pct`, and `row_count` values written to the
sidecar at build time will confirm this identity. If any of the three
differ from the expected values above, that is a construction failure,
not a sidecar failure.

---

## 5. Whether post-hoc sidecar creation is safe

**Verdict: NOT RECOMMENDED. Rebuild under the parameterised script is
preferred (see §6).**

A post-hoc sidecar is a manually authored JSON file whose field values
are reconstructed from the Stage A implementation report and the
existing parquet rather than written by the build process at
construction time. The question is whether such a file is a safe
substitute for the C7-generated sidecar.

**Arguments for post-hoc creation:**
- The existing un-tagged parquet is correct and passes all Stage A
  checks. The field values are recoverable: `opportunity_year` and
  `benchmark_pct` are recorded in the implementation report;
  `row_count` is directly observable from the parquet (54); `idf_parity_difference`
  and `benchmark_difference_pct` are recorded in the implementation
  report (IDF parity PASS, national benchmark PASS); the input paths
  are deterministic from the build date and the K2/C6 decisions.
- Writing the sidecar post-hoc avoids the need to run the script
  during the provenance-lock step.

**Arguments against post-hoc creation (decisive):**

1. **`build_timestamp` and `script_version` cannot be correctly
   populated post-hoc.** The `build_timestamp` for the original build
   is 2026-05-17T20:44:25 (local mtime), but the C7 block writes UTC
   ISO 8601 from `datetime.datetime.now(datetime.timezone.utc)` at the
   moment the parquet is written. Populating this field from the mtime
   is an approximation, not a build-time record. The `script_version`
   field records the SHA of the script at build time; the original
   build used the pre-remediation script (no C7 block, hardcoded year),
   and that commit is not in the git history of the current repo state.
   Recording the current post-remediation SHA would be factually
   incorrect.

2. **The sidecar's purpose is to attest to a build, not to document
   what a build would have produced.** A post-hoc sidecar attests to
   the author's reconstruction, not to the build process. The C7 block
   is designed to be written by the same execution that writes the
   parquet, so that the `row_count`, `idf_parity_difference`, and
   `benchmark_difference_pct` are read directly from the validation
   results of that run. A post-hoc file relies on the author correctly
   transcribing values from the implementation report; an error in
   transcription would create a provenance record that is internally
   inconsistent with the parquet it purports to describe.

3. **The rebuild under the parameterised script produces both the
   year-tagged parquet and the correct sidecar in one step,** and the
   value-identity check against the existing un-tagged file confirms
   the year-invariant logic is preserved. This is strictly more
   informative than a post-hoc sidecar.

4. **The authorization explicitly defers K1 resolution to the
   construction authorization** (authorization §9 as corrected by the
   correction memo C4). Creating the sidecar post-hoc during the
   remediation would step outside that boundary without a separate
   authorization.

**Conclusion:** post-hoc sidecar creation is not safe as a
provenance substitute, and is not authorized by the remediation scope.
The sidecar is produced by the C7 block at construction authorization
time.

---

## 6. Whether y2016 rebuild under the parameterised script is preferred

**Verdict: YES. The y2016 rebuild under the parameterised script is
the preferred and authorized lock procedure.**

The rebuild approach produces:
1. `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` — the
   year-tagged lookup;
2. `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json` — the
   C7-generated provenance record with all 14 fields stamped at build
   time;
3. A value-identity match against the existing un-tagged lookup,
   confirming that the C1–C7 parameterisation preserves the
   year-invariant construction logic exactly.

**Why preferred:**

- The C1–C7 changes are confined to the input-selection and output-tagging
  layers. The year-invariant construction logic (aggregation, education
  alignment, Y20-64 age-band selection, drgn1=9 stub handling, IDF parity
  check, benchmark validation, output schema) is unchanged. Running the
  parameterised script for y2016 with the same 2016 inputs must reproduce
  the same 48 × 6 + 6 = 54 rows with value-identical `gsur` entries. A
  value-identity match is a strong empirical confirmation of the
  parameterisation correctness.
- The rebuild resolves K1 (missing sidecar) and the C6 output-naming
  issue (un-tagged filename) simultaneously and automatically, without
  manual intervention.
- The rebuild is authorised under the construction authorization. It
  does not require a separate or special authorization; it is the
  first step of the standard construction workflow (run
  `--opportunity-year 2016`, verify value-identity, accept and retire
  un-tagged file, then proceed to y2015 and y2014).

**Risk assessment:** Low. The inputs for y2016 are all present and
verified:
- `Data/external/FR_gsur.xlsx` — present (A1 PASS)
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` — present (confirmed)
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` — present (confirmed)
- `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` — present (O1 PASS)
- `Data/external/insee_001688526_2016.csv` — present (O9; benchmark
  value 9.725%)

The parameterised script was statically validated (V4a/V4b/V4c all
PASS, commit `178ca72`). The year-invariant construction logic is
unchanged. The only new code path for y2016 is the C7 sidecar write,
which depends only on Python `json`, `datetime`, and `subprocess`
(available in the venv). There is no plausible failure mode that would
alter the `gsur` values in the lookup while leaving the script
syntactically valid.

**Interpreter to use:** `.venv\Scripts\python.exe`
(resolved: `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).
System Python must not be used.

---

## 7. O7 crosswalk sign-off requirement

**Status: PENDING.** The O7 crosswalk sign-off was not obtained at
the time of the Stage A build (implementation report §8, §3 O7:
"The O7 crosswalk sign-off has not been obtained… The merge step
is blocked until explicit user approval"). This status is unchanged
by the remediation.

**What O7 requires for y2016:**

The O7 sign-off is the user's explicit approval of two things:

(a) **The crosswalk:** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`
    (22 rows, all `verified_against_eurostat = YES`). The crosswalk
    maps pre-2016 NUTS-2 codes (old_nuts2_code) to post-2016 codes
    (new_nuts2_code_2016) and to drgn1 groups. The drgn1 compositions
    are:

    | drgn1 | Region label | NUTS-2 components (post-2016) |
    |-------|-------------|-------------------------------|
    | 1 | Île-de-France | FR10 |
    | 2 | Bassin Parisien | FRF2, FRE2, FRD2, FRB0, FRD1, FRC1 |
    | 3 | Nord-Pas-de-Calais | FRE1 |
    | 4 | Est | FRF3, FRF1, FRC2 |
    | 5 | Ouest | FRG0, FRH0, FRI3 |
    | 6 | Sud-Ouest | FRI1, FRJ2, FRI2 |
    | 7 | Rhône-Alpes / Auvergne | FRK2, FRK1 |
    | 8 | Méditerranée | FRJ1, FRL0, FRM0 |
    | 9 | DOM stub | (none — NaN placeholder) |

(b) **The merge key:** `(drgn1, educ3, sex)`.

    The Stage A lookup is already aggregated to drgn1 level; the
    crosswalk is consumed during lookup construction and is not
    re-applied at merge time. The MNL merge join is a direct
    left-join on `(drgn1, educ3, sex)`, one row per individual
    (singles) or two rows per couple (one for each partner using
    their respective `educ3` and `sex`).

**Merge procedure the sign-off covers:**

1. For each MNL individual, read `drgn1`, `educ3`, `sex`.
2. Left-join to the y2016 lookup parquet on `(drgn1, educ3, sex)`.
3. Assign `gsur` (and ancillary columns) to the individual row.
4. For `dag == 65`, set `gsur_age_band_used = "Y20-64_fallback_age65"` (O3).
5. For `drgn1 == 9`, all GSUR columns remain NaN (O5 stub).
6. For couples: apply the join twice — `(drgn1, educ3_male, 'M')` for
   the male partner and `(drgn1, educ3_female, 'F')` for the female
   partner.

**What the sign-off does NOT require:**

O7 sign-off covers the crosswalk and merge key only. It does not
require the user to verify the gsur values themselves, the NUTS-2 rate
data, the IDF parity check, or the benchmark validation. Those are
Stage A construction-time checks. O7 is specifically about approving
the mapping from MNL individuals to drgn1 groups and the join key.

**When O7 is resolved:**

O7 is resolved when the user provides an explicit approval message
referencing `fr_drgn1_to_nuts2_crosswalk.csv` and the merge key
`(drgn1, educ3, sex)`. The O7 resolution is required before the MNL
parquet rebuild (the merge step), but it is NOT required before the
y2016 lookup rebuild under the parameterised script. The lookup
rebuild produces `FR_gsur_ruro_v2_stageA_y2016.parquet`; the MNL
merge is a subsequent, separately authorized step.

See `docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` for the
formal sign-off request document (prepared in the prior Stage A
workflow; still pending user response).

---

## 8. Recommended y2016 lock procedure

The following procedure is recommended for the construction
authorization. Steps are ordered; each step is a precondition for the
next.

**Step 1 — Confirm input files present.**
Confirm that all five y2016 inputs are present in `Data/external/`:
- `FR_gsur.xlsx`
- `lfst_r_lfsd2pop_FR_2016.tsv`
- `lfst_r_lfp2acedu_FR_2016.tsv`
- `fr_drgn1_to_nuts2_crosswalk.csv`
- `insee_001688526_2016.csv`

**Step 2 — Record the existing un-tagged parquet fingerprint.**
Before running the script, record the SHA-256 of the existing un-tagged
parquet as the value-identity baseline:
```
SHA-256: 19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef
Size: 7,444 bytes
```

**Step 3 — Run the parameterised script for y2016.**
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016
```
Expected outputs:
- `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json`

**Step 4 — Value-identity check.**
Compare the new year-tagged parquet column-wise against the existing
un-tagged parquet. Confirm that:
- Row count is identical: 54 rows.
- All 48 active-row `gsur` values are identical to within floating-point
  representation tolerance (max absolute difference = 0.0).
- Schema is identical (same 11 columns, same dtypes).
A mismatch on any `gsur` value is a construction failure requiring
diagnosis before proceeding.

**Step 5 — Inspect sidecar.**
Confirm `FR_gsur_ruro_v2_stageA_y2016__sidecar.json` parses without
error and contains all 14 required fields (§4). Confirm:
- `opportunity_year == 2016`
- `gsur_column_name == "gsur"`
- `benchmark_pct == 9.725`
- `nuts_vintage == "NUTS2016"`
- `idf_parity_difference == 0.0` (or very close)
- `row_count == 54`

**Step 6 — Commit year-tagged parquet and sidecar.**
Add both files to git and commit:
```
git add Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet
git add Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json
git commit -m "gsur_v2(y2016): lock year-tagged lookup and sidecar"
```

**Step 7 — Retire the un-tagged file.**
Move or archive the un-tagged file. Do not silently delete it:
```
git mv Data/external/FR_gsur_ruro_v2_stageA.parquet \
       Data/external/archive/FR_gsur_ruro_v2_stageA_untagged_2026-05-17.parquet
git commit -m "gsur_v2(y2016): retire un-tagged lookup to archive/"
```

**Step 8 — Update references.**
Update any references to `FR_gsur_ruro_v2_stageA.parquet` (without
year tag) in canary and validation scripts to the year-tagged y2016
path. Confirm no remaining references to the old un-tagged stem outside
`docs/archive/`.

**Step 9 — K1 resolved.**
After Steps 3–8 complete successfully, K1 (missing sidecar) is
resolved. The y2016 lock is complete.

**Note:** O7 sign-off (§7 above) is not a precondition for Steps 1–9.
O7 gates the MNL parquet merge, which is downstream of the lookup
lock.

---

## 9. What is not authorized

The following are explicitly outside the scope of this provenance lock
plan and of the remediation as a whole.

- **Running the parameterised script with `--opportunity-year 2016`**
  is not authorized during the remediation. It is authorized by the
  construction authorization memo (a separate document, not yet
  produced).
- **Writing `FR_gsur_ruro_v2_stageA_y2016.parquet`** during the
  remediation is not authorized.
- **Writing `FR_gsur_ruro_v2_stageA_y2016__sidecar.json`** during the
  remediation is not authorized.
- **Retiring or archiving the existing un-tagged parquet**
  (`FR_gsur_ruro_v2_stageA.parquet`) is not authorized during the
  remediation. It takes place at Step 7 of the lock procedure above,
  under the construction authorization.
- **Building y2014 or y2015 lookups** is not authorized here or in the
  remediation; those are sequenced after the y2016 lock under the
  same construction authorization.
- **MNL parquet rebuild, pooled estimation, welfare** are all
  downstream of the lookup lock and require their own authorizations.
- **Post-hoc sidecar creation** (manually authored JSON for the
  existing un-tagged lookup) is not authorized; see §5.

---

## 10. Exact next task

The construction authorization memo is the next task. It must be a
separate document that:

1. Confirms all remediation preconditions are met (referencing the
   script remediation report `docs/JMP_GSURv2_script_remediation_report_v1.md`
   and validation report `Results/JMP_GSURv2_script_remediation_static_validation_v1.md`).
2. Explicitly authorizes running:
   ```
   .venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016
   ```
3. Specifies the value-identity check (§8 Step 4) as a mandatory
   pass/fail gate. If the check fails, construction is halted.
4. Authorizes Steps 5–8 of the lock procedure (§8) contingent on the
   value-identity check passing.
5. Does not authorize y2014 or y2015 construction in the same memo
   (those are sequenced after the y2016 lock is confirmed), unless
   the user explicitly scopes all three years together.
6. Does not authorize the MNL parquet rebuild; that requires a
   separate authorization after the y2016 Stage A construction verdict.

**Exact command to be authorized (for inclusion in the construction
authorization memo):**
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016
```

**Expected outputs of the authorized run:**
- `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` (54 rows,
  value-identical to the existing un-tagged parquet)
- `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json` (14
  fields per §4 of this document)

**Pass criteria for the construction authorization:**
- Value-identity: max absolute difference in `gsur` vs. the existing
  un-tagged parquet = 0.0 (or machine epsilon).
- Sidecar: all 14 fields present; `opportunity_year == 2016`;
  `benchmark_pct == 9.725`; `row_count == 54`; `idf_parity_difference`
  consistent with Stage A IDF PASS.
- No MNL parquet written, no canonical path touched.

**What is produced by this document (O5):**
This provenance lock plan document is the sole output of the current
task. It contains the sidecar field specification (§4), the post-hoc
vs. rebuild analysis (§§5–6), the O7 sign-off specification (§7),
and the lock procedure (§8) that the construction authorization will
execute. No parquet was written. No script was run with
`--opportunity-year`.