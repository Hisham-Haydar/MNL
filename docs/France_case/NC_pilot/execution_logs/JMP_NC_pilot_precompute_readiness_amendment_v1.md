# JMP NC Pilot — Precompute-Readiness Amendment v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: precompute-readiness transformation, narrow.** Authorizes
only the addition of an explicit `is_chosen = is_chosen_joint` alias and a
chosen-first sort on the post-EM pilot product parquet, producing a new
pilot-only precompute-ready file. It does **not** run GSUR, precompute,
estimation, welfare, SA2, or promotion, and does **not** create a scalar
`draw` column. M1-clean 2016 remains active. The corrected pooled P3a track is
unaffected.

---

## 1. Purpose

To make the post-EM pilot product parquet consumable by the downstream
precompute step's two implicit conventions — a single `is_chosen` column and a
chosen-row-first ordering within each choice set — without altering any data
values, the draw identifiers, or the choice-set content. This is a pure
relabel-and-reorder transformation: add `is_chosen` as an integer alias of the
existing `is_chosen_joint`, and sort so the chosen row leads each group.

---

## 2. Current post-EUROMOD status

The merge slice passed (mergemeta v1, 17.5 s):

- Output `fr_pilot_nc_2016_couples_product__post_em.parquet`: **2,319,300 rows**,
  151 columns (149 base + `ils_dispy_male` + `ils_dispy_female`).
- Both income columns non-missing (0 missing each); means ≈2,017 (male) /
  ≈2,037 (female).
- `draw_joint = 30·draw_male + draw_female` consistent on all rows (HM7 PASS).
- Exactly **2,577** chosen rows at `draw_male==0 ∧ draw_female==0 ∧
  draw_joint==0` (HM8 PASS).
- Partner mapping one-to-one (HM4 PASS); merged on true IDs (HM2 PASS).
- No `is_chosen` alias, no chosen-first sort, no GSUR/precompute/estimation/
  welfare/SA2/promotion.

The post-EM parquet carries `is_chosen_joint`/`is_chosen_male`/
`is_chosen_female` but **not** a single `is_chosen` column, and is **not**
sorted chosen-first. Those are exactly the two gaps this slice closes.

---

## 3. Why this slice is needed

The `draw_joint` re-pointing audit identified two implicit downstream
assumptions the pilot parquet does not yet satisfy:

1. **Single `is_chosen` column.** The chosen-column priority chain in
   `estimation_utils.py` and the ~15 sites in `RURO_post_estimation_styled.py`
   expect a column literally named `is_chosen`. The pilot's joint-aware
   `is_chosen_joint` is the correct chosen indicator but under a different
   name. An explicit alias resolves this without touching the joint logic.
2. **Chosen-row-first ordering.** `estimation_engine.py:380` carries an
   implicit position-0 chosen-row assumption — the chosen alternative must be
   the first row in its choice-set group. The merge slice preserved the
   product ordering but did not enforce chosen-first.

Both are precompute *preconditions*, not the precompute itself. They are a
deterministic transform with no estimation content, so they get their own
narrow, validated slice rather than being smuggled into a precompute run.

---

