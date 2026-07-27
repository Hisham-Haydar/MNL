# FR P2a Region-Live — Phase-3 Attempt-ID Fix Report — v1

Date: 2026-07-25. Applies the single localized fix required by
`FR_P2a_region_live_phase3_code_review_v6.md` (verdict **APPROVE AFTER FIXES**,
§17). No real Phase 3; no optimizer invoked; nothing committed.

## 1. Fix verdict

**READY FOR FINAL REVIEW UPDATE.** The clock-modulo attempt identifier is replaced by
collision-resistant uuid4-based allocation performed atomically while the exclusive
Phase-3 lock is held; deterministic collision and retry-exhaustion regression tests are
added; the previously flaky transaction suite is proven stable (100/100 single-process
iterations, 100/100 solo repeats of the formerly flaky test, 10/10 full-suite runs); the
three stale comments named in review-v6 §16 are corrected; all other behavior is
unchanged.

## 2. Review-v6 blocker addressed

Review-v6 §11/§16.1: `Phase3Transaction.attempt_id` used
`time.time_ns() % 1_000_000`, which repeats heavily on this Windows host (123 distinct
values in a 10,000-construction probe). A same-ID collision could strand new attempt
evidence in `.staging/`, leave the lock behind, or corrupt attempt identity/status on
the outer STOPPED retry — violating execution-scope §9 (unique attempt staging,
preserved non-success attempts). §17 required: collision-resistant IDs (preferably
`uuid.uuid4().hex`) allocated under the lock, a deterministic regression test, repeated
suite stability, and the three comment corrections — and nothing else.

## 3. Files inspected

Read in full before editing: the execution scope doc, the simplification report, code
review v6, the runner, the config YAML, the safety test module, and the current Git
diff/state of both repositories (MNL HEAD `8ba73c161af9cec87802e2d87dd42e9d777fe0e7`,
which committed the reviewed simplification state; nested HEAD = gitlink
`27756a06ea189339aa82915ed2124628afed20eb`, nested tree clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (+59/−9)
2. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+101/−4)

Created: `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6_pre_fix.md`
(byte-for-byte archival copy of review v6, made FIRST; SHA-256
`6b6e33306c75ae355619f923a06a4dffff47a2fb7ccb852467093f9eda73718b4` identical for both
files) and this report. The config YAML is untouched (the fix needed no declarative
value); neither review file was otherwise edited; no threshold or gate value changed.

## 5. Attempt-ID design

`import uuid` added. The attempt id is now
`{UTC %Y%m%dT%H%M%SZ}_{pid}_{uuid.uuid4().hex}_{label}` — human-readable timestamp,
process id, and label retained; the UUID token is the full 32-hex `uuid4().hex`, never
truncated and never reduced by modulo. `Phase3Transaction.__init__` no longer chooses
an id: `attempt_id`/`staging` start as `None` and are set only during `acquire()`.
Destinations keep the exact prior layout (`attempts/{attempt_id}_{status}`,
`complete/`), and the final id is persisted in the manifest exactly as before
(`_phase3_run` stamps `manifest["attempt_id"]` immediately after `acquire()`; the lock
file records the allocated id).

## 6. Atomic allocation

`Phase3Transaction._allocate_unique_attempt(label)` runs ONLY while the exclusive
`.phase3.lock` (O_CREAT|O_EXCL) is held, so no two normal Phase-3 processes can reserve
the same destination. Per candidate it (1) generates a uuid4, (2) builds the id,
(3) confirms no matching destination exists in `.staging/` or `attempts/` under any
status suffix (exact name or `id_` prefix; `complete/` has a fixed, non-id-derived name
so it cannot clash), then (4) creates the staging directory with
`mkdir(parents=True, exist_ok=False)` — the mkdir itself is the atomic reservation, and
a losing race surfaces as `FileExistsError` → retry.

## 7. Collision handling

Any detected clash (pre-check or mkdir) discards the candidate and retries with a fresh
uuid4. Nothing is written outside the transaction during retries; earlier attempts are
never touched, so no result can overwrite an earlier attempt.

## 8. Retry exhaustion

The defensive bound is `_ATTEMPT_ALLOC_MAX_TRIES = 100`. On exhaustion the allocator
raises the registered stop `StopRun("S-0", "attempt-allocation", …)`; `acquire()`
catches it, releases the lock through the normal controlled path (no evidence was
staged yet, so releasing is safe), and re-raises. No attempt evidence is written
outside the controlled transaction and no misleading destination is published.

## 9. Evidence preservation

Unchanged and re-proven: dry-run/STOPPED/REVIEW_REQUIRED attempts land under
`attempts/`; `complete/` is immutable; success publishes by atomic same-root
`os.replace`; no result overwrites an earlier attempt; `.staging` holds nothing after
normal finalization. Test 31 shows two same-label same-status attempts preserved side
by side with distinct ids and intact contents.

## 10. Lock behavior

Lock-first order preserved (O_EXCL create, legacy migration under the lock, never
auto-deleted on contention, crash still leaves the lock as the intentional fail-safe).
New: the lock JSON is written with `attempt: null` at creation and updated with the
allocated id; on allocation exhaustion the lock is released via `release()` before the
stop propagates (tests 31/32 assert the lock is absent after both the normal and the
controlled-failure paths).

