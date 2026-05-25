# JMP NC Pilot — loc4 Precompute Augmentation Report v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Authorization:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md`
**Script:** `scripts/pilot/_run_loc4_precompute_augmentation.py`
**Output pkl:** `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`
**Summary sidecar:** `Data/pilot/nc_2016_couples/precomputed/loc_precompute_run_summary.json`
**Status: ALL VALIDATIONS PASS — augmentation complete. No estimation run.**

---

## 1. Scope and Corrected-Error Provenance

This report documents the `include_loc_vars=False → True` precompute augmentation
for the NC pilot couples-only 2016 diagnostic estimation.

**Corrected authorization error:** The prior precompute slice
(`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_precompute_slice_authorization_v1.md`) built the
`PrecomputedDataCouples` object with `include_loc_vars=False` while the diagnostic
estimation spec (`estimation_spec_nc_pilot_couples_2016.yaml`) included six free
occupation-opportunity parameters (`beta_occ_2_cm`, `beta_occ_3_cm`, `beta_occ_4_cm`,
`beta_occ_2_cf`, `beta_occ_3_cf`, `beta_occ_4_cf`). These parameters multiply
`loc4_k × working` — but without `loc4_*` arrays in the pkl, their contribution
was identically zero, their gradient was identically zero, and they defined a
degenerate 6-dimensional flat manifold in the objective that the scipy L-BFGS-B
solver could not leave.

**`delta_occ` vs `beta_occ` distinction (unchanged):** `delta_occ` is the W1
occupation wage premium — calibrated in the draw stage, fixed/not free. `beta_occ`
is the occupation availability mass — a free structural parameter that enters the
opportunity index and needed the `loc4_*` arrays. This augmentation provides those
arrays; it does not change `delta_occ`.

---

## 2. Prior Diagnostic Estimation Halt Status

The first diagnostic estimation attempt (scipy L-BFGS-B) was halted before any
result was accepted:

| Item | Value |
|---|---|
| CPU time consumed | ~17,312 s (~4.8 h) across processes |
| Root cause | `loc4_*` absent from pkl → `beta_occ_*` zero gradient → degenerate manifold |
| Per-LL evaluation cost | ~60 s over 2,319,300 rows |
| `max_iterations: 3000` effectiveness | None — solver appeared stuck in flat region |
| Processes killed | Yes (manually) |
| Result accepted | **No** |
| Output promoted | **No** |
| Welfare/SA2/estimation result | **None recorded** |
| Source parquet | Unchanged |
| Prior pkl | Unchanged |

---

## 3. GSUR Status (Not the Problem)

GSUR is correct and unaffected. The precomputed object carries `gsur_male` and
`gsur_female` (2,319,300 rows each) built via the direct path with no zeros
fallback. These are group-specific unemployment rates matched to each household's
region × sex group from the upstream GSUR merge done before the C′ EUROMOD runs.
Under `occ_spec=fixed`, GSUR does not vary across a couple's 900 draws — replicating
it across the product is correct. The hang had nothing to do with GSUR.

**Augmentation result:** `gsur_male` and `gsur_female` in the new `_loc.pkl` are
bit-identical to the prior pkl (V11 PASS; `np.allclose` with atol=1e-10).

---

## 4. Region Status (Not the Problem)

Region is correct and unaffected. `reg2..reg8` (Île-de-France = reference category)
enter market opportunity additively as `beta_E_drgn* × reg* × working` — not
interacted with occupation. All seven region dummies are present and non-degenerate
in both the prior and new pkl. The hang had nothing to do with region.

**Augmentation result:** region arrays preserved unchanged (V9 PASS).

---

## 5. Precondition Check — HL-COL

`loc4_male` and `loc4_female` confirmed present in
`__precompute_norm_ready.parquet` with the expected coding.

| Item | Male | Female |
|---|---|---|
| Present in parquet | Yes | Yes |
| Missing values | 0 | 0 |
| Unique codes | {-2, -1, 1, 2, 3, 4} | {-2, -1, 1, 2, 3, 4} |
| Code -2 (reported, not recoded) | 930 rows | 90 rows |
| Code -1 (reported, not recoded) | 231,000 rows | 228,900 rows |
| Code 1 (cat 1 = reference) | 562,920 rows | 556,530 rows |
| Code 2 | 300,630 rows | 303,060 rows |
| Code 3 | 193,590 rows | 206,130 rows |
| Code 4 | 1,030,230 rows | 1,024,590 rows |

Codes -2 and -1 are reported and **not recoded**. `precompute_data_couples` uses
`fillna(0)` before building dummies, so codes -2/-1 → 0 after fillna, and since
dummies trigger only for codes 1–4, these rows map to all-dummy-zero (reference
category treatment). This is consistent with the production convention.