## 4. Input post-EM parquet (base)

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet`
— 2,319,300 rows, 151 columns, with `idhh`, `year_tag`, `draw_male`,
`draw_female`, `draw_joint`, `is_chosen_joint`/`is_chosen_male`/
`is_chosen_female`, `ils_dispy_male`, `ils_dispy_female`, the W1
wage/proposal-density columns, and the per-partner attribute columns.
**Read-only base; never overwritten** (HC1). The slice writes a new file (§9).

---

## 5. Required chosen-row convention

The chosen alternative for each couple is the joint baseline:
`draw_male == 0 AND draw_female == 0`, equivalently `draw_joint == 0`. Exactly
one such row exists per couple (2,577 total, merge-confirmed). This slice does
not redefine the chosen row; it relabels it (`is_chosen`) and repositions it
(first in group). `is_chosen_joint` is the authoritative source for the alias;
the slice must verify `is_chosen_joint == 1` ⇔ `draw_joint == 0` before
aliasing (§11).

---

## 6. is_chosen aliasing rule

Add a new integer/binary column **`is_chosen = is_chosen_joint`**, cast to
`int` (values in {0, 1}). The alias is a copy, not a move:
`is_chosen_joint`/`is_chosen_male`/`is_chosen_female` are **preserved**
unchanged. No other chosen-indicator column is created or renamed. After
aliasing, exactly one `is_chosen == 1` per couple (2,577 total), and
`is_chosen == 1` ⇔ `draw_joint == 0` on every row.

---

## 7. chosen-first sorting rule

Within each choice-set group (§8), sort so the chosen row (`draw_joint == 0`)
is the **first** row of the group. The remaining 899 alternatives follow in a
**deterministic, stable** order — sort by `draw_joint` ascending within the
group, so the full within-group order is `draw_joint = 0, 1, 2, …, 899`
(which automatically puts the chosen row first since it is `draw_joint == 0`).
Stable sort; no row dropped, none duplicated; only row order changes. Group
order in the file (which couple comes first) is not constrained beyond being
deterministic.

---

## 8. Grouping convention

The choice-set group is **`(idhh, year_tag)`**. For the 2016 couples pilot,
`year_tag == 2` for all rows, so the group reduces to `idhh`, but the slice
keys on `(idhh, year_tag)` for forward-compatibility with the pooled cycle.
Every group has exactly **900** rows (HC group-size check, §11). The chosen-row
position-0 requirement (§7) is enforced per `(idhh, year_tag)` group.

---

## 9. Required output parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet`
— the post-EM parquet's 151 columns **plus** `is_chosen`, **2,319,300 rows**,
sorted chosen-first within each `(idhh, year_tag)` group. Pilot-only path; the
post-EM parquet is **not** overwritten (HC1).

Preserved unchanged (values and presence): `ils_dispy_male`,
`ils_dispy_female`; the W1 wage / log-proposal-density columns;
`draw_male`, `draw_female`, `draw_joint`; `is_chosen_joint`/`is_chosen_male`/
`is_chosen_female`; all per-partner attribute columns.

**No scalar `draw` column is created** (HC-DRAW). `draw_male`, `draw_female`,
`draw_joint` remain the only draw identifiers. Any scalar-`draw` compatibility
alias is a separate later authorization.

---

## 10. Required metadata sidecar

`fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json` recording:
authorization (this amendment); input post-EM parquet path + row count; the
`is_chosen = is_chosen_joint` alias (dtype int, copy not move); the grouping
key `(idhh, year_tag)` and the chosen-first sort rule (`draw_joint` ascending);
output path, row count (2,319,300), column count (152 = 151 + `is_chosen`);
the §11 validation results; explicit confirmation that **no scalar `draw`
column exists**; and not_run flags (GSUR/precompute/estimation/welfare/SA2/
promotion = false). M1-clean active; P3a unaffected.

---

## 11. Required validation checks

- **Row count** = 2,319,300 (unchanged from input).
- **Group size** = 900 for every `(idhh, year_tag)` group (2,577 groups).
- **One chosen per couple:** exactly one `is_chosen == 1` per group (2,577
  total).
- **One baseline per couple:** exactly one `draw_joint == 0` per group.
- **Alias equivalence:** `is_chosen == 1` iff `draw_joint == 0` on every row
  (and `is_chosen == is_chosen_joint` everywhere).
- **Chosen-first:** the first row of every `(idhh, year_tag)` group has
  `is_chosen == 1` and `draw_joint == 0`.
- **No scalar draw:** no column named `draw` exists in the output (HC-DRAW).
- **Preservation:** `ils_dispy_male`/`ils_dispy_female` values and missingness
  identical to input (0 missing); `draw_male`/`draw_female`/`draw_joint` and
  the W1 columns present and unchanged; `is_chosen_joint`/`_male`/`_female`
  preserved.
