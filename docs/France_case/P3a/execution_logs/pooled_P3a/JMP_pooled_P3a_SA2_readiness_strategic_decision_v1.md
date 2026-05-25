# JMP Pooled P3a — SA2-Readiness / Strategic Decision v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-22*

Specification class: SA2-readiness / strategic decision memo. This memo
delivers the updated SA2-readiness verdict on the corrected-region pooled
P3a model after the S4/S5/S6/S8 diagnostics, and decides the strategic
disposition of the pooled route. It does not issue the SA2 verdict, does
not authorize welfare computation, does not authorize canonical
promotion, and does not displace M1-clean 2016. The welfare-measurement
and welfare-scaffolding design memos remain active; welfare computation
remains gated behind a separate M1-clean welfare implementation
authorization.

Reference documents:
- `Results/P3a/pooled_P3a/JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md` and
  the four diagnostic JSONs (`...S4_wald.json`, `...S5_S8_hessian_diag.json`,
  `...S6_preference_comparison.json`, `...S6_theta_c_singles_LL_profile.json`)
- `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md` (the
  prior review that opened S4/S5/S6/S8)
- `Results/P3a/pooled_P3a/JMP_pooled_P3a_corrected_region_estimation_report_v1.md` (the
  corrected estimation)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the SA1-STANDS baseline and the
  region joint-Wald benchmark)
- `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` and
  `docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` (active welfare design
  memos, keyed to the operational M1-clean baseline)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to convert the completed S4/S5/S6/S8
diagnostics into a final SA2-readiness verdict on the corrected-region
pooled P3a model and a decision on what to do with the pooled route. The
prior review left four criteria open and computable; they are now
computed. Three fail and one passes, and the verdict turns on the two
that fail on harness-independent evidence. The memo states the verdict,
explains why the SA2 verdict cannot issue and why S10/S11 simulation is
not worth running on this fit, separates what the pooled model still
contributes (GSUR robustness) from what it cannot do (serve as the main
baseline), evaluates whether a constrained pooled respecification is
worth the time, and routes the main JMP path back to M1-clean welfare
implementation through a separate gate.

---

## 2. Current status of the pooled P3a route

**Estimated, identified in the region/GSUR block, but NOT SA2-ready, and
not a viable main baseline as specified.** The corrected-region run
converged cleanly on the GAMS objective (three starts, identical reported
LL, region block now numerically identified), but the saved-artifact
diagnostics show the region opportunity block is jointly insignificant
(S4), the preference block has drifted massively from the accepted
M1-clean baseline (S6), and the Hessian-based diagnostics signal numerical
trouble at the converged point (S8, plus an anomaly in §4). M1-clean 2016
remains the active JMP baseline.

---

## 3. Evidence from corrected-region estimation

The corrected estimation established the things the region repair was for,
and these still stand:

- **Convergence and reported stability.** Three starts reached the same
  GAMS objective (joint LL −19,084.3313) with converged vectors agreeing
  to L∞ < 10⁻⁸; the region block converges consistently (no flat ridge);
  CONOPT terminated cleanly (status 1, model status 2, reduced gradient
  below tolerance, zero infeasibilities) with interior region marginals.
- **GSUR recovered and robustly significant.** `beta_E_gsur` = −1.1999,
  cluster-robust SE 0.1911, t = −6.28; magnitude 90.3% of M1-clean
  (−1.329), i.e. a +9.7% change — within the S3 tolerance and just inside
  the S6 10% band. This is harness-independent (it comes from the
  estimation and the cluster-robust SE step) and is the load-bearing
  positive result of the pooled run.
- **Region block numerically identified.** Finite inferential robust SEs
  (0.34–0.55), interior CONOPT marginals — the cause-B defect is gone.

These support S1, S2, S3, S7, S9 (PASS) and the GSUR-robustness reading
(§8). They do not establish region significance or preference-block
consistency, which the diagnostics address.

---

## 4. Evidence from S4/S5/S6/S8 diagnostics

