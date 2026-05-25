> Archived on 2026-05-26 — superseded by the corrected-region post-estimation review after the region-dummy repair and re-estimation.
> Replacement (kept active): `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Pooled P3a Estimation — Post-Estimation Review / SA2-Readiness Verdict v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Specification class: strict post-estimation review / SA2-readiness
verdict. This is the gate the execution authorization correction (C1)
places immediately after estimation and before any SA2 verdict. It
adjudicates whether the pooled P3a estimation report and the mandatory
diagnostics pass. It does NOT issue an SA2 verdict, does NOT authorize
welfare, does NOT authorize canonical promotion, does NOT authorize any
new estimation, and does NOT displace M1-clean.

Reviewed artifacts:
- `Results/JMP_pooled_P3a_estimation_report_v2.md`
- `Results/JMP_pooled_P3a_orchestrator_summary.json`
- `Results/JMP_pooled_P3a_start1_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_start2_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_start3_cluster_robust_se.json`
- `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` + correction
- `docs/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md`
- `docs/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`
- `Results/JMP_pooled_P3a_estimation_preflight_report_v2.md`

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Verdict

**PASS-WITH-BLOCKERS for execution and infrastructure; NOT
SA2-READY.** The pooled P3a estimation ran cleanly, within
authorization, with strong objective stability and a recovered headline
opportunity result (GSUR). But two identification problems block the
SA2 verdict, and three SA2 criteria cannot be evaluated without
separately authorized work.

What passes, strictly verified against the raw SE JSONs:
- The estimation followed the authorization and the repair clearance
  (§2); the three-start protocol is satisfied with one documented,
  non-blocking deviation (§3).
- Objective stability is excellent: all three starts reach an identical
  joint log-likelihood (−57,280.621315) to nine decimals, and all
  identified parameters agree across starts to ~12 significant figures
  (§4, §5). Per the review standard, identical LL across three distinct
  starts is a success for objective stability.
- The GSUR loading — the central opportunity result — is recovered:
  −1.198, t = −6.70 (cluster-robust), 90.1% of the M1-clean magnitude
  (§7). S2 and S3 pass.

What blocks SA2:
- **(B1) The seven region dummies are exactly non-identified.** Start 2
  converged with all seven at 0.000 while Starts 1 and 3 converged at
  different non-zero vectors, all at the identical LL. This is a flat
  likelihood ridge, not sampling uncertainty. Their cluster-robust SEs
  (~10⁻¹⁴–10⁻¹⁵) are numerical noise, not inference. **S4 and S5 are
  INDETERMINATE.** (§8, §9, §10)
- **(B2) The singles-consumption sub-block has shifted sharply from
  M1-clean inside a known weakly-identified block.** `beta_c_sm`
  0.55→2.75, `beta_c_sf` 0.51→2.36, `theta_c_singles` −1.05→+0.05 — and
  these are exactly the three parameters with near-singular Hessian
  behavior in both M1-clean and the pooled fit. S6 (preference block
  max |Δ| < 10%) cannot be presumed to pass and is likely to fail when
  computed; it is currently unevaluated. (§13, §15)
- **(B3) Fit diagnostics S6, S10, S11 are unevaluated** — they require a
  preference-comparison computation and a participation/hours simulation
  that are not authorized here. (§15)

Consequently: the SA2 verdict cannot be issued (§19); pooled P3a cannot
replace M1-clean (§20); M1-clean 2016 remains the active baseline. The
appropriate next gate is a scoped region-dummy non-identification
diagnostic, which is the precondition to a likely pooled
no-region-dummy design memo (§22, §23).

---

## 2. Whether estimation followed authorization

**Yes, with one authorized data-input substitution and one documented
protocol deviation, neither material.**

The estimation ran `ruro_occ_P3a_pooled` (55 parameters; `theta_c`
fixed at 0.0 for couples, hence 54 estimated/free positions reported)
under the primary authorization and its correction, against the
split-stem base `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`
— the substitution the repair clearance made binding (clearance §2),
replacing the unified parquet referenced in authorization §6. The two
representations derive from the same source; the split was verified
(V1–V2 conservation: 1,244,500 rows; 12,445 household-years; 9,657
clusters). This is an authorized deviation, not a violation.

The hard constraints held throughout: no welfare (D14), no canonical
promotion (D15), no M1-clean displacement (D15), and no halt H1–H6
fired. The cluster key was `idorighh` (D13), and income routing
followed GA15 (D12). All three starts returned `returncode = 0`
(orchestrator summary). I find no authorization breach.

---

## 3. Whether the three-start protocol was satisfied

**Yes.** Three starts ran and converged:
- Start 1 — warm from M1-clean (53→55 by name; year dummies at 0.0).
- Start 2 — spec defaults (cold, YAML initial values).
- Start 3 — perturbed start (seed 42, ±0.1).

One documented deviation (report PD1): Start 3 perturbed the **converged**
Start 1 theta rather than the **initial** warm-start vector. I accept the
report's assessment that this is non-blocking and, if anything, a more
stringent test of optimum stability — but I note it strictly as a
deviation from the literal §8/§9 wording, not a silent change. Because
all three starts reach the same LL and the same identified parameters,
the deviation does not affect any conclusion here.

---

## 4. Convergence and objective-value evidence

**Convergence: clean. Objective stability: PASS (S1).**

All nine group-solver records report `success = True`,
NormalCompletion / OptimalLocal, in 14–19 iterations and ~280–300 s
wall per start. No H3 (non-convergence) fired.

Joint log-likelihood by start: −57,280.621315 / −57,280.621315 /
−57,280.621315 — identical to nine decimals (max |Δ| < 10⁻⁹). Reaching
the same LL from a warm M1-clean start, a cold YAML start, and a
perturbed-converged start is strong evidence of a dominant optimum on
the identified subspace. Per the review standard, identical LL across
three starts is treated as a success for objective stability. **S1
PASS.**

I do not compare this LL level to M1-clean's −6,487.55: the two are not
comparable (single-year vs three-year pooled, different N, non-nested).

---

## 5. Parameter-vector stability

**Stable on the identified subspace; unstable only where
non-identified.**

I verified against the three SE JSONs directly. For the identified
parameters, the three converged vectors agree to ~12 significant figures
(e.g., `beta_E_gsur`: −1.1980536481250086 / −1.198053648126334 /
−1.19805364812634; `theta_c_singles`: 0.04845094693283109 /
0.0484509469327161 / 0.04845094693272475). The entire cross-start
disagreement is confined to the seven region dummies (§8).

One important strict consequence: because the identified block is
reproducible across all three starts to 12 figures, the large
M1-clean→pooled shift in the singles-consumption parameters (§13) is a
**stable, real feature of the pooled optimum**, not start-dependent
noise. That makes it more, not less, of a concern.

---

## 6. Year-effect estimates

Both year effects are positive and individually insignificant under
cluster-robust SEs:

| Parameter | Estimate | SE robust | t | 
|-----------|----------|-----------|---|
| beta_E_y2015 | 0.1097 | 0.2532 | 0.43 |
| beta_E_y2017 | 0.3255 | 0.2773 | 1.17 |

The year effects ARE identified (real SEs, consistent estimates across
starts), in contrast to the region dummies. Neither reaches conventional
significance; the SA2-REVISION threshold (individually significant and
large year effects) is not met. This is acceptable: small, insignificant
year effects relative to the FR_2016 reference are a benign result, not
a blocker. It does, however, mean the pooling buys little in the
market-opportunity time dimension at current precision — relevant
context for whether pooling is worth its identification cost (§20).

---

## 7. GSUR coefficient result

**The headline opportunity result is recovered. S2 and S3 PASS.**

| | beta_E_gsur | SE robust | t | % of M1-clean |
|-|-------------|-----------|---|---------------|
| Pooled P3a | −1.1981 | 0.1788 | −6.70 | 90.1% |
| M1-clean FR_2016 | −1.329 | 0.163 | −8.15 | — |

The GSUR loading is negative, highly significant under cluster-robust
inference (|t| = 6.70 > 2.576, S2 PASS), and within 10% of the M1-clean
magnitude (S3 PASS, threshold ±50%). This is the single most important
positive finding: the pooled specification reproduces the GSUR
market-opportunity identification that anchors the JMP's
opportunity-vs-preference decomposition. It is the strongest argument
against abandoning pooled P3a (§20, §22).

---

## 8. Region-dummy identification problem

**The seven region dummies (`beta_E_drgn2`–`beta_E_drgn8`) are exactly
non-identified. This is the primary SA2 blocker.**

Evidence, verified in the raw SE JSONs:

| Param | Start 1 | Start 2 | Start 3 | SE robust |
|-------|---------|---------|---------|-----------|
| beta_E_drgn2 | 0.801 | 0.000 | 0.710 | ~8.6e-15 |
| beta_E_drgn3 | 0.656 | 0.000 | 0.587 | ~7.1e-15 |
| beta_E_drgn4 | 1.563 | 0.000 | 1.599 | ~1.4e-14 |
| beta_E_drgn5 | 0.772 | 0.000 | 0.821 | ~1.1e-15 |
| beta_E_drgn6 | 0.767 | 0.000 | 0.860 | ~1.7e-14 |
| beta_E_drgn7 | 0.640 | 0.000 | 0.606 | ~7.3e-15 |
| beta_E_drgn8 | 0.463 | 0.000 | 0.437 | ~5.6e-15 |

Three converged points — one at exactly zero, two at materially
different non-zero vectors — all yielding the identical joint LL to nine
decimals is mathematically conclusive: the likelihood is **flat** along
the region-dummy subspace at the optimum. Per the review standard, this
is treated as non-identification, NOT as normal sampling uncertainty.
The values reported in any single start's parameter table are arbitrary
points on a flat ridge and carry no economic meaning.

A strict caution the report does not draw out. M1-clean identified these
same region dummies off cross-sectional region variation in FR_2016.
Pooling **adds** years and a year-effect block; it does not remove the
cross-sectional region variation that identified the dummies in
M1-clean. It is therefore implausible on its face that pooling alone
would drive these parameters from identified to **exactly** flat. The
report's structural explanation ("time-invariant region effects are not
identified when household-year effects enter through other channels") is
asserted, not demonstrated, and competes with a more mundane and — given
this pipeline's history — more likely hypothesis: a degeneracy or
wiring problem in the region columns of the rebuilt split-stem data. The
`year_2015_indicator` / `year_2017_indicator` shifters in this very
build were initially **silently skipped** by a `_collect_extra_vars`
bug; an analogous silent issue affecting `reg_nuts1_2`–`reg_nuts1_8`
(degenerate, constant, all-zero, or not wired into the `beta_E`
market-opportunity term) would produce exactly this flat-ridge
signature. This must be ruled out before any spec change is canonized
(§22).

---

## 9. Cluster-robust SE validity

**Valid and inferential for the identified parameters; non-inferential
for the region dummies.**

The post-estimation cluster-robust SE machinery ran correctly on all
three starts: T3 confirms exactly 9,657 `idorighh` clusters on the full
12,445×55 score matrix; the true Hessian (central differences on
`compute_gradient_joint` at the converged theta) was used, not the dummy
Hessian; T4 reports n_nonpositive = 0 over n_free = 54; T5 reports
n_below = 0. The robust-to-Hessian ratios of ~2–8× on identified
parameters are consistent with positive within-`idorighh` correlation
across years, as expected for a three-year panel.

The strict qualification: the seven region-dummy SEs (~10⁻¹⁴–10⁻¹⁵) are
**non-inferential numerical noise**, approximately machine precision,
arising from a near-zero Hessian sub-block in the unidentified subspace.
They pass T4's `se ≤ 0` check only on a technicality (they are positive
floating-point noise). Per the review standard, these machine-scale SEs
are treated as carrying no inferential content and must not be reported
as standard errors. T4 PASS is therefore "technically correct but
materially hollow" for those seven positions; for the 47 identified free
parameters, the SEs are genuine.

---

## 10. Hessian and numerical identification

**The identified subspace is well-behaved; the full Hessian is
ill-conditioned solely because of the region-dummy ridge and a
near-singular singles-consumption block.**

The full 54-free Hessian condition numbers are 5.2×10²⁴ / 1.1×10²⁵ /
2.8×10²⁵ — extreme, driven by the flat region-dummy subspace. Restricted
to the 47 identified parameters, the VCV condition number is 2.0×10¹⁰,
comparable to M1-clean (5.1×10¹⁰). So the ill-conditioning is localized,
not pervasive.

Two near-singular pockets remain, and I treat them differently:
- The seven region dummies — exact non-identification (§8). Blocking.
- The three singles-consumption parameters (`beta_c_sm`, `beta_c_sf`,
  `theta_c_singles`) — near-singular Hessian behavior, present in
  M1-clean too. The report frames this as "same as M1-clean, handled by
  pinv." That is true numerically but incomplete: these three are also
  the parameters that **shifted most** from M1-clean (§13). Weak
  identification plus a large shift is a combination the report should
  not wave through, because it means S6 cannot be presumed and the
  pooled singles-consumption estimates may be unreliable in level even
  though they are stable across starts.

S5 (no negative eigenvalues in the GSUR-region Hessian sub-block) is
INDETERMINATE: the sub-block contains the unidentified region dummies
with eigenvalues of both signs at machine scale, so the criterion cannot
be adjudicated until the region issue is resolved. S8 (no new
negative-diagonal entries beyond M1-clean's three) PASS — the same three
singles-consumption entries, no new ones.

---

## 11. Income-routing confirmation

**Confirmed correct (GA15).** Singles read `ils_dispy_real` (non-null
for all 500,700 singles rows); couples read `ils_dispy_male` /
`ils_dispy_female` and the couples consumption path uses `c_norm`, never
`ils_dispy_real` (non-null for all 743,800 couples rows). No
singles/couples income mixing. H2 did not fire (D12). I find no income-
routing defect.

---

## 12. Cluster-key confirmation

**Confirmed correct.** The SE CLI ran with `--cluster-col idorighh`; T3
confirmed 9,657 unique `idorighh` clusters on the full dataset on all
three starts; the strictness safeguard was active and no silent `idhh`
fallback occurred. H1 did not fire (D13). I find no cluster-key defect.

---

## 13. Preference-parameter comparison to M1-clean

**Mixed, and this is a strict concern the report under-reported.**

The leisure side is stable: the leisure Box-Cox exponents and age/kids
leisure terms are close to M1-clean (e.g., `theta_l_sm` −0.7193 vs
−0.7125; `theta_l_f` −0.6590 vs the M1-clean leisure block), consistent
with a well-identified preference geometry over leisure.

The **singles-consumption sub-block has moved sharply**, and it moved in
the same three parameters flagged as near-singular:

| Param | M1-clean | Pooled | Change |
|-------|----------|--------|--------|
| beta_c_sm | 0.5537 | 2.7460 | ≈ 5× |
| beta_c_sf | 0.5056 | 2.3597 | ≈ 4.7× |
| theta_c_singles | −1.0485 | +0.0485 | sign flip |

These are stable across the three starts (so not numerical noise within
the pooled fit), but they are an order-of-magnitude departure from the
single-year baseline in a block known to be weakly identified. A naive
S6 ("preference block max |Δ| < 10% vs M1-clean") would **fail
decisively**, driven by this block. The report set S6 to "not
evaluated"; strictly, S6 should be flagged as **at high risk of failure
pending the authorized comparison computation**, not left as a neutral
"not evaluated." Whether this reflects (a) genuine multi-year
re-identification of singles consumption curvature or (b) weak
identification letting the block drift cannot be settled without the
comparison computation and is itself a reason the pooled fit is not yet
defensible as a baseline.

The couples consumption weight `beta_c` (4.331 vs 4.000, +8.3%) is
within 10% and benign.

---

## 14. Opportunity-parameter comparison to M1-clean

**The core opportunity loading is recovered; the region opportunity
dimension collapsed; the time dimension is weak.**

- `beta_E` (market-opportunity intercept): −2.281 vs −2.499, ≈9%
  smaller. Within tolerance; stable.
- `beta_E_gsur` (GSUR loading): −1.198 vs −1.329, 90.1% of magnitude,
  t = −6.70. Recovered and significant (§7). This is the load-bearing
  opportunity parameter for the JMP, and it survives pooling.
- Region dummies (`beta_E_drgn*`): non-identified (§8). The region
  opportunity dimension that M1-clean carried is **lost** in the pooled
  fit as currently specified.
- Year effects (`beta_E_y2015/2017`): new to the pooled spec; small and
  insignificant (§6).
- Hours and occupation opportunity shifters (`beta_h_*`, `beta_occ_*`):
  broadly comparable, with sensible signs and mostly significant robust
  t-ratios.

Net: the opportunity side is healthy except for the region block, which
is exactly the block that is non-identified. The JMP's opportunity
construct does not collapse — GSUR carries it — but a region-based
opportunity dimension is currently unavailable in the pooled spec.

---

## 15. Post-estimation fit diagnostics still missing

Three criteria cannot be evaluated from the estimation artifacts alone
and were not authorized in this run:
- **S6 — preference-block comparison vs M1-clean.** Requires the
  explicit per-parameter Δ computation. Per §13, this is at high risk of
  failing on the singles-consumption block; it must be computed before
  any SA2 verdict, not assumed.
- **S10 — participation fit (≤ 2 pp regression vs M1-clean).** Requires a
  post-estimation participation simulation. Not authorized; not run.
- **S11 — mean-hours fit (≤ 0.5 hrs regression vs M1-clean).** Requires a
  post-estimation hours simulation. Not authorized; not run.

Per the review standard, S6, S10, and S11 remain **unevaluated** unless
the preference-comparison and simulation steps are separately
authorized. They are not failures, but they are not passes; the SA2
verdict cannot treat them as satisfied.

---

## 16. SA2 criteria table

| # | Criterion | Status | Basis |
|---|-----------|--------|-------|
| S1 | LL within 1 unit; identified params within 0.01 | **PASS** | LL identical to 9 dp; identified params agree to ~10⁻¹² (§4, §5) |
| S2 | beta_E_gsur significant p < 0.01 (robust) | **PASS** | t = −6.70 (§7) |
| S3 | beta_E_gsur within 50% of M1-clean | **PASS** | 90.1% of magnitude (§7) |
| S4 | Region-dummy joint Wald p < 0.01 (robust) | **INDETERMINATE** | Region dummies non-identified; Wald inverse degenerate (§8) |
| S5 | No negative eigenvalues in GSUR-region Hessian sub-block | **INDETERMINATE** | Sub-block contains non-identified region dummies; both-sign machine-scale eigenvalues (§10) |
| S6 | Preference block max |Δ| < 10% vs M1-clean | **UNEVALUATED (high risk of FAIL)** | Singles-consumption block shifted ≈5× / sign flip (§13); comparison not computed |
| S7 | beta_ll t > 5 (robust) | **PASS** | t = 7.09 |
| S8 | No new negative-diagonal Hessian entries beyond M1-clean's 3 | **PASS** | Same 3 singles-consumption entries; no new ones (§10) |
| S9 | Gate-A GA1–GA17 all clear | **PASS** | Gate-A PASS + GA17 cleared |
| S10 | Participation fit ≤ 2 pp vs M1-clean | **UNEVALUATED** | Requires simulation; not authorized (§15) |
| S11 | Mean-hours fit ≤ 0.5 hrs vs M1-clean | **UNEVALUATED** | Requires simulation; not authorized (§15) |

---

## 17. Which SA2 criteria pass

**S1, S2, S3, S7, S8, S9 pass.** Objective and identified-parameter
stability (S1), the GSUR significance and magnitude (S2, S3), the
labour-supply scale parameter `beta_ll` (S7, t = 7.09), the Hessian
negative-diagonal pattern unchanged from M1-clean (S8), and the upstream
Gate-A / GA17 clearances (S9). These establish that the estimation
machinery and the central opportunity identification are sound.

---

## 18. Which SA2 criteria fail or are indeterminate

- **S4 — INDETERMINATE.** The region-dummy joint Wald test is not
  computable: the region-dummy VCV sub-block is degenerate (flat ridge),
  so its inverse does not exist. S4 is INDETERMINATE **because the region
  dummies are not identified**, not because the test was run and
  inconclusive.
- **S5 — INDETERMINATE.** The GSUR-region Hessian sub-block contains the
  non-identified region dummies, with both-sign eigenvalues at machine
  scale. The eigenvalue-sign criterion cannot be adjudicated until region
  identification is resolved.
- **S6 — UNEVALUATED, high risk of FAIL.** Not computed; on the visible
  evidence the singles-consumption block would drive a naive S6 to fail.
  It must be computed, not assumed, before SA2.
- **S10, S11 — UNEVALUATED.** Require post-estimation simulation that is
  not authorized.

No criterion is recorded as a clean PASS that should instead be a fail;
but S4 and S5 cannot be passed, and S6/S10/S11 cannot be claimed.

---

## 19. Whether SA2 verdict can be issued now

**No. The SA2 verdict cannot be issued.** Three of the eleven SA2
criteria are blocked (S4, S5 INDETERMINATE) or unevaluated with high
fail risk (S6), and two more (S10, S11) are unevaluated. The correction
(C1) sequencing requires that the SA2 verdict be drafted only if the
estimation report and all mandatory diagnostics pass under this strict
review. They do not all pass: the region-dummy non-identification alone
is sufficient to withhold the SA2 verdict, and the singles-consumption
shift and the missing fit diagnostics independently reinforce that
conclusion. No SA2 verdict is issued here.

---

## 20. Whether pooled P3a can replace M1-clean now

**No. Pooled P3a cannot replace M1-clean 2016 as the active baseline.**

M1-clean identified the region opportunity dimension; the pooled spec as
estimated does not (§8). Replacing a baseline that identifies region
opportunity with one that silently loses it — possibly through a data
build defect (§8) — would degrade the JMP's opportunity construct, not
improve it. The pooled fit's genuine gains (a recovered GSUR loading
across three years, stable preferences on the leisure side) do not
outweigh an unresolved exact non-identification and an unexplained
singles-consumption shift. Additionally, the year effects are small and
insignificant (§6), so at current precision pooling buys little in the
time dimension while costing region identification. M1-clean 2016
remains the active JMP baseline, displaced only by a future SA2 verdict
explicitly promoting an identified pooled specification.

---

## 21. What not to claim yet

Until the blockers are resolved and the missing diagnostics are
authorized and computed, do NOT claim:
- that the pooled P3a specification is accepted, validated, or the
  baseline (it is not; SA2 is not issued);
- any economic interpretation of the seven region-dummy values — they
  are arbitrary points on a flat ridge (§8);
- that the region opportunity dimension is estimated in the pooled model
  (it is not identified);
- that the year effects show a meaningful time trend in opportunity
  (they are small and insignificant, §6);
- that the pooled preference estimates are comparable to M1-clean — the
  singles-consumption block has shifted ≈5× / sign-flipped and S6 is
  uncomputed (§13);
- any participation or hours fit (S10, S11 unevaluated);
- any welfare or inequality-decomposition result — welfare is not
  authorized and not computed (D14);
- that pooled P3a improves on or replaces M1-clean (§20).

The only defensible claims at this stage: the estimation converged with
strong objective stability, and the GSUR opportunity loading is
recovered and significant across three pooled years.

---

## 22. Required next repair or diagnostic

**Decision: the appropriate next gate is a scoped region-dummy
non-identification diagnostic (option 3), framed as the precondition to
a likely pooled no-region-dummy design memo (option 1).** The other two
options are rejected.

Reasoning, strictly. The modeling endpoint your instinct points to — a
pooled no-region-dummy specification — is probably correct: three
converged points with maximally different region-dummy values at
identical LL prove the region block contributes nothing to the
identified likelihood, so dropping it is observationally equivalent
(same LL, same identified parameters, same GSUR) and yields a clean
48-free-parameter model. **But the design memo must not be issued
blind.** The reason is concrete, not precautionary boilerplate: it is
implausible that pooling more years onto M1-clean — which identified
these dummies cross-sectionally — would by itself drive them to *exactly*
flat, and this pipeline has an established precedent of a silent
extra-vars wiring bug (the year indicators were initially skipped by
`_collect_extra_vars`). An analogous degeneracy or mis-wiring of
`reg_nuts1_2`–`reg_nuts1_8` in the rebuilt split-stem data would produce
this exact flat-ridge signature. If that is the cause, the correct
response is a data-build fix, not a spec change; canonizing a region-free
spec would then mask a bug and silently discard a legitimate opportunity
dimension.

The diagnostic must therefore establish, with no new estimation:
1. **Column integrity.** Are `reg_nuts1_2`–`reg_nuts1_8` present,
   non-constant, non-all-zero, and correctly populated in BOTH split-stem
   files? (Cross-tab region against `year_tag` and `household_type`.)
2. **Wiring.** Are the region dummies actually entering the `beta_E`
   market-opportunity term in the pooled build — i.e., are they in the
   `extra_vars` / market-opportunity shifter list that reaches the
   gradient, the way the year indicators eventually were?
3. **Collinearity.** Are the region columns collinear with `gsur`, the
   year dummies, the occupation dummies, or an absorbed intercept in the
   pooled design matrix? (Rank / condition check on the
   region-plus-related design block.)
4. **Flatness confirmation.** Confirm the LL is exactly invariant to the
   region-dummy values at the optimum (already strongly evidenced by the
   three starts; confirm directly).

The diagnostic then branches:
- If columns are intact and wired but structurally collinear/redundant in
  the pooled panel → proceed to the **pooled no-region-dummy design
  memo** (option 1), which is then well-founded.
- If columns are degenerate or mis-wired → the gate becomes a **pooled
  data-build fix** (rebuild the split-stem region columns), after which
  the region dummies may re-identify and no spec change is needed.

Rejected options:
- **Option 2 (constrained-region design memo):** rejected. There is no
  theoretical basis for pinning the region dummies to specific non-zero
  values; a constraint would be arbitrary. If regions are genuinely
  redundant, drop them (option 1); do not constrain them.
- **Option 4 (abandon pooled P3a for M1-clean):** rejected as premature.
  The pooled fit recovered the central GSUR result at 90% magnitude with
  t = −6.70 and stable preferences on the leisure side. Abandoning a
  working multi-year estimate over seven unidentified secondary
  parameters would discard real progress. Abandonment is only on the
  table if the diagnostic reveals a deep, unfixable structural problem,
  which the current evidence does not suggest.

---

## 23. Immediate next task

**Run the scoped region-dummy non-identification diagnostic. No new
estimation, no welfare, no SA2, no canonical promotion.**

Tool path: Claude Code (local codebase; inspects existing artifacts,
the split-stem data columns, and the design matrix — no solver run).
Interpreter: `.venv\Scripts\python.exe`.

Files to place/confirm in the workspace: the two split-stem parquets
(`fr_p3a_gsurv2_estimation_ready__singles.parquet`,
`...__couples.parquet`) and `__mnlmeta.json`; the pooled YAML; the three
SE JSONs; `scripts/maintenance/prepare_pooled_estimation_ready.py` (the
build script); `estimation_utils.py` and the market-opportunity /
`extra_vars` wiring in the engine; this review.

Prompt to use (Claude Code):

> Run a read-only region-dummy non-identification diagnostic for the
> pooled P3a fit per
> `docs/JMP_pooled_P3a_post_estimation_review_v1.md` §22. Use
> `.venv\Scripts\python.exe`. Do NOT run the solver. Do NOT re-estimate.
> Do NOT compute welfare. Do NOT issue SA2. Do NOT promote anything.
>
> Establish, with no estimation: (1) column integrity of
> `reg_nuts1_2`–`reg_nuts1_8` in both split-stem files — present,
> non-constant, non-all-zero, correctly populated; cross-tab region by
> `year_tag` and `household_type`; (2) wiring — confirm whether the
> region dummies actually reach the `beta_E` market-opportunity term in
> the pooled build (the `extra_vars` / market-opportunity shifter list
> that enters the gradient), the way `year_2015_indicator` /
> `year_2017_indicator` eventually did; (3) collinearity — rank and
> condition of the region-plus-related design block (region vs `gsur`,
> year dummies, occupation dummies, absorbed intercept); (4) confirm the
> LL is exactly invariant to the region-dummy values at the optimum.
>
> Save the diagnostic as
> `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md`,
> recording each of (1)–(4) with the evidence, and a decisive cause
> classification: (A) intact-and-wired-but-collinear/redundant →
> recommend a pooled no-region-dummy design memo; or (B)
> degenerate/mis-wired columns → recommend a pooled data-build fix.
> Confirm at the end: no estimation run, no welfare, no SA2, no
> promotion, M1-clean 2016 still active.

Output to save:
`Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md`.

What to do next: return the diagnostic to the project chat. If cause (A),
the next gate is a **pooled no-region-dummy specification design memo**;
if cause (B), the next gate is a **pooled data-build fix**. Either way,
re-estimation of the revised specification is a separate, later gate and
is NOT authorized now. Welfare, SA2, canonical promotion, and M1-clean
displacement remain gated.

---

**Required final statements**

- **No SA2 verdict is issued.** This is the strict post-estimation
  review / SA2-readiness verdict; the SA2 verdict remains a later gate.

- **The pooled P3a estimation is PASS-WITH-BLOCKERS, not SA2-ready.**
  S1, S2, S3, S7, S8, S9 pass; S4 and S5 are INDETERMINATE (region
  dummies not identified); S6 is unevaluated with high fail risk; S10
  and S11 are unevaluated.

- **Pooled P3a may not replace M1-clean.** M1-clean 2016 remains the
  active JMP baseline, displaced only by a future SA2 verdict explicitly
  promoting an identified pooled specification.

- **Welfare computation is NOT authorized**, and no new estimation is
  authorized. The next gate is a read-only region-dummy diagnostic.

- **No output is promoted to canonical status.** The pooled estimates
  remain candidate results at versioned paths.
