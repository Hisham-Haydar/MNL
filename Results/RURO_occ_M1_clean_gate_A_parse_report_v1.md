# RURO occ M1-clean Gate-A Parse Report v1

Date: 2026-05-18  
Spec: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`  
Baseline: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`  
Data stem: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`

---

## Gate-A result: PASS — 18/18 static checks, load smoke test passed with expected benign warnings

---

## 1. Parse/static validation (18 checks)

All 18 checks passed. No failures.

| # | Check | Result |
|---|-------|--------|
| 1 | `param_count == 53` | PASS — got 53 |
| 2 | `beta_E_educH` absent from parameter list | PASS |
| 3 | All of `beta_E_drgn2`–`beta_E_drgn8` present | PASS |
| 4 | `beta_E_gsur` present (preserved unchanged) | PASS |
| 5 | All 7 drgn shifters have `applies_to: "household"` | PASS |
| 6 | drgn variable names: `beta_E_drgn{k}` → `reg{k}` | PASS |
| 7 | All drgn `initial_values` == 0.0 | PASS |
| 8 | All drgn `bounds` == [−10.0, 10.0] | PASS |
| 9 | Utility block unchanged | PASS |
| 10 | `theta_c_couples_fixed == 0.0` | PASS |
| 11 | `beta_ll` coef name unchanged | PASS |
| 12 | Wage block unchanged | PASS |
| 13 | Hours opportunity unchanged | PASS |
| 14 | Occupation opportunity unchanged (12 shifters) | PASS |
| 15 | GSUR meta-fields unchanged (`offer_only_vars`, `center_within_choice_set`, `center_weights`, `variable_scales`) | PASS |
| 16 | Solver settings unchanged | PASS |
| 17 | Expression constraints unchanged (2 constraints) | PASS |
| 18 | `spec.name == "ruro_occ_M1_clean"` | PASS |

---

## 2. Precompute load smoke test

Both parquets loaded and passed to `precompute_data_singles` / `precompute_data_couples`
with `extra_precompute_vars` derived from the M1-clean spec (same logic as
`enh_RURO_estimate_FR.py` §5a).

`extra_precompute_vars` extracted from spec: `['gsur', 'loc4_2', 'loc4_3', 'loc4_4',
'reg2', 'reg3', 'reg4', 'reg5', 'reg6', 'reg7', 'reg8']`

| Attribute | Singles | Couples |
|-----------|---------|---------|
| `reg2` | Available | Available |
| `reg3` | Available | Available |
| `reg4` | Available | Available |
| `reg5` | Available | Available |
| `reg6` | Available | Available |
| `reg7` | Available | Available |
| `reg8` | Available | Available |

All 7 region dummies available on both data objects.

### Warning messages from precompute

`estimation_utils` emitted warnings of the form:

```
WARNING: Extra var 'reg2_male' could NOT be derived from couples data
WARNING: Extra var 'reg2_female' could NOT be derived from couples data
... (same for reg3–reg8)
```

These are **expected and benign**. The generic extra-vars code path in
`precompute_data_couples` attempts to derive `reg{k}_male` and `reg{k}_female`
as an intermediate step, but `reg2`–`reg8` are already declared dataclass fields
populated by the region-dummy block (from `drgn1`) and are available directly.
The skip-if-already-present guard (`if getattr(result, var_name, None) is not None: continue`)
ensures the final attributes are correct. These warnings do not indicate a data
deficiency and do not affect estimation behaviour.

`gsur` and `working` "not found" on couples via the extra-vars route are similarly
expected: both are already-declared couples attributes populated through separate
code paths.

The smoke test **passed**. The warnings are a known diagnostic artefact of the
generic extra-vars logic and are not suppressible without altering the precompute
implementation. They do not signal silent dropout for M1-clean, provided all seven
region shifters carry `applies_to: "household"` in the YAML (verified by check 5).

---

## 3. MNL file modification check

Parquet modification times confirm no MNL files were altered during this
implementation step:

| File | Last modified |
|------|--------------|
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | 2026-05-17 22:05:57 |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | 2026-05-17 22:05:59 |
| `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | 2026-05-13 10:38:22 |

None of these timestamps postdate the start of this session. No MNL files modified.

---

## 4. Files created in this implementation step

```
scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml
docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_YAML_implementation_report_v1.md
docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_implementation_audit_v1.md
Results/RURO_occ_M1_clean_gate_A_parse_report_v1.md
```

Files unmodified: both GSURv2 parquets, `estimation_spec_parser.py`,
`enh_RURO_estimate_FR.py`, `gamspy_estimation_vectorized.py`,
`estimation_utils.py`, `RURO_post_estimation_styled.py`,
`estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`.

---

## 5. Gate-A verdict

**PASS.** The M1-clean YAML is structurally correct, parses to exactly 53 parameters,
preserves all frozen blocks, and the precompute smoke test confirms all 7 region
dummies are available on both data objects at load time.

The spec is ready for estimation subject to the pre-estimation constraint in
`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_implementation_audit_v1.md` §20: the M1-specific
post-estimation diagnostics (joint Wald test, region covariance sub-block,
region-conditional GSUR Hessian sub-matrix) require a supplementary diagnostic
implementation before the post-estimation step can satisfy design memo v2 §21.
That constraint does not block estimation itself.