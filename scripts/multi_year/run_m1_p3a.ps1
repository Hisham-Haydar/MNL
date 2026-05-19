# run_m1_p3a.ps1
# ==============
# FRANCE P3a RESEARCH ORCHESTRATION WRAPPER
# ------------------------------------------
# This script is intentionally France-P3a-specific. It hard-codes France
# EUROMOD paths, step labels, and the P3a year set (2015+2016+2017). It is
# NOT a reusable Stage M1 runner and does NOT accept --stage-config. A
# country-agnostic orchestration wrapper would read all paths and steps from
# a YAML and is a separate future task.
#
# Stage M1 — ordered execution sequence for P3a (2015+2016+2017).
#
# Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §18 (Orchestration).
#
# This script documents and optionally runs each Stage M1 step in the correct
# order.  Steps marked [MANUAL] require action outside this script.
# Steps marked [SCRIPT] are automated by the Stage M1 Python scripts.
#
# Authorization: Stage M1 implementation scaffolding only.
# NOT authorised in this script:
#   - Pooled estimation
#   - Welfare computation
#   - Canonical MNL promotion
#   - P3b activation (requires ISF check)
#
# Usage:
#   .\scripts\multi_year\run_m1_p3a.ps1 [-DryRun] [-StepFrom 6]
#
# Parameters:
#   -DryRun    : Pass --dry-run to all Python scripts; no files written.
#   -StepFrom  : Start execution from step N (1–10); default = 1.
#   -StepTo    : Stop after step N (1–10); default = 10.
# ---------------------------------------------------------------------------

param(
    [switch]$DryRun,
    [int]$StepFrom = 1,
    [int]$StepTo = 10
)

$ErrorActionPreference = "Stop"
$REPO = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PYTHON = "$REPO\.venv\Scripts\python.exe"
$DRY = if ($DryRun) { "--dry-run" } else { "" }

function Step-Banner {
    param([int]$N, [string]$Label, [string]$Type)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  Step $N — [$Type] $Label" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Require-Step {
    param([int]$N)
    return ($N -ge $StepFrom -and $N -le $StepTo)
}

# ---------------------------------------------------------------------------
# STEP 1 — [MANUAL] Acquire Eurostat denominators and INSEE benchmark
# ---------------------------------------------------------------------------
if (Require-Step 1) {
    Step-Banner 1 "Acquire Eurostat denominators and INSEE benchmark" "MANUAL"
    Write-Host @"

TODO (manual data acquisition):

1a. Download lfst_r_lfsd2pop (working-age population denominators) for 2015-2017:
    Eurostat API: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/
                  lfst_r_lfsd2pop?startPeriod=2015&endPeriod=2017&geo=FR*
    Save to: Data/external/lfst_r_lfsd2pop_2015_2017_full.csv

1b. Download lfst_r_lfp2acedu (labour force participation denominators) for 2015-2017:
    Same Eurostat API endpoint pattern.
    Save to: Data/external/lfst_r_lfp2acedu_2015_2017_full.csv

1c. Retrieve INSEE BDM series 001688526 for 2015 and 2017 annual average:
    BDM endpoint: https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526
    Extract annual averages for 2015 and 2017.
    Save to: Data/external/insee_001688526_2015_2017.csv

References: §15 of Stage M1 plan.
"@
    Write-Host "Press Enter to confirm Step 1 is complete, or Ctrl+C to abort..." -ForegroundColor Yellow
    if (-not $DryRun) { Read-Host }
}

# ---------------------------------------------------------------------------
# STEP 2 — [MANUAL] CPI source decision and write harmonisation CSV
# ---------------------------------------------------------------------------
if (Require-Step 2) {
    Step-Banner 2 "CPI source decision — write cpi_hicp_fr_harmonisation.csv" "MANUAL"
    Write-Host @"

TODO (§7 decision required):

2a. Make the CPI source decision:
    Option A: Retrieve INSEE domestic CPI (IPC, all-items, metropolitan France,
              base 2015=100) — PREFERRED if readily available.
    Option B: Formally adopt EUROMOD HICP from HICPCONFIG.xml (Eurostat/AMECO,
              base 2015=100) with documented φ_t factors:
                year 2015: φ_t = 1.0031
                year 2016: φ_t = 1.0000 (base year)
                year 2017: φ_t = 0.9886
                year 2018: φ_t = 0.9682 (if P3b later activated)

2b. Fill in Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv
    and save as Data/external/cpi_hicp_fr_harmonisation.csv.
    Do NOT hard-code phi_t values in any script; they must come from this CSV.

Template location: Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv
Output required:  Data/external/cpi_hicp_fr_harmonisation.csv

IMPORTANT: Do NOT create the final CSV until the §7 decision is documented.
           Running m1_harmonise_cpi.py without this file will abort with a clear error.
"@
    Write-Host "Press Enter to confirm Step 2 is complete, or Ctrl+C to abort..." -ForegroundColor Yellow
    if (-not $DryRun) { Read-Host }
}

