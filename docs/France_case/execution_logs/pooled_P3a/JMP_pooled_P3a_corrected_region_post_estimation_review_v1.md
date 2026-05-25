# JMP Pooled P3a — Corrected-Region Post-Estimation Review v1

*France FR_2015 / FR_2016 / FR_2017 | Strict post-estimation review / SA2-readiness verdict of the corrected-region run*
*Date: 2026-05-22 | Estimation report: Results/JMP_pooled_P3a_corrected_region_estimation_report_v1.md*

Specification class: post-estimation review / SA2-readiness verdict. This
memo adjudicates whether the **corrected-region** pooled P3a estimation
meets the requirements for an SA2 verdict. It is the gate that follows
the corrected re-estimation. It is not the SA2 verdict and does not issue
one. M1-clean 2016 remains the active JMP baseline.

Reference documents:
- `Results/JMP_pooled_P3a_corrected_region_estimation_report_v1.md` (the
  corrected estimation report under review)
- `docs/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md`
  (the authorization the run executed)
- `docs/JMP_pooled_P3a_region_dummy_repair_report_v1.md` and
  `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md` (the
  repair and its post-repair diagnostic)
- `docs/JMP_pooled_P3a_post_estimation_review_v1.md` (the prior review of
  the pre-repair run; the S1–S11 criteria are carried forward unchanged)
- `Results/JMP_pooled_P3a_estimation_report_v2.md` (pre-repair evidence
  only)
- Three corrected SE JSONs (`corrected_start1/2/3_cluster_robust_se.json`),
  the orchestrator summary, and the Start 3 perturbed-init JSON

---

## 1. Verdict

**NOT SA2-ready. The SA2 verdict cannot be issued. M1-clean 2016 remains
the active JMP baseline.**

The corrected run is a clear success on the question the repair was meant
to settle: the region block is now **identified**. All three starts reach
an identical optimum (joint LL −19,084.3313, cross-start L∞ < 10⁻⁸), the
seven region dummies converge to stable, reproducible values with
finite, inferential-magnitude robust SEs (0.34–0.55), and the flat-ridge
signature of the pre-repair run is gone. Five SA2 criteria pass cleanly
(S1, S2, S3, S7, S9).

But identification is not the SA2 bar, and three things block the
verdict. First, the two region criteria the whole repair was for — **S4**
(region joint robust Wald) and **S5** (GSUR-region Hessian eigenvalue
sign) — were **not computed**: the estimation report explicitly deferred
both to "the next review" (§29, §30, §32 of the report). They are now
*computable* from the saved robust VCVs, but they are *unevaluated*, so
S4 and S5 cannot be scored PASS. Second, **S6 fails as written**: the
singles-consumption sub-block sits ~5× from M1-clean with a sign flip in
`theta_c_singles`, exactly the block flagged at high risk in the prior
review, and the corrected report omitted the comparison entirely — the
region repair did not touch this block, so the divergence persists
unaddressed. Third, **S8 is no longer a clean pass**: the in-estimation
negative-variance count rose from M1-clean's 3 to 5, and the report did
not enumerate the 5 or establish they are M1-clean's 3 plus benign
additions.

The disciplined reading: the repair achieved **identification** of the
region block (objective 1), did **not** establish its **statistical
significance** (objective 2 — individually insignificant, jointly
untested), and certainly did not establish its **substantive usefulness**
(objective 3). The next gate is not the SA2 verdict, a new specification,
or a fallback — it is a focused **post-estimation diagnostics**
authorization that computes S4, S5, S6, and S8 from the artifacts already
on disk (no re-estimation), and then the S10/S11 simulation.

---

## 2. Whether re-estimation followed authorization

**Substantially yes, with one recurring documented deviation (Start 3).**

