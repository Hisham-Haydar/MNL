# JMP NC Pilot — Precompute-Slice Report v2

*France RURO multi-year extension | 2026-05-23*

---

## 1. Precompute Verdict

**PASSED. All 13 pre-run checks and all 11 post-run validations cleared; no
halt condition fired.**

`precompute_data_couples` ran on the HN-POS-resolved, normalized pilot parquet
(`__precompute_norm_ready.parquet`) and completed in **0.46 seconds**. The
`PrecomputedDataCouples` artifact was persisted to the pilot-only output path.
HP-NORM is confirmed cleared: `c_scale_pilot = 4,054.2856 EUR/month` (pilot
all-rows mean) was used, not the old production `c_scale = 7,597 EUR/month`.

---

## 2. Authorization Scope

**Authorizing documents:**

- `docs/JMP_NC_pilot_precompute_slice_authorization_v1.md` (precompute slice)
- `docs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md` (HN-POS resolution,
  prior slice — cleared before this run)

**Authorized in this run:** 13 pre-run inspection checks; `precompute_data_couples`
called as-is with `include_wage_vars=True, include_loc_vars=False`; artifact
persistence; 11 post-run validations; this report.

**Not authorized and not performed:** Any edit to `precompute_data_couples` or
`_resolve_draw_column` (HP-LOGIC); any synthetic column (HP-SYNTH); adding a
scalar `draw` (HP-DRAW); modifying the pilot parquet, any production parquet, or
the frozen P3a YAML (HP-MUT); GSUR, estimation, welfare, SA2, promotion, or
M1-clean displacement (HP-STAGE).

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/JMP_NC_pilot_precompute_slice_authorization_v1.md` | Authorizing document |
| `Results/JMP_NC_pilot_HN_POS_resolution_report_v1.md` | HN-POS resolution confirmation (123 rows, 6 households floored) |
| `Results/JMP_NC_pilot_precompute_report_v1.md` | Prior HP-NORM halt detail |
| `scripts/enhanced/estimation_utils.py` | `precompute_data_couples` (line 944); `_resolve_draw_column` (line 59); `EPS = 1e-12` (line 49) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet` | Input (read-only); 2,319,300 × 154 |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json` | Normalization metadata |

---

## 4. Files Created

| File | Description |
|---|---|
| `scripts/pilot/_run_precompute.py` | Pre-run checks + precompute execution + post-run validation |
| `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl` | `PrecomputedDataCouples` artifact (pickle protocol 5, 858.2 MB) |
| `Data/pilot/nc_2016_couples/precomputed/precompute_run_summary.json` | Machine-readable run summary |
| `Results/JMP_NC_pilot_precompute_report_v2.md` | This report |

---

## 5. Files Modified

**None.** The input parquet (`__precompute_norm_ready.parquet`), the original
precompute-ready parquet, all production parquets, the P3a YAML,
`precompute_data_couples`, and `_resolve_draw_column` are unchanged.

---

## 6. Input Normalized Parquet

```
Path:   Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready.parquet
Shape:  2,319,300 rows × 154 columns
        (152 original precompute-ready cols
         + c_norm rebuilt from C′ joint income
         + c_pilot_raw_nonpositive diagnostic flag
         + diagnostic c_pilot column)
