# JMP Welfare Specification Memo v2

**Date:** 2026-06-01
**Document class:** prose design memo. Settles the money-metric welfare
object before any welfare implementation. Does **not** write welfare code,
compute welfare numbers, or compute decomposition numbers.
**Answers:** JMP supporting question 2 — how to compute money-metric
well-being when households face *different* feasible job sets.
**Certified baseline it is written against:** the 47-param pooled spec
`joint_pooled_v1_bll0_tlmpin` (`beta_ll=0`; `theta_l_m=-0.8` pinned;
`beta_E`, `beta_h_pt2` SHARED), identification-certified at the 901-alt
production resolution (synthetic Check-5 PD `min_eig=+1.706`; real-data
Hessian PD `min_eig=+0.459`, "SEPARATELY IDENTIFIED").

**Relationship to other documents.** This is the welfare-object layer of the
two v2 welfare memos
(`JMP_welfare_measurement_decisions_memo_v2.md`,
`JMP_welfare_scaffolding_design_memo_v2.md`), updated to the certified
baseline, and it supersedes `JMP_welfare_spec_v1.md`. It is the contract a
later `RURO_welfare_scaffold_design_contract_v1.md` translates into code.

---

## 0. What this memo carries forward and what it revises

The two v2 memos were written with single-year M1-clean as the operative
baseline and a pooled specification held as an SA2-gated contingency. The
certified baseline is now that pooled object. Because the v2 memos were built
specification-agnostic (decisions memo I1–I12; scaffolding memo C1–C6), the
switch is a configuration change at the input boundary, not a redesign.

**Carried forward unchanged from v1.** (i) The primary welfare object is a
household-level, money-metric, preference-respecting equivalent income
$\Omega_i$. (ii) EV/CV/Atkinson-equivalent are secondary objects via the
de Palma–Kilani log-sum-exp adjustment. (iii) The normative cut is three-way —
{preference, ability, access} — made order-independent by Shapley–Shorrocks,
reported as a **bracketed opportunity share `[access-only, access+ability]`**.
(iv) Gender attribution rules A1/A2/A3 are reported side by side. (v) Inference
is by bootstrap, cluster-robust on `idorighh`. (vi) Singles and couples are
reported separately; couples are the strongest welfare claim. (vii) The welfare
layer reads block membership and fixed parameters from the YAML. (viii) Three
findings from the certified fit bind the object and its inference (§3).

**New or revised in v2.**

- **(V2-1) The welfare object is grounded in a characterised measure.** The
  baseline object is the **reference-opportunity-set equivalent income**, which
  coincides with **Measure $W^5$** of the *companion theory paper*
  (Haydar–Maniquet, in progress). The JMP **imports** this measure as its
  welfare object and **carries zero theory load**: it restates no axioms,
  reproduces no proofs, lists no impossibility or characterisation theorems as
  JMP results. The characterisation is the companion paper's content, not the
  JMP's. The relationship is the one any applied paper has to the Atkinson or
  Gini index — one citation, then straight to estimation. (§1.3)
- **(V2-2) The reference is a reference opportunity *set*, not a single
  reference job.** v1 inverted attained utility at a fixed full-time reference
  job. v2 sharpens this to the $W^5$ form: the reference is a reference
  opportunity set $\bar A$, and equivalent income is the uniform pay shift to
  $\bar A$ that equates attained utility. The v1 "reference job" becomes the
  utility-maximising job *within* the (shifted) reference set, determined
  endogenously rather than fixed exogenously. (§1.2, §1.3)
- **(V2-3) The access/ability cut has an interpretive home.** The split is read
  through the companion paper's **Independence of $A$** (not responsible for
  *which* jobs you can take = access) vs **Independence of $\mathbf{y}$** (not
  responsible for *how much* jobs pay = the productivity/ability dimension).
  This language is used *lightly, as interpretation* of an empirical cut — not
  as theory exposition. (§2)
