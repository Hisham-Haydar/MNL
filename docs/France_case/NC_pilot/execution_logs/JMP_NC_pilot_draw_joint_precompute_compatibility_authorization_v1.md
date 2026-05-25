# JMP NC Pilot — draw_joint Precompute-Compatibility Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: production-code patch authorization, narrow.** Authorizes
a single, surgical change to `estimation_utils.py` — the draw-identifier
resolution used for couples choice-set/group construction — to accept
`draw_joint` when a scalar `draw` is absent, while leaving legacy production
behaviour byte-identical. It does **not** add a scalar `draw` to the pilot
parquet, change any likelihood/income/region/parameter logic, run GSUR,
precompute, estimation, welfare, SA2, or promotion. M1-clean 2016 remains
active. The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To resolve the last precompute blocker: `estimation_utils.py` expects a column
named `draw` in the couples group-builder, but the NC pilot's precompute-ready
parquet carries `draw_male`/`draw_female`/`draw_joint` and **no** scalar
`draw` (by design — HC-DRAW). This authorizes **Option B**: teach the
group-builder's draw-identifier resolution to fall back to `draw_joint` when
`draw` is absent, rather than aliasing `draw = draw_joint` into the data
(Option A, rejected — §4).

---

## 2. Current precompute-readiness status

The precompute-readiness slice passed (readymeta v1, 12.3 s):

- `fr_pilot_nc_2016_couples_product__precompute_ready.parquet`: **2,319,300
  rows**, 152 columns (151 + `is_chosen`).
- `is_chosen = is_chosen_joint` added (int, copy; `is_chosen==1` iff
  `draw_joint==0`).
- Chosen-first sort on `(idhh, year_tag, draw_joint)`: first row of every
  group has `draw_joint==0` and `is_chosen==1` (V10/V11 PASS).
- Every `(idhh, year_tag)` group = 900 rows (2,577 groups; V4 PASS).
- `draw_male`/`draw_female`/`draw_joint` are the only draw identifiers; **no
  scalar `draw`** (V17 PASS).
- `ils_dispy_male`/`ils_dispy_female` complete (V12/V13 PASS).
- No GSUR/precompute/estimation/welfare/SA2/promotion.

The data is precompute-ready in every respect except the group-builder's
hard expectation of a `draw` column — a code expectation, not a data defect.

---

## 3. Compatibility blocker

The couples group-builder in `estimation_utils.py` references a column named
`draw` to construct/identify choice-set groups (the re-pointing audit flagged
this site, alongside the position-0 chosen-row assumption already resolved by
the readiness sort). On the pilot parquet — which deliberately has no scalar
`draw` — that reference raises `KeyError`. This is the documented final
blocker from the readiness report.

The blocker is purely the *identifier-resolution* step. The likelihood
computation, income routing, region-dummy logic, and parameter handling do
not need a scalar `draw`; only the group-builder's column lookup does.

---

## 4. Why scalar draw alias is not preferred

Option A (add `draw = draw_joint` to the pilot parquet) is rejected:

1. **It reintroduces the forbidden alias.** The re-pointing audit and every
   subsequent slice forbade `draw = draw_joint` because the joint key (0..899)
   is not interchangeable with the production scalar `draw` (0..N marginal) —
   they have different semantics and ranges, and conflating them risks
   `id_multiplier`/draw-arithmetic confusion downstream (the same hazard that
   forced Strategy B/C′ apart at EUROMOD).
2. **It mutates clean data to fit stale code.** The readiness parquet is
   correct as-is; adding a semantically-loaded scalar to placate one lookup
   pushes a fragile compatibility shim into the *data*, where it propagates to
   every future consumer, instead of into the *code*, where it can be scoped
   and reasoned about.
3. **It is harder to make backward-safe.** A data alias would have to be
   stripped or special-cased everywhere production logic reads `draw`; a code
   fallback isolates the change to one resolution point.

Option B (code fallback) keeps the data honest and the change auditable.

---

## 5. Authorized patch

A single change to `estimation_utils.py`: at the draw-identifier resolution
used by the couples choice-set/group construction, replace the direct `draw`
column reference with a **resolution helper** implementing the §6 rule. The
patch:

- Touches **only** the draw-identifier resolution for group/choice-set
  construction.
- Does **not** change likelihood formulas, income routing
  (`ils_dispy_male`/`ils_dispy_female`), region-dummy logic, or parameter
  handling.
- Does **not** modify any data file (the pilot parquet and all production
  parquets are read-only here).
- Is additive and backward-compatible: legacy data with a scalar `draw`
  resolves to `draw` exactly as before; the new branch fires only when `draw`
  is absent.

Where feasible, factor the rule into a small named function (e.g.
`_resolve_draw_column(df)`) so the fallback is testable and the change is one
reviewable unit rather than scattered inline edits.

---

## 6. Required draw-column resolution rule

```
def _resolve_draw_column(df):
    if "draw" in df.columns:
        return df["draw"]            # legacy production: unchanged
    elif "draw_joint" in df.columns:
        return df["draw_joint"]      # NC pilot: joint key as the group draw id
    else:
        raise <loud error>          # neither present: fail loudly, do not guess
```

