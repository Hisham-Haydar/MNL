# JMP — Ability vs Opportunity Framework v1

Date: 2026-05-14

Scope: foundational conceptual document. Locks the JMP's three-way
decomposition framework (opportunity / ability / preferences), the
parametric mapping into the RURO model, the spec changes required from
M0c_b/M0c_b2 to support the framework, the treatment of gender, the
counterfactual decomposition design, the reference-point choice, and
the implied commitments for downstream welfare scaffolding and code
design. This memo supersedes the conceptual content of earlier design
memos and is the reference for all subsequent welfare/decomposition
code.

Inputs to this memo:
- The verdict and design memos from M0a-clean through M0c_b2
- `Aaberge_Colombino_Strom_1999.md`, `Capeau_et_al_2015.md` (the
  RURO literature framing)
- `Bossert_Ferreira_Menendez_2007.md`, `Ferreira_Gignoux_2011.md`
  (parametric decomposition methods)
- `Shorrocks_2013.md` (Shapley-based decomposition)
- The François Maniquet theory paper (treated as the normative
  scaffolding reference; not implemented as theory in this empirical
  paper)

---

## 1. The two-tier vs pure-opportunity attribution choice

Most of the labour-supply literature decomposes welfare inequality
into two compartments: preferences (responsibility-relevant) and
opportunities (compensation-relevant). This is the framing in Capéau
et al. (2015/16) and Aaberge-Colombino-Strøm (1999). Under that
framing, every covariate that enters `q` or `g_1` or `g_2` is
"opportunity," and only the utility function's shape and stochastic
preference component count as preferences.

This conflates two distinct economic objects:

(i) **Genuine opportunity differences** — variation in the *rate* at
which jobs arrive or the *availability* of specific (w, h, occ)
combinations, driven by factors outside the individual's control
(location, regional demand, possibly discrimination).

(ii) **Ability-mediated differences** — variation in the *content* of
job offers (mainly the wage offered) driven by individual-level
productivity-correlated characteristics (education, accumulated
experience, possibly cognitive skills).

Under the two-tier framing both are "opportunity." Under this JMP's
three-way framing they are separate, and the distinction matters for
the normative reading. Specifically:

- **Opportunity differences** are unambiguously compensation-relevant
  under the responsibility-sensitive position (Fleurbaey, Bossert,
  Maniquet, Roemer): individuals should not be held responsible for
  the labour market they happen to face.

- **Ability differences** are contested. Under the strong Roemer
  position, ability is itself shaped by family background and
  childhood-stage opportunity, so ability differences are also
  compensation-relevant. Under a weaker Dworkinian position, "ability
  exercised through productive activity" is part of the self the
  person is rightly held to be. The JMP takes the weaker position
  empirically (ability differences are not in the opportunity
  compartment) but reports the alternative under the strong position
  as a robustness exercise (§8).

- **Preference differences** are responsibility-relevant under any
  liberal position. They remain in the preference compartment.

The JMP's contribution is to make the (i)/(ii) split explicit and
quantitatively measurable, while existing structural-RURO papers
conflate them.

---

## 2. Parametric mapping: ability vs opportunity covariates

The RURO model has four structural blocks. Each block's covariates
get assigned to opportunity, ability, or preferences:

