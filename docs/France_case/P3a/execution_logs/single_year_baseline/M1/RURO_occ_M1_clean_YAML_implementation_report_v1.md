# RURO occ M1-clean YAML Implementation Report v1

Date: 2026-05-18  
Author: Claude (YAML creation only — no estimation, post-estimation, or welfare computation)

---

## 1. Source YAML

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml
```

317 lines. Parser-verified parameter count: **47**.

---

## 2. New YAML

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml
```

Parser-verified parameter count: **53**.

---

## 3. Exact fields changed

Five semantic fields differ between the source and the new YAML — these are the
only changes that affect the model, parser, or estimation behaviour. The literal
file diff is wider: the top comment block was rewritten, inline comments on
`beta_l0_m` and `beta_ll` were removed (the boundary-relaxation rationale
belongs to M0c_b2 provenance, not M1-clean), and a trailing-newline difference
exists. None of those comment changes alter any YAML key, value, or economic
content.

| Field | Source (M0c_b2_GSURv2) | New (M1-clean) |
|-------|------------------------|----------------|
| `specification.name` | `"ruro_occ_M0c_b2_GSURv2"` | `"ruro_occ_M1_clean"` |
| `specification.description` | M0c_b2 boundary-relaxation description | M1-clean ability/opportunity-clean description (see below) |
| `market_opportunity.shifters` | 2 entries: `beta_E_gsur`, `beta_E_educH` | 8 entries: `beta_E_gsur`, `beta_E_drgn2`–`beta_E_drgn8` |
| `initial_values` | contains `beta_E_educH: 0.0` | `beta_E_educH` removed; `beta_E_drgn2`–`beta_E_drgn8` added at `0.0` |
| `optimization.bounds` | contains `beta_E_educH: [-10.0, 10.0]` | `beta_E_educH` removed; `beta_E_drgn2`–`beta_E_drgn8` added at `[-10.0, 10.0]` |

New description:

> "M1-clean: ability/opportunity-clean specification derived from M0c_b2_GSURv2.
> Removes beta_E_educH (education reclassified as ability, not opportunity) and
> adds seven EUROMOD drgn1 region dummies beta_E_drgn2 through beta_E_drgn8
> (region of residence as a normative circumstance). First specification aligned
> with the JMP welfare partition."

---

## 4. Exact parameters removed

| Parameter | Block | M0c_b2_GSURv2 initial | M0c_b2_GSURv2 bounds | Reason |
|-----------|-------|----------------------|----------------------|--------|
| `beta_E_educH` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | Education reclassified as ability under the JMP welfare partition; must not enter the opportunity-side index. |

---

## 5. Exact parameters added

| Parameter | Block | Initial value | Bounds | Variable | `applies_to` |
|-----------|-------|--------------|--------|----------|-------------|
| `beta_E_drgn2` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg2` | `household` |
| `beta_E_drgn3` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg3` | `household` |
| `beta_E_drgn4` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg4` | `household` |
| `beta_E_drgn5` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg5` | `household` |
| `beta_E_drgn6` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg6` | `household` |
| `beta_E_drgn7` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg7` | `household` |
| `beta_E_drgn8` | `market_opportunity.shifters` | 0.0 | [−10.0, 10.0] | `reg8` | `household` |

Each uses `interaction: ["working"]`, consistent with the GSUR shifter and all
prior market-opportunity entries. `applies_to: "household"` is mandatory: without
it the couples likelihood silently looks for non-existent `reg2_male`/`reg2_female`
attributes and the shifter drops out of the couples log-likelihood with no warning.

The `reg2`–`reg8` variables are built at precompute time by `estimation_utils.py`
for both data groups: singles via `reg_nuts1_2`–`reg_nuts1_8` columns present in the
singles parquet; couples via `(drgn1 == k).astype(float)` comparison since the
couples parquet carries only `drgn1`. IDF (drgn1 = 1) is the reference category.

---

## 6. Expected parameter count

| Specification | Parameters | Computation |
|---------------|-----------|-------------|
| M0c_b2_GSURv2 (source) | 47 | Parser-verified |
| − beta_E_educH | 46 | − 1 |
| + beta_E_drgn2 through beta_E_drgn8 | 53 | + 7 |
| **M1-clean (new)** | **53** | **Parser-verified** |

