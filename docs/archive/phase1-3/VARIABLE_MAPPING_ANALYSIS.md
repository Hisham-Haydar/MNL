# Variable Mapping Analysis - EUROMOD to RURO

**Date:** December 15, 2025
**Source:** Drd_vars.txt + france_data_prep.py + RURO_prep.py

---

## Executive Summary

This document maps variables from the EUROMOD FR_2016.txt dataset to RURO requirements.

**Key Finding:** `lma`, `lun`, `lmc` are **NOT in the input data** - they must be EUROMOD simulation outputs.

---

## Input Variables (Available in FR_2016.txt)

### Identifiers
| Variable | Description | Source |
|----------|-------------|--------|
| `idhh` | Household ID | db030 |
| `idperson` | Person ID | rb030 |
| `idfather` | Father's person ID | rb220 |
| `idmother` | Mother's person ID | rb230 |
| `idpartner` | Partner's person ID | rb240 |

### Demographics
| Variable | Description | Values | Source |
|----------|-------------|--------|--------|
| `dag` | Age | Years | rx020 |
| `dgn` | Gender | 0=Female, 1=Male | rb090 |
| `dms` | Marital status | 1=Single, 2=Married, 3=Separated, 4=Divorced, 5=Widowed | pb190 |
| `ddi` | Disability | 0=Not disabled, 1=Disabled | pl031==8 |
| `dwt` | Weight | Numeric | db090 |

### Education
| Variable | Description | Values | Source |
|----------|-------------|--------|--------|
| `dec` | Current education status | 0-6 (Pre-primary to Tertiary) | pe020 |
| `deh` | Highest education | 0-5 (Not completed Primary to Tertiary) | pe040 |
| `dehde` | Highest education (detailed) | 0-800 (ISCED codes) | pe040 |
| `dey` | Years of education | Derived from deh | Calculated |
| `dew` | Year achieved highest education | Year | pe030 |

### Region
| Variable | Description | Values |
|----------|-------------|--------|
| `drgn1` | NUTS Level 1 | 1-5 (France regions) |
| `drgn2` | NUTS Level 2 | 1-27 (France regions detailed) |
| `drgur` | Urban region | 0/1 |
| `drgmd` | Middle density | 0/1 |
| `drgru` | Rural region | 0/1 |

### Labor Market (INPUT - From EU-SILC)
| Variable | Description | Values | Source | RURO Use |
|----------|-------------|--------|--------|----------|
| `les` | Economic status | 0-10 (see below) | pl031/pl040 | ✅ Fallback for worker ID |
| `lcs` | Civil servant | 0/1 | ? | ❓ |
| `lfs` | Firm size | 0-50 | pl130 | ❓ |
| `lindi` | Industry (NACE) | 1-12 | pl111 | ✅ Used in RURO |
| `loc` | Occupation (ISCO) | 0-9, -1 | pl051 | ✅ Used in RURO |
| `lhw` | Hours worked per week | Numeric | pl060+pl100 | ✅ CRITICAL for RURO |
| `lhw_f` | Hours worked flag | 1-4 | Flag | ❓ |
| `liwmy` | Months in work per year | 0-12 | pl073+pl074+pl075+pl076 | ✅ Used for yem calc |
| `liwftmy` | Months full-time per year | 0-12 | pl073+pl075 | ❓ |
| `liwptmy` | Months part-time per year | 0-12 | pl074+pl076 | ❓ |
| `liwwh` | Work history (months) | Numeric | pl200*12 | ❓ |
| `lpemy` | Months in retirement | 0-12 | pl085 | ❓ |
| `lse` | Self-employed status | 0-3 | pl040 | ✅ Used in RURO |
| `lunmy` | Months unemployed per year | 0-12 | pl080 | ✅ Note: This is MONTHS, not status! |
| `lowas` | Actively seeking work | 0/1 | pl020 | ❓ |
| `ltr` | Job transition | 0/1/-1 | pl160 | ❓ |

**`les` Economic Status Values:**
- 0: Pre-school
- 1: Farmer
- 2: Employer or self-employed
- 3: Employee ← **Used as fallback for worker identification!**
- 4: Pensioner
- 5: Unemployed
- 6: Student
- 7: Inactive
- 8: Sick or Disabled
- 9: Other
- 10: Family worker

