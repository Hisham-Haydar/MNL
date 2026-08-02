# FR P2a — JMP-M05C Streaming Inference — Increment A implementation report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Increment:** A — Streaming score reducer (charter §4-A)
**Mode:** implementation + tests only. No commit beyond the pre-step. No full-population run.
**Date:** 2026-08-02
**Implementation base (MNL HEAD):** `b5169293b647dda3e07070c678f8d46d33b1bf89`
**Nested `dclaborsupply` HEAD = MNL gitlink:** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Increment verdict

**READY FOR REVIEW A**

Every Increment-A deliverable enumerated in the mission prompt (items 1–8) and
charter §4-A is implemented, exercised on the real production path, and proved by
a reviewer-runnable command with an accompanying failure demonstration. 42 tests
pass; the full repository suite (104 tests) passes, the 62 pre-existing ones unchanged.

Two matters the reviewer must rule on rather than take as settled — neither is a
defect in the delivered code, both are disclosed rather than absorbed:

1. **The addendum §2 digest fixes the composition but not the integer encoding.**
   This implementation fixes it (`int64` little-endian, §4 below) and publishes
   the constant on the result object. The reviewer should ratify the byte
   contract before Increment C freezes any digest into an artifact.
2. **The digest is a function of (subset, AD mode, batch size)**, not of the
   subset alone. Measured: identical across most chunkings but *not* all
   (batch size 3 differs from 8/24 by `8.88e-16` per entry, i.e. 1 ULP at this
   magnitude, ~5 orders inside the T-11 bar). Addendum §4 already pins "actual
   batch size" in the reproduction comparison, so this is compatible with the
   design as written — but it means **T-12S must compare at a fixed batch size**,
   and no batch-size-independent digest claim is made anywhere in this increment.

One defect was found and fixed during verification and is written up in full in
§6.0: `jax_enable_x64` is set lazily by the package's first builder call, so the
test's reference helper silently ran in float32 whenever it executed first. The
binding now activates float64 eagerly and refuses to proceed otherwise, and every
production test was re-verified in isolation.

Two incidental, unrelated worktree entries appeared during regression testing and
are disclosed in §2.6 and §8. They were **not** created by any Increment-A code
and I have not deleted them.

---

## 2. Starting state and pre-step commit

### 2.1 Verified starting state

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD before pre-step | `ffd060f7a0f4535150498aae6361a3df35cf8b53` | `ffd060f7a0f4535150498aae6361a3df35cf8b53` | PASS |
| MNL worktree before pre-step | exactly one untracked file | `?? docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md` and nothing else | PASS |
| Nested `dclaborsupply` HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | `27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| MNL gitlink for `dclaborsupply-monorepo` | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean (`--untracked-files=all` empty) | PASS |

### 2.2 Pre-step commit

Staged exactly one path; single-line message exactly as instructed.

```text
git -C c:/Users/hisham/Repo/MNL add docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
git -C c:/Users/hisham/Repo/MNL commit -m "docs(p2a): add M05C streaming design addendum"
```

```text
[main b516929] docs(p2a): add M05C streaming design addendum
 1 file changed, 195 insertions(+)
 create mode 100644 docs/France_case/P2a/JMP_M05C_streaming_inference_design_addendum_v1.md
