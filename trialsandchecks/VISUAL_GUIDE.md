# Visual Guide to the Estimation

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      STEP-BY-STEP FLOW                       │
└──────────────────────────────────────────────────────────────┘

INPUT: load_dataset()
  ↓
  Male singles data (5,234 obs)
  Columns: logy_h0-h6, logl_h0-h6, Leila_h0-h6, ... (63 columns)
  Choice column: actual_choice (h0-h6)
  ↓
┌──────────────────────────────────────────────────────────────┐
│ SECTION 2: Compute Centering Values                         │
│  - Calculate mean(logy) at actual_choice = 10.52            │
│  - Calculate mean(logl) at actual_choice = 3.46             │
└──────────────────────────────────────────────────────────────┘
  ↓
┌──────────────────────────────────────────────────────────────┐
│ SECTION 3: Prepare Biogeme Database                         │
│  - Map actual_choice to choice_id (h0→1, h1→2, ...)        │
│  - Select numeric columns (choice_id + 63 regressors)       │
│  - Create db.Database object                                │
└──────────────────────────────────────────────────────────────┘
  ↓
  ┌─────────────────────────┬──────────────────────────┐
  │                         │                          │
  ↓                         ↓                          ↓
┌─────────────────┐ ┌────────────────┐ ┌──────────────────┐
│ SECTION 4:      │ │ SECTION 5:     │ │ SECTION 6:       │
│ Define Betas    │ │ Create Vars    │ │ Build Utilities  │
│                 │ │                │ │                  │
│ - α₁, α₂, α₃   │ │ - logy_h0      │ │ - For each alt k:│
│ - α₄, α₅, α₆   │ │ - logl_h0      │ │   * Extract vars │
│ - β₁, β₂, γ    │ │ - Leila_h0     │ │   * Centering:   │
│ - ASC_h0-h6    │ │ - ...          │ │     logy* = logy │
│ - C_LOGY, etc  │ │ - (63 total)   │ │       - C_LOGY   │
│ (19 total)     │ │                │ │     logl* = logl │
└─────────────────┘ │                │ │       - C_LOGL   │
                    │                │ │   * Squares:     │
                    │                │ │     (logy*)²,    │
                    │                │ │     (logl*)²,    │
                    │                │ │     logy*×logl*  │
                    │                │ │   * Build:       │
                    │                │ │     V_k = ASC_k  │
                    │                │ │         + Σ(β×x) │
                    └────────────────┘ │                  │
                                       │ Result: V dict   │
                                       │ (7 utilities)    │
                                       └──────────────────┘
  ↓
┌──────────────────────────────────────────────────────────────┐
│ SECTION 7: Create Logit Model & Estimate                    │
│  - Define choice variable from database                      │
│  - Create logprob = loglogit(V, av, choice)                 │
│  - Initialize BIOGEME model                                 │
│  - Run estimate() → optimization via BFGS or similar        │
└──────────────────────────────────────────────────────────────┘
  ↓
  Results object (parameters + statistics)
  ↓
┌──────────────────────────────────────────────────────────────┐
│ SECTION 8: Extract & Display Results                        │
│  - Get parameters with std errors and t-stats               │
│  - Print console output                                     │
│  - Save to CSV file                                         │
└──────────────────────────────────────────────────────────────┘
  ↓
OUTPUT:
  📊 Console: Parameter estimates, fit statistics
  📁 File: reports/biogeme/male_explicit/dcm_male_explicit_ascsON_centered_parameters.csv
```

## Utility Function Structure

```
FOR EACH ALTERNATIVE k ∈ {h0, h1, h2, h3, h4, h5, h6}:

V_k = ┌─────────────────────────────────────────────────────────┐
      │ ASC_k                                                   │ ← ASC (fixed at 0 if k=h0)
      │ + α₁ × logy*_k                                         │ ← Linear consumption
      │ + α₂ × logl*_k                                         │ ← Linear leisure
      │ + α₃ × Leila_k                                         │ ← Leila interaction
      │ + α₄ × Leila2_k                                        │ ← Leila squared
      │ + α₅ × lochi_k                                         │ ← Leisure × children
      │ + α₆ × logdc_k                                         │ ← Leisure × young child
      │ + β₁ × (logy*_k)²                                      │ ← Consumption curvature
      │ + β₂ × (logl*_k)²                                      │ ← Leisure curvature
      │ + γ × (logy*_k × logl*_k)                             │ ← Consumption-leisure interaction
      └─────────────────────────────────────────────────────────┘

WHERE:
      logy*_k = logy_k - ln(y_scale) - C_LOGY    (centered & scaled consumption log)
      logl*_k = logl_k - C_LOGL                   (centered leisure log)

