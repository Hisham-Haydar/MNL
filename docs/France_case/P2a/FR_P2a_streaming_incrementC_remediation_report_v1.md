# FR P2a — JMP-M05C Increment C — narrow remediation report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Authority:** M05C-AC-18, ruling R-48 — the single AAF-budget remediation cycle
**Authoritative fix source:** `FR_P2a_streaming_incrementC_review_v1.md` §§8–9 (locations from §§3–4)
**Charter:** [docs/France_case/P2a/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md](JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md) — dual-filed by this task (§9)
**Mode:** documentation- and test-only, plus two binding constants. No commit. No full-population run.
**Date:** 2026-08-03
**MNL HEAD (unchanged throughout):** `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

> **Supersession, per house convention.** `FR_P2a_streaming_incrementC_report_v1.md`
> and `FR_P2a_streaming_incrementC_review_v1.md` are **byte-identical** to their
> reviewed state. The corrections F2, F3 and F4 are recorded here and supersede
> the cited sections of increment report v1 — §6.1 (F2), §8's `ruff` line (F3),
> and §10 (F4). A reader of report v1 should treat those three sections as
> replaced by §4, §5 and §6 below. The charter citation in report v1's header is
> likewise superseded by this report's header.

---

## 1. Remediation verdict

**READY FOR DECISIVE REVIEW V2**

All five required fixes of Review C v1 §9 are implemented, plus the entailed
binding advance and the traceability closure the Goal-1 Manager directed. The
Increment-C suite grew 45 → 48; the full repository suite is **273 passed, 1
deselected**.

| Fix | Review C v1 §9 requirement | Status |
| --- | --- | --- |
| **F1** | `test_Q2` de-vacuoused — the child must run from a genuinely empty cwd | DONE, non-vacuity demonstrated (§3) |
| **F2** | Report §6.1 corrected to describe the actual mechanism | DONE (§4) |
| **F3** | Report §8 `ruff` line corrected and re-run verbatim | DONE (§5) |
| **F4** | Report §10 re-sequenced for the clean-worktree precondition (D1) | DONE (§6) |
| **F5** | Two missing tamper tests + the missing `test_R4` assertion | DONE (§7) |

Nothing else changed. No numerical result, schema, gate constant, design
formula, parameter map, or Increment-A/B file was touched; `git diff --check`
exits 0; `attempts/` is still 70; the canonical `phase5_inference_v1` root is
still ABSENT.

---

## 2. Starting state

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36` | identical | PASS |
| Untracked set | exactly the five declared paths | exactly those five | PASS |
| Nested HEAD / gitlink | `27756a06ea189339aa82915ed2124628afed20eb` | identical, gitlink matches | PASS |
| Nested worktree | clean | clean | PASS |

### 2.1 Files changed by this task

| Path | Reviewed SHA-256 | After remediation | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/run_p2a_phase5_inference.py](../../../scripts/p2a/run_p2a_phase5_inference.py) | `f283f1ac3d5664a42d2276cc142aa665a1c7aebc5b82cefb4cba042816c35ed0` | `d7480d939558c5bed023046d1672d4568f26db254dc89fb4fe1123d069aee3fb` | 1,058 → 1,075 |
| [scripts/p2a/configs/p2a_phase5_inference_v1.yaml](../../../scripts/p2a/configs/p2a_phase5_inference_v1.yaml) | `7ca3428a783b9b66bd20dd9a40a2c2ebce02d39e9867ee069de2be9c49d54f0a` | `ac991937615fcf3957f43adf7b60f0d274cbb2927135be34146bb7be78022139` | 71 → 75 |
| [tests/p2a/test_p2a_phase5_runner.py](../../../tests/p2a/test_p2a_phase5_runner.py) | `01ce44cbdec49ed98be6b1526c2813534ff930c2294b157155bafd54039c3f7c` | `ea88afcf3c5fcee97aa947a3c753e4e1cd22c92b01bb5d608dccec566493417a` | 644 → 726 |

