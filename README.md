# 🎵 Vinyl Spotify Player

> A custom-built Spotify player designed to look and behave like a classic turntable. A real vinyl record rotates around a fixed circular display that shows the current album artwork. Playback is controlled using a mechanical tonearm, similar to a real record player.

---

## 💡 Project Idea

The goal of this school technology project is to combine **design, mechanics, electronics, and software** into one functional device. The system intentionally mimics the behavior of a traditional record player:

- 🎛️ **Placing the tonearm** starts music playback and rotates the record.
- ⏸️ **Lifting the tonearm** pauses playback and stops the rotation.

Spotify starts automatically when the device is powered on, without requiring a keyboard, mouse, or screen interaction from the user.

---

## ✨ Features

- 🚀 **Automatic Spotify startup** (Spotify Connect)
- 🖥️ **Circular touch display** showing album artwork
- 🔄 **Rotating vinyl record** (ring construction)
- 🎛️ **Mechanical tonearm** used as play/pause control
- 🔊 **Quiet motor operation**
- 🔈 **Integrated speakers**
- 🖨️ **Fully custom 3D-printed enclosure**

---

## 🛠️ Bill of Materials (BOM)

### Core
- **Raspberry Pi Zero 2 W**
- **microSD card** (16–32 GB)

### Display
- **Round HDMI IPS display** (≈2.8", 480×480)

### Audio
- **USB sound card**
- **PAM8403 audio amplifier** (2×3 W)
- **2× speakers** (4 Ω, 3–5 W, 40–50 mm)

### Mechanics
- **12" vinyl record** (used as rotating ring)
- **Custom subplatter / subplate** (~210 mm)
- **608ZZ ball bearing** (8×22×7 mm)
- **DC gear motor JGA25-370** (12 V, ~30 RPM)
- **GT2 pulley** (20T, 5 mm bore, no flange)
- **Rubber O-ring belt** (Ø 170–180 mm)

### Control & Sensors
- **Rotary encoder** (EC11)
- **Hall effect sensor** (A3144)
- **Neodymium magnet** (~6×3 mm)

### Power
- **12 V power supply**
- **Buck converter** (12 V → 5 V)

### Misc
- Wires, screws, spacers
- Custom 3D-printed enclosure parts

---

## 📂 Repository Structure

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
│   └─ 3d-models/
│       └─ 3d-model.stl
│
└─ software/
   ├─ pi/
   │   ├─ main.py
   │   ├─ motor.py
   │   └─ display.py
   └─ install/
       └─ setup.sh
```

----

## 🔄 Operation Flow

1. 🔌 **Power is connected**
2. 💻 **Raspberry Pi boots automatically**
3. 🎵 **Spotify Connect service starts**
4. 📱 **Device appears instantly** as a playback device in Spotify
5. 🎛️ **Placing the tonearm** starts playback and rotation
6. ⏸️ **Lifting the tonearm** pauses playback and stops rotation

---

## ⚡ Quick Start (Raspberry Pi)

```bash
cd software/install
chmod +x setup.sh
./setup.sh
```

The setup script installs dependencies, syncs the project to `/opt/vinyl-spotify-player`, and creates a systemd service named `vinyl-spotify-player`.

---

## 📋 Project Status

**Work in progress** (school project)

### ✅ Implemented Starter Files

- `software/pi/main.py` — Runtime state machine scaffold
- `software/pi/motor.py` — Motor controller abstraction
- `software/pi/display.py` — Display abstraction
- `software/install/setup.sh` — Pi bootstrap + service installer
- `docs/concept.md` — Architecture + milestones
- `docs/wiring.md` — Initial wiring map + safety notes
- `hardware/3d-models/3d-model.stl` — 3D model for custom enclosure

---

## 🎯 Next Steps

- [ ] Implement real GPIO/Hall sensor integration
- [ ] Add PWM motor control with smooth acceleration
- [ ] Integrate circular display with album art
- [ ] Connect Spotify API for playback control
- [ ] Build and test enclosure with 3D-printed parts
- [ ] Add thermal and power monitoring
- [ ] Polish error handling and retry logic

---

## 📄 License

This project is open for educational purposes. Feel free to fork and modify.
