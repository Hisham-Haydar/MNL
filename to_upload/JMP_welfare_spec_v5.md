# JMP Welfare Specification Memo v5

**Date:** 2026-06-01
**Document class:** prose design memo. Settles the money-metric welfare
object(s) before any welfare implementation. Does **not** write welfare code,
compute welfare numbers, or compute decomposition numbers.
**Answers:** JMP supporting question 2 (how to compute money-metric well-being
under *different* feasible job sets) and elevates supporting question 4
(sensitivity to alternative welfare measures) from a robustness check to a
**headline object**.
**Certified baseline it is written against:** the 47-param pooled spec
`joint_pooled_v1_bll0_tlmpin` (`beta_ll=0`; `theta_l_m=-0.8` pinned;
`beta_E`, `beta_h_pt2` SHARED), identification-certified at the 901-alt
resolution (synthetic Check-5 PD `min_eig=+1.706`; real-data Hessian PD
`min_eig=+0.459`).

**Relationship to other documents.** Welfare-object layer of the two v2 welfare
memos, updated to the certified baseline. Supersedes `JMP_welfare_spec_v1.md`,
`JMP_welfare_spec_v2.md`, `JMP_welfare_spec_v3.md`, and `JMP_welfare_spec_v4.md`.
The single contract a later
`RURO_welfare_scaffold_design_contract_v1.md` translates into code.

---

## 0. What this memo carries forward and what it revises

**Carried forward unchanged.** Household-level, money-metric,
preference-respecting equivalent income; ex-ante log-sum (inclusive-value)
attained utility with the mandatory proposal/prior correction; the three-way
{preference, ability, access} cut; Shapley–Shorrocks order-independence; gender
attribution rules A1/A2/A3; cluster-robust bootstrap on `idorighh`;
singles–couples reporting separation; specification-agnostic YAML-driven input
boundary; the three baseline-specific bindings of §3.

**The headline revision in v3 — the welfare object is a *family*, not one
measure.** v2 fixed the object to $W^5$. v3 removes that restriction: the JMP
computes the **entire characterised family $W^1,\dots,W^6$** from the companion
theory paper (Haydar–Maniquet, in progress) and **compares them**. The
comparison across the family is no longer a robustness footnote; it is the
JMP's direct, empirical answer to "how does the assessment of well-being
inequality depend on the normative stance about responsibility." This is
*stronger* than a single-measure design and it is the right shape for a paper
about responsibility disagreement.

**Consequences of the revision, settled in this memo.**

- **(V3-1) Two distinct exercises, kept distinct.** *Exercise A — the measure
  menu:* compute each $W^k$ and compare the resulting welfare distributions and
  inequality $I(\Omega^k)$ along a compensation–responsibility spectrum.
  *Exercise B — the source decomposition:* attribute the inequality of a chosen
  measure to access / ability / preference by Shapley equalisation. A and B are
  complementary lenses on one disagreement; the memo specifies how each is run
  and how they relate (§1.3, §2).
- **(V3-2) The opportunity content is a *surface*, not a single bracket.** It
  depends on two axes — which measure (normative stance) and which channel is
  equalised. The v2 `[access-only, access+ability]` bracket survives as the
  *within-measure* range; the measure menu is the *across-stance* range; the
  headline is their joint surface (§2, §5).
- **(V3-3) The measure choice and the decomposition channel are the *same*
  normative cut, operationalised two ways.** Each $W^k$ encodes a stance through
  its Independence-of-$\mathbf{y}$ / Independence-of-$A$ properties; the
  decomposition encodes a stance through which channel it equalises. They must
  be reported **jointly** and not double-interpreted. The decomposition is
  *anchored* on measures that do not pre-absorb the channel being attributed
  (§1.3, §2).
- **(V3-4 → v4) Family vs single measure: both halves of the citability
  trade-off.** Using the family is robust to proof-incompleteness in a way the
  v2 single-measure design was not — the *comparison's* validity needs the
  functional forms and their normative readings, not each finalised uniqueness
  proof. It does, however, import a *broader* normative taxonomy than v2's single
  object, so in the sense of the JMP–theory-paper boundary it leans on the
  companion paper's interpretation *more*, not less. Both are true; v4 states
  both and locks the resolution: import the normative readings as cited
  primitives, re-derive nothing, default to the spectrum framing if the companion
  paper is not yet citable (§1.3).
