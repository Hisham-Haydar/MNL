# France_case/_shared/

Cross-track France material — files that document the **France data** or **cross-track governance decisions**, not any single estimation track.

## Subfolders

- **`euromod_reference/`** — EUROMOD-FR input/output variable definitions, system documentation. Index of EUROMOD reference data files (.md, .csv, .jsonl, .txt).
- **`gsur/`** — Group-Specific Unemployment Rate (GSUR) data product. Audits, rebuild specifications, external acquisition consolidation. Currently consumed by P3a (GSURv2 build); the data product itself is reusable across tracks.
- **`data_audits/`** — France data evidence and audit trails: continuous data build audit, data audit + addendum, sample funnel, GSUR-year support patch.
- **`notes/`** — EUROMOD system notes for France 2015, R-reference vs Python specification comparison.
- **`results/`** — Pointer to Results/ directory (KEEP_RESULTS.md).
- **`governance/`** — Cross-track spec and methodology decisions: spec redesign v2 (governs both NC and P3a per its own §D-SCOPE), GSUR year alignment, CPI/HICP source decision.

## Track consumers

| Subfolder | Currently consumed by |
|---|---|
| euromod_reference/ | all tracks |
| gsur/ | P3a (GSURv2 build); reusable for any future track |
| data_audits/ | P3a, NC_pilot (both depend on FR continuous data) |
| notes/ | all tracks |
| governance/ | NC_pilot + P3a (per spec redesign v2 §D-SCOPE) |

## Sibling tracks

- [`../P3a/`](../P3a/) — active 3-year stacked 2015/2016/2017 estimation
- [`../NC_pilot/`](../NC_pilot/) — active couples 30×30=900 alternatives pilot
- [`../job_model/`](../job_model/) — archived discrete (occupation, hours, wage) combination approach