New (traceability, §9): `docs/France_case/P2a/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md`,
SHA-256 `3425ab19b463cadbc115cb870a4fffa0ba994d78fba890b1af0a73862974f51e`.

Unchanged, byte-identical: increment report v1 `461e81741096ecb4ce9097ebf28cf98c98e0ab9d00fa7874d212bc6e446b8827`;
review v1 `f60e7f404ddeceeb78d9247d1354046be5e3f46c83c132202af02602179b611a`.
`git status` for every Increment-A and Increment-B file is empty.

---

## 3. F1 — `test_Q2` de-vacuoused

**The defect (review §1, §9 F1).** As shipped, `test_Q2` could not fail.
`monkeypatch.chdir(tmp_path)` bound the **parent's** cwd, while
`run_repro_subprocess` pinned the **child's** cwd to `repo_root`. The assertion
`sorted(p.name for p in tmp_path.rglob("*")) == before == []` was therefore true
regardless of what the child wrote — the assertion target and the child's working
directory were disjoint. The behaviour was already correct; the packet simply
contained no test capable of catching a regression.

**The fix.** `run_repro_subprocess` gains a keyword-only `cwd` parameter
defaulting to `repo_root` — a pure widening, since every path the child uses is
already absolute (`MNL_ROOT` is resolved from `__file__`). `test_Q2` now creates
a genuinely empty directory, runs the child **in it**, and asserts on two
independent arms:

1. the child's own working directory is still empty afterwards;
2. `git status --porcelain --untracked-files=all` over the repository is
   byte-identical before and after — the review's own PROOF-C4 formulation.

### 3.1 Hunk map

| File | Line(s) | Change | Fix |
| --- | --- | --- | --- |
| `run_p2a_phase5_inference.py` | 580–582 | `run_repro_subprocess` signature gains `*, cwd: Optional[Path] = None` | F1 |
| `run_p2a_phase5_inference.py` | 583–595 | docstring: the `cwd` contract and why the shipped test could not fail | F1 |
| `run_p2a_phase5_inference.py` | 602 | `cwd=str(repo_root if cwd is None else cwd)` | F1 |
| `test_p2a_phase5_runner.py` | 489–514 | `test_Q2` rewritten: empty child cwd + git-delta arm | F1 |

This is the only runner change in the remediation that touches a code path, and
it changes no default behaviour: with `cwd` omitted the child still runs in
`repo_root`, exactly as before.

### 3.2 Non-vacuity demonstration (temporary in-memory mutation, then restored)

The probe was run twice against the *same* test body: once with the real
`run_repro_subprocess`, once with an in-memory wrapper that additionally drops a
`phase5_scores_free.npy`-shaped file into the child's working directory — i.e. a
child that leaks a second score file. Nothing on disk was modified; the wrapper
lived only in the probe process and was restored immediately.

```text
F1 non-vacuity probe (in-memory mutation only; nothing on disk changed)
  unmutated child            arm1(empty cwd)=True  arm2(git delta)=True  -> PASS
  MUTATED leaky child        arm1(empty cwd)=False arm2(git delta)=True  -> FAIL

unmutated PASSES : True
mutated   FAILS  : True
PROBE IS NON-VACUOUS: True
restored to real implementation: True
```

Post-run residue check: `git status --porcelain --untracked-files=all` shows only
the expected untracked set, and a repository-wide search for
`phase5_scores_free.npy` returns nothing.

**Probe re-run:** `test_Q2` passes in the shipped suite (§10, PROOF-7,
`4 passed, 44 deselected`).

---

## 4. F2 — increment report §6.1 corrected

**Superseding text.** Increment report v1 §6.1 states:

> "`test_Q2` runs it from an empty temp cwd and asserts the tree is still empty
> afterwards, and that the returned object's key set is exactly the thirteen
> aggregate fields…"

