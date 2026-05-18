# RURO occ M1-naive — YAML Implementation Report v1

Date: 2026-05-18  
Author: research pipeline  
Status: YAML implementation only — no estimation, no post-estimation, no welfare

---

## 1. Source YAML

`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`

M1-clean is the source. M1-naive is derived from M1-clean by re-adding
`beta_E_educH` to the market-opportunity block, with all other content
byte-identical to M1-clean. M1-clean was itself derived from
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
(the `beta_E_educH` entry is copied from there).

---

## 2. New YAML

`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml`

---

## 3. Exact fields changed relative to M1-clean

Four fields were modified. No other field was touched.

### 3.1 `specification.name`

| Field | M1-clean | M1-naive |
|---|---|---|
| `specification.name` | `"ruro_occ_M1_clean"` | `"ruro_occ_M1_naive"` |

### 3.2 `specification.description`

M1-clean description states the ability/opportunity-clean rationale (dropping
`beta_E_educH`, adding seven region dummies). M1-naive description is updated
to state that this is the naive robustness specification that retains
`beta_E_educH` in the market-opportunity block alongside the region dummies,
and that it is not the preferred specification.

### 3.3 `market_opportunity.shifters`

One entry added immediately after the `beta_E_gsur` shifter and before the
first region dummy (`beta_E_drgn2`), exactly as it appears in M0c_b2_GSURv2:

```yaml
    - variable: "educH"
      coefficient: "beta_E_educH"
      interaction: ["working"]
```

No `applies_to` field — this is the same form as in M0c_b2_GSURv2 (the entry
applies to both singles and couples, consistent with M0c_b2_GSURv2 behaviour).

The region dummy entries (`beta_E_drgn2` through `beta_E_drgn8`) follow
immediately after, unchanged from M1-clean.

### 3.4 `initial_values`

One entry added in the market-opportunity group, immediately after
`beta_E_gsur` and before `beta_E_drgn2`:

```yaml
  beta_E_educH:  0.0
```

Initial value `0.0` is identical to M0c_b2_GSURv2.

### 3.5 `optimization.bounds`

One entry added in the market-opportunity group, immediately after
`beta_E_gsur` and before `beta_E_drgn2`:

```yaml
    beta_E_educH:  [-10.0, 10.0]
```

Bounds `[-10.0, 10.0]` are identical to M0c_b2_GSURv2.

---

## 4. Exact parameter added

| Parameter | YAML field | Value |
|---|---|---|
| `beta_E_educH` | `market_opportunity.shifters` | variable `educH`, interaction `["working"]` |
| `beta_E_educH` | `initial_values` | `0.0` |
| `beta_E_educH` | `optimization.bounds` | `[-10.0, 10.0]` |

The `beta_E_educH` entry is copied verbatim from
`estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`. The M0c_b2_GSURv2 estimated
value was `+0.4386` (SE 0.2257, t = 1.943, p = 0.052). The initial value `0.0`
is neutral; a warm-start prompt may supply the M0c_b2_GSURv2 or M1-clean
parameter vector as the starting point, with `beta_E_educH` initialised at the
M0c_b2_GSURv2 estimate or at zero.

---

## 5. Expected parameter count

| Specification | Source count | Change | Expected count |
|---|---|---|---|
| M0c_b2_GSURv2 | 47 | — | 47 |
| M1-clean | 47 − 1 + 7 | −`beta_E_educH`, +7 region | 53 |
| M1-naive | 53 + 1 | +`beta_E_educH` | **54** |

The parser must report 54 free parameters for M1-naive. Any other count
is a flag requiring investigation before the estimation run is accepted.

---

## 6. M1-naive differs from M1-clean only by adding beta_E_educH

**Confirmed.** The diff between `estimation_spec_ruro_occ_M1_naive.yaml` and
`estimation_spec_ruro_occ_M1_clean.yaml` contains exactly five changes:

