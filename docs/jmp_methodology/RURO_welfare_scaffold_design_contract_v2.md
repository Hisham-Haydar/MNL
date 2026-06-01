# RURO Welfare-Scaffold Design Contract v2

**Date:** 2026-06-01
**Document class:** code-design contract. This is the specification the welfare
module **must meet**; it is the object a later `RURO_welfare_scaffold_verdict_v1.md`
audits the implemented code against. It translates the frozen welfare-object memo
`JMP_welfare_spec_v5.md` (and the two v2 welfare memos it supersedes the object
layer of) into a written code contract. **v2 supersedes
`RURO_welfare_scaffold_design_contract_v1.md`**, re-grounding the contract on the
frozen `JMP_welfare_spec_v5.md` (which settles the welfare-integration scheme; the
welfare object is unchanged from v4).

**What this contract is.** A binding description of the module boundaries, the
computational core, the configuration schema, the build order, and the validation
gates the welfare scaffolding must satisfy. It is the welfare-side analogue of a
spec design memo: it fixes *what the code must do and on what grounds*, so the
implementation is audited against a written contract rather than discovered from
code.

**What this contract is not.** It is **not** an authorisation to implement, and
not a welfare result. It writes no welfare code, runs no estimation, welfare,
decomposition, bootstrap, or data-rebuild script, and computes **no welfare or
decomposition numbers**. Nothing here constitutes a welfare finding. Implementation
is gated on a separate authorisation that takes this contract and the resolved
certified baseline path as joint inputs.

**Anchors (grounded against the repo, read-only).**

- **Certified estimate:** the 47-param pooled spec `joint_pooled_v1_bll0_tlmpin`
  (`beta_ll=0`; `theta_l_m=-0.8` pinned; `beta_E`, `beta_h_pt2` **shared**),
  identification-certified at the 901-alt resolution (synthetic Check-5 PD
  `min_eig=+1.706`; real-data Hessian PD `min_eig=+0.459`).
- **`theta_hat` store:** `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` —
  48 rows (header + 47 params), columns `parameter,value,se_hessian,se_clustered`.
  The spec is `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`.
- **JAX likelihood / engine entry points:** `build_jax_singles_ll`,
  `build_jax_couples_ll` (`scripts/bpool/jax_ll_probe.py`); the joint assembler
  `build_joint_neg_ll` (`scripts/bpool/jax_joint_hessian.py`). The numpy reference
  engine is `compute_likelihood_singles` / `compute_likelihood_couples`
  (`scripts/enhanced/estimation_engine.py`), used for the synthetic DGP and as the
  validated cross-check, not the welfare path.
- **Proposal/prior correction:** the engine forms
  `V = u + log_h + log_w + log_market - log_prior`
  (`jax_ll_probe.py:260,461`). The `prior` column on the engine-ready parquets is
  `prior = exp(log_prior)`, with
  `log_prior = log_q_E + working*(log_q_Occ + log_q_H + log_q_W)` for singles and
  the partner-independent joint analogue for couples
  (`build_bpool_singles.py`, `build_bpool_couples.py`,
  `harmonise_bpool_engine_ready.py`). This `-log_prior` term **is** the welfare
  `-log π(j)` correction of `JMP_welfare_spec_v5.md` §1.1. The proposal is **partly
  individualised** per `welfare_proposal_individualisation_check.md`: the wage
  channel (household-specific mean `μ_i = X_i b + δ_occ[loc4_i]`) and the occupation
  channel (gender×education stratum) condition on `x_i`; hours (fixed D1 five-mode
  mixture) and employment (flat `π0 = 0.10`) are common; the structural market
  block (GSUR/region/year) lives in `g`, not in `π`. Therefore `-log_prior` is a
  **household-specific per-row column**, not a common function of `(w,h)` (the
  traced construction `V = u + log_h + log_w + log_market − log_prior` is unchanged).
- **Config mechanism:** `scripts/enhanced/estimation_spec_parser.py`
  (`parse_specification`) parses generic top-level YAML blocks `fixed_params:`
  (pin a parameter, remove from the free vector), `gender_split:` (relax a base
  coefficient to `_m`/`_f`), and `reporting:` (case-owned, estimation-ignored).
  These are the precedents the welfare config blocks below mirror.