That was false as shipped, for the reason in §3. **The corrected statement,
which supersedes it, is:**

> `test_Q2` runs the child **in a genuinely empty directory**, passed through
> `run_repro_subprocess(..., cwd=...)`, and asserts on two independent arms:
> that the child's own working directory is still empty afterwards, and that
> `git status --porcelain --untracked-files=all` over the repository is
> byte-identical before and after. A child that wrote a second score file
> anywhere would fail one of the two arms — demonstrated by in-memory mutation
> in remediation report §3.2. The returned object's key set is separately
> asserted to be exactly the thirteen aggregate fields, with
> `score_sum_free37` of length 37 and both meats square.

No other sentence in §6.1 is affected: the T-12S comparison table, the
cross-tuple refusal paragraph and the non-vacuity paragraph all reproduce as
printed.

---

## 5. F3 — increment report §8 `ruff` line corrected

**The defect (review D2).** Report v1 §8 printed
`ruff check --select F,E9 (all three files) → All checks passed!`. Handing the
YAML config to a Python linter yields 28 errors, so the line as printed does not
reproduce.

**Re-run verbatim, both forms:**

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m ruff check --select F,E9 scripts\p2a\run_p2a_phase5_inference.py tests\p2a\test_p2a_phase5_runner.py
```

```text
All checks passed!
```

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m ruff check --select F,E9 scripts\p2a\run_p2a_phase5_inference.py scripts\p2a\configs\p2a_phase5_inference_v1.yaml tests\p2a\test_p2a_phase5_runner.py
```

```text
Found 28 errors.
```

**Superseding text for report v1 §8.** The lint line should read:

> ```text
> ruff check --select F,E9 (the two PYTHON files)          All checks passed!
> yaml.safe_load on the config                             parses; 7 top-level keys
> ```

The YAML's own check, run verbatim:

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import yaml;d=yaml.safe_load(open('scripts/p2a/configs/p2a_phase5_inference_v1.yaml',encoding='utf-8'));print('yaml.safe_load parses:', isinstance(d,dict), '| top-level keys:', sorted(d))"
```

```text
yaml.safe_load parses: True | top-level keys: ['accepted', 'authorization', 'gates', 'population', 'reproduction_tuple', 'revisions', 'run']
```

The 28 errors are entirely an artefact of linting YAML as Python; no Python
defect existed or exists.

---

## 6. F4 — increment report §10 re-sequenced

**The defect (review D1).** `authorization.requires_clean_worktrees: true` makes
`verify_dry_run_authorization` call `_git_fully_clean(repo)` with
`--untracked-files=all`. Report v1 §10 step 2 said "commit the exact reviewed
state … **then create** the Increment-C approval document", which leaves the
approval untracked — so the very run it authorizes refuses at the cleanliness
arm. `--expected-mnl-head` must also name the **new** commit that contains the
approval, not the reviewed HEAD.

**Superseding sequence for report v1 §10.** Fixed documents and the decisive
APPROVE review are **committed before** the authorized run:

1. Apply this remediation (done) and obtain **Review C v2** carrying an exact
   `**FINAL VERDICT: APPROVE**` at
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md`, drafted
   against the §4 parser contract — exactly one line matching the verdict token,
   and no indented mention of it anywhere.
2. **Commit everything together, in one commit**: the runner, the config, the
   tests, increment report v1, this remediation report, review v1, review v2,
   the dual-filed charter, and the JMP-M05C ledger update. Both worktrees must
   then be fully clean under `--untracked-files=all`.
3. Recompute the approval's SHA-256 **on the committed file** and record the new
   commit SHA — call it `<C2>`.