### Income (INPUT)
| Variable | Description | Source | RURO Use |
|----------|-------------|--------|----------|
| `yem` | Employment income | py010g/12*hx010 | ✅ CRITICAL - calculated from lhw×yivwg |
| `yse` | Self-employment income | py050g/12*hx010 | ✅ Used |
| `yiy` | Investment income | hy090g/12*hx010 | ✅ Used |
| `ypr` | Property income | Derived | ✅ Used |
| `yivwg` | Hourly wage (IMPUTED) | Imputed | ✅ CRITICAL for RURO draws |

---

## Missing Variables (Expected from EUROMOD Output)

These variables are **NOT in Drd_vars.txt**, meaning they are EUROMOD simulation outputs:

### Labor Market Status (EUROMOD OUTPUTS)
| Variable | Expected Meaning | RURO Use | Status |
|----------|------------------|----------|--------|
| `lma` | Labor market active | ✅ PRIMARY worker identification | ❌ MISSING! |
| `lun` | Labor market inactive/unemployed | ✅ Opportunity model | ❌ MISSING! |
| `lmc` | Labor market constrained | ❓ Unknown use | ❌ MISSING! |
| `lhw_a` | Hours worked (adjusted?) | ❓ Unknown | ❌ MISSING! |
| `lhw_a1` | Hours worked variant 1 | ❓ Unknown | ❌ MISSING! |
| `lhw_a_9` | Hours worked variant 9 | ❓ Unknown | ❌ MISSING! |
| `lhw_a_20` | Hours worked variant 20 | ❓ Unknown | ❌ MISSING! |

### Disposable Income (EUROMOD OUTPUTS)
| Variable | Expected Meaning | RURO Use | Status |
|----------|------------------|----------|--------|
| `ils_dispy` | Disposable income | ✅ CRITICAL - consumption in utility | ✅ Should exist |
| `ils_*` | Various income components | ✅ Tax-benefit calculations | ✅ Should exist |

---

## RURO Requirements Analysis

### Critical Variables for RURO_prep.py

