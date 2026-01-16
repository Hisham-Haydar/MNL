# 🧹 COMPREHENSIVE CLEANUP - INSTRUCTIONS

## 🎯 What This Does

**Cleans EVERYTHING:**
- ✅ Root folder
- ✅ scripts/ folder
- ✅ scripts/enhanced/ folder  
- ✅ All subfolders recursively

**Actions:**
1. **Archives** all .md files (root + subfolders) → `docs/archive/`
2. **Removes** test/debug .py files (`test_*.py`, `debug_*.py`, etc.)
3. **Removes** unnecessary .ps1 files
4. **Removes** `__pycache__` folders
5. **Moves** logs and temp files to archive

---

## 🚀 Run the Cleanup

```powershell
powershell -ExecutionPolicy Bypass -File cleanup_comprehensive.ps1
```

**Or manually approve:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\cleanup_comprehensive.ps1
```

---

## 📋 What Gets Removed

### .md Files (ARCHIVED, not deleted)
**From root:**
- All `*_FIX*.md`, `*_COMPLETE*.md`, `*_READY*.md`, etc.
- All `GAMSPY_*.md`, `COLUMN_*.md`, etc.
- **KEEPS:** `README.md`

**From scripts/ and subfolders:**
- All .md files except `README.md` in each folder
- Moved to `docs/archive/scripts_docs/`

### Python Files (REMOVED permanently)
- `test_*.py` (test files)
- `debug_*.py` (debug scripts)
- `diagnose_*.py`, `analyze_*.py`, `fix_*.py`
- `verify_*.py`, `check_*.py`
- `*_test.py`, `*_debug.py`

**EXCEPTION:** Keeps these if essential:
- `test_4group_likelihood.py`
- `test_joint_likelihood.py`

### PowerShell Files (REMOVED permanently)
- `FRESH_START_MENU.ps1`
- `RUN_COLUMN_REDUCTION.ps1`
- `run_estimation_detailed_log.ps1`
- `run_estimation_verbose.ps1`
- `run_gamspy_joint.ps1`
- `test_column_reduction_dry_run.ps1`
- `run_gamspy.ps1`

**KEEPS:**
- `RUN_PIPELINE_WITH_REDUCED_FILES.ps1`
- `cleanup_workspace.ps1`
- `cleanup_repo.ps1`

### Temporary Files (MOVED to archive)
- `__pycache__/` directories
- `*.pyc` files
- `*.log` files
- `*_output.txt`, `*_columns.txt`, `dry_run*.txt`

---

## 📁 Archive Structure

```
docs/archive/
├── troubleshooting_sessions/  (root .md files)
├── scripts_docs/              (scripts/ .md files)
├── logs/                      (log files, temp outputs)
├── old_scripts/               (old .ps1 files)
└── test_files/                (archived test files)
```

---

## ✅ After Cleanup

### Root Folder Will Have:
- `README.md`
- `RUN_PIPELINE_WITH_REDUCED_FILES.ps1`
- `cleanup_comprehensive.ps1`
- `cleanup_repo.ps1`
- `pyproject.toml`
- `requirements.txt`
- Essential config files

### scripts/ Folder Will Have:
- Only production scripts
- `README.md` in each subfolder
- **NO** .md documentation files
- **NO** test_*.py files

### scripts/enhanced/ Will Have:
- Only production scripts (enh_*.py)
- estimation_spec*.yaml files
- **NO** .md files
- **NO** test files

---

## ⚠️ IMPORTANT

**This cleanup is AGGRESSIVE:**
- Test files are **REMOVED permanently** (not archived)
- Only .md files are archived
- Make sure you don't need any test files before running

**If unsure:**
1. Review what will be removed (see lists above)
2. Backup important test files manually first
3. Then run cleanup

---

## 🔄 Undo (If Needed)

**Can restore:**
- ✅ .md files (archived in `docs/archive/`)

**Cannot restore:**
- ❌ Test .py files (permanently deleted)
- ❌ Old .ps1 files (permanently deleted)
- ❌ __pycache__ folders (can be regenerated)

---

## 📊 Expected Results

### Before:
```
Root: 42+ .md files, many test_*.py, old .ps1
scripts/: Many .md files
scripts/enhanced/: Many .md files
__pycache__/: Everywhere
```

### After:
```
Root: 1 .md file (README.md), 3-4 .ps1 files
scripts/: 0-1 .md files (README.md only)
scripts/enhanced/: 0-1 .md files (README.md only)
__pycache__/: Cleaned
```

---

## 🚀 Quick Start

**Just run:**
```powershell
powershell -ExecutionPolicy Bypass -File cleanup_comprehensive.ps1
```

**When prompted, type `y` to confirm.**

The script will show you everything it's doing in real-time!

---

**Ready to clean your workspace!** 🧹
