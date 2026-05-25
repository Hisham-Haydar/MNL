# JMP NC Pilot — Post-EUROMOD Merge-Slice Amendment v1

*France RURO multi-year extension | v1 | 2026-05-22*

**Document category: merge-slice authorization, narrow.** Authorizes only the
assembly of the 30 Strategy C′ EUROMOD block outputs into one wide
post-EUROMOD pilot product parquet carrying partner-specific disposable
income (`ils_dispy_male`, `ils_dispy_female`) for all 2,319,300 alternatives.
It does **not** add `is_chosen`, sort chosen-first, run GSUR, precompute,
estimate, compute welfare, issue SA2, or promote anything. M1-clean 2016
remains active. The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To merge the partner-specific EUROMOD disposable-income outputs from the 30
Strategy C′ blocks back onto the existing 900-alternative pilot product
parquet, producing one wide file with `ils_dispy_male` and `ils_dispy_female`
populated per joint alternative — using **true identifiers** (`idperson_true`,
`idhh_true`), not the draw-encoded IDs — and halting on any ambiguity in the
male/female partner mapping or any income gap.

---

## 2. Current Stage 5 status

Strategy C′ completed successfully:

- All 30 blocks (`f = 0,…,29`) ran; block `f = 0` passed the checkpoint first.
- Each block output: **254,340 rows × 343 columns**; total **7,630,200** rows.
- HE7 stayed quiet under the both-deciders design.
- `id_multiplier = 1000`, `n_draws = 30` consistent across block sidecars.
- The full 30 × 30 joint EUROMOD surface exists across the per-block outputs.

**Row decomposition (merge-relevant).** Per block, 254,340 = 2,577 couples ×
30 male-draws × 2 adult deciders (154,620) + ~99,720 replicated non-decider
(child/other) baseline rows (≈3,324 non-decider persons × 30). The merge must
therefore **filter to decider rows** to isolate the two adult partners before
extracting partner income; the non-decider rows are not partner-income
sources.

Not yet executed: post-EUROMOD merge; `draw_joint` reconstruction into a
merged output; `is_chosen` aliasing; chosen-first sorting; GSUR; precompute;
estimation; welfare; SA2; promotion.

---

## 3. Why a separate post-EUROMOD merge slice is needed

The block outputs are the runner's long-format per-person EUROMOD results with
**draw-encoded** IDs (`idhh = idhh_true·1000 + draw`, `idperson =
idperson_true·1000 + draw`, runner lines 808–823). They are not the model's
choice-set object: they are keyed per person per male-draw within a block, not
per joint alternative per couple. Turning them into the wide
(idhh, draw_male, draw_female) → (ils_dispy_male, ils_dispy_female) object
requires (a) decoding to true IDs, (b) classifying each decider row as the
male or female partner, (c) recovering the block constant `f` and the run
scalar `m` to rebuild `draw_joint`. Each step has an ambiguity failure mode
that warrants its own gated slice rather than being folded into the Stage 5
run.

---

## 4. Required partner-specific disposable-income objects

For every couple and every joint alternative (m, f), two scalars:

- **`ils_dispy_male`** = `ils_dispy` from the **male partner's decider row** in
  the block-`f` output at scalar `draw = m`.
- **`ils_dispy_female`** = `ils_dispy` from the **female partner's decider row**
  in the same block/draw.

These are the production couples income routing
(`income_routing.couples_male = ils_dispy_male`,
`couples_female = ils_dispy_female`). They must be recovered **per partner**,
not collapsed into a household scalar (§16). EUROMOD's tax-benefit
computation is household-joint (both partners' earnings entered together
within the block), so the per-partner `ils_dispy` values already reflect the
joint household calculation; the merge extracts each partner's value, it does
not re-aggregate.

---

