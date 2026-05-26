# RUM/RURO Package Refactor Plan — v1

**Date:** 2026-05-27  
**Status:** Documentation only — no code was modified  
**Companion documents:**  
- `RUM_RURO_codebase_audit_v1.md` — factual baseline this plan builds on  
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
┌─────────────────────┐         ┌──────────────────────────────────────┐
│  Stage 2a (RUM)     │         │  Stage 2b (RURO)                     │
│  Build discrete     │         │  Draw opportunity set                │
│  hour grid:         │         │  • Non-employment Bernoulli(π₀)      │
│  h_j = j × IL       │         │  • Hours draw (Uniform or GMM)       │
│  j ∈ {0, …, n-1}   │         │  • Wage draw (Uniform or empirical)  │
│  n = ⌊max/IL⌋       │         │  • Occupation draw (optional)        │
│  prior = 1.0        │         │  • Couples: matched or grid mode     │
│  for all alts       │         │  prior = proposal density π(h,w,occ) │
└─────────────────────┘         └──────────────────────────────────────┘
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
┌─────────────────────┐         ┌──────────────────────────────────────┐
│  Stage 4a (RUM)     │         │  Stage 4b (RURO)                     │
│  Assemble long      │         │  Assemble long data                  │
│  data:              │         │  • Merge EUROMOD output with draws   │
│  • Merge alts with  │         │  • Filter draw bounds                │
│    EUROMOD output   │         │  • Add demographic variables         │
│  • prior = 1.0      │         │  • Add GSUR if configured            │
│  • Add demographic  │         │  • Couples: merge male + female      │
│    variables        │         │    draws into household-level rows   │
└─────────────────────┘         └──────────────────────────────────────┘
           │                                │
           └───────────────┬────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 5: Estimate model                                                 │
│  • Shared estimation engine (estimation_engine.py)                       │
│  • Utility form: Box-Cox (only form currently executable)                │
│  • Solver: GAMSPy/CONOPT (primary) or SciPy L-BFGS-B (fallback)        │
│  • RUM: prior = 1.0 → correction term = 0 automatically                 │
│  • RURO: prior = π(h,w,occ) → importance-sampling correction active     │
│  • Multistart; YAML spec drives all utility terms                        │
└─────────────────────────┬───────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 6: Post-estimation / reporting                                    │
│  • SE (Hessian-based), cluster-robust sandwich SE                        │
│  • McFadden ρ², AIC/BIC, elasticities                                    │
│  • Styled HTML + Markdown report                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key design principle:** The only difference between RUM and RURO is Stages 2 and 4
(alternative construction and data assembly).  The estimation engine is shared without
modification.  The opportunity-density correction is controlled by the `prior` column
in the assembled data, not by a flag in the engine.

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
  interval_length: null                                  # required when model_type = rum
  hours_max:       null                                  # required when model_type = rum
  # n_alts = floor(hours_max / interval_length)
  # h_j    = j × interval_length,  j ∈ {0, …, n_alts − 1}
  # h_0 = 0 (non-employment); hours_max is NOT a grid point

estimation_spec:  specifications/estimation_spec_v3.yaml # path relative to scripts/enhanced/

output:
  run_label:  fr_2016_run01
  results_dir: null                                      # null → outputs_root() / estimates / {country} / ...
