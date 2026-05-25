# RURO occ P3a Pooled — GA17 Clearance Addendum v1

Date: 2026-05-21

Addendum to: `Results/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md`
(the Gate-A parse report that returned PASS WITH BLOCKER, GA1–GA16
PASS, GA17 PENDING).

Object of clearance: GA17 — the cluster-robust standard-error
infrastructure that the Gate-A parse report identified as the
blocker between Gate-A and the pooled-estimation authorization memo.

Primary evidence:
- `docs/estimation/RURO_cluster_robust_SE_design_audit_v1.md` (the design audit
  specifying the sandwich estimator and the T1–T6 validation tests)
- `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md` (the
  implementation report)
- `docs/estimation/RURO_cluster_robust_SE_implementation_correction_v1.md` (the
  implementation correction applying the GA17-wording, C2-check, and
  cluster-key-strictness fixes)
- `Results/RURO_cluster_robust_SE_static_validation_v1.md` (the
  regenerated static/smoke validation report, C1–C17)

Governing documents:
- `docs/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md` (the Gate-A
  parse report under addendum)
- `docs/JMP_pooled_P3a_estimation_design_memo_v1.md` and its
  correction (the pooled design, including the corrected GA17 verdict
  semantics)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  baseline)

Interpreter of record: `.venv\Scripts\python.exe`.

Scope of addendum: the addendum adjudicates whether GA17 is cleared,
strictly distinguishing the GA17 smoke-test callability clearance
from the full post-estimation robust-SE diagnostics (T4, T5, and the
full-dataset T3), and updates the Gate-A status accordingly. The
addendum does not authorise pooled estimation or welfare computation;
those steps are separately gated.

---

## 1. Purpose

The purpose of this addendum is to adjudicate the GA17 clearance
following the implementation of the cluster-robust standard-error
infrastructure, and to update the Gate-A status. The Gate-A parse
report returned PASS WITH BLOCKER: GA1–GA16 passed, but GA17 was
PENDING because no cluster-robust sandwich estimator clustered at
`idorighh` existed in the estimation engine. The cluster-robust SE
infrastructure has now been implemented, corrected, and statically
validated.

The addendum makes one clearance decision under a strict scope
distinction. It clears GA17 at the level the GA17 check actually
requires at the pre-estimation stage — smoke-test callability: the
score-extraction, meat-assembly, and sandwich-covariance interfaces
are implemented and callable on the pooled parquet at initial values,
with the sign convention and the meat symmetry verified. It does not
clear, and explicitly does not claim, the full post-estimation
robust-SE diagnostics (the SE-positivity check T4, the robust-versus-
Hessian comparison T5, and the full-dataset cluster-count
confirmation T3), which require the converged parameter vector and
the true Hessian and remain post-estimation checks.

The distinction is the addendum's central discipline. The GA17 check,
under the corrected Gate-A verdict semantics, is a pre-estimation
infrastructure-callability gate: it asks whether the cluster-robust SE
machinery exists and is callable, not whether the cluster-robust SEs
are numerically validated for inference. The latter requires
estimation to have run. The addendum clears GA17 at the callability
level and records the post-estimation diagnostics as deferred.

With GA17 cleared at the smoke-test-callability level, the Gate-A
status is updated from PASS WITH BLOCKER to PASS for pre-estimation
authorization purposes (§13). This update licenses the drafting of
the pooled-estimation authorization memo (§14); it does not authorise
pooled estimation execution, which remains gated behind that separate
memo. The single-year M1-clean 2016 specification remains the active
JMP baseline (§15).

---

## 2. Previous Gate-A status

The Gate-A parse report returned **PASS WITH BLOCKER**. GA1 through
GA16 all passed (GA15 with a documented structural note on the
singles-only `ils_dispy_real` column), confirming that the pooled YAML
(`estimation_spec_ruro_occ_P3a_pooled.yaml`, 55 parameters, parsing
correctly, all M1-clean frozen blocks byte-identical) and the pooled
data input (year-tag construction, GSUR completeness, CPI/real-income,
cluster-key) are structurally valid.

