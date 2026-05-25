# JMP NC Pilot — Precompute-Slice Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: precompute-slice authorization, narrow.** Authorizes only
running `precompute_data_couples` on the NC pilot precompute-ready parquet,
preceded by a mandatory column-inspection gate, and writing one pilot-only
precomputed artifact + report. It does **not** change `precompute_data_couples`
logic, patch around missing columns, run GSUR, run estimation (not even
diagnostic), compute welfare, issue SA2, or promote. M1-clean 2016 remains
active. The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To exercise the couples precompute on the pilot's product-based, EUROMOD-priced
choice set — turning the 2,319,300-row precompute-ready parquet into the array
bundle the estimator consumes — and to **measure** the precompute cost
(wall time, peak memory) the feasibility audit flagged as unknown. Execution is
gated on a read-only inspection that confirms every column
`precompute_data_couples` *actually* requires is present.

---

## 2. Current status

The compatibility patch passed:

- Pilot precompute-ready parquet exists: 2,319,300 rows, 152 columns,
  `is_chosen = is_chosen_joint` present, chosen-first sorted, every
  `(idhh, year_tag)` group = 900 rows, no scalar `draw`,
  `ils_dispy_male`/`ils_dispy_female` complete.
- `estimation_utils.py::_resolve_draw_column` now resolves `draw` → else
  `draw_joint` → else fail-loud (verified: legacy `draw`-present path
  unchanged).
- No GSUR, full precompute, estimation, welfare, SA2, or promotion run.

---

## 3. Why precompute is now the next gate

Every upstream blocker is cleared: the choice set is a product (not diagonal),
wages are W1-conditioned, EUROMOD priced all 900 cells per couple, income
merged on true IDs, `is_chosen` and chosen-first ordering satisfy the
estimator's conventions, and the draw-column resolver accepts the pilot's
`draw_joint`. Precompute is the last transform before a (later, separately
authorized) diagnostic estimation. It is also the **measurement point**: its
wall time × the pooled couples factor (7,438/2,577) projects the full-cycle
precompute budget.

---

## 4. Authorized precompute entry point

`precompute_data_couples` in `scripts/enhanced/estimation_utils.py` (line 944),
**called as-is** — or a thin local pilot wrapper that calls it **without
altering its logic**. The function signature is
`precompute_data_couples(df, metadata, include_wage_vars=True,
include_loc_vars=False, include_extra_vars=None)`. For the pilot, call with
`include_wage_vars=True` (W1 wages are in the data) and `include_loc_vars=False`
(occupation is calibrated into the wage draw under `occ_spec=fixed`, not a
free precompute layer for this pilot). **The function body is not edited in
this slice** (HP-LOGIC).

---

## 5. Input parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet`
— 2,319,300 rows × 152 cols. Read-only. The function re-sorts by `(idhh,
year_tag)` internally when `year_tag.nunique() > 1` (a no-op here since
`year_tag == 2` throughout) and otherwise asserts `idhh` monotonic — the
chosen-first sort already satisfies the grouping.

---