```

---

### B.4 Estimation spec YAML (existing, unchanged)

52 specs already exist under `scripts/enhanced/specifications/`.  
The only proposed addition is a top-level `model_type: rum | ruro` annotation
(informational; not read by the estimation engine).  The engine is controlled entirely
by which columns are present in the assembled data (particularly `prior`).

---

## Section C — Canonical Script Proposal

### C.1 Stage 1: Load & filter data

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

| Action | Script | Rationale |
|--------|--------|-----------|
| **Create new** | `scripts/enhanced/rum_grid_builder.py` | No equivalent exists; reads `interval_length` and `hours_max` from run config |

This is the only net-new module required for the RUM branch.

---

### C.3 Stage 2b: RURO draw generation

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

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep / extend | `enh_RURO_euromod.py` | Canonical; add `euromod.system`/`dataset` from country config |
| Wrap temporarily | `RURO_euromod.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_euromod.py` | After equivalence confirmed |

---

### C.5 Stage 4: Data assembly

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep / extend | `enh_RURO_prep_mnl_basic.py` | Canonical; fix P0 bounds inconsistency; add `prior = 1.0` path for RUM |
| Keep / extend | `enh_RURO_prep.py` | Canonical; replace hardcoded dummies with country-config lookups |
| Wrap temporarily | `RURO_prep_mnl_basic.py`, `RURO_prep.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_prep_mnl_basic.py`, `RURO_prep.py` | After equivalence confirmed |

---

### C.6 Stage 5: Estimation

| Action | Script | Rationale |
|--------|--------|-----------|
| Keep unchanged | `estimation_engine.py` | No modification needed for RUM (prior=1.0 handles it) |
| Keep unchanged | `estimation_spec_parser.py` | Add optional `model_type` key (informational) |
| Keep | `gamspy_estimation_vectorized.py` | Primary solver; no changes needed |
| Archive eventually | `gamspy_estimation.py` | Non-vectorised; superseded by vectorised version |
| Keep | `enh_RURO_estimate_FR.py` | Canonical orchestrator |
| Wrap temporarily | `RURO_estimate_FR.py` | Keep until equivalence test passes |
| Deprecate later | `RURO_estimate_FR.py` | After equivalence confirmed |
| Archive | All `scripts/archive/rum_approach/RUM/` | Already archived; do not modify |

---

### C.7 Stage 6: Post-estimation

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

### D.1 Golden reference

The only valid equivalence anchor for legacy ↔ enhanced comparison is a **continuous RURO**
spec (the only type legacy `RURO_*.py` supports).

```
Run folder:   outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
File:         estimation_results.json
LL (recorded from JSON): -6608.591013943798
Spec used:    base_vw_with_interaction  (wage_spec: vw)
```

**Before running any equivalence test:** Read `estimation_results.json` directly to confirm
the LL value.  Do not rely on this document as the authoritative number — the JSON is the
ground truth.

P3a (`ruro_occ_P3a_pooled`) and M2e_b (-22161.05) are enhanced-only references.
They may serve as internal sanity checks for the enhanced pipeline but cannot be compared
against the legacy pipeline.

---

### D.2 Equivalence test protocol

#### Step E0 — Confirm golden reference

```
1. Read estimation_results.json from the v3 run folder above.
2. Record: final_ll, parameter vector, SE vector, Hessian norm.
3. Save as docs/estimation/equivalence_golden_v3.json.
```

#### Step E1 — Data prep equivalence (Stage 1 + 2)

```
Test: Run enh_france_data_prep.py and france_data_prep.py on the same raw input.
Pass criteria:
  • Row count difference ≤ 0 (enhanced may be equal or fewer due to stricter filtering)
  • Mean absolute difference in continuous columns (yem, wage, etc.) < 1e-6
  • Filter exclusion counts match
```

#### Step E2 — Draw equivalence (Stage 2b)

```
Test: Fix random seed; run enh_RURO_draws.py and RURO_draws.py.
Pass criteria:
  • Number of draw rows equal
  • Mean of h, w, prior columns: difference < 1e-4
  • Proportion non-employed: difference < 0.001
```

#### Step E3 — EUROMOD output equivalence (Stage 3)

```
Test: Same draw files → same EUROMOD input → compare ils_dispy output.
Pass criteria:
  • ils_dispy: max absolute row-level difference < 1e-2 (EUR)
  • Any missing/extra rows: 0
```

#### Step E4 — MNL data assembly equivalence (Stage 4)

```
Test: Same inputs → run enh_RURO_prep_mnl_basic.py and RURO_prep_mnl_basic.py.
Pass criteria:
  • Row counts equal
  • log_income, log_leisure columns: max absolute difference < 1e-6
  • prior column: max absolute difference < 1e-8
```

#### Step E5 — Likelihood equivalence (Stage 5)

```
Test: Same assembled data → run both estimation engines with the v3 spec.
Pass criteria:
  • final_ll: |enhanced_ll − reference_ll| < 1.0   (absolute)
  • Parameter vector: max absolute difference < 0.01
  • SE vector: max absolute difference < 0.05
```

#### Step E6 — Full pipeline regression (Stages 1–6 end-to-end)

```
Test: Run full enhanced pipeline on FR 2016 continuous RURO spec.
Pass criteria:
  • All E1–E5 criteria met
  • Generated HTML report is non-empty and contains parameter table
  • No exceptions or NaN values in output
