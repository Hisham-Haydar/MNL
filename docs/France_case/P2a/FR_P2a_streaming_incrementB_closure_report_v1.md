# FR P2a — JMP-M05C Increment B — three-fix mechanical closure report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Authority:** `JMP_M05C_incrementB_proportionality_decision_v1.md` (deputy, 2026-08-03), under `JMP_certification_proportionality_rule_v1.md`
**Target:** exactly the three residual defects of Review B v2 §7
**Mode:** test-first mechanical closure. No commit. No Increment C. No full-population run.
**Date:** 2026-08-03
**MNL HEAD (unchanged throughout):** `92e299de6313bad0b0421c0db3dd268fdbcfdb59`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

> **Heading note.** The task prompt body specifies 17 headings and the verdict
> string `READY FOR FOCUSED INCREMENT-B CLOSURE REVIEW`; the Goal-1 Manager
> addendum, marked binding, specifies 8 headings and the verdict string
> `READY FOR FOCUSED VERIFICATION`. This report follows the **addendum**, as the
> binding instrument, and folds the prompt-body sections (scope, probe
> provenance, files modified, numerical/statistical/package preservation, proof
> results, artifact integrity, nonblocking technical debt, whether focused
> review may begin) into those eight headings so nothing is dropped.

---

## 1. Closure verdict

**READY FOR FOCUSED VERIFICATION**

The three frozen probes were written and run **before** any implementation
change, and all three failed against the pre-fix state for exactly the reasons
Review B v2 §7 gives. Three localized corrections were then applied. The same
three probes — byte-identical, never re-touched after freezing — now pass.

| Review B v2 §7 defect | Pre-fix probe failure | Post-fix |
| --- | --- | --- |
| 1. T-22 expected name set caller-overridable | `AssertionError: a forged expected-name set satisfied T-22` (`passed=True`, `required_names=['forged_active']`) | PASS — parameter removed |
| 2. Serializers refuse only after writing | `AssertionError: matrix: refusal left files behind: [('phase5_covariance_model.npy', '1daead27…')]` | PASS — destination absent/byte-identical |
| 3. `extra=` persists prohibited content | `AssertionError: score_block_5x37: a row-level score block was persisted` | PASS — channel removed |

Scope was held to exactly these three. No new gate, no additional hardening, no
refactor beyond what the three fixes strictly entail. The numerical core is
untouched: **all 18 Review B v2 §5 regression values reproduce exactly** (§6).
The 13-column schema, every constant, the Increment-A files and the four prior
Increment-B documents are byte-identical.

**Scope, in one line** (prompt-body §2): the three frozen probes, three
localized corrections, the existing regression suites, and this report. Nothing
in the numerical or econometric implementation, covariance formulas, gradient
source, parameter maps, active-bound interpretation, schemas, constants,
accepted likelihood/theta/Hessian/bundles, Increment-A source, or
`dclaborsupply` was altered. No runner, transaction, reproduction or
Increment-C functionality was added.

---

## 2. Starting state

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `92e299de6313bad0b0421c0db3dd268fdbcfdb59` | identical | PASS |
| Untracked set | exactly the six declared files | exactly those six | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean | PASS |

Untracked at task start:

```text
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_refix_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_review_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_review_v2.md
?? scripts/p2a/p2a_phase5_inference.py
?? tests/p2a/test_p2a_phase5_inference.py
```

### 2.1 Files modified

| Path | Before (Review B v2 §2) | After | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/p2a_phase5_inference.py](scripts/p2a/p2a_phase5_inference.py) | `506e9dc5574563a2ba233a87f25c025e6a54f4c372a5835517b3e89d691447e9` | `c8f371eeb5b52bbe1f62ef056cb66352839b7d573562fe7c1c331f7f96d8a466` | 1,486 → 1,527 |
| [tests/p2a/test_p2a_phase5_inference.py](tests/p2a/test_p2a_phase5_inference.py) | `f5a4bbf89b5a75fab8739b5955869a392db1342b4121c9bfd1ff0dae464c468b` | `5ae1aa88856241cccc298312e88971acccf8ecea32d73d07cdbb58f71d7e66e1` | 1,107 → 1,302 |

Byte-identical, verified against a task-start snapshot:

