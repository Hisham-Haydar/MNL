# JMP GSURv2 Multi-Year Extension — Construction Authorization v1

Date: 2026-05-20

Specification class: construction authorization memo. The memo
authorises the GSURv2 Stage A lookup construction for opportunity
years 2016, 2015, and 2014 under Option B — a single controlled
construction task that runs y2016 first as a provenance and
value-identity lock and constructs y2015 and y2014 only on
conditional success. It is an authorization document for the
lookup construction only; it does not authorise the MNL-parquet
rebuild, pooled stacking, pooled estimation, welfare work, or
canonical promotion.

Reference documents:
- `docs/JMP_GSURv2_multi_year_extension_readiness_reaudit_v1.md`
  (the re-audit returning READY FOR GSURv2 CONSTRUCTION)
- `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`
  (the remediation authorization, now satisfied)
- `docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` (the y2016
  provenance-lock procedure, with correction
  `docs/JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md`)
- `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md` (the
  governing design memo)
- `docs/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule and the GSURv2 final-build requirement)
- `Results/JMP_GSURv2_external_file_remediation_report_v1.md` (the
  external-file retrieval confirmation)
- `docs/JMP_GSURv2_script_remediation_report_v1.md` (the C1–C7
  parameterisation confirmation)
- `Results/JMP_GSURv2_script_remediation_static_validation_v1.md`
  (the static V4a/V4b/V4c validation)

Interpreter: all commands use the project virtual environment
`.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`). System
Python is not the validated interpreter for this project.

Scope of memo: the memo authorises the construction of the three
GSURv2 opportunity-year lookups (y2016, y2015, y2014) under Option
B, with the y2016 value-identity gate as the mandatory
precondition for the y2015 and y2014 construction. The memo does
not authorise the MNL-parquet rebuild, the pooled stacking re-run,
pooled estimation, welfare implementation, welfare computation, or
canonical promotion; those steps are separately gated.

---

## 1. Purpose

The purpose of this memo is to authorise the GSURv2 Stage A lookup
construction for opportunity years 2016, 2015, and 2014 under
Option B, following the readiness re-audit's verdict of READY FOR
GSURv2 CONSTRUCTION. The construction produces the three
opportunity-year GSURv2 lookups required by the multi-year pooled
sample, replacing the v1-fallback opportunity-side rates with
GSURv2 education- and sex-stratified rates at the lookup level.

The memo serves five functions. First, it confirms the readiness
verdict and the satisfaction of all construction preconditions
(§2, §3). Second, it specifies the construction scope under Option
B and the required opportunity years (§4, §5). Third, it specifies
the y2016 value-identity gate as the mandatory precondition for
the y2015 and y2014 construction, and authorises the y2015 and
y2014 construction conditional on the gate (§6, §7, §8). Fourth,
it specifies the input files, commands, output files, sidecar
metadata, and validation checks (§9 through §13), the halt
conditions (§14), and the failure-handling protocols (§17, §18).
Fifth, it bounds the authorization (§15, §16), specifies the
construction report (§19), and delivers the exact Claude Code task
(§20).

The memo authorises lookup construction only. It does not
authorise any downstream step. The single-year M1-clean 2016
specification remains the active JMP baseline throughout the
construction and until a future SA2 verdict on a final pooled
specification determines otherwise (§16).

---

## 2. Current readiness verdict

The readiness re-audit returned **READY FOR GSURv2 CONSTRUCTION**.
All seven post-remediation validation checks (V1–V7 per the
remediation authorization §14) pass, and all remediation outputs
required before construction authorization (O1–O5) are present and
verified (re-audit §1). No blocking item remains for lookup
construction (re-audit §11).

The re-audit confirmed the resolution of all eight conditions that
the original implementation audit flagged as failing or flagged
(re-audit §2): the unemployment-rate workbook covers all three
years (A1), the four Eurostat denominator files and two INSEE
benchmark files are retrieved and present (A2, A3), the NUTS-2016
vintage of the retrieved files is confirmed compatible with the
crosswalk (A4), the y2016 sidecar is deferred to construction
under the lock plan (A5/K1), the K2 column-naming decision is
applied (`gsur` retained, `gsur_v2` removed from the config), the
O7 sign-off request is assembled and pending but does not block
lookup construction (A5/K3), and all seven C1–C7 script changes
are implemented and statically validated (A6).

The re-audit recommended Option B — y2016 provenance lock plus
y2014/y2015 construction in one controlled construction task,
scoped to Stage A lookup production only (re-audit §1, §14). This
memo adopts Option B.

The re-audit explicitly noted that it is not itself an
authorization (re-audit §12): all construction preconditions are
met, and construction authorization may now be issued, but a
separate construction authorization memo is required. This memo is
that construction authorization.

---

## 3. Why construction is now authorized

GSURv2 lookup construction is authorised because all preconditions
established by the design memo, the remediation authorization, and
the readiness re-audit are now satisfied. Four precondition
categories are confirmed.

First, the external inputs are present and verified. All twelve
external input files required across the three opportunity years
are present in `Data/external/` with correct sizes (re-audit §3):
the unemployment-rate workbook (`FR_gsur.xlsx`), the crosswalk
(`fr_drgn1_to_nuts2_crosswalk.csv`), and the year-specific D2
denominators, D1 denominators, and INSEE benchmark CSVs for 2014,
2015, and 2016. The NUTS-2016 vintage of the 2014 and 2015 files
is confirmed (re-audit §3), so no NUTS-vintage conversion is
required. The benchmark values are fixed: 9.9 per cent for 2014,
10.025 per cent for 2015, and 9.725 per cent for 2016 (re-audit
§3), each computed as the mean of the four quarterly INSEE BDM
001688526 values with `obs_status=A`.

Second, the construction script is parameterised and statically
validated. All seven C1–C7 changes are implemented and committed
(commit `178ca72`; script remediation report §3 through §9), the
year-invariant construction logic is preserved unchanged (re-audit
§4 V7), and the static validation V4a/V4b/V4c passes on all checks
(static validation report §V7). The script accepts the
`--opportunity-year` argument, reads the year-specific inputs,
writes the year-tagged outputs, and writes the C7 sidecar.

Third, the naming decisions are resolved. The K2 decision is
applied: the active column name is `gsur`, and `gsur_v2` is
removed from the config's deflation-exclusion list (re-audit §5;
script remediation report §10). The C6 decision is applied: the
script writes year-tagged output paths (re-audit §6).

Fourth, the y2016 provenance-lock plan is ready. The lock plan
document is present, complete, and verified (re-audit §9), with
the value-identity baseline recorded: the existing un-tagged y2016
parquet `FR_gsur_ruro_v2_stageA.parquet` has SHA-256
`19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`,
size 7,444 bytes, 54 rows, 11 columns (re-audit §9). The
construction's y2016 run must reproduce this lookup value-
identically, which is the construction's primary quality gate.

The O7 crosswalk sign-off is pending the user's decision but does
not block lookup construction (re-audit §10): O7 gates the MNL-
parquet merge step, which is downstream of the lookup construction
and is not authorised by this memo. The construction authorization
covers lookup production only and may be issued and executed
without the O7 sign-off.

All preconditions for lookup construction are satisfied.
Construction is authorised under Option B.

---

## 4. Construction scope

The construction is authorised under **Option B**: a single
controlled construction task that constructs all three opportunity-
year GSURv2 lookups in sequence, with the y2016 run serving as the
provenance and value-identity lock and the y2015 and y2014 runs
proceeding only on conditional success.

Option B is adopted over Option A (y2016 only, with y2014 and y2015
deferred to a second authorization) for three reasons recorded in
the re-audit §14: all three years share the same inputs (crosswalk,
workbook), the same script version (commit `178ca72`), and the
same construction logic, so running them in sequence under one
authorization produces three consistent, co-dated lookups with
matching sidecar provenance; the y2016 value-identity check is the
empirical gate, and if it passes, y2014 and y2015 can proceed
immediately without a second round-trip; and Option A would
require a second construction authorization memo for y2014 and
y2015, adding unnecessary overhead when the conditions are
identical.

The construction scope is Stage A lookup production only. It
covers running the parameterised script for the three opportunity
years, performing the y2016 value-identity check, inspecting the
sidecars and validation outputs, and committing the three lookups
and sidecars. Post-construction cleanup, archival of the un-tagged
y2016 file, and reference migration are separately gated after the
construction report and validation report pass. It does not cover
the MNL-parquet rebuild, the pooled stacking re-run, pooled
estimation, welfare work, or canonical promotion (§16).

The construction is sequential and conditional. The y2016 run
executes first; the y2015 run executes only if the y2016 value-
identity gate passes; the y2014 run executes only if both the
y2016 value-identity gate passes and the y2015 construction and
validation pass. The sequence and the conditionality are the
defining features of Option B and are specified in §6 through §8
and §14.

---

## 5. Required opportunity years

The construction covers three opportunity years, mapped to the
three survey years by the alignment rule (year-alignment decision
§2). Table 1 specifies the years, the benchmark values, and the
construction order.

| Construction order | Opportunity year | Required by survey year | Benchmark (%) | Role |
|---|---|---|---|---|
| 1 (first) | 2016 | FR_2017 | 9.725 | provenance / value-identity lock |
| 2 (conditional on y2016) | 2015 | FR_2016 | 10.025 | new construction |
| 3 (conditional on y2016 and y2015) | 2014 | FR_2015 | 9.900 | new construction |

The construction order is y2016 first, then y2015, then y2014.
The order is not arbitrary: y2016 runs first because it is the one
opportunity year for which an existing validated lookup exists
(`FR_gsur_ruro_v2_stageA.parquet`), so the y2016 run can be checked
for value-identity against that existing lookup, validating the
parameterised script's construction logic before any genuinely
new lookup (y2015, y2014) is produced. The y2016 value-identity
check is therefore the empirical gate that licenses the y2015 and
y2014 construction.

The y2015 run executes only if the y2016 value-identity gate
passes (§6, §7). The y2014 run executes only if both the y2016
value-identity gate passes and the y2015 construction and
validation pass (§6, §8). The conditional sequencing ensures that
no genuinely new lookup is produced until the parameterised
script's construction logic has been validated against the
existing y2016 lookup, and that the y2014 run does not proceed if
the y2015 run reveals a construction problem.

---

## 6. y2016 value-identity gate

The y2016 value-identity gate is the mandatory precondition for
the y2015 and y2014 construction. The y2016 run must produce a
year-tagged lookup whose `gsur` values are value-identical to the
existing un-tagged y2016 lookup, under a key-aligned comparison.
If the gate fails, the construction halts and the y2015 and y2014
runs do not proceed (§14, §17).

The y2016 run produces:
- `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json`

The value-identity check compares the produced
`FR_gsur_ruro_v2_stageA_y2016.parquet` against the existing
un-tagged `FR_gsur_ruro_v2_stageA.parquet`. The check is **key-
aligned, not row-order-only**: the two parquets are joined on the
key tuple `(year, drgn1, educ3, sex)`, and the `gsur` values are
compared within matched keys. A row-order-only comparison (row $i$
of one file against row $i$ of the other) is insufficient because
it would spuriously fail if the two files carried identical values
in a different row order, and would spuriously pass if a key were
present in one file but not the other at the same row position. The
key-aligned comparison is the correct identity check.

The value-identity gate requires all of the following:

(G1) Both files have exactly **54 rows**. The 54 rows comprise 48
active cells (drgn1 ∈ {1, …, 8} × educ3 ∈ {0, 1, 2} × sex ∈ {M,
F}) and 6 drgn1=9 stub rows (NaN `gsur`).

(G2) All keys match exactly. The set of `(year, drgn1, educ3,
sex)` tuples in the produced y2016 lookup equals the set in the
existing un-tagged lookup. The `year` key is 2016 in both files.
No key is present in one file and absent in the other.

(G3) No duplicate keys. Within each file, the key tuple `(year,
drgn1, educ3, sex)` is unique across all 54 rows. No key appears
more than once in either file.

(G4) Maximum absolute difference in `gsur` is **0.0**, or **≤
1e-12** only if floating-point representation requires it. The
difference is computed over the matched keys. The 6 drgn1=9 stub
rows carry NaN `gsur` in both files; the difference check is NaN-
aware: the 6 stub rows must be NaN-aligned (NaN in both files at
matched keys), and the maximum-absolute-difference computation is
performed over the 48 active (non-null) cells. A naive max-
absolute-difference computation that includes the NaN stub rows
would yield NaN and spuriously fail the check; the NaN-aware
computation confirms the 6 stub rows are NaN in both files and
computes the difference over the 48 active cells.

The value-identity gate passes if and only if all four conditions
(G1, G2, G3, G4) hold. The pass confirms that the parameterised
script reproduces the existing validated y2016 lookup exactly,
validating the construction logic. The fail indicates that the
parameterisation has altered the construction logic or that the
y2016 inputs differ from the inputs that produced the existing
lookup; either case requires diagnosis before any further
construction (§17).

The y2016 sidecar (`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`)
must additionally be inspected: it must contain all 14 fields
(§12), with `opportunity_year=2016`, `gsur_column_name="gsur"`,
`benchmark_pct=9.725`, `row_count=54`, and
`idf_parity_difference` ≈ 0.0. The sidecar inspection is part of
the y2016 validation (§13) and complements the value-identity
gate.

The y2016 value-identity gate is the load-bearing precondition of
Option B. It must pass before the y2015 run proceeds.

---

## 7. y2015 construction authorization

The y2015 construction is authorised **conditional on the y2016
value-identity gate passing** (§6). If and only if the y2016 gate
passes, the y2015 run executes.

The y2015 run produces:
- `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2015__sidecar.json`

The y2015 run constructs a genuinely new lookup (no existing y2015
GSURv2 lookup exists), so there is no value-identity check for
y2015. The y2015 validation instead confirms the construction's
internal correctness:

(Y2015-1) Row count is 54 (48 active + 6 drgn1=9 stubs).

(Y2015-2) The sidecar contains all 14 fields, with
`opportunity_year=2015`, `gsur_column_name="gsur"`,
`benchmark_pct=10.025`, `row_count=54`, and
`idf_parity_difference` ≈ 0.0.

(Y2015-3) The IDF parity check holds: drgn1=1 (Île-de-France,
single-component group FR10) matches the FR10 source values
exactly (`idf_parity_difference` ≈ 0.0 in the sidecar). This is
the load-bearing construction-correctness check, as it confirms
the population-weighted aggregation reduces correctly to the
single-component value for the single-component region.

(Y2015-4) The L5 national-benchmark check is recorded: the
constructed national GSUR aggregate is compared against the y2015
benchmark of 10.025 per cent, and the difference is recorded in
the sidecar (`benchmark_difference_pct`). The L5 check is a
consistency diagnostic, not a construction input; a deviation does
not invalidate the cell-level rates but must be recorded.

(Y2015-5) The NUTS-2016 vintage of the y2015 D2 denominator is
confirmed compatible with the crosswalk (the L-vintage check),
already confirmed at retrieval (re-audit §3).

The y2015 validation passes if and only if Y2015-1 through Y2015-3
hold and Y2015-4 and Y2015-5 are recorded. The y2015 construction
and validation must pass before the y2014 run proceeds (§8, §14).

If the y2015 construction or validation fails — for instance, if
the row count is not 54, if the IDF parity check fails, or if the
sidecar is malformed — the construction halts and the y2014 run
does not proceed (§14, §18).

---

## 8. y2014 construction authorization

The y2014 construction is authorised **conditional on both the
y2016 value-identity gate passing (§6) and the y2015 construction
and validation passing (§7)**. If and only if both conditions
hold, the y2014 run executes.

The y2014 run produces:
- `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2014__sidecar.json`

The y2014 run constructs a genuinely new lookup (no existing y2014
GSURv2 lookup exists), so there is no value-identity check for
y2014. The y2014 validation confirms the construction's internal
correctness:

(Y2014-1) Row count is 54 (48 active + 6 drgn1=9 stubs).

(Y2014-2) The sidecar contains all 14 fields, with
`opportunity_year=2014`, `gsur_column_name="gsur"`,
`benchmark_pct=9.9`, `row_count=54`, and `idf_parity_difference`
≈ 0.0.

(Y2014-3) The IDF parity check holds: drgn1=1 matches the FR10
source values exactly (`idf_parity_difference` ≈ 0.0).

(Y2014-4) The L5 national-benchmark check is recorded: the
constructed national GSUR aggregate is compared against the y2014
benchmark of 9.9 per cent, and the difference is recorded in the
sidecar.

(Y2014-5) The NUTS-2016 vintage of the y2014 D2 denominator is
confirmed compatible with the crosswalk, already confirmed at
retrieval (re-audit §3).

The y2014 validation passes if and only if Y2014-1 through Y2014-3
hold and Y2014-4 and Y2014-5 are recorded.

The y2014 run is the terminal construction step. If it passes, all
three opportunity-year lookups are constructed and the commit step
(§10 Step 8) proceeds. Post-construction cleanup, archival of the
un-tagged y2016 file, and reference migration are separately gated
after the construction report and validation report pass. If the
y2014 construction or validation fails, the construction halts; the
y2016 and y2015 lookups are retained (they passed their gates), and
the y2014 failure is diagnosed (§18).

---

## 9. Required input files

The construction requires the twelve external input files
confirmed present by the re-audit §3. Table 2 specifies the files
by opportunity year.

| Role | y2016 | y2015 | y2014 |
|---|---|---|---|
| Unemployment-rate workbook (C2) | `FR_gsur.xlsx` (shared) | `FR_gsur.xlsx` (shared) | `FR_gsur.xlsx` (shared) |
| D2 denominator (C3) | `lfst_r_lfsd2pop_FR_2016.tsv` | `lfst_r_lfsd2pop_FR_2015.tsv` | `lfst_r_lfsd2pop_FR_2014.tsv` |
| D1 denominator, diagnostic (C4) | `lfst_r_lfp2acedu_FR_2016.tsv` | `lfst_r_lfp2acedu_FR_2015.tsv` | `lfst_r_lfp2acedu_FR_2014.tsv` |
| INSEE benchmark (C5) | `insee_001688526_2016.csv` | `insee_001688526_2015.csv` | `insee_001688526_2014.csv` |
| Crosswalk (shared) | `fr_drgn1_to_nuts2_crosswalk.csv` | (shared) | (shared) |

All paths are relative to `Data/external/`. The unemployment-rate
workbook and the crosswalk are year-invariant and shared across
all three years (re-audit §3). The D2 denominator is the
operational denominator (re-audit §3); the D1 denominator is
diagnostic only (the Eurostat D1 table does not publish the Y20-64
age band at NUTS-2 level, a year-invariant limitation). The INSEE
benchmark provides the year-specific `BENCHMARK_PCT` value.

The construction additionally requires the existing un-tagged
y2016 lookup `Data/external/FR_gsur_ruro_v2_stageA.parquet` (SHA-
256 `19ac53…`, 7,444 bytes, 54 rows, 11 columns) as the value-
identity baseline for the y2016 gate (§6).

All thirteen files (the twelve inputs plus the value-identity
baseline) are confirmed present (re-audit §3, §9). No input file
is missing. No file retrieval is required by this construction.

---

## 10. Required commands

The construction executes the following commands in order, using
the project virtual-environment interpreter
`.venv\Scripts\python.exe`. The commands are conditional: the
y2015 command runs only if the y2016 value-identity gate passes,
and the y2014 command runs only if both the y2016 gate and the
y2015 validation pass (§14).

Step 1 — y2016 provenance lock (value-identity gate):
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016
```

