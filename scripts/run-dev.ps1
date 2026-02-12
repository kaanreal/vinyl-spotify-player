# PowerShell run script for Windows
# Vinyl Spotify Player - Development Mode

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "ERROR Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run .\scripts\install.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Check tokens
if (-not (Test-Path "data\tokens\spotify_tokens.json")) {
    Write-Host "ERROR Spotify tokens not found!" -ForegroundColor Red
    Write-Host "Please run .\scripts\pair.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

Write-Host "=== Starting Vinyl Spotify Player (Dev Mode) ===" -ForegroundColor Green
Write-Host ""
Write-Host "Keyboard Controls:" -ForegroundColor Yellow
Write-Host "  T              - Toggle tonearm (play/pause)"
Write-Host "  SPACE          - Tap to play/pause"
Write-Host "  LEFT/RIGHT     - Previous/Next track"
Write-Host "  UP/DOWN        - Volume up/down"
Write-Host "  ESC            - Quit"
Write-Host ""

# Run the app
python -m app.main
