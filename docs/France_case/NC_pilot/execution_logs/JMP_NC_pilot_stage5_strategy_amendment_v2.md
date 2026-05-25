# JMP NC Pilot — Stage 5 Strategy Amendment v2

*France RURO multi-year extension | v2 | 2026-05-22*

**Document category: strategy amendment to
`docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md`.** Amendment v1 halted
cleanly at HE7 (the runner's `yem = yem00 + yemxp` identity assertion) during
the male pass, before EUROMOD `system.run`. This v2 replaces the failed
ingestion strategy (Strategy B, per-partner with the off-axis partner as a
non-decider) with **Strategy C′: blockwise joint-product EUROMOD**, in which
both partners are deciders in every run. It changes the EUROMOD ingestion
strategy only; the pilot specification, the wide product parquet, and all
downstream gates are unchanged. M1-clean 2016 remains active. The corrected
pooled P3a track is unaffected.

---

## 1. Purpose

To authorize a corrected Stage 5 ingestion strategy that computes EUROMOD
disposable income for the pilot's 900-alternative couples choice set without
tripping the runner's earnings-identity assertion, by treating **both
partners as deciders** and sweeping the joint product as **30 blocks** (one
per fixed female draw). This v2 supersedes the per-partner Strategy B of
amendment v1 as the Stage 5 method, while keeping every safeguard,
pilot-path discipline, and non-authorization boundary of v1.

---

## 2. Current Stage 5 status

Amendment-v1 build halted at HE7, cleanly:

- `import euromod` passed (`PYTHONNET_RUNTIME=coreclr`).
- The pilot adapter `scripts/pilot/export_pilot_euromod_inputs.py` was created.
- Male and female per-partner input files were created; `is_decider` and
  drawsmeta checks passed.
- The **male pass halted at the runner's `yem = yem00 + yemxp` identity
  assertion** (runner lines 769–778); EUROMOD `system.run` was never reached.
- The female pass was not launched. No EUROMOD output was written.
- No GSUR, precompute, estimation, welfare, SA2, or promotion occurred.
- The pilot wide product parquet (2,319,300 rows) and the singles production
  parquet (500,700 rows) are untouched.

This is a halt-and-report under v1 §16, exactly as designed — the strategy
defect surfaced before any irreversible action.

---

## 3. Why amendment v1 halted

Strategy B ran one partner as the decider (varying over 30 draws) and the
other partner as a **non-decider** held at survey/template baseline and
replicated across the draws. The runner's earnings-identity block applies
asymmetrically by decider status:

- For **deciders**, the runner *recomputes* `yem00`, `yemxp`, and
  `yem = yem00 + yemxp` from the final `lhw × yivwg` it is about to send to
  EUROMOD (runner lines 738–760). The identity therefore holds **by
  construction** for decider rows.
- For **non-deciders**, the runner keeps `baseline_yem00`, `baseline_yemxp`,
  `baseline_yem` straight from the EUROMOD template (lines 758–760,
  `np.where(is_decider, …, baseline_*)`).

The assertion at lines 769–778 then checks the identity across **all** rows.
It thus *presumes the template already satisfies* `yem = yem00 + yemxp` for
the non-decider partner. The off-axis partner's template earnings did not
reconcile (template `yem` ≠ `yem00 + yemxp` to 1e-6), and because the runner
deliberately does not touch non-decider earnings, it could not repair it —
so the assertion raised.

---

## 4. What HE7 revealed

HE7 is not a wage-propagation bug on the *varying* partner (the W1 wages
propagated correctly — that path is the decider path and would have passed).
It revealed a structural property of the runner: **the identity assertion is
only self-consistent for rows the runner recomputes, i.e. deciders.** Any row
left at template baseline must already satisfy the identity, and the FR_2016
template does not guarantee this for every individual (template `yem` can be a
survey aggregate not equal to the `yem00 + yemxp` decomposition). Strategy B
put the off-axis partner in exactly that unguarded position. The fix is to
leave no partner in the non-decider/baseline position: make both partners
deciders so both earnings vectors are recomputed and the identity holds for
every row.

---

## 5. Why this is not a model failure

Nothing about the RURO model, the W1 calibrated wage draw, the product
choice set, or the Halton draws is implicated. The halt is entirely in the
**EUROMOD-ingestion plumbing** — specifically the assumption Strategy B made
about how the off-axis partner is presented to the runner. The wide product
parquet, the calibrated `delta_occ` (−0.0797, 0.0251, 0.2415), the common
`sigma` (0.3771), and the HP2 lockstep (verified, max_abs_diff 0.0 on 1,024
samples) all stand. The fix is an adapter-strategy change, not a
re-specification and not a re-build of Stages 1–4.

---

## 6. Why Strategy B is no longer valid as written

Strategy B is invalid for this runner because it relies on the off-axis
partner's template earnings satisfying the identity, which is not guaranteed
and empirically failed. Beyond the assertion, Strategy B was also
**economically incomplete** for a product choice set: with one partner fixed
at observed baseline, a per-partner pass only ever varies one axis, so it
never produces household disposable income for an off-diagonal
(draw_male, draw_female) cell with *both* partners at hypothetical jobs. The
product's whole point is the off-diagonal. Strategy B, even if it had passed
HE7, could not by itself populate the 900-cell joint product. It is retired
as the Stage 5 method.

---

## 7. Evaluation of Strategy B′

**Strategy B′** (both partners deciders, but still a *single* per-couple
sweep — e.g. pairing each partner's draw by a shared index, or running the
diagonal) fixes the HE7 assertion (both earnings vectors recomputed) but does
**not** produce the full joint product: a single shared-index sweep only
visits 30 (draw_male = draw_female) cells, i.e. the diagonal of the
30×30 — the very diagonal defect the whole NC cycle exists to correct. B′ is
therefore acceptable **only as an optional smoke test** that the
both-deciders construction clears HE7 and reaches `system.run`, on a small
input. It is **not** the Stage 5 product-income solution and must not be used
to populate the pilot's joint product.

---

## 8. Limitation of Strategy B′ for a 30×30 product choice set

The pilot requires disposable income for **every** (draw_male, draw_female)
pair, all 900 per couple, including the 870 off-diagonal cells. B′ visits at
most the 30 diagonal cells. Scaling B′ to the full product would require
either 900 separate single-pair runs (impractical) or aliasing the joint key
into the scalar `draw` slot (forbidden — HE2). Neither is acceptable. The
product structure forces a method that holds one axis fixed while sweeping the
other across all 30 values, repeated for each fixed value — i.e. a **blockwise
joint sweep** (Strategy C′).

---

## 9. Required disposable-income object for the NC pilot

The pilot needs, for each couple and each joint alternative
(m, f) ∈ {0..29} × {0..29}, the household disposable income with **both**
partners placed at their respective hypothetical jobs — the male partner at
his draw-m job and the female partner at her draw-f job, simultaneously. This
is a genuinely joint object (EUROMOD computes household-level disposable
income with both earners' earnings entering the tax-benefit calculation
together); it cannot be assembled from two independent single-axis sweeps. The
output target is `ils_dispy_male` and `ils_dispy_female` (the production
couples income routing) for all 2,319,300 wide-parquet rows — but that
**merge** is the later slice; Stage 5 v2 produces the 30 per-block EUROMOD
outputs from which the merge will draw.

---

## 10. Recommended Strategy C′: blockwise joint-product EUROMOD

**Adopt Strategy C′.** Sweep the joint product as **30 blocks**, one per fixed
female draw `f = 0,…,29`. Within block `f`:

- The **female partner is fixed** at her draw-`f` job (her hours, wage, loc4,
  yem from draw f).
- The **male partner varies** across the runner's scalar `draw = 0,…,29`
  (his 30 draws).
- **Both partners are deciders** in the run, so the runner recomputes
  `yem00/yemxp/yem` for both from final `lhw × yivwg` and the identity holds
  for every row — clearing HE7 by construction.
- One EUROMOD run per block ⇒ 30 runs total covers all 30 × 30 = 900 joint
  cells per couple.

Each block thus produces household disposable income for the 30 joint cells
{(m, f) : m = 0..29} at the block's fixed `f`. Concatenating the 30 blocks
gives all 900 cells. (The choice to fix female and vary male is a convention;
fixing male and varying female across 30 blocks is equivalent. Fix **female**,
vary **male**, per the required decisions.)

---

## 11. Draw-index convention under Strategy C′

- The runner's **scalar `draw` is the male marginal draw `m ∈ {0..29}`**
  within each block. The female draw `f` is the block constant, not the
  scalar draw.
- **Never** set the scalar `draw` to `draw_joint` (0..899) — HE2, forbidden.
  Per-block `max_draw = 29` ⇒ `id_multiplier = 1000` (production floor),
  unchanged.
- `draw_male`, `draw_female`, `draw_joint` remain intact on the wide product
  parquet (untouched by Stage 5).
- **`draw_joint = 30·draw_male + draw_female` is reconstructed only after**
  EUROMOD output returns, in the later merge slice — from the block's fixed
  `f` and the run's scalar `m`. Stage 5 records `(m, f)` per output row so the
  merge can rebuild the joint key; it does not build the joint key itself.

---

## 12. Decider convention under Strategy C′

**Both partners are deciders in every block run** (`is_decider = 1` for both
the male and the female record on every row). This is the core fix:

- Both earnings vectors are recomputed by the runner from final inputs, so
  `yem = yem00 + yemxp` holds for every row — no row is left at unguarded
  template baseline.
- The female partner, though held at a fixed job within the block, is still a
  **decider at that fixed job** — her hours/wage/loc4 are the draw-`f`
  values, presented as decider inputs so the runner recomputes her earnings
  too. She is "fixed" in the sense of not varying across the block's scalar
  draw, **not** in the sense of being a non-decider at survey baseline. This
  distinction is what separates C′ from the failed B.

The runner's `is_decider`-explicit path (lines 484–487) is used; the
`max(draw)>0` fallback is never relied upon (HE-DEC).

---

## 13. Block structure and expected number of runs

- **30 blocks**, `f = 0,…,29`.
- **One EUROMOD run per block** ⇒ **30 runs total** for the full sweep.
- **Checkpoint:** run **only block `f = 0` first** (§18). Full 30-block
  execution proceeds only if block `f = 0` passes all §16 validations; else
  halt and report.
- Each block writes its own scenario dir and output, so the 30 runs are
  independently checkpointed (a failed block re-runs alone).

---

## 14. Expected row counts per block and total

Per block (one fixed `f`, male varying over 30 draws), both partners deciders:

- Decider rows ≈ 2,577 couples × 2 partners × 30 male-draws = **~154,620**
  decider rows, plus any replicated child/other-member non-decider rows held
  at baseline (children remain non-deciders; their template earnings must
  satisfy the identity — see HE7 note in §16). The exact count is computed and
  reported by the adapter per block.
- Per-block input is well under the production diagonal run (518,724 couples
  draw-rows) and poses no scaling concern.

Across 30 blocks: the union covers all 2,577 × 900 = **2,319,300** joint cells
(each block contributes 2,577 × 30 = 77,310 joint cells; 30 × 77,310 =
2,319,300). The per-block EUROMOD outputs are **not** merged into the wide
parquet here — that 2,319,300-row assembly is the later merge slice.

---

## 15. Required pilot adapter changes

Modify the pilot adapter `scripts/pilot/export_pilot_euromod_inputs.py`
(pilot-only; no production edit) to emit **per-block** long-format inputs:

- A function that, given block `f`, builds one long-format frame containing
  **both partners as decider rows**: the male partner with scalar
  `draw = m ∈ {0..29}` at his draw-m job; the female partner at her fixed
  draw-`f` job, presented as a decider (her draw-f hours/wage/loc4/yem), also
  keyed so she appears once per `(couple, m)` with `is_decider = 1`.
- Carry: `idperson` (each partner's own id), `idhh`, `draw` (= m), the
  per-partner `hours`, `wage`, `yem`, `yivwg`, `lhw`, `loc_ruro`, `loc4`,
  Mincer covariates, and **`is_decider = 1` for both partners**.
- Record the block constant `f` and each row's `m` in the frame (and/or its
  drawsmeta) so the later merge can reconstruct `draw_joint = 30·m + f`.
- **Drop** the five stray `ils_*` columns (`ils_earns`, `ils_origy`,
  `ils_pen`, `ils_sicdy`, `ils_earns_real`) before the runner call.
- Write each block's input + `__drawsmeta.json` (`id_multiplier = 1000`,
  `n_draws = 30`, `max_draw = 29`, `household_type = "couples"`, `block_f = f`,
  source tag) under `Data/pilot/nc_2016_couples/em_inputs/block_f{f:02d}/`.
