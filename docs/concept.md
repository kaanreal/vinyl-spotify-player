# Concept

The **Vinyl Spotify Player** should feel like a physical record player while running fully autonomous on Raspberry Pi.

## UX Goals

- **Zero-friction startup:** power on → device appears in Spotify Connect.
- **Physical controls first:** tonearm placement drives playback state.
- **Visual coherence:** circular display always reflects currently playing media.
- **Graceful degradation:** if Spotify API/display/motor fails, keep the rest usable.

## Runtime Components

1. `main.py`
   - orchestrates sensor reading and playback state transitions
2. `motor.py`
   - controls motor speed / start-stop behavior
3. `display.py`
   - renders album art + status text (fallback UI when no art available)

## State Machine

- `IDLE` → tonearm lifted
- `PLAYING` → tonearm down, rotation enabled
- `PAUSED` → tonearm lifted after prior playback
- `ERROR` → hardware/service failure; show error on display

Transitions should be deterministic and debounced to prevent noisy sensor toggles.

## Milestone Plan

1. Bring-up: stable Pi boot + service manager
2. Sensor integration: hall sensor tonearm detection
3. Motor integration: smooth acceleration/deceleration
4. Display integration: album art and fallback status screen
5. Spotify integration: auto-connect and playback controls
6. Polishing: logs, retries, thermal/power checks
