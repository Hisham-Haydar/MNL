# ==============================================================================
# PHASE 1 EXECUTION GUIDE
# ==============================================================================
# How to run all 4 SciPy specification tests in parallel
# ==============================================================================

## WHAT TO RUN

You have a ready-to-run PowerShell script:

  FILE: phase1_scipy_commands.ps1

  This file contains all 4 SciPy commands ready to execute.

---

## HOW TO RUN (Two Options)

### OPTION 1: Run the full script at once (RECOMMENDED)
```powershell
# In PowerShell, navigate to MNL directory:
cd U:\Desktop\Nizam_Hisham\MNL

# Run the script:
.\phase1_scipy_commands.ps1

# That's it! All 4 will run in parallel, then script waits for completion.
```

### OPTION 2: Copy-paste individual commands
```powershell
# Copy each of the 4 commands from phase1_scipy_commands.ps1
# Open PowerShell in U:\Desktop\Nizam_Hisham\MNL
# Paste each command (ends with &)
# Each will start in background immediately

# Then run:
Get-Job | Wait-Job
```

---

## WHAT WILL HAPPEN

### During Execution (2-3 hours total):

Each specification will:
1. Load French RURO MNL data
2. Parse the specification YAML
3. Run optimization with SciPy L-BFGS-B
4. Compute standard errors (numerical Hessian)
5. Save results to JSON

You'll see:
- 4 PowerShell prompts return immediately (background execution)
- "All 4 SciPy runs started in parallel..." message
- Script waits with "Waiting for completion..."
- Logs written to: outputs/estimates/fr/spec_tests/N_*/run_*/estimation.log

---

## WHERE RESULTS WILL BE

After completion, you'll have:

```
outputs/estimates/fr/spec_tests/
├── 1_minimal_theta0_scipy/
│   └── run_2026-01-XX_HH-MM-SS/
│       ├── estimation_results.json     ← KEY FILE
│       ├── estimation.log
│       ├── estimation_summary.txt
│       └── ...
├── 2_pooled_consumption_scipy/
│   └── run_2026-01-XX_HH-MM-SS/
│       ├── estimation_results.json     ← KEY FILE
│       └── ...
├── 3_pooled_leisure_scipy/
│   └── run_2026-01-XX_HH-MM-SS/
│       ├── estimation_results.json     ← KEY FILE
│       └── ...
└── 4_ultra_minimal_scipy/
    └── run_2026-01-XX_HH-MM-SS/
        ├── estimation_results.json     ← KEY FILE
        └── ...
```

---

## HOW TO EXTRACT RESULTS

After all 4 complete, extract key metrics from each `estimation_results.json`:

```python
import json

specs = [
    "1_minimal_theta0_scipy",
    "2_pooled_consumption_scipy",
    "3_pooled_leisure_scipy",
    "4_ultra_minimal_scipy"
]

for spec in specs:
    # Find latest run directory
    result_file = f"outputs/estimates/fr/spec_tests/{spec}/run_*/estimation_results.json"

    with open(result_file) as f:
        data = json.load(f)

    # Extract key metrics
    ll = data["results"]["singles_male"]["log_likelihood"]  # or check structure
    cond_num = data.get("hessian_diagnostics", {}).get("condition_number", "N/A")
    n_params = len(data["specification"]["all_param_names"])

    print(f"{spec}:")
    print(f"  LL: {ll}")
    print(f"  Cond #: {cond_num}")
    print(f"  k: {n_params}")
```

---

## WHAT MAKES EACH SPEC DIFFERENT

### SPEC 1: minimal_theta0 (Baseline - 15 params)
- Consumption: 3 separate (beta_c, beta_c_sm, beta_c_sf)
- Leisure: 4 separate (beta_l0_sm, beta_l0_sf, beta_l0_m, beta_l0_f)
- Utility: Box-Cox with theta params (all at bounds → log utility)
- **Purpose:** Your current baseline (should match recent run)

### SPEC 2: pooled_consumption (13 params)
- Consumption: 1 pooled (beta_c for all)
- Leisure: 4 separate
- Utility: Log-only (no theta)
- **Purpose:** Test if consumption utility differs by group
- **Expected:** Condition # should improve ~20-30%

