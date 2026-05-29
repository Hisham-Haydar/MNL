# B-pool pipeline — `scripts/bpool/`

Read-only walkthrough: how the scripts in `scripts/bpool/` work, in execution order, **and** where their inputs come from. Confirms that the bpool stage does **not** read raw EUROMOD `.txt` micro-data and does **not** clean / filter households — that all happens **upstream**. The bpool stage consumes pre-cooked parquets, builds alternative-expanded choice sets, prices them through EUROMOD, and writes engine-ready parquets for the RURO MNL estimator.

---

## TL;DR — the questions you asked

> *"It relies on data already produced elsewhere, it doesn't read the raw data?"*
**Correct.** The bpool scripts never open `FR_2015_a2.txt` / `FR_2016_a3.txt` / `FR_2017_a2.txt` directly. They read **two** classes of pre-cooked parquets:
1. **Per-year individual rosters** `<storage>/Data/processed/fr/{year}/fr_{year}.parquet` — full HH rosters in EUROMOD-input schema, built by `scripts/enhanced/enh_france_data_prep.py` from the raw `.txt`. Used in Stage 2 (the long-format expand).
2. **Stacked pooled "GSURv2 estimation-ready" parquets** `<storage>/Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__{singles,couples}.parquet` — the cleaned, filtered, harmonised, year-stacked deciders+covariates pool. Built by `enh_france_data_prep → enh_RURO_prep_mnl_basic → multi_year/m1_*` upstream. Used in Stage 1 (the actual draws).

> *"It doesn't clean the data itself?"*
**Correct.** Filtering (age 18–65, `les ∈ {3,5,7}`, opposite-sex couples only, wage bounds `[2, 170]`, hours bounds `[10, 70]`, retirement/disability removal, etc.), wage reconstruction, head/partner/decider identification, child-count construction, region recoding, CPI deflation, year stacking and `stacked_hh_uid` assignment, GSUR (external gender×age×region unemployment-rate) merge — **none** of that happens in `scripts/bpool/`. The bpool stage **only** simulates alternatives, re-prices them, and re-shapes the output for the estimator.

> *"Is the number of draws hardcoded?"*
**Yes.** `N_DRAWS = 100` (singles) and `PRODUCT_SIZE = 30 → N_JOINT = 900` (couples) are module-level constants — no CLI override. Same for `π0 = 0.10`, the D1 mixture weights, the empirical loc4 frequencies, the `WEEKS_PER_MONTH = 52/12` and `FRANCE_STANDARD_HOURS = 35` accounting constants, the CPI φ vector, and the EUROMOD system pairing table. The **master seed** is the only knob exposed via `--seed` (default 2026). See §6 for the full hard-coded-knob inventory.

---

## 1. Where the bpool input parquets come from (upstream story)

The bpool stage starts from data that has already been through a long upstream chain. To make this report self-contained, here is the full path raw → bpool input.

### 1.1 Raw EUROMOD micro-data

For France, EUROMOD ships per-year tab-delimited text files in `<storage>/Data/FR/`:

```
FR_2015_a2.txt    (122 input columns — see _RAW_SCHEMA[2015])
FR_2016_a3.txt    (124 input columns — see _RAW_SCHEMA[2016])
FR_2017_a2.txt    (128 input columns — see _RAW_SCHEMA[2017])
```

These are individual-level (one row per person), with EUROMOD-standard columns (`idhh, idperson, idfather, idmother, idpartner, dag, dgn, dms, deh, drgn1/2/ru/ur, les, lhw, lhw_f, yivwg, yem, yem00, yemxp, ils_*` etc.). The exact column sets per year are reproduced as hard-coded lists `_RAW_SCHEMA` inside `build_bpool_precompute.py` / `run_bpool_euromod_chunk.py` and used as a strict superset contract (G1 gate).

### 1.2 Per-year cleaning → `fr_{year}.parquet`

`scripts/enhanced/enh_france_data_prep.py` does the heavy cleaning. For each `year ∈ {2015, 2016, 2017}` (script driver: `enh_france_data_prep.py --year <YYYY>`):

1. `load_fr_txt(...)` — `pd.read_csv(FR_{year}_aN.txt, sep="\t")`.
2. `clean_harmonize_fr(...)`:
   - Snapshot baseline labour-input columns as `lhw_base, yivwg_base, yem*_base`.
   - **Run baseline EUROMOD** (`em.Model(model_dir)`, `system.run(df, dataset)`) using the *next year's* system (`FR_{year-1}`) on this year's raw data → recovers `ils_dispy` and all `ils_*` components on the OBSERVED-earnings baseline.
   - Identify household head via `tu_household_fr_HeadID == idperson`, partner via `idpartner` linking back to head, and `ruro_decider = head or partner`.
   - `create_income_columns(...)` — build `income_employment, income_market, benefit_retire_disab, benefit_ub_sa, replacement_income_total, ils_disp`.
   - `correct_labor_status(...)` — reclassify `les` (1=farmer, 2=self-employed, 3=employee, 4=pensioner, 5=unemployed, 6=student, 7=inactive, 8=sick, 9=other, 10=family worker) using income thresholds (`emp ≥ 100, yse ≥ 300, hrs ≥ 10, yse/yem ≥ 4 ⇒ SE-dominated`). Written to `les_enforced`.
   - `compute_wage_for_ruro(...)` — reconstruct hourly wage `wage_final` from the DRD annualised-monthly `yem*` + `lhw` + months-worked (`liwmy`/`liwftmy+liwptmy`/`yemmy`). Prefers `yivwg` if it sits in `[2, 170]` and is consistent, else falls back to the implied wage. `wage_clipped_flag` records clipping.