```

**Mission implementation base: `b5169293b647dda3e07070c678f8d46d33b1bf89`.**
`git show --stat` confirms the commit touches that one file and nothing else.

### 2.3 Accepted-bundle rehash (manifest-excluded hash-of-hashes, separate per phase)

Algorithm reused verbatim from Phase 4 [design v4 §17.2]:
`sha256(utf8("\n".join(f"{n}:{sha256(n)}" for n in sorted(members) if n != manifest)))`.

| Bundle | Expected | Recomputed | Verdict |
| --- | --- | --- | --- |
| Phase-3 (`phase3_estimation_v1/complete`, 4 hashed members) | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | PASS |
| Phase-4 (`phase4_curvature_v1/complete`, 7 hashed members) | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | PASS |
| `hessian_free.npy` (authoritative bread, **not consumed in Increment A**) | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | PASS |

No bundle member was modified. The bread is *not* loaded by Increment A — bread
authentication and use belong to Increment B.

### 2.4 Provenance discipline

No archived or rejected JMP-M05B Phase-5 implementation source was read or
copied. The only stale trace of it in the tree is compiled bytecode
(`tests/p2a/__pycache__/test_p2a_regionlive_phase5_inference.*.pyc`) whose source
is absent; it was not read, is not imported, and is not collected by pytest.
Module and test names delivered here are distinct from it.

### 2.5 Environment (design v4 §3.4 requires this be recorded going forward)

| Item | Value |
| --- | --- |
| Python | 3.12.2 (CPython, MSC v.1937, 64-bit) |
| Platform | `Windows-2022Server-10.0.20348-SP0` |
| jax / jaxlib | 0.10.1 / 0.10.1 |
| numpy / pandas / scipy | 2.3.5 / 2.3.3 / 1.16.2 |
| pytest | 8.4.2 |
| `jax_enable_x64` at score time | `True` (set by `engine_jax._load_jax()`; enforced, see §4 item 9) |

### 2.6 Incidental worktree entries — disclosed, not created by this increment

Running the **whole** repository suite for regression cover executed the
pre-existing accepted test
`tests/p2a/test_p2a_regionlive_phase3_safety.py::test_29_subprocess_dry_run_never_optimizes`,
which by design invokes the Phase-3 runner as a subprocess against the canonical
output root and therefore appends one dry-run attempt directory to the
never-deleted `attempts/` history. Two full-suite runs were performed (one before
and one after the §4 item 9 float64 guard was added), so there are two such
entries:

```text
?? outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/
   20260802T153430Z_270236_480b4748926746fa994fd3f616a36d94_dryrun_PHASE_3_DRY_RUN_COMPLETE/
     phase3_console.log
     phase3_manifest.json
?? outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/
   20260802T155349Z_500640_ed2da8d233294b158fbe93d003e04b75_dryrun_PHASE_3_DRY_RUN_COMPLETE/
     phase3_console.log
     phase3_manifest.json
