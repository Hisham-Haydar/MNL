# JMP Pooled P3a — Corrected-Region Re-Estimation Authorization v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Specification class: re-estimation authorization memo. This memo
authorises a single three-start re-estimation of the unchanged
`ruro_occ_P3a_pooled` specification against the corrected
(region-repaired) estimation-ready split stem, with full solver-artifact
capture and the standing post-estimation diagnostic and inference
requirements. It does NOT authorise welfare, an SA2 verdict, canonical
promotion, or any displacement of M1-clean 2016. After the
re-estimation, the immediate next gate is a fresh strict post-estimation
review / SA2-readiness verdict — not the SA2 verdict itself.

Reference documents:
- `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_report_v1.md` (the completed
  region repair — R1/R2 applied, V1–V9 PASS, defective split archived)
- `Results/P3a/pooled_P3a/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md` (the
  post-repair diagnostic — cause-B defect resolved; region dummies
  wired, full-rank, gradient-relevant)
- `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_post_estimation_review_v1.md` (the prior strict
  review that withheld SA2 on region non-identification)
- `Results/P3a/pooled_P3a/JMP_pooled_P3a_estimation_report_v2.md` (the previous,
  pre-repair pooled estimation — now pre-repair evidence only)
- `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and
  `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md`
  (the standing estimation authorization and its sequencing/artifact
  corrections, carried forward unchanged in substance)
- `Results/P3a/pooled_P3a/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md` (the
  diagnostic that traced the original defect)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to authorise the re-estimation of the
corrected pooled P3a model so that the seven region dummies
`beta_E_drgn2`–`beta_E_drgn8`, which were exactly non-identified in the
previous run because of an all-NaN couples input column, are estimated
on data where they are now populated, wired into the couples
market-opportunity index, and gradient-relevant. The specification is
unchanged; only the data has been corrected. The re-estimation re-runs
the same three-start protocol, captures the GAMSPy/CONOPT solver
artifacts that the previous run did not surface, computes Hessian-based
and true-Hessian cluster-robust standard errors, and reruns the T3/T4/T5
inference diagnostics, so that the next strict post-estimation review can
adjudicate the region criteria (S4, S5) on real evidence rather than on
a flat ridge.

The memo authorises exactly this re-estimation and its required
reporting. It carries forward, unchanged in substance, the standing
authorization's specification, cluster key, income rule, three-start
design, halt conditions, and not-authorized scope; it adds the corrected
data input, the explicit pre-solver region-wiring sanity checks, and the
solver-artifact / CONOPT-diagnostic reporting requirements. It does not
pre-judge whether the region dummies are statistically significant — that
is the empirical question the re-estimation exists to answer — and it
does not authorise welfare, SA2, canonical promotion, or M1-clean
displacement.

---

## 2. Current status

The region repair is complete and corroborated by two independent
documents.

R1 (couples region-dummy data-build fix) and R2
(`precompute_data_couples` value-presence guard) are applied. The
defective couples split (all-NaN `reg_nuts1_2`–`reg_nuts1_8`) has been
archived to
`Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet`
and replaced with a regenerated couples split in which the seven region
dummies are derived from `drgn1` (0 NaN, binary, `reg_nuts1_k == 1[drgn1
== k]` exactly, region 1 omitted). All validation checks V1–V9 PASS. The
precompute now produces non-zero `data.reg2`–`data.reg8` (55,437–134,900
non-zero rows per region), and the gradient-relevant product
`reg_k × (working_male + working_female)` is non-zero for 55,437–133,537
rows per region. The post-repair couples design (7 region dummies + 2
year indicators) is full-rank (9/9) and well-conditioned (κ = 3.195),
with no collinearity introduced. No solver was run in the repair; no
welfare, no SA2, no canonical promotion; M1-clean 2016 remains the active
baseline.

The corrected data is therefore ready for re-estimation, and this memo
provides the authorization that the repair report identified as the next
gate.

---

## 3. Why re-estimation is now required

Re-estimation is required because the previous pooled estimate is
contaminated in the region block by a data defect that has since been
fixed, and the region criteria cannot be adjudicated without re-running
the solver on corrected data.

The prior strict post-estimation review withheld the SA2 verdict
specifically because the seven region dummies were exactly
non-identified: three starts reached the identical joint LL
(−57,280.6213) with the region dummies sitting at arbitrary values
(Start 2 at exactly 0.000; Starts 1 and 3 at different non-zero vectors).
The diagnostic established that this was not structural redundancy but a
zero-gradient artifact of an all-NaN couples input. With the input now
corrected and the gradient non-zero in all seven region directions, the
likelihood surface in the region subspace is materially different from
the one the previous run optimised over. The previous converged theta,
its region-block values, and the SA2 region criteria (S4 joint Wald, S5
eigenvalue-sign) are all computed on the defective surface and cannot be
carried forward. Only a fresh estimation on the corrected data can
produce region estimates and a region-block Hessian that mean anything.

A second, smaller reason: the previous run did not surface the
GAMSPy/CONOPT solver artifacts (solver log, listing, RGmax / reduced-
gradient trace, solver and model status). Those diagnostics are needed to
confirm the corrected run converged cleanly in the region subspace rather
than terminating on a flat or near-flat ridge — exactly the failure mode
the repair targets. The re-estimation must capture them.

---

## 4. What changed since the previous pooled estimation

What changed is the **data**, and only the data (plus the precompute
guard that reads it). The specification is unchanged.

- **Couples region-dummy columns.** Previously all-NaN
  (743,800/743,800), zeroed by `fillna(0.0)` in precompute. Now derived
  from `drgn1`: valid binary float, 0 NaN, exact one-region-per-household
  partition, region 1 omitted.
- **Precompute guard.** `precompute_data_couples` previously took the
  direct `reg_nuts1_*` path on schema presence and silently zeroed the
  region block. It now takes the direct path only on value presence
  (present + non-missing + non-degenerate), falls back to `drgn1` when
  the direct columns are absent/all-NaN/all-zero, and raises `ValueError`
  if no usable source exists.
- **Estimation-ready split stem.** The couples split, the singles split,
  and the `__mnlmeta.json` were regenerated from the same unified source
  in one build run; the singles content is identical to the pre-repair
  version (its region dummies were already valid); the metadata carries a
  `region_dummy_repair` note. The defective couples split is archived.

What did NOT change: the specification YAML
(`estimation_spec_ruro_occ_P3a_pooled.yaml`, 55 parameters, `theta_c`
fixed at 0.0 for couples, FR_2016 reference year, the seven region
shifters and two year shifters all `applies_to: household`,
`interaction: [working]`); the cluster key (`idorighh`); the income rule
(GA15); the singles `applies_to: "household"` guard (region dummies
correctly enter only through the couples index — by design, confirmed in
diagnostic v2); the solver; the three-start design; and the
not-authorized scope.

---

## 5. Why the previous pooled estimation report is now pre-repair evidence only

`Results/P3a/pooled_P3a/JMP_pooled_P3a_estimation_report_v2.md` remains a valid record
of *what was estimated on the defective data*, but it is **pre-repair
evidence only** and must not be used as final evidence on the region
block or as the basis for any SA2 region adjudication.

Concretely: the report's seven region-dummy point estimates are
arbitrary points on a flat ridge and have no economic meaning; their
machine-scale robust SEs (~10⁻¹⁴–10⁻¹⁵) are non-inferential numerical
noise; the report's S4 (region Wald) and S5 (region eigenvalue-sign) were
correctly marked INDETERMINATE because the region block was
non-identified. None of these region results transfers to the corrected
model. The previous report's findings on the *identified* parameters (the
GSUR loading −1.198 at t = −6.70, the leisure block, the year effects,
objective stability across starts) are informative as priors for what the
corrected run should reproduce, but even these must be re-confirmed on the
corrected data: changing the couples region columns changes the couples
likelihood, so the corrected optimum need not reproduce the previous
identified-block values exactly, and the re-estimation must be evaluated
on its own converged output. The previous report is superseded for
region inference and is a comparison reference, not a substitute, for the
identified block.

The defective archived couples split must not be used as an input to the
re-estimation (§6, §15).

---

## 6. Corrected data input

**Data input (authorized):** the corrected estimation-ready split-stem
base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`
(the estimator appends `__singles.parquet`, `__couples.parquet`,
`__mnlmeta.json`). This is the regenerated, region-repaired stem
validated V1–V9.