- **Cluster unit:** `cluster_ids == idorighh` on the engine-ready parquets
  (`step4_realdata_baseline.py`); 9,657 clusters at the certified baseline.

---

## 1. Purpose & document class

The welfare scaffold is the code layer that, given the certified structural
parameter vector `theta_hat` and the 901-alt engine-ready data, constructs the
**Exercise A welfare family**: the ex-ante inclusive-value attained-utility core
`V_i`, the six reference constructions `W^1`..`W^6` as reference + own-preference
inversion, and the inequality `I(Omega^k)` of each measure's welfare distribution.

The scaffold reads `theta_hat` as a fixed input. It does **not** re-estimate, re-fit,
re-derive, or modify any structural object. Inference uncertainty enters only through
the cluster-robust bootstrap (§8), which invokes the scaffold once per replicate;
the re-estimation is external.

The contract is written against the JAX backend at the 901-alt couples resolution
(901 = 30×30; singles 101 alts), the same engine and the same `-log_prior`
convention the certified fit used. The welfare path must call the **same** utility
and opportunity-density construction as the estimator (one machine, not a
re-implementation), so that `V_i` at `theta_hat` is by construction consistent
with the likelihood that produced `theta_hat`.

This contract is the spec a later verdict audits the code against. It is not an
authorisation and contains no welfare numbers.

---

## 2. Scope

**In scope — the Exercise A welfare family only:**

1. The ex-ante inclusive-value attained-utility core `V_i` (§3), with the
   mandatory `-log π(j)` proposal/prior correction.
2. The six reference constructions `W^1`..`W^6` (§3), each as a declared
   **reference** plus an **own-preference inversion** to money.
3. The inequality `I(Omega^k)` of each measure `k`, computed by a
   measure-agnostic, index-agnostic inequality module.
4. The welfare-side validation gates (§6).

**Deferred to their own artifacts (out of scope here):**

- **Exercise B — the source decomposition.** The access/ability/preference
  Shapley–Shorrocks equalisation and its component CIs are a separate
  decomposition contract. This contract only guarantees that the Exercise A
  outputs are **structured so the decomposition can consume them without
  refactoring** (§7) — it does not implement equalisation, Shapley averaging, or
  any decomposition number.
- **Gender-split robustness.** Baseline welfare uses **shared** `beta_E`,
  `beta_h_pt2` (`JMP_welfare_spec_v5.md` §3c). Gender-differentiated offers are a
  planned robustness only; `beta_h_pt2` is excluded from any identified gendered
  path (`RURO_gsplit_nonid_structure_v1.md`: independent mislocation, not
  reparameterisable). A future `beta_E` contrast swap is a config change, deferred.
- **Stochastic dominance** of choice sets (`JMP_welfare_spec_v5.md` §5): deferred
  until the family numbers exist.
- **Intra-household equivalisation:** deferred. The welfare unit is the household
  (§3); couples are never split.

**The welfare-vs-decomposition boundary, stated explicitly.** Exercise A
(*the measure menu*) computes each `Omega_i^k` and the inequality of each measure's
distribution — it varies the **normative stance** (how much each opportunity
dimension is compensated) and reports the resulting spread across measures.
Exercise B (*the source decomposition*) holds a chosen measure fixed and attributes
its inequality to access/ability/preference by equalising a channel and measuring
the inequality fall. **This contract delivers only Exercise A and the interfaces
Exercise B will later attach to.** The measure stance (Exercise A) and the
decomposition channel (Exercise B) are the same normative cut operationalised two
ways and must never be double-interpreted; keeping them in separate contracts is
the structural guard.

---

## 3. Computational contract

### 3.1 The ex-ante attained-utility core `V_i`

For each household `i`, the scaffold computes the ex-ante expected-maximum
(inclusive-value) attained utility over the household's feasible set `C_i`:

```
V_i = log Σ_{j ∈ C_i} exp( v_i(c_j, ℓ_j) + log g(j; x_opp,i) − log π(j) )
```

- `v_i(c_j, ℓ_j)` is the household's **own**-preference deterministic utility
  (Box-Cox consumption/leisure, the certified `theta_hat` preference block).
- `log g(j; x_opp,i)` is the opportunity-density term (hours + wage + market +
  occupation), assembled by the **same** engine construction the estimator uses.
