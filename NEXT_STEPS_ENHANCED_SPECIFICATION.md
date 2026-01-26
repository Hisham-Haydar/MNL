# Next Steps: Enhanced Minimal Specification

## What I Created For You

### ✅ New Specification: `estimation_spec_enhanced_minimal.yaml`

Based on your requirements:
1. ✅ **Singles parameters SEPARATED by gender** (already in ultra_minimal)
   - Males: `beta_l0_sm`, `beta_l_educL_sm`, `beta_l_educH_sm`, `beta_c_sm`
   - Females: `beta_l0_sf`, `beta_l_educL_sf`, `beta_l_educH_sf`, `beta_c_sf`

2. ✅ **Theta for couples consumption** (`theta_c`)
   - Box-Cox curvature for household consumption
   - Singles use log utility (more stable)
   - Only couples have flexible curvature

3. ✅ **Occupation/Education shifters** (educL, educH)
   - Low education dummy (educL)
   - High education dummy (educH)
   - Medium education is reference (omitted)
   - Gender-specific coefficients for singles and couples

**Total Parameters: 18** (vs 10 in ultra_minimal, 17 in baseline)

---

## Parameter Breakdown

### Leisure Utility (12 parameters)
```
Singles Male:    beta_l0_sm, beta_l_educL_sm, beta_l_educH_sm
Singles Female:  beta_l0_sf, beta_l_educL_sf, beta_l_educH_sf
Couples Male:    beta_l0_m,  beta_l_educL_m,  beta_l_educH_m
Couples Female:  beta_l0_f,  beta_l_educL_f,  beta_l_educH_f
```

### Consumption Utility (4 parameters)
```
Singles Male:      beta_c_sm
Singles Female:    beta_c_sf
Couples Household: beta_c, theta_c  ← NEW: Box-Cox curvature!
```

### Opportunity Parameters (6 parameters)
```
Hours:  beta_work, beta_pt1, beta_pt2, beta_ft
Wages:  beta_w0, sigma
```

---

## Key Decisions Made

### 1. **Education Instead of Occupation**
**Why?** Your data has `educL`, `educM`, `educH` dummies which are:
- Clean binary indicators
- Available for all groups
- Well-identified (variation in data)

**Alternative:** If you have occupation variables (e.g., `occ_white_collar`, `occ_service`), we can add those instead/in addition.

### 2. **Log Leisure Utility (theta_l = null)**
**Why?** From Phase 1/2 analysis:
- Theta parameters for leisure were UNIDENTIFIED
- All specs collapsed to log utility anyway
- Keeps model stable and parsimonious

**Your choice:** You CAN add `theta_l` parameters if you want, but expect:
- Higher condition number
- Potential identification issues
- Longer estimation time

### 3. **Theta ONLY for Couples Consumption**
**Why?**
- Couples have joint consumption decision (household level)
- More likely to have non-log curvature
- Singles kept simple (log) for stability
- Limits parameter explosion (1 theta vs 3)

### 4. **Focal Hours Indicators Added**
**Why?**
- Captures observed clustering in work hours
- Part-time 1 (~20h/week), Part-time 2 (~30h), Full-time (~40h)
- Standard in labor supply models
- Only 3 additional parameters

---

## How to Run

### Step 1: Quick Test with SciPy
```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/enhanced_minimal/scipy" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

**Expected runtime:** ~10-15 minutes (18 parameters, more complex than ultra_minimal)

### Step 2: Validate with GAMSPy CONOPT
```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/enhanced_minimal/gamspy" \
  --group joint \
  --solver gamspy-conopt \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "outputs/estimates/fr/enhanced_minimal/scipy/run_*/estimation_results.json" \
  --auto-timestamp \
  --verbose
```

**Expected runtime:** ~15-20 minutes

### Step 3: Check Identification
After estimation, check:
```
Condition number (κ):
  - κ < 100:     EXCELLENT
  - κ < 10,000:  GOOD (ultra_minimal had 17,000)
  - κ > 100,000: CONCERNING (pooled_leisure had 1 million)
```

---

## What to Expect

### Best Case Scenario ✅
- Condition number stays around 20,000-50,000 (reasonable)
- Education shifters are statistically significant
- Theta_c estimates around 0.2-0.5 (non-log curvature)
- Log-likelihood improves vs ultra_minimal by ~20-50 points

### Potential Issues ⚠️

1. **Education shifters not significant**
   - Education may not strongly affect leisure preferences
   - Solution: Drop educL/educH shifters, revert to simpler spec

2. **Theta_c hits bounds (0 or 5)**
   - If theta_c → 0: Couples also prefer log utility
   - If theta_c → 5: May be over-flexible, check identification
   - Solution: Fix theta_c = 0 and re-estimate

3. **Condition number explodes (>100,000)**
   - Model is over-parameterized for your data
   - Solution: Drop some shifters or fix theta_c = 0

---

## Modification Options

### Option A: Add More Occupation Variables
If you want to include occupation instead of education:

```yaml
leisure:
  shifters:
    # Replace educL/educH with:
    - variable: "occ_white_collar"  # If available in data
      coefficient: "beta_l_occ_wc"

    - variable: "occ_manual"
      coefficient: "beta_l_occ_manual"
