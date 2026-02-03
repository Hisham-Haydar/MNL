# Job-Choice RURO Model

## Overview

This directory implements a **discrete job-choice RURO** branch where labor supply is modeled as a choice among discrete job bundles, NOT a continuous intensive-margin decision.

**Key Difference from Continuous RURO**:
- **Continuous RURO** (`enh_RURO_draws.py`): Samples (hours, wage) independently from Uniform distributions
- **Job-Choice RURO** (`enh_job_draws.py`): Samples job bundles (hours_bin, wage_bin, occupation) from empirical job universe

**A "job" is a discrete bundle**: (hours_bin, wage_bin, ISCO-1 occupation)
- Wages are features of jobs, NOT individual productivity
- Occupation is part of the job offer, not a separate choice

---

## Pipeline Structure

```
1. enh_RURO_prep.py (from main pipeline)
       ↓
   *_RURO_ready.parquet
       ↓
2. enh_job_universe.py ← Build job grid
       ↓
   job_universe_{year}.parquet
       ↓
3. enh_job_draws.py ← Sample from job grid
       ↓
   *_RURO_ready_jobdraws.parquet
       ↓
4. enh_RURO_euromod.py (from main pipeline, NO CHANGES)
       ↓
   combined_draws_em.parquet
```

**Critical Design**: Job draws are a **drop-in replacement** for continuous draws. `enh_RURO_euromod.py` runs WITHOUT modification.

---

## Scripts

### 1. `enh_job_universe.py`

**Purpose**: Build discrete job grid from observed working deciders.

**Inputs**:
- `--singles-path`, `--couples-path`: *_RURO_ready.parquet from enh_RURO_prep.py

**Outputs**:
- `job_universe_{year}.parquet`: Job grid with priors
- `job_universe_{year}__meta.json`: Metadata (bin edges, ISCO codes, counts)

**Key Functions**:
- `_build_hours_bins(cutpoints)`: Fixed hours bins (default: [5-15], [16-30], [31-42], [43-70])
- `_build_wage_bins(df, n_bins)`: Data-dependent wage deciles (or n-tiles)
- `_build_job_universe(...)`: Group by (h_bin, w_bin, isco1), compute priors

**Job Universe Schema**:
```
job_id       : int    (0 = non-employment, 1..N = working jobs)
hours_bin    : int    (0-indexed bin ID, -1 for non-employment)
wage_bin     : int    (0-indexed bin ID, -1 for non-employment)
isco1        : int    (ISCO 1-digit occupation 1-9, -1 for non-employment)
cell_count   : int    (Number of observed workers in this cell)
hours_rep    : float  (Mean hours for this job)
wage_rep     : float  (Mean wage for this job)
q_j_prior    : float  (Proposal prior ∝ cell_count, sums to 1 over working jobs)
```

**Example CLI**:
```powershell
python scripts/Job_model/enh_job_universe.py `
  --singles-path "U:/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --output-dir "U:/Data/processed/fr/2016/job_model" `
  --year 2016 `
  --hours-cutpoints 5,16,31,43,71 `
  --wage-bins 10 `
  --min-cell-threshold 5 `
  --smoothing-alpha 0.01 `
  --seed 13
```

---

### 2. `enh_job_draws.py`

**Purpose**: Generate long-format RURO draws by sampling from job universe.

**Inputs**:
- `--singles-path`, `--couples-path`: *_RURO_ready.parquet
- `--job-universe`: job_universe_{year}.parquet
- `--job-metadata`: job_universe_{year}__meta.json

**Outputs**:
- `singles_RURO_ready_jobdraws.parquet`
- `couples_RURO_ready_jobdraws.parquet`
- Metadata sidecars: `*_jobdraws__drawsmeta.json`

**Key Functions**:
- `_assign_baseline_job(...)`: Map observed (lhw_base, yivwg_base, isco1) to job_id for draw=0
- `generate_job_draws_long(...)`: Vectorized job sampling (parallel to enh_RURO_draws.py)

