# RURO `ruro_occ_M0b1` — Wage Pathology Diagnostic v1

Date: 2026-05-14
Script: `Results/_wage_pathology_diag_ruro_occ_M0b1.py`
Run: `run_2026-05-14_12-07-18`
MNL data: `fr_2016_RURO_mnl__couples.parquet` (257,700 rows / 2,577 households)

---

## 1. Wage variable audit

| role | column | present | unit |
|---|---|---|---|
| couples male observed wage | `wage_male` | yes | EUR/hour (EUROMOD net hourly wage draw) |
| couples female observed wage | `wage_female` | yes | EUR/hour |
| predicted wage (both) | prob-weighted `wage_male` / `wage_female` | computed | EUR/hour |

No column mismatch. Both observed and predicted wages are in the same EUR/hour unit.

---

## 2. Wage draw support (all working alternatives)

| gender | p1 | p25 | p50 | p75 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|
| male | 3.7 | 42.5 | 85.1 | 127.5 | 161.4 | 168.3 | 170.0 |
| female | 3.6 | 42.8 | 85.3 | 127.6 | 161.5 | 168.3 | 170.0 |

**Finding**: the wage draw support is heavily right-skewed. The MNL parquet
contains Monte Carlo wage draws from the lognormal proposal distribution, not
just observed wages. Most draws are at high wage levels; the p25 across all
working alternatives is already 42.5 EUR/h and the max is 170 EUR/h. This is
the RURO draw mechanism: each household has 100 alternatives, most of which
are high-wage / high-hours draws. The observed chosen wage (p50 ~15 EUR/h) is
in the left tail of the draw support.

---

## 3. Observed chosen wage distribution

| gender | n working | p25 | p50 | p75 | p95 | mean |
|---|---|---|---|---|---|---|
| male | 2,504 | 12.3 | 15.3 | 20.6 | 33.4 | 17.7 |
| female | 2,487 | 11.1 | 13.8 | 17.3 | 27.0 | 15.2 |

Observed wages are concentrated 10-25 EUR/h, consistent with French labour
market data. The observed chosen alternatives are in the lower 25-30% of the
draw support.

---

## 4. Predicted chosen wage distribution (M0b1, prob-weighted)

| gender | p25 | p50 | p75 | p95 | mean |
|---|---|---|---|---|---|
| male | 121.9 | 145.2 | 159.7 | 168.1 | 137.2 |
| female | 123.6 | 145.1 | 159.6 | 168.3 | 137.3 |

Predicted wages are 8-10× larger than observed. The model is assigning
probability mass to the highest-wage alternatives in the draw.

---

## 5. Probability mass by wage bin

Bins are defined on the draw-support distribution (p25=42.5, p75=127.5,
p95=161.4 EUR/h for males).

| gender | non-work | wage < p25 | p25–p75 | p75–p95 | wage > p95 |
|---|---|---|---|---|---|
| male | 0.02% | 0.93% | 28.4% | 49.1% | 21.6% |
| female | 0.02% | 0.96% | 28.1% | 50.1% | 20.8% |

**71% of predicted probability mass is concentrated above the wage draw p75
(127 EUR/h).** Only 0.9-1.0% falls below draw-support p25 (42.5 EUR/h),
where the actual observed wages live. This directly explains the predicted
mean of ~137 EUR/h.

---

## 6. Choice-index V decomposition by wage bin

Average V components per bin, weighted by predicted probability mass. `U` is
preference utility; `int` is the `beta_ll` interaction; `O_m`/`O_f` is the
combined opportunity layer per partner (hours + market + wage + occupation);
`-log_prior` is the proposal correction; `V` is the total choice index.

### Couples male

| bin | prob mass | U | beta_ll interaction | O_m | O_f | −log_prior | V |
|---|---|---|---|---|---|---|---|
| non-work | 0.6 | 329.5 | 3.4 | 0.0 | −28.5 | 13.7 | 318.1 |
| wage < p25 | 24.1 | 336.0 | 3.2 | −8.7 | −27.4 | 21.2 | 324.3 |
| p25–p95 | 1,996 | 360.5 | 3.2 | −24.8 | −24.9 | 21.2 | 335.2 |
| wage > p95 | 556 | 365.5 | 3.3 | −28.7 | −23.5 | 21.2 | 337.8 |

### Couples female

| bin | prob mass | U | beta_ll interaction | O_m | O_f | −log_prior | V |
|---|---|---|---|---|---|---|---|
| non-work | 0.6 | 328.2 | 3.4 | −29.2 | 0.0 | 12.4 | 314.8 |
| wage < p25 | 24.8 | 338.4 | 3.2 | −28.3 | −8.5 | 21.2 | 326.0 |
| p25–p95 | 2,015 | 360.5 | 3.2 | −25.8 | −24.0 | 21.2 | 335.1 |
| wage > p95 | 537 | 365.8 | 3.3 | −24.1 | −27.8 | 21.2 | 338.4 |

**Key observation**: the V gap between high-wage and low-wage bins is:

- `U` gap (high vs low wage): +29.5 nats (365.5 − 336.0 for males)
- `beta_ll` interaction gap: +0.1 nats (negligible)
- Opportunity gap: −20.0 nats (O_m more negative at high wages — O_W is
  more negative because high-wage draws are less likely under the lognormal)
- Net V gap: +13.5 nats (337.8 − 324.3)

The `U` dominates. The `beta_ll` interaction contributes ~3.2-3.4 nats
**uniformly across all bins** — it does not drive the selection toward
high-wage alternatives specifically.

---

## 7. High-wage dominance diagnosis

| driver | contribution to high-wage selection | verdict |
|---|---|---|
| Consumption utility U (driven by theta_c = +0.27) | +29.5 nats from low- to high-wage bin | **PRIMARY CAUSE** |
| `beta_ll` interaction | ~0.1 nats differential; uniform ~3.4 nats in all working bins | not the driver |
| Wage opportunity O_W (negative, penalises high-wage draws) | offsets U by ~20 nats but insufficient | partial mitigant, not dominant |
| Prior correction −log_prior | identical across all working bins (~21.2) | no role |
| Plot/reporting | weights are correct (checked via prob sum = 1.0 per hh) | not a bug |

With `theta_c = +0.27`, the consumption Box-Cox `BC(C, 0.27)` is nearly
linear over the observed consumption range. A high-wage / high-hours
alternative provides much more disposable income than a low-wage / part-time
alternative, and the near-linear `BC(C)` translates this income difference
into a large utility difference: mean `U` at high-wage alternatives is ~300
EUR/h (`beta_c × BC(C)`) vs ~233 EUR/h at low-wage alternatives (see
check 7 raw output). The opportunity layer penalises these alternatives (they
have lower lognormal density given the observed sigma), but is overwhelmed by
the U gap.

---

## 8. M0b1 vs M0a-clean comparison

| metric | M0a-clean | M0b1 | change |
|---|---|---|---|
| `theta_c` (couples) | 0.319 | 0.271 | slightly lower (less linear) |
| `beta_c` (couples) | 6.154 | 5.885 | slightly lower |
| `beta_ll` | 0.0 (absent) | 2.0 (at upper bound) | new, but see note |
| cou_m predicted wage mean | 139.9 EUR/h | 137.2 EUR/h | −1.9% |
| cou_m predicted wage p50 | 146.9 EUR/h | 145.2 EUR/h | −1.2% |
| cou_f predicted wage mean | 140.1 EUR/h | 137.3 EUR/h | −2.0% |
| cou_f predicted wage p50 | 146.5 EUR/h | 145.1 EUR/h | −0.9% |
| cou_m predicted participation | 1.0000 | 0.9998 | negligible |

**M0b1 does not worsen the wage pathology relative to M0a-clean.** The
~137-140 EUR/h predicted couples wages were identical in M0a-clean. The
`beta_ll` interaction hitting its upper bound (+2.0) adds approximately
3.4 nats uniformly to all working alternatives — it does not concentrate
selection toward high-wage alternatives. `theta_c` decreased marginally from
0.319 → 0.271 but remains solidly positive, so the consumption block remains
near-linear. The wage pathology is therefore a **pre-existing structural
problem** in the M0a family, not introduced by M0b1.

---

## 9. Verdict

**ROOT CAUSE: model-selection problem.**

The ~137 EUR/h predicted couples wage is not a plotting/reporting bug (the
reporter correctly aggregates prob-weighted wages; probability sums to 1.0
per household to within 1e-15) and not a wage draw/support problem (the draw
support itself is right-skewed by construction, but the observed chosen wages
are in the left tail of this support). The model assigns near-all probability
mass to the highest-wage/hours alternatives because consumption utility U is
near-linear (`theta_c ≈ +0.27`): the U gap between a 15 EUR/h 35h alternative
and a 165 EUR/h 60h alternative is ~30 nats, which the wage opportunity
penalty cannot offset. The `beta_ll` interaction term is not the driver.
The same pathology was already present in M0a-clean.

---

## 10. Recommendation

**Run M0b2.**

M0b2 tightens `theta_c` to `[-8, 0]`, forcing at most logarithmic consumption
utility (`theta_c = 0` → `BC(C, 0) = log(C)`). This is the intervention that
can break the near-linear utility gap and allow the model to produce realistic
wage and hours distributions for couples. M0b1 is insufficient: `beta_ll`
saturated at its upper bound (+2.0) and the resulting reduction in `theta_c`
(0.319 → 0.271) is too small to resolve the identification problem.

Run M0b2 from spec defaults (`--warm-start none`) with at least three start
points. After M0b2, if `theta_c` settles strictly interior to the new bound
(not at 0.0), the pathology should resolve. If `theta_c` hits 0.0, a further
intervention (M0c: pooling couples and singles `theta_c`, or an adult-
equivalence scale on consumption) will be needed.

---

## Reproducibility

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\Results\_wage_pathology_diag_ruro_occ_M0b1.py"
```

Output JSON: `Results/_wage_pathology_diag_ruro_occ_M0b1.json`
