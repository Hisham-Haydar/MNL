# Timestamped Output Folders - Feature Documentation

**Date:** 2026-01-16  
**Status:** ✅ IMPLEMENTED

---

## Overview

New `--auto-timestamp` flag automatically creates timestamped subfolders for each estimation/post-estimation run, keeping all outputs organized by date/time.

---

## What It Does

### Before (Default Behavior)
```
outputs/estimates/fr/2016/
├── estimation.log
├── estimation_results.json
└── parameters.csv
```

**Problem:** Multiple runs overwrite each other!

### After (With `--auto-timestamp`)
```
outputs/estimates/fr/2016/
├── run_2026-01-16_09-30-15/
│   ├── estimation.log
│   ├── estimation_results.json
│   └── parameters.csv
├── run_2026-01-16_14-25-42/
│   ├── estimation.log
│   ├── estimation_results.json
│   └── parameters.csv
└── run_2026-01-17_10-15-33/
    ├── estimation.log
    ├── estimation_results.json
    └── parameters.csv
```

**Benefit:** Complete history of all runs, never lose results!

---

## Usage

### Estimation Script

```powershell
# Without timestamp (overwrites previous run)
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016 `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\estimation_spec.yaml

# With timestamp (creates run_YYYY-MM-DD_HH-MM-SS subfolder)
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016 `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --auto-timestamp
```

### Post-Estimation Script

```powershell
# Without timestamp
python scripts\enhanced\RURO_post_estimation_styled.py `
    --results-json outputs\estimates\fr\2016\estimation_results.json `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016

# With timestamp (creates run_YYYY-MM-DD_HH-MM-SS subfolder)
python scripts\enhanced\RURO_post_estimation_styled.py `
    --results-json outputs\estimates\fr\2016\run_2026-01-16_09-30-15\estimation_results.json `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\post_estimation\fr\2016 `
    --auto-timestamp
```

---

## Complete Workflow Example

### Step 1: Run Estimation with Timestamp

```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016 `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --auto-timestamp
```

**Output:**
```
Auto-timestamp enabled: outputs\estimates\fr\2016\run_2026-01-16_14-30-25
...
Estimation complete! Results saved to: outputs\estimates\fr\2026-01-16_14-30-25
```

**Files created:**
```
outputs/estimates/fr/2016/run_2026-01-16_14-30-25/
├── estimation.log              # Full estimation log
├── estimation_results.json     # Parameter estimates + metadata
├── parameters.csv              # Parameter table
└── diagnostics/                # (if generated)
```

### Step 2: Run Post-Estimation on That Run

```powershell
# Note: Use the timestamped path from Step 1
python scripts\enhanced\RURO_post_estimation_styled.py `
    --results-json outputs\estimates\fr\2016\run_2026-01-16_14-30-25\estimation_results.json `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --output-dir outputs\post_estimation\fr\2016 `
    --auto-timestamp
```

**Output:**
```
Auto-timestamp enabled: outputs\post_estimation\fr\2016\run_2026-01-16_14-35-12
...
Post-estimation complete!
```

**Files created:**
```
outputs/post_estimation/fr/2016/run_2026-01-16_14-35-12/
├── post_estimation.log
├── summary_statistics.csv
├── elasticities_sm.csv
├── elasticities_sf.csv
├── elasticities_cou.csv
├── plots/
│   ├── wage_response_sm.png
│   ├── wage_response_sf.png
│   └── participation_probability.png
└── tables/
    └── formatted_results.html
```

---

## Folder Naming Convention

**Format:** `run_YYYY-MM-DD_HH-MM-SS`

**Examples:**
- `run_2026-01-16_09-30-15` - January 16, 2026 at 9:30:15 AM
- `run_2026-01-16_14-25-42` - January 16, 2026 at 2:25:42 PM
- `run_2026-01-17_10-15-33` - January 17, 2026 at 10:15:33 AM

**Sorting:** Folders sort chronologically (YYYY-MM-DD format)

---

## Use Cases

### 1. Comparing Different Specifications

```powershell
# Run 1: Base specification
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_base `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --auto-timestamp ...

# Run 2: Alternative specification
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_alt `
    --spec-config scripts\enhanced\estimation_spec_v2.yaml `
    --auto-timestamp ...
```

**Result:**
```
outputs/estimates/fr/
├── 2016_base/
│   └── run_2026-01-16_09-00-00/
└── 2016_alt/
    └── run_2026-01-16_10-00-00/
```

### 2. Comparing SciPy vs GAMSPy

```powershell
# SciPy run
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_scipy `
    --solver scipy `
    --auto-timestamp ...

# GAMSPy run
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_gamspy `
    --solver gamspy-conopt `
    --auto-timestamp ...
```

### 3. Parameter Sensitivity Testing

```powershell
# Test different initial values
python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_sensitivity `
    --init-params test_values_1.csv `
    --auto-timestamp ...

python scripts\enhanced\enh_RURO_estimate_FR.py `
    --output-dir outputs\estimates\fr\2016_sensitivity `
    --init-params test_values_2.csv `
    --auto-timestamp ...
```

**Result:**
```
outputs/estimates/fr/2016_sensitivity/
├── run_2026-01-16_09-00-00/  # Init values 1
└── run_2026-01-16_09-15-00/  # Init values 2
```

---

## Finding Latest Run

### PowerShell

```powershell
# Get most recent estimation run
$latest = Get-ChildItem "outputs\estimates\fr\2016" -Filter "run_*" | 
          Sort-Object Name -Descending | 
          Select-Object -First 1
          