Conservation carried forward and to be re-confirmed at load: singles
500,700 rows; couples 743,800 rows; total 1,244,500; 12,445 household-year
choice sets; 9,657 unique `idorighh` clusters; 100 alternatives per
choice set with exactly one chosen.

**Prohibited inputs.** The re-estimation must NOT use:
- the defective archived couples split
  `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet`
  (or any pre-repair archive copy);
- the unified `fr_p3a_gsurv2_harmonised.parquet` directly (the estimator
  consumes the split stem; the unified parquet's couples region columns
  are themselves all-NaN — it is the un-split source of the defect);
- any other pre-repair or un-validated stem.

Using any prohibited input is a halt condition (§16, H7).

---

## 7. Specification to estimate

**Specification (unchanged):** `ruro_occ_P3a_pooled`, from
`scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`.

55 parameters: the 53 M1-clean shared parameters plus `beta_E_y2015` and
`beta_E_y2017`; `theta_c` fixed at 0.0 for couples
(`couples_fixed_box_cox_exponent: 0.0`), hence 54 free positions in the
inference subspace; FR_2016 the reference year; the seven region-dummy
market-opportunity shifters `beta_E_drgn2`–`beta_E_drgn8` (variables
`reg_nuts1_2`–`reg_nuts1_8`, `applies_to: household`, `interaction:
[working]`, region 1 omitted) and the two year shifters with the same
structure.

