# FR P2a Region-Live — Phase-4 Remediation Report — v3

Date: 2026-07-29. Applies the residual fixes of
`FR_P2a_region_live_phase4_code_review_v3.md` §17–§18 (verdict APPROVE AFTER
FIXES): failed-authentication diagnostic preservation, the two
authentication-failure finalization tests, the explicit evidence label, and
rebinding of the approval gate to Phase-4 review v4. No real gradient or
Hessian; no optimizer; theta untouched; no Phase 5+; dclaborsupply-monorepo and
the accepted Phase-3 bundle unmodified; nothing committed.

## 1. Remediation-v3 verdict

**READY FOR PHASE-4 REVIEW V4.** The single review-v3 defect is closed: when a
post-evaluation authentication check stops the attempt (runtime-map fingerprint
mismatch or input-hash recheck failure), the STOPPED manifest now retains the
complete live diagnostic record — gradient, symmetry, full spectrum, loading
shares, design rank, regional subblock and Schur evidence — under an explicit
`diagnostic_evidence_status: FAILED_AUTHENTICATION_ATTEMPT` label, with
true/true derivative flags and the exact stop code/gate. Suite: **54 passed**;
both new tests pass in five consecutive repetitions; `git diff --check` exit 0;
canonical dry-run awaits `PHASE4_REVIEW_V4` approval with all evaluation flags
false; Phase-3 bundle byte-identical.

## 2. Review-v3 defect addressed

§17 (Medium): `_phase4_merge_progress` suppressed `partial_diagnostics`
whenever `gates4` existed, so an S-8 stop after complete diagnostics but
before artifact staging (fingerprint or input recheck) discarded the in-memory
evidence. Fixed per §18.1–.4; persistence is no longer inferred from the gate
summary.

## 3. Files inspected

Read in full: code review v3, remediation report v2, the Phase-3 manager
acceptance, the runner, the config, the safety tests, and the complete current
Git diff (HEAD `c7d558a36489520a0f8487abf939d5300deaffb1`; nested HEAD =
gitlink `27756a06ea189339aa82915ed2124628afed20eb`, clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (cumulative uncommitted
   +952/−17): staging-aware partial merge, evidence-status label, review-v4
   rebinding.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+43/−5): comment-only
   v3→v4 corrections; no threshold or anchor change.
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+729/−3): tests 53–54
   added; test 42/52 rebound to v4; all 52 prior tests retained.

Created: this report. Implementation report v1, reviews v1–v3, and remediation
reports v1–v2 are preserved unchanged. The real review-v4 file was NOT created.

## 5. Live diagnostic lifecycle

One live `diag` dict is built incrementally by `_phase4_diagnose` and exposed
by reference as `progress["partial_diagnostics"]` from the first line of the
diagnostic route. `_phase4_run_diagnostics` now tracks `artifacts_staged`,
set true only after `_phase4_write_artifacts` returns. On ANY StopRun, the
handler attaches the live record whenever the artifacts were **not** staged —
explicitly independent of whether `gates4` was already recorded — together
with `exception: {type, message, code, gate}` and the merged derivative-
progress flags. Once artifacts are staged, the full record already persists in
`phase4_diagnostics.json` inside the preserved attempt directory, so no
duplication occurs.

## 6. Runtime-map fingerprint failure

Test 53: clean fake diagnostics complete (gradient + Hessian + full battery),
then the post-evaluation fingerprint check fails. Finalized STOPPED manifest:
stop `S-8` / gate `runtime-map`; `gradient_evaluated: true`,
`hessian_evaluated: true`; `diagnostic_evidence_status:
FAILED_AUTHENTICATION_ATTEMPT`; retained record includes the 37-element
gradient, passing symmetry, the full 37-eigenvalue spectrum, design rank 10,
Schur rank 10, and the full gate summary; `complete/` absent, `_STOPPED`
attempt preserved, staging empty, lock released.

## 7. Input-hash recheck failure

Test 54: a real temporary authenticated input is tampered after its
authentication record is fixed; the fingerprint passes (paths unchanged) and
the post-evaluation recheck raises `S-8` / `input-recheck` after recording
pre/post/accepted hashes. Finalized STOPPED manifest: true/true flags; the
`input_recheck_after_evaluation` table retains the pre hash, the differing
post hash and `ok: false`; the full pre-recheck diagnostic record is retained
under the FAILED_AUTHENTICATION_ATTEMPT label; `complete/` absent, separate
`_STOPPED` attempt, staging empty, lock released.

## 8. Failed-authentication evidence label

`_phase4_evidence_status(gate)` returns the fixed value
`FAILED_AUTHENTICATION_ATTEMPT` for the `runtime-map` and `input-recheck`
gates and `STOPPED_ATTEMPT_PARTIAL_EVIDENCE` for all other exceptional
retention; `_phase4_merge_progress` persists it as
`diagnostic_evidence_status` alongside every attached record. Retained
evidence therefore can never be mistaken for a successful published Phase-4
result; successful-result artifacts and `complete/` publication rules are
unchanged.

## 9. Exceptional finalization

Every controlled Phase-4 exception path — inside the diagnostic body and in
the outer contract-phase/unexpected handlers — merges the live progress state,
attaches the labelled evidence when artifacts were not staged, persists
exception type/message and exact stop code/gate, finalizes under
`attempts/<attempt>_STOPPED/`, never publishes `complete/`, and releases the
lock. The exact successful artifact-set requirement is untouched.

