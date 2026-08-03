# FR P2a — JMP-M05C Streaming Inference — Increment C — Review C (final integrated) — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Increment:** C — dry-run-only runner, aggregate-only transaction, fresh-process reproduction
**Reviewer role:** final integrated independent reviewer under Goal-1 ruling R-47 (substituting for
Codex, quota-exhausted; substitution disclosed to the deputy). Read-only, fresh, independent of the
implementer session.
**Date:** 2026-08-03
**MNL HEAD reviewed:** `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`
**Nested `dclaborsupply-monorepo` HEAD / MNL gitlink:** `27756a06ea189339aa82915ed2124628afed20eb`
**Certification proportionality rule:** BINDING. Blocking scope is exactly the eight items in §3.

---

## 1. Review-C verdict

**APPROVE AFTER FIXES** — 5 required fixes, all documentation- and test-only. No behavioural
change is required, and no numerical result is re-opened.

All eight blocking-scope items pass on my own live execution. The implementation is correct on
every axis the proportionality rule fixes as blocking: the runner really runs, the fresh-process
reproduction is bitwise exact, the transaction is aggregate-only and allowlist-closed, STOPPED is
truthful and mutation-resistant, `complete/` is structurally absent, no row-level score array is
written on any path, every accepted anchor is load-bearing, and the committed Increments A and B
are unmodified with their numbers reproducing exactly.

The verdict is nevertheless not a clean APPROVE, for one reason that is squarely inside blocking
item 2 and two that surround it:

* the increment report's §6.1 states that `test_Q2` "runs it from an empty temp cwd and asserts the
  tree is still empty afterwards". **That is false.** `test_Q2` monkeypatches only the *parent's*
  cwd, while `run_repro_subprocess` pins the child's cwd to `repo_root`; the assertion it makes is
  therefore true no matter what the child writes. The shipped packet contains **no** test that can
  fail if the child writes a second score file. The *behaviour* is correct — I proved it
  independently in §5, PROOF-C4 — but that proof exists only in this review, not in the record
  being committed;
* §8's `ruff` line does not reproduce as printed;
* §10's next-action sequence, followed literally, makes the very run it authorizes refuse.

This programme's own precedent (Increment-B Review v1) treated non-reproducing evidentiary claims
as blocking-grade. I apply the same standard here, at the lowest tier that fits: the fixes are
cheap, mechanical, and touch nothing that was numerically certified.

Because this document is itself the dry-run authorization instrument, a non-APPROVE verdict here
must not authorize the full-population run. §4 verifies, by live execution against the shipped
parser, that it does not.

---

## 2. Scope and exact state