```

Both are `PHASE_3_DRY_RUN_COMPLETE` attempts with `optimizer_called: false`; they
are entries 71 and 72 of an `attempts/` history whose earlier 70 entries are
committed. Neither touches a `complete/` bundle (proved by that test's own
byte-identity assertion on the accepted Phase-3 bundle).

**I have not deleted them.** The repository's own Phase-3 safety suite documents a
never-delete evidence policy for `attempts/`, and removing an execution record is
not reversible. They are also outside the Increment-A commit scope, so they are
neither staged nor committed. **Manager decision requested:** commit them as
routine test evidence, or authorise their removal. Proof that Increment-A code did
**not** create them is in §7, PROOF-7.

---

## 3. Deliverable inventory with SHA-256

All three files are **new and untracked**; nothing existing was modified.

| Path | SHA-256 | Bytes | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/p2a_phase5_score_stream.py](scripts/p2a/p2a_phase5_score_stream.py) | `6083eada192e1ba92fa6147bdac0463efcf49f66880192b55e43035c87c032bd` | 34,140 | 768 |
| [tests/p2a/test_p2a_phase5_score_stream.py](tests/p2a/test_p2a_phase5_score_stream.py) | `5dc910243935d9a373837258f4244ed17e486c8dd80f471fb269b4afea5e3ef0` | 33,089 | 712 |
| [tests/p2a/conftest.py](tests/p2a/conftest.py) | `2292222620e7206a48483039cca54b68e127f66210a2cba5e07f1851534a73d3` | 537 | 13 |

`conftest.py` exists solely to register the `production` pytest marker locally,
so that no existing tracked file (in particular `pyproject.toml`) had to be
edited and no unknown-marker warning is emitted.

Recompute with:

```text
python -c "import hashlib;[print(hashlib.sha256(open(p,'rb').read()).hexdigest(),p) for p in ['scripts/p2a/p2a_phase5_score_stream.py','tests/p2a/test_p2a_phase5_score_stream.py','tests/p2a/conftest.py']]"
```

### 3.1 Public surface of the module

| Object | Role |
| --- | --- |
| `load_parameter_map` → `ParameterMap` | authenticated 47/37/35 index spaces, by name; T-17 fingerprints |
| `build_canonical_order` → `CanonicalOrder` | `idhh`-ascending order + `batches(batch_size)` iterator |
| `build_production_binding` → `LikelihoodBinding` | binds spec, stem, accepted θ̂, real loader; `household_limit` is the only subsetting knob |
| `compute_batch_scores` | one bounded, transient `(n_b, 37)` float64 block on the accepted route |
| `ScoreStreamReducer` | running `g₃₇`, `M₃₇`, `M₃₅`, digest; `update()` retains nothing |
| `run_score_stream` → `ScoreStreamResult` | the stream; aggregate-only return |
| `ScoreStreamError` | contract violation; messages carry shapes/counts/positions only |

---

## 4. Design conformance map

| # | Prompt / charter requirement | Where implemented | Governing section |
| --- | --- | --- | --- |
| 1 | Canonical household iterator in `idhh`-ascending order, bound to the authenticated parameter map and loader group order | `build_canonical_order`, `CanonicalOrder.batches`; order taken from `PrecomputedDataSingles.group_ids` of the **real** loader for both genders, never from a re-read of the frame | design v4 §6.3 order (b); §6.1; T-3 |
| 2 | Bounded batch score computation via `jax.jacfwd` on the accepted per-group likelihood route (import-only; scores transient) | `_gender_score_block` / `compute_batch_scores`: slices the production frame to whole households → `load_singles` → `build_jax_singles_ll(..., per_group=True)` → `jax.jacfwd` of `base_full.at[free_idx].set(x_free)` | design v4 §5.1, §5.2, §5.4 baseline; audit §10 |
| 3 | Streaming aggregate score vector `(37,)` with the running sum | `ScoreStreamReducer._g37`, `+= block.sum(axis=0)` per batch | addendum §2 (`g₃₇`) |
| 4 | Streaming meat: 37×37 and the 35×35 interior selection, per batch, never materialising `(G × 37)` | `_m37 += block.T @ block`; `_m35 += interior.T @ interior` with `interior = block[:, I]`, `I` from the by-name interior selector | addendum §2 (`M₃₇`, `M₃₅`); design v4 §9.1, §7.2 |
| 5 | Global canonical score-stream digest per addendum §2, computed inside the stream | `ScoreStreamReducer.update` folds each row into one running `hashlib.sha256` **as the batch is consumed**; never over a stored matrix | addendum §2 |
| 6 | No row-level persistence anywhere (disk, logs, exceptions, test artifacts) | module has no write path at all (static proof PROOF-4); `ScoreStreamError` messages carry only shapes/counts/names/positions; result object carries only `(37,)`, `(37,37)`, `(35,35)` | addendum §6, T-23S |
| 7 | REAL production-path integration test on a bounded subset; only the subset size patched; cross-checked against a direct `jacrev` | test family E, `SUBSET_HOUSEHOLDS = 24`; `_direct_jacrev_reference` is an independent single-call-per-gender reference using the same accepted loader and likelihood but **no** reducer, iterator or batching | charter §5 |
| 8 | Deterministic synthetic tests: exact aggregates, both meat blocks, exact digest; batch-size invariance; failure tests | test family C (C1–C9) on an integer-exact fixture; C4 asserts **bitwise** invariance across six chunkings; C5–C9 are the failure tests | prompt item 8 |
| 9 | *(added guard)* float64 contract enforced, not assumed | `build_production_binding` triggers the accepted `engine_jax._load_jax()` float64 initialiser **eagerly** and raises unless `jax_enable_x64` is then active; `_gender_score_block` additionally rejects a non-`float64` **raw** device dtype before `np.asarray` could upcast it | design v4 §3.3, audit §17; T-15 precursor |

### 4.1 Digest byte contract, fixed here

Addendum §2 specifies the composition — `idhh canonical encoding || 37 float64
little-endian score values` — and leaves the integer encoding open. This
implementation fixes and publishes it:

```text
per household:  struct.pack("<q", int(idhh))      #   8 bytes, int64 little-endian
                s_g.astype("<f8").tobytes()       # 296 bytes, 37 x float64 little-endian
                                                  # 304 bytes/household, canonical order