The YAML is NOT modified by this memo. No region shifter is dropped, no
parameter is added or removed, no bound is changed. This is a
re-estimation of the identical specification on corrected data — the
controlled comparison that isolates the effect of the region repair.

---

## 8. Required pre-solver sanity checks

Before the solver is invoked for any start, the run must confirm the
following on the corrected stem, and HALT if any fails (these guard
against re-running on defective or mis-wired data):

- **(PS1) Couples region columns valid.** `reg_nuts1_2`–`reg_nuts1_8` in
  the couples split are non-missing (0 NaN) and not all-zero; each is
  binary; the seven plus the omitted region 1 form an exact
  one-region-per-household partition consistent with `drgn1`
  (`reg_nuts1_k == 1[drgn1 == k]`).
- **(PS2) Precompute produces non-zero region arrays.**
  `precompute_data_couples` on the corrected couples split takes the
  direct `reg_nuts1_*` path (value-presence guard satisfied) and yields
  non-zero `data.reg2`–`data.reg8` (the documented 55,437–134,900
  non-zero rows per region).
- **(PS3) Region dummies enter the couples market-opportunity index.**
  The product `data.reg_k × (data.working_male + data.working_female)` is
  non-zero (55,437–133,537 rows per region), so `beta_E_drgn_k` receives
  a non-zero gradient contribution. (The singles index does not carry
  region dummies — the `applies_to: "household"` guard is correct by
  design; identification is through couples, so this check is on the
  couples index specifically.)
- **(PS4) Cluster key.** `cluster_id == idorighh` on both split files;
  the strictness safeguard is active; no silent `idhh` fallback.
- **(PS5) Income routing (GA15).** Singles read `ils_dispy_real`
  (non-null for all singles rows); couples read `ils_dispy_male` /
  `ils_dispy_female`; the couples consumption path uses `c_norm` and does
  not read `ils_dispy_real`.

PS1–PS3 are the region-specific additions for this run; PS4–PS5 are the
carried-forward GA13/GA15 confirmations. All five must pass before the
first solver call.

---

## 9. Starts to run

Three starts, identical in design to the standing authorization:

1. **Start 1 — M1-clean warm start.** Initialise from the M1-clean
   converged results, mapping the 53 shared parameters by name to the 55
   pooled positions, with `beta_E_y2015 = 0.0` and `beta_E_y2017 = 0.0`
   (spec defaults). (`--warm-start` from the M1-clean results / 
   `--init-params` from the M1-clean `estimation_results.json`, per the
   established orchestrator path.)
