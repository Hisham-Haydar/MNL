# JMP Pooled P3a — Post-Estimation Diagnostics Authorization v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-22*

Specification class: narrow post-estimation diagnostics authorization
memo. This memo authorises the four computable adjudications (S4, S5, S6,
S8) that the corrected-region post-estimation review left open, using
only saved corrected-region artifacts and deterministic post-estimation
recomputation at the saved converged theta. It authorises **no solver
run, no re-estimation, no welfare, no SA2 verdict, no canonical
promotion, and no displacement of M1-clean 2016.** S10/S11 (simulation
fit) are a later, separate gate.

Reference documents:
- `docs/JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md`
  (the review that left S4/S5/S6/S8 open and is NOT SA2-ready)
- `Results/JMP_pooled_P3a_corrected_region_estimation_report_v1.md` (the
  corrected estimation report)
- `Results/JMP_pooled_P3a_corrected_orchestrator_summary.json` and the
  three corrected SE JSONs (`corrected_start1/2/3_cluster_robust_se.json`)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the M1-clean baseline: the
  verdict-selected run, the region joint Wald benchmark, and the three
  negative-variance entries)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to authorise a narrow set of post-estimation
diagnostics that resolve the four SA2 criteria the corrected-region
review left open and that are computable **without re-estimation**: the
region joint robust Wald test (S4), the GSUR-region Hessian eigenvalue
check (S5), the preference-block comparison to M1-clean with the
singles-consumption diagnosis (S6), and the negative-variance enumeration
versus M1-clean (S8). Three of these (S4, S6, S8) require only arithmetic
on artifacts already on disk; one (S5) may require a deterministic
recomputation of the true Hessian at the saved converged theta if the
full Hessian matrix was not persisted — a post-estimation diagnostic, not
a solve and not a re-estimation.

The review established the prerequisite: the corrected run is identified
(region block stable across starts, finite robust SEs, interior CONOPT
marginals), five SA2 criteria pass (S1, S2, S3, S7, S9), and the only
obstacles to an SA2 verdict are the four open criteria here plus the
simulation-dependent S10/S11. This memo closes the computable four. It
does not issue the SA2 verdict, which remains a later gate even if all
four clear, because S10/S11 still require a separately-authorised
simulation.

---

## 2. Current SA2-readiness status

**NOT SA2-ready.** Per the corrected-region review:

- **PASS (5):** S1 (objective/parameter stability across starts), S2
  (GSUR robust t = −6.28), S3 (GSUR within 50% of M1-clean, 90.3%), S7
  (`beta_ll` t = 7.10), S9 (Gate-A / GA1–GA17, spec unchanged, corrected
  data validated).
- **Open and computable now (4):** S4 (region joint Wald — not computed),
  S5 (GSUR-region Hessian eigenvalues — not extracted), S6 (preference-
  block Δ vs M1-clean, singles-consumption — omitted by the report), S8
  (negative-variance enumeration — count rose 3 → 5, not enumerated).
- **Open, simulation-dependent (2):** S10 (participation fit), S11
  (mean-hours fit) — require a post-estimation simulation, deferred.

The region block is identified but not shown jointly significant
(individual t-ratios 0.50–1.16; joint Wald uncomputed), and the singles-
consumption block diverges ~5× from M1-clean with a sign flip in
`theta_c_singles`. These are the substantive questions the four
diagnostics resolve.

---

## 3. Why diagnostics are authorized now

The diagnostics are authorised now, ahead of any further estimation,
because the binding open criteria require no new estimation — they are
deterministic functions of artifacts that already exist. S4 is a
quadratic form in the saved robust VCV and the seven region coefficients.
S6 and S8 are comparisons of the saved converged theta and the saved
Hessian-based variance object against the M1-clean baseline. S5 needs the
GSUR-region sub-block of the true Hessian, which is either already saved
or deterministically recomputable at the fixed saved theta. Running these
first is the cheapest, lowest-risk way to move S4/S5/S6/S8 off their open
status, and it strictly precedes any decision about a new specification,
a constraint, or a fallback — none of which can be justified before these
results are in hand. The simulation-dependent S10/S11 are deliberately
excluded here so this step stays narrow, deterministic, and solver-free.

