# JMP Welfare Specification Memo v1

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

**Supersedes nothing; revises selectively.** This memo is the welfare-object
layer of the two v2 memos, updated to the certified baseline. It is the
contract a later `RURO_welfare_scaffold_design_contract_v1.md` translates
into code.

---

## 0. What this memo carries forward and what it revises

The two v2 memos —
`JMP_welfare_measurement_decisions_memo_v2.md` (normative/measurement
decisions) and `JMP_welfare_scaffolding_design_memo_v2.md` (code-design
contract) — were written with single-year M1-clean as the operative baseline
and a pooled multi-year specification held as an SA2-gated contingency. The
certified baseline is now that pooled object. The crucial point is that the v2
memos were *deliberately built specification-agnostic* (decisions memo I1–I12;
scaffolding memo C1–C6), so the move to the pooled 47-param spec is a
configuration change at the input boundary, **not** a redesign.

**Carried forward unchanged.** (i) The primary welfare object is household
equivalent income $\Omega_i$, money-metric, preference-respecting at the
household level. (ii) EV/CV/Atkinson-equivalent are secondary objects via the
de Palma–Kilani log-sum-exp adjustment. (iii) The reference bundle
$(c^*,\ell^*)$ is the type-conditional median; the reference job is full-time
at the type/gender-conditional median full-time wage; the reference
opportunity set is the explicit, declared offer environment. (iv) The
normative cut is three-way — {preference, ability, access} — made
order-independent by Shapley–Shorrocks, with the headline reported as a
**bracketed opportunity share `[access-only, access+ability]`**. (v) Gender
attribution rules A1/A2/A3 are reported side by side. (vi) Inference is by
bootstrap, cluster-robust on `idorighh`. (vii) Singles and couples are
reported separately; couples are the strongest welfare claim. (viii) The
welfare layer reads block membership and fixed parameters from the YAML.

**Revised for the certified baseline.** (R1) The baseline parameter vector is
the pooled 47-param $\hat\theta$, not single-year M1-clean; the v2 "if
SA2-STANDS" pooled branch is now the operative branch. (R2) Year offer shifts
(`beta_E_y2015`, `beta_E_y2017`) are inside the **access** block and are
equalised in the opportunity counterfactual; the welfare distribution is
evaluated on a declared cross-section under the pooled $\hat\theta$ (default:
the 2016 sub-sample; pooled-sample and reweighted-2016 as sensitivities). (R3)
Occupation offers enter as **six gender-specific** params
(`beta_occ_{2,3,4}_{m,f}`), not the earlier four marital-status blocks. (R4)
Three structural facts from the certified fit now bind the welfare object and
its inference and are treated in §3: `beta_l0_m` at its floor; the
opportunity-vs-preference SE asymmetry; and the shared (not gender-split)
offer parameters. (R5) The parameter-count anchor in
`JMP_ability_opportunity_cut_v1.md` is 49; the certified baseline is 47
(`beta_ll` removed, `theta_l_m` pinned). The {preference, ability, access}
*mapping* is unchanged; only block membership updates (§2).

---

## 1. The welfare object

### 1.1 Candidates

Three money-metric objects are available from the certified RURO estimates.
All use $\beta_c=1$ as the consumption numeraire that fixes the utility scale;
none of them is *defined* by that normalisation — each requires an explicit
income inversion at a stated reference (§1.2).

**Candidate A — ex-ante expected-maximum utility (inclusive value / log-sum).**
By the Dagsvik / Aaberge–Colombino structure, the household's attained utility
is the expected maximum over its *latent feasible job set*, which under the
Gumbel architecture is the log-sum over the household's sampled alternatives:

$$
V_i \;=\; \log \sum_{j \in \mathcal{C}_i}
\exp\!\Big( v_i(c_j,\ell_j)\;+\;\log g(j;x_{\mathrm{opp},i})\;-\;\log \pi(j)\Big),
$$

