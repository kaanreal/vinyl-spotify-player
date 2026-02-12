"""Metadata manager for polling Spotify currently playing track."""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from spotify_client import SpotifyClient


@dataclass
class TrackInfo:
    """Current track information."""
    track_id: str
    track_name: str
    artists: str
    album: str
    album_art_url: str
    progress_ms: int
    duration_ms: int
    is_playing: bool
    
    def __eq__(self, other) -> bool:
        """Check if track info is equal (same track)."""
        if not isinstance(other, TrackInfo):
            return False
        return self.track_id == other.track_id


class MetadataManager:
    """Manage metadata polling and change detection."""
    
    def __init__(self, spotify_client: SpotifyClient, poll_interval: float = 1.0):
        """Initialize metadata manager.
        
        Args:
            spotify_client: Spotify API client
            poll_interval: Polling interval in seconds
        """
        self.spotify = spotify_client
        self.poll_interval = poll_interval
        self.current_track: Optional[TrackInfo] = None
        self.last_poll_time: float = 0
    
    def _extract_track_info(self, data: Dict[str, Any]) -> Optional[TrackInfo]:
        """Extract track info from API response.
        
        Args:
            data: API response data
        
        Returns:
            TrackInfo object or None
        """
        if not data or 'item' not in data:
            return None
        
        item = data['item']
        if not item or item.get('type') != 'track':
            return None
        
        try:
            # Extract artists
            artists = ', '.join([artist['name'] for artist in item['artists']])
            
            # Extract album art (prefer largest image)
            album_images = item['album'].get('images', [])
            album_art_url = album_images[0]['url'] if album_images else ''
            
            return TrackInfo(
                track_id=item['id'],
                track_name=item['name'],
                artists=artists,
                album=item['album']['name'],
                album_art_url=album_art_url,
                progress_ms=data.get('progress_ms', 0),
                duration_ms=item['duration_ms'],
                is_playing=data.get('is_playing', False)
            )
        except (KeyError, TypeError) as e:
            print(f"Error extracting track info: {e}")
            return None
    
    def poll(self) -> Optional[TrackInfo]:
        """Poll for current track info.
        
        Returns:
            TrackInfo if available, None otherwise
        """
        current_time = time.time()
        
        # Respect poll interval
        if current_time - self.last_poll_time < self.poll_interval:
            return self.current_track
        
        self.last_poll_time = current_time
        
        try:
            # Get currently playing track
            data = self.spotify.get_currently_playing()
            
            if not data:
                # Nothing playing
                if self.current_track:
                    print("Playback stopped")
                self.current_track = None
                return None
            
            new_track = self._extract_track_info(data)
            
            if not new_track:
                return self.current_track
            
            # Check if track changed
            if self.current_track is None or new_track != self.current_track:
                print(f"Now playing: {new_track.track_name} by {new_track.artists}")
                self.current_track = new_track
            else:
                # Update progress and playing state
                self.current_track.progress_ms = new_track.progress_ms
                self.current_track.is_playing = new_track.is_playing
            
            return self.current_track
            
        except requests.exceptions.RequestException as e:
            print(f"Network error polling metadata: {e}")
            return self.current_track
        except Exception as e:
            print(f"Error polling metadata: {e}")
            return self.current_track
    
    def has_track_changed(self) -> bool:
        """Check if track has changed since last poll.
        
        Returns:
            True if track changed
        """
        old_track = self.current_track
        new_track = self.poll()
        
        if old_track is None and new_track is None:
            return False
        
        if old_track is None or new_track is None:
            return True
        
        return old_track.track_id != new_track.track_id
