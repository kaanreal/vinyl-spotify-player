# Vinyl Spotify Player

A Raspberry Pi-based Spotify Connect device with a 480x480 circular display and GPIO tonearm control. This project uses Raspotify (librespot) for playback and the Spotify Web API for metadata display and control.

## Hardware Requirements

- Raspberry Pi (3B+, 4, or Zero 2 W recommended)
- 480x480 round display (SPI/DPI interface)
- GPIO-connected tonearm switch
- Speaker or audio output device
- Power supply

## Software Requirements

- Raspberry Pi OS Lite (headless, no desktop)
- Python 3.10+
- Raspotify
- Spotify Premium account
- Spotify Developer App credentials

## Installation

### 1. Flash Raspberry Pi OS Lite

Flash Raspberry Pi OS Lite (64-bit recommended) to your SD card using Raspberry Pi Imager.

Enable SSH before first boot:
- Create an empty file named `ssh` in the boot partition

Configure WiFi (optional):
- Create `wpa_supplicant.conf` in the boot partition with your network credentials

### 2. Initial Setup

SSH into your Raspberry Pi:
```bash
ssh pi@raspberrypi.local
```

Update the system:
```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Raspotify

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

Configure Raspotify:
```bash
sudo nano /etc/raspotify/conf
```

Add/modify these settings:
```
DEVICE_NAME="Vinyl Player"
BITRATE="320"
VOLUME_NORMALISATION="false"
BACKEND="alsa"
```

Enable and start Raspotify:
```bash
sudo systemctl enable raspotify
sudo systemctl start raspotify
```

### 4. Install Python Dependencies

```bash
sudo apt install -y python3-pip python3-pygame python3-pil python3-requests python3-rpi.gpio
cd /home/pi
git clone <your-repo-url> vinyl-spotify-player
cd vinyl-spotify-player
pip3 install -r requirements.txt
```

### 5. Configure Display

For SPI displays, enable SPI:
```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
```

Configure framebuffer for 480x480:
```bash
sudo nano /boot/config.txt
```

Add (adjust for your specific display):
```
dtoverlay=vc4-kms-dpi-generic
dtparam=hactive=480
dtparam=vactive=480
dtparam=hsync=1
dtparam=hfp=1
dtparam=hbp=1
dtparam=vsync=1
dtparam=vfp=1
dtparam=vbp=1
dtparam=rgb666-padhi
```

### 6. Create Spotify Developer App

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify Premium account
3. Click "Create App"
4. Fill in:
   - App name: "Vinyl Spotify Player"
   - App description: "Raspberry Pi display"
   - Redirect URI: `http://127.0.0.1:8888/callback`
5. Save and note your **Client ID** and **Client Secret**

### 7. Configure Credentials

```bash
cd /home/pi/vinyl-spotify-player
cp config.json.example config.json
nano config.json
```

Add your Spotify credentials:
```json
{
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here",
  "redirect_uri": "http://127.0.0.1:8888/callback",
  "device_name": "Vinyl Player",
  "tonearm_gpio_pin": 17,
  "display_width": 480,
  "display_height": 480
}
```

### 8. Pair with Spotify

Run the OAuth pairing script:
```bash
python3 oauth_pair.py
```

This will:
1. Print a URL to authorize the app
2. Open that URL in a browser on your computer
3. Log in and authorize the app
4. Copy the full callback URL from your browser
5. Paste it into the terminal
6. Save tokens to `tokens.json`

### 9. Test the Application

```bash
python3 src/main.py
```

The display should show:
- Album artwork (circular)
- Track information
- Playback progress

Test the tonearm GPIO control.

### 10. Enable Automatic Start

Install the systemd service:
```bash
sudo cp vinyl-spotify-player.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vinyl-spotify-player.service
sudo systemctl start vinyl-spotify-player.service
```

Check status:
```bash
sudo systemctl status vinyl-spotify-player.service
```

View logs:
```bash
sudo journalctl -u vinyl-spotify-player.service -f
```

### 11. Reboot and Test

```bash
sudo reboot
```

After reboot:
- Raspotify should start automatically
- The device appears in Spotify Connect
- The display application starts automatically
- Control playback from your phone
- Use the tonearm to play/pause

## GPIO Wiring

Connect your tonearm switch to:
- GPIO pin 17 (configurable in `config.json`)
- Ground (GND)

The switch should be normally open (NO) and close when the tonearm is placed on the record.

## Troubleshooting

### Display not working
```bash
DISPLAY=:0 python3 src/main.py
```

Or force framebuffer:
```bash
SDL_FBDEV=/dev/fb0 python3 src/main.py
```

### Raspotify not appearing
```bash
sudo systemctl status raspotify
sudo journalctl -u raspotify -f
```

### Token expired
Delete `tokens.json` and run `python3 oauth_pair.py` again.

### GPIO not responding
Check wiring and GPIO pin number in `config.json`.

## File Structure

```
vinyl-spotify-player/
├── README.md
├── requirements.txt
├── config.json.example
├── config.json (created by you)
├── tokens.json (created by oauth_pair.py)
├── oauth_pair.py
├── vinyl-spotify-player.service
├── install.sh
└── src/
    ├── main.py
    ├── config.py
    ├── spotify_client.py
    ├── display_renderer.py
    └── tonearm_controller.py
```

## Features

- ✅ Spotify Connect playback via Raspotify
- ✅ Real-time metadata display
- ✅ Circular album artwork
- ✅ Track name, artist, and album
- ✅ Progress bar with time remaining
- ✅ GPIO tonearm play/pause control
- ✅ Automatic token refresh
- ✅ Headless operation (no desktop required)
- ✅ Boot-time auto-start
- ✅ Robust error handling
- ✅ Local album art caching

## License

MIT