GA17 returned PENDING. The parse report's §6 established, by grep
across the four SE-relevant files, that no cluster-robust sandwich
estimator existed: `estimation_engine.py`,
`gamspy_estimation_vectorized.py`, `compute_standard_errors.py`, and
`enh_RURO_estimate_FR.py` all contained only Hessian-based SE
computation, with no cluster argument, no score-matrix computation,
and no meat-matrix assembly. The parse report identified the cluster-
robust SE infrastructure build as the blocker between Gate-A and the
pooled-estimation authorization memo, and recorded that the pooled
estimation requires three conditions: Gate-A passing (met), the GA17
blocker cleared (not yet met), and a separate pooled-estimation
authorization memo (not yet issued).

This addendum addresses the second condition: clearing the GA17
blocker at the smoke-test-callability level.

---

## 3. What GA17 required

GA17 required the implementation of a cluster-robust sandwich
standard-error estimator, clustered at `cluster_id = idorighh`, that
is callable on the pooled parquet, and the passing of the design
audit's validation tests appropriate to the pre-estimation stage.

The design audit specified the sandwich estimator V = H⁻¹ B H⁻¹,
where H is the Hessian of the negative log-likelihood (the bread,
identical to the existing Hessian-only SE bread) and B = Σⱼ sⱼ sⱼᵀ is
the meat matrix, with sⱼ = Σ_{g∈j} s_g the per-cluster score summed
over all choice-set groups belonging to household `idorighh = j`. The
per-group score s_g = (dV_obs_g − dV_exp_g) is the choice-set score
for the positive log-likelihood, extracted from the existing
analytical gradient loop.

The design audit specified six validation tests (T1–T6) and
distinguished those that clear GA17 at the pre-estimation stage from
those that require completed estimation:

- **Smoke-test-stage tests (clear GA17):** T1 (score consistency:
  the per-group scores aggregate to the full gradient), T2 (meat-
  matrix symmetry), and T6 (the dummy-theta smoke test: the sandwich
  is callable at initial values, returning finite SEs). The design
  audit §18 states explicitly that "T6 is the minimum test needed to
  record GA17 as CONFIRMED before pooled estimation begins."

- **Post-estimation-stage tests (do NOT gate GA17 clearance):** T4
  (SE positivity, which requires a non-degenerate theta and the
  correct Hessian), T5 (the robust-versus-Hessian comparison, which
  requires converged theta), and the full-dataset confirmation of T3
  (the 9,657-cluster count, which requires the full-data load that the
  smoke test bounds).

GA17 therefore required: the sandwich infrastructure implemented and
callable, the score sign convention and meat symmetry verified
(T1, T2), and the dummy-theta smoke test passing (T6) — all at the
pre-estimation stage. It did not require the post-estimation
diagnostics, which the design audit explicitly deferred.

---

## 4. Cluster-robust SE implementation status

**IMPLEMENTED. The sandwich estimator infrastructure is complete and
committed.**

The implementation created two files and modified two existing files
(implementation report §2, §3). The new file
`scripts/enhanced/cluster_robust_se.py` provides the sandwich library:
`assemble_meat_matrix`, `compute_cluster_robust_se`, and the T1–T5
check functions. The new file
`scripts/enhanced/run_cluster_robust_se.py` provides the CLI smoke-
test and post-estimation interface (the GA17 clearance entry point).
The modified `estimation_utils.py` adds a `cluster_ids: np.ndarray`
field to `PrecomputedDataSingles` and `PrecomputedDataCouples`,
extracted from the `idorighh` column at the group-start indices. The
modified `estimation_engine.py` adds a `return_scores: bool = False`
parameter to `compute_gradient_singles` and `compute_gradient_couples`
and the `compute_scores_joint` function.