---

## 4. S4 diagnostic authorization

**Authorize: the region joint robust Wald test.**

Compute the joint robust Wald statistic and p-value for the null
`beta_E_drgn2 = beta_E_drgn3 = … = beta_E_drgn8 = 0` (seven restrictions),
using the saved **corrected-region** cluster-robust VCV and the seven
region coefficients from the saved converged theta.

- **Coefficients.** `beta_E_drgn2`–`beta_E_drgn8` are at positions 28–34
  (1-indexed; 0-indexed 27–33) in the 55-parameter vector. From the
  corrected Start 1 converged theta these are 0.3965, 0.3500, 0.6416,
  0.4310, 0.3577, 0.3671, 0.1675 (confirm against the saved theta; do not
  hard-code).
- **VCV sub-block.** Extract the 7×7 region sub-block `V_R` from the saved
  robust VCV `.npy` (the full 55×55 sandwich VCV, with the `free_mask`
  applied; the region rows/columns are all free).
- **Statistic.** `W = b_R' V_R⁻¹ b_R`, where `b_R` is the 7-vector of
  region coefficients; `W ~ χ²(7)` under the null; report `W`, the
  degrees of freedom (7), and the p-value.
- **Cross-start.** Compute `W` from all three corrected VCVs
  (start1/start2/start3) and report all three; they should agree closely
  (the converged thetas agree to L∞ < 10⁻⁸). Report the spread as a
  numerical-stability check.
- **Conditioning guard.** Before inverting `V_R`, report its condition
  number and smallest eigenvalue; if `V_R` is near-singular (so that
  `V_R⁻¹` is unreliable), report the Wald via a pseudo-inverse with the
  effective rank and flag the result as conditioning-limited rather than
  asserting a clean p-value.

**Benchmark (for interpretation, not for the pass rule).** M1-clean's
region block had a joint Wald `W = 28.18` on 7 d.f., `p = 0.0002`
(`RURO_occ_M1_clean_verdict_v1.md` Q1). The corrected pooled `W` is
interpreted against the S4 threshold (`p < 0.01`); the M1-clean figure is
context, since the pooled couples-only region channel and the
three-year pooled sample differ from M1-clean's 2016 cross-section.

**Adjudication.** S4 PASSES if the joint robust Wald `p < 0.01` with a
well-conditioned `V_R`; FAILS if `p ≥ 0.01` with a well-conditioned
`V_R`; remains REQUIRES-FURTHER-DIAGNOSIS if `V_R` is too ill-conditioned
to yield a reliable statistic. Individual region t-ratios are not the S4
test and do not override the joint result.

---

## 5. S5 diagnostic authorization

**Authorize: the GSUR-region Hessian/eigenvalue check, with deterministic
Hessian recomputation permitted only at the saved converged theta.**

Examine the sub-block of the true Hessian (and/or the robust VCV)
corresponding to `beta_E_gsur` (position 27; 0-indexed 26) together with
the seven region dummies `beta_E_drgn2`–`beta_E_drgn8` (positions 28–34) —
an 8×8 GSUR-region sub-block.

- **Preferred source.** If the full true Hessian (the 54×54 numerical
  Hessian used as the sandwich bread) is saved, extract the 8×8
  GSUR-region sub-block from it directly.
- **Permitted recomputation.** If the full Hessian matrix was not
  persisted (the SE JSONs record the condition number 3.316 × 10⁹ and the
  SE vectors but may not store the full matrix), authorize a
  **deterministic recomputation of the true numerical Hessian at the
  saved corrected-region converged theta**, using the saved estimation
  result, the P3a YAML, the corrected split-stem data, and the existing
  `compute_gradient_joint` central-difference Hessian code — the same
  computation the SE step already performed. This is a post-estimation
  diagnostic at a fixed parameter vector; it is NOT a solve and NOT a
  re-estimation. The theta is held fixed at the saved converged value;
  no optimisation step is taken.
