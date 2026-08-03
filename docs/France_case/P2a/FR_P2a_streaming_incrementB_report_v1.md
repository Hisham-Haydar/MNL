# FR P2a — JMP-M05C Streaming Inference — Increment B implementation report — v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Increment:** B — covariance and inference objects (charter §4-B)
**Mode:** implementation + tests only. No commit. No runner/transaction/reproduction. No full-population run.
**Date:** 2026-08-02
**MNL HEAD (unchanged throughout):** `92e299de6313bad0b0421c0db3dd268fdbcfdb59`
**Nested `dclaborsupply` HEAD = MNL gitlink (unchanged):** `27756a06ea189339aa82915ed2124628afed20eb`

---

## 1. Increment verdict

**READY FOR REVIEW B**

Every charter §4-B deliverable is implemented as pure functions over the
Increment-A aggregates plus the accepted artifacts: the authenticated bread, the
model covariance, the corrected robust conditional-35 sandwich with CR0
recoverable, the exact 13-column 47-row reporting table, the H0-A/B/C/G regional
battery in both model and robust form, every design-v4 T/W gate computable at
this layer, and the addendum §3 aggregate serializers. 59 Increment-B tests pass;
the full repository suite is **196 passed, 1 deselected**.

Three things a reviewer should read before the numbers, because each is a
disclosure rather than a clean result:

1. **The first-64 production integration is a `subset-diagnostic`, not
   inference.** The bread is always the whole-sample Phase-4 Hessian, so pairing
   it with a 64-household meat gives a covariance whose scale is wrong by `G/n`.
   Rather than caveat this in prose, the module *labels* it: every covariance
   carries `inference_grade`, and W-1/W-4/W-5 echo it. §5.4 states exactly which
   gates are meaningful at subset scale and which are not.
2. **W-1 flags on the subset, correctly.** Its `min_ratio` is `0.061`, below the
   `[0.2, 5]` band — the arithmetic consequence of item 1, not a defect. It is
   warning-tier and cannot fail a run (design v4 §14).
3. **The committed parameter map's `grad_free_negll` column is a
   reduced-precision rendering.** `phase4_diagnostics.json → gradient_free`
   reproduces design v4's published interior maximum *exactly*; the CSV differs
   in the 13th significant digit. The module therefore reads the JSON and never
   the CSV for gradient values — the same authoritative/rendering distinction
   design v4 F-4 drew for the Hessian. §9.2.

No design formula, gate, tolerance or constant was altered. No gate was weakened.

---

## 2. Starting state

Preflight, verified before any file was created.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| MNL HEAD | `92e299de6313bad0b0421c0db3dd268fdbcfdb59` | identical | PASS |
| MNL worktree | fully clean | clean (`--untracked-files=all` empty) | PASS |
| Nested HEAD | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| MNL gitlink | `27756a06…` | `160000 commit 27756a06ea189339aa82915ed2124628afed20eb` | PASS |
| Nested worktree | clean | clean | PASS |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | identical | PASS |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | identical | PASS |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | identical | PASS |

HEAD `92e299d feat(p2a): streaming score reducer - increment A reviewed` is the
committed Increment-A state approved by Review A v2. Increment B builds on it and
modifies none of its three files (§8.4).

---

## 3. Deliverable inventory with SHA-256

Two new, untracked files. Nothing existing was modified.

| Path | SHA-256 | Bytes | Lines |
| --- | --- | --- | --- |
| [scripts/p2a/p2a_phase5_inference.py](scripts/p2a/p2a_phase5_inference.py) | `218859e91073cfb4d325ec9da5870700fec49c6232d9d6fdb3094672938d98a3` | 57,065 | 1,210 |
| [tests/p2a/test_p2a_phase5_inference.py](tests/p2a/test_p2a_phase5_inference.py) | `90633103d0540bd04796025a18cb2b1f04a628a401d0e4d548fc4a58a5a5be75` | 38,294 | 836 |

