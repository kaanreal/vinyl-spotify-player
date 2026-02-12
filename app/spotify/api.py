"""Spotify Web API client."""

import requests
from typing import Optional, Dict, Any
from app.spotify.tokens import TokenManager
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class SpotifyAPI:
    """Spotify Web API client."""
    
    BASE_URL = 'https://api.spotify.com/v1'
    
    def __init__(self, token_manager: TokenManager):
        """Initialize Spotify API client.
        
        Args:
            token_manager: Token manager instance
        """
        self.token_manager = token_manager
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers.
        
        Returns:
            dict: Headers with authorization token
        """
        access_token = self.token_manager.get_access_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
    
    def get_current_playback(self) -> Optional[Dict[str, Any]]:
        """Get current playback state.
        
        Returns:
            Optional[dict]: Playback state, or None if nothing playing
        """
        url = f'{self.BASE_URL}/me/player'
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 204:
                # No content - nothing playing
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to get playback state: {e}")
            return None
    
    def get_currently_playing(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track.
        
        Returns:
            Optional[dict]: Currently playing track info, or None
        """
        url = f'{self.BASE_URL}/me/player/currently-playing'
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 204:
                # No content - nothing playing
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to get currently playing: {e}")
            return None
    
    def play(self, device_id: Optional[str] = None) -> bool:
        """Resume playback.
        
        Args:
            device_id: Optional device ID to play on
            
        Returns:
            bool: True if successful
        """
        url = f'{self.BASE_URL}/me/player/play'
        
        params = {}
        if device_id:
            params['device_id'] = device_id
        
        try:
            response = requests.put(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            logger.debug("Playback resumed")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to resume playback: {e}")
            return False
    
    def pause(self, device_id: Optional[str] = None) -> bool:
        """Pause playback.
        
        Args:
            device_id: Optional device ID to pause on
            
        Returns:
            bool: True if successful
        """
        url = f'{self.BASE_URL}/me/player/pause'
        
        params = {}
        if device_id:
            params['device_id'] = device_id
        
        try:
            response = requests.put(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            logger.debug("Playback paused")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to pause playback: {e}")
            return False
    
    def next_track(self, device_id: Optional[str] = None) -> bool:
        """Skip to next track.
        
        Args:
            device_id: Optional device ID
            
        Returns:
            bool: True if successful
        """
        url = f'{self.BASE_URL}/me/player/next'
        
        params = {}
        if device_id:
            params['device_id'] = device_id
        
        try:
            response = requests.post(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            logger.debug("Skipped to next track")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to skip track: {e}")
            return False
    
    def previous_track(self, device_id: Optional[str] = None) -> bool:
        """Skip to previous track.
        
        Args:
            device_id: Optional device ID
            
        Returns:
            bool: True if successful
        """
        url = f'{self.BASE_URL}/me/player/previous'
        
        params = {}
        if device_id:
            params['device_id'] = device_id
        
        try:
            response = requests.post(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            logger.debug("Skipped to previous track")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to go to previous track: {e}")
            return False
    
    def set_volume(self, volume_percent: int, device_id: Optional[str] = None) -> bool:
        """Set playback volume.
        
        Args:
            volume_percent: Volume level (0-100)
            device_id: Optional device ID
            
        Returns:
            bool: True if successful
        """
        volume_percent = max(0, min(100, volume_percent))
        url = f'{self.BASE_URL}/me/player/volume'
        
        params = {'volume_percent': volume_percent}
        if device_id:
            params['device_id'] = device_id
        
        try:
            response = requests.put(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            logger.debug(f"Volume set to {volume_percent}%")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def get_devices(self) -> list:
        """Get available playback devices.
        
        Returns:
            list: List of available devices
        """
        url = f'{self.BASE_URL}/me/player/devices'
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('devices', [])
        
        except requests.RequestException as e:
            logger.error(f"Failed to get devices: {e}")
            return []
    
    def transfer_playback(self, device_id: str, force_play: bool = False) -> bool:
        """Transfer playback to a specific device.
        
        Args:
            device_id: Device ID to transfer to
            force_play: Whether to ensure playback starts
            
        Returns:
            bool: True if successful
        """
        url = f'{self.BASE_URL}/me/player'
        
        data = {
            'device_ids': [device_id],
            'play': force_play,
        }
        
        try:
            response = requests.put(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            logger.info(f"Playback transferred to device {device_id}")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to transfer playback: {e}")
            return False