### 2.1 State verification (all PASS)

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36` | identical | PASS |
| MNL gitlink | `160000 commit 27756a06…` | identical | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| Nested worktree | clean | clean (`--untracked-files=all`) | PASS |
| MNL untracked set | exactly the four declared paths | exactly those four | PASS |
| MNL tracked modifications | none | none | PASS |
| Increment-C report SHA-256 | `461e8174…c6446b8827` | identical | PASS |
| `phase3_estimation_v1/attempts/` | 70 subdirectories | 70 | PASS |
| canonical `phase5_inference_v1` root | ABSENT | ABSENT (before, during and after) | PASS |

The four untracked paths, with the SHA-256 of each as reviewed:

| Path | SHA-256 |
| --- | --- |
| `scripts/p2a/run_p2a_phase5_inference.py` | `f283f1ac3d5664a42d2276cc142aa665a1c7aebc5b82cefb4cba042816c35ed0` |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | `7ca3428a783b9b66bd20dd9a40a2c2ebce02d39e9867ee069de2be9c49d54f0a` |
| `tests/p2a/test_p2a_phase5_runner.py` | `01ce44cbdec49ed98be6b1526c2813534ff930c2294b157155bafd54039c3f7c` |
| `docs/France_case/P2a/FR_P2a_streaming_incrementC_report_v1.md` | `461e81741096ecb4ce9097ebf28cf98c98e0ab9d00fa7874d212bc6e446b8827` |

Nothing else was found in the worktree. This review file is the fifth and only file I created.

### 2.2 What I did and did not do

I ran the report's twelve PROOFS, the full test suite, and fourteen independent adversarial probes
of my own (§5). I created no file other than this one, edited nothing, committed nothing, and did
**not** execute the full-population dry run. Every run I performed was a bounded subset (8–64
households) written to a system temporary directory outside the repository; I verified after each
that the repository worktree was byte-identical to its starting state.

---

## 3. Blocking-scope findings (items 1–8)

Every item below was verified by live execution, treating the increment report as unproven claims.

### Item 1 — actual production runner — **PASS**

A real bounded dry run through `rc.execute_dry_run` at 24 households, batch 128, `jacfwd`, into a
temporary output root, with the T-12S subprocess enabled:

| Observation | Result |
| --- | --- |
| status | `PHASE_5_DRY_RUN_COMPLETE` |
| publication target | `attempts/<id>_PHASE_5_DRY_RUN_COMPLETE` |
| members published | **19**, `set(members) ⊆ ALLOWED_ARTIFACTS`, and the allowlist is fully covered (no member missing) |
| gating gates | **13** — T-5, T-6, T-7, T-8, T-9, T-10, T-14, T-17, T-18, T-19, T-22, T-12S, T-23S |
| gating gates passed | all 13 |
| `gating_failures` | `[]` |
| warning gates | 6 — T-1/T-4 (not applicable), W-1 (flags), W-2, W-3, W-4, W-5 |
| `manifest.member_inventory` vs disk | equal |
| bundle SHA-256 | recomputes exactly from `artifact_hashes`; manifest excluded from its own hash |
| `complete/` | does not exist |
| lock | released; `.staging/` drained |
| `creates_complete` / `real_run_supported` | `false` / `false` |
| `inference_grade` on every `ArtifactRecord` | `subset-diagnostic` (R-37a) |
| every published `.npy` | square, ∈ {37×37, 35×35} |

The allowlist is the closed union: 16 Increment-B aggregate members + 3 runner-owned
(`phase5_diagnostics.json`, `phase5_manifest.json`, `phase5_console.log`) = 19, no duplicates.

### Item 2 — T-12S fresh-process aggregate reproduction — **PASS (behaviour); evidence defective**

A **real** subprocess (`sys.executable`, `--repro-json`, a fresh interpreter) at the frozen tuple
`(int64_le, 128, jacfwd)`:

| Compared | Rule | Observed |
| --- | --- | --- |
| `score_stream_sha256` | exact | parent `6644365fd69bae20…` == child `6644365fd69bae20…` |
| `order_sha256`, `free_names_sha256`, `interior_names_sha256` | exact | equal |
| `n_households`, `batch_size`, `n_batches`, `idhh_encoding`, `dtype`, `byte_order` | exact | equal |
| `score_sum_free37` | `atol = rtol = 0` | max abs dev **exactly `0.0`** |
| `meat_free37` | `atol = rtol = 0` | max abs dev **exactly `0.0`** |
| `meat_interior35` | `atol = rtol = 0` | max abs dev **exactly `0.0`** |

Gate identity `T-12S`, tier `gating`, `passed=True`. Non-vacuity confirmed independently: a changed
digest fails it, and a `1e-9` perturbation of one score-sum component fails it.

**Cross-tuple comparison RAISES**, it does not report a mismatch (R-32b): substituting
`batch_size=64` or `idhh_encoding=int32_le` on either side raises `StopRun` with "cross-tuple digest
comparison is refused". Verified for both dimensions. See §8 D6 for the one tuple dimension that
cannot be checked.

**The child writes nothing — verified, but not by the shipped test.** I ran the child directly with
its cwd set to a genuinely empty temporary directory: exit 0, the directory tree was still empty
afterwards, `git status --porcelain --untracked-files=all` was byte-identical before and after, and
the returned object's key set was exactly the thirteen aggregate fields (`score_sum_free37` length
37, both meats square). No second score file exists at any point.

The shipped `test_Q2` does **not** establish this. `monkeypatch.chdir(tmp_path)` changes the
parent's cwd only; `run_repro_subprocess` passes `cwd=str(repo_root)` to `subprocess.run`, so the
child never sees `tmp_path` and its assertion `sorted(p.name for p in tmp_path.rglob("*")) ==
before == []` is unfalsifiable. Report §6.1's description of that test is factually wrong. This is
required fix **F1/F2**.

### Item 3 — aggregate-only transaction — **PASS**

* **Closed allowlist enforced pre-publication.** `txn.enforce_allowlist()` is called after every
  write and before `txn.finish()`; it raises `HP-ALLOW` on any staged member outside
  `ALLOWED_ARTIFACTS`. Verified live: a planted `phase5_scores_free.npy` in staging produced
  `[HP-ALLOW] artifact-allowlist: non-allowlisted member(s) staged: ['phase5_scores_free.npy']`.
* **Per-file fsync then atomic rename.** `atomic_write_text` writes `<name>.tmp`, `flush()`,
  `os.fsync()`, `os.replace()`. `finish()` fsyncs every staged file, fsyncs the staging directory
  (POSIX only), then `os.replace()`s the staging directory into `attempts/` — same volume, atomic.
  `_fsync_file` opens `"rb+"` because Windows refuses `os.fsync` on a read-only handle; that is a
  correct workaround and does not truncate.
* **`attempts/` only.** The publication destination is unconditionally
  `self.attempts / f"{attempt_id}_{status}"`. The lock is `O_EXCL`; exclusion verified.

### Item 4 — STOPPED truthfulness — **PASS, mutation-tested**

Three injected failure stages, each a real bounded run into a temporary root:

| Injected stage | Status | Members | `…in_memory_only` | `…serialized` | inventory == disk |
| --- | --- | --- | --- | --- | --- |
| `binding` | `.STOPPED` | 3 runner-owned | `false` | `false` | yes |
| `post_stream` | `.STOPPED` | 3 runner-owned | **`true`** | `false` | yes |
| `post_gates` | `.STOPPED` | 3 runner-owned | `false` | `false` | yes |

Each `.STOPPED` attempt carries a `stop` record naming halt/stage/reason, a gate register that
includes T-23S evaluated on the failure path, and a `member_inventory` equal to what is on disk.

**The mandate's specific demand — that an always-false implementation must fail the shipped tests —
is satisfied.** I built two mutants of the runner in memory (no file was edited) and drove them
through `execute_dry_run`:

| Mutant | `post_stream`/`binding` reports | `test_S1` assertion | Outcome |
| --- | --- | --- | --- |
| transient flag forced **false** at `post_stream` | `false` | expects `True` | **test catches it** |
| transient flag forced **true** at entry | `true` at `binding` | expects `False` | **test catches it** |
| `member_inventory` drops the manifest | inventory ≠ disk | `sorted(inventory) == on_disk` | **test catches it** |

The booleans genuinely track the injected stage; the tests are not blind.

### Item 5 — no `complete/` — **PASS (structural absence, not a guard)**

Verified as absence, exactly as the mandate requires — not by finding a guard:

* **No attribute.** `Phase5Transaction` has no `complete`, `complete_exists`, `success_status` or
  `promote` attribute (checked on a live instance).
* **No AST write path.** A walk of the full module AST finds **zero** `ast.Attribute` named
  `complete`, zero `ast.Name` named `complete`, and zero string `ast.Constant` whose value is
  `complete` (or `/complete`).
* **No construction site.** Every directory-creating and directory-moving call in the module is
  enumerated: `self.root.mkdir`, `self.attempts.mkdir`, `self.staging_base.mkdir`,
  `(self.staging_base / attempt_id).mkdir`, `os.replace(self.staging, dest)` and the tmp-file
  `os.replace(tmp, path)`. None can produce a path component `complete`.
* `finish()` touches only the attributes `attempt_id`, `attempts`, `staging`, `is_file`, `iterdir`,
  `replace`.
* No run in this review produced a `complete/` directory, and the canonical production root was
  never created.

The only occurrences of the word in the system are **read-side**: the accepted Phase-3 and Phase-4
bundle directories, which legitimately live under `…/complete`.

### Item 6 — no row-level persistence (T-23S) — **PASS**

All five conditions are **individually falsifiable**; I falsified each one separately by driving
`gate_T23S_no_row_persistence` directly:

| # | Condition | Falsifying input | Gate result |
| --- | --- | --- | --- |
| baseline | — | a legitimate 37×37 `meat_free37.npy` | `passed=True` |
| 1 | `member_set_allowlisted` | a non-allowlisted member name | `False` |
| 2 | `no_row_level_score_member` | `phase5_scores_free.npy` | `False` |
| 3 | `no_row_level_2d_array` | a planted `(12, 37)` array | `False` |
| 4 | `no_restricted_store_member` | `restricted_store_ref.json` | `False` |
| 5 | `no_temporary_batch_remains` | a planted `.tmp` leftover | `False` |

**No code path writes a 2-D household-score array.** An AST walk of the runner finds no `save`,
`savez`, `savetxt`, `tofile`, `to_csv`, `to_parquet`, `to_pickle` or `to_hdf` call anywhere in it,
and every builtin `open` uses `"r"`, `"rb"`, `"rb+"` or `"w"` — no append or truncate mode exists.
All artifact serialization is delegated to the committed Increment-B writers. On the real published
attempt, every `.npy` is square and 37×37 or 35×35, and the recorded T-23S gate reports
`transient_batch_serialized: false`.

Two evidence gaps, both recorded as debt rather than blockers: `test_R4` falsifies condition 2 but
does not assert it (F5), and the recorded T-23S gate inspects 16 of the 19 published members (§8
D3).

### Item 7 — accepted-artifact / revision binding — **PASS**

Every anchor was tampered with, live, one at a time. `verify_accepted_binding` runs before the
parameter map is loaded and before any array is created; on the full-population path
`verify_dry_run_authorization` runs earlier still, inside `main()`, before `execute_dry_run` is
entered. So all five anchors are verified before compute.

| Anchor | Where bound | Tampered | Result |
| --- | --- | --- | --- |
| Phase-3 bundle | `verify_accepted_binding` | digest → zeros | `HP-MUT` raised |
| Phase-4 bundle | `verify_accepted_binding` | digest → zeros | `HP-MUT` raised |
| bread | `verify_accepted_binding` | digest → zeros | `HP-BREAD` raised |
| theta bytes | `verify_accepted_binding` | digest → zeros | `HP-MUT` raised |
| certified spec | `verify_accepted_binding` | digest → zeros | `HP-MUT` raised |
| expected nested HEAD | `verify_accepted_binding` | → zeros | `HP-REV` raised |
| **gitlink == nested HEAD** | `verify_accepted_binding` | gitlink → zeros | `HP-REV` raised |
| config digest | `load_config` | one byte / wrong root | `HP-CONFIG` raised |
| **MNL HEAD** | `verify_dry_run_authorization` | well-formed but wrong `--expected-mnl-head` | raised: `MNL HEAD c2cf6a36… != expected aaaa…` |
| nested HEAD | `verify_dry_run_authorization` | well-formed but wrong | raised |
| gitlink | `verify_dry_run_authorization` | gitlink → zeros | raised |
| worktree cleanliness | `verify_dry_run_authorization` | real, unstubbed | raised (4 untracked files present today) |

Every anchor is load-bearing. Two qualifications, both recorded as debt:

* **MNL HEAD is recorded, not bound, inside `verify_accepted_binding`.** I confirmed this directly:
  with `_git_head` returning zeros for the MNL repo, `verify_accepted_binding` returns
  `verified: True` with `mnl_head: "000000000000…"`. MNL HEAD is bound only on the authorized
  full-run path. For the run this document gates, that is sufficient — but a bounded diagnostic
  run does not bind it. The module docstring is honest about this ("MNL HEAD (recorded)").
* **The shipped suite has no tamper test for the MNL-HEAD arm or the gitlink arm.** Both are proven
  load-bearing above, by me, live; neither proof is in the packet. Required fix **F5**.

### Item 8 — numerical regression, integrated — **PASS**

**Increments A and B unmodified.** `git status --porcelain` for
`p2a_phase5_score_stream.py`, `p2a_phase5_inference.py`, `test_p2a_phase5_score_stream.py`,
`test_p2a_phase5_inference.py` and `conftest.py` is empty. The full suite is green:
`270 passed, 1 deselected in 124.52s`.

**Review-B-v2 §5 values — all reproduce exactly** (bread and covariance route, first 64,
batch 64):

| Quantity | Review-B-v2 | Reproduced | Match |
| --- | --- | --- | --- |
| raw bread asymmetry | `1.8189894035458565e-12` | `1.8189894035458565e-12` | ✔ |
| bread minimum eigenvalue | `0.10373269638807983` | `0.10373269638807983` | ✔ |
| bread condition number | `405353.9471978127` | `405353.9471978127` | ✔ |
| meat asymmetry | `0.0` | `0.0` | ✔ |
| meat minimum eigenvalue | `2.0597024553162405e-13` | `2.0597024553162405e-13` | ✔ |
| correction | `1.0230263157894737` | `1.0230263157894737` | ✔ |
| solve-vs-pinv deviation | `1.9602097722781764e-12` | `1.9602097722781764e-12` | ✔ |
| `max(abs(H_II @ V_model − I))` | `1.2038803846172754e-14` | `1.2038803846172754e-14` | ✔ |
| T-19 maximum ratio | `0.0003819780309704067` | `0.0003819780309704067` | ✔ |
| robust covariance minimum eigenvalue | `-9.474781170961761e-20` | `-9.474781170961761e-20` (T-9 gate) | ✔ |
| regional robust minimum eigenvalue | `1.7170023605273287e-06` | `1.71700236052…e-06` (see §8 D7) | ✔* |
| W-1 robust/model ratio range | `0.06105116993643892` – `0.4261454847830435` | identical | ✔ |
| meat numerical rank | `34` | `34` | ✔ |
| W-5 score-sum infinity norm | `22.52139019527921` | `22.52139019527921` | ✔ |

Interior maximum `0.00010992597206183063` at `beta_w_educH`, and active multipliers
`0.8445544161794221` / `1.4682021491125388`, also reproduce exactly.

**Increment-A first-64 T-11/T-16 figures — all reproduce exactly:**

| Quantity | Increment-A refix §P-9 | Reproduced |
| --- | --- | --- |
| `max\|S\|` first 64 | `30.23468094208269` | identical |
| T-11 bar `1e-12·max\|S\|` | `3.023468094208269e-11` | identical |
| T-11 deviation, batch 16 vs 64 | `0.0` | `0.0` |
| T-16 bar `1e-10·max\|S\|` | `3.023468094208269e-09` | identical |
| T-16 deviation, jacfwd vs jacrev | `7.105427357601002e-15` | identical |

**The streamed score-identity gate is wired exactly as ruling R-46b requires.**
`gate_score_identity` takes `full_population` and returns, when it is false, gate `T-1/T-4` at tier
`warning` with `observed.applicable = false`, `passed=True`, and a purely informational deviation.
Only when `full_population` is true does it return tier `gating` with `applicable: true` and a real
`np.allclose(sum_scores, −gradient_free, atol=1e-8, rtol=1e-8)` verdict. On my bounded run the
recorded gate is `tier=warning, applicable=False`, and it is correctly excluded from
`gating_failures`. `full_population` is derived as `n_households is None or n_households ==
cfg.population.n_households_full`, so a subset can never silently promote the gate — and,
symmetrically, requesting `--households 1555` routes through the full-run authorization rather than
around it (verified in §5, PROOF-C2 combos 7, 8, 10).

---

## 4. Self-referential authorization check

This document is the dry-run authorization instrument. I read `verify_dry_run_authorization` and
then characterized its parser by live execution against twelve synthetic review files.

**The exact contract this file must satisfy:**

1. **Path** — the `--approved-review` argument must equal, as a POSIX path, exactly
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md`; the file read is that path
   under the repository root. This file is at that path. ✔
