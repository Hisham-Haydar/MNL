# JMP Opportunity Block — Read-Only Diagnostic v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: read-only diagnostic. No estimation, no data modification,
no welfare computation, no SA2, no canonical-model change. M1-clean 2016
remains the active JMP baseline throughout.

---

## 1. Diagnostic verdict

**Part A — Wage-offer structure: W1 warranted; W2 supported as refinement.**

The occupation-conditional log-wage distributions are materially separated
(η² = 15.87% overall, 14.96% male, 17.57% female). The Non-Intellectual
occupation (loc4 = 4) is separated from all others by a mean log-wage gap
exceeding 0.26–0.39 log-units, with IQR overlap below 17% vs Routine-Manual
and Non-Routine-Manual. Adding loc4 dummies to the Mincer regression raises
R² by 0.066 (F = 127.87, p < 1×10⁻¹⁶). The pre-committed decision rule
(§4 of the design note) is triggered: **adopt occupation-conditional wage draws
in the next rebuild cycle**.

The current wage block (`wage_opportunity`) has five common parameters and a
single `sigma`. Occupation enters the model only through the `occupation_opportunity`
block (separate log-linear shifters), not through the wage equation. This is
the "occupation in opportunity layer" case described in the design note —
the case where conditioning wages on occupation is most directly required
for internal consistency.

**Part B — Couples draw structure: Classification A confirmed.**

The couples estimation-ready parquet is in wide format. Each row is one
(couple-year, draw-index) with male and female fields side-by-side. The
draw index is shared: his draw *i* is always paired with her draw *i*. This
is the index-paired diagonal. Off-diagonal combinations (his draw *i*, her
draw *j*, *i* ≠ *j*) are absent by construction. The code path that produces
this is the `(idhh, draw)` inner-merge in `_reshape_couples_to_wide()`.

**Part C — Combined implication: one bundled next-cycle rebuild.**

Both corrections (diagonal → product; unconditional → occupation-conditional
wages) are upstream of EUROMOD and the GSUR merge. They must be done in a
single data-preparation cycle, not piecemeal.

---

## 2. Authorization scope

This diagnostic is explicitly authorized as read-only by:

- `docs/JMP_conditional_wage_on_occupation_decision_note_v1.md` §4
- `docs/JMP_couples_opportunity_draw_design_note_v1.md` §7
- `Prompts/replies_GPT` (sections A, B, C), which specifies Road C:
  finish current corrected pooled diagnostics, then run a combined
  read-only audit

Actions **not authorized** by this document:
- Rebuilding data
- Re-running EUROMOD
- Modifying YAML specifications
- Running estimation
- Computing welfare
- Issuing SA2
- Replacing M1-clean 2016 as active baseline

---

## 3. Files inspected

| File | Purpose |
|---|---|
| `docs/JMP_conditional_wage_on_occupation_decision_note_v1.md` | Wage-conditioning decision rule and diagnostic protocol |
| `docs/JMP_couples_opportunity_draw_design_note_v1.md` | Couples diagonal-vs-product correction |
| `Prompts/replies_GPT` | GPT advisory (sections A, B, C); Road C sequencing |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | Active P3a spec: wage and occupation blocks |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | 500,700 rows, 148 cols; pooled singles estimation-ready data |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | 743,800 rows, 148 cols; pooled couples estimation-ready data (wide) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | n_draws=100, normalization, cluster key, income routing |
| `scripts/enhanced/enh_RURO_draws.py` | RURO draw generation: individual-level hours/wage/occupation draws |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | MNL dataset builder: couples reshape and wide-format merge |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Split-stem prep: splits unified parquet into singles/couples |

---

## 4. Current placement of loc4

The YAML specification (`estimation_spec_ruro_occ_P3a_pooled.yaml`) places
`loc4` exclusively in the **`occupation_opportunity` block**, as a set of
log-linear shifters in the joint market-opportunity index. The relevant
block:

```yaml
occupation_opportunity:
  variable: "loc4"
  reference: 1
  shifters:
    - variable: "loc4_2" / "loc4_3" / "loc4_4"
      coefficient: "beta_occ_2_sm" ... "beta_occ_4_cf"
      applies_to: sm / sf / cm / cf
      interaction: ["working"]
```

Twelve parameters cover four sub-groups (singles-male, singles-female,
couples-male, couples-female) × three non-reference occupation categories.
Reference category is loc4 = 1 (Routine-Manual).

