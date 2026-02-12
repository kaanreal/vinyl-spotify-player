"""Path utilities for the Vinyl Spotify Player."""

from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.
    
    Returns:
        Path: Project root directory
    """
    # app/util/paths.py -> app/util -> app -> project_root
    return Path(__file__).parent.parent.parent


def get_config_path() -> Path:
    """Get the path to config.json.
    
    Returns:
        Path: Path to config.json
    """
    return get_project_root() / 'app' / 'config' / 'config.json'


def get_example_config_path() -> Path:
    """Get the path to config.example.json.
    
    Returns:
        Path: Path to config.example.json
    """
    return get_project_root() / 'app' / 'config' / 'config.example.json'


def get_tokens_dir() -> Path:
    """Get the tokens directory path.
    
    Returns:
        Path: Tokens directory
    """
    tokens_dir = get_project_root() / 'data' / 'tokens'
    tokens_dir.mkdir(parents=True, exist_ok=True)
    return tokens_dir


def get_cache_dir() -> Path:
    """Get the cache directory path.
    
    Returns:
        Path: Cache directory
    """
    cache_dir = get_project_root() / 'data' / 'cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_logs_dir() -> Path:
    """Get the logs directory path.
    
    Returns:
        Path: Logs directory
    """
    logs_dir = get_project_root() / 'data' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_token_path() -> Path:
    """Get the path to the Spotify token file.
    
    Returns:
        Path: Path to spotify_tokens.json
    """
    return get_tokens_dir() / 'spotify_tokens.json'
