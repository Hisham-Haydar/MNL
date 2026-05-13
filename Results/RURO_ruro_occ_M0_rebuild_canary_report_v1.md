# RURO R reference Occ M0 — Rebuild Canary Report v1

Date: 2026-05-13 (revised after code-side fix)

**Purpose**: Run the smallest feasible canary on the current France 2016 MNL
parquet files to verify whether the M0_ruro_occ rebuild has effectively
landed before committing to the full data rebuild.

**Inputs inspected** (read-only, no modifications):

| File | Size | Last modified |
| --- | --- | --- |
| `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet` | 21,299,439 B | 2026-02-05 14:11:02 |
| `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet` | 42,433,564 B | 2026-02-05 14:11:01 |

Singles: 167,600 rows × 74 cols. Couples: 257,700 rows × 80 cols.

The canary script lives at `Results/_canary_ruro_occ_M0.py`; raw JSON at
`Results/_canary_ruro_occ_M0_results.json`.

---

## Headline

**Overall result: 7 of 9 checks FAIL.** The current parquets predate every
M0_ruro_occ code change. They were built on 2026-02-05 — before the MNL
prep changes that compute the frozen R reference aliases, and before any
`--occ-spec empirical` rebuild. **The full rebuild plan must be executed;
the canary cannot be "rescued" by a partial fix.**

What this means for the rebuild ladder:

- C0 (input file existence) — Step 0 of the rebuild plan still needs to be
  run before draws.
- C1/C2 (post-draw canaries) — N/A until draws are rebuilt.
- C3/C4 (post-MNL canaries) — exactly the failures reported below; they will
  flip to PASS only after Steps 1–3 complete.

---

## Per-check results

