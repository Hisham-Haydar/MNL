# JMP GSURv2 Multi-Year Extension — Readiness Re-Audit v1

*France 2014–2015–2016 | v1 | 2026-05-20*

Interpreter used for all static checks: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`)

Reference: `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`
§14 (validation checks V1–V7)

---

## 1. Re-audit verdict

**READY FOR GSURv2 CONSTRUCTION**

All seven post-remediation validation checks (V1–V7 per authorization §14)
pass. All remediation outputs required before construction authorization
(O1–O5) are present and verified. No blocking item remains.

Construction authorization is recommended as option **B — y2016 provenance
lock plus y2014/y2015 construction in one controlled construction task**,
scoped to Stage A lookup production only. MNL parquet rebuild, pooled
estimation, and welfare computation remain separately gated and are not
authorized by this re-audit.

---

## 2. What changed since the failed audit

The original implementation audit
(`docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md`)
returned **NOT READY — CODE CHANGES REQUIRED** with eight failing or
flagged conditions. All eight have been resolved by the remediation work
committed between 2026-05-20 and 2026-05-20.

| Condition | Audit verdict | Remediation action | Re-audit verdict |
|-----------|--------------|-------------------|-----------------|
| A1 — FR_gsur.xlsx covers 2014–2016 | PASS | No change required | PASS |
| A2 — y2014/y2015 D2/D1 denominator files | FAIL (absent) | Retrieved via Eurostat SDMX-CSV API; committed `e4dd6c2` | PASS |
| A3 — y2014/y2015 INSEE benchmark CSVs | FAIL (absent) | Retrieved via INSEE BDM API; committed `e4dd6c2` | PASS |
| A4 — NUTS-2016 vintage of retrieved files | CONDITIONAL | Confirmed PASS at retrieval: all geo codes FR10…FRM0 (NUTS-2016) | PASS |
| A5/K1 — y2016 sidecar JSON absent | FAIL | Lock plan prepared (O5, commit `1f3e6b7`); sidecar deferred to construction | PASS (plan ready) |
| A5/K2 — y2016 column-name inconsistency | FLAG | `gsur` retained; `gsur_v2` removed from config; committed `178ca72` | PASS |
| A5/K3 — O7 crosswalk sign-off pending | FAIL | Sign-off request document present; O7 sign-off itself still pending (gates MNL merge, not lookup construction) | PASS for construction; PENDING for MNL merge |
| A6 — C1–C7 script parameterisation | FAIL (all unimplemented) | All seven changes implemented and committed `178ca72`; static V4a/V4b/V4c PASS | PASS |

**Commits that resolve the audit failures:**

| Commit | Content |
|--------|---------|
| `cc77b0a` | Authorization memo revised to conservative y2016 provenance-lock approach |
| `372237b` | Residual `--opportunity-year 2016` invocation removed from auth memo V4/V7/§15 |
| `e4dd6c2` | All 6 external files retrieved; provenance text files extended |
| `df873d0` | External file remediation report |
| `178ca72` | C1–C7 implemented; K2 config updated; static validation PASS |
| `d29052a` | Documentation fixes: venv interpreter, commit references corrected |
| `1f3e6b7` | y2016 provenance lock plan (O5) |
| `f1f5779` | Lock plan authorization wording and next-task sequencing corrected |

Working tree is clean. No uncommitted changes.

---

## 3. External files readiness

**Verdict: ALL PRESENT — PASS**

All 12 external input files required for construction across all three
opportunity years are present in `Data/external/` and have correct sizes.

| File | Size (bytes) | Role | Status |
|------|-------------|------|--------|
| `FR_gsur.xlsx` | 1,077,164 | Unemployment rates 2007–2019 (A1) | PRESENT |
| `fr_drgn1_to_nuts2_crosswalk.csv` | 768 | drgn1→NUTS2 mapping, 22 rows | PRESENT |
| `lfst_r_lfsd2pop_FR_2014.tsv` | 357,116 | D2 operative denominator, y2014 | PRESENT |
| `lfst_r_lfp2acedu_FR_2014.tsv` | 88,241 | D1 diagnostic denominator, y2014 | PRESENT |
| `insee_001688526_2014.csv` | 479 | Benchmark CSV y2014 (9.9%) | PRESENT |
| `lfst_r_lfsd2pop_FR_2015.tsv` | 354,590 | D2 operative denominator, y2015 | PRESENT |
| `lfst_r_lfp2acedu_FR_2015.tsv` | 87,404 | D1 diagnostic denominator, y2015 | PRESENT |
| `insee_001688526_2015.csv` | 484 | Benchmark CSV y2015 (10.025%) | PRESENT |
| `lfst_r_lfsd2pop_FR_2016.tsv` | 357,080 | D2 operative denominator, y2016 | PRESENT |
| `lfst_r_lfp2acedu_FR_2016.tsv` | 88,055 | D1 diagnostic denominator, y2016 | PRESENT |
| `insee_001688526_2016.csv` | 477 | Benchmark CSV y2016 (9.725%) | PRESENT |
| `FR_gsur_ruro_v2_stageA.parquet` | 7,444 | Existing un-tagged y2016 lookup (untracked) | PRESENT |

**NUTS-2016 vintage (A4):** confirmed PASS for y2014 and y2015 at
retrieval (external file remediation report §6). All geo codes are the
22 NUTS-2016 metropolitan France codes (FR10…FRM0), matching the
crosswalk. No NUTS-vintage conversion is required.

**Benchmark values (A3):**

| Year | Annual average | Source | C5 value |
|------|---------------|--------|----------|
| 2014 | 9.900% | INSEE BDM 001688526, mean(9.8, 9.8, 9.9, 10.1) | 9.9 |
| 2015 | 10.025% | INSEE BDM 001688526, mean(10.0, 10.2, 10.0, 9.9) | 10.025 |
| 2016 | 9.725% | INSEE BDM 001688526, mean(9.9, 9.7, 9.6, 9.7) | 9.725 |

All quarterly values carry `obs_status=A` (final, accepted by INSEE).

---

## 4. Script parameterisation readiness

**Verdict: ALL C1–C7 IMPLEMENTED — PASS**

Static validation checks V4a, V4b, V4c all run and all pass. No script
was invoked with `--opportunity-year`.

**V4a — Import without error:**
```
.venv\Scripts\python.exe -c "import scripts.enhanced.enh_prepare_FR_gsur_v2; print('IMPORT: OK')"
```
Result: `IMPORT: OK`

**V4b — `--help` lists `--opportunity-year`:**
```
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --help
```
Output confirms `--opportunity-year YEAR` listed as required argument.

**V4c — Source-inspection checks (19 checks, all PASS):**

| Check | Result |
|-------|--------|
| C1 argparse `--opportunity-year` | PASS |
| C1 `global YEAR` set in `main()` | PASS |
| C3 D2 f-string `lfst_r_lfsd2pop_FR_{YEAR}.tsv` | PASS |
| C4 D1 f-string `lfst_r_lfp2acedu_FR_{YEAR}.tsv` | PASS |
| C5 benchmark f-string `insee_001688526_{YEAR}.csv` | PASS |
| C6 OUT template `FR_gsur_ruro_v2_stageA_y{YEAR}.parquet` | PASS |
| C6 SIDECAR template `FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json` | PASS |
| C6 `OUT = None` at module level | PASS |
| C6 `SIDECAR = None` at module level | PASS |
| C7 `json.dump` sidecar write present | PASS |
| C7 `opportunity_year` field | PASS |
| C7 `gsur_column_name` field | PASS |
| C7 `build_timestamp` field | PASS |
| C7 `script_version` field | PASS |
| No hardcoded un-tagged `FR_gsur_ruro_v2_stageA.parquet` | PASS |
| `import argparse` | PASS |
| `import json` | PASS |
| `import datetime` | PASS |
| `import subprocess` | PASS |

**Module-level state confirmed:**
- `YEAR = 2016` (guard default; overridden in `main()`)
- `BENCHMARK_PCT = 9.725` (guard default; overridden in `main()`)
- `OUT = None` (set in `main()` from `--opportunity-year`)
- `SIDECAR = None` (set in `main()` from `--opportunity-year`)

**V7 — Year-invariant logic preservation:** C1–C7 changes are confined to
the input-selection and output-tagging layers (argparse block, CSV read,
path assignments, sidecar write at the end of `main()`). The
population-weighted aggregation, education alignment, Y20-64 age-band
selection, drgn1=9 stub handling, IDF parity check, benchmark validation,
and 11-column output schema are all untouched. Confirmed by source
inspection at commit `178ca72`.

---

## 5. K2 naming decision status

**Verdict: RESOLVED — PASS**

Active column name: `gsur` (confirmed in script and lookup parquet).

Config check result:
```
variables_excluded_from_deflation: ['dgn', 'dag', 'dms', 'deh', 'drgn1', 'idhh',
  'idperson', 'idorighh', 'idorigperson', 'dwt', 'gsur', 'year_tag', 'year',
  'tpr', 'stacked_hh_uid', 'stacked_person_uid', 'cluster_id']
