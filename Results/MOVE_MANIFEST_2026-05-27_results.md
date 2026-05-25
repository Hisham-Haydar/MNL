# Move Manifest — 2026-05-27 Round 4 Results/ Track Restructure

## Context

- **Approver:** Hisham (2026-05-27 conversation)
- **Scope:** `Results/` reorganization. Reports (`.md`) only get track-organized; machine artifacts stay where code expects them; stale run-log CSVs archived.
- **Key difference from the docs rounds:** `Results/` is estimation **output**, and ~63 code/config sites reference `Results/` paths (read targets, write defaults, pipeline gates). So this round does NOT blindly mirror the docs layout — it moves the report `.md` files and leaves coupled machine artifacts in place.
- **Method:** `git mv` for tracked `.md` reports (history-preserving); filesystem move for git-ignored stale CSVs; targeted writer-script edits for spec-specific output paths; auto-mapped cross-reference patch.

## Decisions taken

1. **Scope:** reports track-split + archive stale non-coupled machine artifacts. Machine artifacts (`.json` results/inits, `.npy`, `.log`, latest CSV manifests, `pilot/`, `NC_pilot/diagnostic_estimation_v1/`, `_M0*_multistart_inits/`) stay at their code-expected locations.
2. **Coupled reports:** move + update the writer — but **only for spec-specific scripts**; reusable/country-agnostic writers are left unedited (see §C).
3. **Archive discipline:** dated archive subdir + this manifest + README.

## Target layout (reports)

```
Results/
├── P3a/
│   ├── single_year_baseline/{M0,M0a,M0b,M0c,M1}/   42 reports
│   ├── multi_year_stage_M1/                         18 reports
│   ├── pooled_P3a/                                  9 reports
│   └── gsurv2/                                      7 reports
├── NC_pilot/                                        24 reports (+ existing diagnostic_estimation_v1/ machine subdir)
├── _shared/                                         5 reports
├── figures/, pilot/, diagnostics/, _M0*_inits/      unchanged (machine)
├── archive/
│   ├── 2026-05-20_post_gsurv2_mnl_rebuild/          unchanged
│   └── 2026-05-27_results_stale_runs/               16 stale CSVs + README
└── <machine artifacts at root>                      _*.py, _*.json, *.npy, *.log, latest M1_*.csv
```

## Commit chain

| Phase | Commit | Description |
|---|---|---|
| B1 | `13cc677` | Move 23 single-year M0 ladder reports (M0/M0a/M0b/M0c) |
| B2 | `ad01b72` | Move 9 M1 baseline reports |
| B3 | `e4ebc4d` | Move 18 multi-year stage-M1 reports |
| B4 | `f443d34` | Move 9 pooled-P3a reports |
| B5 | `fce1ccc` | Move 7 GSURv2 reports |
| B6 | `bf02589` | Move 24 NC pilot reports |
| B7 | `aa206f5` | Move 5 shared/cross-cutting reports |
| C1 | `62f16ad` | Update 4 spec-specific writer output paths |
| C2 | `33eaba2` | Patch 139 inbound references to new report paths |
| D | this commit | Archive 16 stale CSVs + README + this manifest |

Total `.md` reports relocated: **95**.

## C. Writer-script handling (the code-coupling decision)

### C1 — spec-specific writers updated (commit `62f16ad`)

These scripts are France-GSUR / NC-pilot specific or the path is a CLI default, so hardcoding the new track path is safe:

| Script | Old output path | New output path |
|---|---|---|
| `scripts/enhanced/enh_RURO_mnl_rebuild_GSURv2_stageA.py` | `Results/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md` | `Results/P3a/gsurv2/...` |
| `scripts/pilot/_run_beta_l0_m_diagnostic.py` | `Results/JMP_NC_pilot_beta_l0_m_diagnostic_report_v1.md` | `Results/NC_pilot/...` |
| `scripts/pilot/_run_diagnostic_estimation_rerun.py` | `Results/JMP_NC_pilot_diagnostic_estimation_rerun_report_v1.md` | `Results/NC_pilot/...` |
| `scripts/enhanced/run_cluster_robust_se.py` | `--output` default `Results/RURO_cluster_robust_SE_static_validation_v1.md` | `Results/_shared/...` (+ usage example) |