The run executed the authorized specification (`ruro_occ_P3a_pooled`,
unchanged YAML, 55 parameters) against the corrected split stem
`fr_p3a_gsurv2_estimation_ready`, with the prohibited inputs confirmed
unused (the archived defective couples split; the unified parquet
directly). The five pre-solver sanity checks PS1–PS5 passed before the
solver was called. Solver artifacts were captured per start. True-Hessian
cluster-robust SEs and T3/T4/T5 were rerun on each start. No welfare, no
SA2, no canonical promotion; M1-clean confirmed active in all three SE
outputs. The authorized scope was respected.

The deviation: Start 3 perturbed the **converged Start 1 theta**, not the
M1-clean **warm-start vector** that the authorization (§9) specified.
This is the PD1 deviation repeated from the previous run, and the report
documents it (§18, §55). The report's claim that "the authorization
explicitly accepts either base provided it is documented" is not accurate
— the authorization specified the warm-start vector and explained why
(a perturbed near-optimum is a weaker robustness test than a perturbed
seed). The substantive impact is nonetheless limited, because **Start 2
is a genuine independent cold start** from spec defaults (region dummies
at 0.0) that converged to the identical optimum; Start 2, not Start 3,
carries the independent-start burden. So the multi-start robustness
conclusion holds, but Start 3 should be understood as a near-optimum
robustness check, not a third independent start. The recurrence of PD1
should be fixed in the orchestrator before any future run that needs
three genuinely independent starts.

---

## 3. Whether the region repair was correctly carried into estimation

**Yes — confirmed end-to-end, and this is the central success of the
run.**

The pre-solver checks confirm the repair reached the likelihood. PS1: the
couples `reg_nuts1_2`–`reg_nuts1_8` are 0-NaN, binary, and match
`1[drgn1 == k]` exactly, with the documented per-region non-zero counts
(134,900 / 56,000 / 66,300 / 134,900 / 82,800 / 88,700 / 70,500). PS2:
`precompute_data_couples` took the direct value-validated path (the R2
guard) and produced non-zero `data.reg2`–`data.reg8`, with the DEBUG line
"region dummies sourced from reg_nuts1_* columns (direct path)" emitted
in all three starts. PS3: the gradient-relevant product
`reg_k × (working_male + working_female)` is non-zero for 7.5%–18.0% of
couples rows per region. These match the post-repair diagnostic v2
exactly. The region block entered the couples market-opportunity index
with genuine variation; the repair is correctly in force for this run.

---

## 4. Three-start convergence evidence

**Strong.** All three starts: CONOPT4 Normal Completion (status 1),
Locally Optimal (status 2), 0 infeasibilities, 0 evaluation errors,
0 non-optimal residuals, "reduced gradient less than tolerance."

| Start | Init | Solver / model | Joint LL | Iters | Wall |
|-------|------|----------------|----------|-------|------|
| 1 | M1-clean warm (53→55) | NormalCompletion / OptimalLocal | −19,084.3313 | 14 | 820 s |
| 2 | Spec defaults (cold) | NormalCompletion / OptimalLocal | −19,084.3313 | 17 | 1,046 s |
| 3 | Perturbed Start-1 converged (seed 42, ±0.1) | NormalCompletion / OptimalLocal | −19,084.3313 | 20 | 1,058 s |

Per §2, Start 2 is the genuine independent cold start; its convergence to
the identical optimum is the strongest single piece of multi-start
evidence. Start 3's perturbed-near-optimum design makes it a weaker test
than intended but it does not weaken the conclusion.

---

## 5. Objective-value and parameter-vector stability

**Excellent — and decisively better than the pre-repair run on the region
block.**

The joint LL is identical across starts (−19,084.3313). The full
55-vector agrees to L∞ < 10⁻⁸ (theta-norms 10.84814369662677 /
…62335 / …62383, differing at the 11th significant figure). Per the
required interpretation, identical LL across starts is treated as a
success for objective stability (S1). The region block now agrees across
all three starts to 6+ significant figures — the defining contrast with
the pre-repair run, where the region dummies wandered to arbitrary values
at identical LL. There is no remaining flat-ridge signature.

One caveat for §14: this stability is a property of the optimum's
location, not of its conditioning. The vector is found consistently; the
Hessian around it is ill-conditioned (κ ≈ 3.3 × 10⁹). The two facts
coexist and are addressed separately.