- `−log π(j)` is the **mandatory** proposal/prior correction — the welfare analogue
  of the sampling-of-alternatives correction. Operationally it is the engine's
  `− log_prior` term, with `prior = exp(log_prior)` read from the engine-ready
  parquet column. The scaffold MUST apply it; a `V_i` computed without `−log π(j)`
  is not a valid welfare core and is forbidden as a headline object.
- The draw count and scheme (B-pool D1+W1; 901 couples, 101 singles) MUST be
  recorded in the output provenance, and the three-part welfare-integration gate
  (§6) MUST pass before any `V_i`-derived distribution is trusted.

**Primary welfare-integration estimator.** The primary scheme is **importance
sampling over the existing estimation draws** with the household-specific per-row
prior, `V_i^IS`, grounded in `JMP_welfare_spec_v5.md` §1.1 and
`welfare_proposal_individualisation_check.md`:

```
V_i^IS = log Σ_{j ∈ C_i} exp( v_i(c_j, ℓ_j) + log ĝ(j; x_i) − log π(j; x_i) )
```

where `−log π(j; x_i)` is the per-row `prior` column already on the engine-ready
data. It is **analytic in the extreme-value shocks** (the log-sum is the closed-form
expectation over `ε`) and invokes **no Fréchet draws and no simulated argmax**
(those belong to behavioural simulation — fit, elasticities, counterfactuals — which
remain deferred). It is well-conditioned because the two proposal channels that
carry heavy covariate-driven concentration in `ĝ` — wage and occupation — are the
individualised ones, so the IS divergence is small on exactly the dimensions that
would otherwise dominate its variance. The redraw-from-`ĝ_i` estimator, `V_i^dir`
(integration nodes drawn from the estimated individual opportunity density, `ε`
still integrated analytically), is **retained as the validation cross-check** and is
**escalated to primary only on a flagged subset per the §6 ESS gate**.

`V_i` is the common core of **all six** measures; the measures differ only in the
reference against which `V_i` is converted to money under the household's own
preferences.

### 3.2 Each `W^k` as a declared reference + own-preference inversion

Every `W^k` is an equivalent-income-type object: the income/subsidy that equates
the household's attained situation (`V_i`) to a measure-specific **reference**,
evaluated under the household's **own** preferences `R`. The scaffold computes each
`W^k` as a one-dimensional numerical inversion of the own-utility map at the
declared reference (a bracketing root solve), never by a closed-form shortcut that
would bypass the household's preferences.

The six references, imported from the companion theory paper as **cited
primitives** (definitions and the Ind-`y`/Ind-`A` classification only; no proofs
reproduced, no axioms restated as JMP results):

| Measure | Reference / construction | Ind `y` | Ind `A` | Normative reading |
|---|---|---|---|---|
| `W^1` | preferred job in **own** set `A`, pay ignored (consumption `c'=w` at the preferred feasible job) | + | − | compensate pay; responsible for the set |
| `W^2` | **best-paid equivalent** in own set `A` (uniform tax/subsidy `t`; `w = max_{j∈A} y(j) − t`) | − | − | Full Responsibility (own everything) |
| `W^3` | **laissez-faire** in own set `A` with pay (`c' = y(j') + w`) | − | − | Full Responsibility (laissez-faire) |
| `W^4` | **staying-home** equivalent (indifference to `(w, o)`, the non-employment option `o` with `y(o)=0`) | + | + | Full Compensation |
| `W^5` | **uniform subsidy to reference set `Ā`** (`j' ∈ Ā`, `c' = y(j') + w`) | − | + | compensate the set; responsible for pay |
| `W^6` | **best job in the whole economy `J`** (preferred job over `J` under `y^w`) | + | + | Full Compensation (+ Weak Responsibility) |

Endpoints and duals (drive build order §5 and the deferred decomposition anchoring):
`W^4/W^6` = Full Compensation endpoint; `W^2/W^3` = Full Responsibility endpoint;
`W^1` (compensate pay, responsible for access) and `W^5` (compensate access,
responsible for pay) are the two one-sided duals — the access/ability cut read off
the menu. All six read attained utility `V_i`, so unequal access lowers welfare
under **every** measure through attainment; the Ind-`y`/Ind-`A` properties bite only
in the *direct* evaluation channel. This is why a later decomposition is
measure-dependent and must be anchored — recorded here as a forward fact, not
implemented.