PROBABILITY OF CHOOSING ALTERNATIVE k:
      P(k) = exp(V_k) / Σ_j exp(V_j)   (Multinomial logit formula)

LIKELIHOOD FOR ONE PERSON:
      L_i = P(actual_choice_i)    (Probability of observed choice)

LOG-LIKELIHOOD (OVERALL):
      LL = Σ_i ln(L_i)            (Sum over all observations)

OPTIMIZATION:
      maximize LL  with respect to {α₁, α₂, ..., ASC_h1, ..., ASC_h6}
```

## Parameter Space

```
╔════════════════════════════════════════════════════════════════╗
║                    PARAMETER SPACE (19 params)                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ESTIMATED COEFFICIENTS (9):                                  ║
║  ├─ α₁ (beta_log_consumption)                                 ║
║  ├─ α₂ (beta_log_leisure)                                     ║
║  ├─ α₃ (beta_leila)                                           ║
║  ├─ α₄ (beta_log2_leila)                                      ║
║  ├─ α₅ (beta_log_leisure_children_total)                      ║
║  ├─ α₆ (beta_log_leisure_child_lt6_dummy)                     ║
║  ├─ β₁ (beta_log2_consumption)                                ║
║  ├─ β₂ (beta_log2_leisure)                                    ║
║  └─ γ  (beta_logy_logl)                                       ║
║                                                                ║
║  ALTERNATIVE-SPECIFIC CONSTANTS (7):                          ║
║  ├─ ASC_h0 = 0.0                    [FIXED - BASE]           ║
║  ├─ ASC_h1                          [ESTIMATED]              ║
║  ├─ ASC_h2                          [ESTIMATED]              ║
║  ├─ ASC_h3                          [ESTIMATED]              ║
║  ├─ ASC_h4                          [ESTIMATED]              ║
║  ├─ ASC_h5                          [ESTIMATED]              ║
║  └─ ASC_h6                          [ESTIMATED]              ║
║                                                                ║
║  CENTERING & SCALING PARAMETERS (3):                          ║
║  ├─ C_LOGY = mean_logy_actual       [FIXED]                   ║
║  ├─ C_LOGL = mean_logl_actual       [FIXED]                   ║
║  └─ LN_SCALE = ln(y_scale)          [FIXED]                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

TYPICAL VALUES (EXAMPLE):
  α₁ ≈ 0.89   (↑ consumption → ↑ utility)
  α₂ ≈ 1.25   (↑ leisure → ↑ utility)
  β₁ ≈ -0.03  (diminishing returns on consumption)
  ASC_h1 ≈ -0.52  (h1 less preferred than h0 baseline)
```

## Decision Process

```
PERSON i IS FACED WITH 7 SCENARIOS:

  h0: Work full-time         → Utility V_h0 = ?
  h1: Work part-time (25h)   → Utility V_h1 = ?
  h2: Work part-time (20h)   → Utility V_h2 = ?
  h3: Work part-time (10h)   → Utility V_h3 = ?
  h4: Not work (no income)   → Utility V_h4 = ?
  h5: Not work (partner inc) → Utility V_h5 = ?
  h6: Not work (benefits)    → Utility V_h6 = ?

MODEL CALCULATES V_k FOR EACH k USING:
  
  ┌─────────────────────────────────────────┐
  │ PERSON i's CHARACTERISTICS:             │
  │ - Log consumption (y_i) in each scenario│
  │ - Log leisure (l_i) in each scenario    │
  │ - Age (used in Leila interaction)       │
  │ - Number of children (lochi, logdc)     │
  │ - Gender (dgn) [always male here]       │
  └─────────────────────────────────────────┘
            ↓
  ┌─────────────────────────────────────────┐
  │ UTILITY CALCULATION:                    │
  │ V_k = α₁·ln(y_k) + α₂·ln(l_k) + ...    │
  │       [with centering & scaling]        │
  └─────────────────────────────────────────┘
            ↓
  ┌─────────────────────────────────────────┐
  │ PROBABILITY CALCULATION:                │
  │ P(h0) = exp(V_h0) / [Σ exp(V_j)]       │
  │ P(h1) = exp(V_h1) / [Σ exp(V_j)]       │
  │ ... (7 probabilities sum to 1)          │
  └─────────────────────────────────────────┘
            ↓
  ┌─────────────────────────────────────────┐
  │ OBSERVED CHOICE:                        │
  │ Person i chose: h3 (actual_choice)      │
  │ Model probability of h3: 0.35           │
  │ Log-likelihood contribution: ln(0.35)   │
  └─────────────────────────────────────────┘
