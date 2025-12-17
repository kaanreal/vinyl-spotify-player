# Vinyl Spotify Player

A custom-built Spotify player designed to look and behave like a classic turntable. A real vinyl record rotates around a fixed circular display that shows the current album artwork. Playback is controlled using a mechanical tonearm, similar to a real record player.

---

## Project Description (Short)

A Raspberry Pi–based Spotify player that combines mechanical motion, physical interaction, and digital media playback in a turntable-inspired design.

---

## Project Idea

The goal of this school technology project is to combine **design, mechanics, electronics, and software** into one functional device. The system intentionally mimics the behavior of a traditional record player:

* Placing the tonearm starts music playback and rotates the record.
* Lifting the tonearm pauses playback and stops the rotation.

Spotify starts automatically when the device is powered on, without requiring a keyboard, mouse, or screen interaction from the user.

---

## Features

* Automatic Spotify startup (Spotify Connect)
* Circular touch display showing album artwork
* Rotating vinyl record (ring construction)
* Mechanical tonearm used as play/pause control
* Quiet motor operation
* Integrated speakers
* Fully custom 3D-printed enclosure

---

## Technical Overview

### Core System

* Raspberry Pi Zero 2 W

### Display & Input

* Circular HDMI touch display
* Python-based UI and control logic

### Audio

* External DAC or USB sound card
* Amplifier and speakers

### Mechanics

* Real vinyl record modified into a rotating ring
* Bearing or turntable-style rotary mechanism for low noise
* Motor with friction wheel or belt drive

### Sensors

* Mechanical switch or Hall sensor to detect tonearm position

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
│   ├─ cad/
│   ├─ stl/
│   └─ schematics/
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
