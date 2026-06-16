from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.getenv("VINYL_CONFIG_DIR", Path.home() / ".config" / "vinyl-spotify"))
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "tokens.json"

DEFAULT_CONFIG = {
    "spotify_client_id": "YOUR_SPOTIFY_CLIENT_ID",
    "spotify_redirect_uri": "http://localhost:8888/callback",
    "gpio": {
        "hall_sensor_pin": 17,
        "motor_pwm_pin": 18,
        "motor_dir_pin": 24,
        "encoder_a": 22,
        "encoder_b": 23,
    },
    "display": {
        "width": 480,
        "height": 480,
    },
    "poll_interval": 2,
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text())}
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def load_tokens() -> dict | None:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return None


def save_tokens(tokens: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