Recompute:

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import hashlib;[print(hashlib.sha256(open(p,'rb').read()).hexdigest(),p) for p in ['scripts/p2a/p2a_phase5_inference.py','tests/p2a/test_p2a_phase5_inference.py']]"
```

### 3.1 Public surface

| Object | Role |
| --- | --- |
| `load_bread` → `Bread` | authenticate, symmetrise, name-reduce to `H_II`; never recompute |
| `load_accepted_gradients` → `AcceptedGradients` | the authoritative free gradient, projected by name |
| `build_covariances` → `Covariances` | `V_model`, `V_robust`, `V_robust_cr0`, SEs, diagnostics |
| `correlation_from_covariance` | exact unit diagonal |
| `regional_selector`, `null_selector` | `E_R` (10×35) and `A` (q×10), both by name |
| `run_regional_tests` → `RegionalTests` | H0-A/B/C/G, model and robust, separate p-values |
| `build_parameter_table`, `validate_parameter_table` | the exact 13-column 47-row schema |
| `gate_T5…T22`, `warning_W1…W5` | pure checkable gate functions returning `GateResult` |
| `gating_failures` | gating-tier verdict; warnings never determine it |
| `write_matrix`, `write_table`, `write_score_aggregate_summary` | the only write paths |
| `assert_aggregate_payload` | refusal-by-construction guard |
| `InferenceError`, `SerializerRefusal` | typed contract violations with `IB-*` codes |

---

## 4. Design conformance map

| # | Prompt / charter requirement | Where implemented | Governing section |
| --- | --- | --- | --- |
| 1 | Bread: load `hessian_free.npy` under its SHA-256, symmetrise on load, gate at `2.3588019878151842e-4`, name-reduce to `H_II`, never recompute | `load_bread`; `Hs = (H + Hᵀ)/2`; `H_II = Hs[np.ix_(sel, sel)]` with `sel` from the authenticated interior names, cross-checked against the name sequence | design v4 §8.1; T-5, T-6 |
| 2 | Model covariance by solves, never explicit inverses | `_cho_inverse` = `cho_solve(cho_factor(H_II), I₃₅)`, exactly the route design v4 §8.2 names. `np.linalg.inv` appears nowhere (proved statically by `test_F9`); `np.linalg.pinv` appears once, as the T-8 reference design v4 §15 itself prescribes | design v4 §8.2, §8.3; T-8 |
| 3 | `V35 = c · H_II⁻¹ M_35 H_II⁻¹`, `c = 1555/1520`, CR0 recoverable | `build_covariances`; `V_robust_cr0 = B M B` stored alongside, and `V_robust == c · V_robust_cr0` holds by construction and is asserted bitwise | design v4 §9.1, §10.1; deputy D-1 |
| 4 | 13-column schema, literal `NA` for the two active-bound and ten pinned rows, mandatory footnote | `build_parameter_table` + `validate_parameter_table`; `PIN_TABLE_FOOTNOTE` is the design v4 §12.4 text verbatim | design v4 §11.3, §12.2, §12.4, §17.3 |
| 5 | `E_R` (10×35) by authenticated names; H0-A/B/C/G; Wald via solves; separate `p_model`/`p_robust` | `regional_selector`, `null_selector`, `run_regional_tests`; `W = d' (A V_RR A')⁻¹ d` via `cho_factor`/`cho_solve` | design v4 §13.2, §13.4; T-14 |
| 6 | Every design-v4 T/W gate computable at this layer, as pure checkable functions; no gate weakened, no constant altered | T-5, T-6, T-7, T-8, T-9, T-10, T-14, T-17, T-18, T-19, T-22; W-1…W-5. Each returns a `GateResult` carrying `passed`, `observed`, `bar` | design v4 §14, §15, §16 |
| 7 | Addendum §3 serializers, refusing row-level or id-paired content by construction | `AGGREGATE_ARTIFACTS` closed set + `assert_aggregate_payload`; three write functions and no other write path (proved statically by `test_J7`) | addendum §3, §6; charter §8 |
| 8 | Synthetic analytic fixtures; production integration on streamed first-64; failure tests for every rejection path | families F, K and G/H/I/J respectively — 59 tests | charter §5 |

### 4.1 Frozen constants carried verbatim

`HESSIAN_SYMMETRY_THRESHOLD = 2.3588019878151842e-4`;
`KAPPA_BE_CERTIFIED = 6.0424e-12`; `COVARIANCE_PSD_REL = 1e-10`;
`SYMMETRY_REL = 1e-12`; `SOLVE_VS_PINV_ATOL = 1e-8`;
`STATIONARITY_SE_FRACTION = 0.05`; `KKT_ACTIVITY_FACTOR = 100`;
`CORRELATION_BOUND = 1 + 1e-10`; `Z_975 = 1.959963984540054`;
`W1_RATIO_RANGE = (0.2, 5.0)`; `CORRECTION_C = 1555/1520`;
`CHI2_CRIT_95 = {10: 18.307038…, 7: 14.067140…, 2: 5.991464…, 1: 3.841458…}`;
`PHASE4_MIN_EIG/MAX_EIG/CONDITION_NUMBER` at `rtol 1e-10`.
`test_F6` and `test_G6` pin these against the design's published values.

### 4.2 Deliberate non-scope

No runner, transaction, lock, staging directory, attempts handling, manifest,
console log, `complete/`, T-12S reproduction, T-13 immutability recheck or T-23
custody block — all Increment C. No optimizer call, no Hessian evaluation, no
score evaluation beyond the Increment-A reducer, no full-population run. No
package file touched. No design, spec, θ̂, pin, or tolerance changed.

T-1/T-2/T-3/T-4/T-11/T-15/T-16/T-20 belong to the Increment-A score layer and
are already covered there; they are not re-implemented here.

---

## 5. Numerical results vs design bars

All from the accepted artifacts and the streamed first-64 aggregates.
Reproduce with PROOF-12 (§6).

### 5.1 Bread (scale-free — exact at any subset size)

| Quantity | Bar / anchor | Observed | Verdict |
| --- | --- | --- | --- |
| `hessian_free.npy` SHA-256 | `e9ca080e…4061` | identical | PASS |
| `max\|H − Hᵀ\|` (T-6) | `≤ 2.3588019878151842e-4` | `1.8189894035458565e-12` | PASS, ~8 orders |
| `min_eig(Hs)` | `0.1037326963880782`, rtol `1e-10` | `0.10373269638807983` | PASS |
| `max_eig(Hs)` | `42048.457934380494`, rtol `1e-10` | `42048.45793438045` | PASS |
| condition number | `405353.94719781954`, rtol `1e-10` | `405353.9471978127` | PASS |
| rank(Hs) | 37 | 37 | PASS |
| Cholesky of `H_II` | succeeds | succeeds | PASS |

### 5.2 Meat, correction and solves

| Quantity | Bar | Observed | Verdict |
| --- | --- | --- | --- |
| `max\|M − Mᵀ\|` before symmetrisation (T-7) | `≤ 1e-12 · max\|M\|` | `0.0` exactly | PASS |
| `min_eig(M)` (T-7) | `≥ −6.0424e-12 · max_eig` = `−1.42580003805006e-08` | `+2.0597024553162405e-13` | PASS |
| correction `c` (T-10) | `1555/1520` | `1.0230263157894737` | PASS |
| SE inflation | `+1.1448 %` | `1.1447633735663931 %` | PASS |
| solve vs pinv (T-8) | `≤ 1e-8` | `1.9602097722781764e-12` | PASS, ~4 orders |
| `max\|H_II · V_model − I₃₅\|` | residual of the solve | `1.2038803846172754e-14` | — |

### 5.3 Covariance and stationarity

| Quantity | Bar | Observed | Verdict |
| --- | --- | --- | --- |
| `V_model` symmetry (T-9) | `≤ 1e-12 · max\|V\|` | `3.05e-16` | PASS |
| `V_robust` symmetry (T-9) | `≤ 1e-12 · max\|V\|` | `1.99e-17` | PASS |
| `V_model` min eig (T-9, PD) | `> 0` | `2.378208564786934e-05` | PASS |
| `V_robust` min eig (T-9, PSD) | `≥ −1e-10 · max_eig` = `−4.43e-12` | `−9.474781170961761e-20` | PASS |
| correlations (T-18) | `\|ρ\| ≤ 1 + 1e-10`, unit diagonal | bound respected, diagonal exactly `1.0` | PASS |
| T-19 displacement / robust SE | `≤ 0.05` | `3.819780309704067e-4` (worst: `beta_l0_sf`) | PASS |
| `V_RR` (T-14) | PD, rank 10, all `W` finite, df `[10,7,2,1]` | min eig `1.717e-06`, rank 10, all finite | PASS |

### 5.4 What the first-64 subset does and does not establish

This is the honest part of the section. The bread is always the whole-sample
Phase-4 Hessian; the meat here is 64 households. The three classes:

| Class | Gates | Status on the subset |
| --- | --- | --- |
| **Scale-free** — depend only on the accepted bread, map, gradient and frozen constants | T-5, T-6, T-8, T-10, T-17, T-22 | **Exact and final.** These results will not change at 1,555. |
| **Structural** — properties of whatever aggregate is supplied | T-7, T-9, T-14, T-18 | **Validated.** They prove the algebra and the solve discipline, at subset scale. |
| **Whole-sample** — meaning requires `n = G = 1555` | W-1, W-4, W-5, all Wald magnitudes, and `M`'s rank | **Not inferential here.** Reported, labelled `subset-diagnostic`, never presented as a result. |

Consequences visible in the numbers, all expected:

* **W-1 flags** (`min_ratio 0.061`, `max_ratio 0.426`, band `[0.2, 5]`). A
  64-household meat gives robust SEs about `√(64/1555) ≈ 0.20` of full-sample,
  against a full-sample model SE. Warning-tier, non-gating.
* **`rank(M) = 34`, `min_eig = 2.06e-13`.** Design v4 §9.3 expects generic full
  rank 35 at `G/K ≈ 44`; at `n = 64` the ratio is `1.8`, so near-deficiency is
  arithmetic, not a defect. T-7's PSD floor is still cleared by five orders.
* **Wald magnitudes are inflated by ≈ `G/n ≈ 24`** (e.g. H0-A `W_robust`
  `20313.7`). They are reported for structural completeness only. **No regional
  inferential claim is made anywhere in this increment.**
* **W-5 `‖Σ_g s_{g,I}‖_∞ = 22.52`** on the subset, against the whole-sample
  published `1.0992597206183063e-4`. The first-order condition is a whole-sample
  property; a prefix sum is not near zero. Expected, and why W-5 is whole-sample.
* **T-19 passes conservatively.** Smaller subset SEs make its displacement/SE bar
  strictly *harder*, so the `3.82e-4` against `0.05` is a valid one-sided signal.

### 5.5 Independent corroboration of design v4's published values

Three quantities recomputed here reproduce the design memo exactly, which is
useful evidence that this layer is reading the same objects Phase 4 accepted:

| Quantity | Design v4 | Recomputed | Match |
| --- | --- | --- | --- |
| interior `max\|∇negLL\|` (§9.2, §10.3) | `1.0992597206183063e-4` at `beta_w_educH` | identical, same coordinate | exact |
| `μ_sm` (§11.1) | `0.8445544161794221` | identical | exact |
| `μ_sf` (§11.1) | `1.4682021491125388` | identical | exact |
| T-22 activity ratios (§11.5) | `7,682.9` and `13,356.3` | `7682.9`, `13356.3` | to published precision |
| regional interior positions (§7.3) | 13…22 | 13…22 | exact |

---

## 6. Proofs (reviewer-runnable)

**Every command below was executed exactly as printed, in PowerShell, from
`C:\Users\hisham\Repo\MNL`.** All are read-only, create no reviewer-owned file,
require no edit, and use the exact virtual-environment interpreter.
`-p no:cacheprovider` keeps `.pytest_cache` from being written. Every full-suite
command deselects test 29, which the Increment-A conftest guard also enforces.

### PROOF-1 — starting state and worktrees

```powershell
cd C:\Users\hisham\Repo\MNL
git rev-parse HEAD
git status --porcelain --untracked-files=all
git ls-tree HEAD dclaborsupply-monorepo
git -C dclaborsupply-monorepo rev-parse HEAD
git -C dclaborsupply-monorepo status --porcelain --untracked-files=all
```

Expected:

```text
92e299de6313bad0b0421c0db3dd268fdbcfdb59
?? scripts/p2a/p2a_phase5_inference.py
?? tests/p2a/test_p2a_phase5_inference.py
160000 commit 27756a06ea189339aa82915ed2124628afed20eb	dclaborsupply-monorepo
27756a06ea189339aa82915ed2124628afed20eb
(no output - nested worktree clean)
```

### PROOF-2 — accepted bundles and the bread hash

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import hashlib,os;s=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();b=lambda d,m:hashlib.sha256(('\n'.join(f'{n}:{s(os.path.join(d,n))}' for n in sorted(os.listdir(d)) if n!=m)).encode('utf-8')).hexdigest();print('phase3',b('outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete','phase3_manifest.json'));print('phase4',b('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete','phase4_manifest.json'));print('bread ',s('outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/hessian_free.npy'))"
```

