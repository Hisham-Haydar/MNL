# JMP NC Pilot — Normalization-Rebuild Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: pilot normalization-rebuild authorization, narrow.**
Authorizes only rebuilding the consumption normalization (`c_norm`) on a new
pilot-only parquet, from the correct post-C′ consumption object
(`ils_dispy_male + ils_dispy_female`), so the precompute's normalization
consistency check passes. It does **not** rebuild leisure normalization, run
precompute, GSUR, estimation, welfare, SA2, or promotion. M1-clean 2016 remains
active. The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To clear the HP-NORM halt by rebuilding `c_norm` from the pilot's true
consumption object — the C′ joint EUROMOD disposable income — and establishing a
documented `c_scale_pilot`, written to a new pilot-only parquet + metadata
sidecar that `precompute_data_couples` can consume. Leisure normalization is
untouched (out of scope, §14).

---

## 2. Current precompute halt status

The precompute slice halted cleanly at HP-NORM (no precompute run, no artifact):

- Hard-required column gate **passed** (all 10 present); wage layer present;
  GSUR (`gsur_male`/`gsur_female`) and region (`reg_nuts1_2..8`, `drgn1`)
  present — **no guarded fallback would fire**.
- HP-NORM **fired**: `max |c_norm × c_scale_production − consumption| = 25,355`
  EUR/month vs the 1.0 tolerance — a structural staleness, not rounding.
- No estimation/welfare/SA2/promotion; pilot parquet and production unmodified.

---

## 3. Why normalization must be rebuilt

`c_norm` in the pilot parquet was inherited from the **production diagonal**
parquet: built from old single-draw EUROMOD income divided by
`c_scale_production = 7,597 EUR/month`, then replicated 900× per couple during
the Stage 3/4 cross-join. The post-EUROMOD merge (Stage 5) added the new
partner-specific income `ils_dispy_male`/`ils_dispy_female` for all 900 joint
cells but **did not** rebuild `c_norm`. So `c_norm` reflects the old diagonal
consumption surface, not the C′ joint surface the model must use. The fix is to
rebuild `c_norm` from the correct object:

```
c_pilot = ils_dispy_male + ils_dispy_female
```

This is the household-level consumption the couples utility index requires, and
it is exactly what EUROMOD produced for each joint alternative.

---

## 4. Input parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet`
— 2,319,300 rows × 152 cols, with `ils_dispy_male`/`ils_dispy_female` (complete,
0 missing), the stale `c_norm`, `l_norm_male`/`l_norm_female`, the W1/GSUR/region
columns, and chosen-first ordering. **Read-only; never overwritten** (HN-MUT).
The slice writes a new file (§9).

---

## 5. Correct pilot consumption object

```
c_pilot = ils_dispy_male + ils_dispy_female   (per row, per joint alternative)
```

This is the household joint disposable income EUROMOD computed with both
partners at their respective draw jobs — the consumption that varies correctly
across all 900 cells per couple (unlike the stale diagonal `c_norm`, which is
constant across draws). The merge metadata gives marginals (means ≈2,017 male /
≈2,037 female), so `c_pilot` means ≈4,054 EUR/month at the row level — but the
**min** must be checked for the positivity gate (§8): both income columns have
negative minima (male −2,150; female −1,576), so `c_pilot` could be ≤ 0 on some
rows.

---

## 6. c_scale_pilot rule

Define `c_scale_pilot` from the **pilot consumption distribution** and record the
exact rule. **Decision: `c_scale_pilot = mean(c_pilot)` over all 2,319,300 rows**
— the standard normalization convention (normalize by the sample mean so `c_norm`
is dimensionless and centred near 1), matching how the production `c_scale` was a
mean-type scale. The report records the computed value to full precision. (If the
production convention was a different statistic — e.g. mean over chosen rows only
— the rule must match it; absent evidence otherwise, the all-rows mean is the
documented choice and the report states it explicitly.)

```
c_scale_pilot = mean(ils_dispy_male + ils_dispy_female)   over all rows
```

---

## 7. c_norm rebuild rule

```
c_norm = c_pilot / c_scale_pilot
```

Computed per row, replacing the stale `c_norm` in the **output** parquet (the
input is preserved). No other column is recomputed in this slice.

