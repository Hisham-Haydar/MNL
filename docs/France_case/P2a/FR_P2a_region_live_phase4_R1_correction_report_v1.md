# FR P2a Region-Live — Phase-4 R-1 Correction Report — v1

Date: 2026-07-29. Corrects only the false-failure R-1 design source identified
by the accepted audit (`FR_P2a_region_live_phase4_R1_design_audit_v1.md`,
verdict CURRENT_R1_FALSE_FAILURE). No Hessian/gradient/theta/threshold/
transaction change; Phase 4 not rerun; the preserved first STOPPED attempt
untouched; nothing committed.

## 1. Correction verdict

**READY FOR PHASE-4 REVIEW V7.** R-1 now ranks the exact production loader
arrays that enter the JAX likelihood — extracted directly from the
already-loaded likelihood data objects and reduced at the loader's own group
boundaries — never the frozen stem's stored, identically-zero `reg2..reg8`
placeholders. The rank tolerance and the rank == 10 requirement are unchanged.
Suite: **57 passed** (twice); the new false-failure regression passes **10/10**
consecutive runs; the canonical dry-run reports the corrected design
diagnostics without evaluating any derivative; the first STOPPED attempt is
byte-identical; `git diff --check` exit 0.

## 2. Accepted audit finding

The stopped first real Phase-4 attempt failed R-1 with rank 3 because the gate
ranked the stem's STORED `reg2..reg8` columns — all-zero region-dead legacy
placeholders the likelihood never reads. The production loader derives its
`reg2..reg8` as `1{drgn1 == k}` (no `reg_nuts1_*` columns exist in the stem),
giving the true likelihood design: 1,555 × 10, rank 10 under the unchanged
tolerance, consistent with the attempt's own PD subblock and full-rank Schur
evidence.

## 3. Files inspected

Read in full: the R1 design audit, Phase-4 code review v6, the Phase-3 manager
acceptance, the runner, the config, the safety tests, the frozen stem (schema
and audited columns), the production singles loader (`_region_dummies`
fallback rule), the preserved STOPPED attempt, and the current Git diff (HEAD
`09531651313367954b5a016200ff563d26fde383`; nested HEAD = gitlink
`27756a06ea189339aa82915ed2124628afed20eb`, clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (+84/−31 vs the committed v6
   checkpoint): `_phase4_regional_design` helper, contract rewiring,
   diagnostics fields, one added Phase-3-contract return key, review-v7
   rebinding.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+8/−4): design-source
   declaration + comment corrections; no threshold change.
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+106/−8): test 57 added,
   test 42 strengthened, review battery rebound.

Created: this report. The audit, all prior reports/reviews, the stem, and the
STOPPED attempt are unmodified. The real review-v7 file was NOT created.

## 5. Old R-1 design source

`_phase4_contract` previously read `gsur, reg2..reg8, drgur, drgmd` directly
from the authenticated frozen stem and reduced per household — ranking the
dead stored columns (rank 3). That construction is fully removed; test 57
asserts by source guard that `_phase4_contract` no longer touches
`frozen_stem_parquet` for the design.

## 6. Corrected R-1 design source

`_phase3_contract` now also returns the two production loader data objects
(`loader_data = (dm, df_)`) — the exact objects from which the JAX objective
is built; returning them changes no Phase-3 behavior (nothing else consumes
the key; the full Phase-3 battery passes unchanged). The new
`_phase4_regional_design(dm, dfem)` extracts the canonical ordered ten
attributes (`gsur, reg2..reg8, drgur, drgmd`) directly from those objects —
no loader fallback logic is duplicated anywhere.

## 7. Loader-array binding

Before rank is computed the contract requires: exactly 1,555 households;
exactly ten columns in canonical order; loader `group_ids` unique and equal in
count to the loader groups; every design array finite; every design array
constant within each 101-alternative household block (checked per block on the
loader's own `group_starts..group_ends`). The binding record
(`design_loader_binding`) is persisted with the diagnostics; any violation is
an S-5 stop before R-1.

## 8. Household reduction

One row per household is taken at the loader's own `group_starts` (never an
arbitrary alternative row; constancy is proven first), male and female blocks
stacked and deterministically ordered by loader `group_ids`. Test 57 proves
the helper's output is exactly array-equal to this reduction recomputed
independently from the loader objects.

## 9. Parameter-to-column mapping

The ten design columns are position-matched to the ten regional parameters and
persisted (`design_column_to_parameter`): `gsur → beta_E_gsur`,
`reg2..reg8 → beta_E_drgn2..beta_E_drgn8`, `drgur → beta_E_drgur`,
`drgmd → beta_E_drgmd`. The regional names remain derived from the accepted
specification and forced equal to the plan/YAML lists (unchanged).

## 10. R-1 rank gate

Unchanged: numerical rank under `1e-10 × largest singular value` must equal
**10**. Nothing was weakened or reinterpreted; only the input matrix now is
the likelihood's actual design. The manifest additionally records
`regional_design_source: production_likelihood_loader_arrays` (declared in
YAML and asserted equal by `_validate_phase4_constants`) and the diagnostics
carry the same field.

## 11. False-failure regression test

Test 57 (frozen stem + production loader, no derivatives): (1) the stored stem
`reg2..reg8` are identically zero; (2) the old stored-column construction has
rank 3 and fails the gate; (3) the loader matrix has rank 10; (4/5) the
corrected helper's matrix is exactly array-equal to the loader arrays reduced
at the loader group boundaries, and equals the `1{drgn1 == k}` derivation
column-by-column; (6) the corrected gate passes; (7) substituting the dead
stored-column matrix fails; (8) no gradient or Hessian is evaluated. A source
guard additionally fails the test if `_phase4_contract` ever reads the stem
for the design again or drops `_phase4_regional_design`/`loader_data`.