- **Checks.** Report (a) the eigenvalues of the 8×8 GSUR-region Hessian
  sub-block and their signs; (b) the eigenvalues / conditioning of the
  corresponding 8×8 robust-VCV sub-block; (c) whether the region VCV
  diagonal is strictly positive (already implied by T4, re-confirm here);
  and (d) the smallest eigenvalue and condition number of the sub-block.
- **Cross-start.** Confirm consistency across the three saved VCVs (and,
  if recomputed, note the Hessian condition number agrees with the
  ~3.316 × 10⁹ recorded in the SE JSONs).

**Adjudication.** S5 PASSES if the GSUR-region Hessian sub-block has no
negative eigenvalues (the criterion as written) and the VCV sub-block is
positive-definite / well-posed; FAILS if a negative eigenvalue is present
in the GSUR-region Hessian sub-block; REQUIRES-FURTHER-DIAGNOSIS if the
sub-block is so ill-conditioned that the eigenvalue signs are
numerically ambiguous. Note for interpretation: the full Hessian is
ill-conditioned (κ ≈ 3.3 × 10⁹), so report eigenvalues with an explicit
numerical-tolerance statement rather than asserting exact zeros.

---

## 6. S6 diagnostic authorization

**Authorize: the preference-block comparison to M1-clean, with the
singles-consumption diagnosis.**

Compute the per-parameter difference between the corrected pooled
converged theta and the M1-clean baseline, for the shared preference
block, with special focus on `beta_c_sm`, `beta_c_sf`, `theta_c_singles`,
`beta_ll`, and the leisure parameters (`theta_l_sm`, `theta_l_sf`,
`theta_l_m`, `theta_l_f`, and the age/kids leisure terms).

- **M1-clean baseline artifact.** Use the **verdict-selected** M1-clean
  run: `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/
  estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/`
  (`RURO_occ_M1_clean_verdict_v1.md` §"Selected estimation run"; LL =
  −6487.5522). Document the artifact path used. Note the documented
  wrinkle: the pooled run warm-started from a *different* M1-clean run
  (`run_2026-05-18_12-38-37`, LL −6487.55); both are the same converged
  optimum (bit-identical vector across M1-clean starts per the verdict),
  but the comparison baseline of record is the verdict-selected
  `11-33-46` run. If the diagnostics can justify a different M1-clean
  artifact (e.g., the warm-start run is the only one with a saved theta on
  disk and is confirmed bit-identical), that substitution is permitted
  **only if** the bit-identity to the verdict-selected run is verified and
  documented.
- **Comparison.** For each shared preference parameter report: M1-clean
  value, corrected pooled value, absolute Δ, and relative Δ. Apply the
  literal S6 threshold (max |Δ| < 10% vs M1-clean) and report which
  parameters breach it.
- **Singles-consumption diagnosis.** For `beta_c_sm`, `beta_c_sf`,
  `theta_c_singles` (the block that the review found at ~5× / sign flip),
  go beyond the Δ: (a) report the corrected-run robust and Hessian SEs for
  these three (from the saved SE vectors); (b) cross-reference S8 (these
  three are M1-clean's known negative-variance entries); (c) where
  feasible without re-estimation, profile the joint log-likelihood in
  `theta_c_singles` at the saved theta (vary only that coordinate around
  its converged value, holding others fixed, using the existing
  likelihood code — a deterministic evaluation, not an optimisation) to
  characterise whether the divergence reflects genuine multi-year
  re-identification (a well-defined optimum away from M1-clean) or
  weak-identification drift (a flat/near-flat profile). State which the
  evidence supports, or that it is inconclusive.

**Benchmark.** M1-clean's singles-consumption block is the structurally
inherited negative-variance limitation (V1): `beta_c_sm`, `beta_c_sf`,
`theta_c_singles`, with M1-clean point estimates that shifted < 0.10 from
M0c_b2_GSURv2. The corrected pooled values (≈2.73, ≈2.35, ≈+0.039) versus
M1-clean (≈0.554, ≈0.506, ≈−1.049) are the departure to diagnose.

**Adjudication.** S6 PASSES only if the preference block satisfies the
max |Δ| < 10% threshold; on the current evidence it is expected to FAIL
on the singles-consumption block, in which case the diagnosis must state
whether the failure is genuine re-identification (which may warrant
re-framing rather than rejection) or weak-identification drift (which
would point toward a constrained specification). The leisure block and
`beta_ll` are expected to pass and should be confirmed.

---

## 7. S8 diagnostic authorization

**Authorize: the negative-variance enumeration and comparison to
M1-clean.**

Enumerate the negative-variance parameters in the corrected pooled run
and compare them to M1-clean's known three.

- **Source.** The negative entries come from the **Hessian-based**
  variance object (`diag(H⁻¹)` on the 54×54 true Hessian), i.e. the
  in-estimation SE computation that warned "5 free parameters have
  negative variance." Enumerate the five by name. (Note: the cluster-
  robust sandwich SEs are all positive — T4 PASS — so the negative
  entries are a property of the Hessian-based variance, not the robust
  SE; report both for each named parameter.) If the Hessian-based VCV is
  not directly saved, use the saved Hessian (or the §5 recomputed Hessian
  at the saved theta) to recompute `diag(H⁻¹)` deterministically.