- **(V3-5) The "random opportunities" framing remains removed.** Opportunities
  are deterministic, as in the companion theory paper. The JJT differentiation
  is re-grounded accordingly and sharpened by the menu (§4).
- **(V3-6) Baseline membership update** (unchanged from v2): occupation offers
  are six gender-specific params; year shifts are inside access; the count is
  the certified 47 (`beta_ll` removed, `theta_l_m` pinned).
- **(V5-1) Integration scheme fixed against the proposal audit; object
  unchanged.** v5 leaves the welfare object identical to v4 and settles only how
  the ex-ante attained utility is *evaluated*. The proposal audit
  (`welfare_proposal_individualisation_check.md`) establishes that the estimation
  proposal $\pi$ is partly individualised — wage (household-specific mean
  $\mu_i = X_i b + \delta_{\mathrm{occ}}[\mathrm{loc4}_i]$) and occupation
  (gender$\times$education stratum) condition on $x_i$; hours (fixed D1 five-mode
  mixture) and employment (flat $\pi_0 = 0.10$) are common; the structural market
  block (GSUR/region/year) lives in utility $g$, not in $\pi$. Because the two
  individualised channels are the high-dispersion channels of the integrand,
  importance sampling over the existing draws is well-conditioned, and the redraw
  scheme is demoted to a validation cross-check. §1.1 and §6 are revised
  accordingly; nothing else changes.

---

## 1. The welfare object(s)

### 1.1 Computational form: ex-ante attained utility, then invert

All six measures are equivalent-income-type objects — each is an income/subsidy
that equates the household's attained situation to a reference under the
household's **own preferences**. The common computational core is the **ex-ante
expected-maximum (inclusive-value) attained utility**

$$
V_i \;=\; \log \sum_{j \in \mathcal{C}_i}
\exp\!\Big( v_i(c_j,\ell_j)\;+\;\log g(j;x_{\mathrm{opp},i})\;-\;\log \pi(j)\Big),
$$

with $-\log\pi(j)$ the mandatory proposal/prior correction (the welfare analogue
of the sampling-of-alternatives correction; state draw count/scheme — the §6
welfare-integration gate governs its validation). The six measures differ only in
the **reference** against which $V_i$ is converted to money.

The welfare-integration estimator is **importance sampling over the existing
estimation draws** with the household-specific proposal weight:

$$
\widehat V_i^{\,\mathrm{IS}} \;=\; \log \sum_{j \in \mathcal{C}_i}
\exp\!\Big( v_i(c_j,\ell_j) + \log \hat g(j;x_i) - \log \pi(j;x_i) \Big),
$$

where $-\log\pi(j;x_i)$ is the per-row `prior` column already on the engine-ready
data. This is the **primary** scheme. Its consistency for the inclusive value
$V_i$ does not depend on $\pi$ conditioning on $x_i$; the proposal audit
(`welfare_proposal_individualisation_check.md`) additionally establishes that it
is **well-conditioned**, because the two proposal channels that carry heavy
covariate-driven concentration in $\hat g$ — wage and occupation — are
individualised, so the importance-sampling divergence $D(\hat g_i \,\|\, \pi)$ is
small on exactly the dimensions that would otherwise dominate its variance. The
scheme is **analytic in the extreme-value shocks** (the log-sum is the closed-form
expectation over $\varepsilon$); it invokes **no Fréchet draws and no simulated
argmax**, which belong to behavioural simulation (fit, elasticities,
counterfactuals) and remain deferred. The redraw-from-$\hat g_i$ estimator
$\widehat V_i^{\,\mathrm{dir}}$ (integration nodes drawn from the estimated
individual opportunity density, $\varepsilon$ still integrated analytically) is
**retained as a validation cross-check**, escalated to primary only on a flagged
subset per the §6 effective-sample-size gate. Two guardrails carry from v2
unchanged: the **ex-post chosen-alternative certainty-equivalent** (conditioning
on the observed $j^*$) is a proposal-correction-free cross-check, diagnostic not
headline; and **EV/CV** (de Palma–Kilani) are secondary objects for AC/JJT
comparability. Both are analytic in $\varepsilon$; the entire welfare layer
requires no shock draws.

