# One-time Windows setup. Run in PowerShell. Safe to re-run.
winget install -e --id Git.Git
winget install -e --id Python.Python.3.12
winget install -e --id OpenJS.NodeJS.LTS
Set-Location (Join-Path $PSScriptRoot "..")
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tools\requirements.txt
git init 2>$null
Write-Host "Done. Open this folder in VS Code and install the recommended extensions."
