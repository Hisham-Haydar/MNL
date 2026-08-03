# FR P2a — JMP-M05C Streaming Inference — Increment C implementation report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Increment:** C — dry-run-only runner, aggregate-only transaction, fresh-process reproduction (charter §4-C)
**Mode:** implementation + tests only. No commit. No full-population run.
**Date:** 2026-08-03
**MNL HEAD (unchanged throughout):** `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Increment verdict

**READY FOR REVIEW C**

Every charter §4-C deliverable is implemented on top of the committed Increment-A
reducer and Increment-B inference objects, which remain the only compute routes.
45 Increment-C tests pass; the full repository suite is **270 passed, 1
deselected**.

The blocking scope the proportionality rule fixes for this increment is
discharged as follows:

| Blocking item | Evidence |
| --- | --- |
| actual production runner | a real end-to-end bounded dry run publishes 19 allowlisted members (§5) |
| fresh-process aggregate reproduction | T-12S passes in a **real subprocess**, digest bitwise identical, all deviations exactly `0.0` (§6) |
| aggregate-only transaction | closed allowlist enforced pre-publication; per-file fsync then atomic rename (§5) |
| STOPPED truthfulness | three injected-failure stages each publish a `.STOPPED` attempt whose inventory equals what is on disk (§5.3) |
| no `complete/` | structurally absent — the transaction has no `complete` attribute and the source contains no such write-side path (§5.2) |
| no row-level persistence | T-23S static + behavioural; no 2-D household-score array on any path (§6.2) |
| accepted-artifact / revision binding | verified before any computation; five anchors each proved load-bearing (§4) |
| numerical regression | Increment-A and Increment-B suites unchanged and green (§8) |

Nothing outside that scope was built: no import-surface counting, no capability
tokens, no general security machinery.

**The full-population dry run was not executed**, by construction. It is
config-reachable and refused, through exactly the addendum §8 mechanism: the
Increment-C review approval it requires does not exist yet (§7 PROOF-11).

---

## 2. Starting state

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36` | identical | PASS |
| MNL worktree | fully clean | clean (`--untracked-files=all`) | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean | PASS |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | identical | PASS |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | identical | PASS |

HEAD `c2cf6a3 feat(p2a): covariance and inference objects - increment B closed
under proportionality rule` is the committed Increment-B state.

---

## 3. Deliverable inventory with SHA-256

Three new, untracked files. Nothing existing was modified.

| Path | SHA-256 | Bytes | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/run_p2a_phase5_inference.py](scripts/p2a/run_p2a_phase5_inference.py) | `f283f1ac3d5664a42d2276cc142aa665a1c7aebc5b82cefb4cba042816c35ed0` | 49,416 | 1,058 |
| [scripts/p2a/configs/p2a_phase5_inference_v1.yaml](scripts/p2a/configs/p2a_phase5_inference_v1.yaml) | `7ca3428a783b9b66bd20dd9a40a2c2ebce02d39e9867ee069de2be9c49d54f0a` | 3,574 | 71 |
| [tests/p2a/test_p2a_phase5_runner.py](tests/p2a/test_p2a_phase5_runner.py) | `01ce44cbdec49ed98be6b1526c2813534ff930c2294b157155bafd54039c3f7c` | 29,290 | 644 |

The config SHA-256 is the value the runner is **digest-bound** to
(`CONFIG_SHA256`): it recomputes the file's hash at start-up and refuses to run
if it differs, so editing the configuration is a reviewable change rather than a
silent one.

### 3.1 Public surface

| Object | Role |
| --- | --- |
| `load_config` | canonical YAML + digest binding; refuses any non-dry-run mode |
| `activate_float64_or_refuse` | R-32c: eager `_load_jax()` then hard refusal |
| `capture_environment` | design v4 §18.5 environment mandate |
| `verify_accepted_binding` | HEAD, gitlink, both bundles, bread, theta, spec, config |
| `verify_dry_run_authorization` | the addendum §8 full-run gate |
| `Phase5Transaction` | lock, staging, allowlist, fsync + atomic rename, `attempts/` only |
| `execute_dry_run` | the single execution path |
| `run_repro_subprocess`, `compare_reproduction` | T-12S |
| `gate_T23S_no_row_persistence`, `gate_score_identity` | T-23S and addendum §5 |
| `main` / `build_parser` | the single CLI entry |