The implementation matches the design audit's specification on every
substantive point. The score extraction reuses the existing analytical
gradient loop with `return_scores=True`, requiring no additional
function evaluations (implementation report §5); the score is the
per-choice-set quantity (dV_obs − dV_exp) for the positive log-
likelihood, with the sign convention flipped relative to the negative-
LL gradient as the design audit required. The meat matrix is assembled
by summing per-cluster scores over `idorighh` and accumulating outer
products (implementation report §6). The bread is the numerical
Hessian of the negative log-likelihood, identical to the existing
Hessian-only SE bread (implementation report §7). The free-parameter
mask restricts the sandwich to the estimated parameters and assigns
zero SE to bounded parameters (implementation report §8). The fixed
parameter `theta_c` (couples Box-Cox exponent, fixed at 0.0) is absent
from the 55-parameter vector and does not enter the computation
(implementation report §9).

The implementation correction (correction report) applied five fixes
that strengthen the implementation: it added the C2 CLI-help check
(absent from the v1 smoke test), corrected the GA17 label from an
unqualified "CONFIRMED" to "smoke-test callability: CONFIRMED" (the
strict scoping this addendum adopts), added the T4/T5 deferral note,
corrected the next-gate wording, and corrected the cluster-key
strictness in both `precompute_data_singles` and
`precompute_data_couples` so that the silent `idhh` fallback is now
loudly documented as invalid for the pooled P3a GA17 context. The
cluster-key strictness correction is a meaningful safeguard: it
prevents the engine from silently clustering at the household-year
level (`idhh`) rather than the cross-year household level (`idorighh`)
on the pooled parquet.

The cluster-robust SE infrastructure is implemented, corrected, and
complete at the infrastructure level.

---

## 5. Whether the implementation is callable

**Yes. The implementation is callable on the pooled parquet at initial
values. All 17 static/smoke checks (C1–C17) pass.**

The static validation report records all seventeen checks passing
(static validation report, C1–C17): the module imports (C1), the CLI
`--help` (C2, added in the correction), the P3a pooled YAML parse
(C3), the 55-free-parameter vector length (C4), the pooled-parquet
schema read (C5), the `cluster_id` column existence (C6), the
`cluster_id == idorighh` bounded check (C7), the documented 9,657-
cluster expectation (C8, on a bounded sample), the score-interface
callability (C9), the score-matrix shape (C10), the cluster-id
alignment to score rows (C11), the sign check (C12/T1), the meat-
matrix symmetry (C13/T2), the sandwich-covariance callability (C14),
the finite robust-SE output (C15, with a dummy Hessian), the no-
estimation confirmation (C16), and the no-welfare confirmation (C17).

Two of these are the substantive correctness checks at the pre-
estimation stage. The sign check (C12/T1) confirms that the per-group
scores sum to the negative of the negative-LL gradient — that is, the
scores aggregate to the gradient of the positive log-likelihood — with
a maximum absolute difference of 5.82×10⁻¹⁰, well within the 10⁻⁶
tolerance. This is the key correctness verification of the score
extraction: it establishes that the per-cluster score contributions
are the correct analytical scores, not an incorrectly signed or
incorrectly assembled quantity. The meat-matrix symmetry check
(C13/T2) confirms B = Bᵀ to within 10⁻¹⁰ on the smoke sample.

The callability is established with two explicit qualifications that
the addendum records honestly (and that §10 and §11 detail). First,
the finite-robust-SE check (C15) uses a *dummy Hessian* H = 0.1·I,
not the true Hessian: it confirms the sandwich formula is callable and
returns finite output, not that the returned SEs are the inference-
valid SEs. The implementation report §7 is explicit that the dummy
Hessian "is not the correct bread for inference — it is used only to
verify the interface at initial_values." Second, the checks are run at
`theta = initial_values` (the starting vector), not at a converged
theta: they verify the interface, not the inference.

