# RURO Stijn Occ M0 — Full Rebuild Report v1

Date: 2026-05-13 (rebuild complete — all 9 canary checks PASS)

## Status

**Full rebuild complete. All 9 post-MNL canary checks PASS.** The
France 2016 continuous MNL parquets are now in the `M0_stijn_occ` state
with occupation drawn from the pooled empirical distribution.

### Timeline of this session

1. Step 0 (read-only pre-flight): PASS — `loc4` present in both
   RURO-ready files with 5 distinct values among `lhw > 0` rows.
2. Step 1 first attempt: 30 s; sanity checks PASS but post-draw canary
   revealed a latent bug in `_sample_occ_vectorized_by_stratum` and
   `_log_q_occ_for_given_occ` (pooled `__all__` stratum fell through to
   fallback). EUROMOD held.
3. **Sampler patch** applied to `scripts/enhanced/enh_RURO_draws.py`.
4. Step 1 re-run: 25 s, C1 + C2 PASS (median distinct `loc4` per hh = 4.0
   for singles and both couples partners).
5. **Pre-Step 3 archive**: old `fr_2016_RURO_mnl__{singles,couples}.parquet`
   and `__mnlmeta.json` renamed with `__pre_stijn_occ_20260513` suffix.
6. Step 2 (EUROMOD): 2 minutes wall (much faster than the 30–90 min the
   plan budgeted — the underlying data is small).
7. Step 3 first attempt: crashed with `KeyError: 'h_min'` —
   `enh_RURO_prep_mnl_basic.py` reads drawsmeta keys from the top level,
   but `enh_RURO_draws.py` writes them under `distributional_params`.
8. **Drawsmeta-reader patch** applied to
   `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (accepts nested form,
   falls back to flat for older sidecars).
9. Step 3 re-run: 2m28s, sanity checks PASS, MNL parquets written.
10. Final canary (`Results/_canary_stijn_occ_M0.py`): **all 9 PASS**.

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

### Step 2 — EUROMOD (executed)

Command:

```powershell
& $PY scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "$RAW/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "$EM" `
  --scenario-dir "$SCEN"
```

Runtime: **2 minutes wall** (10:29:06 → 10:31). Far below the
30–90 min plan budget because the underlying FR_2016 microdata is small
(26,560 individuals → 10,873 RURO-ready deciders+non-deciders).

Output:

| File | Size | mtime |
| --- | --- | --- |
| `$SCEN/combined_draws_em.parquet` | 487,855,335 B (488 MB) | 2026-05-13 10:31 |
| `$SCEN/combined_draws_em__euromodmeta.json` | 381 B | 2026-05-13 10:31 |

Warnings:

- `[RURO_euromod] 375851 rows (34.6%) have ils_dispy=0` — consistent with
  non-working draws (~10 % π0 zero-employment mass per draw plus children
  / non-deciders propagated at draw=0). Not a problem.
- EUROMOD log line: `Simulation for system FR_2015 with dataset
  FR_training_data finished.` This dataset name is a **cosmetic label**
  from the EUROMOD public release's FR.xml `DataConfigs` block; the
  script supplies the actual microdata via `--microdata-template`, which
  resolves to `Z:/hisham/EUROMOD-STORAGE/Data/raw/FR_2016.txt` — verified
  as **real EU-SILC FR 2016 microdata** (26,560 individuals,
  11,459 households, IDs `1,483,000 – 93,789,900`), not the HHoT
  synthetic training data (which would be 2,397 hh / 7,482 individuals
  and is not present in `Data/raw/`).
- `DeprecationWarning: datetime.utcnow()` — upstream, harmless.

### Step 3 — MNL prep (executed after drawsmeta-reader patch)

**Pre-step archive (replacement behaviour, explicit):**

```bash
mv fr_2016_RURO_mnl__singles.parquet \
   fr_2016_RURO_mnl__singles__pre_stijn_occ_20260513.parquet
