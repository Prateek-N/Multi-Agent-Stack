#Requires -Version 5.1
<#
.SYNOPSIS
    One-command setup for agents-maker on Windows.

.DESCRIPTION
    quickstart.ps1 — agents-maker bootstrap for Windows PowerShell

    Usage (from your project root, with agents-maker\ cloned inside it):
        .\agents-maker\quickstart.ps1
        .\agents-maker\quickstart.ps1 -Update      # regenerate system_prompt.md
        .\agents-maker\quickstart.ps1 -SkipInit    # skip init, just validate + show usage
        .\agents-maker\quickstart.ps1 -NoColor     # plain output (CI/logging)

    What it does:
        1. Checks Python 3.9+ is available
        2. Installs pyyaml (the only runtime dependency)
        3. Runs tools\validate_kit.py to confirm the kit is intact
        4. Runs tools\init_project.py to scan your project and generate system_prompt.md
        5. Prints everything you need to run your first session

.PARAMETER Update
    Regenerate system_prompt.md even if it already exists.

.PARAMETER SkipInit
    Skip init_project.py — only install deps, validate, and show usage.

.PARAMETER NoColor
    Disable colored output (useful in CI or when piping to a file).
#>

param(
    [switch]$Update,
    [switch]$SkipInit,
    [switch]$NoColor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
function Write-Ok   { param([string]$Msg) Write-Colored "[OK]   " "Green"  $Msg }
function Write-Info { param([string]$Msg) Write-Colored "[INFO] " "Cyan"   $Msg }
function Write-Warn { param([string]$Msg) Write-Colored "[WARN] " "Yellow" $Msg }
function Write-Fail { param([string]$Msg) Write-Colored "[FAIL] " "Red"    $Msg }

function Write-Colored {
    param([string]$Tag, [string]$Color, [string]$Msg)
    if ($NoColor) {
        Write-Host "$Tag $Msg"
    } else {
        Write-Host $Tag -ForegroundColor $Color -NoNewline
        Write-Host " $Msg"
    }
}

function Write-Step { param([string]$Msg)
    Write-Host ""
    if ($NoColor) { Write-Host "==> $Msg" }
    else { Write-Host "==> $Msg" -ForegroundColor White }
}

function Write-Hr {
    $line = "-" * 60
    if ($NoColor) { Write-Host $line }
    else { Write-Host $line -ForegroundColor Cyan }
}

# ---------------------------------------------------------------------------
# Locate kit directory (the directory this script lives in)
# ---------------------------------------------------------------------------
$KitDir     = $PSScriptRoot
$ProjectRoot = Split-Path $KitDir -Parent

Write-Hr
Write-Host "  agents-maker quickstart" -ForegroundColor White
Write-Host "  Kit:     $KitDir"
Write-Host "  Project: $ProjectRoot"
Write-Hr

# ---------------------------------------------------------------------------
# Step 1 — Python version check
# ---------------------------------------------------------------------------
Write-Step "Step 1 - Checking Python"

$PY = $null
$candidates = @("python", "python3", "py")

foreach ($candidate in $candidates) {
    $found = Get-Command $candidate -ErrorAction SilentlyContinue
    if (-not $found) { continue }

    try {
        $versionStr = & $candidate -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -ne 0) { continue }

        $parts = $versionStr.Trim().Split(".")
        $major = [int]$parts[0]
        $minor = [int]$parts[1]

        if ($major -ge 3 -and $minor -ge 9) {
            $PY = $candidate
            Write-Ok "Found Python $versionStr at $($found.Source)"
            break
        } else {
            Write-Warn "Skipping $candidate ($versionStr) - need 3.9+"
        }
    } catch {
        continue
    }
}

if (-not $PY) {
    Write-Fail "Python 3.9+ not found."
    Write-Host "  Install from https://python.org, ensure 'Add Python to PATH' is checked, then re-run."
    exit 1
}

# ---------------------------------------------------------------------------
# Step 2 — Install dependencies
# ---------------------------------------------------------------------------
Write-Step "Step 2 - Installing dependencies"

$ReqFile = Join-Path $KitDir "requirements.txt"
if (-not (Test-Path $ReqFile)) {
    Write-Fail "requirements.txt not found at $ReqFile"
    exit 1
}

