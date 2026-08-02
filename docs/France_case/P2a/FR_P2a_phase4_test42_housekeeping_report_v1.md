# FR_P2a Phase-4 Test-42 Acceptance-Safe Housekeeping — Report v1

## 1. Scope

Correct the stale Phase-4 test `test_42_phase4_subprocess_dry_run_never_evaluates_hessian`
in `tests/p2a/test_p2a_regionlive_phase3_safety.py`. No Phase-4 production code,
config, accepted artifacts, or manifests were touched. No Hessian was
evaluated. No Phase-5 code was touched. This task did not commit.

## 2. Problem found

The test's final assertion was:

```python
assert not (runner.CANONICAL_PHASE4_ROOT / "complete").exists()
```

That assertion is stale: the real Phase-4 curvature run has since been
accepted, so `phase4_curvature_v1/complete/` now exists on disk (last
modified 2026-07-30) and this assertion would fail on the next run.

Separately, the dry-run subprocess is invoked with
`--out CANONICAL_REGIONLIVE_ROOT` because the runner refuses any other `--out`
for `--phase 4` (enforced at `run_p2a_regionlive_rebuild.py`, confirmed by
`test_10_canonical_out_and_config_refused`). Every dry-run invocation
therefore writes a new timestamped directory under the canonical, **git-tracked**
`phase4_curvature_v1/attempts/`. Unlike `test_29` (which by design keeps
exactly one preserved Phase-3 dry-run bundle under `phase3_estimation_v1/attempts/`,
per this file's module docstring), `test_42` was never given an isolation/cleanup
step, and the repeated re-execution this housekeeping task requires (10
consecutive runs) would otherwise leave 10 new permanent, git-visible
directories under production evidence history.

## 3. Fix applied (test source only)

File: `tests/p2a/test_p2a_regionlive_phase3_safety.py`

- Added `import shutil`.
- Updated the module docstring to state that `test_42`, unlike `test_29`,
  isolates and removes its generated evidence rather than adding to the
  permanent `attempts/` history.
- Replaced the stale `complete/`-absence assertion with an acceptance-safe
  contract, implemented in `test_42_phase4_subprocess_dry_run_never_evaluates_hessian(tmp_path)`:
  1. `_phase4_complete_inventory()` (new helper) hashes and inventories
     **every** member of the accepted `phase4_curvature_v1/complete/`
     directory (all 8 files, not just the 7-file `PHASE4_ARTIFACTS` subset
     used for the aggregate bundle hash) — captured as `before`.
  2. Records the pre-run member set of `phase4_curvature_v1/attempts/`.
  3. Runs the derivative-free subprocess dry run exactly as before
     (`--phase 4`, no `--execute-phase4`, canonical `--out`, since the
     runner refuses any other out root for phase 4).
  4. Identifies the exactly-one newly created attempt directory by set
     difference, then `shutil.move`s it into `tmp_path` (a test-owned,
     pytest-managed temporary root) **before** any assertions run against
     its contents — restoring `attempts/` to its pre-run state immediately.
  5. Asserts `gradient_evaluated`, `hessian_evaluated`, and
     `optimizer_called` are all `False` (unchanged from the prior version),
     plus the existing contract/design/binding assertions, all read from the
     isolated copy.
  6. Re-inventories `complete/` (`after`) and asserts `after == before` —
     exact byte identity **and** identical member set in one dict
     comparison.
  7. `finally:` removes the isolated `tmp_path` copy explicitly
     (`shutil.rmtree`), rather than relying on pytest's own tmp retention/
     cleanup timing.
  8. Asserts `.phase3.lock` is absent (unchanged from the prior version;
     Phase-4 reuses `Phase3Transaction`'s lock file).

No change was made to `run_p2a_regionlive_rebuild.py` or any config/YAML.

## 4. Validation

### 4a. Accepted Phase-4 bundle hash — before and after

Computed with the same join formula as `PHASE3_ACCEPTED_BUNDLE_SHA256`
(`"\n".join(f"{n}:{sha256(n)}" for n in sorted(PHASE4_ARTIFACTS))`, then
sha256 of that string) against
`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/`:

| Point in time | bundle_sha256 | member count |
|---|---|---|
| Before any test_42 runs | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | 8 |
| After 1 run + 10 consecutive runs + 13 related tests + full-file run | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | 8 |

Matches the value specified in the housekeeping prompt exactly. Per-file
hashes (unchanged before/after, verified by direct comparison, not just the
join):

```
hessian_eigenvalues.csv         f29a1a1b31cbfe73e9359c6e38f175cd55e744744d0835a006511afe10476611
hessian_free.csv                8985b619858ce8b6c5f4bbb2700bfbb7c22333c17538cc1eb8dc5b09b58f470e
hessian_free.npy                e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061
phase4_console.log              581a307e92534277534c04fedf150044b651e5ef65beffde7e29e5f7983c887d
phase4_diagnostics.json         5facb3ab9a6aa326e688eede781da8178b6033569c5891eb7bd0b8197ba3a1f3
phase4_manifest.json            1b9bf807499edf92a70bc9ad737fa6834c9a44c191db676b1a7512a4066d503b
regional_hessian_subblock.csv   2dc64925319773235d6ceb30c49aa4cf59a44781af4c592eb0bd017f9511b909
regional_schur_complement.csv   c00127bbb650d7edf46934e1e6189d5e88dd470ca616df4312b808c57705614d
```

### 4b. Corrected test run 10 consecutive times

```
RUN 1  ... 1 passed in 4.42s
RUN 2  ... 1 passed in 4.33s
RUN 3  ... 1 passed in 4.33s
RUN 4  ... 1 passed in 4.33s
RUN 5  ... 1 passed in 4.39s
RUN 6  ... 1 passed in 4.41s
RUN 7  ... 1 passed in 4.38s
RUN 8  ... 1 passed in 4.43s
RUN 9  ... 1 passed in 4.38s
RUN 10 ... 1 passed in 4.35s
```

`phase4_curvature_v1/attempts/` member count: 55 before the first run of
this task, 55 after all 10 consecutive runs (plus the 1 confirmatory run
before the loop) — zero net residue.

### 4c. Related Phase-4 no-Hessian tests

`pytest tests/p2a/test_p2a_regionlive_phase3_safety.py -k "test_33 or test_34
or test_35 or test_36 or test_37 or test_38 or test_39 or test_40 or test_41
or test_42 or test_43 or test_44 or test_45"` → **13 passed**.

Full file (`test_01` .. `test_57`) also run as an additional check → **57
passed**.

### 4d. `git diff --check`

Exit code 0 — no whitespace errors.

## 5. Byte-identity contract on the Phase-5 working set (Goal-1 manager addendum a)

SHA-256 of every uncommitted Phase-5 working-set file, before this task
started and after all validation above completed — identical in every case:

| File | SHA-256 (before == after) |
|---|---|
| `.gitignore` | `09e1945563b082d75f63f18f7c9164be4a4c84f407dc06bffc66634d3b5503d5` |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md` | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md` | `2dc01c8f230feceef2df50beb30121298566af8c43bc28966d99966bfd6a65e9` |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_remediation_report_v1.md` | `6954261bcb0a1a1567ee279ee82fc7bf06e2c6fb8c3e3b43e5703c6fdc0cb4b4` |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | `2c9b4f0593853e4378ab562c90938217639429d7029afab974dc3e6ddd33b27b` |
| `scripts/p2a/phase5_inference.py` | `d28977e97d6be9693681b834a8aa08b62ad5555398131b80fe80462526acce94` |
| `scripts/p2a/run_p2a_phase5_inference.py` | `63ea1d653eadbdfb123b21d445f4fd07ec6535b6a8419232e83496c4f87a8e20` |
| `tests/p2a/test_p2a_regionlive_phase5_inference.py` | `6f70c507de3b730b0c9a95e51486048cbfe720108be3b2da4186682202ded2c2` |

None of these files were opened with a write-capable tool during this task.

## 6. Worktree diff — disclosure

`git status --porcelain` before this task started vs. after all validation:

**Before** (unchanged since task start, matches Section 5's file list plus
`.gitignore`):
```
 M .gitignore
?? docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_remediation_report_v1.md
?? scripts/p2a/configs/p2a_phase5_inference_v1.yaml
?? scripts/p2a/phase5_inference.py
?? scripts/p2a/run_p2a_phase5_inference.py
?? tests/p2a/test_p2a_regionlive_phase5_inference.py
```

**After**, the same list plus exactly two additions:
```
 M tests/p2a/test_p2a_regionlive_phase3_safety.py
?? outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/20260801T155028Z_242820_7bd3042fec0d4ca193ee496c54789eb8_dryrun_PHASE_3_DRY_RUN_COMPLETE/
```

The first addition (`test_p2a_regionlive_phase3_safety.py`, modified) is the
permitted test_42 source change described in Section 3.

The second addition is **not** produced by test_42 or its fix. It is a
preserved Phase-3 dry-run attempt bundle created by `test_29`
(`test_29_subprocess_dry_run_never_optimizes`), which this file's own module
docstring documents as intentionally writing one such bundle per invocation,
consistent with the project's never-delete evidence discipline — the same
behavior every prior invocation of `test_29` has produced (there are ~30
such directories already committed under `phase3_estimation_v1/attempts/`
from earlier work). `test_29` is explicitly out of scope for this task
(deputy decision s7 / addendum b: "observe, do not touch"), and I did not
modify it.

This directory was produced because the "run related Phase-4 no-Hessian
tests" validation step (Section 4c) included, beyond what the prompt
required, one additional full-file run (`pytest
tests/p2a/test_p2a_regionlive_phase3_safety.py`) as an extra regression
check; that full-file run collects and executes `test_29` along with
everything else. The scoped runs that were actually required by the prompt
(the 10 consecutive `test_42` runs, and the `test_33`..`test_45` selection)
never invoke `test_29` and produced zero residue, as shown in Section 4b/4c.

I did not delete this directory: doing so would contradict the same
never-delete-evidence discipline that governs every other `phase3_estimation_v1/attempts/`
entry, and deleting or otherwise modifying anything `test_29`-related is
outside the authorization given for this task. This is disclosed here in
full rather than silently left out of the report; the Goal-1 Manager or
deputy should decide whether to keep, commit, or otherwise dispose of that
one directory. It contains no Hessian, gradient, or optimizer evaluation
(it is Phase-3 dry-run evidence, structurally identical to the ~30 other
preserved `test_29` bundles already in the tree).

## 7. Verdict

HOUSEKEEPING READY FOR REVIEW V2
