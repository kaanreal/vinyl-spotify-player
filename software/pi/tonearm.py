"""Tonearm GPIO control for play/pause functionality."""

import time
import RPi.GPIO as GPIO
from typing import Callable, Optional
from config import Config


class TonearmController:
    """Control playback via GPIO tonearm sensor."""
    
    def __init__(self, config: Config, on_state_change: Optional[Callable[[bool], None]] = None):
        """Initialize tonearm controller.
        
        Args:
            config: Application configuration
            on_state_change: Callback when tonearm state changes (placed=True, lifted=False)
        """
        self.config = config
        self.on_state_change = on_state_change
        self.pin = config.gpio_tonearm_pin
        self.active_state = config.gpio_tonearm_active_state
        
        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure pull resistor
        pull_mode = GPIO.PUD_UP if config.gpio_tonearm_pull == 'UP' else GPIO.PUD_DOWN
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_mode)
        
        # State tracking
        self.last_state: Optional[bool] = None
        self.last_change_time: float = 0
        self.debounce_time: float = 0.2  # 200ms debounce
        
        # Read initial state
        self._update_state()
    
    def _is_placed(self) -> bool:
        """Check if tonearm is currently placed.
        
        Returns:
            True if tonearm is placed (active)
        """
        gpio_value = GPIO.input(self.pin)
        return gpio_value == self.active_state
    
    def _update_state(self) -> None:
        """Update current state without triggering callback."""
        self.last_state = self._is_placed()
    
    def check(self) -> None:
        """Check tonearm state and trigger callback if changed."""
        current_state = self._is_placed()
        current_time = time.time()
        
        # Check if state changed
        if current_state != self.last_state:
            # Debounce check
            if current_time - self.last_change_time < self.debounce_time:
                return
            
            self.last_change_time = current_time
            self.last_state = current_state
            
            # Trigger callback
            if self.on_state_change:
                try:
                    self.on_state_change(current_state)
                except Exception as e:
                    print(f"Error in tonearm callback: {e}")
    
    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        GPIO.cleanup(self.pin)
