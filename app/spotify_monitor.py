"""Monitor Spotify playback via MPRIS DBus interface."""

import time
from typing import Optional, Dict, Any
import logging

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    logging.warning("DBus not available - running in mock mode")

from config import (
    MPRIS_BUS_NAME,
    MPRIS_OBJECT_PATH,
    MPRIS_PLAYER_INTERFACE,
    MPRIS_PROPERTIES_INTERFACE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrackInfo:
    """Container for current track information."""
    
    def __init__(self) -> None:
        self.title: str = "No Track Playing"
        self.artist: str = ""
        self.album: str = ""
        self.album_art_url: str = ""
        self.duration_us: int = 0
        self.position_us: int = 0
        self.is_playing: bool = False
        self.track_id: str = ""
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackInfo):
            return False
        return self.track_id == other.track_id and self.is_playing == other.is_playing
    
    @property
    def duration_seconds(self) -> float:
        return self.duration_us / 1_000_000.0
    
    @property
    def position_seconds(self) -> float:
        return self.position_us / 1_000_000.0
    
    @property
    def progress(self) -> float:
        if self.duration_us > 0:
            return min(1.0, self.position_us / self.duration_us)
        return 0.0


class SpotifyMonitor:
    """Monitor Spotify playback status via MPRIS DBus."""
    
    def __init__(self) -> None:
        self.bus: Optional[Any] = None
        self.player: Optional[Any] = None
        self.properties: Optional[Any] = None
        self.last_position_update: float = 0.0
        self.estimated_position_us: int = 0
        self._connect()
    
    def _connect(self) -> None:
        """Connect to DBus and get player interface."""
        if not DBUS_AVAILABLE:
            logger.warning("DBus not available")
            return
        
        try:
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SessionBus()
            
            proxy = self.bus.get_object(MPRIS_BUS_NAME, MPRIS_OBJECT_PATH)
            self.player = dbus.Interface(proxy, MPRIS_PLAYER_INTERFACE)
            self.properties = dbus.Interface(proxy, MPRIS_PROPERTIES_INTERFACE)
            logger.info("Connected to Raspotify via DBus")
        except dbus.DBusException as e:
            logger.error(f"Failed to connect to DBus: {e}")
            self.player = None
            self.properties = None
    
    def get_track_info(self) -> TrackInfo:
        """Get current track information."""
        track_info = TrackInfo()
        
        if not self.properties:
            self._connect()
            if not self.properties:
                return track_info
        
        try:
            metadata = self.properties.Get(MPRIS_PLAYER_INTERFACE, "Metadata")
            playback_status = self.properties.Get(MPRIS_PLAYER_INTERFACE, "PlaybackStatus")
            position = self.properties.Get(MPRIS_PLAYER_INTERFACE, "Position")
            
            if metadata:
                track_info.title = str(metadata.get("xesam:title", "Unknown Title"))
                
                artists = metadata.get("xesam:artist")
                if artists and len(artists) > 0:
                    track_info.artist = str(artists[0])
                
                track_info.album = str(metadata.get("xesam:album", ""))
                
                art_url = metadata.get("mpris:artUrl", "")
                track_info.album_art_url = str(art_url)
                
                track_id = metadata.get("mpris:trackid", "")
                track_info.track_id = str(track_id)
                
                length = metadata.get("mpris:length", 0)
                track_info.duration_us = int(length)
            
            track_info.is_playing = str(playback_status) == "Playing"
            track_info.position_us = int(position)
            
            self.last_position_update = time.time()
            self.estimated_position_us = track_info.position_us
            
        except dbus.DBusException as e:
            logger.error(f"Error getting track info: {e}")
            self._connect()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        return track_info
    
    def get_estimated_position(self, track_info: TrackInfo) -> int:
        """Estimate current position based on last update and playback status."""
        if track_info.is_playing:
            elapsed_since_update = time.time() - self.last_position_update
            estimated = self.estimated_position_us + int(elapsed_since_update * 1_000_000)
            return min(estimated, track_info.duration_us)
        return self.estimated_position_us
    
    def play_pause(self) -> None:
        """Toggle play/pause."""
        if not self.player:
            logger.warning("Player interface not available")
            return
        
        try:
            self.player.PlayPause()
            logger.info("Toggled play/pause")
        except dbus.DBusException as e:
            logger.error(f"Failed to toggle play/pause: {e}")
            self._connect()
