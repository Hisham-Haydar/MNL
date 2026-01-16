# 🎯 Column Reduction - Quick Reference Card

## ✅ CORRECTED - Ready to Use!

### The Right Command
```powershell
# Dry run (test first):
python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016 `
    --dry-run

# Actually reduce:
python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016
```

### What It Does
- **Reads:** `U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet` (488 MB)
- **Creates:** `U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet` (~65 MB)
- **Keeps:** 115 columns (all needed for any YAML spec)
- **Drops:** ~800-1100 columns (EUROMOD internals)
- **Savings:** ~420 MB (85-90% reduction)

### Update Pipeline (After Reduction)
Edit `run_enhanced_pipeline.ps1` line 94:
```powershell
$SCEN = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_${YEAR}_reduced"
```

### Why This Works
Step 6 reads `$EM_COMBINED` which is `$SCEN\combined_draws_em.parquet`  
So we reduce that ONE file, then point Step 6 to the reduced version!

### Status
✅ Script corrected  
✅ Compiles successfully  
✅ Dry-run tested  
⏳ Waiting for your go-ahead to run actual reduction

---

**That's it! Thanks for catching the wrong directory issue!** 🙏
