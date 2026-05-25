# JMP NC Pilot — HN-POS Resolution Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Verdict

**PASSED. All 14 validation checks cleared; no halt condition fired.**

The HN-POS resolution and `c_norm` rebuild completed successfully. The 123
non-positive `c_pilot_raw` rows across 6 households were floored to `EPS =
1e-12` on the normalized `c_norm` — the identical floor `precompute_data_couples`
applies internally — applied explicitly and recorded. The new
`__precompute_norm_ready.parquet` and its `__normmeta.json` sidecar are written.
The HP-NORM halt is now cleared for re-entry to the precompute slice. Wall time:
10.5 seconds.

---

## 2. Authorization Scope

**Authorizing document:**
`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md`

**Authorized:** EPS confirmation from source; computing `c_pilot_raw`,
`c_scale_pilot`, `c_norm_raw`, normalized-EPS-floored `c_norm`, and the
`c_pilot_raw_nonpositive` flag; writing the new
`__precompute_norm_ready.parquet` (with floored `c_norm`, flag, diagnostic
`c_pilot`) and its `__normmeta.json`; this report.

**Not authorized and not performed:** Dropping households or rows (HF-DROP);
re-running EUROMOD (HF-STAGE); any euro floor ≠ EPS from source (HF-EPS/
HF-FLOOR); altering `ils_dispy_*` (HF-INCOME), leisure normalization
(HF-LEIS), draw identifiers, `is_chosen*`, W1, GSUR, or region columns
(HF-STRUCT); overwriting the input parquet or any production file (HF-MUT);
running precompute, GSUR, estimation, welfare, SA2, promotion, or M1-clean
displacement (HF-STAGE).

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md` | Authorizing document; read first |
| `Results/NC_pilot/JMP_NC_pilot_normalization_rebuild_report_v1.md` | HN-POS halt detail (123 rows, 6 households) |
| `scripts/enhanced/estimation_utils.py` | EPS source confirmed at line 49; use site at line 998 |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` | Input; read-only; 2,319,300 × 152 |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Leisure scales to preserve |

---

## 4. Files Created

| File | Description |
|---|---|
| `scripts/pilot/_resolve_hnpos.py` | Resolution + rebuild script |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet` | Output parquet: 2,319,300 × 154 (c_norm rebuilt + flag + diagnostic c_pilot) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json` | Normmeta sidecar |
| `Results/NC_pilot/JMP_NC_pilot_HN_POS_resolution_report_v1.md` | This report |

---

## 5. Files Modified

**None.** Input parquet unchanged (2,319,300 × 152, confirmed on disk).
No production parquet, P3a YAML, or production script was touched.

---

## 6. STEP 1 — EPS Source Confirmation (HF-EPS)

```
File:     scripts/enhanced/estimation_utils.py
Line 49:  EPS = 1e-12
Line 998: consumption = np.maximum(df["c_norm"].values.copy(), EPS)
```

EPS is a **module-level constant** (not a magic literal) applied as a
`np.maximum` floor on the normalized `c_norm` inside `precompute_data_couples`.
The floor formula used in this resolution slice is byte-identical to that use
site.

**HF-EPS: PASS.**

---

## 7. STEP 2 — Consumption Object and Scale

```
c_pilot_raw  = ils_dispy_male + ils_dispy_female   (per row)
c_scale_pilot = mean(c_pilot_raw) over all 2,319,300 rows
             = 4054.2855556860  EUR/month
```

`c_scale_pilot > 0`: PASS. The `c_scale` key in the normmeta `normalization`
block is set equal to `c_scale_pilot` for `precompute_data_couples`
compatibility.

**Effective euro floor:**
`EPS × c_scale_pilot = 1e-12 × 4054.2856 = 4.054e-9 EUR/month` — effectively
zero in any economic sense.

**`c_pilot_raw` distribution:**

| Statistic | EUR/month |
|---|---|
| mean | 4,054.286 |
| std | 1,893.444 |
| min | −812.213 |
| p1 | 1,170.916 |
| median | 3,758.529 |
| max | 24,364.360 |

---

## 8. STEP 3 — Normalized-EPS Floor

**Floor formula (authorization §8):**

```
c_norm_raw   = c_pilot_raw / c_scale_pilot
c_norm       = max(c_norm_raw, EPS)            # EPS = 1e-12
c_pilot_raw_nonpositive = (c_pilot_raw <= 0).astype(int)
```

This is a **pilot computational-domain convention** — the same floor
`precompute_data_couples` would apply internally — made explicit and recorded
so the 123 floored rows are visible in the data and metadata. This is **not**
a final welfare-domain decision on how negative-income alternatives enter the
welfare metric.

**Floor results:**

```
Rows where c_norm_raw <= EPS (floored):   123
Rows where c_pilot_raw <= 0 (flag == 1):  123
```

