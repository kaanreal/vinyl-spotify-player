"""Spotify Web API client with automatic token refresh."""

import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests


class SpotifyClient:
    """Spotify Web API client with OAuth token management."""

    API_BASE = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: str, client_secret: str, tokens_path: Path):
        """Initialize the Spotify client.
        
        Args:
            client_id: Spotify application client ID.
            client_secret: Spotify application client secret.
            tokens_path: Path to the tokens JSON file.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tokens_path = tokens_path
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: float = 0
        
        self._load_tokens()
    
    def _load_tokens(self) -> None:
        """Load tokens from file."""
        if not self.tokens_path.exists():
            raise FileNotFoundError(
                f"Tokens file not found: {self.tokens_path}\n"
                f"Please run oauth_pair.py first to authorize the application."
            )
        
        with open(self.tokens_path, 'r') as f:
            tokens = json.load(f)
        
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")
        self.expires_at = tokens.get("expires_at", 0)
    
    def _save_tokens(self) -> None:
        """Save tokens to file."""
        tokens = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at
        }
        
        with open(self.tokens_path, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def _refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.expires_at = time.time() + token_data["expires_in"]
        
        # Refresh token may be updated
        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]
        
        self._save_tokens()
    
    def _ensure_valid_token(self) -> None:
        """Ensure the access token is valid, refreshing if necessary."""
        if time.time() >= self.expires_at - 60:  # Refresh 1 minute before expiry
            self._refresh_access_token()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        self._ensure_valid_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_current_playback(self) -> Optional[Dict[str, Any]]:
        """Get current playback state.
        
        Returns:
            Playback state dictionary or None if nothing is playing.
        """
        url = f"{self.API_BASE}/me/player"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 204:
                # No content - nothing playing
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            print(f"Error fetching playback state: {e}")
            return None
    
    def get_currently_playing(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track.
        
        Returns:
            Currently playing track data or None.
        """
        url = f"{self.API_BASE}/me/player/currently-playing"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 204:
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            print(f"Error fetching currently playing: {e}")
            return None
    
    def play(self, device_id: Optional[str] = None) -> bool:
        """Start or resume playback.
        
        Args:
            device_id: Optional device ID to target.
        
        Returns:
            True if successful, False otherwise.
        """
        url = f"{self.API_BASE}/me/player/play"
        
        if device_id:
            url += f"?device_id={device_id}"
        
        try:
            response = requests.put(url, headers=self._get_headers())
            
            if response.status_code in (204, 202):
                return True
            
            response.raise_for_status()
            return True
        
        except requests.RequestException as e:
            print(f"Error starting playback: {e}")
            return False
    
    def pause(self, device_id: Optional[str] = None) -> bool:
        """Pause playback.
        
        Args:
            device_id: Optional device ID to target.
        
        Returns:
            True if successful, False otherwise.
        """
        url = f"{self.API_BASE}/me/player/pause"
        
        if device_id:
            url += f"?device_id={device_id}"
        
        try:
            response = requests.put(url, headers=self._get_headers())
            
            if response.status_code in (204, 202):
                return True
            
            response.raise_for_status()
            return True
        
        except requests.RequestException as e:
            print(f"Error pausing playback: {e}")
            return False
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get available devices.
        
        Returns:
            List of available device dictionaries.
        """
        url = f"{self.API_BASE}/me/player/devices"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            return data.get("devices", [])
        
        except requests.RequestException as e:
            print(f"Error fetching devices: {e}")
            return []
    
    def find_device_by_name(self, device_name: str) -> Optional[str]:
        """Find device ID by name.
        
        Args:
            device_name: Name of the device to find.
        
        Returns:
            Device ID if found, None otherwise.
        """
        devices = self.get_devices()
        
        for device in devices:
            if device.get("name") == device_name:
                return device.get("id")
        
        return None
    
    def transfer_playback(self, device_id: str, play: bool = False) -> bool:
        """Transfer playback to a specific device.
        
        Args:
            device_id: Target device ID.
            play: Whether to start playing immediately.
        
        Returns:
            True if successful, False otherwise.
        """
        url = f"{self.API_BASE}/me/player"
        
        data = {
            "device_ids": [device_id],
            "play": play
        }
        
        try:
            response = requests.put(url, headers=self._get_headers(), json=data)
            
            if response.status_code == 204:
                return True
            
            response.raise_for_status()
            return True
        
        except requests.RequestException as e:
            print(f"Error transferring playback: {e}")
            return False