- **Input untouched:** the post-EM parquet (2,319,300 × 151) is unchanged
  (HC1).

Any failed check → halt and report (§12).

---

## 12. Halt conditions

| Halt | Condition |
|---|---|
| **HC1** | Any overwrite of the post-EM parquet, the Stage-4 product parquet, the Stage-5 block outputs, any production script, or the P3a YAML. |
| **HC-DRAW** | A scalar column named `draw` is created, or `draw = draw_joint` aliasing is performed. |
| **HC-CHOSEN** | `is_chosen == 1` not exactly once per group, or `is_chosen == 1` not iff `draw_joint == 0`, or the first row of any group is not the chosen row. |
| **HC-GROUP** | Any `(idhh, year_tag)` group size ≠ 900, or total row count ≠ 2,319,300. |
| **HC-PRESERVE** | Any change to `ils_dispy_*` values/missingness, the W1 columns, or the draw identifiers; any dropped/duplicated row. |
| **HC-STAGE** | Any attempt to run GSUR, precompute, estimation, welfare, SA2, promotion, or M1-clean displacement. |

Any fired halt → stop, write the report up to the halt, await direction. Do
not work around.

---

## 13. What is authorized

- Reading the post-EM parquet (read-only base).
- Adding the integer `is_chosen = is_chosen_joint` alias.
- Chosen-first stable sort within each `(idhh, year_tag)` group (`draw_joint`
  ascending).
- Writing the new `__precompute_ready.parquet` and its `__readymeta.json` under
  the pilot path.
- The §11 validations and the report (§15).

---

## 14. What is not authorized

- Overwriting the post-EM parquet or any prior pilot/production artifact.
- Creating a scalar `draw` column or `draw = draw_joint` alias (HC-DRAW).
- Renaming/moving `is_chosen_joint`/`is_chosen_male`/`is_chosen_female` (alias
  is a copy).
- Altering any `ils_dispy_*`, W1, or draw-identifier values.
- GSUR; precompute; estimation; welfare; SA2; canonical promotion; M1-clean
  displacement.
- Any edit to production P3a files or production data.

---

## 15. Required report

`Results/NC_pilot/JMP_NC_pilot_precompute_readiness_report_v1.md`, covering: scope and
authorization provenance; the `is_chosen` alias (dtype, copy-not-move,
equivalence to `draw_joint==0`); the grouping key and chosen-first sort rule;
the output (path, 2,319,300 rows, +`is_chosen`); the §11 validations (row
count, group size 900, one-chosen-per-couple, alias equivalence, chosen-first
first-row, no-scalar-draw, preservation, input-untouched); halt-condition
status (none/which fired); and required final statements (no GSUR/precompute/
estimation/welfare/SA2/promotion; no scalar draw; M1-clean active; P3a
unaffected; precompute-readiness slice only).

---

## 16. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Pure pandas; read-only input; one new
output file + sidecar; stop after validation.

