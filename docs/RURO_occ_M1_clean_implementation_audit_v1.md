# RURO Occupation-Opportunity M1-clean Implementation Audit v1

Date: 2026-05-18  
Auditor: Claude (read-only audit — no code or data files modified)  
Reference design memo: `docs/RURO_occ_M1_clean_design_memo_v2.md`  
Data stem inspected: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`

---

## 1. Audit scope

This document is a read-only implementation audit for M1-clean as defined in the
accepted design memo v2. It does not authorise estimation, code modification, welfare
computation, or parquet promotion.

Sources read during the audit:

| Source | Method |
|--------|--------|
| `docs/RURO_occ_M1_clean_design_memo_v2.md` | Full read |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` | Full read (317 lines) |
| `scripts/enhanced/estimation_spec_parser.py` | Full read |
| `scripts/enhanced/enh_RURO_estimate_FR.py` §5a–5b | Full read |
| `scripts/enhanced/gamspy_estimation_vectorized.py` singles + couples blocks | Full read |
| `scripts/enhanced/estimation_utils.py` precompute dataclasses and functions | Full read |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | Column inspection + smoke test |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | Column inspection + smoke test |

The smoke test called `precompute_data_singles` and `precompute_data_couples` with
empty `include_extra_vars` and verified `reg2`–`reg8` attributes on both returned
data objects. A second smoke test with `include_extra_vars=['reg2', 'reg3']` confirmed
the skip-if-already-present guard.

---

## 2. M1-clean specification summary

M1-clean makes exactly two changes to the M0c_b2_GSURv2 market-opportunity block:

1. **Remove** the `beta_E_educH` entry from `market_opportunity.shifters`.
2. **Add** seven entries, one for each of `beta_E_drgn2` through `beta_E_drgn8`,
   each encoding the regional market-opportunity effect relative to IDF (drgn1 = 1).

All other model blocks — wage opportunity, utility, occupation opportunity, GSUR
shifter, proposal-density correction, solver settings — are preserved unchanged from
M0c_b2_GSURv2.

Parameter count: 47 − 1 + 7 = **53**.

Canonical spec filename (design memo v2 §18): `estimation_spec_ruro_occ_M1_clean.yaml`  
Specification name field: `ruro_occ_M1_clean`

---

## 3. M1-naive versus M1-clean distinction

The design memo v2 defines two variants for reference:

- **M1-clean** (this audit): removes `beta_E_educH`, adds 7 region dummies → 53 parameters.
- **M1-naive** (not audited here): retains `beta_E_educH`, adds 7 region dummies → 54 parameters.

This audit addresses M1-clean only.

---

## 4. Three candidate implementation paths

Design memo v2 §19 defines three paths to supply the seven region indicators:

| Path | Mechanism | Parquet change needed |
|------|-----------|----------------------|
| A | Add `reg_nuts1_2`–`reg_nuts1_8` to couples parquet | Yes — couples rebuild |
| B | Use `reg2`–`reg8` already built at precompute from `drgn1` | No |
| C | Add `drgn2`–`drgn8` binary columns to both parquets | Yes — both parquets rebuild |

**Audit decision: Path B is operative. No parquet rebuild is required.**  
The precompute layer already constructs `reg2`–`reg8` on both data objects for every
load. The attributes are verified present and correctly populated (§7 below). Paths A
and C are redundant given Path B.

---

## 5. Singles parquet: region-relevant physical columns

Parquet: `fr_2016_RURO_mnl_GSURv2__singles.parquet` (81 columns)

Region-relevant columns confirmed present:

```
drgn1            integer, values 1–8
reg_nuts1_1      binary dummy, region 1 (IDF, reference)
reg_nuts1_2      binary dummy, region 2
reg_nuts1_3      binary dummy, region 3
reg_nuts1_4      binary dummy, region 4
reg_nuts1_5      binary dummy, region 5
reg_nuts1_6      binary dummy, region 6
reg_nuts1_7      binary dummy, region 7
reg_nuts1_8      binary dummy, region 8
```

All nine region-related columns are present. The precompute function takes the
`if "reg_nuts1_2" in df.columns` branch and reads the pre-built indicator columns
directly.

---

## 6. Couples parquet: region-relevant physical columns