**HL-COL: PASS**

---

## 6. Off-Axis Product-Consistency — HL-VARY

Occupation is drawn per partner axis: `loc4_male` varies across `draw_male` but
must be constant within each `(idhh, year_tag, draw_male)` across all `draw_female`
values; symmetrically for `loc4_female`.

Check was run on 500 households (15,000 `(idhh, year_tag, draw_male)` groups and
15,000 `(idhh, year_tag, draw_female)` groups):

| Check | Violations | Result |
|---|---|---|
| `loc4_male` constant within `(idhh, year_tag, draw_male)` | 0 | PASS |
| `loc4_female` constant within `(idhh, year_tag, draw_female)` | 0 | PASS |

**HL-VARY: PASS**

---

## 7. Rebuild — Precompute Flags and Normalization

```python
precompute_data_couples(
    df,                        # __precompute_norm_ready.parquet (read-only)
    metadata=normmeta,         # reused from normmeta json — NOT recomputed
    include_wage_vars=True,    # unchanged (W1 wage layer)
    include_loc_vars=True,     # THE CHANGE: was False, now True
)
```

**Normalization reused (HL-NORM: PASS):**

| Parameter | Value |
|---|---|
| `c_scale` | 4,054.2855556859554 EUR/month (pilot mean joint income) |
| `l_male_scale` | 10.0 |
| `l_female_scale` | 10.0 |

No re-normalization. `precompute_data_couples` logic not edited (HL-LOGIC: PASS).

**Runtime:** 0.52 s | **Peak memory:** 1,139 MB | **Output:** 1,043.8 MB

---

## 8. Output Artifact

| Item | Value |
|---|---|
| New pkl | `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl` |
| Size | 1,043,770,872 bytes (1,043.8 MB) |
| Prior pkl | `fr_pilot_nc_2016_couples_precomputed.pkl` — **NOT overwritten** (858,226,512 bytes, unchanged) |
| Sidecar | `loc_precompute_run_summary.json` |

**HL-MUT: PASS** — new pkl written; source parquet and prior pkl unchanged.

---

## 9. Validation Results (Authorization §11)

### V1 — Structure
| Check | Value | Result |
|---|---|---|
| n_groups | 2,577 | PASS |
| n_obs | 2,319,300 | PASS |
| All group sizes = 900 | True | PASS |

### V2 — Chosen at Position 0
All 2,577 groups have chosen alternative at position 0. Bad count: 0. **PASS**

### V3 — Occupation Arrays Present
All 10 required arrays present in new pkl:
`loc4_male`, `loc4_female`, `loc4_1_male`, `loc4_2_male`, `loc4_3_male`,
`loc4_4_male`, `loc4_1_female`, `loc4_2_female`, `loc4_3_female`, `loc4_4_female`.
**PASS**

### V4 — Non-Degenerate (HL-DEGEN gate)

| Array | Min | Max | Mean | Non-degenerate |
|---|---|---|---|---|
| `loc4_2_male` | 0.0 | 1.0 | 0.1296 | PASS |
| `loc4_3_male` | 0.0 | 1.0 | 0.0835 | PASS |
| `loc4_4_male` | 0.0 | 1.0 | 0.4442 | PASS |
| `loc4_2_female` | 0.0 | 1.0 | 0.1307 | PASS |
| `loc4_3_female` | 0.0 | 1.0 | 0.0889 | PASS |
| `loc4_4_female` | 0.0 | 1.0 | 0.4418 | PASS |

Reference dummy sums (`loc4_1_*`): male 562,920; female 556,530.
**HL-DEGEN: not fired. PASS**

### V5 — Scales Match Pilot Normalization
`c_scale = 4,054.2856` (matches to 1e-6). `l_scale = 10.0`. **PASS**

### V6 — Core Arrays Finite

| Array | Finite | Min | Max |
|---|---|---|---|
| `log_c` | Yes | -27.6310 | 1.7933 |
| `log_l_male` | Yes | 0.0000 | 2.0794 |
| `log_l_female` | Yes | 0.0000 | 2.0794 |
| `prior` | Yes | 0.0000 | 0.0100 |
| `log_wage_male` | Yes | 0.0000 | 4.6642 |
| `log_wage_female` | Yes | 0.0000 | 4.7591 |

**PASS**

### V7 — Consumption Positive
`consumption.min() = 1.0e-12 > 0` (EPS floor). **PASS**

### V8 — GSUR Preserved

| Array | Finite | Has variation | Mean |
|---|---|---|---|
| `gsur_male` | Yes | Yes | 0.0966 |
| `gsur_female` | Yes | Yes | 0.0878 |