| Path | SHA-256 |
| --- | --- |
| `FR_P2a_streaming_incrementB_report_v1.md` | `3e9e69cf20321c889c2ec0284d3d3cc55e825c3a64615f8fc877ce46272c76b0` |
| `FR_P2a_streaming_incrementB_refix_report_v1.md` | `638c5f2788b8fac1285f12174ce4803b214b8c74c235be39ae052987d5f6dd27` |
| `FR_P2a_streaming_incrementB_review_v1.md` | `822b0fbc91ab6f906bca2dd49931bbbd27f9ee4bfa25f87db4cbd95a06b3a3af` |
| `FR_P2a_streaming_incrementB_review_v2.md` | `f045bf6c73582b48803be531abe784f95caea5eec17057806c9b6cf01e6e52bb` |

`git status` for the three committed Increment-A files is empty. Both modified
files remain LF-only, so the hunk maps below are meaningful. `git diff --check`
exits 0.

### 2.2 Frozen probe provenance

The three probes were appended to the test file and run against the **unmodified**
implementation (`506e9dc5…`) before any fix. The probe file was hashed at that
moment:

```text
frozen probe file  5ae1aa88856241cccc298312e88971acccf8ecea32d73d07cdbb58f71d7e66e1  61200 bytes
implementation     506e9dc5574563a2ba233a87f25c025e6a54f4c372a5835517b3e89d691447e9  (pre-fix)
```

**The final test-file hash is `5ae1aa88856241cccc298312e88971acccf8ecea32d73d07cdbb58f71d7e66e1` — identical.**
The probes were therefore not modified, corrected or weakened after freezing; no
before/after correction hash pair is required, because no correction occurred.

One ordering detail, disclosed: `hashlib` had been dropped from the test
module's imports during the earlier refix (it was unused then). The import was
restored as part of **writing** the probes, i.e. before the first probe run and
before the hash above was taken, so it is inside the frozen artefact rather than
a post-freeze edit. It is test-infrastructure only and touches no assertion.

Probes are deliberately written to accept **either** admissible closure the
decision allows — "the argument/channel is gone" (`TypeError`) or "the input is
rejected before any write" — so each probe pins the contract rather than one
chosen implementation of it.

---

## 3. Fix 1 — B-1, T-22 authority

**Defect (Review B v2 §3.2, §7.1).** `gate_T22_numerical_kkt` exposed
`active_names` as a caller-controlled argument defaulting to
`ACTIVE_BOUND_NAMES`. The direct call

```python
gate_T22_numerical_kkt({'forged_active': 1.0}, 1e-4, active_names=('forged_active',))
```

returned `passed=True` and reported `required_names=['forged_active']`, so the
gate did not invariably authenticate against the certified pair.

**Correction.** The `active_names` parameter is **removed**. The gate binds
unconditionally to the module's frozen `ACTIVE_BOUND_NAMES`. It still accepts
observed gradient values from the caller — that is the gate's input — but no
longer accepts a replacement expected-name authority in any form, by keyword or
positionally.

On the decision's alternative ("the frozen authenticated constant checked
against that map"): the equality of `ACTIVE_BOUND_NAMES` with the pair derived
from the authenticated parameter map is asserted by the pre-existing `test_I11`
and again by probe B-1 item 3. A runtime `pmap` argument was deliberately *not*
added, because a caller-supplied map would reinstate exactly the defect being
closed in a different guise — a forged map naming `forged_active` would then be
accepted as the authority.

**Hunk map** (module, `diff -U0` against the pre-fix snapshot):

| Hunk | Location | Change |
| --- | --- | --- |
| 1 | `@@ -1056,3 +1056 @@` | signature: `active_names` parameter deleted |
| 2 | `@@ -1061,4 +1059 @@` | docstring: stale "Fix 2" preamble condensed |
| 3 | `@@ -1066,0 +1062,11 @@` | docstring: closure B-1 rationale |
| 4 | `@@ -1068 +1074 @@` | body: `expected = tuple(ACTIVE_BOUND_NAMES)` |

**Frozen probe re-run** — `test_CLOSURE_B1_t22_expected_name_set_is_not_caller_overridable`:

```text
pre-fix : FAILED — AssertionError: a forged expected-name set satisfied T-22
          (GateResult(..., passed=True, bar={'required_names': ['forged_active'], ...}))
post-fix: PASSED
```

