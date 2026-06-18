#!/usr/bin/env bash
set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.env"

# Colour support
if [[ -t 1 ]]; then
    BOLD="\033[1m"
    CYAN="\033[36m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    RED="\033[31m"
    RESET="\033[0m"
else
    BOLD=""; CYAN=""; GREEN=""; YELLOW=""; RED=""; RESET=""
fi

log_step()   { echo -e "${BOLD}${CYAN}==>${RESET} ${BOLD}$*${RESET}"; }
log_ok()     { echo -e "  ${GREEN}✓${RESET} $*"; }
log_warn()   { echo -e "  ${YELLOW}⚠${RESET} $*"; }
log_error()  { echo -e "  ${RED}✗${RESET} $*"; }

# ── Root check ──────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)."
    exit 1
fi

# ── Step 1: System packages ─────────────────────────────────────────────────
log_step "Installing system dependencies..."

apt-get update -qq

DEPS=(shairport-sync playerctl python3-pip python3-flask python3-pygame avahi-daemon)

apt-get install -y -qq "${DEPS[@]}"
log_ok "System dependencies installed"

# ── Step 2: Raspotify ──────────────────────────────────────────────────────
log_step "Installing Raspotify (Spotify Connect)..."
if command -v raspotify &>/dev/null; then
    log_ok "Raspotify already installed"
else
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
    log_ok "Raspotify installed"
fi

# ── Step 3: Config files ────────────────────────────────────────────────────
log_step "Installing configuration files..."

sed -e "s|\${DEVICE_NAME}|${DEVICE_NAME}|g" \
    -e "s|\${AUDIO_OUTPUT}|${AUDIO_OUTPUT}|g" \
    "${SCRIPT_DIR}/config/shairport-sync.conf" > /etc/shairport-sync.conf
log_ok "shairport-sync.conf installed"

sed -e "s|\${DEVICE_NAME}|${DEVICE_NAME}|g" \
    -e "s|\${AUDIO_OUTPUT}|${AUDIO_OUTPUT}|g" \
    "${SCRIPT_DIR}/config/raspotify.conf" > /etc/raspotify/conf
log_ok "raspotify.conf installed"

# ── Step 4: Systemd services ────────────────────────────────────────────────
log_step "Installing systemd services..."

for svc in musicui shairport-metadata-bridge; do
    sed "s/\${PI_USER}/${PI_USER}/g" "${SCRIPT_DIR}/systemd/${svc}.service" > "/etc/systemd/system/${svc}.service"
    log_ok "${svc}.service installed"
done

systemctl daemon-reload
log_ok "systemd reloaded"

# ── Step 5: UI application ──────────────────────────────────────────────────
log_step "Installing UI application..."

APP_DEST="/home/${PI_USER}/jukebox"
rm -rf "${APP_DEST}"
cp -r "${SCRIPT_DIR}" "${APP_DEST}"
chown -R "${PI_USER}:${PI_USER}" "${APP_DEST}"
log_ok "Application copied to ${APP_DEST}"

pip3 install --break-system-packages -r "${APP_DEST}/software/pi/requirements.txt" -q 2>/dev/null || pip3 install -r "${APP_DEST}/software/pi/requirements.txt" -q
log_ok "Python dependencies installed"

# ── Step 6: Display config ──────────────────────────────────────────────────
log_step "Configuring display..."

CONFIG_TXT="/boot/config.txt"
DISPLAY_BLOCK_START="# --- Jukebox display config ---"
DISPLAY_BLOCK_END="# --- End Jukebox display config ---"

if grep -qF "${DISPLAY_BLOCK_START}" "${CONFIG_TXT}" 2>/dev/null; then
    log_ok "Display config already present in ${CONFIG_TXT}"
else
    cat >> "${CONFIG_TXT}" <<-EOF

${DISPLAY_BLOCK_START}
# Round HDMI LCD — 720x720 @ 60 Hz
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=720 720 60 1 0 0 0
hdmi_timings=720 0 20 30 30 720 0 5 5 20 0 0 0 60 0 6400000 1
display_rotate=${DISPLAY_ROTATE}
${DISPLAY_BLOCK_END}
EOF
    log_ok "Display config appended to ${CONFIG_TXT}"
fi

# ── Step 7: SDL2/ pygame viewer autostart ───────────────────────────────────
log_step "Configuring pygame SDL2 viewer autostart..."

if ls /usr/share/wayland-sessions/labwc* &>/dev/null || ls /usr/share/xsessions/labwc* &>/dev/null; then
    # labwc autostart — shell script
    AUTOSTART_DIR="/home/${PI_USER}/.config/labwc"
    AUTOSTART_DEST="${AUTOSTART_DIR}/autostart"
    mkdir -p "${AUTOSTART_DIR}"

    cat > "${AUTOSTART_DEST}" <<-EOF
#!/bin/sh
# Jukebox — SDL2/ pygame vinyl viewer on the round display
export DISPLAY=:0
export GDK_BACKEND=x11
sleep 2
python3 /home/${PI_USER}/jukebox/software/pi/viewer.py &
EOF
    chmod +x "${AUTOSTART_DEST}"
else
    # LXDE / lxsession autostart — @command format
    AUTOSTART_DEST=""
    if [[ -f /etc/xdg/lxsession/LXDE-pi/autostart ]]; then
        AUTOSTART_DEST="/etc/xdg/lxsession/LXDE-pi/autostart"
    elif [[ -d /home/${PI_USER}/.config/lxsession/LXDE-pi ]]; then
        AUTOSTART_DEST="/home/${PI_USER}/.config/lxsession/LXDE-pi/autostart"
    else
        mkdir -p "/home/${PI_USER}/.config/lxsession/LXDE-pi"
        AUTOSTART_DEST="/home/${PI_USER}/.config/lxsession/LXDE-pi/autostart"
    fi

    for line in \
        "@xset s off" \
        "@xset -dpms" \
        "@xset s noblank" \
        "@python3 /home/${PI_USER}/jukebox/software/pi/viewer.py"
    do
        if ! grep -qF "${line}" "${AUTOSTART_DEST}" 2>/dev/null; then
            echo "${line}" >> "${AUTOSTART_DEST}"
        fi
    done
fi

chown -R "${PI_USER}:${PI_USER}" "/home/${PI_USER}/.config" 2>/dev/null || true
log_ok "Autostart configured in ${AUTOSTART_DEST}"

# ── Step 8: Enable and start services ──────────────────────────────────────
log_step "Enabling and starting services..."

SERVICES=(shairport-sync raspotify musicui shairport-metadata-bridge avahi-daemon)

for svc in "${SERVICES[@]}"; do
    systemctl enable "${svc}" 2>/dev/null || log_warn "Could not enable ${svc}"
    systemctl restart "${svc}" 2>/dev/null || log_warn "Could not start ${svc}"
    log_ok "${svc} enabled and started"
done

# ── Done ────────────────────────────────────────────────────────────────────
LAN_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  Jukebox installation complete!${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Device name : ${BOLD}${DEVICE_NAME}${RESET}"
echo -e "  LAN address : ${BOLD}${LAN_IP}${RESET}"
echo -e "  Web UI      : ${BOLD}http://${LAN_IP}:${UI_PORT}${RESET}"
echo ""
echo -e "  ${YELLOW}Reboot recommended to apply display settings.${RESET}"
echo -e "  ${YELLOW}Run: sudo reboot${RESET}"
echo ""
