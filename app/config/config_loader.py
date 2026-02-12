"""Configuration loader for the Vinyl Spotify Player."""

import json
import shutil
from pathlib import Path
from typing import Dict, Any
from .validate import validate_config
from app.util.paths import get_config_path, get_example_config_path


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json.
    
    If config.json doesn't exist, creates it from config.example.json.
    
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config.example.json is missing
        ValueError: If configuration is invalid
    """
    config_path = get_config_path()
    example_path = get_example_config_path()
    
    # Create config from example if it doesn't exist
    if not config_path.exists():
        if not example_path.exists():
            raise FileNotFoundError(
                f"Example config not found at {example_path}"
            )
        
        print(f"Creating config.json from example at {config_path}")
        shutil.copy(example_path, config_path)
        print("⚠️  Please edit app/config/config.json with your Spotify credentials")
    
    # Load and validate config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    validate_config(config)
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config.json.
    
    Args:
        config: Configuration dictionary to save
    """
    validate_config(config)
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