### 3.3 Household-unit construction

- The welfare unit is the **household**. One `Omega_i^k` per couple, from **joint**
  utility and **joint** budget. Couples are **never** split into two individual
  welfare objects.
- Within-couple gender enters only through the attribution rules of the deferred
  decomposition; this contract carries the couple as a single unit.
- Singles male, singles female, and couples are processed under type-conditional
  references and reported separately (never pre-pooled into one
  opportunity/welfare headline — §7, and `JMP_welfare_spec_v5.md` §3a).
- Intra-household equivalisation is deferred.

### 3.4 The reference sets `Ā`, `J`, `o` are config-defined

- `o` (non-employment / staying-home option for `W^4`): the existing
  non-employment alternative in each household's choice set; declared in config by
  its alternative key, not hardcoded.
- `J` (universal job set for `W^6`): the pooled support of offered job types,
  declared in config (`JMP_welfare_spec_v5.md` §1.2). Not a hardcoded France/2016
  enumeration.
- `Ā` (reference ability set for `W^5`): the reference opportunity set, declared in
  config. The within-`W^5` reference (e.g. type-conditional median vs maximal) is a
  config-selected sensitivity, constructed by shared code.

---

## 4. Config schema (YAML)

Everything that is a normative or specification choice is **config-driven**;
adding or removing a measure from the menu, or changing a reference, is a
configuration change, **not** a code change. The schema mirrors the existing
`fixed_params:` / `gender_split:` / `reporting:` precedent in
`estimation_spec_parser.py`. No hardcoded France/2016/P3a constants anywhere in the
welfare code; case-specific values live only in config and in the cited spec/parquet.

```yaml
welfare:
  baseline:
    spec_yaml_path: "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
    theta_hat_path: "scripts/bpool/specs/theta_hat_realdata_901_v1.csv"   # cols: parameter,value,se_hessian,se_clustered
    couples_stem: "fr_p3a_bpool_engine_ready"        # 901-alt; resolution asserted at load
    singles_stem: "fr_p3a_bpool_engine_ready"        # 101-alt singles legs
    resolution_guard:
      couples_alts: 901                              # MUST match at load or abort

  core:
    proposal_correction: "minus_log_prior"           # mandatory; prior = exp(log_prior) from parquet
    proposal_correction_required: true               # a V_i without it is rejected
    draw_scheme: "bpool_d1w1"                         # recorded in provenance
    integration:                                     # v5 welfare-integration controls (§6 three-part gate)
      primary_estimator: "importance_sampling_existing_draws"  # V_i^IS over existing draws
      per_household_stability:
        enabled: true                                # V_i^IS stable as draws grow at production resolution
        draw_multipliers: [1, 2, 4]
        tolerance: "declared"                        # drift beyond tolerance fails the gate
      ess_threshold: "declared"                      # flag households with ESS_i below this
      report_max_normalised_weight: true             # per-household max ω_is reported
      cross_check_on_flagged: "redraw_v_dir"         # V_i^dir on the flagged subset only; persistent disagreement => escalate

  measures:
    active: ["W3", "W5", "W2", "W4", "W6", "W1"]      # the menu; add/remove = config change
    reference_preference:                            # the preference the reference is evaluated under
      W2: "R_c"                                       # consumption-only reference preference
      W5: "R_h"                                       # horizontal reference preference
      default: "own"                                  # measures evaluated under own R unless overridden
    reference_sets:
      o_nonemployment_key: "..."                     # W4 staying-home option (alt key in choice set)
      J_universal: "pooled_offered_job_support"      # W6 universal set
      Abar_reference:                                # W5 reference ability set
        primary: "type_conditional_median_opportunity"
        sensitivity: ["maximal_opportunity"]

  unit:
    household: true                                  # one Omega per couple; never split
    report_groups: ["singles_male", "singles_female", "couples"]
    pool_opportunity_share: false                    # couples/singles NEVER pre-pooled (JMP_welfare_spec_v5.md §3a)

  fixed_params:                                       # mirrors estimation fixed_params; held in welfare too
    theta_l_m: -0.8
    beta_ll: 0.0
  pinned_zero_uncertainty: ["theta_l_m", "beta_ll"]   # bootstrap holds these fixed (JMP_welfare_spec_v5.md §3a)

  blocks:                                             # channel membership read from config, not hardcoded
    preference: [...]                                 # v (tastes); per JMP_welfare_spec_v5.md §2 table
    ability:    [...]                                 # wage tech in g
    access:     [...]                                 # hours/market/occupation/year in g
    # NOTE: consumed by the deferred decomposition; declared here so A-outputs are equalisation-ready

  inequality:
    active_indices: ["gini"]                          # measure-agnostic; secondary indices = config add
    sensitivity_indices: ["cv_squared", "theil_l", "atkinson_eps1", "atkinson_eps2"]

  inference:
    procedure: "cluster_bootstrap"
    cluster_unit: "idorighh"                          # 9,657 clusters at the certified baseline
    n_replicates: 200
    confidence_level: 0.95
    asymptotic_se_for_headline: false                 # forbidden; bounds params invalidate them

  decomposition_readiness:                            # interfaces only; NOT implemented here
    preference_equalisation_pinned_switch: "held"     # "held" | "swapped" (JMP_welfare_spec_v5.md §3a) — see §7
    expose_block_structure: true
    separable_opportunity_shares: true                # couples/singles separable, never pre-pooled

  output:
    table_dir: "outputs/welfare/tables/"
    figure_dir: "outputs/welfare/figures/"
    diagnostic_dir: "outputs/welfare/diagnostics/"
    provenance: "write_resolved_config_and_draw_scheme"
```

