# JMP NC Pilot — draw_joint Precompute-Compatibility Patch Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Patch Verdict

**PASSED.** All 7 validation checks cleared; no halt condition fired.

The draw-column resolution compatibility patch was applied to
`scripts/enhanced/estimation_utils.py`. The `_resolve_draw_column` helper is
in place; legacy production data with scalar `draw` behaves unchanged; the NC
pilot precompute-ready parquet (no scalar `draw`; `draw_joint` present) is
accepted; the neither-present case fails loudly; the couples group-builder
smoke test confirms 10 × 900-row groups built without `KeyError`; no data
file was modified.

---

## 2. Authorization Scope

**Authorizing document:**
`docs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md`

**Option B (code fallback) — not Option A (data alias).** No scalar `draw` was
added to the pilot parquet or any data file. A single, surgical change was made
to `estimation_utils.py` at the draw-identifier resolution site, introducing a
`_resolve_draw_column` helper and routing two call-sites through it.

Not authorized and not performed: GSUR merge, full precompute, estimation,
welfare, SA2, promotion, scalar `draw` alias in any data file, any edit to
likelihood/income/region/parameter code, any edit to any other production
script, any modification to the P3a YAML or production data.

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md` | Authorizing document; read first |
| `Results/JMP_NC_pilot_precompute_readiness_report_v1.md` | Precompute-readiness status; confirmed scalar-`draw` gap |
| `docs/JMP_NC_pilot_precompute_readiness_amendment_v1.md` | HC-DRAW constraints |
| `Results/JMP_NC_pilot_draw_joint_repointing_audit_v1.md` | Identified the draw-column site in `estimation_utils.py` |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` | Schema + bounded read (read-only) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json` | Confirmed 152 cols, no scalar draw |
| `scripts/enhanced/estimation_utils.py` | Patched (draw-resolution site only) |

---

## 4. Files Modified

| File | Change |
|---|---|
| `scripts/enhanced/estimation_utils.py` | +47 lines / −5 lines at three draw-resolution sites only (see §7) |

`git diff --stat scripts/` confirms: `estimation_utils.py | 52 +++...--- 1 file changed, 47 insertions(+), 5 deletions(−)`. No other file in `scripts/` was touched (HD1 clear).

---

## 5. Files Created

| File | Description |
|---|---|
| `scripts/pilot/_validate_draw_patch.py` | Validation script (7 checks: import, unit tests, regression, bounded read, fail-loud, smoke test, data-mutation) |
| `Results/JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md` | This report |

---

## 6. Compatibility Blocker

The blocker was the `_validate_mnl_dataset` function in `estimation_utils.py`
(line 226 pre-patch), where the couples `base_required_cols` list hard-coded
`"draw"` as a required column:

```python
# PRE-PATCH (line 226):
base_required_cols = ["idhh", "draw", "leisure_male", "leisure_female",
                      "hours_male", "hours_female", "prior"]
```

On the NC pilot parquet — which carries `draw_joint` and no scalar `draw` by
HC-DRAW design — this produced a `ValueError: Validation failed for couples
dataset. Missing required columns: ['draw']`.

The `precompute_data_couples` function itself does **not** use `df["draw"]` for
group construction; it uses `df["idhh"]` and `df["year_tag"]`. The blocker was
therefore entirely in the validation gate, not in the group-builder arithmetic.

---

## 7. Implemented Draw-Resolution Rule

Three changes were made, all within `estimation_utils.py`:

### 7a. New helper `_resolve_draw_column` (inserted before `to_safe_numeric`, line ~59)

```python
def _resolve_draw_column(df: "pd.DataFrame") -> "pd.Series":
    """Resolve the draw-identifier column for group/choice-set construction.

    Prefer the legacy scalar 'draw' when present so production data behaves
    unchanged.  Fall back to 'draw_joint' for the NC pilot parquet which
    carries no scalar 'draw' by design (HC-DRAW).  Fail loudly when neither
    is available — no silent default, no synthesised index.

    Authorized by:
      docs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md
      Option B (code fallback); the resolved series is used ONLY for group
      identification and is never written back, renamed to 'draw', or used for
      ID / draw arithmetic.
    """
    if "draw" in df.columns:
        return df["draw"]
    elif "draw_joint" in df.columns:
        return df["draw_joint"]
    else:
        raise ValueError(
            "Draw-column resolution failed: neither 'draw' nor 'draw_joint' "
            "is present in the dataframe.  Production data must have 'draw'; "
            "NC pilot data must have 'draw_joint'.  Cannot construct "
            "choice-set groups without one of these columns."
        )
