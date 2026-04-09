#!/bin/bash

echo "Starte Spotify Token Refresher..."
python3 /home/pi/spotify-player/refresh.py &

echo "Starte Webserver..."
cd /home/pi/spotify-player
python3 -m http.server 8000