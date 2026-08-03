# FR P2a — JMP-M05C Minimal Streaming Implementation, Increment C
## Decisive Review C v3 (post-refix)

Reviewer: Goal-1 deputy reviewer. Mode: live adversarial verification,
read-only on the subject, exactly one file created (this one). No commits, no
full-population run. Proportionality rule binding.

---

## 1. Review-C-v3 verdict

**APPROVE.**

The single authorized defect (F6) is fixed, and the fix is verified live rather
than accepted on report. The entailed binding advance v2 → v3 is correct and
enforced at the path arm specifically. The blocking-scope items from reviews v1
and v2 all still hold under my own re-execution. The one newly-surfaced finding
(the N6/P5 canonical-output-root assertions) is adjudicated as **certified with
a pre-registered condition**, recorded as debt **D11** — see §5, where I confirm
the finding is real, measure its exact consequence, and give the reasoning for
upholding rather than rejecting.

| Mandate item | Result |
| --- | --- |
| 1. F6 by live probe, both lifecycle states | **PASS** — identical counts in both states; all three `test_N3a` branches independently falsified by mutation |
| 2. Binding advance v2 → v3 | **PASS** — v1 and v2 refused on the path arm even carrying a well-formed APPROVE line and their correct digests |
| 3. N6/P5 adjudication | **UPHOLD** manager recommendation — certify with pre-registered condition, debt D11 |
| 4. Blocking-scope spot-regression | **PASS** — 19/19 members, 13/13 gating gates green, T-12S bitwise, `complete/` structurally absent |
| 5. Self-referential, both directions | **PASS** — §7 |
| 6. Post-write suite state | **PASS** — §7 |

---

## 2. Scope and exact state

Verified at the start of this review, by direct measurement:

```text
MNL HEAD                        c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36
dclaborsupply-monorepo HEAD     27756a06ea189339aa82915ed2124628afed20eb  (clean)
phase3 attempts/                70
canonical Phase-5 output root   ABSENT
```

Untracked set — exactly nine paths, no more and no less, digests confirmed
against the values named in my mandate:

| Path | SHA-256 |
| --- | --- |
| `scripts/p2a/run_p2a_phase5_inference.py` | (deliverable) |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | `08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9` |
| `tests/p2a/test_p2a_phase5_runner.py` | (deliverable) |
| `docs/…/FR_P2a_streaming_incrementC_report_v1.md` | `461e81741096ecb4ce9097ebf28cf98c98e0ab9d00fa7874d212bc6e446b8827` |
| `docs/…/FR_P2a_streaming_incrementC_review_v1.md` | `f60e7f404ddeceeb78d9247d1354046be5e3f46c83c132202af02602179b611a` |
| `docs/…/FR_P2a_streaming_incrementC_remediation_report_v1.md` | `9e4f20a1dcaefbfe6ac95791100d1caac166af47eb4dafcc9a936bbdbf7c5214` |
| `docs/…/FR_P2a_streaming_incrementC_review_v2.md` | `27f15d2bd3ed074b0f21c3c11b7aeceb439d6c9ca3c73a97be5d385755b4946a` |
| `docs/…/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md` | `3425ab19b463cadbc115cb870a4fffa0ba994d78fba890b1af0a73862974f51e` |
| `docs/…/FR_P2a_streaming_incrementC_refix_report_v1.md` | `b1a7a873cbe0544c4a3b4cff4d3594ffd3a1161a25f4c93e878e863ffb4d8f38` |

All eight digests match. Plus this file, once written — the tenth path.

### 2.1 What I executed, and what it left behind

Everything ran under `.venv\Scripts\python.exe` from the MNL root. Three
transient fixtures were created and destroyed, each inside a single block with
guaranteed removal, each verified gone afterwards:

1. a **synthetic, well-formed APPROVE document** at the canonical review path
   (§3.2), body marked `# SYNTHETIC TEST FIXTURE - NOT A REAL REVIEW`;
2. an **empty canonical output root** `outputs/…/phase5_inference_v1/attempts`
   (§5.2) — an empty directory, which git does not track, so `git status`
   was byte-identical throughout and after;
3. scratchpad-only probe scripts and a pytest mutation plugin, never in the
   repository tree.

After all probing, `git status --porcelain` returns exactly the nine untracked
paths above. Nothing under review was modified.

---

## 3. F6 — the single authorized defect

### 3.1 The forbidden assertion is gone

