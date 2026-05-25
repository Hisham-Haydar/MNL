# JMP NC Pilot — HN-POS Resolution Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: HN-POS resolution + normalization-rebuild authorization,
narrow.** Authorizes only resolving the 123 non-positive `c_pilot` rows via an
**explicit normalized-EPS floor** consistent with `precompute_data_couples`, and
completing the `c_norm` rebuild on a new pilot-only parquet. It does **not** drop
households or rows, re-run EUROMOD, run precompute, GSUR, estimation, welfare,
SA2, or promotion. M1-clean 2016 remains active. The corrected pooled P3a track
is unaffected.

---

## 1. Purpose

To clear the HN-POS halt by making explicit, at the normalization step, the same
floor `precompute_data_couples` already applies internally
(`np.maximum(c_norm, EPS)`), so the 123 non-positive joint-income cells are
handled by a documented, visible rule rather than silently inside precompute —
and to finish the `c_norm` rebuild (`c_scale_pilot` already computed as
4,054.2856 EUR/month) and write the normalized parquet.

---

## 2. Current HN-POS status

The rebuild halted cleanly at HN-POS (no output written):

- `c_scale_pilot = 4,054.2856` EUR/month (all-rows mean of `c_pilot`), `> 0`.
- **123 rows across 6 households** have `c_pilot = ils_dispy_male +
  ils_dispy_female ≤ 0` (raw `c_pilot` min −812.21 EUR/month). These are real
  EUROMOD outputs for specific product-draw cells (a partner assigned a high-tax/
  low-net occupation in those cells), not missing-data or merge artifacts.
- No masking applied; no parquet/sidecar written; no precompute/GSUR/estimation/
  welfare/SA2/promotion; production and input parquet unchanged.

---

## 3. Why a domain decision is required

`precompute_data_couples` takes `log(c_norm)` and internally floors with
`np.maximum(c_norm, EPS)`. The 123 non-positive cells *would* be floored anyway
when precompute runs — but silently, inside the function, invisible to anyone
reading the data. HN-POS deliberately halted to force the choice to be **named**:
do we drop the cells, drop the households, re-run EUROMOD, or floor explicitly?
The decision has a domain dimension (negative joint disposable income is a real
tax-benefit outcome, not noise) and a structural dimension (the precompute relies
on uniform 900-row groups, which dropping rows would break). This authorization
records the choice and its justification rather than letting the floor happen by
default.

---

## 4. Options considered

From the rebuild report §12:

1. **Drop the 6 households** (→ 2,571 × 900 = 2,313,900 rows).
2. **Drop the 123 rows** (→ ragged groups of 875–898; breaks uniform 900).
3. **Floor `c_pilot` at a positive value** (EPS or chosen-cell income) — explicit
   floor.
4. **Re-run EUROMOD** for the 6 households (if negative income is a model
   artefact).
5. **Accept the precompute's internal EPS floor** as informational-only.

---

## 5. Rejected options

- **Drop households (1) — rejected.** Removes 6 real couples (0.23%) entirely,
  including their 5,277 perfectly-valid cells, and biases the pilot sample by
  selecting out households with any net-negative job combination. The negative
  cells are off-diagonal alternatives the couple did not choose; the couple's
  observed (chosen) cell is fine. Dropping the household discards information for
  a property of unchosen alternatives.
- **Drop rows (2) — rejected.** Produces ragged choice sets (875–898 alts) and
  breaks the uniform 900-row group structure the precompute and the
  simulation-consistency design depend on. Non-trivial group-size handling for a
  0.0053% edge case.
- **Re-run EUROMOD (4) — rejected for the pilot.** The negative income is a
  genuine French tax-benefit outcome (clawbacks/liabilities exceeding gross
  earnings at certain low-net occupations), not an obvious artefact. Re-running
  is disproportionate and would itself be a fresh EUROMOD authorization; defer
  unless a later review judges the negatives implausible.
- **Implicit acceptance (5) — rejected as the recorded mechanism.** Letting the
  precompute floor silently is functionally what we do, but leaving it
  *undocumented* is exactly what HN-POS exists to prevent. We adopt the same
  floor **explicitly** (option 6) so the metadata records it.

