# France_case/job_model/ — ARCHIVED TRACK

**Status: ARCHIVED.** This track defined a discrete-choice job opportunity as a combination of (occupation, hours, wage). It was replaced by the **P3a** and **NC pilot** tracks, which use different opportunity-set constructions (continuous opportunity draws + occupation opportunity layer for P3a; product-of-marginals couples draws for NC).

The track folder is preserved here for reference — the work, decisions, and acceptance tests are still readable. The files are **not moved to docs/archive/** because they document a coherent track whose code (`scripts/enhanced/enh_job_universe.py`, `enh_job_draws.py`, etc.) may still exist.

## Files

- `README_job_model.md` — original branch description (job universe construction, draws generation, EUROMOD run, modes, parameters)
- `ACCEPTANCE_TESTS.md` — acceptance tests for the job-model pipeline
- `Commands_job.txt` — command examples

## When was this archived as a track?

Last validated run: 2026-02-04 (FR 2016, full grid with ISCO0, 199 simulated draws).

Track replaced by **continuous-RURO with occupation opportunity** (P3a / NC) during the redesign documented in `_shared/governance/RURO_spec_redesign_decisions_v2.md`.

## See also

- [`../P3a/README.md`](../P3a/README.md) — active 3-year stacked track that replaced this one
- [`../NC_pilot/README.md`](../NC_pilot/README.md) — active couples-product track
- [`../_shared/governance/RURO_spec_redesign_decisions_v2.md`](../_shared/governance/RURO_spec_redesign_decisions_v2.md) — the spec redesign that led to retiring this approach