The `wage_opportunity` block has **no `loc4` term**:

```yaml
wage_opportunity:
  specification: "log_normal"
  mean_shifters:
    - {variable: "intercept",    coefficient: "beta_w0"}
    - {variable: "educL",        coefficient: "beta_w_educL"}
    - {variable: "educH",        coefficient: "beta_w_educH"}
    - {variable: "pexp_years",   coefficient: "beta_w_pexp"}
    - {variable: "pexp_years2",  coefficient: "beta_w_pexp2"}
  variance:
    parameter: "sigma"
```

This is the design note's "occupation in opportunity layer" case: occupation
is a discrete job attribute in the opportunity index, and the wage draw is
independent of it. Internal consistency would require occupation-conditional
wage draws.

---

## 5. Current wage-opportunity specification

**Specification family:** log-normal, unconditional on occupation and sex.

**Mean equation:**
```
log w_i = beta_w0 + beta_w_educL × educL_i + beta_w_educH × educH_i
         + beta_w_pexp × pexp_years_i + beta_w_pexp2 × pexp_years2_i + ε_i
```

**Variance:** single common `sigma` across all workers, sexes, and occupations.

**Estimated values (P3a corrected, Start 1):**

| Parameter | Estimate | SE_robust |
|---|---|---|
| beta_w0 | 2.0348 | 0.0944 |
| beta_w_educL | −0.0420 | 0.0737 |
| beta_w_educH | 0.3058 | 0.0602 |
| beta_w_pexp | 0.0172 | 0.0087 |
| beta_w_pexp2 | −0.0002 | 0.0002 |
| sigma | 0.4033 | 0.0015 |

No sex-specific wage coefficients; no occupation-specific intercepts; no
occupation-specific sigma. The five-parameter Mincer block treats all workers
as drawing from the same log-wage distribution after conditioning on education
and experience.

---

## 6. Observed wage sample used

**Source:** draw=0 rows in the singles parquet (chosen/observed alternatives).
Restricted to:
- `loc4` ∈ {1, 2, 3, 4} (working occupation codes only; excludes loc4 = −1
  non-worker and loc4 = −2 unknown-working stubs)
- `wage` > 0

**Sample counts:**

| Subsample | n |
|---|---|
| Working singles (pooled) | 4,611 |
| Working males | 2,048 |
| Working females | 2,563 |
| Year 2015 | 1,511 |
| Year 2016 | 1,560 |
| Year 2017 | 1,540 |

Wage variable used: `wage` (= `yivwg`, hourly wage in EUR/hour). Log-wage
computed as `log(wage)`. These are **accepted/chosen wages** (the
selected-on-employed distribution), not the offer distribution. This
downward-selection caveat is noted where relevant.

Additionally verified in the couples parquet (draw=0, wide format):
- Working male partners (loc4_male ∈ {1,2,3,4}, wage_male > 0): n = 7,134
- Working female partners (loc4_female ∈ {1,2,3,4}, wage_female > 0): n = 7,141

---

## 7. Wage distributions by occupation

Log-wage summary for working singles, loc4 ∈ {1,2,3,4}, all years, both sexes:

| loc4 | Label | n | Mean | Median | SD | p10 | p25 | p50 | p75 | p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Routine-Manual | 1,367 | 2.517 | 2.527 | 0.362 | 2.143 | 2.345 | 2.527 | 2.680 | 2.907 |
| 2 | Non-Routine-Manual | 684 | 2.458 | 2.496 | 0.455 | 1.991 | 2.298 | 2.496 | 2.670 | 2.839 |
| 3 | Intellectual | 446 | 2.585 | 2.581 | 0.317 | 2.266 | 2.432 | 2.581 | 2.749 | 2.911 |
| 4 | Non-Intellectual | 2,114 | 2.848 | 2.839 | 0.402 | 2.393 | 2.623 | 2.839 | 3.094 | 3.325 |

Key observation: loc4 = 4 (Non-Intellectual) occupies a clearly higher wage tier.
loc4 = 1 (Routine-Manual) and loc4 = 2 (Non-Routine-Manual) are close. loc4 = 3
(Intellectual) is intermediate, closer to loc4 = 1/2 than to loc4 = 4.

---

## 8. Wage distributions by sex

Log-wage summary for working singles, pooled occupations:

