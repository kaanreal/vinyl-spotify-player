"""Cover rotation animation synchronized with playback."""

import math
import time
from typing import Optional
from PIL import Image
import pygame


class CoverRotation:
    """Manages rotating album cover animation."""
    
    def __init__(self, target_rpm: float = 33.3, ease_duration: float = 0.3):
        """Initialize cover rotation.
        
        Args:
            target_rpm: Target rotation speed in RPM
            ease_duration: Time in seconds for smooth easing transitions
        """
        self.target_rpm = target_rpm
        self.ease_duration = ease_duration
        self.rotation_angle = 0.0
        self.is_rotating = False
        self.current_speed = 0.0  # 0.0 to 1.0
        self.target_speed = 0.0   # 0.0 or 1.0
        self._last_update_time = time.time()
    
    def start(self) -> None:
        """Start rotation animation with smooth ease-in."""
        self.is_rotating = True
        self.target_speed = 1.0
    
    def stop(self) -> None:
        """Stop rotation animation with smooth ease-out."""
        self.is_rotating = False
        self.target_speed = 0.0
    
    def update(self) -> float:
        """Update rotation angle with Apple-style smooth easing.
        
        Returns:
            float: Current rotation angle in degrees
        """
        current_time = time.time()
        dt = current_time - self._last_update_time
        self._last_update_time = current_time
        
        # Smooth speed transition
        if self.current_speed != self.target_speed:
            # Smooth acceleration/deceleration
            speed_diff = self.target_speed - self.current_speed
            acceleration = (speed_diff / self.ease_duration) * dt
            
            if abs(speed_diff) < abs(acceleration):
                self.current_speed = self.target_speed
            else:
                self.current_speed += acceleration
        
        # Always update rotation angle based on current speed
        degrees_per_second = self.target_rpm * 6.0 * self.current_speed
        self.rotation_angle = (self.rotation_angle + degrees_per_second * dt) % 360
        
        return self.rotation_angle
    
    def get_angle(self) -> float:
        """Get current rotation angle without updating.
        
        Returns:
            float: Current rotation angle in degrees
        """
        return self.rotation_angle
    
    def reset(self) -> None:
        """Reset rotation to zero."""
        self.rotation_angle = 0.0
        self._pause_angle = 0.0
        self._start_time = None


def rotate_image_pil(image: Image.Image, angle: float) -> Image.Image:
    """Rotate PIL image around its center.
    
    Args:
        image: PIL Image to rotate
        angle: Rotation angle in degrees
        
    Returns:
        Image.Image: Rotated image
    """
    return image.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=False)


def rotate_surface_pygame(surface: pygame.Surface, angle: float) -> pygame.Surface:
    """Rotate pygame surface around its center.
    
    Args:
        surface: Pygame surface to rotate
        angle: Rotation angle in degrees
        
    Returns:
        pygame.Surface: Rotated surface
    """
    return pygame.transform.rotate(surface, angle)


def create_circular_mask(size: int) -> pygame.Surface:
    """Create a circular mask surface.
    
    Args:
        size: Diameter of the circle
        
    Returns:
        pygame.Surface: Circular mask with alpha channel
    """
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    return mask


def apply_circular_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    """Apply circular mask to a surface.
    
    Args:
        surface: Surface to mask
        mask: Circular mask surface
        
    Returns:
        pygame.Surface: Masked surface
    """
    result = surface.copy()
    result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result