# ---------------------------------------------------------------------------
# STEP 3 — [MANUAL] Run EUROMOD for FR_2015, FR_2016, FR_2017
# ---------------------------------------------------------------------------
if (Require-Step 3) {
    Step-Banner 3 "Run EUROMOD for FR_2015, FR_2016, FR_2017" "MANUAL"
    Write-Host @"

TODO (manual EUROMOD UI steps — cannot be automated):

3a. Open EUROMOD J1.0+ at: Z:\Hisham\EUROMOD-STORAGE\
3b. Run FR_2015 system. Output to: Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\
3c. Run FR_2016 system (multi-year run — may differ from existing 2016 output).
    Output to: Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\
3d. Run FR_2017 system. Output to: Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\

Note: The existing 2016 canonical output at
      Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm
      should NOT be overwritten. Use a separate output directory for multi-year runs.

References: §3 (Inputs table) of Stage M1 plan.
"@
    Write-Host "Press Enter to confirm Step 3 is complete, or Ctrl+C to abort..." -ForegroundColor Yellow
    if (-not $DryRun) { Read-Host }
}

# ---------------------------------------------------------------------------
# STEP 4 — [MANUAL] Run enh_RURO_prep_mnl_basic.py for 2015 and 2017
# ---------------------------------------------------------------------------
if (Require-Step 4) {
    Step-Banner 4 "Run enh_RURO_prep_mnl_basic.py for 2015 and 2017" "MANUAL"
    Write-Host @"

TODO (must be run after EUROMOD output and draws are available):

4a. For 2015:
    $PYTHON scripts/enhanced/enh_RURO_prep_mnl_basic.py ``
        --singles-draws <path_to_2015_singles_draws.parquet> ``
        --euromod-combined <path_to_2015_combined_draws_em.parquet> ``
        --out-base Data/processed/fr/fr_2015_RURO_mnl_job_gmm ``
        --gsur-file Data/external/FR_gsur_ruro.parquet ``
        --year 2015 ``
        --write-combined

4b. For 2017 (same pattern with 2017 paths):
    $PYTHON scripts/enhanced/enh_RURO_prep_mnl_basic.py ``
        --singles-draws <path_to_2017_singles_draws.parquet> ``
        --euromod-combined <path_to_2017_combined_draws_em.parquet> ``
        --out-base Data/processed/fr/fr_2017_RURO_mnl_job_gmm ``
        --gsur-file Data/external/FR_gsur_ruro.parquet ``
        --year 2017 ``
        --write-combined

Note: The --year argument is metadata-only; all paths are explicit CLI arguments.
      No changes to sample logic, utility variables, or alternatives.
      See: scripts/enhanced/enh_RURO_prep_mnl_basic.py --help

References: §18 (Modified scripts) of Stage M1 plan.
"@
    Write-Host "Press Enter to confirm Step 4 is complete, or Ctrl+C to abort..." -ForegroundColor Yellow
    if (-not $DryRun) { Read-Host }
}