| Sex | n | Mean | Median | SD | p10 | p25 | p50 | p75 | p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| Male (dgn=1) | 2,048 | 2.711 | 2.684 | 0.428 | 2.257 | 2.475 | 2.684 | 2.936 | 3.229 |
| Female (dgn=0) | 2,563 | 2.631 | 2.626 | 0.422 | 2.210 | 2.407 | 2.626 | 2.856 | 3.136 |

The unconditional gender gap is 0.080 log-units (≈ 8.0%). The sex difference
is real but secondary to the occupation separation (see §11). The Mincer
regression confirms that adding sex after baseline (Regression C) raises R²
by 0.011, while adding loc4 (Regression B) raises R² by 0.066.

---

## 9. Wage distributions by occupation and sex

Log-wage summary for working singles, by loc4 × dgn:

| Sex | loc4 | n | Mean | SD | p25 | p50 | p75 |
|---|---|---|---|---|---|---|---|
| Male | 1 (RM) | 838 | 2.567 | 0.360 | 2.389 | 2.586 | 2.757 |
| Male | 2 (NRM) | 195 | 2.530 | 0.443 | 2.312 | 2.545 | 2.698 |
| Male | 3 (Intel) | 104 | 2.595 | 0.383 | 2.384 | 2.627 | 2.798 |
| Male | 4 (NonInt) | 911 | 2.895 | 0.416 | 2.659 | 2.885 | 3.142 |
| Female | 1 (RM) | 529 | 2.437 | 0.352 | 2.276 | 2.444 | 2.627 |
| Female | 2 (NRM) | 489 | 2.429 | 0.456 | 2.290 | 2.478 | 2.654 |
| Female | 3 (Intel) | 342 | 2.582 | 0.295 | 2.440 | 2.568 | 2.721 |
| Female | 4 (NonInt) | 1,203 | 2.812 | 0.387 | 2.594 | 2.793 | 3.033 |

Also confirmed in the couples parquet (draw=0 wide, male/female partners):

| Gender | loc4 | n | Mean | SD | p25 | p50 | p75 |
|---|---|---|---|---|---|---|---|
| Couple-Male | 1 (RM) | 2,626 | 2.596 | 0.351 | 2.422 | 2.604 | 2.769 |
| Couple-Male | 2 (NRM) | 560 | 2.577 | 0.370 | 2.410 | 2.587 | 2.772 |
| Couple-Male | 3 (Intel) | 285 | 2.688 | 0.278 | 2.539 | 2.673 | 2.837 |
| Couple-Male | 4 (NonInt) | 3,663 | 2.942 | 0.413 | 2.688 | 2.917 | 3.172 |
| Couple-Female | 1 (RM) | 1,226 | 2.401 | 0.397 | 2.254 | 2.420 | 2.609 |
| Couple-Female | 2 (NRM) | 1,461 | 2.388 | 0.435 | 2.288 | 2.443 | 2.620 |
| Couple-Female | 3 (Intel) | 1,069 | 2.590 | 0.314 | 2.434 | 2.601 | 2.731 |
| Couple-Female | 4 (NonInt) | 3,385 | 2.792 | 0.378 | 2.595 | 2.782 | 2.992 |

Pattern is consistent across singles and couples samples: the loc4 = 4 premium
is large and similar for both sexes; the occupation-wage pattern is not a
sex-specific artifact.

---

## 10. Wage distributions by year

Log-wage summary for working singles, by year:

| year_tag | Year | n | Mean | SD | p10 | p50 | p90 |
|---|---|---|---|---|---|---|---|
| 1 | 2015 | 1,511 | 2.664 | 0.424 | 2.238 | 2.635 | 3.180 |
| 2 | 2016 | 1,560 | 2.650 | 0.444 | 2.177 | 2.639 | 3.177 |
| 3 | 2017 | 1,540 | 2.686 | 0.410 | 2.267 | 2.670 | 3.176 |

Year-to-year differences are small (0.014–0.036 log-units on mean, 2.5 EUR/h
range at median). The year-conditional wage distribution is stable across the
three pooled years. This is consistent with the design note's decision to
pool years. No year-specific wage conditioning is indicated.

---

## 11. Occupation wage-separation diagnostics

### One-way ANOVA (log wage on loc4)

