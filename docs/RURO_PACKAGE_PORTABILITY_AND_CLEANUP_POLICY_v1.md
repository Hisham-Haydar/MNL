# RURO Package Portability And Cleanup Policy v1

**Purpose:** define the target package architecture for country/year portability
and the active cleanup policy for generated files.

**Current status:** the production code is not yet fully country/year-agnostic.
France 2016 is the implemented working case. The target package should become
country/year-agnostic by separating generic RURO logic from country/year
harmonization.

---

## 1. Answer To The Main Question

No, the current production code is not fully country/year-agnostic.

You cannot take an arbitrary EUROMOD country/year and run the full pipeline
without editing or adding configuration. France-specific assumptions still live
in:

- raw data preparation;
- education mappings;
- occupation mappings;
- region mappings;
- EUROMOD system/dataset choices;
- path conventions;
- external shifters such as GSUR;
- some documentation and run commands.

The correct target is:

```text
country/year-specific harmonization
  -> canonical RURO schema
  -> generic RURO package engine
```

---

## 2. Generic Package Core

The generic core should not know about France.

It should implement:

- canonical long MNL data loading;
- singles/couples choice-set handling;
- Box-Cox utility;
- opportunity blocks;
- proposal correction;
- YAML spec parsing;
- parameter initialization and bounds;
- likelihood evaluation;
- solver wrappers;
- standard errors and diagnostics;
- post-estimation reporting;
- validation gates.

Candidate future package modules:

```text
src/ruro_mnl/config/
src/ruro_mnl/schema/
src/ruro_mnl/harmonization/
src/ruro_mnl/draws/
src/ruro_mnl/euromod/
src/ruro_mnl/mnl/
src/ruro_mnl/specs/
src/ruro_mnl/estimation/
src/ruro_mnl/reporting/
src/ruro_mnl/cleanup/
```

The current `src/mnl/` is only a scaffold and should not be documented as the
production implementation.

---

## 3. Country/Year Adapter

Each country/year should have a declarative adapter config.

Example target path:

```text
configs/countries/fr_2016.yaml
configs/countries/be_2019.yaml
configs/countries/de_2021.yaml
```

Each adapter should define:

```yaml
country: FR
year: 2016
euromod:
  system: FR_2015
  dataset: FR_2016
  disposable_income_output: ils_dispy
raw_columns:
  household_id: idhh
  person_id: idperson
  sex: dgn
  age: dag
  education: deh
  hours: lhw
  employment_status: les
  employee_income: yem
  occupation: loc
  industry: lindi
  weight: dwt
derived_columns:
  education_mapping: france_deh_to_educ3
  occupation_mapping: loc_to_loc4
  region_mapping: france_drgn1
sample:
  min_age: 18
  max_age: 64
  require_decider: true
```

The exact keys can change, but the principle should not: raw country variables
are mapped once into the canonical schema, and all downstream code consumes the
canonical schema.

---

## 4. Canonical Schema Contract

After harmonization, every country/year must provide the same canonical columns
or explicit documented substitutes.

Minimum required columns before draw generation:

```text
idhh
idperson
dgn
dag
dwt
lhw
les
wage
educ3
educL
educM
educH
pexp
pexp2
ruro_sample
working
loc
loc4
```

Minimum required columns before estimation:

```text
idhh
choice/chosen flag
draw or alternative id
consumption/c_norm
leisure/l_norm
hours
wage
working
prior
log_prior
```

For the Stijn occupation baseline:

```text
loc4
loc4_male
loc4_female
log_q_E/H/W/Occ
log_q_E/H/W/Occ_male
log_q_E/H/W/Occ_female
working_male
working_female
```

---

## 5. Adding A New Country/Year

Required steps:

1. Create or verify EUROMOD variable reference files for that country/year.
2. Create a country/year harmonization config.
3. Implement or select education mapping.
4. Implement or select occupation mapping.
5. Implement or select region mapping.
6. Define the EUROMOD system and dataset names.
7. Build RURO-ready files.
8. Run a small draw canary.
9. Run EUROMOD on a small canary if possible.
10. Build MNL parquets.
11. Run prior and schema validation.
12. Only then run estimation.