gsur in list: True
gsur_v2 in list: False
```

The K2 mismatch (audit R4) is resolved: `gsur` is in the deflation-
exclusion list; `gsur_v2` is absent. The GSUR proportion will be correctly
excluded from CPI deflation at MNL-merge time.

Sidecar field `gsur_column_name` in the C7 block records `"gsur"` as the
active column name, making the K2 decision explicit and auditable per-build.

---

## 6. C6 output naming status

**Verdict: RESOLVED — PASS**

The parameterised script writes year-tagged output paths:
- `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json`

No year-tagged parquet or sidecar has been written yet (construction is not
yet authorized). The existing un-tagged file
`FR_gsur_ruro_v2_stageA.parquet` is present and will be retired at Step 7
of the lock procedure (lock plan §8) once the year-tagged y2016 file is
produced and value-identity-verified.

Current state of Data/external/ year-tagged files:

| File | Exists? |
|------|---------|
| `FR_gsur_ruro_v2_stageA_y2014.parquet` | No — not yet built |
| `FR_gsur_ruro_v2_stageA_y2014__sidecar.json` | No — not yet built |
| `FR_gsur_ruro_v2_stageA_y2015.parquet` | No — not yet built |
| `FR_gsur_ruro_v2_stageA_y2015__sidecar.json` | No — not yet built |
| `FR_gsur_ruro_v2_stageA_y2016.parquet` | No — deferred to construction |
| `FR_gsur_ruro_v2_stageA_y2016__sidecar.json` | No — deferred to construction |

This is the expected state at re-audit time. All six files will be produced
by the construction authorization.

---

## 7. y2014 construction readiness

**Verdict: INPUTS READY — awaiting construction authorization**

All inputs required for `--opportunity-year 2014` are present and verified:

| Input | File | Status |
|-------|------|--------|
| Unemployment rates (C2) | `Data/external/FR_gsur.xlsx` | PRESENT — covers 2007–2019 |
| D2 denominator (C3) | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | PRESENT — 357,116 bytes; NUTS-2016; Y20-64 operative band available |
| D1 denominator (C4) | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | PRESENT — 88,241 bytes; NUTS-2016; diagnostic only (broad age bands) |
| Benchmark CSV (C5) | `Data/external/insee_001688526_2014.csv` | PRESENT — 479 bytes; BENCHMARK_PCT=9.9; all quarterly obs_status=A |
| Crosswalk | `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | PRESENT — 22 rows; all verified_against_eurostat=YES |

