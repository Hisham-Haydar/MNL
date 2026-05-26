# RUM/RURO Codebase Audit — v2

> **v2 note:** Supersedes v1 in Sections C and F.4 only. Sections A–B, D–E, F.1–F.3, F.5
> are unchanged from `RUM_RURO_codebase_audit_v1.md`. Read v1 for unchanged sections.
> Changes: (1) F.4 — downgraded "no engine change needed" from established fact to
> unverified hypothesis; all four extra V terms must be zero for pure RUM, not just prior.
> (2) C — added ASC requirement. (3) F.4 — added Phase 1 spike as the verification gate.

**Date:** 2026-05-27  
**Status:** Documentation only — no code was modified  
**Produced by:** Revision of v1 per user review, 2026-05-27  
**Companion documents:**  
- `RUM_RURO_package_refactor_plan_v2.md` — revised architecture and migration plan  
- `RUM_RURO_codebase_audit_v1.md` — previous version  
- `PROMPT_RUM_RURO_refactor_plan_2026-05-26.md` — verbatim prompt record  

---

## Section A — Pipeline Stage Map

*(Unchanged from v1. Reproduced for completeness.)*

The pipeline has seven logical stages. Each table row gives path, purpose, whether the
script is shared between RUM and RURO or specific to one model type, and operational status.

### Status legend

| Code | Meaning |
|------|---------|
| ACTIVE | canonical production script, runs routinely |
| MAINT | maintenance-mode; kept for equivalence testing, no new features |
| PILOT | diagnostic / experimental; not part of routine production |
| ARCH | archived; frozen provenance record |

---

### Stage 1 — Load input data and external data

| Path | Purpose | Shared/RUM/RURO | Status |
|------|---------|-----------------|--------|
| `scripts/enhanced/enh_france_data_prep.py` | Load raw SILC/EUROMOD microdata, merge GSUR, apply France-specific variable transforms | SHARED | ACTIVE (canonical) |
| `scripts/france_data_prep.py` | Legacy equivalent of above; predates enhanced pipeline | SHARED | MAINT |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | Build GSUR lookup from INSEE data; writes to `external/` | SHARED | ACTIVE |
| `scripts/enhanced/enh_prepare_FR_gsur.py` | First version of GSUR build; superseded by v2 | SHARED | MAINT |
| `scripts/prepare_FR_gsur.py` | Legacy root-level GSUR prep | SHARED | MAINT |
| `scripts/multi_year/m1_config.py` | Configuration constants for multi-year data stacking | SHARED | ACTIVE |
| `scripts/multi_year/m1_isf_check_2018.py` | ISF validation for 2018 add-on data | SHARED | ACTIVE |
| Other `scripts/multi_year/m1_*.py` | Multi-year harmonisation and stacking utilities | SHARED | ACTIVE |

---

### Stage 2 — Apply sample filters

Filtering is not an isolated stage in the current codebase; it is embedded inside Stage 1
scripts.  Canonical logic is in `enh_france_data_prep.py` (see Section E for hardcoded
filter constants).  Legacy `france_data_prep.py` replicates the same filters.

---

### Stage 3 — Build RUM alternatives or RURO opportunity draws

#### RURO — continuous-hours variant

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/enhanced/enh_RURO_draws.py` | Vectorised draw generation: non-employment Bernoulli, hours Uniform, wage Uniform, occupation empirical or fixed | ACTIVE (canonical) |
| `scripts/RURO_draws.py` | Legacy draw generator; no multistart, no metadata sidecar | MAINT |

#### RURO — job / occupation-choice variant (LOC4)

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/Job_model/enh_job_universe.py` | Build job universe: `empirical_pruned`, `empirical_all`, `full_grid`, `gmm_occ`, `kmeans_occ` | ACTIVE |
| `scripts/Job_model/enh_job_draws.py` | Draw from job universe; outputs `job_id`, `hours_bin`, `wage_bin`, `isco1`, `prior` | ACTIVE |

