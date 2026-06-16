#!/usr/bin/env bash
# Launch the vinyl player kiosk on the round display.
# Run this from the Pi console or via SSH with DISPLAY=:0.

set -euo pipefail

KIOSK_URL="${1:-http://localhost:8888}"

echo "Starting kiosk on DISPLAY=$DISPLAY → $KIOSK_URL"

exec chromium-browser \
  --kiosk \
  --no-first-run \
  --disable-features=TranslateUI \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --touch-events=enabled \
  "$KIOSK_URL"
