# JMP Pooled P3a Estimation — Execution Authorization v1

Date: 2026-05-21

Specification class: execution authorization memo. The memo
authorises the execution of the pooled P3a estimation
(`ruro_occ_P3a_pooled`) — the three-start maximum-likelihood
estimation of the pooled 55-parameter specification on the GSURv2
opportunity-year-aligned pooled dataset, with cluster-robust
standard errors at `idorighh` — and binds the mandatory post-
estimation diagnostics that must be completed before any SA2
verdict. It is an authorization document for the pooled estimation
execution only; it does not authorise welfare computation, canonical
promotion, or the displacement of the M1-clean baseline.

Reference documents:
- `Results/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md` (Gate-A
  PASS WITH BLOCKER → PASS for pre-estimation purposes)
- `docs/RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md` (GA17
  smoke-test callability CONFIRMED; Gate-A updated to PASS for pre-
  estimation authorization purposes)
- `docs/estimation/RURO_cluster_robust_SE_design_audit_v1.md`,
  `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md`,
  `docs/estimation/RURO_cluster_robust_SE_implementation_correction_v1.md`,
  `Results/RURO_cluster_robust_SE_static_validation_v1.md` (the
  cluster-robust SE infrastructure and its validation)
- `docs/JMP_pooled_P3a_estimation_design_memo_v1.md`, its correction,
  and its review addendum (the pooled estimation design)
- `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` (the
  pooled dataset construction PASS)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  baseline)

Interpreter of record: `.venv\Scripts\python.exe`.

Scope of memo: the memo authorises the pooled P3a estimation
execution, specifying the specification (§5), the data input (§6),
the cluster-robust inference requirement (§7), the three starts (§8),
the warm-start strategy (§9), the solver and vectorised mode (§10),
the expected runtime (§11), the required outputs (§12), the mandatory
post-estimation diagnostics (§13), the cluster-robust SE outputs
(§14), the SA2 verdict requirements (§15), the halt conditions (§18),
and the exact Claude Code estimation prompt (§19). The memo does not
authorise welfare computation, canonical promotion, or M1-clean
displacement; those steps are separately gated.

---

## 1. Purpose

The purpose of this memo is to authorise the execution of the pooled
P3a estimation — the three-start maximum-likelihood estimation of the
`ruro_occ_P3a_pooled` specification (55 parameters) on the GSURv2
opportunity-year-aligned pooled dataset, with cluster-robust standard
errors at `cluster_id = idorighh` — and to bind the mandatory post-
estimation diagnostics that gate any subsequent SA2 verdict.

The estimation is authorised because the three preconditions the
Gate-A parse report established are now met. Gate-A passed (GA1–GA16
PASS, the pooled YAML and data input structurally validated). The
GA17 cluster-robust SE infrastructure blocker is cleared at the
smoke-test-callability level (the sandwich estimator is implemented,
callable, correctly clustered at `idorighh`, with the score sign
convention and meat symmetry verified). This memo is the third
precondition: the separate pooled-estimation authorization.

The memo is precise about what the estimation produces and what it
does not. It produces the first pooled preference point estimates —
the 55-parameter vector estimated across the three survey years
FR_2015, FR_2016, FR_2017 — together with the Hessian-based and
cluster-robust standard errors and the post-estimation diagnostics.
It does not produce a final, defensible, reportable pooled baseline:
that requires the post-estimation cluster-robust diagnostics (the
full 9,657-cluster confirmation, the robust-SE positivity, the
robust-versus-Hessian comparison) to confirm the inference validity,
and then a separate SA2 verdict to determine whether the pooled
specification is accepted and whether it displaces M1-clean.

The memo carries forward two limitations from the upstream gates. The
GA15 income rule (§6, §7): singles use `ils_dispy_real`, couples use
`ils_dispy_male` / `ils_dispy_female`, and no downstream step may
assume the scalar `ils_dispy_real` covers couples. The GA17
limitation (§7, §14): the cluster-robust SE infrastructure is
confirmed callable at the smoke-test level with a dummy Hessian, but
its inference validity must be confirmed after convergence using the
true Hessian and the converged theta. Both limitations are binding
constraints on the estimation and its diagnostics.

The single-year M1-clean 2016 specification remains the active JMP
baseline throughout the estimation and until a future SA2 verdict on
the estimated pooled specification determines otherwise (§17).

---

## 2. Current status

The current status is that the pooled estimation is fully gated-in
for execution: the specification exists and is validated, the data
input is the final non-provisional pooled dataset, the cluster-robust
SE infrastructure is implemented and callable, and the three
preconditions for execution are met.

The pooled specification `ruro_occ_P3a_pooled` exists as
`scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`,
with 55 parameters (53 M1-clean + 2 year dummies), parsing without
error, and all M1-clean frozen blocks byte-identical (Gate-A parse
report §2, §3). The pooled data input
`Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` is the
final non-provisional GSURv2 opportunity-year-aligned pooled dataset
(construction verdict PASS; 1,244,500 rows; 12,445 household-years;
9,657 unique clusters). The cluster-robust SE infrastructure is
implemented (`cluster_robust_se.py`, `run_cluster_robust_se.py`, and
the engine extensions) and confirmed callable at the smoke-test level
(GA17 clearance addendum).

