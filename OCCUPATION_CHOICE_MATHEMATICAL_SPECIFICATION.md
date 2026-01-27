# Complete Mathematical Specification: Occupation Choice Model

## Model Overview

This is a **Random Utility Random Opportunity (RURO) Multinomial Logit (MNL)** model where individuals choose from a discrete set of alternatives characterized by:
- **Hours of work** (h): Weekly hours (lhw), ranging from 0 to 70 hours/week
- **Hourly wage** (w): Hourly wage rate (EUR for France, NOK for Norway)
- **Occupation** (occ): One of 4 occupation categories (loc4: routine_manual=1, nonroutine_manual=2, routine_cognitive=3, nonroutine_cognitive=4)

The choice set for each individual contains **400 alternatives**: 100 (hours, wage) pairs for each of the 4 occupations.

---

## 1. UTILITY FUNCTION

### 1.1 General Form

For individual *i* choosing alternative *j* with characteristics (c_ij, L_ij, occ_j), the utility is:

```
U_ij = v(c_ij, L_ij, occ_j; X_i, θ) · ε_ij
```

where:
- **c_ij** = disposable income (consumption) for alternative j
- **L_ij** = leisure for alternative j = 168 - h_j (weekly leisure hours, where 168 = 7 days × 24 hours)
- **occ_j** ∈ {loc4_1, loc4_2, loc4_3, loc4_4} = occupation for alternative j
- **X_i** = individual characteristics (demographics)
- **θ** = parameter vector
- **ε_ij** ~ Type I Extreme Value (Gumbel) distribution, i.i.d.

The systematic utility component v(·) is in **log form**:

```
log v(c_ij, L_ij, occ_j; X_i, θ) = U_consumption + U_leisure + U_occupation
```

---

### 1.2 Consumption Utility Component

The consumption utility uses a **Box-Cox transformation** (with exponent = 0, giving log utility):

```
U_consumption = β_c · log(c_ij)
```

where:
- **β_c** = consumption preference parameter
  - For singles male: β_c_sm
  - For singles female: β_c_sf
  - For couples: β_c (shared household consumption)

**Note:** The Box-Cox exponent θ_c is set to 0 (not estimated), giving pure log utility.

---

### 1.3 Leisure Utility Component

The leisure utility has two parts: base leisure preference and occupation-specific leisure shifters.

#### 1.3.1 Base Leisure Utility

```
U_leisure_base = [β_l0 + 0] · log(L_ij)
```

where:
- **β_l0** = leisure intercept parameter (gender-specific)
  - Singles male: β_l0_sm
  - Singles female: β_l0_sf
  - Couples male: β_l0_m
  - Couples female: β_l0_f

**Note:** No demographic shifters on leisure in this specification (shifters list is empty except for occupation). The Box-Cox exponent θ_l is set to 0, giving log utility.

#### 1.3.2 Occupation-Specific Leisure Shifters

Different occupations may have different work-life balance, flexibility, etc., captured by:

```
U_leisure_occupation = [β_l_nm · 1{occ_j = loc4_2}
                       + β_l_rc · 1{occ_j = loc4_3}
                       + β_l_nc · 1{occ_j = loc4_4}] · log(L_ij)
```

where:
- **1{occ_j = loc4_k}** = indicator that alternative j is in occupation k
- **β_l_nm** = additional leisure preference for Nonroutine manual (relative to Routine manual)
  - Singles male: β_l_nm_sm
  - Singles female: β_l_nm_sf
  - Couples male: β_l_nm_m
  - Couples female: β_l_nm_f
- **β_l_rc** = additional leisure preference for Routine cognitive
  - Singles male: β_l_rc_sm, Singles female: β_l_rc_sf
  - Couples male: β_l_rc_m, Couples female: β_l_rc_f
- **β_l_nc** = additional leisure preference for Nonroutine cognitive
  - Singles male: β_l_nc_sm, Singles female: β_l_nc_sf
  - Couples male: β_l_nc_m, Couples female: β_l_nc_f

**Reference:** Routine manual (loc4_1) have β_l_occ = 0 (reference category).

**Total Leisure Utility:**
```
U_leisure = [β_l0 + β_l_occ(occ_j)] · log(L_ij)
```

---

### 1.4 Occupation Preference Component

Individuals may have intrinsic preferences for different occupations, and these preferences may vary with demographic characteristics.

