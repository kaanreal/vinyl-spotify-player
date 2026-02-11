"""GPIO control for mechanical tonearm."""

import logging
import time
from typing import Optional, Callable

from config import TONEARM_GPIO_PIN, TONEARM_DEBOUNCE_TIME, ENABLE_TONEARM_GPIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("GPIO not available - tonearm control disabled")


class TonearmController:
    """Control playback based on tonearm position via GPIO."""
    
    def __init__(self, on_state_change: Optional[Callable[[bool], None]] = None) -> None:
        self.button: Optional[Button] = None
        self.on_state_change: Optional[Callable[[bool], None]] = on_state_change
        self.last_state: bool = False
        self.last_trigger_time: float = 0.0
        self.enabled: bool = ENABLE_TONEARM_GPIO and GPIO_AVAILABLE
        
        if self.enabled:
            self._setup_gpio()
        else:
            logger.info("Tonearm GPIO control disabled")
    
    def _setup_gpio(self) -> None:
        """Initialize GPIO button."""
        try:
            self.button = Button(
                TONEARM_GPIO_PIN,
                pull_up=True,
                bounce_time=TONEARM_DEBOUNCE_TIME,
            )
            
            self.button.when_pressed = self._on_pressed
            self.button.when_released = self._on_released
            
            self.last_state = self.button.is_pressed
            
            logger.info(f"Tonearm GPIO initialized on pin {TONEARM_GPIO_PIN}")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            self.button = None
            self.enabled = False
    
    def _on_pressed(self) -> None:
        """Handle tonearm placed (button pressed)."""
        if not self._should_trigger():
            return
        
        logger.info("Tonearm placed - triggering play")
        self.last_state = True
        
        if self.on_state_change:
            self.on_state_change(True)
    
    def _on_released(self) -> None:
        """Handle tonearm lifted (button released)."""
        if not self._should_trigger():
            return
        
        logger.info("Tonearm lifted - triggering pause")
        self.last_state = False
        
        if self.on_state_change:
            self.on_state_change(False)
    
    def _should_trigger(self) -> bool:
        """Check if enough time has passed since last trigger."""
        current_time = time.time()
        if current_time - self.last_trigger_time < TONEARM_DEBOUNCE_TIME:
            return False
        
        self.last_trigger_time = current_time
        return True
    
    def get_state(self) -> bool:
        """Get current tonearm state (True = placed, False = lifted)."""
        if self.button:
            return self.button.is_pressed
        return False
    
    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        if self.button:
            self.button.close()
            logger.info("GPIO cleaned up")