The shipped `test_N3` asserted `not (MNL_ROOT / CANONICAL_APPROVED_REVIEW_REL).exists()`,
encoding a transient property of the pre-approval worktree as a standing
invariant. A full-text scan of the suite for the canonical approval path finds
exactly one surviving reference:

```text
tests/p2a/test_p2a_phase5_runner.py:364    "FR_P2a_streaming_incrementC_review_v3.md")
```

which is `test_N3d`'s *name* assertion on the binding constant, not an
existence claim. The only `.exists()` call naming the approval is line 242,
rooted at the fixture `fake`, not at `MNL_ROOT`. **No test in the suite asserts
the approval's absence at the canonical layout.** Confirmed.

### 3.2 Both lifecycle states, at identical counts

Run twice, differing only in whether a synthetic well-formed APPROVE document
was present at the canonical path:

```text
######## STATE (a): canonical approval ABSENT ########
N family      14 passed, 37 deselected in 1.67s
full suite    276 passed, 1 deselected in 114.88s (0:01:54)

######## STATE (b): synthetic well-formed APPROVE PRESENT ########
N family      14 passed, 37 deselected in 1.73s
full suite    276 passed, 1 deselected in 116.36s (0:01:56)
--- cleanup: removed; still present? False ---
```

**Identical counts, both states, both scopes.** This is the property F6 was
supposed to restore, and it holds. I reproduced the refix report §3.4 result
independently rather than accepting it.

### 3.3 `test_N3a`'s three branches are each load-bearing

Green is not evidence that a branch is doing work. I compiled three mutants of
`verify_dry_run_authorization` **into the runner module's own namespace**, so
that the tests' `monkeypatch` calls still bind, and ran `test_N3a` against each.

| Mutant | Change | `test_N3a` | Killed at | Branch proved |
| --- | --- | --- | --- | --- |
| — (baseline) | none | **1 passed** | — | — |
| M1 | `if not review.is_file():` → `if False:` | **1 failed** | `run_p2a_phase5_inference.py:135` `FileNotFoundError` on the `absent` fixture | (a) approval ABSENT → refused at the existence arm |
| M2 | `if not review.is_file():` → `if True:` | **1 failed** | `test_…:288` — `StopRun … approved Increment-C review missing` | (b) approval PRESENT → authorization SUCCEEDS |
| M3 | `if actual != review_sha:` → `if False:` | **1 failed** | `test_…:294` — `DID NOT RAISE StopRun` | (c) wrong-digest control |

Each mutant kills exactly the branch it targets and no other. In particular
**M3 confirms the wrong-digest control at line 294 is real**: it is what proves
the existence arm was *passed* rather than *skipped* in branch (b), which is the
whole load of the F6 fix. `test_N3a` is not vacuous on any of its three arms.

### 3.4 Verdict on F6

Fixed, correctly, and by the right mechanism — fixture-root isolation, mirroring
how `test_N4` already isolated the verdict arm. The rewrite of `test_N3` and the
new `test_N3a` add coverage the packet did not previously have (the *present*
lifecycle state was untested in every prior increment). **F6 CLOSED.**

---

## 4. Binding advance v2 → v3

### 4.1 The constants

```text
CANONICAL_APPROVED_REVIEW_REL  docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md
SUPERSEDED_REVIEW_RELS         [ …_review_v1.md, …_review_v2.md ]
CONFIG_SHA256   (constant)     08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9
config bytes    (disk)         08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9
load_config()   (runtime)      08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9
```

Constant, disk and runtime agree. The advance is to the v3 path as required.

### 4.2 The packet's own tests

```text
test_N3a_the_arm_is_green_in_both_lifecycle_states        PASSED
test_N3c_a_superseded_review_can_never_authorize[0]       PASSED
test_N3c_a_superseded_review_can_never_authorize[1]       PASSED
test_N3d_the_superseded_list_names_v1_and_v2              PASSED
```

`test_N3d` pins the list explicitly, ordered, and disjoint from the canonical
binding — so a silent re-pointing of the advance cannot pass unnoticed.

### 4.3 My own probe — the strongest adversarial case

`test_N3c` is the right shape, but I did not want to rely on the packet's own
framing. I re-derived it, and added a control the packet does not have.

For each superseded review, I built a fixture document carrying a genuinely
well-formed single APPROVE verdict line, computed its correct digest, stubbed
every git arm to satisfaction, and then submitted it **twice**: once named at the
superseded path, and once at the canonical path with byte-identical content.

