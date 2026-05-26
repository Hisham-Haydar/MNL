# RURO Output Path Design

**Date:** 2026-05-26  
**Scope:** Package-layer specification for `outputs_root()` and `reports_root()`

---

## Why outputs live outside the repo

The repo is shared, version-controlled code. Estimation outputs are large, run-specific, and
machine-generated — they do not belong in git. Keeping outputs in the repo:

- Bloats git history (JSON/HTML/numpy files, some multi-MB)
- Creates merge conflicts when two runs happen on the same branch
- Breaks portability: a colleague cloning the repo gets an empty `outputs/` folder anyway
- Prevents clean diffs: script changes are drowned out by JSON noise

Outputs and reports are therefore written to **EUROMOD-STORAGE** (the same external store used
for processed parquets and raw microdata). EUROMOD-STORAGE is configured per-machine via
`~/.mnl/config.yaml` and synced to `\\crc\...` post-run by `sync_backup.ps1`.

---

## Resolution order for `outputs_root()`

```
1. ~/.mnl/config.yaml  key: outputs_root
2. MNL_OUTPUTS_ROOT    environment variable
3. storage_root() / "outputs"   (auto-derived fallback)
```

Resolution order for `reports_root()`:

```
1. ~/.mnl/config.yaml  key: reports_root
2. MNL_REPORTS_ROOT    environment variable
3. storage_root() / "reports"   (auto-derived fallback)
```

Both functions are `@lru_cache(maxsize=1)` — resolution runs once per process and is free
on every subsequent call.

---

## User configuration

The canonical user config file is `~/.mnl/config.yaml`. Example:

```yaml
storage_root:  C:/Users/jdoe/MNL/EUROMOD-STORAGE
outputs_root:  C:/Users/jdoe/MNL/EUROMOD-STORAGE/outputs   # optional override
reports_root:  C:/Users/jdoe/MNL/EUROMOD-STORAGE/reports   # optional override
backup_root:   //server/share/MNL_backup
```

If `outputs_root` and `reports_root` are not set, they default to subdirectories of
`storage_root`. Most users do not need to set them explicitly.

This file is **gitignored** and **machine-specific**. Users create it once (future `mnl-setup`
entry point or manually). See `RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` for the full
config schema.

---

## `--output-dir` CLI override convention

Any script that writes estimation outputs must:

1. Accept `--output-dir` (or equivalent) as a CLI argument
2. Default the argument to `None`
3. Resolve after `parse_args()`:

```python
if args.output_dir is None:
    args.output_dir = outputs_root() / "estimates" / country / str(year)
```

**Never remove `--output-dir` from a script.** The user override must always work so that
individual runs can be directed to a custom path (e.g., a scratch directory on a compute node).

---

## Expected subfolder structure under outputs/

```
outputs/
├── estimates/
│   └── fr/
│       ├── 2016/                        ← single-year canonical run
│       └── spec/                        ← spec-driven runs
│           ├── ruro_occ_M1_clean/
│           │   └── gamspy/
│           │       └── run_YYYY-MM-DD_HH-MM-SS/
│           │           ├── estimation_results.json
│           │           └── post_estimation/
│           └── ruro_occ_P3a_pooled/
│               └── gamspy/
│                   └── start_1/
│                       └── run_YYYY-MM-DD_HH-MM-SS/
│                           └── estimation_results.json
├── post_estimation/
│   └── fr/
│       └── 2016/
│           └── joint/
│               └── fr_2016_joint_diagnostics.html
└── diagnostics/
    └── loc_by_dehde/
        └── *.png
```

---

## Expected subfolder structure under reports/

```
reports/
├── gamspy/                    ← GAMSPy solver analysis HTML reports
│   └── boxcox/
├── mle_dcm/                   ← MLE DCM reports
├── oracle/                    ← JAX/oracle benchmark reports
└── *.md                       ← compact LLM summaries (written by RURO_post_estimation_styled.py)
```

---

## See also

- `RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md` — full storage architecture
- `RURO_PATH_MIGRATION_HANDOFF.md` — all migrations performed on 2026-05-26
- `OUTPUTS_FRANCE_CASE_2026-05-26.md` — developer-layer details (exact paths, script map)
- `PROMPT_outputs_migration_2026-05-26.md` — the prompt that produced this state