```

Published on `ScoreStreamResult` as `idhh_encoding="int64_le"`, `dtype="float64"`,
`byte_order="little"`, `bytes_per_household=304`, so the addendum §3
`score_aggregate_summary.json` "dtype and byte-order contract" field is
satisfiable in Increment C without re-deriving anything. Non-integral identifiers
are rejected rather than silently truncated. `test_D7` proves the constant is
load-bearing: big-endian `idhh`, big-endian scores, `int32` `idhh`, or dropping
`idhh` each produce a different digest.

### 4.2 Deliberate non-scope

No runner, transaction, staging directory, manifest, allowlist, or STOPPED
handling (Increment C). No bread load, covariance, standard error, Wald object,
correction scalar, or `phase5_diagnostics.json` (Increment B). No restricted
store. No `complete/`. No full-population run. No package source touched — the
nested repository is byte-clean at the same gitlink it started at. No design,
spec, θ, pin, or tolerance constant changed.

---

## 5. Proofs (reviewer-runnable)

Run from the MNL repository root, `c:/Users/hisham/Repo/MNL`. Each proof gives the
exact command, the expected output, and its failure demonstration.

### PROOF-1 — starting state, pre-step commit, gitlink

```text
git -C c:/Users/hisham/Repo/MNL rev-parse HEAD
git -C c:/Users/hisham/Repo/MNL show --stat --oneline HEAD
git -C c:/Users/hisham/Repo/MNL ls-tree HEAD dclaborsupply-monorepo
git -C c:/Users/hisham/Repo/MNL/dclaborsupply-monorepo rev-parse HEAD
git -C c:/Users/hisham/Repo/MNL/dclaborsupply-monorepo status --porcelain --untracked-files=all
```

Expected:

```text
b5169293b647dda3e07070c678f8d46d33b1bf89
b516929 docs(p2a): add M05C streaming design addendum
 ..._M05C_streaming_inference_design_addendum_v1.md | 195 +++++++++++++++++++++
 1 file changed, 195 insertions(+)
