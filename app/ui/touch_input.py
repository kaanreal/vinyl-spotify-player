"""Touch input handling with gesture detection."""

import time
from typing import Optional, Callable, Tuple
from enum import Enum
import pygame


class Gesture(Enum):
    """Touch gestures."""
    TAP = "tap"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"


class TouchInput:
    """Touch input handler with gesture detection."""
    
    def __init__(self, 
                 swipe_threshold: int = 50,
                 tap_max_duration: float = 0.3):
        """Initialize touch input handler.
        
        Args:
            swipe_threshold: Minimum pixel distance for swipe detection
            tap_max_duration: Maximum duration for tap detection (seconds)
        """
        self.swipe_threshold = swipe_threshold
        self.tap_max_duration = tap_max_duration
        
        self._touch_start = None
        self._touch_start_time = None
        
        # Gesture callbacks
        self._on_tap = None
        self._on_swipe = None
    
    def on_tap(self, callback: Callable[[], None]) -> None:
        """Set tap gesture callback.
        
        Args:
            callback: Function to call on tap
        """
        self._on_tap = callback
    
    def on_swipe(self, callback: Callable[[Gesture], None]) -> None:
        """Set swipe gesture callback.
        
        Args:
            callback: Function to call on swipe with Gesture type
        """
        self._on_swipe = callback
    
    def handle_mouse_down(self, pos: Tuple[int, int]) -> None:
        """Handle mouse/touch down event.
        
        Args:
            pos: (x, y) position
        """
        self._touch_start = pos
        self._touch_start_time = time.time()
    
    def handle_mouse_up(self, pos: Tuple[int, int]) -> None:
        """Handle mouse/touch up event.
        
        Args:
            pos: (x, y) position
        """
        if self._touch_start is None or self._touch_start_time is None:
            return
        
        duration = time.time() - self._touch_start_time
        dx = pos[0] - self._touch_start[0]
        dy = pos[1] - self._touch_start[1]
        distance = (dx**2 + dy**2)**0.5
        
        # Detect gesture
        if duration < self.tap_max_duration and distance < self.swipe_threshold / 2:
            # Tap
            if self._on_tap:
                self._on_tap()
        
        elif distance >= self.swipe_threshold:
            # Swipe
            gesture = self._detect_swipe_direction(dx, dy)
            if gesture and self._on_swipe:
                self._on_swipe(gesture)
        
        # Reset
        self._touch_start = None
        self._touch_start_time = None
    
    def _detect_swipe_direction(self, dx: float, dy: float) -> Optional[Gesture]:
        """Detect swipe direction from delta.
        
        Args:
            dx: X delta
            dy: Y delta
            
        Returns:
            Optional[Gesture]: Detected swipe gesture, or None
        """
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        if abs_dx > abs_dy:
            # Horizontal swipe
            return Gesture.SWIPE_RIGHT if dx > 0 else Gesture.SWIPE_LEFT
        else:
            # Vertical swipe
            return Gesture.SWIPE_DOWN if dy > 0 else Gesture.SWIPE_UP


class DevTouchInput(TouchInput):
    """Touch input with keyboard simulation for development."""
    
    def __init__(self, 
                 swipe_threshold: int = 50,
                 tap_max_duration: float = 0.3,
                 tap_key: int = pygame.K_SPACE,
                 next_key: int = pygame.K_RIGHT,
                 prev_key: int = pygame.K_LEFT):
        """Initialize dev touch input.
        
        Args:
            swipe_threshold: Minimum pixel distance for swipe detection
            tap_max_duration: Maximum duration for tap detection
            tap_key: Keyboard key for tap simulation
            next_key: Keyboard key for next/swipe right
            prev_key: Keyboard key for previous/swipe left
        """
        super().__init__(swipe_threshold, tap_max_duration)
        self.tap_key = tap_key
        self.next_key = next_key
        self.prev_key = prev_key
    
    def handle_key_down(self, key: int) -> None:
        """Handle keyboard event for simulation.
        
        Args:
            key: Pygame key constant
        """
        if key == self.tap_key:
            if self._on_tap:
                self._on_tap()
        
        elif key == self.next_key:
            if self._on_swipe:
                self._on_swipe(Gesture.SWIPE_RIGHT)
        
        elif key == self.prev_key:
            if self._on_swipe:
                self._on_swipe(Gesture.SWIPE_LEFT)
