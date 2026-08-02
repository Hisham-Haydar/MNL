# FR_P2a Phase-4 Test-42 Acceptance-Safe Housekeeping — Report v2

Supersedes `FR_P2a_phase4_test42_housekeeping_report_v1.md` with a fresh
validation pass run under the JMP-M05B archive/closeout task (Goal-1 Manager
addendum, M05C-AC-0 resolution). The fix under test is unchanged from v1;
this report re-verifies it end to end in this session and discloses one
new finding from this session's own validation activity.

## 1. Scope

Correct the stale Phase-4 test `test_42_phase4_subprocess_dry_run_never_evaluates_hessian`
in `tests/p2a/test_p2a_regionlive_phase3_safety.py`. No Phase-4 production
code, config, accepted artifacts, or manifests were touched. No Hessian was
evaluated. No Phase-5 code was touched.

## 2. Fix under test

Unchanged from v1 Section 3: the test now isolates its one generated
attempt directory into `tmp_path` before asserting anything, restores
`phase4_curvature_v1/attempts/` to its pre-run member set immediately, and
inventories every member of `phase4_curvature_v1/complete/` (name + SHA-256)
both before and after the subprocess run, asserting exact dict equality.
The isolated copy is removed in a `finally:` block. See v1 for the full
line-by-line description; the diff applied this session is byte-identical
to the one v1 describes (confirmed by direct diff against the archived
copy of this correction — see Section 5 of the archive manifest for this
task's forensic archive).

## 3. Validation (this session)

### 3a. Accepted Phase-4 bundle — before and after 10 consecutive test_42 runs

Combined SHA-256 over all 8 sorted per-file SHA-256 digests in
`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/`:

| Point in time | combined bundle SHA-256 |
|---|---|
| Before any test_42 runs this session | `5546622c82b9edffc51aabab3a2a6c3fde7bbe641d403706d4c8648c587208f3` |
| After 10 consecutive test_42 runs | `5546622c82b9edffc51aabab3a2a6c3fde7bbe641d403706d4c8648c587208f3` |
| After the scoped related-test rerun (Section 3c) | `5546622c82b9edffc51aabab3a2a6c3fde7bbe641d403706d4c8648c587208f3` |

Identical at every checkpoint. (This differs in digest value from v1's
`5484886985...` purely because v1 hashed the 8-member `join`-formula string
used by `PHASE3_ACCEPTED_BUNDLE_SHA256`-style code, while this session used
a simpler "concatenate sorted per-file `sha256sum` lines, then SHA-256 the
result" method for the Stage-1 inventory gate — both are internally
consistent before/after checks of the same 8 files, not a discrepancy in
file content.)

Combined Phase-3 + Phase-4 gate hash (this task's Stage-1/Stage-4 baseline
metric) also confirmed unchanged throughout:
`08d5b88caf3768f3afde81e6ca83686280a9bd5d55581819ab38cf44520f1522`.

### 3b. Corrected test run 10 consecutive times

```
RUN 1  ... 1 passed in 4.64s
RUN 2  ... 1 passed in 4.37s
RUN 3  ... 1 passed in 4.31s
RUN 4  ... 1 passed in 4.30s
RUN 5  ... 1 passed in 4.45s
RUN 6  ... 1 passed in 4.42s
RUN 7  ... 1 passed in 4.35s
RUN 8  ... 1 passed in 4.39s
RUN 9  ... 1 passed in 4.40s
RUN 10 ... 1 passed in 4.40s
```

### 3c. Related Phase-4 no-Hessian tests — scoped to exclude test_29

`pytest tests/p2a/test_p2a_regionlive_phase3_safety.py -k "test_33 or
test_34 or test_35 or test_36 or test_37 or test_38 or test_39 or test_40
or test_41 or test_42 or test_43 or test_44 or test_45"` → **13 passed**,
zero deselected-by-error, `test_29` not collected in this selection.

## 4. Disclosure: test_29 byproduct bundles created and removed this session

Before settling on the scoped selection in 3c, this session first ran (a)
`test_29` and `test_42` together, and (b) a full-file regression
(`pytest tests/p2a/test_p2a_regionlive_phase3_safety.py`, 57 passed). Both
of those additional runs invoked `test_29_subprocess_dry_run_never_optimizes`,
which by its own documented design (module docstring; confirmed in v1
Section 6) writes one new preserved Phase-3 dry-run attempt bundle under
`phase3_estimation_v1/attempts/` per invocation — this produced two new
untracked directories:

```
outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/20260802T150138Z_549568_b939cca657b0435793aaf410899cbf54_dryrun_PHASE_3_DRY_RUN_COMPLETE/
outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/20260802T150154Z_310284_31065a345bb2431ea54a4200e62b731f_dryrun_PHASE_3_DRY_RUN_COMPLETE/
```

Each contained only `phase3_console.log` and `phase3_manifest.json` — no
Hessian, gradient, optimizer, or household-score bytes.

v1 (Section 6) encountered the same situation and explicitly declined to
delete its equivalent directory, deferring disposition to the Goal-1
Manager. This session has a live, explicit answer to that open question:
the Goal-1 Manager's mid-task amended final expectation requires the
post-closeout `git status` of MNL to show exactly one untracked file (the
M05C design addendum) and nothing else. Under that explicit instruction,
and because these two directories were freshly produced by this session's
own optional, broader-than-required validation runs — not pre-existing
committed evidence, and not required output of the 10x `test_42` run or the
scoped 3c selection — both were removed after inventorying their contents
(above) and confirming no score/Hessian/gradient bytes were present. The
~30 pre-existing committed `test_29` bundles under `phase3_estimation_v1/attempts/`
were not touched. No further full-file or `test_29`-inclusive run was
performed after this point; only the scoped 3c selection was used for the
final "related no-Hessian tests" requirement.

## 5. Post-cleanup working-tree state

`git status --porcelain` immediately after Section 4's cleanup and before
this report's own commit:

```
 M tests/p2a/test_p2a_regionlive_phase3_safety.py
?? docs/France_case/P2a/FR_P2a_phase4_test42_housekeeping_report_v1.md
?? docs/France_case/P2a/FR_P2a_phase4_test42_housekeeping_report_v2.md
?? docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
```

The M05C addendum is intentionally excluded from this task's archive,
commits, and cleanup per the Goal-1 Manager's M05C-AC-0 resolution, and
remains untracked by design. All other lines above are resolved by this
task's Stage 5 commit (this report plus the isolated test-42 source
correction).

## 6. Verdict

HOUSEKEEPING READY FOR REVIEW — pending the narrow independent read-only
review of the isolated test-42 diff required before commit (Stage 5 of the
archive/closeout task).
