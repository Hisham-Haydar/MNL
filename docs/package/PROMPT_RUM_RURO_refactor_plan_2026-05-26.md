# Prompt Record: RUM/RURO Package Refactor Plan

**Date saved:** 2026-05-26  
**Purpose:** Verbatim copy of the instruction prompt that produced `RUM_RURO_codebase_audit_v1.md`
and `RUM_RURO_package_refactor_plan_v1.md`. Any future agent can read this to understand
exactly what question produced the current state of those documents.

---

## Original Prompt (verbatim)

# Task: Audit and plan the RUM/RURO package refactor

Use the following raw requirement as the domain goal, but turn it into a concrete audit and refactor plan. Do not implement refactors yet.

## Domain Goal

 we begin with plan  and fix a plan for the package to perform RUM and RURO . the code exists it must be cleaned , removing redundancy and repetitiveness cleaning removing unneeded the result should be a code or a pipeline instead of having several scripts it should be generalized, in a way no unnecessary chunks or parts in the code exist, the code must always be country, year, specification agnostic, as usual, if there exist 2 or three scripts that do the same thing they must be unified in 1 for the moment for the scripts I dont want to remove the old until sure that they are 100% efficiently replaced .so there must be a clear plan on how to do so.  the Pipeline starts by reading the input data and if there exist some external data (regional, time variant , group specific ....etc. for example the GSUR data) the data is read the user must using a specifying feature determine the needed filters like age , who to keep who remove based on what , like in my current code for example we keep households with specific criteria non recipient of replacement income les 3 5 7 different sex head and partner, age between 2 numbers etc... ) so the data is cleaned this for example is common for RURO (Random utility random opportuity model )or RUM (random utility model) after this we have the data preparation either RUM RURO here I think we must decide if RUM how many labour hours  alternatives we have (width of the interval) like Van soest 1995 (attached) for example he he argued it can be 1 hour 2 hours 5 hours 6 hours etc... and he choosen 10 and 12 lengh so for and assume 0 60 hours of work then end up with 5 (fort IL =12 ) or 6 for IL =10 , alternatives then we calculate the labor income (yem =  yem00 + yemxp  for france case ) , always the labor income basic and extra hours must be defined by the user , and then the euromod run this step is similar to the draws in RURO where we first need to decide the Opportunity component, usually wage, hours, and in some cases sector or occupation ( my case in france i have wage, hours and occupation aggregated to 4 categories routine non routine and another dimention so from LOC to LOC4 where LOC is isco08 classification of occupations) so given this in RURO the user define the opportunity spaces then the number of draws for singles and then for couples, the user must have option between drawing similarly for couples and singles for example 99 draws +1 the observed for each member in the couples household then for the each draw simultanously for both members of the household they are matched so 100 draws for male and female results in 100 alternatives for the couples household or for example to draw 9 19 29 ( 24 works as well....) but no a large number then a each draw for each member is matched with each other draw of the second member creating an n*m grid so fo 9+1 we have 10 male *10 females = 100 couple  alternatives , or 29 +1 so 30 males *30 females = 900 couples alternatives after the draws for RURO and the interval scenario building for RUM are handled the 2nd step is to run euromod to simulate the after-tax income (ils_dispy usually called) , for the households after this step we prepare the data for estimation either following RUM or RURO then the post estimation. the main goal remain alwasy the package must remain country year specification agnostic. vectorization as much as possible to focus on speed in estimation the main bottlneck in these models is always the estimation so if we can do all the work to make the estimation as smooth and as fast as possible while always resulting in obtaining all needed statistics like the robus ses the hessian matrix, the analytical gradient etc.. 

## Important constraints

- Do not modify package code.

- Do not move, delete, archive, or rename files.

- Documentation-only output is allowed.

- Treat the unified RUM/RURO architecture as a design hypothesis to validate against the existing code and literature.

- Old scripts must remain until equivalence tests prove that the new pipeline replaces them.

- The final package design must be country-, year-, and specification-agnostic.

- Do not assume France 2016, GSUR, LOC4, `yem00 + yemxp`, or `ils_dispy` are universal. Treat them as France-case examples and identify where they must become user-configurable.

- Prioritize vectorized/data-efficient design because estimation is the bottleneck.

- No git commit unless explicitly requested after review.

## Read first

Read these if they exist:

- README.md

- scripts/script_files_structure.md

- scripts/enhanced/README.md

- scripts/Job_model/README_job_model.md

- docs/package/RURO_PATH_MIGRATION_HANDOFF.md

- docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md

- docs/estimation/RURO_ACTIVE_RESULTS_REGISTRY.md

- any model/specification contract files related to RURO/RUM

- any literature files in `literature/`, especially Van Soest 1995 and Capéau-Decoster-Dekkers 2016 if present

## Step 1 — Audit existing codebase

Walk every Python and PowerShell file under:

- scripts/

- src/mnl/ if it exists

Produce:

`docs/package/RUM_RURO_codebase_audit_v1.md`

The audit must cover:

### A. Pipeline stage map

For each stage, list scripts/files involved, with path, purpose, RUM/RURO/shared status, and active/superseded/experimental/archive status:

1. Load input data and external data

2. Apply sample filters

3. Build RUM alternatives or RURO opportunity draws

4. Run EUROMOD and recover disposable income

5. Assemble estimation-ready long data