```
U_occupation = α_nm · 1{occ_j = loc4_2} + α_nm_educ · 1{occ_j = loc4_2} · education_i
              + α_nm_age · 1{occ_j = loc4_2} · age_i

              + α_rc · 1{occ_j = loc4_3} + α_rc_educ · 1{occ_j = loc4_3} · education_i
              + α_rc_age · 1{occ_j = loc4_3} · age_i

              + α_nc · 1{occ_j = loc4_4} + α_nc_educ · 1{occ_j = loc4_4} · education_i
              + α_nc_age · 1{occ_j = loc4_4} · age_i
```

**Parameters (all gender-specific with suffixes _sm, _sf, _m, _f):**

**Nonroutine manual (loc4_2):**
- **α_nm** = base preference for Nonroutine manual occupations
- **α_nm_educ** = interaction with education (years of schooling)
- **α_nm_age** = interaction with age

**Routine cognitive (loc4_3):**
- **α_rc** = base preference for Routine cognitive occupations
- **α_rc_educ** = interaction with education (years of schooling)
- **α_rc_age** = interaction with age

**Nonroutine cognitive (loc4_4):**
- **α_nc** = base preference for Nonroutine cognitive occupations
- **α_nc_educ** = interaction with education (years of schooling)
- **α_nc_age** = interaction with age

**Reference:** Routine manual (loc4_1) have all α parameters = 0.

**Demographic Variables:**
- **education_i** = years of schooling or education level (continuous or ordinal)
- **age_i** = age of individual in years

---

### 1.5 Complete Utility Function (Systematic Component)

Putting it all together, the **log systematic utility** is:

```
log v(c_ij, L_ij, occ_j; X_i, θ) =
    β_c · log(c_ij)
    + [β_l0 + β_l_occ(occ_j)] · log(L_ij)
    + α_occ(occ_j) + Σ_k α_occ_k(occ_j) · X_k,i
```

where:
- β_c, β_l0, β_l_occ are preference parameters
- α_occ, α_occ_k are occupation preference parameters
- X_k,i are demographic characteristics
- occ_j ∈ {loc4_1, loc4_2, loc4_3, loc4_4}

**Total utility (with random component):**
```
U_ij = exp[log v(c_ij, L_ij, occ_j; X_i, θ)] · ε_ij
     = v(c_ij, L_ij, occ_j; X_i, θ) · ε_ij
```

**For couples:** Add leisure interaction term:
```
log v(couple) = log v(male) + log v(female) + α_leisure_interact · log(L_male) · log(L_female)
```

---

## 2. OPPORTUNITY SET

The opportunity density describes how (hours, wage, occupation) combinations are distributed in the labor market for individual i.

### 2.1 General Form

Following Aaberge & Colombino (2011), the opportunity density is:

```
p(h, w, occ | X_i; θ) = p_1k · g_1(h | occ; θ_h) · g_2(w | occ, X_i; θ_w) · g_3(occ | X_i; θ_occ)   if h > 0
                       = p_0k = 1 - p_1k                                                                if h = 0
```

where:
- **p_1k** = proportion of market opportunities (working alternatives)
- **p_0k** = proportion of non-market opportunities (non-working, h=0)
- **g_1(h | occ)** = occupation-specific hours density
- **g_2(w | occ, X)** = occupation-specific wage density
- **g_3(occ | X)** = occupation availability density
- **X_i** = individual characteristics (experience, education)

**Key insight:** Hours and wages are **independently distributed** within each occupation, but the distributions **differ across occupations**.

---

### 2.2 Hours Opportunity Density: g_1(h | occ)

The hours density has **occupation-specific clustering** at focal hours peaks matching the France 2016 pipeline:

```
g_1(h | occ; θ_h) = γ_occ · exp[π_pt1_occ · 1{h ∈ PT1} + π_pt2_occ · 1{h ∈ PT2} + π_ft_occ · 1{h ∈ FT} + β_work · 1{h > 0}]
```

where:
- **γ_occ** = base density for occupation (normalization constant)
- **π_pt1_occ** = part-time 1 clustering parameter for occupation (20h/week peak)
- **π_pt2_occ** = part-time 2 clustering parameter for occupation (30h/week peak)
- **π_ft_occ** = full-time clustering parameter for occupation (40h/week peak)
- **β_work** = working indicator (applies to all h > 0)
- **PT1** = part-time 1 range: h ∈ [18.5, 20.5] hours/week (focal point ≈ 20h)
- **PT2** = part-time 2 range: h ∈ [29.5, 30.5] hours/week (focal point ≈ 30h)
- **FT** = full-time range: h ∈ [37.5, 40.5] hours/week (focal point ≈ 40h)