Parser output (verbatim):

```
Parameter count: 53

Market opportunity (9): ['beta_E', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4',
    'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_gsur']
Wage opportunity   (6): ['beta_w0', 'beta_w_educH', 'beta_w_educL', 'beta_w_pexp',
    'beta_w_pexp2', 'sigma']
Occupation        (12): ['beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_2_sm',
    'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_3_sm',
    'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'beta_occ_4_sm']
Utility + hours   (26): ['beta_c', 'beta_c_sf', 'beta_c_sm', 'beta_h_ft', 'beta_h_pt1',
    'beta_h_pt2', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l0_sm',
    'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age2_sm',
    'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_age_sm',
    'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'theta_c_singles',
    'theta_l_f', 'theta_l_m', 'theta_l_sf', 'theta_l_sm']

M0c_b2_GSURv2 count: 47
Removed: ['beta_E_educH']
Added:   ['beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5',
          'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8']
```

---

## 7. Utility: unchanged

The `utility` block is byte-identical to M0c_b2_GSURv2:

- `functional_form: "box_cox"` — unchanged.
- `consumption.coefficient: "beta_c"`, `box_cox_exponent: "theta_c"`,
  `singles_box_cox_exponent: "theta_c_singles"`,
  `couples_fixed_box_cox_exponent: 0.0` — all unchanged.
- `leisure.intercept: "beta_l0"`, `box_cox_exponent: "theta_l"` — unchanged.
- Leisure shifters `beta_l_age`, `beta_l_age2`, `beta_l_nkids` — unchanged.
- `couples.leisure_interaction.coefficient: "beta_ll"` — unchanged.

Parameters `theta_c_singles`, `theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f`,
`beta_c`, `beta_c_sm`, `beta_c_sf`, `beta_l0_sm`, `beta_l0_sf`, `beta_l0_m`,
`beta_l0_f` and all age/children leisure shifters are unchanged in initial values,
bounds, and interpretation.

`theta_c` remains fixed at 0.0 (log-utility for couples) and is not estimated.

---

## 8. Wage opportunity: unchanged

The `wage_opportunity` block is byte-identical to M0c_b2_GSURv2:

- `specification: "log_normal"` — unchanged.
- Mean shifters: `beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`,
  `beta_w_pexp2` — all unchanged in initial values, bounds, and interpretation.
- `sigma: 0.5`, bounds `[0.1, 20.0]` — unchanged.

Note: `beta_w_educH` (wage returns to high education) remains in the wage-opportunity
block. It is a market-price signal and is correctly classified as a wage parameter.
Only `beta_E_educH` (education entering the opportunity-side index) was removed; the
wage block is unaffected.

---

## 9. Occupation opportunity: unchanged

The `occupation_opportunity` block is byte-identical to M0c_b2_GSURv2:

- `variable: "loc4"`, `reference: 1` — unchanged.
- All 12 occupation shifters (`beta_occ_2_sm` through `beta_occ_4_cf`),
  initial values 0.0, bounds [−10.0, 10.0] — unchanged.

---

## 10. Prior/proposal correction: unchanged

The market-opportunity meta-fields governing the proposal-density correction are
byte-identical to M0c_b2_GSURv2:

- `applies_to: "both"` — unchanged (market-opportunity level; individual shifters
  may override with `applies_to: "household"`).
- `employment_indicator: "working"` — unchanged.
- `gsur_variable: "gsur"` — unchanged.
- `offer_only_vars: ["gsur"]` — unchanged.
- `center_within_choice_set: true` — unchanged.
- `center_weights: "proposal"` — unchanged.
- `variable_scales: {gsur: 10.0}` — unchanged.

---

## 11. No MNL files modified

The following files were **not modified** during this implementation:

| File | Status |
|------|--------|
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | Unchanged |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | Unchanged |
| `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | Unchanged |
| `scripts/enhanced/estimation_utils.py` | Unchanged |
| `scripts/enhanced/estimation_spec_parser.py` | Unchanged |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | Unchanged |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Unchanged |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Unchanged |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml` | Unchanged |

The only files created in this implementation step are:

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml
docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_YAML_implementation_report_v1.md
```