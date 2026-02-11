"""Configuration settings for Vinyl Spotify Player."""

import os
from pathlib import Path

DISPLAY_WIDTH: int = 480
DISPLAY_HEIGHT: int = 480
DISPLAY_FPS: int = 30

ALBUM_ART_SIZE: int = 400
ALBUM_ART_CACHE_DIR: Path = Path.home() / ".cache" / "vinyl-player" / "album-art"
ALBUM_ART_CACHE_DIR.mkdir(parents=True, exist_ok=True)

TONEARM_GPIO_PIN: int = 17
TONEARM_DEBOUNCE_TIME: float = 0.5

MPRIS_BUS_NAME: str = "org.mpris.MediaPlayer2.raspotify"
MPRIS_OBJECT_PATH: str = "/org/mpris/MediaPlayer2"
MPRIS_PLAYER_INTERFACE: str = "org.mpris.MediaPlayer2.Player"
MPRIS_PROPERTIES_INTERFACE: str = "org.freedesktop.DBus.Properties"

POLL_INTERVAL: float = 0.5

BACKGROUND_COLOR: tuple[int, int, int] = (20, 20, 20)
TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)
ACCENT_COLOR: tuple[int, int, int] = (30, 215, 96)
PROGRESS_BG_COLOR: tuple[int, int, int] = (80, 80, 80)

FONT_TITLE_SIZE: int = 28
FONT_ARTIST_SIZE: int = 22
FONT_TIME_SIZE: int = 18

DEFAULT_ALBUM_ART_COLOR: tuple[int, int, int] = (60, 60, 60)

ENABLE_TONEARM_GPIO: bool = True