2. **Start 2 — spec defaults.** Cold start at the YAML `initial_values`
   for all 55 parameters (`--warm-start none`).
3. **Start 3 — perturbed M1-clean warm start.** Seed 42, perturbation
   ±0.1, applied to the Start 1 warm-start vector.

Note on Start 3 base vector: the previous run perturbed the *converged*
Start 1 theta (documented deviation PD1). For this run the intended base
is the M1-clean warm-start vector; if the orchestrator reuses the prior
perturbed-init path, the base vector used must be documented explicitly
in the report so the protocol is unambiguous. Either base is acceptable
for a stability check provided it is documented; the report must state
which was used.

The three starts are the multi-start convergence check: agreement on the
identified block and — the question of interest — whether the now-wired
region dummies converge to consistent, identified values or still wander
on a (now-expected-to-be-resolved) ridge.

---

## 10. Solver artifact and CONOPT/GAMSPy diagnostics requirement

For each start, the run must capture the GAMSPy/CONOPT solver artifacts
using `--save-solver-artifacts`, and save and document, per start:

- the **solver log** (`solver.log`) path;
- the **GAMS listing** (`solver.lst` / `.lst` listing file) path.

The corrected estimation report must report the following CONOPT/GAMS
diagnostics, per start, **when available** from the artifacts:

- **RGmax / reduced-gradient trace** — the CONOPT maximum reduced
  gradient at termination (and its trajectory if the listing provides
  it). This is the solver's own optimality measure.
- **solver status** and **model status** (e.g., NormalCompletion;
  OptimalLocal / LocallyOptimal).
- **maximum infeasibility** at termination, if available.
- **iteration count**.
- **termination message**.

**Critical distinction (do not conflate).** CONOPT's RGmax (the reduced
gradient of the GAMS/CONOPT optimisation) is a different object from the
Python likelihood-gradient / score diagnostic used in the cluster-robust
SE machinery (the `compute_gradient_joint` / `compute_scores_joint`
score, whose sum equals −grad of the positive LL, T1). The report must
present CONOPT RGmax as a solver-side optimality diagnostic and the
Python score/gradient as the inference-side diagnostic, and must not
report one under the other's name or treat them as interchangeable. Both
are reported; they are labelled distinctly.

The region-block reading of these diagnostics is the point: a clean
CONOPT termination with small RGmax across all seven region directions is
the solver-side confirmation that the region block is now identified,
complementing the Python-side T3/T4/T5 (§11) and the gradient-relevance
established in the repair.

---

## 11. Cluster-robust SE requirements

After each converged start, the run must compute, using the corrected
data and the converged theta:

- **Hessian-based SEs** — from the true numerical Hessian of the negative
  log-likelihood at the converged theta (central differences on
  `compute_gradient_joint`), with the `free_mask` excluding the fixed
  `theta_c` and any bounded parameter.
- **Cluster-robust (sandwich) SEs** — `V = H⁻¹ B H⁻¹` with the **true
  Hessian** as bread (NOT the dummy `H = 0.1·I` of the smoke test, NOT
  any placeholder theta), and the meat `B` assembled from per-choice-set
  scores aggregated to the `idorighh` cluster key.

Run `run_cluster_robust_se.py --mode post-estimation` against each start's
`estimation_results.json` on the corrected stem, and rerun the three
inference diagnostics:

- **T3** — confirm the meat assembly aggregates over exactly **9,657**
  unique `idorighh` clusters on the full corrected dataset.
- **T4** — robust-SE positivity for all free parameters at the converged
  theta. The region-block reading is decisive here: in the previous run
  the seven region SEs were machine-scale noise (non-inferential); in the
  corrected run, genuine positive region SEs of ordinary magnitude are
  the inference-side signal that the region dummies are now identified.
  The report must state the region-dummy robust SEs explicitly and
  whether they are now of inferential magnitude.
- **T5** — robust-vs-Hessian comparison for all 55 parameters, with the
  per-parameter ratio, flagging any robust SE below its Hessian SE.

Persist each start's robust VCV (the `.npy` path) and document it.

---

