# 🧹 WORKSPACE CLEANUP GUIDE

**Problem:** 42+ troubleshooting .md files cluttering the workspace

**Solution:** Move them to organized archive folders

---

## 🚀 Quick Cleanup (Copy & Paste)

```powershell
# Create archive directories
New-Item -ItemType Directory -Force -Path "docs/archive/troubleshooting_sessions" | Out-Null
New-Item -ItemType Directory -Force -Path "docs/archive/logs" | Out-Null
New-Item -ItemType Directory -Force -Path "docs/archive/old_scripts" | Out-Null

# Move troubleshooting/session .md files
Move-Item -Path "*_FIX*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_FIXED*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_COMPLETE*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_READY*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_STATUS*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_SUMMARY*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_RESULTS*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_ANALYSIS*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_IMPLEMENTATION*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_GUIDE*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_COMMANDS*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*SESSION*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*DEBUG*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "GAMSPY_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "COLUMN_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "POST_ESTIMATION_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "DRAWS_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "ESTIMATION_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "COUPLES_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "DEMOGRAPHICS_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "R_vs_PYTHON*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "RURO_POST*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "INDENTATION*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "ALL_*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*START_HERE*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*QUICK_REF*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "FRESH_START*.md" -Destination "docs/archive/troubleshooting_sessions/" -Force -ErrorAction SilentlyContinue

# Move log files
Move-Item -Path "*.log" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_output.txt" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_columns.txt" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "*_analysis.txt" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue

# Move debug/diagnostic scripts
Move-Item -Path "debug_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "diagnose_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "analyze_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "fix_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "compute_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "run_gamspy.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CLEAN_*.py" -Destination "docs/archive/logs/" -Force -ErrorAction SilentlyContinue

# Move old PowerShell scripts
Move-Item -Path "FRESH_START_MENU.ps1" -Destination "docs/archive/old_scripts/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "RUN_COLUMN_REDUCTION.ps1" -Destination "docs/archive/old_scripts/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "run_estimation_detailed_log.ps1" -Destination "docs/archive/old_scripts/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "run_estimation_verbose.ps1" -Destination "docs/archive/old_scripts/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "run_gamspy_joint.ps1" -Destination "docs/archive/old_scripts/" -Force -ErrorAction SilentlyContinue

Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
Write-Host "`nArchived to:" -ForegroundColor Cyan
Write-Host "  - docs/archive/troubleshooting_sessions/ (session .md files)"
Write-Host "  - docs/archive/logs/ (log files & debug scripts)"
Write-Host "  - docs/archive/old_scripts/ (old PowerShell scripts)"

Write-Host "`nRemaining in root:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.md" -File | Select-Object Name
Get-ChildItem -Path . -Filter "*.ps1" -File | Select-Object Name
```

---

## 📁 What Gets Kept in Root

**Essential files only:**
- `README.md` - Main project documentation
- `RUN_PIPELINE_WITH_REDUCED_FILES.ps1` - Pipeline runner
- `cleanup_workspace.ps1` - This cleanup script
- `verify_optimizations.py` - Optimization checker
- `test_column_filtering.py` - Column filtering test

**Everything else moves to `docs/archive/`**

---

## ✅ After Cleanup

Your root folder will have:
- **~5 files** instead of 42+ .md files
- Clean, organized structure
- All troubleshooting docs archived for reference

---

## 🔍 To View Archived Files Later

```powershell
# List troubleshooting session docs
Get-ChildItem docs/archive/troubleshooting_sessions/

# List logs
Get-ChildItem docs/archive/logs/

# List old scripts
Get-ChildItem docs/archive/old_scripts/
```

---

**Just copy & paste the commands above to clean your workspace!** 🧹