```text
refused[PATH] FR_P2a_streaming_incrementC_review_v1.md:
    --approved-review must be exactly '…_review_v3.md'
    (identical bytes DID authorize at the canonical path
     -> the refusal is the path arm, not the content)
refused[PATH] FR_P2a_streaming_incrementC_review_v2.md:   (same)
```

The control is the point: the same bytes, same digest, same verdict line
**do authorize** when placed at the canonical path (`verified=True`,
`execution_ready=True`). So the refusal of v1 and v2 is attributable to the path
arm and to nothing else — not to content, not to digest, not to a stubbed git
check.

Second arm, against the **real on-disk documents with their real digests** and
the real repository root:

```text
refused[PATH] real …_review_v1.md (sha f60e7f404dde…)
refused[PATH] real …_review_v2.md (sha 27f15d2bd3ed…)
```

Third arm, path-spelling variants against a fixture carrying a valid approval at
the canonical path:

| Spelling | Result |
| --- | --- |
| absolute `C:\…\…_review_v3.md` | refused |
| `./docs/France_case/P2a/…_review_v3.md` | accepted |
| `docs\France_case\P2a\…_review_v3.md` (backslashes) | accepted |
| `docs/France_case/P2a/../P2a/…_review_v3.md` | refused |

The two accepted spellings are `Path(...).as_posix()` normalizations that denote
**the same canonical file**, not a different document. There is no spelling under
which a *superseded or foreign* document is admitted. This is correct behaviour,
not a bypass; I record it only so it is not later mistaken for one.

### 4.4 Verdict on the binding advance

Correct and enforced. There is no argument combination under which review v1 or
review v2 can authorize the run, whatever its digest. **CLOSED.**

---

## 5. N6/P5 adjudication (Goal-1 ruling R-51c)

### 5.1 The finding is real — premise verified, not assumed

```text
tests/p2a/test_p2a_phase5_runner.py:404  (test_N6)
tests/p2a/test_p2a_phase5_runner.py:542  (test_P5)
    assert not (MNL_ROOT / rc.CANONICAL_OUTPUT_ROOT).exists()
```

The refix report §5.3 asserts these become permanently false once the authorized
dry run publishes. I checked the premise rather than taking it:

* `scripts/p2a/configs/p2a_phase5_inference_v1.yaml:23` sets
  `output_root: outputs/p2a_singles2016/region_live_v1/phase5_inference_v1` —
  **identical** to `CANONICAL_OUTPUT_ROOT`;
* in `main`, the canonical-root refusal at line 1060 is an `elif` on the
  *bounded-subset* branch. The authorized full-population run takes the `if full:`
  branch and therefore publishes into the canonical root by default.

So yes: the very next authorized step creates that root, and both assertions go
permanently false. The finding is confirmed, and it is genuinely the same class
as F6 — a transient worktree property encoded as a standing invariant.

### 5.2 The exact consequence — measured, not predicted

I created the canonical output root as an empty directory and ran the full
suite, then removed it:

```text
canonical output root PRESENT (empty simulation of a published run)
FAILED tests/p2a/test_p2a_phase5_runner.py::test_N6_cli_refuses_a_subset_into_the_canonical_root
FAILED tests/p2a/test_p2a_phase5_runner.py::test_P5_run_writes_nothing_into_the_repository
2 failed, 274 passed, 1 deselected in 114.59s (0:01:54)
--- cleanup: still present? False ---
```

Two facts worth having on record. First, the failure set is **exactly and only**
those two tests — no third test is coupled to the root's existence. Second, an
**empty** directory suffices, so the trigger is the root's existence alone, not
any published content; the post-dry-run state will be no worse than this.

### 5.3 Ruling: UPHOLD — certify with a pre-registered condition

I uphold the manager's recommendation. Reasoning, given honestly, because the
opposite reading is defensible:

1. **Proportionality binds me as much as the implementer.** The refix was
   authorized for exactly one defect plus the entailed binding advance. The
   implementer found this, declined to fix it, and flagged it. That is the rule
   working correctly. Rejecting *because* the implementer obeyed the scope rule
   would make the rule unusable, and would convert every incidental finding into
   an unbounded scope expansion.
