# France case — EUROMOD 2015–2017

Empirical application of the RUM/RURO package to French EUROMOD data (years 2015, 2016, 2017 stacked). Raw data and EUROMOD systems live in `U:\EUROMOD-STORAGE\` and are out of repo.

## Layout

- [euromod_reference/](euromod_reference/) — FR EUROMOD input/output variable indices, 2015 reference tables, DRD exports.
- [notes/](notes/) — France-specific notes (EUROMOD FR system, R-reference vs Python specification).
- [canary_reports/](canary_reports/) — France canary / rebuild diagnostic reports.
- [job_choice/](job_choice/) — France job-choice model docs (README, acceptance tests, commands).
- [results/](results/) — France results pointers (KEEP_RESULTS marker).
- [jmp/](jmp/) — France-specific JMP memos (decisions tied to FR data/years/EUROMOD-FR).
- [execution_logs/](execution_logs/) — dated run/phase logs (NC_pilot, Bpool, GSURv2, occ_M0a/b/c, occ_M1, pooled_P3a, stage_M1).
- [consolidated/](consolidated/) — merged canonical docs for chains that were previously split across decision/report/completion memos.
- [cleanup/](cleanup/) — cleanup manifests for docs reorganization passes.

## Cleanup history

- 2026-05-25 — initial split of general vs France material; topical package layout introduced at `docs/` root. See [cleanup/MOVE_MANIFEST_2026-05-25.md](cleanup/MOVE_MANIFEST_2026-05-25.md).
