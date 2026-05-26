# RUM/RURO Package Refactor Plan — v2

> **v2 note:** Supersedes v1 in Sections A (Stage 5 caveat), B.3 (rum config + ASCs),
> C.2 (ASCs in grid builder), C.6 (engine edit contingency), D (split equivalence classes,
> tightened tolerances, new E7/E8, replaced D.4), E (reordered phases; new Phase 1 spike;
> archival moved to Phase 6), and the Opportunity Density appendix. All other content is
> unchanged. See `RUM_RURO_package_refactor_plan_v1.md` for unchanged sections.

**Date:** 2026-05-27  
**Status:** Documentation only — no code was modified  
**Companion documents:**  
- `RUM_RURO_codebase_audit_v2.md` — revised factual baseline  
- `RUM_RURO_package_refactor_plan_v1.md` — previous version  
- `PROMPT_RUM_RURO_refactor_plan_2026-05-26.md` — verbatim prompt record  

---

## Section A — Target Architecture

The unified pipeline has six logical stages with two branch points (B).  
All stages must be country-, year-, and specification-agnostic.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 1: Load & filter data                                             │
│  • Load microdata (any country/year)                                     │
│  • Merge external data (GSUR, CPI, other) if configured                  │
│  • Apply user-defined sample filters                                      │
│  • Compute labour income via user-defined formula                         │
│  • Output: clean individual-level parquet                                 │
└─────────────────────────┬───────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           │       BRANCH B1: model type    │
           ▼                                ▼
┌─────────────────────────┐     ┌──────────────────────────────────────┐
│  Stage 2a (RUM)         │     │  Stage 2b (RURO)                     │
│  Build discrete grid:   │     │  Draw opportunity set                │
│  h_j = j × IL           │     │  • Non-employment Bernoulli(π₀)      │
│  j ∈ {0, …, n-1}       │     │  • Hours draw (Uniform or GMM)       │
│  n = ⌊max/IL⌋           │     │  • Wage draw (Uniform or empirical)  │
│  prior = 1.0 (all rows) │     │  • Occupation draw (optional)        │
│  ASC indicator per bin  │     │  • Couples: matched or grid mode     │
│  (reference = h_0 = 0)  │     │  prior = proposal density π(h,w,occ) │
└─────────────────────────┘     └──────────────────────────────────────┘
           │                                │
           └───────────────┬────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 3: EUROMOD simulation                                             │
│  • For each draw/alternative, compute disposable income (ils_dispy)      │
│  • Write scenario parquets with tax-benefit outcomes                     │
│  • EUROMOD system/dataset configurable per country/year                  │
└─────────────────────────┬───────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           │       BRANCH B2: assembly      │
           ▼                                ▼
┌─────────────────────────┐     ┌──────────────────────────────────────┐
│  Stage 4a (RUM)         │     │  Stage 4b (RURO)                     │
│  Assemble long data:    │     │  Assemble long data                  │
│  • Merge alts with      │     │  • Merge EUROMOD output with draws   │
│    EUROMOD output       │     │  • Filter draw bounds                │
│  • prior = 1.0          │     │  • Add demographic variables         │
│  • ASC columns          │     │  • Add GSUR if configured            │
│  • Add demographic      │     │  • Couples: merge male + female      │
│    variables            │     │    draws into household-level rows   │
└─────────────────────────┘     └──────────────────────────────────────┘
           │                                │
           └───────────────┬────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 5: Estimate model                                                 │
│  • Shared estimation engine (estimation_engine.py)                       │
│  • Utility form: Box-Cox (only form currently executable)                │
│  • Solver: GAMSPy/CONOPT (primary) or SciPy L-BFGS-B (fallback)        │
│  • RUM: prior=1.0 zeros prior term; HYPOTHESIS (Phase 1 must verify):   │
│    log_h, log_w, log_market can also be zeroed via spec/data choices     │
│    without engine edits — if not, Phase 4 adds a model_type flag         │
│  • RURO: prior = π(h,w,occ) → importance-sampling correction active     │
│  • Multistart; YAML spec drives all utility terms including ASCs         │
└─────────────────────────┬───────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 6: Post-estimation / reporting                                    │
│  • SE (Hessian-based), cluster-robust sandwich SE                        │
│  • McFadden ρ², AIC/BIC, elasticities                                    │
│  • Styled HTML + Markdown report                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key design principle:** RUM and RURO differ only at Stages 2 and 4.  The estimation
engine is shared.  For RUM, the opportunity-density correction is eliminated by writing
`prior = 1.0` in Stage 4a (necessary but not sufficient — see Stage 5 caveat above and
Appendix: Opportunity Density Correction).