### SPEC 3: pooled_leisure (13 params)
- Consumption: 3 separate
- Leisure: 2 by gender (beta_l0_m, beta_l0_f)
- Utility: Log-only
- **Purpose:** Test if marital status affects leisure
- **Expected:** Smaller improvement (leisure issue is secondary)

### SPEC 4: ultra_minimal (7 params)
- Consumption: 1 pooled
- Leisure: 2 by gender
- Utility: Log-only
- **Purpose:** Maximum simplification - test if works
- **Expected:** Condition # < 1,000 (best identification)

---

## EXPECTED OUTCOMES

### Log-Likelihood Comparison
- Should decrease slightly as you add constraints
- Example: -6954 → -6955 → -6956 → -6958 (normal)
- Large jumps (> 10 LL units) suggest constraint violation

### Condition Number Progression
- Baseline: ~17,000 (SEVERE)
- Pooled consumption: ~12,000 (still severe)
- Pooled leisure: ~14,000 (moderate improvement)
- Ultra minimal: ~1,000 or less (EXCELLENT)

### Recommendation Decision Tree
```
IF ultra_minimal cond # < 1,000:
  → Use ultra_minimal as final spec ✓
ELSE IF pooled_consumption cond # < 5,000:
  → Use pooled_consumption
ELSE:
  → Fundamental identification issue, need different model
```

---

## NEXT STEP AFTER PHASE 1

Once Phase 1 completes:

1. **Collect results** from all 4 estimation_results.json files
2. **Compare LL, cond #, AIC, BIC** for each spec
3. **Pick best 2-3 specs** (lowest cond #, best BIC)
4. **Run Phase 2**: phase2_gamspy_commands.ps1
   - Uses GAMSPy CONOPT on top specs
   - Validates solver agreement
   - Gets exact Hessian diagnostics

---

## TROUBLESHOOTING

### If a spec fails to converge
- Check the estimation.log file for errors
- Common issues:
  - Bounds too tight (theta [0, 1e-6])
  - Poor warm-start values
  - Singular Hessian (identification issue)
- Solution: Increase maxiter or relax bounds slightly

### If all specs fail
- Check data files exist at:
  `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl`
- Check spec YAML files exist in:
  `scripts/enhanced/estimation_spec_*.yaml`
- Review estimation.log for specific error

### If results look very different from expected
- Check warm-start values are correct
- Verify specification YAML is valid
- Compare to your recent successful run

---

## TIMELINE

**Execution:**
- Start Phase 1 (all 4 parallel): Take ~2-3 hours
- Check results: 15-30 minutes
- Start Phase 2 (2-3 specs): Take ~2-3 hours

**Total:** 4-7 hours elapsed time (much of it parallel)

---

## YOUR COMMANDS AT A GLANCE

You asked for 4 commands. Here's what you're running:

1. **minimal_theta0** (baseline):
   - Uses: --spec-config estimation_spec_minimal_theta0.yaml
   - Output: outputs/estimates/fr/spec_tests/1_minimal_theta0_scipy

2. **pooled_consumption** (test):
   - Uses: --spec-config estimation_spec_pooled_consumption.yaml
   - Output: outputs/estimates/fr/spec_tests/2_pooled_consumption_scipy

3. **pooled_leisure** (test):
   - Uses: --spec-config estimation_spec_pooled_leisure.yaml
   - Output: outputs/estimates/fr/spec_tests/3_pooled_leisure_scipy

4. **ultra_minimal** (best case):
   - Uses: --spec-config estimation_spec_ultra_minimal.yaml
   - Output: outputs/estimates/fr/spec_tests/4_ultra_minimal_scipy

All use:
- Solver: scipy (L-BFGS-B, fast)
- Method: L-BFGS-B with bounds
- Warm-start: From your recent successful minimal_theta0 run
- Auto-timestamp: Automatic run directory naming

---

## READY?

Run: `.\phase1_scipy_commands.ps1` and let it finish!

Then send me the results and we'll analyze Phase 2.
