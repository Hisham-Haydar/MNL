# FR P2a — JMP-M05C Streaming Inference — Increment A bounded refix report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Task:** the one bounded Increment-A refix authorized by `JMP_M05C_incrementA_E2_deputy_decision_v1.md`
**Mode:** implementation + tests only. No commit. No Increment B. No full-population run.
**Date:** 2026-08-02
**MNL HEAD (unchanged throughout):** `b5169293b647dda3e07070c678f8d46d33b1bf89`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Refix verdict

**READY FOR REVIEW A V2**

All five authorized fixes are implemented, each with a reviewer-runnable proof and
a non-vacuity demonstration. The exact expected working set was restored **inside
this task** — the four unexpected test-29 attempt files were inventoried, hashed,
content-checked and deleted, and the two directories they occupied removed. The
Increment-A test set grew from 42 to **76 tests**, all passing; the safe broader
suite is **137 passed, 1 deselected**, run twice, leaving `attempts/` at its
committed count of 70.

Two things the reviewer should know before reading further, because both are
disclosures rather than clean results:

1. **The Fix A-1 detector was itself defective on first write, and I found and
   fixed it.** My exception-graph walker used an `id()`-keyed visited set without
   pinning the visited objects. CPython recycles the ids of freed temporaries, so
   the walk could silently skip a node — a false-green generator inside the very
   test meant to prove no false green. It is now deterministic (proved by
   `test_D20`, and by 20 consecutive green runs). §7.3 gives the full account.
2. **Foreign exception messages are now suppressed** at the stream boundaries, in
   exchange for the guarantee that no third-party message can carry array values
   into a log. This costs debuggability. §17 records it as a residual warning for
   Increment C rather than burying it.

`FR_P2a_streaming_incrementA_report_v1.md` and `FR_P2a_streaming_incrementA_review_v1.md`
are **byte-identical** to their task-start state, per the Goal-1 Manager addendum
(d); verified in §16.4. This report — not report v1 — carries the repaired
verbatim PROOFS packet required by Fix A-4 (§10, §15).

---

## 2. Scope

Exactly the five fixes of Review A §9 / deputy decision §2. Nothing else moved.

| Fix | Review finding | Deputy ref | Status |
| --- | --- | --- | --- |
| 1 | NP-1 — score array retained by the failure traceback | A-1 | DONE (§7) |
| 2 | DG-1 — non-integral batch IDs silently truncated | A-2 | DONE (§8) |
| 3 | T16-1 — T-16 run on 24 households, not the frozen 64 | A-3 | DONE (§9) |
| 4 | PR-1 — PROOFS not verbatim-reproducible | A-4 | DONE (§10, §15) |
| 5 | ST-1 — four unexpected test-29 attempt files; no safe full-suite rule | A-5 | DONE (§4, §11) |

**Explicitly not done, by prohibition:** no commit; no Increment-B object (bread,
covariance, standard errors, Wald, correction scalar, diagnostics JSON); no
Increment-C object (runner, transaction, manifest, reproduction gate); no
restricted-store reference; no full-population run; no change to design v4, the
addendum, the charter, the package, θ̂, the pins, or any tolerance constant.

---

## 3. Starting state

Recorded before any action in this task.

| Item | Expected (addendum (a)) | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `b5169293b647dda3e07070c678f8d46d33b1bf89` | identical | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean (`--untracked-files=all` empty) | PASS |

Untracked working set at task start — exactly the nine paths the addendum names:

```text
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_review_v1.md
?? outputs/.../attempts/20260802T153430Z_..._dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_console.log
?? outputs/.../attempts/20260802T153430Z_..._dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_manifest.json
?? outputs/.../attempts/20260802T155349Z_..._dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_console.log
?? outputs/.../attempts/20260802T155349Z_..._dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_manifest.json
?? scripts/p2a/p2a_phase5_score_stream.py
?? tests/p2a/conftest.py
?? tests/p2a/test_p2a_phase5_score_stream.py
```

Nothing else was present. No halt condition fired.

---

## 4. State disposition

Executed inside this task as a verified step (deputy decision §4 — never a human
pre-step).

### 4.1 Inventory and hashes of the four files

| Path (under `outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/`) | Bytes | SHA-256 |
| --- | --- | --- |
| `20260802T153430Z_270236_480b4748926746fa994fd3f616a36d94_dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_console.log` | 342 | `f0a1ffce431b9080d21c693b6fd1e8f7e9f4d8126a54049007e213b0c6d80af6` |
| `20260802T153430Z_270236_480b4748926746fa994fd3f616a36d94_dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_manifest.json` | 22,771 | `d8f96d80dd7f8c469ac99fbcdb72f75fa3c0ca5954d9aae7d71b31fe2d1e97d9` |
| `20260802T155349Z_500640_ed2da8d233294b158fbe93d003e04b75_dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_console.log` | 342 | `9f571de14aa3fe0bebd3f8e1c349f09e197b52c1ff75de1f30bfccb00f8d3e22` |
| `20260802T155349Z_500640_ed2da8d233294b158fbe93d003e04b75_dryrun_PHASE_3_DRY_RUN_COMPLETE/phase3_manifest.json` | 22,771 | `b485665fb9533322d24dbb440cbf2a4fa2345fba1d3f00934486558dccf8f011` |