```

This is the HN-POS-resolved parquet produced in the prior slice. The 123 rows
with `c_pilot_raw ≤ 0` have `c_norm = EPS = 1e-12` (normalized floor, explicit
and flagged). The old `__precompute_ready.parquet` was **not** used.

---

## 7. Input Normalization Metadata

```
File:   Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json
Schema: nc_pilot_precompute_norm_ready_v1
```

Normalization block consumed by `precompute_data_couples`:

| Key | Value | Source |
|---|---|---|
| `c_scale` | 4,054.2855556860 EUR/month | Pilot: mean(ils_dispy_male + ils_dispy_female) over all rows |
| `l_male_scale` | 10.0 | Production mnlmeta (preserved, not recomputed) |
| `l_female_scale` | 10.0 | Production mnlmeta (preserved, not recomputed) |

**Pre-check 8.1 result:** `c_scale = 4,054.29 ≠ 7,597.08` (old production).
Pilot value confirmed; HP-NORM does not re-fire.

The function resolves the nested `normalization.couples.c_scale` path (line
985–988 of `estimation_utils.py`) and sets `c_scale = 4,054.2856` and
`l_scale = 10.0` for use inside `precompute_data_couples`.

---

## 8. Entry Point Used

```python
eu.precompute_data_couples(
    df,
    metadata,                 # normalization from normmeta
    include_wage_vars=True,   # W1 wage layer populated
    include_loc_vars=False,   # occupation not a free layer (pilot occ_spec=fixed)
)
```

`precompute_data_couples` is called **as-is** with no modification to its logic
(HP-LOGIC clear). `_resolve_draw_column` is invoked internally by the function.

---

## 9. Required-Column Check

All 13 pre-run checks passed before the function was called.

| Check | Column / Condition | Result |
|---|---|---|
| 1 | Row count = 2,319,300 | PASS |
| 2–3 | Groups = 2,577; all size 900 | PASS |
| 4 | Chosen-first (draw_joint==0, is_chosen==1 at pos 0) | PASS (0 violations) |
| 5 | `draw_joint` present; scalar `draw` absent | PASS |
| 6 | `_resolve_draw_column` → `draw_joint` | PASS |
| 7 | `ils_dispy_male`, `ils_dispy_female` complete (0 missing) | PASS |
| 8 | `c_norm` finite, positive, ≥ EPS; mean=1.000005; min=1e-12 | PASS |
| 8.1 | `c_scale = 4,054.29` (pilot), not 7,597.08 (old production) | PASS |
| 9 | `c_pilot_raw_nonpositive` flag present; sum = 123 | PASS |
| 10 | `l_norm_male`, `l_norm_female` finite; min=1.0 | PASS |
| 11 | W1: `wage_male`, `wage_female`, `pexp_years_male`, `pexp_years_female` | PASS |
| 12 | Hard-required: `idhh`, `year_tag`, `draw_joint`, `is_chosen`, `c_norm`, `l_norm_male`, `l_norm_female`, `hours_male`, `hours_female`, `prior` | PASS (0 missing) |
| 13 | No missing hard-required column → do not halt | N/A (all present) |

---

## 10. Draw-Column Resolution

```
_resolve_draw_column(df) → "draw_joint"
```

`draw_joint` is present; scalar `draw` is absent. The resolver returns
`df["draw_joint"]` (Option B fallback, patched in
`docs/JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md`).
No scalar `draw` was added to the data (HP-DRAW clear).

Internally, `precompute_data_couples` uses `idhh` + `year_tag` for group
construction (not `draw`); `draw_joint` is used only for validation and
chosen-row identification.

---

## 11. Normalization Check

**HP-NORM: CLEARED.**

| Quantity | Value |
|---|---|
| `c_scale_pilot` used | 4,054.2855556860 EUR/month |
| Old production `c_scale` | 7,597.0813 EUR/month |
| Prior HP-NORM max diff | 25,355 EUR/month (using old c_scale on stale c_norm) |
| Post-rebuild identity max diff | 1.82 × 10⁻¹² EUR/month (non-floored rows) |
| `c_norm` mean | 1.000005 (≈ 1 by construction) |
| `c_norm` min | 1 × 10⁻¹² (= EPS, on the 123 floored rows) |

The consumption array inside `precompute_data_couples` is:

```python
consumption = np.maximum(df["c_norm"].values.copy(), EPS)  # EPS = 1e-12
```

Since `c_norm ≥ EPS` already holds for all rows (enforced in the rebuild
slice), `np.maximum` is a no-op here. The 123 floored rows enter with
`consumption = EPS = 1e-12` → `log_c = log(1e-12) ≈ −27.63`, giving
near-zero utility weight in the softmax.

---

## 12. Chosen-Row Validation

| Check | Result |
|---|---|
| First row of each group has `draw_joint == 0` | PASS (0 violations, 2,577 groups) |
| First row of each group has `is_chosen == 1` | PASS (0 violations) |
| Post-precompute: `actual_choice` at position 0 in all groups | PASS (0 bad; `is_chosen` path used) |

`precompute_data_couples` correctly identified the chosen row from `is_chosen`
for all 2,577 groups.

---

## 13. Group-Size Validation

```
n_groups = 2,577
n_obs    = 2,319,300
All group sizes = 900: PASS
Group structure: uniform 2,577 × 900
```

`year_tag == 2` throughout the pilot parquet (2016 only), so the function's
internal multi-year sort is a no-op and `_group_col = df["idhh"].astype(int64)`
is used for boundary detection.

---

## 14. Income-Column Validation

| Column | Missing | Notes |
|---|---|---|
| `ils_dispy_male` | 0 | Complete; used to build `c_norm` (prior slice) |
| `ils_dispy_female` | 0 | Complete; used to build `c_norm` (prior slice) |
| `c_pilot_raw_nonpositive` | — | Flag sum = 123; marks the EPS-floored cells |

`ils_dispy_male` and `ils_dispy_female` are preserved unchanged in the parquet;
`precompute_data_couples` does not read them directly (consumption enters via
the pre-built `c_norm`).

---

## 15. W1/Proposal-Density Validation

| Column | Present | Non-finite |
|---|---|---|
| `wage_male` | Yes | 0 |
| `wage_female` | Yes | 0 |
| `pexp_years_male` | Yes | — |
| `pexp_years_female` | Yes | — |

With `include_wage_vars=True`, the function consumed all four columns:

```
log_wage_male:   populated (non-None); non-finite = 0
log_wage_female: populated (non-None); non-finite = 0
pexp_years_male/female: extracted; pexp_years2_* derived as squares
```

The W1 wage layer is **fully populated**; no silent zeroing occurred.

---

## 16. Precompute Execution

```
Entry point:        precompute_data_couples (estimation_utils.py line 944)
include_wage_vars:  True
include_loc_vars:   False
Rows consumed:      2,319,300
Groups built:       2,577
Alternatives/group: 900
Chosen-row source:  is_chosen column (all 2,577 groups identified cleanly)
Draw resolution:    draw_joint (via _resolve_draw_column)
Region path:        reg_nuts1_2..8 (direct path, all 7 present and non-degenerate)
GSUR path:          gsur_male / gsur_female (direct; no zeros fallback)
idorighh:           absent → idhh fallback for cluster_ids
                    (pilot is 2016-only; cross-year clustering not required)