## 5. Input product parquet (left/base)

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet` —
2,319,300 rows (2,577 × 900), 149 columns, with `draw_male`, `draw_female`,
`draw_joint`, `is_chosen_joint`/`is_chosen_male`/`is_chosen_female`, the couple
household ID, and the per-partner ID columns. **Read-only base; never
overwritten.** The merge output is a new file (§11).

The merge must first **confirm which product-parquet columns hold the male and
female partner person-IDs** (§7). The Stage-4 build carried bare identifiers as
male-only values; the female partner ID lives in a `_female`-suffixed column
if present. This identification is a precondition; if it cannot be made
unambiguously, halt.

---

## 6. Input EUROMOD block outputs

The 30 per-block outputs
`Data/pilot/nc_2016_couples/em_outputs/block_f{NN}/combined_draws_em.parquet`
(NN = 00…29), 254,340 × 343 each. **Read-only; never overwritten.** Each row
carries: encoded `idhh`/`idperson`; **`idhh_true`/`idperson_true`** (decoded);
`draw` (= male marginal `m`); `is_decider`; `ils_dispy` and the full ≈343-col
EUROMOD output schema; and the block's `f` (from the block dir and/or the
recorded (m, f) tagging from Stage 5 v2 §15).

---

## 7. Partner-ID mapping

**Use `idperson_true` and `idhh_true` from the EUROMOD outputs as the merge
identifiers. Do NOT merge on encoded `idperson`/`idhh`** unless this amendment
explicitly proves the decode correct — and since the runner's encoding is
`id = id_true·1000 + draw`, the encoded IDs are draw-contaminated and must not
be used as join keys. The decoded `*_true` columns are the canonical join keys.

Mapping procedure (and its halts):

1. **Filter each block output to `is_decider == 1`** → the two adult partners
   per (couple, m). Excludes the ~99,720 non-decider rows/block.
2. **Validate `idhh_true` matches the product-parquet household ID** for the
   couples in scope. If any `idhh_true` has no product-parquet match (or vice
   versa within scope), halt.
3. **Classify each decider `idperson_true` as male or female** by mapping to
   the product parquet's confirmed male/female partner-ID columns (§5). The
   mapping must be **one-to-one**: each couple's two `idperson_true` values map
   to exactly one male and exactly one female product-parquet partner ID.
4. **If the male/female mapping is ambiguous** (an `idperson_true` matches both
   or neither partner column, or a couple resolves to two males / two females /
   one adult), **halt** — do not guess.
5. **If duplicate `(idperson_true, draw, block_f)` rows exist after the decider
   filter, halt** (each partner must appear once per (m, f)).

---

## 8. Merge-key convention

- Recover, per block-output decider row, the tuple **`(idhh_true, draw_male,
  draw_female)`** where `draw_male = m` (the run scalar `draw`) and
  `draw_female = f` (the block constant).
- Join the male-classified rows and the female-classified rows separately onto
  the product parquet on **`(idhh, draw_male, draw_female)`** (product
  household ID ≡ validated `idhh_true`).
- Never use `draw_joint` as a join scalar into the runner; `draw_joint` is
  reconstructed (§9), not used as a merge key into EUROMOD outputs.
- Each side contributes exactly one income scalar per product row:
  `ils_dispy_male` from the male join, `ils_dispy_female` from the female join.

---

## 9. draw_male, draw_female, draw_joint reconstruction

- `draw_male`, `draw_female`, `draw_joint` on the **product parquet are
  preserved** as-is (the base file is authoritative for the choice-set keys).
- From the EUROMOD side, reconstruct the alternative identity as `m` (scalar
  `draw`) and `f` (block constant), and verify
  **`draw_joint = 30·draw_male + draw_female`** is consistent between the
  reconstructed (m, f) and the product parquet's existing `draw_joint` on every
  merged row. If any row's reconstructed joint key disagrees with the product
  parquet's `draw_joint`, halt.

---

## 10. Partner-specific disposable-income extraction

1. From each block (filtered to deciders), split into male-classified and
   female-classified rows (§7).
2. From the male rows, take `(idhh_true, m, f, ils_dispy)` → rename
   `ils_dispy → ils_dispy_male`. From the female rows likewise →
   `ils_dispy_female`.
3. **Validate no duplicated partner-income rows** before the wide merge: the
   male table has exactly one row per `(idhh, m, f)`, and so does the female
   table. Halt on any duplicate.
4. Left-join both onto the product parquet on `(idhh, draw_male=m,
   draw_female=f)`.
5. **For each `(idhh, draw_male, draw_female)`, recover exactly one
   `ils_dispy_male` and exactly one `ils_dispy_female`.** Halt if any product
   row receives zero or more than one of either.

---

## 11. Required merged output

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet`
— the product parquet's 149 base columns **plus** `ils_dispy_male` and
`ils_dispy_female`, **2,319,300 rows**. Pilot-only path. The Stage-4 product
parquet and the Stage-5 block outputs are **not** overwritten; this is a new
file. No `is_chosen` column, no chosen-first sort (those are the next slice).