## 10. Phase-4 review-v4 binding

`CANONICAL_APPROVED_PHASE4_REVIEW_REL` now points to
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v4.md`; CLI help,
YAML comments, the manifest labels (`AWAITING_PHASE4_REVIEW_V4_APPROVE` /
`PHASE4_REVIEW_V4_APPROVED`), the module header, and the tests are updated
consistently. Test 52 proves: the synthetic exact review-v4 APPROVE passes
structurally; the v1, v2 AND v3 paths are rejected; the Phase-3 review-v6 is
rejected with its dedicated message; and the REAL review-v3 body (APPROVE
AFTER FIXES) copied to the v4 path is rejected by the verdict parser. The
real review-v4 file does not exist and was not created.

## 11. Numerical-logic preservation

Unchanged: accepted bundle hash `2cf23764…`; accepted theta; 37-free/10-pin
map; the ten regional names; gradient/Hessian construction; symmetry 1e-8;
rank 1e-10; strict PD gates; condition 1e7/1e10 tiers; the solve-based Schur
formula; the warning-only loading-share interpretation. The diagnostic
routines themselves were not touched — only the retention of their output on
exceptional paths.

## 12. Transaction preservation

Untouched: `phase4_curvature_v1/` root, lock/staging/attempts/immutable
`complete/`, exact seven-artifact + manifest-last bundle without self-hash,
atomic publication, overwrite refusal, and the shared transaction's Phase-3
default. Phase-3/Phase-4 transaction batteries pass unchanged.

## 13. Test additions

Tests 53–54 (suite 52 → **54**) drive both authentication failures through the
production `_phase4_run_diagnostics` finalization with fake derivatives only,
asserting status, exact stop code/gate, true/true flags, the retained labelled
evidence (including Schur), the pre/post hash table, no `complete/`, preserved
separate attempts, empty staging, and released locks. Tests 42 and 52 were
rebound to v4 (with the v3 path added to the rejected set and the real
review-v3 body rejection). No test calls the real gradient or Hessian; all 52
prior tests are retained and passing.

## 14. Full no-Hessian suite

`pytest -q` → **54 passed** (~27 s), twice. `py_compile` clean; YAML parses;
`git diff --check` exit 0 (after trimming one EOF blank line the checker
caught).

## 15. Repeated authentication-failure tests

Tests 53+54 executed in five consecutive fresh pytest runs: exit codes
`0,0,0,0,0` (2 passed each run).

## 16. Phase-4 dry-run

Canonical `--phase 4` without `--execute-phase4`: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`; `gradient_evaluated: false`,
`hessian_evaluated: false`, `optimizer_called: false`,
`execution_ready: false`, `review_gate: AWAITING_PHASE4_REVIEW_V4_APPROVE`;
`complete/` absent, lock absent, staging empty. Phase 5 refused (exit 2).

## 17. Phase-3 bundle regression

All accepted `complete/` artifact hashes equal the Phase-3 manifest record;
the deterministic bundle digest recomputes to
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`; the
manifest hash is unchanged (`60eb1412…`). Nested repository clean at
`27756a0…`; no notebook, package, theta, estimate, or accepted evidence
changed (tracked diff remains the three authorized files).

## 18. Prohibited-operation audit

No real gradient/Hessian (fake matrices only; dry-run flags false), no
optimizer, no theta change, no Phase 5+ (refused), no
inference/post-estimation/welfare/synthetic recovery/EUROMOD/notebooks, no
dclaborsupply-monorepo edit, no prior report altered, nothing committed.
Writes: preserved attempt evidence and this report.

## 19. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +43/−5
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +952/−17  (cumulative)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +729/−3   (cumulative)
 ?? docs/…/phase4_code_review_{v1,v2,v3}.md (reviewer records)
 ?? docs/…/phase4_{implementation,remediation_v1,remediation_v2,remediation_v3} reports
 ?? outputs/…/attempts/… (preserved dry-run/test evidence)
```

`git diff --check` exit 0; index clean; HEAD `c7d558a` untouched.

## 20. Residual warnings

- A STOPPED manifest carrying the full labelled record grows by roughly the
  size of `phase4_diagnostics.json` (tens of KB) — accepted as the cost of
  complete failed-authentication evidence.
- On the rare exceptional path where artifacts WERE already staged, the
  manifest omits `partial_diagnostics` because the identical full record
  persists as the staged `phase4_diagnostics.json` inside the preserved
  attempt directory; reviewers should confirm this is the intended reading of
  "before phase4_diagnostics.json has been staged".
- The gates4 summary remains in the manifest alongside the attached record on
  authentication failures (slight duplication, deliberate: neither is inferred
  from the other).

## 21. Whether review v4 may begin

**YES.** The review-v3 defect is closed with deterministic finalization
evidence on both named paths, the gate is bound to the not-yet-existing
review v4, and the exact uncommitted state is ready for the narrow fourth
independent no-Hessian review.

## 22. Immediate next action

Independent Phase-4 review v4 of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict` at the
canonical v4 path: commit the reviewed state cleanly, then execute the single
real Phase-4 run via `--phase 4 --execute-phase4 --expected-mnl-head
<post-commit SHA> --expected-dclaborsupply-head 27756a0…
--approved-phase4-review …phase4_code_review_v4.md
--approved-phase4-review-sha256 <committed hash>`. Do not run
`--execute-phase4` before then.

**FINAL VERDICT: READY FOR PHASE-4 REVIEW V4** (no real derivatives; nothing
committed).