```

The function completed without exception. No guarded fallbacks fired for GSUR
or region. The `idorighh` fallback to `idhh` is expected for the pilot (single
year; `idhh == idorighh` in single-year data).

---

## 17. Wall-Time and Memory

```
Wall time:             0.46 seconds
Peak memory (tracemalloc): 953.4 MB
Output artifact:       858.2 MB (pickle protocol 5)
```

**Pooled-cycle projection** (from pilot measurements):

| Scenario | Couples | Alts | Est. wall time | Est. peak memory |
|---|---|---|---|---|
| Pilot (measured) | 2,577 | 900 | 0.46 s | 953 MB |
| Pooled P3a (projected, 900 alts) | 7,438 | 900 | 1.3 s | 2,752 MB |
| Pooled P3a (projected, 1,600 alts) | 7,438 | 1,600 | 2.3 s | 4,892 MB |

Scale factor: 7,438 / 2,577 = 2.886×. Precompute cost at production scale is
well within feasibility bounds. Memory at 1,600 alts (~4.9 GB) is the binding
constraint for server RAM sizing.

---

## 18. Output Artifact

```
Path:     Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl
Format:   Python pickle, protocol 5
Type:     PrecomputedDataCouples (dataclass)
Size:     858,226,512 bytes (858.2 MB)
Readable: PASS (read-back verified)
```

**Key arrays in the artifact:**

| Array | Shape | Notes |
|---|---|---|
| `consumption` | (2,319,300,) | `np.maximum(c_norm, EPS)`; min = 1e-12 |
| `log_c` | (2,319,300,) | `log(consumption)`; min = −27.63 (floored rows) |
| `leisure_male` | (2,319,300,) | `np.maximum(l_norm_male, EPS)` |
| `log_l_male` | (2,319,300,) | `log(leisure_male)`; min = 0.0 |
| `leisure_female` | (2,319,300,) | `np.maximum(l_norm_female, EPS)` |
| `log_l_female` | (2,319,300,) | `log(leisure_female)`; min = 0.0 |
| `prior` | (2,319,300,) | `np.maximum(prior, EPS)`; min = 6.29e-11 |
| `log_wage_male` | (2,319,300,) | W1 log wages, male; non-finite = 0 |
| `log_wage_female` | (2,319,300,) | W1 log wages, female; non-finite = 0 |
| `group_starts` | (2,577,) | Group boundary indices |
| `group_ends` | (2,577,) | Group boundary indices |
| `actual_choice` | (2,319,300,) | 1.0 at chosen row (position 0) of each group |
| `c_scale` | scalar | 4,054.2855556860 |
| `l_scale` | scalar | 10.0 |

No production precomputed artifact was overwritten.

---

## 19. Output Validation

| # | Check | Result |
|---|---|---|
| V1 | Precompute completed without exception | PASS |
| V2 | `n_groups` = 2,577 | PASS |
| V3 | All group sizes = 900 | PASS |
| V4 | Chosen at position 0 (all groups; bad=0) | PASS |
| V5 | Draw resolution: `draw_joint` used, no scalar `draw` | PASS |
| V6 | `c_norm` rebuilt from `(ils_dispy_male + ils_dispy_female) / c_scale_pilot` | PASS (normmeta) |
| V7 | `consumption` (c_norm post-floor): positive, finite; min=1e-12 | PASS |
| V8 | `log_c`, `log_l_male`, `log_l_female` finite; `prior` finite and positive | PASS |
| V9 | `log_wage_male`, `log_wage_female` non-None; non-finite=0 | PASS |
| V10 | Output file exists and is readable | PASS |
| V11 | No GSUR, estimation, welfare, SA2, or promotion | PASS |

**All 11 post-run validations: PASS.**

---

## 20. Halt-Condition Status

| Halt | Condition | Status |
|---|---|---|
| **HP-LOGIC** | Edit to `precompute_data_couples` or `_resolve_draw_column` | NOT FIRED |
| **HP-COL** | Hard-required column or normalization metadata missing | NOT FIRED |
| **HP-SYNTH** | Synthetic column created | NOT FIRED |
| **HP-NORM** | Normalization inconsistency > 1.0 EUR/month | NOT FIRED (c_scale_pilot used; identity 1.82e-12) |
| **HP-DRAW** | Scalar `draw` written to data | NOT FIRED |
| **HP-MUT** | Pilot parquet, production parquet, or P3a YAML modified | NOT FIRED |
| **HP-STAGE** | GSUR, estimation, welfare, SA2, promotion, M1-clean displacement | NOT FIRED |

---

## 21. What Was Not Executed

- No EUROMOD was run.
- No GSUR merge was run.
- No MNL estimation was run (not even a diagnostic run).
- No welfare computation was performed.
- No SA2 was issued.
- No canonical promotion was performed.
- No modification to the frozen P3a YAML.
- No edit to any production script.
- No scalar `draw` was added to any data file.
- `precompute_data_couples` logic was not changed.

---

## 22. Whether Pilot Estimation Preflight Is Now Ready

**Precompute is complete; estimation preflight requires a separate
authorization.** The `PrecomputedDataCouples` artifact at
`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl`
is the input the estimator consumes. The immediate prerequisites for a
diagnostic estimation run are:

1. A diagnostic-estimation authorization slice naming:
   - the exact estimator entry point (`estimate_couples_mnl` or equivalent),
   - the pilot YAML or inline parameter dict,
   - the halt conditions (no welfare, no SA2, no promotion),
   - the maximum number of solver iterations permitted.
2. Confirmation that a pilot-specific YAML (or parameter override) is available
   and does not point at production P3a data.
3. Cluster-ID note: the precomputed artifact uses `idhh` as `cluster_ids`
   (the `idorighh` fallback was invoked because `idorighh` is absent from the
   pilot parquet). For a diagnostic single-year pilot run this is acceptable;
   for a production-quality SE estimate `idorighh` would need to be present.

---

## 23. Whether Welfare Computation Is Authorized

**No.** Welfare requires estimated preference parameters from a completed MNL
run, which is downstream of precompute. No authorization for welfare computation
is pending or implied.

---

## 24. Whether M1-Clean Remains Active

**Yes.** M1-clean 2016 is the active production baseline. No production data,
P3a YAML, production scripts (other than the single draw-resolution site
patched in the compatibility slice), or the corrected pooled P3a track were
modified. The pilot artifact is pilot-only; no production precomputed artifact
was overwritten.

---

## 25. Immediate Next Task

A **diagnostic-estimation authorization** — a narrowly scoped amendment that:

1. Names the estimator entry point and solver (e.g. `estimate_couples_mnl`
   with `--solver gamspy-conopt --vectorized`).
2. Specifies the pilot precomputed artifact as input.
3. Provides a pilot YAML or inline parameter dict (not the frozen P3a YAML).
4. States halt conditions: no welfare, no SA2, no promotion; stop after
   convergence or max-iteration limit.
5. States the output path for the estimated parameter vector.
6. Addresses cluster-SE handling (`idhh` vs `idorighh` for the pilot).

---

## Required Final Statements

- **The precompute retry PASSED.** All 13 pre-run checks and all 11 post-run
  validations cleared; no halt condition fired. `precompute_data_couples`
  completed in 0.46 seconds on 2,319,300 rows × 2,577 groups.

- **No EUROMOD was run.**

- **No GSUR merge was run.**

- **No estimation was run.**

- **No welfare was computed.**

- **No SA2 was issued.**

- **No scalar draw column was added to the pilot parquet.**

- **M1-clean 2016 remains the active production baseline.** No production data,
  P3a YAML, or production scripts were modified. The corrected pooled P3a track
  (1,244,500 rows, construction complete 2026-05-20) is unaffected.

- **The corrected pooled P3a track is unaffected.**

- **`c_scale_pilot = 4,054.2856 EUR/month`** (all-rows mean of
  `ils_dispy_male + ils_dispy_female` in the pilot parquet) was used, not the
  old production `c_scale = 7,597 EUR/month`. HP-NORM is confirmed cleared.

- **The 123 EPS-floored rows** (6 households with negative joint disposable
  income in specific product-draw cells) enter the precomputed artifact with
  `consumption = EPS = 1e-12` → `log_c ≈ −27.63`. This is the explicit,
  flagged computational-domain convention authorized by
  `docs/JMP_NC_pilot_HN_POS_resolution_authorization_v1.md`. It is not a
  final welfare-domain decision.

---

*Status: precompute-slice report v2. Precompute PASSED; artifact persisted.
Immediate next item: diagnostic-estimation authorization (§25).*
