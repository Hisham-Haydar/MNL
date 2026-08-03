# FR P2a — JMP-M05C Streaming Inference — Increment B bounded refix report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Task:** the one bounded Increment-B refix authorized by M05C-AC-9, ruling R-38 (standing-rule-3 conversion)
**Authoritative fix source:** `FR_P2a_streaming_incrementB_review_v1.md` §§8–9 (locations from §§4–7)
**Mode:** implementation + tests only. No commit. No Increment C. No full-population run.
**Date:** 2026-08-02
**MNL HEAD (unchanged throughout):** `92e299de6313bad0b0421c0db3dd268fdbcfdb59`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Refix verdict

**READY FOR REVIEW B V2**

All six required fixes are implemented, each verified against the review's own
adversarial example. The Increment-B test set grew from 59 to **85 tests**, all
passing; the full repository suite is **222 passed, 1 deselected**.

Every one of the review's six residual defects now reproduces as a refusal:

| Review §8 defect | Before | After |
| --- | --- | --- |
| 1. T-5 omits the theta-byte hash | absent from `observed`/`bar` | present, and the gate cannot be called without it |
| 2. T-22 passes vacuously | `{}` → `passed=True`; `{"wrong_name":…}` → `passed=True` | both → `passed=False`, on the name check, before the threshold |
| 3. table uses CSV gradients | rendered `0.0001099259720618` at `beta_w_educH` | renders `0.00010992597206183063`; CSV column proven inert |
| 4. `inference_grade` not propagated | absent from regional/table objects | on both containers, their `.attrs`, and every serializer record |
| 5. serializer admits 5×35 block and NaN frame | both accepted | both refused (`IB-REFUSE`) |
| 6. PROOF-1/PROOF-11 expected output false | as printed | corrected in §10; both re-executed |

No design, package, architecture or constant changed. The 13-column schema and
every gate constant are untouched. The committed Increment-A files are
unmodified, and report v1 and review v1 are byte-identical.

---

## 2. Starting state

Verified before any file was touched.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `92e299de6313bad0b0421c0db3dd268fdbcfdb59` | identical | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean | PASS |

Untracked at task start — exactly the four declared paths, nothing else:

```text
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_review_v1.md
?? scripts/p2a/p2a_phase5_inference.py
?? tests/p2a/test_p2a_phase5_inference.py
```

### 2.1 Files modified, with hashes

| Path | SHA-256 (after refix) | Bytes | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/p2a_phase5_inference.py](scripts/p2a/p2a_phase5_inference.py) | `506e9dc5574563a2ba233a87f25c025e6a54f4c372a5835517b3e89d691447e9` | 71,658 | 1,486 |
| [tests/p2a/test_p2a_phase5_inference.py](tests/p2a/test_p2a_phase5_inference.py) | `f5a4bbf89b5a75fab8739b5955869a392db1342b4121c9bfd1ff0dae464c468b` | 52,403 | 1,107 |

Unchanged, byte-identical to task start (verified by byte comparison against a
task-start snapshot):

| Path | SHA-256 |
| --- | --- |
| `FR_P2a_streaming_incrementB_report_v1.md` | `3e9e69cf20321c889c2ec0284d3d3cc55e825c3a64615f8fc877ce46272c76b0` |
| `FR_P2a_streaming_incrementB_review_v1.md` | `822b0fbc91ab6f906bca2dd49931bbbd27f9ee4bfa25f87db4cbd95a06b3a3af` |

`git status` for the three committed Increment-A files
(`p2a_phase5_score_stream.py`, `test_p2a_phase5_score_stream.py`,
`conftest.py`) is empty. Both files remain LF-only, as at task start, so the
hunk maps below are meaningful. `git diff --check` exits 0.

---

## 3. Fix 1 — T-5 theta-byte authentication

**Review finding 1 / §4 nonconformity 1.** Design v4 §15 states T-5 as four
anchors — `hessian_free.npy`, the Phase-4 bundle, the Phase-3 bundle, and
`θ̂ bytes hash to c024b893…`. The shipped gate checked three and its
`observed`/`bar` keys carried no theta hash at all.

