## 🎵 Feature: 3D Model, Pi Runtime Scaffold, and Project Cleanup

### Summary

This PR adds the initial 3D model for the custom enclosure, implements a Pi runtime scaffold with state machine architecture, and performs comprehensive cleanup and formatting improvements across the entire project.

### Changes

#### 🖨️ 3D Asset
- **Added** `hardware/3d-models/3d-model.stl` — 3D model file for custom enclosure
- **Renamed** `hardware/3D filez/` → `hardware/3d-models/` for consistent naming
- **Removed** placeholder files (`idk.yet`)

#### 💻 Software Implementation
- **Added** `software/pi/main.py` — Runtime state machine scaffold with:
  - State management (IDLE, PLAYING, PAUSED, ERROR)
  - Deterministic state transitions
  - Logging and signal handling
- **Added** `software/pi/motor.py` — Motor controller abstraction layer
- **Added** `software/pi/display.py` — Display abstraction layer
- **Added** `software/install/setup.sh` — Pi bootstrap script that:
  - Installs Python dependencies
  - Syncs project to `/opt/vinyl-spotify-player`
  - Creates systemd service for auto-startup

#### 📄 Documentation
- **Added** `docs/concept.md` — Architecture overview with:
  - UX goals and design philosophy
  - Runtime components breakdown
  - State machine flow
  - Milestone plan (6 phases)
- **Added** `docs/wiring.md` — Technical wiring guide with:
  - Power distribution diagram
  - GPIO mapping (Pi Zero 2 W)
  - Audio routing
  - Safety notes
- **Updated** `README.md` with:
  - 🎨 Emoji-led sections for better readability
  - 📂 Updated repository structure
  - 🎯 Added "Next Steps" section with clear TODO items
  - ✅ Clean formatting with consistent headings and lists

#### 🧹 Cleanup & Formatting
- **Renamed** directory: `3D filez/` → `3d-models/` (standard naming convention)
- **Removed** all placeholder files (empty `idk.yet` files)
- **Standardized** file naming throughout the project
- **Verified** all documentation files are properly formatted

### 📋 Files Changed

- `README.md` — Major formatting and content improvements
- `docs/concept.md` — New architecture documentation
- `docs/wiring.md` — New technical wiring guide
- `hardware/3d-models/` — Renamed from `3D filez/`
- `hardware/3d-models/3d-model.stl` — New 3D model added
- `software/pi/main.py` — New runtime state machine
- `software/pi/motor.py` — New motor controller
- `software/pi/display.py` — New display controller
- `software/install/setup.sh` — New installation script

### ✅ Testing

All project files verified to be:
- ✅ Properly formatted with consistent markdown
- ✅ Following standard naming conventions
- ✅ Well-documented with clear sections
- ✅ Ready for continued development

### 🔍 Notes

This PR establishes a clean foundation for the project going forward. The new runtime scaffold enables the next phase of development (GPIO integration, motor control, Spotify API). The 3D model enables physical enclosure development.

---

## 📊 Type of Change

- [x] Documentation
- [x] Asset addition
- [x] New feature implementation
- [x] Code cleanup/formatting

---

## 🎯 Checklist

- [x] Added 3D model asset
- [x] Implemented Pi runtime scaffold
- [x] Added installation script
- [x] Cleaned up project structure
- [x] Formatted and improved README
- [x] Standardized directory naming
- [x] Added technical documentation
- [ ] Review and merge
