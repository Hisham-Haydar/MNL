# FR P2a Region-Live — Phase-4 Remediation Report — v1

Date: 2026-07-27. Applies the four required fixes of
`FR_P2a_region_live_phase4_code_review_v1.md` (§22, verdict APPROVE AFTER
FIXES). No real Hessian evaluated; no optimizer; theta untouched; no Phase 5+;
no SE/post-estimation/welfare/synthetic-recovery/EUROMOD/notebooks;
dclaborsupply-monorepo and the accepted Phase-3 bundle unmodified; nothing
committed.

## 1. Remediation verdict

**READY FOR PHASE-4 REVIEW V2.** The real Phase-4 path is now authorized only by
a Phase-4-specific approved review (the not-yet-existing
`FR_P2a_region_live_phase4_code_review_v2.md`; the Phase-3 review-v6 is
explicitly rejected); the ineffective raw-subblock test is replaced by direct
deterministic assertions; the singular-Schur, fake-derivative orchestration and
exact gate-boundary batteries are added; and all stale phase metadata now reads
"Phases 1–4 implemented, real runs approval-gated, Phases 5–8 refused". Suite:
**49 passed**; `git diff --check` exit 0; canonical Phase-4 dry-run exit 0 with
`gradient_evaluated: false` and `hessian_evaluated: false`; Phase-3 bundle
byte-identical.

## 2. Review-v1 blockers addressed

§21.1 (High) Phase-3 review-v6 could authorize Phase 4 → fixed by the dedicated
gate (§5–§7 below). §21.2 (Medium) missing deterministic raw-PD, singular-Schur
and orchestration coverage → fixed (§8–§11). §21.3 (Low) stale phase metadata →
fixed (§12). §21.4 noted the 94-hex digest in the external review request was
malformed; this remediation uses only the valid 64-hex accepted bundle digest.

## 3. Files inspected

Read in full: the Phase-4 implementation report, code review v1, the Phase-3
manager acceptance and estimation report, manager decisions v2, production
rebuild plan v2, the runner, the config, the safety tests, and the complete
current Git diff/state (MNL HEAD `c7d558a36489520a0f8487abf939d5300deaffb1`,
nested HEAD = gitlink `27756a06ea189339aa82915ed2124628afed20eb`, nested clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (cumulative uncommitted
   +863/−15; remediation adds the Phase-4 review parser/verifier, CLI args,
   S-5-first stop ordering, `gradient_evaluated` manifest field, metadata).
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+42/−5; header and
   run-metadata corrections only — no threshold or anchor change).
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+551/−3; test_40 rewritten,
   tests 45–49 added, test_42 strengthened).

Created: this report. The implementation report and review-v1 are preserved
unchanged as immutable audit records. The real review-v2 file was NOT created.

## 5. Phase-4-specific approval gate

New `_verify_phase4_execution_gates` (called by `run_phase4` for
`--execute-phase4`; dry-runs never call it and require no review): requires
`--expected-mnl-head`/`--expected-dclaborsupply-head` (40-hex, equal to the
live HEADs), MNL gitlink == nested HEAD, full `--untracked-files=all`
cleanliness of BOTH worktrees, package-identity checks unchanged in
`_phase4_run`, and the new `--approved-phase4-review` +
`--approved-phase4-review-sha256`: the path must equal exactly
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v2.md`, the file's
SHA-256 must equal the supplied 64-hex value, and
`_parse_review_verdict_phase4` requires the exact first heading
`# 1. Phase-4 review verdict` with exactly one complete
`**FINAL VERDICT: APPROVE**` line in the first section — APPROVE AFTER FIXES,
REJECT, wrong headings and multiple verdict lines are refused. Everything runs
BEFORE any gradient or Hessian evaluation; the manifest review-gate field is now
`AWAITING_PHASE4_REVIEW_V2_APPROVE` / `PHASE4_REVIEW_V2_APPROVED`.

## 6. Phase-3 review rejection