3. `separate_household_types(...)` — couples = HH with exactly 1 head **and** ≥1 partner; singles = 1 head, 0 partners.
4. `stepwise_filter_households(...)` — sequential household-level filters (logged stepwise):
   - **Age (Head)**: `dag ∈ [18, 65]`.
   - **Education (Head)**: `dec == 0` (not currently in education).
   - **Retirement/Disability**: drop HH where any member has `byr + pdi + poa + psu > 0`.
   - **Allowed LES (Deciders)**: head AND partner must have `les_enforced ∈ {3, 5, 7}` (employee, unemployed, inactive). **Farmers (1) and self-employed (2) are intentionally excluded** for the French case.
   - **Age (Partner)** and **Education (Partner)** for couples.
   - **Opposite-Sex Couples Only**: keep only HH with exactly 1 male + 1 female decider (`dgn==1` and `dgn==0`).
   - **Other Members**: drop HH where any non-decider working-age adult has meaningful labour income or is not student/disabled.
   - **Hours capping + Wage filter**: cap `lhw > 70 → 70`; floor `5 < lhw ≤ 10 → 10`; `lhw ≤ 5` and decider → reclassify to `les=7` (inactive) and zero out income. Drop HH whose `wage_unbounded` falls outside `[2, 170]`.
5. Child counts by age band (`num_children_0_3, 3_6, 6_11, 11_17, total`) — built from `idfather`/`idmother` links restricted to `dag ∈ [0, 17]`.
6. Stamp `data_year, system_year, input_year`; write to **`<storage>/Data/processed/fr/{year}/fr_{year}.parquet`** (this is the file Stage 2 of bpool reads as "the roster") plus separate `..._singles.parquet` and `..._couples.parquet` (deciders + chosen-row covariates only).

These parquets are stored under EUROMOD-STORAGE/Data/processed/fr/`{year}` and indexed by `_bpool_paths.FR_PARQUETS[year]`.

### 1.3 Old per-year draws + EUROMOD pricing + MNL prep

For the *original* (pre-bpool) design, the chain continued through:

- `enh_RURO_draws.py` — old per-decider draws: `π0=0.10`, hours `Uniform[5, 70]`, wage `Uniform[2, 170]`, occupation either "fixed" (copy observed) or "empirical" (stratum frequencies). Default `N_DRAWS = 99`. Wrote `*_draws.parquet`.
- `enh_RURO_euromod.py` — passed the draws through EUROMOD (same `EuromodRunner` the bpool stage now reuses) → priced each alternative.
- `enh_prepare_FR_gsur.py` — merged in external GSUR (gender × age × region external unemployment rate) — this gives the engine the **external** market-tightness signal that protects against endogeneity.
- `enh_RURO_prep_mnl_basic.py` — applied the canonical MNL normalisation: `TOTAL_LEISURE_HOURS = 80, leisure = clip(80 − hours, 1), c_scale = mean(consumption), l_scale = min(positive chosen leisure)`, computed `c_norm/l_norm/log_c_norm/log_l_norm`, restricted to deciders only, separated singles vs couples. Wrote `fr_{year}_RURO_mnl_GSURv2_y*__singles/couples.parquet`.

This is the same normalisation the bpool stage's **Stage 6** (`harmonise_bpool_engine_ready.py`) repeats — verbatim — so the bpool engine-ready output is on the same footing as the per-year files.

### 1.4 Multi-year stacking (Stage M1) → the pooled GSURv2 pool

`scripts/multi_year/m1_*.py` (driven by `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml`):

1. `m1_stack_years.py` — concatenates per-year MNL parquets (2015, 2016, 2017) and assigns:
   - `year_tag = {2015→1, 2016→2, 2017→3}` (from the YAML).
   - `stacked_hh_uid = year_tag · B + idhh` with `B = uid_base = 10^11` (UID base in the YAML).
   - `stacked_person_uid = year_tag · B + idperson`.
2. `m1_harmonise_cpi.py` — applies HICP-FR deflation to all monetary columns (`ils_dispy, ils_earns, yem, yse, ypen, ypt, ils_ben`) using `Data/external/cpi_hicp_fr_harmonisation.csv`. Writes `ils_dispy_real` and analogous `_real` columns.
3. `m1_add_cluster_key.py` — sets `cluster_id = idorighh` for clustered standard errors.
4. `m1_validate.py` / `m1_identity_validation.py` — V1–V9 invariant checks (row counts, year overlap counts, sex stability ≥ 99.9%, age progression ≥ 99.5%, HH continuity ≥ 97%, etc.).

Output (under `<storage>/Data/processed/fr/pooled/`):

```
fr_p3a_gsurv2_estimation_ready__singles.parquet
fr_p3a_gsurv2_estimation_ready__couples.parquet
stage_m1_meta.json
```

These two parquets are **the input to the bpool stage**. They contain, per `stacked_hh_uid`:
- The decider rows in wide format (suffixed `_male/_female` for couples).
- All demographic / education / region covariates (`dgn, educ3, educL/M/H, pexp_years[2], age_norm[2], reg_nuts1_1..8, drgur/drgmd/drgru, n_children`).
- The observed alternative (`draw==0`) with `hours, wage, loc4, working` for singles and `_male/_female`-suffixed for couples.
- External `gsur` (singles), `gsur_male`, `gsur_female` (couples) — the GSURv2-opportunity-year-aligned market unemployment rate.
- The CPI-deflated baseline `ils_dispy_real, consumption, log_c, log_c_norm, c_norm, leisure, l_norm, log_l, log_l_norm` (these get **dropped** and rebuilt later — they reflect the OLD draws design, not the new D1+W1 alternatives).
- Year indicators `year_2015_indicator, year_2017_indicator` (2016 = base).
- Cluster key `idorighh` / `cluster_id`.