A household-total disposable-income column is **not** created. If one is added
for convenience, it must be explicitly named as derived and non-primary (e.g.
`ils_dispy_hh_derived`) and documented as such (§16); the primary objects are
the two partner-specific columns.

---

## 12. Required metadata sidecar

`fr_pilot_nc_2016_couples_product__post_em__mergemeta.json` recording:
authorization (this amendment); the 30 block-output sources; merge keys used
(`idperson_true`/`idhh_true`, decided explicitly over encoded IDs); the
confirmed male/female partner-ID columns; the decider-filter row reduction
(254,340 → adult deciders per block); `draw_joint` reconstruction formula and
the consistency-check result; output row count (2,319,300); chosen-row count
(2,577 at `draw_joint==0`); income-completeness result; and whether a derived
household total was added (and that it is non-primary). EUROMOD/GSUR/precompute/
estimation/welfare/SA2 = not_run.

---

## 13. Required validation checks

- **Partner mapping:** `idhh_true` ↔ product household one-to-one within scope;
  male/female `idperson_true` map one-to-one to the product partner columns;
  no ambiguous couple (§7). Halt on failure.
- **No duplicates:** male and female income tables each have one row per
  `(idhh, m, f)` after the decider filter (§10.3). Halt on duplicate.
- **One income each:** exactly one `ils_dispy_male` and one `ils_dispy_female`
  per product alternative (§10.5).
- **Joint-key consistency:** reconstructed `30·draw_male + draw_female`
  equals product `draw_joint` on every row (§9).
- **Row count:** merged output = **2,319,300**.
- **Chosen row:** exactly one per couple at `draw_male==0 ∧ draw_female==0 ∧
  draw_joint==0` (2,577 rows).
- **Income completeness:** `ils_dispy_male` and `ils_dispy_female` both
  non-missing on **all** 2,319,300 rows (this is the HE3 wide-completeness
  check, now in-scope for this slice).
- **Untouched inputs:** Stage-4 product parquet (2,319,300 rows, 149 cols) and
  all 30 block outputs unchanged; singles production parquet still 500,700
  rows.

---

## 14. Halt conditions

| Halt | Condition |
|---|---|
| **HM1** | Any in-place edit/overwrite of the Stage-4 product parquet, the 30 Stage-5 block outputs, any production script, or the P3a YAML. |
| **HM2** | Merge performed on encoded `idperson`/`idhh` instead of `idperson_true`/`idhh_true`. |
| **HM3** | `idhh_true` does not match the product household ID for any in-scope couple. |
| **HM4** | Male/female `idperson_true` mapping ambiguous (matches both/neither partner column; couple resolves to two same-sex or fewer than two adults). |
| **HM5** | Duplicate `(idperson_true, draw, block_f)` decider rows, or duplicate `(idhh, m, f)` in either partner-income table. |
| **HM6** | Any product alternative receives zero or >1 `ils_dispy_male` or `ils_dispy_female`. |
| **HM7** | Reconstructed `30·draw_male + draw_female` ≠ product `draw_joint` on any row. |
| **HM8** | Merged row count ≠ 2,319,300, or chosen-row count ≠ 2,577 at `draw_joint==0`. |
| **HM9** | Any `ils_dispy_male`/`ils_dispy_female` missing on any of the 2,319,300 rows. |
| **HM-STAGE** | Any attempt to add `is_chosen`, sort chosen-first, run GSUR, precompute, estimate, compute welfare, issue SA2, promote, or displace M1-clean. |

