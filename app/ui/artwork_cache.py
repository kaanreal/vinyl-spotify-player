"""Album artwork cache with background downloading."""

import hashlib
import requests
from pathlib import Path
from typing import Optional
from PIL import Image
import io
import threading
from app.util.paths import get_cache_dir
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class ArtworkCache:
    """Manages album artwork caching and background downloading."""
    
    def __init__(self, target_size: tuple = (480, 480)):
        """Initialize artwork cache.
        
        Args:
            target_size: Target size for cached images (width, height)
        """
        self.cache_dir = get_cache_dir()
        self.target_size = target_size
        self._download_queue = {}  # url -> callbacks list
        self._lock = threading.Lock()
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for a URL.
        
        Args:
            url: Image URL
            
        Returns:
            Path: Cache file path
        """
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.png"
    
    def get_cached_image(self, url: str) -> Optional[Image.Image]:
        """Get cached image if available.
        
        Args:
            url: Image URL
            
        Returns:
            Optional[Image.Image]: Cached image, or None if not cached
        """
        if not url:
            return None
        
        cache_path = self._get_cache_path(url)
        
        if cache_path.exists():
            try:
                return Image.open(cache_path)
            except Exception as e:
                logger.error(f"Failed to load cached image: {e}")
                # Delete corrupted cache file
                cache_path.unlink(missing_ok=True)
        
        return None
    
    def download_image(self, url: str, callback=None) -> None:
        """Download image in background thread.
        
        Args:
            url: Image URL to download
            callback: Optional callback(image) when download completes
        """
        if not url:
            return
        
        # Check if already downloading
        with self._lock:
            if url in self._download_queue:
                # Add callback to existing download
                if callback:
                    self._download_queue[url].append(callback)
                return
            
            # Start new download
            self._download_queue[url] = [callback] if callback else []
        
        def download_thread():
            try:
                logger.debug(f"Downloading album art: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Load and resize image
                img = Image.open(io.BytesIO(response.content))
                img = img.convert('RGB')
                img = img.resize(self.target_size, Image.Resampling.LANCZOS)
                
                # Save to cache
                cache_path = self._get_cache_path(url)
                img.save(cache_path, 'PNG')
                logger.debug(f"Cached album art: {cache_path.name}")
                
                # Notify callbacks
                with self._lock:
                    callbacks = self._download_queue.pop(url, [])
                
                for cb in callbacks:
                    if cb:
                        try:
                            cb(img)
                        except Exception as e:
                            logger.error(f"Artwork callback error: {e}")
            
            except Exception as e:
                logger.error(f"Failed to download album art: {e}")
                with self._lock:
                    self._download_queue.pop(url, None)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def get_or_download(self, url: str, callback=None) -> Optional[Image.Image]:
        """Get cached image or start download.
        
        Args:
            url: Image URL
            callback: Optional callback(image) when download completes (if not cached)
            
        Returns:
            Optional[Image.Image]: Cached image if available, None if downloading
        """
        cached = self.get_cached_image(url)
        if cached:
            return cached
        
        # Start download
        self.download_image(url, callback)
        return None
