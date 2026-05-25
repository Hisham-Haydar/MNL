# 2026-05-27 — Results stale run-log archive

This subdirectory holds **superseded timestamped run-log CSVs** moved out of `Results/` root during the 2026-05-27 Results reorganization (Round 4).

## What's here

16 stale Stage-M1 validation manifests. Each `m1_*.py` script writes a fresh `<name>_<UTC-timestamp>.csv` to `results_dir` on every run (never overwriting, never read back), so older timestamps accumulate as pure run-logs. Only the latest of each family was kept at `Results/` root; the earlier runs are archived here.

| Family | Archived (older runs) | Kept at root (latest) |
|---|---:|---|
| `M1_stacked_id_manifest` | 6 | `..._20260520_223909.csv` |
| `M1_validation_summary` | 3 | `..._20260520_223909.csv` |
| `M1_raw_id_preservation_check` | 3 | `..._20260520_223909.csv` |
| `M1_cluster_key_check` | 2 | `..._20260520_223716.csv` |
| `M1_cpi_harmonisation_check` | 2 | `..._20260520_223658.csv` |

## Notes

- These CSVs are git-ignored (`*.csv` in `.gitignore`), so they were never tracked; this archive is a working-tree declutter, not a git history change.
- No code reads these files — confirmed: the `m1_*.py` writers only *write* timestamped manifests (`scripts/multi_year/m1_stack_years.py`, `m1_validate.py`, `m1_add_cluster_key.py`, `m1_harmonise_cpi.py`). A future Stage-M1 run will write fresh manifests to `results_dir` root, unaffected by this archive.
- Provenance: `Results/MOVE_MANIFEST_2026-05-27_results.md`.
