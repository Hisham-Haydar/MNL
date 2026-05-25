# JMP NC Pilot — Precompute-Slice Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Verdict

**HALTED. Halt condition HP-NORM fired at STEP 1b (Normalization Gate).**

The precompute slice did not run. No `PrecomputedDataCouples` artifact was
created. The inspection gate confirmed all hard-required columns are present in
the pilot parquet, but the normalization consistency check failed: the production
`c_scale` (7,597.0813 EUR/month) does not reproduce the `c_norm` values already
in the parquet to within tolerance.

STEP 2, STEP 3, and STEP 4 were not executed. Wall time and peak memory are
N/A (precompute never ran). The pooled-cycle projection is pending.

---

## 2. Authorization Scope

**Authorizing document:**
`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md`

**Authorized:** Column-inspection gate; running `precompute_data_couples` as-is
with `include_wage_vars=True, include_loc_vars=False`; persisting the
`PrecomputedDataCouples` artifact to the pilot path; validation checks; this
report.

**Not authorized and not performed:** Any edit to `precompute_data_couples` or
`_resolve_draw_column` logic (HP-LOGIC); any synthetic column (HP-SYNTH); adding
a scalar `draw` (HP-DRAW); modifying the pilot parquet, any production parquet,
or the frozen P3a YAML (HP-MUT); GSUR, estimation (including diagnostic),
welfare, SA2, promotion, M1-clean displacement (HP-STAGE); guessing or inventing
normalization constants (HP-NORM).

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md` | Authorizing document; read first |
| `Results/NC_pilot/JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md` | Prior patch report confirming compatibility patch PASSED |
| `scripts/enhanced/estimation_utils.py` | Read `precompute_data_couples` (line 944) and `_resolve_draw_column` (line ~59) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` | Schema + bounded read (read-only); 2,319,300 × 152 |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json` | Sidecar metadata; confirmed no normalization block |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Production couples normalization constants (c_scale, l_scale) |

---

## 4. Files Created

| File | Description |
|---|---|
| `scripts/pilot/_precompute_gate.py` | Inspection + normalization gate script; halted at HP-NORM |
| `Results/NC_pilot/JMP_NC_pilot_precompute_report_v1.md` | This report |

---

## 5. Files Modified

**None.** No file was modified. The pilot parquet, production parquets, P3a
YAML, `precompute_data_couples`, and `_resolve_draw_column` are all unchanged.

---

## 6. STEP 1 — Inspection Gate

### 6a. Parquet Dimensions

```
Pilot parquet: 2,319,300 rows × 152 columns
```

Dimensions match the precompute-readiness report (PASS).

### 6b. Hard-Required Column Check

Per authorization §7, the hard-required columns are those accessed via bare
`df["..."]` in `precompute_data_couples` — no `.get()` / `in df.columns` guard:

| Column | Present? | Result |
|---|---|---|
| `idhh` | Yes | PASS |
| `year_tag` | Yes | PASS |
| `draw_joint` | Yes (no scalar `draw`) | PASS |
| `is_chosen` | Yes | PASS |
| `c_norm` | Yes | PASS |
| `l_norm_male` | Yes | PASS |
| `l_norm_female` | Yes | PASS |
| `hours_male` | Yes | PASS |
| `hours_female` | Yes | PASS |
| `prior` | Yes | PASS |

**Hard-required column check: PASS.** All 10 columns confirmed present.

### 6c. Wage Column Check (include_wage_vars=True)

The W1 wage columns are guarded (`in df.columns`) but their presence determines
whether the wage layer is populated or zeroed:

| Column | Present? |
|---|---|
| `wage_male` | Yes |
| `wage_female` | Yes |
| `pexp_years_male` | Yes |
| `pexp_years_female` | Yes |

**Wage-layer check: PASS.** All four present → wage layer would be populated
(not zeroed) when precompute runs.

### 6d. Guarded Fallback Inventory

Guarded columns that are present (no fallback would fire):

| Column | Present? | Fallback if absent |
|---|---|---|
| `gsur_male` | Yes | zeros + warning |
| `gsur_female` | Yes | zeros + warning |
| `reg_nuts1_2` through `reg_nuts1_8` | Yes (all 7) | region fallback / zeros |
| `drgn1` | Yes | region fallback |

Guarded columns that are absent (would fire fallback when precompute eventually
runs):

| Column | Absent? | Fallback |
|---|---|---|
| `u_rate_male` | Absent | GSUR path preferred; `gsur_male` present so no fallback needed |
| `u_rate_female` | Absent | Same as above |
| `drgn` | Absent | `drgn1` present — direct path used |

**Guarded-fallback assessment:** No opportunity-index fallbacks will fire. GSUR
columns (`gsur_male`, `gsur_female`) are present so the GSUR opportunity shifter
is populated directly; no zeros substitution. Region dummies (`reg_nuts1_2..8`)
are present; `drgn1` is present (direct region path). The absence of `u_rate_*`
and `drgn` is immaterial because the preferred guarded columns are present.

---

## 7. STEP 1b — Normalization Gate (HP-NORM)

### 7a. Normalization Column Values (from parquet)

```
c_norm:       mean = 0.98639   min = 0.04209   max = (not captured; bounded read)
l_norm_male:  mean = 4.59927   min = 1.00000
l_norm_female: mean = 4.61699  min = 1.00000
```

The `c_norm` values are dimensionless (mean ≈ 0.99, range well below 10),
consistent with unit-normalized household consumption.

### 7b. Normalization Metadata Source Search

The readymeta sidecar
(`fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json`) carries
no `normalization` block. Per authorization §6 and §10, the normalization
constants must be sourced from elsewhere.

The production couples normalization was found at:

```
Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json
  c_scale = 7597.0813  (EUR/month)
  l_scale = 10.0