The provisioning label embedded in the upstream metadata is `gsurv2_opportunity_year_aligned`, which the bpool stage records and inherits unchanged.

So when the bpool stage starts, all the hard data work (raw read, EUROMOD baseline, head/partner identification, filtering, wage reconstruction, child counts, year stacking, CPI deflation, GSUR merge) is already done. The bpool stage's job is **alternatives generation + re-pricing + estimator-ready shaping**.

---

## 2. Execution order — the bpool pipeline itself

| # | Script | What it produces |
|---|---|---|
| 0 | `_bpool_paths.py` | Shared path resolver (imported by every other script). |
| 1 | `build_bpool_singles.py` | `fr_p3a_bpool_d1w1__singles.parquet` — 100 simulated alts + 1 chosen per single-decider HH. |
| 1' | `build_bpool_couples.py` | `fr_p3a_bpool_d1w1__couples.parquet` — 30×30=900 simulated alts + 1 chosen per couple HH. |
| 1″ | `run_bpool_draws.py` | Orchestrates 1 + 1' in sequence, then runs V1–V5 invariant checks. |
| 2 | `build_bpool_precompute.py` | Per-year individual-level **long** files with drawn hours/wage merged onto the full HH roster; computes canonical earnings split (`yem00/yemxp/yem`). 6 files (3 years × {singles, couples}). |
| 3 | `run_bpool_euromod_chunk.py` (× many, launched by `launch_chunks.ps1`) | One chunk parquet per draw band → `chunks/fr_p3a_bpool_priced__{year}__{mode}__cN.parquet`. Calls EUROMOD via `EuromodRunner`. (`run_bpool_euromod.py` is the older in-process equivalent.) |
| 4 | `assemble_bpool_priced.py` | Concatenates chunks → `fr_p3a_bpool_priced__{year}__{mode}.parquet` (6 files) + canary checks. |
| 5 | `build_bpool_estimation_ready.py` | Collapses the priced long files back to one row per alt, joins household-joint `ils_dispy_real`, adds region/loc4 one-hots, urbanisation, age-banded child counts. Hard-gated against `specs/estimation_spec_bpool_p3a_v1.yaml`. |
| 6 | `harmonise_bpool_engine_ready.py` | Normalises consumption/leisure, rescales squared regressors, sets engine grouping keys, writes the final `fr_p3a_bpool_engine_ready__{singles,couples}.parquet`. |

Helpers used inside Stage 1:
- `hours_mixture_d1.py` — five-mode D1 hours-mixture sampler.
- `occ_draw_empirical.py` — empirical loc4 occupation sampler (dgn×educ3 strata).
- `../pilot/pilot_wage_draw.py` — W1 occupation-conditional log-normal wage sampler (Halton).

Diagnostic / validation (not in the production chain): `recovery_test.py`, `phase_a_param_binding.py`, `phase_b_recovery_test.py`, `phase0_repricing_variation.py`, `proto_gamspy_intermediate_var.py`, `validate_*.py`, `check_*.py`, `diag_nchildren_per_parent.py`, `rebuild_meta.py`.

Output root for all stages: `<storage>/new_data/` (resolved by `_bpool_paths.bpool_dir()`).

---

## 3. Stage-by-stage detail

### Stage 0 — `_bpool_paths.py`

Pure path layer. No data. Reads `~/.mnl/config.yaml` (or `MNL_STORAGE_ROOT`) via `path_helpers`, then exposes:
- `bpool_dir()` → `<storage>/new_data` (the B-pool intermediates root).
- `POOLED_DATA_DIR` → `<storage>/Data/processed/fr/pooled` (Stage-M1 / GSURv2 source pool).
- `FR_PARQUETS[year]` → `<storage>/Data/processed/fr/{year}/fr_{year}.parquet` (full individual rosters built from raw EUROMOD micro-data).
- `em_root()` → user-installed EUROMOD release dir.
- `raw_data_dir()` → `<storage>/Data/FR` (raw `FR_20YY_aN.txt` EUROMOD inputs — referenced as **dataset names** by EUROMOD, not opened directly by bpool).

### Stage 1 — Build the draws (`build_bpool_singles.py` + `build_bpool_couples.py`)

**Input.** The "GSURv2-opportunity-year-aligned" P3a estimation-ready pooled parquets (§1.4):
- `fr_p3a_gsurv2_estimation_ready__singles.parquet`
- `fr_p3a_gsurv2_estimation_ready__couples.parquet`

These contain one row per (HH × old-design draw). The builders use **only** the observed (`draw==0`) row of each `stacked_hh_uid` as a template and **rebuild all simulated alternatives from scratch**, replacing the previous uniform-hours / uniform-wage proposal with D1 hours + W1 wages + empirical occ.

**Singles loop (per `stacked_hh_uid`)** — see `_draw_singles_block`:

For each of `N_DRAWS = 100` simulated alternatives:

1. **Employment**: `working = Bernoulli(1 − π0)` with `π0 = 0.10`.
   - `log_q_E = log(π0)` if non-working, else `log(1 − π0)`.
2. **Occupation** (working only) — `draw_loc4(dgn, educ3, rng)` from `occ_draw_empirical.py`:
   - Draws `loc4 ∈ {1,2,3,4}` from a hard-coded empirical frequency table conditioned on the (dgn, educ3) stratum (6 cells, derived from the observed P3a pool — see §6.2).
   - Returns `log_q_Occ = log(p_loc4 | dgn,educ3)`.