### 4.2 Content verification before deletion

| Check | Result |
| --- | --- |
| Contains household score rows | NO — no `NUMPY` magic; no `score` token; no `idhh` token in either file of either directory |
| Is an accepted bundle member | NO — neither SHA-256 appears among the Phase-3 (5) or Phase-4 (8) `complete/` member hashes |
| Contains an accepted artifact | NO — each manifest's `artifact_hashes` names only its own sibling `phase3_console.log` |
| Is required evidence | NO — status `PHASE_3_DRY_RUN_COMPLETE`, `optimizer_called: false`, `execution_ready: false`, `stop: null`; duplicates of the 70 committed attempts of the same kind |
| Referenced anywhere else | NO — a repo-wide search for both attempt ids and both uuids returns only the two manifests themselves plus report v1 and Review A, which cite them *as the finding* |

### 4.3 Actions taken

1. deleted exactly the four files listed in §4.1;
2. confirmed both parent directories were then empty (0 entries each) and removed
   them with `rmdir` — no recursive delete was used anywhere;
3. `attempts/` returned to **70** entries, its committed count.

### 4.4 Post-action working set

```text
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_refix_report_v1.md   <- this file
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_review_v1.md
?? scripts/p2a/p2a_phase5_score_stream.py
?? tests/p2a/conftest.py
?? tests/p2a/test_p2a_phase5_score_stream.py
```

Exactly the authorized Increment-A files, report v1, Review A v1, and this
remediation report. Nothing else. Re-verified after every test run in §14.

---

## 5. Files inspected

Read in full, in binding order: the deputy decision; the streaming addendum; the
M05C charter; `FR_P2a_region_live_phase5_inference_design_v4.md` (§§3, 5–7, 14–17
in detail); `FR_P2a_streaming_incrementA_report_v1.md`;
`FR_P2a_streaming_incrementA_review_v1.md`;
`JMP_M05C_E2_incrementA_review_reject_v1.md`; the three delivered Increment-A
files; `phase5_parameter_map_v1.csv`; `phase5_source_inventory_v1.json`; the
Phase-3 and Phase-4 `complete/` bundles and both manifests.

Inspected read-only and **not modified**: the nested package
(`data/loader.py`, `likelihood/engine_jax.py`), and
`scripts/p2a/run_p2a_regionlive_rebuild.py` (to confirm test 29's target root
for Fix A-5).

---

## 6. Files modified

Three files. No file outside this list was touched.

| Path | SHA-256 (after refix) | Bytes | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/p2a_phase5_score_stream.py](scripts/p2a/p2a_phase5_score_stream.py) | `9285aad5e040dcd7462204d2c4ec1353d266b1d2a6558f18b7a1a8e356250377` | 46,437 | 1,012 |
| [tests/p2a/test_p2a_phase5_score_stream.py](tests/p2a/test_p2a_phase5_score_stream.py) | `8152ad1a62493459ba7af76c1e9d20ea59477685e217091ba0d04a8fb21448ed` | 58,284 | 1,241 |
| [tests/p2a/conftest.py](tests/p2a/conftest.py) | `e519416604462256341b2465dabde4c7188ccf463e22c444acf1d33d358e58bd` | 2,898 | 68 |

Unchanged, byte-identical to task start (§16.4):

| Path | SHA-256 |
| --- | --- |
| `docs/France_case/P2a/FR_P2a_streaming_incrementA_report_v1.md` | `ed59e8b3dcee74d86e09e14772705539449fe0da548e601629fa849be586b1fa` |
| `docs/France_case/P2a/FR_P2a_streaming_incrementA_review_v1.md` | `4ab8f808ca222ccee23fa9aaaaa784613c9fdf221c944b274e03720c6259b9f1` |

### 6.1 Mechanical hunk → fix map (addendum (b))

Diffs taken against a task-start snapshot of each file, line-endings normalised.
`diff -U0` hunk counts: module 29, tests 8, conftest 3. Every hunk maps to a fix.

**`scripts/p2a/p2a_phase5_score_stream.py` — 29 hunks**

| Hunks | Region | Fix |
| --- | --- | --- |
| 1 | `typing` import gains `NoReturn` | A-1 |
| 2 | new constants `_CANONICAL_ID_DTYPE`, `_INT64_MAX`, `_FLOAT64_EXACT_INT_MAX` | A-2 |
| 3 | `ScoreStreamError` gains `code`; docstring | A-1 |
| 4 | new `_sanitize`, `_raise_clean` | A-1 |
| 5 | `_as_int64_ids` replaced by `_require_canonical_ids` | A-2 |
| 6 | new `_loader_ids_to_canonical` | A-2 |
| 7–8 | `build_canonical_order` uses the loss-free converter; docstring | A-2 |
| 9 | `ScoreStreamReducer.__init__` gains `_failed` | A-1 |
| 10 | `_check_batch` gains the poisoned guard and the strict ID gate | A-1 + A-2 |
| 11–20 | `_check_batch` error messages gain `SS-*` codes; `.astype` removed from the canonical-order comparison | A-1 (codes) + A-2 (`.astype`) |
| 21–23 | `update` becomes a sanitized boundary; fold extracted to `_accumulate` | A-1 |
| 24–25 | `result` gains the poisoned guard and routes raises through `_raise_clean` | A-1 |
| 26 | `_gender_score_block` uses `_loader_ids_to_canonical`; no `.astype` in the id comparison | A-2 |
| 27 | `compute_batch_scores` becomes a sanitized boundary; body split to `_compute_batch_scores` | A-1 |
| 28–29 | `run_score_stream` becomes a sanitized boundary with `finally`-release | A-1 |