```

### 7c. Normalization Consistency Check

The consistency check requires:

```
max |c_norm × c_scale − consumption| ≤ 1.0  (EUR/month, per authorization §10)
```

**Result:**

```
max |c_norm × c_scale − consumption| = 25,355  EUR/month
```

**HP-NORM FIRED.** The check fails by four orders of magnitude relative to the
1.0 EUR/month tolerance. The precompute cannot proceed.

---

## 8. Root Cause of HP-NORM

### 8a. How the Pilot Parquet Was Built

The pilot precompute-ready parquet was assembled in Stages 1–5:

1. **Stage 1–4 (Strategy C′ cross-join):** A 30×30 product draw was formed by
   cross-joining the production diagonal parquet with 30 female draws. The
   production diagonal parquet already carried `c_norm` (built from old
   production EUROMOD disposable income at the production `c_scale` of
   7,597 EUR/month).
2. **Stage 5 (post-EUROMOD merge):** The 30 EUROMOD runs produced
   `ils_dispy_male` and `ils_dispy_female` for all 900 cells per couple. These
   new partner-specific income values were merged onto the cross-join product.
   `c_norm` was **not** updated at this stage — it was inherited as-is from the
   Stage 3/4 product.

### 8b. Why the Consistency Check Fails

The `c_norm` column in the pilot parquet was constructed from **old production
EUROMOD income** (single-draw diagonal) divided by `c_scale_production =
7,597 EUR/month`. The `consumption` column (also carried from production) was
likewise built from old income values and replicated 900× per couple during the
cross-join.

After Strategy C′, the **true pilot income** is
`ils_dispy_male + ils_dispy_female` (the new EUROMOD output for each of the 900
cells per couple). This new income surface has not been normalized into `c_norm`.
Consequently:

- `c_norm × c_scale_production` reconstructs old single-draw consumption
  (varies per couple but constant across draws, replicated from diagonal).
- The `consumption` column in the parquet reflects old production values too,
  but the relationship `c_norm × 7597 = consumption` holds only to the extent
  that both were carried from the same old production run — they may diverge due
  to index mismatches or rounding during the cross-join.
- Neither value reflects the new pilot income surface.

The 25,355 EUR/month discrepancy is therefore not a rounding error or a
wrong-constant error — it is structural: the `c_norm` column is stale relative
to the pilot's new EUROMOD income outputs.

### 8c. What Is Required to Resolve HP-NORM

A new authorization slice must cover:

1. **Rebuild `c_norm`** from the pilot income:
   `c_norm_new = (ils_dispy_male + ils_dispy_female) / c_scale_pilot`
   where `c_scale_pilot` is derived from the new pilot income distribution
   (e.g., the mean or a quantile of `ils_dispy_male + ils_dispy_female` across
   all draws, consistent with the normalization convention used for production).
2. **Establish `c_scale_pilot`** consistently and document it in the pilot
   readymeta sidecar or a pilot-specific normalization artifact.
3. **Rebuild `l_norm_male` / `l_norm_female`** if the leisure normalization
   scale also needs to be re-derived from the pilot data (the current `l_norm_*`
   values have `min = 1.0`, which may be consistent with the production `l_scale
   = 10.0` — but this must be confirmed rather than assumed).
4. **Update the pilot parquet** with the new `c_norm` (and `l_norm_*` if
   needed), incrementing the readymeta.
5. **Write a normalization-rebuild authorization** covering the income-to-c_norm
   construction step with halt conditions for any synthetic column, production
   file modification, or out-of-tolerance result.

Until this rebuild is authorized and executed, the precompute cannot run without
violating HP-NORM.

---

## 9. Halt Condition Status

| Halt | Condition | Status |
|---|---|---|
| **HP-LOGIC** | Edit to `precompute_data_couples` or `_resolve_draw_column` | NOT FIRED — no logic changed |
| **HP-COL** | Hard-required column or normalization metadata missing | NOT FIRED — all hard-required columns present |
| **HP-SYNTH** | Synthetic column created | NOT FIRED — no column synthesised |
| **HP-NORM** | Normalization scales inconsistent with `c_norm`/`l_norm_*` | **FIRED** — `max |c_norm × c_scale − consumption| = 25,355 > 1.0` |
| **HP-DRAW** | Scalar `draw` written to data | NOT FIRED — no data modification |
| **HP-MUT** | Pilot parquet, production parquet, or frozen P3a YAML modified | NOT FIRED — no file modified |
| **HP-STAGE** | GSUR, estimation, welfare, SA2, promotion, or M1-clean displacement | NOT FIRED — none attempted |

**Halt condition fired: HP-NORM only.**

---

## 10. Precompute Run

**Not executed.** HP-NORM halted the script before STEP 2.

---

## 11. Artifact

**Not created.** The `PrecomputedDataCouples` artifact at
`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl`
does not exist. No write was attempted.

---

## 12. Wall Time and Peak Memory

**Not measured.** The precompute did not run. Pooled-cycle projection is pending
the precompute run.

For reference: the pilot has 2,577 couples × 900 alternatives = 2,319,300 rows.
The full pooled couples dataset has 7,438 couples (production P3a). The
pooled-cycle scaling factor is 7,438 / 2,577 = 2.885×.

---

## 13. Validation Results

| Check | Status |
|---|---|
| Hard-required columns present | PASS |
| Wage columns present | PASS |
| Guarded fallbacks — GSUR zeros | Would NOT fire (gsur_male/female present) |
| Guarded fallbacks — region zeros | Would NOT fire (reg_nuts1_2..8 + drgn1 present) |
| Normalization consistency | **FAIL — HP-NORM fired** (max diff 25,355 EUR/month) |
| Precompute run (shape, groups) | NOT EXECUTED |
| Draw resolution (draw_joint) | NOT EXECUTED |
| Finiteness (log_c, log_l, prior) | NOT EXECUTED |
| Wage layer populated | NOT EXECUTED |
| No mutation — pilot parquet | PASS (unmodified) |
| No mutation — production | PASS (unmodified) |
| `precompute_data_couples` body unchanged | PASS (no edit to function) |

---

## 14. Immediate Next Step

A **normalization-rebuild authorization** covering:

1. Derivation of `c_scale_pilot` from the pilot income surface
   (`ils_dispy_male + ils_dispy_female`) using the same normalization convention
   as production.
2. In-place update of `c_norm` in the pilot parquet:
   `c_norm_new = (ils_dispy_male + ils_dispy_female) / c_scale_pilot`.
3. Verification that the rebuilt `c_norm` satisfies
   `max |c_norm × c_scale_pilot − (ils_dispy_male + ils_dispy_female)| ≤ 1.0`.
4. Confirmation that `l_norm_male` / `l_norm_female` are consistent with the
   existing `l_scale = 10.0` (check `l_norm_male ≈ leisure_male / 10.0`).
5. Update of the readymeta sidecar with a `normalization` block carrying
   `c_scale_pilot` and `l_scale`.
6. Halt conditions: no synthetic column; no modification to production files;
   no modification to anything other than `c_norm` in the pilot parquet and the
   readymeta sidecar; no re-run of estimation or welfare.

Once the rebuilt `c_norm` passes the consistency check, the precompute-slice
authorization (§14 HP-NORM cleared) permits re-entry at STEP 2.

---

## Required Final Statements

- **This authorization covered only the pilot couples precompute slice.**
  `precompute_data_couples` was called as-is (no logic change). The slice
  halted at HP-NORM before the function was invoked.

- **No logic change was made.** `precompute_data_couples` and
  `_resolve_draw_column` are byte-for-byte identical to their state after the
  draw-joint compatibility patch.

- **No synthetic columns were created.** The HP-SYNTH constraint was not
  triggered; no column was added to any dataframe.

- **No scalar `draw` was added to the data.** HP-DRAW is clear.

- **No GSUR merge was run.**

- **No estimation was run** (not even diagnostic). HP-STAGE is clear.

- **No welfare was computed.**

- **No SA2 was issued.**

- **No promotion was performed.**

- **M1-clean 2016 remains the active production baseline.** No production data,
  P3a YAML, or production scripts were modified.

- **The corrected pooled P3a track is unaffected.** 1,244,500 rows (Stage M1
  P3a construction complete 2026-05-20) unchanged.

- **The pilot precompute-ready parquet is unmodified.** 2,319,300 rows × 152
  columns; `draw_joint`, `is_chosen`, `c_norm`, `l_norm_male`, `l_norm_female`,
  `hours_male`, `hours_female`, `prior` all present and unchanged.

- **HP-NORM fired.** The `c_norm` column in the pilot parquet was inherited from
  the production diagonal (old EUROMOD income). After Strategy C′, the true
  pilot income is `ils_dispy_male + ils_dispy_female`. The `c_norm` has not been
  rebuilt from this new income surface. The normalization consistency check
  `max |c_norm × c_scale_production − consumption| = 25,355 EUR/month` exceeds
  the 1.0 EUR/month tolerance by four orders of magnitude. No normalization
  constant was guessed or invented. The precompute cannot run until `c_norm` is
  rebuilt from the new pilot income and the normalization scale is established
  consistently.

---

*Status: precompute-slice report v1. HP-NORM fired; precompute not executed;
no artifact created. Immediate next item: normalization-rebuild authorization
(§14 above).*