Post-fix behaviour: both the keyword and the positional forgery now raise
`TypeError` (the argument does not exist); the certified mapping still passes
with `required_names == ['beta_l_age2_sm', 'beta_l_age2_sf']`; and
`{'forged_active': 1.0}` alone still fails on the name check.

---

## 4. Fix 2 — B-2, refusal leaves the destination untouched

**Defect (Review B v2 §3.4, §7.2).** All three serializers validated a nonempty
`inference_grade` only inside `_record`, which each writer called **after**
creating its target. Empty-grade calls raised `IB-REFUSE` while leaving the
target present, so a refusal was not byte-neutral.

**Correction.** A new `_require_grade(member, inference_grade)` performs the
validation, and is called at the **top** of each writer — before
`path.parent.mkdir`, before `np.save`/`to_csv`/`write_text`, before any
temporary file. `_record` retains the same check as defence in depth, where it
can no longer be the first to fire. The check also now rejects a non-`str` or
whitespace-only grade, which is the same condition stated exactly rather than
relying on falsiness.

Ordering after the fix, for every writer: member allowlist → grade → payload →
member contract → (names) → *first write action*.

**Hunk map:**

| Hunk | Location | Change |
| --- | --- | --- |
| 5 | `@@ -1372,4 +1378,10 @@` | new `_require_grade` with closure B-2 rationale |
| 6 | `@@ -1378,0 +1391,8 @@` | `_record` now delegates to `_require_grade` |
| 7 | `@@ -1388 +1408,5 @@` | `write_matrix` docstring: pre-write ordering |
| 8 | `@@ -1389,0 +1414 @@` | `write_matrix`: `_require_grade` call |
| 9 | `@@ -1411 +1436,4 @@` | `write_table` docstring: pre-write ordering |
| 10 | `@@ -1412,0 +1441 @@` | `write_table`: `_require_grade` call |
| 12 (part) | `@@ -1433,2 +1460,17 @@` | `write_score_aggregate_summary`: `_require_grade` call |

**Frozen probe re-run** — `test_CLOSURE_B2_refusal_leaves_the_destination_untouched`:

```text
pre-fix : FAILED — AssertionError: matrix: refusal left files behind:
          [('phase5_covariance_model.npy', '1daead27b7c9fe8ac09e2105459965edfcbcb6736bce86ed568ddcad1db0f76f')]
post-fix: PASSED
```

The probe covers all four writer paths (`.npy` matrix, `.csv` matrix, table,
JSON summary) in both starting conditions the decision names: a **nonexistent**
destination that must remain nonexistent, and a **sentinel** destination whose
bytes and hash must be unchanged. Both are checked by full directory
fingerprinting (`(relpath, sha256)` for every file under the target), plus an
explicit assertion that no partial or temporary file exists at the target.

---

## 5. Fix 3 — B-3, no arbitrary `extra=` persistence

**Defect (Review B v2 §3.5, §7.3).** `write_score_aggregate_summary` accepted an
unrestricted `extra: Optional[Dict[str, Any]]` merged into the payload *after*
construction. `extra={'temporary_scores_free37': np.zeros((5,37)).tolist()}`
persisted a complete row-level score block; `extra={'inference_grade': ''}`
overwrote a protected field while the returned record still reported the true
grade. This is the one defect the deputy classed as independently sufficient to
block, because it contradicts the no-row-level-persistence and disclosure
contract.