---

## 8. Positivity gate

`precompute_data_couples` takes `log(c_norm)`; non-positive consumption is
undefined. The rebuild must verify, **before writing**:

- `c_pilot > 0` for **all** 2,319,300 rows;
- `c_norm > 0` for **all** rows (equivalent, since `c_scale_pilot > 0`).

**If any `c_pilot ≤ 0` or `c_norm ≤ 0`, halt** (HN-POS) and report the count and
the offending `(idhh, draw_joint)` rows. Do **not** silently floor, clip, or
EPS-substitute — that is the precompute's internal `np.maximum(·, EPS)` job, not
the rebuild's, and a genuinely negative joint disposable income is a substantive
finding (a couple whose tax-benefit position is net-negative at some job
combination) that must be surfaced, not masked. Negative income is plausible
given both partners' negative income minima (§5); if it occurs, it is a real
modelling question for the next decision, not a rebuild workaround.

---

## 9. Required output parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet`
— the input's 152 columns with **`c_norm` replaced** by the rebuilt values,
2,319,300 rows, chosen-first ordering preserved. Pilot-only; input not
overwritten (HN-MUT).

**Preserved unchanged:** `draw_male`, `draw_female`, `draw_joint`, `is_chosen`,
`is_chosen_joint`/`is_chosen_male`/`is_chosen_female`, `ils_dispy_male`,
`ils_dispy_female`, the W1 wage/proposal-density columns, GSUR
(`gsur_male`/`gsur_female`), region (`reg_nuts1_2..8`, `drgn1`),
`l_norm_male`/`l_norm_female`, and the chosen-first sort.

**`c_pilot` column:** optional. If added, mark it **diagnostic/non-primary** in
metadata; otherwise record its distribution in the metadata/report only. It is
not a model-consumed column (precompute reads `c_norm`).

---

## 10. Required metadata sidecar

`fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json`
recording:

- authorization (this doc); input parquet path + row count;
- the consumption object (`c_pilot = ils_dispy_male + ils_dispy_female`);
- **`c_scale_pilot`** (value + the exact rule, §6);
- **`c_scale = c_scale_pilot`** (set explicitly for `precompute_data_couples`
  compatibility — the function reads `metadata["normalization"]["c_scale"]`);
- a `normalization` block in the structure `precompute_data_couples` expects
  (flat `c_scale`/`l_scale`, or nested `couples.c_scale`/`l_male_scale` — match
  whichever the function resolves; supply both keys if unsure);
- **preserved leisure scales** `l_scale` and/or `l_male_scale`/`l_female_scale`
  (carried from production / the prior readymeta — **not** recomputed);
- the rebuilt `c_norm` distribution (mean ≈ 1 by construction, min, max);
- the `c_pilot` distribution (mean, min, max; whether added as a column and its
  non-primary status);
- positivity-gate result; the §11 validations; not_run flags.

---

## 11. Required validation checks

- **Consumption object:** `c_pilot = ils_dispy_male + ils_dispy_female` on all
  rows.
- **Scale:** `c_scale_pilot > 0`; equals the documented rule; `c_scale` set =
  `c_scale_pilot` in metadata.
- **Rebuild identity:** `max |c_norm × c_scale_pilot − c_pilot| ≤ 1.0`
  EUR/month (the check that HP-NORM will re-run; it must now pass).
- **Positivity:** `c_pilot > 0` and `c_norm > 0` on all 2,319,300 rows (else
  HN-POS halt).
- **Leisure preserved:** `l_norm_male`/`l_norm_female` and the leisure scale
  metadata unchanged from input.
- **Structure preserved:** row count 2,319,300; 2,577 groups × 900; chosen-first
  (first row of each `(idhh, year_tag)` group has `is_chosen==1` and
  `draw_joint==0`); `draw_male`/`draw_female`/`draw_joint`/`is_chosen*`/income/
  W1/GSUR/region columns present and unchanged; **no scalar `draw`**.
- **No mutation:** input precompute-ready parquet unchanged (2,319,300 × 152);
  no production file or P3a YAML touched.

Any hard failure → halt and report.

---

## 12. Halt conditions

