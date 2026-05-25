> Archived on 2026-05-26 as a documentation-only formatting correction whose substance is reabsorbed.
> Base file (kept active): `docs/France_case/execution_logs/stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Stage M1 P3a GSURv2 Stacking Authorization — Correction v1

*France 2014–2015–2016 | v1 | 2026-05-21*

---

## 1. Purpose

This document records a narrow formatting correction applied to
`docs/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`. No
authorization scope, input requirements, output requirements, validation
requirements, halt conditions, or substantive text was changed.

| # | Issue | Action |
|---|-------|--------|
| C1 | The closing block `Required final statements` appeared as a `##`-level heading, adding a 16th `##` heading to the document and making the numbered section count inconsistent | Demoted to `**Required final statements**` (bold inline text) under section 15, restoring the document to exactly 15 numbered `##` sections |

---

## 2. Heading correction

The authorization document requires exactly 15 numbered `##` sections
(§1 Purpose through §15 Exact next Claude Code task). A sixteenth
`##` heading (`## Required final statements`) appeared after §15,
outside the numbered sequence.

**Before correction:**

```
## 15. Exact next Claude Code task
[body]
---
## Required final statements
- Stage M1 P3a GSURv2 stacking re-run is authorized only after …
…
```

**After correction:**

```
## 15. Exact next Claude Code task
[body]
---
**Required final statements**
- Stage M1 P3a GSURv2 stacking re-run is authorized only after …
…
```

The corrected document has exactly 15 `##` headings (§1–§15). The
`Required final statements` block remains in place under §15 as bold
text, and its four bullet points are unchanged.

**Verification:**

Running `grep "^## " docs/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`
returns exactly 15 lines, §1 through §15. No `## Required final
statements` line is present.

---

## 3. What was not changed

The following are confirmed unchanged by this correction:

- The exact GSURv2 input stem requirements (§5, Table 1):
  `fr_2015_RURO_mnl_GSURv2_y2014__`, `fr_2016_RURO_mnl_GSURv2_y2015__`,
  `fr_2017_RURO_mnl_GSURv2_y2016__` (each `__singles.parquet` and
  `__couples.parquet`), with their confirmed SHA-256 hashes.
- The no-broad-glob requirement (§5 I3 and §13 H1): the re-run must
  not use a broad input glob that could accidentally match a non-GSURv2
  parquet.
- The dedicated config / exact-stem config patch requirement (§10):
  Option 1 (dedicated `fr_p3a_gsurv2_stage_m1.yaml`) or Option 2
  (tightly scoped patch), with no v1-fallback or v2gsurY stems resolved.
- The output stems (§6): `fr_p3a_gsurv2_stacked_raw.parquet` and
  `fr_p3a_gsurv2_harmonised.parquet`.
- The provisioning label (§7): `gsurv2_opportunity_year_aligned`.
- The V1–V9 validation requirements (§9) and their expected values.
- All halt conditions H1–H7 (§13).
- The required execution report structure (§14, R1–R10).
- The exact Claude Code task prompt (§15).
- The Required final statements text and all four bullet points:
  exact-GSURv2-input-resolution enforcement, pooled estimation NOT
  authorized, welfare NOT authorized, M1-clean 2016 active baseline.
- All SHA-256 hashes, row counts, household counts, CPI factors, and
  cluster-key specifications recorded in the authorization.

No authorization scope was changed. No data was modified. No script was
run. No parquet was written.

---

## 4. Final authorization status

**The Stage M1 P3a GSURv2 stacking re-run authorization remains fully
in effect.**

The formatting correction does not affect the authorization scope,
the input requirements, the output requirements, the validation
battery, the halt conditions, or any substantive content. The
authorization document now has exactly 15 numbered `##` sections as
required.

**Stage M1 P3a GSURv2 stacking re-run is authorized**, subject to
exact GSURv2 input resolution (§5, §10) and the halt conditions (§13),
as specified in `docs/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.**