- Any per-couple child/other non-decider members retained must have template
  earnings satisfying `yem = yem00 + yemxp`; if the FR_2016 template does not
  guarantee this for some non-decider individuals, the adapter must either
  (a) recompute their `yem00/yemxp` to reconcile before the runner, or
  (b) confirm the template satisfies it — and HE7 will catch any residual
  violation regardless. State which in the report.

---

## 16. Required validation checks

For **block `f = 0`** (the checkpoint) and each subsequent block:

- Input frame: scalar `draw = m` present, values exactly **0..29**;
  `is_decider == 1` for **both** partners on every row; five stray `ils_*`
  absent; drawsmeta `id_multiplier == 1000`.
- Runner reached `system.run` (HE7 did **not** raise — the both-deciders
  construction is the test of the fix).
- Output `combined_draws_em.parquet` exists, ≈343 cols; `ils_dispy` present,
  not all-NaN / not all-zero on decider rows; metadata sidecar written.
- The block's row→(m, f) recording is present so the merge can rebuild
  `draw_joint`.

Slice-level:

- Pilot wide product parquet untouched (2,319,300 rows; draw keys intact).
- Singles production parquet untouched (500,700 rows — HE5).
- For the full sweep: 30 block outputs present, one per `f`; their union
  covers all 900 joint indices per couple (verify the (m, f) coverage is
  exactly {0..29} × {0..29}).