---

## 4. Design conformance map

| # | Requirement | Where implemented | Governing section |
| --- | --- | --- | --- |
| 1 | Dry-run-only runner: config-driven, digest-bound; eager float64 with hard refusal; environment logging; single CLI; no real-run pathway | `load_config` (mode + `real_run_supported` asserted), `CONFIG_SHA256`, `activate_float64_or_refuse`, `capture_environment`, one `main()`; `test_L3` proves no real-run function or flag exists | charter §4-C; R-32c; design v4 §18.5 |
| 2 | Aggregate-only attempt transaction: unique dir, allowlisted members only, `ArtifactRecord` manifest with `inference_grade`, fsync + atomic rename, never `complete/` | `Phase5Transaction`; `ALLOWED_ARTIFACTS`; `enforce_allowlist()` before publication; `_fsync_file` + `os.replace`; no `complete` attribute exists | addendum §3, §8; R-37a |
| 3 | T-12S fresh-process reproduction at the frozen tuple; digest, score sum, `M_37`, `M_35`, order fingerprint, count, batch size, environment; no second score file | `run_repro_subprocess` (real subprocess, `--repro-json`, prints between sentinels), `compare_reproduction` (refuses cross-tuple) | addendum §4, §7; R-32b |
| 4 | T-23S: member set free of row-level artifacts, no restricted store, no temporary batch after success or failure, static + behavioural, truthful in-memory reporting | `gate_T23S_no_row_persistence`; family R | addendum §6 |
| 5 | STOPPED truthfulness with member inventory and gate register | `execute_dry_run` finalisation; `.STOPPED` publication; family S | addendum §8 |
| 6 | Score identity from the **streamed** aggregate against `phase4_diagnostics.json → gradient_free` | `gate_score_identity`, `atol=rtol=1e-8` | addendum §5; R-37b |
| 7 | Accepted-artifact / revision binding verified before any computation | `verify_accepted_binding`, called before the parameter map is even loaded | design v4 §18.2 |
| 8 | Bounded-subset integration under a pytest tmp root; T-12S in a real subprocess; T-23S static+behavioural; STOPPED on injection; full run refused | families P, Q, R, S, N | charter §5 |

### 4.1 Compute-route discipline

The runner recomputes nothing. Scores come from `ss.run_score_stream`; the bread,
gradients, covariances, Wald battery, parameter table and every T/W gate come
from the committed Increment-B API; every artifact write is delegated to
`ib.write_matrix` / `ib.write_table` / `ib.write_score_aggregate_summary`, which
refuse row-level and id-paired content by construction. The runner's own writers
are text/JSON only — `test_R1` proves this statically.

### 4.2 Deliberate non-scope

No import-surface counting, capability tokens, or general software-security
machinery. No real-run pathway. No `complete/`. No restricted store. No change to
any design formula, constant, schema, parameter map, or to Increments A/B.

---

## 5. Transaction and STOPPED evidence

### 5.1 A real bounded dry run

`--households 24`, batch 128, `jacfwd`, into a scratch root. Result:
`PHASE_5_DRY_RUN_COMPLETE`, published to
`attempts/<id>_PHASE_5_DRY_RUN_COMPLETE`, **19 members**, bundle SHA-256
`b704d10dc753e6cde300d60a4f770ea6d7ca5e0b2acd93b89428208d3e615bbc`.

Members (all in the closed allowlist): `score_aggregate_summary.json`,
`score_sum_free37.csv`, `meat_free37.{npy,csv}`, `meat_interior35.{npy,csv}`,
`phase5_covariance_model.{npy,csv}`, `phase5_covariance_robust.{npy,csv}`,
`phase5_correlation_{model,robust}.csv`, `phase5_regional_covariance.csv`,
`phase5_standard_errors.csv`, `phase5_parameter_table.csv`,
`phase5_regional_tests.csv`, `phase5_diagnostics.json`, `phase5_manifest.json`,
`phase5_console.log`.