From [RURO_prep.py:576-585](scripts/RURO_prep.py#L576-L585):

```python
# Worker identification (CRITICAL!)
lma = None
if "lma" in df.columns:
    lma = cast(pd.Series, pd.to_numeric(df["lma"], errors="coerce"))

if lma is not None:
    is_worker_bool = (lma == 1) & (lhw > 0.0)  # Preferred method
else:
    is_worker_bool = les.eq(3) & (lhw > 0.0)   # Fallback to les
```

**Findings:**
1. **Preferred:** Use `lma` (labor market active) if available
2. **Fallback:** Use `les == 3` (employee status) if `lma` missing
3. **Current state:** `lma` is missing/zero → using fallback
4. **Problem:** Fallback may misclassify workers

### Variables Used in RURO Models

From RURO_prep.py and estimation scripts:

**Utility Function Variables:**
- ✅ `ruro_consumption` (from `ils_dispy`)
- ✅ `ruro_leisure_m`, `ruro_leisure_f` (from hours)
- ✅ `dag` (age)
- ✅ `educL`, `educM`, `educH` (education dummies)
- ✅ `reg*` (region dummies)
- ✅ `ch0_3`, `ch4_6`, `ch7_9` (children by age)

**Opportunity Variables:**
- ✅ `gsur_probability` (labor force participation - from external model)
- ✅ `wage_draw_m`, `wage_draw_f` (from wage draws)
- ⚠️ `lma`, `lun`, `lmc` - MISSING but expected

---

## Hypothesis: What are lma/lun/lmc?

Based on naming conventions and EUROMOD structure:

### `lma` - Labor Market Activity
**Likely definition:** Binary indicator (0/1) for whether person is economically active
- Similar to ILO definition: employed OR actively seeking work
- Formula: `lma = 1 if (les in [1,2,3]) OR (les==5 AND lowas==1)`
- Alternative: EUROMOD might calculate based on actual labor market participation

### `lun` - Labor Market Unemployment/Inactive
**Likely definition:** Binary indicator for labor market inactive
- Could be: `lun = 1 if les in [0,4,6,7,8,9]` (not active in labor market)
- Or: `lun = 1 - lma` (complement of active)

### `lmc` - Labor Market Constrained
**Likely definition:** Indicator for facing labor market constraints
- Could indicate: involuntary part-time, underemployment, discouraged workers
- More complex derivation from EUROMOD policy rules

---

## Recommendations

### Immediate Actions

1. **Verify EUROMOD Output Contains lma/lun/lmc**
   ```python
   # After running Step 1 with fixed france_data_prep.py
   df = pd.read_parquet('...fr_2016_processed.parquet')

   for var in ['lma', 'lun', 'lmc']:
       if var in df.columns:
           print(f"{var}: EXISTS, std={df[var].std():.4f}")
       else:
           print(f"{var}: MISSING from EUROMOD output")
   ```

2. **If lma is Missing from EUROMOD:**
   - Construct it ourselves from `les`:
   ```python
   df['lma'] = (df['les'].isin([1, 2, 3])).astype(int)
   # Or more complex:
   df['lma'] = ((df['les'].isin([1, 2, 3])) |
                ((df['les'] == 5) & (df['lowas'] == 1))).astype(int)
   ```

3. **If lma Exists but is Zero:**
   - This was the original problem (now fixed by merge logic)
   - The fix should preserve EUROMOD's calculated `lma`

### Alternative Worker Identification

If `lma` is truly not available from EUROMOD, use enhanced `les`-based logic:

```python
# More robust worker identification without lma
def identify_workers(df):
    """
    Identify workers using les (economic status) and lhw (hours).

    Workers are:
    - Employees (les==3) with positive hours
    - Self-employed (les in [1,2]) with positive hours
    """
    is_employee = (df['les'] == 3) & (df['lhw'] > 0)
    is_self_employed = (df['les'].isin([1, 2])) & (df['lhw'] > 0)

    return (is_employee | is_self_employed).astype(int)
```

---

## Variable Availability Summary

| Category | Available in FR_2016.txt | EUROMOD Output | RURO Requirement |
|----------|-------------------------|----------------|------------------|
| Demographics | ✅ All present | N/A | ✅ Satisfied |
| Education | ✅ All present | N/A | ✅ Satisfied |
| Region | ✅ All present | N/A | ✅ Satisfied |
| Hours (`lhw`) | ✅ Present | Updated by EUROMOD? | ✅ Satisfied |
| Wage (`yivwg`) | ✅ Imputed | N/A | ✅ Satisfied |
| Economic Status (`les`) | ✅ Present | N/A | ✅ Satisfied (fallback) |
| Labor Market Activity (`lma`) | ❌ MISSING | ⚠️ Unknown | ⚠️ CRITICAL NEED |
| Unemployed (`lun`) | ❌ MISSING | ⚠️ Unknown | ❓ Unknown need |
| Constrained (`lmc`) | ❌ MISSING | ⚠️ Unknown | ❓ Unknown need |
| Disposable Income (`ils_dispy`) | ❌ Not in input | ✅ EUROMOD output | ✅ CRITICAL NEED |

---

## Testing Plan

### After Running Fixed Pipeline

1. **Check if lma exists in Step 1 output:**
   ```python
   df = pd.read_parquet('fr_2016_processed.parquet')
   print('lma' in df.columns)
   print(df['lma'].std() if 'lma' in df.columns else 'MISSING')
   ```

2. **Compare lma vs les for worker identification:**
   ```python
   if 'lma' in df.columns:
       workers_lma = ((df['lma'] == 1) & (df['lhw'] > 0)).sum()
       workers_les = ((df['les'] == 3) & (df['lhw'] > 0)).sum()
       print(f"Workers by lma: {workers_lma}")
       print(f"Workers by les: {workers_les}")
       print(f"Difference: {abs(workers_lma - workers_les)}")
   ```

3. **Verify is_worker flag in Step 2:**
   ```python
   df_ruro = pd.read_parquet('singles_RURO_ready.parquet')
   print(f"is_worker distribution: {df_ruro['is_worker'].value_counts()}")
   ```

---

## Conclusion

The Drd_vars.txt analysis confirms:
1. ✅ Most variables needed by RURO are in FR_2016.txt
2. ❌ `lma`, `lun`, `lmc` are NOT in input data
3. ✅ These must come from EUROMOD simulation output
4. ✅ Our fix (prioritizing EUROMOD outputs) should preserve them
5. ⚠️ If EUROMOD doesn't produce `lma`, we can construct it from `les`

**Next Step:** Run the interactive pipeline and verify whether `lma` exists in EUROMOD output after the fix!
