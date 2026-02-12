# Vinyl Spotify Player

A physical vinyl-inspired Spotify player featuring a rotating display, tonearm control, and motor-driven turntable simulation. Designed for Raspberry Pi Zero 2 W with full PC/VM development support.

**You can develop and test everything on your PC/VM first. Hardware is optional until final deployment.**

## Features

- 🎵 **Spotify Connect Integration** - Raspotify for seamless Premium playback
- 🎨 **480x480 Touch Display** - Rotating album artwork synced with playback
- 🎚️ **Hall Effect Tonearm** - Physical play/pause control via magnet sensor
- 🔊 **Rotary Encoder** - Physical volume knob
- 💿 **Motor Control** - DC gear motor spinning at ~33 RPM synced with playback
- 🖱️ **Touch Gestures** - Tap to play/pause, swipe for next/previous
- 💻 **Full PC Development Mode** - Test everything without hardware using keyboard/mouse
- 🔄 **Hardware Abstraction** - Automatic platform detection and stub/real implementation switching

## Hardware (Final Deployment on Pi)

- Raspberry Pi Zero 2 W
- 2.8" round 480x480 touch display (e.g., Waveshare)
- Hall effect sensor (e.g., A3144)
- Rotary encoder (e.g., KY-040)
- DC gear motor with driver (e.g., L298N)
- Power supply and wiring (see [docs/wiring.md](docs/wiring.md))

## Quick Start (PC/VM)

### 1. Install

**Windows:**

```powershell
.\scripts\install.ps1
```

**Linux/macOS:**

```bash
chmod +x scripts/*.sh
./scripts/install.sh --pc
```

### 2. Configure Spotify

1. Create a Spotify app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Set redirect URI to: `http://localhost:8888/callback`
3. Edit `app/config/config.json`:
    ```json
    {
        "spotify": {
            "client_id": "your_client_id_here",
            "client_secret": "your_client_secret_here",
            "redirect_uri": "http://localhost:8888/callback",
            "device_name": "raspotify"
        }
    }
    ```

### 3. Pair with Spotify

**Windows:**

```powershell
.\scripts\pair.ps1
```

**Linux/macOS:**

```bash
./scripts/pair.sh
```

This opens your browser to authorize the app. Tokens are saved locally for future use.

### 4. Run Development Mode

**Windows:**

```powershell
.\scripts\run-dev.ps1
```

**Linux/macOS:**

```bash
./scripts/run-dev.sh
```

A 480x480 window will open showing the UI. Use your keyboard to simulate hardware:

| Key        | Action            |
| ---------- | ----------------- |
| T          | Toggle tonearm    |
| SPACE      | Tap (play/pause)  |
| LEFT/RIGHT | Swipe (prev/next) |
| UP/DOWN    | Encoder (volume)  |
| ESC        | Quit              |

## Quick Start (Raspberry Pi)

### 1. Install

```bash
chmod +x scripts/*.sh
./scripts/install.sh --pi
```

This installs:

- Python dependencies
- Raspotify (Spotify Connect daemon)
- Systemd service for auto-start

### 2. Configure and Pair

Same as PC mode:

```bash
# Edit config
nano app/config/config.json

# Pair with Spotify
./scripts/pair.sh
```

### 3. Run

**Manual start:**

```bash
./scripts/run-dev.sh  # For testing
```

**Auto-start on boot:**

```bash
sudo systemctl enable vinyl-player
sudo systemctl start vinyl-player
```

**Check status:**

```bash
sudo systemctl status vinyl-player
sudo journalctl -u vinyl-player -f
```

## Project Structure