## 12. Required enhanced post-estimation reporting

If the enhanced post-estimation reporting path is available, run it for
each start using:

- `--cluster-se-json` — the start's cluster-robust SE JSON;
- `--solver-log` — the start's `solver.log`;
- `--listing-file` — the start's GAMS `.lst` listing;
- `--gamspy-diagnostics` — the GAMSPy/CONOPT diagnostics (RGmax, solver
  status, model status, infeasibility, iterations, termination message);
- `--gradient-diagnostics` — the Python likelihood-gradient / score
  diagnostics (kept distinct from CONOPT RGmax per §10).

The enhanced reporting consolidates, per start, the point estimates, the
Hessian-based and cluster-robust SEs, the solver-side CONOPT diagnostics,
and the inference-side gradient/score diagnostics into the estimation
report. If the enhanced reporting path is not available, the report must
still contain all of the same artifacts assembled manually from the
per-start JSONs, logs, and listings; "enhanced reporting unavailable" is
not a waiver of the content requirement.

---

## 13. Required post-estimation diagnostics

The corrected estimation report must record, for each converged start,
the full diagnostic set carried forward from the standing authorization
(§13, §14, D1–D15) plus the region-specific reads:

- **Convergence (D1–D3):** per-group solver success, status, iterations,
  wall time; the joint log-likelihood; the cross-start parameter-vector
  agreement (L∞ on the identified block, and — newly meaningful — on the
  region block).
- **CONOPT/GAMS diagnostics (per §10):** RGmax / reduced-gradient,
  solver/model status, infeasibility, iterations, termination — per
  start, distinctly labelled from the Python gradient.
- **Inference (D9–D11 / T3–T5):** 9,657-cluster confirmation; robust-SE
  positivity (with the region-dummy SEs called out explicitly);
  robust-vs-Hessian comparison.
- **Region identification read (new, the purpose of this run):** whether
  the seven region dummies converge to consistent values across the three
  starts (contrast with the previous flat ridge); their robust SEs and
  t-ratios; and the region-block Hessian sub-block conditioning (the
  input to a future S4/S5 adjudication). The report states the evidence;
  it does NOT issue the S4/S5 verdict (that is the next review's job).
- **Carry-forward confirmations (D12–D15):** income routing (GA15);
  cluster key (`idorighh`); no welfare computed; M1-clean active, no
  canonical promotion.
- **Identified-block reproduction:** whether the corrected run reproduces
  the previous run's identified-block results (GSUR loading, leisure
  block, year effects, objective stability), reported as a comparison,
  with any material change flagged.

The full cluster-robust SE artifact list required by authorization
correction C2 (converged theta by start; true-Hessian bread source
explicitly identified; T3 cluster count; robust SE vector; robust VCV or
path; T4; T5; no-welfare; M1-clean-active) must be included.

---

## 14. What is authorized

The following are authorized by this memo, and only these.

- **(A1)** Run the three-start re-estimation of `ruro_occ_P3a_pooled`
  (§7, §9) against the corrected split stem
  `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready` (§6), after
  the pre-solver sanity checks PS1–PS5 pass (§8).
- **(A2)** Capture the GAMSPy/CONOPT solver artifacts per start with
  `--save-solver-artifacts`, and save/document each start's `solver.log`
  and `.lst` listing (§10).
- **(A3)** Compute Hessian-based and true-Hessian cluster-robust SEs and
  rerun T3/T4/T5 after each converged start (§11).
- **(A4)** Run the enhanced post-estimation reporting (or assemble the
  equivalent content) with the five documented flags (§12).
- **(A5)** Write the corrected estimation report (§17) and the per-start
  artifacts (results JSONs, SE JSONs, VCV `.npy`, solver logs, listings)
  to versioned/documented paths.

---

## 15. What is not authorized

The following are NOT authorized by this memo. Each remains gated.

- **(N1) Welfare computation.** Not run; separately gated behind an
  accepted SA2 verdict.
- **(N2) An SA2 verdict.** Not issued. After re-estimation the immediate
  next gate is a fresh strict post-estimation review / SA2-readiness
  verdict; the SA2 verdict is drafted only if that review passes.
