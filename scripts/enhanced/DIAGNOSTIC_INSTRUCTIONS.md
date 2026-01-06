# Pre-Estimation Diagnostic Instructions

## Summary

Your RURO pipeline completed successfully! Before proceeding to estimation, run comprehensive diagnostics to verify data quality.

## What Happened in Your Pipeline Run

✅ **All 6 steps completed successfully** (logged to `server/enh_pipeline_FR_2016_20260102_233648.txt`)

### Pipeline Summary:
1. **Step 1: Data Prep** - Processed France 2016 SILC data
2. **Step 2: RURO Prep** - Created singles (1,676 deciders) and couples (2,577 households)
3. **Step 3: Draw Generation** - Generated 100 draws (0-99) for each decider
4. **Step 4: EUROMOD Simulation** - Simulated 1,087,300 person-draw rows
5. **Step 5: GSUR Integration** - Merged unemployment rates
6. **Step 6: MNL Datasets** - Created:
   - Singles: 167,600 rows (1,676 households × 100 draws)
   - Couples: 257,700 rows (2,577 households × 100 draws)
   - Combined: 425,300 total rows

### Final Outputs:
```
U:\EUROMOD-STORAGE\Data\processed\fr\2016\
  ├─ singles_RURO_ready.parquet          (Step 2 output)
  ├─ couples_RURO_ready.parquet          (Step 2 output)
  ├─ singles_RURO_ready_RURO_draws.parquet (Step 3 output)
  ├─ couples_RURO_ready_RURO_draws.parquet (Step 3 output)
  ├─ fr_2016_RURO_mnl__singles.parquet   (Step 6 - READY FOR ESTIMATION)
  ├─ fr_2016_RURO_mnl__couples.parquet   (Step 6 - READY FOR ESTIMATION)
  └─ fr_2016_RURO_mnl__mnlmeta.json      (Metadata)

U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\
  └─ combined_draws_em.parquet           (Step 4 output)
```