& $PY -m pip install -r $ReqFile --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Fail "pip install failed. Try: $PY -m pip install pyyaml"
    exit 1
}
Write-Ok "Dependencies installed (pyyaml)"

# ---------------------------------------------------------------------------
# Step 3 — Validate kit integrity
# ---------------------------------------------------------------------------
Write-Step "Step 3 - Validating kit integrity"

$Validator = Join-Path $KitDir "tools\validate_kit.py"
if (-not (Test-Path $Validator)) {
    Write-Fail "tools\validate_kit.py not found - is the kit complete?"
    exit 1
}

& $PY $Validator
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Kit validation failed - see output above."
    Write-Host ""
    Write-Host "  If you modified agent or skill files, re-run validate_kit.py manually:"
    Write-Host "    $PY agents-maker\tools\validate_kit.py"
    exit 1
}
Write-Ok "All integrity checks passed"

# ---------------------------------------------------------------------------
# Step 4 — init_project.py
# ---------------------------------------------------------------------------
if (-not $SkipInit) {
    Write-Step "Step 4 - Initializing project (generating system_prompt.md)"

    $InitScript = Join-Path $KitDir "tools\init_project.py"
    if (-not (Test-Path $InitScript)) {
        Write-Fail "tools\init_project.py not found - is the kit complete?"
        exit 1
    }

    Write-Host ""
    $updateArg = if ($Update) { "--update" } else { "" }
    Write-Info "Running: $PY $InitScript $updateArg --path $ProjectRoot"
    Write-Info "You will be asked to confirm or override the detected domain."
    Write-Host ""

    if ($Update) {
        & $PY $InitScript "--update" "--path" $ProjectRoot
    } else {
        & $PY $InitScript "--path" $ProjectRoot
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "init_project.py failed - see output above."
        exit 1
    }
    Write-Ok "init_project.py completed"
} else {
    Write-Step "Step 4 - Skipping init (-SkipInit)"
    Write-Info "system_prompt.md was not regenerated."
}

# ---------------------------------------------------------------------------
# Step 5 — Final summary and usage guide
# ---------------------------------------------------------------------------
$SystemPromptPath = Join-Path $KitDir "system_prompt.md"

Write-Host ""
Write-Hr
Write-Host "  Setup complete. Here is everything you need to know." -ForegroundColor White
Write-Hr
Write-Host ""

if (Test-Path $SystemPromptPath) {
    $bytes  = (Get-Item $SystemPromptPath).Length
    $tokens = [int]($bytes / 4)
    Write-Ok "system_prompt.md  (~$bytes chars, ~$tokens tokens)"
    Write-Host "  Paste it into your AI tool's system prompt / project instructions."
    Write-Host "  You only need to do this once per AI context."
} else {
    Write-Warn "system_prompt.md was not created. Re-run without -SkipInit."
}

Write-Host ""
Write-Host "  How to generate prompts" -ForegroundColor White
Write-Host ""
Write-Host "  Basic:"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"describe your task here`""
Write-Host ""
Write-Host "  With phase:"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"your task`" --phase implementation"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"your task`" --phase review"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"your task`" --phase solution_design"
Write-Host ""
Write-Host "  With token compression:"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"your task`" --compress"
Write-Host ""
Write-Host "  With full system prompt (for models without persistent system prompt):"
Write-Host "    $PY agents-maker\tools\generate_prompt.py `"your task`" --full"
Write-Host ""
Write-Host "  Valid phases: task_framing | requirements | solution_design |"
Write-Host "                implementation | review_refinement | handoff"
Write-Host ""
Write-Host "  Context loaders (run and paste output with your task)" -ForegroundColor White
Write-Host ""
Write-Host "    $PY agents-maker\context_loaders\project_summary.py --path ."
Write-Host "    $PY agents-maker\context_loaders\repo_tree.py --path ."
Write-Host "    $PY agents-maker\context_loaders\file_chunker.py --path . --files src\main.py src\auth.py"
Write-Host ""
Write-Host "  Keeping system_prompt.md current" -ForegroundColor White
Write-Host ""
Write-Host "    .\agents-maker\quickstart.ps1 -Update"
Write-Host "    # or: $PY agents-maker\tools\init_project.py --update"
Write-Host ""
Write-Host "  Validate any time" -ForegroundColor White
Write-Host ""
Write-Host "    $PY agents-maker\tools\validate_kit.py"
Write-Host ""
Write-Hr
Write-Host ""