```

**Check first:** Run this to see available occupation variables:
```bash
python -c "import pandas as pd; df = pd.read_parquet('Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_singles.parquet'); print([c for c in df.columns if 'occ' in c.lower()])"
```

### Option B: Add Age Effects
```yaml
leisure:
  shifters:
    - variable: "age_norm"
      coefficient: "beta_l_age_norm"
      description: "Age effect on leisure (demeaned)"

    - variable: "age_norm2"
      coefficient: "beta_l_age_norm2"
      description: "Age squared (lifecycle effects)"
```

**Cost:** +8 parameters (age_norm × 4 groups, age_norm2 × 4 groups)

### Option C: Add Children Effect (Females Only)
```yaml
leisure:
  shifters:
    - variable: "n_children"
      coefficient: "beta_l_n_children"
      description: "Number of children effect"
      gender_specific: true  # Only for females
```

**Cost:** +2 parameters (singles female, couples female)

### Option D: Add Theta for Singles Consumption
If you want Box-Cox curvature for singles too:

```yaml
consumption:
  coefficient: "beta_c"
  box_cox_exponent: "theta_c"  # Will create theta_c_sm, theta_c_sf, theta_c
```

**Cost:** +2 parameters (theta_c_sm, theta_c_sf)
**Warning:** May create identification issues (Phase 1 showed thetas collapsed to 0)

---

## Decision Matrix

| Specification | Parameters | Pros | Cons | Recommendation |
|---------------|-----------|------|------|----------------|
| **ultra_minimal** | 10 | Simple, robust, proven | No occupation, no couples theta | ✅ BASELINE |
| **enhanced_minimal** | 18 | Education, couples theta_c, focal hours | More complex | ✅ **START HERE** |
| **+ Age effects** | 26 | Lifecycle dynamics | High complexity | ⚠️ If needed |
| **+ Children** | 20 | Family effects | Moderate | ✅ Consider |
| **+ Singles thetas** | 20 | Full flexibility | Risk of non-ID | ❌ Avoid (Phase 1 evidence) |

---

## My Recommendation

### **Start with `enhanced_minimal` as-is (18 params)**

**Reasoning:**
1. Moderate increase from ultra_minimal (10 → 18)
2. Education is likely well-identified (binary dummies with variation)
3. Theta_c for couples is theoretically motivated (joint consumption decision)
4. Focal hours are standard and well-identified
5. Still avoids problematic leisure thetas

**Then iterate based on results:**
- If κ < 50,000 and education coefficients significant → Keep it! ✅
- If κ > 100,000 → Drop education shifters, keep theta_c
- If theta_c → 0 → Fix theta_c = 0 and re-estimate
- If you want more → Add age or children one at a time

---

## Next Commands

### Run the estimation:
```bash
# Copy this command
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/enhanced_minimal/scipy" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

### Monitor progress:
```bash
# In another terminal
tail -f outputs/estimates/fr/enhanced_minimal/scipy/run_*/estimation.log
```

### After completion, check results:
```bash
# Look at condition number and parameter estimates
cat outputs/estimates/fr/enhanced_minimal/scipy/run_*/estimation_summary.txt
```

---

## Questions to Answer

Before running, decide:

1. **Do you want OCCUPATION instead of EDUCATION?**
   - If yes: I need to know the column name (e.g., `occ_manager`, `occ_service`)
   - If no: Keep education (educL, educH)

2. **Do you want AGE effects?**
   - Yes → Add age_norm, age_norm2 (+8 params → 26 total)
   - No → Keep simple

3. **Do you want CHILDREN effect for females?**
   - Yes → Add n_children (+2 params → 20 total)
   - No → Keep as-is

4. **Do you want theta for SINGLES consumption too?**
   - Yes → Risk identification issues (Phase 1 evidence)
   - No → Keep theta only for couples (recommended)

---

## Summary

**I created:** `estimation_spec_enhanced_minimal.yaml` (18 parameters)

**It has:**
- ✅ Gender-specific singles parameters (as requested)
- ✅ Theta for couples consumption (as requested)
- ✅ Education shifters (occupation proxy)
- ✅ Focal hours indicators (standard practice)
- ✅ Log leisure utility (stable, from ultra_minimal)

**Next:** Run the estimation and check results!

**Timeline:** ~15 minutes to run, then we can iterate based on what we find.
