# JMP NC Pilot — Stage 5 EUROMOD Build Report v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: pilot build report. Records execution of NC pilot
Stage 5 (EUROMOD) under
`docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md`. **HE7 fired on the
male pass; build halted; female pass not started.** Per amendment §16:
"Halt and report; do not work around." No EUROMOD output was
written for the female pass. No GSUR merge; no post-EUROMOD merge to
the wide parquet; no `is_chosen` aliasing; no chosen-first sorting;
no precompute; no estimation; no welfare; no SA2; no promotion.
M1-clean 2016 remains the active baseline. Corrected pooled P3a
track unaffected.

---

## 1. Stage 5 verdict

**HALTED — HE7 (`yem = yem00 + yemxp` identity assertion).** The male
EUROMOD pass raised
`ValueError("Earnings identity yem = yem00 + yemxp violated in 22560
rows (max_diff=0.000300)")` from
`enh_RURO_euromod.py:778` (assertion at lines 768–778). The runner
exited with code 1. No `combined_draws_em.parquet` was written for
the male pass. The female pass was not started, in keeping with
"Do not work around a halt."

**Cause located.** The runner replicates non-decider rows from the
FR_2016 microdata template (`U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt`)
across all draws (lines 510–524). For the male pass, the female
partner is treated as a non-decider (per Strategy B as specified in
amendment §10). The FR_2016 template's `yem00`, `yemxp`, `yem`
columns for those female partners are **observed survey values** that
do NOT satisfy `yem = yem00 + yemxp` to 1e-6 tolerance — the strict
threshold the runner's assertion enforces.

Independent verification on the production FR_2016 couples draws
file (`U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet`)
**at draw=0** confirms this: 4,960 of 5,154 `is_decider==1` baseline
rows violate the identity (max diff 18,080 EUR); 0 of 3,324
`is_decider==0` rows violate it. The production diagonal run
succeeded because BOTH partners were deciders simultaneously, so the
runner's lines 754–756 wrote `yem_computed = yem00_computed +
yemxp_computed` for both — by construction the identity then held.

**This is a Strategy-B architectural mismatch with the runner's
assertion semantics**, not a bug in the adapter. The amendment named
HE7 as a halt condition but did not anticipate that under Strategy B
the off-axis partner would inherit unfixed baseline `yem` from the
template. The fix is a Strategy or design decision that requires a
contract amendment — not an in-place edit, not an adapter
work-around, not an HE7 bypass. The fix surface is named in §13.

---

## 2. Authorization scope

Stage 5 (EUROMOD) only, per
`docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md`. Strategy B
(per-partner long-format export). Pilot-only paths. Hard stop before
the post-EUROMOD merge. None of the not-authorized actions
(GSUR / precompute / estimation / welfare / SA2 / promotion /
M1-clean displacement / in-place production edits) was performed.

---

## 3. `euromod` import check (HE-EM-PKG)

| Property | Value |
|---|---|
| Python executable | `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe` |
| Python version | `3.12.2` |
| Bare `python -c "import euromod"` | **FAILS** with `RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize from …\pythonnet\runtime\Python.Runtime.dll` (netfx loader path) |
| `PYTHONNET_RUNTIME=coreclr` + `python -c "import euromod"` | **OK** |
| Runner module (`import enh_RURO_euromod`) | **OK** — the runner itself sets `os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")` at line 67 before importing |

**Verdict: HE-EM-PKG passes** with the documented coreclr-runtime
flag the runner already sets internally. Direct invocations of
`enh_RURO_euromod.py` succeed at the package-import boundary (the
HE7 failure later in this report is at the deterministic-identity
assertion, not at package import).

---

## 4. Pilot adapter built

`scripts/pilot/export_pilot_euromod_inputs.py` — new pilot-only
module, 285 lines, written today. **No production file was modified.**

The adapter:

1. Reads the production FR_2016 couples draws baseline
   (`U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet`)
   filtered to `draw == 0` (8,478 baseline rows: 5,154 RURO deciders +
   3,324 non-decider children).
2. Reads the pilot wide product parquet
   (`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`)
   for each partner side and projects to the partner's marginal-draw
   slice (`draw_other == 0`) — 77,310 rows per side.