**`tests/p2a/test_p2a_phase5_score_stream.py` — 8 hunks**

| Hunks | Region | Fix |
| --- | --- | --- |
| 1 | `T16_HOUSEHOLDS = 64` constant | A-3 |
| 2 | graph walker, leak detector, capture helpers | A-1 |
| 3 | `test_D9`–`test_D12`, `test_D20` (failure graph) | A-1 |
| 3 | `test_D13`–`test_D17` (strict IDs) | A-2 |
| 4 | `test_D18`, `test_D19` (test-29 guard) | A-5 |
| 5 | `_capture_stream_failure` helper | A-1 |
| 6 | `test_D10` rule-4 assertions updated to shape-scoped exemption | A-1 |
| 7 | `binding64` fixture | A-3 |
| 8 | `test_E4`/`test_E5` → first 64; `test_E4s`/`test_E5s` smoke; `test_E13` | A-3 + A-1 |

**`tests/p2a/conftest.py` — 3 hunks**: all Fix A-5 (module docstring documenting
the rule, the `TEST29_*` constants and `test29_is_allowed`, and the
`pytest_runtest_setup` guard).

### 6.2 One incidental correction, disclosed

While applying Fix A-1 a scripted edit rewrote the module with Windows line
endings, flipping all 768 lines from LF to CRLF. That is a whole-file change with
no fix number, so it was **reverted**: the module is back to its task-start
LF convention, which is what makes the 29-hunk map above meaningful. The two test
files were CRLF and LF respectively at task start and remain so. No content was
affected either way.

---

## 7. Fix 1 — failure-path score release

### 7.1 What was wrong

Review A §5 raised the shipped non-finite error and walked `exc.__traceback__`,
finding the same `(3, 37)` float64 array live in three frames:

```text
('trigger', 'scores', (3, 37), 'float64')
('update',  'scores', (3, 37), 'float64')
('_check_batch', 'scores', (3, 37), 'float64')
```

The v1 test asserted only that `str(exc)` carried no values and that the cwd was
empty. It never inspected `__traceback__`, `__context__` or `__cause__`.

### 7.2 What changed

A sanitized boundary at each public entry point — `ScoreStreamReducer.update`,
`compute_batch_scores`, `run_score_stream` — plus `ScoreStreamReducer.result`.

* `_sanitize(exc, boundary_code)` returns a **new** `ScoreStreamError` with
  `__traceback__`, `__cause__` and `__context__` all `None`. The failing object
  graph is discarded wholesale, not pruned.
* Each boundary drops its own binding on the score array **before** raising:
  `update` does `del scores` in a `finally`; `run_score_stream` does `del block`
  in a `finally`, so the release happens during unwinding, before the exception
  leaves the frame. `del` removes the name from the frame entirely rather than
  rebinding it.
* `_raise_clean(error)` performs the raise from a frame whose only local is the
  error itself, and is called only from *outside* an `except` block so Python
  attaches no implicit `__context__`.
* Message policy: our own messages are preserved verbatim (they are authored here
  and carry only shapes, counts, names, dtypes and canonical positions); a foreign
  exception's message is replaced by its type plus the boundary code, because a
  NumPy/JAX/pandas message may embed array contents.
* The reducer is **poisoned** after any failed batch: `result()` and further
  `update()` calls refuse with `SS-POISONED`. A partial accumulator set and a
  partial digest are not a stream.

Observed traceback after the fix, for the reviewer's own scenario:

```text
frames: ['<caller>', 'update', '_raise_clean']
  <caller>      locals: ['b', 'r']            <- caller dropped its own reference
  update        locals: ['batch', 'failure', 'self']   <- no 'scores' at all
  _raise_clean  locals: ['error']
```

### 7.3 The detector defect I found and fixed

`test_D9` traverses the **complete** final exception graph: the exception, its
`args`, its instance `__dict__`, `__cause__`, `__context__`, every `__traceback__`
frame's `f_locals`, and containers and plain-object `__dict__`s reachable from
those, to a bounded depth and node budget. `frame.f_globals`/`f_builtins` are
deliberately excluded: they are the module and builtin namespaces, alive
regardless of the exception, and walking them would report this test module's own
`SYNTH_SCORES` constant as "retained".

The first version of that walker keyed its visited set on `id(obj)` **without
holding a reference to the visited objects**. Traversal creates short-lived
temporaries (`dict(f_locals)`, `vars(obj)`); once freed, CPython reuses their ids,
so a later distinct object could inherit an id already marked seen and be skipped.
Measured directly: three consecutive `_score_leaks` calls on one exception
returned `0, 1, 1` findings. A detector that can silently skip nodes is a
false-green generator — precisely the class of defect this fix exists to remove.