where $v_i$ is systematic utility under household $i$'s own preferences,
$g(\cdot)=g_{\text{hours}}\cdot g_{\text{wage}}\cdot g_{\text{occ}}\cdot
g_{\text{market}}$ is the opportunity density, $\mathcal{C}_i$ is the sampled
feasible set, and $-\log\pi(j)$ is the **proposal/prior correction**: the log
of the sampling protocol's inclusion density, subtracted so the finite-sample
log-sum is a consistent estimate of the true inclusive value. This is the
*welfare analogue of the importance-sampling (sampling-of-alternatives)
correction in estimation* — it is the same additive log-correction the
likelihood already carries, and it must be applied identically in the welfare
integral or the opportunity term is mis-weighted. With a finite $\mathcal{C}_i$,
$V_i$ carries simulation error controlled by the number and spread of draws;
quasi-random (Halton/Sobol) draws reduce it for a given count (cf.
`JMP_couples_opportunity_draw_design_note_v1.md`).

- *Measures:* the welfare value of facing the whole feasible set ex ante,
  before the taste shock is realised.
- *Parameters:* the full $\hat\theta$ — preference block $v$, wage/hours/
  occupation/market offer blocks $g$, and the proposal correction.
- *Heterogeneous feasible sets:* handled natively — each household's $V_i$ is
  taken over *its own* $\mathcal{C}_i$ and $g(\cdot;x_{\mathrm{opp},i})$, so a
  thin or restricted feasible set lowers $V_i$ directly. This is the channel
  the JMP exists to measure.
- *Normative reading:* preference-respecting (own $v$), with opportunity
  entering through the household's own $g$.
- *Level:* household.
- *Decomposition suitability:* **high** — the opportunity blocks enter $V_i$
  explicitly and can be counterfactually equalised.

**Candidate B — ex-post chosen-alternative certainty-equivalent.**
Evaluate utility at the *realised* chosen job $j^*(i)$:
$u_i\big(c_{j^*},\ell_{j^*}\big)$, then invert to income at the reference.

- *Measures:* the welfare value of the job actually taken.
- *Parameters:* preference block $v$ only (the offer blocks do not enter once
  $j^*$ is conditioned on).
- *Heterogeneous feasible sets:* **largely invisible** — two households with
  the same realised job but different feasible sets receive the same welfare,
  which suppresses exactly the opportunity channel.
- *Normative reading:* ex-post, conditional on the realised draw; closest to
  an observed-choice valuation.
- *Level:* household.
- *Decomposition suitability:* **low as primary** (it cannot carry the access
  component), **high as a robustness cross-check** — because it conditions on
  the observed $j^*$ it needs *no proposal correction and no sampled-set
  expectation*, so it isolates how much of the headline depends on the
  log-sum approximation.

**Candidate C — equivalent income / EV–CV (the AC welfare tradition).**
Equivalent income is Candidate A inverted at a fixed reference (it *is* the
recommended object below). EV/CV are *differences* between two states,
computed by the de Palma–Kilani log-sum-exp adjustment — the standard object
in Aaberge–Dagsvik–Strøm (1995) and Jacquet–Jia–Thoresen (2026).

- *Measures (EV/CV):* the income transfer equating welfare across two
  environments.
- *Parameters:* full $\hat\theta$, plus the two environments' offer/budget
  specifications.
- *Heterogeneous feasible sets:* handled, but as a *difference*, not a level.
- *Normative reading:* compensation for a change of state.
- *Level:* household.
- *Decomposition suitability:* the JMP decomposes a **level** of inequality,
  so the level (equivalent income) is primary; EV/CV are kept **secondary**
  for comparability with the AC/JJT literature and for any
  counterfactual-gain translation.

### 1.2 Guardrails the object must satisfy

1. **`beta_c=1` does not define income welfare.** It fixes the utility scale
   and the consumption metric; it does not by itself produce a money number.
   The welfare object is the income inversion
   $\Omega_i = y^\star$ solving
   $\;u_i\big(c(y^\star,\text{ref job}),\,\ell^*\big)\big|_{\text{ref opp set}}
   = V_i^{\text{actual}}$, where the reference bundle $(c^*,\ell^*)$, the
   reference job, and the reference opportunity set are the *normative inputs
   that make the inversion well-defined*. They must be declared, not implied.

