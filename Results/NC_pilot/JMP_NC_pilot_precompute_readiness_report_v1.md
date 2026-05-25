# JMP NC Pilot — Precompute-Readiness Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Readiness Verdict

**PASSED.** All 17 validation checks cleared; no halt condition fired.

The precompute-readiness transformation completed successfully:

- `is_chosen = is_chosen_joint` integer alias added (copy, not move).
- Each `(idhh, year_tag)` group sorted chosen-first (`draw_joint` ascending),
  satisfying `estimation_engine.py:380`'s position-0 invariant.
- Output: 2,319,300 rows × 152 columns.
- No scalar `draw` column created (HC-DRAW clear).
- All 17 validation checks PASS; all HC halt conditions clear.

---

## 2. Authorization Scope

**Authorizing document:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_readiness_amendment_v1.md`

This slice authorizes only:
- Reading the post-EM parquet (read-only).
- Adding the `is_chosen = is_chosen_joint` integer alias.
- Stable chosen-first sort within each `(idhh, year_tag)` group.
- Writing the new `__precompute_ready.parquet` + `__readymeta.json`.
- The §11 validations and this report.

Not authorized by this amendment: GSUR merge, precompute, estimation, welfare,
SA2, promotion, scalar `draw` column creation, or M1-clean displacement. Those
require separate authorizing documents.

**Executing script:** `scripts/pilot/build_precompute_ready.py`
**Wall time:** 12.3 seconds

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_readiness_amendment_v1.md` | Authorizing document; read first |
| `Results/NC_pilot/JMP_NC_pilot_post_em_merge_report_v1.md` | Post-EM merge status confirmation |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet` | Input base (read-only) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em__mergemeta.json` | Merge metadata (income stats, validation record) |
| `Results/NC_pilot/JMP_NC_pilot_draw_joint_repointing_audit_v1.md` | Context for position-0 invariant and downstream assumptions |

---

## 4. Files Created

| File | Description |
|---|---|
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` | 2,319,300 rows × 152 cols; chosen-first sorted; `is_chosen` added |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json` | Metadata sidecar per amendment §10 |
| `scripts/pilot/build_precompute_ready.py` | Transformation script; pilot-only; read-only input |
| `Results/NC_pilot/JMP_NC_pilot_precompute_readiness_report_v1.md` | This report |

---

## 5. Files Modified

None. The post-EM parquet, Stage-4 product parquet, Stage-5 block outputs,
production scripts, and P3a YAML are all unchanged. No production file was
accessed for writing.

---

## 6. Input Post-EM Parquet

| Item | Value |
|---|---|
| Path | `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet` |
| Rows | 2,319,300 |
| Columns | 151 (149 Stage-4 base + `ils_dispy_male` + `ils_dispy_female`) |
| Chosen rows | 2,577 at `draw_male==0 ∧ draw_female==0 ∧ draw_joint==0` |
| `is_chosen` present | No (gap this slice closes) |
| Chosen-first sort | No (gap this slice closes) |
| Confirmed unchanged at validation | Yes (HC1 PASS) |

Pre-checks on load confirmed:
- `is_chosen_joint == 1` iff `draw_joint == 0` on all 2,319,300 rows (PASS).
- `ils_dispy_male` and `ils_dispy_female` non-missing (0 missing each, PASS).
- `draw_joint = 30 * draw_male + draw_female` consistent on all rows (PASS).
- No scalar `draw` column in input (PASS).

---

## 7. Output Precompute-Ready Parquet

| Item | Value |
|---|---|
| Path | `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` |
| Rows | 2,319,300 |
| Columns | 152 (151 post-EM + `is_chosen`) |
| File size | 102,411,500 bytes (~97.7 MB) |
| Compression | Snappy (pyarrow engine) |
| Produced at | 2026-05-23T07:49:57Z |

---

## 8. is_chosen Aliasing

**Rule:** `is_chosen = is_chosen_joint.astype(int)`

- **Copy, not move:** `is_chosen_joint`, `is_chosen_male`, and `is_chosen_female`
  are preserved unchanged in the output.
- **Dtype:** integer (values in {0, 1}).
- **Source:** `is_chosen_joint` — the authoritative joint chosen indicator
  from Stage 3/4 construction, where `is_chosen_joint = 1` iff
  `draw_male == 0 AND draw_female == 0`.
