# JMP Single-Year FR_2017 — Replication Report v1

**Document:** Results/P3a/multi_year_stage_M1/JMP_single_year_FR2017_replication_report_v1.md  
**Date:** 2026-05-20  
**Author:** Pipeline execution via Claude Code  
**Authorization:** `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`  
**Command plan:** `docs/JMP_single_year_replication_2015_2017_command_plan_v2.md` + `_addendum_v1.md`  
**GSUR decision:** `docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md` (Decision 2)  
**Output stem:** `fr_2017_RURO_mnl_v1gsurY2016`

---

## 1. Execution verdict

**PASS — FR_2017 single-year pipeline completed successfully. All five stages executed without errors. All validation checks pass.**

- EUROMOD system confirmed via XML preflight: `FR_2016` / dataset `FR_2017_a2`.
- GSUR opportunity year 2016 applied via `--gsur-year 2016` (Option A per command plan addendum §4).
- Cell-level GSUR rate verification: `singles[0]` rate matches v1 year=2016 table exactly.
- Zero missing `gsur` in both singles and couples.
- All script-internal sanity checks passed.
- Stage M1 P3a dry-run: **2015 FOUND, 2016 FOUND, 2017 FOUND — status: ready to run.**

---

## 2. Commands run

**Stage 1 — France data prep:**
```powershell
& python enh_france_data_prep.py --year 2017 --raw-dir "Z:\...\Data\FR" `
    --raw-filename "FR_2017_a2.txt" --out-dir "Z:\...\Data\processed\fr\2017" `
    --system-year 2016 --export-format parquet
```

**Stage 2 — RURO prep:**
```powershell
& python enh_RURO_prep.py --processed-dir "Z:\...\Data\processed\fr\2017" `
    --base-year 2017 --export-format parquet
```

**Stage 3 — RURO draws:**
```powershell
& python enh_RURO_draws.py --singles-path "Z:\...\fr\2017\singles_RURO_ready.parquet" `
    --couples-path "Z:\...\fr\2017\couples_RURO_ready.parquet" `
    --n-draws 99 --wage-spec vw --occ-spec empirical --occ-strata __all__ `
    --pi0-m 0.1 --pi0-f 0.1 --h-min 5.0 --h-max 70.0 --w-min 2.0 --w-max 170.0 `
    --rng-seed 17
```

**Stage 4 — EUROMOD combined run:**
```powershell
& python enh_RURO_euromod.py --singles-draws "Z:\...\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\...\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --microdata-template "Z:\...\Data\FR\FR_2017_a2.txt" `
    --euromod-root "Z:\...\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
    --euromod-system FR_2016 --euromod-dataset FR_2017_a2 `
    --scenario-dir "Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios"
```

**Stage 5 — MNL prep (with GSUR opportunity year 2016):**
```powershell
& python enh_RURO_prep_mnl_basic.py `
    --singles-draws "Z:\...\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\...\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\...\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base "Z:\...\fr\2017\fr_2017_RURO_mnl_v1gsurY2016" `
    --drawsmeta "Z:\...\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file "U:\...\MNL\Data\external\FR_gsur_ruro.parquet" `
    --gsur-year 2016 --year 2017