The estimation has not been run. No pooled parameter estimate exists;
the pooled specification has not been fit to the data. The provisional
M1-clean single-year estimates (LL = −6487.55 on FR_2016) are the only
estimated structural parameters; the pooled estimation produces the
first multi-year estimates. The estimation is the next authorised
step, and this memo authorises it.

---

## 3. Evidence that Gate-A has passed

**Gate-A has passed for pre-estimation authorization purposes.**

The Gate-A parse report returned PASS WITH BLOCKER: GA1 through GA16
all passed, and GA17 was PENDING (the cluster-robust SE infrastructure
did not exist). GA1–GA16 confirmed the pooled YAML and data input are
structurally valid: the YAML exists and parses (GA1, GA2), the
specification name is `ruro_occ_P3a_pooled` (GA3), the parameter count
is 55 (GA4), the two year dummies are present with initial value 0.0,
bounds [−5.0, 5.0], `applies_to: household`, and `interaction:
["working"]` (GA5–GA10), all M1-clean frozen blocks are byte-identical
(GA11), `beta_E_gsur` and the seven region dummies are present and
unchanged (GA12), the year indicators construct on both household
types (GA13), the GSUR columns are complete for the active sample
(GA14), the CPI/real-income check passes with the documented singles-
only `ils_dispy_real` note (GA15), and the cluster key satisfies
`cluster_id == idorighh` on the bounded sample (GA16).

The GA17 clearance addendum cleared the GA17 blocker at the smoke-
test-callability level (§4) and updated the Gate-A status from PASS
WITH BLOCKER to **PASS for pre-estimation authorization purposes.**
The Gate-A PASS confirms the static validation gate is fully cleared:
the pooled YAML is structurally valid, the pooled data input is
structurally valid, and the cluster-robust SE infrastructure is
implemented and callable. This is the first of the three preconditions
the Gate-A parse report established for pooled estimation execution,
and it is met.

The Gate-A PASS is qualified "for pre-estimation authorization
purposes" precisely because it does not certify the inference validity
of the cluster-robust SEs, which belongs to the post-estimation stage
(§7, §14). The estimation this memo authorises is the step that
produces the converged theta and the true Hessian needed for that
post-estimation certification.

---

## 4. Evidence that GA17 smoke-test callability has been confirmed

**GA17 smoke-test callability is CONFIRMED.**

The GA17 clearance addendum confirmed the cluster-robust SE
infrastructure at the smoke-test-callability level. The infrastructure
is implemented (the sandwich library `cluster_robust_se.py`, the CLI
`run_cluster_robust_se.py`, the `cluster_ids` field on the precomputed
data objects, and the `return_scores` mode and `compute_scores_joint`
function in the engine), and all seventeen static/smoke checks
(C1–C17) pass (static validation report). Three substantive
correctness properties are verified at the smoke-test stage: the score
sign convention is correct (T1: the per-group scores sum to the
gradient of the positive log-likelihood, max abs diff 5.82×10⁻¹⁰), the
meat matrix is symmetric (T2), and the sandwich is callable at initial
values returning finite output (T6, with a dummy Hessian).

The clearance is strictly scoped. It confirms the infrastructure is
implemented, callable, correctly clustered at `idorighh`, with the
draw-expanded rows handled at the choice-set level (not as independent
clusters) and the singles/couples income paths kept separate. It does
not confirm the post-estimation robust-SE diagnostics — the full-
dataset 9,657-cluster confirmation (T3), the SE-positivity check (T4),
and the robust-versus-Hessian comparison (T5) — which require the
converged theta and the true Hessian and remain mandatory post-
estimation checks (§14).

The GA17 clearance is the second of the three preconditions the
Gate-A parse report established for pooled estimation execution, and
it is met at the level the pre-estimation gate requires. The GA17
limitation — that the smoke-test clearance used a dummy Hessian and
must be re-confirmed with the true Hessian after convergence — is
carried forward as a binding constraint on the post-estimation
diagnostics (§7, §14).

---

## 5. Pooled estimation specification

**Specification: `ruro_occ_P3a_pooled` (55 free parameters).**

The estimation fits the pooled specification
`ruro_occ_P3a_pooled`, defined in
`scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`.
The specification is the M1-clean single-year specification (53
parameters) extended by two year-dummy shifters in the market-
opportunity index, for 55 parameters.

The 55 parameters are (Gate-A parse report §3): the 12 singles
preference parameters (positions 1–12), the 9 couples preference
parameters (positions 13–21), the household consumption and
employment shifters `beta_c` and `beta_E` (positions 22–23), the 3
hours-opportunity shifters (positions 24–26), the GSUR loading
`beta_E_gsur` (position 27), the 7 region dummies
`beta_E_drgn2`–`beta_E_drgn8` (positions 28–34), the **2 new year
dummies** `beta_E_y2015` and `beta_E_y2017` (positions 35–36, the
pooled extension), the 12 occupation shifters (positions 37–48), the
6 wage/Mincer parameters including `sigma` (positions 49–54), and the
household leisure interaction `beta_ll` (position 55).

