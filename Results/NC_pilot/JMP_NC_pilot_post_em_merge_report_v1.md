# JMP NC Pilot — Post-EUROMOD Merge Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Scope and Authorization Provenance

This report documents the post-EUROMOD merge slice for the NC pilot, executed
2026-05-23. Authorization: **`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_post_em_merge_amendment_v1.md`**
(merge-slice authorization, narrow). The slice assembles the 30 Strategy C'
EUROMOD block outputs into one wide post-EM pilot product parquet carrying
partner-specific disposable income (`ils_dispy_male`, `ils_dispy_female`) for
all 2,319,300 joint alternatives.

**Executing script:** `scripts/pilot/merge_pilot_em_outputs.py`
**Wall time:** 17.5 seconds

The following are **not** in scope for this slice and were **not** performed:
`is_chosen` aliasing, chosen-first sorting, GSUR, precompute, estimation,
welfare, SA2, promotion, or M1-clean 2016 displacement.

---

## 2. Stage 5 v2 Input Status

Strategy C' completed successfully prior to this merge:

| Item | Value |
|---|---|
| Blocks completed | 30 (f = 0 … 29) |
| Rows per block | 254,340 × 343 columns |
| Total EUROMOD output rows | 7,630,200 |
| HE7 identity assertion | Quiet (max diff = 0.0) |
| id_multiplier | 1,000 |
| n_draws per block | 30 |
| Strategy | C' (both partners as deciders) |

All 30 block outputs confirmed intact at validation time (HM1 PASS; see §20).

---

## 3. Input Product Parquet (Base)

| Item | Value |
|---|---|
| Path | `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet` |
| Rows | 2,319,300 (2,577 couples × 900 alternatives) |
| Columns | 149 |
| Key columns | `idhh`, `idperson`, `idpartner`, `draw_male`, `draw_female`, `draw_joint` |
| Chosen alternatives | 2,577 rows at `draw_male==0 AND draw_female==0 AND draw_joint==0` |
| EUROMOD income at this stage | Not present (dropped at Stage 4 as not valid pre-EUROMOD) |

The Stage-4 product parquet was confirmed unchanged at validation time: 2,319,300 rows (HM1 PASS).

---

## 4. Input EUROMOD Block Outputs

Thirty per-block outputs, each:

| Item | Value |
|---|---|
| Path pattern | `Data/pilot/nc_2016_couples/em_outputs/block_f{NN}/combined_draws_em.parquet` |
| Rows per block | 254,340 (decider: 154,620 + non-decider: 99,720) |
| Total rows across 30 blocks | 7,630,200 |
| Columns per block | 343 |
| Key carried columns | `idhh_true`, `idperson_true`, `draw`, `ils_dispy` |
| Block constant f | Encoded in directory name `block_f{NN}` (not a parquet column) |