Parquet: `fr_2016_RURO_mnl_GSURv2__couples.parquet` (105 columns)

Region-relevant columns:

```
drgn1    integer, values 1–8
```

`reg_nuts1_2`–`reg_nuts1_8` are absent. The precompute function takes the
`elif "drgn1" in df.columns` fallback branch and derives all seven indicators via
`(drgn1 == k).astype(float)`. Cross-check confirmed: `c_pre.reg2 == (drgn1 == 2)`
for all rows.

---

## 7. Precompute smoke test: reg2–reg8 availability

Both parquets were loaded and passed to `precompute_data_singles` /
`precompute_data_couples`. Observed sums for each attribute:

| Attribute | Singles sum | Couples sum | Non-zero |
|-----------|------------|------------|---------|
| `reg2`    | 26 900     | 44 600     | Yes |
| `reg3`    | 12 600     | 19 100     | Yes |
| `reg4`    | 14 500     | 22 700     | Yes |
| `reg5`    | 29 700     | 48 400     | Yes |
| `reg6`    | 19 000     | 29 200     | Yes |
| `reg7`    | 19 700     | 30 500     | Yes |
| `reg8`    | 18 100     | 24 900     | Yes |

All attributes non-zero, correctly populated. The zero-fallback branch
(`else: reg2 = ... = reg8 = np.zeros(n_obs)`) is not triggered.

Singles: 27 100 observations in reference region (IDF); 140 500 in regions 2–8.  
Couples: 38 300 observations in reference region (IDF); 219 400 in regions 2–8.

---

## 8. Precompute derivation logic (estimation_utils.py)

For both singles and couples the region-dummy block reads:

```python
if "reg_nuts1_2" in df.columns:          # singles: uses parquet columns
    reg2 = df["reg_nuts1_2"].fillna(0.0).values
    ...
elif "drgn1" in df.columns:              # couples: derived from drgn1
    reg2 = (drgn1 == 2).astype(float)
    ...
else:
    reg2 = ... = reg8 = np.zeros(n_obs)  # not triggered
```

The result is stored on the dataclass as `reg2`–`reg8` declared fields on
`PrecomputedDataSingles` (lines 409–418) and `PrecomputedDataCouples`
(lines 503–510).

---

## 9. extra_precompute_vars interaction for reg2–reg8

`enh_RURO_estimate_FR.py` §5a adds each `variable` name from
`spec.market_opportunity_shifters` to `extra_precompute_vars_set`. For
`variable: "reg2"` this adds `"reg2"` to the set, which is then passed to
`precompute_data_singles` and `precompute_data_couples`.

Inside both precompute functions, the extra-vars path contains:

```python
if getattr(result, var_name, None) is not None:
    continue   # already built — skip
```

Because `reg2`–`reg8` are declared dataclass fields already populated by the
region-dummy block, the extra-vars path is a no-op for these variables.
Smoke test with `include_extra_vars=['reg2', 'reg3']` returned identical sums,
confirming the skip-if-already-present guard.

---

## 10. Section 5b validation (enh_RURO_estimate_FR.py)

§5b validates that every variable referenced in `spec.market_opportunity_shifters`
is accessible on the data objects. For singles it calls `hasattr(data_obj, vn)`.
For couples it checks `hasattr(data_cou, f"{vn}_{gender}")` with a household
fallback when `applies_to == "household"`.

For `variable: "reg2"` with `applies_to: "household"`, the validation uses the
base attribute name `"reg2"` directly against the couples data object, which has
`reg2` built from `drgn1`. Validation will pass without code changes.

---

## 11. Singles likelihood: variable resolution

`gamspy_estimation_vectorized.py` singles `get_var_param`:

```python
def get_var_param(var_name: str) -> Optional[Parameter]:
    if var_name in var_cache:
        return var_cache[var_name]
    if not hasattr(data, var_name):
        return None
    arr = getattr(data, var_name)
    ...
```

For `variable: "reg2"`: `hasattr(data, "reg2")` → True for all singles loads.
No code change needed.

---

## 12. Couples likelihood: variable resolution and applies_to requirement

`gamspy_estimation_vectorized.py` couples `get_var_param` with `gender` and
`fallback_to_base=False`:

```python
attr_candidate = f"{base_name}_{gender}"   # e.g. "reg2_male"
if hasattr(data, attr_candidate):
    attr = attr_candidate
elif fallback_to_base:
    attr = base_name
else:
    return None                             # silent dropout
```

With the default `applies_to: "both"`, the couples likelihood looks for
`reg2_male` and `reg2_female`. Neither exists on `PrecomputedDataCouples`; both
calls return `None` and the region dummy is **silently omitted from couples**.

With `applies_to: "household"`, the couples likelihood calls `get_var_param("reg2")`
with no gender argument → `attr = "reg2"` → `hasattr(data, "reg2")` → True.
The region effect is applied to `working_m + working_f` (the count of partners in
work: 0, 1, or 2 — not a binary indicator). No code change needed provided the
YAML field is set correctly.

**`applies_to: "household"` is mandatory on all seven region-dummy shifter entries.**
Omitting it causes silent dropout from the couples likelihood with no error or warning.

---

## 13. YAML shifters block for M1-clean

Complete replacement block for `market_opportunity.shifters`:

```yaml
shifters:
  - variable: "gsur"
    coefficient: "beta_E_gsur"
    interaction: ["working"]
  - variable: "reg2"
    coefficient: "beta_E_drgn2"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg3"
    coefficient: "beta_E_drgn3"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg4"
    coefficient: "beta_E_drgn4"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg5"
    coefficient: "beta_E_drgn5"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg6"
    coefficient: "beta_E_drgn6"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg7"
    coefficient: "beta_E_drgn7"
    interaction: ["working"]
    applies_to: "household"
  - variable: "reg8"
    coefficient: "beta_E_drgn8"
    interaction: ["working"]
    applies_to: "household"
```

The `beta_E_educH` entry is removed. The `beta_E_gsur` entry is unchanged.
No other market-opportunity field changes (`offer_only_vars`, `center_within_choice_set`,
`center_weights`, `variable_scales`).

---

## 14. Initial values and bounds for new parameters

The design memo v2 §18 specifies that the seven new entries carry `initial_value: 0.0`
and bounds `[-10.0, 10.0]`, consistent with the existing market-opportunity
parameter conventions. The `beta_E_educH` entry (previously `initial_value: 0.0`,
bounds `[-10.0, 10.0]`) is removed.

---

## 15. Spec file naming

Design memo v2 §18 specifies:

- Filename: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
- `specification.name`: `ruro_occ_M1_clean`

These names do not carry a `_GSURv2` provenance suffix. The M0c_b2_GSURv2 YAML is
retained without modification as the provenance baseline. Any future run outputs for
M1-clean will be stored under `outputs/.../spec/ruro_occ_M1_clean/`.

---

## 16. YAML fields actually present in the source spec

The source YAML (`estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`) does **not** contain
a `specification.version` field or a `parameters.market_opportunity` section.
The parameter list is fully inferred by the parser from the `initial_values`,
`bounds`, and `shifters` blocks. No such fields need to be added to or removed from
the M1-clean YAML.

Fields to update in the M1-clean YAML relative to the source:

| Field | Action |
|-------|--------|
| `specification.name` | Change to `ruro_occ_M1_clean` |
| `specification.description` | Update to describe M1-clean |
| `market_opportunity.shifters` | Replace per §13 |
| `initial_values` | Remove `beta_E_educH`; add `beta_E_drgn2`–`beta_E_drgn8` at 0.0 |
| `bounds` | Remove `beta_E_educH`; add `beta_E_drgn2`–`beta_E_drgn8` at [−10, 10] |

All other YAML fields are copied unchanged.

---

## 17. Parser changes required

**None.**

`estimation_spec_parser.py` builds `market_opportunity_shifters` from
`market_config.get("shifters", [])` generically. Each entry's `variable`,
`coefficient`, `interaction`, and `applies_to` fields pass through to the shifter
struct without special-casing any variable name or coefficient name.
`_build_parameter_list` adds each `coefficient` to the parameter list by name.

The new coefficient names `beta_E_drgn2`–`beta_E_drgn8` require no parser change.

---

## 18. Estimator changes required

**None.**