The two year dummies are the only structural addition relative to
M1-clean: `beta_E_y2015` (variable `year_2015_indicator = (year_tag ==
1)`) and `beta_E_y2017` (variable `year_2017_indicator = (year_tag ==
3)`), both entering the market-opportunity index, both `applies_to:
household`, both interacting with `["working"]`, with FR_2016 as the
omitted reference year. The fixed parameter `theta_c` (couples Box-Cox
consumption exponent, fixed at 0.0) is absent from the 55-parameter
vector, consistent with M1-clean.

The specification is frozen for this estimation. The estimation does
not modify the specification; it fits the existing 55-parameter YAML.
No specification change is authorised by this memo.

---

## 6. Pooled data input

**Input: `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`.**

The estimation reads the final non-provisional GSURv2 opportunity-
year-aligned pooled dataset. Its properties (construction verdict;
design memo §5): 1,244,500 draw-expanded rows; 12,445 household-years
(5,007 singles, 7,438 couples); 100 draws per household-year; 9,657
unique `idorighh` clusters; survey years FR_2015, FR_2016, FR_2017
with opportunity years y2014, y2015, y2016; provisioning label
`gsurv2_opportunity_year_aligned`; CPI base year 2016. The active GSUR
columns carry the GSURv2 opportunity-year-aligned rates: `gsur` for
singles, `gsur_male` / `gsur_female` for couples.

The estimation must use the harmonised parquet, not the stacked-raw
parquet (the harmonised parquet is the CPI-deflated version; the
stacked-raw parquet is pre-deflation and must not be used as the
estimation input).

**GA15 income rule (binding).** The income handling is carried forward
from the GA15 structural note and the GA17 clearance: singles
consumption derives from `ils_dispy_real` (the CPI-deflated scalar
column, non-null for the 500,700 singles rows, null for couples);
couples consumption derives from `ils_dispy_male` and
`ils_dispy_female` (the gender-specific CPI-deflated columns). The
scalar `ils_dispy_real` column is singles-only; no step in the
estimation or its diagnostics may assume `ils_dispy_real` covers
couples rows. The estimation engine must read `ils_dispy_real` for
singles and `ils_dispy_male` / `ils_dispy_female` for couples,
matching the M1-clean engine behaviour, and the estimation report
must confirm this income routing explicitly (§13).

The pooled parquet is read-only for the estimation. The estimation
does not modify the parquet; it reads the columns it requires and
fits the specification.

---

## 7. Cluster-robust inference requirement

**The pooled estimation must produce cluster-robust standard errors at
`cluster_id = idorighh`. The unadjusted Hessian-based SEs are computed
as a diagnostic comparison only; the cluster-robust SEs are the
reported inference.**

The clustering is required because the pooled dataset contains within-
cluster correlation that invalidates the Hessian-based (i.i.d.) SEs
(design memo §15). Two sources: the household-level correlation across
years (the 2,788 households appearing in both FR_2016 and FR_2017
contribute correlated observations within the `idorighh` cluster), and
the draw-level correlation within household-years (the 100 draws per
household-year are correlated by construction). The sandwich estimator
at `idorighh` handles both: it clusters at the cross-year household
level and sums score contributions across all of a household's
household-year appearances and draws before forming the meat matrix.

The cluster-robust SEs are computed using the GA17 infrastructure
(`compute_scores_joint` and `compute_cluster_robust_se`) after each
converged start (§8, §14). The sandwich is V = H⁻¹ B H⁻¹, where H is
the true Hessian at the converged theta (not the dummy Hessian used in
the smoke test) and B is the meat matrix summed over the 9,657
`idorighh` clusters.

**GA17 limitation (binding).** The cluster-robust SE infrastructure is
confirmed callable at the smoke-test level with a dummy Hessian H =
0.1·I at initial values (§4). The smoke-test clearance does not confirm
the inference validity of the cluster-robust SEs. After each start
converges, the cluster-robust SEs must be computed with the **true
Hessian** (the numerical second derivative of the negative log-
likelihood at the **converged theta**), and the post-estimation
diagnostics (§14) must confirm: the full-dataset 9,657-cluster count
(T3), the robust-SE positivity for all free parameters (T4), and the
robust-versus-Hessian comparison (T5). The smoke-test clearance is not
a substitute for these post-estimation checks; the cluster-robust SEs
are not inference-valid until the post-estimation diagnostics confirm
them on the converged fit.

**Cluster-key strictness (binding).** The estimation must cluster at
`idorighh`, not `idhh`. The cluster-key strictness safeguard
(implemented in `precompute_data_singles` and `precompute_data_couples`)
must be active: if `idorighh` is absent, the run must not silently fall
back to `idhh`. The estimation report must confirm that `idorighh` was
used as the cluster key and that the silent `idhh` fallback was not
invoked (§13).

