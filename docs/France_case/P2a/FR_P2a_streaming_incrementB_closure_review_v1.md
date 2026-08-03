# FR P2a — JMP-M05C Increment B focused closure review — v1

## 1. Focused review verdict

**FINAL VERDICT: PASS**

Every re-runnable check specified by the review instrument reproduces
independently: the three frozen probes pass against the current source; live,
independently-constructed adversarial re-probes of all three defects (forged
T-22 name set, empty-grade write, `extra=` persistence/overwrite) fail exactly
as the closure is supposed to make them fail; the full Increment-A (76) and
Increment-B (88) suites and the guarded full-repository suite
(225 passed, 1 deselected) reproduce the closure report's exact counts;
all twelve reviewer-runnable proofs reproduce their claimed output verbatim;
accepted Phase-3/Phase-4 bundle, bread and theta hashes rehash to their
anchors; the nested `dclaborsupply-monorepo` gitlink and worktree are
unchanged and clean; no row-level score artifact or Increment-5 output
directory exists on disk; and no Increment-C code (runner, transaction,
manifest writer, `phase6`, etc.) exists anywhere in the reviewed files.

One limitation is flagged rather than silently resolved in the implementer's
favor: the probe files are untracked (this project's declared workflow commits
Increment-B only after a `PASS`), so there is **no git commit history** that
can independently timestamp "probes written and run before the fix." The only
available provenance is a SHA-256 hash chain quoted across four prior
documents (report v1, review v1, refix report v1, review v2) plus the closure
report itself. I recomputed every one of those hashes independently with
`sha256sum` against the files as they sit on disk today, and every one matches
its claimed value exactly (§3). That is real, non-fabricated evidence, but it
proves internal consistency of the paper trail, not the temporal claim that
the probes were frozen before the implementation was touched. Under the
certification proportionality rule §2/§3, this gap does not fall into a
blocking class (it is not accepted-artifact provenance, not reproducibility of
a reported *numerical* result, and does not touch row-level persistence); it
is recorded as a nonblocking documentation/provenance limitation in §3 and
§11, not silently accepted as proven.

## 2. Scope

Independent, read-only review at MNL HEAD `92e299de6313bad0b0421c0db3dd268fdbcfdb59`
(nested `dclaborsupply-monorepo` HEAD `27756a06ea189339aa82915ed2124628afed20eb`,
unchanged, worktree clean). No file was modified other than this report. No
commit was made. No Increment C work was started. No full population job was
run — only the existing unit/regression suites, `sha256sum`, `git`, `ruff`,
and direct Python probes against the installed `.venv` interpreter
(`Python 3.12.2`). I read the proportionality decision, the focused-review
prompt, the certification proportionality rule, the three-fix closure prompt,
the Goal-1-Manager resume prompt, Review B v1/v2, report v1, the refix report,
and the closure report in full before running anything, and treated every
claim in the closure report as unverified until reproduced myself.

## 3. Probe provenance

**Item 1 (probes added before implementation changes, or hashes/provenance
otherwise establish freezing) — UNVERIFIABLE via git.** `git log`, `git stash
list`, `git reflog`, and `git fsck --dangling --unreachable` were all checked;
`scripts/p2a/p2a_phase5_inference.py` and
`tests/p2a/test_p2a_phase5_inference.py` are untracked and have never been
committed, so git has no record of any earlier state. I also searched
`//crc/users/hisham/Desktop/tran/Copied/` and the full MNL working tree for
any archived pre-fix copy of either file; none exists. The claim that the
three probes were written and run against the unmodified pre-fix
implementation rests entirely on the closure report's own narrative.

**Item 2 (probes reproduce the original defects on archived/pre-fix source) —
UNVERIFIABLE.** No pre-fix source snapshot exists anywhere I could find, so
there is nothing to re-run the probes against to independently reproduce the
claimed pre-fix failures. I could not construct this test myself without
reverting the current file, which the task prohibits (no file modification
other than this report).