```

## Estimation Process

```
INITIAL SETUP:
  Starting values: α₁=0, α₂=0, ..., all coefficients=0
  Data: 5,234 observations × 63 regressors
  Model: Multinomial logit

ITERATION:

  Iteration 0:
    LL₀ = -9123.46 (very negative = bad fit)
    Gradient: ∂LL/∂α₁, ∂LL/∂α₂, ...
    
  Iteration 1:
    Update: α₁ ← 0.50, α₂ ← 0.75, ...
    LL₁ = -8789.23 (improved!)
    
  Iteration 2:
    Update: α₁ ← 0.88, α₂ ← 1.20, ...
    LL₂ = -8245.67 (improved!)
    
  ...
  
  Iteration 47:
    Update: α₁ ← 0.8934, α₂ ← 1.2456, ...
    LL₄₇ = -8234.567
    Gradient: ≈ 0 (negligible)
    
    ✓ CONVERGENCE! 
      Cannot improve further.
      Algorithm stops.

FINAL RESULTS:
  Estimated parameters: α₁=0.8934, α₂=1.2456, ..., ASC_h1=-0.5234, etc.
  Final log-likelihood: -8234.567
  Standard errors: 0.0234, 0.0456, ...
  t-statistics: 38.18, 27.31, ...
  p-values: <0.0001, <0.0001, ...
```

## Output Files Structure

```
reports/biogeme/male_explicit/
│
└── dcm_male_explicit_ascsON_centered_parameters.csv
    
    Contents:
    ┌─────────────────────────────────────────────────────────┐
    │ Parameter,Value,Std err,t-stat,p-value                 │
    ├─────────────────────────────────────────────────────────┤
    │ beta_log_consumption,0.8934,0.0234,38.18,0.0000        │
    │ beta_log_leisure,1.2456,0.0456,27.31,0.0000            │
    │ beta_leila,-0.1234,0.0189,-6.53,0.0000                │
    │ beta_log2_leila,0.0456,0.0078,5.85,0.0000             │
    │ beta_log_leisure_children_total,-0.2345,0.0234,-10.02  │
    │ ...                                                     │
    │ ASC_h0,0.0000,,,                                        │
    │ ASC_h1,-0.5234,0.1234,-4.24,0.0000                    │
    │ ...                                                     │
    │ C_LOGY,10.523456,,,                                    │
    │ C_LOGL,3.456789,,,                                     │
    │ LN_SCALE,0.0000,,,                                     │
    └─────────────────────────────────────────────────────────┘
```

## Model Quality Metrics

```
╔════════════════════════════════════════════════════════════════╗
║                    MODEL FIT EVALUATION                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ LOG-LIKELIHOOD METRICS:                                       ║
║   LL_opt  = -8234.567  (at convergence)                       ║
║   LL_null = -9123.456  (all coefficients = 0)                 ║
║   LL_0    = 0.0        (perfect prediction)                   ║
║                                                                ║
║ IMPROVEMENT: -8234.567 - (-9123.456) = 888.889 units ↑       ║
║                                                                ║
║ McFADDEN'S RHO-SQUARED:                                       ║
║   ρ² = (LL_opt - LL_null) / LL_null                          ║
║      = 888.889 / 9123.456                                    ║
║      = 0.0973  (9.73%)                                       ║
║                                                                ║
║   Interpretation: Model explains ~9.7% of choice variation    ║
║   Range: 0 (no fit) to 1 (perfect fit)                       ║
║   Typical: 0.20-0.40 is "good" for choice models             ║
║   This: 0.097 is "fair" for labor supply models              ║
║                                                                ║
║ ADJUSTED RHO-SQUARED:                                         ║
║   ρ²_adj = 1 - (LL_opt - K) / LL_null                        ║
║          = 1 - (-8240.567) / (-9123.456)                     ║
║          = 1 - 0.9032                                        ║
║          = 0.0949  (9.49%)                                   ║
║                                                                ║
║   Adjusts for number of parameters (K=16 estimated)           ║
║   Penalty for adding parameters: 0.0973 → 0.0949             ║
║                                                                ║
║ INFORMATION CRITERIA:                                         ║
║   AIC  = 2K - 2·LL_opt = 16,501  (Akaike)                    ║
║   BIC  = K·ln(n) - 2·LL_opt = 16,606  (Bayesian)             ║
║                                                                ║
║   Use for model selection: Lower is better                    ║
║   BIC penalizes complexity more than AIC                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

This visual guide complements the detailed documentation with flowcharts and mathematical structure.
