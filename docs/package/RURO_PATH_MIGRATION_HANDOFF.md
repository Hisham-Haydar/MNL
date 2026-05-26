# RURO Path Migration — Agent Handoff Document

**Date:** 2026-05-26  
**Scope:** Data storage consolidation + path resolution refactor across all active pipeline scripts  
**Status:** Complete for all active pipeline scripts. Diagnostics/archive deferred (see §6).

---

## 1. What Changed and Why

All data has been migrated from slow network shares (U:, Z:) to a local SSD (C:)
for ~10× faster I/O during estimation. Simultaneously, every hardcoded drive-letter
path (`U:/EUROMOD-STORAGE/...`, `Z:/hisham/EUROMOD-STORAGE/...`) in active scripts
was removed and replaced with dynamic resolution via `path_helpers.py`.

The goal is a distributable Python package: no script or module may contain a
hardcoded absolute path. All machine-specific locations are resolved at runtime.

---

## 2. Current Data Location (Developer Machine)

| What | Where |
|---|---|
| Primary working data (fast local SSD) | `C:\Users\hisham\MNL\EUROMOD-STORAGE\` |
| Backup (UNC archive, synced post-run) | `\\crc\users\hisham\MNL_backup\EUROMOD-STORAGE\` |
| Project repo / scripts | `U:\Desktop\Nizam_Hisham\MNL\` (unchanged) |
| `.venv` | `U:\Desktop\Nizam_Hisham\MNL\.venv\` (unchanged — code, not data) |
| EUROMOD releases | User-installed separately; path set in `~/.mnl/config.yaml` |

### Storage layout under `C:\Users\hisham\MNL\EUROMOD-STORAGE\`

```
EUROMOD-STORAGE/
├── Data/
│   ├── processed/fr/{2015,2016,2017}/   ← parquets (migrated from Z: and U:)
│   ├── raw/                              ← EUROMOD microdata .txt files
│   └── FR/                              ← FR-specific microdata + DRD files
├── interim/                             ← EUROMOD scenario outputs
├── new_data/                            ← bpool intermediates
├── outputs/
└── reports/
```

---

## 3. Path Resolution — How It Works Now

### Resolution order (first match wins)

```
1. ~/.mnl/config.yaml       →  storage_root: key
2. MNL_STORAGE_ROOT env var
3. MNL_DATA_ROOT env var
4. ~/EUROMOD-STORAGE        (legacy fallback if it exists)
5. FileNotFoundError        (with instructions to run mnl-setup)
```

### User config file: `C:\Users\hisham\.mnl\config.yaml`

```yaml
storage_root: C:/Users/hisham/MNL/EUROMOD-STORAGE
backup_root:  //crc/users/hisham/MNL_backup
# euromod_root: set this after installing EUROMOD separately
```

This file is **gitignored** and **machine-specific**. Never commit it.  
Future users create it by running `mnl-setup` (entry point to be implemented in package).

### Public API — always use these, never construct absolute paths

```python
from path_helpers import (
    resolve_storage_root,  # → C:\Users\hisham\MNL\EUROMOD-STORAGE
    data_root,             # → C:\Users\hisham\MNL\EUROMOD-STORAGE\Data
    euromod_root,          # → wherever user installed EUROMOD releases
    euromod_raw_root,      # → data_root() / "raw"
    reports_root,          # → storage_root / "reports"
    outputs_root,          # → storage_root / "outputs"
    backup_root,           # → \\crc\users\hisham\MNL_backup (or None)
    resolve_repo_root,     # → U:\Desktop\Nizam_Hisham\MNL (git root)
    ensure_dir,            # mkdir -p + return path
    ensure_local_workdir,  # redirect GAMSPY_WORKING_DIR off UNC shares
)
```

Both copies of `path_helpers.py` are identical and updated:
- `scripts/path_helpers.py`
- `scripts/enhanced/path_helpers.py`

### The one rule for all scripts and package code

```python
# CORRECT
from path_helpers import data_root
parquet = data_root() / "processed" / "fr" / "2016" / "fr_2016_RURO_mnl__singles.parquet"