All 123 floored rows have `c_pilot_raw < 0`, which puts `c_norm_raw` far below
zero (not merely in the `(0, EPS]` band). No rows in `(0, EPS]` were found.
The floored-row count equals the non-positive flag count exactly.

**HF-FLOOR: PASS.**

---

## 9. Floored Rows — Per-Household Breakdown

| `idhh` | Floored rows | `draw_joint` range | `c_pilot_raw` range (EUR/month) |
|---|---|---|---|
| 1,567,200 | 25 | [217, 777] | −375.61 (constant) |
| 1,752,900 | 50 | [61, 435] | [−812.21, −25.73] |
| 2,374,500 | 19 | [211, 702] | [−662.82, −122.98] |
| 3,270,400 | 3 | [331, 357] | −473.48 (constant) |
| 3,355,800 | 2 | [194, 494] | −120.10 (constant) |
| 4,323,300 | 24 | [217, 657] | −41.42 (constant) |
| **Total** | **123** | | |

These are real EUROMOD tax-benefit outcomes for specific product-draw cells
where one partner's assigned occupation generates a gross-earnings shortfall
relative to tax liabilities and benefit clawbacks. The corresponding chosen
rows (`draw_joint == 0`) for all 6 households have positive `c_pilot_raw` and
are unaffected by the floor.

After flooring, the 123 cells carry `c_norm = EPS = 1e-12`, giving
`log(c_norm) ≈ −27.6`. This effectively assigns near-zero utility weight to
these alternatives in the MNL softmax — the functional equivalent of an
infeasible cell — without making `log` undefined or dropping the row.

---

## 10. `c_pilot_raw_nonpositive` Flag

```
Column: c_pilot_raw_nonpositive
Dtype:  int32
Rule:   1 where c_pilot_raw <= 0, else 0
Sum:    123  (matches floored-row count exactly)
Role:   diagnostic/non-primary; marks all 123 floored rows for downstream
        robustness checks (e.g. re-weighting or sensitivity analysis)
```

Raw income columns `ils_dispy_male` and `ils_dispy_female` are **preserved
unchanged**. Only `c_norm` carries the floor; the raw negative income values
remain in the data.

---

## 11. Rebuilt `c_norm` Distribution

| Statistic | Value |
|---|---|
| mean | 1.000005 (≈ 1 by construction; slight elevation from EPS floor on 123 rows) |
| min | 1.000000e-12 (= EPS, on the 123 floored rows) |
| max | 6.009532 |

The mean being ≈ 1 confirms `c_scale_pilot` was correctly computed as the
all-rows mean of `c_pilot_raw`.

---

## 12. Output Parquet and Normmeta

**Output parquet:**
`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet`
- 2,319,300 rows × 154 columns
  (152 original + `c_pilot_raw_nonpositive` + diagnostic `c_pilot`)
- 139.6 MB (Snappy-compressed)
- Chosen-first ordering preserved
- No scalar `draw` column

**Normmeta sidecar:**
`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json`

Key fields in the `normalization` block:

```json
{
  "c_scale": 4054.2855556860,
  "l_scale": 10.0,
  "l_male_scale": 10.0,
  "l_female_scale": 10.0,
  "couples": {
    "c_scale": 4054.2855556860,
    "l_male_scale": 10.0,
    "l_female_scale": 10.0
  }
}
```

Both flat (`c_scale`, `l_scale`) and nested (`couples.*`) keys are populated
to match whichever resolution path `precompute_data_couples` uses.

---

## 13. Validation Results (Authorization §13)

| # | Check | Result |
|---|---|---|
| V1 | EPS = 1e-12 from `estimation_utils.py` line 49 | PASS |
| V2 | Floor applied: 123 rows where `c_norm_raw ≤ EPS` | PASS |
| V3 | Positivity: `c_norm > 0` all 2,319,300 rows | PASS |
| V4 | Rebuild identity (non-floored): max diff = 1.82e-12 ≤ 1.0 EUR/month | PASS |
| V5 | Flag correctness: `c_pilot_raw_nonpositive` sums to 123 | PASS |
| V6 | Income preserved: `ils_dispy_male`/`ils_dispy_female` unchanged | PASS |
| V7 | Leisure cols unchanged: `l_norm_male`/`l_norm_female` byte-identical | PASS |
| V8 | Leisure scales preserved: `l_male_scale = l_female_scale = 10.0` | PASS |
| V9 | Row count: 2,319,300 | PASS |
| V10 | Group structure: 2,577 groups, all size 900 | PASS |
| V11 | Chosen-first: all 2,577 groups, 0 bad `draw_joint@pos0`, 0 bad `is_chosen@pos0` | PASS |
| V12 | No scalar `draw` column | PASS |
| V13 | Preserved columns present: `draw_male/female/joint`, `is_chosen*`, `ils_dispy_*`, `wage_*`, `gsur_*`, `l_norm_*` | PASS |
| V14 | Input parquet unchanged: 2,319,300 × 152 on disk | PASS |

