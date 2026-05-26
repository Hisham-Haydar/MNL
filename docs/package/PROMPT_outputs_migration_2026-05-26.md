# Task: Move outputs/ to external storage and make output paths configurable

## Working directory
Repo root: U:\Desktop\Nizam_Hisham\MNL
All relative paths are relative to this root.

## Goal
Same as the previous data relocation work, but now for repo outputs and reports.
The package must not depend on repo-local output paths. Users must be able to
configure output locations.

## Read first
- docs/package/RURO_PATH_MIGRATION_HANDOFF.md
- docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md
- src/mnl/config.py or the current path_helpers.py location
- docs/package/RURO_DATA_CONSOLIDATION_2026-05-26.md

## Step 1 — Audit first, then proceed
Find every place where output/report paths are:
- hardcoded absolute paths
- repo-relative paths like `./outputs`, `outputs/...`, or `Path(...)/"outputs"`
- default CLI output paths inside the repo

Show the file and line number list before editing. Then proceed unless there
is a blocker.
If matches are found under `scripts/archive/`, report them but do not modify
those files.

## Step 2 — Add configurable path helpers
Add `outputs_root()` and `reports_root()` to path_helpers.py following the
exact same style as the existing `storage_root()` helper.

Resolution order for `outputs_root()`:
1. `~/.mnl/config.yaml` key: `outputs_root`
2. `MNL_OUTPUTS_ROOT` environment variable
3. `storage_root() / "outputs"` (auto-derived fallback)
4. Clear `FileNotFoundError` with setup instructions if unresolved

Resolution order for `reports_root()`:
1. `~/.mnl/config.yaml` key: `reports_root`
2. `MNL_REPORTS_ROOT` environment variable
3. `storage_root() / "reports"` (auto-derived fallback)
4. Clear `FileNotFoundError` with setup instructions if unresolved

Do not hardcode any user-specific path in package code or reusable scripts.

## Step 3 — Move physical outputs
Create:
  C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs

Move contents of the current repo `outputs/` folder there, preserving all
subfolders and files.
Do not delete source files until verifying file counts match between source
and destination.

If repo `reports/` exists, move it to:
  C:\Users\hisham\MNL\EUROMOD-STORAGE\reports
If it does not exist, create the folder and configure it as the reports root.

## Step 4 — Update local config
Update C:\Users\hisham\.mnl\config.yaml and add:

```yaml
outputs_root: C:/Users/hisham/MNL/EUROMOD-STORAGE/outputs
reports_root: C:/Users/hisham/MNL/EUROMOD-STORAGE/reports
```

## Step 5 — Patch all scripts
Replace every hardcoded or repo-relative output path found in Step 1 with
calls to outputs_root() or reports_root() from path_helpers.

For any script that accepts --output-dir as a CLI argument:
- Keep the argument exactly as-is
- Change only the default value to outputs_root() / [relevant subpath]
- Never remove --output-dir — the user override must always work

## Step 6 — Extend backup sync
Update the backup sync script so that outputs/ and reports/ under
EUROMOD-STORAGE are synced to:
  \\crc\users\hisham\MNL_backup\EUROMOD-STORAGE\
Following the same pattern already used for Data/.

## Step 7 — Update .gitignore
Ensure outputs/ and reports/ are excluded from git tracking.
Exception: outputs/KEEP_RESULTS.md must remain tracked — it is the
results registry pointer and belongs in git.

## Step 8 — Document on two layers

Layer 1 — Package documentation:
Write docs/package/RURO_OUTPUT_PATH_DESIGN.md covering:
- Why outputs live outside the repo
- How outputs_root() and reports_root() resolve
- How any user configures their output location via config or env var
- The --output-dir CLI override pattern
- Expected subfolder structure under outputs/

Layer 2 — France case / current developer:
Write docs/France_case/OUTPUTS_FRANCE_CASE_2026-05-26.md covering:
- Exact current paths on developer machine
- Exact current paths on \\crc backup
- Subfolder map of what is currently in outputs/
- Which scripts write to which subfolders
- How to verify outputs are being written to the correct location
- What KEEP_RESULTS.md points to and why it stays in git

## Step 9 — Save this prompt to the repo
Save this prompt as:
  docs/package/PROMPT_outputs_migration_2026-05-26.md
So any future agent can see exactly what instruction produced the current state.

## Step 10 — Stage and commit
git add all changed files
git commit -m "feat: move outputs to external storage, add outputs_root() to path_helpers

- outputs/ moved to C:/Users/hisham/MNL/EUROMOD-STORAGE/outputs/
- reports/ moved to C:/Users/hisham/MNL/EUROMOD-STORAGE/reports/
- path_helpers.py: added outputs_root() and reports_root()
- all active scripts: output paths resolve via outputs_root()
- ~/.mnl/config.yaml: outputs_root and reports_root keys added
- backup sync extended to cover outputs/ and reports/
- .gitignore updated (KEEP_RESULTS.md kept tracked)
- docs: RURO_OUTPUT_PATH_DESIGN.md (package layer)
- docs: OUTPUTS_FRANCE_CASE_2026-05-26.md (France case layer)
- docs: PROMPT_outputs_migration_2026-05-26.md (prompt record)"

## Hard constraints
- No hardcoded paths anywhere in package code or active scripts
- Do not remove --output-dir from any CLI script
- Do not delete source files before destination is verified
- outputs/KEEP_RESULTS.md must stay tracked in git
- .claude/settings.local.json must NOT be committed
- scripts/archive/ must NOT be modified
