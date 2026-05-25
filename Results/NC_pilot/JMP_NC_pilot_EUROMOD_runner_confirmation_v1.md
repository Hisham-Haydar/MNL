# JMP NC Pilot — EUROMOD Runner Confirmation Audit v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: read-only audit. No EUROMOD run; no data modified; no
production code modified; no GSUR merge; no precompute; no estimation;
no welfare; no SA2; no promotion. M1-clean 2016 remains the active
baseline. Corrected pooled P3a track unaffected.

---

## 1. Audit verdict

**Stage 5 EUROMOD authorization is READY in principle, conditional on
one named amendment-style decision: the pilot must run EUROMOD on a
NEW long-format per-partner draws export derived from the pilot
marginals, NOT on the wide product parquet.** Option **B** of the
prompt's A/B/C/D taxonomy (a temporary long-format partner-level
export derived from the product parquet) is the correct strategy, with
two implementation notes that the next-slice authorization document
must pin down before any build action.

The recommended runner is the production wrapper
`scripts/enhanced/enh_RURO_euromod.py` (proven on FR_2016 in the
prior cycle — `combined_draws_em.parquet` already exists for the
diagonal 100-draw spec at `U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016`).
The wrapper expects a long-format `draws_df` with a scalar `draw`
column and one row per `(idperson, draw)`. The pilot's wide product
parquet does **not** fit that shape, so a **pilot-only long-format
adapter** is required to project the wide product into the runner's
expected schema.

There are **three named open items** the next-slice document must
resolve before any build action (see §17 HE-list and §20):

1. **Decider identification for the pilot.** The pilot wide parquet has
   no `is_decider` column. The fallback in the runner infers
   `is_decider = (max(draw) > 0)`. Under the pilot's per-partner
   marginal-draw export, every couple-member is a decider on its own
   30-draw axis, but the couple's two partners must BOTH be marked as
   deciders so that the wrapper's non-decider replication logic does
   not mis-classify them. This must be set explicitly in the adapter.
2. **`id_multiplier` configuration.** Production EUROMOD runs used
   `id_multiplier=1000` (derived from `max_draw=99`). With 30 marginal
   draws per partner, `_compute_id_multiplier` falls back to its
   minimum of 1000 — but the pilot's draws files should carry an
   explicit `__drawsmeta.json` with `id_multiplier=1000` to make the
   choice traceable. **Critical:** the male and female pilot drawsmeta
   sidecars MUST share the same multiplier (the wrapper raises if
   they disagree).
3. **Five `ils_*` columns survived the Stage-4 output-column drop.**
   The pilot parquet still contains `ils_earns`, `ils_origy`, `ils_pen`,
   `ils_sicdy`, `ils_earns_real` (not caught by the
   `ils_dispy`/`ils_dispy_em`/`i_`/`il_`/`tu_` prefix filter applied
   by the Stage 4 builder). These would be silently treated as
   "carry" columns by the wrapper since they are NOT in
   `EUROMOD_OUTPUT_PREFIXES` (`ils_`, `bho_`, `bch_`, `bdi_`, `bed_`,
   `bsa00_`, `tin_`, `tsc_`) → except `ils_*` IS in that prefix
   set, so the wrapper's input-filter at lines 871–877 would
   correctly drop them. They are flagged here so the pilot adapter
   notices and drops them explicitly before the EUROMOD call rather
   than relying on the wrapper's safety net.