---

## 6. Solver diagnostics and CONOPT/GAMS evidence

**Captured per start and clean; the RGmax/Python-gradient distinction is
correctly observed.**

For all three starts the GAMS listing reports CONOPT4 v4.38.2, status 1
(Normal Completion), model status 2 (Locally Optimal), objective
−19,084.3313, 0 infeasibilities, termination "Optimal solution. Reduced
gradient less than tolerance." The seven region-dummy variables carry
marginal = EPS (interior solution, reduced gradient below tolerance) —
the solver-side confirmation that the region block is at an interior
optimum, not on a flat ridge or at a bound. Solver-log and listing paths
are documented per start (report §37); H6 did not fire.

The report correctly keeps the CONOPT reduced-gradient (RGmax) distinct
from the Python likelihood-gradient / score (`compute_gradient_joint`,
used in the sandwich), stating they are different objects from different
tools that must not be conflated (report §13, §43). This requirement is
satisfied.

One genuine flag surfaces here for §14: `beta_l0_m` is at its lower bound
(1e−6) with a non-EPS marginal of −10.137 (a live shadow price). It is
excluded from the free mask (n_free = 54). This is a bound-active
parameter, not an interior optimum, and is the proximate source of the
in-estimation negative-variance warning (§14, S8).

---

## 7. Cluster-robust SE validity

**Valid. True-Hessian sandwich; T3/T4/T5 PASS on all three starts.**

The bread is the true numerical Hessian (central differences on
`compute_gradient_joint` at the converged theta, explicitly not the dummy
H = 0.1·I). T3 = 9,657 unique `idorighh` clusters (PASS, all starts); T4 =
0 non-positive robust SEs among 54 free parameters (PASS, all starts);
T5 = 0 robust SEs below their Hessian SE (PASS, all starts). The robust
VCVs are saved per start. The region-block robust SEs are finite and
positive (0.34–0.55), the inference-side confirmation that the gradient
defect is resolved.

The inference machinery is sound. Note this is a statement about SE
*validity*, not about what the SEs *show* for the region block (§9) or
about Hessian conditioning (§14).

---

## 8. Region-dummy identification after repair

**Identified — decisively. This is the repair's success and must not be
confused with significance.**

Four independent signatures confirm identification: (a) the seven robust
SEs are finite and of inferential magnitude (0.34–0.55), versus
machine-scale O(10⁻¹⁴) pre-repair; (b) the seven estimates agree across
all three starts to 6+ significant figures (no wandering); (c) the CONOPT
region marginals are EPS at an interior solution; (d) the post-repair
design is full-rank (9/9, κ = 3.195) with the region block gradient-
relevant for 7.5%–18% of couples rows. The likelihood is no longer flat
in the region directions. The prior review's INDETERMINATE-due-to-non-
identification status for S4 and S5 is therefore **resolved at the
identification level**: the tests are now well-posed and computable.

This is identification only. Whether the identified block is
statistically significant (§9) and whether it is substantively useful
(§24) are separate questions, addressed below. Per the required
interpretation, the individual insignificance documented in §9 is **not**
evidence of non-identification — the block is identified; its individual
effects are merely imprecise.

---

## 9. Region-dummy statistical evidence

**Individually insignificant; jointly UNEVALUATED. This is the crux of
the non-readiness.**

Region estimates (reference = region 1, Île-de-France), with robust SEs
and t-ratios:

| Param | Region | Estimate | SE_robust | t_robust |
|-------|--------|----------|-----------|----------|
| `beta_E_drgn2` | Nord–Ouest | 0.3965 | 0.3845 | 1.03 |
| `beta_E_drgn3` | Nord–Est | 0.3500 | 0.3991 | 0.88 |
| `beta_E_drgn4` | Sud–Est | 0.6416 | 0.5537 | 1.16 |
| `beta_E_drgn5` | Grand–Ouest | 0.4310 | 0.4427 | 0.97 |
| `beta_E_drgn6` | Centre–Est | 0.3577 | 0.4682 | 0.76 |
| `beta_E_drgn7` | Méditerranée | 0.3671 | 0.4370 | 0.84 |
| `beta_E_drgn8` | Outre-mer | 0.1675 | 0.3370 | 0.50 |

