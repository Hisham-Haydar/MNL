# JMP GSURv2 Multi-Year Extension — Remediation Authorization Final Wording Fix v1

*France 2015–2016–2017 | v1 | 2026-05-20*

---

## 1. Fix verdict

Three targeted edits applied to
`docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`.
No data were built, no scripts were run, no files were retrieved,
and no parquets were written. All edits are textual; the underlying
authorizations and naming decisions are unchanged.

| # | Location | Issue | Action |
|---|----------|-------|--------|
| F1 | §14 V4 item (c) | "calling the script with `--opportunity-year 2016 --dry-run`" — a script invocation with an opportunity year — appeared inside the static/no-write validation block | Replaced with "by source inspection or import-time path-template evaluation — do NOT invoke the script with `--opportunity-year`" |
| F2 | §14 V7 closing sentence | "The V4 value-identity check provides the empirical confirmation" — implies V4 runs an empirical check against output data | Replaced with "The V4 static parameterisation check provides no-write confirmation that the parser, path templates, and sidecar block are present; the value-identity regression is deferred to construction authorization" |
| F3 | §15 step 5 item (c) | "confirm path computation resolves the y2016 output path to…" — implicit allowance of invoking the script with `--opportunity-year` | Replaced with explicit source-inspection / import-time path-template instruction; added "do NOT invoke the script with `--opportunity-year`" and "Do NOT write any output parquet" |

---

## 2. Files inspected

