#!/usr/bin/env python3
"""Main application for Vinyl Spotify Player."""

import sys
import time
import signal
from pathlib import Path
from config import Config
from spotify_client import SpotifyClient
from display import Display
from metadata import MetadataManager
from tonearm import TonearmController


class VinylSpotifyPlayer:
    """Main application coordinator."""
    
    def __init__(self):
        """Initialize application."""
        self.running = False
        
        # Load configuration
        print("Loading configuration...")
        self.config = Config()
        
        # Initialize Spotify client
        print("Initializing Spotify client...")
        self.spotify = SpotifyClient(self.config)
        
        # Initialize display
        print("Initializing display...")
        self.display = Display(
            width=self.config.display_width,
            height=self.config.display_height,
            fullscreen=self.config.display_fullscreen,
            cache_dir=self.config.cache_dir
        )
        
        # Initialize metadata manager
        print("Initializing metadata manager...")
        self.metadata = MetadataManager(self.spotify, poll_interval=1.0)
        
        # Initialize tonearm controller
        print("Initializing tonearm controller...")
        self.tonearm = TonearmController(self.config, on_state_change=self.on_tonearm_change)
        
        # State
        self.device_id: Optional[str] = None
        self.last_track_id: Optional[str] = None
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print(f"\nReceived signal {signum}, shutting down...")
        self.shutdown()
    
    def get_device_id(self) -> Optional[str]:
        """Get Raspotify device ID.
        
        Returns:
            Device ID or None if not found
        """
        if self.device_id:
            return self.device_id
        
        # Try to find device
        device_id = self.spotify.get_device_id()
        if device_id:
            print(f"Found device: {self.config.spotify_device_name} ({device_id})")
            self.device_id = device_id
        
        return device_id
    
    def on_tonearm_change(self, is_placed: bool) -> None:
        """Handle tonearm state change.
        
        Args:
            is_placed: True if tonearm placed, False if lifted
        """
        print(f"Tonearm {'placed' if is_placed else 'lifted'}")
        
        # Get device ID
        device_id = self.get_device_id()
        
        if is_placed:
            # Start playback
            if device_id:
                success = self.spotify.play(device_id)
                if success:
                    print("Playback started")
                else:
                    print("Failed to start playback")
            else:
                print("No active device found, cannot start playback")
        else:
            # Pause playback
            if device_id:
                success = self.spotify.pause(device_id)
                if success:
                    print("Playback paused")
                else:
                    print("Failed to pause playback")
            else:
                # Try to pause without device ID
                success = self.spotify.pause()
                if success:
                    print("Playback paused")
    
    def update_display(self) -> None:
        """Update display with current track info."""
        track = self.metadata.current_track
        
        if not track:
            # No track playing, show blank screen
            if self.last_track_id is not None:
                self.display.clear()
                self.last_track_id = None
            return
        
        # Check if track changed
        if track.track_id != self.last_track_id:
            # Load new album art
            if track.album_art_url:
                self.display.load_album_art(track.album_art_url)
            self.last_track_id = track.track_id
        
        # Render display
        self.display.render(
            track_name=track.track_name,
            artists=track.artists,
            album=track.album,
            progress_ms=track.progress_ms,
            duration_ms=track.duration_ms,
            is_playing=track.is_playing
        )
    
    def run(self) -> None:
        """Run main application loop."""
        self.running = True
        print("Vinyl Spotify Player started")
        print(f"Waiting for playback on {self.config.spotify_device_name}...")
        
        # Show blank screen initially
        self.display.clear()
        
        try:
            while self.running:
                # Poll metadata
                self.metadata.poll()
                
                # Update display
                self.update_display()
                
                # Check tonearm
                self.tonearm.check()
                
                # Small delay to prevent busy loop
                time.sleep(0.05)  # 50ms = 20 FPS
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Clean shutdown."""
        self.running = False
        
        print("Cleaning up...")
        
        # Clean up tonearm GPIO
        try:
            self.tonearm.cleanup()
        except Exception as e:
            print(f"Error cleaning up tonearm: {e}")
        
        # Clean up display
        try:
            self.display.quit()
        except Exception as e:
            print(f"Error cleaning up display: {e}")
        
        print("Goodbye!")


def main():
    """Entry point."""
    # Check for tokens
    token_file = Path('tokens.json')
    if not token_file.exists():
        print("ERROR: No tokens found!")
        print("Please run oauth_pair.py first to authenticate with Spotify.")
        sys.exit(1)
    
    # Create and run application
    app = VinylSpotifyPlayer()
    app.run()


if __name__ == '__main__':
    main()