6. Estimate model

7. Post-estimation/reporting

### B. Duplicate/redundant script families

Group scripts that appear to do the same thing. For each group:

- likely canonical script

- candidate scripts to deprecate later

- why they overlap

- what equivalence check is needed before removal

Do not delete anything.

### C. RUM status

Locate all RUM code, including archived Biogeme/DCM scripts. Explain:

- what exists

- what backend it uses

- what stages are implemented

- what is missing to make RUM a first-class branch beside RURO

### D. RURO status

Map current RURO implementation:

- continuous-hours RURO

- job/occupation-choice RURO

- pilot/precompute/bpool variants

- opportunity components: wage, hours, occupation/LOC4, sector if any

- singles draw logic

- couples draw logic

- matched draws vs Cartesian/grid draws

### E. Configuration gaps

Identify where code is still hardcoded for:

- country

- year

- France-specific variables

- GSUR

- LOC/LOC4

- labour income formula, e.g. `yem = yem00 + yemxp`

- age/filter rules

- replacement-income exclusions

- household/head/partner criteria

- number and construction of alternatives

- EUROMOD system/dataset assumptions

### F. Estimation engine inventory

Inventory estimation-related modules. For each, say whether it supports:

- vectorization

- analytical gradient

- Hessian

- robust SE

- cluster-robust SE

- GAMSPy or SciPy

- warm starts

- specification-driven utility terms

## Step 2 — Refactor architecture plan

Produce:

`docs/package/RUM_RURO_package_refactor_plan_v1.md`

The plan must include:

### A. Target architecture

Design one generalized package pipeline with shared stages and branch points:

- shared: load/filter data

- branch: build alternatives/draws for RUM vs RURO

- shared: EUROMOD simulation

- branch: assemble RUM/RURO estimation data

- shared: estimation engine

- shared: post-estimation/reporting

### B. User-facing configuration design

Define the intended config/spec surface for:

- country and year

- input data paths

- external data sources

- sample filters

- labour income formula

- RUM hours interval width, e.g. Van Soest-style interval length

- RUM alternatives, e.g. 0–60 hours with configurable interval length

- RURO opportunity spaces: wage, hours, occupation/LOC4, sector if applicable

- singles draw counts

- couples draw mode:

  - matched mode: N+1 alternatives per couple

  - grid mode: `(n+1) x (m+1)` alternatives

- EUROMOD system/dataset

- estimation specification

- output/report paths

### C. Canonical script proposal

For each pipeline stage, propose:

- canonical script/module to keep or build toward

- scripts to wrap temporarily

- scripts to deprecate later

- scripts that should stay archived

### D. Equivalence test plan

Define how to prove old scripts are replaced safely:

- golden reference runs

- expected output files

- likelihood comparison

- parameter comparison

- standard error comparison

- Hessian/gradient checks

- tolerance levels

- when it is safe to archive/delete old scripts

### E. Phased migration plan

Give phases. For each phase:

- goal

- files likely touched

- what not to touch

- test gate

- documentation update

- rollback strategy

No implementation yet.

## Step 3 — Save prompt record

Also save this exact prompt as:

`docs/package/PROMPT_RUM_RURO_refactor_plan_2026-05-26.md`

## Output rules

- Write only the documentation files listed above.

- Do not edit code.

- Do not move/delete/archive files.

- Do not commit.

- Keep the plan concrete enough that another agent can implement it phase by phase.

---

## Post-Prompt Amendments (applied before writing the docs)

These clarifications were added by the user after the initial plan was drafted:

1. **RUM alternative formula** — General: `n_alts = floor(hours_max / interval_length)`,
   grid points `h_j = j × interval_length` for j ∈ {0, …, n_alts−1}. `h_0 = 0` (non-employment)
   is the first point. The top endpoint is NOT a grid point. Illustrative examples only:
   IL=12, max=60 → 5 points; IL=10, max=60 → 6 points.

2. **Equivalence golden reference** — Legacy root RURO_*.py only supports continuous RURO.
   Equivalence anchor must be a continuous RURO spec. Use the v3 run in the active results
   registry (`outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/`), reading LL
   from its `estimation_results.json`. P3a and M2e_b are enhanced-only sanity checks.

3. **Utility functional form** — Enhanced engine supports Box-Cox, log, linear (NOT translog).
   Van Soest 1995 used translog; it exists only in the archived Biogeme DCM1 scripts.
   RUM will use Box-Cox as a deliberate architectural choice. Translog is deferred.

4. **RUM likelihood check** — Audit must document whether the engine can suppress the
   opportunity-density correction (g₁, g₂, q proposal terms) via `model_type: rum` in the
   spec YAML. RURO uses importance-sampling correction; RUM (deterministic grid) does not.

5. **Factual corrections to hardcoded-defaults table:**
   - Age range in `enh_france_data_prep.py:113` is **(18, 65)**, not (16, 65).
   - `enh_RURO_draws.py:103-106` defaults: h∈[**5**, 70], w∈[**2**, 170]
   - `enh_RURO_prep_mnl_basic.py:58-61` defaults: h∈[**1**, 70], w∈[**1**, 120]
   - These two sets of defaults are **inconsistent** (P0 configuration gap).
     In practice the pipeline passes bounds via metadata sidecar; standalone default
     mismatch is a latent bug.
