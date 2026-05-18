# RURO Occupation-Opportunity M1-clean Implementation Audit v1

Date: 2026-05-18  
Auditor: Claude (implementation audit only — no code edits made)  
Reference design memo: `docs/RURO_occ_M1_clean_design_memo_v2.md`  
Data stem: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`

---

## 1. Audit scope and method

This audit covers the feasibility of implementing M1-clean as defined in the accepted
design memo v2. It is read-only: no code, YAML, or data files were modified.

Sources inspected:

| Source | How inspected |
|--------|--------------|
| `docs/RURO_occ_M1_clean_design_memo_v2.md` | Full read |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` | Full read (317 lines) |
| `scripts/enhanced/estimation_spec_parser.py` | Full read |
| `scripts/enhanced/enh_RURO_estimate_FR.py` (§5a–5b) | Full read |
| `scripts/enhanced/gamspy_estimation_vectorized.py` (singles + couples likelihood) | Full read |
| `scripts/enhanced/estimation_utils.py` (precompute dataclasses + functions) | Full read |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | Column inspection + precompute smoke test |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | Column inspection + precompute smoke test |

The parquet smoke test called `precompute_data_singles` and `precompute_data_couples`
with empty `include_extra_vars`, then verified `reg2`–`reg8` attributes on the
returned data objects.

---

## 2. M1-clean specification recap

M1-clean makes exactly two changes to the M0c_b2_GSURv2 market-opportunity block:

1. **Remove** `beta_E_educH` (education effect on market opportunity).
2. **Add** `beta_E_drgn{k}` for k = 2, 3, 4, 5, 6, 7, 8 — seven region dummies
   entering the market-opportunity utility, with IDF (drgn1 = 1) as reference category.

All other model blocks (wage opportunity, utility, occupation opportunity, GSUR shifter,
proposal-density correction, solver settings) remain identical to M0c_b2_GSURv2.

Expected parameter count: 47 − 1 (educH) + 7 (drgn2–8) = **53**.

---

## 3. Three candidate implementation paths (§19 of design memo)

The design memo v2 §19 identified three paths to provide the region-dummy variables
to the likelihood:

| Path | Column source | Action required |
|------|--------------|----------------|
| A | Add `reg_nuts1_2`–`reg_nuts1_8` to couples parquet | Couples parquet rebuild |
| B | Use precomputed `reg2`–`reg8` attributes that `estimation_utils` already builds | YAML-only change |
| C | Add explicit `drgn{k}` binary columns to both parquets | Both parquets rebuild |

The audit decision is stated in §4 below.

---

## 4. Path decision: Path B is operative — no parquet rebuild required

**Path B is the correct and fully operative path.**

The precompute layer (`estimation_utils.py`) already builds `reg2`–`reg8` as explicit
attributes on both `PrecomputedDataSingles` and `PrecomputedDataCouples` for every
data load, regardless of which parquet columns are present. Both data objects expose
`reg2`–`reg8` as direct attributes accessible to the likelihood via `hasattr` /
`getattr`. No parquet modification is needed.

Path A and Path C are both redundant given Path B. They would require parquet rebuilds
for no benefit.

---

## 5. Singles parquet: physical columns present

GSURv2 singles parquet (`fr_2016_RURO_mnl_GSURv2__singles.parquet`, 81 columns):

**Region-relevant columns present:**

```
drgn1            (integer, values 1–8)
reg_nuts1_1      (binary dummy, region 1 = IDF reference)
reg_nuts1_2      (binary dummy, region 2)
reg_nuts1_3      (binary dummy, region 3)
reg_nuts1_4      (binary dummy, region 4)
reg_nuts1_5      (binary dummy, region 5)
reg_nuts1_6      (binary dummy, region 6)
reg_nuts1_7      (binary dummy, region 7)
reg_nuts1_8      (binary dummy, region 8)
```

All eight NUTS-1 dummy columns are present. The precompute function takes the
`if "reg_nuts1_2" in df.columns` branch and reads these pre-built columns directly.

---

## 6. Couples parquet: physical columns present

