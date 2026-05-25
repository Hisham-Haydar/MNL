# RURO Cluster-Robust SE Static Validation

*Generated: 20260521T113948Z | Mode: smoke-test*

---

## Validation checks

| # | Check | Status | Notes |
|---|-------|--------|-------|
| C1 | Module imports | **PASS** | all imports succeeded |
| C2 | CLI --help works | **PASS** | argparse --help exited with code 0 |
| C3 | P3a pooled YAML parses | **PASS** |  |
| C4 | Free-parameter vector length = 55 | **PASS** | n=55, expected=55 |
| C5 | Pooled parquet schema readable | **PASS** |  |
| C6 | cluster_id column exists | **PASS** |  |
| C7 | cluster_id == idorighh (bounded) | **PASS** |  |
| C8 | 9,657 clusters documented | **PASS** | Bounded sample (50,000 rows) contains 500 unique idorighh. Full dataset expected 9,657 clusters per GA16. |
| C9 | Score interface callable (smoke-test) | **PASS** |  |
| C10 | Score matrix shape correct | **PASS** |  |
| C11 | Cluster ids aligned to score rows | **PASS** |  |
| C12/T1 | Sign check: sum(scores)==-grad | **PASS** | max_diff=5.82e-10 |
| C13/T2 | Meat matrix B symmetric | **PASS** | 2000 clusters in smoke sample |
| C14 | Sandwich covariance callable | **PASS** |  |
| C15 | Robust SE output finite | **PASS** | dummy Hessian H=0.1*I used; actual SEs will differ post-estimation |
| C16 | No pooled estimation run | **PASS** | Smoke test only. No solver invoked. |
| C17 | No welfare computation run | **PASS** | Welfare not authorized. Not computed. |

---

## GA17 final status: **smoke-test callability: CONFIRMED**

| Item | Status |
|------|--------|
| GA17 | **smoke-test callability: CONFIRMED** |
| T4/T5 note | T4 (SE positivity) and T5 (robust vs Hessian comparison) are post-estimation checks requiring converged theta and the true Hessian. They are not part of the smoke-test clearance. |
| Pooled estimation | NOT authorized |
| Welfare computation | NOT authorized |
| Active JMP baseline | M1-clean 2016 |
| Next gate | GA17 clearance addendum; if cleared, pooled-estimation execution authorization memo |
