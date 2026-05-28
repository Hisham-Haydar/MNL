Reparameterise the RURO utility specification from the additive Box-Cox form to the
Aaberge-Colombino-Strom (ACS) multiplicative-shifter form, following the R reference
implementation at U:\Desktop\Nizam_Hisham\MNL\stijn\Ruro_functions_EMRWS.R
(specifically ff_calc_util, lines ~685-714). Read that file ONLY to confirm the
structural form; do not port R code into Python. Read also
RURO_recovery_test_results_v1.md (current diagnosis: utility-scale ridge along
beta_c / beta_l0_m / beta_l0_f produces non-PD Hessian) before starting.

Execute three phases in sequence. Each phase is gated on the success of its predecessor.

═══════════════════════════════════════════════════════════════════════════════
PHASE 0 — Pre-estimation verification of repricing variation (read-only)
═══════════════════════════════════════════════════════════════════════════════
Before any specification change, verify that the EUROMOD repricing has produced
the data variation that the likelihood requires.

0a. On the engine-ready B-pool parquets (singles + couples), compute within-household
    statistics of ils_dispy_real across simulated alternatives:
      - mean and standard deviation of ils_dispy_real within (stacked_hh_uid).
      - count of households with within-HH standard deviation equal to zero.
      - distribution of within-HH standard deviation (percentiles 5, 25, 50, 75, 95).
    Expected: substantial within-HH variation (median std dev on the order of
    several hundred to several thousand euros/month); zero households with
    std-dev = 0.
0b. For working alternatives (drawn working == 1), plot ils_dispy_real against
    drawn earnings (hours * wage * 52/12) on a random sample of 50 households.
    Expected: monotone, concave (progressive tax-benefit structure). Report
    visually and as a per-household Spearman rank correlation.
0c. For non-working alternatives (drawn working == 0), tabulate the distribution
    of ils_dispy_real across households. Expected: positive disposable income
    reflecting benefits, transfers, and capital income; substantial cross-household
    variation reflecting heterogeneous welfare-system coverage.
0d. Report a PASS/FAIL verdict on each of the three checks. Any FAIL halts the
    sequence and is escalated for diagnosis before Phase 1 begins.

═══════════════════════════════════════════════════════════════════════════════
PHASE 1 — Reparameterisation (only if Phase 0 returns PASS)
═══════════════════════════════════════════════════════════════════════════════
Change utility from
  U = beta_l0 * BC_l(leisure) + (shifters * leisure_terms) + beta_c * BC_c(c) + ...
to
  U = A_g(x) * BC_l(leisure_g) + beta_c * BC_c(c) + (couples interaction term)
where
  A_g(x) = alpha_0,g + alpha_1,g * log(age) + alpha_2,g * log(age)^2
         + alpha_3,g * children + alpha_4,g * drgur + alpha_5,g * drgmd
         + alpha_6,g * educL + alpha_7,g * educH
for each block g in {sm, sf, m, f}. Children variable adjusted by age band per the
present specification convention; gender-specific shifters as documented.

REGIONAL TRANSLATION: do NOT transliterate the R reference's regW/regB as
reg_nuts1_* in A_g(x). The NUTS-1 region dummies remain exclusively in the
market_opportunity (access) layer. The preference-layer regional analogues
of regW/regB are the urbanisation dummies drgur and drgmd (rural as reference),
on the methodological grounds set out in the accompanying memorandum.

SAME-VARIABLE-TWO-LAYERS: drgur and drgmd enter both the preference layer A_g(x)
AND the access layer (where they are already present). This is admissible under
the identification conditions documented in the memorandum and will be verified
in Phase 2 through the Hessian-implied correlation between the preference and
access coefficients on the same dummy.

