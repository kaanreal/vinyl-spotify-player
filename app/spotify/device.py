"""Spotify device management."""

from typing import Optional, Dict, Any
from app.spotify.api import SpotifyAPI
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class DeviceManager:
    """Manages Spotify playback devices."""
    
    def __init__(self, api: SpotifyAPI, preferred_device_name: str):
        """Initialize device manager.
        
        Args:
            api: Spotify API client
            preferred_device_name: Name of preferred device (e.g., 'raspotify')
        """
        self.api = api
        self.preferred_device_name = preferred_device_name
        self._active_device_id = None
    
    def get_active_device(self) -> Optional[Dict[str, Any]]:
        """Get the currently active device.
        
        Returns:
            Optional[dict]: Active device info, or None if no active device
        """
        devices = self.api.get_devices()
        
        for device in devices:
            if device.get('is_active'):
                self._active_device_id = device['id']
                return device
        
        return None
    
    def find_preferred_device(self) -> Optional[Dict[str, Any]]:
        """Find the preferred device by name.
        
        Returns:
            Optional[dict]: Preferred device info, or None if not found
        """
        devices = self.api.get_devices()
        
        for device in devices:
            if device['name'].lower() == self.preferred_device_name.lower():
                return device
        
        return None
    
    def ensure_playback_on_preferred_device(self) -> bool:
        """Ensure playback is on the preferred device.
        
        If the preferred device is available but not active, transfers playback to it.
        
        Returns:
            bool: True if preferred device is active or transfer successful
        """
        active = self.get_active_device()
        
        # Check if already on preferred device
        if active and active['name'].lower() == self.preferred_device_name.lower():
            logger.debug(f"Already playing on preferred device: {self.preferred_device_name}")
            return True
        
        # Try to find and transfer to preferred device
        preferred = self.find_preferred_device()
        if preferred:
            logger.info(f"Transferring playback to {self.preferred_device_name}")
            return self.api.transfer_playback(preferred['id'], force_play=False)
        
        # Preferred device not found
        if active:
            logger.warning(
                f"Preferred device '{self.preferred_device_name}' not found. "
                f"Using active device: {active['name']}"
            )
            self._active_device_id = active['id']
            return True
        else:
            logger.warning(
                f"No active device found and preferred device '{self.preferred_device_name}' unavailable"
            )
            return False
    
    def get_current_device_id(self) -> Optional[str]:
        """Get the current active device ID.
        
        Returns:
            Optional[str]: Device ID, or None
        """
        active = self.get_active_device()
        return active['id'] if active else None