The implementation is callable at the smoke-test level: the
interfaces exist, are wired correctly, and return finite output with
the score sign convention and the meat symmetry verified. This is the
callability that the GA17 pre-estimation gate requires.

---

## 6. Whether the implementation uses cluster_id = idorighh

**Yes. The implementation clusters at `cluster_id = idorighh`, with a
safeguard against the silent `idhh` fallback.**

The cluster key is `idorighh`, the original EU-SILC household
identifier that persists across survey waves (implementation report
§6; design audit §7). The `cluster_ids` field added to
`PrecomputedDataSingles` and `PrecomputedDataCouples` is extracted from
the `idorighh` column at the group-start indices, so each choice-set
group carries its household's cross-year cluster key. The static
validation confirms the `cluster_id` column exists (C6) and that
`cluster_id == idorighh` on the bounded sample (C7), consistent with
the Gate-A GA16 confirmation that `cluster_id == idorighh` on row
group 0.

The cluster-key strictness correction (correction report §7) is the
safeguard that makes this robust. The pre-correction code carried a
terse warning and a silent fallback to `idhh` when `idorighh` was
absent; the correction replaced this in both `precompute_data_singles`
and `precompute_data_couples` with an explicit multi-line warning that
names the `idhh` fallback as NOT valid for pooled P3a GA17 clearance,
states the distinction between `idhh` (the household-year key) and
`idorighh` (the cross-year cluster key), and carries a four-line
header comment explaining that the silent fallback must never be
invoked on the P3a pooled parquet. The fallback path is retained only
for legacy single-year datasets where `idhh == idorighh` holds. This
safeguard prevents the consequential error of clustering at the
household-year level on the pooled data — which would treat each
annual appearance of a repeat household as an independent cluster,
defeating the cluster-robust correction.

The implementation uses `cluster_id = idorighh`, and the safeguard
ensures it does not silently degrade to `idhh` on the pooled parquet.

---

## 7. Whether score aggregation is consistent with the likelihood

**Yes. The score aggregation is consistent with the likelihood, with
the sign convention verified analytically (T1).**

The per-group score is s_g = (dV_obs_g − dV_exp_g), the choice-set
score for the positive log-likelihood, extracted from the existing
softmax-weighted gradient loop (implementation report §5; design audit
§8). The aggregation to the cluster level sums all per-group scores
belonging to the same `idorighh` into the cluster score s_j, and the
meat matrix accumulates the outer products B = Σⱼ s_j s_jᵀ
(implementation report §6).

The consistency with the likelihood is verified by the T1 sign check
(static validation C12/T1): the sum of the per-group scores over all
groups equals the negative of the negative-LL gradient, i.e. the
gradient of the positive log-likelihood, with a maximum absolute
difference of 5.82×10⁻¹⁰. This is the load-bearing consistency check:
it establishes that the per-group scores, summed, reconstruct the
full-sample gradient. Because the gradient is the sum of the per-
observation score contributions at the likelihood's stationary
structure, the T1 identity confirms that the score extraction has not
dropped, double-counted, or mis-signed any contribution. The score
object is therefore the correct score of the RURO/MNL likelihood, and
its cluster aggregation is the correct clustered meat.

The sign convention is the specific point the design audit flagged as
error-prone: the gradient functions return ∇(−ℓ), and the sandwich
requires the score of ∇(+ℓ) = −∇(−ℓ). The implementation flips the
sign correctly (implementation report §5), and the T1 check confirms
the flip is correct (the scores sum to −grad of the negative LL, i.e.
+grad of the positive LL). The score aggregation is consistent with
the likelihood.

---

## 8. Whether the implementation handles draw-expanded rows correctly

**Yes. The draw-expanded rows are handled at the choice-set level; the
100 draws are not treated as independent clusters or independent
observations.**