---

## 8. Starts to run

**Three independent starts.** The estimation runs three independent
optimisation starts, each producing a converged parameter vector, an
objective value, and (after convergence) cluster-robust SEs. The three
starts test the robustness of the optimum to the starting point and
provide the multistart convergence evidence the SA2 verdict requires.

(Start 1) **Warm from M1-clean.** The 53 M1-clean parameter values are
transferred to the pooled starting vector, with the two new year-effect
parameters `beta_E_y2015` and `beta_E_y2017` initialised at 0.0. The
M1-clean estimates provide a near-optimal starting point for the shared
structural parameters (§9).

(Start 2) **Spec defaults.** All 55 parameters are initialised at the
YAML-specified `initial_values` (the same defaults used in M1-clean's
Start 2). This provides an independent check against the Start 1
convergence, starting from the specification defaults rather than the
M1-clean optimum.

(Start 3) **Perturbed warm start.** A random perturbation (seed 42,
magnitude ±0.1) is applied to the Start 1 vector. This tests the
sensitivity of the optimum to the warm-start neighbourhood.

Each start runs to convergence under the solver and vectorised mode
(§10), and the cluster-robust SE computation (§7, §14) is run after
each start converges. The three starts' convergence and agreement are
the basis for the S1 SA2 criterion (§15).

---

## 9. Warm-start strategy

**Start 1 warms from the M1-clean FR_2016 estimates; the two year
dummies start at 0.0.**

The warm-start strategy transfers the converged M1-clean parameter
values to the shared structural parameters of the pooled vector. The 53
M1-clean parameters (the preference block, the hours/wage/occupation
opportunity blocks, `beta_E`, `beta_E_gsur`, the seven region dummies,
`beta_ll`) are mapped one-to-one to their pooled counterparts (the
pooled positions 1–34 and 37–55 correspond to the M1-clean positions
1–53, per the Gate-A parse report §3). The two new year dummies
`beta_E_y2015` and `beta_E_y2017` (pooled positions 35–36) are
initialised at 0.0, the value that corresponds to no year effect (the
FR_2016 reference).