Gate register: T-5, T-6, T-7, T-8, T-9, T-10, T-14, T-17, T-18, T-19, T-22,
T-12S, T-23S all **PASS** (gating); W-2, W-3, W-4, W-5 pass and W-1 flags
(warning-tier, `subset-diagnostic` scale, non-gating — the Increment-B behaviour,
unchanged). `gating_failures == []`.

The manifest records the accepted binding (`verified: true`, gitlink == nested
HEAD, bread and theta hashes), the config digest, the environment (Python 3.12.2,
NumPy 2.3.5, SciPy 1.16.2, JAX/jaxlib 0.10.1, `Windows-2022Server-10.0.20348-SP0`,
all seven thread/XLA variables captured as `null`), `float64_activation:
{jax_enable_x64: true}`, the reproduction tuple, and one `ArtifactRecord` per
artifact each carrying `inference_grade: subset-diagnostic` (R-37a). The bundle
hash covers every member except the manifest and recomputes exactly.

### 5.2 `complete/` is structurally absent

Not conditional, not guarded — absent:

* `Phase5Transaction` has no `complete`, `complete_exists` or `success_status`
  attribute (`test_L4` asserts all three);
* `finish()` publishes only under `self.attempts`; its AST contains no
  `complete` attribute access (`test_L5`);
* the source contains no `self.complete`, no `/ "complete"`, no `'complete'`
  write-side construction (`test_L4`);
* after every run in this task, `complete/` does not exist and the canonical
  production root `outputs/…/phase5_inference_v1` does not exist at all.

### 5.3 STOPPED truthfulness

Three injected failure stages, each a real run into a tmp root:

| Injected stage | Status | Members published | `transient_batch_existed_in_memory_only` | `transient_batch_serialized` |
| --- | --- | --- | --- | --- |
| `binding` (before compute) | `STOPPED` | 3 runner-owned only | `false` | `false` |
| `post_stream` | `STOPPED` | 3 runner-owned only | **`true`** | `false` |
| `post_gates` | `STOPPED` | 3 runner-owned only | `false` | `false` |

Each `.STOPPED` attempt carries a `stop` record naming halt, stage and reason;
a gate register including T-23S evaluated **on the failure path**; and a
`member_inventory` asserted equal to what is actually on disk. The `post_stream`
case is the important one: it reports truthfully that a transient batch existed
in memory, and equally truthfully that it was never serialized — the report is a
boolean, never the content. `test_S1` asserts the boolean matches the injected
stage exactly, so a runner that always said `false` (or always `true`) would fail.

### 5.4 Write semantics

`atomic_write_text` / `atomic_write_json` write to `<name>.tmp`, `flush()`,
`os.fsync()`, then `os.replace()` — same volume, atomic. Before publication
`finish()` fsyncs every staged file and the staging directory, then renames the
directory into `attempts/`. `_fsync_file` opens `"rb+"` rather than `"rb"`
because Windows refuses `os.fsync` on a read-only handle with `EBADF`; `"rb+"`
gives a writable handle without truncating. Directory fsync is skipped on
Windows, which has no directory file descriptor — recorded in §9.

---

## 6. T-12S and T-23S evidence

### 6.1 T-12S — fresh-process aggregate reproduction

The parent streams the aggregates; a **real subprocess** (`sys.executable`,
`--repro-json`) re-derives them from the accepted sources in a fresh interpreter
and prints only an aggregate fingerprint between sentinels on stdout. The parent
parses and compares.

| Compared | Rule | Observed |
| --- | --- | --- |
| `score_stream_sha256` | exact | `a15cebb8a2ee1eff…` parent == child |
| `order_sha256`, `free_names_sha256`, `interior_names_sha256` | exact | equal |
| `n_households`, `batch_size`, `n_batches`, `idhh_encoding`, `dtype`, `byte_order` | exact | equal |
| `score_sum_free37` | `atol=rtol=0` | max abs dev `0.0` |
| `meat_free37` | `atol=rtol=0` | max abs dev `0.0` |
| `meat_interior35` | `atol=rtol=0` | max abs dev `0.0` |

**No second score file exists at any point.** The child writes nothing: `test_Q2`
runs it from an empty temp cwd and asserts the tree is still empty afterwards,
and that the returned object's key set is exactly the thirteen aggregate fields —
no row-level payload, `score_sum_free37` of length 37, both meats square.