### 1.2 Guardrails common to all measures

1. **`beta_c=1` fixes the scale, not the money number.** Every measure is an
   inversion at a declared reference; the references, the within-reference
   evaluation, and the reference preference are the normative inputs.
2. **Stochastic-choice analogue, stated.** Each $W^k$ is defined on a realised
   bundle $z$; the empirics replace $z$ with attained utility $V_i$. This gap
   applies uniformly to all six and must be named, not hidden.
3. **Welfare unit = household; do not split couples.** One $\Omega_i^k$ per
   couple from joint utility and joint budget; within-couple gender enters
   through the attribution rules; intra-household equivalisation is deferred.
4. **Two references need an explicit universal set.** $W^4$ (staying-home) needs
   the non-employment option $o$ — present in the choice set. $W^6$ (best job in
   the whole economy) needs the universal job set $\mathcal{J}$ — define it as
   the pooled support of offered job types and declare it in config. $W^5$ needs
   the reference ability set $\bar A$ (the v2 reference opportunity set).

### 1.3 The measure family $W^1$–$W^6$: the compensation–responsibility spectrum

The companion theory paper *characterises* $W^1,\dots,W^6$ by axioms. The JMP
carries **zero theory load**: it imports the measures, cites the companion paper
for their foundation, and proceeds to estimation, computation, and comparison.
It restates no axioms as JMP results and reproduces no proofs. The
characterisation is the companion paper's content; the empirical comparison is
the JMP's.

The organising axis is the pair of compensation properties: **Independence of
$\mathbf{y}$** (not responsible for *how much* jobs pay — the pay/productivity =
*ability* dimension) and **Independence of $A$** (not responsible for *which*
jobs are feasible — the *access* dimension). Full Compensation $=$ both.

| Measure | Reference / construction | Ind $\mathbf{y}$ | Ind $A$ | Normative reading |
|---|---|---|---|---|
| $W^4$ | staying-home equivalent | + | + | **Full Compensation** — compensate access *and* pay |
| $W^6$ | best job in the whole economy $\mathcal{J}$ | + | + | **Full Compensation** (+ Weak Responsibility) |
| $W^1$ | preferred job in own set, pay ignored | + | − | **compensate pay; responsible for the set** |
| $W^5$ | uniform subsidy to reference set $\bar A$ | − | + | **compensate the set; responsible for pay** |
| $W^2$ | best-paid equivalent in own set | − | − | **Full Responsibility** (own everything) |
| $W^3$ | laissez-faire (own set, with pay) | − | − | **Full Responsibility** (laissez-faire) |

Three structural facts about this family drive the design.

**The endpoints and the duals.** $W^4/W^6$ are the **Full Compensation**
endpoint (compensate both opportunity dimensions); $W^2/W^3$ are the **Full
Responsibility** endpoint (own both). $W^1$ and $W^5$ are the **two one-sided
duals**: $W^1$ compensates the *pay* (ability) dimension and holds the
individual responsible for *access*; $W^5$ compensates the *access* dimension
and holds responsible for *pay*. This duality is exactly the access/ability cut,
read off the measure menu rather than imposed by the decomposition.

**All six read attained utility, so access never "drops out."** A measure
satisfying Independence of $A$ does not depend on the *shape* of the actual set,
but it reads attained utility $V_i$, and a constrained set lowers $V_i$. So
unequal access still produces unequal welfare under *every* measure, through
attainment/choice. Where the Ind-$\mathbf{y}$/Ind-$A$ properties bite is in the
*direct* evaluation channel: a non-Ind-$\mathbf{y}$ measure ($W^2,W^3,W^5$) also
revalues welfare when pay changes *holding the attained bundle fixed*; an
Ind-$\mathbf{y}$ measure ($W^1,W^4,W^6$) does not. This is precisely why the
decomposition is **not measure-invariant** and must be anchored (below).

**Measure choice and decomposition channel are one disagreement, twice.**
Choosing $W^4$ (Full Compensation) already compensates the opportunity
dimensions; running an "equalise access" decomposition on top then captures only
the residual *attainment* channel, not the full opportunity content. Choosing a
Full Responsibility measure ($W^2/W^3$) pre-compensates nothing, so the
decomposition does *all* the attribution work and the opportunity content is at
its largest. The two operations therefore overlap, and the memo keeps them
distinct by anchoring the decomposition (D2) on measures that do not
axiomatically pre-absorb the channel being attributed.

