"""Configuration management for Vinyl Spotify Player."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Load and manage application configuration."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.json.example to config.json and fill in your details."
            )
        
        with open(self.config_path, 'r') as f:
            self._config = json.load(f)
    
    def save(self) -> None:
        """Save configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    @property
    def spotify_client_id(self) -> str:
        """Get Spotify client ID."""
        return self._config['spotify']['client_id']
    
    @property
    def spotify_client_secret(self) -> str:
        """Get Spotify client secret."""
        return self._config['spotify']['client_secret']
    
    @property
    def spotify_redirect_uri(self) -> str:
        """Get Spotify OAuth redirect URI."""
        return self._config['spotify'].get('redirect_uri', 'http://127.0.0.1:8888/callback')
    
    @property
    def spotify_device_name(self) -> str:
        """Get Raspotify device name."""
        return self._config['spotify'].get('device_name', 'Vinyl Spotify Player')
    
    @property
    def gpio_tonearm_pin(self) -> int:
        """Get GPIO pin for tonearm control."""
        return self._config['gpio']['tonearm_pin']
    
    @property
    def gpio_tonearm_pull(self) -> str:
        """Get GPIO pull mode (UP or DOWN)."""
        return self._config['gpio'].get('tonearm_pull', 'UP')
    
    @property
    def gpio_tonearm_active_state(self) -> int:
        """Get GPIO active state (0 or 1) when tonearm is placed."""
        return self._config['gpio'].get('tonearm_active_state', 0)
    
    @property
    def display_width(self) -> int:
        """Get display width in pixels."""
        return self._config['display'].get('width', 480)
    
    @property
    def display_height(self) -> int:
        """Get display height in pixels."""
        return self._config['display'].get('height', 480)
    
    @property
    def display_fullscreen(self) -> bool:
        """Get display fullscreen mode."""
        return self._config['display'].get('fullscreen', True)
    
    @property
    def cache_dir(self) -> Path:
        """Get cache directory path."""
        cache_path = Path(self._config.get('cache_dir', './cache'))
        cache_path.mkdir(exist_ok=True)
        return cache_path
    
    @property
    def token_file(self) -> Path:
        """Get token file path."""
        return Path(self._config.get('token_file', 'tokens.json'))
    
    def get_access_token(self) -> Optional[str]:
        """Get stored access token."""
        if not self.token_file.exists():
            return None
        
        with open(self.token_file, 'r') as f:
            tokens = json.load(f)
        return tokens.get('access_token')
    
    def get_refresh_token(self) -> Optional[str]:
        """Get stored refresh token."""
        if not self.token_file.exists():
            return None
        
        with open(self.token_file, 'r') as f:
            tokens = json.load(f)
        return tokens.get('refresh_token')
    
    def get_token_expires_at(self) -> Optional[float]:
        """Get token expiration timestamp."""
        if not self.token_file.exists():
            return None
        
        with open(self.token_file, 'r') as f:
            tokens = json.load(f)
        return tokens.get('expires_at')
    
    def save_tokens(self, access_token: str, refresh_token: str, expires_at: float) -> None:
        """Save OAuth tokens to file.
        
        Args:
            access_token: Spotify access token
            refresh_token: Spotify refresh token
            expires_at: Token expiration timestamp
        """
        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f, indent=2)