Step 2 — y2016 value-identity check (§6). Key-aligned comparison
of `FR_gsur_ruro_v2_stageA_y2016.parquet` against
`FR_gsur_ruro_v2_stageA.parquet` on keys `(year, drgn1, educ3,
sex)`, confirming G1 through G4. If the check fails: HALT (§17).

Step 3 — y2016 sidecar inspection (§12, §13): confirm 14 fields,
`opportunity_year=2016`, `benchmark_pct=9.725`, `row_count=54`,
`idf_parity_difference` ≈ 0.0.

Step 4 — y2015 construction (conditional on Step 2 PASS):
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2015
```

Step 5 — y2015 validation (§7): confirm row count 54, sidecar 14
fields, `benchmark_pct=10.025`, `idf_parity_difference` ≈ 0.0. If
the validation fails: HALT (§18).

Step 6 — y2014 construction (conditional on Step 2 PASS and Step 5
PASS):
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2014
```

Step 7 — y2014 validation (§8): confirm row count 54, sidecar 14
fields, `benchmark_pct=9.9`, `idf_parity_difference` ≈ 0.0. If the
validation fails: HALT (§18).

Step 8 — commit (conditional on all three years passing): commit
the three parquets and three sidecars to git. Post-construction
cleanup, archival of the un-tagged y2016 file, and reference
migration are separately gated after the construction report and
validation report pass.

