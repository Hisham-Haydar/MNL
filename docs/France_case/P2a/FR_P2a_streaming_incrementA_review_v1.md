# FR P2a — JMP-M05C streaming inference — Increment A independent review — v1

**Review mode:** independent, read-only except for this review file  
**Review date:** 2026-08-02  
**Implementation base:** `b5169293b647dda3e07070c678f8d46d33b1bf89`  
**Nested gitlink/HEAD:** `27756a06ea189339aa82915ed2124628afed20eb`

## 1. Review-A verdict

**FINAL VERDICT: REJECT**

The accepted loader and likelihood are genuinely exercised, the reducer's
successful-path aggregates are numerically correct, and the first-64-household
reviewer check passes the frozen T-11 and T-16 bars. Approval is nevertheless
barred by two demonstrated contract failures in the delivered boundary:

1. a failed reducer call leaves the transient `(batch, 37)` score array reachable
   through the exception traceback, contrary to the required failure-path
   no-persistence proof; and
2. `ScoreStreamReducer.update` silently truncates forged non-integral batch IDs
   before hashing, contradicting the published `int64_le` encoding claim.

The shipped test also labels a 24-household comparison as T-16 even though design
v4 T-16 freezes the first 64 households. The report's PROOFS packet is not
verbatim-reproducible, and the worktree has four unexpected files produced by two
prohibited full-suite executions of test 29. These are five required fixes, not
one narrow remediation.

## 2. Scope and exact state

The review read the M05C charter §§4-A and 5, streaming addendum §§2, 5 and 9,
design v4's score formulas, parameter maps, T-11/T-16 definitions and numerical
bars, `phase5_parameter_map_v1.csv`, `phase5_source_inventory_v1.json`, the three
delivered implementation/test files, and the implementation report. The report
was treated as claims to test.

State observed before this review file was created:

- MNL HEAD exactly `b5169293b647dda3e07070c678f8d46d33b1bf89`;
- HEAD's parent is `ffd060f7a0f4535150498aae6361a3df35cf8b53`;
- the addendum commit contains exactly its one reported file;
- the nested repository HEAD equals the MNL gitlink at `27756a06…` and its
  worktree is clean;
- the three implementation/test deliverables and report are untracked as
  expected; and
- four additional untracked files exist under two Phase-3 dry-run attempt
  directories, timestamps `20260802T153430Z…` and `20260802T155349Z…`.

Those four attempt files are outside the supplied exact expected set and are a
finding. They resulted from running the full suite without deselecting test 29,
as the report itself acknowledges. The reviewer did not modify, delete, stage or
commit them. All reviewer test runs used bytecode/cache suppression; the safe
full-suite run deselected test 29. State remained unchanged through testing.

No full-population score run was performed. The largest score evaluation was the
design-prescribed first-64-household T-16 check. No accepted bundle member or
nested-package file was changed.

## 3. Proofs executed

Every printed PROOFS command was attempted. Where the report required a file
creation or an unspecified environment activation, the exact failure was
retained and a file-free/intended-environment merits check was run separately.

| Proof | Observed result | Adjudication |
| --- | --- | --- |
| PROOF-1 | HEAD, one-file commit stat, gitlink, nested HEAD and empty nested status all matched. `HEAD~1` identified `ffd060f…`. | PASS |
| PROOF-2 | Phase-3 `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`; Phase-4 `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`. Including manifests instead gave `d2115d…` and `311414…`. | PASS |
| PROOF-3 | All selected tests passed, but actual output is `29 passed, 13 deselected`, not the expected `29 passed, 12 deselected`. C5–C9 reproduced their rejection paths; an in-memory one-hex mutation produced the claimed C3 red bar without editing a file. | FAIL exact-output rule |
| PROOF-4 | `8 passed`; D2 demonstrated that the scanner detects its probe. The result does not prove the stronger failure-path claim because D6 checks only `str(exc)`, cwd files and not exception traceback references. | Command PASS; claim FAIL |
| PROOF-5 | From the repository root as printed, `python` resolved to CPython 3.14.2 without JAX: 12 setup errors and one failure. With the repository `.venv` activated while leaving the pytest command unchanged, the production family passed `13 passed, 29 deselected`, not the expected `12 passed, 29 deselected`. | FAIL reviewer-runnable/exact-output rule; implementation tests PASS in intended environment |
| PROOF-6 | `6 passed`; A3/B3/B4/E10/E11/E12 reproduced the stated map, order, evaluator-mutation and dtype rejection demonstrations. | PASS |
| PROOF-7 | In Git Bash: attempts `72 → 72`, dirty files `8 → 8`, and `42 passed`. Increment-A tests created no additional repository member. | PASS, while confirming the pre-existing unexpected files |
| PROOF-8 | Exact `python proof8.py` failed because `proof8.py` does not exist and this review was allowed to create only the review file. The unchanged code run through stdin reproduced every expected scalar exactly. | FAIL reviewer-runnable rule; numerical body PASS |