Fixed by pinning every visited object for the duration of the walk. Now
deterministic: eight consecutive walks give 704 nodes each and a stable verdict,
and the walk demonstrably reaches the reducer's own `_m37` attribute, so it is not
merely shallow. `test_D20` asserts both properties.

**Leak rules.** A finding is: identity with the supplied block; sharing memory
with it; equality in shape/dtype/value with it; any 2-D `ndarray` with 37 columns
that is not an addendum §2 aggregate shape `(37,37)`/`(35,35)` and is not an
explicitly permitted array; or raw score bytes in `bytes`/`bytearray`/`memoryview`.
The aggregate-shape exemption is not a hole — `test_D20(b)` shows a retained
37×37 *score* block is still caught by the identity/memory/equality rules.

### 7.4 Coverage

| Test | What it proves |
| --- | --- |
| `test_D9` (×3: NaN, +Inf, −Inf) | the caller-visible exception retains no score, on the synthetic reducer path |
| `test_D10` | the walker and detector are not vacuous: frame-local, `__context__`, `__cause__`, attribute-payload, raw-bytes and rule-4 leaks are each detected |
| `test_D20` | traversal is deterministic and deep enough; the shape exemption is not a hole |
| `test_D11` | a failed reducer is poisoned — no `result()`, no further `update()` |
| `test_D12` | foreign messages suppressed; our own preserved; chaining fields cleared |
| `test_E13` | **the real production path**: real loader, real likelihood, real reducer; one NaN injected into a genuinely computed block so `run_score_stream` is holding a live `(8, 37)` array when it fails |
| retained | `test_D5`, `test_D6`, `test_D8` — file, message and stdout/stderr checks, unchanged |

---

## 8. Fix 2 — strict ID validation

### 8.1 What was wrong

`_check_batch` compared `batch.idhh.astype(np.int64)` and the digest then called
`int(batch.idhh[k])`. A forged batch with ids `10.5, 20.5, 30.5` was accepted and
produced **the same digest** as ids `10, 20, 30` — contradicting the published
`int64_le` contract. Separately, `_as_int64_ids` cast to `int64` *first* and
validated afterwards, so an out-of-range or non-integral value was truncated
before it was inspected.

### 8.2 What changed

Two functions, one strict and one loss-free, with the strict one at the boundary.

**`_require_canonical_ids(ids, where)` — the reducer boundary.** Performs **no
cast of any kind**. It accepts exactly one representation: a 1-D, C-contiguous,
native-byte-order signed `int64` numpy array — the representation
`build_canonical_order` produces and `CanonicalOrder.batches` slices. Every
required rejection follows from the dtype gate alone, with no probing cast:

* floats, *including numerically integral ones*, are not `int64`;
* `NaN`, `±Inf`, fractional values and magnitudes outside signed-64-bit cannot
  exist in an `int64` array, so they can only arrive under a rejected dtype;
* `object`, `str`/`bytes`, `bool`, `complex`, unsigned, narrower/wider integer
  dtypes and non-native byte order are each a dtype other than native `int64`
  (`np.dtype('>i8') != np.dtype(np.int64)`, so endianness is covered).

It runs **first** in `_check_batch`, before the order comparison and before any
digest update. The order comparison no longer casts.

**`_loader_ids_to_canonical(values, tag)` — the one permitted conversion.** The
package loader may hand back any integer or float dtype, so exactly one
conversion point exists, and it validates on the **original** dtype before
casting: unsigned values are range-checked against `int64` max; floats are
checked finite, then integral (`arr == trunc(arr)`), then bounded by `2**53`
beyond which a float64 no longer represents every integer exactly; anything else
is rejected. Only then does it cast.

**R-32a freeze condition (deputy §2 A-2, note §4 of the E2 memo):** after this
fix the reducer boundary rejects non-integral, non-finite, out-of-range and
non-canonical ID representations before any digest update. `test_D14` is the
forged-`.5` proof.

### 8.3 Coverage

