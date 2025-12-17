# Enhanced RURO France 2016 – Joint Estimation (side branch)
# -----------------------------------------------------------
# This script mirrors the base pipeline but swaps in the enhanced prep/estimation
# wrappers. The original scripts remain untouched.
#
# Steps (manual run recommended for clarity):
#   1) Prep MNL with enhanced wrapper (adds log_age, drgn1 dummies, meta JSON):
#        python .\scripts\enhancement\enh_RURO_prep_mnl_basic.py `
#          --singles-draws "$PROC\singles_RURO_ready_RURO_draws.parquet" `
#          --euromod-combined "$SCEN\combined_draws_em.parquet" `
#          --out-base "$PROC\fr_${YEAR}_RURO_mnl" `
#          --wage-spec $WAGE_SPEC `
#          --use-region-dummies `
#          --mean-dispy-norm 2500 --mean-lhw-norm 35
#        # add --couples-draws if available
#
#   2) Estimate with enhanced wrapper (richer spec, auto-normalization from meta):
#        python .\scripts\enhancement\enh_RURO_estimate_FR.py `
#          --mnl-file "$PROC\fr_${YEAR}_RURO_mnl.parquet" `
#          --joint --wage-spec $WAGE_SPEC `
#          --optimizer L-BFGS-B --maxiter 2000 `
#          --use-numba --n-jobs $CPU_CORES `
#          --post-estimation `
#          --out-file "$RESULTS_DIR\fr_${YEAR}_joint_ENH.json"
#
# Notes:
# - Normalization is auto-read from <mnl>_meta.json if flags are omitted.
# - Region dummies on by default; toggle with --use-region-dummies/--use-year-dummies.
# - Base pipeline (run_fr_2016_joint_only.ps1) stays unchanged.

param(
    [int]$YEAR = 2016,
    [string]$WAGE_SPEC = "vw",
    [int]$CPU_CORES = 8,
    [switch]$USE_SAMPLE_MNL,         # if true, look for <out-base>_sample.parquet (manual creation)
    [switch]$MAKE_SAMPLE_MNL,        # if set, create a sampled MNL parquet from the main MNL
    [double]$SAMPLE_FRACTION = 0.05  # fraction of households for the sample
)

$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$PROC = "U:\EUROMOD-STORAGE\Data\processed\fr\$YEAR"
$SCEN = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_$YEAR"
$RESULTS_DIR = "$PROJ_ROOT\outputs\estimates\fr\$YEAR"

Write-Host "Enhanced pipeline (side branch) - manual steps above." -ForegroundColor Cyan
Write-Host "Tip: set -USE_SAMPLE_MNL to point estimation at <out-base>_sample.parquet if you prepared one." -ForegroundColor DarkGray

# Convenience: derive MNL path and switch to sample if requested
$MNL_BASE = "$PROC\fr_${YEAR}_RURO_mnl"
$MNL_MAIN = "$MNL_BASE.parquet"
$MNL_SAMPLE = "${MNL_BASE}_sample.parquet"
$MNL_USE = $MNL_MAIN

# Optionally create a sampled MNL (household-level) for faster dry runs
if ($MAKE_SAMPLE_MNL) {
    Write-Host "Creating sampled MNL at $MNL_SAMPLE (fraction=$SAMPLE_FRACTION)..." -ForegroundColor Yellow
    $sampleCmd = @"
import pandas as pd
import numpy as np
src = r'$MNL_MAIN'
dst = r'$MNL_SAMPLE'
df = pd.read_parquet(src)
id_col = 'idhh' if 'idhh' in df.columns else ('idperson' if 'idperson' in df.columns else None)
if id_col is None:
    samp = df.sample(frac=$SAMPLE_FRACTION, random_state=1)
else:
    ids = df[id_col].dropna().unique()
    n_keep = max(1, int(len(ids)*$SAMPLE_FRACTION))
    keep_ids = pd.Series(ids).sample(n=n_keep, random_state=1).values
    samp = df[df[id_col].isin(keep_ids)].copy()
samp.to_parquet(dst, index=False)
print(f'Sampled MNL rows: {len(samp)}')
"@
    python - <<EOF
$sampleCmd
EOF
}

if ($USE_SAMPLE_MNL -and (Test-Path $MNL_SAMPLE)) {
    $MNL_USE = $MNL_SAMPLE
    Write-Host "Using sample MNL: $MNL_USE" -ForegroundColor Yellow
}