- **(N3) Canonical promotion.** No output is promoted to canonical
  status. The corrected estimates are candidate results at versioned
  paths.
- **(N4) M1-clean displacement.** M1-clean 2016 remains the active JMP
  baseline.
- **(N5) Specification modification.** The pooled YAML is unchanged; no
  region shifter is dropped, no parameter added/removed, no bound
  changed. (In particular, the no-region design is NOT adopted — the
  whole point of this run is to estimate the region block on corrected
  data.)
- **(N6) Using prohibited inputs.** The defective archived couples split,
  the unified parquet directly, and any pre-repair/un-validated stem are
  not used (§6).
- **(N7) Any new estimation beyond the three authorized starts** of this
  one specification on this one corrected stem — no alternative pooled
  specifications, no additional years, no other countries.
- **(N8) Pre-judging the region result.** The report records the region
  evidence; it does not declare the region dummies significant or issue
  S4/S5. That adjudication is the next review's.

---

## 16. Halt conditions

The re-estimation halts under the following conditions. Each halt
preserves the artifacts produced up to the halt and requires diagnosis
before proceeding.

- **(H1) Pre-solver sanity check fails.** If any of PS1–PS5 (§8) fails —
  region columns not valid, precompute zeros the region arrays, region
  dummies not in the couples index, cluster key wrong, income routing
  wrong — the solver is NOT invoked and the run halts.
- **(H2) A start fails to converge.** If any start does not reach solver
  success / NormalCompletion / a locally optimal model status, the run
  halts and reports the solver diagnostics (RGmax, status, infeasibility,
  termination) for the failed start.
- **(H3) Region block still flat.** If, despite the corrected data, the
  three starts still produce arbitrary region-dummy values at identical
  LL with machine-scale region SEs (the previous flat-ridge signature),
  the run halts and reports: this would indicate the repair did not, in
  fact, restore identification, contradicting diagnostic v2, and must be
  re-diagnosed before any further step.
- **(H4) Cluster-robust SE computation fails.** If T3 ≠ 9,657, or a free
  parameter's robust SE is non-positive at the converged theta with the
  true Hessian (T4 fail), or the sandwich errors, the run halts.
- **(H5) Income routing or cluster key corrupted at runtime.** If the
  couples consumption path reads `ils_dispy_real`, or income is mixed, or
  a silent `idhh` fallback occurs, the run halts.
- **(H6) Solver artifacts not captured.** If `--save-solver-artifacts`
  does not produce the per-start `solver.log` and `.lst` listing, the run
  halts: the CONOPT diagnostics are a required output of this run, not
  optional.
- **(H7) Welfare, SA2, canonical, M1-clean displacement, spec
  modification, or a prohibited input attempted.** If the run would do
  any of these, it halts: none is authorised (§15).

---

## 17. Required estimation report

The re-estimation must be recorded in a report saved as
`Results/P3a/pooled_P3a/JMP_pooled_P3a_corrected_region_estimation_report_v1.md`. The
report must include:

- the execution verdict (all three starts converged / a halt, with the
  halting condition named) and the authorization provenance (this memo,
  the standing authorization and its correction, the repair report and
  diagnostic v2);
- the corrected data input confirmed (the regenerated stem; the
  prohibited inputs explicitly not used) and the pre-solver sanity checks
  PS1–PS5 with results;
- the per-start convergence and objective values (D1–D3);
- the per-start CONOPT/GAMS diagnostics — RGmax / reduced-gradient,
  solver status, model status, max infeasibility (if available),
  iteration count, termination message — distinctly labelled from the
  Python likelihood-gradient / score diagnostic (§10), with the
  `solver.log` and `.lst` paths documented;
- the full cluster-robust SE artifact set per start (correction C2 list):
  converged theta; the true-Hessian bread source, explicitly identified
  as the true Hessian (not the dummy, not a placeholder theta); T3
  9,657-cluster confirmation; the robust SE vector; the robust VCV or its
  documented path; T4 positivity; T5 robust-vs-Hessian; no-welfare
  confirmation; M1-clean-active confirmation;