#### RURO — bpool (precomputed opportunity pool)

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/bpool/build_bpool_singles.py` | Build single-person opportunity pool | ACTIVE |
| `scripts/bpool/build_bpool_couples.py` | Build couple opportunity pool | ACTIVE |
| `scripts/bpool/build_bpool_precompute.py` | Precompute tax-benefit for pool entries | ACTIVE |
| `scripts/bpool/assemble_bpool_priced.py` | Merge EUROMOD prices into pool | ACTIVE |
| `scripts/bpool/run_bpool_draws.py` | Draw from precomputed pool at estimation time | ACTIVE |

#### RUM — Van Soest-style discrete-interval grid

**No active RUM alternative-construction script exists.**  
The archived DCM scripts constructed alternatives, but those were removed from the active
pipeline when the Biogeme/GAMSPy RUM experiments concluded.  Implementing Stage 3 for RUM
is the primary gap for making RUM a first-class pipeline branch (see Section C).

---

### Stage 4 — Run EUROMOD and recover disposable income

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/enhanced/enh_RURO_euromod.py` | Launch EUROMOD for each draw scenario; recover `ils_dispy`; write parquet | ACTIVE (canonical) |
| `scripts/RURO_euromod.py` | Legacy EUROMOD runner; no metadata sidecar | MAINT |
| `scripts/bpool/run_bpool_euromod.py` | EUROMOD for bpool entries (chunked variant also available) | ACTIVE |
| `scripts/bpool/run_bpool_euromod_chunk.py` | Chunked EUROMOD runner for large pools | ACTIVE |

---

### Stage 5 — Assemble estimation-ready long data

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Core: merge draws with EUROMOD output, compute disposable income, filter bounds, write long-form parquet | ACTIVE (canonical) |
| `scripts/enhanced/enh_RURO_prep.py` | Enhanced variable construction: education dummies, regional dummies, focal-hours dummies, GSUR merge | ACTIVE |
| `scripts/RURO_prep_mnl_basic.py` | Legacy version of `enh_RURO_prep_mnl_basic.py` | MAINT |
| `scripts/RURO_prep.py` | Legacy variable construction | MAINT |
| `scripts/enhanced/reduce_mnl_columns.py` | Reduce parquet column count to spec-required subset | ACTIVE |
| `scripts/enhanced/reduce_draws_files.py` | Trim draw files for storage/transfer | ACTIVE |

---

### Stage 6 — Estimate model

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/enhanced/estimation_engine.py` | Core log-likelihood, gradient, Hessian (NumPy vectorised) | ACTIVE (canonical) |
| `scripts/enhanced/estimation_spec_parser.py` | Parse YAML spec → typed `EstimationSpec` dataclass | ACTIVE |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | GAMSPy/CONOPT nonlinear solver wrapper (vectorised, 2026-01-28) | ACTIVE (primary solver) |
| `scripts/enhanced/gamspy_estimation.py` | Older non-vectorised GAMSPy wrapper | MAINT |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | Pipeline orchestrator: multistart, spec loop, group dispatch, metadata | ACTIVE |
| `scripts/RURO_estimate_FR.py` | Legacy estimation entry point | MAINT |
| `scripts/enhanced/parallel_estimation.py` | Parallel group-level estimation utility | ACTIVE |
| `scripts/enhanced/specifications/` (52 YAML files) | All estimation specs; drive every configurable choice | ACTIVE |
| `scripts/archive/rum_approach/RUM/DCM1*.py` | Biogeme / SciPy RUM experiments | ARCH |
| `scripts/archive/rum_approach/RUM/DCM2_gamspy*.py` | GAMSPy RUM experiments | ARCH |

---

### Stage 7 — Post-estimation / reporting

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/enhanced/compute_standard_errors.py` | Hessian-based SE, McFadden ρ², AIC/BIC | ACTIVE |
| `scripts/enhanced/cluster_robust_se.py` | Cluster-robust sandwich SE (clustering by `idorighh`) | ACTIVE |
| `scripts/enhanced/run_cluster_robust_se.py` | CLI entry point for cluster-robust SE | ACTIVE |
| `scripts/RURO_post_estimation.py` | Legacy post-estimation | MAINT |
| `scripts/run_post_estimation_standalone.py` | Standalone post-estimation runner | ACTIVE |
| `scripts/generate_html_report.py` | Styled HTML/Markdown report generation | ACTIVE |
| `scripts/pilot/_run_diagnostic_estimation.py` | P3a diagnostic estimation run | PILOT |
| `scripts/Job_model/sanity_checks_job.py` | Job-choice model validation | ACTIVE |
| `scripts/enhanced/diagnostic_consumption_variation.py` | Consumption diagnostics | ACTIVE |
| `scripts/enhanced/diagnostics_bundle.py` | Bundled diagnostics | ACTIVE |
| `scripts/enhanced/sanity_checks.py` | General sanity checks | ACTIVE |