160000 commit 27756a06ea189339aa82915ed2124628afed20eb	dclaborsupply-monorepo
27756a06ea189339aa82915ed2124628afed20eb
(no output — nested worktree clean)
```

**Failure demonstration.** `git -C … show --stat HEAD~1` shows the pre-step
commit's parent is `ffd060f…`, so any additional file in the commit would appear
in the `--stat` block above; the block lists exactly one path.

### PROOF-2 — accepted bundles rehash (manifest-excluded, separate per phase)

```text
python -c "import hashlib,os;s=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();b=lambda d,m:hashlib.sha256(('\n'.join(f'{n}:{s(os.path.join(d,n))}' for n in sorted(os.listdir(d)) if n!=m)).encode('utf-8')).hexdigest();print('phase3',b('outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete','phase3_manifest.json'));print('phase4',b('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete','phase4_manifest.json'))"
```

Expected:

```text
phase3 2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b
phase4 5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3
```

**Failure demonstration.** Including the manifest in the member set (drop the
`if n!=m` clause) produces a different hash for both bundles, which is why the
manifest-exclusion is stated explicitly rather than assumed.

### PROOF-3 — deterministic synthetic reducer (exact aggregates, exact digest, chunk invariance, failures)

```text
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -m "not production" -v
```

Expected: `29 passed, 12 deselected` in well under a second, including

```text
test_C1_exact_aggregate_vector PASSED
test_C2_exact_meat_blocks PASSED
test_C3_exact_digest_matches_the_documented_convention PASSED
test_C4_batch_size_invariance_is_bitwise PASSED
test_C5_failure_wrong_order PASSED
test_C6_failure_permuted_identifiers_within_a_batch PASSED
test_C7_failure_corrupted_batch[rows-score shape] PASSED
test_C7_failure_corrupted_batch[cols-score shape] PASSED
test_C7_failure_corrupted_batch[dtype-score dtype] PASSED
test_C7_failure_corrupted_batch[type-must be a numpy array] PASSED
test_C8_failure_non_finite_scores[nan] PASSED
test_C8_failure_non_finite_scores[inf] PASSED
test_C8_failure_non_finite_scores[-inf] PASSED
test_C9_failure_incomplete_stream PASSED
```

The fixture is `s[i,j] = (i+1)·c_j` with `c_j = (j mod 5) − 2`, `i = 0…5` — every
entry a small integer, hence exact in float64 — so the expected values are
analytic: `Σ_i s_i = 21·c`, `(SᵀS)_{jk} = 91·c_j c_k`, `(S_IᵀS_I)_{jk} = 91·c_I[j]c_I[k]`,
and the digest is the pinned constant
`a077a2ab7b5e8141247dd6bdd3591669b795511ad6881409988353ed3327175c`.

**Failure demonstration.** `test_C5`–`test_C9` *are* the failure demonstrations:
each drives the reducer with a wrong-order, permuted, mis-shaped, mis-typed,
non-finite or incomplete stream and asserts `ScoreStreamError`. `test_D7`
separately proves the digest constant is not vacuous. To see a red bar directly,
edit `SYNTH_DIGEST` by one hex character and re-run — `test_C3` fails.

### PROOF-4 — no row-level persistence (static + behavioural + failure path)

```text
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -k "D1 or D2 or D3 or D4 or D5 or D6 or D7 or D8" -v
```

Expected: `8 passed`.

* `D1` parses the module's AST and asserts it contains **no** `save/savez/savetxt/
  tofile/to_csv/to_parquet/to_pickle/to_json/write/writelines/write_text/
  write_bytes/dump/print` call, **no** `open()` whose literal mode is not
  read-mode, and **no** import of `pickle/shelve/csv/sqlite3/logging/shutil/tempfile`.
* `D3` asserts the result object's only arrays are `(37,)`, `(37,37)`, `(35,35)`.
* `D4` takes a `weakref` to the batch array, calls `update()`, drops the caller's
  reference, forces `gc.collect()`, and asserts the weakref is dead.
* `D5` runs a full stream in a temporary cwd and asserts the temp tree is empty
  and the accepted `region_live_v1` tree is byte-for-byte unchanged.
* `D6` triggers the non-finite failure and asserts no score value appears in the
  exception message and no temporary batch is left on disk.
* `D8` asserts nothing reaches stdout/stderr.

**Failure demonstration.** `test_D2` writes a probe module containing `np.save`
and `open(p,'w').write(...)` and asserts the D1 scanner detects all three — so a
green `D1` means "no write path", not "scanner blind".

### PROOF-5 — REAL production-path integration on a bounded subset

```text
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -m production -v
```

Expected: `12 passed, 29 deselected in ~58s`, including

```text
test_E1_binding_uses_the_accepted_authenticated_sources PASSED
test_E2_streamed_aggregates_match_a_direct_jacrev_reference PASSED
test_E3_digest_reproduces_the_direct_reference_bitwise PASSED
test_E3b_digest_is_deterministic_at_a_fixed_batch_size PASSED
test_E4_t11_chunk_route_invariance PASSED
test_E5_t16_forward_reverse_mode_agreement PASSED
test_E6_aggregates_are_chunking_stable_within_tolerance PASSED
test_E7_production_stream_writes_nothing PASSED
test_E8_subset_size_is_the_only_patched_quantity PASSED
test_E9_household_limit_is_validated PASSED
test_E12_float64_is_active_and_enforced_on_the_route PASSED
test_E10_corrupted_production_slice_is_detected PASSED
```

What is real and what is patched: the parameter map is the committed
`phase5_parameter_map_v1.csv` cross-authenticated against
`phase4_manifest.json → contract.parameter_map`; the spec is the certified YAML
under its accepted SHA-256; θ̂ is the accepted 47-vector under its accepted
SHA-256; the loader is `dclaborsupply.data.loader.load_singles`; the likelihood is
`build_jax_singles_ll(..., per_group=True)`; the reducer is `ScoreStreamReducer`.
**The only patched quantity is `household_limit=24`.** `test_E8` re-runs the
whole path at `household_limit=6` and asserts it reproduces the 24-household
result as a prefix, which is what makes the subset-size knob safe.

**Failure demonstration.** `test_E11_a_mutated_evaluator_would_be_caught` (also in
this family, listed under PROOF-6) perturbs the evaluator by `1e-6` inside a
`monkeypatch` scope and asserts the E2 comparison then *exceeds* its tolerance —
so a green E2 is not vacuous.

### PROOF-6 — the integration test would catch a wrong evaluator

```text
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -k "E11 or E12 or E10 or A3 or B3 or B4" -v
```

Expected: `6 passed`. These are the mutation and rejection proofs:

| Test | Mutation / bad input | Asserted consequence |
| --- | --- | --- |
| `E11` | `_gender_score_block` returns `block[0,0] + 1e-6` | E2's tolerance is exceeded; digest changes |
| `E12` | `jax.jacfwd` returns a float32 jacobian | `ScoreStreamError: … != float64` (not a silent upcast) |
| `E10` | batch names households absent from the gender frame | `ScoreStreamError: household slice has …` |
| `A3` | `phase4_manifest.json` free-name order permuted | `ScoreStreamError: … free-name sequence …` |
| `B3` | a household in both builders' group-id sets | `ScoreStreamError: … strictly increasing` |
| `B4` | non-integral household identifier | `ScoreStreamError: … not integral` |

### PROOF-7 — Increment-A code creates nothing on disk

```text
D=outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts
ls $D | wc -l; git status --porcelain -uall | wc -l
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -q
ls $D | wc -l; git status --porcelain -uall | wc -l
```

Observed (POSIX shell / Git Bash), most recent run:

```text
before: attempts=72 dirty=8
42 passed in 58.83s
after:  attempts=72 dirty=8
```

The `attempts/` count and the dirty-file count are unchanged across a full
Increment-A run. The §2.6 attempt directories are therefore attributable to the
pre-existing `test_29_subprocess_dry_run_never_optimizes`, not to this increment.
(`dirty=8` = 3 deliverables + this report + the 4 files of the two §2.6 attempt
directories.)

### PROOF-8 — numerical evidence against the design tolerances

Save as `proof8.py` and run `python proof8.py` (kept as a file so no shell
quoting is involved):

```python
import sys; sys.path.insert(0, "scripts/p2a")
import numpy as np, p2a_phase5_score_stream as S
b = S.build_production_binding(household_limit=24)
g = lambda bs, m="jacfwd": np.vstack(
    [S.compute_batch_scores(b, x, mode=m) for x in b.order.batches(bs)])