**BENCHMARK_PCT for y2014:** 9.9 (simple mean of Q1–Q4 2014 quarterly SA
values: 9.8, 9.8, 9.9, 10.1).

**Suppression pattern:** The FRM0 (Corse) and NRP suppression patterns at
Y20-64 are year-invariant. The same D3 (approximate_uniform) fallback with
reviewer sign-off that handles FRM0 in y2016 applies to y2014 — no new
suppression behaviour. FRI2 (Limousin) is the second-most suppressed region
in 2014 (53 cells), same as 2016. No empty OBS_VALUE cells among the
usable ED0-2/ED3_4/ED5-8 operative cells at Y20-64 except in FRM0 and FRI2.

**Blocker:** none for input readiness. Construction is gated solely on the
construction authorization memo (not yet produced).

---

## 8. y2015 construction readiness

**Verdict: INPUTS READY — awaiting construction authorization**

All inputs required for `--opportunity-year 2015` are present and verified:

| Input | File | Status |
|-------|------|--------|
| Unemployment rates (C2) | `Data/external/FR_gsur.xlsx` | PRESENT — covers 2007–2019 |
| D2 denominator (C3) | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | PRESENT — 354,590 bytes; NUTS-2016; Y20-64 operative band available |
| D1 denominator (C4) | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | PRESENT — 87,404 bytes; NUTS-2016; diagnostic only |
| Benchmark CSV (C5) | `Data/external/insee_001688526_2015.csv` | PRESENT — 484 bytes; BENCHMARK_PCT=10.025; all quarterly obs_status=A |
| Crosswalk | `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | PRESENT — 22 rows; all verified_against_eurostat=YES |

**BENCHMARK_PCT for y2015:** 10.025 (simple mean of Q1–Q4 2015 quarterly SA
values: 10.0, 10.2, 10.0, 9.9).

**Suppression pattern:** Identical year-invariant FRM0/NRP pattern. FRM0
all ED cells at Y20-64 flagged `u` in 2015 — same D3 fallback applies.
Y20-64 operative band: 326 rows, 70 suppressed (21.5%), 6 empty OBS_VALUE
(2016 reference: 330 rows, 73 suppressed, 12 empty). No new suppression
behaviour.

**Blocker:** none for input readiness. Construction gated on construction
authorization only.

---

## 9. y2016 provenance-lock readiness

**Verdict: LOCK PLAN READY — awaiting construction authorization**

The y2016 lock plan document is present, complete, and verified:

- **File:** `docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`
  (23,882 bytes; corrected by `docs/JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md`)
- **All 14 required sidecar fields specified:** PASS (verified by source
  inspection — all 14 field names present in lock plan §4)
- **All 9 lock procedure steps present:** PASS (Steps 1–9 confirmed present)
- **Post-hoc vs rebuild analysis:** §5 rules out post-hoc; §6 confirms
  rebuild is the preferred and correct approach
- **O7 sign-off scope clarified:** §7 specifies O7 gates MNL merge only,
  not the y2016 lookup rebuild

**Value-identity baseline recorded in lock plan §8 Step 2:**
- Existing un-tagged parquet SHA-256:
  `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`
- Size: 7,444 bytes; 54 rows; 11 columns

The construction authorization run for y2016 must produce a year-tagged
parquet whose `gsur` column values are value-identical (max absolute
difference = 0.0) to the existing un-tagged parquet. This identity check
is the primary quality gate for y2016.

**K1 status:** RESOLVED AT CONSTRUCTION TIME — the C7 sidecar block writes
`FR_gsur_ruro_v2_stageA_y2016__sidecar.json` automatically when the script
runs; no additional action needed.

---

## 10. O7 crosswalk sign-off readiness

**Verdict: REQUEST DOCUMENT READY — sign-off itself still PENDING**

The O7 sign-off request document is present:
`docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` (12,880 bytes).

O7 requires the user's explicit approval of:
1. `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` (22 rows; all
   `verified_against_eurostat=YES`)
2. Merge key `(drgn1, educ3, sex)`

**O7 does NOT block GSURv2 lookup construction.** It gates only the MNL
parquet merge step, which is downstream of the lookup construction and
requires its own separate authorization. The construction authorization
(which covers only lookup production) may be issued and executed without
O7 sign-off.

**O7 DOES block MNL parquet rebuild.** The MNL merge — replacing v1 GSUR
fallback rates in the FR_2015/FR_2016/FR_2017 parquets with GSURv2 rates —
cannot proceed until O7 is signed off. The construction authorization must
explicitly exclude MNL parquet rebuild for this reason.

The O7 sign-off request has been assembled and is ready for the user's
decision at any time.

---

## 11. Remaining blockers

**None that block GSURv2 lookup construction.**

| Item | Status | Blocks what? |
|------|--------|-------------|
| Construction authorization memo | Not yet produced | Lookup construction for all three years |
| O7 crosswalk sign-off | Pending user decision | MNL parquet merge only — does NOT block lookup construction |
| MNL parquet rebuild | Not yet authorized | Downstream of lookup + O7 sign-off |
| Pooled estimation | Not yet authorized | Downstream of MNL rebuild |
| Welfare | Not yet authorized | Downstream of estimation |

No external file is missing. No script change is required. No naming
decision is unresolved. No static validation check fails.

The sole remaining gate for GSURv2 lookup construction is the construction
authorization memo.

---

## 12. Whether GSURv2 construction is now authorized

**No.** This re-audit establishes that all preconditions are met and that
construction is **ready to be authorized**. The re-audit is not itself
an authorization. A separate construction authorization memo is required.

The authorization state of each action:

| Action | Authorization state |
|--------|---------------------|
| Run `--opportunity-year 2016` (y2016 lock) | REQUIRES construction authorization memo |
| Run `--opportunity-year 2014` (y2014 build) | REQUIRES construction authorization memo |
| Run `--opportunity-year 2015` (y2015 build) | REQUIRES construction authorization memo |
| Retire un-tagged `FR_gsur_ruro_v2_stageA.parquet` | REQUIRES construction authorization (Step 7 of lock procedure) |
| MNL parquet rebuild | NOT AUTHORIZED — additionally requires O7 sign-off |
| Pooled estimation | NOT AUTHORIZED |
| Welfare computation | NOT AUTHORIZED |

The re-audit finding is: **all construction preconditions are met; construction
authorization may now be issued**.

---

## 13. If not authorized, exact remaining fixes

Not applicable — the re-audit verdict is READY FOR GSURv2 CONSTRUCTION.

There are no remaining code fixes, no missing files, and no unresolved
decisions. The only item between the current state and construction is the
construction authorization memo itself, which is a governance document, not
a technical fix.

---

## 14. If authorized, exact construction scope

The construction authorization must cover the following, and only the
following.

**Authorized scope (Option B — all three years in one controlled task):**

The recommended scope is Option B: y2016 provenance lock plus y2014/y2015
construction in one controlled construction task. The rationale for Option B
over Option A (y2016 only) is:

- All three years share the same inputs (crosswalk, workbook), the same
  script version (commit `178ca72`), and the same construction logic. Running
  them in sequence under one authorization produces three consistent, co-dated
  lookups with matching sidecar provenance.
- The y2016 value-identity check is the empirical gate. If it passes,
  y2014 and y2015 can proceed immediately under the same authorization
  without a second round-trip.
- Option A would require a second construction authorization memo for y2014
  and y2015, adding unnecessary overhead when the conditions are identical.

**Exact commands to be authorized:**

```
# Step 1 — y2016 provenance lock (value-identity gate)
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016