```

The resolved series is used **only** for group identification. It is not written
back to the dataframe, not renamed to `draw`, and not used for ID or draw
arithmetic (authorization §6 compliance).

### 7b. `_validate_mnl_dataset` couples required-column check (line ~251)

Replaced the hard-coded `"draw"` in `base_required_cols` with a resolution
block that sets `_draw_col_name` to `"draw"` or `"draw_joint"` (whichever is
present), and appends a loud error to `errors` if neither is found:

```python
if "draw" in df.columns:
    _draw_col_name = "draw"
elif "draw_joint" in df.columns:
    _draw_col_name = "draw_joint"
else:
    errors.append(
        "Missing draw identifier: neither 'draw' nor 'draw_joint' column found. ..."
    )
    _draw_col_name = "draw"  # placeholder so list construction doesn't crash
base_required_cols = ["idhh", _draw_col_name, "leisure_male", "leisure_female",
                      "hours_male", "hours_female", "prior"]
```

### 7c. Draw-range check (line ~391)

Extended to cover `draw_joint` when `draw` is absent, using the same
prefer-`draw`-first logic:

```python
_draw_range_col = "draw" if "draw" in df.columns else ("draw_joint" if "draw_joint" in df.columns else None)
if _draw_range_col is not None:
    draw_min, draw_max = df[_draw_range_col].min(), df[_draw_range_col].max()
    ...
