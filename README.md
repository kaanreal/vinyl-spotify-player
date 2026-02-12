# Vinyl Spotify Player

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Raspberry%20Pi-lightgrey.svg)]()

A fun project that turns Spotify into a vinyl-like experience! Features a smooth rotating circular display with album artwork and a progress bar that matches your album colors.

**Try it on your computer first - no hardware needed!**

![Demo](docs/demo.gif)

## ✨ What It Does

- 🎨 **Rotating Album Art** - Smooth 60 FPS circular display that spins with your music
- 🌈 **Smart Colors** - Progress bar automatically matches your album artwork
- ⌨️ **Easy Controls** - Use your keyboard to control Spotify
- 🎵 **Full Spotify Integration** - Play, pause, skip tracks, adjust volume
- 🔄 **Smooth Animations** - Professional animations inspired by Apple's design

## 🚀 Quick Start (5 minutes)

### 1. Install

**Windows:**
```powershell
.\scripts\install.ps1
```

**Mac/Linux:**
```bash
chmod +x scripts/*.sh
./scripts/install.sh --pc
```

### 2. Setup Spotify

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add this redirect URI: `http://127.0.0.1:3000/callback`
4. Copy your Client ID and Client Secret
5. Edit `app/config/config.json` with your credentials

### 3. Connect Your Account

**Windows:**
```powershell
.\scripts\pair.ps1
```

**Mac/Linux:**
```bash
./scripts/pair.sh
```

This opens your browser to authorize the app.

### 4. Run It!

**Windows:**
```powershell
.\scripts\run-dev.ps1
```

**Mac/Linux:**
```bash
./scripts/run-dev.sh
```

A circular window appears showing your current Spotify track!

## 🎮 Controls

Use your keyboard to control playback:

| Key | Action |
|-----|--------|
| **SPACE** | Play/Pause |
| **LEFT/RIGHT** | Previous/Next Track |
| **UP/DOWN** | Volume Up/Down |
| **T** | Toggle Tonearm (simulates vinyl player arm) |
| **ESC** | Exit |

## 💡 How It Works

The app uses Spotify's Web API to:
1. Get your currently playing track
2. Download the album artwork
3. Extract a vibrant color for the progress bar
4. Rotate the artwork smoothly at 33 RPM (like a real vinyl record)
5. Show a circular progress bar around the edge

Everything runs at 60 FPS for buttery smooth animations!

## 🎓 For School Projects

This project demonstrates:
- **API Integration** - Spotify Web API with OAuth
- **UI/UX Design** - Smooth animations and responsive interface
- **Software Architecture** - Clean code structure with separation of concerns
- **Cross-Platform Development** - Works on Windows, Mac, Linux, and Raspberry Pi
- **Real-World Application** - Actual useful software you can use daily

## 📁 Project Structure

```
vinyl-spotify-player/
├── app/
│   ├── main.py           # Main application
│   ├── spotify/          # Spotify API integration
│   ├── ui/               # Display and animations  
│   └── config/           # Configuration files
├── scripts/              # Setup and run scripts
└── docs/                 # Documentation
```

## 🔧 Customization

Edit `app/config/config.json` to customize:
- **Display size** - Change `width` and `height`
- **FPS** - Adjust `fps` (30-60 recommended)
- **Rotation speed** - Change `target_rpm` (default: 33.3)
- **Keyboard shortcuts** - Modify `dev_mode` keys

## ❓ Common Issues

**"No active device found"**
- Make sure Spotify is playing on your phone or computer first

**"Invalid redirect URI"**
- Check that you added `http://127.0.0.1:3000/callback` exactly in Spotify Dashboard

**"No tokens found"**
- Run the pair script again: `./scripts/pair.ps1` or `./scripts/pair.sh`

**Album art not showing**
- Check your internet connection
- Look for errors in `data/logs/`

## 🤝 Contributing

Want to improve this project?
1. Fork it
2. Make your changes
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - Feel free to use for school projects, personal use, or learning!

## 🙏 Credits

- [Pygame](https://www.pygame.org/) - Game/UI library
- [Spotify Web API](https://developer.spotify.com/documentation/web-api) - Music control
- Built as a school/learning project

---

**Enjoy your vinyl Spotify experience! 🎵**