Observed:

```text
phase3 2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b
phase4 5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3
bread  e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061
```

### PROOF-3 — the complete Increment-B test set

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider
```

Observed: `59 passed in 5.42s`

### PROOF-4 — fast families only

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -m "not production"
```

Observed: `50 passed, 9 deselected in 1.24s`

### PROOF-5 — production family (real reducer, real bread)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -m production
```

Observed: `9 passed, 50 deselected in 5.07s`

### PROOF-6 — bread loading and every rejection path (family G)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_G1 or test_G2 or test_G3 or test_G4 or test_G5 or test_G6 or test_G7 or test_G8"
```

Observed: `11 passed, 48 deselected in 0.77s`

Failure demonstrations inside the selection: `test_G4` writes a bread differing
by `1e-9` in one entry — still a valid PD matrix — and asserts `IB-BREADHASH`;
`test_G5` parametrises shape, dtype, non-finite and symmetry-threshold breaches;
`test_G7` feeds an indefinite `H_II` and asserts the Cholesky route refuses
rather than silently returning a pseudo-inverse.

### PROOF-7 — the 13-column schema and the NA rules (family H)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_H1 or test_H2 or test_H3 or test_H4 or test_H5 or test_H6 or test_H7"
```

Observed: `14 passed, 45 deselected in 1.14s`

`test_H6` is the failure demonstration: eight parametrised violations — dropped
column, extra `flag` column, wrong row count, unknown status, a numeric SE on a
pinned row, a zero SE on an active-bound row, a non-zero pin gradient, and a
`lower` bound side — each asserted to raise the matching `IB-*` code.

### PROOF-8 — serializer refusal by construction (family J)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_J1 or test_J2 or test_J3 or test_J4 or test_J5 or test_J6 or test_J7 or test_J8 or test_J9"
```