Before each construction run, the existing-output guard applies
(§11): if a year-tagged output for the target year already exists,
the run must not overwrite it silently — the existing file is
archived or the run is halted and the existing file is documented
before re-running.

---

## 11. Required output files

The construction produces six output files, listed in Table 3. The
output naming is year-tagged per the C6 decision (re-audit §6).

| Opportunity year | Lookup parquet | Sidecar JSON |
|---|---|---|
| 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` | `FR_gsur_ruro_v2_stageA_y2016__sidecar.json` |
| 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` | `FR_gsur_ruro_v2_stageA_y2015__sidecar.json` |
| 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` | `FR_gsur_ruro_v2_stageA_y2014__sidecar.json` |

All paths are relative to `Data/external/`. Each lookup parquet
carries 54 rows and the eleven-column schema (re-audit §4 V7;
design memo §6). Each sidecar carries the 14 provenance fields
(§12).

The existing-output guard is a construction requirement: **if any
year-tagged output file already exists, the construction must not
overwrite it silently**. The re-audit §6 confirms that none of the
six year-tagged files exists at construction time (all are "not
yet built"), so the guard is not expected to trigger. If, however,
a year-tagged output is found to exist before its construction run
— for instance, from an aborted prior run — the existing file must
be archived (moved to `Data/external/archive/` with a timestamp)
or the run must be halted and the existing file documented, before
the construction run for that year proceeds. Silent overwriting is
not authorised.

The existing un-tagged y2016 lookup
`FR_gsur_ruro_v2_stageA.parquet` is not retired by this
construction. Post-construction cleanup, archival of the un-tagged
y2016 file, and reference migration are separately gated after the
construction report and validation report pass.

---

## 12. Required sidecar metadata

Each lookup parquet carries a sidecar JSON with the 14 provenance
fields specified by the C7 implementation (script remediation
report §9) and the design memo §14. Table 4 specifies the fields.

| Field | y2016 value | y2015 value | y2014 value |
|---|---|---|---|
| `opportunity_year` | 2016 | 2015 | 2014 |
| `gsur_column_name` | `"gsur"` | `"gsur"` | `"gsur"` |
| `output_path` | `…_y2016.parquet` | `…_y2015.parquet` | `…_y2014.parquet` |
| `input_d2` | `lfst_r_lfsd2pop_FR_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` |
| `input_d1` | `lfst_r_lfp2acedu_FR_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` |
| `input_unemployment_workbook` | `FR_gsur.xlsx` | (same) | (same) |
| `input_benchmark_csv` | `insee_001688526_2016.csv` | `…_2015.csv` | `…_2014.csv` |
| `benchmark_pct` | 9.725 | 10.025 | 9.9 |
| `nuts_vintage` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` |
| `idf_parity_difference` | ≈ 0.0 | ≈ 0.0 | ≈ 0.0 |
| `benchmark_difference_pct` | (recorded) | (recorded) | (recorded) |
| `row_count` | 54 | 54 | 54 |
| `build_timestamp` | (UTC ISO) | (UTC ISO) | (UTC ISO) |
| `script_version` | (commit hash) | (commit hash) | (commit hash) |

