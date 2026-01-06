# RURO Pipeline - Quick Start Guide

## 🚀 Running the Complete Pipeline

### Prerequisites

1. **Activate virtual environment**:
   ```powershell
   cd U:\Desktop\Nizam_Hisham\MNL
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify data is in place**:
   - Raw data: `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt`
   - EUROMOD: `U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`

### Option 1: Automated Run (Recommended)

Run the complete pipeline with a single command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

**What it does**:
- Runs all 7 steps automatically
- Skips intermediate steps if files already exist
- Uses warm start if previous estimation exists
- Generates detailed logs with timestamps
- Creates post-estimation diagnostics

**Expected runtime**:
- First run (full pipeline): 30-60 minutes
- Subsequent runs (with warm start): 5-15 minutes

### Option 2: Manual Step-by-Step

For debugging or partial runs:

```powershell
# Step 1: Data Prep
python scripts\enhanced\enh_france_data_prep.py --year 2016 --raw-dir "U:\EUROMOD-STORAGE\Data\raw" --out-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" --system-year 2015 --export-format parquet

# Step 2: RURO Prep
python scripts\enhanced\enh_RURO_prep.py --processed-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" --base-year 2016 --export-format parquet

# Step 3: Draws
python scripts\enhanced\enh_RURO_draws.py --singles-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" --couples-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet" --n-draws 99 --wage-spec vw

# Step 4: EUROMOD (slowest step)
python scripts\enhanced\enh_RURO_euromod.py --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" --euromod-system FR_2015 --euromod-dataset FR_2016 --scenario-dir "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016"

# Step 5: GSUR (optional)
python scripts\enhanced\enh_prepare_FR_gsur.py --input "Data\external\FR_gsur.xlsx" --output-dir "Data\external"

# Step 6: MNL Dataset
python scripts\enhanced\enh_RURO_prep_mnl_basic.py --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" --euromod-combined "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet" --gsur-file "Data\external\FR_gsur_ruro.parquet" --out-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" --wage-spec vw --year 2016 --skip-csv

# Step 7: Estimation
python scripts\enhanced\enh_RURO_estimate_FR.py --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" --joint --wage-spec vw --optimizer L-BFGS-B --maxiter 5000 --use-numba --n-jobs 8 --post-estimation --out-file "outputs\estimates\fr\2016\fr_2016_joint.json"
```

## 📁 Pipeline Files (All in scripts/enhanced/)

### Core Pipeline Scripts
1. `enh_france_data_prep.py` - Step 1: Data preparation
2. `enh_RURO_prep.py` - Step 2: RURO-ready datasets
3. `enh_RURO_draws.py` - Step 3: Opportunity draws
4. `enh_RURO_euromod.py` - Step 4: EUROMOD simulation
5. `enh_prepare_FR_gsur.py` - Step 5: GSUR unemployment data
6. `enh_RURO_prep_mnl_basic.py` - Step 6: MNL dataset
7. `enh_RURO_estimate_FR.py` - Step 7: Estimation

### Supporting Files
- `run_enhanced_pipeline.ps1` - Automated pipeline runner
- `estimation_spec.yaml` - Model specification
- `estimation_engine.py` - Optimization engine
- `estimation_utils.py` - Utility functions
- `parallel_estimation.py` - Parallel processing
- `enh_RURO_post_estimation.py` - Post-estimation analysis
- `diagnose_pre_estimation.py` - Pre-estimation diagnostics

### Documentation
- `PIPELINE_GUIDE.md` - Complete documentation (this file)
- `QUICK_START.md` - Quick reference (this file)
- `README_POST_ESTIMATION.md` - Post-estimation guide

## 📊 Output Files

After successful run, you'll have:

```
U:\EUROMOD-STORAGE\Data\processed\fr\2016\
├── fr_2016.parquet                              # Step 1
├── singles_RURO_ready.parquet                   # Step 2
├── couples_RURO_ready.parquet                   # Step 2
├── singles_RURO_ready_RURO_draws.parquet        # Step 3
├── couples_RURO_ready_RURO_draws.parquet        # Step 3
└── fr_2016_RURO_mnl.parquet                     # Step 6

U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\
└── combined_draws_em.parquet                    # Step 4

U:\Desktop\Nizam_Hisham\MNL\outputs\
├── estimates\fr\2016\
│   ├── fr_2016_joint.json                       # Step 7 (results)
│   └── fr_2016_joint_params.csv                 # Parameters
├── post_estimation\fr\2016\
│   └── fr_2016_joint_post_estimation.html       # Diagnostics
└── logs\
    └── fr_2016_enhanced_pipeline_[timestamp].md # Execution log
```

## ✅ Verifying Success

### Quick Check
```powershell
# Check if estimation completed successfully
python -c "import json; f = open('outputs/estimates/fr/2016/fr_2016_joint.json'); d = json.load(f); print(f\"Converged: {d['converged']}, LL: {d['log_likelihood']:.2f}\")"
```

### View Results
```powershell
# Open post-estimation report in browser
Invoke-Item "outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html"

# View parameter estimates
Get-Content "outputs\estimates\fr\2016\fr_2016_joint_params.csv" | Select-Object -First 20
```

## 🔧 Configuration Options

Edit [`run_enhanced_pipeline.ps1`](run_enhanced_pipeline.ps1:32) to customize:

```powershell
$YEAR = 2016              # Data year
$N_DRAWS = 99             # Number of counterfactual draws
$WAGE_SPEC = "vw"         # "vw" = variable wages, "fw" = fixed wages
$MAX_ITER = 5000          # Maximum optimizer iterations
$SKIP_IF_MNL_EXISTS = $true  # Skip Steps 1-6 if data exists
```

## 🐛 Common Issues

### Issue: Not in virtual environment
```
ERROR: Not running in .venv!
```
**Solution**: Run `.\.venv\Scripts\Activate.ps1` first

### Issue: EUROMOD exits with code 1
```
FAILED: Run EUROMOD on all draws (exit code: 1)
```
**Solution**: This is often a false alarm. Check if `combined_draws_em.parquet` was created. The script handles this automatically.

### Issue: Estimation not converging
**Solution**:
1. Use warm start with `--init-params` (automatic in pipeline script)
2. Increase `$MAX_ITER` to 10000
3. Check data quality (NaN/inf values)

## 📖 Full Documentation

For detailed documentation, see:
- [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) - Complete guide with all details
- [README_POST_ESTIMATION.md](README_POST_ESTIMATION.md) - Post-estimation analysis

## 🆘 Support

1. Check log file: `outputs\logs\fr_2016_enhanced_pipeline_[timestamp].md`
2. Review diagnostics: `outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html`
3. Consult [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) troubleshooting section

---

**Version**: Enhanced Pipeline v2.0
**Last Updated**: 2026-01-03