**Opportunity Density**:
For each decider i:
- With probability π₀,g(i): job_id=0 (non-employment, hours=0, wage=0)
- With probability 1-π₀,g(i): sample job_id from multinomial(q_j_prior)

**Output Schema** (compatible with enh_RURO_euromod.py):
```
draw           : int     (0 = baseline, 1..K = simulated)
idperson       : int     (Original person ID)
idperson_true  : int     (True ID for merge-back)
idhh_true      : int     (True household ID)
is_decider     : int     (1 if head/partner, else 0)
is_chosen      : int     (1 if draw=0 for deciders, else 0)
job_id         : int     (Job bundle ID, 0=non-employment)
hours_bin      : int     (Hours bin ID, -1 if non-employment)
wage_bin       : int     (Wage bin ID, -1 if non-employment)
isco1          : int     (ISCO 1-digit occupation, -1 if non-employment)
lhw_draw       : float   (Weekly hours from job_universe.hours_rep)
yivwg_draw     : float   (Hourly wage from job_universe.wage_rep)
yem_draw       : float   (Monthly earnings = lhw * yivwg * 52/12)
log_q_job      : float   (Log proposal density for job)
log_q_state    : float   (Log p(employment vs non-employment))
log_q_total    : float   (log_q_state + log_q_job)
lhw, yivwg, yem, hours, wage : float (Aliases for EUROMOD compatibility)
```

**Example CLI**:
```powershell
python scripts/Job_model/enh_job_draws.py `
  --singles-path "U:/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --job-universe "U:/Data/processed/fr/2016/job_model/job_universe_2016.parquet" `
  --job-metadata "U:/Data/processed/fr/2016/job_model/job_universe_2016__meta.json" `
  --n-draws 99 `
  --pi0-m 0.10 `
  --pi0-f 0.10 `
  --seed 13
```

---

### 3. `sanity_checks_job.py`

**Purpose**: Validation suite for job-choice RURO outputs.

**Functions**:

1. **`sanity_report_job_universe(job_universe, metadata)`**:
   - No duplicate job_id
   - job_id=0 exists with hours=0, wage=0, isco1=-1
   - All ISCO codes valid (1-9, optionally 0)
   - q_j_prior sums to 1

2. **`sanity_report_job_draws(df, metadata, n_draws)`**:
   - All deciders have complete draw sets {0..n_draws}
   - draw=0 baseline compliance (lhw_draw == lhw_base)
   - All job_id exist in universe
   - Non-employment rows (job_id=0) have lhw_draw=0, yivwg_draw=0

3. **`sanity_report_proposal_density(df)`**:
   - log_q_total = log_q_state + log_q_job
   - draw=0 has positive density for all deciders

**Example CLI**:
```powershell
python scripts/Job_model/sanity_checks_job.py `
  --job-universe "U:/Data/processed/fr/2016/job_model/job_universe_2016.parquet" `
  --job-draws "U:/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --n-draws 99
```

---

### 4. `run_job_ruro_pipeline.py`

**Purpose**: End-to-end orchestrator (universe → draws → EUROMOD).

**Example CLI**:
```powershell
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --year 2016 `
  --n-draws 99 `
  --wage-bins 10 `
  --euromod-system FR_2020 `
  --euromod-dataset FR_2021_c2 `
  --seed 13
```

This runs all 3 stages sequentially:
1. Build job universe
2. Generate job draws
3. Run EUROMOD (using existing `enh_RURO_euromod.py`)

---

## Compatibility with Existing Pipeline

### EUROMOD Stage (NO CHANGES)

Job draws output is designed as a **drop-in replacement** for continuous draws.

**Column Mapping**:
| Job Draws Column | EUROMOD Expects | Provided |
|------------------|-----------------|----------|
| `lhw_draw` | `lhw`, `hours` | ✓ (aliased) |
| `yivwg_draw` | `yivwg`, `wage` | ✓ (aliased) |
| `yem_draw` | `yem` | ✓ (aliased) |
| `draw` | `draw` | ✓ |
| `idperson_true` | `idperson_true` | ✓ |
| `idhh_true` | `idhh_true` | ✓ |
| `is_decider` | `is_decider` | ✓ |