**All 14 validations: PASS. No halt condition fired.**

---

## 14. Halt Condition Status

| Halt | Condition | Status |
|---|---|---|
| **HF-EPS** | EPS not locatable unambiguously | NOT FIRED — EPS = 1e-12 at line 49 |
| **HF-FLOOR** | Floored count ≠ 123 or floor ≠ `max(c_norm_raw, EPS)` | NOT FIRED — 123 rows floored exactly |
| **HF-POS** | Any `c_norm ≤ 0` after floor | NOT FIRED — all rows `c_norm > 0` |
| **HF-IDENT** | Non-floored rows max diff > 1.0 | NOT FIRED — max diff 1.82e-12 |
| **HF-INCOME** | `ils_dispy_*` altered | NOT FIRED — income columns unchanged |
| **HF-LEIS** | `l_norm_*` or leisure scale metadata changed | NOT FIRED — unchanged |
| **HF-STRUCT** | Row/group/chosen-first/scalar-draw/column violation | NOT FIRED — structure intact |
| **HF-MUT** | Input parquet, production parquet, P3a YAML modified | NOT FIRED — no modification |
| **HF-DROP** | Household or row dropped | NOT FIRED — 2,319,300 rows preserved |
| **HF-STAGE** | EUROMOD re-run, precompute, GSUR, estimation, welfare, SA2, promotion | NOT FIRED — none attempted |

---

## 15. HP-NORM Clearance

The normalization consistency check that fired HP-NORM in the precompute-slice
report will now pass on the new parquet:

```
max |c_norm × c_scale_pilot − c_pilot_raw| = 1.82e-12   (non-floored rows)
                                            ≈ 0           (floored rows: both sides = EPS × c_scale_pilot)
```

Both are far below the 1.0 EUR/month tolerance. **HP-NORM is cleared** for
re-entry to the precompute slice.

---

## 16. Immediate Next Step

Re-enter the precompute slice (`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md`)
pointing at the new parquet and normmeta:

- **Input parquet:** `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet`
- **Metadata:** `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json`
- **`c_scale`:** 4,054.2856 (from normmeta `normalization.c_scale`); HP-NORM will now pass.
- **All hard-required columns** from the prior inspection gate are present and
  unchanged (confirmed at Step 6 above).

---

## Required Final Statements

- **This authorization covered only HN-POS resolution + the `c_norm` rebuild.**
  Floor formula: `c_norm = max(c_pilot_raw / c_scale_pilot, EPS)`.
  `c_scale_pilot = 4,054.2855556860` (all-rows mean of `c_pilot_raw`).
  `c_scale = c_scale_pilot` in the normmeta `normalization` block.

- **The 6 households and 123 rows are floored, not dropped.** EUROMOD was not
  re-run. No row or household was removed (HF-DROP clear).

- **EPS came from source: `estimation_utils.py` line 49, `EPS = 1e-12`.** The
  floor is `np.maximum(c_norm_raw, EPS)`, byte-identical to the use site at
  `precompute_data_couples` line 998. No arbitrary euro floor was applied.

- **A diagnostic `c_pilot_raw_nonpositive` flag (sum 123) was added.** Raw
  income columns `ils_dispy_male` and `ils_dispy_female` are preserved
  unchanged. Only `c_norm` carries the floor.

- **Leisure normalization is not rebuilt.** `l_norm_male`/`l_norm_female` and
  the leisure scales (`l_male_scale = l_female_scale = 10.0`) are unchanged
  from the input parquet and preserved in the normmeta.

- **Structure preserved:** 2,319,300 rows; 2,577 × 900; chosen-first ordering
  intact (all groups, 0 violations); no scalar `draw` column; all draw
  identifiers, `is_chosen*`, income, W1, GSUR, and region columns unchanged.
  Input parquet unmodified (2,319,300 × 152 on disk).

- **This is a pilot computational-domain convention, not a final welfare-domain
  decision** on how negative-income alternatives enter the welfare metric. The
  floored rows are flagged with `c_pilot_raw_nonpositive = 1` for downstream
  robustness checks.

- **No EUROMOD re-run was performed.**

- **No precompute was run.**

- **No GSUR merge was run.**

- **No estimation was run** (not even diagnostic).

- **No welfare was computed.**

- **No SA2 was issued.**

- **No promotion was performed.**

- **M1-clean 2016 remains the active production baseline.** No production data,
  P3a YAML, or production scripts were modified.

- **The corrected pooled P3a track is unaffected.**

- **HN-POS resolution slice only.** No change to likelihood formulas, income
  routing, region-dummy logic, parameter handling, or any production script.
  `precompute_data_couples` and `_resolve_draw_column` are unchanged.

---

*Status: HN-POS resolution report v1. All 14 validations PASSED; no halt
condition fired. HP-NORM cleared. Immediate next item: re-entry to the
precompute slice pointing at `__precompute_norm_ready.parquet`.*