3. **Hours** (working only) — `draw_hours_d1(n, rng)` from `hours_mixture_d1.py`:
   - Finite mixture of six uniforms over [5, 70] h:
     - PT1 [17.5, 21.5) w=0.15
     - PT2 [28.5, 30.5) w=0.10
     - F35 [33.5, 36.5) w=0.24
     - FT  [36.5, 40.5) w=0.20
     - LH  [44.5, 70.0] w=0.10
     - BG  [5.0,  70.0] w=0.21 (background uniform)
   - Sample component `k ∼ Categorical(w)`, then `h ∼ Uniform(lo_k, hi_k)`.
   - `log_q_H = log(w_k / width_k)` — the lockstep-safe density at the drawn point (components only overlap at the measure-zero point 36.5).
4. **Wage** (working only) — `draw_pilot_wages(...)` from `scripts/pilot/pilot_wage_draw.py`:
   - Log-normal Mincer-style model "W1": `log(w) = α + βL·educL + βH·educH + γ1·pexp + γ2·pexp² + δ_occ_k + year_FE`, sampled with **Halton** quasi-random draws seeded by `stacked_hh_uid` for reproducibility.
   - Coefficients live in `scripts/pilot/config/pilot_mincer_coefficients_v1.json` (calibrated, fixed at draw time, NOT free structural parameters).
   - `log_q_W` = log-normal density at the drawn wage, locked to the same Halton draw.
5. **Joint log-proposal density**:
   ```
   log_prior = log_q_E + working · (log_q_Occ + log_q_H + log_q_W)
   ```
6. The simulated rows inherit every household-constant column from the observed row; draw-varying columns (`hours`, `wage`, `loc4`, the four `log_q_*`, `log_prior`, `is_chosen=0`) are overwritten.
7. **Hours-band flags** (`working_pt1/pt2/ft/lh`) are recomputed from each row's own (hours, working) using the same band+gate as the estimator expects. F35 is the reference (no `working_f35`). `working_lh` is built here because upstream omits it.
8. **Chosen row** (`draw==0`): observed `hours/wage/loc4/working` retained, all `log_q*` set to 0 (the importance-sampling anchor), `is_chosen=1`. Band flags are recomputed fresh from the chosen row's own hours; if upstream `working_ft/pt1/pt2` disagree with the fresh recompute, the fresh values win and a warning prints. `working_lh` is always built from scratch (it never exists upstream).

Output: 101 rows per HH (1 chosen + 100 simulated). Written to `fr_p3a_bpool_d1w1__singles.parquet` + a sidecar `__bpoolmeta.json` describing the D1 bands, W1 coefficients, π0, formula, and guardrails.

Per-HH seeding: master `seed` → per-`stacked_hh_uid` integer seed → both the numpy `Generator` (employment/occ/hours) and the Halton wage draws use the same seed for end-to-end reproducibility.

**Couples loop (per `stacked_hh_uid`)** — see `_build_product_block`:

Independent marginals are drawn per partner (head = male, `dgn=1`; partner = female, `dgn=0`):

1. For each partner, draw `PRODUCT_SIZE = 30` marginals via the same E / Occ / H / W chain as singles (`_draw_partner_marginals`). The female partner uses `seed + 1` for its Halton wage stream so male/female wage Haltons are decorrelated.
2. **Cartesian product**: 30 male × 30 female = 900 joint alternatives.
   - `draw_male`, `draw_female` are 1-indexed (0 reserved for chosen).
   - `draw_joint = 30·m_idx + f_idx` ∈ [0, 899] within the simulated rows.
3. **Joint log-proposal**: partners are drawn independently, so
   ```
   log_prior = log_prior_male + log_prior_female
             = (log_q_E_m + w_m·(log_q_Occ_m + log_q_H_m + log_q_W_m))
             + (log_q_E_f + w_f·(log_q_Occ_f + log_q_H_f + log_q_W_f))
   ```
4. Working-band flags `working_{pt1,pt2,ft,lh}_{male,female}` computed per row+partner.
5. Chosen row: `draw_male=0`, `draw_female=0`, `draw_joint=0`, `is_chosen_joint=1`, observed values retained, all `log_q*` = 0. Band flags rebuilt from observed hours (with the same upstream/fresh disagreement guard as singles).

Output: 901 rows per HH (1 chosen + 900 product). Note the **draw_joint=0 collision**: the chosen row and the first simulated cell are both `draw_joint=0` — disambiguated downstream by `is_chosen_joint`.

**Orchestrator** — `run_bpool_draws.py`:
- Runs both builders sequentially, then for each output applies 5 invariant checks:
  - V1 row count = n_hh × (alts+1).
  - V2 log_prior reconstruction residual < 1e-9 on simulated rows.
  - V3 log_q columns all zero on chosen rows.
  - V4 `gsur` (and `gsur_male/female` for couples) match the source parquet (provenance check).
  - V5 `loc4` ∈ {1,2,3,4} on simulated working rows.
- Writes a global `__run_summary.json` and exits 1 on any failure.

### Stage 2 — `build_bpool_precompute.py` (long-format EUROMOD input)

The draws above are *household-level* (one row per alt, with male/female suffixes for couples). EUROMOD needs *individual-level* long files: every person in every HH, replicated across all alternatives, with each decider's `lhw` (weekly hours) and `yivwg` (hourly wage) set to the drawn values.

For each `data_year ∈ {2015, 2016, 2017}` and each `mode ∈ {singles, couples}`:

1. Load the per-year **roster**: `<storage>/Data/processed/fr/{yr}/fr_{yr}.parquet` (the full EUROMOD micro-population for that year — every person, with `ruro_decider` flag, parent pointers `idmother/idfather/idpartner`, observed `lhw`/`yivwg`/`yem*`, region, demographics, etc.). This is the file built by §1.2.
2. Filter the bpool draw parquet to that `data_year`.
3. **Vectorised merge**: `bpool_draws ⋈ roster` on `idhh` → one row per (alt × person). For couples, also merge on a male/female decider-id table built from `roster[ruro_decider==1]` grouped by `dgn`.
4. **Overwrite** decider rows only:
   - `lhw ← drawn hours if working else 0`
   - `yivwg ← drawn wage`
   - Non-deciders keep observed `lhw`, `yivwg`, and all `yem*`.