The schema fixes the shape; the values fix the run. Switching the active measure
set, a reference, the reference preference, the inequality index, or the cluster
unit is a single config edit. The welfare source code MUST contain **zero**
hardcoded specification-identifying strings, reference constants, or
country/year constants — the test of genuine agnosticism, exactly as the estimator
reads block membership and pins from YAML.

---

## 5. Build-order gate

The claim "family comparison = the headline" is an empirical bet whose strength
equals the across-measure spread, which is unknown until computed
(`JMP_welfare_spec_v5.md` §6). The scaffold is therefore built and validated in
this order; **no** "sensitivity to the welfare measure is the result" claim is made
before the spread is observed.

**Step 1 — validate `W^3` (laissez-faire, Full Responsibility) end-to-end first.**
Full Responsibility pre-absorbs nothing, so it is the cleanest stress-test of the
welfare core + inversion + inequality machinery, with no measure-side compensation
masking a bug. *Validated* at this step requires, all on `W^3`: (a) `V_i` computed
with the `-log π(j)` correction and passing the welfare-integration gate (§6);
(b) the inversion passing the inversion-sanity gate (§6) — reference recovers zero,
monotonicity holds; (c) the household-unit-integrity gate (§6) passing (one
`Omega_i` per couple, joint budget); (d) `I(Omega^3)` computed by the inequality
module and reproducible bit-for-bit on re-run given identical inputs.

**Step 2 — compute the access face `W^5` and the endpoints (`W^2`, `W^4`/`W^6`) to
observe the spread.** `W^5` is the access-compensated dual; `W^2` is the second
Full-Responsibility check; `W^4`/`W^6` are the Full Compensation endpoints. Each
reuses the validated core and inversion under its declared reference. *Validated*
at this step requires every active measure to pass gates (a)–(d), plus the menu to
be ordered Full Responsibility (`W^2`,`W^3`) → one-sided (`W^1`,`W^5`) → Full
Compensation (`W^4`,`W^6`) for reporting.

**Step 3 — decide the headline empirically (no code gate; a reporting decision).**
If the across-measure spread is material, the family comparison is the headline; if
not, the family is a robustness surface and the **committed focal pair** —
`W^3` (Full-Responsibility total) and `W^5` (access-compensated dual) — carries the
headline. This focal pair is a committed design element so the abstract has a home
regardless of the spread. **No welfare numbers are produced under this contract;**
this step only fixes *what the code must be able to report*, not any result.

(Validating first on `W^5` is forbidden: its own access-compensation would hide the
access channel behind the measure, the opposite of a first stress-test —
`JMP_welfare_spec_v5.md` §6.)

---

## 6. Pre-computation validation gates

These MUST pass before any welfare distribution is trusted. They are real checks,
not interpretive identities.