```

All commands completed with exit code 0. No warnings beyond pre-existing
`DeprecationWarning` for `datetime.utcnow()` and the expected EUROMOD uprate
component-sum warnings (identical pattern to FR_2015 and FR_2016 runs).

---

## 3. Input files used

| Input | Path | Status |
|-------|------|--------|
| EU-SILC raw microdata | `Z:\...\Data\FR\FR_2017_a2.txt` | Present (9.8 MB) |
| v1 GSUR lookup | `Data/external/FR_gsur_ruro.parquet` | Present (2,160 rows; year=2016 confirmed: 120 rows) |
| Draws metadata (inherited) | `Z:\...\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json` | Written by Stage 3 |

All intermediate outputs (Stages 1–4) were produced fresh in this session. No
pre-existing FR_2017 data existed on Z: at the start of this task.

---

## 4. EUROMOD system used

**Preflight method:** `euromod` Python package via `em.Model(euromod_root())`, with
`PYTHONNET_RUNTIME=coreclr` set before import (required by pythonnet/.NET runtime;
`enh_france_data_prep.py` line 35 sets this env var). Initial standalone test failed
because the env var was not set; corrected script succeeded. EUROMOD root resolved by
`path_helpers.euromod_root()` to
`U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`.

**Preflight result (systems for FR_2013–FR_2018, from `em.Model`):**

| System | Datasets available |
|--------|-------------------|
| FR_2013 | FR_training_data, FR_2012_b3, FR_2013_hhot, training_data |
| FR_2014 | FR_training_data, FR_2012_b3, FR_2014_hhot, FR_2015_a2, training_data |
| FR_2015 | FR_training_data, FR_2015_a2, FR_2015_hhot, FR_2016_a3, training_data |
| FR_2016 | FR_training_data, FR_2015_a2, FR_2016_a3, FR_2016_hhot, **FR_2017_a2**, training_data |
| FR_2017 | FR_training_data, FR_2015_a2, FR_2016_a3, FR_2017_a2, FR_2017_hhot, FR_2018_a2, training_data |
| FR_2018 | FR_training_data, FR_2016_a3, FR_2017_a2, FR_2018_a2, FR_2018_hhot, FR_2019_c2, training_data |

**Selected for FR_2017 data-year run:**
- `--euromod-system FR_2016` (EUROMOD system year = data year − 1)
- `--euromod-dataset FR_2017_a2` (matches the actual microdata file `FR_2017_a2.txt`)

This is consistent with the convention confirmed for FR_2016 (system=`FR_2015`,
dataset=`FR_2016_a3`) and authorized by §7 of the authorization memo. The EUROMOD
simulation confirmed: `System: FR_2016, Dataset: FR_2017_a2` (from
`combined_draws_em__euromodmeta.json`).

---

## 5. First EUROMOD/data-prep output

**Script:** `enh_france_data_prep.py` — Stage 1  
**System used in Stage 1:** FR_2016 / FR_2017_a2 (EUROMOD called internally by the script)

| Statistic | Value |
|-----------|-------|
| Raw records loaded (`FR_2017_a2.txt`) | 25,309 |
| Total households | 11,068 |
| RURO deciders (heads + partners) | 17,439 |
| Couple households (filtered) | 2,295 |
| Single households (filtered) | 1,662 |
| Combined filtered records | 9,910 |
| EUROMOD simulation time | 5.2 seconds |
| EUROMOD output columns | 378 (133 input + 258 simulated C_cols) |

**Outputs written:**
- `Z:\...\Data\processed\fr\2017\fr_2017.parquet` (full dataset)
- `Z:\...\Data\processed\fr\2017\fr_2017_singles.parquet` (2,364 rows / 1,662 HHs)
- `Z:\...\Data\processed\fr\2017\fr_2017_couples.parquet` (7,546 rows / 2,295 HHs)
- `Z:\...\Data\processed\fr\2017\fr_2017__colgroups.json`
- `U:\...\outputs\prep\fr\2017\fr_2017_meta.json`

The EUROMOD log message: `Simulation for system FR_2016 with dataset FR_2017_a2 finished.`

---

## 6. Draw-generation output

**Script:** `enh_RURO_draws.py` — Stage 3

| Parameter | Value | Expected |
|-----------|-------|----------|
| `n_draws` | 99 | 99 ✓ |
| `wage_spec` | `vw` | `vw` ✓ |
| `occ_spec` | `empirical` | `empirical` ✓ |
| `occ_strata` | `__all__` | `__all__` ✓ |
| `pi0_m`, `pi0_f` | 0.1 | 0.1 ✓ |
| `h_min` / `h_max` | 5.0 / 70.0 | 5.0 / 70.0 ✓ |
| `w_min` / `w_max` | 2.0 / 170.0 | 2.0 / 170.0 ✓ |
| `rng_seed` | 17 | 17 ✓ |

Draw grid completeness: 100% (4,590/4,590 deciders have complete draw sets 0..99).
Draw=0 baseline compliance: 100%.

**Outputs written:**
- `Z:\...\fr\2017\singles_RURO_ready_RURO_draws.parquet`
- `Z:\...\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json`
- `Z:\...\fr\2017\couples_RURO_ready_RURO_draws.parquet`
- `Z:\...\fr\2017\couples_RURO_ready_RURO_draws__drawsmeta.json`

---

## 7. Second RURO EUROMOD output

**Script:** `enh_RURO_euromod.py` — Stage 4

EUROMOD combined-draws run: applies EUROMOD tax-benefit rules to each (household, draw)
combination to produce simulated disposable incomes.

| Statistic | Value |
|-----------|-------|
| System | FR_2016 |
| Dataset | FR_2017_a2 |
| Combined draws parquet rows | 1,086,700 (per euromodmeta n_rows) |
| `ils_dispy=0` rows | ~34.6% (343,059 / 990,900 decider rows) — expected pattern |

The `ils_dispy=0` warning (34.6%) is the same pattern observed in FR_2015 (0.0%
missing after switch to `ils_dispy_em`) and is resolved in Stage 5 by the script's
`EUROMOD merge: Using ils_dispy_em ... as canonical ils_dispy (missing rate: 0.0%)`
fallback. This is expected and not an error.

EUROMOD uprate component-sum warnings for 5 idperson values (`bun`, `bsa` components)
are pre-existing EUROMOD behaviour — identical to warnings seen in FR_2015/FR_2016
runs.

**Output written:**
- `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet`
- `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em__euromodmeta.json`

---

## 8. Single-year MNL-input parquet outputs

**Script:** `enh_RURO_prep_mnl_basic.py` — Stage 5  
**GSUR flag used:** `--gsur-year 2016 --year 2017` (Option A per command plan addendum §4)

| File | Rows | Columns | Size |
|------|------|---------|------|
| `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | 166,200 | 75 | 20.4 MB |
| `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | 229,500 | 93 | 37.2 MB |
| `fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` | — | — | ~60 KB |

The output stem `fr_2017_RURO_mnl_v1gsurY2016` encodes the GSUR source (v1 fallback)
and the opportunity year (2016) in the filename, distinct from any future
`fr_2017_RURO_mnl_GSURv2__` files.

---

## 9. Metadata sidecars

### MNL metadata (`fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json`)

| Field | Value |
|-------|-------|
| `script` | `enh_RURO_prep_mnl_basic.py` |
| `timestamp` | `2026-05-20T07:36:06.778507Z` |
| `year` | `2017` |
| `gsur_version` | `v1_fallback_opportunity_year_aligned` (patched post-run) |
| `gsur_opportunity_year` | `2016` (patched post-run) |
| `gsur_alignment_status` | `aligned` (auto-written by script) |
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` |
| `gsur_data_year` | `2017` |
| `gsur_note` | `GSUR filtered to opportunity year 2016 (EUROMOD system year FR_2016) before merge. Data year: 2017. v1_fallback_opportunity_year_aligned / not final for pooled estimation until GSURv2 opportunity-year-aligned rates are available.` |
| `prior_parameters.wage_spec` | `vw` |
| `prior_parameters.pi0_m` | `0.1` |
| `prior_parameters.h_min` | `5.0` |