The report's instructions to edit `SYNTH_DIGEST` and to save `proof8.py` are not
read-only, exact commands. They must be replaced with file-free commands or
committed test cases. The report also needs an exact `.venv` activation or an
exact interpreter path before any `python` proof.

Additional regression command, with the mandated deselection:

```text
python -m pytest -q -k "not test_29_subprocess_dry_run_never_optimizes"
103 passed, 1 deselected in 82.77s
```

## 4. Production-path integrity

Production-path integrity passes on the merits.

- `tests/p2a/conftest.py` only registers the `production` marker. It defines no
  evaluator, reducer, loader, fixture or autouse hook.
- The module and production fixture import the actual
  `dclaborsupply.data.loader.load_singles` and
  `dclaborsupply.likelihood.engine_jax.build_jax_singles_ll` objects.
- Reviewer-recomputed SHA-256 values match the committed source inventory:
  loader `68cf26f141d1459043f3fba32df503518e45c87310c23a1c04afd66a4220a651`,
  likelihood `49bf6b7048f0065f248bf49dc750797ca9d9809c2aade29bd8808baeea2ceeed`,
  frozen parquet `8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`,
  and metadata `05be40300288bdfb82a1f29d3649b420ee055e548658b6556424d024a87f5de1`.
- E2's production leg calls `run_score_stream` and the actual
  `ScoreStreamReducer`. The direct `jacrev` code is only the independent
  comparison leg; it does not replace the reducer that produces the tested
  result.
- E11 and E12 monkeypatch subjects only inside explicit mutation/rejection
  demonstrations. They do not manufacture a green production result.
- The only production integration reduction is the bounded canonical prefix.
  No likelihood formula, loader, reducer or parameter map is substituted.

The production source route therefore satisfies charter §5. This conclusion
does not cure the proof-count/environment defects in §3 or the failure-path
defect in §5.

## 5. No-persistence

The successful path is appropriately aggregate-only: the module has no file or
logging write call, stdout/stderr tests are silent, the result's only arrays are
`(37,)`, `(37,37)` and `(35,35)`, and a successful reducer update does not retain
the caller's batch array. The digest is updated row by row in memory and the
hash object exposes only digest state, not a row-level artifact.

The failure-path claim does not pass. A reviewer probe raised the shipped
non-finite-score error and traversed `exc.__traceback__`. The same `(3, 37)`
float64 score array remained reachable in these module/call frames:

```text
('trigger', 'scores', (3, 37), 'float64')
('update', 'scores', (3, 37), 'float64')
('_check_batch', 'scores', (3, 37), 'float64')
```

Thus the transient score bytes can travel with the exception traceback and can
be exposed by traceback/logging systems that render locals. D6 asserts only that
the exception *message* omits values and that its temporary cwd is empty; it
never inspects `__traceback__`, `__context__` or `__cause__`. This is a
false-green against the review checklist and the addendum's failure-path release
requirement.

No reviewer run found a row-level score file, console emission or returned score
matrix. The defect is specifically reachability through failure exception state,
not successful-path disk I/O.

## 6. Numerical conformance

The reducer is numerically conformant on the actual accepted loader/likelihood
route.

| Check | Frozen bar | Observed | Result |
| --- | --- | --- | --- |
| Report subset T-11, batch 3 vs 8 | `3.023468094208269e-11` | `8.881784197001252e-16` | PASS |
| Report subset T-11, batch 24 vs 8 | `3.023468094208269e-11` | `0.0` | PASS |
| Report subset forward/reverse | `3.023468094208269e-09` | `1.0658141036401503e-14` | PASS |
| Design T-11, first 64, batch 16 vs 64 | `3.023468094208269e-11` | `0.0` | PASS |
| Design T-16, first 64, forward vs reverse | `3.023468094208269e-09` | `7.105427357601002e-15` | PASS |

On the real first-64 streamed result, both meat asymmetries were exactly `0.0`.
The 35×35 meat was bitwise equal to the by-name selected block of the 37×37
meat. The selector is authenticated from the CSV status/name sequence against
the Phase-4 manifest; its two excluded names are `beta_l_age2_sm` and
`beta_l_age2_sf`, not hard-coded positional deletion. The T-17 fingerprints
also reproduced (`cb50ecd8…` free-37 and `44af628f…` interior-35).