5. **Canonical earnings identity** (verbatim from `enh_RURO_euromod.py §11`, applied per decider row):
   ```
   FRANCE_STANDARD_HOURS = 35.0
   WEEKS_PER_MONTH       = 52/12 = 4.333…
   regular  = min(lhw, 35)
   overtime = max(lhw − 35, 0)
   yem00 = regular  · yivwg · WEEKS_PER_MONTH      (regular monthly earnings)
   yemxp = overtime · yivwg · WEEKS_PER_MONTH      (overtime monthly earnings)
   yem   = yem00 + yemxp                            (asserted with 1e-6 tolerance)
   ```
   Plus the YEMMY/LUNMY block: `yemmy=12, lunmy=0` for working deciders; `yemmy=0, lunmy=12` for non-working deciders (full-year employment assumption). Non-deciders untouched.
6. **Preserved untouched**: `lhw_f, liwwh, liwwh_f, yem_f, yempv` (previous-year / flags / ranges).
7. **Column ordering**: raw EUROMOD schema (per-year, hard-coded in `_RAW_SCHEMA`) first, then B-pool extras (`draw*`, `is_chosen*`, `log_q*`, `working_*`, `loc4*`, `wage*`, `gsur*`, etc.).
8. Write `fr_p3a_bpool_precompute__{yr}__{mode}__long.parquet`.

**Gate checks** (`_run_gate`) run on every long file:
- **G1 (HARD STOP)**: every raw EUROMOD column for that year must be present (`_RAW_SCHEMA[year]` is the contract).
- **G2**: one row per (alt, idhh, idperson). Couples key on `(draw_male, draw_female)` because `draw_joint=0` is intentionally shared between the chosen row and the (m=0,f=0) simulated cell.
- **G3**: every HH has the same person count across all alternatives (full roster replicated).
- **G4**: non-decider `lhw`, `yem`, `yem00`, `yemxp` constant across alternatives within HH.
- **G5**: decider `lhw` varies across alternatives.
- **G6**: `|yem − (yem00 + yemxp)| < 1e-6`.
- **G7**: parent pointers `idmother / idfather / idpartner` constant per person across alternatives.

### Stage 3 — EUROMOD pricing

**System pairing** (`opportunity_year = data_year − 1`): each year's drawn earnings are passed to the **prior year's** EUROMOD tax-benefit system (opportunity-year alignment):

| data_year | EUROMOD system | dataset           |
|-----------|----------------|-------------------|
| 2015      | FR_2014        | FR_2015_a2        |
| 2016      | FR_2015        | FR_2016_a3        |
| 2017      | FR_2016        | FR_2017_a2        |

Two pricing paths exist; both call the same `EuromodRunner` from `scripts/enhanced/enh_RURO_euromod.py`:

- **`run_bpool_euromod.py`** — in-process, sequential, with internal chunking (n_chunks=6 for couples to keep each .NET+pandas pass at ~1.1 M rows). Used to run the canary year (2017 singles) first, hard-stop on failure, then proceed.

- **`run_bpool_euromod_chunk.py`** + **`launch_chunks.ps1`** — production path. Each chunk is one Python process pricing one draw-range band; PowerShell launcher caps concurrency at 2 parallel processes (each peaking 7–10 GB RAM). Couples are split into 6 bands of 150 `draw_joint` values; singles run as one chunk.

Per chunk:

1. **Stamp draw-specific IDs** (`_stamp_draw_ids`): EUROMOD requires unique `idhh / idperson` across alternatives. Original IDs are preserved as `idhh_true / idperson_true`, then `idhh_new = idhh_orig · id_multiplier + draw` (`id_multiplier = 1_000` for singles, `10_000` for couples). Parent pointers (`idfather/idmother/idpartner`) are stamped identically (zeros preserved as zero so non-existent links stay non-existent).
2. **Build EUROMOD input**: project the long file down to the exact `_RAW_SCHEMA[year]` columns, coerce to numeric, fill NaN→0.
3. `runner.run_on_dataframe(em_input, country="FR", system_code=..., dataset_name=...)` → DataFrame with `ils_dispy, ils_origy, ils_ben, ils_tax, ils_sicdy`.
4. Row count must match `len(chunk_df)` exactly; otherwise hard-stop.
5. **Restore true IDs**, attach EUROMOD outputs.
6. **CPI deflation**: `ils_dispy_real = ils_dispy · φ_year` with `φ_2015=1.0031, φ_2016=1.0000, φ_2017=0.9886` (base = 2016).
7. Write `chunks/fr_p3a_bpool_priced__{yr}__{mode}__cN.parquet` + meta JSON.

