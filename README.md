# 🎵 Jukebox

> A wireless music player that looks and behaves like a classic turntable. A real vinyl record rotates around a round display that shows the current album artwork. Stream from AirPlay 2 or Spotify Connect — no accounts, no sign-in, no configuration.

---

## Overview

The Jukebox is a custom-built music player developed as a school technology project. It combines a Raspberry Pi with a round HDMI touchscreen, Shairport-Sync for AirPlay 2, and Raspotify for Spotify Connect into a single zero-configuration appliance.

The result is a unique music player that appears as a speaker on your phone the moment you connect to the same Wi-Fi network — with the physical feel of a classic record player.

---

## Features

- **AirPlay 2** — stream from iPhone, iPad, or Mac
- **Spotify Connect** — stream from Spotify (Premium required)
- **Rotating cover art** — album art spins like a vinyl record on the round display
- **Touch controls** — tap to pause/resume
- **Zero configuration** — set the name once; phones discover it automatically
- **Custom enclosure** — 3D-printed turntable design
- **Optional tonearm** — automatic playback via Hall effect sensor

---

## Hardware

### Main Components

| Component | Purpose |
|---|---|
| Raspberry Pi 3B (or Zero 2 W) | Main controller |
| Round HDMI LCD (720×720 or 480×480) | Album artwork display and touch controls |
| USB Audio Interface / HDMI audio | Audio output |
| Audio Amplifier | Speaker amplification |
| Hall Effect Sensor | Tonearm position detection |
| Neodymium Magnet | Trigger for automatic playback |
| JGA25-370 Geared Motor | Optional vinyl rotation |
| Motor Controller | Motor control |
| Bearings | Smooth mechanical movement |
| Rubber Belt | Vinyl drive mechanism |

### Enclosure

The entire enclosure was designed from scratch in Onshape and 3D-printed using Bambu Lab printers. No pre-made enclosure design was used.

## Software

### Architecture

The software runs entirely on the Raspberry Pi and is split into three components:

1. **`server.py`** — Flask web server with Server-Sent Events (SSE), exposes a `/status` JSON endpoint and pushes real-time state updates to all connected clients via `/events`. Runs `playerctl --follow status` in a background thread to detect playback changes instantly.

2. **`viewer.py`** — Native pygame/SDL2 vinyl record viewer. Renders spinning cover art at 30 FPS on the round display. Connects to the server's SSE endpoint for instant state updates and falls back to polling `/status` every 400ms.

3. **`metadata_bridge.py`** — Reads AirPlay cover art from the shairport-sync metadata pipe and writes it to a file for the server to serve.

### How It Works

The Pi runs **Shairport-Sync** (AirPlay 2 receiver) and **Raspotify** (Spotify Connect receiver) simultaneously. Both expose playback metadata via MPRIS, which `playerctl` can query.

When you play music from your phone:
1. The phone streams audio directly to the Pi
2. The server detects the playback state change via playerctl (or SSE push)
3. The viewer starts spinning the cover art
4. Metadata (title, artist, cover art) appears on the display

### Quick Start

```bash
git clone https://github.com/yourname/jukebox
cd jukebox
nano config.env        # set device name and audio output
sudo bash install.sh
sudo reboot
```

After reboot, the device appears as **Jukebox** in your AirPlay and Spotify device lists.

---

## Design & Manufacturing

The circular display shows the current album artwork. A vinyl record with a center cutout is placed around the display, creating the illusion that the artwork is part of the record itself.

- The user can start, pause, and control playback through the touchscreen
- When the tonearm is moved into playback position, a Hall effect sensor detects it and automatically starts playback
- The motorized platter system was designed for optional vinyl rotation

---

## Challenges

During development we encountered several challenges:
- Long shipping times for components
- The original display failed to arrive and had to be reordered
- AirPlay pause detection required SSE push to avoid polling delay
- Replacing the Chromium kiosk with a native pygame viewer reduced CPU load and heat significantly
- Limited project timeline
- Integration of hardware and software systems

---

## Team

### Kaan
Project planning, hardware sourcing, software development, GitHub management, enclosure design, testing and integration.

### Marc
Software development, prototype implementation, testing and troubleshooting.

### Lennard
Mechanical construction, 3D design support, assembly and prototyping.

---

## Documentation

- [Kaan's Development Log](docs/kaan.md)
- [Marc's Development Log](docs/marc.md)
- [Lennard's Development Log](docs/lennard.md)
- [Hardware Guide](docs/hardware.md)
- [Wiring Guide](docs/wiring.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Project Concept](docs/concept.md)

---

## Repository

GitHub Repository:
https://github.com/kaanreal/jukebox

---

## Project Timeline

Project Start: **14 April 2026**

Project developed during the 2026 school technology project period.

---

## License

This project was created for educational purposes as part of a school technology project.
