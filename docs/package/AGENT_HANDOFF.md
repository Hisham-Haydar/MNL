# Agent Handoff — Read Me First

**Date:** 2026-05-26
**Author:** prior Claude session
**For:** any agent picking up work in this repo

This is the short version. Two detailed docs back it up:
- `docs/package/RURO_PATH_MIGRATION_HANDOFF.md` — full file-by-file change log
- `docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` — architecture spec

---

## 1. What I did (one sentence)

I migrated the France data off the slow network shares (`U:`, `Z:`) onto a
local SSD, and removed every hardcoded drive-letter / UNC path from the active
pipeline scripts, replacing them with runtime resolution via `path_helpers.py`.

There were also earlier commits (already in git history) reorganising the
`docs/` and `reports/` trees — see "rounds 3 & 4" in `git log`. Those are
**done and committed**. The path migration is **uncommitted** (see §4).

---

## 2. The one rule you must follow

**Never hardcode a path.** No `Path("U:/...")`, no `Path("Z:/...")`, no
`\\crc\...`, no hardcoded `2016` or `fr` in a storage path. Always:

```python
from path_helpers import data_root, resolve_storage_root
parquet = data_root() / "processed" / "fr" / "2016" / "fr_2016_RURO_mnl__singles.parquet"
```

`path_helpers.py` exists in **two identical copies** — keep them in sync:
- `scripts/path_helpers.py`
- `scripts/enhanced/path_helpers.py`

bpool scripts get their paths from the new `scripts/bpool/_bpool_paths.py`.

Public API: `resolve_storage_root()`, `data_root()`, `euromod_root()`,
`euromod_raw_root()`, `reports_root()`, `outputs_root()`, `backup_root()`,
`resolve_repo_root()`, `ensure_dir()`, `ensure_local_workdir()`.

---

## 3. Actual path resolution order (authoritative — code beats the docs)

The two detailed docs mention a project-local `./mnl_config.yaml` step. **That
step is NOT implemented.** The real order in `path_helpers.resolve_storage_root()` is:

```
1. ~/.mnl/config.yaml          →  storage_root: (or data_root:) key
2. env vars: MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT
3. ~/EUROMOD-STORAGE            (legacy fallback, if it exists)
4. FileNotFoundError           ("run mnl-setup")
```

On this machine, `~/.mnl/config.yaml` exists and points at
`C:/Users/hisham/MNL/EUROMOD-STORAGE` (gitignored, machine-specific — do not commit).

Verify your environment resolves correctly:

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, r'U:\Desktop\Nizam_Hisham\MNL\scripts'); from path_helpers import resolve_storage_root, data_root; print(resolve_storage_root()); print(data_root())"
```

Expected: `C:\Users\hisham\MNL\EUROMOD-STORAGE` and `...\EUROMOD-STORAGE\Data`.

---

## 4. Current git state — IMPORTANT before you commit

The path migration is **uncommitted** in the working tree. Modified + new files:

**Modified (22):** `.gitignore`, both `path_helpers.py`, `RURO_draws.py`,
`RURO_euromod.py`, `RURO_prep.py`, `run_post_estimation_standalone.py`,
the 5 `enhanced/` scripts, and 10 `bpool/` scripts.

**New (untracked):**
- `scripts/bpool/_bpool_paths.py` — shared bpool path module
- `scripts/sync_backup.ps1` — robocopy backup sync to the UNC archive
- `docs/package/RURO_PATH_MIGRATION_HANDOFF.md`
- `docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md`
- `docs/package/AGENT_HANDOFF.md` (this file)
- `C:\Users\hisham\.mnl\config.yaml` — outside repo, gitignored

If you `git add .` / commit, you will sweep up this whole migration. If that's
not what your task is about, **commit selectively** (only your own files) so you
don't entangle your change with this in-flight refactor.

---

## 5. What I deliberately did NOT change (so don't be surprised)

- **Docstrings / CLI examples** still show `U:/EUROMOD-STORAGE/...` paths in:
  `RURO_euromod.py`, `enh_RURO_euromod.py`, `RURO_prep.py`, `enh_RURO_prep.py`,
  and several `bpool/` module docstrings. These are **text, not live code** —
  they don't affect any run. Cosmetic cleanup, deferred.
- **`scripts/diagnostics/`** — 4 ad-hoc scripts still have live hardcoded paths
  (`check_nchildren_simple.py`, `check_preference_diagnostics.py`,
  `check_type_ids.py`, `check_nchildren_variation.py`). Not part of the main
  pipeline. Fix when you next touch them.
- **`scripts/archive/`** and **`scripts/runners/legacy/`** — frozen provenance
  records. Their hardcoded paths are intentional. Do not modify.
- **EUROMOD releases** — not migrated to C:. User-installed; set `euromod_root:`
  in `~/.mnl/config.yaml` (or `MNL_EUROMOD_ROOT`).

---

## 6. Backup sync

Local data is the working copy; the UNC share is the backup. Sync manually:

```powershell
.\scripts\sync_backup.ps1            # sync Data/processed, raw, FR + interim/outputs/reports
.\scripts\sync_backup.ps1 -DryRun    # preview only
.\scripts\sync_backup.ps1 -All       # full EUROMOD-STORAGE mirror
```

It reads source/dest from `~/.mnl/config.yaml` and no-ops gracefully if the UNC
share is unreachable.