Fields `gsur_version` and `gsur_opportunity_year` added by post-run sidecar patch
(same procedure as FR_2015 rebuild). Fields `gsur_data_year`, `gsur_alignment_rule`,
`gsur_alignment_status`, and `gsur_note` auto-written by script Edit 3 of the
`--gsur-year` patch.

### EUROMOD metadata (`combined_draws_em__euromodmeta.json`)

| Field | Value |
|-------|-------|
| `system` | `FR_2016` |
| `dataset` | `FR_2017_a2` |

### Draws metadata (`singles_RURO_ready_RURO_draws__drawsmeta.json`)

| Field | Value |
|-------|-------|
| `n_draws` | `99` |
| `distributional_params.wage_spec` | `vw` |
| `distributional_params.occ_spec` | `empirical` |

---

## 10. Row counts

| Dataset | Decider HHs | Total rows | Draws per HH |
|---------|------------|-----------|-------------|
| Singles MNL input | 1,662 | 166,200 | 100 (draws 0–99) |
| Couples MNL input | 2,295 | 229,500 | 100 (draws 0–99) |

Singles: 1,662 × 100 = 166,200 ✓  
Couples: 2,295 × 100 = 229,500 ✓

All draw counts validated by script sanity check: all households have exactly 100 draws.

---