- **(V2-4) The "random opportunities" framing is removed.** Opportunities are
  treated **deterministically** — the frame of the companion theory paper,
  where the ability set $A$ is a deterministic subset of the job universe. The
  differentiation from Jacquet–Jia–Thoresen (JJT, 2026) is re-grounded on
  deterministic terms (§1.3, §4); there is no claim that opportunity randomness
  is welfare-relevant.
- **(V2-5) Robustness and scope are sharpened.** First-line robustness is
  *across characterised measures* ($W^5$ at alternative $\bar A$; $W^2$);
  full **stochastic dominance of choice sets** is a bounded, deferred extension,
  not the main object (§5).
- **(V2-6) Baseline membership update.** Occupation offers enter as six
  gender-specific params (`beta_occ_{2,3,4}_{m,f}`); year offer shifts
  (`beta_E_y2015`, `beta_E_y2017`) are inside the access block; the
  parameter-count anchor moves from 49 (in `JMP_ability_opportunity_cut_v1.md`)
  to the certified 47 (`beta_ll` removed, `theta_l_m` pinned). The
  {preference, ability, access} *mapping* is unchanged. (§2)

---

## 1. The welfare object

### 1.1 Candidates

Three money-metric objects are available from the certified RURO estimates.
All use $\beta_c=1$ as the consumption numeraire that fixes the utility scale;
none is *defined* by that normalisation — each requires an explicit income
inversion at a stated reference (§1.2).

**Candidate A — ex-ante expected-maximum utility (inclusive value / log-sum).**
By the Dagsvik / Aaberge–Colombino structure, the household's attained utility
is the expected maximum over its latent feasible job set, the log-sum over its
sampled alternatives:

$$
V_i \;=\; \log \sum_{j \in \mathcal{C}_i}
\exp\!\Big( v_i(c_j,\ell_j)\;+\;\log g(j;x_{\mathrm{opp},i})\;-\;\log \pi(j)\Big),
$$

where $v_i$ is systematic utility under household $i$'s own preferences,
$g(\cdot)=g_{\text{hours}}\cdot g_{\text{wage}}\cdot g_{\text{occ}}\cdot
g_{\text{market}}$ is the opportunity density, $\mathcal{C}_i$ is the sampled
feasible set, and $-\log\pi(j)$ is the **proposal/prior correction** — the
welfare analogue of the importance-sampling (sampling-of-alternatives)
correction in estimation, applied identically here or the opportunity term is
mis-weighted. With finite $\mathcal{C}_i$, $V_i$ carries simulation error
controlled by the number and spread of draws (Halton/Sobol reduce it for a
given count; cf. `JMP_couples_opportunity_draw_design_note_v1.md`).

- *Measures:* the welfare value of facing the whole feasible set ex ante.
- *Parameters:* full $\hat\theta$ — preference, wage/hours/occupation/market
  offer blocks, and the proposal correction.
- *Heterogeneous feasible sets:* handled natively — each $V_i$ is over the
  household's own $\mathcal{C}_i$ and $g(\cdot;x_{\mathrm{opp},i})$; a thin set
  lowers $V_i$ directly. This is the channel the JMP exists to measure.
- *Normative reading:* preference-respecting (own $v$), opportunity through own
  $g$.
- *Level:* household. *Decomposition suitability:* **high** — offer blocks
  enter $V_i$ explicitly and can be equalised. Inverted at a reference
  opportunity set, this is the recommended object (= $W^5$, §1.3).

**Candidate B — ex-post chosen-alternative certainty-equivalent.**
Evaluate utility at the realised chosen job $j^*(i)$: $u_i(c_{j^*},\ell_{j^*})$,
then invert at the reference.

- *Parameters:* preference block only (offer blocks drop once $j^*$ is
  conditioned on).
- *Heterogeneous feasible sets:* **largely invisible** — same realised job →
  same welfare regardless of feasible set, suppressing the access channel.
- *Decomposition suitability:* **low as primary**, **high as a robustness
  cross-check** — needs no proposal correction and no sampled-set expectation,
  so it isolates how much the headline depends on the log-sum approximation.

