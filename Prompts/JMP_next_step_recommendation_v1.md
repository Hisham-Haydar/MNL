# JMP Next-Step Recommendation v1

Date: 2026-05-18

Specification class: strategic recommendation memo. The memo
adjudicates among three candidate next operational steps —
welfare-measurement design, pooled multi-year estimation, and
further single-year specification adjustment — and recommends a
sequenced parallel-track design. The memo does not authorise
implementation; its output is a recommended task allocation and
sequencing that the subsequent operational prompts will build
upon.

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the accepted structural
  baseline)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_naive_robustness_verdict_v1.md` (the R2
  robustness exposure on the structural side, settled)
- `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the multi-year strategy design)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  welfare framework whose decisions memo this recommendation
  argues to draft)

---

## 1. The three candidates

The question posed identifies three candidate next steps for the
JMP. Each maps to a distinct category of project activity with
its own evidentiary content, operational cost, and dependency
relationship to the project's primary deliverable (the welfare
decomposition).

*Candidate (a) — Welfare-measurement decisions memo.* A design
document specifying the methodological choices for the welfare
decomposition: the welfare functional, the inequality index, the
counterfactual decomposition procedure, the reference
distributions, the gender attribution rule, and the operational
treatment of the singles consumption joint-identification
limitation. The memo is methodologically independent of the
structural specification: it applies equivalently to the M1-clean
preferred baseline, to the M1-naive robustness specification, and
to any future pooled multi-year specification. The document is
the methodological prerequisite for the welfare-scaffolding
implementation that produces the JMP's primary results. Its
production is a Claude Project chat task of medium scope,
approximately one to two focused sessions of drafting and
revision.

*Candidate (b) — Multi-year pooled estimation.* The structural
extension to a 2015–2017 pooled sample articulated in the v3.1
multi-year strategy memo. The full sequence comprises six
operational stages: a feasibility audit (Stage M0), a CPI
harmonisation and ID stacking utility (Stage M1), a GSURv2
lookup construction for 2015 and 2017 (Stage M2), a pooled MNL
parquet construction (Stage M3), pooled estimation in the (P2)
and (P3) configurations, and cluster-robust inference for the
(P3) configuration. The deliverable that earns operational
acceptance is the SA2 verdict on the pooled specification. The
full sequence is a multi-week Claude Code Sonnet undertaking;
the feasibility audit alone is a single-session entry-point task.

*Candidate (c) — Further single-year specification adjustment.*
Further refinements to the M1-clean specification beyond the
current 53-parameter configuration. Candidate refinements
identified in the framework memo and the M1-clean design memo
include Stage B age-specific GSUR (the O6 decision deferred from
the GSUR rebuild specification), an M2 fine-occupation
specification using the disaggregated `loc` variable, an M3
occupation-conditional wage specification with separate Mincer
parameters per occupation category, and an M4 occupation-
conditional hours specification. Each candidate refinement is a
multi-week Claude Code Sonnet undertaking with its own design
memo, implementation prompt, estimation run, post-estimation
diagnostics, and verdict.

---

## 2. Why candidate (c) is rejected

Candidate (c) is rejected as the immediate next step on four
grounds.

First, the structural baseline has reached a natural pause point.
The M0c_b2 → M0c_b2_GSURv2 → M1-clean trajectory delivered three
substantive structural improvements: the boundary-relaxation
resolution of the M0c_b leisure-intercept pathology, the
correction of the regional-misalignment and education-sex-
stratification failures in the GSUR variable, and the
operationalisation of the ability/opportunity partition through
the educational reclassification and the seven region dummies.
Each transition was motivated by specific diagnostic evidence
documented in the corresponding verdict memo. No comparable
diagnostic evidence currently motivates a further single-year
specification change. The M1-clean SA1-STANDS verdict and the
M1-naive R2 robustness exposure jointly establish that the
preference-block parameters, the wage-block parameters, the
occupation-block parameters, and the region-dummy block are
stable across the educational-reclassification decision; the
welfare-critical parameters R5.1 through R5.5 are preserved
unchanged; and the structural specification is operationally
coherent at the current 53-parameter configuration.