---

## 6. Authorized option: explicit normalized-EPS floor

**Adopt option 3 in its normalized-EPS form** — apply, at the rebuild step, the
identical floor `precompute_data_couples` uses internally, but explicitly and
recorded. This keeps the consumption surface byte-identical to what the
precompute would produce, while making the 123 floored cells visible in the data
(diagnostic flag) and metadata.

This is a **pilot computational-domain convention** — the minimal step that lets
`log(c_norm)` be defined — **not a final welfare-domain decision** on how
net-negative-income alternatives should enter the welfare metric. That welfare
treatment is a separate, later question.

---

## 7. EPS source rule

**EPS must be read from the actual `precompute_data_couples` implementation /
shared constant, not assumed.** Confirmed value:

```
EPS = 1e-12          (estimation_utils.py line 49)
used as: consumption = np.maximum(df["c_norm"].values.copy(), EPS)   (line 998)
```

EPS is a **floor on the normalized `c_norm`**, not a euro floor. If, at build
time, EPS cannot be located unambiguously at this constant / use site, **halt**
(HF-EPS) — do not substitute a guessed value.

---

## 8. Correct floor formula

```
c_pilot_raw  = ils_dispy_male + ils_dispy_female
c_norm_raw   = c_pilot_raw / c_scale_pilot
c_norm       = max(c_norm_raw, EPS)            # EPS = 1e-12, normalized floor
```

Equivalently (raw-euro form, for the diagnostics):

```
c_pilot_for_norm = max(c_pilot_raw, EPS * c_scale_pilot)
c_norm           = c_pilot_for_norm / c_scale_pilot
```

with `EPS * c_scale_pilot = 1e-12 × 4054.2856 ≈ 4.05e-9` EUR/month — an
effectively-zero floor (the 123 cells map to `c_norm = 1e-12`, i.e.
`log c_norm ≈ −27.6`, a large-negative utility that makes those alternatives
near-irrelevant in the softmax, without an undefined `log`). The floor is applied
only where `c_norm_raw ≤ EPS`; all other rows are unchanged.

---

## 9. Raw consumption diagnostics

Preserve, in metadata/report (not destroyed by the floor):

- count of floored rows (expected 123) and the 6 affected `idhh`;
- `c_pilot_raw` distribution (mean 4,054.29; min −812.21; the §9a per-household
  breakdown from the rebuild report);
- `c_pilot_for_norm` distribution (post-floor; min = `EPS × c_scale_pilot`);
- `EPS` value (1e-12);
- `EPS × c_scale_pilot` in EUR/month (≈4.05e-9);
- `c_scale_pilot` (4,054.2856) and the all-rows-mean rule.

`ils_dispy_male`/`ils_dispy_female` are **preserved unchanged** — the raw income
remains in the data; only `c_norm` carries the floor.

---

## 10. Flagging rule

Add a diagnostic column:

```
c_pilot_raw_nonpositive = 1[c_pilot_raw <= 0]    (int, 1 on the 123 rows, else 0)
```

This makes every floored row identifiable downstream (e.g. for a robustness check
that drops or re-weights them later) without altering the income or the floored
`c_norm`. Mark it diagnostic/non-primary in metadata. A `c_pilot` column, if
added, is likewise diagnostic/non-primary.

---

## 11. Required output parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet`
— the input's 152 columns with **`c_norm` replaced** by the floored rebuild,
**plus** `c_pilot_raw_nonpositive` (and optionally diagnostic `c_pilot`),
2,319,300 rows, chosen-first preserved. Pilot-only; input not overwritten
(HF-MUT).

**Preserved unchanged:** `draw_male`/`draw_female`/`draw_joint`,
`is_chosen`/`is_chosen_joint`/`is_chosen_male`/`is_chosen_female`,
`ils_dispy_male`/`ils_dispy_female`, the W1 wage/proposal-density columns, GSUR
(`gsur_male`/`gsur_female`), region (`reg_nuts1_2..8`, `drgn1`),
`l_norm_male`/`l_norm_female`, chosen-first sort; no scalar `draw`.

---

## 12. Required metadata sidecar

`fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json`:

- authorization (this doc); input path + row count;
- consumption object (`c_pilot_raw = ils_dispy_male + ils_dispy_female`);
- **`c_scale_pilot` = 4,054.2856** (+ all-rows-mean rule); **`c_scale =
  c_scale_pilot`**; a `normalization` block in the structure
  `precompute_data_couples` expects (flat `c_scale`/`l_scale` and/or nested
  `couples`); **preserved leisure scales** (`l_male_scale`/`l_female_scale` =
  10.0, `l_scale` = 10.0 — not recomputed);
- **explicit statement that 123 rows across 6 affected households were floored
  using normalized-EPS semantics** (`EPS = 1e-12`; `EPS × c_scale_pilot ≈
  4.05e-9` EUR/month);
- the §9 diagnostics; the `c_pilot_raw_nonpositive` flag (count, non-primary);
- a note that this is a **pilot computational-domain convention, not a final
  welfare-domain decision**;
- the §13 validations; not_run flags.

---

## 13. Required validation checks

- **Floor applied correctly:** `c_norm = max(c_pilot_raw / c_scale_pilot, EPS)`;
  exactly the rows with `c_pilot_raw / c_scale_pilot ≤ EPS` are floored (expected
  123); all others equal `c_pilot_raw / c_scale_pilot`.
- **Positivity now holds:** `c_norm > 0` on all 2,319,300 rows (= EPS on floored
  rows).
- **Rebuild identity (non-floored):** on rows not floored,
  `|c_norm × c_scale_pilot − c_pilot_raw| ≤ 1.0` EUR/month.
- **Flag correctness:** `c_pilot_raw_nonpositive` sums to 123; equals
  `1[c_pilot_raw ≤ 0]`.
- **Income preserved:** `ils_dispy_male`/`ils_dispy_female` unchanged (the floor
  touches only `c_norm`).
- **Scale:** `c_scale_pilot > 0`; `c_scale` set = `c_scale_pilot` in metadata.
- **Leisure preserved:** `l_norm_male`/`l_norm_female` and leisure scale metadata
  unchanged.
- **Structure:** 2,319,300 rows; 2,577 × 900; chosen-first (first row of each
  `(idhh, year_tag)` group has `is_chosen==1`, `draw_joint==0`); no scalar
  `draw`; all preserved columns intact.
- **No mutation:** input parquet unchanged (2,319,300 × 152); no production file
  or P3a YAML touched.

Any hard failure → halt and report.

---

## 14. Halt conditions

| Halt | Condition |
|---|---|
| **HF-EPS** | EPS cannot be located unambiguously in `precompute_data_couples` / its shared constant (expected `EPS = 1e-12`, line 49). Do NOT guess. |
| **HF-FLOOR** | Floor not applied as `max(c_norm_raw, EPS)` (e.g. an arbitrary euro floor, or `c_norm` floored to a value ≠ EPS), or floored-row count ≠ 123 without explanation. |
| **HF-POS** | Any `c_norm ≤ 0` after the floor (the floor failed to ensure positivity). |
| **HF-IDENT** | On non-floored rows, `max |c_norm × c_scale_pilot − c_pilot_raw| > 1.0`. |
| **HF-INCOME** | `ils_dispy_male`/`ils_dispy_female` altered (floor must touch only `c_norm`). |
| **HF-LEIS** | `l_norm_male`/`l_norm_female` or leisure scale metadata changed. |
| **HF-STRUCT** | Row count ≠ 2,319,300; groups ≠ 2,577×900; chosen-first broken; scalar `draw` introduced; a preserved column dropped/altered. |
| **HF-MUT** | Input parquet, any production parquet, or the frozen P3a YAML modified. |
| **HF-DROP** | Any household or row dropped (the resolution floors, it does not drop). |
| **HF-STAGE** | Any attempt to re-run EUROMOD, precompute, GSUR, estimation, welfare, SA2, promotion, or M1-clean displacement. |

Any fired halt → stop, write the report up to the halt, await direction. Do not
work around.

---

## 15. What is authorized

- Reading the input precompute-ready parquet (read-only) and confirming `EPS`
  at its source.