**Candidate C — equivalent income / EV–CV (the AC welfare tradition).**
Equivalent income is Candidate A inverted at a fixed reference (it *is* the
recommended object). EV/CV are *differences* between two states, computed by
the de Palma–Kilani adjustment — the standard object in Aaberge–Dagsvik–Strøm
(1995) and JJT (2026). Because the JMP decomposes a **level** of inequality,
the level (equivalent income) is primary; EV/CV are **secondary**, kept for
comparability with the AC/JJT literature.

### 1.2 Guardrails the object must satisfy

1. **`beta_c=1` does not define income welfare.** It fixes the utility scale
   and the consumption metric; the welfare object is the income inversion at a
   stated reference. The reference opportunity set $\bar A$ (§1.3), the
   within-set evaluation, and the reference preference are the normative inputs
   that make the inversion well-defined. They are declared, not implied.

2. **Sampling/proposal correction is mandatory in any log-sum object.** The
   $-\log\pi(j)$ term and the finite sampled-set approximation enter the
   welfare integral exactly as they enter the likelihood. State the draw count
   and scheme; report a simulation-consistency check (welfare quantities stable
   as draws grow). This is the binding subtlety for Candidate A and the reason
   Candidate B is retained as a correction-free cross-check.

3. **The chosen-alternative object sidesteps the expectation.** Candidate B
   needs neither the sampled-set expectation nor the proposal correction; it
   buys that simplicity by collapsing the feasible set to one point — narrow
   ex-post interpretation, structurally unable to carry the access component.
   It is a diagnostic, not the headline.

4. **Define the welfare unit explicitly; do not split couples.** Couples
   welfare is **household-level** money-metric welfare: one $\Omega_i$ per
   couple, from the couple's joint utility and joint budget. The joint problem
   is **not** treated as two independent individual objects. Within-couple
   gender enters through the attribution rules (§2), not by splitting
   $\Omega_i$. An intra-household equivalisation rule is a **deferred robustness
   layer**, not the baseline unit.

### 1.3 Grounding the object: the companion measure $W^5$, and relation to JJT

**The object is a characterised measure imported off the shelf.** The
recommended baseline object is the **reference-opportunity-set equivalent
income**, which coincides with **Measure $W^5$** of the companion theory paper
(Haydar–Maniquet, in progress). In that paper's notation, for a household with
attained bundle/utility under preferences $R$, $W^5$ is the uniform pay shift
$w$ to a fixed **reference ability set $\bar A$** that makes the household
indifferent between its attained situation and the best job it would take in
the shifted reference set:

$$
W^{5}\;:\quad \text{attained} \;\;I\;\; \max_R\big\{(c',j') : j'\in\bar A,\;
c'=\mathbf{y}(j')+w\big\}, \qquad \Omega_i \equiv w_i .
$$

The JMP's *reference opportunity set* is exactly this $\bar A$; the equivalent
income is $w_i$. **Empirical analogue:** the realised bundle is replaced by the
model-implied **attained utility** (the inclusive value $V_i$ of §1.1), and the
"best job in the shifted reference set" is itself an inclusive value over
$\bar A$. So $\Omega_i$ solves
$V_i^{\text{actual}} = \mathrm{IV}\big(\bar A;\ \text{pay}+\Omega_i,\ R_i\big)$.
This is the standard stochastic-choice analogue of $W^5$, and the gap between
the pointwise theory object and the expectation-based empirical object must be
**stated**, not hidden.

**Division of labour (this is a hard boundary).** The *characterisation* —
which axioms pin down $W^1,\dots,W^6$ — is the **companion theory paper's**
result, joint with Maniquet. The JMP is **solo** and carries **zero theory
load**: it cites the companion paper for the axiomatic foundation of $W^5$ and
proceeds directly to estimation, computation, and decomposition. The JMP's own
content is the structural estimation, the welfare computation on French data,
and the access/ability/preference Shapley decomposition — *not* the
characterisation. The Independence-of-$A$ / Independence-of-$\mathbf{y}$
vocabulary (below) is used only as interpretive intuition for the empirical
cut.