| Block | Mathematical object | Covariate | Assignment |
|---|---|---|---|
| Utility | `BC(C, θ_c)` | curvature | preferences |
| Utility | `BC(L_g, θ_l_g)` | curvature | preferences |
| Utility | `β_l_age`, `β_l_age²` | age in leisure | preferences |
| Utility | `β_l_nkids` | children in leisure | preferences |
| Utility | `β_ll` | leisure-leisure interaction | preferences |
| Utility | random Fréchet error | preference taste | preferences |
| `g_1(w; x_w)` Mincer mean | `β_w_educL`, `β_w_educH` | education | **ability** |
| `g_1(w; x_w)` Mincer mean | `β_w_pexp`, `β_w_pexp²` | potential experience | **ability** |
| `g_1(w; x_w)` Mincer mean | gender-on-wage | gender | ability (G1 reading) or both (G4 reading) |
| `g_1(w; x_w)` variance | `σ` | wage-offer dispersion | shared (technically opportunity if regional, but currently not regional) |
| `q(x_opp)` | `β_E_gsur` | regional unemployment | **opportunity** |
| `q(x_opp)` | gender-on-arrival | gender | opportunity (G2 reading) or both (G4 reading) |
| `q(x_opp)` | NUTS-1 region (M1 addition) | location | **opportunity** |
| `q(x_opp)` | `β_E_educH` (current spec) | education | **REMOVE under (b)** — currently violates clean split |
| `g_2(h)` | `β_h_pt1`, `β_h_pt2`, `β_h_ft` | gender-specific hours focal points | opportunity (institutional features of the labour market) |
| `O^Occ` | `β_occ_k_g` | task-content × group | opportunity (occupation availability conditional on offer) |
| Proposal correction | `−log_prior` | sampler implementation | not in opportunity or ability — purely a likelihood-correction artifact |

This assignment is the operational commitment of (b). Four covariates
that the original spec placed in opportunity move out: nothing moves
into opportunity in this memo (region will be added at M1 separately).

**The single required spec change**: `β_E_educH` must come out of the
employment-arrival rate `q(x_opp)`. Education's effect on employment
runs through wages: educated workers face higher-mean wage offers
(`β_w_educH = 0.30`), which makes more jobs in their choice set
acceptable, which produces endogenously higher participation. There
is no direct labour-demand-side education preference in the
specification beyond this.

This is a substantive empirical restriction. Capéau et al. *include*
education in `q`. Your spec follows them at M0c_b. The (b)
commitment requires breaking with their convention here. Section 3
specifies the implementation.

---

## 3. Required spec changes to clean the opportunity layer

The M1 step in the v4 contract roadmap was originally specified as
"add region dummies to `O^E + O^H`." Under (b), M1 expands to a
two-part change:

**M1-clean** (replacing the original M1):

(a) **Remove** `β_E_educH` from `market_opportunity.shifters`.
(b) **Add** three NUTS-1 region dummies (`region_north`,
    `region_south`, `region_idf` with one reference category) as
    interactions with `working` under `market_opportunity.shifters`.
(c) **Keep** `β_E_gsur` (regional unemployment rate) as is — it is
    already a clean opportunity covariate.
(d) **Keep** `β_E` (employment intercept) and the focal-point
    parameters (`β_h_pt1`, `β_h_pt2`, `β_h_ft`) as is.

Net parameter change: −1 (drop `β_E_educH`) + 3 (region dummies) =
+2 in `O^E`. M0c_b2 has 47 params; M1-clean has 49.

The wage block is unchanged: `β_w_educH` stays in `g_1` (where
education-as-ability lives). The occupation block is unchanged.
Utility is unchanged.

**M1-clean estimation order**:

1. Estimate M1-clean from spec defaults with multi-start (3 starts).
2. If Gate B passes: M1-clean becomes the main JMP baseline.
3. If Gate B fails on identification grounds (e.g., region dummies
   collinear with `β_E_gsur`): drop one region dummy or pool region
   into a coarser two-level partition (e.g., Paris vs rest of France).
4. **Sensitivity run M1-naive** (additionally): keep `β_E_educH` in
   `q` and re-estimate. This is the spec that would be obtained if
   the JMP followed the Capéau-style convention. Report the
   opportunity-attributed inequality from both M1-clean and M1-naive
   in the paper. The gap between them is the "ability-mediated
   opportunity" — the inequality that earlier literature attributes
   to opportunity but actually runs through productivity-correlated
   characteristics.

---

## 4. Treatment of gender (G4)

Gender does not fit cleanly into either compartment. The empirically
plausible position is that some of the gender wage gap is
productivity-related (occupation choice, hours pattern, accumulated
experience differences) and some is discrimination (employer
preferences over identical workers). The structural model does not
identify these separately. The JMP commits to G4: estimate gender
effects in both `q` and `g_1` (where the data place them), and report
the decomposition under multiple attribution rules in the paper.