---

## Section B — Duplicate / Redundant Script Families

*(Unchanged from v1.)*

### Family 1: Data preparation and sample filtering

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_france_data_prep.py` | `scripts/enhanced/` | **YES** | `france_data_prep.py` |
| `france_data_prep.py` | `scripts/` | NO (MAINT) | — |

**Overlap:** Both load the raw microdata, apply age/LES/replacement-income filters, compute
labour income, and write a clean parquet.  The enhanced version adds metadata sidecar writing.

**Equivalence check needed:** Run both on FR 2016; compare row counts, column means,
distribution of filtered households.

---

### Family 2: GSUR build

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_prepare_FR_gsur_v2.py` | `scripts/enhanced/` | **YES** | `enh_prepare_FR_gsur.py`, `prepare_FR_gsur.py` |
| `enh_prepare_FR_gsur.py` | `scripts/enhanced/` | NO (MAINT) | `prepare_FR_gsur.py` |
| `prepare_FR_gsur.py` | `scripts/` | NO (MAINT) | — |

**Equivalence check needed:** Compare GSUR lookup tables produced by all three; verify
identical GSUR assignment for matched households.

---

### Family 3: RURO draw generation

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_RURO_draws.py` | `scripts/enhanced/` | **YES** | `RURO_draws.py` |
| `RURO_draws.py` | `scripts/` | NO (MAINT) | — |

**Overlap:** Both draw hours, wage, and non-employment status.  Enhanced adds metadata
sidecar, occupation draws, and fully vectorised NumPy operations.

**Equivalence check needed:** Draw seeds fixed → compare draw distributions; verify
proposal-density columns match.

---

### Family 4: EUROMOD runner

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_RURO_euromod.py` | `scripts/enhanced/` | **YES** | `RURO_euromod.py` |
| `RURO_euromod.py` | `scripts/` | NO (MAINT) | — |

**Equivalence check needed:** Same draws → same EUROMOD input → compare `ils_dispy` output
row-for-row.

---