| # | Check | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `loc4` varies across working alternatives within household | **FAIL** | Singles median distinct `loc4` per `idhh` (over `working == 1`) = **1.0**; 99.58 % of households have a single occupation across all working alts; max is 2. Couples (working indicator falls back to `hours_{male,female} > 0`): median 1.0; 98.8 % (male) / 99.88 % (female) of households at distinct = 1. |
| 2 | Median distinct `loc4` per household ≥ 3 | **FAIL** | Same evidence; medians are 1.0 across singles, couples-male, couples-female. Target is ≥ 3. |
| 3 | `log_q_Occ` exists | **FAIL** | Singles: `log_q_Occ` missing. Couples: `log_q_Occ_male` and `log_q_Occ_female` both missing. *This is the immediate cause of the C7/C8/C9 failures below.* |
| 4 | `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` exist (singles); `_male`/`_female` analogues (couples) | **FAIL** | Singles missing: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`. Couples missing all 8 partner-suffixed aliases. `working_male`/`working_female` are also absent on this old file, but the canary now resolves that via the `hours > 0` fallback — see the working-indicator section below. |
| 5 | `prior > 0` | **PASS** | Singles min `prior` = 8.241758e-05 (no zeros, no NaNs). Couples min `prior` = 6.792658e-09 (no zeros, no NaNs). |
| 6 | `log_prior == log(prior)` | **PASS** | Max `\|log(prior) − log_prior\|` = 0.000000e+00 on both singles (n=167,600) and couples (n=257,700). The prior-density / log_prior storage convention is correct. |
| 7 | Singles: `log_prior == log_q_E + working*(log_q_H + log_q_W + log_q_Occ)` | **FAIL** | Cannot evaluate — all four `log_q_E/H/W/Occ` alias columns are absent. The MNL prep that creates them has not been run on this file. |
| 8 | Couples: `log_prior` decomposes as male + female components with `log_q_{E,H,W,Occ}_{male,female}` | **FAIL** | Cannot evaluate — all 8 per-partner alias columns are absent. Working indicators are no longer a blocker for this check (resolved via `hours > 0` fallback in the canary). |
| 9 | Non-work alternatives have occupation contribution gated off (`working == 0` ⇒ `log_q_Occ == 0`) | **FAIL** | Cannot evaluate the contribution magnitude because `log_q_Occ`/`log_q_Occ_male`/`log_q_Occ_female` are absent. Partial evidence: on non-work alts `loc4` is uniformly `-1` for singles (n=16,813), couples-male (n=26,053), and couples-female (n=25,693) — consistent with the draw convention — but the gating identity itself cannot be verified without the column. |

---

## What's actually in the file (forensics)

The current singles parquet still carries the **raw draw-layer log-q columns**
(`log_q_state`, `log_q_total`) instead of the frozen aliases. Couples has
neither the raw layer columns nor the aliases. The
implementation report explicitly forbids `log_q_state` and `log_q_total` in
the final keep set:

```text
singles raw/forbidden cols present: ['log_q_state', 'log_q_total']
couples raw/forbidden cols present: []
```

So:

- **Singles** is in an *intermediate* state: built when MNL prep wrote the
  raw `log_q_state` / `log_q_total` columns but did not yet drop them and
  did not yet alias `log_q_state → log_q_E`, `log_q_hours → log_q_H`, etc.
- **Couples** is in an *earlier* state: it doesn't even have the raw
  per-layer log-q columns — only `log_q_total_{male,female}`. It also uses
  the older `hours_{male,female} > 0` convention rather than the
  `working_{male,female}` indicator the spec expects.

Both files were produced before *any* of the ruro_occ MNL prep changes
described in `docs/RURO_ruro_occ_baseline_implementation_report_v1.md`.

---

## Couples working-indicator: a real code-side bug, now fixed

The current couples file uses `hours_{male,female}` (continuous) as the only
working indicator. The proposal-alias rebuild is expected to expose binary
`working_{male,female}` — that is what the M0 engine routing and the C8
reconstruction identity assume.

Investigation of `scripts/enhanced/enh_RURO_prep_mnl_basic.py` showed that
the per-gender working indicators **are** computed (lines 794–797):

```python
df[f"working_{gender}"]      = (hours > 0).astype(int)
df[f"working_pt1_{gender}"]  = ((hours >= 18.5) & (hours <= 21.5)).astype(int)
df[f"working_pt2_{gender}"]  = ((hours >= 29.5) & (hours <= 30.5)).astype(int)
df[f"working_ft_{gender}"]   = ((hours >= 37.5) & (hours <= 40.5)).astype(int)
```

…but `get_essential_columns_for_estimation()` only listed the singles names
(`working`, `working_pt1`, `working_pt2`, `working_ft`) — so the keep-set
filter at the end of MNL prep dropped all eight gendered variants. A clean
rebuild from this code would still ship a couples MNL file without
`working_male`/`working_female`, and C8 would fail.

**Fix applied** to `enh_RURO_prep_mnl_basic.py` keep set (labour-market
block, around line 1750):

```python
# Gendered working indicators (couples; engine routes male/female via these)
"working_male", "working_female",
"working_pt1_male", "working_pt1_female",
"working_pt2_male", "working_pt2_female",
"working_ft_male", "working_ft_female",
```

This is the only code-side change required to unblock the full rebuild.

## Canary script: hours fallback for couples

The original C8/C9 implementation hard-required `working_{male,female}` and
silently returned `null` in the JSON when they were absent (which is exactly
the case on the current couples file). The script now uses a
`_working_mask(df, work_col, hours_fallback)` helper that prefers
`working_{male,female}` if present, otherwise falls back to
`hours_{male,female} > 0`, and records the source it used:

```text
couples_male   [working source: hours_male > 0 (fallback)]:   n_hh=2,577  median=1.0
couples_female [working source: hours_female > 0 (fallback)]: n_hh=2,577  median=1.0
```

The couples medians now appear in `_canary_ruro_occ_M0_results.json`
together with a `"working_source"` field — so each value is self-describing
about which indicator it came from. This matters once `working_male`/
`working_female` are present after the rebuild: the same JSON will record
that the binary indicator was used.

---

## Why the canary cannot be "rescued" without the full rebuild

The user asked, "if a canary run is impossible without full rebuild, explain
why." The canary *itself* ran fine — but checks 1, 2, 3, 4, 7, 8, 9 all
depend on columns that the current MNL parquets simply do not contain.
Those columns are written by `enh_RURO_prep_mnl_basic.py` only when:

1. The draws file was produced with `--occ-spec empirical` (creates a
   meaningful `log_q_occ` per row), AND
2. The MNL prep step that creates the R reference aliases (`log_q_E`, `log_q_H`,
   `log_q_W`, `log_q_Occ`, with `_male`/`_female` for couples) and the
   `working_{male,female}` indicators has run.

Neither precondition holds on the 2026-02-05 files. There is no shortcut:
the columns must be created by Steps 1–3 of the rebuild plan. A partial
patch (e.g. computing aliases ad hoc from the singles file's `log_q_state`)
would synthesize check passes without rebuilding the underlying occupation
draws, and check 1/2 would still fail — so any such "rescue" would mask the
identification problem.

---

## Recommendation

**Order matters.** Do not start the rebuild before the keep-set fix above
is in place. With that committed, execute the rebuild plan as written in
`docs/RURO_ruro_occ_M0_rebuild_command_plan_v1.md`:

1. **Step 0** — confirm `loc4` exists in `singles_RURO_ready.parquet` and
   `couples_RURO_ready.parquet`. This is the only "free" pre-check; if
   `loc4` is missing the rebuild needs a pre-step regardless.
2. **Step 1** — `enh_RURO_draws.py --occ-spec empirical --occ-strata __all__`.
3. **C1 / C2** — post-draw canaries.
4. **Step 2** — EUROMOD on rebuilt draws.
5. **Step 2b** (optional) — `reduce_mnl_columns.py`.
6. **Step 3** — `enh_RURO_prep_mnl_basic.py` with `--drawsmeta`.
7. **Re-run this canary script** (`Results/_canary_ruro_occ_M0.py`). All
   9 checks should flip to PASS. If any of them remain FAIL, the rebuild's
   MNL prep step did not produce the expected columns and the implementation
   report's claims need to be re-checked against the running code.

The canary script and its JSON output should be archived alongside the
estimation results once the rebuild produces a clean run, so the
identification precondition is documented for the final spec.

---

## Files produced

| File | Purpose |
| --- | --- |
| `Results/_canary_ruro_occ_M0.py` | Reusable canary — re-run after the rebuild to confirm all 9 checks PASS |
| `Results/_canary_ruro_occ_M0_results.json` | Machine-readable check results for this run |
| `Results/RURO_ruro_occ_M0_rebuild_canary_report_v1.md` | This report |