Second, the only remaining substantive identification weakness
in the M1-clean specification — the three negative-variance
parameters in the singles consumption joint-identification sub-
block (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`) — is sample-
size-sensitive rather than specification-driven. The same three
parameters exhibit the same near-singular Hessian sub-block in
M0c_b2_GSURv2, in M1-clean, and in M1-naive, with point estimates
shifting by less than 0.10 utility units across all three
specifications. The limitation reflects insufficient cross-
household variation in the singles consumption-leisure tradeoff
to identify both the scale parameters and the Box-Cox curvature
parameter simultaneously. Specification changes that preserve the
functional form (Box-Cox utility on consumption with a shared
exponent across the singles group) will not resolve the
limitation; specification changes that alter the functional form
(for instance, abandoning the Box-Cox specification in favour of
a translog or CES form) would impose a larger structural
restriction whose justification cannot rest on the singles-
consumption identification alone. The candidate refinements
identified in §1(c) — age-specific GSUR, fine occupation, and the
occupation-conditional wage and hours specifications — do not
address the singles consumption limitation.

Third, further single-year specification adjustment carries a
real risk of specification mining. The M1-clean verdict documented
four qualifications (Q1 through Q4) under the SA1-STANDS
decision: the marginal individual significance of
`beta_E_drgn8`, the singles-male participation regression of 0.92
percentage points, the singles-male hours-bin L1 regression of
9.6 per cent, and the BIC penalty of 50.4 units. None of the four
qualifications constitutes an identification failure; each
reflects a documented tradeoff associated with the structural
choices that the welfare partition motivates. Pursuing further
single-year refinements with the aim of resolving these
qualifications would risk producing a specification whose fit
improvements are driven by post-hoc tinkering rather than by
principled structural extensions. The accumulated qualifications
across multiple sequential refinements would weaken rather than
strengthen the JMP's empirical credibility.

Fourth, the framework memo's robustness architecture treats Stage
B age-specific GSUR (the O6 decision) and the M2/M3/M4 occupation-
conditional specifications as *post-baseline* extensions to be
evaluated against an established preferred baseline. Pursuing them
now — before the welfare scaffolding is implemented and the
welfare decomposition is computed — would produce structural
findings without a welfare-baseline reference against which to
evaluate them. The robustness exposures these extensions support
are most informatively reported once the welfare baseline is in
place; pursuing them in advance of welfare computation puts the
robustness exposures before the primary result.

Candidate (c) is therefore not recommended as the next step. The
candidate refinements remain in the project's task inventory as
post-welfare-baseline robustness exposures and may be revisited
when the welfare baseline is operative.

---

## 3. Why candidates (a) and (b) are complementary

Candidates (a) and (b) are not in competition for the next
operational slot. They occupy distinct tracks of project activity
that proceed on different tool platforms (Claude Project chat for
(a); Claude Code Sonnet for (b)), produce distinct deliverable
types (a methodological design document for (a); empirical
estimates and a SA2 verdict for (b)), and converge at distinct
points in the project sequence (the welfare-measurement memo
becomes a prerequisite for welfare scaffolding implementation;
the pooled estimation becomes a prerequisite for the SA2 verdict
that determines the JMP's primary baseline).

The two tracks are methodologically independent. The welfare-
measurement decisions memo articulates the functional, the
inequality index, the decomposition method, and the gender
attribution rule under which welfare results will be reported.
These methodological choices apply equivalently regardless of
whether the operative structural baseline is M1-clean (the
current preferred specification), M1-naive (the R2 robustness
exposure), or a future pooled specification under a SA2-STANDS
verdict. The memo specifies how the welfare results *will be
computed* once a structural baseline is locked, not which
structural baseline that will be.

The multi-year track, conversely, addresses the question of which
structural baseline is operative. The v3.1 strategy memo §10
establishes that M1-clean remains the JMP's preferred baseline
until a pooled specification earns its own SA2-style verdict; the
multi-year track is the operational route by which a pooled
specification may earn that verdict. The track's success is
neither assured nor required: under SA2-OVERTURNED, the JMP
defaults to the M1-clean single-year baseline and the multi-year
work is archived as a methodological investigation. The track is
worth pursuing not because its outcome is predetermined but
because its evidentiary returns — improved parameter precision,
potential resolution of the singles consumption identification
limitation, temporal generalisability across 2015–2017 — would be
substantial under SA2-STANDS and would strengthen the JMP's
empirical contribution.

The two tracks therefore proceed on parallel critical paths. The
welfare-measurement decisions memo can be drafted, reviewed, and
finalised in this chat over approximately one to two focused
sessions. The multi-year feasibility audit can be executed in
Claude Code Sonnet as a single-session preparatory step that
authorises the subsequent pipeline implementation stages. Neither
task blocks the other; both contribute to the JMP's eventual
welfare-scaffolding implementation; together they constitute the
most efficient next-step sequencing.

---

## 4. Why the welfare-measurement decisions memo is the higher-leverage chat task

Within the parallel-track recommendation, the welfare-measurement
decisions memo is the higher-leverage chat task on three grounds.

First, the memo is the methodological backbone of the JMP's
welfare contribution. The functional choice (Fleurbaey-style
equivalent income, equivalent variation, compensating variation,
or an alternative), the inequality index (Gini, Atkinson with
specified inequality-aversion parameter, generalised entropy
with specified parameter, or alternative), the decomposition
method (ordered removal, Shapley, or both reported as robustness),
the reference distributions for ability and opportunity, and the
gender attribution rule (A1, A2, A3, or a documented alternative)
collectively determine the form of the welfare decomposition that
the JMP will report. Each of these choices is independently
defensible under multiple framings; the memo's role is to commit
the JMP to a specific principled framing whose justification
operates across the empirical estimates.

Second, the memo has been deferred across multiple verdict chains.
The M0c_b2_GSURv2 verdict §11 noted welfare scaffolding as a
deferred task. The M1-clean verdict §22 and §24 reaffirmed that
welfare scaffolding implementation requires the welfare-
measurement decisions memo as a prerequisite. The M1-naive
robustness verdict §15 and §17 again identified the memo as a
recommended parallel task. The successive deferrals reflect the
structural-side priorities of the recent project sequence, but
they have produced a critical-path bottleneck: any subsequent
project work that touches welfare computation requires the
memo's methodological commitments, and the absence of those
commitments now constrains what the multi-year track's
deliverables can ultimately support. Producing the memo at this
point resolves the bottleneck and unblocks the welfare-scaffolding
implementation that will eventually consume the M1-clean
estimates, the M1-naive estimates (for robustness), and any
pooled estimates that earn SA2 promotion.

Third, the memo is the operational vehicle through which the
substantial welfare-literature reading in the project (Aaberge-
Colombino 2018; Bhattacharya 2015; Bargain et al. 2013; Capéau et
al. 2021; Fleurbaey-Maniquet 2006/2011/2018/2019; Bargain et al.
2016; Aaberge-Colombino on rank-dependent SWFs; Shorrocks 2013 on
Shapley decomposition; Ferreira-Gignoux 2011; Bourguignon-
Ferreira-Menendez 2007) is operationalised in a JMP-specific
framework. The literature provides multiple defensible choices on
every dimension of the welfare decomposition; the memo selects
among them on principled grounds connected to the JMP's specific
empirical context (a structural labour-supply model with latent
job opportunities, a household sample of singles and couples in
metropolitan France, an ability/opportunity partition that
implements the framework memo's interpretation of the weak
Dworkinian welfare criterion). The selection is not an arbitrary
methodological choice but a substantive contribution to the JMP's
welfare-decomposition design.

The memo is the appropriate next chat task. Its production does
not delay or compete with the multi-year track; it complements
it.

---

## 5. Why the multi-year feasibility audit is the appropriate parallel Claude Code Sonnet task

Within the parallel-track recommendation, the multi-year
feasibility audit is the natural Claude Code Sonnet task on three
grounds.

First, the audit is a low-cost entry point that initiates the
multi-year track without committing to its full implementation.
The v3.1 strategy memo §4 specifies six conditions the audit
verifies: EUROMOD FR_2015 and FR_2017 system installation; EU-
SILC microdata availability for 2015 and 2017; Eurostat
`lfst_r_lfu3rt` and `lfst_r_lfsd2pop` availability for 2015 and
2017; INSEE BDM 001688526 unemployment-rate benchmark for 2015
and 2017; INSEE CPI series for 2015, 2016, and 2017; and EUROMOD
output variable comparability across the three years. The audit
also records the maximum identifier magnitudes required by the
§6 numerical encoding scheme and confirms the canonical
clustering key (`idhh_raw` or `idorighh_raw`). The audit's
walltime is approximately one focused Claude Code Sonnet
session.

Second, the audit's findings determine the operational scope of
the subsequent multi-year work. If all six conditions pass, the
audit authorises the pipeline implementation stages M1 (CPI
harmonisation and ID stacking utilities), M2 (GSURv2 lookups for
2015 and 2017), and M3 (pooled MNL parquet construction). If any
condition fails — for instance, if EU-SILC 2015 is unavailable
in the local data directory, or if the EUROMOD FR_2015 system is
not configured — the audit identifies the operational response
and may adjust the scope of the pooled estimation to a two-year
configuration (P2 only, dropping 2017 entirely, or P1
reparameterised dropping 2016). The audit therefore serves as a
sequencing-decision input for the subsequent multi-year work,
ensuring that the pipeline implementation proceeds against a
verified data foundation.

Third, the audit produces information that informs the welfare-
measurement decisions memo. The memo's specification of the
reference distributions, the gender attribution rule's
operational application, and the treatment of the singles
consumption identification limitation may benefit from knowing
whether the multi-year track is two-year (2015 + 2016 only) or
three-year (2015 + 2016 + 2017) in scope. The audit's findings,
delivered in parallel with the memo's drafting, allow the memo
to specify the multi-year-track contingencies explicitly rather
than abstractly.

The audit is the appropriate Claude Code Sonnet task. Its
parallel execution alongside the welfare-measurement decisions
memo produces the maximum information yield from the next
operational stage without overcommitting to either track's full
implementation.

---

## 6. Recommended task allocation and sequencing

The recommendation is summarised in Table 1.

| Track | Task | Tool platform | Walltime | Output |
|---|---|---|---|---|
| Chat | Welfare-measurement decisions memo | Claude Project chat | 1–2 focused sessions | `docs/JMP_welfare_measurement_decisions_memo_v1.md` |
| Code | Multi-year feasibility audit | Claude Code Sonnet | 1 focused session | `Results/P3a/multi_year_stage_M1/JMP_multi_year_feasibility_audit_v1.md` |
| Deferred | Further single-year specification adjustment | (n/a) | (n/a) | Deferred until welfare baseline is in place |

The chat task and the code task proceed in parallel. Neither
blocks the other; both contribute to the project's eventual
welfare-scaffolding implementation. The recommended ordering
within the chat track is that the welfare-measurement decisions
memo is drafted before the multi-year feasibility audit
authorises any pipeline implementation work, ensuring that the
memo's methodological commitments are settled before the multi-
year empirical infrastructure begins to consume Claude Code
Sonnet sessions on a sustained basis.

The downstream sequencing, following these two parallel tasks,
proceeds as follows:

1. After the welfare-measurement decisions memo is finalised:
   the methodological choices are locked, and the welfare-
   scaffolding implementation may be specified.
2. After the multi-year feasibility audit completes
   successfully: the pipeline implementation Stages M1, M2, M3
   may be initiated in Claude Code Sonnet.
3. After Stages M1–M3 complete: the pooled estimation in (P2)
   configuration may be initiated, followed by the (P3)
   configuration under cluster-robust inference.
4. After the pooled estimation completes: the SA2 verdict is
   written, determining whether the pooled specification
   replaces M1-clean as the JMP's primary baseline.
5. After the SA2 verdict: the welfare-scaffolding implementation
   may proceed, operating against whichever specification is
   the JMP's primary baseline at that stage.
6. After welfare scaffolding is implemented: the welfare-
   decomposition computation produces the JMP's primary
   results, supplemented by the R1 through R9 robustness
   exposures including R2 (the M1-clean-vs-M1-naive comparison
   on the welfare side).
7. After the welfare results are computed: the JMP draft and
   slides are produced.

Steps 1 and 2 may proceed in parallel from the current point.
Step 3 follows step 2. Step 4 follows step 3. Step 5 requires
both step 1 and step 4 to be complete. Steps 6 and 7 follow
step 5.

The total walltime from the current point through step 4
(SA2 verdict) is approximately eight to ten weeks of focused
work under the parallel-track design, dominated by the Claude
Code Sonnet pipeline implementation. The walltime from step 4
through step 7 (JMP draft) depends on the SA2 outcome and on
the welfare-decomposition computational scope; an additional
six to ten weeks is a reasonable expectation.

---

## 7. What the recommendation does not do

The recommendation does not commit the project to the full
multi-year track. The feasibility audit is the entry-point task;
its completion authorises but does not require the subsequent
pipeline implementation. If the audit reveals that the multi-year
infrastructure is more costly than anticipated (for instance, if
EUROMOD FR_2015 requires substantial configuration work or if
the EU-SILC microdata for 2015 is unavailable), the subsequent
sequencing may be revised to defer or descope the multi-year
work. The recommendation's commitment is to *initiate* the
multi-year track through the audit, not to *complete* it.

The recommendation does not pre-empt the welfare-measurement
decisions memo's specific methodological commitments. The memo's
choice of welfare functional, inequality index, decomposition
method, reference distributions, gender attribution rule, and
operational handling of the singles consumption limitation
remains open at the design stage. The recommendation is that
these choices be made and documented; it is not that they take
any particular form.

The recommendation does not authorise welfare-scaffolding
implementation, welfare-decomposition computation, canonical
MNL promotion, Stage B age-specific GSUR work, or any
specification adjustment beyond M1-clean. Those activities
remain deferred to their respective gating decisions.

The recommendation does not foreclose option (c). If the
welfare-measurement decisions memo identifies a methodological
requirement that motivates a specific single-year specification
adjustment (for instance, if the decomposition method requires
identified consumption-leisure substitution parameters that the
current Box-Cox formulation does not deliver), the project may
revisit option (c) with the specific motivation in hand.

---

## 8. The strict recommendation, stated concisely

The next operational step is the parallel-track design comprising
(a) the welfare-measurement decisions memo drafted in this chat
and (b) the multi-year feasibility audit executed in Claude Code
Sonnet. Option (c) is deferred indefinitely pending welfare-
baseline establishment.

The welfare-measurement decisions memo is the higher-leverage
immediate chat task because it has been deferred across multiple
verdict chains, it is methodologically independent of the
structural baseline, and it is the prerequisite for the welfare-
scaffolding implementation that consumes all subsequent
empirical estimates.

The multi-year feasibility audit is the appropriate parallel
Claude Code Sonnet task because it is a single-session preparatory
step that initiates the pooled-specification track at low
operational cost, and its findings inform both the subsequent
pipeline implementation and the welfare-measurement decisions
memo's specification of multi-year-track contingencies.

The recommendation answers the question posed: the next step is
*not* a single choice from (a), (b), or (c), but a sequenced
parallel-track design with (a) and (b) advancing in tandem and
(c) deferred.