`test_D13` — 13 parametrised rejections at the reducer boundary: fractional
floats (the reviewer's forgery), numerically integral floats, NaN, +Inf, −Inf,
out-of-int64-range floats, float32, int32, uint64, big-endian int64, object,
strings, bool. Each asserts the code is `SS-IDDTYPE`/`SS-IDTYPE` **and** that
`reducer._cursor` is still 0, i.e. nothing was folded and nothing hashed.

`test_D14` — the honest int64 stream reproduces the pinned digest
`a077a2ab…`; the `+0.5` forgery is refused with `SS-IDDTYPE`; the reducer is then
poisoned so it cannot be coaxed into emitting any digest.
`test_D15` — canonical production int64 ids pass and reproduce the pinned digest.
`test_D16` — six cases proving the loader conversion validates before casting.
`test_D17` — int64/int32/uint32/integral-float64 loader dtypes convert exactly.

---

## 9. Fix 3 — first-64 T-16

`test_E5_t16_forward_reverse_mode_agreement_first64` and
`test_E4_t11_chunk_route_invariance_first64` now run on the design v4 frozen
slice, backed by a new `binding64` fixture (`household_limit=64`).

| Item | T-11 (first 64) | T-16 (first 64) |
| --- | --- | --- |
| Forward mode | `jax.jacfwd` | `jax.jacfwd` |
| Reverse mode | — (same mode both legs) | `jax.jacrev` |
| Batch tuple | (16, 64) — four batches vs one | (64, 64) — one batch each leg |
| Frozen bar | `1e-12 · max\|S\|` = `3.023468094208269e-11` | `1e-10 · max\|S\|` = `3.023468094208269e-09` |
| Observed deviation | `0.0` | `7.105427357601002e-15` |
| `max\|S\|` over the slice | `30.23468094208269` | `30.23468094208269` |
| Result | **PASS** | **PASS** (≈5.6 orders of margin) |

Both figures reproduce Review A §6's independent first-64 run exactly
(`0.0` and `7.105427357601002e-15` against the same two bars), which is useful
corroboration that the reviewer and this implementation are measuring the same
object.

The 24-household checks are retained but **renamed and relabelled** as smoke
coverage only — `test_E4s_smoke_chunk_invariance_24` and
`test_E5s_smoke_mode_agreement_24`. Their docstrings state explicitly that they
are not T-11/T-16 evidence. They earn their place by exercising ragged final
batches (sizes 3, 8, 24) that the 16/64 split does not produce.

---

## 10. Fix 4 — reviewer-runnable proofs

The repaired PROOFS packet is §15 of **this** report. Report v1 is left
byte-identical per addendum (d), so §15 supersedes report v1 §5 for review
purposes; a reviewer should execute §15 and ignore report v1 §5.

What was repaired, against each Review A §3 complaint:

| Defect | Repair |
| --- | --- |
| no interpreter/activation command; bare `python` resolved to CPython 3.14.2 without JAX | every command invokes `.\.venv\Scripts\python.exe` explicitly |
| stale counts (`29 passed, 12 deselected`; `12 passed, 29 deselected`) | all counts regenerated after every new test was in place and frozen in §15 |
| PROOF-8 required the reviewer to create `proof8.py` | replaced by a single-line `-c` command; no file is created |
| edit-based red bars (`change one hex character of SYNTH_DIGEST`) | replaced by committed tests that perform the mutation in memory (`test_D7`, `test_D10`, `test_D20`, `test_E11`, `test_E12`) |
| working directory unstated | every command states `cd C:\Users\hisham\Repo\MNL` |
| full-suite commands wrote attempts | every full-suite command carries `-k "not test_29_subprocess_dry_run_never_optimizes"` |

Every §15 command was executed **verbatim in PowerShell from the repository
root** before this report was written; §15 records the outputs actually observed,
not predicted ones. All are read-only, create no reviewer-owned file, and require
no source edit. `-p no:cacheprovider` is included so no `.pytest_cache` is written.

---

## 11. Fix 5 — test-29 state rule

Two parts.

**The rule.** Every full-suite command in this report and in future M05C cards
carries `-k "not test_29_subprocess_dry_run_never_optimizes"`. §15 P-10 is the
canonical safe command.

**The guard.** `tests/p2a/conftest.py` now installs a `pytest_runtest_setup` hook
that fails test 29 **in setup** — before the test body runs, and therefore before
its subprocess can spawn or write — unless the operator opts in explicitly with
`MNL_ALLOW_TEST29=1`. The failure message names both escapes.

The guard was live-fired: running the whole suite selected on test 29 without the
opt-in produces `137 deselected, 1 error in 0.42s` and `attempts/` stays at 70.
Before the guard, that same invocation appended a directory.

`test_D18` verifies the hook against a stand-in item (no subprocess is spawned):
blocked by default, message names both escapes, unrelated test names untouched,
and the opt-in releases it. `test_D19` documents *why* by asserting that test 29's
target is the canonical accepted output root, which holds the immutable
`complete/` bundle.

The guard is test-infrastructure only. `conftest.py` still defines no evaluator,
loader, reducer, fixture or autouse hook, so Review A §4's production-path
integrity finding is unaffected.

---

## 12. Statistical-design preservation

Nothing in the streaming statistical design changed. Specifically unchanged:

* the score definition `s_g = ∇_x ℓ_g` on the accepted per-group positive
  log-likelihood, and the Phase-4 pin-fixed reparameterisation
  `base_full_47.at[free_idx].set(x_free)`;
* the canonical order — design v4 §6.3 order (b), `idhh`-ascending stable argsort
  of the loader group ids;
* the addendum §2 accumulators `g₃₇`, `M₃₇`, `M₃₅` and the by-name 35-interior
  selector (active positions still `(2, 6)` = `beta_l_age2_sm`, `beta_l_age2_sf`);
* the digest composition and the `int64_le` + float64-LE byte contract, 304
  bytes/household. Fix A-2 changes only *which representations may reach* the
  encoder, never the encoding;
* the frozen bars `1e-12·max|S|` (T-11) and `1e-10·max|S|` (T-16);
* θ̂, the ten pins, the certified spec, and both accepted bundles.

Evidence that the numbers did not move: the pinned synthetic digest
`a077a2ab7b5e8141247dd6bdd3591669b795511ad6881409988353ed3327175c` and the
analytic aggregates (`21·c`, `91·c_jc_k`) still hold bitwise (`test_C1`–`test_C4`);
the T-17 fingerprints still reproduce (`cb50ecd8…`, `44af628f…`); and the
production aggregates still match the direct `jacrev` reference (`test_E2`).

---

## 13. Package-boundary preservation

`dclaborsupply-monorepo` is untouched: HEAD `27756a06…` equals the MNL gitlink,
and `git status --porcelain --untracked-files=all` inside it is empty (§16.2).
No package file was edited, and no package change was required.

The module calls into the package at three points only, all read-only and all
pre-existing: `dclaborsupply.data.loader.load_singles`,
`dclaborsupply.likelihood.engine_jax.build_jax_singles_ll(..., per_group=True)`,
and `engine_jax._load_jax()` for eager float64 activation. The last is the
package's own float64 initialiser, named as such by design v4 §3.3; calling it is
not modifying it.

---

## 14. Test results

All runs used `.\.venv\Scripts\python.exe` from `C:\Users\hisham\Repo\MNL`.

| Run | Result |
| --- | --- |
| Complete Increment-A set, run 1 | `76 passed in 70.97s` |
| Complete Increment-A set, run 2 | `76 passed in 68.55s` |
| Fast families (`-m "not production"`) | `60 passed, 16 deselected in 0.74s` |
| Production family (`-m production`) | `16 passed, 60 deselected in 68.66s` |
| Exception-object-graph tests × 20 consecutive | `7 passed, 69 deselected` on **all 20**; ALL 20 GREEN |
| Strict-ID validation tests × 20 consecutive | `22 passed, 54 deselected` on **all 20**; ALL 20 GREEN |
| First-64 T-11/T-16 production proofs | `2 passed, 74 deselected in 12.43s` |
| Safe broader suite (test-29 deselected), run 1 | `137 passed, 1 deselected in 85.12s` |
| Safe broader suite (test-29 deselected), run 2 | `137 passed, 1 deselected in 86.83s` |
| `attempts/` count after every run above | `70` — unchanged |
| `ruff check --select F,E9` on all three files | `All checks passed!` |
| `python -c "import ast; ast.parse(...)"` on all three files | `parse OK` ×3 |

Test-count reconciliation: Increment A grew 42 → 76 (+34), all from the five
fixes — Fix A-1 +11 (`D9`×3, `D10`, `D11`, `D12`, `D20`, `E13`, plus the
`E4s`/`E5s` split is counted under A-3), Fix A-2 +22 (`D13`×13, `D14`, `D15`,
`D16`×6, `D17`), Fix A-3 +2 net (`E4`/`E5` retargeted, `E4s`/`E5s` added), Fix
A-5 +2 (`D18`, `D19`). Repository total is 138 = 62 pre-existing + 76; the safe
command runs 137 and deselects test 29.

The `UP***`/`I001` ruff style codes remain unfixed, deliberately and as before:
the accepted production runner `scripts/p2a/run_p2a_regionlive_rebuild.py`
carries the identical profile, and these files match the surrounding code's
`typing.Dict/List/Tuple` idiom.

---

## 15. Verbatim proof results

**Every command below was executed exactly as printed, in PowerShell, from
`C:\Users\hisham\Repo\MNL`.** All are read-only. None creates a file. None
requires a source edit. Expected output is what was actually observed.

### P-1 — state, commit, gitlink, nested cleanliness

```powershell
cd C:\Users\hisham\Repo\MNL
git rev-parse HEAD
git ls-tree HEAD dclaborsupply-monorepo
git -C dclaborsupply-monorepo rev-parse HEAD
git -C dclaborsupply-monorepo status --porcelain --untracked-files=all
git status --porcelain --untracked-files=all
```

Expected:

```text
b5169293b647dda3e07070c678f8d46d33b1bf89
160000 commit 27756a06ea189339aa82915ed2124628afed20eb	dclaborsupply-monorepo
27756a06ea189339aa82915ed2124628afed20eb
(no output - nested worktree clean)
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_refix_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementA_review_v1.md
?? scripts/p2a/p2a_phase5_score_stream.py
?? tests/p2a/conftest.py
?? tests/p2a/test_p2a_phase5_score_stream.py
```

Note the four test-29 files are **absent** — that is the ST-1 fix.

### P-2 — accepted bundles rehash (manifest-excluded, separate per phase)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import hashlib,os;s=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();b=lambda d,m:hashlib.sha256(('\n'.join(f'{n}:{s(os.path.join(d,n))}' for n in sorted(os.listdir(d)) if n!=m)).encode('utf-8')).hexdigest();print('phase3',b('outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete','phase3_manifest.json'));print('phase4',b('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete','phase4_manifest.json'))"
```

Observed:

```text
phase3 2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b
phase4 5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3
```

### P-3 — the complete Increment-A test set

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider
```

Observed: `76 passed in 69.01s (0:01:09)`

### P-4 — fast families only (sub-second)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider -m "not production"
```

Observed: `60 passed, 16 deselected in 0.74s`

### P-5 — production family (real loader, likelihood, reducer)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider -m production
```

Observed: `16 passed, 60 deselected in 68.66s (0:01:08)`

### P-6 — Fix 1: failure-path exception-object-graph

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider -k "test_D9_ or test_D10_ or test_D11_ or test_D12_ or test_D20_"
```

Observed: `7 passed, 69 deselected in 0.41s`

Non-vacuity is inside the selection: `test_D10` builds exceptions that *do* retain
the block through a frame local, `__context__`, `__cause__`, an attribute payload
and raw bytes, and asserts each is detected; `test_D20` asserts the traversal is
deterministic and reaches the reducer's own `_m37`.

### P-7 — Fix 2: strict canonical ID validation

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider -k "test_D13_ or test_D14_ or test_D15_ or test_D16_ or test_D17_"
```

Observed: `22 passed, 54 deselected in 0.44s`

`test_D14` is the forged-`.5` demonstration; `test_D13` covers all 13 rejection
classes.

### P-8 — Fix 3: frozen first-64 T-11 and T-16

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_score_stream.py -q -p no:cacheprovider -k "test_E4_ or test_E5_"
```

Observed: `2 passed, 74 deselected in 12.04s`

### P-9 — Fix 3: the first-64 numbers themselves

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import sys;sys.path.insert(0,'scripts/p2a');import numpy as np,p2a_phase5_score_stream as S;b=S.build_production_binding(household_limit=64);g=lambda bs,m='jacfwd':np.vstack([S.compute_batch_scores(b,x,mode=m) for x in b.order.batches(bs)]);f16,f64,r64=g(16),g(64),g(64,'jacrev');mx=float(np.max(np.abs(f64)));print('max|S| first64            ',repr(mx));print('T-11 bar  1e-12*max|S|    ',repr(1e-12*mx));print('T-11 dev  batch(16 vs 64) ',repr(float(np.max(np.abs(f16-f64)))));print('T-16 bar  1e-10*max|S|    ',repr(1e-10*mx));print('T-16 dev  jacfwd vs jacrev',repr(float(np.max(np.abs(f64-r64)))))"
```

Observed:

```text
max|S| first64             30.23468094208269
T-11 bar  1e-12*max|S|     3.023468094208269e-11
T-11 dev  batch(16 vs 64)  0.0
T-16 bar  1e-10*max|S|     3.023468094208269e-09
T-16 dev  jacfwd vs jacrev 7.105427357601002e-15
```

### P-10 — Fix 5: the safe full-suite command

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "not test_29_subprocess_dry_run_never_optimizes"
```

Observed: `137 passed, 1 deselected in 91.57s (0:01:31)`

### P-11 — Fix 5: the guard blocks an unsafe invocation

```powershell
cd C:\Users\hisham\Repo\MNL
& .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "test_29_subprocess_dry_run_never_optimizes"
(Get-ChildItem outputs\p2a_singles2016\region_live_v1\phase3_estimation_v1\attempts).Count
```

Observed: `137 deselected, 1 error in 0.42s`, then `70`. The error is raised in
**setup**, so the Phase-3 subprocess never runs and no attempt directory is
created. Before this fix, the same invocation appended one.

### P-12 — no row-level score artifact anywhere

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import numpy as np;from pathlib import Path;hits=[];[hits.append((f'shape {a.shape}',str(p))) for p in Path('.').rglob('*.npy') if not {'.git','.venv','__pycache__'} & set(p.parts) for a in [np.load(p,mmap_mode='r',allow_pickle=False)] if a.ndim==2 and a.shape[1]==37 and a.shape[0]>37];named=[str(p) for p in Path('.').rglob('*') if p.is_file() and not {'.git','.venv','__pycache__'} & set(p.parts) and 'score' in p.name.lower() and p.suffix in {'.npy','.csv','.parquet','.npz','.bin'}];print('37-column .npy arrays :',hits if hits else 'NONE');print('score-named artifacts :',named if named else 'NONE')"
```

Observed:

```text
37-column .npy arrays : NONE
score-named artifacts : NONE
```

---

## 16. Artifact and repository integrity

### 16.1 Accepted bundles

Both rehash exactly, manifest-excluded, separate canonical hash per phase — P-2.
Phase-3 `2cf23764…`, Phase-4 `5484886985…`. No bundle member was read for
modification or written.

### 16.2 Nested package

HEAD `27756a06ea189339aa82915ed2124628afed20eb` = MNL gitlink; worktree clean
under `--untracked-files=all`. Unchanged from task start.

### 16.3 Whitespace / diff hygiene

`git diff --check` exits 0.

### 16.4 Frozen documents

| File | Task-start SHA-256 | Now | Verdict |
| --- | --- | --- | --- |
| `FR_P2a_streaming_incrementA_report_v1.md` | `ed59e8b3dcee74d86e09e14772705539449fe0da548e601629fa849be586b1fa` | identical | byte-identical |
| `FR_P2a_streaming_incrementA_review_v1.md` | `4ab8f808ca222ccee23fa9aaaaa784613c9fdf221c944b274e03720c6259b9f1` | identical | byte-identical |

Verified with a byte comparison against the task-start snapshot, per addendum (d).

### 16.5 No Increment-B or Increment-C code

A grep of the module for `cho_factor|cho_solve|np.linalg.inv|pinv|covariance|
sandwich|wald|hessian_free|se_robust|chi2` returns matches on **docstring lines
only** (lines 26 and 29, which say these are out of scope). No bread is loaded,
no covariance formed, no runner, transaction, staging directory, manifest or
allowlist exists. No `complete/` was created. No full-population run occurred —
the largest evaluation in this task was the design-prescribed first-64 slice.

### 16.6 Attempt files

`attempts/` holds 70 entries, its committed count, verified after every test run
including both safe full-suite runs. No unexpected attempt file remains.

---

## 17. Residual warnings

1. **Foreign exception messages are suppressed** at the three stream boundaries.
   Only the exception type and the boundary code survive. This is a deliberate
   trade of debuggability for the no-leak guarantee, since a NumPy/JAX/pandas
   message can embed array contents. Increment C should assume that a failure
   inside the stream will be diagnosable by type and canonical position, not by
   the original message, and should size its console-log expectations accordingly.
2. **Frame-local release is a property of this module's boundaries, not of
   Python.** A *caller* that keeps its own reference to a score block, and whose
   frame is part of the traceback, will still hold it — the module cannot and
   should not reach into a caller's frame. Increment C's runner must apply the
   same `finally`-release discipline at its own boundary; §7.2 is the pattern.
3. **The digest remains scoped to `(encoding, batch size, AD mode)`** — upheld
   ruling R-32b, unchanged by this refix. Increment C's reproduction gate must
   pin the whole tuple and refuse cross-tuple comparison. Measured again here:
   T-11 first-64 batch(16 vs 64) deviation is exactly `0.0`, but a 1-ULP
   difference at other batch shapes was measured during Increment A.
4. **The test-29 guard changes the behaviour of an accepted test file's
   execution.** It never modifies that file, and `MNL_ALLOW_TEST29=1` restores the
   original behaviour, but a future operator who expects a bare `pytest` to run
   test 29 will see an error instead. This is intentional and documented in
   `conftest.py`.
5. **`jax_enable_x64` is process-global and lazily set** — carried forward
   unchanged from report v1 §8. The binding activates it eagerly and refuses to
   proceed otherwise; Increment C's runner must record it in the manifest (T-15).
6. **Full-population wall time and peak memory remain `UNKNOWN`.** No
   1,555-household run is authorized in Increment A. Each batch traces and
   compiles a fresh likelihood, so the dry-run cost must be measured in
   Increment C.
7. **The all-1,555 score-identity gate (T-1/T-4) is still not exercised**, and
   correctly so: `Σ_g s_g = −∇negLL` is meaningless on a bounded prefix. It is an
   Increment-B/C obligation consuming this increment's aggregate vector.

---

## 18. Whether Review A v2 may begin

**Yes.**

All five authorized fixes are complete and independently provable. The exact
expected working set was restored inside this task and re-verified after every
test run. Both accepted bundles rehash. The nested package is clean and unchanged
at the pinned gitlink. Report v1 and Review A v1 are byte-identical. No commit was
made; the commit gate remains closed until Review A v2 returns `APPROVE`.

Review A v2 should execute §15 P-1 … P-12 verbatim and confirm:

* NP-1 closed — traverse a failed reducer call's complete exception graph;
* DG-1 closed — a forged `.5` batch cannot hash as its truncated integers;
* T16-1 closed — T-16 evidence is the first 64 canonical households;
* PR-1 closed — every proof runs verbatim, read-only, with correct counts;
* ST-1 closed — the four files are gone and the guard prevents recurrence;
* no design, package, estimand, architecture or scope expansion (§12, §13, §16.5).

The reviewer should also independently re-derive the §7.3 determinism finding, as
it is the one place where a defect in the *test* rather than the *implementation*
could still hide a false green.

---

## 19. Immediate next action

1. **Launch Review A v2** — fresh Codex session, strongest available review model,
   maximum reasoning, read-only, at MNL `b5169293b647dda3e07070c678f8d46d33b1bf89`.
   Scope: the original Increment-A contract, the five fixes, exact-state
   integrity, no scope expansion. Verdict is binary `APPROVE` / `REJECT`; a v2
   `REJECT` is an E2 halt (deputy decision §5).
2. **Give the reviewer this report as the PROOFS packet**, noting that it
   supersedes report v1 §5 while report v1 itself stays byte-identical.
3. **On `APPROVE` only**: commit the reviewed implementation, tests, report v1,
   this refix report and Review A v2; require both worktrees clean; update the
   JMP-M05C ledger; then authorize Increment B (deputy decision §6).
4. **Carry into Increment C** the four forward-looking items of §17: the
   `(encoding, batch size, AD mode)` reproduction tuple, the `finally`-release
   pattern at the runner boundary, T-15 manifest recording of `jax_enable_x64`,
   and measurement of full-population wall time and peak memory.

**FINAL VERDICT: READY FOR REVIEW A V2**