**Occupation-Specific Parameters:**
- Routine manual (loc4_1): π_pt1_rm, π_pt2_rm, π_ft_rm
- Nonroutine manual (loc4_2): π_pt1_nm, π_pt2_nm, π_ft_nm
- Routine cognitive (loc4_3): π_pt1_rc, π_pt2_rc, π_ft_rc
- Nonroutine cognitive (loc4_4): π_pt1_nc, π_pt2_nc, π_ft_nc

**Expected patterns:**
- Nonroutine cognitive: Low π_pt1, Low π_pt2, High π_ft (strong full-time)
- Routine manual: Higher π_pt1, Higher π_pt2, Moderate π_ft (more part-time work)

**Log hours density:**
```
log g_1(h | occ) = log(γ_occ) + π_pt1_occ · 1{h ∈ PT1} + π_pt2_occ · 1{h ∈ PT2} + π_ft_occ · 1{h ∈ FT} + β_work · 1{h > 0}
```

---

### 2.3 Wage Opportunity Density: g_2(w | occ, X)

Each occupation has its own **Mincer wage equation** with log-normal distribution:

```
log(w) | occ, X ~ N(μ_occ(X), σ²_occ)
```

where the mean log-wage is:

```
μ_occ(X_i) = β_0_occ + β_exp_occ · (exp_i / 10) + β_exp2_occ · (exp_i / 10)² + β_ed_occ · ed_i
```

**Variables:**
- **exp_i** = years of experience for individual i (scaled by 10 to give decades)
- **ed_i** = education level (e.g., years of schooling, or categorical)

**Parameters for each occupation-gender combination:**

**Routine manual (loc4_1):**
- Intercept: β_w0_rm_sm = 2.7, β_w0_rm_sf = 2.6
- Experience: β_w_exp_rm_sm = 0.19, β_w_exp_rm_sf = 0.17
- Experience²: β_w_exp2_rm_sm = -0.03, β_w_exp2_rm_sf = -0.02
- Education: β_w_ed_rm_sm = 0.03, β_w_ed_rm_sf = 0.03
- Std dev: σ_rm_sm = 0.24, σ_rm_sf = 0.22

**Nonroutine manual (loc4_2):**
- Intercept: β_w0_nm_sm = 2.8, β_w0_nm_sf = 2.7
- Experience: β_w_exp_nm_sm = 0.20, β_w_exp_nm_sf = 0.18
- Experience²: β_w_exp2_nm_sm = -0.03, β_w_exp2_nm_sf = -0.03
- Education: β_w_ed_nm_sm = 0.04, β_w_ed_nm_sf = 0.04
- Std dev: σ_nm_sm = 0.25, σ_nm_sf = 0.23

**Routine cognitive (loc4_3):**
- Intercept: β_w0_rc_sm = 2.9, β_w0_rc_sf = 2.8
- Experience: β_w_exp_rc_sm = 0.21, β_w_exp_rc_sf = 0.19
- Experience²: β_w_exp2_rc_sm = -0.03, β_w_exp2_rc_sf = -0.03
- Education: β_w_ed_rc_sm = 0.04, β_w_ed_rc_sf = 0.04
- Std dev: σ_rc_sm = 0.26, σ_rc_sf = 0.24

**Nonroutine cognitive (loc4_4):**
- Intercept: β_w0_nc_sm = 3.1, β_w0_nc_sf = 3.0
- Experience: β_w_exp_nc_sm = 0.23, β_w_exp_nc_sf = 0.21
- Experience²: β_w_exp2_nc_sm = -0.04, β_w_exp2_nc_sf = -0.03
- Education: β_w_ed_nc_sm = 0.05, β_w_ed_nc_sf = 0.05
- Std dev: σ_nc_sm = 0.28, σ_nc_sf = 0.26

**Log-normal density:**
```
log g_2(w | occ, X_i) = -log(w · σ_occ · √(2π)) - (1/2) · [(log w - μ_occ(X_i)) / σ_occ]²
```

**Expected wage hierarchy:** Nonroutine cognitive > Routine cognitive > Nonroutine manual > Routine manual

---

### 2.4 Occupation Availability: g_3(occ | X)

