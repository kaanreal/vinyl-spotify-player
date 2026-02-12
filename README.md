# Vinyl Spotify Player

A production-ready Raspberry Pi project that transforms your Pi into a physical Spotify Connect device with a vintage vinyl record player aesthetic. Features a 480x480 round display showing circular album artwork and track information, with GPIO-based tonearm control for play/pause functionality.

![Concept](docs/concept.md)

## 🎯 Features

- **Spotify Connect Device**: Appears as a native Spotify Connect device on your network
- **Circular Display**: 480x480 round display showing circular album artwork
- **Physical Control**: GPIO tonearm sensor for play/pause (place to play, lift to pause)
- **Real-time Updates**: Track changes and playback state update instantly
- **Headless Operation**: Runs on Raspberry Pi OS Lite without GUI/desktop
- **Auto-start**: Fully automatic boot behavior, no manual intervention needed
- **Production Ready**: Robust error handling, token refresh, caching, and logging

## 📋 Requirements

### Hardware

- Raspberry Pi (3B+, 4, or newer recommended)
- 480x480 round display (SPI or HDMI)
- MicroSD card (16GB+ recommended)
- Power supply (5V/2.5A minimum)
- GPIO tonearm sensor/switch (optional)
- Speakers or audio output

## Software Requirements

- Raspberry Pi OS Lite (Debian 11/Bullseye or newer)
- Python 3.9+
- Raspotify (installed via official script)

## Installation

### 1. Prepare Raspberry Pi OS

Flash Raspberry Pi OS Lite to your SD card:

```bash
# Use Raspberry Pi Imager or manual flash
# Enable SSH in Pi Imager settings if needed
```

Boot the Pi and connect via SSH:

```bash
ssh pi@raspberrypi.local
```

### 2. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/vinyl-spotify-player.git
cd vinyl-spotify-player
```

### 4. Install Raspotify

```bash
chmod +x install/install_raspotify.sh
./install/install_raspotify.sh
```

Edit Raspotify configuration if needed:

```bash
sudo nano /etc/raspotify/conf
```

Configure device name and audio output:

```
DEVICE_NAME="Vinyl Player"
BACKEND="alsa"
DEVICE="default"
```

### 5. Install Dependencies

```bash
chmod +x install/install_dependencies.sh
./install/install_dependencies.sh
```

### 6. Configure Display (if using SPI display)

Enable SPI interface:

```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
```

For specific display drivers, install manufacturer's drivers here.

### 7. Configure GPIO

No special configuration needed for GPIO pin 17 (default). To use a different pin, edit `app/config.py`:

```python
TONEARM_GPIO_PIN: int = 17  # Change to your pin number
```

### 8. Set Up Autostart

```bash
chmod +x install/setup_autostart.sh
./install/setup_autostart.sh
```

### 9. Enable Services

```bash
chmod +x install/enable_services.sh
./install/enable_services.sh
```

### 10. Reboot and Test

```bash
sudo reboot
```

After reboot:

1. Open Spotify on your phone
2. Start playing a song
3. Tap the "Devices Available" icon
4. Select "Vinyl Player"
5. Music should play through the Pi
6. Display should show album art and track info
7. Test tonearm control (place/lift to play/pause)

## Configuration

### Audio Output

To change audio output device:

```bash
aplay -L  # List audio devices
sudo nano /etc/raspotify/conf
```

Set the `DEVICE` parameter:

```
DEVICE="hw:CARD=Headphones,DEV=0"  # For 3.5mm
DEVICE="hw:CARD=ALSA,DEV=0"        # For HDMI
```

Restart service:

```bash
sudo systemctl restart raspotify
```

### Display Settings

Edit `app/config.py` for display customization:

```python
DISPLAY_WIDTH: int = 480
DISPLAY_HEIGHT: int = 480
ALBUM_ART_SIZE: int = 400
DISPLAY_FPS: int = 30
```

### Tonearm Settings

Adjust debounce time in `app/config.py`:

```python
TONEARM_DEBOUNCE_TIME: float = 0.5  # seconds
TONEARM_GPIO_PIN: int = 17
```

To disable GPIO control (for testing):

```python
ENABLE_TONEARM_GPIO: bool = False
```

## Testing

### Test Raspotify Service

```bash
systemctl status raspotify
```

Should show "active (running)".

### Test Display Application

```bash
cd ~/vinyl-spotify-player/app
python3 main.py
```

Display should appear. Press 'Q' or ESC to quit.

### Test GPIO

```bash
gpio readall
```

Verify pin 17 is configured as input.

### View Logs

```bash
# Raspotify logs
journalctl -u raspotify -f