- **M1-clean comparison.** M1-clean's three negative-variance entries are
  `beta_c_sm`, `beta_c_sf`, and `theta_c_singles`
  (`RURO_occ_M1_clean_verdict_v1.md` V1). Report whether the corrected
  pooled five are exactly these three plus two others; name the two
  others; and locate them relative to the singles-consumption block and
  the region block.
- **Interpretation.** State whether the two additional negative-variance
  entries are (a) adjacent to the singles-consumption block (consistent
  with the S6 finding), (b) in the region block (which would qualify the
  S4/S5 identification reading), or (c) elsewhere. Connect the result to
  S6 and S5.

**Adjudication.** S8 as written is "no new negative-diagonal Hessian
entries beyond M1-clean's 3." With five present, S8 PASSES only if the
diagnosis shows the additional entries are benign and explained (e.g.,
the bound-active `beta_l0_m` neighbourhood or a known weak block) and do
not signal new structural non-identification; otherwise S8 FAILS or
remains a documented qualification. The enumeration is required before
any pass can be asserted.

---

## 8. Required input artifacts

The diagnostics use only the following, all corrected-region or M1-clean
baseline artifacts. No pre-repair pooled artifact is used.

**Corrected-region cluster-robust VCV files (required, explicitly):**
- `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se_vcv.npy`

**Corrected-region SE JSONs (converged theta, SE vectors, free_mask,
Hessian condition number, bread source):**
- `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se.json`

