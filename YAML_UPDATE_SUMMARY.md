# YAML Specification Update Summary

**Date:** 2026-01-27
**File:** scripts/enhanced/estimation_spec_occupation_choice.yaml

## Overview

Successfully updated the occupation choice YAML specification to align with the France 2016 pipeline structure and base specification. All 115 parameters have been renamed and the specification now matches the mathematical specification document.

---

## Changes Made

### 1. Header and Documentation
- ✅ Updated occupation structure from "Managers, Professionals, Technicians, Service" to correct loc4 categories
- ✅ Added ISCO mapping details for each occupation
- ✅ Added hours peaks documentation (PT1, PT2, FT with weekly ranges)

### 2. Leisure Shifters (12 parameters)
- `beta_l_prof_*` → `beta_l_nm_*` (4 parameters: _sm, _sf, _m, _f)
- `beta_l_tech_*` → `beta_l_rc_*` (4 parameters)
- `beta_l_service_*` → `beta_l_nc_*` (4 parameters)

### 3. Occupation Preferences (36 parameters)
- `alpha_prof_*` → `alpha_nm_*` (12 parameters: base, educ, age × 4 gender groups)
- `alpha_tech_*` → `alpha_rc_*` (12 parameters)
- `alpha_service_*` → `alpha_nc_*` (12 parameters)

### 4. Hours Opportunity (13 parameters)
**Added PT2 peaks for all occupations:**
- `pi_pt_mgr`, `pi_ft_mgr` → `pi_pt1_rm`, `pi_pt2_rm`, `pi_ft_rm`
- `pi_pt_prof`, `pi_ft_prof` → `pi_pt1_nm`, `pi_pt2_nm`, `pi_ft_nm`
- `pi_pt_tech`, `pi_ft_tech` → `pi_pt1_rc`, `pi_pt2_rc`, `pi_ft_rc`
- `pi_pt_service`, `pi_ft_service` → `pi_pt1_nc`, `pi_pt2_nc`, `pi_ft_nc`
- `beta_work` (unchanged)

**Total:** 1 + 4 + 4 + 4 = 13 parameters

### 5. Wage Opportunity (40 parameters)
**All occupation-gender combinations renamed:**
- `beta_w0_mgr_*` → `beta_w0_rm_*` (2 parameters: _sm, _sf)
- `beta_w_exp_mgr_*` → `beta_w_exp_rm_*` (2 parameters)
- `beta_w_exp2_mgr_*` → `beta_w_exp2_rm_*` (2 parameters)
- `beta_w_ed_mgr_*` → `beta_w_ed_rm_*` (2 parameters)
- `sigma_mgr_*` → `sigma_rm_*` (2 parameters)

**Same pattern for:** prof → nm, tech → rc, service → nc

**Total:** 4 occupations × 2 genders × 5 parameters = 40 parameters

### 6. Occupation Availability (6 parameters)
- `mu_mgr_sm` → `mu_nm_sm` (routine manual is now reference, not service)
- `mu_mgr_sf` → `mu_nm_sf`
- `mu_prof_sm` → `mu_rc_sm`
- `mu_prof_sf` → `mu_rc_sf`
- `mu_tech_sm` → `mu_nc_sm`
- `mu_tech_sf` → `mu_nc_sf`

**Reference:** Changed from loc4_4 (Service) to loc4_1 (Routine manual)

### 7. Couples Interaction (1 parameter)
- `alpha_leisure_interact` → `beta_interact`
- Updated value from 4.84 to -0.5534 (matches base specification)

### 8. Optimization Bounds
Updated sigma bounds to use new parameter names:
- `sigma_mgr_*` → `sigma_rm_*`
- `sigma_prof_*` → `sigma_nm_*`
- `sigma_tech_*` → `sigma_rc_*`
- `sigma_service_*` → `sigma_nc_*`

---

## Parameter Count Verification

