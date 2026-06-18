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

# ── Confirmation ────────────────────────────────────────────────────────────
echo -e "${BOLD}${RED}WARNING:${RESET} This will remove all Jukebox files and configuration."
read -r -p "Are you sure you want to continue? [y/N] " reply
if [[ ! "${reply}" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# ── Step 1: Stop and disable services ───────────────────────────────────────
log_step "Stopping and disabling Jukebox services..."

SERVICES=(musicui shairport-metadata-bridge)

for svc in "${SERVICES[@]}"; do
    systemctl stop "${svc}" 2>/dev/null || true
    systemctl disable "${svc}" 2>/dev/null || true
    log_ok "${svc} stopped and disabled"
done

# Do NOT disable shairport-sync, raspotify, or avahi-daemon — user may want them.
log_ok "shairport-sync, raspotify, and avahi-daemon left untouched"

# ── Step 2: Remove systemd service files ────────────────────────────────────
log_step "Removing Jukebox systemd service files..."

for svc in musicui shairport-metadata-bridge; do
    rm -f "/etc/systemd/system/${svc}.service"
    log_ok "Removed /etc/systemd/system/${svc}.service"
done

systemctl daemon-reload
log_ok "systemd reloaded"

# ── Step 3: Remove UI application ───────────────────────────────────────────
log_step "Removing UI application..."

APP_DEST="/home/${PI_USER}/jukebox"
if [[ -d "${APP_DEST}" ]]; then
    rm -rf "${APP_DEST}"
    log_ok "Removed ${APP_DEST}"
else
    log_warn "${APP_DEST} does not exist, skipping"
fi

# ── Step 4: Remove display config from /boot/config.txt ────────────────────
log_step "Cleaning display configuration..."

CONFIG_TXT="/boot/config.txt"
DISPLAY_BLOCK_START="# --- Jukebox display config ---"
DISPLAY_BLOCK_END="# --- End Jukebox display config ---"

if [[ -f "${CONFIG_TXT}" ]] && grep -qF "${DISPLAY_BLOCK_START}" "${CONFIG_TXT}"; then
    # Remove lines between and including the markers
    sed -i "/${DISPLAY_BLOCK_START}/,/${DISPLAY_BLOCK_END}/d" "${CONFIG_TXT}"
    log_ok "Display config removed from ${CONFIG_TXT}"
else
    log_warn "Display config not found in ${CONFIG_TXT}"
fi

# ── Step 5: Remove autostart entries ────────────────────────────────────────
log_step "Removing Jukebox autostart entries..."

# Remove labwc autostart
LABWC_DIR="/home/${PI_USER}/.config/labwc"
if [[ -f "${LABWC_DIR}/autostart" ]] && grep -q 'Jukebox' "${LABWC_DIR}/autostart" 2>/dev/null; then
    rm -f "${LABWC_DIR}/autostart"
    log_ok "Removed labwc autostart"
fi

# Remove lxsession autostart entries (pygame viewer)
AUTOSTART_PATHS=(
    "/etc/xdg/lxsession/LXDE-pi/autostart"
    "/home/${PI_USER}/.config/lxsession/LXDE-pi/autostart"
)

for autofile in "${AUTOSTART_PATHS[@]}"; do
    if [[ -f "${autofile}" ]]; then
        sed -i '/^@xset s off$/d' "${autofile}"
        sed -i '/^@xset -dpms$/d' "${autofile}"
        sed -i '/^@xset s noblank$/d' "${autofile}"
        sed -i '\|/jukebox/software/pi/viewer.py|d' "${autofile}"
        log_ok "Cleaned autostart entries from ${autofile}"
    fi
done

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  Jukebox uninstallation complete!${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${YELLOW}A reboot is recommended to revert display settings.${RESET}"
echo ""
