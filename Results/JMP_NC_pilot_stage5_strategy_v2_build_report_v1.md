# JMP NC Pilot — Stage 5 v2 (Strategy C′) Build Report v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: pilot build report. Records execution of NC pilot
Stage 5 v2 (EUROMOD under Strategy C′ — blockwise joint-product
EUROMOD with both partners deciders in every block) per
`docs/JMP_NC_pilot_stage5_strategy_amendment_v2.md`. **All 30 blocks
completed; no halt fired; HE7 stayed quiet on every block.** The
post-EUROMOD merge, GSUR, precompute, estimation, welfare, SA2, and
promotion are NOT run in this slice. M1-clean 2016 remains the active
baseline. Corrected pooled P3a track unaffected.

---

## 1. Stage 5 v2 verdict

**PASSED.** All 30 blocks (`f = 0..29`) executed under Strategy C′
(both partners deciders, scalar runner draw = male marginal
`m ∈ {0..29}`, female draw `f` block constant). HE7 (the
`yem = yem00 + yemxp` identity assertion that halted v1's Strategy B)
stayed quiet on every block (max identity diff = 0.0 across all three
sampled blocks). The runner reached `system.run` on every block and
produced a `combined_draws_em.parquet` (≈90 MB, 254,340 rows, 343
columns) plus `__euromodmeta.json` sidecar plus `run.log`.

The joint product coverage is complete: 30 blocks × 30 m-values
covers all 30 × 30 = 900 `(m, f)` joint cells per couple. The pilot
wide product parquet (2,319,300 rows; `draw_male`/`draw_female`/
`draw_joint`/`is_chosen_joint`) and the singles production parquet
(500,700 rows) are both untouched. No production script was edited
in place.

The next gate is the **separate post-EUROMOD merge slice** (NOT this
slice) that joins the 30 per-block EUROMOD outputs back onto the
pilot wide product parquet by `(idperson_male, draw_male=m)` and
`(idperson_female, draw_female=f)` per block, populates
`ils_dispy_male`/`ils_dispy_female`, adds `is_chosen = is_chosen_joint`,
and sorts each (idhh, year_tag) group so `draw_joint == 0` is first
(per the v1 re-pointing audit). That slice is unauthorized here.

---

## 2. Authorization scope

Stage 5 v2 (EUROMOD) only, per
`docs/JMP_NC_pilot_stage5_strategy_amendment_v2.md` (Strategy C′
supersedes Strategy B of amendment v1, which halted at HE7). Pilot
paths only. Block `f = 0` first as a checkpoint; full 30-block sweep
authorized only after f = 0 passed all §16 validations. None of the
not-authorized actions (post-EUROMOD merge / GSUR / precompute /
estimation / welfare / SA2 / promotion / M1-clean displacement /
production-script in-place edits) was performed.

---

## 3. Python environment

| Property | Value |
|---|---|
| Python executable | `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe` |
| Python version | `3.12.2` |
| `PYTHONNET_RUNTIME` | `coreclr` (set on the runner subprocess; also set internally by `enh_RURO_euromod.py:67` via `os.environ.setdefault`) |
| `PYTHONUNBUFFERED` | `1` |
| Pre-launch `import euromod` check | **PASSED** — `python -c "import os; os.environ.setdefault('PYTHONNET_RUNTIME','coreclr'); import euromod"` returned `euromod OK`, exit 0. |

HE-EM-PKG: **NOT FIRED.**

---

## 4. Strategy C′ recap and v1 HE7 halt

Amendment v1 (Strategy B) halted at the runner's
`yem = yem00 + yemxp` identity assertion (line 778 of
`scripts/enhanced/enh_RURO_euromod.py`) on the male pass. Root cause:
the off-axis partner (female) was treated as a non-decider; the
runner does NOT recompute non-decider earnings; the FR_2016 template's
non-decider `yem`/`yem00`/`yemxp` triples don't satisfy the identity
to 1e-6 for ~752 female-partner records; replicated across 30 draws
this surfaced 22,560 assertion-violating rows.

Strategy C′ (v2) treats **both** partners as deciders in every block.
Within block `f`, the female partner is held at her draw-`f` job
(hours/wage/loc4/yem from draw f) but presented as `is_decider=1`,
so the runner's lines 738–760 recompute her `yem00`/`yemxp`/`yem` from
final `lhw × yivwg` just as it does for the male partner. The
identity then holds by construction on every row. The male partner
varies over the runner's scalar `draw = m ∈ {0..29}`. Children remain
non-deciders at their production baseline values (whose template
triple does satisfy the identity, per the v1 verification).

Block coverage: 30 blocks × (male m ∈ {0..29}) = 900 joint cells per
couple. `draw_joint = 30·m + f` is reconstructed only by the later
merge slice; it is not present on any Stage 5 v2 artifact.

---

## 5. Adapter built / modified

**New module:** `scripts/pilot/export_pilot_euromod_inputs_v2.py`
(pilot-only; ~250 lines; production scripts NOT modified). The v1
adapter `scripts/pilot/export_pilot_euromod_inputs.py` is left
intact as historical reference.

Per-block construction (per amendment §15):

- Source baseline: production FR_2016 couples draws file
  (`U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet`)
  at `draw=0` (8,478 baseline rows: 5,154 RURO deciders +
  3,324 non-decider children).
- Source per-partner job values: pilot wide product parquet
  (`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`),
  one slice per partner with 77,310 rows (= 2,577 couples × 30
  marginal draws).
- For block `f`:
  - **Male decider rows:** 5,154 × 30 / 2 = 77,310 rows (2,577 male
    deciders × 30 m-draws); each row has draw-`m` hours/wage/loc4/yem;
    `is_decider = 1`.
  - **Female decider rows:** 77,310 rows (2,577 female deciders ×
    30 m-draws); each row has the SAME draw-`f` hours/wage/loc4/yem
    (block constant) replicated across all m; `is_decider = 1`.
  - **Non-decider rows:** 3,324 children at `draw = 0`,
    `is_decider = 0`; the runner replicates them across all 30
    draws by its existing non-decider logic.
  - **Stray `ils_*` columns dropped:** `ils_earns`, `ils_origy`,
    `ils_pen`, `ils_sicdy` (4 of the 5 named; `ils_earns_real` is
    absent from the production baseline). Confirmed dropped in
    every block.
  - **`block_f` column** added on every row (= the block constant)
    for later (m, f) reconstruction.

Per-block totals: **157,944 input rows** (154,620 decider +
3,324 non-decider). Output parquet ≈ 11.1 MB; sidecar carries
`id_multiplier = 1000`, `n_draws = 30`, `max_draw = 29`,
`household_type = "couples"`, `strategy = "C_prime_blockwise_joint_product"`,
`both_partners_deciders = true`, `block_f = f`.

---

## 6. Exact EUROMOD command (one per block)

For each block f ∈ {0..29}:

```powershell
$env:PYTHONNET_RUNTIME = "coreclr"; $env:PYTHONUNBUFFERED = "1"
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
  "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\block_f{FF}\fr_pilot_2016_couples_block_f{FF}_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\block_f{FF}"
```

with `{FF}` = `00`, `01`, …, `29`. stdout/stderr redirected to
`Data/pilot/nc_2016_couples/em_outputs/block_f{FF}/run.log` per block.

A small driver `scripts/pilot/run_pilot_em_blocks.py --lo 1 --hi 29`
ran blocks 1..29 sequentially after block f=0 passed its checkpoint
validations.

---

## 7. Block f = 0 checkpoint result

| Check | Result |
|---|---|
| Input rows | 157,944 (154,620 decider + 3,324 non-decider) |
| Decider `draw` range | 0..29 (30 distinct values, both partners) |
| `is_decider == 1` on both partners | True (77,310 male deciders + 77,310 female deciders = 154,620) |
| Stray `ils_*` columns absent | True (4 dropped) |
| Drawsmeta `id_multiplier == 1000` | True |
| Runner reached `system.run` | **YES** — output written |
| HE7 (`yem = yem00 + yemxp`) | **NOT FIRED** — max identity diff = 0.0 |
| Output `combined_draws_em.parquet` | Present (90,540,912 bytes) |
| Output rows | 254,340 (154,620 decider + ≈99,720 replicated non-decider) |
| Output cols | 343 (full production EUROMOD schema) |
| `ils_dispy` populated on decider rows | 154,620/154,620 not-NaN; 153,233 > 0; 970 = 0 |
| Within-couple `ils_dispy` std across m (decider rows) | mean 947 EUR; min 366; median 900; max 4,610 |
| Block elapsed (incl. EUROMOD `system.run`) | ≈5 min |

**Checkpoint PASSED → full 30-block sweep authorized.**

---

## 8. Full 30-block sweep — block-by-block outcomes

All 30 blocks produced a `combined_draws_em.parquet` (~90 MB,
254,340 rows, 343 cols) and `combined_draws_em__euromodmeta.json`
sidecar. Driver exit 0; sweep summary at
`Data/pilot/nc_2016_couples/em_outputs/sweep_summary_f01_to_f29.json`.

Per-block status (wall = adapter + runner):

| f | Output bytes | Runner secs | Wall secs | Status |
|---|---|---|---|---|
| 00 | 90,540,912 | ≈290 (initial coreclr load) | ≈5 min | OK (checkpoint) |
| 01 | 90,184,615 | 86.2 | 97.1 | OK |
| 02 | 90,199,253 | 87.8 | 97.1 | OK |
| 03 | 90,206,325 | 92.5 | 101.3 | OK |
| 04 | 90,224,835 | 92.2 | 101.1 | OK |
| 05 | 90,209,471 | (≈92) | 101.5 | OK |
| 06 | 90,301,338 | (≈92) | ≈100 | OK |
| 07 | 90,216,580 | (≈92) | ≈100 | OK |
| 08 | 90,275,688 | (≈92) | ≈100 | OK |
| 09 | 90,154,063 | (≈92) | ≈100 | OK |
| 10 | 90,240,656 | (≈92) | ≈100 | OK |
| 11 | 90,247,305 | (≈92) | ≈100 | OK |
| 12 | 90,286,826 | (≈92) | ≈100 | OK |
| 13 | 90,209,767 | (≈92) | ≈100 | OK |
| 14 | 90,219,566 | (≈92) | ≈100 | OK |
| 15 | 90,285,133 | (≈92) | ≈100 | OK |
| 16 | 90,218,849 | (≈92) | ≈100 | OK |
| 17 | 90,150,465 | (≈92) | ≈100 | OK |
| 18 | 90,235,048 | (≈92) | ≈100 | OK |
| 19 | 90,163,871 | (≈92) | ≈100 | OK |
| 20 | 90,284,416 | (≈92) | ≈100 | OK |
| 21 | 90,319,470 | (≈92) | ≈100 | OK |
| 22 | 90,253,722 | (≈92) | ≈100 | OK |
| 23 | 90,209,693 | (≈92) | ≈100 | OK |
| 24 | 90,243,756 | (≈92) | ≈100 | OK |
| 25 | 90,151,270 | 90.7 | (≈99) | OK |
| 26 | 90,209,103 | 87.9 | (≈97) | OK |
| 27 | 90,222,002 | 85.7 | (≈95) | OK |
| 28 | 90,288,909 | 92.1 | (≈101) | OK |
| 29 | 90,215,528 | 82.8 | (≈92) | OK |

**Totals:** 30 blocks; **2,707,168,435 bytes** combined (≈2.5 GB);
**7,630,200 output rows** (30 × 254,340); 30 sidecars; 30 logs.

**Sweep wall time:** blocks 1..29 = **2,852 s ≈ 47.5 min** (per
driver summary JSON). Block 0 (initial; included coreclr+EUROMOD
warmup) ≈ 5 min. **Total Stage 5 v2 EUROMOD time ≈ 52 min.**

---

## 9. Output paths

Inputs (one tree per block):
```
Data/pilot/nc_2016_couples/em_inputs/block_f{00..29}/
  fr_pilot_2016_couples_block_f{FF}_draws.parquet
  fr_pilot_2016_couples_block_f{FF}_draws__drawsmeta.json
```

Outputs (one tree per block):
```
Data/pilot/nc_2016_couples/em_outputs/block_f{00..29}/
  combined_draws_em.parquet              (~90 MB; 254,340 rows; 343 cols)
  combined_draws_em__euromodmeta.json    (id_multiplier=1000, n_draws=30)
  run.log
```

Driver summary + log:
```
Data/pilot/nc_2016_couples/em_outputs/sweep_summary_f01_to_f29.json
Data/pilot/nc_2016_couples/em_outputs/blocks_1_29_driver.log
```

Pilot adapter + driver code:
```
scripts/pilot/export_pilot_euromod_inputs_v2.py
scripts/pilot/run_pilot_em_blocks.py
```

---

## 10. Row counts (before / after each EUROMOD block)

| Quantity | Before EUROMOD (adapter input, per block) | After EUROMOD (runner output, per block) |
|---|---|---|
| Total rows | 157,944 | 254,340 |
| Decider rows | 154,620 (2,577 couples × 30 m × 2 partners) | 154,620 |
| Non-decider rows (children) | 3,324 (at draw=0) | 99,720 (= 3,324 × 30 replicated) |
| `draw` range | 0..29 (deciders); 0 (non-deciders) | 0..29 (deciders + replicated non-deciders) |
| `block_f` (input) | constant = f | (column not preserved in EM output; carried in sidecar instead) |

The runner's non-decider replication produced 99,720 child rows
(3,324 × 30) from a single baseline row per child. Decider counts
match exactly the adapter input. The block constant `f` is captured
in the per-block `__drawsmeta.json` and `__euromodmeta.json` sidecars;
the runner does not propagate the adapter's `block_f` column into
the EUROMOD output (the merge slice will recover it from the
sidecars).

---

## 11. HE7 status across all blocks

The `yem = yem00 + yemxp` deterministic identity was sampled on
blocks 0, 14, and 29 (representative of the start, middle, and end
of the sweep):

| Block | `yem` identity max abs diff |
|---|---|
| f=0 | 0.000000 |
| f=14 | 0.000000 |
| f=29 | 0.000000 |

**HE7: NOT FIRED on any block.** The both-deciders construction
clears the assertion by construction across the sweep, exactly as
predicted by the amendment.

---

## 12. `ils_dispy` population summary

Per block (sampled): all 254,340 rows have non-NaN `ils_dispy`. The
positive-income rate is ≈63% per block:

| Block | rows | `ils_dispy` notna | `ils_dispy` > 0 | median (EUR/month) |
|---|---|---|---|---|
| f=0 | 254,340 | 254,340 | 158,873 | 1,025 |
| f=14 | 254,340 | 254,340 | 158,688 | 774 |
| f=29 | 254,340 | 254,340 | 158,887 | 787 |

Non-positive `ils_dispy` reflects (a) non-working hypothetical
alternatives for children (≈100k replicated rows per block) and
(b) tax-credit/clawback rows where decider net household income
is slightly negative or zero (~6% of decider rows). Within-couple
`ils_dispy` varies across `m` per the block-0 sample (mean std ≈ 947
EUR/month), confirming EUROMOD recomputed disposable income for
every joint cell rather than returning a constant.

The runner emitted one informational warning per block:
"[RURO_euromod] 95050 rows (37.4%) have ils_dispy=0. This is
unusually high and may indicate issues." This warning is at the
default 1e-6 zero-detection threshold and is dominated by replicated
non-decider children with no household-level income flowing to them.
It is informational, not a halt; under Strategy C′ the decider-side
`ils_dispy` is the merge-slice target.

---

## 13. Slice-level validations

| Validation | Result |
|---|---|
| Pilot wide product parquet rows | **2,319,300** (unchanged; expected 2,319,300) |
| Pilot wide parquet `draw_male`/`draw_female`/`draw_joint`/`is_chosen_joint` | All present (unchanged) |
| Singles production parquet rows | **500,700** (unchanged; HE5) |
| 30 per-block `combined_draws_em.parquet` present | True |
| 30 per-block `__euromodmeta.json` sidecars present | True |
| 30 per-block `run.log` present | True |
| (m, f) coverage union across 30 blocks | {0..29} × {0..29} = 900 joint cells per couple |
| `id_multiplier == 1000` across all 30 sidecars | True (uniform) |
| `n_draws == 30` across all 30 sidecars | True (uniform) |
| HE7 (sampled blocks) | 0.0 max identity diff (clear) |

All slice-level validations pass.

---

## 14. Halt-condition status

| Halt | Condition | Status |
|---|---|---|
| **HE1** | In-place edit to production scripts | **NOT FIRED** (only new files under `scripts/pilot/` and `Data/pilot/`). |
| **HE2** | Scalar `draw` aliased to `draw_joint` | **NOT FIRED** (scalar `draw` = male marginal `m ∈ {0..29}`). |
| **HE4** | `id_multiplier ≠ 1000` or inconsistent sidecars | **NOT FIRED** (1000 uniform across 30 sidecars). |
| **HE5** | Singles parquet or wide product parquet altered | **NOT FIRED** (read-only access; both unchanged). |
| **HE6** | Welfare / SA2 / promotion / M1-clean displacement / out-of-scope | **NOT FIRED**. |
| **HE7** | `yem = yem00 + yemxp` raised | **NOT FIRED** on any block (max diff 0.0 sampled). |
| **HE-DEC** | `is_decider` not explicitly 1 on both partners | **NOT FIRED** (154,620 decider rows per block, half male, half female). |
| **HE-DRAWSMETA** | Missing / inconsistent drawsmeta | **NOT FIRED**. |
| **HE-EM-PKG** | `import euromod` failed | **NOT FIRED** with `PYTHONNET_RUNTIME=coreclr`. |
| **HE-BLOCK** | Full sweep begun before f=0 passed | **NOT FIRED** (f=0 passed checkpoint before f=1..29 launched). |
| **HE-STAGE** | Post-Stage-5 actions attempted | **NOT FIRED** (merge / GSUR / precompute / estimation / welfare / SA2 / promotion all NOT performed). |

**No halt fired.**

---

## 15. (m, f) coverage union

Per amendment §16 slice-level check: the union of the 30 blocks'
`(m, f)` pairs must be exactly `{0..29} × {0..29}`.

- Each block `f` covers `m ∈ {0..29}` on decider rows (verified
  empirically on blocks 0, 15, 29).
- Block sidecars carry `block_f = f` uniquely for f = 0..29.
- Coverage union: 30 × 30 = 900 distinct `(m, f)` pairs per couple.
- Per couple, decider rows yield 900 joint alternatives — matching
  the pilot product's 900 alternatives per couple.

Coverage is complete.

---

## 16. Promotion-debt

- **Block count = 30** is the chosen sweep direction (fix female,
  vary male). Equivalent direction (fix male, vary female) is also
  valid; the choice is conventional and would parameterize trivially.
- **`EXPECTED_COUPLES = 2577`** hard-coded in the v2 adapter
  (carried forward from v1).
- **`N_MALE_DRAWS = 30`** hard-coded (the marginal draw count;
  parameterizes for 20×20 or 40×40 consistency builds later).
- **`ID_MULTIPLIER = 1000`** explicitly set; matches the runner's
  floor for `max_draw < 1000`.
- The "fix-female-vary-male" convention is encoded in the adapter
  (`build_block_input` keys on `draw_male` as the scalar runner
  `draw` and on `draw_female == f` for the block constant). The
  reverse direction would require a symmetric adapter pass.
- Stray `ils_*` drop list (`ils_earns`, `ils_origy`, `ils_pen`,
  `ils_sicdy`, `ils_earns_real`) hard-coded from the v1 audit.
- The `__fragment_index`/`__batch_index`/`__last_in_fragment`/
  `__filename` parquet-side metadata columns appear in the EUROMOD
  output (pyarrow dataset artefacts); the merge slice may or may
  not want them. Flagged.

---

## 17. What was not executed

- **Post-EUROMOD merge** to the pilot wide product parquet (joining
  per-block decider `ils_dispy` onto `(idperson_male, draw_male = m)`
  and `(idperson_female, draw_female = f)` per block to populate
  `ils_dispy_male`/`ils_dispy_female` for all 2,319,300 wide rows):
  **NOT performed.** This is the next slice; it requires its own
  authorization document.
- **`draw_joint` reconstruction into the wide parquet:** NOT
  performed.
- **`is_chosen = is_chosen_joint` aliasing:** NOT performed.
- **Chosen-first sorting of the wide parquet:** NOT performed.
- **GSUR re-merge:** NOT performed.
- **Precompute / estimation / welfare / SA2 / canonical promotion /
  M1-clean displacement:** NOT performed.
- **Production scripts:** `scripts/enhanced/enh_RURO_euromod.py`,
  `scripts/enhanced/enh_RURO_draws.py`,
  `scripts/enhanced/enh_RURO_prep_mnl_basic.py`,
  `scripts/maintenance/prepare_pooled_estimation_ready.py`, and the
  frozen P3a YAML — all read-only; NOT modified.
- **Optional B′ smoke test (amendment §18):** Not performed.
  Block f=0 served as the equivalent checkpoint (HE7 + reach
  `system.run` + populated `ils_dispy`) at full scale.
- **Singles production parquet, frozen P3a artifacts, corrected
  pooled P3a outputs:** untouched.
- Two transient temp scripts under `%LOCALAPPDATA%\Temp`
  (`validate_block_f00.py`, `slice_validate.py`) were created for
  read-only validations and deleted after use.

---

## 18. Next gate

**Post-EUROMOD merge slice.** A separate authorization document
(suggested: `docs/JMP_NC_pilot_post_em_merge_amendment_v1.md`)
should pin:

1. The merge keys: `(idperson_male, draw_male = m, block_f = f)` →
   `ils_dispy_male`; `(idperson_female, draw_female = f)` →
   `ils_dispy_female`. The latter is constant within a block; the
   former varies with `m`.
2. The reconstruction of `draw_joint = 30·m + f` on the merged wide
   parquet.
3. The synthetic `is_chosen = is_chosen_joint` aliasing.
4. The chosen-first sort within each (idhh, year_tag) group so
   `draw_joint == 0` is the first row (the
   `estimation_engine.py:380` position-0 invariant from the
   re-pointing audit).
5. The HE3 wide-completeness check (no NaN/zero `ils_dispy_male`
   and `ils_dispy_female` across the 2,319,300 wide rows).
6. The `idperson_true` lookup back from the EUROMOD output's
   `id_multiplier`-encoded `idperson` to the original ID, for the
   merge to be unambiguous.

That document, plus a build report after the merge runs, are the
next two artefacts. The Stage 5 v2 deliverables (30 per-block
EUROMOD outputs + sidecars + logs) are the merge's inputs.

The post-merge agenda (precompute / estimation / etc.) remains
gated on the merge slice's success.

---

## 19. Required final statements

- **Stage 5 v2 PASSED.** All 30 blocks executed under Strategy C′;
  no halt fired; HE7 stayed quiet on every sampled block; 30
  `combined_draws_em.parquet` outputs (≈2.5 GB total) and 30
  metadata sidecars and 30 run logs written under pilot paths.
- **The post-EUROMOD merge was NOT run** and is not authorized in
  this slice.
- **No GSUR merge, precompute, estimation, welfare, SA2, or
  promotion** occurred in this session.
- **No production script was edited in place.**
- **M1-clean 2016 remains the active baseline.**
- **The corrected pooled P3a track is unaffected** and continues
  on its frozen 100-diagonal, unconditional-wage spec.
- **Stage 5 v2 only.** The merge slice is the next gate, under a
  separate authorization document.

---

*Status: NC pilot Stage 5 v2 build report v1, produced 2026-05-22.
Authorization: `docs/JMP_NC_pilot_stage5_strategy_amendment_v2.md`.
All 30 blocks PASSED; HE7 stayed quiet; M1-clean 2016 active; frozen
pooled P3a spec and post-estimation track unaffected; merge slice
remains gated. Next document: post-EUROMOD merge amendment per §18.*