- **Equivalence verified:** `is_chosen == 1` iff `draw_joint == 0` on all
  2,319,300 rows before aliasing (precondition check PASS). After aliasing,
  `is_chosen == is_chosen_joint.astype(int)` on all rows (alias equivalence
  check PASS).
- **Motivation:** `estimation_utils.py` group-builder and ~15 sites in
  `RURO_post_estimation_styled.py` look for a column literally named
  `is_chosen`. The joint-aware `is_chosen_joint` is the correct chosen
  indicator but under a different name; this alias resolves the naming gap
  without altering any choice-set logic.

---

## 9. Chosen-First Sorting

**Sort keys:** `(idhh, year_tag, draw_joint)` ascending, stable.

- This is equivalent to: within each `(idhh, year_tag)` group, sort by
  `draw_joint` ascending, so `draw_joint = 0, 1, 2, …, 899`. Since the chosen
  row is exactly `draw_joint == 0`, it becomes the first row of every group.
- **Stable sort:** `pandas.DataFrame.sort_values(…, kind="stable")` used; row
  order among non-chosen alternatives is deterministic and stable.
- **No rows dropped or duplicated:** row count = 2,319,300 before and after.
- **Motivation:** `estimation_engine.py:380` carries an implicit position-0
  assumption — `V[group_starts[g]]` is taken as the utility of the chosen
  alternative. The re-pointing audit found the pre-sort pilot parquet had the
  chosen row at position 0 in only 175 of 2,577 groups (median position ≈ 465).
  After this sort, all 2,577 groups have the chosen row at position 0.

---

## 10. Grouping Convention

**Group key:** `(idhh, year_tag)`.

For the 2016 couples pilot, `year_tag == 2` for all 2,319,300 rows, so the
key reduces to `idhh` in practice. Keying on `(idhh, year_tag)` is used for
forward-compatibility with the pooled multi-year cycle (where different year
sub-samples for the same household would form separate groups).

| Item | Value |
|---|---|
| Group key | `(idhh, year_tag)` |
| Number of groups | 2,577 |
| Rows per group | 900 (30 × 30) |
| `year_tag` in pilot | 2 (all rows) |

---

## 11. Row-Count Validation

| Check | Expected | Observed | Result |
|---|---|---|---|
| Input rows | 2,319,300 | 2,319,300 | PASS |
| Output rows | 2,319,300 | 2,319,300 | PASS |
| Output columns | 152 | 152 | PASS |

No rows were added, dropped, or duplicated by the transformation.

---

## 12. Group-Size Validation

| Check | Expected | Observed | Result |
|---|---|---|---|
| Number of `(idhh, year_tag)` groups | 2,577 | 2,577 | PASS |
| Rows per group (all groups) | 900 | 900 | PASS |
| Groups with size ≠ 900 | 0 | 0 | PASS |

Every couple-year group has exactly 900 alternatives (30 male draws × 30
female draws). No partial or oversized group exists.

---

## 13. draw_joint Validation

| Check | Expected | Result |
|---|---|---|
| `draw_joint = 30 * draw_male + draw_female` on all rows | True everywhere | PASS |
| `draw_joint` minimum | 0 | PASS |
| `draw_joint` maximum | 899 | PASS |
| Exactly one `draw_joint == 0` per group | 1 per group | PASS |

`draw_male`, `draw_female`, and `draw_joint` are preserved unchanged from the
post-EM input. No scalar `draw` column was created (V17 PASS, HC-DRAW clear).

---

## 14. is_chosen Validation

| Check | Result |
|---|---|
| `is_chosen` column present in output | PASS |
| `is_chosen` values in {0, 1} only | PASS |
| Total `is_chosen == 1` rows | 2,577 (exactly one per group) |
| `is_chosen == 1` iff `draw_joint == 0` (all rows) | PASS |
| `is_chosen == is_chosen_joint.astype(int)` (all rows) | PASS |
| `is_chosen_joint` preserved unchanged | PASS |
| `is_chosen_male` preserved unchanged | PASS |
| `is_chosen_female` preserved unchanged | PASS |

---

## 15. Position-0 Chosen-Row Validation

