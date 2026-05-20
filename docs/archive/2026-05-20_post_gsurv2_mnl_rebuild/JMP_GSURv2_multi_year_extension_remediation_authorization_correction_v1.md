# JMP GSURv2 Multi-Year Extension — Remediation Authorization Correction v1

*France 2015–2016–2017 | v1 | 2026-05-20*

---

## 1. Correction verdict

Eight sections of
`docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`
revised to adopt the conservative y2016 provenance-lock approach.
No data were built, no scripts were run, no parquets were written,
and no external files were retrieved. All corrections are textual;
the underlying audit findings, naming decisions, and file-retrieval
authorizations are unchanged.

| # | Section | Issue | Action |
|---|---------|-------|--------|
| C1 | §4 table + paragraph | y2016 row described "provenance lock to prepare; year-tag to apply" as a remediation output | Changed to "provenance lock plan to prepare; year-tag scheme decided; rebuild deferred to construction authorization" |
| C2 | §7 closing | "reference updates and retirement are authorised as part of the remediation (§11)" | Replaced with "deferred to the construction authorization, when the year-tagged y2016 lookup will actually be produced" |
| C3 | §8 closing | "The one bounded exception is the y2016 reproduction authorised in §9" | Replaced with "No year-tagged lookup parquet is written during the remediation" |
| C4 | §9 full rewrite | Authorised running `--opportunity-year 2016` to reproduce the y2016 lookup and retire the un-tagged file | Replaced with lock-plan documentation only: sidecar field specification, lock procedure, K1/K3 status; all reproduction deferred to construction authorization |
| C5 | §11 A2 | "References updated; un-tagged y2016 file retired when the year-tagged y2016 lookup is produced" | Replaced with "deferred to construction authorization" |
| C6 | §11 A5 | "Parameterised script run with `--opportunity-year 2016`…generating the year-tagged y2016 lookup and its sidecar" | Replaced with "lock-plan document prepared; actual y2016 reproduction deferred to construction authorization" |
| C7 | §12 N1 | "y2016 reproduction (A5) is the one bounded exception" | Replaced with "no GSURv2 lookup construction or reproduction is authorized for y2014, y2015, or y2016 during this remediation" |
| C8 | §13 O5 | "Year-tagged y2016 lookup and its sidecar" as required output | Replaced with "y2016 provenance and sidecar lock-plan document (`docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`)" |
| C9 | §14 V4 | "Run the parameterised script with `--opportunity-year 2016`…value-identity match" as validation | Replaced with static/no-write validation: imports, `--help`, path computation, C7 block presence |
| C10 | §14 V5 | "Confirm y2016 sidecar is written, parses, records K1 fields" | Replaced with "confirm lock-plan document is present and contains required fields" |
| C11 | §14 closing | "V4 reproduces the existing y2016 lookup under value-identity control" | Replaced with "No lookup parquet written; value-identity regression deferred to construction authorization" |
| C12 | §15 prompt + output + next | Prompt included step 5 (`--opportunity-year 2016` run) and step 6 (reference updates); "What to do next" cited V4 regression as a remediation pass/fail gate | Step 5 replaced with static parameterisation check; step 6 replaced with lock-plan document preparation; step 7 remains (O7 sign-off); "What to do next" updated to defer y2016 value-identity regression to construction authorization |

---

## 2. Files inspected