Any fired halt → stop, write the report up to the halt, await direction. Do
not work around (especially: do not fall back to encoded IDs to resolve a
mapping failure).

---

## 15. What is authorized

- Reading the product parquet (base) and the 30 block outputs (read-only).
- Filtering block outputs to decider rows; classifying male/female via
  `idperson_true`; reconstructing (m, f) and validating `draw_joint`.
- Building the male and female partner-income tables and left-joining onto the
  product parquet.
- Writing the new `__post_em.parquet` (+149 base, +2 income cols) and its
  `__mergemeta.json` under the pilot path.
- The §13 validations and the merge report (§17).

---

## 16. What is not authorized

- Overwriting the Stage-4 product parquet or any Stage-5 block output.
- Merging on encoded IDs (HM2).
- Creating a **primary** household-total income column (a clearly-named
  derived, non-primary `ils_dispy_hh_derived` is permitted only if documented
  as such in the sidecar; the two partner-specific columns remain primary).
- `is_chosen` aliasing; chosen-first sorting; GSUR; precompute; estimation;
  welfare; SA2; canonical promotion; M1-clean displacement.
- Any edit to production P3a files or production data.

---

## 17. Required merge report

`Results/NC_pilot/JMP_NC_pilot_post_em_merge_report_v1.md`, covering: scope and
authorization provenance; the partner-ID mapping (confirmed product male/female
columns; `idperson_true`/`idhh_true` chosen over encoded IDs; one-to-one
validation result); the decider filter (254,340 → adult deciders/block);
partner-income table construction and duplicate checks; `draw_joint`
reconstruction and consistency result; the merged output (path, 2,319,300 rows,
+2 income cols); the §13 validations (row count, chosen-row, income
completeness, untouched inputs); whether a derived household total was added
(and its non-primary status); halt-condition status (none/which fired); and
required final statements (no `is_chosen`/sort/GSUR/precompute/estimation/
welfare/SA2/promotion; M1-clean active; P3a unaffected; merge slice only).

---

## 18. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Read-only inputs; one new output file +
sidecar; stop after validation.