The pooled parquet is draw-expanded: 1,244,500 rows = 12,445
household-years × 100 draws. The implementation handles this correctly
by operating at the choice-set (household-year) level, not the row
level (implementation report §12; design audit §9). The per-choice-set
score s_g = (dV_obs_g − dV_exp_g) already integrates over all 100 draws
via the softmax probability P_group, which weights each draw within the
choice set; it is a single (n_params,) vector per choice set, and there
is no per-draw score. The meat-matrix assembler loops over the choice-
set groups (≈12,445), not over the rows (1,244,500), guaranteed by the
structure of `compute_scores_joint`, which calls the gradient functions
that iterate over `data.n_groups`.

This is the correct treatment, and it avoids two errors. First, the
100 draws within a household-year are not treated as independent
observations: they are summed inside the gradient loop before the
score is recorded, so the choice-set score correctly reflects the
single household-year's contribution, not 100 spurious independent
contributions. Second, the draws are not treated as independent
clusters: the clustering is at `idorighh` (the household), which
aggregates all of a household's choice-set scores — across draws,
across household types, and across survey years — into one cluster
score before the outer product. Treating the draws as independent
clusters or independent observations would massively understate the
SEs by inflating the effective sample size from 9,657 clusters to
1,244,500 pseudo-observations; the implementation does not do this.

The draw-expanded rows are handled correctly: the score is defined at
the choice-set level, the meat loops over groups, and the clustering
is at the household. The 100 draws are neither independent observations
nor independent clusters.

---

## 9. Whether singles/couples income handling is safe

**Yes. The singles and couples income paths are kept separate: singles
use `ils_dispy_real`; couples use `ils_dispy_male` / `ils_dispy_female`.
The two paths are never mixed.**

The implementation preserves the GA15 income-handling structure
(implementation report §11; design audit §14). The singles score
extractor reads `PrecomputedDataSingles`, whose `consumption` field
derives from `ils_dispy_real` (the CPI-deflated real income column,
non-null for the 500,700 singles rows, null for couples). The couples
score extractor reads `PrecomputedDataCouples`, whose `consumption`
field derives from the household sum `(ils_dispy_male +
ils_dispy_female)` via the normalisation, independent of
`ils_dispy_real`. The `compute_scores_joint` function calls
`compute_gradient_singles` for singles groups and
`compute_gradient_couples` for couples groups independently, and stacks
the resulting score matrices via `np.vstack` after they are computed
from their respective precomputed objects. The two income paths are
never mixed.

The safety of this handling is the resolution of the GA15 structural
note that the Gate-A parse report flagged. The Gate-A report (§4 GA15,
§8 carry-forward note) recorded that `ils_dispy_real` is singles-only
and that couples income enters via the gender-specific columns, and
required that any downstream step reading income data acknowledge this
explicitly so that no step assumes `ils_dispy_real` covers couples
rows. The cluster-robust SE implementation honours this: the singles
path reads `ils_dispy_real`, the couples path reads the gender-specific
columns, and the score extraction does not read `ils_dispy_real` for
couples rows (which are null). The income handling is safe in the
specific sense the GA15 note required: the singles-only `ils_dispy_real`
column is not assumed to cover couples, and the couples consumption is
correctly sourced from the gender-specific columns.

The singles/couples income handling is safe: the two paths use
distinct source columns, are computed independently, and are never
confused.

---

## 10. Validation evidence

The validation evidence comprises the seventeen static/smoke checks
(C1–C17) and the design audit's T1, T2, and T6 tests at the pre-
estimation stage, with T3 (full count), T4, and T5 explicitly deferred.

Table 1 summarises the pre-estimation validation evidence.