```text
Work locally in my RURO/MNL codebase. PRECOMPUTE-READINESS SLICE, FR_2016
couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_readiness_amendment_v1.md.

HARD CONSTRAINTS (halt and report if any would be violated):
- Input READ-ONLY: do NOT overwrite the post-EM parquet or any prior
  pilot/production artifact. Write a NEW file. (HC1)
- Do NOT create a scalar 'draw' column; do NOT alias draw = draw_joint.
  draw_male/draw_female/draw_joint remain the ONLY draw identifiers. (HC-DRAW)
- Do NOT rename/move is_chosen_joint/is_chosen_male/is_chosen_female; the
  is_chosen alias is a COPY.
- Do NOT change any ils_dispy_*, W1 wage/proposal-density, or draw-identifier
  values; drop/duplicate no rows. (HC-PRESERVE)
- Do NOT run GSUR/precompute/estimation/welfare/SA2/promotion or displace
  M1-clean. (HC-STAGE)

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_readiness_amendment_v1.md
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em__mergemeta.json

STEP 1 — Load and pre-check:
- Confirm input is 2,319,300 rows, 151 cols, has is_chosen_joint, draw_male,
  draw_female, draw_joint, year_tag, idhh, ils_dispy_male, ils_dispy_female.
- Verify is_chosen_joint == 1 iff draw_joint == 0 on all rows. If not, HALT
  (HC-CHOSEN).

STEP 2 — Alias:
- Add is_chosen = is_chosen_joint.astype(int) (values in {0,1}). Copy, not move.

STEP 3 — Chosen-first sort:
- Stable sort within each (idhh, year_tag) group by draw_joint ascending, so
  draw_joint==0 is row 0 of each group. No row dropped/duplicated.
- (A stable sort on (idhh, year_tag, draw_joint) achieves this.)

STEP 4 — Write NEW output (pilot path):
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet
= 151 input cols + is_chosen (152 total), 2,319,300 rows.
Write fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json
(amendment s.10).

STEP 5 — Validate (amendment s.11):
- row count == 2,319,300; every (idhh, year_tag) group size == 900 (2,577 groups);
- exactly one is_chosen==1 per group (2,577 total); exactly one draw_joint==0
  per group;
- is_chosen==1 iff draw_joint==0 everywhere; is_chosen == is_chosen_joint
  everywhere;
- first row of every group has is_chosen==1 AND draw_joint==0;
- NO column named 'draw' exists in the output (HC-DRAW);
- ils_dispy_male/ils_dispy_female values + 0-missing preserved; draw_male/
  draw_female/draw_joint and W1 columns unchanged; is_chosen_joint/_male/_female
  preserved;
- post-EM parquet unchanged (2,319,300 x 151).

THEN STOP. Do not begin GSUR / precompute.

Halt conditions: HC1, HC-DRAW, HC-CHOSEN, HC-GROUP, HC-PRESERVE, HC-STAGE
(amendment s.12). On any fire: STOP, write the report to that point, await
direction.

Write ONE report: Results/NC_pilot/JMP_NC_pilot_precompute_readiness_report_v1.md per
amendment s.15. End with required final statements (no GSUR/precompute/
estimation/welfare/SA2/promotion; no scalar draw; M1-clean active; P3a
unaffected; precompute-readiness slice only).
```

Save the report as:
`Results/NC_pilot/JMP_NC_pilot_precompute_readiness_report_v1.md`

---

**Required final statements:**

- **This amendment authorizes only the precompute-readiness transformation** —
  an `is_chosen = is_chosen_joint` integer alias and a chosen-first sort,
  producing a new pilot-only parquet.
- **No scalar `draw` column is created**; `draw_male`/`draw_female`/`draw_joint`
  remain the only draw identifiers; a scalar-`draw` alias requires a separate
  later authorization.
- **Chosen row** = `draw_joint == 0` is relabeled and moved to position 0 of
  each `(idhh, year_tag)` group; exactly one per couple; `is_chosen == 1` iff
  `draw_joint == 0`; all 900 alternatives per couple preserved.
- **`ils_dispy_male`/`ils_dispy_female`, the W1 columns, and the draw
  identifiers are preserved unchanged**; the post-EM parquet is not overwritten.
- **Output = 2,319,300 rows; no GSUR, precompute, estimation, welfare, SA2, or
  promotion.** M1-clean 2016 active; corrected pooled P3a track unaffected.

---

*Status: precompute-readiness amendment v1. Authorizes the `is_chosen` alias +
chosen-first sort on true-ID-merged post-EM data, under the §12 halts;
executes nothing itself. Next document: the readiness report (§15), then a
separate precompute (and, if needed, scalar-`draw` compatibility) slice.*