1. **Welfare-integration gate (three parts)** — the
   `JMP_welfare_spec_v5.md` §6 gate, replacing the single simulation-consistency
   check of v4:
   - **(i) Per-household stability of `V_i^IS`.** `V_i^IS` and each `Omega_i^k`'s
     inequality must be **stable as the draw count grows** at the production
     resolution (`core.integration.per_household_stability.draw_multipliers`). Drift
     beyond the declared tolerance (`core.integration.per_household_stability.tolerance`)
     fails the gate and no distribution from that configuration is reported.
   - **(ii) Effective-sample-size diagnostic.** Report, per household,
     `ESS_i = (Σ_s ω_is)^2 / Σ_s ω_is^2` (where `ω_is` are the importance weights)
     and the **maximum normalised weight** (`core.integration.report_max_normalised_weight`).
     Flag households with `ESS_i` below the executable threshold
     `core.integration.ess_threshold` — the exposure created by the **common** hours
     and employment proposal channels. On that flagged subset only, run the
     cross-check `core.integration.cross_check_on_flagged` (compute `V_i^dir`) and
     require agreement within tolerance. **Persistent disagreement on the flagged
     subset is the sole escalation trigger** to promote the redraw `V_i^dir` from
     cross-check to primary for those households; aggregate draw-count stability does
     **not** by itself clear per-household weight degeneracy.
   - **(iii) Reference-coverage / EUROMOD gate, narrowed to reference packages
     only.** No reference is evaluated until every required household-specific
     disposable income `c_ij` for the reference packages of `Ā`, `J`, and `o`
     exists — present from the build or supplied by a targeted EUROMOD evaluation.
     The reference packages MUST be evaluated at the build's **2016-real price
     basis and EUROMOD system year**. A **wholesale EUROMOD rerun is forbidden**
     (regression risk to verified deflation consistency); **silent interpolation**
     of missing `c_ij` is forbidden; missing reference packages block computation
     rather than being approximated. Because **integration nodes are not redrawn
     under the primary scheme**, this gate touches reference packages only, not
     integration nodes.

2. **Inversion sanity.** For each measure, a household placed **at** its own
   reference must invert to **zero** welfare (`W^k = 0` at the reference, per the
   theory-paper normalisations — e.g. `W^5 = 0` when `z = argmax_{(Ā,y)} R`), and
   the inversion must be **monotone** (more attained utility → weakly higher
   equivalent income). The bracketing solve must converge for every household;
   non-convergence is flagged per household and gates the run.

3. **Household-unit integrity.** Exactly one `Omega_i^k` per couple, computed from
   joint utility and joint budget; no couple produces two individual welfare
   objects; singles and couples carry type-conditional references. A violation
   (e.g. a per-capita split leaking in) gates the run.

**Forward requirement (named, not implemented here): the Shapley-exhaustiveness
gate.** The deferred decomposition contract MUST enforce that the
access/ability/preference Shapley components sum **exactly** to `I(Omega^k)` for the
chosen measure (order-independence/exhaustiveness). This contract does not implement
it; it records it as a required gate the decomposition contract must carry, and it
guarantees (§7) that the Exercise A outputs expose `I(Omega^k)` and the block
structure that gate will need.

---

## 7. Decomposition-readiness

This contract does **not** decompose. It guarantees the Exercise A outputs are
**structured so the downstream decomposition module can equalise a channel without
refactoring**:

- **Outputs exposed:** per household and per measure, `Omega_i^k`; the core `V_i`;
  the per-measure inequality `I(Omega^k)`; and the **block structure**
  (`welfare.blocks`: preference / ability / access membership) read from config, so
  the decomposition can set a block to a reference environment and recompute
  `Omega_i^k` through the same core.
- **Pinned-preference switch exposed as a config flag.** `theta_l_m` and `beta_ll`
  are pinned (zero uncertainty by construction; the bootstrap holds them fixed).
  Under the deferred **preference-equalisation** channel the pinned params may be
  either **held at their pinned values** or **swapped for the reference preference**
  (`JMP_welfare_spec_v5.md` §3a). This choice sizes the couples preference component
  and therefore the couples opportunity share, so it MUST be a config flag
  (`decomposition_readiness.preference_equalisation_pinned_switch: held | swapped`),
  surfaced now even though equalisation is implemented later. The default recorded
  here is `held`; the contract requires the flag to exist and be honoured by the
  later module, not that either value be computed now.
