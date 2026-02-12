#!/bin/bash
# System diagnostics for Vinyl Spotify Player

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Vinyl Spotify Player Diagnostics ===${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check Python
echo -e "${BLUE}[1] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
fi
echo ""

# Check virtual environment
echo -e "${BLUE}[2] Checking virtual environment...${NC}"
if [[ -d "venv" ]]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
    
    # Check if packages are installed
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        
        PACKAGES=("requests" "pygame" "Pillow")
        for pkg in "${PACKAGES[@]}"; do
            if python -c "import $pkg" 2>/dev/null; then
                echo -e "${GREEN}  ✓ $pkg installed${NC}"
            else
                echo -e "${RED}  ✗ $pkg not installed${NC}"
            fi
        done
    fi
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo -e "${YELLOW}  Fix: Run ./scripts/install.sh${NC}"
fi
echo ""

# Check configuration
echo -e "${BLUE}[3] Checking configuration...${NC}"
if [[ -f "app/config/config.json" ]]; then
    echo -e "${GREEN}✓ Configuration file exists${NC}"
    
    # Check if configured
    if grep -q "YOUR_SPOTIFY_CLIENT_ID" app/config/config.json; then
        echo -e "${RED}  ✗ Configuration not complete (contains placeholder values)${NC}"
        echo -e "${YELLOW}  Fix: Edit app/config/config.json with your Spotify credentials${NC}"
    else
        echo -e "${GREEN}  ✓ Configuration appears complete${NC}"
    fi
else
    echo -e "${RED}✗ Configuration file not found${NC}"
    echo -e "${YELLOW}  Fix: Run ./scripts/install.sh${NC}"
fi
echo ""

# Check tokens
echo -e "${BLUE}[4] Checking Spotify tokens...${NC}"
if [[ -f "data/tokens/spotify_tokens.json" ]]; then
    echo -e "${GREEN}✓ Spotify tokens exist${NC}"
    
    # Check if tokens are valid (basic check)
    if [[ -s "data/tokens/spotify_tokens.json" ]]; then
        echo -e "${GREEN}  ✓ Token file is not empty${NC}"
    else
        echo -e "${RED}  ✗ Token file is empty${NC}"
        echo -e "${YELLOW}  Fix: Run ./scripts/pair.sh${NC}"
    fi
else
    echo -e "${RED}✗ Spotify tokens not found${NC}"
    echo -e "${YELLOW}  Fix: Run ./scripts/pair.sh${NC}"
fi
echo ""

# Check Spotify connectivity
echo -e "${BLUE}[5] Checking Spotify API connectivity...${NC}"
if [[ -f "data/tokens/spotify_tokens.json" ]] && [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    
    python3 - <<'EOF'
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    from app.config.config_loader import load_config
    from app.spotify.tokens import TokenManager
    from app.spotify.api import SpotifyAPI
    
    config = load_config()
    token_manager = TokenManager(
        config['spotify']['client_id'],
        config['spotify']['client_secret']
    )
    
    if token_manager.has_valid_tokens():
        api = SpotifyAPI(token_manager)
        devices = api.get_devices()
        
        print("\033[0;32m✓ Successfully connected to Spotify API\033[0m")
        print(f"\033[0;32m  Found {len(devices)} device(s)\033[0m")
        
        for device in devices:
            active = "🎵 ACTIVE" if device.get('is_active') else ""
            print(f"    - {device['name']} ({device['type']}) {active}")
    else:
        print("\033[0;31m✗ Invalid tokens\033[0m")
        print("\033[1;33m  Fix: Run ./scripts/pair.sh\033[0m")

except Exception as e:
    print(f"\033[0;31m✗ Failed to connect to Spotify API\033[0m")
    print(f"\033[0;31m  Error: {e}\033[0m")
    sys.exit(1)
EOF
else
    echo -e "${YELLOW}⊘ Skipped (prerequisites not met)${NC}"
fi
echo ""

# Platform detection
echo -e "${BLUE}[6] Platform information...${NC}"
if [[ -f /proc/device-tree/model ]]; then
    MODEL=$(cat /proc/device-tree/model)
    echo -e "${GREEN}✓ Hardware: $MODEL${NC}"
else
    echo -e "${YELLOW}⊘ Not running on Raspberry Pi${NC}"
fi

if command -v raspotify &> /dev/null; then
    echo -e "${GREEN}✓ Raspotify installed${NC}"
else
    echo -e "${YELLOW}⊘ Raspotify not installed (OK for PC/VM mode)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
echo "If all checks pass, you're ready to run:"
echo "  ./scripts/run-dev.sh"
echo ""
