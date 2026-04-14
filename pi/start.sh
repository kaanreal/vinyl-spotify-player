#!/bin/bash

echo "Starte Spotify Token Refresher..."
python3 /home/pi/spotify-player/refresh.py &

chromium-browser http://localhost:8000 &

echo "Starte Webserver..."
cd /home/pi/spotify-player
python3 -m http.server 8000