The wide-merge income-completeness check (`ils_dispy_male`/`ils_dispy_female`
non-NaN over all 2,319,300 rows) remains a **merge-slice** check (HE3),
deferred.

---

## 17. Halt conditions

| Halt | Condition |
|---|---|
| **HE1** | Any in-place edit to `enh_RURO_euromod.py` or any production script. Pilot adapter + pilot output dirs only. |
| **HE2** | Scalar `draw` set to `draw_joint` (0..899) or any joint key, in any block. The scalar draw is the male marginal `m ∈ {0..29}`. |
| **HE4** | `id_multiplier ≠ 1000` for any block, or inconsistent multipliers across the per-block drawsmeta. |
| **HE5** | Any change to the singles production parquet (≠ 500,700 rows) or the pilot wide product parquet (≠ 2,319,300 rows; draw keys altered). |
| **HE6** | Any attempt to compute welfare, issue SA2, promote a pilot output, displace M1-clean, or run beyond couples-2016 scope. |
| **HE7** | The `yem = yem00 + yemxp` assertion raises in any block. Under C′ both partners are deciders, so a decider-row violation indicates a wage-propagation bug; a non-decider-row violation indicates an unreconciled child/other template earnings (see §15). Halt and audit; do not work around. |
| **HE-DEC** | `is_decider` not explicitly 1 for **both** partners on any block row (the failure mode that produced the v1 halt). |
| **HE-DRAWSMETA** | A block's drawsmeta absent or inconsistent `id_multiplier`. |
| **HE-EM-PKG** | `python -c "import euromod"` fails (confirm before each session; it passed last run with `PYTHONNET_RUNTIME=coreclr`). |
| **HE-BLOCK** | Full 30-block execution begun before block `f = 0` passed all §16 checks (§18). |
| **HE-STAGE** | Any attempt to begin the post-EUROMOD merge, `draw_joint` reconstruction into the wide parquet, `is_chosen` aliasing, chosen-first sorting, GSUR, precompute, or estimation in this slice. |