The critical precondition for `estimation_engine.py:380`:

| Check | Result |
|---|---|
| First row of every group has `draw_joint == 0` | PASS (all 2,577 groups) |
| First row of every group has `is_chosen == 1` | PASS (all 2,577 groups) |

**Before this sort:** the chosen row was at position 0 in only 175 of 2,577
groups (median position ≈ 465), as identified by the draw_joint re-pointing
audit.

**After this sort:** all 2,577 groups have the chosen row at position 0.
The estimation engine's `V[group_starts[g]]` extraction will correctly read
the chosen-alternative utility for every couple.

---

## 16. Income-Column Validation

| Column | Missing rows | Mean (EUR/mo) | Std | Min | Max |
|---|---|---|---|---|---|
| `ils_dispy_male` | 0 | 2,017.45 | 1,377.11 | -2,149.51 | 15,237.52 |
| `ils_dispy_female` | 0 | 2,036.83 | 1,333.05 | -1,576.10 | 13,480.52 |

Values are identical to the post-EM input (the sort does not alter values,
only row order). No household-total income column (`ils_dispy_hh_derived` or
similar) was created (V14 PASS). The 8 W1 log-proposal-density columns
(`log_q_wage_male_pilot`, `log_q_wage_female_pilot`, `log_q_E_*`,
`log_q_H_*`, `log_q_Occ_*`, `log_q_W_*`) are all present and unchanged
(HC-PRESERVE PASS).

---

## 17. Production-Safety Validation

| Check | Result |
|---|---|
| Post-EM parquet unchanged (2,319,300 × 151) | PASS (HC1) |
| Stage-4 product parquet untouched | PASS |
| Stage-5 block outputs untouched | PASS |
| No production P3a script modified | PASS |
| No P3a YAML modified | PASS |
| No production data file modified | PASS |
| Singles production parquet unaffected | PASS |

---

