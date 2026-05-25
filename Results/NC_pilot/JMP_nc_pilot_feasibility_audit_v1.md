# JMP Next-Cycle Pilot — Read-Only Feasibility Audit v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: read-only feasibility audit. No existing files modified. No data
modified. No draws regenerated. No EUROMOD run. No estimation run. No
welfare computed. No SA2 issued. M1-clean 2016 remains the active JMP
baseline. The corrected pooled P3a track is unaffected.

---

## 1. Audit verdict

**Feasible for the 2016 couples-only pilot at 900 (30×30) product alternatives, conditional on a list of named blockers (§20).**

The two code paths to be changed (couples combine in `_reshape_couples_to_wide()`; wage draw in `enh_RURO_draws.py`) are precisely localised and quoted in §4 and §6. The marginal per-partner draws can be reused as-is for the couples product (combination-rule change only). The wage path requires a new conditional draw mechanism — not a simple parameter retune. `scipy.stats.qmc` (Halton, Sobol) is importable (scipy 1.16.2). The 2016 couples count is **2,577** confirmed directly from the parquet (§12). The five binding feasibility unknowns — EUROMOD couples-product cost, precompute scaling, gradient/Hessian cost per row, the wage-occupation double-counting identification (§11), and the offer-vs-accepted-wage construction (§9 of plan) — are design-time questions the pilot is *designed to answer*, not pre-pilot blockers. The pilot is the right instrument to resolve them.

---

## 2. Authorization scope

This audit is read-only. It is authorized by §28 of `docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md`. Actions explicitly outside scope:

- No existing file modification (verified: only one file written: this audit report).
- No data modification.
- No draw regeneration.
- No EUROMOD execution.
- No YAML modification.
- No estimation.
- No welfare computation.
- No SA2 verdict.
- No promotion of any model over M1-clean 2016.

The corrected pooled P3a track continues independently on its frozen 100-diagonal, unconditional-wage spec.

---

## 3. Files inspected

| File | Reading method | Purpose |
|---|---|---|
| `docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md` | Full read | Plan / NC-baseline / pilot scope |
| `Results/JMP_opportunity_block_readonly_diagnostic_v1.md` | Full read | Prior diagnostic evidence |
| `docs/jmp_methodology/JMP_couples_opportunity_draw_design_note_v1.md` | Full read | Diagonal-to-product design |
| `docs/jmp_methodology/JMP_conditional_wage_on_occupation_decision_note_v1.md` | Full read | Wage-conditioning decision rule |
| `scripts/enhanced/enh_RURO_draws.py` | Targeted Grep + ranged Read (lines 100–120, 543–580, 700–730, 900–940, 1023–1065, 1115–1234) | Wage / occupation / draw RNG |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Targeted Read (lines 880–1080) | Couples reshape (`_reshape_couples_to_wide()`) |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Ranged Read (lines 1–80) + targeted Grep | Split-stem prep |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | Full read (lines 1–373) | YAML blocks |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | **Bounded parquet read** (columns `idhh`, `draw`, `year_tag`) for §12 counts | 2016 couples n confirmation |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Not opened here (counts from `__mnlmeta.json` and prior diagnostic suffice) | — |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Full read | n_draws, row counts, cluster key |

Parquet reads were **bounded by column** (only `idhh`, `draw`, `year_tag` were materialised) for the 2016 couples n confirmation in §12. Singles parquet was not opened in this audit; its row count (500,700) is taken from the metadata JSON.

---

## 4. Couples combine code path