The `gsur_column_name` field records the K2 decision (`gsur` as
the active column name) explicitly per build (re-audit §5). The
`benchmark_pct` field records the year-specific INSEE benchmark
value read from the year-specific CSV (script remediation report
§7). The `idf_parity_difference` field records the Île-de-France
parity check result (the maximum absolute difference between the
constructed drgn1=1 GSUR and the FR10 source values), which must
be ≈ 0.0 for a correct construction. The `script_version` field
records the git commit hash of the construction script (commit
`178ca72` or its descendant), falling back to `"unknown"` if the
git call fails. The `build_timestamp` is timezone-aware UTC.

The sidecar inspection (§13) confirms that each sidecar contains
all 14 fields with the expected values. A malformed sidecar (a
missing field, a wrong `opportunity_year`, a wrong `benchmark_pct`,
or a non-negligible `idf_parity_difference`) is a validation
failure that halts the construction (§14, §18).

---

## 13. Required validation checks

The construction is validated by the following checks, applied per
opportunity year. Table 5 summarises the checks.

| Check | y2016 | y2015 | y2014 |
|---|---|---|---|
| Row count = 54 | required | required | required |
| Value-identity vs un-tagged baseline (key-aligned, G1–G4) | required (gate) | n/a | n/a |
| Sidecar 14 fields present | required | required | required |
| `opportunity_year` correct | 2016 | 2015 | 2014 |
| `gsur_column_name = "gsur"` | required | required | required |
| `benchmark_pct` correct | 9.725 | 10.025 | 9.9 |
| `row_count = 54` in sidecar | required | required | required |
| IDF parity (`idf_parity_difference` ≈ 0.0) | required | required | required |
| L5 benchmark difference recorded | required | required | required |
| NUTS-2016 vintage (L-vintage) | confirmed | confirmed | confirmed |
| No year-tagged output overwritten silently | required | required | required |