**Citability, reframed as a feature.** The companion draft still marks several
characterisations "to be proven." Two things are true at once and v4 states
both. First, the *comparison* across a family of well-defined functional forms
with transparent normative readings (full compensation, one-sided compensation,
full responsibility) is valid independently of whether each uniqueness proof is
final — so v4 is robust to proof-incompleteness in a way the v2 single-measure
design was not. Second, and against the favourable reading, v4 imports a
*broader* normative taxonomy than v2's single object — the
Ind-$\mathbf{y}$/Ind-$A$ classification, the full-compensation/full-responsibility
labels, and the choice of *these six* are the companion paper's content — so in
the sense of the JMP–theory-paper boundary v4 leans on the companion paper's
interpretation *more*, not less. The resolution: import the normative readings
as **cited primitives**, re-derive nothing, and make the spectrum framing the
**default presentation** — "money-metric measures spanning the
compensation–responsibility spectrum," leaning on Fleurbaey–Maniquet (2018) and
Decancq–Fleurbaey–Schokkaert (2015) with a forward reference — to be used if the
companion paper is not at working-paper stage when the JMP is submitted. Either
way the JMP stands alone; the dependence is on cited interpretation, not on
reproduced proofs.

**Relation to JJT, sharpened.** JJT compare two objects — CV (own preferences)
vs CV$^{\text{circ}}$ (preferences neutralised) — i.e. they vary the
**preference** axis at a single (education-driven, deterministic) opportunity
treatment. The JMP holds preferences *respected* throughout and varies the
**opportunity** treatment across six characterised stances. The two designs are
near-orthogonal: JJT move along the preference dimension, the JMP along the
access/pay dimension. The JMP can additionally run a JJT-style
preference-neutralisation as a *further* robustness, but the core contribution
is the opportunity-treatment menu, which JJT do not have.

### 1.4 Recommendation

- **D1 — Welfare object = the family (Exercise A is the headline).** Compute
  $\Omega_i^k$ for $k\in\{1,\dots,6\}$ on the ex-ante attained utility $V_i$, and
  report the welfare distributions and inequality $I(\Omega^k)$ ordered along the
  compensation–responsibility spectrum (Full Responsibility $W^2,W^3$ →
  one-sided $W^1,W^5$ → Full Compensation $W^4,W^6$). This menu *is* the JMP's
  answer to supporting question 4.
- **D2 — Decomposition (Exercise B), anchored.** Run the access/ability/
  preference Shapley decomposition on the measures that do not pre-absorb the
  attributed channels: a **Full Responsibility anchor** ($W^2$ or $W^3$) as the
  "total source-composition" picture (the decomposition does all the work), and
  the **one-sided duals** $W^5$ (access-compensated) and $W^1$ (pay-compensated)
  to expose each dimension. Report the decomposition under the Full Compensation
  measures *as well*, framed explicitly as showing the opportunity content
  migrating into the measure as the stance becomes more compensatory — i.e. the
  opportunity surface (V3-2).
- **D3 — Secondary forms.** Ex-post chosen-alternative CE (correction-free
  cross-check); EV/CV (AC/JJT comparability). Configuration switches, one
  machine.

A narrative note: lead the paper with the menu (Exercise A) plus two focal
decompositions — the Full Responsibility "total sources" and the $W^5$
"access-compensated" — and present the remaining measures as the sensitivity
surface. The memo settles the design; the focal point is an exposition choice.

---

## 2. How the family feeds the decomposition

The structural-to-normative mapping is unchanged: preference $= v$;
ability $+$ access $= g$ (cut $g$ in two).

**Block membership at the certified 47-param baseline.**