```

---

### D.3 Tolerance justification

| Quantity | Tolerance | Justification |
|---------|----------|---------------|
| LL | ±1.0 | Numerical optimiser convergence tolerance; CONOPT reports ~1e-6 gradient norm |
| Parameters | ±0.01 | Typical SE on θ parameters is 0.05–0.2; 0.01 is well inside rounding error |
| SE | ±0.05 | Hessian numerical approximation; cluster-robust SE variance from sample split |
| Continuous columns | < 1e-6 | Floating-point arithmetic should be identical given same input |
| ils_dispy | < 1e-2 | EUROMOD rounding to cents |

---

### D.4 Safe-to-archive criteria

A legacy script family is safe to archive when all of the following hold:
1. E5 and E6 pass for the same country-year and spec.
2. The equivalence results are committed to `docs/estimation/equivalence_golden_v3.json`.
3. At least one full production run using only enhanced scripts completes without error.
4. The legacy script is not referenced in any active PS1 runner or YAML config.

---

## Section E — Phased Migration Plan

### Phase 0 — Fix P0 configuration gap (prerequisite)

**Goal:** Eliminate the draw-bounds inconsistency before any refactor work begins.  
This is a latent bug (currently masked by the metadata sidecar) that must be resolved
before equivalence testing is meaningful.

**Files to touch:**
- `scripts/enhanced/enh_RURO_draws.py` — ensure DEFAULT_H_MIN, DEFAULT_W_MIN, DEFAULT_W_MAX
  match what `enh_RURO_prep_mnl_basic.py` enforces, OR eliminate standalone defaults in both
  scripts and require the run config to supply all bounds

**Files not to touch:** estimation engine, any legacy scripts, YAML specs

**Test gate:** Running `enh_RURO_draws.py` standalone with defaults produces bounds that
`enh_RURO_prep_mnl_basic.py` would not silently override.  
Equivalently: default bounds in both scripts are identical or both scripts error-out if
bounds are not supplied via config.

**Documentation update:** Update Section E of `RUM_RURO_codebase_audit_v1.md` to mark
P0 gap as resolved.

**Rollback:** Revert both files; no other script is affected.

---

### Phase 1 — Configuration externalisation (Stage 1)

**Goal:** Remove all France-specific constants from `enh_france_data_prep.py` and replace
them with lookups from the country config YAML.  The enhanced data-prep module becomes
country-agnostic.

**Files to touch:**
- `scripts/enhanced/enh_france_data_prep.py` — replace hardcoded constants with
  `config["sample_filters.*"]`, `config["variables.*"]`
- `config/countries/fr_2016.yaml` — **new file** containing all France 2016 constants
  (see Section B.2 for template)
- `scripts/enhanced/enh_prepare_FR_gsur_v2.py` — route METRO_NUTS2 codes and benchmark
  rate through country config (or leave as France-only external-data script, since GSUR
  is inherently France-specific)

**Files not to touch:** estimation engine, legacy scripts, any RURO draw scripts

**Test gate:** Run E1 (data prep equivalence): row counts and column distributions must
match legacy `france_data_prep.py` on FR 2016 input.

**Documentation update:** Update the hardcoded-defaults table in the audit to mark Stage 1
items as resolved.

**Rollback:** Restore `enh_france_data_prep.py` from git; delete `fr_2016.yaml`.

---

### Phase 2 — RURO draw and assembly configuration (Stages 2b and 4b)

**Goal:** Route all draw bounds through the run config YAML.  Eliminate standalone defaults
in `enh_RURO_draws.py` and `enh_RURO_prep_mnl_basic.py`.

**Files to touch:**
- `scripts/enhanced/enh_RURO_draws.py` — read bounds from run config / metadata sidecar;
  error if not supplied
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` — same
- `config/runs/fr_2016_run01.yaml` — **new file** with draw bounds, n_singles, couples mode
- `scripts/enhanced/enh_RURO_estimate_FR.py` — pass run config to draw and prep scripts

**Files not to touch:** estimation engine, legacy scripts, GSUR scripts

**Test gate:** Run E2 and E4 (draw and assembly equivalence) with FR 2016 defaults
reproduced via config YAML.

**Documentation update:** Mark Stage 2b / 4b configuration gaps in audit as resolved.

**Rollback:** Restore both prep scripts and the estimate orchestrator from git.

---

### Phase 3 — Equivalence tests and legacy archival

**Goal:** Run the full equivalence test suite (E1–E6) against the v3 golden reference.
Archive legacy scripts once all tests pass.

**Prerequisite:** Phases 0, 1, 2 complete.

**Files to touch:**
- `docs/estimation/equivalence_golden_v3.json` — **new file**: golden LL and parameter
  vector read from `estimation_results.json`
- Git archive operation: move `scripts/RURO_draws.py`, `RURO_euromod.py`,
  `RURO_prep.py`, `RURO_prep_mnl_basic.py`, `RURO_estimate_FR.py`,
  `france_data_prep.py`, `RURO_post_estimation.py` →
  `scripts/archive/legacy_ruro_root/` as a single commit