GSURv2 couples parquet (`fr_2016_RURO_mnl_GSURv2__couples.parquet`, 105 columns):

**Region-relevant columns present:**

```
drgn1    (integer, values 1–8)
```

`reg_nuts1_2`–`reg_nuts1_8` are **absent** from the couples parquet. The precompute
function takes the `elif "drgn1" in df.columns` fallback branch and derives all seven
dummies via `(drgn1 == k).astype(float)` comparisons.

Smoke-test cross-check confirmed: `c_pre.reg2 == (drgn1 == 2)` for all rows.

---

## 7. Precompute: reg2–reg8 derivation logic

`estimation_utils.py` region-dummy construction (same pattern for singles and couples):

```python
if "reg_nuts1_2" in df.columns:
    reg2 = df["reg_nuts1_2"].fillna(0.0).values   # singles: uses parquet columns
    ...
elif "drgn1" in df.columns:
    reg2 = (drgn1 == 2).astype(float)              # couples: derived on the fly
    ...
else:
    reg2 = ... = reg8 = np.zeros(n_obs)             # fallback (not triggered here)
```

The resulting arrays are stored on the dataclass as `reg2` through `reg8` fields
(explicitly declared in `PrecomputedDataSingles` and `PrecomputedDataCouples`).

**Smoke test results (precompute with empty extra_vars):**

| Attribute | Singles sum | Couples sum |
|-----------|------------|------------|
| `reg2`    | 26 900     | 44 600     |
| `reg3`    | 12 600     | 19 100     |
| `reg4`    | 14 500     | 22 700     |
| `reg5`    | 29 700     | 48 400     |
| `reg6`    | 19 000     | 29 200     |
| `reg7`    | 19 700     | 30 500     |
| `reg8`    | 18 100     | 24 900     |

All non-zero, all correctly populated.

---

## 8. Region coverage and reference category

Both parquets carry drgn1 values 1–8.

- **Reference region (IDF, drgn1 = 1)**: implicitly captured by the intercept; all seven
  dummies are zero for IDF observations.
- Singles: 27 100 observations in reference region (IDF); 140 500 in regions 2–8.
- Couples: 38 300 observations in reference region (IDF); 219 400 in regions 2–8.
- Total coverage: every observation is assigned to exactly one of the eight regions.

---

## 9. extra_precompute_vars: no action required for reg2–reg8

`enh_RURO_estimate_FR.py` §5a builds `extra_precompute_vars_set` by walking
`spec.market_opportunity_shifters`. When `variable: "reg2"` appears in the YAML shifter,
`"reg2"` is added to this set and passed to `precompute_data_singles` /
`precompute_data_couples`.

Inside the precompute functions, the extra-vars path contains:

```python
if getattr(result, var_name, None) is not None:
    continue   # already built — skip
```

Because `reg2`–`reg8` are declared fields and already populated by the region-dummy
block, the extra-vars path is a no-op for these variables. No duplication, no override.

Smoke-test with `include_extra_vars=['reg2', 'reg3']` returned identical values
(`reg2` sum = 26 900), confirming the skip-if-already-present guard works correctly.

---

## 10. Singles likelihood: variable lookup mechanism

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

For `variable: "reg2"` in a YAML shifter: `hasattr(data, "reg2")` → True (always,
for singles). The parameter is built from the array and cached. No code change needed.

---

## 11. Couples likelihood: variable lookup and applies_to requirement

`gamspy_estimation_vectorized.py` couples `get_var_param` with `gender` argument
and `fallback_to_base=False`:

```python
attr_candidate = f"{base_name}_{gender}"   # e.g. "reg2_male"
if hasattr(data, attr_candidate):
    attr = attr_candidate
elif fallback_to_base:
    attr = base_name
else:
    return None                             # ← silently returns None
```

With the default `applies_to: "both"`, the couples likelihood looks for
`reg2_male` and `reg2_female`. Neither exists on `PrecomputedDataCouples`. With
`fallback_to_base=False`, both calls return `None` and the region dummy is silently
omitted from couples.

**Required YAML field:** Every region-dummy shifter entry must carry `applies_to: "household"`.