- **`draw` present → use `draw`.** Legacy production (P3a, M1-clean, singles)
  behaves exactly as before; the new code path is never entered.
- **`draw` absent, `draw_joint` present → use `draw_joint`** as the
  group/choice-set draw identifier. This is the pilot path.
- **Neither present → fail loudly** with a clear error naming both expected
  columns. No silent default, no synthesised index.

The resolved series is used **only** for group/choice-set identification. It is
not written back to the dataframe, not renamed to `draw`, and not used to
construct IDs or draw arithmetic.

---

## 7. Required safeguards for legacy data

- **Legacy production data with scalar `draw` must behave unchanged** — same
  groups, same ordering, same results. The fallback branch must be
  unreachable when `draw` exists; verify by confirming the `draw`-present path
  is identical to the pre-patch code path (ideally the literal same expression).
- **No production parquet is read-modified-written.** P3a singles/couples and
  M1-clean data are untouched.
- **Frozen P3a YAML untouched.**
- The patch must not change column dtypes, group keys (still `(idhh,
  year_tag)` or the production equivalent), or sort assumptions for legacy
  data.

---

## 8. Required validation checks

- **Legacy-unchanged (regression):** on a production-shaped fixture (or a
  representative production parquet, read-only), the group-builder produces
  identical group structure with the patch as without — the `draw`-present
  path is byte-for-byte equivalent. (A focused unit test on
  `_resolve_draw_column` covering all three branches is the minimum.)
- **Pilot-accepted:** the group-builder runs on
  `fr_pilot_nc_2016_couples_product__precompute_ready.parquet` without
  `KeyError`; resolves the draw id from `draw_joint`; yields 2,577 groups of
  900.
- **Fail-loud:** a fixture with neither `draw` nor `draw_joint` raises the
  explicit error (not a `KeyError` from a downstream line, not a silent
  empty/NaN).
- **No data mutation:** the pilot precompute-ready parquet is unchanged
  (2,319,300 × 152; `draw_male`/`draw_female`/`draw_joint` intact; still no
  scalar `draw`); no production parquet modified.
- **Scope:** `git diff` (or equivalent) shows changes confined to the
  draw-resolution site(s) in `estimation_utils.py`; no edits to likelihood,
  income, region, or parameter code.

This authorization permits **running the group-builder far enough to validate
resolution** (it must construct groups to confirm 2,577×900 and no KeyError),
but **not** the full precompute, and nothing downstream.

---

## 9. What is authorized

- Patching the draw-identifier resolution in `estimation_utils.py` per §5–§6
  (preferably via a small `_resolve_draw_column` helper).
- Adding a unit test for the three-branch rule and a regression check that the
  `draw`-present path is unchanged.
- Running the couples group-builder **only** to validate resolution on the
  pilot parquet (groups built; 2,577×900; no KeyError) and on a legacy fixture.
- Writing the patch report (§12).

---

## 10. What is not authorized

- Adding `draw = draw_joint` (or any scalar `draw`) to the pilot parquet or any
  data file (Option A, rejected).
- Any change to likelihood formulas, income routing, region-dummy logic, or
  parameter handling.
- Modifying P3a data, M1-clean data, singles production data, or the frozen
  P3a YAML.
- Running GSUR, the full precompute, estimation, welfare, SA2, or canonical
  promotion; M1-clean displacement.
- Editing any production script other than the single
  draw-resolution site in `estimation_utils.py`.

---

## 11. Halt conditions

| Halt | Condition |
|---|---|
| **HD1** | Any edit outside the draw-resolution site in `estimation_utils.py` (likelihood, income routing, region, parameters, or any other file). |
| **HD2** | A scalar `draw` (or `draw = draw_joint`) is written into the pilot parquet or any data file. |
| **HD3** | The `draw`-present (legacy) path is not byte-for-byte equivalent to the pre-patch behaviour, or the regression check shows any change to legacy group construction. |
| **HD4** | The neither-present case does not fail loudly (silent default, NaN, or a misleading downstream error instead of the explicit error). |
| **HD5** | The pilot precompute-ready parquet is modified (row/col count change; `draw_male`/`draw_female`/`draw_joint` altered; scalar `draw` introduced). |
| **HD6** | Any production parquet or the frozen P3a YAML is modified. |
| **HD-STAGE** | Any attempt to run GSUR, full precompute, estimation, welfare, SA2, promotion, or M1-clean displacement. |

Any fired halt → stop, write the report up to the halt, await direction. Do
not work around (especially: do not resolve a failure by adding a data-side
alias).

---

## 12. Required patch report

`Results/NC_pilot/JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md`,
covering: scope and authorization provenance; the exact `estimation_utils.py`
site(s) changed (file, function, line range, the `_resolve_draw_column`
helper); the three-branch rule as implemented; the regression result
(legacy `draw`-present path unchanged); the pilot-accepted result
(group-builder runs on the precompute-ready parquet, 2,577×900, no KeyError);
the fail-loud result (neither-present fixture raises the explicit error); the
no-data-mutation confirmation (pilot parquet 2,319,300×152 unchanged, no
scalar `draw`; no production parquet touched); the diff-scope confirmation;
halt-condition status (none/which fired); and required final statements (no
data alias; legacy unchanged; no GSUR/full-precompute/estimation/welfare/SA2/
promotion; M1-clean active; P3a unaffected; compatibility-patch slice only).

