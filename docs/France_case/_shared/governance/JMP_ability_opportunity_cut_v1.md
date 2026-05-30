# The Ability / Opportunity / Preference Cut for the JMP Decomposition

**Project:** Unequal Job Opportunities and Well-Being Inequality (JMP)
**Status:** conceptual cut, settled in prose; precedes and constrains the joint spec build
**Governs:** what `estimation_spec_joint_pooled_v1.yaml` must encode, and what the welfare/decomposition stage equalises
**Anchors:** Roemer (1998) circumstance/effort; Ferreira-Gignoux (2011); Bourguignon-Ferreira-Menendez (2007); the AC welfare tradition; `RURO_spec_redesign_decisions_v2.md` Sections D2/D3/D10

This memo does not change the 49-parameter joint estimation object. It classifies the estimated channels for the later welfare decomposition and constrains the way the joint spec and welfare module must treat those channels.

---

## 0. The one distinction the whole memo turns on: structural block does not equal normative component

The structural RURO model has **two** objects: systematic utility **v** (preferences) and the opportunity density **g** (the offer environment). The normative decomposition has **three** components: **preference, ability, access**. These do not line up one-to-one, and the single most common way to get this paper wrong is to assume they do.

The mapping is:

> **preference = v** (the whole utility side)
> **ability + access = g** (the opportunity side, split into two normative pieces)

So the three-way cut does not sit on top of the two-block structural architecture; it **cuts g in two**. The wage/Mincer technology is structurally part of g (it is the offer side; what wage a job pays is not chosen, it is offered), but normatively it is **ability** (returns to own education and experience), which most responsibility-sensitive criteria treat as responsibility-relevant and therefore not compensation-relevant. Everything else in g - the availability of jobs by hours band, occupation, region, urbanisation, and local demand - is **access**, which is not under individual control and is compensation-relevant.

Two consequences follow immediately, and both are load-bearing:

1. **A parameter's normative role follows the channel it acts through, not the observable that drives it.** The same observable can appear in more than one component. Education acts through wages (ability) and could in principle act through offer availability (access) and through leisure taste (preference). The rule is to route each channel to its component, never the variable wholesale.

2. **Reporting a bracket is mandatory, not optional.** Because ability sits on the contested boundary (productivity returns are responsibility-relevant under most criteria, but education is partly shaped by family background), the opportunity share must be reported as **[access-only, access+ability]**. This is the Section D2 bracket, and it is the honest representation of where the normative disagreement actually lives. The lower bound (access-only) is conservative in precisely Ferreira-Gignoux's sense: it both omits ability and uses only the circumstances we observe, so it is a lower bound on a lower bound.

---

## 1. The three-way taxonomy mapped to this model's parameters

Using the 49-parameter partition from `JMP_joint_estimation_spec_v1.md` (29 shared opportunity + 20 group-specific preference).

### Preferences (tastes) - the utility side v; never compensation-relevant in the baseline

All group-specific preference parameters:

- Leisure blocks: `beta_l0_{sm,sf,m,f}`, `beta_l_age{,2}_{sm,sf,m,f}`, `beta_l_nkids_{sf,f}`
- Leisure curvature: `theta_l_{sm,sf,m,f}`
- Consumption curvature: `theta_c_singles` (couples `theta_c=0` by spec)
- Couples leisure interaction: `beta_ll`
- Consumption coefficient `beta_c=1` (numeraire; defines the metric, not a taste to be compensated)