| Crit. | Result | Deciding evidence | Reliability |
|-------|--------|-------------------|-------------|
| S4 | **FAIL** | Region joint robust Wald W = 2.658, df = 7, **p = 0.9148**, well-conditioned (cond V_R = 6.31), identical across all 3 starts. Reverses M1-clean W = 28.18, p = 0.0002. | High — from saved robust VCV; harness-independent |
| S5 | **PASS (caveated)** | GSUR-region 8×8 Hessian sub-block: 0 negative eigenvalues, min eig 20.4, cond 44.5; region 7×7 even cleaner (cond 2.28). | Caveated — see harness anomaly below |
| S6 | **FAIL** | 14/27 focus params breach 10% vs M1-clean; 3 sign flips. Singles consumption: `beta_c_sm` +394%, `beta_c_sf` +365%, `theta_c_singles` −1.05→+0.04 (sign flip). | High on parameters (direct θ comparison); profile portion caveated |
| S8 | **FAIL** | 5 Hessian-based negative-variance entries — `beta_l0_sm`, `theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f` — **all leisure block, disjoint from M1-clean's 3 consumption entries**. Full Hessian has 5 negative eigenvalues (min −1.38×10⁶). | Caveated — see harness anomaly below |

**Harness anomaly that must be flagged (strict audit).** The S5/S8 Hessian
and the S6 LL-profile were produced by a Python diagnostic harness that, at
the saved "converged" theta, reports a **maximum absolute free-gradient of
≈ 7.99 × 10⁷** and a profile joint LL of **−209,155** — versus the
estimation's converged LL of **−19,084** (a ~11× scale mismatch). A genuine
optimum has a near-zero gradient. This means the harness objective is not
on the same scale as — and may not be identical to — the GAMS objective the
solver optimized. Consequences: (a) the **S4** result (saved VCV) and the
**S6 parameter comparison** (direct θ-vs-θ) are unaffected and reliable;
(b) the **S5 pass** and **S8 fail**, and the S6 LL-profile non-stationarity,
all rest on a Hessian/objective evaluated at a point the harness itself
does not see as stationary, so they carry a reliability caveat and the
verdict does not lean on them. The anomaly is itself a signal that the
pooled fit + diagnostic state is not clean and should be understood before
any further pooled estimation (§10, §17).

The verdict below rests on the two harness-independent failures (S4, S6
parameters), which are sufficient on their own.

---

## 5. Updated SA2-readiness verdict

**The corrected-region pooled P3a is NOT SA2-ready.** Of the eleven SA2
criteria: S1, S2, S3, S7, S9 PASS; **S4 FAILS** (region jointly
insignificant, p = 0.91); **S6 FAILS** (preference block diverges from
M1-clean, singles consumption ~4–5× with a sign flip); **S8 FAILS** (5
negative-variance entries in the leisure block, disjoint from M1-clean,
caveated by the harness anomaly); S5 PASSES (caveated); S10, S11 remain
UNEVALUATED and should not be run on this fit (§7). With two clean,
harness-independent failures (S4, S6) the model cannot be SA2-accepted,
independent of the caveated S5/S8.

---

## 6. Why SA2 cannot be issued

The SA2 verdict issues only if all SA2-readiness criteria are clearly
satisfied. They are not. Two failures are decisive and reliable:

- **S4.** The region opportunity block — the dimension the entire region
  repair existed to estimate — is jointly insignificant in the pooled
  couples channel (W = 2.658, p = 0.91), a near-complete reversal of the
  M1-clean cross-section (W = 28.18, p = 0.0002). Identification was
  restored, but the pooled data carry essentially no joint region signal.
  An SA2 verdict cannot certify a region opportunity result that the joint
  test rejects.
- **S6.** The preference block is not consistent with the accepted
  baseline: 14 of 27 focus parameters breach the 10% band, the singles-
  consumption block is ~4–5× M1-clean with a sign flip in
  `theta_c_singles`, and three parameters flip sign. A welfare baseline
  whose preference parameters disagree this sharply with the SA1-STANDS
  specification cannot be certified for the money-metric welfare
  computation that is the JMP's headline output.

S8 and the harness anomaly add further reason for caution but are not
needed for the verdict. Issuing SA2 now would certify a fit that fails its
own region criterion and departs sharply from the accepted preference
structure.

---

## 7. Why S10/S11 simulation should not be run on the current fit

S10 (participation fit ≤ 2 pp vs M1-clean) and S11 (mean-hours fit ≤ 0.5
hrs vs M1-clean) require a post-estimation simulation that is more
expensive than the saved-artifact diagnostics already run. Running it now
would be wasted effort, for three reasons. First, the fit is already
disqualified on S4 and S6, so even a passing S10/S11 could not produce an
SA2 acceptance. Second, the preference block — which drives the labour-
supply simulation that S10/S11 evaluate — is exactly the block that
failed S6, so the simulation would be run on parameters known to disagree
with the baseline; a good or bad fit would be uninterpretable as evidence
about the pooled specification's validity. Third, the harness anomaly (§4)
should be resolved before any further computation that depends on the
pooled likelihood harness. The diagnostics report's own recommendation —
do not spend simulation effort on the current fit before resolving
S4/S6/S8 — is correct and is adopted here. S10/S11 remain a later gate
and are not authorized.

