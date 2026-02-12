"""Display renderer for the 480x480 circular display using pygame."""

import os
import math
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
import pygame
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import requests


class DisplayRenderer:
    """Renders spinning album art with vinyl record aesthetics."""

    def __init__(self, width: int, height: int, cache_dir: Path):
        """Initialize the display renderer.
        
        Args:
            width: Display width in pixels.
            height: Display height in pixels.
            cache_dir: Directory for caching album artwork.
        """
        self.width = width
        self.height = height
        self.cache_dir = cache_dir
        
        # Initialize pygame
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.mouse.set_visible(False)
        
        # Try to use framebuffer mode
        try:
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
            )
        except pygame.error:
            # Fallback to windowed mode for testing
            self.screen = pygame.display.set_mode((width, height))
        
        pygame.display.set_caption("Vinyl Spotify Player")
        
        # Clock for smooth animation
        self.clock = pygame.time.Clock()
        
        # Colors
        self.bg_color = (10, 10, 12)
        
        # Vinyl record settings
        self.vinyl_size = int(width * 0.95)  # 95% of screen
        self.album_art_size = int(self.vinyl_size * 0.62)  # Album art is 62% of vinyl
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Animation state
        self.rotation_angle = 0.0
        self.rotation_speed = 0.0  # Degrees per second
        self.target_rotation_speed = 0.0
        self.playing_speed = 33.33  # RPM converted to degrees/sec (33.33 RPM = ~200 deg/sec)
        
        # Transition state
        self.transition_alpha = 0.0
        self.transitioning = False
        self.old_album_art: Optional[pygame.Surface] = None
        
        # Current track info
        self.current_track_id: Optional[str] = None
        self.current_album_art: Optional[pygame.Surface] = None
        self.current_album_art_rotated: Optional[pygame.Surface] = None
        self.fallback_art: Optional[pygame.Surface] = None
        
        # Vinyl record base (cached)
        self.vinyl_base: Optional[pygame.Surface] = None
        
        # Create vinyl and fallback art
        self._create_vinyl_base()
        self._create_fallback_art()
    
    
    def _create_vinyl_base(self) -> None:
        """Create a realistic vinyl record base with grooves and shine."""
        size = self.vinyl_size
        
        # Create PIL image for the vinyl
        vinyl = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vinyl)
        
        # Main vinyl disc - dark with slight gradient
        for i in range(20):
            shade = 15 + i
            radius = size // 2 - i
            draw.ellipse(
                (size//2 - radius, size//2 - radius, size//2 + radius, size//2 + radius),
                fill=(shade, shade, shade, 255)
            )
        
        # Draw vinyl grooves (concentric circles)
        groove_start = self.album_art_size // 2 + 20
        groove_end = size // 2 - 10
        
        for radius in range(groove_start, groove_end, 3):
            alpha = 40 if radius % 6 == 0 else 15
            draw.ellipse(
                (size//2 - radius, size//2 - radius, size//2 + radius, size//2 + radius),
                outline=(0, 0, 0, alpha),
                width=1
            )
        
        # Add subtle shine effect on one side
        shine = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        shine_draw = ImageDraw.Draw(shine)
        
        # Gradient shine
        for i in range(30):
            alpha = int(15 * (1 - i / 30))
            offset = int(size * 0.15) + i * 2
            shine_draw.ellipse(
                (offset, offset, size - offset, size - offset),
                outline=(255, 255, 255, alpha),
                width=2
            )
        
        vinyl = Image.alpha_composite(vinyl, shine)
        
        # Convert to pygame surface
        vinyl_bytes = vinyl.tobytes()
        self.vinyl_base = pygame.image.fromstring(vinyl_bytes, (size, size), 'RGBA')
    
    def _create_fallback_art(self) -> None:
        """Create a stylish fallback album art image."""
        size = self.album_art_size
        
        # Create gradient background
        img = Image.new('RGB', (size, size), color=(25, 25, 30))
        draw = ImageDraw.Draw(img)
        
        # Draw concentric circles as music symbol
        center = size // 2
        for i in range(5):
            radius = 30 + i * 15
            color = (60 + i * 20, 60 + i * 20, 80 + i * 20)
            draw.ellipse(
                (center - radius, center - radius, center + radius, center + radius),
                outline=color,
                width=3
            )
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        output = Image.new('RGB', (size, size), self.bg_color)
        output.paste(img, (0, 0), mask)
        
        # Convert to pygame surface
        data = output.tobytes()
        self.fallback_art = pygame.image.fromstring(data, (size, size), 'RGB')
    
    
    def _make_circular_surface(self, image_path: Path) -> pygame.Surface:
        """Create a circular pygame surface from an image with enhanced quality.
        
        Args:
            image_path: Path to the image file.
        
        Returns:
            Circular pygame surface.
        """
        size = self.album_art_size
        
        # Load image with PIL
        img = Image.open(image_path).convert('RGB')
        
        # Enhance image quality
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Create circular mask with anti-aliasing
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        
        # Smooth the mask edges
        mask = mask.filter(ImageFilter.GaussianBlur(1))
        
        # Apply mask
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Convert to pygame surface
        data = output.tobytes()
        surface = pygame.image.fromstring(data, (size, size), 'RGBA')
        
        return surface.convert_alpha()
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for an album art URL.
        
        Args:
            url: Album art URL.
        
        Returns:
            Path to cached file.
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def _download_album_art(self, url: str) -> Optional[Path]:
        """Download and cache album art.
        
        Args:
            url: Album art URL.
        
        Returns:
            Path to cached file or None if download failed.
        """
        cache_path = self._get_cache_path(url)
        
        # Return cached file if exists
        if cache_path.exists():
            return cache_path
        
        # Download
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            with open(cache_path, 'wb') as f:
                f.write(response.content)
            
            return cache_path
        
        except requests.RequestException as e:
            print(f"Error downloading album art: {e}")
            return None
    
    def _load_album_art(self, url: str) -> pygame.Surface:
        """Load album art from URL, with caching.
        
        Args:
            url: Album art URL.
        
        Returns:
            Pygame surface with circular album art.
        """
        image_path = self._download_album_art(url)
        
        if image_path:
            try:
                return self._make_circular_surface(image_path)
            except Exception as e:
                print(f"Error creating circular surface: {e}")
        
        return self.fallback_art
    
    def _update_rotation(self, is_playing: bool, delta_time: float) -> None:
        """Update rotation animation smoothly.
        
        Args:
            is_playing: Whether music is currently playing.
            delta_time: Time elapsed since last frame in seconds.
        """
        # Set target speed based on playback state
        self.target_rotation_speed = self.playing_speed if is_playing else 0.0
        
        # Smooth acceleration/deceleration
        speed_diff = self.target_rotation_speed - self.rotation_speed
        acceleration = 50.0  # Degrees per second squared
        
        if abs(speed_diff) > 0.1:
            change = min(abs(speed_diff), acceleration * delta_time)
            self.rotation_speed += change if speed_diff > 0 else -change
        else:
            self.rotation_speed = self.target_rotation_speed
        
        # Update rotation angle
        self.rotation_angle += self.rotation_speed * delta_time
        self.rotation_angle %= 360
    
    def _rotate_surface(self, surface: pygame.Surface, angle: float) -> pygame.Surface:
        """Rotate a surface smoothly around its center.
        
        Args:
            surface: Surface to rotate.
            angle: Rotation angle in degrees.
        
        Returns:
            Rotated surface.
        """
        return pygame.transform.rotate(surface, -angle)
    
    def _apply_fade_transition(self, alpha: float) -> None:
        """Apply fade overlay for transitions.
        
        Args:
            alpha: Alpha value (0-255).
        """
        if alpha > 0:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.fill(self.bg_color)
            fade_surface.set_alpha(int(alpha))
            self.screen.blit(fade_surface, (0, 0))
    
    def render(self, playback_data: Optional[Dict[str, Any]]) -> None:
        """Render spinning vinyl with album art.
        
        Args:
            playback_data: Current playback data from Spotify API.
        """
        # Get delta time for smooth animation
        delta_time = self.clock.tick(60) / 1000.0  # 60 FPS target
        
        # Clear screen with dark background
        self.screen.fill(self.bg_color)
        
        if not playback_data or not playback_data.get("item"):
            # Nothing playing - show idle state
            self._render_idle(delta_time)
            pygame.display.flip()
            return
        
        track = playback_data["item"]
        is_playing = playback_data.get("is_playing", False)
        
        # Extract track info
        track_id = track["id"]
        album_images = track["album"]["images"]
        album_art_url = album_images[0]["url"] if album_images else None
        
        # Handle track change with transition
        if track_id != self.current_track_id:
            self.old_album_art = self.current_album_art
            self.current_track_id = track_id
            
            # Load new album art
            if album_art_url:
                self.current_album_art = self._load_album_art(album_art_url)
            else:
                self.current_album_art = self.fallback_art
            
            # Start transition
            self.transitioning = True
            self.transition_alpha = 0.0
        
        # Update rotation animation
        self._update_rotation(is_playing, delta_time)
        
        # Render the vinyl record (rotates)
        if self.vinyl_base:
            rotated_vinyl = self._rotate_surface(self.vinyl_base, self.rotation_angle)
            vinyl_rect = rotated_vinyl.get_rect(center=(self.center_x, self.center_y))
            self.screen.blit(rotated_vinyl, vinyl_rect.topleft)
        
        # Render album art (rotates with vinyl)
        if self.current_album_art:
            rotated_art = self._rotate_surface(self.current_album_art, self.rotation_angle)
            art_rect = rotated_art.get_rect(center=(self.center_x, self.center_y))
            
            # Handle transition fade
            if self.transitioning and self.old_album_art:
                # Fade out old art
                old_rotated = self._rotate_surface(self.old_album_art, self.rotation_angle)
                old_rect = old_rotated.get_rect(center=(self.center_x, self.center_y))
                
                old_alpha = int(255 * (1.0 - self.transition_alpha))
                old_rotated.set_alpha(old_alpha)
                self.screen.blit(old_rotated, old_rect.topleft)
                
                # Fade in new art
                new_alpha = int(255 * self.transition_alpha)
                rotated_art.set_alpha(new_alpha)
                self.screen.blit(rotated_art, art_rect.topleft)
                
                # Update transition
                self.transition_alpha += delta_time * 2.0  # 0.5 second transition
                
                if self.transition_alpha >= 1.0:
                    self.transitioning = False
                    self.transition_alpha = 1.0
                    self.old_album_art = None
            else:
                # Normal rendering
                self.screen.blit(rotated_art, art_rect.topleft)
        
        # Add subtle glow when playing
        if is_playing and self.rotation_speed > 10:
            self._render_glow()
        
        pygame.display.flip()
    
    def _render_idle(self, delta_time: float) -> None:
        """Render idle state when nothing is playing.
        
        Args:
            delta_time: Time elapsed since last frame.
        """
        # Slow rotation when idle
        self._update_rotation(False, delta_time)
        
        # Render vinyl base
        if self.vinyl_base:
            rotated_vinyl = self._rotate_surface(self.vinyl_base, self.rotation_angle * 0.2)
            vinyl_rect = rotated_vinyl.get_rect(center=(self.center_x, self.center_y))
            self.screen.blit(rotated_vinyl, vinyl_rect.topleft)
        
        # Render fallback art
        if self.fallback_art:
            rotated_art = self._rotate_surface(self.fallback_art, self.rotation_angle * 0.2)
            art_rect = rotated_art.get_rect(center=(self.center_x, self.center_y))
            self.screen.blit(rotated_art, art_rect.topleft)
    
    def _render_glow(self) -> None:
        """Render subtle glow effect around the vinyl."""
        glow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw multiple circles with decreasing alpha for glow effect
        for i in range(8):
            radius = (self.vinyl_size // 2) + (i * 4)
            alpha = int(15 * (1 - i / 8))
            pygame.draw.circle(
                glow_surface,
                (30, 215, 96, alpha),
                (self.center_x, self.center_y),
                radius,
                2
            )
        
        self.screen.blit(glow_surface, (0, 0))
    
    def handle_events(self) -> bool:
        """Handle pygame events.
        
        Returns:
            False if quit event received, True otherwise.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
        
        return True
    
    def cleanup(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