2. **No safety coverage is at stake either way.** Neither assertion carries the
   property its test exists to prove. `test_N6`'s actual claim is the CLI
   refusal — `returncode == 2` and `"canonical production root" in stderr`,
   asserted on the two lines immediately above 404, and the refusal is raised in
   `main` *before* `execute_dry_run` is ever called, so nothing can have been
   created. `test_P5`'s actual claim is carried by lines 543–544, which assert no
   allowlisted artifact landed in the repository. Deleting line 404 and line 542
   would lose no protective power at all. The harm here is legibility, not
   safety.
3. **Different blast radius from F6.** F6's instance sat on the *authorization*
   path: it reddened the moment an approval was created, i.e. *before* the run
   could be authorized, souring the very act being gated. N6/P5 sit on the
   *output* path and redden only *after* the authorized run has completed and is
   already scheduled for a mandated audit. The condition therefore lands in a
   venue where it will actually be read.
4. **The redness is enumerated, bounded and owned.** Two named tests, at two
   named line numbers, with a measured expected count, a named cause and a
   one-line fix already specified. That is a genuine control, not a vague
   promise.

The contrary argument — that certifying a suite guaranteed to redden trains
reviewers to tolerate red, which is the very harm F6 concerned — is real, and I
do not dismiss it. I judge it outweighed because the condition below is exact
enough to be falsifiable: it names the only two permitted failures and the exact
resulting counts, so a third failure cannot hide inside the allowance.

### 5.4 The pre-registered condition (debt D11) — binding

Recorded **before** the run, as part of the commit:

* **D11.** `test_N6:404` and `test_P5:542` encode the canonical Phase-5 output
  root's absence as a standing invariant. Both become permanently false once the
  authorized dry run publishes.
* **Expected post-run suite state, exactly:** `2 failed, 274 passed, 1 deselected`,
  the two failures being precisely
  `test_N6_cli_refuses_a_subset_into_the_canonical_root` and
  `test_P5_run_writes_nothing_into_the_repository`.
* **Audit rule.** The post-dry-run audit treats exactly those two failures as
  expected lifecycle events, not regressions. **Any third failure, any different
  identifier, or any count other than 274 passed is a regression and halts the
  audit.** The allowance is not extensible by judgement.
* **Disposition** (refix report §5.3, adopted verbatim): in both tests, replace
  the absence assertion with the property actually under test — that *this run*
  wrote nothing there — by comparing the root's listing before and after, or by
  relying on the CLI refusal arms alone.
* **Window.** The fix rides the next authorized change window. It is **not**
  authorized as part of this commit; doing so would be the scope widening the
  proportionality rule forbids.
* **Escalation.** The deputy ruling on D11 is carried to the final packet.

---

## 6. Blocking-scope regression

I re-executed the previously blocking items myself rather than reading them off
the packet. One bounded dry run under a temporary root, `SUBSET = 12`,
reproduction enabled.

| Item | Required | Observed |
| --- | --- | --- |
| Bounded dry run completes | publishes to `attempts/` | `PHASE_5_DRY_RUN_COMPLETE`, parent `attempts` |
| Member set | 19, exactly the closed allowlist | **19**; outside allowlist `[]`; allowlist unwritten `[]` |
| Gate register | 13 gating gates, all green | **13 gating / 6 warning**, all gating passed, `gating_failures = []` |
| Gating gates | T-5,6,7,8,9,10,14,17,18,19,22, T-12S, T-23S | all present, all passed |
| T-12S subprocess | bitwise digest equality | parent `6644365fd69bae20…` == child `6644365fd69bae20…` |
| T-12S deviations | 0.0 | `score_sum_free37 = 0.0`, `meat_free37 = 0.0`, `meat_interior35 = 0.0` — exact |
| T-12S tuple arms | all exact | `order`, `free_names`, `interior_names`, `n_households`, `batch_size`, `n_batches`, `idhh_encoding`, `dtype`, `byte_order` — all `True` |
| `complete/` | structurally absent | `(out/"complete").exists() = False`; `rglob("complete") = []`; manifest `creates_complete = False` |
| Lock / staging | released, drained | `True` / `True` |
| Canonical root | untouched | `False` |
| T-23S falsifiable | clean passes, planted `(12, 37)` fails | `True` / `False` → falsifiable |
| Accepted anchors load-bearing | each refuses when tampered | `phase3` `HP-MUT`, `phase4` `HP-MUT`, `bread` `HP-BREAD`, `theta_bytes` `HP-MUT`, `spec` `HP-MUT`, `expected_dcl_head` `HP-REV` |
| Manifest | grade + bundle hash | `real_run_supported=False`, `inference_grade=subset-diagnostic`, bundle hash recomputes `True` |
| Full repository suite | 276 passed, 1 deselected | **276 passed, 1 deselected** (both lifecycle states) |

