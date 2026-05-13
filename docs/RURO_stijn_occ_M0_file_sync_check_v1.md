# RURO R reference Occ M0 — File Sync Check v1

Date: 2026-05-12

Verifies that every file referenced in the implementation report and run
instructions is present at the expected path.

## 1. File inventory

| Expected path | Status | Notes |
|---|---|---|
| `docs/RURO_model_spec_contract_v4_ruro_occ.md` | **EXISTS** | Correct location. |
| `docs/RURO_occ_pipeline_audit_v1.md` | **EXISTS** | Correct location. |
| `docs/RURO_ruro_occ_baseline_spec_v1.md` | **EXISTS** | Correct location (see §2). |
| `docs/RURO_ruro_occ_baseline_implementation_report_v1.md` | **EXISTS** | Correct location. |
| `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` | **EXISTS** | Correct location. |

## 2. Path mismatch — `RURO_ruro_occ_baseline_spec_v1.md`

The implementation report (§ "Reference contracts") and the YAML header cite
this file as:

```
Prototype/RURO_ruro_occ_baseline_spec_v1.md
```

The file does **not** exist under `Prototype/`. It lives at:

```
docs/RURO_ruro_occ_baseline_spec_v1.md
```

### Required fix

Update the reference path in:

1. `docs/RURO_ruro_occ_baseline_implementation_report_v1.md` — header
   "Inputs read" list, line 3.
2. `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` — comment block,
   line 8 (`Prototype/RURO_ruro_occ_baseline_spec_v1.md`).

No file needs to be moved. Only the two citation strings need correcting.

## 3. Code-side verification summary

Cross-checked against the implementation report Gate-A scorecard and the
commit that landed 52 parameters:

| Claim | Verified in source | Location |
|---|---|---|
| `model_family: regular` | Yes | `estimation_spec_ruro_occ_M0.yaml:49` |
| `spec.name == ruro_occ_M0` | Yes | `estimation_spec_ruro_occ_M0.yaml:47` |
| 12 occupation coefficients (`sm/sf/cm/cf`) | Yes | YAML lines 240–251; parser appends to `market_opportunity_shifters` |
| `beta_E · working` base intercept | Yes | `estimation_spec_ruro_occ_M0.yaml:79–80` |
| Mincer wage mean (`beta_w0` … `beta_w_pexp2`) | Yes | YAML lines 94–104 |
| `sigma` variance parameter | Yes | YAML lines 103–104 |
| `applies_to: sm/sf/cm/cf` routing — NumPy engine | Yes | `estimation_engine.py:112–117, 224, 254` |
| `applies_to: sm/sf/cm/cf` routing — GAMSPy vectorized | Yes | `gamspy_estimation_vectorized.py:556–560, 983, 1003` |
| Log-normal wage Jacobian `−log(wage)` | Yes | `estimation_engine.py:648` |
| PT1 band `[18.5, 21.5]` | Yes | `enh_RURO_prep_mnl_basic.py:706` |
| proposal-component aliases (`log_q_E/H/W/Occ`) | Yes | `enh_RURO_prep_mnl_basic.py:1338–1356, 1427, 1562` |
| `loc4` excluded from utility/hours/wage/market blocks | Yes (parser enforces) | `estimation_spec_parser.py` |
| M0-forbidden artifacts dropped from keep set | Yes | `enh_RURO_prep_mnl_basic.py` keep set; `reduce_mnl_columns.py` |

## 4. Remaining prerequisites before estimation

| Item | Owner | Status |
|---|---|---|
| Rebuild draws: `--occ-spec empirical --occ-strata __all__` | Data pipeline | **PENDING** |
| Run EUROMOD on rebuilt draws | Data pipeline | **PENDING** |
| Rebuild MNL parquet with `enh_RURO_prep_mnl_basic.py` | Data pipeline | **PENDING** |
| Canary: median distinct `loc4` per household ≥ 3 | Validation | **PENDING** |
| Correct citation paths (§2 above) | Docs | **PENDING** |

Gate-A is fully green on the code side. The single remaining code-level action
is correcting the two citation strings in §2. All other blockers are data
rebuild steps.