**What changed.** A new `accepted_theta_sha256(repo_root)` reads
`estimation_results.json → results.joint.theta` from the Phase-3 bundle and
hashes the C-contiguous float64 bytes, exactly as the accepted anchor was
produced. `gate_T5_bread_provenance` now takes `theta_sha256` as a **required
keyword-only** argument and reports all four arms individually. Keyword-only and
required matters: a caller cannot omit it and still obtain a pass, which is
precisely how three-of-four went unnoticed.

Recomputed here: `c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`
— identical to the design v4 §3.2 / §15 anchor.

**Tests.** `test_I8` (match, and both key sets carry the theta hash); `test_I9`
(one-byte mismatch — XOR `0x01` into the first byte of the accepted vector, write
it to a scratch tree, re-hash through the real loader, assert T-5 fails **and**
that the other three arms still pass, so only the theta arm fired); `test_I10`
(omitting the argument is a `TypeError`, not a silent pass).

**Hunks:** module 1, 2, 4, 5 (constants `PHASE3_RESULTS`, `ACCEPTED_THETA_SHA256`,
`PHASE3_BUNDLE_SHA256`, `PHASE4_BUNDLE_SHA256`; `accepted_theta_sha256`;
`gate_T5_bread_provenance`); module 47–50 (exports). Tests hunks 4, 17.

---

## 4. Fix 2 — T-22 validates the exact authenticated active set

**Review finding 2 / §4 nonconformity 2.** `gate_T22_numerical_kkt({}, 1e-4)`
returned `passed=True`, as did `{"wrong_name": …}`: `all(...)` over an empty or
irrelevant mapping is vacuously true. A gate satisfiable by supplying nothing is
not a gate.

**What changed.** The key set is validated against the two authenticated
active-bound names **before** the `100×` threshold is applied. `missing_names`
and `extra_names` are computed and reported; when the names are wrong the
threshold arm is never evaluated and `ratios` stays empty, so the failure is
unambiguously attributable. `ACTIVE_BOUND_NAMES = ("beta_l_age2_sm",
"beta_l_age2_sf")` is added to the module's frozen-constants block (design v4
§3.3 / §7.2) and `test_I11` asserts it equals the names derived from the
authenticated parameter map — the constant cannot drift from the map.

**Tests.** `test_I12` parametrises six non-exact mappings — empty, missing one,
extra name, wrong name only, two wrong names, one-right-one-wrong — and asserts
each fails on `active_names_ok`, with `ratios == {}`. `test_I13` asserts the
exact pair above the threshold passes. `test_I4` now uses the real names and
additionally asserts a threshold-only failure keeps `active_names_ok=True`,
separating the two failure modes. `test_K4` asserts the production mapping's key
set is exactly the authenticated pair before running the gate.

**Hunks:** module 21–26 (`gate_T22_numerical_kkt`), module 1 (`ACTIVE_BOUND_NAMES`).
Tests hunks 5–7, 18.

---

## 5. Fix 3 — the table builder consumes `AcceptedGradients`

**Review finding 3 / ruling R-37b.** `build_parameter_table` read
`grad_free_negll` from the parameter-map CSV for every free coordinate and
derived the two multipliers as `-g` from it. At `beta_w_educH` the table
rendered `0.0001099259720618` where the authoritative value is
`0.00010992597206183063`. The active values happened to round-trip exactly, but
as the review put it, source authority cannot depend on that accident.

**What changed.** `build_parameter_table(pmap, cov, param_map_frame, grads)` now
takes `AcceptedGradients` as a **required positional** argument and builds
`grad_by_name` from `grads.free` projected by the authenticated free-name
sequence. `grad_negll` for interior and active-bound rows, and both multipliers,
come from that mapping. Pinned rows keep structural `0.0` (design v4 §12.3).