**Correction.** The `extra=` channel is **removed** — the decision's preferred
baseline (§3 B-3: "remove `extra=` entirely unless Increment C has a specific
accepted need for named scalar extensions"). Increment C has declared no such
need, so the allowlist alternative was not built.

Every payload field is now constructed exclusively inside the serializer from
`stream_result` and `inference_grade`. There is **no caller-supplied content
path into this artifact at all**, so the surface is closed by construction
rather than by filtering: no allowlist to get wrong, no type screen to bypass,
no protected-field collision check to forget. Protected fields cannot be
overwritten because nothing can reach them.

**Hunk map:**

| Hunk | Location | Change |
| --- | --- | --- |
| 11 | `@@ -1423,3 +1452 @@` | signature: `extra` parameter deleted |
| 12 | `@@ -1433,2 +1460,17 @@` | docstring: closure B-3 rationale (+ the B-2 call, above) |
| 13 | `@@ -1435,0 +1478 @@` | (docstring continuation) |
| 14 | `@@ -1457,2 +1499,0 @@` | body: `if extra: payload.update(_jsonable(extra))` deleted |

**Frozen probe re-run** — `test_CLOSURE_B3_no_arbitrary_extension_persistence`:

```text
pre-fix : FAILED — AssertionError: score_block_5x37: a row-level score block was persisted
          ('temporary_scores_free37' present in the written payload)
post-fix: PASSED
```

The probe drives eight attempts, each starting from a nonexistent destination:
the reviewer's `5×37` block as a nested list and as an `ndarray`; a
household-scale 1,555-element sequence; a nested container carrying a score
block; raw `bytes`; and overwrites of three protected fields
(`inference_grade`, `score_stream_sha256`, `n_households`). Post-fix every
attempt raises `TypeError` — the channel does not exist — and the destination
is asserted empty.

---

## 6. Regression

### 6.1 Numerical core

All 18 values Review B v2 §5 published reproduce **exactly** (`==`, not
`allclose`) on the first-64 production path:

| Quantity | Reproduced | Quantity | Reproduced |
| --- | ---: | --- | ---: |
| raw bread asymmetry | `1.8189894035458565e-12` | robust cov min eig | `-9.474781170961761e-20` |
| bread min eigenvalue | `0.10373269638807983` | regional robust min eig | `1.7170023605273287e-06` |
| bread condition number | `405353.9471978127` | W-1 ratio min | `0.06105116993643892` |
| meat asymmetry | `0.0` | W-1 ratio max | `0.4261454847830435` |
| meat min eigenvalue | `2.0597024553162405e-13` | meat numerical rank | `34` |
| correction | `1.0230263157894737` | W-5 score-sum ∞-norm | `22.52139019527921` |
| solve-vs-pinv deviation | `1.9602097722781764e-12` | interior max \|grad\| | `0.00010992597206183063` |
| `max(abs(H_II @ V_model − I))` | `1.2038803846172754e-14` | `μ_sm` | `0.8445544161794221` |
| T-19 maximum ratio | `0.0003819780309704067` | `μ_sf` | `1.4682021491125388` |

T-22 activity ratios remain `7682.9` and `13356.3`. The three corrections
touched an argument list, a validation call site, and a payload-merge line —
no arithmetic.

### 6.2 Statistical-design, package and artifact preservation

* **Statistical design.** No covariance formula, gradient source, parameter map,
  active-bound interpretation, schema or constant changed. The 13-column
  parameter schema and the 16-member aggregate artifact set are unchanged.
* **Accepted artifacts.** Phase-3 bundle
  `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`;
  Phase-4 bundle `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`;
  bread `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061`;
  theta `c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`.
  All four rehash to their anchors.
* **Package boundary.** `dclaborsupply-monorepo` HEAD equals the gitlink at
  `27756a06ea189339aa82915ed2124628afed20eb` and its worktree is clean.
* **No row-level persistence.** Generated Phase-5 artifact files: `NONE`;
  Phase-5 output directories: `NONE`. Phase-3 `attempts/` = 70 before and after.
* **No Increment-C code.** A grep for runner/transaction/staging/manifest-writer/
  lock/reproduction/CLI constructs returns only docstring text and read-paths to
  the accepted `complete/` bundles.

---

## 7. Test results

```text
[1] three frozen probes                     3 passed,  85 deselected in 1.11s
[2] Increment-B suite, run 1               88 passed in 5.75s
[2] Increment-B suite, run 2               88 passed in 5.61s
      fast (-m "not production")           79 passed,  9 deselected in 1.36s
      production (-m production)            9 passed, 79 deselected in 5.49s
[3] committed Increment-A suite            76 passed in 68.56s
[4] safe broader suite (test 29 deselected) 225 passed, 1 deselected in 89.59s
[6] git diff --check                       exit 0
    ruff check --select F,E9               All checks passed!
```

Increment-B grew 85 → 88 (+3): exactly the three frozen probes. Repository total
225 = 137 pre-existing + 88.

### 7.1 Proof results — the twelve existing reviewer-runnable proofs

Refix report §10 remains the PROOFS packet; all twelve were re-executed verbatim
in PowerShell with `.\.venv\Scripts\python.exe` from `C:\Users\hisham\Repo\MNL`.

| Proof | Review B v2 observed | Now | Result |
| --- | --- | --- | --- |
| PROOF-1 | five untracked paths | six (this report added) | PASS |
| PROOF-2 | four hashes | identical | PASS |
| PROOF-3 | `85 passed` | `88 passed in 5.48s` | PASS (+3 probes) |
| PROOF-4 | `76 passed, 9 deselected` | `79 passed, 9 deselected in 1.36s` | PASS (+3) |
| PROOF-5 | `9 passed, 76 deselected` | `9 passed, 79 deselected in 5.49s` | PASS |
| PROOF-6 | `12 passed, 73 deselected` | `12 passed, 76 deselected in 0.42s` | PASS |
| PROOF-7 | `6 passed, 79 deselected` | `6 passed, 82 deselected in 1.12s` | PASS |
| PROOF-8 | `19 passed, 66 deselected` | `19 passed, 69 deselected in 1.27s` | PASS |
| PROOF-9 | `20 passed, 65 deselected` | `20 passed, 68 deselected in 1.20s` | PASS |
| PROOF-10 | `222 passed, 1 deselected` | `225 passed, 1 deselected in 94.45s` | PASS |
| PROOF-11 | `NONE` / `NONE` | `NONE` / `NONE` | PASS |
| PROOF-12 | every scalar reproduced | every scalar reproduced | PASS |

**Only the deselected/total counts move, by exactly +3**, which is the three
probes. PROOF-1's expected untracked block gains this closure report; a focused
reviewer should expect six paths, not five. No proof command text needs editing.

### 7.2 Nonblocking technical debt

Recorded under the proportionality rule §3, **not** proposed for action:

1. `_record` still re-validates the grade after the writers already have. It is
   dead defence in depth, kept deliberately; removing it would be a refactor
   beyond the three fixes.
2. Removing `extra=` forecloses named scalar extensions. If Increment C later
   needs one, it requires an explicit keyword-only scalar field plus allowlist
   per the decision §3 B-3 — not a generic mapping.
3. `write_matrix`/`write_table` still accept a caller `metadata` mapping that
   reaches `ArtifactRecord.metadata` (in-memory only, never the artifact bytes).
   Out of scope for these three fixes and with no persistence consequence.
4. The pandas-stub type-checker notes on `frame.attrs.update(...)` and
   `float(Scalar)` persist; runtime behaviour is correct and lint is clean.

### 7.3 Whether focused verification may begin

**Yes.** The decision §4 acceptance criteria are met: the exact three frozen
probes pass (§3–§5); the Increment-A and Increment-B regression suites pass
(§7); numerical outputs, constants, schemas and source authorities are unchanged
(§6); no row-level score artifact is written (§6.2); and accepted bundles and
the nested package are unchanged (§6.2). The remaining item is the focused
reviewer's binary `PASS`/`FAIL`.

---

## 8. Immediate next action

1. **Focused Increment-B closure review** — read-only, at MNL
   `92e299de6313bad0b0421c0db3dd268fdbcfdb59`, scope limited by the
   proportionality decision §2 and §5 to: the three frozen probes, the three
   hunk maps of §3–§5, the §6 regression, and exact-state integrity. The verdict
   is binary. Per the rule §4, a new finding may block only if it falls in
   proportionality-rule §2 (econometric correctness, accepted-artifact use,
   production path, reproducibility, provenance, row-level persistence or
   disclosure, evidence loss, paper-facing interpretation); anything else is
   recorded as nonblocking debt.
2. **Expect six untracked paths in PROOF-1**, not five — this report is the
   sixth. No other proof text changes; counts move by exactly +3.
3. **On `PASS`**: commit the exact reviewed Increment-B state with both worktrees
   clean, update the JMP-M05C ledger, and authorize **Increment C** under
   `JMP_certification_proportionality_rule_v1.md` §6 — production runner
   execution, fresh-process reproduction, aggregate-only transaction, STOPPED
   truthfulness, no `complete/`, no row-level persistence, accepted-artifact and
   revision binding. Increment C must not restart capability-security or
   import-surface certification.
4. **On `FAIL`**: per the decision §5, the manager may correct only a direct
   implementation error in one of these same three frozen probes; any new review
   class or architectural redesign requires deputy escalation.

**FINAL VERDICT: READY FOR FOCUSED VERIFICATION**
