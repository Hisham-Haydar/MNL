# RURO Data Consolidation — 2026-05-26

**Goal:** eliminate data replicated across drives. Make `C:\Users\hisham\MNL\EUROMOD-STORAGE`
the single canonical store, automatically backed up to `\\crc`, and remove the
duplicate copies from `U:` and `Z:`.

This document records every step so another agent can verify or continue the work.

---

## 1. Starting situation (inventory)

Three distinct physical servers held overlapping copies:

| Drive | Maps to | Held |
|---|---|---|
| `C:` | local SSD | partial store (only `Data/processed/fr` had been migrated earlier) |
| `U:` | `\\users\users\hisham` | repo (`U:\Desktop\…\MNL`) **and** a full `U:\EUROMOD-STORAGE` replica |
| `Z:` | `\\aff300msh.cifs.myliser.lu\ComputeShare` | full `Z:\hisham\EUROMOD-STORAGE` replica |
| `H:` | `\\crc\users\hisham` | backup target (`MNL_backup`) — **did not exist yet** |

Data that was **missing from C:** before this session:

| Data | Authoritative source | Size |
|---|---|---|
| `new_data` (bpool: chunks, precompute, priced, d1w1) | `U:\EUROMOD-STORAGE\new_data` | 2.81 GB |
| `pooled` (gsurv2, provisional, stage-M1) | repo `U:\Desktop\…\MNL\Data\processed\fr\pooled` | 1.33 GB |
| `interim/ruro/fr` (EUROMOD scenario outputs) | `Z:` superset (+ U: subset) | 3.21 GB |
| `Data/DE/` (German EUROMOD raw microdata) | U:/Z: | 0.14 GB |
| `Data/inspecting/` (audit + predrop parquets) | U: | 0.44 GB |
| loose raw/source files at `Data/` root | U:/Z: | — |

`Data/raw` (182 MB) and `Data/FR` (397 MB) were already present on C: and matched.

---

## 2. Decisions taken (confirmed with user)

1. **new_data + pooled → move under `C:\EUROMOD-STORAGE`** and update code so `pooled`
   resolves from `data_root()` instead of the repo working tree (no data in the repo).
2. **interim → migrate to `C:\EUROMOD-STORAGE\Data\interim\ruro\fr`** — note the new
   location is under `Data/` (not the old top-level `interim/`). Scripts updated to match.
3. **Legacy experiment dirs** (`RURO1`, `old_Data_results`, `old rep`, `boxcox_local`,
   `male_ascsON_q99`, `gamspy`) → cold-archive to `\\crc` once, then deletable.
4. **U:/Z: replica deletion → present exact list first, do not auto-delete.**
5. **EUROMOD system** (clarified by user): `EUROMOD_RELEASES_J1.0+` is the *old* model
   software (systems, not data). It was copied to C: by mistake and **deleted**. The
   current version is `Euromod_model\EUROMOD_RELEASES_J2.0+`, already on C:. The EUROMOD
   system is re-downloadable software and is **not** part of the data backup.

---

## 3. Migration executed (all non-destructive copies; 0 failed, 0 mismatch)

robocopy logs in the job dir (`mig_*.log`). Summary:

| Step | Source → Dest | Files | Size |
|---|---|---|---|
| bpool new_data | `U:\EUROMOD-STORAGE\new_data` → `C:\…\new_data` | 104 | 2.81 GB |
| pooled | repo `…\Data\processed\fr\pooled` → `C:\…\Data\processed\fr\pooled` | 23 | 1.33 GB |
| interim (Z superset) | `Z:\…\interim` → `C:\…\Data\interim` | 13 | 2.48 GB |
| interim (U top-up) | `U:\…\interim` → `C:\…\Data\interim` | 5 | 0.73 GB |
| Data additive top-up | `U:`+`Z:` `\Data` → `C:\…\Data` (`/XO`, no deletes) | 164 | DE, inspecting, loose files |
| outputs + reports | U:+Z: → C: | 591 | ~24 MB |

EUROMOD_RELEASES_J1.0+ was copied then **deleted** (see §2.5).

### Final canonical store: `C:\Users\hisham\MNL\EUROMOD-STORAGE`

```
EUROMOD-STORAGE/
├── Data/                         7.97 GB
│   ├── processed/fr/{2015,2016,2017,pooled}/
│   ├── raw/                      (EUROMOD raw microdata)
│   ├── FR/                       (FR microdata + DRD)
│   ├── DE/                       (DE microdata + DRD)
│   ├── interim/ruro/fr/          (EUROMOD scenario outputs — MOVED here)
│   └── inspecting/               (audit + predrop parquets)
├── new_data/                     2.81 GB   (bpool intermediates)
├── Euromod_model/                1.98 GB   (EUROMOD system J2.0+ — software, not backed up)
├── outputs/                      ~0.01 GB
└── reports/                      ~0.01 GB
```

---

## 4. Code changes (so scripts read from the new locations)

All verified with `py_compile`. No hardcoded paths introduced — everything resolves
via `path_helpers`.

| File | Change |
|---|---|
| `scripts/bpool/_bpool_paths.py` | `POOLED_DATA_DIR` now `data_root()/processed/fr/pooled` (was repo working tree) |
| `scripts/enhanced/enh_RURO_euromod.py` | default scenario dir → `…/Data/interim/ruro/<cc>/scenarios` |
| `scripts/RURO_euromod.py` | same interim relocation |
| `scripts/enhanced/quick_verify.py` | `EUROMOD_OUTPUT` → `data_root()/interim/…` |
| `scripts/RURO_draws.py` | help text updated to `Data/interim/…` default |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | `POOLED_DIR` → `data_root()/processed/fr/pooled` |
| `scripts/multi_year/m1_isf_check_2018.py` | `POOLED_DIR` + processed search → `data_root()` |
| `scripts/sync_backup.ps1` | new layout (Data, new_data, outputs, reports); reachability fix + auto-create backup root; EUROMOD system excluded; ASCII-only |
| `~/.mnl/config.yaml` (gitignored) | `euromod_root: …/Euromod_model/EUROMOD_RELEASES_J2.0+` |

Verified resolution:
```
storage_root: C:\Users\hisham\MNL\EUROMOD-STORAGE
data_root   : C:\Users\hisham\MNL\EUROMOD-STORAGE\Data
euromod_root: C:\Users\hisham\MNL\EUROMOD-STORAGE\Euromod_model\EUROMOD_RELEASES_J2.0+
backup_root : \\crc\users\hisham\MNL_backup
pooled      : C:\Users\hisham\MNL\EUROMOD-STORAGE\Data\processed\fr\pooled
```

---

## 5. Backup

`scripts/sync_backup.ps1` now mirrors the **data** (Data, new_data, outputs, reports)
to `\\crc\users\hisham\MNL_backup\EUROMOD-STORAGE`. The EUROMOD system (`Euromod_model`)
is re-downloadable software and is excluded. The script auto-creates the backup root
and no-ops if the `\\crc` share is unreachable. Legacy experiment dirs were cold-archived
to `\\crc\users\hisham\MNL_backup\_legacy_archive\`.

Run manually: `.\scripts\sync_backup.ps1` (add `-DryRun` to preview, `-All` for a full mirror).

---

## 6. Pending: U:/Z: replica deletion (NOT yet done)

Per the user's instruction, the exact deletion list is presented for sign-off before
anything is removed. Nothing on U: or Z: has been deleted by this session. The repo's
`Data/processed/fr/pooled` (now duplicated on C:) is also a candidate for removal.
See the deletion list presented in the session / handoff.
