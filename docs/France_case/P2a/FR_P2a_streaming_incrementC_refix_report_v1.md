# FR P2a — JMP-M05C Increment C — bounded refix report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Authority:** M05C-AC-20, ruling R-50 — rule-3 conversion, the only refix for this increment
**Fix source:** `FR_P2a_streaming_incrementC_review_v2.md` (REJECT; one defect, F6)
**Charter:** [docs/France_case/P2a/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md](JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md)
**Mode:** test code + binding constants + config header only. No commit. No full-population run.
**Date:** 2026-08-03
**MNL HEAD (unchanged throughout):** `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Refix verdict

**READY FOR DECISIVE REVIEW V3**

F6 is implemented and both lifecycle states are proved green. The entailed
binding advance v2 → v3 is applied, with the superseded set now naming v1 **and**
v2. The Increment-C suite grew 48 → 51; the full repository suite is **276
passed, 1 deselected** — identical with and without an approval document present
at the canonical path.

| Item | Status |
| --- | --- |
| **F6** — `test_N3` lifecycle-aware; no assertion about the canonical path's existence | DONE (§3) |
| Both lifecycle states proved green (absent / present) | DONE (§3.3) |
| Binding advance v2 → v3; superseded names v1 and v2; `CONFIG_SHA256` advanced | DONE (§4) |
| `test_N3c` pattern extended: v2 with correct SHA and all other arms satisfied does not authorize | DONE (§4.2) |

Reviews v1 and v2 and all three prior reports are **byte-identical**; nothing
behavioural, numerical, schema-level or gate-level changed; `git diff --check`
exits 0; `attempts/` is 70; the canonical `phase5_inference_v1` output root is
ABSENT.

**One newly-observed latent defect of the same class is flagged, not fixed**
(§5.3) — it is outside the single authorized defect and is the manager's call.

---

## 2. Starting state

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36` | identical | PASS |
| Untracked set | the seven prior paths + review v2 | exactly those eight | PASS |
| Review v2 SHA-256 | `27f15d2bd3ed074b0f21c3c11b7aeceb439d6c9ca3c73a97be5d385755b4946a` | identical | PASS |
| Nested HEAD / gitlink | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| Nested worktree | clean | clean | PASS |

### 2.1 Files changed

| Path | Before | After | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/run_p2a_phase5_inference.py](../../../scripts/p2a/run_p2a_phase5_inference.py) | `d7480d939558c5bed023046d1672d4568f26db254dc89fb4fe1123d069aee3fb` | `054139c699321b6ca07e04a51e17d0cf4454fd3a75b3d5bcbf39b709cab4f72f` | 1,075 → 1,078 |
| [scripts/p2a/configs/p2a_phase5_inference_v1.yaml](../../../scripts/p2a/configs/p2a_phase5_inference_v1.yaml) | `ac991937615fcf3957f43adf7b60f0d274cbb2927135be34146bb7be78022139` | `08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9` | 75 → 78 |
| [tests/p2a/test_p2a_phase5_runner.py](../../../tests/p2a/test_p2a_phase5_runner.py) | `ea88afcf3c5fcee97aa947a3c753e4e1cd22c92b01bb5d608dccec566493417a` | `427717cdbaffc4adc9042eb6c57c4e458f05049d804d09dcd03f39635ee0756f` | 726 → 805 |

Byte-identical, verified: review v1 `f60e7f40…`, review v2 `27f15d2b…`,
increment report v1 `461e8174…`, remediation report v1 `9e4f20a1…`, the
dual-filed charter `3425ab19…`. Every Increment-A and Increment-B file has an
empty `git status`.

---

## 3. F6 — `test_N3` made lifecycle-aware

### 3.1 The defect

Review v2 §1 and its "Required fix — F6": `test_N3` asserted

```python
assert not (MNL_ROOT / rc.CANONICAL_APPROVED_REVIEW_REL).exists()
```

as a standing invariant. That encodes a **transient property of the pre-approval
worktree** as a permanent one, so the test fails for every future reviewer the
moment a real approval document exists at the canonical path — precisely the
state the next step of the process creates. The mechanism under test was never
wrong; the precondition was.

### 3.2 The fix

`test_N3` now isolates the review-file arm against a **fixture repository root**
that contains no approval — the technique `test_N4` already used for the verdict
arm, applied one level further. The forbidden assertion is gone: no test in the
suite refers to the existence of the real canonical approval path.

A companion `test_N3a` makes the lifecycle-independence explicit by exercising
**both** branches against fixture roots:

* approval **absent** → refused at the review-file arm;
* approval **present** and well-formed → authorization **succeeds**
  (`verified`/`execution_ready` true);
* approval **present** with the wrong digest → refused at the *digest* arm,
  which proves the existence arm was passed rather than skipped.

That third branch matters: without it, a test could "pass" the present-branch by
never reaching the existence check at all.

### 3.3 Hunk map

| File | Line(s) | Change | Item |
| --- | --- | --- | --- |
| `test_p2a_phase5_runner.py` | 224–253 | `test_N3` rewritten against a fixture root; standing absence assertion deleted; renamed `..._authorization_refuses_when_the_approval_is_absent` | F6 |
| `test_p2a_phase5_runner.py` | 255–318 | new `test_N3a` — both lifecycle branches plus the digest-arm control | F6 |

### 3.4 Both lifecycle states proved

The N family and the full repository suite were run twice, differing only in
whether a **synthetic, well-formed APPROVE document** was present at the
canonical path `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md`:

```text
############ STATE (a): NO approval present at the canonical path ############
canonical approval ABSENT (as now)
14 passed, 37 deselected in 1.66s
276 passed, 1 deselected in 110.00s (0:01:50)

############ STATE (b): synthetic well-formed APPROVE present ############
canonical approval PRESENT (synthetic fixture)
14 passed, 37 deselected in 1.71s
276 passed, 1 deselected in 108.53s (0:01:48)
--- cleanup: removed docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md ---
```

**Identical counts in both states.** Before F6, state (b) would have produced
`276 passed, 1 failed` on `test_N3`, exactly as review v2 §5.6 recorded.

The fixture was created and destroyed inside a single shell block with an `EXIT`
trap guaranteeing removal, and its body was marked
`# SYNTHETIC TEST FIXTURE - NOT A REAL REVIEW` so it could never be mistaken for
an authorization instrument. Post-run verification:

```text
synthetic fixture removed : ABSENT (removed)
git status                : exactly the eight expected untracked paths
attempts/                 : 70
phase5_inference_v1 root  : ABSENT
```

### 3.5 Confirmation at the REAL canonical layout

A grep for any assertion touching the real approval path returns nothing:

```text
grep "assert not (MNL_ROOT ... CANONICAL_APPROVED_REVIEW_REL" -> NONE
grep "must not exist yet"                                     -> NONE
```

The two surviving `assert not (MNL_ROOT / …).exists()` lines refer to
`CANONICAL_OUTPUT_ROOT`, not to the approval document — see §5.3, where they are
flagged as a separate finding.

---

## 4. Binding advance v2 → v3

Third application of the R-29 / R-48 precedent. Review v1 is immutable
APPROVE-AFTER-FIXES evidence; review v2 is immutable **REJECT** evidence. Neither
may ever authorize the run, so the authorization is advanced to the decisive v3
document.

### 4.1 Hunk map

| File | Line(s) | Change |
| --- | --- | --- |
| `run_p2a_phase5_inference.py` | 85–97 | `CANONICAL_APPROVED_REVIEW_REL` → v3; `SUPERSEDED_REVIEW_REL` (single) replaced by `SUPERSEDED_REVIEW_RELS` naming **v1 and v2**; rationale comment updated |
| `run_p2a_phase5_inference.py` | 82 | `CONFIG_SHA256` → `08be1cf6…`, advanced with the config it binds |
| `p2a_phase5_inference_v1.yaml` | 67–74 | `approved_review_path` → v3; `superseded_review_path` → `superseded_review_paths` list naming v1 and v2; ADVISORY note retained (review D4) |
| `test_p2a_phase5_runner.py` | 320–355 | `test_N3c` parametrised over both superseded documents, on the F6 fixture pattern |
| `test_p2a_phase5_runner.py` | 357–364 | new `test_N3d` — the superseded list is explicit, ordered, and disjoint from the canonical binding |

The refusal remains **by binding**, not by an added check: `--approved-review`
must equal `CANONICAL_APPROVED_REVIEW_REL` exactly, so every superseded path is
inadmissible whatever its digest. No behavioural code changed.

### 4.2 `test_N3c` extended, as directed

For **each** of v1 and v2, the test builds a fixture root containing that
document with a well-formed `**FINAL VERDICT: APPROVE**` line, supplies its
**correct** SHA-256, satisfies every other arm (heads, gitlink, cleanliness), and
asserts the refusal `approved-review must be exactly …`. A superseded document
therefore cannot authorize even when it is materially perfect in every respect
except its identity.