## 6. Input metadata

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json`
— **plus** the normalization constants the function requires from a `metadata`
dict (§7). `precompute_data_couples` reads `metadata["normalization"]` and
expects either a nested `["normalization"]["couples"]["c_scale"]` /
`["l_male_scale"]` or a flat `["normalization"]["c_scale"]` / `["l_scale"]`.
**The readymeta sidecar does not currently carry a `normalization` block**, so
the pilot must supply the normalization metadata (from the pilot's own
`c_norm`/`l_norm_*` construction, or the production couples normalization
constants if the pilot reused them). The inspection gate (§7) must confirm the
normalization metadata is available and consistent with the `c_norm`/`l_norm_*`
columns; if it is absent, **halt** — do not invent constants.

---

## 7. Required columns

**Mandatory pre-execution inspection.** Before running, Claude Code must read
`precompute_data_couples` and confirm the columns it accesses **without a
`.get()`/`in df.columns` fallback** are present — these are the hard
requirements that raise `KeyError`/`ValueError` if missing. From the function
body (lines 944–1130+), the hard-required couples columns are:

- `idhh`, `year_tag` (grouping / sort)
- `draw_joint` (via `_resolve_draw_column`, since no scalar `draw`)
- `is_chosen`
- **`c_norm`** (consumption, `df["c_norm"].values` — bare access)
- **`l_norm_male`, `l_norm_female`** (leisure, bare access)
- **`hours_male`, `hours_female`** (bare access)
- **`prior`** (bare access)
- normalization metadata `c_scale` + `l_scale` (or nested `couples` variants) —
  from `metadata`, not the dataframe (§6)

With `include_wage_vars=True`, the **W1 wage columns** `wage_male`,
`wage_female`, `pexp_years_male`, `pexp_years_female` are consumed **if
present** (guarded by `in df.columns`); they are in the pilot data and should
be confirmed present so the wage layer is populated (not silently zeroed).

**Columns that are NOT hard-required (guarded, fall back to zeros with a
warning) — do NOT halt if absent, and do NOT synthesise them:**

- `ils_dispy_male`/`ils_dispy_female` are **not read directly** by
  `precompute_data_couples`; consumption enters via the pre-built `c_norm`
  (the household-sum normalization). Confirm `c_norm` exists; the income
  columns' role was upstream (they fed `c_norm` construction), so their
  presence is preserved but not consumed here.
- `gsur_male`/`gsur_female` (or `u_rate_*`): guarded → zeros + warning if
  absent.
- `drgn1`/`drgn`, `reg_nuts1_2..8`: guarded → region fallback / zeros if
  absent.
- `age_norm_*`, `educ*_*`, `n_children`: guarded via `.get(...)` → 0.0 if
  absent.

**Correction to the requested column list:** `leisure_male`/`leisure_female`
are *not* the consumed columns — the function reads `l_norm_male`/
`l_norm_female`. And `ils_dispy_male`/`ils_dispy_female` are *not* directly
required by `precompute_data_couples` (consumption is pre-normalized into
`c_norm`). The gate must check the **actual** hard-required set above, not a
superset that would false-halt on guarded columns.

**Gate rule:** if any **hard-required** column (or the normalization metadata)
is missing → **halt and report**; do not patch around it, do not synthesise it.
Missing **guarded** columns are logged (the function's own warning) and do not
halt — but the report must list which guarded fallbacks fired (GSUR zeros,
region fallback), since zeroed GSUR/region changes the opportunity index and
must be visible.

---

## 8. Draw-column handling

`precompute_data_couples` resolves the draw identifier via the patched
`_resolve_draw_column`: `draw` if present, else `draw_joint`, else fail-loud.
The pilot has `draw_joint` and no `draw`, so resolution returns `draw_joint`,
used **only** for group/choice-set identification. No scalar `draw` is added
to the data (HP-DRAW). `draw_male`/`draw_female`/`draw_joint` are preserved.

---

## 9. Chosen-row handling

The data is already chosen-first (`draw_joint == 0` at position 0 of each
`(idhh, year_tag)` group; `is_chosen == 1` iff `draw_joint == 0`). The
precompute consumes `is_chosen` and the per-group ordering as-is; this slice
adds no chosen logic and re-sorts only via the function's internal
`(idhh, year_tag)` sort (a no-op for 2016-only).

---

## 10. Normalization and metadata requirements

The pilot must pass `metadata` with a `normalization` block carrying the
couples consumption scale (`c_scale`) and leisure scale (`l_scale`/
`l_male_scale`) **consistent with the `c_norm`/`l_norm_male`/`l_norm_female`
columns already in the parquet**. The function's companion validation
(`c_norm ≈ consumption / c_scale`) must hold within tolerance. If the pilot
built `c_norm`/`l_norm_*` with known scales, supply those exact constants. If
the scales cannot be established consistently, **halt** (do not guess scales —
inconsistent normalization silently corrupts the utility index). No other
metadata is synthesised.

---

## 11. Required output path

Pilot-only. Use the repository-standard precomputed-data format actually
produced by the codebase (a `PrecomputedDataCouples` dataclass; persist via the
repo's standard mechanism — pickle or the existing serializer). Suggested path:
`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl`
(or the existing repo-standard precomputed artifact name/format). **The report
must state the exact format and path actually used.** No production precomputed
artifact is overwritten.

---

## 12. Required validation checks

- **Inspection gate passed:** all hard-required columns + normalization
  metadata present (§7); the list of any guarded fallbacks that fired (GSUR,
  region) recorded.
- **Shape:** precompute consumed 2,319,300 rows; produced arrays of length
  2,319,300 (or the function's documented per-obs array length); 2,577 groups
  of 900.
- **Draw resolution:** resolver returned `draw_joint` (no scalar `draw`
  created).
- **Normalization consistency:** `c_norm ≈ consumption/c_scale`,
  `l_norm_* ≈ leisure_*/l_scale` within the function's tolerance (no warning
  escalated to error).
- **Finiteness:** core precomputed arrays (`log_c`, `log_l_male`,
  `log_l_female`, `prior`) finite; `prior > 0` (EPS-floored), consumption and
  leisure EPS-floored as the function does.
- **No mutation:** the precompute-ready parquet unchanged (2,319,300 × 152);
  no production parquet or YAML modified; `precompute_data_couples` body
  unchanged (diff empty for the function).
- **Wage layer populated:** with `include_wage_vars=True`, `log_wage_male`/
  `log_wage_female` non-None (W1 wages consumed, not zeroed).

Any hard-required failure → halt and report.

---

## 13. Wall-time and memory capture

Capture and record in the report: precompute wall time (seconds) and peak
resident memory if feasible (e.g. `tracemalloc` peak or RSS delta). These are
the slice's measurement deliverable — the per-2,577-couple, 900-alt precompute
cost that, scaled by 7,438/2,577 (pooled couples) and re-checked at 1,600
alts, sizes the full-cycle precompute budget.

---

## 14. Halt conditions

| Halt | Condition |
|---|---|
| **HP-LOGIC** | Any edit to `precompute_data_couples` (or `_resolve_draw_column`) logic. The function is called, not changed. |
| **HP-COL** | Any hard-required column (`c_norm`, `l_norm_male`, `l_norm_female`, `hours_male`, `hours_female`, `prior`, `idhh`, `year_tag`, `is_chosen`, `draw_joint`) or the normalization metadata is missing. Halt; do NOT patch around or synthesise. |
| **HP-SYNTH** | Any synthetic column is created that `precompute_data_couples` does not create internally. |
| **HP-NORM** | Normalization scales cannot be established consistently with `c_norm`/`l_norm_*` (validation exceeds tolerance, or scales unknown). |
| **HP-DRAW** | A scalar `draw` (or `draw = draw_joint`) is written into the data. |
| **HP-MUT** | The precompute-ready parquet, any production parquet, or the frozen P3a YAML is modified. |
| **HP-STAGE** | Any attempt to run GSUR, estimation (incl. diagnostic), welfare, SA2, promotion, or M1-clean displacement. |

Any fired halt → stop, write the report up to the halt, await direction. Do
not work around (especially: do not synthesise a missing hard-required column
or guess a normalization scale).

---

## 15. What is authorized

- Reading `precompute_data_couples` and performing the §7 inspection gate.
- Running `precompute_data_couples` (as-is, or via a logic-preserving wrapper)
  on the pilot precompute-ready parquet with `include_wage_vars=True,
  include_loc_vars=False`.
- Supplying the consistent normalization metadata (§10).
- Persisting the `PrecomputedDataCouples` artifact under the pilot path (§11).
- Capturing wall time / memory (§13).
- The §12 validations and the report (§17).

---

## 16. What is not authorized

- Editing `precompute_data_couples` or `_resolve_draw_column` logic (HP-LOGIC).
- Patching around or synthesising any missing hard-required column (HP-COL,
  HP-SYNTH).
- Adding a scalar `draw` to the data (HP-DRAW).
- Running GSUR; estimation (including a diagnostic run); welfare; SA2;
  promotion; M1-clean displacement (HP-STAGE).
- Modifying the precompute-ready parquet, any production parquet/data, or the
  frozen P3a YAML (HP-MUT).

---

## 17. Required precompute report

`Results/JMP_NC_pilot_precompute_report_v1.md`, covering: scope and
authorization provenance; the §7 inspection-gate result (hard-required columns
confirmed present; normalization metadata source; which guarded fallbacks fired
— GSUR zeros, region fallback — and the opportunity-index implication);
the precompute run (entry point, `include_wage_vars`/`include_loc_vars`,
draw resolution = `draw_joint`); output (exact format + path actually used,
array lengths, 2,577×900 group structure); the §12 validations (shape,
normalization consistency, finiteness, wage-layer populated, no mutation);
**measured wall time and peak memory** (§13) with the pooled-cycle projection;
halt-condition status (none/which fired); and required final statements (no
logic change; no synthetic columns; no GSUR/estimation/welfare/SA2/promotion;
M1-clean active; P3a unaffected; precompute slice only).

---

## 18. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Inspection gate first; run precompute;
persist one pilot artifact; stop before estimation.

```text
Work locally in my RURO/MNL codebase. PRECOMPUTE SLICE, FR_2016 couples pilot.
Authorized by docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md.