---

## 8. What the pooled model still contributes

**One genuine, harness-independent contribution: robustness evidence that
the GSUR / opportunity result survives multi-year pooling.** The pooled
run recovers `beta_E_gsur` = −1.20 (robust t = −6.28), within 9.7% of the
M1-clean −1.33. Because this comes from the estimation and the cluster-
robust SE step — not the diagnostic harness — it is unaffected by the
harness anomaly and by the S4/S6/S8 failures. It is a legitimate, citable
robustness check: the headline opportunity loading is stable when the same
specification is estimated on three pooled survey years rather than 2016
alone.

This is robustness evidence, not a baseline. It supports a sentence of the
form "the GSUR opportunity loading is robust to multi-year pooling
(−1.20 pooled vs −1.33 in the 2016 baseline)," with the explicit
qualification that the pooled fit is otherwise not accepted (region block
jointly insignificant; preference block divergent). It does not support
any claim built on the pooled region dummies, the pooled preference
estimates, or a pooled welfare decomposition.

---

## 9. Why the pooled model should not replace M1-clean

M1-clean is SA1-STANDS: a clean, accepted fit with a jointly significant
region block (W = 28.18), a documented and contained singles-consumption
limitation (three negative-variance entries in the consumption block,
point estimates stable within 0.10), and the welfare design memos already
keyed to it. The corrected pooled P3a, by contrast, has a jointly
insignificant region block (S4), a preference block that diverges 4–5× in
singles consumption with a sign flip (S6), negative-variance entries that
have *moved into the leisure block* and multiplied (S8, caveated), and a
diagnostic-harness anomaly (§4). On every dimension that matters for a
welfare baseline — region identification, preference-block stability,
Hessian health — the pooled fit is weaker than or inconsistent with the
accepted baseline. Replacing a clean SA1-STANDS specification with a fit
that fails three of four readiness diagnostics would be a regression, not
an upgrade.

---

## 10. Whether to pursue constrained pooled respecification

**Not now.** A constrained respecification (option B) is a substantial
additional cycle — new spec, Gate-A, three-start estimation, SE step,
diagnostics, review — and its payoff is uncertain and, at best, still only
robustness. Three considerations weigh against doing it now. First, the
pooled route's one real contribution (GSUR robustness) is **already in
hand** from the current run; a constrained respecification is not needed
to obtain it. Second, the diagnostic-harness anomaly (§4 — an 8×10⁷
gradient and a ~11× LL-scale mismatch at the converged theta) should be
understood *before* investing in another pooled estimation, or the same
scale issue may recur and contaminate the new run's diagnostics. Third,
the main JMP contribution — the welfare decomposition on the accepted
M1-clean baseline — is the higher-value next step and is currently blocked
only by the absence of a welfare implementation authorization, not by any
estimation gap. A constrained pooled spec is therefore held as an optional
future robustness refinement (§11), not a current task.

---

## 11. Candidate constrained pooled specifications

If, later, a stronger multi-year robustness exposure than the current GSUR
check is wanted, three concrete constrained pooled specifications are
candidates. They are recorded here as options; none is authorized.

1. **Preference-fixed pooled (preferred candidate).** Fix the entire
   preference block — consumption (`beta_c_sm`, `beta_c_sf`,
   `theta_c_singles`, `beta_c`) and leisure (`beta_l*`, `theta_l_*`) — at
   the M1-clean converged values; estimate only the opportunity block
   (`beta_E`, GSUR, region, year), hours, occupation, and wage on the
   pooled data. Rationale: by construction this removes the divergent
   consumption block (the S6 failure) and the indefinite leisure
   directions (the S8 entries), and it tests the cleanest multi-year
   question — *is the opportunity structure stable across years, holding
   preferences at the accepted 2016 baseline?* This is the candidate most
   worth the time if multi-year opportunity-stability evidence is needed
   beyond the current GSUR robustness, because it isolates the opportunity
   block and sidesteps the two preference-side failures.

2. **Region-free pooled.** Drop the seven region dummies (S4 says they
   carry no joint signal in the pooled channel); estimate the rest.
   Rationale: removes 7 jointly insignificant parameters that may be
   adding noise. Cost: it discards the region opportunity dimension that
   M1-clean *does* identify cross-sectionally, so it is a different model,
   not a clean multi-year analogue of M1-clean; weaker as a robustness
   comparison.