2. **Existence** — the file must exist. ✔
3. **Digest** — `--approved-review-sha256` must equal the file's SHA-256, recomputed at run time.
4. **Verdict line** — the parser collects every line whose `.strip()` begins with the token
   `**FINAL VERDICT:` and requires that list to be **exactly one element long and equal to
   `**FINAL VERDICT: APPROVE**`**.
5. Plus, independently: `--execute-dry-run`, a 40-hex `--expected-mnl-head` matching live MNL HEAD,
   a 40-hex `--expected-dclaborsupply-head` matching live nested HEAD, gitlink == nested HEAD, and
   **both worktrees fully clean under `--untracked-files=all`**.

**Parser behaviour, verified live:**

| Review file content | Result |
| --- | --- |
| exactly one line `**FINAL VERDICT: APPROVE**` | **AUTHORIZED** |
| `**FINAL VERDICT: APPROVE AFTER FIXES**` | **REFUSED** |
| `**FINAL VERDICT: REJECT**` | **REFUSED** |
| no verdict line at all | **REFUSED** |
| two APPROVE lines | **REFUSED** |
| APPROVE plus a second verdict line at column 0 | **REFUSED** |
| APPROVE plus an *indented* second verdict line | **REFUSED** (`.strip()` is applied first) |
| APPROVE plus a blockquoted or mid-sentence mention | AUTHORIZED (correctly ignored) |
| APPROVE, wrong `--approved-review-sha256` | **REFUSED** |
| APPROVE, `--approved-review` naming any other path | **REFUSED** |