The probability that occupation occ is available to individual i follows a **multinomial logit** form:

```
g_3(occ | X_i; θ_occ) = exp(μ_occ) / [Σ_k exp(μ_k)]
```

where:
- **μ_occ** = log-odds parameter for occupation availability
- Reference category: Routine manual (loc4_1) with μ_rm = 0

**Parameters (singles only, gender-specific):**
- Routine manual: μ_rm = 0 (reference)
- Nonroutine manual: μ_nm_sm = -0.5, μ_nm_sf = -0.3
- Routine cognitive: μ_rc_sm = -1.0, μ_rc_sf = -0.8
- Nonroutine cognitive: μ_nc_sm = -1.5, μ_nc_sf = -1.2

**Interpretation:** More negative μ means occupation is rarer. Nonroutine cognitive occupations are the rarest, routine manual positions are most common.

**Log occupation availability:**
```
log g_3(occ) = μ_occ - log[exp(μ_rm) + exp(μ_nm) + exp(μ_rc) + exp(μ_nc)]
             = μ_occ - log[1 + exp(μ_nm) + exp(μ_rc) + exp(μ_nc)]
```

---

## 3. CHOICE PROBABILITY (MNL MODEL)

### 3.1 Composite Value Function

The composite value function combines utility and opportunity density:

```
V_ij = log v(c_ij, L_ij, occ_j; X_i, θ) + log p(h_j, w_j, occ_j | X_i; θ)
```

Expanding:

```
V_ij = [β_c · log(c_ij) + [β_l0 + β_l_occ(occ_j)] · log(L_ij) + α_occ(occ_j) + Σ_k α_occ_k(occ_j) · X_k,i]
     + [log g_1(h_j | occ_j) + log g_2(w_j | occ_j, X_i) + log g_3(occ_j)]
```

**For h_j > 0 (working alternatives):**
```
V_ij = β_c · log(c_ij)
     + [β_l0 + β_l_occ(occ_j)] · log(L_ij)
     + α_occ(occ_j) + Σ_k α_occ_k(occ_j) · X_k,i
     + π_pt1_occ(occ_j) · 1{h_j ∈ PT1} + π_pt2_occ(occ_j) · 1{h_j ∈ PT2} + π_ft_occ(occ_j) · 1{h_j ∈ FT} + β_work
     + log g_2(w_j | occ_j, X_i)
     + μ_occ(occ_j) - log[Σ_k exp(μ_k)]
```

**For h_j = 0 (non-working):**
```
V_i0 = log(p_0k) = log(1 - p_1k)
```

---

### 3.2 Choice Probability

Under the Type I Extreme Value distribution for ε_ij, the probability that individual i chooses alternative j is:

```
P_i(j) = exp(V_ij) / [Σ_{k=1}^{J_i} exp(V_ik)]
```

where J_i = 400 alternatives (100 for each of 4 occupations).

**Equivalently:**
```
P_i(j) = v(c_ij, L_ij, occ_j; X_i, θ) · p(h_j, w_j, occ_j | X_i; θ)
         ────────────────────────────────────────────────────────────
         Σ_{k=1}^{400} v(c_ik, L_ik, occ_k; X_i, θ) · p(h_k, w_k, occ_k | X_i; θ)
```

---

## 4. LIKELIHOOD FUNCTION

### 4.1 Individual Likelihood Contribution

For individual i with observed choice j* = (h*_i, w*_i, occ*_i), the likelihood contribution is:

```
L_i(θ) = P_i(j*) = exp(V_ij*) / [Σ_{k=1}^{400} exp(V_ik)]
```

**Log-likelihood contribution:**
```
ℓ_i(θ) = log L_i(θ) = V_ij* - log[Σ_{k=1}^{400} exp(V_ik)]
```

**Expanded form:**
```
ℓ_i(θ) = β_c · log(c_ij*)
       + [β_l0 + β_l_occ(occ*_i)] · log(L_ij*)
       + α_occ(occ*_i) + Σ_k α_occ_k(occ*_i) · X_k,i
       + π_pt1_occ(occ*_i) · 1{h*_i ∈ PT1} + π_pt2_occ(occ*_i) · 1{h*_i ∈ PT2} + π_ft_occ(occ*_i) · 1{h*_i ∈ FT} + β_work · 1{h*_i > 0}
       + log g_2(w*_i | occ*_i, X_i)
       + μ_occ(occ*_i) - log[Σ_k exp(μ_k)]
       - log[Σ_{k=1}^{400} exp(V_ik)]
```