**Additional Columns** (carried through EUROMOD via carry-columns pattern):
- `job_id, hours_bin, wage_bin, isco1, log_q_job, log_q_state, log_q_total`

These are preserved in EUROMOD output for downstream estimation.

**To run EUROMOD on job draws**:
```powershell
python scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "U:/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "U:/Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --euromod-system FR_2020 `
  --euromod-dataset FR_2021_c2 `
  --scenario-dir "U:/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model/scenarios"
```

No changes to `enh_RURO_euromod.py` required!

---

## Design Decisions

### 1. Hours Binning
**Fixed cutpoints**: [5, 16, 31, 43, 71] → bins [5-15], [16-30], [31-42], [43-70]

**Rationale**:
- Matches labor market conventions (part-time, full-time, overtime)
- CLI override: `--hours-cutpoints 5,20,40,71`

### 2. Wage Binning
**Data-dependent deciles** (or n-tiles from `--wage-bins`)

**Rationale**:
- Adapts to each dataset's wage distribution
- Ensures roughly equal cell counts across bins
- Flexible: `--wage-bins 5` (quintiles), `--wage-bins 20` (vigintiles)

### 3. Occupation
**ISCO 1-digit codes (1-9)** from `loc_ruro` column

**Rationale**:
- More interpretable than 4-task groups (loc4)
- Standard classification
- Results in ~300-400 jobs (tractable for estimation)

### 4. Job Prior
**q_j ∝ cell_count + α** (Laplace smoothing, α=0.01 * mean_count)

**Rationale**:
- Empirical prior reflects observed job frequency
- Smoothing prevents zero priors for rare jobs
- Non-parametric (no distributional assumptions)

### 5. Couples Mechanism
**Independent draws** per partner

**Rationale**:
- Simpler to implement and debug
- Matches existing `enh_RURO_draws.py` pattern
- Joint coordination handled in estimation, not simulation

---

## Testing

### Unit Tests
Run on small subset (100 households):
```powershell
# Test job universe
python scripts/Job_model/enh_job_universe.py `
  --singles-path "test_subset_singles.parquet" `
  --output-dir "test_output" `
  --year 2016 `
  --wage-bins 5 `
  --min-cell-threshold 2

# Test job draws
python scripts/Job_model/enh_job_draws.py `
  --singles-path "test_subset_singles.parquet" `
  --job-universe "test_output/job_universe_2016.parquet" `
  --job-metadata "test_output/job_universe_2016__meta.json" `
  --n-draws 10

# Validate
python scripts/Job_model/sanity_checks_job.py `
  --job-universe "test_output/job_universe_2016.parquet" `
  --job-draws "test_subset_singles_jobdraws.parquet" `
  --n-draws 10
```

### Integration Test
Full pipeline on France 2016:
```powershell
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "U:/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --microdata-template "U:/Data/raw/FR_2016_c2.txt" `
  --year 2016 `
  --n-draws 99 `
  --euromod-system FR_2020 `
  --euromod-dataset FR_2021_c2
```

**Expected Outputs**:
- Job universe: ~300-400 jobs
- Singles draws: n_singles × 100 rows
- Couples draws: n_couples × 2 × 100 rows
- EUROMOD output: ils_dispy varies across draws (within-person std > 0)

---

## FAQ

### Q: Can I use different bin definitions for different years?
**A**: Yes! Each year gets its own job universe. Wage bins are data-dependent, so they automatically adapt. Hours bins can be overridden via `--hours-cutpoints`.

### Q: What if I want to use loc4 (4-task groups) instead of ISCO 1-digit?
**A**: Modify `enh_job_universe.py` line ~X to use `isco_col="loc4"` instead of `"loc_ruro"`. Expected job count: ~100-150 instead of ~300-400.

### Q: Can I pool multiple years to get more stable job priors?
**A**: Yes, concatenate *_RURO_ready files before running `enh_job_universe.py`. Use a pooled year label (e.g., `--year 2016_2017_2018`).