**Conclusion.** The parser authorizes if and only if the file carries exactly one verdict line and
that line is the APPROVE form. A non-APPROVE file cannot authorize — confirmed for both non-APPROVE
verdicts in the permitted set. **This file carries `APPROVE AFTER FIXES`, so it does not authorize
the full-population dry run**, which is the correct and intended consequence of my verdict. I have
deliberately written every other mention of the verdict token mid-sentence so that exactly one
line in this document matches the parser.

**Verified against this file as written.** The parser finds exactly one verdict-token line in this
document, carrying the APPROVE-AFTER-FIXES form. Passing this file to
`verify_dry_run_authorization` with correct heads, the correct canonical path, its true SHA-256,
and git cleanliness stubbed so the verdict arm is the one under test, refuses with *"approved review
does not carry exactly one APPROVE verdict"*. Invoked end-to-end through the CLI with every
authorization argument supplied and this file named, the run exits **2** — refused one arm earlier,
at `MNL worktree not fully clean`, which is finding D1 demonstrating itself. Either way the
full-population dry run does not start, and the canonical `phase5_inference_v1` root remains absent.

One drafting hazard is worth passing to whoever writes the eventual APPROVE document: an
**indented** mention of the token — inside a fenced code block, a nested list, or an example — is
stripped before matching and therefore *counts*, and will silently refuse the run. Keep such
mentions inline or blockquoted.

