"""Configuration validation."""

from typing import Dict, Any


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure and required fields.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ['spotify', 'display', 'motor', 'tonearm', 'encoder', 'polling']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    
    # Validate Spotify config
    spotify = config['spotify']
    spotify_required = ['client_id', 'client_secret', 'redirect_uri', 'device_name']
    for field in spotify_required:
        if field not in spotify:
            raise ValueError(f"Missing required Spotify config field: {field}")
        if not spotify[field] or spotify[field].startswith('YOUR_'):
            raise ValueError(
                f"Spotify {field} not configured. "
                "Please edit app/config/config.json with your credentials."
            )
    
    # Validate display config
    display = config['display']
    if 'width' not in display or 'height' not in display:
        raise ValueError("Display config must include width and height")
    
    # Validate numeric values
    if display['width'] <= 0 or display['height'] <= 0:
        raise ValueError("Display dimensions must be positive")
    
    if config['motor']['target_rpm'] <= 0:
        raise ValueError("Motor target_rpm must be positive")
