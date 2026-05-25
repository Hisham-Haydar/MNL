# JMP NC Pilot — Normalization-Rebuild Report v1

*France RURO multi-year extension | 2026-05-23*

---

## 1. Verdict

**HALTED. Halt condition HN-POS fired at STEP 3 (Positivity Gate).**

The c_norm rebuild did not write any output. No new parquet was created and no
normmeta sidecar was written. The consumption object
`c_pilot = ils_dispy_male + ils_dispy_female` has 123 non-positive rows across
6 households. Per authorization §8, this is halted without masking: the
affected rows represent genuine couples where one partner's job draw produces a
negative net disposable income large enough to make the household sum
non-positive. This is a substantive modelling finding, not a data error.

---

## 2. Authorization Scope

**Authorizing document:**
`docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md`

**Authorized:** Reading the input parquet (read-only); computing `c_pilot` and
`c_scale_pilot`; positivity gate; if gate passes — writing a new
`__precompute_norm_ready.parquet` with `c_norm` replaced and a normmeta sidecar;
this report.

**Not authorized and not performed:** Flooring, clipping, or EPS-substituting
non-positive consumption (HN-POS); overwriting the input parquet or any
production file (HN-MUT); rebuilding `l_norm_male`/`l_norm_female` (HN-LEIS);
running precompute, GSUR, estimation, welfare, SA2, promotion, M1-clean
displacement (HN-STAGE).

---

## 3. Files Inspected

