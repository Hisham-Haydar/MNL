# France Case Outputs — 2026-05-26 Migration Record

**Date:** 2026-05-26  
**Scope:** Developer-layer documentation of France-case output paths after migration

---

## Current output locations (developer machine)

| Directory | Path |
|---|---|
| Estimation outputs (active) | `C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs\` |
| Reports / LLM summaries | `C:\Users\hisham\MNL\EUROMOD-STORAGE\reports\` |
| Backup (post-run sync) | `\\crc\users\hisham\MNL_backup\EUROMOD-STORAGE\outputs\` |
| Backup reports | `\\crc\users\hisham\MNL_backup\EUROMOD-STORAGE\reports\` |

Both are synced automatically by `scripts/sync_backup.ps1` after estimation runs. The backup
destinations are created by robocopy if they do not exist.

**Config:** `C:\Users\hisham\.mnl\config.yaml`:
```yaml
outputs_root: C:/Users/hisham/MNL/EUROMOD-STORAGE/outputs
reports_root: C:/Users/hisham/MNL/EUROMOD-STORAGE/reports
```

---

## Subfolder map of outputs/ (5,603 items as of 2026-05-26)

```
outputs/
├── diagnostics/
│   └── loc_by_dehde/           ← LOC-by-DEHDE distribution PNGs
├── estimates/
│   └── fr/
│       ├── 2016/               ← early single-year scipy/GAMSPy runs
│       ├── phase2/             ← Phase 2 GAMSPy spec tests
│       ├── spec_tests/         ← spec comparison (SciPy vs GAMSPy)
│       └── spec/
│           ├── job_choice/     ← M2c job-choice model (NC pilot)
│           ├── ruro_occ_M0*/   ← M0-series spec runs
│           ├── ruro_occ_M1_clean/     ← M1 clean verdict run (2026-05-18)
│           └── ruro_occ_P3a_pooled/   ← P3a three-start pooled (2026-05-21+)
├── logs/                        ← per-run log files
└── post_estimation/
    └── fr/
        └── 2016/
            └── joint/          ← HTML diagnostics from early runs
```

---

## Which scripts write to which subfolders

| Script | Output subpath |
|---|---|
| `RURO_estimate_FR.py` | `outputs_root() / "estimates/fr"` (fallback when no `--out-file`) |
| `enhanced/enh_RURO_estimate_FR.py` | `outputs_root() / "estimates/{country}/{spec}"` via `--output-dir` |
| `RURO_post_estimation.py` | `outputs_root() / "post_estimation"` |
| `enhanced/RURO_post_estimation_styled.py` | alongside `estimation_results.json` parent |
| `enhanced/RURO_post_estimation_styled.py` (reports) | `reports_root()` (LLM summary `.md`) |
| `run_post_estimation_standalone.py` | `outputs_root() / "post_estimation/fr/2016/joint"` |
| `generate_html_report.py` | `outputs_root() / "post_estimation/fr/2016/joint"` |
| `extract_excel_text.py` | `outputs_root()` directly |
| `Job_model/plot_loc_by_dehde.py` | user-supplied `--output-dir` (required arg) |
| `diagnostics/compare_scipy_gamspy.py` | reads from `outputs_root() / "estimates/fr/..."` |
| `diagnostics/test_gamspy_vs_scipy.py` | reads/writes `outputs_root() / "estimates/fr/..."` |
| `maintenance/run_pooled_P3a_estimation.py` | `outputs_root() / "estimates/fr/spec/ruro_occ_P3a_pooled"` |

---

## How to verify outputs are being written to the correct location

```powershell
# 1. Verify path_helpers resolves correctly
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" -c "
import sys; sys.path.insert(0, r'U:\Desktop\Nizam_Hisham\MNL\scripts')
from path_helpers import outputs_root, reports_root
print('outputs:', outputs_root())
print('reports:', reports_root())
"

# 2. After a run, check the most recent subdirectory
Get-ChildItem "C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs\estimates" -Recurse -Filter "estimation_results.json" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 5 FullName, LastWriteTime

# 3. Run the backup sync and verify
.\scripts\sync_backup.ps1 -DryRun
```

---

## What KEEP_RESULTS.md points to and why it stays in git

`outputs/KEEP_RESULTS.md` (at `U:\Desktop\Nizam_Hisham\MNL\outputs\KEEP_RESULTS.md`) is a
single tracked file whose only purpose is to help anyone browsing `outputs/` find the
authoritative results registry:

```markdown
# Output Runs to Keep

The project-level active results registry is:
docs/estimation/RURO_ACTIVE_RESULTS_REGISTRY.md
```

It is kept in git (via `!outputs/KEEP_RESULTS.md` in `.gitignore`) so that collaborators
cloning the repo get a pointer file even though the actual outputs are not committed.
The physical `outputs/` directory in the repo may be empty or contain only this file.

---

## Physical migration performed 2026-05-26

Source → Destination (robocopy /E /COPY:DAT):

| Source (U: repo) | Destination (C: storage) | Files |
|---|---|---|
| `U:\...\MNL\outputs\` | `C:\...\EUROMOD-STORAGE\outputs\` | ~5,606 |
| `U:\...\MNL\reports\` | `C:\...\EUROMOD-STORAGE\reports\` | 21 markdown + 346 existing |

The 21 markdown LLM summary files were removed from git tracking (`git rm -r reports/`).
The `.gitignore` whitelist (`!reports/`, `!reports/**`) was removed; `reports/` is now
fully ignored in the repo.