`is_decider` and `block_f` were NOT carried as columns in the EUROMOD output
(they are carry columns not emitted by the runner's merge-back logic). The
decider ID set was recovered from the adapter input (§6 below).

---

## 5. Merge Keys Used (HM2 Compliance)

Merge was performed exclusively on **decoded true identifiers**:

- **Household key:** `idhh` on the product parquet matched to `idhh_true` in
  the EUROMOD outputs. These are the pre-encoding values; the EUROMOD runner
  encodes `idhh = idhh_true * 1000 + draw` at lines 547–548 of
  `enh_RURO_euromod.py`. The encoded `idhh` column was **never** used as a
  join key (HM2 PASS).
- **Person key (for decider classification):** `idperson_true` from EUROMOD
  outputs matched against the 5,154-element decider-ID set loaded from the
  adapter input (`em_inputs/block_f00/…_draws.parquet`, `is_decider==1`).
  The encoded `idperson = idperson_true * 1000 + draw` column was **never**
  used (HM2 PASS).
- **Income join keys:** `(idhh, draw_male, draw_female)` on both sides after
  recovering `draw_male = draw` (scalar EUROMOD column) and
  `draw_female = f` (block constant).

---

## 6. Decider Filter (HM1 / Amendment §7 Step 1)

The EUROMOD output does not carry `is_decider` as a column (it is not in the
runner's standard carry-back output schema). The decider person-ID set was
recovered from the adapter input parquet for block f=00, which does carry
`is_decider`:

| Source | Path |
|---|---|
| Adapter input | `Data/pilot/nc_2016_couples/em_inputs/block_f00/fr_pilot_2016_couples_block_f00_draws.parquet` |
| Column used | `is_decider == 1` |

The decider set is constant across all 30 blocks (same 2,577 households ×
2 partners = 5,154 unique `idperson` values). The non-decider rows (~3,324
children at `draw=0`, replicated to 99,720 rows per block by the runner) have
`idperson_true` values that do not appear in the decider set (confirmed: zero
overlap between the 5,154 decider IDs and 3,324 non-decider IDs).

**Decider filter result per block:**

| Item | Count |
|---|---|
| Total rows per block | 254,340 |
| Decider rows extracted | 154,620 |
| Non-decider rows dropped | 99,720 |
| Male decider rows (`dgn == 1.0`) | 77,310 |
| Female decider rows (`dgn == 0.0`) | 77,310 |

---

## 7. Partner-ID Mapping (HM4 Validation)

**Confirmed product parquet male/female partner-ID columns:**

| Partner | Product column | Description |
|---|---|---|
| Male | `idperson` | Male partner person ID (household-level, same across all 900 alternatives per couple) |
| Female | `idpartner` | Female partner person ID (= male's household partner) |

These identifications derive from the Stage-3 cross-join construction in
`build_pilot_couples_product.py`: the male side carried the bare `idperson`
and shared/household columns; the female side's person ID is accessible via
`idpartner` (the EUROMOD production field for the household partner of the
male decider).

**Mapping validation result (HM4 PASS):**

| Check | Result |
|---|---|
| EM male decider IDs match product `idperson` | 2,577 / 2,577 |
| EM female decider IDs match product `idpartner` | 2,577 / 2,577 |
| EM male IDs appearing in product female column | 0 (no crossovers) |
| EM female IDs appearing in product male column | 0 (no crossovers) |
| Ambiguous couples (two-male or two-female) | 0 |
| Couples with fewer than 2 adult deciders | 0 |

The mapping is one-to-one and unambiguous. No halt condition HM4 fired.

---

## 8. draw_joint Reconstruction (HM7)

From the EUROMOD output side:

- `draw_male` = scalar `draw` column in the EUROMOD output (= male marginal
  m ∈ {0..29}).
- `draw_female` = block constant f ∈ {0..29}, recovered from the directory
  name `block_f{NN}` (not from a parquet column, since `block_f` is not in
  the carry-back output).

Consistency check against the product parquet's existing `draw_joint`:

```
Reconstructed: 30 * draw_male + draw_female
```

**HM7 result:** PASS. All 2,319,300 merged rows satisfy
`30 * draw_male + draw_female == draw_joint` exactly (integer arithmetic, no
floating-point tolerance needed). Zero mismatches.

---

## 9. Partner-Income Table Construction

For each of the 30 blocks, decider rows were split by gender classification:

**Male income table (per block):**
- Rows: 77,310 (= 2,577 couples × 30 male draws)
- Key: `(idhh, draw_male, draw_female)` where `draw_female = f` (block constant)
- Value column: `ils_dispy` renamed to `ils_dispy_male`

**Female income table (per block):**
- Rows: 77,310
- Key: `(idhh, draw_male, draw_female)`
- Value column: `ils_dispy` renamed to `ils_dispy_female`

After concatenating all 30 blocks:

| Table | Rows | Expected |
|---|---|---|
| Male income | 2,319,300 | 2,319,300 |
| Female income | 2,319,300 | 2,319,300 |

---

## 10. Duplicate Checks (HM5)

Three levels of duplicate checking were performed:

1. **Per-block, per-row:** No duplicate `(idperson_true, draw)` within any
   block's decider rows. All 30 blocks PASS.
2. **Per-block income tables:** No duplicate `(idhh, draw_male, draw_female)`
   in either the male or female income table for any block. All 30 blocks PASS.
3. **Global income tables:** No duplicate `(idhh, draw_male, draw_female)` in
   either the combined 2,319,300-row male or female income table across all
   30 blocks. PASS.

**HM5 result:** PASS. No duplicates at any level.

---

## 11. Wide Merge onto Product Parquet

Left-join procedure (amendment §10.4):

1. Product parquet (2,319,300 rows × 149 cols) left-joined on male income
   table on `(idhh, draw_male, draw_female)` → 2,319,300 rows × 150 cols.
2. Result left-joined on female income table on same keys →
   2,319,300 rows × 151 cols.

No fan-out occurred: row count held at 2,319,300 after both joins (confirmed
by HM6 check: `len(merged) == len(product)`).

---

## 12. Merged Output (HM6)

| Check | Result |
|---|---|
| Exactly one `ils_dispy_male` per product row | PASS |
| Exactly one `ils_dispy_female` per product row | PASS |
| Zero `ils_dispy_male` on any row | PASS (no gaps) |
| Zero `ils_dispy_female` on any row | PASS (no gaps) |

**HM6 result:** PASS.

---

## 13. Output File

| Item | Value |
|---|---|
| Path | `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet` |
| Rows | 2,319,300 |
| Columns | 151 (149 base + `ils_dispy_male` + `ils_dispy_female`) |
| File size | 105,215,754 bytes (~100 MB) |
| Compression | Snappy (pyarrow engine) |
| Produced at | 2026-05-23T07:03:19Z |

The Stage-4 product parquet (`fr_pilot_nc_2016_couples_product.parquet`) is
**not** modified. This is a new file at a new path.

---

## 14. Metadata Sidecar

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em__mergemeta.json`

Records: authorization; 30 block-output sources (all `ok: true`); merge keys
(decoded `idhh_true`/`idperson_true` over encoded IDs, HM2 explicit); confirmed
partner-ID columns (`idperson` = male, `idpartner` = female); decider filter
reduction (254,340 → 154,620 per block); `draw_joint` formula and HM7 result;
output row count (2,319,300); chosen rows (2,577); income completeness (HM9);
no household-total derived column created; all `not_run` flags set to `false`.

---

## 15. Income Column Statistics

**`ils_dispy_male`** (male partner EUROMOD disposable income, monthly EUR):

| Statistic | Value |
|---|---|
| Mean | 2,017.45 |
| Std dev | 1,377.11 |
| Min | -2,149.51 |
| Max | 15,237.52 |
| Missing | 0 |

**`ils_dispy_female`** (female partner EUROMOD disposable income, monthly EUR):

| Statistic | Value |
|---|---|
| Mean | 2,036.83 |
| Std dev | 1,333.05 |
| Min | -1,576.10 |
| Max | 13,480.52 |
| Missing | 0 |

Both columns are primary income objects per amendment §4. The distributions are
plausible: mean near 2,000 EUR/month for each partner, with male dispersion
slightly higher (std 1,377 vs 1,333), and male minimum slightly more negative
(reflecting larger earnings variance feeding into the tax-benefit system).
Income is per-partner, not a household total.

---

## 16. No Household-Total Income Column

No `ils_dispy_hh_derived` or household-total income column was created, per
amendment §11. The two partner-specific columns `ils_dispy_male` and
`ils_dispy_female` are the only income additions. If a derived household total
is needed in a future slice, it must be explicitly named as non-primary and
documented as derived in that slice's sidecar.

---

## 17. Row Count and Chosen-Row Validation (HM8)

| Check | Expected | Observed | Result |
|---|---|---|---|
| Total merged rows | 2,319,300 | 2,319,300 | PASS |
| Chosen rows at `draw_joint == 0` | 2,577 | 2,577 | PASS |
| Unique households with chosen row | 2,577 | 2,577 | PASS |

**HM8 result:** PASS.

---

## 18. Income Completeness (HM9)

| Column | Missing rows | Result |
|---|---|---|
| `ils_dispy_male` | 0 | PASS |
| `ils_dispy_female` | 0 | PASS |

Both income columns are non-null on all 2,319,300 rows. This constitutes the
HE3 wide-completeness check (now in-scope for this slice per amendment §13).

**HM9 result:** PASS.

---

## 19. draw_joint Consistency (HM7)

Checked on all 2,319,300 merged rows:

```
assert (30 * merged["draw_male"] + merged["draw_female"] == merged["draw_joint"]).all()
```

Mismatches: 0.

**HM7 result:** PASS.

---

## 20. Untouched Inputs (HM1)

| Input | Expected | Confirmed | Result |
|---|---|---|---|
| Stage-4 product parquet | 2,319,300 rows, 149 cols | 2,319,300 rows | PASS |
| All 30 Stage-5 block outputs | 254,340 rows each | 254,340 rows each | PASS |
| Singles production parquet | 500,700 rows | Not checked at run time (confirmed at Stage 4) | — |

No production P3a files, production scripts, or P3a YAML files were accessed
or modified.

**HM1 result:** PASS.

---

## 21. Halt Condition Status

| Code | Condition | Fired? |
|---|---|---|
| HM1 | Overwrite of Stage-4 product, block outputs, or production files | No |
| HM2 | Merge on encoded `idperson`/`idhh` | No |
| HM3 | `idhh_true` not matching product household IDs | No |
| HM4 | Male/female `idperson_true` mapping ambiguous | No |
| HM5 | Duplicate decider rows or duplicate income-table keys | No |
| HM6 | Zero or >1 income value per product alternative | No |
| HM7 | Reconstructed `draw_joint` mismatch | No |
| HM8 | Row count or chosen-row count mismatch | No |
| HM9 | Missing income on any row | No |
| HM-STAGE | `is_chosen`, sort, GSUR, precompute, estimation, welfare, SA2, promotion | No |

No halt condition fired. Merge slice completed successfully.

---

## 22. What Was Not Done

The following are **explicitly not** part of this slice (per amendment §16):

- No `is_chosen` column added to the merged parquet.
- No chosen-first sort applied to merged groups.
- No GSUR re-merge.
- No precompute.
- No MNL estimation.
- No welfare computation.
- No SA2 issuance.
- No canonical promotion of pilot to production.
- No M1-clean 2016 displacement.
- No primary household-total income column (`ils_dispy_hh_derived` not created).

These are authorized in separate future slices.

---

## 23. Stage Status

| Track | Status |
|---|---|
| M1-clean 2016 | Active (unmodified) |
| Corrected pooled P3a | Unaffected (no P3a files touched) |
| Singles production parquet | Unaffected |
| NC pilot post-EM merge | Complete (this report) |

---

## 24. Produced Artifacts

| Artifact | Description |
|---|---|
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet` | 2,319,300 rows × 151 cols; 149 base + `ils_dispy_male` + `ils_dispy_female` |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em__mergemeta.json` | Merge metadata sidecar per amendment §12 |
| `scripts/pilot/merge_pilot_em_outputs.py` | Merge script; pilot-only; read-only inputs; halts on any HM condition |
| `Results/JMP_NC_pilot_post_em_merge_report_v1.md` | This report |

---

## 25. Required Final Statements

- **This amendment authorizes only the post-EUROMOD merge slice** — assembling
  the 30 Strategy C' block outputs into one wide post-EM product parquet with
  partner-specific disposable income.

- **Merge keys are `idperson_true`/`idhh_true`**, never the draw-encoded IDs
  (`idperson = idperson_true * 1000 + draw`). The male/female partner mapping
  was confirmed one-to-one with zero ambiguity (HM4 PASS). No fallback to
  encoded IDs was required or attempted.

- **`ils_dispy_male` and `ils_dispy_female` are the primary income objects**,
  recovered one-per-partner per joint alternative from decider rows only.
  No primary household-total income column was created.

- **`draw_male`/`draw_female`/`draw_joint` preserved from the base parquet.**
  The identity `draw_joint = 30 * draw_male + draw_female` was reconstructed
  from EUROMOD outputs and verified on all 2,319,300 rows (HM7 PASS).

- **Output = 2,319,300 rows; exactly one chosen row per couple (2,577) at
  `draw_joint == 0`; both income columns non-missing on all rows (HM9 PASS).**

- **Stage-4 product parquet and all 30 Stage-5 block outputs are not
  overwritten; no production file was modified (HM1 PASS).**

- **No `is_chosen` aliasing, chosen-first sorting, GSUR, precompute,
  estimation, welfare, SA2, or promotion was performed.** M1-clean 2016 is
  active. The corrected pooled P3a track is unaffected. This report covers the
  merge slice only.

---

*Status: post-EUROMOD merge-slice report v1. Merge complete; all HM1-HM9 and
HM-STAGE checks passed. Next slice: `is_chosen` aliasing and chosen-first sort
for estimation-engine position-0 invariant, followed by precompute readiness
check.*