mv fr_2016_RURO_mnl__couples.parquet \
   fr_2016_RURO_mnl__couples__pre_stijn_occ_20260513.parquet
mv fr_2016_RURO_mnl__mnlmeta.json \
   fr_2016_RURO_mnl__mnlmeta__pre_stijn_occ_20260513.json
```

The old files (from 2026-02-05) are retained under
`__pre_stijn_occ_20260513` so they remain available for diff/inspection.

**First attempt failed** with `KeyError: 'h_min'` because the drawsmeta
reader expected flat keys but the writer puts them under
`distributional_params`. Patched the reader to accept the nested form
(falls back to flat for older sidecars).

**Command** (Step 3 retry):

```powershell
& $PY scripts/enhanced/enh_RURO_prep_mnl_basic.py `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "$SCEN/combined_draws_em.parquet" `
  --out-base "$DATA/fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --gsur-file "$GSUR" `
  --drawsmeta "$DATA/singles_RURO_ready_RURO_draws__drawsmeta.json"
```

**Runtime**: 2 m 28 s wall.

**Output**:

| File | Rows | Cols | Size | mtime |
| --- | --- | --- | --- | --- |
| `fr_2016_RURO_mnl__singles.parquet` | 167,600 | 75 | 21,500,551 B (20.5 MB) | 2026-05-13 10:38 |
| `fr_2016_RURO_mnl__couples.parquet` | 257,700 | 93 | 43,108,822 B (41.1 MB) | 2026-05-13 10:38 |
| `fr_2016_RURO_mnl__mnlmeta.json` | — | — | sidecar | 2026-05-13 10:38 |

**Household / group counts and alternatives per household**:

| File | Households | Alts / hh | Working alts | Non-working alts |
| --- | --- | --- | --- | --- |
| singles | 1,676 | 100 | 150,787 (89.97/hh) | 16,813 (10.03/hh) |
| couples | 2,577 | 100 | varies per partner | varies per partner |

For couples, the working filter is per partner: 231,647 rows with
`working_male = 1` (≈ 89.9 / hh) and 232,007 rows with
`working_female = 1` (≈ 90.0 / hh). Non-work counts: 26,053 (male) /
25,693 (female).

**Column-filter outcome**:

- singles: 962 → 75 cols (92.2 % reduction). All required Stijn aliases
  (`log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`) and `loc4` retained.
- couples: 1468 → 93 cols (93.7 % reduction). `working_{male,female}` and
  the four gendered Stijn aliases retained (per the earlier keep-set
  fix). M0-forbidden columns (`lindi`, `industry`, `nace`, `log_q_job`,
  `log_q_total`, `log_q_state`, `job_id`, `type_id`, `hours_bin`,
  `wage_bin`) confirmed absent — `raw/forbidden cols present: []` for
  both files in the canary.

**Sanity checks** (script-internal): all PASS.

- singles: consumption std = 8456.30, leisure std = 21.01, 1,676 hh × 100 draws.
- couples: consumption std = 8456.30, leisure std = 21.01, 2,577 hh × 100 draws.

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

## Final canary (C1–C9) on rebuilt MNL files

Ran `Results/_canary_stijn_occ_M0.py` on the new MNL parquets:

| # | Check | Status | Detail |
| --- | --- | --- | --- |
| 1 | `loc4` varies across working alts | **PASS** | singles median = 4.0 (max 5), couples-male 4.0 (max 5), couples-female 4.0 (max 5). Zero households with only 1 distinct `loc4`. |
| 2 | Median distinct `loc4` per hh ≥ 3 | **PASS** | all medians = 4.0. |
| 3 | `log_q_Occ` exists | **PASS** | singles + both couples partners. |
| 4 | All required Stijn alias columns exist | **PASS** | `log_q_{E,H,W,Occ}` (singles); `_male` / `_female` analogues (couples). No missing. |
| 5 | `prior > 0` | **PASS** | singles min = 7.819e-06, couples min = 6.290e-11; no zeros, no NaNs. |
| 6 | `log_prior == log(prior)` | **PASS** | max diff = 0.0 on both files (167,600 + 257,700 rows). |
| 7 | Singles `log_prior` reconstruction | **PASS** | max\|`log_prior − recon`\| = 0.0. |
| 8 | Couples `log_prior` reconstruction (male + female) | **PASS** | max\|`log_prior − recon`\| = 0.0 using `working_male` / `working_female`. |
| 9 | Non-work alts gate off `log_q_Occ` | **PASS** | singles 16,813 non-work rows: all `log_q_Occ = 0`, all `loc4 = -1`. Couples-male 26,053 non-work: all gated. Couples-female 25,693 non-work: all gated. |

Saved details: `Results/_canary_stijn_occ_M0_results.json`.

### `loc4 = -2` observed-row convention

`loc4 = -2` is an unknown-worker sentinel, not an occupation category. It is
present only on a small number of observed working alternatives (`draw = 0`):

| File / partner | Count |
| --- | ---: |
| Singles | 7 |
| Couples male | 31 |
| Couples female | 3 |

These rows are retained. Because M0 estimates only the occupation dummies for
`loc4 = 2`, `loc4 = 3`, and `loc4 = 4` with `loc4 = 1` omitted, `loc4 = -2`
sets all occupation dummies to zero and contributes zero to `O^Occ`. This is
numerically safe for estimation, but it should be described in methodology
text as unknown observed occupation, not as routine-manual work. Simulated
working alternatives contain valid `loc4` draws in `{1, 2, 3, 4}`.

---

## Summary

| Item | Value |
| --- | --- |
| Rebuild status | **Complete and green** |
| Total wall time (Step 1 + 2 + 3 + canary, including the two patch loops) | ~10 minutes |
| Net Step 1 + 2 + 3 runtime (final, clean) | 25 s + 2 min + 2 m 28 s ≈ **5 m** |
| Code patches landed today | 2 (sampler in `enh_RURO_draws.py`, drawsmeta reader in `enh_RURO_prep_mnl_basic.py`) |
| Code patch landed earlier today | gendered `working_{male,female}` indicators added to the MNL keep set (essential for C8 / C9 on couples) |
| Old MNL files | archived as `__pre_stijn_occ_20260513.*` |
| Draws files | regenerated (timestamp 10:24) |
| EUROMOD scenario file | newly created (`$SCEN/combined_draws_em.parquet`, 488 MB) |
| Final MNL singles | 167,600 rows × 75 cols, 1,676 hh × 100 alts |
| Final MNL couples | 257,700 rows × 93 cols, 2,577 hh × 100 alts |
| Canary | 9/9 PASS |

Estimation is **not** run per instruction.

---

## Files of record

| Artefact | Path |
| --- | --- |
| Draws (singles) | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet` |
| Draws (couples) | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet` |
| Drawsmeta sidecars | `..._RURO_draws__drawsmeta.json` (each) |
| EUROMOD output | `Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/scenarios/combined_draws_em.parquet` |
| MNL singles (new) | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet` |
| MNL couples (new) | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet` |
| MNL mnlmeta (new) | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__mnlmeta.json` |
| MNL singles (archived) | `..._RURO_mnl__singles__pre_stijn_occ_20260513.parquet` |
| MNL couples (archived) | `..._RURO_mnl__couples__pre_stijn_occ_20260513.parquet` |
| MNL mnlmeta (archived) | `..._RURO_mnl__mnlmeta__pre_stijn_occ_20260513.json` |
| Step 2 log | `Results/_step2_euromod.log` |
| Step 3 log | `Results/_step3_mnl_prep.log` |
| Canary script | `Results/_canary_stijn_occ_M0.py` |
| Canary JSON | `Results/_canary_stijn_occ_M0_results.json` |
| This report | `Results/RURO_stijn_occ_M0_full_rebuild_report_v1.md` |