# Step 2 — y2015 construction (conditional on y2016 value-identity PASS)
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2015

# Step 3 — y2014 construction (conditional on y2016 value-identity PASS)
.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2014
```

**y2016 value-identity check is a mandatory gate:** if
`FR_gsur_ruro_v2_stageA_y2016.parquet` does not match
`FR_gsur_ruro_v2_stageA.parquet` column-wise (max absolute `gsur` diff = 0.0),
the y2015 and y2014 runs must NOT proceed and the construction authorization
is halted for diagnosis.

**Pass criteria per year:**

| Year | Row count | Sidecar `benchmark_pct` | IDF parity (drgn1=1) | Additional |
|------|-----------|------------------------|----------------------|------------|
| 2016 | 54 | 9.725 | diff = 0.000000 | Value-identical to un-tagged baseline |
| 2015 | 54 | 10.025 | diff = 0.000000 | — |
| 2014 | 54 | 9.9 | diff = 0.000000 | — |

**Post-construction steps authorized under the same task:**
1. Commit all three parquets and sidecars to git.
2. Retire the un-tagged `FR_gsur_ruro_v2_stageA.parquet` to
   `Data/external/archive/` via `git mv`.
3. Update references to the un-tagged path in canary and validation scripts
   to the year-tagged y2016 path.

**Explicitly NOT authorized under the construction scope:**
- MNL parquet rebuild (additionally requires O7 sign-off and separate authorization)
- Pooled estimation
- Welfare computation
- Canonical promotion of any file
- Modification of the construction script beyond what is already committed

---

## 15. Exact next task

The exact next task is the **GSURv2 construction authorization memo**.

It must be a standalone document (e.g.
`docs/JMP_GSURv2_construction_authorization_v1.md`) that:

1. Cites this re-audit (`docs/JMP_GSURv2_multi_year_extension_readiness_reaudit_v1.md`)
   as the basis for the READY verdict and confirms all preconditions are met.

2. Explicitly authorizes running the parameterised script for all three
   years in the order: y2016 first (provenance lock + value-identity gate),
   then y2015, then y2014.

3. States the y2016 value-identity check as a mandatory pass/fail gate:
   max absolute `gsur` difference vs. the un-tagged baseline must be 0.0
   (within floating-point representation tolerance); any non-zero difference
   halts the construction and requires diagnosis.

4. Specifies the sidecar inspection checks per year (14 fields; benchmark_pct
   per §3 of this re-audit; row_count = 54; idf_parity_difference ≈ 0.0).

5. Authorizes the post-construction retirement of the un-tagged parquet
   (Step 7 of the lock procedure, §8 of the lock plan) and the reference
   updates (Step 8).

6. Explicitly does NOT authorize MNL parquet rebuild, pooled estimation, or
   welfare computation.

7. Specifies the interpreter: `.venv\Scripts\python.exe`.

**Recommended phrasing for the construction task prompt (to be included in
the construction authorization memo):**

> Run the following commands in order.
>
> 1. `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2016`
> 2. Perform the value-identity check: compare
>    `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` column-wise against
>    `Data/external/FR_gsur_ruro_v2_stageA.parquet`. Confirm max absolute
>    `gsur` difference = 0.0 (or machine epsilon). If not: HALT.
> 3. Inspect `FR_gsur_ruro_v2_stageA_y2016__sidecar.json`: confirm all 14
>    fields present, `opportunity_year=2016`, `benchmark_pct=9.725`,
>    `row_count=54`.
> 4. `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2015`
> 5. Inspect y2015 sidecar: `benchmark_pct=10.025`, `row_count=54`.
> 6. `.venv\Scripts\python.exe scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year 2014`
> 7. Inspect y2014 sidecar: `benchmark_pct=9.9`, `row_count=54`.
> 8. Commit all three parquets and sidecars.
> 9. Retire `FR_gsur_ruro_v2_stageA.parquet` via `git mv` to `Data/external/archive/`.
> 10. Update references to the un-tagged path in canary/validation scripts.
>
> Do NOT rebuild MNL parquets. Do NOT run pooled estimation. Do NOT compute
> welfare. Do NOT modify the construction script.