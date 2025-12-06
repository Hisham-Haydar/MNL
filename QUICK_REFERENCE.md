# RURO Pipeline - Quick Reference

## ⚡ Quick Commands

### Run Everything
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_pipeline.ps1
```

### Post-Estimation Only
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_post_estimation.ps1
```

### Debug Single Step
```powershell
cd U:\Desktop\Nizam_Hisham\MNL\scripts
python RURO_estimate_FR.py --help
```

---

## 📊 Performance Settings

### Current (Auto-Detected)
- **CPU Cores:** 32 (detected automatically)
- **Process Priority:** High
- **NumPy Threads:** 32
- **Numba Threads:** 32

### Manual Override
Edit `run_fr_2016_pipeline.ps1`, lines 73-81:
```powershell
$env:OMP_NUM_THREADS = "64"      # Change this
$env:MKL_NUM_THREADS = "64"      # Change this
$env:NUMBA_NUM_THREADS = "64"    # Change this
```

---

## 📁 Key File Locations

### Configuration
- **Pipeline:** `scripts/run_fr_2016_pipeline.ps1`
- **Post-Estimation:** `scripts/run_post_estimation.ps1`
- **Init Params:** `scripts/init_params_singles_template.csv`

### Results
- **Estimates:** `outputs/estimates/fr/2016/*.json`
- **Post-Est:** `outputs/post_estimation/fr/2016/*/`
- **Logs:** `outputs/logs/fr_2016_pipeline_*.md`

### Data
- **Raw:** `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt`
- **Processed:** `U:\EUROMOD-STORAGE\Data\processed\fr\2016\*.parquet`
- **MNL:** `U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet`

---

## 🔧 Troubleshooting

### Pipeline Hangs
✅ **FIXED** - Was using `$args` variable and `ProcessStartInfo`

### Wrong Python
✅ **FIXED** - Now auto-detects venv Python

### Column Errors
✅ **FIXED** - Column renaming and mapping updated

### Low CPU Usage
✅ **FIXED** - Auto-detects cores, sets high priority

### Post-Estimation No Output
- Check that estimation JSON files exist
- Run manually: `python scripts/RURO_post_estimation.py --results <file> --mnl-file <file> --out-dir <dir>`

---

## 💡 Tips

1. **Check Logs:** All output saved to `outputs/logs/fr_2016_pipeline_*.md`
2. **Resume Failed Run:** Comment out completed steps in PowerShell script
3. **Parallel Testing:** Copy script, change `$YEAR` variable
4. **Memory Issues:** Reduce `$N_DRAWS` from 99 to 50 or 25
5. **Speed Up:** Skip post-estimation (comment out Step 8)

---

## 🎯 Next Steps

1. **Debug Couples Estimation** - Run with `--verbose` flag
2. **Compute Standard Errors** - Implement gradient function
3. **Validate Results** - Compare with previous RURO papers
4. **Run Other Years** - Duplicate script for 2017, 2018, etc.
5. **Sensitivity Analysis** - Vary initial parameters

---

**Last Updated:** December 6, 2025
