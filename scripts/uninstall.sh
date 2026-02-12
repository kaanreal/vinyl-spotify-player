#!/bin/bash
# Uninstall Vinyl Spotify Player

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}=== Uninstall Vinyl Spotify Player ===${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Confirm
read -p "Are you sure you want to uninstall? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Stop and disable service if on Pi
if [[ -f /etc/systemd/system/vinyl-player.service ]]; then
    echo -e "${YELLOW}Stopping and removing systemd service...${NC}"
    sudo systemctl stop vinyl-player || true
    sudo systemctl disable vinyl-player || true
    sudo rm /etc/systemd/system/vinyl-player.service
    sudo systemctl daemon-reload
fi

# Remove virtual environment
echo -e "${YELLOW}Removing virtual environment...${NC}"
rm -rf venv

# Optionally remove data
read -p "Remove cached data and logs? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing data...${NC}"
    rm -rf data/cache/*
    rm -rf data/logs/*
fi

# Optionally remove tokens
read -p "Remove Spotify tokens? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing tokens...${NC}"
    rm -rf data/tokens/*
fi

# Optionally remove config
read -p "Remove configuration? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing config...${NC}"
    rm -f app/config/config.json
fi

echo ""
echo -e "${GREEN}Uninstall complete!${NC}"
echo "To completely remove the project, delete this directory:"
echo "  rm -rf $PROJECT_ROOT"