The CSV column is now read in exactly one place and for exactly one purpose: an
explicit non-authoritative comparison recorded in
`ParameterTable.metadata["csv_vs_authoritative_gradient_max_abs_dev"]`, next to
`csv_gradient_column_used_for_arithmetic: False` and a note naming it a
reduced-precision rendering.

Verified after the fix: the table renders `0.00010992597206183063` at
`beta_w_educH`, and the multipliers are exactly `0.8445544161794221` and
`1.4682021491125388`.

**Tests.** `test_H8` asserts every free row's `grad_negll` equals the JSON value
by name, checks the review's exact `beta_w_educH` case, checks both multipliers
against design v4 §11.1, and confirms pinned rows stay `0.0`. `test_H9` is the
decisive one, inverted: it overwrites the **entire** CSV gradient column with
`12345.6789`, rebuilds, and asserts the resulting frame is identical via
`pd.testing.assert_frame_equal` — proving the column feeds no arithmetic — while
the recorded comparison diagnostic does change, which is the only effect it is
allowed to have. `test_H10` asserts omitting `grads` is a `TypeError`, so a
caller cannot fall back to the CSV by omission.

**Hunks:** module 13–20 (`build_parameter_table` signature, docstring, gradient
projection, both row branches, metadata block). Tests hunks 2, 3, 14, 19.

---

## 6. Fix 4 — `inference_grade` propagation

**Review finding 4 / ruling R-37a.** A first-64 covariance said
`subset-diagnostic` and W-1/W-4/W-5 echoed it, but `RegionalTests.diagnostics`,
the regional table and `ParameterTable` carried no grade, so subset Wald
statistics, p-values and precision rows could be serialized unlabelled.

**What changed** — everywhere as enclosing-object metadata, never as a column:

* `RegionalTests` gains `inference_grade` and `metadata` fields; the grade is
  also written into `diagnostics` and into `table.attrs`.
* `ParameterTable` gains `inference_grade`, `gradient_source` and `metadata`;
  the grade is also written into `frame.attrs`.
* `W-2` now echoes the grade, joining W-1, W-4 and W-5.
* All three serializers take a **required** `inference_grade` keyword and return
  a new `ArtifactRecord` (`member`, `path`, `kind`, `shape`, `sha256`,
  `inference_grade`, `metadata`) with a JSON-ready `as_dict()` — the
  manifest-facing wrapper Increment C will consume. An empty grade is refused
  with `IB-REFUSE`.
* `score_aggregate_summary.json` additionally carries the grade **inside** the
  payload, since it is the one member with a free-form schema.

**The 13-column schema is untouched.** `test_H11` asserts the column list is
exactly the design v4 §17.3 sequence, that its length is 13, and that
`inference_grade` is *not* among the columns while being present on the
container, on `.attrs` and in `metadata`.

**Tests.** `test_H11` (parameter table), `test_H12` (regional container,
diagnostics, `.attrs`, W-2 echo, and Wald schema unchanged), `test_J15`
(serializers require the grade; empty string refused; record is
JSON-serialisable), `test_K8` (all three real-path records report
`subset-diagnostic`).

**Hunks:** module 6–12 (`RegionalTests`, `run_regional_tests` metadata), 18–20
(`ParameterTable`), 26 (W-2), 33–46 (`ArtifactRecord`, `_record`, the three
writers). Tests hunks 1, 8, 10–13, 15, 16, 20.

---

## 7. Fix 5 — member-specific serializer contracts and DataFrame finiteness

**Review finding 5 / §6 adversarial failures.** Two gaps:
`assert_aggregate_payload(np.zeros((5, 35)), "temporary_interior_scores")` was
accepted — a prohibited temporary row-level interior-score batch — because the
score-block rule covered only the 37-column case. And a numeric DataFrame
containing `NaN` was accepted, because only the ndarray branch checked
finiteness. As the review noted, the closed filename set did not repair the shape
gap, since `write_table` accepted any frame under any allowed member.

**What changed:**

1. **The score-block rule now covers both widths.** Any 2-D payload whose column
   count is 37 or 35 and whose row count does not equal that width is refused, in
   both the ndarray and the DataFrame branch.