2. **Sampling/proposal correction is mandatory in any log-sum object.** The
   $-\log\pi(j)$ term and the finite sampled-set approximation must enter the
   welfare integral exactly as they enter the likelihood. State the draw count
   and the draw scheme; report a simulation-consistency check (welfare
   quantities stable as draws grow). This is the binding subtlety for
   Candidate A and the reason Candidate B is retained as a correction-free
   cross-check.

3. **The chosen-alternative object sidesteps the expectation.** Candidate B
   needs neither the sampled-set expectation nor the proposal correction. That
   simplicity is real, but it buys it by collapsing the feasible set to one
   point — narrow ex-post interpretation, and structurally unable to carry the
   access component. Weigh accordingly: B is a diagnostic, not the headline.

4. **Define the welfare unit explicitly; do not split couples.** Couples
   welfare is **household-level** money-metric welfare: one $\Omega_i$ per
   couple, built from the couple's joint utility and joint budget. The joint
   household problem is **not** treated as two independent individual welfare
   objects. Within-couple gender questions are handled by the attribution
   rules (§2, A1/A2/A3) acting on *components*, not by splitting $\Omega_i$. An
   intra-household allocation / equivalisation rule (per-adult-equivalised
   welfare) is a **deferred robustness layer**, not the baseline unit.

### 1.3 Recommendation

- **D1 — Baseline welfare object:** household equivalent income $\Omega_i$
  built on the **ex-ante log-sum attained utility** (Candidate A inverted at
  the reference, = Candidate C-as-equivalent-income). This is exactly the v2
  object, carried forward, and it is the only candidate that carries the
  opportunity channel into the level.
- **D2 — Robustness alternatives:** (i) the **ex-post chosen-alternative
  certainty-equivalent** (Candidate B) as the proposal-correction-free
  cross-check on the log-sum approximation; (ii) **EV/CV** (Candidate C as
  difference) for AC/JJT comparability. Both are configuration switches on the
  same machinery, not separate builds.

---

## 2. How the object feeds the decomposition

The decomposition follows `JMP_ability_opportunity_cut_v1.md`: the two
structural objects ($v$, $g$) map to three normative components by **cutting
$g$ in two**.

$$
\text{preference} = v;\qquad \text{ability} + \text{access} = g.
$$

**Block membership at the certified 47-param baseline.**

