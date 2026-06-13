# RURO Welfare F4-A — Singles Measure Core (W3/W4/W1) + W6 Design Audit

Date: 2026-06-13 · spec_hash `492bcfa9c766bfcb` · theta_hash `1dd94e9cf1f35464` · stem `fr_p3a_bpool_engine_ready_staged_threeB1`

Internal validation artifact. No inequality statistic, decomposition, V_dir, EUROMOD pricing, promotion, or commit. W6 NOT computed (grid unratified).

## Provenance & preconditions

- Consumed: `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_ViIS_dualstem_v1.parquet`
  - SHA256 `495de8f5904f97792c870329c45c3db0275265d0eb2fc189c68f8cfae078df9f`
- Unique non-null HH keys: **5007** (expected 5007; ok=True)
- spec_hash match: True; theta_hash match: True; all input file hashes match manifest: True
- Gate-0 welfare/engine logsum-negLL parity max|Δ|: **0.00e+00**
- Staged singles negLL reproduced: engine 63900.99724 vs manifest 63900.99724 (|Δ|=1.46e-11)
- **PRECONDITIONS_PASS: True**

## Units & scaling (Task 0.2)

- Engine consumption: c_norm = consumption_eur / c_scale (dimensionless); c_scale=2034.988978049439, l_scale=10.0
- Solver I/O: real-2016 EUR (public); internally w_norm = w_eur / c_scale
- beta_c (fixed) = 1.0; theta_c_singles = 0.0075809783 (>0 ⇒ u unbounded above in c)
- Consumption floor = 1.0 EUR; Ω units = 2016-real EUR (W1/W4 = consumption level; W3 = shift ~0)

## Memo status (Task 0.1)

PRE-REGISTRATION (UNRATIFIED): no signed/ratified artifact found; memo header says pre-registration and the sign-off checklist is unchecked.
(sign-off checklist unchecked items: 5)

## W4 home-node audit (Task 0.3)

| group | n_hh | zero-home HH | non-unique home leisure | unique state |
|---|---|---|---|---|
| singles_male | 2243 | 0 | 0 | True |
| singles_female | 2764 | 0 | 0 | True |

Home node selection: lowest-draw working==0 alternative (deterministic). STOP_W4 = False.

## Utility-only evaluator gate (Task 1)

| group | max_abs_u_diff_vs_engine | pass |
|---|---|---|
| singles_male | 4.44e-16 | True |
| singles_female | 1.78e-15 | True |

Reconstructed u = leisure_term + beta_c·BoxCox(c_norm; theta_c) vs estimation_engine.compute_likelihood_singles(return_components=True)['u'].

## Synthetic kappa-recovery gates (Task 1 / Task 4)

Target recomputed from the SAME transformed reference at known κ, then re-solved.

| group | replace κ=1500 max_err | single_node κ=1500 | shift κ=200 | W1 zero-recovery κ=1234 |
|---|---|---|---|---|
| singles_male | 3.240e-10 | 3.240e-10 | 3.041e-10 | 3.038e-10 |
| singles_female | 8.390e-11 | 8.390e-11 | 4.371e-10 | 2.842e-10 |

## W3 — Laissez-faire revalidation (Task 2)

| group | ref_at_w0_max_abs_vs_ViIS_staged | omega_abs_max_converged | n_nonconverged | nonconv_lt_0p5pct |
|---|---|---|---|---|
| singles_male | 3.553e-15 | 2.926e-10 | 0 | True |
| singles_female | 3.553e-15 | 1.491e-10 | 0 | True |

W3 PASS: **True** (ref value at w=0 ≡ V_i^IS_staged ≤1e-9; |Ω³|≤1e-8; non-convergence <0.5%).

## W4 — Staying-home equivalent (Task 3)

| group | num_vs_analytic_max_abs_norm | n_compared_in_bracket | n_below_floor | n_above_cap | n_genuine_nonconverged | omega_primary_median_eur |
|---|---|---|---|---|---|---|
| singles_male | 1.831e-10 | 2132 | 0 | 111 | 0 | 4.492e+06 |
| singles_female | 4.686e-10 | 2691 | 0 | 73 | 0 | 5.566e+06 |