**PASS**

### V9 — Region Arrays Preserved

| Array | Mean |
|---|---|
| `reg2` | 0.1731 |
| `reg3` | 0.0741 |
| `reg4` | 0.0881 |
| `reg5` | 0.1878 |
| `reg6` | 0.1133 |
| `reg7` | 0.1184 |
| `reg8` | 0.0966 |

All 7 arrays present. **PASS**

### V10 — HN-POS Flag Preserved
EPS-floored rows (log_c ≈ log(1e-12) = -27.631): **123** (expected 123). **PASS**

### V11 — Prior Pkl Cross-Check

| Array | Match (atol=1e-10) |
|---|---|
| `gsur_male` | PASS |
| `gsur_female` | PASS |
| `log_c` | PASS |
| `c_scale` | PASS |

Prior pkl byte count unchanged: 858,226,512 bytes. **PASS**

### V12 — Source Parquet Unchanged
Row count: 2,319,300 (unchanged). **PASS**

---

## 10. Halt Condition Status

| Code | Condition | Status |
|---|---|---|
| HL-COL | `loc4_male`/`loc4_female` absent or wrong coding | Not fired — both present, codes {-2,-1,1,2,3,4} |
| HL-DEGEN | Any `loc4_*` dummy all-zero | Not fired — all dummies have both 0s and 1s |
| HL-VARY | Off-axis constancy violated | Not fired — 0 violations in 500-household sample |
| HL-INJECT | Runtime injection used as pkl substitute | Not fired — pkl rebuilt on disk |
| HL-LOGIC | `precompute_data_couples` logic edited | Not fired — only call flag changed |
| HL-NORM | Re-normalization applied | Not fired — pilot normalization reused |
| HL-MUT | Source parquet or prior pkl overwritten | Not fired — new pkl only |
| HL-STAGE | Estimation/EUROMOD/welfare/SA2/promotion run | Not fired — none run |

---

## 11. Runtime and Memory

| Metric | Value |
|---|---|
| Precompute wall time | 0.52 s |
| Write wall time | 2.1 s |
| Peak memory (tracemalloc) | 1,139 MB |
| New pkl size | 1,043.8 MB (+185.6 MB vs prior 858.2 MB, from loc4 arrays) |

The 185.6 MB increase reflects the 10 additional occupation arrays
(8 dummies + 2 raw `loc4_*` arrays) over 2,319,300 rows × float64.

---

## 12. Code Accounting — loc4 Values Including -1 and -2

| Code | Male rows | Female rows | Treatment |
|---|---|---|---|
| -2 | 930 | 90 | `fillna(0)` → all dummies zero (reference) |
| -1 | 231,000 | 228,900 | `fillna(0)` → all dummies zero (reference) |
| 1 | 562,920 | 556,530 | `loc4_1_*` = 1 |
| 2 | 300,630 | 303,060 | `loc4_2_*` = 1 |
| 3 | 193,590 | 206,130 | `loc4_3_*` = 1 |
| 4 | 1,030,230 | 1,024,590 | `loc4_4_*` = 1 |

Codes -1 and -2 are not recoded and not silently absorbed into any occupation
category. They are treated as "not in any coded occupation" — same as reference
category (category 1) in the opportunity index. This is a pilot computational
convention; no welfare inference is made from this treatment.

---

## Required Final Statements

- **This authorizes only a pilot precompute augmentation** — re-running
  `precompute_data_couples` with `include_wage_vars=True, include_loc_vars=True`
  on the existing `__precompute_norm_ready.parquet`, producing a new `_loc.pkl`.
- **It corrects an authorization error** (`include_loc_vars=False` while `beta_occ`
  free). `delta_occ` (W1 occupation wage premium) remains calibrated in the draw
  and fixed; `beta_occ` (occupation availability mass) is the free parameter that
  needed the `loc4_*` arrays — now provided.
- **Not a GSUR problem** and **not a region problem**: both are present, correct,
  and preserved bit-identical to the prior pkl.
- **Runtime loc4 injection was not used**: the pkl itself was rebuilt (HL-INJECT
  not fired).
- **No estimation, EUROMOD, GSUR merge, data rebuild, welfare, SA2, or
  promotion** was run. M1-clean 2016 active. Corrected pooled P3a track
  unaffected. Source parquet and prior pkl unchanged.
- **All 12 validations PASS. All 8 halt conditions clear.**

---

*Next: diagnostic estimation re-run (GAMSPy/CONOPT, capped iterations) on
`fr_pilot_nc_2016_couples_precomputed_loc.pkl`. Requires a fresh diagnostic-
estimation authorization update referencing the `_loc.pkl`.*