- **Couples and singles opportunity shares kept separable, never pre-pooled.** The
  pinned/degenerate couples-male leisure preference (`beta_l0_m` at floor)
  mechanically compresses the couples preference component, which would inflate the
  couples opportunity share for a non-structural reason if pooled with singles
  (`JMP_welfare_spec_v5.md` §3a). The outputs MUST keep singles and couples
  opportunity shares separable; the scaffold MUST NOT emit a single pooled
  opportunity-share object (`unit.pool_opportunity_share: false`).

These are interface guarantees only — shapes, flags, and separability — not
decomposition computations.

---

## 8. Inference hooks

- **Cluster-robust bootstrap on `idorighh`** (9,657 clusters at the certified
  baseline) is the inference procedure of record. The scaffold is invocable as a
  pure function of a single `theta_hat`; the bootstrap orchestration is external and
  calls the scaffold once per replicate. The scaffold holds no state across
  invocations.
- **Per-measure welfare uncertainty now.** This contract requires per-measure
  bootstrap CIs on each measure's welfare distribution / inequality `I(Omega^k)`.
- **Per-component CIs are a downstream decomposition-interface requirement, not
  implemented here.** The decomposition contract will require cluster-robust CIs on
  each access/ability/preference component; this contract only guarantees the
  outputs and the bootstrap entry point support that later.
- **No asymptotic SEs for headline claims.** Three params sit at bounds at the
  certified baseline (`beta_l0_m` lo, `beta_l_age2_sf` hi, `beta_l_age2_f` hi),
  where asymptotic SEs are invalid; the bootstrap is the inference procedure.
  Pinned params (`theta_l_m`, `beta_ll`) carry zero uncertainty by construction and
  are held fixed across replicates.
- **Bootstrap cost scales with menu size.** Each replicate recomputes every active
  measure; cost ≈ `n_replicates × |active measures| × per-measure inversion cost`.
  This is a compute-budget item the orchestration must account for, recorded here so
  the menu length is a known cost driver. Opportunity-content CIs are expected
  **tighter** than preference CIs (the opportunity blocks are an order of magnitude
  more precisely estimated than the leisure blocks — `JMP_welfare_spec_v5.md` §3b);
  the scaffold states this expectation, it does not assert it as a result.

---

## 9. Forbidden items

Beyond the execution / code-write / implementation / number-computation bans
already stated (no implementation, no estimation, no welfare or decomposition
numbers, no bootstrap run, no data rebuild):

- **No hardcoded France/2016/P3a constants** anywhere in the welfare source. Block
  membership, references (`Ā`, `J`, `o`), the cross-section filter, the reference
  preference, the cluster unit, the fixed params, and the active measure set are
  all read from config. Specification-identifying strings live only in config and
  in the cited spec/parquet. Zero such strings in the code is the agnosticism test.
- **Occupation is never called "sector" or "industry."** The occupation block is
  occupation (task-content availability conditional on an offer); the naming is
  fixed.
- **The `W^1`/`W^5` dual is corroborating interpretation, not a numerical
  reconciliation gate.** `W^1` and `W^5` are different money metrics with different
  references; their inequality gap is not equal to any single measure's
  decomposition components, and there is no theorem equating them. Report the dual
  spread alongside the decomposition as interpretation; **do not** write it in as a
  reconciliation/identity gate (`JMP_welfare_spec_v5.md` §6).
- **No `beta_h_pt2` gendered offer parameter** in any measure. Baseline welfare uses
  **shared** offer parameters; `beta_h_pt2` is excluded from any identified gendered
  path (independent mislocation, not reparameterisable —
  `RURO_gsplit_nonid_structure_v1.md`). A future `beta_E` contrast swap is a
  deferred config change, not part of this contract.
- **No couple splitting and no intra-household equivalisation** — the unit is the
  household; both are deferred.
- **No pooled opportunity-share headline** that merges singles and couples (§7,
  `JMP_welfare_spec_v5.md` §3a).

---

Keep the implementation country/year/spec-agnostic throughout: the welfare code is
a measure machine pointed at a certified `theta_hat` and an engine-ready dataset via
config; the certified 47-param France/2016–2017/P3a baseline is the *current* input,
not a constant in the code.

**Save this as `docs/jmp_methodology/RURO_welfare_scaffold_design_contract_v2.md`.**