### 4.1 Addendum §8 refusal verified today (mandate item ii)

With no review file present, I invoked the CLI across **ten** argument combinations: no arguments;
`--execute-dry-run` alone; with one, two, then three of the four authorization arguments; with a
correctly-hashed but *wrong* review document; `--households 1555` with and without an explicit
`--out`; `--execute-dry-run --no-reproduction` fully argued; and the full-population form with every
argument supplied. **All ten exited 2** with an `[HP-AUTH]` refusal on stderr. The canonical
`phase5_inference_v1` root did not exist before, during or after the battery.

Isolating the review-file arm specifically (git cleanliness stubbed, both heads correct), the
refusal is `approved Increment-C review missing: docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md`.
Unstubbed, today's refusal arrives one arm earlier, at `MNL worktree not fully clean` — which is
the basis of finding D1 in §8.

---

## 5. Proofs executed

All commands were run from `C:\Users\hisham\Repo\MNL` using `.\.venv\Scripts\python.exe`. The
report's twelve PROOFS were executed as printed; PROOF-C1…C14 are my own additional adversarial
probes. Every writing run used a system temporary directory outside the repository.

### 5.1 The report's twelve PROOFS

| PROOF | Report's claim | My observation | Verdict |
| --- | --- | --- | --- |
| PROOF-1 | HEAD, four untracked paths, gitlink, nested HEAD, clean nested worktree | identical, exactly four untracked paths | PASS |
| PROOF-2 | phase3 `2cf23764…`, phase4 `54848869…`, bread `e9ca080e…`, theta `c024b893…`, config match | identical, all five | PASS |
| PROOF-3 | `45 passed in 25.64s` | `45 passed in 25.65s` | PASS |
| PROOF-4 | `33 passed, 12 deselected in 2.50s` | `33 passed, 12 deselected in 2.52s` | PASS |
| PROOF-5 | `12 passed, 33 deselected in 23.49s` | `12 passed, 33 deselected in 23.25s` | PASS |
| PROOF-6 | `9 passed, 36 deselected in 1.78s` | `9 passed, 36 deselected in 1.73s` | PASS |
| PROOF-7 | `4 passed, 41 deselected in 12.64s` | `4 passed, 41 deselected in 13.02s` | PASS |
| PROOF-8 | `6 passed, 39 deselected in 9.42s` | `6 passed, 39 deselected in 9.34s` | PASS |
| PROOF-9 | `4 passed, 41 deselected in 7.33s` | `4 passed, 41 deselected in 7.28s` | PASS |
| PROOF-10 | `270 passed, 1 deselected in 116.68s` | `270 passed, 1 deselected in 124.52s` | PASS |
| PROOF-11 | full run refused, `exit=2`, review absent, canonical root absent | identical, verbatim | PASS |
| PROOF-12 | bounded subset into the canonical root refused, `exit=2` | identical, verbatim | PASS |