**Three attribution rules to report**:

| Rule | Gender effects in `q` and `g_1` count as | Most common reader interpretation |
|---|---|---|
| **A1 — gender as ability** | both treated as ability-mediated | productivity gap; small opportunity component |
| **A2 — gender as opportunity** | both treated as opportunity | discrimination gap; large opportunity component |
| **A3 — split (literature-anchored)** | gender-on-wage counts as ability (40% of gap); gender-on-arrival counts as opportunity (60%) | reflects Blinder-Oaxaca decomposition norms; this is the central JMP report |

The 40/60 split in A3 is a literature anchor based on Blau-Kahn
(2017) and related decompositions of the French gender wage gap. The
paper reports A1 and A2 as upper and lower bounds and A3 as the main
result. The reader can choose their normative position; the JMP
reports the empirical magnitudes.

This is methodologically conservative: the JMP does not force a
normative position on gender, but it does force the reader to be
explicit about what their position implies for the magnitudes.

**Estimation implication**: nothing changes. The model is estimated
once. The decomposition code reads off the gender coefficients and
applies the three attribution rules to the same θ̂.

---

## 5. Counterfactual decomposition design

The decomposition is **counterfactual**, not variance-of-shifters.
The structural model lets us compute, for each household i, a
welfare measure `Ω_i` as a function of θ̂, the household's
opportunity covariates `x_opp^i`, ability covariates `x_w^i`, and
preference shifters (which enter U).

For each household, we compute four versions of `Ω`:

| Version | x_opp | x_w | Preferences (U shape) | Interpretation |
|---|---|---|---|---|
| `Ω_i^actual` | observed | observed | observed | actual welfare |
| `Ω_i^opp_eq` | reference | observed | observed | opportunity-equalised |
| `Ω_i^abil_eq` | observed | reference | observed | ability-equalised |
| `Ω_i^both_eq` | reference | reference | observed | both equalised; only preference variation remains |

These four versions span the variance space. The natural
decomposition is:

**Total welfare inequality**: I(Ω_i^actual) — some inequality index
on the actual welfare distribution.

**Opportunity contribution**: I(Ω_i^actual) − I(Ω_i^opp_eq) — how
much inequality disappears when opportunities are equalised, holding
ability and preferences at their observed values.

**Ability contribution**: I(Ω_i^actual) − I(Ω_i^abil_eq) — how much
inequality disappears when ability is equalised, holding opportunity
and preferences at their observed values.

**Preference contribution**: I(Ω_i^both_eq) — the residual
inequality after both opportunity and ability are equalised.

**Interaction term**: opportunity + ability + preference need not sum
to total. The residual is the opportunity-ability interaction (e.g.,
educated workers also tend to live in metropolitan areas, so
equalising both at once removes more inequality than the sum of
equalising each separately). The JMP reports this interaction
explicitly rather than allocating it.

**Shapley alternative**: a Shapley decomposition (Shorrocks 2013)
allocates the interaction term proportionally across the three
factors, removing path-dependence. The JMP reports both the
ordered-removal decomposition and the Shapley decomposition for
robustness. The Shapley method is the conceptually cleaner choice
but the ordered-removal is more transparent to readers.

**Welfare measure choice**: money-metric `Ω` is the standard. Two
specific candidates:

(i) **Equivalent variation (EV)**: the lump-sum income transfer that
    would make the household indifferent between their actual
    situation and a reference utility level (typically the
    population-median utility). This is the JMP's main measure.

(ii) **Compensating variation (CV)**: the lump-sum income transfer
    that would compensate the household for moving from their actual
    situation to a counterfactual. Reported as a robustness exercise.

For CV and EV in a discrete-choice model, the standard formula is
the log-sum-exp adjustment (de Palma–Kilani). The welfare scaffolding
code implements this.

---

## 6. Reference-point choice for the counterfactual

The reference values for `x_opp` and `x_w` are themselves normative
choices. The JMP commits to **population median by gender and
household type** as the primary reference:

- `x_opp` reference: median `gsur`, median region (typically the
  modal region), median NUTS-1 dummies (zero for non-modal regions)
- `x_w` reference: median education, median potential experience,
  reference gender (the JMP uses female as reference under G4 A3 —
  computing male welfare *as if* he had female-typical ability
  characteristics is the more interesting counterfactual)

**Why median rather than mean**: median is robust to outliers and
doesn't depend on the (skewed) distribution of education or
experience. Means inflate the reference toward the top of the
distribution; medians stay representative.

**Sensitivity references for the robustness section**:

(i) **Mean** instead of median.
(ii) **"Best available"**: the 10th-percentile `gsur` (i.e., the
     lowest-unemployment region), the 90th-percentile education
     (i.e., highly educated). This is the "equality up to the
     best" reference and produces an upper bound on what opportunity
     equalisation could achieve.
(iii) **By gender separately**: report decomposition for males using
      male-median reference, and for females using female-median
      reference, then aggregate. This is the "within-group"
      decomposition and is informative for understanding gender
      decomposition.

The François Maniquet theory paper has a view on the right reference
choice that's worth consulting before final paper writing. The
median-by-gender-and-household-type default is robust enough for the
main result but should be cross-checked with him.

---

## 7. What the decomposition can and cannot say

**Can**:

(a) Quantify how much money-metric well-being inequality is
    mechanically attributable to differing opportunity sets, differing
    ability characteristics, and differing preferences, given the
    structural model and chosen attribution rule.

(b) Identify which subgroups face the largest opportunity-driven
    welfare gaps (e.g., low-education workers in high-unemployment
    regions).

(c) Simulate counterfactual policies that affect `q` or `g_1`
    directly (e.g., a regional employment subsidy that increases `q`
    in low-employment regions, or an education subsidy that shifts
    `g_1`).

