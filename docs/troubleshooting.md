# Troubleshooting

Common issues and their solutions.

---

## 1. Device not showing up in AirPlay

**Check:** Is `shairport-sync` running?

```bash
sudo systemctl status shairport-sync
```

If it is not active, start and enable it:

```bash
sudo systemctl enable --now shairport-sync
```

**Check:** Is `avahi-daemon` running? AirPlay discovery uses mDNS (Bonjour).

```bash
sudo systemctl status avahi-daemon
```

**Check:** Are the Pi and your phone on the same network subnet? mDNS does not route across subnets.

**Check:** Does your network allow mDNS? Some enterprise or guest Wi-Fi networks block it.

---

## 2. Device not showing up in Spotify

**Check:** Is the raspotify service running?

```bash
sudo systemctl status raspotify
```

**Check:** Raspotify config at `/etc/raspotify/conf` — is `LIBRESPOT_NAME` set correctly?

```bash
grep LIBRESPOT_NAME /etc/raspotify/conf
```

**Check:** Is port 5353 (mDNS) open? Spotify discovery also uses mDNS.

**Reboot** — occasionally raspotify needs a restart after network changes.

---

## 3. Cover art not loading

**For AirPlay:** Check the metadata bridge:

```bash
sudo systemctl status shairport-metadata-bridge
journalctl -u shairport-metadata-bridge --no-pager -n 20
```

Look for errors about the pipe or base64 decoding.

**For Spotify:** `playerctl metadata mpris:artUrl` should return a file:// path. If not, raspotify may not be exposing MPRIS metadata. Try restarting:

```bash
sudo systemctl restart raspotify
```

**Check:** Does `/tmp/current_art.jpg` exist? If not, the metadata bridge hasn't written any cover art yet. Play a track with cover art to test.

**Check:** The UI server logs:

```bash
journalctl -u musicui --no-pager -n 20
```

---

## 4. Touch not responding

**Check:** Is the touch controller recognised?

```bash
ls /dev/input/event*
```

Touch the screen and run `evtest` to see if events are registered.

**Check:** If using I2C touch, verify I2C is enabled:

```bash
sudo raspi-config nonint get_i2c
```

This should return `0` (enabled).

---

## 5. No audio output

**Check:** ALSA device is correct:

```bash
aplay -l
```

Compare the output with your `AUDIO_OUTPUT` setting in `config.env`.

**Test audio directly:**

```bash
speaker-test -t sine -f 440 -l 1 -D hw:0,0
```

Replace `hw:0,0` with your device.

**Check volume:** Run `alsamixer` and ensure the output is not muted (MM means muted — press `m` to unmute).

---

## 6. Display shows nothing / wrong resolution

**Check:** The display block in `/boot/config.txt`:

```bash
grep -A 8 "Jukebox display config" /boot/config.txt
```

**Check:** The `hdmi_cvt` values match your display's native resolution (720×720 for the Waveshare 4", 480×480 for smaller panels).

**Check:** Is the display receiving power? The Pi's 5V rail may not supply enough. Use a separate power injector if needed.

**Try:** Force HDMI output by adding `hdmi_force_hotplug=1` if missing.

---

## 7. Services not starting after reboot

**Check:** Are the service files in place?

```bash
ls /etc/systemd/system/musicui.service /etc/systemd/system/shairport-metadata-bridge.service
```

**Check:** Were the services enabled?

```bash
systemctl is-enabled musicui
systemctl is-enabled shairport-metadata-bridge
```

**Check:** The user in the service files matches `PI_USER`:

```bash
grep User /etc/systemd/system/musicui.service
```

**Check:** The Python path is correct:

```bash
which python3
```

---

## 8. How to change the device name after install

Edit the `config.env` file in the jukebox directory:

```bash
nano /home/pi/jukebox/config.env
```

Then re-run install:

```bash
sudo bash install.sh
```

Or manually update:

1. `/etc/shairport-sync.conf` — change the `name` field
2. `/etc/raspotify/conf` — change `LIBRESPOT_NAME`
3. Restart both: `sudo systemctl restart shairport-sync raspotify`