1. `specification.name`: `"ruro_occ_M1_clean"` → `"ruro_occ_M1_naive"`
2. `specification.description`: updated to reflect robustness purpose
3. `market_opportunity.shifters`: one entry added (`beta_E_educH`)
4. `initial_values`: one entry added (`beta_E_educH: 0.0`)
5. `optimization.bounds`: one entry added (`beta_E_educH: [-10.0, 10.0]`)

No other field differs. The market-opportunity block of M1-naive contains
nine shifters: `beta_E_gsur`, `beta_E_educH`, and `beta_E_drgn2` through
`beta_E_drgn8`. M1-clean contains eight shifters: `beta_E_gsur` and
`beta_E_drgn2` through `beta_E_drgn8`.

---

## 7. Utility block — unchanged

**Confirmed unchanged from M1-clean.**

The utility block (`utility.functional_form`, all `consumption` fields,
all `leisure` fields including intercept, Box-Cox exponent, and three
shifters) is byte-identical to M1-clean. No parameter is added or removed.
The `couples.leisure_interaction` (`beta_ll`) is also unchanged.

---

## 8. Wage opportunity — unchanged

**Confirmed unchanged from M1-clean.**

The `wage_opportunity` block is byte-identical to M1-clean. It contains:
`beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`,
`sigma`. Education enters the wage block through `beta_w_educH` in both
M1-clean and M1-naive; the M1-naive educational reclassification concerns
only the market-opportunity block. No wage-block parameter is added or
removed.

---

## 9. Occupation opportunity — unchanged

**Confirmed unchanged from M1-clean.**

The `occupation_opportunity` block is byte-identical to M1-clean. It
contains twelve group-specific occupation shifters (`beta_occ_{2,3,4}_{sm,sf,cm,cf}`),
reference category `loc4 = 1`, and `interaction: ["working"]` on each
entry. No occupation parameter is added or removed.

---

## 10. Prior/proposal correction — unchanged

**Confirmed unchanged from M1-clean.**

The `market_opportunity` block configuration fields are byte-identical to
M1-clean:

| Field | Value |
|---|---|
| `applies_to` | `"both"` |
| `employment_indicator` | `"working"` |
| `gsur_variable` | `"gsur"` |
| `offer_only_vars` | `["gsur"]` |
| `center_within_choice_set` | `true` |
| `center_weights` | `"proposal"` |
| `variable_scales.gsur` | `10.0` |

The expression constraints (`mul_cou_m_positive`, `mul_cou_f_positive`),
solver settings (method, tolerances, max iterations), and
`gradient_verification` block are all byte-identical to M1-clean.

---

## 11. MNL files — not modified

**Confirmed. No MNL parquet file was created or modified.**

M1-naive uses the same data contract as M1-clean:
`Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`.
The region dummy variables `reg2`–`reg8` are resolved at precompute time by
`estimation_utils.py` (from `reg_nuts1_*` columns in singles, from `drgn1`
via indicator comparison in couples), as documented in the M1-clean YAML
header and the M1-clean verdict §2. `beta_E_educH` uses `educH`, which is
a pre-existing column in both parquets — it was already in use under
M0c_b2_GSURv2 and remains available in the GSURv2 MNL parquets. No rebuild
step is required.

---

## Summary

| Item | Status |
|---|---|
| Source YAML | `estimation_spec_ruro_occ_M1_clean.yaml` |
| New YAML | `estimation_spec_ruro_occ_M1_naive.yaml` |
| Fields changed | 5 (name, description, 1 shifter entry, 1 initial value, 1 bounds entry) |
| Parameter added | `beta_E_educH` (copied from M0c_b2_GSURv2) |
| Expected parameter count | 54 |
| Differs from M1-clean only by `beta_E_educH` | Yes |
| Utility unchanged | Yes |
| Wage opportunity unchanged | Yes |
| Occupation opportunity unchanged | Yes |
| Prior/proposal correction unchanged | Yes |
| MNL files modified | No |

The M1-naive YAML is ready for the estimation prompt. Estimation, post-estimation
diagnostics, and any welfare work are explicitly not authorised by this
implementation step; they are separately gated per the M1-clean verdict §16.