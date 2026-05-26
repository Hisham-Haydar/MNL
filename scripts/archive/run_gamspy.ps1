# Save as run_gamspy.ps1 or paste directly into PowerShell from repo root
$DATA   = "\\users\users\hisham\EUROMOD-STORAGE\Data\processed\scenarios\DE_2014_2016_cpi2015"
$OUT    = "\\users\users\hisham\EUROMOD-STORAGE\reports\gamspy\boxcox\DE_2014_2016_panel"
$SOLVER = "knitro"   # or ipopth / conopt

$cmds = @(
  # ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --genders female --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER",
  # ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --genders female --include-ascs --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER",
  # ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --genders male --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER",
  # ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --genders male --include-ascs --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER",
  ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --pooled --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER",
  ".\.venv\Scripts\python.exe scripts\DCM2_gamspy.py --pooled --include-ascs --data-dir `"$DATA`" --output-dir `"$OUT`" --solver $SOLVER"
)

foreach ($c in $cmds) {
  Write-Host ">>> $c" -ForegroundColor Cyan
  Invoke-Expression $c
  if ($LASTEXITCODE -ne 0) { Write-Host "Command failed, stopping." -ForegroundColor Red; break }
}