**Cross-tuple comparison is refused, not reported as a mismatch** (R-32b): the
digest is only defined within the frozen `(int64_le, 128, jacfwd)` tuple, so a
differing encoding or batch size raises rather than returning `passed=False`
(`test_Q3`). `test_Q4` proves the gate is not vacuous: a changed digest, and a
`1e-9` drift in one score-sum component, each fail it.

### 6.2 T-23S — no row-level score persistence

Five conditions, each checked and each individually falsifiable:

| Condition | Mechanism | Non-vacuity proof |
| --- | --- | --- |
| member set allowlisted | closed union of Increment-B's 16 + 3 runner-owned | `test_R4` plants `phase5_scores_free.npy` → fails |
| no row-level score member | name check outside the aggregate set | `test_R4` |
| no row-level 2-D array | every published `.npy` loaded and shape-checked square and ∈ {37, 35} | `test_R3` plants a `(12, 37)` block → fails |
| no restricted-store member | name check | `test_R4` |
| no temporary batch remains | `.tmp` / `.batch` sweep of the attempt dir | `test_R3` plants a `.tmp` → fails |

Static: `test_R1` walks the runner AST and asserts no `save`/`savez`/`savetxt`/
`tofile`/`to_csv`/`to_parquet`/`to_pickle`/`to_hdf` call exists anywhere in it,
and that every builtin `open` uses a read mode or one of the two write-capable
modes (`"w"` for the atomic tmp writer, `"rb+"` for the fsync handle). `test_R2`
proves that scanner detects a planted `np.save`. Behavioural: `test_R6` inspects
the **published** attempt — every `.npy` is square and 37×37 or 35×35, the
summary carries no list longer than 37, and the recorded T-23S gate says
`transient_batch_serialized: false`.

### 6.3 Score identity (addendum §5)

Computed from the streamed aggregate against
`phase4_diagnostics.json → gradient_free` (R-37b) with `atol = rtol = 1e-8`.

On a bounded subset it is reported as **not applicable**, warning-tier, with
`observed.applicable = false` — the first-order condition is a whole-sample
property, and a prefix sum is nowhere near the accepted gradient. Reporting a
pass there would be a false green and reporting a fail would be a false red; the
gate becomes gating-tier only on the full population. `test_P4` asserts exactly
this on the bounded run.

---

## 7. Proofs (reviewer-runnable)

**Every command below was executed exactly as printed, in PowerShell, from
`C:\Users\hisham\Repo\MNL`.** All are read-only for the reviewer, create no
reviewer-owned file, and use the exact virtual-environment interpreter. Tests
that write do so under pytest's `tmp_path`. `-p no:cacheprovider` prevents a
`.pytest_cache` write. Full-suite commands carry the test-29 deselection, which
the conftest guard also enforces.

### PROOF-1 — starting state and worktrees

```powershell
cd C:\Users\hisham\Repo\MNL
git rev-parse HEAD
git status --porcelain --untracked-files=all
git ls-tree HEAD dclaborsupply-monorepo
git -C dclaborsupply-monorepo rev-parse HEAD
git -C dclaborsupply-monorepo status --porcelain --untracked-files=all
```

Expected:

```text
c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36
?? docs/France_case/P2a/FR_P2a_streaming_incrementC_report_v1.md
?? scripts/p2a/configs/p2a_phase5_inference_v1.yaml
?? scripts/p2a/run_p2a_phase5_inference.py
?? tests/p2a/test_p2a_phase5_runner.py
160000 commit 27756a06ea189339aa82915ed2124628afed20eb	dclaborsupply-monorepo
27756a06ea189339aa82915ed2124628afed20eb
(no output - nested worktree clean)
```

### PROOF-2 — accepted bundles, bread, theta, config digest

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import hashlib,os,sys;sys.path.insert(0,'scripts/p2a');import p2a_phase5_inference as ib,run_p2a_phase5_inference as rc;s=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();b=lambda d,m:hashlib.sha256(('\n'.join(f'{n}:{s(os.path.join(d,n))}' for n in sorted(os.listdir(d)) if n!=m)).encode('utf-8')).hexdigest();print('phase3',b('outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete','phase3_manifest.json'));print('phase4',b('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete','phase4_manifest.json'));print('bread ',s('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/hessian_free.npy'));print('theta ',ib.accepted_theta_sha256());print('config',s(rc.CONFIG_REL),'==',rc.CONFIG_SHA256)"
```

Observed:

```text
phase3 2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b
phase4 5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3
bread  e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061
theta  c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d
config 7ca3428a783b9b66bd20dd9a40a2c2ebce02d39e9867ee069de2be9c49d54f0a == 7ca3428a783b9b66bd20dd9a40a2c2ebce02d39e9867ee069de2be9c49d54f0a
```

### PROOF-3 — the complete Increment-C test set

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider
```

