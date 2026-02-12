# PowerShell installation script for Windows/PC mode
# Vinyl Spotify Player

$ErrorActionPreference = "Stop"

Write-Host "=== Vinyl Spotify Player Installation (PC Mode) ===" -ForegroundColor Green
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Green
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "OK Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR Python not found. Please install Python 3.9 or later." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "OK Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "OK Virtual environment already exists" -ForegroundColor Yellow
}

# Activate and install dependencies
Write-Host ""
Write-Host "[3/4] Installing Python dependencies..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -e .

# Create data directories
Write-Host ""
Write-Host "[4/4] Creating data directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\tokens" | Out-Null
New-Item -ItemType Directory -Force -Path "data\cache" | Out-Null
New-Item -ItemType Directory -Force -Path "data\logs" | Out-Null

# Initialize configuration
if (-not (Test-Path "app\config\config.json")) {
    Copy-Item "app\config\config.example.json" "app\config\config.json"
    Write-Host "OK Configuration file created" -ForegroundColor Yellow
    Write-Host "  Please edit app\config\config.json with your Spotify credentials!" -ForegroundColor Yellow
}
else {
    Write-Host "OK Configuration file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit app\config\config.json with your Spotify credentials"
Write-Host "  2. Run: .\scripts\pair.ps1 to authenticate with Spotify"
Write-Host "  3. Run: .\scripts\run-dev.ps1 to start the app"
Write-Host ""
Write-Host "Create a Spotify app at: https://developer.spotify.com/dashboard" -ForegroundColor Yellow