**Open architectural question — bpool as primary speed path:**  
bpool (precomputed EUROMOD) is listed in Stage 3 above as an ACTIVE variant for RURO and
is the main lever for reducing estimation wall-time (EUROMOD is run once ahead of
estimation, not per iteration).  Whether bpool should be the *recommended* path in the
unified pipeline config (rather than just an optional variant) is a decision pending user
input.  Until resolved, bpool remains documented as a variant; the architecture does not
yet prescribe it as default.

---

## Section B — User-Facing Configuration Design

The target configuration surface is a hierarchy of YAML files read at runtime.  
No absolute paths, country names, or variable names may be hardcoded in any module.

### B.1 Machine config (gitignored) — already implemented

```yaml
# ~/.mnl/config.yaml
storage_root:  C:/Users/<user>/MNL/EUROMOD-STORAGE
backup_root:   //server/share/MNL_backup
outputs_root:  C:/Users/<user>/MNL/EUROMOD-STORAGE/outputs   # optional override
reports_root:  C:/Users/<user>/MNL/EUROMOD-STORAGE/reports   # optional override
euromod_root:  C:/path/to/EUROMOD_RELEASES_J1.0+
```

Resolution is handled by `path_helpers.py` (already implemented).

---

### B.2 Country/year config (one per country-year)

*(Unchanged from v1.)*

```yaml
# config/countries/fr_2016.yaml
country: fr
year: 2016

data:
  input_parquet:  processed/fr/2016/fr_2016_raw.parquet   # relative to data_root()
  external:
    gsur:         external/gsur/fr_gsur_v2.parquet        # omit if not used
    cpi:          external/cpi/fr_cpi.parquet             # omit if not used

sample_filters:
  age_min: 18
  age_max: 65
  les_thresholds: [3, 5, 7]                               # LES exclusion cutoffs
  replacement_income_columns: [bun, bsa, poa, pdi]       # columns that disqualify HH
  max_children: null                                      # null = no child filter

variables:
  labour_income_basic:    yem00                           # base pay column
  labour_income_extra:    yemxp                           # extra pay column; null if none
  # labour_income = labour_income_basic + labour_income_extra (if not null)
  education_column:       deh
  education_codes:        [0, 1, 2, 3, 4, 5]
  education_start_ages:   {0: 16, 1: 17, 2: 18, 3: 19, 4: 21, 5: 23}
  region_column:          nuts1
  region_codes:           [11, 21, 22, 23, 24, 25, 26, 31, 41, 42]
  focal_hours:            [20, 30, 40]                    # RURO focal-hours dummies

euromod:
  system:                    FR_2016_sl
  dataset:                   FR_2016_std
  disposable_income_var:     ils_dispy
  tax_unit_level:            household
```

---

### B.3 Pipeline run config (one per run)

*(v2 change: added `rum.asc` block and `rum.interval_length` divisibility note.)*

```yaml
# config/runs/fr_2016_run01.yaml
country_config:  config/countries/fr_2016.yaml
model_type:      ruro                                     # ruro | rum

ruro:
  variant:        continuous                             # continuous | job_choice
  draws:
    n_singles:    99                                     # +1 observed = 100 alternatives
    couples_mode: matched                                # matched | grid
    n_couples_male:   29                                 # for matched: +1 = 30 each
    n_couples_female: 29                                 # for grid: 30×30 = 900 alts
    # n_alternatives for matched: n_singles + 1
    # n_alternatives for grid:   (n_couples_male+1) × (n_couples_female+1)
    pi0_male:     0.10
    pi0_female:   0.10
    total_leisure: 80.0
  opportunity:
    hours:
      min: 5.0
      max: 70.0
    wage:                                                # omit if wage_spec = fw
      min: 2.0
      max: 170.0
    occupation:
      mode: empirical                                    # empirical | fixed | none
      strata: [dgn, educ3]
      min_cell_size: 30

rum:
  interval_length: null    # required when model_type = rum; must be > 0
  hours_max:       null    # required when model_type = rum; must be > interval_length
  # n_alts = floor(hours_max / interval_length)
  # h_j    = j × interval_length,  j ∈ {0, …, n_alts − 1}
  # h_0 = 0 (non-employment); hours_max is NOT a grid point
  # interval_length is NOT required to divide hours_max exactly.
  # If it does not, the trailing partial interval
  # [n_alts × interval_length, hours_max) is excluded — no grid point is placed there.
  #
  asc:
    estimate:            true          # include ASCs on hours categories (recommended)
    reference_category:  0            # h_0 = 0 (non-employment) is the reference; no ASC
    # Free ASC parameters: one per non-reference grid point (n_alts − 1 parameters)
    # e.g. for n_alts=5: γ_1 (h=IL), γ_2 (h=2×IL), γ_3 (h=3×IL), γ_4 (h=4×IL)
    # Van Soest (1995) found ASCs on part-time / full-time bins were required for fit;
    # Model I (utility only) was empirically inadequate.

estimation_spec:  specifications/estimation_spec_v3.yaml # path relative to scripts/enhanced/

output:
  run_label:  fr_2016_run01
  results_dir: null                                      # null → outputs_root() / estimates / {country} / ...
```