With `applies_to: "household"`, the couples likelihood calls `get_var_param("reg2")`
with no gender argument → `attr = "reg2"` → `hasattr(data, "reg2")` → True → correct.
The interaction is applied as `working_m + working_f` (the household working indicator).

---

## 12. YAML market_opportunity.shifters block for M1-clean

The complete replacement block for `market_opportunity.shifters` in the new spec YAML:

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

Changes from M0c_b2_GSURv2:
- `beta_E_educH` entry removed.
- Seven `beta_E_drgn{k}` entries added, each with `applies_to: "household"`.
- `beta_E_gsur` entry is unchanged.

No changes to `offer_only_vars`, `center_within_choice_set`, `center_weights`,
`variable_scales`, or any other market-opportunity field.

---

## 13. Parameter list: additions and removals

Starting from M0c_b2_GSURv2 (47 parameters):

| Action | Parameter | Count delta |
|--------|-----------|------------|
| Remove | `beta_E_educH` | −1 |
| Add    | `beta_E_drgn2` | +1 |
| Add    | `beta_E_drgn3` | +1 |
| Add    | `beta_E_drgn4` | +1 |
| Add    | `beta_E_drgn5` | +1 |
| Add    | `beta_E_drgn6` | +1 |
| Add    | `beta_E_drgn7` | +1 |
| Add    | `beta_E_drgn8` | +1 |

Net: +6. M1-clean total: **53 parameters**.

---

## 14. Specification metadata fields to update

In addition to the `shifters` block, the following YAML fields must be updated in the
new `estimation_spec_ruro_occ_M1_clean_GSURv2.yaml`:

| Field | Old value | New value |
|-------|-----------|-----------|
| `specification.name` | `ruro_occ_M0c_b2_GSURv2` | `ruro_occ_M1_clean_GSURv2` |
| `specification.description` | (M0c_b2 description) | M1-clean description |
| `specification.version` | (M0c_b2 version) | M1 version |
| `parameters.market_opportunity` | lists `beta_E_educH` + `beta_E_gsur` | lists `beta_E_gsur` + `beta_E_drgn2`–`beta_E_drgn8` |

The `parameters.market_opportunity` section lists parameter names for the solver's
variable declarations. It must match the `shifters` coefficients exactly.

---

## 15. Parser changes required

**None.**

`estimation_spec_parser.py` processes `market_opportunity.shifters` generically:
- `market_opportunity_shifters` is built directly from `market_config.get("shifters", [])`.
- Each entry's `variable`, `coefficient`, `interaction`, and `applies_to` fields are
  passed through without special-casing any variable name.
- `_build_parameter_list` adds each `coefficient` to the parameter list by name.
- `applies_to` is propagated to the shifter struct used by the likelihood.

No parser modification is needed.

---

## 16. Estimator (enh_RURO_estimate_FR.py) changes required

**None.**

§5a extra-vars extraction walks `spec.market_opportunity_shifters` generically.
`"reg2"`–`"reg8"` will be added to `extra_precompute_vars_set` and passed to
precompute — where they are silently skipped (already built). This is correct behaviour.

§5b validation calls `hasattr(data_obj, vn)` for singles and
`hasattr(data_cou, f"{vn}_{gender}")` for couples (with household fallback). For
`applies_to: "household"` shifters the validation path uses the base attribute name
directly, which resolves to `data_cou.reg2` — present. Validation will pass.

No estimator modification is needed.

---

## 17. Vectorized likelihood (gamspy_estimation_vectorized.py) changes required

**None.**

Singles: `get_var_param("reg2")` resolves via `hasattr(data, "reg2")` — already works.

Couples: `get_var_param` with `applies_to: "household"` calls the base-name path
(no gender argument) → resolves `data.reg2` → already works.

The `applies_to: "household"` routing is already implemented in the couples likelihood
(lines 967–995 of the current file). No new code path is needed.

No likelihood modification is needed.

---

## 18. Post-estimation (RURO_post_estimation_styled.py) changes required

**None.**