# WRONG — never do this
parquet = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet")
parquet = Path("Z:/hisham/EUROMOD-STORAGE/...")
parquet = Path(r"\\crc\users\hisham\...")
```

---

## 4. Files Changed

### `path_helpers.py` (both copies) — rewritten

New behaviour:
- Reads `~/.mnl/config.yaml` first (new)
- Falls back to env vars, then `~/EUROMOD-STORAGE`
- Removed all hardcoded `U:/EUROMOD-STORAGE` fallback candidates
- Added `backup_root()` function (reads `backup_root:` from config)
- Error message now says "run mnl-setup" with doc reference

### `scripts/enhanced/` — fixed

| File | Change |
|---|---|
| `quick_verify.py` | `DRAWS_DIR` and `EUROMOD_OUTPUT` now use `data_root()` / `resolve_storage_root()` |
| `reduce_draws_files.py` | Argparse defaults removed; dynamic resolution added after `parse_args()` |
| `enh_RURO_euromod.py` | Deleted 85-line inline path-helper block; replaced with `from path_helpers import ...` |
| `enh_RURO_mnl_rebuild_GSURv2_stageA.py` | `REPO_ROOT` and `STORAGE` now use `resolve_repo_root()` and `data_root()` |
| `enh_RURO_prep.py` | Removed `Path("U:/EUROMOD-STORAGE")` hardcoded fallback from `_resolve_processed_dir()` |

### `scripts/` (root-level) — fixed

| File | Change |
|---|---|
| `RURO_draws.py` | Deleted 65-line inline path-helper block; replaced with `from path_helpers import ...` |
| `RURO_euromod.py` | Deleted 85-line inline path-helper block; replaced with `from path_helpers import ...` |
| `RURO_prep.py` | Removed `Path("U:/EUROMOD-STORAGE")` and `~/EUROMOD-STORAGE` hardcoded fallbacks |
| `run_post_estimation_standalone.py` | Added `from path_helpers import data_root`; fixed `mnl_file` path |

### `scripts/bpool/` — fixed

| File | Change |
|---|---|
| `_bpool_paths.py` | **New file** — shared path constants for all bpool scripts |
| `assemble_bpool_priced.py` | `_BPOOL_DIR`, `_FR_PARQUET` → from `_bpool_paths` |
| `build_bpool_couples.py` | `_DATA_DIR`, `_OUT_DIR` → from `_bpool_paths` |
| `build_bpool_singles.py` | `_DATA_DIR`, `_OUT_DIR` → from `_bpool_paths` |
| `build_bpool_precompute.py` | `_BPOOL_DIR`, `_FR_PARQUET` → from `_bpool_paths` |
| `run_bpool_euromod.py` | `_BPOOL_DIR`, `_EM_ROOT`, `_RAW_DATA`, `_FR_PARQUET` → from `_bpool_paths` |
| `run_bpool_euromod_chunk.py` | `_BPOOL_DIR`, `_EM_ROOT`, `_RAW_DATA` → from `_bpool_paths` |
| `validate_chosen_vs_canonical.py` | `_BPOOL_DIR`, `_FR_PARQUET` → from `_bpool_paths` |
| `validate_chosen_vs_tminus1.py` | `_BPOOL`, `_EM_ROOT`, `_FR` → from `_bpool_paths` |
| `validate_chosen_yem_couples.py` | `_BPOOL`, `_FR` → from `_bpool_paths` |
| `validate_female_repricing.py` | `_BPOOL` → from `_bpool_paths` |

### New files

| File | Purpose |
|---|---|
| `C:\Users\hisham\.mnl\config.yaml` | Machine-specific config; gitignored |
| `scripts/sync_backup.ps1` | Post-run robocopy sync to `\\crc\users\hisham\MNL_backup` |
| `docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` | Full architecture spec |
| `scripts/bpool/_bpool_paths.py` | Shared bpool path resolution module |

### `.gitignore` — updated

Added:
```
mnl_config.yaml
.mnl/
```

---

## 5. What Was NOT Changed (Intentional)

### Docstrings with `U:/` example paths — cosmetic only, not executable

These files still contain `U:/EUROMOD-STORAGE/...` inside docstrings or
`logger.error()` usage hints. They are **not live code** and will not affect
any run. Update them when refactoring those scripts:

- `scripts/bpool/assemble_bpool_priced.py` (module docstring)
- `scripts/bpool/build_bpool_precompute.py` (module docstring)
- `scripts/bpool/run_bpool_euromod.py` (module docstring)
- `scripts/bpool/run_bpool_euromod_chunk.py` (module docstring)
- `scripts/bpool/run_bpool_draws.py` (module docstring)
- `scripts/enhanced/enh_RURO_euromod.py` (module docstring CLI example)
- `scripts/enhanced/enh_RURO_estimate_FR.py` (module docstring CLI examples — lines 17, 948)
- `scripts/enhanced/compute_standard_errors.py` (module docstring)
- `scripts/enhanced/reduce_mnl_columns.py` (module docstring)
- `scripts/enhanced/run_cluster_robust_se.py` (module docstring)
- `scripts/diagnostics/test_gamspy_vs_scipy.py` (`logger.error()` usage hint)
- `scripts/enhanced/enh_RURO_prep.py` (docstring describing resolution order)
- `scripts/RURO_prep.py` (same)
- `scripts/RURO_euromod.py` (module docstring CLI example)

### `scripts/diagnostics/` — deferred, not active pipeline

These 4 files have live hardcoded paths but are ad-hoc scripts, not part of the
main estimation pipeline. Fix when needed:

- `check_nchildren_simple.py:8` — `Path("Z:/hisham/EUROMOD-STORAGE/...")`
- `check_preference_diagnostics.py:8` — `Path(r"Z:/hisham/EUROMOD-STORAGE/...")`
- `check_type_ids.py:7` — `Path(r"Z:/hisham/EUROMOD-STORAGE/...")`
- `check_nchildren_variation.py:9` — `Path("U:/Desktop/Nizam_Hisham/MNL/outputs/...")`

Fix pattern: replace with `from path_helpers import data_root` and
`data_root() / "processed" / "fr" / "2016" / ...`.

### `scripts/archive/` — frozen, do not modify

Files under `scripts/archive/` are provenance records. Their hardcoded paths
are intentional — they document the exact commands used at the time.

### EUROMOD releases — user-installed, not migrated

`EUROMOD_RELEASES_J1.0+/` was not copied to C:. Users install EUROMOD separately
and set the path in `~/.mnl/config.yaml`:

```yaml
euromod_root: C:/path/to/EUROMOD_RELEASES_J1.0+
```

`path_helpers.euromod_root()` reads this key first, then `MNL_EUROMOD_ROOT` env var,
then auto-discovers under `storage_root`. If none found: `FileNotFoundError`.

---

## 6. For a New Agent Continuing This Work

### To verify the environment is correct

```python
from path_helpers import resolve_storage_root, data_root, backup_root
print(resolve_storage_root())  # should be C:\Users\hisham\MNL\EUROMOD-STORAGE
print(data_root())             # should be C:\Users\hisham\MNL\EUROMOD-STORAGE\Data
print(backup_root())           # should be \\crc\users\hisham\MNL_backup
```

Or from PowerShell:

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" -c "
import sys; sys.path.insert(0, r'U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced')
from path_helpers import resolve_storage_root, data_root
print(resolve_storage_root())
print(data_root())
"
```

### To run the backup sync manually

```powershell
.\scripts\sync_backup.ps1           # sync Data/ + interim/ + outputs/ + reports/
.\scripts\sync_backup.ps1 -DryRun   # preview without copying
.\scripts\sync_backup.ps1 -All      # sync entire EUROMOD-STORAGE
```

### To add a new country/year

No code changes needed. Place parquets under:
```
C:\Users\hisham\MNL\EUROMOD-STORAGE\Data\processed\{country}\{year}\
```
Then pass `--country {cc} --year {yyyy}` to the estimation entrypoint.

### If path resolution breaks

1. Check `C:\Users\hisham\.mnl\config.yaml` exists and `storage_root:` is correct.
2. Check `C:\Users\hisham\MNL\EUROMOD-STORAGE\Data\processed\` exists.
3. Run `mnl-setup --verify` (once the entry point is implemented).
4. As a temporary override: `$env:MNL_STORAGE_ROOT = "C:/Users/hisham/MNL/EUROMOD-STORAGE"`.

---

## 7. Architecture Reference

Full spec: `docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md`  
Package portability policy: `docs/package/RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md`
