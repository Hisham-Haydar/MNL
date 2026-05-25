> Archived on 2026-05-26 — explicitly superseded by `stage5_strategy_amendment_v2` (Strategy C′: blockwise joint-product EUROMOD with both partners as deciders), which replaces Strategy B (per-partner with off-axis non-decider) after the HE7 yem-identity assertion halt.
> Replacement (kept active): `docs/France_case/execution_logs/NC_pilot/JMP_NC_pilot_stage5_strategy_amendment_v2.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP NC Pilot — Stage 5 EUROMOD Scope Amendment v1

*France RURO multi-year extension | v1 | 2026-05-22*

**Document category: scope amendment to `docs/JMP_NC_pilot_spec_contract_v1.md`.**
This amendment authorizes **Stage 5 (EUROMOD) only** for the FR_2016
couples-only NC pilot, under **Strategy B** (temporary long-format
per-partner exports derived from the pilot product parquet; the wide product
parquet is never passed to EUROMOD). It changes execution scope, not the
specification. The post-EUROMOD merge, `is_chosen` aliasing, and chosen-first
sorting are explicitly a **separate later slice** and are NOT authorized here.
M1-clean 2016 remains the active baseline. The corrected pooled P3a track is
unaffected.

---

## 1. Purpose

To authorize the EUROMOD pass(es) that compute disposable income for the
pilot's 900-alternative couples choice set, using the proven production
runner `scripts/enhanced/enh_RURO_euromod.py::run_euromod_for_draws()` on a
**new pilot-only adapter export**, not on the wide product parquet directly.
The amendment pins the four open items the runner-confirmation audit flagged
(adapter design, drawsmeta sidecars, explicit `is_decider`, package-import
check) so the build has no judgment calls left, and it bounds the slice with
a hard stop before the post-EUROMOD merge.

---

## 2. Current pilot status

- **Stages 1–4 passed.** The pilot wide product parquet exists at
  `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`:
  **2,319,300 rows** (2,577 couples × 900), 149 columns, with
  `draw_male`/`draw_female`/`draw_joint` and
  `is_chosen_joint`/`is_chosen_male`/`is_chosen_female`. No scalar `draw`
  column (by design). EUROMOD-dependent income columns dropped at Stage 4.
- **`draw_joint` re-pointing audit complete.** Forbids global `draw =
  draw_joint` aliasing; identifies the downstream chosen-column / position-0
  surface for the later merge slice.
- **EUROMOD-runner confirmation audit complete.** Verdict: Stage 5 ready
  under Strategy B, conditional on this amendment pinning the adapter,
  drawsmeta, decider flag, and package check.
- **Active baseline:** M1-clean 2016, not displaced. Corrected pooled P3a
  track independent and unaffected.

---

## 3. Why Stage 5 is now considered

Stages 1–4 produced a valid choice-set scaffold (regenerated draws + W1 wage
values) but deliberately omitted disposable income, which only EUROMOD can
supply for the new product alternatives. Stage 5 is the binding data-build
step the whole NC cycle has been gated on. It is considered now — and only
now — because the two read-only audits have (a) confirmed the runner exists
and is FR_2016-proven, (b) determined the *correct ingestion strategy*
(Strategy B, per-partner long-format), and (c) reduced the open risks to a
small, named, pinnable list. Without those audits, launching EUROMOD would
have been the large-blast-radius action the Stage 1–4 build correctly refused.

---

## 4. Inputs from Stages 1–4

The Stage 5 adapter consumes:

- The pilot wide product parquet (above), or equivalently the per-partner
  marginal draws preserved as Stage 2–3 intermediate state, as the source of
  per-partner `(idperson, draw)` rows.
- The W1 (calibrated) wage values already written into the pilot draws
  (`wage_male`/`wage_female` and the per-partner Mincer covariates), so
  EUROMOD's earnings identity (`yem = yem00 + yemxp`) is fed consistent
  wages.
- The pilot metadata sidecar recording the Stage-4 column drops and the
  `n_draws=900` couples convention.

The adapter does **not** consume or modify any production estimation-ready
parquet.

---

## 5. Findings from draw_joint re-pointing audit

Carried forward as binding constraints:

1. **Do NOT globally alias `draw = draw_joint`.** Forcing the 0..899 joint
   key into the runner's scalar `draw` slot would set `id_multiplier` from
   `max_draw=899` (30× the production arithmetic) and drive the non-decider
   replication loop over 900 values — a regime the runner was never tested
   for. Forbidden (Strategy A, globally rejected).
2. **Preserve `draw_male`, `draw_female`, `draw_joint`** in the pilot wide
   parquet; the per-partner passes key on the marginal draws and the joint
   key is reconstructed later via `draw_joint = 30·draw_male + draw_female`.
3. The downstream chosen-column surface (synthetic `is_chosen = is_chosen_joint`;
   chosen-first group sorting for the position-0 assumption at
   `estimation_engine.py:380`; ~15 sites in `RURO_post_estimation_styled.py`)
   is **identified but belongs to the merge slice**, not Stage 5.

---

## 6. Findings from EUROMOD-runner confirmation audit

Carried forward:

1. **Runner:** `scripts/enhanced/enh_RURO_euromod.py`, entry
   `run_euromod_for_draws()` (line 346), FR_2016-proven (existing
   `combined_draws_em.parquet`, 1,087,300×343, from the diagonal 99-draw run).
2. **Strategy B required.** The wide product parquet is not the runner's
   `(idperson, draw)` long shape; a pilot adapter projects it to two
   per-partner long-format frames. Runner hard-raises `KeyError` if no scalar
   `draw` column (line 426).
3. **System/dataset:** `--euromod-system FR_2015` (policy year = data year − 1,
   per the production pipelines) on `--euromod-dataset FR_2016`.
4. **`is_decider` must be set explicitly** (the `max(draw)>0` fallback
   mis-classifies under per-partner export).
5. **`id_multiplier = 1000`** on both per-partner drawsmeta sidecars; the
   runner raises if the two disagree (line 1190).
6. **Five stray `ils_*` columns** (`ils_earns`, `ils_origy`, `ils_pen`,
   `ils_sicdy`, `ils_earns_real`) survived the Stage-4 drop; the adapter drops
   them explicitly before the runner call.
7. **`euromod` package import** must be confirmed in the venv before launch
   (HE-EM-PKG); the runner imports it inside the `EuromodRunner` constructor
   (line 191).
8. Release root auto-resolves to
   `U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`
   (confirmed present); `FR_2016.txt` template confirmed present.

---

## 7. Stage 5 scope

**Authorized:** building the pilot EUROMOD adapter, generating the two
per-partner long-format draws files with drawsmeta sidecars, and running the
**two EUROMOD passes** (male, female) via the production runner on pilot-only
paths, producing two per-pass `combined_draws_em.parquet` outputs with
metadata sidecars.

**Hard stop:** the slice ends when both per-pass EUROMOD outputs and their
metadata sidecars exist and pass the §15 per-pass validations. It does **not**
merge the outputs back to the wide parquet, add `is_chosen`, sort chosen-first,
run precompute, estimate, or anything downstream.

Scope is **FR_2016 couples only**. Singles are not touched.

---

## 8. Pilot EUROMOD adapter design

New module `scripts/pilot/export_pilot_euromod_inputs.py` (pilot-only;
no production code edited). For each partner side (male, female) it builds a
long-format draws frame:

- **One row per `(idperson_partner, draw_partner)`**, 30 draws/person, where
  `draw = draw_male` (male pass) or `draw = draw_female` (female pass), values
  **0..29** (scalar partner-level draw — §9).
- **Columns:** `idperson` (the partner's own id, not the male-only carry),
  `idhh` (couple household id), `draw`, `hours`, `wage`, `yem`, `yivwg`,
  `lhw`, `loc_ruro`, `loc4`, the partner's observed Mincer covariates, the
  other-partner household carry needed for non-decider replication, and
  **`is_decider = 1`** (§10).
- **Drop** the five stray `ils_*` columns (§6.6) before writing.
- **Write** each frame to `Data/pilot/nc_2016_couples/em_inputs/` as
  `fr_pilot_2016_couples_male_partner_draws.parquet` /
  `..._female_partner_draws.parquet`, each with a matching
  `__drawsmeta.json` (§11).

The adapter is self-contained (<300 lines), testable, and writes only under
pilot paths. The runner-confirmation audit recommended the adapter could
warrant its own read-only design doc first; given its design is now fully
specified here (inputs, outputs, decider flag, drawsmeta, column drops), the
build may proceed directly to writing it under the §16 halts — but if the
executor finds any adapter design point underspecified at build time, that is
a halt-and-report, not an improvise.

---

## 9. Draw-index handling

- **Scalar `draw` per pass = partner-level marginal draw, 0..29.** Male pass
  uses `draw_male`; female pass uses `draw_female`.
- **No `draw = draw_joint` aliasing** anywhere (HE2). If the adapter would
  emit `draw_joint` (or `draw_male`/`draw_female`) into the scalar `draw`
  slot as the joint 0..899 key, halt.
- `draw_male`, `draw_female`, `draw_joint` remain intact on the pilot wide
  parquet (untouched by Stage 5); the joint key is reconstructed only in the
  later merge slice.
- Per-pass `max_draw = 29` ⇒ runner `id_multiplier` floor = **1000** (matches
  production); IDs `idhh = idhh_true·1000 + draw` stay well within int64.

---

## 10. Decider-mask requirement

**`is_decider = 1` is set explicitly on every adapter output row** for the
partner being processed in that pass (HE-DEC). The runner's fallback
`is_decider = (max(draw) > 0)` is unreliable under per-partner export and must
not be relied on. The non-decider partner (and any children) are held at
observed baseline and replicated across the 30 draws by the runner's existing
non-decider replication (lines 510–524); the adapter supplies the carry
columns that replication needs. If the decider flag is absent or not 1 on the
decider rows, halt.

---

## 11. Drawsmeta sidecar contract

Each per-partner draws parquet is accompanied by a `__drawsmeta.json` with:

- `id_multiplier = 1000` (**identical across both sidecars** — HE-DRAWSMETA;
  the runner raises at line 1190 if they differ),
- `n_draws = 30`, `max_draw = 29`,
- `household_type = "couples"`,
- a source-set tag (pilot product parquet provenance, partner side),
- the W1-calibrated-wage provenance note (so the earnings identity input is
  auditable).

---

## 12. EUROMOD runner and command

Runner: `scripts/enhanced/enh_RURO_euromod.py` (production, **read-only** —
invoked, never edited). Two passes, pilot-only `--scenario-dir`:

**Male pass:**
```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\fr_pilot_2016_couples_male_partner_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\male_pass"
```

**Female pass:** identical with `_male` → `_female` in the draws path and
`male_pass` → `female_pass` in the scenario dir.

Notes: `--singles-draws` is the runner's *primary* draws-file flag (a misnomer
here — it accepts any long-format frame; `--couples-draws` is unused since
each pass is one partner). `--euromod-system FR_2015` is the policy year for
FR_2016 microdata, matching `run_fr_2016_joint_only.ps1`.

**Pre-launch (HE-EM-PKG):** confirm `python -c "import euromod"` succeeds in
the project venv before either pass. If it fails, halt — do not attempt the
run.

---

## 13. Expected outputs

- `Data/pilot/nc_2016_couples/em_outputs/male_pass/combined_draws_em.parquet`
  + `combined_draws_em__euromodmeta.json`
- `Data/pilot/nc_2016_couples/em_outputs/female_pass/combined_draws_em.parquet`
  + `combined_draws_em__euromodmeta.json`

Each ≈343-column production EUROMOD output schema, `n_draws=30`. Per-pass row
count ≈ 2,577 × 30 × (decider + replicated non-decider members) — bounded,
well under the production 518,724, computed and reported by the adapter. Each
metadata sidecar records `system`, `dataset`, `n_rows`, `n_draws`,
`id_multiplier`, `carried_columns`, `timestamp`.

The post-EUROMOD wide parquet (`...__post_em.parquet`) with `ils_dispy_male`/
`ils_dispy_female` populated is **NOT** produced here — that is the merge slice.

---

## 14. Logging and checkpoint strategy

- Redirect each pass's stdout/stderr to `…/male_pass/run.log` and
  `…/female_pass/run.log`.
- Persist each pass's `__euromodmeta.json` and a small per-pass timing JSON
  (wall time + row-count breakdown) — the pilot's measurement objective.
- **Two separate processes = the checkpoint.** If male succeeds and female
  fails, the male output is preserved; only female re-runs. A thin driver may
  short-circuit a pass whose `__euromodmeta.json` already exists.
- No internal chunking (per-pass input ≤~200k rows is well within the runner's
  single-call capacity).

---

## 15. Required validation checks

Per pass, before declaring the pass complete:

- Input draws frame: scalar `draw` present, values exactly **0..29**; one row
  per `(idperson, draw)` for the decider; `is_decider == 1` on decider rows;
  five stray `ils_*` columns absent.
- Drawsmeta: `id_multiplier == 1000`, identical across both sidecars.
- Runner completed without raising the `yem = yem00 + yemxp` identity
  assertion (HE7) — confirms W1 wages propagated to `yivwg`/`lhw` consistently.
- Output: `combined_draws_em.parquet` exists, ≈343 cols, `ils_dispy` present
  and not all-NaN / not all-zero on the decider rows; metadata sidecar written.

Slice-level (both passes):

- Both per-pass outputs + sidecars present.
- Singles production parquet untouched (row count still 500,700 — HE5).
- Pilot wide product parquet untouched (still 2,319,300 rows; draw keys
  intact).

**Note:** the couples-completeness check (`ils_dispy_male`/`ils_dispy_female`
non-NaN over all 2,319,300 wide rows — HE3) is a **merge-slice** check, not a
Stage 5 check, because the wide merge does not happen here. Stage 5 validates
per-pass income population only.

---

## 16. Halt conditions

| Halt | Condition |
|---|---|
| **HE1** | Any in-place edit to `enh_RURO_euromod.py` or any production script. Pilot adapter + pilot output dirs only. |
| **HE2** | EUROMOD inputs presented with `draw_joint`/`draw_male`/`draw_female` aliased into the scalar `draw` slot as a 0..899 joint key (forbidden Strategy A). Manual halt even if the runner does not raise. |
| **HE4** | `_compute_id_multiplier` ≠ 1000 for the 30-draw pilot, or the two per-partner drawsmeta sidecars carry different multipliers (runner raises at line 1190). |
| **HE5** | Any change to the singles production parquet (row count ≠ 500,700). |
| **HE6** | Any attempt to compute welfare, issue SA2, promote a pilot output, displace M1-clean, or run beyond couples-2016 scope. |
| **HE7** | The `yem = yem00 + yemxp` deterministic identity assertion (runner line 776) raises — Mincer wages not consistently propagated to `yivwg`/`lhw`. Halt and audit the adapter's wage columns. |
| **HE-DEC** | `is_decider` not explicitly set to 1 for the decider partner on a pass (runner falls back to unreliable inference). |
| **HE-DRAWSMETA** | A per-partner drawsmeta sidecar is absent or the two carry inconsistent `id_multiplier`. |
| **HE-EM-PKG** | `python -c "import euromod"` fails in the venv. Confirm before launch; halt if it fails. |
| **HE-STAGE** | Any attempt to begin the post-EUROMOD merge, `is_chosen` aliasing, chosen-first sorting, precompute, or estimation in this slice. |

HE3 (wide-merge income completeness) is deferred to the merge slice (§15
note). Any fired halt → stop, write the report up to the halt, await
direction. Do not work around.

---

## 17. What is authorized

- Writing the pilot adapter `scripts/pilot/export_pilot_euromod_inputs.py`
  (pilot-only).
- Generating the two per-partner long-format draws parquets +
  `__drawsmeta.json` sidecars under `Data/pilot/nc_2016_couples/em_inputs/`.
- The `python -c "import euromod"` pre-launch check.
- Running the two EUROMOD passes via the production runner with the §12
  commands, writing per-pass `combined_draws_em.parquet` + metadata +
  `run.log` + timing JSON under `Data/pilot/nc_2016_couples/em_outputs/`.
- The §15 per-pass and slice-level validations.
- The Stage 5 build report (§19).

---

## 18. What is not authorized

- The post-EUROMOD merge to the wide parquet; the synthetic `is_chosen =
  is_chosen_joint`; chosen-first group sorting; the HE3 wide-completeness
  check — **all the next (merge) slice.**
- GSUR merge; precompute; estimation; welfare; SA2; canonical promotion;
  M1-clean displacement.
- Singles rebuild / singles EUROMOD; the 400/1,600 consistency builds.
- Any in-place edit to production scripts, the P3a YAML, or production guards.
- Any write to production data/estimation directories.
- Global `draw = draw_joint` aliasing.

---

## 19. Required Stage 5 report

`Results/JMP_NC_pilot_stage5_euromod_build_report_v1.md`, covering: scope and
authorization provenance (this amendment); adapter built (path, inputs,
outputs, the explicit `is_decider=1`, the five `ils_*` columns dropped); the
two per-partner draws files + drawsmeta (with `id_multiplier=1000` consistency
confirmed); `import euromod` check result; the two runner invocations
(commands, system `FR_2015` / dataset `FR_2016`); per-pass outputs (paths, row
counts, ≈col count, `ils_dispy` population, wall time); the §15 validations
(scalar draw 0..29, decider flag, yem identity not raised, singles + wide
parquet untouched); halt-condition status (none/which fired); promotion-debt
list (any hard-coded pilot constants); and required final statements (merge
NOT run; M1-clean active; P3a unaffected; no GSUR/precompute/estimation/
welfare/SA2/promotion; Stage 5 only).

---

## 20. Exact Claude Code Stage 5 task

Use **Claude Code (Sonnet)**, local. Pilot paths only; stop after both passes.

```text
Work locally in my RURO/MNL codebase. PILOT BUILD — STAGE 5 (EUROMOD) ONLY,
FR_2016 couples only, Strategy B. Authorized by
docs/JMP_NC_pilot_stage5_euromod_amendment_v1.md.

