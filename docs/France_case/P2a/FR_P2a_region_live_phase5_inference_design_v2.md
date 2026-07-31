# FR P2a Region-Live — Phase-5 Inference Design — v2

**Mission:** JMP-M05 Stage D, remediation cycle 1 of 2 — household-clustered inference design
**Mode:** design only; no implementation, no computation, no commit
**Date:** 2026-07-31
**Target repository path:** `MNL/docs/France_case/P2a/FR_P2a_region_live_phase5_inference_design_v2.md`
**Supersedes:** `FR_P2a_region_live_phase5_inference_design_v1.md`, which is **retained unedited** as the object the Stage-C review cites (ruling R-12). v1 is not amended in place.
**Remediation authority:** `JMP_M05_stageD_cycle1_instruction_v1.md` (rulings R-11–R-12), implementing fixes 1–7 of `FR_P2a_region_live_phase5_inference_methods_review_v1.md` §17, verdict `APPROVE AFTER FIXES`.
**Commit status:** UNCOMMITTED pending the targeted Stage-C recheck and Stage-E manager acceptance

**Citation convention.** Every factual claim about the likelihood, parameters, bounds, pins, clusters, weights, regional covariates, bread, or environment carries a bracketed source, or is marked `UNKNOWN`. `[audit §N]` = `FR_P2a_region_live_phase5_source_verification_v1.md`; `[map]` = `phase5_parameter_map_v1.csv`; `[inv]` = `phase5_source_inventory_v1.json`; `[P4D]` = `phase4_diagnostics.json`; `[P4A §N]` = `FR_P2a_region_live_phase4_manager_acceptance_v1.md`; `[charter §N]` = `JMP_M05_phase5_inference_mission_charter_v1.md`; `[plan §N]` = `JMP_M05_task_plan_v1.md`; `[C-n]` = binding corrections of `JMP_M05_task_plan_manager_acceptance_v1.md`; `[F-n]`, `[ERR-n]` = ratified findings and errata of `JMP_M05_mission_ledger_v2.md` §3–§4; `[CS §N]` = `JMP_canonical_state_v1.md`; `[DL]` = `JMP_decision_log_v1.md`. Arithmetic performed on already-published accepted values is labelled **[arith]** and is not a Phase-5 computation.

---

## 1. Design verdict

**READY WITH OPEN DECISIONS**

Every decision the charter §9 requires has exactly one recommended baseline, with rejected alternatives named, rejection reasons given, and a pre-registered falsification criterion attached. No charter §13 halt fires and no plan §15 `HM-*` halt fires. The design is complete on its statistical axis and implementable as written. The Stage-C independent review returned `APPROVE AFTER FIXES` with no E2 finding and confirmed that no residual defect required changing the accepted model, the accepted estimate, the conditional estimand, or the Phase-5 baseline [review §1, §16]. All seven required fixes are implemented in this version (§1.1).

The verdict string is unchanged from v1, but the composition of what is open has changed materially. The v1 reason that has **closed**: the [C-4] mandate for independent review of the 35-dimensional conditional covariance is discharged — the Stage-C review ruled the conditional-35 object defensible for the stated estimand and stated that the central D-2 decision may be frozen once the fixes are incorporated and rechecked [review §9, §18].

Three items remain open, none derivational:

1. **The targeted Stage-C recheck has not been performed.** The review conditions manager acceptance on a recheck confirming eight specific properties of the corrected text [review §18]. This memo implements the fixes; it does not and cannot certify that the recheck passed. That determination is the reviewer's.
2. **One `UNKNOWN` conditions the score-artifact disclosure route.** Whether household-level derived arrays from EU-SILC/EUROMOD input data may be committed to version control depends on the licence terms and the repository's disclosure status. Neither is a repository fact the Stage-A audit established, so it is `UNKNOWN` here, and the review explicitly leaves the licence question to the principal investigator [review §13]. The durable restricted-custody requirements are now specified **unconditionally** (§17.1, §18.5), so the design is complete under either outcome and execution cannot be blocked by the determination.
3. **Ratification of the canonical row order (D-7) is still requested**, because the audit required the memo to fix one of two candidate orders and the choice determines every artifact hash (§22).

Nothing else is open. In particular, `ln(101)` is not restated in any form [F-1]; no pin is assigned a normalisation category [F-2]; `gsur` is treated as a continuous rate distinct from the NUTS-1 dummy set [F-3]; `hessian_free.npy` is named the sole authoritative bread [F-4]; and symmetrisation on load against the recorded threshold is mandated [F-5].

### 1.1 Revision register (v1 → v2)

Every change from v1 is listed below. No change was made outside these rows [Stage-D instruction §3]. No recommended baseline changed in substance and no gate was weakened; the fixes alter justification, precision of claims, dimensional explicitness, schema completeness, tolerance tightness, language discipline, and fallback custody [Stage-D instruction §2].

| Fix | Requirement (review §17) | Sections and subsections changed in v2 |
| --- | --- | --- |
| **F1** | Restrict the Loewner claim to model-based inverse-information objects; delete the robust-SE extension and every known-direction downstream-uncertainty claim; recast T-22 as sample numerical KKT evidence; adopt the two-tier downstream trigger of review §9 | §11.2 (third bullet rewritten; new fourth bullet on what is *not* ordered); §11.5 (T-22 recast); §15 (T-22 row); §16.2 (T-22 row renamed); §19 (downstream declaration and trigger rewritten) |
| **F2** | Define `K = 35` as the local dimension/rank of the restricted estimating problem under strict activity; present `c` as a pre-registered HC1/CR1-style regression-analogue convention; remove "exactly-satisfied" score-equation reliance and the referee-expectation claim; scalar unchanged | §10.3 (rewritten); §10.4 (CR0 and `K = 37` rejection reasons rewritten); §10.6 (falsification criterion restated in dimension/rank terms) |
| **F3** | Make every regional Wald object dimensionally explicit: `E_R ∈ ℝ^{10×35}`, `V_RR = E_R V_I E_R'`, `A ∈ ℝ^{q×10}`, `r`, the solve, name-keyed rows for H0-A/B/C/G, separate `p_model` / `p_robust` | §13.4 (statistic, selector algebra and null table rewritten); §17.2 (`phase5_regional_tests.csv` field list) |
| **F4** | Reconcile boundary reporting with the exact artifact schema: add `bound_value`, `bound_side`, `grad_negll`, `multiplier`; remove or define the stray `flag`; five inferential fields stay literal `NA` | §11.3 (reporting sentence bound to the §17.3 schema); §12.2 (pin baseline aligned to the schema field names); §17.2 (parameter-table row); §17.3 (exact 13-column schema and population rules; `flag` removed in favour of `status`) |
| **F5** | Repair gate definitions: T-4 as the signed max-norm identity; T-7/T-9 PSD no looser than the `1e-10` rank convention unless quantitatively justified; W-4 on the robust 95 % interval with equality-to-bound triggering | §14 (T-4 row); §15 (T-7, T-9, W-4 rows); §11.5 (W-4 statement); §16.2 (PSD rows rewritten with a quantified backward-error bound, the erroneous "one order looser" sentence removed, and a W-4 critical-value row added) |
| **F6** | Restore language discipline: conditional couples/pooled degeneracy; H0-B as the common NUTS-1 intercept component; sweep for equivalent wording | §6.2 (symmetric conditional statement); §11.6 (absorption wording narrowed); §13.4 (H0-B description); §19 (opportunity-channel wording); §20.3 (`will break` → conditional) |
| **F7** | Complete the disclosure fallback: durable, access-controlled, immutable restricted custody with locator, SHA-256, size, shape, row/column fingerprints, `disclosure_class`, retention responsibility recorded in the manifest | §17.1 (fallback rewritten); §17.2 (manifest custody block); §18.5 (manifest mandate extended); §15 (new gate T-23) |
| **C-a** | Consequential, entailed by F1 and F6 | §20.2 (claims-register lines on the Loewner ordering, downstream-uncertainty direction, and future clustering rewritten); §20.1 (permitted-claim line on conditionality) |
| **C-b** | Consequential, required by Stage-D instruction §3 | §22 (decision statuses and open-item register updated to the post-review state) |
| **C-c** | Consequential, required by Stage-D instruction §3 | §1 (verdict re-derived from the post-review state); §1.1 (this register, new) |
| **C-d** | Consequential, required by ruling R-12 | Front matter (version, supersession note, remediation authority, commit status) |
| **C-e** | Consequential, entailed by the completion of Stage C: v1's §23 described Stage C as upcoming and recorded zero remediation cycles used, both of which are now false | §23 (process position, return contract, and gating condition corrected) |

Two review observations required no edit and are recorded here for the recheck's convenience: the Stage-C attachment limitation for the Phase-3/Phase-4 memos and `phase4_diagnostics.json` is explicitly not charged against this memo [review §3]; and the decision not to centre the meat, the forward-mode score route, the 64-household cross-mode check, the canonical row order, the bread sourcing chain, and the pin treatment were all reviewed as correct and are carried forward unchanged [review §4, §5, §6, §7, §10, §13].

---

## 2. Scope

**In scope.** The definition, construction, validation, certification and reporting contract for: the 1,555 × 37 household score matrix; the model-based covariance; the household-clustered robust sandwich; the finite-sample correction; the treatment of the two active-bound coordinates; the treatment of the ten fixed pins; individual and joint inference for the ten regional/urbanisation/GSUR access coordinates; the numerical gate register with exact tolerances; the immutable output bundle; and the transaction and execution contract for the follow-on implementation mission.

**Out of scope, and not performed in producing this memo** [charter §6]: implementation; computation of any score, covariance, standard error, confidence interval, test statistic or p-value; any optimizer, gradient, Hessian, post-estimation, welfare, decomposition, synthetic-recovery, EUROMOD or notebook run; any alteration of the accepted estimate or artifacts; any respecification of the RURO model; any broadening to couples, pooled years, or other countries; any commit.

**One operational consequence, stated explicitly** [plan §2.5]: **the bread may not be recomputed.** Recomputing the Hessian would constitute invoking the Hessian. It must be loaded from the accepted Phase-4 bundle under hash verification (§8, §15 T-5).

**Language discipline carried throughout** [C-2, C-5]: this memo distinguishes (i) regional/urbanisation/GSUR access-block inference, (ii) the full opportunity mechanism, and (iii) the later welfare decomposition. The ten-coordinate block is not the complete opportunity mechanism: the opportunity index `log_market` additionally carries six occupation coordinates, the separate `log_h` block carries five hours-offer coordinates, and `log_w` carries six wage-density coordinates [audit §15].

---

## 3. Accepted dependencies

### 3.1 Binding revisions

| Item | Value | Source |
| --- | --- | --- |
| MNL canonical checkpoint | `982c52217031158c4a2368709d4a6b211ebcde76` | [audit §3], [CS] |
| MNL Phase-4 execution revision | `fee60723ed27d6979976a3dc85b09cde3096e011` | [audit §5] |
| Nested `dclaborsupply` HEAD = MNL gitlink | `27756a06ea189339aa82915ed2124628afed20eb` | [audit §3] |
| Descendancy `982c5221…` ⊃ `fee60723…` | verified, exactly one intervening commit | [audit §5] |

Phase 5 must execute at MNL `982c5221…` with gitlink `27756a06…`. No source, config, spec, or theta file changed between the execution revision and the checkpoint [audit §5].

### 3.2 Accepted bundles and artifacts

| Object | SHA-256 | Source |
| --- | --- | --- |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | [audit §18] |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | [audit §16] |
| **`hessian_free.npy`** (authoritative bread) | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | [audit §16], [F-4] |
| `hessian_free.csv` (rendering, **not** authoritative) | `8985b619858ce8b6c5f4bbb2700bfbb7c22333c17538cc1eb8dc5b09b58f470e` | [audit §16] |
| Accepted θ̂ (47-vector bytes) | `c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d` | [audit §18], [P4D] |
| Certified spec YAML | `492bcfa9c766bfcb5d8536f5e920cc0b00ffa600b7b89db60b250365f331f211` | [audit §6] |

Accepted negLL `19053.46553160093`; accepted free Hessian 37 × 37, rank 37, strictly positive definite, `min_eig 0.1037326963880782`, `max_eig 42048.457934380494`, condition number `405353.94719781954`, tier `clean` [P4D], [P4A §6–§7].

### 3.3 Verified structural facts consumed by this design

| Fact | Value | Source |
| --- | --- | --- |
| Additive likelihood terms | 1,555 (714 male + 841 female) | [audit §13] |
| Alternatives per term | 101; `157,055 = 1,555 × 101` exactly | [audit §13] |
| Objective scaling | **unweighted sum**; `dwt` present in the stem but never read | [audit §12] |
| Cluster identity | `cluster_id = idorighh = idhh` elementwise at group starts; 1,555 unique | [audit §14] |
| Clustering status | **degenerate** — exactly one term per cluster | [audit §13], [inv] |
| Score hook | `build_jax_singles_ll(..., per_group=True)` returns the `(n_groups,)` **positive** log-likelihood vector | [audit §10] |
| Free-vector dimension | 37; ten pins removed from the optimization vector entirely in Phase 3 | [audit §6.2], [audit §8] |
| Active set | `beta_l_age2_sm` (free 2), `beta_l_age2_sf` (free 6), both at **upper** bound `1.0` | [audit §8], [ERR-1] |
| float64 | source-established at `engine_jax.py::_load_jax()`, before every array creation on the accepted route | [audit §17] |