## 18. Metadata Sidecar

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json`

Records: authorization document; input path + row/col count; `is_chosen` alias
rule (dtype int, copy-not-move, equivalence verified); grouping key
`(idhh, year_tag)` and sort rule (`draw_joint` ascending, stable); output path,
row count (2,319,300), column count (152), file bytes (102,411,500); all 17
validation results; explicit confirmation that no scalar `draw` column exists
and that `draw_male`/`draw_female`/`draw_joint` are the only draw identifiers;
income column statistics; `not_run` flags (GSUR/precompute/estimation/welfare/
SA2/promotion/M1_clean_displacement = false); stage status (M1-clean 2016
active, P3a unaffected).

---

## 19. Halt-Condition Status

| Code | Condition | Fired? |
|---|---|---|
| HC1 | Overwrite of post-EM parquet or any prior pilot/production artifact | No |
| HC-DRAW | Scalar `draw` column created or `draw = draw_joint` alias performed | No |
| HC-CHOSEN | `is_chosen == 1` not exactly once per group, or not iff `draw_joint == 0`, or first row not chosen | No |
| HC-GROUP | Any group size ≠ 900, or total row count ≠ 2,319,300 | No |
| HC-PRESERVE | Any change to `ils_dispy_*`, W1 columns, or draw identifiers; dropped/duplicated rows | No |
| HC-STAGE | GSUR, precompute, estimation, welfare, SA2, promotion, or M1-clean displacement | No |

No halt condition fired. All 17 validation checks PASSED.

---

## 20. What Was Not Executed

The following were explicitly not performed:

- No EUROMOD run.
- No GSUR merge.
- No precompute.
- No MNL estimation.
- No welfare computation.
- No SA2 issuance.
- No canonical promotion of pilot to production.
- No scalar `draw` column or `draw = draw_joint` alias created.
- No `is_chosen_joint`/`is_chosen_male`/`is_chosen_female` renamed or removed.
- No `ils_dispy_*` or W1 column values altered.
- No M1-clean 2016 displacement.

---

## 21. Whether GSUR Merge Authorization Is Now Ready

The precompute-readiness parquet does **not** require a GSUR re-merge before
pilot precompute can proceed. The post-EM merge (merge report v1) already
incorporated the EUROMOD disposable-income outputs; GSUR is a production
step that reweights survey records. For the NC pilot, GSUR was not run at
any prior stage (all prior GSUR columns are carried from the production
diagonal parquet via Stage 3/4). A GSUR re-merge for the pilot would require
a separate authorizing document and is **not** a precondition for piloting
the precompute/estimation logic on the existing product parquet.

**Status:** GSUR merge not authorized by this amendment; not a blocker for
the next precompute slice.

---

## 22. Whether Precompute Is Authorized

**Not yet authorized.** This slice closes the two precompute preconditions
identified in the re-pointing audit (`is_chosen` alias + chosen-first sort).
Precompute itself requires:

1. A separate precompute-slice amendment naming the exact precompute
   script, input path, and output path.
2. Resolution of any remaining `draw_joint` re-pointing gaps in the
   precompute utilities (`estimation_utils.py` group-builder for couples,
   which currently reads the scalar `draw` column to identify groups).
3. Confirmation that the scalar `draw` compatibility question is addressed
   (either by a `draw = draw_joint` alias — requiring its own HC-DRAW
   authorization — or by patching `estimation_utils.py` to accept
   `draw_joint`).

The precompute-ready parquet produced here satisfies the positional and
naming preconditions. The scalar-`draw` compatibility gap is the remaining
open item before a precompute run is possible.

---

## 23. Whether Welfare Computation Is Authorized

**No.** Welfare computation requires a completed MNL estimation (estimated
preference parameters) and is downstream of precompute. It is not authorized
by this amendment and is not a task for the current or immediately next slice.

---

## 24. Whether M1-Clean Remains Active

**Yes.** M1-clean 2016 is the active production baseline and is unaffected by
this pilot slice. No production data, production scripts, or P3a YAML files
were modified. The corrected pooled P3a track (1,244,500 rows, Stage M1 P3a
construction complete 2026-05-20) is unaffected.

---

## 25. Immediate Next Task

The immediate next task is a **scalar `draw` compatibility resolution** —
either:

- **(A) HC-DRAW authorization:** Obtain authorization for a `draw = draw_joint`
  alias column to be added to the precompute-ready parquet, resolving the
  `estimation_utils.py` group-builder's expectation of a scalar `draw` column
  without patching production code.
- **(B) Code patch:** Patch `estimation_utils.py`'s couples group-builder to
  accept `draw_joint` in place of the scalar `draw` column (requires a code-
  modification authorization for `estimation_utils.py`).

Once the scalar-`draw` gap is resolved, the next authorized action is the
precompute slice using the precompute-ready parquet as input and the existing
`estimation_utils.py` precompute entry point.

---

## Required Final Statements

- **The precompute-readiness slice PASSED.** All 17 validation checks cleared;
  no halt condition fired.

- **No EUROMOD was run.**

- **No GSUR merge was run.**

- **No precompute was run.**

- **No estimation was run.**

- **No welfare was computed.**

- **No SA2 was issued.**

- **M1-clean 2016 remains the active baseline.** No production data or scripts
  were modified.

- **The corrected pooled P3a track is unaffected.** No P3a files were touched.

- **This amendment authorizes only the precompute-readiness transformation** —
  an `is_chosen = is_chosen_joint` integer alias and a chosen-first sort,
  producing a new pilot-only parquet at
  `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet`.

- **No scalar `draw` column was created.** `draw_male`, `draw_female`, and
  `draw_joint` remain the only draw identifiers. A scalar-`draw` compatibility
  alias requires separate later authorization (HC-DRAW).

- **Chosen row = `draw_joint == 0` is relabeled (`is_chosen == 1`) and moved to
  position 0 of each `(idhh, year_tag)` group.** Exactly one per couple (2,577
  total); `is_chosen == 1` iff `draw_joint == 0` everywhere; all 900
  alternatives per couple preserved.

- **`ils_dispy_male`/`ils_dispy_female`, the W1 columns, and the draw
  identifiers are preserved unchanged.** The post-EM parquet is not overwritten.

- **Output = 2,319,300 rows × 152 columns.** No GSUR, precompute, estimation,
  welfare, SA2, or promotion.

---

*Status: precompute-readiness report v1. Transformation PASSED; all HC checks
clear. Immediate next item: scalar `draw` compatibility resolution (§25), then
precompute slice.*