A, B, C, D = g(8), g(3), g(24), g(8, "jacrev")
mx = float(np.max(np.abs(A)))
print("max|S|                    ", mx)
print("T-11 bar   1e-12*max|S|   ", 1e-12 * mx)
print("  |S_bs3  - S_bs8|        ", float(np.max(np.abs(A - B))))
print("  |S_bs24 - S_bs8|        ", float(np.max(np.abs(A - C))))
print("T-16 bar   1e-10*max|S|   ", 1e-10 * mx)
print("  |S_jacfwd - S_jacrev|   ", float(np.max(np.abs(A - D))))
```

Expected output:

```text
max|S|                     30.23468094208269
T-11 bar   1e-12*max|S|    3.023468094208269e-11
  |S_bs3  - S_bs8|         8.881784197001252e-16
  |S_bs24 - S_bs8|         0.0
T-16 bar   1e-10*max|S|    3.023468094208269e-09
  |S_jacfwd - S_jacrev|    1.0658141036401503e-14
```

**Failure demonstration.** `test_E4` and `test_E5` assert exactly these bounds;
raising the perturbation in `test_E11` from `1e-6` past the bars turns them red.

---

## 6. Test results

```text
python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -q
42 passed in 59.25s

python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -m "not production" -q
29 passed, 13 deselected in 0.63s

python -m pytest tests/p2a/test_p2a_phase5_score_stream.py -m production -q
13 passed, 29 deselected in 58.84s