Observed: `45 passed in 25.64s`

### PROOF-4 — fast families only

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -m "not production"
```

Observed: `33 passed, 12 deselected in 2.50s`

### PROOF-5 — production family (real end-to-end runs)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -m production
```

Observed: `12 passed, 33 deselected in 23.49s`

### PROOF-6 — dry-run authorization refusals (family N)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -k "test_N1 or test_N2 or test_N3 or test_N4 or test_N5 or test_N6"
```

Observed: `9 passed, 36 deselected in 1.78s`

Failure demonstrations inside the selection: each authorization argument omitted
in turn; the approval file absent (`test_N3`, with git cleanliness stubbed so the
refusal demonstrated is the review-file arm specifically); a review present but
carrying `REJECT` (`test_N4`); and the two CLI-level refusals with exit code 2.

### PROOF-7 — T-12S fresh-process reproduction (family Q)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -k "test_Q1 or test_Q2 or test_Q3 or test_Q4"
```

Observed: `4 passed, 41 deselected in 12.64s`

### PROOF-8 — T-23S no-row-level persistence (family R)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -k "test_R1 or test_R2 or test_R3 or test_R4 or test_R5 or test_R6"
```

Observed: `6 passed, 39 deselected in 9.42s`

### PROOF-9 — STOPPED truthfulness (family S)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_runner.py -q -p no:cacheprovider -k "test_S1 or test_S2"
```

Observed: `4 passed, 41 deselected in 7.33s`

### PROOF-10 — the safe full repository suite

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "not test_29_subprocess_dry_run_never_optimizes"
```

Observed: `270 passed, 1 deselected in 116.68s (0:01:56)`

### PROOF-11 — the full-population dry run is reachable and REFUSED

```powershell
cd C:\Users\hisham\Repo\MNL
& .\.venv\Scripts\python.exe scripts\p2a\run_p2a_phase5_inference.py
Write-Output "exit=$LASTEXITCODE"
Test-Path docs\France_case\P2a\FR_P2a_streaming_incrementC_review_v1.md
Test-Path outputs\p2a_singles2016\region_live_v1\phase5_inference_v1
```

Observed:

```text
REFUSED: [HP-AUTH] dry-run-authorization: the full-population dry run requires --execute-dry-run
exit=2
False
False
```

The approval document does not exist, so no argument combination can authorize
the run. This is the addendum §8 mechanism, not an omission.

### PROOF-12 — a bounded subset cannot touch the canonical root

```powershell
cd C:\Users\hisham\Repo\MNL
& .\.venv\Scripts\python.exe scripts\p2a\run_p2a_phase5_inference.py --households 8 --out outputs/p2a_singles2016/region_live_v1/phase5_inference_v1
Write-Output "exit=$LASTEXITCODE"
```

Observed:

```text
REFUSED: [HP-AUTH] output-root: a bounded subset may not be written into the canonical production root; pass an explicit --out
exit=2
```

**Failure demonstration for the whole packet.** Substituting the runner, reducer
or covariance builder invalidates every test above: families P/Q/S call
`rc.execute_dry_run` and `rc.run_repro_subprocess` directly, which in turn call
the committed `ss.run_score_stream` and `ib.*` objects. The only patched
quantities are the household subset size and the output root.

---

## 8. Test results

```text
Increment-C set                            45 passed in 25.23s
  fast (-m "not production")               33 passed, 12 deselected in 2.50s
  production (-m production)               12 passed, 33 deselected in 23.49s
