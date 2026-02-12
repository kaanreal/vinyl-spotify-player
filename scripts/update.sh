#!/bin/bash
# Update Vinyl Spotify Player

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Updating Vinyl Spotify Player ===${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Pull latest changes
echo -e "${GREEN}[1/3] Pulling latest changes from git...${NC}"
git pull

# Update virtual environment dependencies
echo -e "${GREEN}[2/3] Updating Python dependencies...${NC}"
if [[ -d "venv" ]]; then
    source venv/bin/activate
    pip install --upgrade pip
    
    # Detect mode
    if [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        pip install --upgrade -e ".[pi]"
    else
        pip install --upgrade -e .
    fi
else
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Please run ./scripts/install.sh first"
    exit 1
fi

# Check for config changes
echo -e "${GREEN}[3/3] Checking configuration...${NC}"
if [[ -f "app/config/config.example.json" ]]; then
    echo -e "${YELLOW}Check if app/config/config.example.json has new fields${NC}"
    echo -e "${YELLOW}You may need to manually update your config.json${NC}"
fi

echo ""
echo -e "${GREEN}Update complete!${NC}"
