# One command check: lint, import boundaries, then the fast test suites.
# Stops at the first failure. Add -Spark to run the Spark suite as well.
#   powershell -ExecutionPolicy Bypass -File scripts\check.ps1 [-Spark]
param([switch]$Spark)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = "src;vendor;."

function Step([string]$Name, [scriptblock]$Run) {
    Write-Host "== $Name"
    & $Run
    if ($LASTEXITCODE -ne 0) {
        Write-Host "check failed at: $Name"
        exit $LASTEXITCODE
    }
}

Step "ruff" { python -m ruff check . }
Step "import boundaries" { lint-imports }
Step "unit and module tests" { python -m pytest tests/unit tests/modules -q }
if ($Spark) {
    # Set as the scheduler sets it for the valuation job. See docs/runbook.md.
    $env:PYSPARK_PYTHON = "python"
    Step "spark tests" { python -m pytest tests/spark -q }
}
Write-Host "check passed"
exit 0
