#!/bin/bash
#
# Vinyl Spotify Player - Installation Script
# Complete setup for Raspberry Pi OS Lite
#

set -e

echo "=========================================="
echo "Vinyl Spotify Player - Installation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}ERROR: Do not run this script as root${NC}"
    echo "Run as regular user (pi): ./setup.sh"
    exit 1
fi

echo -e "${GREEN}[1/9] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${GREEN}[2/9] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-pygame \
    git \
    curl \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libportmidi-dev \
    libpng-dev \
    python3-rpi.gpio

echo ""
echo -e "${GREEN}[3/9] Installing Raspotify...${NC}"
if ! command -v librespot &> /dev/null; then
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
    echo "Raspotify installed successfully"
else
    echo "Raspotify already installed"
fi

echo ""
echo -e "${GREEN}[4/9] Creating application directory...${NC}"
APP_DIR="$HOME/vinyl-spotify-player"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/cache"

echo ""
echo -e "${GREEN}[5/9] Copying application files...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp "$SCRIPT_DIR/../pi/"*.py "$APP_DIR/"
cp "$SCRIPT_DIR/../pi/requirements.txt" "$APP_DIR/"
cp "$SCRIPT_DIR/../pi/config.json.example" "$APP_DIR/"
cp "$SCRIPT_DIR/../pi/vinyl-spotify-player.service" "$APP_DIR/"
cp "$SCRIPT_DIR/../pi/raspotify.conf" "$APP_DIR/"

# Make scripts executable
chmod +x "$APP_DIR/main.py"
chmod +x "$APP_DIR/oauth_pair.py"

echo ""
echo -e "${GREEN}[6/9] Installing Python dependencies...${NC}"
pip3 install --upgrade pip
pip3 install -r "$APP_DIR/requirements.txt"

echo ""
echo -e "${GREEN}[7/9] Configuring Raspotify...${NC}"
if [ -f "$APP_DIR/raspotify.conf" ]; then
    sudo cp "$APP_DIR/raspotify.conf" /etc/raspotify/conf
    echo "Raspotify configuration updated"
fi

# Enable and start Raspotify
sudo systemctl enable raspotify
sudo systemctl restart raspotify
echo "Raspotify enabled and started"

echo ""
echo -e "${GREEN}[8/9] Setting up systemd service...${NC}"
sudo cp "$APP_DIR/vinyl-spotify-player.service" /etc/systemd/system/
sudo systemctl daemon-reload
echo "Systemd service installed (not enabled yet)"

echo ""
echo -e "${GREEN}[9/9] Final configuration...${NC}"

# Create config file if it doesn't exist
if [ ! -f "$APP_DIR/config.json" ]; then
    cp "$APP_DIR/config.json.example" "$APP_DIR/config.json"
    echo "Config file created: $APP_DIR/config.json"
fi

# Set up framebuffer for display
echo "Configuring display..."
if ! grep -q "dtoverlay=vc4-fkms-v3d" /boot/config.txt; then
    echo "" | sudo tee -a /boot/config.txt
    echo "# Display configuration for Vinyl Spotify Player" | sudo tee -a /boot/config.txt
    echo "dtoverlay=vc4-fkms-v3d" | sudo tee -a /boot/config.txt
    echo "hdmi_force_hotplug=1" | sudo tee -a /boot/config.txt
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Create a Spotify Developer Application:"
echo "   - Go to https://developer.spotify.com/dashboard"
echo "   - Create a new app"
echo "   - Add redirect URI: http://127.0.0.1:8888/callback"
echo "   - Copy Client ID and Client Secret"
echo ""
echo "2. Edit configuration file:"
echo "   nano $APP_DIR/config.json"
echo "   - Add your Spotify Client ID"
echo "   - Add your Spotify Client Secret"
echo "   - Configure GPIO pin if needed (default: GPIO 17)"
echo ""
echo "3. Run OAuth pairing (one-time setup):"
echo "   cd $APP_DIR"
echo "   python3 oauth_pair.py"
echo "   - Open the URL in a browser"
echo "   - Log in and authorize"
echo ""
echo "4. Test the application manually:"
echo "   cd $APP_DIR"
echo "   python3 main.py"
echo ""
echo "5. Enable auto-start on boot:"
echo "   sudo systemctl enable vinyl-spotify-player.service"
echo "   sudo systemctl start vinyl-spotify-player.service"
echo ""
echo "6. Check service status:"
echo "   sudo systemctl status vinyl-spotify-player.service"
echo ""
echo "7. View logs:"
echo "   journalctl -u vinyl-spotify-player.service -f"
echo ""
echo -e "${YELLOW}NOTE: A reboot is recommended after configuration.${NC}"
echo ""
