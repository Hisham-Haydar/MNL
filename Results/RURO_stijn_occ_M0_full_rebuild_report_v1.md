# RURO Stijn Occ M0 — Full Rebuild Report v1

Date: 2026-05-13 (Step 1 patched + re-run; Step 2 held for review)

## Status

**Step 1 (draws) complete and C1/C2 PASS.** Step 2 (EUROMOD) and Step 3
(MNL prep) are paused for user review per the chosen workflow ("Patch and
stop after Step 1 + C1/C2 for review").

### Timeline of this session

1. Step 0 (read-only pre-flight): PASS — `loc4` present in both
   RURO-ready files with 5 distinct values among `lhw > 0` rows.
2. Step 1 first attempt: ran in 30 s with no script-level errors, but
   the post-draw canary revealed a **latent bug** in
   `_sample_occ_vectorized_by_stratum` and `_log_q_occ_for_given_occ` —
   the empirical sampler silently fell through to the
   observed-occupation fallback under the pooled `--occ-strata __all__`
   path. Held EUROMOD per the plan's stop-condition.
3. **Patch applied** to both helpers in
   `scripts/enhanced/enh_RURO_draws.py`: replaced the buggy
   `pd.unique`/`np.where(stratum_keys == k)` pattern with an explicit
   Python-level dict group-by that is correct for object arrays of
   single-element tuples.
4. Step 1 re-run: 25 s, all sanity checks PASS.
5. C1 + C2 canaries on patched output: **PASS** (see numbers below).
6. **Stop here** for user review before touching EUROMOD.

The user's instruction was conditional: *"If the canary passed, run the full
France 2016 rebuild."* Per
`Results/RURO_stijn_occ_M0_rebuild_canary_report_v1.md` the canary headline
is **7 of 9 checks FAIL** on the current pre-rebuild parquet files. Those
failures are exactly the *expected* pre-rebuild state — they confirm the
rebuild is needed — but they do not constitute "the canary passed". The
literal reading of the conditional is therefore "do not run".

Independently of the conditional, the rebuild's blast radius warrants
explicit confirmation:

- **Step 1 (draws)** overwrites `singles_RURO_ready_RURO_draws.parquet` and
  `couples_RURO_ready_RURO_draws.parquet` in
  `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/`. These are shared with
  the existing continuous pipeline.
- **Step 2 (EUROMOD)** takes 30–90 minutes, requires `.NET CoreCLR` and the
  EUROMOD release at
  `Z:/hisham/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+`,
  and writes `combined_draws_em.parquet` into a new scenario directory.
- **Step 3 (MNL prep)** overwrites `fr_2016_RURO_mnl__singles.parquet` and
  `fr_2016_RURO_mnl__couples.parquet`. Any estimation reading these
  files will see the rebuilt occupation-varying data afterwards.

The system-level guidance is to confirm before destructive, long-running,
or shared-system-affecting actions. All three apply here.

---

## Post-patch canary numbers (the new green state)

C1 (post-draw occupation variation), run on the re-built draws:

| Source | Households | Median distinct `loc4` per hh (sim working) | Distribution of distinct counts |
| --- | --- | --- | --- |
| singles | 1,676 | **4.0** | `{4: 1676}` (all hh see all 4 task groups) |
| couples (per partner, `lhw > 0`) | 2,577 | **4.0** | `{4: 2577}` |

`log_q_occ` on simulated working draws is fully populated with negative
values consistent with empirical log-probabilities:

- Singles: 149,220 / 149,220 nonzero; range `[-2.355, -0.775]`, mean `-1.226`.
- Couples: 458,663 / 458,663 nonzero; range `[-2.341, -0.708]`, mean `-1.207`.

Sim-working `loc4` marginal vs the empirical pool used for sampling:

| `loc4` | Pool (singles working, draw=0) | Sim singles | Sim couples |
| --- | --- | --- | --- |
| 1 | 454 | 43,310 | 122,899 |
| 2 | 239 | 22,803 | 66,201 |
| 3 | 148 | 14,086 | 44,115 |
| 4 | 720 | 69,021 | 225,448 |

Empirical proportions (singles): 0.29 / 0.15 / 0.09 / 0.46 — matches pool
0.29 / 0.15 / 0.09 / 0.46 within RNG noise.

C2 (drawsmeta): `occ_spec=empirical`, `occ_strata=['__all__']`, `n_draws=99`,
seed=17 (singles) / 18 (couples).

---

## C1 failure (initial run, pre-patch) and root cause

After Step 1 completed, the post-draw canary reported:

```text
singles: loc4 present=True, log_q_occ present=True
  Median distinct loc4 per idhh_true in simulated working draws (lhw>0): 1.0
couples: loc4 present=True, log_q_occ present=True
  Median distinct loc4 per idhh_true in simulated working draws (lhw>0): 2.0
```

The plan's C1 pass criterion is median ≥ 2. **Singles fails; couples
"passes" but only because each couple has two deciders with different
observed `loc4`** — the sampler is still broken, the union just spans more
values per household.

### Forensics

In the simulated working draws of the singles file, the overall `loc4`
distribution matches the empirical pool perfectly (1: 40,406 — 2: 21,276 —
3: 13,196 — 4: 74,342, against pool sizes 454 / 239 / 148 / 720). But
within each household, all ~89 simulated working draws share **one**
`loc4` value, and that value matches the observed `loc4` in 92.66 % of
households. The remaining 7.34 % spill is consistent with the 7 mode-imputed
`loc4 = -2` deciders (forced to mode = 4) plus minor RNG-state effects from
unrelated `rng.choice` calls earlier in the same function. `log_q_occ` is
**0.0 across all 149,220 simulated working rows** — the proposal density
contribution that should accompany empirical sampling is entirely absent.

### Root cause

`scripts/enhanced/enh_RURO_draws.py:570` in
`_sample_occ_vectorized_by_stratum`:

```python
uniq = pd.unique(stratum_keys)
for k in uniq:
    key = tuple(k) if isinstance(k, (list, tuple, np.ndarray)) else (k,)
    idx = np.where(stratum_keys == k)[0]
```

When `--occ-strata __all__` is used, `strata_cols == ('__all__',)`, and the
synthetic `decider_df["__all__"] = 1` column makes every stratum tuple
`(1,)`. The variable `stratum_keys` becomes a 1-D object numpy array of 5+
thousand `(1,)` tuples.

NumPy's broadcasting rule treats `k = (1,)` as a length-1 sequence and
performs element-wise comparison: `arr[i] == 1` per element. Since each
`arr[i]` is the tuple `(1,)`, not the int `1`, the comparison returns
`False` everywhere. `idx` is empty, the loop body is skipped, `occ_out`
stays at `fallback_occ` (the observed occupation replicated across draws),
and `logq` stays zero.

Minimal reproducer:

```python
import numpy as np
arr = np.array([(1,)] * 5, dtype=object)
arr == (1,)
# -> array([False, False, False, False, False])
```

The same comparison pattern exists in `_log_q_occ_for_given_occ` at
`enh_RURO_draws.py:611`. Both helpers need the same fix.

### Fix applied

Both `_sample_occ_vectorized_by_stratum` and `_log_q_occ_for_given_occ` in
`scripts/enhanced/enh_RURO_draws.py` now use an explicit Python-level
group-by instead of `pd.unique` + `np.where(stratum_keys == k)`:

```python
groups: dict[tuple, list[int]] = {}
for i, sk in enumerate(stratum_keys):
    key_i = tuple(sk) if isinstance(sk, (list, tuple, np.ndarray)) else (sk,)
    groups.setdefault(key_i, []).append(i)

for key, idx_list in groups.items():
    idx = np.asarray(idx_list, dtype=np.int64)
    ...
```

This compares tuples with Python `==` semantics (not NumPy broadcasting),
so single-element tuples work correctly. Both helpers were otherwise
correct.

Inline comments cite the failure mode so future readers do not regress
this. The patched draws produced the green C1/C2 above.

---

## What was actually run

### Step 0 — pre-flight canary (read-only, ~3 s)

Single Python invocation against the RURO-ready inputs. No files modified.

```python
for name, path in [
    ("singles", r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet"),
    ("couples", r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet"),
]:
    df = pd.read_parquet(path)
    required = ["loc4", "dgn", "lhw", "yivwg"]
    missing = [c for c in required if c not in df.columns]
    working_mask = df["lhw"] > 0
    vc = df.loc[working_mask, "loc4"].value_counts().sort_index()
```

**Results**:

| File | Rows | `loc4` present? | `loc4` distribution among `lhw > 0` |
| --- | --- | --- | --- |
| `singles_RURO_ready.parquet` | 2,395 | yes | `{-2: 7, 1: 454, 2: 239, 3: 148, 4: 720}` |
| `couples_RURO_ready.parquet` | 8,478 | yes | `{-2: 34, 1: 1326, 2: 714, 3: 477, 4: 2442}` |

- All required columns present in both files (`loc4`, `dgn`, `lhw`, `yivwg`).
- 5 distinct `loc4` values are seen in the working subsample (the 4 task
  groups plus a `-2` "invalid" sentinel). The draws script handles `loc4 = -2`
  via mode imputation (see `enh_RURO_draws.py:1080-1088`) and samples only
  from `{1, 2, 3, 4}` for working draws.
- 5 distinct ≥ the required 3.

**Step 0: PASS.** The destructive rebuild is unblocked on the input-data
side.

---

### Step 1 — draws (first attempt; output was broken — superseded)

```powershell
& $PY scripts/enhanced/enh_RURO_draws.py `
  --singles-path "$DATA/singles_RURO_ready.parquet" `
  --couples-path "$DATA/couples_RURO_ready.parquet" `
  --n-draws 99 --wage-spec vw `
  --occ-spec empirical --occ-strata __all__ --occ-min-cell 30 `
  --h-min 5.0 --h-max 70.0 --w-min 2.0 --w-max 170.0 --rng-seed 17
```

**Runtime**: 30 s wall.

**Output written** (overwrote previous files):

| File | Rows | Decider rows | Non-decider rows |
| --- | --- | --- | --- |
| `singles_RURO_ready_RURO_draws.parquet` | 168,319 | 167,600 (1,676 × 100) | 719 |
| `couples_RURO_ready_RURO_draws.parquet` | 518,724 | 515,400 (5,154 × 100) | 3,324 |

Plus drawsmeta sidecars confirming `occ_spec=empirical`, `occ_strata=['__all__']`,
`n_draws=99`, seed=17 (singles) / 18 (couples).

**Warnings emitted**:

- `lhw_base differs from canonical hours in 38 rows` (singles) — script
  canonicalised `lhw_base` to current `hours`. Raw preserved in
  `lhw_base_raw`. Informational, not a problem.
- `lhw_base differs from canonical hours in 116 rows` (couples) — same.
- `FutureWarning` on `Groupby` level parameter, `DeprecationWarning` on
  `datetime.utcnow()` — both upstream, neither affects correctness.

**Sanity checks reported by the script itself**: all PASS (column presence,
draw-grid completeness, baseline compliance, hours/wage non-negative).

But the post-script C1 canary revealed the empirical sampler did not
actually run — see the C1 failure section above. The output of this first
attempt was overwritten by the post-patch re-run.

### Step 1 — draws (patched, final)

Same command as the first attempt, after patching both helpers in
`enh_RURO_draws.py`. Runtime: 25 s wall.

**Output written** (overwrote the first attempt):

| File | Rows | Decider rows | Non-decider rows |
| --- | --- | --- | --- |
| `singles_RURO_ready_RURO_draws.parquet` | 168,319 | 167,600 (1,676 × 100) | 719 |
| `couples_RURO_ready_RURO_draws.parquet` | 518,724 | 515,400 (5,154 × 100) | 3,324 |
| `singles_..._drawsmeta.json` | sidecar | — | — |
| `couples_..._drawsmeta.json` | sidecar | — | — |

Sanity checks: all PASS. C1 + C2 canaries: **PASS** (see numbers table at
the top of this report).

### Step 2 — EUROMOD (NOT executed; paused for review)

Held pending the fix.

### Step 3 — MNL prep (NOT executed; paused for review)

---

## Commands queued (not yet executed)

These are the exact commands from
`docs/RURO_stijn_occ_M0_rebuild_command_plan_v1.md` that will fire on
authorisation.

### Notation

```powershell
$PY        = "U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe"
$DATA      = "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016"
$EM        = "Z:/hisham/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+"
$RAW       = "Z:/hisham/EUROMOD-STORAGE/Data/raw"
$SCEN      = "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/scenarios"
$GSUR      = "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"
$PROJ      = "U:/Desktop/Nizam_Hisham/MNL"
```

### Optional backup of current draws

```powershell
Rename-Item "$DATA/singles_RURO_ready_RURO_draws.parquet" `
            "$DATA/singles_RURO_ready_RURO_draws__pre_stijn_occ.parquet"
Rename-Item "$DATA/couples_RURO_ready_RURO_draws.parquet" `
            "$DATA/couples_RURO_ready_RURO_draws__pre_stijn_occ.parquet"
```

### Step 1 — draws

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_draws.py" `
  --singles-path "$DATA/singles_RURO_ready.parquet" `
  --couples-path "$DATA/couples_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw `
  --occ-spec empirical `
  --occ-strata __all__ `
  --occ-min-cell 30 `
  --h-min 5.0 `
  --h-max 70.0 `
  --w-min 2.0 `
  --w-max 170.0 `
  --rng-seed 17
```

### Step 2 — EUROMOD

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_euromod.py" `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "$RAW/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "$EM" `
  --scenario-dir "$SCEN"
```

### Step 3 — MNL prep

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_prep_mnl_basic.py" `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "$SCEN/combined_draws_em.parquet" `
  --out-base "$DATA/fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --gsur-file "$GSUR" `
  --drawsmeta "$DATA/singles_RURO_ready_RURO_draws__drawsmeta.json"
```

### Post-rebuild verification

```powershell
& $PY "$PROJ/Results/_canary_stijn_occ_M0.py"
```

Expected: all 9 checks PASS (currently 7 FAIL on the old files).

---

## Expected output files (not yet created)

| Step | File | Location |
| --- | --- | --- |
| 1 | `singles_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| 1 | `singles_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |
| 1 | `couples_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| 1 | `couples_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |
| 2 | `combined_draws_em.parquet` | `$SCEN/` |
| 3 | `fr_2016_RURO_mnl__singles.parquet` | `$DATA/` |
| 3 | `fr_2016_RURO_mnl__couples.parquet` | `$DATA/` |

---

## Expected row counts (predicted from Step 0)

Based on the RURO-ready row counts and `--n-draws 99`:

| File | Predicted rows | Predicted households |
| --- | --- | --- |
| singles draws (deciders only) | n_decider_s × 100 alts | ~1,676 (matches current canary; previously observed) |
| couples draws (deciders only) | n_decider_c × 100 alts | ~2,577 |
| MNL singles | n_s × 100 alternatives per hh | ~1,676 × 100 = 167,600 |
| MNL couples | n_c × 100 alternatives per hh | ~2,577 × 100 = 257,700 |

These predictions match the current pre-rebuild file sizes
(167,600 and 257,700 rows), since the `--n-draws 99` produces 100
alternatives per household (1 observed + 99 simulated) and household count
does not change.

---

## Runtime budget

| Step | Estimated wall time |
| --- | --- |
| Step 1 — draws | 5–15 min |
| C1/C2 — post-draw canaries | <1 min |
| Step 2 — EUROMOD | **30–90 min** |
| Step 3 — MNL prep | 10–20 min |
| C3/C4 — post-MNL canaries | <1 min |
| **Total** | **~45 min to ~2 hours** |

---

## Warnings to expect

- The draws script may warn about `loc4 = -2` rows being imputed to the
  pool mode (7 singles, 34 couples observed).
- The MNL prep may log a warning if any forbidden columns
  (`lindi`/`industry`/`nace`/`log_q_job`/`log_q_total`/`log_q_state`/...)
  are present in the EUROMOD output before filtering — by design, these
  are dropped by the keep set fixed in
  `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (rev 2026-05-13 keep-set
  patch that also added the gendered `working_{male,female}` indicators).
- EUROMOD .NET runtime warnings on stderr are normal; they do not indicate
  failure unless the script exits non-zero.

---

## Decision needed (now)

Step 1 is green. EUROMOD is the next step and the long one (30–90 min) and
overwrites no files outside `$SCEN`. Choose one:

1. **Proceed with Step 2 (EUROMOD) → Step 3 (MNL prep) → C3 + C4 canaries.**
   The estimated tail is ~45 min – 2 h. I'll report row counts, runtimes,
   warnings, and the canary outcome by overwriting this report.
2. **Hold.** Leave the patched draws in place; do not touch EUROMOD or MNL
   prep. The pre-rebuild MNL parquets remain in place (unchanged by today)
   and are still incompatible with the M0 spec.

---

## What this report does NOT yet contain

Until execution is authorised, the following sections will remain
placeholders:

- Actual commands run (with timestamps)
- Actual output file sizes and mtimes
- Actual row counts per file
- Actual households / groups
- Alternatives per household (final)
- Actual runtimes (per step and total)
- Warnings emitted (verbatim, with provenance)
- Final rebuild success / failure status
- Post-rebuild canary result (all 9 checks)

These will be filled in by overwriting this report after Step 3 completes.
