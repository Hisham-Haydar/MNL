# Incremental Specification Testing Plan

## Strategy: Add Complexity One Step at a Time

**Goal:** Find the sweet spot between model richness and identification

**Method:** Start simple, add parameters incrementally, STOP when identification degrades

---

## Specification Roadmap

### ✅ Spec 0: ultra_minimal (BASELINE - 10 params)
**Status:** VALIDATED in Phase 1/2
- Condition number: 1.7e4 (GOOD)
- SciPy = GAMSPy (ROBUST)
- LL = -7862.91

---

### 🔄 Spec 1: enhanced_minimal_v1 (18 params, +8 from baseline)

**What's Added:**
- Education shifters for leisure: 8 params
  - beta_l_educL_sm, beta_l_educH_sm (singles male)
  - beta_l_educL_sf, beta_l_educH_sf (singles female)
  - beta_l_educL_m, beta_l_educH_m (couples male)
  - beta_l_educL_f, beta_l_educH_f (couples female)
- Theta for couples consumption: 1 param
  - theta_c
- Focal hours indicators: 3 params
  - beta_pt1, beta_pt2, beta_ft

**Expected:**
- LL improvement: ~30-60 points
- Condition number: 30,000-60,000
- Education coefficients: Negative for educH (higher edu → lower leisure value)

**Decision:**
- If κ < 80,000 and educL/educH significant → PROCEED to Spec 2
- If κ > 100,000 → STOP, use ultra_minimal instead
- If educL/educH not significant → Drop education, try Spec 2 without it

**Run Command:**
```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/incremental/v1_enhanced_minimal" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

---

### 🔄 Spec 2: enhanced_minimal_v2 (21 params, +3 from v1)

**What's Added (to v1):**
- Hours opportunity interactions: 3 params
  - beta_gsur (unemployment rate × working)
  - beta_work_educL (low education × working)
  - beta_work_educH (high education × working)

**Rationale:**
- GSUR: Unemployment affects work propensity
- Education × working: Higher education → different work patterns

**Expected:**
- LL improvement: ~10-30 points over v1
- Condition number: 50,000-100,000
- GSUR coefficient: Negative (high unemployment → less work)

**Decision:**
- If κ < 120,000 and interactions significant → PROCEED to Spec 3
- If κ > 150,000 → STOP, use Spec 1
- If only GSUR significant → Drop education interactions, keep GSUR

**I will create this spec AFTER you run Spec 1**

---

### 🔄 Spec 3: enhanced_minimal_v3 (23 params, +2 from v2)

**What's Added (to v2):**
- Wage equation factors: 2 params
  - beta_w_educL (low education wage penalty)
  - beta_w_educH (high education wage premium)

**Rationale:**
- Standard Mincer equation
- Education strongly affects wages

**Expected:**
- LL improvement: ~5-15 points over v2
- Condition number: 70,000-150,000
- Education wage premiums: educH > 0, educL < 0

**Decision:**
- If κ < 150,000 → FINAL SPEC, use for policy
- If κ > 200,000 → STOP, use Spec 2

**I will create this spec AFTER you run Spec 2**

---

## Testing Protocol

### After Each Estimation:

1. **Check Condition Number**
   ```bash
   grep "condition_number" outputs/estimates/fr/incremental/v*/run_*/estimation_results.json
   ```
   - κ < 50,000: EXCELLENT
   - κ < 100,000: GOOD
   - κ > 150,000: STOP ADDING

2. **Check Parameter Significance**
   ```bash
   cat outputs/estimates/fr/incremental/v*/run_*/estimation_summary.txt | grep -A 20 "Parameter estimates"
   ```
   - |t-value| > 2: Significant
   - |t-value| < 2: Not significant, consider dropping

3. **Check Log-Likelihood**
   - Must improve by at least 5 points per added parameter
   - If LL improvement < 5 per param → Not worth the complexity

4. **Check Solver Agreement (Optional but Recommended)**
   Run GAMSPy on same spec:
   - If SciPy LL ≈ GAMSPy LL (diff < 1): ROBUST
   - If diff > 10: Multiple local maxima, STOP

---

## What Parameters to Expect

### Education Effects (Spec 1):

**Leisure:**
- educH: Negative (higher education → work more, value leisure less)
- educL: Positive or zero (lower education → may value leisure more)

**Example from literature:**
- beta_l_educH ≈ -0.3 to -0.7
- beta_l_educL ≈ 0.1 to 0.3

### Unemployment Effect (Spec 2):

**GSUR:**
- Negative (high unemployment → less likely to work)
- beta_gsur ≈ 0 to -5

### Wage Effects (Spec 3):

**Education Premiums:**
- beta_w_educH: +0.2 to +0.4 (high edu → 20-40% higher wages)
- beta_w_educL: -0.1 to -0.3 (low edu → 10-30% lower wages)

---

## Stopping Conditions

**STOP ADDING if ANY of these occur:**

1. ✋ **Condition number > 200,000**
   - Severe identification issues
   - Results will be unstable for policy simulation

2. ✋ **Multiple local maxima detected**
   - SciPy and GAMSPy differ by > 10 LL points
   - Non-reproducible results

3. ✋ **New parameters not significant**
   - All new t-values < 2
   - Adding complexity without explanatory power

4. ✋ **LL improvement too small**
   - Improvement < 5 points per parameter
   - Not worth the added complexity

5. ✋ **Parameters hit bounds**
   - Many parameters at 0, 5, or other bounds
   - Model is over-flexible, trying to escape non-identification

---

## My Prediction

Based on Phase 1/2 results:

**Most likely outcome:**
- Spec 1 (18 params): ✅ Works well, κ ≈ 40,000
- Spec 2 (21 params): ✅ Still OK, κ ≈ 80,000
- Spec 3 (23 params): ⚠️ Borderline, κ ≈ 130,000

**Your final spec will probably be Spec 2 (21 params)**

**Reasoning:**
- Education effects are strong in labor supply data
- GSUR has clear variation (regional unemployment rates)
- Wage education premiums are well-documented
- Beyond this, you'd need richer data (occupation, industry, etc.)

---

## Timeline

**Phase:** Run Spec 1
**Expected:** 15 minutes
**Then:** Report back condition number and education coefficients

**Phase:** Run Spec 2 (if Spec 1 looks good)
**Expected:** 20 minutes
**Then:** Report back κ and GSUR coefficient

**Phase:** Run Spec 3 (if Spec 2 looks good)
**Expected:** 25 minutes
**Then:** Final decision

**Total time:** 1-2 hours for full incremental testing

---

## Next Action

**START WITH SPEC 1:**

```bash
cd //crc/users/hisham/Desktop/Nizam_Hisham/MNL

python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/incremental/v1_enhanced_minimal" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

**Monitor:**
```bash
tail -f outputs/estimates/fr/incremental/v1_enhanced_minimal/run_*/estimation.log
```

**After completion, check:**
```bash
grep "condition_number" outputs/estimates/fr/incremental/v1_enhanced_minimal/run_*/estimation_results.json
cat outputs/estimates/fr/incremental/v1_enhanced_minimal/run_*/estimation_summary.txt
```

**Report back:**
1. Condition number
2. Are education coefficients significant? (look for t-values)
3. What's the new LL?

Then I'll create Spec 2 for you!