### Only Warnings Observed:
- ⚠️ Performance warnings about DataFrame fragmentation (harmless - just slower pandas operations)
- ⚠️ Deprecation warning for `datetime.utcnow()` (cosmetic - doesn't affect results)

## Run Diagnostics Before Estimation

### On the Server (Recommended):

```powershell
cd U:\Desktop\Nizam_Hisham\MNL
.\scripts\enhanced\run_diagnostics.ps1
```

This will check:

### 1. **Decider Identification Quality**
- Which method was used to identify deciders?
  - ✅ **Preferred:** `hh_IsHead` / `hh_IsPartner` (household structure-based)
  - ✅ **Standard:** `ruro_decider` flag (from Step 2)
  - ⚠️ **Fallback:** `lma==1` (labor market attachment - only if others missing)
- What % of observations used each method?

### 2. **Worker Status Consistency**
- Compare baseline `is_worker` (from Step 1) with actual working draws (Step 4)
- Check: Do baseline workers (`is_worker==1`) have `hours>0` in their draw==0?
- Verify: RURO correctly offers hypothetical jobs to non-workers

### 3. **EUROMOD Input Sanity**
- ✅ Non-workers (hours<=0) have `loc=-1` (no occupation)
- ✅ Workers (hours>0) have positive employment income (`yem>0`)
- ✅ Workers have zero unemployment benefits (`bun==0`)
- ✅ Benefit values are sensible

### 4. **MNL Dataset Completeness**
- All required columns present:
  - Singles: `idhh`, `draw`, `consumption`, `leisure`, `hours`, `wage`, `u_rate` (GSUR)
  - Couples: `idhh`, `draw`, `consumption`, `leisure_male`, `leisure_female`, `hours_male`, `hours_female`, `u_rate_male`, `u_rate_female`
- No missing values in key columns
- Reasonable value ranges

### 5. **LMA Usage Analysis**
- Where was `lma` used in the pipeline?
- Was it informative (had variation + some 1s)?
- Impact on worker identification

## Expected Diagnostic Results

### ✅ **GOOD** (proceed to estimation):
- Deciders identified using `hh_IsHead`/`hh_IsPartner` or `ruro_decider`
- All baseline workers have hours>0 in draw==0
- EUROMOD inputs are consistent (loc, yem, bun)
- MNL datasets complete with no missing GSUR data
- LMA only used as fallback (if at all)

### ⚠️ **REVIEW NEEDED**:
- If `lma` was used as primary decider identification method
- If baseline workers have hours<=0 in draw==0
- If EUROMOD inputs have inconsistencies (loc!=-1 for non-workers, etc.)
- If MNL datasets have missing values or columns

### ❌ **ERRORS** (fix before estimation):
- Missing required columns in MNL datasets
- Missing GSUR unemployment rates
- Widespread EUROMOD input inconsistencies

## After Diagnostics

### If All Checks Pass:
✅ **Proceed to MNL estimation** using your final datasets:
- `fr_2016_RURO_mnl__singles.parquet`
- `fr_2016_RURO_mnl__couples.parquet`

### If Issues Found:
1. Review specific warnings in diagnostic output
2. Check pipeline log: `server/enh_pipeline_FR_2016_20260102_233648.txt`
3. Fix issues and re-run affected pipeline steps
4. Re-run diagnostics

## What About `lma`?

**Key Finding:** The pipeline logic is **sound** regarding `lma` usage:

### Where `lma` is Used (as optional fallback):

1. **Step 1 (RURO_prep)** - Worker identification:
   - IF `lma` exists AND is informative (has variation + some 1s):
     - Use: `is_worker = (lma==1) & (lhw>0)`
   - ELSE:
     - Use: `is_worker = (les==3) & (lhw>0)` (employment status)

2. **Step 4 (RURO_euromod)** - EUROMOD template:
   - IF `lma` exists: pass it through to EUROMOD
   - ELSE: assume `lma=1` for all (fallback)
   - **BUT:** Working status in draws uses `hours>0` **ONLY** (not lma)

3. **Step 6 (MNL prep)** - Decider restriction (LAST fallback):
   - Priority: `hh_IsHead`/`hh_IsPartner` > `ruro_decider` > `lma==1`
   - Only uses `lma==1` if other methods missing

### Why This is Correct:
- `lma` (labor market attachment) is a legitimate SILC/EUROMOD variable
- Using it as a fallback is reasonable when better methods aren't available
- **RURO draws use `hours>0`** to determine working status (correct for hypothetical scenarios)
- The pipeline never *requires* `lma` - it always has fallbacks

## Diagnostic Output

After running diagnostics, you'll get:

1. **Console output** with colored status indicators:
   - ✅ Green checks for passed tests
   - ⚠️ Yellow warnings for review items
   - ❌ Red errors for critical issues

2. **JSON report** saved to:
   ```
   c:\Users\hisham\Desktop\Nizam_Hisham\MNL\outputs\diagnostics\pre_estimation_diagnostics.json
   ```

## Questions to Answer Before Estimation

The diagnostics will answer:

1. ✅ **Are deciders correctly identified?** (check method used)
2. ✅ **Is worker status consistent?** (baseline vs draws)
3. ✅ **Are EUROMOD inputs valid?** (loc, yem, bun)
4. ✅ **Are MNL datasets complete?** (no missing data)
5. ✅ **Was lma used appropriately?** (only as fallback)

## Next Steps

```
1. Run diagnostics    → .\scripts\enhanced\run_diagnostics.ps1
2. Review output      → Check for ✅ / ⚠️ / ❌
3. Fix any issues     → Re-run affected pipeline steps if needed
4. Proceed to MNL     → Estimate labor supply model on final datasets
```

---

**Status:** ✅ Pipeline completed successfully - ready for diagnostics!
