# JMP Pooled P3a Estimation Execution Authorization — Correction v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This document records two wording/scope corrections applied to
`docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` before
execution. The authorization is accepted in substance: the three-start
pooled estimation of `ruro_occ_P3a_pooled` remains authorized, with the
specification, data input, cluster-robust inference requirement, starts,
solver, halt conditions, and not-authorized scope all unchanged. The two
corrections concern (C1) the sequencing of the gate after estimation and
(C2) the explicit enumeration of the cluster-robust SE artifacts the
estimation report must include.

No data, parquet, specification, validation result, or authorization
scope is changed. The corrections are wording-and-scope clarifications to
the post-estimation sequencing and the report-contents requirement.

| # | Issue | Action |
|---|-------|--------|
| C1 | Several passages stated the immediate next chat task after estimation is "the SA2 verdict", conflating the SA2-readiness review with the SA2 adjudication | Replaced with: the immediate next gate after estimation is a strict post-estimation review / SA2-readiness verdict; the SA2 verdict is drafted only if the estimation report and all mandatory diagnostics pass |
| C2 | §19 required "the Hessian-based and cluster-robust SEs, all post-estimation diagnostics" but did not explicitly enumerate the cluster-robust SE artifacts the report must include or produce | §19 revised to require the full cluster-robust SE artifact list as report contents, not only point estimates |

---

## 2. C1 — post-estimation gate sequencing correction

**Problem.** The authorization stated, in three places, that the
immediate next chat task after the estimation is the SA2 verdict. This
wording conflated two distinct gates: the strict post-estimation review
(the SA2-readiness verdict, which adjudicates whether the estimation
report and the mandatory diagnostics pass) and the SA2 verdict itself
(the adjudication of the SA2 criteria S1–S11 that determines acceptance
and the M1-clean-versus-pooled baseline question). The SA2 verdict must
not be the immediate next step; it is drafted only after a strict post-
estimation review confirms the estimation report and all mandatory
diagnostics pass.

**Affected passages and corrected wording.**

| Location | Before | After |
|----------|--------|-------|
| §1 (Purpose, closing of the "what the estimation produces" paragraph) | "…and then a separate SA2 verdict to determine whether the pooled specification is accepted and whether it displaces M1-clean." | "…and then, only if the estimation report and all mandatory diagnostics pass under a strict post-estimation review (SA2-readiness verdict), a separate SA2 verdict to determine whether the pooled specification is accepted and whether it displaces M1-clean." |
| §19 ("What to do next" paragraph) | "return the estimation report to the project chat for the SA2 verdict. The SA2 verdict is a separate adjudication against the SA2 criteria (§15)…" | "return the estimation report to the project chat for a strict post-estimation review / SA2-readiness verdict. Only if the estimation report and all mandatory diagnostics (§13, §14) pass should the SA2 verdict be drafted. The SA2 verdict is a separate adjudication against the SA2 criteria (§15) and is NOT the immediate next step…" |
| §15 (opening, reaffirmed) | "No SA2 verdict is issued by this memo or by the estimation. The SA2 verdict is a separate adjudication, issued after the estimation and the complete post-estimation diagnostics…" | Reaffirmed and sharpened: "No SA2 verdict is issued by this memo or by the estimation. After the estimation, the immediate next gate is a strict post-estimation review / SA2-readiness verdict. The SA2 verdict is drafted only if that review confirms the estimation report and all mandatory diagnostics pass; it is a separate adjudication, not the immediate next step." |

**Corrected sequencing (authoritative).**

1. The estimation runs (three starts; cluster-robust SEs after each
   converged start; the full post-estimation diagnostics §13, §14).
2. The estimation report is returned to the project chat.
3. **The immediate next gate is a strict post-estimation review /
   SA2-readiness verdict.** This review adjudicates whether the
   estimation report and all mandatory diagnostics pass — convergence
   (D1–D3), the inference-validity confirmations (D9 full 9,657-cluster
   count, D10 robust-SE positivity, D11 robust-vs-Hessian comparison),
   and the carry-forward confirmations (D12 income routing, D13 cluster
   key, D14 no welfare, D15 M1-clean active).
4. **Only if the post-estimation review passes is the SA2 verdict
   drafted.** The SA2 verdict adjudicates the SA2 criteria S1–S11 (§15)
   and the M1-clean-versus-pooled baseline question.

The SA2 verdict remains a later adjudication gate. It is not the
immediate next step after estimation; the strict post-estimation review
/ SA2-readiness verdict is.

---

## 3. C2 — §19 cluster-robust SE artifact requirement

**Problem.** The §19 prompt instructed the estimation to save the report
"recording the per-start results, the Hessian-based and cluster-robust
SEs, all post-estimation diagnostics, the exact solver invocation used,
any halt and diagnosis, and the readiness of the SA2 verdict." This
required the SEs and the diagnostics in aggregate but did not explicitly
enumerate the cluster-robust SE artifacts the report must include or
produce. To remove any ambiguity that the report could record point
estimates without the full cluster-robust SE artifact set, §19 is revised
to require the artifact list explicitly.

**Revised §19 report-contents requirement.** The §19 prompt's report-
saving instruction is revised so that the estimation report must include
or produce, for each converged start, the following cluster-robust SE
artifacts (not only point estimates):

