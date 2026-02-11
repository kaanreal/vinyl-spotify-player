"""Control Raspotify service and playback."""

import subprocess
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaspotifyControl:
    """Control Raspotify service and playback via playerctl."""
    
    @staticmethod
    def is_service_running() -> bool:
        """Check if raspotify service is running."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "raspotify"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() == "active"
        except Exception as e:
            logger.error(f"Failed to check service status: {e}")
            return False
    
    @staticmethod
    def restart_service() -> bool:
        """Restart raspotify service."""
        try:
            subprocess.run(
                ["sudo", "systemctl", "restart", "raspotify"],
                check=True,
                timeout=10,
            )
            logger.info("Raspotify service restarted")
            return True
        except Exception as e:
            logger.error(f"Failed to restart service: {e}")
            return False
    
    @staticmethod
    def play_pause() -> bool:
        """Toggle play/pause via playerctl."""
        try:
            subprocess.run(
                ["playerctl", "-p", "raspotify", "play-pause"],
                check=True,
                timeout=5,
            )
            logger.info("Toggled play/pause via playerctl")
            return True
        except subprocess.CalledProcessError:
            logger.warning("playerctl command failed - no active player")
            return False
        except Exception as e:
            logger.error(f"Failed to toggle play/pause: {e}")
            return False
    
    @staticmethod
    def play() -> bool:
        """Start playback via playerctl."""
        try:
            subprocess.run(
                ["playerctl", "-p", "raspotify", "play"],
                check=True,
                timeout=5,
            )
            logger.info("Started playback via playerctl")
            return True
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
            return False
    
    @staticmethod
    def pause() -> bool:
        """Pause playback via playerctl."""
        try:
            subprocess.run(
                ["playerctl", "-p", "raspotify", "pause"],
                check=True,
                timeout=5,
            )
            logger.info("Paused playback via playerctl")
            return True
        except Exception as e:
            logger.error(f"Failed to pause playback: {e}")
            return False
    
    @staticmethod
    def get_status() -> Optional[str]:
        """Get current playback status via playerctl."""
        try:
            result = subprocess.run(
                ["playerctl", "-p", "raspotify", "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return None
