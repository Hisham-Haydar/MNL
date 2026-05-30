# RURO build fix: wage deflation + idorighh carry-through v1

Date: 2026-05-30

Scope: build-side only. No estimation or welfare logic was changed or run.

## Fix 1: wage price basis

Chosen stage: estimator-facing assembly in `scripts/bpool/build_bpool_estimation_ready.py`, using the same CPI factors as the disposable-income deflation:

| year | phi |
|---:|---:|
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |

Reason:

1. Do not deflate at `build_bpool_precompute.py` when drawn wages are written into `yivwg`. At that point the wage feeds nominal EUROMOD earnings.
2. The actual chain is:
   `D1W1 wage nominal -> precompute yivwg nominal -> yem00/yemxp/yem nominal -> EUROMOD ils_dispy nominal -> ils_dispy_real = ils_dispy * phi`.
3. If `yivwg` were deflated before `_apply_earnings`, EUROMOD would price a real wage as if it were nominal, and then `ils_dispy_real` would apply `phi` again. That is the double-deflation path.
4. In this codebase, `build_bpool_estimation_ready.py` reads estimator wage columns from `fr_p3a_bpool_d1w1__{singles,couples}.parquet`; it only joins `ils_dispy_real` from priced long files. Therefore editing only `run_bpool_euromod.py` would not change the wage columns consumed by estimation.

Convention:

| estimator-facing real column | retained nominal copy |
|---|---|
| `wage` | `wage_nominal` |
| `wage_male` | `wage_male_nominal` |
| `wage_female` | `wage_female_nominal` |

`wage`, `wage_male`, and `wage_female` are now 2016-real in estimation-ready and engine-ready parquets. Nominal wages remain in `*_nominal`. Precompute and priced files remain nominal by design.

Rebuilt affected outputs:

| file | rows |
|---|---:|
| `fr_p3a_bpool_estimation_ready__singles.parquet` | 505,707 |
| `fr_p3a_bpool_estimation_ready__couples.parquet` | 6,701,638 |
| `fr_p3a_bpool_engine_ready__singles.parquet` | 505,707 |
| `fr_p3a_bpool_engine_ready__couples.parquet` | 6,701,638 |

Backups: 16 requested stage parquets were copied under `C:/Users/hisham/MNL/EUROMOD-STORAGE/new_data/` with suffix `.pre_wage_deflation.bak`, spanning precompute, priced, estimation-ready, and engine-ready.

## Fix 1 verification

Engine-ready comparison was against the `.pre_wage_deflation.bak` files.

| check | singles | couples |
|---|---:|---:|
| row count unchanged | PASS | PASS |
| `ils_dispy_real` values byte-identical | PASS | PASS |
| nominal wage copies match pre-fix wage columns | PASS | PASS |
| 2015 wage = pre-fix wage * 1.0031 | PASS | PASS |
| 2016 wage unchanged | PASS | PASS |
| 2017 wage = pre-fix wage * 0.9886 | PASS | PASS |

All maximum absolute wage scaling residuals were 0.0.

Positive-wage means show the phi adjustment:

| mode | column | 2015 nominal | 2015 real | 2016 nominal/real | 2017 nominal | 2017 real |
|---|---|---:|---:|---:|---:|---:|
| singles | `wage` | 15.703946 | 15.752628 | 15.950052 | 16.209364 | 16.024577 |
| couples | `wage_male` | 15.758500 | 15.807351 | 15.960220 | 16.351383 | 16.164977 |
| couples | `wage_female` | 15.579992 | 15.628290 | 15.922181 | 16.195201 | 16.010576 |

Fix 1 gate: PASS.

## Fix 2: idorighh

`idorighh` was already present in the B-pool source and carried through to engine-ready. The build now includes an explicit check that `idorighh` is present, non-null, and equals `cluster_id`. No substitution with `stacked_hh_uid` or restacked `idhh` was made.

Engine-ready recurrence, counted over unique `(stacked_hh_uid, idorighh, data_year)` household-year units:

| mode | 1-wave idorighh | 2-wave idorighh | 3-wave idorighh |
|---|---:|---:|---:|
| singles | 2,797 | 1,105 | 0 |
| couples | 4,238 | 1,600 | 0 |

Non-null rows:

| mode | non-null `idorighh` | rows |
|---|---:|---:|
| singles | 505,707 | 505,707 |
| couples | 6,701,638 | 6,701,638 |

Fix 2 gate: PASS.

## Build checks

Commands run:

```powershell
$env:MNL_STORAGE_ROOT='C:\Users\hisham\MNL\EUROMOD-STORAGE'
.\.venv\Scripts\python.exe scripts\bpool\build_bpool_estimation_ready.py
.\.venv\Scripts\python.exe scripts\bpool\harmonise_bpool_engine_ready.py
.\.venv\Scripts\python.exe scripts\bpool\check_bpool_engine_ready.py
```

`check_bpool_engine_ready.py` result: OVERALL PASS.

