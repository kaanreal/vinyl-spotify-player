#!/bin/bash
set -e

echo "Setting up autostart services..."

APP_DIR="/home/pi/vinyl-spotify-player/app"

sudo cp /home/pi/vinyl-spotify-player/systemd/vinyl-display.service /etc/systemd/system/

sudo sed -i "s|/path/to/app|${APP_DIR}|g" /etc/systemd/system/vinyl-display.service

sudo systemctl daemon-reload

echo "Autostart configuration complete"
