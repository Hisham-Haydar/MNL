# FR P2a — JMP-M05C Increment C — decisive Review C v2

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Authority:** M05C-AC-18, ruling R-48 — decisive review after the single AAF-budget remediation cycle
**Subject:** `FR_P2a_streaming_incrementC_remediation_report_v1.md` (treated as *claims*, re-derived here)
**Charter:** [JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md](JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md)
**Mode:** read-only, live adversarial verification. No commit. No full-population run. One file created — this one.
**Certification proportionality rule:** the eight blocking items of increment report v1 §4 bind; everything else is nonblocking debt.
**Date:** 2026-08-03
**MNL HEAD:** `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`
**Nested `dclaborsupply` HEAD = MNL gitlink:** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Review-C-v2 verdict

**REJECT — for one defect, discovered by the mandated self-referential check, with a one-line fix.**

Let me state the good news first, because it is most of the packet. All five required fixes of
Review C v1 §9 are present and correct. Where they are evidentiary claims I re-derived them under
my own mutations rather than the remediating task's, and two held **more strongly** than claimed
(§3.1, §4.2). The binding advance is right. Seven of the eight blocking items of increment report
v1 §4 re-verify live and clean. No numerical result, formula, schema, gate constant or
Increment-A/B file moved.

The defect is this. `test_N3` asserts, unconditionally, that the Increment-C approval document does
**not** exist:

```python
review = MNL_ROOT / rc.CANONICAL_APPROVED_REVIEW_REL
assert not review.exists(), "the Increment-C approval must not exist yet"
```