No new country/year should bypass the canonical schema validation.

---

## 6. Validation Gates For Portability

Every country/year must pass:

```text
V0: raw files exist and load
V1: required raw columns exist or are mapped
V2: canonical schema exists after harmonization
V3: sample restrictions are recorded
V4: draw metadata matches draw command
V5: EUROMOD output contains disposable income source
V6: MNL files contain required model columns
V7: prior > 0
V8: log_prior == log(prior)
V9: model-specific proposal reconstruction holds
```

For occupation models:

```text
V10: occupation varies across working alternatives
V11: non-work occupation contribution is gated off
```

---

## 7. Cleanup Policy

The cleanup policy is active, but it is archive-first.

The project should avoid silent accumulation of obsolete generated artifacts,
but it must not silently destroy provenance.

Allowed automatic cleanup:

- remove temporary scratch files created in the current run;
- remove partial files inside a run-specific temporary directory after failure;
- clean empty directories created by a failed current run;
- overwrite files only when the output path is run-specific or explicitly
  declared replaceable.

Archive-first cleanup:

- deterministic draw files;
- deterministic MNL files;
- EUROMOD scenario directories;
- canary reports tied to a data state;
- result folders that were once candidates.

Never auto-delete:

- raw data;
- EUROMOD releases;
- external reference documentation;
- active result registry entries;
- active baseline result folders;
- documentation explaining current methods;
- files not created by the current pipeline run.

---

## 8. Replacement Rule

When a step replaces a deterministic file, use this rule:

```text
if target exists and target is not a run-specific timestamped output:
    move/copy target to archive path with timestamp and reason
    write replacement
    write manifest entry
```

Example archive naming:

```text
fr_2016_RURO_mnl__singles__archived_YYYYMMDD_HHMMSS__before_stijn_occ.parquet
```

Every archive action should record:

```text
source path
archive path
timestamp
reason
command or script
git commit if available
user or machine
```

---

## 9. Cleanup Manifest

Each cleanup/archive pass should write a manifest.

Suggested path:

```text
outputs/manifests/cleanup_manifest_YYYYMMDD_HHMMSS.json
```

Suggested fields:

```json
{
  "created_at": "...",
  "mode": "archive-first",
  "entries": [
    {
      "action": "archive",
      "source": "...",
      "destination": "...",
      "reason": "...",
      "safe_to_delete_original": false
    }
  ]
}
```

Deletion should be a separate reviewed action, not the default replacement
behaviour.

---

## 10. Temporary State Policy

Temporary state must be isolated.

Preferred paths:

```text
outputs/tmp/<run_id>/
Z:/hisham/EUROMOD-STORAGE/interim/ruro/<country>/<year>/<experiment>/tmp/
```

Rules:

- temporary files must include the run id or experiment id;
- temporary directories may be removed after a successful run;
- failed temporary directories may be removed only after logs and manifests are
  preserved;
- no script should use a generic shared `tmp` path for important intermediate
  data.

---

## 11. Current Refactor Roadmap

Short-term:

- keep `scripts/enhanced/` and `scripts/Job_model/` as production;
- document every active command and validation gate;
- keep Stijn M0 rebuild commands and canaries current;
- keep cleanup archive-first and manifest-based.

Medium-term:

- introduce country/year config files;
- move harmonization functions behind an adapter interface;
- move reusable schema validation into package code;
- make draw and MNL prep scripts read country/year config;
- turn active scripts into thin wrappers.

Long-term:

- package the generic RURO engine;
- expose stable CLI entrypoints;
- support multiple countries/years without editing estimator code;
- keep country-specific assumptions only in configs and adapters.

---

## 12. Documentation Rule

Any new feature must update documentation in the same pass:

- method effect;
- affected files;
- command changes;
- required columns;
- validation gates;
- cleanup/overwrite risk;
- what remains unimplemented.

If a future user must read a script to understand ordinary workflow behaviour,
the documentation is incomplete.