All twelve reproduce. (Wall-clock differs only as expected.)

### 5.2 My own probes

| # | Probe | Result |
| --- | --- | --- |
| PROOF-C1 | Anchor tampering: 5 accepted digests, expected nested HEAD, gitlink, config digest, MNL HEAD — one at a time | 8 of 9 raise; MNL HEAD **not** bound in `verify_accepted_binding` (§3 item 7) |
| PROOF-C2 | Authorization arms: wrong MNL HEAD, wrong nested HEAD, wrong gitlink, real worktree cleanliness, review-file arm isolated | all five raise |
| PROOF-C3 | Ten-combination CLI refusal battery with no review file | all exit 2; canonical root absent throughout |
| PROOF-C4 | **Child run from a genuinely empty cwd** | exit 0, tree still empty, zero git delta, 13 aggregate keys only |
| PROOF-C5 | Parent vs child at 12 households: digest, three aggregate deviations | digests identical; all three deviations exactly `0.0` |
| PROOF-C6 | Cross-tuple refusal on `batch_size` and `idhh_encoding` | both raise, not `passed=False` |
| PROOF-C7 | T-12S non-vacuity: changed digest; `1e-9` score-sum drift | both fail the gate |
| PROOF-C8 | Real bounded dry run at 24 households under a tmp root | 19 members, 13 gating gates, `gating_failures == []` |
| PROOF-C9 | Planted non-allowlisted member in staging → `enforce_allowlist` | `HP-ALLOW` raised pre-publication |
| PROOF-C10 | T-23S five conditions falsified individually | all five flip to `False`; baseline passes |
| PROOF-C11 | **Mutation test**: always-false, always-true, and lying-inventory mutants | shipped `test_S1` catches all three |
| PROOF-C12 | `complete/` structural absence: attributes, full-AST scan, enumerated mkdir/replace sites | no attribute, no AST site, no construction path |
| PROOF-C13 | Authorization-parser characterization, 12 synthetic review files | contract as stated in §4 |
| PROOF-C14 | Review-B-v2 §5 and Increment-A first-64 T-11/T-16 anchors | all reproduce (§3 item 8) |

---

## 6. Integrated regression