where the last term is the **log-sum-exp** over all 400 alternatives:

```
log[Σ_{k=1}^{400} exp(V_ik)] = log[Σ_{k=1}^{400} v(c_ik, L_ik, occ_k) · p(h_k, w_k, occ_k | X_i)]
```

---

### 4.2 Sample Likelihood

For a sample of N individuals, the **total log-likelihood** is:

```
ℓ(θ) = Σ_{i=1}^{N} ℓ_i(θ) = Σ_{i=1}^{N} [V_ij* - log Σ_{k=1}^{400} exp(V_ik)]
```

**Objective:** Maximize ℓ(θ) with respect to θ = (preference parameters, opportunity parameters)

**Optimization:** Use L-BFGS-B with analytical gradients.

---

### 4.3 Full Likelihood Expression

Putting everything together, the **complete log-likelihood** for the sample is:

```
ℓ(θ) = Σ_{i=1}^{N} {
         β_c · log(c_ij*_i)
       + [β_l0 + Σ_{occ∈{2,3,4}} β_l_occ · 1{occ*_i = occ}] · log(L_ij*_i)
       + Σ_{occ∈{2,3,4}} [α_occ · 1{occ*_i = occ}
                         + α_occ_educ · 1{occ*_i = occ} · education_i
                         + α_occ_age · 1{occ*_i = occ} · age_i]
       + Σ_{occ∈{1,2,3,4}} [π_pt_occ · 1{occ*_i = occ, h*_i ∈ PT}
                           + π_ft_occ · 1{occ*_i = occ, h*_i ∈ FT}]
       + β_work · 1{h*_i > 0}
       - (1/2) · [(log w*_i - μ_occ*_i(X_i)) / σ_occ*_i]²
       - log(w*_i · σ_occ*_i · √(2π))
       + μ_occ*_i - log[Σ_{k∈{1,2,3,4}} exp(μ_k)]
       - log[Σ_{j=1}^{400} exp(V_ij)]
       }
```

where:
- **N** = sample size
- **j*_i** = observed choice for individual i
- **(c_ij*_i, L_ij*_i, h*_i, w*_i, occ*_i)** = observed characteristics
- **V_ij** = composite value function for each of 400 alternatives
- **μ_occ(X_i)** = occupation-specific mean log-wage from Mincer equation
- **All parameters** are gender-specific (suffix _sm, _sf, _m, _f)

---

## 5. PARAMETER VECTOR

The complete parameter vector θ contains **111 parameters**:

### 5.1 Preference Parameters (19 parameters)

**Leisure intercepts (4 params):**
- β_l0_sm, β_l0_sf, β_l0_m, β_l0_f

**Occupation-specific leisure shifters (12 params):**
- β_l_nm_sm, β_l_nm_sf, β_l_nm_m, β_l_nm_f
- β_l_rc_sm, β_l_rc_sf, β_l_rc_m, β_l_rc_f
- β_l_nc_sm, β_l_nc_sf, β_l_nc_m, β_l_nc_f

**Consumption (3 params):**
- β_c_sm, β_c_sf, β_c (couples shared)

---

### 5.2 Hours Opportunity Parameters (13 parameters)

**Working indicator (1 param):**
- β_work

**Part-time 1 clustering (4 params, ~20h/week):**
- π_pt1_rm, π_pt1_nm, π_pt1_rc, π_pt1_nc

**Part-time 2 clustering (4 params, ~30h/week):**
- π_pt2_rm, π_pt2_nm, π_pt2_rc, π_pt2_nc

**Full-time clustering (4 params, ~40h/week):**
- π_ft_rm, π_ft_nm, π_ft_rc, π_ft_nc

---

### 5.3 Wage Opportunity Parameters (40 parameters)

For each occupation × gender (4 occupations × 2 genders = 8 combinations) × 5 parameters:

**5 parameters per occupation-gender:**
- Intercept: β_w0_occ_g
- Experience: β_w_exp_occ_g
- Experience²: β_w_exp2_occ_g
- Education: β_w_ed_occ_g
- Std dev: σ_occ_g

**Total:** 4 occ × 2 gender × 5 params = 40 parameters

---

### 5.4 Occupation Preference Parameters (36 parameters)

For each occupation (Nonroutine manual, Routine cognitive, Nonroutine cognitive) × gender group (4 groups):