| Sample | F | p-value | η² | Classification |
|---|---|---|---|---|
| All singles (pooled sex) | 289.65 | 2.99×10⁻¹⁷² | 0.159 (15.9%) | Materially separated |
| Singles male | 119.84 | 1.70×10⁻⁷¹ | 0.150 (15.0%) | Materially separated |
| Singles female | 181.83 | 7.16×10⁻¹⁰⁷ | 0.176 (17.6%) | Materially separated |
| Couples male | 478.90 | 1.67×10⁻²⁸³ | 0.168 (16.8%) | Materially separated |
| Couples female | 536.25 | 2.68×10⁻³¹⁴ | 0.184 (18.4%) | Materially separated |

All η² values exceed the 0.10–0.15 "materially separated" threshold from the
design note. The design note's pre-committed decision rule is triggered.

### Pairwise mean gaps and IQR overlap (singles, pooled sex)

| Pair | Mean gap (log-units) | IQR overlap | Verdict |
|---|---|---|---|
| RM vs NRM | −0.059 | 97% / 87% | Near-identical; same group |
| RM vs Intel | +0.068 | 74% / 78% | Modest separation |
| **RM vs NonInt** | **+0.331** | **17% / 12%** | **Strongly separated** |
| NRM vs Intel | +0.128 | 64% / 75% | Moderate separation |
| **NRM vs NonInt** | **+0.391** | **13% / 10%** | **Strongly separated** |
| Intel vs NonInt | +0.263 | 40% / 27% | Meaningful separation |

The primary separation is loc4 = 4 (Non-Intellectual) vs the rest. RM and NRM
are nearly indistinguishable on wages (IQR overlap >87%), so a two-group
wage structure (NonInt vs others) might capture most of the variation. A
four-group structure is the full fix; a two-group structure is the
parsimonious fix.

---

## 12. Descriptive Mincer regressions

OLS on log wage, working singles only, pooled years and sexes. Covariates:
`educL`, `educH`, `pexp_years`, `pexp_years2` (baseline). n = 4,611.

| Regression | Covariates | n | R² | sigma | ΔAIC |
|---|---|---|---|---|---|
| A: baseline | educL, educH, pexp, pexp² | 4,611 | 0.1435 | 0.3951 | — |
| B: + loc4 | A + loc4_2, loc4_3, loc4_4 dummies | 4,611 | 0.2093 | 0.3797 | −363.2 |
| C: + sex | A + dgn | 4,611 | 0.1547 | 0.3926 | −59.1 |
| D: + loc4 × sex | A + dgn + loc4 dummies + loc4×sex | 4,611 | 0.2211 | 0.3771 | −422.1 |

### F-tests

| Test | F | p-value | ΔR² | Interpretation |
|---|---|---|---|---|
| B vs A (add loc4) | 127.87 | 1.1×10⁻¹⁶ | +0.066 | Loc4 intercepts highly significant |
| C vs A (add sex) | 61.35 | 5.9×10⁻¹⁵ | +0.011 | Sex significant but smaller contribution |
| D vs B (add loc4×sex) | 13.86 | 1.8×10⁻¹³ | +0.012 | Occupation × sex interactions significant |

### Residual SD by occupation and sex (Regression B residuals)

| loc4 | Male SD | Female SD |
|---|---|---|
| 1 (RM) | 0.356 | 0.360 |
| 2 (NRM) | 0.430 | 0.458 |
| 3 (Intel) | 0.375 | 0.279 |
| 4 (NonInt) | 0.401 | 0.357 |

Residual SD is heteroskedastic across occupations: NRM has the largest residual
scatter for both sexes; Intellectual-Female has the smallest. A single `sigma`
misrepresents the within-occupation spread.

---

## 13. Wage-conditioning decision rule

Per `docs/JMP_conditional_wage_on_occupation_decision_note_v1.md` §2:

**Trigger condition met:** η² > 0.10–0.15 AND IQR overlap substantially
non-overlapping for key pairs.

- η² = 0.159 overall (>0.15 threshold). ✓
- RM vs NonInt IQR overlap 17% (strongly non-overlapping). ✓
- NRM vs NonInt IQR overlap 13% (strongly non-overlapping). ✓

**Pre-committed action:** adopt occupation-conditional wage draws in the next
rebuild cycle.

**Recommended structural form (consistent with GPT advisory, section A):**

```
W1 (primary): log w_i = X_i β + δ_{occ} + ε_i
    — common Mincer slopes, occupation-specific intercepts
```