Supplying the Phase-3 review-v6 path raises a dedicated
`phase4-review-gate` stop ("the Phase-3 review-v6 document cannot authorize
Phase-4 execution") before any other review processing; any other non-canonical
path (e.g. the Phase-4 review v1) is likewise refused. Proven by test 45 on
temporary Git repositories carrying both review files.

## 7. Commit and cleanliness gates

Unchanged in substance and now bound into the Phase-4 verifier: MNL-HEAD
mismatch, nested-HEAD mismatch, committed-gitlink mismatch, dirty MNL worktree
(untracked), and dirty nested worktree are each individually proven refused
(tests 45–46, temp repos; gitlink via `update-index --cacheinfo 160000`). The
exact review-v2 APPROVE contract passes structurally (verified on a temp repo
with a synthetic review-v2 file; the real file must not and does not exist).

## 8. Raw regional-subblock PD failure

Review-v1 found the old test's PSD construction yielded
`raw_subblock_pd_ok: true` (min eig ≈ 8.9e-16) behind a disjunctive assertion.
Replaced twice over: (a) test 40 now uses a deterministic diagonal with a
regional entry of −0.5 and asserts **directly** `raw_subblock_pd_ok is False`
and `raw_subblock_min_eig <= 0`; (b) test 47 drives the same construction
through the production `_phase4_diagnose` orchestration (fake derivative, 37×37)
and asserts the registered stop `S-5`/`G-9`, the recorded gate flags, and — via
the real transaction — that only a `_STOPPED` attempt is published and
`complete/` never appears. To make the registered R-2 stop reachable (eigenvalue
interlacing means a non-PD regional subblock always implies a non-PD full
Hessian), `_phase4_diagnose` now raises S-5/G-9 when the regional hard
conjunction fails, before the S-4 curvature stop; curvature flags remain fully
recorded either way, and pure-curvature failures still raise S-4.

## 9. Singular Schur nuisance-block failure

Test 48 case 7 builds a symmetric 37×37 fake Hessian whose nuisance block
contains an exactly singular `[[1,1],[1,1]]` sub-block; the production
solve route (`np.linalg.solve(H_NN, H_NR)`) raises `LinAlgError` and the
implementation converts it to exactly `StopRun("S-5", "schur-solve", …)` —
asserted by code AND gate name. No pinv result substitutes for the gating
solve (the informational pinv cross-check is computed only after a successful
solve), and nothing is published.

## 10. Fake-derivative orchestration tests

Test 48 exercises `_phase4_diagnose` — the production diagnostic orchestration
that runs after contract validation — with only the derivative output replaced
(fake `hess_fn`/`grad_fn` in the contract-shaped context; `jax.hessian` is
never called on the real model anywhere in the suite). All eleven wirings are
proven: (1) symmetry failure → S-4; (2) non-PD → S-4; (3) rank 36 → S-4 with
PD true; (4) condition tier failure → S-4; (5) design-rank failure → S-5/G-9;
(6) raw-subblock PD failure → S-5/G-9; (7) singular H_NN → S-5/schur-solve;
(8) Schur rank 9 and (9) Schur min eig −0.21 → S-5/G-9 with both flags false
and raw-PD true; (10) regional-dominated smallest eigenvector → warning-only
on a `PHASE_4_COMPLETE` result; (11) clean spectrum → `PHASE_4_COMPLETE`, no
warnings, all gates true.

## 11. Exact gate-boundary tests

Test 49: symmetry exactly at `1e-8·max|H|` passes and one ulp above fails;
an eigenvalue exactly at `1e-10·max` is NOT counted toward rank and one ulp
above is; condition exactly 1e7 = clean, one ulp above = warning, exactly
1e10 = warning, one ulp above = failure; PD min-eig `>0` passes while exactly
0 and negative fail.

## 12. Phase metadata corrections

Runner module header, hard-refusal block, `--phase` help, review-hash help
texts, and the YAML header + `run` block now state consistently: Phases 1–4
implemented; Phase-3/Phase-4 real execution approval-gated
(`phase3_execution_authorized: false`, new `phase4_supported: true`,
`phase4_execution_authorized: false`); Phase-4 dry-run supported and
non-evaluating; Phases 5–8 unsupported and refused
(`phases_5_to_8_supported: false`; `phases_implemented: [1, 2, 3, 4]`). No
code reads these keys (verified); no threshold or anchor changed.

## 13. Numerical logic preservation

Unchanged, byte-for-byte where applicable: accepted bundle hash `2cf23764…`;
37-free/10-pin map; accepted theta binding; the ten regional names; symmetry
1e-8; rank 1e-10; strict PD gates; condition 1e7/1e10 tiers; the Schur formula
and solve route; the loading-share warning-only interpretation. The only
behavioral change in `_phase4_diagnose` is the S-5-before-S-4 stop selection
when the regional conjunction fails (§8) — gate values and recorded flags are
identical.

## 14. Transaction preservation

Untouched: Phase-4 output root `phase4_curvature_v1/`, lock/staging/attempts/
immutable `complete/`, exact seven-artifact + manifest-last bundle with no
manifest self-hash, atomic publication, overwrite refusal, and the shared
transaction's Phase-3 default (`success_status="PHASE_3_COMPLETE"`). The
Phase-3/Phase-4 transaction batteries (tests 14–16, 31–32, 41) pass unchanged.

## 15. Test-suite result

`pytest -q` → **49 passed**, exit 0 (~25 s; runs 44 → 49 tests: test_40
rewritten, 45–49 added, 42 strengthened with `gradient_evaluated` and the new
review-gate label). `python -m py_compile` clean for runner and tests; YAML
parses; `git diff --check` exit 0 (after trimming one EOF blank line the
checker itself caught).

## 16. Phase-4 dry-run

Canonical `--phase 4` without `--execute-phase4`: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`; manifest: `gradient_evaluated: false`,
`hessian_evaluated: false`, `optimizer_called: false`,
`execution_ready: false`, `review_gate: AWAITING_PHASE4_REVIEW_V2_APPROVE`;
`complete/` absent, lock absent, staging empty; bundle bound (`2cf23764…`),
negLL(theta_hat) deviation 0.00e+00, ten regional names identified. Phase 5
refused, exit 2.

## 17. Phase-3 bundle regression

All five accepted `complete/` files re-hashed after the full suite and
dry-run: every artifact hash equals the Phase-3 manifest record; the recomputed
deterministic bundle hash equals `2cf23764…`; the manifest file's own SHA-256
is unchanged (`60eb1412…`). Certified spec/warm-start re-authenticated inside
every contract run.

## 18. Prohibited-operation audit

No real Hessian or gradient of the real model (dry-run flags + structural
branch + test 42; fake matrices only in tests); no optimizer; theta untouched;
no Phase 5+ (refused, exit 2); no SE/scores/post-estimation/welfare/synthetic
recovery/EUROMOD/notebooks; dclaborsupply-monorepo clean and unmodified; the
real Phase-4 review-v2 file was not created; nothing committed; no history
rewritten. Writes: only preserved attempt bundles under the two canonical
`attempts/` histories plus this report.

## 19. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +42/−5
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +863/−15  (cumulative)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +551/−3   (cumulative)
 ?? docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v1.md (reviewer)
 ?? docs/France_case/P2a/FR_P2a_region_live_phase4_implementation_report_v1.md
 ?? docs/France_case/P2a/FR_P2a_region_live_phase4_remediation_report_v1.md
 ?? outputs/.../phase{3,4}_…/attempts/… (44 preserved evidence files)
```

`git diff --check` exit 0; index clean; HEAD `c7d558a` untouched; nested clean
at `27756a0`.

## 20. Residual warnings

- Interlacing coupling (§8): a non-PD regional subblock always co-fails G-5;
  the S-5-first ordering makes the more specific regional stop authoritative
  while recording every curvature flag. Reviewers should confirm this ordering
  is the intended reading of plan v2 S-4/S-5.
- Condition-tier failures mathematically imply rank failures under
  `ε_rank = 1e-10·max` (min < 1e-10·max ⇔ cond > 1e10); the orchestration tests
  therefore assert each target flag rather than isolated single-gate failures.
- The first dry-run attempt of the implementation task remains a preserved
  STOPPED bundle (csv/json representational round-off, since fixed) under the
  never-delete discipline.
- Validation added dry-run attempt bundles under both canonical `attempts/`
  histories (44 untracked evidence files total, incl. prior tasks'), to be
  committed with the fix per the established policy.

## 21. Whether review v2 may begin

**YES.** All four required fixes are implemented and deterministically tested;
the exact uncommitted state is ready for the independent Phase-4 review v2. A
real Phase-4 run remains impossible until that review exists at the canonical
path with an exact APPROVE and the reviewed state is committed cleanly.

## 22. Immediate next action

Independent Phase-4 review v2 of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict`: commit the
reviewed state, then execute the single real Phase-4 run via
`--phase 4 --execute-phase4 --expected-mnl-head <post-commit SHA>
--expected-dclaborsupply-head 27756a0… --approved-phase4-review
docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v2.md
--approved-phase4-review-sha256 <committed hash>`. Do not run
`--execute-phase4` before then.

**FINAL VERDICT: READY FOR PHASE-4 REVIEW V2** (no real Hessian; no optimizer;
nothing committed).