2. **The DataFrame branch checks numeric finiteness**, over
   `select_dtypes(include=[np.number])` so string columns are not coerced.
3. **`_MEMBER_CONTRACTS`** declares, for each of the 16 members, its `kind`
   (`matrix` / `table` / `json`) and its exact expected shape — square
   `(37,37)`, `(35,35)` or `(10,10)` for matrices; exact row counts for tables;
   and the exact 13-column sequence for `phase5_parameter_table.csv`. The new
   `assert_member_contract` enforces it, so a payload can only be filed under a
   member whose contract it actually meets. `write_matrix` also rejects a
   name-list whose length disagrees with the matrix.

Verified after the fix: both of the review's adversarial cases now raise
`IB-REFUSE`, and the genuine 35×35 aggregate is still accepted.

**Tests.** `test_J10` (the review's 5×35 case, standalone *and* attempted under
the legitimate `meat_interior35.npy` member, with the target directory asserted
empty afterwards, plus the genuine 35×35 still accepted); `test_J11` (NaN, +Inf,
−Inf frames refused; a clean mixed string/float frame still accepted);
`test_J12` (five member-contract mismatches — wrong shape, non-square, wrong
kind, non-DataFrame); `test_J13` (the parameter-table member requires the exact
column sequence and exactly 47 rows); `test_J14` (every declared member has a
contract, so the two sets cannot drift apart).

**Hunks:** module 27–32 (`_MEMBER_CONTRACTS`, `assert_aggregate_payload` both
branches, `assert_member_contract`), 33–46 (writers wired to it). Tests hunk 14.

---

## 8. Fix 6 — corrected PROOFS

**Review finding 6 / §3.** Two proofs did not reproduce their printed expected
output:

* **PROOF-1** printed an expected `git status` block that omitted the report's
  own untracked path, so the block could never match.
* **PROOF-11**'s predicate matched any file whose name contains `score`,
  `covariance` or starts with `phase5_`, which caught three **committed design
  inputs** — `phase5_full_score_surface_inventory_v1.json`,
  `phase5_parameter_map_v1.csv`, `phase5_source_inventory_v1.json`. Its expected
  `NONE` was therefore false, and the predicate could not establish the
  no-artifact conclusion it claimed.

**What changed.** §10 below carries the corrected packet. PROOF-1's expected
block now lists the full untracked set including this refix report. PROOF-11 is
narrowed to **generated Phase-5 output** only: files whose basename is in the
module's own closed `AGGREGATE_ARTIFACTS` set, plus any `phase5*` directory under
`outputs/`. That is checkable, is tied to the artifact set the module can
actually write, and returns a true `NONE`.

Report v1 is left byte-identical as required, so **§10 supersedes report v1 §6**
for review purposes. Every command was re-executed verbatim before this report
was written.

---

## 9. Test results

All runs used `.\.venv\Scripts\python.exe` from `C:\Users\hisham\Repo\MNL`.

```text
Increment-B set, run 1                     85 passed in 5.60s
Increment-B set, run 2                     85 passed in 5.67s
  fast families (-m "not production")      76 passed,  9 deselected in 1.34s
  production family (-m production)         9 passed, 76 deselected in 5.34s
full repository, test-29 deselected       222 passed, 1 deselected in 89.79s
attempts/ count after every run                                          70
ruff check --select F,E9 (both files)                    All checks passed!
git diff --check                                                     exit 0
```

Test growth 59 → 85 (+26), all attributable to the six fixes:

| Fix | New tests | Count |
| --- | --- | --- |
| 1 | `test_I8`, `test_I9`, `test_I10` | 3 |
| 2 | `test_I11`, `test_I12` (×6 params), `test_I13` | 8 |
| 3 | `test_H8`, `test_H9`, `test_H10` | 3 |
| 4 | `test_H11`, `test_H12`, `test_J15` | 3 |
| 5 | `test_J10`, `test_J11`, `test_J12` (×5 params), `test_J13`, `test_J14` | 9 |
| 6 | — (report-only) | 0 |