All seven point estimates are positive (higher market opportunity outside
Île-de-France), largest in Sud–Est (0.64). **None is individually
significant at 5%** (all |t| ≤ 1.16).

The **joint** question — S4, whether the seven are jointly significant via
a robust Wald test — is the one that matters for the region opportunity
dimension, and **the estimation report did not compute it** (report §29,
§32 explicitly defer it). Per the required interpretation, finite region
SEs are **not** sufficient evidence that S4 passes, and individual
insignificance does **not** settle the joint question (correlated
estimates can be jointly significant even when individually weak, and
vice versa). The robust VCV is saved, so the joint Wald is computable
without re-estimation — but until it is computed, **S4 is UNEVALUATED**,
not PASS and not FAIL. My own read of the magnitudes (all |t| ≤ 1.16,
estimates of similar sign and size) suggests joint significance at p<0.01
is unlikely, but I will not pre-judge a test that can simply be run.

---

## 10. GSUR coefficient result

**Recovered and strongly significant — the load-bearing opportunity
parameter survives the corrected pooling. S2 and S3 PASS.**

`beta_E_gsur` = −1.1999, robust SE = 0.1911, t = −6.28 (p < 0.001).
Magnitude is 90.3% of the M1-clean −1.329, well within the 50% tolerance.
The estimate is essentially unchanged from the pre-repair pooled value
(−1.198), as expected: GSUR is unaffected by the region-dummy defect. The
slight SE increase versus the pre-repair run (0.191 vs 0.179, t −6.28 vs
−6.70) is immaterial; the coefficient remains the robustly identified
core of the opportunity construct.

---

## 11. Year-effect estimates

**Both small and insignificant — consistent with the pooling assumption,
not a problem.**

`beta_E_y2015` = −0.0591 (robust SE 0.2573, t = −0.23);
`beta_E_y2017` = 0.1554 (robust SE 0.2701, t = 0.58); FR_2016 reference.
Identical across starts. Neither differs significantly from zero,
indicating limited year-to-year shift in the market-opportunity structure
over 2015–2017, which supports rather than undermines pooling. The year
effects are not an SA2 criterion in their own right.

---

## 12. Preference-parameter comparison to M1-clean

**Mixed, and the adverse half is a hard obstacle the corrected report
omitted. This drives S6.**

The leisure block is stable and precisely estimated: `theta_l_m` −0.682
(t −18.1), `theta_l_f` −0.658 (t −20.9), `theta_l_sm` −0.719 (t −11.7),
`theta_l_sf` −0.702 (t −12.1) — all close to M1-clean. The couples
consumption weight `beta_c` (4.312) is within ~8% of M1-clean (4.000).
These are healthy.

The **singles-consumption sub-block has not moved back** — it remains the
same large departure from M1-clean flagged in the prior review, because
the region repair did not touch it:

| Param | M1-clean | Corrected pooled | Change |
|-------|----------|------------------|--------|
| `beta_c_sm` | 0.5537 | 2.7331 | ≈ 4.9× |
| `beta_c_sf` | 0.5056 | 2.3513 | ≈ 4.65× |
| `theta_c_singles` | −1.0485 | +0.0392 | sign flip + magnitude collapse |

