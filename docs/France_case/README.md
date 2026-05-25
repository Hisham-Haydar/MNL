# France case — EUROMOD 2015–2017

Empirical application of the RUM/RURO package to French EUROMOD data. Raw data and EUROMOD systems live in `U:\EUROMOD-STORAGE\` and are out of repo.

## Tracks

Three estimation tracks plus a shared subtree for cross-track material.

| Track | Status | What it is |
|---|---|---|
| [`P3a/`](P3a/) | **Active baseline** | 3-year stacked 2015-2016-2017. Continuous-RURO with occupation opportunity; the current main estimation effort. Includes single-year M0→M1 ladder as precursor + multi-year stage M1 + GSURv2 + pooled estimation. |
| [`NC_pilot/`](NC_pilot/) | **Active** | Couples 30×30=900 alternatives pilot. Product-of-marginals choice set for couples; both partners as deciders. Concurrent with P3a per spec redesign v2 §D-SCOPE. |
| [`job_model/`](job_model/) | **Archived** | Discrete (occupation, hours, wage) combination approach. Replaced by P3a + NC pilot. Track folder preserved for reference. |
| [`_shared/`](_shared/) | n/a | Cross-track material: EUROMOD reference, GSUR data product, France data audits, governance decisions, notes, results pointer. |

## Cleanup machinery

- [`cleanup/MOVE_MANIFEST_2026-05-25.md`](cleanup/MOVE_MANIFEST_2026-05-25.md) — Round 1: initial split of general vs France material; topical package layout at `docs/` root.
- [`cleanup/MOVE_MANIFEST_2026-05-26_round2.md`](cleanup/MOVE_MANIFEST_2026-05-26_round2.md) — Round 2: chain compression (24 files archived).
- [`cleanup/MOVE_MANIFEST_2026-05-27_round3.md`](cleanup/MOVE_MANIFEST_2026-05-27_round3.md) — Round 3: track-based France_case restructure (this pass).