The y2016 value-identity check (§6) is the gate that licenses the
y2015 and y2014 construction. Its four conditions (G1 both files
54 rows; G2 all keys match exactly; G3 no duplicate keys; G4 max
absolute `gsur` difference 0.0 or ≤ 1e-12, NaN-aware over the 48
active cells) are the precise specification of the value-identity
requirement. The check is key-aligned on `(year, drgn1, educ3,
sex)`, not row-order-only.

The IDF parity check (`idf_parity_difference` ≈ 0.0) is the load-
bearing construction-correctness check for each year. Because
drgn1=1 (Île-de-France) is a single-component group (FR10), the
population-weighted aggregation reduces to the single-component
value, and the constructed drgn1=1 GSUR must match the FR10 source
exactly. A non-negligible IDF parity difference indicates a
construction error and is a validation failure.

The L5 national-benchmark check is recorded but is a consistency
diagnostic, not a pass/fail construction gate: a deviation between
the constructed national aggregate and the INSEE benchmark does
not invalidate the cell-level rates (the rebuild specification
classifies the L5 check as a diagnostic), but the deviation is
recorded in the sidecar for audit.

All checks must pass (or be recorded, for the diagnostic L5 check)
for the construction to complete. A failure of any pass/fail check
halts the construction per the halt conditions (§14).

---

## 14. Halt conditions

The construction halts under the following conditions. Each halt
preserves the outputs produced up to the halt point and requires
diagnosis before any further construction.

(H1) **y2016 value-identity gate fails.** If the y2016 value-
identity check (§6) fails on any of G1 through G4 — the row counts
differ, the keys do not match exactly, a duplicate key exists, or
the maximum absolute `gsur` difference exceeds the tolerance — the
construction halts after the y2016 run. The y2015 and y2014 runs
do NOT proceed. The y2016 failure is diagnosed (§17).

(H2) **y2016 sidecar malformed.** If the y2016 sidecar is missing a
field, carries a wrong `opportunity_year`, a wrong `benchmark_pct`,
or a non-negligible `idf_parity_difference`, the construction halts
after the y2016 run. The y2015 and y2014 runs do NOT proceed.

(H3) **y2015 construction or validation fails.** If the y2015 run
produces a lookup that fails any pass/fail check (§7, §13) — the
row count is not 54, the IDF parity check fails, or the sidecar is
malformed — the construction halts after the y2015 run. The y2014
run does NOT proceed (§18).

(H4) **y2014 construction or validation fails.** If the y2014 run
produces a lookup that fails any pass/fail check (§8, §13), the
construction halts after the y2014 run. The y2016 and y2015
lookups (which passed their gates) are retained (§18).

(H5) **Existing year-tagged output found.** If a year-tagged output
file for any target year already exists before its construction run
(§11), the construction halts before overwriting it. The existing
file is archived or documented before the run proceeds. Silent
overwriting is not authorised.