3. For each pass, restricts decider baseline persons to
   `(is_decider == 1) AND (dgn == decider_gender)` — 2,577 male
   deciders / 2,577 female deciders.
4. Cross-joins the 2,577 deciders × 30 draws = 77,310 decider rows.
5. Applies the pilot W1 wage values (`hours`, `lhw`, `wage`, `yivwg`,
   `yem`, `loc4`, `loc_ruro`) onto the decider rows by joining on
   `(idhh, draw)` to the pilot product slice. 77,310 / 77,310 rows
   matched.
6. Adds **5,901 non-decider rows at draw=0** per pass (the
   other-partner-as-non-decider plus children).
7. Sets **`is_decider == 1` explicitly** on decider rows (HE-DEC).
8. Drops the four stray `ils_*` columns that survived the Stage-4
   filter and live on the production baseline (`ils_earns`,
   `ils_origy`, `ils_pen`, `ils_sicdy`). A fifth column from the
   audit list (`ils_earns_real`) lives only on the pilot wide
   parquet and is absent from the production baseline used here.
9. Writes per-partner draws parquet + `__drawsmeta.json` sidecar.

---

## 5. Per-partner inputs written

| File | Rows | Size | Status |
|---|---|---|---|
| `Data/pilot/nc_2016_couples/em_inputs/fr_pilot_2016_couples_male_partner_draws.parquet` | 83,211 | 11,358,841 bytes | **Created** |
| `…/em_inputs/fr_pilot_2016_couples_male_partner_draws__drawsmeta.json` | — | (JSON) | **Created** |
| `…/em_inputs/fr_pilot_2016_couples_female_partner_draws.parquet` | 83,211 | 11,362,591 bytes | **Created** |
| `…/em_inputs/fr_pilot_2016_couples_female_partner_draws__drawsmeta.json` | — | (JSON) | **Created** |

Per pass breakdown: 77,310 decider rows (`is_decider == 1`, draws
0..29) + 5,901 non-decider rows (`is_decider == 0`, draw=0).

---

## 6. `is_decider == 1` set explicitly

**Both passes:** yes. Adapter validation passed:

| Check | Male | Female |
|---|---|---|
| Decider rows (`is_decider == 1`) | 77,310 | 77,310 |
| Expected = 2,577 × 30 | 77,310 | 77,310 |
| Decider `draw` range | 0..29 | 0..29 |
| Stray `ils_*` columns | absent | absent |

HE-DEC: **NOT FIRED.**

---

## 7. Drawsmeta sidecar `id_multiplier == 1000` consistency

Both per-partner drawsmeta sidecars carry `id_multiplier = 1000`
(hard-set by the adapter). Both also carry `n_draws = 30`, `max_draw
= 29`, `household_type = "couples"`, and a wage-provenance note
linking the W1 draws to
`scripts/pilot/config/pilot_mincer_coefficients_v1.json`.

HE-DRAWSMETA: **NOT FIRED.**

---

## 8. Whether EUROMOD ran

**Partial.** The male pass was launched and ran into the runner's
deterministic-earnings-identity assertion at line 778 of
`scripts/enhanced/enh_RURO_euromod.py`, raising `ValueError` and
exiting with code 1. The female pass was not started after HE7
fired on the male pass.

No `combined_draws_em.parquet` was written for either pass.
EUROMOD's simulation step (the `system.run(...)` call at runner
line 237) was **NOT reached**, because the assertion at line 778
sits BEFORE the EUROMOD-call site. Strictly, *EUROMOD itself did
not run* — the runner's input-construction pipeline halted at the
yem identity assertion.

---

## 9. Exact commands run

**`euromod` import check (HE-EM-PKG, pre-launch):**

```powershell
$env:PYTHONNET_RUNTIME = "coreclr"
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" -c "import os; os.environ.setdefault('PYTHONNET_RUNTIME','coreclr'); import euromod; print('OK')"
# OK; exit 0
```

**Runner-module sanity check:**

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, r'U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced'); import enh_RURO_euromod; print('runner import OK')"
# runner import OK; exit 0
```

**Adapter:**

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" "U:\Desktop\Nizam_Hisham\MNL\scripts\pilot\export_pilot_euromod_inputs.py"
# Exit 0 — both per-partner inputs + sidecars written and validated.
```