| File | Purpose |
|------|---------|
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | Memo subject to correction |
| `docs/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | Source of the two resolution-path options for K1 (§9 of audit addendum); confirmed that both paths (post-hoc sidecar and rebuild-reproduction) were offered but neither was mandated |

No code files were read. No data files were read. No scripts were
run.

---

## 3. Scope problem in v1

The v1 memo authorised running the parameterised script with
`--opportunity-year 2016` during the remediation (§9, §11 A5, §14
V4, §15 step 5). This authorisation was inconsistent with the
conservative y2016 provenance-lock approach for three reasons.

First, running `--opportunity-year 2016` writes a year-tagged y2016
parquet (`FR_gsur_ruro_v2_stageA_y2016.parquet`) and retires the
existing un-tagged y2016 lookup. These are data-construction and
data-management actions, not documentation or parameterisation
actions. The remediation memo explicitly limits its scope to
construction-precondition activities (§3 closing); writing a new
parquet and retiring an existing one fall outside that scope.

Second, the value-identity regression check (V4 in v1) was gated
on the `--opportunity-year 2016` run succeeding. If the run failed
for any reason — a missing input, a path error, an unexpected code
path — the remediation would stall at V4, blocking all downstream
construction authorization. The conservative approach decouples the
parameterisation validation (which can be checked statically) from
the construction run, so that a static check failure is diagnosable
without the added complexity of a live data write.

Third, the v1 memo placed the y2016 provenance lock — resolving K1
— inside the remediation boundary. The K1 resolution (writing the
sidecar) is an output of the C7 implementation running against y2016
inputs. Deferring the C7 run to the construction authorization means
K1 is resolved at the same time and under the same conditions as the
y2014 and y2015 sidecar writes, which is the cleaner separation: the
remediation implements and validates the C7 logic; the construction
authorization exercises it for each year.

---

## 4. y2016 reproduction removed

The following authorizations from v1 are removed.

**Removed from §8 (C1–C7 authorization):** The sentence "The one
bounded exception is the y2016 reproduction authorised in §9, which
validates the parameterisation and generates the y2016 provenance
lock without constructing a new lookup." This exception no longer
exists; no script run is authorised during the remediation.

**Removed from §9 (y2016 provenance and sidecar lock):** The entire
reproduction-and-retirement framework — running
`--opportunity-year 2016`, comparing the reproduced lookup value-
identically against the existing un-tagged lookup, accepting the
year-tagged y2016 lookup, and retiring the un-tagged file — is
removed from the remediation. The logic is preserved in the §9 lock
procedure, which is now a plan for execution at construction
authorization time.

**Removed from §11 A5:** The phrase "The parameterised script is run
with `--opportunity-year 2016` to reproduce the existing y2016
lookup, subject to the value-identity regression check (§9, §14),
generating the year-tagged y2016 lookup and its sidecar (resolving
K1). This is a bounded reproduction of an existing validated lookup,
not a new construction." Replaced with preparation of the lock-plan
document only.

**Removed from §12 N1:** The sentence "The y2016 reproduction (A5)
is the one bounded exception, and it reproduces an existing
validated lookup rather than constructing a new one." The revised N1
states explicitly that no GSURv2 lookup construction or reproduction
is authorized for y2014, y2015, or y2016 during the remediation.

**Removed from §13 O5:** The year-tagged y2016 parquet
(`FR_gsur_ruro_v2_stageA_y2016.parquet`) and its sidecar
(`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`) are no longer
required remediation outputs.

**Removed from §14 V4:** The `--opportunity-year 2016` run and
value-identity comparison are no longer a remediation validation.

**Removed from §15 step 5:** The command to run the parameterised
script with `--opportunity-year 2016` and the value-identity
comparison against the un-tagged lookup are removed.

**Removed from §15 step 6:** The step to update all references to
the un-tagged path `FR_gsur_ruro_v2_stageA.parquet` in the canary
and validation scripts is removed from the remediation prompt.

---

## 5. y2016 provenance-lock planning retained

The y2016 provenance-lock planning is retained as a remediation
activity, now expressed as document preparation rather than script
execution.

**Retained in §9:** The lock-plan content — the required sidecar
fields (opportunity year, GSUR column name, input paths, benchmark
value, NUTS vintage, IDF parity difference, benchmark difference,
row count, build timestamp, script version) and the five-step lock
procedure (run, write sidecar, compare value-identically, accept,
retire un-tagged file) — is retained in §9 as the specification for
the construction authorization to follow. The planning work is done
in the remediation; the execution is deferred.

**Retained in §11 A5:** A5 now authorises preparation of the lock-
plan document (`docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`)
containing the §9 specification.

**Retained in §13 O5:** O5 now lists the lock-plan document as a
required remediation output in place of the year-tagged y2016
parquet.

**Retained in §14 V5:** V5 now checks that the lock-plan document
is present and contains the required fields, in place of the sidecar
parse check.

**Retained in §15 step 6 (renumbered):** A new step 6 in the §15
prompt authorises preparation of the lock-plan document, replacing
the now-removed reference-update step.

The K1 provenance-lock requirement is not resolved during the
remediation. K1 will be resolved when the construction authorization
executes the y2016 reproduction per the lock procedure in the lock-
plan document.

---

## 6. Sections revised

| Section | Summary of revision |
|---------|---------------------|
| §4 table and paragraph | y2016 row: "rebuild deferred to construction authorization"; paragraph updated accordingly |
| §7 closing paragraph | Reference updates and retirement: "deferred to the construction authorization" |
| §8 closing | Exception sentence removed; replaced with "No year-tagged lookup parquet is written during the remediation" |
| §9 full body | Rewritten from reproduction-and-retirement to lock-plan documentation: sidecar field list, five-step lock procedure, K1/K3 status, lock-plan document as output |
| §11 A2 | "References updated; file retired" → "deferred to construction authorization" |
| §11 A5 | "Script run with `--opportunity-year 2016`" → "lock-plan document prepared" |
| §12 N1 | "y2016 reproduction is the one bounded exception" → "no GSURv2 lookup construction or reproduction authorized for y2014, y2015, or y2016" |
| §13 O5 | Year-tagged y2016 parquet → lock-plan document |
| §14 V4 | `--opportunity-year 2016` run + value-identity comparison → static/no-write parameterisation check |
| §14 V5 | Sidecar parse check → lock-plan document presence check |
| §14 closing | "V4 reproduces existing lookup" → "No lookup parquet written; value-identity regression deferred" |
| §15 full | Step 5 (`--opportunity-year 2016`) removed; step 6 (reference updates) removed; step 5 replaced with static parameterisation check; step 6 replaced with lock-plan document preparation; "What to do next" updated |

Sections not revised: §1, §2, §3, §5, §6, §10, §11 A1/A3/A4/A6/A7,
§12 N2–N7, §13 O1–O4/O6–O7, §14 V1–V3/V6–V7. All naming decisions,
file-retrieval authorizations, C1–C7 parameterisation authorizations,
O7 sign-off preparation, and not-authorised items are unchanged.

---

## 7. What remains authorized

The following remediation activities are unchanged and remain
authorised.

- **K2 decision implemented (A1):** Config YAML updated from
  `gsur_v2` to `gsur` in `variables_excluded_from_deflation`,
  committed atomically with script changes.
- **C6 scheme decided (A2):** Year-tagged output naming
  (`_y2014`, `_y2015`, `_y2016`) decided and implemented in the
  parameterised script; reference updates and un-tagged file
  retirement deferred to construction authorization.
- **Six external files retrieved (A3):** Eurostat D2 and D1
  denominator files for y2014 and y2015; INSEE benchmark files for
  y2014 and y2015; provenance text files extended.
- **C1–C7 implemented (A4):** Seven parameterisation changes in
  `scripts/enhanced/enh_prepare_FR_gsur_v2.py`, confined to input-
  selection and output-tagging layers, year-invariant logic
  preserved unchanged.
- **y2016 lock plan prepared (A5):** Lock-plan document
  (`docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`) prepared
  with sidecar field specification and lock procedure.
- **O7 sign-off request prepared (A6):** Crosswalk, merge key,
  drgn1 compositions, and merge procedure assembled for user
  decision.
- **Post-remediation validation (A7):** Static parameterisation
  check (V4), lock-plan document check (V5), and all other V1–V7
  checks per §14.

---

## 8. What remains not authorized

The following items are not authorised by the remediation, unchanged
from v1 except where noted.

- **GSURv2 lookup construction or reproduction for any year (N1,
  revised):** Running the parameterised script with
  `--opportunity-year` for y2014, y2015, or y2016 is not authorised.
  This is a strengthening of the v1 N1, which previously excepted
  the y2016 reproduction.
- **Retirement of the un-tagged y2016 file:** Not authorised during
  the remediation; deferred to the construction authorization (new
  in this correction).
- **Reference updates to the un-tagged y2016 path** in the canary
  and validation scripts: Not authorised during the remediation;
  deferred to the construction authorization (new in this
  correction).
- **MNL-parquet rebuilding (N2):** Unchanged.
- **O7 merge check (N3):** Unchanged.
- **Pooled estimation (N4):** Unchanged.
- **Welfare implementation and computation (N5):** Unchanged.
- **Canonical MNL promotion (N6):** Unchanged.
- **Displacement of the M1-clean baseline (N7):** Unchanged.

---

## 9. Whether remediation may proceed

Yes. The revised remediation authorization is internally consistent
with the conservative y2016 provenance-lock approach. The
authorised steps (A1–A7) are all documentation, code-change, or
external-file-retrieval activities; none writes a year-tagged GSURv2
lookup parquet, none runs the construction script, and none retires
or archives any existing data file. The post-remediation validation
(V1–V7) is fully static: it checks files, parses documents, runs
import tests, and verifies path computation, but writes nothing.

The remediation may proceed on the basis of the revised
authorization. The immediate next operational task is the Claude
Code task specified in §15 of the revised memo.

---

## 10. Exact next task

The next task is the Claude Code remediation task specified verbatim
in §15 of `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`
(revised). The task executes eight steps:

1. Retrieve six missing external files (A3, V1–V3).
2. L-vintage check on retrieved denominator files (V2).
3. Implement C1–C7 in `enh_prepare_FR_gsur_v2.py` without running
   the script (A4).
4. Update config YAML from `gsur_v2` to `gsur`, committed
   atomically (A1).
5. Static parameterisation check: imports, `--help`, path
   computation, C7 block presence — no script run, no parquet
   written (V4).
6. Prepare lock-plan document
   `docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` with sidecar
   field specification and lock procedure (A5, V5).
7. Assemble O7 crosswalk sign-off request for user decision (A6).
8. Run post-remediation validation checks V1–V7 and save the
   remediation completion report (A7, O7).

No `--opportunity-year` command is issued. No year-tagged GSURv2
lookup parquet is written. No existing file is retired or archived.
The remediation completion report (O7) is the deliverable that
gates the subsequent construction authorization.