python -m pytest -q                       # whole repository, regression cover
104 passed in 80.43s
```

42 = 29 fast + 13 production. The repository total is 104 = 62 pre-existing + 42
delivered here. The `-v` listings quoted in PROOF-3 and PROOF-5 were captured
before `test_E12` was added; that test is the only difference.

### 6.0 Order-independence check (a real defect this caught)

Every production test was additionally run **in isolation**, because family E's
first draft passed only as a family. Cause, found and fixed before this report was
issued: `engine_jax._load_jax()` enables `jax_enable_x64` **lazily, on the first
builder call**, so any `jnp` array created before that call is float32. The test's
direct reference helper built `jnp.asarray(base_full)` first and therefore ran the
whole reference in float32 whenever it executed before any other JAX work — a
false-green risk, not a false-red. Two changes:

* `build_production_binding` now invokes the accepted float64 initialiser
  **eagerly** and raises if `jax_enable_x64` is not then active, so the binding —
  not the call ordering — carries the contract;
* the reference helper asserts `jax_enable_x64` and `base_full.dtype == float64`
  before differentiating.

Verified after the fix, each test run alone:

```text
E1 PASS  E2 PASS  E3 PASS  E3b PASS  E4 PASS  E5 PASS  E6 PASS
E7 PASS  E8 PASS  E9 PASS  E10 PASS  E11 PASS  E12 PASS
```

Lint: `python -m ruff check --select F,E9 <deliverables>` → `All checks passed!`.
The `UP***`/`I001` style codes are not fixed, deliberately: the accepted
production runner `scripts/p2a/run_p2a_regionlive_rebuild.py` carries the
identical profile (118 `UP006`, 29 `UP045`, 3 `I001`, …), and the module matches
the surrounding code's `typing.Dict/List/Tuple` idiom rather than diverging from it.

### 6.1 Measured quantities against the design register

| Design quantity | Bar | Observed (24-household subset) | Margin |
| --- | --- | --- | --- |
| T-11 chunk-route invariance | `≤ 1e-12 · max\|S\|` = `3.023e-11` | `8.882e-16` (bs 3 vs 8); `0.0` (bs 24 vs 8) | ~4.6 orders |
| T-16 forward/reverse agreement | `≤ 1e-10 · max\|S\|` = `3.023e-09` | `1.066e-14` | ~5.5 orders |
| Aggregate `Σs` chunk stability | `≤ 1e-12 · max\|S\|` | `3.553e-15` | ~4 orders |
| `M₃₇` chunk stability | accumulation rounding | `2.274e-13` | — |
| `M₃₇`, `M₃₅` symmetry | exact by construction | `0.0`, `0.0` | exact |
| `M₃₅` = by-name interior block of `M₃₇` | bitwise | bitwise equal | exact |
| Raw derivative dtype | `float64` | `float64`, `jax_enable_x64 True` | enforced |

### 6.2 Fingerprints produced (informational; frozen only in Increment C)

| Object | Value |
| --- | --- |
| Ordered 37 `free_names` SHA-256 (T-17) | `cb50ecd838951c83a7c7844e388c764a3f4b5686047d94b733b71e3da32d3333` |
| Ordered 35 interior names SHA-256 (T-17) | `44af628ff113e675ec530e70e712da4ce3f0231e7bea5b449e144046e4c3942b` |
| Canonical order fingerprint, full 1,555 | `133914d863d411534b4bb60e88e12c2b797edcb1d428a427fdb1c607f4f31334` |
| Canonical order fingerprint, 24-household test subset | `59724b8293c7603aa3e720b36066ac901e2ac996202c62ab9b154eed2fd39a24` |
| Score-stream digest, 24-household subset, `jacfwd`, batch 24 | `a15cebb8a2ee1effaf99a1217fdba416f83d3b7c8537ae4f95c0f42561c96f50` |

The full-1,555 order fingerprint is derived from loader group ids only and
involves **no** score evaluation, so producing it is not a full-population run.
The two digest values are test-subset values and carry no inferential content.

---

## 7. No-persistence evidence

Addendum §6 / T-23S is an artifact-persistence gate. Increment A's contribution:

1. **Structural.** The module has no write path of any kind. Its only file
   access is four reads: the parameter-map CSV, `phase4_manifest.json`,
   `estimation_results.json`, and the frozen stem parquet + `__mnlmeta.json`
   (plus `open(path,"rb")` inside the SHA-256 helper). Proved statically by
   `test_D1`; the scanner is proved non-vacuous by `test_D2`.
2. **No `(G × 37)` object exists.** `run_score_stream` never concatenates and
   never returns score rows. `ScoreStreamResult` carries exactly three arrays,
   `(37,)`, `(37,37)`, `(35,35)` — asserted by `test_D3`, which also asserts the
   household count appears in none of their shapes.
3. **Batches are released.** `ScoreStreamReducer.update` deletes every local view
   before returning and holds no attribute referencing the block;
   `run_score_stream` `del`s the block each iteration. `test_D4` proves this with
   a `weakref` that must be dead after `gc.collect()`.
4. **Failure finalisation is truthful and silent about values.**
   `ScoreStreamError` messages carry shapes, counts, names and canonical
   positions only. `test_D6` asserts no score value and no `nan` token appears in
   the non-finite failure message and that no file is left behind.
5. **Behavioural, synthetic.** `test_D5` runs a full stream in a temporary cwd and
   asserts the temp tree is empty and the accepted `region_live_v1` tree is
   unchanged (path + size for all 286 files).
6. **Behavioural, real path.** `test_E7` does the same around a real
   24-household production stream, additionally snapshotting
   `docs/France_case/P2a`.
7. **Whole-suite.** PROOF-7 shows the `attempts/` count and the dirty-file count
   unchanged across a complete Increment-A run.
8. **Nothing printed.** `test_D8` asserts stdout and stderr are empty. No test in
   the file prints or persists a score value.

What Increment A does **not** discharge, and does not claim to: the output
allowlist, the staging/attempt member set, and the STOPPED finalisation path are
Increment C objects; T-23S can only be closed there.

---

## 8. Residual limitations

1. **Digest integer encoding is an implementation decision, not a design
   ratification.** Addendum §2 leaves it open; §4.1 fixes it as `int64` LE and
   publishes it. Reviewer should ratify before Increment C freezes it.
2. **The digest is batch-size-scoped.** Measured at 1-ULP level: batch size 3
   differs from 8 and 24. Consequence: **T-12S must compare at a fixed batch
   size**, which addendum §4 already requires by recording "actual batch size".
   No batch-size-independent digest claim is made. Increment C should record the
   batch size in `score_aggregate_summary.json` (addendum §3 already requires it)
   and refuse a reproduction comparison across differing batch sizes.
3. **`jacfwd` and `jacrev` produce different digests** (same aggregates to
   `1.07e-14`). The design baseline is `jacfwd`; `jacrev` exists only as the
   T-16 reference. Increment C must record the mode alongside the batch size.
4. **Compilation cost scales with batch count.** Each batch traces and compiles a
   fresh likelihood (the builder captures data as device constants, so no jit
   cache is shared across batches). At 24 households this is ~1.4 s for one batch
   and ~5 s for three. The full 1,555-household dry run's wall time is therefore
   **`UNKNOWN` and must be measured in Increment C**, together with peak memory
   (design v4 §5.4 already flags peak memory as `UNKNOWN` and manifest-required).
   Increment A performed no full-population run.
5. **Score identity (T-1/T-4) is not tested here.** `Σ_g s_g = −∇negLL` can only
   be checked against the accepted 37-element `gradient_free` over **all** 1,555
   households; on a 24-household subset it is meaningless. The addendum §5 gate
   is an Increment-B/C obligation. Increment A supplies the streamed aggregate
   vector the gate consumes.
6. **Bread, covariance, correction scalar, regional tests, diagnostics, manifest
   and transaction are absent by design** (Increments B and C).
7. **Unrelated worktree entries** from the pre-existing Phase-3 safety test —
   §2.6, two directories. Manager decision requested; not deleted, not committed.
   Increment C should note that any full-suite run adds one more.
8. **`jax_enable_x64` is a process-global, lazily-set flag** (§6.0). Increment C's
   runner must activate it before any array creation and record it in the manifest
   (T-15), and must not assume an earlier import did so.
9. **The 24-household subset size is a test constant**, chosen to keep family E
   under a minute while spanning both genders and several chunkings (batch sizes
   3, 5, 8, 12, 24 and full). It is not a statistical sample and carries no
   inferential content.

---

## 9. Immediate next action

1. **Independent Codex review A** of
   `scripts/p2a/p2a_phase5_score_stream.py` and
   `tests/p2a/test_p2a_phase5_score_stream.py` at MNL
   `b5169293b647dda3e07070c678f8d46d33b1bf89`, executing PROOF-1 … PROOF-8
   verbatim. Charter §6: `APPROVE` / `APPROVE AFTER FIXES` (one narrow
   remediation) / `REJECT` (E2 halt). **Increment B must not start before an
   approving verdict.**
2. **Two reviewer rulings requested** with the verdict: (a) ratify the §4.1
   digest byte contract; (b) confirm that T-12S will compare at a fixed
   (batch size, AD mode), per §8 items 2–3.
3. **Manager decision requested** on the §2.6 incidental `attempts/` entry:
   commit as routine test evidence, or authorise removal.
4. On `APPROVE`, proceed to **Increment B** — bread loading and authentication
   (`hessian_free.npy`, T-5/T-6), model-based and corrected robust covariance,
   active-bound and fixed-pin reporting, H0-A/B/C/G regional tests, numerical
   gates and diagnostics, aggregate serializers — consuming this increment's
   `ScoreStreamResult` unchanged.

**FINAL VERDICT: READY FOR REVIEW A**