— [test_p2a_phase5_runner.py:231-232](../../../tests/p2a/test_p2a_phase5_runner.py#L231-L232). Creating this
review, at the canonical path, as remediation §6 step 1 requires, falsifies that assertion. The
Increment-C suite is now **1 failed, 47 passed**, live, this session (§5.6).

This is not transient and it is not an artefact of my working directory. Remediation §6 step 2
requires committing this document. Once committed, `review.exists()` is permanently `True`, so
`test_N3` fails **for every future reviewer who checks out that commit and runs the suite**. The
prescribed sequence therefore commits a permanently red certified suite into the accepted record —
and family N is named explicitly in blocking item 8. That places the failure inside blocking scope,
not in debt.

I want to be precise about what is and is not wrong. **The runner's behaviour is correct.** With
the approval present and every arm satisfied it authorizes, exactly as designed — I verified that
end-to-end (§4.3). The defect is in the test: `test_N3` encodes a transient property of the
implementation environment as if it were an invariant. The fix is one line, test-only, changes no
behaviour, and is stated in §7.

The structural point is worth recording. Review C v1 could not have caught this: until a document
existed at the canonical path, the assertion was true and the test passed. It becomes discoverable
only at the moment the approval is written — which is why the mandated self-referential check
exists, and it is what that check found.

Under the binary verdict I am permitted, APPROVE would authorize an immediate commit of a red
suite. Review v1 §10 declined to commit for materially the same reason — that committing would put
a claim into the accepted record that does not reproduce. I hold to that standard.

---

## 2. Scope and exact state

### 2.1 Starting state, verified live

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36` | identical | PASS |
| Untracked set | exactly seven declared paths | exactly those seven (eight after this file) | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean (`--untracked-files=all`, empty) | PASS |
| Phase-3 `attempts/` | 70 | 70 | PASS |
| Canonical `phase5_inference_v1` root | ABSENT | absent | PASS |
| `git diff --check` | exit 0 | exit 0 | PASS |

### 2.2 Digest inventory, recomputed

| Path | SHA-256 | Expected by state | Verdict |
| --- | --- | --- | --- |
| `FR_P2a_streaming_incrementC_report_v1.md` | `461e81741096ecb4ce9097ebf28cf98c98e0ab9d00fa7874d212bc6e446b8827` | `461e8174…` | PASS |
| `FR_P2a_streaming_incrementC_review_v1.md` | `f60e7f404ddeceeb78d9247d1354046be5e3f46c83c132202af02602179b611a` | `f60e7f40…` | PASS |
| `FR_P2a_streaming_incrementC_remediation_report_v1.md` | `9e4f20a1dcaefbfe6ac95791100d1caac166af47eb4dafcc9a936bbdbf7c5214` | as stated in full | PASS |
| `JMP_M05C_…_mission_charter_v1.md` | `3425ab19b463cadbc115cb870a4fffa0ba994d78fba890b1af0a73862974f51e` | `3425ab19…` (verify) | **PASS — verified** |
| `scripts/p2a/run_p2a_phase5_inference.py` | `d7480d939558c5bed023046d1672d4568f26db254dc89fb4fe1123d069aee3fb` | remediation §2.1 | PASS |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | `ac991937615fcf3957f43adf7b60f0d274cbb2927135be34146bb7be78022139` | remediation §2.1 | PASS |
| `tests/p2a/test_p2a_phase5_runner.py` | `ea88afcf3c5fcee97aa947a3c753e4e1cd22c92b01bb5d608dccec566493417a` | remediation §2.1 | PASS |

Report v1 and review v1 are byte-identical to their reviewed state, as the supersession convention
requires. Both remain immutable evidence.

### 2.3 What I did

Thirteen of my own probes, **PROOF-V1 … PROOF-V13**, plus a verbatim re-run of report v1's
PROOF-1 … PROOF-11. Everything quoted below is live output from this session, not a restatement of
the remediation report. My probes are in-memory or under a `tempfile` root; the repository is
otherwise unchanged — the untracked count is seven before every probe and eight after this file was
written, with no other delta, and a repository-wide search for `phase5_scores_free.npy` returns
nothing.

**Ordering note.** Every PROOF-1…11 figure in §5.6 was measured *before* this document existed, so
those are the numbers the remediation report is entitled to be compared against. §5.6 also records
the numbers *after*, which is the state that matters for the commit.

---

## 3. F1–F5 findings

All five are DONE. This section is a clean bill; the defect of §1 is not among them.

### 3.1 F1 — `test_Q2` de-vacuoused: CONFIRMED, and stronger than reported

The defect as diagnosed in review v1 §9 is real and the fix addresses it at the right level.
`run_repro_subprocess` gains a keyword-only `cwd` defaulting to `repo_root`
([run_p2a_phase5_inference.py:580-602](../../../scripts/p2a/run_p2a_phase5_inference.py#L580-L602)) — a pure
widening; with `cwd` omitted the child still runs in `repo_root`, so no default behaviour moves.
Every path the child uses is absolute (`MNL_ROOT` resolves from `__file__`), which is what makes the
widening safe.

**PROOF-V1 — my own non-vacuity re-derivation.** I ran `test_Q2`'s body verbatim
([test_p2a_phase5_runner.py:501-524](../../../tests/p2a/test_p2a_phase5_runner.py#L501-L524)) against three
suppliers of the child result. Nothing on disk was modified; the wrappers lived only in the probe
process and were restored in a `finally`.

```text
  A_unmutated        arm1(empty cwd)=True  arm2(git delta)=True  -> PASS
  B_leak_child_cwd   arm1(empty cwd)=False arm2(git delta)=True  -> FAIL
  C_leak_repo        arm1(empty cwd)=True  arm2(git delta)=False -> FAIL

unmutated PASSES           : True
child-cwd leak FAILS (arm1): True
repo leak FAILS (arm2)     : True
BOTH ARMS INDEPENDENTLY LOAD-BEARING: True
restored to real impl      : True
git status identical to baseline: True
residue search phase5_scores_free.npy in repo: []
untracked paths now: 7
```

Case **C is mine, not the remediation report's**. The report demonstrated only a child-cwd leak,
which falsifies arm 1 and leaves arm 2 unexercised — that shows the test can fail, but not that the
repository-delta arm carries any weight. Case C leaks into the repository instead: arm 1 stays
`True` and arm 2 flips to `False`. Both arms are therefore independently capable of catching a
regression, which is strictly stronger than the claim. Restore and residue checks are clean.

**F1 DONE.** The behaviour was already correct; the packet now contains a proof that can fail, on
two independent grounds.

### 3.2 F2 — increment report §6.1 corrected: CONFIRMED

I checked the superseding text of remediation §4 against the code rather than against the report.
Every clause holds: the child is placed in a genuinely empty directory via `cwd`; both arms are
asserted; the returned key set is separately asserted to be exactly the thirteen aggregate fields;
`score_sum_free37` is asserted at length `ib.N_FREE` (37) and both meats are asserted square at
`(37, 37)` and `(35, 35)`. The in-memory-mutation citation to remediation §3.2 is now independently
corroborated by PROOF-V1.

The supersession mechanism is the right call: report v1 must stay byte-identical, so correcting it
in place was not available.

**F2 DONE.**

### 3.3 F3 — increment report §8 `ruff` line corrected: CONFIRMED, re-run verbatim

Both forms re-run exactly as printed in remediation §5, from `C:\Users\hisham\Repo\MNL`:

```text
ruff --select F,E9, the two PYTHON files    -> All checks passed!      exit 0
ruff --select F,E9, incl. the YAML config   -> Found 28 errors.        exit 1
yaml.safe_load on the config -> parses: True | top-level keys:
  ['accepted', 'authorization', 'gates', 'population',
   'reproduction_tuple', 'revisions', 'run']
```

Seven top-level keys, matching the superseding line. The 28 errors are entirely the artefact of
linting YAML as Python; no Python defect existed or exists. The corrected line reproduces.

**F3 DONE.**

### 3.4 F4 — increment report §10 re-sequenced: CONFIRMED, and its premise verified live

*The mechanism.* `authorization.requires_clean_worktrees: true`
([p2a_phase5_inference_v1.yaml:73](../../../scripts/p2a/configs/p2a_phase5_inference_v1.yaml#L73)) makes
`verify_dry_run_authorization` call `_git_fully_clean(repo)`
([run_p2a_phase5_inference.py:358-364](../../../scripts/p2a/run_p2a_phase5_inference.py#L358-L364)), which is
`git status --porcelain --untracked-files=all` compared to the empty string
([:161-162](../../../scripts/p2a/run_p2a_phase5_inference.py#L161-L162)). An untracked approval document
therefore refuses the very run it authorizes.

*The premise, verified live.* Re-running report v1's PROOF-11 with the **correct** expected heads
and the canonical v2 review path, at the current state:

```text
REFUSED: [HP-AUTH] dry-run-authorization: MNL worktree not fully clean (--untracked-files=all)
exit=2
```

That is D1 reproducing exactly, so F4 is not a theoretical correction. Note the arm order: format
arms, then head identity, then cleanliness, then the review file
([:332-375](../../../scripts/p2a/run_p2a_phase5_inference.py#L332-L375)). The run refuses at cleanliness
*before* ever reading the review — so report v1's old ordering would have failed without ever
consulting the approval it had just created.

*The superseding sequence.* Remediation §6 steps 1–6 are correct as far as they go: obtain the
approval at the canonical v2 path first; commit everything together so both worktrees are clean;
recompute the SHA-256; set `--expected-mnl-head` to the new commit `<C2>` rather than `c2cf6a36…`;
audit; do not create `complete/`. The identification of `<C2>` as the commit that *contains* the
approval is the substance of the fix and it is stated correctly.

**F4 DONE** as a correction of D1. What §6 does not anticipate is that creating the approval also
breaks `test_N3` — the same class of precondition defect, one layer over. That is §1's finding, and
it belongs to F4's step 1/step 2 boundary rather than to any of F1–F5 as written.

### 3.5 F5 — three test-evidence gaps closed: CONFIRMED by independent tampering

All three additions are present. I did not rely on the added tests passing; I tampered with both
arms myself, outside the test file.

**PROOF-V2 — gitlink arm, independently tampered.**

```text
  tampered gitlink refuses : True | halt = HP-REV
  reason names 'gitlink'   : True
  reason: MNL gitlink 9999999999999999999999999999999999999999 != nested HEAD 27756a06ea18…
  unpatched call succeeds  : True
```

The refusal comes from the arm, not the fixture — the same call succeeds once the patch is undone.
`test_M4` ([test_p2a_phase5_runner.py:173-187](../../../tests/p2a/test_p2a_phase5_runner.py#L173-L187))
asserts exactly this, including the undo.

**PROOF-V3 — MNL-HEAD arm, independently tampered.**

```text
  well-formed wrong head refuses: True | halt = HP-AUTH
  reason names wrong AND real   : True
```

A well-formed 40-hex head that is not the real one is refused, and the message names both. This
matters more than it looks: review v1 §3 item 7 established that `verify_accepted_binding` does
**not** bind MNL HEAD identity — I re-confirmed that — so this authorization arm is the only place
MNL HEAD identity is enforced anywhere in the runner. `test_N3b`
([:245-264](../../../tests/p2a/test_p2a_phase5_runner.py#L245-L264)) stubs cleanliness to `True` so the
demonstrated refusal is the identity arm specifically. Correct construction.

**`test_R4`'s missing assertion** is present at
[test_p2a_phase5_runner.py:642](../../../tests/p2a/test_p2a_phase5_runner.py#L642), and PROOF-V10 shows that
condition is individually falsifiable.

**F5 DONE.** Family M is 8, family N is 11, `test_R4` gained an assertion rather than a test —
matching the claimed 45 → 48 growth exactly.

---

## 4. Binding advance and self-referential check

### 4.1 The binding advance is correct and consistently applied

**PROOF-V4.**

```text
  CANONICAL_APPROVED_REVIEW_REL: docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md
  == v2 path                   : True
  SUPERSEDED_REVIEW_REL        : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md
  CONFIG_SHA256 == on-disk cfg : True | ac991937615fcf3957f43adf7b60f0d274cbb2927135be34146bb7be78022139
  config approved_review_path  : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md
  config superseded_review_path: docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md
```

`CANONICAL_APPROVED_REVIEW_REL` is the v2 path; `CONFIG_SHA256` equals the SHA-256 of the config on
disk and equals the digest `load_config` recomputes at start-up. Runner constant, config and tests
agree. The mechanism choice is also right: no refused set exists in this runner, and inventing one
would have exceeded the authorized scope, so binding to v2 — with `SUPERSEDED_REVIEW_REL` present
purely to make the refusal legible — is the correct fallback under the instruction.

### 4.2 Review v1 cannot authorize — by two independent mechanisms

`test_N3c` ([test_p2a_phase5_runner.py:267-286](../../../tests/p2a/test_p2a_phase5_runner.py#L267-L286))
re-run inside PROOF-6: passes. My own probe supplies the v1 path with its **correct** SHA-256 and
every other arm satisfied, in four spellings:

```text
  v1 exists on disk            : True
  v1 sha256                    : f60e7f404ddeceeb78d9247d1354046be5e3f46c83c132202af02602179b611a
  v1 as posix form     refused: True | --approved-review must be exactly 'docs/France_case/…
  v1 as windows form   refused: True | --approved-review must be exactly 'docs/France_case/…
  v1 as absolute form  refused: True | --approved-review must be exactly 'docs/France_case/…
  v1 as dot-slash form refused: True | --approved-review must be exactly 'docs/France_case/…
  file read is hardcoded canonical: True | no use of review_arg as a path: True
```

The remediation report claims one mechanism (exact-path equality). There are in fact **two**, and
the second is stronger: the file actually opened is `repo / CANONICAL_APPROVED_REVIEW_REL`
([run_p2a_phase5_inference.py:366](../../../scripts/p2a/run_p2a_phase5_inference.py#L366)) — the
command-line argument is a *declaration* that is checked for equality and then never used as a
path. Even if the equality arm were bypassed, v1's bytes could not be read. The binding advance is
sound.

### 4.3 Self-referential check — both directions verified, and the defect it exposed

**The parser contract**, read from source at
[run_p2a_phase5_inference.py:376-380](../../../scripts/p2a/run_p2a_phase5_inference.py#L376-L380): collect
every line whose **stripped** form starts with the token `**FINAL VERDICT:`; the list must equal
exactly `["**FINAL VERDICT: APPROVE**"]`. Characterized live, **PROOF-V5**:

```text
  APPROVE, one line              admits=True  verdict-lines=1
  REJECT, one line               admits=False verdict-lines=1
  APPROVE + quoted READY line    admits=True  verdict-lines=1
  APPROVE + indented APPROVE     admits=False verdict-lines=2
  APPROVE twice                  admits=False verdict-lines=2
  no verdict line                admits=False verdict-lines=0
  APPROVE inline, not line-start admits=False verdict-lines=0
  end-to-end APPROVE file   authorizes=True  (want True)
  end-to-end REJECT file    authorizes=False (want False)
```

Because the parser strips before testing, an **indented** occurrence still counts — review v1 §9's
"no indented mention anywhere" is a necessary constraint, not a stylistic one. A blockquoted
occurrence does not count, since `>` survives the strip.

**PROOF-V13 — this document, against the shipped parser, both directions.** I first drafted this
review carrying an APPROVE verdict and ran the parser against the actual bytes on disk:

```text
path on disk        : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md
== CANONICAL_APPROVED_REVIEW_REL: True
verdict-token lines : [(555, '**FINAL VERDICT: APPROVE**')]
exactly one         : True   and it is APPROVE : True   not indented : True
  AS WRITTEN (APPROVE)   -> AUTHORIZES  execution_ready=True
  REJECT VARIANT         -> REFUSED     approved review does not carry exactly one APPROVE verdict
  WRONG SHA              -> REFUSED     approved review SHA-256 != --approved-review-sha256
```

Both directions hold, and the digest arm holds independently. The path, the single-verdict-line
requirement and the digest arm all behave exactly as specified — **the authorization instrument
itself is sound.** This document, now carrying REJECT, is correctly refused by that same parser,
which is the required behaviour for a non-APPROVE verdict.

**And this is where the defect surfaced.** Writing the file at the canonical path — the necessary
act of the mandated check — falsified `test_N3`'s standing assertion. Running the suite immediately
afterwards:

```text
FAILED tests/p2a/test_p2a_phase5_runner.py::test_N3_the_approved_review_file_does_not_exist_yet
E       AssertionError: the Increment-C approval must not exist yet
E       assert not True
E        +  where True = exists()
E        +    where exists = WindowsPath('C:/Users/hisham/Repo/MNL/docs/France_case/P2a/
                             FR_P2a_streaming_incrementC_review_v2.md').exists
1 failed, 10 passed, 37 deselected in 1.86s
```

`test_N3`'s stated purpose is sound — it isolates the review-file arm of
`verify_dry_run_authorization` by stubbing cleanliness and satisfying every other arm. What is
wrong is the precondition it asserts on the way there. `assert not review.exists()` is a statement
about the *implementation environment*, true only until the approval is written, and it is asserted
as though it were an invariant of the system under test. I scanned the rest of the file: every other
absence assertion targets the canonical output root, staging, the lock, or `complete/` — none of
which this process creates. `test_N3` line 232 is the sole point of failure.

---

## 5. Blocking-scope regression

The eight blocking items are increment report v1 §4's design-conformance requirements. Seven pass.
Item 8 fails.

| # | Blocking item | Evidence this session | Verdict |
| --- | --- | --- | --- |
| 1 | Dry-run-only runner: config-driven, digest-bound; eager float64 with hard refusal; environment logging; single CLI; no real-run pathway | PROOF-V9 (full-AST: no forbidden function, no real-run flag), PROOF-V11 (config digest refuses `HP-CONFIG`), PROOF-5 (`test_L*`, `test_P3` manifest env + `jax_enable_x64: true`) | PASS |
| 2 | Aggregate-only attempt transaction: unique dir, closed allowlist, `ArtifactRecord` manifest with grade, fsync + atomic rename, never `complete/` | PROOF-V6: **19 members**, all allowlisted, published under `attempts`, lock released, staging drained, `inference_grade: subset-diagnostic` | PASS |
| 3 | T-12S fresh-process reproduction at the frozen tuple; no second score file | PROOF-V8, PROOF-V1 | PASS |
| 4 | T-23S: static + behavioural, truthful in-memory reporting | PROOF-V10, PROOF-8 | PASS |
| 5 | STOPPED truthfulness with member inventory and gate register | PROOF-9 (families S) | PASS |
| 6 | Score identity from the **streamed** aggregate against `phase4_diagnostics.json → gradient_free` | PROOF-V7 (§5.4) | PASS |
| 7 | Accepted-artifact / revision binding verified before any computation | PROOF-V11, PROOF-V2 | PASS |
| 8 | Bounded-subset integration under a pytest tmp root; T-12S in a real subprocess; T-23S static+behavioural; STOPPED on injection; full run refused — **families P, Q, R, S, N** | Green while the approval is absent; **`test_N3` (family N) fails permanently once the approval exists** (§4.3, §5.6) | **FAIL** |

### 5.1 One real bounded dry run under a tmp root — 19 members, 13 gating gates green

**PROOF-V6**, `--households 24`, batch 128, `jacfwd`, into a `tempfile` root:

```text
  status                 : PHASE_5_DRY_RUN_COMPLETE
  published under        : attempts
  members                : 19
  members allowlisted    : True
  gating gates           : 13 | all passed: True
  gating gate names      : ['T-10','T-12S','T-14','T-17','T-18','T-19','T-22','T-23S',
                            'T-5','T-6','T-7','T-8','T-9']
  gating_failures        : []
  warning gates          : [('T-1/T-4',True),('W-1',False),('W-2',True),('W-3',True),
                            ('W-4',True),('W-5',True)]
  complete/ exists       : False
  lock released          : True
  staging drained        : True
  inference_grade        : subset-diagnostic
```

Nineteen members and thirteen gating gates, `gating_failures == []`. W-1 flags at warning tier and
does not gate — the unchanged Increment-B behaviour at `subset-diagnostic` scale, exactly as report
v1 §5.1 records.

### 5.2 T-12S — bitwise-identical digests, deviations exactly 0.0

**PROOF-V8**, from the same published attempt:

```text
  parent digest          : a15cebb8a2ee1effaf99a1217fdba416f83d3b7c8537ae4f95c0f42561c96f50
  child  digest          : a15cebb8a2ee1effaf99a1217fdba416f83d3b7c8537ae4f95c0f42561c96f50
  bitwise identical      : True
  score_sum_free37_max_abs_dev    : 0.0  is exactly 0.0: True
  meat_free37_max_abs_dev         : 0.0  is exactly 0.0: True
  meat_interior35_max_abs_dev     : 0.0  is exactly 0.0: True
  all exact keys True    : True
  tier/passed            : gating True
```

The digest `a15cebb8a2ee1eff…` is the value Increment A recorded for the first-24 subset at batch
128 / `jacfwd`, so the reducer's output is unchanged by this remediation — as report v1 §8.1 claims
and as remediation §10.3's numerical-core claim requires. All three deviations are exactly `0.0`,
not merely within tolerance; `repro_aggregate_atol/rtol` are both `0.0`, so the gate demands
exactness within the frozen tuple.

### 5.3 `complete/` structural absence; T-23S falsifiable; anchors load-bearing

**PROOF-V9 — structural absence, by full-AST scan of the current runner:**

```text
  string constant 'complete' anywhere in AST: []
  attribute named complete*                : []
  forbidden fn names present               : set()
  txn has complete attrs                   : False
  finish() publishes to attempts only      : True
```

Not guarded, not conditional — absent. There is no construction path.

**PROOF-V10 — T-23S's five conditions individually falsified.** Baseline passes with all five
`True`; each condition then flipped in isolation:

```text
  member_set_allowlisted       -> False gate passed=False (falsified as intended: True)
  no_row_level_score_member    -> False gate passed=False (falsified as intended: True)
  no_restricted_store_member   -> False gate passed=False (falsified as intended: True)
  no_row_level_2d_array        -> False gate passed=False (falsified as intended: True)
  no_temporary_batch_remains   -> False gate passed=False (falsified as intended: True)
```

All five are load-bearing, including the one `test_R4` now asserts.

**PROOF-V11 — accepted anchors, one-at-a-time tampering:**

```text
  phase3_bundle_sha256   -> refuses HP-MUT     theta_bytes_sha256   -> refuses HP-MUT
  phase4_bundle_sha256   -> refuses HP-MUT     spec_sha256          -> refuses HP-MUT
  bread_sha256           -> refuses HP-BREAD   expected_nested_head -> refuses HP-REV
  config digest          -> refuses HP-CONFIG
```

Every anchor is genuinely bound. With PROOF-V2 (gitlink) and PROOF-V3 (MNL HEAD, at the
authorization layer), the binding surface is complete.

### 5.4 R-46b — on-disk record matches the implementation

Remediation §9.2 records R-46b verbatim and states its implementation correspondence. I checked the
record against the code, not against the report. **PROOF-V7:**

```text
  subset tier            : warning | applicable: False | passed: True
  full-pop arm formula   : np.allclose(summed, target, atol=atol, rtol=rtol) -> present
  atol/rtol from config  : 1e-08 1e-08
  gradient source        : outputs/…/phase4_curvature_v1/complete/phase4_diagnostics.json
```

`gate_score_identity` ([run_p2a_phase5_inference.py:715-747](../../../scripts/p2a/run_p2a_phase5_inference.py#L715-L747))
returns `tier="warning"` with `observed.applicable = False` when `full_population` is false, and
`tier="gating"` with `observed.applicable = True` and the `1e-8/1e-8` `allclose` against
`gradient_free` otherwise. `full_population` is `n_households is None or n_households ==
cfg["population"]["n_households_full"]`
([:770-771](../../../scripts/p2a/run_p2a_phase5_inference.py#L770-L771)) — gating **only** at full
population, exactly what the ruling says. `test_P4` asserts the warning-tier arm on the bounded run.
The gating-tier arm is unexercised until the authorized run and must be audited there. **The on-disk
record and the implementation agree.**

### 5.5 Nothing else regressed

Increments A and B have an empty `git status`. No formula, constant, schema, parameter map or gate
threshold changed. Test growth 45 → 48 is exactly `test_M4`, `test_N3b`, `test_N3c`.

### 5.6 Suites and PROOFS — before and after the approval exists

Measured **before** this document was written — the comparison the remediation report is entitled
to:

| Proof | Remediation claim | Observed (approval absent) | Verdict |
| --- | --- | --- | --- |
| PROOF-3 | `48 passed in 26.92s` | `48 passed in 26.93s` | PASS |
| PROOF-4 | `36 passed, 12 deselected in 2.84s` | `36 passed, 12 deselected in 2.89s` | PASS |
| PROOF-5 | `12 passed, 36 deselected in 23.60s` | `12 passed, 36 deselected in 23.90s` | PASS |
| PROOF-6 | `11 passed, 37 deselected in 1.92s` | `11 passed, 37 deselected in 1.87s` | PASS |
| PROOF-7 | `4 passed, 44 deselected in 12.92s` | `4 passed, 44 deselected in 12.45s` | PASS |
| PROOF-8 | `6 passed, 42 deselected in 9.91s` | `6 passed, 42 deselected in 9.54s` | PASS |
| PROOF-9 | `4 passed, 44 deselected in 7.36s` | `4 passed, 44 deselected in 7.43s` | PASS |
| PROOF-10 | `273 passed, 1 deselected in 117.02s` | `273 passed, 1 deselected in 115.47s` | PASS |
| PROOF-11 | refused, exit 2 | refused, exit 2, at the cleanliness arm | PASS |
| PROOF-1/2 | seven untracked paths; anchors identical | identical (§2.1, §2.2) | PASS |

Every remediation figure reproduces. **The remediation report's evidence is honest and complete for
the state it was measured in.**

Measured **after** this document was written — the state remediation §6 step 2 requires at commit:

```text
Increment-C set    1 failed, 47 passed in 26.04s
  failing test     test_N3_the_approved_review_file_does_not_exist_yet
full repository    272 passed, 1 failed, 1 deselected
```

This is the finding of §1. It is a property of the commit state, not of my working copy: after the
commit, `review.exists()` is `True` for everyone, forever.

---

## 6. Nonblocking debt

Carried forward from review v1 §8, unchanged and none blocking:

* **D3** — T-23S inspects 16 of 19 published members. **Re-measured live**: `observed.members` has
  16 entries against 19 on disk, confirming the debt persists exactly as described. Mitigated on
  both sides — `enforce_allowlist()` runs over the final staged set before publication, and
  `atomic_write_*` removes its own `.tmp` via `os.replace`. Recommend evaluating T-23S after all
  writes.
* **D4** — declared-but-unread config keys. The two *concerning* keys, `approved_review_path` and
  `approved_review_verdict_line`, are now marked ADVISORY with the reason stated
  ([p2a_phase5_inference_v1.yaml:67-69](../../../scripts/p2a/configs/p2a_phase5_inference_v1.yaml#L67-L69)) —
  the correct minimal response, since the runner binds to the constants. `run.track`,
  `gates.repro_digest_exact`, `requires_expected_heads` and `never_creates_complete` remain unread.
  Partially closed; residue nonblocking.
* **D5** — `reproduction_tuple.ad_mode` is not part of the cross-tuple refusal; a `jacfwd`-vs-
  `jacrev` comparison would report a mismatch rather than refuse. Cannot arise today, since both
  sides read `ad_mode` from the same digest-bound config.
* **D6** — a bounded subset can be written into a *subdirectory* of the canonical root; the guard
  is exact equality, not a prefix check.
* **D7** — informational: regional robust minimum eigenvalue matches to 12 significant digits
  rather than bitwise; route-dependent symmetrization noise, not a regression.

New this session, all outside the eight blocking items:

* **D8 — report v1 §5.1's published bundle SHA-256 is not reproducible, and is presented as if it
  were.** Report v1 §5.1 records `b704d10dc753e6cde300d60a4f770ea6d7ca5e0b2acd93b89428208d3e615bbc`
  for a 24-household bounded run; my run of the same configuration produced
  `fac86317b151b2524494476a7376e1209480bf17bd7d22f687a80edb196d71d8`. **PROOF-V12** isolates the
  cause — two bounded runs at 24 in one session:

  ```text
  members differing between runs : ['phase5_console.log', 'phase5_diagnostics.json']
  members bitwise identical      : 16 of 18
  every NUMERIC member identical : True
  ```

  Every numeric member is bitwise identical; only the two timestamped runner-owned members differ,
  so the bundle hash is run-dependent **by construction**. This is not numeric drift — the T-12S
  digest is the reproducible anchor and it reproduces (§5.2). The debt is report accuracy: a
  reviewer could read §5.1's bundle hash as a reproducible check and wrongly infer a regression.
  Recommend annotating it as run-dependent.
* **D9 — the approval digest is over working-tree bytes, and this repository has
  `core.autocrlf=true` with no root `.gitattributes`.** `_sha256_file` hashes the file as it sits in
  the working tree. Committing does not rewrite the working tree, so a SHA-256 computed after the
  commit is stable for that run. But a fresh clone or re-checkout could materialize different line
  endings and a different SHA-256, invalidating a recorded `--approved-review-sha256`. I confirmed
  tracked markdown in this same directory is LF on disk and clean, so there is no live breakage.
  Remediation §6 step 3 already prescribes the right mitigation — recompute on the committed file at
  run time, never reuse an earlier digest. Worth an explicit note in the run log.
* **D10 — remediation §6 step 2's "commit everything together" spans two repositories.** The
  JMP-M05C ledger lives in `Job_Market_paper/docs/Missions/`, not in MNL. The runner's cleanliness
  arm checks MNL and `dclaborsupply-monorepo` only, so the ledger commit is a governance obligation
  rather than a gate precondition — it must not be skipped on the assumption the gate would catch
  it. It would not.

Under the certification proportionality rule, D3–D10 are nonblocking. None was in remediation scope;
none is in mine.

---

## 7. Whether commit and the single dry run may proceed

**Commit: NO — not in the current state.** Committing now would place a permanently failing
`test_N3` into the accepted record: 272 passed, 1 failed. Every future reviewer who checks out that
commit and runs the certified suite sees a red packet, and the remediation report's own §10.1 claim
of `273 passed` would no longer reproduce at that commit. Review v1 §10 declined to commit on
materially the same ground — that a commit must not carry a claim that does not reproduce.

**The single full-population dry run: NO — but not because the authorization mechanism is wrong.**
The mechanism is sound and I verified it end-to-end in both directions (§4.3). The run is blocked
because it must not be reached through a red commit, and because this document carries a non-APPROVE
verdict and is therefore correctly refused by the shipped parser — which is the mechanism working as
designed, not a defect.

### Required fix — F6, one line, test-only

`test_N3` must stop asserting the approval's absence as an invariant. It should isolate the
review-file arm in a way that holds whether or not the real approval exists — the same technique the
test already uses for cleanliness, applied one level further. The natural form, matching the
packet's existing idiom, is to run the arm against a `tmp_path` repository containing no approval
(as `test_N4` already does) rather than against `MNL_ROOT`, so the refusal demonstrated is the
review-file arm under a controlled absence. Any equivalent construction is acceptable. What must not
survive is `assert not (MNL_ROOT / rc.CANONICAL_APPROVED_REVIEW_REL).exists()`.

This changes no runner behaviour, no formula, constant, schema, parameter map, gate threshold, or
Increment-A/B file. It touches `tests/p2a/test_p2a_phase5_runner.py` only.

### The path forward, in order

1. Apply **F6**. Nothing else in the packet needs to change — F1–F5, the binding advance, the
   traceability closure and all seven other blocking items are verified sound above.
2. Re-run the Increment-C suite and PROOF-10 **with this document present on disk**. That is the
   state that matters; a green run with the approval absent proves nothing about the commit. Expect
   `48 passed` and `273 passed, 1 deselected`.
3. Confirm `attempts/` is still 70 and the canonical `phase5_inference_v1` root is still absent.
4. Obtain a Review C v3 carrying an APPROVE verdict at
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md`, and advance
   `CANONICAL_APPROVED_REVIEW_REL`, `SUPERSEDED_REVIEW_REL` and the config to v3 — the same binding
   advance this cycle performed for v1 → v2, for the same reason: this document is immutable
   evidence of a REJECT verdict and must never authorize the run. Re-record `CONFIG_SHA256`.
   Re-scoping is small: only F6, the constants, and the suite need re-review.
5. Then follow remediation §6 unchanged: commit everything together (including the ledger in
   `Job_Market_paper`, D10); record `<C2>`; recompute the approval's SHA-256 on disk at that moment
   (D9); invoke the run with `--expected-mnl-head <C2>`,
   `--expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb`, and the canonical
   approved-review path and digest.
6. Audit that run against increment report v1 §9 items 1, 3 and 4: wall time and peak memory; the
   score-identity gate reporting `observed.applicable = true` at **gating** tier and passing — its
   first exercise ever (§5.4); W-1's behaviour at full scale; the T-12S digest at the frozen tuple.
7. **Do not create `complete/`.** Promotion remains deputy-reserved; verified structurally in §5.3
   that the runner has no code path capable of it.
8. Carry D3–D10 forward as open debt. None blocks.

### Recommendation to the Goal 1 Manager

The remediation did what Review C v1 required, and did it well — every claim I could test
independently held, and two held more strongly than claimed. I am rejecting on a single one-line
test defect that no prior review could have seen, because it only becomes observable when the
approval document is created, and because its consequence is a permanently red certified suite in
the accepted record rather than a transient inconvenience. This warrants a short F6 pass on the
scale of the one just completed, not a re-implementation, and the seven passing blocking items do
not need re-verification beyond the suite re-run in step 2.

---

**FINAL VERDICT: REJECT**
