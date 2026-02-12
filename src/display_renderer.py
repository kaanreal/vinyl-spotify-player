"""Display renderer for the 480x480 circular display using pygame."""

import os
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
import pygame
from PIL import Image, ImageDraw
import requests


class DisplayRenderer:
    """Renders album art and playback information on a circular display."""

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
        
        # Font sizes
        self.font_large = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont("Arial", 18)
        
        # Colors
        self.bg_color = (18, 18, 18)
        self.text_color = (255, 255, 255)
        self.sub_text_color = (180, 180, 180)
        self.progress_bg_color = (60, 60, 60)
        self.progress_fg_color = (30, 215, 96)
        
        # Album art settings
        self.album_art_size = 320
        self.album_art_x = (width - self.album_art_size) // 2
        self.album_art_y = 40
        
        # Current track info
        self.current_track_id: Optional[str] = None
        self.current_album_art: Optional[pygame.Surface] = None
        self.fallback_art: Optional[pygame.Surface] = None
        
        # Create fallback album art
        self._create_fallback_art()
    
    def _create_fallback_art(self) -> None:
        """Create a fallback album art image."""
        size = self.album_art_size
        
        # Create PIL image
        img = Image.new('RGB', (size, size), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        output = Image.new('RGB', (size, size), (18, 18, 18))
        output.paste(img, (0, 0), mask)
        
        # Draw musical note icon in center
        center_x, center_y = size // 2, size // 2
        draw_on_output = ImageDraw.Draw(output)
        draw_on_output.ellipse(
            (center_x - 60, center_y - 60, center_x + 60, center_y + 60),
            outline=(100, 100, 100),
            width=4
        )
        
        # Convert to pygame surface
        mode = img.mode
        size = img.size
        data = output.tobytes()
        self.fallback_art = pygame.image.fromstring(data, size, mode)
    
    def _make_circular_surface(self, image_path: Path) -> pygame.Surface:
        """Create a circular pygame surface from an image.
        
        Args:
            image_path: Path to the image file.
        
        Returns:
            Circular pygame surface.
        """
        size = self.album_art_size
        
        # Load image with PIL
        img = Image.open(image_path).convert('RGB')
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        output = Image.new('RGB', (size, size), self.bg_color)
        output.paste(img, (0, 0), mask)
        
        # Convert to pygame surface
        mode = output.mode
        img_size = output.size
        data = output.tobytes()
        
        return pygame.image.fromstring(data, img_size, mode)
    
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
    
    def _truncate_text(self, text: str, font: pygame.font.Font, max_width: int) -> str:
        """Truncate text to fit within max width.
        
        Args:
            text: Text to truncate.
            font: Pygame font.
            max_width: Maximum width in pixels.
        
        Returns:
            Truncated text with ellipsis if needed.
        """
        if font.size(text)[0] <= max_width:
            return text
        
        # Binary search for the right length
        left, right = 0, len(text)
        result = text
        
        while left < right:
            mid = (left + right + 1) // 2
            truncated = text[:mid] + "..."
            
            if font.size(truncated)[0] <= max_width:
                result = truncated
                left = mid
            else:
                right = mid - 1
        
        return result
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds as MM:SS.
        
        Args:
            ms: Time in milliseconds.
        
        Returns:
            Formatted time string.
        """
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def render(self, playback_data: Optional[Dict[str, Any]]) -> None:
        """Render the display with current playback information.
        
        Args:
            playback_data: Current playback data from Spotify API.
        """
        # Clear screen
        self.screen.fill(self.bg_color)
        
        if not playback_data or not playback_data.get("item"):
            # Nothing playing
            self._render_idle()
            pygame.display.flip()
            return
        
        track = playback_data["item"]
        is_playing = playback_data.get("is_playing", False)
        progress_ms = playback_data.get("progress_ms", 0)
        
        # Extract track info
        track_id = track["id"]
        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        album_name = track["album"]["name"]
        duration_ms = track["duration_ms"]
        
        # Get album art URL (largest available)
        album_images = track["album"]["images"]
        album_art_url = album_images[0]["url"] if album_images else None
        
        # Load album art if track changed
        if track_id != self.current_track_id:
            self.current_track_id = track_id
            if album_art_url:
                self.current_album_art = self._load_album_art(album_art_url)
            else:
                self.current_album_art = self.fallback_art
        
        # Render album art
        if self.current_album_art:
            self.screen.blit(self.current_album_art, (self.album_art_x, self.album_art_y))
        
        # Render track name
        y_pos = self.album_art_y + self.album_art_size + 20
        track_text = self._truncate_text(track_name, self.font_large, self.width - 40)
        track_surface = self.font_large.render(track_text, True, self.text_color)
        track_rect = track_surface.get_rect(centerx=self.width // 2, top=y_pos)
        self.screen.blit(track_surface, track_rect)
        
        # Render artists
        y_pos += 40
        artists_text = self._truncate_text(artists, self.font_medium, self.width - 40)
        artists_surface = self.font_medium.render(artists_text, True, self.sub_text_color)
        artists_rect = artists_surface.get_rect(centerx=self.width // 2, top=y_pos)
        self.screen.blit(artists_surface, artists_rect)
        
        # Render album name
        y_pos += 30
        album_text = self._truncate_text(album_name, self.font_small, self.width - 40)
        album_surface = self.font_small.render(album_text, True, self.sub_text_color)
        album_rect = album_surface.get_rect(centerx=self.width // 2, top=y_pos)
        self.screen.blit(album_surface, album_rect)
        
        # Render progress bar
        y_pos = self.height - 50
        progress_bar_width = self.width - 80
        progress_bar_height = 6
        progress_bar_x = 40
        
        # Background
        pygame.draw.rect(
            self.screen,
            self.progress_bg_color,
            (progress_bar_x, y_pos, progress_bar_width, progress_bar_height),
            border_radius=3
        )
        
        # Progress
        if duration_ms > 0:
            progress_ratio = min(progress_ms / duration_ms, 1.0)
            progress_width = int(progress_bar_width * progress_ratio)
            pygame.draw.rect(
                self.screen,
                self.progress_fg_color,
                (progress_bar_x, y_pos, progress_width, progress_bar_height),
                border_radius=3
            )
        
        # Time labels
        y_pos += 15
        current_time = self._format_time(progress_ms)
        total_time = self._format_time(duration_ms)
        
        time_surface = self.font_small.render(current_time, True, self.sub_text_color)
        self.screen.blit(time_surface, (progress_bar_x, y_pos))
        
        time_surface = self.font_small.render(total_time, True, self.sub_text_color)
        time_rect = time_surface.get_rect(right=progress_bar_x + progress_bar_width, top=y_pos)
        self.screen.blit(time_surface, time_rect)
        
        # Paused indicator
        if not is_playing:
            pause_surface = self.font_medium.render("PAUSED", True, (255, 100, 100))
            pause_rect = pause_surface.get_rect(center=(self.width // 2, 20))
            self.screen.blit(pause_surface, pause_rect)
        
        pygame.display.flip()
    
    def _render_idle(self) -> None:
        """Render idle state when nothing is playing."""
        # Render fallback art
        if self.fallback_art:
            self.screen.blit(self.fallback_art, (self.album_art_x, self.album_art_y))
        
        # Render message
        y_pos = self.album_art_y + self.album_art_size + 40
        message = "No music playing"
        message_surface = self.font_large.render(message, True, self.sub_text_color)
        message_rect = message_surface.get_rect(centerx=self.width // 2, top=y_pos)
        self.screen.blit(message_surface, message_rect)
        
        y_pos += 50
        hint = "Start playback from your phone"
        hint_surface = self.font_small.render(hint, True, self.sub_text_color)
        hint_rect = hint_surface.get_rect(centerx=self.width // 2, top=y_pos)
        self.screen.blit(hint_surface, hint_rect)
    
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
