#!/bin/bash
set -e

echo "Installing Raspotify..."

curl -sL https://dtcooper.github.io/raspotify/install.sh | sh

echo "Configuring Raspotify..."

sudo tee /etc/raspotify/conf <<EOF
DEVICE_NAME="Vinyl Player"
BITRATE="320"
VOLUME_NORMALISATION="false"
BACKEND="alsa"
DEVICE="default"
MIXER="Master"
INITIAL_VOLUME="80"
OPTIONS="--cache /var/cache/raspotify"
EOF

echo "Raspotify installed successfully"