**Canary checks** (in `run_bpool_euromod.py` & `assemble_bpool_priced.py`):
- **C1**: `ils_dispy` non-null on every row.
- **C2**: non-working deciders receive benefits — `ils_ben > 0` (or `<5%` negative `ils_dispy` and median `> 0`).
- **C3**: chosen-row internal consistency — CPI identity holds, working chosen rows have non-negative `ils_dispy` and positive `corr(yem, ils_dispy)`, non-working chosen rows have positive median `ils_dispy`. (Explicit note in the code: do **not** cross-check against `roster.ils_dispy` — that was computed by the NEXT year's system on ORIGINAL earnings, so divergence is expected.)
- **C4**: within one sample HH, `corr(lhw, ils_dispy) > 0` (more hours → more net income).

### Stage 4 — `assemble_bpool_priced.py`

Reads the 6 chunk parquets per (year, mode), `pd.concat` (chunks are already draw-ordered, no global sort needed — avoids a ~28 GB deep-copy on couples), runs the canary checks, writes the 6 final parquets:

```
fr_p3a_bpool_priced__{2015,2016,2017}__{singles,couples}.parquet
fr_p3a_bpool_priced__meta.json
```

These are *individual-level* (one row per person per alternative) and are the bridge between EUROMOD and the estimator.

### Stage 5 — `build_bpool_estimation_ready.py`

Collapses the long priced files back to the d1w1 layout (one row per (HH, alt)) and adds the missing estimation regressors.

Per mode:

1. Start from the **draws** file `fr_p3a_bpool_d1w1__{mode}.parquet` (NOT the long priced file — the draws file already has all demographics in the right shape).
2. Drop stale disposable-income columns (`ils_dispy_real`, `consumption`, …) — they were copied from an older priced run.
3. **Join `ils_dispy_real`** from the freshly-priced long file:
   - Singles: decider-row `ils_dispy_real`, keyed on `(stacked_hh_uid, draw, data_year)`.
   - Couples: **joint household disposable income** = `groupby(stacked_hh_uid, draw_joint, is_chosen_joint, data_year).ils_dispy_real.sum()` over the whole tax unit (everyone, not just deciders). This is the consumption budget the household faces under that joint alternative.
4. `consumption = ils_dispy_real`.
5. **Region dummies**: `reg2..reg8` from the seven `reg_nuts1_2..reg_nuts1_8` flags (reg_nuts1_1 = omitted base).
6. **`loc4` one-hots**: `loc4_2 / loc4_3 / loc4_4` (singles) or per-partner (couples); `loc4==1` is the reference.
7. **Urbanisation** (`drgur` urban / `drgmd` middle / `drgru` rural) joined from the priced long file (HH-constant). Rural is the spec's reference category.
8. **Age-banded per-parent child counts** (D5 increment) — `per_parent_child_bands(year)`:
   - From the EUROMOD roster, for each person who is listed as `idmother` or `idfather` of someone in the same HH, count their in-HH children in left-inclusive bands [0,3), [3,6), [6,9), [9,12), [12,18), [18,∞). Sum = `n_children_total`. Singles get unsuffixed columns; couples get `_male`/`_female`.
9. `cluster_id = idorighh` (for clustered standard errors).
10. **Hard gate**: the spec `estimation_spec_bpool_p3a_v1.yaml` is parsed, every variable it references (in utility / leisure / hours_opportunity / wage_opportunity / market_opportunity / occupation_opportunity blocks) is expanded into the concrete column name(s) it should map to — `_male/_female`-suffixed for person-specific vars on couples, plain for household vars (`ils_dispy_real`, region, year dummies, `n_children`). Any missing column FAILS the build (and the file is not written).
11. Six post-build CHECKs:
    - 1: `ils_dispy_real` non-null on all alts.
    - 2: row counts exactly 101 (singles) or 901 (couples) per HH.
    - 3: exactly one chosen row per HH.
    - 4: `dgn` partition (singles); male+female suffixed columns present (couples).
    - 5: `log_prior` reconstruction identity holds.
    - 6: `n_children_total{_g} == sum(n_children_band{_g})` per row.

Writes `fr_p3a_bpool_estimation_ready__{singles,couples}.parquet` + a sidecar `__meta.json` with the full spec-coverage report.

### Stage 6 — `harmonise_bpool_engine_ready.py`

Final transformation to the contract the MNL estimator (`scripts/enhanced/estimation_engine.py`) expects. **Mirrors Stage-M1 (`enh_RURO_prep_mnl_basic.py`) exactly** so bpool-track and original-track outputs are on the same footing:

1. **Leisure** = `clip(TOTAL_LEISURE_HOURS − hours, 1.0)` with `TOTAL_LEISURE_HOURS = 80`. Per gender on couples.
2. **Consumption** = `clip(ils_dispy_real, 1.0)`.
3. **Normalisation**:
   - `c_scale = mean(consumption)` over ALL rows.
   - `l_scale = min(positive leisure)` over CHOSEN rows (per gender on couples).
   - `c_norm = consumption / c_scale`; `l_norm = leisure / l_scale`; `log_c_norm`, `log_l_norm`.
4. **Prior density** = `clip(exp(clip(log_prior, −700, 700)), 1e-16, ∞)`. The engine uses `V = … − log(prior)` to subtract the importance-sampling proposal density from the systematic utility.
5. **Squared-regressor rescaling** (`_rescale_squared_regressors`) — `pexp_years[_male/_female]` divided by 20, `age_norm[_male/_female]` by 10; squares recomputed from the rescaled linears. Reason logged in the file's docstring: in raw units `pexp_years2` reached ~2400 and `age_norm2` ~640, so `beta_w_pexp2` / `beta_l_age2_*` dominated `|g|_max` and blocked the L-BFGS-B convergence test even at the optimum (recovery-test diagnosis). Coefficients now interpret per-decade. Idempotency guarded by checking `max|.| > 6`.
6. **Keys**: `idhh = stacked_hh_uid` (per-alt repeated); `year_tag = {2015→1, 2016→2, 2017→3}`; `cluster_id = idorighh`; `is_chosen` mirrors `is_chosen_joint` on couples so the engine's "chosen-row" reader works the same way for both modes.
7. Sort by `(idhh, draw[_joint])`.

Writes `fr_p3a_bpool_engine_ready__{singles,couples}.parquet` + `__mnlmeta.json`. These are the files consumed by the recovery tests and the production estimator.

---

## 4. Cross-cutting design choices

- **Importance-sampling identity.** The simulated alternatives are not observed; they are proposal draws. Their density appears in the choice-probability denominator as `exp(V_j − log_prior_j)`. The chosen (observed) row is the IS anchor: its `log_q_*` are forced to 0 so it contributes only its systematic utility. Verified at multiple stages (V2/V3, CHECK 5).
- **Per-HH reproducibility.** A master seed (default 2026) feeds a single Generator that draws one integer seed per `stacked_hh_uid`. That HH-seed drives both the numpy choice/uniform draws and the Halton wage draws, so re-running with the same seed reproduces every alternative exactly.
- **Couples partner independence.** Male and female marginals are drawn separately and joined by Cartesian product. Joint `log_prior` is the sum of marginal log-priors. Opposite-sex coupling is hard-coded (`DGN_MALE=1, DGN_FEMALE=0`).
- **GSUR provenance.** `gsur, gsur_male, gsur_female` are inherited verbatim from the GSURv2 opportunity-year-aligned source — never recomputed in the bpool stage. V4 enforces this.
- **EUROMOD ID stamping.** EUROMOD has no concept of "alternatives"; it expects a single cross-section. The pipeline tricks it into pricing all alternatives in one pass by inflating `idhh / idperson` by `draw_index`, then restoring true IDs from `*_true` columns after pricing.
- **`working_lh` reconstruction.** The Stage-M1 pooled parquets ship `working_pt1/pt2/ft` but **not** `working_lh`. The bpool builders recompute all four band flags on every row (simulated and chosen) from the row's own `hours/working`. A documented bug (logged in `RURO_recovery_test_results_singles_v1.md`) was that without this, `working_lh` defaulted to 0 on chosen rows for ~17% of singles workers and ~30% of male couples, driving `beta_h_lh` to its lower bound during estimation.
- **Spec-driven hard gate at Stage 5.** The estimation spec YAML is the single source of truth for what columns are required; Stage 5 refuses to write the parquet if any are missing.
- **No cleaning, no filtering.** The bpool stage never adds or removes households; row count of decider HHs in is exactly row count out. All filters were applied upstream in `enh_france_data_prep.stepwise_filter_households`.

---

## 5. Full data flow — raw → estimation

```
raw EUROMOD micro-data  <storage>/Data/FR/FR_{year}_aN.txt
                │
                ▼ enh_france_data_prep.py  (run baseline EUROMOD, classify heads/partners, fix les, reconstruct wages, filter HH by age/edu/les/wage/hours/retirement, opposite-sex couples, child counts)
<storage>/Data/processed/fr/{year}/fr_{year}.parquet                    (full roster, EUROMOD-input schema)
        +  ..._singles.parquet  /  ..._couples.parquet                  (deciders + covariates, per year)
                │
                ▼ enh_RURO_draws.py  → enh_RURO_euromod.py  → enh_prepare_FR_gsur.py  → enh_RURO_prep_mnl_basic.py
        (old per-year draws + EUROMOD pricing + GSUR merge + canonical MNL normalisation, per year)
fr_{year}_RURO_mnl_GSURv2_y*__{singles,couples}.parquet                 (per-year MNL-ready)
                │
                ▼ multi_year/m1_stack_years.py  (year_tag, stacked_hh_uid = year_tag·10^11 + idhh)
                ▼ multi_year/m1_harmonise_cpi.py  (HICP-FR deflation → ils_dispy_real etc.)
                ▼ multi_year/m1_add_cluster_key.py + m1_validate.py
<storage>/Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__{singles,couples}.parquet   ← bpool input
                │
                ▼ build_bpool_{singles,couples}.py  (D1 hours + W1 wages + empirical loc4 + π0 employment)
fr_p3a_bpool_d1w1__{singles,couples}.parquet                             (101 / 901 alts per HH, HH-level rows)
                │
                ▼ build_bpool_precompute.py  (× full HH roster, vectorised merge, canonical earnings split)
fr_p3a_bpool_precompute__{year}__{mode}__long.parquet                    (individual rows, EUROMOD-input schema)
                │
                ▼ launch_chunks.ps1 → run_bpool_euromod_chunk.py  (× 6 chunks for couples, × 1 for singles)
chunks/fr_p3a_bpool_priced__{year}__{mode}__cN.parquet                   (per-band priced)
                │
                ▼ assemble_bpool_priced.py
fr_p3a_bpool_priced__{year}__{mode}.parquet                              (6 files, full priced individual rows)
                │
                ▼ build_bpool_estimation_ready.py  (collapse to (HH,alt); join joint dispy; add regions, loc4 OHE, urbanisation, child bands; HARD GATE vs spec)
fr_p3a_bpool_estimation_ready__{singles,couples}.parquet
                │
                ▼ harmonise_bpool_engine_ready.py  (leisure, normalise c & l, prior=exp(log_prior), rescale squared regressors, set engine keys)
fr_p3a_bpool_engine_ready__{singles,couples}.parquet                     ← consumed by the MNL estimator + recovery tests
```

---

## 6. Every hard-coded knob (in the bpool stage)

> Anything not listed here is either (a) inherited from upstream parquets, (b) read from `_bpool_paths` (which itself reads `~/.mnl/config.yaml`), or (c) controlled by CLI flags (`--seed`, `--singles-only`, `--year`, `--n-chunks`, `--canary-only`, etc.).

### 6.1 Draws constants (`build_bpool_singles.py`, `build_bpool_couples.py`)

| Constant | Value | Location | Editable via |
|---|---|---|---|
| `N_DRAWS` (singles per HH) | **100** | `build_bpool_singles.py:59` | source edit only |
| `PRODUCT_SIZE` (per partner) | **30** | `build_bpool_couples.py:58` | source edit only |
| `N_JOINT` (couples joint alts per HH) | **30·30 = 900** | `build_bpool_couples.py:59` | derived |
| `PI0` (non-employment probability) | **0.10** | both files line 60 | source edit only |
| `DGN_MALE / DGN_FEMALE` | **1 / 0** | `build_bpool_couples.py:65-66` | source edit only |
| master `seed` (default) | **2026** | both `__main__` blocks | `--seed N` CLI |

### 6.2 D1 hours mixture (`hours_mixture_d1.py`)

Hard-coded band table `_BANDS`:

| Component | Band [lo, hi) | Width | Default weight |
|---|---|---:|---:|
| PT1 | [17.5, 21.5) |  4.0 | 0.15 |
| PT2 | [28.5, 30.5) |  2.0 | 0.10 |
| F35 | [33.5, 36.5) |  3.0 | 0.24 |
| FT  | [36.5, 40.5) |  4.0 | 0.20 |
| LH  | [44.5, 70.0] | 25.5 | 0.10 |
| BG  | [5.0,  70.0] | 65.0 | 0.21 |

Weights are passable per call (`draw_hours_d1(..., weights=...)`) but no CLI exposes them. `H_MIN = 5.0`, `H_MAX = 70.0` hard-coded at module level.

### 6.3 Empirical loc4 frequencies (`occ_draw_empirical.py`)

Hard-coded table `_FREQ[(dgn, educ3)] → np.array(p_loc4=1..4)` — 6 cells derived once from the P3a observed pool. Listed verbatim in `occ_draw_empirical.py:34-42`. Re-deriving requires editing that dict.

### 6.4 W1 wage model

Coefficients live in `scripts/pilot/config/pilot_mincer_coefficients_v1.json` (loaded at every run). Includes `alpha, beta_educL, beta_educH, gamma_pexp, gamma_pexp2, delta_occ2/3/4, sigma, year_FE_2015/2017`. The bpool stage treats these as **calibrated and fixed at draw time, not free structural parameters**.

### 6.5 Earnings accounting (`build_bpool_precompute.py`)

| Constant | Value | Why |
|---|---|---|
| `FRANCE_STANDARD_HOURS` | **35.0** | regular/overtime split at 35 h/wk |
| `WEEKS_PER_MONTH`       | **52 / 12 = 4.333…** | annualised-monthly factor |
| YEMMY (working decider) | **12** | full-year employment assumption |
| LUNMY (non-working decider) | **12** | symmetric: full-year non-employment |

### 6.6 EUROMOD pricing (`run_bpool_euromod*.py`)

| Knob | Value |
|---|---|
| System pairing | `2015→FR_2014/FR_2015_a2`, `2016→FR_2015/FR_2016_a3`, `2017→FR_2016/FR_2017_a2` |
| CPI φ | `φ_2015 = 1.0031, φ_2016 = 1.0000, φ_2017 = 0.9886` (base 2016) |
| `id_multiplier` singles | **1_000** (> max draw 100) |
| `id_multiplier` couples | **10_000** (> max draw_joint 900) |
| `_EM_OUTPUT_COLS` | `[ils_dispy, ils_origy, ils_ben, ils_tax, ils_sicdy]` |
| `_RAW_SCHEMA[year]` | per-year column list (the EUROMOD input contract; 122 / 124 / 128 cols) |
| Couples chunk count | **6** (`--n-chunks` CLI, default 6) |
| Max concurrent chunk processes | **2** (`launch_chunks.ps1`, `$maxConcurrent`) |

### 6.7 Estimation-ready / engine-ready

| Knob | Value | Where |
|---|---|---|
| Child age bands | `[0,3), [3,6), [6,9), [9,12), [12,18), [18,∞)` | `build_bpool_estimation_ready.py:_CHILD_BANDS` |
| Spec YAML | `specs/estimation_spec_bpool_p3a_v1.yaml` | the hard gate's source of truth |
| `TOTAL_LEISURE_HOURS` | **80.0** | `harmonise_bpool_engine_ready.py:43` |
| `DCM_MIN_POSITIVE` | **1.0** | floor on consumption/leisure |
| `_YEAR_TAG` | `{2015:1, 2016:2, 2017:3}` | `harmonise_bpool_engine_ready.py:45` |
| Squared-regressor rescales | `pexp_years[_g] / 20`, `age_norm[_g] / 10` | `_SQUARED_PAIRS` |

### 6.8 Diagnostic / not-in-pipeline

`recovery_test.py`, `phase_a_param_binding.py`, `phase_b_recovery_test.py`, `phase0_repricing_variation.py`, `proto_gamspy_intermediate_var.py`, `validate_*.py`, `check_*.py`, `diag_nchildren_per_parent.py`, `rebuild_meta.py` — these are post-hoc audits and recovery tests; they don't produce production data and can be skipped on a clean rerun.

---

## 7. What would change to vary `N_DRAWS` or any other "hard-coded" value

To change the number of singles draws from 100 to, say, 200:

1. Edit `build_bpool_singles.py` line 59 → `N_DRAWS = 200`.
2. Re-run `python scripts/bpool/run_bpool_draws.py --seed 2026 --singles-only`.
3. Re-run Stages 2–6 for singles (couples can stay if you only changed singles). Stage 5's CHECK 2 expects 101; you'd need to change `expected = 101 if mode == "singles" else 901` in `build_bpool_estimation_ready.py:356` to 201 to match.

The constants are intentionally constants (not CLI args) because they encode the **design decision** behind the alternative pool — changing them is a methodological change, not a runtime tweak. The decision log is `docs/France_case/P3a/.../RURO_spec_redesign_decisions_v2.md` (referenced repeatedly in docstrings).

Same logic applies to PI0 (the non-employment probability), the D1 band weights, the W1 Mincer coefficients, the loc4 frequency table, the CPI vector, and the system pairing.