These are stable across the three corrected starts (not within-fit noise),
but they breach a literal S6 threshold ("preference block max |Δ| < 10%
vs M1-clean") by a wide margin, driven entirely by this block. The
corrected report's §33 compared GSUR and leisure but **omitted the
singles-consumption comparison entirely** — i.e., it was silent on
precisely the block that was the prior review's chief concern. Whether
this reflects genuine multi-year re-identification of singles consumption
curvature or weak-identification drift cannot be settled from the point
estimates alone; it requires the explicit comparison plus a look at the
block's conditioning (related to §14, S8). Either way, S6 is not
satisfied as written.

---

## 13. Opportunity-parameter comparison to M1-clean

**The opportunity side is now healthier than the pre-repair run on the
region dimension; GSUR carries the construct.**

`beta_E` (opportunity intercept) −2.398 vs M1-clean −2.499 (≈4% smaller).
`beta_E_gsur` recovered (§10). The **region dummies are now identified and
estimated** (§8) rather than collapsed — the pre-repair run had lost this
dimension entirely; the corrected run restores it to the model, even if
its individual effects are imprecise (§9). Hours shifters (`beta_h_*`) and
occupation shifters (`beta_occ_*`) are sensible and largely significant
(occupation t-ratios 5–15; `beta_h_ft` t = 16.5). Net: the opportunity
block is structurally intact and the region dimension is back in play —
the open question is its joint significance (S4), not its presence.

---

## 14. Hessian and numerical diagnostics

**Two genuine concerns the report partly explained away: ill-conditioning
and a risen negative-variance count.**

The full 54×54 true Hessian has condition number κ ≈ 3.316 × 10⁹,
consistent across starts. This is moderately-to-severely ill-conditioned
and is not specific to the region block. It does not invalidate the
sandwich SEs (T4/T5 PASS), but it is the reason the in-estimation crude
`diag(H⁻¹)` produced **5 negative-variance parameters** in all three
starts.

The report (§36) frames the 5 as a benign artifact "resolved by the
true-Hessian sandwich." That is correct *for SE positivity* (T4 PASS) but
it does **not** dispose of criterion **S8** as written ("no new negative-
diagonal Hessian entries beyond M1-clean's 3"). M1-clean had 3; the
corrected pooled run has 5; the report did not enumerate which 5, nor
confirm they are M1-clean's 3 plus benign additions. Given the singles-
consumption divergence (§12), the natural hypothesis is that the two
"new" weakly-identified directions live in or near that block — but that
must be checked, not assumed. `beta_l0_m` at its lower bound (§6) is a
separate, understood feature (excluded from the free mask) and is not a
new defect, but it confirms the model sits in a region of the parameter
space with weak curvature in at least one direction. S8 is therefore
INDETERMINATE pending enumeration, a downgrade from the prior PASS.

---

## 15. Income-routing confirmation

**Confirmed correct (GA15).** PS5 confirms singles `ils_dispy_real`
non-null for all 500,700 rows; couples `ils_dispy_male`/`ils_dispy_female`
non-null for all 743,800 rows; the couples `ils_dispy_real` column is
all-NaN, confirming the couples consumption path routes through the
gender-specific columns via `c_norm` and never reads the scalar. No
singles/couples income mixing. No defect.

---

## 16. Cluster-key confirmation

**Confirmed correct.** PS4 confirms `idorighh` present in both splits
(couples 5,838; singles 3,902 unique), combined 9,657 unique clusters
(T3, all starts), no silent `idhh` fallback, strictness safeguard active.
No defect.

---

## 17. Post-estimation fit diagnostics

**Absent — and four of them are computable now without re-estimation.**

The corrected report contains no fit/simulation diagnostics and, more
importantly, deferred four adjudications that the saved artifacts already
support:

- **S4 (region joint robust Wald)** — computable from the saved robust
  VCV (the 7×7 region sub-block); not computed.
- **S5 (GSUR-region Hessian eigenvalue sign)** — computable from the
  saved Hessian/VCV sub-block; not computed (report §30 reserved it).
- **S6 (preference-block Δ vs M1-clean)** — computable from the converged
  theta and the M1-clean vector; the singles-consumption comparison was
  omitted (§12).
- **S8 (negative-variance enumeration)** — computable from the saved
  Hessian; the 5 were not enumerated or compared to M1-clean's 3 (§14).

Two further criteria genuinely require simulation and were not run:

- **S10 (participation fit ≤ 2 pp vs M1-clean)** — requires a
  post-estimation participation simulation.
- **S11 (mean-hours fit ≤ 0.5 hrs vs M1-clean)** — requires a
  post-estimation hours simulation.

Per the required interpretation, S10 and S11 are UNEVALUATED (not passes),
and S4/S5/S6/S8 are UNEVALUATED/INDETERMINATE rather than assumed.

---

## 18. Comparison to pre-repair pooled estimation report v2

**Report v2 is pre-repair evidence only; the corrected run supersedes it
on the region block and confirms it on the identified core.**

| Characteristic | Pre-repair (v2) | Corrected (this run) |
|----------------|-----------------|----------------------|
| Joint LL | −57,280.62 | −19,084.33 (not comparable across runs) |
| Region estimates | Arbitrary (Start 2 = 0.000; 1/3 ≠ 0) | Consistent across starts, L∞ < 10⁻⁸ |
| Region robust SEs | Machine-scale O(10⁻¹⁴) | Inferential 0.34–0.55 |
| Region CONOPT marginals | Flat (zero gradient) | EPS (interior) |
| GSUR | −1.198, t ≈ −6.7 | −1.1999, t = −6.28 (stable) |
| Singles-consumption block | ~5× / sign flip vs M1-clean | unchanged (~5× / sign flip persists) |
| Flat-ridge signature | Present | Absent |

The large LL gap is expected and not informative: with all-zero region
arrays the pre-repair market-opportunity index was misspecified, so the
absolute LL values are not comparable. The region-block estimates in
report v2 remain uninterpretable artifacts and must not be cited; the
corrected run is the evidentiary basis for the region block. The
identified core (GSUR, leisure) is stable across the two runs.

---

## 19. SA2 criteria table

Criteria carried forward verbatim from the prior review (S1–S11),
adjudicated on the **corrected-region** run.

| # | Criterion | Status | Basis |
|---|-----------|--------|-------|
| S1 | LL within 1 unit; identified params within 0.01 | **PASS** | LL identical across starts; L∞ < 10⁻⁸ (§5) |
| S2 | beta_E_gsur significant p < 0.01 (robust) | **PASS** | t = −6.28 (§10) |
| S3 | beta_E_gsur within 50% of M1-clean | **PASS** | 90.3% of magnitude (§10) |
| S4 | Region-dummy joint Wald p < 0.01 (robust) | **UNEVALUATED** | Block now identified, but joint Wald not computed; computable from saved VCV (§9, §17) |
| S5 | No negative eigenvalues in GSUR-region Hessian sub-block | **UNEVALUATED** | Sub-block eigenvalues not extracted; report §30 deferred; computable from saved Hessian/VCV (§17) |
| S6 | Preference block max |Δ| < 10% vs M1-clean | **FAIL (as written) / requires investigation** | Singles-consumption block ~5× + sign flip vs M1-clean; comparison omitted by report (§12) |
| S7 | beta_ll t > 5 (robust) | **PASS** | t = 7.10 (§7 artifacts) |
| S8 | No new negative-diagonal Hessian entries beyond M1-clean's 3 | **INDETERMINATE** | Negative-variance count rose 3 → 5; not enumerated or compared (§14) |
| S9 | Gate-A GA1–GA17 all clear | **PASS** | Spec unchanged; GA17 cleared; corrected data validated (V1–V9) |
| S10 | Participation fit ≤ 2 pp vs M1-clean | **UNEVALUATED** | Requires simulation; not run (§17) |
| S11 | Mean-hours fit ≤ 0.5 hrs vs M1-clean | **UNEVALUATED** | Requires simulation; not run (§17) |

---

## 20. Which SA2 criteria pass

Five criteria pass cleanly on the corrected run: **S1** (objective and
identified-parameter stability across starts), **S2** (GSUR robustly
significant, t = −6.28), **S3** (GSUR within 50% of M1-clean, 90.3%),
**S7** (`beta_ll` t = 7.10), and **S9** (Gate-A / GA1–GA17 clear, spec
unchanged, corrected data validated). These establish that the corrected
pooled fit converges stably and recovers the load-bearing opportunity
parameter — a genuine and reportable advance over the pre-repair state,
where the region block was the open wound. They are necessary but not
sufficient for SA2.

---

## 21. Which SA2 criteria fail or remain indeterminate

Six criteria are not satisfied, in three distinct senses.

**Unevaluated but computable now (no re-estimation): S4, S5.** The region
joint Wald (S4) and the GSUR-region Hessian eigenvalue-sign check (S5) —
the two criteria the repair existed to make answerable — were deferred by
the estimation report. Both are computable from the saved robust VCVs and
Hessian. Their prior INDETERMINATE-due-to-non-identification status is
resolved at the identification level (§8); they are now simply *not yet
run*. They cannot be scored PASS until run.

**Fails as written / requires investigation: S6.** The singles-
consumption block departs from M1-clean by ~5× with a sign flip in
`theta_c_singles`. On the literal S6 threshold this is a decisive failure;
the deeper question of re-identification vs weak-identification drift is
unresolved and is itself a reason the pooled fit is not yet a defensible
baseline. The corrected report did not perform this comparison.

**Indeterminate: S8.** The negative-variance count rose from M1-clean's 3
to 5; the 5 were not enumerated or compared. Likely related to the
singles-consumption block, but unverified.

**Unevaluated, requires simulation: S10, S11.** Participation and
mean-hours fit versus M1-clean require post-estimation simulations that
were not run.

---

## 22. Whether SA2 verdict can be issued now

**No.** The required interpretation is explicit: the SA2 verdict issues
only if all SA2-readiness criteria are clearly satisfied. They are not.
Two region criteria (S4, S5) are unevaluated, S6 fails as written on the
singles-consumption block, S8 is indeterminate, and S10/S11 are
unevaluated. A verdict now would either rest on uncomputed tests (S4, S5)
or paper over a real preference-block divergence (S6) — both
unacceptable. The SA2 verdict remains a later gate, downstream of the
diagnostics in §25.

---

## 23. Whether pooled P3a can replace M1-clean now

**No. M1-clean 2016 remains the active JMP baseline.** Replacement is
gated behind an accepted SA2 verdict, which cannot be issued (§22). The
corrected estimates are candidate results at versioned paths; nothing is
promoted. The corrected run strengthens the case that pooled P3a *could*
eventually serve as the baseline — stable convergence, recovered GSUR,
restored region identification — but "could eventually" is not "now," and
the singles-consumption divergence (S6) is a substantive open question
that bears directly on whether the pooled fit is interpretable as a
welfare baseline at all.

---

## 24. What not to claim yet

- **Do not claim the region dimension matters.** It is identified, not
  shown to be significant. Individually all seven are insignificant; the
  joint Wald (S4) is uncomputed. Claiming a "region opportunity effect"
  now would be unsupported.
- **Do not claim the region block is non-identified.** It is identified
  (§8). Individual insignificance is precision, not non-identification —
  the two must not be conflated.
- **Do not claim the pooled preference estimates match M1-clean.** The
  singles-consumption block does not (§12); S6 is unmet.
- **Do not claim the model is well-conditioned.** κ ≈ 3.3 × 10⁹ and a
  risen negative-variance count (§14) say otherwise; the sandwich SEs are
  valid despite this, but the conditioning is a caveat, not a clean bill.
- **Do not claim SA2-readiness, welfare-readiness, or baseline status.**
  None holds yet (§22, §23).
- **Do not cite the pre-repair report v2 region estimates** as anything
  but superseded artifacts (§18).
- **Do not over-read the three-start agreement** as full robustness:
  Start 3 was a perturbed near-optimum, not an independent start (§2);
  Start 2 carries that weight.

What *can* be claimed: the region-dummy non-identification defect is
fixed and the block is now identified; the model converges stably to a
unique optimum; and GSUR, the core opportunity parameter, is robustly
recovered under corrected pooling.

---

## 25. Required next diagnostic or repair

**Next gate: a post-estimation diagnostics authorization (option 2) — not
the SA2 verdict, not a new specification, not a fallback to M1-clean.**

The decisive consideration is that four of the six open criteria need
**no new estimation** — they are computable from artifacts already on
disk (the converged thetas, the saved robust VCVs `.npy`, the saved
Hessians). A focused diagnostics step should compute, with no solver run:

1. **S4 — region joint robust Wald.** Compute the Wald statistic and
   p-value for `beta_E_drgn2 = … = beta_E_drgn8 = 0` from the 7×7 region
   sub-block of the saved robust VCV (cross-checked across the three
   starts' VCVs). Adjudicate S4.
2. **S5 — GSUR-region Hessian eigenvalues.** Extract and sign-check the
   eigenvalues of the GSUR-region sub-block of the true Hessian (and the
   region VCV sub-block conditioning). Adjudicate S5.
3. **S6 — preference-block Δ vs M1-clean.** Compute the explicit
   per-parameter Δ for the full preference block, foregrounding
   `beta_c_sm`, `beta_c_sf`, `theta_c_singles`, and diagnose whether the
   singles-consumption departure is genuine multi-year re-identification
   or weak-identification drift (e.g., profile the LL in
   `theta_c_singles`, inspect the block's Hessian sub-conditioning).
4. **S8 — negative-variance enumeration.** Enumerate the 5 negative-
   variance parameters, identify the 2 beyond M1-clean's 3, and locate
   them relative to the singles-consumption block.

Only after these four are adjudicated should the simulation step be
authorized for **S10/S11** (participation and mean-hours fit vs M1-clean).
A constrained/alternative pooled specification (option 3) is premature: it
becomes the right move only if S6 diagnosis shows weak-identification
drift that a constraint would cure, or if S4 shows the region block is
jointly uninformative and a region-free spec is then evidenced. Fallback
to M1-clean welfare (option 4) is also premature: the pooled fit is not
disqualified, only incompletely diagnosed. Neither (3) nor (4) is
justified before the §25.1–§25.4 diagnostics are in hand.

---

## 26. Immediate next task

**Draft a post-estimation diagnostics authorization memo** (Claude
project chat) that authorizes the four no-re-estimation computations above
(S4 Wald, S5 eigenvalues, S6 preference-block Δ with singles-consumption
diagnosis, S8 enumeration) against the saved corrected-run artifacts, with
no solver invocation, no welfare, no SA2, no canonical promotion, and
M1-clean held active. Save it as
`docs/JMP_pooled_P3a_post_estimation_diagnostics_authorization_v1.md`.

Then run that authorization in **Claude Code**, producing
`Results/JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md` (the
S4/S5/S6/S8 adjudications). Return it here for an updated SA2-readiness
verdict. If S4/S5/S6/S8 clear, authorize the S10/S11 simulation as a
separate step; only if all of S1–S11 then clearly pass is the SA2 verdict
drafted. Welfare, canonical promotion, and M1-clean displacement remain
gated throughout.

---

**Required final statements**

- **The corrected-region pooled P3a estimation is NOT SA2-ready, and no
  SA2 verdict is issued.** Five criteria pass (S1, S2, S3, S7, S9); S4 and
  S5 are unevaluated (computable from saved artifacts); S6 fails as
  written on the singles-consumption block; S8 is indeterminate; S10 and
  S11 require simulation.

- **The region-dummy block is now identified** — stable across starts,
  finite inferential SEs, interior CONOPT marginals — but it is **not
  shown to be statistically significant** (individually insignificant;
  jointly untested) and **not shown to be substantively useful**. These
  three are kept strictly distinct.

- **The flat region ridge is gone**, confirming the repair reached the
  likelihood; the pre-repair report v2 region estimates remain superseded
  artifacts.

- **Welfare computation is NOT authorized**, and **no output is promoted
  to canonical status.**

- **M1-clean 2016 remains the active JMP baseline**, displaced only by a
  future SA2 verdict that itself can issue only after the §25 diagnostics
  clear S4, S5, S6, and S8 and the S10/S11 simulation passes.