| Component | Parameters (47-param baseline) | Channel |
|---|---|---|
| **Preference** ($v$) | `beta_l0_{sm,sf,f}`, `beta_l_age{,2}_{sm,sf,m,f}`, `beta_l_nkids_{sf,f}`, `theta_l_{sm,sf,f}`, `theta_c_singles`; fixed `theta_l_m=-0.8`, `beta_ll=0`, `beta_c=1` | tastes over consumption, leisure, children-time |
| **Ability** (in $g$, wage tech.) | `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma`; `beta_w0` = common anchor | returns to own education/experience; residual productivity |
| **Access** (in $g$, rest) | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh`; `beta_E_gsur`, `beta_E_drgn2..8`, `beta_E_drgur`, `beta_E_drgmd`, `beta_E_y2015`, `beta_E_y2017`; `beta_occ_{2,3,4}_{m,f}` | hours/market/occupation/year offer availability |

**Two cuts, related.** The ability/access boundary is the
Independence-of-$\mathbf{y}$ / Independence-of-$A$ distinction. The *measure menu*
(Exercise A) operationalises that distinction by **choosing how much each
dimension is compensated**; the *decomposition* (Exercise B) operationalises it
by **equalising a channel and measuring the inequality fall**. The two endpoints
of the menu bracket the decomposition: under Full Responsibility ($W^2/W^3$) the
decomposition's opportunity content is largest (nothing pre-compensated); under
Full Compensation ($W^4/W^6$) it is smallest (opportunity pre-compensated, only
the attainment channel remains); the one-sided duals $W^1/W^5$ sit between and
isolate one dimension each.

**What is held fixed to isolate each component** (welfare recomputed under each
equalisation; Shapley-averaged over the $3!=6$ orderings, summing exactly to
$I(\Omega^k)$ for the chosen measure $k$):

- **Access:** set the access blocks (hours, market, occupation, year) to a
  common reference offer environment; hold ability and preference at actual
  values; recompute $\Omega^k$. Mechanically this changes each household's $V_i$
  via the feasible set, which feeds every measure; under non-Ind-$A$ measures it
  additionally changes the direct evaluation. The inequality fall is the access
  component; **lower bound** of the opportunity share *for that measure*.
- **Ability:** neutralise the wage technology's dependence on own
  education/experience and residual productivity (`beta_w0` stays as anchor);
  hold access and preference fixed; recompute. Access $+$ ability $=$ **upper
  bound** of the opportunity share *for that measure*. The companion paper's
  Extension (abilities as $A(e,b)$ from effort $e$ and background $b$) is why
  ability sits on the contested boundary and is reported as a range, not a
  point.
- **Preference:** assign a common reference preference (the horizontal reference
  $R^h$ is the natural choice and is the comparability device several of the
  measures already use) and revalue each feasible set with it. This changes the
  yardstick; report conditional on the reference with a reference-preference
  sensitivity. Preference is the complement of the opportunity content.

**The headline object is the opportunity surface** over (measure $\times$
channel), with the v2 within-measure `[access-only, access+ability]` bracket
nested inside it. Report it as such; do not collapse it to one number, and do
not double-interpret the measure stance and the decomposition channel.

**Specification/case agnosticism.** Block membership, fixed parameters,
references ($\bar A$, $\mathcal{J}$, $o$), the cross-section filter (year), the
reference preference, the cluster unit, *and the active measure set* are read
from YAML/config — no hardcoded France/2016/P3a constants except when describing
current evidence. Adding or removing a measure from the menu is a configuration
change, not a code change.

---

## 3. Baseline-specific constraints from the actual estimate

Findings from the certified 47-param fit, not hypotheticals. They bind every
measure in the family identically (all read the same $\hat\theta$ and $V_i$).

### 3a. Couples-male leisure is near-degenerate (`beta_l0_m` at floor)

`beta_l0_m = 1\mathrm{e}{-6}` (floor); `theta_l_m` pinned at $-0.8$. The
couples-male leisure side of $v$ collapses toward zero — a data fact
(near-universal male full-time participation), not an artifact. Under the
household-level unit this is benign (a positive argument for that unit); under an
individual-level unit it would mean attributing a near-empty male preference per
capita. Report the couples-male preference contribution as
near-zero/structurally pinned, with the caveat that it reflects *unidentified*
male-leisure variation, not absent preferences. `theta_l_m` and `beta_ll` are
pinned → **zero uncertainty** by construction; the bootstrap holds them fixed.
This is identical across all six measures.

**Trace into the decomposition (Exercise B) — this is the consequential step.**
The pinned/degenerate couples-male leisure preference mechanically **compresses
the couples preference component**. Because the decomposition attributes
"everything not preference" to opportunity, a compressed preference channel will
**inflate the couples opportunity share relative to singles for a non-structural
reason** — not because access genuinely binds harder on couples. Two
requirements follow for the scaffold contract: (i) it must specify whether the
pinned preference params (`theta_l_m`, `beta_ll`) are *held at their pinned
values* or *swapped for the reference preference* under the
preference-equalisation channel, since that choice sizes the couples preference
component and therefore the couples opportunity share; and (ii) couples and
singles opportunity shares must be reported **separately** under this caveat —
never pooled into a single opportunity-share headline number. This is a
refinement of the decomposition reporting, not a redesign.

### 3b. SE asymmetry → component-uncertainty asymmetry

Certified-baseline median SEs (clustered on `idorighh`): wage_opp 0.012;
occupation_opp 0.047; market_hours_opp 0.124; couples_leisure 0.394;
singles_leisure 0.387. The opportunity blocks are an order of magnitude tighter
than the leisure blocks. **The opportunity content — the JMP's headline — is
more precisely estimated than the preference complement, under every measure.**
Inference: per-component, per-measure bootstrap CIs, cluster-robust on
`idorighh` (9,657 clusters); state that opportunity-content CIs are expected
tighter than preference CIs. No asymptotic SEs for the headline — three params
sit at bounds (`beta_l0_m` lo, `beta_l_age2_sf` hi, `beta_l_age2_f` hi), where
asymptotic SEs are invalid; the bootstrap is the inference procedure. Note the
bootstrap cost now scales with the number of measures on the menu; this is a
compute-budget item for the scaffold contract, not a design change.

### 3c. Shared `beta_E` / `beta_h_pt2` (gender split NOT certified)

Baseline uses **shared** hours-offer parameters. The LR test rejected sharing
in-sample, but the synthetic gate showed the split is **not separately
recoverable** at 901 (`RURO_gsplit_nonid_structure_v1.md`): `beta_h_pt2` =
independent mislocation (no reparameterisation rescues it; pooled is the only
honest baseline; any gender difference is an in-sample caveat, never an
identified estimate, and must not enter any measure as a recovered gendered offer
parameter); `beta_E` = partial ridge (contrast modestly identified, level flat;
a level+deviation reparameterisation might recover the contrast later). Baseline
welfare for all six measures uses shared offer parameters; gender-differentiated
offers are a planned robustness only; a future `beta_E` swap is a config change
(offer-param names read from YAML); `beta_h_pt2` is excluded from that path.

---

## 4. Literature positioning

The recommended objects sit in the Aaberge–Colombino / latent-jobs welfare
tradition (Aaberge–Colombino–Strøm 1999; Dagsvik–Jia 2016; Aaberge–Colombino
2018; Dagsvik et al. 2014; JJT 2026): money-metric objects from a job-choice
random-utility model, with the inclusive value and de Palma–Kilani CV machinery
as standard apparatus.

Where the JMP differs, enforced by this memo:

- **A characterised *family*, not one heuristic object.** The JMP computes
  $W^1$–$W^6$, each with axiomatic content (imported, cited, zero theory load),
  spanning the compensation–responsibility spectrum. JJT's CV$^{\text{circ}}$ is
  a single uncharacterised preference-neutralisation.
- **Sensitivity to the welfare measure is the *result*, not a footnote.** The
  menu is the JMP's empirical answer to whether the well-being-inequality picture
  is robust to the responsibility stance — a question JJT raise (their CV vs
  CV$^{\text{circ}}$ contrast) but answer at only two points and on a different
  axis.
- **Orthogonal axis to JJT.** JJT vary preferences; the JMP varies the
  opportunity (access/pay) treatment while respecting preferences. Different
  lane.
- **Heterogeneous, deterministic feasible sets are central;** opportunity
  heterogeneity leaves a measurable trace in the welfare *level*; no claim that
  opportunities are random.
- **Level decomposition, not reform-CV;** three-way Shapley surface, not a
  two-way contrast; couples as joint choice units; specification-agnostic
  throughout.

---

## 5. Robustness, scope, and the dominance extension

**The menu is the robustness — promoted to headline.** Reporting the family
$W^1$–$W^6$ *is* the answer to supporting question 4, replacing the v2
single-measure-plus-sensitivity design. Within that, the across-measure range
and the within-measure `[access-only, access+ability]` bracket compose into the
opportunity surface (V3-2).

**Deferred extension — stochastic dominance of choice sets.** Ranking feasible
sets by stochastic dominance would give *reference-free* statements about unequal
opportunity, robust to the choice of measure, reference, and cardinalisation —
the most ambitious possible answer to question 4. Anchors exist in the project
library (Bhattacharya 2015 on dominance/nonparametric welfare in discrete
choice; the opportunity-set-ranking tradition, Pattanaik–Xu). But it is a
**partial order** — many sets are incomparable — so it complements the cardinal
family and cannot replace it or yield a headline number alone. **Scope
decision:** treat full choice-set stochastic dominance as a deferred extension
(or a discussion-level "unambiguous-dominance cases" check); **do not open it
until the France family-comparison numbers exist**, consistent with the
baseline-first discipline. The six-measure menu already delivers most of the
robustness payoff at far lower cost.

---

## 6. Recommendation and next step

**Build-order gate (precedes D1 as the operative headline).** The family is the
intended design, but the claim "family comparison = the headline" is an
empirical bet that has not been placed: §1.3 establishes that *every* measure
reflects unequal access through attained utility $V_i$, so the six distributions
*could* come out similar, in which case the menu's message is "robust / the
stance does not move the picture much" — a legitimate finding, but not a
headline-grabbing one. The strength of the family-as-headline thesis equals the
empirical spread across measures, and that spread is unknown until computed.
Therefore, consistent with the project's baseline-first discipline, no claim that
"sensitivity to the welfare measure is the result" is made before the spread is
observed. Build order:

1. **Validate one focal measure end-to-end first: a Full Responsibility measure
   ($W^3$, laissez-faire).** Rationale: Full Responsibility pre-absorbs nothing,
   so the decomposition does *all* the attribution work — it is the cleanest
   stress-test of the welfare-plus-decomposition machinery, with no measure-side
   compensation masking a bug. (Validating first on $W^5$ would hide the access
   channel behind the measure's own access-compensation, the opposite of what a
   first stress-test wants.)
2. **Compute the access face ($W^5$) and the endpoints ($W^2$ as the second
   Full-Responsibility check; $W^4/W^6$ Full Compensation) to observe the
   spread.**
3. **Decide the headline empirically.** If the across-measure spread is
   material, the family comparison is the headline; if not, the family is
   reported as a robustness surface and the **committed focal pair** — the
   Full-Responsibility total ($W^3$) and the access-compensated dual ($W^5$) —
   carries the headline and supplies the abstract's number. This focal pair is
   promoted from the §1.4 narrative aside to a committed design element, so the
   abstract has a defined home regardless of the spread.

**Real validation gates (not interpretive identities).** The checks the scaffold
contract must enforce, and one tempting check it must *not* assert. **(a)** The
Shapley components must sum exactly to total inequality $I(\Omega^k)$ for each
measure — the order-independence/exhaustiveness gate. **(b) Welfare-integration
gate (three parts)** — replaces the single simulation-consistency check of v4.
*(i) Per-household stability:* $\widehat V_i^{\,\mathrm{IS}}$ and each
$\Omega_i^k$'s inequality must be stable as the draw count grows at the production
resolution; drift beyond a declared tolerance fails the gate. *(ii)
Effective-sample-size diagnostic:* report
$\mathrm{ESS}_i = \big(\sum_s \omega_{is}\big)^2 / \sum_s \omega_{is}^2$ and the
maximum normalised weight per household, where $\omega_{is}$ are the importance
weights; flag households with $\mathrm{ESS}_i$ below a declared threshold — the
exposure created by the **common** hours and employment channels — and on that
flagged subset only, compute $\widehat V_i^{\,\mathrm{dir}}$ and require agreement
within tolerance. Persistent disagreement on the flagged subset is the **sole**
trigger to escalate the redraw from cross-check to primary for those households;
aggregate draw-count stability does not by itself clear per-household weight
degeneracy. *(iii) Reference-coverage / EUROMOD gate:* no reference is evaluated
until every required household-specific disposable income $c_{ij}$ for the
reference packages of $\bar A, \mathcal J, o$ exists — present from the build or
supplied by a targeted EUROMOD evaluation at the build's 2016-real price basis and
EUROMOD system year. A wholesale EUROMOD rerun is forbidden (regression risk to
verified deflation consistency); silent interpolation of missing $c_{ij}$ is
forbidden; missing reference packages block computation rather than being
approximated. Because integration nodes are not redrawn under the primary scheme,
this gate touches reference packages only, not integration nodes. **Not a gate:**
the $W^1$/$W^5$ dual is a conceptual mapping of the access/ability cut onto the
menu, **not** a numerical identity — $W^1$ and $W^5$ are different money metrics
with different references, so their inequality gap is not the same quantity as any
single measure's Shapley access/ability components, and there is no theorem
equating them. Report the dual spread alongside the decomposition as
*corroborating interpretation*; do not write it in as a reconciliation gate.

- **Welfare object (D1):** the **family $W^1$–$W^6$**, computed on the ex-ante
  log-sum attained utility via the importance-sampling estimator
  $\widehat V_i^{\,\mathrm{IS}}$ over the existing draws (mandatory proposal
  correction; redraw $\widehat V_i^{\,\mathrm{dir}}$ as ESS-gated cross-check),
  with the three-part welfare-integration gate and the
  realised-bundle-vs-inclusive-value caveat stated. Report welfare distributions
  and inequality across the family, ordered Full Responsibility → one-sided →
  Full Compensation. Theory load on the
  JMP: **citations only.**
- **Decomposition (D2):** anchored on non-pre-absorbing measures — a Full
  Responsibility anchor ($W^3$, with $W^2$ as the second check) for total
  source-composition, and the one-sided duals $W^5$/$W^1$ for the access/ability
  dimensions — with the Full Compensation measures reported as the migrating end
  of the opportunity surface. Three-way {access, ability, preference},
  Shapley–Shorrocks; measure stance and decomposition channel reported jointly,
  never double-interpreted.
- **Secondary forms (D3):** ex-post chosen-alternative CE (correction-free
  cross-check); EV/CV (AC/JJT comparability).
- **Unit:** household-level for couples; intra-household equivalisation deferred.
- **Inference:** cluster-robust bootstrap on `idorighh`; per-measure,
  per-component CIs; opportunity-content CIs expected tighter than preference
  CIs; no asymptotic SEs for the headline; bootstrap cost scales with the menu
  size (compute-budget item).
- **Baseline-specific carries:** couples-male preference structurally
  pinned/near-zero with the data-fact caveat; the pinned-preference compression
  of the couples preference component requires couples and singles opportunity
  shares reported separately, never pooled (§3a); shared offer parameters with
  any gender split as robustness only, `beta_h_pt2` excluded from identified
  gendered estimates.
- **Scope:** the six-measure menu is the primary robustness; stochastic
  dominance deferred until the family-comparison numbers exist.

This memo settles the welfare object(s). It does **not** authorise welfare
scaffolding implementation or any welfare/decomposition computation; the next
artifact is `RURO_welfare_scaffold_design_contract_v2.md` (re-grounding the v1
contract on this memo's settled integration scheme), pointed at the certified
47-param pooled $\hat\theta$, with the active measure set read from configuration
and the following written in as required, pre-computation validation gates: the
build-order gate ($W^3$ validated first, then the spread); the
pinned-preference-under-preference-equalisation decision (held vs swapped) with
couples/singles opportunity shares reported separately; the Shapley
exhaustiveness gate (components sum to $I(\Omega^k)$); and the **three-part
welfare-integration gate** ($\widehat V_i^{\,\mathrm{IS}}$ stability; the
effective-sample-size diagnostic with $\widehat V_i^{\,\mathrm{dir}}$ cross-check
and escalation rule on the flagged subset; the reference-coverage / EUROMOD gate
narrowed to the $\bar A/\mathcal J/o$ reference packages). The $W^1$/$W^5$ dual is
reported as corroborating interpretation, not as a reconciliation gate.

**Save this as `JMP_welfare_spec_v5.md`** (design memo; methodology docs folder,
superseding `JMP_welfare_spec_v1.md`, `JMP_welfare_spec_v2.md`,
`JMP_welfare_spec_v3.md`, and `JMP_welfare_spec_v4.md`).