The diagonal is produced by an inner merge on `["idhh", "draw"]` in `_reshape_couples_to_wide()`, [`scripts/enhanced/enh_RURO_prep_mnl_basic.py:1058-1065`](scripts/enhanced/enh_RURO_prep_mnl_basic.py#L1058-L1065):

```python
# Merge on (idhh, draw)
merge_keys = ["idhh", "draw"]
df_wide = df_male_renamed.merge(
    df_female_renamed,
    on=merge_keys,
    how="inner",
    suffixes=("_MALE_DUP", "_FEMALE_DUP")
)
```

This pairs male draw `i` with female draw `i` only — the index-paired diagonal of the 100 × 100 joint draw space. Off-diagonal combinations (`his_i, her_j`, `i ≠ j`) are absent by construction.

Precondition checks immediately preceding the merge ([prep_mnl_basic.py:922-944](scripts/enhanced/enh_RURO_prep_mnl_basic.py#L922-L944)) enforce *exactly* 2 rows per `(idhh, draw)` (one male, one female), so the merge is well-defined and 1-to-1 within each `(idhh, draw)` key.

**Change required for product:** replace the inner merge on `["idhh", "draw"]` with a cross-join on `idhh` followed by a draw-index re-keying that constructs `draw_pair_id = (draw_male, draw_female)` — see §5.

---

## 5. Product-join feasibility

A 30×30 product is constructed by replacing the diagonal `merge(on=["idhh", "draw"], how="inner")` with the following logical steps (sketch only — no code written):

1. Subset `df_male_renamed` to draws `m ∈ {0, 1, …, 29}` and rename its draw column to `draw_male`; subset `df_female_renamed` to draws `f ∈ {0, 1, …, 29}` and rename its draw column to `draw_female`.
2. Cross-join on `idhh`: `df_wide_900 = df_male_30.merge(df_female_30, on=["idhh"], how="inner", suffixes=("_MALE_DUP","_FEMALE_DUP"))`. This produces `30 × 30 = 900` rows per `idhh`.
3. Construct a stable joint-draw key, e.g. `draw_pair_id = 30 * draw_male + draw_female` (range 0..899), so downstream consumers continue to see a single integer draw index per joint alternative.
4. Define the chosen alternative as the row where `draw_male == 0 AND draw_female == 0` (or, equivalently, `draw_pair_id == 0`) to preserve the convention that the observed couple alternative is `draw == 0`.
5. Preserve the validation invariants (exactly one male and one female per joint key; `is_chosen_male == is_chosen_female`) under the new keying.

**Reusability of marginal draws.** The marginal per-partner draws — generated by `generate_draws_long()` in `enh_RURO_draws.py` — can be **reused as-is** for the product. The diagonal is purely a combination-rule artefact of the `_reshape_couples_to_wide()` merge: the male marginal draws (100 per male) and female marginal draws (100 per female) are independent objects. A 30×30 product uses the first 30 of each. **No re-draw of marginals is required** for a combination-rule change.

**Caveat.** If the pilot also adopts an occupation-conditional wage (W1) — which is the NC-baseline plan — the wage marginal *must* be regenerated, because the current marginal samples wage from `Uniform[w_min, w_max]` unconditionally (see §6). The product-join change alone is combination-rule-only; the wage-density change requires re-running `enh_RURO_draws.py`. The two changes are bundled by intent (§17 of plan), not by code coupling — the diagonal-to-product change is feasible *in isolation* on the existing marginals; the W1 wage change is the part that forces a re-draw.

---

## 6. Wage draw code path

The unconditional wage draw is at [`scripts/enhanced/enh_RURO_draws.py:1196-1204`](scripts/enhanced/enh_RURO_draws.py#L1196-L1204):

```python
# Wages: 0 for non-employment
# For working: Uniform[w_min, w_max] if vw, else observed wage
wage_sim = np.zeros(n_sim, dtype=float)
if n_working > 0:
    if wage_spec == "vw":
        wage_sim[is_working] = rng.uniform(w_min, w_max, size=n_working)
    else:
        # Fixed wage: use observed wage
        wage_sim[is_working] = obs_wage_sim[is_working]
```

Defaults at [enh_RURO_draws.py:105-106](scripts/enhanced/enh_RURO_draws.py#L105-L106):

```python
DEFAULT_W_MIN = 2.0
DEFAULT_W_MAX = 170.0
```

The proposal-density (importance-sampling) contribution for the wage is at [enh_RURO_draws.py:1225-1234](scripts/enhanced/enh_RURO_draws.py#L1225-L1234):

```python
log_q_wage = np.zeros(n_sim, dtype=float)
if wage_spec == "vw":
    if w_max <= w_min:
        raise ValueError("w_max must be > w_min for Uniform wages.")
    log_q_wage[is_working] = -np.log(w_max - w_min)
elif wage_spec == "fw":
    # degenerate at observed wage: treat as "not sampled" for proposal accounting
    log_q_wage[:] = 0.0
else:
    raise ValueError("Unsupported wage_spec.")
```

The wage is drawn from `Uniform[2, 170]` unconditionally — no dependence on `loc4`, education, experience, sex, or any covariate.

**W1 occupation-intercept wage draw — what it requires.** Three pieces:

1. **A fitted W1 model** — either externally pre-fit (Mincer with `delta_occ2/3/4` on the accepted-wage sample, common Mincer slopes) or fit at draw time on the observed-wage subset. The plan flags the accepted-wage approximation explicitly (§9 of the plan).
2. **A new sampling distribution per working draw** — sample log w from `Normal(X_i β + δ_{loc4_i}, σ²)` and exponentiate, where `X_i` is the simulated person's `educL`, `educH`, `pexp_years`, `pexp_years2` and `loc4_i` is the simulated occupation (which equals the observed occupation under `occ_spec="fixed"`; see §9).
3. **A matching proposal-density term** — `log_q_wage[is_working] = log_normal_pdf(wage_sim[is_working]; mean_i, sigma)`. The current uniform-density term `-log(w_max - w_min)` must be replaced; otherwise the importance-sampling correction becomes inconsistent with the proposal.

**Two-group wage draw — what it requires.** Same three pieces, but with the mean equation
`X_i β + δ_{NonInt} · 1[loc4_i = 4]` — one occupation parameter instead of three. The sampling and proposal-density steps are identical in shape; only the mean equation differs.

**Common requirement (both W1 and two-group).** The fitted Mincer must be available *before* draws are generated. This adds a pre-draw step to the pipeline (fit Mincer → write coefficients → consume in `enh_RURO_draws.py`). The coefficients must be tagged with their fitting set (which years, which population) so the draw stage is auditable.

---

## 7. W1 occupation-intercept wage draw requirements

Restating §6 as a requirements list:

- Reference category: `loc4 = 1` (Routine-Manual), matching the existing `occupation_opportunity` block.
- Three added wage-mean parameters: `delta_occ2`, `delta_occ3`, `delta_occ4`.
- Common Mincer slopes on `educL`, `educH`, `pexp_years`, `pexp_years2`.
- A single common `sigma` for the pilot (per §12 of the plan); occupation-specific sigma is a separate variant (S-occ, §16 of plan) and is not required for the W1 pilot itself.
- Mincer must be fit on the **working singles + working couples** observed (draw=0) sample, restricted to `loc4 ∈ {1,2,3,4}` and `wage > 0`. The pilot is 2016-only (§25 of plan), so the Mincer fit may be either 2016-only or pooled — record the choice in the spec contract.
- The fitted coefficients are an **explicit data-build input**, not a free estimation parameter at the structural stage. The spec contract must state whether the structural model re-estimates `delta_occ*` (free) or treats them as fixed draw-distribution parameters (calibrated). This is the §11 double-counting question.

---

## 8. Two-group wage alternative requirements

Same as §7 but with a single occupation parameter `delta_NonInt` attached to the indicator `1[loc4 = 4]`. All other loc4 values share the reference mean. The reference category in §7's mean equation absorbs `loc4 ∈ {1, 2, 3}`.

This is the parsimony variant motivated by the §11 diagnostic finding that RM vs NRM IQR overlap is 87–97 % and Intel vs the rest is modest — the binding empirical separation is `loc4 = 4` vs the rest. Two-group ships one wage parameter where W1 ships three.

---

## 9. `occ_spec="fixed"` confirmation

Default at [enh_RURO_draws.py:114](scripts/enhanced/enh_RURO_draws.py#L114):

```python
DEFAULT_OCC_SPEC = "fixed"  # "fixed" or "empirical"
```

The fixed-occupation branch is the *default* path at [enh_RURO_draws.py:1119-1124](scripts/enhanced/enh_RURO_draws.py#L1119-L1124):

```python
# -------------------------------------------------------------------------
# Occupation draws (Case B)
# -------------------------------------------------------------------------
# Default: keep observed occupation for working draws; enforce -1 for non-employment
occ_sim = occ_obs_sim.astype(np.int16, copy=True)
log_q_occ = np.zeros(n_sim, dtype=float)
```

`occ_obs_sim` is the observed (draw=0) occupation per person, replicated across the draw index. The `if occ_spec == "empirical":` block at line 1125 is only entered if explicitly requested; under the default `"fixed"`, working simulated draws *inherit* the observed `loc4` and `log_q_occ` is zero (no proposal-density contribution from occupation).

Non-employment override at [enh_RURO_draws.py:1178-1180](scripts/enhanced/enh_RURO_draws.py#L1178-L1180):

```python
# enforce non-employment convention
occ_sim[is_nonemployment] = -1
log_q_occ[is_nonemployment] = 0.0
```

Confirmed: under the pilot's intended `occ_spec="fixed"`, occupation is not resampled across working draws. Every working draw for person `p` has `loc4 = observed_loc4_p`.

---

## 10. `loc4` placement confirmation

**`wage_opportunity` block — no `loc4` term** ([estimation_spec_ruro_occ_P3a_pooled.yaml:88-102](scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml#L88-L102)):

```yaml
wage_opportunity:
  specification: "log_normal"
  mean_shifters:
    - variable: "intercept"
      coefficient: "beta_w0"
    - variable: "educL"
      coefficient: "beta_w_educL"
    - variable: "educH"
      coefficient: "beta_w_educH"
    - variable: "pexp_years"
      coefficient: "beta_w_pexp"
    - variable: "pexp_years2"
      coefficient: "beta_w_pexp2"
  variance:
    parameter: "sigma"
```

**`occupation_opportunity` block — all `loc4` shifters** ([estimation_spec_ruro_occ_P3a_pooled.yaml:155-206](scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml#L155-L206)):

```yaml
occupation_opportunity:
  variable: "loc4"
  reference: 1
  shifters:
    - variable: "loc4_2"
      coefficient: "beta_occ_2_sm"
      applies_to: "sm"
      interaction: ["working"]
    - variable: "loc4_3"
      coefficient: "beta_occ_3_sm"
      applies_to: "sm"
      interaction: ["working"]
    - variable: "loc4_4"
      coefficient: "beta_occ_4_sm"
      applies_to: "sm"
      interaction: ["working"]
    # ... 9 more shifters: sf (3), cm (3), cf (3)
    # 12 total = 4 sub-groups (sm, sf, cm, cf) × 3 non-reference categories
```

Confirmed: `loc4` enters the choice index only through `occupation_opportunity`. The wage block has no `loc4` dependence. This is the "occupation in the opportunity layer, wage drawn independently of it" case.

---

## 11. Wage-occupation double-counting surface

**Current placements of `loc4` in the choice index (P3a):**

| Block | Coefficient(s) | Variable | Channel | Sub-groups |
|---|---|---|---|---|
| `occupation_opportunity` | `beta_occ_2_sm`, `beta_occ_3_sm`, `beta_occ_4_sm` | `loc4_2/3/4` × `working` | **Opportunity weight** (log-linear shifters in market-opportunity index) | singles male |
| `occupation_opportunity` | `beta_occ_2_sf`, `beta_occ_3_sf`, `beta_occ_4_sf` | `loc4_2/3/4` × `working` | Opportunity weight | singles female |
| `occupation_opportunity` | `beta_occ_2_cm`, `beta_occ_3_cm`, `beta_occ_4_cm` | `loc4_2/3/4` × `working` | Opportunity weight | couples male |
| `occupation_opportunity` | `beta_occ_2_cf`, `beta_occ_3_cf`, `beta_occ_4_cf` | `loc4_2/3/4` × `working` | Opportunity weight | couples female |

Twelve parameters; reference `loc4 = 1`. `loc4` does **not** appear in: `wage_opportunity`, `consumption`, `leisure`, `hours_opportunity`, `market_opportunity`, `couples.leisure_interaction`.

**Where W1 `delta_occ*` would enter (NC-baseline, planned):**

| Block | Coefficient(s) | Variable | Channel |
|---|---|---|---|
| `wage_opportunity.mean_shifters` (new) | `delta_occ2`, `delta_occ3`, `delta_occ4` | `1[loc4=2]`, `1[loc4=3]`, `1[loc4=4]` | **Wage level** (mean of log-normal wage draw → enters consumption via disposable income) |

For G2 (two-group), the single parameter `delta_NonInt` on `1[loc4=4]` plays the wage-level role; the opportunity-weight `beta_occ_*` block is unchanged.

**Double-counting risk.** `delta_occ*` and `beta_occ_*` are both functions of `loc4`. Under `occ_spec="fixed"`, the channels are conceptually distinct:

- `delta_occ*` shifts the **wage level** within the person's fixed occupation; this changes disposable income for every draw at that fixed `loc4`.
- `beta_occ_*` shifts the **opportunity weight** of the `loc4` category in the market-opportunity index; this changes the probability mass on alternatives carrying that `loc4`.

These channels enter the choice index at different terms (wage→consumption→utility vs opportunity shift directly in the index). In principle they are separately identifiable; in practice, separate identification must be **verified**, not assumed. The pilot must include the separate-identification check called for in §11 of the plan (information-matrix diagonals on `delta_occ*` and `beta_occ_*`; correlation of estimates across the three starts; comparison of `delta_occ*` against pre-fitted Mincer values to flag drift).

**Fallback if not separately identified:** the plan's §11 directive — keep `beta_occ_*` in the opportunity layer, drop `delta_occ*` as a *free* structural parameter, and instead bake the occupation-conditional offer density into the **draw construction** (empirical Mincer-fit fixed at the draw stage; not re-estimated structurally). The plan flags this as the most likely resolution if identification fails.

---

## 12. 2016 couples count and projected row counts

**Confirmed directly from the parquet** (`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`, columns `idhh`, `draw`, `year_tag` materialised, draw=0 rows):

| year_tag | Year | Couples (draw=0 rows) |
|---|---|---|
| 1 | 2015 | 2,566 |
| 2 | **2016** | **2,577** |
| 3 | 2017 | 2,295 |
| All | pooled | 7,438 |

The plan's working figure of 2,577 for 2016 couples is **confirmed**.

**Projected pilot row counts (2016 couples only, singles unchanged):**

| Product size | Alts/couple | 2016 couples rows | Multiple vs current |
|---|---|---|---|
| Diagonal (current 100) | 100 | 257,700 | 1× |
| Product 20 × 20 | 400 | 1,030,800 | 4× |
| Product 30 × 30 | 900 | 2,319,300 | 9× |
| Product 40 × 40 | 1,600 | 4,123,200 | 16× |
| Product 100 × 100 | 10,000 | 25,770,000 | 100× |

For reference (not the pilot scope), pooled three-year couples row counts:

| Product size | Alts/couple | Pooled couples rows |
|---|---|---|
| Diagonal (current 100) | 100 | 743,800 |
| Product 30 × 30 | 900 | 6,694,200 |
| Product 40 × 40 | 1,600 | 11,900,800 |
| Product 100 × 100 | 10,000 | 74,380,000 |

---

## 13. Halton/Sobol availability

**Importable.** Confirmed in the project venv (`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`):

- `scipy` version: **1.16.2**
- `scipy.stats.qmc.Halton` — available.
- `scipy.stats.qmc.Sobol` — available.

Both support seeding and scrambling (default `scramble=True`; `seed=` argument accepts `np.random.Generator` or integer). No additional package install is required for the pilot's draw-design change.

The Sobol generator has the standard caveat that the sample size should be a power of 2 for balance properties (with `scramble=True` this is less strict, but the discrepancy properties are best at powers of 2). For 30×30 = 900, neither 30 nor 900 is a power of 2; for the per-partner marginal of 30, a Sobol-30 is acceptable as a randomised slice but is not the "balanced" Sobol sample. Halton is less sensitive to non-power-of-2 lengths and may be the lower-friction default. The spec contract decision is sequence + seed + scramble.

---

## 14. Current draw RNG and seed handling

Singles draws: at [`enh_RURO_draws.py:906`](scripts/enhanced/enh_RURO_draws.py#L906):

```python
rng = np.random.default_rng(rng_seed)
```

`rng_seed` defaults via `DEFAULT_RNG_SEED` (see args parser at line 1447). Couples receive a different seed: [`enh_RURO_draws.py:1567`](scripts/enhanced/enh_RURO_draws.py#L1567):

```python
rng_seed=args.rng_seed + 1,  # different seed for couples
```

The seed is logged into the per-run JSON metadata (`"seed": args.rng_seed` at line 1508; `args.rng_seed + 1` at line 1591), so the current draws are reproducible and auditable. The RNG is `numpy.random.default_rng` (PCG64). Switching to Halton/Sobol is a localised change at the four `rng.uniform(...)` call sites (state, hours, wage, and the `rng.choice` for empirical occupation at line 577) plus a Sobol/Halton initialiser. The seed-and-log discipline is already in place.

---

## 15. Precompute and estimator row-count scaling

The pilot's row-count increase falls on:

1. **`precompute_data_couples()`** at [`scripts/enhanced/estimation_utils.py:902`](scripts/enhanced/estimation_utils.py#L902) — materialises the couples design matrices (Box-Cox transforms, region/year dummies, shifter products) at the parquet row count. Memory and one-time CPU scale linearly with rows. At 9× rows (900 alts), expect roughly 9× wall time and 9× transient memory in this step for couples. Singles precompute (`precompute_data_singles`, line 558) is unaffected.

2. **`compute_log_sum_exp_by_group()`** at [`estimation_utils.py:1494`](scripts/enhanced/estimation_utils.py#L1494) and the numba-jitted kernel `_compute_lse_numba` at line 1467 — the per-iteration LSE step iterates over choice groups; cost scales with total choice rows, paid at every gradient and Hessian-vector evaluation. At 9× couples rows, expect couples LSE wall time to rise 9× (singles unchanged).

3. **`compute_choice_probabilities()`** at [`estimation_utils.py:1546`](scripts/enhanced/estimation_utils.py#L1546) — same per-iteration scaling as (2).

4. **The estimator main loop** (in `estimation_engine.py` / `gamspy_estimation_vectorized.py`, not re-read in this audit) — iterations are dominated by the LSE + gradient kernels; total estimation wall time scales approximately linearly with total choice rows for the couples block.

5. **The covariance computation (sandwich SE)** — Hessian construction iterates choice rows once; same 9× factor on the couples portion.

The singles portion of the model is unaffected by the couples product (singles draws remain 100/individual; singles parquet unchanged at 500,700 rows).

**Empirical-budget unknown.** The audit cannot predict per-iteration wall time without timing — the pilot's first objective (§25 of plan) is to *measure* precompute and gradient timing on the 900-alt couples block to calibrate the budget for the full cycle. Treat the 9× factor as a worst-case row-count multiplier, not a worst-case wall-time multiplier (some kernels have fixed overheads).

---

## 16. EUROMOD rerun surface

Disposable income (`ils_dispy_male`, `ils_dispy_female` for couples; `ils_dispy_real` for singles) is the input to consumption in the utility/choice index (per `__mnlmeta.json` income routing block). For each new joint alternative `(his_job_m, her_job_f)` in the product, the household disposable income must be recomputed from EUROMOD on the new `(hours_male, wage_male, hours_female, wage_female, loc4_male, loc4_female)` combination.

**EUROMOD must rerun for every new product alternative.** This is the binding data-build cost (it is why the diagonal-to-product change is not read-only and not a quick edit). For the 2016 couples pilot at 30×30, that is **2,577 couples × 900 alternatives = 2,319,300 EUROMOD evaluations** for couples. Singles do not require re-running (singles draws are unchanged at 100/individual; singles disposable income is already computed). Pooled full cycle (later, not pilot): 7,438 × 900 = 6,694,200 evaluations.

Pre-existing EUROMOD throughput, the parallelism profile, and the wall-time estimate are out of scope for this audit. The plan's §19 names EUROMOD as the binding rerun; the audit confirms the surface and the count.

---

## 17. GSURv2 merge surface

After EUROMOD: the new product alternatives must be re-merged with GSUR to obtain the market-opportunity proxies (`gsur` and the region/year shifters already in `market_opportunity`). The GSUR variable in P3a is centred within choice set (`center_within_choice_set: true` with `proposal` weights). The choice set definition changes when alternatives go from 100 (diagonal) to 900 (product), so the centring is computed against a different choice set — the centring step is *not* a trivial copy of the P3a centred GSUR values; it must be re-run on the new product set.

Order of operations for the rebuild (read from the plan §18–§20; quoted here for surface):

1. `enh_RURO_draws.py` — regenerate marginal draws (only if wage draw changes; pure product on existing marginals does not need this).
2. EUROMOD — run on the product alternatives.
3. GSURv2 merge — re-merge market-opportunity proxies; re-centre GSUR within the new choice set.
4. `enh_RURO_prep_mnl_basic.py` — build the wide-format couples parquet under the product combine rule.
5. `prepare_pooled_estimation_ready.py` — produce the split-stem singles/couples parquets and the `__mnlmeta.json` for the pilot; verify income routing intact; verify R1 region repair re-applied if needed.

---

## 18. MNL rebuild surface

The MNL parquet rebuild in `enh_RURO_prep_mnl_basic.py` is mechanically the change in §4–§5: replace the diagonal merge with a product/cross join, re-key joint draws, preserve the validation invariants. The downstream `prepare_pooled_estimation_ready.py` is largely unchanged — it splits singles/couples and applies R1/R3 — but the *row counts* it asserts (`EXPECTED_TOTAL_ROWS = 1_244_500`, `EXPECTED_HH_YEARS = 12_445`) at [`prepare_pooled_estimation_ready.py:70-72`](scripts/maintenance/prepare_pooled_estimation_ready.py#L70-L72) are pooled-3-year diagonal expectations. For a 2016-only pilot at 900 alts, **`prepare_pooled_estimation_ready.py`'s expected-row guards must be updated** (or the pilot uses a different driver script that asserts pilot-appropriate counts). This is a small-but-real surface; the plan's spec contract should call it out explicitly.

`__mnlmeta.json` for the pilot will need `n_draws` redefined: under a 30×30 product, the natural joint-draw count is 900 (a single index over the joint draw pair), and the metadata file's existing `n_draws: 100` is no longer correct for couples. Singles `n_draws` remains 100.

---

## 19. Estimated parameter-count change

Current P3a free parameters: **55 (54 free, `beta_l0_m` at active lower bound)**. Counted from the YAML `initial_values` block (lines 212–279 of [estimation_spec_ruro_occ_P3a_pooled.yaml](scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml#L212)) plus the fixed `theta_c = 0.0` (which is not free) — matches the YAML header "55 free parameters."

Parameter-count change under candidate specs:

| Spec | Wage block | Variance | Free parameter change vs P3a | Total free parameters |
|---|---|---|---|---|
| **Current P3a (A0)** | beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2 (5) | sigma (1) | — | 55 (54 free) |
| **NC-baseline (W1)** | + delta_occ2, delta_occ3, delta_occ4 (+3) | sigma (1) | **+3 mean** | 58 (57 free) |
| **G2 (two-group)** | + delta_NonInt (+1) | sigma (1) | **+1 mean** | 56 (55 free) |
| **S-occ (NC-baseline + occ-σ)** | + delta_occ2/3/4 (+3) | sigma_1..sigma_4 (1 → 4; +3) | **+3 mean, +3 variance** | 61 (60 free) |
| **W2 (occ × sex)** | + delta_occ × sex (~+5 over W1) | sigma (1) | **+~8 mean total** | ~63 (62 free) |

Notes:
- All counts assume the wage parameters are estimated structurally (free). If `delta_occ*` are calibrated from a pre-fit Mincer and held fixed at draw time (the §11 fallback), the structural free-parameter count returns to 55.
- The `delta_occ` values must use the same reference `loc4 = 1` as `occupation_opportunity` to avoid an interpretive clash between the two blocks (see §11).
- The W2 count is approximate; sex-specific occupation intercepts could be parameterised as +3 (sex-male offset across all three occ deltas) or +6 (full sex × occ interaction); the spec contract decides.

---

## 20. Identified blockers or unknowns

**Hard blockers (must be resolved in the spec contract before any build is authorized):**

1. **Wage-occupation double-counting / separate identification (§11).** The decision whether `delta_occ*` is a *free* structural parameter or a *calibrated* draw-distribution input is not made by this audit and is not made by the diagnostic. The plan flags it; the spec contract must resolve it. If left ambiguous, the pilot will hit an identification issue that the diagnostics may or may not surface cleanly.

2. **Accepted-wage vs offer-wage object for the Mincer fit (§9 of plan).** The W1 fit on accepted wages is an approximation to the offer distribution. Whether the pilot ships with this approximation (labelled) or with a selection-corrected offer Mincer is a spec-contract decision. The diagnostic does not have the selection model in scope.

3. **Joint-draw indexing convention.** The current code assumes a single integer `draw` per couple-row, with `draw == 0` being the chosen alternative. The product introduces a joint key `(draw_male, draw_female)`. Downstream code that consumes `draw == 0` semantics (search across the precompute, estimation, post-estimation code) must be audited for any hard-coded reliance on the single-integer `draw` column. This audit did not exhaustively grep that surface.

4. **`prepare_pooled_estimation_ready.py` row-count guards.** Hard-coded `EXPECTED_TOTAL_ROWS = 1_244_500` and friends ([prepare_pooled_estimation_ready.py:70-72](scripts/maintenance/prepare_pooled_estimation_ready.py#L70-L72)) will raise on the pilot parquet. Either the script gains a `--pilot` mode with different expectations, or the pilot uses a separate driver. Not a deep blocker but explicit work.

5. **Couples-only pilot vs pooled wage fit.** If the Mincer (W1) is fit pooled (2015–2017) but the pilot rebuild is 2016 only, the pilot's wage draws use coefficients informed by years not in the pilot. This is fine as a design choice (it actually strengthens the wage fit), but it must be documented; if instead the Mincer is fit 2016-only, sample sizes per `loc4` cell are smaller and some cells (Intel-Male n=104 in singles, per the diagnostic) become thin.

**Softer unknowns (the pilot is designed to measure these):**

6. EUROMOD throughput on 2,319,300 couples × 1 year — unknown wall time.
7. Precompute and gradient/Hessian wall time at 9× couples rows — unknown without timing.
8. Stability of the simulation-consistency check (400 → 900 → 1,600) for the W1 + product spec — unknown without building it.
9. Whether the Halton/Sobol product point count needed for stable estimates is *less* than 900 — possible (one of the key motivations for low-discrepancy draws), but unknown without measurement.

**Non-blockers explicitly checked:**

- `scipy.stats.qmc` import: OK (§13).
- 2016 couples n: confirmed at 2,577 (§12).
- Marginal-draw reuse for product (no re-draw needed if wage is unchanged): OK (§5).
- Seed/RNG discipline: already in place (§14).

---

## 21. Feasibility verdict for 2016 couples-only pilot

**Feasible**, with the qualifications in §20. The two code-path changes are precisely localised and quoted. The library dependencies are in place. The 2016 couples n is confirmed. The marginal draws are reusable for the product-rule change (no re-draw of marginal draws is required for the combination-rule change alone; the W1 wage change does force a re-draw, but it is a planned bundled change). The expected row-count growth is 9× on the couples block only; singles are unchanged.

The two binding *technical* questions the pilot is designed to resolve — wage-occupation double-counting identification, and computational budget at 9× couples rows — are the right questions for the pilot to settle, not pre-pilot blockers. The hard spec-contract decisions (§20 items 1–5) are decision items, not feasibility blockers; they are work to do before authorizing the build, not reasons the build cannot be done.

**Recommendation (not authorization):** the pilot can proceed once the spec contract resolves §20 items 1–5. Until then, the pilot itself is not built and M1-clean 2016 remains the active baseline.

---

## 22. What was not executed

- No existing file modification (only this audit report was written).
- No data modification.
- No draw regeneration.
- No EUROMOD run.
- No GSURv2 merge.
- No MNL rebuild.
- No estimation.
- No welfare computation.
- No SA2 verdict.
- No YAML modification.
- No promotion of any model over M1-clean 2016.

Parquet reads were limited to columns `idhh`, `draw`, `year_tag` of the couples parquet for the 2016 couples-n confirmation. No other parquet was opened in this audit. No write was made to data directories or estimation directories.

---

## 23. Immediate next task

The next deliverable per §28 of the plan is the **pilot spec contract + data-build authorization** (`RURO_model_spec_contract_v3_NC.md` or similar), not code. That document must resolve §20 items 1–5 (double-counting, accepted-vs-offer wage object, joint-draw indexing convention, `prepare_pooled_estimation_ready.py` row guards, and the Mincer fitting set). This audit and the design memo (`docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md`) are its inputs; neither replaces it.

Independent of that next-cycle track, the corrected pooled P3a track continues on its frozen 100-diagonal, unconditional-wage spec toward its fresh strict post-estimation review / SA2-readiness verdict.

---

**Required final statements:**

- This was read-only.
- No existing files were modified.
- No data were modified.
- No draws were regenerated.
- No EUROMOD was run.
- No estimation was run.
- No welfare was computed.
- No SA2 was issued.
- M1-clean 2016 remains the active baseline.
- The corrected pooled P3a track is unaffected.

---

*Status: read-only feasibility audit v1. Produced 2026-05-22. Authorization: §28 of `docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md`. Output is text-only and modifies no other artefact in the repository.*
