"""Main application entry point for Vinyl Spotify Player."""

import sys
import time
import pygame
from pathlib import Path

from app.config.config_loader import load_config
from app.util.logging import setup_logging
from app.util.paths import get_token_path
from app.io.platform import Platform
from app.io.tonearm_hall import create_tonearm_sensor
from app.io.volume_encoder import create_volume_encoder
from app.io.motor_control import create_motor_controller, StubMotorController
from app.spotify.tokens import TokenManager
from app.spotify.api import SpotifyAPI
from app.spotify.device import DeviceManager
from app.spotify.control import PlaybackController
from app.ui.display import Display
from app.ui.touch_input import Gesture

logger = setup_logging("main")


class VinylSpotifyPlayer:
    """Main application class."""
    
    def __init__(self):
        """Initialize the Vinyl Spotify Player."""
        logger.info("=" * 60)
        logger.info("Vinyl Spotify Player Starting")
        logger.info("=" * 60)
        
        # Load configuration
        try:
            self.config = load_config()
            logger.info(f"Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
        
        # Detect platform
        platform_name = Platform.get_platform_name()
        dev_mode = Platform.is_dev_mode(self.config)
        logger.info(f"Platform: {platform_name}")
        logger.info(f"Dev Mode: {'ENABLED' if dev_mode else 'DISABLED'}")
        
        # Check for tokens
        if not get_token_path().exists():
            logger.error("No Spotify tokens found!")
            logger.error("Please run: ./scripts/pair.sh")
            sys.exit(1)
        
        # Initialize Spotify
        self._init_spotify()
        
        # Initialize hardware/stubs
        self._init_hardware()
        
        # Initialize display
        self._init_display()
        
        # Connect event handlers
        self._connect_handlers()
        
        logger.info("Initialization complete")
    
    def _init_spotify(self) -> None:
        """Initialize Spotify components."""
        logger.info("Initializing Spotify integration...")
        
        spotify_config = self.config['spotify']
        
        # Token manager
        self.token_manager = TokenManager(
            spotify_config['client_id'],
            spotify_config['client_secret']
        )
        
        if not self.token_manager.has_valid_tokens():
            logger.error("Invalid or missing Spotify tokens!")
            logger.error("Please run: ./scripts/pair.sh")
            sys.exit(1)
        
        # API client
        self.api = SpotifyAPI(self.token_manager)
        
        # Device manager
        self.device_manager = DeviceManager(
            self.api,
            spotify_config['device_name']
        )
        
        # Playback controller
        poll_interval = self.config['polling']['spotify_state_interval_ms']
        self.playback = PlaybackController(
            self.api,
            self.device_manager,
            poll_interval
        )
        
        logger.info("Spotify integration ready")
    
    def _init_hardware(self) -> None:
        """Initialize hardware components (or stubs)."""
        logger.info("Initializing hardware...")
        
        # Tonearm sensor
        self.tonearm = create_tonearm_sensor(self.config)
        
        # Volume encoder
        self.encoder = create_volume_encoder(self.config)
        
        # Motor controller
        self.motor = create_motor_controller(self.config)
        
        logger.info("Hardware initialized")
    
    def _init_display(self) -> None:
        """Initialize display UI."""
        logger.info("Initializing display...")
        
        self.display = Display(self.config)
        
        logger.info("Display ready")
    
    def _connect_handlers(self) -> None:
        """Connect event handlers."""
        logger.info("Connecting event handlers...")
        
        # Tonearm -> play/pause + motor
        def on_tonearm_change(is_down: bool):
            logger.info(f"Tonearm {'DOWN' if is_down else 'UP'} -> {'PLAY' if is_down else 'PAUSE'}")
            if is_down:
                self.playback.play()
                self.motor.start()
            else:
                self.playback.pause()
                self.motor.stop()
        
        self.tonearm.start_monitoring(on_tonearm_change)
        
        # Encoder -> volume
        def on_volume_change(delta: int):
            self.playback.adjust_volume(delta)
        
        self.encoder.start_monitoring(on_volume_change)
        
        # Touch tap -> play/pause toggle
        def on_tap():
            logger.info("Touch TAP -> TOGGLE PLAY/PAUSE")
            self.playback.toggle_playback()
        
        # Touch swipe -> next/previous
        def on_swipe(gesture: Gesture):
            if gesture == Gesture.SWIPE_LEFT:
                logger.info("Touch SWIPE LEFT -> PREVIOUS")
                self.playback.previous()
            elif gesture == Gesture.SWIPE_RIGHT:
                logger.info("Touch SWIPE RIGHT -> NEXT")
                self.playback.next()
        
        self.display.set_touch_callbacks(on_tap, on_swipe)
        
        # Playback state changes -> update display + motor
        def on_state_change(state):
            self.display.update_playback_state(state)
            
            # Sync motor with playback state
            if state and state.get('is_playing'):
                if not self.motor.is_running():
                    self.motor.start()
            else:
                if self.motor.is_running():
                    self.motor.stop()
        
        self.playback.add_state_callback(on_state_change)
        
        # Dev mode keyboard handlers
        if Platform.is_dev_mode(self.config):
            self._setup_dev_mode_handlers()
        
        logger.info("Event handlers connected")
    
    def _setup_dev_mode_handlers(self) -> None:
        """Set up development mode keyboard handlers."""
        dev_config = self.config.get('dev_mode', {})
        
        logger.info("Dev mode keyboard controls:")
        logger.info(f"  Tonearm toggle: {dev_config.get('tonearm_key', 't').upper()}")
        logger.info(f"  Play/Pause: {dev_config.get('play_pause_key', 'space').upper()}")
        logger.info(f"  Next track: {dev_config.get('next_key', 'right').upper()}")
        logger.info(f"  Previous track: {dev_config.get('prev_key', 'left').upper()}")
        logger.info(f"  Volume up: {dev_config.get('volume_up_key', 'up').upper()}")
        logger.info(f"  Volume down: {dev_config.get('volume_down_key', 'down').upper()}")
    
    def run(self) -> None:
        """Run the main application loop."""
        logger.info("Starting main loop...")
        
        # Start Spotify state polling
        self.playback.start_polling()
        
        # Main loop
        running = True
        try:
            while running:
                # Handle dev mode keyboard for tonearm/volume
                if Platform.is_dev_mode(self.config):
                    self._handle_dev_mode_keys()
                
                # Run display frame
                if not self.display.run_frame():
                    running = False
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)
        
        finally:
            self.shutdown()
    
    def _handle_dev_mode_keys(self) -> None:
        """Handle development mode keyboard inputs."""
        keys = pygame.key.get_pressed()
        dev_config = self.config.get('dev_mode', {})
        
        # Tonearm toggle (T key)
        key_name = dev_config.get('tonearm_key', 't')
        key_const = f"K_{key_name.lower() if len(key_name) == 1 else key_name.upper()}"
        tonearm_key = getattr(pygame, key_const)
        if keys[tonearm_key]:
            # Debounce with a small delay
            if not hasattr(self, '_last_tonearm_toggle') or \
               time.time() - self._last_tonearm_toggle > 0.5:
                from app.io.tonearm_hall import StubTonearmSensor
                if isinstance(self.tonearm, StubTonearmSensor):
                    self.tonearm.toggle()
                    self._last_tonearm_toggle = time.time()
        
        # Volume up (UP arrow)
        key_name = dev_config.get('volume_up_key', 'up')
        key_const = f"K_{key_name.lower() if len(key_name) == 1 else key_name.upper()}"
        volume_up_key = getattr(pygame, key_const)
        if keys[volume_up_key]:
            if not hasattr(self, '_last_volume_up') or \
               time.time() - self._last_volume_up > 0.3:
                from app.io.volume_encoder import StubVolumeEncoder
                if isinstance(self.encoder, StubVolumeEncoder):
                    self.encoder.simulate_rotation(1)
                    self._last_volume_up = time.time()
        
        # Volume down (DOWN arrow)
        key_name = dev_config.get('volume_down_key', 'down')
        key_const = f"K_{key_name.lower() if len(key_name) == 1 else key_name.upper()}"
        volume_down_key = getattr(pygame, key_const)
        if keys[volume_down_key]:
            if not hasattr(self, '_last_volume_down') or \
               time.time() - self._last_volume_down > 0.3:
                from app.io.volume_encoder import StubVolumeEncoder
                if isinstance(self.encoder, StubVolumeEncoder):
                    self.encoder.simulate_rotation(-1)
                    self._last_volume_down = time.time()
    
    def shutdown(self) -> None:
        """Clean shutdown."""
        logger.info("Shutting down...")
        
        # Stop polling
        self.playback.stop_polling()
        
        # Stop hardware monitoring
        self.tonearm.stop_monitoring()
        self.encoder.stop_monitoring()
        self.motor.stop()
        
        # Close display
        self.display.quit()
        
        logger.info("Shutdown complete")


def main():
    """Main entry point."""
    try:
        app = VinylSpotifyPlayer()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