These say how much each type values consumption, leisure, children-time, and joint leisure. Under a **preference-respecting** welfare criterion (the AC tradition's default, and the baseline here), differences in these are responsibility-respecting: people who choose differently because they want different things are not owed compensation for the resulting welfare differences. The one contestable place - adaptive or gendered preferences - is flagged in Section 2 and handled as a discussion-level robustness, not a baseline bound.

### Ability / productivity - structurally inside g (wage technology); responsibility-relevant under most criteria

The wage technology defines the ability channel:

- `beta_w_educL`, `beta_w_educH` (returns to education)
- `beta_w_pexp`, `beta_w_pexp2` (returns to potential experience)
- `sigma` (residual wage dispersion / unobserved productivity)
- `beta_w0` (the common wage-level anchor within the wage block)

These map own education and experience into the wage offered jobs pay. That is individual productivity. Roemer would file "how long one studies" under effort/responsibility, and the wage return to that schooling is the cleanest case of a responsibility-relevant object in the model. **Nothing outside the wage technology is ability.**

For decomposition arithmetic, the ability equalisation acts on individual productivity variation: education, experience, and residual productivity. `beta_w0` belongs to the wage block structurally, but it is a common wage-level anchor, not itself an individual responsibility margin. `sigma` travels with the broad ability block because it captures residual productivity dispersion, but it must be reported with a caveat: residual wage dispersion may also contain unobserved access, matching frictions, or noise that the wage equation does not separately model.

### Opportunity / access - structurally inside g (everything except wage technology); compensation-relevant

Three blocks, all shared across groups:

- **Hours opportunity:** `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh` - availability of jobs by hours band, including base employment attractiveness `beta_E`, the existence-of-any-offer margin.
- **Market opportunity:** `beta_E_gsur`, `beta_E_drgn2..8`, `beta_E_drgur`, `beta_E_drgmd`, `beta_E_y2015`, `beta_E_y2017` - local demand, region, urbanisation, and year-level offer shifts.
- **Occupation opportunity:** `beta_occ_{2,3,4}_{m,f}` - gender-segmented offer mass over occupation categories (offer availability, not wage parameters; cf. Section D3).

These govern which jobs the market makes available to a person, conditional only on circumstances (region, urbanisation, local demand, gender-segmentation of occupations, and the aggregate cycle). A person who would prefer part-time but lives where only full-time is offered, or whose region offers thin local demand, faces a constrained feasible set through no choice of their own. That is the paper's central object, and it is compensation-relevant.

---

## 2. The hard cases - decided

### Education: ability via the wage return; the access-purity rule binds

**Rule: education enters the decomposition through exactly one channel - the wage equation - and is therefore counted as ability. Education never enters the access blocks.** This is `RURO_spec_redesign_decisions_v2.md` Sections D2/D10 ("education/experience never in access; `educH` wage-offer -> ability") and Section D4(b), which verified on disk that `educH` appears only in `wage_opportunity`. Keep it that way: no education term in hours-opportunity, market-opportunity, or occupation-opportunity.

The Roemer tension is real and is handled by the bracket, not by re-routing. Education's return is responsibility-flavoured (it is productivity), so the **access-only lower bound excludes it**. But education itself is partly a circumstance (family background drives schooling), so the **access+ability upper bound includes it**. The width of the bracket between these two bounds is the quantified disagreement over whether education counts. Do not try to settle it inside the model; report it.

One permitted exception, only if the spec later adds it: if education enters leisure taste (`educH` as a `beta_l` shifter), that channel is **preference**, not ability and not access. Section D2 already states this ("`educH` leisure-taste -> preference"). The current intended joint spec has no such term; if one is added later, it goes to preference.

### Age: split between ability and preference; never access

Age has two clean channels and they go to two different components:

- **Potential experience** (`beta_w_pexp`, `beta_w_pexp2`), which is constructed from age, is a productivity return and therefore **ability**.
- **Age in the leisure block** (`beta_l_age`, `beta_l_age2`) is a life-cycle taste for leisure and therefore **preference**.

Age is **not** access. The market does not ration offers on age in this model, and the joint spec should not let it: an age term in the market-opportunity block would conflate life-cycle taste/productivity with rationing. So age never appears in any access block.

### Gender: circumstance, not ability, with effects split by channel

Gender is a circumstance. It is not ability. Gender-driven access gaps are compensation-relevant.

The reconciliation is that "ability" in the responsibility-relevant sense means individual productivity that can be held to the person - education return, experience return, and residual productivity. Gender is not that; it is an ascriptive characteristic.

Gender enters this model through two structural channels:

1. **Gender-in-offers.** Occupation offers are gender-specific (`beta_occ_*_m` vs `_f`); occupational segregation is an offer-side fact. This channel is **access -> opportunity -> compensation-relevant**, always and in both bracket bounds. Hours opportunity remains shared in the baseline unless the joint pooling tests later justify a disciplined relaxation.

2. **Gender-in-tastes.** Leisure blocks are gender-specific (`beta_l0_f`, `beta_l_nkids_sf`, etc.). This channel is **preference -> baseline not compensated**.

The structural model identifies the split between these channels: the leisure block fits within-gender hours behaviour conditional on offers, while the occupation-offer block fits cross-gender availability of occupations. This is the JMP's advance over a standard ex-ante IOp type partition. In a cell-based exercise, gender is a type-defining circumstance and all gender-correlated welfare variation, taste channel included, is mechanically "opportunity." Here, only the offer channel is opportunity; the taste channel is preference.

One contestable residue is handled as discussion, not as a baseline bound. If gendered preferences are adaptive - if women value leisure more partly because the labour market offered them less - then part of the "preference" channel is itself circumstance, and the baseline understates opportunity. Do not fold this into a third bracket bound. Handle it in the discussion section as a stated direction of bias: if gendered leisure preferences are partly adaptive, the access-only and access+ability bounds are both lower bounds on opportunity. This keeps the baseline preference-respecting while being honest about the limit.

---

## 3. Variable-placement table and flags for the intended joint spec

The table below is the normative placement the intended joint spec must implement. It is clean if `estimation_spec_joint_pooled_v1.yaml` follows this placement.

| Observed variable | Channel it acts through | Decomposition component | Spec block it belongs in | Consistent with intended joint spec? |
|---|---|---|---|---|
| `educL`, `educH` | wage return | **ability** | `wage_opportunity` | Yes; `educH` was verified only in the wage layer in Section D4(b) |
| `pexp_years`, `pexp_years2` (from age) | wage return | **ability** | `wage_opportunity` | Yes |
| `age_norm`, `age_norm2` | leisure taste | **preference** | `utility.leisure.shifters` | Yes |
| `n_children` | leisure taste (female) | **preference** | `utility.leisure.shifters` (`beta_l_nkids_{sf,f}`) | Yes |
| gender (via group `sm`/`sf`/`m`/`f`) | leisure taste | **preference** | group-specific leisure blocks | Yes |
| gender (via `_m`/`_f` occupation offers) | occupation offer availability | **access** | `occupation_opportunity` | Yes, if the joint spec collapses occupation to gender |
| `gsur` | local demand | **access** | `market_opportunity` | Yes |
| `reg2..reg8` (NUTS-1) | regional offer availability | **access** | `market_opportunity` | Yes |
| `drgur`, `drgmd` (urbanisation) | offer availability by density | **access** | `market_opportunity` | Yes |
| `loc4` (occupation category) | offer mass over occupations | **access** | `occupation_opportunity` | Yes; offer mass, not wage |
| year `y2015`/`y2017` | aggregate offer level | **access** | `market_opportunity` | Yes; wage basis was fixed in `RURO_build_fix_wage_idorighh_v1` |
| `sigma` | residual productivity dispersion | **ability** | `wage_opportunity.variance` | Yes, with the residual-heterogeneity caveat |

No variable in the intended joint spec is normatively misrouted if the YAML implements this table. Two things should be watched rather than re-routed:

- **`sigma` is filed as ability but is residual dispersion.** It may capture unobserved productivity, unobserved access, matching frictions, or noise. It belongs in the broad access+ability bound, but the welfare report should state this caveat and, if feasible, include a sensitivity check that excludes residual wage dispersion from the broad bound.

- **The real-wage requirement is resolved.** `RURO_build_fix_wage_idorighh_v1` confirmed that estimator-facing wages are now 2016-real using the same `phi` basis as `ils_dispy_real`, with nominal wages preserved as `*_nominal`. The year indicators therefore absorb real aggregate offer-level shifts, not nominal wage drift.

---

## 4. External regional data: defer; decide after the joint run

**Recommendation: run the baseline on the internal access variables (`gsur` + NUTS-1 + urbanisation). Pre-register external regional data as the first refinement (Section D6), but do not scope it now.**

Three reasons, in order of weight:

1. **You do not yet know the access component is large enough to be worth sharpening.** The whole point of the joint run is that region and urbanisation were inert on every singles slice and only identified on the couples 2016 slice; the pool is what first activates them for all groups. Until the joint estimate reports the magnitude and stability of the access block, scoping external data is premature. If the access share turns out small, external data is wasted effort; if large, the estimate will show exactly which margin (region, urbanisation, or demand) needs sharpening.

2. **External data is the natural first-refinement extension, and the project already treats it that way.** Section D6 defers external regional labour-demand data (vacancy, job-finding, or sectoral employment by NUTS, from DARES/INSEE/Eurostat, merged on `drgn2`/`drgn1`) as the first refinement, with the internal variables as the baseline. Bringing it in now would violate the "one increment at a time, baseline first" discipline in Section D10 and entangle a clean extension with the baseline identification.

3. **The internal variables still need honest interpretation.** `gsur` + region dummies + urbanisation are reduced-form proxies for local demand, similar in spirit to the BFM-2007 kind of opportunity proxy the paper claims to supersede. The structural advance is that they enter the offer density g rather than the wage directly, and that the feasible set is modelled explicitly. That is real, but it does not make region dummies an exogenous demand shock. External regional demand data would buy a cleaner interpretation of access as local labour demand outside individual control and less contaminated by residential sorting. Sequence it as the first refinement, and let the joint run's access-block result decide priority.

---

## 5. How the cut maps onto the decomposition arithmetic

The welfare object is money-metric well-being computed at each individual's **own** preferences over their **own** feasible offered set - the constrained-feasible-set welfare object of the concept note. Inequality of this object, `I(W)`, is decomposed into three components by **counterfactual equalisation**, made order-independent by the **Shapley-Shorrocks** rule. Three factors means averaging over the `3! = 6` equalisation orderings; the three contributions sum exactly to `I(W)`.

What is held fixed vs equalised to isolate each component:

- **Access component.** Equalise the access blocks: give every individual a common offer environment over hours, occupation, region, urbanisation, and local demand (for example the population-average offer density, or a reference cell), while holding ability (own education/experience and residual productivity) and preferences at actual values. Recompute money-metric welfare on the new common feasible set. The fall in inequality attributable to this equalisation, Shapley-averaged over orderings, is the **access component**. This is the lower bound of the opportunity share.

- **Ability component.** Equalise the wage technology's dependence on own characteristics: neutralise the education/experience returns and residual productivity differences so offered wages no longer track individual productivity, while holding access and preferences fixed. `beta_w0` remains the common wage-level anchor. Recompute welfare; the Shapley contribution is the **ability component**. Adding it to access gives the **upper bound** of the opportunity share. The gap between the two bounds is the education/ability normative disagreement, quantified.

- **Preference component.** Equalise preferences by assigning a common reference preference (a reference type's `v`) and revaluing each feasible set with it. This is the conceptually hardest counterfactual and must be flagged as such: under money-metric welfare, the preference used to value bundles is the metric, so "equalising preferences" changes the yardstick, not merely an input. The baseline practical resolution is to fix a single reference preference (for example pooled or a designated reference type), report the preference component conditional on it, and run a sensitivity check over the choice of reference type. Do not present the preference component as reference-free; it is not.

The headline output is therefore not one number but a **bracketed opportunity share**: narrow = access component; broad = access + ability. The preference component is the complement, with reference-preference sensitivity attached. This is the structural analogue of Ferreira-Gignoux's lower-bound IOp share, refined into model channels rather than circumstance cells.

---

## Summary of decisions

| Question | Decision |
|---|---|
| Structural vs normative | Two structural objects (`v`, `g`); three normative components; the cut splits `g` into ability + access |
| Preferences | All leisure blocks, `theta_l`, `theta_c_singles`, `beta_ll`, and `beta_c`; baseline non-compensated |
| Ability | Wage technology channel; individual variation from education, experience, and residual productivity; `beta_w0` is the common wage-level anchor |
| Access | Hours + market + occupation-offer blocks; compensation-relevant; included in both opportunity bounds |
| Education | Ability through the wage channel only; access-purity rule binds; the bracket carries the Roemer disagreement |
| Age | Split: experience -> ability, age-in-leisure -> preference; never access |
| Gender | Circumstance, not ability; effects split by channel: offers -> access, tastes -> preference; adaptive-preference caveat is discussion, not a third bound |
| Spec consistency | The intended joint spec is normatively clean if it implements this table; watch `sigma` as residual heterogeneity |
| Wage basis | Resolved by `RURO_build_fix_wage_idorighh_v1`: estimator-facing wages and `ils_dispy_real` are both 2016-real |
| External regional data | Defer; baseline on internal access; pre-register as first refinement; decide after the joint run shows access-block size/stability |
| Arithmetic | Shapley-Shorrocks over {preference, ability, access}; money-metric welfare recomputed under each equalisation; report [access-only, access+ability] bracket; flag reference-preference indeterminacy on preference equalisation |