| Category | Count | Verified |
|----------|-------|----------|
| Preference (leisure + consumption) | 19 | ✅ |
| Hours opportunity (PT1 + PT2 + FT + work) | 13 | ✅ |
| Wage opportunity (4 occ × 2 gender × 5) | 40 | ✅ |
| Occupation preferences (3 occ × 4 gender × 3) | 36 | ✅ |
| Occupation availability (3 occ × 2 gender) | 6 | ✅ |
| Couples interaction | 1 | ✅ |
| **TOTAL** | **115** | ✅ |

---

## Occupation Mapping

### loc4 Categories (France 2016 Pipeline)

| loc4 | Name | ISCO Groups | Expected Characteristics |
|------|------|-------------|-------------------------|
| 1 | Routine manual | 6,7,8 (Craft, Plant, Elementary) | Low wages, high PT1/PT2, moderate FT |
| 2 | Nonroutine manual | 5 (Service/Sales) | Low-medium wages, high PT1/PT2 |
| 3 | Routine cognitive | 4 (Clerical) | Medium wages, moderate PT1/PT2, high FT |
| 4 | Nonroutine cognitive | 1,2,3 (Mgr, Prof, Tech) | Highest wages, low PT1/PT2, very high FT |

### Hours Peaks (Weekly Hours)

| Peak | Range | Description |
|------|-------|-------------|
| PT1 | 18.5-20.5h | Part-time 1 (~20h/week) |
| PT2 | 29.5-30.5h | Part-time 2 (~30h/week) |
| FT | 37.5-40.5h | Full-time (~40h/week) |

---

## Key Initial Values Updated

### Hours Clustering by Occupation
```yaml
# Routine manual (loc4_1)
pi_pt1_rm: 1.5  # High part-time 1
pi_pt2_rm: 1.8  # High part-time 2
pi_ft_rm: 1.2   # Moderate full-time

# Nonroutine cognitive (loc4_4)
pi_pt1_nc: 0.3  # Very low part-time 1
pi_pt2_nc: 0.5  # Low part-time 2
pi_ft_nc: 2.0   # Very high full-time
```

### Wage Hierarchy by Occupation
```yaml
# Routine manual (lowest wages)
beta_w0_rm_sm: 2.7  # ~17 EUR/hr

# Nonroutine cognitive (highest wages)
beta_w0_nc_sm: 3.1  # ~28 EUR/hr
```

### Occupation Availability (Relative Rarity)
```yaml
# Reference: Routine manual (mu_rm = 0, most common)
mu_nm_sm: -0.5   # Nonroutine manual somewhat rare
mu_rc_sm: -1.0   # Routine cognitive moderately rare
mu_nc_sm: -1.5   # Nonroutine cognitive rarest
```

---

## Compatibility Status

| Component | Status |
|-----------|--------|
| **Mathematical Specification** | ✅ Fully compatible |
| **YAML Specification** | ✅ Fully updated |
| **Pipeline Data (loc4, hours indicators)** | ✅ Already compatible |
| **Base Specification (estimation_spec.yaml)** | ✅ Matches structure |
| **Implementation Code** | ❓ Needs verification |

---

## Next Steps

1. ✅ YAML specification updated and verified
2. ❓ Verify Python implementation (estimation_engine.py, estimation_spec_parser.py)
3. ❓ Test with small sample dataset
4. ❓ Check if occupation-specific opportunity densities are implemented
5. ❓ Verify McFadden sampling supports 400-alternative choice sets

---

## Files Modified

- **scripts/enhanced/estimation_spec_occupation_choice.yaml** - Completely updated with 115 parameters

## Files to Check Next

- **scripts/enhanced/estimation_engine.py** - Verify occupation choice implementation
- **scripts/enhanced/estimation_spec_parser.py** - Verify YAML parsing handles new structure
- **scripts/enhanced/gamspy_estimation.py** - Check GAMS implementation support

---

**Last Updated:** 2026-01-27
