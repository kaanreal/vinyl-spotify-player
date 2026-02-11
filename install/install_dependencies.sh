#!/bin/bash
set -e

echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

echo "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-pygame \
    python3-pil \
    python3-dbus \
    python3-requests \
    python3-gpiozero \
    playerctl \
    git \
    fonts-dejavu-core

echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install \
    pygame \
    Pillow \
    requests \
    dbus-python \
    gpiozero \
    python-cachecontrol

echo "Creating cache directory..."
mkdir -p /home/pi/.cache/vinyl-player/album-art

echo "Dependencies installed successfully"