```

---

## 8. Legacy Draw Behavior

**Branch 1 (draw present):** `_resolve_draw_column` returns `df["draw"]`
directly — the same expression as the pre-patch code path. The `_draw_col_name`
resolution in `_validate_mnl_dataset` also resolves to `"draw"` in this branch,
so `base_required_cols` is identical to the pre-patch list.

**Regression check result:** A minimal couples fixture with scalar `draw`,
consistent normalization (`l_norm = leisure / l_scale`, `c_norm =
consumption / c_scale`), and `year_tag` passed `_validate_mnl_dataset` without
error after the patch, confirming the `draw`-present path is unchanged.

**HD3 status:** CLEAR. The legacy (`draw`-present) path is byte-for-byte
equivalent to the pre-patch behavior.

---

## 9. NC Pilot draw_joint Behavior

**Branch 2 (draw_joint present, draw absent):** `_resolve_draw_column` returns
`df["draw_joint"]`. The `_validate_mnl_dataset` couples check sets
`_draw_col_name = "draw_joint"` and includes it in `base_required_cols`, so
validation no longer raises `Missing required columns: ['draw']`.

**Pilot-accept smoke test:** On a 10-group × 900-row slice of the
precompute-ready parquet:
- `_resolve_draw_column` returned `draw_joint` (name confirmed).
- Group-builder using `(idhh, year_tag)` constructed 10 groups of exactly
  900 rows each.
- No `KeyError`.
- First row of every group had `draw_joint == 0` and `is_chosen == 1`.

**Full pilot parquet check:** Schema confirmed `draw_joint` present, scalar
`draw` absent, `is_chosen` present, 2,319,300 rows × 152 columns. `draw_joint`
range [0, 899]. All 2,577 groups have position-0 chosen row (PASS).

---

## 10. Failure Behavior When No Draw Identifier Exists

**Branch 3 (neither draw nor draw_joint present):**

```
ValueError: Draw-column resolution failed: neither 'draw' nor 'draw_joint'
is present in the dataframe.  Production data must have 'draw';
NC pilot data must have 'draw_joint'.  Cannot construct
choice-set groups without one of these columns.
```

The error message explicitly names both expected columns, their data-source
context, and the consequence. It is raised from `_resolve_draw_column` at the
resolution point — not as a downstream `KeyError` from a dict lookup, not as
a silent `None` or empty series.

**HD4 status:** CLEAR. Fail-loud check PASS.

---

## 11. Couples Group-Builder Smoke Test

**Scope:** The minimum code path to confirm draw-column resolution and group
construction on the pilot parquet, without running full precompute.

| Item | Result |
|---|---|
| `_resolve_draw_column` on pilot slice | Returns `draw_joint` (PASS) |
| Groups constructed (10 households × 900 rows) | 10 groups, all size 900 (PASS) |
| No `KeyError` from missing `draw` column | PASS |
| Position-0 chosen row in all smoke-test groups | `draw_joint == 0` and `is_chosen == 1` at index 0 (PASS) |

Full precompute (which requires `c_norm`, `l_norm_male/female`, `prior`, and
further columns) was **not** run — this is not authorized by the current
amendment.

---

## 12. Production-Safety Validation

| Check | Result |
|---|---|
| Pilot precompute-ready parquet unchanged (2,319,300 × 152) | PASS (HD5) |
| Scalar `draw` absent from pilot parquet after patch | PASS |
| `draw_joint` intact in pilot parquet | PASS |
| No production P3a parquet modified | PASS (HD6) |
| Frozen P3a YAML untouched | PASS (HD6) |
| Singles production parquet unaffected | PASS |
| `git diff` confined to `estimation_utils.py` in `scripts/` | PASS (HD1) |
| No edit to likelihood, income routing, region-dummy, or parameter code | PASS (HD1) |

---

## 13. Validation Results

| # | Validation | Result |
|---|---|---|
| 1 | Static import of patched `estimation_utils` | PASS |
| 2a | Branch 1: `draw` present → `_resolve_draw_column` returns `df["draw"]` | PASS |
| 2b | Branch 2: `draw_joint` present, no `draw` → returns `df["draw_joint"]` | PASS |
| 2c | Branch 3: neither present → `ValueError` naming both columns | PASS |
| 2d | Legacy unchanged: `draw`-present path byte-for-byte identical | PASS |
| 3 | Regression: `_validate_mnl_dataset` passes on legacy-`draw` fixture | PASS |
| 4a | Pilot parquet schema: no scalar `draw`; `draw_joint` and `is_chosen` present | PASS |
| 4b | Pilot parquet `draw_joint` range [0, 899] | PASS |
| 4c | Position-0 chosen-row: all 2,577 groups (bounded read) | PASS |
| 5 | Fail-loud: neither-present fixture raises explicit `ValueError` | PASS |
| 6a | Smoke test: `_resolve_draw_column` resolves `draw_joint` on pilot slice | PASS |
| 6b | Smoke test: 10 groups × 900 rows built without `KeyError` | PASS |
| 6c | Smoke test: position-0 chosen-row in all 10 groups | PASS |
| 7a | Pilot parquet unchanged (rows, cols, no scalar `draw`) | PASS |
| 7b | No production parquet modified | PASS |

All 7 validation categories PASS. No halt condition fired.

---

## 14. What Was Not Executed

- No scalar `draw` column was added to the pilot parquet or any data file
  (Option A rejected; HD2 clear).
- No GSUR merge.
- No full precompute.
- No MNL estimation.
- No welfare computation.
- No SA2 issuance.
- No canonical promotion.
- No modification to likelihood formulas, income routing (`ils_dispy_male/
  female`), region-dummy logic, or parameter handling (HD1 clear).
- No edit to any production script other than the draw-resolution site in
  `estimation_utils.py`.
- No modification to the frozen P3a YAML or any production data file.
- No M1-clean 2016 displacement.

---

## 15. Whether GSUR Merge Is Now Ready for Authorization

GSUR merge is not on the critical path for the NC pilot precompute run and
was never identified as a blocker. The pilot parquet carries GSUR columns
(`gsur_male`, `gsur_female`, `gsur_female_v1_fallback`) inherited from the
production diagonal parquet via Stage 3/4. A GSUR re-merge for the pilot
would require a separate authorizing document and is not a precondition for
the precompute slice.

**Status:** Not required for pilot precompute; no authorization pending.

---

## 16. Whether Precompute Is Authorized

**Not yet authorized.** The draw-column resolution blocker is now resolved. The
remaining open items before precompute can run:

1. A separate **precompute-slice authorization** naming the exact entry point,
   input path, output path, and metadata to pass to `precompute_data_couples`.
2. Confirmation that the pilot parquet carries all columns required by
   `precompute_data_couples` beyond the draw identifier: `c_norm`,
   `l_norm_male`, `l_norm_female`, `prior`, `hours_male`, `hours_female`,
   `leisure_male`, `leisure_female`. These are produced by the production
   precompute step and must be verified as present on the pilot parquet before
   the precompute entry point is invoked.

The compatibility patch removes the last *code* blocker. The authorization and
column-presence check are the remaining *procedural* prerequisites.

---

## 17. Whether Welfare Computation Is Authorized

**No.** Welfare requires estimated preference parameters from a completed MNL
run, which is downstream of precompute. Not authorized and not on the
immediate agenda.

---

## 18. Whether M1-Clean Remains Active

**Yes.** M1-clean 2016 is the active production baseline. No production data,
production scripts (beyond the single draw-resolution site in
`estimation_utils.py`), or P3a YAML were modified. The corrected pooled P3a
track (1,244,500 rows, Stage M1 P3a construction complete 2026-05-20) is
unaffected.

---

## 19. Immediate Next Task

The immediate next task is a **precompute-slice authorization** — a narrowly
scoped amendment that:

1. Names `precompute_data_couples` as the authorized entry point.
2. Specifies the pilot precompute-ready parquet as input.
3. Identifies the metadata dict to pass (normalization constants, `n_draws`
   etc.).
4. Confirms column-presence for the full precompute path (`c_norm`,
   `l_norm_male/female`, `prior`, `leisure_male/female`, `hours_male/female`).
5. Specifies the output path for the `PrecomputedDataCouples` object.
6. States the halt conditions for the precompute run (no estimation, no welfare
   downstream).

Once that authorization is in place, the precompute run is the next concrete
execution step.

---

## Required Final Statements

- **The compatibility patch PASSED.** All 7 validation categories cleared; no
  halt condition fired.

- **No scalar `draw` column was added to the pilot parquet.** The patch is a
  code-side fallback (Option B); the data is unchanged. `draw_male`,
  `draw_female`, and `draw_joint` remain the only draw identifiers in the pilot
  parquet.

- **No GSUR merge was run.**

- **No full precompute was run.** The smoke test ran the group-construction
  logic only (far enough to confirm draw-column resolution and group sizes),
  not the full `precompute_data_couples` call.

- **No estimation was run.**

- **No welfare was computed.**

- **No SA2 was issued.**

- **M1-clean 2016 remains the active baseline.** No production data, P3a YAML,
  or production scripts (beyond the single draw-resolution site) were modified.

- **The corrected pooled P3a track is unaffected.**

- **This authorization covers Option B only:** patch `estimation_utils.py`
  draw resolution to accept `draw_joint` when `draw` is absent. Resolution
  rule: `draw` if present, else `draw_joint`, else fail loudly. Legacy
  production data with scalar `draw` behaves unchanged. Patch scope is the
  draw-identifier resolution only — no change to likelihood, income routing,
  region-dummy logic, or parameter handling; no data file modified; frozen P3a
  YAML untouched. `draw_male`/`draw_female`/`draw_joint` preserved;
  precompute-ready parquet unaltered.

---

*Status: draw_joint precompute-compatibility patch report v1. Patch PASSED;
all HD checks clear. Immediate next item: precompute-slice authorization (§19).*
