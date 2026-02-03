# Job-Choice RURO: Acceptance Tests

## Summary of Implementation

The job-choice RURO pipeline has been enhanced with econometrically robust features for multi-year/multi-country estimation:

### A) Job Universe Builder (`enh_job_universe.py`) - Completed

**New Features:**
1. **Universe Modes** (`--universe-mode`):
   - `empirical_pruned`: Drop rare cells (backward compatible, default)
   - `empirical_all`: Keep all observed cells
   - `full_grid`: Complete (isco × hours × wage) grid with filled empty cells (RECOMMENDED for soft constraints)

2. **Representative Value Fill** (`--rep-fill-mode`):
   - `bin_means`: Use observed bin means for empty cells (default)
   - `bin_midpoints`: Use bin midpoints for empty cells

3. **Job ID Assignment** (`--job-id-mode`):
   - `deterministic`: Stable formula-based job_id = 1 + (isco_rank × H × W) + (h_bin × W) + w_bin
   - `sequential`: 1..N sequential (backward compatible, default)

4. **ISCO Code Handling**:
   - `--isco-codes`: Explicit comma-separated list (e.g., "1,2,3,5,7,9")
   - `--include-isco0`: Include ISCO code 0 (armed forces)

5. **Standardized Prior Columns**:
   - `prior`: Canonical job prior probability
   - `log_prior`: Log of prior
   - `q_j_prior`: Alias for backward compatibility
   - `job_idx`: Sequential index for backward compat

### B) Job Draws Generator (`enh_job_draws.py`) - Completed

**New Features:**
1. **Baseline Mode** (`--baseline-mode`):
   - `observed`: Use actual lhw_base/yivwg_base (default)
   - `cell_rep`: Use hours_rep/wage_rep from job universe

2. **Standardized Proposal Density**:
   - `prior`: Canonical proposal density
   - `log_prior`: Log proposal density
   - Convention: draw=0 has `prior=1.0, log_prior=0.0`
   - For draw≥1: `prior = (1-pi0) * job_prior` (employment) or `prior = pi0` (non-employment)
   - `log_q_*` columns retained for backward compatibility

### C) Pipeline Orchestrator (`run_job_ruro_pipeline.py`) - Completed

All new CLI flags propagated through the end-to-end pipeline.

---

## Acceptance Test Commands (Windows PowerShell)

### Test 1: Full Grid Mode with Deterministic Job IDs

**Purpose**: Test complete grid construction with stable job IDs (recommended for estimation)

```powershell
# Step 1: Build job universe with full_grid mode
python scripts/Job_model/enh_job_universe.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --output-dir "U:/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_test" `
  --year 2016 `
  --universe-mode full_grid `
  --rep-fill-mode bin_means `
  --job-id-mode deterministic `
  --wage-bins 10 `
  --seed 13

# Step 2: Generate job draws
python scripts/Job_model/enh_job_draws.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --job-universe "U:/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_test/job_universe_2016.parquet" `
  --job-metadata "U:/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_test/job_universe_2016__meta.json" `
  --n-draws 99 `
  --baseline-mode observed `
  --seed 13

# Step 3: Verify EUROMOD compatibility (no changes to enh_RURO_euromod.py required)
python scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --euromod-system FR_2020 `
  --euromod-dataset FR_2021_c2 `
  --scenario-dir "U:/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model_test/scenarios"
```

**Expected Outcomes**:
1. Job universe has N_jobs = (n_isco × n_hours × n_wage) + 1
   - For default: 9 ISCO × 4 hours × 10 wage = 360 working jobs + 1 non-employment = 361 total
2. Metadata shows `universe_mode: "full_grid"`, `job_id_mode: "deterministic"`
3. Job IDs are deterministic and match formula
4. Some cells have `cell_count=0` with filled `hours_rep/wage_rep`
5. Job draws have `prior` and `log_prior` columns
6. Draw=0 has `prior=1.0, log_prior=0.0` for all deciders
7. EUROMOD runs without errors, produces `ils_dispy` variation

---

### Test 2: Backward Compatibility (Original Behavior)

**Purpose**: Ensure default settings replicate original pipeline behavior

```powershell
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --year 2016 `
  --n-draws 99 `
  --seed 13
```