(H6) **Input file missing or NUTS-vintage mismatch.** If a required
input file is missing at construction time, or if the L-vintage
check on a D2 denominator reveals a NUTS-vintage incompatible with
the crosswalk, the construction halts for that year. The re-audit
§3 confirms all inputs are present and NUTS-2016-compatible, so
this halt is not expected, but the check is retained as a guard.

(H7) **Construction script modification detected.** If the
construction script `enh_prepare_FR_gsur_v2.py` is found to differ
from the committed version (commit `178ca72` or its authorised
descendant) at construction time, the construction halts. The
construction must run against the committed, statically validated
script; modifying the script during construction is not authorised
(§16).

The halt conditions are protective: they stop the construction at
the first sign of a problem, preserving the outputs produced up to
that point and preventing a downstream lookup from being
constructed on a faulty foundation. The most consequential halt is
H1 (y2016 value-identity failure), which indicates that the
parameterised script does not reproduce the existing validated
lookup — a problem that must be resolved before any new lookup is
trusted.

---

## 15. What is authorized

The construction authorises the following, and only the following.

(A1) **Running the parameterised script for opportunity year 2016**
(`--opportunity-year 2016`) to produce the year-tagged y2016
lookup and its sidecar, as the provenance and value-identity lock.

(A2) **The y2016 value-identity check** (§6), key-aligned on
`(year, drgn1, educ3, sex)`, against the existing un-tagged y2016
lookup.

(A3) **Running the parameterised script for opportunity year 2015**
(`--opportunity-year 2015`), conditional on the y2016 value-
identity gate passing, to produce the year-tagged y2015 lookup and
its sidecar.

(A4) **Running the parameterised script for opportunity year 2014**
(`--opportunity-year 2014`), conditional on both the y2016 value-
identity gate passing and the y2015 validation passing, to produce
the year-tagged y2014 lookup and its sidecar.

(A5) **Inspection of all sidecars and validation outputs** (§12,
§13) for the three years.

(A6) **Committing the three lookups and three sidecars to git**,
conditional on all three years passing their gates.

(A7) **Archiving any pre-existing year-tagged output** (if found)
before re-running, per the existing-output guard (§11).

The authorised steps are the GSURv2 lookup construction under
Option B and the commit of the three lookups and sidecars (A6).
Post-construction cleanup, archival of the un-tagged y2016 file,
and reference migration are separately gated after the construction
report and validation report pass. They do not extend to any
downstream step.

---

## 16. What is not authorized

The construction does not authorise the following. Each is
separately gated.

(N1) **MNL parquet rebuild.** The merge of the GSURv2 lookups into
the FR_2015, FR_2016, and FR_2017 MNL parquets — replacing the v1-
fallback rates with GSURv2 rates in the MNL data — is NOT
authorised. It is downstream of the lookup construction, requires
its own authorization, and additionally requires the O7 crosswalk
sign-off (re-audit §10), which is pending the user's decision.

(N2) **Pooled stacking re-run.** The re-run of the Stage M1 pooled
stacking against GSURv2-based MNL parquets is NOT authorised. It is
downstream of the MNL rebuild.

(N3) **Pooled estimation.** No pooled estimation, provisional or
final, is authorised. The final pooled estimation remains gated
behind the complete GSURv2-based MNL rebuild, the cluster-robust
SE wrapper, and the pooled specification.

(N4) **Welfare implementation or computation.** No welfare work is
authorised. Welfare implementation and computation require their
own authorizations and an accepted empirical baseline.

(N5) **Canonical promotion.** No canonical promotion of any GSURv2
lookup or MNL parquet is authorised. The versioned-path discipline
holds: the GSURv2 lookups are written to `Data/external/` under
year-tagged versioned names; canonical promotion requires explicit
approval after a downstream Stage A verdict.

(N6) **Modification of the construction script during
construction.** The construction must run against the committed,
statically validated script (commit `178ca72` or its authorised
descendant). Modifying `enh_prepare_FR_gsur_v2.py` during the
construction is NOT authorised; a modification detected at
construction time halts the construction (§14 H7). If the
construction reveals a script defect, the construction halts and a
separate remediation addresses the defect before the construction
is re-authorised.

(N7) **Replacing M1-clean 2016 as the active JMP baseline.** The
single-year M1-clean 2016 specification remains the active JMP
baseline. The GSURv2 construction is a data-construction step that
produces opportunity-side lookups; it does not produce any
estimation result and cannot displace the M1-clean baseline. M1-
clean remains active until a future SA2 verdict on a final
(GSURv2-based) pooled specification determines otherwise.

The not-authorised steps are everything downstream of the lookup
construction and its housekeeping. The construction prepares the
GSURv2 lookups; it does not consume them in any estimation, merge,
or welfare step.

---

## 17. What happens if y2016 fails

If the y2016 value-identity gate fails (halt condition H1) or the
y2016 sidecar is malformed (halt condition H2), the construction
halts after the y2016 run. The y2015 and y2014 runs do NOT
proceed.

The y2016 failure is the most consequential failure mode, because
the y2016 run is the validation of the parameterised script's
construction logic against the existing validated lookup. A y2016
value-identity failure indicates one of two problems: either the
parameterisation (C1–C7) has altered the construction logic (the
script no longer reproduces the existing lookup from the same
inputs), or the y2016 inputs at construction time differ from the
inputs that produced the existing un-tagged lookup. Either problem
invalidates the trust in the parameterised script, and no
genuinely new lookup (y2015, y2014) may be constructed until the
problem is resolved.

The failure-handling protocol is:

(F1) **Halt and preserve.** The construction halts. The produced
year-tagged y2016 lookup and its sidecar are preserved (not
deleted) for diagnosis. The existing un-tagged y2016 lookup is NOT
retired (the retirement at Step 8 is conditional on the value-
identity pass).

