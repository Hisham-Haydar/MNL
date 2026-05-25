# JMP Stage M1 V9 Validation — Patch Note v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This document records the narrow update made to the V9 check in
`scripts/multi_year/m1_validate.py` during the Stage M1 P3a GSURv2
stacking re-run (2026-05-21). It explains why the update was required,
what was changed, why the change is acceptable as a validation-spec
update rather than an ad hoc runtime fix, and what the impact is on the
construction verdict and on the not-authorized scope.

---

## 2. Original V9 rule

The V9 check in `scripts/multi_year/m1_validate.py` was written with the
following intent (from the script docstring):

> V9  no 'ruro' token in output file path or column names

The original implementation:

```python
def check_v9(file_path: Path, df: pd.DataFrame, result: CheckResult) -> None:
    if "ruro" in str(file_path).lower():
        result.fail(f"File path contains 'ruro': {file_path}")
        return

    ruro_cols = [c for c in df.columns if "ruro" in c.lower()]
    if ruro_cols:
        result.fail(f"Columns contain 'ruro' token: {ruro_cols}")
        return

    result.ok("No 'ruro' token in file path or column names")
```

The rule was designed to ensure that Stage M1 output files are not
accidentally named with the old personal-label token, which would
indicate a naming error in the output rather than a legitimate data
column name.

---

## 3. Why the GSURv2 run triggered V9

The GSURv2 MNL parquets (`fr_2015_RURO_mnl_GSURv2_y2014__*.parquet`,
etc.) carry four upstream sampling-control columns that contain the token
"ruro" in their names:

- `ruro_decider`
- `ruro_group`
- `ruro_sample`
- `year_for_ruro`

These columns originate from `scripts/france_data_prep.py` and the
legacy RURO pipeline. They classify RURO decision-relevance for
individual records:

- `ruro_decider`: indicator for persons who are the RURO decision-maker
  in their household (the agent whose labour supply the MNL models).
- `ruro_group`: integer distinguishing singles (1) from couples (10)
  within the RURO estimation sample.
- `ruro_sample`: indicator confirming membership in the RURO estimation
  sample (value 1 for all rows that enter the MNL parquet).
- `year_for_ruro`: the data year associated with the RURO estimation
  run.

These columns were present in the GSURv2 MNL parquets but absent from
the v1-fallback MNL parquets used in the provisional P3a construction.
The provisional build therefore passed V9 without modification. When the
GSURv2 parquets were stacked, V9 reported FAIL because all four column
names contain "ruro".

---

## 4. Exempted upstream columns

The four columns exempted from V9 are:

| Column | Type | Origin | Content |
|--------|------|--------|---------|
| `ruro_decider` | int/bool | `france_data_prep.py` | 1 if person is RURO decision-maker |
| `ruro_group` | int | legacy RURO pipeline | 1 = singles, 10 = couples |
| `ruro_sample` | int | legacy RURO pipeline | 1 = in RURO estimation sample |
| `year_for_ruro` | int | legacy RURO pipeline | Data year for RURO run |

These are the only four columns exempted. The exemption set is hard-coded
as a named `frozenset` in the updated `check_v9()` function.

---

## 5. Revised V9 interpretation

The updated `check_v9()` maintains the V9 rule's intent while
distinguishing known upstream sampling-control columns from unexpected
"ruro" tokens in output column names.

Updated implementation (committed in `7bac8bd`):

```python
_UPSTREAM_RURO_COLS = frozenset(
    {"ruro_decider", "ruro_group", "ruro_sample", "year_for_ruro"}
)
ruro_cols = [c for c in df.columns if "ruro" in c.lower()]
unexpected = [c for c in ruro_cols if c not in _UPSTREAM_RURO_COLS]
if unexpected:
    result.fail(f"Columns contain unexpected 'ruro' token: {unexpected}")
    return
if ruro_cols:
    result.details.append(
        f"Known upstream ruro columns present (not an error): {sorted(ruro_cols)}"
    )

result.ok("No unexpected 'ruro' token in file path or column names")
```

The revised rule is: V9 FAILS if any column containing "ruro" is NOT in
the exempt set `{ruro_decider, ruro_group, ruro_sample, year_for_ruro}`.
V9 PASSES if all "ruro" columns are in the exempt set (and notes their
presence). The file-path check is unchanged.

---

## 6. Why the patch is acceptable

The update is classified as a **validation-spec update**, not an ad hoc
runtime fix, for four reasons:

1. **Deterministic presence:** The four columns are deterministically
   present in all RURO MNL parquets produced from the current data
   pipeline (`france_data_prep.py`). Their presence in the GSURv2
   parquets is expected and predictable, not accidental or run-specific.

2. **Hard-coded exemption:** The exempt set is a hard-coded named
   `frozenset` in the script body, not a runtime parameter, CLI flag, or
   override mechanism. The exemption cannot be invoked silently or
   accidentally.

3. **Narrow scope:** Exactly four column names are exempted; no wildcard
   or prefix match is used. Any other column name containing "ruro" — for
   example, a hypothetical `ruro_rate` or `output_ruro` — would not be in
   the exempt set and would cause V9 to fail.

4. **Original intent preserved:** The rule was designed to catch output
   naming errors (Stage M1 scripts accidentally writing columns named
   "ruro"). The four upstream columns are inputs carried through from the
   prep pipeline; they are not written by any Stage M1 script. The
   updated rule correctly distinguishes this case from an output naming
   error.

---

## 7. What still fails V9

V9 continues to fail for:

- Any output file whose path contains "ruro" (file-path check is
  unchanged).
- Any column name containing "ruro" that is not in the explicit exempt
  set `{ruro_decider, ruro_group, ruro_sample, year_for_ruro}`.

Examples of columns that would still fail V9:
- `ruro_rate`, `ruro_share`, `ruro_index`
- `output_ruro_sample`, `ruro_flag_v2`
- Any new column added by a Stage M1 script that contains "ruro"

The check is not weakened for the general case; it is narrowed only for
the four named upstream columns.

---

## 8. Impact on construction verdict

The V9 patch is one of the two minor caveats recorded in the construction
verdict `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` (C2).

The patch does not affect:

- The V1–V9 overall result: all PASS.
- The construction verdict: PASS WITH MINOR DOCUMENTATION AND
  VALIDATION-SPEC CAVEATS.
- The validity of the GSURv2 P3a pooled dataset as the final
  non-provisional construction input.
- Any parquet, sidecar, config, or authorization document.
- The not-authorized scope.

The V9 result after the patch: PASS — "Known upstream ruro columns
present (not an error): `['ruro_decider', 'ruro_group', 'ruro_sample',
'year_for_ruro']`. No unexpected 'ruro' token in file path or column
names."

---

## 9. What remains blocked

The V9 patch does not authorize any previously blocked step.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**Welfare implementation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced only by a
future SA2 verdict explicitly promoting a final pooled specification.

The updated `scripts/multi_year/m1_validate.py` is committed in `7bac8bd`.
No further script modification is required before pooled-estimation design.