`enh_RURO_estimate_FR.py` §5a extracts extra-precompute variables generically.
§5b validates data attributes generically. Both handle arbitrary variable and
coefficient names from the YAML without code changes.

---

## 19. Vectorized likelihood changes required

**None.**

Singles: direct `hasattr` / `getattr` lookup works for `"reg2"`–`"reg8"`.

Couples: `applies_to: "household"` routing already implemented (lines 967–995 of
`gamspy_estimation_vectorized.py`). No new code path is needed.

---

## 20. Post-estimation changes required

**The standard post-estimation script (`RURO_post_estimation_styled.py`) requires no
modification** to produce the standard diagnostics for M1-clean. It operates on the
parameter vector, standard errors, Hessian, and precomputed data objects generically;
the new coefficient names appear in the output automatically.

**However, three M1-specific diagnostics required by design memo v2 §21 are not
produced by the current script:**

1. **Joint Wald test** for `beta_E_drgn2 = ... = beta_E_drgn8 = 0` (chi-squared,
   df = 7, p-value).
2. **Region covariance sub-block**: the 7×7 variance-covariance sub-matrix for the
   region coefficients plus the derived correlation matrix; flag correlations > 0.9.
3. **Region-conditional GSUR identification sub-matrix**: eigenvalues of the Hessian
   restricted to `(beta_E_gsur, beta_E_drgn2, ..., beta_E_drgn8)`.

These diagnostics require a separate implementation step. Two acceptable options:

- **Option A (recommended)**: Implement as a supplementary M1 diagnostic script,
  e.g. `scripts/enhanced/RURO_post_estimation_M1_diagnostics.py`, called after the
  standard post-estimation run and writing to
  `Results/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md` per §21 of the memo.
- **Option B**: Extend `RURO_post_estimation_styled.py` with a region-group
  diagnostic block triggered by the presence of `beta_E_drgn*` in the parameter list.

Either option requires implementation before the M1-clean post-estimation step.
This is a **new implementation requirement not covered by the YAML-only change**.

---

## 21. offer_only_vars and variable_scales

`offer_only_vars: ["gsur"]` — unchanged. Region dummies are individual/household
characteristics, not job-offer characteristics.

`variable_scales: {gsur: 10.0}` — unchanged. No scaling needed for binary 0/1 region
indicators.

---

## 22. Files to create and files to modify

**Files to create (1):**

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml
```

Derived from `estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` with changes in §16.

**Supplementary diagnostic implementation (1 new file, pre-estimation not required):**

```
scripts/enhanced/RURO_post_estimation_M1_diagnostics.py   (or equivalent)
```

Required before post-estimation, not before estimation itself.

**Files to modify (0):** No existing source files require modification.

**Files unchanged:** Both GSURv2 parquets, `estimation_spec_parser.py`,
`enh_RURO_estimate_FR.py`, `gamspy_estimation_vectorized.py`,
`estimation_utils.py`, `RURO_post_estimation_styled.py`.

---

## 23. Summary: required work before estimation can proceed

| Item | Required | Notes |
|------|----------|-------|
| Create `estimation_spec_ruro_occ_M1_clean.yaml` | Yes | YAML-only change; see §13, §14, §16 |
| `applies_to: "household"` on all 7 region shifters | Yes | Mandatory; silent dropout otherwise |
| Parquet rebuild (singles or couples) | No | Path B is operative |
| Parser changes | No | Generic handling already correct |
| Estimator changes | No | Generic extra-vars and validation |
| Likelihood changes | No | `applies_to: "household"` path exists |
| Standard post-estimation changes | No | Runs correctly for standard output |
| M1-specific diagnostic implementation | **Pre-post-estimation** | Wald test, region covariance, sub-Hessian |

---

## 24. Feasibility verdict

**M1-clean is fully implementable as a YAML-only change for the estimation step.**

No parquet rebuild is required. No code changes are required in the parser, estimator,
likelihood, or post-estimation script to produce the standard diagnostics.

The sole mandatory pre-estimation action is authoring
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml` with the
`market_opportunity.shifters` block in §13 and `applies_to: "household"` on all seven
region-dummy entries.

An additional implementation step — the M1-specific supplementary diagnostics (§20) —
is required before post-estimation can satisfy the design memo v2 §21 requirements. This
step does not block estimation itself.