Repository total 222 = 137 pre-existing (62 legacy + 75 Increment-A) + 85
Increment-B, with test 29 deselected by the Increment-A conftest guard.

### 9.1 Each review defect, re-run as a live check

```text
gate_T22_numerical_kkt({}, 1e-4).passed            = False
gate_T22_numerical_kkt({'wrong_name': 1.0}).passed = False
T-5 observed/bar carry theta_sha256                = True / True
table grad_negll at beta_w_educH                   = 0.00010992597206183063
  (authoritative match = True; CSV value = 0.0001099259720618)
RegionalTests.inference_grade / .diagnostics / .attrs = subset-diagnostic ×3
ParameterTable.inference_grade / .attrs               = subset-diagnostic ×2
13-column schema intact                            = True
assert_aggregate_payload(np.zeros((5,35)), ...)    = REFUSED [IB-REFUSE]
assert_aggregate_payload(DataFrame with NaN, ...)  = REFUSED [IB-REFUSE]
```

---

## 10. Updated PROOFS (supersedes report v1 §6)

**Every command below was executed exactly as printed, in PowerShell, from
`C:\Users\hisham\Repo\MNL`.** All are read-only, create no reviewer-owned file,
require no source edit, and use the exact virtual-environment interpreter.
`-p no:cacheprovider` prevents a `.pytest_cache` write. Full-suite commands carry
the test-29 deselection, which the Increment-A conftest guard also enforces.

Report v1 §6 is superseded in full by this section. PROOF-2 through PROOF-10 and
PROOF-12 are unchanged in substance; PROOF-1 and PROOF-11 are corrected; the
test counts are regenerated after the 26 new tests.

### PROOF-1 — starting state and worktrees *(corrected)*

```powershell
cd C:\Users\hisham\Repo\MNL
git rev-parse HEAD
git status --porcelain --untracked-files=all
git ls-tree HEAD dclaborsupply-monorepo
git -C dclaborsupply-monorepo rev-parse HEAD
git -C dclaborsupply-monorepo status --porcelain --untracked-files=all
```

Expected — **all five untracked paths, including this refix report**:

```text
92e299de6313bad0b0421c0db3dd268fdbcfdb59
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_refix_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_report_v1.md
?? docs/France_case/P2a/FR_P2a_streaming_incrementB_review_v1.md
?? scripts/p2a/p2a_phase5_inference.py
?? tests/p2a/test_p2a_phase5_inference.py
160000 commit 27756a06ea189339aa82915ed2124628afed20eb	dclaborsupply-monorepo
27756a06ea189339aa82915ed2124628afed20eb
(no output - nested worktree clean)
```

### PROOF-2 — accepted bundles, bread and theta

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import hashlib,os,sys;sys.path.insert(0,'scripts/p2a');import p2a_phase5_inference as ib;s=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();b=lambda d,m:hashlib.sha256(('\n'.join(f'{n}:{s(os.path.join(d,n))}' for n in sorted(os.listdir(d)) if n!=m)).encode('utf-8')).hexdigest();print('phase3',b('outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete','phase3_manifest.json'));print('phase4',b('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete','phase4_manifest.json'));print('bread ',s('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/hessian_free.npy'));print('theta ',ib.accepted_theta_sha256())"
```

Observed:

```text
phase3 2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b
phase4 5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3
bread  e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061
theta  c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d
```

### PROOF-3 — the complete Increment-B test set

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider
```

Observed: `85 passed in 5.60s`

### PROOF-4 — fast families only

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -m "not production"
```

Observed: `76 passed, 9 deselected in 1.34s`

### PROOF-5 — production family (real reducer, real bread)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -m production
```

Observed: `9 passed, 76 deselected in 5.34s`

### PROOF-6 — Fix 1 and Fix 2: T-5 and T-22 gate integrity

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_I4 or test_I8 or test_I9 or test_I10 or test_I11 or test_I12 or test_I13"
```

Observed: `12 passed, 73 deselected in 0.53s`

### PROOF-7 — Fix 3 and Fix 4: authoritative gradients and grade propagation

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_H8 or test_H9 or test_H10 or test_H11 or test_H12 or test_J15"
```