The warm-start rationale is that the M1-clean optimum is a near-optimal
starting point for the pooled shared parameters: the pooled
specification re-estimates the M1-clean model on the three-year panel
with year controls, and if the structural parameters are stable across
years (the JMP's central claim), the pooled optimum is close to the
M1-clean optimum. Starting Start 1 at the M1-clean optimum therefore
gives the optimiser a strong initial point and makes the convergence
fast and reliable. The 0.0 initialisation of the year dummies starts
them at the no-effect value, so Start 1 begins at the M1-clean optimum
embedded in the pooled parameter space with zero year effects.

Start 3 perturbs this warm start (seed 42, ±0.1) to test the optimum's
stability; Start 2 starts from the spec defaults independently. The
three starts together confirm whether the pooled optimum is robust to
the starting point (the S1 criterion, §15).

---

## 10. Solver and vectorized mode

**Solver: `--solver gamspy-conopt --vectorized`, subject to the local
CLI's exact syntax.**

The estimation runs with the GAMSPy-CONOPT solver in vectorised mode,
the same solver and mode used for the M1-clean single-year estimation.
The intended invocation is
`--solver gamspy-conopt --vectorized`, using the
`.venv\Scripts\python.exe` interpreter.

**CLI-syntax confirmation (binding).** If the local estimation CLI
requires a different exact syntax for the solver and vectorised mode
(for instance, a different flag name, a config-file option, or a
different solver string), the estimation must use the exact syntax the
local CLI requires, and the estimation report must document the exact
invocation used (§13). The estimation must not be run with a solver or
mode that differs from the M1-clean estimation's solver and mode
without documenting the difference; the SA2 comparison (§15) requires
that the pooled estimation uses the same estimation machinery as the
M1-clean baseline, so any solver or mode difference must be recorded
and its implications for the comparison noted.

The vectorised mode is required for the runtime to be tractable on the
1,244,500-row pooled dataset (§11); the non-vectorised mode would be
substantially slower. The estimation must confirm that the vectorised
mode is active.

---

## 11. Expected runtime

**Approximately 1,000–2,100 seconds per start; 3,000–6,300 seconds for
the three-start protocol.**

The pooled dataset is 1,244,500 rows, approximately 2.93× the FR_2016
single-year size (425,300 rows). If the estimator vectorises across
draws, the walltime scales sub-linearly with the row count; the design
memo §14 estimates 3–6× the single-year per-start walltime, or
approximately 1,000–2,100 seconds per start. The three-start protocol
therefore requires approximately 3,000–6,300 seconds of compute.

The cluster-robust SE computation after each start is negligible in
runtime (the meat assembly over 9,657 clusters is approximately 29 M
FLOPs, under 1 ms; the bread is the Hessian already computed for the
Hessian-based SEs; implementation report §15). The runtime is dominated
by the three optimisation starts, not by the SE computation.

The runtime estimate is a planning figure, not a halt condition; a
start that runs longer is not a failure provided it converges (§18). A
start that fails to converge within a reasonable iteration budget is a
halt condition (§18 H3).

---

## 12. Required outputs

The estimation produces the following outputs, written to a versioned
results directory (not a canonical path; §17).

(Out1) **The three per-start estimation results.** For each start: the
converged 55-parameter vector, the objective value (log-likelihood),
the convergence status, the iteration count, and the solver return
status. Persisted to per-start results JSON files.

(Out2) **The Hessian-based standard errors.** For each converged start:
the numerical Hessian at the converged theta, the Hessian-based SEs
(the diagonal of H⁻¹), and the free-parameter mask. Persisted alongside
the per-start results.

(Out3) **The cluster-robust standard errors.** For each converged
start: the cluster-robust SEs (the sandwich V = H⁻¹ B H⁻¹ at the true
Hessian and converged theta), the cluster-robust variance-covariance
matrix, and the cluster count used in the meat assembly. Persisted
alongside the per-start results (§14).

(Out4) **The estimation report.** A report
(`Results/JMP_pooled_P3a_estimation_report_v1.md` or equivalent)
recording the estimation execution, the per-start results, the post-
estimation diagnostics (§13), and the readiness of the SA2 verdict.

The outputs are written to a versioned path. No canonical promotion of
any output is authorised (§17). The pooled estimation outputs are
candidate results pending the SA2 verdict, not final reportable
results.

---

## 13. Required post-estimation diagnostics

The estimation must produce the following post-estimation diagnostics
before any SA2 verdict is considered. The diagnostics are mandatory:
the SA2 verdict requires the complete diagnostic set, and no SA2
verdict may be issued until the diagnostics are complete (§15).

(D1) **Convergence status by start.** For each of the three starts:
converged / not converged, the solver return status, and the iteration
count.

(D2) **Objective value by start.** For each start: the converged log-
likelihood. The three values must agree within the S1 tolerance (§15).

(D3) **Parameter vector comparison across starts.** The L∞ distance
between the three converged parameter vectors, parameter by parameter,
confirming agreement within the S1 tolerance (0.01 absolute).

(D4) **Year-effect estimates and signs.** The `beta_E_y2015` and
`beta_E_y2017` point estimates, their cluster-robust SEs, t-statistics,
p-values, and signs. The magnitudes are checked against the SA2-
REVISION threshold (§15).

(D5) **GSUR coefficient estimate and sign.** The `beta_E_gsur` point
estimate, its cluster-robust SE, t-statistic, p-value, and sign,
compared to the M1-clean estimate (−1.329, SE 0.163, t = −8.15). The
sign and magnitude are checked against the SA2 criteria S2 and S3 (§15).

(D6) **Region-dummy stability.** The seven `beta_E_drgn2`–`beta_E_drgn8`
point estimates and their cluster-robust SEs, the joint Wald test on
the seven dummies using the cluster-robust VCV sub-block (W statistic,
d.f. = 7, p-value, compared to M1-clean W = 28.18, p = 0.0002), and the
directional consistency with M1-clean.

(D7) **Hessian condition and invertibility.** The Hessian condition
number, the minimum and maximum eigenvalues, the number of near-zero
(<1) and negative eigenvalues, compared to M1-clean (condition number
5.10×10¹⁰, 3 negative-diagonal entries in the singles-consumption sub-
block). The singles-consumption sub-block eigenvalue check is carried
forward (the three near-singular parameters `beta_c_sm`, `beta_c_sf`,
`theta_c_singles`).

(D8) **Cluster-robust SE availability.** Confirmation that the cluster-
robust SEs were computed for all three starts using the GA17
infrastructure, with the true Hessian and the converged theta.

(D9) **Full 9,657-cluster confirmation (T3).** Confirmation that the
meat-matrix assembly aggregated over exactly 9,657 unique `idorighh`
clusters on the full dataset (not the bounded smoke-test sample). This
is the post-estimation completion of the deferred T3 check.

(D10) **Robust-SE positivity (T4).** Confirmation that the cluster-
robust SEs are strictly positive for all free parameters at the
converged theta with the true Hessian. This is the post-estimation
completion of the deferred T4 check.

(D11) **Robust-versus-Hessian comparison (T5).** For each of the 55
parameters, the Hessian-based SE and the cluster-robust SE, with the
ratio cluster-robust/Hessian. Any parameter where the robust SE is
smaller than the Hessian SE is flagged for review (clustering normally
inflates SEs when within-cluster correlation is present). This is the
post-estimation completion of the deferred T5 check.

(D12) **Income-routing confirmation.** Confirmation that the estimation
read `ils_dispy_real` for singles and `ils_dispy_male` /
`ils_dispy_female` for couples (the GA15 income rule, §6), and that no
step assumed the scalar `ils_dispy_real` covers couples.

(D13) **Cluster-key confirmation.** Confirmation that the cluster key
was `idorighh` and that the silent `idhh` fallback was not invoked (the
cluster-key strictness safeguard, §7).

(D14) **No-welfare confirmation.** Confirmation that no welfare
computation was run during the estimation.

(D15) **M1-clean-active confirmation.** Confirmation that M1-clean
remains the active JMP baseline pending the SA2 verdict, and that the
pooled estimation did not promote or canonicalise any output.

The diagnostics D9, D10, D11 are the post-estimation completion of the
deferred GA17 diagnostics (T3, T4, T5); they are the inference-validity
confirmation that the GA17 smoke-test clearance explicitly did not
provide. They are mandatory before the SA2 verdict.

---

## 14. Required cluster-robust SE outputs

The cluster-robust SE outputs are the inference deliverable of the
pooled estimation, computed with the true Hessian after each start
converges.

For each converged start, the estimation must compute and persist:

(R1) **The cluster-robust variance-covariance matrix.** The sandwich
V = H⁻¹ B H⁻¹, where H is the numerical Hessian of the negative log-
likelihood at the converged theta (the **true Hessian**, not the dummy
Hessian of the smoke test), and B is the meat matrix summed over the
9,657 `idorighh` clusters.

(R2) **The cluster-robust standard errors.** The square roots of the
diagonal of the cluster-robust VCV, with zero SE assigned to
fixed/bounded parameters via the free-parameter mask.

(R3) **The cluster count used in the meat assembly.** Confirmed to be
9,657 on the full dataset (D9 / T3).

(R4) **The Hessian-based standard errors, for comparison.** The
diagonal of H⁻¹, computed as the diagnostic comparison (D11 / T5). The
cluster-robust SEs are the reported inference; the Hessian-based SEs
are labelled as the diagnostic comparison.

The cluster-robust SE computation must use the GA17 infrastructure
(`compute_scores_joint` to extract the per-cluster scores and
`compute_cluster_robust_se` to assemble the sandwich), invoked in the
post-estimation mode of `run_cluster_robust_se.py` with the converged
theta from the estimation results JSON. The smoke-test mode (dummy
Hessian, initial values) is not used for the inference; the post-
estimation mode with the true Hessian and converged theta is required.

The cluster-robust SE outputs complete the deferred GA17 diagnostics.
The GA17 smoke-test clearance confirmed the infrastructure is callable;
these outputs confirm the infrastructure produces inference-valid SEs
on the converged fit. The two are distinct: the smoke-test clearance is
a callability confirmation, and these outputs are the inference-validity
confirmation. Both are required for the SA2 verdict.

---

## 15. SA2 verdict requirements

**No SA2 verdict is issued by this memo or by the estimation. The SA2
verdict is a separate adjudication, issued after the estimation and the
complete post-estimation diagnostics, against the SA2 criteria.**

The SA2 verdict is the pooled counterpart of the M1-clean SA1 verdict.
It determines whether the pooled specification is accepted (SA2-STANDS),
accepted with qualification (SA2-QUALIFIED), requires revision (SA2-
REVISION), or is rejected (SA2-FAIL), and whether the pooled
specification displaces M1-clean as the active JMP baseline.

The SA2 verdict requires the complete post-estimation diagnostics
(§13), including the inference-validity confirmations D9 (full 9,657-
cluster count), D10 (robust-SE positivity), and D11 (robust-versus-
Hessian comparison). The SA2-STANDS criteria (design memo §21,
carried forward):

- S1: all three starts converge to the same LL within 1 unit and
  parameter vectors within 0.01 (D1, D2, D3).
- S2: pooled `beta_E_gsur` significant at p < 0.01 under cluster-robust
  SEs (D5).
- S3: pooled `beta_E_gsur` within 50% of the M1-clean magnitude
  (−1.329) (D5).
- S4: region-dummy joint Wald test p < 0.01 under cluster-robust SEs
  (D6).
- S5: GSUR-region Hessian sub-block has no negative eigenvalues (D7).
- S6: preference block maximum |Δ| < 10% relative to M1-clean (D7 /
  parameter comparison).
- S7: `beta_ll` remains strongly positive (t > 5, cluster-robust).
- S8: no new negative-diagonal Hessian entries beyond M1-clean's 3 (D7).
- S9: Gate-A GA1–GA17 all clear (met: Gate-A PASS + GA17 cleared).
- S10: participation fit — no group-year regresses by more than 2 pp
  relative to M1-clean FR_2016.
- S11: mean-hours fit — no group-year mean-hours regression exceeds 0.5
  hours relative to M1-clean FR_2016.

The SA2-STANDS criteria require the cluster-robust SEs (S2, S4, S7),
which require the post-estimation cluster-robust diagnostics (§14). The
SA2 verdict therefore cannot be issued until the estimation has run and
the post-estimation diagnostics, including the inference-validity
confirmations, are complete. The SA2 verdict is a separate document,
not authorised or pre-empted by this execution authorization.

---

## 16. What is authorized

The memo authorises the following, and only the following.

(A1) **Running the three-start pooled estimation** of
`ruro_occ_P3a_pooled` (§5) on the harmonised pooled parquet (§6) under
the solver and vectorised mode (§10), producing the three converged
parameter vectors and objective values (§8, §9).

(A2) **Computing the Hessian-based and cluster-robust standard errors**
after each converged start, using the true Hessian and the GA17
infrastructure in post-estimation mode (§7, §14).

(A3) **Producing the post-estimation diagnostics** (§13), including the
inference-validity confirmations (D9 full cluster count, D10 robust-SE
positivity, D11 robust-versus-Hessian comparison).

(A4) **Writing the estimation outputs** (§12) to a versioned results
directory, with the estimation report.

The authorised steps are the pooled estimation execution and its post-
estimation diagnostics. They do not extend to the SA2 verdict, welfare,
canonical promotion, or M1-clean displacement.

---

## 17. What is not authorized

The memo does not authorise the following. Each is separately gated.

(N1) **The SA2 verdict.** The SA2 verdict is a separate adjudication,
issued after the estimation and the complete post-estimation
diagnostics (§15). This memo authorises the estimation and the
diagnostics; it does not issue or pre-empt the SA2 verdict.

(N2) **Welfare computation.** No welfare implementation or computation
is authorised. Welfare computation requires an accepted SA2 verdict on
the pooled specification and a separate welfare-computation
authorization. The estimation must not run any welfare computation
(D14).

(N3) **Canonical promotion.** No canonical promotion of the pooled
specification, the pooled estimates, or any pooled output is
authorised. The outputs are written to a versioned path and are
candidate results pending the SA2 verdict.

(N4) **M1-clean displacement.** The pooled estimation does not displace
M1-clean. M1-clean 2016 remains the active JMP baseline until a future
SA2 verdict explicitly promotes the pooled specification (D15). The
pooled estimates are candidate results; they do not become the active
baseline by being estimated.

(N5) **Specification modification.** The estimation does not modify the
pooled specification, the M1-clean specification, or the M1-naive
specification. It fits the existing 55-parameter pooled YAML.

(N6) **Alternative pooled specifications.** The year-interacted GSUR,
year-interacted preferences, and other alternative pooled
specifications are post-SA2 sensitivities, not authorised by this memo.

The not-authorised steps are everything downstream of the estimation
and its diagnostics. The estimation produces candidate pooled estimates
with cluster-robust inference; the SA2 verdict, welfare, canonical
promotion, and M1-clean displacement remain gated.

---

## 18. Halt conditions

The estimation halts under the following conditions. Each halt
preserves the outputs produced up to the halt and requires diagnosis
before the estimation proceeds.

(H1) **Cluster key not `idorighh`.** If the estimation cannot use
`idorighh` as the cluster key — if `idorighh` is absent and the run
would fall back to `idhh` — the estimation halts. The cluster-key
strictness safeguard must prevent the silent fallback (§7); a halt here
indicates the safeguard fired correctly and the input must be
corrected.

(H2) **Income routing wrong.** If the estimation engine reads
`ils_dispy_real` for couples rows (which are null) or otherwise
violates the GA15 income rule (§6), the estimation halts: the income
routing is incorrect and would corrupt the couples consumption.

(H3) **Start fails to converge.** If a start fails to converge within a
reasonable iteration budget, or returns a solver error, the estimation
records the failure and halts that start. The multistart protocol
requires all three starts to converge for the S1 criterion; a
non-converging start is recorded and diagnosed.

(H4) **Cluster-robust SE computation fails.** If the post-estimation
cluster-robust SE computation fails — if the meat assembly does not
aggregate over 9,657 clusters (D9 / T3 fails), if a robust SE is not
positive for a free parameter (D10 / T4 fails), or if the sandwich
computation errors — the estimation records the failure and halts
before the SA2 verdict. The cluster-robust SEs are the reported
inference; a failure in their computation is a halt.

(H5) **Welfare or canonical step attempted.** If the estimation would
run any welfare computation or promote any output to a canonical path,
the estimation halts: these are not authorised (§17).

(H6) **Specification modification attempted.** If the estimation would
modify the pooled, M1-clean, or M1-naive specification, the estimation
halts (§17 N5).

The halt conditions are protective. The most consequential are H1
(cluster key) and H2 (income routing), which guard against the two
silent errors that would corrupt the inference or the couples
consumption, and H4 (cluster-robust SE computation), which guards
against an SA2 verdict being considered on incomplete or invalid
inference.

---

## 19. Exact Claude Code estimation prompt

The following prompt initiates the pooled estimation in Claude Code
Sonnet. The prompt executes the authorised estimation (§16) under the
halt conditions (§18) and produces the estimation report with the post-
estimation diagnostics (§13).

Tool path: Claude Code Sonnet (local codebase, pooled estimation).

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present: the pooled YAML
(`estimation_spec_ruro_occ_P3a_pooled.yaml`); the harmonised pooled
parquet (`fr_p3a_gsurv2_harmonised.parquet`); the M1-clean estimates
(for the warm start); the cluster-robust SE infrastructure
(`cluster_robust_se.py`, `run_cluster_robust_se.py`, the engine
extensions); and this execution authorization.

Prompt to use:

> Execute the pooled P3a estimation per
> `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md`. Use
> the interpreter `.venv\Scripts\python.exe`. Do NOT compute welfare.
> Do NOT promote any output to a canonical path. Do NOT modify the
> pooled, M1-clean, or M1-naive specifications. Do NOT issue an SA2
> verdict.
>
> Estimate `ruro_occ_P3a_pooled`:
> - Spec:
>   `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
>   (55 parameters).
> - Data:
>   `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`.
> - Cluster key: `cluster_id = idorighh`. Confirm `idorighh` is used
>   and the silent `idhh` fallback is NOT invoked; HALT if it would be.
> - Income routing (GA15): singles use `ils_dispy_real`; couples use
>   `ils_dispy_male` / `ils_dispy_female`. Confirm this routing; HALT
>   if `ils_dispy_real` is read for couples.
>
> Run three starts with `--solver gamspy-conopt --vectorized` (if the
> local CLI requires a different exact syntax for solver/vectorised
> mode, use it and DOCUMENT the exact invocation):
> 1. Warm from M1-clean: transfer the 53 M1-clean parameter values;
>    set `beta_E_y2015 = 0.0` and `beta_E_y2017 = 0.0`.
> 2. Spec defaults: all 55 parameters at the YAML `initial_values`.
> 3. Perturbed warm start: Start 1 vector perturbed by ±0.1, seed 42.
>
> After each start converges, compute cluster-robust SEs using the GA17
> infrastructure in post-estimation mode (`run_cluster_robust_se.py
> --mode post-estimation` with the converged theta and the TRUE Hessian
> — NOT the dummy Hessian of the smoke test).
>
> Produce the post-estimation diagnostics: convergence status by start;
> objective value by start; parameter-vector comparison across starts;
> year-effect estimates and signs; GSUR coefficient estimate and sign
> (vs M1-clean −1.329); region-dummy stability and joint cluster-robust
> Wald test; Hessian condition/invertibility (incl. the singles-
> consumption sub-block); cluster-robust SE availability; FULL 9,657-
> cluster confirmation (T3 on the full dataset); robust-SE positivity
> (T4); robust-vs-Hessian comparison (T5); income-routing confirmation;
> cluster-key confirmation; no-welfare confirmation; M1-clean-active
> confirmation.
>
> HALT conditions: cluster key not `idorighh`; income routing wrong; a
> start fails to converge; cluster-robust SE computation fails (T3 not
> 9,657, T4 not positive, or sandwich error); any welfare or canonical
> step; any specification modification.
>
> Save the estimation report as
> `Results/JMP_pooled_P3a_estimation_report_v1.md`, recording the per-
> start results, the Hessian-based and cluster-robust SEs, all post-
> estimation diagnostics, the exact solver invocation used, any halt and
> diagnosis, and the readiness of the SA2 verdict. Write all outputs to
> a versioned path. Do NOT compute welfare. Do NOT promote canonically.
> Do NOT issue an SA2 verdict.

Output to save: the estimation report at
`Results/JMP_pooled_P3a_estimation_report_v1.md`, with the per-start
results, SEs, and diagnostics.

What to do next: return the estimation report to the project chat for
the SA2 verdict. The SA2 verdict is a separate adjudication against the
SA2 criteria (§15), requiring the complete post-estimation diagnostics
including the inference-validity confirmations (D9, D10, D11). If the
estimation halts — particularly on H1 (cluster key), H2 (income
routing), or H4 (cluster-robust SE computation) — the report informs
the diagnosis. Welfare, canonical promotion, and M1-clean displacement
remain gated and are not authorised by this estimation.

---

**Required final statements**

- **The pooled P3a estimation execution is authorized** for the three-
  start estimation of `ruro_occ_P3a_pooled` on the harmonised pooled
  parquet, with cluster-robust SEs at `idorighh`, subject to the GA15
  income rule and the GA17 limitation.

- **Post-estimation diagnostics are mandatory before any SA2 verdict.**
  The full 9,657-cluster confirmation (T3), the robust-SE positivity
  (T4), and the robust-versus-Hessian comparison (T5) — the inference-
  validity confirmations the GA17 smoke-test clearance deferred — must
  be completed on the converged fit with the true Hessian before the
  SA2 verdict.

- **Welfare computation is NOT authorized.** Separately gated behind an
  accepted SA2 verdict.

- **Canonical promotion is NOT authorized.** The pooled estimates are
  candidate results written to a versioned path.

- **M1-clean 2016 remains the active JMP baseline.** The pooled
  estimation produces candidate results; M1-clean is displaced only by
  a future SA2 verdict that explicitly promotes the pooled
  specification.
