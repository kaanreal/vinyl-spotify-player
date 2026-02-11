"""Display UI for showing album art and track information."""

import logging
from typing import Optional
import pygame
from PIL import Image

from config import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    DISPLAY_FPS,
    ALBUM_ART_SIZE,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    ACCENT_COLOR,
    PROGRESS_BG_COLOR,
    FONT_TITLE_SIZE,
    FONT_ARTIST_SIZE,
    FONT_TIME_SIZE,
)
from spotify_monitor import TrackInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisplayUI:
    """Pygame-based UI for displaying track information."""
    
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Vinyl Spotify Player")
        
        self.screen: pygame.Surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        
        try:
            self.font_title: pygame.font.Font = pygame.font.Font(
                pygame.font.match_font("dejavusans"), FONT_TITLE_SIZE
            )
            self.font_artist: pygame.font.Font = pygame.font.Font(
                pygame.font.match_font("dejavusans"), FONT_ARTIST_SIZE
            )
            self.font_time: pygame.font.Font = pygame.font.Font(
                pygame.font.match_font("dejavusans"), FONT_TIME_SIZE
            )
        except Exception:
            self.font_title = pygame.font.Font(None, FONT_TITLE_SIZE)
            self.font_artist = pygame.font.Font(None, FONT_ARTIST_SIZE)
            self.font_time = pygame.font.Font(None, FONT_TIME_SIZE)
        
        self.running: bool = True
        self.current_album_art: Optional[pygame.Surface] = None
        self.album_art_y: int = 20
        self.progress_bar_height: int = 8
        self.progress_bar_y: int = self.album_art_y + ALBUM_ART_SIZE + 20
    
    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to Pygame Surface."""
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        return pygame.image.fromstring(data, size, mode)
    
    def _render_text_centered(
        self, text: str, font: pygame.font.Font, color: tuple[int, int, int], y: int
    ) -> None:
        """Render centered text at given y position."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(DISPLAY_WIDTH // 2, y))
        self.screen.blit(text_surface, text_rect)
    
    def _render_text_truncated(
        self, text: str, font: pygame.font.Font, color: tuple[int, int, int], y: int, max_width: int
    ) -> None:
        """Render centered text with truncation if too long."""
        text_surface = font.render(text, True, color)
        
        if text_surface.get_width() > max_width:
            while len(text) > 0 and text_surface.get_width() > max_width - 30:
                text = text[:-1]
                text_surface = font.render(text + "...", True, color)
        
        text_rect = text_surface.get_rect(center=(DISPLAY_WIDTH // 2, y))
        self.screen.blit(text_surface, text_rect)
    
    def _draw_progress_bar(self, progress: float, y: int) -> None:
        """Draw progress bar."""
        bar_width = DISPLAY_WIDTH - 80
        bar_x = (DISPLAY_WIDTH - bar_width) // 2
        
        pygame.draw.rect(
            self.screen,
            PROGRESS_BG_COLOR,
            (bar_x, y, bar_width, self.progress_bar_height),
            border_radius=4,
        )
        
        if progress > 0:
            filled_width = int(bar_width * progress)
            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR,
                (bar_x, y, filled_width, self.progress_bar_height),
                border_radius=4,
            )
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def update_album_art(self, pil_image: Image.Image) -> None:
        """Update displayed album art."""
        self.current_album_art = self._pil_to_pygame(pil_image)
    
    def render(self, track: TrackInfo, estimated_position_us: int) -> None:
        """Render the UI with current track info."""
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.current_album_art:
            art_x = (DISPLAY_WIDTH - ALBUM_ART_SIZE) // 2
            self.screen.blit(self.current_album_art, (art_x, self.album_art_y))
        
        title_y = self.progress_bar_y + 30
        artist_y = title_y + 40
        time_y = artist_y + 35
        
        max_text_width = DISPLAY_WIDTH - 40
        
        self._render_text_truncated(
            track.title, self.font_title, TEXT_COLOR, title_y, max_text_width
        )
        
        if track.artist:
            self._render_text_truncated(
                track.artist, self.font_artist, TEXT_COLOR, artist_y, max_text_width
            )
        
        if track.duration_us > 0:
            progress = min(1.0, estimated_position_us / track.duration_us)
            self._draw_progress_bar(progress, self.progress_bar_y)
            
            current_time = self._format_time(estimated_position_us / 1_000_000.0)
            total_time = self._format_time(track.duration_seconds)
            time_text = f"{current_time} / {total_time}"
            self._render_text_centered(time_text, self.font_time, TEXT_COLOR, time_y)
        
        pygame.display.flip()
        self.clock.tick(DISPLAY_FPS)
    
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
        return True
    
    def close(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
        logger.info("Display closed")