PARAMETER COUNT: total remains 58. The leisure intercept (former beta_l0_*)
becomes the constant alpha_0,g of A_g(x); the leisure shifters (former beta_l_age_*,
beta_l_age2_*, beta_l_nkids_*) become alpha_1,g through alpha_3,g within A_g(x);
the urbanisation preference shifters alpha_4,g and alpha_5,g are NEW preference-layer
parameters, but they are accommodated within the 58 total by recognising that the
former beta_l0_* parameter has been absorbed into A_g(x) as alpha_0,g. Confirm
58/58 in the new YAML before proceeding.

WAIT — recount required. The translation reorganises but also adds 2 shifters per
block (urbanisation in preference layer). For each of {sm, sf, m, f}, A_g(x) gains
alpha_4,g and alpha_5,g. That is 8 new parameters across the four blocks. Net change:
+8 from urbanisation preference shifters; -4 from no longer having a standalone
beta_l0_* (now subsumed into A_g(x) constant); the leisure shifter renames are
neutral. Net: 58 + 8 - 4 + 4 (reinstated alpha_0,g constants) = 62. Re-verify with
the user before committing to 62 vs 58.

This recount supersedes the earlier "parameter count invariant" instruction in
v1 of this prompt. The reparameterisation as specified increases the parameter
count from 58 to 62. If a 58-parameter specification is required for reasons
of sample-size or governance, the urbanisation preference shifters can be
omitted (returning to the additive-Box-Cox base plus the multiplicative-shifter
restructuring of the existing parameters), in which case the count remains
58 and the regional preference analogue of regW/regB is deferred to a later
specification increment.

ASK THE USER which option to implement before proceeding:
  Option B-strict: 58 params, multiplicative-shifter restructuring of existing
    parameters, no urbanisation in preference layer.
  Option B-extended: 62 params, multiplicative-shifter restructuring plus
    urbanisation preference shifters in A_g(x).

Implement only after the user selects.

1a. Rewrite estimation_spec_bpool_p3a_v1.yaml per the selected option. Document
    the rename map at the top of the YAML so the lineage from the old parameter
    names is preserved.
1b. Rewrite the utility function in estimation_engine.py to implement A_g(x) *
    BC_l(leisure_g) for each block. Confirm against R lines 706-712 for the
    couples leisure interaction.
1c. Update the analytical gradient in estimation_engine.py. Verify against
    numerical-difference check on 50 households; require max |analytical -
    numerical| / |numerical| < 1e-6.
1d. Smoke test: load the new spec, run precompute, evaluate U on 100 simulated
    alternatives, confirm finite values.

═══════════════════════════════════════════════════════════════════════════════
PHASE 2 — Recovery test on reparameterised specification (only if Phase 1 passes)
═══════════════════════════════════════════════════════════════════════════════
2a. Run recovery_test.py with the new spec, couples 2016 slice, 300 HH, scipy
    trust-constr, no maxiter cap.
2b. Report:
    - Convergence status, iterations, final negLL.
    - G3 conditioning: Hessian positive-definite (yes/no), minimum eigenvalue,
      condition number.
    - G1 recovery: per-parameter |theta_hat - theta*| and error/SE.
    - G2 reproducibility: two starts (warm = theta*, cold = spec defaults).
    - G3b urbanisation x region: Hessian-implied correlation of alpha_4,g and
      alpha_5,g (preference) with beta_E_drgur and beta_E_drgmd (access).
      Verdict on whether the same-variable-two-layers identification holds:
      |rho| < 0.8 for joint identifiability; |rho| >= 0.8 suggests the
      configuration is empirically degenerate even if theoretically admissible.
    - G4 block-level recovery confirmation.
2c. Write RURO_recovery_test_results_v2.md.

SUCCESS CRITERION: positive-definite Hessian, recovery of theta* within tolerance,
finite condition number, and (if Option B-extended) |rho| < 0.8 for the
preference-access correlation on each urbanisation dummy.

NON-OBJECTIVES: do not modify the harmoniser, the draw construction, the EUROMOD
pricing, the importance-sampling correction, the post-estimation reports, or the
B-pool data files. Do not re-estimate any prior result yet. Do not commit any
artefacts until Phase 2 returns success.