# Occupation (loc4) vs Education Choice

## What is loc4?

**`loc4`** = 4-category occupation classification based on **ISCO-08** (International Standard Classification of Occupations)

### The 4 Categories:

1. **loc4_1** - Managers (ISCO-08 major group 1)
   - High skill, high status
   - Expected leisure effect: NEGATIVE (value work more than leisure)

2. **loc4_2** - Professionals (ISCO-08 major group 2)
   - High skill (doctors, lawyers, teachers, engineers)
   - Expected leisure effect: NEGATIVE

3. **loc4_3** - Technicians (ISCO-08 major group 3)
   - Medium-high skill (technicians, associate professionals)
   - Expected leisure effect: SLIGHTLY NEGATIVE

4. **loc4_4** - Clerks/Service workers (ISCO-08 major groups 4-9)
   - Medium-low skill (clerical, sales, service, operators, elementary)
   - **REFERENCE CATEGORY** (omitted from regression)

---

## Your Two Options

### Option A: Education Shifters (Already Created)
**File:** `estimation_spec_enhanced_minimal.yaml`
**Parameters:** 18 total

**Leisure shifters:**
```yaml
- educL (low education dummy)
- educH (high education dummy)
# educM (medium education) is reference
```

**Pros:**
- ✅ Standard in labor supply literature
- ✅ Education affects both preferences AND wages (structural interpretation)
- ✅ Fewer parameters (2 dummies × 4 groups = 8 params)

**Cons:**
- ❌ Less granular than occupation
- ❌ Education is fixed, occupation varies over life
- ❌ Doesn't capture job characteristics (stress, flexibility, etc.)

**Expected coefficients:**
- `beta_l_educH`: -0.3 to -0.7 (higher education → work more)
- `beta_l_educL`: 0.0 to 0.3 (lower education → may value leisure more)

---

### Option B: Occupation Shifters (Just Created)
**File:** `estimation_spec_enhanced_minimal_v2.yaml`
**Parameters:** 23 total

**Leisure shifters:**
```yaml
- loc4_1 (Managers)
- loc4_2 (Professionals)
- loc4_3 (Technicians)
# loc4_4 (Clerks/Service) is reference
```

**Pros:**
- ✅ More granular (captures job characteristics)
- ✅ Directly related to work behavior
- ✅ Occupation varies endogenously (could be policy-relevant)
- ✅ Better captures labor market segmentation

**Cons:**
- ❌ More parameters (3 dummies × 4 groups = 12 params)
- ❌ May have less variation in data than education
- ❌ Occupation choice may be endogenous (causality concerns)

**Expected coefficients:**
- `beta_l_loc4_1` (Managers): -0.3 to -0.5 (high status → low leisure value)
- `beta_l_loc4_2` (Professionals): -0.2 to -0.4
- `beta_l_loc4_3` (Technicians): -0.1 to -0.2

---

## Option C: BOTH Education AND Occupation (Advanced)

**Not recommended initially** because:
- Total: 18 + 12 = 30 parameters (HIGH risk of over-identification)
- Education and occupation are correlated (multicollinearity)
- Expected condition number: >150,000 (severe issues)

**BUT could test later if:**
- Option B works well (κ < 60,000)
- You want to capture BOTH education effects AND occupation effects
- You're willing to risk higher condition number

---

## My Recommendation

### Start with Option B (Occupation)

**Reasoning:**

1. **More directly related to labor supply**
   - Occupation captures job characteristics (hours constraints, flexibility)
   - Education is more about human capital accumulation

2. **Policy relevance**
   - Occupation shifts are observable in simulations
   - Education shifts are rare (fixed in short run)

3. **Empirical evidence**
   - Occupation dummies typically have stronger effects in labor supply models
   - loc4 data should have good variation (all workers have an occupation)

4. **You specifically asked for occupation!**
   - "where is the occupation loc4 ??" 😊

### Testing Strategy

