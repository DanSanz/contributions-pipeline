# Pre-commit hook body. Turn the hook on once per clone with:
#   git config core.hooksPath .githooks
# Ruff on the staged Python files only. Tests run in scripts\check.ps1 and in CI.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$python = @(git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -like "*.py" })
if ($python.Count -eq 0) { exit 0 }

python -m ruff check --force-exclude @python
exit $LASTEXITCODE
