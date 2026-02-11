#!/usr/bin/env python3
"""Main application for Vinyl Spotify Player."""

import signal
import sys
import time
import logging
from typing import Optional

from config import POLL_INTERVAL
from spotify_monitor import SpotifyMonitor, TrackInfo
from album_art_cache import AlbumArtCache
from display_ui import DisplayUI
from tonearm_gpio import TonearmController
from raspotify_control import RaspotifyControl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class VinylSpotifyPlayer:
    """Main application controller."""
    
    def __init__(self) -> None:
        self.running: bool = True
        self.monitor: SpotifyMonitor = SpotifyMonitor()
        self.cache: AlbumArtCache = AlbumArtCache()
        self.display: DisplayUI = DisplayUI()
        self.tonearm: TonearmController = TonearmController(
            on_state_change=self._on_tonearm_change
        )
        
        self.current_track: Optional[TrackInfo] = None
        self.last_track_id: str = ""
        
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame: Optional[object]) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _on_tonearm_change(self, is_placed: bool) -> None:
        """Handle tonearm state change."""
        if is_placed:
            logger.info("Tonearm placed - attempting to play")
            self.monitor.play_pause()
        else:
            logger.info("Tonearm lifted - attempting to pause")
            self.monitor.play_pause()
    
    def _update_track_info(self) -> None:
        """Update track information and album art if changed."""
        track = self.monitor.get_track_info()
        
        if track.track_id != self.last_track_id:
            logger.info(f"Track changed: {track.title} - {track.artist}")
            self.last_track_id = track.track_id
            
            album_art = self.cache.get_album_art(track.album_art_url)
            self.display.update_album_art(album_art)
        
        self.current_track = track
    
    def _render_display(self) -> None:
        """Render current display state."""
        if not self.current_track:
            return
        
        estimated_position = self.monitor.get_estimated_position(self.current_track)
        self.display.render(self.current_track, estimated_position)
    
    def _check_service(self) -> None:
        """Check if Raspotify service is running."""
        if not RaspotifyControl.is_service_running():
            logger.error("Raspotify service is not running!")
    
    def run(self) -> None:
        """Main application loop."""
        logger.info("Vinyl Spotify Player starting...")
        
        self._check_service()
        
        last_update_time: float = 0.0
        
        try:
            while self.running:
                if not self.display.handle_events():
                    logger.info("Display closed by user")
                    break
                
                current_time = time.time()
                if current_time - last_update_time >= POLL_INTERVAL:
                    self._update_track_info()
                    last_update_time = current_time
                
                self._render_display()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Clean shutdown of all components."""
        logger.info("Shutting down...")
        self.tonearm.cleanup()
        self.display.close()
        logger.info("Shutdown complete")


def main() -> None:
    """Application entry point."""
    logger.info("="*50)
    logger.info("Vinyl Spotify Player")
    logger.info("="*50)
    
    try:
        player = VinylSpotifyPlayer()
        player.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