# Display application logs
journalctl -u vinyl-display -f
```

## Troubleshooting

### Device Not Appearing in Spotify Connect

1. Check Raspotify service:

```bash
systemctl status raspotify
journalctl -u raspotify -n 50
```

2. Restart service:

```bash
sudo systemctl restart raspotify
```

3. Verify network connectivity:

```bash
ping -c 4 google.com
```

### No Album Art or Metadata

1. Check DBus connection:

```bash
dbus-send --session --print-reply --dest=org.mpris.MediaPlayer2.raspotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata'
```

2. Verify display app is running:

```bash
systemctl status vinyl-display
```

3. Check logs:

```bash
journalctl -u vinyl-display -n 100
```

### Display Not Showing

1. Check if pygame can initialize:

```bash
cd ~/vinyl-spotify-player/app
python3 -c "import pygame; pygame.init(); print('OK')"
```

2. Verify DISPLAY environment variable:

```bash
echo $DISPLAY
```

Should show `:0`.

3. Test X11 if using desktop:

```bash
DISPLAY=:0 xrandr
```

### Tonearm Not Working

1. Test GPIO manually:

```bash
python3 -c "from gpiozero import Button; btn = Button(17); print('Waiting...'); btn.wait_for_press(); print('Pressed!')"
```

2. Check wiring:
    - GPIO 17 to one side of switch
    - Ground to other side of switch
    - Internal pull-up resistor is enabled in code

3. Check logs for GPIO errors:

```bash
journalctl -u vinyl-display | grep -i gpio
```

### Audio Issues

1. Test audio output:

```bash
speaker-test -t wav -c 2
```

2. Adjust volume:

```bash
alsamixer
```

3. List audio devices:

```bash
aplay -L
```

### High CPU Usage

1. Check polling interval in `app/config.py`:

```python
POLL_INTERVAL: float = 0.5  # Increase to reduce CPU
```

2. Lower display FPS:

```python
DISPLAY_FPS: int = 20  # Reduce from 30
```

### Service Won't Start on Boot

1. Check service status:

```bash
systemctl status vinyl-display
```

2. Enable service:

```bash
sudo systemctl enable vinyl-display
```

3. Check dependencies:

```bash
systemctl list-dependencies vinyl-display
```

## File Structure

```
vinyl-spotify-player/
├── README.md
├── install/
│   ├── install_raspotify.sh      # Install Raspotify
│   ├── install_dependencies.sh   # Install Python packages
│   ├── setup_autostart.sh        # Configure systemd service
│   └── enable_services.sh        # Enable and start services
├── app/
│   ├── config.py                 # Configuration settings
│   ├── spotify_monitor.py        # MPRIS DBus interface
│   ├── album_art_cache.py        # Album art download/cache
│   ├── display_ui.py             # Pygame UI renderer
│   ├── tonearm_gpio.py           # GPIO tonearm control
│   ├── raspotify_control.py      # Raspotify service control
│   └── main.py                   # Main application
└── systemd/
    └── vinyl-display.service     # Systemd service file
```

## Development

### Running Without GPIO

For development without physical hardware, disable GPIO:

```python
# In app/config.py
ENABLE_TONEARM_GPIO: bool = False
```

### Manual Testing

```bash
cd ~/vinyl-spotify-player/app
python3 main.py
```

Press Q or ESC to quit.

### Debugging

Enable debug logging:

```python
# In app/main.py
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

- Album art is cached locally to reduce network usage
- Metadata polling interval is configurable (default: 0.5s)
- Position estimation between polls to smooth progress bar
- Circular masking is pre-computed and cached
- Display FPS is capped at 30fps

## Security Notes

- No Spotify API credentials stored
- No OAuth tokens required
- Metadata accessed via local DBus only
- Runs as non-root user (pi)
- Album art cache stored in user directory

## Credits

- [Raspotify](https://github.com/dtcooper/raspotify) - librespot wrapper for Raspberry Pi
- [librespot](https://github.com/librespot-org/librespot) - Open source Spotify client library

## License

MIT License

## Support

For issues and feature requests, please open an issue on GitHub.

## Future Enhancements

- Volume control knob
- Multi-room audio sync
- OLED display support
- Web configuration interface
- Playlist selection via NFC tags
- LED status indicators

### Control & Sensors

- Rotary encoder (EC11)
- Hall effect sensor (A3144)
- Neodymium magnet (~6×3 mm)

### Power

- 12 V power supply
- Buck converter (12 V → 5 V)

### Misc

- Wires, screws, spacers
- Custom 3D-printed enclosure parts

---

## Repository Structure

```text
vinyl-spotify-player/
│
├─ README.md
├─ docs/
│   ├─ concept.md
│   ├─ wiring.md
│   └─ images/
│
├─ hardware/
│   └─ 3D filez
│
├─ software/
│   ├─ pi/
│   │   ├─ main.py
│   │   ├─ motor.py
│   │   └─ display.py
│   └─ install/
│       └─ setup.sh
│
└─ media/
    └─ ui_assets/
```

---

## Operation Flow

1. Power is connected
2. Raspberry Pi boots automatically
3. Spotify Connect service starts
4. Device appears instantly as a playback device in Spotify
5. Placing the tonearm starts playback and rotation
6. Lifting the tonearm pauses playback and stops rotation

---

## Project Status

Work in progress (school project)
