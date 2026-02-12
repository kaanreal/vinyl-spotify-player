"""Configuration loader for Vinyl Spotify Player."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str = "config.json"):
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.base_dir = Path(__file__).parent.parent
        self.config_path = self.base_dir / config_path
        
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.json.example to config.json and fill in your credentials."
            )
        
        with open(self.config_path, 'r') as f:
            self._config: Dict[str, Any] = json.load(f)
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required configuration fields."""
        required_fields = [
            "client_id",
            "client_secret",
            "redirect_uri",
            "device_name",
            "tonearm_gpio_pin",
            "display_width",
            "display_height"
        ]
        
        missing = [field for field in required_fields if not self._config.get(field)]
        
        if missing:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")
    
    @property
    def client_id(self) -> str:
        """Spotify application client ID."""
        return self._config["client_id"]
    
    @property
    def client_secret(self) -> str:
        """Spotify application client secret."""
        return self._config["client_secret"]
    
    @property
    def redirect_uri(self) -> str:
        """OAuth redirect URI."""
        return self._config["redirect_uri"]
    
    @property
    def device_name(self) -> str:
        """Raspotify device name."""
        return self._config["device_name"]
    
    @property
    def tonearm_gpio_pin(self) -> int:
        """GPIO pin number for tonearm switch."""
        return int(self._config["tonearm_gpio_pin"])
    
    @property
    def display_width(self) -> int:
        """Display width in pixels."""
        return int(self._config["display_width"])
    
    @property
    def display_height(self) -> int:
        """Display height in pixels."""
        return int(self._config["display_height"])
    
    @property
    def poll_interval_ms(self) -> int:
        """Polling interval for playback state in milliseconds."""
        return int(self._config.get("poll_interval_ms", 1000))
    
    @property
    def album_art_cache_dir(self) -> Path:
        """Directory for caching album artwork."""
        cache_dir = self._config.get("album_art_cache_dir", "album_art_cache")
        path = self.base_dir / cache_dir
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def tokens_path(self) -> Path:
        """Path to tokens storage file."""
        return self.base_dir / "tokens.json"