Any fired halt → stop, write the report up to the halt, await direction. Do
not work around.

---

## 18. Checkpoint rule before full 30-block execution

**Run block `f = 0` alone first.** It is the smoke test that the C′
both-deciders construction (a) clears HE7 and reaches `system.run`, and
(b) returns populated `ils_dispy`. Full 30-block execution is authorized
**only if block `f = 0` passes every §16 block-level check**. If block `f = 0`
fails any check, **halt and report** — do not launch blocks `f = 1,…,29`.
This bounds the blast radius of a strategy that has already failed once: one
block, not thirty, is the cost of a second strategy defect.

(Optional, permitted but not required: a single B′ diagonal smoke run on a
tiny input purely to confirm both-deciders clears HE7, *before* even block
`f = 0`. This is a throwaway diagnostic, not a product-income artifact, and
must not be merged anywhere.)

---

## 19. What is authorized

- Modifying the pilot adapter to emit per-block both-deciders long-format
  inputs (pilot-only path).
- Generating block `f = 0` input + drawsmeta, and (after the checkpoint
  passes) blocks `f = 1,…,29`.
- The `import euromod` pre-launch check.
- Running EUROMOD **for block `f = 0` first**; then, conditional on its
  validation, the remaining 29 blocks — each via the production runner with
  pilot-only `--scenario-dir`, system `FR_2015`, dataset `FR_2016`, writing
  per-block `combined_draws_em.parquet` + metadata + `run.log` + timing JSON.
- An optional throwaway B′ HE7 smoke run (§18).
- The §16 validations and the Stage 5 v2 build report (§21).

---

## 20. What is not authorized