**Files not to touch:** enhanced scripts (test them, don't change them)

**Test gate:** All E1–E6 criteria pass.  No regression in the enhanced pipeline.

**Documentation update:** Update `RUM_RURO_codebase_audit_v1.md` to mark legacy scripts
as ARCH.

**Rollback:** `git revert` the archive commit; restore all files.

---

### Phase 4 — RUM branch (Stage 2a + 4a)

**Goal:** Implement `rum_grid_builder.py` (Stage 2a) and add the `prior = 1.0` path to
the data-assembly stage.  Run a first RUM estimation and verify LL is internally consistent.

**Files to touch (new):**
- `scripts/enhanced/rum_grid_builder.py` — reads `interval_length`, `hours_max` from run
  config; outputs `n_alts = floor(hours_max / interval_length)` alternatives per individual:
  `h_j = j × interval_length` for `j ∈ {0, …, n_alts − 1}`; writes long-format parquet
  with `prior = 1.0`

**Files to touch (extend):**
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` — add `prior = 1.0` path when
  `model_type = rum` in run config (so correction term vanishes in engine)
- `scripts/enhanced/enh_RURO_estimate_FR.py` — dispatch to RUM branch based on
  `model_type` key in run config
- One new YAML spec for RUM, annotated `model_type: rum`

**Files not to touch:** `estimation_engine.py` (no change needed)

**Test gate:**
- `n_alts = floor(hours_max / interval_length)` matches configured values for the chosen
  `interval_length` and `hours_max`
- `prior` column is 1.0 for all rows in the assembled RUM data
- Estimation converges (finite LL, no NaN gradients)
- LL is stable across two independent runs with same inputs (deterministic grid)

**Note on utility form:**  
The initial RUM implementation uses Box-Cox utility, which is already executable in the
engine.  Translog (Van Soest 1995) is deferred — adding it requires extending both
`estimation_engine.py` and `estimation_spec_parser.py` and is out of scope for this phase.

**Documentation update:** Create `docs/estimation/RUM_v1_results.md` with first-run LL,
spec, and date.

**Rollback:** Delete `rum_grid_builder.py`; restore `enh_RURO_prep_mnl_basic.py` and
`enh_RURO_estimate_FR.py` from git.

---

### Phase 5 — EUROMOD configuration and multi-country readiness

**Goal:** Replace hardcoded EUROMOD system/dataset strings with lookups from country config
so that a second country (e.g. Belgium 2018) can be run without code changes.

**Files to touch:**
- `scripts/enhanced/enh_RURO_euromod.py` — read system, dataset, disposable income variable
  from country config
- `config/countries/fr_2016.yaml` — add `euromod:` block (see Section B.2)
- `config/countries/be_2018.yaml` — **new** illustrative second-country config (stub)

**Test gate:** FR 2016 production run produces identical output to Phase 3 result.  
Stub BE 2018 config loads without error (data files need not exist).

**Documentation update:** Update `RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` §4 "To add a
new country/year" to reference the country config YAML.

---

## Appendix — RUM Alternative Construction Formula

The formula is user-configurable; worked examples are illustrative, not fixed choices.

```
General:
  n_alts = floor(hours_max / interval_length)
  h_j    = j × interval_length,   j ∈ {0, 1, …, n_alts − 1}
  h_0    = 0   (non-employment; first grid point, not a separate state)
  hours_max is NOT a grid point

Illustrative examples only:
  interval_length=12, hours_max=60:  n_alts=5,  h ∈ {0, 12, 24, 36, 48}
  interval_length=10, hours_max=60:  n_alts=6,  h ∈ {0, 10, 20, 30, 40, 50}
```

---

## Appendix — Utility Form Architecture Decision

**Current engine state:**  
`estimation_spec_parser.py:445` raises `NotImplementedError` if `utility_form != "box_cox"`.
The enhanced engine supports Box-Cox only at runtime, regardless of what the spec declares.

**Decision for RUM implementation:**  
Box-Cox is the deliberate choice for the initial RUM branch.  
Box-Cox with `θ → 0` subsumes log-utility as a special case, providing empirical flexibility.

**Translog status:**  
Van Soest (1995) used translog (`U = α₀ + α₁ ln c + α₂ ln l + α₃(ln c)² + …`).  
Translog is NOT in scope for the current refactor.  Adding it requires:
1. Extending `estimation_engine.py` with a new utility evaluation branch
2. Extending `estimation_spec_parser.py` to parse translog parameters
3. New YAML spec template
4. Separate test suite

Translog may be revisited if an economic motivation arises for comparing RUM translog
vs. Box-Cox results.

---

## Appendix — Opportunity Density Correction Architecture

**RURO (importance sampling):**
```
V_ij = u(c_ij, l_ij) + log h(h_ij) + log w(w_ij) + log_market − log π(h_ij, w_ij)
     = u + log_h + log_w + log_market − np.log(data.prior)   [line 363]
```
`data.prior` = proposal density π > 0, correction is non-zero.

**RUM (deterministic grid):**
```
prior = 1.0  for all alternatives
→ np.log(1.0) = 0
→ correction vanishes: V_ij = u(c_ij, l_ij) + log_market
```

No `model_type` flag is needed in `estimation_engine.py`.  
The branch is controlled entirely by what the data-assembly stage writes to `prior`.  
For a basic RUM with no wage or occupation draws, `log_h` and `log_w` should also be
suppressed by omitting them from the spec or setting them to zero in the assembled data.

---

*End of refactor plan. No code was modified in producing this document.*