3. **Singles-consumption-constrained pooled.** Fix only `beta_c_sm`,
   `beta_c_sf`, `theta_c_singles` at M1-clean values; estimate the rest.
   Rationale: targets the specific S6 divergence and the known-weak block
   while leaving the rest free. Cost: leaves the leisure-block S8 entries
   and the region S4 failure unaddressed; a partial fix.

The preferred candidate is (1); but per §10 and §12 it is not worth doing
now, and would in any case be a robustness exercise, not a main-baseline
replacement.

---

## 12. Recommended strategic decision

**Decision A: pause the pooled P3a route as a main-baseline candidate,
retain the current corrected run as robustness evidence for the
GSUR / opportunity result, and return the main JMP path to M1-clean 2016
welfare/decomposition implementation through a separate authorization
gate.**

The choice among A/B/C/D is decided as follows. **D (keep as main
candidate)** is rejected: three of four readiness diagnostics fail and SA2
cannot issue. **C (abandon entirely)** is rejected: it would discard the
genuine, harness-independent GSUR robustness evidence the run produced.
**B (constrained respecification now)** is rejected as a current task: its
payoff is uncertain and at best robustness, the GSUR robustness is already
obtained, and the diagnostic-harness anomaly should be understood before
another pooled estimation (§10). **A** is the disciplined choice: it
banks the robustness contribution, stops sinking estimation effort into a
route that cannot be the main baseline, and frees the main path for the
welfare decomposition on the accepted M1-clean specification — which the
project framing has always treated as the first credible baseline, with
multi-year work as a later extension. B's preferred candidate (§11.1) is
held as an optional future robustness refinement, not a blocker.

This recommendation matches the stated prior and survives strict scrutiny
because the two decisive diagnostics (S4, S6) are harness-independent and
the pooled route's only salvageable value (GSUR robustness) does not
require the route to continue as a baseline candidate.

---

## 13. Consequence for the JMP baseline

**M1-clean 2016 remains the JMP's preferred structural baseline,
unchanged.** Nothing in the corrected pooled run or its diagnostics
displaces it; the pooled fit is weaker on every baseline-relevant
dimension (§9). The JMP's structural baseline for all forward purposes —
welfare scaffolding, decomposition, paper text, supervisor memos — is
M1-clean, exactly as the M1-clean verdict established. The pooled run is
reclassified from "candidate baseline under SA2 review" to "multi-year
robustness artifact for the GSUR result."

---

## 14. Consequence for welfare implementation

**The welfare path is clarified, not blocked: build the welfare layer on
M1-clean.** The welfare-measurement decisions memo (v2) and the
welfare-scaffolding design memo (v2) remain **active and valid** — they
are keyed to the operational RURO baseline, which is M1-clean, and nothing
in this memo changes their content. The pooled non-readiness simply
confirms that M1-clean, not pooled P3a, is the structural substrate for
the welfare decomposition. Welfare *computation* remains gated behind a
**separate M1-clean welfare implementation authorization**, which is the
recommended next gate (§17, §19). This memo does not authorize welfare
computation, the welfare scaffold build, or canonical promotion; it routes
the main path toward that separate authorization.

---

## 15. Consequence for the multi-year route

The multi-year / pooled route is **paused as a main-baseline effort and
preserved as a robustness track**, consistent with the project framing
that country/year comparisons are later extensions, not the core
contribution. The corrected pooled run stands as the multi-year robustness
evidence for GSUR. Any future strengthening of the multi-year exposure
should (a) first resolve the diagnostic-harness anomaly (§4), then (b) use
the preference-fixed constrained spec (§11.1) as a robustness exercise —
not as a baseline-replacement attempt. Stage-B age-specific GSUR work and
other extensions remain separately gated and unaffected.

---

## 16. What not to claim

- **Do not claim a pooled / multi-year region opportunity effect.** S4
  rejects it (p = 0.91). The pooled region dummies are identified but
  jointly insignificant.
- **Do not claim the pooled model is an accepted or alternative baseline.**
  It is not SA2-ready (§5); M1-clean is the baseline (§13).
- **Do not claim the pooled preference estimates.** They diverge from
  M1-clean (S6); the singles-consumption and (per S8) leisure blocks are
  not cleanly identified at the pooled point.
- **Do not present the pooled fit's diagnostics (S5/S8, the LL profile) as
  settled** without noting the harness anomaly (§4): an 8×10⁷ gradient and
  ~11× LL-scale mismatch at the "converged" theta mean those Hessian-based
  readings are caveated.