W4 PASS: **True** (numerical vs **exact analytic** Box-Cox inversion ≤1e-8 in normalized consumption units, in-bracket & feasible; below-floor, above-cap, and genuine non-convergence reported separately; genuine non-convergence <0.5%).

Primary W4 Ω = exact analytic inversion (defined beyond the bracket cap). `above_cap` flags households whose staying-home-equivalent income exceeds 50× their max observed consumption — not a solver failure. Rates: singles_male 4.9%, singles_female 2.6%.

> **Substantive scale observation (flagged for F5; contract NOT changed).** W4 Ω values are very large (median ≈ several million EUR). This is correct under the locked memo definition but is structural, not a bug: the W4 reference is a SINGLE home node with `no weights` — it carries NO opportunity-density term — whereas the target V_i^actual = V_i^IS = logsumexp_j(u_j + log ĝ_j − log π_j) DOES. W1/W3 stay at sane monthly scales because BOTH sides carry the same (log ĝ − log π) terms, which cancel; W4's single node does not, so the entire opportunity-set inclusive-value scale (including the −log π importance-sampling correction) must be compensated through consumption. With near-log consumption utility (theta_c≈0.0076) that compensation is exponentially large. This is the memo's explicit `full-compensation endpoint` (opportunity AND wage priced into w). Whether the W4 reference target should net out the opportunity-density / IS-correction scale is a DEFINITIONAL question for ratification at F5 — surfaced here, not resolved.

## W1 — Equal-pay over own set (Task 4)

| group | n_below_floor | n_above_cap | n_nonconverged | omega_median_eur | working_only_omega_median_eur |
|---|---|---|---|---|---|
| singles_male | 0 | 0 | 0 | 1.621e+03 | 1.717e+03 |
| singles_female | 0 | 0 | 0 | 1.742e+03 | 1.804e+03 |

W1 PASS: **True**. Pre-registered working-only sensitivity computed separately (home keeps actual non-employment consumption). Corrected synthetic zero-recovery (all c_j=κ ⇒ w*=κ) gate reported above.

## W6 — Design decision (Task 5, NOT COMPUTED)

Rule (locked): J = {home node} U {one node per canonical hours band of the estimation spec}, all at consumption w, uniform weights (no g_hat, no pi).

| J node | candidate source | proposed value | BG included? | unresolved decision |
|---|---|---|---|---|
| home | working==0 leisure state | 0h → leisure=TOTAL_LEISURE_HOURS | n/a | time-endowment constant ratification |
| pt1 | estimation band [18.5,21.5] | UNSET (representative hours) | no | which point in band |
| pt2 | estimation band [29.5,30.5] | UNSET | no | which point in band |
| F35 (ref) | estimation reference [33.5,36.5] | UNSET | no | include reference node? |
| ft | estimation band [37.5,40.5] | UNSET | no | which point in band |
| lh | estimation band [44.5,70] | UNSET | no | which point in band |
| (BG?) | D1 background uniform [5,70] | UNSET | UNRESOLVED | include at all? at what hours? |

Unresolved governance decisions:
- Representative hours value WITHIN each band: each band is a RANGE; u depends on leisure = (TOTAL_LEISURE_HOURS - hours), so one hours point per band must be chosen (band midpoint? D1 modal hours? chosen-hours mean?). NOT invented here.
- BG support band treatment: BG is a proposal-density background over [5,70], not a preference focal band. Include a J node for it? If so, at what representative hours (the band spans the whole support)? UNRESOLVED.
- F35 reference band: opportunity reference (beta_h=0). In W6 opportunity betas do not enter (uniform weights), so include an F35 leisure node? Default yes, but confirm.
- TOTAL_LEISURE_HOURS time endowment used to map hours->leisure for J nodes (80h here) must be ratified as the universal mapping constant.

W6 status in output: `BLOCKED_PENDING_GRID_RATIFICATION`.

## Outputs

- `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_measures_F4A_v1.parquet` (sha256 `ddfbd867871b69ddcb708862503826c56e7b122e062012f72e1c066272c5782f`, 5007 rows)
- `F4A_manifest_v1.json` (this manifest)
- gates_all_pass: **True**

---

READY FOR F5: NO — W6 grid remains unratified.
REQUIRED NEXT INPUT: explicit ratification of the W6 universal hours grid.