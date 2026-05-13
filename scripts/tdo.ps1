# =====================================================================
# RURO FR 2021 - FULL CLEAN PIPELINE
# =====================================================================

# # Paths
# $PROC = "U:/EUROMOD-STORAGE/Data/processed/fr/2021"
# $RAW  = "U:/EUROMOD-STORAGE/Data/raw/FR_2021_c2.txt"
# $SCEN = "U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios"

# Thread env for this session
$env:OMP_NUM_THREADS="32"
$env:MKL_NUM_THREADS="32"
$env:NUMEXPR_NUM_THREADS="32"

# $cmds = @(
#   # 1) Prep raw FR2021
#   "python.exe .\scripts\run_fr_2021_prep.py",

#   # 2) RURO prep (ready singles/couples)
#   "python scripts/RURO_prep.py --processed-dir `"$PROC`" --base-year 2021 --export-format parquet",

#   # 3) Generate draws
#   "python scripts/RURO_draws.py --singles-path `"$PROC/singles_RURO_ready.parquet`" --couples-path `"$PROC/couples_RURO_ready.parquet`" --n-draws 9 --wage-spec vw",

#   # 4) EUROMOD over draws (system set to 2020)
#   "python scripts/RURO_euromod.py --singles-draws `"$PROC/singles_RURO_ready_RURO_draws.parquet`" --couples-draws `"$PROC/couples_RURO_ready_RURO_draws.parquet`" --microdata-template `"$RAW`" --euromod-root `"U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+`" --euromod-system FR_2020 --euromod-dataset FR_2021_c2 --scenario-dir `"$SCEN`"",

#   # 5) Build MNL dataset
#   "python scripts/RURO_prep_mnl_basic.py --singles-draws `"$PROC/singles_RURO_ready_RURO_draws.parquet`" --couples-draws `"$PROC/couples_RURO_ready_RURO_draws.parquet`" --euromod-combined `"$SCEN/combined_draws_em.parquet`" --out-base `"$PROC/fr_2021_RURO_mnl`" --wage-spec vw",

#   # 6) Optional estimation (uses prior from full MNL)
#   "python scripts/RURO_boxcox_group_opportunities.py --data-path `"$PROC/fr_2021_RURO_mnl.parquet`" --t-hours 80 --c-ref mean --l-ref mean --num-threads 32 --pgtol 1e-8 --ftol 1e-12 --maxiter 5000 --model-name fr2021_ruro_boxcox_meanmean"
# )

# foreach ($c in $cmds) {
#   Write-Host ">>> $c" -ForegroundColor Cyan
#   Invoke-Expression $c
#   if ($LASTEXITCODE -ne 0) { Write-Host "Command failed, stopping." -ForegroundColor Red; break }
# }