All blocking items hold. Nothing certified in reviews v1/v2 has regressed under
the refix.

---

## 7. Post-write suite state

### 7.1 Self-referential check, both directions, on the final bytes of this file

Run against fixture roots, after this document reached its final form:

* **Forward.** This file, at the canonical path, with its own SHA-256 and every
  other arm satisfied → authorization **succeeds**: `verified=True`,
  `execution_ready=True`.
* **Reverse.** A variant identical to this file except that its single verdict
  line carries the word REJECT instead of APPROVE, with its own correct digest
  and every other arm satisfied → **refused**, `HP-AUTH … approved review does
  not carry exactly one APPROVE verdict`.
* **Well-formedness.** This file contains **exactly one** line whose stripped
  form begins with the verdict marker, and that line is the APPROVE line. Note
  that the runner strips each line before matching, so indentation does not
  shelter a second verdict line; there is none.

So this document authorizes if and only if it approves. Measured results in §7.3.

### 7.2 Suite state with this file present at the canonical path

Measured after writing this file, i.e. on the to-be-committed state. Results in
§7.3.

### 7.3 Measured results

```text
self-referential forward (APPROVE)   verified=True  execution_ready=True
self-referential reverse (REJECT)    REFUSED: approved review does not carry
                                     exactly one APPROVE verdict
verdict lines in this file           1

with this file present at the canonical path:
N family              14 passed, 37 deselected in 1.67s
Increment-C set       51 passed in 25.93s
full repository       276 passed, 1 deselected in 115.70s (0:01:55)
```

Identical to state (a) and state (b) of §3.2. The to-be-committed state is green
with the real approval on disk.

**Digest caveat.** The SHA-256 quoted to `--approved-review-sha256` must be
recomputed on the **committed** bytes of this file. It is not reproduced here,
because a document cannot contain its own digest.

---

## 8. Nonblocking debt

| ID | Item | Status |
| --- | --- | --- |
| **D11** | `test_N6:404` / `test_P5:542` canonical-output-root absence assertions | **NEW** — pre-registered condition, §5.4; fix rides the next authorized change window |
| D3–D10 | Carried forward from review v2 unchanged | open, none blocking |

Observations recorded but **not** debt, because they are correct behaviour:

* `--approved-review` accepts `./`-prefixed and backslash spellings of the
  canonical path via `as_posix()` normalization (§4.3). Same file; no foreign
  document is admissible.
* The `warning`-tier gate `T-1/T-4` correctly reports `applicable = false` on a
  bounded subset. Its gating-tier arm (R-46b) has never yet been exercised; the
  authorized full-population run will be its first exercise, and the audit must
  confirm it reports `applicable = true` and passes.

---

## 9. Whether commit and the single dry run may proceed

**Both may proceed.** Conditions, in order:

1. **Commit everything together** — the runner, the config, the tests, all
   reports, reviews v1, v2 and v3, the charter, and the ledger entry in
   `Job_Market_paper`. Record the resulting MNL commit as `<C2>`.
2. **Record D11 in the commit**, with §5.4's expected post-run counts and the
   audit rule. The condition must be pre-registered *before* the run, not
   reconstructed after it.
3. **Recompute this file's SHA-256 on the committed bytes.**
4. **Invoke the run exactly once**, with:
   `--execute-dry-run`,
   `--expected-mnl-head <C2>`,
   `--expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb`,
   `--approved-review docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md`,
   and that digest. Both worktrees must be fully clean at invocation
   (`--untracked-files=all`), which the authorization arm enforces.
5. **Audit the dry run** against increment report v1 §9 items 1, 3 and 4, and
   confirm R-46b's gating-tier arm reports `applicable = true` and passes.
6. **Re-run the suite after the dry run** and check it against §5.4: exactly
   `2 failed, 274 passed, 1 deselected`, failures exactly `test_N6` and
   `test_P5`. Anything else halts the audit.
7. **Do not create `complete/`.** Promotion remains deputy-reserved. The runner
   has no code path to it, and none may be added.

No further review of Increment C is required before the run.

**FINAL VERDICT: APPROVE**
