"""Main display UI with pygame."""

import pygame
import pygame.gfxdraw
import time
import math
from typing import Optional, Dict, Any
from PIL import Image
import io
from app.ui.artwork_cache import ArtworkCache
from app.ui.cover_rotation import CoverRotation, create_circular_mask, apply_circular_mask
from app.ui.touch_input import TouchInput, DevTouchInput, Gesture
from app.io.platform import Platform
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class Display:
    """Main display UI for the Vinyl Spotify Player."""
    
    def __init__(self, config: dict):
        """Initialize display.
        
        Args:
            config: Application configuration
        """
        self.config = config
        display_config = config['display']
        
        self.width = display_config['width']
        self.height = display_config['height']
        self.fps = display_config.get('fps', 30)
        
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Vinyl Spotify Player")
        
        # Create display surface
        if Platform.is_dev_mode(config):
            self.screen = pygame.display.set_mode((self.width, self.height))
        else:
            # Fullscreen on Pi
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        
        self.clock = pygame.time.Clock()
        
        # UI components
        self.artwork_cache = ArtworkCache(target_size=(self.width, self.height))
        self.cover_rotation = CoverRotation(target_rpm=config['motor']['target_rpm'])
        
        # Touch input
        if Platform.is_dev_mode(config):
            dev_config = config.get('dev_mode', {})
            
            # Pygame uses lowercase for single-letter keys, uppercase for special keys
            def get_key_const(key_name: str) -> int:
                key_const = f"K_{key_name.lower() if len(key_name) == 1 else key_name.upper()}"
                return getattr(pygame, key_const)
            
            self.touch = DevTouchInput(
                tap_key=get_key_const(dev_config.get('play_pause_key', 'space')),
                next_key=get_key_const(dev_config.get('next_key', 'right')),
                prev_key=get_key_const(dev_config.get('prev_key', 'left'))
            )
        else:
            self.touch = TouchInput()
        
        # State
        self.current_state = None
        self.current_artwork = None
        self.artwork_surface = None
        self.next_artwork_surface = None
        self.artwork_fade_progress = 1.0  # 0.0 to 1.0
        self.artwork_fade_start = None
        self.artwork_fade_duration = 0.3  # seconds
        self.circular_mask = create_circular_mask(min(self.width, self.height))
        
        # Progress bar
        self.progress_smoothed = 0.0  # Smoothly interpolated progress
        self.progress_color = (52, 199, 89)  # Default Apple green
        
        # Default placeholder image
        self.placeholder_surface = self._create_placeholder()
        
        self.running = False
        
        logger.info(f"Display initialized: {self.width}x{self.height} @ {self.fps}fps")
    
    def _create_placeholder(self) -> pygame.Surface:
        """Create placeholder image for when no artwork is available.
        
        Returns:
            pygame.Surface: Placeholder surface
        """
        surface = pygame.Surface((self.width, self.height))
        surface.fill((40, 40, 40))
        
        # Draw vinyl record shape
        center = (self.width // 2, self.height // 2)
        radius = min(self.width, self.height) // 2 - 20
        
        pygame.draw.circle(surface, (60, 60, 60), center, radius)
        pygame.draw.circle(surface, (40, 40, 40), center, radius // 4)
        pygame.draw.circle(surface, (30, 30, 30), center, radius // 8)
        
        return surface
    
    def set_touch_callbacks(self, on_tap, on_swipe):
        """Set touch gesture callbacks.
        
        Args:
            on_tap: Callback for tap gesture
            on_swipe: Callback for swipe gesture (receives Gesture enum)
        """
        self.touch.on_tap(on_tap)
        self.touch.on_swipe(on_swipe)
    
    def update_playback_state(self, state: Optional[Dict[str, Any]]) -> None:
        """Update display with new playback state.
        
        Args:
            state: Playback state dictionary
        """
        self.current_state = state
        
        if state:
            # Update rotation based on is_playing
            if state.get('is_playing'):
                self.cover_rotation.start()
            else:
                self.cover_rotation.stop()
            
            # Load artwork if changed
            artwork_url = state.get('album_art_url')
            if artwork_url and artwork_url != getattr(self, '_last_artwork_url', None):
                self._last_artwork_url = artwork_url
                
                # Try to get from cache
                cached = self.artwork_cache.get_cached_image(artwork_url)
                if cached:
                    self._set_artwork(cached)
                else:
                    # Download in background
                    self.artwork_cache.download_image(artwork_url, callback=self._set_artwork)
        else:
            self.cover_rotation.stop()
    
    def _set_artwork(self, image: Image.Image) -> None:
        """Set album artwork from PIL image with smooth crossfade.
        
        Args:
            image: PIL Image of album artwork
        """
        # Convert PIL image to pygame surface
        mode = image.mode
        size = image.size
        data = image.tobytes()
        
        surface = pygame.image.fromstring(data, size, mode)
        
        # Extract dominant color for progress bar
        self._extract_dominant_color(image)
        
        # Start crossfade if there's existing artwork
        if self.artwork_surface is not None:
            self.next_artwork_surface = surface
            self.artwork_fade_progress = 0.0
            self.artwork_fade_start = time.time()
        else:
            self.artwork_surface = surface
            self.artwork_fade_progress = 1.0
        
        logger.debug("Artwork updated")
    
    def _extract_dominant_color(self, image: Image.Image) -> None:
        """Extract dominant vibrant color from album artwork.
        
        Args:
            image: PIL Image to extract color from
        """
        try:
            from colorsys import rgb_to_hsv, hsv_to_rgb
            
            # Resize for faster processing
            img_small = image.resize((50, 50))
            pixels = list(img_small.getdata())
            
            # Collect vibrant colors
            color_scores = []
            
            for pixel in pixels:
                r, g, b = pixel[:3]
                
                # Skip very dark or very bright pixels
                brightness = (r + g + b) / 3
                if brightness < 60 or brightness > 220:
                    continue
                
                # Calculate saturation and value
                h, s, v = rgb_to_hsv(r/255, g/255, b/255)
                
                # Score based on saturation and brightness
                # Prefer vibrant, visible colors
                score = s * 2 + v * 0.5
                
                if s > 0.3 and v > 0.4:
                    color_scores.append((score, (r, g, b)))
            
            if color_scores:
                # Sort by score and get the most vibrant color
                color_scores.sort(reverse=True)
                best_color = color_scores[0][1]
                
                # Boost saturation slightly for better visibility
                h, s, v = rgb_to_hsv(best_color[0]/255, best_color[1]/255, best_color[2]/255)
                s = min(1.0, s * 1.2)  # Boost saturation by 20%
                v = min(1.0, max(0.6, v))  # Ensure decent brightness
                
                r, g, b = hsv_to_rgb(h, s, v)
                self.progress_color = (int(r * 255), int(g * 255), int(b * 255))
            else:
                # Default to cyan if no good colors found
                self.progress_color = (0, 200, 255)
                
        except Exception as e:
            logger.debug(f"Color extraction failed: {e}")
            self.progress_color = (0, 200, 255)
    
    def handle_events(self) -> bool:
        """Handle pygame events.
        
        Returns:
            bool: False if quit requested, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Dev mode keyboard simulation
                if Platform.is_dev_mode(self.config) and isinstance(self.touch, DevTouchInput):
                    self.touch.handle_key_down(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.touch.handle_mouse_down(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.touch.handle_mouse_up(event.pos)
        
        return True
    
    def render(self) -> None:
        """Render the current frame with smooth animations."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Update rotation angle
        angle = self.cover_rotation.update()
        
        # Update artwork crossfade
        if self.artwork_fade_start is not None:
            elapsed = time.time() - self.artwork_fade_start
            raw_progress = min(1.0, elapsed / self.artwork_fade_duration)
            
            # Apple-style ease-out (cubic)
            self.artwork_fade_progress = 1 - pow(1 - raw_progress, 3)
            
            if self.artwork_fade_progress >= 1.0:
                self.artwork_surface = self.next_artwork_surface
                self.next_artwork_surface = None
                self.artwork_fade_start = None
                self.artwork_fade_progress = 1.0
        
        # Get artwork surface
        artwork = self.artwork_surface if self.artwork_surface else self.placeholder_surface
        
        # Create rendering surface
        result = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))
        
        # Crossfade rendering
        if self.next_artwork_surface is not None:
            # Rotate both artworks
            old_rotated = pygame.transform.rotozoom(artwork, angle, 1.0)
            new_rotated = pygame.transform.rotozoom(self.next_artwork_surface, angle, 1.0)
            
            old_rect = old_rotated.get_rect(center=(self.width // 2, self.height // 2))
            new_rect = new_rotated.get_rect(center=(self.width // 2, self.height // 2))
            
            # Blend old and new
            old_alpha = int(255 * (1 - self.artwork_fade_progress))
            new_alpha = int(255 * self.artwork_fade_progress)
            
            if old_alpha > 0:
                old_rotated.set_alpha(old_alpha)
                result.blit(old_rotated, old_rect)
            
            new_rotated.set_alpha(new_alpha)
            result.blit(new_rotated, new_rect)
        else:
            # Normal rendering
            rotated = pygame.transform.rotozoom(artwork, angle, 1.0)
            rotated_rect = rotated.get_rect(center=(self.width // 2, self.height // 2))
            result.blit(rotated, rotated_rect)
        
        # Apply circular mask
        mask_rect = self.circular_mask.get_rect(center=(self.width // 2, self.height // 2))
        result.blit(self.circular_mask, mask_rect, special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw to screen
        self.screen.blit(result, (0, 0))
        
        # Draw circular progress bar
        if self.current_state:
            self._draw_circular_progress()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def _draw_circular_progress(self) -> None:
        """Draw clean circular progress bar around the vinyl disc."""
        progress_ms = self.current_state.get('progress_ms', 0)
        duration_ms = self.current_state.get('duration_ms', 1)
        
        if duration_ms <= 0:
            return
        
        # Target progress
        target_progress = progress_ms / duration_ms
        
        # Smooth interpolation
        lerp_factor = 0.3
        self.progress_smoothed += (target_progress - self.progress_smoothed) * lerp_factor
        
        # Ring parameters
        center = (self.width // 2, self.height // 2)
        disc_radius = min(self.width, self.height) // 2
        radius = disc_radius - 7
        thickness = 5
        
        # Draw progress arc
        if self.progress_smoothed > 0.001:
            angle = self.progress_smoothed * 360
            
            # Draw arc using multiple circles along the path for smooth appearance
            num_points = max(10, int(angle * 2))  # 2 points per degree
            
            for i in range(num_points + 1):
                current_angle = -90 + (angle * i / num_points)
                rad = math.radians(current_angle)
                
                x = int(center[0] + radius * math.cos(rad))
                y = int(center[1] + radius * math.sin(rad))
                
                # Draw small filled circle at each point
                pygame.gfxdraw.filled_circle(self.screen, x, y, thickness, self.progress_color)
                pygame.gfxdraw.aacircle(self.screen, x, y, thickness, self.progress_color)
    
    def run_frame(self) -> bool:
        """Run one frame of the display loop.
        
        Returns:
            bool: False if quit requested, True otherwise
        """
        if not self.handle_events():
            return False
        
        self.render()
        return True
    
    def quit(self) -> None:
        """Clean up and quit pygame."""
        pygame.quit()
        logger.info("Display closed")
