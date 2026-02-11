"""Album art caching and image processing."""

import hashlib
import logging
from pathlib import Path
from typing import Optional
import requests
from PIL import Image, ImageDraw
import io

from config import ALBUM_ART_CACHE_DIR, ALBUM_ART_SIZE, DEFAULT_ALBUM_ART_COLOR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlbumArtCache:
    """Handle album art downloading, caching, and circular masking."""
    
    def __init__(self) -> None:
        self.cache_dir: Path = ALBUM_ART_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_image: Optional[Image.Image] = None
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path from URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.png"
    
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            return image.convert("RGB")
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None
    
    def _create_circular_mask(self, size: int) -> Image.Image:
        """Create a circular alpha mask."""
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        return mask
    
    def _make_circular(self, image: Image.Image, size: int) -> Image.Image:
        """Apply circular mask to image."""
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        
        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(image, (0, 0))
        
        mask = self._create_circular_mask(size)
        output.putalpha(mask)
        
        return output
    
    def get_album_art(self, url: str, size: int = ALBUM_ART_SIZE) -> Image.Image:
        """Get album art, from cache or download."""
        if not url:
            return self._get_default_image(size)
        
        cache_path = self._get_cache_path(url)
        
        if cache_path.exists():
            try:
                cached_image = Image.open(cache_path)
                return cached_image.resize((size, size), Image.Resampling.LANCZOS)
            except Exception as e:
                logger.error(f"Failed to load cached image: {e}")
                cache_path.unlink(missing_ok=True)
        
        image = self._download_image(url)
        if not image:
            return self._get_default_image(size)
        
        circular_image = self._make_circular(image, size)
        
        try:
            circular_image.save(cache_path, "PNG")
            logger.info(f"Cached album art: {cache_path.name}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
        
        return circular_image
    
    def _get_default_image(self, size: int) -> Image.Image:
        """Create default circular image when no album art available."""
        if not self.default_image or self.default_image.size != (size, size):
            image = Image.new("RGB", (size, size), DEFAULT_ALBUM_ART_COLOR)
            draw = ImageDraw.Draw(image)
            
            note_size = size // 4
            note_x = size // 2 - note_size // 2
            note_y = size // 2 - note_size // 2
            
            draw.ellipse(
                (note_x, note_y, note_x + note_size, note_y + note_size),
                fill=(100, 100, 100)
            )
            
            self.default_image = self._make_circular(image, size)
        
        return self.default_image.copy()
    
    def clear_cache(self) -> None:
        """Clear all cached album art."""
        for file in self.cache_dir.glob("*.png"):
            file.unlink()
        logger.info("Album art cache cleared")