### 3.4 Permanent `UNKNOWN`s inherited

JAX/jaxlib versions, platform string, and thread/XLA flag settings at Phase-3/4 execution time; SciPy version at Phase-3 execution time [audit §19]. These were never recorded and are unrecoverable by static inspection. They do not block this design: the `1e-8` identity tolerance depends on float64, which is established from source and not from a version string [audit §17]. Phase-5 execution must not inherit this gap — the manifest requirement in §18.5 closes it going forward.

---

## 4. Inferential target

Phase 5 quantifies the **sampling variability of the accepted estimator at the accepted estimate**, for the France 2016 singles P2a region-live application, under household-clustered misspecification-robust asymptotics.

Formally, the target is the asymptotic covariance of the interior subvector of the constrained quasi-maximum-likelihood estimator, and the associated Wald objects for the regional/access block. Because the constrained estimator's probability limit is a pseudo-true value under possible misspecification, the sandwich — not the inverse information — is the object with the correct interpretation, and the model-based covariance is retained as a specification diagnostic rather than as the headline (§8, §9).

Three things the target is **not**:

- **Not identification certification.** Phase 4 delivered real-data *local* identification at a point estimate [P4A §14]. Precision is not identification.
- **Not structural recovery.** Synthetic recovery is separate and mandatory [DL D-009], [P4A §16] (§19).
- **Not a decomposition or welfare statement.** Welfare and decomposition remain non-reportable on P2a [CS §10], [P4A §17], [DL D-010].

The mission's most consequential single output is the regional/access block's joint inferential statement [plan §2.3, §9.1], delivered under the language discipline of [C-2] and [C-5]: it is a statement about the modelled regional/urbanisation/GSUR access block, not about the opportunity mechanism as a whole and not about the decomposition share.

---

## 5. Household score definition

### 5.1 Reparameterisation, stated exactly

Let θ ∈ ℝ⁴⁷ be the full parameter vector in the certified order [audit §6.1]. Let

- 𝒫 = {10, 11, 12, 13, 14, 15, 16, 17, 31, 32} — the ten pinned full indices (0-based) [audit §6.2],
- ℱ = {0,…,46} \ 𝒫 — the 37 free full indices, order preserved.

Define the **pin-fixed injection** ι : ℝ³⁷ → ℝ⁴⁷ by

```
ι(x)_i = x_{k(i)}   if i ∈ ℱ,  where k(i) is the free position of full index i
ι(x)_i = p_i        if i ∈ 𝒫,  where p_i is the accepted pin value
```

This is the exact production route: `base_full` is the 47-vector carrying pins at their pin values, and `base_full.at[free_idx].set(x_free)` installs the free coordinates [audit §10]. **It is a reparameterisation with pins held constant, not a 47-vector projection with zeros** — a 47-vector with zeros in the pinned slots would evaluate a different objective [audit §10]. Every derivative below is taken with respect to `x ∈ ℝ³⁷` through ι, so pins never enter differentiation: `∂/∂x_k = Σ_i (∂ι_i/∂x_k) ∂/∂θ_i = ∂/∂θ_{ℱ(k)}`, and the pinned coordinates contribute no term because `∂ι_i/∂x_k = 0` for `i ∈ 𝒫`.

### 5.2 Household contribution

For household `g ∈ {1,…,G}`, `G = 1,555`, with 101 alternatives indexed by `j` [audit §13]:

```
V_gj(x) = u_gj + log_h_gj + log_w_gj + log_market_gj − log_prior_gj
ℓ_g(x)  = V_{g,0}(x) − logsumexp_j V_gj(x)                        ≤ 0
negLL(x) = − Σ_{g=1}^{G} ℓ_g(x)
```

