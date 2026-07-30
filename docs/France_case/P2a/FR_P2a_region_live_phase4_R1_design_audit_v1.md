# FR P2a Region-Live — Phase-4 R-1 Design Audit — v1

Date: 2026-07-29. Read-only diagnosis of the failed R-1 regional-design rank
gate from the first real Phase-4 attempt
(`20260729T121430Z_322592_6a8a24821914433f9f4303f2a6459025_curvature_STOPPED`).
No production file modified; Phase 4 not rerun; no gradient/Hessian/optimizer;
nothing committed. Writes confined to
`outputs/…/region_live_v1/phase4_R1_design_audit_v1/` and this document.

## 1. Audit verdict

**CURRENT_R1_FALSE_FAILURE.** R-1 was computed from the frozen stem's STORED
`reg2..reg8` columns, which are identically zero for all 1,555 households —
region-dead legacy placeholders that the likelihood never reads. The design
that actually enters the likelihood (loader-derived `drgn1` dummies) has full
rank 10 under the unchanged tolerance. The regional block is identified — the
observed rank 3 is a false failure of the audit input, not of the model.

## 2. Scope

Determine whether R-1 tested the same regional design arrays that enter the
likelihood, by constructing (A) the current Phase-4 stored-column matrix
exactly as the production code reads it, (B) the loader-equivalent matrix
derived from the authoritative stem variables, and (C) the actual
likelihood-loader matrix, then comparing supports, equality, and numerical
ranks under the unchanged `1e-10 × max singular value` tolerance.

## 3. Stopped Phase-4 evidence

The STOPPED attempt (S-5/G-9) recorded: full free-Hessian rank 37 with minimum
eigenvalue 0.1037326963880782 and condition number 405,353.9 (clean tier); raw
regional subblock PD (min eig 3.3787399166319405); Schur rank 10 with minimum
eigenvalue 2.255741652065068; **R-1 design rank 3** with singular values
(2.897e+01, 1.820e+01, 2.356e+00) followed by seven values ≤ 1.25e-15 —
i.e. exactly three genuinely nonzero columns. Every curvature and
Schur-information gate already said the ten regional directions carry strictly
positive conditional information; only the design gate contradicted them.

## 4. Current R-1 construction

`_phase4_contract` reads columns `gsur, reg2, reg3, reg4, reg5, reg6, reg7,
reg8, drgur, drgmd` directly from the authenticated frozen stem, verifies
household-constancy, and reduces to one row per `idhh` (sorted). Those stored
`reg*` columns are what R-1 ranked.

## 5. Likelihood-loader construction

The dclaborsupply singles loader (`_region_dummies`, loader.py) builds
`reg2..reg8` from `reg_nuts1_2..8` columns ONLY if all seven are present;
otherwise it derives them as `1{drgn1 == k}` from the authoritative `drgn1`
column. The frozen stem contains **no** `reg_nuts1_*` columns, so the JAX
likelihood consumes `drgn1`-derived dummies and never touches the stem's
stored `reg2..reg8`. `gsur`, `drgur`, `drgmd` are read directly by name (and
are identical in both constructions).

## 6. Stored-column matrix

A is 1,555 × 10, household-constant, sorted by `idhh`. Nonzero counts:
`gsur` 1,555; `reg2..reg8` **0 each** (identically zero); `drgur` 832;
`drgmd` 328. Numerical rank **3**; singular values match the stopped attempt
to full precision.

## 7. drgn1-derived matrix

B is 1,555 × 10 over the same sorted households: `gsur`, seven `1{drgn1 == k}`
dummies (k = 2..8), `drgur`, `drgmd`. All eight regions are populated (§11),
every dummy has positive support. Numerical rank **10**.

## 8. Actual loader matrix

C was produced by running the male (714 households) and female (841) stem
frames through the production `load_singles` with the certified specification
and stem metadata, extracting `d.gsur, d.reg2..d.reg8, d.drgur, d.drgmd`,
verifying within-group constancy across every 101-alternative block, reducing
at the loader `group_starts`, and sorting by the loader `group_ids`.
C is 1,555 × 10 with numerical rank **10**.

## 9. Matrix equality results

Households and ordering agree across all three matrices
(`ids_A == ids_B == ids_C`, 1,555 each). **B equals C exactly**
(`np.array_equal` true) — the drgn1-derived construction is bit-identical to
what the likelihood consumes. A agrees with B exactly on `gsur`, `drgur`,
`drgmd` and disagrees on all seven `reg*` columns (max abs diff 1.0 each):
A's are zero, B's are the true dummies.

## 10. Column support