(F2) **Diagnose the discrepancy.** The diagnosis compares the
produced y2016 lookup against the existing un-tagged lookup cell by
cell, identifying which cells differ and by how much. The
diagnosis distinguishes the two problem classes: a uniform or
structured difference across many cells suggests an altered
construction logic (a parameterisation error); a difference
confined to specific cells suggests an input difference (a year-
specific input file that differs from the input that produced the
existing lookup).

(F3) **Report and re-authorise.** The diagnosis is recorded in the
construction report (§19), and a separate remediation addresses the
identified problem. The construction is re-authorised only after
the problem is resolved and the y2016 value-identity gate is
confirmed to pass. The y2015 and y2014 construction does not
proceed until the y2016 gate passes.

A y2016 failure does not produce any y2015 or y2014 lookup, does
not retire the existing un-tagged y2016 lookup, and does not
trigger any downstream step. The construction is suspended pending
diagnosis and re-authorisation.

---

## 18. What happens if y2016 passes but y2015 or y2014 fails

If the y2016 value-identity gate passes but the y2015 construction
or validation fails (halt condition H3), or if both y2016 and
y2015 pass but the y2014 construction or validation fails (halt
condition H4), the construction halts at the failing year. The
outputs produced up to the halt point are retained.

The y2015-or-y2014 failure is less consequential than a y2016
failure, because the y2016 value-identity pass has already
confirmed that the parameterised script reproduces the existing
validated lookup correctly. A failure of a new-year construction
(y2015 or y2014) therefore points to a year-specific problem — a
malformed year-specific input, an unexpected suppression pattern in
the year-specific denominator, or a year-specific IDF parity
failure — rather than a systematic construction-logic error.

The failure-handling protocol is:

(F4) **Halt at the failing year.** If y2015 fails, the construction
halts after the y2015 run and the y2014 run does NOT proceed. If
y2014 fails, the construction halts after the y2014 run. The
outputs that passed (the y2016 lookup, and the y2015 lookup if the
failure is at y2014) are retained.

(F5) **Preserve the passing outputs.** The y2016 lookup (which
passed the value-identity gate) is retained. If the failure is at
y2014, the y2015 lookup (which passed its validation) is also
retained. The post-construction steps (commit, retire un-tagged
y2016, update references) are deferred until the failing year is
resolved, because the construction is incomplete.

(F6) **Diagnose the year-specific failure.** The diagnosis examines
the failing year's construction outputs: the row count, the IDF
parity difference, the sidecar fields, the year-specific
denominator suppression pattern. The diagnosis identifies the
year-specific cause.

(F7) **Report and re-run the failing year.** The diagnosis is
recorded in the construction report (§19). The failing year is
re-constructed after the year-specific problem is resolved. The
y2016 value-identity gate does not need to be re-run (it has
already passed), but the existing-output guard (§11) applies to the
re-run of the failing year: if a partial year-tagged output exists
from the failed run, it is archived before the re-run.

A y2015 or y2014 failure retains the passing outputs, halts the
construction at the failing year, and defers the post-construction
housekeeping until the construction is complete. It does not
trigger any downstream step.

The decision on whether to proceed with the post-construction
housekeeping (commit, retire un-tagged y2016) when one new-year
construction has failed is deferred to the user: the construction
report (§19) records the partial-success state, and the user
decides whether to commit the passing lookups and re-run the
failing year separately, or to halt entirely until all three years
pass. The construction authorization does not pre-empt this
decision; it specifies that the post-construction housekeeping is
conditional on all three years passing, and that a partial success
is reported for the user's decision.

---

## 19. Required construction report

The construction produces a construction report
(`Results/JMP_GSURv2_multi_year_extension_construction_report_v1.md`
or equivalent) recording the outcome of each construction step and
each validation check. The report is the deliverable that confirms
the construction outcome and informs the next gating decision.

The report must record:

(R1) **The construction sequence and outcomes.** For each
opportunity year, whether the construction run executed, whether
the validation passed, and the halt point if the construction
halted.

(R2) **The y2016 value-identity result.** The key-aligned
comparison outcome: the row counts (G1), the key-match result
(G2), the duplicate-key check (G3), and the maximum absolute `gsur`
difference (G4). The report records the exact maximum absolute
difference, confirming it is 0.0 or ≤ 1e-12.

(R3) **The per-year validation results.** For each year, the row
count, the sidecar field values (the 14 fields), the IDF parity
difference, and the L5 benchmark difference.

(R4) **The sidecar inspection.** The contents of each sidecar,
confirming the 14 fields with the expected values (Table 4).

(R5) **The commit record.** Whether the three lookups and sidecars
were committed to git and the commit hash. Post-construction
cleanup, archival of the un-tagged y2016 file, and reference
migration are separately gated and are not recorded here.

(R6) **The halt and failure-handling record, if applicable.** If
the construction halted, the halt condition, the diagnosis, and the
recommended remediation.

(R7) **The readiness of the next gate.** A statement of which
downstream gate is next (the MNL-parquet rebuild, gated behind the
O7 sign-off and a separate authorization) and a confirmation that
the construction did not perform any downstream step.

The construction report is returned to the project chat for the
next gating decision. If all three years pass, the next gate is the
O7 crosswalk sign-off (a user decision) followed by the MNL-parquet
rebuild authorization. If the construction halts, the report
informs the diagnosis and re-authorisation.

---

## 20. Exact next Claude Code task

The following prompt initiates the GSURv2 construction task in
Claude Code Sonnet under Option B. The prompt executes the
authorised construction sequence (§10) under the halt conditions
(§14) and produces the construction report (§19). It does not
rebuild any MNL parquet, re-run the pooled stacking, estimate any
model, or compute welfare.

Tool path: Claude Code Sonnet (local codebase, construction
execution).

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present: the parameterised construction script
(`scripts/enhanced/enh_prepare_FR_gsur_v2.py`, commit `178ca72`);
the twelve external input files (re-audit §3); the existing un-
tagged y2016 lookup
(`Data/external/FR_gsur_ruro_v2_stageA.parquet`, SHA-256
`19ac53…`); and this construction authorization.