**Why $W^5$ and not $W^4$.** $W^4$ (the staying-home-equivalent measure)
satisfies **Full Compensation** = Independence of $A$ *and* Independence of
$\mathbf{y}$. It therefore neutralises **both** opportunity dimensions, leaving
**no opportunity component to decompose**. $W^5$ satisfies **Independence of
$A$** but **not Independence of $\mathbf{y}$**: it is anchored to a common
reference set (so it does not reward the idiosyncratic shape of one's own set),
yet pay/productivity differences still register. That is exactly the object the
access/ability decomposition requires.

**How access still bites under an "Independence-of-$A$" object.** $W^5$ being
independent of $A$ does **not** mean access drops out of the results. A
household with a constrained feasible set attains a worse bundle (lower $V_i$)
because it cannot reach better jobs, and that worse attained utility yields a
lower $\Omega_i$. Access enters through **choices/attainment**, not through $A$
entering the measure directly. This is the compensation logic operating
correctly, and it is the mechanism the access counterfactual (§2) exploits.

**Citability caveat and fallback.** The companion draft still marks $W^5$ and
some properties "to be proven." To cite $W^5$ as a *characterised* object, the
companion paper must be far enough along (working-paper/submission stage). If
it is not, the JMP still **uses the $W^5$ functional form** and describes it
directly as "the reference-opportunity-set equivalent-income measure," leaning
on the published equivalent-income tradition (Fleurbaey–Maniquet 2018;
Decancq–Fleurbaey–Schokkaert 2015) for foundation, with a forward reference to
the companion paper for the full axiomatics. Either way the JMP stands alone.

**Relation to JJT, re-grounded on deterministic terms.** JJT also treat
opportunities deterministically (their education-driven $\log Q$), so
"deterministic opportunities in a welfare measure" is *not* the differentiator.
The differentiation is the combination, and every piece is something JJT lack:
(i) an **axiomatically characterised** welfare object — JJT's CV$^{\text{circ}}$
is a heuristic preference-neutralisation with no characterisation; (ii) the
**access/ability split inside the opportunity side** (Ind-$A$ vs
Ind-$\mathbf{y}$) — JJT collapse all opportunity into one education-driven
scalar and cannot make this cut; (iii) a **level-inequality decomposition**,
not the CV of a single tax reform; (iv) a **three-way Shapley bracket**, not a
two-way CV-vs-CV$^{\text{circ}}$ contrast.

### 1.4 Recommendation

- **D1 — Baseline welfare object:** the **reference-opportunity-set equivalent
  income** $\Omega_i$ (= $W^5$), built on the ex-ante log-sum attained utility
  (Candidate A), with the mandatory proposal/prior correction, a
  simulation-consistency check, and the realised-bundle-vs-inclusive-value
  caveat stated.
- **D2 — Robustness alternatives:** (i) the **ex-post chosen-alternative
  certainty-equivalent** (Candidate B) as the proposal-correction-free
  cross-check; (ii) **EV/CV** (Candidate C as difference) for AC/JJT
  comparability; (iii) **across-measure robustness** — recompute the
  decomposition under $W^5$ at alternative $\bar A$ and under $W^2$
  (best-paid-equivalent), and show the opportunity share is stable (§5). All
  are configuration switches on one machine, not separate builds.

---

## 2. How the object feeds the decomposition

The decomposition follows `JMP_ability_opportunity_cut_v1.md`: the two
structural objects ($v$, $g$) map to three normative components by **cutting
$g$ in two**:

$$
\text{preference} = v;\qquad \text{ability} + \text{access} = g.
$$

**Block membership at the certified 47-param baseline.**

| Component | Parameters (47-param baseline) | Channel |
|---|---|---|
| **Preference** ($v$) | `beta_l0_{sm,sf,f}`, `beta_l_age{,2}_{sm,sf,m,f}`, `beta_l_nkids_{sf,f}`, `theta_l_{sm,sf,f}`, `theta_c_singles`; fixed `theta_l_m=-0.8`, `beta_ll=0`, `beta_c=1` | tastes over consumption, leisure, children-time |
| **Ability** (in $g$, wage tech.) | `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma`; `beta_w0` = common anchor | returns to own education/experience; residual productivity |
| **Access** (in $g$, rest) | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh`; `beta_E_gsur`, `beta_E_drgn2..8`, `beta_E_drgur`, `beta_E_drgmd`, `beta_E_y2015`, `beta_E_y2017`; `beta_occ_{2,3,4}_{m,f}` | hours/market/occupation/year offer availability |

**Interpretive basis for the cut (light use of the companion vocabulary).** The
ability/access boundary is the companion paper's Independence-of-$\mathbf{y}$ /
Independence-of-$A$ distinction: the wage technology is the pay dimension
($\mathbf{y}$), the offer blocks are the feasible-set dimension ($A$). The
companion paper establishes that these are two *independent* dimensions of the
compensation/responsibility trade-off; the JMP uses that only to justify why
the cut is principled, and does not reproduce the argument.

**What is held fixed to isolate each component** (welfare recomputed under each
equalisation; Shapley-averaged over the $3!=6$ orderings, so contributions sum
exactly to $I(\Omega)$):

- **Access:** set the access blocks (hours, market, occupation, year) to a
  common reference offer environment; hold ability and preference at actual
  values; recompute $\Omega$. The inequality fall is the access component =
  **lower bound** of the opportunity share. Mechanically, equalising access
  changes each household's attained utility $V_i$ (and hence $\Omega_i = W^5$)
  via the feasible set — the channel identified in §1.3.
- **Ability:** neutralise the wage technology's dependence on own
  education/experience and residual productivity (`beta_w0` stays as the common
  anchor); hold access and preference fixed; recompute $\Omega$. Access +
  ability = **upper bound** of the opportunity share; the gap between bounds is
  the education/ability normative disagreement, quantified. (The companion
  paper's Extension — abilities as $A(e,b)$ from effort $e$ and background $b$ —
  is the conceptual reason ability sits on the contested boundary and is
  reported as a bracket, not a point.)
- **Preference:** assign a common reference preference (the companion paper's
  horizontal reference $R^h$ is the natural choice, consistent with $W^5$'s
  Compensation-for-$R^h$ property) and revalue each feasible set with it. This
  changes the *yardstick*, not merely an input; report conditional on the
  reference and run a reference-preference sensitivity. The preference component
  is the **complement** of the opportunity bracket.

**Where the responsibility cut enters.** Baseline = weak-Dworkin (preferences
responsibility-relevant, access compensation-relevant, ability on the
boundary → bracket). Strong-Roemer (ability also compensation-relevant) = upper
bound. The bracket is the honest representation of where the disagreement lives.

**Specification/case agnosticism.** The welfare layer reads block membership,
fixed parameters (`theta_l_m`, `beta_ll`, `beta_c`), the reference set $\bar A$,
the cross-section filter (year), the reference preference, and the cluster unit
from YAML/config — no hardcoded France/2016/P3a constants except when
describing current evidence. Year offer shifts being inside access means the
opportunity-equalisation absorbs across-year offer variation into the
opportunity contribution rather than the preference residual.

---

## 3. Baseline-specific constraints from the actual estimate

Findings from the certified 47-param fit, not hypotheticals.

### 3a. Couples-male leisure is near-degenerate (`beta_l0_m` at floor)

`beta_l0_m = 1\mathrm{e}{-6}` (at floor); `theta_l_m` pinned at $-0.8$. The
couples-male leisure side of $v$ collapses toward a near-zero baseline, with
only small age shifters moving it. Reading: couples-male hours are concentrated
at full-time and the data do not identify a male-leisure margin for couples — a
data fact (near-universal male full-time participation), not a modelling
artifact, and the reason `theta_l_m` was pinned.

- **Does couples-male welfare collapse to consumption-only on the male-leisure
  side?** Effectively yes on that side; the couple's $\Omega$ is driven by
  consumption, male hours through the joint budget, and the strongly identified
  female leisure structure.
- **Household vs individual welfare.** Under the recommended **household-level**
  unit this is benign — a positive argument for that unit. Under an
  individual-level unit it would mean attributing a near-empty male preference
  per capita.
- **Reporting.** Report the couples-male preference contribution as
  near-zero/structurally pinned, with the explicit caveat that it reflects
  *unidentified* male-leisure variation among couples, not "men have no leisure
  preferences." `theta_l_m` and `beta_ll` are pinned → **zero uncertainty** by
  construction; the bootstrap holds them fixed. Flag this so the preference
  component's CI is not mis-read.

### 3b. SE asymmetry → component-uncertainty asymmetry

Certified-baseline median SEs by block (clustered on `idorighh`):

| Block | median SE (clustered) | role |
|---|---|---|
| wage_opp | 0.012 | ability |
| occupation_opp | 0.047 | access |
| market_hours_opp | 0.124 | access |
| couples_leisure | 0.394 | preference |
| singles_leisure | 0.387 | preference |

The opportunity blocks are an order of magnitude tighter than the leisure
blocks. **Therefore the opportunity component — the JMP's headline object — is
more precisely estimated than the preference component.** This is favourable:
the paper's main number (the opportunity share / bracket) is the
precisely-estimated part; the preference residual is the imprecise complement.

Inference treatment: **per-component bootstrap CIs**, cluster-robust on
`idorighh` (9,657 clusters; 2016–2017 repeat households resampled as units);
report a CI for each of access, ability, preference, and the opportunity
bracket; state explicitly that the opportunity-share CI is expected **tighter**
than the preference-share CI. **Asymptotic SEs are not used for the headline** —
three parameters sit at bounds (`beta_l0_m` lo, `beta_l_age2_sf` hi,
`beta_l_age2_f` hi), where asymptotic SEs are invalid; the bootstrap
re-estimation is the inference procedure.

### 3c. Shared `beta_E` / `beta_h_pt2` (gender split NOT certified)

The baseline uses **shared** hours-offer parameters. The LR pooling test
rejected sharing in-sample (`beta_E` LR$=65.7$; `beta_h_pt2` LR$=206.6$, male
$-1.19$/female $+0.37$, opposite signs), but the synthetic gate showed the
gender split is **not separately recoverable** at 901
(`RURO_gsplit_nonid_structure_v1.md`):

- `beta_h_pt2` split = **independent mislocation** — circular covariance, no
  combination rescues it; **no reparameterisation helps**. Pooled is the only
  honest baseline. Any `beta_h_pt2` gender difference is an **in-sample fit
  caveat**, never an identified gendered structural estimate, and must **not**
  enter the welfare object as a recovered gendered offer parameter.
- `beta_E` split = **partial ridge** — the gender *contrast* is modestly
  identified, the *level* flat; a level+deviation reparameterisation *might*
  recover the contrast if a later result demands it.

Welfare-spec consequences: **baseline welfare uses shared offer parameters**;
**"does gender-differentiating the offer move the opportunity share?" is a
planned robustness check only**; **a future `beta_E` robustness swap must be
possible without redesign** (the welfare layer reads offer-parameter names from
YAML, so a level+deviation `beta_E` re-gate is a config change); `beta_h_pt2`
is excluded from this path on identification grounds.

---

## 4. Literature positioning

The recommended object sits in the Aaberge–Colombino / latent-jobs welfare
tradition (Aaberge–Colombino–Strøm 1999; Dagsvik–Jia 2016; Aaberge–Colombino
2018; Dagsvik et al. 2014; JJT 2026): a money-metric object from a job-choice
random-utility model, with the inclusive value / log-sum and the de Palma–Kilani
CV machinery as the standard apparatus.

Where the JMP differs, and how this memo enforces the difference:

- **A characterised welfare object.** $\Omega_i = W^5$ is imported from the
  companion theory paper; its fairness content is pinned by axioms
  (Independence of $A$, Compensation for $R^h$, Responsibility for reference
  abilities). JJT's CV$^{\text{circ}}$ has no characterisation. The JMP carries
  no theory load — it cites and applies.
- **Heterogeneous feasible job sets are central, and deterministic.** $\Omega_i$
  is computed over each household's own constrained feasible set; opportunity
  heterogeneity leaves a measurable trace in the welfare *level*. There is no
  claim that opportunities are random.
- **The decomposition separates access, ability, and preference** — a three-way
  order-independent (Shapley–Shorrocks) split reported as a bracket, grounded
  interpretively in Ind-$A$/Ind-$\mathbf{y}$. JJT collapse opportunity into one
  scalar and run a two-way preference-neutralisation contrast.
- **Level-decomposition, not reform-CV.** The JMP decomposes a level of welfare
  inequality, not the CV of a single tax reform.
- **Couples are joint choice units** with household-level welfare; within-couple
  gender enters through the attribution rules.
- **Specification-agnostic by construction**, so the certified pooled baseline,
  a future `beta_E`-reparameterised robustness, alternative reference sets, and
  alternative cross-sections are configuration choices on one welfare layer.

---

## 5. Robustness across measures, and the stochastic-dominance extension

**First-line robustness — across characterised measures.** The companion
paper's family gives a *theory-native* sensitivity that directly answers
supporting question 4: recompute the decomposition under $W^5$ at several
reference sets $\bar A$ and under $W^2$ (best-paid-equivalent), and show the
opportunity share / bracket is stable across them. This is cheaper than, and
prior to, any dominance machinery, and it uses objects already in hand.

**Deferred extension — stochastic dominance of choice sets.** Ranking
households' feasible sets by stochastic dominance (e.g. FOSD over the induced
distribution of attainable money-metric values) would let the JMP make
*reference-free* statements about unequal opportunity, robust to the choice of
$\bar A$, reference preference, and cardinalisation. It is genuinely attractive
and has a ready anchor in the project library (Bhattacharya 2015 on
dominance/nonparametric welfare in discrete choice; the opportunity-set-ranking
tradition, Pattanaik–Xu). But it is a **partial order** — many pairs of sets
are incomparable — so it **complements** the cardinal $W^5$ decomposition and
cannot replace it or yield a headline number on its own. **Scope decision:**
treat full choice-set stochastic dominance as a deferred extension (or a
discussion-level "unambiguous-dominance cases" check); **do not open it until
the France $W^5$ decomposition number exists**, consistent with the
baseline-first discipline.

---

## 6. Recommendation and next step

- **Baseline welfare object (D1):** the reference-opportunity-set equivalent
  income $\Omega_i = W^5$, imported from the companion theory paper, built on
  the ex-ante log-sum attained utility, with the mandatory proposal correction,
  a simulation-consistency check, and the realised-bundle-vs-inclusive-value
  caveat stated. Theory load on the JMP: **one citation, nothing more**.
- **Robustness (D2):** chosen-alternative certainty-equivalent
  (correction-free cross-check); EV/CV (AC/JJT comparability); across-measure
  robustness ($W^5$ at alternative $\bar A$; $W^2$).
- **Unit:** household-level for couples; intra-household equivalisation
  deferred.
- **Decomposition:** three-way {access, ability, preference}, Shapley–Shorrocks,
  headline = bracketed opportunity share `[access-only, access+ability]`;
  ability/access read via Ind-$A$/Ind-$\mathbf{y}$; preference is the
  reference-conditional complement.
- **Inference:** cluster-robust bootstrap on `idorighh`, per-component CIs,
  opportunity-share CI expected tighter than preference-share CI; no asymptotic
  SEs for the headline.
- **Baseline-specific carries:** couples-male preference reported as
  structurally pinned/near-zero with the data-fact caveat; shared offer
  parameters with any gender split as robustness only, `beta_h_pt2` excluded
  from identified gendered estimates.
- **Scope:** across-measure robustness first; stochastic dominance deferred
  until the baseline $W^5$ number exists.

This memo settles the welfare object. It does **not** authorise welfare
scaffolding implementation or any welfare/decomposition computation; the next
artifact is `RURO_welfare_scaffold_design_contract_v1.md`, which translates
these decisions into a code contract for audit, pointed at the certified
47-param pooled $\hat\theta$.

**Save this as `JMP_welfare_spec_v2.md`** (design memo; methodology docs
folder, alongside the two v2 welfare memos and superseding
`JMP_welfare_spec_v1.md`).