**Base preference (12 params):**
- α_nm_sm, α_nm_sf, α_nm_m, α_nm_f
- α_rc_sm, α_rc_sf, α_rc_m, α_rc_f
- α_nc_sm, α_nc_sf, α_nc_m, α_nc_f

**Education interaction (12 params):**
- α_nm_educ_sm, α_nm_educ_sf, α_nm_educ_m, α_nm_educ_f
- α_rc_educ_sm, α_rc_educ_sf, α_rc_educ_m, α_rc_educ_f
- α_nc_educ_sm, α_nc_educ_sf, α_nc_educ_m, α_nc_educ_f

**Age interaction (12 params):**
- α_nm_age_sm, α_nm_age_sf, α_nm_age_m, α_nm_age_f
- α_rc_age_sm, α_rc_age_sf, α_rc_age_m, α_rc_age_f
- α_nc_age_sm, α_nc_age_sf, α_nc_age_m, α_nc_age_f

---

### 5.5 Occupation Availability Parameters (6 parameters)

For singles only (nonroutine manual, routine cognitive, nonroutine cognitive) × gender:

- μ_nm_sm, μ_nm_sf
- μ_rc_sm, μ_rc_sf
- μ_nc_sm, μ_nc_sf

(Routine manual is reference: μ_rm = 0)

---

### 5.6 Couples Interaction Parameter (1 parameter)

- α_leisure_interact (leisure interaction between spouses)

---

### 5.7 Total Parameter Count

- Preference: 19
- Hours opportunity: 13
- Wage opportunity: 40
- Occupation preferences: 36
- Occupation availability: 6
- Couples interaction: 1

**TOTAL: 115 parameters**

---

## 6. ESTIMATION PROCEDURE

### 6.1 McFadden Sampling

For each individual i:

1. **Observe:** (h*_i, w*_i, occ*_i) from data
2. **Sample 400 alternatives:**
   - For each occupation k ∈ {1, 2, 3, 4}:
     - Sample 100 (h, w) pairs from p(h, w | occ_k, X_i)
   - Replace one alternative with observed choice
3. **Compute:** V_ij for all j = 1, ..., 400
4. **Likelihood:** ℓ_i(θ) = V_ij* - log Σ_j exp(V_ij)

### 6.2 Optimization

**Method:** L-BFGS-B (quasi-Newton with bounds)

**Objective:** Maximize Σ_i ℓ_i(θ)

**Gradients:** Analytical derivatives computed for faster convergence

**Bounds:**
- σ_occ_g ∈ [0.1, 1.0] (wage variance must be positive and bounded)
- All other parameters unbounded

**Convergence criteria:**
- Tolerance: 1e-6
- Gradient tolerance: 1e-6
- Max iterations: 2000

---

## 7. INITIAL VALUES

All 111 initial values are specified in the YAML file. Key features:

**Wage intercepts** create hierarchy:
- Managers: β_w0 ~ 3.2
- Professionals: β_w0 ~ 3.1
- Technicians: β_w0 ~ 2.9
- Service: β_w0 ~ 2.7

**Experience returns** decline with experience (negative β_w_exp2)

**Occupation preferences** initialized at zero (estimated from data)

**Hours clustering:**
- Nonroutine cognitive: low PT1 (0.3), low PT2 (0.5), high FT (2.0)
- Routine manual: high PT1 (1.5), high PT2 (1.8), moderate FT (1.2)

**Occupation availability:**
- Managers rarest: μ_mgr = -2.5
- Service most common: μ_service = 0

---

## SUMMARY

This is a **discrete choice model** where individuals choose from 400 alternatives (100 hours × 4 occupations), maximizing utility subject to market opportunities.

**Key equations:**

1. **Utility:** log v = β_c log(c) + [β_l0 + β_l_occ] log(L) + α_occ + Σ α_occ_k X_k

2. **Opportunity:** log p = log g_1(h|occ) + log g_2(w|occ,X) + log g_3(occ)

3. **Choice probability:** P(j) = exp(V_j) / Σ_k exp(V_k)

4. **Likelihood:** ℓ(θ) = Σ_i [V_ij* - log Σ_k exp(V_ik)]

**The model captures:**
- Occupation sorting by education and age
- Occupation-specific wage profiles
- Occupation-specific work hours patterns
- Occupation availability constraints
- Comprehensive labor supply and occupation choice responses

---

**Document Date:** 2026-01-27
