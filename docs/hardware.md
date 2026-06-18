# Hardware Guide

This document covers confirmed-compatible hardware and wiring instructions for Jukebox.

---

## Compatible round HDMI displays

| Model | Resolution | Notes |
|---|---|---|
| Waveshare 4" Round LCD (720×720) | 720×720 | Best tested; HDMI + USB touch |
| Kadi 4" Round HDMI LCD | 720×720 | Same panel as Waveshare |
| Generic 3.5" round TFT | 480×480 | Requires adjusted `hdmi_cvt` values |

### /boot/config.txt (Waveshare 4" 720×720)

```ini
# --- Jukebox display config ---
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=720 720 60 1 0 0 0
hdmi_timings=720 0 20 30 30 720 0 5 5 20 0 0 0 60 0 6400000 1
display_rotate=0
# --- End Jukebox display config ---
```

Change `display_rotate` to:
- `0` — normal
- `1` — 90° clockwise
- `2` — 180°
- `3` — 270° clockwise

### For 480×480 displays

Replace the `hdmi_cvt` line with:

```ini
hdmi_cvt=480 480 60 1 0 0 0
```

And adjust `hdmi_timings` accordingly (consult your display datasheet).

---

## Wiring (text diagram)

```
┌──────────────────────────────────────────────┐
│            Raspberry Pi 3B GPIO              │
├──────────────────────────────────────────────┤
│                                              │
│  HDMI ────── to display HDMI input           │
│                                              │
│  USB  ────── to display touch controller     │
│              (or I2C if applicable)           │
│                                              │
│  5V GPIO 2,4 ──── to display 5V power        │
│  GND GPIO 6  ──── to display GND             │
│                                              │
│  3.5mm jack ──── speakers / amp              │
│  (or HDMI audio to display speakers)          │
└──────────────────────────────────────────────┘
```

---

## Touch interface

Most round HDMI displays use either USB HID touch (works out of the box) or I2C.

### USB HID touch

Plug the display's USB cable into the Pi's USB port. It should be recognised immediately:

```bash
ls /dev/input/event*
```

If you see a new event device appear when you plug it in, touch is working.

### I2C touch (e.g. FT5x06 / GT911)

Enable I2C in raspi-config:

```bash
sudo raspi-config nonint do_i2c 0
```

Then install a device tree overlay. For Waveshare displays this is often:

```bash
dtoverlay=waveshare-round-lcd-4inch
```

in `/boot/config.txt`. Check your display's documentation for the exact overlay name.

---

## Audio output options

### HDMI audio

Audio is carried over HDMI to the display. The ALSA device is typically `hw:0,0`. Set in `config.env`:

```bash
AUDIO_OUTPUT="hw:0,0"
```

### 3.5mm headphone jack

On the Pi 3B the built-in 3.5mm jack is usually `hw:0,0` or `hw:1,0` depending on whether HDMI is the primary output. Switch the audio output in raspi-config:

```bash
sudo raspi-config nonint do_audio 1
```

Then set:

```bash
AUDIO_OUTPUT="hw:0,0"
```

Test with:

```bash
speaker-test -t sine -f 440 -l 1
```

### USB DAC

Plug in a USB DAC (e.g. AudioQuest DragonFly, Hifime, etc.). It will appear as a new ALSA device. List devices:

```bash
aplay -l
```

Then update `config.env` with the correct `hw:X,Y` value, for example:

```bash
AUDIO_OUTPUT="hw:1,0"
```

---

## Power supply

Use a **5V 2.5A** power supply (official Raspberry Pi PSU recommended). The Pi 3B + display + USB DAC draws close to 2A under load.