---

### B.4 Estimation spec YAML (existing, unchanged)

52 specs already exist under `scripts/enhanced/specifications/`.  
Proposed additions for RUM support:
- Top-level `model_type: rum` annotation (informational; documents intent)
- ASC parameter declarations for each non-reference hours category (new parameter block,
  analogous to existing demographic shifter declarations)

---

## Section C — Canonical Script Proposal

### C.1 Stage 1: Load & filter data

*(Unchanged from v1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep / extend | `enh_france_data_prep.py` | Replace France-specific constants with lookups from country config YAML |
| Rename target | → `data_prep.py` or `pipeline_data_prep.py` | Renamed once France constants are removed |
| Wrap temporarily | `france_data_prep.py` | Keep until equivalence test passes |
| Deprecate later | `france_data_prep.py` | After equivalence confirmed |
| GSUR canonical | `enh_prepare_FR_gsur_v2.py` | Keep; wrap by routing through external-data config |
| Deprecate later | `enh_prepare_FR_gsur.py`, `prepare_FR_gsur.py` | After v2 equivalence confirmed |

---

### C.2 Stage 2a: RUM alternative construction (new module)

*(v2 change: ASC generation added to module responsibilities.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| **Create new** | `scripts/enhanced/rum_grid_builder.py` | No equivalent exists; reads `interval_length`, `hours_max`, and `asc` config from run config |

Responsibilities of `rum_grid_builder.py`:
1. Compute grid: `h_j = j × interval_length` for `j ∈ {0, …, n_alts − 1}`,
   `n_alts = floor(hours_max / interval_length)`
2. Set `prior = 1.0` for all alternatives
3. Generate ASC indicator columns `asc_j` (binary, one per non-reference grid point)
4. Compute labour income `c_ij` for each alternative using the country-config formula
5. Write long-format parquet compatible with `enh_RURO_prep_mnl_basic.py`

Whether `rum_grid_builder.py` requires any changes to `enh_RURO_prep_mnl_basic.py` or
`estimation_engine.py` depends on the Phase 1 spike outcome.

---

### C.3 Stage 2b: RURO draw generation

*(Unchanged from v1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep | `enh_RURO_draws.py` | Canonical; extend to read bounds from run config (not defaults) |
| Wrap temporarily | `RURO_draws.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_draws.py` | After equivalence confirmed |
| Keep | `enh_job_universe.py`, `enh_job_draws.py` | Canonical for job-choice RURO |
| Keep | `scripts/bpool/*.py` | Canonical for bpool precomputation |

**P0 fix required (before migration):** Ensure `enh_RURO_draws.py` default bounds match
the values actually enforced in `enh_RURO_prep_mnl_basic.py` (or, better, eliminate
standalone defaults entirely and require bounds from run config).

---

### C.4 Stage 3: EUROMOD

*(Unchanged from v1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep / extend | `enh_RURO_euromod.py` | Canonical; add `euromod.system`/`dataset` from country config |
| Wrap temporarily | `RURO_euromod.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_euromod.py` | After equivalence confirmed |

---

### C.5 Stage 4: Data assembly

*(Unchanged from v1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep / extend | `enh_RURO_prep_mnl_basic.py` | Canonical; fix P0 bounds inconsistency; add `prior = 1.0` path for RUM |
| Keep / extend | `enh_RURO_prep.py` | Canonical; replace hardcoded dummies with country-config lookups |
| Wrap temporarily | `RURO_prep_mnl_basic.py`, `RURO_prep.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_prep_mnl_basic.py`, `RURO_prep.py` | After equivalence confirmed |

---

### C.6 Stage 5: Estimation

*(v2 change: "no modification needed" replaced with contingency language pending Phase 1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep; possibly extend | `estimation_engine.py` | Needed for RURO regardless; RUM requires Phase 1 to verify whether engine edits are also needed to suppress log_h/log_w/log_market |
| Keep unchanged | `estimation_spec_parser.py` | Add optional `model_type` key and ASC parameter declarations |
| Keep | `gamspy_estimation_vectorized.py` | Primary solver; no changes needed |
| Archive eventually | `gamspy_estimation.py` | Non-vectorised; superseded by vectorised version |
| Keep | `enh_RURO_estimate_FR.py` | Canonical orchestrator |
| Wrap temporarily | `RURO_estimate_FR.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_estimate_FR.py` | After equivalence confirmed |
| Archive | All `scripts/archive/rum_approach/RUM/` | Already archived; do not modify |

---

### C.7 Stage 6: Post-estimation

*(Unchanged from v1.)*

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep | `compute_standard_errors.py` | Canonical |
| Keep | `cluster_robust_se.py` | Canonical |
| Keep | `run_cluster_robust_se.py` | Canonical CLI |
| Keep | `generate_html_report.py` | Canonical |
| Wrap temporarily | `RURO_post_estimation.py` | Keep until equivalence confirmed |
| Deprecate later | `RURO_post_estimation.py` | After equivalence confirmed |

---

## Section D — Equivalence Test Plan

*(v2 change: equivalence split into two classes with different tolerances. Regression
class uses tight numeric gates; legacy↔enhanced cross-check is informational only.
E1 corrected. E7 and E8 added. D.3 and D.4 replaced.)*

---

### D.1 Golden reference

*(Unchanged from v1.)*

The only valid equivalence anchor for legacy ↔ enhanced comparison is a **continuous RURO**
spec (the only type legacy `RURO_*.py` supports).

```
Run folder:   outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
File:         estimation_results.json
LL (recorded from JSON): -6608.591013943798
Spec used:    base_vw_with_interaction  (wage_spec: vw)
```

**Before running any equivalence test:** Read `estimation_results.json` directly to confirm
the LL value.  Do not rely on this document as the authoritative number.

P3a (`ruro_occ_P3a_pooled`) and M2e_b (-22161.05) are enhanced-only references.
They may serve as internal sanity checks for the enhanced pipeline but cannot be compared
against the legacy pipeline.

---

### D.2 Equivalence classes

**Class A — Regression equivalence (refactored-enhanced vs golden-enhanced):**  
Both runs use the same solver (GAMSPy/CONOPT), the same engine, and the same data.
The refactor only moved configuration out of the code.  Tolerances are tight.

```
LL:         |Δ| < 1e-3  (absolute)
Parameters: |Δθ_k| / max(|θ_k|, 1e-3) < 1e-4  (relative; per-parameter)
            Rationale: Box-Cox β parameters can range 30–150; absolute tolerance
            of ±0.01 (v1) would pass materially different models. Relative
            tolerance correctly scales to parameter magnitude.
```

**Class B — Legacy ↔ enhanced cross-check (informational only):**  
Different solver (legacy uses SciPy only; enhanced uses GAMSPy), different features
(no multistart in legacy).  A tight numeric match is not expected or required.  
Report the LL gap, parameter-level differences, and a qualitative explanation.  
This cross-check does NOT gate archival; it documents the magnitude of the legacy gap.

---

### D.3 Equivalence test protocol

#### Step E0 — Confirm golden reference

```
1. Read estimation_results.json from the v3 run folder.
2. Record: final_ll, parameter vector (all θ), SE vector, Hessian norm.
3. Save as docs/estimation/equivalence_golden_v3.json.
```

#### Step E1 — Data prep equivalence (Stage 1; Class A)

```
Test: Run enh_france_data_prep.py (refactored, with fr_2016.yaml) and the
      same script at its last committed state (pre-refactor) on the same raw input.
Pass criteria:
  • Row count difference = 0 (exactly equal; any silent row drop is a failure)
  • Filter-exclusion counts identical (same number of households dropped at each filter)
  • Mean absolute difference in continuous columns (yem, wage, etc.) < 1e-6
```

#### Step E2 — Draw equivalence (Stage 2b; Class A)

```
Test: Fix random seed; run enh_RURO_draws.py (refactored) vs pre-refactor version.
Pass criteria:
  • Number of draw rows = equal
  • Mean of h, w, prior columns: |Δ| < 1e-4
  • Proportion non-employed: |Δ| < 0.001
```

#### Step E3 — EUROMOD output equivalence (Stage 3; Class A)

```
Test: Same draw files → same EUROMOD input → compare ils_dispy output.
Pass criteria:
  • ils_dispy: max absolute row-level |Δ| < 1e-2 (EUR)
  • Missing or extra rows: 0
```

#### Step E4 — MNL data assembly equivalence (Stage 4; Class A)

```
Test: Same inputs → run enh_RURO_prep_mnl_basic.py (refactored) vs pre-refactor.
Pass criteria:
  • Row counts equal
  • log_income, log_leisure columns: max absolute |Δ| < 1e-6
  • prior column: max absolute |Δ| < 1e-8
```

#### Step E5 — Regression likelihood equivalence (Stage 5; Class A)

```
Test: Same assembled data → run refactored-enhanced pipeline with v3 spec.
Pass criteria:
  • LL: |enhanced_ll − golden_ll| < 1e-3
  • Parameters: |Δθ_k| / max(|θ_k|, 1e-3) < 1e-4  for all k
  • No NaN in gradient or Hessian
```

#### Step E5b — Legacy ↔ enhanced cross-check (Class B; informational)

```
Test: Same raw input → run legacy RURO_*.py pipeline and enhanced pipeline,
      both with v3 spec (continuous RURO, wage_spec=vw).
Record:
  • Legacy LL, enhanced LL, |Δ|
  • Parameter differences (absolute and relative) per θ_k
  • Qualitative explanation of any material gap (solver difference, multistart, etc.)
This step does NOT gate archival. Output is documentation only.
```

#### Step E6 — Full pipeline regression (Stages 1–6 end-to-end; Class A)

```
Test: Run full refactored-enhanced pipeline on FR 2016 continuous RURO spec.
Pass criteria:
  • All E1–E5 criteria met
  • Generated HTML report is non-empty and contains parameter table
  • No exceptions or NaN values in output
```

#### Step E7 — Couples spec equivalence (Class A)

```
Test: Run a couples-specific spec through the refactored-enhanced pipeline.
Pass criteria:
  • LL: |Δ| < 1e-3 vs the same spec run on the pre-refactor pipeline
  • Parameter vector: relative |Δ| < 1e-4 for all k
  • Couple-level log-sum-exp values: max |Δ| < 1e-6 across all households
Rationale: GSUR merge and couple-draw matching are both couples-specific code paths
not exercised by E5 (which uses a singles spec for the v3 golden reference).
```

#### Step E8 — GSUR lookup-table equivalence (Class A)

```
Test: Run enh_prepare_FR_gsur_v2.py (refactored) and the pre-refactor version
      on the same INSEE input.
Pass criteria:
  • Output parquet row counts equal
  • GSUR rate column: max absolute |Δ| < 1e-8 (pure arithmetic, not solver-dependent)
  • Household-level GSUR assignment: exact match for all matched household IDs
Rationale: GSUR is used in estimation as a market-opportunity shifter; a discrepancy
here propagates to every log-likelihood evaluation.
```

---

### D.4 Safe-to-archive criteria

A legacy script family is safe to archive when ALL FOUR of the following hold:

**(a) Tight regression equivalence:**  
The refactored-enhanced pipeline reproduces the v3 golden reference within Class A
tolerances (E5 passes: LL |Δ| < 1e-3, all parameters |Δθ_k|/max(|θ_k|, 1e-3) < 1e-4).

**(b) Both singles and couples production runs complete clean:**  
A full enhanced-only production run completes without exception or NaN for at least one
singles spec AND one couples spec, both on FR 2016 data.

**(c) GSUR lookup-table equivalence confirmed:**  
E8 passes.  GSUR discrepancy between legacy and refactored GSUR scripts is zero or
below the numerical tolerance defined in E8.

**(d) No active runner or YAML references the legacy script:**  
No `.ps1` pipeline runner, no YAML estimation spec, and no Python import statement
references the script to be archived.

**These four gates are cumulative; all must pass before a single file is moved.**

---

### D.5 Tolerance justification

*(v2: replaces v1 D.3.)*

| Comparison class | Quantity | Tolerance | Justification |
|-----------------|---------|----------|---------------|
| Class A (regression) | LL | < 1e-3 | Same solver, same engine; any Δ > 1e-3 indicates a code change, not numerical noise |
| Class A (regression) | Parameters | relative < 1e-4 | Box-Cox β can be 30–150; absolute ±0.01 (v1) would pass materially different models on large params |
| Class A (regression) | Continuous columns | < 1e-6 | Identical arithmetic pipeline; float64 rounding only |
| Class A (regression) | ils_dispy | < 1e-2 | EUROMOD rounds to cents |
| Class A (regression) | GSUR | < 1e-8 | Pure arithmetic; should be bit-identical given same input |
| Class B (informational) | LL | n/a | Report Δ; do not gate on magnitude |
| Class B (informational) | Parameters | n/a | Report Δ; explain qualitatively |

---

## Section E — Phased Migration Plan

*(v2 change: phases renumbered; new Phase 1 = RUM verification spike added;
archival moved from Phase 3 to Phase 6 (now last and irreversible).
No file may be archived before Phase 6.)*

---

### Phase 0 — Fix P0 configuration gap (prerequisite)

*(Unchanged from v1.)*

**Goal:** Eliminate the draw-bounds inconsistency before any refactor work begins.

**Files to touch:**
- `scripts/enhanced/enh_RURO_draws.py` — ensure DEFAULT_H_MIN, DEFAULT_W_MIN, DEFAULT_W_MAX
  match what `enh_RURO_prep_mnl_basic.py` enforces, OR eliminate standalone defaults in both
  scripts and require the run config to supply all bounds

**Files not to touch:** estimation engine, any legacy scripts, YAML specs

**Test gate:** Default bounds in both scripts are identical, OR both scripts error-out if
bounds are not supplied via config.

**Documentation update:** Update Section E of `RUM_RURO_codebase_audit_v2.md` P0 row.

**Rollback:** Revert both files; no other script is affected.

---

### Phase 1 — RUM verification spike (NEW; prerequisite for Phase 4)

**Goal:** Prove or disprove the hypothesis that the enhanced estimation engine can produce
a pure-RUM index `V = u + ASC_j` (no `log_h`, no `log_w`, no `log_market`) with finite LL
on a small FR 2016 sample, using NO modifications to `estimation_engine.py`.

**Rationale:** The v1 plan asserted "no engine change needed" as an established fact.
This is incorrect — it is an unverified hypothesis.  Engine editability is the most
consequential design question for the RUM branch.  If the hypothesis fails, Phase 4 scope
changes materially.  This must be determined before building config scaffolding on top
of the assumption.

**What the spike does:**

1. Construct a minimal RUM test dataset from FR 2016:
   - Small sample (e.g. 500 single-member households)
   - Fixed `interval_length`, `hours_max` chosen to produce a small number of alternatives
   - `prior = 1.0` for all alternatives
   - ASC indicator columns for each non-reference bin

2. Write a minimal RUM YAML spec:
   - `wage_spec: fw` (fixed wage; candidate for suppressing `log_w`)
   - No GSUR or market-opportunity terms (candidate for suppressing `log_market`)
   - No hours draw density (candidate for suppressing `log_h`)
   - ASC parameters declared for each non-reference bin
   - `model_type: rum` annotation

3. Run the existing `estimation_engine.py` on this dataset without any code changes

4. Inspect the composite value function `V` for each alternative:
   - Confirm `log_h = 0` (or absent) for all rows
   - Confirm `log_w = 0` (or absent) for all rows
   - Confirm `log_market = 0` (or absent) for all rows
   - Confirm `prior = 1.0` and `−np.log(prior) = 0` for all rows

5. Check estimation outcome:
   - LL must be finite (non-NaN, non-Inf)
   - Gradient must be finite at the optimum
   - LL must be stable across two runs with identical inputs (deterministic grid → deterministic LL)

**Pass outcome:**  
All four V terms confirmed zero without engine edits.  
Phase 4 proceeds with `rum_grid_builder.py` only; no engine changes in scope.

**Fail outcome:**  
One or more of `log_h`, `log_w`, `log_market` is non-zero (or cannot be zeroed via
spec/data choices).  Record which terms require engine suppression.  Phase 4 scope
expands: add a `model_type: rum` flag to `estimation_engine.py` that sets those terms
to zero when `model_type = rum`.

**Files to touch:** none permanently.  Spike uses existing code.  Artefacts:
- `docs/estimation/RUM_spike_v1.md` — records the test setup, V inspection results,
  and pass/fail verdict for each term; this document becomes the evidence base for
  Phase 4 engine decisions.

**Files not to touch:** estimation engine, estimation spec parser, any legacy scripts

**Test gate:** `docs/estimation/RUM_spike_v1.md` exists, contains verbatim V term values,
and explicitly states the pass/fail verdict for each of the four terms.

**Documentation update:** `RUM_RURO_codebase_audit_v2.md` Section F.4 — update the
"Hypothesis" box to "Confirmed" or "Rejected" with a link to `RUM_spike_v1.md`.

**Rollback:** No code was touched; nothing to revert.

---

### Phase 2 — Configuration externalisation (Stage 1)

*(Was Phase 1 in v1; content unchanged.)*

**Goal:** Remove all France-specific constants from `enh_france_data_prep.py` and replace
them with lookups from the country config YAML.

**Files to touch:**
- `scripts/enhanced/enh_france_data_prep.py` — replace hardcoded constants
- `config/countries/fr_2016.yaml` — **new file** containing all France 2016 constants
- `scripts/enhanced/enh_prepare_FR_gsur_v2.py` — route through country config or accept
  country-specific GSUR config file

**Files not to touch:** estimation engine, legacy scripts, any RURO draw scripts

**Test gate:** Run E1 (data prep equivalence — Class A): row counts exactly equal;
filter-exclusion counts identical; column distributions within 1e-6.

**Documentation update:** Mark Stage 1 P1 items as resolved in the audit.

**Rollback:** Restore `enh_france_data_prep.py` from git; delete `fr_2016.yaml`.

---

### Phase 3 — RURO draw and assembly configuration (Stages 2b and 4b)

*(Was Phase 2 in v1; content unchanged.)*

**Goal:** Route all draw bounds through the run config YAML.

**Files to touch:**
- `scripts/enhanced/enh_RURO_draws.py` — read bounds from run config; error if not supplied
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` — same
- `config/runs/fr_2016_run01.yaml` — **new file** with draw bounds, n_singles, couples mode
- `scripts/enhanced/enh_RURO_estimate_FR.py` — pass run config to draw and prep scripts

**Files not to touch:** estimation engine, legacy scripts, GSUR scripts

**Test gate:** Run E2 and E4 (draw and assembly equivalence — Class A) with FR 2016 defaults
reproduced via config YAML.

**Documentation update:** Mark Stage 2b / 4b configuration gaps in audit as resolved.

**Rollback:** Restore both prep scripts and the estimate orchestrator from git.

---

### Phase 4 — RUM full branch (Stage 2a + 4a + estimation)

*(Was Phase 4 in v1; content extended with ASCs and engine contingency.)*

**Prerequisite:** Phase 1 spike complete with a documented pass/fail verdict per V term.

**Goal:** Implement `rum_grid_builder.py`, add ASC columns to the data-assembly stage,
and run a first RUM estimation.

**Files to touch (new):**
- `scripts/enhanced/rum_grid_builder.py` — grid construction, prior=1.0, ASC indicators
  (see C.2 for full responsibilities)
- `docs/estimation/RUM_spike_v1.md` (already created in Phase 1)

**Files to touch (extend):**
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` — add `prior = 1.0` path for RUM;
  preserve ASC columns from grid builder
- `scripts/enhanced/enh_RURO_estimate_FR.py` — dispatch to RUM branch
- `scripts/enhanced/estimation_spec_parser.py` — add `model_type` key; add ASC parameter
  declarations; mark `model_type: rum` as valid
- One new YAML spec for RUM: `specifications/estimation_spec_rum_v1.yaml`

**Conditional on Phase 1 fail outcome:**
- `scripts/enhanced/estimation_engine.py` — add `model_type: rum` handling to suppress
  `log_h`, `log_w`, `log_market` for the terms found non-suppressible via spec/data

**Files not to touch:** `estimation_engine.py` IF Phase 1 passes; legacy scripts

**Test gate:**
- `n_alts = floor(hours_max / interval_length)` matches config for the chosen values
- `prior = 1.0` for all rows in assembled RUM data
- All four V terms (log_h, log_w, log_market, −log_prior) confirmed zero or absent
  in the first RUM run (inspect intermediate tensors)
- ASC parameters appear in the estimation output with finite values
- LL is finite and stable (identical across two runs with same input)

**Note on utility form:**  
Box-Cox is the deliberate choice.  Translog (Van Soest 1995) is deferred.

**Documentation update:** Create `docs/estimation/RUM_v1_results.md` with first-run LL,
spec, ASC values, and date.

**Rollback:** Delete `rum_grid_builder.py`, `estimation_spec_rum_v1.yaml`; restore modified
scripts from git.  If engine was edited: also restore `estimation_engine.py`.

---

### Phase 5 — EUROMOD configuration and multi-country readiness

*(Was Phase 5 in v1; content unchanged.)*

**Goal:** Replace hardcoded EUROMOD system/dataset strings with lookups from country config.

**Files to touch:**
- `scripts/enhanced/enh_RURO_euromod.py` — read system, dataset, disposable income variable
  from country config
- `config/countries/fr_2016.yaml` — add `euromod:` block
- `config/countries/be_2018.yaml` — **new** illustrative second-country config (stub)

**Test gate:** FR 2016 production run produces identical output to Phase 3 result (Class A
regression tolerances).  Stub BE 2018 config loads without error.

**Documentation update:** Update `RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` §4.

---

### Phase 6 — Equivalence suite → legacy archival (LAST; irreversible)

*(Was Phase 3 in v1, but is now the final phase.  No archival may happen before this phase.)*

**Goal:** Run the complete equivalence test suite (E0–E8) and archive legacy scripts once
all four D.4 gates pass.

**Prerequisite:** Phases 0–5 all complete and documented.

**Files to touch:**
- `docs/estimation/equivalence_golden_v3.json` — **new file**: golden LL, parameter vector,
  SE vector read from `estimation_results.json`
- Git archive operation (single commit): move
  `scripts/RURO_draws.py`, `RURO_euromod.py`, `RURO_prep.py`, `RURO_prep_mnl_basic.py`,
  `RURO_estimate_FR.py`, `france_data_prep.py`, `RURO_post_estimation.py` →
  `scripts/archive/legacy_ruro_root/`

**Files not to touch:** enhanced scripts (test, do not change them in this phase)

**Test gate:** All of E0–E8 pass at Class A tolerances.  D.4 gates (a), (b), (c), (d)
all confirmed.  E5b (Class B cross-check) documented with quantified Δ and explanation.

**Documentation update:** Update `RUM_RURO_codebase_audit_v2.md` to mark archived
scripts as ARCH.

**Rollback:** `git revert` the archive commit; all files restored.  No other damage.

---

## Appendix — RUM Alternative Construction Formula

*(v2 change: added divisibility note.)*

```
General:
  n_alts = floor(hours_max / interval_length)
  h_j    = j × interval_length,   j ∈ {0, 1, …, n_alts − 1}
  h_0    = 0   (non-employment; first grid point, not a separate state)
  hours_max is NOT a grid point

Divisibility: interval_length is NOT required to divide hours_max exactly.
  If it does not, the trailing partial interval [n_alts × interval_length, hours_max)
  is excluded — no grid point is placed in that range.

Illustrative examples only:
  interval_length=12, hours_max=60:  n_alts=5,  h ∈ {0, 12, 24, 36, 48}
  interval_length=10, hours_max=60:  n_alts=6,  h ∈ {0, 10, 20, 30, 40, 50}
  interval_length=11, hours_max=60:  n_alts=5,  h ∈ {0, 11, 22, 33, 44};
                                     hours 55–60 are excluded
```

---

## Appendix — Utility Form Architecture Decision

*(Unchanged from v1.)*

**Current engine state:**  
`estimation_spec_parser.py:445` raises `NotImplementedError` if `utility_form != "box_cox"`.
The enhanced engine supports Box-Cox only at runtime, regardless of what the spec declares.

**Decision for RUM implementation:**  
Box-Cox is the deliberate choice for the initial RUM branch.  
Box-Cox with `θ → 0` subsumes log-utility as a special case.

**Translog status:**  
Van Soest (1995) used translog.  Not in scope for this refactor.  Adding it requires:
1. Extending `estimation_engine.py` with a new utility evaluation branch
2. Extending `estimation_spec_parser.py` to parse translog parameters
3. New YAML spec template
4. Separate test suite

---

## Appendix — Opportunity Density Correction Architecture

*(v2 change: corrected. v1 asserted "no engine change needed" based on prior=1.0 alone.
v2 documents the full four-term problem and downgrades the claim to a hypothesis.)*

**Full composite value index (estimation_engine.py:363):**

```
V_ij = u(c_ij, l_ij)          [Box-Cox utility]
     + log_h(h_ij)             [log density of hours draw: g₂(h); RURO-specific]
     + log_w(w_ij)             [log density of wage draw: g₁(w); RURO-specific]
     + log_market_ij           [log market opportunity, GSUR-based; RURO-specific]
     − np.log(data.prior)      [importance-sampling correction; RURO-specific]
```

**For genuine Van Soest RUM, the target index is:**

```
V_ij = u(c_ij, l_ij) + ASC_j
```

All four RURO-specific terms must be identically zero.

**Prior term — achievable without engine change:**

```
Write prior = 1.0 for all rows in Stage 4a (RUM data assembly).
− np.log(1.0) = 0.  ✓ No engine edit needed for this term.
```

**Remaining three terms — Phase 1 spike must determine:**

| Term | Candidate suppression (no engine edit) | Confirmed? |
|------|----------------------------------------|-----------|
| `log_w` | `wage_spec="fw"` (fixed wage, no draw) | Unverified — Phase 1 |
| `log_h` | No hours density if grid is deterministic | Unverified — Phase 1 |
| `log_market` | Omitting GSUR from spec or data | Unverified — Phase 1 |

**If Phase 1 confirms suppression via spec/data choices:** no engine edit needed.  
**If any term persists without engine edit:** add `model_type: rum` flag to
`estimation_engine.py` that gates those terms to zero when `model_type = rum`.

---

*End of refactor plan v2. No code was modified in producing this document.*
