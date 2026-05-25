# RURO Naming And Package Scope v1

## Purpose

The package-facing terminology describes the model as **RURO** (Random
Utility Random Opportunity), never with a person-specific label. Earlier
development files used `ruro_occ` as a working label because the
continuous branch was compared against an existing R reference
implementation; that label has been fully retired across the active tree.

Personal acknowledgement is centralised — and centralised only — in:

```text
docs/ACKNOWLEDGEMENTS.md
```

## Preferred Terms

| Use | Do not use |
| --- | --- |
| continuous RURO baseline | "Stijn-style RURO baseline" |
| RURO occupation-opportunity M0 | "Stijn occupation M0" |
| proposal-component aliases | "Stijn proposal aliases" |
| proposal-density correction | "Stijn prior correction" |
| layered proposal components | "Stijn log_q aliases" |
| enhanced continuous RURO branch | "Stijn-style enhanced branch" |
| the R reference implementation | "Stijn's R implementation" |
| the continuous RURO reference design | "Stijn's continuous model" |
| R reference work / R reference files | "Stijn's R work" / "Stijn's R files" |

## Active Specification Name

All runs use:

```text
scripts/enhanced/estimation_spec_ruro_occ_M0.yaml
```

The previously-retained compatibility file
`scripts/enhanced/estimation_spec_stijn_occ_M0.yaml` has been **deleted**
as a byte-identical duplicate of the canonical RURO YAML. Any old commands
referencing the legacy path must be updated.

The estimation results JSON records `specification = "ruro_occ_M0"`. Output
folders use `outputs/{estimates,post_estimation}/fr/spec/ruro_occ/...` and
the per-run prefix `fr_2016_ruro_occ_gamspy_...`.

## Method Description For Papers

Use wording like:

```text
We estimate preferences in a Random Utility Random Opportunity (RURO)
framework. Alternatives are sampled over employment, hours, wages, and
occupation. The systematic choice index adds preference utility and additive
opportunity components, then subtracts the log proposal density exactly once.
Occupation enters the opportunity block and not the direct utility function.
```

This describes the model object without tying it to a person-specific
label.

## Safe Havens (personal name preserved by design)

Three locations intentionally retain references to the original R reference
author for legitimate citation reasons:

1. `stijn/` — original R notebooks (`*.Rmd`, `*.R`, `.Rhistory`). The YAML
   `author:` fields are academic-citation metadata and are kept verbatim.
2. `docs/archive/` — sealed historical snapshot. Frozen on purpose; do not
   rewrite.
3. `docs/ACKNOWLEDGEMENTS.md` — the single centralised personal
   acknowledgement.

Everywhere else in the active tree, the rename to neutral RURO terminology
is final. New files should not reintroduce personal labels.

## Rename History

A one-shot sweep was performed by
`scripts/maintenance/rename_stijn_to_ruro.py` on 2026-05-20. The script
walks the tree (excluding the three safe havens above plus build caches),
applies prose + identifier replacement maps, and uses `git mv` for path
renames. A defensive citation guard refuses to mutate any line containing
the literal author's full name. Manifests are written to
`Results/rename_stijn_to_ruro_manifest_<UTC>.csv` per invocation. The
script is self-protective: its own source file is in the safe-haven set so
re-runs cannot collapse its replacement maps into identities.

## Out Of Scope (separate manual step)

The EUROMOD shared-storage scenarios directory

```text
Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/scenarios/
```

is outside the repo and has **not** been renamed. It can be `Rename-Item`'d
to `.../ruro_occ/scenarios/` whenever shared-storage hygiene is convenient;
the references in the two affected docs
(`docs/RURO_ruro_occ_M0_rebuild_command_plan_v1.md` and
`Results/RURO_ruro_occ_M0_full_rebuild_report_v1.md`) deliberately preserve
the original Z: path until that storage-side rename happens.
