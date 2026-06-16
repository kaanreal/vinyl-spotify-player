#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/vinyl-spotify-player"
SERVICE_NAME="vinyl-spotify-player"
KIOSK_SERVICE="vinyl-kiosk"
REPO_URL="https://github.com/kaanreal/vinyl-spotify-player.git"
PI_USER="${SUDO_USER:-pi}"

echo "============================================"
echo " Vinyl Spotify Player — Full Setup"
echo "============================================"

echo ""
echo "[1/7] Installing system packages..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  git python3 python3-venv python3-pip \
  chromium-browser matchbox-window-manager xserver-xorg x11-xserver-utils \
  raspotify

echo ""
echo "[2/7] Syncing project..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$PI_USER":"$PI_USER" "$APP_DIR"
if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$APP_DIR"
fi

echo ""
echo "[3/7] Creating Python virtualenv..."
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/software/install/requirements.txt"

echo ""
echo "[4/7] Writing backend systemd service..."
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" >/dev/null <<SERVICEEOF
[Unit]
Description=Vinyl Spotify Player — Backend
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$PI_USER
WorkingDirectory=$APP_DIR/software/pi
ExecStart=$APP_DIR/.venv/bin/python server.py
Restart=always
RestartSec=2
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo ""
echo "[5/7] Writing kiosk systemd service..."
sudo tee "/etc/systemd/system/${KIOSK_SERVICE}.service" >/dev/null <<KIOSKEOF
[Unit]
Description=Vinyl Spotify Player — Kiosk Display
After=${SERVICE_NAME}.service
Wants=${SERVICE_NAME}.service

[Service]
Type=simple
User=$PI_USER
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$PI_USER/.Xauthority
ExecStartPre=/usr/bin/sleep 5
ExecStart=/usr/bin/startx /usr/bin/chromium-browser \\
  --kiosk \\
  --no-first-run \\
  --disable-features=TranslateUI \\
  --noerrdialogs \\
  --disable-infobars \\
  --disable-session-crashed-bubble \\
  --disable-pinch \\
  --overscroll-history-navigation=0 \\
  --touch-events=enabled \\
  http://localhost:8888
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
KIOSKEOF

echo ""
echo "[6/7] Configuring display rotation (if needed)..."
# Uncomment one of these for your display:
# Waveshare round LCD via HDMI:
# echo "display_rotate=3" | sudo tee -a /boot/config.txt
# Waveshare SPI round LCD:
# echo "dtoverlay=waveshare35a:rotate=270" | sudo tee -a /boot/config.txt

echo ""
echo "[7/7] Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}.service"
sudo systemctl enable "${KIOSK_SERVICE}.service"

echo ""
echo "============================================"
echo " Setup complete!"
echo ""
echo " Next steps:"
echo "  1. Create a Spotify App at:"
echo "     https://developer.spotify.com/dashboard"
echo ""
echo "  2. Add this Redirect URI in the Spotify App:"
echo "     http://localhost:8888/callback"
echo ""
echo "  3. Edit the config file:"
echo "     sudo -u $PI_USER nano /home/$PI_USER/.config/vinyl-spotify/config.json"
echo "     → set your spotify_client_id"
echo ""
echo "  4. Reboot, then authenticate:"
echo "     Open http://raspberrypi:8888/setup in a browser"
echo "     (or ssh in and run: curl http://localhost:8888/setup)"
echo ""
echo "  5. Optional: set up display driver in /boot/config.txt"
echo "============================================"