```
vinyl-spotify-player/
├── app/
│   ├── main.py                    # Main application entry point
│   ├── config/
│   │   ├── config.example.json    # Configuration template
│   │   ├── config_loader.py       # Config loading
│   │   └── validate.py            # Config validation
│   ├── spotify/
│   │   ├── oauth_pair.py          # OAuth authorization flow
│   │   ├── tokens.py              # Token management & refresh
│   │   ├── api.py                 # Spotify Web API client
│   │   ├── device.py              # Device management
│   │   └── control.py             # High-level playback control
│   ├── ui/
│   │   ├── display.py             # Main pygame UI (480x480)
│   │   ├── artwork_cache.py       # Background artwork downloading
│   │   ├── touch_input.py         # Touch gesture detection
│   │   └── cover_rotation.py      # Rotating artwork animation
│   ├── io/
│   │   ├── platform.py            # Platform detection (Pi vs PC)
│   │   ├── tonearm_hall.py        # Tonearm sensor (real + stub)
│   │   ├── volume_encoder.py      # Rotary encoder (real + stub)
│   │   └── motor_control.py       # Motor driver (real + stub)
│   └── util/
│       ├── paths.py               # Path utilities
│       └── logging.py             # Logging configuration
├── scripts/
│   ├── install.sh / install.ps1   # Installation
│   ├── pair.sh / pair.ps1         # OAuth pairing
│   ├── run-dev.sh / run-dev.ps1   # Run in dev mode
│   ├── doctor.sh                  # System diagnostics
│   ├── update.sh                  # Update dependencies
│   └── uninstall.sh               # Uninstall
├── systemd/
│   └── vinyl-player.service       # Systemd service for Pi
├── docs/
│   ├── wiring.md                  # Hardware wiring guide
│   ├── assembly.md                # Physical assembly instructions
│   └── troubleshooting.md         # Common issues and fixes
├── data/
│   ├── tokens/                    # Spotify tokens (gitignored)
│   ├── cache/                     # Album artwork cache
│   └── logs/                      # Application logs
├── pyproject.toml                 # Python dependencies
└── README.md                      # This file
```

## How It Works

### Architecture

The app is built with platform abstraction:

- **Platform Detection** (`app/io/platform.py`) - Auto-detects Raspberry Pi vs PC
- **Hardware Modules** - Each hardware component has:
    - **Real implementation** - Uses GPIO/hardware on Pi
    - **Stub implementation** - Simulated behavior for PC/VM
- **Factory Functions** - Auto-select real or stub based on platform

### Spotify Integration

- **Raspotify** - Runs as a Spotify Connect device on Pi
- **Web API** - Controls playback, reads state, adjusts volume
- **OAuth Flow** - Authorization Code Flow with refresh tokens
- **Polling** - Checks playback state every 1 second
- **Device Management** - Auto-transfers playback to Raspotify device

### UI & Animation

- **Pygame Display** - 480x480 window (PC) or fullscreen (Pi)
- **Rotating Album Art** - Synced with motor RPM (default 33.3 RPM)
- **Touch Gestures** - Tap and swipe detection
- **Background Downloads** - Artwork cached to prevent UI freezing
- **Progress Bar** - Real-time playback progress

### Event Flow

1. **Tonearm DOWN** → Play + Start Motor + Start Rotation
2. **Tonearm UP** → Pause + Stop Motor + Stop Rotation
3. **Touch TAP** → Toggle play/pause
4. **Swipe LEFT/RIGHT** → Previous/Next track
5. **Encoder Rotation** → Adjust volume
6. **Playback State Changes** (from phone/other device) → Motor and rotation sync automatically

## Development & Testing

### Diagnostics

Run system checks:

```bash
./scripts/doctor.sh
```

This checks:

- Python installation
- Virtual environment
- Configuration
- Spotify tokens
- API connectivity
- Available devices

### Logs

Logs are written to:

- Console (stdout)
- `data/logs/vinyl_player_YYYYMMDD.log`

### Testing Without Spotify Premium

You need Spotify Premium for playback. However, you can:

- Test OAuth flow without Premium
- Use the diagnostics script to check connectivity
- Develop UI/hardware modules independently

### Customization

Edit `app/config/config.json`:

- `display.fps` - UI refresh rate
- `motor.target_rpm` - Rotation speed
- `polling.spotify_state_interval_ms` - How often to check Spotify state
- `dev_mode.enabled` - Force dev mode on/off
- GPIO pins for hardware components

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues.

**Quick fixes:**

- **"No tokens found"** → Run `./scripts/pair.sh`
- **"Invalid configuration"** → Edit `app/config/config.json` with your Spotify credentials
- **"No active device"** → Make sure Spotify is playing on any device, or install Raspotify on Pi
- **UI frozen when loading artwork** → Check internet connection, artwork downloads in background

## Contributing

This project is designed for personal use and education. Feel free to fork and customize!

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- Built with [pygame](https://www.pygame.org/) for UI
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Raspotify](https://github.com/dtcooper/raspotify) for Spotify Connect on Pi

---

**Enjoy your vinyl-inspired Spotify experience! 🎵💿**
