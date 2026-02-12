#!/bin/bash

# Vinyl Spotify Player - Installation Script
# This script automates the installation process for Raspberry Pi

set -e

echo "======================================"
echo "Vinyl Spotify Player - Installation"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This does not appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Step 1: Updating system..."
echo "--------------------------------------"
sudo apt update
sudo apt upgrade -y
echo "✓ System updated"
echo ""

# Install Raspotify
echo "Step 2: Installing Raspotify..."
echo "--------------------------------------"
if ! command -v raspotify &> /dev/null; then
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
    echo "✓ Raspotify installed"
else
    echo "✓ Raspotify already installed"
fi
echo ""

# Configure Raspotify
echo "Step 3: Configuring Raspotify..."
echo "--------------------------------------"
RASPOTIFY_CONF="/etc/raspotify/conf"

if [ -f "$RASPOTIFY_CONF" ]; then
    sudo cp "$RASPOTIFY_CONF" "${RASPOTIFY_CONF}.backup"
    echo "✓ Backed up existing configuration"
fi

sudo tee "$RASPOTIFY_CONF" > /dev/null <<EOF
# Raspotify Configuration for Vinyl Spotify Player

# Device name as shown in Spotify Connect
DEVICE_NAME="Vinyl Player"

# Audio bitrate (96, 160, or 320)
BITRATE="320"

# Volume normalization
VOLUME_NORMALISATION="false"

# Audio backend
BACKEND="alsa"

# Additional options
OPTIONS="--initial-volume=50"
EOF

echo "✓ Raspotify configured"
echo ""

# Enable and start Raspotify
sudo systemctl enable raspotify
sudo systemctl restart raspotify
echo "✓ Raspotify enabled and started"
echo ""

# Install Python dependencies
echo "Step 4: Installing Python dependencies..."
echo "--------------------------------------"
sudo apt install -y \
    python3-pip \
    python3-pygame \
    python3-pil \
    python3-requests \
    python3-rpi.gpio

pip3 install -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Enable SPI (for display)
echo "Step 5: Enabling SPI..."
echo "--------------------------------------"
if ! raspi-config nonint get_spi | grep -q 0; then
    sudo raspi-config nonint do_spi 0
    echo "✓ SPI enabled (reboot required)"
else
    echo "✓ SPI already enabled"
fi
echo ""

# Create config from example
echo "Step 6: Setting up configuration..."
echo "--------------------------------------"
if [ ! -f "config.json" ]; then
    cp config.json.example config.json
    echo "✓ Created config.json from example"
    echo ""
    echo "IMPORTANT: You must now edit config.json with your Spotify credentials:"
    echo "  nano config.json"
    echo ""
    echo "You need to add:"
    echo "  - client_id (from Spotify Developer Dashboard)"
    echo "  - client_secret (from Spotify Developer Dashboard)"
    echo "  - device_name (should match Raspotify configuration)"
    echo "  - tonearm_gpio_pin (GPIO pin number for tonearm switch)"
else
    echo "✓ config.json already exists"
fi
echo ""

# Create cache directory
mkdir -p album_art_cache
echo "✓ Created album art cache directory"
echo ""

echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Create a Spotify Developer App:"
echo "   https://developer.spotify.com/dashboard"
echo ""
echo "2. Add redirect URI to your Spotify app:"
echo "   http://127.0.0.1:8888/callback"
echo ""
echo "3. Edit config.json with your credentials:"
echo "   nano config.json"
echo ""
echo "4. Run OAuth pairing:"
echo "   python3 oauth_pair.py"
echo ""
echo "5. Test the application:"
echo "   python3 src/main.py"
echo ""
echo "6. Enable automatic startup:"
echo "   sudo cp vinyl-spotify-player.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable vinyl-spotify-player.service"
echo "   sudo systemctl start vinyl-spotify-player.service"
echo ""
echo "7. Reboot to test automatic startup:"
echo "   sudo reboot"
echo ""
