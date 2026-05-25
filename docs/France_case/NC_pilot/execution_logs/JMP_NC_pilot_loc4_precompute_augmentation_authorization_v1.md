# JMP NC Pilot — loc4 Precompute-Augmentation Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: precompute-augmentation authorization, narrow.** Authorizes
only re-running `precompute_data_couples` with `include_loc_vars=True` on the
**same** `__precompute_norm_ready.parquet`, producing a new pilot pkl that
carries the `loc4_*` occupation arrays — so the free `beta_occ_*` occupation-
opportunity parameters are identified. No EUROMOD, GSUR merge, data rebuild,
estimation, welfare, SA2, or promotion. M1-clean 2016 active; corrected pooled
P3a track unaffected.

---

## 1. Purpose

To correct the precomputed object so the first diagnostic estimation can run
cleanly. The current pilot pkl was built with `include_loc_vars=False`, so
`loc4_male`, `loc4_female`, and the `loc4_*` dummies are absent and the free
`beta_occ_*` parameters are inert. This slice re-runs the couples precompute
with `include_loc_vars=True` (and `include_wage_vars=True`) on the existing
normalized parquet, writing a new `_loc.pkl`, so `beta_occ` is identified. It
changes only the precompute call flags — no logic, no data, no normalization.

This corrects an error in the prior precompute/diagnostic authorizations, which
set `include_loc_vars=False` while keeping `beta_occ` free — incompatible,
because `beta_occ_*` multiplies `loc4_* × working` and cannot be identified
without the `loc4_*` arrays. The W1 `delta_occ` wage premium (calibrated, in the
draw) is unaffected and remains fixed; only `beta_occ` (occupation availability
mass, free) needed the arrays.

---

## 2. Current diagnostic-estimation halt status

The first diagnostic estimation was stopped before any result was accepted:

- The scipy / L-BFGS-B run consumed ~17,312 CPU s (~4.8 h) without healthy
  convergence; `max_iterations: 3000` did not stop it in time.
- Root cause: the precomputed pkl has **no** `loc4_*` arrays (confirmed by
  field listing), so the 6 `beta_occ_*` parameters have **zero gradient and
  zero contribution** — a degenerate 6-D flat manifold the solver could not
  leave. ~60 s per LL/gradient evaluation over 2,319,300 rows compounded the
  runaway.
- The hung processes were killed. **No result accepted; no output promoted; no
  welfare, SA2, or estimation result recorded.** Source parquet and prior pkl
  unchanged.

---

## 3. Why the current precomputed object is incomplete

`precompute_data_couples` builds the occupation arrays only inside
`if include_loc_vars:` and then `if "loc4_male" in df.columns` /
`if "loc4_female" in df.columns` (estimation_utils.py lines 1076–1089). The
pilot pkl was produced with the default `include_loc_vars=False`, so none of
`loc4_male`, `loc4_female`, `loc4_1_male..loc4_4_male`,
`loc4_1_female..loc4_4_female` were ever constructed. The opportunity index's
occupation term (`beta_occ_k × loc4_k × working`) therefore multiplies absent
arrays → zero contribution, zero gradient. The fix is to rebuild the pkl with
`include_loc_vars=True` so these arrays exist and `beta_occ` is identified.

---

## 4. Why this is not a GSUR problem

GSUR is present and correct. `gsur_male` and `gsur_female` are in the
precomputed object (2,319,300 rows each, no missing values, non-degenerate
variation) and were consumed by the direct path (no zeros fallback). They were
carried from the upstream GSUR merge done before the C′ EUROMOD runs, and —
because GSUR is keyed on fixed (sex × group) attributes that do not vary across
a couple's 900 draws under `occ_spec=fixed` — replicating them across the
product is correct. The hang had nothing to do with GSUR; the GSUR arrays are
preserved unchanged by this augmentation and re-validated in §11.

---

## 5. Why this is not a region problem

Region is present and correct. `reg2..reg8` (Île-de-France = reference) and
`drgn1` are in the precomputed object and enter `log_market` as standalone
region shifters (`× working`), additively — not interacted with occupation. They
were consumed directly (no zeros fallback). The hang was not a region issue; the
region arrays are preserved unchanged by this augmentation and re-validated in
§11. (A region × occupation interaction is not in the current spec and is not
part of this slice.)

---

## 6. Why runtime loc4 injection is not accepted

A runtime workaround that reads `loc4_*` from the parquet and attaches the
arrays to the in-memory `PrecomputedDataCouples` object would make a single
estimation run work, but it is **not** the clean authorized path:

- The persisted pkl would remain incomplete, so every downstream consumer
  (re-runs, the eventual verdict-grade run, robustness checks) would need the
  same ad-hoc injection — fragile and unauditable.
- The provenance of the occupation arrays would live in estimation-script
  glue, not in the precompute artifact, breaking the slice discipline that has
  governed every prior step.

The correct fix is to rebuild the pkl itself so the occupation arrays are a
first-class, validated part of the artifact. Runtime injection is therefore
**not accepted** as a substitute (HL-INJECT).

---

## 7. Authorized augmentation

Re-run `precompute_data_couples` on `__precompute_norm_ready.parquet` with:

- `include_loc_vars=True` (the change),
- `include_wage_vars=True` (unchanged — W1 wage layer),
- the **same** normalization metadata (`c_scale = c_scale_pilot = 4,054.2856`,
  leisure scales 10.0) — no re-normalization,
- the patched `_resolve_draw_column` (resolves `draw_joint`).

`precompute_data_couples` logic is **not** edited (HL-LOGIC); only the call flag
changes. Output a **new** pkl; the prior pkl is **not** overwritten.

**Precondition (halt gate, HL-COL):** the occupation arrays are built only if
`loc4_male`/`loc4_female` exist in the parquet. The augmentation must confirm
both columns are present (values in the documented pilot coding; observed expected
codes are {-2, -1, 1, 2, 3, 4} — codes 1..4 define occupation dummies, while -1/-2
must be reported and not silently recoded) **before**
relying on the rebuild. If absent, halt — do not synthesise; the fallback
(source/merge `loc4_*`, or drop `beta_occ` from the diagnostic spec) is a
separate decision.

---

## 8. Input normalized pilot parquet

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet`
— 2,319,300 rows (2,577 × 900), with W1 wages, EPS-floored `c_norm`,
GSUR/region columns, the `c_pilot_raw_nonpositive` HN-POS flag, chosen-first
ordering, and (precondition) `loc4_male`/`loc4_female`. **Read-only; not
overwritten** (HL-MUT). It is reused as-is — no re-normalization, no re-merge.

---

## 9. Required precompute flags

```
precompute_data_couples(df, metadata,
                        include_wage_vars=True,
                        include_loc_vars=True)
