# Frequently Asked Questions

## General Questions

**What is this project?**
A fun Spotify player that displays album art as a spinning vinyl record with smooth animations and a color-matched progress bar.

**Do I need Spotify Premium?**
Yes, Premium is required to control playback.

**Can I use it on my computer?**
Yes! Works on Windows, Mac, and Linux without any hardware.

## Setup

**How do I get started?**
1. Run the install script
2. Create a Spotify app at [developer.spotify.com](https://developer.spotify.com/dashboard)
3. Add your credentials to `config.json`
4. Run the pairing script
5. Launch the app!

**I get a "redirect error" when pairing**
Make sure your Spotify Dashboard has exactly: `http://127.0.0.1:3000/callback`

**Where are my login tokens stored?**
In `data/tokens/spotify_tokens.json` - they auto-refresh when needed.

## Using the App

**How do I control it?**
- **SPACE** - Play/Pause
- **LEFT/RIGHT** - Previous/Next track
- **UP/DOWN** - Volume
- **T** - Toggle tonearm animation
- **ESC** - Exit

**Can I change the window size?**
Yes! Edit `display.width` and `display.height` in `config.json`.

**The UI is laggy**
- Try lowering FPS in config (default is 60)
- Close other programs
- Check if your computer is under heavy load

**The UI is laggy**
- Try lowering FPS in config (default is 60)
- Close other programs
- Check if your computer is under heavy load

## Spotify Issues

**"No active device found"**
- Start playing Spotify on your phone or computer first
- The app needs an active Spotify session to control

**Playback doesn't start**
- Make sure you have Spotify Premium
- Re-run the pair script: `./scripts/pair.ps1` or `./scripts/pair.sh`
- Check logs in `data/logs/` for errors

**Can I control my phone's Spotify?**
Yes! The app can control any active Spotify device.

## Customization

**Can I change the rotation speed?**
Yes! Edit `motor.target_rpm` in `config.json` (default: 33.3 RPM like a real record).

**Can I choose the progress bar color?**
It automatically matches your album artwork! The code extracts the most vibrant color.

**Can I add my own animations?**
Yes! Check out `app/ui/display.py` and `app/ui/cover_rotation.py` to see how animations work.

## Troubleshooting

**"Invalid configuration" error**
Check that `config.json` has your Spotify Client ID and Secret filled in.

**"No module named XXX" error**
Run the install script again:
- Windows: `.\scripts\install.ps1`
- Mac/Linux: `./scripts/install.sh --pc`

**Album art not loading**
- Check your internet connection
- Look for errors in `data/logs/`

## For School Projects

**Album art not loading**
- Check your internet connection
- Look for errors in `data/logs/`

## For School Projects

**What does this project demonstrate?**
- API integration (Spotify Web API with OAuth)
- UI/UX design principles (smooth animations)
- Software architecture (organized code structure)
- Cross-platform development
- Real-world application development

**Can I modify it for my project?**
Absolutely! The code is open source (MIT License). Feel free to customize and extend it.

**What technologies does it use?**
- Python for the main application
- Pygame for graphics and UI
- Spotify Web API for music control
- OAuth 2.0 for authentication

## Contributing

**How can I help improve this?**
See [CONTRIBUTING.md](../CONTRIBUTING.md) - all contributions welcome!

**I found a bug**
Open an issue on GitHub with details about what went wrong.

**I have an idea for a feature**
Great! Open an issue to discuss it or submit a pull request.

---

**Still have questions?** Open an issue on GitHub!
