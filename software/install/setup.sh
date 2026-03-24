#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/vinyl-spotify-player"
SERVICE_NAME="vinyl-spotify-player"
REPO_URL="https://github.com/kaanreal/vinyl-spotify-player.git"

echo "[1/5] Installing base packages..."
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip

echo "[2/5] Syncing project..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"
if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$APP_DIR"
fi

echo "[3/5] Creating virtualenv..."
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install --upgrade pip

echo "[4/5] Writing systemd service..."
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" >/dev/null <<EOF
[Unit]
Description=Vinyl Spotify Player runtime
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR/software/pi
ExecStart=$APP_DIR/.venv/bin/python main.py
Restart=always
RestartSec=2
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "[5/5] Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}.service"
sudo systemctl status "${SERVICE_NAME}.service" --no-pager || true

echo "Done. Service installed: ${SERVICE_NAME}"