- the **region identification read** (the purpose of this run): the seven
  region-dummy estimates and their cross-start consistency, their robust
  SEs and t-ratios, and the region-block Hessian conditioning — presented
  as evidence for the next review, with NO S4/S5 verdict issued here;
- the identified-block comparison to the previous (pre-repair) report
  (GSUR, leisure block, year effects, objective stability), with any
  material change flagged, and an explicit statement that the previous
  report is pre-repair evidence only on the region block;
- any halt (§16) and its diagnosis;
- a "what was not executed" section: no welfare, no SA2, no canonical
  promotion, no M1-clean displacement, no spec modification, no
  prohibited input, no estimation beyond the three authorized starts;
- the required final statements (below).

**Required final statements (to appear in the estimation report):**
- The corrected pooled P3a was re-estimated (three starts) on the
  region-repaired stem; the region dummies are now estimated on
  gradient-relevant data (or the run halted, with the condition named).
- The CONOPT/GAMS solver diagnostics were captured per start and are
  reported distinctly from the Python likelihood-gradient diagnostic.
- True-Hessian cluster-robust SEs were computed and T3/T4/T5 rerun;
  region-dummy SEs are reported explicitly.
- No welfare was computed; no SA2 verdict was issued.
- No output was promoted to canonical status; M1-clean 2016 remains the
  active JMP baseline.

---

## 18. Exact Claude Code estimation prompt

Tool path: **Claude Code** (local re-estimation; invokes the solver).
Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present before starting: the corrected split stem
(`fr_p3a_gsurv2_estimation_ready__singles.parquet`,
`...__couples.parquet`, `...__mnlmeta.json`); the pooled YAML; the
M1-clean `estimation_results.json` (Start 1 warm source); the estimator
`enh_RURO_estimate_FR.py`; the orchestrator
`scripts/maintenance/run_pooled_P3a_estimation.py`; the cluster-robust SE
CLI `run_cluster_robust_se.py`; `estimation_utils.py` (with R2 applied);
the repair report and diagnostic v2; this authorization.

Prompt to use:

> Execute the corrected-region three-start re-estimation of
> `ruro_occ_P3a_pooled` per
> `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md`.
> Use the interpreter `.venv\Scripts\python.exe`. Do NOT compute welfare.
> Do NOT issue an SA2 verdict. Do NOT promote any output to canonical
> status. Do NOT modify the pooled YAML or drop any region shifter. Do
> NOT replace M1-clean 2016. Do NOT use the defective archived couples
> split or the unified parquet directly — use only the corrected stem
> `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`.
>
> PRE-SOLVER (HALT if any fails, do not invoke the solver): confirm
> PS1 couples `reg_nuts1_2`–`reg_nuts1_8` non-missing, binary, not
> all-zero, and `reg_nuts1_k == 1[drgn1 == k]`; PS2
> `precompute_data_couples` yields non-zero `data.reg2`–`data.reg8`
> (direct path, value-presence guard); PS3 `data.reg_k × (working_male +
> working_female)` non-zero so `beta_E_drgn_k` is gradient-relevant; PS4
> `cluster_id == idorighh` (no `idhh` fallback); PS5 income routing —
> singles `ils_dispy_real`, couples `ils_dispy_male`/`ils_dispy_female`,
> couples consumption path does not read `ils_dispy_real`.
>
> RUN three starts of `ruro_occ_P3a_pooled` against
> `--mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`
> with `--spec-config .../estimation_spec_ruro_occ_P3a_pooled.yaml`,
> `--group joint`, `--solver gamspy-conopt`, `--vectorized`, and
> `--save-solver-artifacts`:
> Start 1 = M1-clean warm start (`--init-params` from the M1-clean
> `estimation_results.json`, mapping 53→55 by name, `beta_E_y2015 =
> beta_E_y2017 = 0.0`); Start 2 = spec defaults (`--warm-start none`);
> Start 3 = perturbed M1-clean warm start (seed 42, ±0.1) — document the
> exact base vector used. Save each start's `solver.log` and `.lst`
> listing and document their paths.
>
> AFTER each converged start: compute Hessian-based SEs and true-Hessian
> cluster-robust SEs via `run_cluster_robust_se.py --mode post-estimation`
> on that start's `estimation_results.json` against the corrected stem
> (TRUE Hessian as bread — NOT the dummy Hessian, NOT a placeholder
> theta). Rerun T3 (9,657 clusters), T4 (robust-SE positivity — report
> the seven region-dummy SEs explicitly), T5 (robust-vs-Hessian). Persist
> each robust VCV `.npy`.
>
> REPORT the CONOPT/GAMS diagnostics per start when available: RGmax /
> reduced-gradient trace, solver status, model status, max infeasibility,
> iteration count, termination message — and keep CONOPT RGmax DISTINCT
> from the Python likelihood-gradient / score diagnostic; do not conflate
> them. Run the enhanced post-estimation reporting if available with
> `--cluster-se-json`, `--solver-log`, `--listing-file`,
> `--gamspy-diagnostics`, `--gradient-diagnostics`; if unavailable,
> assemble the same content manually.
>
> HALT conditions: any PS1–PS5 fail (no solver); a start fails to
> converge; the region block is still flat (arbitrary region values at
> identical LL with machine-scale region SEs); T3 ≠ 9,657 or a free T4 SE
> non-positive or sandwich error; income routing or cluster key corrupted
> at runtime; solver artifacts not captured; any welfare/SA2/canonical/
> M1-clean/spec/prohibited-input action attempted.
>
> Save the report as
> `Results/P3a/pooled_P3a/JMP_pooled_P3a_corrected_region_estimation_report_v1.md`,
> including: the per-start convergence and objective values; the per-start
> CONOPT/GAMS diagnostics (distinctly labelled) with log/listing paths;
> the full cluster-robust SE artifact set per start (converged theta;
> true-Hessian bread explicitly identified; T3; robust SE vector; robust
> VCV path; T4; T5; no-welfare; M1-clean-active); the region
> identification read (region estimates, cross-start consistency, robust
> SEs/t-ratios, region-block Hessian conditioning) WITHOUT issuing S4/S5;
> the identified-block comparison to the pre-repair report v2 with
> material changes flagged; any halt and diagnosis; a "what was not
> executed" section; and the required final statements. Write all outputs
> to versioned/documented paths.

Output to save: the estimation report at
`Results/P3a/pooled_P3a/JMP_pooled_P3a_corrected_region_estimation_report_v1.md`, plus
the per-start results JSONs, cluster-robust SE JSONs, robust VCV `.npy`
files, `solver.log` files, and `.lst` listings, and an orchestrator
summary.

What to do next: return the corrected estimation report to the project
chat for a **fresh strict post-estimation review / SA2-readiness
verdict** — the immediate next gate. That review adjudicates whether the
region block is now identified (S4, S5), whether the preference-block
comparison (S6) passes, and whether the SA2 criteria are met; only if it
passes is the SA2 verdict drafted. Welfare, SA2, canonical promotion, and
M1-clean displacement remain gated and are not authorized here.

---

**Required final statements**

- **The corrected-region three-start re-estimation of
  `ruro_occ_P3a_pooled` is authorized** against the region-repaired
  split stem `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`,
  with the unchanged specification, the pre-solver region-wiring sanity
  checks PS1–PS5, GAMSPy/CONOPT solver-artifact capture, true-Hessian
  cluster-robust SEs, and the T3/T4/T5 reruns.

- **The previous pooled estimation report (v2) is pre-repair evidence
  only** on the region block and must not be used as final region
  evidence or as the basis for an SA2 region adjudication; the defective
  archived couples split must not be used as an input.

- **The CONOPT/GAMS solver diagnostics (RGmax, solver/model status,
  infeasibility, iterations, termination) must be captured and reported
  per start, distinctly from the Python likelihood-gradient / score
  diagnostic.**

- **Welfare computation is NOT authorized, no SA2 verdict is issued, and
  no output is promoted to canonical status.** After re-estimation the
  immediate next gate is a fresh strict post-estimation review /
  SA2-readiness verdict.

- **M1-clean 2016 remains the active JMP baseline**, displaced only by a
  future SA2 verdict explicitly promoting an identified pooled
  specification.
