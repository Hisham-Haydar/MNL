# MNL — Documentation Root

This is the documentation for the RUM / RURO discrete-choice labor-supply package and its current empirical application (France 2015–2017).

## Layout

- [package/](package/) — package-level policy, scope, naming, hygiene, memory map, return guide.
- [methods/](methods/) — model methodology, country-agnostic (RUM van Soest 1995, RURO Dagsvik / Aaberge / Capeau).
- [specifications/](specifications/) — model spec contracts, dictionaries, pipeline audits.
- [estimation/](estimation/) — solver backends (GAMSPy, SciPy), inference, results registry.
- [reporting/](reporting/) — post-estimation reporting design.
- [jmp_methodology/](jmp_methodology/) — JMP-level methodology memos (welfare scaffolding, multi-year strategy, estimator architecture).
- [France_case/](France_case/) — current empirical application: France EUROMOD 2015–2017, GSUR build, execution logs, consolidated decision docs.
- [archive/](archive/) — historical material, frozen except the dated supersession subdir from any given cleanup pass.

## Project chrome (root)

- [ROADMAP.md](ROADMAP.md)
- [PIPELINE_ENTRYPOINTS.md](PIPELINE_ENTRYPOINTS.md)
- [MIRRORED_DOCUMENTS_INDEX.md](MIRRORED_DOCUMENTS_INDEX.md)
- [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)

## Most recent reorganization

2026-05-25 — split the root into topical package subfolders and consolidated France-specific material into `France_case/`. See [France_case/cleanup/MOVE_MANIFEST_2026-05-25.md](France_case/cleanup/MOVE_MANIFEST_2026-05-25.md) and [archive/2026-05-25_docs_supersession/README.md](archive/2026-05-25_docs_supersession/README.md).
