# Run Styled Post-Estimation Analysis for GAMSPY Results
# This generates a beautiful HTML report with all diagnostics

python scripts\enhanced\RURO_post_estimation_styled.py `
    --results-json outputs\estimates\fr\2016_gamspy\run_2026-01-16_20-22-31\estimation_results.json `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\post_estimation\fr\2016_gamspy_styled `
    --prefix fr_2016_gamspy_ `
    --compute-se