with `V_{g,0}` the chosen alternative under the verified column-0 convention (`use_actual_choice=False`; `_validate_chosen_first` proves exactly one chosen alternative per group and that it is the group's first row) [audit §11].

**The household contribution is exactly ONE additive term.** It is not a sum of separable components. The wage density, hours-offer, market/regional, occupation and prior-correction terms all enter *inside* the index `V_gj`, are alternative-specific, and therefore do not cancel between `V_{g,0}` and the log-sum-exp. Any derivation writing `ℓ_g` as "choice term + wage-density term" is wrong for this model [audit §11], [F-1]. No statement anywhere in this design rests on the average negLL, and the `ln(101)` comparison is not restated in any form [F-1], [C-1].

### 5.3 Score, sign convention, and the frozen identity

The **household score** is the gradient of the **positive log-likelihood** contribution:

```
s_g(x) = ∇_x ℓ_g(x) ∈ ℝ³⁷
S      = [ s_1' ; s_2' ; … ; s_G' ] ∈ ℝ^{1555×37}
```

The sign convention is fixed once, here, for the whole document and for the implementation:

| Object | Definition | Sign |
| --- | --- | --- |
| `s_g` | ∇ log-likelihood | as stored |
| `H` | ∇² negLL = observed information | positive definite [P4D] |
| `M` | Σ_g s_g s_g′ | invariant to the sign of `s_g` |

The meat is invariant to the score's sign because it is an outer product; the only sign hazard is loading a log-likelihood Hessian in place of a negLL Hessian, which gate T-6 catches (a negated matrix has `min_eig < 0`).

Because the objective is a verified **unweighted sum** over households with no per-observation scaling and no survey weight [audit §12], the charter-frozen identity holds with matched scaling and **no correction factor**:

```
Σ_{g=1}^{G} s_g = ∇_x Σ_g ℓ_g = − ∇_x negLL
```

This is a **verified**, not an assumed, property [audit §12], [charter §8]. Its operational form is gate T-1:

```
np.allclose(S.sum(axis=0), -gradient_free_accepted, atol=1e-8, rtol=1e-8)
```

where `gradient_free_accepted` is the recorded 37-element `gradient_free` of `phase4_diagnostics.json` [P4D]. Comparing against the *recorded* gradient rather than a freshly evaluated one is deliberate: it tests the score route and reproduces Phase 4's accepted gradient in a single check, and it avoids a new gradient evaluation. Phase 4's gradient itself reproduced the published Phase-3 free-gradient projection to `8.881784197001252e-16` [P4D], so this closes a three-phase chain of custody.

### 5.4 Efficient construction route — recommended baseline

**Baseline: `jax.jacfwd` of the verified `per_group=True` vector, evaluated over household-blocked chunks, stacked in canonical row order.**

The construction uses the production hook and requires no new likelihood code [audit §10]:

1. For each builder (male, 714 groups; female, 841 groups [audit §13]), obtain the per-group **positive** log-likelihood vector via `build_jax_singles_ll(..., per_group=True)` [audit §10].
2. Wrap it in the same pin-fixed free-coordinate reparameterisation Phase 4 used (`negll_free`-style, `base_full.at[free_idx].set(x_free)`) [audit §10], so that Phase 5 differentiates exactly the object Phase 3 estimated and Phase 4 diagnosed.
3. Take `jax.jacfwd` of that map, ℝ³⁷ → ℝ^{n_chunk}, over chunks of whole households.
4. Concatenate chunks, then stack male and female blocks, then apply the canonical row permutation (§6.3).

**Why forward mode.** The Jacobian is tall and thin: 1,555 outputs, 37 inputs. Forward mode costs O(37) JVP passes; reverse mode costs O(1,555) VJP passes. Forward mode is the appropriate mode whenever the input dimension is far below the output dimension. The module docstring's statement that `jax.jacrev` of the per-group vector is the score matrix [audit §10] is correct and is not contradicted here — the choice is one of cost and memory, not of correctness, and T-16 pre-registers a subset agreement check between the two modes.

**Why chunked.** A single `jacrev` call over 714 or 841 outputs materialises cotangent-space intermediates once per output row; with 72,114 and 84,941 rows respectively this is an order-of-magnitude-gigabyte peak and is precisely the memory-unsafe route requirement A excludes. Chunking by **whole households** is exact rather than approximate, because `ℓ_g` depends only on group `g`'s rows: the log-sum-exp is within-group, and the proposal-weighted `log_market` centering is *within-choice-set* [audit §11]. No term couples households. Chunk size `C` is a free implementation constant; it is recorded in the manifest and gated by T-11.

*The memory figures in this subsection are design-time order-of-magnitude estimates from the verified row counts, not measurements. Peak memory at execution is `UNKNOWN` and must be recorded in the Phase-5 manifest (§18.5).*

**Rejected alternatives.**

| Rejected | Reason |
| --- | --- |
| Single-call `jax.jacrev` over all outputs, unchunked | Peak memory scales with (#outputs × per-pass intermediate size); this is the memory-unsafe route requirement A excludes. |
| Row-level Jacobian, 157,055 × 37 | **Undefined for this likelihood.** There is no row-level additive log-likelihood term; the household contribution is exactly one additive term [audit §11], [F-1]. Even as a formal object it would require 157,055 reverse passes. |
| Finite differences over 37 coordinates | Introduces truncation error at the `1e-8` identity tolerance for no benefit; exact AD is available on the accepted route. |
| Re-deriving `ℓ_g` analytically and coding a bespoke score | Would place a second, unverified likelihood implementation beside the accepted one; the production hook already exists [audit §10]. |

**Pre-registered falsification criterion (route).** If T-1 fails at the frozen tolerance, or if T-16 shows `jacfwd`/`jacrev` disagreement above `1e-10 · max|S|` on the subset, the forward-mode chunked route is falsified: the implementation halts, does not fall back silently, and returns to the manager with the deviation recorded. It does not "fix" the discrepancy by loosening a tolerance.

---

## 6. Cluster definition

### 6.1 Contract

The inferential cluster is the household `idhh`. `G = 1,555` exactly [DL D-008], [charter §8]. All 101 alternatives of a household belong to one contribution and are never split across clusters.

Verified mechanism [audit §14]: the loader sorts by `idhh` with a stable mergesort, derives group boundaries from value changes, and takes both `group_ids` and `cluster_ids` at the *same* `starts` indices of the *same* sorted frame. Alignment is therefore a shared group-boundary array, not a re-merge or a re-sort. Verified counts: `nunique(idhh) = nunique(idorighh) = nunique(cluster_id) = 1,555`; 101 rows per household for every household; exactly one chosen row per household; `cluster_id == idhh == idorighh` elementwise at group starts; no missing or non-finite cluster ids; male/female split 714/841 [audit §14].

**Rejected clusterings**, each explicitly: row/alternative clustering (157,055 rows are not independent observations — they are the alternatives of a single multinomial contribution, already integrated out inside `ℓ_g` [audit §13]); person clustering (identical to household here — singles, one decision-maker per household [audit §13] — and so not a distinct object); region clustering (would impose a dependence structure the likelihood does not contain, and would collapse `G` to 8, entering the small-cluster regime the design explicitly avoids); year clustering (single year, `G = 1`, degenerate and meaningless); occupation or urbanisation clustering (same objection as region).

### 6.2 Degeneracy, and the terminology it licenses

Exactly one likelihood term per cluster [audit §13], [inv]. The cluster score is `s_j = Σ_{g ∈ cluster j} s_g`, and with a single `g` per cluster `s_j = s_g`, so

```
Σ_j s_j s_j′ = Σ_g s_g s_g′
```

The household-cluster sandwich is therefore **algebraically identical** to the household-level outer-product-of-gradients sandwich **in this application** [audit §13].

Terminology, fixed here under [C-3]: the estimator is described as **household-clustered and misspecification-robust**, and the algebraic equivalence to the OPG sandwich is stated wherever the estimator is named. The sandwich is misspecification-robust, **not dependence-robust**: with one term per cluster, clustering removes no dependence, because there is none across contributions to remove [audit §13]. **No claim is made in either direction about couples or pooled years.** Whether clustering remains degenerate or becomes binding in those applications is conditional on how their primitive likelihood contributions and repeated-unit structure are defined, which is not settled by anything in this application [C-3], [review §5].

*Inventory note, not an instruction:* the package ships `dclaborsupply/se/cluster_robust.py` whose `run_t3_cluster_count_check` default is `expected=9657`, a P3a-pooled constant that does not apply here; the P2a policy is auto-resolution of unique non-missing `idorighh`, never 9657 [audit §13]. Gate T-3 must assert 1,555 explicitly and must not rely on a library default.

### 6.3 Canonical row order — decision

The audit records two candidate orders and requires the memo to fix one [audit §14]: (a) builder concatenation, male block then female block; (b) `idhh`-ascending across both genders, obtained by a stable argsort of the concatenated group ids — the order Phase 4's accepted regional design uses.

**Baseline: order (b), `idhh`-ascending, stable argsort.** Grounds: it row-aligns the score matrix with the accepted 1,555 × 10 Phase-4 regional design without any further re-sort [P4A §8]; it is reproducible from `idhh` alone, so the artifact does not encode the male/female split as a structural feature; and it is stable under any future change to builder invocation order.

**This choice has no effect on any reported statistic.** `Σ_g s_g` and `Σ_g s_g s_g′` are permutation-invariant. It affects only the artifact bytes, its hash, and joinability — which is exactly why it must be fixed rather than left implicit. Floating-point summation order induces differences of order machine-epsilon × G, roughly 15 orders of magnitude below the T-1 gate.

**Rejected:** order (a), on the ground that it silently encodes a builder-invocation convention into a certified artifact.

**Pre-registered falsification criterion.** T-3 requires that the stored `cluster_id` column be strictly increasing and equal, elementwise, to `np.sort(np.unique(idhh))`. Failure halts.

---

## 7. Parameter ordering and mapping

### 7.1 Sources and status

Ordering is established **by name** from two independently agreeing committed sources — `EstimationSpec.all_param_names` built from the certified spec YAML, and `phase4_manifest.json → contract.parameter_map`, which publishes `all_names`, `free_names`, `pin_names`, `free_indices`, `pin_indices`, `pin_values` verbatim with round-trip proofs [audit §6]. The Phase-4 runner asserts `list(theta_estimated.csv["param"]) == names` before proceeding [audit §6]. `HM-MAP` does not fire.

Status counts, verified [map]: **35 interior + 2 active_bound + 10 pinned = 47.**

### 7.2 The three index spaces

| Space | Dim | Definition |
| --- | --- | --- |
| Full θ | 47 | certified spec order [audit §6.1] |
| Free `x` | 37 | delete pinned full indices `{10,11,12,13,14,15,16,17,31,32}`, order preserved [audit §6.2] |
| Interior `x_I` | 35 | delete free positions `{2, 6}` **by name** (`beta_l_age2_sm`, `beta_l_age2_sf`) [audit §7] |

Write `𝒜 = {2, 6}` (free, 0-based) for the active set and `ℐ` for its complement, `|ℐ| = 35`.

**Every index map is taken by name, never by arithmetic** [plan S-1]. The implementation must key on `phase5_parameter_map_v1.csv` and assert name equality at each projection; a positional derivation that happens to agree is not acceptable evidence.

### 7.3 Regional/access block positions (by name)

| Design column | Parameter | Full | Free | Interior | Accepted value |
| --- | --- | --- | --- | --- | --- |
| `gsur` | `beta_E_gsur` | 23 | 15 | 13 | `−1.104768` |
| `reg2` | `beta_E_drgn2` | 24 | 16 | 14 | `−0.205036` |
| `reg3` | `beta_E_drgn3` | 25 | 17 | 15 | `−0.088528` |
| `reg4` | `beta_E_drgn4` | 26 | 18 | 16 | `−0.689727` |
| `reg5` | `beta_E_drgn5` | 27 | 19 | 17 | `−0.265395` |
| `reg6` | `beta_E_drgn6` | 28 | 20 | 18 | `−0.521941` |
| `reg7` | `beta_E_drgn7` | 29 | 21 | 19 | `−0.387714` |
| `reg8` | `beta_E_drgn8` | 30 | 22 | 20 | `−0.308744` |
| `drgur` | `beta_E_drgur` | 33 | 23 | 21 | `−0.010019` |
| `drgmd` | `beta_E_drgmd` | 34 | 24 | 22 | `+0.108673` |

Free positions 15–24 match `phase4_diagnostics.json → regional.regional_positions_free` exactly [audit §7], [P4D]. Accepted values are from [map] and carry **no inferential statement** at this stage; they are listed so that the reporting table's construction is unambiguous. Note for the reporting contract: magnitudes are not directly comparable across the block, because `gsur` enters as `beta_E_gsur · (10.0 · gsur · working)` with a `variable_scales` factor of 10 and a `working` gate, while the dummies enter as `beta · (indicator · working)` [audit §15].

### 7.4 Parameter-order fingerprint

Gate T-17 requires a fingerprint that binds every downstream object to this ordering: the SHA-256 of the newline-joined ordered 37 `free_names`, and separately of the ordered 35 interior names, recorded in the Phase-5 manifest and asserted equal to the values recomputed from `phase4_manifest.json → contract.parameter_map` at load. Positional agreement without name agreement is a T-17 failure.

---

## 8. Model-based covariance

### 8.1 Bread: loaded, symmetrised, restricted

```
H     ← np.load("hessian_free.npy")              # 37×37 float64 C-contiguous, raw
assert sha256(file) == e9ca080e…                 # T-5
assert max|H − Hᵀ| ≤ 2.3588019878151842e-4       # T-6, recorded threshold
Hs    = (H + Hᵀ)/2                               # T-6, mandatory
H_II  = Hs[ℐ, ℐ]                                 # 35×35, by name
```

Three points, each load-bearing.

1. **`hessian_free.npy` is the sole authoritative bread** [F-4]. `hessian_free.csv` differs from it in 337 of 1,369 entries at up to `1.8189894035458565e-12` absolute / `4.649896209284979e-13` relative, because the CSV is written at pandas' default float formatting and does not round-trip float64 exactly [audit §16]. All fingerprint gates bind to the `.npy`.
2. **Symmetrisation on load is mandatory** [F-5]. The bundle persists the raw, unsymmetrised `H`; the `Hs` that Phase 4 used for its eigenspectrum, loading shares, regional subblock and Schur complement is **not persisted anywhere** [audit §16]. A Phase 5 that skipped this step would not be using the object Phase 4 accepted. The recorded asymmetry is `1.8189894035458565e-12` against a threshold of `2.3588019878151842e-4` [P4D].
3. **The bread is not recomputed** [plan §2.5]. Recomputation would constitute invoking the Hessian, which charter §6 forbids.

### 8.2 The covariance and why no extra scaling appears

```
B = H_II⁻¹        obtained as cho_solve(cho_factor(H_II), I₃₅)
V_model = B
```

`negLL` is an unweighted **sum** over households [audit §12], so `H` is the sum-scale observed information and `H⁻¹` already carries the `1/G` implicitly. Any additional `1/G` or `G` factor is a double count. The equivalence is exact: writing `Ā = H/G` and `M̄ = M/G` for the average-scale objects, the textbook form gives

```
(1/G) · Ā⁻¹ M̄ Ā⁻¹ = (1/G) · (G H⁻¹)(M/G)(G H⁻¹) = H⁻¹ M H⁻¹
```

identically. **No sample scaling is applied at any point** [charter, requirement C].

### 8.3 Solve discipline

Every inverse-like operation is a factorisation-based solve — Cholesky where the matrix is symmetric positive definite, never an explicit `inv()` [charter §10]. This follows the accepted Phase-4 precedent, in which the Schur-complement solve agreed with a pseudo-inverse reference to `8.526512829121202e-14` [P4D]. Gate T-8 re-imposes that discipline with a `1e-8` bar. `H_II` is a principal submatrix of a positive-definite matrix and is therefore positive definite by construction; a Cholesky failure at T-6 is evidence of an implementation error, which is exactly what the gate is for.

### 8.4 Status of the model-based object

`V_model` is reported for every interior parameter, but it is **not** the certified headline. Under possible misspecification the information-matrix equality fails and `H_II⁻¹` is not the estimator's asymptotic covariance; the sandwich is (§9). `V_model` earns its place as the denominator of the robust/model ratio, which is the design's principal specification diagnostic (W-1).

---

## 9. Cluster-robust covariance

### 9.1 Definition

```
S_I = S[:, ℐ]                       # 1555×35, by-name column selection
M   = S_Iᵀ S_I = Σ_g s_{g,ℐ} s_{g,ℐ}ᵀ        # 35×35
B   = H_II⁻¹                                  # §8.2
V_robust = c · B M B                          # c per §10
```

with `M` symmetrised after gate T-7 (`M ← (M + Mᵀ)/2`) to remove accumulation asymmetry, and `B M B` formed by two solves rather than by materialising `B` where the implementation permits.

**Column selection is exact, not approximate.** `s_{g,ℐ} = ∂ℓ_g/∂x_ℐ` evaluated at `(x̂_ℐ, x̂_𝒜 = 1.0)`; holding `x_𝒜` fixed does not change partial derivatives with respect to the other coordinates. The 1,555 × 37 matrix is therefore the stored primitive and the 1,555 × 35 matrix is a derived by-name selection [plan §10.2(1)], with T-1 verified on the full 37 columns *before* selection.

### 9.2 Centring — decision

**Baseline: do not centre the meat.** The uncentred OPG is the standard estimator and, at an interior optimum of the restricted problem, `Σ_g s_{g,ℐ} = 0` exactly in population terms, so centring is a null operation up to the numerical residual. That residual is published: `max |Σ_g s_{g,ℐ}| = 1.0992597206183063e-4` at `beta_w_educH` [P4D], [audit §8]. **Rejected:** centring, on the ground that it would subtract a quantity that is asymptotically zero and would introduce a second, non-standard meat definition into a certified artifact. The magnitude of the correction that is *not* applied is nonetheless recorded as diagnostic W-5, so that the choice is visible rather than implicit.

### 9.3 Rank and conditioning

`M` is a sum of `G = 1,555` rank-one outer products in 35 dimensions, so generic full rank 35 is expected and rank deficiency does not arise — the small-`G` pathology that motivates leverage-corrected or bootstrap alternatives is absent at `G/K ≈ 44` [arith]. Gate T-7 records the rank and eigenspectrum; diagnostic W-3 reports effective rank relative to 35.

---

## 10. Finite-sample correction

### 10.1 Recommended baseline

**Baseline: the two-factor correction, with `N = G = 1,555` and `K = 35`:**

```
c = [G/(G−1)] · [(N−1)/(N−K)] = [1555/1554] · [1554/1520] = 1555/1520
  = 1.0230263157894737
√c = 1.0114476337        →  +1.1448 % on every standard error          [arith]
```

### 10.2 The telescoping, stated once

Because `N = G` is a **verified** equality and not a presumption — there are exactly 1,555 additive terms, exactly 1,555 clusters, and no weighting [audit §12, §13], [F: correction-scalar inputs] — the two factors are not two independent corrections. They telescope exactly:

```
[G/(G−1)] · [(G−1)/(G−K)] = G/(G−K)
```

The "two-factor cluster correction" is therefore, in this application, *identically* the degrees-of-freedom correction on `G` observations. Saying so removes the appearance that two distinct finite-sample problems are being addressed when one is [arith].

**The row count 157,055 is definitively not a candidate for `N`** [audit §13], [F: correction-scalar inputs]. A correction built on it would inflate `(N−1)/(N−K)` toward 1.0002 while pretending to a sample size the likelihood does not have. This is exactly the "regression correction with an incoherent N" the charter's requirement D excludes, and it is excluded here by name.

### 10.3 What `K` counts, and the status of the correction

`K = 35`. **`K` is the local dimension — equivalently the rank — of the restricted estimating problem under strict activity.** Conditional on the two upper-bound constraints being strictly active in the population, the two boundary coordinates are locally constant, the restricted estimating system has 35 free directions, and the covariance object of §11 is defined over exactly those 35 coordinates. The justification is dimensional, not a claim about which sample score equations are or are not exactly satisfied [review §8].

Two things this design explicitly does **not** claim:

- **`c` is not an exact unbiasedness correction for this estimator.** The two-factor form `[G/(G−1)]·[(N−1)/(N−K)]` is a finite-sample convention from the linear-regression setting (HC1/CR1 in style), and the standard treatment notes that cluster-only `G/(G−1)` is what is commonly carried over to nonlinear extensions [review §8]. Applying the two-factor form to a nonlinear constrained QMLE is a **transparent, pre-registered regression-analogue convention**, disclosed as such, not a theorem about this sandwich's finite-sample behaviour.
- **No claim is made about what a referee necessarily expects.** The baseline is defended on the grounds that it is explicit, pre-registered, arithmetically reproducible from verified counts, and disclosed in magnitude — not on an appeal to disciplinary expectation.

The two-factor scalar is retained as the pre-registered baseline because the numerical difference against the alternatives is immaterial (§10.3 table) and because a stated convention is preferable to a silent one. The comparative background for the sample score sums is retained as context only: at the accepted estimate `max |Σ_g s_{g,j}| = 1.0993e-4` over the 35 interior coordinates, while the two active coordinates carry `0.8445544161794221` and `1.4682021491125388` [P4D], [audit §8]. That contrast motivates the active-set conditioning of §11; **it does not carry the weight of the `K` definition.**

Magnitudes, so the stakes are visible [arith], [plan §6.2(1)]:

| Convention | `c` | SE inflation |
| --- | --- | --- |
| CR0 (none) | 1.0000000 | 0 % |
| Cluster-only `G/(G−1)` | 1.0006435 | +0.0322 % |
| **Two-factor, `K = 35` (baseline)** | **1.0230263** | **+1.1448 %** |
| Two-factor, `K = 37` | 1.0243742 | +1.2114 % |

The `K = 35` versus `K = 37` choice moves standard errors by 0.066 % [arith]. **No significance verdict can plausibly turn on the correction choice.** The decision is about convention and defensibility, and the memo says so rather than implying a substantive stake [plan §6.2(1)].

### 10.4 Rejected alternatives

| Rejected | Reason |
| --- | --- |
| CR0 | Asymptotically defensible and a legitimate choice; rejected only because an explicit, pre-registered, magnitude-disclosed convention is preferable to none. No claim is made that its absence would be treated as a defect. |
| Cluster-only `G/(G−1)` | At `G = 1,555` this is +0.03 % — numerically indistinguishable from CR0 while carrying the rhetorical weight of a correction. It is the form conventionally carried over to nonlinear settings [review §8], and remains the pre-registered fallback under §10.6; it is not the baseline because it omits the parameter-count adjustment entirely. |
| Two-factor with `K = 37` | Coherent, and within 0.07 % of the baseline; rejected because 37 is not the local dimension of the restricted estimating problem — two of those coordinates are locally constant under the active-set conditioning of §11. |
| Any correction with `N = 157,055` | Excluded by verified fact [audit §13]. |
| CR2 / CR3 leverage corrections | Require per-cluster Hessian blocks that are not in the accepted Phase-4 artifact set, and rest on a hat-matrix analogue that is heuristic for a non-linear QMLE. Their motivating regime — few clusters, high leverage — does not obtain at `G = 1,555`. |
| Wild cluster bootstrap | Explicitly declined, not silently omitted [plan §6.2(4)]. It is machinery for small `G`; at `G = 1,555` it adds cost, a resampling seed, and a re-optimisation requirement the charter forbids, with no expected change in verdict. |

### 10.5 Reference distributions

Normal and χ² critical values are fixed. Recorded so no reader supposes the alternative was overlooked [arith]: `t(G−1)` gives `1.9614917` against `1.9599640` at the two-sided 5 % level, a 0.078 % difference; for the ten-degree-of-freedom joint test, `χ²(10)₀.₉₅ = 18.3070381` against `10 · F(10, G−K)₀.₉₅ = 18.3691769`, a 0.34 % difference. The χ² form alone is reported, with the F-form difference recorded once in the diagnostics [plan §9.2(3)].

### 10.6 Pre-registered falsification criterion

If the implementation finds that `N ≠ G` — that the number of additive likelihood terms differs from the number of clusters — or that any weighting enters the objective, the telescoping fails, the two factors cease to have a common count, and the design falls back to the cluster-only factor `G/(G−1)` with the ambiguity documented, rather than choosing a factor whose inputs it cannot define [plan §6.3]. On the verified facts this cannot trigger without a change to the accepted model. Separately: **if the covariance object is ever changed from the conditional-35 to the unrestricted-37 (§11), `K` must move to 37 in the same edit.** `K` is the local dimension of the estimating problem the covariance is defined over, so the two decisions are not independent.

---

## 11. Active-bound parameters

### 11.1 The verified situation

`beta_l_age2_sm` (free 2) and `beta_l_age2_sf` (free 6) sit at their **upper** bound `1.0`, spec bounds `[−1.0, 1.0]`, `dist_ub = 0.0` [audit §8], [map], [ERR-1]. This supersedes the design prompt's "accepted lower bounds" statement, which is factually wrong; the canonical state and the charter state no direction, so there is no canonical conflict and no halt [ERR-1].

KKT, with the objective minimised subject to `x_j ≤ 1.0`: stationarity requires `∂negLL/∂x_j + μ_j = 0`, `μ_j ≥ 0`, hence `∂negLL/∂x_j ≤ 0`. Observed: `−0.8445544161794221` and `−1.4682021491125388`, giving `μ_sm = 0.8446`, `μ_sf = 1.4682`, both strictly positive [audit §8], [P4D]. The recorded upper direction is consistent with the published gradient signs; `HM-KKT` does not fire [audit §8].

**Strict activity, quantified** [arith]: the multipliers exceed the interior maximum `|∇negLL| = 1.0992597206183063e-4` (at `beta_w_educH`, free 33) by factors of **7,682.9** and **13,356.3**. The task plan §7.3 falsification criterion — a bound-coordinate gradient of the same order as the interior maximum — does not trigger. Phase-3 gate evidence agrees: G-15 recorded bound hits at exactly this pair, matching both the spec-derived and config-declared expectation; G-16 recorded zero in-bounds violations at `ε = 1e-9` [audit §8].

**Direction of the constraint, stated as the addendum requires.** The negLL gradient is negative in these coordinates, so the objective would fall further if they could rise past 1.0. The unconstrained optimum lies outside the feasible box on the upper side; the feasible cone at the accepted point admits only non-positive movements in these two coordinates.

### 11.2 The four candidate objects, and why they differ

Partition the symmetrised bread as `Hs = [[H_II, H_I𝒜], [H_𝒜I, H_𝒜𝒜]]`.

| # | Object | Formula | Meaning |
| --- | --- | --- | --- |
| 1 | Unrestricted 37-dim | `Hs⁻¹`, `V₃₇ = c·Hs⁻¹ M₃₇ Hs⁻¹` | covariance if all 37 coordinates were interior and estimated |
| 2 | **Conditional / restricted (baseline)** | `B = H_II⁻¹`, `V₃₅ = c·B M B` | covariance of the interior 35 with `x_𝒜` treated as known constants |
| 3 | Marginal submatrix | `[Hs⁻¹]_II = (H_II − H_I𝒜 H_𝒜𝒜⁻¹ H_𝒜I)⁻¹` | interior block of the unrestricted inverse |
| 4 | Schur complement | `𝒮 = H_II − H_I𝒜 H_𝒜𝒜⁻¹ H_𝒜I` | an **information** matrix, not a covariance |

**Why these are not the same object**, as requirement E demands:

- Objects 3 and 4 are inverses of each other: `[Hs⁻¹]_II = 𝒮⁻¹`. Object 4 is frequently mistaken for a covariance; it is a conditional information matrix, and its units are the reciprocal.
- Objects 2 and 3 coincide **if and only if** `H_I𝒜 = 0`. Since `H_I𝒜 H_𝒜𝒜⁻¹ H_𝒜I ⪰ 0` for positive-definite `Hs`, we have `𝒮 ⪯ H_II` in the Loewner order and therefore

  ```
  H_II⁻¹  ⪯  𝒮⁻¹ = [Hs⁻¹]_II
  ```

  **This ordering holds for the model-based inverse-information objects, and for those objects only.** It is a statement about `H_II⁻¹` versus `[Hs⁻¹]_II`. It says that the model-based conditional object is weakly smaller than the model-based marginal one, which is the reason the conditional route must be declared rather than presented as the neutral default.
- **What is *not* ordered.** No Loewner ordering is established between the restricted **robust** sandwich `c·H_II⁻¹ M H_II⁻¹` and any unrestricted or boundary-aware robust covariance. The latter depends on the full meat and its cross-blocks as well as on the bread, and the inverse-Hessian inequality above does not propagate through a sandwich [review §7, §9]. Accordingly this design makes **no claim** that the reported robust standard errors are weakly smaller, weakly larger, or otherwise ordered relative to any marginal or boundary-aware robust alternative. What is claimed, and what §20 requires be said in the paper, is that the reported robust standard errors are **conditional** on the two active-set restrictions and exclude active-set and specification uncertainty, whose magnitude and direction are not identified here.
- Object 1 additionally suffers a derivational failure, not merely an interpretive one: the sandwich `H⁻¹MH⁻¹` is derived from the mean-value expansion of the first-order condition `∇negLL(x̂) = 0`. Here `∇negLL(x̂) ≠ 0` in coordinates 2 and 6 — it is `−0.84` and `−1.47`, values that are O(1) and not numerical noise [P4D]. The expansion the formula rests on does not hold. Object 1 is not an inefficient choice; it is an invalid one.

**A distinct object that must not be reused.** Phase 4 computed a Schur complement `H_RR − H_RN H_NN⁻¹ H_NR` over the partition {10 regional | 27 nuisance}, with rank 10 and `min_eig 2.255741652065068` [P4D], [P4A §10]. That is a *different partition* from the {35 interior | 2 active} partition above and answers a different question (conditional regional identification). Neither object may be substituted for the other. Gate T-6 requires the Phase-5 bread construction to be built from `Hs` afresh by name-keyed deletion, never from any persisted Phase-4 subblock or Schur artifact.

### 11.3 Recommended baseline

**Baseline: object 2 — the conditional 35 × 35 sandwich, `V₃₅ = c · H_II⁻¹ M H_II⁻¹`, with the two active coordinates treated as equality restrictions at `1.0` and excluded from the reported covariance entirely.**

**Validity condition, stated explicitly.** Conditional inference on the interior block is asymptotically valid when the constraints are strictly active *in the population*, so that the active set is correctly identified with probability approaching one. Under that condition, the relevant model is the restricted model with `x₂ = x₆ = 1`, standard 35-dimensional asymptotics apply to it, and no boundary problem arises for the interior block. The strict-activity evidence supports this: multipliers three to four orders of magnitude above interior gradient noise indicate that the unconstrained optimum lies strictly outside the feasible box, not marginally at its edge [audit §8]. If instead the population parameter sat exactly on the boundary, the active set would be random across samples and conditioning would be invalid.

**Why the sandwich rather than the inverse information, given the restriction.** The restricted model's probability limit is a pseudo-true value. That is the setting in which the misspecification-robust sandwich, not `H_II⁻¹`, is the correct asymptotic covariance. The restriction therefore strengthens rather than weakens the case for the robust object as the certified headline.

**The two bound coordinates are reported as follows, and no other way.** In the 47-row parameter table of §17.3, using its exact column names: `estimate = 1.0`; `bound_value = 1.0`; `bound_side = upper`; `grad_negll` = the recorded negLL free-gradient component; `multiplier = −grad_negll`; and `status = active-bound`. **No standard error, no z-statistic, no p-value, no confidence interval** [C-4], [plan §7.2(2)]: the five inferential fields `se_model`, `se_robust`, `ratio_robust_model`, `z`, `p` each take the literal string `NA`. The status text and the field names are fixed here and in §17.3 so that implementation cannot improvise, and so that the boundary-reporting rule and the exact artifact schema are satisfiable simultaneously [review §10].

**What inference on them would require, recorded so the absence is explained rather than unexplained** [plan §7.2(3)]: one-sided or likelihood-ratio inference against the restricted model, or a resampling scheme, each of which requires re-optimisation. Re-optimisation is forbidden in this mission [charter §6, §8]. This is a candidate for a separately authorised later mission, not an oversight.

### 11.4 Rejected alternatives

| Rejected | Reason |
| --- | --- |
| Object 1, unrestricted 37-dim sandwich, SEs for all 37 | Derivation invalid (`∇negLL ≠ 0` at two coordinates); reports symmetric Wald objects for boundary parameters, which is precisely the naive treatment charter §10 prohibits. |
| Object 3, marginal submatrix `[Hs⁻¹]_II` | Allows the bound coordinates to vary in a direction the constraint forbids, attributing to the interior parameters a sampling variability the constraint has removed [plan §7.2(1)]. |
| Object 4, Schur complement, used as a covariance | Category error: it is an information matrix. |
| Dropping the two coordinates from the *model* rather than from the covariance | Would be a respecification of the accepted model, forbidden [charter §6]. They remain in the likelihood at `1.0`; only the covariance excludes them. |
| One-sided / LR / bootstrap boundary inference now | Requires re-optimisation, forbidden here. Deferred with a named trigger (§19, §22 D-6). |

### 11.5 Pre-registered falsification criteria

- **T-22 (gating) — a numerical KKT gate, and nothing more.** Both multipliers must exceed `100 ×` the interior maximum `|∇negLL|`. Observed ratios 7,682.9 and 13,356.3 [arith] clear this by two orders of magnitude. **T-22 establishes strong sample numerical KKT activity relative to optimizer residuals. It is not a statistical test and it does not prove strict activity of the population pseudo-true constraint** [review §9]. Its role is to confirm that the sample active set is unambiguous at the accepted point, so that the conditioning of §11.3 is being applied to a numerically well-determined active set rather than to a near-tie. If a future recomputation of the accepted state fails it, the sample-level basis for the equality-restriction treatment collapses, and the coordinate must instead be treated as interior-but-near-boundary with the limitation reported [plan §7.3]. The population condition itself is an assumption, declared as such in §11.3 and in §20.
- **T-19 (gating).** The restricted-model stationarity must be numerically real, not merely assumed. The implied Newton displacement `‖H_II⁻¹ g_ℐ‖` must be small relative to the robust standard errors: **each coordinate's implied displacement ≤ 0.05 × its robust SE.** Design-time bound on published values: `‖g_ℐ‖₂ = 2.623980639599166e-4` and `λ_min(Hs) = 0.1037326963880782` give a worst-case displacement norm of `2.53e-3` and an implied negLL suboptimality bound of `3.32e-7` nats [arith]. The per-coordinate comparison against SEs is not computable at design time and is `UNKNOWN` until execution.
- **W-4 (warning, mandatory escalation).** Defined on the **robust** 95 % interval. For each interior parameter `j`, form `[θ̂_j − z₀.₉₇₅·se_robust_j, θ̂_j + z₀.₉₇₅·se_robust_j]` with `z₀.₉₇₅ = 1.959963984540054`. The warning **triggers if the interval reaches or crosses either spec bound**, i.e. if `θ̂_j − z₀.₉₇₅·se_robust_j ≤ lb_j` **or** `θ̂_j + z₀.₉₇₅·se_robust_j ≥ ub_j`. Equality with a bound triggers the warning; "strictly inside" is the passing condition [review §12]. Two coordinates are the plausible candidates: `sigma`, accepted `0.413492` with lower bound `0.10` (distance `0.313`), and `theta_c_singles`, accepted `0.093459` with upper bound `0.95` (distance `0.857`) [map]. Whether either trips is `UNKNOWN` until standard errors exist. If one does, it is flagged in the table and escalated to the manager; the boundary machinery of §11.3 is **not** extended to it in Phase 5, because it is a nominally interior coordinate whose first-order condition holds, not an active-bound estimate [review §9].

### 11.6 Economic reading, carried as a caveat not resolved here

These are the age-squared terms in the singles leisure block — the curvature of the leisure-preference profile in age. Their sitting at a corner means the estimated preference block absorbs age curvature at the constrained extreme. Because age-in-leisure routes to the preference channel under the project's normative bookkeeping, and because the headline decomposition separates opportunity from preferences [DL D-011], the concern must be stated plainly: **a preference coordinate constrained at a corner has less scope to absorb variation in that dimension than an unconstrained one would, which bears on the interpretation of any absorption result in JMP-M07** [plan §7.2(4)]. This is a statement about the constrained specification's flexibility in one dimension; it is not a claim about the direction or magnitude of any bias in an absorption estimand, which is not established here. Whether the bound is tight because of the covariate's scaling (`age_norm2`) or because of substantive curvature is `UNKNOWN` and is not investigated here. This is a caveat for the manuscript and a handoff item for M07/M08 — not evidence about the specification, not a defect to be resolved in Phase 5, and not grounds for respecification within this mission.

---

## 12. Fixed pins

### 12.1 Exclusion

The ten pins are excluded from differentiation structurally, by the reparameterisation of §5.1: they are constants inside `ι`, so no derivative with respect to them is ever taken. They are excluded from the meat, the bread, the covariance, and every test. Phase 3 removed them from the optimization vector entirely, so no pin-clamped bound entered the optimizer [audit §8].

### 12.2 Reporting — recommended baseline

**Baseline: all ten pins appear in the parameter table with their pinned value, a category label, and the literal string `NA` in the five inferential fields `se_model`, `se_robust`, `ratio_robust_model`, `z`, `p`, under `status = pinned`, with a table footnote.** Field names are those of the exact §17.3 schema.

**Rejected:** a numeric standard error (asserts estimated precision); a zero standard error (asserts *infinite* precision — see §12.3, where the truth is the opposite); `NaN` (invites a "computation failed" reading and is silently coerced by spreadsheet software); a blank cell (indistinguishable from an omission); exclusion of pinned rows from the table altogether (a 47-parameter specification that displays 37 rows invites the reader to ask which ten are missing and why [plan §8.3]).

### 12.3 Why `NA` and not `0` — the rigorous reason

Requirement F asks for `NA` unless a stronger reason exists. The stronger reason runs the other way, and it is worth stating because it is the referee-proof version of the argument.

All ten pins have gradient component **exactly `0.0`** in the published 47-element `gradient_final` [audit §9]. This is not because they satisfy a first-order condition. It is structural: eight are unreferenced by the singles builder, and two multiply an identically-zero 2016 covariate [audit §9]. For those coordinates `∂negLL/∂θ_j ≡ 0` *for all θ*, hence `∂²negLL/∂θ_j∂θ_k ≡ 0`. The full 47 × 47 information matrix has ten exactly-zero rows and columns. The likelihood is **flat** in these directions; the information is zero, not infinite. A reported standard error of `0` would assert perfect precision where in fact there is no information at all. `NA` is the only representation that is not actively false.

### 12.4 Category assignment — no normalisation category

**No pin is a normalisation** [F-2], [audit §9]. This overturns the task plan §8.2(1) working assumption, which named `theta_l_f` as the normalisation candidate; `theta_l_f` is the couples-female leisure Box–Cox exponent, unreferenced by the singles objective [audit §9]. A pin-reporting convention with a "normalisation" category would have no members, so the design defines two categories, both under structural inapplicability:

| Category label | Members | Mechanism |
| --- | --- | --- |
| `structurally-inapplicable: unreferenced` | `beta_l0_m`, `beta_l_age_m`, `beta_l_age2_m`, `beta_l0_f`, `beta_l_age_f`, `beta_l_age2_f`, `beta_l_nkids_f`, `theta_l_f` | resolved only by `build_jax_couples_ll`, which the P2a run never calls [audit §9] |
| `structurally-inapplicable: null-covariate-2016` | `beta_E_y2015`, `beta_E_y2017` | declared in `market_opportunity.shifters`, but both covariate columns are identically zero across all 157,055 rows [audit §9] |

**Mandatory table footnote**, so that a referee counting fixed quantities is not misled: *"Ten coordinates are pinned run-overlay restrictions, not estimates. All ten are structurally inapplicable to a 2016 singles sample and carry exactly zero gradient for structural reasons; standard errors are undefined, not zero. The specification's genuine normalisations — `beta_c = 1.0`, couples `theta_c = 0.0`, `theta_l_m = −0.8`, and the removed `beta_ll` — lie outside the 47-vector and outside this table; `theta_l_m` in particular is a `fixed_params` entry and is not one of the ten pins."* [audit §9], [F-2].

### 12.5 Provenance and decomposition relevance

Pin values are reported alongside the Phase-3 finding `pins_bitwise_accepted: true` — IEEE-754 byte equality from the accepted pin values through the applied start vector to the final estimate [audit §9]. That is the evidence that pins are conventions rather than estimates.

`beta_E_y2015` and `beta_E_y2017` are by name opportunity/access coordinates, so the decomposition-relevance flag stands nominally; but because their covariates are identically zero in the 2016 sample, they contribute nothing to the P2a opportunity index at any value [audit §9]. The design declares this and hands any sensitivity question to JMP-M08/M09; it does not analyse it [plan §8.2(4)].

**Pre-registered falsification criterion.** If the implementation finds any pinned coordinate with a non-zero gradient component in the 47-element gradient, the structural-inapplicability classification is falsified for that coordinate, the `NA` justification of §12.3 no longer applies to it, and the run halts pending manager review.

---

## 13. Regional-block inference

### 13.1 Constructs — three, not one

The ten coordinates span three distinct constructs and must never be described as one homogeneous block [F-3], [audit §15]:

1. **`gsur`** — a **continuous** local labour-market rate, sourced from a `(drgn1, educ3, sex)` lookup at opportunity year 2015, scaled by 10, gated on `working`, and declared `offer_only_vars`. Verified household-level values: 47 unique values, range `[0.053183, 0.225]`, mean `0.09450886`, constant within household [audit §15]. **It is not a region dummy and has no omitted category.** It varies with region, education and sex jointly. Assigning it to a null over "across-region differences" would conflate a rate with a set of region intercepts.
2. **`reg2 … reg8`** — seven NUTS-1 region dummies built by the loader fallback `reg{k} = (drgn1 == k)`; the stem's stored `reg2..reg8` columns are identically-zero region-dead placeholders never read by the likelihood [audit §15]. Household counts `{1: 245, 2: 254, 3: 122, 4: 135, 5: 279, 6: 175, 7: 182, 8: 163}`. **Reference category: `drgn1 == 1`, 245 households** [audit §15].
3. **`drgur`, `drgmd`** — urbanisation-degree indicators from EU-SILC `db100`. Counts `drgur = 832`, `drgmd = 328`, `drgru = 395`. `drgru` is loaded but carries no coefficient. **Reference category: rural `drgru`, 395 households** [audit §15].

### 13.2 Covariance sub-objects

`V_RR` is the 10 × 10 block of `V_robust` at interior positions 13–22, extracted **by name** [audit §7]. The model-based counterpart is the same block of `V_model`. Both are reported. The 10 × 10 correlation matrix is derived from `V_RR` and reported alongside.

### 13.3 Individual diagnostics

For each of the ten: estimate; model SE; robust SE; robust/model ratio; `z = θ̂_j / se_robust_j`; two-sided p-value against the standard normal. **These are descriptive detail, not the significance claim** [plan §9.2(5)]. No multiplicity adjustment is applied to them, because the joint test carries the claim. Coefficients are never interpreted causally [charter, requirement G]: they are conditional associations within the modelled offer/access index, at the accepted estimate, for this sample.

### 13.4 Joint tests

**Objects and dimensions, stated explicitly.** Let `V_I ∈ ℝ^{35×35}` denote the interior covariance — either `V_model` or `V_robust` of §8–§9 — and `θ̂_I ∈ ℝ³⁵` the interior estimate subvector. Define:

```
E_R ∈ ℝ^{10×35}     access-block selector; row b of E_R is the unit vector
                     for the interior position of access-block name b (§7.3)
θ̂_R = E_R θ̂_I ∈ ℝ¹⁰
V_RR = E_R V_I E_Rᵀ ∈ ℝ^{10×10}
A ∈ ℝ^{q×10}         null-specific selector, rows keyed by parameter name
r = 0 ∈ ℝ^q
```

The statistic, for each null:

```
d = A θ̂_R − r ∈ ℝ^q
W = dᵀ (A V_RR Aᵀ)⁻¹ d          via cho_factor / cho_solve on A V_RR Aᵀ ∈ ℝ^{q×q};
                                 never an explicit inverse
W ~ χ²(q) asymptotically under H0
```

The equivalent one-step form `W = (R θ̂_I − r)ᵀ (R V_I Rᵀ)⁻¹ (R θ̂_I − r)` with `R = A E_R ∈ ℝ^{q×35}` is algebraically identical and may be used instead; the two-step `E_R` form is canonical here because it makes the 10 × 10 access block an explicitly named intermediate object [review §11]. Every selector row is constructed **by name** from `phase5_parameter_map_v1.csv`, never positionally.

| Null | `q` | Rows of `A` (parameter names, in block order) | Status |
| --- | --- | --- | --- |
| **H0-A** | **10** | `beta_E_gsur`, `beta_E_drgn2` … `beta_E_drgn8`, `beta_E_drgur`, `beta_E_drgmd` — i.e. `A = I₁₀` | **certified omnibus** — the single confirmatory test [charter, requirement G] |
| H0-B | 7 | `beta_E_drgn2`, `beta_E_drgn3`, `beta_E_drgn4`, `beta_E_drgn5`, `beta_E_drgn6`, `beta_E_drgn7`, `beta_E_drgn8` | pre-registered **primary sub-test**. It tests the **common NUTS-1 intercept component** of the modelled access index: the seven NUTS-1 intercept shifts jointly zero relative to reference region 1. **It is not a test of a common opportunity environment** [review §11], [C-2], [C-5]. |
| H0-C | 2 | `beta_E_drgur`, `beta_E_drgmd` | pre-registered secondary; urbanisation intercepts relative to rural |
| H0-G | 1 | `beta_E_gsur` | pre-registered secondary, **stated separately**; `gsur` belongs to neither H0-B nor H0-C [F-3] |

Each null is computed in both model-based and robust forms — `W_model` from `V_I = V_model`, `W_robust` from `V_I = V_robust` — and the output carries **separate `p_model` and `p_robust` fields**, never a single undifferentiated p-value (§17.2). The robust form carries the reported verdict. Critical values `χ²(10)₀.₉₅ = 18.3070`, `χ²(7)₀.₉₅ = 14.0671`, `χ²(2)₀.₉₅ = 5.9915`, `χ²(1)₀.₉₅ = 3.8415` [arith].

**Multiplicity convention, fixed.** H0-A is the single confirmatory test and carries the significance claim; H0-B, H0-C and H0-G are pre-registered secondary tests reported with unadjusted p-values and explicitly labelled as not carrying independent confirmatory weight [plan §9.2(5)]. No post-hoc null may be added after seeing the results.

**Rejected:** designating H0-B as the confirmatory test (the charter and design prompt fix the ten-degree-of-freedom omnibus as the required certified test); folding `gsur` into H0-B to obtain an eight-degree-of-freedom "region" null (forbidden by [F-3]); adding data-driven nulls after inspection.

### 13.5 Mandatory conditioning report

The regional design's singular values decline smoothly from `30.400` to `11.269`, then fall to `7.717` and `1.679` [P4D], [audit §15]. The smallest is roughly a factor of five below the next. One linear combination of the regional covariates is therefore substantially less well supported than the others, which bears on whether individual regional coefficients are separately informative even though the block is jointly identified. **The eigenspectrum of `V_RR` must be reported with its weakest direction identified** (W-2). This is a reporting requirement, not a gate: Phase 4 already passed rank and positive-definiteness on this design [plan §9.2(4)], [P4A §8].

### 13.6 Model-versus-robust divergence

The robust/model SE ratio is reported for the block and flagged if outside `[0.2, 5]` (W-1). **It must not be interpreted as evidence of anything.** It is a warning-tier diagnostic in the manner of Phase 4's loading-share diagnostic, which was explicitly warning-only and never gating [plan §9.2(6)], [P4D `loading_shares.note`].

### 13.7 Pre-registered falsification criterion

If `V_RR` is not positive definite, or its rank is below 10, or `W` is non-finite for any pre-registered null, the regional protocol is falsified and the run halts (T-14). Given `M` has rank 35 generically at `G = 1,555` and Phase 4 established the design has rank 10 with a positive-definite conditional Schur complement [P4D], this is not expected to trigger; it is registered because a rank failure would indicate an implementation defect rather than a data property.

---

## 14. Score validation gates

Gate names extend the accepted register of [plan §11]. **Gating** tier halts the run; **warning** tier is informational and never determines the verdict, following Phase 4's explicit precedent [P4D].

| Gate | Statement | Tier |
| --- | --- | --- |
| **T-1** | Score identity: `np.allclose(S.sum(0), −gradient_free_accepted, atol=1e-8, rtol=1e-8)`; max abs deviation recorded | gating |
| **T-2** | `S` is exactly `(1555, 37)`, `float64`, C-contiguous, and `np.isfinite(S).all()` | gating |
| **T-3** | Cluster count and completeness: 1,555 unique `cluster_id`; no missing or non-finite; stored id vector strictly increasing and elementwise equal to `np.sort(np.unique(idhh))`; every household exactly once; group sizes sum to 157,055 | gating |
| **T-4** | Signed max-norm score identity: `max(abs(S.sum(0) + gradient_free_accepted)) <= 1e-12`. The sign is explicit — `S.sum(0) = −∇negLL`, so the correct comparison is a **sum**, not a difference (Phase 4 achieved `8.88e-16` against Phase 3) | gating |
| **T-11** | Route invariance: if chunked, `max\|S_chunked − S_reference\| ≤ 1e-12 · max\|S\|`; chunk size `C` recorded; bitwise equality recorded as a diagnostic, not required | gating |
| **T-12** | Fresh-process reproduction: rerun in a new interpreter reproduces the `.npy` SHA-256 **bitwise** | gating; see §16.3 |
| **T-15** | `jax_enable_x64` confirmed true at runtime | gating |
| **T-16** | Mode agreement: on the first 64 households in canonical order, `max\|S_jacfwd − S_jacrev\| ≤ 1e-10 · max\|S\|` | gating |
| **T-17** | Parameter-order fingerprint: SHA-256 of newline-joined ordered 37 `free_names`, and of the ordered 35 interior names, equal to values recomputed from `phase4_manifest.json → contract.parameter_map`; name equality asserted at every projection | gating |
| **T-20** | No optimizer call: `optimizer_called: false` recorded; no `scipy.optimize` invocation on the Phase-5 path; verified by code review at Stage-C/implementation review and asserted in the manifest | gating |
| **W-5** | Centring diagnostic: record `‖Σ_g s_{g,ℐ}‖∞` and the magnitude of the centring correction to `M` that is **not** applied | warning |

---

## 15. Covariance validation gates

| Gate | Statement | Tier |
| --- | --- | --- |
| **T-5** | Bread provenance: `hessian_free.npy` SHA-256 = `e9ca080e…`; Phase-4 bundle SHA-256 recomputes to `5484886985…`; Phase-3 bundle to `2cf23764…`; θ̂ bytes hash to `c024b893…` | gating |
| **T-6** | Bread integrity on load: `max\|H − Hᵀ\| ≤ 2.3588019878151842e-4`; symmetrise to `Hs`; `min_eig(Hs) > 0`, rank 37 at tolerance `1e-10 · max_eig`; recomputed `min_eig` and condition number agree with `0.1037326963880782` and `405353.94719781954` to `rtol 1e-10`; `H_II` built by name-keyed deletion from `Hs`, never from a persisted Phase-4 subblock; Cholesky of `H_II` succeeds | gating |
| **T-7** | Meat validity: `max\|M − Mᵀ\| ≤ 1e-12 · max\|M\|` before symmetrisation; **`min_eig(M) ≥ −κ_BE · max_eig(M)` with `κ_BE = K·G·u = 35 × 1555 × 2⁻⁵³ = 6.0423888115224145e-12`** (§16.2); rank recorded | gating |
| **T-8** | Solve stability: every inverse-like operation by factorisation; max abs deviation from a pseudo-inverse reference ≤ `1e-8` (Phase 4 achieved `8.53e-14`) | gating |
| **T-9** | Covariance validity: `V_model` and `V_robust` symmetric to `1e-12` relative; `V_model` positive definite; **`V_robust` PSD with `min_eig ≥ −1e-10 · max_eig`** — the declared rank convention, not looser (§16.2); all 35 diagonal entries of both strictly positive and finite | gating |
| **T-10** | Correction scalar recorded as an explicit number with its formula and the numerical values of `G`, `N`, `K`, plus the telescoped form `G/(G−K)` | gating |
| **T-13** | Immutability: post-evaluation recheck confirms all authenticated inputs, the ten pins, θ̂, and both accepted bundles bitwise unchanged; runtime-map fingerprint stable | gating |
| **T-14** | Regional tests: `V_RR` positive definite, rank 10; `W` finite for H0-A, H0-B, H0-C, H0-G; both model and robust computed; degrees of freedom recorded as 10, 7, 2, 1 | gating |
| **T-18** | Valid correlations: `\|ρ_ij\| ≤ 1 + 1e-10` for all pairs in both covariances; unit diagonal after construction | gating |
| **T-19** | Conditional-35 stationarity: implied Newton displacement `\|(H_II⁻¹ g_ℐ)_j\| ≤ 0.05 · se_robust_j` for every interior coordinate | gating |
| **T-22** | **Numerical KKT activity** (sample-level, not a population claim): `μ_sm` and `μ_sf` each ≥ `100 ×` interior max `\|∇negLL\|`. Records that the sample active set is unambiguous; does **not** establish population strict activity (§11.5) | gating |
| **T-23** | Custody-record completeness: the manifest carries `disclosure_class` and named retention responsibility on **every** run; and, whenever the authoritative `.npy` is not committed, additionally the custody/locator identifier, SHA-256, byte size, shape, row fingerprint and column fingerprint (§17.1, §18.5) | gating |
| **W-1** | Robust/model SE ratio per parameter; flag any ratio outside `[0.2, 5]` | warning |
| **W-2** | Eigenspectrum of `V_RR` reported, weakest direction identified | warning |
| **W-3** | Effective-rank summary of `M` relative to 35 | warning |
| **W-4** | Near-boundary containment on the **robust** interval: for every interior parameter, `θ̂_j ± z₀.₉₇₅·se_robust_j` with `z₀.₉₇₅ = 1.959963984540054` must lie **strictly** inside `[lb_j, ub_j]`; **equality with a bound triggers the warning** (§11.5); violations flagged and escalated to the manager | warning, mandatory escalation |

---

## 16. Numerical tolerances

### 16.1 Reused certified tolerances

| Quantity | Value | Provenance |
| --- | --- | --- |
| Score identity | `atol=1e-8, rtol=1e-8` | frozen [charter §8] |
| Hessian symmetry threshold | `2.3588019878151842e-4` | Phase-4 recorded [P4D] |
| Rank tolerance | `1e-10 × max_eig` | Phase-4 convention, verified: `4.204845793438049e-06 = 1e-10 × 42048.457934380494`; the same convention appears in `design.rank_tolerance` and `schur_rank_tolerance` [P4D], [arith] |
| Solve-versus-pinv | `≤ 1e-8` absolute | Phase-4 achieved `8.526512829121202e-14` [P4D] |
| Gradient reproduction | `≤ 1e-12` | Phase 4 achieved `8.881784197001252e-16` against Phase 3 [P4D] |

### 16.2 New tolerances, each with its justification

| Quantity | Value | Justification |
| --- | --- | --- |
| Meat PSD (T-7) | `min_eig ≥ −κ_BE × max_eig`, `κ_BE = K·G·u = 35 × 1555 × 2⁻⁵³ = 6.0423888115224145e-12` | **Quantitatively justified backward-error bound.** `M = S_Iᵀ S_I` is a Gram matrix formed by inner products of length `G = 1,555` in float64 with unit roundoff `u = 2⁻⁵³ = 1.1102230246251565e-16`; the standard floating-point Gram bound gives `γ_G = G·u/(1−G·u) = 1.7263968032924165e-13`, and the dimension factor `K = 35` in the Weyl perturbation of the smallest eigenvalue yields `κ_BE`. This is **16.5× tighter** than the `1e-10` rank convention [arith] |
| Covariance PSD (T-9) | `min_eig ≥ −1e-10 × max_eig` | Set **equal to**, and never looser than, the declared rank convention. `V_robust = c·BMB` is PSD by construction whenever `M` is (`xᵀBMBx = (Bx)ᵀM(Bx) ≥ 0`), but its numerical floor inherits the conditioning of `H_II`; the full `Hs` has condition number `405,353.9` [P4D]. A tighter bound would require a forward-error analysis of the two solves, which is not supplied, so the rank convention is adopted rather than a weaker figure asserted |
| Symmetry of accumulated matrices | `≤ 1e-12 × max\|·\|` | `M` and `V` are symmetric by construction; deviation is pure accumulation rounding |
| Chunk-route invariance | `≤ 1e-12 × max\|S\|` | Chunking is mathematically exact (§5.4); residual is XLA fusion-order rounding, not algorithmic |
| Mode agreement (T-16) | `≤ 1e-10 × max\|S\|` | Forward and reverse AD differ in accumulation order; two orders looser than T-11 because the operation sequences differ substantially |
| Stationarity displacement (T-19) | `≤ 0.05 × robust SE` | A displacement below 5 % of a standard error cannot move any reported interval materially |
| Numerical KKT activity (T-22) | `≥ 100 ×` interior max gradient | Observed margin is 7,683 and 13,356 [arith] — two orders of magnitude of headroom. A **sample** numerical threshold on optimizer residuals, not a population claim (§11.5) |
| Near-boundary warning (W-4) | `z₀.₉₇₅ = 1.959963984540054`; trigger on `≤ lb_j` or `≥ ub_j` | Equality with a bound triggers; the passing condition is strict interiority of the robust interval [review §12] |
| Correlation bound (T-18) | `1 + 1e-10` | Matches the rank-tolerance scale |
| Phase-4 eigen agreement (T-6) | `rtol 1e-10` | Reproduction of published accepted scalars, not a new computation |

### 16.3 Determinism, with a named escalation path

T-12 requires **bitwise** SHA-256 reproduction of the score `.npy` in a fresh process. The whole certification model is hash-based, and F-4 demonstrates how silently non-bit-exact artifacts arise. If bitwise reproduction fails and the cause is traced to a documented XLA or threading non-determinism, the gate does **not** silently downgrade: the run halts, the failure is recorded with the observed `max abs diff`, and the manager decides whether to accept a tolerance-based substitute of `≤ 1e-13 × max|S|` with the non-determinism documented in the manifest. Named halt: **`HP-REPRO`**.

---

## 17. Required output artifacts

### 17.1 Score artifact — decision

**Baseline: `.npy` binary committed as the authoritative artifact, with committed summaries and a committed CSV rendering explicitly flagged non-authoritative.**

Grounds:

- **Size is not the axis.** 1,555 × 37 float64 is 57,535 values = **460,280 bytes (0.439 MiB)** raw binary, roughly **1.4 MB** as CSV at 17 significant digits [arith], [plan §10.2(2)]. Both are trivially committable; the "too large" argument does not apply and is not invoked.
- **Hash fragility is the axis, and this repository has demonstrated it twice.** First, `hessian_free.csv` differs from `hessian_free.npy` in 337 of 1,369 entries because the accepted writer used pandas' default formatting [F-4], [audit §16]. Second, two nested package source files have working-tree SHA-256 values differing from their recorded `committed_sha256` purely through line-ending normalisation between the git object and the checked-out file [audit §18]. A `.npy` hash is invariant to line endings, locale and float formatting; a CSV hash is not.
- **This inverts the task plan's working presumption, and does so on a ground the plan did not anticipate.** [plan §10.3] presumed CSV canonical with `.npy` alongside, and pre-registered its falsification as "a repository policy against committing binary artifacts." The actual falsifying fact was different: the premise that the accepted precedent round-trips exactly is false for the writer used [F-4]. The general numerical claim — that 17 significant decimal digits suffice for float64 round-trip — remains true; what fails is the precedent's implementation of it. The departure is recorded here rather than made silently.
- The CSV rendering is nonetheless committed, written with an explicit `float_format='%.17g'`, and the manifest carries an `authoritative: true|false` flag per artifact so that no future consumer repeats the F-4 confusion.

**Rejected:** CSV as the sole or canonical artifact (hash fragility, demonstrated twice in this repository); and — critically — **any fallback in which the authoritative bytes are merely left outside version control on a working machine, with only summaries and a hash committed.** A hash plus summaries does not preserve reproducibility: it certifies bytes that nothing durably retains [review §13]. That is the v1 fallback's defect, and it is corrected below.

**Pre-registered fallback, complete as a certification contract.** If the licence or disclosure determination (§22, open item 3) returns that household-level derived arrays may not be committed, the baseline switches to **restricted custody**, not to abandonment of the artifact. The authoritative `.npy` must then be retained in a **durable, access-controlled, immutable** artifact store or restricted bundle — not a working directory, not a personal drive, not a mutable network share. The public or shared repository then contains only the summaries, the fingerprints, and the hashes.

Under the fallback, the manifest must record all of:

| Manifest field | Content |
| --- | --- |
| `custody_locator` | Non-public custody or locator identifier for the restricted store; sufficient to retrieve the bytes under authorisation, and not itself disclosive |
| `sha256` | SHA-256 of the authoritative `.npy` |
| `size_bytes` | Exact byte size (`460,280` for the 1,555 × 37 float64 array [arith]) |
| `shape`, `dtype`, `layout` | `(1555, 37)`, `float64`, C-contiguous |
| `row_fingerprint` | SHA-256 of the newline-joined canonical `cluster_id` sequence (§6.3) |
| `column_fingerprint` | SHA-256 of the newline-joined ordered 37 `free_names` — the same value T-17 asserts |
| `disclosure_class` | e.g. `derived_microdata_household_level` |
| `retention_responsibility` | Named role accountable for retention and for authorised retrieval |

**These requirements are specified unconditionally.** The `disclosure_class` and `retention_responsibility` fields are written on **every** Phase-5 run regardless of which route is taken, and the custody fields are additionally required whenever the `.npy` is not committed. Gate T-23 enforces this. The design is therefore complete under either outcome of the determination, and execution cannot be blocked by it [Stage-D instruction §2]. **This memo does not decide the licence question**; that is the principal investigator's [review §13].

### 17.2 The immutable Phase-5 bundle

Written to `outputs/p2a_singles2016/region_live_v1/phase5_inference_v1/complete/`, following the Phase-3/Phase-4 pattern exactly:

| Artifact | Content | Authoritative |
| --- | --- | --- |
| `phase5_scores_free.npy` | 1,555 × 37 float64 C-contiguous, canonical row order | **yes** |
| `phase5_scores_free.csv` | rendering at `%.17g`, named columns | no |
| `phase5_score_row_index.csv` | 1,555 `cluster_id` in canonical order | yes |
| `phase5_score_columns.csv` | ordered 37 free names with free/interior index map | yes |
| `phase5_score_summary.csv` | per column: sum, deviation from `−∇negLL`, min, max, mean, L2 norm | yes |
| `phase5_meat.npy` | 35 × 35 `M` | yes |
| `phase5_covariance_model.npy` / `.csv` | 35 × 35 `V_model` | npy yes / csv no |
| `phase5_covariance_robust.npy` / `.csv` | 35 × 35 `V_robust` | npy yes / csv no |
| `phase5_regional_covariance.csv` | 10 × 10 robust block plus correlation matrix | yes |
| `phase5_parameter_table.csv` | 47 rows, the exact 13-column schema of §17.3 | yes |
| `phase5_regional_tests.csv` | one row per null: `null_id`, `q`, `restriction_names`, `W_model`, `W_robust`, `p_model`, `p_robust`, `chi2_crit_95`, `tier` ∈ {`confirmatory`, `secondary`} | yes |
| `phase5_diagnostics.json` | every gate result, tolerance, and warning-tier value | yes |
| `phase5_console.log` | full run log | yes |
| `phase5_manifest.json` | written last, excluded from its own hash map | yes |

**Bundle hash algorithm, reused verbatim from Phase 4** [audit §16]:

```
hashes = {n: sha256(staging/n) for n in PHASE5_ARTIFACTS}      # manifest excluded
joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
bundle_sha256 = sha256(joined.encode("utf-8")).hexdigest()
```

The exact artifact set is enforced twice — before the console log is written and again after the manifest — so that bundle membership is closed rather than conventional [audit §16]. Every member is a required member; none is described as "optional," which corrects the documentation understatement flagged for the Stage-E packet [ledger §4].

### 17.3 Reporting contract

`phase5_parameter_table.csv` has exactly these **13 columns**, in this order, for all 47 rows:

```
name, block, status, estimate, bound_value, bound_side, grad_negll, multiplier,
se_model, se_robust, ratio_robust_model, z, p
```

`status ∈ {interior, active-bound, pinned}`. There is **no `flag` column**; `status` is the single status field, and v1's stray reference to `flag` is removed [review §10]. Population rules, exhaustive by status:

| Column | `interior` | `active-bound` | `pinned` |
| --- | --- | --- | --- |
| `estimate` | accepted value | `1.0` | pinned value |
| `bound_value` | `NA` | `1.0` | `NA` |
| `bound_side` | `NA` | `upper` | `NA` |
| `grad_negll` | recorded free-gradient component | recorded free-gradient component | `0.0` (structural — §12.3) |
| `multiplier` | `NA` | `−grad_negll` | `NA` |
| `se_model`, `se_robust`, `ratio_robust_model`, `z`, `p` | computed | **`NA`** | **`NA`** |

The five inferential fields are the literal string `NA` for every `active-bound` and `pinned` row, without exception (§11.3, §12.2). This satisfies the boundary-reporting rule of §11.3 and the exact artifact schema simultaneously, which v1 did not [review §10, §16 R-4].

**Why the bound diagnostics live in the parameter table rather than in a separate artifact.** The review permitted either route [review §10, §13]. Adding columns is preferred because a dedicated bound-diagnostics table would create a second authoritative object carrying facts that also appear in the first — precisely the duplicated-truth pathology that F-4 exposed for the Hessian. One authoritative table, one row per coordinate, all 47 rows present.

Reported precision is local at the accepted estimate and carries no identification or recovery claim [plan S-9].

---

## 18. Transaction and execution contract

Research-grade reproducibility, following Phases 3–4 — not production-security maximalism [charter, requirement J].

### 18.1 Review binding

Execution requires a Phase-5 code review whose SHA-256 is recorded in the manifest, with `review_gate: PHASE5_REVIEW_V1_APPROVED` and `execution_ready: true`, exactly as Phase 4 bound itself to review v7 [P4A §2]. Without both fields the runner refuses to start.

### 18.2 Accepted dependencies re-verified at run time

Before any evaluation: recompute and match the Phase-3 bundle, the Phase-4 bundle, `hessian_free.npy`, θ̂ bytes, the certified spec YAML, and the thirteen runtime input files against their accepted anchors [audit §18]. Verify MNL HEAD `982c5221…` and gitlink `27756a06…`, and that both worktrees are clean. Any mismatch halts before the score is touched.

### 18.3 Lock, staging, attempts, complete

One lock file for the run directory. All writes go to `staging/`. On any gate failure, the staging directory is preserved under `attempts/<timestamp>_STOPPED/` with the failure recorded — following the Phase-4 precedent that preserved the stopped rank-3 attempt `52f34b54…` [P4A §8]. `complete/` is written only when every gating item passes, and is never overwritten.

### 18.4 Dry run and the one-run rule

**Dry run:** the full 1,555-household computation with the complete gate battery, writing only to `attempts/dryrun_<timestamp>/`, producing no `complete/` and no manifest promotion. A subset dry run is rejected because T-1 is not evaluable on a subset — the identity is a whole-sample property. The full dry run is affordable: Phase 4's exact 37 × 37 `jax.hessian` over the same objective completed in `4.0` wall seconds [P4D], and a 37-JVP forward-mode Jacobian is of the same order.

**One-run rule:** exactly one authorised real run. If it fails a gate, it stops, is preserved under `attempts/`, and a new authorisation is required. Re-running until a gate passes is prohibited.

### 18.5 Post-evaluation recheck and the environment mandate

After evaluation, re-verify every authenticated input, the ten pins, θ̂, and both accepted bundles bitwise (T-13), recording `pre == post == accepted` for every label, as Phase 4 did [audit §18].

**The Phase-5 manifest must record, for every run:** Python, NumPy, pandas, SciPy, **JAX, jaxlib**, platform string, machine, thread settings and XLA flag settings, plus peak memory and the chunk size `C`. This is a binding handoff requirement: those fields were never recorded for Phase 3 or Phase 4 and are permanently unrecoverable [audit §19], [ledger §2]. Phase 5 must not reproduce that gap.

**The manifest must additionally record, on every run and independently of the disclosure determination:** `disclosure_class` and `retention_responsibility` for the authoritative score artifact, plus its `sha256`, `size_bytes`, `shape`, `dtype`, `layout`, `row_fingerprint` and `column_fingerprint` (§17.1). Whenever the authoritative `.npy` is not committed, `custody_locator` is additionally required and must resolve to a durable, access-controlled, immutable store. Gate T-23 enforces completeness of this block. Recording custody metadata unconditionally means the certification contract does not change shape depending on how the licence question resolves [review §13], [Stage-D instruction §2].

### 18.6 Halt-condition register

| Name | Trigger |
| --- | --- |
| `HP-IDENT` | T-1 score identity fails at the frozen tolerance |
| `HP-SHAPE` | T-2 or T-3 fails: shape, finiteness, cluster count, completeness, or row order |
| `HP-BREAD` | T-5 or T-6 fails: bread hash, symmetry, positive definiteness, or Phase-4 eigen agreement |
| `HP-MEAT` | T-7 fails: meat symmetry or PSD |
| `HP-COV` | T-9, T-18 or T-14 fails: covariance validity, correlations, or regional rank |
| `HP-KKT` | T-22 fails: active-set strictness collapses |
| `HP-STAT` | T-19 fails: restricted-model stationarity is not numerically real |
| `HP-REPRO` | T-12 fails: fresh-process reproduction is not bitwise (§16.3) |
| `HP-ORDER` | T-17 fails: parameter-order fingerprint mismatch |
| `HP-MUT` | T-13 fails: any accepted input, pin, or bundle changed |
| `HP-SCOPE` | The run requires an optimizer call, a respecification, or any welfare/decomposition/EUROMOD/notebook step |

---

## 19. Synthetic-recovery boundary

**Phase 5 does not contain, approximate, or replace synthetic recovery.**

The two answer different questions. Phase 5 asks: given this specification and this sample, how precisely is the accepted parameter vector pinned down by the data? Synthetic recovery asks: if the model itself generated the data at a known parameter vector, would this estimation pipeline return that vector? Neither answer implies the other. **Standard errors can be small while the estimator fails to recover truth**, because precision is a property of the likelihood's curvature and recovery is a property of the map from parameters to observables together with the estimation route.

Governance, unchanged and unaffected by anything in this memo:

- Synthetic recovery remains mandatory before P2a promotion to a certified structural result, before any claim that the regional/access block is structurally identified, and before P2a can replace the certified pooled baseline [P4A §16], [DL D-009]. **Nothing in Phase 5 discharges it.**
- Welfare and decomposition remain non-reportable on P2a [P4A §17], [CS §10], [DL D-010]. The Phase-5 covariance is not a licence to propagate uncertainty into a welfare functional; that requires JMP-M08 and M09.
- The pooled 47-parameter specification `joint_pooled_v1_bll0_tlmpin`, negLL `238504.6360973987`, remains the formal certified baseline [CS §4]. Phase-5 results do not promote P2a.
- Phase-4 identification evidence is **local** at a point estimate and is not a global-identification claim [P4A §14].

**Downstream declaration, pre-registered** [plan S-10]. Delta-method propagation into M08/M09 will consume the 35 × 35 interior covariance. The two active-bound coordinates enter downstream functionals as fixed, and the ten pins likewise.

**The correct statement about what this omits is a conditionality statement, not a directional one** [review §9, §14]. Downstream inference built on this covariance is **conditional** on the two active-set restrictions and on the ten pins, and it **excludes active-set and specification uncertainty, whose magnitude and direction are not identified here.** No claim is made that fixing these coordinates understates decomposition uncertainty, and none that the omission has a known direction. Under genuine population strict activity, treating the boundary coordinates as fixed *is* the first-order asymptotic law of the constrained estimator and does not automatically understate sampling variance; if active-set selection is non-negligible, no general directional ordering follows. For the structurally inapplicable pins, the current likelihood contains no information at all in those directions (§12.3), so relative to some different unconstrained or respecified model, uncertainty is not ordered without further assumptions.

**Two-tier pre-registered trigger** [review §9]:

- **Tier 1 — disclose and consider sensitivity.** If any pinned or active-bound coordinate loads materially on a welfare or opportunity functional, M08/M09 must disclose the conditioning explicitly and consider bound and specification sensitivity. **Material loading alone does not establish that resampling is required**, and does not establish that the omitted uncertainty is positive in any known direction.
- **Tier 2 — boundary-aware or resampling inference becomes required.** This is triggered if, and only if, the paper seeks (i) inference on a bound coordinate itself; (ii) an unconditional claim that integrates over active-set selection; or (iii) a functional for which the strict-activity assumption is not defensible. X-005 currently defers the decomposition bootstrap [DL X-005]; Tier 2 is the condition under which that deferral must be revisited, and Tier 1 is not.

For the paper claims permitted in §20.1 — all of which are explicitly conditional and none of which is inference on the two bound coordinates — **no alternative boundary-aware method is required** [review §9, §18].

---

## 20. Interpretation limits

### 20.1 Permitted claims

- "At the accepted France 2016 singles P2a region-live estimate, household-clustered misspecification-robust standard errors for the 35 interior free parameters are as reported, conditional on `beta_l_age2_sm` and `beta_l_age2_sf` held at their upper bound of 1.0."
- "The ten regional/urbanisation/GSUR access coordinates are jointly [significant / not significant] at the *x* % level under the H0-A omnibus test, with `q = 10`."
- "Clustering at the household is degenerate in this application: each household contributes exactly one likelihood term, so the household-cluster sandwich is algebraically identical to a household-level OPG sandwich. The estimator is household-clustered and misspecification-robust."
- "The finite-sample correction is `c = G/(G−K) = 1555/1520 = 1.0230`, a pre-registered regression-analogue convention, inflating standard errors by 1.14 %."
- "Ten coordinates are pinned restrictions with structurally zero information; standard errors are undefined for them and are reported as `NA`."
- "Reported precision is local at the accepted estimate."
- "The reported standard errors and tests are conditional on the two upper-bound restrictions and the ten pins, and exclude active-set and specification uncertainty, whose magnitude and direction are not identified here."

### 20.2 Prohibited claims

- ❌ That the ten-parameter test establishes the presence or absence of **opportunity heterogeneity of any kind**. It concerns the modelled regional/urbanisation/GSUR access block only, and the opportunity index additionally carries six occupation, five hours-offer and six wage-density coordinates [C-2], [C-5], [audit §15].
- ❌ That it is the complete opportunity-versus-preference test, or a direct test of the decomposition share [C-2].
- ❌ Any causal interpretation of the regional coefficients.
- ❌ That `gsur` is a region dummy, or that it belongs to the "across-region differences" null [F-3].
- ❌ That clustering will be non-degenerate, or that the OPG equivalence will fail, for couples or pooled years [C-3].
- ❌ Any symmetric Wald interval, z-statistic or p-value for the two active-bound coordinates [C-4].
- ❌ Presenting the conditional standard errors as unconditional. They are conditional on the two active-set restrictions and on the ten pins, and they exclude active-set and specification uncertainty (§19).
- ❌ Extending the model-based Loewner result `H_II⁻¹ ⪯ [Hs⁻¹]_II` to the **robust** covariances. No ordering is established between the reported robust sandwich and any unrestricted or boundary-aware robust alternative (§11.2).
- ❌ Asserting that fixing the bound coordinates or the pins understates downstream or decomposition uncertainty, or that the omission has a known direction. Neither is established (§19).
- ❌ Reading T-22 as evidence that the constraints are strictly active **in the population**. It is a sample numerical KKT gate (§11.5).
- ❌ Describing any of the ten pins as a normalisation, or stating that the specification has ten fixed quantities without distinguishing `theta_l_m` and the other three true normalisations outside the 47-vector [F-2].
- ❌ Any statement resting on the average negLL, or restating the `ln(101)` comparison in any form [F-1], [C-1].
- ❌ Reading Phase-5 precision as identification, as structural recovery, or as grounds for promoting P2a over the pooled baseline [P4A §14, §16, §17], [CS §4, §7].
- ❌ Any responsibility language attached to preference parameters [DL D-012].
- ❌ Any statement about occupation-specific wage densities, continuous regional labour-market conditions, couples, or pooled years [DL X-001–X-004], [CS §13].

### 20.3 Package-interface constraints carried forward

The design must be expressible in a generic `dclaborsupply` API without encoding France, EU-SILC, EUROMOD, or P2a assumptions [plan §12], [CS §11]: cluster identity is an argument, never a hard-coded `idhh`; the interface must not assume cluster count equals term count, because couples and pooled panels **may** break the degenerate case, conditional on how their primitive likelihood contributions and repeated-unit structure are defined [review §5]; the active set is an input, not inferred from France bounds, and its cardinality is not fixed at two; pins are a generic boolean mask with a generic value vector; the finite-sample correction is selectable with the chosen convention recorded in returned metadata; restriction testing takes a generic `(R, r)` pair; nothing assumes 101 alternatives, one year, one household type, or 37 coordinates. This memo states these as constraints on itself; it does not design the API, which is PKG-M02's artifact.

---

## 21. Implementation sequence

For the follow-on implementation mission. This is handoff content, not the implementation charter, which is the programme manager's artifact.

1. **Bind and verify.** Check out MNL `982c5221…` with gitlink `27756a06…`; confirm both worktrees clean; recompute and match every anchor in §18.2. Record the review-gate string and `execution_ready`.
2. **Load the parameter contract.** Read `phase4_manifest.json → contract.parameter_map` and `phase5_parameter_map_v1.csv`; build the 47 → 37 → 35 maps **by name**; compute and assert the T-17 fingerprints.
3. **Load the bread.** `np.load("hessian_free.npy")`; T-5 hash; T-6 symmetry, symmetrisation, eigen agreement; build `H_II` by name-keyed deletion; Cholesky.
4. **Build the score.** Reconstruct the accepted `tot` route with `per_group=True`; wrap in the pin-fixed free reparameterisation; `jax.jacfwd` over household-blocked chunks; stack in canonical `idhh`-ascending order; run T-2, T-3, T-11, T-15, T-16.
5. **Verify the identity.** T-1 against the recorded `gradient_free`; T-4 at the tighter `1e-12` bar. **Halt here on failure — do not proceed to covariance.**
6. **Build meat and covariances.** Select interior columns by name; form `M`; T-7; form `V_model` and `V_robust` with `c` from §10; T-8, T-9, T-10, T-18, T-19, T-22.
7. **Regional block.** Extract `V_RR` by name; individual diagnostics; H0-A, H0-B, H0-C, H0-G by Cholesky solve; T-14; W-1, W-2, W-3.
8. **Warning tier and reporting.** W-4, W-5; assemble the 47-row parameter table with `NA` discipline for the twelve non-interior rows.
9. **Dry run first.** Steps 1–8 writing only to `attempts/dryrun_<ts>/`. Inspect. Only then the single authorised real run.
10. **Finalise.** Post-evaluation recheck (T-13); write artifacts to `staging/`; enforce the exact artifact set; write `phase5_manifest.json` last with the full environment block of §18.5; compute the bundle SHA-256; promote to `complete/`; enforce the exact set again.
11. **Return.** Execution report plus bundle to the manager. No commit before acceptance.

---

## 22. Decisions requiring manager approval

| # | Decision | Recommended baseline | Status |
| --- | --- | --- | --- |
| **D-1** | Finite-sample correction | Two-factor with `N = G = 1,555`, `K = 35`, telescoping to `c = G/(G−K) = 1.0230263157894737` (§10). Scalar unchanged from v1; rationale repaired per Fix 2 | recommended; ready to freeze |
| **D-2** | Active-bound treatment | Conditional 35 × 35 sandwich; the two bound coordinates reported with `NA` and `status = active-bound`; no symmetric Wald inference (§11) | recommended; **ruled defensible by Stage-C review (§9, §18); freeze subject to targeted recheck of fixes** |
| **D-3** | Score artifact | `.npy` authoritative + committed summaries + non-authoritative `%.17g` CSV rendering; restricted-custody fallback completed per Fix 7 (§17.1) | recommended; artifact choice ready to freeze; **the disclosure route remains conditional on the determination below**, and the design is complete under either outcome |
| **D-4** | Fixed-pin representation | Literal `NA` in the five inferential fields; two structural-inapplicability categories; **no normalisation category**; mandatory footnote (§12); schema completed per Fix 4 (§17.3) | recommended; ready to freeze |
| **D-5** | Regional covariance and joint-test protocol | H0-A (`q = 10`) certified omnibus; H0-B (7), H0-C (2), H0-G (1) pre-registered secondary; `gsur` stated separately; χ² reference; joint test carries the claim (§13). Wald objects made dimensionally explicit per Fix 3; H0-B language narrowed per Fix 6 | recommended; ready to freeze |
| **D-6** | Numerical gates and tolerances | The T-/W- register of §14–§16, extending the accepted [plan §11] naming. T-4, T-7, T-9 and W-4 repaired per Fix 5; T-23 added per Fix 7; **no gate weakened** | recommended; ready to freeze |
| **D-7** | Canonical row order | `idhh`-ascending, stable argsort (§6.3) | recommended; **ratification request stands**, because it determines artifact hashes |
| **D-8** | `K` is tied to the covariance object | If D-2 is overturned toward the unrestricted 37, `K` moves to 37 in the same edit (§10.6) | recommended as a linked constraint |

**Open items, stated as such.**

1. **[C-4] independent review of D-2 — discharged, pending targeted recheck.** The Stage-C review ruled the conditional-35 object defensible for the stated estimand and confirmed each element [C-4] required: the active-bound direction and KKT consistency [review §9]; that conditioning on the active set is a coherent estimand under population strict activity [review §9]; that the correct bread is `H_II` and not a Schur complement, with the 35-column score meat [review §9]; the limits of treating the active set as fixed, now stated in §11.2, §19 and §20.2; and that **no alternative boundary-aware method is required for the limited claims permitted here** [review §9, §18]. The review states the central D-2 decision may then be frozen. What remains is the targeted Stage-C recheck of the seven fixes.
2. **The targeted Stage-C recheck has not been performed.** Review §18 conditions manager acceptance on a recheck confirming: the conditional-35 estimand unchanged; no robust Loewner or known-direction uncertainty claim remaining; the correction scalar presented as a transparent convention; all Wald matrices dimensionally conformant; the bound-reporting artifact complete; the repaired gates exact and computable; C-2/C-3/C-5 language consistent throughout; and the fallback preserving authoritative bytes under restricted custody. This memo implements all seven fixes and believes each condition met, but **it does not and cannot certify the recheck**. That is the reviewer's determination [review §19].
3. **`UNKNOWN` — disclosure status of household-level derived arrays; open with the principal investigator.** The 1,555-row score matrix is derived from EU-SILC/EUROMOD input microdata. Whether it may be committed to version control, and whether it may appear in any future public replication package, depends on the Eurostat/EUROMOD licence terms and on the repository's disclosure status. Neither is a repository fact the Stage-A audit established. **This memo does not decide it, and the Stage-C review explicitly leaves it to the principal investigator** [review §13]. It cannot block execution: the durable restricted-custody contract of §17.1 and §18.5 is specified unconditionally and gated by T-23, so the design is complete under either outcome. Standing constraint regardless: any future public release excludes household-level rows unless the determination explicitly permits them.
4. **Ratification of D-7**, since the audit explicitly required the memo to fix one of two candidate row orders [audit §14] and the choice determines every artifact hash. The review found the choice sound [review §5, §13]; ratification is nonetheless a manager act.

**Handoff content for the implementation charter** (supplied without writing the charter): scope = §2 plus §21; authoritative inputs = §3; frozen decisions = D-1 through D-8 as accepted; gates = §14–§16; artifacts = §17; transaction contract = §18; halts = §18.6; the mandatory environment-logging requirement = §18.5; non-scope = no optimizer, no respecification, no welfare, no decomposition, no synthetic recovery, no couples, no pooled years, no commit before acceptance.

---

## 23. Immediate next action

Return this memo, unmodified and **uncommitted**, together with a cover note stating the verdict, the §1.1 revision register, confirmation that no baseline changed and no gate was weakened, and any fix whose implementation surfaced a conflict with a frozen decision, to the **Goal 1 Manager chat only** — not to the deputy programme director [Stage-D instruction §5]. The user saves it to `MNL/docs/France_case/P2a/` alongside the retained v1.

Process position: Stage A closed; Stage B delivered as v1; **Stage C complete**, verdict `APPROVE AFTER FIXES` with no E2 finding; **Stage D remediation cycle 1 of 2 is this document**, leaving one cycle in reserve. The expected sequence from here is: the **targeted Stage-C recheck** of the corrected sections [review §19], which this memo does not pre-judge; then, on a clean recheck, Stage E — the Goal 1 decision packet `JMP_M05_goal_manager_acceptance_v1.md` and the return to the deputy programme director with a recommendation on whether to launch the Phase-5 implementation mission. The principal investigator's disclosure determination (§22, open item 3) may be recorded at any point before implementation; it does not gate the recheck.

Do not commit this file before the targeted recheck and manager acceptance. Do not implement Phase 5. Do not run inference.

---

**FINAL VERDICT: READY WITH OPEN DECISIONS**