4. Only then invoke the run:

   ```powershell
   cd C:\Users\hisham\Repo\MNL
   & .\.venv\Scripts\python.exe scripts\p2a\run_p2a_phase5_inference.py --execute-dry-run `
     --expected-mnl-head <C2> `
     --expected-dclaborsupply-head 27756a06ea189339aa82915ed2124628afed20eb `
     --approved-review docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md `
     --approved-review-sha256 <sha256 of the committed review v2>
   ```

5. Audit that run against increment report v1 §9 items 1, 3 and 4: record wall
   time and peak memory; confirm the score-identity gate reports
   `observed.applicable = true` at gating tier and passes; confirm W-1's
   behaviour at full scale; confirm the T-12S digest at the frozen tuple.
6. **Do not create `complete/`.** Promotion remains deputy-reserved and the
   runner has no code path capable of it.

The ordering change is the whole fix: `--expected-mnl-head` is `<C2>`, the
commit that *contains* the approval, not `c2cf6a36…`.

---

## 7. F5 — the three missing test-evidence gaps closed

Review §9 F5 named three conditions proved load-bearing in review §3 item 7 but
never asserted by the packet.

| Added | What it proves |
| --- | --- |
| `test_M4_binding_refuses_a_gitlink_that_diverges_from_nested_head` | the **gitlink arm** of `verify_accepted_binding`: `_git_gitlink` monkeypatched away from nested HEAD → `HP-REV`, message names `gitlink`. It then undoes the patch and asserts the same call succeeds, so the refusal came from the arm and not the fixture. |
| `test_N3b_authorization_refuses_a_wrong_expected_mnl_head` | the **MNL-HEAD arm** of `verify_dry_run_authorization`: a *well-formed* but wrong 40-hex head is refused. Format and identity are separate arms; only format was covered. Cleanliness is stubbed `True` so the demonstrated refusal is the identity arm specifically, and the message is asserted to name both the wrong and the real head. |
| `assert g.observed["no_row_level_score_member"] is False` in `test_R4` | the condition the fixture already falsified but never asserted — a gate that stopped computing it would previously have gone unnoticed. |

A third test was added by the entailed binding advance (§8):
`test_N3c_the_superseded_v1_review_can_never_authorize`.

### 7.1 Hunk map

| File | Line(s) | Change | Fix |
| --- | --- | --- | --- |
| `test_p2a_phase5_runner.py` | 173–187 | new `test_M4` (gitlink arm) | F5 |
| `test_p2a_phase5_runner.py` | 245–264 | new `test_N3b` (MNL-HEAD arm) | F5 |
| `test_p2a_phase5_runner.py` | 267–286 | new `test_N3c` (superseded v1 refused) | binding advance |
| `test_p2a_phase5_runner.py` | 642 | `test_R4` gains the missing assertion | F5 |

**Probe re-run:** family M `test_M4` and family N `test_N3b`/`test_N3c` pass
inside PROOF-6 (`11 passed, 37 deselected`, up from 9); `test_R4` passes inside
PROOF-8 (`6 passed, 42 deselected`).

---

## 8. Binding advance (entailed, R-29 precedent, disclosed)

Review C v1 returned **APPROVE AFTER FIXES**. It is immutable evidence of that
verdict and must never authorize the run. The authorization is therefore advanced
from `..._incrementC_review_v1.md` to `..._incrementC_review_v2.md` in the runner
constant, the config, and the tests.

**Mechanism chosen.** The instruction was: add v1 to the refused set *if one
exists*, else ensure the parser refuses it *by binding*. No refused set exists in
this runner, and adding one would be a behavioural change beyond the authorized
scope (the constraint permits changes only to F1/F5 test code and the binding
constants). The fallback therefore applies: `--approved-review` must equal
`CANONICAL_APPROVED_REVIEW_REL` **exactly**, so advancing that constant to v2
makes v1 unusable by binding. `SUPERSEDED_REVIEW_REL` is added as a named
constant so the refusal is legible rather than incidental, and the config records
`superseded_review_path` alongside.