### Family 5: MNL data assembly

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_RURO_prep_mnl_basic.py` | `scripts/enhanced/` | **YES** | `RURO_prep_mnl_basic.py` |
| `RURO_prep_mnl_basic.py` | `scripts/` | NO (MAINT) | — |
| `enh_RURO_prep.py` | `scripts/enhanced/` | **YES** (variable construction) | `RURO_prep.py` |
| `RURO_prep.py` | `scripts/` | NO (MAINT) | — |

**Critical difference:** The two `_prep_mnl_basic.py` scripts have INCONSISTENT default
draw bounds (see Section E, P0 gap).  In production the bounds are passed via the metadata
sidecar, so runtime behaviour is correct; the standalone default mismatch is a latent bug.

---

### Family 6: Estimation entry point

| Script | Location | Canonical? | Supersedes |
|--------|----------|-----------|----------|
| `enh_RURO_estimate_FR.py` | `scripts/enhanced/` | **YES** | `RURO_estimate_FR.py` |
| `RURO_estimate_FR.py` | `scripts/` | NO (MAINT) | — |

**Major capability gap:** Legacy `RURO_estimate_FR.py` has no multistart, no GAMSPy solver,
no metadata sidecar, no cluster-robust SE.  It cannot run enhanced specs.

---

## Section C — RUM Status

*(v2 change: added ASC requirement under "What is missing"; archived status table unchanged.)*

### What exists (archived)

All RUM code is frozen in `scripts/archive/rum_approach/RUM/`.

| File | Backend | Utility form | Stages implemented |
|------|---------|-------------|-------------------|
| `DCM1.py` | Biogeme | **Translog** | Data prep, MNL estimation, reporting |
| `DCM1_boxcox.py` | Biogeme / SciPy L-BFGS-B | Box-Cox | Data prep, Box-Cox utility, analytical gradient |
| `DCM1_boxcox_gender_split.py` | SciPy | Box-Cox | Gender-specific Box-Cox exponents |
| `DCM1_gamspy.py` | GAMSPy (IPOPTH/CONOPT/KNITRO) | Box-Cox | GAMSPy nonlinear model, demographic shifters |
| `DCM2_gamspy.py` | GAMSPy | Box-Cox | Pooled MNL, gender shifters |
| `DCM2_gamspy_gender_split.py` | GAMSPy | Box-Cox | Pooled + gender-split Box-Cox |
| `data_prep.py` | — | — | Wide-to-long, draw generation (for archived specs) |
| `train_mnl.py` | various | various | Legacy MNL training loop |
| Other `old_*.py`, `biotest.py` | Biogeme/deprecated | Mixed | Legacy |

**What the archives do NOT have:**
- Van Soest-style discrete-interval alternative construction using the general formula
  `n_alts = floor(hours_max / interval_length)`
- A configurable `interval_length` / `hours_max` parameter (numbers were hardcoded)
- Country-agnostic data loading
- Metadata sidecar pattern
- Connection to the active YAML-spec system
- Hours-category alternative-specific constants (ASCs) implemented within the active
  estimation-spec system

---

### What is missing for RUM as a first-class branch

1. **Stage 3 — discrete-interval grid builder** (entirely missing from active pipeline):
   - A module that accepts `hours_max` and `interval_length` from the pipeline config
   - Generates alternatives `h_j = j × interval_length` for `j ∈ {0, …, n_alts − 1}`,
     where `n_alts = floor(hours_max / interval_length)`
   - `h_0 = 0` is the first grid point (non-employment); the top endpoint `hours_max` is
     NOT a grid point
   - If `interval_length` does not divide `hours_max` exactly, the trailing partial interval
     `[n_alts × interval_length, hours_max)` is excluded; no grid point is generated there
   - Computes labour income `c_ij` for each `(individual i, hours alternative j)` pair
   - Writes long-format parquet compatible with `enh_RURO_prep_mnl_basic.py` structure

2. **Hours-category alternative-specific constants (ASCs) — required for credible fit:**
   Van Soest (1995) found that Model I (utility only, no ASCs) produced systematically
   wrong predictions; Model II (utility + ASCs on the part-time / full-time categories)
   was needed for the model to fit observed labour supply choices.  ASCs absorb systematic
   preference for particular hours ranges that the utility function alone cannot explain.
   - The grid builder must generate an ASC indicator for each hours category except the
     reference (conventionally h_0 = 0, non-employment)
   - The estimation YAML spec must be able to declare ASC parameters for each non-reference
     hours category
   - This is a required feature for any empirically credible RUM; it is not optional

3. **Stage 5 — data assembly**:
   - Set `prior = 1.0` for all rows (deterministic grid → importance weight = 1)
   - This is necessary but not sufficient: see Section F.4 for the full engine-compatibility
     analysis and the unverified hypothesis about `log_h`, `log_w`, `log_market`

4. **Stage 6 — estimation**:
   - Engine compatibility is an **unverified hypothesis** (see Section F.4 for details)
   - If the engine can suppress all four non-utility terms without code change, no engine
     edit is needed.  Phase 1 spike must determine this before any RUM implementation begins
   - Spec YAML needs `model_type: rum` annotation and ASC parameter declarations

5. **Configuration**:
   - `interval_length` and `hours_max` must be user-configurable; no hardcoded values
   - Labour income formula must be configurable (France: `yem = yem00 + yemxp`)
   - Multiple alternative-width examples illustrate the formula without fixing it:
     - `IL=12, max=60`: n_alts = floor(60/12) = 5, h ∈ {0, 12, 24, 36, 48}
     - `IL=10, max=60`: n_alts = floor(60/10) = 6, h ∈ {0, 10, 20, 30, 40, 50}

6. **Utility form**:
   - Translog (Van Soest 1995 original) is NOT implemented in the enhanced engine (see
     Section F). RUM will use Box-Cox as a deliberate architectural choice.

---

## Section D — RURO Status

*(Unchanged from v1.)*

### D.1 Continuous-hours RURO

**Implementation:** complete in both legacy and enhanced pipelines.

Draw model:
- Non-employment: Bernoulli(π₀) with `π₀ = 0.10` for both male and female (default)
- Hours (conditional on employment): Uniform[h_min, h_max]
- Wage (conditional on employment, `vw` spec only): Uniform[w_min, w_max]
- Wage (fixed, `fw` spec): observed wage used directly

Opportunity components supported:
- `wage_spec: fw` — fixed observed wage; no wage draw
- `wage_spec: vw` — variable wage drawn from Uniform; proposal density includes `log_w`
- `wage_spec: loc_empirical` — occupation-conditioned wage; Job model branch

**Draw defaults (inconsistency — P0 gap, see Section E):**

| Script | h_min | h_max | w_min | w_max |
|--------|-------|-------|-------|-------|
| `enh_RURO_draws.py:103-106` | **5.0** | 70.0 | **2.0** | **170.0** |
| `enh_RURO_prep_mnl_basic.py:58-61` | **1.0** | 70.0 | **1.0** | **120.0** |
| `RURO_prep_mnl_basic.py:26-29` | **1.0** | 70.0 | **1.0** | **120.0** |

The inconsistency is a latent bug.  In production, bounds are passed from `enh_RURO_draws.py`
to downstream stages via a JSON metadata sidecar, so runtime behaviour is correct.  Running
either prep script standalone with default values would silently use different bounds.

---

### D.2 Job/Occupation-choice RURO

**Implementation:** active, enhanced pipeline only (`scripts/Job_model/`).

Opportunity components:
- Hours bin (`hours_bin`): discrete categories from job universe
- Wage bin (`wage_bin`): discrete from job universe
- Occupation (`isco1` / LOC4): 4-category classification (routine/non-routine ×
  manual/cognitive) derived from ISCO08 `loc` field

Job universe modes (`enh_job_universe.py`):
- `empirical_pruned` (default): observed (hours, wage, occ) tuples, low-count cells pruned
- `empirical_all`: all observed tuples retained
- `full_grid`: Cartesian product of hours × wage × occ bins (deterministic grid)
- `gmm_occ`: GMM-latent-type occupation grouping (implemented)
- `kmeans_occ`, `hier_occ`: clustering-based (stubs)

**Singles draw:** N independent draws from universe per individual  
**Couples draw (matched mode):** N draws for male head + N draws for female head; draws
matched 1:1 to produce N couple alternatives  
**Couples draw (grid mode):** available via `full_grid` universe mode in job model;
(n+1)×(m+1) Cartesian product with separate male/female draw counts not yet user-configurable
in the continuous-hours pipeline

**Last validated:** 2026-02-04 (FR 2016, 199 simulated draws)

---

### D.3 Pilot / bpool variants

**bpool (precomputed pool):**
- Precomputes EUROMOD scenarios for a large pool of (hours, wage, occ) tuples
- At estimation time, each individual draws from the pre-priced pool → no EUROMOD call
  during estimation iterations
- Scripts: `scripts/bpool/` (13 files)
- Status: ACTIVE; used for P3a pooled spec

**Pilot:**
- Small-sample diagnostic runs to validate the pipeline before full estimation
- Scripts: `scripts/pilot/` (25 files)
- Status: PILOT; not part of routine production

---

## Section E — Configuration Gaps

*(Unchanged from v1.)*

### P0 (must fix before equivalence testing)

| Gap | Location | Hardcoded value | Should become |
|-----|----------|----------------|---------------|
| Draw bounds mismatch: h_min | `enh_RURO_draws.py:103` vs `enh_RURO_prep_mnl_basic.py:58` | 5.0 vs 1.0 | Single source, passed via metadata sidecar |
| Draw bounds mismatch: w_min | `enh_RURO_draws.py:105` vs `enh_RURO_prep_mnl_basic.py:60` | 2.0 vs 1.0 | Single source, passed via metadata sidecar |
| Draw bounds mismatch: w_max | `enh_RURO_draws.py:106` vs `enh_RURO_prep_mnl_basic.py:61` | 170.0 vs 120.0 | Single source, passed via metadata sidecar |

**Note:** In production the pipeline reads bounds from the metadata sidecar written by
`enh_RURO_draws.py`, so runtime is correct.  The standalone defaults are the latent bug.

---

### P1 (France-specific hardcoding — must abstract for multi-country)

| Layer | File | Line | Hardcoded for France | User-configurable target |
|-------|------|------|---------------------|--------------------------|
| Data prep | `enh_france_data_prep.py` | 113 | `age_range: (18, 65)` | `sample_filters.age_min`, `sample_filters.age_max` |
| Data prep | `enh_france_data_prep.py` | — | LES thresholds [3, 5, 7] | `sample_filters.les_thresholds` |
| Data prep | `enh_france_data_prep.py` | — | Replacement income columns: `bun`, `bsa`, `poa`, `pdi` | `sample_filters.replacement_income_columns` |
| Data prep | `enh_france_data_prep.py` | — | Education codes `deh` 0–5 | `variables.education_column` + `variables.education_codes` |
| Data prep | `enh_france_data_prep.py` | — | NUTS-1 region codes | `variables.region_column` + `variables.region_codes` |
| Labour income | `enh_france_data_prep.py` | — | `yem = yem00 + yemxp` | `variables.labour_income_formula` |
| RURO variables | `enh_RURO_prep.py` | — | Focal hours 20h, 30h, 40h | `ruro.focal_hours` |
| RURO variables | `enh_RURO_prep.py` | — | Education start ages | `variables.education_start_ages` |
| RURO variables | `enh_RURO_prep.py` | — | 10 regional dummy columns | `variables.region_dummies` |
| Draw constants | `enh_RURO_draws.py` | 103-106 | Total leisure 80h, π₀=0.10 M/F | `ruro.draws.total_leisure`, `ruro.draws.pi0_male`, `ruro.draws.pi0_female` |
| GSUR build | `enh_prepare_FR_gsur_v2.py` | — | METRO_NUTS2 22 codes | Country-specific external data config |
| GSUR build | `enh_prepare_FR_gsur_v2.py` | — | ISCED→educ3 mapping | Country-specific mapping config |
| GSUR build | `enh_prepare_FR_gsur_v2.py` | — | Benchmark rate 9.725%, Corsica fix | Country-specific calibration |
| Multi-year | `m1_config.py` | — | FR deflation columns | Country-specific variable config |
| Multi-year | `m1_config.py` | — | uid formula | Country-specific id construction |

---

### P2 (EUROMOD assumptions)

| Gap | Location | Hardcoded | Should become |
|-----|----------|----------|---------------|
| EUROMOD system name | Various | France system `FR_2016` style | `euromod.system` in pipeline config |
| EUROMOD dataset | Various | `FR_2016_std` style | `euromod.dataset` in pipeline config |
| Disposable income variable | Various | `ils_dispy` | `euromod.disposable_income_variable` |
| EUROMOD installation path | `~/.mnl/config.yaml` | User-configured | Already solved via `path_helpers.py` |

---

### P3 (diagnostic scripts — deferred, not active pipeline)

`scripts/diagnostics/check_nchildren_simple.py:8`,
`check_preference_diagnostics.py:8`, and `check_type_ids.py:7`
still contain hardcoded `Z:/hisham/EUROMOD-STORAGE/...` paths.
These are ad-hoc scripts; fix when converting to active use.

---

## Section F — Estimation Engine Inventory

### F.1 Core files

*(Unchanged from v1.)*

| File | Role |
|------|------|
| `scripts/enhanced/estimation_engine.py` | Log-likelihood, gradient, Hessian (NumPy) |
| `scripts/enhanced/estimation_spec_parser.py` | YAML → `EstimationSpec` dataclass |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | GAMSPy/CONOPT solver (primary) |
| `scripts/enhanced/gamspy_estimation.py` | Older non-vectorised GAMSPy (backup) |
| `scripts/enhanced/parallel_estimation.py` | Parallel group dispatch |
| `scripts/enhanced/compute_standard_errors.py` | SE, ρ², AIC/BIC |
| `scripts/enhanced/cluster_robust_se.py` | Cluster-robust sandwich SE |

---

### F.2 Capability matrix

*(Unchanged from v1.)*

| Capability | Supported | Notes |
|-----------|-----------|-------|
| Vectorisation | YES | Full NumPy; no Python loops in hot path |
| Analytical gradient | YES | GAMSPy/CONOPT computes exact derivatives |
| Hessian | YES | GAMSPy provides exact; SciPy provides finite-difference approximation |
| Robust SE (Hessian-based) | YES | `compute_standard_errors.py` |
| Cluster-robust SE | YES | `cluster_robust_se.py`; clustering by `idorighh` |
| GAMSPy / CONOPT | YES | Primary solver via `gamspy_estimation_vectorized.py` |
| SciPy L-BFGS-B | YES | Fallback; used in some pilot specs |
| Warm starts / multistart | YES | `enh_RURO_estimate_FR.py` orchestrates multistart with jitter |
| Spec-driven utility terms | YES | 52 YAML specs; demographic shifters, income-leisure interactions |

---

### F.3 Utility functional forms

*(Unchanged from v1.)*

| Form | Declared in spec parser | Actually executable | Notes |
|------|------------------------|--------------------|----|
| `box_cox` | YES | **YES** | Primary and only usable form |
| `log` | YES (declared) | **NO** | `estimation_spec_parser.py:445` raises `NotImplementedError` if `utility_form != "box_cox"` |
| `linear` | YES (declared) | **NO** | Same as above |
| Translog | NOT in enhanced engine | **NO** | Only in `scripts/archive/rum_approach/RUM/DCM1.py` (Biogeme); deliberately excluded |

**Box-Cox form:** `U = (x^θ − 1)/θ` (reduces to `ln x` as `θ → 0`).  
Both consumption `θ_c` and leisure `θ_l` are estimated; gender-specific exponents supported.

**Translog status:** Van Soest (1995) used translog
(`U = α₀ + α₁ln c + α₂ln l + α₃(ln c)² + α₄(ln l)² + α₅ ln c · ln l`).  
This form is not in scope for the current refactor.  Adding it would require
extending `estimation_engine.py` and `estimation_spec_parser.py`.

---

### F.4 Opportunity density correction — RUM compatibility

*(v2 change: v1 claim "no engine change needed" downgraded to unverified hypothesis.
The prior=1.0 trick only zeros the last term; three other terms must also be zero
for a genuine pure-RUM index. Whether those can be suppressed without code change is
unverified — Phase 1 spike must determine it.)*

---

**The full engine composite value index (`estimation_engine.py:363`):**

```
V_ij = u(c_ij, l_ij)     [utility: Box-Cox of consumption and leisure]
     + log_h(h_ij)        [log density of hours draw: g₂(h)]
     + log_w(w_ij)        [log density of wage draw: g₁(w)]
     + log_market_ij      [log market opportunity: related to GSUR/local unemployment rate]
     − np.log(data.prior) [importance-sampling correction: −log π(h, w)]