**Corrected-region estimation result JSONs (per start, for theta and, if
present, the saved Hessian):**
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-22_00-18-36/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-22_00-53-54/estimation_results.json`
  (paths from `JMP_pooled_P3a_corrected_orchestrator_summary.json`)

**Specification and data (only if §5 Hessian recomputation is needed):**
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
- the corrected split stem
  `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`
  (`__singles.parquet`, `__couples.parquet`, `__mnlmeta.json`)
- the existing `compute_gradient_joint` central-difference Hessian code

**M1-clean baseline (for S6, S8 comparison):**
- `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json`
  (the verdict-selected M1-clean run)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the region joint-Wald benchmark
  and the three negative-variance entries)

The three corrected VCV `.npy` files are explicitly required for S4 and
S5. If only pre-repair VCVs are present, the diagnostics halt (§11).

---

## 9. What is authorized

The following are authorized by this memo, and only these.

- **(A1)** S4 — the region joint robust Wald test from the corrected VCVs
  and the seven region coefficients (§4).
- **(A2)** S5 — the GSUR-region Hessian/VCV eigenvalue check, including
  deterministic recomputation of the true Hessian at the saved converged
  theta if the full matrix was not saved (§5).
- **(A3)** S6 — the preference-block comparison to the verdict-selected
  M1-clean run, with the singles-consumption diagnosis including, where
  feasible, a deterministic LL profile in `theta_c_singles` at the saved
  theta (§6).
- **(A4)** S8 — the negative-variance enumeration and comparison to
  M1-clean's three (§7).
- **(A5)** Writing the diagnostics report (§12) and any small computed
  artifacts (e.g., the Wald statistics, the eigenvalue lists, the Δ
  table) to versioned/documented paths.

All computations are saved-artifact arithmetic or deterministic
evaluations at the fixed saved converged theta. No optimisation step is
taken at any point.

---

## 10. What is not authorized

The following are NOT authorized. Each remains gated.

- **(N1)** Running the solver / any optimisation step. The Hessian
  recomputation (§5) and the LL profile (§6) are evaluations at a fixed
  theta, not solves.
- **(N2)** Re-estimation of any specification.
- **(N3)** Welfare computation. Separately gated behind an accepted SA2
  verdict.
- **(N4)** Issuing the SA2 verdict. Even if S4/S5/S6/S8 all clear, S10/S11
  remain (§2), so SA2 is not reachable from this step alone.
- **(N5)** Canonical promotion of any pooled output.
- **(N6)** Displacing M1-clean 2016 as the active JMP baseline.
- **(N7)** Specification modification (the pooled YAML is read-only here).
- **(N8)** S10/S11 simulation. A later, separately-authorised gate.
- **(N9)** Use of any pre-repair pooled artifact (the pre-repair VCVs, the
  pre-repair report v2 estimates, the archived defective split). Only
  corrected-region artifacts are used.

---

## 11. Halt conditions

The diagnostics halt under the following conditions; each preserves the
outputs produced up to the halt and requires diagnosis before proceeding.

- **(H1) Only pre-repair VCVs found.** If the three corrected VCV `.npy`
  files (§8) are absent and only pre-repair VCVs are present, halt: the
  diagnostics must run on corrected-region artifacts, never pre-repair
  ones.
- **(H2) Corrected theta cannot be loaded.** If the corrected-region
  converged theta cannot be loaded from the SE JSONs or the estimation
  result JSONs, halt: S4/S5/S6/S8 all depend on it.
- **(H3) Hessian recomputation at the wrong point.** If any Hessian
  recomputation is attempted at anything other than the saved converged
  corrected-region theta — any perturbed, re-optimised, or
  alternative-start theta — halt. The §5 recomputation is permitted ONLY
  at the fixed saved converged theta.
- **(H4) VCV sub-block non-invertible without disclosure.** If the 7×7
  region VCV sub-block (S4) or the 8×8 GSUR-region sub-block (S5) is
  near-singular and a plain inverse is used without reporting the
  conditioning, halt and switch to the disclosed pseudo-inverse / rank
  treatment (§4, §5).
- **(H5) M1-clean baseline mismatch.** If the M1-clean comparison artifact
  is not the verdict-selected run and its bit-identity to the
  verdict-selected run cannot be verified, halt rather than comparing
  against an unverified baseline (§6).
- **(H6) Out-of-scope action.** If the diagnostics would run the solver,
  re-estimate, compute welfare, issue SA2, promote canonically, displace
  M1-clean, modify the spec, or run the S10/S11 simulation, halt (§10).

---

## 12. Required diagnostics report

The diagnostics must be recorded in a report saved as
`Results/JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md`. The
report must include:

- a one-line adjudication per criterion (S4, S5, S6, S8): PASS / FAIL /
  REQUIRES-FURTHER-DIAGNOSIS, with the deciding number;
- **S4:** the joint robust Wald `W`, d.f. (7), and p-value from each of
  the three corrected VCVs; the `V_R` condition number and smallest
  eigenvalue; the seven region coefficients used; the M1-clean benchmark
  (W = 28.18, p = 0.0002) for context; and the explicit statement that
  individual t-ratios do not override the joint test;
- **S5:** the eigenvalues (with signs and a numerical tolerance
  statement) of the 8×8 GSUR-region Hessian sub-block and the 8×8 robust
  VCV sub-block; whether the Hessian was read from a saved matrix or
  deterministically recomputed at the saved theta (stated explicitly,
  with confirmation that no optimisation step was taken and that the
  recomputed Hessian condition number agrees with ~3.316 × 10⁹);
- **S6:** the per-parameter M1-clean-vs-pooled Δ table for the preference
  block (absolute and relative), the parameters breaching the 10%
  threshold, the M1-clean baseline artifact path used (and any documented
  substitution with bit-identity verification), and the singles-
  consumption diagnosis — the three parameters' robust and Hessian SEs,
  the `theta_c_singles` LL-profile result, and the verdict on
  re-identification vs weak-identification drift (or inconclusive);
- **S8:** the enumeration of the five negative-variance parameters by
  name, with each parameter's Hessian-based variance sign and its robust
  SE; the identification of the two beyond M1-clean's three
  (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`); and their location
  relative to the singles-consumption and region blocks, connected to S6
  and S5;