- The post-EUROMOD merge; reconstructing `draw_joint` into the wide parquet;
  `is_chosen = is_chosen_joint`; chosen-first sorting; the HE3 wide-completeness
  check — **all the next (merge) slice.**
- Using B or B′ to populate the joint product (B retired; B′ smoke-test only).
- GSUR merge; precompute; estimation; welfare; SA2; canonical promotion;
  M1-clean displacement.
- Singles rebuild / singles EUROMOD; the 400/1,600 consistency builds.
- Any in-place edit to production scripts, the P3a YAML, or production guards.
- Any write to production data/estimation directories.
- Scalar `draw = draw_joint` aliasing.
- Launching blocks `f = 1,…,29` before block `f = 0` passes (HE-BLOCK).

---

## 21. Required Stage 5 v2 build report

`Results/JMP_NC_pilot_stage5_strategy_v2_build_report_v1.md`, covering: scope
and authorization provenance (this v2 amendment); the v1 HE7 halt recap and
the C′ rationale; adapter changes (per-block both-deciders construction, the
`is_decider=1` on both partners, the five `ils_*` dropped, the (m, f)
recording, child/non-decider earnings reconciliation per §15); block `f = 0`
checkpoint result (input validation, `import euromod`, runner reached
`system.run`, HE7 status, `ils_dispy` population, wall time); if the checkpoint
passed, the remaining-blocks results (per-block paths, row counts, wall times,
(m, f) coverage union over all 30 blocks); the §16 slice-level validations
(wide + singles parquet untouched); halt-condition status (none/which fired);
promotion-debt list (block-count, fix-female-vary-male convention, any
hard-coded constants); and required final statements (merge NOT run; M1-clean
active; P3a unaffected; no GSUR/precompute/estimation/welfare/SA2/promotion;
Stage 5 v2 only).

---

## 22. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Pilot paths only; block `f=0` first; stop
per the checkpoint rule.