```

In RURO, draws are random from Uniform densities; `prior` = π(h, w) ≠ 1, so all four
RURO-specific terms (`log_h`, `log_w`, `log_market`, `-log_prior`) are non-trivial.

---

**What a genuine Van Soest RUM requires:**

In RUM (Van Soest 1995, eq. 16), alternatives are a deterministic grid with no random
opportunity component.  The index for RUM must equal:

```
V_ij = u(c_ij, l_ij) + ASC_j   [utility + optional hours-category constant]
```

That means ALL FOUR non-utility terms must be identically zero:

| Term | RURO | RUM target | How to achieve |
|------|------|-----------|----------------|
| `log_h` | non-zero (Uniform hours density) | = 0 | Unverified: wage_spec="fw" may suppress log_h if hours density is not computed separately; Phase 1 must confirm |
| `log_w` | non-zero (Uniform wage density, vw spec) | = 0 | Potentially: use `wage_spec="fw"` (fixed/observed wage); verify that log_w is then set to 0 in engine |
| `log_market` | non-zero (GSUR-based opportunity term) | = 0 | Unverified: unclear whether omitting GSUR from spec zeros this term or whether engine still computes it; Phase 1 must confirm |
| `−log(prior)` | non-zero | = 0 | Achievable: write `prior = 1.0` for all rows in data assembly; `−log(1.0) = 0` |

---

**Current engine state regarding RUM:**

- No `model_type` flag exists in `estimation_engine.py` to suppress RURO-specific terms
- The terms are named `g1`, `g2`, `q_proposal` in the literature but stored as `log_h`,
  `log_w`, `log_market`, and `data.prior` in the engine
- Whether spec choices (e.g. `wage_spec="fw"`, omitting `log_market` from spec) can zero
  each term **without engine code changes is unverified**

---

**Hypothesis (to be tested by Phase 1 spike):**

> The enhanced engine can produce a pure-RUM index `V = u + ASC_j` by choosing
> `wage_spec="fw"`, omitting opportunity terms from the spec, and writing `prior = 1.0`
> in the assembled data — without any modification to `estimation_engine.py`.

**If the hypothesis holds:** Phase 4 can proceed without engine changes.  
**If the hypothesis fails:** Engine work enters Phase 4 scope; a `model_type: rum` flag
must be added to `estimation_engine.py` to suppress `log_h`, `log_w`, and `log_market`
independently of spec choices.

This determination is the sole purpose of Phase 1 (RUM verification spike).

---

### F.5 Golden reference for equivalence testing

*(Unchanged from v1.)*

**Continuous RURO v3 run (the only valid equivalence anchor for legacy ↔ enhanced comparison):**

```
Path:  outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
File:  estimation_results.json
LL:    -6608.591013943798   (read verbatim from JSON; verify before citing)
Spec:  base_vw_with_interaction  (wage_spec: vw)
Time:  2026-02-05T14:15:40 UTC+0, 20 iterations, 56.99 s
```

**Why this run is the anchor:**  
Legacy `RURO_*.py` supports only continuous RURO.  P3a and M2e_b are enhanced-only
(pooled / job-choice) and cannot be replicated by the legacy pipeline.

**Before running equivalence tests:**  
Read `estimation_results.json` directly to confirm the LL; do not rely on cached values.
Record the confirmed LL in the equivalence test section of the refactor plan.

---

*End of audit v2. No code was modified in producing this document.*