HARD CONSTRAINTS (halt and report if any would be violated):
- Do NOT edit precompute_data_couples or _resolve_draw_column logic. Call
  as-is (or a logic-preserving wrapper). (HP-LOGIC)
- Do NOT synthesise or patch around any missing hard-required column.
  If a hard-required column or normalization metadata is missing -> HALT. (HP-COL/HP-SYNTH)
- Do NOT add a scalar 'draw' to the data. (HP-DRAW)
- Do NOT modify the precompute-ready parquet, any production parquet, or the
  frozen P3a YAML. (HP-MUT)
- Do NOT run GSUR / estimation (not even diagnostic) / welfare / SA2 /
  promotion / M1-clean displacement. (HP-STAGE)

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md
- scripts/enhanced/estimation_utils.py (precompute_data_couples @ line 944;
  _resolve_draw_column @ line 59)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet (schema)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json

STEP 1 — INSPECTION GATE (mandatory, before running):
- Read precompute_data_couples and enumerate columns it accesses via BARE
  df["..."] (hard-required) vs guarded (.get / "in df.columns" -> zeros/warn).
- Confirm hard-required present in the parquet: idhh, year_tag, draw_joint,
  is_chosen, c_norm, l_norm_male, l_norm_female, hours_male, hours_female,
  prior.
