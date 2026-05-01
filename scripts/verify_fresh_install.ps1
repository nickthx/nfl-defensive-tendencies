# Fresh-venv reproducibility check (SHIP-02), Windows.
# Same contract as scripts/verify_fresh_install.sh.
#
# Usage:
#   pwsh -File scripts\verify_fresh_install.ps1
#
# Notes:
# - Creates `.venv-fresh\` at repo root; deletes any existing one first so the
#   "fresh" claim holds. Does NOT touch the developer's `.venv\`.
# - Uses the two-step nfl_data_py install pattern (PROJECT.md Key Decisions):
#     pip install (all requirements except nfl_data_py line)
#     pip install nfl_data_py==0.3.3 --no-deps appdirs fastparquet
#   The first pass installs transitive deps with the strict pandas>=2.1,<2.3
#   constraint; the second installs nfl_data_py without re-resolving its
#   declared pandas<2.0 metadata conflict.
# - Requires `py -3.11` (the standard Windows Python launcher; PROJECT.md Key
#   Decisions locks this dispatch because system `python` resolves to 3.14 on
#   Windows 11).
# - .venv-fresh\ is gitignored; it is left in place after the run for inspection.

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $RepoRoot

$VenvDir = Join-Path $RepoRoot '.venv-fresh'
$Start = Get-Date

Write-Host "==> Removing any existing fresh-venv at $VenvDir"
if (Test-Path $VenvDir) { Remove-Item -Recurse -Force $VenvDir }

Write-Host "==> Creating Python 3.11 venv at $VenvDir"
& py -3.11 -m venv $VenvDir

$Activate = Join-Path $VenvDir 'Scripts\Activate.ps1'
& $Activate

Write-Host "==> Upgrading pip"
python -m pip install --upgrade pip

Write-Host "==> Installing requirements.txt (excluding nfl_data_py for now)"
$tmp = New-TemporaryFile
Get-Content requirements.txt | Where-Object { $_ -notmatch '^nfl_data_py' } | Set-Content $tmp
pip install -r $tmp
Remove-Item $tmp

Write-Host "==> Installing nfl_data_py==0.3.3 with --no-deps + companions"
pip install --no-deps nfl_data_py==0.3.3 'appdirs>=1' 'fastparquet>=0.5'

Write-Host "==> Verifying core imports"
python -c "import nfl_data_py; import pandas; import numpy; import scipy; import matplotlib; import seaborn; import jupytext; import nbconvert; print('imports OK')"

Write-Host "==> Running ETL: python -m etl.run"
python -m etl.run

Write-Host "==> Executing notebooks end-to-end"
foreach ($nb in @(
    'analysis\01_exploratory.ipynb',
    'analysis\02_predictability_modeling.ipynb',
    'analysis\03_visualizations.ipynb'
)) {
    Write-Host "    --> $nb"
    jupyter nbconvert --to notebook --execute --inplace $nb
}

Write-Host "==> Clearing notebook outputs"
foreach ($nb in @(
    'analysis\01_exploratory.ipynb',
    'analysis\02_predictability_modeling.ipynb',
    'analysis\03_visualizations.ipynb'
)) {
    jupyter nbconvert --clear-output --inplace $nb
}

$End = Get-Date
$Elapsed = ($End - $Start).TotalSeconds
Write-Host ("==> Fresh-install reproducibility check PASSED in {0:N0}s" -f $Elapsed)
Write-Host ("    Reproducibility budget: 600s (10 min). Observed: {0:N0}s." -f $Elapsed)
if ($Elapsed -gt 600) {
    Write-Host 'WARNING: exceeded 10-minute reproducibility budget'
    exit 1
}