| Halt | Condition |
|---|---|
| **HN-POS** | Any `c_pilot ≤ 0` or `c_norm ≤ 0`. Halt; report count + offending `(idhh, draw_joint)`; do NOT floor/clip/EPS-substitute. |
| **HN-IDENT** | `max |c_norm × c_scale_pilot − c_pilot| > 1.0` after rebuild (rebuild did not reproduce `c_pilot`). |
| **HN-SCALE** | `c_scale_pilot ≤ 0`, or `c_scale` not set equal to `c_scale_pilot` in metadata, or the rule not recorded. |
| **HN-LEIS** | `l_norm_male`/`l_norm_female` values changed, or leisure scale metadata dropped/altered. |
| **HN-STRUCT** | Row count ≠ 2,319,300; groups ≠ 2,577×900; chosen-first broken; a scalar `draw` introduced; any preserved column dropped/altered. |
| **HN-MUT** | Input parquet, any production parquet, or the frozen P3a YAML modified. |
| **HN-STAGE** | Any attempt to run precompute, GSUR, estimation, welfare, SA2, promotion, or M1-clean displacement. |

Any fired halt → stop, write the report up to the halt, await direction. Do not
work around (especially: do not mask non-positive consumption).

---

## 13. What is authorized

- Reading the input precompute-ready parquet (read-only).
- Computing `c_pilot`, `c_scale_pilot` (§6 rule), and rebuilt `c_norm`.
- The positivity gate (§8).
- Writing the new `__precompute_norm_ready.parquet` (with `c_norm` replaced,
  everything else preserved) and its `__normmeta.json` (with `c_scale_pilot`,
  `c_scale = c_scale_pilot`, preserved leisure scales).
- Optionally adding a diagnostic/non-primary `c_pilot` column.
- The §11 validations and the report (§15).

---

## 14. What is not authorized

- Rebuilding `l_norm_male`/`l_norm_female` or changing any leisure scale
  (out of scope this slice).
- Flooring/clipping/EPS-substituting non-positive consumption (HN-POS).
- Overwriting the input parquet or any production file (HN-MUT).
- Adding a scalar `draw`; altering draw identifiers, `is_chosen*`, income, W1,
  GSUR, or region columns; breaking chosen-first.
- Running precompute, GSUR, estimation, welfare, SA2, promotion; M1-clean
  displacement (HN-STAGE).

---

## 15. Required normalization-rebuild report

`Results/NC_pilot/JMP_NC_pilot_normalization_rebuild_report_v1.md`, covering: scope and
authorization provenance; the HP-NORM root cause recap (stale diagonal `c_norm`
vs C′ joint income); the consumption object and `c_scale_pilot` (value + exact
rule); the rebuilt `c_norm` and `c_pilot` distributions; the positivity-gate
result (and, if HN-POS fired, the offending rows); the §11 validations
(rebuild identity within tolerance, leisure preserved, structure/chosen-first
preserved, no mutation); the metadata written (`c_scale_pilot`,
`c_scale = c_scale_pilot`, preserved `l_scale`/`l_*_scale`); halt-condition
status; and required final statements (leisure not rebuilt; no precompute/GSUR/
estimation/welfare/SA2/promotion; M1-clean active; P3a unaffected; normalization
rebuild slice only).

---

## 16. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Pure pandas; read-only input; one new
parquet + sidecar; positivity-gated; stop before precompute.

