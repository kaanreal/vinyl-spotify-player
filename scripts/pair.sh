#!/bin/bash
# Spotify OAuth pairing script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Spotify OAuth Pairing ===${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Please run ./scripts/install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if config exists
if [[ ! -f "app/config/config.json" ]]; then
    echo -e "${RED}Configuration file not found!${NC}"
    echo "Please run ./scripts/install.sh first"
    exit 1
fi

# Run pairing
echo -e "${YELLOW}Starting OAuth flow...${NC}"
echo "This will open your browser to authorize the app."
echo ""

python3 - <<EOF
import sys
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path.cwd()))

from app.config.config_loader import load_config
from app.spotify.oauth_pair import start_oauth_flow
from app.spotify.tokens import TokenManager
from app.util.logging import setup_logging

logger = setup_logging("pair")

try:
    # Load config
    config = load_config()
    spotify_config = config['spotify']
    
    # Start OAuth flow
    auth_code = start_oauth_flow(
        spotify_config['client_id'],
        spotify_config['redirect_uri']
    )
    
    if not auth_code:
        logger.error("Failed to get authorization code")
        sys.exit(1)
    
    # Exchange code for tokens
    token_manager = TokenManager(
        spotify_config['client_id'],
        spotify_config['client_secret']
    )
    
    tokens = token_manager.exchange_code_for_tokens(
        auth_code,
        spotify_config['redirect_uri']
    )
    
    print()
    print("✓ Successfully paired with Spotify!")
    print(f"✓ Tokens saved to {token_manager.token_path}")
    print()
    print("You can now run: ./scripts/run-dev.sh")

except Exception as e:
    logger.error(f"Pairing failed: {e}")
    sys.exit(1)
EOF

echo ""
echo -e "${GREEN}Pairing complete!${NC}"