* Committed Increment-A and Increment-B files: **unmodified** (empty `git status` for all five).
* Full repository suite: **`270 passed, 1 deselected`** with test-29 deselected, as required.
* Increment-C suite: **`45 passed`**; families L 6, M 7, N 9, O 4, P 5, Q 4, R 6, S 4.
* `git diff --check`: exit 0.
* `ruff check --select F,E9` on the two Python files: **All checks passed!** (see D2 for the
  report's claim about the third file).
* Phase-3 `attempts/` count: **70**, unchanged before and after every run in this review.
* Canonical `phase5_inference_v1` root: **absent** throughout.
* Repository worktree at the end of this review: the four declared untracked paths, plus this
  review file. No tracked file was modified. No Phase-5 artifact was written into the repository.

---

## 7. Nonblocking debt

Recorded for the Goal 1 Manager; none of these blocks the commit or the dry run.

1. **Directory `fsync` is skipped on Windows.** Per-file fsync and the atomic `os.replace` both run.
   Correctly disclosed in the report §9.2.
2. **The lock is advisory within one host** (`O_EXCL`); a stale lock after a hard kill needs manual
   removal. Same as the accepted Phase-3/4 transaction.
3. **`.staging/` survives as an empty directory** after a run. Cosmetic.
4. **`--inject-failure` is CLI-reachable.** It can only raise a controlled `StopRun` at one of three
   named stages and cannot make a failing run succeed. Deliberate, so STOPPED evidence is
   reproducible without editing source. Acceptable, but it is a production CLI surface that exists
   only for tests; consider hiding it behind `argparse.SUPPRESS` at production promotion.
5. **Non-`StopRun` exceptions are sanitized to `HP-INTERNAL`** with the type name only. Costs
   debugging detail; correct for the no-household-quantity guarantee.
6. **`staged_members()` and `enforce_allowlist()` consider only files.** A directory placed in
   staging would be published unchecked. No code path creates one.
7. **The mission charter is not on disk.** `docs/missions/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md`
   — cited as binding governance in the runner docstring, the config header and the report header —
   does not exist; there is no `docs/missions/` directory in the repository. Ruling R-46b is
   likewise not recorded in any on-disk document. A reviewer cannot inspect the governing
   instruments. This is a traceability gap for the Manager, not a code defect.
8. **Wall time and peak memory for 1,555 households remain UNKNOWN** and must be measured in the
   authorized run. Correctly disclosed in the report §9.1.

---

## 8. Residual defects

| # | Defect | Severity |
| --- | --- | --- |
| **D1** | **The full dry run requires fully clean worktrees, so the approval document must itself be committed.** `requires_clean_worktrees: true` makes `verify_dry_run_authorization` call `_git_fully_clean(repo)` with `--untracked-files=all`. An untracked approval document therefore refuses the run at the cleanliness arm — verified live today, where the four untracked files produce exactly that refusal. Report §10 step 2 prescribes "commit the exact reviewed state … **then create** the Increment-C approval document", which leaves the approval untracked and would make the run refuse. `--expected-mnl-head` must also name the *new* commit that contains the approval, not the reviewed HEAD. | **Required fix F4** — operational, would block the authorized run |
| **D2** | **Report §8's `ruff` line does not reproduce.** `ruff check --select F,E9` over "all three files" yields **28 errors**, because the YAML config is handed to a Python linter. The two Python files alone give `All checks passed!`. | Required fix F3 — report accuracy |
| **D3** | **T-23S inspects 16 of the 19 published members.** The gate is evaluated on `members_before`, taken *before* `phase5_diagnostics.json`, `phase5_console.log` and `phase5_manifest.json` are written; confirmed live (`observed.members` has 16 entries, disk has 19). Its `.tmp` sweep likewise cannot see a leftover from those three writes. Mitigated on both sides: `enforce_allowlist()` runs over the *final* staged set before publication, and `atomic_write_*` removes its own `.tmp` via `os.replace`. | Debt — recommend evaluating T-23S after all writes |
| **D4** | **Six config keys are declared but never read**: `run.track`, `gates.repro_digest_exact`, `authorization.approved_review_path`, `authorization.approved_review_verdict_line`, `authorization.requires_expected_heads`, `authorization.never_creates_complete`. The two authorization keys are the concerning pair: the config appears to define the approval path and verdict line, but the runner uses the hardcoded `CANONICAL_APPROVED_REVIEW_REL` and `APPROVE_LINE` constants. Editing the config would not move the gate. Digest-binding limits the risk to reader confusion. | Debt — either wire them or mark them advisory |
| **D5** | **`reproduction_tuple.ad_mode` is not part of the cross-tuple refusal.** `aggregate_fingerprint` carries no AD-mode field, so `compare_reproduction` can only refuse cross-tuple on `idhh_encoding` and `batch_size`. A `jacfwd`-vs-`jacrev` comparison would be reported as a mismatch rather than refused. In practice both sides read `ad_mode` from the same digest-bound config, so the case cannot arise today. | Debt — add `ad_mode` to the fingerprint |
| **D6** | **A bounded subset can be written into a *subdirectory* of the canonical root.** The guard compares `out_root.resolve() == canonical` exactly; `--out <canonical>/scratch` is permitted. | Debt — prefix check |
| **D7** | **Regional robust minimum eigenvalue matches to 12 significant digits, not bitwise** (`1.7170023605257833e-06` via a direct `eigvalsh` vs the recorded `1.7170023605273287e-06`); the ~1.5e-18 absolute difference is route-dependent symmetrization noise on a value with a `1e-6` scale. Every other Review-B-v2 anchor, including the delicate `-9.474781170961761e-20`, matches bitwise through its own gate API. Not a regression. | Informational |

---

## 9. Required fixes

Five, all documentation- or test-only. None changes runner behaviour, any design formula, constant,
schema, parameter map, or Increments A/B. None re-opens a numerical result.

**F1 — Make `test_Q2` capable of failing.** As shipped it cannot: `monkeypatch.chdir(tmp_path)`
binds the parent's cwd while `run_repro_subprocess` pins the child's to `repo_root`. Give
`run_repro_subprocess` a cwd parameter and run the child under `tmp_path`, or assert on the
repository tree (`git status --porcelain --untracked-files=all` identical before and after). The
behaviour is already correct — this only puts the proof in the packet. Reference implementation:
PROOF-C4 in §5.2.

**F2 — Correct report §6.1.** The sentence "`test_Q2` runs it from an empty temp cwd and asserts the
tree is still empty afterwards" is false as shipped. Restate it to match whatever F1 lands.

**F3 — Correct report §8's `ruff` line.** Report the command actually run — `--select F,E9` over the
two Python files, `All checks passed!` — and drop the YAML from the claim, or state the YAML check
separately (e.g. `yaml.safe_load` parses).

**F4 — Correct report §10 step 2 for the cleanliness precondition (D1).** The approval document and
the ledger update must be **committed** before the dry run is attempted, and `--expected-mnl-head`
must be the resulting commit. The current ordering leaves the approval untracked and the run
refuses. This is the one fix with operational consequences.

**F5 — Close the three test-evidence gaps.** Add a tamper test for the MNL-HEAD arm (a well-formed
but wrong `--expected-mnl-head`) and one for the gitlink arm (`_git_gitlink` monkeypatched away from
nested HEAD) — both proven load-bearing in §3 item 7, neither proven by the packet. Add
`assert g.observed["no_row_level_score_member"] is False` to `test_R4`, which already falsifies that
condition without asserting it.

Fixes F1 and F5 touch `tests/p2a/test_p2a_phase5_runner.py` (and, for F1, possibly one signature in
the runner); F2, F3 and F4 touch the increment report only. A re-review need cover only the changed
files plus a re-run of the Increment-C suite and PROOF-10 — every other result in this document
stands.

---

## 10. Whether commit and the single dry run may proceed

**Commit: not yet.** Apply F1–F5 first. Fixes F1 and F5 change files that are part of the
certified set, so the commit must carry the corrected versions; committing now would put a false
evidentiary claim (§6.1) and a non-reproducing command (§8) into the accepted record.

**The single full-population dry run: not yet, and not on the strength of this document.** This
review carries a non-APPROVE verdict, so the shipped parser refuses to authorize the run — verified
live in §4. That is the intended behaviour of the addendum §8 mechanism and requires no action.

**The path forward, in order:**

1. Apply F1–F5. Nothing else in the increment needs to change.
2. Re-run the Increment-C suite and PROOF-10; confirm `attempts/` is still 70 and the canonical
   `phase5_inference_v1` root is still absent.
3. Obtain a Review-C document carrying an APPROVE verdict at the canonical path, drafted with the
   §4 parser contract in mind — **exactly one** line matching the verdict token, and no indented
   mention of it anywhere.
4. **Commit everything together**: the runner, the config, the tests, the corrected report, the
   approval document and the JMP-M05C ledger update — so that both worktrees are fully clean under
   `--untracked-files=all` at run time (D1).
5. Only then invoke the run, with `--expected-mnl-head` set to the **new** commit created in step 4,
   `--expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb`, `--approved-review`
   naming the canonical path exactly, and `--approved-review-sha256` recomputed on the committed
   approval document.
6. Audit that run against report §9 items 1, 3 and 4: record wall time and peak memory; confirm the
   score-identity gate reports `observed.applicable = true` at gating tier and passes; confirm W-1's
   behaviour at full scale; and confirm the T-12S digest at the frozen tuple.
7. **Do not create `complete/`.** Promotion remains deputy-reserved, and — verified structurally in
   §3 item 5 — the runner has no code path capable of it.

Recommendation to the Goal 1 Manager: the implementation itself is sound and I found no behavioural
defect in blocking scope. Treat F1–F5 as a single short remediation pass, not a re-implementation.

---

**FINAL VERDICT: APPROVE AFTER FIXES**