```

with `metadata` carrying the existing pilot normalization (`c_scale =
4,054.2856`, `l_scale = l_male_scale = l_female_scale = 10.0`). No other flag
or metadata change.

---

## 10. Required output artifact

`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`
(+ a run-summary sidecar). A **new** file. The prior pkl
`fr_pilot_nc_2016_couples_precomputed.pkl` is **not mutated** (HL-MUT).

---

## 11. Required validation checks

- **Precondition:** `loc4_male`/`loc4_female` present in the parquet, expected
  coding (else HL-COL halt).
- **Occupation arrays present:** the new pkl contains `loc4_male`,
  `loc4_female`, `loc4_2_male`, `loc4_3_male`, `loc4_4_male`, `loc4_2_female`,
  `loc4_3_female`, `loc4_4_female` (and `loc4_1_*` reference dummies).
- **Non-degenerate:** each `loc4_*` dummy has both 0s and 1s (not all-zero —
  the defect that killed the gradient) (else HL-DEGEN).
- **Product-consistency (off-axis constancy):** occupation is part of the drawn
  job, so `loc4_male` may vary across `draw_male` but must be **constant within
  each `(idhh, year_tag, draw_male)` across all `draw_female`**; symmetrically
  `loc4_female` may vary across `draw_female` but must be **constant within each
  `(idhh, year_tag, draw_female)` across all `draw_male`** (else HL-VARY).
- **Code accounting:** report `loc4` code counts including `-1` and `-2`; build
  `loc4_1..loc4_4` dummies only for codes 1..4; `-1`/`-2` are not recoded.
- **GSUR preserved:** `gsur_male`/`gsur_female` present, non-missing,
  non-degenerate, identical to the prior pkl.
- **Region preserved:** `reg2..reg8` present, identical to the prior pkl.
- **Structure:** groups = 2,577; alternatives per group = 900; chosen
  alternative at position 0.
- **Consumption:** `c_norm` positive and finite on all rows.
- **HN-POS flag preserved:** the `c_pilot_raw_nonpositive` flag (123 EPS-floored
  rows) carried through unchanged; the corresponding `c_norm = EPS` rows intact.
- **Everything else unchanged:** `log_c`/`log_l_*`/`log_wage_*`/`prior` finite;
  `c_scale`/`l_scale` identical to the prior pkl.
- **No mutation:** source parquet unchanged (2,319,300 rows); prior pkl
  unchanged; no production file or P3a YAML touched.

---

## 12. Halt conditions

| Halt | Condition |
|---|---|
| **HL-COL** | `loc4_male`/`loc4_female` absent from the parquet (or wrong coding). Halt; do NOT synthesise. |
| **HL-DEGEN** | After rebuild, any `loc4_*` dummy all-zero / degenerate (`beta_occ` would still be inert). |
| **HL-VARY** | Off-axis constancy violated: `loc4_male` not constant within `(idhh, year_tag, draw_male)` across `draw_female` (or the symmetric `loc4_female` condition). Occupation IS drawn per partner-axis, so it varies across a partner's own marginal draws — that is correct, not a halt. |
| **HL-INJECT** | Occupation arrays injected at runtime into the in-memory object instead of rebuilt into the pkl. |
| **HL-LOGIC** | Any edit to `precompute_data_couples` / `_resolve_draw_column`. |
| **HL-NORM** | Any re-normalization (`c_scale`/`l_scale` change) — must reuse the pilot normalization. |
| **HL-MUT** | Source parquet, prior pkl, any production file, or the frozen P3a YAML modified/overwritten. |
| **HL-STAGE** | Any attempt to run estimation, EUROMOD, GSUR merge, data rebuild, welfare, SA2, promotion, or M1-clean displacement in this slice. |

Any fired halt → stop, write the report up to the halt, await direction. Do not
work around (especially: do not synthesise `loc4_*`, do not inject at runtime as
a substitute for the pkl rebuild).

---

## 13. What is authorized

- The §7 precondition check.
- Re-running `precompute_data_couples` with `include_wage_vars=True,
  include_loc_vars=True` on the existing normalized parquet, reusing the pilot
  normalization metadata.
- Writing the new `_loc.pkl` + run-summary sidecar.
- The §11 validations and the report (§15).

---

## 14. What is not authorized

- Editing `precompute_data_couples` / `_resolve_draw_column` (HL-LOGIC).
- Re-normalizing (HL-NORM).
- Synthesising `loc4_*` or runtime-injecting them as a pkl substitute
  (HL-COL / HL-INJECT).
- Overwriting the source parquet or the prior pkl (HL-MUT).
- Running estimation, EUROMOD, GSUR merge, data rebuild, welfare, SA2,
  promotion; M1-clean displacement (HL-STAGE).

---

## 15. Required augmentation report

`Results/JMP_NC_pilot_loc4_precompute_augmentation_report_v1.md`, covering: scope
and corrected-error provenance (`include_loc_vars` False→True; `delta_occ`
calibrated vs `beta_occ` free distinction); the halt recap (4.8 h, dead
`beta_occ_*`); the §7 precondition result (`loc4_male`/`loc4_female` present +
coding); the rebuild (flags, same normalization, new `_loc.pkl` path); the §11
validations (the 8 named occupation arrays present + non-degenerate +
off-axis product-consistency; GSUR preserved; region preserved; 2,577 × 900; chosen at
position 0; `c_norm` positive/finite; HN-POS flag preserved; everything else
identical; no mutation); halt-condition status; and required final statements
(no estimation/EUROMOD/GSUR/rebuild/welfare/SA2/promotion; `delta_occ` still
calibrated; M1-clean active; P3a unaffected; augmentation slice only).

---

## 16. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Precondition-gated; rebuild pkl only; stop
before estimation.

```text
Work locally in my RURO/MNL codebase. LOC4 PRECOMPUTE AUGMENTATION, FR_2016
couples pilot. Authorized by
docs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md. Rebuild the
precomputed pkl with include_loc_vars=True so beta_occ_* are identified.

HARD CONSTRAINTS (halt and report if any would be violated):
- Do NOT edit precompute_data_couples / _resolve_draw_column logic. (HL-LOGIC)
- Do NOT re-normalize: reuse c_scale = 4054.2856, l_scale = 10.0 from normmeta. (HL-NORM)
- Do NOT synthesise loc4_*; if loc4_male/loc4_female absent from the parquet -> HALT. (HL-COL)
- Do NOT inject loc4_* at runtime as a substitute for the pkl rebuild. (HL-INJECT)
- Do NOT overwrite the source parquet or the prior pkl; write a NEW pkl. (HL-MUT)
- Do NOT run estimation/EUROMOD/GSUR/rebuild/welfare/SA2/promotion. (HL-STAGE)