- Computing `c_pilot_raw`, `c_norm_raw`, the normalized-EPS-floored `c_norm`, and
  the `c_pilot_raw_nonpositive` flag.
- Writing the new `__precompute_norm_ready.parquet` (with floored `c_norm`, the
  flag, optional diagnostic `c_pilot`, everything else preserved) and its
  `__normmeta.json` (with `c_scale_pilot`, `c_scale = c_scale_pilot`, preserved
  leisure scales, the explicit floor statement + diagnostics).
- The §13 validations and the report (§17).

---

## 16. What is not authorized

- Dropping the 6 households or the 123 rows (HF-DROP).
- Re-running EUROMOD (HF-STAGE).
- An arbitrary euro floor, or any floor value ≠ the source EPS (HF-FLOOR/HF-EPS).
- Altering `ils_dispy_*` (HF-INCOME), leisure normalization (HF-LEIS), draw
  identifiers, `is_chosen*`, W1/GSUR/region columns, or chosen-first (HF-STRUCT).
- Overwriting the input parquet or any production file (HF-MUT).
- Running precompute, GSUR, estimation, welfare, SA2, promotion; M1-clean
  displacement (HF-STAGE).
- Treating this floor as the **welfare-domain** treatment of negative-income
  alternatives (it is a computational-domain convention only).

---

## 17. Required report

`Results/NC_pilot/JMP_NC_pilot_HN_POS_resolution_report_v1.md`, covering: scope and
authorization provenance; the HN-POS recap (123 rows, 6 households, real EUROMOD
negatives); the EPS source confirmation (1e-12, line 998 use); the floor formula
and `EPS × c_scale_pilot` in EUR/month; the floored-row result (count 123, the 6
`idhh`, per-household cell counts); the `c_pilot_raw` / `c_pilot_for_norm`
distributions; the `c_pilot_raw_nonpositive` flag (sum 123); the §13 validations
(positivity now holds, identity on non-floored rows, income/leisure/structure
preserved, no mutation); the metadata written (`c_scale_pilot`, `c_scale`,
preserved leisure scales, explicit floor statement, computational-not-welfare
note); halt-condition status; and required final statements (floored not dropped;
EPS from source; income/leisure preserved; no EUROMOD re-run/precompute/GSUR/
estimation/welfare/SA2/promotion; M1-clean active; P3a unaffected; HN-POS
resolution slice only).

---

## 18. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Pure pandas; read-only input; EPS from
source; one new parquet + sidecar; stop before precompute.