**Male EUROMOD pass (HALTED at yem identity assertion):**

```powershell
$env:PYTHONNET_RUNTIME = "coreclr"; $env:PYTHONUNBUFFERED = "1"
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
  "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\fr_pilot_2016_couples_male_partner_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\male_pass" `
  *>&1 | Tee-Object -FilePath "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\male_pass\run.log"
# Exit 1 — HE7 fired.
```

**Female EUROMOD pass:** NOT LAUNCHED. Per amendment §16
"Halt → stop, write the report up to that point, await direction.
Do not work around."

---

## 10. Row counts before and after EUROMOD

**Before EUROMOD (adapter outputs, validated):**

| Frame | Rows | Decider rows | Non-decider rows |
|---|---|---|---|
| Male pilot draws parquet | 83,211 | 77,310 | 5,901 |
| Female pilot draws parquet | 83,211 | 77,310 | 5,901 |

**After EUROMOD:** N/A. No `combined_draws_em.parquet` was produced.

Runner internal state at the point of the assertion (read from the
runner log; not from a written artifact):

| Quantity | Value |
|---|---|
| FR_2016 template `em_input` rows | 26,560 (read by the runner's `_read_dataframe`) |
| Decider-merged rows after EUROMOD-template merge | ≈77,310 (each male decider × 30 draws merged with their template row) |
| Non-decider replicated rows | ≈5,901 × 30 = ≈177,030 |
| `yem` identity violations | **22,560 rows** with `max_diff = 0.000300` (the figure in the assertion message) |

The 22,560 figure exactly equals 752 violating template persons × 30
replicated draws. Approximately 752 distinct female-partner records
in the FR_2016 template carry a yem-imprecision ≥ 1e-6 between
`yem` and `yem00 + yemxp`. After 30-draw replication those become
22,560 assertion-violating rows.

---

## 11. Output paths

| Path | Status |
|---|---|
| `Data/pilot/nc_2016_couples/em_inputs/fr_pilot_2016_couples_male_partner_draws.parquet` | **Present** (11.4 MB) |
| `Data/pilot/nc_2016_couples/em_inputs/fr_pilot_2016_couples_male_partner_draws__drawsmeta.json` | **Present** |
| `Data/pilot/nc_2016_couples/em_inputs/fr_pilot_2016_couples_female_partner_draws.parquet` | **Present** (11.4 MB) |
| `Data/pilot/nc_2016_couples/em_inputs/fr_pilot_2016_couples_female_partner_draws__drawsmeta.json` | **Present** |
| `Data/pilot/nc_2016_couples/em_outputs/male_pass/run.log` | **Present** (assertion-failure log) |
| `Data/pilot/nc_2016_couples/em_outputs/male_pass/combined_draws_em.parquet` | **Absent** — runner exited before write |
| `Data/pilot/nc_2016_couples/em_outputs/male_pass/combined_draws_em__euromodmeta.json` | **Absent** |
| `Data/pilot/nc_2016_couples/em_outputs/female_pass/*` | **Absent** — pass not launched |
| `Results/NC_pilot/JMP_NC_pilot_stage5_euromod_build_report_v1.md` | **Present** (this report) |

Production parquets, the corrected pooled P3a estimation artifacts,
the M1-clean baseline, the pilot wide product parquet, the singles
production parquet — **all untouched** by this session.

---

## 12. Disposable-income output population

No `ils_dispy` output was produced. **The runner halted before the
EUROMOD `system.run(...)` call** (assertion at line 778 precedes the
EUROMOD invocation at line 929). No disposable-income column exists
for any pilot product alternative as a result of this session.

The pilot wide product parquet retains its pre-EUROMOD scaffold
state (no `ils_dispy_male` / `ils_dispy_female` columns; per the
Stage-4 build report, EUROMOD-dependent income columns were dropped
at Stage 4 and were always expected to be populated by Stage 5 —
which has now halted).

---

## 13. Halt condition status

| Halt | Condition | Status |
|---|---|---|
| **HE1** | In-place edit to production scripts | **NOT FIRED** — `git status` shows no `M`-flagged file in `scripts/enhanced/`, `scripts/maintenance/`, or under `scripts/enhanced/specifications/`. Only new files under `scripts/pilot/`, `Data/pilot/nc_2016_couples/em_inputs/`, `Data/pilot/nc_2016_couples/em_outputs/male_pass/run.log`, and this report. |
| **HE2** | `draw_joint` aliased to scalar `draw`, or wide parquet passed directly to EUROMOD | **NOT FIRED** — Strategy B respected; per-partner inputs carry scalar `draw ∈ {0..29}`. |
| **HE4** | `id_multiplier ≠ 1000` or sidecars disagree | **NOT FIRED** — both sidecars carry `id_multiplier = 1000`. |
| **HE5** | Singles production parquet altered | **NOT FIRED** — read-only access only. |
| **HE6** | Welfare / SA2 / promotion / M1-clean displacement / out-of-scope run | **NOT FIRED**. |
| **HE7** | `yem = yem00 + yemxp` deterministic identity violated | **FIRED on male pass.** 22,560 violations with `max_diff = 0.000300`. Source: female-partner-as-non-decider rows in the FR_2016 template have observed `yem` not equal to `yem00 + yemxp` to 1e-6; the runner replicates these across 30 draws; the assertion at line 778 catches the cumulative violation count. |
| **HE-DEC** | `is_decider == 1` not set on decider rows | **NOT FIRED**. |
| **HE-DRAWSMETA** | Missing / inconsistent drawsmeta sidecar | **NOT FIRED**. |
| **HE-EM-PKG** | `import euromod` fails | **NOT FIRED** with `PYTHONNET_RUNTIME=coreclr` (the runner sets this internally). |
| **HE-STAGE** | Any post-Stage-5 action attempted | **NOT FIRED** — female pass not launched after halt; no merge / GSUR / precompute / estimation / welfare / SA2 attempted. |

**One halt condition fired: HE7.**

---

## 14. Strategy-B architectural mismatch (HE7 root cause)

The amendment specifies Strategy B (per-partner long-format export
with the off-axis partner as a non-decider). The runner's
deterministic-earnings-identity assertion (lines 723–778) was
designed for production's "both partners as deciders" pattern.
Under production, lines 754–756 overwrite both partners'
`yem00`/`yemxp`/`yem` with `yem_computed = yem00_computed +
yemxp_computed` — by construction the identity holds. Under
Strategy B, only ONE partner is a decider per pass; the other
partner's `yem`/`yem00`/`yemxp` are inherited from the FR_2016
template at line 754's `baseline_*` branch, where the survey
recording precision is ±0.0001 EUR — not within the 1e-6 threshold.

**Three possible Strategy fixes (audit-only listing — do not
implement):**

A. **Tighten the non-decider triple in the adapter or pre-runner
   step.** The adapter could overwrite non-decider `yem00`/`yemxp`/
   `yem` with the deterministic identity recomputation
   `(min(lhw,35) × yivwg × WPM, max(lhw-35,0) × yivwg × WPM,
   their sum)` *before* the runner's assertion. This stays
   pilot-only (no production edit). It changes the non-decider
   partner's EUROMOD-reported earnings from her survey-observed
   `yem` to a yem-derived-from-lhw-and-yivwg approximation. For
   the female-partner-as-non-decider case in the male pass, that
   would replace her observed annual yem with a recomputed monthly
   ×12 figure that may differ from her observed survey income
   (because survey yem includes irregular pay, deductions, period
   adjustments that the simple identity misses). **This is a
   semantic shift, not just a numerical tweak**, and warrants an
   explicit amendment decision.

B. **Treat both partners as deciders in a single pass, with the
   off-axis partner pinned to her draw=0 values across all 30
   draws of the on-axis partner.** Drops back closer to the
   production pattern. Both partners get `is_decider=1`; both get
   `yem_computed = yem00_computed + yemxp_computed` written by
   the runner's deterministic-identity logic; assertion passes by
   construction. Requires the adapter to expand the off-axis
   partner to 30 rows (her observed baseline replicated 30
   times) rather than 1 row at draw=0. Increases per-pass row
   count from 83,211 to ≈155,000 (~2× current). This is the
   strategy variant the production runner was actually tested
   against.

C. **Loosen the assertion tolerance** (production-side change).
   Forbidden by HE1.

The audit recommends **option B as a minimal-blast-radius fix**:
no production edit; preserves the deterministic identity by
construction; produces a clean EUROMOD output where both partners'
disposable income depends on the on-axis partner's draw varying
while the off-axis partner is held at her observed baseline. This
is closer to the production behaviour the existing
`combined_draws_em.parquet` validates. It is a Strategy-B'
variant (Strategy B with deciders=both rather than deciders=one),
and it warrants a narrow amendment to the existing Stage 5
amendment.

---

## 15. What was not executed

- **EUROMOD female pass:** not launched (HE7 halt on male pass).
- **EUROMOD male pass `system.run(...)`:** not reached (assertion at
  line 778 sits before EUROMOD invocation at line 929).
- **Post-EUROMOD merge to the wide product parquet:** not authorized
  in this slice and not performed.
- **`is_chosen = is_chosen_joint` aliasing:** not authorized and not
  performed.
- **Chosen-first sorting of the wide parquet:** not authorized and
  not performed.
- **GSUR re-merge:** not authorized and not performed.
- **Precompute / estimation / welfare / SA2 / canonical promotion /
  M1-clean displacement:** not authorized and not performed.
- **Singles production parquet, frozen P3a YAML, corrected pooled
  P3a artifacts:** all untouched.
- **No `import euromod` failure response was needed** (the package
  imports successfully with `PYTHONNET_RUNTIME=coreclr`).
- Four transient temp scripts under `%LOCALAPPDATA%\Temp` (read-only
  schema / identity inspections) were deleted after use.

---

## 16. Next gate

**Yes — but not the merge slice yet.** The next gate is **a narrow
Stage-5 amendment v2** that resolves the Strategy-B architectural
mismatch (§14). Recommended: amendment §14 option B (Strategy B' —
both partners as deciders in each pass, with the off-axis partner
pinned to baseline values across all 30 draws). The amendment
should:

1. Restate Strategy B' explicitly (both partners `is_decider == 1`
   per pass; off-axis partner replicated to 30 draws at observed
   baseline values; the on-axis partner gets W1 draws on 1..29 and
   observed baseline on 0).
2. Carry over all other Stage-5 §16 halt conditions unchanged.
3. State why option A was rejected (semantic shift in
   non-decider yem from observed to recomputed).
4. Authorize a re-run of the male and female passes under
   Strategy B' on the existing adapter outputs (after the
   adapter is updated).
5. Re-state that the post-EUROMOD merge remains a SEPARATE later
   slice.

Only after that amendment is in hand may the build proceed to
re-launch EUROMOD.

The post-EUROMOD merge slice (separate document) remains the gate
*after* Stage 5 successfully produces both per-pass
`combined_draws_em.parquet` outputs.

---

## 17. Required final statements

- **HE7 fired on the male pass; build halted; female pass not
  started.** The runner exited with code 1 at the deterministic
  `yem = yem00 + yemxp` identity assertion. No `combined_draws_em.parquet`
  exists for either pass.
- **`euromod` import check PASSED** (with `PYTHONNET_RUNTIME=coreclr`,
  which the runner sets internally).
- **Python executable used:** `U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`
  (Python 3.12.2).
- **Both per-partner long-format inputs were created** and validated
  (83,211 rows each; 77,310 decider rows; 5,901 non-decider rows).
- **`is_decider == 1` set explicitly on decider rows in both passes.**
- **Both drawsmeta sidecars carry `id_multiplier == 1000`** identically.
- **EUROMOD did NOT run** (assertion fired before `system.run(...)`).
- **No GSUR merge, precompute, estimation, welfare, SA2, or
  promotion occurred.**
- **M1-clean 2016 remains the active baseline.**
- **The corrected pooled P3a track is unaffected.**
- **Next gate: a narrow Stage-5 amendment v2** to resolve the
  Strategy-B architectural mismatch (§14, §16) — NOT the
  post-EUROMOD merge slice (which remains gated on Stage 5
  completion).

---

*Status: NC pilot Stage 5 build report v1, produced 2026-05-22.
Authorization: `docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md`.
HALTED at HE7 on the male pass. M1-clean 2016 active. Frozen pooled
P3a spec and post-estimation track unaffected.*