HARD CONSTRAINTS (halt and report if any would be violated):
- STOP after both EUROMOD passes complete and validate. Do NOT merge outputs
  to the wide parquet, do NOT add is_chosen, do NOT sort chosen-first, do NOT
  run GSUR/precompute/estimation/welfare/SA2.
- Do NOT edit enh_RURO_euromod.py or any production script in place. The
  runner is invoked, never modified. Adapter + outputs live under
  scripts/pilot/ and Data/pilot/nc_2016_couples/ only.
- Do NOT alias draw = draw_joint anywhere. Scalar draw per pass = partner
  marginal draw 0..29.
- Do NOT touch the singles production parquet or the pilot wide product
  parquet (read-only inputs).
- Do NOT compute welfare, issue SA2, promote, or displace M1-clean.

Pre-launch check (HE-EM-PKG):
- Run: python -c "import euromod"  in the project venv. If it fails, HALT and
  write the report; do not attempt any EUROMOD run.

Read first (confirm, don't assume):
- docs/JMP_NC_pilot_stage5_euromod_amendment_v1.md
- Results/JMP_NC_pilot_EUROMOD_runner_confirmation_v1.md
- Results/JMP_NC_pilot_draw_joint_repointing_audit_v1.md
- scripts/enhanced/enh_RURO_euromod.py  (read-only reference)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet (schema)
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json

STEP 1 — Adapter: write scripts/pilot/export_pilot_euromod_inputs.py.
For each partner side (male, female), build a long-format draws frame:
- one row per (idperson_partner, draw_partner), draw in 0..29 scalar;
- columns: idperson (partner's own id), idhh, draw, hours, wage, yem, yivwg,
  lhw, loc_ruro, loc4, partner Mincer covariates, other-partner household
  carry for non-decider replication, and is_decider = 1 (EXPLICIT);
- DROP the 5 stray ils_* cols: ils_earns, ils_origy, ils_pen, ils_sicdy,
  ils_earns_real;
- write to Data/pilot/nc_2016_couples/em_inputs/
  fr_pilot_2016_couples_{male,female}_partner_draws.parquet
- write matching __drawsmeta.json: id_multiplier=1000 (IDENTICAL both sides),
  n_draws=30, max_draw=29, household_type="couples", source tag.

STEP 2 — Validate each input frame BEFORE running EUROMOD:
- scalar draw present, values exactly 0..29; is_decider==1 on decider rows;
  5 stray ils_* absent; both drawsmeta id_multiplier==1000 and equal.
- If any fails: HALT (HE2/HE-DEC/HE-DRAWSMETA), write report.

STEP 3 — Male pass:
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\fr_pilot_2016_couples_male_partner_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\male_pass"
Redirect stdout/stderr to `Data/pilot/nc_2016_couples/em_outputs/male_pass/run.log`.
Save timing JSON.

STEP 4 — Female pass: identical with _male->_female and male_pass->female_pass.

STEP 5 — Per-pass + slice validation (amendment section 15):
- output combined_draws_em.parquet exists, ils_dispy present, not all-NaN /
  not all-zero on decider rows; metadata sidecar written;
- yem=yem00+yemxp assertion did NOT raise (HE7);
- singles production parquet untouched (==500,700); pilot wide parquet
  untouched (==2,319,300, draw keys intact).

THEN STOP. Do not begin the merge slice.

Halt conditions: HE1, HE2, HE4, HE5, HE6, HE7, HE-DEC, HE-DRAWSMETA,
HE-EM-PKG, HE-STAGE (amendment section 16). If any fires, STOP, write the
report to that point, await direction.

Write ONE report: Results/JMP_NC_pilot_stage5_euromod_build_report_v1.md per
amendment section 19. End with required final statements (merge NOT run;
M1-clean active; P3a unaffected; no GSUR/precompute/estimation/welfare/SA2/
promotion; Stage 5 only).
```

Save the report as: `Results/JMP_NC_pilot_stage5_euromod_build_report_v1.md`

---

**Required final statements:**

- **This amendment authorizes Stage 5 (EUROMOD) only**, under Strategy B, for
  the FR_2016 couples-only NC pilot. It changes execution scope, not the spec.
- **The wide product parquet is never passed to EUROMOD**; two per-partner
  long-format adapter exports are, with scalar `draw ∈ {0..29}`.
- **No `draw = draw_joint` aliasing**; `draw_male`/`draw_female`/`draw_joint`
  preserved on the wide parquet.
- **`is_decider = 1` set explicitly per pass; drawsmeta `id_multiplier = 1000`
  identical on both sidecars; the five stray `ils_*` columns dropped;
  `import euromod` verified before launch.**
- **Runner `enh_RURO_euromod.py` invoked, never edited**; system `FR_2015`,
  dataset `FR_2016`.
- **The post-EUROMOD merge, `is_chosen` aliasing, and chosen-first sorting are
  the next slice and are NOT authorized here.**
- **M1-clean 2016 remains active; corrected pooled P3a track unaffected; no
  GSUR merge, precompute, estimation, welfare, SA2, or promotion.**

---

*Status: scope amendment v1 — Stage 5 EUROMOD only, Strategy B, pilot paths,
under the §16 halts. Executes nothing itself. Next document: the Stage 5 build
report (§19), then a separate post-EUROMOD merge-slice authorization.*
