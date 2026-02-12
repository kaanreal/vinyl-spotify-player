#!/bin/bash
# Installation script for Vinyl Spotify Player
# Supports PC/VM mode and Raspberry Pi mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect mode
MODE="auto"
if [[ "$1" == "--pc" ]]; then
    MODE="pc"
elif [[ "$1" == "--pi" ]]; then
    MODE="pi"
fi

# Auto-detect if not specified
if [[ "$MODE" == "auto" ]]; then
    if [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        MODE="pi"
    else
        MODE="pc"
    fi
fi

echo -e "${GREEN}=== Vinyl Spotify Player Installation ===${NC}"
echo -e "Mode: ${YELLOW}$MODE${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Install system dependencies
echo -e "${GREEN}[1/5] Installing system dependencies...${NC}"

if [[ "$MODE" == "pi" ]]; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv \
        python3-pygame python3-pil python3-rpi.gpio \
        git curl
    
    # Install Raspotify if not present
    if ! command -v raspotify &> /dev/null; then
        echo -e "${YELLOW}Installing Raspotify...${NC}"
        curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
    else
        echo -e "${GREEN}Raspotify already installed${NC}"
    fi
else
    # PC/VM mode - check for Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 not found. Please install Python 3.9 or later.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Python 3 found: $(python3 --version)${NC}"
fi

# Create virtual environment
echo -e "${GREEN}[2/5] Creating virtual environment...${NC}"

if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
echo -e "${GREEN}[3/5] Installing Python dependencies...${NC}"

if [[ "$MODE" == "pi" ]]; then
    pip install -e ".[pi]"
else
    pip install -e .
fi

# Create data directories
echo -e "${GREEN}[4/5] Creating data directories...${NC}"
mkdir -p data/tokens data/cache data/logs

# Initialize configuration
echo -e "${GREEN}[5/5] Initializing configuration...${NC}"

if [[ ! -f "app/config/config.json" ]]; then
    cp app/config/config.example.json app/config/config.json
    echo -e "${YELLOW}Configuration file created at app/config/config.json${NC}"
    echo -e "${YELLOW}Please edit this file with your Spotify credentials!${NC}"
else
    echo -e "${GREEN}Configuration file already exists${NC}"
fi

# Pi-specific setup
if [[ "$MODE" == "pi" ]]; then
    echo ""
    echo -e "${GREEN}[Pi] Installing systemd service...${NC}"
    
    # Create service file with correct paths
    sudo cp systemd/vinyl-player.service /etc/systemd/system/
    sudo sed -i "s|/home/pi/vinyl-spotify-player|$PROJECT_ROOT|g" /etc/systemd/system/vinyl-player.service
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}Systemd service installed${NC}"
    echo -e "${YELLOW}To enable on boot: sudo systemctl enable vinyl-player${NC}"
    echo -e "${YELLOW}To start now: sudo systemctl start vinyl-player${NC}"
fi

echo ""
echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit app/config/config.json with your Spotify credentials"
echo "  2. Run: ./scripts/pair.sh to authenticate with Spotify"

if [[ "$MODE" == "pc" ]]; then
    echo "  3. Run: ./scripts/run-dev.sh to start the app"
else
    echo "  3. Run: sudo systemctl start vinyl-player"
    echo "     OR reboot for auto-start if enabled"
fi

echo ""
echo -e "${YELLOW}Don't have Spotify credentials yet?${NC}"
echo "Create an app at: https://developer.spotify.com/dashboard"
