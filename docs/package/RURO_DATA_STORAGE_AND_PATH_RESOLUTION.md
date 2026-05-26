# RURO Data Storage and Path Resolution

**Scope:** defines how the RURO package locates data at runtime — on the
developer's machine today, and on any user's machine once the package is
published.

**Design principle:** the package itself contains zero hardcoded paths.
All machine-specific locations are resolved at runtime through a layered
config system. Scripts and modules never import or reference a drive letter,
UNC share, or absolute path.

---

## 1. Resolution Order

When any package code calls `path_helpers.resolve_storage_root()` or
`path_helpers.data_root()`, the lookup proceeds in this exact order:

```
1. ~/.mnl/config.yaml          (user-level, machine-specific, never committed)
2. Environment variables        (MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT)
3. ~/EUROMOD-STORAGE           (legacy fallback — if it exists on disk)
4. FileNotFoundError           (clear error with setup instructions)
```

> Note: an earlier draft of this doc listed a project-local `./mnl_config.yaml`
> step. That is **not** implemented in `path_helpers.py` — the real order is the
> four steps above.

The first location that exists and contains `Data/processed` or `Data/raw`
wins. This means a user on a different machine just needs step 1 — they
install the package, run `mnl-setup`, and are done.

---

## 2. User Config File: `~/.mnl/config.yaml`

Created once by running `mnl-setup` (or by the user manually).
Never committed to git. Gitignored globally.

**Schema:**

```yaml
# ~/.mnl/config.yaml
# Created by: mnl-setup
# Edit manually if your paths change.

storage_root: /path/to/EUROMOD-STORAGE     # contains Data/, interim/, reports/
data_root:    /path/to/EUROMOD-STORAGE/Data # optional override; derived from storage_root if absent
euromod_root: /path/to/EUROMOD_RELEASES    # optional; discovered under storage_root if absent
backup_root:  /path/to/backup/location     # optional; used by sync_backup
```

**Examples per machine type:**

| Machine | `storage_root` |
|---|---|
| Developer workstation (Windows) | `C:/Users/hisham/MNL/EUROMOD-STORAGE` |
| CRC network share (UNC) | `//crc/users/hisham/MNL/EUROMOD-STORAGE` |
| HPC cluster (Linux) | `/scratch/hisham/EUROMOD-STORAGE` |
| Package user (any OS) | wherever they store their country data |

---

## 3. Environment Variable Overrides

For HPC/cluster environments where a config file is inconvenient:

| Variable | Meaning |
|---|---|
| `MNL_STORAGE_ROOT` | Overrides `storage_root` from config |
| `MNL_DATA_ROOT` | Overrides `data_root` from config |
| `MNL_EUROMOD_ROOT` | Overrides `euromod_root` from config |
| `MNL_BACKUP_ROOT` | Overrides `backup_root` from config |

Environment variables take precedence over the config file.

---

## 4. `mnl-setup` CLI Entry Point

Installed as a console script when the package is installed (`pip install ruro-mnl`).

**Usage:**

```bash
mnl-setup
```

**Interactive prompts:**

```
RURO MNL — first-time setup
----------------------------
Storage root (directory containing Data/, interim/, reports/):
  > C:/Users/hisham/MNL/EUROMOD-STORAGE

EUROMOD releases directory [auto-detect]:
  > (leave blank to auto-detect under storage root)

Backup root (optional — for post-run sync):
  > //crc/users/hisham/MNL_backup

Config written to: C:/Users/hisham/.mnl/config.yaml
Run `mnl-setup --verify` to confirm all paths resolve correctly.
```

**Verify:**

```bash
mnl-setup --verify
```

Output:

```
storage_root  : C:/Users/hisham/MNL/EUROMOD-STORAGE  [OK]
data_root     : C:/Users/hisham/MNL/EUROMOD-STORAGE/Data  [OK]
euromod_root  : C:/Users/hisham/MNL/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+  [OK]
backup_root   : //crc/users/hisham/MNL_backup  [OK — reachable]
```

---

## 5. Expected Storage Layout

The package expects this layout under `storage_root`:

```
EUROMOD-STORAGE/
├── Data/
│   ├── processed/
│   │   └── {country}/
│   │       ├── {year}/
│   │       │   ├── {country}_{year}_RURO_mnl_{spec}__singles.parquet
│   │       │   ├── {country}_{year}_RURO_mnl_{spec}__couples.parquet
│   │       │   └── {country}_{year}_RURO_mnl_{spec}__mnlmeta.json
│   │       └── pooled/                      (multi-year stage-M1 / gsurv2 inputs)
│   ├── raw/
│   │   └── {COUNTRY}_{year}_{version}.txt   (EUROMOD microdata)
│   ├── FR/ , DE/                            (country raw microdata + DRD files)
│   ├── interim/
│   │   └── ruro/{country}/scenarios.../     (EUROMOD scenario outputs — under Data/)
│   └── inspecting/                          (audit + exploration outputs)
├── new_data/                                (bpool intermediates: chunks, precompute, priced)
├── Euromod_model/                           (EUROMOD system software — NOT data, NOT backed up)
├── reports/
└── outputs/
```

Note: `interim/` lives **under `Data/`** (`Data/interim/ruro/...`), not at the
storage root. The EUROMOD system (`Euromod_model/`, currently
`EUROMOD_RELEASES_J2.0+`) is re-downloadable software kept alongside the data but
excluded from the data backup; point `euromod_root` at it (see §6).

This layout is country/year-agnostic by design: adding Germany 2019 means
adding `Data/processed/de/2019/` with the canonical filenames — no code change.

---

## 6. Developer Machine Setup (Current: Hisham)

The working data for the France case lives locally at:

```
C:\Users\hisham\MNL\EUROMOD-STORAGE\     ← fast local SSD (~7 GB/s read)
```

With backup sync to:

```
\\crc\users\hisham\MNL_backup\EUROMOD-STORAGE\    ← UNC archive
```

Config at `C:\Users\hisham\.mnl\config.yaml`:

```yaml
storage_root: C:/Users/hisham/MNL/EUROMOD-STORAGE
backup_root:  //crc/users/hisham/MNL_backup
euromod_root: C:/Users/hisham/MNL/EUROMOD-STORAGE/Euromod_model/EUROMOD_RELEASES_J2.0+
```

`euromod_root` is set explicitly because auto-discovery would otherwise stop at the
`Euromod_model/` parent rather than the nested `EUROMOD_RELEASES_J2.0+` release
(which contains `Input/`, `XMLParam/Countries`, etc.).

Post-run sync is triggered automatically by the estimation pipeline and
can also be run manually:

```powershell
# From project root
.\scripts\sync_backup.ps1
```

---

## 7. What Scripts Must NOT Do

Scripts and package modules must never:

- Import or construct an absolute path to a drive letter (`U:/`, `Z:/`, `C:/`)
- Import or construct a UNC path (`\\crc\...`, `\\users\...`)
- Use a hardcoded default path as a `Path(...)` literal anywhere except
  `path_helpers.py`'s explicit fallback list
- Use `os.chdir()` to a data directory (breaks relative-path saves)
- Hardcode a year (`2016`) or country (`fr`) in a storage path

**Correct pattern:**

```python
from path_helpers import data_root

processed = data_root() / "processed" / country / str(year)
singles = processed / f"{country}_{year}_RURO_mnl_{spec}__singles.parquet"
```

**Incorrect pattern (never do this):**

```python
singles = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet")
```

---

## 8. Adding a New Country/Year

No code changes needed. Steps:

1. Prepare MNL-ready parquets following the canonical schema (see
   `RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md` §4).
2. Place them under `storage_root/Data/processed/{country}/{year}/`.
3. Run `mnl-setup --verify` to confirm the path resolves.
4. Pass `--country {cc} --year {yyyy}` to the estimation entrypoint.

---

## 9. Migration History

| Date | Change |
|---|---|
| 2026-05-26 | Initial policy. Migrated France 2015–2017 data from `Z:\hisham\EUROMOD-STORAGE` and `U:\EUROMOD-STORAGE` to `C:\Users\hisham\MNL\EUROMOD-STORAGE`. Introduced `~/.mnl/config.yaml` and `mnl-setup` entry point. Removed all hardcoded `U:/` and `Z:/` paths from active pipeline scripts. |
| 2026-05-26 | Consolidation: migrated the remaining U:/Z:-only data into C: — bpool `new_data`, `pooled` (moved out of the repo working tree), `interim` (relocated under `Data/interim`), `Data/DE`, `Data/inspecting`, and loose raw files. First `\\crc` backup created and verified (10.8 GB). Legacy experiment dirs cold-archived to `\\crc\…\_legacy_archive`. EUROMOD system pinned to `Euromod_model/EUROMOD_RELEASES_J2.0+`. See `RURO_DATA_CONSOLIDATION_2026-05-26.md`. |