```text
Work locally in my RURO/MNL codebase. NORMALIZATION REBUILD SLICE, FR_2016
couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md.

HARD CONSTRAINTS (halt and report if any would be violated):
- Input READ-ONLY: do NOT overwrite the precompute-ready parquet or any
  production file. Write a NEW parquet. (HN-MUT)
- Rebuild ONLY c_norm. Do NOT rebuild l_norm_male/l_norm_female; do NOT change
  any leisure scale. (HN-LEIS)
- Do NOT floor/clip/EPS-substitute non-positive consumption. If any c_pilot<=0
  or c_norm<=0 -> HALT. (HN-POS)
- Do NOT add a scalar 'draw'; preserve draw_male/draw_female/draw_joint,
  is_chosen/is_chosen_joint/_male/_female, ils_dispy_male/female, W1, GSUR,
  region, chosen-first order. (HN-STRUCT)
- Do NOT run precompute/GSUR/estimation/welfare/SA2/promotion or displace
  M1-clean. (HN-STAGE)

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md
- Results/NC_pilot/JMP_NC_pilot_precompute_report_v1.md (the HP-NORM halt)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json
- Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json (leisure scales to PRESERVE)

STEP 1 — Consumption object + scale:
- c_pilot = ils_dispy_male + ils_dispy_female (per row).
- c_scale_pilot = mean(c_pilot) over all 2,319,300 rows. Record to full precision.
  (If production used a different statistic per mnlmeta, MATCH it and document;
   else all-rows mean is the documented rule.)

STEP 2 — Positivity gate (BEFORE writing):
- If any c_pilot <= 0 -> HALT (HN-POS): report count + offending (idhh,
  draw_joint). Do NOT clip/floor/EPS.

STEP 3 — Rebuild:
- c_norm_new = c_pilot / c_scale_pilot. Replace c_norm in the OUTPUT only.
- Verify max|c_norm_new * c_scale_pilot - c_pilot| <= 1.0 (HN-IDENT).
- Verify c_norm_new > 0 all rows (HN-POS).

STEP 4 — Write NEW outputs (pilot path):
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet
= 152 cols with c_norm replaced (optionally + diagnostic non-primary c_pilot),
2,319,300 rows, chosen-first preserved.
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json
with: c_scale_pilot (+ rule), c_scale = c_scale_pilot, a normalization block in
the structure precompute_data_couples expects, PRESERVED l_scale/l_male_scale/
l_female_scale (from mnlmeta/readymeta, NOT recomputed), c_norm + c_pilot
distributions, positivity result.

STEP 5 — Validate (authorization s.11):
- c_pilot = ils_dispy_male+female all rows; c_scale_pilot>0; c_scale==c_scale_pilot;
- rebuild identity within 1.0; c_pilot>0 and c_norm>0 all rows;
- l_norm_male/female + leisure scales unchanged;
- row count 2,319,300; 2,577 groups x 900; chosen-first intact; no scalar draw;
  draw/is_chosen*/income/W1/GSUR/region preserved;
- input parquet unchanged (2,319,300 x 152); no production file touched.

THEN STOP. Do not run precompute.

Halt conditions: HN-POS, HN-IDENT, HN-SCALE, HN-LEIS, HN-STRUCT, HN-MUT,
HN-STAGE (authorization s.12). On any fire: STOP, write report to that point,
await direction. Do NOT mask non-positive consumption.

Write ONE report: Results/NC_pilot/JMP_NC_pilot_normalization_rebuild_report_v1.md per
authorization s.15. End with required final statements (leisure not rebuilt;
no precompute/GSUR/estimation/welfare/SA2/promotion; M1-clean active; P3a
unaffected; normalization rebuild slice only).
```

Save the report as:
`Results/NC_pilot/JMP_NC_pilot_normalization_rebuild_report_v1.md`

---

## Required final statements

- **This authorizes only the pilot consumption normalization rebuild** —
  `c_norm = (ils_dispy_male + ils_dispy_female) / c_scale_pilot` on a new
  pilot-only parquet.
- **`c_scale_pilot` is defined from the pilot consumption distribution** (mean
  of `c_pilot`, rule recorded); **`c_scale` is set = `c_scale_pilot`** for
  `precompute_data_couples` compatibility.
- **Leisure normalization is not rebuilt;** `l_scale`/`l_male_scale`/
  `l_female_scale` and `l_norm_male`/`l_norm_female` are preserved.
- **Positivity is gated:** any `c_pilot ≤ 0` or `c_norm ≤ 0` halts (no masking).
- **Structure preserved:** 2,319,300 rows; 2,577×900; chosen-first; all draw/
  chosen/income/W1/GSUR/region columns; no scalar `draw`; input not overwritten.
- **No precompute, GSUR, estimation, welfare, SA2, or promotion.** M1-clean 2016
  active; corrected pooled P3a track unaffected.

---

*Status: normalization-rebuild authorization v1. Authorizes the pilot `c_norm`
rebuild from the C′ joint income object under the §12 halts; executes nothing
itself. Next document: the rebuild report (§15), then re-entry to the
precompute slice (HP-NORM cleared).*