```text
Work locally in my RURO/MNL codebase. HN-POS RESOLUTION + c_norm REBUILD,
FR_2016 couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md. Resolution = explicit
normalized-EPS floor (NOT drop, NOT EUROMOD re-run).

HARD CONSTRAINTS (halt and report if any would be violated):
- Input READ-ONLY: do NOT overwrite the precompute-ready parquet or any
  production file. Write a NEW parquet. (HF-MUT)
- Do NOT drop the 6 households or the 123 rows. (HF-DROP)
- Do NOT re-run EUROMOD. (HF-STAGE)
- EPS MUST come from precompute_data_couples / its shared constant
  (expected EPS = 1e-12, estimation_utils.py line 49). If not locatable
  unambiguously -> HALT. Do NOT guess or use an arbitrary euro floor. (HF-EPS)
- Floor ONLY c_norm. Do NOT alter ils_dispy_male/female (HF-INCOME), leisure
  normalization (HF-LEIS), draw ids / is_chosen* / W1 / GSUR / region /
  chosen-first (HF-STRUCT).
- Do NOT run precompute/GSUR/estimation/welfare/SA2/promotion or displace
  M1-clean. (HF-STAGE)

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md
- Results/NC_pilot/JMP_NC_pilot_normalization_rebuild_report_v1.md (HN-POS detail)
- scripts/enhanced/estimation_utils.py (confirm EPS = 1e-12 @ line 49; use @ line 998)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet
- Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json (leisure scales to PRESERVE)

STEP 1 — Confirm EPS:
- Read estimation_utils.py; confirm EPS = 1e-12 and that c_norm is floored via
  np.maximum(df["c_norm"], EPS). If EPS not unambiguous -> HALT (HF-EPS).

STEP 2 — Consumption + scale:
- c_pilot_raw = ils_dispy_male + ils_dispy_female.
- c_scale_pilot = mean(c_pilot_raw) over all rows  (expect 4054.2856; record full precision).

STEP 3 — Normalized-EPS floor:
- c_norm_raw = c_pilot_raw / c_scale_pilot
- c_norm     = np.maximum(c_norm_raw, EPS)        # EPS = 1e-12
- c_pilot_raw_nonpositive = (c_pilot_raw <= 0).astype(int)
- Record EPS * c_scale_pilot in EUR/month (~4.05e-9).

STEP 4 — Validate (authorization s.13):
- floored rows == rows with c_norm_raw <= EPS (expect 123); c_pilot_raw_nonpositive
  sums to 123;
- c_norm > 0 all rows; on non-floored rows |c_norm*c_scale_pilot - c_pilot_raw|<=1.0;
- ils_dispy_male/female unchanged; l_norm_male/female + leisure scales unchanged;
- 2,319,300 rows; 2,577 groups x 900; chosen-first intact; no scalar draw;
  draw/is_chosen*/W1/GSUR/region preserved.

STEP 5 — Write NEW outputs (pilot path):
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet
= 152 cols with c_norm replaced + c_pilot_raw_nonpositive (optional diagnostic
c_pilot), 2,319,300 rows, chosen-first preserved.
Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json
with: c_scale_pilot (+rule), c_scale = c_scale_pilot, normalization block in the
structure precompute_data_couples expects, PRESERVED l_scale/l_male_scale/
l_female_scale (from mnlmeta, NOT recomputed), EXPLICIT statement that 123 rows
across 6 households were floored via normalized-EPS (EPS=1e-12,
EPS*c_scale_pilot~=4.05e-9 EUR/mo), the §9 diagnostics, and the
"computational-domain convention, not final welfare decision" note.

THEN STOP. Do not run precompute.

Halt conditions: HF-EPS, HF-FLOOR, HF-POS, HF-IDENT, HF-INCOME, HF-LEIS,
HF-STRUCT, HF-MUT, HF-DROP, HF-STAGE (authorization s.14). On any fire: STOP,
write report to that point, await direction.

Write ONE report: Results/NC_pilot/JMP_NC_pilot_HN_POS_resolution_report_v1.md per
authorization s.17. End with required final statements (floored not dropped;
EPS from source; income/leisure preserved; no EUROMOD re-run/precompute/GSUR/
estimation/welfare/SA2/promotion; M1-clean active; P3a unaffected; HN-POS
resolution slice only).
```

Save the report as:
`Results/NC_pilot/JMP_NC_pilot_HN_POS_resolution_report_v1.md`

---

## Required final statements

- **This authorizes only HN-POS resolution + the `c_norm` rebuild**, via an
  explicit normalized-EPS floor matching `precompute_data_couples`
  (`EPS = 1e-12`, from source).
- **The 6 households and 123 rows are floored, not dropped; EUROMOD is not
  re-run.**
- **Floor formula:** `c_norm = max(c_pilot_raw / c_scale_pilot, EPS)`;
  `c_scale_pilot = 4,054.2856` (all-rows mean); `c_scale = c_scale_pilot`.
- **A diagnostic `c_pilot_raw_nonpositive` flag (sum 123) is added**; raw income
  preserved; the 123 floored rows are recorded in metadata.
- **Leisure normalization preserved** (`l_*_scale = 10.0`); income columns
  unchanged; structure (2,319,300 / 2,577×900 / chosen-first / no scalar draw)
  preserved; input not overwritten.
- **This is a pilot computational-domain convention, not a final welfare-domain
  decision** on negative-income alternatives.
- **No precompute, EUROMOD re-run, GSUR, estimation, welfare, SA2, or
  promotion.** M1-clean 2016 active; corrected pooled P3a track unaffected.

---

*Status: HN-POS resolution authorization v1. Authorizes the explicit
normalized-EPS floor and `c_norm` rebuild under the §14 halts; executes nothing
itself. Next document: the resolution report (§17), then re-entry to the
precompute slice pointing at `__precompute_norm_ready.parquet` (HP-NORM cleared).*
