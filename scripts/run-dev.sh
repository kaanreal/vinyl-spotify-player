#!/bin/bash
# Run the Vinyl Spotify Player in development mode

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Check if tokens exist
if [[ ! -f "data/tokens/spotify_tokens.json" ]]; then
    echo -e "${RED}Spotify tokens not found!${NC}"
    echo "Please run ./scripts/pair.sh first"
    exit 1
fi

echo -e "${GREEN}=== Starting Vinyl Spotify Player (Dev Mode) ===${NC}"
echo ""
echo -e "${YELLOW}Keyboard Controls:${NC}"
echo "  T              - Toggle tonearm (play/pause)"
echo "  SPACE          - Tap to play/pause"
echo "  LEFT/RIGHT     - Previous/Next track"
echo "  UP/DOWN        - Volume up/down"
echo "  ESC            - Quit"
echo ""

# Run the app
python3 -m app.main