**Item 3 (implementer did not weaken or replace the probes) — supported, not
provable end-to-end.** Independently computed `sha256sum` of the current test
file is `5ae1aa88856241cccc298312e88971acccf8ecea32d73d07cdbb58f71d7e66e1`,
exactly matching the closure report's claimed "frozen" and "final" hash (they
are asserted identical to each other, i.e. no correction occurred). I also
independently confirmed every other document hash the closure report claims
as unchanged: `FR_P2a_streaming_incrementB_report_v1.md`
(`3e9e69cf...276b0`), `..._review_v1.md` (`822b0fbc...3a3af`),
`..._refix_report_v1.md` (`638c5f27...6dd27`), and `..._review_v2.md`
(`f045bf6c...e52bb`) — all match exactly. The source file's current hash
`c8f371eeb5b52bbe1f62ef056cb66352839b7d573562fe7c1c331f7f96d8a466` also
matches the closure report's claimed "after" hash. I then read the bodies of
`test_CLOSURE_B1_t22_expected_name_set_is_not_caller_overridable`,
`test_CLOSURE_B2_refusal_leaves_the_destination_untouched`, and
`test_CLOSURE_B3_no_arbitrary_extension_persistence` directly
(tests/p2a/test_p2a_phase5_inference.py:1139-1302): all three are
substantively adversarial (forged keyword/positional name sets; four writer
paths against both nonexistent and sentinel destinations with directory
fingerprinting; eight `extra=` attack payloads including the exact `5×37`
block, nested containers, raw bytes, and three protected-field overwrites),
not trivial stand-ins, and they match the residual defects named in Review B
v2 §7 verbatim. This is strong, independently-gathered circumstantial
evidence that the probes are genuine and were not weakened, but — per item 1 —
it cannot close the pure timing gap. **This is flagged as an explicit,
unresolved provenance limitation**, recorded as nonblocking per the
certification proportionality rule (it is a "proof-format or documentation
imperfection that does not prevent reproduction," not a Section-2 blocker),
but a human Goal-1-Manager judgment call, not something I can certify as
independently proven.

## 4. T-22 authority

**PASS**, independently verified by direct source reading and live probing.
`gate_T22_numerical_kkt` (scripts/p2a/p2a_phase5_inference.py:1055-1074) now
has the signature `(multipliers: Dict[str, float], interior_max_abs_grad:
float) -> GateResult` — the `active_names` parameter is gone entirely. I
called it directly:

```
gate_T22_numerical_kkt({'forged_active': 1.0}, 1e-4, active_names=('forged_active',))
  -> TypeError: got an unexpected keyword argument 'active_names'
gate_T22_numerical_kkt({'forged_active': 1.0}, 1e-4, ('forged_active',))
  -> TypeError: takes 2 positional arguments but 3 were given
```

The function binds unconditionally to the module-level constant
`ACTIVE_BOUND_NAMES = ("beta_l_age2_sm", "beta_l_age2_sf")` (line 68).
`test_I11` (line 674) and my own re-check both assert
`ib.ACTIVE_BOUND_NAMES == tuple(pmap.free_names[p] for p in
pmap.active_positions_in_free)`, i.e. the frozen constant is proved equal to
names derived from the authenticated parameter map, not merely declared. A
plain forged mapping alone (`{'forged_active': 1.0}` with no `active_names`
argument) still returns `passed=False`. The genuine certified pair
(`gr.active_multipliers`) still passes with `required_names ==
['beta_l_age2_sm', 'beta_l_age2_sf']`.

## 5. Pre-write serializer refusal

**PASS**, independently verified by direct source reading and live probing.
`_require_grade` (line 1378) is called at the top of `write_matrix` (line
1414, before `path.parent.mkdir` at line 1422), `write_table` (line 1441,
before `path.parent.mkdir` at line 1444), and `write_score_aggregate_summary`
(line 1478, before `path.parent.mkdir` at line 1501) — in every case before
any directory creation, temp file, or write call. `_record`'s own grade check
(line 1398) now fires only after the writers have already validated, making it
dead defense-in-depth as the closure report itself describes.

Live probe: calling `write_matrix(nonexistent_dir, ..., inference_grade='')`
raised `SerializerRefusal` and the directory was confirmed absent both before
and after (`os.path.exists` False/False). A second live probe against a
sentinel file (`SENTINEL-BYTES-DO-NOT-TOUCH`) confirmed the file's SHA-256 was
identical before and after the refused call. The frozen probe
`test_CLOSURE_B2_...` (line 1181) independently covers all four writer entry
points (`.npy` matrix, `.csv` matrix, table, JSON summary) against both
starting conditions with full directory fingerprinting, and passed when I ran
it.

## 6. No arbitrary score-summary extension

**PASS**, with one nonblocking finding. `write_score_aggregate_summary`'s
signature is now `(out_dir, stream_result, *, inference_grade: str) ->
ArtifactRecord` (line 1451) — the `extra` parameter is gone; `grep -n "extra"`
over the source shows no remaining `extra=` parameter path (the only other
hits are an unrelated local variable inside `gate_T22_numerical_kkt` counting
extra active-name keys, and docstring prose describing the removed channel).
Live probe: calling `write_score_aggregate_summary(..., extra={...})` raises
`TypeError: got an unexpected keyword argument 'extra'` for every attack
payload, including the reviewer's exact `5×37` block, a nested container, raw
bytes, and overwrite attempts on `inference_grade`, `score_stream_sha256`, and
`n_households`. Because the parameter no longer exists, none of these can
reach the payload by any means — the closure report's "closed by construction"
characterization is accurate: every payload field
(lines 1482-1499) is built exclusively from `stream_result` and
`inference_grade`, with no caller-supplied content path at all.

**Nonblocking finding.** `assert_aggregate_payload` (line 1250), called in
isolation, does **not** itself reject raw `bytes`/`memoryview` or a nested
`dict` containing an array — I confirmed this directly:
`assert_aggregate_payload(b'\x00'*80, 'x')` and
`assert_aggregate_payload({'nested': np.zeros((5,37))}, 'x')` both return
`None` with no refusal. In isolation this is a gap relative to the
proportionality decision's literal wording ("the serializer must ... reject
... bytes/memoryviews"). However, in every actual writer this function is
never called alone: `write_matrix` and `write_table` also call
`assert_member_contract`, which enforces an exact expected shape per member
(e.g. `(35, 35)` for the model covariance) and independently refuses bytes,
memoryviews, and nested dicts before any write, which I confirmed live for
both `write_matrix` and `write_table`. `write_score_aggregate_summary` has no
caller-content path at all (above), so the gap is unreachable there by
construction. Net effect: no real writer entry point can be made to persist
these payload types, but `assert_aggregate_payload`'s docstring ("Refuse
row-level or id-paired score content BY CONSTRUCTION") overstates what the
function does on its own — it is complete only in combination with
`assert_member_contract`. This does not affect the actual production path and
is recorded as nonblocking technical debt (§11), not a Section-2 blocker.

## 7. Numerical regression

**PASS.** I independently re-ran the full covariance pipeline
(`load_bread` → `run_score_stream` → `gate_T7_meat_validity` →
`build_covariances` → `build_parameter_table` → `run_regional_tests`) on the
first-64 production path and obtained, bit-for-bit:

| Quantity | Reproduced (this review) | Claimed (closure report §6.1) |
| --- | ---: | ---: |
| raw bread asymmetry | `1.8189894035458565e-12` | identical |
| bread minimum eigenvalue | `0.10373269638807983` | identical |
| meat minimum eigenvalue | `2.0597024553162405e-13` | identical |
| correction `c` | `1.0230263157894737` | identical |
| solve-vs-pinv deviation | `1.9602097722781764e-12` | identical |
| T-22 empty mapping | `False` | `False` |
| T-22 wrong-name mapping | `False` | `False` |
| T-22 exact certified pair | `True` | `True` |
| active multipliers | `beta_l_age2_sm=0.8445544161794221`, `beta_l_age2_sf=1.4682021491125388` | identical |
| interior max abs grad (`beta_w_educH`) | `0.00010992597206183063` | identical |
| `grad_negll` at `beta_w_educH` in table | `0.00010992597206183063` | identical |
| `inference_grade` (table / regional) | `subset-diagnostic` / `subset-diagnostic` | identical |
| 13-column schema intact | `True` | `True` |

Accepted-bundle rehash (independently recomputed): Phase-3
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`, Phase-4
`5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`, bread
`e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061`, theta
`c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d` — all match
the anchors quoted in review v2 and the closure report exactly.

## 8. Statistical-design preservation

**PASS.** `build_parameter_table` still requires `AcceptedGradients` as a
required positional argument and keys the free-coordinate gradient/multiplier
values by the authenticated free-name sequence (R-37b remains enforced; not
touched by this closure). `ACTIVE_BOUND_NAMES` is proved equal to the names
derived from the authenticated parameter map (§4). The 13-column parameter
schema (`name, block, status, estimate, bound_value, bound_side, grad_negll,
multiplier, se_model, se_robust, ratio_robust_model, z, p`) and the 16-member
`AGGREGATE_ARTIFACTS` set are unchanged and were independently counted. No
covariance formula, gradient source, parameter map, or active-bound
interpretation was touched by any of the three hunks I inspected (T-22 name
binding, `_require_grade` placement, `extra=` deletion) — none of them are
arithmetic changes. Every numerical value in §7 reproduces bit-for-bit against
the values review v2 and the closure report separately (and, for review v2,
independently of the closure) reported, which is strong evidence the
covariance/gradient arithmetic is untouched.

## 9. Package-boundary preservation

**PASS.** `git ls-tree HEAD dclaborsupply-monorepo` reports
`160000 commit 27756a06ea189339aa82915ed2124628afed20eb`; `git -C
dclaborsupply-monorepo rev-parse HEAD` returns the identical SHA; `git -C
dclaborsupply-monorepo status --porcelain --untracked-files=all` returns no
output (clean). `git diff --stat HEAD -- scripts/p2a/p2a_phase5_score_stream.py
tests/p2a/test_p2a_phase5_score_stream.py tests/p2a/conftest.py` is empty —
the three committed Increment-A files are byte-identical to HEAD.

## 10. Artifact and repository integrity

**PASS**, all items independently reproduced:

- Increment-B suite: `88 passed in 5.57s` (matches closure report's `88
  passed`).
- Increment-A suite: `76 passed in 69.11s` (matches `76 passed`).
- Guarded full repository suite (`-k "not
  test_29_subprocess_dry_run_never_optimizes"`): `225 passed, 1 deselected in
  91.18s` (matches exactly).
- The three frozen probes alone: `3 passed, 85 deselected in 1.12s`.
- Twelve reviewer-runnable proofs, all re-run independently with matching
  counts: PROOF-3 `88 passed`; PROOF-4 `79 passed, 9 deselected`; PROOF-5 `9
  passed, 79 deselected`; PROOF-6 `12 passed, 76 deselected`; PROOF-7 `6
  passed, 82 deselected`; PROOF-8 `19 passed, 69 deselected`; PROOF-9 `20
  passed, 68 deselected`; PROOF-10 `225 passed, 1 deselected`; PROOF-11
  `generated Phase-5 artifact files: NONE` / `Phase-5 output directories:
  NONE`; PROOF-12 numerical scalars per §7, all identical. PROOF-1 (HEAD,
  gitlink, nested status) and PROOF-2 (bundle/bread/theta hashes) reproduced
  per §7/§9 above.
- Phase-3 `attempts/` directory count: `70`, unchanged.
- `ruff check --select F,E9` on both files: `All checks passed!` (with an
  unrelated pyproject.toml deprecation warning about `ignore`/`select` moving
  under `[lint]`, not a finding against this change). `git diff --check`
  exits 0.
- No row-level score artifact or generated Phase-5 output directory exists
  anywhere in the working tree (independently re-scanned against the module's
  own closed `AGGREGATE_ARTIFACTS` set).
- No Increment-C code: `grep -riln "increment_c|IncrementC|increment-c|phase6|phase_6"`
  over both reviewed files returns no matches; a broader grep for
  `runner|transaction|manifest_writer|reproduction_lock|dry_run_runner`
  matches only one line, a docstring negation ("Not a runner, transaction,
  staging directory, manifest, console log, lock, or ...").
- Exact commit-ready state: `git status` shows exactly the seven expected
  untracked paths (five docs, the source module, the test module) plus, after
  this review is written, this file as an eighth — no other tracked or
  untracked change exists anywhere in the working tree.

## 11. Nonblocking technical debt

1. **Probe-provenance timing gap (§3).** No git-based evidence establishes
   that the three frozen probes were written and run before the
   implementation fix; only a self-consistent, independently-reproduced hash
   chain across five documents exists. Recorded here rather than resolved
   silently in the implementer's favor. Does not fall into a Section-2
   blocking class under the certification proportionality rule.
2. **`assert_aggregate_payload` is not self-sufficient (§6).** It does not
   reject raw bytes, memoryviews, or nested dict/mapping payloads on its own;
   protection at the three real writer entry points is provided by pairing it
   with `assert_member_contract`'s exact-shape enforcement. If Increment C (or
   any future caller) ever calls `assert_aggregate_payload` standalone without
   `assert_member_contract`, the "by construction" guarantee in its docstring
   would not hold. No current production path does this.
3. **`write_matrix`/`write_table` `metadata` kwarg remains a caller-controlled,
   unvalidated channel.** I confirmed live that it never reaches the persisted
   file bytes (only `ArtifactRecord.metadata`, in memory) — consistent with
   the closure report's own §7.2 item 3. If Increment C's manifest writer ever
   serializes `ArtifactRecord.as_dict()` (which includes `metadata`) into a
   persisted manifest, this channel would need the same scrutiny B-3 gave
   `extra=`; it is out of scope for Increment B.
4. **`_record`'s grade re-check is now dead-code defense-in-depth**, as the
   closure report states; each writer's `_require_grade` call fires first.
   Harmless, deliberately retained.

## 12. Whether Increment B may be committed

**Yes.** Every acceptance criterion in the proportionality decision §4 is
independently confirmed: the exact three frozen probes pass; the Increment-A
and Increment-B regression suites pass; numerical outputs, constants, schemas,
and source authorities reproduce unchanged; no row-level score artifact is
written; accepted bundles and the nested package are unchanged. The one
flagged limitation (§3, probe-timing provenance) is a documentation/process
gap inherent to this project's untracked-until-commit workflow, not a defect
in the shipped code, and does not meet any Section-2 blocking criterion in the
certification proportionality rule.

## 13. Whether Increment C may begin

**Yes, once Increment B is committed.** Per the proportionality decision §5-6
and the certification proportionality rule §7, a `PASS` here authorizes
Increment C, scoped to: actual production runner execution; fresh-process
reproduction; aggregate-only transaction; STOPPED truthfulness; no
`complete/`; no row-level persistence; accepted-artifact and revision binding.
Increment C must not reopen capability-security or import-surface
certification, and per §11 item 3 above, its manifest-writer design should
treat `ArtifactRecord.metadata` with the same scrutiny B-3 applied to
`extra=` if it plans to persist that field.

## 14. Immediate next action

1. Commit the exact reviewed state — `scripts/p2a/p2a_phase5_inference.py`,
   `tests/p2a/test_p2a_phase5_inference.py`, the four prior Increment-B
   documents, the proportionality decision/rule records, and this review —
   with both MNL and nested `dclaborsupply-monorepo` worktrees clean, exactly
   as verified in §9/§10.
2. Update the JMP-M05C mission ledger to record Increment B `PASS` and this
   review's file path/date.
3. Launch Increment C under the certification proportionality rule §6 /
   decision §6 scope (§13 above); carry `inference_grade` into its manifest
   from day one, and resolve nonblocking-debt item 3 (§11) — an explicit
   policy for whether/how `ArtifactRecord.metadata` may reach a persisted
   manifest — before any manifest writer serializes `ArtifactRecord.as_dict()`.
4. No further Increment-B review is required; the remediation and
   verification budgets defined by the proportionality decision are exhausted
   and satisfied.
