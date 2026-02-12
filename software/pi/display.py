"""Display manager for 480x480 round display using pygame."""

import os
import pygame
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import requests
from io import BytesIO


class Display:
    """Manage pygame display for album artwork and track info."""
    
    # Colors
    BG_COLOR = (20, 20, 20)
    TEXT_COLOR = (255, 255, 255)
    TEXT_DIM_COLOR = (180, 180, 180)
    PROGRESS_BG_COLOR = (60, 60, 60)
    PROGRESS_FG_COLOR = (30, 215, 96)  # Spotify green
    PAUSED_COLOR = (255, 100, 100)
    
    def __init__(self, width: int = 480, height: int = 480, fullscreen: bool = True, cache_dir: Path = Path('./cache')):
        """Initialize display.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
            fullscreen: Whether to use fullscreen mode
            cache_dir: Directory for caching album artwork
        """
        self.width = width
        self.height = height
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize pygame
        os.environ['SDL_VIDEODRIVER'] = 'fbcon'
        os.environ['SDL_FBDEV'] = '/dev/fb0'
        pygame.init()
        
        # Set up display
        if fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))
        
        pygame.display.set_caption('Vinyl Spotify Player')
        pygame.mouse.set_visible(False)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Current state
        self.current_album_art: Optional[pygame.Surface] = None
        self.album_art_url: Optional[str] = None
        
        # Create fallback image (solid circle)
        self._create_fallback_image()
    
    def _create_fallback_image(self) -> None:
        """Create fallback image when no album art available."""
        size = min(self.width, self.height) - 100
        self.fallback_image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            self.fallback_image,
            (60, 60, 60),
            (size // 2, size // 2),
            size // 2
        )
    
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL.
        
        Args:
            url: Image URL
        
        Returns:
            PIL Image or None if download fails
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def _make_circular(self, image: Image.Image) -> Image.Image:
        """Apply circular mask to image.
        
        Args:
            image: PIL Image
        
        Returns:
            Circular masked PIL Image
        """
        size = image.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        output = Image.new('RGBA', size)
        output.paste(image, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def _get_cached_path(self, url: str) -> Path:
        """Get cache file path for URL.
        
        Args:
            url: Image URL
        
        Returns:
            Path to cached file
        """
        # Use URL hash as filename
        filename = f"{hash(url)}.png"
        return self.cache_dir / filename
    
    def load_album_art(self, url: str) -> None:
        """Load and cache album artwork.
        
        Args:
            url: Album artwork URL
        """
        if url == self.album_art_url and self.current_album_art:
            return  # Already loaded
        
        self.album_art_url = url
        cache_path = self._get_cached_path(url)
        
        # Load from cache if available
        if cache_path.exists():
            try:
                pil_image = Image.open(cache_path)
            except Exception as e:
                print(f"Error loading cached image: {e}")
                pil_image = None
        else:
            # Download and cache
            pil_image = self._download_image(url)
            if pil_image:
                try:
                    # Resize and make circular
                    size = min(self.width, self.height) - 100
                    pil_image = pil_image.resize((size, size), Image.Resampling.LANCZOS)
                    pil_image = self._make_circular(pil_image)
                    pil_image.save(cache_path, 'PNG')
                except Exception as e:
                    print(f"Error processing image: {e}")
                    pil_image = None
        
        # Convert to pygame surface
        if pil_image:
            try:
                mode = pil_image.mode
                size = pil_image.size
                data = pil_image.tobytes()
                
                self.current_album_art = pygame.image.fromstring(data, size, mode)
            except Exception as e:
                print(f"Error converting image to pygame surface: {e}")
                self.current_album_art = None
        else:
            self.current_album_art = None
    
    def _truncate_text(self, text: str, font: pygame.font.Font, max_width: int) -> str:
        """Truncate text with ellipsis to fit width.
        
        Args:
            text: Text to truncate
            font: Pygame font
            max_width: Maximum width in pixels
        
        Returns:
            Truncated text
        """
        if font.size(text)[0] <= max_width:
            return text
        
        ellipsis = "..."
        while text and font.size(text + ellipsis)[0] > max_width:
            text = text[:-1]
        
        return text + ellipsis
    
    def render(
        self,
        track_name: str = "",
        artists: str = "",
        album: str = "",
        progress_ms: int = 0,
        duration_ms: int = 1,
        is_playing: bool = False
    ) -> None:
        """Render display with current track info.
        
        Args:
            track_name: Track name
            artists: Artist names (comma separated)
            album: Album name
            progress_ms: Playback progress in milliseconds
            duration_ms: Track duration in milliseconds
            is_playing: Whether track is playing
        """
        # Clear screen
        self.screen.fill(self.BG_COLOR)
        
        # Draw album art (circular)
        art_surface = self.current_album_art if self.current_album_art else self.fallback_image
        art_x = (self.width - art_surface.get_width()) // 2
        art_y = 40
        self.screen.blit(art_surface, (art_x, art_y))
        
        # Calculate text area
        text_y_start = art_y + art_surface.get_height() + 30
        max_text_width = self.width - 40
        
        # Draw track name
        if track_name:
            track_text = self._truncate_text(track_name, self.font_large, max_text_width)
            track_surface = self.font_large.render(track_text, True, self.TEXT_COLOR)
            track_x = (self.width - track_surface.get_width()) // 2
            self.screen.blit(track_surface, (track_x, text_y_start))
        
        # Draw artists
        if artists:
            artist_text = self._truncate_text(artists, self.font_medium, max_text_width)
            artist_surface = self.font_medium.render(artist_text, True, self.TEXT_DIM_COLOR)
            artist_x = (self.width - artist_surface.get_width()) // 2
            self.screen.blit(artist_surface, (artist_x, text_y_start + 50))
        
        # Draw album
        if album:
            album_text = self._truncate_text(album, self.font_small, max_text_width)
            album_surface = self.font_small.render(album_text, True, self.TEXT_DIM_COLOR)
            album_x = (self.width - album_surface.get_width()) // 2
            self.screen.blit(album_surface, (album_x, text_y_start + 90))
        
        # Draw progress bar
        progress_bar_height = 8
        progress_bar_y = self.height - 30
        progress_bar_x = 20
        progress_bar_width = self.width - 40
        
        # Background
        pygame.draw.rect(
            self.screen,
            self.PROGRESS_BG_COLOR,
            (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height),
            border_radius=4
        )
        
        # Progress
        if duration_ms > 0:
            progress_ratio = min(1.0, progress_ms / duration_ms)
            progress_width = int(progress_bar_width * progress_ratio)
            
            progress_color = self.PROGRESS_FG_COLOR if is_playing else self.PAUSED_COLOR
            
            if progress_width > 0:
                pygame.draw.rect(
                    self.screen,
                    progress_color,
                    (progress_bar_x, progress_bar_y, progress_width, progress_bar_height),
                    border_radius=4
                )
        
        # Update display
        pygame.display.flip()
    
    def clear(self) -> None:
        """Clear display to background color."""
        self.screen.fill(self.BG_COLOR)
        pygame.display.flip()
    
    def quit(self) -> None:
        """Quit pygame and clean up."""
        pygame.quit()