Per-column dtype/min/max/mean/std/unique/nonzero for A, B and C are in
`phase4_R1_column_summary.csv`. A's seven `reg*` columns are float64 constant
zero (1 unique value, 0 nonzero); the 10×10 exact-equality matrices
(`phase4_R1_exact_equality_matrix.csv`) show A's seven `reg*` columns mutually
identical (all-zero) — the 21 duplicate pairs plus 7 zero columns that
collapse A's rank to 3.

## 11. Region support

Household counts by `drgn1`: region 1: 245; 2: 254; 3: 122; 4: 135; 5: 279;
6: 175; 7: 182; 8: 163 — all eight NUTS-1 macro-regions present with
substantial support (minimum 122).

## 12. Urbanisation support

`phase4_R1_region_urbanisation_crosstab.csv` tabulates `drgur`, `drgmd`,
`drgru` and the residual (neither) counts by region: 832 urban, 328
mid-density households overall, distributed across all eight regions — no
region is urbanisation-degenerate.

## 13. Rank decomposition

Under the unchanged tolerance `1e-10 × max singular value`
(`phase4_R1_rank_comparison.json`):

| matrix | rank |
|---|---|
| A stored columns (current R-1 input) | **3** |
| A region columns only | 0 |
| B drgn1-derived (loader-equivalent) | **10** |
| C actual likelihood loader | **10** |
| region dummies only (from drgn1) | 7 |
| region dummies + urbanisation | 9 |
| full ten-column authoritative design | **10** |

The rank requirement was not altered during this audit.

## 14. Exact linear dependencies

In A: `reg2 = reg3 = … = reg8 = 0` identically — seven trivial zero-column
dependencies (and hence all 21 pairwise equalities among them). No other
dependency exists: `gsur`, `drgur`, `drgmd` are mutually independent (rank 3).
B/C have no dependencies (rank 10 of 10).

## 15. Whether R-1 tested the likelihood design

**No.** R-1 ranked the stem's stored `reg2..reg8` — dead placeholder columns
carried through from the region-dead frame lineage and byte-frozen by the
reconciliation contract — while the likelihood derives its region dummies from
`drgn1` inside the loader. The arrays R-1 tested never enter the estimation.

## 16. Scientific interpretation

The estimate's regional identification evidence is internally consistent once
the wrong input is recognized: the full 37×37 Hessian is PD with rank 37 and a
clean condition number; the raw 10×10 regional subblock is PD (min eig 3.38);
the conditional Schur complement has rank 10 with strictly positive minimum
eigenvalue 2.26 — all computed from derivatives of the actual likelihood,
whose design (B = C) has full rank 10. The three-tier evidence R-2/R-4 already
demonstrated local regional identification; the R-1 result was an artefact of
auditing dead columns. Nothing suggests a true rank deficiency.

## 17. Whether a code correction is required

**Yes — one narrow correction, not made in this audit.** Phase-4's R-1 design
construction must source the seven region dummies the way the likelihood does
(derive `1{drgn1 == k}` from the authenticated stem's `drgn1`, or read the
loader outputs), instead of the stem's stored `reg2..reg8`. The design-column
list in the immutable constants/YAML (`reg2..reg8` as stored names) must be
recharacterized accordingly. No threshold, tolerance, or gate logic should
change. The correction requires its own remediation round and independent
Phase-4 review before any rerun, per the established gate discipline.

## 18. Whether Phase 4 may be rerun

**Not yet.** The STOPPED attempt is preserved evidence; the current committed
implementation would deterministically fail R-1 again on the same dead
columns. Rerun only after: (a) the R-1 source correction is implemented and
validated no-Hessian; (b) the next independent Phase-4 review returns exact
APPROVE at the then-canonical review path; (c) the corrected state is
committed cleanly and the new expected HEAD/review hash are supplied to the
execution CLI.

## 19. Files created

Under `outputs/p2a_singles2016/region_live_v1/phase4_R1_design_audit_v1/`:
`phase4_R1_column_summary.csv` (30 rows: A/B/C × 10 columns),
`phase4_R1_rank_comparison.json` (checks, seven SVD/rank records, exact
dependencies, loader source rule),
`phase4_R1_exact_equality_matrix.csv` (A and B 10×10 boolean matrices),
`phase4_R1_region_urbanisation_crosstab.csv` (8 regions × urbanisation
counts). Plus this document. Nothing else was written; no production file was
modified.

## 20. Immediate next action

Manager decision on the narrow R-1 source correction (§17): authorize a
remediation that derives the R-1 design from `drgn1` exactly as the loader
does, re-validate with the no-Hessian suite plus a new deterministic test that
the R-1 matrix equals the loader construction, obtain the next independent
Phase-4 review APPROVE, commit, and only then rerun the single real Phase-4
via the documented CLI. Do not delete the STOPPED attempt.

**FINAL VERDICT: CURRENT_R1_FALSE_FAILURE**