full repository, test-29 deselected       270 passed, 1 deselected in 108.35s
Phase-3 attempts/ count, before and after                              70
canonical phase5_inference_v1 root                                 ABSENT
ruff check --select F,E9 (all three files)               All checks passed!
git diff --check                                                   exit 0
```

Repository total 270 = 225 pre-existing + 45 Increment-C. Family breakdown:
L 6, M 7, N 9, O 4, P 5, Q 4, R 6, S 4.

### 8.1 Regression on Increments A and B

Neither committed module was modified; `git status` for
`p2a_phase5_score_stream.py`, `p2a_phase5_inference.py`,
`test_p2a_phase5_score_stream.py`, `test_p2a_phase5_inference.py` and
`conftest.py` is empty. Their suites run inside PROOF-10 and are green. The
T-12S digest `a15cebb8a2ee1eff…` for the first-24 subset at batch 128 / `jacfwd`
is the same value Increment A recorded for that tuple, so the reducer's output is
unchanged by anything in this increment.

---

## 9. Residual limitations and debt

1. **The full-population dry run has not been executed.** Wall time and peak
   memory for 1,555 households remain `UNKNOWN` and must be measured in that
   separately authorized run. The bounded runs here are 12–24 households.
2. **Directory `fsync` is skipped on Windows**, which exposes no directory file
   descriptor. Per-file `fsync` and the atomic `os.replace` both run. On a POSIX
   host the directory fsync also runs. Recorded rather than worked around.
3. **The score-identity gate is warning-tier on a subset** and becomes gating
   only at the full population (§6.3). A reviewer should confirm that the first
   full run reports `observed.applicable = true` and a gating pass.
4. **W-1 flags on bounded runs** (`subset-diagnostic` scale), unchanged
   Increment-B behaviour, warning-tier, non-gating. It should not flag at full
   population; that is a thing to check in the dry run, not here.
5. **`inject_failure` is a test seam** on `execute_dry_run`. It can only raise a
   controlled `StopRun` at one of three named stages; it cannot make a failing
   run succeed and does not alter any computation. It is reachable from the CLI
   via `--inject-failure` — deliberately, so a reviewer can reproduce the STOPPED
   evidence without editing source.
6. **Non-`StopRun` exceptions are sanitized** into `HP-INTERNAL` with the type
   name only, message suppressed, mirroring the Increment-A foreign-exception
   policy. This costs debugging detail to guarantee no household quantity reaches
   a record; the type and stage remain.
7. **The lock is advisory within one host.** It is an `O_EXCL` create; a stale
   lock after a hard kill must be removed manually. Same behaviour as the
   accepted Phase-3/Phase-4 transaction.
8. **`.staging/` remains as an empty directory** after a run; the attempt
   directory itself is renamed out of it. Cosmetic, no member consequence.

---

## 10. Immediate next action

1. **Independent Codex review C** of `scripts/p2a/run_p2a_phase5_inference.py`,
   `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` and
   `tests/p2a/test_p2a_phase5_runner.py` at MNL
   `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`, executing PROOF-1 … PROOF-12
   verbatim. Under the proportionality rule the blocking scope is exactly:
   actual production runner, fresh-process aggregate reproduction,
   aggregate-only transaction, STOPPED truthfulness, no `complete/`, no
   row-level persistence, accepted-artifact/revision binding, numerical
   regression. Import-surface counting, capability tokens and general security
   hardening are out of scope; other observations are nonblocking technical debt.
2. **On `APPROVE`**: commit the exact reviewed state with both worktrees clean,
   update the JMP-M05C ledger, then create the Increment-C approval document at
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md`. That file's
   existence, SHA-256 and exact `**FINAL VERDICT: APPROVE**` line are what unlock
   the single full-population dry run:

   ```powershell
   & .\.venv\Scripts\python.exe scripts\p2a\run_p2a_phase5_inference.py --execute-dry-run `
     --expected-mnl-head <commit> --expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb `
     --approved-review docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md `
     --approved-review-sha256 <sha256>
   ```

3. **Audit the dry run** against §9 items 1, 3 and 4: record wall time and peak
   memory, confirm the score identity is gating and passes, and confirm W-1's
   behaviour at full scale. Then return to the deputy programme director for
   production-run authorization per charter §9.
4. **Do not create `complete/`** in that run or afterwards; promotion remains
   deputy-reserved and the runner has no code path for it.

**FINAL VERDICT: READY FOR REVIEW C**
