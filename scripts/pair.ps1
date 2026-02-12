# PowerShell pairing script for Windows
# Vinyl Spotify Player - Spotify OAuth

$ErrorActionPreference = "Stop"

Write-Host "=== Spotify OAuth Pairing ===" -ForegroundColor Green
Write-Host ""

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

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Run pairing
Write-Host "Starting OAuth flow..." -ForegroundColor Yellow
Write-Host "This will open your browser to authorize the app."
Write-Host ""

python -c @"
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from app.config.config_loader import load_config
from app.spotify.oauth_pair import start_oauth_flow
from app.spotify.tokens import TokenManager
from app.util.logging import setup_logging

logger = setup_logging('pair')

try:
    config = load_config()
    spotify_config = config['spotify']
    
    auth_code = start_oauth_flow(
        spotify_config['client_id'],
        spotify_config['redirect_uri']
    )
    
    if not auth_code:
        logger.error('Failed to get authorization code')
        sys.exit(1)
    
    token_manager = TokenManager(
        spotify_config['client_id'],
        spotify_config['client_secret']
    )
    
    tokens = token_manager.exchange_code_for_tokens(
        auth_code,
        spotify_config['redirect_uri']
    )
    
    print()
    print('SUCCESS Successfully paired with Spotify!')
    print(f'SUCCESS Tokens saved to {token_manager.token_path}')
    print()
    print('You can now run: .\scripts\run-dev.ps1')

except Exception as e:
    logger.error(f'Pairing failed: {e}')
    sys.exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Pairing complete!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Pairing failed. Please check the error above." -ForegroundColor Red
    exit 1
}