| Component | Parameters (47-param baseline) | Channel |
|---|---|---|
| **Preference** ($v$) | `beta_l0_{sm,sf,f}`, `beta_l_age{,2}_{sm,sf,m,f}`, `beta_l_nkids_{sf,f}`, `theta_l_{sm,sf,f}`, `theta_c_singles`; fixed structure `theta_l_m=-0.8`, `beta_ll=0`, `beta_c=1` | tastes over consumption, leisure, children-time |
| **Ability** (in $g$, wage tech.) | `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma`; `beta_w0` = common anchor | returns to own education/experience; residual productivity |
| **Access** (in $g$, rest) | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh`; `beta_E_gsur`, `beta_E_drgn2..8`, `beta_E_drgur`, `beta_E_drgmd`, `beta_E_y2015`, `beta_E_y2017`; `beta_occ_{2,3,4}_{m,f}` | hours/market/occupation/year offer availability |

**What is held fixed to isolate each component** (welfare recomputed under
each equalisation; Shapley-averaged over the $3!=6$ orderings so the three
contributions sum exactly to $I(\Omega)$):

- **Access:** set the access blocks (hours, market, occupation, year) to a
  common reference offer environment; hold ability and preference at actual
  values; recompute $\Omega$. The inequality fall is the access component =
  **lower bound** of the opportunity share.
- **Ability:** neutralise the wage technology's dependence on own
  education/experience and residual productivity (`beta_w0` stays as the
  common anchor); hold access and preference fixed; recompute $\Omega$. Access
  + ability = **upper bound** of the opportunity share; the gap between the
  bounds is the education/ability normative disagreement, quantified.
- **Preference:** assign a common reference preference $\bar v$ and revalue
  each feasible set with it. This changes the *yardstick*, not merely an
  input — it must be flagged as the hardest counterfactual and reported
  conditional on the reference type, with a reference-preference sensitivity.
  The preference component is the **complement** of the opportunity bracket.

**Where the responsibility cut enters.** The baseline is weak-Dworkin:
preferences responsibility-relevant, access compensation-relevant, ability on
the contested boundary — hence the bracket. The strong-Roemer alternative
(ability also compensation-relevant) is the upper bound. The bracket *is* the
honest representation of where the disagreement lives; the JMP reports it
rather than picking a point.

**Specification/case agnosticism.** The welfare layer reads block membership,
fixed parameters (`theta_l_m`, `beta_ll`, `beta_c`), the cross-section filter
(year), reference choices, and the cluster unit from the YAML/config — no
hardcoded France/2016/P3a constants except when describing current evidence.
Year offer shifts being inside access means the opportunity-equalisation
absorbs across-year offer variation into the opportunity contribution rather
than the preference residual; this is the pooled-baseline treatment the v2
design anticipated.

---

## 3. Baseline-specific constraints from the actual estimate

These are findings from the certified 47-param fit, not hypotheticals.

### 3a. Couples-male leisure is near-degenerate (`beta_l0_m` at floor)

`beta_l0_m = 1\mathrm{e}{-6}` (at floor); `theta_l_m` pinned at $-0.8$. The
couples-male leisure side of $v$ collapses toward a near-zero baseline, with
only the small age shifters (`beta_l_age_m`$=-0.067$, `beta_l_age2_m`$=+0.088$)
moving it. Reading: couples-male hours are concentrated at full-time and the
data do not identify a male-leisure margin for couples — this is a data fact
(near-universal male full-time participation), not a modelling artifact, and
it is exactly why `theta_l_m` was pinned.

- **Does couples-male welfare collapse to consumption-only on the male-leisure
  side?** Effectively yes, on that side: the male-leisure term contributes
  almost nothing to the couple's $v$. The couple's $\Omega$ is then driven by
  consumption, the male hours through the joint budget, and the (strongly
  identified) female leisure structure (`beta_l0_f`$\approx 10.05$,
  `theta_l_f`$\approx -2.13$).
- **Household vs individual welfare.** Under the recommended **household-level**
  unit this is benign — the couple's welfare is well-defined and the male-leisure
  degeneracy is absorbed into a joint object. Under an individual-level unit it
  would be a defect (a near-empty male preference attributed per-capita). This
  is a positive argument for the household-level unit (D1, guardrail 4).
- **Reporting.** Report the couples-male preference contribution as
  near-zero/structurally pinned, with the explicit caveat that it reflects
  unidentified male-leisure variation among couples, **not** "men have no
  leisure preferences." `theta_l_m` and `beta_ll` are pinned, so they
  contribute **zero uncertainty** by construction; the bootstrap holds them
  fixed. Flag this so the preference component's CI is not mis-read as
  certainty about the male-leisure margin.

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
(preference) blocks. **Therefore the opportunity component of welfare
inequality — the JMP's headline object — is more precisely estimated than the
preference component.** This is favourable: the paper's main number (the
opportunity share) is the precisely-estimated part; the preference residual is
the imprecise complement.

Inference treatment:

- **Per-component bootstrap CIs**, cluster-robust on `idorighh` (9,657
  clusters; the 2016–2017 repeat households resampled as units). Report a CI
  for each of access, ability, preference, and for the opportunity bracket.
- **Component-specific uncertainty**, reported explicitly: state that the
  opportunity-share CI is expected to be **tighter** than the preference-share
  CI, and show both.
- **Asymptotic SEs are not used for the headline.** Three parameters sit at
  bounds (`beta_l0_m` lo, `beta_l_age2_sf` hi, `beta_l_age2_f` hi); asymptotic
  SEs are invalid at boundaries. The bootstrap re-estimation is the inference
  procedure (carried forward from decisions memo §21 / N10).

### 3c. Shared `beta_E` / `beta_h_pt2` (gender split NOT certified)

The baseline uses **shared** hours-offer parameters. The LR pooling test
rejected sharing in-sample (`beta_E` LR$=65.7$; `beta_h_pt2` LR$=206.6$,
male $-1.19$/female $+0.37$, opposite signs), but the synthetic gate showed the
gender split is **not separately recoverable** at 901
(`RURO_gsplit_nonid_structure_v1.md`):

- `beta_h_pt2` split = **independent mislocation** — circular covariance
  ellipse, no linear combination rescues it; **no reparameterisation helps**.
  Pooled is the only honest baseline. Any `beta_h_pt2` gender difference must
  be reported as an **in-sample fit caveat**, never as an identified gendered
  structural estimate, and must **not** enter the welfare object as a
  recovered gendered offer parameter.
- `beta_E` split = **partial ridge** — the gender *contrast* is modestly
  identified, the *level* is flat; a level+deviation reparameterisation
  *might* recover the contrast if a later result demands it.

Welfare-spec consequences:

- **Baseline welfare uses shared offer parameters** (`beta_E`, `beta_h_pt2`
  pooled). This is the access block as certified.
- **"Does gender-differentiating the offer move the opportunity share?" is a
  planned robustness check only**, not part of the baseline.
- **A future `beta_E` robustness swap must be possible without redesign.**
  Because the welfare layer reads offer-parameter names from the YAML
  (spec-agnostic input boundary), swapping in a level+deviation
  `beta_E` parameterisation and re-gating its contrast requires only a config
  change. `beta_h_pt2` is excluded from this path on identification grounds.

---

## 4. Literature positioning

The recommended object sits squarely in the Aaberge–Colombino / latent-jobs
welfare tradition (Aaberge–Colombino–Strøm 1999; Dagsvik–Jia 2016;
Aaberge–Colombino 2018; Dagsvik et al. 2014; Jacquet–Jia–Thoresen 2026): a
money-metric welfare object derived from a job-choice random-utility model,
with the inclusive value / log-sum and the de Palma–Kilani CV machinery as the
standard apparatus.

Where the JMP differs, and where this memo enforces the difference:

- **Heterogeneous feasible job sets are central.** $\Omega_i$ is computed over
  *each household's own* constrained feasible set $\mathcal{C}_i$ and offer
  density $g(\cdot;x_{\mathrm{opp},i})$ — not over a common deterministic
  hours menu. Opportunity heterogeneity leaves a measurable trace in the
  welfare *level*, which is the object the decomposition acts on.
- **The decomposition separates access, ability, and preference** — a
  three-way order-independent (Shapley–Shorrocks) split reported as a bracket,
  not a two-way preference-neutralisation contrast (the JJT CV vs CV$^{\text{circ}}$
  comparison). The JMP decomposes a **level of inequality**, not the CV of a
  single reform.
- **Couples are joint choice units** with household-level money-metric
  welfare; within-couple gender enters through the attribution rules, not by
  splitting the welfare object.
- **The object is specification-agnostic by construction**, so the certified
  pooled baseline, a future `beta_E`-reparameterised robustness, or a
  single-year cross-section are all configuration choices on one welfare
  layer.

---

## 5. Recommendation and next step

- **Baseline welfare object (D1):** household equivalent income $\Omega_i$ on
  the ex-ante log-sum attained utility, inverted at the declared reference
  bundle / reference job / reference opportunity set, with the mandatory
  proposal/prior correction and a simulation-consistency check.
- **Robustness (D2):** ex-post chosen-alternative certainty-equivalent
  (correction-free cross-check) and EV/CV (AC/JJT comparability).
- **Unit:** household-level for couples; intra-household equivalisation
  deferred.
- **Decomposition:** three-way {access, ability, preference}, Shapley–Shorrocks,
  headline = bracketed opportunity share `[access-only, access+ability]`;
  preference is the reference-conditional complement.
- **Inference:** cluster-robust bootstrap on `idorighh`, per-component CIs,
  opportunity-share CI expected tighter than preference-share CI; no
  asymptotic SEs for the headline.
- **Baseline-specific carries:** report couples-male preference as
  structurally pinned/near-zero with the data-fact caveat; use shared offer
  parameters and treat any gender split as robustness only, with `beta_h_pt2`
  excluded from identified gendered estimates.

This memo settles the welfare object. It does **not** authorise welfare
scaffolding implementation or any welfare/decomposition computation; the next
artifact is `RURO_welfare_scaffold_design_contract_v1.md`, which translates
these decisions into a code contract for audit.

**Save this as `JMP_welfare_spec_v1.md`** (design memo; methodology docs
folder, alongside the two v2 welfare memos it carries forward).