## 12. Dry-run behavior

The canonical dry-run (exit 0, no derivative evaluation) now reports:
`regional_design_source: production_likelihood_loader_arrays`;
`design_shape: [1555, 10]`; the canonical ten column names; the
column-to-parameter mapping; and the structural binding record (constancy,
finiteness, 1,555 unique households/groups) — verified live and asserted in
the subprocess test 42. No rank value is claimed during dry-run (unchanged
discipline: spectral results belong to the real run).

## 13. Review-v7 binding

`CANONICAL_APPROVED_PHASE4_REVIEW_REL` now points to
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v7.md`; CLI help,
YAML comments, module header and manifest labels
(`AWAITING_PHASE4_REVIEW_V7_APPROVE` / `PHASE4_REVIEW_V7_APPROVED`) are
updated; the dry-run reports `AWAITING_PHASE4_REVIEW_V7_APPROVE` (verified
live). Test 52 rejects the Phase-4 v1–v6 paths and the separate Phase-3
review-v6, rejects the real conditional review-v5 body at the canonical path,
refuses a wrong hash for the real review-v6 body, and passes a synthetic exact
v7 APPROVE. The real review-v7 file was not created.

## 14. Numerical-logic preservation

Unchanged: accepted Phase-3 bundle hash `2cf23764…`; accepted theta;
37-free/10-pin map; the ten regional parameter names; gradient/Hessian
construction; symmetry 1e-8; Hessian rank tolerance 1e-10; condition
1e7/1e10 tiers; PD gates; raw regional-subblock gate; Schur formula and
gates; loading-share warning. Only the R-1 input matrix source changed.

## 15. Transaction preservation

Untouched: artifact set, lock/staging/attempts/immutable `complete/`,
manifest-last + no-self-hash, atomic publication, exceptional-finalization and
evidence policies. The transaction batteries (14–16, 31–32, 41, 47, 50–51,
55–56) pass unchanged.

## 16. Test-suite result

`pytest -q` → **57 passed** (~27 s), twice. `py_compile` clean; YAML parses;
`git diff --check` exit 0 (after trimming one EOF blank line).

## 17. Repeated R-1 test

Test 57: **10/10** consecutive fresh pytest runs, exit codes all 0.

## 18. Phase-3 bundle regression

All accepted `complete/` artifact hashes equal the Phase-3 manifest record and
the deterministic bundle digest recomputes to `2cf23764…`. Nested repository
clean at `27756a0…`.

## 19. Preserved STOPPED-attempt regression

Every file of
`attempts/20260729T121430Z_322592_6a8a24821914433f9f4303f2a6459025_curvature_STOPPED`
was SHA-256-hashed before and after the full validation battery:
**byte-identical**. The false-failure evidence is preserved untouched.

## 20. Prohibited-operation audit

No real gradient/Hessian evaluated (dry-run flags false; tests use the loader
data and fake matrices only), no optimizer, no theta change, no stem change,
no Phase 4 rerun, no Phase 5+ (refused, exit 2), no
inference/post-estimation/welfare/EUROMOD/synthetic recovery/notebooks, no
dclaborsupply-monorepo edit, nothing committed. Writes: dry-run attempt
evidence and this report.

## 21. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |   +8/−4
 M scripts/p2a/run_p2a_regionlive_rebuild.py          |  +84/−31
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +106/−8
 ?? docs/…/phase4_R1_design_audit_v1.md (accepted audit, this round's input)
 ?? docs/…/phase4_R1_correction_report_v1.md (this report)
 ?? outputs/…/phase4_R1_design_audit_v1/ (audit evidence)
 ?? outputs/…/attempts/… (preserved STOPPED + dry-run evidence)
```

`git diff --check` exit 0; HEAD `0953165` untouched.

## 22. Residual warnings

- The audit report/evidence and the preserved real-run attempt bundles remain
  untracked; they should be committed together with this correction at the
  review-v7 checkpoint.
- A structurally valid APPROVE body copied to the canonical v7 path would pass
  the parser — as with every prior round, content provenance is bound by the
  operator-supplied SHA-256 of the genuine review (documented in test 52).
- The YAML `regional_design_columns` names are unchanged (`reg2..reg8`) but
  now explicitly denote loader-array attributes, not stem columns; the comment
  and the new `regional_design_source` declaration make this unambiguous.

## 23. Whether review v7 may begin

**YES.** The single audited defect is corrected at its source, deterministically
regression-protected against reintroduction, and validated end-to-end in the
non-evaluating dry-run; all accepted numerical and transactional logic is
preserved bit-for-bit.

## 24. Immediate next action

Independent Phase-4 review v7 of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict` at the
canonical v7 path: commit the corrected state (including the audit evidence
and preserved attempts), then rerun the single real Phase-4 via
`--phase 4 --execute-phase4 --expected-mnl-head <post-commit SHA>
--expected-dclaborsupply-head 27756a0… --approved-phase4-review
…phase4_code_review_v7.md --approved-phase4-review-sha256 <committed hash>`.
Do not run `--execute-phase4` before then.

**FINAL VERDICT: READY FOR PHASE-4 REVIEW V7** (no real derivatives; nothing
committed).