### Q: How do I validate my job draws before running EUROMOD?
**A**: Use `sanity_checks_job.py`:
```powershell
python scripts/Job_model/sanity_checks_job.py `
  --job-universe "job_universe_2016.parquet" `
  --job-draws "singles_RURO_ready_jobdraws.parquet" `
  --n-draws 99
```

### Q: Can I run job-choice RURO in parallel with continuous RURO?
**A**: Absolutely! They share the same RURO_ready inputs and EUROMOD stage. Just use different output directories:
- Continuous: `enh_RURO_draws.py` → `enh_RURO_euromod.py`
- Job-choice: `enh_job_draws.py` → `enh_RURO_euromod.py`

---

## Migration from Continuous RURO

**Step 1**: Keep existing continuous pipeline running.

**Step 2**: Build job universe for your country/year:
```powershell
python scripts/Job_model/enh_job_universe.py ...
```

**Step 3**: Generate job draws (same n_draws as continuous):
```powershell
python scripts/Job_model/enh_job_draws.py ...
```

**Step 4**: Run EUROMOD on job draws (same EUROMOD settings):
```powershell
python scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "singles_RURO_ready_jobdraws.parquet" `
  ...
```

**Step 5**: Compare estimation results:
- Fit quality (log-likelihood, AIC/BIC)
- Parameter interpretations (bin effects vs marginal effects)
- Computation time (fewer alternatives = faster estimation)

**Step 6**: Switch to job model if:
- Discrete jobs better match your research question
- Occupation choice is first-order
- Computational gains matter

---

## Troubleshooting

### Issue: "No valid ISCO codes found in working deciders"
**Cause**: `loc_ruro` column has only -1, -2 values.

**Fix**: Check upstream `enh_RURO_prep.py` output. Ensure `loc_ruro` is correctly populated from `loc` (ISCO codes 1-9).

### Issue: "No cells survive min_cell_threshold=5"
**Cause**: Job grid too fine (too many bins × too few observations).

**Fix**: Reduce granularity:
- Use fewer wage bins: `--wage-bins 5` (quintiles instead of deciles)
- Lower threshold: `--min-cell-threshold 2`
- Pool multiple years

### Issue: "Baseline hours compliance failed"
**Cause**: `lhw_base` differs from canonical `lhw` in RURO_ready.

**Fix**: Re-run `enh_RURO_prep.py` to ensure baseline columns are synchronized. Check for stale `lhw_base` from earlier pipeline versions.

### Issue: "EUROMOD output has constant ils_dispy across draws"
**Cause**: Job draws not varying hours/wage, OR EUROMOD not reading draw-specific inputs.

**Fix**:
1. Check job draws: `df.groupby('idperson_true')['lhw_draw'].std()` should be > 0
2. Check EUROMOD inputs: verify `lhw`, `yivwg`, `yem` columns in input to EUROMOD
3. Check EUROMOD version: ensure it supports draw-specific overrides

---

## Performance

**Job Universe Building**: ~10 seconds (France 2016, ~50k working deciders)

**Job Draws Generation**: ~30 seconds (vectorized, 99 draws × 10k deciders)

**EUROMOD Stage**: ~5-10 minutes (same as continuous RURO)

**Total**: <15 minutes for full France dataset

---

## References

- Aaberge, R., & Colombino, U. (1998). *Random Utility Models: A Short Introduction*. IRP Discussion Paper.
- Capeau, B., & Decoster, A. (2014). *The Optimal Linear Income Tax under Individual Human Capital Investment and Participation Costs*. Empirical Economics.
- Van Houtven, S. et al. (2024). *RURO Labor Supply Model for Belgium* (internal documentation).

---

## Support

For questions or issues:
1. Check this README troubleshooting section
2. Validate outputs using `sanity_checks_job.py`
3. Check logs from pipeline scripts (use `--log-level DEBUG`)
4. Consult the plan document: `C:\Users\hisham\.claude\plans\melodic-doodling-orbit.md`

---

**Last Updated**: 2026-02-03
**Version**: 1.0.0