| Test | Status | Evidence |
|---|---|---|
| C1–C17 (17 static/smoke checks) | ALL PASS | static validation report |
| T1 — score sign consistency (scores sum to gradient) | PASS | max abs diff 5.82×10⁻¹⁰ (tol 10⁻⁶) |
| T2 — meat-matrix symmetry | PASS | max\|B − Bᵀ\| < 10⁻¹⁰ on smoke sample (2,000 clusters) |
| T6 — dummy-theta smoke test (sandwich callable at initial values) | PASS | finite SEs returned with dummy Hessian H = 0.1·I |
| Score interface callable | PASS | scores shape (n_groups, 55) confirmed |
| Sandwich interface callable | PASS | finite output |
| Cluster-id alignment | PASS | len(cluster_ids) == n_score_rows |
| No estimation run | PASS | no solver invoked |
| No welfare run | PASS | welfare not computed |

The validation evidence establishes the smoke-test-stage clearance:
the infrastructure is callable (T6), the score extraction is correct
(T1, the load-bearing analytical check), and the meat matrix is well-
formed (T2). The bounded read (200,000 rows per the implementation
report §16; a 50,000-row sample with 500 unique clusters per the
static validation C8) confirms the interface operates on the pooled
parquet without a full-data materialisation, consistent with the
Gate-A bounded-read rule.

The validation evidence does not include T3 (full-dataset 9,657-
cluster count), T4 (SE positivity at a non-degenerate theta with the
correct Hessian), or T5 (robust-versus-Hessian comparison at converged
theta). These are recorded as deferred to post-estimation (§11),
consistent with the design audit's classification.

The validation evidence is sufficient for the smoke-test-callability
clearance of GA17 and is explicitly insufficient for the post-
estimation robust-SE validation, which the addendum does not claim.

---

## 11. Remaining limitations

Three limitations bound the GA17 clearance. Each is a deferral to the
post-estimation stage, not a defect in the implementation, and each is
recorded so that the clearance is not over-read.

(L1) **The smoke test uses a dummy Hessian, not the true bread.** The
finite-robust-SE check (C15) uses H = 0.1·I, which confirms the
sandwich formula is callable and returns finite output but is not the
inference-valid bread. The true Hessian — the numerical second
derivative of the negative log-likelihood at the converged theta — is
the correct bread, and the inference-valid cluster-robust SEs can only
be computed after estimation converges. The GA17 clearance is
therefore a callability clearance, not an SE-validity clearance: it
confirms the machinery produces finite SEs from a valid sandwich
formula, not that the produced SEs are the numbers that will be
reported.

(L2) **The full-dataset cluster count (T3) is not confirmed.** The
smoke test bounds the read to a sample (200,000 rows / 2,000 clusters
in the implementation report; 50,000 rows / 500 clusters in the static
validation C8 — the two documents record different bounded-sample
sizes, a minor documentation inconsistency that does not affect the
clearance). The full-dataset confirmation that the meat matrix
aggregates over exactly 9,657 unique `idorighh` clusters (T3) requires
the full-data load, which `compute_scores_joint` performs at
estimation time. The 9,657 figure is documented as expected (from the
Gate-A GA16 and the construction validation V6), but the exact count
on the full dataset is confirmed post-estimation, not at the smoke-
test stage.

(L3) **The post-estimation diagnostics (T4, T5) are deferred.** The
SE-positivity check (T4: all free-parameter robust SEs strictly
positive at a non-degenerate theta) and the robust-versus-Hessian
comparison (T5: robust SEs generally ≥ Hessian SEs, flagging any
parameter where robust < Hessian) require the converged parameter
vector and the true Hessian. They are post-estimation checks and are
not part of the GA17 smoke-test clearance. They must be run as part of
the post-estimation diagnostics (the design memo's D6 cluster-robust-
versus-Hessian SE comparison) when the pooled estimation has converged.

These three limitations are the precise content of the smoke-test-
versus-post-estimation distinction. The GA17 clearance confirms the
infrastructure is implemented, callable, and correct in its score
extraction and meat assembly (T1, T2, T6); it defers the inference-
validity confirmation (T3 full count, T4, T5) to the post-estimation
stage. The minor documentation inconsistency in the bounded-sample
size (L2) is recorded for cleanup but does not affect the clearance.