| File | Purpose |
|------|---------|
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | Memo subject to fix; §§14 and 15 read in full |
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md` | Correction report from the prior pass; read to confirm the scope of the previous correction and identify the residual contradiction |

No code files were read. No data files were read. No scripts were run.

---

## 3. Residual contradiction fixed

The prior correction pass (recorded in
`docs/JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md`)
removed all explicit authorizations to run the parameterised script
with `--opportunity-year 2016`. However, two residual passages
carried forward language that implicitly invited an opportunity-year
invocation.

**In §14 V4**, item (c) read:

> "calling the script with `--opportunity-year 2016 --dry-run`
> (or equivalent import-time path-computation test) resolves the
> output path to `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`
> and the sidecar path to
> `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json`"

The phrase "calling the script with `--opportunity-year 2016
--dry-run`" is a script invocation with an opportunity year, even if
qualified by a `--dry-run` flag. A `--dry-run` flag is not
implemented in the current script (C1–C7 add `--opportunity-year`,
not `--dry-run`), so the instruction as written could not be
executed as a no-write check. More fundamentally, any invocation of
the construction script with `--opportunity-year 2016` is prohibited
by the conservative approach: the prohibition is categorical, not
conditional on a `--dry-run` flag that may or may not exist.

**In §14 V7**, the sentence:

> "The V4 value-identity check provides the empirical confirmation"

was a carry-over from the v1 memo's V4, which did run the script and
perform a value-identity comparison. After the correction pass, V4
no longer performs an empirical run; calling it a "value-identity
check" was a stale label that contradicted the static/no-write
characterisation of V4 established in the same correction pass.

**In §15 step 5**, item (c) read:

> "confirm path computation resolves the y2016 output path to
> `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`"

The phrase "path computation" without explicit qualification could be
read as allowing the operator to run `python
enh_prepare_FR_gsur_v2.py --opportunity-year 2016` and observe the
output path. The fix makes the method explicit: source inspection or
import-time path-template evaluation, not script invocation with an
opportunity year.

The root cause in all three cases is the same: the prior correction
pass replaced explicit `--opportunity-year 2016` authorizations at
the section level but did not sweep item-level phrasing within V4
and V7 that retained language from the original empirical-run
design.

---

## 4. V4 wording after fix

**§14 V4 — Static parameterisation check (no-write validation).**

> Confirm the parameterised script passes the following static
> checks without writing any output parquet and without invoking
> the script with an opportunity year: (a) the script imports
> without error; (b) `--help` runs without error and lists the
> `--opportunity-year` argument; (c) by source inspection or
> import-time path-template evaluation (not by invoking the script
> with `--opportunity-year`), confirm the output path template
> resolves to the pattern
> `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}.parquet` and the
> sidecar path template to
> `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json`;
> (d) the C7 sidecar block is present in the script and contains
> the required fields (§9). No lookup parquet is written during
> this validation. The value-identity regression check is deferred
> to the construction authorization.

Key properties of the fixed V4:

- The path-template check (c) uses the template form
  `y{YEAR}` rather than the y2016-specific instantiation, making
  clear it is a structural check of the parameterisation, not an
  execution for a specific year.
- Items (a) and (b) allow `python script.py --help` because `--help`
  is a standard argparse exit that does not invoke the construction
  logic and writes no output.
- Item (c) explicitly names the permitted method: source inspection
  (reading the script) or import-time helper (importing the module
  and calling a path-construction function directly), not CLI
  invocation with `--opportunity-year`.
- Item (d) is a code-read check only.

---

## 5. V7 wording after fix

**§14 V7 — Script-logic-preservation check.**

> Confirm that the C1–C7 changes are confined to the input-
> selection and output-tagging layers and that the year-invariant
> construction logic (the aggregation, education alignment, age-
> band selection, drgn1=9 stub handling, IDF parity check,
> benchmark validation, output schema) is unchanged. The V4 static
> parameterisation check provides no-write confirmation that the
> parser, path templates, and sidecar block are present; the
> value-identity regression is deferred to construction
> authorization. This check provides the code-inspection
> confirmation that the year-invariant logic is untouched.

The revised V7 correctly characterises V4 as a structural/static
check (parser, templates, sidecar block present) and V7 as the code-
inspection check (year-invariant logic unchanged), while placing the
empirical value-identity regression squarely in the construction
authorization where it belongs.

---

## 6. Section 15 wording after fix

**§15 step 5 (static parameterisation check):**

> 5. Run the static parameterisation check (V4 per the
>    authorization §14): (a) confirm the script imports without
>    error; (b) confirm `--help` runs without error and lists
>    `--opportunity-year`; (c) by source inspection or import-time
>    path-template evaluation — do NOT invoke the script with
>    `--opportunity-year` — confirm the output path template
>    resolves to the pattern
>    `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}.parquet` and
>    the sidecar path template to
>    `Data/external/FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json`;
>    (d) confirm the C7 sidecar block is present and contains the
>    required fields. Do NOT invoke the script with an opportunity
>    year. Do NOT write any output parquet.

The prohibition "do NOT invoke the script with `--opportunity-year`"
appears inline within item (c), immediately after the permitted
method is named, so it cannot be read past without encountering the
restriction. The closing lines reinforce it at the step level.

---

## 7. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | Text correction | §14 V4 item (c): `--opportunity-year 2016 --dry-run` invocation removed; replaced with source-inspection / import-time template instruction. §14 V7: "value-identity check" label replaced with correct static-check description. §15 step 5 item (c): same clarification as V4 with inline prohibition. |
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md` | New file | This report. |

No other files were modified. No code was changed. No data were
built.

---

## 8. Final status

After the three fixes, the remediation authorization memo is
internally consistent with the conservative y2016 provenance-lock
approach throughout. Every location that specifies how to validate
the C1–C7 parameterisation now uses the same method: source
inspection or import-time path-template evaluation only, with no
invocation of the construction script with an opportunity year and
no lookup parquet written.

The only remaining references to `--opportunity-year 2016` in the
memo appear in §9 (the lock procedure, explicitly labelled as
deferred to construction authorization), §15 "What to do next"
(describing the first step of the construction authorization memo,
explicitly labelled as the next authorization stage), and §12 N1
(the not-authorized list, which prohibits this invocation during
the remediation). All three occurrences are correctly scoped; none
is inside the remediation boundary.

The memo is ready to serve as the governing authorization for the
remediation task.