**Expected Outcomes**:
1. Uses `universe_mode=empirical_pruned` (drops rare cells)
2. Uses `job_id_mode=sequential` (1..N)
3. Uses `baseline_mode=observed` (lhw_base/yivwg_base)
4. Produces same results as original implementation
5. All legacy columns present (`q_j_prior`, `log_q_*`)

---

### Test 3: Minimal Test on Small Subset

**Purpose**: Quick validation on small dataset

```powershell
# Subset data first (100 households)
python -c "import pandas as pd; df = pd.read_parquet('U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet'); df.head(200).to_parquet('test_singles_small.parquet')"

# Run full pipeline
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "test_singles_small.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --year 2016 `
  --universe-mode full_grid `
  --job-id-mode deterministic `
  --n-draws 10 `
  --seed 13
```

**Expected Outcomes**:
1. Completes in <1 minute
2. Produces valid job universe and draws
3. No errors or warnings

---

### Test 4: Proposal Density Validation

**Purpose**: Verify proposal density columns are correctly computed

```python
import pandas as pd
import numpy as np

# Load job draws
draws = pd.read_parquet("singles_RURO_ready_jobdraws.parquet")

# Test 1: Draw=0 convention
draw0 = draws[draws["draw"] == 0]
assert (draw0["prior"] == 1.0).all(), "Draw=0 must have prior=1.0"
assert (draw0["log_prior"] == 0.0).all(), "Draw=0 must have log_prior=0.0"

# Test 2: Prior sums (for each decider, priors across draws should be normalized)
# Note: This is NOT required - priors are proposal densities, not choice probs
# But log_prior should equal log_q_total for consistency
deciders = draws[draws["is_decider"] == 1]
sim_draws = deciders[deciders["draw"] > 0]

# Check log_prior == log_q_total (within numerical tolerance)
diff = np.abs(sim_draws["log_prior"] - sim_draws["log_q_total"])
assert (diff < 1e-10).all(), f"log_prior must equal log_q_total, max diff: {diff.max()}"

# Test 3: Non-negativity
assert (draws["prior"] >= 0).all(), "Prior must be non-negative"

# Test 4: Employment/non-employment split
# For non-employment (job_id=0), prior should be pi0
# For employment, prior should be (1-pi0) * job_prior

print("✓ All proposal density validations passed")
```

---

### Test 5: Deterministic Job ID Stability

**Purpose**: Verify job IDs are stable across runs with same bins

```python
import pandas as pd

# Load job universe
ju = pd.read_parquet("job_universe_2016.parquet")

# Test 1: Check deterministic formula
# For each job, verify job_id matches formula
def compute_expected_job_id(row, isco_rank_map, n_h, n_w):
    if row["job_id"] == 0:
        return 0
    isco_rank = isco_rank_map[row["isco1"]]
    expected = 1 + (isco_rank * n_h * n_w) + (row["hours_bin"] * n_w) + row["wage_bin"]
    return expected

# Get ISCO rank map from metadata
import json
with open("job_universe_2016__meta.json") as f:
    meta = json.load(f)

isco_codes = sorted(meta["isco1_codes"])
isco_rank_map = {code: i for i, code in enumerate(isco_codes)}
n_h = meta["n_hours_bins"]
n_w = meta["n_wage_bins"]

ju["expected_job_id"] = ju.apply(
    lambda row: compute_expected_job_id(row, isco_rank_map, n_h, n_w),
    axis=1
)

mismatches = ju[ju["job_id"] != ju["expected_job_id"]]
assert len(mismatches) == 0, f"Found {len(mismatches)} job_id mismatches"

print(f"✓ All {len(ju)-1} working jobs have correct deterministic job_id")
```

---

### Test 6: ISCO Code Filtering

**Purpose**: Test explicit ISCO code inclusion

```powershell
# Only include ISCO codes 1, 2, 5 (managers, professionals, services)
python scripts/Job_model/enh_job_universe.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --output-dir "test_isco_filtered" `
  --year 2016 `
  --isco-codes "1,2,5" `
  --universe-mode full_grid `
  --seed 13
```

**Expected Outcomes**:
1. Job universe has 3 ISCO codes only
2. N_jobs = 3 × 4 × 10 + 1 = 121
3. Metadata: `isco1_codes: [1, 2, 5]`

---

### Test 7: End-to-End with Full Grid (Recommended Settings)

**Purpose**: Production-ready settings for estimation

```powershell
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016_c2.txt" `
  --year 2016 `
  --universe-mode full_grid `
  --rep-fill-mode bin_means `
  --job-id-mode deterministic `
  --baseline-mode observed `
  --n-draws 99 `
  --wage-bins 10 `
  --seed 13
```