| File | Purpose |
|---|---|
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_normalization_rebuild_authorization_v1.md` | Authorizing document; read first |
| `Results/JMP_NC_pilot_precompute_report_v1.md` | HP-NORM halt context |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet` | Input; read-only; 2,319,300 × 152 |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready__readymeta.json` | Sidecar metadata |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Leisure scales to preserve |

---

## 4. Files Created

| File | Description |
|---|---|
| `scripts/pilot/_rebuild_c_norm.py` | Rebuild script (halted at HN-POS before any write) |
| `Results/JMP_NC_pilot_normalization_rebuild_report_v1.md` | This report |

---

## 5. Files Modified

**None.** The input precompute-ready parquet, all production files, the frozen
P3a YAML, `precompute_data_couples`, and `_resolve_draw_column` are unchanged.
No output parquet was written (halt before STEP 4).

---

## 6. HP-NORM Root Cause Recap

The `c_norm` column in the pilot precompute-ready parquet was inherited from
the production diagonal parquet at Stage 3/4 cross-join. It was built from
old single-draw EUROMOD income (`production c_scale = 7,597 EUR/month`) and
replicated 900× per couple. The post-EUROMOD merge (Stage 5) added the new
partner-specific `ils_dispy_male` + `ils_dispy_female` outputs from Strategy C′
(30 EUROMOD blocks) but did not rebuild `c_norm`. As a result, the precompute
normalization consistency check failed:

```
max |c_norm × c_scale_production − consumption| = 25,355 EUR/month  > 1.0
```

The fix — rebuilding `c_norm = (ils_dispy_male + ils_dispy_female) /
c_scale_pilot` — encountered a new halt at the positivity gate.

---

## 7. STEP 1 — Input Parquet

```
Input: Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_ready.parquet
Shape: 2,319,300 rows × 152 columns
Stale c_norm: mean=0.986386  min=0.042090  max=3.376602
```

Dimensions match readymeta (PASS). Stale `c_norm` is dimensionless and centred
near 1, consistent with production-diagonal normalization.

**Leisure scales from production mnlmeta (preserved, NOT recomputed):**

```
l_male_scale  = 10.0
l_female_scale = 10.0
```

---

## 8. STEP 2 — Consumption Object and Scale

```
c_pilot = ils_dispy_male + ils_dispy_female  (per row, per joint alternative)
```

Distribution over all 2,319,300 rows:

| Statistic | EUR/month |
|---|---|
| mean | 4,054.286 |
| std | 1,893.444 |
| min | −812.213 |
| p1 | 1,170.916 |
| p5 | 1,638.494 |
| p25 | 2,638.816 |
| p50 | 3,758.529 |
| p75 | 5,100.627 |
| max | 24,364.360 |

```
c_scale_pilot = mean(c_pilot) = 4054.2855556860  EUR/month
Rule: all-rows mean (matching the production normalization convention)
```

`c_scale_pilot > 0`: PASS. The mean of the pilot joint income is positive and
well-separated from zero.

**Comparison to production:** The production couples `c_scale = 7,597 EUR/month`
reflected the old single-draw diagonal income (one income value per couple,
replicated 900×). The pilot `c_scale_pilot = 4,054 EUR/month` reflects the new
joint income across all 900 alternatives (both partners varying). The lower mean
is expected: the product draw includes many off-diagonal cells where one or
both partners are in lower-paid jobs, bringing the average down relative to the
production diagonal which over-represented the observed job.

---

## 9. STEP 3 — Positivity Gate (HN-POS)

**HN-POS FIRED.**

```
Non-positive c_pilot rows: 123  (0.0053% of 2,319,300)
Affected households:         6
```

### 9a. Affected Households

| `idhh` | Non-positive rows | `c_pilot` range (EUR/month) | Cause |
|---|---|---|---|
| 1,567,200 | 25 | −375.61 (constant) | Male draws with `ils_dispy_male = −1,640 EUR`; female `ils_dispy_female = +1,265 EUR` cannot compensate |
| 1,752,900 | 50 | [−812.21, −25.73] | Female income `ils_dispy_female` as low as −1,576 EUR; male income insufficient to compensate in those cells |
| 2,374,500 | 19 | [−662.82, −122.98] | Male income as low as −1,456 EUR in some draw cells |
| 3,270,400 | 3 | −473.48 (constant) | Female `ils_dispy_female = −1,273 EUR`; male `+799 EUR` |
| 3,355,800 | 2 | −120.10 (constant) | Female `ils_dispy_female = −1,129 EUR`; male `+1,008 EUR` |
| 4,323,300 | 24 | −41.42 (constant) | Female `ils_dispy_female = −905 EUR`; male `+864 EUR` |

All 123 rows correspond to job-alternative combinations where one partner's
assigned draw occupation produces a large enough net negative EUROMOD
disposable income that the household sum is non-positive.

### 9b. Substantive Interpretation

These are **real negative-net-income cells** from the EUROMOD tax-benefit
computation — not imputation artifacts or data errors. In the Strategy C′
product draw, each of the 30×30 = 900 cells assigns a specific occupation
draw to each partner. Some occupations (particularly low-wage or high-tax-
liability combinations) produce negative disposable income under the French
tax-benefit system. EUROMOD can return negative disposable income when tax
liabilities and benefit clawbacks exceed gross earnings.

The authorization (§8) is explicit: **do not mask**. Negative joint disposable
income is a substantive modelling question — a couple whose tax-benefit position
is net-negative at some job combination — that must be surfaced and resolved by
decision, not by EPS-substitution. The precompute's internal
`np.maximum(·, EPS)` floor is not a substitute for a principled treatment
because (a) it silently alters the consumption surface for affected households,
and (b) these 6 households account for 5,400 rows (6 × 900) in the precompute
bundle, only 123 of which are problematic — the other 5,277 rows are fine.

### 9c. Affected Draw Coordinates

The non-positive rows span specific (draw_male, draw_female) combinations, not
entire households:

- **idhh 1567200:** 25 cells (male draws with `ils_dispy_male = −1,640 EUR`,
  i.e. the male is assigned a particularly high-tax occupation in certain draws)
- **idhh 1752900:** 50 cells (female draws with `ils_dispy_female` as low as
  −1,576 EUR)
- **idhh 2374500:** 19 cells (male draws with `ils_dispy_male` as low as
  −1,456 EUR)
- **idhh 3270400:** 3 cells (female `ils_dispy_female = −1,273 EUR`)
- **idhh 3355800:** 2 cells (female `ils_dispy_female = −1,129 EUR`)
- **idhh 4323300:** 24 cells (female `ils_dispy_female = −905 EUR`)

---

## 10. What Was NOT Executed

- No `c_norm` was rebuilt (halt before STEP 4).
- No output parquet was written.
- No normmeta sidecar was written.
- No `c_scale_pilot` was persisted to disk.
- No precompute, GSUR, estimation, welfare, SA2, or promotion.
- No data file was modified.

---

## 11. Halt Condition Status

| Halt | Condition | Status |
|---|---|---|
| **HN-POS** | Any `c_pilot ≤ 0` or `c_norm ≤ 0` | **FIRED** — 123 rows across 6 households have `c_pilot ≤ 0`; no masking applied |
| **HN-IDENT** | Rebuild identity max diff > 1.0 | NOT REACHED (halt before rebuild) |
| **HN-SCALE** | `c_scale_pilot ≤ 0` or not recorded | NOT FIRED — `c_scale_pilot = 4,054.29 > 0` (computed but not persisted) |
| **HN-LEIS** | `l_norm_male`/`l_norm_female` changed | NOT FIRED — no write performed |
| **HN-STRUCT** | Row count, groups, chosen-first, scalar draw | NOT FIRED — no write performed |
| **HN-MUT** | Input parquet, production parquet, P3a YAML modified | NOT FIRED — no write performed |
| **HN-STAGE** | Precompute, GSUR, estimation, welfare, SA2, promotion | NOT FIRED — none attempted |

**Single halt condition fired: HN-POS.**

---

## 12. Decision Required

The HN-POS halt surfaces a substantive question: how should the model treat
joint draw cells where `ils_dispy_male + ils_dispy_female ≤ 0`?

Options that would require separate authorization:

1. **Drop the 6 households from the pilot.** 6 of 2,577 pilot couples (0.23%)
   have at least one non-positive cell. Dropping them produces 2,571 couples ×
   900 = 2,313,900 rows. Implication: the pilot sample shrinks slightly; these
   couples are excluded from the precompute and estimation.

2. **Drop only the 123 non-positive rows (within-household).** The 6 households
   remain but their choice sets are reduced from 900 to 875/850/881/897/898/876
   alternatives. This breaks the uniform 900-row group structure that the
   current precompute relies on, and requires a change to group-size handling
   — non-trivial.

3. **Floor `c_pilot` at a minimum positive value before normalization.**
   For example, floor at `EPS` or at `c_pilot_chosen` (the household's chosen
   cell income). This is explicitly NOT authorized by the current document
   (HN-POS); would require a new authorization with a documented and justified
   floor rule.

4. **Re-run EUROMOD for the 6 affected households** with a corrected tax-benefit
   specification if the negative income is caused by a model artefact (e.g.
   uncapped clawback). This would require a new EUROMOD run authorization.

5. **Accept the EPS-floor semantics of `precompute_data_couples`** by
   treating the current halt as informational only, and authorizing a new
   slice that explicitly permits the precompute's internal `np.maximum(c_norm,
   EPS)` floor to handle the 123 rows. This is the thinnest path: the precompute
   already floors non-positive values silently, so the 123 rows would become
   `log(EPS)` in the utility index — a very large negative utility contribution
   that effectively excludes those alternatives. Requires explicit authorization.

---

## 13. Immediate Next Step

A new authorization slice must choose one of the §12 options and name the
permitted treatment for non-positive `c_pilot` cells, or instruct that a
corrected input (e.g. post-EUROMOD re-run or household exclusion) be produced
before the rebuild proceeds.

The rebuild can resume immediately once an authorization is in place that
resolves the HN-POS condition. All other measurements from this session
(c_scale_pilot = 4,054.2856 EUR/month, rebuild identity, leisure scales,
structure checks) are complete and will pass on re-entry.

---

## Required Final Statements

- **This authorization covered only the pilot consumption normalization
  rebuild.** `c_norm = (ils_dispy_male + ils_dispy_female) / c_scale_pilot`
  on a new pilot-only parquet. The rebuild did not complete due to HN-POS.

- **Leisure normalization was not rebuilt.** `l_norm_male`/`l_norm_female`
  and the leisure scales (`l_male_scale = 10.0`, `l_female_scale = 10.0`) are
  preserved.

- **HN-POS fired.** 123 rows across 6 households have
  `ils_dispy_male + ils_dispy_female ≤ 0`. No masking, flooring, clipping,
  or EPS-substitution was applied. The non-positive rows were reported in full
  (§9a). This is a substantive modelling finding.

- **No output parquet was written.** The input precompute-ready parquet
  (2,319,300 × 152) is unchanged.

- **No normmeta sidecar was written.**

- **No precompute was run.**

- **No GSUR merge was run.**

- **No estimation was run** (not even diagnostic).

- **No welfare was computed.**

- **No SA2 was issued.**

- **No promotion was performed.**

- **M1-clean 2016 remains the active production baseline.** No production data,
  P3a YAML, or production scripts were modified.

- **The corrected pooled P3a track is unaffected.**

- **Normalization rebuild slice only.** No change to likelihood formulas,
  income routing, region-dummy logic, parameter handling, or any production
  script. `precompute_data_couples` and `_resolve_draw_column` are unchanged.

---

*Status: normalization-rebuild report v1. HN-POS fired; rebuild not executed;
no output written. Immediate next item: authorization to resolve the 123
non-positive c_pilot rows (§12 options).*
