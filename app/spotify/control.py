"""High-level Spotify playback control."""

from typing import Optional, Dict, Any, Callable
import time
import threading
from app.spotify.api import SpotifyAPI
from app.spotify.device import DeviceManager
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class PlaybackController:
    """High-level Spotify playback controller."""
    
    def __init__(self, api: SpotifyAPI, device_manager: DeviceManager, poll_interval_ms: int = 1000):
        """Initialize playback controller.
        
        Args:
            api: Spotify API client
            device_manager: Device manager
            poll_interval_ms: Polling interval for playback state
        """
        self.api = api
        self.device_manager = device_manager
        self.poll_interval = poll_interval_ms / 1000.0
        
        self._current_state = None
        self._is_polling = False
        self._state_callbacks = []
        self._last_track_uri = None
    
    def add_state_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback for playback state updates.
        
        Args:
            callback: Function to call with playback state dict
        """
        self._state_callbacks.append(callback)
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get the most recent playback state.
        
        Returns:
            Optional[dict]: Current playback state
        """
        return self._current_state
    
    def _refresh_state_now(self) -> None:
        """Force an immediate state refresh (non-blocking)."""
        def refresh():
            try:
                state = self.api.get_current_playback()
                if state:
                    parsed_state = self._parse_state(state)
                    self._current_state = parsed_state
                    # Notify callbacks
                    for callback in self._state_callbacks:
                        try:
                            callback(parsed_state)
                        except Exception as e:
                            logger.error(f"State callback error: {e}")
            except Exception as e:
                logger.debug(f"Immediate refresh error: {e}")
        
        # Run in background thread to not block
        threading.Thread(target=refresh, daemon=True).start()
    
    def is_playing(self) -> bool:
        """Check if currently playing.
        
        Returns:
            bool: True if playing
        """
        if self._current_state is None:
            return False
        return self._current_state.get('is_playing', False)
    
    def play(self) -> bool:
        """Resume playback.
        
        Returns:
            bool: True if successful
        """
        device_id = self.device_manager.get_current_device_id()
        result = self.api.play(device_id=device_id)
        if result:
            # Trigger immediate state update for instant feedback
            self._refresh_state_now()
        return result
    
    def pause(self) -> bool:
        """Pause playback.
        
        Returns:
            bool: True if successful
        """
        device_id = self.device_manager.get_current_device_id()
        result = self.api.pause(device_id=device_id)
        if result:
            # Trigger immediate state update for instant feedback
            self._refresh_state_now()
        return result
    
    def toggle_playback(self) -> bool:
        """Toggle between play and pause.
        
        Returns:
            bool: True if successful
        """
        if self.is_playing():
            return self.pause()
        else:
            return self.play()
    
    def next(self) -> bool:
        """Skip to next track.
        
        Returns:
            bool: True if successful
        """
        device_id = self.device_manager.get_current_device_id()
        result = self.api.next_track(device_id=device_id)
        if result:
            # Trigger immediate state update for instant feedback
            self._refresh_state_now()
        return result
    
    def previous(self) -> bool:
        """Skip to previous track.
        
        Returns:
            bool: True if successful
        """
        device_id = self.device_manager.get_current_device_id()
        result = self.api.previous_track(device_id=device_id)
        if result:
            # Trigger immediate state update for instant feedback
            self._refresh_state_now()
        return result
    
    def adjust_volume(self, delta: int) -> bool:
        """Adjust volume by delta.
        
        Args:
            delta: Volume change (-100 to +100)
            
        Returns:
            bool: True if successful
        """
        if self._current_state is None:
            return False
        
        device = self._current_state.get('device', {})
        current_volume = device.get('volume_percent', 50)
        new_volume = max(0, min(100, current_volume + delta))
        
        device_id = self.device_manager.get_current_device_id()
        return self.api.set_volume(new_volume, device_id=device_id)
    
    def start_polling(self) -> None:
        """Start polling for playback state updates."""
        if self._is_polling:
            return
        
        self._is_polling = True
        
        def poll_loop():
            logger.info("Started Spotify state polling")
            
            while self._is_polling:
                try:
                    # Get current playback state
                    state = self.api.get_current_playback()
                    
                    if state:
                        # Extract relevant information
                        parsed_state = self._parse_state(state)
                        
                        # Check for track changes
                        current_uri = parsed_state.get('track_uri')
                        if current_uri != self._last_track_uri:
                            if current_uri:
                                logger.info(f"Now playing: {parsed_state.get('track_name')} - {parsed_state.get('artist_name')}")
                            self._last_track_uri = current_uri
                        
                        self._current_state = parsed_state
                        
                        # Notify callbacks
                        for callback in self._state_callbacks:
                            try:
                                callback(parsed_state)
                            except Exception as e:
                                logger.error(f"State callback error: {e}")
                    else:
                        # No active playback
                        if self._current_state is not None:
                            logger.info("Playback stopped")
                        self._current_state = None
                    
                    # Ensure on preferred device periodically
                    self.device_manager.ensure_playback_on_preferred_device()
                
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                
                time.sleep(self.poll_interval)
        
        self._poll_thread = threading.Thread(target=poll_loop, daemon=True)
        self._poll_thread.start()
    
    def stop_polling(self) -> None:
        """Stop polling for playback state updates."""
        self._is_polling = False
        if hasattr(self, '_poll_thread'):
            self._poll_thread.join(timeout=2.0)
        logger.info("Stopped Spotify state polling")
    
    def _parse_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API state into simplified format.
        
        Args:
            state: Raw API playback state
            
        Returns:
            dict: Simplified playback state
        """
        item = state.get('item', {})
        
        # Get artists
        artists = item.get('artists', [])
        artist_names = ', '.join(artist['name'] for artist in artists)
        
        # Get album art
        album = item.get('album', {})
        images = album.get('images', [])
        album_art_url = images[0]['url'] if images else None
        
        return {
            'is_playing': state.get('is_playing', False),
            'track_name': item.get('name', 'Unknown'),
            'artist_name': artist_names or 'Unknown',
            'album_name': album.get('name', 'Unknown'),
            'album_art_url': album_art_url,
            'track_uri': item.get('uri'),
            'progress_ms': state.get('progress_ms', 0),
            'duration_ms': item.get('duration_ms', 0),
            'device_name': state.get('device', {}).get('name', 'Unknown'),
            'volume_percent': state.get('device', {}).get('volume_percent', 0),
        }