Post-estimation does not reference individual `market_opportunity_shifters` variable
names directly. It operates on the parameter vector, standard errors, and precomputed
data objects — all of which will be correctly populated by the new YAML.

The region-dummy coefficients (`beta_E_drgn2`–`beta_E_drgn8`) will appear in the
parameter table and LLM summary automatically.

No post-estimation modification is needed.

---

## 19. Conceptual indicators required vs. physical columns vs. derived attributes

| Layer | Region dummies | Status |
|-------|---------------|--------|
| **Conceptual** | `beta_E_drgn{k}` × I(region k) × working | Defined in design memo v2 |
| **Singles parquet columns** | `reg_nuts1_2`–`reg_nuts1_8` present | Confirmed (81-col parquet) |
| **Couples parquet columns** | `reg_nuts1_*` absent; `drgn1` present | Confirmed (105-col parquet) |
| **Precomputed data attributes** | `reg2`–`reg8` on both Singles and Couples | Confirmed by smoke test |
| **YAML variable names** | `"reg2"` through `"reg8"` | Must match precomputed attribute names |
| **couples `applies_to`** | Must be `"household"` (not `"both"`) | Required YAML change |

---

## 20. M1-naive vs M1-clean distinction (audit confirmation)

Design memo v2 defines two variants:

- **M1-clean** (this audit): removes `beta_E_educH`, adds 7 region dummies → 53 params.
- **M1-naive** (not this audit): retains `beta_E_educH`, adds 7 region dummies → 54 params.

This audit addresses M1-clean only. The YAML for M1-naive would differ only in retaining
the `educH` shifter entry and the `beta_E_educH` parameter declaration.

---

## 21. Interaction term: working

All seven region-dummy shifters use `interaction: ["working"]`, consistent with the
GSUR and educH shifters in M0c_b2_GSURv2. This means the region effect enters as:

```
beta_E_drgn{k} × I(drgn1 = k) × working
```

For couples with `applies_to: "household"`, `working` resolves to `working_m + working_f`
(the household sum of employment indicators), consistent with all other household-level
market-opportunity shifters.

---

## 22. offer_only_vars and variable_scales

`offer_only_vars: ["gsur"]` — unchanged. Region dummies are not offer-only variables
(they are individual/household characteristics, not job-offer characteristics).

`variable_scales: {gsur: 10.0}` — unchanged. No scaling entry is needed for region
dummies (they are 0/1 binary indicators).

---

## 23. Files to create and files to modify

**Files to create (1):**

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean_GSURv2.yaml
```

This is a copy of `estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` with:
- `specification.name`, description, version updated to M1-clean.
- `market_opportunity.shifters` replaced per §12 above.
- `parameters.market_opportunity` updated to list `beta_E_gsur` + `beta_E_drgn2`–`beta_E_drgn8`
  (remove `beta_E_educH`).

**Files to modify (0):** No existing source files require modification.

**Files unchanged:** Both GSURv2 parquets, all scripts, the parser, the estimator,
the likelihood, and the post-estimation script.

---

## 24. Verdict: implementation feasibility and recommended path

**M1-clean is fully implementable via a YAML-only change (Path B).**

Summary:

| Item | Decision |
|------|----------|
| Path A (add reg_nuts1_* to couples parquet) | Not required |
| Path B (use existing reg2–reg8 precomputed attributes) | **Operative — recommended** |
| Path C (add drgn{k} binary columns to both parquets) | Not required |
| Code changes to parser | None |
| Code changes to estimator | None |
| Code changes to likelihood | None |
| Code changes to post-estimation | None |
| Parquet rebuilds | None |
| YAML change | New spec file: 8 shifter entries replacing 2 |
| Critical YAML field | `applies_to: "household"` on all 7 region dummies |
| Expected parameter count | 53 |
| Expected spec file | `estimation_spec_ruro_occ_M1_clean_GSURv2.yaml` |

The only substantive implementation work is authoring the new YAML specification file.
The `applies_to: "household"` field on all seven region-dummy shifters is mandatory:
omitting it causes silent dropout of region dummies from the couples likelihood.