```
W2 (refinement if sample supports): log w_i = X_i β + δ_{occ,s} + ε_i
    — sex-specific occupation intercepts
```

W2 is supported by the data (F = 13.86 for loc4 × sex interactions) but adds
8 parameters over W1. Given the small cell sizes for some groups (Intel-Male:
n = 104 in singles), W1 is the recommended first step.

The single `sigma` should be revisited in the next cycle; residual SDs differ
by occupation group. Whether to use occupation-specific sigmas or a single
sigma is a parameter-count decision for the specification memo.

**What is not decided here:** the exact implementation of occupation-conditional
wage draws (whether from observed empirical frequencies, a Mincer-fitted
distribution, or parametric draws from the estimated W1 equation). That is
a next-cycle specification memo item.

---

## 14. Couples current alternative count

From the metadata and parquet:

| Quantity | Value |
|---|---|
| n_draws per person | 100 (indices 0..99; draw=0 is observed) |
| Couple-years (pooled) | 7,438 |
| Unique households (idhh) | 5,838 (across 3 pooled years) |
| Couples rows in parquet | 743,800 = 7,438 × 100 |
| Alternatives per couple-year | 100 |
| Format | WIDE: one row per (couple-year, draw-index) |

Each row contains both male and female fields for draw index `i` (columns
`_male`, `_female`). The draw index is shared. This is the diagonal.

For reference, product-sample alternatives counts:

| Product size | Alts / couple | Couples rows (pooled) |
|---|---|---|
| Diagonal (current) | 100 | 743,800 |
| Product 30 × 30 | 900 | 6,694,200 |
| Product 40 × 40 | 1,600 | 11,900,800 |
| Product 100 × 100 | 10,000 | 74,380,000 |

---

## 15. Couples draw-construction code path

The draw construction proceeds in two stages:

**Stage 1 — Individual draws (`enh_RURO_draws.py`):**
`generate_draws_long()` generates N draws per individual (head or partner)
independently. For each decider, draws 1..99 are simulated (hours ~ Uniform,
wage ~ Uniform[2, 170] if `wage_spec=vw`, occupation fixed at observed baseline
since `occ_spec=fixed`). Draw 0 is the observed alternative.

Key default: `occ_spec = "fixed"` → working simulated draws keep the
observed occupation. No occupation is sampled from empirical frequencies.
This means both the occupation and the wage are at the draw level (the
same individual-level draw index), but occupation is not varied for working draws.

**Stage 2 — Couples wide reshape (`enh_RURO_prep_mnl_basic.py`, function
`_reshape_couples_to_wide()`):**

The long format (2 rows per household-draw: one male, one female) is reshaped
to wide format by:

```python
# Lines 1058–1065 of enh_RURO_prep_mnl_basic.py
df_wide = df_male_renamed.merge(
    df_female_renamed,
    on=["idhh", "draw"],
    how="inner",
    suffixes=("_MALE_DUP", "_FEMALE_DUP")
)
```

This `inner` merge on `["idhh", "draw"]` pairs male draw index `i` with
female draw index `i` for every household. It is the precise code path
that produces the diagonal.

**Validation in `_validate_couples_draw_consistency()`** confirms that both
partners have the same draw set {0, 1, ..., 99} per household — this
consistency check verifies the diagonal structure, not the product.

---

## 16. Diagonal/product classification

**Classification: A — Index-paired diagonal.**

Evidence:

| Evidence type | Finding |
|---|---|
| Parquet row count | 743,800 = 7,438 × 100; 1 row per (couple-year, draw-index) |
| Wide format | Both `_male` and `_female` columns in same row |
| Draw indices | Shared draw index per row (his draw_i is always paired with her draw_i) |
| dgn distribution | All rows have dgn = 1.0 (wide format; dgn refers to head) |
| Code path | `_reshape_couples_to_wide()` merges on `["idhh", "draw"]` |
| Off-diagonal check | No row represents (his draw_i, her draw_j, i ≠ j) |

The full product space would be 7,438 × 100 × 100 = 74,380,000 rows —
100× larger than the current parquet. The current construction samples only
the 1% of the product space that lies on the diagonal.

This is not a product subsample (classification C). It is the worst-case
subsample: a one-dimensional curve through the joint space that imposes
maximal partner-draw dependence (his draw 1 is perfectly correlated with
her draw 1). The design note (§1) correctly identifies this as a
specification error, not a simulation-accuracy issue.

---