# ---------------------------------------------------------------------------
# STEP 5 — [MANUAL] Run enh_prepare_FR_gsur_v2.py for 2015 and 2017
# ---------------------------------------------------------------------------
if (Require-Step 5) {
    Step-Banner 5 "Run enh_prepare_FR_gsur_v2.py for 2015 and 2017" "MANUAL"
    Write-Host @"

TODO (requires Eurostat denominator files from Step 1):

NOTE: enh_prepare_FR_gsur_v2.py currently has YEAR = 2016 hard-coded at
      line 44.  Year parameterization is audited but NOT implemented in
      Stage M1 scaffolding.  See docs/ GSURv2 year-parameterization audit note.

      Before running for 2015/2017, the --year CLI argument must be added
      to scripts/enhanced/enh_prepare_FR_gsur_v2.py (a separate Stage M2
      task).  This step is therefore DEFERRED until GSURv2 year
      parameterization is implemented.

Current GSUR coverage:
    FR_gsur_ruro.parquet       covers 2015, 2016, 2017, 2018 (v1, broad age)
    FR_gsur_ruro_v2_stageA.parquet  covers 2016 only (v2)

Stage M1 stacking can proceed using FR_gsur_ruro.parquet (v1) as the GSUR
source for 2015 and 2017 rows.  The merge is performed in the prep script,
not in the stacking scripts.

References: §15 (GSURv2 year-parameterization), §20 (What not to change).
"@
}

# ---------------------------------------------------------------------------
# STEP 6 — [SCRIPT] m1_stack_years.py --config p3a
# ---------------------------------------------------------------------------
if (Require-Step 6) {
    Step-Banner 6 "m1_stack_years.py --config p3a" "SCRIPT"
    $cmd = "$PYTHON scripts/multi_year/m1_stack_years.py --config p3a $DRY"
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step 6 failed (exit $LASTEXITCODE). Aborting."
        exit 1
    }
    Write-Host "Step 6 complete." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# STEP 7 — [SCRIPT] m1_identity_validation.py --config p3a
# ---------------------------------------------------------------------------
if (Require-Step 7) {
    Step-Banner 7 "m1_identity_validation.py --config p3a" "SCRIPT"
    $cmd = "$PYTHON scripts/multi_year/m1_identity_validation.py --config p3a"
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step 7 BLOCKED — identity validation failed. See Results/M1_identity_validation_summary.md"
        exit 1
    }
    Write-Host "Step 7 complete." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# STEP 8 — [SCRIPT] m1_harmonise_cpi.py --config p3a
# ---------------------------------------------------------------------------
if (Require-Step 8) {
    Step-Banner 8 "m1_harmonise_cpi.py --config p3a" "SCRIPT"
    $cmd = "$PYTHON scripts/multi_year/m1_harmonise_cpi.py --config p3a $DRY"
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step 8 failed (exit $LASTEXITCODE). Aborting."
        exit 1
    }
    Write-Host "Step 8 complete." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# STEP 9 — [SCRIPT] m1_add_cluster_key.py --config p3a
# ---------------------------------------------------------------------------
if (Require-Step 9) {
    Step-Banner 9 "m1_add_cluster_key.py --config p3a" "SCRIPT"
    $cmd = "$PYTHON scripts/multi_year/m1_add_cluster_key.py --config p3a $DRY"
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step 9 failed (exit $LASTEXITCODE). Aborting."
        exit 1
    }
    Write-Host "Step 9 complete." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# STEP 10 — [SCRIPT] m1_validate.py --config p3a
# ---------------------------------------------------------------------------
if (Require-Step 10) {
    Step-Banner 10 "m1_validate.py --config p3a" "SCRIPT"
    $cmd = "$PYTHON scripts/multi_year/m1_validate.py --config p3a"
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step 10 FAILED — validation did not pass. See Results/M1_validation_summary_*.csv"
        exit 1
    }
    Write-Host "Step 10 complete — Stage M1 P3a DONE." -ForegroundColor Green
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  Stage M1 P3a run complete." -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "Expected outputs (Data/processed/fr/pooled/):"
Write-Host "  fr_p3a_stacked_raw.parquet"
Write-Host "  fr_p3a_harmonised.parquet   (with cluster_id, *_real columns)"
Write-Host ""
Write-Host "Expected results (Results/):"
Write-Host "  M1_stacked_id_manifest_*.csv"
Write-Host "  M1_raw_id_preservation_check_*.csv"
Write-Host "  M1_cluster_key_check_*.csv"
Write-Host "  M1_cpi_harmonisation_check_*.csv"
Write-Host "  M1_identity_validation_summary.md"
Write-Host "  M1_validation_summary_*.csv"
Write-Host ""
Write-Host "NOT produced (as intended):"
Write-Host "  - No pooled estimation output"
Write-Host "  - No welfare output"
Write-Host "  - No P3b parquet (blocked until ISF check)"