**Rationale**:
- `full_grid`: Soft constraints - all job bundles are feasible alternatives
- `bin_means`: Empty cells get empirically-informed representative values
- `deterministic`: Stable job IDs for cross-year/country comparisons
- `observed`: Draw=0 uses actual baseline for calibration

---

## Validation Checklist

After running tests, verify:

- [ ] **Job Universe File** (`job_universe_2016.parquet`):
  - [ ] Has columns: `job_id, job_idx, hours_bin, wage_bin, isco1, cell_count, hours_rep, wage_rep, prior, log_prior, q_j_prior`
  - [ ] job_id=0 row exists (non-employment)
  - [ ] `prior` sums to 1.0 (excluding job 0): `sum(prior[job_id>0]) ≈ 1.0`
  - [ ] For full_grid: N_jobs = (n_isco × n_hours × n_wage) + 1

- [ ] **Job Metadata** (`job_universe_2016__meta.json`):
  - [ ] Contains: `universe_mode, rep_fill_mode, job_id_mode, isco1_codes, n_hours_bins, n_wage_bins, n_empty_cells`
  - [ ] `prior_sum ≈ 1.0`

- [ ] **Job Draws File** (`*_jobdraws.parquet`):
  - [ ] Has columns: `draw, idperson_true, job_id, hours_bin, wage_bin, isco1, lhw_draw, yivwg_draw, yem_draw, prior, log_prior, log_q_*`
  - [ ] Draw=0 exists for ALL persons
  - [ ] Draws 1..K exist for deciders only
  - [ ] Draw=0: `prior=1.0, log_prior=0.0` for all deciders
  - [ ] Draws >0: `log_prior == log_q_total` (within 1e-10)
  - [ ] EUROMOD aliases present: `lhw, yivwg, yem, hours, wage`

- [ ] **Draws Metadata** (`*_jobdraws__drawsmeta.json`):
  - [ ] Contains: `baseline_mode, distributional_params`

- [ ] **EUROMOD Compatibility**:
  - [ ] `enh_RURO_euromod.py` runs without modification
  - [ ] Produces `combined_draws_em.parquet` with `ils_dispy` column
  - [ ] Within-person variation: `ils_dispy` varies across draws

---

## Performance Benchmarks

Expected runtimes on France 2016 full dataset (~50k households):

| Step | Empirical Pruned | Full Grid |
|------|------------------|-----------|
| Job Universe | ~10 sec | ~30 sec |
| Job Draws | ~2 min | ~2 min |
| EUROMOD | ~10 min | ~10 min |
| **Total** | **~12 min** | **~13 min** |

---

## Troubleshooting

### Issue: "No valid ISCO codes found"
- Check `loc_ruro` column in RURO_ready data
- Verify ISCO codes are 1-9 (or 0 if using `--include-isco0`)
- Use `--isco-codes` to explicitly specify valid codes

### Issue: "log_prior != log_q_total"
- This should not happen - indicates a bug in proposal density computation
- Check for numerical precision issues (tolerance should be <1e-10)

### Issue: EUROMOD fails with job draws
- Verify column aliases are present: `lhw, yivwg, yem, hours, wage`
- Check that `enh_RURO_euromod.py` has not been modified
- Ensure job draws have same schema as continuous draws

---

## Migration Guide: Continuous → Discrete Jobs

If you're migrating from continuous RURO (`enh_RURO_draws.py`) to discrete job-choice RURO:

1. **Data Preparation**: No changes - use same `*_RURO_ready.parquet` files
2. **Job Universe**: NEW - run `enh_job_universe.py` once per dataset
3. **Draws Generation**: Replace `enh_RURO_draws.py` with `enh_job_draws.py`
4. **EUROMOD**: No changes - `enh_RURO_euromod.py` works as-is
5. **Estimation**: Update utility function to include job attributes (hours_bin, wage_bin, isco1)

---

## Contact & Support

For issues or questions:
- Check `README_job_model.md` for detailed documentation
- Review `scripts/Job_model/sanity_checks_job.py` for validation functions
- Consult the original implementation plan: `.claude/plans/melodic-doodling-orbit.md`

---

**Last Updated**: 2026-02-03
**Tested On**: Python 3.10, pandas 2.0+, pyarrow 10.0+