Prompt to use:

> Execute the GSURv2 Stage A lookup construction under Option B per
> `docs/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`.
> Use the interpreter `.venv\Scripts\python.exe`. Do NOT rebuild any
> MNL parquet. Do NOT re-run the pooled stacking. Do NOT estimate
> any model. Do NOT compute welfare. Do NOT promote any file to a
> canonical path. Do NOT modify the construction script.
>
> Run the following in order:
>
> 1. Run y2016 (provenance / value-identity lock):
>    `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016`
>    Before running, confirm `FR_gsur_ruro_v2_stageA_y2016.parquet`
>    does not already exist; if it does, archive it to
>    `Data/external/archive/` before proceeding (do not overwrite
>    silently).
>
> 2. Perform the y2016 value-identity check, KEY-ALIGNED (not
>    row-order-only): join `FR_gsur_ruro_v2_stageA_y2016.parquet`
>    and the existing `FR_gsur_ruro_v2_stageA.parquet` on keys
>    `(year, drgn1, educ3, sex)`. Confirm: both files have 54 rows;
>    all keys match exactly; no duplicate keys within either file;
>    the 6 drgn1=9 stub rows are NaN-aligned (NaN in both); and the
>    maximum absolute difference in `gsur` over the 48 active
>    (non-null) cells is 0.0 (or ≤ 1e-12 if floating precision
>    requires). If the check FAILS on any condition: HALT, preserve
>    the produced y2016 lookup for diagnosis, do NOT retire the
>    un-tagged lookup, do NOT run y2015 or y2014, and report the
>    discrepancy.
>
> 3. Inspect `FR_gsur_ruro_v2_stageA_y2016__sidecar.json`: confirm
>    14 fields, `opportunity_year=2016`, `gsur_column_name="gsur"`,
>    `benchmark_pct=9.725`, `row_count=54`, `idf_parity_difference`
>    ≈ 0.0. If malformed: HALT.
>
> 4. ONLY IF the y2016 value-identity check passed, run y2015:
>    `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2015`
>    Confirm `FR_gsur_ruro_v2_stageA_y2015.parquet` does not already
>    exist before running; archive if it does.
>
> 5. Validate y2015: confirm row count 54; sidecar 14 fields,
>    `opportunity_year=2015`, `benchmark_pct=10.025`, `row_count=54`,
>    `idf_parity_difference` ≈ 0.0; L5 benchmark difference recorded.
>    If validation FAILS: HALT, preserve the y2016 and y2015
>    outputs, do NOT run y2014, and report.
>
> 6. ONLY IF y2016 value-identity passed AND y2015 validation
>    passed, run y2014:
>    `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2014`
>    Confirm `FR_gsur_ruro_v2_stageA_y2014.parquet` does not already
>    exist before running; archive if it does.
>
> 7. Validate y2014: confirm row count 54; sidecar 14 fields,
>    `opportunity_year=2014`, `benchmark_pct=9.9`, `row_count=54`,
>    `idf_parity_difference` ≈ 0.0; L5 benchmark difference recorded.
>    If validation FAILS: HALT, preserve all outputs, and report.
>
> 8. ONLY IF all three years passed: commit the three parquets and
>    three sidecars to git. Post-construction cleanup, archival of
>    the un-tagged y2016 file, and reference migration are separately
>    gated after the construction report and validation report pass —
>    do NOT retire the un-tagged file, do NOT run `git mv`, do NOT
>    update canary or validation scripts.
>
> Save the construction report as
> `Results/JMP_GSURv2_multi_year_extension_construction_report_v1.md`,
> recording the construction sequence and outcomes, the y2016 value-
> identity result (exact max absolute difference), the per-year
> validation results, the sidecar contents, the commit record, any
> halt and diagnosis, and the readiness of the next gate. Do NOT
> rebuild MNL parquets. Do NOT run pooled estimation. Do NOT compute
> welfare. Do NOT modify the construction script.

Output to save: the construction report at
`Results/JMP_GSURv2_multi_year_extension_construction_report_v1.md`,
together with the six year-tagged output files (three lookups,
three sidecars) in `Data/external/`.

What to do next: return the construction report to the project chat
for the next gating decision. If all three years pass, the next
gate is the O7 crosswalk sign-off (a user decision) followed by the
MNL-parquet rebuild authorization, neither of which is authorised
by this construction. If the construction halts, the report informs
the diagnosis and the re-authorisation.

---

**Required final statements**

The following statements are made explicitly, as required.

- **GSURv2 lookup construction is authorized only under Option B.**
  The construction runs y2016 first as a provenance and value-
  identity lock, constructs y2015 only if the y2016 value-identity
  gate passes, and constructs y2014 only if both the y2016 gate and
  the y2015 validation pass. No other construction scope is
  authorised.

- **MNL parquet rebuild is NOT authorized.** The merge of the
  GSURv2 lookups into the MNL parquets is downstream of the lookup
  construction, requires its own authorization, and additionally
  requires the pending O7 crosswalk sign-off.

- **Pooled stacking re-run is NOT authorized.** The re-run of the
  Stage M1 pooled stacking against GSURv2-based MNL parquets is
  downstream of the MNL rebuild and is not authorised.

- **Pooled estimation is NOT authorized.** No pooled estimation,
  provisional or final, is authorised by this construction.

- **Welfare implementation/computation is NOT authorized.** No
  welfare work is authorised by this construction.

- **M1-clean 2016 remains the active JMP baseline.** The single-
  year M1-clean 2016 specification remains the active JMP baseline.
  The GSURv2 lookup construction produces opportunity-side lookups;
  it does not produce any estimation result and does not displace
  the M1-clean baseline. M1-clean remains active until a future SA2
  verdict on a final pooled specification determines otherwise.