Observed: `6 passed, 79 deselected in 1.13s`

### PROOF-8 — Fix 5: serializer contracts and refusals

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_J1 or test_J2 or test_J3 or test_J4 or test_J5 or test_J6 or test_J7 or test_J8 or test_J9 or test_J10 or test_J11 or test_J12 or test_J13 or test_J14 or test_J15"
```

Observed: `19 passed, 66 deselected in 1.22s`

### PROOF-9 — bread rejections and the analytic fixtures

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_F1 or test_F2 or test_F3 or test_F4 or test_F5 or test_F6 or test_F7 or test_F8 or test_F9 or test_G1 or test_G2 or test_G3 or test_G4 or test_G5 or test_G6 or test_G7 or test_G8"
```

Observed: `20 passed, 65 deselected in 1.19s`

### PROOF-10 — the safe full repository suite

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "not test_29_subprocess_dry_run_never_optimizes"
```

Observed: `222 passed, 1 deselected in 89.79s (0:01:29)`

### PROOF-11 — no GENERATED Phase-5 output exists in the repository *(corrected)*

The predicate is now tied to the module's own closed artifact set, so it tests
what it claims and its `NONE` is true.

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import sys;sys.path.insert(0,'scripts/p2a');from pathlib import Path;import p2a_phase5_inference as ib;members=set(ib.AGGREGATE_ARTIFACTS);skip={'.git','.venv','__pycache__'};hits=sorted(str(p) for p in Path('.').rglob('*') if p.is_file() and skip.isdisjoint(set(p.parts)) and p.name in members);dirs=sorted(str(p) for p in Path('outputs').rglob('phase5*') if p.is_dir());print('generated Phase-5 artifact files:', hits if hits else 'NONE');print('Phase-5 output directories     :', dirs if dirs else 'NONE')"
```

Observed:

```text
generated Phase-5 artifact files: NONE
Phase-5 output directories     : NONE
```

The three committed files the old predicate caught —
`phase5_full_score_surface_inventory_v1.json`, `phase5_parameter_map_v1.csv`,
`phase5_source_inventory_v1.json` — are committed **design inputs** under
`docs/France_case/P2a/`, not generated outputs, and are correctly outside this
scan.