## 11. Household counts

| Stage | Singles HHs | Couples HHs |
|-------|------------|------------|
| Stage 1 (data prep filtered) | 1,662 | 2,295 |
| Stage 2 (RURO prep) | 1,662 | 2,295 |
| Stage 3 (draws, deciders) | 1,662 | 2,295 |
| Stage 5 (MNL input, draw=0 rows) | 1,662 | 2,295 |

Consistent across all stages. Total P3a-eligible FR_2017 households: **3,957** (1,662 + 2,295).

**Comparison to prior years:**

| Year | Singles HHs | Couples HHs | Total |
|------|------------|------------|-------|
| 2015 | 1,669 | 2,566 | 4,235 |
| 2016 | ~1,600 (GSURv2) | ~2,540 (GSURv2) | ~4,140 |
| 2017 | **1,662** | **2,295** | **3,957** |

FR_2017 couples count (2,295) is lower than FR_2015 (2,566) by 271 households
(~10.6%). This is expected given annual variation in the EU-SILC sample and eligibility
criteria; no anomaly threshold is triggered.

---

## 12. Person counts

| File | Rows | Description |
|------|------|-------------|
| Raw EU-SILC `FR_2017_a2.txt` | 25,309 | All persons (all ages, all types) |
| Stage 2 RURO prep singles | 2,364 | Working-age single deciders + non-deciders |
| Stage 2 RURO prep couples | 7,546 | Couple household members (partners + others) |
| Stage 5 singles MNL (draw=0) | 1,662 | Decider singles only |
| Stage 5 couples MNL (draw=0 per member) | 4,590 | Decider persons (2,295 HHs × 2) |

---

## 13. Identifier checks

Script sanity check confirmed:

- `idhh`: PRESENT, missing=0
- `draw`: PRESENT, missing=0
- `idperson` present in draws data (pre-column-filter)
- `idorighh`, `idorigperson` verified to exist in raw draws data prior to MNL prep
  column filter (column filter retains 75 essential columns for singles, 93 for couples)

Stage M1 raw-ID fields confirmed in YAML spec:
`['idorighh', 'idorigperson', 'idhh', 'idperson']` — these are listed in the P3a
stacker's `raw_ids_to_preserve` field and will be carried through pooling.

---

## 14. Raw-ID preservation

The Stage M1 P3a dry-run output confirms the UID scheme:

| Year | Tag | UID range |
|------|-----|-----------|
| 2015 | 1 | 100,000,000,001 to 199,999,999,999 |
| 2016 | 2 | 200,000,000,001 to 299,999,999,999 |
| 2017 | 3 | 300,000,000,001 to 399,999,999,999 |

Original IDs (`idorighh`, `idorigperson`) are preserved alongside the synthetic UIDs
in the stacked output, ensuring traceability back to the EU-SILC microdata.

---

## 15. Key variables present

All required variables confirmed present in `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet`:

| Variable | Present | Missing |
|----------|---------|---------|
| `idhh` | YES | 0 |
| `draw` | YES | 0 |
| `consumption` | YES | 0 |
| `leisure` | YES | 0 |
| `gsur` | YES | 0 |
| `dgn` | YES | 0 |
| `drgn1` | YES | 0 |
| `educ3` | YES | 0 |
| `year` | YES | 0 |
| `data_year` | YES | 0 |
| `year_for_ruro` | YES | 0 |
| `ils_dispy` | YES | 0 |
| `ils_earns` | YES | 0 |