- **Converged theta by start** — the converged 55-parameter vector for
  each start.
- **Hessian / bread source** — the true Hessian (numerical second
  derivative of the negative log-likelihood at the converged theta) used
  as the sandwich bread, explicitly identified as the true Hessian, not
  the dummy Hessian of the smoke test.
- **Full 9,657-cluster confirmation** — confirmation that the meat-matrix
  assembly aggregated over exactly 9,657 unique `idorighh` clusters on the
  full dataset (T3).
- **Cluster-robust SE vector** — the cluster-robust standard-error vector
  for the 55 parameters (the square roots of the diagonal of the sandwich
  VCV, with zero at fixed/bounded parameters).
- **Robust covariance, or a documented output path to it** — the cluster-
  robust variance-covariance matrix, persisted and either reported or
  referenced by a documented output path.
- **T4 robust-SE positivity** — confirmation that the cluster-robust SEs
  are strictly positive for all free parameters at the converged theta
  with the true Hessian.
- **T5 robust-vs-Hessian comparison** — for each of the 55 parameters,
  the Hessian-based SE and the cluster-robust SE with the ratio
  cluster-robust/Hessian, flagging any parameter where the robust SE is
  smaller than the Hessian SE.
- **No welfare computation** — confirmation that no welfare computation
  was run.
- **M1-clean remains active pending SA2** — confirmation that M1-clean
  remains the active JMP baseline and that no output was promoted or
  canonicalised.

**Corrected §19 report-saving sentence.**

| Before | After |
|--------|-------|
| "Save the estimation report as `Results/JMP_pooled_P3a_estimation_report_v1.md`, recording the per-start results, the Hessian-based and cluster-robust SEs, all post-estimation diagnostics, the exact solver invocation used, any halt and diagnosis, and the readiness of the SA2 verdict." | "Save the estimation report as `Results/JMP_pooled_P3a_estimation_report_v1.md`. The report must include or produce, for each converged start, the full cluster-robust SE artifacts (not only point estimates): converged theta by start; Hessian/bread source (the TRUE Hessian, explicitly identified, not the dummy Hessian); full 9,657-cluster confirmation (T3); the cluster-robust SE vector; the robust covariance matrix or a documented output path to it; T4 robust-SE positivity; T5 robust-vs-Hessian comparison; confirmation that no welfare computation was run; and confirmation that M1-clean remains active pending SA2. The report must also record the per-start point estimates and objective values, all post-estimation diagnostics (§13), the exact solver invocation used, and any halt and diagnosis." |

**Corrected §19 closing instruction (the line following the report-save).**
The §19 closing instruction is revised to add, after "Do NOT issue an SA2
verdict":

> After estimation, the immediate next gate is a strict post-estimation
> review / SA2-readiness verdict. Only if the estimation report and all
> mandatory diagnostics pass should the SA2 verdict be drafted.

This aligns the §19 prompt's closing with the C1 sequencing correction.

---

## 4. What was not changed

The following are confirmed unchanged by this correction:

- The authorization to run the three-start pooled estimation of
  `ruro_occ_P3a_pooled` (§16 A1).
- The specification (§5, 55 parameters), data input (§6, harmonised
  pooled parquet), and cluster-robust inference requirement (§7,
  `idorighh`).
- The three starts (§8), the warm-start strategy (§9), the solver and
  vectorised mode (§10), and the expected runtime (§11).
- The required outputs (§12), the post-estimation diagnostics (§13,
  D1–D15), the cluster-robust SE outputs (§14, R1–R4), and the SA2
  verdict criteria (§15, S1–S11).
- The halt conditions (§18, H1–H6).
- The GA15 income rule (singles `ils_dispy_real`; couples
  `ils_dispy_male` / `ils_dispy_female`; no step assumes the scalar
  covers couples) and the GA17 limitation (smoke-test callability
  confirmed; inference validity confirmed post-estimation with the true
  Hessian and converged theta).
- The not-authorized scope (§17): the SA2 verdict, welfare computation,
  canonical promotion, M1-clean displacement, specification modification,
  and alternative pooled specifications all remain NOT authorized.
- All five required final statements.

No data was modified. No parquet was written. No specification was
changed. No estimation was run.

---

## 5. Final status

**The pooled P3a estimation execution authorization remains in effect
with the two corrections applied.**

The three-start pooled estimation of `ruro_occ_P3a_pooled` remains
authorized. The two corrections clarify (C1) that the immediate next gate
after estimation is a strict post-estimation review / SA2-readiness
verdict — not the SA2 verdict, which is drafted only if that review and
all mandatory diagnostics pass — and (C2) that §19 requires the full
cluster-robust SE artifacts as report contents, not only point estimates.

**The estimation may still be run** as authorized, per the corrected §19
prompt.

**The SA2 verdict remains a later adjudication gate, not the immediate
next step.** The immediate next gate after estimation is the strict
post-estimation review / SA2-readiness verdict.

**Welfare computation is NOT authorized.** Separately gated behind an
accepted SA2 verdict.

**Canonical promotion is NOT authorized.** The pooled estimates are
candidate results written to a versioned path.

**M1-clean 2016 remains the active JMP baseline.** Displaced only by a
future SA2 verdict explicitly promoting the pooled specification.