| File | Line(s) | Change |
| --- | --- | --- |
| `run_p2a_phase5_inference.py` | 85–94 | `CANONICAL_APPROVED_REVIEW_REL` → v2; new `SUPERSEDED_REVIEW_REL` = v1; rationale comment |
| `run_p2a_phase5_inference.py` | 82 | `CONFIG_SHA256` advanced to `ac991937…` for the edited config |
| `p2a_phase5_inference_v1.yaml` | 67–71 | `approved_review_path` → v2; new `superseded_review_path` = v1; marked ADVISORY (review D4) |
| `test_p2a_phase5_runner.py` | 267–287 | `test_N3c` proves v1 can never authorize |

Verified live:

```text
binds to      : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md
superseded    : docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v1.md
v2 exists     : False
v1 exists     : True
```

`test_N3c` supplies the v1 path with its *correct* SHA-256 and every other arm
satisfied, and asserts the refusal `--approved-review must be exactly …`. The
full run therefore remains refused, now for two independent reasons: the flag is
absent, and the decisive v2 document does not exist.

The config comment also addresses review **D4** for the two authorization keys by
marking them ADVISORY — the runner binds to the constants, not the config. The
remaining D4 keys, and D3, D5, D6, D7, remain open debt as the review classed
them; none is in remediation scope.

---

## 9. Traceability closure

### 9.1 Charter dual-filing

`JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md` was copied from
`Job_Market_paper/docs/Missions/` into `MNL/docs/France_case/P2a/`, following the
dual-filing pattern. Hash-verified on copy:

```text
source : 3425ab19b463cadbc115cb870a4fffa0ba994d78fba890b1af0a73862974f51e  5652 bytes
copy   : 3425ab19b463cadbc115cb870a4fffa0ba994d78fba890b1af0a73862974f51e  5652 bytes
IDENTICAL: True
```

Citations corrected to the dual-filed path
(`docs/France_case/P2a/JMP_M05C_minimal_streaming_implementation_mission_charter_v1.md`):

| File | Line | Was | Now |
| --- | --- | --- | --- |
| `run_p2a_phase5_inference.py` | 7 | `docs/missions/JMP_M05C_…` | `docs/France_case/P2a/JMP_M05C_…` |
| `p2a_phase5_inference_v1.yaml` | 7 | `docs/missions/JMP_M05C_…` | `docs/France_case/P2a/JMP_M05C_…` |
| this report | header | — | cites the dual-filed path |

Increment report v1's header citation is **superseded** by this report's header
rather than edited, since report v1 must remain byte-identical.

### 9.2 Ruling R-46b, recorded verbatim

> **R-46b.** The subset score-identity gate is warning-tier, gating only at full
> population.

Implementation correspondence, for the record: `gate_score_identity` returns
`tier="warning"` with `observed.applicable = False` whenever
`full_population` is false, and `tier="gating"` with `observed.applicable = True`
on the full population, where it applies
`np.allclose(sum_scores, -gradient_free, atol=1e-8, rtol=1e-8)` against
`phase4_diagnostics.json → gradient_free` (R-37b). `test_P4` asserts the
warning-tier/`applicable=False` behaviour on the bounded run. The gating-tier
arm is exercised for the first time in the authorized full-population dry run and
must be audited there (§6 step 5).

---

## 10. Regression

### 10.1 Suites

```text
Increment-C set                            48 passed in 26.92s   (was 45; +3)
  fast (-m "not production")               36 passed, 12 deselected in 2.84s
  production (-m production)               12 passed, 36 deselected in 23.60s
full repository, test-29 deselected       273 passed, 1 deselected in 117.02s
Phase-3 attempts/ count                                                   70
canonical phase5_inference_v1 root                                    ABSENT
ruff --select F,E9 (the two Python files)               All checks passed!
git diff --check                                                      exit 0
```

