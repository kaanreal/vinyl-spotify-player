# Troubleshooting Guide

Common issues and solutions for the Vinyl Spotify Player.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Spotify / Authentication Issues](#spotify--authentication-issues)
- [Hardware Issues](#hardware-issues)
- [Display / UI Issues](#display--ui-issues)
- [Performance Issues](#performance-issues)
- [Raspberry Pi Specific Issues](#raspberry-pi-specific-issues)

---

## Installation Issues

### "Python not found"

**Symptoms:** Installation script fails with "python3: command not found"

**Solution:**

- **Windows:** Download and install Python from [python.org](https://www.python.org/downloads/)
- **Linux/Pi:** `sudo apt-get install python3 python3-pip python3-venv`
- **macOS:** `brew install python3` (requires Homebrew)

---

### "Virtual environment creation failed"

**Symptoms:** `python3 -m venv venv` fails

**Solution:**

```bash
# Ubuntu/Debian/Pi
sudo apt-get install python3-venv

# Or specify full python version
python3.11 -m venv venv
```

---

### "Permission denied" on scripts

**Symptoms:** `./scripts/install.sh: Permission denied`

**Solution:**

```bash
chmod +x scripts/*.sh
./scripts/install.sh
```

---

## Spotify / Authentication Issues

### "No Spotify tokens found"

**Symptoms:** App exits with "Please run ./scripts/pair.sh"

**Solution:**

1. Ensure you've created a Spotify app at [developer.spotify.com](https://developer.spotify.com/dashboard)
2. Edit `app/config/config.json` with your credentials
3. Run pairing script: `./scripts/pair.sh` (Linux) or `.\scripts\pair.ps1` (Windows)

---

### "Invalid client_id or client_secret"

**Symptoms:** Pairing fails with 401 Unauthorized

**Solution:**

1. Double-check credentials in `app/config/config.json`
2. Ensure no extra spaces or quotes
3. Verify credentials at [Spotify Dashboard](https://developer.spotify.com/dashboard)
4. Make sure you copied the full client_secret (can be very long)

---

### "Redirect URI mismatch"

**Symptoms:** Browser shows error after Spotify login

**Solution:**

1. In Spotify app settings, add exact redirect URI: `http://localhost:8888/callback`
2. URI must match exactly in both Spotify dashboard and `config.json`
3. Don't use `https` unless you've set up SSL (use `http`)

---

### "No active device found"

**Symptoms:** App can't find Spotify device to control

**Solution:**

**On PC/VM:**

- Open Spotify on your phone/computer and start playing a song
- The app will detect and use that device
- Or install Raspotify on a Raspberry Pi and configure `device_name` in config

**On Raspberry Pi:**

- Verify Raspotify is running: `systemctl status raspotify`
- Start Raspotify: `sudo systemctl start raspotify`
- Check Raspotify config: `sudo nano /etc/raspotify/conf`
- Device name in `config.json` must match Raspotify device name

---

### "Token expired" or "Invalid token"

**Symptoms:** App worked before, now can't connect to Spotify

**Solution:**

- Tokens refresh automatically, but if it fails:
    ```bash
    rm data/tokens/spotify_tokens.json
    ./scripts/pair.sh
    ```

---

## Hardware Issues

### Hall Sensor (Tonearm) Not Working

**Symptoms:** Moving tonearm doesn't trigger play/pause

**Diagnostics:**

```bash
./scripts/run-dev.sh
# Watch console logs for "Tonearm state changed" messages
```

**Solutions:**

1. **Check magnet/sensor distance:**
    - Should be 1-10mm apart
    - Test by manually moving magnet near sensor
    - Use a multimeter to check sensor output (should go LOW when magnet near)

2. **Verify GPIO pin:**
    - Default is GPIO 17 (Physical pin 11)
    - Check `config.json` → `tonearm.hall_pin`
    - Verify wiring matches

3. **Check sensor polarity:**
    - Some sensors are NPN (active LOW)
    - Others are PNP (active HIGH)
    - Code assumes active LOW - invert logic in software if needed

4. **Power:**
    - Sensor should be powered with 3.3V (NOT 5V)
    - Check VCC and GND connections

---

### Rotary Encoder Not Responding

**Symptoms:** Turning encoder doesn't change volume

**Diagnostics:**

```bash
# Dev mode: Press UP/DOWN arrows to test volume control
# If that works, issue is hardware

# Check logs for "Encoder: +X" or "Encoder: -X"
```

**Solutions:**

1. **Verify GPIO pins:**
    - Default CLK: GPIO 5, DT: GPIO 6
    - Check `config.json` → `encoder.clk_pin`, `encoder.dt_pin`

2. **Check wiring:**
    - CLK and DT swapped → reverse them
    - Encoder VCC should be 3.3V (NOT 5V)

3. **Rotation direction inverted:**
    - Software expects CLK/DT in certain order
    - If volume goes wrong direction, swap CLK and DT pins

4. **Encoder type:**
    - Some encoders have built-in pull-ups for 5V
    - May need external pull-down resistors for 3.3V operation

---

### Motor Not Spinning

**Symptoms:** Motor doesn't start when playback begins

**Diagnostics:**

```bash
# In dev mode, console should show:
# "[STUB] Motor started (simulated 33 RPM)"
# If that works, problem is hardware
```

**Solutions:**

1. **Check external power:**
    - Motor driver needs 5-12V external power (NOT from Pi)
    - Verify power supply voltage and current rating
    - Common ground between Pi and motor supply

2. **Verify GPIO pins:**
    - Default: PWM=GPIO 18, DIR=GPIO 23, ENABLE=GPIO 24
    - Check `config.json` → `motor` section

3. **Test motor directly:**
    - Connect motor + power supply directly to verify motor works
    - Check motor driver connections (IN1, IN2, ENA, OUT1, OUT2)

4. **PWM duty cycle:**
    - Try increasing duty cycle in code (default 50%)
    - Edit `motor_control.py` → `RealMotorController` → `duty_cycle`

5. **Motor driver enable:**
    - Some drivers have enable jumper - ensure it's set
    - Check if driver has built-in enable logic

---

### Motor Running Too Fast/Slow

**Symptoms:** Motor speed doesn't match 33 RPM

**Solutions:**

1. **Adjust target RPM:**
    - Edit `config.json` → `motor.target_rpm`
    - Try values between 30-35 to find ideal speed

2. **PWM duty cycle:**
    - Higher duty = faster speed
    - Edit code or add config option for duty cycle

3. **Gear ratio:**
    - Check motor's gearbox ratio
    - Calculate needed ratio: motor base RPM / 33.3 = required gear ratio

4. **Measure actual RPM:**
    - Use phone camera (slow-mo mode) to count rotations
    - Stopwatch: count rotations in 1 minute

---

## Display / UI Issues

### "Pygame not found" or Import Error

**Symptoms:** `ModuleNotFoundError: No module named 'pygame'`

**Solution:**

```bash
source venv/bin/activate  # Linux
# or
.\venv\Scripts\Activate.ps1  # Windows

pip install pygame
```

---

### Display Window Too Small/Large

**Symptoms:** UI doesn't fit screen or is wrong size

**Solution:**

- Edit `config.json` → `display.width` and `display.height`
- Standard is 480x480 for round display
- Can test with smaller window like 400x400 on PC

---

### Album Artwork Not Loading

**Symptoms:** Display shows placeholder vinyl, no real album art

**Diagnostics:**

- Check internet connection
- Look for errors in logs: `data/logs/vinyl_player_*.log`

**Solutions:**

1. **Network issue:**
    - Verify internet connection
    - Test: `ping api.spotify.com`

2. **Firewall/Proxy:**
    - Ensure Python/pygame can make HTTPS requests
    - Check firewall settings

3. **Clear cache:**

    ```bash
    rm -rf data/cache/*
    ```

4. **Pillow/PIL not installed:**
    ```bash
    pip install Pillow
    ```

---

### Touch Input Not Working

**Symptoms:** Taps and swipes don't register

**Solution (PC/VM):**

- Use mouse clicks instead of touch
- Use keyboard shortcuts: SPACE, LEFT, RIGHT

**Solution (Pi with touch screen):**

- Verify touch driver installed
- Check if touch inputs appear in system: `evtest` (install: `sudo apt-get install evtest`)
- May need to configure pygame to use correct input device

---

### UI Freezing

**Symptoms:** Display stops updating, app becomes unresponsive

**Diagnostics:**

- Check CPU usage: `top` or Task Manager
- Check logs for errors

**Solutions:**

1. **Artwork download blocking:**
    - Should download in background, but check logs
    - Clear cache: `rm -rf data/cache/*`

2. **Spotify polling too fast:**
    - Increase `config.json` → `polling.spotify_state_interval_ms` to 2000

3. **Pi performance:**
    - Close other apps
    - Disable desktop environment (use lite OS)

---

## Performance Issues

### High CPU Usage

**Symptoms:** CPU at 100%, Pi running hot

**Solutions:**

1. **Reduce FPS:**
    - Edit `config.json` → `display.fps` to 20 or 15

2. **Increase polling interval:**
    - Edit `config.json` → `polling.spotify_state_interval_ms` to 2000

3. **Optimize rotation:**
    - Rotation calculation is CPU-intensive
    - May need to reduce rotation quality (edit `cover_rotation.py`)

---

### Delayed Response

**Symptoms:** Button presses take 1-2 seconds to register

**Solutions:**

- Reduce tonearm poll interval: `config.json` → `tonearm.poll_interval_ms` to 25
- Reduce Spotify poll interval to 500ms for faster state updates
- Check network latency to Spotify API

---

## Raspberry Pi Specific Issues

### "RPi.GPIO not available"

**Symptoms:** Error about missing RPi.GPIO module

**Solution:**

```bash
sudo apt-get install python3-rpi.gpio
# Or
pip install RPi.GPIO
```

---

### Systemd Service Won't Start

**Symptoms:** `sudo systemctl start vinyl-player` fails

**Diagnostics:**

```bash
sudo systemctl status vinyl-player
sudo journalctl -u vinyl-player -n 50
```

**Solutions:**

1. **Check paths in service file:**
    - Edit: `sudo nano /etc/systemd/system/vinyl-player.service`
    - Verify `WorkingDirectory` and `ExecStart` paths are correct

2. **Permissions:**
    - Service runs as `pi` user
    - Ensure `pi` owns project files: `sudo chown -R pi:pi /home/pi/vinyl-spotify-player`

3. **Python venv path:**
    - Ensure venv exists: `/home/pi/vinyl-spotify-player/venv/bin/python`

4. **Reload service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart vinyl-player
    ```

---

### Display Not Working on Pi

**Symptoms:** Display stays black or shows garbage

**Solutions:**

1. **Enable SPI:**

    ```bash
    sudo raspi-config
    # Interface Options → SPI → Enable
    sudo reboot
    ```

2. **Check display driver:**
    - Some displays need kernel modules
    - Check manufacturer instructions
    - May need dtoverlay in `/boot/config.txt`

3. **Framebuffer config:**
    - Pygame may need framebuffer for small displays
    - Check display-specific pygame guides

---

### Raspotify Not Found

**Symptoms:** `command not found: raspotify`

**Solution:**

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
sudo systemctl enable raspotify
sudo systemctl start raspotify
```

---

## General Debugging Tips

### Enable Debug Logging

Edit `app/util/logging.py`:

```python
logger.setLevel(logging.DEBUG)  # Changed from INFO
```

---

### Run Doctor Script

```bash
./scripts/doctor.sh
```

Checks:

- Python installation
- Dependencies
- Configuration
- Tokens
- Spotify connectivity

---

### Test Individual Components

**Test Spotify API:**

```python
python3 -c "
from app.config.config_loader import load_config
from app.spotify.tokens import TokenManager
from app.spotify.api import SpotifyAPI

config = load_config()
tm = TokenManager(config['spotify']['client_id'], config['spotify']['client_secret'])
api = SpotifyAPI(tm)
print(api.get_devices())
"
```

**Test GPIO (on Pi):**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print(GPIO.input(17))
GPIO.cleanup()
```

---

## Getting Help

If you're still stuck:

1. **Check logs:** `cat data/logs/vinyl_player_*.log`
2. **Run diagnostics:** `./scripts/doctor.sh`
3. **Verify wiring:** Review [wiring.md](wiring.md)
4. **Check Spotify Dashboard:** Verify app settings
5. **Test on PC first:** Rule out hardware vs software issues

---

**Happy troubleshooting!** 🔧