(d) Compare to literature numbers (Capéau et al.'s 0.32–0.69 wage
    elasticities, Bargain et al.'s decomposition shares) using the
    same structural framework.

**Cannot**:

(e) Identify causal effects. The decomposition is model-implied,
    not causally identified. The same residence pattern that
    produces low `q` might also affect ability acquisition; the
    structural model doesn't separate these.

(f) Resolve the gender attribution question. The reader is given
    three attribution rules; the choice is normative.

(g) Speak to opportunity differences in childhood (which would
    affect ability formation). The decomposition treats `x_w` as
    given, not as itself the outcome of earlier opportunity. A full
    Roemer-style decomposition would require longitudinal data and is
    out of scope.

(h) Identify a "right" reference point. The decomposition magnitudes
    depend on the reference; the paper reports sensitivity but cannot
    avoid the choice.

(i) Distinguish discrimination from productivity differences in the
    gender wage gap. G4 acknowledges this; the paper does not claim
    to.

(j) Provide standard errors derived from the asymptotic distribution.
    Boundary parameters (`θ_c` in M0c_b, possibly `β_l0_m` in M0c_b2)
    make asymptotic inference invalid for those parameters. The
    decomposition's confidence bands come from bootstrap.

---

## 8. Robustness exercises required

The paper reports the main decomposition under specific choices and a
set of robustness exercises that vary those choices. Required:

(R1) **Gender attribution**: A1 vs A2 vs A3 (§4). Three columns in
     the main decomposition table.

(R2) **Spec choice**: M1-clean (β_E_educH dropped) vs M1-naive
     (β_E_educH retained). Two rows.

(R3) **Reference point**: median (main) vs mean vs best-available
     (§6). Three rows.

(R4) **Welfare measure**: EV (main) vs CV (§5). Two rows.

(R5) **Inequality index**: Gini (main) vs CV² (coefficient of
     variation squared) vs Theil. Three rows.

(R6) **Decomposition method**: ordered-removal vs Shapley. Two rows.

(R7) **Subsample**: full population (main) vs singles only vs
     couples only. Three rows.

(R8) **Bootstrap CIs**: 95% confidence bands on each decomposition
     number, computed via 200-replicate bootstrap with re-estimation
     of θ̂.

(R9) **Strong Roemer position** (alternative attribution): treat
     ability differences as compensation-relevant too. Report the
     decomposition under (opportunity + ability) vs preferences only.
     This is the upper bound on the responsibility-sensitive
     opportunity number.

The main paper text reports R1 explicitly and references the
appendix table for R2–R9. This is the standard structure for
responsibility-sensitive empirical papers.

---

## 9. Relation to the literature

| Paper | Decomposition compartments | Treatment of education in `q` | Treatment of gender |
|---|---|---|---|
| Aaberge-Colombino-Strøm 1999 | preferences vs opportunities (two-way) | in `q` | both `q` and `g_1` |
| Capéau-Decoster-Dekkers 2015/16 | preferences vs opportunities (two-way) | in `q` | both `q` and `g_1` |
| Bargain-Orsini-Peichl 2013 | tax/transfer + preferences (counterfactual) | n/a | gender-by-group estimation |
| Beffy-Blundell-Bozio-Laroque-To 2019 | preferences with hour restrictions | n/a | gender-by-group |
| Ferreira-Gignoux 2011 | circumstances + effort (parametric, two-way) | circumstances | gender as circumstance |
| Bourguignon-Ferreira-Menendez 2007 | same as FG2011 | circumstances | gender as circumstance |
| Roemer-Bossert tradition | circumstances + effort (axiomatic) | not applicable | typically circumstance |
| Maniquet-Fleurbaey | preferences + opportunities (axiomatic) | not modelled | varies by paper |
| **This JMP** | **opportunity + ability + preferences (three-way)** | **excluded from `q` (M1-clean)** | **G4 multi-rule reporting** |

The contribution is twofold:

(i) **Empirical**: a clean three-way decomposition on French data,
    distinguishing what RURO-style papers conflate.

(ii) **Methodological**: an explicit framework for separating
    ability-mediated from genuinely opportunity-driven welfare
    inequality in structural labour-supply models.

This is not a country-ranking exercise (FG2011, BFM2007 style) and
not a tax-reform counterfactual (BOP2013, BBBL2019 style). It is a
welfare decomposition with a sharper notion of what counts as
opportunity than the existing literature uses.

---

## 10. Commitments for welfare scaffolding code

The welfare scaffolding code, when implemented (after M0c_b2 freezes
the model and before M1-clean runs), must support the following
operations. This is the design contract for the welfare layer.

(C1) **Compute Ω given θ̂ and (x_opp, x_w, U-shifters)**. The
    primary function `compute_welfare(theta_hat, x_opp_i, x_w_i,
    preferences_i)` returns the EV-style money-metric welfare for
    household i.

(C2) **Compute Ω under counterfactual (x_opp, x_w)**. The function
    must accept reference values and produce
    `Ω_i^opp_eq`, `Ω_i^abil_eq`, `Ω_i^both_eq` for each household.

(C3) **Support multiple attribution rules** for the decomposition
    by partitioning the parameter vector θ̂ into
    (θ_opp, θ_abil, θ_pref). The partitioning depends on which
    attribution rule is chosen (A1, A2, A3 for gender; M1-clean vs
    M1-naive for education).

(C4) **Compute multiple inequality indices** (Gini, CV², Theil)
    on each of the four versions of Ω.

(C5) **Compute the ordered-removal decomposition** and the
    **Shapley decomposition** of total inequality across the three
    compartments.

(C6) **Compute bootstrap confidence intervals** by re-estimating θ̂
    on B = 200 bootstrap resamples (or partial-bootstrap with
    re-sampling at the choice-set level) and recomputing the
    decomposition for each.

(C7) **Output a single decomposition table** with rows R1–R9 and
    columns for each compartment, ready for the paper's main table.

(C8) **Handle the boundary-parameter issue**. For parameters at
    boundaries (e.g., `θ_c = 0` in M0c_b, possibly `β_l0_m = 0` in
    M0c_b2 if it's structurally fixed), the bootstrap must constrain
    these parameters to the same boundary in each replicate. This
    prevents the bootstrap from artificially inflating uncertainty
    via parameters that are actually fixed.

(C9) **Distinguish reporting of substantive results from inference**.
    Point estimates from M0c_b/M0c_b2 are reported as-is. Confidence
    bands are bootstrap-based. Parameter standard errors for
    boundary-pinned parameters are reported as "boundary" rather
    than "NA" or zero — a normal-language convention that makes
    clear what's been estimated and what's been imposed.

The code is to be developed in a new directory
`scripts/welfare/` parallel to `scripts/enhanced/`. The main entry
point will be `scripts/welfare/compute_decomposition.py`, with
helpers for the inequality indices, the counterfactual generation,
and the bootstrap.

This is the JMP-paper layer of the codebase, distinct from the
estimation layer.

---

## 11. What this memo commits and what it leaves open

**Locked**:

- The three-way decomposition framework (opportunity / ability /
  preferences) replaces the two-way framework standard in RURO
  papers.
- `β_E_educH` is removed from `q` at M1-clean; education-on-employment
  runs entirely through wages.
- Region dummies are added to `q` at M1-clean (three NUTS-1 dummies
  if the parquets carry `drgn1`).
- Gender effects are estimated normally; the decomposition reports
  three attribution rules (A1, A2, A3).
- Counterfactual decomposition with population-median-by-gender-and-
  household-type as the primary reference.
- The decomposition is welfare-inequality-of-Ω, not
  variance-of-shifters.
- Ordered-removal and Shapley decompositions reported.
- Bootstrap-based CIs.

**Left open (require François's input or further data work)**:

- Final choice of reference point (median may be replaced after
  discussion with François if the theory paper has a clearer
  position).
- Treatment of the wage-block `σ` as ability-related vs
  opportunity-related (currently shared across all groups; if
  regional differences in `σ` were estimated at M1-clean, region
  would partially absorb it).
- Whether the strong-Roemer alternative (R9) is reported as a main
  result or as a footnote. This depends on the paper's eventual
  framing.
- The Hicksian inequality index choice in the main table (currently
  Gini, but Atkinson or Bossert indices might be preferable for the
  responsibility-sensitive framing).
- The decision tree for handling additional boundary-parameter
  issues that surface in M1-clean or beyond.

**Sequenced after M0c_b2 verdict**:

- M1-clean implementation and estimation.
- M1-clean ↔ M1-naive sensitivity.
- Welfare scaffolding code (per §10).
- Decomposition table generation.
- Bootstrap inference.
- Paper drafting.

---

## 12. The cascade of choices implied by this framework

For your own working memory, here are the choices this framework
locks in, in the order they matter for downstream code:

1. **Spec layer** — M1-clean drops `β_E_educH` from `q` and adds
   region. Other RURO blocks unchanged.

2. **Welfare layer** — Ω is EV-based; counterfactual versions
   computed for opportunity, ability, both.

3. **Decomposition layer** — three-way (opp / abil / pref) using
   ordered-removal and Shapley; multiple inequality indices.

4. **Attribution layer** — three gender attribution rules reported
   for every decomposition; education attribution is fixed via the
   spec change.

5. **Inference layer** — bootstrap CIs with boundary-parameter
   constraints; point estimates from M0c_b/M0c_b2 reported as-is.

6. **Robustness layer** — R1–R9 sensitivity table in appendix.

7. **Paper layer** — main text reports R1 (gender attribution) and
   the M1-clean main number; appendix has R2–R9 and the M1-naive
   comparison.

The next concrete deliverable, after M0c_b2 finishes, is **not**
the welfare code. It is the M1-clean spec and estimation. The
welfare code can be developed in parallel against synthetic data
while M1-clean runs.

---

## Suggested filename

Save this memo as: `docs/JMP_ability_vs_opportunity_framework_v1.md`
(category: framework memo / foundational).

This memo is referenced by all subsequent design and verdict memos.
Any downstream decision that conflicts with the framework here
should be flagged and the framework updated to v2 before
implementation.