Observed: `9 passed, 50 deselected in 0.44s`

### PROOF-9 — analytic fixtures (family F)

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest tests\p2a\test_p2a_phase5_inference.py -q -p no:cacheprovider -k "test_F1 or test_F2 or test_F3 or test_F4 or test_F5 or test_F6 or test_F7 or test_F8 or test_F9"
```

Observed: `9 passed, 50 deselected in 1.07s`

### PROOF-10 — the safe full repository suite

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "not test_29_subprocess_dry_run_never_optimizes"
```

Observed: `196 passed, 1 deselected in 93.65s (0:01:33)`

### PROOF-11 — no Phase-5 artifact was written into the repository

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "from pathlib import Path;named=[str(p) for p in Path('.').rglob('*') if p.is_file() and set(p.parts).isdisjoint({'.git','.venv','__pycache__'}) and ('score' in p.name.lower() or 'covariance' in p.name.lower() or p.name.startswith('phase5_')) and p.suffix in {'.npy','.csv','.json','.npz'}];print('phase5/score/covariance artifacts in repo:', named if named else 'NONE')"
```

Observed: `phase5/score/covariance artifacts in repo: NONE`

### PROOF-12 — the numbers of §5

```powershell
cd C:\Users\hisham\Repo\MNL; & .\.venv\Scripts\python.exe -c "import sys;sys.path.insert(0,'scripts/p2a');import numpy as np,p2a_phase5_score_stream as ss,p2a_phase5_inference as ib;pm=ss.load_parameter_map();br=ib.load_bread(pm);gr=ib.load_accepted_gradients(pm);r=ss.run_score_stream(ss.build_production_binding(household_limit=64),batch_size=64);t7=ib.gate_T7_meat_validity(r.meat_interior35);cv=ib.build_covariances(br,r.meat_interior35,meat_n_households=r.n_households);print('bread asym      ',repr(br.diagnostics['max_abs_asymmetry_raw']),'bar',repr(ib.HESSIAN_SYMMETRY_THRESHOLD));print('bread min_eig   ',repr(br.diagnostics['min_eig_Hs']),'anchor',repr(ib.PHASE4_MIN_EIG));print('bread cond      ',repr(br.diagnostics['condition_number_Hs']),'anchor',repr(ib.PHASE4_CONDITION_NUMBER));print('meat asym       ',repr(t7.observed['max_abs_asymmetry']));print('meat min_eig    ',repr(t7.observed['min_eig']),'floor',repr(t7.bar['psd_floor']));print('correction c    ',repr(cv.correction_c));print('solve vs pinv   ',repr(cv.diagnostics['solve_vs_pinv_max_abs_dev']),'bar',repr(ib.SOLVE_VS_PINV_ATOL));print('H_II@V_model-I  ',repr(float(np.max(np.abs(br.H_II@cv.V_model-np.eye(35))))));print('T-22 int max|g| ',repr(gr.interior_max_abs),'at',gr.interior_argmax_name);print('T-22 ratios     ',{k:round(v/gr.interior_max_abs,1) for k,v in gr.active_multipliers.items()});print('T-19 max ratio  ',repr(ib.gate_T19_stationarity(br,cv,gr.interior).observed['max_ratio']),'bar',ib.STATIONARITY_SE_FRACTION);print('inference grade ',cv.diagnostics['inference_grade'])"
```

Observed:

```text
bread asym       1.8189894035458565e-12 bar 0.00023588019878151842
bread min_eig    0.10373269638807983 anchor 0.1037326963880782
bread cond       405353.9471978127 anchor 405353.94719781954
meat asym        0.0
meat min_eig     2.0597024553162405e-13 floor -1.42580003805006e-08
correction c     1.0230263157894737
solve vs pinv    1.9602097722781764e-12 bar 1e-08
H_II@V_model-I   1.2038803846172754e-14
T-22 int max|g|  0.00010992597206183063 at beta_w_educH
T-22 ratios      {'beta_l_age2_sm': 7682.9, 'beta_l_age2_sf': 13356.3}
T-19 max ratio   0.0003819780309704067 bar 0.05
inference grade  subset-diagnostic
```

The last line is the point of §5.4: the object labels itself.

---

## 7. Test results

```text
Increment-B set, run 1                     59 passed in 5.54s
Increment-B set, run 2                     59 passed in 5.52s
  fast families (-m "not production")      50 passed,  9 deselected in 1.25s
  production family (-m production)         9 passed, 50 deselected in 5.45s
