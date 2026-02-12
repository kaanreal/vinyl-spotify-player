"""Main application for Vinyl Spotify Player."""

import sys
import time
import signal
from typing import Optional, Dict, Any

from config import Config
from spotify_client import SpotifyClient
from display_renderer import DisplayRenderer
from tonearm_controller import TonearmController


class VinylSpotifyPlayer:
    """Main application class for the Vinyl Spotify Player."""

    def __init__(self):
        """Initialize the application."""
        print("Initializing Vinyl Spotify Player...")
        
        # Load configuration
        self.config = Config()
        
        # Initialize Spotify client
        self.spotify = SpotifyClient(
            self.config.client_id,
            self.config.client_secret,
            self.config.tokens_path
        )
        
        # Initialize display
        self.display = DisplayRenderer(
            self.config.display_width,
            self.config.display_height,
            self.config.album_art_cache_dir
        )
        
        # Initialize tonearm controller
        self.tonearm = TonearmController(
            self.config.tonearm_gpio_pin,
            on_place=self._handle_tonearm_place,
            on_lift=self._handle_tonearm_lift
        )
        
        # Application state
        self.running = True
        self.device_id: Optional[str] = None
        self.last_playback_data: Optional[Dict[str, Any]] = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("Initialization complete")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False
    
    def _find_device_id(self) -> Optional[str]:
        """Find the device ID for the configured Raspotify device.
        
        Returns:
            Device ID if found, None otherwise.
        """
        device_id = self.spotify.find_device_by_name(self.config.device_name)
        
        if device_id:
            print(f"Found device: {self.config.device_name} (ID: {device_id})")
        else:
            print(f"Device not found: {self.config.device_name}")
            print("Make sure Raspotify is running and the device name in config.json matches")
        
        return device_id
    
    def _handle_tonearm_place(self) -> None:
        """Handle tonearm being placed on the record."""
        # Find device if not already found
        if not self.device_id:
            self.device_id = self._find_device_id()
        
        # Start playback
        if self.device_id:
            success = self.spotify.play(self.device_id)
            if not success:
                print("Failed to start playback")
        else:
            # Try without device ID (use currently active device)
            success = self.spotify.play()
            if not success:
                print("Failed to start playback - no active device")
    
    def _handle_tonearm_lift(self) -> None:
        """Handle tonearm being lifted from the record."""
        # Find device if not already found
        if not self.device_id:
            self.device_id = self._find_device_id()
        
        # Pause playback
        if self.device_id:
            success = self.spotify.pause(self.device_id)
            if not success:
                print("Failed to pause playback")
        else:
            # Try without device ID (use currently active device)
            success = self.spotify.pause()
            if not success:
                print("Failed to pause playback - no active device")
    
    def _update_playback_state(self) -> None:
        """Update and render current playback state."""
        try:
            playback_data = self.spotify.get_current_playback()
            
            # Update device ID if playing on our device
            if playback_data and playback_data.get("device"):
                device = playback_data["device"]
                if device.get("name") == self.config.device_name:
                    self.device_id = device.get("id")
            
            # Render display
            self.display.render(playback_data)
            
            self.last_playback_data = playback_data
        
        except Exception as e:
            print(f"Error updating playback state: {e}")
    
    def run(self) -> None:
        """Run the main application loop."""
        print("Starting main loop...")
        print(f"Polling interval: {self.config.poll_interval_ms}ms")
        print("Press Ctrl+C to exit")
        
        # Find device on startup
        self.device_id = self._find_device_id()
        
        # Main loop
        last_update_time = 0
        poll_interval_sec = self.config.poll_interval_ms / 1000.0
        
        while self.running:
            # Handle display events
            if not self.display.handle_events():
                self.running = False
                break
            
            # Check tonearm state
            self.tonearm.check()
            
            # Update playback state at polling interval
            current_time = time.time()
            if current_time - last_update_time >= poll_interval_sec:
                self._update_playback_state()
                last_update_time = current_time
            
            # Small sleep to prevent busy loop
            time.sleep(0.01)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        print("Cleaning up...")
        
        try:
            self.tonearm.cleanup()
        except Exception as e:
            print(f"Error cleaning up tonearm: {e}")
        
        try:
            self.display.cleanup()
        except Exception as e:
            print(f"Error cleaning up display: {e}")
        
        print("Cleanup complete")


def main():
    """Main entry point."""
    try:
        app = VinylSpotifyPlayer()
        app.run()
        app.cleanup()
        sys.exit(0)
    
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