Test growth 45 → 48 is exactly the three added tests: `test_M4` (F5),
`test_N3b` (F5), `test_N3c` (binding advance). `test_R4` gained an assertion
rather than a test. Family breakdown now: L 6, M 8, N 11, O 4, P 5, Q 4, R 6, S 4.

### 10.2 PROOFS re-run, verbatim in PowerShell

| Proof | Report v1 | Now | Result |
| --- | --- | --- | --- |
| PROOF-2 | four hashes | identical; `config` line now `ac991937…` on both sides | PASS (digest advanced with the config) |
| PROOF-3 | `45 passed` | `48 passed in 26.92s` | PASS (+3) |
| PROOF-4 | `33 passed, 12 deselected` | `36 passed, 12 deselected in 2.84s` | PASS (+3) |
| PROOF-5 | `12 passed, 33 deselected` | `12 passed, 36 deselected in 23.60s` | PASS |
| PROOF-6 | `9 passed, 36 deselected` | `11 passed, 37 deselected in 1.92s` | PASS (+2) |
| PROOF-7 | `4 passed, 41 deselected` | `4 passed, 44 deselected in 12.92s` | PASS |
| PROOF-8 | `6 passed, 39 deselected` | `6 passed, 42 deselected in 9.91s` | PASS |
| PROOF-9 | `4 passed, 41 deselected` | `4 passed, 44 deselected in 7.36s` | PASS |
| PROOF-10 | `270 passed, 1 deselected` | `273 passed, 1 deselected in 117.02s` | PASS (+3) |
| PROOF-11 | refused, exit 2 | refused, exit 2; binding now v2 | PASS |

Only counts move, and only by the three added tests, plus PROOF-2's `config`
digest which advances with the config it binds. PROOF-1's expected untracked
block now lists **seven** paths (the five at task start, plus the dual-filed
charter and this report) — a reviewer should expect seven, not five.

### 10.3 Numerical core

Untouched. No formula, constant, schema, parameter map or gate threshold changed;
Increments A and B have an empty `git status`. The T-12S digest, the aggregate
deviations and every Review-B-v2 anchor are unaffected by anything in this
remediation, which altered one function signature (a pure widening), two binding
constants, four citation lines and test code.

---

## 11. Immediate next action

1. **Decisive Review C v2** — read-only, at MNL
   `c2cf6a36a17e63f6da9922b2cf0fe0e8b9a1fd36`. Per review v1 §9 the re-review
   need cover only the changed files —
   `run_p2a_phase5_inference.py`, `p2a_phase5_inference_v1.yaml`,
   `test_p2a_phase5_runner.py` — plus this report, a re-run of the Increment-C
   suite and PROOF-10. Every other result in review v1 stands. The verdict must
   be written to
   `docs/France_case/P2a/FR_P2a_streaming_incrementC_review_v2.md` with exactly
   one `**FINAL VERDICT: APPROVE**` line and no indented mention of the token,
   because that document is now the authorization instrument.
2. **On APPROVE**: follow §6 exactly — commit *everything together first*
   (sources, tests, report v1, this report, review v1, review v2, the dual-filed
   charter, the ledger), then invoke the run with `--expected-mnl-head` set to
   that new commit and `--approved-review-sha256` recomputed on the committed
   review v2. Committing after creating the approval is what makes the
   cleanliness arm pass.
3. **Audit the dry run** against increment report v1 §9 items 1, 3 and 4, and
   confirm R-46b's gating-tier arm (§9.2) reports `applicable = true` and passes.
4. **Do not create `complete/`**; promotion remains deputy-reserved.
5. **Carry the open debt forward** unchanged: review D3 (T-23S evaluated on 16 of
   19 members), D4 (remaining unread config keys), D5 (`ad_mode` absent from the
   cross-tuple refusal), D6 (canonical-root prefix check), D7 (informational).
   None was in remediation scope and none blocks.

**FINAL VERDICT: READY FOR DECISIVE REVIEW V2**