`test_N3c` is itself lifecycle-robust: it runs against fixture roots and asserts
nothing about which review documents exist in the real repository — the F6 lesson
applied consistently rather than only where the review named it.

### 4.3 Live confirmation

```text
binds to      : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md
superseded    : [..._review_v1.md, ..._review_v2.md]
```

The full run remains refused: the flag is absent, and the v3 document does not
exist.

---

## 5. Regression

### 5.1 Suites

```text
Increment-C set                            51 passed in 25.78s   (was 48; +3)
  N family                                 14 passed, 37 deselected in 1.83s
full repository, test-29 deselected       276 passed, 1 deselected  (was 273; +3)
  state (a) approval absent               276 passed, 1 deselected
  state (b) approval present              276 passed, 1 deselected
Phase-3 attempts/                                                          70
canonical phase5_inference_v1 root                                     ABSENT
ruff --select F,E9 (the two Python files)               All checks passed!
git diff --check                                                       exit 0
```

Test growth 48 → 51 is exactly: `test_N3a` (+1), `test_N3c` 1 → 2 parametrised
cases (+1), `test_N3d` (+1). `test_N3` itself was rewritten, not added.

### 5.2 Scope discipline

Only test code, two binding constants (`CANONICAL_APPROVED_REVIEW_REL` /
`SUPERSEDED_REVIEW_RELS`, plus the dependent `CONFIG_SHA256`) and the config
header changed. No runner behaviour, no formula, constant, schema, parameter
map, gate threshold, or Increment-A/B file. The numerical core is untouched:
nothing in this refix reaches a computation.

### 5.3 Newly-observed latent defect — FLAGGED, NOT FIXED

While confirming §3.5 I found a defect of **exactly the same class as F6**, one
layer over, that the review did not name:

```text
tests/p2a/test_p2a_phase5_runner.py:404  (test_N6)
tests/p2a/test_p2a_phase5_runner.py:542  (test_P5)
    assert not (MNL_ROOT / rc.CANONICAL_OUTPUT_ROOT).exists()
```

Both encode "the canonical Phase-5 **output** root does not exist" as a standing
invariant. That is true today, and will become permanently false the moment the
authorized full-population dry run publishes its attempt — i.e. at the very next
step of the process. Both tests would then fail for every future reviewer, for
the same reason `test_N3` did.

I have **not** fixed it: this bounded refix is authorized for the single defect
F6 plus the entailed binding advance, and silently widening scope is what the
proportionality rule exists to prevent. Recommended one-line disposition, for
the manager: in both tests, replace the absence assertion with the property
actually under test — that *this run* wrote nothing there — e.g. compare the
root's directory listing before and after, or assert the CLI refusal alone
(`returncode == 2` plus the refusal message), which is already asserted
immediately above line 404.

Review v2's D3–D10 debt items are carried forward unchanged; none blocks.

---

## 6. Immediate next action

1. **Decisive Review C v3** — read-only, at MNL
   `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`. Per review v2 §"path forward"
   step 4 the re-scope is small: **F6, the constants, and the suite**. Everything
   else in review v2 stands verified. Run the Increment-C suite and PROOF-10
   **with the review v3 document present on disk** — expect `51 passed` and
   `276 passed, 1 deselected`, unchanged from the absent state (§3.4).
2. **Write the verdict to**
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md` with exactly
   one `**FINAL VERDICT: APPROVE**` line and no indented mention of the token —
   that document is now the authorization instrument.
3. **Decide the §5.3 finding** before the dry run, since it bites immediately
   after it. Either authorize the one-line disposition above as part of the
   commit, or accept it as known debt with the consequence recorded.
4. **On APPROVE**: follow remediation report §6 unchanged — commit everything
   together first (sources, tests, all reports, reviews v1/v2/v3, the charter,
   the ledger in `Job_Market_paper`), record `<C2>`, recompute the approval's
   SHA-256 on the committed file, then invoke the run with
   `--expected-mnl-head <C2>`,
   `--expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb`,
   `--approved-review docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v3.md`
   and that digest.
5. **Audit the dry run** against increment report v1 §9 items 1, 3 and 4, and
   confirm R-46b's gating-tier arm reports `applicable = true` and passes — its
   first exercise ever.
6. **Do not create `complete/`.** Promotion remains deputy-reserved.

**FINAL VERDICT: READY FOR DECISIVE REVIEW V3**