---

## 12. Updated GA17 status

**GA17: smoke-test callability CONFIRMED.**

GA17 is cleared at the smoke-test-callability level. The cluster-
robust SE infrastructure is implemented (§4), callable on the pooled
parquet at initial values (§5), correctly clustered at `idorighh`
(§6), with score aggregation consistent with the likelihood (§7),
draw-expanded rows handled at the choice-set level (§8), and
singles/couples income handling kept separate (§9). The smoke-test-
stage validation tests (T1 score consistency, T2 meat symmetry, T6
dummy-theta callability) and all seventeen static/smoke checks
(C1–C17) pass (§10).

The GA17 status is stated with the strict qualification adopted in the
implementation correction: **smoke-test callability: CONFIRMED**, not
an unqualified "CONFIRMED." The qualification is load-bearing. GA17 is
confirmed at the level the pre-estimation gate requires — the
infrastructure exists and is callable, the score extraction is correct,
and the sandwich is well-formed — and is explicitly not confirmed at
the post-estimation inference-validity level (the full-dataset cluster
count T3, the SE positivity T4, and the robust-versus-Hessian
comparison T5), which remains deferred to post-estimation (§11). The
unqualified "CONFIRMED" that the implementation v1 first recorded was
corrected precisely because it overstated the clearance scope; this
addendum adopts the qualified statement.

GA17 smoke-test callability is CONFIRMED. The post-estimation robust-
SE diagnostics (T3 full count, T4, T5) remain post-estimation checks
and are not cleared by this addendum.

---

## 13. Updated Gate-A status

**Gate-A: PASS (for pre-estimation authorization purposes).**

With GA1–GA16 passed (Gate-A parse report) and GA17 cleared at the
smoke-test-callability level (§12), the Gate-A status is updated from
PASS WITH BLOCKER to **PASS for pre-estimation authorization
purposes.** The blocker that produced the PASS WITH BLOCKER verdict —
the absent cluster-robust SE infrastructure — is removed: the
infrastructure now exists and is callable.