Write-Host "Latest run: $($latest.FullName)"

# Use it in post-estimation
python scripts\enhanced\RURO_post_estimation_styled.py `
    --results-json "$($latest.FullName)\estimation_results.json" `
    --auto-timestamp ...
```

### Python Helper Function

```python
from pathlib import Path
from datetime import datetime

def get_latest_run(base_dir: Path) -> Path:
    """Get most recent run_* folder"""
    runs = sorted(base_dir.glob("run_*"), reverse=True)
    if not runs:
        raise FileNotFoundError(f"No run folders in {base_dir}")
    return runs[0]

# Usage
latest = get_latest_run(Path("outputs/estimates/fr/2016"))
results_path = latest / "estimation_results.json"
```

---

## Backward Compatibility

**Default behavior:** `--auto-timestamp` is **OFF** by default

- ✅ Existing scripts work without changes
- ✅ Opt-in feature (add flag when you want it)
- ✅ No breaking changes

---

## Tips & Best Practices

### 1. Always Use for Production Runs

```powershell
# ✅ GOOD: Never lose results
--auto-timestamp

# ❌ BAD: Overwrites previous run
# (no timestamp flag)
```

### 2. Organize by Purpose

```
outputs/
├── experiments/           # Exploratory runs
│   └── test_idea_1/
│       ├── run_2026-01-16_09-00-00/
│       └── run_2026-01-16_10-00-00/
├── production/            # Final results
│   └── fr_2016_final/
│       └── run_2026-01-16_15-00-00/
└── debugging/             # Test runs
    └── bug_fix_test/
        └── run_2026-01-16_11-00-00/
```

### 3. Keep Notes

Create `README.md` in each run folder:

```markdown
# Run Notes: 2026-01-16 14:30

## Purpose
Testing GAMSPy CONOPT vs SciPy performance

## Specification
- Base spec (estimation_spec.yaml)
- GAMSPy CONOPT solver
- Joint estimation

## Results
- Runtime: 14.2 minutes (vs 35 min with SciPy)
- Final LL: -25,249.26
- Converged successfully

## Notes
- First production run with GAMSPy
- All validation checks passed
```

### 4. Archive Old Runs

```powershell
# Compress old runs
Compress-Archive -Path "outputs\estimates\fr\2016\run_2026-01-*" `
                 -DestinationPath "archives\estimates_jan_2026.zip"

# Delete originals (after verifying archive)
Remove-Item "outputs\estimates\fr\2016\run_2026-01-*" -Recurse
```

---

## Troubleshooting

### Issue: Too many folders

**Solution:** Use date-based organization:

```powershell
# Instead of flat structure:
outputs/estimates/fr/2016/
├── run_2026-01-16_09-00-00/
├── run_2026-01-16_10-00-00/
├── ... (100 more folders)

# Use date subfolders:
outputs/estimates/fr/2016/
├── 2026-01-16/
│   ├── run_09-00-00/
│   ├── run_10-00-00/
│   └── run_11-00-00/
└── 2026-01-17/
    └── run_09-00-00/
```

*(Not implemented yet - future enhancement)*

### Issue: Long paths on Windows

**Problem:** Windows has 260-character path limit

**Solution:** Use shorter base paths:

```powershell
# ❌ BAD: Long path
--output-dir "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\france\2016\sensitivity_analysis\"

# ✅ GOOD: Shorter path
--output-dir "outputs\est\fr\2016"
```

---

## Implementation Details

### Modified Files

1. **`scripts/enhanced/enh_RURO_estimate_FR.py`**
   - Added `--auto-timestamp` argument
   - Auto-creates `run_{timestamp}` subfolder
   - Logs timestamp info

2. **`scripts/enhanced/RURO_post_estimation_styled.py`**
   - Added `--auto-timestamp` argument
   - Auto-creates `run_{timestamp}` subfolder
   - Handles `None` output_dir gracefully

### Code Changes

```python
# Estimation script
if args.auto_timestamp:
    timestamp = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")
    output_dir = output_dir_base / timestamp
    print(f"Auto-timestamp enabled: {output_dir}")
```

```python
# Post-estimation script
if args.auto_timestamp:
    timestamp = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")
    if output_dir is None:
        output_dir = args.results_json.parent / timestamp
    else:
        output_dir = Path(output_dir) / timestamp
```

---

## Future Enhancements

### 1. Auto-cleanup old runs

```powershell
--auto-cleanup-days 30  # Delete runs older than 30 days
```

### 2. Run metadata file

Auto-create `run_metadata.json`:

```json
{
  "timestamp": "2026-01-16T14:30:25",
  "command": "python ...",
  "spec_config": "estimation_spec.yaml",
  "solver": "gamspy-conopt",
  "runtime_seconds": 842.3,
  "final_ll": -25249.26
}
```

### 3. Symlink to latest

Auto-create symlink `latest/` → most recent run

---

## Summary

**Feature:** `--auto-timestamp`  
**Status:** ✅ Implemented  
**Files:** Estimation + Post-Estimation  
**Default:** OFF (backward compatible)  
**Benefit:** Never lose results, complete run history

**Usage:**
```powershell
# Just add this flag to any command:
--auto-timestamp
```

**Result:**
```
outputs/
└── run_2026-01-16_14-30-25/  ← All outputs here!
    ├── estimation.log
    ├── estimation_results.json
    └── ...
```

---

**Recommended:** Use `--auto-timestamp` for ALL production runs!