## 11. Deterministic collision tests

Two new tests (suite now 32) with a frozen timestamp source and a monkeypatched
`uuid.uuid4` sequence — fully deterministic, no clock dependence:

- **test_31** (uuid sequence a,a,a,b): first attempt takes `a`; the second detects the
  collision against the existing `…a…_STOPPED` destination twice, retries, and lands on
  `b` (uuid call count asserted 1 → 4). Asserts: distinct ids, full untruncated hex in
  the id, both same-label/same-status attempts preserved under `attempts/` with
  distinct intact contents, `.staging` empty, lock absent; a planted stranded
  `.staging` directory is recognized as an occupied destination.
- **test_32** (uuid stuck on `f`×32): allocation stops cleanly after exactly 100
  candidates (call count asserted 101), raising the `attempt-allocation` StopRun;
  asserts lock absent (releasable controlled path), `.staging` empty, `attempts/`
  unchanged with the first attempt intact, no `complete/`; a fresh transaction then
  reuses the root normally.

## 12. Repeated stability tests

All in one process via a scratchpad driver (E1/E2), then whole-suite repeats (E3):

- E1: the five transaction tests (14, 15, 16, 31, 32) × 100 consecutive iterations —
  **100/100 passed** (500 test executions), exit 0.
- E2: previously flaky `test_14_success_bundle_immutable` × 100 solo iterations —
  **100/100 passed**.
- E3: complete no-optimizer suite × 10 consecutive runs —
  **10/10 runs, 32 passed each**, exit codes `0,0,0,0,0,0,0,0,0,0`.

No real optimizer invoked in any run (estimator tests monkeypatch
`scipy.optimize.minimize`; the subprocess dry-run never reaches estimation).

## 13. Comment corrections

Exactly the three stale comments from review-v6 §16.2, no behavior change:

1. Module-inventory comment: “tracked, byte-identical blob” → tracked blob with
   Git-canonical content equality (`git hash-object --path`; autocrlf rationale).
2. `_phase3_estimate` docstring: removed the stale `minimize_fn`-injection sentence;
   now states unit tests monkeypatch `scipy.optimize.minimize`.
3. Test-module preamble: now states test 29's canonical dry-run intentionally writes
   one preserved attempt bundle under the production `attempts/` history
   (never-delete discipline); no other test writes a production path.

## 14. Phase 1–2 regression

Scratch-root `--phase 2 --dry-run`: exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`; frames
byte-identical, G-19 objective jax = numpy = 19053.4655316009 (|dev| 0.00e+00,
|jax−np| 3.64e-12); regenerated stem **byte-identical** at
`8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

## 15. Phase-3 dry-run

Canonical CLI without `--execute-phase3`: exit 0, `PHASE_3_DRY_RUN_COMPLETE`;
`optimizer_called: false`, `execution_ready: false`,
`review_gate: AWAITING_REVIEW_V6_APPROVE`; `complete/` absent; lock released; the
published attempt id carries the new full-uuid format.

## 16. Prohibited-operation audit

No real Phase 3, no real optimizer, no EUROMOD/inference/post-estimation/welfare/
synthetic-recovery/notebook runs; `--phase 4` refused (exit 2);
dclaborsupply-monorepo untouched (clean at `27756a0…`); Phase 1–2 evidence, data,
theta files, specifications, certified pooled baseline, config YAML, and both review
files unmodified; no Git history rewritten; nothing committed.

## 17. Git diff summary

```text
 M scripts/p2a/run_p2a_regionlive_rebuild.py      (+59/−9)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py (+101/−4)
 ?? docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6_pre_fix.md
 ?? docs/France_case/P2a/FR_P2a_region_live_phase3_attempt_id_fix_report_v1.md
 ?? outputs/.../phase3_estimation_v1/attempts/…_dryrun_PHASE_3_DRY_RUN_COMPLETE/
    (validation dry-run bundles, new uuid id format)
```

`git diff --check` exit 0. MNL HEAD `8ba73c1` untouched; history intact.

## 18. Residual warnings

- Validation added 12 dry-run attempt bundles (11 full-suite runs' test 29 plus the
  standalone canonical dry-run) to the canonical `attempts/` history — consistent
  with the never-delete discipline, and to be committed with the fix per
  review-v6 §19.
- The review-v6 §18 low-severity coverage niceties from the simplification report §18
  remain as previously recorded; review v6 did not require them for this fix.
- The lock file now momentarily reads `attempt: null` between lock creation and
  allocation (milliseconds); a crash in that window leaves a lock without an attempt
  id, which is the intended fail-safe and inspectable either way.

## 19. Whether final review update may begin

**YES.** The single in-scope blocker is fixed exactly as prescribed, with
deterministic tests and repeated-run stability evidence; everything else is
byte-preserved except the three sanctioned comment corrections.

## 20. Immediate next action

Independent verification of this diff and update of the canonical v6 review to an
exact `**FINAL VERDICT: APPROVE**`. Then: commit the fixed state in a fully clean
tree, record the post-commit MNL SHA, nested SHA, and approved-review SHA-256, and
execute the first real Phase-3 estimation once via the scope-doc §8 CLI. Phases 4–8
remain manager-gated.

**FINAL VERDICT: READY FOR FINAL REVIEW UPDATE** (no real Phase 3; nothing committed).
