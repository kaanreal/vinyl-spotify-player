# How It Works

This document explains how the Vinyl Spotify Player is built and how the different parts work together.

## Main Idea

The app has three main parts:
1. **Spotify API** - Talks to Spotify to control music and get track info
2. **Display** - Shows the spinning album art and progress bar  
3. **Controls** - Handles keyboard input (or hardware on Raspberry Pi)

## File Structure

```
app/
├── main.py              # Starts everything up
├── spotify/             # Talks to Spotify API
│   ├── oauth_pair.py    # Logs you into Spotify
│   ├── tokens.py        # Manages your login tokens
│   ├── api.py           # Sends requests to Spotify
│   └── control.py       # High-level controls (play, pause, etc.)
├── ui/                  # Visual stuff
│   ├── display.py       # Main window and graphics
│   ├── cover_rotation.py # Makes the album art spin
│   └── artwork_cache.py  # Downloads and saves album art
└── config/              # Settings
    └── config.json      # Configuration file
```

## How It Works

### 1. Starting Up

When you run the app:
1. Loads settings from `config.json`
2. Checks if you have valid Spotify login tokens
3. Creates the pygame window (480x480 pixels)
4. Starts checking Spotify every 100ms for updates

### 2. Spotify Integration

**Getting Track Info:**
- Every 100ms, asks Spotify "what's playing?"
- Gets: song name, artist, album art URL, play/pause state, progress

**Controlling Playback:**
- When you press SPACE, sends play/pause command to Spotify
- When you press LEFT/RIGHT, sends previous/next command
- Immediately checks for updates after each command

**Authentication:**
- Uses OAuth 2.0 (like "Sign in with Spotify")
- Stores tokens in `data/tokens/` for reuse
- Auto-refreshes expired tokens

### 3. Display & Graphics

**The Window:**
- 480x480 pixel square window
- Everything drawn inside is masked to a circle
- Runs at 60 FPS for smooth animation

**Drawing Steps (each frame):**
1. Clear to black background
2. Draw the album artwork (rotated based on playback)
3. Apply circular mask to make it round
4. Draw the progress bar around the edge
5. Draw text (song name, artist)
6. Update the display

**The Spinning Animation:**
- When playing: spins at 33.3 RPM (like a real vinyl record)
- When paused: gradually slows to a stop
- Uses "easing" for smooth acceleration/deceleration
- Rotation angle updates based on time elapsed

**The Progress Bar:**
- Draws a circular ring around the album art
- Color extracted from the album artwork
- Finds the most vibrant/saturated color
- Shows how far through the song you are

### 4. Album Artwork

**Downloading:**
- When a new song starts, gets the artwork URL from Spotify
- Downloads it in the background (doesn't freeze the UI)
- Saves it to `data/cache/` so it doesn't re-download

**Processing:**
- Loads the image
- Resizes to fit the display
- Applies rotation transform
- Analyzes colors for progress bar

## Key Concepts

### Delta Time
Instead of counting frames, we measure actual time. This means:
- Animations look the same on fast and slow computers
- 60 FPS on fast PC, 30 FPS on slow PC, but same speed

### Smooth Animations
Uses "easing functions" (math that makes motion look natural):
- Fast at the start, slow at the end (ease-out)
- Slow at start, fast in middle, slow at end (ease-in-out)
- Like how a car accelerates smoothly, not instantly

### Color Extraction
To get the progress bar color:
1. Look at all pixels in the album art
2. Convert RGB to HSV (Hue, Saturation, Value)
3. Find the most saturated (vibrant) color
4. Boost saturation 20% to make it pop
5. Use that for the progress bar

## Configuration

Everything is customizable in `config.json`:

```json
{
  "display": {
    "fps": 60,              // How many frames per second
    "width": 480,           // Window width
    "height": 480           // Window height
  },
  "polling": {
    "spotify_state_interval_ms": 100  // Check Spotify every 100ms
  },
  "motor": {
    "target_rpm": 33.3      // Rotation speed (33.3 = vinyl LP speed)
  },
  "transition": {
    "duration_seconds": 0.3  // How long transitions take
  }
}
```

## What Happens When...

**You press SPACE:**
1. Keyboard event captured
2. Sends play/pause toggle to Spotify API
3. Immediately refreshes current state
4. Updates rotation animation
5. Updates display

**A new song starts:**
1. Poll detects track changed
2. Downloads new album artwork
3. Extracts progress bar color
4. Crossfades to new artwork
5. Resets progress bar to 0%

**You close the app:**
1. pygame window closes
2. Stops polling thread
3. Saves any pending data
4. Clean exit

## For Your School Project

This architecture demonstrates:
- **API Integration** - OAuth authentication, REST API calls
- **Event-Driven Programming** - Callbacks and listeners
- **Animation** - Delta-time, easing functions
- **Threading** - Background tasks without blocking UI
- **Caching** - Smart data storage to reduce network calls
- **Abstraction** - Clean separation between components

## Want to Add Features?

**Easy:**
- Add more keyboard shortcuts in `display.py`
- Change colors/sizes in config
- Add text displays (lyrics, time remaining)

**Medium:**
- Add new animations (bouncing, pulsing)
- Support playlists
- Add visualizers

**Advanced:**
- Hardware integration (LEDs, motors)
- Web interface for remote control
- Multi-room synchronization

---

**Questions?** Check [FAQ.md](FAQ.md) or [CONTRIBUTING.md](../CONTRIBUTING.md)