### C2 — reusable/country-agnostic writers NOT edited (deliberate)

These scripts are part of the portable package surface; hardcoding France-P3a paths would undermine portability. The reports were moved into track subdirs, but the writers are left generic. **Run-command convention:** when these are re-run, pass the track path as the output destination.

| Report (now in track subdir) | Writer (left generic) | Run convention |
|---|---|---|
| `Results/P3a/multi_year_stage_M1/M1_identity_validation_summary.md` | `scripts/multi_year/m1_identity_validation.py` (uses `cfg.results_dir`) | summary should be written under the multi_year_stage_M1 subdir; writer keeps writing to `cfg.results_dir` root by default |
| `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_supplementary_diagnostics_v1.md` | `scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py` (`--output-dir` required) | pass `--output-dir Results/P3a/single_year_baseline/M1` |
| `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_supplementary_diagnostics_v1.md` | `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py` (`--output-dir`) | pass `--output-dir Results/P3a/single_year_baseline/M1` |

**Consequence to be aware of:** if one of these three is re-run with the *default/old* output dir, a fresh copy will land at `Results/` root (a re-run artifact, not a broken pipeline). Re-file it into the track subdir, or pass the track path on the command line.

### Gate path not affected

`Results/M1_ISF_tpr_comparability_check_2018.md` (the P3b gate in `config/multi_year/fr_p3a_stage_m1.yaml` and `m1_isf_check_2018.py`) does **not exist yet** and was **not moved**; the gate path is unchanged.

## D. Stale run-log CSVs archived (16)

Moved to `Results/archive/2026-05-27_results_stale_runs/` (filesystem move — these are git-ignored `*.csv`). Latest of each family kept at `Results/` root. Confirmed write-only (never code-read). See that dir's README for the per-family breakdown.

## What was deliberately NOT moved

- **Machine result/init JSONs** (`_M0*_multistart_inits/`, `_*.json`, `pilot/.../estimation_result*.json`, `NC_pilot/diagnostic_estimation_v1/`): code-read (warm starts, oracle theta). Left in place.
- **Diagnostic scripts** (`_*.py`) and their JSON outputs at root: paired toolkit artifacts; left in place.
- **`.npy` arrays, `.log` solver logs, `.tex` tables**: run artifacts; left in place.
- **`figures/`, `diagnostics/`**: unchanged.
- **Latest-per-family M1 CSVs**: kept at root where the pipeline expects the most recent manifest.

## Verification

```powershell
# 1. No .md reports left at Results/ root (all in tracks/_shared/archive)
Get-ChildItem Results -File -Filter '*.md' | Measure-Object   # expect 0

# 2. Per-track report counts
foreach ($t in 'P3a','NC_pilot','_shared') {
  "$t : " + (Get-ChildItem "Results/$t" -Recurse -File -Filter '*.md' | Measure-Object).Count
}

# 3. Git history preserved for a moved report
git log --follow --oneline -- Results/P3a/pooled_P3a/JMP_pooled_P3a_estimation_report_v2.md | Select-Object -First 5

# 4. No stale Results/<flat-report>.md refs in code (outside archive)
Get-ChildItem -Recurse -File -Include '*.py','*.yaml','*.yml','*.ps1' scripts, config |
  Select-String -Pattern 'Results[/\\](JMP_|RURO_occ_|RURO_GSUR_v2|RURO_cluster|RURO_ruro_occ_)' |
  Where-Object { $_.Line -notmatch 'P3a|NC_pilot|_shared|archive' } | Select-Object -First 10
# expect empty (only the 4 updated writers + comment refs, all now track-pathed)

# 5. Stale-run archive populated
Get-ChildItem Results/archive/2026-05-27_results_stale_runs -File   # 16 csv + README
```
