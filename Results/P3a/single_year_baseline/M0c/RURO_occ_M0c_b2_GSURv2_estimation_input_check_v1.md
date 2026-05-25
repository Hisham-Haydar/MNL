# RURO occ M0c_b2 GSURv2 Estimation Input Check v1

Date: 2026-05-17
Prepared by: Claude Code
Authorisation basis: `Results/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md` (all M1–M10 PASS)

---

## 1. Files checked

| File | Path | Status |
|---|---|---|
| GSURv2 singles parquet | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet` | EXISTS |
| GSURv2 couples parquet | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__couples.parquet` | EXISTS |
| Canonical metadata sidecar | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__mnlmeta.json` | EXISTS (source) |
| GSURv2 metadata sidecar | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | CREATED (copied) |
| Canonical singles parquet | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet` | EXISTS, UNTOUCHED |
| Canonical couples parquet | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet` | EXISTS, UNTOUCHED |
| Economic model YAML | `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml` | EXISTS, UNTOUCHED |
| Provenance YAML copy | `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` | CREATED |

---

## 2. GSURv2 parquet paths

The estimator `--mnl-base` stem to use:

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2
```

The estimator will load:

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__couples.parquet
```

---

## 3. Metadata sidecar status

`fr_2016_RURO_mnl_GSURv2__mnlmeta.json` **did not exist** before this task.

Action taken: copied from canonical sidecar without content modification.

| Property | Value |
|---|---|
| Source | `fr_2016_RURO_mnl__mnlmeta.json` |
| Destination | `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` |
| Source size | 57,973 bytes |
| Destination size | 57,973 bytes (identical) |
| Source mtime | 2026-05-13T08:38:22Z |

---

## 4. Metadata copy — what was changed and why

**Nothing was changed in the metadata content.** The file is a byte-for-byte copy.

The sidecar records preparation-step provenance (MNL prep script, draws paths, normalization
constants, sample sizes, column lists). All of these values are identical between the canonical
and GSURv2 parquets: the GSURv2 rebuild added GSUR columns only; it did not change row counts,
household counts, normalization constants, draws paths, or any other prep-step property.

The `gsur_file` entry in the sidecar (`inputs.gsur_file`) references
`Data/external/FR_gsur_ruro.parquet` (the v1 GSUR file used during MNL prep). This entry is
descriptive provenance of the original prep step; it is not re-read at estimation time. The
corrected GSUR values are already embedded in the GSURv2 parquet columns and do not require a
separate lookup at estimation time. No update to this field is needed or appropriate.

---

## 5. Row and household counts

Verified by `pd.read_parquet` on the live files:

| Parquet | Rows | Households | Matches rebuild report |
|---|---|---|---|
| GSURv2 singles | 167,600 | 1,676 | YES (report §3: 167,600 rows) |
| GSURv2 couples | 257,700 | 2,577 | YES (report §3: 257,700 rows) |
| Canonical singles | 167,600 | 1,676 | Unchanged |
| Canonical couples | 257,700 | 2,577 | Unchanged |

---

## 6. Canonical files untouched

| File | mtime before | mtime after | Size | Status |
|---|---|---|---|---|
| `fr_2016_RURO_mnl__singles.parquet` | 2026-05-13T08:38:21Z | 2026-05-13T08:38:21Z | 21,500,551 bytes | **UNTOUCHED** |
| `fr_2016_RURO_mnl__couples.parquet` | 2026-05-13T08:38:22Z | 2026-05-13T08:38:22Z | 43,108,822 bytes | **UNTOUCHED** |
| `fr_2016_RURO_mnl__mnlmeta.json` | 2026-05-13T08:38:22Z | 2026-05-13T08:38:22Z | 57,973 bytes | **UNTOUCHED** |

---

## 7. Exact `--mnl-base` to use

```
--mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2"
```

The estimator appends `__singles.parquet`, `__couples.parquet`, and `__mnlmeta.json` to this stem.
All three files now exist at the GSURv2 stem.

---

## 8. Metadata strategy

The GSURv2 sidecar is a **content-identical copy** of the canonical sidecar.

Rationale: the sidecar records prep-step provenance (normalization constants, draws paths, sample
sizes, column inventory). None of these change between canonical and GSURv2 parquets. The GSUR
correction is embedded in the parquet columns at rebuild time; the estimator reads `gsur` directly
from the parquet, not from the sidecar. Copying without modification is correct and sufficient.

If a future pipeline version begins reading `inputs.gsur_file` from the sidecar at estimation
time, the sidecar would need to be updated to reference the Stage A lookup. That is not the case
for the current estimator.

---

## 9. Provenance-only YAML

| Item | Value |
|---|---|
| Source YAML | `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml` |
| Provenance copy | `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` |
| Lines differing | **1 line only** (line 41) |
| Change | `specification.name: "ruro_occ_M0c_b2"` → `"ruro_occ_M0c_b2_GSURv2"` |
| Purpose | Output folder naming: the estimator writes results under a path derived from `specification.name`. The `_GSURv2` suffix ensures GSURv2 results land in a distinct folder from any future v1-GSUR re-run of M0c_b2. |

**This is a provenance label change, not an economic specification change.**

Unchanged between source and provenance copy (verified by line-by-line diff):
- `specification.description`
- `specification.wage_spec`, `specification.model_family`
- All `utility` blocks (consumption, leisure, Box-Cox exponents, shifters)
- All `hours_opportunity`, `wage_opportunity`, `market_opportunity`, `occupation_opportunity` blocks
- All `couples.leisure_interaction` settings
- All `initial_values` (47 parameters)
- All `optimization` settings (method, tolerances, bounds, expression constraints)
- `gradient_verification`

---

## 10. Estimation readiness

| Gate | Status |
|---|---|
| MNL rebuild validation (M1–M10 + M12-diag) | **PASS** (rebuild report §1) |
| GSURv2 singles parquet exists | **YES** |
| GSURv2 couples parquet exists | **YES** |
| GSURv2 metadata sidecar exists | **YES** (created this task) |
| Row counts match rebuild report | **YES** |
| Canonical files untouched | **YES** |
| Economic model YAML unchanged | **YES** |
| Provenance YAML created | **YES** |

**Estimation is ready to run.**

Exact command (schema):

```
<python> scripts/enhanced/enh_RURO_estimate_FR.py \
  --spec scripts/enhanced/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --solver gamspy-conopt --vectorized
```

Do not estimate until explicitly instructed.
Do not run post-estimation.
Do not run welfare computation.
Do not move to M1-clean.