- Confirm normalization metadata (c_scale + l_scale, or nested couples
  variants) is AVAILABLE and consistent with c_norm/l_norm_* (validation
  c_norm ~= consumption/c_scale within tolerance). Source it from the pilot's
  own normalization (or production couples constants if the pilot reused them).
- With include_wage_vars=True, confirm wage_male/wage_female/pexp_years_male/
  pexp_years_female PRESENT (so the wage layer is populated, not zeroed).
- RECORD which guarded fallbacks WILL fire (gsur_male/female or u_rate_*
  absent -> zeros; drgn1/drgn or reg_nuts1_* absent -> region fallback/zeros).
- If ANY hard-required column or the normalization metadata is missing: HALT,
  write the report listing exactly what is missing. Do NOT synthesise.

STEP 2 — RUN precompute (only if gate passes):
- Call precompute_data_couples(df, metadata, include_wage_vars=True,
  include_loc_vars=False) on the precompute-ready parquet, with the consistent
  normalization metadata.
- Wrap in wall-time timing and (if feasible) tracemalloc/RSS peak capture.

STEP 3 — PERSIST (pilot-only):
- Save the PrecomputedDataCouples artifact using the repo-standard format
  (pickle or the existing serializer) to
  Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl
  (or the repo-standard name/format). REPORT the exact format + path used.

STEP 4 — VALIDATE (authorization s.12):
- consumed 2,319,300 rows; arrays length 2,319,300; 2,577 groups x 900;
- draw resolution returned draw_joint (no scalar draw created);
- normalization consistency within tolerance (no warning escalated to error);
- log_c / log_l_male / log_l_female / prior finite; prior>0;
- log_wage_male / log_wage_female non-None (wage layer populated);
- precompute-ready parquet unchanged (2,319,300 x 152); no production file
  modified; precompute_data_couples body unchanged (empty function diff).

THEN STOP. Do not run estimation.

Halt conditions: HP-LOGIC, HP-COL, HP-SYNTH, HP-NORM, HP-DRAW, HP-MUT,
HP-STAGE (authorization s.14). On any fire: STOP, write report to that point,
await direction.

Write ONE report: Results/JMP_NC_pilot_precompute_report_v1.md per
authorization s.17, INCLUDING measured wall time + peak memory and the
pooled-cycle projection. End with required final statements (no logic change;
no synthetic columns; no GSUR/estimation/welfare/SA2/promotion; M1-clean
active; P3a unaffected; precompute slice only).
```

Save the report as: `Results/JMP_NC_pilot_precompute_report_v1.md`

---

**Required final statements:**

- **This authorizes only the pilot couples precompute slice** —
  `precompute_data_couples` called as-is on the pilot precompute-ready parquet,
  after a mandatory column-inspection gate.
- **The inspection gate is binding:** missing hard-required column or
  normalization metadata → halt; no patching around, no synthetic columns.
- **Draw resolution uses the patched logic** (`draw` → `draw_joint` →
  fail-loud); no scalar `draw` added to the data.
- **`precompute_data_couples` logic is not changed**; the precompute-ready
  parquet and all production files are unmodified.
- **Wall time and peak memory are captured** as the slice's measurement
  deliverable.
- **No GSUR, estimation (incl. diagnostic), welfare, SA2, or promotion.**
  M1-clean 2016 active; corrected pooled P3a track unaffected.

---

*Status: precompute-slice authorization v1. Authorizes the gated couples
precompute and one pilot artifact under the §14 halts; executes nothing
itself. Next document: the precompute report (§17), then a separate diagnostic-
estimation authorization slice.*