**Step 1:** Run Option B (Occupation, 23 params)
```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/incremental/v1b_occupation" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal_v2.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

**Expected:** κ ≈ 50,000-80,000 (acceptable)

**Step 2:** If κ < 80,000 and occupation coefficients significant → Keep it!

**Step 3:** (Optional) Try Option A (Education, 18 params) for comparison
- If education performs better (higher t-values, lower κ) → Switch
- If both are good → Choose based on research question

---

## Comparison Table

| Feature | Education (18 params) | Occupation (23 params) | Both (30 params) |
|---------|----------------------|----------------------|------------------|
| **Parameters** | 18 | 23 | 30 |
| **Shifters** | educL, educH (2) | loc4_1/2/3 (3) | 5 total |
| **Expected κ** | 35,000-60,000 | 50,000-80,000 | 120,000-200,000 |
| **Policy relevance** | Medium (fixed) | High (variable) | Highest |
| **Identification risk** | Low | Medium | HIGH |
| **Interpretation** | Human capital | Job characteristics | Both |
| **Literature support** | Strong | Strong | Moderate |
| **My recommendation** | ✅ Good baseline | ✅✅ **BEST CHOICE** | ❌ Too risky |

---

## What Occupation Coefficients Tell You

### If beta_l_loc4_1 (Managers) < 0:
- Managers value leisure LESS than clerks/service workers
- They are more work-oriented (career concerns, status)
- Higher opportunity cost of leisure

### If beta_l_loc4_2 (Professionals) < 0:
- Professionals (doctors, lawyers) value work over leisure
- Could be due to:
  - Career investment
  - Job satisfaction
  - Higher marginal utility of income (consumption)

### If beta_l_loc4_3 (Technicians) ≈ 0:
- Technicians have similar leisure preferences to reference group
- Medium skill occupations are "neutral"

### If coefficients NOT significant (t < 2):
- Occupation doesn't strongly affect leisure preferences
- Workers sort into jobs based on wages, not preferences
- **Fall back to Option A (Education)**

---

## Quick Decision Guide

**Q:** Do you care more about education policy or labor market dynamics?
- **Education policy** → Use Option A (Education)
- **Labor market dynamics** → Use Option B (Occupation) ✅

**Q:** Will you simulate occupation changes in counterfactuals?
- **Yes** → Use Option B (Occupation) ✅
- **No** → Either works

**Q:** Do you want the most robust specification?
- **Yes** → Use Option A (Education, fewer params)
- **Want richness** → Use Option B (Occupation) ✅

**Q:** Are you willing to test both?
- **Yes** → Run both, compare condition numbers ✅✅
- **No** → Start with Option B (you asked for it!)

---

## Files Created

1. **`estimation_spec_enhanced_minimal.yaml`** (18 params)
   - Education shifters (educL, educH)
   - Theta_c for couples
   - Focal hours

2. **`estimation_spec_enhanced_minimal_v2.yaml`** (23 params) ← **NEW!**
   - **Occupation shifters (loc4_1, loc4_2, loc4_3)**
   - Theta_c for couples
   - Focal hours

---

## Next Action

### Option 1: Run Occupation Version (My Recommendation)

```bash
cd //crc/users/hisham/Desktop/Nizam_Hisham/MNL

python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/incremental/v1b_occupation" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal_v2.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

**Expected:** 20 minutes, κ ≈ 60,000

### Option 2: Run Education Version (Conservative)

```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/incremental/v1a_education" \
  --group joint \
  --solver scipy \
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" \
  --warm-start "none" \
  --auto-timestamp \
  --verbose
```

**Expected:** 15 minutes, κ ≈ 40,000

### Option 3: Run Both in Parallel! (Best)

Open two terminals and run both commands above simultaneously. Compare results after 20 minutes.

---

## Summary

**I found loc4!** It's occupation data with 4 categories (Managers, Professionals, Technicians, Clerks/Service).

**I created a new spec for you:** `estimation_spec_enhanced_minimal_v2.yaml` with occupation instead of education.

**My recommendation:** Run the OCCUPATION version (Option B) since you specifically asked for it and it's more policy-relevant.

**Your choice:** Education (18 params, safer) or Occupation (23 params, richer)?