- **Do not over-claim the GSUR robustness.** The defensible claim is
  narrow: the GSUR loading is stable to multi-year pooling (−1.20 vs −1.33),
  with the pooled fit otherwise not accepted. Do not extend it to the
  region block, preferences, or a pooled decomposition.
- **Do not treat the pooled run as evidence against M1-clean's region
  result.** The pooled couples-only channel and three-year sample differ
  from M1-clean's 2016 cross-section; S4's pooled insignificance does not
  overturn M1-clean's W = 28.18.
- **Do not claim welfare readiness on any specification yet.** Welfare
  computation is gated (§14).

---

## 17. What is authorized next

This memo authorizes only the drafting of the next-gate documents (no
estimation, no welfare computation, no solver):

- **(A1)** Drafting a **separate M1-clean welfare implementation
  authorization** (project chat) that will gate the welfare scaffold build
  and the welfare/decomposition computation on the M1-clean SA1-STANDS
  estimates, per the active welfare memos. (Authorization to *run* welfare
  is issued there, not here.)
- **(A2)** Recording the corrected pooled P3a run as a **GSUR robustness
  artifact** — a short robustness note labelling the run's status (GSUR
  −1.20 robust; region jointly insignificant; preference block divergent;
  not SA2-accepted) so it is cited correctly and not mistaken for a
  baseline.

Nothing else is authorized: no pooled re-estimation, no constrained pooled
spec, no S10/S11 simulation, no welfare computation, no SA2 verdict, no
canonical promotion.

---

## 18. What remains blocked

- **SA2 verdict** — blocked (not SA2-ready; S4, S6 fail).
- **Welfare computation** — gated behind the separate M1-clean welfare
  implementation authorization (§14, §17).
- **Canonical promotion** — not authorized; no output promoted.
- **M1-clean displacement** — blocked; M1-clean remains active.
- **Pooled re-estimation / constrained pooled spec** — not authorized
  (held as optional future robustness, §11).
- **S10/S11 simulation** — not authorized on the current fit (§7).
- **The diagnostic-harness anomaly (§4)** — must be understood before any
  further pooled estimation; flagged, not yet investigated (no
  authorization issued here to investigate it, but it is a precondition
  for any future pooled work).

---

## 19. Immediate next task

**Draft the M1-clean welfare implementation authorization** (Claude
project chat) — the separate gate that authorizes building and running the
welfare scaffolding and the opportunity/ability/preference decomposition
on the M1-clean SA1-STANDS estimates, per
`docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` and
`docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md`. Save it as
`docs/JMP_M1_clean_welfare_implementation_authorization_v1.md`. This is the
main JMP path forward.

In parallel (project chat), write the short **GSUR robustness note**
recording the corrected pooled run's status and the one defensible claim
(GSUR stable to multi-year pooling), saved as
`Results/JMP_pooled_P3a_GSUR_robustness_note_v1.md`, so the pooled run is
cited correctly.

Welfare computation, the SA2 verdict, canonical promotion, M1-clean
displacement, and any further pooled estimation remain gated and are not
authorized by this memo.

---

**Required final statements**

- **The corrected-region pooled P3a is NOT SA2-ready, and no SA2 verdict
  is issued.** S1, S2, S3, S7, S9 pass; S4 fails (region jointly
  insignificant, W = 2.658, p = 0.91); S6 fails (preference block diverges
  from M1-clean, singles consumption ~4–5× with a sign flip); S8 fails (5
  leisure-block negative-variance entries, caveated by a diagnostic-harness
  anomaly); S5 passes (caveated). The verdict rests on the harness-
  independent failures S4 and S6.

- **S10/S11 simulation is not useful on the current fit** and is not run:
  the fit is already disqualified on S4 and S6, and the preference block
  that drives the simulation is the block that failed S6.

- **The pooled model is retained as robustness evidence for the GSUR /
  opportunity result** (GSUR −1.20, within 9.7% of M1-clean), explicitly
  distinguished from acceptance as the main structural baseline, which it
  is not.

- **The recommended decision is A:** pause the pooled route as a main-
  baseline candidate, retain it as GSUR robustness, and return the main
  JMP path to M1-clean welfare/decomposition implementation through a
  separate authorization gate.

- **Welfare computation is NOT authorized**, **canonical promotion is NOT
  authorized**, and **M1-clean 2016 remains the active JMP baseline.** The
  welfare-measurement and welfare-scaffolding memos remain active, with
  welfare computation gated behind the separate M1-clean welfare
  implementation authorization.