- the input artifacts used (the three corrected VCV `.npy`, the SE JSONs,
  the estimation result JSONs, the M1-clean baseline), with paths;
- any halt (§11) and its diagnosis;
- a "what was not executed" section confirming: no solver, no
  re-estimation, no welfare, no SA2, no canonical promotion, no spec
  modification, no S10/S11 simulation, no pre-repair artifact used;
- the required final statements (below).

**Required final statements (to appear in the diagnostics report):**
- S4, S5, S6, S8 are adjudicated (PASS / FAIL / REQUIRES-FURTHER-
  DIAGNOSIS) from corrected-region artifacts and deterministic
  recomputation at the saved converged theta only.
- No solver was run; no re-estimation was performed; no Hessian was
  computed at any point other than the saved converged corrected-region
  theta.
- No welfare was computed; no SA2 verdict was issued; no output was
  promoted to canonical status.
- S10/S11 simulation remains a later separate gate.
- M1-clean 2016 remains the active JMP baseline.

---

## 13. Exact Claude Code task

Tool path: **Claude Code** (local artifact arithmetic and deterministic
post-estimation diagnostics). Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present before starting: the three corrected VCV `.npy`
files; the three corrected SE JSONs; the three corrected estimation
result JSONs (paths in the orchestrator summary); the verdict-selected
M1-clean estimation result JSON and the M1-clean verdict; and (only if the
Hessian must be recomputed) the P3a YAML, the corrected split stem, and
`compute_gradient_joint`.

Prompt to use:

> Run the narrow post-estimation diagnostics per
> `docs/JMP_pooled_P3a_post_estimation_diagnostics_authorization_v1.md`.
> Use `.venv\Scripts\python.exe`. Do NOT run the solver. Do NOT
> re-estimate. Do NOT compute welfare. Do NOT issue SA2. Do NOT promote
> any output to canonical status. Do NOT modify the pooled YAML. Do NOT
> replace M1-clean 2016. Do NOT run the S10/S11 simulation. Use ONLY
> corrected-region artifacts — never pre-repair pooled artifacts.
>
> S4 — region joint robust Wald. Load the three corrected VCVs
> (`Results/JMP_pooled_P3a_corrected_start{1,2,3}_cluster_robust_se_vcv.npy`).
> Extract the 7×7 region sub-block (`beta_E_drgn2`–`beta_E_drgn8`,
> positions 28–34 / 0-indexed 27–33). Take the seven region coefficients
> from the saved converged theta (do not hard-code). Compute
> W = b_R' V_R⁻¹ b_R ~ χ²(7), the p-value, from all three VCVs; report
> V_R condition number and smallest eigenvalue; if near-singular, use a
> pseudo-inverse and flag conditioning-limited. Compare to the M1-clean
> benchmark W = 28.18, p = 0.0002 (context only). Adjudicate S4 (PASS if
> p < 0.01 well-conditioned).
>
> S5 — GSUR-region Hessian/eigenvalue check. Form the 8×8 sub-block for
> `beta_E_gsur` (position 27) + the seven region dummies. Prefer the saved
> true Hessian; if the full Hessian matrix is not saved, deterministically
> recompute the true numerical Hessian at the SAVED converged
> corrected-region theta (central differences on `compute_gradient_joint`,
> P3a YAML, corrected split stem) — a fixed-theta evaluation, NOT a solve,
> NOT a re-estimation, and ONLY at the saved converged theta. Report the
> sub-block eigenvalues and signs (with a numerical-tolerance statement),
> the VCV sub-block conditioning, and confirm the recomputed Hessian
> condition number ≈ 3.316e9. Adjudicate S5 (PASS if no negative
> eigenvalues in the GSUR-region Hessian sub-block).
>
> S6 — preference-block comparison to M1-clean. Use the verdict-selected
> M1-clean run
> (`.../ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json`);
> if a different M1-clean artifact is used, verify and document
> bit-identity to it. Build the per-parameter Δ table (absolute, relative)
> for the shared preference block, focusing on `beta_c_sm`, `beta_c_sf`,
> `theta_c_singles`, `beta_ll`, and the leisure parameters; flag breaches
> of max |Δ| < 10%. For the singles-consumption block, report the three
> parameters' robust and Hessian SEs, and profile the joint LL in
> `theta_c_singles` at the saved theta (vary only that coordinate, hold
> others fixed, existing likelihood code — deterministic, no
> optimisation) to judge genuine re-identification vs weak-identification
> drift. Adjudicate S6.
>
> S8 — negative-variance enumeration. Enumerate the five negative-variance
> parameters from the Hessian-based variance object (diag(H⁻¹) on the
> 54×54 true Hessian; recompute deterministically at the saved theta if
> not saved). Name them; report each one's Hessian-based variance sign and
> robust SE; identify the two beyond M1-clean's three (`beta_c_sm`,
> `beta_c_sf`, `theta_c_singles`); locate them relative to the
> singles-consumption and region blocks; connect to S6 and S5. Adjudicate
> S8.
>
> HALT conditions: only pre-repair VCVs found; corrected theta not
> loadable; any Hessian recomputation attempted at anything other than the
> saved converged corrected-region theta; a VCV sub-block near-singular
> and inverted without disclosure; M1-clean baseline not the
> verdict-selected run and bit-identity unverifiable; any
> solver/re-estimation/welfare/SA2/canonical/M1-clean/spec/S10-S11 action.
>
> Save the report as
> `Results/JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md`,
> recording the per-criterion adjudication (S4/S5/S6/S8) with deciding
> numbers; the S4 Wald (all three VCVs) with conditioning; the S5
> eigenvalues with the Hessian source stated and the no-optimisation
> confirmation; the S6 Δ table, M1-clean artifact path, and
> singles-consumption diagnosis with the LL profile; the S8 enumeration
> and M1-clean comparison; the input artifacts; any halt; a "what was not
> executed" section; and the required final statements. Write outputs to
> versioned/documented paths.

Output to save: the diagnostics report at
`Results/JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md`, plus
any small computed artifacts (the Wald statistics, the eigenvalue lists,
the Δ table, the LL-profile values) at documented paths.

What to do next: return the diagnostics report to the project chat for an
**updated SA2-readiness verdict** that re-scores S4, S5, S6, S8. If all
four clear, the next gate is a separately-authorised S10/S11 simulation;
only if S1–S11 then all clearly pass is the SA2 verdict drafted. Welfare,
canonical promotion, and M1-clean displacement remain gated throughout.

---

**Required final statements**

- **The narrow post-estimation diagnostics for S4, S5, S6, and S8 are
  authorized**, using only the saved corrected-region artifacts (the three
  cluster-robust VCV `.npy` files, the SE JSONs, the estimation result
  JSONs) and the verdict-selected M1-clean baseline, with deterministic
  recomputation of the true Hessian and the `theta_c_singles` LL profile
  permitted ONLY at the saved converged corrected-region theta.

- **No solver is run, no re-estimation is performed**, and no Hessian or
  likelihood is evaluated at any point other than the saved converged
  corrected-region theta.

- **Welfare computation is NOT authorized**, and **no SA2 verdict is
  issued.** Even if S4/S5/S6/S8 all clear, S10/S11 simulation remains a
  later separate gate before any SA2 verdict.

- **No output is promoted to canonical status**, and **only
  corrected-region artifacts are used** — never pre-repair pooled
  artifacts.

- **M1-clean 2016 remains the active JMP baseline**, displaced only by a
  future SA2 verdict.
