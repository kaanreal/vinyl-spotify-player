"""Spotify Web API client with OAuth and token management."""

import time
import base64
import requests
from typing import Optional, Dict, Any, List
from config import Config


class SpotifyClient:
    """Spotify Web API client with automatic token refresh."""
    
    SCOPES = [
        'user-read-playback-state',
        'user-read-currently-playing',
        'user-modify-playback-state'
    ]
    
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE = 'https://api.spotify.com/v1'
    
    def __init__(self, config: Config):
        """Initialize Spotify client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self._access_token: Optional[str] = config.get_access_token()
        self._refresh_token: Optional[str] = config.get_refresh_token()
        self._expires_at: Optional[float] = config.get_token_expires_at()
    
    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        params = {
            'client_id': self.config.spotify_client_id,
            'response_type': 'code',
            'redirect_uri': self.config.spotify_redirect_uri,
            'scope': ' '.join(self.SCOPES)
        }
        query = '&'.join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query}"
    
    def exchange_code_for_tokens(self, code: str) -> None:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth callback
        """
        auth_header = base64.b64encode(
            f"{self.config.spotify_client_id}:{self.config.spotify_client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.config.spotify_redirect_uri
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data['access_token']
        self._refresh_token = token_data['refresh_token']
        self._expires_at = time.time() + token_data['expires_in']
        
        self.config.save_tokens(
            self._access_token,
            self._refresh_token,
            self._expires_at
        )
    
    def refresh_access_token(self) -> None:
        """Refresh access token using refresh token."""
        if not self._refresh_token:
            raise RuntimeError("No refresh token available. Run oauth_pair.py first.")
        
        auth_header = base64.b64encode(
            f"{self.config.spotify_client_id}:{self.config.spotify_client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data['access_token']
        self._expires_at = time.time() + token_data['expires_in']
        
        # Refresh token may be updated
        if 'refresh_token' in token_data:
            self._refresh_token = token_data['refresh_token']
        
        self.config.save_tokens(
            self._access_token,
            self._refresh_token,
            self._expires_at
        )
    
    def ensure_valid_token(self) -> None:
        """Ensure access token is valid, refresh if needed."""
        if not self._access_token or not self._expires_at:
            raise RuntimeError("No access token available. Run oauth_pair.py first.")
        
        # Refresh if token expires in less than 60 seconds
        if time.time() >= (self._expires_at - 60):
            self.refresh_access_token()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object
        """
        self.ensure_valid_token()
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self._access_token}'
        
        url = f"{self.API_BASE}/{endpoint.lstrip('/')}"
        return requests.request(method, url, headers=headers, **kwargs)
    
    def get_current_playback(self) -> Optional[Dict[str, Any]]:
        """Get current playback state.
        
        Returns:
            Playback state dict or None if nothing playing
        """
        try:
            response = self._make_request('GET', '/me/player')
            if response.status_code == 204:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting playback state: {e}")
            return None
    
    def get_currently_playing(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track.
        
        Returns:
            Currently playing track dict or None
        """
        try:
            response = self._make_request('GET', '/me/player/currently-playing')
            if response.status_code == 204:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting currently playing: {e}")
            return None
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get available Spotify devices.
        
        Returns:
            List of device dicts
        """
        try:
            response = self._make_request('GET', '/me/player/devices')
            response.raise_for_status()
            return response.json().get('devices', [])
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
    
    def get_device_id(self, device_name: Optional[str] = None) -> Optional[str]:
        """Get device ID by name.
        
        Args:
            device_name: Device name to find (defaults to config device name)
        
        Returns:
            Device ID or None if not found
        """
        if device_name is None:
            device_name = self.config.spotify_device_name
        
        devices = self.get_devices()
        for device in devices:
            if device['name'] == device_name:
                return device['id']
        return None
    
    def play(self, device_id: Optional[str] = None) -> bool:
        """Start or resume playback.
        
        Args:
            device_id: Optional device ID to play on
        
        Returns:
            True if successful
        """
        try:
            params = {}
            if device_id:
                params['device_id'] = device_id
            
            response = self._make_request('PUT', '/me/player/play', params=params)
            
            # 204 = success, 404 = no active device, 403 = premium required
            if response.status_code in (204, 202):
                return True
            
            print(f"Play request returned {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"Error starting playback: {e}")
            return False
    
    def pause(self, device_id: Optional[str] = None) -> bool:
        """Pause playback.
        
        Args:
            device_id: Optional device ID to pause
        
        Returns:
            True if successful
        """
        try:
            params = {}
            if device_id:
                params['device_id'] = device_id
            
            response = self._make_request('PUT', '/me/player/pause', params=params)
            
            if response.status_code in (204, 202):
                return True
            
            print(f"Pause request returned {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"Error pausing playback: {e}")
            return False
    
    def transfer_playback(self, device_id: str, play: bool = False) -> bool:
        """Transfer playback to a device.
        
        Args:
            device_id: Device ID to transfer to
            play: Whether to start playing
        
        Returns:
            True if successful
        """
        try:
            data = {
                'device_ids': [device_id],
                'play': play
            }
            response = self._make_request('PUT', '/me/player', json=data)
            
            if response.status_code in (204, 202):
                return True
            
            print(f"Transfer request returned {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"Error transferring playback: {e}")
            return False