---

## 13. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Single-site code patch + tests; no data
mutation; validate resolution only; stop before full precompute.

```text
Work locally in my RURO/MNL codebase. DRAW-RESOLUTION COMPATIBILITY PATCH,
FR_2016 couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md.
Option B (code fallback), NOT Option A (data alias).

HARD CONSTRAINTS (halt and report if any would be violated):
- Patch ONLY the draw-identifier resolution used by the couples
  choice-set/group construction in estimation_utils.py. Do NOT touch
  likelihood formulas, income routing (ils_dispy_male/female), region-dummy
  logic, or parameter handling. (HD1)
- Do NOT add a scalar 'draw' or draw = draw_joint to the pilot parquet or any
  data file. (HD2)
- Legacy 'draw'-present path must be byte-for-byte unchanged. (HD3)
- Do NOT modify the pilot precompute-ready parquet, any production parquet, or
  the frozen P3a YAML. (HD5/HD6)
- Do NOT run GSUR / full precompute / estimation / welfare / SA2 / promotion.
  (HD-STAGE)

Read (read-only except the single patch site):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md
- Results/NC_pilot/JMP_NC_pilot_precompute_readiness_report_v1.md
- Results/NC_pilot/JMP_NC_pilot_draw_joint_repointing_audit_v1.md (the draw-column site)
- scripts/.../estimation_utils.py (the couples group-builder)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet (schema)

STEP 1 — Locate: find the exact site(s) in estimation_utils.py where the
couples group-builder references the 'draw' column for choice-set/group
construction. Confirm it is the resolution step only (not likelihood/income/
region/parameter code).

STEP 2 — Patch (Option B): introduce a small helper
  def _resolve_draw_column(df):
      if "draw" in df.columns: return df["draw"]
      elif "draw_joint" in df.columns: return df["draw_joint"]
      else: raise <explicit error naming both expected columns>
and route the group-builder's draw-id reference through it. The
'draw'-present branch must reproduce the pre-patch expression exactly. The
resolved series is used ONLY for group identification; do NOT write it back,
rename it to 'draw', or use it for ID/draw arithmetic.

STEP 3 — Tests / validation:
- Unit test _resolve_draw_column on all three branches (draw present;
  draw_joint present, draw absent; neither -> raises).
- Regression: on a production-shaped fixture (or a read-only production
  parquet), confirm group construction is identical with vs without the patch.
- Pilot-accept: run the group-builder on the precompute-ready parquet far
  enough to confirm it resolves draw_joint, builds 2,577 groups x 900, no
  KeyError. Do NOT run the full precompute.

STEP 4 — Confirm no mutation:
- pilot precompute-ready parquet unchanged (2,319,300 x 152; draw_male/
  draw_female/draw_joint intact; no scalar 'draw');
- no production parquet modified; frozen P3a YAML untouched;
- git diff confined to the draw-resolution site(s) in estimation_utils.py.

THEN STOP. Do not begin GSUR / full precompute / estimation.

Halt conditions: HD1, HD2, HD3, HD4, HD5, HD6, HD-STAGE (authorization s.11).
On any fire: STOP, write the report to that point, await direction. Do NOT
resolve a failure by adding a data-side alias.

Write ONE report:
Results/NC_pilot/JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md
per authorization s.12. End with required final statements (no data alias;
legacy unchanged; no GSUR/full-precompute/estimation/welfare/SA2/promotion;
M1-clean active; P3a unaffected; compatibility-patch slice only).
```

Save the report as:
`Results/NC_pilot/JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md`

---

**Required final statements:**

- **This authorizes Option B only:** patch `estimation_utils.py` draw
  resolution to accept `draw_joint` when `draw` is absent. No scalar `draw` is
  added to the pilot parquet (Option A rejected).
- **Resolution rule:** `draw` if present, else `draw_joint`, else fail loudly.
- **Legacy production data with scalar `draw` behaves unchanged**; pilot NC
  data with `draw_joint` and no `draw` is accepted.
- **Patch scope is the draw-identifier resolution only** — no change to
  likelihood, income routing, region-dummy logic, or parameter handling; no
  data file modified; frozen P3a YAML untouched.
- **`draw_male`/`draw_female`/`draw_joint` preserved; the precompute-ready
  parquet unaltered.**
- **No GSUR, full precompute, estimation, welfare, SA2, or promotion.**
  M1-clean 2016 active; corrected pooled P3a track unaffected.

---

*Status: draw_joint precompute-compatibility authorization v1. Authorizes a
single backward-compatible code fallback in `estimation_utils.py` under the
§11 halts; executes nothing itself. Next document: the patch report (§12),
then a separate full-precompute authorization slice.*