The shipped E5 test is nevertheless not the frozen T-16 test: it uses the first
24 households, while design v4 T-16 states the first 64. The reviewer result
shows the code passes at 64, so this is a test/report conformance defect rather
than a numerical implementation failure.

## 7. Manager rulings

**R-32a — UPHOLD the byte contract, but do not freeze this implementation yet.**
Signed int64 little-endian is explicit, portable, published on the result, and
the score rows are correctly encoded as 37 little-endian float64 values. The
choice is meritorious. However, `_check_batch` compares
`batch.idhh.astype(np.int64)` and the digest then calls `int(batch.idhh[k])`.
A forged canonical-looking batch with IDs `10.5, 20.5, 30.5` was accepted and
produced the same digest as integer IDs `10, 20, 30`. The reducer boundary must
reject non-integral IDs before this ruling is frozen into an Increment-C
artifact.

**R-32b — UPHOLD.** Digest validity is scoped to a fixed `(encoding, batch size,
AD mode)` tuple, with the numerical environment also recorded as required by the
addendum. The measured 1-ULP batch-shape difference and forward/reverse
difference make a tuple-scoped reproduction gate necessary. Freeze the tuple at
Increment C's reproduction gate and refuse cross-tuple digest comparison.

**R-32c — UPHOLD.** In a fresh reviewer process, `jax_enable_x64` was `False`
before binding and `True` after `build_production_binding`. With the accepted
initializer temporarily made ineffective in memory, the binding refused to
proceed. E12 run in isolation also rejected a raw float32 Jacobian before NumPy
could upcast it. Eager activation plus post-activation refusal and raw-dtype
checking genuinely closes the lazy-initialization false-green identified by the
report.

## 8. Residual defects

1. **NP-1 — score array retained by failure traceback (blocking).** The delivered
   no-persistence proof checks messages and files, not exception object graphs;
   module frames retain the score array after failure.
2. **DG-1 — non-integral batch IDs silently truncated (blocking).** The public
   reducer accepts a forged non-integral batch and hashes truncated IDs, contrary
   to its published encoding and report claim.
3. **T16-1 — wrong frozen test slice.** E5 and PROOF-8 exercise 24 households,
   not design v4's first 64, even though an independent first-64 run passes.
4. **PR-1 — PROOFS are not verbatim-reproducible.** The environment activation
   is absent, two expected test counts are stale, PROOF-8 requires an absent
   reviewer-created file, and edit-based failure demonstrations violate the
   read-only role.
5. **ST-1 — exact-state violation.** Four unexpected Phase-3 attempt files remain
   from two full-suite runs that did not deselect test 29.

No runner, transaction, bread, covariance, standard-error or Wald code is
smuggled into Increment A. The aggregate result exposes the score sum, the two
meats, the single global digest and scalar/contract metadata only. Import-callable
batch-score helpers are permitted by addendum §9 and do not themselves add a
runner or persistence surface.

The report's disclosed absence of the all-1,555 score-identity gate, bread,
covariance and transaction objects is correct Increment-A non-scope, not an
additional defect.

## 9. Required fixes

Exactly five fixes are required before a new Review A:

1. Restructure public failure boundaries so no module exception traceback,
   chained exception or exception payload retains a transient score array after
   failure. Add tests that traverse traceback/context/cause object graphs and
   fail on row-level score arrays or bytes; retain the existing message, disk and
   stdout/stderr checks.
2. Validate batch IDs at the reducer boundary without lossy casting. Reject
   non-integral, non-finite, out-of-range or non-canonical representations before
   digest update, and add a forged-float batch failure test proving that `.5`
   identifiers cannot hash as their truncated integers.
3. Make the production T-16 test use the frozen first 64 canonical households
   and report its actual bar and deviation. Keep the existing smaller tests only
   as additional smoke coverage, not as T-16 evidence.
4. Repair the implementation report's PROOFS section: provide an exact intended
   interpreter/activation command, correct the E12-era counts to 29/13 and
   13/29, and replace `proof8.py` creation and edit-based red bars with exact
   file-free read-only commands or committed tests.
5. Obtain the manager-authorized disposition of the four unexpected test-29
   attempt files, restore the exact expected worktree, and record a safe
   full-suite command that always deselects test 29.

## 10. Whether Increment B may begin

No. Increment B must not begin. The no-persistence and digest-validation defects
touch two core Increment-A contracts, and the remaining proof/state defects
exceed the charter's one-narrow-remediation budget. Complete all five fixes,
restore exact state, and submit a fresh independent Review A before proceeding.