Read (read-only except the new pkl write):
- docs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md
- scripts/enhanced/estimation_utils.py (precompute_data_couples; loc4 build @ 1076-1089)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json

STEP 1 — PRECONDITION (HL-COL):
- Confirm loc4_male AND loc4_female exist; observed codes {-2,-1,1,2,3,4}. Codes
  1..4 define dummies; -1/-2 reported, NOT silently recoded.
- If absent/wrong coding -> HALT, write report, do NOT synthesise.

STEP 2 — Rebuild pkl:
- precompute_data_couples(df, metadata, include_wage_vars=True,
  include_loc_vars=True) on __precompute_norm_ready.parquet with the SAME
  normalization metadata (c_scale=4054.2856, l_scale=10.0).
- Write NEW pkl: Data/pilot/nc_2016_couples/precomputed/
  fr_pilot_nc_2016_couples_precomputed_loc.pkl  (+ run-summary sidecar).

STEP 3 — Validate (authorization s.11):
- new pkl contains loc4_male, loc4_female, loc4_2_male, loc4_3_male, loc4_4_male,
  loc4_2_female, loc4_3_female, loc4_4_female (+ loc4_1_* reference);
- each loc4_* dummy NON-DEGENERATE (0s and 1s; not all-zero) -> else HL-DEGEN;
- PRODUCT-CONSISTENCY (off-axis), NOT constancy across all 900:
  loc4_male constant within (idhh, year_tag, draw_male) across draw_female;
  loc4_female constant within (idhh, year_tag, draw_female) across draw_male
  (loc4 IS drawn per partner-axis, so it varies across that partner's own
  marginal draws -- that is correct) -> else HL-VARY;
- report loc4 code counts incl -1 and -2; build loc4_1..loc4_4 only for codes 1..4;
- gsur_male/gsur_female present, non-missing, non-degenerate, identical to prior pkl;
- reg2..reg8 present, identical to prior pkl;
- 2,577 groups x 900; chosen at position 0; c_norm positive and finite;
- c_pilot_raw_nonpositive HN-POS flag (123 rows) preserved; c_norm=EPS rows intact;
- log_c/log_l_*/log_wage_*/prior finite; c_scale/l_scale identical to prior pkl;
- source parquet unchanged (2,319,300 rows); prior pkl unchanged; no production
  file touched.

THEN STOP. Do not run estimation.

Halt conditions: HL-COL, HL-DEGEN, HL-VARY, HL-INJECT, HL-LOGIC, HL-NORM,
HL-MUT, HL-STAGE (authorization s.12). On any fire: STOP, write report to that
point, await direction.

Write ONE report: Results/JMP_NC_pilot_loc4_precompute_augmentation_report_v1.md
per authorization s.15. End with required final statements (no estimation/EUROMOD/
GSUR/rebuild/welfare/SA2/promotion; delta_occ still calibrated; M1-clean active;
P3a unaffected; augmentation slice only).
```

Save the report as:
`Results/JMP_NC_pilot_loc4_precompute_augmentation_report_v1.md`

---

## Required final statements

- **This authorizes only a pilot precompute augmentation** — re-running the
  couples precompute with `include_wage_vars=True, include_loc_vars=True` on the
  existing `__precompute_norm_ready.parquet`, producing a new `_loc.pkl` so the
  free `beta_occ_*` parameters are identified.
- **It corrects an authorization error** (`include_loc_vars=False` while
  `beta_occ` free). `delta_occ` (wage premium) remains calibrated in the draw;
  `beta_occ` (occupation availability mass) is the free parameter that needed
  `loc4_*`.
- **Not a GSUR problem** (§4) and **not a region problem** (§5): both are present,
  correct, and preserved unchanged.
- **Runtime loc4 injection is not accepted** (§6); the pkl itself is rebuilt.
- **Precondition halt (HL-COL):** if `loc4_male`/`loc4_female` are absent, halt —
  no synthesis.
- **No re-normalization, no logic edit, no source-parquet or prior-pkl
  overwrite. No estimation, EUROMOD, GSUR merge, rebuild, welfare, SA2, or
  promotion.** M1-clean 2016 active; corrected pooled P3a track unaffected.

---

*Status: loc4 precompute-augmentation authorization v1 (16-heading spec).
Authorizes the `include_loc_vars=True` pkl rebuild under the §12 halts; executes
nothing itself. Next: the augmentation report (§15), then the diagnostic
estimation re-run (GAMSPy/CONOPT, capped iterations) on `_loc.pkl`.*