The qualification "for pre-estimation authorization purposes" is
precise and is retained deliberately. The Gate-A PASS licenses the
next pre-estimation step — the drafting of the pooled-estimation
authorization memo (§14) — by confirming that the pooled YAML is
structurally valid, the pooled data input is structurally valid, and
the cluster-robust SE infrastructure is implemented and callable. It
does not certify that the cluster-robust SEs are inference-valid; that
certification belongs to the post-estimation stage, when the
infrastructure is run on the converged theta with the true Hessian and
the post-estimation diagnostics (T3 full count, T4, T5, and the design
memo's D6 comparison) are evaluated.

The Gate-A PASS therefore means: the static validation gate is fully
cleared, and the pipeline is unblocked at the YAML-and-data-and-
infrastructure level. It does not mean pooled estimation is authorised
(§14) or that the cluster-robust inference is validated (§11). Under
the corrected Gate-A verdict semantics (design memo correction), this
is the PASS outcome: GA1–GA16 pass and GA17 is cleared, so Gate-A
passes without a blocker for pre-estimation authorization purposes.

---

## 14. Whether pooled estimation authorization may now be drafted

**Yes. The pooled-estimation authorization memo may now be drafted.
The Gate-A PASS (§13) clears the pre-estimation gate that the
authorization memo requires. The authorization memo is a separate
document; this addendum does not authorise pooled estimation
execution.**

The Gate-A parse report established that pooled estimation execution
requires three conditions: Gate-A passing, the GA17 cluster-robust SE
infrastructure blocker cleared, and a separate pooled-estimation
authorization memo. The first two conditions are now met: Gate-A is
PASS for pre-estimation authorization purposes (§13), and the GA17
blocker is cleared at the smoke-test-callability level (§12). The third
condition — the authorization memo — may now be drafted.

The authorization memo, when drafted, must carry forward the
limitations this addendum records (§11) and the GA15 income carry-
forward (§9). Specifically, it must (a) require the post-estimation
robust-SE diagnostics (T3 full-dataset cluster count, T4 SE positivity,
T5 robust-versus-Hessian comparison, and the design memo's D6
comparison) to be run on the converged theta with the true Hessian,
and must not treat the smoke-test clearance as a substitute for these;
(b) confirm that the estimation engine reads `ils_dispy_real` for
singles and `ils_dispy_male` / `ils_dispy_female` for couples,
matching the M1-clean engine behaviour; (c) specify the three-start
protocol (warm from M1-clean, spec defaults, perturbed) and the SA2
post-estimation diagnostics; and (d) confirm the cluster-key strictness
safeguard (no silent `idhh` fallback) is active on the pooled run.

The authorization memo is the gate between this addendum and pooled
estimation execution. This addendum does not authorise the execution;
it clears the pre-estimation gate so that the authorization memo may
be drafted. The drafting of the authorization memo is the immediate
next task.

---

## 15. What remains blocked

The addendum clears the GA17 pre-estimation gate and licenses the
drafting of the pooled-estimation authorization memo (§14). It does
not authorise the following; each remains gated.

(B1) **Pooled estimation execution.** No pooled estimation is
authorised. Pooled estimation execution requires the separate pooled-
estimation authorization memo (§14), which has not yet been drafted or
issued. This addendum clears the pre-estimation gate; it does not
authorise the execution.

(B2) **The post-estimation robust-SE diagnostics as a fait accompli.**
The full-dataset cluster-count confirmation (T3), the SE-positivity
check (T4), and the robust-versus-Hessian comparison (T5) are not
cleared by this addendum. They are post-estimation checks requiring the
converged theta and the true Hessian, and they must be run as part of
the post-estimation diagnostics. The GA17 smoke-test clearance does not
substitute for them.

(B3) **Welfare implementation or welfare computation.** No welfare work
is authorised. Welfare computation requires an accepted SA2 verdict on
a pooled specification and a separate welfare-computation
authorization.

(B4) **Canonical promotion.** No canonical promotion of the pooled
YAML, the pooled dataset, the cluster-robust SE infrastructure, or any
pooled output is authorised.

(B5) **M1-clean displacement.** The pooled specification and the
cluster-robust SE infrastructure do not displace M1-clean. M1-clean
2016 remains the active JMP baseline, displaced only by a future SA2
verdict on an estimated pooled specification.

The addendum clears GA17 at the smoke-test-callability level and
updates Gate-A to PASS for pre-estimation authorization purposes;
everything downstream of the pooled-estimation authorization memo
remains gated.

---

**Required final statements**

- **GA17 smoke-test callability is CONFIRMED**, and is strictly
  distinguished from the full post-estimation robust-SE diagnostics:
  the infrastructure is implemented and callable (C1–C17 pass, T1 and
  T2 pass, T6 dummy-theta smoke test passes), clustered at
  `cluster_id = idorighh`, with draw-expanded rows handled at the
  choice-set level (not as independent clusters) and singles/couples
  income kept separate (singles `ils_dispy_real`; couples
  `ils_dispy_male` / `ils_dispy_female`).

- **T4 and T5 (and the full-dataset T3 cluster count) remain post-
  estimation checks**, requiring the converged theta and the true
  Hessian. They are deferred and are not cleared by this addendum.

- **Gate-A is updated from PASS WITH BLOCKER to PASS for pre-estimation
  authorization purposes.** The pooled-estimation authorization memo
  may now be drafted.

- **Pooled estimation is NOT authorized.** Pooled estimation execution
  requires a separate pooled-estimation authorization memo, which has
  not yet been issued.

- **Welfare computation is NOT authorized.** Separately gated.

- **M1-clean 2016 remains the active JMP baseline.** Displaced only by
  a future SA2 verdict explicitly promoting a final pooled
  specification.