```text
Work locally in my RURO/MNL codebase. PILOT BUILD — STAGE 5 v2 (EUROMOD),
Strategy C' (blockwise joint-product), FR_2016 couples only. Authorized by
docs/JMP_NC_pilot_stage5_strategy_amendment_v2.md. This SUPERSEDES Strategy B
in amendment v1 (which halted at HE7).

HARD CONSTRAINTS (halt and report if any would be violated):
- Run BLOCK f=0 FIRST. Do NOT launch blocks f=1..29 until f=0 passes all
  block-level checks (HE-BLOCK).
- STOP after the authorized blocks complete and validate. Do NOT merge to the
  wide parquet, do NOT reconstruct draw_joint into it, do NOT add is_chosen,
  do NOT sort chosen-first, do NOT run GSUR/precompute/estimation/welfare/SA2.
- Do NOT edit enh_RURO_euromod.py or any production script in place. Runner is
  invoked, never modified. Adapter + outputs under scripts/pilot/ and
  Data/pilot/nc_2016_couples/ only.
- BOTH partners are deciders in every block (is_decider=1 for male AND female
  on every row). This is the fix for the v1 HE7 halt. Never rely on the
  max(draw)>0 fallback.
- Scalar runner draw = male marginal m in 0..29. NEVER draw = draw_joint.
  Female draw f is the block constant.
- Do NOT touch the singles production parquet or the pilot wide product
  parquet (read-only inputs).
- Do NOT compute welfare/SA2/promote/displace M1-clean.

Pre-launch (HE-EM-PKG): python -c "import euromod" (PYTHONNET_RUNTIME=coreclr).
If it fails, HALT and report.

Read first:
- docs/JMP_NC_pilot_stage5_strategy_amendment_v2.md
- docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md
- Results/JMP_NC_pilot_stage5_euromod_build_report_v1.md (the HE7 halt)
- scripts/enhanced/enh_RURO_euromod.py (read-only; note the yem identity at
  lines ~738-778 recomputes earnings for DECIDERS only)
- scripts/pilot/export_pilot_euromod_inputs.py (the v1 adapter to modify)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet (schema)

STEP 1 — Adapter (per-block, both deciders):
Modify scripts/pilot/export_pilot_euromod_inputs.py to add a per-block export.
For block f, build ONE long-format frame with BOTH partners as decider rows:
- male partner: scalar draw = m in 0..29, his draw-m hours/wage/loc4/yem,
  is_decider=1;
- female partner: fixed at her draw-f job (draw-f hours/wage/loc4/yem),
  presented as a DECIDER (is_decider=1), appearing once per (couple, m);
- carry idperson (each partner's own id), idhh, draw=m, hours, wage, yem,
  yivwg, lhw, loc_ruro, loc4, Mincer covariates;
- record block constant f and each row's m (for later draw_joint=30*m+f);
- DROP 5 stray ils_*: ils_earns, ils_origy, ils_pen, ils_sicdy, ils_earns_real;
- any child/other non-decider members: ensure their template yem=yem00+yemxp
  (recompute to reconcile if needed) — HE7 will catch residual violations;
- write input + __drawsmeta.json (id_multiplier=1000, n_draws=30, max_draw=29,
  household_type="couples", block_f=f) under
  Data/pilot/nc_2016_couples/em_inputs/block_f00/ (and block_fNN/ later).

STEP 2 — Validate block f=0 input BEFORE running:
scalar draw values exactly 0..29; is_decider==1 for BOTH partners on every
row; 5 stray ils_* absent; drawsmeta id_multiplier==1000. Fail -> HALT.

STEP 3 — Run block f=0:
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\block_f00\fr_pilot_2016_couples_block_f00_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\block_f00"
Redirect stdout/stderr to `Data/pilot/nc_2016_couples/em_outputs/block_f00/run.log`.
Save timing JSON.

STEP 4 — Validate block f=0 output (amendment section 16):
runner reached system.run (HE7 did NOT raise); combined_draws_em.parquet
exists, ils_dispy present, not all-NaN/not all-zero on decider rows; sidecar
written; (m,f) recording present.

CHECKPOINT (HE-BLOCK): only if block f=0 passes ALL checks, proceed to
STEP 5. Otherwise HALT and write the report.

STEP 5 — Blocks f=1..29 (only after checkpoint):
Repeat STEP 1-4 per block under block_fNN/ dirs. Each block is independently
checkpointed (a failed block re-runs alone). After all 30: verify the (m,f)
coverage union is exactly {0..29} x {0..29}.

STEP 6 — Slice validation:
pilot wide parquet untouched (2,319,300; draw keys intact); singles untouched
(500,700). THEN STOP. Do not begin the merge slice.

Halt conditions: HE1, HE2, HE4, HE5, HE6, HE7, HE-DEC, HE-DRAWSMETA,
HE-EM-PKG, HE-BLOCK, HE-STAGE (amendment section 17). If any fires, STOP,
write the report to that point, await direction.

Optional (permitted): a tiny throwaway B' diagonal run to confirm
both-deciders clears HE7 before block f=0. Throwaway only; merge nowhere.

Write ONE report: Results/JMP_NC_pilot_stage5_strategy_v2_build_report_v1.md
per amendment section 21. End with required final statements (merge NOT run;
M1-clean active; P3a unaffected; no GSUR/precompute/estimation/welfare/SA2/
promotion; Stage 5 v2 only).
```

Save the report as:
`Results/JMP_NC_pilot_stage5_strategy_v2_build_report_v1.md`

---

**Required final statements:**

- **This v2 amendment replaces Strategy B with Strategy C′ (blockwise
  joint-product EUROMOD) as the Stage 5 method.** It changes the ingestion
  strategy only; the pilot spec and the wide product parquet are unchanged.
- **Strategy B is retired** (off-axis non-decider tripped HE7 and could not
  populate the joint product). **B′ is permitted only as a throwaway HE7
  smoke test**, never as the product-income solution.
- **C′ computes disposable income for every (draw_male, draw_female) pair via
  30 blocks** (one per fixed female draw `f`), **both partners deciders** in
  every block, **scalar runner draw = male marginal `m ∈ {0..29}`**, never
  `draw_joint`.
- **`draw_male`/`draw_female`/`draw_joint` preserved; `draw_joint`
  reconstructed only after EUROMOD output, in the later merge slice.**
- **Block `f = 0` runs first as a checkpoint; the full 30-block sweep is
  authorized only if `f = 0` passes all validations**, else halt and report.
- **The wide product parquet stays untouched until the merge slice; no
  production script is edited in place.**
- **M1-clean 2016 remains active; corrected pooled P3a track unaffected; no
  GSUR, precompute, estimation, welfare, SA2, or promotion.**

---

*Status: strategy amendment v2 — Stage 5 EUROMOD via Strategy C′ (blockwise
joint product, both partners deciders), block f=0 checkpoint first, pilot
paths, under the §17 halts. Supersedes Strategy B of amendment v1. Executes
nothing itself. Next document: the Stage 5 v2 build report (§21), then a
separate post-EUROMOD merge-slice authorization.*