Unique draw values: 100 (0–99). All positive for consumption and leisure (script sanity
check PASS: std_consumption=5946.85 for singles, std_leisure=21.02).

---

## 16. Monetary variables and CPI/HICP readiness

**Nominal variables in parquet:** `consumption`, `ils_dispy`, `ils_earns` and related
income components are in nominal EUR, year 2017 prices. No CPI deflation is applied in
the single-year pipeline.

**CPI/HICP deflation** is applied at Stage M1 (m1_stack_years.py / harmonisation
step), using `Data/external/cpi_hicp_fr_harmonisation.csv`. The φ_t value for
2017 = **0.9886** (EUROMOD HICP, Option B, provisional). Source:
`docs/France_case/_shared/governance/JMP_multi_year_CPI_HICP_source_decision_v1.md`.

This parquet is CPI/HICP-ready: it is nominal, consistently constructed with 2015
and 2016 parquets, and will be deflated at the pooled stage. No correction needed here.

The HICP adoption remains provisional — if INSEE IPC is retrieved and any φ_t differs
by ≥0.5 pp, the harmonised parquets must be rebuilt (addendum v2 §Issue 1). This does
not affect the single-year parquet itself.

---

## 17. GSUR status for 2017

**GSUR opportunity year used: 2016** (EUROMOD system year for data year 2017).

The GSUR filter log from Stage 5:
```
Loaded GSUR lookup: 2,160 rows
GSUR filtered to opportunity year 2016: 120 rows
GSUR lookup year column set to data year 2017 for merge-key alignment (opportunity year: 2016).
GSUR merge (singles): filled 166200 rows using fallback age_group=Y20-64
GSUR merge (male): filled 229300 rows using fallback age_group=Y20-64
GSUR merge (female): filled 229300 rows using fallback age_group=Y20-64
```

**Cell-level verification:**

| Item | Value |
|------|-------|
| First row: `drgn1=1, dgn=0, educ3=1` | gsur = 0.103 |
| v1 table year=2016 rate for this cell | **0.103** (exact match) |
| v1 table year=2017 rate for this cell | 0.108 |
| Matches year=2016 | **YES** (within float tolerance) |

Singles mean gsur: **0.096078** (year=2016 rates applied).

This is Command Plan Addendum §4 **Option A** (preferred): `--gsur-year 2016` supplied,
GSUR rates from year=2016, sidecar records `gsur_alignment_status: aligned`.

**GSUR alignment rule applied:** `opportunity_year = euromod_system_year` (FR_2016 system → GSUR year 2016).

---

## 18. Whether output is GSURv2-final or pre-GSURv2

**Pre-GSURv2. Not final for pooled estimation.**

