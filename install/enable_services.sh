#!/bin/bash
set -e

echo "Enabling Raspotify..."
sudo systemctl enable raspotify
sudo systemctl start raspotify

echo "Waiting for Raspotify to initialize..."
sleep 5

echo "Enabling Vinyl Display service..."
sudo systemctl enable vinyl-display.service
sudo systemctl start vinyl-display.service

echo "Services enabled and started"
echo ""
echo "Service status:"
systemctl status raspotify --no-pager
echo ""
systemctl status vinyl-display --no-pager

echo ""
echo "Installation complete! The system will start automatically on boot."
echo "Open Spotify on your phone and look for 'Vinyl Player' in Spotify Connect."