full repository, test-29 deselected       196 passed, 1 deselected in 89.19s
attempts/ count after every run                                          70
ruff check --select F,E9 (both files)                    All checks passed!
git diff --check                                                     exit 0
```

Repository total: 196 = 137 pre-existing (62 legacy + 75 Increment-A) + 59
Increment-B, with test 29 deselected in every full-suite invocation.

Family breakdown: F 9 (analytic), G 11 (bread + rejections), H 14 (schema),
I 7 (gates), J 9 (serializers), K 9 (production path).

### 7.1 Failure demonstrations shipped as tests

| Test | Injected fault | Asserted refusal |
| --- | --- | --- |
| `test_G4` | bread perturbed by `1e-9` (still valid PD) | `IB-BREADHASH` |
| `test_G5` ×4 | wrong shape / float32 / NaN / symmetry breach | `IB-BREADSHAPE`, `IB-BREADDTYPE`, `IB-BREADFINITE`, `IB-BREADSYM` |
| `test_G7` | indefinite `H_II` | `IB-CHOL` — never a silent pseudo-inverse |
| `test_H6` ×8 | eight distinct schema violations | `IB-SCHEMA`, `IB-NA`, `IB-PIN`, `IB-BOUND` |
| `test_H7` | forged regional / null names | `IB-REGNAME`, `IB-NULLNAME` |
| `test_I1` | negative eigenvalue below the T-7 floor; asymmetry above `1e-12·max\|M\|` | T-7 fails |
| `test_I2` | `V_robust` shifted non-PSD | T-9 fails |
| `test_I4` | multiplier just under `100×` | T-22 fails |
| `test_I5` | interval endpoint exactly equal to a bound | W-4 triggers (equality triggers, per §16.2) |
| `test_J1`–`test_J4`, `test_J6` | 1555×37 block, 5×37 block, id-paired frame, member outside the closed set, non-finite | `IB-REFUSE` |
| `test_K9` | a score matrix fed to the covariance builder | `IB-MEATSHAPE`, `IB-MEATFINITE` |
| `test_J8`, `test_F9` | scanner non-vacuity | probe detected; `np.linalg.inv` absent |

---

## 8. No-persistence and serializer-refusal evidence

1. **Closed persistable set.** `AGGREGATE_ARTIFACTS` is a fixed tuple of 16
   member names drawn from addendum §3 and charter §8. `_target()` refuses any
   other name before a path is even formed — `test_J4` asserts
   `phase5_scores_free.npy` is refused and that the target directory stays empty.
2. **Structural refusal, not name-based.** `assert_aggregate_payload` refuses:
   any array or frame whose leading dimension exceeds 47 (the largest legitimate
   aggregate row count); any 2-D array with 37 columns whose row count is not 37
   (a score block, not `M_37`); any frame carrying an identifier-like column
   (`idhh`, `idorighh`, `cluster_id`, `household`, `hh_id`, `row_index`,
   `score_row`); and any non-finite content. A *mislabelled* household-scale
   array is refused just as firmly as a correctly-labelled one — `test_J1` and
   `test_J2` prove both.
3. **Only three write paths exist.** `test_J7` walks the module AST and asserts
   that no function other than `write_matrix`, `write_table` and
   `write_score_aggregate_summary` contains a write call, and that the single
   `open()` in the module is read-mode (`"rb"`, in the bread hasher). `test_J8`
   proves the scanner detects a planted `np.save`.
4. **The summary carries no per-household datum.** `test_J9` asserts the key set
   is exactly the addendum §3 contract and that no value is a list longer than 37.
   `idhh_encoding`, `n_households` and `bytes_per_household` are mandated scalar
   contract fields, not identifiers — the length check is what proves the point.
5. **Nothing written outside `tmp_path`.** Every serializer test writes only to
   pytest's `tmp_path`. PROOF-11 confirms no Phase-5 artifact exists anywhere in
   the repository, and `git status` after the full suite shows only the two new
   source files.
6. **Increment-A files untouched.** `git status` for
   `p2a_phase5_score_stream.py`, `test_p2a_phase5_score_stream.py` and
   `conftest.py` is empty — the committed Increment-A state is unmodified.

---

## 9. Residual limitations

1. **No full-sample inferential result exists yet, by design.** Everything in §5
   from the meat onward is `subset-diagnostic`. The certified covariance,
   standard errors and the H0-A verdict require the 1,555-household dry run,
   which is Increment C's and only after review. **No regional inferential claim
   is made in this report.**
2. **The committed parameter map's `grad_free_negll` is a reduced-precision
   rendering** (13 significant digits; interior max `1.099259720618e-4` against
   the authoritative `1.0992597206183063e-4`, relative `~2.8e-13`). Immaterial
   against T-19/T-22 margins, but Increment C must read
   `phase4_diagnostics.json → gradient_free`, as this module does. Pinned by
   `test_G8`.
3. **`inference_grade` is an implementation safeguard, not a design gate.** It
   was added because a whole-sample bread paired with a subset meat is otherwise
   silently misreadable. It weakens nothing and alters no constant, but a
   reviewer should confirm they are content with a non-design field appearing on
   the covariance object and echoed by W-1/W-4/W-5.
4. **T-7's `rank(M) = 34` at `n = 64`** is arithmetic, not a defect (§5.4).
   Increment C should confirm rank 35 at the full sample, where design v4 §9.3
   expects generic full rank.
5. **`V_model` and `V_robust` are not force-symmetrised.** Design v4 mandates
   symmetrisation for `Hs` (T-6) and `M` (T-7) only, so adding a third would be
   respecifying. T-9 measures the residual asymmetry instead; observed `3.05e-16`
   and `1.99e-17`, far inside `1e-12` relative.
6. **Gates not implemented here, and why:** T-1/T-2/T-3/T-4/T-11/T-15/T-16/T-20
   are Increment-A score-layer gates, already covered; T-12/T-12S (fresh-process
   reproduction), T-13 (post-evaluation immutability), T-21 (absent from the
   register) and T-23/T-23S (custody/manifest completeness) require the runner
   and transaction, and are Increment C.
7. **W-2 and W-3 are reporting requirements**, not pass/fail gates; they return
   `passed=True` with their payloads, matching design v4 §13.5 and §15.
8. **Serialization is exercised but not orchestrated.** Which artifacts a real
   run writes, in what order, into which staging directory, with what manifest
   and hash map, is Increment C. This layer only guarantees each writer refuses
   non-aggregate content.

---

## 10. Immediate next action

1. **Independent Codex review B** of `scripts/p2a/p2a_phase5_inference.py` and
   `tests/p2a/test_p2a_phase5_inference.py` at MNL
   `92e299de6313bad0b0421c0db3dd268fdbcfdb59`, executing PROOF-1 … PROOF-12
   verbatim. Charter §6: `APPROVE`, `APPROVE AFTER FIXES` (one narrow
   remediation), or `REJECT` (E2 halt). **Increment C must not start before an
   approving verdict.**
2. **Two reviewer rulings requested:** (a) accept `inference_grade` as an
   implementation safeguard (§9.3); (b) confirm that Increment C reads the
   gradient from `phase4_diagnostics.json`, not the parameter-map CSV (§9.2).
3. **On approval**, commit the reviewed Increment-B state with both worktrees
   clean and update the JMP-M05C ledger, then authorize **Increment C** —
   dry-run-only runner, immutable aggregate-only attempt transaction, T-12S
   fresh-process reproduction over the fixed `(encoding, batch size, AD mode)`
   tuple, T-23S no-row-persistence gate, manifest and provenance including
   `jax_enable_x64`, peak memory and wall time, STOPPED behaviour, and no
   `complete/`.
4. **Carry forward** the §9 items, in particular that the first full-sample
   covariance and the H0-A verdict are produced for the first time in the
   Increment-C dry run and must be audited there, not assumed from §5.

**FINAL VERDICT: READY FOR REVIEW B**