### PROOF-12 — the numerical results, plus every review defect re-checked

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import sys;sys.path.insert(0,'scripts/p2a');import numpy as np,pandas as pd,p2a_phase5_score_stream as ss,p2a_phase5_inference as ib;pm=ss.load_parameter_map();mp=pd.read_csv('docs/France_case/P2a/phase5_parameter_map_v1.csv');br=ib.load_bread(pm);gr=ib.load_accepted_gradients(pm);r=ss.run_score_stream(ss.build_production_binding(household_limit=64),batch_size=64);t7=ib.gate_T7_meat_validity(r.meat_interior35);cv=ib.build_covariances(br,r.meat_interior35,meat_n_households=r.n_households);pt=ib.build_parameter_table(pm,cv,mp,gr);rg=ib.run_regional_tests(pm,cv,np.zeros(35));print('bread asym      ',repr(br.diagnostics['max_abs_asymmetry_raw']),'bar',repr(ib.HESSIAN_SYMMETRY_THRESHOLD));print('bread min_eig   ',repr(br.diagnostics['min_eig_Hs']),'anchor',repr(ib.PHASE4_MIN_EIG));print('meat min_eig    ',repr(t7.observed['min_eig']),'floor',repr(t7.bar['psd_floor']));print('correction c    ',repr(cv.correction_c));print('solve vs pinv   ',repr(cv.diagnostics['solve_vs_pinv_max_abs_dev']),'bar',repr(ib.SOLVE_VS_PINV_ATOL));print('T-22 empty      ',ib.gate_T22_numerical_kkt({},1e-4).passed);print('T-22 wrong name ',ib.gate_T22_numerical_kkt({'wrong_name':1.0},1e-4).passed);print('T-22 exact pair ',ib.gate_T22_numerical_kkt(gr.active_multipliers,gr.interior_max_abs).passed);print('grad beta_w_educH',repr(float(pt.frame.set_index('name').loc['beta_w_educH','grad_negll'])));print('grade table/reg  ',pt.inference_grade,'/',rg.inference_grade);print('13 columns intact',list(pt.frame.columns)==list(ib.PARAMETER_TABLE_COLUMNS))"
```

Observed:

```text
bread asym       1.8189894035458565e-12 bar 0.00023588019878151842
bread min_eig    0.10373269638807983 anchor 0.1037326963880782
meat min_eig     2.0597024553162405e-13 floor -1.42580003805006e-08
correction c     1.0230263157894737
solve vs pinv    1.9602097722781764e-12 bar 1e-08
T-22 empty       False
T-22 wrong name  False
T-22 exact pair  True
grad beta_w_educH 0.00010992597206183063
grade table/reg   subset-diagnostic / subset-diagnostic
13 columns intact True
```

Every numerical value the review verified in its §5 is unchanged: the fixes
touched authentication, validation, source authority, metadata and serializer
contracts, not the covariance arithmetic.

---

## 11. Residual warnings

1. **The first-64 path remains `subset-diagnostic`.** No full-sample inferential
   result exists, by design; the certified covariance, standard errors and the
   H0-A verdict are produced for the first time in the Increment-C dry run. The
   grade now travels on every derived container and every serializer record, so
   this can no longer be lost downstream — but it must be carried into the
   Increment-C manifest, per R-37a.
2. **W-1 still flags at subset scale** (`min_ratio 0.061`), for the arithmetic
   reason given in report v1 §5.4. Warning-tier, non-gating, unchanged.
3. **The serializer contract set is fixed at 16 members.** Adding an artifact in
   Increment C requires adding both its name and its contract; `test_J14`
   enforces that the two sets stay in step, and will fail loudly if only one is
   updated.
4. **Foreign-message suppression** in Increment A and the reduced-precision CSV
   gradient column remain as previously recorded. The CSV column is now provably
   inert in this layer (`test_H9`); Increment C must likewise read only
   `phase4_diagnostics.json`.
5. **`ArtifactRecord` is a new return type.** Callers now receive a record rather
   than a `Path`; `record.path` is the file. This is the manifest-facing surface
   Increment C consumes, and is the mechanism by which R-37a's "serializer/
   manifest metadata" requirement is met without touching any artifact schema.
6. **T-13, T-23/T-23S, T-12/T-12S remain Increment C.** Nothing in this refix
   moved that boundary; no runner, transaction, manifest or reproduction code
   exists in this layer.

---

## 12. Immediate next action

1. **Launch Review B v2** — fresh independent Codex session, read-only, at MNL
   `92e299de6313bad0b0421c0db3dd268fdbcfdb59`, executing §10 PROOF-1 … PROOF-12
   verbatim. Scope: the six fixes, the original Increment-B contract, and
   exact-state integrity; no scope expansion. Per M05C-AC-9 / R-38 this is the
   only refix for this increment — **a second REJECT returns the mission to the
   deputy programme director.**
2. **Give the reviewer this refix report as the PROOFS packet**, noting that §10
   supersedes report v1 §6 while report v1 itself stays byte-identical.
3. **On `APPROVE`**: commit the reviewed Increment-B state with both worktrees
   clean, update the JMP-M05C ledger, then authorize **Increment C** — dry-run
   runner, aggregate-only attempt transaction, T-12S reproduction over the fixed
   `(encoding, batch size, AD mode)` tuple, T-23S, manifest and provenance
   carrying `inference_grade` and `jax_enable_x64`, STOPPED behaviour, no
   `complete/`.
4. **Carry into Increment C** the §11 items, in particular that the first
   full-sample covariance and the H0-A verdict are produced for the first time in
   the dry run and must be audited there, never inferred from the first-64 slice.

**FINAL VERDICT: READY FOR REVIEW B V2**