```text
Work locally in my RURO/MNL codebase. POST-EUROMOD MERGE SLICE, FR_2016
couples pilot. Authorized by docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md.

HARD CONSTRAINTS (halt and report if any would be violated):
- Inputs READ-ONLY: do NOT overwrite the Stage-4 product parquet or any of the
  30 Stage-5 block outputs; do NOT touch production P3a files/data.
- Merge on idperson_true / idhh_true ONLY. NEVER on encoded idperson/idhh
  (runner encodes id = id_true*1000 + draw). (HM2)
- Do NOT add is_chosen, do NOT sort chosen-first, do NOT run GSUR/precompute/
  estimation/welfare/SA2, do NOT promote, do NOT displace M1-clean. (HM-STAGE)
- Do NOT create a primary household-total income column. A derived,
  clearly-named non-primary ils_dispy_hh_derived is allowed ONLY if documented
  as non-primary in the sidecar.

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet (base; schema + keys)
- Data/pilot/nc_2016_couples/em_outputs/block_f00..f29/combined_draws_em.parquet
- scripts/enhanced/enh_RURO_euromod.py (read-only; confirm idhh_true/idperson_true
  are emitted and that id encoding is id_true*1000+draw, lines ~546-548, ~808-823)

STEP 1 — Confirm product partner-ID columns:
Identify which product-parquet columns hold the MALE and FEMALE partner
person-IDs and the couple household ID. If this cannot be made unambiguous,
HALT (precondition).

STEP 2 — Per block (f=0..29):
- Read the block output; FILTER to is_decider==1 (drops ~99,720 non-decider
  rows/block; keeps the two adult partners per (couple,m)).
- Use idhh_true, idperson_true (decoded). VALIDATE idhh_true matches product
  household IDs in scope (HM3).
- CLASSIFY each decider idperson_true as male or female via the STEP-1 columns,
  one-to-one per couple. Ambiguous -> HALT (HM4).
- Record draw_male = m (= the block-output scalar 'draw') and draw_female = f
  (the block constant from the block dir / recorded (m,f) tag).
- Check no duplicate (idperson_true, draw, block_f) decider rows (HM5).

STEP 3 — Partner-income tables:
- Male table: one row per (idhh, m, f) with ils_dispy renamed ils_dispy_male.
- Female table: one row per (idhh, m, f) with ils_dispy renamed ils_dispy_female.
- VALIDATE each table has exactly one row per (idhh, m, f) (HM5).

STEP 4 — Wide merge onto product parquet:
- Left-join male and female tables onto the base on (idhh, draw_male=m,
  draw_female=f).
- VALIDATE exactly one ils_dispy_male and one ils_dispy_female per product row
  (HM6).
- VALIDATE 30*draw_male + draw_female == product draw_joint on every row (HM7).

STEP 5 — Write output (pilot path, NEW file):
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet
= 149 base cols + ils_dispy_male + ils_dispy_female, 2,319,300 rows.
Write fr_pilot_nc_2016_couples_product__post_em__mergemeta.json (amendment s.12).

STEP 6 — Validate (amendment s.13):
- row count == 2,319,300 (HM8);
- exactly 2,577 chosen rows at draw_male==0 & draw_female==0 & draw_joint==0 (HM8);
- ils_dispy_male AND ils_dispy_female non-missing on ALL 2,319,300 rows (HM9);
- Stage-4 product parquet (2,319,300x149) and all 30 block outputs unchanged;
  singles production parquet still 500,700 rows.

THEN STOP. Do not begin GSUR / is_chosen / sort / precompute.

Halt conditions: HM1-HM9, HM-STAGE (amendment s.14). On any fire: STOP, write
the report to that point, await direction. Do NOT fall back to encoded IDs.

Write ONE report: Results/NC_pilot/JMP_NC_pilot_post_em_merge_report_v1.md per
amendment s.17. End with required final statements (no is_chosen/sort/GSUR/
precompute/estimation/welfare/SA2/promotion; M1-clean active; P3a unaffected;
merge slice only).
```

Save the report as: `Results/NC_pilot/JMP_NC_pilot_post_em_merge_report_v1.md`

---

**Required final statements:**

- **This amendment authorizes only the post-EUROMOD merge slice** — assembling
  the 30 C′ block outputs into one wide post-EM product parquet with
  partner-specific disposable income.
- **Merge keys are `idperson_true`/`idhh_true`**, never the draw-encoded IDs;
  ambiguous male/female mapping → halt.
- **`ils_dispy_male` and `ils_dispy_female` are the primary objects**, recovered
  one-per-partner per alternative from decider rows; no primary household-total
  column is created.
- **`draw_male`/`draw_female`/`draw_joint` preserved; `draw_joint = 30·draw_male
  + draw_female` reconstructed and consistency-checked.**
- **Output = 2,319,300 rows; exactly one chosen row per couple; both income
  columns non-missing on all rows.**
- **Stage-4 product parquet and Stage-5 block outputs are not overwritten; no
  production file is modified.**
- **No `is_chosen` aliasing, chosen-first sorting, GSUR, precompute, estimation,
  welfare, SA2, or promotion.** M1-clean 2016 active; corrected pooled P3a track
  unaffected.

---

*Status: post-EUROMOD merge-slice amendment v1. Authorizes the partner-specific
income merge on true identifiers, under the §14 halts; executes nothing itself.
Next document: the merge report (§17), then a separate
is_chosen/sort/precompute-readiness slice.*
