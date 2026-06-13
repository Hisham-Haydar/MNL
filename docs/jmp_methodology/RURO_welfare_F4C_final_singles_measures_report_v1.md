# RURO Welfare F4-C — Final Singles Measures (W3/W1/W4/W6), Ratified Normalization

Date: 2026-06-13 · spec_hash `492bcfa9c766bfcb` · theta_hash `1dd94e9cf1f35464` · stem `fr_p3a_bpool_engine_ready_staged_threeB1` · S=101/HH

Frozen final singles welfare measures under the operator-ratified normalization contract. F4A/F4B preserved as immutable diagnostics. No estimation/EUROMOD/V_dir/inequality/decomposition/promotion/commit.

## Normalization: two distinct objects

- **Raw `V_i^IS` = log Σ_j exp(V_j)** over S=101 IS draws — the conditional-logit denominator; **likelihood-compatible** (estimation uses this; −log S is a θ-independent constant invisible to the MLE).
- **Normalized `V_actual = V_i^IS − log(S)`** — the cardinality-invariant **welfare level** (consistent IS estimate of the inclusive value); used for ALL welfare-level comparisons here. S_i=101 for every household.

## Ratified contract (frozen)

- **1_actual_target**: V_actual_i = V_i^IS_staged - log(S_i); S_i = household actual draw count
- **2_deterministic_reference_normalization**: uniform log-mean: logsumexp(values) - log(|J|)
- **2_w4_single_node**: u(w, leisure_home) unchanged because log(1)=0
- **3_w4_bracket**: [1 EUR, 50 x max observed c]; expand once; remaining flagged/excluded; analytic extrapolation beyond authorized bracket NOT accepted as convergence
- **4_w6_grid_hours**: [0.0, 20.0, 30.0, 35.0, 39.0, 48.0]
- **4_w6_node_labels**: ['home', 'PT1', 'PT2', 'F35', 'FT', 'LH']
- **4_w6_bg_excluded**: BG is continuous proposal support, not a canonical preference/reference state
- **4_total_leisure_hours**: 80.0
- **5_w4_interpretation**: full-compensation staying-home endpoint; large magnitude retained and caveated; normalization removes artificial draw-count scale only, NOT genuine opportunity-set compensation

Consumption time unit: monthly real-2016 EUR (FR EUROMOD ils_dispy; build earnings use WEEKS_PER_MONTH=52/12 => monthly; c_scale≈2035 ≈ mean monthly disposable income).

## Provenance (Task 0)

- 5,007 unique HH keys: True; S_i uniform 101: True; spec/theta hash match: True/True
- Consumed F4A parquet sha256 `ddfbd867871b69ddcb708862503826c56e7b122e062012f72e1c066272c5782f`
- Consumed dualstem V_iIS sha256 `495de8f5904f97792c870329c45c3db0275265d0eb2fc189c68f8cfae078df9f`

## W3 / W1 — regression vs F4A (Task 2)

| group | W3_max_domega_vs_F4A | W3_abs_max | W1_max_domega_vs_F4A | W1wo_max_domega_vs_F4A | W3_genuine_nonconv | W1_genuine_nonconv |
|---|---|---|---|---|---|---|
| singles_male | 0.000e+00 | 2.926e-10 | 0.000e+00 | 0.000e+00 | 0 | 0 |
| singles_female | 1.096e-10 | 1.491e-10 | 1.687e-10 | 1.692e-10 | 0 | 0 |

Gate (Δω vs F4A ≤1e-8 EUR; |W3 ω|≤1e-8; 0 genuine non-conv): **PASS**. Subtracting log(S) from BOTH actual and own-set reference leaves the root unchanged ⇒ W3/W1 are numerically identical to F4A.

## W4 — Staying-home full-compensation endpoint (Task 3)

| group | median_eur | p10_eur | p90_eur | min_eur | max_eur | median_ratio_to_actual_c | n_outside_bracket_after_expand | n_genuine_nonconv | num_vs_analytic_max_norm |
|---|---|---|---|---|---|---|---|---|---|
| singles_male | 5.368e+04 | 2.465e+04 | 1.196e+05 | 3.820e+03 | 6.894e+05 | 2.675e+01 | 0 | 0 | 4.863e-12 |
| singles_female | 6.701e+04 | 3.293e+04 | 1.226e+05 | 5.046e+03 | 9.650e+05 | 3.407e+01 | 0 | 0 | 6.407e-12 |

Gate (num-vs-analytic ≤1e-8 normalized in-bracket; outside-bracket <0.5%; genuine non-conv <0.5%): **PASS**. Convergence classified SOLELY by the bracket+one-expansion contract; analytic extrapolation beyond the bracket is NOT accepted (0 outside under the normalized target). 
> **Full-compensation magnitude caveat (retained).** W4 medians are large (~tens of thousands of EUR/month, ~30× actual consumption). Normalization removed the artificial draw-count scale (log S, ~84×) but NOT the genuine opportunity-set compensation: the single home node carries no opportunity density while `V_actual` does. This is the memo's full-compensation staying-home endpoint, by design.

## W6 — Min-of-equal-pay over the universal grid (Task 4)

Grid (identical for every household): hours [0.0, 20.0, 30.0, 35.0, 39.0, 48.0] (home, PT1, PT2, F35, FT, LH); leisure [80.0, 60.0, 50.0, 45.0, 41.0, 32.0] (= 80 − hours). Utility-only u(c,ℓ), equal consumption w at all 6 nodes, uniform prob 1/6, no opportunity-density/prior. `V_ref = logsumexp_j(u_j(w)) − log(6)`. BG excluded (proposal support, not a canonical state).

| group | median_eur | p10_eur | p90_eur | min_eur | max_eur | median_ratio_to_actual_c | n_outside_bracket_after_expand | n_genuine_nonconv |
|---|---|---|---|---|---|---|---|---|
| singles_male | 5.897e+04 | 2.716e+04 | 1.309e+05 | 4.341e+03 | 7.618e+05 | 2.948e+01 | 0 | 0 |
| singles_female | 8.610e+04 | 4.248e+04 | 1.607e+05 | 6.879e+03 | 1.368e+06 | 4.401e+01 | 0 | 0 |

Invariance / synthetic gates:
| group | synthetic_kappa_max_err | duplication_invariance_max_nats | cross_hh_invariance_diff_eur | beta_l_coeff_recovery_spread |
|---|---|---|---|---|
| singles_male | 3.240e-10 | 8.882e-16 | 0.000e+00 | 2.220e-15 |
| singles_female | 8.390e-11 | 1.776e-15 | 0.000e+00 | 5.329e-15 |

Gate (grid identical across HH; no opp/prior terms; synthetic-κ ≤1e-8; node-duplication invariance ≤1e-10 nats; cross-HH invariance ≤1e-8; outside-bracket & non-conv <0.5%): **PASS**. W6 also carries the full-compensation interpretation (own-opportunity-set AND pay priced against a common benchmark); magnitude caveat applies.

## Outputs

- `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_measures_F4C_v1.parquet` (sha256 `dd163e2ec87b43ca97a5613bd0983fd6de720889d7e34ed0f048b9d71e827a4b`, 5007 rows): V_actual_normalized, S_i, W3/W1/W4/W6 + W1 working-only, solver & bracket status.
- `F4C_manifest_v1.json`; this report.
- all_measure_gates_pass: **True**

---

W3 STATUS: valid
W1 STATUS: valid
W4 STATUS: valid
W6 STATUS: valid
READY FOR F5: yes