| Label field | Value |
|-------------|-------|
| `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| `gsur_opportunity_year` | `2016` |
| `gsur_alignment_status` | `aligned` |
| Filename stem | `fr_2017_RURO_mnl_v1gsurY2016__` (no `GSURv2` segment) |

The v1 GSUR lookup (`FR_gsur_ruro.parquet`) was used — the only source available for
2016 opportunity-year rates. GSURv2 for year 2016 exists only as
`FR_gsur_ruro_v2_stageA.parquet` (2016 hardcoded), which carries more refined rates
derived from Eurostat denominators and INSEE BDM benchmarks. The v2 rates were not
used here to maintain consistency with FR_2015 (which also uses v1 fallback).

**Conditions for promotion to final status (Decision 4 of the alignment decision memo):**
1. GSURv2 extended to opportunity year 2016 via `enh_prepare_FR_gsur_v2.py` (requires Eurostat and INSEE BDM for 2016).
2. A new authorization memo for the GSURv2-upgraded FR_2017 run.

Until those conditions are met, this parquet is suitable for:
- Stage M1 provisional dry-run and cross-year stability diagnostics.
- Single-year sample-size and income-variable validation.
- Provisional pooled dry-run under the `provisional_v1_fallback` label (Decision 3).

---

## 19. tpr/twl annotation

**Check D result (authorization memo §10, addendum v2 §Issue 2):**

| Variable | Non-zero rows (RURO singles sample, n=2,364) | WA incidence | Threshold |
|----------|---------------------------------------------|-------------|-----------|
| `tpr` | 0 / 2,364 | 0.000% | ≤ 1% |
| `twl` | **6 / 2,364** | **0.254%** | ≤ 1% |

**Both below 1% threshold. No escalation required.**

The `twl` (ISF wealth tax) pattern for FR_2017 is consistent with addendum v2
findings: 2017 carries `twl` at 0.254–0.295% working-age incidence. This matches the
expected pattern (2015 and 2018 carry `tpr`; 2016 and 2017 carry `twl`). The tax-field
asymmetry is low-incidence, symmetric, and enters `ils_dispy` as an observed EU-SILC
input (not a EUROMOD simulation). Not a P3a-blocking gate.

**Required validation annotation for Stage M1 report:**

| Year | `tpr` non-zero (RURO sample) | `twl` non-zero (RURO sample) | Note |
|------|------------------------------|------------------------------|------|
| 2015 | 5 singles (estimated; matches addendum v2 ~5–53 range) | — | Property tax observed input |
| 2016 | — | ~4–5 singles (GSURv2 run; not re-examined here) | Wealth tax (ISF) observed input |
| **2017** | **0** | **6 singles (0.254%)** | Wealth tax (ISF) observed input |

---

## 20. Comparability to 2016

**⚠ CORRECTION (addendum 2026-05-20):** The original version of this section stated
that FR_2016 and FR_2017 both use GSUR opportunity year 2016 and are therefore
comparably keyed. This is incorrect. Under the alignment rule
(`opportunity_year = euromod_system_year`), the correct GSUR opportunity year for
FR_2016 is **2015** (EUROMOD system FR_2015), not 2016. FR_2016's current M1-clean
operative file (`fr_2016_RURO_mnl_GSURv2__`) carries GSUR rates keyed to year=2016
(confirmed by cell-level check: first row rate=0.153 matches v1 year=2016 exactly).
Its sidecar contains no alignment fields (`gsur_opportunity_year`, `gsur_alignment_status`
all ABSENT) and cites `FR_gsur_ruro.parquet` (v1) as the GSUR source — which is also
incorrect (actual rates are from `FR_gsur_ruro_v2_stageA.parquet`). FR_2016 GSUR
opportunity-year status is therefore **UNRESOLVED** under the adopted alignment rule.

| Dimension | FR_2016 (GSURv2, M1-clean) | FR_2017 (v1gsurY2016) | Status |
|-----------|---------------------------|----------------------|--------|
| EUROMOD system | FR_2015 | FR_2016 | Both lag by 1 year ✓ |
| Dataset | FR_2016_a3 | FR_2017_a2 | Same EU-SILC series ✓ |
| Draw parameters | vw, n=99, seed=17 | vw, n=99, seed=17 | ✓ |
| GSUR source | GSURv2 stageA | v1 fallback | Mixed — different rate tables |
| Correct GSUR opp. year (per rule) | **2015** | 2016 | FR_2016 is **misaligned** |
| Actual GSUR year used | **2016** (wrong) | 2016 (correct for 2017) | FR_2016 uses wrong year |
| Sidecar alignment fields | **ABSENT** | Present | FR_2016 not annotated |
| Column counts (singles / couples) | 75 / 93 | 75 / 93 | ✓ |
| Normalization c_scale (singles) | ~7,500 | 7,584 | Consistent |

**Consequence for Stage M1 pooled stacking:** The three P3a files currently present in
`Data/processed/fr/` have inconsistent GSUR alignment status:

| Year | File stem | GSUR opp. year used | Correct opp. year | Aligned? |
|------|-----------|---------------------|-------------------|----------|
| 2015 | `v1gsurY2014` | 2014 | 2014 | ✓ aligned |
| 2016 | `GSURv2` | **2016** | **2015** | ✗ misaligned |
| 2017 | `v1gsurY2016` | 2016 | 2016 | ✓ aligned |

**Stage M1 live execution is not authorized** on this basis. Two options:

- **Option A (preferred):** Rebuild FR_2016 MNL input as `fr_2016_RURO_mnl_v1gsurY2015`
  using existing 2016 draws and EUROMOD output, with `--gsur-year 2015 --year 2016`.
  This would give a v1-fallback aligned set for all three years (2014/2015/2016), which
  is coherent for a provisional dry-run under the `provisional_v1_fallback` label.
- **Option B:** Proceed with the current mixed-source P3a dry-run only, explicitly
  prohibiting interpretation of outputs as a pooled empirical model. Document FR_2016's
  misalignment in all outputs and report tables.

A consolidated single-year readiness verdict must be issued before any pooled stacking
proceeds.

---

## 21. Comparability to corrected 2015

| Dimension | FR_2015 (v1gsurY2014) | FR_2017 (v1gsurY2016) | Comparable |
|-----------|----------------------|----------------------|-----------|
| GSUR source | v1 fallback | v1 fallback | Yes ✓ (same lookup file) |
| GSUR opportunity year | 2014 | 2016 | Correct per rule (both = EUROMOD system year) |
| GSUR alignment status | aligned | aligned | ✓ |
| Draw parameters | vw, n=99, seed=17 | vw, n=99, seed=17 | ✓ |
| Singles HHs | 1,669 | 1,662 | Similar |
| Couples HHs | 2,566 | 2,295 | 2017 lower by 271 HHs (~10.6%); within expected annual variation |
| Column count (singles) | 75 | 75 | ✓ |
| gsur mean (singles) | 0.094059 (year=2014 rates) | 0.096078 (year=2016 rates) | Different by design (different opp. years) |

Both FR_2015 and FR_2017 use the v1 fallback with correctly-keyed opportunity years.
They are internally consistent for provisional pooled use under the
`provisional_v1_fallback` label. Pooled estimates must carry that label until GSURv2
rates are available for all three opportunity years (2014, 2015/2016).

---

## 22. Files created

**Z: canonical storage (new files written this session):**

| File | Size |
|------|------|
| `Z:\...\Data\processed\fr\2017\fr_2017.parquet` | Stage 1 output |
| `Z:\...\Data\processed\fr\2017\fr_2017_singles.parquet` | Stage 1 output |
| `Z:\...\Data\processed\fr\2017\fr_2017_couples.parquet` | Stage 1 output |
| `Z:\...\Data\processed\fr\2017\fr_2017__colgroups.json` | Stage 1 sidecar |
| `Z:\...\Data\processed\fr\2017\singles_RURO_ready.parquet` | Stage 2 output |
| `Z:\...\Data\processed\fr\2017\couples_RURO_ready.parquet` | Stage 2 output |
| `Z:\...\Data\processed\fr\2017\singles_RURO_ready__colgroups.json` | Stage 2 sidecar |
| `Z:\...\Data\processed\fr\2017\couples_RURO_ready__colgroups.json` | Stage 2 sidecar |
| `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet` | Stage 3 output |
| `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json` | Stage 3 sidecar |
| `Z:\...\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet` | Stage 3 output |
| `Z:\...\Data\processed\fr\2017\couples_RURO_ready_RURO_draws__drawsmeta.json` | Stage 3 sidecar |
| `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet` | Stage 4 output |
| `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em__euromodmeta.json` | Stage 4 sidecar |
| `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | Stage 5 output (20.4 MB) |
| `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | Stage 5 output (37.2 MB) |
| `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` | Stage 5 sidecar |

**Local repo mirror (new files copied this session):**

| File | Size | Match |
|------|------|-------|
| `Data/processed/fr/fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | 21,356,869 bytes | SIZE_MATCH |
| `Data/processed/fr/fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | 38,961,983 bytes | SIZE_MATCH |
| `Data/processed/fr/fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` | 61,646 bytes | SIZE_MATCH |

**Report created:**
- `Results/P3a/multi_year_stage_M1/JMP_single_year_FR2017_replication_report_v1.md` (this document)

---

## 23. Files modified

**Post-run sidecar patch** (`fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` on Z:):
- Added `gsur_version: v1_fallback_opportunity_year_aligned`
- Added `gsur_opportunity_year: 2016`
- Updated `gsur_note` with explicit system year reference (FR_2016)

No other existing files were modified. Canonical FR_2016 files untouched.
Old FR_2017 files: none existed prior to this session — no overwrite issue.

---

## 24. What was not executed

Per authorization scope (not authorized in this task):

| Action | Status |
|--------|--------|
| FR_2015 re-run | Not executed (already rebuilt as `v1gsurY2014` in prior session) |
| Pooled stacking (`m1_stack_years.py` live run) | Not executed (dry-run only) |
| Final P3a/P3b pooled parquets | Not written |
| Estimation (`enh_RURO_estimate_FR.py`) | Not executed |
| Welfare computation | Not executed |
| P3b activation | Not executed |
| GSURv2 year-parameterization | Not executed (requires Eurostat + INSEE BDM acquisition) |
| Overwrite of canonical FR_2016 files | Not executed |
| FR_2018 run | Not executed (separate authorization required; P3b contingent) |

---

## 25. PASS / FAIL for FR_2017 MNL-input readiness

| Gate | Status |
|------|--------|
| Authorization memo exists (`docs/JMP_single_year_replication_2015_2017_authorization_v1.md`) | **PASS** |
| EUROMOD preflight completed; system=FR_2016, dataset=FR_2017_a2 confirmed from XML | **PASS** |
| Stage 1 (data prep) completed without errors | **PASS** |
| Stage 2 (RURO prep) completed without errors | **PASS** |
| Stage 3 (draws) completed; draw grid 100% complete; drawsmeta digest PASS | **PASS** |
| Stage 4 (EUROMOD combined) completed; system/dataset confirmed in euromodmeta | **PASS** |
| Stage 5 (MNL prep) completed without errors; all sanity checks PASS | **PASS** |
| Check A: drawsmeta digest (n_draws=99, vw, empirical, h_min=5.0, w_min=2.0) | **PASS** |
| Check B: EUROMOD system confirmed (FR_2016 / FR_2017_a2) | **PASS** |
| Check C: draw count uniformity (100 draws per HH; 1,662 singles deciders, 2,295 couples deciders) | **PASS** |
| Check D: tpr incidence 0.000%, twl incidence 0.254% — both below 1% threshold | **PASS** |
| GSUR cell-level: row0 rate=0.103 matches v1 year=2016 table exactly | **PASS** |
| Zero missing gsur (singles and couples) | **PASS** |
| Sidecar fields: gsur_version, gsur_opportunity_year, gsur_alignment_status | **PASS** |
| Z: output files written (SIZE_MATCH for all 3 MNL files) | **PASS** |
| Local mirror copied (SIZE_MATCH, all 3 files) | **PASS** |
| No canonical FR_2016 files overwritten | **PASS** |
| Stage M1 P3a dry-run: 2015 FOUND, 2016 FOUND, 2017 FOUND — **ready to run** | **PASS** |

**Overall verdict: PASS**

FR_2017 MNL-input parquets are complete, validated, and ready for Stage M1 provisional
dry-run. The output carries `v1_fallback_opportunity_year_aligned` labels and must not
be used in production P3a estimation without GSURv2 upgrade.

**Next step:** Issue Stage M1 execution authorization once all prerequisites are
confirmed — the P3a dry-run is ready. FR_2018 replication requires a separate
authorization (P3b contingent).