## 17. Shared next-cycle rebuild implications

Both corrections share the same upstream pipeline:

```
enh_RURO_draws.py  →  enh_RURO_euromod.py  →  GSURv2 merge  →
enh_RURO_prep_mnl_basic.py  →  prepare_pooled_estimation_ready.py
```

**Correction 1 (diagonal → product):** change the combination rule in
`_reshape_couples_to_wide()` from `merge on ["idhh", "draw"]` (diagonal)
to a product or randomised product sample. This affects only the couples
pipeline, but it requires re-running EUROMOD on the new joint alternatives
to obtain their disposable incomes.

**Correction 2 (unconditional → occupation-conditional wage):** change the
wage draw in `enh_RURO_draws.py` from `Uniform[w_min, w_max]` (unconditional)
to a draw from the occupation-conditional offer distribution. This requires
a fit of the W1 (or W2) Mincer model and sampling from it; it affects both
the singles and couples pipelines.

Because both changes are upstream of EUROMOD and the GSUR merge, they must
be implemented together in a single data-preparation rebuild. Implementing
one without the other leaves the opportunity mechanism partially corrected
and still internally inconsistent.

**Computational cost:** the product correction multiplies couples rows by
9× (900 alts) to 16× (1,600 alts). Combined with occupation-conditional
wages, the per-iteration evaluation cost increases accordingly. The
design note (§5) recommends treating these as joint choices against one
computational budget.

**Recommended pilot first:** build the corrected pipeline for 2016 couples
only, at 900 alternatives (30 × 30 product), with W1 occupation wage
intercepts. Verify EUROMOD run, GSURv2 merge, precompute timing, and
gradient evaluation time before committing to a full P3a pooled rebuild.

---

## 18. Recommended next gate

**Immediate:** no action on current estimation. Let the corrected pooled P3a
baseline remain on the frozen 100-diagonal spec. The M1-clean 2016 baseline
is unaffected.

**Next task:** write one consolidated next-cycle opportunity respecification
plan (in ChatGPT or Claude project chat), attaching this diagnostic and the
design notes. The plan should specify jointly:

1. Couples choice set = product sample (not diagonal). Candidate sizes: 900
   (30×30) or 1,600 (40×40), sized by simulation-consistency check. Consider
   Halton/Sobol draws to reduce required count.
2. Wage-offer structure = W1 (occupation intercepts, common Mincer slopes).
   Four intercepts (one per loc4) plus a decision on sigma (common or
   occupation-specific).
3. Sex-specific wage equation (W2) as an alternative to test if W1 pilot
   runs cleanly.
4. Pilot scope: 2016 couples only, 900-alternative product, W1 wages.

The recommended file for the plan:
`docs/JMP_next_cycle_opportunity_respecification_plan_v1.md`

---

## 19. What was not executed

- No structural MNL estimation.
- No EUROMOD execution.
- No data rebuild.
- No YAML specification was modified.
- No welfare computation.
- No SA2 evaluation.
- No draws were regenerated.
- No occupation-conditional wage model was estimated (the Mincer regressions
  in §12 are descriptive OLS diagnostics only; they are not the structural
  model and do not alter any estimated parameters).
- No figures or density plots were generated (the diagnostic is text-only
  as requested).

---

## 20. Required final statements

**M1-clean 2016 remains the active JMP baseline.** The corrected pooled P3a
model (ruro_occ_P3a_pooled) is a candidate empirical baseline under evaluation;
it does not displace M1-clean until a full SA2 verdict is issued.

**The corrected pooled P3a estimation is not affected by this diagnostic.**
The diagnostic reads existing parquets and produces no changes to the frozen
spec, the estimation outputs, or the SE artifacts.

**No welfare computation is authorized.** Welfare requires SA2 passage.
SA2 is not issued here.

**No SA2 is issued here.** The diagnostic is a data-structure audit, not
a post-estimation verdict.

**The diagonal-to-product and wage-conditioning corrections are next-cycle
data-rebuild decisions.** Neither change is authorized here. Both require
a new specification memo, a data-build authorization, and a new estimation
cycle, as described in the design notes.

---

*Produced by: read-only diagnostic script (no output written to data or
estimation directories). Source parquets: `fr_p3a_gsurv2_estimation_ready__*.parquet`.
Diagnostic date: 2026-05-22. Authorization: design decision notes v1 (§4
of wage note; §7 of couples note).*