If these three items are nailed in a narrow amendment, **Stage 5 is
ready**. If any cannot be resolved (especially #1), **authorization is
NOT ready**.

---

## 2. Authorization scope

This audit is read-only. Authorized by §19 of
`Results/JMP_NC_pilot_draw_joint_repointing_audit_v1.md` and §23 of
the Stage 1–4 build report. Outside scope: any EUROMOD run, any code
or data modification, any GSUR merge, any precompute, any estimation,
any welfare, any SA2, any promotion, any M1-clean displacement.

---

## 3. Files inspected

| File | Method |
|---|---|
| `Results/JMP_NC_pilot_stage1_4_build_report_v1.md` | Full read (prior turn) |
| `Results/JMP_NC_pilot_draw_joint_repointing_audit_v1.md` | Full read (prior turn) |
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md` | Full read |
| `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md` | Full read |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet` | Schema + bounded column reads (149 cols; 2,319,300 rows) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json` | Full read |
| `scripts/pilot/build_pilot_couples_product.py` | Full read (Stage 3–4 driver) |
| `scripts/enhanced/enh_RURO_euromod.py` | Full read (1229 lines; lines 1–120, 120–300, 420–720, 720–1000, 1000–1229) |
| `scripts/enhanced/enh_RURO_draws.py` | Targeted reads in prior turns (CLI + draw structure) |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Reads in prior turns (couples reshape, normalization fallbacks) |
| `scripts/RURO_euromod.py` | Header only (legacy / superseded by `enh_RURO_euromod.py`) |
| `src/mnl/integration/euromod.py` | Full read — thin `euromod` package wrapper used by `EuromodRunner` |
| `scripts/run_fr_2016_pipeline.ps1` | Read for Step 4 (EUROMOD invocation) and config block |
| `scripts/run_fr_2016_joint_only.ps1` | Read for Step 4 (EUROMOD invocation, enhanced variant) and config block |
| `U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet` | Schema only (518,724 rows; 600 cols; reference long-format draws file) |
| `U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet` | Schema only (168,319 rows; 600 cols) |
| `U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws__drawsmeta.json` | Full read (reference drawsmeta) |
| `U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet` | Schema only (1,087,300 rows; 343 cols; reference combined-EM output) |
| `U:/EUROMOD-STORAGE/Data/raw/FR_2016.txt` | Existence-only confirmation |
| `U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+/` | Directory existence-only confirmation |

All reads were schema- or column-bounded where possible. The pilot
wide parquet was read with explicit column subsets only. **No file
was modified by this session except this report.**

---

## 4. Pilot input parquet

Path: `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`

| Property | Value |
|---|---|
| Total rows | **2,319,300** (= 2,577 couples × 900 alternatives) |
| Total columns | 149 |
| Wide format | Yes — male/female fields side-by-side |
| Scalar `draw` column | **Absent** (per re-pointing audit §4) |
| `draw_male` (0..29) | Present |
| `draw_female` (0..29) | Present |
| `draw_joint = 30·draw_male + draw_female` (0..899) | Present |
| `is_chosen_joint`, `is_chosen_male`, `is_chosen_female` | Present |
| Legacy `is_chosen` / `chosen` | **Absent** |
| Bare identifiers (`idhh`, `idperson`, `idpartner`, `idfather`, `idmother`, `idorighh`, `idorigperson`) | Present — but **male-partner values only** (carried over from the male-side merge in `_build_product` lines 130–135 of the Stage-4 driver) |
| `_male` variants of Mincer/labor columns | `educL_male`, `educH_male`, `educM_male`, `educ3_male`, `hours_male`, `loc4_male`, `pexp_years_male`, `pexp_years2_male`, `wage_male`, `yem_male` |
| `_female` variants | identical key set with `_female` suffix |
| Bare `hours` / `wage` / `yem` / `lhw` / `loc4` columns | Present — also male-partner-side values (from the male-side carry) |
| Surviving `ils_*` columns | **5: `ils_earns`, `ils_origy`, `ils_pen`, `ils_sicdy`, `ils_earns_real`** — slipped past the Stage-4 prefix filter |

**Key implication for the EUROMOD runner.** The pilot parquet shape
is *not* the long-format `(idperson, draw)` shape the wrapper
consumes. To run EUROMOD, the pilot must be projected to the
runner's expected schema. This is the central plumbing question the
audit answers.

---

## 5. Required EUROMOD input schema

From `scripts/enhanced/enh_RURO_euromod.py`:

- **Function:** `run_euromod_for_draws(draws_df, micro_template_path, ...)`.
- **draws_df contract** (validated at lines 425–428):
  - **MUST** contain a scalar `"draw"` column. Hard `raise KeyError`
    if absent.
  - **MUST** contain a scalar id column (default `"idperson"`).
  - One row per `(idperson, draw)`. The wrapper takes `all_draws =
    sorted(draws_df["draw"].unique())` and `max_draw = max(all_draws)`.
- **Optional columns the wrapper consumes if present** (lines 430–460):
  `hours`, `wage`, `yem`, `yivwg`, `lhw`, `loc_ruro`, `isco1`,
  `job_id`, `hours_bin`, `wage_bin`, `baseline_job_id`,
  `loc_ruro_draw`, `loc_ruro_obs`.
- **Optional decider flag** (lines 484–493): `is_decider`. If absent,
  the wrapper falls back to inferring `is_decider = max(draw) > 0`
  per person.
- **`drawsmeta` sidecar** (lines 263–277): `__drawsmeta.json`
  alongside the parquet, providing `id_multiplier` (and any other
  metadata). If present and consistent across singles/couples
  drawsmeta, the wrapper uses it; otherwise it computes
  `id_multiplier = max(1000, 10**ceil(log10(max_draw+1)))`.
- **Microdata template** (`--microdata-template`): the EUROMOD
  baseline microdata file (`FR_2016.txt` in production); the wrapper
  reads it with `pd.read_csv(sep="\t")` and uses it as the canonical
  set of input columns.
- **EUROMOD release root** (`--euromod-root` / env
  `MNL_EUROMOD_ROOT`): path to the EUROMOD installation
  (production: `U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`).

**Internal pipeline inside `run_euromod_for_draws`**, per inspection
of the function body:

1. Read EUROMOD template (lines 408–420), capture
   `original_template_cols`.
2. Validate `draws_df` schema (lines 425–428).
3. Identify deciders / non-deciders (lines 484–496).
4. Merge deciders with draws and replicate non-deciders across all
   draws (lines 506–540).
5. Set `idhh_true`, `idperson_true` (lines 546–548).
6. Apply hours/wage/yem/yivwg overrides for **deciders only** (lines
   654–700).
7. Deterministic earnings identity (lines 723–780): set
   `yem00 = min(lhw, 35) * yivwg * WEEKS_PER_MONTH`,
   `yemxp = max(lhw - 35, 0) * yivwg * WEEKS_PER_MONTH`,
   `yem = yem00 + yemxp` for working deciders; assertion fails the
   run if `yem ≠ yem00 + yemxp`.
8. EUROMOD consistency fixes (lines 783–805): `bun=0`, `bsa=0`,
   `yemmy=12`, `lunmy=0` for working deciders.
9. Draw-specific IDs (lines 808–823): `idhh = idhh_true *
   id_multiplier + draw`; same for `idperson` and kin IDs.
10. Filter to EUROMOD input column set: `(template_cols ∪
    force_input_cols) \ output_cols`, where
    `EUROMOD_OUTPUT_PREFIXES = ("ils_", "bho_", "bch_", "bdi_",
    "bed_", "bsa00_", "tin_", "tsc_")` (line 86).
11. Run EUROMOD via the `euromod` Python package wrapped by
    `EuromodRunner` (lines 186–238).
12. Merge EUROMOD outputs back to the carry columns by direct
    zero-copy assignment with key-alignment verification on a 1000-row
    sample (lines 977–1037).
13. Sanity checks (`sanity_report_euromod`, lines 1116–1121).
14. Write `combined_draws_em.parquet` and the
    `combined_draws_em__euromodmeta.json` sidecar to `--scenario-dir`.

The wrapper is mature: it has explicit input/output schemas, key
alignment verification, deterministic earnings identity assertions,
metadata sidecars on input and output, and runtime sanity checks.

---

## 6. Missing or invalid columns before EUROMOD

The pilot parquet is **NOT** a valid EUROMOD input on its own. Missing
or invalid for the EUROMOD path:

| Missing / invalid | Status |
|---|---|
| Scalar `draw` column | Absent (HP-required by the wrapper) |
| `is_decider` column | Absent — wrapper would fall back to `max(draw)>0` inference, which is wrong without scalar `draw` |
| Baseline EUROMOD template columns (≈170 cols including all `dXXX`, `lXXX`, `yXXX`, `bXXX`, `tXXX`, `xXXX`, `kXXX`, `aXXX`, `iXXX` variables from `FR_2016.txt`) | Absent from pilot parquet entirely — the pilot retains 149 cols, mostly RURO-specific |
| Per-person merge keys (single `idperson`) | Bare `idperson` exists but holds MALE values only (149-column carry-through artefact); the female `idperson` lives in `idperson_female` if at all |
| 5 stray `ils_*` columns surviving the Stage-4 drop | Present (`ils_earns`, `ils_origy`, `ils_pen`, `ils_sicdy`, `ils_earns_real`) — should be dropped before EUROMOD |
| Wage and hours per partner | Present as `_male`/`_female` and as bare male-only carry — but **NOT** in EUROMOD's per-person `(idperson, draw, hours, wage)` shape |

**Confirmed: EUROMOD-dependent income columns were intentionally
dropped at Stage 4** (per the pilot metadata sidecar, 5 prefixes
removed: `ils_dispy`, `ils_dispy_em`, `i_`, `il_`, `tu_`). These
columns MUST be recomputed by EUROMOD on the pilot product
alternatives. The 5 surviving `ils_*` columns named above are
*non-disposable-income* `ils_*` variables that the Stage-4 filter did
not match; they should be dropped by the pilot adapter before the
EUROMOD call.

---

## 7. Draw-index handling for EUROMOD

The runner expects a **scalar `draw` column with values 0..N**. Two
hard rules apply:

1. **Do NOT globally alias `draw = draw_joint`.** The re-pointing
   audit explicitly forbids this (§15). The runner's
   `_compute_id_multiplier` would compute `id_multiplier = 1000` from
   `max_draw=899`, producing 30× larger ID arithmetic than the
   production multiplier. Worse, the wrapper's non-decider
   replication loop (lines 510–524) iterates over all 900 distinct
   `draw_joint` values, replicating non-deciders 900 times — but the
   pilot's couples-only scope has every couple-member as a decider on
   one of the two partner axes, so non-decider replication does not
   apply identically. Forcing `draw = draw_joint` would put
   the runner in a regime it was never tested for.

2. **Use partner-level marginal `draw_male` (0..29) and `draw_female`
   (0..29) as the runner's scalar `draw`.** Two separate runner calls
   — one per partner — each on its own long-format draws file with 30
   draws per person. This matches the runner's existing contract
   exactly. The pilot wide product parquet is reconstructed
   post-EUROMOD by joining the two partner disposable-income series
   onto `(idperson_male, draw_male)` and `(idperson_female,
   draw_female)`, then producing `ils_dispy_male` and
   `ils_dispy_female` as the wide-format income columns.

**Rationale for partner-level rather than joint-level:** EUROMOD
computes household-level disposable income, but at the
**single-person-axis** level the partner who is NOT being varied
should hold their observed baseline. Splitting into two runner
passes means each pass treats one partner as the decider and the
other as a non-decider (replicated across draws). The runner already
implements that non-decider replication via lines 510–524. So the
adapter only has to compose the right long-format inputs per pass.

A consequence to record: in the male pass, the female partner is a
non-decider held at her OBSERVED baseline; in the female pass, the
male partner is the non-decider at his OBSERVED baseline. **Neither
pass produces couple-level disposable income for the joint product
cell directly.** The joint disposable income comes from the *sum* (or
appropriate combination) of the two partner-side `ils_dispy_*` values
computed per partner-side pass — which is what the production
couples flow already does (per the production
`__mnlmeta.json`: `income_routing.couples_male = ils_dispy_male`,
`income_routing.couples_female = ils_dispy_female`). This is
internally consistent.

---

## 8. Required pilot adapter, if any

**YES — a pilot adapter is required.** Strategy **B** of the prompt's
A/B/C/D taxonomy: a temporary long-format partner-level export
derived from the product parquet, NOT a direct ingestion of the wide
product parquet.

The adapter is a new Python module (next-slice work, not
authorized here): `scripts/pilot/export_pilot_euromod_inputs.py`
(suggested name). At a high level it would:

1. Read the pilot wide product parquet (or, equivalently, the
   per-partner marginal draws maintained as intermediate state by
   Stage 2–3, if the executor chooses to preserve them).
2. For each partner side (male, female), build a long-format draws
   frame with:
   - One row per `(idperson_partner, draw_partner)`, 30 draws/person.
   - Columns: `idperson`, `idhh` (couple-level household ID), `draw`
     (= `draw_male` or `draw_female`), `hours`, `wage`, `yem`,
     `yivwg`, `lhw`, `loc_ruro`, `loc4`, `is_decider = 1`.
   - Plus, on each row, the partner's observed Mincer covariates
     and the **other-partner-side household carry** (non-decider
     replication input).
3. Write each frame as a parquet under
   `Data/pilot/nc_2016_couples/em_inputs/` with a matching
   `__drawsmeta.json` carrying `id_multiplier=1000`, `n_draws=30`,
   `max_draw=29`, `household_type` = `"couples"`, source-set tag.
4. Drop the 5 surviving `ils_*` columns.
5. Ensure `is_decider == 1` for both partners on their respective
   pass (the production runner falls back to inferring deciders if
   the column is absent, but the inference rule `max(draw) > 0` is
   unreliable when partners have draw=0 baseline rows).

The adapter is itself a self-contained, testable Python module
(estimated <300 lines) and lives under `scripts/pilot/`. No
production code is touched.

---

## 9. EUROMOD runner location

**Confirmed: `scripts/enhanced/enh_RURO_euromod.py`** is the runner
script. (The legacy `scripts/RURO_euromod.py` at the repo top level
has the same docstring banner but was superseded by `enh_*`; the
enhanced variant is the version invoked by the FR_2016 joint pipeline
script `scripts/run_fr_2016_joint_only.ps1` line 411.)

- **Function entry point:** `run_euromod_for_draws()` at line 346.
- **CLI entry point:** `main()` at line 1149 with
  `parse_args()` at line 1135.
- **EuromodRunner wrapper:** `EuromodRunner` class at line 186, which
  imports the `euromod` Python package locally (line 191) and
  instantiates `em.Model(em_root)`.
- **`euromod` package access:** indirectly via
  `src/mnl/integration/euromod.py::ensure_euromod_package()` — but
  `enh_RURO_euromod.py` imports `euromod` directly inside the
  EuromodRunner constructor, so the `src/mnl` wrapper is **not**
  used by the active runner. Confirmation that the EUROMOD Python
  package is installed in the venv is a build-step prerequisite (the
  audit did not import it to avoid side effects).
- **EUROMOD release root:** auto-resolved by `_euromod_root()` at
  line 158 to
  `U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`
  (directory existence confirmed in §3); override via
  `--euromod-root` or env `MNL_EUROMOD_ROOT`.

The runner has been **validated on FR_2016 in production**: the
output `U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet`
exists with 1,087,300 rows × 343 columns from a 99-draw
(singles+couples diagonal) run. The pilot rerun uses the SAME runner
on a NEW per-partner long-format input.

---

## 10. Exact command template

Two passes (one per partner), each a separate invocation. Pilot-only
paths; nothing overwritten.

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

**Female pass:** identical, with `_male` replaced by `_female`:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_inputs\fr_pilot_2016_couples_female_partner_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\Desktop\Nizam_Hisham\MNL\Data\pilot\nc_2016_couples\em_outputs\female_pass"
```

Notes on flag values (consistent with the production pipeline scripts):

- `--euromod-system FR_2015` — **system year = data year − 1**, per
  `run_fr_2016_pipeline.ps1` line 31 and
  `run_fr_2016_joint_only.ps1` line 33. The system is the policy
  year applied to the FR_2016 microdata.
- `--euromod-dataset FR_2016` — the dataset code. Production used
  `${COUNTRY}_$YEAR` = `FR_2016`.
- `--singles-draws` flag name is a misnomer for the pilot — the
  runner accepts it as the *primary* draws file and processes any
  long-format draws frame on it. (The `--couples-draws` flag exists
  but is not used for the pilot since each pass is one partner only.)
- The `--scenario-dir` is pilot-specific. Production used
  `U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016`; the pilot
  must write under `Data/pilot/nc_2016_couples/em_outputs/`.

---

## 11. Expected output path

The runner writes one combined output per pass:

- Male pass: `Data/pilot/nc_2016_couples/em_outputs/male_pass/combined_draws_em.parquet`
- Female pass: `Data/pilot/nc_2016_couples/em_outputs/female_pass/combined_draws_em.parquet`

Each writes a metadata sidecar
`combined_draws_em__euromodmeta.json` alongside (lines 310–343 of
the runner) carrying `system`, `dataset`, `n_rows`, `n_draws`,
`id_multiplier`, `carried_columns`, `timestamp`.

After both passes complete, a separate **next-slice merge step**
(NOT this audit, NOT Stage 5) joins the two outputs back onto the
pilot wide product parquet by `(idperson_partner, draw_partner)` →
`ils_dispy_partner` for each side, producing the post-EUROMOD wide
parquet at:

- `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__post_em.parquet`

with `ils_dispy_male` and `ils_dispy_female` populated for all
2,319,300 rows. The audit recommends this as a separate authorized
slice (Stage 6 / merge), not bundled into Stage 5.

---

## 12. Expected output schema

From the reference 99-draw FR_2016 combined output
(`combined_draws_em.parquet`, 343 columns):

- All 343 columns of the production EUROMOD output schema.
- Key population-relevant outputs include `ils_dispy` (disposable
  income), `ils_earns`, `ils_tax`, `ils_ben`, `ils_taxin`, `ils_sicee`,
  `ils_sicer`, all `bXXX` benefits, all `tinXXX` taxes, all `bsaXXX`
  social assistance fields.
- Carry columns include `idhh_true`, `idperson_true`, `draw`,
  `is_decider`, plus the input columns from the draws file
  (`hours`, `wage`, `yem`, `lhw`, `loc4`, `is_chosen`,
  `log_q_*`, RURO metadata).
- ID columns `idhh` and `idperson` are draw-multiplied
  (`idhh_true * id_multiplier + draw`).

For the pilot, each per-partner pass output will have a similar
schema (≈343 columns) but with `n_draws=30` and rows ≈ 30 *
(2,577 + N_nondeciders_per_couple). The exact row count is bounded
by the wrapper's decider+non-decider replication arithmetic (§13).

---

## 13. Expected row count

**Per-partner pass (estimated, requires confirmation in the adapter
slice):**

- 2,577 couples × 30 draws × (1 decider + N_other_members) per
  household. The number of "other members" varies per household
  (often 0 for a pure two-adult couple; up to ~5 if children are
  present and replicated). In the FR_2016 production diagonal run
  the couples draws file had 518,724 rows = 2,577 × 100 × ~2.0 (i.e.
  on average ~2 records per couple-draw because both partners exist
  on the long-format file but only one varies at a time? — actually
  in the production long-format file BOTH partners appear with
  their own (idperson, draw) keys, hence ~2.0×).
- The pilot per-partner pass extracts only ONE partner as the
  decider (with 30 draws) and the OTHER partner as a non-decider
  baseline (replicated to 30 rows). So each pass roughly:
  **2,577 couples × 30 draws × (2 adult partners + N_children
  replicated to 30 draws each) ≈ 154,620 rows + non-decider rows**.

The exact number is small and trivially computable in the adapter;
the audit confirms it is **well under the production 518,724** and
should pose no scaling problem.

**Post-EUROMOD merge to pilot wide parquet:**

- Target row count: **2,319,300** (one row per pilot product
  alternative). HE3 requires that `ils_dispy_male` and
  `ils_dispy_female` are populated on every one of these rows after
  the merge.

---

## 14. Expected wall-time and memory risk

The reference FR_2016 production diagonal run produced
`combined_draws_em.parquet` (1,087,300 rows × 343 cols, ≈3 GB on
disk uncompressed) on the same hardware. **No published wall-time
record was located** in any of the inspected files — `Results/_step2_euromod.log`
exists but was not read in this audit; the run.ps1 scripts log timing
but the actual log files are not in the repo.

**Estimated pilot wall time** (multiplicative scaling, very rough):

- Per-partner pass: ~30 draws × 2,577 couples ≈ 77,310 decider
  records + ~5–10× as many non-decider rows. Compared to the
  production combined run's 1,087,300 rows, each pilot pass is
  roughly 10–20% the scale. **Provisional estimate: 30 min – 2 h per
  pass**, with substantial variance depending on EUROMOD policy-rule
  evaluation cost per row. Two passes ⇒ **1 h – 4 h total**.
- This is a *bounded* estimate; the pilot's first objective is to
  *measure* the actual wall time.

**Memory risk:** the runner uses zero-copy direct assignment after
key-alignment verification (lines 977–1037) to avoid intermediate
copies on the merge-back. The production diagonal run succeeded; the
pilot pass is smaller; no specific memory risk is anticipated.
However, the `_compute_id_multiplier` arithmetic at
`idhh = idhh_true * 1000 + draw` would yield IDs up to ~10^7 for
typical `idhh_true` values — well within int64 capacity.

---

## 15. Logging and checkpoint strategy

The production runner already logs extensively (`logging.info` at
~80 call sites; debug summary at lines 836–852 with yem/lhw/yivwg
statistics; sanity-check failure raises at line 1121). The pilot
should:

- Redirect runner stdout/stderr to per-pass logs:
  `Data/pilot/nc_2016_couples/em_outputs/male_pass/run.log` and
  `…/female_pass/run.log`.
- Save the runner's metadata sidecar
  (`combined_draws_em__euromodmeta.json`) per pass.
- Compute and persist (in a small JSON) the wall time per pass and
  the row-count breakdown.

**Chunking:** the production runner does NOT chunk internally —
`run_euromod_for_draws` is one EUROMOD call on the full merged
frame. For the pilot's ≤200,000-row per-pass input, **no chunking is
needed**. (Chunking would be required only if a per-pass input
exceeded EUROMOD's in-memory limits — not the case here.)

**Checkpointing:** running the two passes as separate processes is
itself a checkpoint. If the male pass succeeds and the female pass
fails, the male output is preserved and only the female pass is
re-run. Both passes write `__euromodmeta.json` sidecars that record
completion; a small driver wrapper around the two `python …`
invocations can short-circuit if both sidecars are already present.

---

## 16. Post-EUROMOD merge and chosen-row requirements

The post-EUROMOD merge is a **separate next-slice operation** —
authorized in a different document, NOT in this Stage-5
authorization. The audit confirms the requirements (do not implement):

1. **Preserve `draw_male`, `draw_female`, `draw_joint`** on the
   post-EUROMOD wide parquet. The two per-pass EUROMOD outputs are
   joined on `(idperson_male, draw_male)` and
   `(idperson_female, draw_female)` respectively; the joint key
   `draw_joint` is reconstructed from the two partner-side draw keys
   via the existing formula `draw_joint = 30·draw_male + draw_female`.
2. **Add a synthetic `is_chosen` column equal to `is_chosen_joint`**
   before precompute. This resolves the chosen-column priority chain
   in `estimation_utils.py` (lines 780, 1156) and the ≈15 sites in
   `RURO_post_estimation_styled.py`. (Per the re-pointing audit §14.)
3. **Sort each (idhh, year_tag) group so `draw_joint == 0` is the
   first row in its group**, before passing to the precompute step.
   This resolves the implicit position-0 chosen-row assumption in
   `estimation_engine.py:380`. (Per the re-pointing audit §9.)
4. **Drop the 5 stray `ils_*` columns from the Stage-4 pilot
   parquet** (`ils_earns`, `ils_origy`, `ils_pen`, `ils_sicdy`,
   `ils_earns_real`) before EUROMOD, OR rely on the runner's
   `EUROMOD_OUTPUT_PREFIXES` filter (which DOES include `ils_`) to
   strip them at the input-schema-build step. Either is acceptable;
   the audit recommends explicit drop in the adapter for traceability.

**Validation of EUROMOD completeness after merge** (HE3 check):

- After the post-EUROMOD wide parquet is built, check
  `df[["ils_dispy_male","ils_dispy_female"]].notna().all(axis=None) == True`
  and `df[["ils_dispy_male","ils_dispy_female"]].gt(0).any()` (no
  all-NaN, no all-zero income column).
- Verify row count `== 2_319_300`.
- Verify singles parquet rows still `== 500_700` (HE5).
- Verify `is_chosen_joint == 1` selects exactly 2,577 rows (HE2).

---

## 17. Halt conditions for Stage 5

The re-pointing audit's HE1–HE7 from §17 carry forward unchanged.
Restated with EUROMOD-specific tightening:

| Halt | Condition |
|---|---|
| **HE1** | Any in-place edit to `scripts/enhanced/enh_RURO_euromod.py` or any other production script. Pilot adapter and pilot output dirs only. |
| **HE2** | EUROMOD inputs exported from the wide pilot product parquet directly (i.e. presenting `draw_joint`/`draw_male`/`draw_female` as scalar `draw`). The runner halts on `KeyError("draws_df must contain a 'draw' column")` from line 426; if the adapter alias-maps `draw_joint → draw`, **manually halt** — this is the forbidden Strategy A globally. |
| **HE3** | Post-EUROMOD merge produces any row with NaN or unset `ils_dispy_male` or `ils_dispy_female` (couples disposable-income population check). Halt before precompute. |
| **HE4** | `_compute_id_multiplier` returns a value other than 1000 for the 30-draw pilot, or the two per-partner drawsmeta sidecars carry different multipliers (the wrapper raises at line 1190; do not work around). |
| **HE5** | Any change to the singles production parquet (`fr_p3a_gsurv2_estimation_ready__singles.parquet` row count ≠ 500,700). |
| **HE6** | Any attempt to compute welfare, issue SA2, promote a pilot output, displace M1-clean 2016, or run beyond couples-2016 scope. |
| **HE7** | The `yem = yem00 + yemxp` deterministic identity assertion at line 776 of the runner raises. This indicates Mincer-derived wages were not consistently propagated to `yivwg`/`lhw`. Halt and audit the adapter's wage column. |
| **HE-DEC** | Decider mask is NOT explicitly set for both partners on each pass. The runner falls back to `is_decider = max(draw)>0` inference, which is wrong when the non-decider partner is replicated across draws but has only `draw=0` rows on his/her side. Halt unless the adapter sets `is_decider == 1` explicitly per pass. |
| **HE-DRAWSMETA** | The two per-partner drawsmeta sidecars are absent or carry inconsistent `id_multiplier`. Halt; the wrapper rejects this at line 1190. |
| **HE-EM-PKG** | The `euromod` Python package is not importable in the venv (the wrapper raises at line 192). Confirm `python -c "import euromod"` succeeds before launching. |

The five-item list named in §1 of this audit reduces to four when
HE2/HE-DEC are pinned in the adapter and HE-DRAWSMETA is set by the
adapter's drawsmeta-writing step. HE-EM-PKG is an environment check
the next-slice document must call out.

---

## 18. Whether Stage 5 authorization is now ready

**Conditional yes.** Stage 5 authorization is READY contingent on
producing a narrow next-slice amendment (suggested name:
`docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md`) that pins down:

1. The pilot adapter design (per §8) — including explicit
   `is_decider=1` flag on every adapter output row.
2. The per-partner drawsmeta sidecar contents (per §17 HE-DRAWSMETA).
3. The pilot output directory layout (per §11).
4. The decision to run two passes (one per partner) under the
   recommended Strategy B (per §7).
5. The choice of EUROMOD system code: `FR_2015` (data year − 1, per
   the production pipelines), confirmed.
6. HE1–HE7 + HE-DEC + HE-DRAWSMETA + HE-EM-PKG as Stage-5 halt
   conditions (per §17).
7. Confirmation that the `euromod` Python package is installed and
   importable in the project venv (HE-EM-PKG environment check).

Once that amendment is in hand and the package check succeeds, the
build can proceed: (a) write the adapter under
`scripts/pilot/export_pilot_euromod_inputs.py`, (b) generate the two
per-partner long-format draws frames with drawsmeta sidecars, (c)
launch the two runner passes under the exact commands of §10, (d)
write the per-pass `combined_draws_em.parquet` and metadata sidecars
under the §11 paths, (e) write a Stage-5 build report.

The audit recommends **doing the adapter design as a separate
read-only design document first** (before any code is written),
because the adapter is the single most consequential new artefact in
the Stage 5 surface and warrants its own focused review.

---

## 19. What was not executed

- No EUROMOD run.
- No data modified.
- No production code modified.
- No GSUR merge.
- No precompute.
- No estimation.
- No welfare.
- No SA2.
- No promotion.
- No singles parquet touched.
- The `euromod` Python package was NOT imported in this session (to
  avoid side effects from EUROMOD's `coreclr`/`pythonnet` runtime
  setup). Whether it is importable in the venv is the HE-EM-PKG
  environment check that the next-slice document must call out.
- Two transient temp scripts (`check_em_artifacts.py`,
  `check_pilot_cols.py`) were created under `%LOCALAPPDATA%\Temp` for
  schema-only read-only parquet inspections; both were deleted after
  use.

---

## 20. Immediate next task

**Author** `docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md` — a
narrow next-slice authorization document covering the §18 items 1–7.
Following the cadence established by the Stage 1–4 amendment, that
document:

- Restates §17 HE-list as authorized halt conditions for Stage 5.
- Pins the §8 pilot adapter design (its inputs, outputs, drawsmeta
  contract, and the explicit `is_decider=1` flag).
- Pins the §10 exact command template (with `--euromod-system FR_2015`
  and the pilot output directory layout of §11).
- Pre-decides §17 environment confirmations (EUROMOD package
  importable; EUROMOD release directory present; FR_2016.txt
  template present — the last two were confirmed in §3 of this
  audit).
- States that the **post-EUROMOD merge slice is a DIFFERENT future
  document** (not bundled into Stage 5).

**Independently:** verify that `python -c "import euromod"`
succeeds in the project venv (HE-EM-PKG); this is the only
runtime-environment check the audit could not perform without
side effects.

---

**Required final statements:**

- **No EUROMOD was run.**
- No data was modified. No production code was modified. No GSUR
  merge was run. No precompute was run. No estimation was run. No
  welfare was computed. No SA2 was issued.
- M1-clean 2016 remains the active baseline.
- The corrected pooled P3a track is unaffected.
- Recommended Stage-5 strategy: **B** — a pilot adapter that exports
  two per-partner long-format draws files derived from the pilot
  product parquet; EUROMOD consumes those long-format files via the
  existing `scripts/enhanced/enh_RURO_euromod.py` runner with
  `draw ∈ {0..29}` per partner; the wide product parquet is **not**
  passed to EUROMOD.
- Stage 5 authorization is READY conditional on a narrow next-slice
  amendment that pins down the adapter design, the drawsmeta
  sidecar contract, the explicit `is_decider=1` setting, and the
  `euromod`-package import check.

---

*Status: read-only EUROMOD-runner confirmation audit v1. Produced
2026-05-22. Authorization: §19 of the re-pointing audit and §23 of
the Stage 1–4 build report. No EUROMOD run; no data or production
code modified; M1-clean 2016 remains active; corrected pooled P3a
track unaffected. Next document: Stage 5 amendment per §20.*
